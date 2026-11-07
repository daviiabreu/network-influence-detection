"""Export public-shape synthetic aggregates; never open experiment stores.

The aggregate envelope/fields follow 3334ac0f. Pure reading and summary
functions have identical source bytes here and at that revision.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from unittest import mock

import pytest

from ic_study.analysis.detection_v4_report import Inputs, Loaded, load_inputs
from ic_study.analysis.v4_exploratory_comparisons import compare_exploratory
from ic_study.analysis.v4_exploratory_export import (
    _boundary_consistency,
    _coverage_consistency,
    _table,
    export,
)
from ic_study.analysis.v4_report_export import (
    RESULT,
    generated_files,
    result_values,
    used_ids,
)
from ic_study.analysis.v4_report_protocol import protocol_values
from ic_study.analysis.v4_report_schema import GateRecords, parse_release
from ic_study.analysis.v4_report_synthetic import (
    GatePlan,
    UnitPlan,
    build_gate,
    build_release,
    logistic_profile,
    unit_keys,
)
from ic_study.simulation import v4_exploratory_x3 as x3
from ic_study.simulation import v4_exploratory_x4 as x4
from ic_study.simulation import v4_exploratory_x6 as x6
from ic_study.simulation import v4_exploratory_x7 as x7
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES

STUDY = Path(__file__).resolve().parents[2]
MANUSCRIPT = STUDY / "publications/jcss-manuscript"
SHELLS = MANUSCRIPT / "pipeline/drafts/2026-09-30/exploratory-results-shells.tex"


@pytest.mark.parametrize("kind", ["first", "sustained"])
def test_valid_uncensored_boundaries_must_contain_their_point(kind: str) -> None:
    for record in (
        {kind: 0.03, kind + "_interval": [0.001, 0.01]},
        {
            "unit_status": "completo válido",
            kind: {"point": 0.03, "interval": [0.001, 0.01]},
        },
    ):
        with pytest.raises(ValueError, match=f"X6R-03: x7/{kind}"):
            _boundary_consistency(record, "x7")
        _boundary_consistency(
            record
            | {"status": "completo inválido", "unit_status": "completo inválido"},
            "x7",
        )


def test_missing_interval_is_not_silently_treated_as_censoring() -> None:
    record = {"first": 0.03, "first_interval": [None, None]}
    with pytest.raises(ValueError, match="with a finite lower end"):
        _boundary_consistency(record, "x7")
    _boundary_consistency(record | {"first_interval_censoring": "gap"}, "x7")


@pytest.mark.parametrize("kind", ["first", "sustained"])
def test_uncensored_crossing_beyond_the_grid_leaves_the_upper_end_open(
    kind: str,
) -> None:
    for record in (
        {kind: 0.3, kind + "_interval": [0.3, None]},
        {
            "unit_status": "completo válido",
            kind: {"point": 0.3, "interval": [0.3, None]},
        },
    ):
        _boundary_consistency(record, "x7")
    for interval in ([0.6, None], [None, 0.3]):
        with pytest.raises(ValueError, match=f"X6R-03: x7/{kind}"):
            _boundary_consistency({kind: 0.3, kind + "_interval": interval}, "x7")


@pytest.mark.parametrize("fault", ["intersection", "gaps"])
def test_x6_rejects_inconsistent_joint_sets(fault: str) -> None:
    section = synthetic_x6()["x6a"]
    if fault == "intersection":
        for primary in [
            section["band"]["vs_d1"]["primary"],
            section["band"]["vs_d1"]["gaps_as_misses"],
        ]:
            primary["covered"] = 140
    else:
        section["band"]["vs_d1"]["gaps_as_misses"]["covered"] -= 1
    with pytest.raises(ValueError, match="X6R-02"):
        _coverage_consistency(section, "x6/x6a")


def test_export_rejects_incoherent_boundary_before_creating_outputs(
    tmp_path: Path,
) -> None:
    inputs = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(inputs["x7"].read_text())
    data["units"][0]["rich"]["first"] = 0.03
    inputs["x7"].write_text(json.dumps(data))
    with pytest.raises(ValueError, match=r"X6R-03: x7/units/0/rich/first"):
        export(inputs, tmp_path / "manuscript")
    assert not (tmp_path / "manuscript/generated").exists()


def envelope(kind: str, sizes: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": f"ic-study.v4-exploratory-{kind}.v1",
        "label": "exploratory; never promoted to confirmatory evidence",
        "synthetic": True,
        "declaration": {"synthetic": True},
        "release": {"synthetic": True},
        "sources": [],
        "sizes": sizes,
        "code": [],
        "host": [],
        "seeds": {},
        "timing": {},
    }


def synthetic_x3() -> dict[str, Any]:
    cells = []
    for i, (unit, position) in enumerate(x3.CELLS):
        kind = i % 6
        interval = [[-0.06, -0.02], [-0.01, 0.01], [-0.03, 0.04]][min(kind, 2)]
        row: dict[str, Any] = {
            "cell": x3.cell_identity(i, unit, position),
            "error": "SYNTHETIC execution error" if kind == 3 else None,
            "success": kind < 3,
            "gap": "known" if kind == 4 else "free" if kind == 5 else None,
            "attempts": ["known:interior", "free:budget"],
            "known": {"success": kind != 4, "auc": 0.74, "interval_95": [0.72, 0.76]},
            "free": {
                "success": kind < 3,
                "auc": 0.67,
                "interval_95": [0.65, 0.69],
                "attempts": [
                    {"matching_pairs": 1024, "status": "inner-solver-failure"},
                    {"matching_pairs": 4096, "status": "budget"},
                ],
            },
            "delta": {"point": -0.04, "interval_95": interval} if kind < 3 else None,
            "means": None,
        }
        if kind == 4:
            row["free"] = None
        row.update(x3.read_cell(row))
        cells.append(row)
    return {
        **envelope("x3", asdict(x3.DECLARED)),
        "cells_declared": len(x3.CELLS),
        "incomplete": [],
        "summary": {
            "readings": {
                k: sum(c["reading"] == k for c in cells)
                for k in (
                    "supports-objection",
                    "against-objection",
                    "inconclusive",
                    "error",
                    "gap",
                    "free-gap",
                )
            },
            "lost_crossing": [
                [c["cell"]["a"], c["cell"]["r"]] for c in cells if c["lost_crossing"]
            ],
            "margin": x3.MARGIN,
            "multiplicity": "none; per-cell readings only, no whole-curve claim",
        },
        "outer_rule": x3.OUTER_RULE,
        "cells": cells,
    }


def synthetic_x4() -> dict[str, Any]:
    loaded: dict[str, list[dict[str, Any]]] = {}
    flags: dict[str, dict[str, str | None]] = {}
    for name, declared in (("x4a", x4.CELLS), ("x4b", x4.SINGLE_CELLS)):
        rows = []
        flags[name] = {}
        for i, (unit, position) in enumerate(declared):
            flag = ("calibrated", "liberal", "conservative")[unit.block % 3]
            size_interval = {
                "calibrated": [0.03, 0.07],
                "liberal": [0.06, 0.10],
                "conservative": [0.01, 0.04],
            }[flag]
            interval = size_interval if position == 0 else [0.15, 0.23]
            normal = (0.19, 0.3, 0.1)[i % 3]
            statistics: dict[str, Any] = {
                "test_panels": 1000 if name == "x4a" else 200,
            }
            if name == "x4a":
                statistics.update(
                    auc_ref=0.7,
                    auc_ref_interval_95=[0.68, 0.72],
                    normal_theory_power={
                        "at_auc_ref": normal,
                        "at_interval_95": [0.16, 0.21],
                    },
                    critical_score=1.6,
                    critical_rule=x4.CRITICAL_RULE,
                    rejections=190,
                    power_or=0.19,
                    power_or_interval_95=interval,
                )
            else:
                difference = [[-0.12, -0.04], [-0.02, 0.02], [-0.08, 0.07]][i % 3]
                statistics.update(
                    p_value_rule=x4.P_VALUE_RULE,
                    single_index=x4.SINGLE_INDEX,
                    fit_statuses={"interior": 180, "budget": 20},
                    fit_failures=20,
                    failure_rate=0.1,
                    power_pu=0.15,
                    power_pu_interval_95=interval,
                    power_pu_without_failures=1 / 6,
                    power_or_paired=0.2,
                    power_or_paired_interval_95=[0.15, 0.25],
                    difference=-0.05,
                    difference_interval_95=difference,
                    panels=[],
                )
            row = {
                "cell": x3.cell_identity(i, unit, position),
                "success": True,
                "error": None,
                "attempts": ["interior"],
                name: statistics,
            }
            if position == 0:
                flags[name][str(unit.cells[position].reliability)] = flag
            if name == "x4a":
                row["normal_theory_reading"] = x4.normal_reading(normal, interval)
            else:
                row.update(
                    size_flag=flag,
                    quantity="power"
                    if flag == "calibrated"
                    else "power-lower-bound"
                    if flag == "conservative"
                    else "rejection-rate",
                    single_panel_reading=x4.single_panel_reading(difference)
                    if flag in {"calibrated", "conservative"}
                    else None,
                )
            rows.append(row)
        loaded[name] = rows
    return {
        **envelope("x4", asdict(x4.DECLARED)),
        "incomplete": {"x4a": [], "x4b": []},
        "summary": {
            "size_at_a0": flags,
            "normal_theory_in_auc_range": {"range": list(x4.AUC_RANGE)},
            "single_panel_effect": {"margin": x4.MARGIN},
        },
        "rules": {"critical": x4.CRITICAL_RULE, "p_value": x4.P_VALUE_RULE},
        **loaded,
    }


def coverage_row(success: bool = True) -> dict[str, Any]:
    return {
        "success": success,
        "point": 0.7,
        "se": 0.01,
        "pointwise": [0.68, 0.72],
        "band": [0.67, 0.73],
        "retry": False,
        "residual_se_units": [0.1, 0.2],
        "mean_shift": 0.001,
        "amplification": 1.0,
    }


def synthetic_x6(
    repetitions: int = 200, *, joint_covered: int | None = None
) -> dict[str, Any]:
    sizes = x6.X6Sizes(repetitions=repetitions, truth_pipelines=2)
    sections = {}
    for name in ("x6a", "x6b"):
        records = []
        for job in x6.queue(name, sizes):
            if job.kind == "pop":
                record = {
                    "trainings": [0.69, 0.71],
                    "success": True,
                    "error": None,
                    "fit": {},
                }
            elif job.kind == "truth":
                record = {"cells": [coverage_row()], "error": None}
            else:
                row = coverage_row()
                if job.number >= repetitions - 2:
                    row.pop("point")
                    row["success"] = False if job.number == repetitions - 2 else None
                rows = [copy.deepcopy(row) for _ in (GRID if name == "x6a" else (0,))]
                if name == "x6a" and "point" in rows[0]:
                    rows[0].update(point=0.5, pointwise=[0.49, 0.51], band=[0.48, 0.52])
                    if joint_covered is not None and job.number >= joint_covered:
                        rows[0].update(
                            point=0.8, pointwise=[0.79, 0.81], band=[0.78, 0.82]
                        )
                record = {
                    "cells": rows,
                    "error": "SYNTHETIC error" if row["success"] is None else None,
                    "success": row["success"],
                    "curve": None
                    if row["success"] is None
                    else {
                        "band_complete": row["success"],
                        "empirical_exceeds_floor": False,
                        "band_reproduced": True,
                    },
                }
            records.append({"job": job.describe(), **record})
        sections[name] = {
            "units": len(records),
            "recorded": len(records),
            "incomplete_units": [],
            "timing": {},
            **x6.summarize(name, records),
        }
    return {
        **envelope("x6", asdict(sizes)),
        "pointwise_critical": x6.POINTWISE_CRITICAL,
        "truth_se_target": x6.TRUTH_SE_TARGET,
        "minimum_complete_repetitions": x6.MINIMUM_COMPLETE,
        "verification_sha256": [],
        **sections,
    }


def synthetic_x7() -> dict[str, Any]:
    units = []
    cells = []
    for i, r in enumerate(RELIABILITIES):
        curve = {
            "status": "completo válido",
            "valid_null_gate": True,
            "gap_count": 0,
            "first": 0.03,
            "first_interval": [0.01, 0.1],
            "first_censoring": None,
            "first_interval_censoring": None,
            "sustained": 0.03,
            "sustained_interval": [0.01, 0.1],
            "sustained_censoring": None,
            "sustained_interval_censoring": None,
            "available_strengths": list(GRID),
            "auc": [0.5] * 9,
            "lower": [0.4] * 9,
            "upper": [0.6] * 9,
        }
        frozen, rich = copy.deepcopy(curve), copy.deepcopy(curve)
        delta = {
            a: {"delta": 0.0, "interval": [-0.01, 0.01], "auc_x7": 0.7, "auc_rich": 0.7}
            for a in GRID
        }
        kind = i % 6
        if kind == 0:
            rich["first"] = 0.003
            rich["first_interval"] = [0.001, 0.01]
        elif kind == 2:
            delta[0.03]["interval"] = [-0.1, 0.1]
        elif kind == 3:
            rich["first_censoring"] = "gap"
        elif kind == 4:
            rich["valid_null_gate"] = False
        errors = {"0.03": "SYNTHETIC error"} if kind == 5 else {}
        unit = {
            "r": r,
            "unit": f"x7-r{i}",
            "errors": errors,
            "rich_errors": {},
            "rich_gaps": {},
            "x7": None if errors else frozen,
            "rich": None if errors else rich,
            "delta_auc": [{"a": a, **v} for a, v in delta.items()]
            if not errors
            else [],
            "reading": x7.x7_reading(
                None if errors else frozen, None if errors else rich, delta
            ),
        }
        units.append(unit)
    for i in range(len(x7.x7_cells())):
        cells.append(
            {
                "cell": x7.cell_identity(i),
                "error": None,
                "rich_error": None,
                "success": True,
                "rich_success": True,
                "rich_gap": None,
                "attempts": ["interior"],
            }
        )
    return {
        **envelope("x7", asdict(x7.DECLARED_X7)),
        "compatibility": {},
        "estimands": {"x7": "frozen-feature LDA", "rich": "expanded-feature LDA"},
        "bootstrap": {"resamples": 1000, "paired": True, "margin": x7.MARGIN},
        "summary": [
            {k: u.get(k) for k in ("r", "unit", "status", "reading")} for u in units
        ],
        "incomplete": [],
        "verification_sha256": [],
        "successor": [],
        "units": units,
        "cells": cells,
    }


def synthetic_x1b() -> dict[str, Any]:
    curves = []
    template = synthetic_x7()["units"][0]["x7"]
    for index, r in enumerate(RELIABILITIES):
        curve = copy.deepcopy(template)
        curve.update(unit=f"x1b-r{index}", r=r)
        if index == 0:
            curve.update(
                first=0.03,
                first_interval=[0.01, None],
                first_interval_censoring="gap at a=0.6",
                sustained=0.1,
                sustained_interval=[0.03, None],
                sustained_interval_censoring="not reached",
            )
        elif index == 1:
            for kind in ("first", "sustained"):
                curve.update(
                    {
                        kind: None,
                        kind + "_interval": [None, None],
                        kind + "_censoring": "gap at a=0.6",
                        kind + "_interval_censoring": "gap at a=0.6",
                    }
                )
        elif index == 2:
            for kind in ("first", "sustained"):
                curve.update({kind: None, kind + "_interval": [None, None]})
        elif index == 3:
            curve["status"] = "completo inválido"
        curves.append(curve)
    return {
        "summary": [{"r": c["r"], "unit": c["unit"]} for c in curves],
        "curves": [c for c in curves if c["r"] != 0.75],
    }


def synthetic_inputs(directory: Path, *, with_x1b: bool = False) -> dict[str, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    aggregates = {
        "x3": synthetic_x3(),
        "x4": synthetic_x4(),
        "x6": synthetic_x6(),
        "x7": synthetic_x7(),
    }
    curves = {}
    for r in RELIABILITIES:
        first = {
            "state": "disponível",
            "reason": None,
            "point": 0.03,
            "interval": [0.01, 0.1],
            "censoring": None,
            "interval_censoring": None,
            "censored_at": None,
        }
        curves[r] = {
            "unit_status": "completo válido",
            "main_curve_valid": False,
            "first": first,
            "sustained": copy.deepcopy(first),
            "available_strengths": list(GRID),
            "auc": [0.5, 0.51, 0.52, 0.6, 0.72, 0.75, 0.8, 0.9, 0.95],
            "lower": [0.48] * 9,
            "upper": [0.97] * 9,
        }
    comparisons = compare_exploratory(
        curves,
        x1b=synthetic_x1b() if with_x1b else None,
        x3=aggregates["x3"],
        x4=aggregates["x4"],
    )
    comparisons["synthetic"] = True
    comparisons["provenance"] = {"synthetic": True}
    aggregates["comparisons"] = comparisons
    paths = {}
    for name, value in aggregates.items():
        path = directory / f"{name}.json"
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        paths[name] = path
    return paths


def refresh_selected_comparisons(paths: dict[str, Path]) -> None:
    comparison = json.loads(paths["comparisons"].read_bytes())
    expected = compare_exploratory(
        {row["r"]: row["main_curve"] for row in comparison["by_r"].values()},
        x3=json.loads(paths["x3"].read_bytes()),
        x4=json.loads(paths["x4"].read_bytes()),
    )
    for r, row in comparison["by_r"].items():
        for component in ("x3", "x4"):
            row[component] = expected["by_r"][r][component]
    paths["comparisons"].write_text(json.dumps(comparison))


def test_layout_preserves_the_pre_change_synthetic_values_catalog(
    tmp_path: Path,
    catalog_presentation_proof: Any,
) -> None:
    inputs = synthetic_inputs(tmp_path / "inputs")
    result = export(inputs, tmp_path / "manuscript")
    legacy_catalog = before_x7_fixture_correction(result.catalog)
    catalog_presentation_proof(
        legacy_catalog,
        "dfe82bb5a94deb6d73def63fffca5f17cd4263897c7e84f2dea80c98dc7d3334",
        wilson95=json.loads(inputs["x6"].read_text())["x6a"]["band"]["vs_d1"][
            "primary"
        ]["wilson95"],
    )


def before_x7_fixture_correction(catalog: dict[str, str]) -> dict[str, str]:
    projected = catalog.copy()
    for share in ("r050", "r080"):
        key = f"v4x.x7.units.{share}.rich.first"
        if key in projected:
            assert projected[key] == "0.003"
            projected[key] = "0.03"
    return projected


@pytest.mark.parametrize("with_x1b", [False, True])
def test_x1b_supplement_keeps_every_r_and_full_boundary_records(
    tmp_path: Path, with_x1b: bool
) -> None:
    inputs = synthetic_inputs(tmp_path / "inputs", with_x1b=with_x1b)
    result = export(inputs, tmp_path / "manuscript")
    tex = (tmp_path / "manuscript/generated/exploratory-x1b-boundaries.tex").read_text()
    rows = [
        line
        for line in tex.splitlines()
        if line.startswith(r"\raggedright \resultnum{v4x.comparisons.by_r.")
    ]
    assert len(rows) == len(RELIABILITIES)
    assert "Exploratory X1b" in tex
    assert "context only" in tex
    assert "without a between-curve test" in tex
    assert "SYNTHETIC REHEARSAL, NOT A RESULT" in tex
    projection = json.loads(inputs["comparisons"].read_text())["by_r"]
    for field, row in zip(projection, rows, strict=True):
        key = "v4x.comparisons.by_r." + field.replace(".", "-")
        for component in ("x1b", "main_curve"):
            view = projection[field][component]
            for kind in ("first", "sustained"):
                prefix = key + "." + component + "." + kind
                if kind not in view:
                    assert key + "." + component + ".state" in row
                    assert key + "." + component + ".reason" in row
                    continue
                for suffix in ("point", "state", "censoring", "interval_censoring"):
                    assert prefix + "." + suffix in row
                if view[kind]["interval"] is None:
                    assert prefix + ".interval" in row
                else:
                    assert prefix + ".interval.i000" in row
                    assert prefix + ".interval.i001" in row
                if view[kind]["reason"] is not None:
                    assert prefix + ".reason" in row
            if "unit_status" in view:
                assert key + "." + component + ".unit_status" in row
        assert key + ".main_curve.main_curve_valid" in row
    assert all(result.catalog[key] == value for key, value in RESULT.findall(tex))
    assert all(key in result.sources for key, _ in RESULT.findall(tex))
    assert not any(key.startswith("v4x.unavailable.") for key, _ in RESULT.findall(tex))


def test_x7_supplement_keeps_both_boundaries_intervals_and_censoring(
    tmp_path: Path,
) -> None:
    inputs = synthetic_inputs(tmp_path / "inputs")
    result = export(inputs, tmp_path / "manuscript")
    tex = (tmp_path / "manuscript/generated/exploratory-x7-boundaries.tex").read_text()
    for r in RELIABILITIES:
        prefix = f"v4x.x7.units.r{round(r * 100):03d}"
        assert tex.count(rf"\resultnum{{{prefix}.r}}") == 4
        for arm in ("x7", "rich"):
            for kind in ("first", "sustained"):
                key = prefix + "." + arm + "." + kind
                for field in ("", "_censoring", "_interval_censoring"):
                    ident = key + field
                    if ident not in result.catalog:
                        ident = "v4x.unavailable." + ident.removeprefix("v4x.")
                    assert rf"\resultnum{{{ident}}}" in tex
                if key + "_interval.i000" in result.catalog:
                    assert key + "_interval.i000" in tex
                    assert key + "_interval.i001" in tex
                else:
                    ident = key + "_interval"
                    if ident not in result.catalog:
                        ident = "v4x.unavailable." + ident.removeprefix("v4x.")
                    assert rf"\resultnum{{{ident}}}" in tex


def synthetic_catalog(
    directory: Path, scenario: str, with_x1b: bool
) -> tuple[dict[str, str], GateRecords | None]:
    catalog = {}
    gate = None
    if scenario.startswith("release"):
        plans = {
            key: UnitPlan(logistic_profile(0.02) if family == "B" else (0.5,) * 9)
            for family, tier in (("B", 1), ("A", 2), ("C", 2), ("D", 2), ("E", 2))
            for key in unit_keys(tier=tier, family=family).values()
        }
        with mock.patch("os.fsync", lambda _fd: None):
            release = parse_release(
                build_release(directory / "curves", plans, draws=40)
            )
        loaded = Loaded(release, None, None, None, None, None)
        _, cells = generated_files(loaded, lambda stem: stem + ".pdf", True)
        catalog.update(result_values(loaded) | cells)
    elif scenario.startswith("gate"):
        with mock.patch("os.fsync", lambda _fd: None):
            inputs = Inputs(
                None,
                build_gate(directory / "gate", GatePlan(stages=("G0",))),
                criteria=STUDY
                / "experiments/exploratory/detection-boundary-v4/criteria-v43.json",
            )
        loaded = load_inputs(inputs, synthetic=True)
        gate = loaded.gate
        _, cells = generated_files(loaded, lambda stem: stem + ".pdf", True)
        catalog.update(result_values(loaded) | cells)
    if "exploratory" in scenario:
        result = export(
            synthetic_inputs(directory / "inputs", with_x1b=with_x1b),
            directory / "manuscript",
        )
        assert not catalog.keys() & result.catalog.keys()
        catalog.update(result.catalog)
    return catalog, gate


# The release scenarios were renewed for amendment v4.4: the T4 gaps_propagation
# cells are their only additions.
@pytest.mark.parametrize(
    # T57f renewed the release digests: only the r lists changed
    # (publications/jcss-manuscript/pipeline/review/t57f-r-list-digest-proof.json).
    "scenario,with_x1b,expected",
    [
        (
            "release",
            False,
            "88cccbca8b5277a0773f152ccc23aa9c809d8cebcffc8449c24e9461c33721eb",
        ),
        (
            "gate",
            False,
            "265e6f0ca927c985d3e3ff6c7be081cca12f0f2ef7ad4348509fc3274f300842",
        ),
        (
            "exploratory",
            False,
            "dfe82bb5a94deb6d73def63fffca5f17cd4263897c7e84f2dea80c98dc7d3334",
        ),
        (
            "exploratory",
            True,
            "4d42a8f0c6603de226db23ee07d0d7e2eb910815637d82bbf9a88eaee2c33233",
        ),
        (
            "release+exploratory",
            False,
            "17f71c8eda6abed50814456166ae50a525394a5c9dc6e49114a179c9efd6065d",
        ),
        (
            "release+exploratory",
            True,
            "65ab9a0aecb499091ff40eb577f2a9f4e73ef00dd62a121c1eec0945b1994334",
        ),
        (
            "gate+exploratory",
            False,
            "953086e7bca477898bde9cbc064df84749ef2ae63f35efd61c2b1b3594c67531",
        ),
        (
            "gate+exploratory",
            True,
            "ec617a5fb3afe85921253d6ab92371eee92e06e434a196fc47ac40451b90cb25",
        ),
    ],
)
def test_x1b_presentation_preserves_pre_change_catalog_bytes(
    tmp_path: Path,
    scenario: str,
    with_x1b: bool,
    expected: str,
    catalog_presentation_proof: Any,
) -> None:
    catalog, gate = synthetic_catalog(tmp_path, scenario, with_x1b)
    wilson95 = (
        json.loads((tmp_path / "inputs/x6.json").read_text())["x6a"]["band"]["vs_d1"][
            "primary"
        ]["wilson95"]
        if "exploratory" in scenario
        else None
    )
    catalog_presentation_proof(
        before_x7_fixture_correction(catalog), expected, gate, wilson95=wilson95
    )


def test_empty_table_keeps_its_label_and_reports_unavailability() -> None:
    tex = _table("stress-comparisons", "Equivalent strength.", ("State",), [], True)
    assert "No rows are available." in tex
    assert "SYNTHETIC REHEARSAL" in tex
    assert r"\label{tab:v4x-stress-comparisons}" in tex
    assert r"\begin{tabular" not in tex
    assert r"\clearpage" not in tex
    assert not RESULT.findall(tex)


def test_table_continuations_preserve_every_bound_cell_and_allow_float_flow() -> None:
    rows = [
        [rf"\resultnum{{test.value{i}}}{{{i}}}", "supports-objection"]
        for i in range(100)
    ]
    tex = _table(
        "readings", "Cell readings.", ("Value", "Machine reading"), rows, False
    )
    parts = tex.count(r"\begin{table*}")
    assert 1 < parts < 7
    assert tex.count(r"\addtocounter{table}{-\csname @ne\endcsname}") == parts - 1
    assert tex.count(r"\renewcommand{\theHtable}") == parts - 1
    assert tex.count("(continued, part ") == parts - 1
    assert r"\clearpage" not in tex
    assert RESULT.findall(tex) == [(f"test.value{i}", str(i)) for i in range(100)]
    assert r"\small" in tex
    assert r"\footnotesize" not in tex
    assert r"\mbox{Machine} \mbox{reading}" in tex


def test_export_preserves_cell_readings_denominators_and_synthetic_mark(
    tmp_path: Path,
) -> None:
    inputs = synthetic_inputs(tmp_path / "inputs")
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    manuscript.joinpath("main.tex").write_text("")
    result = export(inputs, manuscript)
    assert result.synthetic
    assert result.catalog["v4x.x3.count.supports-objection"] == "12"
    assert result.catalog["v4x.x3.recorded"] == "72"
    assert result.catalog["v4x.x3.incomplete"] == "0"
    assert result.catalog["v4x.x6.x6a.band.vs_d1.primary.total"] == "198"
    assert result.catalog["v4x.x6.x6a.band.vs_d1.gaps_as_misses.total"] == "199"
    assert result.catalog["v4x.x6.x6a.without_curve"] == "1"
    assert result.catalog["v4x.x7.count.far"] == "2"
    assert all(key.startswith("v4x.") for key in result.catalog)
    assert all("SYNTHETIC" in path.read_text() for path in result.written)
    for path in result.written:
        assert all(
            result.catalog[m[0]] == m[1] for m in RESULT.findall(path.read_text())
        )


@pytest.mark.parametrize(
    "name,field", [("x3", "cells"), ("x4", "x4a"), ("x4", "x4b"), ("x7", "cells")]
)
def test_unaccounted_incomplete_inventory_is_refused(
    tmp_path: Path, name: str, field: str
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths[name].read_text())
    data[field].pop()
    paths[name].write_text(json.dumps(data))
    with pytest.raises(ValueError, match="denominator"):
        export(paths, tmp_path / "manuscript")
    assert not (tmp_path / "manuscript/generated").exists()


def test_reading_with_insufficient_complete_repetitions_is_refused(
    tmp_path: Path,
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = synthetic_x6(50)
    data["x6a"]["band"]["vs_d1"]["primary"]["reading"] = "adequate"
    paths["x6"].write_text(json.dumps(data))
    with pytest.raises(ValueError, match="minimum"):
        export(paths, tmp_path / "manuscript")


def test_explicit_cutoff_incomplete_cells_remain_outside_denominator(
    tmp_path: Path,
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["x3"].read_text())
    missing = data["cells"].pop()
    data["incomplete"] = [missing["cell"]["index"]]
    # An incomplete cell has no reading, rather than an extra gap/error.
    data["summary"]["readings"][missing["reading"]] -= 1
    paths["x3"].write_text(json.dumps(data))
    result = export(paths, tmp_path / "manuscript")
    assert result.catalog["v4x.x3.recorded"] == "71"
    assert result.catalog["v4x.x3.incomplete"] == "1"


def test_duplicate_cell_identity_is_refused(tmp_path: Path) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["x3"].read_text())
    data["cells"][-1]["cell"] = copy.deepcopy(data["cells"][0]["cell"])
    paths["x3"].write_text(json.dumps(data))
    with pytest.raises(ValueError, match="Duplicate"):
        export(paths, tmp_path / "manuscript")


@pytest.mark.parametrize(
    "reading,covered",
    [("adequate", 190), ("subnominal", 174), ("failure", 140), ("no reading", 30)],
)
def test_x6_machine_branches_are_preserved(
    tmp_path: Path, reading: str, covered: int
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = (
        synthetic_x6(50)
        if reading == "no reading"
        else synthetic_x6(joint_covered=covered)
    )
    assert data["x6a"]["band"]["vs_d1"]["primary"]["reading"] == reading
    paths["x6"].write_text(json.dumps(data))
    result = export(paths, tmp_path / "manuscript")
    assert result.catalog["v4x.x6.x6a.band.vs_d1.primary.reading"] == reading


def test_precision_and_conservative_flags_are_preserved(tmp_path: Path) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["x6"].read_text())
    reference = data["x6a"]["band"]["vs_d1"]["primary"]
    reference.update(
        reading="inconclusive-truth-precision",
        nominal_reading="adequate",
        truth_precision={
            "inconclusive": True,
            "minus_2se": "failure",
            "plus_2se": "adequate",
        },
    )
    paths["x6"].write_text(json.dumps(data))
    result = export(paths, tmp_path / "manuscript")
    assert (
        result.catalog["v4x.x6.x6a.band.vs_d1.primary.truth_precision.inconclusive"]
        == "true"
    )
    assert (
        result.catalog["v4x.x6.x6a.band.vs_d1.primary.reading"]
        == "inconclusive-truth-precision"
    )


def test_merge_rejects_even_equal_id_collisions_and_propagates_synthetic() -> None:
    from ic_study.analysis.v4_exploratory_export import merge_values

    confirmatory = {"synthetic": False, "values": {"v4.inv.n_valid": "3"}}
    exploratory = {"synthetic": True, "values": {"v4x.x3.recorded": "72"}}
    merged = merge_values(confirmatory, exploratory)
    assert merged["synthetic"] is True
    assert merged["values"] == {"v4.inv.n_valid": "3", "v4x.x3.recorded": "72"}
    with pytest.raises(ValueError, match="collision"):
        merge_values(confirmatory, confirmatory)


def test_cli_fills_shells_and_merged_values_pass_real_checker(tmp_path: Path) -> None:
    from ic_study.analysis.v4_exploratory_export import main

    inputs = synthetic_inputs(tmp_path / "inputs")
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    manuscript.joinpath("main.tex").write_text(r"\input{sections/results}" + "\n")
    sections = manuscript / "sections"
    sections.mkdir()
    sections.joinpath("results.tex").write_text(
        r"\resultnum{v4.inv.n_valid}{[n]}" + "\n" + SHELLS.read_text()
    )
    confirmatory = tmp_path / "confirmatory.json"
    confirmatory.write_text(
        json.dumps(
            {
                "synthetic": True,
                "values": {
                    "v4.inv.n_valid": "3",
                    "v4.protocol.target": protocol_values()["v4.protocol.target"],
                },
            }
        )
    )
    values, catalog = tmp_path / "values.json", tmp_path / "catalog.json"
    assert (
        main(
            [
                argument
                for name, path in inputs.items()
                for argument in (f"--{name}", str(path))
            ]
            + [
                "--manuscript",
                str(manuscript),
                "--values",
                str(values),
                "--catalog",
                str(catalog),
                "--confirmatory-values",
                str(confirmatory),
                "--fill",
            ]
        )
        == 0
    )
    spec = importlib.util.spec_from_file_location(
        "exploratory_paper_check", MANUSCRIPT / "pipeline/paper_check.py"
    )
    assert spec is not None and spec.loader is not None
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    assert (
        checker.result_consistency(
            manuscript, checker.tex_sources(manuscript), values, True
        )
        == []
    )
    record = json.loads(values.read_text())
    assert set(record["values"]) == used_ids(manuscript)
    assert record["synthetic"] is True
    assert record["sources"]
    assert "[n]" not in sections.joinpath("results.tex").read_text()


def test_cli_missing_id_returns_failure_without_filling(tmp_path: Path) -> None:
    from ic_study.analysis.v4_exploratory_export import main

    inputs = synthetic_inputs(tmp_path / "inputs")
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    manuscript.joinpath("main.tex").write_text(r"\resultnum{v4x.unknown}{[n]}")
    assert (
        main(
            [
                argument
                for name, path in inputs.items()
                for argument in (f"--{name}", str(path))
            ]
            + [
                "--manuscript",
                str(manuscript),
                "--values",
                str(tmp_path / "values.json"),
                "--fill",
            ]
        )
        == 1
    )
    assert "[n]" in manuscript.joinpath("main.tex").read_text()


def test_x7_cutoff_and_missing_x6_truth_remain_unavailable(tmp_path: Path) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["x7"].read_text())
    cell = data["cells"].pop()
    data["incomplete"] = [cell["cell"]["index"]]
    data["units"][-1] = {"r": 0.9, "unit": "x7-r8", "status": "incomplete"}
    paths["x7"].write_text(json.dumps(data))
    coverage = json.loads(paths["x6"].read_text())
    coverage["x6a"]["band"]["vs_d1"] = None
    paths["x6"].write_text(json.dumps(coverage))
    result = export(paths, tmp_path / "manuscript")
    assert result.catalog["v4x.x7.count.incomplete"] == "1"
    assert result.catalog["v4x.x6.x6a.band.vs_d1"] == "unavailable"
    assert "v4x.x6.x6a.band.vs_d1.primary.total" not in result.catalog


def test_x6b_unaccounted_jobs_are_refused(tmp_path: Path) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["x6"].read_text())
    data["x6b"]["recorded"] -= 1
    paths["x6"].write_text(json.dumps(data))
    with pytest.raises(ValueError, match="denominator"):
        export(paths, tmp_path / "manuscript")


def test_conservative_flag_and_single_input_synthetic_mark_propagate(
    tmp_path: Path,
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    for name in paths:
        data = (
            synthetic_x6(1000) if name == "x6" else json.loads(paths[name].read_text())
        )
        data["synthetic"] = name == "x6"
        paths[name].write_text(json.dumps(data))
    result = export(paths, tmp_path / "manuscript")
    assert result.synthetic
    assert result.catalog["v4x.x6.x6a.band.vs_d1.primary.conservative"] == "true"
    assert all("SYNTHETIC" in path.read_text() for path in result.written)


def test_stress_comparison_conditions_have_distinct_ids_and_all_states(
    tmp_path: Path,
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["comparisons"].read_text())
    row = data["by_r"]["0.5"]
    row["x5"] = [
        {
            "a": 0.0,
            "r": 0.5,
            "channel": {"name": f"stress-{i}"},
            "state": state,
            "reason": None if state == "disponível" else "SYNTHETIC missing",
            "equivalent_strength": {
                "state": state,
                "point": 0.03 if state == "disponível" else None,
                "censored_at": 0.001 if state == "censurada" else None,
            },
            "interval_comparison": {
                "state": "disponível" if i < 3 else "indisponível",
                "relation": ("sobrepõe", "acima", "abaixo")[i % 3] if i < 3 else None,
            },
        }
        for i, state in enumerate(
            ("disponível", "censurada", "acima da grade", "indisponível")
        )
    ]
    paths["comparisons"].write_text(json.dumps(data))
    result = export(paths, tmp_path / "manuscript")
    prefix = "v4x.comparisons.by_r.0-5.x5.r050.a0000."
    assert result.catalog[prefix + "stress-0.equivalent_strength.point"] == "0.03"
    assert result.catalog[prefix + "stress-1.equivalent_strength.state"] == "censurada"
    assert (
        result.catalog[prefix + "stress-2.equivalent_strength.state"]
        == "acima da grade"
    )
    assert (
        result.catalog[prefix + "stress-3.equivalent_strength.state"] == "indisponível"
    )


@pytest.mark.parametrize("kind", ["error", "gap"])
def test_x4_missing_statistics_never_become_zero_power(
    tmp_path: Path, kind: str
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["x4"].read_text())
    row = data["x4b"][1]
    row.update(
        success=None if kind == "error" else False,
        error="SYNTHETIC error" if kind == "error" else None,
        x4b=None,
        single_panel_reading=None,
    )
    paths["x4"].write_text(json.dumps(data))
    result = export(paths, tmp_path / "manuscript")
    assert result.catalog["v4x.x4.x4b.r050.a0010.x4b"] == "unavailable"
    assert "v4x.x4.x4b.r050.a0010.x4b.power_pu" not in result.catalog
    assert (
        result.catalog["v4x.unavailable.x4.x4b.r050.a0010.x4b.power_pu"]
        == "unavailable"
    )
    tex = (tmp_path / "manuscript/generated/exploratory-x4-failures.tex").read_text()
    line = next(line for line in tex.splitlines() if "r050.a0010" in line)
    failed = line.split(" & ")[1]
    assert failed.endswith("{unavailable}")
    assert "/" not in failed


def test_comparison_provenance_cannot_bind_other_aggregate_bytes(
    tmp_path: Path,
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["comparisons"].read_text())
    data["provenance"] = {"inputs": {"x3": {"sha256": "0" * 64}}}
    paths["comparisons"].write_text(json.dumps(data))
    with pytest.raises(ValueError, match="provenance"):
        export(paths, tmp_path / "manuscript")


@pytest.mark.parametrize(
    "component,field,value",
    [
        ("x3", ("delta", "point"), 0.123),
        ("x3", ("delta", "interval_95"), [-0.9, -0.8]),
        ("x3", ("reading",), "supports-objection"),
        ("x3", ("cell", "a"), 0.1),
        ("x4", ("P_or", "statistics", "power_or"), 0.123),
        ("x4", ("P_pu", "statistics", "power_pu"), 0.123),
        ("x4", ("calibration", "x4a", "flag"), "liberal"),
    ],
)
def test_export_refuses_divergent_projection_with_correct_input_hashes(
    tmp_path: Path, component: str, field: tuple[str, ...], value: Any
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    comparison = json.loads(paths["comparisons"].read_bytes())
    r = "0.7" if "P_pu" in field else "0.6"
    selected = comparison["by_r"][r][component]
    for key in field[:-1]:
        selected = selected[key]
    assert selected[field[-1]] != value
    selected[field[-1]] = value
    comparison["provenance"]["inputs"] = {
        name: {"sha256": hashlib.sha256(paths[name].read_bytes()).hexdigest()}
        for name in ("x3", "x4")
    }
    paths["comparisons"].write_text(json.dumps(comparison))
    with pytest.raises(ValueError, match="projection"):
        export(paths, tmp_path / "manuscript")
    assert not (tmp_path / "manuscript").exists()


@pytest.mark.parametrize("missing", ["x3", "x4"])
def test_production_export_requires_each_comparison_input_binding(
    tmp_path: Path, missing: str
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    for path in paths.values():
        data = json.loads(path.read_bytes())
        data.pop("synthetic")
        path.write_text(json.dumps(data))
    comparison = json.loads(paths["comparisons"].read_bytes())
    comparison["provenance"]["inputs"] = {
        name: {"sha256": hashlib.sha256(paths[name].read_bytes()).hexdigest()}
        for name in ("x3", "x4")
        if name != missing
    }
    paths["comparisons"].write_text(json.dumps(comparison))
    with pytest.raises(ValueError, match="provenance"):
        export(paths, tmp_path / "manuscript")
    assert not (tmp_path / "manuscript").exists()


def test_bound_production_projection_exports_unchanged_values(tmp_path: Path) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    rehearsal = export(paths, tmp_path / "rehearsal")
    for path in paths.values():
        data = json.loads(path.read_bytes())
        data.pop("synthetic")
        path.write_text(json.dumps(data))
    comparison = json.loads(paths["comparisons"].read_bytes())
    comparison["provenance"] = {
        "inputs": {
            name: {"sha256": hashlib.sha256(paths[name].read_bytes()).hexdigest()}
            for name in ("x3", "x4")
        }
    }
    paths["comparisons"].write_text(json.dumps(comparison))
    result = export(paths, tmp_path / "manuscript")
    assert not result.synthetic
    assert {
        k: v for k, v in rehearsal.catalog.items() if not k.endswith(".synthetic")
    } == result.catalog
    assert result.catalog["v4x.comparisons.by_r.0-6.x3.delta.point"] == "-0.04"


@pytest.mark.parametrize("point", [None, 0.0, 0.03])
def test_projection_validation_preserves_unavailability_and_declared_domains(
    tmp_path: Path, point: float | None
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    comparison = json.loads(paths["comparisons"].read_bytes())
    first = comparison["by_r"]["0.6"]["main_curve"]["first"]
    first.update(
        point=point,
        state="indisponível" if point is None else "disponível",
        reason="SYNTHETIC unavailable boundary" if point is None else None,
    )
    if point == 0.0:
        first["interval"] = [0.0, 0.0]
    paths["comparisons"].write_text(json.dumps(comparison))
    refresh_selected_comparisons(paths)
    before = {name: path.read_bytes() for name, path in paths.items()}
    result = export(paths, tmp_path / "manuscript")
    prefix = "v4x.comparisons.by_r.0-6."
    assert result.catalog[prefix + "x3.state"] == (
        "indisponível"
        if point is None
        else "fora do domínio declarado"
        if point == 0
        else "disponível"
    )
    assert result.catalog[prefix + "x4.P_pu.state"] == "fora do domínio declarado"
    assert result.catalog[prefix + "x4.P_or.state"] == (
        "indisponível" if point is None else "disponível"
    )
    assert {name: path.read_bytes() for name, path in paths.items()} == before


def test_normal_reference_counts_use_only_declared_auc_range(tmp_path: Path) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["x4"].read_text())
    for row in data["x4a"]:
        row["x4a"]["auc_ref"] = 0.5
    paths["x4"].write_text(json.dumps(data))
    refresh_selected_comparisons(paths)
    result = export(paths, tmp_path / "manuscript")
    for reading in ("describes", "overstates", "understates"):
        assert result.catalog[f"v4x.x4a.count.{reading}"] == "0"


def test_text_fields_keep_tex_control_words_separate_from_following_text(
    tmp_path: Path,
) -> None:
    paths = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(paths["comparisons"].read_text())
    data["by_r"]["0.5"]["x3"]["reason"] = r"SYNTHETIC {fit}\path<a>"
    paths["comparisons"].write_text(json.dumps(data))
    result = export(paths, tmp_path / "manuscript")
    key = "v4x.comparisons.by_r.0-5.x3.reason"
    displayed = result.catalog[key]
    assert r"\textbraceleft fit" in displayed
    assert r"\textbackslash path" in displayed
    assert r"\textless a" in displayed
    table = next(p for p in result.written if p.stem.endswith("comparison-states"))
    assert (key, displayed) in RESULT.findall(table.read_text())


def test_boundary_notes_define_missing_fields_and_gloss_original_labels(
    tmp_path: Path,
) -> None:
    result = export(
        synthetic_inputs(tmp_path / "inputs", with_x1b=True), tmp_path / "manuscript"
    )
    generated = tmp_path / "manuscript/generated"
    twin = (generated / "exploratory-x1b-boundaries.tex").read_text()
    assert "C or IC unavailable means no gap censoring" in twin
    assert "complete valid unit" in twin
    assert "não atingida na grade = not reached on the grid" in twin
    x7 = (generated / "exploratory-x7-boundaries.tex").read_text()
    assert "x7: frozen-feature LDA; rich: expanded-feature LDA" in x7
    for name in (
        "exploratory-comparisons",
        "exploratory-comparison-states",
        "exploratory-stress-comparisons",
    ):
        assert "disponível = available" in (generated / (name + ".tex")).read_text()
    states = (generated / "exploratory-comparison-states.tex").read_text()
    for line in states.splitlines():
        if ".state}{disponível}" in line:
            assert ".reason}" not in line
    prefix = "v4x.x6.x6a.band.vs_d1.primary.wilson95."
    for index, label in enumerate(("lower", "upper")):
        assert (
            result.catalog[prefix + "prose_" + label]
            == f"{float(result.catalog[prefix + f'i{index:03d}']):.3f}"
        )
    for key in (
        "x3.sizes.matching",
        "x3.sizes.retry_matching",
        "x4.sizes.check",
        "x6.x6a.recorded",
        "x6.x6a.units",
        "x6.sizes.population_pairs",
    ):
        ident = "v4x." + key
        assert result.catalog[ident + "_prose"] == f"{int(result.catalog[ident]):,}"


@pytest.mark.parametrize(
    "interval,expected,original",
    [
        ([0.939677, 0.99059], ("0.940", "0.991"), ("0.939677", "0.99059")),
        ([0.8, 0.9496], ("0.800", "0.9496"), ("0.8", "0.9496")),
        ([0.8, 0.9504], ("0.800", "0.9504"), ("0.8", "0.9504")),
        ([0.8, 0.8996], ("0.800", "0.8996"), ("0.8", "0.8996")),
        ([0.8, 0.9004], ("0.800", "0.9004"), ("0.8", "0.9004")),
        ([0.8, 0.94996], ("0.800", "0.94996"), ("0.8", "0.94996")),
        ([0.9900004, 0.999999], ("0.9900004", "1.000"), ("0.99", "0.999999")),
        ([0.99, 0.999999], ("0.990", "1.000"), ("0.99", "0.999999")),
    ],
)
def test_primary_wilson_prose_uses_the_minimum_precision_to_distinguish_cutoffs(
    tmp_path: Path,
    interval: list[float],
    expected: tuple[str, str],
    original: tuple[str, str],
) -> None:
    inputs = synthetic_inputs(tmp_path / "inputs")
    data = json.loads(inputs["x6"].read_text())
    data["x6a"]["band"]["vs_d1"]["primary"]["wilson95"] = interval
    inputs["x6"].write_text(json.dumps(data))
    result = export(inputs, tmp_path / "manuscript")
    key = "v4x.x6.x6a.band.vs_d1.primary.wilson95."
    assert result.catalog[key + "prose_lower"] == expected[0]
    assert result.catalog[key + "prose_upper"] == expected[1]
    assert result.catalog[key + "i000"] == original[0]
    assert result.catalog[key + "i001"] == original[1]


@pytest.mark.parametrize(
    "interval,prose,accepted",
    [
        ([0.939677, 0.99059], ("0.940", "0.991"), True),
        ([0.8, 0.9496], ("0.800", "0.9496"), True),
        ([0.8, 0.9504], ("0.800", "0.9504"), True),
        ([0.8, 0.8996], ("0.800", "0.8996"), True),
        ([0.8, 0.9004], ("0.800", "0.9004"), True),
        ([0.8, 0.94996], ("0.800", "0.94996"), True),
        ([0.9900004, 0.999999], ("0.9900004", "1.000"), True),
        ([0.99, 0.999999], ("0.990", "1.000"), True),
        ([0.8, 0.9496], ("0.800", "0.950"), False),
        ([0.8, 0.9496], ("0.800", "0.94960"), False),
        ([0.939677, 0.99059], ("0.9397", "0.991"), False),
        ([0.99, 0.999999], ("0.9900", "1.000"), False),
    ],
)
def test_catalog_proof_requires_threshold_aware_minimum_wilson_precision(
    interval: list[float],
    prose: tuple[str, str],
    accepted: bool,
    catalog_presentation_proof: Any,
) -> None:
    prefix = "v4x.x6.x6a.band.vs_d1.primary.wilson95."
    baseline = {
        prefix + "i000": f"{interval[0]:.6g}",
        prefix + "i001": f"{interval[1]:.6g}",
        "v4x.protocol.x6.conservative": "0.99",
        "v4x.protocol.x6.nominal": "0.95",
        "v4x.protocol.x6.failure": "0.90",
    }
    previous = hashlib.sha256(
        (
            json.dumps(baseline, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
        ).encode()
    ).hexdigest()
    catalog = baseline | {
        prefix + "prose_lower": prose[0],
        prefix + "prose_upper": prose[1],
    }
    if accepted:
        catalog_presentation_proof(catalog, previous, wilson95=interval)
    else:
        with pytest.raises(AssertionError):
            catalog_presentation_proof(catalog, previous, wilson95=interval)


def test_comparison_availability_retains_partial_and_outside_domain_reasons(
    tmp_path: Path,
) -> None:
    result = export(synthetic_inputs(tmp_path / "inputs"), tmp_path / "manuscript")
    table = (
        tmp_path / "manuscript/generated/exploratory-comparison-states.tex"
    ).read_text()
    rows = [line for line in table.splitlines() if ".state}{parcial}" in line]
    assert rows
    for key, state in result.catalog.items():
        if (
            key.startswith("v4x.comparisons.by_r.")
            and key.rsplit(".", 2)[-2] in {"main_curve", "x1b", "x3", "x4"}
            and key.endswith(".state")
            and state in {"parcial", "fora do domínio declarado"}
        ):
            reason_key = key.removesuffix(".state") + ".reason"
            if reason_key in result.catalog:
                row = next(line for line in table.splitlines() if key + "}" in line)
                assert reason_key + "}" in row
    assert "Reasons appear on every row that is not available." in table
