from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ic_study.analysis.forecast_pilot import cells, summarize, trajectory


def specification() -> dict[str, Any]:
    path = (
        Path(__file__).resolve().parents[2]
        / "experiments/exploratory/probabilistic-forecast-pilot-v1/spec.json"
    )
    return json.loads(path.read_text())  # type: ignore[no-any-return]


def test_json_roundtrip_and_precision_reuse_only_observations() -> None:
    spec = specification()
    cell = cells(spec)[8]
    primary = trajectory(spec, cell, 0, "primary", 2)
    reordered = json.loads(json.dumps(spec, sort_keys=True))
    assert primary == trajectory(reordered, cell, 0, "primary", 2)
    precision = trajectory(spec, cell, 0, "precision", 2)
    confirmation = trajectory(spec, cell, 0, "confirmation", 2)
    for a, b, c in zip(
        primary["waves"], precision["waves"], confirmation["waves"], strict=True
    ):
        assert a["observed"] == b["observed"]
        assert a["outcome"] == b["outcome"]
        assert a["data_seed"] == b["data_seed"]
        assert a["data_seed"] != c["data_seed"]
        assert a["forecasts"] != b["forecasts"]


def test_selection_uses_only_training_and_summary_clusters_trajectories() -> None:
    spec = specification()
    cell = cells(spec)[4]
    rows = [trajectory(spec, cell, r, "primary", 3) for r in range(2)]
    for row in rows:
        for score, choice in row["selected_on_train"].items():
            training = row["waves"][: spec["train_steps"]]
            optimum = min(
                spec["model_order"],
                key=lambda m: sum(w["forecasts"][m]["scores"][score] for w in training),
            )
            assert choice == optimum
    summary = summarize(rows, spec)[0]
    assert summary["scores"]["energy"]["losses"]["constant"]["n"] == 2
    assert sum(summary["scores"]["energy"]["selected_model_counts"].values()) == 2
