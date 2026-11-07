"""Derive assembly facts from validated public aggregates, before shell audit.

No SHP report can distinguish not-run, a fit that stopped before writing its
report, or a divergence recorded before execution. Those states, the public
reason/divergence record and observation at close remain Owner declarations.
Only admissible and parameter-bound are decidable from an emitted SHP report.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
from contextlib import redirect_stdout
from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from typing import Any

from ic_study.analysis.detection_v4_report import (
    Inputs,
    add_input_arguments,
    load_inputs,
    parse_inputs,
)
from ic_study.analysis.v4_manuscript_assembly import (
    _permitted,
    load_facts,
)
from ic_study.analysis.v4_manuscript_assembly import (
    main as assembly_main,
)
from ic_study.analysis.v4_manuscript_assembly_facts import (
    FACTS_SCHEMA,
    merge_facts,
    unique_object,
    validate_facts,
)
from ic_study.analysis.v4_report_protocol import protocol
from ic_study.analysis.v4_report_schema import VALID, Boundary, GateRecords, parse_shp
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES

SHELL_BLOCKS = {
    "tier2.boundaries_differ": "B06",
    "main.boundary_nonmonotone": "B07",
    "shp.state": "B14",
    "shp.grid_position": "B13",
    "gate.G0.failed_criteria": "B1b-G0",
    "gate.G1c.failed_criteria": "B1b-G1c",
    "gate.G2.failed_criteria": "B1b-G2",
    "gate.G2c.failed_comparisons": "B1b-G2c",
}


def _digest(path: Path) -> str:
    return hashlib.sha256(_permitted(path).read_bytes()).hexdigest()


def _public_inputs(inputs: Inputs) -> Inputs:
    paths = {
        name: None if (path := getattr(inputs, name)) is None else _permitted(path)
        for name in (
            "curves",
            "gate_root",
            "shp",
            "criteria",
            "crosswalk",
            "allocation",
            "release_record",
        )
    }
    checked = replace(
        inputs, **paths, successors=tuple(_permitted(p) for p in inputs.successors)
    )
    if checked.curves is not None and checked.release_record is None:
        checked = replace(
            checked,
            release_record=_permitted(checked.curves.with_name("release-record.json")),
        )
    if checked.gate_root is not None and checked.gate_root.is_dir():
        # The report loader follows root-level metadata and task result/seal files.
        for child in checked.gate_root.iterdir():
            _permitted(child)
            if child.is_dir():
                _permitted(child / "result.json")
                _permitted(child / "seal.json")
    return checked


def _tuple(boundary: Boundary) -> tuple[object, ...]:
    return (
        boundary.point,
        boundary.interval,
        boundary.censoring,
        boundary.interval_censoring,
    )


def _number(record: dict[str, Any], key: str, *, integer: bool = False) -> float:
    value = record.get(key)
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        or value < 0
        or (integer and type(value) is not int)
    ):
        raise ValueError("Invalid aggregate number: " + key)
    return float(value)


def _flag(record: dict[str, Any], key: str) -> bool:
    value = record.get(key)
    if type(value) is not bool:
        raise ValueError("Invalid aggregate boolean: " + key)
    return bool(value)


def _g2_failures(
    summary: dict[str, Any], thresholds: dict[str, float] | None
) -> list[str] | None:
    ratios = summary.get("cell_ratios")
    if not isinstance(ratios, list):
        raise ValueError("Invalid aggregate cell_ratios")
    failed = []
    if not _flag(summary, "failure_allowance_met"):
        failed.append("allowance")
    if ratios:
        if thresholds is None:
            return None
        lower, upper = summary.get("cell_lower"), summary.get("cell_upper")
        if (
            not isinstance(lower, list)
            or not isinstance(upper, list)
            or len(lower) != len(ratios)
            or len(upper) != len(ratios)
        ):
            raise ValueError("G2 intervals must align with cell_ratios")
        lows = [_number({"value": v}, "value") for v in lower]
        highs = [_number({"value": v}, "value") for v in upper]
        pooled_lo, pooled_hi = (
            _number(summary, "pooled_lower"),
            _number(summary, "pooled_upper"),
        )
        if (
            any(lo > hi for lo, hi in zip(lows, highs, strict=True))
            or pooled_lo > pooled_hi
        ):
            raise ValueError("G2 interval endpoints reversed")
        if (
            any(v > thresholds["cell_upper"] for v in lows)
            or pooled_lo > thresholds["pooled_upper"]
        ):
            failed.append("above")
        if (
            any(v < thresholds["cell_lower"] for v in highs)
            or pooled_hi < thresholds["pooled_lower"]
        ):
            failed.append("below")
    if not _flag(summary, "fd_stable"):
        failed.append("fd")
    if not ratios:
        failed.append("insufficient")
    return failed


def _gate_failures(
    gate: GateRecords, thresholds: dict[str, float] | None
) -> dict[str, list[str]]:
    result = {}
    p = protocol()
    for stage in ("G0", "G1c", "G2", "G2c"):
        if gate.verdict(stage) != "fail":
            continue
        summary = gate.summaries[stage]
        failed: list[str] | None = None
        suffix = "failed_criteria"
        if stage == "G0" and "fits" in summary:
            fits = _number(summary, "fits", integer=True)
            if not fits:
                raise ValueError("G0 criteria require fits")
            failed = [
                name
                for name, yes in (
                    ("anchor", _number(summary, "anchor_failures", integer=True) > 0),
                    ("budget", _number(summary, "budget_statuses", integer=True) > 0),
                    (
                        "implementation",
                        _number(summary, "implementation_statuses", integer=True) / fits
                        > p.g0_implementation_limit,
                    ),
                )
                if yes
            ]
        elif stage == "G1c" and "anchor_count" in summary:
            failed = [
                name
                for name, yes in (
                    ("anchor", summary["anchor_count"] < p.g1c_fits),
                    (
                        "pointwise",
                        summary["pointwise_failures"] > p.g1c_pointwise_limit,
                    ),
                    ("mean", summary["mean_z"] > p.g1c_mean_z_limit),
                )
                if yes
            ]
        elif stage == "G2" and "cell_ratios" in summary:
            failed = _g2_failures(summary, thresholds)
        elif stage == "G2c" and "comparisons" in summary:
            comparisons = summary["comparisons"]
            if (
                not isinstance(comparisons, list)
                or len(comparisons) != 2
                or any(not isinstance(c, dict) for c in comparisons)
            ):
                raise ValueError("G2c requires its two ordered comparisons")
            if any("ratio" not in c for c in comparisons):
                continue
            failed = []
            for name, a, comparison in zip(
                ("a010", "a003"), (0.1, 0.03), comparisons, strict=True
            ):
                count = p.g2c_refits[a]
                if _number(comparison, "denominator", integer=True) != count:
                    raise ValueError("G2c comparison order/denominator differs")
                _number(comparison, "ratio")
                failures = _number(comparison, "failure_count", integer=True)
                lower, upper = (
                    _number(comparison, "lower"),
                    _number(comparison, "upper"),
                )
                if failures > count or lower > upper:
                    raise ValueError("G2c counts or interval endpoints differ")
                bad = (
                    failures > p.g2c_failure_allowances[count]
                    or upper < p.g2c_upper_minimum
                    or lower > p.g2c_lower_maximum
                )
                if _flag(comparison, "pass") == bad:
                    raise ValueError("G2c pass differs from its aggregate predicate")
                if bad:
                    failed.append(name)
            suffix = "failed_comparisons"
        if failed is not None:
            if not failed:
                raise ValueError(stage + " failed without a failed aggregate criterion")
            result[f"gate.{stage}.{suffix}"] = failed
    return result


def _gate_source(inputs: Inputs, gate: GateRecords, stage: str) -> tuple[str, str, str]:
    if stage in gate.from_successor:
        item = next(s for s in gate.successors if s.stage == stage)
        return item.name, "/summary", item.sha256
    assert inputs.gate_root is not None and gate.criteria_sha256 is not None
    path = inputs.gate_root / "criteria.jsonl"
    lines = path.read_text().splitlines()
    line = max(
        i for i, raw in enumerate(lines, 1) if json.loads(raw) == gate.summaries[stage]
    )
    return path.name, f"JSONL line {line} (gate={stage})", gate.criteria_sha256


def derive_facts(inputs: Inputs, *, synthetic: bool = False) -> dict[str, Any]:
    """Load through the report validator and derive only decidable raw facts."""
    inputs = _public_inputs(inputs)
    loaded = load_inputs(inputs, synthetic=synthetic)
    facts: dict[str, Any] = {}

    def add(name: str, value: object, record: str, locator: str, digest: str) -> None:
        facts[name] = {
            "value": value,
            "source": {
                "record": record,
                "locator": locator + "; Results shell block " + SHELL_BLOCKS[name],
                "sha256": digest,
            },
        }

    release = loaded.release
    if release is not None:
        assert inputs.curves is not None and loaded.release_record is not None
        origin = inputs.curves.name, loaded.release_record.curves_sha256
        different = any(
            _tuple(c.first) != _tuple(c.sustained)
            for c in release.curves.values()
            if c.meta.tier == 2 and c.status == VALID
        )
        add(
            "tier2.boundaries_differ",
            different,
            origin[0],
            "/curves; any VALID tier-2 first/sustained four-tuples differ",
            origin[1],
        )
        ordered = []
        for curve in sorted(release.curves.values(), key=lambda c: c.meta.r):
            if curve.meta.tier != 1 or curve.status != VALID:
                continue
            if curve.first.point is not None:
                ordered.append(GRID.index(curve.first.point))
            elif curve.first.censoring is None:
                ordered.append(len(GRID))
        monotone = all(a <= b for a, b in pairwise(ordered)) or all(
            a >= b for a, b in pairwise(ordered)
        )
        add(
            "main.boundary_nonmonotone",
            not monotone,
            origin[0],
            "/curves; defined ordinals by r: idx(first) if ATT, "
            "9 if uncensored null, otherwise omitted",
            origin[1],
        )
    if loaded.shp is not None:
        assert inputs.shp is not None
        content = inputs.shp.read_bytes()
        raw = json.loads(content, object_pairs_hook=unique_object)
        if parse_shp(raw) != loaded.shp:
            raise ValueError("SHP aggregate changed during derivation")
        multiwave = raw.get("multiwave")
        if not isinstance(multiwave, dict) or not _flag(multiwave, "converged"):
            raise ValueError("An emitted SHP report requires a converged primary fit")
        bound = _flag(multiwave, "at_parameter_bound")
        digest = hashlib.sha256(content).hexdigest()
        add(
            "shp.state",
            "parameter-bound" if bound else "admissible",
            inputs.shp.name,
            "/multiwave/at_parameter_bound",
            digest,
        )
        if not bound and release is not None:
            anchor = loaded.shp
            lo, hi = RELIABILITIES[0], RELIABILITIES[-1]
            position = (
                "below"
                if anchor.estimate < lo
                else "above"
                if anchor.estimate > hi
                else "interval-outside"
                if anchor.wald_95_interval[0] < lo or anchor.wald_95_interval[1] > hi
                else "inside"
            )
            add(
                "shp.grid_position",
                position,
                inputs.shp.name,
                "/anchor; compare estimate then Wald endpoints with inclusive "
                "[0.50,0.90], without rounding",
                digest,
            )
    if loaded.gate is not None:
        for name, value in _gate_failures(loaded.gate, loaded.thresholds).items():
            record, locator, digest = _gate_source(
                inputs, loaded.gate, name.split(".")[1]
            )
            if name == "gate.G2.failed_criteria" and inputs.criteria is not None:
                locator += (
                    f"; thresholds /thresholds in {inputs.criteria.name} "
                    f"sha256={_digest(inputs.criteria)}"
                )
            add(
                name,
                value,
                record,
                locator + "; exact failed clauses over unrounded aggregates",
                digest,
            )
    return validate_facts(
        {"schema": FACTS_SCHEMA, "synthetic": synthetic, "facts": facts}
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_input_arguments(parser)
    parser.add_argument("--owner-facts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--confirmatory-values", type=Path, required=True)
    parser.add_argument("--exploratory-values", type=Path)
    parser.add_argument("--manuscript", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.public_aggregates is not None:
            raise ValueError("Derivation needs the authorized released inputs")
        output = _permitted(args.out)
        if output.exists():
            raise ValueError("Facts output must be a new file")
        derived = derive_facts(parse_inputs(parser, args), synthetic=args.synthetic)
        merged = merge_facts(load_facts(args.owner_facts), derived)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(
                json.dumps(merged, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
            )
        audit_args = [
            "--audit-only",
            "--confirmatory-values",
            str(args.confirmatory_values),
            "--assembly-facts",
            str(output),
            "--manuscript",
            str(args.manuscript),
        ]
        if args.exploratory_values:
            audit_args += ["--exploratory-values", str(args.exploratory_values)]
        captured = io.StringIO()
        with redirect_stdout(captured):
            code = assembly_main(audit_args)
        audit = json.loads(captured.getvalue())
        refusals = [d for d in audit.get("decisions", []) if d["state"] == "refused"]
        missing = sorted(
            {
                name
                for d in refusals
                for name in re.findall(r"Missing assembly fact: ([\w.]+)", d["reason"])
            }
        )
        refusal = audit.get("error") or (
            "Assembly refused: "
            + "; ".join(
                f"{d['id']} ({d['source']}:{d['line']}): {d['reason']}"
                for d in refusals
            )
            if refusals
            else None
        )
        print(
            json.dumps(
                {
                    "facts_output": str(output),
                    "derived_facts": sorted(derived["facts"]),
                    "missing_facts": missing,
                    "refusal": refusal,
                    "assembly_audit": audit,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return code
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
