"""One coarse development check at externally fixed reliability; no parameter search."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from ic_study.analysis.redesign import balanced_accuracy, fit_discriminant
from ic_study.models.anchored_panel import Floats, Integers
from ic_study.simulation.redesign_calibration import (
    CalibrationRun,
    CalibrationSpec,
    panel_gate,
    pilot_seed,
)

HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[2]
ROOT = STUDY.parents[1]
OFFSET = 10000


class CorrectionRun(CalibrationRun):
    def panel(
        self, phase: str, index: int, strength: float, rho: float
    ) -> tuple[Floats, Integers, float]:
        return super().panel(phase, OFFSET + index, strength, rho)


def audit_seeds(count: int) -> dict[str, int]:
    ledger = HERE.parent / "redesign-calibration-v1/run-01/panel-ledger.jsonl"
    old = {
        seed
        for line in ledger.read_text().splitlines()
        for seed in json.loads(line)["seeds"].values()
    }
    for phase in ("dose-calibration", "dose-check"):
        for role in ("network", "state", "source"):
            old.update(pilot_seed(phase, role, i) for i in range(48))
    new = {
        pilot_seed(phase, role, OFFSET + i)
        for phase in ("primary-train", "primary-check")
        for role in ("state", "network", "events", "mask", "error")
        for i in range(2 * count)
    }
    reserved: set[int] = set()

    def reserve(phase: str, role: str, number: int) -> None:
        for i in range(number):
            name = f"ic-redesign-v1|{phase}|{role}|{i}"
            reserved.add(
                int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "big")
            )

    for phase, number in (
        ("confirm-train", 4000),
        ("confirm-validation", 800),
        ("confirm-test", 1000),
    ):
        for role in ("network", "state", "events", "mask", "error"):
            size = 500 if phase == "confirm-test" and role == "network" else number
            reserve(phase, "panel/" + role, size)
    for role, number in (("network", 500), ("state", 1000), ("source", 1000)):
        reserve("confirm-test", "dose/" + role, number)
    for candidate in ("panel", "dose"):
        reserve("confirm-bootstrap", candidate + "/resampling", 1)
    if new & old or new & reserved or len(new) != 20 * count:
        raise ValueError("Seed separation failed")
    return {
        "old_pilot_seeds": len(old),
        "new_pilot_seeds": len(new),
        "reserved_confirmatory_seeds": len(reserved),
        "intersection_count": 0,
        "confirmatory_simulations": 0,
    }


def deadline(_signal: int, _frame: object) -> None:
    raise TimeoutError("Correction pilot exceeded its budget")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = CalibrationSpec(**json.loads((HERE / "spec.json").read_text()))
    if spec.primary_reliability != 0.70 or spec.max_seconds > 590:
        raise ValueError("The external correction and budget must remain fixed")
    previous = HERE.parent / "redesign-calibration-v1/run-01/summary.json"
    selection = next(
        r
        for r in json.loads(previous.read_text())["records"]
        if r["kind"] == "panel_selection"
    )
    strength, rho = float(selection["strength"]), float(selection["rho"])
    if (strength, rho) != (0.4, 0.838961863215152):
        raise ValueError("Unexpected inherited operating point")
    audit = audit_seeds(spec.primary_count)
    run = CorrectionRun(spec, args.output)
    research = STUDY / "research/questions/exploration/2026-09-24-parallel"
    inputs = [
        *sorted((STUDY / "src/ic_study").rglob("*.py")),
        STUDY / "uv.lock",
        HERE / "spec.json",
        HERE / "protocol.md",
        Path(__file__).resolve(),
        previous,
        research / "reliability-and-prior-art.md",
        research / "decision-13-amendment.md",
    ]
    manifest = {
        "started_utc": datetime.now(UTC).isoformat(),
        "head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "command": sys.argv,
        "seed_offset": OFFSET,
        "inputs_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in inputs
        },
        "seed_audit": audit,
        "operating_point_reselected": False,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, spec.max_seconds)
    status = "completed"
    try:
        train, labels, _ = run.sample(
            "primary-train", spec.primary_count, strength, rho
        )
        check, truth, diagnostics = run.sample(
            "primary-check", spec.primary_count, strength, rho
        )
        model = fit_discriminant(train, labels)
        run.record(
            "reliability_correction_gate",
            reliability=spec.primary_reliability,
            strength=strength,
            rho=rho,
            **panel_gate(balanced_accuracy(model.score(check), truth)),
            **diagnostics,
        )
    except (TimeoutError, ValueError, RuntimeError) as error:
        status = f"incomplete: {type(error).__name__}: {error}"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        result = {
            "status": status,
            "elapsed_seconds": time.perf_counter() - run.started,
            "simulations": run.simulations,
            "records": run.records,
            "primary_values_exported": False,
            "confirmatory_simulations": 0,
        }
        (args.output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result), flush=True)
    if status != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
