"""Release sealed confirmatory curves when the inventory completes or at close.

The release amendment registers this successor to ``run_curve.py
--release-at-close``. Run it with the frozen checkout's environment: the
pre-flight verifies the study that provides ``ic_study``, and a checkout that
holds this file never matches the frozen code map.
"""

from __future__ import annotations

# ruff: noqa: E402 -- BLAS limits must precede NumPy imports.
import os

for variable in ("OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import fcntl
import hashlib
import json
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path

import ic_study
from ic_study.simulation.v4_curve import CLOSE, CurveUnit, curve_units, released_curves
from ic_study.simulation.v4_gate import (
    aggregate,
    allocation_preflight,
    g0_statuses,
    preflight,
)
from ic_study.simulation.v4_store import DEFAULT_SEALED, SealedStore

AMENDMENT = {
    "path": "studies/ic-2026-2027/research/questions/exploration/"
    "2026-09-24-parallel/detection-boundary-v4-release-amendment.md",
    "commit": "428ca7cd6158244b494dcb520b9a69738b5bfae6",
}
EARLY = "inventory-complete"
AT_CLOSE = "declared-close"


def identifier(freeze: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(freeze["code"], sort_keys=True).encode()
    ).hexdigest()


def confirmatory_path(freeze: dict[str, object]) -> Path:
    return DEFAULT_SEALED.parent / "sealed-v4-confirmatory" / identifier(freeze)


def verified_root(
    freeze_path: Path, allocation: Path, criteria_path: Path | None
) -> SealedStore:
    """The frozen ``--release-at-close`` pre-flight, in the frozen order."""
    study = Path(ic_study.__file__).resolve().parents[2]
    freeze = preflight(freeze_path, study)
    freeze_digest = hashlib.sha256(freeze_path.read_bytes()).hexdigest()
    gate = SealedStore(DEFAULT_SEALED / identifier(freeze))
    criteria_bytes = (
        criteria_path
        or study / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
    ).read_bytes()
    criteria = json.loads(criteria_bytes)
    cells = allocation_preflight(
        allocation, freeze_digest, g0_statuses(gate), criteria_bytes
    )
    binding = hashlib.sha256(allocation.read_bytes()).hexdigest()
    for stage in ("G0", "G1b", "G1c", "G2", "G2c"):
        result = aggregate(
            stage,
            gate.root,
            criteria,
            cells=cells,
            binding={
                "freeze_sha256": freeze_digest,
                "binding_sha256": binding if stage in {"G2", "G2c"} else freeze_digest,
            },
        )
        if not result["pass"]:
            raise ValueError("Coverage prerequisite incomplete or failed")
    return SealedStore(confirmatory_path(freeze))


def pending_units(root: Path, units: Iterable[CurveUnit]) -> list[str]:
    """Units without a curve record, judged by file existence, never by content."""
    return [unit.key for unit in units if not (root / unit.key / "curve.json").exists()]


def curve_workers_running() -> bool:
    found = subprocess.run(
        ["pgrep", "-f", "run_curve.py"], stdout=subprocess.DEVNULL, check=False
    ).returncode
    if found not in {0, 1}:
        raise RuntimeError("Cannot list run_curve.py processes")
    return found == 0


def release_condition(now: datetime, pending: int, running: bool) -> str:
    """The amendment condition that holds at ``now``; anything else is refused."""
    if running:
        raise ValueError("A run_curve.py process is still running")
    if now >= CLOSE:
        return AT_CLOSE
    if pending:
        raise ValueError("No partial release before the declared close")
    return EARLY


def _temporary(directory: Path, content: bytes) -> Path:
    descriptor, name = tempfile.mkstemp(prefix=".release-", dir=directory)
    path = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path


def _publish(temporary: Path, target: Path) -> None:
    os.replace(temporary, target)
    descriptor = os.open(target.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def release(
    root: SealedStore | Callable[[], SealedStore],
    record: Path,
    *,
    now: datetime | None = None,
    running: bool | Callable[[], bool],
) -> str:
    """Lock the entire attempt; publish durable curves before their receipt."""
    record.parent.mkdir(parents=True, exist_ok=True)
    output_path = record.with_name("released-curves.json")
    descriptor = os.open(record.parent / ".release.lock", os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, "rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if record.exists():
            side = json.loads(record.read_bytes())
            if not output_path.is_file():
                raise ValueError("Release receipt has no published curves")
            published = output_path.read_bytes()
            if (
                side.get("released_curves_sha256")
                != hashlib.sha256(published).hexdigest()
            ):
                raise ValueError(
                    "Release receipt SHA-256 differs from published curves"
                )
            return published.decode("utf-8")
        if callable(root):
            root = root()
        now = datetime.now(UTC) if now is None else now
        condition = release_condition(
            now,
            len(pending_units(root.root, curve_units())),
            running() if callable(running) else running,
        )
        temporaries: list[Path] = []
        try:
            released = released_curves(root, now=CLOSE if condition == EARLY else None)
            output = json.dumps(released, allow_nan=False) + "\n"
            curves_temp = _temporary(record.parent, output.encode())
            temporaries.append(curves_temp)
            side = {
                "schema": 1,
                "amendment": AMENDMENT,
                "condition": condition,
                "released_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "released_curves_sha256": hashlib.sha256(output.encode()).hexdigest(),
                "script_sha256": hashlib.sha256(
                    Path(__file__).read_bytes()
                ).hexdigest(),
            }
            record_temp = _temporary(
                record.parent,
                (json.dumps(side, indent=2, sort_keys=True) + "\n").encode(),
            )
            temporaries.append(record_temp)
            _publish(curves_temp, output_path)
            _publish(record_temp, record)
            return output
        finally:
            for path in temporaries:
                path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--allocation", type=Path, required=True)
    parser.add_argument("--criteria", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-only", action="store_true")
    mode.add_argument("--record", type=Path)
    args = parser.parse_args()
    try:
        if args.check_only:
            path = confirmatory_path(json.loads(args.freeze.read_bytes()))
            pending = len(pending_units(path, curve_units()))
            complete = not pending and not curve_workers_running()
            print(json.dumps({"complete": complete, "pending": pending}))
        else:
            release(
                lambda: verified_root(args.freeze, args.allocation, args.criteria),
                args.record,
                running=curve_workers_running,
            )
            print(json.dumps({"release_record": str(args.record)}))
        return 0
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        print(json.dumps({"preflight_or_execution_failure_count": 1}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
