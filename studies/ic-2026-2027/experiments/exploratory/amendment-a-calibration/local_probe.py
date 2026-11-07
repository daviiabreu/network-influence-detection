"""Measure local-bootstrap stencils against saved full refits."""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.simulation.amendment_a import (
    LocalNuisance,
    calibration_profiles,
    local_nuisance_draws,
)


def stencil(task: tuple[float, float, int, str]) -> dict[str, Any]:
    a, h, j, destination = task
    out = Path(destination)
    fit = json.loads((out / f"refit-{a}-1.json").read_text())
    parameters = np.array([fit["rho"], fit["trait"]])
    step = h if parameters[j] + h <= (0.999, 0.8)[j] else -h
    parameters[j] += step
    kwargs = dict(rho=float(parameters[0]), trait=float(parameters[1]))
    started = time.perf_counter()
    samples = {
        phase: calibration_profiles(
            a,
            0.7,
            count,
            block=1,
            phase=phase,
            lags=2 if phase == "match" else 5,
            **kwargs,
        )
        for phase, count in (("match", 256), ("train", 2000), ("reference", 4000))
    }
    name = f"stencil-{a}-{h}-{j}.npz"
    with (out / name).open("xb") as stream:
        np.savez_compressed(stream, **samples)
    return dict(
        share=a,
        step=step,
        h=h,
        parameter=j,
        file=name,
        seconds=time.perf_counter() - started,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--aggregate-only", action="store_true")
    args = parser.parse_args()
    started = time.perf_counter()
    tasks = [
        (a, h, j, str(args.output))
        for a in (0.03, 0.1)
        for h in (0.005, 0.01)
        for j in (0, 1)
    ]
    if args.aggregate_only:
        rows = [
            json.loads((args.output / f"stencil-{a}-{h}-{j}.json").read_text())
            for a, h, j, _ in tasks
        ]
    else:
        with ProcessPoolExecutor(max_workers=8) as pool:
            rows = list(pool.map(stencil, tasks))
    summaries = []
    for a in (0.03, 0.1):
        fit = json.loads((args.output / f"refit-{a}-1.json").read_text())
        parameters = np.array([fit["rho"], fit["trait"]])
        base = np.load(args.output / f"refit-data-{a}.npz")
        target = calibration_profiles(a, 0.7, 256, block=1, phase="match", lags=2)
        null = calibration_profiles(
            a,
            0.7,
            256,
            block=1,
            phase="match",
            lags=2,
            rho=fit["rho"],
            trait=fit["trait"],
        )
        for h in (0.005, 0.01):
            deriv = [np.load(args.output / f"stencil-{a}-{h}-{j}.npz") for j in (0, 1)]
            steps = [
                next(
                    r["step"]
                    for r in rows
                    if r["share"] == a and r["h"] == h and r["parameter"] == j
                )
                for j in (0, 1)
            ]
            jacobian = np.stack(
                [
                    (d["match"].mean(0) - null.mean(0)) / s
                    for d, s in zip(deriv, steps, strict=True)
                ],
                axis=1,
            )
            data = LocalNuisance(
                parameters,
                null - target,
                jacobian,
                base["null_train"],
                base["social_train"],
                base["null_reference"],
                base["social_reference"],
                np.stack(
                    [
                        (d["train"][:, 2:5] - base["null_train"]) / s
                        for d, s in zip(deriv, steps, strict=True)
                    ]
                ),
                np.stack(
                    [
                        (d["reference"][:, 2:5] - base["null_reference"]) / s
                        for d, s in zip(deriv, steps, strict=True)
                    ]
                ),
            )
            boot_start = time.perf_counter()
            values = local_nuisance_draws(data)
            summaries.append(
                dict(
                    share=a,
                    h=h,
                    variance=float(values.var(ddof=1)),
                    mean=float(values.mean()),
                    jacobian=jacobian.tolist(),
                    condition=float(np.linalg.cond(jacobian)),
                    draws=2000,
                    bootstrap_seconds=time.perf_counter() - boot_start,
                )
            )
            with (args.output / f"local-draws-{a}-{h}.npy").open("xb") as stream:
                np.save(stream, values)
    report = dict(
        stencils=rows, summaries=summaries, wall_seconds=time.perf_counter() - started
    )
    with (args.output / "local-probe.json").open("x") as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
