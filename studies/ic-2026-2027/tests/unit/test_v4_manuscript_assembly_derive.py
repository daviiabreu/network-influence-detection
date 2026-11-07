"""Raw synthetic aggregates decide facts; Owner assertions cannot override them."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from ic_study.analysis import v4_manuscript_assembly as assembly
from ic_study.analysis.detection_v4_report import Inputs
from ic_study.analysis.v4_manuscript_assembly import load_facts
from ic_study.analysis.v4_manuscript_assembly_derive import (
    SHELL_BLOCKS,
    derive_facts,
    main,
)
from ic_study.analysis.v4_manuscript_assembly_facts import (
    DERIVABLE_FACTS,
    FACTS_SCHEMA,
    merge_facts,
)
from ic_study.analysis.v4_report_schema import (
    CRITICAL_FLOOR,
    NOT_STARTED,
    SUCCESSOR_SCHEMA,
    VALID,
    _expected_boundaries,
    unit_catalog,
)
from ic_study.analysis.v4_report_synthetic import write_release
from ic_study.simulation.detection_v4 import GRID
from ic_study.simulation.v4_plan import CLOSE_UTC, gate_tasks

STUDY = Path(__file__).resolve().parents[2]
FIXTURES = STUDY / "tests/fixtures/v4_manuscript_assembly"
MANUSCRIPT = STUDY / "publications/jcss-manuscript"
CRITERIA = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
SYNTHETIC: dict[str, Any] = json.loads((FIXTURES / "synthetic_inputs.json").read_text())
KNOWN_DIVERGENCES = {
    ("dress", "ii-comparison-no-ratio", "shp.state"): ("admissible", "parameter-bound")
}


def write(path: Path, obj: Any) -> Path:
    path.write_text(json.dumps(obj, allow_nan=False), encoding="utf-8")
    return path


def record(facts: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"schema": FACTS_SCHEMA, "synthetic": True, "facts": facts or {}}


def fact(value: Any) -> dict[str, Any]:
    return {
        "value": value,
        "source": {
            "record": "owner-decision.json",
            "locator": "/declaration",
            "sha256": "a" * 64,
        },
    }


def release_file(
    tmp_path: Path,
    curves: list[dict[str, Any]],
    incomplete: dict[str, str] | None = None,
) -> Path:
    statuses = {k: NOT_STARTED for k in unit_catalog()}
    statuses.update(incomplete or {})
    statuses.update({c["unit"]: c["status"] for c in curves})
    main_valid = all(
        statuses[k] == VALID for k, m in unit_catalog().items() if m.tier == 1
    )
    for curve in curves:
        if unit_catalog()[curve["unit"]].tier == 1 and not main_valid:
            curve["main_curve_valid"] = False
    obj: dict[str, object] = {
        "inventory": {
            "closed_utc": CLOSE_UTC,
            "main_curve_valid": main_valid,
            "units": [
                {"unit": k, "tier": m.tier, "status": statuses[k]}
                for k, m in unit_catalog().items()
            ],
        },
        "curves": curves,
    }
    path = tmp_path / "released-curves.json"
    write_release(path, obj)
    return path


def gate_file(tmp_path: Path, summaries: list[dict[str, Any]]) -> Path:
    root = tmp_path / "gate"
    root.mkdir(exist_ok=True)
    (root / "criteria.jsonl").write_text(
        "".join(json.dumps(s) + "\n" for s in summaries)
    )
    return root


def case_inputs(tmp_path: Path, case: dict[str, Any]) -> Inputs:
    curves = None
    if case["release"] is not None:
        release = SYNTHETIC["releases"][case["release"]]
        curves = release_file(
            tmp_path,
            [
                copy.deepcopy(SYNTHETIC["profiles"][i]) | {"unit": k}
                for k, i in release["profiles"].items()
            ],
            release["incomplete"],
        )
    shp = (
        None
        if case["shp"] is None
        else write(tmp_path / "shp.json", SYNTHETIC["shp"][case["shp"]])
    )
    return Inputs(
        curves, gate_file(tmp_path, SYNTHETIC["gates"][case["gate"]]), shp, CRITERIA
    )


@pytest.mark.parametrize(
    "case", SYNTHETIC["cases"], ids=lambda c: c["dataset"] + "/" + c["case"]
)
def test_all_24_rehearsals_match_manual_derivable_facts_except_recorded_error(
    tmp_path: Path, case: dict[str, Any]
) -> None:
    derived = derive_facts(case_inputs(tmp_path, case), synthetic=True)["facts"]
    manual = load_facts(
        FIXTURES / case["dataset"] / case["case"] / "assembly-facts.json"
    )["facts"]
    for name, entry in derived.items():
        key = case["dataset"], case["case"], name
        if key in KNOWN_DIVERGENCES:
            assert (manual[name]["value"], entry["value"]) == KNOWN_DIVERGENCES[key]
            assert entry["source"]["locator"].endswith("Results shell block B14")
        else:
            assert entry["value"] == manual[name]["value"], (key, SHELL_BLOCKS[name])
    assert derived or case["case"] in {
        "ii-comparison-no-ratio",
        "iii-comparisons-absent",
    }


def raw_curve(
    unit: str,
    points: list[float],
    *,
    gaps: set[int] | None = None,
    null_valid: bool = True,
) -> dict[str, Any]:
    gaps = gaps or set()
    success = [i not in gaps for i in range(len(GRID))]
    available = [a for a, ok in zip(GRID, success, strict=True) if ok]
    auc = [v for v, ok in zip(points, success, strict=True) if ok]
    lower = [max(0.0, v - 0.02) for v in auc]
    upper = [min(1.0, v + 0.02) for v in auc]
    boundary = _expected_boundaries(available, auc, lower, upper, success)
    return {
        "unit": unit,
        "status": VALID if null_valid else "completo inválido",
        "gap_count": len(gaps),
        "band_complete": not gaps,
        "valid_null_gate": null_valid,
        "valid_curve": null_valid,
        "available_strengths": available,
        "auc": auc,
        "lower": lower,
        "upper": upper,
        "critical": CRITICAL_FLOOR,
        "empirical_exceeds_floor": False,
        "cells": [
            {
                "success": ok,
                "attempts": [
                    {"status": "interior" if ok else "no-L1-root", "evaluations": 1}
                ],
            }
            for ok in success
        ],
        **boundary,
    }


def curves_inputs(tmp_path: Path, curves: list[dict[str, Any]]) -> Inputs:
    return Inputs(release_file(tmp_path, curves), gate_file(tmp_path, []))


@pytest.mark.parametrize(
    "points,expected",
    [
        ([4, 4, 4], False),
        ([4, 5, 6], False),
        ([6, 5, 4], False),
        ([4, 6, 5], True),
        ([4, 9, 5], True),
    ],
)
def test_ordinals_include_ties_and_uncensored_not_attained(
    tmp_path: Path, points: list[int], expected: bool
) -> None:
    curves = [
        raw_curve(
            f"t1-u00-r{i}", [0.5] + [0.55 if j < index else 0.8 for j in range(1, 9)]
        )
        for i, index in enumerate(points)
    ]
    values = derive_facts(curves_inputs(tmp_path, curves), synthetic=True)["facts"]
    assert values["main.boundary_nonmonotone"]["value"] is expected


def test_ordinals_omit_censored_null_and_invalid_units_but_keep_attained_before_gap(
    tmp_path: Path,
) -> None:
    curves = [
        raw_curve("t1-u00-r0", [0.5, 0.55, 0.55, 0.55, 0.8, 0.8, 0.8, 0.8, 0.8]),
        raw_curve(
            "t1-u00-r1", [0.5, 0.55, 0.55, 0.55, 0.8, 0.8, 0.8, 0.8, 0.8], gaps={3}
        ),
        raw_curve("t1-u00-r2", [0.8] * 9, null_valid=False),
        raw_curve(
            "t1-u00-r3", [0.5, 0.55, 0.55, 0.55, 0.55, 0.8, 0.8, 0.8, 0.8], gaps={7}
        ),
        raw_curve("t1-u00-r4", [0.5, 0.55, 0.55, 0.55, 0.55, 0.55, 0.8, 0.8, 0.8]),
    ]
    assert curves[1]["first"] is None and "first_censoring" in curves[1]
    assert curves[3]["first"] == 0.1
    values = derive_facts(curves_inputs(tmp_path, curves), synthetic=True)["facts"]
    assert values["main.boundary_nonmonotone"]["value"] is False


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("gap", True),
        ("dip", True),
        ("interval", True),
        ("invalid", False),
        ("equal", False),
    ],
)
def test_tier2_compares_full_tuples_and_ignores_invalid_unit(
    tmp_path: Path, kind: str, expected: bool
) -> None:
    points = [0.5, 0.55, 0.55, 0.55, 0.8, 0.8, 0.8, 0.8, 0.8]
    if kind in {"dip", "invalid"}:
        points[5] = 0.55
    if kind == "invalid":
        points[0] = 0.8
    if kind == "interval":
        points[5] = 0.71
    curve = raw_curve(
        "t2-u01-r0",
        points,
        gaps={7} if kind == "gap" else None,
        null_valid=kind != "invalid",
    )
    if kind == "interval":
        assert (
            curve["first"] == curve["sustained"]
            and curve["first_interval"] != curve["sustained_interval"]
        )
    values = derive_facts(curves_inputs(tmp_path, [curve]), synthetic=True)["facts"]
    assert values["tier2.boundaries_differ"]["value"] is expected


@pytest.mark.parametrize(
    "estimate,se,expected",
    [
        (0.4999999, 0.0, "below"),
        (0.9000001, 0.0, "above"),
        (0.5, 0.0, "inside"),
        (0.9, 0.0, "inside"),
        (0.7, 0.0, "inside"),
        (0.598, 0.05, "inside"),
        (0.5, 0.01, "interval-outside"),
        (0.9, 0.01, "interval-outside"),
    ],
)
def test_shp_uses_unrounded_point_then_inclusive_interval_edges(
    tmp_path: Path, estimate: float, se: float, expected: str
) -> None:
    inputs = curves_inputs(tmp_path, [])
    shp = copy.deepcopy(SYNTHETIC["shp"][0])
    shp["anchor"].update(
        estimate=estimate,
        standard_error=se,
        wald_95_interval=[max(0, estimate - 1.96 * se), min(1, estimate + 1.96 * se)],
    )
    inputs = replace(inputs, shp=write(tmp_path / "shp.json", shp))
    facts = derive_facts(inputs, synthetic=True)["facts"]
    assert facts["shp.state"]["value"] == "admissible"
    assert facts["shp.grid_position"]["value"] == expected
    assert inputs.shp is not None
    assert (
        facts["shp.state"]["source"]["sha256"]
        == hashlib.sha256(inputs.shp.read_bytes()).hexdigest()
    )


def test_parameter_bound_is_derived_even_without_curves_and_reason_stays_missing(
    tmp_path: Path,
) -> None:
    shp = copy.deepcopy(SYNTHETIC["shp"][0])
    shp["multiwave"]["at_parameter_bound"] = True
    inputs = Inputs(None, gate_file(tmp_path, []), write(tmp_path / "shp.json", shp))
    facts = derive_facts(inputs, synthetic=True)
    assert set(facts["facts"]) == {"shp.state"}
    assert facts["facts"]["shp.state"]["value"] == "parameter-bound"
    assert merge_facts(record(), facts) == facts


@pytest.mark.parametrize("flag", [None, "false", 0])
def test_shp_without_strict_parameter_bound_flag_is_refused(
    tmp_path: Path, flag: object
) -> None:
    shp = copy.deepcopy(SYNTHETIC["shp"][0])
    shp["multiwave"]["at_parameter_bound"] = flag
    inputs = Inputs(None, gate_file(tmp_path, []), write(tmp_path / "shp.json", shp))
    with pytest.raises(ValueError, match="aggregate boolean"):
        derive_facts(inputs, synthetic=True)


@pytest.mark.parametrize("name", sorted(DERIVABLE_FACTS))
def test_owner_cannot_supply_any_calculable_fact_even_without_input(name: str) -> None:
    value = (
        "admissible"
        if name == "shp.state"
        else "inside"
        if name == "shp.grid_position"
        else ["a010"]
        if name.endswith("comparisons")
        else ["anchor"]
        if name.endswith("criteria") and ".G2." not in name
        else ["above"]
        if name.endswith("criteria")
        else False
    )
    with pytest.raises(ValueError, match="Owner cannot supply"):
        merge_facts(record({name: fact(value)}), record())


def test_merge_refuses_conflict_and_equal_override_and_keeps_owner_sources() -> None:
    calculated = record({"tier2.boundaries_differ": fact(False)})
    with pytest.raises(ValueError, match="Conflicting"):
        merge_facts(record({"tier2.boundaries_differ": fact(True)}), calculated)
    with pytest.raises(ValueError, match="Owner cannot supply"):
        merge_facts(calculated, calculated)
    owner = record(
        {
            "shp.state": fact("failed"),
            "shp.reason": fact("public run error"),
            "gate.at_close": fact(True),
            "post.x5_supplied": fact(True),
        }
    )
    assert (
        merge_facts(owner, calculated)["facts"] == owner["facts"] | calculated["facts"]
    )
    with pytest.raises(ValueError, match="synthetic"):
        merge_facts(owner | {"synthetic": False}, calculated)
    with pytest.raises(ValueError, match="Owner declaration"):
        merge_facts(record(), owner)


@pytest.mark.parametrize("state", ["not-run", "failed", "pre-run-divergence"])
def test_no_shp_aggregate_leaves_owner_state_undecided(
    tmp_path: Path, state: str
) -> None:
    derived = derive_facts(Inputs(None, gate_file(tmp_path, [])), synthetic=True)
    assert derived["facts"] == {}
    assert merge_facts(record({"shp.state": fact(state)}), derived)["facts"][
        "shp.state"
    ] == fact(state)


def summary(stage: str, **fields: Any) -> dict[str, Any]:
    count = len(gate_tasks(stage))
    return {
        "gate": stage,
        "planned": count,
        "completed": count,
        "failures": 0,
        "pass": False,
        **fields,
    }


@pytest.mark.parametrize(
    "stage,fields,expected",
    [
        (
            "G0",
            {
                "fits": 100,
                "anchor_failures": 1,
                "budget_statuses": 1,
                "implementation_statuses": 2,
            },
            ["anchor", "budget", "implementation"],
        ),
        (
            "G0",
            {
                "fits": 100,
                "anchor_failures": 0,
                "budget_statuses": 1,
                "implementation_statuses": 1,
            },
            ["budget"],
        ),
        (
            "G1c",
            {
                "anchor_count": 149,
                "pointwise_failures": 4,
                "mean_z": 3.0000001,
                "tie_rate": 0,
            },
            ["anchor", "pointwise", "mean"],
        ),
        (
            "G1c",
            {"anchor_count": 149, "pointwise_failures": 3, "mean_z": 3, "tie_rate": 0},
            ["anchor"],
        ),
        (
            "G2",
            {"cell_ratios": [], "failure_allowance_met": False, "fd_stable": False},
            ["allowance", "fd", "insufficient"],
        ),
    ],
)
def test_gate_failure_clauses_and_exact_equal_limits(
    tmp_path: Path, stage: str, fields: dict[str, Any], expected: list[str]
) -> None:
    inputs = Inputs(
        None, gate_file(tmp_path, [summary(stage, **fields)]), criteria=CRITERIA
    )
    facts = derive_facts(inputs, synthetic=True)["facts"]
    assert facts[f"gate.{stage}.failed_criteria"]["value"] == expected


@pytest.mark.parametrize("stage", ["G0", "G1c", "G2", "G2c"])
def test_incomplete_and_early_task_failure_do_not_invent_criteria(
    tmp_path: Path, stage: str
) -> None:
    row = summary(stage, failures=1)
    inputs = Inputs(None, gate_file(tmp_path, [row]))
    assert not derive_facts(inputs, synthetic=True)["facts"]
    row["completed"] -= 1
    gate_file(tmp_path, [row])
    assert not derive_facts(inputs, synthetic=True)["facts"]


def test_g2_checks_pooled_and_cell_intervals_and_threshold_source(
    tmp_path: Path,
) -> None:
    criteria = write(
        tmp_path / "criteria.json",
        {
            "thresholds": {
                "cell_lower": 0.8,
                "cell_upper": 1.2,
                "pooled_lower": 0.9,
                "pooled_upper": 1.1,
            }
        },
    )
    row = summary(
        "G2",
        cell_ratios=[1, 1],
        cell_lower=[0.7, 1.2000001],
        cell_upper=[0.7999999, 1.3],
        pooled_lower=1.1000001,
        pooled_upper=1.2,
        failure_allowance_met=True,
        fd_stable=True,
    )
    inputs = Inputs(None, gate_file(tmp_path, [row]), criteria=criteria)
    entry = derive_facts(inputs, synthetic=True)["facts"]["gate.G2.failed_criteria"]
    assert entry["value"] == ["above", "below"]
    assert (
        hashlib.sha256(criteria.read_bytes()).hexdigest() in entry["source"]["locator"]
    )
    assert not derive_facts(replace(inputs, criteria=None), synthetic=True)["facts"]
    row.update(
        cell_lower=[0.8, 1.2],
        cell_upper=[0.8, 1.2],
        pooled_lower=0.9,
        pooled_upper=1.1,
        fd_stable=False,
    )
    gate_file(tmp_path, [row])
    assert derive_facts(inputs, synthetic=True)["facts"]["gate.G2.failed_criteria"][
        "value"
    ] == ["fd"]
    row.update(
        cell_lower=[0.9, 0.9],
        cell_upper=[1.1, 1.1],
        pooled_lower=1.1000001,
        pooled_upper=1.2,
        fd_stable=True,
    )
    gate_file(tmp_path, [row])
    assert derive_facts(inputs, synthetic=True)["facts"]["gate.G2.failed_criteria"][
        "value"
    ] == ["above"]


@pytest.mark.parametrize(
    "comparison,change,expected",
    [
        (0, {"upper": 0.7999999}, ["a010"]),
        (1, {"lower": 2.0000001, "upper": 2.1}, ["a003"]),
        (0, {"failure_count": 4}, ["a010"]),
        (1, {"failure_count": 3}, ["a003"]),
    ],
)
def test_g2c_exact_failures_do_not_use_rounded_values(
    tmp_path: Path, comparison: int, change: dict[str, Any], expected: list[str]
) -> None:
    comparisons = [
        {
            "denominator": 100,
            "failure_count": 3,
            "lower": 0.7,
            "upper": 0.8,
            "ratio": 0.75,
            "pass": True,
        },
        {
            "denominator": 40,
            "failure_count": 2,
            "lower": 2.0,
            "upper": 2.1,
            "ratio": 2.05,
            "pass": True,
        },
    ]
    comparisons[comparison].update(change, **{"pass": False})
    row = summary("G2c", comparisons=comparisons)
    inputs = Inputs(None, gate_file(tmp_path, [row]))
    assert (
        derive_facts(inputs, synthetic=True)["facts"]["gate.G2c.failed_comparisons"][
            "value"
        ]
        == expected
    )
    comparisons[comparison]["pass"] = True
    gate_file(tmp_path, [row])
    with pytest.raises(ValueError, match="aggregate predicate"):
        derive_facts(inputs, synthetic=True)


def test_used_stage_successor_has_its_own_source_not_criteria_jsonl(
    tmp_path: Path,
) -> None:
    gate = gate_file(tmp_path, [])
    write(gate / "authorization-G1c.json", {"freeze_sha256": "f" * 64})
    for task in gate_tasks("G1c"):
        directory = gate / task.key
        directory.mkdir()
        write(directory / "result.json", {})
    row = summary("G1c", anchor_count=149, pointwise_failures=3, mean_z=3, tie_rate=0)
    successor = write(
        tmp_path / "successor.json",
        {
            "schema": SUCCESSOR_SCHEMA,
            "stage": "G1c",
            "reason": "synthetic aggregate",
            "freeze_sha256": "f" * 64,
            "sealed_root_identifier": gate.name,
            "summary": row,
        },
    )
    inputs = Inputs(None, gate, successors=(successor,))
    entry = derive_facts(inputs, synthetic=True)["facts"]["gate.G1c.failed_criteria"]
    assert entry["source"]["record"] == successor.name
    assert (
        entry["source"]["sha256"] == hashlib.sha256(successor.read_bytes()).hexdigest()
    )
    gate_file(tmp_path, [row])
    assert (
        derive_facts(inputs, synthetic=True)["facts"]["gate.G1c.failed_criteria"][
            "source"
        ]["record"]
        == "criteria.jsonl"
    )


def test_release_receipt_and_allocation_binding_are_validated_before_derivation(
    tmp_path: Path,
) -> None:
    inputs = case_inputs(tmp_path, SYNTHETIC["cases"][0])
    receipt = tmp_path / "release-record.json"
    raw = json.loads(receipt.read_text())
    raw["released_curves_sha256"] = "0" * 64
    write(receipt, raw)
    with pytest.raises(ValueError, match="SHA-256"):
        derive_facts(inputs, synthetic=True)
    allocation = write(
        tmp_path / "allocation.json",
        {
            "schema": 1,
            "stage": "post-G0-pre-G2",
            "freeze_sha256": "f" * 64,
            "criteria_sha256": "0" * 64,
            "g0_statuses_sha256": "0" * 64,
            "g0_gap_binding": {},
            "g2_cells": [[0.03, 0.7]],
        },
    )
    with pytest.raises(ValueError, match="criteria bound"):
        derive_facts(
            replace(inputs, curves=None, allocation=allocation), synthetic=True
        )


@pytest.mark.parametrize(
    "part",
    [
        "sealed-v4-any",
        "sealed-v4-exploratory-x3-x7",
        "restricted",
        "coord-20260925/v4-release",
        "coord-20260925/v4-tier-logs",
        "coord-20260925/v4-gate-logs",
    ],
)
def test_forbidden_inputs_are_rejected_before_load(tmp_path: Path, part: str) -> None:
    with pytest.raises(ValueError, match="Forbidden"):
        derive_facts(Inputs(tmp_path / part / "curves.json", None))


def test_gate_child_symlink_to_forbidden_path_is_refused_before_load(
    tmp_path: Path,
) -> None:
    gate = gate_file(tmp_path, [])
    (gate / "G0-r0").symlink_to(tmp_path / "restricted", target_is_directory=True)
    with pytest.raises(ValueError, match="Forbidden"):
        derive_facts(Inputs(None, gate), synthetic=True)


def test_cli_refuses_public_aggregates_before_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "facts.json"
    code = main(
        [
            "--public-aggregates",
            str(tmp_path / "public-aggregates.json"),
            "--owner-facts",
            str(tmp_path / "owner-facts.json"),
            "--out",
            str(out),
            "--confirmatory-values",
            str(tmp_path / "a-catalog.json"),
            "--manuscript",
            str(tmp_path),
        ]
    )
    assert code == 2
    assert "authorized released inputs" in capsys.readouterr().out
    assert not out.exists()


def test_cli_writes_new_facts_then_audits_missing_owner_declarations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    case = next(
        c
        for c in SYNTHETIC["cases"]
        if c["dataset"] == "release-day" and c["case"] == "unavailable"
    )
    inputs = case_inputs(tmp_path, case)
    shell = tmp_path / "synthetic-shell.tex"
    shell.write_text("Synthetic " * 150 + "\n")
    (tmp_path / "main.tex").write_text(r"\abstract{Synthetic.}")
    (tmp_path / "sections").mkdir()
    for name, text in {
        "discussion.tex": "% DS01\nSynthetic fixed discussion.\n",
        "conclusion.tex": (
            "[Insert result.] [State whether boundary.] [Insert implication.]"
        ),
        "supplement.tex": "Synthetic supplement.\n",
    }.items():
        (tmp_path / "sections" / name).write_text(text)
    conditions: dict[str, Any] = {
        name: name == "B1a"
        for name in (
            "B1a",
            "B1b-G0",
            "B1b-G1b",
            "B1b-G1c",
            "B1c",
            "B1b-G2",
            "B1b-G2c",
            "B1d",
        )
    }
    conditions |= {
        "A.synthetic": True,
        "SHP": {"fact_recorded": "shp.state"},
        "REASON": {
            "all": [
                {"fact_eq": ["shp.state", "not-run"]},
                {"fact_recorded": "shp.reason"},
            ]
        },
    }
    rules = write(
        tmp_path / "synthetic-rules.json",
        {
            "schema": "ic-study.v4-manuscript-assembly-rules.v1",
            "sources": {
                "synthetic": {
                    "path": shell.name,
                    "sha256": hashlib.sha256(shell.read_bytes()).hexdigest(),
                }
            },
            "predicates": {"PASS": {"ref": "B1a"}, "POST": False},
            "rules": [
                {
                    "id": name,
                    "source": "synthetic",
                    "line": 1,
                    "end_line": 1,
                    "condition": condition,
                    "operation": "abstract" if name == "A.synthetic" else "group",
                    "slot": "abstract" if name == "A.synthetic" else "gate",
                    "order": 0,
                }
                for name, condition in conditions.items()
            ],
        },
    )
    monkeypatch.setattr(assembly, "RULES", rules)
    catalog = write(
        tmp_path / "catalog.json",
        {"schema": "ic-study.v4-result-values.v1", "values": {}},
    )
    owner = write(tmp_path / "owner.json", record())
    output = tmp_path / "facts.json"
    args = [
        "--curves",
        str(inputs.curves),
        "--gate-root",
        str(inputs.gate_root),
        "--criteria",
        str(CRITERIA),
        "--owner-facts",
        str(owner),
        "--out",
        str(output),
        "--synthetic",
        "--confirmatory-values",
        str(catalog),
        "--manuscript",
        str(tmp_path),
    ]
    assert main(args) == 2
    audit = json.loads(capsys.readouterr().out)
    assert "shp.state" in audit["missing_facts"]
    assert "Assembly refused:" in audit["refusal"]
    assert set(load_facts(output)["facts"]) == {
        "main.boundary_nonmonotone",
        "tier2.boundaries_differ",
    }
    before = output.read_bytes()
    assert main(args) == 2
    assert "new file" in capsys.readouterr().out
    assert output.read_bytes() == before
    owner.write_text(
        json.dumps(
            record(
                {
                    "shp.state": fact("not-run"),
                    "shp.reason": fact("synthetic run omitted"),
                }
            )
        )
    )
    ready = tmp_path / "ready-facts.json"
    args[args.index("--out") + 1] = str(ready)
    assert main(args) == 0
    assert not json.loads(capsys.readouterr().out)["missing_facts"]
    assert load_facts(ready)["facts"]["shp.reason"] == fact("synthetic run omitted")
