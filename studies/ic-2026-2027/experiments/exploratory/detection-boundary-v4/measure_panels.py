"""Timing-only final-code panel probes; no classifier import or invocation."""

from __future__ import annotations

import os

# ruff: noqa: E402 -- BLAS limits must precede numerical imports.
for variable in ("OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import hashlib
import json
import multiprocessing
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan


def task(payload: tuple[Cell, bool, int]) -> tuple[float, float]:
    cell, alternative, start = payload
    source = PanelSource(cell, SeedPlan(9002))
    cpu, wall = time.process_time(), time.perf_counter()
    source.profiles(
        "match",
        8,
        start=start,
        parameters=None
        if alternative
        else np.array([0.85, 0 if cell.family in {"A", "C"} else 0.1]),
    )
    return time.process_time() - cpu, time.perf_counter() - wall


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    study = Path(__file__).resolve().parents[3]
    files = [Path(__file__), *sorted((study / "src").rglob("*.py")), study / "uv.lock"]
    provenance = {
        str(p.relative_to(study)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
    }
    rows = []
    configurations = [
        ("anchor-social", Cell(0, 0.7), True),
        ("main-social", Cell(0.03, 0.7), True),
        *[("main-null-" + f, Cell(0.03, 0.7, family=f), False) for f in "ABCDE"],
        ("control-social", Cell(0.03, 0.7, channel="latent"), True),
        ("control-null", Cell(0.03, 0.7, channel="latent"), False),
        ("mobility-social", Cell(0.03, 0.7, mobility=True), True),
        ("mobility-null", Cell(0.03, 0.7, mobility=True), False),
        ("c050", Cell(0.03, 0.7, error_correlation=0.5), True),
        ("delta020", Cell(0.03, 0.7, gain=0.2), True),
        ("omega100", Cell(0.03, 0.7, anchor=1), True),
        ("steps24-social", Cell(0.03, 0.7, steps=24), True),
        ("steps24-null", Cell(0.03, 0.7, steps=24), False),
    ]
    with ProcessPoolExecutor(
        max_workers=8, mp_context=multiprocessing.get_context("spawn")
    ) as pool:
        for name, cell, alternative in configurations:
            results = list(
                pool.map(task, [(cell, alternative, 8 * i) for i in range(8)])
            )
            rows.append(
                {
                    "operation": name,
                    "cell": asdict(cell),
                    "panels": 64,
                    "cpu_seconds": sum(r[0] for r in results),
                    "worker_wall_seconds": sum(r[1] for r in results),
                }
            )
    result = {
        "kind": "final-code-cost-only",
        "seed_repetition": 9002,
        "phase": "match",
        "workers": 8,
        "OPENBLAS_NUM_THREADS": 1,
        "VECLIB_MAXIMUM_THREADS": 1,
        "classifiers_trained": 0,
        "panels": rows,
        "code": provenance,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "host_sha256": hashlib.sha256(
            (platform.node() + platform.machine()).encode()
        ).hexdigest(),
    }
    with args.output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"panel_count": 64 * len(rows), "classifiers_trained": 0}))


if __name__ == "__main__":
    main()
