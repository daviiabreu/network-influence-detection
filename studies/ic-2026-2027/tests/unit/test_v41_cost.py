"""Projection charges actual mean stencils and G2-only covariance panels."""

import runpy
from pathlib import Path


def test_panel_budget_removes_confirmatory_drift_but_charges_g2_covariance() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "experiments/exploratory/detection-boundary-v4/project_v41.py"
    )
    budget = runpy.run_path(str(path))["panel_budget"]
    main = budget(evaluations=30, matching=1024, dimensions=2)
    assert main == {"social": 13072, "null": 44816}
    gate = budget(evaluations=30, matching=1024, dimensions=2, g2=True)
    assert gate == {"social": 13072, "null": 70864}
    control = budget(evaluations=30, matching=1024, dimensions=2, fit_dimensions=1)
    assert control == main
    anchor = budget(evaluations=1, matching=1024, dimensions=2, identity=True)
    assert anchor == {"social": 9072, "null": 9072}
    retry = budget(evaluations=64, matching=4096, dimensions=2, kind="match")
    assert retry == {"social": 6144, "null": 272384}


def test_full_refits_charge_social_reference_regeneration_in_each_task() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "experiments/exploratory/detection-boundary-v4/project_v41.py"
    )
    budget = runpy.run_path(str(path))["panel_budget"]
    assert budget(evaluations=30, matching=1024, dimensions=2, kind="refit") == {
        "social": 9072,
        "null": 40816,
    }
