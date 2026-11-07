"""Render watermarked SYNTHETIC sample figures and tables into ``samples/``.

Builds artificial release, gate and SHP records with the frozen emitters (see
``ic_study.analysis.v4_report_synthetic``), including the post-G0 second binding,
the G1c stage-summary successor that the frozen runner needs when a passing G1c
line cannot be appended, the SHP successor-1 sections and a synthetic crosswalk
aggregate, in a temporary directory outside the checkout, then runs the
reporting CLI path on them. No gate stage, confirmatory tier or real data is
touched.

    cd studies/ic-2026-2027
    uv run --frozen python \\
        experiments/exploratory/detection-boundary-v4/report/render_samples.py
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from ic_study.analysis.detection_v4_report import Inputs, render
from ic_study.analysis.v4_report_synthetic import (
    UnitPlan,
    build_gate,
    build_release,
    crosswalk_fixture,
    logistic_profile,
    shp_successor_fixture,
    stage_successor,
    unit_keys,
    write_release,
)
from ic_study.simulation.v4_curve import curve_units

HERE = Path(__file__).resolve().parent
CRITERIA = HERE.parent / "criteria-v43.json"
# Band straddling 0.70 at the top: the sustained upper end is not reached above
# the gap at a = 0.003.
PLATEAU = (0.5, 0.52, 0.55, 0.58, 0.62, 0.66, 0.69, 0.705, 0.705)


def sample_plans() -> dict[str, UnitPlan]:
    """Artificial scenario exercising every registered display state."""
    plans: dict[str, UnitPlan] = {}
    midpoints = {"B": 0.02, "A": 0.01, "C": 0.08, "D": 0.015, "E": 0.03}
    for family, tier in (("B", 1), ("A", 2), ("C", 2), ("D", 2), ("E", 2)):
        for r, key in unit_keys(tier=tier, family=family).items():
            midpoint = midpoints[family] * (0.9 / r) ** 4
            plans[key] = UnitPlan(logistic_profile(midpoint))
    b = unit_keys(tier=1, family="B")
    plans[b[0.55]] = UnitPlan(logistic_profile(0.9), gaps=frozenset({6}))
    plans[b[0.5]] = UnitPlan(logistic_profile(8.0))  # not reached on the grid
    plans[b[0.65]] = UnitPlan(PLATEAU, gaps=frozenset({2}))
    plans[b[0.9]] = UnitPlan(logistic_profile(0.02), partial_cells=4)  # main invalid
    c = unit_keys(tier=2, family="C")
    plans[c[0.5]] = UnitPlan((0.575, *logistic_profile(2.0)[1:]))  # null gate fails
    plans[c[0.55]] = UnitPlan(
        logistic_profile(0.1),
        gaps=frozenset({7, 8}),
        gap_status="family-limit-upper",
        gap_evaluations=0,  # screened by the feasibility pre-check
    )
    plans[c[0.6]] = UnitPlan(
        logistic_profile(0.1), gaps=frozenset({8}), gap_status="family-limit-upper"
    )
    plans[c[0.9]] = UnitPlan(logistic_profile(0.1), partial_cells=4)
    d = unit_keys(tier=2, family="D")
    plans[d[0.55]] = UnitPlan(
        logistic_profile(0.1), gaps=frozenset({5}), gap_status="interior"
    )  # validation failed in both attempts
    for r in (0.8, 0.85, 0.9):
        del plans[d[r]]
    e = unit_keys(tier=2, family="E")
    plans[e[0.75]] = UnitPlan(logistic_profile(0.1), gaps=frozenset({0}))
    for r in (0.8, 0.85, 0.9):
        plans[e[r]] = UnitPlan(logistic_profile(0.1), partial_cells=2)
    c025 = [u.key for u in curve_units() if u.key.startswith("t4-") and u.tier == 4]
    for key in c025[:2]:
        plans[key] = UnitPlan(logistic_profile(0.05))
    plans[c025[2]] = UnitPlan(logistic_profile(0.05), partial_cells=5)
    # Control reusing B's observed fits: a dependency gap at B's gap at r = 0.55.
    latent = unit_keys(tier=3, family="B", channel="latent")
    plans[latent[0.55]] = UnitPlan(logistic_profile(0.9))
    return plans


def main() -> int:
    out = HERE / "samples"
    with tempfile.TemporaryDirectory(prefix="v4-report-synthetic-") as tmp:
        root = Path(tmp)
        release = build_release(root / "confirmatory", sample_plans(), draws=200)
        curves = root / "released_curves_synthetic.json"
        write_release(curves, release)
        allocation = root / "v4-allocation_synthetic.json"
        gate = build_gate(root / "gate", allocation=allocation)
        successor = root / "G1c-aggregate-successor_synthetic.json"
        successor.write_text(
            json.dumps(stage_successor(gate), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        shp = root / "shp_synthetic.json"
        shp.write_text(
            json.dumps(shp_successor_fixture(), indent=2) + "\n", encoding="utf-8"
        )
        crosswalk = root / "crosswalk_synthetic.json"
        crosswalk.write_text(
            json.dumps(crosswalk_fixture(), indent=2) + "\n", encoding="utf-8"
        )
        if out.exists():
            shutil.rmtree(out)
        # Review the vector originals alongside small 150-dpi raster previews.
        inputs = Inputs(
            curves, gate, shp, CRITERIA, crosswalk, (successor,), allocation
        )
        render(inputs, out, dpi=150, synthetic=True, formats=("pdf", "png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
