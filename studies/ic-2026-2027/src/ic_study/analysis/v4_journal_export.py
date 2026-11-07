"""Tabulate public results for the journal without rerunning scientific analysis.

The export reads the four required inputs, the optional approved SHP aggregate,
and the optional sanitized channel-stress aggregate;
its outputs are confined to the generated directory and the journal values file.
The separate sanitizer reads only X1a, X1b, X2 and X5 aggregates and writes sanitized
copies and a removal/hash ledger to its archive directory.
Generic rules remove private metadata fields and absolute/home paths. Supply
site-specific strings only at runtime with the optional, repeatable
--private-pattern REGEX sanitizer argument (case-insensitive). Patterns are not
recorded in the archive or journal values; no site names are built into the code.
This is a rendering projection, not provenance certification.
Missing cell estimates remain unavailable; bands are never used to
reconstruct standard errors. Boundaries are copied, never recomputed.

The normal-theory AUC translation uses delta = sqrt(2) * Phi^-1(AUC) and
power = Phi(delta - 1.6449), for a one-sided test at level 0.05. Phi is the
standard normal cumulative distribution function (statistics.NormalDist).

Crosswalk scenarios follow the declared plan in shp_crosswalk.plan_cells:
a0 = the influence arm at a = 0; b025 = null family B with trait weight eta = 0.25;
b050 = null family B with trait weight eta = 0.50. The latter two are persistence
references, not influence strengths. Public objects.crosswalk.ranges supplies the
named references "a = 0", "B η = 0.25" and "B η = 0.50" respectively.

The j.shp.refresh.* values come from the aggregate's refreshment-entry proxy
(first_valid_answer_2004): an edge estimate from the first wave of its fit.

Free-share grid fits require free.success = true and the last free attempt's
status = interior. Share shifts are fitted minus design share; grid extrema
use their absolute values before rounding. A trait weight on the lower box
edge means the recorded free.parameters.eta equals exactly zero (the frozen
box is [0, 0.8]); small positive weights are not counted as zero. Free gaps
are the archived reading = free-gap, not failed known-share fits.
At each first boundary, the plus trial is the unique recorded attempt point
whose signal minus design share equals exactly 0.01 in catalog decimals.
Its lag-three miss is residual.i002: B minus influence on matching panels,
without standardization, unlike the influence-minus-B standardized T10 miss.

Stress-cell parameters are cells[].parameters (phi, trait weight), and AUC
is cells[].estimate.auc, cross-checked against the released comparison value
where present. Lag differences are data_mean minus null_mean on check panels
at zero influence with B fitted at the known share; they are descriptive
means, not an evaluation of the influence-trained score on those panels.

Model rows group consecutive design shares with the same exact first boundary.
Every common boundary is checked before rendering; differing sustained states
remain explicit per-share exceptions. The levels table reuses the signed,
four-decimal share-shift keys from the fit table.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from contextlib import ExitStack
from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path
from statistics import NormalDist, median
from tempfile import TemporaryDirectory
from typing import Any, cast

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from ic_study.analysis.v4_report_figures import (
    DOUBLE,
    FAMILY_COLOR,
    GAP_COLOR,
    MM,
    OKABE_ITO,
    SOLVER_BUDGET,
    STATUS_COLOR,
    Render,
    save,
    style,
)
from ic_study.analysis.v4_report_schema import CRITICAL_FLOOR, GATE_STAGES
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES
from ic_study.simulation.v4_plan import SCENARIOS

SCHEMA = "ic-study.v4-journal-values.v1"
VALID = "completo válido"
INVALID = "completo inválido"
STATUS = {
    VALID: "complete and valid",
    INVALID: "complete but invalid",
    "parcial por encerramento operacional": "partial at the operational close",
    "não iniciado": "not started",
}
CSV_STATUS = STATUS
CROSSWALK_SCENARIOS = {"a = 0": "a0", "B η = 0.25": "b025", "B η = 0.50": "b050"}
UNITS_README = """Online Resource 2: all simulation units

One row per unit (one comparison at one signal share) of the frozen inventory,
including controls and sensitivities.
This English copy preserves the original rows, columns, order and numeric strings.
The archived original CSV keeps the released Portuguese status labels.

Columns (in file order):
tier: inventory group (1 main B, 2 other models,
  3 measurement controls and mobility variants,
  4 response-channel sensitivities, 5 mechanism sensitivities, 6 24-step sensitivity).
family: persistence model (A autoregressive, B trait plus autoregressive,
  C autoregressive with an altered response channel, D state-dependent, E mover-stayer).
channel: observed, latent (error-free), ordinal_one (signal share one), or latent_rank.
  latent_rank: wave-wise mid-ranks of the error-free latent values.
sensitivity: scenario identifier; see the scenario legend below.
r: signal share in the continuous response before discretization.
exposure: the stored flag "calibration-exposed" marks r = 0.70, examined during
  calibration; otherwise blank.
main_curve_flag: main curve invalid when any main B unit is not complete and valid.
status: unit completion and validity at the operational close. Complete means all
  nine strength cells ran, including cells recorded as gaps; complete and valid
  additionally requires a fitted zero-strength cell whose band contains 0.5.
  Otherwise a complete unit is complete but invalid and its boundaries are suppressed.
null_gate: a unit passes only when its zero-strength cell is fitted and its AUC
  band covers 0.5.
gaps: total unavailable cells on the strength grid.
gaps_screened: family limits from the feasibility pre-check, without solver evaluations.
gaps_family_limit: family limits encountered while fitting the profile.
gaps_solver: other solver statuses preventing an accepted fit.
gaps_validation: accepted fits that failed validation.
gaps_dependency: controls whose observed-channel fit failed.
gaps_propagation: failed uncertainty propagation.
a_star: first grid strength whose point AUC reaches the primary target 0.70,
  reported only strictly below the first gap.
a_star_lower, a_star_upper: lower/upper ends of its inverted-band interval.
a_s_star: first grid strength from which the point AUC stays at or above 0.70
  at every higher strength, reported only strictly above the last gap.
a_s_star_lower, a_s_star_upper: lower/upper ends of its inverted-band interval.
region: small when the entire first-boundary interval lies within (0, 0.03];
  large when the entire interval lies above 0.03; indeterminate when the interval
  crosses 0.03, has a censored end or the boundary is zero; not attained when a
  full gap-free grid never reaches the target; censored (gap) when a fit gap prevents
  declaring the first boundary; NA for invalid or unfinished units.
derived_a_star_060: first boundary at secondary AUC target 0.60.
derived_a_star_060_lower, derived_a_star_060_upper: its interval ends.
derived_a_star_080: first boundary at secondary AUC target 0.80.
derived_a_star_080_lower, derived_a_star_080_upper: its interval ends.
nonmonotone_band: whether either band endpoint decreases along the available grid.
critical: maximum of the empirical max-t critical value and the 2.7729 floor.
max_t_above_floor: whether the empirical critical value exceeds that floor.

Scenario legend:
main: main specification.
mobility: mobility summaries in place of the lag features.
c025: Persistent response style (c = 0.25).
c050: Persistent response style (c = 0.50).
d010: Panel conditioning (delta = 0.10).
d020: Panel conditioning (delta = 0.20).
c050-d020-exploratory: Response style and conditioning (c=0.50, delta=0.20).
b000: Attraction only (b = 0).
omega025: Anchoring (omega = 0.25).
omega050: Anchoring (omega = 0.50).
omega075: Anchoring (omega = 0.75).
omega100: Complete anchoring (omega = 1).
steps24: 24 update steps per wave.

Mobility summaries measure mean absolute one-wave change within each tercile of
the starting wave's mid-rank position. The combined response-style and conditioning
scenario is exploratory.

Boundary intervals invert bands simultaneous over the strengths of one share,
without interpolation or smoothing. The first interval runs from the first
strength whose upper band reaches 0.70 to the first whose lower band does;
the sustained interval applies the same rule to all higher strengths.
First-boundary interval ends are reported only strictly below the first gap;
sustained-boundary interval ends only strictly above the last gap.
"not reached (>0.9)" and ">0.9" denote right censoring on the complete eligible
grid; for a point boundary this is not attained, while an interval end is censored.
"censored at gap a=x" identifies a fit gap, never evidence of not attaining the target.
"suppressed" means the null gate failed. "NA" means unavailable or inapplicable.

Status translation:
completo válido -> complete and valid
completo inválido -> complete but invalid
parcial por encerramento operacional -> partial at the operational close
não iniciado -> not started
"""
GAP_NAMES = {
    "family_limit": "family limit on profile",
    "solver": "other solver status",
    "propagation": "propagation gap",
    "screened": "screened",
    "validation": "validation",
    "dependency": "dependency",
}
MODEL_NAMES = {
    "A": "autoregressive",
    "B": "trait-plus-autoregressive",
    "C": "autoregressive with an altered response channel",
    "D": "state-dependent",
    "E": "mover--stayer",
}
SCENARIO_NAMES = {
    "c025": r"Persistent response style ($c=0.25$)",
    "c050": r"Persistent response style ($c=0.50$)",
    "d010": r"Panel conditioning ($\delta=0.10$)",
    "d020": r"Panel conditioning ($\delta=0.20$)",
    "c050-d020-exploratory": (
        r"Response style and conditioning ($c=0.50$, $\delta=0.20$; exploratory)"
    ),
    "b000": r"Attraction only ($b=0$)",
    "omega025": r"Anchoring ($\omega=0.25$)",
    "omega050": r"Anchoring ($\omega=0.50$)",
    "omega075": r"Anchoring ($\omega=0.75$)",
    "omega100": r"Complete anchoring ($\omega=1$)",
    "steps24": "24 update steps per wave",
}
RESPONSE_SCENARIOS = {"c025", "c050", "d010", "d020", "c050-d020-exploratory"}


def strength(value: float) -> str:
    return f"{value:.3f}" if 0 < value < 0.01 else f"{value:.2f}" if value else "0"


def r_tag(value: float) -> str:
    return f"r{round(value * 100):03d}"


def a_tag(value: float) -> str:
    return f"a{round(value * 10000):04d}"


@dataclass
class Numbers:
    final: Mapping[str, str]
    values: dict[str, str] = field(default_factory=dict)

    def put(self, key: str, value: str) -> str:
        if not key.startswith("j."):
            raise ValueError(f"Journal key must start with j.: {key}")
        if key in self.final:
            raise ValueError(f"Refusing to overwrite final value key {key}")
        if key in self.values and self.values[key] != value:
            raise ValueError(f"Conflicting journal value {key}")
        self.values[key] = value
        return key

    def number(self, key: str, preferred: str | None = None) -> str:
        value = self.values[key]
        if preferred is not None and self.final.get(preferred) == value:
            key = preferred
        return rf"\resultnum{{{key}}}{{{value}}}"


@dataclass(frozen=True)
class JournalCurve:
    key: str
    tier: int
    family: str
    channel: str
    scenario: str
    r: float
    status: str
    record: dict[str, Any]

    @property
    def prefix(self) -> str:
        group = "b" if self.tier == 1 else f"models.{self.family}"
        return f"j.{group}.{r_tag(self.r)}"

    def estimate(self, a: float, kind: str) -> float | None:
        available = cast(list[float], self.record["available"])
        if a not in available:
            return None
        return float(self.record[kind][available.index(a)])

    @property
    def gaps(self) -> list[tuple[float, str]]:
        return [
            (a, str(g))
            for a, g in zip(GRID, self.record["cell_gap"], strict=True)
            if g is not None
        ]


@dataclass(frozen=True)
class Journal:
    values: dict[str, str]
    tables: dict[str, str]
    curves: tuple[JournalCurve, ...]
    notes: tuple[str, ...] = ()


def _curves(public: Mapping[str, Any]) -> tuple[JournalCurve, ...]:
    if public.get("schema") != "ic-study.v4-public-aggregates.v1":
        raise ValueError("Expected the public aggregates schema")
    release = public["objects"]["release"]
    curves = []
    for key, record in release["curves"].items():
        meta = record["meta"]
        if key != meta["key"] or record["status"] != release["statuses"][key]:
            raise ValueError(f"Inconsistent public identity or status: {key}")
        available = record["available"]
        if any(a not in GRID for a in available) or available != sorted(set(available)):
            raise ValueError(f"Invalid available strengths: {key}")
        if any(
            len(record[kind]) != len(available) for kind in ("auc", "lower", "upper")
        ):
            raise ValueError(f"Mismatched AUC vectors: {key}")
        if len(record["cell_gap"]) != len(GRID):
            raise ValueError(f"Missing gap states: {key}")
        if available != [
            a for a, g in zip(GRID, record["cell_gap"], strict=True) if g is None
        ]:
            raise ValueError(f"Available strengths disagree with gaps: {key}")
        curves.append(
            JournalCurve(
                key,
                int(meta["tier"]),
                str(meta["family"]),
                str(meta["channel"]),
                str(meta["sensitivity"]),
                float(meta["r"]),
                str(record["status"]),
                record,
            )
        )
    return tuple(
        sorted(curves, key=lambda c: (c.tier, c.family, c.channel, c.scenario, c.r))
    )


def _censoring_gap(
    curve: JournalCurve, name: str, field_name: str
) -> tuple[float, str] | None:
    text = curve.record[name].get(field_name)
    if not text:
        return None
    match = re.fullmatch(r"gap at a=([0-9.]+)", text)
    if match is None:
        raise ValueError(f"Unknown {field_name} state: {curve.key}")
    gaps = curve.gaps
    gap = gaps[0 if name == "first" else -1] if gaps else None
    position = "first" if name == "first" else "last"
    if gap is None or float(match[1]) != gap[0]:
        raise ValueError(
            f"{name} {field_name} must identify the {position} gap: {curve.key}"
        )
    return gap


def _boundary_values(
    numbers: Numbers, curve: JournalCurve, name: str, prefix: str
) -> None:
    boundary = curve.record[name]
    numbers.put(
        prefix + ".state",
        "invalid"
        if curve.status != VALID
        else "censored"
        if boundary["censoring"]
        else "attained"
        if boundary["point"] is not None
        else "not reached",
    )
    numbers.put(
        prefix + ".point",
        strength(float(boundary["point"]))
        if curve.status == VALID and boundary["point"] is not None
        else "unavailable",
    )
    for suffix, end in zip(
        ("lower", "upper"), boundary["interval"] or [None, None], strict=True
    ):
        numbers.put(
            prefix + "." + suffix,
            strength(float(end))
            if curve.status == VALID and end is not None
            else "unavailable",
        )
    for index, (a, _) in enumerate(curve.gaps):
        numbers.put(prefix + f".gap.{index}.a", strength(a))
    for field_name, suffix in (
        ("censoring", ".censoring_gap.a"),
        ("interval_censoring", ".interval_gap.a"),
    ):
        gap = _censoring_gap(curve, name, field_name)
        if gap is None:
            continue
        if field_name == "censoring" and curve.status != VALID:
            continue
        numbers.put(prefix + suffix, strength(gap[0]))


def _boundary_text(
    numbers: Numbers,
    curve: JournalCurve,
    name: str,
    prefix: str,
    *,
    interval: bool = True,
) -> str:
    boundary = curve.record[name]
    if curve.status != VALID:
        return "invalid; boundary suppressed"
    if boundary["point"] is None:
        if boundary["censoring"] and curve.gaps:
            if name == "first":
                text = (
                    "censored at first gap ("
                    + numbers.number(prefix + ".censoring_gap.a")
                    + ")"
                )
                if (
                    interval
                    and boundary["interval"]
                    and boundary["interval"][0] is not None
                ):
                    text += "; interval from " + numbers.number(prefix + ".lower")
                return text
            gaps = ", ".join(
                numbers.number(prefix + f".gap.{i}.a") for i in range(len(curve.gaps))
            )
            label = "fit gaps at " if len(curve.gaps) > 1 else "fit gap at "
            return "censored (" + label + gaps + ")"
        return "not reached on complete eligible grid"
    point = numbers.number(prefix + ".point")
    if not interval:
        return point
    ends = []
    for i, suffix in enumerate(("lower", "upper")):
        end = (boundary["interval"] or [None, None])[i]
        if end is not None:
            ends.append(numbers.number(prefix + "." + suffix))
        elif boundary.get("interval_censoring") and not (
            name == "sustained" and i == 1 and boundary["interval"][0] is not None
        ):
            ends.append(
                "censored at fit gap " + numbers.number(prefix + ".interval_gap.a")
            )
        else:
            ends.append("beyond grid")
    return point + " [" + ", ".join(ends) + "]"


def _table(
    label: str,
    caption: str,
    columns: str,
    header: Sequence[str],
    rows: Sequence[Sequence[str]],
    *,
    note: str = "",
    wide: bool = False,
    colsep: str = "2pt",
) -> str:
    environment = "table*" if wide else "table"
    columns = re.sub(
        r"p\{[^}]+\}", lambda m: r">{\raggedright\arraybackslash}" + m[0], columns
    )
    lines = [
        rf"\begin{{{environment}}}[tp]",
        rf"\caption{{{caption}}}\label{{{label}}}",
        r"\centering\scriptsize",
        rf"\setlength{{\tabcolsep}}{{{colsep}}}",
        rf"\begin{{tabular}}{{{columns}}}",
        r"\toprule",
        " & ".join(header) + r" \\",
        r"\midrule",
    ]
    lines += [" & ".join(row) + r" \\" for row in rows]
    lines += [r"\botrule", r"\end{tabular}"]
    if note:
        lines += [r"\par\smallskip\parbox{\linewidth}{" + note + "}"]
    lines += [rf"\end{{{environment}}}", ""]
    return "\n".join(lines)


def _identity(curve: JournalCurve) -> tuple[str, ...]:
    return (
        str(curve.tier),
        curve.family,
        curve.channel,
        curve.scenario,
        f"{curve.r:.2f}",
    )


def _inventory_rows(
    curves: Sequence[JournalCurve], rows: Sequence[Mapping[str, str]]
) -> dict[tuple[str, ...], Mapping[str, str]]:
    indexed: dict[tuple[str, ...], Mapping[str, str]] = {
        (row["tier"], row["family"], row["channel"], row["sensitivity"], row["r"]): row
        for row in rows
    }
    if len(indexed) != len(rows) or set(indexed) != {_identity(c) for c in curves}:
        raise ValueError("CSV inventory does not match the public curve identities")
    for curve in curves:
        if indexed[_identity(curve)]["status"] != curve.status:
            raise ValueError(f"CSV status differs from public status: {curve.key}")
    return indexed


def _model_boundary_state(
    curve: JournalCurve, name: str
) -> tuple[str, float | None, str | None, tuple[float, ...]]:
    boundary = curve.record[name]
    censoring = boundary["censoring"]
    return (
        curve.status,
        float(boundary["point"]) if boundary["point"] is not None else None,
        str(censoring) if censoring else None,
        tuple(a for a, _ in curve.gaps) if censoring else (),
    )


def _uniform_model_boundary(
    numbers: Numbers, group: Sequence[JournalCurve], name: str
) -> str:
    if not group or any(
        c.family != group[0].family
        or _model_boundary_state(c, name) != _model_boundary_state(group[0], name)
        for c in group
    ):
        raise ValueError(f"Nonuniform model {name} boundary group")
    return _boundary_text(
        numbers, group[0], name, group[0].prefix + "." + name, interval=False
    )


def _model_share_range(numbers: Numbers, group: Sequence[JournalCurve]) -> str:
    text = numbers.number("j.models." + r_tag(group[0].r) + ".r")
    if len(group) > 1:
        text += "--" + numbers.number("j.models." + r_tag(group[-1].r) + ".r")
    return text


def _grouped_model_rows(
    numbers: Numbers, curves: Sequence[JournalCurve]
) -> list[list[str]]:
    groups: list[list[JournalCurve]] = []
    for curve in sorted(curves, key=lambda c: c.r):
        if (
            groups
            and RELIABILITIES.index(curve.r)
            == RELIABILITIES.index(groups[-1][-1].r) + 1
            and _model_boundary_state(curve, "first")
            == _model_boundary_state(groups[-1][0], "first")
        ):
            groups[-1].append(curve)
        else:
            groups.append([curve])
    rows = []
    for group in groups:
        first = _uniform_model_boundary(numbers, group, "first")
        states: dict[
            tuple[str, float | None, str | None, tuple[float, ...]], list[JournalCurve]
        ] = {}
        for curve in group:
            states.setdefault(_model_boundary_state(curve, "sustained"), []).append(
                curve
            )
        common = max(states.values(), key=len)
        sustained = _uniform_model_boundary(numbers, common, "sustained")
        for curve in group:
            if curve not in common:
                exception = _uniform_model_boundary(numbers, [curve], "sustained")
                state, _, detail = exception.partition(" (")
                sustained += (
                    "; " + state + " at $r=$ " + _model_share_range(numbers, [curve])
                )
                if detail:
                    sustained += " (" + detail
        rows.append(
            [group[0].family, _model_share_range(numbers, group), first, sustained]
        )
    return rows


def _other_models(numbers: Numbers, curves: Sequence[JournalCurve]) -> str:
    entries: dict[float, dict[str, tuple[str, str]]] = {}
    models: dict[str, list[JournalCurve]] = {}
    gap_counts = dict.fromkeys(GAP_NAMES, 0)
    zero_c = []
    for curve in curves:
        if curve.tier != 2:
            continue
        models.setdefault(curve.family, []).append(curve)
        prefix = curve.prefix
        numbers.put(prefix + ".r", f"{curve.r:.2f}")
        numbers.put(prefix + ".status", STATUS[curve.status])
        for a in GRID:
            value = curve.estimate(a, "auc")
            numbers.put(
                prefix + "." + a_tag(a) + ".auc",
                f"{value:.3f}" if value is not None else "unavailable",
            )
        for name in ("first", "sustained"):
            _boundary_values(numbers, curve, name, prefix + "." + name)
        first = _boundary_text(
            numbers, curve, "first", prefix + ".first", interval=False
        )
        sustained = _boundary_text(
            numbers, curve, "sustained", prefix + ".sustained", interval=False
        )
        if curve.status != VALID:
            first = "invalid: zero-strength AUC " + numbers.number(
                prefix + ".a0000.auc"
            )
            sustained = "suppressed"
        if curve.family == "D":
            numbers.put(
                prefix + ".first_gap",
                strength(curve.gaps[0][0]) if curve.gaps else "none",
            )
            for _, kind in curve.gaps:
                gap_counts[kind] += 1
            gap = _censoring_gap(curve, "first", "censoring")
            if gap is not None and curve.status == VALID:
                first += "; " + GAP_NAMES[gap[1]]
        if curve.family == "C":
            value = curve.estimate(0, "auc")
            if value is None:
                raise ValueError(f"C zero-strength AUC is unavailable: {curve.key}")
            zero_c.append((curve.r, value))
        entries.setdefault(curve.r, {})[curve.family] = (first, sustained)
    for kind, count in gap_counts.items():
        numbers.put("j.models.D.gaps." + kind, str(count))
    numbers.put("j.models.D.gaps.total", str(sum(gap_counts.values())))
    if zero_c:
        _nine_shares("C zero-strength AUC", zero_c)
        _extrema(numbers, "j.models.C.zero_auc", zero_c, with_shares=False)
    rows: list[list[str]] = []
    for r in sorted(entries):
        numbers.put("j.models." + r_tag(r) + ".r", f"{r:.2f}")
    for family in ("A", "C", "D", "E"):
        family_curves = models.get(family, [])
        if not family_curves:
            continue
        if family == "C" and all(c.status == INVALID for c in family_curves):
            zero = numbers.number("j.models.C.zero_auc.min")
            if (
                numbers.values["j.models.C.zero_auc.min"]
                != numbers.values["j.models.C.zero_auc.max"]
            ):
                zero += "--" + numbers.number("j.models.C.zero_auc.max")
            rows.append(
                [
                    family,
                    "All shares",
                    "Invalid: zero-strength AUC " + zero,
                    "Suppressed",
                ]
            )
        elif family == "D" and all(
            c.status == VALID
            and c.record["first"]["censoring"]
            and c.record["sustained"]["censoring"]
            for c in family_curves
        ):
            grouped: dict[tuple[float, str], list[JournalCurve]] = {}
            for c in family_curves:
                gap = _censoring_gap(c, "first", "censoring")
                if gap is None:
                    raise ValueError("Censored D boundary has no first gap")
                grouped.setdefault(gap, []).append(c)
            gaps = []
            for (a, kind), group in sorted(grouped.items(), reverse=True):
                count_key = f"j.models.D.first_gap.{a_tag(a)}.{kind}.n"
                numbers.put(count_key, str(len(group)))
                location = (
                    "at " + numbers.number(count_key) + " shares"
                    if len(group) > 1
                    else "at $r=$ " + numbers.number(group[0].prefix + ".r")
                )
                gaps.append(
                    numbers.number(group[0].prefix + ".first.censoring_gap.a")
                    + " "
                    + location
                    + " ("
                    + GAP_NAMES[kind]
                    + ")"
                )
            rows.append(
                [
                    family,
                    "All shares",
                    "Censored at first gap: " + "; ".join(gaps),
                    "Censored (fit gaps)",
                ]
            )
        elif family in ("A", "E") and all(
            c.status == VALID
            and c.record["first"]["point"] is not None
            and not c.record["first"]["censoring"]
            for c in family_curves
        ):
            rows.extend(_grouped_model_rows(numbers, family_curves))
        else:
            for c in family_curves:
                rows.append(
                    [
                        family,
                        numbers.number("j.models." + r_tag(c.r) + ".r"),
                        *entries[c.r][family],
                    ]
                )
    return _table(
        "tab:other-models",
        "Boundaries against the other persistence models.",
        "llp{62mm}p{54mm}",
        ["Model", "$r$", "First boundary", "Sustained boundary"],
        rows,
        note=(
            "$r$ is signal share in the continuous response before discretization. "
            "A: autoregressive; C: autoregressive with an altered response channel; "
            "D: state-dependent; E: mover--stayer. A and E group consecutive "
            "shares with the same first boundary; sustained-boundary exceptions "
            "are explicit. Unmarked entries are complete and valid; C is complete "
            "but invalid, so its boundaries are suppressed. Boundary and "
            "censoring definitions: "
            r"\esmresource, Table~\ref{esm-tab:glossary-terms}; fit statuses: "
            r"Table~\ref{esm-tab:glossary-states}."
        ),
        wide=True,
        colsep="4pt",
    )


def _sensitivity_table(
    numbers: Numbers,
    curves: Sequence[JournalCurve],
    inventory: Mapping[tuple[str, ...], Mapping[str, str]],
) -> str:
    main = {c.r: c for c in curves if c.tier == 1 and c.family == "B"}
    pairs = []
    differences = []
    for curve in curves:
        if curve.tier not in (4, 5, 6) or curve.family != "B" or curve.r not in main:
            continue
        base = main[curve.r]
        if base.status == curve.status == VALID:
            pairs.append(curve)
            if (
                inventory[_identity(base)]["region"]
                != inventory[_identity(curve)]["region"]
            ):
                differences.append(curve)
    for suffix, count in (
        ("n_pairs_compared", len(pairs)),
        ("n_region_differs", len(differences)),
    ):
        expected = numbers.final.get("v4.sens." + suffix)
        if expected is not None and int(expected) != count:
            raise ValueError(
                f"Sensitivity {suffix}: found {count}, final values say {expected}"
            )
        numbers.put("j.sensitivity." + suffix, str(count))
    response_pairs = [
        c for c in pairs if c.tier == 4 and c.scenario in RESPONSE_SCENARIOS
    ]
    numbers.put("j.sensitivity.response_channel.n_pairs", str(len(response_pairs)))
    numbers.put(
        "j.sensitivity.response_channel.n_same_region",
        str(
            sum(
                inventory[_identity(c)]["region"]
                == inventory[_identity(main[c.r])]["region"]
                for c in response_pairs
            )
        ),
    )
    rows = []
    for curve in sorted(differences, key=lambda c: (c.tier, c.scenario, c.r)):
        base = main[curve.r]
        prefix = f"j.sensitivity.{curve.scenario}.{r_tag(curve.r)}"
        numbers.put(prefix + ".scenario", SCENARIO_NAMES[curve.scenario])
        numbers.put(prefix + ".r", f"{curve.r:.2f}")
        for name, item in (("main", base), ("sensitivity", curve)):
            _boundary_values(numbers, item, "first", prefix + "." + name)
            numbers.put(
                prefix + "." + name + ".region", inventory[_identity(item)]["region"]
            )
        rows.append(
            [
                SCENARIO_NAMES[curve.scenario],
                numbers.number(prefix + ".r"),
                _boundary_text(numbers, base, "first", prefix + ".main"),
                _boundary_text(numbers, curve, "first", prefix + ".sensitivity"),
                inventory[_identity(curve)]["region"],
            ]
        )
    return _table(
        "tab:sensitivity-differences",
        "Sensitivity units whose boundary regions differ from the main result.",
        "p{30mm}lp{25mm}p{38mm}l",
        [
            "Scenario",
            "$r$",
            "Main $a^*$ [interval]",
            "Sensitivity $a^*$ [interval]",
            "Sensitivity region",
        ],
        rows,
        note=(
            "$r$ is signal share in the continuous response before discretization. "
            r"$b$ sets repulsion strength; $\delta$ sets the rise in signal share "
            "with earlier interviews in the panel-conditioning channel. "
            "AUC is the area under the receiver operating characteristic curve. "
            "$a^*$ is the first boundary, the first grid strength whose point AUC "
            "reaches "
            + numbers.number("j.target.r070")
            + ". Brackets give its interval from inverting the band's limits, "
            "simultaneous over strengths of that share. Only complete and valid "
            "sensitivity units with different protocol region labels from the main "
            "unit at the same signal share are shown. Indeterminate "
            "means the boundary is zero, its interval crosses "
            + numbers.number("j.grid.a0300")
            + " on the nominal scale, or an interval end is censored. "
            "Censored (gap) and censored at first gap mean no first boundary is "
            "declared across the earliest strength with no accepted AUC estimate. "
            "Censored at fit gap marks an interval end blocked by that gap; "
            "interval from gives the retained lower end."
        ),
    )


def _extrema(
    numbers: Numbers,
    prefix: str,
    entries: Sequence[tuple[float, float]],
    *,
    grid: bool = False,
    with_shares: bool = True,
    decimals: int = 3,
) -> None:
    if not entries:
        return
    for suffix, select in (("min", min), ("max", max)):
        _, value = select(entries, key=lambda item: item[1])
        numbers.put(
            prefix + "." + suffix,
            strength(value) if grid else f"{value:.{decimals}f}",
        )
        if with_shares:
            shares = sorted({r for r, estimate in entries if estimate == value})
            numbers.put(
                prefix + "." + suffix + ".r", ", ".join(f"{r:.2f}" for r in shares)
            )


def _nine_shares(prefix: str, entries: Sequence[tuple[float, float]]) -> None:
    if len(entries) != 9 or {r for r, _ in entries} != set(RELIABILITIES):
        raise ValueError(f"{prefix} summary requires nine values at the design shares")
    if any(not math.isfinite(value) for _, value in entries):
        raise ValueError(f"{prefix} summary contains a non-finite value")


def _released_float(numbers: Numbers, catalog: Mapping[str, Any], key: str) -> float:
    text = numbers.final.get(key, catalog.get("values", {}).get(key))
    if text is None or text == "unavailable":
        raise ValueError(f"Missing or unavailable released value: {key}")
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"Non-finite released value: {key}")
    return value


def _x3_boundary_cells(
    numbers: Numbers, catalog: Mapping[str, Any], main: Sequence[JournalCurve]
) -> list[tuple[JournalCurve, str]]:
    released = catalog.get("values", {})
    cells = []
    _nine_shares("Free-share boundary cells", [(c.r, c.r) for c in main])
    for curve in sorted(main, key=lambda c: c.r):
        a = curve.record["first"]["point"]
        if curve.status != VALID or a is None or curve.record["first"]["censoring"]:
            raise ValueError(
                f"Free-share boundary cell has no valid boundary: {curve.key}"
            )
        stem = f"v4x.x3.cells.{r_tag(curve.r)}.{a_tag(a)}."
        share = f"{curve.r:g}".replace(".", "-")
        boundary = f"v4x.comparisons.by_r.{share}.main_curve.first.point"
        if (
            _released_float(numbers, catalog, stem + "cell.a") != a
            or _released_float(numbers, catalog, stem + "cell.r") != curve.r
            or released.get(stem + "cell.family") != "B"
            or released.get(stem + "cell.channel") != "observed"
            or _released_float(numbers, catalog, boundary) != a
        ):
            raise ValueError(f"Free-share boundary cell identity mismatch: {stem}")
        cells.append((curve, stem))
    return cells


def _x3_levels_table(
    numbers: Numbers, catalog: Mapping[str, Any], main: Sequence[JournalCurve]
) -> tuple[str | None, list[str]]:
    """Read catalog v4x.x3.cells.<r>.<a> at each public B first boundary.

    known.auc and free.auc describe the exploratory lag-four-and-five rules,
    not the main lag-three-through-five classifier. free.parameters.signal
    is the fitted r_B; delta.point and delta.interval_95.i000/i001 are the
    archived free-minus-known difference and its paired interval. Preserve
    lost_crossing, rather than deriving a flag from rounded AUCs. Cross-check
    the cell against v4x.comparisons.by_r.<r>.main_curve.first.point.
    """
    released = catalog.get("values", {})
    if not any(
        key.startswith("v4x.x3.cells.") and key.endswith(".known.auc")
        for key in released
    ):
        return None, ["j.x3 levels: no released catalog AUC levels; table omitted"]
    notes: list[str] = []
    rows = []
    summaries: dict[str, list[tuple[float, float]]] = {
        "known.auc": [],
        "free.auc": [],
        "free.r_b": [],
    }
    for curve, stem in _x3_boundary_cells(numbers, catalog, main):
        prefix = "j.x3." + r_tag(curve.r)
        shown: dict[str, str] = {}
        for suffix, source, decimals in (
            ("known.auc", "known.auc", 3),
            ("free.auc", "free.auc", 3),
            ("delta.point", "delta.point", 3),
            ("delta.lower", "delta.interval_95.i000", 3),
            ("delta.upper", "delta.interval_95.i001", 3),
            ("free.r_b", "free.parameters.signal", 2),
        ):
            key = stem + source
            success = (
                ("known",)
                if suffix == "known.auc"
                else ("free",)
                if suffix.startswith("free.")
                else ("known", "free")
            )
            if released.get(key) in (None, "unavailable") or any(
                released.get(stem + group + ".success") != "true" for group in success
            ):
                shown[suffix] = "not available"
                notes.append(
                    f"{prefix}.{suffix}: {key} not available from a successful fit"
                )
                continue
            value = _finite_float(released[key], key)
            if not (
                -1 <= value <= 1 if suffix.startswith("delta.") else 0 <= value <= 1
            ):
                raise ValueError(f"Free-share boundary cell value out of range: {key}")
            numbers.put(prefix + "." + suffix, f"{value:.{decimals}f}")
            shown[suffix] = numbers.number(prefix + "." + suffix)
            if suffix in summaries:
                summaries[suffix].append((curve.r, value))
        flag = released.get(stem + "lost_crossing")
        if flag not in ("true", "false"):
            shown["flag"] = "not available"
            notes.append(f"{prefix}.lost_crossing: {stem}lost_crossing not available")
        else:
            numbers.put(prefix + ".lost_crossing", "yes" if flag == "true" else "no")
            shown["flag"] = numbers.values[prefix + ".lost_crossing"]
        rows.append(
            [
                numbers.number(curve.prefix + ".r"),
                numbers.number(curve.prefix + ".first.point"),
                shown["known.auc"],
                shown["free.auc"],
                _math(shown["delta.point"])
                + " ["
                + _math(shown["delta.lower"])
                + ", "
                + _math(shown["delta.upper"])
                + "]",
                "$" + numbers.number(prefix + ".free.r_shift") + "$"
                if prefix + ".free.r_shift" in numbers.values
                else "not available",
                shown["flag"],
            ]
        )
    for suffix, entries in summaries.items():
        if len(entries) == len(RELIABILITIES):
            _extrema(
                numbers,
                "j.x3." + suffix,
                entries,
                decimals=2 if suffix == "free.r_b" else 3,
            )
        else:
            notes.append(f"j.x3.{suffix} extrema: incomplete boundary cells; omitted")
    return _table(
        "tab:x3-levels",
        "Known and fitted signal-share comparisons at the first boundary.",
        r"l@{\quad}l@{\quad}p{16mm}p{16mm}p{38mm}p{15mm}p{12mm}",
        [
            "Design $r$",
            "$a^*$",
            "Known-share AUC",
            "Free-share AUC",
            "Difference [interval]",
            "$r_B-r$",
            "Lost crossing",
        ],
        rows,
        note=(
            "Each row selects the first boundary of the main classifier against "
            "trait-plus-autoregressive persistence (B). Both exploratory classifiers "
            "use lag four and lag five; their AUCs are distinct from the main "
            "three-correlation classifier. The known-share fit matches the first "
            "two lags; the free-share fit estimates B's signal share and also "
            "matches lag three. Differences are free minus known, with paired "
            "ninety-five percent bootstrap intervals conditional on the fitted "
            "classifiers; uncertainty from matching is not included. Lost crossing "
            "is the archived flag: known-share point AUC reaches "
            + numbers.number("j.target.r070")
            + " while the free-share interval's upper end is below that target. "
            r"$r_B-r$ is fitted minus design share; Table~\ref{tab:x3-fit} gives "
            "B's fitted parameters."
        ),
    ), notes


def _math(text: str) -> str:
    return text if text == "not available" else "$" + text + "$"


def _decimal_text(value: Decimal, decimals: int) -> str:
    rounded = value.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_EVEN)
    return f"{abs(rounded) if rounded == 0 else rounded:.{decimals}f}"


def _x3_fit_table(
    numbers: Numbers, catalog: Mapping[str, Any], main: Sequence[JournalCurve]
) -> tuple[str | None, list[str]]:
    """Read fitted B parameters at each public first-boundary cell.

    known.parameters.i000/i001 are phi/lambda; free.parameters.phi/eta are
    phi/lambda (eta is the stored trait-weight name), and .signal is r_B.
    r_shift = r_B minus the cell's design r, using exact catalog decimals.
    free.attempts.i000.points.i000 is the initial fit at the true share: check
    its .signal and .parameters against the known-share fit. Its residual.i002
    is B minus influence at lag three over MATCH panels, not the check-panel
    means used in the lag table. Negate residual_se_units.i002 to report
    (influence L3 minus B L3) / se.i002; check the stored standardized residual
    against residual.i002 / se.i002 at the catalog's six-digit precision.
    Signed miss extrema follow that definition; share-shift extrema are absolute.
    """
    released = catalog.get("values", {})
    if not any(
        key.startswith("v4x.x3.cells.") and ".known.parameters." in key
        for key in released
    ):
        return None, ["j.x3 fits: no released parameters; table omitted"]
    notes: list[str] = []
    rows = []
    summaries: dict[str, list[tuple[float, Decimal]]] = {
        "free.r_shift": [],
        "known.lambda": [],
        "free.lambda": [],
        "l3_miss_se": [],
    }
    for curve, stem in _x3_boundary_cells(numbers, catalog, main):
        prefix = "j.x3." + r_tag(curve.r)
        shown: dict[str, str] = {}
        parameters: dict[str, Decimal] = {}
        for suffix, source in (
            ("known.phi", "known.parameters.i000"),
            ("known.lambda", "known.parameters.i001"),
            ("free.phi", "free.parameters.phi"),
            ("free.lambda", "free.parameters.eta"),
            ("free.r", "free.parameters.signal"),
        ):
            key = stem + source
            group = suffix.split(".")[0]
            if (
                released.get(key) in (None, "unavailable")
                or released.get(stem + group + ".success") != "true"
            ):
                shown[suffix] = "not available"
                notes.append(f"{prefix}.{suffix}: {key} not available from a valid fit")
                continue
            value = _finite_float(released[key], "Free-share fit " + key)
            if not 0 <= value <= 1:
                raise ValueError(f"Free-share fit parameter out of range: {key}")
            decimal = Decimal(str(released[key]))
            parameters[suffix] = decimal
            numbers.put(
                prefix + "." + suffix,
                _decimal_text(decimal, 4 if suffix == "free.r" else 3),
            )
            shown[suffix] = numbers.number(prefix + "." + suffix)
            if suffix in summaries:
                summaries[suffix].append((curve.r, decimal))
        if "free.r" in parameters:
            shift = parameters["free.r"] - Decimal(str(released[stem + "cell.r"]))
            numbers.put(prefix + ".free.r_shift", _decimal_text(shift, 4))
            shown["free.r_shift"] = "$" + numbers.number(prefix + ".free.r_shift") + "$"
            summaries["free.r_shift"].append((curve.r, abs(shift)))
        else:
            shown["free.r_shift"] = "not available"
        point = stem + "free.attempts.i000.points.i000."
        fields = (
            "signal",
            "parameters.i000",
            "parameters.i001",
            "residual.i002",
            "se.i002",
            "residual_se_units.i002",
        )
        missing = [
            point + field
            for field in fields
            if released.get(point + field) in (None, "unavailable")
        ]
        if missing or released.get(stem + "known.success") != "true":
            shown["l3_miss_se"] = "not available"
            unavailable = ", ".join(missing) or stem + "known.success"
            notes.append(
                f"{prefix}.l3_miss_se: true-share fit unavailable: {unavailable}"
            )
        else:
            values = {
                field: _finite_float(
                    released[point + field], "Free-share fit " + point + field
                )
                for field in fields
            }
            if values["signal"] != curve.r or released.get(
                point + "inner_status"
            ) not in ("interior", "edge"):
                raise ValueError(
                    f"Free-share fit true-share point identity mismatch: {point}"
                )
            for suffix, index in (("known.phi", "i000"), ("known.lambda", "i001")):
                if suffix in parameters and values["parameters." + index] != float(
                    parameters[suffix]
                ):
                    raise ValueError(
                        f"Free-share fit true-share parameters mismatch: {point}"
                    )
            se = values["se.i002"]
            standardized = values["residual_se_units.i002"]
            if se <= 0 or not math.isclose(
                standardized, values["residual.i002"] / se, rel_tol=1e-5, abs_tol=1e-6
            ):
                raise ValueError(
                    f"Free-share fit lag-three residual/SE mismatch: {point}"
                )
            miss = -Decimal(str(released[point + "residual_se_units.i002"]))
            numbers.put(prefix + ".l3_miss_se", _decimal_text(miss, 1))
            shown["l3_miss_se"] = "$" + numbers.number(prefix + ".l3_miss_se") + "$"
            summaries["l3_miss_se"].append((curve.r, miss))
        rows.append(
            [
                numbers.number(curve.prefix + ".r"),
                numbers.number(curve.prefix + ".first.point"),
                *(
                    shown[suffix]
                    for suffix in (
                        "known.phi",
                        "known.lambda",
                        "free.phi",
                        "free.lambda",
                        "free.r",
                        "free.r_shift",
                        "l3_miss_se",
                    )
                ),
            ]
        )
    for suffix, entries in summaries.items():
        if len(entries) != len(RELIABILITIES):
            notes.append(f"j.x3.{suffix} extrema: incomplete boundary cells; omitted")
            continue
        decimals = 4 if suffix == "free.r_shift" else 1 if suffix == "l3_miss_se" else 3
        for end, select in (("min", min), ("max", max)):
            _, extreme = select(entries, key=lambda entry: entry[1])
            key = "j.x3." + suffix + "." + end
            numbers.put(key, _decimal_text(extreme, decimals))
            numbers.put(
                key + ".r",
                ", ".join(f"{r:.2f}" for r, estimate in entries if estimate == extreme),
            )
    return _table(
        "tab:x3-fit",
        "Known-share and free-share persistence fits at the first boundary.",
        r"l@{\quad}l@{\quad}" + "p{12mm}" * 4 + "p{15mm}p{15mm}p{18mm}",
        [
            "Design $r$",
            "$a^*$",
            "Known $\\phi$",
            "Known $\\lambda$",
            "Free $\\phi$",
            "Free $\\lambda$",
            "Fitted $r_B$",
            "$r_B-r$",
            "Lag-three miss (fit SEs)",
        ],
        rows,
        note=(
            "The share shift is fitted minus design share. The signed lag-three "
            "miss is influence minus B at the true share, divided by the matching "
            "attempt's standard error. It uses matching panels; the mean lag "
            r"differences in Table~\ref{tab:x3-lags} use check panels. The "
            "free-share fit also matches lag three; the contributions of the share "
            "shift and the extra matched lag were not disentangled."
        ),
    ), notes


def _x3_lags_table(
    numbers: Numbers, catalog: Mapping[str, Any], main: Sequence[JournalCurve]
) -> tuple[str | None, list[str]]:
    """Tabulate catalog means at the public main B first-boundary cells.

    v4x.x3.cells.<r>.<a>.means.social/known/free.i000 through i004 are
    population-averaged lag-one-through-five correlations over the check panels
    of the free-share analysis. For lags three through five (i002/i003/i004),
    j.x3.lag_shortfall.<r>.l<lag> is social minus known and .free.l<lag> is
    social minus free. Subtract the catalog decimal strings exactly, then round
    half-even to four decimals, suppress negative zero, and keep ASCII minus in
    values; table math renders the minus.
    negative.n and increasing.n count known-share contrasts using unrounded
    differences and strict comparisons, only when all nine triplets exist.
    ratio_l5_l3.min/max use the unrounded L5/L3 shortfall ratios at the same
    nine cells, rounded half-even to one decimal; a zero L3 omits the range.
    """
    released = catalog.get("values", {})
    if not any(
        key.startswith("v4x.x3.cells.") and ".means." in key for key in released
    ):
        return None, ["j.x3 lag means: none released in the catalog; table omitted"]
    notes: list[str] = []
    rows = []
    known_differences: list[list[Decimal]] = []
    ratios: list[Decimal] = []
    for curve, stem in _x3_boundary_cells(numbers, catalog, main):
        means: dict[str, list[Decimal | None]] = {}
        for group in ("social", "known", "free"):
            means[group] = []
            for lag in (3, 4, 5):
                key = stem + f"means.{group}.i{lag - 1:03d}"
                if released.get(key) in (None, "unavailable") or (
                    group != "social"
                    and released.get(stem + group + ".success") != "true"
                ):
                    means[group].append(None)
                    notes.append(
                        f"j.x3 lag means: {key} not available from a valid fit"
                    )
                    continue
                value = _finite_float(released[key], key)
                if not -1 <= value <= 1:
                    raise ValueError(f"Released lag correlation out of range: {key}")
                means[group].append(Decimal(str(released[key])))
        row = [
            numbers.number(curve.prefix + ".r"),
            numbers.number(curve.prefix + ".first.point"),
        ]
        for group in ("known", "free"):
            differences = []
            for lag, social, reference in zip(
                (3, 4, 5), means["social"], means[group], strict=True
            ):
                if social is None or reference is None:
                    row.append("not available")
                    continue
                difference = social - reference
                differences.append(difference)
                key = f"j.x3.lag_shortfall.{r_tag(curve.r)}."
                key += ("free." if group == "free" else "") + f"l{lag}"
                numbers.put(key, _decimal_text(difference, 4))
                row.append("$" + numbers.number(key) + "$")
            if group == "known" and len(differences) == 3:
                known_differences.append(differences)
                if differences[0] == 0:
                    notes.append(
                        f"j.x3 ratio: zero lag-three shortfall at {stem}; omitted"
                    )
                else:
                    ratios.append(differences[2] / differences[0])
        rows.append(row)
    if len(known_differences) == len(RELIABILITIES):
        numbers.put(
            "j.x3.lag_shortfall.negative.n",
            str(sum(all(d < 0 for d in values) for values in known_differences)),
        )
        numbers.put(
            "j.x3.lag_shortfall.increasing.n",
            str(sum(abs(d3) < abs(d4) < abs(d5) for d3, d4, d5 in known_differences)),
        )
    else:
        notes.append("j.x3 lag-shortfall counts: incomplete known-share means; omitted")
    if len(ratios) == len(RELIABILITIES):
        for end, ratio in (("min", min(ratios)), ("max", max(ratios))):
            numbers.put(
                "j.x3.lag_shortfall.ratio_l5_l3." + end, _decimal_text(ratio, 1)
            )
    else:
        notes.append("j.x3 lag-shortfall ratios: incomplete nonzero triplets; omitted")
    return _table(
        "tab:x3-lags",
        "Mean lag-correlation differences at the first boundary: influence minus "
        "known-share B and influence minus free-share B. These are means over the "
        "check panels of the free-share analysis.",
        r"l@{\quad}l@{\quad}" + "p{16mm}" * 6,
        [
            "Design $r$",
            "$a^*$",
            "Known: lag three",
            "Known: lag four",
            "Known: lag five",
            "Free: lag three",
            "Free: lag four",
            "Free: lag five",
        ],
        rows,
        note=(
            "Each row selects the first boundary of the main classifier against "
            "trait-plus-autoregressive persistence (B). The differences use the "
            "mean correlations recorded in the free-share analysis. Known-share B "
            "matches lags one and two; free-share B also fits the signal share "
            "and matches lag three."
        ),
    ), notes


def _x3_grid_values(numbers: Numbers, catalog: Mapping[str, Any]) -> list[str]:
    """Project accepted interior fits and archived free-gap readings by strength."""
    released = catalog.get("values", {})
    status_pattern = r"v4x\.x3\.cells\.r\d{3}\.a\d{4}\.free\.attempts\.i\d{3}\.status"
    statuses = {
        key: value
        for key, value in released.items()
        if re.fullmatch(status_pattern, key)
    }
    if not statuses:
        return ["j.x3 free-share grid: no released attempt statuses; omitted"]
    fitted: list[tuple[float, Decimal, str]] = []
    gaps: Counter[float] = Counter()
    for key in sorted(released):
        if not re.fullmatch(r"v4x\.x3\.cells\.r\d{3}\.a\d{4}\.cell\.a", key):
            continue
        stem = key.removesuffix("cell.a")
        a = _released_float(numbers, catalog, key)
        r = _released_float(numbers, catalog, stem + "cell.r")
        if (
            a not in GRID
            or r not in RELIABILITIES
            or stem != f"v4x.x3.cells.{r_tag(r)}.{a_tag(a)}."
            or released.get(stem + "cell.family") != "B"
            or released.get(stem + "cell.channel") != "observed"
        ):
            raise ValueError(f"Free-share grid cell identity mismatch: {stem}")
        success = released.get(stem + "free.success")
        if released.get(stem + "reading") == "free-gap":
            if success != "false":
                raise ValueError(f"Free-share gap/success mismatch: {stem}")
            gaps[a] += 1
        if success != "true":
            continue
        attempts = sorted(key for key in statuses if key.startswith(stem))
        if not attempts:
            raise ValueError(f"Free-share grid accepted fit lacks status: {stem}")
        if statuses[attempts[-1]] != "interior":
            continue
        signal = _released_float(numbers, catalog, stem + "free.parameters.signal")
        if not 0 <= signal <= 1:
            raise ValueError(f"Free-share grid fitted share out of range: {stem}")
        shift = Decimal(str(released[stem + "free.parameters.signal"])) - Decimal(
            str(released[stem + "cell.r"])
        )
        fitted.append((a, shift, stem))
    high = [entry for entry in fitted if entry[0] >= 0.01]
    numbers.put("j.x3.free.fits.n", str(len(high)))
    numbers.put(
        "j.x3.free.r_shift.negative.n", str(sum(shift < 0 for _, shift, _ in high))
    )
    notes = []
    for a in (0.01, 0.03, 0.1, 0.3, 0.6):
        shifts = [abs(shift) for strength, shift, _ in fitted if strength == a]
        prefix = "j.x3.free.r_shift." + a_tag(a)
        numbers.put(prefix + ".n", str(len(shifts)))
        if shifts:
            numbers.put(prefix + ".min", _decimal_text(min(shifts), 4))
            numbers.put(prefix + ".max", _decimal_text(max(shifts), 4))
        else:
            notes.append(prefix + ": no accepted interior fits; extrema omitted")
    low = [abs(shift) for a, shift, _ in fitted if a <= 0.003]
    numbers.put("j.x3.free.r_shift.low.n", str(len(low)))
    if low:
        numbers.put("j.x3.free.r_shift.low.max", _decimal_text(max(low), 4))
    else:
        notes.append("j.x3.free.r_shift.low.max: no accepted interior fits; omitted")
    strongest = [stem for a, _, stem in fitted if a == 0.6]
    prefix = "j.x3.free.a6000."
    numbers.put(prefix + "fits.n", str(len(strongest)))
    parameters: dict[str, list[Decimal]] = {"lambda": [], "phi": [], "auc": []}
    for stem in strongest:
        for suffix, field_name, upper in (
            ("lambda", "free.parameters.eta", 0.8),
            ("phi", "free.parameters.phi", 0.999),
            ("auc", "free.auc", 1),
        ):
            value = _released_float(numbers, catalog, stem + field_name)
            if not 0 <= value <= upper:
                raise ValueError(
                    f"Free-share grid parameter/AUC out of range: {stem + field_name}"
                )
            parameters[suffix].append(Decimal(str(released[stem + field_name])))
    numbers.put(
        prefix + "lambda_zero.n", str(sum(value == 0 for value in parameters["lambda"]))
    )
    for suffix in ("phi", "auc"):
        if parameters[suffix]:
            numbers.put(
                prefix + suffix + ".min", _decimal_text(min(parameters[suffix]), 3)
            )
            numbers.put(
                prefix + suffix + ".max", _decimal_text(max(parameters[suffix]), 3)
            )
        else:
            notes.append(
                prefix + suffix + ": no accepted interior fits; extrema omitted"
            )
    if _released_float(numbers, catalog, "v4x.x3.count.free-gap") != sum(gaps.values()):
        raise ValueError("Free-share gap sum differs from released free-gap count")
    for a, count in sorted(gaps.items()):
        numbers.put("j.x3.free_gap." + a_tag(a) + ".n", str(count))
    return notes


def _x3_plus_values(
    numbers: Numbers, catalog: Mapping[str, Any], main: Sequence[JournalCurve]
) -> list[str]:
    """Select the unique r + 0.01 recorded trial on matching panels per boundary."""
    released = catalog.get("values", {})
    pattern = (
        r"v4x\.x3\.cells\.r\d{3}\.a\d{4}\.free\.attempts\.i\d{3}"
        r"\.points\.i\d{3}\.signal"
    )
    points = [key for key in released if re.fullmatch(pattern, key)]
    if not any(".points.i000." not in key for key in points):
        return ["j.x3 plus trials: no released search beyond initial points; omitted"]
    summaries: dict[str, list[tuple[float, Decimal]]] = {"lambda": [], "l3_miss": []}
    for curve, stem in _x3_boundary_cells(numbers, catalog, main):
        target = Decimal(str(released[stem + "cell.r"])) + Decimal("0.01")
        matches = []
        for key in sorted(points):
            if key.startswith(stem):
                _finite_float(released[key], "Free-share plus trial " + key)
                if Decimal(str(released[key])) == target:
                    matches.append(key.removesuffix("signal"))
        if len(matches) != 1:
            raise ValueError(
                f"Free-share plus trial requires one exact r + 0.01 point: {stem}; "
                f"found {len(matches)}"
            )
        point = matches[0]
        if released.get(point + "inner_status") not in ("interior", "edge"):
            raise ValueError(f"Free-share plus trial inner fit unavailable: {point}")
        for suffix, source in (
            ("phi", "parameters.i000"),
            ("lambda", "parameters.i001"),
            ("l3_miss", "residual.i002"),
        ):
            value = _released_float(numbers, catalog, point + source)
            if suffix != "l3_miss" and not 0 <= value <= (
                0.999 if suffix == "phi" else 0.8
            ):
                raise ValueError(
                    f"Free-share plus trial parameter out of range: {point + source}"
                )
            decimal = Decimal(str(released[point + source]))
            numbers.put(
                "j.x3." + r_tag(curve.r) + ".plus." + suffix,
                _decimal_text(decimal, 4 if suffix == "l3_miss" else 3),
            )
            if suffix in summaries:
                summaries[suffix].append((curve.r, decimal))
    numbers.put("j.x3.plus.offset", "0.01")
    for suffix, entries in summaries.items():
        for end, select in (("min", min), ("max", max)):
            _, extreme = select(entries, key=lambda entry: entry[1])
            key = "j.x3.plus." + suffix + "." + end
            numbers.put(key, _decimal_text(extreme, 4 if suffix == "l3_miss" else 3))
            numbers.put(
                key + ".r",
                ", ".join(f"{r:.2f}" for r, value in entries if value == extreme),
            )
    return []


def _x5_signature_values(
    numbers: Numbers, aggregate: Mapping[str, Any], catalog: Mapping[str, Any]
) -> str:
    """Summarize sanitized X5 cells[].estimate.lags at a = 0 against B.

    Subtract null_mean from data_mean at indices 2, 3, 4 (lags three to five),
    checking the stored data_minus_null. Count only estimated, successful cells.
    Negative means all three differences < 0; increasing means |L3| < |L4| < |L5|.
    Median L5/L3 is calculated per declared channel.name from unrounded means.
    Failed fits have no lag estimates and contribute to neither counts nor ratios.
    These descriptive signatures do not evaluate the influence-trained score.
    """
    if aggregate.get("schema") != "ic-study.v4-exploratory-x5.v1":
        raise ValueError("Stress signature requires the sanitized X5 aggregate schema")
    conditions = [condition["name"] for condition in aggregate["conditions"]]
    if len(set(conditions)) != len(conditions) or any(
        not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) for name in conditions
    ):
        raise ValueError("Stress signature condition names are invalid or duplicated")
    ratios: dict[str, list[Decimal]] = {}
    seen: set[tuple[str, float]] = set()
    rows = []
    estimated = negative = increasing = 0
    for cell in sorted(
        aggregate["cells"],
        key=lambda c: (
            conditions.index(c["channel"]["name"])
            if c["channel"]["name"] in conditions
            else -1,
            c["r"],
        ),
    ):
        condition = cell["channel"]["name"]
        r = _finite_float(cell["r"], "Stress signature share")
        identity = (condition, r)
        if (
            condition not in conditions
            or r not in RELIABILITIES
            or cell["a"] != 0
            or cell["family"] != "B"
            or identity in seen
        ):
            raise ValueError(f"Stress signature cell identity mismatch: {identity}")
        seen.add(identity)
        estimate = cell.get("estimate")
        if estimate is None and cell["success"] is False:
            continue
        if estimate is None or cell["success"] is not True:
            raise ValueError(f"Stress signature estimate/success mismatch: {identity}")
        lags = estimate["lags"]
        means: dict[str, list[Decimal]] = {}
        for group in ("data_mean", "null_mean", "data_minus_null"):
            values = lags[group]
            if len(values) != 5:
                raise ValueError(
                    f"Stress signature requires five lag means: {identity}"
                )
            for value in values:
                number = _finite_float(value, "Stress signature " + group)
                if abs(number) > (2 if group == "data_minus_null" else 1):
                    raise ValueError(
                        f"Stress signature lag correlation out of range: {identity}"
                    )
            means[group] = [Decimal(str(value)) for value in values]
        differences = [
            data - null
            for data, null in zip(means["data_mean"], means["null_mean"], strict=True)
        ]
        if any(
            abs(delta - recorded) > Decimal("1e-14")
            for delta, recorded in zip(
                differences, means["data_minus_null"], strict=True
            )
        ):
            raise ValueError(
                f"Stress signature stored differences mismatch: {identity}"
            )
        d3, d4, d5 = differences[2:5]
        estimated += 1
        negative += all(d < 0 for d in (d3, d4, d5))
        increasing += abs(d3) < abs(d4) < abs(d5)
        if d3 == 0:
            raise ValueError(
                f"Stress signature ratio has a zero lag-three denominator: {identity}"
            )
        ratios.setdefault(condition, []).append(d5 / d3)
        labels = {
            "trend-003": ("Signal-share trend, $\\pm", "0.03", "$"),
            "trend-008": ("Signal-share trend, $\\pm", "0.08", "$"),
            "mnar-ln15": ("Attrition, odds ratio ", "1.5", ""),
            "mnar-ln2": ("Attrition, odds ratio ", "2", ""),
        }
        if condition not in labels:
            raise ValueError(
                f"Stress lag table has no plain condition label: {condition}"
            )
        prefix = "j.x5." + condition + "." + r_tag(r)
        parameters = cell.get("parameters")
        if not isinstance(parameters, list) or len(parameters) != 2:
            raise ValueError(
                f"Stress lag table requires fitted phi and trait weight: {identity}"
            )
        for suffix, value, upper in (
            ("phi", parameters[0], 0.999),
            ("lambda", parameters[1], 0.8),
            ("auc", estimate.get("auc"), 1),
        ):
            number = _finite_float(value, "Stress lag table " + suffix)
            if not 0 <= number <= upper:
                raise ValueError(
                    f"Stress lag table parameter/AUC out of range: {identity}"
                )
            if suffix == "auc":
                share = f"{r:g}".replace(".", "-")
                source = (
                    f"v4x.comparisons.by_r.{share}.x5.{r_tag(r)}.a0000."
                    f"{condition}.estimate.auc"
                )
                for values in (numbers.final, catalog.get("values", {})):
                    if source in values and values[source] != f"{number:.6g}":
                        raise ValueError(
                            "Stress lag table AUC differs from released value: "
                            + source
                        )
            numbers.put(prefix + "." + suffix, _decimal_text(Decimal(str(value)), 3))
        for lag, difference in zip((3, 4, 5), (d3, d4, d5), strict=True):
            numbers.put(prefix + f".l{lag}", _decimal_text(difference, 4))
        label, amount, closing = labels[condition]
        amount_key = "j.x5." + condition + ".amount"
        numbers.put(amount_key, amount)
        rows.append(
            [
                label + numbers.number(amount_key) + closing,
                numbers.number("j.b." + r_tag(r) + ".r"),
                numbers.number(prefix + ".phi"),
                numbers.number(prefix + ".lambda"),
                *("$" + numbers.number(prefix + f".l{lag}") + "$" for lag in (3, 4, 5)),
                numbers.number(prefix + ".auc"),
            ]
        )
    for suffix, value in (
        ("cells", estimated),
        ("negative.n", negative),
        ("increasing.n", increasing),
    ):
        numbers.put("j.x5.signature." + suffix, str(value))
    for condition, values in sorted(ratios.items()):
        numbers.put(
            "j.x5.signature.ratio_l5_l3.median." + condition,
            _decimal_text(median(values), 1),
        )
    return _table(
        "tab:x5-lags",
        "Mean lag differences under channel misspecification on check panels at $a="
        + numbers.number("j.grid.a0000")
        + "$ with B fitted at the known share. The influence-trained score was "
        "not evaluated on these panels.",
        "p{36mm}lllllll",
        [
            "Condition",
            "$r$",
            "$\\phi$",
            "$\\lambda$",
            "Lag three",
            "Lag four",
            "Lag five",
            "AUC",
        ],
        rows,
        note="Lag differences are the influence-free arm minus fitted B, averaged "
        "over check panels. "
        "AUCs are from the recorded stress classifier. Only estimated cells are shown; "
        "the wave-step and conditioning fits were unavailable.",
        colsep="5pt",
    )


def _exploratory_values(
    numbers: Numbers, catalog: Mapping[str, Any], main: Sequence[JournalCurve]
) -> list[str]:
    """Use only v4x keys in the final values, never exploratory raw files.

    Boundary comparisons: v4x.comparisons.by_r.<r>.x3.delta.point and
    .x4.P_or.statistics.power_or. Expanded features: v4x.x7.units.<r>.rich.first
    (the .x7.first field is the baseline comparator), and .delta_auc.i004.delta
    after validating its .a field as 0.03. The catalog's x3.cell.a and x4.P_or.a
    must match main_curve.first.point and the public B first boundary.
    Fitted test at zero:
    v4x.x4.x4b.r050.a0000.x4b.power_pu and .power_pu_interval_95.i000/i001.
    Frozen-feature boundaries: v4x.x7.units.<r>.x7.first. The additional
    single-panel keys are v4x.comparisons.by_r.0-9.x1b.first.point and
    v4x.x4.x4a.r070.a0010.x4a.auc_ref (validated against .cell.a). Band coverage
    counting gaps as misses uses v4x.x6.x6a.band.vs_d1.gaps_as_misses.covered,
    .total and .wilson95.i000/i001; the percentage is covered / total * 100.
    X1a and X2 are absent from the final values and catalog supplied for this
    revision. They are reported unavailable rather than read from another input.
    """
    patterns = {
        "j.x3.auc_reduction": r"v4x\.comparisons\.by_r\.(\d+-\d+)\.x3\.delta\.point",
        "j.x4a.boundary_rejection": (
            r"v4x\.comparisons\.by_r\.(\d+-\d+)\.x4\.P_or\.statistics\.power_or"
        ),
        "j.x7.first": r"v4x\.x7\.units\.r(\d+)\.rich\.first",
        "j.x7.frozen_first": r"v4x\.x7\.units\.r(\d+)\.x7\.first",
        "j.x7.auc_gain.a0300": r"v4x\.x7\.units\.r(\d+)\.delta_auc\.i004\.delta",
    }
    notes = []
    main_by_r = {c.r: c for c in main}
    for prefix, pattern in patterns.items():
        entries = []
        for key in numbers.final:
            match = re.fullmatch(pattern, key)
            if match is None:
                continue
            share = match[1]
            r = float(share.replace("-", ".")) if "-" in share else int(share) / 100
            value = _released_float(numbers, catalog, key)
            if prefix in ("j.x3.auc_reduction", "j.x4a.boundary_rejection"):
                stem = f"v4x.comparisons.by_r.{share}."
                expected = _released_float(
                    numbers, catalog, stem + "main_curve.first.point"
                )
                source = "x3.cell.a" if prefix == "j.x3.auc_reduction" else "x4.P_or.a"
                a = _released_float(numbers, catalog, stem + source)
                if (
                    a != expected
                    or r not in main_by_r
                    or expected != main_by_r[r].record["first"]["point"]
                ):
                    raise ValueError(
                        f"Released boundary strength mismatch: {stem + source}"
                    )
            if prefix == "j.x7.auc_gain.a0300" and (
                _released_float(numbers, catalog, key.removesuffix("delta") + "a")
                != 0.03
            ):
                raise ValueError(f"Expanded-feature strength mismatch: {key}")
            if prefix == "j.x3.auc_reduction":
                value = -value
            entries.append((r, value))
        if not entries:
            notes.append(prefix + ": no numeric released values")
            continue
        _nine_shares(prefix, entries)
        if prefix == "j.x4a.boundary_rejection":
            numbers.put(prefix + ".r050", f"{dict(entries)[0.5]:.3f}")
            entries = [(r, value) for r, value in entries if r >= 0.55]
        _extrema(
            numbers,
            prefix,
            entries,
            grid=prefix in ("j.x7.first", "j.x7.frozen_first"),
            with_shares=prefix != "j.x7.frozen_first",
        )
    zero = "v4x.x4.x4b.r050.a0000.x4b."
    for suffix, source in (
        ("", "power_pu"),
        (".lower", "power_pu_interval_95.i000"),
        (".upper", "power_pu_interval_95.i001"),
    ):
        zero_text = numbers.final.get(zero + source)
        if zero_text is None or zero_text == "unavailable":
            notes.append("j.x4b.zero_rejection.r050" + suffix + ": not in final values")
        else:
            numbers.put("j.x4b.zero_rejection.r050" + suffix, f"{float(zero_text):.3f}")
    for target, source, decimals in (
        ("j.x1b.r090.first.point", "v4x.comparisons.by_r.0-9.x1b.first.point", 2),
        ("j.x4a.r070.a0010.auc_ref", "v4x.x4.x4a.r070.a0010.x4a.auc_ref", 3),
    ):
        if source not in numbers.final:
            notes.append(target + ": not in final values; omitted")
            continue
        if (
            target == "j.x4a.r070.a0010.auc_ref"
            and _released_float(numbers, catalog, "v4x.x4.x4a.r070.a0010.cell.a")
            != 0.001
        ):
            raise ValueError("Oracle reference strength mismatch")
        numbers.put(target, f"{_released_float(numbers, catalog, source):.{decimals}f}")
    coverage = "v4x.x6.x6a.band.vs_d1.gaps_as_misses."
    if any(key.startswith(coverage) for key in numbers.final):
        covered = _released_float(numbers, catalog, coverage + "covered")
        total = _released_float(numbers, catalog, coverage + "total")
        if (
            total <= 0
            or not 0 <= covered <= total
            or covered != int(covered)
            or total != int(total)
        ):
            raise ValueError("Invalid released coverage counts")
        numbers.put("j.x6.gaps_as_misses.percent", f"{100 * covered / total:.0f}")
        for suffix, index in (("lower", "i000"), ("upper", "i001")):
            value = _released_float(numbers, catalog, coverage + "wilson95." + index)
            numbers.put("j.x6.gaps_as_misses.wilson." + suffix, f"{value:.3f}")
    else:
        notes.append("j.x6.gaps_as_misses: not in final values; omitted")
    for group in ("x1a", "x2"):
        numbers.put("j." + group + ".available", "no")
        notes.append(group + ": no released final-value keys; quantities omitted")
    return notes


def _round3_values(
    numbers: Numbers, catalog: Mapping[str, Any], main: Sequence[JournalCurve]
) -> list[str]:
    """Project the round-3 diagnostics without estimating new scientific results.

    Margin factors use the full-precision public point AUC and upper band at 0.03,
    on the logit scale. The common critical value cancels in their ratio.
    The nuisance bound is v4.gate.G2c.a003.lower (a003 denotes 0.03 here).

    X3 uses catalog v4x.x3.cells.<r>.<a>.free.success and .lost_crossing.
    The denominator counts successful free-share fits at 0.10, 0.30 and 0.60.
    The numerator counts the frozen true flags among those cells: known-share
    point AUC >= 0.70 AND the free-share 95% interval's upper end < 0.70.
    This is not a count of free-share point estimates below 0.70. Validate it
    against v4x.x3.count.lost_crossing, without reclassifying rounded estimates.

    X4a uses v4x.x4.x4a.<r>.<a>.x4a.auc_ref and
    .auc_ref_interval_95.i000/i001, with .cell.a/r checked. X7's frozen-feature
    boundary is v4x.x7.units.r055.x7.first, not .rich.first.
    """
    notes = []
    factors = []

    def logit(p: float) -> float:
        return math.log(p / (1 - p))

    for curve in main:
        point, upper = curve.estimate(0.03, "auc"), curve.estimate(0.03, "upper")
        if point is None or upper is None or not 0 < point < upper < 0.70:
            raise ValueError(f"Invalid band for logit margin: {curve.key}")
        factor = (logit(0.70) - logit(point)) / (logit(upper) - logit(point))
        factors.append((curve.r, factor))
        numbers.put("j.b.margin.a0300.se_factor." + r_tag(curve.r), f"{factor:.1f}")
    if factors:
        _nine_shares("B logit margin", factors)
        minimum = min(value for _, value in factors)
        numbers.put("j.b.margin.a0300.se_factor.min", f"{minimum:.1f}")
        numbers.put(
            "j.b.margin.a0300.se_factor.min.r",
            ", ".join(f"{r:.2f}" for r, value in factors if value == minimum),
        )
    gate = "v4.gate.G2c.a003.lower"
    if gate in numbers.final:
        lower = _released_float(numbers, catalog, gate)
        if not 0 < lower <= 1:
            raise ValueError("Invalid nuisance-variance lower bound")
        numbers.put("j.gate.g2c.a0300.se_growth_max", f"{1 / math.sqrt(lower):.2f}")
    else:
        notes.append("j.gate.g2c.a0300.se_growth_max: not in final values; omitted")
    released = dict(catalog.get("values", {}))
    released.update(numbers.final)
    cells = [
        key.removesuffix(".cell.a")
        for key in released
        if re.fullmatch(r"v4x\.x3\.cells\.r\d+\.a\d+\.cell\.a", key)
    ]
    if cells:
        fitted = []
        for stem in cells:
            a = _released_float(numbers, catalog, stem + ".cell.a")
            if a not in (0.1, 0.3, 0.6):
                continue
            success = released.get(stem + ".free.success")
            if success not in ("true", "false", "unavailable"):
                raise ValueError(f"Missing free-share fit state: {stem}")
            if success == "true":
                if released.get(stem + ".lost_crossing") not in ("true", "false"):
                    raise ValueError(f"Missing frozen lost-crossing flag: {stem}")
                fitted.append(stem)
        lost = sum(released[stem + ".lost_crossing"] == "true" for stem in fitted)
        if _released_float(numbers, catalog, "v4x.x3.count.lost_crossing") != lost:
            raise ValueError("Frozen lost-crossing count differs from fitted cells")
        numbers.put("j.x3.lost_crossings.n", str(lost))
        numbers.put("j.x3.lost_crossings.cells", str(len(fitted)))
    else:
        notes.append("j.x3.lost_crossings: no released cell keys; omitted")
    source = "v4x.x7.units.r055.x7.first"
    if source in numbers.final:
        numbers.put(
            "j.x7.frozen_first.r055",
            strength(_released_float(numbers, catalog, source)),
        )
    else:
        notes.append("j.x7.frozen_first.r055: not in final values; omitted")
    stem = "v4x.x4.x4a.r055.a1000."
    if stem + "x4a.auc_ref" in numbers.final:
        if (
            _released_float(numbers, catalog, stem + "cell.a") != 0.1
            or _released_float(numbers, catalog, stem + "cell.r") != 0.55
        ):
            raise ValueError("Oracle reference cell mismatch")
        for suffix, field_name in (
            ("", "auc_ref"),
            (".lower", "auc_ref_interval_95.i000"),
            (".upper", "auc_ref_interval_95.i001"),
        ):
            numbers.put(
                "j.x4a.r055.a1000.auc_ref" + suffix,
                f"{_released_float(numbers, catalog, stem + 'x4a.' + field_name):.3f}",
            )
    else:
        notes.append("j.x4a.r055.a1000.auc_ref: not in final values; omitted")
    references = []
    for key in numbers.final:
        match = re.fullmatch(r"v4x\.x4\.x4a\.r(\d+)\.a0300\.x4a\.auc_ref", key)
        if match is None:
            continue
        r = int(match[1]) / 100
        stem = key.removesuffix("x4a.auc_ref")
        if (
            _released_float(numbers, catalog, stem + "cell.a") != 0.03
            or _released_float(numbers, catalog, stem + "cell.r") != r
        ):
            raise ValueError("Oracle reference cell mismatch")
        references.append((r, _released_float(numbers, catalog, key)))
    if references:
        _nine_shares("Oracle reference AUC at 0.03", references)
        maximum = max(value for _, value in references)
        numbers.put("j.x4a.a0300.auc_ref.max", f"{maximum:.3f}")
        numbers.put(
            "j.x4a.a0300.auc_ref.max.r",
            ", ".join(
                f"{r:.2f}" for r, value in sorted(references) if value == maximum
            ),
        )
    else:
        notes.append("j.x4a.a0300.auc_ref.max: not in final values; omitted")
    return notes


def _cell_tables(
    numbers: Numbers, main: Sequence[JournalCurve]
) -> tuple[str, list[str]]:
    rows = []
    standard_errors = {"score_se": 0, "nuisance_se": 0}
    available_errors = [
        kind
        for kind in standard_errors
        if any(
            isinstance(diagnostic, dict) and diagnostic.get(kind) is not None
            for curve in main
            for diagnostic in curve.record.get("diagnostics", [])
        )
    ]
    for curve in main:
        prefix = curve.prefix
        for index, a in enumerate(GRID):
            cell = prefix + "." + a_tag(a)
            diagnostic = (curve.record.get("diagnostics") or [None] * len(GRID))[index]
            errors = []
            for kind in standard_errors:
                value = diagnostic.get(kind) if isinstance(diagnostic, dict) else None
                if value is not None:
                    numbers.put(cell + "." + kind, f"{float(value):.3f}")
                    standard_errors[kind] += 1
                    errors.append(numbers.number(cell + "." + kind))
                else:
                    errors.append("---")
            errors = [
                value
                for kind, value in zip(standard_errors, errors, strict=True)
                if kind in available_errors
            ]
            gap = curve.record["cell_gap"][index]
            state = "available" if gap is None else "fit gap: " + GAP_NAMES[gap]
            numbers.put(cell + ".state", state)
            estimates = [
                numbers.number(cell + "." + kind) if gap is None else "---"
                for kind in ("auc", "lower", "upper")
            ]
            rows.append(
                [
                    numbers.number(prefix + ".r", f"v4.tab.T1.B.{r_tag(curve.r)}.r"),
                    numbers.number("j.grid." + a_tag(a)),
                    *estimates,
                    *errors,
                    numbers.number(prefix + ".critical"),
                    state,
                ]
            )
    for kind, count in standard_errors.items():
        numbers.put("j.b." + kind + ".available", "yes" if count else "no")
    numbers.put("j.b.fitted_parameters.available", "no")
    notes = [
        "B fitted persistence parameters, fit status and retries are absent "
        "from the public curve projection and confirmatory catalog keys."
    ]
    if not any(standard_errors.values()):
        notes.append(
            "B score SE and nuisance SE are absent; "
            "no SE was reconstructed from a band."
        )
    parts = []
    for start in range(0, len(rows), 27):
        part = start // 27
        label = "tab:b-cells" + (f"-part-{chr(97 + part)}" if part else "")
        parts.append(
            _table(
                label,
                "AUC estimates and per-share bands against "
                "trait-plus-autoregressive persistence"
                + (" (continued)." if part else "."),
                "r" * (6 + len(available_errors)) + "p{34mm}",
                [
                    "$r$",
                    "$a$",
                    "AUC",
                    r"\shortstack{Lower\\band}",
                    r"\shortstack{Upper\\band}",
                    *(
                        r"\shortstack{"
                        + ("Score" if kind == "score_se" else "Nuisance")
                        + r"\\SE}"
                        for kind in available_errors
                    ),
                    "Critical",
                    "Cell state",
                ],
                rows[start : start + 27],
                note=(
                    "$r$ is signal share in the continuous response before "
                    "discretization; $a$ is influence strength. AUC is the area "
                    "under the receiver operating characteristic curve. Lower and "
                    "upper band are the limits of that share's band, simultaneous "
                    "over strengths; Critical is the value used to form it. "
                    "Available means an accepted AUC estimate exists; a fit gap "
                    "means it does not. Other solver status means fitting stopped "
                    "for a numerical reason. SE means standard error: score SE "
                    "describes uncertainty from classification scores and nuisance "
                    "SE from fitted persistence parameters. "
                    + (
                        "Score SE and nuisance SE are not in the released artifacts. "
                        if not available_errors
                        else "Dashes mark unavailable standard errors. "
                    )
                    + "Fitted persistence "
                    "parameters, fit status and retries are absent from these "
                    "public inputs."
                    " Dashes indicate unavailable quantities."
                ),
            )
        )
    return "\n".join(parts), notes


def _controls_table(
    numbers: Numbers,
    curves: Sequence[JournalCurve],
    inventory: Mapping[tuple[str, ...], Mapping[str, str]],
) -> str:
    selected = [
        c
        for c in curves
        if c.tier == 3
        and c.family == "B"
        and c.scenario == "main"
        and c.channel in ("latent", "ordinal_one", "latent_rank")
    ]
    shares = sorted({c.r for c in selected})
    indexed = {(c.r, c.channel): c for c in selected}
    rows = []
    at_cut = small = 0
    for r in shares:
        row: list[str] = []
        for channel in ("latent", "ordinal_one", "latent_rank"):
            curve = indexed[(r, channel)]
            prefix = f"j.controls.{channel}.{r_tag(r)}"
            numbers.put(prefix + ".r", f"{r:.2f}")
            numbers.put(prefix + ".status", STATUS[curve.status])
            numbers.put(prefix + ".region", inventory[_identity(curve)]["region"])
            _boundary_values(numbers, curve, "first", prefix + ".first")
            if not row:
                row.append(numbers.number(prefix + ".r"))
            row.append(_boundary_text(numbers, curve, "first", prefix + ".first"))
            if channel == "latent":
                row.append(inventory[_identity(curve)]["region"])
                at_cut += (
                    curve.status == VALID and curve.record["first"]["point"] == 0.03
                )
                small += (
                    curve.status == VALID
                    and inventory[_identity(curve)]["region"] == "small"
                )
        rows.append(row)
    numbers.put("j.controls.latent.n_boundary_a0300", str(at_cut))
    numbers.put("j.controls.latent.n_small", str(small))
    return _table(
        "tab:controls",
        "Measurement-control boundaries against trait-plus-autoregressive persistence.",
        "lp{29mm}lp{29mm}p{29mm}",
        [
            "Design $r$",
            "Latent [interval]",
            "Latent region",
            "Ordinal [interval]",
            "Latent rank [interval]",
        ],
        rows,
        note=(
            "Each row uses the persistence fit for that design signal share $r$, "
            "the latent state's variance share in the continuous response before "
            "discretization. Entries are first boundaries: the first grid strength "
            "whose point AUC reaches "
            + numbers.number("j.target.r070")
            + ", with intervals from inverting bands simultaneous over strengths "
            "of that share. AUC is the area under the receiver operating "
            "characteristic curve. "
            "The latent control is error-free; the ordinal control discretizes "
            "the error-free response; the latent-rank control uses wave-wise "
            "mid-ranks of error-free latent values. Latent region is the protocol's "
            "label: small means a positive boundary with its interval entirely at "
            "or below "
            + numbers.number("j.grid.a0300")
            + " on the nominal scale; indeterminate means the boundary is zero, "
            "the interval crosses that cut-off, or an interval end is censored. "
            "The latent boundary is "
        )
        + numbers.number("j.grid.a0300")
        + " at "
        + numbers.number("j.controls.latent.n_boundary_a0300")
        + " shares; "
        + numbers.number("j.controls.latent.n_small")
        + " shares meet the small-region definition.",
    )


def _summary_values(
    numbers: Numbers, main: Sequence[JournalCurve], rows: Sequence[Mapping[str, str]]
) -> None:
    auc = [(c.r, p) for c in main if (p := c.estimate(0.1, "auc")) is not None]
    _nine_shares("B AUC at 0.10", auc)
    _extrema(
        numbers,
        "j.b.a1000.auc",
        auc,
    )
    upper = [(c.r, p) for c in main if (p := c.estimate(0.03, "upper")) is not None]
    _nine_shares("B upper band at 0.03", upper)
    if upper:
        _, value = max(upper, key=lambda item: item[1])
        numbers.put("j.b.a0300.upper.max", f"{value:.3f}")
        numbers.put(
            "j.b.a0300.upper.max.r",
            ", ".join(f"{r:.2f}" for r, estimate in sorted(upper) if estimate == value),
        )
        numbers.put("j.b.a0300.upper.distance_to_target", f"{0.7 - value:.3f}")
    invalid = [row for row in rows if row["status"] == INVALID]
    c_related = sum(row["family"] == "C" for row in invalid)
    anchoring = sum(
        row["family"] != "C" and row["sensitivity"].startswith("omega")
        for row in invalid
    )
    for suffix, count in (
        ("total", len(invalid)),
        ("c_related", c_related),
        ("anchoring_sensitivities", anchoring),
        ("other", len(invalid) - c_related - anchoring),
    ):
        numbers.put("j.inventory.invalid." + suffix, str(count))


def _sensitivity_values(numbers: Numbers, curves: Sequence[JournalCurve]) -> list[str]:
    notes = []
    for scenario, prefix, kind in (
        ("b000", "j.sensitivity.b000.first", "first"),
        ("omega025", "j.sensitivity.omega025.zero_auc", "auc"),
    ):
        selected = [
            c
            for c in curves
            if c.tier == 5 and c.family == "B" and c.scenario == scenario
        ]
        if len(selected) != 9:
            notes.append(
                f"{prefix}: requires nine shares; found {len(selected)}; "
                "summary omitted"
            )
            continue
        entries = []
        for curve in selected:
            value = (
                curve.estimate(0, "auc")
                if kind == "auc"
                else curve.record["first"]["point"]
            )
            if value is None or (
                kind == "first"
                and (curve.status != VALID or curve.record["first"]["censoring"])
            ):
                raise ValueError(f"Unavailable sensitivity summary value: {curve.key}")
            entries.append((curve.r, float(value)))
        _nine_shares(prefix, entries)
        _extrema(
            numbers, prefix, entries, grid=kind == "first", with_shares=kind == "auc"
        )
    return notes


def _anchoring_gap_values(numbers: Numbers, curves: Sequence[JournalCurve]) -> None:
    for scenario in ("omega075", "omega100"):
        invalid = [
            c
            for c in curves
            if c.tier == 5
            and c.family == "B"
            and c.channel == "observed"
            and c.scenario == scenario
            and c.status == INVALID
        ]
        gaps = Counter(c.record["cell_gap"][GRID.index(0)] for c in invalid)
        if sum(gaps[kind] for kind in ("family_limit", "solver")) != len(invalid):
            raise ValueError(
                f"{scenario} zero-strength gap kind counts must cover all invalid units"
            )
        for kind in ("family_limit", "solver"):
            numbers.put(
                f"j.inventory.invalid.{scenario}.zero_gap.{kind}", str(gaps[kind])
            )


def _finite_float(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Unavailable numeric value: {field_name}") from error
    if not math.isfinite(number):
        raise ValueError(f"Unavailable numeric value: {field_name}")
    return number


def _shp_interval(
    record: Mapping[str, Any], field_name: str, label: str
) -> list[float]:
    value = record.get(field_name)
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"Unavailable {label} {field_name}: expected two endpoints")
    return [_finite_float(end, f"{label} {field_name}") for end in value]


def _shp_fit_flags(fit: Mapping[str, Any], label: str) -> None:
    if fit.get("converged") is not True:
        raise ValueError(f"SHP {label} converged must be true")
    if fit.get("at_parameter_bound") is not False:
        raise ValueError(f"SHP {label} at_parameter_bound must be false")


def _shp_aggregate_checks(
    objects: Mapping[str, Any], aggregate: Mapping[str, Any]
) -> None:
    shp = objects.get("shp")
    if shp is None:
        raise ValueError("SHP public anchor is required to cross-check the aggregate")
    starts = aggregate["successor_1"]["starts_sensitivity"]
    for label, public, approved in (
        ("anchor", shp, aggregate["anchor"]),
        ("STARTS", shp.get("starts"), starts["anchor"]),
    ):
        for field_name in ("year", "estimate", "standard_error", "wald_95_interval"):
            if public is None or public.get(field_name) != approved.get(field_name):
                raise ValueError(f"SHP {label} differs from aggregate: {field_name}")
    if shp["sensitivity_envelope"] != aggregate["sensitivity_envelope"]:
        raise ValueError("SHP specification range differs from aggregate")
    sensitivity = aggregate["sensitivity"]
    for label, fit in (
        ("multiwave", aggregate["multiwave"]),
        ("complete-case", sensitivity["complete_case_multiwave"]),
        ("pre-2004", sensitivity["observed_before_2004_multiwave"]),
        ("STARTS", starts["diagnostics"]),
    ):
        _shp_fit_flags(fit, label)
    wave = aggregate["successor_1"]["wave_2004_description"]
    refresh = wave["first_valid_answer_2004"]
    for label, record, expected in (
        ("STARTS", starts, "admissible"),
        ("wave description", wave, "descriptive"),
        ("refreshment-entry proxy", refresh, "estimated"),
    ):
        if record.get("status") != expected:
            raise ValueError(f"SHP {label} status must be {expected}")
    _shp_fit_flags(refresh["fit"], "refreshment-entry proxy")


def _wave_reliabilities(
    aggregate: Mapping[str, Any], fit: Mapping[str, Any]
) -> dict[int, float]:
    years = aggregate["years"]
    estimates = fit["reliability"]
    if len(years) != len(set(years)) or len(years) != len(estimates):
        raise ValueError("SHP reliability vectors must match the unique years")
    return {
        year: _finite_float(value, f"SHP reliability in {year}")
        for year, value in zip(years, estimates, strict=True)
    }


def _shp_aggregate_values(numbers: Numbers, aggregate: Mapping[str, Any]) -> None:
    multiwave = aggregate["multiwave"]
    sensitivity = aggregate["sensitivity"]
    successor = aggregate["successor_1"]
    starts = successor["starts_sensitivity"]
    wave = successor["wave_2004_description"]
    refresh = wave["first_valid_answer_2004"]
    trait_share = starts["trait_share_of_latent_variance"]
    if refresh["year"] != 2004 or trait_share["year"] != 2004:
        raise ValueError("SHP refreshment and trait-share summaries must refer to 2004")
    reliability = _wave_reliabilities(aggregate, multiwave)
    complete = _wave_reliabilities(aggregate, sensitivity["complete_case_multiwave"])
    pre2004 = _wave_reliabilities(
        aggregate, sensitivity["observed_before_2004_multiwave"]
    )
    counts = aggregate["n_per_wave"]
    if set(counts) != {str(year) for year in aggregate["years"]}:
        raise ValueError("SHP per-wave counts must match the declared years")
    for suffix, count in (
        ("n_any", aggregate["n_people_with_any_response"]),
        ("n_complete", aggregate["n_people_complete"]),
        ("n_pre2004", sensitivity["observed_before_2004_n"]),
        ("n_wave.min", min(counts.values())),
        ("n_wave.max", max(counts.values())),
        ("refresh.n", refresh["n_people"]),
    ):
        if type(count) is not int or count < 0:
            raise ValueError(f"SHP count must be a nonnegative integer: {suffix}")
        numbers.put("j.shp." + suffix, f"{count:,}")
    for suffix, value in (
        ("multiwave.r_t.min", min(reliability.values())),
        ("multiwave.r_t.max", max(reliability.values())),
        ("multiwave.persistence", multiwave["persistence"]),
        (
            "multiwave.max_cc_residual",
            multiwave["max_complete_case_correlation_residual"],
        ),
        ("complete_case.r2004", complete[2004]),
        ("pre2004.r2004", pre2004[2004]),
        ("wave.r2003", wave["primary_fit"]["2003"]["estimate"]),
        ("wave.r2005", wave["primary_fit"]["2005"]["estimate"]),
        ("refresh.r2004", refresh["estimate"]),
        ("refresh.se", refresh["standard_error"]),
        ("starts.persistence", starts["persistence"]),
        ("starts.trait_share_2004", trait_share["value"]),
    ):
        estimate = _finite_float(value, "SHP aggregate " + suffix)
        numbers.put("j.shp." + suffix, f"{estimate:.3f}")


def _heise_windows_table(
    numbers: Numbers, aggregate: Mapping[str, Any], catalog: Mapping[str, Any]
) -> tuple[str | None, list[str]]:
    """Tabulate triplets[].years, heise_reliability and heise_standard_error.

    The wYYYY key names the first year, not the middle wave whose reliability
    Heise estimates under its assumptions. Extrema and spread use the unrounded
    estimates, checked against sensitivity_envelope and v4.shp.env_lo/env_hi.
    others.spread excludes the window starting in 2003; dip2003 is the mean of
    its two adjacent windows (starts 2002 and 2004) minus that window's estimate.
    The approved aggregate contains standard errors but no per-triplet fit flags.
    """
    windows = aggregate.get("triplets")
    if windows is None:
        return None, ["j.shp.heise: no aggregate triplets; table omitted"]
    by_year: dict[int, Mapping[str, Any]] = {}
    for window in windows:
        years = window.get("years")
        if (
            not isinstance(years, list)
            or len(years) != 3
            or any(type(year) is not int for year in years)
            or years != list(range(years[0], years[0] + 3))
            or years[0] in by_year
        ):
            raise ValueError(
                "Heise windows require unique consecutive three-wave years"
            )
        by_year[years[0]] = window
    if set(by_year) != set(range(1999, 2008)):
        raise ValueError("Heise windows require nine starts from 1999 through 2007")
    estimates = {
        start: _finite_float(window.get("heise_reliability"), f"Heise window {start}")
        for start, window in by_year.items()
    }
    if any(not 0 <= value <= 1 for value in estimates.values()):
        raise ValueError("Heise window estimate is outside the reliability range")
    low, high = min(estimates.values()), max(estimates.values())
    if [low, high] != _shp_interval(aggregate, "sensitivity_envelope", "Heise"):
        raise ValueError("Heise window extrema differ from the aggregate envelope")
    for source, value in (("v4.shp.env_lo", low), ("v4.shp.env_hi", high)):
        text = numbers.final.get(source, catalog.get("values", {}).get(source))
        if text is not None and text != f"{value:.3f}":
            raise ValueError(f"Heise window extrema differ from {source}")
    for suffix, value in (("min", low), ("max", high), ("spread", high - low)):
        numbers.put("j.shp.heise." + suffix, f"{value:.3f}")
    others = [value for start, value in estimates.items() if start != 2003]
    numbers.put("j.shp.heise.others.spread", f"{max(others) - min(others):.3f}")
    dip = (estimates[2002] + estimates[2004]) / 2 - estimates[2003]
    numbers.put("j.shp.heise.dip2003", f"{dip:.3f}")
    notes = []
    rows = []
    for start, window in sorted(by_year.items()):
        prefix = f"j.shp.heise.w{start}"
        numbers.put(prefix, f"{estimates[start]:.3f}")
        numbers.put(prefix + ".start", str(start))
        numbers.put(prefix + ".end", str(window["years"][-1]))
        se = window.get("heise_standard_error")
        if se is None:
            shown_se = "not available"
            notes.append(
                f"{prefix}.se: triplets window {start} heise_standard_error absent"
            )
        else:
            value = _finite_float(se, f"Heise window {start} standard error")
            if value < 0:
                raise ValueError(f"Heise window {start} standard error is negative")
            numbers.put(prefix + ".se", f"{value:.3f}")
            shown_se = numbers.number(prefix + ".se")
        rows.append(
            [
                numbers.number(prefix + ".start")
                + "--"
                + numbers.number(prefix + ".end"),
                numbers.number(prefix),
                shown_se,
            ]
        )
    return _table(
        "tab:heise-windows",
        "Heise reliability by three-wave window for the Swiss Household Panel "
        "trust item.",
        "p{42mm}p{36mm}p{42mm}",
        ["Window", "Estimate", "Standard error"],
        rows,
        note=(
            "Estimates and standard errors are copied from the approved aggregate. "
            "Under a first-order Markov latent process and independent errors, "
            "each estimate describes the middle wave's reliability. No per-window "
            "fit flags are recorded. The minimum is "
            + numbers.number("j.shp.heise.min")
            + ", the maximum is "
            + numbers.number("j.shp.heise.max")
            + ", and their spread is "
            + numbers.number("j.shp.heise.spread")
            + "; this range is not a confidence interval."
        ),
    ), notes


def _shp_values(
    numbers: Numbers, objects: Mapping[str, Any], catalog: Mapping[str, Any]
) -> None:
    shp = objects.get("shp")
    if shp is not None:
        interval = _shp_interval(shp, "wald_95_interval", "SHP anchor")
        envelope = _shp_interval(shp, "sensitivity_envelope", "SHP anchor")
        for suffix, value in (
            ("estimate", shp["estimate"]),
            ("wald_lo", interval[0]),
            ("wald_hi", interval[1]),
            ("env_lo", envelope[0]),
            ("env_hi", envelope[1]),
        ):
            text = f"{_finite_float(value, 'SHP anchor ' + suffix):.3f}"
            if numbers.final.get("v4.shp." + suffix) != text:
                numbers.put("j.shp." + suffix, text)
        starts = shp.get("starts")
        if starts is not None:
            interval = _shp_interval(starts, "wald_95_interval", "SHP STARTS")
            if starts["year"] != shp["year"] or starts.get("failure_reasons"):
                raise ValueError("SHP STARTS year or failure_reasons are invalid")
            for suffix, value in (
                ("estimate", starts["estimate"]),
                ("wald_lo", interval[0]),
                ("wald_hi", interval[1]),
            ):
                text = f"{_finite_float(value, 'SHP STARTS ' + suffix):.3f}"
                if catalog.get("values", {}).get("v4.shp.starts." + suffix) != text:
                    raise ValueError(f"SHP STARTS value differs from catalog: {suffix}")
                numbers.put("j.shp.starts." + suffix, text)
    crosswalk = objects.get("crosswalk")
    if crosswalk is None:
        return
    if crosswalk["declared_plan"] is not True:
        raise ValueError("SHP crosswalk must have a declared plan")
    replicates = crosswalk.get("replicates")
    if type(replicates) is not int or replicates <= 0:
        raise ValueError("SHP crosswalk replicates must be a positive integer")
    shares: dict[str, list[tuple[float, float]]] = {
        scenario: [] for scenario in CROSSWALK_SCENARIOS.values()
    }
    for record in crosswalk["ranges"]:
        reference = record["reference"]
        if reference not in CROSSWALK_SCENARIOS:
            raise ValueError(f"Unknown SHP crosswalk reference: {reference}")
        if type(record.get("failures")) is not int or record["failures"] != 0:
            raise ValueError(f"SHP crosswalk failures must be zero: {reference}")
        if type(record.get("values")) is not int or record["values"] != replicates:
            raise ValueError(
                f"SHP crosswalk values must cover all replicates: {reference}"
            )
        scenario = CROSSWALK_SCENARIOS[reference]
        r = _finite_float(record["r"], "SHP crosswalk r")
        low = _finite_float(record["low"], "SHP crosswalk low")
        high = _finite_float(record["high"], "SHP crosswalk high")
        if not 0 <= low <= high <= 1:
            raise ValueError(f"Unavailable or invalid SHP crosswalk range: {reference}")
        shares[scenario].append((r, low))
        for end, value in (("low", low), ("high", high)):
            numbers.put(f"j.shp.crosswalk.{scenario}.{r_tag(r)}.{end}", f"{value:.3f}")
    for scenario, entries in shares.items():
        _nine_shares("SHP crosswalk " + scenario, entries)


def translate_all_units(source: bytes) -> bytes:
    """Translate released labels without changing CSV quoting or numeric strings."""
    rows = list(csv.reader(io.StringIO(source.decode("utf-8"), newline="")))
    if not rows or "status" not in rows[0]:
        raise ValueError("All-units CSV must include a status column")
    status_index = rows[0].index("status")
    expected = [rows[0]]
    for row in rows[1:]:
        if len(row) != len(rows[0]):
            raise ValueError("All-units CSV has an inconsistent column count")
        if row[status_index] not in CSV_STATUS:
            raise ValueError(f"Unknown all-units status: {row[status_index]}")
        translated = [CSV_STATUS.get(value, value) for value in row]
        if any(not value.isascii() for value in translated):
            raise ValueError("Untranslated all-units token")
        expected.append(translated)
    result = source
    for original, english in CSV_STATUS.items():
        result = result.replace(original.encode("utf-8"), english.encode("utf-8"))
    actual = list(csv.reader(io.StringIO(result.decode("utf-8"), newline="")))
    if actual != expected:
        raise ValueError("CSV translation changed a value outside the label mapping")
    return result


def build_journal(
    public: Mapping[str, Any],
    final: Mapping[str, str],
    catalog: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
    *,
    shp_aggregate: Mapping[str, Any] | None = None,
    x5_aggregate: Mapping[str, Any] | None = None,
) -> Journal:
    """Build bound values and table sources from already available quantities."""
    for key, final_value in final.items():
        if key in catalog.get("values", {}) and catalog["values"][key] != final_value:
            raise ValueError(f"Final value differs from catalog: {key}")
    curves = _curves(public)
    inventory = _inventory_rows(curves, rows)
    numbers = Numbers(final)
    for a in GRID:
        numbers.put("j.grid." + a_tag(a), strength(a))
    for target in (0.6, 0.7, 0.8):
        numbers.put("j.target." + r_tag(target), f"{target:.2f}")
        normal = NormalDist()
        delta = math.sqrt(2) * normal.inv_cdf(target)
        prefix = f"j.auc_translation.target{round(target * 100):03d}"
        numbers.put(prefix + ".delta", f"{delta:.2f}")
        numbers.put(prefix + ".power", f"{normal.cdf(delta - 1.6449):.2f}")
    numbers.put("j.chance", "0.5")
    main = [c for c in curves if c.tier == 1 and c.family == "B"]
    main_rows = []
    for curve in main:
        prefix = curve.prefix
        numbers.put(prefix + ".r", f"{curve.r:.2f}")
        numbers.put(prefix + ".status", STATUS[curve.status])
        numbers.put(prefix + ".region", inventory[_identity(curve)]["region"])
        numbers.put(prefix + ".critical", f"{float(curve.record['critical']):.3f}")
        for a in GRID:
            for kind in ("auc", "lower", "upper"):
                value = curve.estimate(a, kind)
                numbers.put(
                    prefix + "." + a_tag(a) + "." + kind,
                    f"{value:.3f}" if value is not None else "unavailable",
                )
        for name in ("first", "sustained"):
            _boundary_values(numbers, curve, name, prefix + "." + name)
        secondary: dict[str, float | None] = {}
        for target_code in ("060", "080"):
            key = f"v4.tab.T1sec.B.{r_tag(curve.r)}.a{target_code}.1"
            text = final.get(key, catalog.get("values", {}).get(key))
            if text is None:
                raise ValueError(f"Missing secondary-target key: {key}")
            secondary[target_code] = None if text == "unavailable" else float(text)
        if Counter(secondary.values()) != Counter(
            item["point"] for item in curve.record["secondary"]
        ):
            raise ValueError(
                f"Secondary boundaries disagree with released keys: {curve.key}"
            )
        for target_code, point in secondary.items():
            numbers.put(
                prefix + ".target" + target_code + ".point",
                strength(float(point)) if point is not None else "unavailable",
            )
        r = numbers.number(prefix + ".r", f"v4.tab.T1.B.{r_tag(curve.r)}.r")
        if curve.r == 0.7:
            r += r"\dag{}"
        main_rows.append(
            [
                r,
                _boundary_text(numbers, curve, "first", prefix + ".first"),
                _boundary_text(numbers, curve, "sustained", prefix + ".sustained"),
                *(
                    numbers.number(prefix + "." + a_tag(a) + ".auc")
                    for a in (0.03, 0.1, 0.3)
                ),
                *(
                    numbers.number(
                        prefix + ".target" + t + ".point",
                        f"v4.tab.T1sec.B.{r_tag(curve.r)}.a{t}.1",
                    )
                    for t in ("060", "080")
                ),
            ]
        )
    large_count = sum(inventory[_identity(c)]["region"] == "large" for c in main)
    numbers.put("j.b.first.large.n", str(large_count))
    table = _table(
        "tab:boundaries-B",
        "Boundaries against trait-plus-autoregressive persistence (B).",
        "lp{22mm}p{28mm}rrrrr",
        [
            "$r$",
            "$a^*$ [interval]",
            "$a_s^*$ [interval]",
            *(
                r"\shortstack{AUC at\\" + numbers.number("j.grid." + a_tag(a)) + "}"
                for a in (0.03, 0.1, 0.3)
            ),
            *(
                r"\shortstack{Target\\" + numbers.number("j.target.r" + t) + "}"
                for t in ("060", "080")
            ),
        ],
        main_rows,
        note=(
            "$r$ is signal share in the continuous response before discretization. "
            "$a^*$: first boundary [interval from the band]; $a_s^*$: sustained "
            "boundary; censored: not declared across fit gaps. "
            + ("All " if large_count == len(main) else "")
            + numbers.number("j.b.first.large.n")
            + " first-boundary intervals lie entirely above "
            + numbers.number("j.grid.a0300")
            + ". AUC columns give point estimates; target columns give first "
            r"boundaries at secondary targets. \dag{} Examined during calibration. "
            r"Definitions: \esmresource, Table~\ref{esm-tab:glossary-terms}."
        ),
        wide=True,
        colsep="5pt",
    )
    tables = {
        "journal-table-boundaries-B.tex": table,
        "journal-table-other-models.tex": _other_models(numbers, curves),
        "journal-esm-sensitivity-differences.tex": _sensitivity_table(
            numbers, curves, inventory
        ),
    }
    cell_table, notes = _cell_tables(numbers, main)
    tables["journal-esm-b-cells.tex"] = cell_table
    tables["journal-esm-controls.tex"] = _controls_table(numbers, curves, inventory)
    _summary_values(numbers, main, rows)
    _anchoring_gap_values(numbers, curves)
    _shp_values(numbers, public["objects"], catalog)
    if shp_aggregate is not None:
        _shp_aggregate_checks(public["objects"], shp_aggregate)
        _shp_aggregate_values(numbers, shp_aggregate)
        heise_table, heise_notes = _heise_windows_table(numbers, shp_aggregate, catalog)
        notes += heise_notes
        if heise_table is not None:
            tables["journal-esm-heise-windows.tex"] = heise_table
    notes += _sensitivity_values(numbers, curves)
    notes += _exploratory_values(numbers, catalog, main)
    x3_fit_table, x3_fit_notes = _x3_fit_table(numbers, catalog, main)
    notes += x3_fit_notes
    if x3_fit_table is not None:
        tables["journal-esm-x3-fit.tex"] = x3_fit_table
    x3_table, x3_notes = _x3_levels_table(numbers, catalog, main)
    notes += x3_notes
    if x3_table is not None:
        tables["journal-esm-x3-levels.tex"] = x3_table
    x3_lags_table, x3_lags_notes = _x3_lags_table(numbers, catalog, main)
    notes += x3_lags_notes
    if x3_lags_table is not None:
        tables["journal-esm-x3-lags.tex"] = x3_lags_table
    notes += _x3_grid_values(numbers, catalog)
    notes += _x3_plus_values(numbers, catalog, main)
    if x5_aggregate is not None:
        tables["journal-esm-x5-lags.tex"] = _x5_signature_values(
            numbers, x5_aggregate, catalog
        )
    else:
        notes.append("j.x5.signature: no sanitized aggregate supplied; omitted")
    notes += _round3_values(numbers, catalog, main)
    tables.update(_diagnostic_wrappers(numbers, public["objects"], curves))
    return Journal(numbers.values, tables, curves, tuple(notes))


def _figure_wrapper(
    file: str,
    label: str,
    caption: str,
    *,
    wide: bool = False,
    height_mm: int | None = None,
) -> str:
    environment = "figure*" if wide else "figure"
    size = r"width=\textwidth"
    if height_mm is not None:
        size += f",height={height_mm}mm,keepaspectratio"
    return "\n".join(
        [
            rf"\begin{{{environment}}}[tp]",
            r"\centering",
            rf"\includegraphics[{size}]{{generated/{file}}}",
            rf"\caption{{{caption}}}\label{{{label}}}",
            rf"\end{{{environment}}}",
            "",
        ]
    )


def _diagnostic_wrappers(
    numbers: Numbers,
    objects: Mapping[str, Any],
    curves: Sequence[JournalCurve],
) -> dict[str, str]:
    numbers.put("j.calibration.r", "0.70")
    counts = Counter(c.status for c in curves)
    entries = []
    for status, code, suffix in (
        (VALID, "V", "valid"),
        (INVALID, "I", "invalid"),
        ("parcial por encerramento operacional", "P", "partial"),
        ("não iniciado", "N", "not_started"),
    ):
        key = "v4.inv.n_" + suffix
        if key in numbers.final:
            value = numbers.final[key]
            if int(value.replace(",", "")) != counts[status]:
                raise ValueError("Inventory caption count differs from public statuses")
            bound = rf"\resultnum{{{key}}}{{{value}}}"
        else:
            key = numbers.put("j.inventory.figure.n_" + suffix, str(counts[status]))
            bound = numbers.number(key)
        entries.append(f"{STATUS[status].capitalize()} ({code}): {bound} units")
    wrappers = {
        "journal-esm-fig-inventory.tex": _figure_wrapper(
            "J5_inventory_status.pdf",
            "fig:inventory-status",
            "Status of every unit of the prespecified inventory at the operational "
            "close, by configuration (rows) and signal share $r$. "
            + "; ".join(entries)
            + ". The legend lists only states that occur. "
            r"$\dag$ $r="
            + numbers.number("j.calibration.r")
            + "$ was examined during calibration.",
            height_mm=160,
        )
    }
    if objects.get("gate") is not None:
        numbers.put("j.gate.solver_budget", str(SOLVER_BUDGET))
        numbers.put("j.gate.critical_floor", f"{CRITICAL_FLOOR:.4f}")
        wrappers["journal-esm-fig-gate.tex"] = _figure_wrapper(
            "J4_gate_diagnostics.pdf",
            "fig:gate-diagnostics",
            "Validation-gate diagnostics from the public aggregates: "
            "(a) final fit statuses and (b) solver evaluations per attempt in the "
            "zero-strength fitting check (budget "
            + numbers.number("j.gate.solver_budget")
            + "); (c) joint coverage per scenario and (d) critical values in the "
            "band calibration on synthetic scores, with the pass mark, nominal "
            "level and critical-value floor "
            + numbers.number("j.gate.critical_floor")
            + "; (e) dispersion ratios in the positive-strength dispersion check "
            "with bootstrap intervals and calibrated cell (shading) and pooled "
            "(green segment) thresholds; (f) local nuisance-variance estimates "
            "relative to full refits in the "
            "nuisance-variance check, with one-sided bounds; (g) completed tasks "
            "and verdict by stage. Family limits are gaps. The zero-strength "
            "band check uses its corrected aggregate record.",
            height_mm=150,
        )
    return wrappers


GATE_NAMES = {
    "G0": "Zero-strength fitting check",
    "G1b": "Band calibration on synthetic scores",
    "G1c": "Zero-strength band check",
    "G2": "Positive-strength dispersion check",
    "G2c": "Nuisance-variance check",
}
GATE_SCENARIOS = {
    "gaussian-icc0": "Gaussian, ICC = 0",
    "gaussian-icc05": "Gaussian, ICC = 0.5",
    "non-gaussian": "Non-Gaussian clusters",
    "ties": "Rounded ties",
    "dependent-slots": "Cross-slot dependence",
}


def _ratio_mark(ax: Axes, point: float, lower: float, upper: float, y: int) -> None:
    ax.plot(point, y, "o", color="black", markersize=3)
    ax.hlines(y, lower, upper, color="black")
    ax.plot([lower, upper], [y, y], "|", color="black", markersize=3)


def _gate_diagnostics(objects: Mapping[str, Any], render: Render) -> None:
    gate = objects["gate"]
    summaries = gate["summaries"]
    with style():
        fig = plt.figure(figsize=(DOUBLE, 185 * MM), layout="constrained")
        grid = fig.add_gridspec(4, 2, height_ratios=(1.4, 1.4, 1.3, 1.15))
        fits, evaluations = (fig.add_subplot(grid[0, i]) for i in range(2))
        coverage, critical = (fig.add_subplot(grid[1, i]) for i in range(2))
        dispersion, nuisance = (fig.add_subplot(grid[2, i]) for i in range(2))
        stages = fig.add_subplot(grid[3, :])
        for ax, tag in zip(
            (fits, evaluations, coverage, critical, dispersion, nuisance, stages),
            "abcdefg",
            strict=True,
        ):
            ax.set_title(f"({tag})", loc="left")

        fit_labels = {
            "anchor-exact": "exact identity fit",
            "interior": "interior fit",
            "boundary": "boundary fit",
            "family-limit-upper": "family limit, upper profile",
            "family-limit-lower": "family limit, lower profile",
            "no-L1-root": "no lag-one root",
            "ill-conditioned": "ill-conditioned fit",
            "non-monotone-profile": "non-monotone profile",
            "dependency-gap": "dependency gap",
        }
        outcomes = sorted(
            gate["g0_fits"],
            key=lambda row: (list(GAP_COLOR).index(row["gap"]), row["status"]),
        )
        fits.barh(
            range(len(outcomes)),
            [row["count"] for row in outcomes],
            color=[GAP_COLOR[row["gap"]] for row in outcomes],
        )
        fits.set_yticks(
            range(len(outcomes)),
            [fit_labels.get(row["status"], row["status"]) for row in outcomes],
            fontsize=7,
        )
        fits.invert_yaxis()
        fits.set_xscale("log")
        fits.set_xlim(left=0.5)
        fits.set_xlabel("Fits by final status")

        histogram = gate["g0_evaluations"]
        evaluations.hist(
            [row["value"] for row in histogram],
            weights=[row["count"] for row in histogram],
            bins=list(range(0, SOLVER_BUDGET + 2, 2)),
            color=OKABE_ITO["sky"],
        )
        evaluations.axvline(
            SOLVER_BUDGET,
            color=OKABE_ITO["vermillion"],
            linestyle="--",
            label=f"Budget {SOLVER_BUDGET}",
        )
        evaluations.legend(loc="upper right", fontsize=7)
        evaluations.set_xlabel("Evaluations per attempt")
        evaluations.set_ylabel("Attempts")

        counts = summaries["G1b"]["coverage_counts"]
        names = [name for name in SCENARIOS if name in counts]
        denominator = summaries["G1b"]["planned"] / len(names)
        coverage.plot(
            [counts[name] / denominator for name in names],
            range(len(names)),
            "o",
            color="black",
        )
        coverage.axvline(0.95, color="0.4", linestyle=":", label="Nominal 0.95")
        coverage.axvline(
            0.935, color=OKABE_ITO["vermillion"], linestyle="--", label="Pass ≥ 0.935"
        )
        coverage.set_yticks(
            range(len(names)),
            [GATE_SCENARIOS[name] for name in names],
            fontsize=7,
        )
        coverage.invert_yaxis()
        coverage.set_xlim(0.90, 1.0)
        coverage.set_xlabel("Joint coverage per scenario")
        coverage.legend(loc="lower right", bbox_to_anchor=(1, 1.08), fontsize=7)

        histogram = gate["g1b_critical"]
        critical.hist(
            [row["value"] for row in histogram],
            weights=[row["count"] for row in histogram],
            bins=40,
            color=OKABE_ITO["sky"],
        )
        critical.axvline(CRITICAL_FLOOR, color=OKABE_ITO["vermillion"], linestyle="--")
        total = sum(row["count"] for row in histogram)
        above = sum(row["count"] for row in histogram if row["value"] > CRITICAL_FLOOR)
        critical.text(
            0.97,
            0.9,
            f"Above floor: {above / total:.1%}",
            transform=critical.transAxes,
            ha="right",
            fontsize=7,
        )
        critical.set_xlabel("Critical value per repetition")
        critical.set_ylabel("Repetitions")

        summary = summaries["G2"]
        ratios = [*summary["cell_ratios"], summary["pooled_ratio"]]
        lower = [*summary["cell_lower"], summary["pooled_lower"]]
        upper = [*summary["cell_upper"], summary["pooled_upper"]]
        for i, (point, lo, hi) in enumerate(zip(ratios, lower, upper, strict=True)):
            _ratio_mark(dispersion, point, lo, hi, i)
        dispersion.axvline(1.0, color="0.4", linestyle=":")
        thresholds = objects.get("thresholds")
        if thresholds is not None:
            dispersion.axvspan(
                thresholds["cell_lower"],
                thresholds["cell_upper"],
                color=OKABE_ITO["green"],
                alpha=0.12,
                linewidth=0,
            )
            dispersion.plot(
                [thresholds["pooled_lower"], thresholds["pooled_upper"]],
                [len(ratios) - 0.55] * 2,
                color=OKABE_ITO["green"],
                linewidth=2,
            )
        dispersion.set_yticks(
            range(len(ratios)),
            [f"a={strength(a)}, r={r:.2f}" for a, r in gate["g2_cells"]] + ["pooled"],
            fontsize=7,
        )
        dispersion.invert_yaxis()
        dispersion.set_xlabel("Dispersion ratio")

        comparisons = summaries["G2c"]["comparisons"]
        for i, row in enumerate(comparisons):
            _ratio_mark(nuisance, row["ratio"], row["lower"], row["upper"], i)
        for threshold in (0.8, 2.0):
            nuisance.axvline(
                threshold,
                color=OKABE_ITO["vermillion"],
                linestyle="--",
                label="Pass limits 0.8, 2.0" if threshold == 0.8 else None,
            )
        nuisance.axvline(1.0, color="0.4", linestyle=":")
        nuisance.set_xscale("log")
        nuisance.set_xticks([0.25, 0.5, 1, 2, 4], ["0.25", "0.5", "1", "2", "4"])
        nuisance.legend(loc="lower right", bbox_to_anchor=(1, 1.08), fontsize=7)
        nuisance.minorticks_off()
        nuisance.set_yticks(
            range(len(comparisons)),
            [
                f"a={strength(a)} ({row['denominator']})"
                for a, row in zip((0.1, 0.03), comparisons, strict=True)
            ],
            fontsize=7,
        )
        nuisance.set_ylim(-0.5, len(comparisons) - 0.5)
        nuisance.invert_yaxis()
        nuisance.set_xlabel(r"$V_{\mathrm{nuis}} / \mathrm{Var}_{\mathrm{refit}}$")

        for i, stage in enumerate(GATE_STAGES):
            row = summaries[stage]
            completed, planned = row["completed"], row["planned"]
            verdict = "pass" if row["pass"] else "fail"
            stages.barh(i, 1, color="none", edgecolor="0.6", linewidth=0.5, height=0.6)
            stages.barh(
                i,
                completed / planned,
                height=0.6,
                color=OKABE_ITO["green" if row["pass"] else "vermillion"],
            )
            stages.text(
                1.05,
                i,
                f"{completed:,}/{planned:,} tasks · {verdict}",
                va="center",
                fontsize=7,
            )
        stages.set_xlim(0, 2.5)
        stages.set_xticks([0, 0.5, 1], ["0%", "50%", "100%"])
        stages.set_yticks(
            range(len(GATE_STAGES)),
            [GATE_NAMES[stage] for stage in GATE_STAGES],
            fontsize=7,
        )
        stages.invert_yaxis()
        for side in ("top", "right"):
            stages.spines[side].set_visible(False)
        stages.spines["bottom"].set_bounds(0, 1)
        save(fig, render, "J4_gate_diagnostics")


def _inventory_label(config: tuple[int, str, str, str]) -> str:
    group, family, channel, scenario = config
    channels = {
        "observed": "observed",
        "latent": "error-free",
        "ordinal_one": "ordinal r=1",
        "latent_rank": "latent ranks",
    }
    if group == 1:
        return "B · main curve"
    if group == 2:
        return family + " · secondary persistence model"
    if group == 3:
        suffix = " · mobility" if scenario == "mobility" else ""
        return f"{family} · {channels[channel]}{suffix}"
    scenarios = {
        "c025": "response style c=0.25",
        "c050": "response style c=0.50",
        "d010": "conditioning δ=0.10",
        "d020": "conditioning δ=0.20",
        "c050-d020-exploratory": "style c=0.50 + conditioning δ=0.20",
        "b000": "attraction only b=0",
        "omega025": "anchoring ω=0.25",
        "omega050": "anchoring ω=0.50",
        "omega075": "anchoring ω=0.75",
        "omega100": "complete anchoring ω=1",
        "steps24": "24 updates per wave",
    }
    return family + " · " + scenarios[scenario]


def _inventory(curves: Sequence[JournalCurve], render: Render) -> None:
    configs = list(
        dict.fromkeys((c.tier, c.family, c.channel, c.scenario) for c in curves)
    )
    statuses = list(STATUS)
    matrix = np.full((len(configs), len(RELIABILITIES)), -1, dtype=int)
    for curve in curves:
        config = (curve.tier, curve.family, curve.channel, curve.scenario)
        position = (configs.index(config), RELIABILITIES.index(curve.r))
        if matrix[position] != -1:
            raise ValueError("Duplicate inventory configuration and signal share")
        matrix[position] = statuses.index(curve.status)
    with style():
        fig, ax = plt.subplots(
            figsize=(DOUBLE, (len(configs) * 3.1 + 28) * MM), layout="constrained"
        )
        ax.pcolormesh(
            np.arange(len(RELIABILITIES) + 1) - 0.5,
            np.arange(len(configs) + 1) - 0.5,
            np.ma.masked_less(matrix, 0),
            cmap=ListedColormap([STATUS_COLOR[s] for s in statuses]),
            norm=BoundaryNorm(np.arange(len(statuses) + 1) - 0.5, len(statuses)),
            edgecolors="white",
            linewidth=0.4,
            rasterized=False,
        )
        codes = ("V", "I", "P", "N")
        for row, col in np.ndindex(matrix.shape):
            if matrix[row, col] >= 0:
                ax.text(
                    col,
                    row,
                    codes[matrix[row, col]],
                    ha="center",
                    va="center",
                    fontsize=7,
                )
        ax.set_xticks(
            range(len(RELIABILITIES)),
            [f"{r:.2f}" + ("†" if r == 0.7 else "") for r in RELIABILITIES],
            rotation=90,
        )
        ax.set_yticks(
            range(len(configs)), [_inventory_label(c) for c in configs], fontsize=7
        )
        ax.invert_yaxis()
        ax.set_xlabel("signal share r")
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.legend(
            handles=[
                Patch(
                    facecolor=STATUS_COLOR[s],
                    edgecolor="0.6",
                    linewidth=0.4,
                    label=f"{codes[i]}: {STATUS[s]} ({int((matrix == i).sum())})",
                )
                for i, s in enumerate(statuses)
                if np.any(matrix == i)
            ],
            loc="outside lower center",
            ncol=1,
            fontsize=7,
        )
        save(fig, render, "J5_inventory_status")


def _profiles(curves: Sequence[JournalCurve], render: Render, family: str) -> None:
    selected = sorted(
        (c for c in curves if c.family == family and c.tier in (1, 2)),
        key=lambda c: c.r,
    )
    columns = min(3, len(selected))
    with style():
        fig, axes = plt.subplots(
            math.ceil(len(selected) / columns),
            columns,
            figsize=(DOUBLE, 150 * MM),
            sharex=True,
            sharey=True,
            squeeze=False,
            layout="constrained",
        )
        color = FAMILY_COLOR[family]
        has_gap = has_boundary = False
        for ax, curve in zip(axes.flat, selected, strict=False):
            ax.axhline(0.7, color="0.3", linestyle="--", linewidth=0.7)
            ax.axhline(0.5, color="0.6", linestyle=":", linewidth=0.7)
            point, lower, upper = (
                np.array(curve.record[kind]) for kind in ("auc", "lower", "upper")
            )
            indices = [GRID.index(a) for a in curve.record["available"]]
            ax.errorbar(
                indices,
                (lower + upper) / 2,
                yerr=(upper - lower) / 2,
                fmt="none",
                color=color,
                elinewidth=0.9,
                capsize=1.5,
            )
            ax.plot(indices, point, "o", color=color, markersize=3)
            for a, _ in curve.gaps:
                ax.plot(
                    GRID.index(a),
                    0.46,
                    marker="x",
                    color=OKABE_ITO["vermillion"],
                    markersize=4,
                )
                has_gap = True
            note = f"r = {curve.r:.2f}" + ("†" if curve.r == 0.7 else "")
            if curve.status != VALID:
                note += "\ncomplete but invalid\nzero-strength check failed"
            else:
                boundary = curve.record["first"]
                if boundary["point"] is not None:
                    ax.axvline(
                        GRID.index(boundary["point"]),
                        color=OKABE_ITO["blue"],
                        linewidth=0.8,
                    )
                    lo, hi = boundary["interval"] or [None, None]
                    if lo is not None and hi is not None:
                        ax.axvspan(
                            GRID.index(lo) - 0.15,
                            GRID.index(hi) + 0.15,
                            color=OKABE_ITO["sky"],
                            alpha=0.22,
                            linewidth=0,
                        )
                    has_boundary = True
                elif boundary["censoring"] and curve.gaps:
                    note += "\nfirst boundary\ncensored at fit gap\n" + strength(
                        float(boundary["censoring"].removeprefix("gap at a="))
                    )
                else:
                    note += "\nfirst boundary not reached"
            ax.set_title(note, loc="left")
            ax.set_xlim(-0.5, len(GRID) - 0.5)
            ax.set_ylim(0.44, 1.04)
            ax.set_xticks(range(len(GRID)), [strength(a) for a in GRID], rotation=90)
            ax.set_yticks([0.5, 0.7, 0.9, 1.0])
        for ax in list(axes.flat)[len(selected) :]:
            ax.set_visible(False)
        fig.supxlabel("influence strength a (grid positions)")
        fig.supylabel("AUC")
        handles: list[Line2D | Patch] = [
            Line2D([], [], color="0.3", linestyle="--", label="target 0.70"),
            Line2D(
                [],
                [],
                color=color,
                marker="o",
                linestyle="none",
                label="AUC and per-share band",
            ),
        ]
        if has_boundary:
            handles += [
                Line2D([], [], color=OKABE_ITO["blue"], label="first boundary"),
                Patch(color=OKABE_ITO["sky"], alpha=0.22, label="boundary interval"),
            ]
        if has_gap:
            handles.append(
                Line2D(
                    [],
                    [],
                    color=OKABE_ITO["vermillion"],
                    marker="x",
                    linestyle="none",
                    label="fit gap",
                )
            )
        fig.legend(handles=handles, loc="outside upper center", ncol=3)
        save(fig, render, "J2_auc_profiles_" + family)


def _boundaries(curves: Sequence[JournalCurve], render: Render) -> None:
    families = [
        f
        for f in ("B", "A", "C", "D", "E")
        if any(c.family == f and c.tier in (1, 2) for c in curves)
    ]
    with style():
        fig, axes = plt.subplots(
            2, 3, figsize=(DOUBLE, 150 * MM), sharey=True, layout="constrained"
        )
        ticks = [-2, -1, *range(len(GRID))]
        labels = ["invalid", "censored", *(strength(a) for a in GRID)]
        if any(
            c.status == VALID
            and c.record[name]["point"] is None
            and not c.record[name]["censoring"]
            for c in curves
            if c.tier in (1, 2)
            for name in ("first", "sustained")
        ):
            ticks.append(len(GRID))
            labels.append("not reached")
        states = set()
        for ax, family in zip(axes.flat, families, strict=False):
            selected = sorted(
                (c for c in curves if c.family == family and c.tier in (1, 2)),
                key=lambda c: c.r,
            )
            color = FAMILY_COLOR[family]
            panel_states = set()
            for curve in selected:
                if curve.status != VALID:
                    ax.plot(curve.r, -2, marker="x", color=color, markersize=4)
                    panel_states.add("invalid")
                    continue
                for name, offset, filled in (
                    ("first", -0.008, True),
                    ("sustained", 0.008, False),
                ):
                    boundary = curve.record[name]
                    x = curve.r + offset
                    face = color if filled else "white"
                    if boundary["point"] is not None:
                        y = GRID.index(boundary["point"])
                        ax.plot(
                            x,
                            y,
                            marker="o",
                            markerfacecolor=face,
                            markeredgecolor=color,
                            linestyle="none",
                            markersize=3,
                        )
                        lo, hi = boundary["interval"] or [None, None]
                        if lo is not None and hi is not None:
                            ax.vlines(
                                x,
                                GRID.index(lo),
                                GRID.index(hi),
                                color=color,
                                linewidth=0.7,
                            )
                        panel_states.add(name)
                    elif boundary["censoring"]:
                        ax.plot(
                            x,
                            -1,
                            marker="s",
                            markerfacecolor=face,
                            markeredgecolor=color,
                            markersize=3,
                        )
                        panel_states.add("censored")
                    else:
                        ax.plot(
                            x,
                            len(GRID),
                            marker="^",
                            markerfacecolor=face,
                            markeredgecolor=color,
                            markersize=3,
                        )
                        panel_states.add("not reached")
            states |= panel_states
            ax.set_yticks(ticks, labels)
            ax.set_ylim(min(ticks) - 0.6, max(ticks) + 0.6)
            ax.set_xlim(0.47, 0.93)
            ax.set_xticks(
                [c.r for c in selected], [f"{c.r:.2f}" for c in selected], rotation=90
            )
            label = family + ": " + MODEL_NAMES[family].replace("--", "\u2013")
            if family == "B":
                label = label.replace("trait-plus-", "trait-plus-\n")
            elif family == "C":
                label = label.replace(
                    " with an altered response channel",
                    "\nwith an altered\nresponse channel",
                )
            ax.set_title(label, loc="left")
        for ax in list(axes.flat)[len(families) :]:
            ax.set_visible(False)
        handles = []
        for name, marker, face in (
            ("first", "o", "black"),
            ("sustained", "o", "white"),
            ("censored", "s", "white"),
            ("invalid", "x", "black"),
            ("not reached", "^", "white"),
        ):
            if name in states:
                handles.append(
                    Line2D(
                        [],
                        [],
                        marker=marker,
                        markerfacecolor=face,
                        color="black",
                        linestyle="none",
                        label=name
                        + (" boundary" if name in ("first", "sustained") else ""),
                    )
                )
        legend_ax = list(axes.flat)[-1]
        legend_ax.set_visible(True)
        legend_ax.set_axis_off()
        legend_ax.legend(handles=handles, loc="center", ncol=1)
        fig.supxlabel("signal share r")
        fig.supylabel("influence strength a (grid positions)")
        save(fig, render, "J1_boundaries_by_model")


def _anchor(shp: Mapping[str, Any], render: Render) -> None:
    with style():
        fig, ax = plt.subplots(figsize=(DOUBLE, 55 * MM), layout="constrained")
        color = OKABE_ITO["blue"]
        lo, hi = shp["sensitivity_envelope"]
        ax.plot(
            [lo, hi],
            [-0.22, -0.22],
            color=color,
            linewidth=5,
            alpha=0.25,
            solid_capstyle="butt",
            label="specification range (not a confidence interval)",
        )
        lo, hi = shp["wald_95_interval"]
        estimate = shp["estimate"]
        ax.errorbar(
            estimate,
            0,
            xerr=[[estimate - lo], [hi - estimate]],
            fmt="o",
            color=color,
            capsize=3,
            label="quasi-simplex anchor and Wald 95% interval",
        )
        starts = shp.get("starts")
        if (
            starts
            and starts["estimate"] is not None
            and starts["wald_95_interval"] is not None
        ):
            lo, hi = starts["wald_95_interval"]
            estimate = starts["estimate"]
            ax.errorbar(
                estimate,
                1,
                xerr=[[estimate - lo], [hi - estimate]],
                fmt="D",
                color=OKABE_ITO["vermillion"],
                capsize=3,
                label="STARTS sensitivity and Wald 95% interval",
            )
        ax.set_ylim(-0.5, 1.5)
        ax.set_xlim(0.47, 0.93)
        ax.set_xticks(
            np.arange(0.5, 0.91, 0.05), [f"{r:.2f}" for r in np.arange(0.5, 0.91, 0.05)]
        )
        ax.set_yticks([])
        ax.set_xlabel(
            "signal share r (design scale; empirical summaries are uncalibrated)"
        )
        fig.legend(loc="outside lower center", ncol=1)
        save(fig, render, "J6_shp_anchor")


def _publish_outputs(outputs: Mapping[Path, bytes]) -> None:
    for destination in outputs:
        if (
            destination.exists() or destination.is_symlink()
        ) and not destination.is_file():
            raise OSError(f"Output target is not a regular file: {destination}")
    with ExitStack() as stack:
        staging = {}
        for parent in {destination.parent for destination in outputs}:
            parent.mkdir(parents=True, exist_ok=True)
            staging[parent] = Path(
                stack.enter_context(
                    TemporaryDirectory(prefix=".ic-journal-export-", dir=parent)
                )
            )
        prepared = {}
        for index, (destination, data) in enumerate(outputs.items()):
            path = staging[destination.parent] / f"new-{index}"
            path.write_bytes(data)
            prepared[destination] = path
        backups: dict[Path, Path] = {}
        published = []
        try:
            for index, (destination, path) in enumerate(prepared.items()):
                if destination.exists() or destination.is_symlink():
                    backup = staging[destination.parent] / f"old-{index}"
                    destination.replace(backup)
                    backups[destination] = backup
                path.replace(destination)
                published.append(destination)
        except OSError:
            for destination in reversed(published):
                destination.unlink()
            for destination, backup in reversed(backups.items()):
                backup.replace(destination)
            raise


EXPLORATORY_FILES = {
    "x1a.json": "Mean-field twin versus the influence arm (paired AUCs).",
    "x1b.json": "Mean-field twin versus matched persistence (AUCs and boundaries).",
    "x2.json": "Variance explained by influence and its spline-adjusted contrast.",
    "x5.json": "Response-channel misspecification with influence switched off.",
}
PRIVATE_FIELDS = {
    "host",
    "hosts",
    "hostname",
    "hostnames",
    "kernel",
    "cpu",
    "cpus",
    "user",
    "users",
    "username",
    "usernames",
}
PRIVATE_STRINGS = re.compile(
    r"/Users/|/home/|/var/home/|/root(?:/|\b)|~/",
    re.IGNORECASE,
)
ABSOLUTE_PATH = re.compile(r"^(?:/|[A-Za-z]:[\\/]|\\\\|file:///)")


def _private_field(key: str) -> bool:
    words = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key)
    words = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", words).lower()
    tokens = set(re.split(r"[^a-z0-9]+", words))
    return bool(
        PRIVATE_FIELDS.intersection(tokens)
        or {"absolute", "path"} <= tokens
        or {"absolute", "paths"} <= tokens
        or "absolutepath" in tokens
    )


def _private_string(value: str, private_patterns: Sequence[re.Pattern[str]]) -> bool:
    return bool(
        PRIVATE_STRINGS.search(value)
        or ABSOLUTE_PATH.match(value)
        or any(pattern.search(value) for pattern in private_patterns)
    )


def sanitize_exploratory_value(
    value: Any, *, private_patterns: Sequence[str] = ()
) -> tuple[Any, tuple[str, ...]]:
    """Remove private fields/string values; preserve every retained JSON value.

    Removed paths are RFC 6901 JSON pointers into the source, including original
    array indices. A removed object field covers its entire subtree. Private list
    items are deleted, not replaced; retained items keep their relative order.
    CPU timing fields are removed as CPU fields, alongside hardware metadata.
    Optional site patterns match keys and string values case-insensitively.
    """
    try:
        patterns = tuple(
            re.compile(pattern, re.IGNORECASE) for pattern in private_patterns
        )
    except re.error:
        raise ValueError("Invalid private pattern") from None
    removed = []

    def clean(item: Any, path: str) -> Any:
        if isinstance(item, dict):
            kept = {}
            for key, child in item.items():
                pointer = path + "/" + key.replace("~", "~0").replace("/", "~1")
                if (
                    _private_field(key)
                    or _private_string(key, patterns)
                    or (isinstance(child, str) and _private_string(child, patterns))
                ):
                    removed.append(pointer)
                else:
                    kept[key] = clean(child, pointer)
            return kept
        if isinstance(item, list):
            kept_items = []
            for index, child in enumerate(item):
                pointer = path + f"/{index}"
                if isinstance(child, str) and _private_string(child, patterns):
                    removed.append(pointer)
                else:
                    kept_items.append(clean(child, pointer))
            return kept_items
        return item

    if isinstance(value, str) and _private_string(value, patterns):
        raise ValueError("Cannot sanitize a private root string without replacing it")
    return clean(value, ""), tuple(removed)


def sanitize_exploratory(
    src_dir: Path, out_dir: Path, *, private_patterns: Sequence[str] = ()
) -> dict[str, tuple[str, ...]]:
    """Archive the four approved aggregates with source/output hashes and paths."""
    inputs = [src_dir / name for name in EXPLORATORY_FILES]
    destinations = [out_dir / name for name in (*EXPLORATORY_FILES, "README.md")]
    for path in (*inputs, *destinations):
        parts = path.resolve().parts
        if (
            "restricted" in parts
            or "v4-tier-logs" in parts
            or any(part.startswith("sealed-v4-") for part in parts)
        ):
            raise ValueError("Forbidden source or output path")
    if {p.resolve() for p in inputs} & {p.resolve() for p in destinations}:
        raise ValueError("Sanitized outputs must not overwrite a source")
    outputs = {}
    ledger = {}
    readme = [
        "# Sanitized exploratory aggregates",
        "",
        "These copies preserve the tracked exploratory results except for the fields",
        "listed below. Sources are the identically named files in",
        "`studies/ic-2026-2027/experiments/exploratory/"
        "detection-boundary-v4-exploratory/results/`.",
        "",
        "Host, hostname, kernel, CPU (including timing), user and absolute-path",
        "fields are removed, as are absolute paths and strings containing home",
        "directories. Site-specific keys and strings are removed when they match",
        "a supplied private pattern. Every retained JSON value and its type are",
        "unchanged; object order and retained array order are preserved.",
        "Whitespace is serialized anew.",
        "",
        "Removed paths use RFC 6901 JSON pointers into each original source, with",
        "zero-based array indices. A removed parent path includes its whole subtree.",
        "",
        "Every reported table and figure regenerates from the archived aggregates",
        "with the archived scripts, except the X1a and X2 tables of Online Resource 1",
        "(Tables S20/S21), whose values are transcribed from the sanitized records",
        "in this folder.",
        "",
        "Random seeds derive from text labels and do not depend on the platform.",
        "The `seed_material_sha256` field is a cache key that hashes numeric",
        "parameters; it can differ across platforms without changing the seeds.",
        "In the recorded cross-host replay of three zero-strength fitting-check",
        "tasks on Linux x86-64, states, decisions and counts were identical, and",
        "1,331,544 continuous values agreed within 7.9e-12 in absolute terms.",
        "The pre-declared equivalence criterion nevertheless failed on the",
        "`seed_material_sha256` field (4,448 divergences); platform, interpreter",
        "and host fields also differed as expected. This component replay was",
        "for equivalence only, not gate evidence; full-release bitwise replay",
        "has not been independently demonstrated. The frozen runners refuse",
        "to start outside the recorded bound environment.",
        "",
        "Regenerate these sanitized files with the study environment:",
        "",
        "```sh",
        "python -m ic_study.analysis.v4_journal_export "
        "--sanitize-exploratory SRC_DIR OUT_DIR --private-pattern 'SITE_REGEX'",
        "```",
        "",
        "Replace SITE_REGEX privately with a site-specific regular expression.",
        "The optional --private-pattern REGEX argument is repeatable and matches",
        "case-insensitively; omit it to use only the generic field/path rules.",
        "Patterns are supplied only at runtime and are not recorded in the archive.",
        "",
    ]
    for name, description in EXPLORATORY_FILES.items():
        source = (src_dir / name).read_bytes()
        sanitized, paths = sanitize_exploratory_value(
            json.loads(source), private_patterns=private_patterns
        )
        data = (
            json.dumps(sanitized, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        ).encode("utf-8")
        outputs[out_dir / name] = data
        ledger[name] = paths
        readme += [
            "## " + name,
            "",
            description,
            "",
            "- Source SHA-256: `" + hashlib.sha256(source).hexdigest() + "`",
            "- Sanitized SHA-256: `" + hashlib.sha256(data).hexdigest() + "`",
            "",
            "Removed JSON paths:",
            "",
        ]
        readme += ["- `" + path + "`" for path in paths] or ["None."]
        readme.append("")
    outputs[out_dir / "README.md"] = "\n".join(readme).encode("utf-8")
    _publish_outputs(outputs)
    return ledger


def export(
    public_path: Path,
    values_path: Path,
    catalog_path: Path,
    csv_path: Path,
    generated: Path,
    journal_values: Path,
    shp_aggregate_path: Path | None = None,
    x5_aggregate_path: Path | None = None,
) -> Journal:
    """Write the journal projection; reject input aliases and key collisions first."""
    inputs = {
        "public_aggregates": public_path,
        "values": values_path,
        "catalog": catalog_path,
        "all_units": csv_path,
    }
    if shp_aggregate_path is not None:
        inputs["shp_aggregate"] = shp_aggregate_path
    if x5_aggregate_path is not None:
        inputs["x5_aggregate"] = x5_aggregate_path
    for path in (*inputs.values(), generated, journal_values):
        parts = path.resolve().parts
        if (
            "restricted" in parts
            or "v4-tier-logs" in parts
            or any(part.startswith("sealed-v4-") for part in parts)
        ):
            raise ValueError("Forbidden source or output path")
    if journal_values.resolve() in {p.resolve() for p in inputs.values()}:
        raise ValueError("Journal values must not overwrite an input")
    public = json.loads(public_path.read_bytes())
    final = json.loads(values_path.read_bytes())["values"]
    catalog = json.loads(catalog_path.read_bytes())
    csv_bytes = csv_path.read_bytes()
    english_csv = translate_all_units(csv_bytes)
    rows = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8"), newline="")))
    shp_aggregate = (
        None
        if shp_aggregate_path is None
        else json.loads(shp_aggregate_path.read_bytes())
    )
    x5_aggregate = (
        None
        if x5_aggregate_path is None
        else json.loads(x5_aggregate_path.read_bytes())
    )
    journal = build_journal(
        public,
        final,
        catalog,
        rows,
        shp_aggregate=shp_aggregate,
        x5_aggregate=x5_aggregate,
    )
    tables = dict(journal.tables)
    families = [
        f
        for f in ("B", "A", "C", "D", "E")
        if any(c.family == f and c.tier in (1, 2) for c in journal.curves)
    ]
    for family in families:
        name = (
            "journal-fig-auc-B.tex"
            if family == "B"
            else "journal-esm-fig-auc-others.tex"
        )
        wrapper = _figure_wrapper(
            "J2_auc_profiles_" + family + ".pdf",
            "fig:auc-" + family,
            "AUC profiles against "
            + (
                "autoregressive persistence with an altered response channel"
                if family == "C"
                else MODEL_NAMES[family] + " persistence"
            )
            + " ("
            + family
            + (
                "), one panel per signal share $r$. Points are point AUCs; "
                "vertical bars show that share's band, simultaneous over strengths; "
                "the vertical line marks the first boundary and the shading its "
                "interval; crosses mark fit gaps. Dashed line: target "
                if family == "B"
                else "). Vertical bars show per-share bands and crosses mark fit gaps. "
                "The target is "
            )
            + r"\resultnum{j.target.r070}{0.70}"
            + (
                r". Dotted line: chance (\resultnum{j.chance}{0.5})"
                if family == "B"
                else ""
            )
            + r". $\dag$ Examined during calibration.",
            wide=family == "B",
        )
        tables[name] = tables.get(name, "") + wrapper
    tables["journal-esm-fig-boundaries.tex"] = _figure_wrapper(
        "J1_boundaries_by_model.pdf",
        "fig:boundaries-by-model",
        "First and sustained boundaries by persistence model and signal share. "
        "Censored boundaries and invalid units occupy separate rows. "
        "Filled and open markers distinguish first and sustained boundaries.",
    )
    shp = public["objects"].get("shp")
    if shp is not None:
        year_key = "v4.protocol.shp.anchor_year"
        if str(shp["year"]) != final[year_key]:
            raise ValueError("SHP anchor year differs from final values")
        envelope = []
        for suffix in ("env_lo", "env_hi"):
            key = "j.shp." + suffix
            if key not in journal.values:
                key = "v4.shp." + suffix
            value = journal.values[key] if key in journal.values else final[key]
            envelope.append(rf"\resultnum{{{key}}}{{{value}}}")
        tables["journal-esm-fig-shp.tex"] = _figure_wrapper(
            "J6_shp_anchor.pdf",
            "fig:shp-anchor",
            "Reliability summaries for the Swiss Household Panel trust item. "
            "The quasi-simplex anchor and the STARTS point estimate refer to the "
            + rf"\resultnum{{{year_key}}}{{{final[year_key]}}}"
            + " wave and have Wald 95\\% intervals. "
            "The shaded specification range spans the nine Heise triplet estimates "
            "over 1999--2009, from "
            + envelope[0]
            + " (2003--2005) to "
            + envelope[1]
            + " (2007--2009); it is not a confidence interval. "
            "The anchor is placed on the signal-share axis without calibrating "
            "it to the design.",
        )
    module = Path(__file__)
    payload = {
        "schema": SCHEMA,
        "sources": {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in inputs.items()
        },
        "code": {
            "module": "ic_study.analysis.v4_journal_export",
            "sha256": hashlib.sha256(module.read_bytes()).hexdigest(),
        },
        "values": journal.values,
    }
    values_text = (
        json.dumps(
            payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
        )
        + "\n"
    )
    with TemporaryDirectory(prefix="ic-journal-export-") as temporary:
        staging = Path(temporary)
        render = Render(staging, formats=("pdf",))
        try:
            for family in families:
                _profiles(journal.curves, render, family)
            _boundaries(journal.curves, render)
            _inventory(journal.curves, render)
            if public["objects"].get("gate") is not None:
                _gate_diagnostics(public["objects"], render)
            if shp is not None:
                _anchor(shp, render)
        finally:
            plt.close("all")
        figures = {path.name: path.read_bytes() for path in staging.iterdir()}
    outputs = {generated / name: data for name, data in figures.items()}
    outputs.update(
        {generated / name: source.encode("utf-8") for name, source in tables.items()}
    )
    outputs[journal_values] = values_text.encode("utf-8")
    outputs[generated / "online-resource-2-units.csv"] = english_csv
    outputs[generated / "online-resource-2-README.txt"] = UNITS_README.encode("utf-8")
    if {p.resolve() for p in outputs} & {p.resolve() for p in inputs.values()}:
        raise ValueError("Journal outputs must not overwrite an input")
    _publish_outputs(outputs)
    return Journal(journal.values, tables, journal.curves, journal.notes)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sanitize-exploratory", nargs=2, type=Path, metavar=("SRC_DIR", "OUT_DIR")
    )
    parser.add_argument(
        "--private-pattern",
        dest="private_patterns",
        action="append",
        default=[],
        metavar="REGEX",
        help="case-insensitive sanitizer site pattern; repeatable, never recorded",
    )
    for name in (
        "public-aggregates",
        "values",
        "catalog",
        "all-units",
        "generated",
        "journal-values",
    ):
        parser.add_argument("--" + name, type=Path)
    parser.add_argument("--shp-aggregate", type=Path)
    parser.add_argument("--x5-aggregate", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.sanitize_exploratory is not None:
            if any(
                value is not None
                for name, value in vars(args).items()
                if name not in {"sanitize_exploratory", "private_patterns"}
            ):
                raise ValueError("Sanitizer and journal export options are separate")
            ledger = sanitize_exploratory(
                *args.sanitize_exploratory, private_patterns=args.private_patterns
            )
            for name, paths in ledger.items():
                print(f"sanitized {name}: {len(paths)} removed JSON paths")
            return 0
        if args.private_patterns:
            raise ValueError("--private-pattern requires --sanitize-exploratory")
        missing = [
            name
            for name in (
                "public_aggregates",
                "values",
                "catalog",
                "all_units",
                "generated",
                "journal_values",
            )
            if getattr(args, name) is None
        ]
        if missing:
            raise ValueError(
                "Missing export options: "
                + ", ".join("--" + name.replace("_", "-") for name in missing)
            )
        journal = export(
            args.public_aggregates,
            args.values,
            args.catalog,
            args.all_units,
            args.generated,
            args.journal_values,
            args.shp_aggregate,
            args.x5_aggregate,
        )
    except (ValueError, KeyError, OSError) as error:
        parser.error(str(error))
    print(
        f"journal export: {len(journal.values)} values; "
        f"{len(journal.tables)} LaTeX files"
    )
    for note in journal.notes:
        print("NOTE: " + note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
