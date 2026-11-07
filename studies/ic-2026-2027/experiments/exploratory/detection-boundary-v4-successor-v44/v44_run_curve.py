"""Amendment v4.4 runner: the frozen tier runner with one recorded exception handled.

The frozen scheduler accepts the per-cell worker as a parameter. This successor
loads the frozen ``run_curve.py`` from the checkout named by ``--freeze`` and
runs its unchanged preflight and loop with a worker that differs from the frozen
``execute_cell`` in a single case: the ``ValueError("ill-conditioned local
profile")`` raised by ``project_shift`` during nuisance propagation. That cell is
recorded as a propagation gap and sealed; every other exception still ends the
shard as before. The file lives outside the frozen checkout, so the code hashes
that the frozen preflight and the shard resume check are unchanged.
"""

from __future__ import annotations

import functools
import hashlib
import importlib.util
import sys
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any

AMENDMENT = "v4.4"
KIND = "propagation"
MESSAGE = "ill-conditioned local profile"
FUNCTION = "project_shift"
MODULE_FILE = "detection_boundary_v4.py"
SELF_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def raised_by_projection(error: BaseException) -> bool:
    """True only for the recorded ill-conditioned projection error."""
    if type(error) is not ValueError or str(error) != MESSAGE:
        return False
    frames = traceback.extract_tb(error.__traceback__)
    if not frames:
        return False
    last = frames[-1]
    return last.name == FUNCTION and Path(last.filename).name == MODULE_FILE


def gap_record() -> dict[str, object]:
    return {
        "success": False,
        "attempts": [],
        "dependency_gap": False,
        "successor_gap": {
            "amendment": AMENDMENT,
            "kind": KIND,
            "error": MESSAGE,
            "function": FUNCTION,
            "successor_sha256": SELF_SHA256,
        },
    }


def successor_worker(
    unit: Any, index: int, directory: Path, *, execute_cell: Any, store_type: Any
) -> None:
    try:
        execute_cell(unit, index, directory)
    except ValueError as error:
        if not raised_by_projection(error):
            raise
        store = store_type(directory)
        if store.get_json("result") is not None:
            raise
        store.put_json("result", gap_record())
        store.seal()


def load_frozen_runner(freeze: Path) -> ModuleType:
    runner = freeze.resolve().parent / "run_curve.py"
    spec = importlib.util.spec_from_file_location("frozen_run_curve", runner)
    if spec is None or spec.loader is None:
        raise ValueError("Frozen runner not found beside the freeze record")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _freeze_argument(argv: list[str]) -> Path:
    for index, value in enumerate(argv):
        if value == "--freeze" and index + 1 < len(argv):
            return Path(argv[index + 1])
        if value.startswith("--freeze="):
            return Path(value.split("=", 1)[1])
    raise SystemExit("--freeze is required")


def main() -> int:
    module = load_frozen_runner(_freeze_argument(sys.argv[1:]))
    from ic_study.simulation.v4_curve import execute_cell, schedule
    from ic_study.simulation.v4_store import SealedStore

    worker = functools.partial(
        successor_worker, execute_cell=execute_cell, store_type=SealedStore
    )
    module.schedule = functools.partial(schedule, worker=worker)  # type: ignore[attr-defined]
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
