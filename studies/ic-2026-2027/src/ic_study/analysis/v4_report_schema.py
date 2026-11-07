"""Strict readers for the frozen v4 release, sealed gate records and SHP anchor.

The accepted shapes are exactly what the frozen emitters write:

- ``run_curve.py --release-at-close`` prints ``released_curves(root)``: an
  ``inventory`` from ``close_inventory`` plus the ``curve.json`` record that
  ``complete_curve`` stores for every completed unit; a cell that the amendment
  v4.4 runner sealed in place of the frozen projection error holds its
  ``gap_record`` (``successor_gap``, no attempt);
- ``run_gate.py`` appends each ``aggregate`` summary to ``criteria.jsonl`` at the
  gate root, and ``execute_task`` seals one ``result.json`` per task directory;
- ``shp_reliability.analyze_panel`` writes the aggregate SHP report, with the
  successor-1 sections when present;
- ``shp_crosswalk`` writes the exploratory synthetic crosswalk aggregate;
- a stage-summary successor record carries a complete ``aggregate`` summary
  that the frozen runner could not append (``ic-study.v4-stage-summary-
  successor.v1``), and the post-G0 second binding record fixes the G2 cells.

Unit metadata (tier, family, channel, sensitivity, r) is not part of the curve
record; it is joined from the frozen inventory by unit key. Readers never write
into a sealed store: seal digests are verified by hashing, without the access
log that ``SealedStore.get_json`` appends.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import cache
from pathlib import Path
from typing import Any, cast

import numpy as np

from ic_study.analysis.detection_boundary import boundary_report
from ic_study.analysis.shp_crosswalk import QUASI_SIMPLEX, TRAIT_WEIGHTS
from ic_study.analysis.shp_crosswalk import SCHEMA as CROSSWALK_SCHEMA
from ic_study.analysis.shp_reliability import (
    STARTS_FAILURES,
    STARTS_NUMERICAL_ERROR,
    SUCCESSOR,
)
from ic_study.analysis.v4_report_protocol import protocol
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES
from ic_study.simulation.v4_plan import CLOSE_UTC, G2_CELLS, gate_tasks, inventory

TARGET = 0.7
SECONDARY_TARGETS = protocol().secondary_targets
SMALL_LARGE_CUT = protocol().small_cut
CRITICAL_FLOOR = 2.7729
BAND_MARGIN = 1 / (2 * 2000)  # frozen band clips the point to [m, 1 - m]
CALIBRATION_EXPOSED_R = 0.7
FAMILIES = ("B", "A", "C", "D", "E")  # B is confirmatory (frozen preregistration)
NOT_STARTED = "não iniciado"
PARTIAL = "parcial por encerramento operacional"
INVALID = "completo inválido"
VALID = "completo válido"
STATUSES = (NOT_STARTED, PARTIAL, INVALID, VALID)
MAIN_CURVE_INVALID = "main curve invalid"
ACCEPTED_FIT = frozenset({"anchor-exact", "interior", "boundary"})
FAMILY_LIMITS = frozenset({"family-limit-upper", "family-limit-lower"})
SOLVER_FAILURES = frozenset(
    {
        "no-L1-root",
        "non-monotone-profile",
        "numerical-limit",
        "ill-conditioned",
        "budget",
    }
)
DEPENDENCY_GAP = "dependency-gap"
PROPAGATION = "propagation"
# Gap kinds of the final attempt; family limits are gaps, not failures (D7):
# family limit from the feasibility pre-check (0 evaluations) or on the profile,
# solver status, accepted status that failed validation, control dependency.
# Amendment v4.4 adds the propagation gap: a curve cell, never a gate fit, whose
# frozen nuisance propagation raised the recorded projection error.
GAP_KINDS = (
    "screened",
    "family_limit",
    "solver",
    "validation",
    "dependency",
    PROPAGATION,
)
GATE_STAGES = ("G0", "G1b", "G1c", "G2", "G2c")
PASS = "pass"
FAIL = "fail"
IN_PROGRESS = "in progress"
APPROVED_G1C_SHA256 = "a945e8484791f886289d51b083886854b4f540f6b26dcf1463d8d4c9dcd9a4d6"
SUCCESSOR_SCHEMA = "ic-study.v4-stage-summary-successor.v1"
SUCCESSOR_SOURCE = "successor record, frozen aggregate"
ALLOCATION_STAGE = "post-G0-pre-G2"
SHP_ANALYSIS = "SHP P$$P04 quasi-simplex; aggregate only"
CROSSWALK_REFERENCES = ("a = 0", *(f"B η = {eta:.2f}" for eta in TRAIT_WEIGHTS))

_REQUIRED = frozenset(
    {
        "unit",
        "gap_count",
        "band_complete",
        "valid_null_gate",
        "valid_curve",
        "first",
        "sustained",
        "first_interval",
        "sustained_interval",
        "cells",
        "status",
    }
)
_ESTIMATES = frozenset(
    {
        "critical",
        "empirical_exceeds_floor",
        "available_strengths",
        "auc",
        "lower",
        "upper",
    }
)
_CENSORING = tuple(
    f"{kind}{suffix}_censoring"
    for kind in ("first", "sustained")
    for suffix in ("", "_interval")
)
_OPTIONAL = _ESTIMATES | {"nonmonotone_band", "main_curve_valid", *_CENSORING}
# A cell sealed by the amendment v4.4 runner (``v44_run_curve.gap_record``): no
# attempt, and this successor_gap beside the SHA-256 of that runner.
_SUCCESSOR_CELL = frozenset({"success", "attempts", "dependency_gap", "successor_gap"})
# SHA-256 of the frozen amendment v4.4 runner (freeze-v44.json).
V44_SUCCESSOR_SHA256 = (
    "0ea2e41e6a8a9939ad59b7fbac8fc95d23ffc2b026966c388e09bd01d9c7b7b5"
)
_PROPAGATION_GAP = {
    "amendment": "v4.4",
    "kind": PROPAGATION,
    "error": "ill-conditioned local profile",
    "function": "project_shift",
}


class SchemaError(ValueError):
    """Input does not match the frozen emitter schema."""


@dataclass(frozen=True)
class UnitMeta:
    key: str
    tier: int
    family: str
    channel: str
    sensitivity: str
    r: float

    @property
    def configuration(self) -> tuple[int, str, str, str]:
        return self.tier, self.family, self.channel, self.sensitivity

    @property
    def main(self) -> bool:
        """Tier 1 (B) and tier 2 (A, C, D, E) on the main observed grid."""
        return self.tier in (1, 2)


@dataclass(frozen=True)
class Boundary:
    """One inverted boundary, exactly as ``curve_report`` recorded it."""

    point: float | None
    interval: tuple[float | None, float | None] | None
    censoring: str | None
    interval_censoring: str | None
    sustained: bool = False

    @property
    def censored_at(self) -> float | None:
        return _gap_value(self.censoring)

    def end_censored_at(self, index: int) -> float | None:
        """Gap censoring a missing interval end (0 lower, 1 upper); None: beyond 0.9.

        ``curve_report`` flags the whole interval once either end is missing. Every
        strength above the last gap is available, so when the sustained lower end
        survived censoring, a missing upper end means that the suffix minimum of the
        lower band never reaches the target: not reached, not censored at the gap.
        """
        if self.interval is None or self.interval[index] is not None:
            return None
        if self.sustained and index == 1 and self.interval[0] is not None:
            return None
        return _gap_value(self.interval_censoring)


@dataclass(frozen=True)
class CellDiagnostics:
    """Released fit and nuisance diagnostics of one cell (frozen ``pipeline_record``).

    Values that are absent or not finite are None: these fields are diagnostics,
    so they never block the registered outputs.
    """

    matching_pairs: tuple[int, ...]  # one per attempt; the retry uses more pairs
    residual_se_units: tuple[float | None, ...]  # final attempt, one per moment
    amplification: float | None  # final attempt
    nuisance_variance: float | None
    nuisance_mcse: float | None
    mean_shift: float | None
    projected_fraction: float | None


@dataclass(frozen=True)
class Curve:
    meta: UnitMeta
    status: str
    valid_null_gate: bool
    gap_count: int
    band_complete: bool
    available: tuple[float, ...]
    auc: tuple[float, ...]
    lower: tuple[float, ...]
    upper: tuple[float, ...]
    critical: float | None
    empirical_exceeds_floor: bool | None
    nonmonotone_band: bool | None
    first: Boundary
    sustained: Boundary
    cell_success: tuple[bool, ...]
    cell_final_status: tuple[str | None, ...]
    cell_gap: tuple[str | None, ...]
    main_curve_valid: bool | None
    secondary: tuple[Boundary, ...] = ()  # first boundaries at SECONDARY_TARGETS
    diagnostics: tuple[CellDiagnostics, ...] = ()  # one per strength of G

    def gap_counts(self) -> dict[str, int]:
        return {kind: self.cell_gap.count(kind) for kind in GAP_KINDS}


@dataclass(frozen=True)
class Release:
    closed_utc: str
    main_curve_valid: bool
    statuses: dict[str, str]
    curves: dict[str, Curve]

    def meta(self, key: str) -> UnitMeta:
        return unit_catalog()[key]


@dataclass(frozen=True)
class FitOutcome:
    """Final status of one G0 fit and its gap kind (None when it succeeded)."""

    status: str
    gap: str | None


@dataclass(frozen=True)
class StageSuccessor:
    """Complete stage summary that the frozen runner could not append."""

    stage: str
    summary: dict[str, Any]
    name: str
    sha256: str


@dataclass(frozen=True)
class Allocation:
    """Post-G0 second binding record: the G2 cells and the bound criteria."""

    cells: tuple[tuple[float, float], ...]
    criteria_sha256: str
    name: str
    sha256: str


@dataclass(frozen=True)
class GateRecords:
    summaries: dict[str, dict[str, Any]]
    summary_counts: dict[str, int]
    stop: dict[str, Any] | None
    g1b_critical: tuple[float, ...]
    g0_evaluations: tuple[int, ...]
    g0_fits: tuple[FitOutcome, ...]
    task_digests: tuple[tuple[str, str], ...]
    criteria_sha256: str | None
    sealed: dict[str, int]  # task directories holding a result, per stage
    planned: dict[str, int]
    authorized: frozenset[str] = frozenset()
    successors: tuple[StageSuccessor, ...] = ()
    from_successor: frozenset[str] = frozenset()
    g2_cells: tuple[tuple[float, float], ...] | None = None

    def started(self, stage: str) -> bool:
        return (
            stage in self.summaries
            or stage in self.authorized
            or self.sealed.get(stage, 0) > 0
        )

    def progress(self, stage: str) -> tuple[int, int] | None:
        """Completed and planned tasks; sealed records stand in before any line."""
        summary = self.summaries.get(stage)
        if summary is not None:
            return int(summary["completed"]), int(summary["planned"])
        if self.started(stage):
            return self.sealed.get(stage, 0), self.planned[stage]
        return None

    def verdict(self, stage: str) -> str | None:
        """Pass or fail once complete, in progress before; None if never started."""
        progress = self.progress(stage)
        if progress is None:
            return None
        summary = self.summaries.get(stage)
        if summary is None or progress[0] < progress[1]:
            return IN_PROGRESS
        if stage == "G1c":
            _validate_g1c(summary)
        return PASS if summary["pass"] else FAIL


@dataclass(frozen=True)
class StartsSensitivity:
    """Successor-1 trait-state-error sensitivity: a point only when admissible."""

    year: int | None
    estimate: float | None
    standard_error: float | None
    wald_95_interval: tuple[float, float] | None
    failure_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ShpAnchor:
    year: int
    estimate: float
    standard_error: float
    wald_95_interval: tuple[float, float]
    sensitivity_envelope: tuple[float, float]
    starts: StartsSensitivity | None = None


@dataclass(frozen=True)
class CrosswalkRange:
    """Replicate range of the quasi-simplex r at wave 5 in one reference cell."""

    reference: str
    r: float
    low: float | None
    high: float | None
    values: int
    failures: int


@dataclass(frozen=True)
class Crosswalk:
    declared_plan: bool
    replicates: int
    ranges: tuple[CrosswalkRange, ...]

    @property
    def missing(self) -> int:
        return len(CROSSWALK_REFERENCES) * len(RELIABILITIES) - len(self.ranges)

    def containing(self, estimate: float) -> dict[str, tuple[float, ...]]:
        """Grid r whose replicate range contains the SHP estimate, per reference."""
        return {
            reference: tuple(
                item.r
                for item in self.ranges
                if item.reference == reference
                and item.low is not None
                and item.high is not None
                and item.low <= estimate <= item.high
            )
            for reference in CROSSWALK_REFERENCES
        }


@cache
def unit_catalog() -> dict[str, UnitMeta]:
    """Frozen inventory, one entry per (configuration, r) unit, in frozen order."""
    catalog: dict[str, UnitMeta] = {}
    for row in inventory():
        key = str(row["unit"])
        if key not in catalog:
            catalog[key] = UnitMeta(
                key,
                int(cast(int, row["tier"])),
                str(row["family"]),
                str(row["channel"]),
                str(row["sensitivity"]),
                float(cast(float, row["r"])),
            )
    return catalog


def grid_index(value: float) -> int:
    return GRID.index(value)


def _gap_value(censoring: str | None) -> float | None:
    if censoring is None:
        return None
    return float(censoring.removeprefix("gap at a="))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SchemaError(message)


def _bool(value: object, name: str) -> bool:
    _require(isinstance(value, bool), f"{name} must be boolean")
    return cast(bool, value)


def _int(value: object, name: str) -> int:
    _require(
        isinstance(value, int) and not isinstance(value, bool), f"{name} not integer"
    )
    return cast(int, value)


def _float(
    value: object, name: str, lo: float = -math.inf, hi: float = math.inf
) -> float:
    _require(
        isinstance(value, (int, float)) and not isinstance(value, bool),
        f"{name} must be a number",
    )
    number = float(cast(float, value))
    _require(math.isfinite(number) and lo <= number <= hi, f"{name} out of range")
    return number


def _dict(value: object, name: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{name} must be an object")
    return cast(dict[str, Any], value)


def _list(value: object, name: str) -> list[Any]:
    _require(isinstance(value, list), f"{name} must be a list")
    return cast(list[Any], value)


def _strength(value: object, name: str) -> float | None:
    if value is None:
        return None
    number = _float(value, name)
    _require(number in GRID, f"{name} is not a frozen grid strength")
    return number


def _interval(value: object, name: str) -> tuple[float | None, float | None] | None:
    if value is None:
        return None
    items = _list(value, name)
    _require(len(items) == 2, f"{name} must have two endpoints")
    lo, hi = _strength(items[0], name), _strength(items[1], name)
    _require(lo is None or hi is None or lo <= hi, f"{name} endpoints reversed")
    return lo, hi


def _vector(value: object, name: str, size: int) -> tuple[float, ...]:
    items = _list(value, name)
    _require(len(items) == size, f"{name} not aligned with available strengths")
    return tuple(_float(item, name, 0, 1) for item in items)


def _censoring(record: Mapping[str, Any], key: str) -> str | None:
    value = record.get(key)
    if value is None:
        _require(key not in record, f"{key} cannot be null")
        return None
    _require(
        isinstance(value, str)
        and re.fullmatch(r"gap at a=[0-9.e-]+", value) is not None,
        f"{key} has an unknown form",
    )
    return cast(str, value)


def _expected_boundaries(
    available: Sequence[float],
    auc: Sequence[float],
    lower: Sequence[float],
    upper: Sequence[float],
    success: Sequence[bool],
    target: float = TARGET,
) -> dict[str, object]:
    """Replay the inversion and gap censoring of the frozen ``curve_report``."""
    keys = ("first", "sustained", "first_interval", "sustained_interval")
    if not available:  # complete_curve skips curve_report without estimates
        return dict.fromkeys(keys)
    if available[0] == 0:
        report = boundary_report(
            np.array(available),
            np.array(auc),
            np.array(lower),
            np.array(upper),
            target=target,
        )
    else:
        report = {**dict.fromkeys(keys), "nonmonotone_band": False}
    gaps = [a for a, ok in zip(GRID, success, strict=True) if not ok]
    if gaps:

        def allowed(value: object, kind: str, limit: float) -> bool:
            return isinstance(value, (float, int)) and (
                value < limit if kind == "first" else value > limit
            )

        for kind, limit in (("first", gaps[0]), ("sustained", gaps[-1])):
            if not allowed(report[kind], kind, limit):
                report[kind] = None
                report[f"{kind}_censoring"] = f"gap at a={limit:g}"
            bounds = report[f"{kind}_interval"]
            if isinstance(bounds, tuple):
                kept = tuple(v if allowed(v, kind, limit) else None for v in bounds)
                report[f"{kind}_interval"] = kept
                if None in kept:
                    report[f"{kind}_interval_censoring"] = f"gap at a={limit:g}"
    for key in ("first_interval", "sustained_interval"):
        if isinstance(report[key], tuple):
            report[key] = list(cast(tuple[object, ...], report[key]))
    return report


def _diagnostic(value: object) -> float | None:
    """A finite released number, else None; a list holds one value per draw set."""
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def cell_diagnostics(
    cell: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]]
) -> CellDiagnostics:
    final = attempts[-1] if attempts else {}
    residuals = final.get("residual_se_units")
    return CellDiagnostics(
        tuple(
            a["matching_pairs"]
            for a in attempts
            if isinstance(a.get("matching_pairs"), int)
        ),
        tuple(_diagnostic(v) for v in residuals) if isinstance(residuals, list) else (),
        _diagnostic(final.get("amplification")),
        _diagnostic(cell.get("nuisance_variance")),
        _diagnostic(cell.get("nuisance_mcse")),
        _diagnostic(cell.get("mean_shift")),
        _diagnostic(cell.get("projected_fraction")),
    )


def _propagation_gap(gap: Mapping[str, Any]) -> None:
    """Accept only the amendment v4.4 record of the frozen projection error."""
    _require(
        set(gap) == {*_PROPAGATION_GAP, "successor_sha256"},
        "successor_gap fields differ from the amendment v4.4 record",
    )
    for key, value in _PROPAGATION_GAP.items():
        _require(gap[key] == value, f"successor_gap {key} differs from amendment v4.4")
    digest = gap["successor_sha256"]
    _require(
        isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
        "successor_gap successor_sha256 must be a SHA-256 digest",
    )
    _require(
        digest == V44_SUCCESSOR_SHA256,
        "successor_gap was not written by the frozen amendment v4.4 runner",
    )


def _successor_gap(cell: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """The amendment v4.4 record of a cell, which then holds nothing else."""
    if "successor_gap" not in cell:
        return None
    _require(
        set(cell) == _SUCCESSOR_CELL,
        "an amendment v4.4 gap cell holds exactly success, attempts, dependency_gap "
        "and successor_gap",
    )
    return _dict(cell["successor_gap"], "successor_gap")


def gap_kind(
    success: bool,
    attempts: Sequence[Mapping[str, Any]],
    dependency_gap: bool,
    successor_gap: Mapping[str, Any] | None = None,
) -> str | None:
    """Gap kind of one unsuccessful fit, from its final attempt; None if it succeeded.

    A family limit found by the feasibility pre-check stops before any solver
    evaluation (``fit_cell``), so zero evaluations separate it from a limit met
    along the profile. A control whose observed fit failed is a dependency gap.
    A cell sealed by the amendment v4.4 runner has no attempt: its
    ``successor_gap`` records the projection error that ended the frozen worker.
    """
    if successor_gap is not None:
        _require(
            not success and not attempts and not dependency_gap,
            "an amendment v4.4 gap is a failed cell with no attempt or dependency gap",
        )
        _propagation_gap(successor_gap)
        return PROPAGATION
    if success:
        return None
    if dependency_gap:
        return "dependency"
    _require(bool(attempts), "a failed fit without attempts must be a dependency gap")
    final = attempts[-1]
    status = final.get("status")
    evaluations = _int(final.get("evaluations"), "evaluations")
    if status in FAMILY_LIMITS:
        return "screened" if evaluations == 0 else "family_limit"
    if status in ACCEPTED_FIT:
        return "validation"
    _require(status in SOLVER_FAILURES, f"unknown final solver status {status!r}")
    return "solver"


def _first_boundary(report: Mapping[str, object]) -> Boundary:
    return Boundary(
        _strength(report["first"], "first"),
        _interval(report["first_interval"], "first_interval"),
        cast(str | None, report.get("first_censoring")),
        cast(str | None, report.get("first_interval_censoring")),
    )


def band_contains_point(lower: float, point: float, upper: float) -> bool:
    """Whether a released band holds its point AUC as the frozen ``band`` builds it.

    The frozen band surrounds the point clipped to ``BAND_MARGIN`` from 0 and 1,
    and sets its upper end to 1 at a point of exactly 1 (its lower end to 0 at
    exactly 0). A point within the margin of 1 can therefore lie slightly above
    the upper end, and symmetrically near 0.
    """
    centre = min(max(point, BAND_MARGIN), 1 - BAND_MARGIN)
    return lower <= centre <= upper and (0 < point < 1 or lower <= point <= upper)


def parse_curve(record: object, meta: UnitMeta) -> Curve:
    data = _dict(record, "curve")
    keys = set(data)
    _require(keys >= _REQUIRED, f"curve {meta.key} misses {sorted(_REQUIRED - keys)}")
    _require(
        keys <= _REQUIRED | _OPTIONAL,
        f"curve {meta.key} has unknown fields {sorted(keys - _REQUIRED - _OPTIONAL)}",
    )
    cells = _list(data["cells"], "cells")
    _require(len(cells) == len(GRID), "cells must cover the nine frozen strengths")
    success: list[bool] = []
    final: list[str | None] = []
    kinds: list[str | None] = []
    diagnostics: list[CellDiagnostics] = []
    for cell in cells:
        item = _dict(cell, "cell")
        ok = _bool(item.get("success"), "cell success")
        attempts = [
            _dict(a, "attempt") for a in _list(item.get("attempts"), "cell attempts")
        ]
        dependency = _bool(item.get("dependency_gap", False), "dependency_gap")
        successor = _successor_gap(item)
        success.append(ok)
        final.append(str(attempts[-1].get("status")) if attempts else None)
        kinds.append(gap_kind(ok, attempts, dependency, successor))
        diagnostics.append(cell_diagnostics(item, attempts))
    gap_count = _int(data["gap_count"], "gap_count")
    _require(gap_count == success.count(False), "gap_count disagrees with cells")
    band_complete = _bool(data["band_complete"], "band_complete")
    _require(band_complete == (gap_count == 0), "band_complete disagrees with gaps")
    available = tuple(a for a, ok in zip(GRID, success, strict=True) if ok)
    has_estimates = bool(available)
    present = _ESTIMATES & keys
    _require(
        present == (_ESTIMATES if has_estimates else frozenset()),
        "estimate fields must be present exactly when a cell succeeded",
    )
    auc: tuple[float, ...] = ()
    lower: tuple[float, ...] = ()
    upper: tuple[float, ...] = ()
    critical: float | None = None
    exceeds: bool | None = None
    if has_estimates:
        listed = tuple(
            _float(v, "available_strengths")
            for v in _list(data["available_strengths"], "available_strengths")
        )
        _require(listed == available, "available_strengths disagrees with cells")
        auc = _vector(data["auc"], "auc", len(available))
        lower = _vector(data["lower"], "lower", len(available))
        upper = _vector(data["upper"], "upper", len(available))
        _require(
            all(
                band_contains_point(lo, p, hi)
                for lo, p, hi in zip(lower, auc, upper, strict=True)
            ),
            "band must contain point AUC",
        )
        critical = _float(data["critical"], "critical", CRITICAL_FLOOR)
        exceeds = _bool(data["empirical_exceeds_floor"], "empirical_exceeds_floor")
        _require(
            exceeds == (critical > CRITICAL_FLOOR), "critical and floor flag disagree"
        )
    nonmonotone: bool | None = None
    if "nonmonotone_band" in data:
        nonmonotone = _bool(data["nonmonotone_band"], "nonmonotone_band")
    _require(
        ("nonmonotone_band" in data) == has_estimates,
        "nonmonotone_band present exactly when estimates are",
    )
    gate = _bool(data["valid_null_gate"], "valid_null_gate")
    expected_gate = bool(
        available and available[0] == 0 and lower[0] <= 0.5 <= upper[0]
    )
    _require(gate == expected_gate, "valid_null_gate disagrees with the a=0 band")
    _require(_bool(data["valid_curve"], "valid_curve") == gate, "valid_curve != gate")
    status = data["status"]
    _require(status == (VALID if gate else INVALID), "status disagrees with gate")
    first = Boundary(
        _strength(data["first"], "first"),
        _interval(data["first_interval"], "first_interval"),
        _censoring(data, "first_censoring"),
        _censoring(data, "first_interval_censoring"),
    )
    sustained = Boundary(
        _strength(data["sustained"], "sustained"),
        _interval(data["sustained_interval"], "sustained_interval"),
        _censoring(data, "sustained_censoring"),
        _censoring(data, "sustained_interval_censoring"),
        sustained=True,
    )
    expected = _expected_boundaries(available, auc, lower, upper, success)
    for key in (
        "first",
        "sustained",
        "first_interval",
        "sustained_interval",
        *_CENSORING,
    ):
        _require(
            data.get(key) == expected.get(key),
            f"{key} of {meta.key} disagrees with frozen inversion and censoring",
        )
    if has_estimates:
        _require(nonmonotone == expected["nonmonotone_band"], "nonmonotone_band")
    main_valid: bool | None = None
    if "main_curve_valid" in data:
        main_valid = _bool(data["main_curve_valid"], "main_curve_valid")
        _require(meta.tier == 1 and main_valid is False, "main_curve_valid misplaced")
    return Curve(
        meta,
        cast(str, status),
        gate,
        gap_count,
        band_complete,
        available,
        auc,
        lower,
        upper,
        critical,
        exceeds,
        nonmonotone,
        first,
        sustained,
        tuple(success),
        tuple(final),
        tuple(kinds),
        main_valid,
        tuple(
            _first_boundary(
                _expected_boundaries(available, auc, lower, upper, success, target)
            )
            for target in SECONDARY_TARGETS
        ),
        tuple(diagnostics),
    )


def parse_release(data: object) -> Release:
    top = _dict(data, "release")
    _require(set(top) == {"inventory", "curves"}, "release needs inventory and curves")
    closed = _dict(top["inventory"], "inventory")
    _require(
        set(closed) == {"closed_utc", "units", "main_curve_valid"},
        "inventory fields differ from close_inventory",
    )
    _require(closed["closed_utc"] == CLOSE_UTC, "closed_utc differs from frozen close")
    catalog = unit_catalog()
    rows = _list(closed["units"], "inventory units")
    _require(len(rows) == len(catalog), "inventory is not the full frozen inventory")
    statuses: dict[str, str] = {}
    for row, meta in zip(rows, catalog.values(), strict=True):
        item = _dict(row, "inventory row")
        _require(set(item) == {"unit", "tier", "status"}, "inventory row fields")
        _require(
            item["unit"] == meta.key and item["tier"] == meta.tier,
            "inventory order or tier differs from the frozen inventory",
        )
        _require(item["status"] in STATUSES, f"unknown D9 status {item['status']!r}")
        statuses[meta.key] = cast(str, item["status"])
    main_valid = _bool(closed["main_curve_valid"], "main_curve_valid")
    _require(
        main_valid
        == all(statuses[k] == VALID for k, m in catalog.items() if m.tier == 1),
        "main_curve_valid disagrees with tier-1 statuses",
    )
    curves: dict[str, Curve] = {}
    for record in _list(top["curves"], "curves"):
        key = _dict(record, "curve").get("unit")
        _require(isinstance(key, str) and key in catalog, "curve for unknown unit")
        key = cast(str, key)
        _require(key not in curves, f"duplicate curve {key}")
        curve = parse_curve(record, catalog[key])
        _require(curve.status == statuses[key], f"{key} status differs from inventory")
        _require(
            (curve.main_curve_valid is False)
            == (curve.meta.tier == 1 and not main_valid),
            "tier-1 curve must carry main_curve_valid=false exactly when invalid",
        )
        curves[key] = curve
    completed = {k for k, s in statuses.items() if s in (VALID, INVALID)}
    _require(set(curves) == completed, "completed units and released curves differ")
    return Release(CLOSE_UTC, main_valid, statuses, curves)


@dataclass(frozen=True)
class ReleaseRecord:
    name: str
    sha256: str
    condition: str
    released_utc: str
    curves_sha256: str


def load_release_record(path: Path, content: bytes, release: Release) -> ReleaseRecord:
    _require(path.is_file(), "Released curves require release-record.json")
    raw = path.read_bytes()
    data = _dict(json.loads(raw), "release record")
    _require(
        type(data.get("schema")) is int and data["schema"] == 1,
        "Not a v4 release record",
    )
    digest = hashlib.sha256(content).hexdigest()
    _require(
        data.get("released_curves_sha256") == digest,
        "Release record SHA-256 differs from received curve bytes",
    )
    stamp = data.get("released_utc")
    _require(
        isinstance(stamp, str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", stamp) is not None,
        "Release time must be a real UTC timestamp",
    )
    try:
        actual = datetime.fromisoformat(cast(str, stamp))
    except ValueError as error:
        raise SchemaError("Release time must be a real UTC timestamp") from error
    _require(actual.tzinfo == UTC, "Release time must be UTC")
    close = datetime.fromisoformat(CLOSE_UTC)
    condition = data.get("condition")
    _require(
        condition in {"inventory-complete", "declared-close"},
        "Unknown release condition",
    )
    if condition == "inventory-complete":
        _require(actual < close, "Inventory completion release must precede the close")
        _require(
            len(release.curves) == len(unit_catalog())
            and all(status in {VALID, INVALID} for status in release.statuses.values()),
            "Early release requires all 414 completed curves",
        )
    else:
        _require(actual >= close, "Declared-close release precedes the nominal close")
    _require(
        data.get("amendment")
        == {
            "path": "studies/ic-2026-2027/research/questions/exploration/"
            "2026-09-24-parallel/detection-boundary-v4-release-amendment.md",
            "commit": "428ca7cd6158244b494dcb520b9a69738b5bfae6",
        },
        "Release record names another amendment",
    )
    _require(
        isinstance(data.get("script_sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", data["script_sha256"]) is not None,
        "Release record needs the script SHA-256",
    )
    return ReleaseRecord(
        path.name,
        hashlib.sha256(raw).hexdigest(),
        cast(str, condition),
        cast(str, stamp),
        digest,
    )


def load_release(path: Path) -> Release:
    """Read the single JSON document printed at close by ``run_curve.py``."""
    return parse_release(json.loads(path.read_text(encoding="utf-8")))


def _sealed_json(path: Path) -> dict[str, Any] | None:
    """Read one sealed JSON record, verifying the directory seal read-only."""
    if not path.exists():
        return None
    _require(not path.is_symlink(), "symlink inside sealed store")
    content = path.read_bytes()
    seal = path.parent / "seal.json"
    if seal.exists():
        files = _dict(json.loads(seal.read_bytes()).get("files"), "seal files")
        _require(
            files.get(path.name) == hashlib.sha256(content).hexdigest(),
            f"sealed digest mismatch for {path.parent.name}/{path.name}",
        )
    return _dict(json.loads(content), path.name)


_SUMMARY_KEYS: dict[str, frozenset[str]] = {
    "G0": frozenset(
        {
            "matching_mask",
            "statuses",
            "fits",
            "anchor_failures",
            "implementation_statuses",
            "budget_statuses",
        }
    ),
    "G1b": frozenset({"coverage_counts", "empirical_exceeds_floor_count"}),
    "G1c": frozenset({"pointwise_failures", "anchor_count", "mean_z", "tie_rate"}),
    "G2": frozenset(
        {
            "complete",
            "denominator",
            "cell_failure_counts",
            "successful_pair_counts",
            "failure_allowance_met",
            "cell_ratios",
            "cell_lower",
            "cell_upper",
            "pooled_ratio",
            "pooled_lower",
            "pooled_upper",
            "loo_tail_counts",
            "loo_z_mean",
            "fd_ratio_median_by_cell",
            "fd_stable",
            "covariance_flag_counts",
        }
    ),
    "G2c": frozenset({"comparisons"}),
}
_BASE_KEYS = frozenset({"gate", "planned", "completed", "failures", "pass"})


def _validate_g1c(data: Mapping[str, Any]) -> None:
    _bool(data["pass"], "G1c pass")
    p = protocol()
    evaluated = data["completed"] == data["planned"] and data["failures"] == 0
    fields = _SUMMARY_KEYS["G1c"]
    if not evaluated:
        _require(
            not data["pass"] and not fields.intersection(data),
            "G1c incomplete or failed summary contradicts "
            "the frozen predicate/early exit",
        )
        return
    _require(fields <= data.keys(), "G1c summary misses frozen predicate fields")
    anchors = _int(data["anchor_count"], "anchor_count")
    pointwise = _int(data["pointwise_failures"], "pointwise_failures")
    _require(
        0 <= anchors <= p.g1c_fits and 0 <= pointwise <= p.g1c_fits,
        "G1c counts outside the frozen predicate domain",
    )
    mean_z = _float(data["mean_z"], "mean_z", 0)
    _float(data["tie_rate"], "tie_rate", 0, 1)
    passed = (
        anchors == p.g1c_fits
        and pointwise <= p.g1c_pointwise_limit
        and mean_z <= p.g1c_mean_z_limit
    )
    _require(
        data["pass"] == passed, "G1c pass differs from the frozen aggregate predicate"
    )


def parse_summary(record: object) -> dict[str, Any]:
    data = _dict(record, "criteria record")
    gate = data.get("gate")
    _require(gate in GATE_STAGES, f"unknown gate stage {gate!r}")
    keys = set(data)
    _require(keys >= _BASE_KEYS, f"{gate} summary misses base fields")
    _require(
        keys <= _BASE_KEYS | _SUMMARY_KEYS[cast(str, gate)],
        f"{gate} summary has unknown fields {sorted(keys - _BASE_KEYS)}",
    )
    planned = _int(data["planned"], "planned")
    completed = _int(data["completed"], "completed")
    _int(data["failures"], "failures")
    _bool(data["pass"], "pass")
    _require(0 <= completed <= planned, "completed exceeds planned")
    if gate != "G2":
        _require(planned == len(gate_tasks(cast(str, gate))), "planned differs")
    if gate == "G1c":
        _validate_g1c(data)
    return data


def _plain_json(path: Path) -> dict[str, Any] | None:
    """Read an unsealed root-level record (stage authorization) without writing."""
    if not path.exists():
        return None
    _require(not path.is_symlink(), "symlink inside sealed store")
    return _dict(json.loads(path.read_bytes()), path.name)


def _parse_stop(record: dict[str, Any]) -> dict[str, Any]:
    """The economy-rule record ``run_gate`` appends when G0 blocks G2."""
    _require(
        record.get("stopped_before_G2") is True
        and record.get("pass") is False
        and set(record) == {"pass", "stopped_before_G2", "g0_gap_binding"},
        "unknown criteria record",
    )
    binding = _dict(record["g0_gap_binding"], "g0_gap_binding")
    _float(binding.get("pass_probability"), "pass_probability", 0, 1)
    _float(binding.get("minimum"), "minimum", 0, 1)
    _int(binding.get("gaps"), "gaps")
    _int(binding.get("denominator"), "denominator")
    return record


_SUCCESSOR_REQUIRED = frozenset(
    {"schema", "stage", "reason", "freeze_sha256", "sealed_root_identifier", "summary"}
)
_SUCCESSOR_OPTIONAL = frozenset(
    {
        "computed_at_utc",
        "conversion",
        "frozen_code_location",
        "pass_type_in_frozen_output",
    }
)


def load_successor(
    path: Path,
    root: Path,
    authorizations: Mapping[str, Mapping[str, Any]],
    *,
    synthetic: bool = False,
) -> StageSuccessor:
    """Validate a stage-summary successor record against the gate root it names."""
    content = path.read_bytes()
    data = _dict(json.loads(content), "stage successor")
    _require(data.get("schema") == SUCCESSOR_SCHEMA, "not a v4 stage-summary successor")
    keys = set(data)
    _require(
        _SUCCESSOR_REQUIRED <= keys <= _SUCCESSOR_REQUIRED | _SUCCESSOR_OPTIONAL,
        "successor record fields differ from the documented schema",
    )
    stage = data["stage"]
    _require(stage in GATE_STAGES, f"successor for unknown stage {stage!r}")
    reason = data["reason"]
    _require(
        isinstance(reason, str) and bool(reason.strip()), "successor needs a reason"
    )
    summary = parse_summary(data["summary"])
    _require(summary["gate"] == stage, "successor summary is for another stage")
    _require(
        summary["completed"] == summary["planned"], "successor summary is incomplete"
    )
    _require(
        data["sealed_root_identifier"] == root.resolve().name,
        "successor record names another sealed gate root",
    )
    authorization = authorizations.get(cast(str, stage))
    _require(
        authorization is not None
        and data["freeze_sha256"] == authorization.get("freeze_sha256"),
        "successor freeze differs from the gate root's stage authorization",
    )
    if stage == "G1c" and not synthetic:
        _require(
            hashlib.sha256(content).hexdigest() == APPROVED_G1C_SHA256,
            "G1c successor differs from the independently approved owner digest",
        )
    return StageSuccessor(
        cast(str, stage), summary, path.name, hashlib.sha256(content).hexdigest()
    )


_ALLOCATION_KEYS = frozenset(
    {
        "schema",
        "stage",
        "freeze_sha256",
        "criteria_sha256",
        "g0_statuses_sha256",
        "g0_gap_binding",
        "g2_cells",
    }
)


def load_allocation(path: Path) -> Allocation:
    """Read the post-G0 second binding record that ``allocation_preflight`` accepts."""
    content = path.read_bytes()
    data = _dict(json.loads(content), "second binding")
    _require(
        set(data) == _ALLOCATION_KEYS
        and data["schema"] == 1
        and data["stage"] == ALLOCATION_STAGE,
        "not the post-G0 second binding record",
    )
    digest = data["criteria_sha256"]
    _require(
        isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
        "criteria_sha256 must be a SHA-256 digest",
    )
    cells: list[tuple[float, float]] = []
    for item in _list(data["g2_cells"], "g2_cells"):
        pair = _list(item, "G2 cell")
        _require(len(pair) == 2, "a G2 cell is (a, r)")
        a, r = _float(pair[0], "G2 cell a"), _float(pair[1], "G2 cell r")
        _require(a in GRID and r in RELIABILITIES, "G2 cell off the frozen grid")
        cells.append((a, r))
    _require(bool(cells) and len(set(cells)) == len(cells), "G2 cells must be distinct")
    return Allocation(
        tuple(cells), cast(str, digest), path.name, hashlib.sha256(content).hexdigest()
    )


def check_criteria_binding(allocation: Allocation, criteria: Path) -> None:
    """Refuse a criteria file other than the one the second binding bound."""
    _require(
        hashlib.sha256(criteria.read_bytes()).hexdigest() == allocation.criteria_sha256,
        f"{criteria.name} is not the criteria bound by {allocation.name}",
    )


def _fit_outcome(fit: object) -> FitOutcome:
    record = _dict(fit, "G0 fit")
    attempts = [_dict(a, "attempt") for a in _list(record.get("attempts"), "attempts")]
    dependency = _bool(record.get("dependency_gap", False), "dependency_gap")
    ok = _bool(record.get("success"), "G0 fit success")
    status = str(attempts[-1].get("status")) if attempts else DEPENDENCY_GAP
    return FitOutcome(status, gap_kind(ok, attempts, dependency))


def load_gate(
    root: Path,
    *,
    successors: Sequence[Path] = (),
    allocation: Allocation | None = None,
    synthetic: bool = False,
) -> GateRecords:
    """Read aggregate summaries and the public task fields of a sealed gate root.

    Each stage reports the criteria line with the most completed tasks; the
    frozen runner appends one line per shard, so mid-run snapshots carry
    ``pass: false``. A successor record supplies a stage only when no line is
    complete. G2 authorized under a second binding needs that record, which fixes
    its cells and criteria. Task directories are only tested for a result; nothing
    is locked.
    """
    _require(root.is_dir(), "gate root is not a directory")
    cells = G2_CELLS if allocation is None else allocation.cells
    authorizations = {
        stage: record
        for stage in GATE_STAGES
        if (record := _plain_json(root / f"authorization-{stage}.json")) is not None
    }
    g2_authorization = authorizations.get("G2")
    if g2_authorization is not None:
        binding = g2_authorization.get("binding_sha256")
        if allocation is None:
            _require(
                binding == g2_authorization.get("freeze_sha256"),
                "G2 ran under a second binding record; pass it (--allocation)",
            )
        else:
            _require(
                binding == allocation.sha256,
                f"{allocation.name} is not the binding that authorized G2 here",
            )
    tasks = {stage: gate_tasks(stage, cells=cells) for stage in GATE_STAGES}
    planned = {stage: len(items) for stage, items in tasks.items()}
    sealed = {
        stage: sum((root / task.key / "result.json").exists() for task in items)
        for stage, items in tasks.items()
    }
    criteria = root / "criteria.jsonl"
    summaries: dict[str, dict[str, Any]] = {}
    counts: dict[str, int] = {}
    stop: dict[str, Any] | None = None
    criteria_sha: str | None = None
    if criteria.exists():
        content = criteria.read_bytes()
        criteria_sha = hashlib.sha256(content).hexdigest()
        for line in content.decode("utf-8").splitlines():
            record = _dict(json.loads(line), "criteria line")
            if "gate" not in record:
                stop = _parse_stop(record)
                continue
            summary = parse_summary(record)
            gate = cast(str, summary["gate"])
            counts[gate] = counts.get(gate, 0) + 1
            best = summaries.get(gate)
            if best is None or summary["completed"] >= best["completed"]:
                summaries[gate] = summary
    loaded = tuple(
        load_successor(path, root, authorizations, synthetic=synthetic)
        for path in successors
    )
    _require(
        len({item.stage for item in loaded}) == len(loaded),
        "at most one successor record per stage",
    )
    used: set[str] = set()
    for item in loaded:
        current = summaries.get(item.stage)
        if current is not None and current["completed"] == current["planned"]:
            continue  # a complete sealed line takes precedence over the successor
        _require(
            sealed[item.stage] == item.summary["completed"],
            f"{item.name} disagrees with the sealed {item.stage} task records",
        )
        summaries[item.stage] = item.summary
        used.add(item.stage)
    g2 = summaries.get("G2")
    if allocation is not None and g2 is not None:
        _require(g2["planned"] == planned["G2"], "G2 plan differs from the allocation")
        _require(
            len(g2.get("cell_failure_counts", cells)) == len(cells),
            "G2 cells differ from the allocation",
        )
    critical: list[float] = []
    evaluations: list[int] = []
    fits: list[FitOutcome] = []
    digests: list[tuple[str, str]] = []

    def results(stage: str) -> Iterable[tuple[str, dict[str, Any]]]:
        for task in tasks[stage]:
            path = root / task.key / "result.json"
            record = _sealed_json(path)
            if record is not None:
                digests.append(
                    (
                        f"{task.key}/result.json",
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
                )
                yield task.key, record

    for _, record in results("G0"):
        for fit in _list(record.get("fits"), "G0 fits"):
            attempts = _list(_dict(fit, "G0 fit").get("attempts"), "G0 attempts")
            for attempt in attempts:
                evaluations.append(
                    _int(_dict(attempt, "attempt")["evaluations"], "evals")
                )
            fits.append(_fit_outcome(fit))
    for _, record in results("G1b"):
        _require(
            set(record)
            == {"success", "covered", "critical", "empirical_exceeds_floor"},
            "G1b task record fields differ from run_task",
        )
        critical.append(_float(record["critical"], "G1b critical", CRITICAL_FLOOR))
    return GateRecords(
        summaries,
        counts,
        stop,
        tuple(critical),
        tuple(evaluations),
        tuple(fits),
        tuple(digests),
        criteria_sha,
        sealed,
        planned,
        frozenset(authorizations),
        loaded,
        frozenset(used),
        None if allocation is None else allocation.cells,
    )


def load_thresholds(path: Path) -> dict[str, float]:
    """G2 dispersion thresholds from the frozen criteria artifact."""
    data = _dict(json.loads(path.read_text(encoding="utf-8")), "criteria")
    thresholds = _dict(data.get("thresholds"), "thresholds")
    names = ("cell_lower", "cell_upper", "pooled_lower", "pooled_upper")
    _require(set(thresholds) == set(names), "threshold fields differ")
    return {name: _float(thresholds[name], name, 0) for name in names}


def _wald_anchor(
    value: object, name: str
) -> tuple[int, float, float, tuple[float, float]]:
    anchor = _dict(value, name)
    _require(
        set(anchor) == {"year", "estimate", "standard_error", "wald_95_interval"},
        f"{name} fields differ from shp_reliability",
    )
    estimate = _float(anchor["estimate"], "estimate", 0, 1)
    se = _float(anchor["standard_error"], "standard_error", 0)
    wald = _list(anchor["wald_95_interval"], "wald_95_interval")
    _require(len(wald) == 2, "Wald interval needs two endpoints")
    lo, hi = (_float(v, "wald_95_interval", 0, 1) for v in wald)
    _require(
        math.isclose(lo, max(0, estimate - 1.96 * se), abs_tol=1e-12)
        and math.isclose(hi, min(1, estimate + 1.96 * se), abs_tol=1e-12),
        f"{name} Wald interval is not the frozen estimate ± 1.96 SE",
    )
    return _int(anchor["year"], "year"), estimate, se, (lo, hi)


def _parse_starts(value: object) -> StartsSensitivity:
    record = _dict(value, "starts_sensitivity")
    if record.get("status") == "failed":
        reasons = tuple(_list(record.get("reasons"), "STARTS failure reasons"))
        known = (*STARTS_FAILURES, STARTS_NUMERICAL_ERROR)
        _require(
            bool(reasons) and all(reason in known for reason in reasons),
            "STARTS failure needs declared reasons",
        )
        _require("anchor" not in record, "a failed STARTS fit carries no estimate")
        return StartsSensitivity(None, None, None, None, cast(tuple[str, ...], reasons))
    _require(record.get("status") == "admissible", "unknown STARTS status")
    year, estimate, se, wald = _wald_anchor(record.get("anchor"), "STARTS anchor")
    return StartsSensitivity(year, estimate, se, wald)


def parse_shp(data: object) -> ShpAnchor:
    report = _dict(data, "SHP report")
    _require(report.get("analysis") == SHP_ANALYSIS, "not an SHP aggregate report")
    year, estimate, se, (lo, hi) = _wald_anchor(report.get("anchor"), "anchor")
    envelope = _list(report.get("sensitivity_envelope"), "sensitivity_envelope")
    _require(len(envelope) == 2, "envelope needs two endpoints")
    env_lo, env_hi = (_float(v, "sensitivity_envelope") for v in envelope)
    _require(env_lo <= env_hi, "envelope reversed")
    starts = None
    if "successor_1" in report:
        successor = _dict(report["successor_1"], "successor_1")
        _require(successor.get("specification") == SUCCESSOR, "unknown SHP successor")
        starts = _parse_starts(successor.get("starts_sensitivity"))
        _require(
            starts.year in (None, year), "STARTS and primary anchors differ in year"
        )
    return ShpAnchor(year, estimate, se, (lo, hi), (env_lo, env_hi), starts)


def load_shp(path: Path) -> ShpAnchor:
    return parse_shp(json.loads(path.read_text(encoding="utf-8")))


def _crosswalk_range(
    item: object, replicates: int
) -> tuple[CrosswalkRange | None, tuple[str, float]]:
    cell = _dict(item, "crosswalk cell")
    r = _float(cell.get("r"), "crosswalk r")
    _require(r in RELIABILITIES, "crosswalk r is not a frozen grid reliability")
    if cell.get("family") == "interaction":
        a = _float(cell.get("a"), "crosswalk a")
        _require(a in GRID and cell.get("eta") is None, "crosswalk a off the grid")
        key = f"a = {a:g}"
    else:
        eta = _float(cell.get("eta"), "crosswalk eta")
        _require(
            cell.get("family") == "B" and eta in TRAIT_WEIGHTS,
            "crosswalk reference must be null B with a declared trait weight",
        )
        key = f"B η = {eta:.2f}"
    estimators = _dict(cell.get("estimators"), "crosswalk estimators")
    summary = _dict(estimators.get(QUASI_SIMPLEX), QUASI_SIMPLEX)
    values = _int(summary.get("n_values"), "n_values")
    failures = _int(summary.get("failures"), "failures")
    _require(
        values >= 0 and failures >= 0 and values + failures == replicates,
        "crosswalk replicate counts do not add up",
    )
    low = high = None
    if values:
        low = _float(summary.get("min"), "crosswalk min", 0, 1)
        high = _float(summary.get("max"), "crosswalk max", 0, 1)
        mean = _float(summary.get("mean"), "crosswalk mean", 0, 1)
        _require(low <= mean <= high, "crosswalk mean outside its range")
    else:
        _require(
            summary.get("min") is None and summary.get("max") is None,
            "crosswalk range without values",
        )
    if key not in CROSSWALK_REFERENCES:
        return None, (key, r)
    return CrosswalkRange(key, r, low, high, values, failures), (key, r)


def parse_crosswalk(data: object) -> Crosswalk:
    top = _dict(data, "crosswalk")
    _require(
        top.get("schema") == CROSSWALK_SCHEMA and top.get("status") == "exploratory",
        "not an exploratory SHP crosswalk aggregate",
    )
    parameters = _dict(top.get("parameters"), "crosswalk parameters")
    replicates = _int(parameters.get("replicates"), "replicates")
    _require(replicates >= 1, "crosswalk needs replicates")
    _require(
        QUASI_SIMPLEX in _list(parameters.get("estimators"), "estimators"),
        "crosswalk lacks the primary quasi-simplex estimator",
    )
    ranges: list[CrosswalkRange] = []
    seen: set[tuple[str, float]] = set()
    for item in _list(top.get("cells"), "crosswalk cells"):
        parsed, key = _crosswalk_range(item, replicates)
        _require(key not in seen, "duplicate crosswalk cell")
        seen.add(key)
        if parsed is not None:
            ranges.append(parsed)
    ranges.sort(key=lambda x: (CROSSWALK_REFERENCES.index(x.reference), x.r))
    return Crosswalk(
        _bool(top.get("declared_plan"), "declared_plan"), replicates, tuple(ranges)
    )


def load_crosswalk(path: Path) -> Crosswalk:
    return parse_crosswalk(json.loads(path.read_text(encoding="utf-8")))


def r_grid() -> tuple[float, ...]:
    return RELIABILITIES
