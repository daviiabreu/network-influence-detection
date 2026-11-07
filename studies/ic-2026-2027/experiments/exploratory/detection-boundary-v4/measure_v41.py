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
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan, fit_cell


def task(payload):
    cell, seeds, parameters, phase, attempt, start, count = payload
    source = PanelSource(cell, seeds)
    cpu, wall = time.process_time(), time.perf_counter()
    values = source.profiles(
        phase, count, start=start, attempt=attempt, parameters=parameters
    )
    return values, time.process_time() - cpu, time.perf_counter() - wall


class MeasuredSource(PanelSource):
    def __init__(self, cell, seeds, pool):
        super().__init__(cell, seeds)
        self.pool = pool
        self.costs = {}

    def profiles(self, phase, count, *, parameters=None, attempt=0, start=0):
        if phase not in {"match", "validate"}:
            raise ValueError("Cost probes forbid training and AUC phases")
        started = time.perf_counter()
        results = list(
            self.pool.map(
                task,
                [
                    (
                        self.cell,
                        self.seeds,
                        parameters,
                        phase,
                        attempt,
                        j,
                        min(32, start + count - j),
                    )
                    for j in range(start, start + count, 32)
                ],
            )
        )
        key = f"{attempt}:{phase}"
        cost = self.costs.setdefault(
            key,
            dict(panels=0, cpu_seconds=0.0, worker_wall_seconds=0.0, wall_seconds=0.0),
        )
        cost["panels"] += count
        cost["cpu_seconds"] += sum(r[1] for r in results)
        cost["worker_wall_seconds"] += sum(r[2] for r in results)
        cost["wall_seconds"] += time.perf_counter() - started
        return np.concatenate([r[0] for r in results])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("panels", "fits"), required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Preserve completed measurements")
    study = Path(__file__).resolve().parents[3]
    files = [Path(__file__), *sorted((study / "src").rglob("*.py")), study / "uv.lock"]
    provenance = {
        str(p.relative_to(study)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
    }
    rows = []
    configurations = []
    for family in "ABCDE":
        for channel in ("observed", "latent", "ordinal_one", "latent_rank"):
            for mobility in (False, True):
                if mobility and channel == "latent_rank":
                    continue
                for alternative in (True, False):
                    summary = "mobility" if mobility else "lags"
                    arm = "social" if alternative else "null"
                    name = f"{family}:{channel}:{summary}:{arm}"
                    configurations.append(
                        (
                            name,
                            Cell(
                                0.03,
                                0.7,
                                family=family,
                                channel=channel,
                                mobility=mobility,
                            ),
                            alternative,
                        )
                    )
    configurations += [
        ("anchor-social", Cell(0, 0.7), True),
        ("c050", Cell(0.03, 0.7, error_correlation=0.5), True),
        ("delta020", Cell(0.03, 0.7, gain=0.2), True),
        ("omega100", Cell(0.03, 0.7, anchor=1), True),
        ("steps24-social", Cell(0.03, 0.7, steps=24), True),
        ("steps24-null", Cell(0.03, 0.7, steps=24), False),
    ]
    with ProcessPoolExecutor(
        max_workers=8, mp_context=multiprocessing.get_context("spawn")
    ) as pool:
        if args.mode == "panels":
            for name, cell, alternative in configurations:
                parameters = (
                    None
                    if alternative
                    else np.array([0.85, 0 if cell.family in "AC" else 0.1])
                )
                started = time.perf_counter()
                results = list(
                    pool.map(
                        task,
                        [
                            (cell, SeedPlan(9002), parameters, "match", 0, 8 * i, 8)
                            for i in range(8)
                        ],
                    )
                )
                rows.append(
                    dict(
                        operation=name,
                        cell=asdict(cell),
                        panels=64,
                        cpu_seconds=sum(r[1] for r in results),
                        worker_wall_seconds=sum(r[2] for r in results),
                        wall_seconds=time.perf_counter() - started,
                    )
                )
        else:
            for block in range(8):
                for share in (0.003, 0.03, 0.30):
                    source = MeasuredSource(
                        Cell(share, 0.7), SeedPlan(9001, block), pool
                    )
                    result = fit_cell(source)
                    row = dict(
                        block=block,
                        a=share,
                        r=0.7,
                        success=result.success,
                        costs=source.costs,
                        attempts=[
                            dict(
                                count=a.count,
                                evaluations=a.fit.evaluations,
                                status=a.fit.status,
                                validation_passed=None
                                if a.validation is None
                                else a.validation.passed,
                            )
                            for a in result.attempts
                        ],
                    )
                    rows.append(row)
                    with args.output.with_suffix(".progress.jsonl").open("a") as handle:
                        handle.write(json.dumps(row) + "\n")
                    print(json.dumps(row), flush=True)
    result = {
        "kind": "v4.1-cost-only-" + args.mode,
        "seed_repetition": 9002 if args.mode == "panels" else 9001,
        "phase": "match",
        "workers": 8,
        "OPENBLAS_NUM_THREADS": 1,
        "VECLIB_MAXIMUM_THREADS": 1,
        "classifiers_trained": 0,
        "measurements": rows,
        "code": provenance,
        "python": platform.python_version(),
        "command": sys.argv,
        "numpy": np.__version__,
        "host_sha256": hashlib.sha256(
            (platform.node() + platform.machine()).encode()
        ).hexdigest(),
    }
    with args.output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"measurements": len(rows), "classifiers_trained": 0}))


if __name__ == "__main__":
    main()
