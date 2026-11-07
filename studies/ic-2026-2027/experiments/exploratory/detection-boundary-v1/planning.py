"""Analytic planning assumptions; no simulation, scores, or confirmatory seeds."""

import json
from math import sqrt
from pathlib import Path
from statistics import NormalDist

normal = NormalDist()
cells = 9 * 9
networks = 2000
critical = normal.inv_cdf(1 - 0.05 / (2 * cells))
rows = []
for nuisance_sd in (0.01, 0.02):
    se = sqrt(1 / (2 * networks) + nuisance_sd**2)
    rows.append(
        {
            "nuisance_sd_assumption": nuisance_sd,
            "auc_se_bound_plus_assumed_nuisance": se,
            "band_halfwidth_reference": critical * se,
            "power_if_true_auc_080": normal.cdf(0.1 / se - critical),
            "power_if_true_auc_075": normal.cdf(0.05 / se - critical),
            "true_auc_for_80pct_power": 0.7 + (critical + normal.inv_cdf(0.8)) * se,
        }
    )
result = {
    "effective_independent_networks_per_class": networks,
    "events_per_network": 2,
    "within_network_icc_worst_case": 1,
    "joint_cells": cells,
    "bonferroni_two_sided_critical_reference": critical,
    "assumptions": (
        "Normal AUC approximation, independent classes, nuisance variance additive; "
        "not measured power or actual bootstrap critical value"
    ),
    "scenarios": rows,
}
Path(__file__).with_name("power-planning.json").write_text(
    json.dumps(result, indent=2) + "\n"
)
