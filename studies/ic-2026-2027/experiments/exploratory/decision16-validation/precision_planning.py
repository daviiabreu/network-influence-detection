"""Known-curve normal planning calculation, not a scientific contrast."""

import hashlib
import json
from pathlib import Path
from statistics import NormalDist

import numpy as np

namespace = "ic-detection-boundary-v3-precision-calibration"
seed = int.from_bytes(hashlib.sha256(namespace.encode()).digest()[:8], "big")
rng = np.random.default_rng(seed)
critical = NormalDist().inv_cdf(1 - 0.05 / (2 * 9))
rows = []
for nuisance_sd in (0.01, 0.02):
    se = np.sqrt(1 / (2 * 2000) + nuisance_sd**2)
    for gap in (0.04, 0.08, 0.12):
        truth = np.array(
            [0.5, 0.51, 0.54, 0.7 - gap, 0.7 + gap, 0.90, 0.94, 0.97, 0.99]
        )
        estimates = np.clip(
            truth + rng.normal(0, se, (100000, 9)), 1 / 4000, 1 - 1 / 4000
        )
        theta = np.log(estimates / (1 - estimates))
        logit_se = se / (estimates * (1 - estimates))
        lower = 1 / (1 + np.exp(-theta + critical * logit_se))
        upper = 1 / (1 + np.exp(-theta - critical * logit_se))
        lo = np.where(upper >= 0.7, np.arange(9), 9).min(1)
        hi = np.where(lower >= 0.7, np.arange(9), 9).min(1)
        valid = (lower[:, 0] <= 0.5) & (upper[:, 0] >= 0.5)
        resolved = valid & (lo <= 4) & (hi >= 4) & (hi < 9) & (hi - lo <= 1)
        rows.append(
            {
                "nuisance_sd": nuisance_sd,
                "adjacent_auc_gap_from_target": gap,
                "se": float(se),
                "probability_valid_covering_width_at_most_one_step": float(
                    resolved.mean()
                ),
                "null_gate_pass_rate": float(valid.mean()),
            }
        )
result = {
    "namespace": namespace,
    "seed": seed,
    "draws_per_scenario": 100000,
    "critical_9_cells": critical,
    "effective_networks_per_class": 2000,
    "assumptions": (
        "Independent normal AUC errors, specified monotone curve; "
        "logit delta bands with Bonferroni reference. "
        "Not measured scientific power or actual bootstrap critical."
    ),
    "scenarios": rows,
}
Path(__file__).with_name("precision-planning.json").write_text(
    json.dumps(result, indent=2) + "\n"
)
