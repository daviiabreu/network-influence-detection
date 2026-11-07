"""Post-release readings on synthetic curves; no experiment stores are opened."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import Uncertainty, band, curve_report
from ic_study.analysis.v4_exploratory_comparisons import (
    compare_exploratory,
    main,
    main_curves,
)
from ic_study.analysis.v4_report_schema import (
    INVALID,
    NOT_STARTED,
    PARTIAL,
    VALID,
    parse_release,
    unit_catalog,
)
from ic_study.analysis.v4_report_synthetic import write_release
from ic_study.simulation.detection_v4 import GRID
from ic_study.simulation.v4_plan import CLOSE_UTC

PROFILE = (0.5, 0.52, 0.54, 0.60, 0.72, 0.66, 0.76, 0.78, 0.80)
B = {
    m.r: m.key
    for m in unit_catalog().values()
    if m.tier == 1 and m.family == "B" and m.channel == "observed"
}


def synthetic_curve(
    unit: str,
    profile: tuple[float, ...] = PROFILE,
    gaps: frozenset[int] = frozenset(),
) -> dict[str, Any]:
    success = np.array([i not in gaps for i in range(len(GRID))])
    point = np.array(profile)[success]
    se = np.full(len(point), 0.005)
    uncertainty = Uncertainty(point, se, se, np.tile(point, (3, 1)))
    interval = band(uncertainty)
    record = curve_report(np.array(GRID), uncertainty, success)
    record.update(
        unit=unit,
        cells=[
            {
                "success": bool(ok),
                "attempts": [
                    {"status": "interior" if ok else "no-L1-root", "evaluations": 18}
                ],
            }
            for ok in success
        ],
        band_complete=bool(success.all()),
        available_strengths=[a for a, ok in zip(GRID, success, strict=True) if ok],
        auc=point.tolist(),
        lower=interval.lower.tolist(),
        upper=interval.upper.tolist(),
        status=VALID if record["valid_null_gate"] else INVALID,
        main_curve_valid=False,
    )
    for name in ("first_interval", "sustained_interval"):
        value = record[name]
        if isinstance(value, tuple):
            record[name] = list(value)
    return record


def synthetic_release(
    curve: dict[str, Any] | None = None, *, status: str = NOT_STARTED
) -> dict[str, Any]:
    return {
        "inventory": {
            "closed_utc": CLOSE_UTC,
            "main_curve_valid": False,
            "units": [
                {
                    "unit": m.key,
                    "tier": m.tier,
                    "status": (curve["status"] if curve is not None else status)
                    if m.key == B[0.5]
                    else NOT_STARTED,
                }
                for m in unit_catalog().values()
            ],
        },
        "curves": [] if curve is None else [curve],
    }


def primary(
    profile: tuple[float, ...] = PROFILE,
    gaps: frozenset[int] = frozenset(),
) -> dict[float, dict[str, Any]]:
    return main_curves(
        parse_release(synthetic_release(synthetic_curve(B[0.5], profile, gaps)))
    )


def x5_input(
    auc: float = 0.70, interval: tuple[float, float] = (0.68, 0.75)
) -> dict[str, Any]:
    channel = {
        "name": "trend-003",
        "trend": 0.03,
        "step": 0,
        "tenure": 0,
        "attrition": 0,
    }
    return {
        "schema": "ic-study.v4-exploratory-x5.v1",
        "conditions": [channel],
        "cells": [
            {
                "a": 0.0,
                "r": 0.5,
                "channel": channel,
                "success": True,
                "attempts": ["interior"],
                "reading": "intermediate",
                "estimate": {
                    "auc": auc,
                    "interval_95": [0.01, 0.02],
                    "interval_27729": list(interval),
                },
            }
        ],
    }


def x1b_input(curve: dict[str, Any] | None = None) -> dict[str, Any]:
    twin = copy.deepcopy(curve or synthetic_curve("x1b-r050", PROFILE, frozenset({3})))
    twin["unit"] = "x1b-r050"
    twin.pop("main_curve_valid", None)
    return {
        "schema": "ic-study.v4-exploratory-x1b.v1",
        "summary": [{"unit": twin["unit"], "r": 0.5, "status": twin["status"]}],
        "curves": [twin],
    }


def x3_input() -> dict[str, Any]:
    cells = []
    for strength, delta, reading in (
        (0.03, -0.04, "supports-objection"),
        (0.3, 0.01, "against-objection"),
    ):
        cells.append(
            {
                "cell": {"a": strength, "r": 0.5},
                "error": None,
                "gap": None,
                "success": True,
                "attempts": ["interior"],
                "known": {"auc": 0.74},
                "free": {"auc": 0.70, "attempts": [{"status": "interior"}]},
                "delta": {"point": delta, "interval_95": [-0.06, -0.02]},
                "reading": reading,
                "lost_crossing": False,
            }
        )
    return {"schema": "ic-study.v4-exploratory-x3.v1", "cells": cells}


def x4_input(flag: str = "calibrated", quantity: str = "power") -> dict[str, Any]:
    return {
        "schema": "ic-study.v4-exploratory-x4.v1",
        "sizes": {"train": 2000, "check": 4000, "test": 1000, "single": 200},
        "rules": {
            "critical": "empirical null quantile",
            "p_value": "failed fits count as non-rejections",
        },
        "summary": {"size_at_a0": {"x4a": {"0.5": flag}, "x4b": {"0.5": flag}}},
        "x4a": [
            {
                "cell": {"a": a, "r": 0.5},
                "error": None,
                "success": True,
                "attempts": ["interior"],
                "x4a": {
                    "power_or": power,
                    "power_or_interval_95": [power - 0.01, power + 0.01],
                    "test_panels": 1000,
                    "rejections": round(power * 1000),
                },
                "normal_theory_reading": "describes",
            }
            for a, power in ((0.0, 0.05), (0.03, 0.19), (0.3, 0.31))
        ],
        "x4b": [
            {
                "cell": {"a": a, "r": 0.5},
                "error": None,
                "success": True,
                "attempts": ["interior"],
                "x4b": {
                    "power_pu": power,
                    "power_pu_interval_95": [power - 0.02, power + 0.02],
                    "power_pu_without_failures": power + 0.01,
                    "test_panels": 200,
                    "fit_failures": 2,
                    "failure_rate": 0.01,
                    "difference": -0.03,
                    "difference_interval_95": [-0.06, 0.0],
                    "panels": [],
                },
                "size_flag": flag,
                "quantity": quantity,
                "single_panel_reading": "inconclusive",
            }
            for a, power in ((0.0, 0.05), (0.03, 0.16), (0.3, 0.28))
        ],
    }


def row(curves: dict[float, dict[str, Any]], **inputs: Any) -> dict[str, Any]:
    return cast(dict[str, Any], compare_exploratory(curves, **inputs)["by_r"]["0.5"])


def test_selects_confirmatory_b_observed_and_keeps_first_and_sustained() -> None:
    data = synthetic_release(synthetic_curve(B[0.5]))
    other = next(m for m in unit_catalog().values() if m.tier == 2 and m.r == 0.5)
    extra = synthetic_curve(other.key, (0.5, *([0.9] * 8)))
    extra.pop("main_curve_valid")
    data["curves"].append(extra)
    next(u for u in data["inventory"]["units"] if u["unit"] == other.key)["status"] = (
        VALID
    )
    curves = main_curves(parse_release(data))
    selected = row(curves)["main_curve"]
    assert len(curves) == 9
    assert selected["unit"] == B[0.5]
    assert selected["first"]["point"] == 0.03
    assert selected["sustained"]["point"] == 0.3
    assert selected["first"]["interval"] == [0.03, 0.03]
    assert selected["unit_status"] == VALID
    assert selected["main_curve_valid"] is False


@pytest.mark.parametrize(
    ("auc", "gaps", "state", "point", "censored_at"),
    [
        (0.70, frozenset(), "disponível", 0.03, None),
        (0.72, frozenset(), "disponível", 0.03, None),
        (0.49, frozenset(), "disponível", 0.0, None),
        (0.81, frozenset(), "acima da grade", None, None),
        (0.70, frozenset({3}), "censurada", None, 0.01),
        (0.81, frozenset({3}), "censurada", None, 0.01),
        (0.70, frozenset({7}), "disponível", 0.03, None),
    ],
)
def test_equivalent_strength_obeys_order_and_gap_censoring(
    auc: float,
    gaps: frozenset[int],
    state: str,
    point: float | None,
    censored_at: float | None,
) -> None:
    reading = row(primary(gaps=gaps), x5=x5_input(auc))["x5"][0]["equivalent_strength"]
    assert reading["state"] == state
    assert reading["point"] == point
    assert reading["censored_at"] == censored_at
    if censored_at is not None:
        assert reading["reason"] == "censurada por lacuna em a = 0.01"


@pytest.mark.parametrize(
    ("interval", "relation"),
    [((0.68, 0.75), "sobrepõe"), ((0.80, 0.85), "acima"), ((0.55, 0.60), "abaixo")],
)
def test_x5_uses_27729_interval_and_band_at_first_boundary(
    interval: tuple[float, float], relation: str
) -> None:
    comparison = row(primary(), x5=x5_input(interval=interval))["x5"][0][
        "interval_comparison"
    ]
    assert comparison["state"] == "disponível"
    assert comparison["relation"] == relation
    assert comparison["x5_interval_27729"] == list(interval)
    assert comparison["a"] == 0.03


def test_touching_interval_endpoints_overlap() -> None:
    curves = primary()
    endpoint = curves[0.5]["upper"][4]
    comparison = row(curves, x5=x5_input(interval=(endpoint, 0.85)))["x5"][0][
        "interval_comparison"
    ]
    assert comparison["relation"] == "sobrepõe"


@pytest.mark.parametrize(
    "cause", ["invalid", "not-attained", "censored", "not-started", "partial"]
)
def test_absent_a_star_disables_every_cell_reading_with_a_reason(cause: str) -> None:
    if cause == "invalid":
        curves = primary((0.58, *PROFILE[1:]))
        expected = INVALID
    elif cause == "not-attained":
        curves = primary((0.5, *([0.6] * 8)))
        expected = "não atingida"
    elif cause == "censored":
        curves = primary(gaps=frozenset({3}))
        expected = "censurada por lacuna em a = 0.01"
    else:
        expected = PARTIAL if cause == "partial" else NOT_STARTED
        curves = main_curves(parse_release(synthetic_release(status=expected)))
    result = row(
        curves,
        x5=x5_input(0.55 if cause == "not-attained" else 0.70),
        x3=x3_input(),
        x4=x4_input(),
    )
    assert result["main_curve"]["first"]["state"] == "indisponível"
    for item in (
        result["x5"][0]["interval_comparison"],
        result["x3"],
        result["x4"]["P_or"],
        result["x4"]["P_pu"],
    ):
        assert item["state"] == "indisponível"
        assert expected in item["reason"]
    if cause == "invalid":
        assert result["x5"][0]["equivalent_strength"]["state"] == "indisponível"
    if cause == "not-attained":
        assert result["x5"][0]["equivalent_strength"]["point"] == 0.001


def test_x1b_side_by_side_preserves_intervals_status_and_all_censoring() -> None:
    result = row(primary(), x1b=x1b_input())
    twin = result["x1b"]
    assert twin["label"] == "exploratory"
    assert twin["unit_status"] == VALID
    assert twin["first"]["state"] == "indisponível"
    assert twin["first"]["censoring"] == "gap at a=0.01"
    assert twin["first"]["interval_censoring"] == "gap at a=0.01"
    assert twin["sustained"]["point"] == 0.3
    assert result["main_curve"]["first"]["point"] == 0.03
    assert "p_value" not in twin


@pytest.mark.parametrize("invalid", [False, True])
def test_x1b_attained_or_invalid_keeps_own_state(invalid: bool) -> None:
    curve = synthetic_curve("x1b-r050", (0.58, *PROFILE[1:]) if invalid else PROFILE)
    twin = row(primary(), x1b=x1b_input(curve))["x1b"]
    assert twin["unit_status"] == (INVALID if invalid else VALID)
    assert twin["first"]["state"] == ("indisponível" if invalid else "disponível")
    assert twin["first"]["interval"] == curve["first_interval"]


def test_x3_and_x4_use_first_boundary_and_retain_aggregate_readings() -> None:
    result = row(primary(), x3=x3_input(), x4=x4_input())
    assert result["x3"]["a"] == 0.03
    assert result["x3"]["reading"] == "supports-objection"
    assert result["x3"]["delta"] == {"point": -0.04, "interval_95": [-0.06, -0.02]}
    x4 = result["x4"]
    assert x4["P_or"]["statistics"]["power_or"] == 0.19
    assert x4["P_pu"]["statistics"]["power_pu"] == 0.16
    assert x4["P_pu"]["statistics"]["fit_failures"] == 2
    assert x4["P_pu"]["statistics"]["power_pu_without_failures"] == 0.17
    assert x4["calibration"]["x4b"]["flag"] == "calibrated"
    assert x4["calibration"]["x4b"]["statistics"]["test_panels"] == 200
    assert x4["P_or"]["quantity"] is None
    assert x4["P_or"]["quantity_reason"]


@pytest.mark.parametrize(
    ("flag", "quantity"),
    [
        ("calibrated", "power"),
        ("conservative", "power-lower-bound"),
        ("liberal", "rejection-rate"),
    ],
)
def test_x4_preserves_quantity_and_calibration_without_reclassifying(
    flag: str, quantity: str
) -> None:
    x4 = row(primary(), x4=x4_input(flag, quantity))["x4"]
    assert x4["P_pu"]["quantity"] == quantity
    assert x4["P_pu"]["size_flag"] == flag
    assert x4["calibration"]["x4a"]["flag"] == flag


@pytest.mark.parametrize("reading", ["error", "gap", "free-gap"])
def test_x3_gaps_preserve_fit_evidence_and_do_not_become_auc(reading: str) -> None:
    x3 = x3_input()
    cell = x3["cells"][0]
    cell.update(reading=reading, delta=None, success=False)
    cell["free"]["attempts"] = [{"status": "budget"}, {"status": "validation"}]
    selected = row(primary(), x3=x3)["x3"]
    assert selected["state"] == "indisponível"
    assert reading in selected["reason"]
    assert selected["reading"] == reading
    assert selected["free"]["attempts"] == cell["free"]["attempts"]


def test_x4b_absence_keeps_oracle_reference_available() -> None:
    x4 = x4_input()
    x4["x4b"] = []
    result = row(primary(), x4=x4)["x4"]
    assert result["P_or"]["state"] == "disponível"
    assert result["P_pu"]["state"] == "indisponível"
    assert result["P_pu"]["reason"]


@pytest.mark.parametrize("aggregate", [False, True])
def test_x3_zero_is_outside_declared_domain_even_without_aggregate(
    aggregate: bool,
) -> None:
    curves = primary()
    curves[0.5]["first"]["point"] = 0.0
    result = row(curves, x3=x3_input() if aggregate else None)["x3"]
    assert result["state"] == "fora do domínio declarado"
    assert result["a"] == 0.0
    assert result["reading"] is None
    assert result["delta"] is None


@pytest.mark.parametrize("r", [0.55, 0.6, 0.65, 0.75, 0.8, 0.85])
@pytest.mark.parametrize("aggregate", [False, True])
def test_x4b_outside_r_domain_is_distinct_from_missing_cell(
    r: float,
    aggregate: bool,
) -> None:
    curve = primary()[0.5]
    x4 = x4_input() if aggregate else None
    if x4 is not None:
        for cell in x4["x4a"]:
            cell["cell"]["r"] = r
    result = compare_exploratory({r: curve}, x4=x4)["by_r"][str(r)]["x4"]
    assert result["P_pu"]["state"] == "fora do domínio declarado"
    assert result["P_pu"]["statistics"] is None
    assert result["calibration"]["x4b"]["state"] == "fora do domínio declarado"


@pytest.mark.parametrize("failure", ["fit-failure", "error", "missing"])
def test_x5_missing_estimate_never_produces_comparisons(failure: str) -> None:
    x5 = x5_input()
    if failure == "missing":
        x5["cells"] = []
    else:
        x5["cells"][0].update(success=False, estimate=None, reading=failure)
    reading = row(primary(), x5=x5)["x5"][0]
    for name in ("equivalent_strength", "interval_comparison"):
        assert reading[name]["state"] == "indisponível"
        assert reading[name]["reason"]


def test_optional_x3_x4_do_not_block_x1b_and_x5_and_inputs_remain_unchanged() -> None:
    curves, x1b, x5 = primary(), x1b_input(), x5_input()
    original = copy.deepcopy((curves, x1b, x5))
    result = row(curves, x1b=x1b, x5=x5)
    assert result["x3"]["state"] == "indisponível"
    assert result["x4"]["P_or"]["state"] == "indisponível"
    assert result["x4"]["P_pu"]["state"] == "indisponível"
    assert result["x1b"]["sustained"]["state"] == "disponível"
    assert result["x5"][0]["equivalent_strength"]["point"] == 0.03
    assert (curves, x1b, x5) == original


def test_each_curve_and_x4_item_has_an_availability_state() -> None:
    selected = row(primary(), x4=x4_input())
    assert selected["main_curve"]["state"] == "disponível"
    assert selected["x4"]["state"] == "disponível"
    assert selected["main_curve"]["reason"] is None
    absent = row(primary())
    assert absent["x4"]["state"] == "indisponível"
    assert absent["x4"]["reason"]
    x4 = x4_input()
    x4["x4b"] = []
    assert row(primary(), x4=x4)["x4"]["state"] == "parcial"


def write_inputs(tmp_path: Path) -> tuple[list[str], dict[str, Path]]:
    paths = {
        name: tmp_path / f"{name}.json" for name in ("curves", "x1b", "x5", "x3", "x4")
    }
    write_release(paths["curves"], synthetic_release(synthetic_curve(B[0.5])))
    for name, value in (
        ("x1b", x1b_input()),
        ("x5", x5_input()),
        ("x3", x3_input()),
        ("x4", x4_input()),
    ):
        paths[name].write_text(json.dumps(value), encoding="utf-8")
    paths["release_record"] = tmp_path / "release-record.json"
    args = [
        argument
        for name, path in paths.items()
        for argument in (f"--{name.replace('_', '-')}", str(path))
    ]
    return args, paths


@pytest.mark.parametrize("failure", ["missing", "wrong-digest"])
def test_cli_refuses_missing_or_mismatched_release_record(
    tmp_path: Path, failure: str, capsys: pytest.CaptureFixture[str]
) -> None:
    args, paths = write_inputs(tmp_path)
    receipt = paths["release_record"]
    if failure == "missing":
        receipt.unlink()
    else:
        data = json.loads(receipt.read_text())
        data["released_curves_sha256"] = "0" * 64
        receipt.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "comparisons.json"
    assert main([*args, "--output", str(output)]) != 0
    assert not output.exists()
    assert capsys.readouterr().out == ""


def test_cli_binds_every_input_byte_and_emits_no_statistics(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args, paths = write_inputs(tmp_path)
    output = tmp_path / "comparisons.json"
    assert main([*args, "--output", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["label"] == "exploratory"
    assert result["by_r"]["0.5"]["x3"]["delta"]["point"] == -0.04
    assert set(result["provenance"]["inputs"]) == set(paths)
    for name, path in paths.items():
        assert (
            result["provenance"]["inputs"][name]["sha256"]
            == hashlib.sha256(path.read_bytes()).hexdigest()
        )
    assert capsys.readouterr() == ("", "")


def test_cli_defaults_to_sibling_receipt_and_all_exploratory_inputs_are_optional(
    tmp_path: Path,
) -> None:
    _, paths = write_inputs(tmp_path)
    output = tmp_path / "comparisons.json"
    assert main(["--curves", str(paths["curves"]), "--output", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["by_r"]["0.5"]["x3"]["state"] == "indisponível"
    assert result["provenance"]["inputs"]["x3"] is None


def test_cli_before_x3_x4_aggregation_keeps_x1b_x5(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _, paths = write_inputs(tmp_path)
    output = tmp_path / "partial.json"
    assert (
        main(
            [
                "--curves",
                str(paths["curves"]),
                "--x1b",
                str(paths["x1b"]),
                "--x5",
                str(paths["x5"]),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    result = json.loads(output.read_text())
    assert result["by_r"]["0.5"]["x1b"]["sustained"]["point"] == 0.3
    assert result["by_r"]["0.5"]["x5"][0]["equivalent_strength"]["point"] == 0.03
    assert result["provenance"]["inputs"]["x3"] is None
    assert result["provenance"]["inputs"]["x4"] is None
    assert capsys.readouterr() == ("", "")


def test_cli_refuses_to_overwrite_an_input(tmp_path: Path) -> None:
    args, paths = write_inputs(tmp_path)
    before = paths["curves"].read_bytes()
    assert main([*args, "--output", str(paths["curves"])]) != 0
    assert paths["curves"].read_bytes() == before
