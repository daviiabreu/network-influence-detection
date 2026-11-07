"""Export the rendered v4 report into the JCSS manuscript sources.

Usage::

    python -m ic_study.analysis.v4_report_export --report DIR \\
        [--curves RELEASE.json] --gate-root GATE_DIR [--shp SHP.json] \\
        [--crosswalk CROSSWALK.json] [--criteria criteria-v43.json] \\
        [--allocation v4-allocation.json] [--stage-successor SUCCESSOR.json]... \\
        --manuscript MANUSCRIPT_DIR --values VALUES.json \\
        [--catalog CATALOG.json] [--fill]

``DIR`` is the output of ``detection_v4_report`` for the same inputs; the export
refuses inputs, tables or figures whose SHA-256 differs from its manifest, and
tables that the reporting code no longer reproduces byte for byte. It writes the
manuscript's ``generated/*.tex`` floats and copies the figure PDFs beside them.
Every numeral in a generated table is ``\\resultnum{id}{value}``, and captions
carry no braces, so ``pipeline/paper_check.py`` skips their protocol constants.
Table cells are bound under ``v4.tab.*`` and the counts the Results text cites
(notes to the results shells, section 4) under the other ``v4.*`` IDs, formatted
as the report tables print them. ``VALUES.json`` holds ``{"values": ...}`` for
exactly the IDs that the manuscript's ``\\input`` tree uses, as the checker
requires; ``--catalog`` writes every ID and ``--fill`` replaces the
``\\resultnum{id}{[..]}`` placeholders of the manuscript sources. Without a
release only the gate outputs and optional SHP anchor values are exported.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, TypeGuard, cast
from zoneinfo import ZoneInfo

from ic_study.analysis.detection_v4_report import (
    MANIFEST_SCHEMA,
    Inputs,
    Loaded,
    add_input_arguments,
    code_commit,
    input_record,
    load_inputs,
    parse_inputs,
    report_tables,
    sha256,
)
from ic_study.analysis.v4_report_protocol import (
    CLOSE_ZONE,
    places,
    protocol,
    protocol_values,
    tag,
)
from ic_study.analysis.v4_report_schema import (
    FAIL,
    FAMILIES,
    GATE_STAGES,
    INVALID,
    NOT_STARTED,
    PARTIAL,
    PASS,
    SECONDARY_TARGETS,
    STATUSES,
    TARGET,
    VALID,
    CellDiagnostics,
    Curve,
    GateRecords,
    Release,
    ShpAnchor,
    grid_index,
    unit_catalog,
)
from ic_study.analysis.v4_report_tables import (
    BEYOND,
    NA,
    Table,
    number,
    region,
    strength,
    tex_escape,
    to_csv,
)
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES

SCHEMA = "ic-study.v4-result-values.v1"
# The numeral and macro patterns of pipeline/paper_check.py.
NUMBER = re.compile(
    r"(?<![A-Za-z0-9])[-+]?(?:\d+\.\d+|\d{1,3}(?:,\d{3})+|\d+)(?![A-Za-z0-9])"
)
RESULT = re.compile(r"\\resultnum\{([^{}]+)\}\{([^{}]+)\}")
PLACEHOLDER = re.compile(r"\\resultnum\{([^{}]+)\}\{(\[[^{}]*\])\}")
INPUT = re.compile(r"\\input\s*\{([^{}]+)\}")
LOW_STRENGTHS = GRID[1:3]  # the first two positive strengths (branch B04)
SHORT_STATUS = {
    VALID: "valid",
    INVALID: "invalid",
    PARTIAL: "partial",
    NOT_STARTED: "not started",
}
SYNTHETIC_CAPTION = "SYNTHETIC REHEARSAL, NOT A RESULT. "
_SYMBOLS = {
    ">=": r"$\geq$",
    "<=": r"$\leq$",
    ">": "$>$",
    "<": "$<$",
    "|": "$|$",
    "†": r"\dag{}",
    "‡": r"\ddag{}",
}
_SPECIAL = re.compile(r">=|<=|[<>|†‡]")


def latex(text: str) -> str:
    """Escape report text for a manuscript table, with math relation symbols."""
    parts: list[str] = []
    position = 0
    for match in _SPECIAL.finditer(text):
        parts += [tex_escape(text[position : match.start()]), _SYMBOLS[match.group()]]
        position = match.end()
    return "".join(parts) + tex_escape(text[position:])


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-") or "row"


@dataclass
class Binder:
    """Wraps every numeral of a cell in ``\\resultnum`` and keeps the bound values."""

    values: dict[str, str] = field(default_factory=dict)

    def _bind(self, ident: str, value: str) -> str:
        if ident in self.values:
            raise ValueError(f"Duplicate result ID {ident}")
        self.values[ident] = value
        return rf"\resultnum{{{ident}}}{{{value}}}"

    def cell(self, text: str, key: str, *, whole: bool = False) -> str:
        """Bind each numeral, or with ``whole`` the entire cell (1.52e-05)."""
        if whole and NUMBER.search(text):
            return self._bind(key, text)
        matches = list(NUMBER.finditer(text))
        parts: list[str] = []
        position = 0
        for index, match in enumerate(matches, 1):
            ident = key if len(matches) == 1 else f"{key}.{index}"
            parts += [
                latex(text[position : match.start()]),
                self._bind(ident, match.group()),
            ]
            position = match.end()
        return "".join(parts) + latex(text[position:])


# Result values cited by the Results text ---------------------------------------


def _count(flags: Iterable[bool]) -> str:
    return str(sum(bool(flag) for flag in flags))


def _valid(curve: Curve | None) -> TypeGuard[Curve]:
    return curve is not None and curve.status == VALID


def _full(curve: Curve | None) -> TypeGuard[Curve]:
    return _valid(curve) and curve.band_complete


def _attained(curve: Curve | None) -> bool:
    return _valid(curve) and curve.first.point is not None


def _crossing(curve: Curve | None) -> bool:
    """A lower band strictly above the target at some strength (M74)."""
    return _valid(curve) and any(value > TARGET for value in curve.lower)


def _below(curve: Curve | None) -> bool:
    """A complete valid band whose upper limit stays below the target."""
    return (
        _valid(curve)
        and curve.band_complete
        and all(value < TARGET for value in curve.upper)
    )


def _resolved(curve: Curve | None) -> bool:
    """Attained, with an interval of at most one grid step (frozen precision goal)."""
    if not _valid(curve) or curve.first.point is None or curve.first.interval is None:
        return False
    lo, hi = curve.first.interval
    return lo is not None and hi is not None and grid_index(hi) - grid_index(lo) <= 1


def _boundary(curve: Curve, *, sustained: bool) -> tuple[object, ...]:
    item = curve.sustained if sustained else curve.first
    return item.point, item.interval, item.censoring, item.interval_censoring


def _censored(curve: Curve) -> bool:
    return any(_boundary(curve, sustained=s)[2:] != (None, None) for s in (False, True))


def main_units(family: str) -> list[str]:
    """Unit keys of one family on the main observed grid, in r order."""
    catalog = unit_catalog()
    keys = [k for k, m in catalog.items() if m.main and m.family == family]
    return sorted(keys, key=lambda k: catalog[k].r)


def cross_mechanism_allowed(release: Release | None) -> bool:
    """Decision 91: M79 tier-2 completeness and D1 main validity govern all prose."""
    return (
        release is not None
        and release.main_curve_valid
        and all(
            release.statuses[key] == VALID
            for key, meta in unit_catalog().items()
            if meta.tier == 2
        )
    )


def _regions(release: Release, keys: Sequence[str]) -> dict[str, str]:
    """Counts of the T1 region column over complete valid units."""
    labels = [region(release.curves[k]) for k in keys if release.statuses[k] == VALID]
    gap, wide = labels.count("censored (gap)"), labels.count("indeterminate")
    return {
        "n_small": str(labels.count("small")),
        "n_large": str(labels.count("large")),
        "n_not_attained": str(labels.count("not attained")),
        "n_censored_gap": str(gap),
        "n_indeterminate": str(wide),
        "n_censored": str(gap + wide),
        "n_attained": _count(_attained(release.curves.get(k)) for k in keys),
    }


def _gap_totals(curves: Iterable[Curve]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for curve in curves:
        for kind, count in curve.gap_counts().items():
            totals[kind] = totals.get(kind, 0) + count
    return totals


def _tier1_values(release: Release) -> dict[str, str]:
    keys = main_units("B")
    curves = [release.curves.get(k) for k in keys]
    released = [c for c in curves if c is not None]
    valid = [c for c in curves if _valid(c)]
    statuses = [release.statuses[k] for k in keys]
    attained = [c for c in valid if c.first.point is not None]
    points = [cast(float, c.first.point) for c in attained]
    gaps = _gap_totals(released)
    upper = [c.upper[c.available.index(0.9)] for c in valid if 0.9 in c.available]
    values = {
        "n_valid": str(len(valid)),
        "n_not_valid": _count(s != VALID for s in statuses),
        "n_invalid_gate": _count(
            c.status == INVALID and c.cell_success[0] for c in released
        ),
        "n_invalid_a0gap": _count(
            c.status == INVALID and not c.cell_success[0] for c in released
        ),
        "n_clock": _count(s in (NOT_STARTED, PARTIAL) for s in statuses),
        "n_crossing": _count(_crossing(c) for c in valid),
        "n_resolved": _count(_resolved(c) for c in valid),
        "n_wide": _count(not _resolved(c) for c in attained),
        "n_interval_wide_finite": _count(
            c.first.interval is not None
            and all(end is not None for end in c.first.interval)
            and not _resolved(c)
            for c in attained
        ),
        "n_interval_beyond_grid": _count(
            any(
                end is None and c.first.end_censored_at(i) is None
                for i, end in enumerate(c.first.interval or (None, None))
            )
            for c in attained
        ),
        "n_interval_gap": _count(
            any(c.first.end_censored_at(i) is not None for i in (0, 1))
            for c in attained
        ),
        "n_first_ne_sustained": _count(
            _boundary(c, sustained=False) != _boundary(c, sustained=True) for c in valid
        ),
        "n_first_gap": _count(c.first.censoring is not None for c in valid),
        "n_sustained_gap": _count(c.sustained.censoring is not None for c in valid),
        "n_dip": _count(
            c.sustained.point != c.first.point and not _censored(c) for c in attained
        ),
        "n_nonmonotone_band": _count(c.nonmonotone_band is True for c in released),
        "n_first_low": _count(p in LOW_STRENGTHS for p in points),
        "n_first_zero": _count(p == 0 for p in points),
        "n_interval_lower_finite": _count(
            c.first.interval is not None and c.first.interval[0] is not None
            for c in valid
        ),
        "n_exceeds_floor": _count(c.empirical_exceeds_floor is True for c in released),
        "gap_cells": str(sum(c.gap_count for c in released)),
        "n_gap_units": _count(c.gap_count > 0 for c in released),
        "gap.screened": str(gaps.get("screened", 0)),
        "gap.profile_limit": str(gaps.get("family_limit", 0)),
        "gap.solver": str(gaps.get("solver", 0)),
        "gap.validation": str(gaps.get("validation", 0)),
        **_regions(release, keys),
        **{
            f"low.{name}": value
            for name, value in _regions(
                release,
                [c.meta.key for c in attained if c.first.point in LOW_STRENGTHS],
            ).items()
        },
    }
    if points:
        values |= {
            "first_min": strength(min(points)),
            "first_max": strength(max(points)),
        }
    if upper:
        values |= {
            "upper_a090_min": number(min(upper)),
            "upper_a090_max": number(max(upper)),
        }
    for index, target in enumerate(SECONDARY_TARGETS):
        values[f"sec{round(target * 100):03d}.n_attained"] = _count(
            c.secondary[index].point is not None for c in valid
        )
    return {f"v4.t1.{name}": value for name, value in values.items()}


def grid_runs(rs: Iterable[float]) -> str:
    """Values of r on the declared grid; three or more neighbours form a--b runs."""
    grid = [f"{r:.2f}" for r in RELIABILITIES]
    found: set[int] = set()
    for r in rs:
        # isclose, not exact membership: a stored r can carry float noise
        # (0.7 - 0.05 is 0.6499999999999999) and must not be refused.
        matches = [i for i, value in enumerate(RELIABILITIES) if math.isclose(r, value)]
        if not matches:
            raise ValueError(f"r is not on the declared grid: {r}")
        found.add(matches[0])
    index = sorted(found)
    items: list[str] = []
    start = 0
    for position, current in enumerate(index):
        if position + 1 < len(index) and index[position + 1] == current + 1:
            continue
        run = index[start : position + 1]
        if len(run) >= 3:
            items.append(f"{grid[run[0]]}--{grid[run[-1]]}")
        else:
            items.extend(grid[i] for i in run)
        start = position + 1
    if not items:
        return "none"
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _pair_values(release: Release) -> dict[str, str]:
    """B against D, E and C per r, on grids complete valid for both (M79, Q8-Q13)."""
    b_keys = main_units("B")
    allowed = cross_mechanism_allowed(release)
    out: dict[str, str] = {}
    for pair, family in (("bd", "D"), ("be", "E"), ("bc", "C")):
        other_keys = main_units(family)
        keys = [
            (x, y)
            for x, y in zip(b_keys, other_keys, strict=True)
            if allowed and _full(release.curves.get(x)) and _full(release.curves.get(y))
        ]
        pairs = [(release.curves[x], release.curves[y]) for x, y in keys]
        crossing = [y for x, y in pairs if _crossing(x)]
        persistence = sum(_below(y) for y in crossing)
        both = sum(_crossing(y) for y in crossing)
        out |= {
            f"v4.{pair}.n_eligible": str(len(pairs)),
            f"v4.{pair}.n_persistence": str(persistence),
            f"v4.{pair}.n_inconclusive": str(len(crossing) - persistence - both),
            f"v4.{pair}.n_both": str(both),
            f"v4.{pair}.n_no_b_crossing": str(len(pairs) - len(crossing)),
            f"v4.{pair}.n_other": str(len(crossing) - persistence),
            f"v4.{pair}.r_eligible": grid_runs(x.meta.r for x, _ in pairs),
            f"v4.{pair}.n_side_by_side": str(len(RELIABILITIES) if allowed else 0),
            f"v4.{pair}.r_side_by_side": grid_runs(RELIABILITIES if allowed else ()),
        }
        for member, member_keys in (
            ("B", [x for x, _ in keys]),
            (family, [y for _, y in keys]),
        ):
            out |= {
                f"v4.{pair}.{member}.{name}": value
                for name, value in _regions(release, member_keys).items()
            }
        readings: dict[str, list[float]] = {
            name: []
            for name in ("persistence", "both", "inconclusive", "no_b_crossing")
        }
        for x, y in pairs:
            reading = (
                "no_b_crossing"
                if not _crossing(x)
                else "persistence"
                if _below(y)
                else "both"
                if _crossing(y)
                else "inconclusive"
            )
            readings[reading].append(x.meta.r)
        out |= {f"v4.{pair}.r_{name}": grid_runs(rs) for name, rs in readings.items()}
    return out


def _exceeds(observed: Curve, control: Curve) -> bool:
    control_auc = dict(zip(control.available, control.auc, strict=True))
    return any(
        a in control_auc and auc > control_auc[a]
        for a, auc in zip(observed.available, observed.auc, strict=True)
    )


def _channel_values(release: Release) -> dict[str, str]:
    """Observed channel against all three registered controls (B11, Q14).

    A pair is one family and r whose observed unit and at least one of its
    masked latent, ordinal_one and latent_rank controls are complete valid.
    """
    catalog = unit_catalog()
    observed = {(m.family, m.r): k for k, m in catalog.items() if m.main}
    controls: dict[tuple[str, float], list[str]] = {}
    for key, meta in catalog.items():
        control = meta.channel in ("latent", "ordinal_one", "latent_rank")
        if meta.tier == 3 and meta.sensitivity == "main" and control:
            controls.setdefault((meta.family, meta.r), []).append(key)
    compared = exceeds = dependent = not_assessed = 0
    for pair, keys in controls.items():
        obs = release.curves.get(observed[pair])
        valid = [c for c in (release.curves.get(k) for k in keys) if _valid(c)]
        if _valid(obs) and valid:
            compared += 1
            exceeds += any(_exceeds(obs, c) for c in valid)
        if _valid(obs):
            full_controls = [c for c in valid if _full(c)]
            if len(full_controls) != 3:
                not_assessed += 1
            else:
                dependent += obs.first.point is not None and all(
                    c.first.point is None for c in full_controls
                )
    dependency = _gap_totals(
        c for k, c in release.curves.items() if catalog[k].tier == 3
    ).get("dependency", 0)
    return {
        "v4.t3.n_pairs_compared": str(compared),
        "v4.t3.n_obs_exceeds": str(exceeds),
        "v4.t3.n_channel_dependent": str(dependent),
        "v4.t3.n_channel_not_assessed": str(not_assessed),
        "v4.t3.gap.dependency": str(dependency),
    }


def _sensitivity_values(release: Release) -> dict[str, str]:
    """Tiers 4-6 against the main B unit at the same r (B12, Q22)."""
    catalog = unit_catalog()
    b = {catalog[k].r: k for k in main_units("B")}
    compared = differs = 0
    for key, meta in catalog.items():
        curve, base = release.curves.get(key), release.curves.get(b[meta.r])
        if meta.tier >= 4 and _valid(curve) and _valid(base):
            compared += 1
            differs += region(curve) != region(base)
    not_valid = sum(
        release.statuses[key] != VALID
        for key, meta in catalog.items()
        if meta.tier >= 4
    )
    return {
        "v4.sens.n_pairs_compared": str(compared),
        "v4.sens.n_region_differs": str(differs),
        "v4.sens.n_not_valid": str(not_valid),
        "v4.sens.use_b12": str(int(bool(differs or not_valid))),
    }


def _inventory_values(release: Release) -> dict[str, str]:
    """D9 status counts over the inventory and per tier (T4 rows)."""
    catalog = unit_catalog()
    names = ("n_not_started", "n_partial", "n_invalid", "n_valid")
    scopes: list[tuple[str, list[str]]] = [("v4.inv", list(catalog))]
    scopes += [
        (f"v4.inv.t{tier}", [k for k, m in catalog.items() if m.tier == tier])
        for tier in sorted({m.tier for m in catalog.values()})
    ]
    out: dict[str, str] = {}
    for prefix, keys in scopes:
        statuses = [release.statuses[k] for k in keys]
        for status, name in zip(STATUSES, names, strict=True):
            out[f"{prefix}.{name}"] = str(statuses.count(status))
        out[f"{prefix}.n_incomplete"] = _count(
            s in (NOT_STARTED, PARTIAL) for s in statuses
        )
    for family in FAMILIES[1:]:
        out |= {
            f"v4.t2.{family}.{name}": value
            for name, value in _regions(release, main_units(family)).items()
        }
    curves = list(release.curves.values())
    out["v4.all.n_curves"] = str(len(curves))
    out["v4.all.n_exceeds_floor"] = _count(
        c.empirical_exceeds_floor is True for c in curves
    )
    return out


@dataclass(frozen=True)
class LowCell:
    """A cell at the first two positive strengths of a B unit whose a* lies there."""

    r: float
    a: float
    diagnostics: CellDiagnostics

    @property
    def retry(self) -> bool:
        return protocol().retry_pairs in self.diagnostics.matching_pairs


def low_cells(release: Release) -> list[LowCell]:
    """The cells that branch B04 and its supplementary table describe (M5)."""
    cells: list[LowCell] = []
    for key in main_units("B"):
        curve = release.curves.get(key)
        if _valid(curve) and curve.first.point in LOW_STRENGTHS:
            cells += [
                LowCell(curve.meta.r, a, curve.diagnostics[grid_index(a)])
                for a in LOW_STRENGTHS
            ]
    return cells


def _low_values(release: Release) -> dict[str, str]:
    cells = low_cells(release)
    fractions = [
        c.diagnostics.projected_fraction
        for c in cells
        if c.diagnostics.projected_fraction is not None
    ]
    amplification = [
        c.diagnostics.amplification
        for c in cells
        if c.diagnostics.amplification is not None
    ]
    out = {
        "v4.low.n_cells": str(len(cells)),
        "v4.low.n_retry": _count(c.retry for c in cells),
    }
    if fractions:
        out["v4.low.projected_fraction_max"] = number(max(fractions))
    if amplification:
        out["v4.low.amplification_max"] = number(max(amplification))
    return out


def _shp_values(release: Release | None, shp: ShpAnchor) -> dict[str, str]:
    lo, hi = shp.wald_95_interval
    if release is None:
        return {
            "v4.shp.estimate": number(shp.estimate),
            "v4.shp.wald_lo": number(lo),
            "v4.shp.wald_hi": number(hi),
            "v4.shp.env_lo": number(shp.sensitivity_envelope[0]),
            "v4.shp.env_hi": number(shp.sensitivity_envelope[1]),
        }
    inside = [r for r in RELIABILITIES if lo <= r <= hi]
    b = {unit_catalog()[k].r: k for k in main_units("B")}
    classes = {
        (
            release.statuses[b[r]],
            region(release.curves[b[r]]) if b[r] in release.curves else NA,
        )
        for r in inside
    }
    out = {
        "v4.shp.year": str(shp.year),
        "v4.shp.estimate": number(shp.estimate),
        "v4.shp.standard_error": number(shp.standard_error),
        "v4.shp.wald_lo": number(lo),
        "v4.shp.wald_hi": number(hi),
        "v4.shp.env_lo": number(shp.sensitivity_envelope[0]),
        "v4.shp.env_hi": number(shp.sensitivity_envelope[1]),
        "v4.shp.n_r_in_interval": str(len(inside)),
        "v4.shp.n_status_classes": str(len(classes)),
    }
    starts = shp.starts
    if starts is not None and starts.estimate is not None:
        out["v4.shp.starts.estimate"] = number(starts.estimate)
        if starts.wald_95_interval is not None:
            out["v4.shp.starts.wald_lo"] = number(starts.wald_95_interval[0])
            out["v4.shp.starts.wald_hi"] = number(starts.wald_95_interval[1])
    return out


def _stage_values(
    stage: str, summary: Mapping[str, Any], thresholds: Mapping[str, float] | None
) -> dict[str, str]:
    """Criterion values of one aggregate summary, printed as T3 prints them."""
    out = {name: str(summary[name]) for name in ("planned", "completed", "failures")}
    if stage == "G0" and "fits" in summary:
        fits, impl = int(summary["fits"]), int(summary["implementation_statuses"])
        out |= {
            name: str(summary[name])
            for name in (
                "fits",
                "anchor_failures",
                "budget_statuses",
                "implementation_statuses",
            )
        }
        out["implementation_share"] = number(impl / fits if fits else math.nan, 4)
    elif stage == "G1b" and "coverage_counts" in summary:
        counts = cast(dict[str, int], summary["coverage_counts"]).values()
        out |= {
            "coverage_min": str(min(counts)),
            "n_scenarios_below": _count(c < protocol().g1b_pass_mark for c in counts),
            "exceeds_floor_count": str(summary["empirical_exceeds_floor_count"]),
        }
    elif stage == "G1c" and "anchor_count" in summary:
        out |= {
            "anchor_count": str(summary["anchor_count"]),
            "pointwise_failures": str(summary["pointwise_failures"]),
            "mean_z": number(summary["mean_z"]),
            "tie_rate": number(summary["tie_rate"], 4),
        }
    elif stage == "G2":
        out |= _g2_values(summary, thresholds)
    elif stage == "G2c":
        for comparison, cell in zip(
            cast(list[dict[str, Any]], summary.get("comparisons", [])),
            ("a010", "a003"),
            strict=False,
        ):
            out[f"{cell}.failures"] = str(comparison["failure_count"])
            out[f"{cell}.denominator"] = str(comparison["denominator"])
            if "ratio" in comparison:
                for name in ("ratio", "lower", "upper"):
                    out[f"{cell}.{name}"] = number(comparison[name])
    return out


def _g2_values(
    summary: Mapping[str, Any], thresholds: Mapping[str, float] | None
) -> dict[str, str]:
    out: dict[str, str] = {}
    failures = cast(list[int], summary.get("cell_failure_counts", []))
    if failures:
        out |= {"n_cells": str(len(failures)), "max_cell_failures": str(max(failures))}
    if summary.get("cell_ratios"):
        for name in ("pooled_ratio", "pooled_lower", "pooled_upper"):
            out[name] = number(summary[name])
        if thresholds is not None:
            out["n_cells_above"] = _count(
                lo > thresholds["cell_upper"] for lo in summary["cell_lower"]
            )
            out["n_cells_below"] = _count(
                hi < thresholds["cell_lower"] for hi in summary["cell_upper"]
            )
    medians = cast(list[float | None], summary.get("fd_ratio_median_by_cell", []))
    finite = [m for m in medians if m is not None and math.isfinite(m)]
    if medians:
        low, high = protocol().fd_range
        inside = sum(low <= m <= high for m in finite)
        out["n_cells_fd_outside"] = str(len(medians) - inside)
    if finite:
        out |= {
            "fd_median_min": number(min(finite)),
            "fd_median_max": number(max(finite)),
        }
    if "covariance_flag_counts" in summary:
        out["covariance_flags"] = str(sum(summary["covariance_flag_counts"]))
    return out


def gate_values(
    gate: GateRecords, thresholds: Mapping[str, float] | None
) -> dict[str, str]:
    """Gate criteria (T3 values), the pre-G2 stop and an unfinished stage (B1d)."""
    out: dict[str, str] = {}
    for stage in GATE_STAGES:
        verdict = gate.verdict(stage)
        out |= {
            f"v4.gate.{stage}.verdict.complete": str(int(verdict in {PASS, FAIL})),
            f"v4.gate.{stage}.verdict.approved": str(int(verdict == PASS)),
            f"v4.gate.{stage}.verdict.stop": str(
                int(stage == "G2" and gate.stop is not None)
            ),
        }
        summary = gate.summaries.get(stage)
        if summary is not None:
            out |= {
                f"v4.gate.{stage}.{name}": value
                for name, value in _stage_values(stage, summary, thresholds).items()
            }
    if gate.stop is not None:
        binding = cast(dict[str, Any], gate.stop["g0_gap_binding"])
        out |= {
            "v4.gate.stop.gaps": str(binding["gaps"]),
            "v4.gate.stop.denominator": str(binding["denominator"]),
            "v4.gate.stop.pass_probability": number(binding["pass_probability"]),
            "v4.gate.stop.minimum": number(binding["minimum"], 2),
        }
    for stage in GATE_STAGES:
        verdict = gate.verdict(stage)
        if verdict == PASS:
            continue
        if verdict != FAIL and gate.stop is None:
            done, planned = gate.progress(stage) or (0, gate.planned[stage])
            out |= {
                "v4.gate.last_stage": stage,
                "v4.gate.last_stage.completed": str(done),
                "v4.gate.last_stage.planned": str(planned),
            }
        break
    return out


def result_values(loaded: Loaded) -> dict[str, str]:
    """Every count, estimate and protocol constant the Results text may cite."""
    out = protocol_values()
    out["v4.mechanisms.allowed"] = str(int(cross_mechanism_allowed(loaded.release)))
    if loaded.release_record is not None:
        receipt = loaded.release_record
        actual = datetime.fromisoformat(receipt.released_utc).astimezone(
            ZoneInfo(CLOSE_ZONE)
        )
        out |= {
            "v4.release.effective_local": (
                f"{actual.day} {actual:%B %Y} at {actual:%H:%M:%S}"
            ),
            "v4.release.effective_utc": receipt.released_utc,
            "v4.release.condition": {
                "inventory-complete": "completion of the full inventory",
                "declared-close": "the declared close",
            }[receipt.condition],
        }
    if loaded.gate is not None:
        out |= gate_values(loaded.gate, loaded.thresholds)
        for key in ("completed", "exceeds_floor_count"):
            ident = "v4.gate.G1b." + key
            if ident in out:
                out[ident + "_prose"] = f"{int(out[ident]):,}"
    release = loaded.release
    if release is not None:
        out |= _inventory_values(release)
        out |= _tier1_values(release)
        out |= _pair_values(release)
        out |= _channel_values(release)
        out |= _sensitivity_values(release)
        out |= _low_values(release)
    if loaded.shp is not None:
        out |= _shp_values(release, loaded.shp)
    return out


# Generated LaTeX -----------------------------------------------------------------

CAPTION_T3 = (
    "Validation-gate outcomes from the sealed gate records (D7; v4.1): tasks, task "
    "failures and criterion values against the registered criterion, with the stage "
    "verdict in parentheses. Each stage uses its criteria line with the most "
    "completed tasks; in progress means fewer tasks aggregated than planned. G2 "
    "cells carry their (a, r) from the second binding record; bracketed values are "
    "bootstrap intervals. A summary that the frozen runner could not append is read "
    "from its documented successor record."
)
CAPTION_F4 = (
    "Validation-gate diagnostics from the sealed gate records: (a) final status of "
    "every G0 fit, (b) G0 solver evaluations per attempt against the frozen budget, "
    "(c) G1b joint coverage per synthetic-score scenario, (d) G1b critical values "
    "against the 2.7729 floor, (e) G2 dispersion ratios with bootstrap intervals and "
    "the calibrated thresholds, (f) G2c variance ratios with one-sided bounds, and "
    "(g) tasks completed and verdict per stage. Family limits are gaps, not failures."
)
CAPTION_T4 = (
    "Inventory at the close of the compute window (D9): units by status for each "
    "frozen configuration, each tier and in total, and the gap cells of the released "
    "curves by kind. NS not started (não iniciado), P partial at operational close "
    "(parcial por encerramento operacional), CI complete invalid (completo "
    "inválido), CV complete valid (completo válido). Gap cells: scr. family limit "
    "screened with no solver evaluation, fam. family limit on the profile, sol. "
    "other solver status, val. accepted status that failed validation, dep. control "
    "whose observed fit failed, prop. ill-conditioned nuisance propagation recorded "
    "as a gap by amendment v4.4. Family limits are gaps, not failures."
)
CAPTION_F5 = (
    "Status of every unit of the frozen inventory at the close of the compute "
    r"window (D9), by frozen configuration and signal share $r$, with counts in the "
    r"legend; \dag marks the calibration-exposed $r$."
)
CAPTION_F1 = (
    r"Detection boundary $a^*(r)$ against the confirmatory null family B "
    "(trait-plus-autoregressive persistence) and the secondary families A "
    "(autoregressive "
    "persistence), C (autoregressive persistence with an altered response "
    "channel), D (state-dependent persistence) and E (mover--stayer persistence). "
    r"The horizontal axis is the continuous response signal share $r$; the "
    r"vertical axis is the nominal partner-drift strength $a$ at the positions of "
    r"the frozen grid, so equal spacing does not denote equal increments of $a$, "
    r"and nothing is interpolated. Filled circles give $a^*$ and bars its interval "
    r"by inclusive inversion of the per-$r$ band; open circles give the sustained "
    r"boundary $a_s^*$ of B. Triangles: not reached on the complete eligible grid; "
    "open squares: censored at a gap; the strip below marks units without a valid "
    "curve. Gray B markers in the other panels are a descriptive reference, not a "
    r"between-family inference. Bands are simultaneous over the strengths of one "
    r"$r$ only. \dag marks the calibration-exposed $r$."
)
CAPTION_F2 = (
    r"Released panel-level AUC profiles of the fixed discriminator behind "
    r"$a^*(r)$ against family FAMILY, one panel per response signal share $r$: "
    r"point AUC and per-$r$ 95\% band at each available strength position, the "
    r"primary target 0.70 (dashed), 0.5 (dotted), $a^*$ (vertical line) and its "
    r"interval (shaded). Strength positions are ordinal. The band is simultaneous "
    r"over the strengths of one $r$ only and gives no joint coverage across $r$, "
    "families or channels. Crosses mark gap cells. No value of $r$ is selected."
)
CAPTION_T1 = (
    "First and sustained boundaries on the main grid at the primary target AUC "
    "0.70: tier 1 (B, confirmatory) and tier 2 (A, C, D, E), with the status at the "
    r"close, the a = 0 null gate, the gap cells, $a^*$ and $a_s^*$ with their "
    r"inverted intervals in brackets, and the region of $a^*$. $>0.9$: not reached "
    "on the complete eligible grid; censored (gap): a boundary censored by a "
    "gap; NA: no boundary for an invalid or unfinished unit; gap x: censored "
    "at the gap at a = x by the "
    "frozen gap-censoring rule; suppressed: failed null gate. Regions: small "
    r"$0<a^*\le0.03$, large $0.03<a^*\le0.9$; indeterminate when $a^*=0$ or the "
    r"interval crosses 0.03 or has a censored end. \dag calibration-exposed $r$. "
    "The secondary targets 0.60 and 0.80 appear only in the supplementary "
    "secondary-target table; gap types, controls, sensitivities and diagnostics "
    "are in the complete inventory records."
)
CAPTION_MAIN_INVALID = (
    r" \ddag Main curve invalid: a tier-1 B unit is not complete valid, and every "
    "B row carries this mark (amendment v4)."
)
CAPTION_SECONDARY = (
    "Derived first boundaries against B at the secondary targets 0.60 (lower) and "
    "0.80 (upper) of the preregistration, with their inverted intervals in "
    "brackets, from the released bands by the frozen inversion and gap censoring; "
    "the frozen release emits the 0.70 boundaries only. Short forms as in the "
    "boundary table."
)
CAPTION_F3 = (
    r"Exploratory and descriptive: offset of each secondary family's $a^*$ from "
    r"B's in grid steps, at every $r$ where both units are complete valid and reach "
    "the target. No between-family contrast is registered, so the offsets carry no "
    "interval, test or registered interpretation."
)
CAPTION_LOW = (
    r"Cells at the first two positive strengths of every B unit whose first "
    r"boundary lies there: whether the retry with more matching pairs was used, "
    r"the residuals of the final attempt in standard-error units at lags one and "
    r"two, the amplification diagnostic, the nuisance variance with its "
    "Monte Carlo standard error, the mean shift of the local AUC draws and the "
    "fraction of projected draws, as released with each cell."
)
CAPTION_GAPS = (
    "Eligible domain of every B unit: the strengths whose cell was not excluded by "
    "the feasibility screen, and the gap cells by final status (screened family "
    "limit, family limit on the profile, other solver status, failed validation). "
    "Units without a released curve are NA."
)
CAPTION_F6 = (
    "Exploratory positioning of distinct quantities, without an empirically "
    r"calibrated equivalence to $r$ or an item-specific boundary: the boundaries "
    r"$a^*(r)$ with the SHP reliability anchor, namely the quasi-simplex estimate "
    r"(dashed) and its model-based Wald 95\% interval (shaded), the envelope of "
    "the nine Heise triplet estimates (hatched; a specification envelope, not a "
    "confidence interval), the STARTS sensitivity when admissible (dotted) and, "
    r"when given, the grid values of $r$ whose synthetic crosswalk range contains "
    "the SHP value. The crosswalk ranges are descriptive and do not propagate the "
    "uncertainty of the empirical anchor. The anchor is placed without choosing "
    r"or rounding to a value of $r$ and without interpolating or extrapolating "
    r"$a^*(r)$. Source: Swiss Household Panel (SHP)."
)


@dataclass(frozen=True)
class Column:
    header: str  # LaTeX without numerals
    key: str  # component of the cell's result IDs
    align: str = "l"
    whole: bool = False  # bind the whole cell, for scientific notation


def _tabular(
    binder: Binder,
    prefix: str,
    columns: Sequence[Column],
    rows: Sequence[tuple[str, Sequence[str]]],
) -> list[str]:
    lines = [
        r"\begin{tabular}{" + "".join(c.align for c in columns) + "}",
        r"\toprule",
        " & ".join(c.header for c in columns) + r" \\",
        r"\midrule",
    ]
    for key, cells in rows:
        lines.append(
            " & ".join(
                binder.cell(text, f"{prefix}.{key}.{column.key}", whole=column.whole)
                for column, text in zip(columns, cells, strict=True)
            )
            + r" \\"
        )
    return [*lines, r"\botrule", r"\end{tabular}"]


def _caption(text: str, label: str, synthetic: bool) -> str:
    return (
        rf"\caption{{{SYNTHETIC_CAPTION if synthetic else ''}{text}}}\label{{{label}}}"
    )


def _table_float(
    caption: str, label: str, size: str, tabular: list[str], synthetic: bool
) -> list[str]:
    return [
        r"\begin{table*}[tp]",
        _caption(caption, label, synthetic),
        rf"\centering\{size}",
        r"\setlength{\tabcolsep}{3pt}",
        *tabular,
        r"\end{table*}",
    ]


def _figure_float(
    path: str, caption: str, label: str, synthetic: bool, *, wide: bool = True
) -> list[str]:
    """A double-column figure fits the text block, leaving room for its caption."""
    env = "figure*" if wide else "figure"
    size = (
        r"width=\textwidth,height=175mm,keepaspectratio"
        if wide
        else r"width=\columnwidth"
    )
    return [
        rf"\begin{{{env}}}[tp]",
        r"\centering",
        rf"\includegraphics[{size}]{{{path}}}",
        _caption(caption, label, synthetic),
        rf"\end{{{env}}}",
    ]


def _rows(table: Table) -> list[dict[str, str]]:
    return [dict(zip(table.header, row, strict=True)) for row in table.rows]


def _short(cell: str) -> str:
    """Short forms that the table captions define for the T1 boundary cells."""
    cell = cell.replace(f"not reached ({BEYOND})", BEYOND)
    return cell.replace("censored at gap a=", "gap ")


def _estimate(point: str, lower: str, upper: str) -> str:
    """A boundary with its inverted interval in brackets, as one cell."""
    if (lower, upper) == (NA, NA):
        return _short(point)
    return f"{_short(point)} [{_short(lower)}, {_short(upper)}]"


def _r_cell(row: Mapping[str, str]) -> str:
    return row["r"] + ("†" if row["exposure"] else "")


def gate_tabular(table: Table, binder: Binder, dependency_gaps: int = 0) -> list[str]:
    """T3 with each stage named once and its verdict in parentheses below it."""
    columns = (
        Column("Stage", "stage", "p{1.3cm}"),
        Column("Item", "item", "p{5.6cm}"),
        Column("Value", "value", "p{3.7cm}"),
        Column("Criterion", "criterion", "p{4.1cm}"),
    )
    groups: dict[str, list[tuple[str, ...]]] = {}
    for row in table.rows:
        groups.setdefault(row[0], []).append(row)
    rows: list[tuple[str, Sequence[str]]] = []
    for stage, members in groups.items():
        if (
            stage == "G0"
            and dependency_gaps
            and any(row[1].startswith("status ") for row in members)
        ):
            members = [
                *members,
                (
                    "G0",
                    "status dependency gap",
                    str(dependency_gaps),
                    "reported",
                    members[0][4],
                ),
            ]
        verdict = f"({members[0][4]})"
        labels = [stage, verdict] if len(members) > 1 else [f"{stage} {verdict}"]
        labels += [""] * (len(members) - len(labels))
        for label, (_, item, value, criterion, _) in zip(labels, members, strict=True):
            rows.append(
                (f"{slug(stage)}.{slug(item)}", (label, item, value, criterion))
            )
    return _tabular(binder, "v4.tab.T3", columns, rows)


def inventory_tabular(table: Table, binder: Binder) -> list[str]:
    """T4 with abbreviated status and gap-kind headers."""
    heads = ("NS", "P", "CI", "CV", "scr.", "fam.", "sol.", "val.", "dep.", "prop.")
    keys = (
        "not_started",
        "partial",
        "invalid",
        "valid",
        "gaps_screened",
        "gaps_family_limit",
        "gaps_solver",
        "gaps_validation",
        "gaps_dependency",
        "gaps_propagation",
    )
    columns = (
        Column("Tier", "tier"),
        Column("Family", "family"),
        Column("Channel", "channel"),
        Column("Sensitivity", "sensitivity"),
        Column("Units", "units", "r"),
        *(Column(h, k, "r") for h, k in zip(heads, keys, strict=True)),
    )
    rows = [(slug("-".join(row[:4])), row) for row in table.rows]
    return _tabular(binder, "v4.tab.T4", columns, rows)


def boundary_tabular(table: Table, binder: Binder) -> tuple[list[str], bool]:
    """T1 boundary columns; the flag says whether the main curve is invalid."""
    columns = (
        Column("Family", "family"),
        Column("$r$", "r", "r"),
        Column("Status", "status"),
        Column("Null gate", "null_gate"),
        Column("Gaps", "gaps", "r"),
        Column("$a^*$ [interval]", "a_star", "p{3.4cm}"),
        Column("$a_s^*$ [interval]", "a_s_star", "p{3.4cm}"),
        Column("Region", "region"),
    )
    rows: list[tuple[str, Sequence[str]]] = []
    for row in _rows(table):
        rows.append(
            (
                f"{row['family']}.r{row['r'].replace('.', '')}",
                (
                    row["family"] + ("‡" if row["main_curve_flag"] else ""),
                    _r_cell(row),
                    SHORT_STATUS[row["status"]],
                    row["null_gate"],
                    row["gaps"],
                    _estimate(row["a_star"], row["a_star_lower"], row["a_star_upper"]),
                    _estimate(
                        row["a_s_star"], row["a_s_star_lower"], row["a_s_star_upper"]
                    ),
                    row["region"],
                ),
            )
        )
    invalid = any(row["main_curve_flag"] for row in _rows(table))
    return _tabular(binder, "v4.tab.T1", columns, rows), invalid


def secondary_tabular(table: Table, binder: Binder) -> list[str]:
    """Derived boundaries of B at the secondary targets (T1 derived columns)."""
    columns = (
        Column("$r$", "r", "r"),
        Column("$a^*$ [interval], lower target", "a060", "p{5cm}"),
        Column("$a^*$ [interval], upper target", "a080", "p{5cm}"),
    )
    rows: list[tuple[str, Sequence[str]]] = []
    for row in _rows(table):
        if row["family"] == "B":
            cells = [_r_cell(row) + ("‡" if row["main_curve_flag"] else "")]
            for target in ("060", "080"):
                name = f"derived_a_star_{target}"
                cells.append(
                    _estimate(row[name], row[f"{name}_lower"], row[f"{name}_upper"])
                )
            rows.append((f"B.r{row['r'].replace('.', '')}", cells))
    return _tabular(binder, "v4.tab.T1sec", columns, rows)


def _scientific(value: float | None) -> str:
    return NA if value is None else f"{value:.2e}"


def low_tabular(release: Release, binder: Binder) -> list[str]:
    """Fit and nuisance diagnostics of every cell that branch B04 describes."""
    columns = (
        Column("$r$", "r", "r"),
        Column("$a$", "a", "r"),
        Column("Retry", "retry"),
        Column("Residuals (SE units)", "residuals"),
        Column("Amplification", "amplification", "r"),
        Column("$V_{nuis}$", "variance", "r", whole=True),
        Column("MCSE of $V_{nuis}$", "mcse", "r", whole=True),
        Column("Mean shift", "mean_shift", "r", whole=True),
        Column("Projected", "projected", "r"),
    )
    rows: list[tuple[str, Sequence[str]]] = []
    for cell in low_cells(release):
        found = cell.diagnostics
        residuals = ", ".join(number(v, 2) for v in found.residual_se_units) or NA
        rows.append(
            (
                f"B.r{places(cell.r).replace('.', '')}.a{tag(cell.a)}",
                (
                    f"{cell.r:.2f}",
                    strength(cell.a),
                    "yes" if cell.retry else "no",
                    residuals,
                    number(found.amplification),
                    _scientific(found.nuisance_variance),
                    _scientific(found.nuisance_mcse),
                    _scientific(found.mean_shift),
                    number(found.projected_fraction),
                ),
            )
        )
    return _tabular(binder, "v4.tab.Slow", columns, rows)


def gap_domain_tabular(release: Release, binder: Binder) -> list[str]:
    """Eligible domain (strengths not screened) and gap cells of each B unit."""
    kinds = ("screened", "family_limit", "solver", "validation")
    columns = (
        Column("$r$", "r", "r"),
        Column("Status", "status"),
        Column("Strengths not excluded by the screen", "eligible", "p{6cm}"),
        *(Column(k.replace("_", " "), k, "r") for k in kinds),
    )
    rows: list[tuple[str, Sequence[str]]] = []
    catalog = unit_catalog()
    for key in main_units("B"):
        r = catalog[key].r
        curve = release.curves.get(key)
        if curve is None:
            cells = [NA] * (1 + len(kinds))
        else:
            eligible = [
                strength(a)
                for a, kind in zip(GRID, curve.cell_gap, strict=True)
                if kind != "screened"
            ]
            counts = curve.gap_counts()
            cells = [", ".join(eligible), *(str(counts[k]) for k in kinds)]
        rows.append(
            (
                f"B.r{places(r).replace('.', '')}",
                (f"{r:.2f}", SHORT_STATUS[release.statuses[key]], *cells),
            )
        )
    return _tabular(binder, "v4.tab.Sgaps", columns, rows)


NO_RELEASE = (
    "No release exists: the gate did not pass before the close (Results branches "
    "B1b, B1c and B1d), so this output is absent."
)
PLACEHOLDERS = (
    "gate-outcomes",
    "unit-status",
    "primary-boundary-figure",
    "auc-profiles",
    "boundary-table",
    "shp-anchor",
    "supplement-auc-profiles",
    "supplement-family-offsets",
    "supplement-secondary-targets",
    "supplement-low-strength-cells",
    "supplement-gap-domain",
)


def generated_files(
    loaded: Loaded, figure: Callable[[str], str], synthetic: bool
) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Content of every generated file and the table cells it binds.

    ``figure`` maps a report figure name to its path from the manuscript root. An
    output that does not exist gets a comment that says why, so the manuscript
    keeps one ``\\input`` per file whatever the outcome.
    """
    binder = Binder()
    tables = {table.name: table for table in report_tables(loaded)}
    files: dict[str, list[str]] = {name: [f"% {NO_RELEASE}"] for name in PLACEHOLDERS}
    if "T3_gate_summary" in tables:
        files["gate-outcomes"] = [
            *_table_float(
                CAPTION_T3,
                "tab:v4-T3",
                "scriptsize",
                gate_tabular(
                    tables["T3_gate_summary"],
                    binder,
                    sum(fit.gap == "dependency" for fit in loaded.gate.g0_fits)
                    if loaded.gate is not None
                    else 0,
                ),
                synthetic,
            ),
            *_figure_float(
                figure("F4_gate_diagnostics"), CAPTION_F4, "fig:v4-F4", synthetic
            ),
        ]
    release = loaded.release
    if release is None:
        return files, binder.values
    boundaries, invalid = boundary_tabular(tables["T1_a_star_grid"], binder)
    files |= {
        "unit-status": [
            *_table_float(
                CAPTION_T4,
                "tab:v4-T4",
                "scriptsize",
                inventory_tabular(tables["T4_inventory"], binder),
                synthetic,
            ),
            *_figure_float(
                figure("F5_inventory_status"), CAPTION_F5, "fig:v4-F5", synthetic
            ),
        ],
        "primary-boundary-figure": _figure_float(
            figure("F1_a_star_by_family"), CAPTION_F1, "fig:v4-F1", synthetic
        ),
        "auc-profiles": _figure_float(
            figure("F2_auc_profiles_B"),
            CAPTION_F2.replace("FAMILY", "B"),
            "fig:v4-F2B",
            synthetic,
        ),
        "boundary-table": _table_float(
            CAPTION_T1 + (CAPTION_MAIN_INVALID if invalid else ""),
            "tab:v4-T1",
            "scriptsize",
            boundaries,
            synthetic,
        ),
        "shp-anchor": [
            "% No SHP aggregate report was given (Results branch B14), so F6 is absent."
        ],
        "supplement-auc-profiles": [
            line
            for family in FAMILIES[1:]
            for line in _figure_float(
                figure(f"F2_auc_profiles_{family}"),
                CAPTION_F2.replace("FAMILY", family),
                f"fig:v4-F2{family}",
                synthetic,
            )
        ],
        "supplement-family-offsets": _figure_float(
            figure("F3_exploratory_family_offsets_vs_B"),
            CAPTION_F3,
            "fig:v4-F3",
            synthetic,
            wide=False,
        )
        if cross_mechanism_allowed(release)
        else ["% MECHANISMS permission is absent, so P7 and F3 do not apply."],
        "supplement-secondary-targets": _table_float(
            CAPTION_SECONDARY + (CAPTION_MAIN_INVALID if invalid else ""),
            "tab:v4-sec",
            "footnotesize",
            secondary_tabular(tables["T1_a_star_grid"], binder),
            synthetic,
        ),
        "supplement-low-strength-cells": [
            "% No first boundary against B lies at the first two positive strengths,"
            " so branch B04 and this table do not apply."
        ],
        "supplement-gap-domain": _table_float(
            CAPTION_GAPS,
            "tab:v4-sgaps",
            "footnotesize",
            gap_domain_tabular(release, binder),
            synthetic,
        ),
    }
    if low_cells(release):
        files["supplement-low-strength-cells"] = _table_float(
            CAPTION_LOW,
            "tab:v4-slow",
            "footnotesize",
            low_tabular(release, binder),
            synthetic,
        )
    if loaded.shp is not None:
        files["shp-anchor"] = _figure_float(
            figure("F6_a_star_shp_anchor"), CAPTION_F6, "fig:v4-F6", synthetic
        )
    return files, binder.values


# Export ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Export:
    """The bound values of one export and the generated files it wrote."""

    catalog: dict[str, str]
    written: tuple[Path, ...]
    synthetic: bool
    manifest_sha256: str


def verified_manifest(report: Path, inputs: Inputs, loaded: Loaded) -> dict[str, Any]:
    """The report manifest, once its inputs and tables match these inputs."""
    manifest = cast(
        dict[str, Any],
        json.loads((report / "manifest.json").read_text(encoding="utf-8")),
    )
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError("Not a v4 report manifest")
    if manifest["inputs"] != input_record(inputs, loaded):
        raise ValueError("The report was rendered from other inputs")
    suffix = "_synthetic" if manifest["synthetic"] else ""
    for table in report_tables(loaded):
        name = f"{table.name}{suffix}.csv"
        path = report / name
        if manifest["outputs"].get(name) != sha256(path) or path.read_text(
            encoding="utf-8"
        ) != to_csv(table):
            raise ValueError(f"{name} differs from the rendered report")
    return manifest


def tex_sources(root: Path) -> dict[Path, str]:
    """``main.tex`` and every file it inputs, as ``paper_check.py`` reads them."""
    found: dict[Path, str] = {}

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in found:
            return
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"missing or outside manuscript: {path}")
        source = path.read_text(encoding="utf-8")
        found[path] = source
        for name in INPUT.findall(source):
            visit(root / (name if name.endswith(".tex") else name + ".tex"))

    visit(root / "main.tex")
    return found


def used_ids(manuscript: Path) -> set[str]:
    return {
        match.group(1)
        for source in tex_sources(manuscript).values()
        for match in RESULT.finditer(source)
    }


def fill(manuscript: Path, catalog: Mapping[str, str]) -> None:
    """Replace ``\\resultnum{id}{[..]}`` placeholders with the exported values."""

    def value(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in catalog:
            return match.group(0)
        return rf"\resultnum{{{key}}}{{{catalog[key]}}}"

    for path, source in tex_sources(manuscript).items():
        filled = PLACEHOLDER.sub(value, source)
        if filled != source:
            path.write_text(filled, encoding="utf-8")


def export(inputs: Inputs, report: Path, manuscript: Path) -> Export:
    """Verify the report, then write the generated files and copy their figures.

    The all-units table T1s goes beside them as the CSV of the electronic
    supplementary material; it is too long for the two-column layout.
    """
    metadata = json.loads((report / "manifest.json").read_bytes())
    synthetic = metadata.get("synthetic") is True
    loaded = load_inputs(inputs, synthetic=synthetic)
    manifest = verified_manifest(report, inputs, loaded)
    copies: list[str] = []

    def output(stem: str, suffix: str) -> str:
        file = f"{stem}_synthetic{suffix}" if synthetic else f"{stem}{suffix}"
        if file not in manifest["outputs"]:
            raise ValueError(f"The report has no {file}; render with PDF figures")
        if manifest["outputs"][file] != sha256(report / file):
            raise ValueError(f"{file} differs from the rendered report")
        copies.append(file)
        return f"generated/{file}"

    def figure(name: str) -> str:
        return output(name, ".pdf")

    files, cells = generated_files(loaded, figure, synthetic)
    if loaded.release is not None:
        output("T1s_a_star_all_units", ".csv")
    values = result_values(loaded)
    if values.keys() & cells.keys():
        raise ValueError("Table cell IDs collide with result IDs")
    digest = sha256(report / "manifest.json")
    header = [
        "% Generated by ic_study.analysis.v4_report_export from the v4 report with",
        f"% manifest SHA-256 {digest}. Export again instead of editing this file.",
    ]
    if synthetic:
        header.append("% SYNTHETIC REHEARSAL: artificial values, not a result.")
    target = manuscript / "generated"
    target.mkdir(parents=True, exist_ok=True)
    for file in copies:
        shutil.copyfile(report / file, target / file)
    written = []
    for name, lines in files.items():
        path = target / f"{name}.tex"
        path.write_text("\n".join([*header, *lines]) + "\n", encoding="utf-8")
        written.append(path)
    return Export(values | cells, tuple(written), synthetic, digest)


def values_record(result: Export, ids: Iterable[str]) -> dict[str, object]:
    """The ``{"values": ...}`` object that ``paper_check.py`` reads, with provenance."""
    return {
        "schema": SCHEMA,
        "synthetic": result.synthetic,
        "report_manifest_sha256": result.manifest_sha256,
        "code": {**code_commit(), "exporter_sha256": sha256(Path(__file__).resolve())},
        "values": {key: result.catalog[key] for key in sorted(ids)},
    }


def _write_json(path: Path, record: Mapping[str, object]) -> None:
    path.write_text(
        json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_input_arguments(parser)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--values", type=Path, required=True)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--fill", action="store_true")
    args = parser.parse_args(argv)
    result = export(parse_inputs(parser, args), args.report, args.manuscript)
    if args.fill:
        fill(args.manuscript, result.catalog)
    used = used_ids(args.manuscript)
    missing = sorted(used - result.catalog.keys())
    _write_json(args.values, values_record(result, used - set(missing)))
    if args.catalog is not None:
        _write_json(args.catalog, values_record(result, result.catalog))
    for key in missing:
        print(f"unresolved result ID: {key}", file=sys.stderr)
    print(
        f"Exported {len(result.written)} generated files; "
        f"{len(used) - len(missing)} of {len(used)} cited result IDs bound"
    )
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
