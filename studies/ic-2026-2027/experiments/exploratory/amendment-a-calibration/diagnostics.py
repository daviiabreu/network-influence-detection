"""Reference and exact-equality diagnostics for the isolated proposal A functions."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from ic_study.analysis.redesign import fit_discriminant
from ic_study.simulation.amendment_a import (
    NAMESPACE,
    bonferroni_band,
    calibration_profiles,
    cluster_auc_se,
    seed_a,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", choices=["zero", "mechanics"], required=True)
    args = parser.parse_args()
    result_path = args.output / f"diagnostic-{args.mode}.json"
    if result_path.exists():
        print(result_path.read_text())
        return
    started = time.perf_counter()
    if args.mode == "zero":
        null = calibration_profiles(0, 0.7, 2000, block=0, phase="train", rho=0.85)[
            :, 2:5
        ]
        social = calibration_profiles(0, 0.7, 2000, block=0, phase="train")[:, 2:5]
        model = fit_discriminant(
            np.concatenate((null, social)), np.repeat([0, 1], 2000)
        )
        samples = [
            np.concatenate(
                [
                    np.load(args.output / f"zero-{label}-{chunk}.npy")
                    for chunk in range(8)
                ]
            )
            for label in (0, 1)
        ]
        value, se = cluster_auc_se(*(model.score(x).reshape(-1, 2) for x in samples))
        row = {
            "auc": value,
            "mc_se": se,
            "z_from_half": (value - 0.5) / se,
            "networks_per_class": 20000,
            "events_per_network": 2,
            "rho": 0.85,
            "trait": 0,
            "matching": "exact known equality point",
            "training_events_per_class": 2000,
        }
    else:
        rng = np.random.default_rng(seed_a(7000, "check", "state", 0))
        covered, widths = [], []
        for _ in range(2000):
            samples = [
                np.sqrt(0.3) * rng.normal(size=(2000, 1, 1))
                + np.sqrt(0.3) * rng.normal(size=(2000, 2, 1))
                + np.sqrt(0.4) * rng.normal(size=(2000, 2, 9))
                for _ in range(2)
            ]
            stats = np.array(
                [
                    cluster_auc_se(samples[0][..., k], samples[1][..., k])
                    for k in range(9)
                ]
            )
            low, high = bonferroni_band(stats[:, 0], stats[:, 1], networks=2000)
            covered.append(bool(np.all((low <= 0.5) & (high >= 0.5))))
            widths.append(float(np.mean(high - low)))
        p = float(np.mean(covered))
        row = {
            "repetitions": 2000,
            "covered": sum(covered),
            "coverage": p,
            "mc_se": float(np.sqrt(p * (1 - p) / 2000)),
            "mean_width": float(np.mean(widths)),
            "law": "identical Gaussian scores; network/event effects; nine cells",
            "scope": "band mechanics only, not full panel matching and training",
        }
    row.update(namespace=NAMESPACE, seconds=time.perf_counter() - started)
    with (args.output / f"diagnostic-{args.mode}.json").open("x") as stream:
        json.dump(row, stream, indent=2)
        stream.write("\n")
    print(json.dumps(row))


if __name__ == "__main__":
    main()
