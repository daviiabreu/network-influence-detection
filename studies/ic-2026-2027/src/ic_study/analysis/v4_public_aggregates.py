"""Project validated reporting objects without certifying their provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import types
from collections import Counter
from dataclasses import asdict, dataclass, fields, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast, get_args, get_origin, get_type_hints

from ic_study.analysis.detection_v4_report import (
    Inputs,
    Loaded,
    add_input_arguments,
    code_commit,
    load_inputs,
    parse_inputs,
    sha256,
)
from ic_study.analysis.shp_crosswalk import QUASI_SIMPLEX
from ic_study.analysis.shp_crosswalk import SCHEMA as CROSSWALK_SCHEMA
from ic_study.analysis.shp_reliability import SUCCESSOR
from ic_study.analysis.v4_report_protocol import protocol
from ic_study.analysis.v4_report_schema import (
    ACCEPTED_FIT,
    CRITICAL_FLOOR,
    CROSSWALK_REFERENCES,
    FAMILY_LIMITS,
    GAP_KINDS,
    GATE_STAGES,
    INVALID,
    PROPAGATION,
    SECONDARY_TARGETS,
    SHP_ANALYSIS,
    SOLVER_FAILURES,
    STATUSES,
    VALID,
    CellDiagnostics,
    Crosswalk,
    Curve,
    FitOutcome,
    GateRecords,
    Release,
    ReleaseRecord,
    SchemaError,
    ShpAnchor,
    StageSuccessor,
    _expected_boundaries,
    _first_boundary,
    band_contains_point,
    parse_crosswalk,
    parse_shp,
    parse_summary,
    unit_catalog,
)
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES
from ic_study.simulation.v4_plan import CLOSE_UTC, SCENARIOS, gate_tasks

SCHEMA = "ic-study.v4-public-aggregates.v1"
NOTICE = "Rendering integrity only; provenance requires authorized access."
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_FIT_STATUSES = ACCEPTED_FIT | FAMILY_LIMITS | SOLVER_FAILURES | {"dependency-gap"}
# Amendment v4.4 covers curve cells only: no G0 fit is a propagation gap.
_FIT_GAPS = (None, *(kind for kind in GAP_KINDS if kind != PROPAGATION))
_BASE = {"gate": str, "planned": int, "completed": int, "failures": int, "pass": bool}
_SUMMARY: dict[str, dict[str, Any]] = {
    "G0": {
        "statuses": {s: int for s in _FIT_STATUSES},
        "fits": int,
        "anchor_failures": int,
        "implementation_statuses": int,
        "budget_statuses": int,
    },
    "G1b": {
        "coverage_counts": {s: int for s in SCENARIOS},
        "empirical_exceeds_floor_count": int,
    },
    "G1c": {
        "pointwise_failures": int,
        "anchor_count": int,
        "mean_z": float,
        "tie_rate": float,
    },
    "G2": {
        "cell_failure_counts": list[int],
        "successful_pair_counts": list[int],
        "cell_ratios": list[float],
        "cell_lower": list[float],
        "cell_upper": list[float],
        "pooled_ratio": float,
        "pooled_lower": float,
        "pooled_upper": float,
        "loo_tail_counts": list[int],
        "fd_ratio_median_by_cell": list[float | None],
        "covariance_flag_counts": list[int],
    },
    "G2c": {
        "comparisons": [
            {
                "failure_count": int,
                "denominator": int,
                "ratio": float,
                "lower": float,
                "upper": float,
                "tails": int,
            }
        ],
    },
}
_OBJECTS = {"release", "gate", "shp", "crosswalk", "thresholds", "release_event"}
_FILE_ROLES = {
    "curves",
    "release_record",
    "shp",
    "crosswalk",
    "criteria",
    "allocation",
    "stage_successors",
    "gate_criteria",
    *(
        f"gate_{stage}_{kind}"
        for stage in GATE_STAGES
        for kind in ("results", "seals", "authorization")
    ),
}


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SchemaError(message)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise SchemaError(f"Non-finite JSON number: {value}")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes(), object_pairs_hook=_pairs, parse_constant=_constant
    )
    _require(isinstance(value, dict), "Expected a JSON object")
    return cast(dict[str, Any], value)


def _fields(
    value: object, allowed: set[str], name: str, *, exact: bool = True
) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{name}: expected object")
    data = cast(dict[str, Any], value)
    _require(set(data) <= allowed, f"{name}: unknown fields {set(data) - allowed}")
    if exact:
        _require(set(data) == allowed, f"{name}: missing fields {allowed - set(data)}")
    return data


def _decode(value: object, spec: Any, name: str) -> Any:
    """Decode only explicitly declared fields, including every nested object."""
    origin, args = get_origin(spec), get_args(spec)
    if spec is type(None):
        _require(value is None, f"{name}: expected null")
        return None
    if origin is types.UnionType:
        for alternative in args:
            try:
                return _decode(value, alternative, name)
            except SchemaError:
                pass
        raise SchemaError(f"{name}: no matching type")
    if spec in (str, int, bool, float):
        valid = type(value) is spec
        if spec is float:
            try:
                valid = type(value) in (int, float) and math.isfinite(
                    cast(float, value)
                )
            except OverflowError:
                valid = False
        _require(valid, f"{name}: expected {spec.__name__}")
        return float(cast(float, value)) if spec is float else value
    if isinstance(spec, dict):
        data = _fields(value, set(spec), name, exact=False)
        return {k: _decode(v, spec[k], f"{name}.{k}") for k, v in data.items()}
    if isinstance(spec, list) or origin in (list, tuple):
        _require(isinstance(value, list), f"{name}: expected array")
        items = cast(list[Any], value)
        if origin is tuple and args[-1] is not Ellipsis:
            _require(len(items) == len(args), f"{name}: wrong array length")
            return tuple(_decode(v, s, name) for v, s in zip(items, args, strict=True))
        item_spec = spec[0] if isinstance(spec, list) else args[0]
        decoded = [_decode(v, item_spec, name) for v in items]
        return tuple(decoded) if origin is tuple else decoded
    if origin is dict:
        _require(isinstance(value, dict), f"{name}: expected object")
        return {
            _decode(k, args[0], name): _decode(v, args[1], f"{name}.{k}")
            for k, v in cast(dict[str, Any], value).items()
        }
    if isinstance(spec, type) and is_dataclass(spec):
        data = _fields(value, {f.name for f in fields(spec)}, name)
        hints = get_type_hints(spec)
        return spec(**{k: _decode(v, hints[k], f"{name}.{k}") for k, v in data.items()})
    raise TypeError(f"Undeclared public type: {spec}")


def _histogram(values: tuple[Any, ...]) -> list[dict[str, Any]]:
    return [
        {"value": value, "count": count}
        for value, count in sorted(Counter(values).items())
    ]


def _gate_object(gate: GateRecords | None) -> dict[str, Any] | None:
    if gate is None:
        return None
    summaries = {}
    for stage, summary in gate.summaries.items():
        summaries[stage] = {
            k: v for k, v in summary.items() if k in _BASE | _SUMMARY[stage]
        }
        if stage == "G2c":
            summaries[stage]["comparisons"] = [
                {k: v for k, v in row.items() if k in _SUMMARY[stage]["comparisons"][0]}
                for row in summary.get("comparisons", [])
            ]
    stop = None
    if gate.stop is not None:
        stop = {
            k: gate.stop["g0_gap_binding"][k]
            for k in ("pass_probability", "minimum", "gaps", "denominator")
        }
    counts = Counter((fit.status, fit.gap) for fit in gate.g0_fits)
    return {
        "summaries": summaries,
        "summary_counts": gate.summary_counts,
        "stop": stop,
        "g1b_critical": _histogram(gate.g1b_critical),
        "g0_evaluations": _histogram(gate.g0_evaluations),
        "g0_fits": [
            {"status": status, "gap": gap, "count": count}
            for (status, gap), count in sorted(counts.items(), key=lambda x: str(x[0]))
        ],
        "sealed": gate.sealed,
        "planned": gate.planned,
        "started": [s for s in GATE_STAGES if gate.started(s)],
        "successors": [
            {"stage": s.stage, "name": s.name, "sha256": s.sha256}
            for s in gate.successors
            if s.stage in gate.from_successor
        ],
        "g2_cells": gate.g2_cells,
    }


def _hash(value: object) -> str:
    _require(
        isinstance(value, str) and _DIGEST.fullmatch(value) is not None,
        "Invalid SHA-256",
    )
    return cast(str, value)


def _stages(value: object, name: str) -> dict[str, int]:
    data = _decode(value, {s: int for s in GATE_STAGES}, name)
    _require(all(v >= 0 for v in data.values()), f"{name}: negative count")
    return cast(dict[str, int], data)


def _expand(value: object, spec: type[int] | type[float], name: str) -> tuple[Any, ...]:
    _require(isinstance(value, list), f"{name}: expected histogram")
    output: list[Any] = []
    seen = set()
    for row in cast(list[Any], value):
        data = _fields(row, {"value", "count"}, name)
        number = _decode(data["value"], spec, name)
        count = _decode(data["count"], int, name)
        _require(number not in seen and 0 < count <= 100_000, f"{name}: invalid bin")
        _require(
            number >= 0 and len(output) + count <= 100_000, f"{name}: invalid histogram"
        )
        seen.add(number)
        output.extend([number] * count)
    return tuple(output)


def _load_gate(value: object) -> GateRecords | None:
    if value is None:
        return None
    data = _fields(
        value,
        {
            "summaries",
            "summary_counts",
            "stop",
            "g1b_critical",
            "g0_evaluations",
            "g0_fits",
            "sealed",
            "planned",
            "started",
            "successors",
            "g2_cells",
        },
        "gate",
    )
    summaries = _fields(data["summaries"], set(GATE_STAGES), "summaries", exact=False)
    parsed = {}
    for stage, summary in summaries.items():
        item = _decode(summary, _BASE | _SUMMARY[stage], stage)
        _require(
            set(item) >= set(_BASE) and item["gate"] == stage, "Summary stage mismatch"
        )
        parsed[stage] = parse_summary(item)
    stop = data["stop"]
    if stop is not None:
        stop = _fields(
            stop, {"pass_probability", "minimum", "gaps", "denominator"}, "stop"
        )
        stop = _decode(
            stop,
            {
                "pass_probability": float,
                "minimum": float,
                "gaps": int,
                "denominator": int,
            },
            "stop",
        )
        _require(
            0 <= stop["pass_probability"] <= 1
            and 0 <= stop["minimum"] <= 1
            and 0 <= stop["gaps"] <= stop["denominator"],
            "Invalid public stop",
        )
        stop = {"pass": False, "stopped_before_G2": True, "g0_gap_binding": stop}
    fits: list[FitOutcome] = []
    seen = set()
    for row in _decode(
        data["g0_fits"], [{"status": str, "gap": str | None, "count": int}], "fits"
    ):
        _require(set(row) == {"status", "gap", "count"}, "Missing fit histogram field")
        key = (row["status"], row["gap"])
        _require(
            row["status"] in _FIT_STATUSES and row["gap"] in _FIT_GAPS,
            "Unknown fit category",
        )
        _require(
            key not in seen
            and 0 < row["count"] <= 100_000
            and len(fits) + row["count"] <= 100_000,
            "Invalid fit histogram",
        )
        seen.add(key)
        fits.extend([FitOutcome(*key)] * row["count"])
    started = _decode(data["started"], list[str], "started")
    _require(
        len(started) == len(set(started)) and set(started) <= set(GATE_STAGES),
        "Unknown/duplicate started stage",
    )
    successors: list[StageSuccessor] = []
    for row in _decode(
        data["successors"], [{"stage": str, "name": str, "sha256": str}], "successors"
    ):
        _require(set(row) == {"stage", "name", "sha256"}, "Missing successor field")
        _require(
            row["stage"] in parsed
            and row["stage"] not in {s.stage for s in successors},
            "Invalid successor stage",
        )
        _require(
            re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9_.-]*", row["name"]) is not None,
            "Unsafe public successor name",
        )
        successors.append(
            StageSuccessor(
                row["stage"], parsed[row["stage"]], row["name"], _hash(row["sha256"])
            )
        )
    cells = _decode(
        data["g2_cells"], tuple[tuple[float, float], ...] | None, "g2_cells"
    )
    if cells is not None:
        _require(
            bool(cells)
            and len(cells) == len(set(cells))
            and all(a in GRID and r in RELIABILITIES for a, r in cells),
            "Invalid G2 cells",
        )
    planned = _stages(data["planned"], "planned")
    sealed = _stages(data["sealed"], "sealed")
    _require(set(planned) == set(sealed) == set(GATE_STAGES), "Missing gate counts")
    _require(
        all(sealed[s] <= planned[s] for s in GATE_STAGES), "Gate count exceeds plan"
    )
    return GateRecords(
        parsed,
        _stages(data["summary_counts"], "summary_counts"),
        stop,
        _expand(data["g1b_critical"], float, "critical"),
        _expand(data["g0_evaluations"], int, "evaluations"),
        tuple(fits),
        (),
        None,
        sealed,
        planned,
        frozenset(started),
        tuple(successors),
        frozenset(s.stage for s in successors),
        cells,
    )


@dataclass(frozen=True)
class PublicAggregates:
    loaded: Loaded
    synthetic: bool
    source_hashes: dict[str, list[str]]


def _release_object(release: Release | None) -> dict[str, Any] | None:
    if release is None:
        return None
    result = asdict(release)
    for key, curve in release.curves.items():
        row = result["curves"][key]
        del row["cell_final_status"]
        del row["main_curve_valid"]
        low = (
            curve.meta.tier == 1
            and curve.status == VALID
            and curve.first.point in GRID[1:3]
        )
        diagnostics = []
        for index, found in enumerate(curve.diagnostics):
            item = None
            if low and index in (1, 2):
                item = asdict(found)
                del item["matching_pairs"]
                item["retry"] = protocol().retry_pairs in found.matching_pairs
            diagnostics.append(item)
        row["diagnostics"] = diagnostics
    return result


def _load_release(value: object) -> Release | None:
    if value is None:
        return None
    top = _fields(value, {f.name for f in fields(Release)}, "release")
    curves = _fields(top["curves"], set(unit_catalog()), "curves", exact=False)
    expanded = dict(top)
    expanded["curves"] = {}
    empty = asdict(CellDiagnostics((), (), None, None, None, None, None))
    curve_fields = {f.name for f in fields(Curve)} - {
        "cell_final_status",
        "main_curve_valid",
    }
    diagnostic_fields = set(empty) - {"matching_pairs"} | {"retry"}
    for key, value in curves.items():
        row = dict(_fields(value, curve_fields, "curve"))
        _require(
            isinstance(row["diagnostics"], list)
            and len(row["diagnostics"]) == len(GRID),
            "Public diagnostics must cover the grid",
        )
        diagnostics = []
        for item in row["diagnostics"]:
            if item is None:
                diagnostics.append(empty)
            else:
                diagnostic = dict(_fields(item, diagnostic_fields, "diagnostics"))
                retry = _decode(diagnostic.pop("retry"), bool, "retry")
                diagnostic["matching_pairs"] = [protocol().retry_pairs] if retry else []
                diagnostics.append(diagnostic)
        row["diagnostics"] = diagnostics
        row["cell_final_status"] = [None] * len(GRID)
        row["main_curve_valid"] = (
            False
            if unit_catalog()[key].tier == 1 and top["main_curve_valid"] is False
            else None
        )
        expanded["curves"][key] = row
    release = cast(
        Release, _decode(json.loads(canonical(expanded)), Release, "release")
    )
    _validate_release(release)
    _require(
        canonical(_release_object(release)) == canonical(top),
        "Diagnostics outside published low-strength cells",
    )
    return release


def _validate_shp(shp: ShpAnchor) -> None:
    anchor = {
        k: v
        for k, v in asdict(shp).items()
        if k in {"year", "estimate", "standard_error", "wald_95_interval"}
    }
    raw: dict[str, Any] = {
        "analysis": SHP_ANALYSIS,
        "anchor": anchor,
        "sensitivity_envelope": shp.sensitivity_envelope,
    }
    if shp.starts is not None:
        found = shp.starts
        starts = (
            {"status": "failed", "reasons": list(found.failure_reasons)}
            if found.failure_reasons
            else {
                "status": "admissible",
                "anchor": {
                    k: v for k, v in asdict(found).items() if k != "failure_reasons"
                },
            }
        )
        raw["successor_1"] = {"specification": SUCCESSOR, "starts_sensitivity": starts}
    _require(
        parse_shp(json.loads(canonical(raw))) == shp, "Public SHP invariants differ"
    )


def _validate_crosswalk(crosswalk: Crosswalk) -> None:
    cells = []
    for row in crosswalk.ranges:
        cell = {
            "r": row.r,
            "estimators": {
                QUASI_SIMPLEX: {
                    "n_values": row.values,
                    "failures": row.failures,
                    "min": row.low,
                    "max": row.high,
                    "mean": row.low,
                }
            },
        }
        if row.reference == "a = 0":
            cell.update({"family": "interaction", "a": 0, "eta": None})
        else:
            _require(
                row.reference in CROSSWALK_REFERENCES, "Unknown crosswalk reference"
            )
            cell.update(
                {"family": "B", "eta": float(row.reference.removeprefix("B η = "))}
            )
        cells.append(cell)
    raw = {
        "schema": CROSSWALK_SCHEMA,
        "status": "exploratory",
        "declared_plan": crosswalk.declared_plan,
        "parameters": {
            "replicates": crosswalk.replicates,
            "estimators": [QUASI_SIMPLEX],
        },
        "cells": cells,
    }
    _require(
        parse_crosswalk(json.loads(canonical(raw))) == crosswalk,
        "Public crosswalk invariants differ",
    )


def _validate_release(release: Release) -> None:
    catalog = unit_catalog()
    _require(release.closed_utc == CLOSE_UTC, "Public close differs from frozen close")
    _require(
        set(release.statuses) == set(catalog),
        "Public inventory differs from frozen inventory",
    )
    _require(
        all(s in STATUSES for s in release.statuses.values()), "Unknown unit status"
    )
    _require(
        set(release.curves)
        == {k for k, s in release.statuses.items() if s in {VALID, INVALID}},
        "Completed public units and curves differ",
    )
    _require(
        release.main_curve_valid
        == all(release.statuses[k] == VALID for k, m in catalog.items() if m.tier == 1),
        "Public main validity differs",
    )
    for key, curve in release.curves.items():
        _require(
            key in catalog and curve.meta == catalog[key],
            "Public unit metadata differs",
        )
        _require(curve.status == release.statuses[key], "Curve status differs")
        _require(
            len(curve.cell_success)
            == len(curve.cell_gap)
            == len(curve.cell_final_status)
            == len(curve.diagnostics)
            == len(GRID),
            "Public cells do not cover frozen grid",
        )
        _require(
            curve.available
            == tuple(a for a, ok in zip(GRID, curve.cell_success, strict=True) if ok),
            "Public available strengths differ",
        )
        _require(
            len(curve.auc)
            == len(curve.lower)
            == len(curve.upper)
            == len(curve.available),
            "Public band length differs",
        )
        _require(
            all(
                0 <= lo <= hi <= 1 and 0 <= p <= 1 and band_contains_point(lo, p, hi)
                for lo, p, hi in zip(curve.lower, curve.auc, curve.upper, strict=True)
            ),
            "Invalid public AUC band",
        )
        _require(
            all(s is None or s in _FIT_STATUSES for s in curve.cell_final_status)
            and all(g in (None, *GAP_KINDS) for g in curve.cell_gap),
            "Unknown public cell category",
        )
        _require(len(curve.secondary) == 2, "Public secondary boundary count differs")
        _require(
            curve.gap_count == curve.cell_success.count(False)
            and curve.band_complete == (curve.gap_count == 0),
            "Public gap count differs",
        )
        null_gate = bool(
            curve.available
            and curve.available[0] == 0
            and curve.lower[0] <= 0.5 <= curve.upper[0]
        )
        _require(
            curve.valid_null_gate == null_gate
            and curve.status == (VALID if null_gate else INVALID),
            "Public null gate differs from band",
        )
        if curve.available:
            _require(
                curve.critical is not None
                and curve.critical >= CRITICAL_FLOOR
                and curve.empirical_exceeds_floor == (curve.critical > CRITICAL_FLOOR),
                "Public critical value differs from floor",
            )
        else:
            _require(
                curve.critical is None
                and curve.empirical_exceeds_floor is None
                and curve.nonmonotone_band is None,
                "Public estimates without available strengths",
            )
        _require(
            not curve.first.sustained and curve.sustained.sustained,
            "Public boundary kind differs",
        )
        _require(
            curve.secondary
            == tuple(
                _first_boundary(
                    _expected_boundaries(
                        curve.available,
                        curve.auc,
                        curve.lower,
                        curve.upper,
                        curve.cell_success,
                        target,
                    )
                )
                for target in SECONDARY_TARGETS
            ),
            "Public secondary boundaries differ from inversion",
        )
        for boundary in (curve.first, curve.sustained, *curve.secondary):
            _require(
                boundary.point is None or boundary.point in GRID,
                "Boundary outside frozen grid",
            )
            if boundary.interval is not None:
                _require(
                    all(v is None or v in GRID for v in boundary.interval),
                    "Interval outside frozen grid",
                )
            for marker in (boundary.censoring, boundary.interval_censoring):
                _require(
                    marker is None
                    or re.fullmatch(r"gap at a=[0-9.e-]+", marker) is not None,
                    "Unknown public censoring",
                )
        expected = _expected_boundaries(
            curve.available, curve.auc, curve.lower, curve.upper, curve.cell_success
        )
        if curve.available:
            _require(
                curve.nonmonotone_band == expected["nonmonotone_band"],
                "Public nonmonotone flag differs",
            )
        for prefix, boundary in (
            ("first", curve.first),
            ("sustained", curve.sustained),
        ):
            _require(
                (
                    boundary.point,
                    boundary.interval,
                    boundary.censoring,
                    boundary.interval_censoring,
                )
                == (
                    expected[prefix],
                    None
                    if expected[f"{prefix}_interval"] is None
                    else tuple(cast(list[Any], expected[f"{prefix}_interval"])),
                    expected.get(f"{prefix}_censoring"),
                    expected.get(f"{prefix}_interval_censoring"),
                ),
                "Public boundary disagrees with frozen inversion",
            )


def load_public(path: Path) -> PublicAggregates:
    """Check structure and self-hashes; do not authenticate the source evidence."""
    return _parse_public(read_json(path))


def _parse_public(value: object) -> PublicAggregates:
    data = _fields(
        value,
        {
            "schema",
            "notice",
            "synthetic",
            "code",
            "source_hashes",
            "objects",
            "objects_sha256",
            "sha256",
        },
        "projection",
    )
    _require(
        data["schema"] == SCHEMA and data["notice"] == NOTICE,
        "Not a public aggregate projection",
    )
    _require(
        _hash(data["sha256"])
        == digest({k: v for k, v in data.items() if k != "sha256"}),
        "Projection SHA-256 mismatch",
    )
    objects = _fields(data["objects"], _OBJECTS, "objects")
    hashes = _fields(data["objects_sha256"], _OBJECTS, "object hashes")
    for key, value in objects.items():
        _require(_hash(hashes[key]) == digest(value), f"{key}: object SHA-256 mismatch")
    code = _fields(
        data["code"], {"commit", "reporting_code_dirty", "modules_sha256"}, "code"
    )
    _require(
        code["commit"] is None
        or (
            isinstance(code["commit"], str)
            and re.fullmatch(r"[0-9a-f]{40}", code["commit"]) is not None
        ),
        "Invalid code revision",
    )
    _decode(code["reporting_code_dirty"], bool | None, "code dirty")
    modules = _fields(
        code["modules_sha256"],
        {"v4_public_aggregates.py", "detection_v4_report.py", "v4_report_schema.py"},
        "modules",
    )
    for value in modules.values():
        _hash(value)
    sources = _fields(data["source_hashes"], _FILE_ROLES, "source hashes", exact=False)
    for values in sources.values():
        _require(isinstance(values, list) and bool(values), "Empty source hash list")
        for value in values:
            _hash(value)
    release = _load_release(objects["release"])
    shp = cast(ShpAnchor | None, _decode(objects["shp"], ShpAnchor | None, "shp"))
    if shp is not None:
        _validate_shp(shp)
    crosswalk = cast(
        Crosswalk | None, _decode(objects["crosswalk"], Crosswalk | None, "crosswalk")
    )
    if crosswalk is not None:
        _validate_crosswalk(crosswalk)
        _require(
            release is not None and shp is not None, "Crosswalk needs release and SHP"
        )
        _require(
            crosswalk.replicates > 0
            and all(
                r.reference in CROSSWALK_REFERENCES and r.r in RELIABILITIES
                for r in crosswalk.ranges
            ),
            "Unknown crosswalk reference",
        )
    thresholds = objects["thresholds"]
    if thresholds is not None:
        thresholds = _fields(
            thresholds,
            {"cell_lower", "cell_upper", "pooled_lower", "pooled_upper"},
            "thresholds",
        )
        thresholds = {k: _decode(v, float, k) for k, v in thresholds.items()}
    event = objects["release_event"]
    receipt = None
    if event is not None:
        event = _fields(event, {"condition", "released_utc"}, "release event")
        _require(
            release is not None
            and event["condition"] in {"inventory-complete", "declared-close"},
            "Invalid release event",
        )
        _require(
            isinstance(event["released_utc"], str)
            and re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", event["released_utc"]
            )
            is not None,
            "Invalid release time",
        )
        actual = datetime.fromisoformat(event["released_utc"])
        _require(actual.tzinfo == UTC, "Public release time must be UTC")
        _require(
            len(sources.get("curves", []))
            == len(sources.get("release_record", []))
            == 1,
            "Release source hashes missing",
        )
        receipt = ReleaseRecord(
            "",
            sources["release_record"][0],
            event["condition"],
            event["released_utc"],
            sources["curves"][0],
        )
    _require((release is None) == (receipt is None), "Release event missing")
    gate = _load_gate(objects["gate"])
    _require(release is not None or gate is not None, "Nothing to report")
    return PublicAggregates(
        Loaded(release, gate, None, shp, crosswalk, thresholds, receipt),
        _decode(data["synthetic"], bool, "synthetic"),
        sources,
    )


def _source_hashes(inputs: Inputs, loaded: Loaded) -> dict[str, list[str]]:
    output: dict[str, list[str]] = {}

    def add(role: str, path: Path) -> None:
        if path.is_file():
            output.setdefault(role, []).append(sha256(path))

    for role in (
        "curves",
        "release_record",
        "shp",
        "crosswalk",
        "criteria",
        "allocation",
    ):
        path = getattr(inputs, role)
        if role == "release_record" and inputs.curves is not None:
            path = path or inputs.curves.with_name("release-record.json")
        if path is not None:
            add(role, path)
    for path in inputs.successors:
        add("stage_successors", path)
    if inputs.gate_root is not None and loaded.gate is not None:
        root = inputs.gate_root
        add("gate_criteria", root / "criteria.jsonl")
        for stage in GATE_STAGES:
            add(f"gate_{stage}_authorization", root / f"authorization-{stage}.json")
            for task in gate_tasks(
                stage,
                **(
                    {}
                    if loaded.gate.g2_cells is None
                    else {"cells": loaded.gate.g2_cells}
                ),
            ):
                add(f"gate_{stage}_results", root / task.key / "result.json")
                if stage in {"G0", "G1b"}:
                    add(f"gate_{stage}_seals", root / task.key / "seal.json")
    return {role: sorted(values) for role, values in output.items()}


def project(inputs: Inputs, out: Path, *, synthetic: bool = False) -> Path:
    """Validate through the authorized reader and publish a new derived file."""
    _require(inputs.public_aggregates is None, "Project requires authorized inputs")
    loaded = load_inputs(inputs, synthetic=synthetic)
    event = loaded.release_record
    objects = {
        "release": _release_object(loaded.release),
        "gate": _gate_object(loaded.gate),
        "shp": None if loaded.shp is None else asdict(loaded.shp),
        "crosswalk": None if loaded.crosswalk is None else asdict(loaded.crosswalk),
        "thresholds": loaded.thresholds,
        "release_event": None
        if event is None
        else {"condition": event.condition, "released_utc": event.released_utc},
    }
    here = Path(__file__).resolve().parent
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "notice": NOTICE,
        "synthetic": synthetic,
        "code": {
            **code_commit(),
            "modules_sha256": {
                name: sha256(here / name)
                for name in (
                    "v4_public_aggregates.py",
                    "detection_v4_report.py",
                    "v4_report_schema.py",
                )
            },
        },
        "source_hashes": _source_hashes(inputs, loaded),
        "objects": objects,
        "objects_sha256": {k: digest(v) for k, v in objects.items()},
    }
    record["sha256"] = digest(record)
    content = (
        json.dumps(
            record, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    )
    _parse_public(json.loads(content))
    with out.open("x", encoding="utf-8") as stream:
        stream.write(content)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    projection = commands.add_parser("project")
    add_input_arguments(projection)
    projection.add_argument("--out", type=Path, required=True)
    projection.add_argument("--synthetic", action="store_true")
    args = parser.parse_args(argv)
    project(parse_inputs(projection, args), args.out, synthetic=args.synthetic)
    print(f"Public aggregates written: {args.out}. {NOTICE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
