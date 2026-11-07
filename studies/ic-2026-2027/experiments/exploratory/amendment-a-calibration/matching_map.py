"""Calibrate a response derivative on disjoint matching-only seed blocks."""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from ic_study.simulation.amendment_a import calibration_profiles


def evaluate(task: tuple[float, float, float]) -> list[float]:
    share, rho, trait = task
    return (
        calibration_profiles(
            share, 0.7, 1024, block=9001, phase="match", rho=rho, trait=trait, lags=2
        )
        .mean(0)
        .tolist()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    tasks = []
    points = []
    for a in (0.03, 0.1):
        fit = json.loads((args.output / f"match-{a}-1024-1.json").read_text())
        points.append((fit["rho"], fit["trait"]))
        tasks.extend(
            [
                (a, fit["rho"], fit["trait"]),
                (a, fit["rho"] + 0.01, fit["trait"]),
                (a, fit["rho"], fit["trait"] + 0.01),
            ]
        )
    with ProcessPoolExecutor(max_workers=6) as pool:
        values = list(pool.map(evaluate, tasks))
    for k, a in enumerate((0.03, 0.1)):
        base, rho, trait = np.array(values[3 * k : 3 * k + 3])
        row = dict(
            share=a,
            initial=points[k],
            jacobian=np.stack(
                ((rho - base) / 0.01, (trait - base) / 0.01), axis=1
            ).tolist(),
            count=1024,
            block=9001,
            step=0.01,
            combined_wall_seconds=time.perf_counter() - started,
        )
        with (args.output / f"matching-map-{a}.json").open("x") as stream:
            json.dump(row, stream, indent=2)
        print(json.dumps(row))


if __name__ == "__main__":
    main()
