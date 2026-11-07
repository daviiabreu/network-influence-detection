"""Artificial-data calibration only: no simulator, classifier, or gate import."""

from __future__ import annotations

# ruff: noqa: E402 -- BLAS limits must precede NumPy imports in spawned workers.
import os

for variable in ("OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import hashlib
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from ic_study.simulation.v4_criteria import dispersion, fd_stability, refit_ratio


def trial(payload: tuple[int, int]) -> list[float]:
    index, cells = payload
    rng = np.random.default_rng(250925000 + index)
    # Student t(5.2) has ordinary kurtosis 3 + 6/(5.2-4) = 8.
    logits = np.linspace(-0.2, 2, cells)[:, None] + 0.025 * rng.standard_t(
        5.2, (cells, 100)
    ) / np.sqrt(5.2 / 3.2)
    probabilities = 1 / (1 + np.exp(-logits))
    errors = 0.025 * probabilities * (1 - probabilities)
    success = rng.random((cells, 100)) >= 0.01
    report = dispersion(probabilities, errors, success, seed=index + 99)
    output = [
        min(report["cell_upper"]),
        max(report["cell_lower"]),
        report["pooled_upper"],
        report["pooled_lower"],
    ]
    refit_allowed = []
    for count in (100, 40):
        local = rng.standard_t(5.2, 2000)
        refits = rng.standard_t(5.2, count)
        refits[rng.random(count) < 0.01] = np.nan
        comparison = refit_ratio(local, refits, seed=index + count)
        output += [float(comparison["lower"]), float(comparison["upper"])]
        refit_allowed.append(
            int(comparison["failure_count"]) <= (3 if count == 100 else 2)
        )
    # Artificial nonlinear FD perturbations: log-ratio SD .25, median ratio one.
    # Per-pipeline outliers are allowed; the predeclared cell median is tested.
    variances = np.stack(
        [np.ones((cells, 100)), np.exp(rng.normal(0, 0.25, (cells, 100)))], axis=-1
    )
    stability = fd_stability(variances, success)
    output += [float(report["failure_allowance_met"]), float(stability["fd_stable"])]
    # Independent refit failures were already counted by the same production rule.
    # Return their counts separately from scale-sensitive variance comparisons.
    return [*output, float(all(refit_allowed))]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", type=int, default=7)
    parser.add_argument("--trials", type=int, default=3000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with ProcessPoolExecutor(
        max_workers=8, mp_context=multiprocessing.get_context("spawn")
    ) as pool:
        data = np.array(
            list(
                pool.map(
                    trial,
                    [(i, args.cells) for i in range(2 * args.trials)],
                    chunksize=10,
                )
            )
        )
    development, validation = np.split(data, 2)
    # Allocate at most 0.5% Monte Carlo development rejection to G2.
    thresholds = np.array(
        [
            np.quantile(development[:, 0], 0.00125),
            np.quantile(development[:, 1], 0.99875),
            np.quantile(development[:, 2], 0.00125),
            np.quantile(development[:, 3], 0.99875),
        ]
    )
    reports = {}
    for label, scale in (
        ("correct", 1.0),
        ("understated_20_percent", 0.8),
        ("inflated_40_percent", 1.4),
    ):
        statistics = validation[:, :4] / scale**2
        g2_statistics = (
            (statistics[:, 0] >= thresholds[0])
            & (statistics[:, 1] <= thresholds[1])
            & (statistics[:, 2] >= thresholds[2])
            & (statistics[:, 3] <= thresholds[3])
        )
        g2 = (
            g2_statistics
            & validation[:, 8].astype(bool)
            & validation[:, 9].astype(bool)
        )
        g2c = (
            (validation[:, 5] * scale**2 >= 0.8)
            & (validation[:, 4] * scale**2 <= 2)
            & (validation[:, 7] * scale**2 >= 0.8)
            & (validation[:, 6] * scale**2 <= 2)
            & validation[:, 10].astype(bool)
        )
        reports[label] = {}
        for key, values in (
            ("G2", g2),
            ("G2c", g2c),
            ("joint", g2 & g2c),
            (
                "G2_given_failure_allowance",
                (g2_statistics & validation[:, 9].astype(bool))[
                    validation[:, 8].astype(bool)
                ],
            ),
        ):
            rate = float(values.mean())
            reports[label][key] = {
                "pass_count": int(values.sum()),
                "denominator": len(values),
                "probability": rate,
                "mcse": float(np.sqrt(rate * (1 - rate) / len(values))),
            }
    result = {
        "kind": "artificial-criteria-calibration-not-a-gate",
        "schema": 2,
        "seed_base": 250925000,
        "development_trials": args.trials,
        "validation_trials": args.trials,
        "bootstrap_replicates": 399,
        "workers": 8,
        "ordinary_kurtosis": 8,
        "G2_cells": args.cells,
        "pipelines_per_cell": 100,
        "disjoint_pairs_per_cell": 50,
        "G2c_refits": [100, 40],
        "local_draws": 2000,
        "dependence": (
            "Independent pipelines; LOO dependence retained, paired differences "
            "resampled in intact pairs; independent gate cells."
        ),
        "failure_rate": 0.01,
        "failure_model": (
            "Independent Bernoulli technical gaps in each G2 pipeline and "
            "G2c refit; independent of data."
        ),
        "failure_rule": {
            "G2_per_100": 5,
            "G2_pooled": "ceil(0.02 * pipelines actually run)",
            "G2c_per_100": 3,
            "G2c_per_40": 2,
            "ratio_pairs": (
                "Drop any pair with a gap; retain all planned attempts in denominators."
            ),
        },
        "fd_model": {
            "per_pipeline_log_ratio_mean": 0,
            "per_pipeline_log_ratio_sd": 0.25,
            "cell_statistic": "median",
            "accepted_interval": [0.8, 1.25],
        },
        "thresholds": dict(
            zip(
                ("cell_lower", "cell_upper", "pooled_lower", "pooled_upper"),
                thresholds.tolist(),
                strict=True,
            )
        ),
        "G2c_fixed_thresholds": {
            "one_sided_95_upper_minimum": 0.8,
            "one_sided_95_lower_maximum": 2.0,
        },
        "operating_characteristics": reports,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "implementation_sha256": hashlib.sha256(
            Path(__file__)
            .parents[3]
            .joinpath("src/ic_study/simulation/v4_criteria.py")
            .read_bytes()
        ).hexdigest(),
        "failure_allowance_pass_probability": float(validation[:, 8].mean()),
        "fd_aggregate_pass_probability": float(validation[:, 9].mean()),
        "supersedes": "criteria-v42.json",
        "supersedes_sha256": hashlib.sha256(
            Path(__file__).with_name("criteria-v42.json").read_bytes()
        ).hexdigest(),
        "conditional_on": [
            "Available G2c local draws; a failed real baseline still blocks G2c",
            "Declared independent 1% gap model and per-cell median FD model",
        ],
    }
    result["joint_targets_met"] = (
        reports["correct"]["joint"]["probability"] >= 0.95
        and reports["understated_20_percent"]["G2"]["probability"] <= 0.20
    )
    with args.output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
