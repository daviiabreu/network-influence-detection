"""Calibration-seed panel/solver timing; never imports or trains a classifier."""

from __future__ import annotations

# ruff: noqa: E402 -- BLAS limits must precede NumPy imports in spawned workers.
import os

for variable in ("OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import json
import multiprocessing
import platform
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ic_study.analysis.detection_boundary_v4 import profile_match, validate_fit
from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan


def batch(
    payload: tuple[Cell, tuple[float, float] | None, int, int, str, int],
) -> tuple[np.ndarray, float, float]:
    cell, parameters, start, count, phase, attempt = payload
    source = PanelSource(cell, SeedPlan(9001))
    wall, cpu = time.perf_counter(), time.process_time()
    values = source.profiles(
        phase,
        count,
        start=start,
        attempt=attempt,
        parameters=None if parameters is None else np.array(parameters),
    )
    return values, time.process_time() - cpu, time.perf_counter() - wall


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = []
    with ProcessPoolExecutor(
        max_workers=8, mp_context=multiprocessing.get_context("spawn")
    ) as pool:
        for label, cell, parameters in (
            ("anchor-social", Cell(0, 0.7), None),
            ("main-social", Cell(0.03, 0.7), None),
            ("main-null-B", Cell(0.03, 0.7), (0.85, 0.1)),
            ("main-null-C", Cell(0.03, 0.7, family="C"), (0.85, 0.0)),
            ("main-null-D", Cell(0.03, 0.7, family="D"), (0.85, 0.1)),
            ("main-null-E", Cell(0.03, 0.7, family="E"), (0.85, 0.1)),
            ("c050", Cell(0.03, 0.7, error_correlation=0.5), None),
            ("delta020", Cell(0.03, 0.7, gain=0.2), None),
            ("omega100", Cell(0.03, 0.7, anchor=1), None),
            ("steps24-social", Cell(0.03, 0.7, steps=24), None),
            ("steps24-null", Cell(0.03, 0.7, steps=24), (0.85, 0.1)),
        ):
            started = time.perf_counter()
            results = list(
                pool.map(
                    batch, [(cell, parameters, j * 8, 8, "match", 0) for j in range(8)]
                )
            )
            records.append(
                {
                    "operation": label,
                    "cell": asdict(cell),
                    "panels": 64,
                    "cpu_seconds": sum(v[1] for v in results),
                    "worker_wall_seconds": sum(v[2] for v in results),
                    "wall_seconds": time.perf_counter() - started,
                }
            )
        counters = {"panels": 0, "cpu_seconds": 0.0, "worker_wall_seconds": 0.0}
        cell = Cell(0.03, 0.7)

        def evaluate(
            parameters: tuple[float, float] | None, phase: str, count: int, attempt: int
        ) -> np.ndarray:
            results = list(
                pool.map(
                    batch,
                    [
                        (cell, parameters, j, min(32, count - j), phase, attempt)
                        for j in range(0, count, 32)
                    ],
                )
            )
            counters["panels"] += count
            counters["cpu_seconds"] += sum(v[1] for v in results)
            counters["worker_wall_seconds"] += sum(v[2] for v in results)
            return np.concatenate([v[0] for v in results])[:, :2]

        attempts = []
        for attempt, count in enumerate((1024, 4096)):
            previous = counters.copy()
            started = time.perf_counter()
            target = evaluate(None, "match", count, attempt)
            fit = profile_match(
                target,
                lambda phi, eta, count=count, attempt=attempt: evaluate(
                    (phi, eta), "match", count, attempt
                ),
            )
            solver = {key: counters[key] - previous[key] for key in counters}
            solver.update(
                {
                    "wall_seconds": time.perf_counter() - started,
                    "evaluations": fit.evaluations,
                    "status": fit.status,
                    "matching_pairs": count,
                    "attempt": attempt,
                }
            )
            if fit.success:
                started = time.perf_counter()
                previous_validation = counters.copy()
                validation = validate_fit(
                    evaluate(tuple(fit.parameters), "validate", 2048, attempt)
                    - evaluate(None, "validate", 2048, attempt),
                    2,
                    fit.se,
                )
                solver["independent_validation_pass"] = validation.passed
                solver["validation_wall_seconds"] = time.perf_counter() - started
                solver["validation_cost"] = {
                    key: counters[key] - previous_validation[key] for key in counters
                }
            attempts.append(solver)
            if not fit.success or validation.passed:
                break
        result = {
            "kind": "isolated-cost-probes-not-G0",
            "workers": 8,
            "blas_threads": 1,
            "size": 10626,
            "waves": 11,
            "seed_repetition": 9001,
            "classifiers_trained": 0,
            "host": {
                "system": platform.system(),
                "machine": platform.machine(),
                "python": platform.python_version(),
            },
            "panels": records,
            "solver_attempts": attempts,
            "a": cell.share,
            "r": cell.reliability,
            "supersedes": "cost-measurements.json",
            "total_solver_and_validation": counters,
        }
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(
            json.dumps(
                {
                    "cost_measurements_written": True,
                    "solver_evaluations": fit.evaluations,
                    "solver_status": fit.status,
                }
            )
        )


if __name__ == "__main__":
    main()
