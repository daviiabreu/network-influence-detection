"""Tables T1, T3 and T4 for the a*(r) paper, emitted as CSV and booktabs LaTeX.

Every cell is formatted once as a string and written verbatim to both files
(LaTeX only escapes it), so the two formats always carry the same numbers.
T2 (contrasts) is not emitted: the frozen protocol defines no between-family
contrast quantity (see ``report/README.md``).
"""

from __future__ import annotations

import csv
import io
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from ic_study.analysis.v4_report_protocol import protocol
from ic_study.analysis.v4_report_schema import (
    CALIBRATION_EXPOSED_R,
    FAMILIES,
    GAP_KINDS,
    GATE_STAGES,
    MAIN_CURVE_INVALID,
    SECONDARY_TARGETS,
    SMALL_LARGE_CUT,
    STATUSES,
    SUCCESSOR_SOURCE,
    VALID,
    Boundary,
    Curve,
    GateRecords,
    Release,
    unit_catalog,
)
from ic_study.simulation.detection_v4 import GRID
from ic_study.simulation.v4_plan import SCENARIOS

NA = "NA"
BEYOND = ">0.9"
STOPPED = "stopped"
_TEX = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    ">": r"\textgreater{}",
    "<": r"\textless{}",
}


@dataclass(frozen=True)
class Table:
    name: str
    header: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    notes: tuple[str, ...]
    long: bool = False


def tex_escape(text: str) -> str:
    return "".join(_TEX.get(ch, ch) for ch in text)


def strength(value: float | None) -> str:
    return NA if value is None else f"{value:g}"


def number(value: float | None, digits: int = 3) -> str:
    if value is None or not math.isfinite(value):
        return NA
    return f"{value:.{digits}f}"


def boundary_cells(curve: Curve, boundary: Boundary) -> tuple[str, str, str]:
    """Point, lower and upper interval endpoint under the frozen censoring rules."""
    if curve.status != VALID:
        return "suppressed", NA, NA
    if boundary.point is not None:
        point = strength(boundary.point)
    elif boundary.censored_at is not None:
        point = f"censored at gap a={boundary.censored_at:g}"
    else:
        point = f"not reached ({BEYOND})"
    ends: list[str] = []
    for index, value in enumerate(boundary.interval or (None, None)):
        cut = boundary.end_censored_at(index)
        if value is not None:
            ends.append(strength(value))
        elif cut is not None:
            ends.append(f"censored at gap a={cut:g}")
        else:
            ends.append(BEYOND)
    return point, ends[0], ends[1]


def region(curve: Curve) -> str:
    """Frozen v1 region of the first a*, with its interval deciding "IC amplo".

    Small is 0 < a* <= 0.03 and large 0.03 < a* <= 0.9; not attained holds on the
    complete eligible grid. Otherwise the region is censored (gap) or
    indeterminate: a* = 0, or an interval that crosses 0.03 or has a censored end.
    """
    if curve.status != VALID:
        return NA
    point = curve.first.point
    if point is None:
        return "censored (gap)" if curve.first.censoring else "not attained"
    lower, upper = curve.first.interval or (None, None)
    if point == 0 or lower is None or upper is None or lower <= SMALL_LARGE_CUT < upper:
        return "indeterminate"
    return "small" if point <= SMALL_LARGE_CUT else "large"


def _target_label(target: float) -> str:
    return f"{round(target * 100):03d}"


T1_HEADER = (
    "tier",
    "family",
    "channel",
    "sensitivity",
    "r",
    "exposure",
    "main_curve_flag",
    "status",
    "null_gate",
    "gaps",
    *(f"gaps_{kind}" for kind in GAP_KINDS),
    "a_star",
    "a_star_lower",
    "a_star_upper",
    "a_s_star",
    "a_s_star_lower",
    "a_s_star_upper",
    "region",
    *(
        f"derived_a_star_{_target_label(target)}{suffix}"
        for target in SECONDARY_TARGETS
        for suffix in ("", "_lower", "_upper")
    ),
    "nonmonotone_band",
    "critical",
    "max_t_above_floor",
)


def _t1_row(release: Release, key: str) -> tuple[str, ...]:
    meta = unit_catalog()[key]
    status = release.statuses[key]
    exposure = "calibration-exposed" if meta.r == CALIBRATION_EXPOSED_R else ""
    flag = MAIN_CURVE_INVALID if meta.tier == 1 and not release.main_curve_valid else ""
    lead = (
        str(meta.tier),
        meta.family,
        meta.channel,
        meta.sensitivity,
        f"{meta.r:.2f}",
        exposure,
        flag,
        status,
    )
    curve = release.curves.get(key)
    if curve is None:
        return lead + (NA,) * (len(T1_HEADER) - len(lead))
    flags = (
        NA
        if curve.nonmonotone_band is None
        else ("yes" if curve.nonmonotone_band else "no"),
        number(curve.critical, 4),
        NA
        if curve.empirical_exceeds_floor is None
        else ("yes" if curve.empirical_exceeds_floor else "no"),
    )
    gaps = curve.gap_counts()
    return (
        *lead,
        "pass" if curve.valid_null_gate else "fail",
        str(curve.gap_count),
        *(str(gaps[kind]) for kind in GAP_KINDS),
        *boundary_cells(curve, curve.first),
        *boundary_cells(curve, curve.sustained),
        region(curve),
        *(
            cell
            for derived in curve.secondary
            for cell in boundary_cells(curve, derived)
        ),
        *flags,
    )


_T1_NOTES = (
    "Publication T1 reports the primary-target boundaries, both first and "
    "sustained, their intervals, status, null gate, gaps and region. The report "
    "CSV retains all columns; secondary-target columns enter only the "
    "supplementary secondary-target table, never Results or the headline.",
    "Families: B = trait-plus-autoregressive persistence (confirmatory); "
    "A = autoregressive "
    "persistence; C = autoregressive persistence with an altered response "
    "channel; D = state-dependent persistence; E = mover--stayer persistence. "
    "r is the continuous response signal share; a is nominal partner-drift "
    "strength before rank transport.",
    "a* = min{a in G: AUC(a,r) >= 0.70}; a_s* = sustained boundary; intervals by "
    "inclusive inversion of the per-r band (simultaneous over the nine strengths of "
    "one r only, not over 81 cells).",
    f"{BEYOND}: not reached on the complete eligible grid (right-censored); a "
    f"sustained upper end above the last gap is {BEYOND} (suffix minimum), never "
    "censored at a gap below it. 'censored at gap': frozen gap-censoring rule. "
    "'suppressed': failed a=0 null gate.",
    f"main_curve_flag: '{MAIN_CURVE_INVALID}' on every tier-1 (B) row when some "
    "tier-1 unit is not completo válido; the boundaries stay reported with this "
    "mark (amendment v4).",
    "gaps_*: gap cells by final status. screened = family limit from the "
    "feasibility pre-check with 0 solver evaluations; family_limit = family limit "
    "on the profile; solver = other solver status; validation = accepted status "
    "that failed validation; dependency = control whose observed fit failed; "
    "propagation = ill-conditioned nuisance propagation recorded as a gap by "
    "amendment v4.4. Family limits are gaps, not failures (D7).",
    f"region: small 0<a*<={SMALL_LARGE_CUT:g}; "
    f"large {SMALL_LARGE_CUT:g}<a*<={GRID[-1]:g}; "
    "not attained on the complete "
    "eligible grid; censored (gap); indeterminate when a*=0 or the a* interval "
    f"crosses {SMALL_LARGE_CUT:g} or has a censored end "
    "(coordinator's operationalisation of the "
    "v1 'IC amplo' clause).",
    f"derived_a_star_{min(SECONDARY_TARGETS) * 100:03.0f}/"
    f"{max(SECONDARY_TARGETS) * 100:03.0f}: "
    f"secondary targets {min(SECONDARY_TARGETS):.2f} "
    f"and {max(SECONDARY_TARGETS):.2f} (PR), derived from "
    "released bands with the frozen boundary_report inversion and curve_report "
    "gap censoring; the frozen release emits the 0.70 boundaries only.",
    "r = 0.70 is calibration-exposed (amendment v4, D8).",
    "Grid spacing represents positions, not equal increments of a; no "
    "interpolation. B and D retain all rows; any paired reading uses the "
    "authorized common gap-free set, without a between-family contrast test.",
    "critical = max(empirical max-t, 2.7729); max_t_above_floor reports D6's count.",
)


def table_t1(release: Release) -> Table:
    catalog = unit_catalog()
    keys = sorted(
        (k for k, m in catalog.items() if m.main),
        key=lambda k: (FAMILIES.index(catalog[k].family), catalog[k].r),
    )
    return Table(
        "T1_a_star_grid",
        T1_HEADER,
        tuple(_t1_row(release, k) for k in keys),
        (
            *_T1_NOTES,
            "T1: tier 1 (B, confirmatory) and tier 2 (A, C, D, E), main grid.",
        ),
    )


def table_t1_full(release: Release) -> Table:
    return Table(
        "T1s_a_star_all_units",
        T1_HEADER,
        tuple(_t1_row(release, k) for k in unit_catalog()),
        (
            *_T1_NOTES,
            "T1s: supplementary full records for every unit of the frozen "
            "inventory (D9), including controls, sensitivities and diagnostics.",
        ),
        long=True,
    )


def _inventory_row(
    release: Release, lead: tuple[str, ...], keys: Sequence[str]
) -> tuple[str, ...]:
    statuses = [release.statuses[k] for k in keys]
    gaps = [release.curves[k].gap_counts() for k in keys if k in release.curves]
    return (
        *lead,
        str(len(keys)),
        *(str(statuses.count(status)) for status in STATUSES),
        *(str(sum(counts[kind] for counts in gaps)) for kind in GAP_KINDS),
    )


def table_t4(release: Release) -> Table:
    catalog = unit_catalog()
    groups: dict[tuple[int, str, str, str], list[str]] = {}
    for key, meta in catalog.items():
        groups.setdefault(meta.configuration, []).append(key)
    rows = [
        _inventory_row(release, (str(t), f, c, s), keys)
        for (t, f, c, s), keys in groups.items()
    ]
    for tier in sorted({m.tier for m in catalog.values()}):
        keys = [k for k, m in catalog.items() if m.tier == tier]
        rows.append(_inventory_row(release, (str(tier), "all", "all", "all"), keys))
    rows.append(_inventory_row(release, ("all", "all", "all", "all"), list(catalog)))
    return Table(
        "T4_inventory",
        (
            "tier",
            "family",
            "channel",
            "sensitivity",
            "units",
            *STATUSES,
            *(f"gap_cells_{kind}" for kind in GAP_KINDS),
        ),
        tuple(rows),
        (
            f"Status at the close {release.closed_utc} (D9); "
            "units are (configuration, r).",
            "main_curve_valid (all tier-1 B units completo válido): "
            + ("yes" if release.main_curve_valid else "no"),
            "gap_cells_*: gap cells of the released curves by final status, as in "
            "T1 (family limits are gaps, not failures).",
        ),
    )


def _ratio(value: float, lower: float, upper: float) -> str:
    return f"{number(value)} [{number(lower)}, {number(upper)}]"


def _series(values: Sequence[Any], digits: int | None = None) -> str:
    if not values:
        return "not estimable"
    if digits is None:
        return " ".join(map(str, values))
    return " ".join(number(v, digits) for v in values)


def cell_label(gate: GateRecords, index: int, *, short: bool = False) -> str:
    """G2 cell in allocation order, with (a, r) from the second binding if given."""
    if gate.g2_cells is None:
        return f"cell {index + 1}"
    a, r = gate.g2_cells[index]
    cell = f"a={a:g}, r={r:.2f}"
    return cell if short else f"cell {index + 1} ({cell})"


_TASK_FAILURE_RULE = {
    "G0": "= 0",
    "G1b": "= 0",
    "G1c": "= 0",
    "G2c": "per comparison",
}
_CRITERIA_FIELD = {
    "G0": "fits",
    "G1b": "coverage_counts",
    "G1c": "anchor_count",
    "G2": "cell_ratios",
    "G2c": "comparisons",
}


def failure_reason(stage: str, summary: dict[str, Any]) -> str | None:
    """Why a complete stage carries no criteria (frozen ``aggregate`` early exits)."""
    if summary["completed"] < summary["planned"] or _CRITERIA_FIELD[stage] in summary:
        return None
    if stage == "G2c":
        return (
            "baseline pipeline failed or left no local nuisance draws; "
            "comparisons not evaluated"
        )
    failures = int(summary["failures"])
    return (
        f"{failures} failed task{'' if failures == 1 else 's'}; the frozen "
        "aggregate evaluates no criterion after a task failure"
    )


def _progress_rows(gate: GateRecords, stage: str) -> list[tuple[str, str, str]]:
    progress = gate.progress(stage)
    if progress is None:
        return [("availability", "not in gate records", "")]
    done, planned = progress
    rows = [("tasks completed", f"{done}/{planned}", "all")]
    summary = gate.summaries.get(stage)
    if summary is None:
        return [*rows, ("summary", "no aggregate line yet (sealed task records)", "")]
    rows.append(
        (
            "task failures",
            str(summary["failures"]),
            (
                f"<= {protocol().g2_pooled_failure_fraction * 100:g}% pooled"
                if stage == "G2"
                else _TASK_FAILURE_RULE[stage]
            ),
        )
    )
    sealed = gate.sealed.get(stage, 0)
    if sealed != done:
        rows.append(("task records sealed", f"{sealed}/{planned}", ""))
    if stage in gate.from_successor:
        rows.append(("summary source", SUCCESSOR_SOURCE, ""))
    return rows


def _stage_rows(
    gate: GateRecords, stage: str, thresholds: dict[str, float] | None
) -> list[tuple[str, str, str]]:
    p = protocol()
    rows = _progress_rows(gate, stage)
    summary = gate.summaries.get(stage)
    if summary is None:
        return rows
    if summary["completed"] < summary["planned"]:
        rows.append(("summary", "in progress; criteria not evaluated yet", ""))
        if stage == "G2" and "cell_failure_counts" in summary:
            failed = cast(list[int], summary["cell_failure_counts"])
            rows.append(
                (
                    "failures by cell",
                    _series(failed),
                    f"<= {p.g2_cell_failure_limit} per cell",
                )
            )
        return rows
    reason = failure_reason(stage, summary)
    if reason is not None:
        return [*rows, ("failure reason", reason, "")]
    if stage == "G0":
        fits = int(summary["fits"])
        impl = int(summary["implementation_statuses"])
        rows += [
            ("fits", str(fits), ""),
            (
                "a=0 identity fits not anchor-exact",
                str(summary["anchor_failures"]),
                "= 0",
            ),
            ("budget statuses", str(summary["budget_statuses"]), "= 0"),
            (
                "implementation statuses / fits",
                f"{impl}/{fits} = {number(impl / fits if fits else math.nan, 4)}",
                f"<= {p.g0_implementation_limit:g}",
            ),
        ]
        statuses = cast(dict[str, int], summary["statuses"])
        rows += [
            (f"status {k}", str(v), "reported") for k, v in sorted(statuses.items())
        ]
    elif stage == "G1b":
        counts = cast(dict[str, int], summary["coverage_counts"])
        rows += [
            (
                f"joint coverage, {s}",
                f"{counts[s]}/{p.g1b_repetitions}",
                f">= {p.g1b_pass_mark}/{p.g1b_repetitions}",
            )
            for s in SCENARIOS
            if s in counts
        ]
        rows.append(
            (
                f"empirical max-t above {p.critical_floor:g}",
                f"{summary['empirical_exceeds_floor_count']}/{summary['completed']}",
                "reported (D6)",
            )
        )
    elif stage == "G1c":
        rows += [
            (
                "anchor-exact fits",
                f"{summary['anchor_count']}/{p.g1c_fits}",
                f"= {p.g1c_fits}/{p.g1c_fits}",
            ),
            (
                f"pointwise failures at {p.critical_floor:g}",
                f"{summary['pointwise_failures']}/{p.g1c_fits}",
                f"<= {p.g1c_pointwise_limit}",
            ),
            (
                f"|mean AUC - {p.null_auc:g}| / SE",
                number(summary["mean_z"]),
                f"<= {p.g1c_mean_z_limit:g}",
            ),
            ("tie rate", number(summary["tie_rate"], 4), "reported"),
        ]
    elif stage == "G2":
        rows += _g2_rows(gate, summary, thresholds)
    elif stage == "G2c":
        rows += _g2c_rows(summary)
    return rows


def _g2_rows(
    gate: GateRecords, summary: dict[str, Any], thresholds: dict[str, float] | None
) -> list[tuple[str, str, str]]:
    p = protocol()
    t = thresholds or {}
    cell_rule = (
        f"upper >= {number(t['cell_lower'])}, lower <= {number(t['cell_upper'])}"
        if t
        else "criteria-v43 thresholds"
    )
    pooled_rule = (
        f"upper >= {number(t['pooled_lower'])}, lower <= {number(t['pooled_upper'])}"
        if t
        else "criteria-v43 thresholds"
    )
    rows: list[tuple[str, str, str]] = []
    if summary["cell_ratios"]:
        for i, (ratio, lo, hi) in enumerate(
            zip(
                summary["cell_ratios"],
                summary["cell_lower"],
                summary["cell_upper"],
                strict=True,
            )
        ):
            rows.append(
                (
                    f"dispersion ratio, {cell_label(gate, i)}",
                    _ratio(ratio, lo, hi),
                    cell_rule,
                )
            )
        rows.append(
            (
                "dispersion ratio, pooled",
                _ratio(
                    summary["pooled_ratio"],
                    summary["pooled_lower"],
                    summary["pooled_upper"],
                ),
                pooled_rule,
            )
        )
    else:
        rows += [
            ("dispersion ratio", "not estimable", cell_rule),
            (
                "successful pairs by cell",
                _series(summary.get("successful_pair_counts", [])),
                f">= {p.g2_min_pairs} per cell to estimate",
            ),
        ]
    return [
        *rows,
        (
            "failures by cell",
            _series(summary["cell_failure_counts"]),
            (
                f"<= {p.g2_cell_failure_limit} per cell; "
                f"<= {p.g2_pooled_failure_fraction * 100:g}% pooled"
            ),
        ),
        (
            "FD variance ratio median by cell",
            _series(summary["fd_ratio_median_by_cell"], 3),
            f"each in [{p.fd_range[0]:g}, {p.fd_range[1]:g}]",
        ),
        ("LOO tail counts by cell", _series(summary["loo_tail_counts"]), "reported"),
        (
            "covariance flags by cell",
            _series(summary["covariance_flag_counts"]),
            "reported (v4.1 R3)",
        ),
    ]


def _g2c_rows(summary: dict[str, Any]) -> list[tuple[str, str, str]]:
    p = protocol()
    rule = f"upper >= {p.g2c_upper_minimum}, lower <= {p.g2c_lower_maximum}"
    rows: list[tuple[str, str, str]] = []
    for comparison, label, allowance in zip(
        cast(list[dict[str, Any]], summary["comparisons"]),
        tuple(
            f"a={share:.2f}, {count} refits" for share, count in p.g2c_refits.items()
        ),
        tuple(
            f"<= {p.g2c_failure_allowances[count]}/{count}"
            for count in p.g2c_refits.values()
        ),
        strict=False,
    ):
        failures = (
            f"{comparison['failure_count']}/{comparison['denominator']}",
            allowance,
        )
        if "ratio" not in comparison:
            rows += [
                (f"Var_D5/Var_refit, {label}", "not estimable", rule),
                (f"refit failures, {label}", *failures),
            ]
            continue
        rows += [
            (
                f"Var_D5/Var_refit, {label}",
                _ratio(comparison["ratio"], comparison["lower"], comparison["upper"]),
                rule,
            ),
            (f"refit failures, {label}", *failures),
            (f"refit tails, {label}", str(comparison["tails"]), "reported"),
        ]
    return rows


def _stop_row(gate: GateRecords) -> tuple[str, ...]:
    binding = cast(dict[str, Any], cast(dict[str, Any], gate.stop)["g0_gap_binding"])
    return (
        "pre-G2 stop",
        "economy rule: G0 gap-rate predictive check before G2",
        f"pass probability {number(binding['pass_probability'])} "
        f"({binding['gaps']}/{binding['denominator']} G0 gaps)",
        f">= {number(binding['minimum'], 2)} to run G2",
        STOPPED,
    )


def table_t3(gate: GateRecords, thresholds: dict[str, float] | None) -> Table:
    rows: list[tuple[str, ...]] = []
    for stage in GATE_STAGES:
        if stage == "G2" and gate.stop is not None:
            rows.append(_stop_row(gate))
        verdict = gate.verdict(stage) or NA
        for item, value, criterion in _stage_rows(gate, stage, thresholds):
            rows.append((stage, item, value, criterion, verdict))
    notes = [
        "Criteria values, counts, ratios and pass/fail only (D7 sealing rule).",
        "Each stage reports its criteria.jsonl line with the most completed tasks: "
        "the frozen runner appends one line per shard, and mid-run lines carry "
        "pass=false. 'in progress': completed < planned, so no verdict yet.",
        "A complete stage without criteria names its failure reason (a failed task "
        "in G0, G1b or G1c; a failed G2c baseline).",
    ]
    if gate.g2_cells is None:
        notes.append(
            "G2 cells in allocation order; bracketed values are bootstrap intervals."
        )
    else:
        notes.append(
            "G2 cells (a, r) from the second binding, in allocation order: "
            + "; ".join(cell_label(gate, i) for i in range(len(gate.g2_cells)))
            + ". Bracketed values are bootstrap intervals."
        )
    for successor in gate.successors:
        if successor.stage in gate.from_successor:
            notes.append(
                f"{successor.stage}: {SUCCESSOR_SOURCE} {successor.name} (sha256 "
                f"{successor.sha256[:12]}), because criteria.jsonl holds no complete "
                f"{successor.stage} line."
            )
    reruns = {k: v for k, v in gate.summary_counts.items() if v > 1}
    if reruns:
        notes.append(
            "Aggregate lines per stage in criteria.jsonl: "
            + ", ".join(f"{k}={v}" for k, v in sorted(reruns.items()))
        )
    return Table(
        "T3_gate_summary",
        ("stage", "item", "value", "criterion", "stage_pass"),
        tuple(rows),
        tuple(notes),
    )


def to_csv(table: Table) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(table.header)
    writer.writerows(table.rows)
    return buffer.getvalue()


def to_latex(table: Table) -> str:
    columns = "".join(
        "r" if _numeric(table, i) else "l" for i in range(len(table.header))
    )
    env = "longtable" if table.long else "tabular"
    lines = [
        f"% {table.name}; requires booktabs" + (" and longtable" if table.long else "")
    ]
    lines += [f"% {note}" for note in table.notes]
    lines += [
        rf"\begin{{{env}}}{{{columns}}}",
        r"\toprule",
        " & ".join(tex_escape(h) for h in table.header) + r" \\",
        r"\midrule",
    ]
    if table.long:
        lines.append(r"\endhead")
    lines += [" & ".join(tex_escape(c) for c in row) + r" \\" for row in table.rows]
    lines += [r"\bottomrule", rf"\end{{{env}}}"]
    return "\n".join(lines) + "\n"


def _numeric(table: Table, index: int) -> bool:
    values = [row[index] for row in table.rows if row[index] not in (NA, "")]
    try:
        [float(v) for v in values]
    except ValueError:
        return False
    return bool(values)


def write_table(table: Table, directory: Path, *, suffix: str = "") -> list[Path]:
    csv_path = directory / f"{table.name}{suffix}.csv"
    tex_path = directory / f"{table.name}{suffix}.tex"
    csv_path.write_text(to_csv(table), encoding="utf-8")
    tex_path.write_text(to_latex(table), encoding="utf-8")
    return [csv_path, tex_path]


def grid_labels() -> Sequence[str]:
    return [strength(a) for a in GRID]
