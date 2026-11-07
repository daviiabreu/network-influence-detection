"""Successor projection preserves measured lineage and charges full refit work."""

import copy
import json
import runpy
from pathlib import Path
from typing import Any

import pytest

PROJECTION = (
    Path(__file__).resolve().parents[2]
    / "experiments/exploratory/detection-boundary-v4/project_v42.py"
)


def records(evaluations: int) -> dict[str, Any]:
    module = runpy.run_path(str(PROJECTION))
    return {
        "classifiers_trained": 0,
        "measurements": [
            {
                "a": a,
                "r": r,
                "block": block,
                "success": True,
                "attempts": [{"evaluations": evaluations, "status": "interior"}],
            }
            for a, r in sorted(module["EXPECTED_CELLS"])
            for block in range(4)
        ],
    }


def test_projection_rejects_partial_or_unpaired_matching_measurements() -> None:
    validate = runpy.run_path(str(PROJECTION))["validate_complete_comparison"]
    before, after = records(60), records(20)
    validate(before, after)
    partial = copy.deepcopy(after)
    partial["measurements"].pop()
    with pytest.raises(ValueError, match="four blocks"):
        validate(before, partial)
    unpaired = copy.deepcopy(after)
    unpaired["measurements"][0]["block"] = 4
    with pytest.raises(ValueError, match="paired"):
        validate(before, unpaired)


def test_projection_uses_optimized_counts_and_separate_historical_timings(
    tmp_path: Path,
) -> None:
    module = runpy.run_path(str(PROJECTION))
    for name in ("panel-cost-v41.json", "inventory.json"):
        (tmp_path / name).write_bytes((PROJECTION.parent / name).read_bytes())
    for name, evaluations in (
        ("cost-fits-v42-before.json", 60),
        ("cost-fits-v42-after.json", 20),
        ("cost-fits-v41.json", 55),
    ):
        (tmp_path / name).write_text(json.dumps(records(evaluations)))
    result = module["build_projection"](tmp_path)
    assert result["solver_evaluations_assumed"] == [20, 96]
    assert result["empirical_retry_fraction"] == 0
    assert result["retry_evaluations_source"] == "unobserved: conservative budget 96"
    (tmp_path / "cost-fits-v41.json").write_text(json.dumps(records(64)))
    updated_history = module["build_projection"](tmp_path)
    assert result["scenarios"] == updated_history["scenarios"]
    assert (
        result["historical_matching_summary"]
        != updated_history["historical_matching_summary"]
    )
    factor = 1.25 / (8 * 3600)
    measured = result["scenarios"]["measured"]
    assert measured["gate_hours"]["score_bootstrap"] == factor * (852 / 9) * 15.70
    assert measured["tier_hours"]["score_bootstrap"] == factor * 414 * 15.70


def test_refits_regenerate_both_references_and_retry_has_independent_budget() -> None:
    budget = runpy.run_path(str(PROJECTION))["panel_budget"]
    matching = budget(evaluations=20, matching=1024, dimensions=2, kind="match")
    refit = budget(evaluations=20, matching=1024, dimensions=2, kind="refit")
    assert refit["social"] - matching["social"] == 2000 + 4000
    assert refit["null"] - matching["null"] == 2000 + 4000
    retry = budget(evaluations=96, matching=4096, dimensions=2, kind="match")
    assert retry == {"social": 6144, "null": 403456}


def test_cheap_gap_does_not_discount_projected_successful_work() -> None:
    module = runpy.run_path(str(PROJECTION))
    after = records(40)["measurements"]
    before = records(60)["measurements"]
    baseline = module["evaluation_assumption"](after)
    gap = after[0]
    gap["success"] = False
    gap["attempts"] = [{"evaluations": 2, "status": "non-monotone-profile"}]
    updated = module["evaluation_assumption"](after)
    assert updated["all_planned_initial_mean"] < baseline["all_planned_initial_mean"]
    assert updated["projected_initial_evaluations"] == 40
    paired = module["paired_success_comparison"](before, after)
    assert paired["planned_pairs"] == 24
    assert paired["validated_pairs"] == 23
    assert paired["excluded_pairs"] == 1
    assert paired["before_initial_mean"] == 60
    assert paired["after_initial_mean"] == 40
    counts = module["fit_accounting"](after)
    assert counts["failures"] == 1
    assert counts["final_statuses"] == {"interior": 23, "non-monotone-profile": 1}
    for row in after:
        row["success"] = False
    assert module["evaluation_assumption"](after)["projected_initial_evaluations"] == 96
