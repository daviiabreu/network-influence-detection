"""Pure exploratory comparisons with the released tier-1 B observed curve."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ic_study.analysis.v4_report_schema import (
    VALID,
    Boundary,
    Release,
    load_release_record,
    parse_release,
    unit_catalog,
)
from ic_study.simulation.detection_v4 import GRID
from ic_study.simulation.v4_exploratory_x4 import SINGLE_RELIABILITIES

AVAILABLE = "disponível"
UNAVAILABLE = "indisponível"
OUTSIDE_DOMAIN = "fora do domínio declarado"
LABEL = "exploratory"
SCHEMA = "ic-study.v4-exploratory-comparisons.v1"


def _unavailable(reason: str, **fields: Any) -> dict[str, Any]:
    return {**fields, "state": UNAVAILABLE, "reason": reason}


def _boundary_view(boundary: Boundary, status: str) -> dict[str, Any]:
    reason = None
    if status != VALID:
        reason = f"unidade: {status}"
    elif boundary.point is None:
        reason = (
            f"censurada por lacuna em a = {boundary.censored_at:g}"
            if boundary.censored_at is not None
            else "não atingida na grade"
        )
    return {
        "state": AVAILABLE if reason is None else UNAVAILABLE,
        "reason": reason,
        "point": boundary.point,
        "interval": None if boundary.interval is None else list(boundary.interval),
        "censoring": boundary.censoring,
        "interval_censoring": boundary.interval_censoring,
        "censored_at": boundary.censored_at,
    }


def main_curves(release: Release) -> dict[float, dict[str, Any]]:
    """Project the validated release onto the principal curve, including missing r."""
    result: dict[float, dict[str, Any]] = {}
    for meta in unit_catalog().values():
        if (meta.tier, meta.family, meta.channel, meta.sensitivity) != (
            1,
            "B",
            "observed",
            "main",
        ):
            continue
        status = release.statuses[meta.key]
        curve = release.curves.get(meta.key)
        missing = Boundary(None, None, None, None)
        result[meta.r] = {
            "label": "confirmatory",
            "unit": meta.key,
            "tier": meta.tier,
            "family": meta.family,
            "channel": meta.channel,
            "sensitivity": meta.sensitivity,
            "r": meta.r,
            "unit_status": status,
            "main_curve_valid": release.main_curve_valid,
            "valid_null_gate": None if curve is None else curve.valid_null_gate,
            "gap_count": None if curve is None else curve.gap_count,
            "first": _boundary_view(missing if curve is None else curve.first, status),
            "sustained": _boundary_view(
                missing if curve is None else curve.sustained, status
            ),
            "available_strengths": [] if curve is None else list(curve.available),
            "auc": [] if curve is None else list(curve.auc),
            "lower": [] if curve is None else list(curve.lower),
            "upper": [] if curve is None else list(curve.upper),
        }
        result[meta.r].update(
            state=result[meta.r]["first"]["state"],
            reason=result[meta.r]["first"]["reason"],
        )
    return result


def equivalent_strength(
    curve: Mapping[str, Any], estimate: Mapping[str, Any]
) -> dict[str, Any]:
    """First point-AUC crossing on G; a preceding gap censors the crossing."""
    fields = {"point": None, "censored_at": None}
    if curve["unit_status"] != VALID:
        return _unavailable(f"unidade principal: {curve['unit_status']}", **fields)
    areas = dict(zip(curve["available_strengths"], curve["auc"], strict=True))
    for strength in GRID:
        if strength not in areas:
            return {
                **fields,
                "state": "censurada",
                "reason": f"censurada por lacuna em a = {strength:g}",
                "censored_at": strength,
            }
        if areas[strength] >= estimate["auc"]:
            return {**fields, "state": AVAILABLE, "reason": None, "point": strength}
    return {**fields, "state": "acima da grade", "reason": "acima da grade"}


def interval_comparison(
    curve: Mapping[str, Any], estimate: Mapping[str, Any]
) -> dict[str, Any]:
    """Compare interval_27729 with the released band at the first point boundary."""
    first = curve["first"]
    fields = {
        "a": first["point"],
        "relation": None,
        "x5_interval_27729": copy.deepcopy(estimate["interval_27729"]),
        "confirmatory_band": None,
    }
    if first["state"] != AVAILABLE:
        return _unavailable(first["reason"], **fields)
    index = curve["available_strengths"].index(first["point"])
    lower, upper = curve["lower"][index], curve["upper"][index]
    lo, hi = estimate["interval_27729"]
    relation = "acima" if lo > upper else "abaixo" if hi < lower else "sobrepõe"
    return {
        **fields,
        "state": AVAILABLE,
        "reason": None,
        "relation": relation,
        "confirmatory_band": [lower, upper],
    }


def _one(records: Sequence[dict[str, Any]]) -> dict[str, Any] | None:
    if len(records) > 1:
        raise ValueError("Duplicate aggregate cell or unit")
    return records[0] if records else None


def _cell(
    records: Sequence[dict[str, Any]], r: float, a: float
) -> dict[str, Any] | None:
    return _one([c for c in records if c["cell"]["r"] == r and c["cell"]["a"] == a])


def _x1b(r: float, aggregate: Mapping[str, Any] | None) -> dict[str, Any]:
    if aggregate is None:
        return _unavailable("agregado X1b não fornecido", label=LABEL)
    summary = _one([u for u in aggregate["summary"] if u["r"] == r])
    if summary is None:
        return _unavailable("unidade X1b ausente no agregado", label=LABEL)
    curve = _one([c for c in aggregate["curves"] if c["unit"] == summary["unit"]])
    if curve is None:
        return _unavailable("curva X1b ausente no agregado", label=LABEL)
    status = curve["status"]
    result = {
        "label": LABEL,
        "unit": curve["unit"],
        "unit_status": status,
        "valid_null_gate": curve.get("valid_null_gate"),
        "gap_count": curve.get("gap_count"),
        "errors": copy.deepcopy(curve.get("errors")),
    }
    for kind in ("first", "sustained"):
        interval = curve.get(f"{kind}_interval")
        result[kind] = _boundary_view(
            Boundary(
                curve.get(kind),
                None if interval is None else tuple(interval),
                curve.get(f"{kind}_censoring"),
                curve.get(f"{kind}_interval_censoring"),
                sustained=kind == "sustained",
            ),
            status,
        )
    result.update(state=result["first"]["state"], reason=result["first"]["reason"])
    return result


def _x5(
    r: float, curve: Mapping[str, Any], aggregate: Mapping[str, Any] | None
) -> list[dict[str, Any]]:
    if aggregate is None:
        return []
    result = []
    for condition in aggregate["conditions"]:
        cell = _one(
            [
                c
                for c in aggregate["cells"]
                if c["r"] == r and c["channel"]["name"] == condition["name"]
            ]
        )
        reason = None
        if cell is None:
            reason = "célula X5 ausente no agregado"
        elif not cell["success"] or cell["estimate"] is None:
            reason = f"X5: {cell['reading']}"
        entry: dict[str, Any] = (
            copy.deepcopy(cell) if cell is not None else {"channel": dict(condition)}
        )
        entry.update(
            label=LABEL,
            state=AVAILABLE if reason is None else UNAVAILABLE,
            reason=reason,
        )
        if reason is not None:
            entry["equivalent_strength"] = _unavailable(
                reason, point=None, censored_at=None
            )
            entry["interval_comparison"] = _unavailable(
                reason, relation=None, a=curve["first"]["point"]
            )
        else:
            assert cell is not None
            entry["equivalent_strength"] = equivalent_strength(curve, cell["estimate"])
            entry["interval_comparison"] = interval_comparison(curve, cell["estimate"])
        result.append(entry)
    return result


def _x3(
    r: float, curve: Mapping[str, Any], aggregate: Mapping[str, Any] | None
) -> dict[str, Any]:
    first = curve["first"]
    fields = {"label": LABEL, "a": first["point"], "reading": None, "delta": None}
    if first["state"] != AVAILABLE:
        return _unavailable(first["reason"], **fields)
    if first["point"] == 0:
        return {
            **fields,
            "state": OUTSIDE_DOMAIN,
            "reason": "X3 não declara célula em a = 0",
        }
    if aggregate is None:
        return _unavailable("agregado X3 não fornecido", **fields)
    cell = _cell(aggregate["cells"], r, first["point"])
    if cell is None:
        return _unavailable("célula X3 ausente no agregado", **fields)
    selected = {**fields, **copy.deepcopy(cell)}
    if cell["reading"] in {"error", "gap", "free-gap"}:
        return _unavailable(f"X3: {cell['reading']}", **selected)
    return {**selected, "state": AVAILABLE, "reason": None}


def _statistics(cell: Mapping[str, Any], kind: str) -> dict[str, Any] | None:
    statistics = cell.get(kind)
    return (
        None
        if statistics is None
        else copy.deepcopy({k: v for k, v in statistics.items() if k != "panels"})
    )


def _x4_reference(
    r: float, curve: Mapping[str, Any], aggregate: Mapping[str, Any] | None, kind: str
) -> dict[str, Any]:
    first = curve["first"]
    fields = {"label": LABEL, "a": first["point"], "quantity": None, "statistics": None}
    if kind == "x4b" and r not in SINGLE_RELIABILITIES:
        return {
            **fields,
            "state": OUTSIDE_DOMAIN,
            "reason": "X4b declara apenas r em {0.50, 0.70, 0.90}",
        }
    if first["state"] != AVAILABLE:
        return _unavailable(first["reason"], **fields)
    if aggregate is None:
        return _unavailable("agregado X4 não fornecido", **fields)
    cell = _cell(aggregate[kind], r, first["point"])
    if cell is None:
        return _unavailable(f"célula {kind.upper()} ausente no agregado", **fields)
    fields.update(
        statistics=_statistics(cell, kind),
        quantity=cell.get("quantity"),
        quantity_reason=None
        if "quantity" in cell
        else f"agregado {kind.upper()} não fornece rótulo de quantidade",
        size_flag=cell.get("size_flag"),
        attempts=copy.deepcopy(cell["attempts"]),
        error=copy.deepcopy(cell["error"]),
        normal_theory_reading=cell.get("normal_theory_reading"),
        single_panel_reading=cell.get("single_panel_reading"),
    )
    if cell["error"] is not None or not cell["success"] or fields["statistics"] is None:
        return _unavailable(
            f"{kind.upper()}: erro ou lacuna do ajuste congelado", **fields
        )
    return {**fields, "state": AVAILABLE, "reason": None}


def _x4(
    r: float, curve: Mapping[str, Any], aggregate: Mapping[str, Any] | None
) -> dict[str, Any]:
    calibration: dict[str, dict[str, Any]] = {}
    for kind in ("x4a", "x4b"):
        if kind == "x4b" and r not in SINGLE_RELIABILITIES:
            calibration[kind] = {
                "state": OUTSIDE_DOMAIN,
                "reason": "X4b declara apenas r em {0.50, 0.70, 0.90}",
                "flag": None,
                "statistics": None,
            }
            continue
        cell = None if aggregate is None else _cell(aggregate[kind], r, 0.0)
        flag = (
            None
            if aggregate is None
            else aggregate["summary"]["size_at_a0"][kind].get(str(r))
        )
        statistics = None if cell is None else _statistics(cell, kind)
        calibration[kind] = {
            "state": AVAILABLE
            if flag is not None and statistics is not None
            else UNAVAILABLE,
            "reason": None
            if flag is not None and statistics is not None
            else "marca de calibração em a = 0 indisponível",
            "flag": flag,
            "statistics": statistics,
        }
    oracle = _x4_reference(r, curve, aggregate, "x4a")
    fitted = _x4_reference(r, curve, aggregate, "x4b")
    available = sum(item["state"] == AVAILABLE for item in (oracle, fitted))
    return {
        "label": LABEL,
        "state": AVAILABLE
        if available == 2
        else "parcial"
        if available
        else UNAVAILABLE,
        "reason": None if available == 2 else oracle["reason"] or fitted["reason"],
        "a": curve["first"]["point"],
        "P_or": oracle,
        "P_pu": fitted,
        "calibration": calibration,
        "sizes": None if aggregate is None else copy.deepcopy(aggregate["sizes"]),
        "rules": None if aggregate is None else copy.deepcopy(aggregate["rules"]),
    }


def compare_exploratory(
    main_by_r: Mapping[float, Mapping[str, Any]],
    *,
    x1b: Mapping[str, Any] | None = None,
    x5: Mapping[str, Any] | None = None,
    x3: Mapping[str, Any] | None = None,
    x4: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Read already-loaded aggregates without fitting, testing or mutating inputs."""
    return {
        "schema": SCHEMA,
        "label": LABEL,
        "by_r": {
            str(r): {
                "r": r,
                "main_curve": copy.deepcopy(dict(curve)),
                "x1b": _x1b(r, x1b),
                "x5_state": {
                    "state": AVAILABLE if x5 is not None else UNAVAILABLE,
                    "reason": None if x5 is not None else "agregado X5 não fornecido",
                },
                "x5": _x5(r, curve, x5),
                "x3": _x3(r, curve, x3),
                "x4": _x4(r, curve, x4),
            }
            for r, curve in sorted(main_by_r.items())
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curves", type=Path, required=True)
    parser.add_argument("--release-record", type=Path)
    for name in ("x1b", "x5", "x3", "x4"):
        parser.add_argument(f"--{name}", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        content = args.curves.read_bytes()
        release = parse_release(json.loads(content))
        receipt_path = args.release_record or args.curves.with_name(
            "release-record.json"
        )
        receipt = load_release_record(receipt_path, content, release)
        provenance: dict[str, Any] = {
            "curves": {"name": args.curves.name, "sha256": receipt.curves_sha256},
            "release_record": {"name": receipt.name, "sha256": receipt.sha256},
        }
        aggregates: dict[str, Any] = {}
        for name in ("x1b", "x5", "x3", "x4"):
            path = getattr(args, name)
            aggregates[name] = None
            provenance[name] = None
            if path is not None:
                raw = path.read_bytes()
                value = json.loads(raw)
                if (
                    not isinstance(value, dict)
                    or value.get("schema") != f"ic-study.v4-exploratory-{name}.v1"
                ):
                    raise ValueError("Unexpected aggregate schema")
                aggregates[name] = value
                provenance[name] = {
                    "name": path.name,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
        result = compare_exploratory(main_curves(release), **aggregates)
        result["provenance"] = {"inputs": provenance, "release": asdict(receipt)}
        encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(encoded)
    except (OSError, ValueError, KeyError, TypeError):
        print(
            "Falha nas entradas ou na gravação; "
            "use entradas liberadas válidas e uma saída nova.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
