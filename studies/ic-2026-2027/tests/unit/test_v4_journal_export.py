"""Journal projections use only public quantities and preserve censoring."""

from __future__ import annotations

from typing import Any

import pytest

from ic_study.analysis.v4_journal_export import build_journal

GRID = [0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 0.6, 0.9]
SHARES = (0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9)


def curve(
    key: str = "main",
    *,
    r: float = 0.5,
    family: str = "B",
    tier: int = 1,
    scenario: str = "main",
    channel: str = "observed",
    status: str = "completo válido",
    first: float | None = 0.1,
    interval: list[float | None] | None = None,
    gaps: dict[float, str] | None = None,
) -> dict[str, Any]:
    gaps = gaps or {}
    available = [a for a in GRID if a not in gaps]
    point = [0.50049, 0.501, 0.51, 0.53, 0.61234, 0.73456, 0.91, 0.97, 0.99]
    boundary = {
        "point": first,
        "interval": interval if interval is not None else [0.1, 0.3],
        "censoring": f"gap at a={min(gaps):g}" if first is None and gaps else None,
        "interval_censoring": None,
    }
    return {
        "meta": {
            "key": key,
            "r": r,
            "family": family,
            "tier": tier,
            "sensitivity": scenario,
            "channel": channel,
        },
        "status": status,
        "available": available,
        "auc": [p for a, p in zip(GRID, point, strict=True) if a not in gaps],
        "lower": [
            max(0, p - 0.02) for a, p in zip(GRID, point, strict=True) if a not in gaps
        ],
        "upper": [
            min(1, p + 0.02) for a, p in zip(GRID, point, strict=True) if a not in gaps
        ],
        "critical": 2.7729,
        "cell_gap": [gaps.get(a) for a in GRID],
        "diagnostics": [None] * len(GRID),
        "first": boundary,
        "sustained": {
            **boundary,
            "sustained": True,
            "censoring": f"gap at a={max(gaps):g}" if first is None and gaps else None,
        },
        "secondary": [{**boundary, "point": 0.1}, {**boundary, "point": 0.3}],
    }


def inputs(
    *curves: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if any(c["meta"]["tier"] == 1 for c in curves):
        existing = {c["meta"]["r"] for c in curves if c["meta"]["tier"] == 1}
        curves += tuple(curve(f"main-{r}", r=r) for r in SHARES if r not in existing)
    statuses = {c["meta"]["key"]: c["status"] for c in curves}
    public = {
        "schema": "ic-study.v4-public-aggregates.v1",
        "objects": {
            "release": {
                "curves": {c["meta"]["key"]: c for c in curves},
                "statuses": statuses,
            },
            "shp": None,
        },
    }
    rows = [
        {
            "tier": str(c["meta"]["tier"]),
            "family": c["meta"]["family"],
            "channel": c["meta"]["channel"],
            "sensitivity": c["meta"]["sensitivity"],
            "r": f"{c['meta']['r']:.2f}",
            "status": c["status"],
            "region": "large",
        }
        for c in curves
    ]
    return public, rows


def secondary_catalog(public: dict[str, Any]) -> dict[str, Any]:
    catalog = {
        "values": {
            f"v4.tab.T1sec.B.r{round(c['meta']['r'] * 100):03d}.a{target}.1": point
            for c in public["objects"]["release"]["curves"].values()
            if c["meta"]["tier"] == 1
            for target, point in (("060", "0.1"), ("080", "0.3"))
        }
    }
    if public["objects"]["shp"] is not None:
        catalog["values"].update(
            {
                "v4.shp.starts.estimate": "0.696",
                "v4.shp.starts.wald_lo": "0.685",
                "v4.shp.starts.wald_hi": "0.708",
            }
        )
    return catalog


def test_secondary_targets_follow_released_keys_when_record_order_changes() -> None:
    c = curve()
    c["secondary"].reverse()
    public, rows = inputs(c)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    assert result.values["j.b.r050.target060.point"] == "0.10"
    assert result.values["j.b.r050.target080.point"] == "0.30"


def test_secondary_targets_reject_disagreement_with_released_boundaries() -> None:
    public, rows = inputs(curve())
    catalog = secondary_catalog(public)
    catalog["values"]["v4.tab.T1sec.B.r050.a060.1"] = "0.03"
    with pytest.raises(ValueError, match="Secondary boundaries"):
        build_journal(public, {}, catalog, rows)


def test_formats_public_auc_bands_and_grid_strengths_without_changing_values() -> None:
    public, rows = inputs(curve())
    final = {"v4.tab.T1.B.r050.r": "0.50"}
    result = build_journal(public, final, secondary_catalog(public), rows)
    assert result.values["j.b.r050.a0300.auc"] == "0.612"
    assert result.values["j.b.r050.a0300.lower"] == "0.592"
    assert result.values["j.b.r050.a0300.upper"] == "0.632"
    assert result.values["j.b.r050.first.point"] == "0.10"
    assert result.values["j.b.r050.critical"] == "2.773"
    assert (
        r"\resultnum{v4.tab.T1.B.r050.r}{0.50}"
        in result.tables["journal-table-boundaries-B.tex"]
    )
    assert final == {"v4.tab.T1.B.r050.r": "0.50"}


def test_censoring_lists_actual_fit_gaps_and_keeps_later_auc_available() -> None:
    c = curve(r=0.55, gaps={0.6: "solver", 0.9: "solver"})
    c["sustained"] = {
        "point": None,
        "interval": [None, None],
        "censoring": "gap at a=0.9",
        "interval_censoring": "gap at a=0.9",
    }
    d = curve(
        "state", r=0.55, family="D", tier=2, first=None, gaps={0.1: "family_limit"}
    )
    public, rows = inputs(c, d)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    b_table = result.tables["journal-table-boundaries-B.tex"]
    assert (
        "censored (fit gaps at \\resultnum{j.b.r055.sustained.gap.0.a}{0.60}, "
        in b_table
    )
    assert r"\resultnum{j.b.r055.sustained.gap.1.a}{0.90}" in b_table
    assert result.values["j.b.r055.a6000.auc"] == "unavailable"
    assert result.values["j.models.D.r055.first_gap"] == "0.10"
    assert (
        "censored at first gap"
        in result.tables["journal-table-other-models.tex"].lower()
    )
    assert result.values["j.models.D.r055.a3000.auc"] == "0.910"


def test_sensitivity_selection_compares_regions_only_for_valid_pairs() -> None:
    public, rows = inputs(
        curve(),
        curve("attraction", tier=5, scenario="b000", interval=[0.03, 0.1]),
        curve("same", tier=4, scenario="c025"),
        curve("invalid", tier=5, scenario="omega025", status="completo inválido"),
    )
    rows[1]["region"] = "indeterminate"
    rows[3]["region"] = "NA"
    result = build_journal(
        public,
        {"v4.sens.n_pairs_compared": "2", "v4.sens.n_region_differs": "1"},
        secondary_catalog(public),
        rows,
    )
    assert result.values["j.sensitivity.n_pairs_compared"] == "2"
    assert result.values["j.sensitivity.n_region_differs"] == "1"
    assert (
        result.values["j.sensitivity.b000.r050.scenario"] == r"Attraction only ($b=0$)"
    )
    table = result.tables["journal-esm-sensitivity-differences.tex"]
    assert "Attraction only" in table
    assert "persistent response style" not in table.lower()
    assert "anchoring" not in table.lower()


def test_sensitivity_counts_refuse_disagreement_with_final_values() -> None:
    import pytest

    public, rows = inputs(curve())
    with pytest.raises(ValueError, match="n_pairs_compared"):
        build_journal(
            public, {"v4.sens.n_pairs_compared": "63"}, secondary_catalog(public), rows
        )


def exploratory_values() -> dict[str, str]:
    final = {
        "v4x.comparisons.by_r.0-5.x3.delta.point": "-0.27282",
        "v4x.comparisons.by_r.0-55.x3.delta.point": "-0.12614",
        "v4x.x7.units.r050.rich.first": "0.03",
        "v4x.x7.units.r090.rich.first": "0.003",
        "v4x.x7.units.r090.x7.first": "0.10",
        "v4x.x7.units.r050.delta_auc.i004.delta": "0.271234",
        "v4x.x7.units.r090.delta_auc.i004.delta": "0.338956",
        "v4x.comparisons.by_r.0-5.x4.P_or.statistics.power_or": "0.447",
        "v4x.comparisons.by_r.0-55.x4.P_or.statistics.power_or": "0.171",
        "v4x.comparisons.by_r.0-6.x4.P_or.statistics.power_or": "0.205",
        "v4x.x4.x4b.r050.a0000.x4b.power_pu": "0.3",
        "v4x.x4.x4b.r050.a0000.x4b.power_pu_interval_95.i000": "0.235",
        "v4x.x4.x4b.r050.a0000.x4b.power_pu_interval_95.i001": "0.365",
    }
    for r in SHARES:
        share = f"{r:g}".replace(".", "-")
        prefix = f"v4x.comparisons.by_r.{share}"
        final.setdefault(prefix + ".x3.delta.point", "-0.2")
        final.setdefault(prefix + ".x4.P_or.statistics.power_or", "0.2")
        feature = f"v4x.x7.units.r{round(r * 100):03d}"
        final.setdefault(feature + ".rich.first", "0.01")
        final.setdefault(feature + ".x7.first", "0.30" if r == 0.5 else "0.10")
        final.setdefault(feature + ".delta_auc.i004.delta", "0.3")
        final[feature + ".delta_auc.i004.a"] = "0.03"
    return final


def exploratory_catalog(public: dict[str, Any]) -> dict[str, Any]:
    catalog = secondary_catalog(public)
    for r in SHARES:
        share = f"{r:g}".replace(".", "-")
        prefix = f"v4x.comparisons.by_r.{share}"
        catalog["values"][prefix + ".main_curve.first.point"] = "0.1"
        catalog["values"][prefix + ".x3.cell.a"] = "0.1"
        catalog["values"][prefix + ".x4.P_or.a"] = "0.1"
    return catalog


def x3_catalog(public: dict[str, Any]) -> dict[str, Any]:
    catalog = secondary_catalog(public)
    levels = [0.584793, 0.541967, 0.543213, 0.534303, 0.546, 0.554, 0.563, 0.568, 0.582]
    for r, free in zip(SHARES, levels, strict=True):
        a = 0.3 if r == 0.5 else 0.1
        stem = f"v4x.x3.cells.r{round(r * 100):03d}.a{round(a * 10000):04d}."
        known = free + (0.27282 if r == 0.5 else 0.12614 if r == 0.55 else 0.2)
        delta = free - known
        catalog["values"].update(
            {
                stem + "cell.a": str(a),
                stem + "cell.r": str(r),
                stem + "cell.family": "B",
                stem + "cell.channel": "observed",
                stem + "known.success": "true",
                stem + "known.auc": str(known),
                stem + "free.success": "true",
                stem + "free.auc": str(free),
                stem + "free.parameters.signal": str(r - 0.002),
                stem + "delta.point": str(delta),
                stem + "delta.interval_95.i000": str(delta - 0.01),
                stem + "delta.interval_95.i001": str(delta + 0.01),
                stem + "lost_crossing": "false" if r == 0.55 else "true",
            }
        )
        share = f"{r:g}".replace(".", "-")
        catalog["values"][f"v4x.comparisons.by_r.{share}.main_curve.first.point"] = str(
            a
        )
    catalog["values"]["v4x.x3.count.lost_crossing"] = "8"
    return catalog


def test_round4_levels_use_the_boundary_cell_and_the_exploratory_classifier() -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_catalog(public)
    result = build_journal(public, {}, catalog, rows)
    assert result.values["j.x3.r050.known.auc"] == "0.858"
    assert result.values["j.x3.r050.free.auc"] == "0.585"
    assert result.values["j.x3.r050.free.r_b"] == "0.50"
    assert result.values["j.x3.r050.delta.point"] == "-0.273"
    assert result.values["j.x3.r050.delta.lower"] == "-0.283"
    assert result.values["j.x3.r050.delta.upper"] == "-0.263"
    assert result.values["j.x3.free.auc.min"] == "0.534"
    assert result.values["j.x3.free.auc.min.r"] == "0.65"
    assert result.values["j.x3.free.auc.max"] == "0.585"
    assert result.values["j.x3.free.auc.max.r"] == "0.50"
    assert result.values["j.x3.known.auc.min"] == "0.668"
    assert result.values["j.x3.known.auc.min.r"] == "0.55"
    assert result.values["j.x3.known.auc.max"] == "0.858"
    assert result.values["j.x3.known.auc.max.r"] == "0.50"
    assert result.values["j.x3.free.r_b.min"] == "0.50"
    assert result.values["j.x3.free.r_b.min.r"] == "0.50"
    assert result.values["j.x3.free.r_b.max"] == "0.90"
    assert result.values["j.x3.free.r_b.max.r"] == "0.90"
    assert result.values["j.x3.r055.lost_crossing"] == "no"
    table = result.tables["journal-esm-x3-levels.tex"]
    assert r"\label{tab:x3-levels}" in table
    assert r"\resultnum{j.b.r050.first.point}{0.30}" in table
    assert r"\resultnum{j.x3.r055.known.auc}{0.668}" in table
    assert "lag four and lag five" in table
    assert r"$\resultnum{j.x3.r050.delta.point}{" in table
    assert r"[$\resultnum{j.x3.r050.delta.lower}{" in table
    assert result.values["j.b.r050.a3000.auc"] == "0.910"
    assert (
        r"\setlength{\tabcolsep}{5pt}"
        in result.tables["journal-table-boundaries-B.tex"]
    )
    assert (
        r"\setlength{\tabcolsep}{4pt}"
        in result.tables["journal-table-other-models.tex"]
    )


@pytest.mark.parametrize("field", ("cell.a", "cell.r", "cell.family", "cell.channel"))
def test_round4_levels_reject_a_misidentified_boundary_cell(field: str) -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_catalog(public)
    catalog["values"]["v4x.x3.cells.r050.a3000." + field] = "0.9"
    with pytest.raises(ValueError, match="Free-share boundary cell"):
        build_journal(public, {}, catalog, rows)


def test_round4_missing_fitted_share_is_reported_without_reconstruction() -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_catalog(public)
    source = "v4x.x3.cells.r050.a3000.free.parameters.signal"
    del catalog["values"][source]
    result = build_journal(public, {}, catalog, rows)
    assert "j.x3.r050.free.r_b" not in result.values
    assert "j.x3.free.r_b.min" not in result.values
    assert any(source in note for note in result.notes)
    assert "not available" in result.tables["journal-esm-x3-levels.tex"]
    assert result.values["j.x3.r050.free.auc"] == "0.585"


def x3_lag_catalog(public: dict[str, Any]) -> dict[str, Any]:
    catalog = x3_catalog(public)
    means = {
        "social": (0.9, 0.8, 0.447986, 0.392996, 0.345054),
        "known": (0.9, 0.8, 0.449082, 0.396470, 0.352080),
        "free": (0.9, 0.8, 0.447902, 0.393295, 0.346310),
    }
    for r in SHARES:
        a = 0.3 if r == 0.5 else 0.1
        stem = f"v4x.x3.cells.r{round(r * 100):03d}.a{round(a * 10000):04d}."
        for group, values in means.items():
            for i, value in enumerate(values):
                catalog["values"][stem + f"means.{group}.i{i:03d}"] = str(value)
    return catalog


def x3_fit_catalog(public: dict[str, Any]) -> dict[str, Any]:
    from decimal import Decimal

    catalog = x3_lag_catalog(public)
    for r in SHARES:
        a = 0.3 if r == 0.5 else 0.1
        stem = f"v4x.x3.cells.r{round(r * 100):03d}.a{round(a * 10000):04d}."
        miss = 13.4 if r == 0.5 else 7.1 if r == 0.55 else 12.0
        catalog["values"].update(
            {
                stem + "known.parameters.i000": "0.850583",
                stem + "known.parameters.i001": "0.156787",
                stem + "free.parameters.phi": "0.866996",
                stem + "free.parameters.eta": "0.0685658",
                stem + "free.parameters.signal": str(
                    Decimal(str(r)) - Decimal("0.00115")
                ),
                stem + "free.attempts.i000.points.i000.signal": str(r),
                stem + "free.attempts.i000.points.i000.inner_status": "interior",
                stem + "free.attempts.i000.points.i000.parameters.i000": "0.850583",
                stem + "free.attempts.i000.points.i000.parameters.i001": "0.156787",
                stem + "free.attempts.i000.points.i000.residual.i002": str(
                    miss * 0.0001
                ),
                stem + "free.attempts.i000.points.i000.se.i002": "0.0001",
                stem + "free.attempts.i000.points.i000.residual_se_units.i002": str(
                    miss
                ),
            }
        )
    return catalog


def test_fit_table_keeps_share_precision_and_uses_the_matching_attempt() -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_fit_catalog(public)
    catalog["values"]["v4x.x3.cells.r050.a1000.known.parameters.i001"] = "0.99"
    catalog["values"]["v4x.x3.cells.r050.a3000.free.parameters.signal"] = "0.497164"
    result = build_journal(public, {}, catalog, rows)
    assert result.values["j.x3.r050.free.r"] == "0.4972"
    assert result.values["j.x3.r050.free.r_shift"] == "-0.0028"
    assert result.values["j.x3.r070.free.r_shift"] == "-0.0012"
    assert result.values["j.x3.free.r_shift.min"] == "0.0012"
    assert result.values["j.x3.free.r_shift.max"] == "0.0028"
    assert result.values["j.x3.free.r_shift.max.r"] == "0.50"
    assert result.values["j.x3.r050.known.phi"] == "0.851"
    assert result.values["j.x3.r050.known.lambda"] == "0.157"
    assert result.values["j.x3.r050.free.phi"] == "0.867"
    assert result.values["j.x3.r050.free.lambda"] == "0.069"
    assert result.values["j.x3.known.lambda.min"] == "0.157"
    assert result.values["j.x3.free.lambda.max"] == "0.069"
    assert result.values["j.x3.r050.l3_miss_se"] == "-13.4"
    assert result.values["j.x3.r055.l3_miss_se"] == "-7.1"
    assert result.values["j.x3.l3_miss_se.min"] == "-13.4"
    assert result.values["j.x3.l3_miss_se.max"] == "-7.1"
    levels = result.tables["journal-esm-x3-levels.tex"]
    assert "$r_B-r$" in levels
    assert "Fitted $r_B$" not in levels
    assert r"$\resultnum{j.x3.r050.free.r_shift}{-0.0028}$" in levels
    assert r"$\resultnum{j.x3.r070.free.r_shift}{-0.0012}$" in levels
    assert r"\resultnum{j.x3.r050.free.r_b}" not in levels
    assert r"Table~\ref{tab:x3-fit} gives B's fitted parameters" in levels
    table = result.tables["journal-esm-x3-fit.tex"]
    assert r"\label{tab:x3-fit}" in table
    assert r"\resultnum{j.b.r050.first.point}{0.30}" in table
    assert r"$\resultnum{j.x3.r050.free.r_shift}{-0.0028}$" in table
    assert r"$\resultnum{j.x3.r050.l3_miss_se}{-13.4}$" in table


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("known.parameters.i001", "1.1"),
        ("free.parameters.phi", "nan"),
        ("free.parameters.signal", "-0.1"),
        ("free.attempts.i000.points.i000.signal", "0.71"),
        ("free.attempts.i000.points.i000.parameters.i001", "0.2"),
        ("free.attempts.i000.points.i000.inner_status", "solver-failure"),
        ("free.attempts.i000.points.i000.se.i002", "0"),
        ("free.attempts.i000.points.i000.residual_se_units.i002", "120"),
    ),
)
def test_fit_table_rejects_invalid_parameters_and_true_share_attempt(
    field: str, value: str
) -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_fit_catalog(public)
    catalog["values"]["v4x.x3.cells.r070.a1000." + field] = value
    with pytest.raises(ValueError, match="Free-share"):
        build_journal(public, {}, catalog, rows)


@pytest.mark.parametrize(
    ("field", "target", "summary"),
    (
        ("free.parameters.signal", "free.r_shift", "free.r_shift"),
        ("known.parameters.i001", "known.lambda", "known.lambda"),
        ("free.attempts.i000.points.i000.se.i002", "l3_miss_se", "l3_miss_se"),
    ),
)
def test_fit_table_does_not_reconstruct_missing_quantities(
    field: str, target: str, summary: str
) -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_fit_catalog(public)
    source = "v4x.x3.cells.r070.a1000." + field
    del catalog["values"][source]
    result = build_journal(public, {}, catalog, rows)
    assert "j.x3.r070." + target not in result.values
    assert "j.x3." + summary + ".min" not in result.values
    assert "not available" in result.tables["journal-esm-x3-fit.tex"]
    assert any(source in note for note in result.notes)


def test_influence_ratio_uses_unrounded_means_and_skips_a_zero_denominator() -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_lag_catalog(public)
    stem = "v4x.x3.cells.r070.a1000.means."
    catalog["values"][stem + "social.i002"] = "0.5"
    catalog["values"][stem + "known.i002"] = "0.50001"
    catalog["values"][stem + "social.i004"] = "0.4"
    catalog["values"][stem + "known.i004"] = "0.4000685"
    result = build_journal(public, {}, catalog, rows)
    assert result.values["j.x3.lag_shortfall.r070.l3"] == "0.0000"
    assert result.values["j.x3.lag_shortfall.ratio_l5_l3.min"] == "6.4"
    assert result.values["j.x3.lag_shortfall.ratio_l5_l3.max"] == "6.8"
    catalog["values"][stem + "known.i002"] = "0.5"
    result = build_journal(public, {}, catalog, rows)
    assert "j.x3.lag_shortfall.ratio_l5_l3.max" not in result.values
    assert any("zero lag-three" in note for note in result.notes)


def x5_aggregate() -> dict[str, Any]:
    return {
        "schema": "ic-study.v4-exploratory-x5.v1",
        "conditions": [{"name": "trend-003"}, {"name": "step-003"}],
        "cells": [
            {
                "a": 0.0,
                "r": r,
                "family": "B",
                "channel": {"name": "trend-003"},
                "success": True,
                "parameters": [0.8355, 0.0785],
                "estimate": {
                    "auc": 0.6843290625,
                    "lags": {
                        "data_mean": [0.8, 0.7, 0.5, 0.4, 0.3],
                        "null_mean": [0.8, 0.7, 0.501, 0.402, 0.3 + ratio * 0.001],
                        "data_minus_null": [0, 0, -0.001, -0.002, -ratio * 0.001],
                    },
                },
            }
            for r, ratio in zip((0.5, 0.55, 0.6), (4.0, 5.0, 9.0), strict=True)
        ]
        + [
            {
                "a": 0.0,
                "r": 0.5,
                "family": "B",
                "channel": {"name": "step-003"},
                "success": False,
                "estimate": None,
            }
        ],
    }


def test_stress_signature_selects_estimated_cells_and_uses_the_condition_median() -> (
    None
):
    public, rows = inputs(curve())
    stress = x5_aggregate()
    result = build_journal(
        public, {}, secondary_catalog(public), rows, x5_aggregate=stress
    )
    assert result.values["j.x5.signature.cells"] == "3"
    assert result.values["j.x5.signature.negative.n"] == "3"
    assert result.values["j.x5.signature.increasing.n"] == "3"
    assert result.values["j.x5.signature.ratio_l5_l3.median.trend-003"] == "5.0"
    assert "j.x5.signature.ratio_l5_l3.median.step-003" not in result.values
    stress["cells"][0]["estimate"]["lags"].update(
        data_mean=[0.8, 0.7, 0.501, 0.502, 0.503],
        null_mean=[0.8, 0.7, 0.5, 0.5, 0.5],
        data_minus_null=[0, 0, 0.001, 0.002, 0.003],
    )
    result = build_journal(
        public, {}, secondary_catalog(public), rows, x5_aggregate=stress
    )
    assert result.values["j.x5.signature.negative.n"] == "2"
    assert result.values["j.x5.signature.increasing.n"] == "3"


@pytest.mark.parametrize(
    "change", ("duplicate", "condition", "influence", "lags", "delta")
)
def test_stress_signature_rejects_misidentified_or_inconsistent_cells(
    change: str,
) -> None:
    public, rows = inputs(curve())
    stress = x5_aggregate()
    cell = stress["cells"][0]
    if change == "duplicate":
        stress["cells"].append(cell)
    elif change == "condition":
        cell["channel"]["name"] = "undeclared"
    elif change == "influence":
        cell["a"] = 0.1
    elif change == "lags":
        cell["estimate"]["lags"]["data_mean"][2] = float("nan")
    else:
        cell["estimate"]["lags"]["data_minus_null"][2] = 0.001
    with pytest.raises(ValueError, match="Stress signature"):
        build_journal(public, {}, secondary_catalog(public), rows, x5_aggregate=stress)


def test_stress_signature_counts_strictly_before_rounding_and_rejects_zero_l3() -> None:
    public, rows = inputs(curve())
    stress = x5_aggregate()
    stress["cells"][0]["estimate"]["lags"].update(
        data_mean=[0.8, 0.7, 0.5, 0.5, 0.5],
        null_mean=[0.8, 0.7, 0.50001, 0.50001, 0.50002],
        data_minus_null=[0, 0, -0.00001, -0.00001, -0.00002],
    )
    result = build_journal(
        public, {}, secondary_catalog(public), rows, x5_aggregate=stress
    )
    assert result.values["j.x5.signature.negative.n"] == "3"
    assert result.values["j.x5.signature.increasing.n"] == "2"
    stress["cells"][0]["estimate"]["lags"]["null_mean"][2] = 0.5
    stress["cells"][0]["estimate"]["lags"]["data_minus_null"][2] = 0
    with pytest.raises(ValueError, match="zero lag-three"):
        build_journal(public, {}, secondary_catalog(public), rows, x5_aggregate=stress)


def x3_grid_catalog(public: dict[str, Any]) -> dict[str, Any]:
    from decimal import Decimal

    catalog = secondary_catalog(public)
    for r, a, shift, success, status, reading in (
        (0.5, 0.01, "-0.00015", True, "interior", "inconclusive"),
        (0.55, 0.01, "-0.00035", True, "interior", "inconclusive"),
        (0.6, 0.03, "0.00025", True, "interior", "inconclusive"),
        (0.65, 0.03, "-0.00004", True, "interior", "inconclusive"),
        (0.5, 0.003, "-0.00024", True, "interior", "inconclusive"),
        (0.55, 0.6, "-0.005", True, "interior", "inconclusive"),
        (0.6, 0.6, "-0.006", True, "interior", "inconclusive"),
        (0.65, 0.01, "-0.03", True, "budget", "inconclusive"),
        (0.7, 0.03, "-0.02", False, "interior", "inconclusive"),
        (0.5, 0.001, "0", False, "budget", "free-gap"),
        (0.65, 0.6, "0", False, "inner-failure", "free-gap"),
        (0.7, 0.9, "0", False, "budget", "free-gap"),
        (0.75, 0.9, "0", False, "inner-failure", "gap"),
    ):
        stem = f"v4x.x3.cells.r{round(r * 100):03d}.a{round(a * 10000):04d}."
        catalog["values"].update(
            {
                stem + "cell.a": str(a),
                stem + "cell.r": str(r),
                stem + "cell.family": "B",
                stem + "cell.channel": "observed",
                stem + "free.success": str(success).lower(),
                stem + "free.attempts.i000.status": status,
                stem + "free.parameters.signal": str(Decimal(str(r)) + Decimal(shift)),
                stem + "reading": reading,
                stem + "lost_crossing": "false",
            }
        )
        if a == 0.6 and success:
            catalog["values"].update(
                {
                    stem + "free.parameters.eta": "0" if r == 0.55 else "0.0000001",
                    stem + "free.parameters.phi": "0.9304" if r == 0.55 else "0.9336",
                    stem + "free.auc": "0.6004" if r == 0.55 else "0.6556",
                }
            )
    catalog["values"]["v4x.x3.count.free-gap"] = "3"
    catalog["values"]["v4x.x3.count.lost_crossing"] = "0"
    return catalog


def test_grid_shift_counts_accepted_interior_fits_before_rounding() -> None:
    public, rows = inputs(curve())
    catalog = x3_grid_catalog(public)
    result = build_journal(public, {}, catalog, rows)
    assert result.values["j.x3.free.fits.n"] == "6"
    assert result.values["j.x3.free.r_shift.negative.n"] == "5"
    assert result.values["j.x3.free.r_shift.a0100.n"] == "2"
    assert result.values["j.x3.free.r_shift.a0100.min"] == "0.0002"
    assert result.values["j.x3.free.r_shift.a0100.max"] == "0.0004"
    assert result.values["j.x3.free.r_shift.a0300.min"] == "0.0000"
    assert result.values["j.x3.free.r_shift.a0300.max"] == "0.0002"
    assert result.values["j.x3.free.r_shift.a1000.n"] == "0"
    assert "j.x3.free.r_shift.a1000.min" not in result.values
    assert result.values["j.x3.free.r_shift.low.n"] == "1"
    assert result.values["j.x3.free.r_shift.low.max"] == "0.0002"
    catalog["values"]["v4x.x3.cells.r055.a0100.free.attempts.i001.status"] = "budget"
    result = build_journal(public, {}, catalog, rows)
    assert result.values["j.x3.free.fits.n"] == "5"
    assert result.values["j.x3.free.r_shift.a0100.n"] == "1"
    assert result.values["j.x3.free.r_shift.a0100.max"] == "0.0002"


def test_strongest_fit_box_edge_is_exact_zero_and_keeps_auc_extrema() -> None:
    public, rows = inputs(curve())
    result = build_journal(public, {}, x3_grid_catalog(public), rows)
    assert result.values["j.x3.free.a6000.fits.n"] == "2"
    assert result.values["j.x3.free.a6000.lambda_zero.n"] == "1"
    assert result.values["j.x3.free.a6000.phi.min"] == "0.930"
    assert result.values["j.x3.free.a6000.phi.max"] == "0.934"
    assert result.values["j.x3.free.a6000.auc.min"] == "0.600"
    assert result.values["j.x3.free.a6000.auc.max"] == "0.656"


def test_free_gaps_preserve_archived_reading_and_reconcile_with_released_total() -> (
    None
):
    public, rows = inputs(curve())
    catalog = x3_grid_catalog(public)
    result = build_journal(public, {}, catalog, rows)
    counts = {
        key: value
        for key, value in result.values.items()
        if key.startswith("j.x3.free_gap.")
    }
    assert counts == {
        "j.x3.free_gap.a0010.n": "1",
        "j.x3.free_gap.a6000.n": "1",
        "j.x3.free_gap.a9000.n": "1",
    }
    assert sum(map(int, counts.values())) == 3
    catalog["values"]["v4x.x3.count.free-gap"] = "4"
    with pytest.raises(ValueError, match="Free-share gap sum"):
        build_journal(public, {}, catalog, rows)


def x3_plus_catalog(public: dict[str, Any]) -> dict[str, Any]:
    from decimal import Decimal

    catalog = x3_fit_catalog(public)
    for r in SHARES:
        a = 0.3 if r == 0.5 else 0.1
        stem = f"v4x.x3.cells.r{round(r * 100):03d}.a{round(a * 10000):04d}."
        point = stem + "free.attempts.i002.points.i004."
        catalog["values"].update(
            {
                point + "signal": str(Decimal(str(r)) + Decimal("0.01")),
                point + "inner_status": "interior",
                point + "parameters.i000": "0.764092",
                point + "parameters.i001": "0.413929",
                point + "residual.i002": "-0.00741618" if r == 0.5 else "0.00741618",
                stem + "free.attempts.i000.points.i001.signal": str(
                    Decimal(str(r)) - Decimal("0.01")
                ),
                stem + "free.attempts.i000.points.i001.parameters.i001": "0.99",
            }
        )
    return catalog


def test_plus_trial_finds_signal_across_attempts_and_preserves_matching_sign() -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_plus_catalog(public)
    catalog["values"]["v4x.x3.cells.r070.a1000.means.known.i002"] = "0.9"
    result = build_journal(public, {}, catalog, rows)
    assert result.values["j.x3.plus.offset"] == "0.01"
    assert result.values["j.x3.r070.plus.lambda"] == "0.414"
    assert result.values["j.x3.r070.plus.phi"] == "0.764"
    assert result.values["j.x3.r070.plus.l3_miss"] == "0.0074"
    assert result.values["j.x3.r050.plus.l3_miss"] == "-0.0074"
    assert result.values["j.x3.plus.l3_miss.min.r"] == "0.50"
    assert (
        result.values["j.x3.plus.l3_miss.max.r"]
        == "0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90"
    )
    assert result.values["j.x3.plus.lambda.max"] == "0.414"


@pytest.mark.parametrize(
    "change", ("offset", "missing", "duplicate", "status", "parameter")
)
def test_plus_trial_refuses_wrong_offset_missing_or_ambiguous_point(
    change: str,
) -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_plus_catalog(public)
    point = "v4x.x3.cells.r070.a1000.free.attempts.i002.points.i004."
    if change == "offset":
        catalog["values"][point + "signal"] = "0.71000001"
    elif change == "missing":
        del catalog["values"][point + "signal"]
    elif change == "duplicate":
        catalog["values"][point.replace("i004", "i005") + "signal"] = "0.71"
    elif change == "status":
        catalog["values"][point + "inner_status"] = "budget"
    else:
        catalog["values"][point + "parameters.i001"] = "0.9"
    with pytest.raises(ValueError, match="Free-share plus trial"):
        build_journal(public, {}, catalog, rows)


def test_stress_lag_table_binds_parameters_means_and_released_auc() -> None:
    import re

    public, rows = inputs(curve())
    catalog = secondary_catalog(public)
    stress = x5_aggregate()
    source = "v4x.comparisons.by_r.0-5.x5.r050.a0000.trend-003.estimate.auc"
    catalog["values"][source] = "0.684329"
    result = build_journal(
        public, {source: "0.684329"}, catalog, rows, x5_aggregate=stress
    )
    prefix = "j.x5.trend-003.r050."
    assert result.values[prefix + "phi"] == "0.836"
    assert result.values[prefix + "lambda"] == "0.078"
    assert result.values[prefix + "l3"] == "-0.0010"
    assert result.values[prefix + "l4"] == "-0.0020"
    assert result.values[prefix + "l5"] == "-0.0040"
    assert result.values[prefix + "auc"] == "0.684"
    assert not any(key.startswith("j.x5.step-003.r") for key in result.values)
    table = result.tables["journal-esm-x5-lags.tex"]
    assert r"\label{tab:x5-lags}" in table
    assert r"$\resultnum{j.x5.trend-003.r050.l3}{-0.0010}$" in table
    assert r"\begin{table}" in table
    bindings = re.findall(r"\\resultnum\{([^{}]+)\}\{([^{}]*)\}", table)
    assert len(bindings) == 25
    assert all(result.values[key] == value for key, value in bindings)
    shown = re.sub(r"\\resultnum\{[^{}]+\}\{[^{}]*\}", "", table)
    shown = re.sub(r"\\label\{[^{}]+\}|\d+(?:\.\d+)?(?:mm|pt)", "", shown)
    assert not re.search(r"\d", shown)
    assert not re.search(r"partner|\bG[012]\w*\b|\bX[1-7]\w*\b|\btier\b", shown)
    catalog["values"][source] = "0.685"
    with pytest.raises(ValueError, match="AUC differs from released"):
        build_journal(public, {}, catalog, rows, x5_aggregate=stress)


@pytest.mark.parametrize("change", ("parameters", "phi", "lambda", "auc"))
def test_stress_lag_table_refuses_unavailable_or_out_of_box_values(change: str) -> None:
    public, rows = inputs(curve())
    stress = x5_aggregate()
    cell = stress["cells"][0]
    if change == "parameters":
        del cell["parameters"]
    elif change == "phi":
        cell["parameters"][0] = 1
    elif change == "lambda":
        cell["parameters"][1] = -0.001
    else:
        cell["estimate"]["auc"] = float("nan")
    with pytest.raises(ValueError, match="Stress lag table"):
        build_journal(public, {}, secondary_catalog(public), rows, x5_aggregate=stress)


def test_cli_hashes_the_optional_stress_input_without_changing_it(
    tmp_path: Any,
) -> None:
    import hashlib
    import json

    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    source = tmp_path / "x5.json"
    source.write_text(json.dumps(x5_aggregate()))
    before = source.read_bytes()
    assert main([*args, "--x5-aggregate", str(source)]) == 0
    payload = json.loads((tmp_path / "journal.json").read_bytes())
    assert source.read_bytes() == before
    assert payload["sources"]["x5_aggregate"] == hashlib.sha256(before).hexdigest()
    assert payload["values"]["j.x5.signature.cells"] == "3"


def test_cli_refuses_a_forbidden_stress_path_before_reading_or_writing(
    tmp_path: Any,
) -> None:
    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main([*args, "--x5-aggregate", str(tmp_path / "restricted" / "x5.json")])
    assert exc.value.code == 2
    assert not (tmp_path / "generated").exists()
    assert not (tmp_path / "journal.json").exists()


def test_heise_details_exclude_the_break_window_and_use_its_adjacent_windows() -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    aggregate = heise_aggregate()
    aggregate["triplets"].reverse()
    result = build_journal(
        public, {}, secondary_catalog(public), rows, shp_aggregate=aggregate
    )
    assert result.values["j.shp.heise.others.spread"] == "0.029"
    assert result.values["j.shp.heise.dip2003"] == "0.065"


def test_lag_shortfalls_subtract_persistence_at_the_first_boundary() -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_lag_catalog(public)
    for group in ("social", "known", "free"):
        for i in range(5):
            catalog["values"][f"v4x.x3.cells.r050.a1000.means.{group}.i{i:03d}"] = "0"
    result = build_journal(public, {}, catalog, rows)
    for share in ("r050", "r070"):
        prefix = f"j.x3.lag_shortfall.{share}"
        assert [result.values[prefix + f".l{lag}"] for lag in (3, 4, 5)] == [
            "-0.0011",
            "-0.0035",
            "-0.0070",
        ]
        assert [result.values[prefix + f".free.l{lag}"] for lag in (3, 4, 5)] == [
            "0.0001",
            "-0.0003",
            "-0.0013",
        ]
    assert result.values["j.x3.lag_shortfall.negative.n"] == "9"
    assert result.values["j.x3.lag_shortfall.increasing.n"] == "9"
    table = result.tables["journal-esm-x3-lags.tex"]
    assert r"\label{tab:x3-lags}" in table
    assert r"\resultnum{j.b.r050.first.point}{0.30}" in table
    assert r"$\resultnum{j.x3.lag_shortfall.r070.l3}{-0.0011}$" in table


def test_lag_shortfall_counts_use_unrounded_strict_comparisons() -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_lag_catalog(public)
    for share, differences in (
        ("r050", (-0.001001, -0.001002, -0.001003)),
        ("r055", (0.001, -0.002, -0.003)),
        ("r060", (-0.001, -0.001, -0.003)),
        ("r065", (-0.000001, -0.002, -0.003)),
    ):
        a = "a3000" if share == "r050" else "a1000"
        stem = f"v4x.x3.cells.{share}.{a}.means."
        for i, difference in zip((2, 3, 4), differences, strict=True):
            catalog["values"][stem + f"social.i{i:03d}"] = "0.5"
            catalog["values"][stem + f"known.i{i:03d}"] = str(0.5 - difference)
    result = build_journal(public, {}, catalog, rows)
    assert result.values["j.x3.lag_shortfall.negative.n"] == "8"
    assert result.values["j.x3.lag_shortfall.increasing.n"] == "8"
    assert [result.values[f"j.x3.lag_shortfall.r050.l{lag}"] for lag in (3, 4, 5)] == [
        "-0.0010",
        "-0.0010",
        "-0.0010",
    ]
    assert result.values["j.x3.lag_shortfall.r065.l3"] == "0.0000"


def test_lag_shortfalls_round_decimal_ties_without_binary_float_error() -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_lag_catalog(public)
    stem = "v4x.x3.cells.r085.a1000.means."
    catalog["values"][stem + "social.i003"] = "0.4"
    catalog["values"][stem + "known.i003"] = "0.404350"
    catalog["values"][stem + "free.i003"] = "0.400250"
    result = build_journal(public, {}, catalog, rows)
    assert result.values["j.x3.lag_shortfall.r085.l4"] == "-0.0044"
    assert result.values["j.x3.lag_shortfall.r085.free.l4"] == "-0.0002"


@pytest.mark.parametrize("group", ("social", "known", "free"))
@pytest.mark.parametrize("value", ("nan", "inf", "1.01", "-1.01"))
def test_lag_shortfalls_reject_invalid_released_correlations(
    group: str, value: str
) -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_lag_catalog(public)
    catalog["values"][f"v4x.x3.cells.r070.a1000.means.{group}.i002"] = value
    with pytest.raises(ValueError, match=r"v4x\.x3\.cells\.r070\.a1000\.means\."):
        build_journal(public, {}, catalog, rows)


@pytest.mark.parametrize("group", ("social", "known", "free"))
def test_missing_lag_means_remain_unavailable_without_reconstruction(
    group: str,
) -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_lag_catalog(public)
    source = f"v4x.x3.cells.r070.a1000.means.{group}.i002"
    del catalog["values"][source]
    result = build_journal(public, {}, catalog, rows)
    assert "not available" in result.tables["journal-esm-x3-lags.tex"]
    assert any(source in note for note in result.notes)
    prefix = "j.x3.lag_shortfall.r070"
    if group in ("social", "known"):
        assert prefix + ".l3" not in result.values
        assert "j.x3.lag_shortfall.negative.n" not in result.values
        assert "j.x3.lag_shortfall.increasing.n" not in result.values
    else:
        assert prefix + ".free.l3" not in result.values
        assert result.values["j.x3.lag_shortfall.negative.n"] == "9"
    assert result.values[prefix + ".l4"] == "-0.0035"


@pytest.mark.parametrize("group", ("known", "free"))
def test_lag_shortfalls_require_successful_persistence_fits(group: str) -> None:
    public, rows = inputs(curve(first=0.3))
    catalog = x3_lag_catalog(public)
    catalog["values"][f"v4x.x3.cells.r070.a1000.{group}.success"] = "false"
    if group == "free":
        catalog["values"]["v4x.x3.count.lost_crossing"] = "7"
    result = build_journal(public, {}, catalog, rows)
    prefix = "j.x3.lag_shortfall.r070" + (".free" if group == "free" else "")
    assert all(prefix + f".l{lag}" not in result.values for lag in (3, 4, 5))
    assert "not available" in result.tables["journal-esm-x3-lags.tex"]


def test_lag_shortfall_table_is_omitted_when_no_means_are_released() -> None:
    public, rows = inputs(curve(first=0.3))
    result = build_journal(public, {}, x3_catalog(public), rows)
    assert "journal-esm-x3-lags.tex" not in result.tables
    assert not any(key.startswith("j.x3.lag_shortfall.") for key in result.values)
    assert any("lag means" in note for note in result.notes)


def test_exploratory_summaries_use_released_comparisons_and_rich_boundaries() -> None:
    public, rows = inputs(curve())
    result = build_journal(
        public, exploratory_values(), exploratory_catalog(public), rows
    )
    assert result.values["j.x3.auc_reduction.min"] == "0.126"
    assert result.values["j.x3.auc_reduction.max"] == "0.273"
    assert result.values["j.x7.first.min"] == "0.003"
    assert result.values["j.x7.first.max"] == "0.03"
    assert result.values["j.x7.auc_gain.a0300.max"] == "0.339"
    assert result.values["j.x4a.boundary_rejection.r050"] == "0.447"
    assert result.values["j.x4a.boundary_rejection.min"] == "0.171"
    assert result.values["j.x4b.zero_rejection.r050"] == "0.300"
    assert result.values["j.x4b.zero_rejection.r050.lower"] == "0.235"
    assert result.values["j.x4b.zero_rejection.r050.upper"] == "0.365"
    assert result.values["j.x1a.available"] == "no"
    assert result.values["j.x2.available"] == "no"


@pytest.mark.parametrize(
    "change", ("missing_share", "unavailable", "wrong_grid", "wrong_x3", "wrong_x4")
)
def test_exploratory_summaries_refuse_incomplete_or_misidentified_cells(
    change: str,
) -> None:
    public, rows = inputs(curve())
    final = exploratory_values()
    catalog = exploratory_catalog(public)
    if change == "missing_share":
        del final["v4x.x7.units.r090.rich.first"]
    elif change == "unavailable":
        final["v4x.x7.units.r090.rich.first"] = "unavailable"
    elif change == "wrong_grid":
        final["v4x.x7.units.r050.delta_auc.i004.a"] = "0.01"
    else:
        source = "x3.cell.a" if change == "wrong_x3" else "x4.P_or.a"
        catalog["values"]["v4x.comparisons.by_r.0-5." + source] = "0.3"
    with pytest.raises(ValueError, match=r"summary|strength|unavailable"):
        build_journal(public, final, catalog, rows)


def test_every_table_number_is_bound_and_visible_terms_follow_journal_vocabulary() -> (
    None
):
    import re

    public, rows = inputs(
        curve(first=0.3),
        curve("control", tier=3, channel="latent"),
        curve("ordinal", tier=3, channel="ordinal_one"),
        curve("rank", tier=3, channel="latent_rank"),
    )
    public["objects"]["shp"] = shp_public()
    result = build_journal(
        public, {}, x3_fit_catalog(public), rows, shp_aggregate=heise_aggregate()
    )
    assert len(result.tables) == 10
    for text in result.tables.values():
        for key, value in re.findall(r"\\resultnum\{([^{}]+)\}\{([^{}]+)\}", text):
            assert result.values.get(key) == value
        visible = re.sub(r"\\resultnum\{[^{}]+\}\{([^{}]+)\}", r"\1", text)
        visible = re.sub(r"\\(?:label|ref)\{[^{}]+\}", "", visible)
        assert not re.search(
            r"\b(?:partners?|G[0-2][abc]?|X[1-7][ab]?|tiers?)\b", visible, re.I
        )
        stripped = re.sub(r"\\resultnum\{[^{}]+\}\{[^{}]+\}", "", text)
        stripped = re.sub(r"\d+(?:\.\d+)?(?:pt|mm|cm|em)", "", stripped)
        stripped = re.sub(r"\\(?:label|ref|begin|end)\{[^{}]+\}", "", stripped)
        stripped = re.sub(r"\\includegraphics(?:\[[^]]*\])?\{[^{}]+\}", "", stripped)
        assert not re.search(r"\d", stripped), stripped


def cli_inputs(tmp_path: Any, final: dict[str, str] | None = None) -> list[str]:
    import csv
    import json

    public, rows = inputs(curve())
    paths = {
        "public-aggregates": tmp_path / "public.json",
        "values": tmp_path / "final.json",
        "catalog": tmp_path / "catalog.json",
        "all-units": tmp_path / "inventory.csv",
    }
    paths["public-aggregates"].write_text(json.dumps(public))
    paths["values"].write_text(json.dumps({"values": final or {}}))
    catalog = secondary_catalog(public)
    catalog["values"].update(final or {})
    paths["catalog"].write_text(json.dumps(catalog))
    with paths["all-units"].open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return [arg for name, path in paths.items() for arg in ("--" + name, str(path))] + [
        "--generated",
        str(tmp_path / "generated"),
        "--journal-values",
        str(tmp_path / "journal.json"),
    ]


def test_cli_refuses_overlapping_final_key_before_writing_outputs(
    tmp_path: Any, capsys: Any
) -> None:
    import pytest

    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path, {"j.b.r050.a0300.auc": "0.612"})
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2
    assert "Refusing to overwrite final value key" in capsys.readouterr().err
    assert not (tmp_path / "generated").exists()
    assert not (tmp_path / "journal.json").exists()


def test_cli_binds_sources_preserves_inputs_and_produces_deterministic_displays(
    tmp_path: Any,
) -> None:
    import hashlib
    import json
    import re

    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    sources = [
        tmp_path / name
        for name in ("public.json", "final.json", "catalog.json", "inventory.csv")
    ]
    before = [path.read_bytes() for path in sources]
    assert main(args) == 0
    payload = json.loads((tmp_path / "journal.json").read_text())
    assert payload["schema"] == "ic-study.v4-journal-values.v1"
    assert payload["sources"]["all_units"] == hashlib.sha256(before[3]).hexdigest()
    assert payload["code"]["module"] == "ic_study.analysis.v4_journal_export"
    assert len(payload["code"]["sha256"]) == 64
    assert [path.read_bytes() for path in sources] == before
    output = {
        path.name: path.read_bytes() for path in (tmp_path / "generated").iterdir()
    }
    assert {name for name in output if name.endswith(".pdf")} == {
        "J1_boundaries_by_model.pdf",
        "J2_auc_profiles_B.pdf",
        "J5_inventory_status.pdf",
    }
    for name, data in output.items():
        if name.endswith(".tex"):
            visible = re.sub(r"\\resultnum\{[^{}]+\}\{([^{}]+)\}", r"\1", data.decode())
            visible = re.sub(r"\\includegraphics(?:\[[^]]*\])?\{[^{}]+\}", "", visible)
            assert not re.search(
                r"\b(?:partners?|G[0-2][abc]?|X[1-7][ab]?|tiers?)\b", visible, re.I
            )
    assert main(args) == 0
    assert {
        path.name: path.read_bytes() for path in (tmp_path / "generated").iterdir()
    } == output


def test_partial_boundary_interval_keeps_the_gap_strength_in_printed_text() -> None:
    c = curve(
        "steps24",
        tier=6,
        scenario="steps24",
        first=None,
        interval=[0.6, None],
        gaps={0.9: "solver"},
    )
    c["first"]["interval_censoring"] = "gap at a=0.9"
    public, rows = inputs(curve(), c)
    rows[1]["region"] = "indeterminate"
    result = build_journal(public, {}, secondary_catalog(public), rows)
    table = result.tables["journal-esm-sensitivity-differences.tex"]
    assert (
        r"censored at first gap (\resultnum{"
        "j.sensitivity.steps24.r050.sensitivity.censoring_gap.a}{0.90}); "
        r"interval from \resultnum{j.sensitivity.steps24.r050.sensitivity.lower}{0.60}"
        in table
    )


def test_d_summary_uses_first_gap_kind_and_preserves_sustained_gap_keys() -> None:
    d = curve(
        "state",
        tier=2,
        family="D",
        first=None,
        gaps={0.1: "family_limit", 0.9: "propagation"},
    )
    public, rows = inputs(curve(), d)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    table = result.tables["journal-table-other-models.tex"]
    assert r"\resultnum{j.models.D.r050.first.censoring_gap.a}{0.10}" in table
    assert "family limit on profile" in table
    assert "Censored (fit gaps)" in table
    assert result.values["j.models.D.r050.sustained.gap.0.a"] == "0.10"
    assert result.values["j.models.D.r050.sustained.gap.1.a"] == "0.90"


@pytest.mark.parametrize("name", ["first", "sustained"])
@pytest.mark.parametrize("field", ["censoring", "interval_censoring"])
def test_censoring_rejects_a_real_gap_at_the_wrong_end(name: str, field: str) -> None:
    d = curve(
        "state",
        tier=2,
        family="D",
        first=None,
        gaps={0.1: "family_limit", 0.9: "propagation"},
    )
    d[name][field] = "gap at a=0.9" if name == "first" else "gap at a=0.1"
    public, rows = inputs(curve(), d)
    with pytest.raises(ValueError, match=r"first gap|last gap"):
        build_journal(public, {}, secondary_catalog(public), rows)


def test_invalid_c_units_suppress_censoring_keys_but_keep_other_boundary_keys() -> None:
    models = [
        curve(
            f"c-{r}",
            r=r,
            family="C",
            tier=2,
            status="completo inválido",
            first=None,
            gaps={0.9: "solver"},
        )
        for r in SHARES
    ]
    for c in models:
        c["first"]["interval_censoring"] = "gap at a=0.9"
    public, rows = inputs(curve(), *models)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    assert not any(
        key.startswith("j.models.C.") and key.endswith(".censoring_gap.a")
        for key in result.values
    )
    assert result.values["j.models.C.r050.first.state"] == "invalid"
    assert result.values["j.models.C.r050.first.interval_gap.a"] == "0.90"
    assert result.values["j.models.C.r050.first.gap.0.a"] == "0.90"


def test_b_summaries_report_all_tied_shares_and_distance_from_target() -> None:
    curves = [
        curve(f"main-{r}", r=r)
        for r in (0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9)
    ]
    for c, value in zip(
        curves, (0.71, 0.71, 0.71, 0.75, 0.8, 0.9, 0.9, 0.9, 0.9), strict=True
    ):
        c["auc"][5] = value
    curves[3]["upper"][4] = 0.689
    public, rows = inputs(*curves)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    assert result.values["j.b.a1000.auc.min"] == "0.710"
    assert result.values["j.b.a1000.auc.min.r"] == "0.50, 0.55, 0.60"
    assert result.values["j.b.a1000.auc.max"] == "0.900"
    assert result.values["j.b.a1000.auc.max.r"] == "0.75, 0.80, 0.85, 0.90"
    assert result.values["j.b.a0300.upper.max"] == "0.689"
    assert result.values["j.b.a0300.upper.max.r"] == "0.65"
    assert result.values["j.b.a0300.upper.distance_to_target"] == "0.011"


def test_normal_theory_translation_is_printed_to_two_decimals() -> None:
    public, rows = inputs(curve())
    result = build_journal(public, {}, secondary_catalog(public), rows)
    for target, delta, power in (
        ("060", "0.36", "0.10"),
        ("070", "0.74", "0.18"),
        ("080", "1.19", "0.32"),
    ):
        assert result.values[f"j.auc_translation.target{target}.delta"] == delta
        assert result.values[f"j.auc_translation.target{target}.power"] == power


def test_sensitivity_summaries_use_valid_response_pairs_and_all_anchoring_aucs() -> (
    None
):
    sensitivities = []
    scenarios = ("c025", "c050", "d010", "d020", "c050-d020-exploratory")
    for scenario in scenarios:
        for r in SHARES:
            sensitivities.append(
                curve(
                    f"{scenario}-{r}",
                    r=r,
                    tier=4,
                    scenario=scenario,
                    status="completo inválido"
                    if scenario == "c025" and r == 0.5
                    else "completo válido",
                )
            )
    for r in SHARES:
        sensitivities.append(
            curve(
                f"b000-{r}",
                r=r,
                tier=5,
                scenario="b000",
                first=0.03 if r >= 0.7 else 0.1,
            )
        )
        omega = curve(
            f"omega025-{r}",
            r=r,
            tier=5,
            scenario="omega025",
            status="completo inválido",
        )
        omega["auc"][0] = 0.647 if r <= 0.55 else 0.892
        sensitivities.append(omega)
    public, rows = inputs(curve(), *sensitivities)
    for row in rows:
        if row["sensitivity"] == "c050-d020-exploratory" and row["r"] == "0.90":
            row["region"] = "indeterminate"
    result = build_journal(public, {}, secondary_catalog(public), rows)
    assert result.values["j.sensitivity.b000.first.min"] == "0.03"
    assert result.values["j.sensitivity.b000.first.max"] == "0.10"
    assert result.values["j.sensitivity.response_channel.n_pairs"] == "44"
    assert result.values["j.sensitivity.response_channel.n_same_region"] == "43"
    assert result.values["j.sensitivity.omega025.zero_auc.min"] == "0.647"
    assert result.values["j.sensitivity.omega025.zero_auc.min.r"] == "0.50, 0.55"
    assert result.values["j.sensitivity.omega025.zero_auc.max"] == "0.892"


def test_additional_exploratory_keys_preserve_the_released_reference_and_coverage() -> (
    None
):
    public, rows = inputs(curve())
    final = exploratory_values()
    final.update(
        {
            "v4x.comparisons.by_r.0-9.x1b.first.point": "0.3",
            "v4x.x4.x4a.r070.a0010.cell.a": "0.001",
            "v4x.x4.x4a.r070.a0010.x4a.auc_ref": "0.504257",
            "v4x.x6.x6a.band.vs_d1.gaps_as_misses.covered": "162",
            "v4x.x6.x6a.band.vs_d1.gaps_as_misses.total": "200",
            "v4x.x6.x6a.band.vs_d1.gaps_as_misses.wilson95.i000": "0.749988",
            "v4x.x6.x6a.band.vs_d1.gaps_as_misses.wilson95.i001": "0.858328",
        }
    )
    result = build_journal(public, final, exploratory_catalog(public), rows)
    assert result.values["j.x7.frozen_first.min"] == "0.10"
    assert result.values["j.x7.frozen_first.max"] == "0.30"
    assert result.values["j.x1b.r090.first.point"] == "0.30"
    assert result.values["j.x4a.r070.a0010.auc_ref"] == "0.504"
    assert result.values["j.x6.gaps_as_misses.percent"] == "81"
    assert result.values["j.x6.gaps_as_misses.wilson.lower"] == "0.750"
    assert result.values["j.x6.gaps_as_misses.wilson.upper"] == "0.858"


def test_cli_render_failure_preserves_all_previous_outputs(
    tmp_path: Any, capsys: Any
) -> None:
    import json

    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path, {"v4.protocol.shp.anchor_year": "2004"})
    public_path = tmp_path / "public.json"
    public = json.loads(public_path.read_text())
    public["objects"]["shp"] = {
        "sensitivity_envelope": [0.6, 0.7],
        "year": 2004,
        "estimate": 0.674,
    }
    public_path.write_text(json.dumps(public))
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "previous.tex").write_text("previous display")
    (tmp_path / "journal.json").write_text("previous values")
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert "wald_95_interval" in capsys.readouterr().err
    assert {p.name: p.read_bytes() for p in generated.iterdir()} == {
        "previous.tex": b"previous display"
    }
    assert (tmp_path / "journal.json").read_text() == "previous values"


def test_cli_reports_missing_input_through_argparse(tmp_path: Any, capsys: Any) -> None:
    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    (tmp_path / "inventory.csv").unlink()
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert "No such file" in capsys.readouterr().err
    assert not (tmp_path / "generated").exists()
    assert not (tmp_path / "journal.json").exists()


def test_invalid_inventory_split_excludes_valid_units_and_counts_each_cause_once() -> (
    None
):
    other = [
        curve(
            f"c-{r}",
            r=r,
            tier=2,
            family="C",
            status="completo inválido" if r <= 0.6 else "completo válido",
        )
        for r in SHARES
    ]
    other += [
        curve("weak", tier=5, scenario="omega025", status="completo inválido"),
        curve("medium", tier=5, scenario="omega050", status="completo inválido"),
        curve("other", tier=5, scenario="b000", status="completo inválido"),
        curve("valid", tier=5, scenario="omega075"),
    ]
    public, rows = inputs(curve(), *other)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    assert result.values["j.inventory.invalid.total"] == "6"
    assert result.values["j.inventory.invalid.c_related"] == "3"
    assert result.values["j.inventory.invalid.anchoring_sensitivities"] == "2"
    assert result.values["j.inventory.invalid.other"] == "1"


def test_d_gap_counts_include_each_released_gap_kind_across_cells() -> None:
    public, rows = inputs(
        curve(),
        curve(
            "d1",
            tier=2,
            family="D",
            first=None,
            gaps={0.1: "family_limit", 0.3: "solver", 0.6: "propagation"},
        ),
        curve(
            "d2",
            r=0.55,
            tier=2,
            family="D",
            first=None,
            gaps={0.03: "screened", 0.1: "validation", 0.9: "solver"},
        ),
    )
    result = build_journal(public, {}, secondary_catalog(public), rows)
    for kind, count in (
        ("family_limit", "1"),
        ("solver", "2"),
        ("propagation", "1"),
        ("screened", "1"),
        ("validation", "1"),
        ("dependency", "0"),
        ("total", "6"),
    ):
        assert result.values["j.models.D.gaps." + kind] == count


def test_control_counts_use_latent_boundaries_and_ignore_invalid_controls() -> None:
    controls = [
        curve(
            f"{channel}-{r}",
            r=r,
            tier=3,
            channel=channel,
            first=0.03 if r != 0.55 else 0.1,
            status="completo inválido" if r == 0.6 else "completo válido",
        )
        for r in (0.5, 0.55, 0.6)
        for channel in ("latent", "ordinal_one", "latent_rank")
    ]
    public, rows = inputs(curve(), *controls)
    for row in rows:
        if row["channel"] == "latent":
            row["region"] = "small"
    result = build_journal(public, {}, secondary_catalog(public), rows)
    assert result.values["j.controls.latent.n_boundary_a0300"] == "1"
    assert result.values["j.controls.latent.n_small"] == "2"
    assert "j.controls.ordinal_one.response_r" not in result.values
    table = result.tables["journal-esm-controls.tex"]
    assert "response signal share" not in table
    assert "Design shares identify" not in table


def test_b_summary_requires_all_nine_shares_with_available_estimates() -> None:
    public, rows = inputs(curve(gaps={0.1: "solver"}))
    with pytest.raises(ValueError, match="summary requires nine"):
        build_journal(public, {}, secondary_catalog(public), rows)


def test_c_zero_summary_rejects_a_missing_zero_strength_estimate() -> None:
    models = [
        curve(
            f"c-{r}", r=r, family="C", tier=2, gaps={0: "solver"} if r == 0.9 else None
        )
        for r in SHARES
    ]
    public, rows = inputs(curve(), *models)
    with pytest.raises(ValueError, match=r"unavailable|summary"):
        build_journal(public, {}, secondary_catalog(public), rows)


def test_cli_write_failure_preserves_previous_outputs(
    tmp_path: Any, capsys: Any
) -> None:
    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "previous.tex").write_text("previous display")
    (tmp_path / "journal.json").mkdir()
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert "error:" in capsys.readouterr().err
    assert {p.name: p.read_bytes() for p in generated.iterdir()} == {
        "previous.tex": b"previous display"
    }
    assert (tmp_path / "journal.json").is_dir()


def test_cli_late_write_error_rolls_back_tables_figures_and_values(
    tmp_path: Any, capsys: Any, monkeypatch: Any
) -> None:
    from pathlib import Path

    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "journal-table-boundaries-B.tex").write_bytes(b"previous table")
    (generated / "J2_auc_profiles_B.pdf").write_bytes(b"previous figure")
    (tmp_path / "journal.json").write_bytes(b"previous values")
    replace = Path.replace

    def write_error(path: Path, destination: Any) -> Path:
        if path.name.startswith("new-") and Path(destination).name == "journal.json":
            raise OSError("output write failed")
        return replace(path, destination)

    monkeypatch.setattr(Path, "replace", write_error)
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert "output write failed" in capsys.readouterr().err
    assert {p.name: p.read_bytes() for p in generated.iterdir()} == {
        "journal-table-boundaries-B.tex": b"previous table",
        "J2_auc_profiles_B.pdf": b"previous figure",
    }
    assert (tmp_path / "journal.json").read_bytes() == b"previous values"
    assert {p.name for p in tmp_path.iterdir()} == {
        "public.json",
        "final.json",
        "catalog.json",
        "inventory.csv",
        "generated",
        "journal.json",
    }


def shp_public() -> dict[str, Any]:
    return {
        "year": 2004,
        "estimate": 0.67443,
        "standard_error": 0.003833,
        "wald_95_interval": [0.666918, 0.681943],
        "sensitivity_envelope": [0.624968, 0.702060],
        "starts": {
            "year": 2004,
            "estimate": 0.69644,
            "standard_error": 0.005715,
            "wald_95_interval": [0.685238, 0.707642],
        },
    }


def shp_aggregate() -> dict[str, Any]:
    return {
        "anchor": {
            "year": 2004,
            "estimate": 0.67443,
            "standard_error": 0.003833,
            "wald_95_interval": [0.666918, 0.681943],
        },
        "sensitivity_envelope": [0.624968, 0.702060],
        "years": [2005, 2004, 2003],
        "n_people_with_any_response": 14756,
        "n_people_complete": 1822,
        "n_per_wave": {"2003": 5092, "2004": 7831, "2005": 6367},
        "multiwave": {
            "converged": True,
            "at_parameter_bound": False,
            "reliability": [0.670339, 0.67443, 0.680314],
            "persistence": 0.961357,
            "max_complete_case_correlation_residual": 0.078283,
        },
        "sensitivity": {
            "observed_before_2004_n": 9096,
            "complete_case_multiwave": {
                "reliability": [0.69, 0.688101, 0.685],
                "converged": True,
                "at_parameter_bound": False,
            },
            "observed_before_2004_multiwave": {
                "reliability": [0.678, 0.678954, 0.680],
                "converged": True,
                "at_parameter_bound": False,
            },
        },
        "successor_1": {
            "starts_sensitivity": {
                "status": "admissible",
                "anchor": shp_public()["starts"],
                "diagnostics": {"converged": True, "at_parameter_bound": False},
                "persistence": 0.716864,
                "trait_share_of_latent_variance": {"year": 2004, "value": 0.758495},
            },
            "wave_2004_description": {
                "status": "descriptive",
                "primary_fit": {
                    "2003": {"estimate": 0.675445},
                    "2005": {"estimate": 0.673487},
                },
                "first_valid_answer_2004": {
                    "status": "estimated",
                    "fit": {"converged": True, "at_parameter_bound": False},
                    "year": 2004,
                    "n_people": 3684,
                    "estimate": 0.681942,
                    "standard_error": 0.010003,
                },
            },
        },
    }


def heise_aggregate() -> dict[str, Any]:
    aggregate = shp_aggregate()
    estimates = [
        0.672749,
        0.675090,
        0.691308,
        0.696851,
        0.624968,
        0.683703,
        0.701641,
        0.695157,
        0.702060,
    ]
    aggregate["triplets"] = [
        {
            "years": [start, start + 1, start + 2],
            "heise_reliability": estimate,
            "heise_standard_error": 0.012144,
        }
        for start, estimate in zip(range(1999, 2008), estimates, strict=True)
    ]
    return aggregate


def test_round4_heise_windows_are_selected_by_year_and_match_the_envelope() -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    aggregate = heise_aggregate()
    aggregate["triplets"].reverse()
    final = {"v4.shp.env_lo": "0.625", "v4.shp.env_hi": "0.702"}
    result = build_journal(
        public, final, secondary_catalog(public), rows, shp_aggregate=aggregate
    )
    assert result.values["j.shp.heise.w1999"] == "0.673"
    assert result.values["j.shp.heise.w2003"] == "0.625"
    assert result.values["j.shp.heise.w2007"] == "0.702"
    assert result.values["j.shp.heise.w1999.se"] == "0.012"
    assert result.values["j.shp.heise.min"] == "0.625"
    assert result.values["j.shp.heise.max"] == "0.702"
    assert result.values["j.shp.heise.spread"] == "0.077"
    table = result.tables["journal-esm-heise-windows.tex"]
    assert r"\label{tab:heise-windows}" in table
    assert table.index("j.shp.heise.w1999}") < table.index("j.shp.heise.w2007}")


@pytest.mark.parametrize(
    "change",
    (
        "missing",
        "duplicate",
        "nonconsecutive",
        "envelope",
        "final",
        "nonfinite",
        "negative_se",
    ),
)
def test_round4_heise_refuses_incomplete_windows_or_conflicting_extrema(
    change: str,
) -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    aggregate = heise_aggregate()
    final = {"v4.shp.env_lo": "0.625", "v4.shp.env_hi": "0.702"}
    windows = aggregate["triplets"]
    if change == "missing":
        windows.pop()
    elif change == "duplicate":
        windows[-1]["years"] = windows[0]["years"]
    elif change == "nonconsecutive":
        windows[0]["years"] = [1999, 2001, 2002]
    elif change == "envelope":
        windows[4]["heise_reliability"] = 0.62
    elif change == "final":
        final["v4.shp.env_hi"] = "0.703"
    elif change == "nonfinite":
        windows[0]["heise_reliability"] = float("nan")
    else:
        windows[0]["heise_standard_error"] = -0.01
    with pytest.raises(ValueError, match="Heise"):
        build_journal(
            public, final, secondary_catalog(public), rows, shp_aggregate=aggregate
        )


def test_round4_heise_missing_se_is_reported_without_deriving_an_interval() -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    aggregate = heise_aggregate()
    del aggregate["triplets"][0]["heise_standard_error"]
    result = build_journal(
        public, {}, secondary_catalog(public), rows, shp_aggregate=aggregate
    )
    assert "j.shp.heise.w1999.se" not in result.values
    assert result.values["j.shp.heise.w1999"] == "0.673"
    assert "not available" in result.tables["journal-esm-heise-windows.tex"]
    assert any("heise_standard_error" in note for note in result.notes)


def test_shp_rounding_reuses_only_exact_final_strings() -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    final = {
        "v4.shp.estimate": "0.674",
        "v4.shp.wald_lo": "0.667",
        "v4.shp.wald_hi": "0.682",
        "v4.shp.env_lo": "0.625",
        "v4.shp.env_hi": "0.702",
    }
    result = build_journal(public, final, secondary_catalog(public), rows)
    assert not any(
        "j.shp." + key.removeprefix("v4.shp.") in result.values for key in final
    )
    assert result.values["j.shp.starts.estimate"] == "0.696"
    assert result.values["j.shp.starts.wald_lo"] == "0.685"
    assert result.values["j.shp.starts.wald_hi"] == "0.708"
    final["v4.shp.estimate"] = "0.674430"
    result = build_journal(public, final, secondary_catalog(public), rows)
    assert result.values["j.shp.estimate"] == "0.674"
    assert final["v4.shp.estimate"] == "0.674430"


@pytest.mark.parametrize("field", ["estimate", "wald_95_interval"])
def test_null_starts_values_raise_clear_value_errors(field: str) -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    public["objects"]["shp"]["starts"][field] = None
    with pytest.raises(ValueError, match="STARTS.*" + field):
        build_journal(public, {}, secondary_catalog(public), rows)


@pytest.mark.parametrize("suffix", ["estimate", "wald_lo", "wald_hi"])
def test_starts_values_must_match_the_catalog(suffix: str) -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    catalog = secondary_catalog(public)
    catalog["values"]["v4.shp.starts." + suffix] = "0.699"
    with pytest.raises(ValueError, match=r"STARTS.*catalog"):
        build_journal(public, {}, catalog, rows)


@pytest.mark.parametrize(
    "field", ["estimate", "wald_95_interval", "standard_error", "year"]
)
def test_public_shp_anchor_must_equal_the_approved_aggregate(field: str) -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    aggregate = shp_aggregate()
    aggregate["anchor"][field] = [0.66, 0.68] if field == "wald_95_interval" else 0.7
    with pytest.raises(ValueError, match="SHP.*aggregate.*" + field):
        build_journal(
            public, {}, secondary_catalog(public), rows, shp_aggregate=aggregate
        )


@pytest.mark.parametrize(
    ("path", "field", "value"),
    [
        (("multiwave",), "converged", False),
        (("multiwave",), "at_parameter_bound", True),
        (("sensitivity", "complete_case_multiwave"), "converged", False),
        (("sensitivity", "observed_before_2004_multiwave"), "at_parameter_bound", True),
        (("successor_1", "starts_sensitivity"), "status", "failed"),
        (("successor_1", "starts_sensitivity", "diagnostics"), "converged", False),
        (
            ("successor_1", "starts_sensitivity", "diagnostics"),
            "at_parameter_bound",
            True,
        ),
        (("successor_1", "wave_2004_description"), "status", "failed"),
        (
            ("successor_1", "wave_2004_description", "first_valid_answer_2004"),
            "status",
            "failed",
        ),
        (
            ("successor_1", "wave_2004_description", "first_valid_answer_2004", "fit"),
            "converged",
            False,
        ),
        (
            ("successor_1", "wave_2004_description", "first_valid_answer_2004", "fit"),
            "at_parameter_bound",
            True,
        ),
    ],
)
def test_shp_aggregate_rejects_failed_or_inadmissible_fits(
    path: tuple[str, ...],
    field: str,
    value: Any,
) -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    aggregate = shp_aggregate()
    target = aggregate
    for part in path:
        target = target[part]
    target[field] = value
    with pytest.raises(ValueError, match="SHP.*" + field):
        build_journal(
            public, {}, secondary_catalog(public), rows, shp_aggregate=aggregate
        )


def test_shp_aggregate_formats_counts_and_selects_2004_by_year() -> None:
    public, rows = inputs(curve())
    public["objects"]["shp"] = shp_public()
    result = build_journal(
        public, {}, secondary_catalog(public), rows, shp_aggregate=shp_aggregate()
    )
    expected = {
        "n_any": "14,756",
        "n_complete": "1,822",
        "n_pre2004": "9,096",
        "n_wave.min": "5,092",
        "n_wave.max": "7,831",
        "multiwave.r_t.min": "0.670",
        "multiwave.r_t.max": "0.680",
        "multiwave.persistence": "0.961",
        "multiwave.max_cc_residual": "0.078",
        "complete_case.r2004": "0.688",
        "pre2004.r2004": "0.679",
        "wave.r2003": "0.675",
        "wave.r2005": "0.673",
        "refresh.n": "3,684",
        "refresh.r2004": "0.682",
        "refresh.se": "0.010",
        "starts.persistence": "0.717",
        "starts.trait_share_2004": "0.758",
    }
    assert {key: result.values["j.shp." + key] for key in expected} == expected
    aggregate = shp_aggregate()
    aggregate["sensitivity"]["complete_case_multiwave"]["reliability"].pop()
    with pytest.raises(ValueError, match=r"years|waves"):
        build_journal(
            public, {}, secondary_catalog(public), rows, shp_aggregate=aggregate
        )


def test_crosswalk_uses_named_references_not_record_order() -> None:
    public, rows = inputs(curve())
    ranges = [
        {
            "reference": reference,
            "r": r,
            "low": low,
            "high": low + 0.01426,
            "failures": 0,
            "values": 10,
        }
        for reference, low in (
            ("a = 0", 0.46945),
            ("B η = 0.25", 0.46143),
            ("B η = 0.50", 0.45830),
        )
        for r in SHARES
    ]
    public["objects"]["crosswalk"] = {
        "declared_plan": True,
        "replicates": 10,
        "ranges": ranges[::-1],
    }
    result = build_journal(public, {}, secondary_catalog(public), rows)
    assert (
        len([key for key in result.values if key.startswith("j.shp.crosswalk.")]) == 54
    )
    assert result.values["j.shp.crosswalk.a0.r050.low"] == "0.469"
    assert result.values["j.shp.crosswalk.a0.r050.high"] == "0.484"
    assert result.values["j.shp.crosswalk.b025.r050.low"] == "0.461"
    assert result.values["j.shp.crosswalk.b050.r050.low"] == "0.458"
    public["objects"]["crosswalk"]["ranges"].pop()
    with pytest.raises(ValueError, match="nine"):
        build_journal(public, {}, secondary_catalog(public), rows)


def test_anchoring_inventory_counts_zero_strength_gaps_only_in_invalid_units() -> None:
    public, rows = inputs(
        curve(),
        curve(
            "w075-limit",
            tier=5,
            scenario="omega075",
            status="completo inválido",
            gaps={0: "family_limit", 0.1: "solver"},
        ),
        curve(
            "w075-solver",
            tier=5,
            r=0.55,
            scenario="omega075",
            status="completo inválido",
            gaps={0: "solver", 0.1: "family_limit"},
        ),
        curve(
            "w100-solver",
            tier=5,
            scenario="omega100",
            status="completo inválido",
            gaps={0: "solver"},
        ),
        curve("valid", tier=5, r=0.6, scenario="omega100", gaps={0.1: "family_limit"}),
        curve(
            "control",
            tier=3,
            channel="latent",
            scenario="omega100",
            status="completo inválido",
            gaps={0: "family_limit"},
        ),
    )
    result = build_journal(public, {}, secondary_catalog(public), rows)
    assert result.values["j.inventory.invalid.omega075.zero_gap.family_limit"] == "1"
    assert result.values["j.inventory.invalid.omega075.zero_gap.solver"] == "1"
    assert result.values["j.inventory.invalid.omega100.zero_gap.family_limit"] == "0"
    assert result.values["j.inventory.invalid.omega100.zero_gap.solver"] == "1"


@pytest.mark.parametrize("gap", [None, "validation", "propagation"])
def test_zero_gap_kind_counts_must_cover_every_invalid_anchoring_unit(
    gap: str | None,
) -> None:
    public, rows = inputs(
        curve(),
        curve(
            "invalid",
            tier=5,
            scenario="omega075",
            status="completo inválido",
            gaps={0: gap} if gap is not None else None,
        ),
    )
    with pytest.raises(ValueError, match=r"zero-strength gap.*invalid"):
        build_journal(public, {}, secondary_catalog(public), rows)


@pytest.mark.parametrize("field", ["low", "high"])
def test_null_crosswalk_ranges_raise_clear_value_errors(field: str) -> None:
    public, rows = inputs(curve())
    record = {
        "reference": "a = 0",
        "r": 0.5,
        "low": 0.4,
        "high": 0.5,
        "failures": 0,
        "values": 10,
    }
    record[field] = None
    public["objects"]["crosswalk"] = {
        "declared_plan": True,
        "replicates": 10,
        "ranges": [record],
    }
    with pytest.raises(ValueError, match="crosswalk.*" + field):
        build_journal(public, {}, secondary_catalog(public), rows)


@pytest.mark.parametrize(("failures", "values"), [(1, 9), (0, 9), (None, 10)])
def test_crosswalk_rejects_failures_and_missing_replicates(
    failures: Any, values: int
) -> None:
    public, rows = inputs(curve())
    public["objects"]["crosswalk"] = {
        "declared_plan": True,
        "replicates": 10,
        "ranges": [
            {
                "reference": "a = 0",
                "r": 0.5,
                "low": 0.4,
                "high": 0.5,
                "failures": failures,
                "values": values,
            }
        ],
    }
    with pytest.raises(ValueError, match=r"crosswalk.*failures|crosswalk.*replicates"):
        build_journal(public, {}, secondary_catalog(public), rows)


def test_partial_status_has_one_english_label() -> None:
    from ic_study.analysis.v4_journal_export import CSV_STATUS, STATUS

    assert (
        STATUS["parcial por encerramento operacional"]
        == "partial at the operational close"
    )
    assert CSV_STATUS == STATUS


def test_english_units_csv_preserves_rows_columns_and_every_other_byte() -> None:
    import csv
    import io

    from ic_study.analysis.v4_journal_export import translate_all_units

    source = (
        "status,a_star,sensitivity\r\n"
        '"completo válido",0.10,main\r\n'
        "completo inválido,suppressed,omega075\r\n"
        'parcial por encerramento operacional,"censored at gap a=0.9",steps24\r\n'
        "não iniciado,NA,main\r\n"
    ).encode()
    expected = (
        b"status,a_star,sensitivity\r\n"
        b'"complete and valid",0.10,main\r\n'
        b"complete but invalid,suppressed,omega075\r\n"
        b'partial at the operational close,"censored at gap a=0.9",steps24\r\n'
        b"not started,NA,main\r\n"
    )
    translated = translate_all_units(source)
    assert translated == expected
    before = list(csv.reader(io.StringIO(source.decode(), newline="")))
    after = list(csv.reader(io.StringIO(translated.decode(), newline="")))
    assert len(before) == len(after) == 5
    assert before[0] == after[0]
    assert all(
        old[1:] == new[1:] for old, new in zip(before[1:], after[1:], strict=True)
    )
    assert translated.isascii()
    with pytest.raises(ValueError, match="status"):
        translate_all_units(source.replace("não iniciado".encode(), b"unknown status"))
    with pytest.raises(ValueError, match="Untranslated"):
        translate_all_units(
            source.replace(b"steps24", "sensibilidade não definida".encode())
        )


def test_cli_optional_shp_records_hash_and_keeps_aggregate_immutable(
    tmp_path: Any,
) -> None:
    import hashlib
    import json

    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    public_path = tmp_path / "public.json"
    public = json.loads(public_path.read_bytes())
    public["objects"]["shp"] = shp_public()
    public_path.write_text(json.dumps(public))
    (tmp_path / "catalog.json").write_text(json.dumps(secondary_catalog(public)))
    (tmp_path / "final.json").write_text(
        json.dumps({"values": {"v4.protocol.shp.anchor_year": "2004"}})
    )
    aggregate_path = tmp_path / "shp.json"
    aggregate_path.write_text(json.dumps(shp_aggregate()))
    before = aggregate_path.read_bytes()
    assert main([*args, "--shp-aggregate", str(aggregate_path)]) == 0
    payload = json.loads((tmp_path / "journal.json").read_bytes())
    assert payload["sources"]["shp_aggregate"] == hashlib.sha256(before).hexdigest()
    assert payload["values"]["j.shp.n_any"] == "14,756"
    assert aggregate_path.read_bytes() == before
    generated = tmp_path / "generated"
    assert (generated / "online-resource-2-units.csv").read_bytes().isascii()
    assert (
        "archived original" in (generated / "online-resource-2-README.txt").read_text()
    )
    assert main(args) == 0
    payload = json.loads((tmp_path / "journal.json").read_bytes())
    assert "shp_aggregate" not in payload["sources"]
    assert "j.shp.n_any" not in payload["values"]


def test_cli_translation_failure_preserves_previous_outputs(
    tmp_path: Any, capsys: Any
) -> None:
    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    inventory = tmp_path / "inventory.csv"
    inventory.write_text(
        inventory.read_text().replace("completo válido", "desconhecido")
    )
    generated = tmp_path / "generated"
    generated.mkdir()
    english = generated / "online-resource-2-units.csv"
    english.write_bytes(b"previous CSV")
    values = tmp_path / "journal.json"
    values.write_bytes(b"previous values")
    with pytest.raises(SystemExit) as error:
        main(args)
    assert error.value.code == 2
    assert "Unknown all-units status" in capsys.readouterr().err
    assert english.read_bytes() == b"previous CSV"
    assert values.read_bytes() == b"previous values"
    assert [p.name for p in generated.iterdir()] == [english.name]


def test_round3_logit_margins_use_unrounded_bands_and_list_tied_minima() -> None:
    import math

    public, rows = inputs(curve())
    for c in public["objects"]["release"]["curves"].values():
        if c["meta"]["r"] in (0.5, 0.55):
            index = c["available"].index(0.03)
            p = c["auc"][index]
            midpoint = (math.log(p / (1 - p)) + math.log(0.7 / 0.3)) / 2
            c["upper"][index] = 1 / (1 + math.exp(-midpoint))
    result = build_journal(
        public, {"v4.gate.G2c.a003.lower": "0.470"}, secondary_catalog(public), rows
    )
    assert result.values["j.b.margin.a0300.se_factor.r050"] == "2.0"
    assert result.values["j.b.margin.a0300.se_factor.r055"] == "2.0"
    assert result.values["j.b.margin.a0300.se_factor.min"] == "2.0"
    assert result.values["j.b.margin.a0300.se_factor.min.r"] == "0.50, 0.55"
    assert result.values["j.gate.g2c.a0300.se_growth_max"] == "1.46"
    assert "Region &" not in result.tables["journal-table-boundaries-B.tex"]
    assert (
        r"All \resultnum{j.b.first.large.n}{9} first-boundary intervals"
        in result.tables["journal-table-boundaries-B.tex"]
    )


def test_round3_counts_frozen_flags_over_fitted_cells_in_the_declared_range() -> None:
    public, rows = inputs(curve())
    catalog = secondary_catalog(public)
    for code, a, success, lost in (
        ("a0300", "0.03", "true", "false"),
        ("a1000", "0.10", "true", "true"),
        ("a3000", "0.30", "true", "false"),
        ("a6000", "0.60", "false", "unavailable"),
        ("a9000", "0.90", "true", "false"),
    ):
        stem = "v4x.x3.cells.r050." + code
        catalog["values"].update(
            {
                stem + ".cell.a": a,
                stem + ".free.success": success,
                stem + ".lost_crossing": lost,
            }
        )
    final = {"v4x.x3.count.lost_crossing": "1"}
    result = build_journal(public, final, catalog, rows)
    assert result.values["j.x3.lost_crossings.n"] == "1"
    assert result.values["j.x3.lost_crossings.cells"] == "2"
    final["v4x.x3.count.lost_crossing"] = "2"
    with pytest.raises(ValueError, match="Frozen lost-crossing count"):
        build_journal(public, final, catalog, rows)


def test_round3_oracle_reference_keys_and_frozen_feature_boundary() -> None:
    public, rows = inputs(curve())
    final = exploratory_values()
    final["v4x.x7.units.r055.x7.first"] = "0.3"
    for r in SHARES:
        stem = f"v4x.x4.x4a.r{round(r * 100):03d}.a0300."
        final.update(
            {
                stem + "cell.a": "0.03",
                stem + "cell.r": str(r),
                stem + "x4a.auc_ref": "0.65149" if r >= 0.85 else "0.6",
            }
        )
    stem = "v4x.x4.x4a.r055.a1000."
    final.update(
        {
            stem + "cell.a": "0.1",
            stem + "cell.r": "0.55",
            stem + "x4a.auc_ref": "0.682714",
            stem + "x4a.auc_ref_interval_95.i000": "0.671661",
            stem + "x4a.auc_ref_interval_95.i001": "0.693736",
        }
    )
    result = build_journal(public, final, exploratory_catalog(public), rows)
    assert result.values["j.x7.frozen_first.r055"] == "0.30"
    assert result.values["j.x4a.r055.a1000.auc_ref"] == "0.683"
    assert result.values["j.x4a.r055.a1000.auc_ref.lower"] == "0.672"
    assert result.values["j.x4a.r055.a1000.auc_ref.upper"] == "0.694"
    assert result.values["j.x4a.a0300.auc_ref.max"] == "0.651"
    assert result.values["j.x4a.a0300.auc_ref.max.r"] == "0.85, 0.90"
    final[stem + "cell.a"] = "0.03"
    with pytest.raises(ValueError, match="Oracle reference cell mismatch"):
        build_journal(public, final, exploratory_catalog(public), rows)


def test_other_models_compacts_c_and_d_without_losing_share_exceptions() -> None:
    models = []
    for r in SHARES:
        c = curve(f"c-{r}", r=r, tier=2, family="C", status="completo inválido")
        c["auc"][0] = 1.0
        models.append(c)
        a, kind = (
            (0.01, "solver")
            if r == 0.5
            else ((0.003, "propagation") if r == 0.6 else (0.1, "family_limit"))
        )
        models.append(
            curve(f"d-{r}", r=r, tier=2, family="D", first=None, gaps={a: kind})
        )
        for family in ("A", "E"):
            first = 0.3 if r == 0.5 or (family == "E" and r <= 0.6) else 0.1
            gaps = (
                {0.6: "solver", 0.9: "solver"}
                if family == "E" and r == 0.55
                else {0.9: "solver"}
                if family == "E" and r == 0.7
                else {}
            )
            c = curve(
                f"{family}-{r}", r=r, tier=2, family=family, first=first, gaps=gaps
            )
            if gaps:
                c["sustained"] = {
                    "point": None,
                    "interval": [None, None],
                    "censoring": "gap at a=0.9",
                    "interval_censoring": "gap at a=0.9",
                }
            models.append(c)
    public, rows = inputs(curve(), *models)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    table = result.tables["journal-table-other-models.tex"]
    assert sum(line.startswith("C &") for line in table.splitlines()) == 1
    assert sum(line.startswith("D &") for line in table.splitlines()) == 1
    assert sum(line.startswith("A &") for line in table.splitlines()) == 2
    assert sum(line.startswith("E &") for line in table.splitlines()) == 2
    assert (
        r"A & \resultnum{j.models.r055.r}{0.55}--\resultnum{j.models.r090.r}{0.90}"
        r" & \resultnum{j.models.A.r055.first.point}{0.10}"
        r" & \resultnum{j.models.A.r055.sustained.point}{0.10}"
    ) in table
    assert (
        r"E & \resultnum{j.models.r050.r}{0.50}--\resultnum{j.models.r060.r}{0.60}"
        r" & \resultnum{j.models.E.r050.first.point}{0.30}"
        r" & \resultnum{j.models.E.r050.sustained.point}{0.30}; censored at $r=$ "
        r"\resultnum{j.models.r055.r}{0.55} (fit gaps at "
        r"\resultnum{j.models.E.r055.sustained.gap.0.a}{0.60}, "
        r"\resultnum{j.models.E.r055.sustained.gap.1.a}{0.90})"
    ) in table
    assert (
        r"censored at $r=$ \resultnum{j.models.r070.r}{0.70} (fit gap at "
        r"\resultnum{j.models.E.r070.sustained.gap.0.a}{0.90})"
    ) in table
    assert r"\resultnum{j.models.C.zero_auc.min}{1.000}" in table
    assert r"\resultnum{j.models.D.first_gap.a1000.family_limit.n}{7}" in table
    assert r"\resultnum{j.models.D.r050.first.censoring_gap.a}{0.01}" in table
    assert r"\resultnum{j.models.D.r060.first.censoring_gap.a}{0.003}" in table
    assert "other solver status" in table and "propagation gap" in table
    import re

    for key, value in re.findall(r"\\resultnum\{([^{}]+)\}\{([^{}]+)\}", table):
        assert result.values[key] == value
    stripped = re.sub(r"\\resultnum\{[^{}]+\}\{[^{}]+\}", "", table)
    stripped = re.sub(r"\\(?:label|ref)\{[^{}]+\}", "", stripped)
    stripped = re.sub(r"\d+(?:\.\d+)?(?:pt|mm|cm|em)", "", stripped)
    assert not re.search(r"\d", stripped)
    body = table.split(r"\midrule")[1].split(r"\botrule")[0]
    assert r"\ref" not in body


@pytest.mark.parametrize(
    ("name", "change"),
    [
        ("first", "point"),
        ("sustained", "point"),
        ("sustained", "censoring"),
        ("first", "status"),
        ("first", "family"),
    ],
)
def test_common_model_boundary_rejects_nonuniform_groups_before_rendering(
    name: str, change: str
) -> None:
    from ic_study.analysis.v4_journal_export import Numbers, _uniform_model_boundary

    a = curve("a-050", tier=2, family="A")
    b = curve("a-055", tier=2, family="A", r=0.55)
    if change == "point":
        b[name]["point"] = 0.100001
    elif change == "censoring":
        b = curve("a-055", tier=2, family="A", r=0.55, gaps={0.9: "solver"})
        b["sustained"].update({"point": None, "censoring": "gap at a=0.9"})
    elif change == "status":
        b["status"] = "completo inválido"
    else:
        b["meta"]["family"] = "E"
    public, rows = inputs(curve(), a, b)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    group = [c for c in result.curves if c.tier == 2]
    if change == "point":
        assert all(
            result.values[c.prefix + "." + name + ".point"] == "0.10" for c in group
        )
    with pytest.raises(ValueError, match="Nonuniform model " + name):
        _uniform_model_boundary(Numbers({}, result.values), group, name)


@pytest.mark.parametrize("shares", [(0.5, 0.6), (0.5, 0.55, 0.6)])
def test_model_share_ranges_do_not_bridge_missing_or_different_boundaries(
    shares: tuple[float, ...],
) -> None:
    models = [
        curve(f"a-{r}", tier=2, family="A", r=r, first=0.3 if r == 0.55 else 0.1)
        for r in shares
    ]
    public, rows = inputs(curve(), *models)
    result = build_journal(public, {}, secondary_catalog(public), rows)
    lines = [
        line
        for line in result.tables["journal-table-other-models.tex"].splitlines()
        if line.startswith("A &")
    ]
    assert len(lines) == len(shares)
    assert all("--" not in line.split(" & ")[1] for line in lines)


def test_main_boundary_notes_are_short_and_glossary_refs_stay_outside_cells() -> None:
    import re

    public, rows = inputs(curve())
    result = build_journal(public, {}, secondary_catalog(public), rows)
    for filename, limit in (
        ("journal-table-boundaries-B.tex", 70),
        ("journal-table-other-models.tex", 80),
    ):
        table = result.tables[filename]
        body = table.split(r"\midrule")[1].split(r"\botrule")[0]
        assert r"\ref" not in body
        note = table.split(r"\parbox{\linewidth}{")[1]
        assert r"\esmresource, Table~\ref{esm-tab:glossary-terms}" in note
        if filename == "journal-table-other-models.tex":
            assert r"fit statuses: Table~\ref{esm-tab:glossary-states}" in note
        visible = re.sub(r"\\resultnum\{[^{}]+\}\{([^{}]+)\}", r"\1", note)
        visible = re.sub(r"\\ref\{[^{}]+\}", "S1", visible)
        visible = visible.replace(r"\esmresource", "Online Resource 1")
        visible = re.sub(r"\\end\{[^{}]+\}", "", visible)
        assert len(visible.split()) <= limit
    assert (
        "protocol's large region" not in result.tables["journal-table-boundaries-B.tex"]
    )


def test_sanitizer_removes_private_fields_and_paths_preserving_every_other_value() -> (
    None
):
    import copy

    from ic_study.analysis.v4_journal_export import sanitize_exploratory_value

    planted = {
        "host": {"hostname": "lab-host-a", "CPU": "planted", "kernel": "private"},
        "nested": {
            "hostName": "private",
            "username": "private",
            "absolute_path": "/private/tmp/result.json",
            "note": "record from /home/planted/results",
            "relative_path": "results/cells.json",
            "value": 0.12345678901234567,
        },
        "items": [
            "kept",
            "output in ~/results",
            "/absolute/path",
            {"cpu_seconds": 1.2, "auc": 0.75},
            "kept again",
        ],
        "a/b~c": "/private/tmp/details",
        "counts": [0, 3, None, True],
        "timing": {"wall_seconds": 2.3},
    }
    original = copy.deepcopy(planted)
    clean, paths = sanitize_exploratory_value(planted)
    assert clean == {
        "nested": {"relative_path": "results/cells.json", "value": 0.12345678901234567},
        "items": ["kept", {"auc": 0.75}, "kept again"],
        "counts": [0, 3, None, True],
        "timing": {"wall_seconds": 2.3},
    }
    assert set(paths) == {
        "/host",
        "/nested/hostName",
        "/nested/username",
        "/nested/absolute_path",
        "/nested/note",
        "/items/1",
        "/items/2",
        "/items/3/cpu_seconds",
        "/a~1b~0c",
    }
    assert planted == original


def test_sanitizer_site_patterns_remove_strings_and_keys_without_changing_values() -> (
    None
):
    from ic_study.analysis.v4_journal_export import sanitize_exploratory_value

    planted = {
        "note": "LaB-HoSt-A output",
        "items": ["kept", "lab-host-b output", {"auc": 0.75}],
        "labhost-a/b~c": {"auc": 0.8},
        "relative_path": "results/cells.json",
    }
    assert sanitize_exploratory_value(planted) == (planted, ())
    clean, paths = sanitize_exploratory_value(
        planted, private_patterns=(r"\blab-?host-a\b", r"\blab-host-b\b")
    )
    assert clean == {
        "items": ["kept", {"auc": 0.75}],
        "relative_path": "results/cells.json",
    }
    assert paths == ("/note", "/items/1", "/labhost-a~1b~0c")


@pytest.mark.parametrize(
    "path",
    [
        "/private/tmp/result.json",
        "record from /Users/planted/results",
        "record from /home/planted/results",
        "record from /var/home/planted/results",
        "record from /root/results",
        "record from ~/results",
        r"C:\results\cells.json",
        r"\\server\results\cells.json",
        "file:///tmp/result.json",
    ],
)
def test_sanitizer_generic_rules_remove_absolute_and_home_paths(path: str) -> None:
    from ic_study.analysis.v4_journal_export import sanitize_exploratory_value

    assert sanitize_exploratory_value({"note": path, "auc": 0.75}) == (
        {"auc": 0.75},
        ("/note",),
    )


def test_sanitizer_site_pattern_refuses_private_root_string() -> None:
    from ic_study.analysis.v4_journal_export import sanitize_exploratory_value

    with pytest.raises(ValueError, match="private root string"):
        sanitize_exploratory_value("lab-host-a", private_patterns=("lab-host-a",))


def test_sanitizer_cli_records_hashes_and_refuses_source_aliases(tmp_path: Any) -> None:
    import hashlib
    import json

    from ic_study.analysis.v4_journal_export import EXPLORATORY_FILES, main

    src, out = tmp_path / "src", tmp_path / "out"
    src.mkdir()
    sources = {}
    for name in EXPLORATORY_FILES:
        data = json.dumps(
            {"host": {"hostname": "lab-host-a"}, "result": [0.53, 42]}
        ).encode()
        (src / name).write_bytes(data)
        sources[name] = data
    args = ["--sanitize-exploratory", str(src), str(out)]
    assert main(args) == 0
    readme = (out / "README.md").read_text()
    for name, data in sources.items():
        assert (src / name).read_bytes() == data
        assert json.loads((out / name).read_bytes()) == {"result": [0.53, 42]}
        assert hashlib.sha256(data).hexdigest() in readme
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() in readme
    assert readme.count("- `/host`") == 4
    before = {path.name: path.read_bytes() for path in out.iterdir()}
    assert main(args) == 0
    assert {path.name: path.read_bytes() for path in out.iterdir()} == before
    with pytest.raises(SystemExit) as exc:
        main(["--sanitize-exploratory", str(src), str(src)])
    assert exc.value.code == 2
    assert all((src / name).read_bytes() == data for name, data in sources.items())


def test_sanitizer_cli_repeated_site_patterns_are_not_recorded(tmp_path: Any) -> None:
    import json

    from ic_study.analysis.v4_journal_export import EXPLORATORY_FILES, main

    src, out = tmp_path / "src", tmp_path / "out"
    src.mkdir()
    for name in EXPLORATORY_FILES:
        (src / name).write_text(
            json.dumps(
                {
                    "host": {"hostname": "lab-host-a"},
                    "note": "LaB-HoSt-A output",
                    "items": ["kept", "lab-host-b output"],
                    "result": [0.53, 42],
                }
            )
        )
    assert (
        main(
            [
                "--sanitize-exploratory",
                str(src),
                str(out),
                "--private-pattern",
                r"\blab-host-a\b",
                "--private-pattern",
                r"\blab-host-b\b",
            ]
        )
        == 0
    )
    for name in EXPLORATORY_FILES:
        assert json.loads((out / name).read_bytes()) == {
            "items": ["kept"],
            "result": [0.53, 42],
        }
    readme = (out / "README.md").read_text()
    assert "--private-pattern" in readme
    assert "lab-host-a" not in readme
    assert "lab-host-b" not in readme
    assert readme.count("- `/note`") == 4
    assert readme.count("- `/items/1`") == 4


def test_sanitizer_invalid_site_pattern_preserves_outputs(
    tmp_path: Any, capsys: Any
) -> None:
    from ic_study.analysis.v4_journal_export import EXPLORATORY_FILES, main

    src, out = tmp_path / "src", tmp_path / "out"
    src.mkdir()
    out.mkdir()
    for name in EXPLORATORY_FILES:
        (src / name).write_text('{"auc": 0.75}')
        (out / name).write_bytes(b"previous archive")
    before = {path.name: path.read_bytes() for path in out.iterdir()}
    with pytest.raises(SystemExit) as exc:
        main(
            [
                "--sanitize-exploratory",
                str(src),
                str(out),
                "--private-pattern",
                "lab-host-a[",
            ]
        )
    assert exc.value.code == 2
    error = capsys.readouterr().err
    assert "Invalid private pattern" in error
    assert "lab-host-a" not in error
    assert {path.name: path.read_bytes() for path in out.iterdir()} == before


def test_journal_cli_rejects_site_patterns_without_sanitizing(
    tmp_path: Any, capsys: Any
) -> None:
    from ic_study.analysis.v4_journal_export import main

    with pytest.raises(SystemExit) as exc:
        main([*cli_inputs(tmp_path), "--private-pattern", "lab-host-a"])
    assert exc.value.code == 2
    assert "requires --sanitize-exploratory" in capsys.readouterr().err
    assert not (tmp_path / "generated").exists()
    assert not (tmp_path / "journal.json").exists()


def diagnostic_objects() -> dict[str, Any]:
    summaries: dict[str, dict[str, Any]] = {
        stage: {"completed": n, "planned": n, "pass": True}
        for stage, n in (("G0", 3), ("G1b", 5000), ("G1c", 2), ("G2", 4), ("G2c", 3))
    }
    summaries["G1b"]["coverage_counts"] = {
        "gaussian-icc0": 954,
        "gaussian-icc05": 959,
        "non-gaussian": 954,
        "ties": 952,
        "dependent-slots": 974,
    }
    summaries["G2"].update(
        {
            "cell_ratios": [0.8, 1.2],
            "cell_lower": [0.6, 0.9],
            "cell_upper": [1.0, 1.4],
            "pooled_ratio": 1.0,
            "pooled_lower": 0.8,
            "pooled_upper": 1.2,
        }
    )
    summaries["G2c"]["comparisons"] = [
        {"ratio": 1.1, "lower": 0.9, "upper": 1.5, "denominator": 100},
        {"ratio": 0.6, "lower": 0.4, "upper": 0.9, "denominator": 40},
    ]
    return {
        "gate": {
            "summaries": summaries,
            "g0_fits": [
                {"status": "anchor-exact", "gap": None, "count": 3},
                {"status": "family-limit-upper", "gap": "family_limit", "count": 2},
                {"status": "no-L1-root", "gap": "solver", "count": 1},
            ],
            "g0_evaluations": [{"value": 1, "count": 4}, {"value": 90, "count": 2}],
            "g1b_critical": [{"value": 2.7729, "count": 4}, {"value": 3.2, "count": 2}],
            "g2_cells": [[0.03, 0.5], [0.1, 0.7]],
        },
        "thresholds": {
            "cell_lower": 0.5,
            "cell_upper": 1.3,
            "pooled_lower": 0.8,
            "pooled_upper": 1.1,
        },
    }


def test_gate_preserves_public_counts_ratios_and_unclipped_reference_legend(
    tmp_path: Any,
    monkeypatch: Any,
) -> None:
    from itertools import pairwise

    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.text import Text

    from ic_study.analysis import v4_journal_export as module
    from ic_study.analysis.v4_report_figures import Render

    captured = []
    monkeypatch.setattr(module, "save", lambda fig, *_: captured.append(fig))
    module._gate_diagnostics(diagnostic_objects(), Render(tmp_path))
    fig = captured[0]
    try:
        fig.canvas.draw()
        fits, evaluations, coverage, critical, dispersion, nuisance, stages = fig.axes
        assert sum(patch.get_width() for patch in fits.patches) == 6
        assert sum(patch.get_height() for patch in evaluations.patches) == 6
        assert sum(patch.get_height() for patch in critical.patches) == 6
        np.testing.assert_allclose(
            coverage.lines[0].get_xdata(), [0.954, 0.959, 0.954, 0.952, 0.974]
        )
        np.testing.assert_allclose(
            [dispersion.lines[i].get_xdata()[0] for i in (0, 2, 4)], [0.8, 1.2, 1.0]
        )
        np.testing.assert_allclose(
            [nuisance.lines[i].get_xdata()[0] for i in (0, 2)], [1.1, 0.6]
        )
        assert len(stages.patches) == 10
        assert "3/3 tasks · pass" in [text.get_text() for text in stages.texts]
        renderer = fig.canvas.get_renderer()
        legend = coverage.get_legend().get_window_extent(renderer)
        assert not legend.overlaps(coverage.get_window_extent(renderer))
        assert not legend.overlaps(coverage._left_title.get_window_extent(renderer))
        for ax in fig.axes:
            ticks: list[Text] = []
            for axis, limits in ((ax.xaxis, ax.get_xlim()), (ax.yaxis, ax.get_ylim())):
                ticks.extend(
                    tick.label1
                    for tick in axis.get_major_ticks()
                    if min(limits) <= tick.get_loc() <= max(limits)
                )
            xlabels = [
                tick.label1.get_window_extent(renderer)
                for tick in ax.xaxis.get_major_ticks()
                if min(ax.get_xlim()) <= tick.get_loc() <= max(ax.get_xlim())
                and tick.label1.get_visible()
            ]
            assert all(not left.overlaps(right) for left, right in pairwise(xlabels))
            texts = [
                *ticks,
                *ax.texts,
                ax.xaxis.label,
                ax.yaxis.label,
                ax._left_title,
            ]
            for text in texts:
                if not text.get_visible() or not text.get_text():
                    continue
                bbox = text.get_window_extent(renderer)
                assert bbox.x0 >= -1 and bbox.y0 >= -1
                assert bbox.x1 <= fig.bbox.x1 + 1 and bbox.y1 <= fig.bbox.y1 + 1
    finally:
        plt.close(fig)


def test_inventory_plots_actual_states_and_never_invents_missing_units(
    tmp_path: Any,
    monkeypatch: Any,
) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    from ic_study.analysis import v4_journal_export as module
    from ic_study.analysis.v4_report_figures import Render

    public, _ = inputs(
        curve(), curve("invalid", family="C", tier=2, status="completo inválido")
    )
    captured = []
    monkeypatch.setattr(module, "save", lambda fig, *_: captured.append(fig))
    module._inventory(module._curves(public), Render(tmp_path))
    fig = captured[0]
    try:
        ax = fig.axes[0]
        assert [text.get_text() for text in fig.legends[0].get_texts()] == [
            "V: complete and valid (9)",
            "I: complete but invalid (1)",
        ]
        assert ax.get_xlabel() == "signal share r"
        cells = ax.collections[0].get_array()
        assert cells.count() == 10
        assert np.sum(cells == 0) == 9
        assert np.sum(cells == 1) == 1
        assert len(ax.texts) == 10
    finally:
        plt.close(fig)


def test_cli_emits_bound_diagnostic_captions_and_preserves_gate_source(
    tmp_path: Any,
) -> None:
    import json
    import re

    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path)
    path = tmp_path / "public.json"
    public = json.loads(path.read_bytes())
    public["objects"].update(diagnostic_objects())
    path.write_text(json.dumps(public))
    before = path.read_bytes()
    assert main(args) == 0
    assert path.read_bytes() == before
    generated = tmp_path / "generated"
    values = json.loads((tmp_path / "journal.json").read_bytes())["values"]
    for name, label in (
        ("gate", "gate-diagnostics"),
        ("inventory", "inventory-status"),
    ):
        tex = (generated / f"journal-esm-fig-{name}.tex").read_text()
        assert rf"\label{{fig:{label}}}" in tex
        for key, value in re.findall(r"\\resultnum\{([^{}]+)\}\{([^{}]+)\}", tex):
            assert values[key] == value
        caption = tex.split(r"\caption{")[1].split(r"}\label")[0]
        visible = re.sub(r"\\resultnum\{[^{}]+\}\{[^{}]+\}", "", caption)
        assert not re.search(r"[0-9]|\bG[0-2][abc]?\b|calibration-exposed", visible)
    assert (generated / "J4_gate_diagnostics.pdf").read_bytes().startswith(b"%PDF")
    assert (generated / "J5_inventory_status.pdf").read_bytes().startswith(b"%PDF")


def test_inventory_caption_rejects_count_disagreement_before_publication(
    tmp_path: Any,
) -> None:
    from ic_study.analysis.v4_journal_export import main

    args = cli_inputs(tmp_path, {"v4.inv.n_valid": "10"})
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2
    assert not (tmp_path / "generated").exists()


def test_sanitizer_cli_missing_input_does_not_publish_partial_archive(
    tmp_path: Any,
) -> None:
    from ic_study.analysis.v4_journal_export import main

    src, out = tmp_path / "src", tmp_path / "out"
    src.mkdir()
    (src / "x1a.json").write_text('{"value": 0.75}')
    with pytest.raises(SystemExit) as exc:
        main(["--sanitize-exploratory", str(src), str(out)])
    assert exc.value.code == 2
    assert not out.exists()


@pytest.mark.parametrize(
    "field",
    [
        "CPUInfo",
        "CPUModel",
        "CPUCount",
        "CPUSeconds",
        "hostName",
        "kernelVersion",
        "userName",
        "absolute_path",
        "absolutePath",
        "absolutePaths",
    ],
)
def test_sanitizer_recognizes_private_field_names_even_without_a_string_value(
    field: str,
) -> None:
    from ic_study.analysis.v4_journal_export import sanitize_exploratory_value

    clean, paths = sanitize_exploratory_value({"nested": {field: None, "auc": 0.75}})
    assert clean == {"nested": {"auc": 0.75}}
    assert paths == ("/nested/" + field,)
