"""Exploratory X3: null B with a free signal share (R2-M1).

Declared on 2026-09-28 in
``experiments/exploratory/detection-boundary-v4-exploratory/README-x3-x7.md``
before any confirmatory result. In each of the 72 tier-1 cells with a > 0,
B_r passes the frozen latent law of B through the frozen observed channel at
its own signal share r_B and is fitted to L1, L2 and L3 of the frozen coupled
matching panels: frozen ``profile_match`` solves (phi, eta) at every r_B and an
Illinois-safeguarded secant solves L3 in r_B. Frozen ``fit_discriminant`` on
L4 and L5 then contrasts the interaction arm with the frozen two-parameter B
of frozen ``fit_cell`` (known contrast) and with B_r (free contrast) on the
same social panels. Every stream comes from the ``v4-exploratory-x3-x7``
namespace. Results stay sealed until the confirmatory release and are never
promoted to confirmatory evidence.
"""

from __future__ import annotations

import json
import math
import time
from collections.abc import Callable, Mapping, Sequence
from contextlib import ExitStack
from dataclasses import asdict, dataclass, replace
from functools import partial
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.analysis.detection_boundary import auc
from ic_study.analysis.detection_boundary_v4 import (
    ProfileFit,
    Validation,
    profile_match,
    validate_fit,
)
from ic_study.analysis.redesign import fit_discriminant
from ic_study.models.anchored_panel import Floats
from ic_study.models.detection_panel_v4 import null
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation.detection_v4 import (
    Cell,
    PanelSource,
    SeedPlan,
    ValidatedFit,
    fit_cell,
)
from ic_study.simulation.v4_curve import _put_array
from ic_study.simulation.v4_exploratory import SIZE, WAVES, observed_profile, utc_now
from ic_study.simulation.v4_exploratory_x1b import ensure_provenance
from ic_study.simulation.v4_gate import fit_record
from ic_study.simulation.v4_store import SealedStore

MODULES = (Path(__file__).resolve(),)
UNITS = f.tier1_units("x3")
CELLS = tuple(
    (unit, index)
    for unit in UNITS
    for index, cell in enumerate(unit.cells)
    if cell.share > 0
)
STORE_CELLS = ((0.0, 0.9), (0.03, 0.5), (0.3, 0.6))
FIT_CELLS = ((0.03, 0.5), (0.3, 0.6))
MATCHING = 1024
VALIDATION = 2048
UPPER = 0.999
STEP = 0.01
MARGIN = 0.02
PRIMARY = 0.70
FIT_ARRAYS = ("parameters", "differences", "residual", "se", "tolerance")
FIT_RULE = (
    "frozen fit_cell and the successor fitting wrapper, same successor unit and "
    "seeds, declared sizes, separate processes on one host and commit; the first "
    "attempt's record (matching pairs, parameters, differences, residuals, "
    "standard errors, tolerances, evaluations, status and fitted moments) equal "
    "byte for byte in every file of the record store except access.jsonl, whose "
    "(action, key) sequence must be equal"
)
OUTER_RULE = (
    "start at the cell's r clipped into [|mean target L1|, 0.999] and a probe "
    "0.01 inside the bracket; secant steps clamped to the bracket until two "
    "points straddle the root; then Illinois-weighted regula falsi with a "
    "bisection every fourth step or when the secant leaves the straddle, as the "
    "frozen eta search; interior when |L3 residual| <= min(5e-5, max(1e-6, "
    "0.25 SE_fit)); family-limit (no L3 root in the bracket) when a clamped "
    "secant repeats the end it stands on without a sign change; inner-failure "
    "when frozen profile_match does not succeed; budget after 12 outer "
    "evaluations"
)
NOMINAL = {"inner_evaluations": 23.2, "outer_evaluations": 6}


@dataclass(frozen=True)
class X3Sizes:
    size: int = SIZE
    matching: int = MATCHING
    retry_matching: int = 4096
    train: int = 2000
    check: int = 4000
    resamples: int = 1000
    outer_budget: int = 12


DECLARED = X3Sizes()


def finite(values: Sequence[float] | Floats) -> list[float | None]:
    return [float(v) if math.isfinite(v) else None for v in values]


def se_units(residual: Floats, se: Floats) -> list[float | None]:
    """Residuals in standard-error units, as frozen ``fit_record`` writes them."""
    z = np.divide(residual, se, out=np.full(len(se), np.inf), where=se > 0)
    z[(residual == 0) & (se == 0)] = 0
    return finite(z)


# Successor source -------------------------------------------------------------


def _interaction_row(
    cell: Cell, _: Cell, size: int, seed: f.SeedFn, index: int, coupled: bool
) -> Floats:
    return f.frozen_social_profile(cell, size, seed, index, coupled)


class SignalShareSource(f.SuccessorSource):
    """X3's tier-1 source: null B_r at signal share r_B, interaction arm at r.

    Null panels are the frozen ``PanelSource._profiles`` of
    ``replace(cell, reliability=r_B)`` with the same seeds. That cell also
    names the frozen checkpoints, so every key carries r_B and sources at
    different shares share one store without collisions. The interaction arm
    is the frozen tier-1 row at the cell's own r. At r_B = r this is the
    frozen source, key for key.
    """

    def __init__(
        self,
        cell: Cell,
        seeds: SeedPlan,
        *,
        signal: float,
        size: int = SIZE,
        store: SealedStore | None = None,
    ) -> None:
        super().__init__(
            replace(cell, reliability=signal),
            seeds,
            social=partial(_interaction_row, cell),
            size=size,
            store=store,
        )


def _neutral_source(
    cell: Cell, plan: f.SuccessorSeedPlan, store: SealedStore, size: int
) -> PanelSource:
    return SignalShareSource(
        cell, plan, signal=cell.reliability, size=size, store=store
    )


# Free fit: frozen inner solve of (phi, eta) and outer solve of L3 in r_B -------


@dataclass(frozen=True)
class Matching:
    """One free-fit attempt: its coupled matching target (L1..L3) and sources."""

    cell: Cell
    seeds: SeedPlan
    size: int
    store: SealedStore | None
    count: int
    attempt: int
    target: Floats

    def source(self, signal: float) -> SignalShareSource:
        return SignalShareSource(
            self.cell, self.seeds, signal=signal, size=self.size, store=self.store
        )


def matching(
    cell: Cell,
    seeds: SeedPlan,
    size: int,
    store: SealedStore | None,
    count: int,
    attempt: int,
) -> Matching:
    """The frozen coupled matching panels of the interaction arm, as fit_cell's."""
    social = SignalShareSource(
        cell, seeds, signal=cell.reliability, size=size, store=store
    )
    target = social.profiles("match", count, attempt=attempt)[:, :3]
    return Matching(cell, seeds, size, store, count, attempt, target)


@dataclass(frozen=True)
class OuterPoint:
    """Frozen ``profile_match`` of (phi, eta) at one r_B and its L3 residual."""

    signal: float
    fit: ProfileFit
    residual: float
    se: float
    tolerance: float

    @property
    def good(self) -> bool:
        return bool(abs(self.residual) <= self.tolerance)


def outer_point(context: Matching, signal: float) -> OuterPoint:
    """One outer evaluation: the inner fit at r_B with the frozen arguments.

    The L3 residual, its SE and tolerance are the third components of the
    frozen fitting formulas applied to L1..L3 at the fitted point.
    """
    source = context.source(signal)

    def evaluate(phi: float, eta: float) -> Floats:
        return source.profiles(
            "match",
            context.count,
            parameters=np.array([phi, eta]),
            attempt=context.attempt,
        )[:, :2]

    fit = profile_match(context.target[:, :2], evaluate, identity=context.cell.identity)
    if not fit.success:
        return OuterPoint(signal, fit, math.nan, math.nan, math.nan)
    rows = source.profiles(
        "match", context.count, parameters=fit.parameters, attempt=context.attempt
    )[:, :3]
    differences = rows - context.target
    se = differences.std(0, ddof=1) / np.sqrt(len(differences))
    tolerance = np.minimum(5e-5, np.maximum(1e-6, 0.25 * se))
    return OuterPoint(
        signal,
        fit,
        float(differences.mean(0)[2]),
        float(se[2]),
        float(tolerance[2]),
    )


class _SolverStopError(Exception):
    pass


def solve_signal(
    evaluate: Callable[[float], OuterPoint],
    start: float,
    lower: float,
    *,
    budget: int,
    upper: float = UPPER,
) -> tuple[str, tuple[OuterPoint, ...]]:
    """X3's outer solver for the L3 residual in r_B on [lower, upper].

    The first two evaluations preserve the registered start and probe. A
    degenerate secant probes unvisited endpoints, then bisects the widest
    unexamined interval. A straddle uses Illinois and safeguarded bisection.
    Finite same-sign samples do not prove absence of a root: without a
    straddle, exhaustion is a budget result. Only a nonzero residual on a
    singleton domain demonstrates a family limit.
    """
    points: list[OuterPoint] = []

    def at(signal: float) -> OuterPoint:
        if len(points) >= budget:
            raise _SolverStopError("budget")
        point = evaluate(signal)
        points.append(point)
        if not point.fit.success:
            raise _SolverStopError("inner-failure")
        return point

    try:
        previous = at(start)
        if previous.good:
            return "interior", tuple(points)
        probe = start + STEP if start + STEP <= upper else start - STEP
        probe = min(max(probe, lower), upper)
        if lower == upper:
            raise _SolverStopError("family-limit")
        if probe == start:
            probe = upper if start != upper else lower
        current = at(probe)
        while not current.good and (current.residual < 0) == (previous.residual < 0):
            slope = (current.residual - previous.residual) / (
                current.signal - previous.signal
            )
            trial = current.signal - current.residual / slope if slope else math.nan
            visited = {point.signal for point in points}
            if math.isfinite(trial):
                trial = min(max(trial, lower), upper)
            if not math.isfinite(trial) or trial in visited:
                endpoints = [value for value in (upper, lower) if value not in visited]
                if endpoints:
                    trial = endpoints[0]
                else:
                    ordered = sorted(visited)
                    left, right = max(
                        pairwise(ordered),
                        key=lambda pair: pair[1] - pair[0],
                    )
                    trial = (left + right) / 2
                    if trial in visited:
                        raise _SolverStopError("budget")
            previous, current = current, at(trial)
        if current.good:
            return "interior", tuple(points)
        negative, positive = (
            (current, previous) if current.residual < 0 else (previous, current)
        )
        negative_weight = positive_weight = 1.0
        side = 0
        iteration = 0
        while True:
            low, high = sorted((negative.signal, positive.signal))
            trial = (low + high) / 2
            if iteration % 4 != 3:
                secant = positive.signal - positive_weight * positive.residual * (
                    positive.signal - negative.signal
                ) / (
                    positive_weight * positive.residual
                    - negative_weight * negative.residual
                )
                if low + 1e-12 < secant < high - 1e-12:
                    trial = secant
            candidate = at(trial)
            if candidate.good:
                return "interior", tuple(points)
            if candidate.residual < 0:
                negative, negative_weight = candidate, 1.0
                positive_weight = positive_weight / 2 if side == -1 else 1.0
                side = -1
            else:
                positive, positive_weight = candidate, 1.0
                negative_weight = negative_weight / 2 if side == 1 else 1.0
                side = 1
            iteration += 1
    except _SolverStopError as stop:
        return str(stop), tuple(points)


@dataclass(frozen=True)
class FreeAttempt:
    count: int
    status: str
    lower: float
    start: float
    points: tuple[OuterPoint, ...]
    validation: Validation | None = None
    passed: bool | None = None


@dataclass(frozen=True)
class FreeFit:
    attempts: tuple[FreeAttempt, ...]

    @property
    def final(self) -> FreeAttempt:
        return self.attempts[-1]

    @property
    def success(self) -> bool:
        return self.final.status == "interior" and self.final.passed is True

    @property
    def point(self) -> OuterPoint:
        return self.final.points[-1]


def solve_attempt(context: Matching, budget: int) -> FreeAttempt:
    lower = abs(float(context.target[:, 0].mean()))
    start = min(max(context.cell.reliability, lower), UPPER)
    status, points = solve_signal(
        partial(outer_point, context), start, lower, budget=budget
    )
    return FreeAttempt(context.count, status, lower, start, points)


def validate_free(context: Matching, point: OuterPoint) -> tuple[Validation, bool]:
    """Frozen validation on 2,048 fresh coupled pairs, its rule applied to L1..L3."""
    social = context.source(context.cell.reliability).profiles(
        "validate", VALIDATION, attempt=context.attempt
    )[:, :3]
    rows = context.source(point.signal).profiles(
        "validate",
        VALIDATION,
        parameters=point.fit.parameters,
        attempt=context.attempt,
    )[:, :3]
    se = np.append(point.fit.se, point.se)
    validation = validate_fit(rows - social, 2, se)
    total = np.hypot(se, validation.se)
    third = bool(abs(validation.residual[2]) <= 4 * total[2])
    return validation, validation.passed and third


def fit_free(
    cell: Cell, seeds: SeedPlan, store: SealedStore | None, sizes: X3Sizes
) -> FreeFit:
    """B_r on L1..L3 with the frozen D4 rule: one retry at 4,096 pairs, and only
    after an interior fit fails validation."""
    attempts: list[FreeAttempt] = []
    for attempt, count in enumerate((sizes.matching, sizes.retry_matching)):
        context = matching(cell, seeds, sizes.size, store, count, attempt)
        solved = solve_attempt(context, sizes.outer_budget)
        if solved.status == "interior":
            validation, passed = validate_free(context, solved.points[-1])
            solved = replace(solved, validation=validation, passed=passed)
        attempts.append(solved)
        if solved.status != "interior" or solved.passed:
            break
    return FreeFit(tuple(attempts))


# Contrasts ----------------------------------------------------------------------


def contrast(
    null_train: Floats, social_train: Floats, null_check: Floats, social_check: Floats
) -> tuple[Floats, Floats]:
    """Frozen ``fit_discriminant`` on L4 and L5 (profile columns 3:5)."""
    model = fit_discriminant(
        np.concatenate([null_train[:, 3:5], social_train[:, 3:5]]),
        np.repeat([0, 1], len(null_train)),
    )
    return model.score(null_check[:, 3:5]), model.score(social_check[:, 3:5])


def _point_record(point: OuterPoint) -> dict[str, Any]:
    fit = point.fit
    record: dict[str, Any] = {
        "signal": point.signal,
        "inner_status": fit.status,
        "inner_evaluations": fit.evaluations,
        "parameters": finite(fit.parameters),
    }
    if not fit.success:
        return record
    residual = np.append(fit.residual, point.residual)
    se = np.append(fit.se, point.se)
    return {
        **record,
        "residual": finite(residual),
        "se": finite(se),
        "tolerance": finite(np.append(fit.tolerance, point.tolerance)),
        "residual_se_units": se_units(residual, se),
    }


def free_record(fit: FreeFit) -> dict[str, Any]:
    attempts = []
    for attempt in fit.attempts:
        validation = attempt.validation
        attempts.append(
            {
                "matching_pairs": attempt.count,
                "status": attempt.status,
                "bracket": [attempt.lower, UPPER],
                "start": attempt.start,
                "outer_evaluations": len(attempt.points),
                "inner_evaluations": sum(p.fit.evaluations for p in attempt.points),
                "points": [_point_record(point) for point in attempt.points],
                "validation_pass": attempt.passed,
                "validation_combined_se_units": None
                if validation is None
                else finite(validation.z),
            }
        )
    record: dict[str, Any] = {
        "success": fit.success,
        "rule": OUTER_RULE,
        "attempts": attempts,
    }
    if fit.success:
        point = fit.point
        record["parameters"] = {
            "phi": float(point.fit.parameters[0]),
            "eta": float(point.fit.parameters[1]),
            "signal": point.signal,
        }
    return record


def known_record(fit: ValidatedFit) -> dict[str, Any]:
    return {**fit_record(fit), "parameters": fit.final.fit.parameters.tolist()}


def x3_contrasts(
    cell: Cell, seeds: SeedPlan, store: SealedStore | None, sizes: X3Sizes
) -> dict[str, Any]:
    """Known and free contrasts of one cell; a failed known fit is a cell gap
    and a failed free fit a gap of the free contrast only."""
    social = SignalShareSource(
        cell, seeds, signal=cell.reliability, size=sizes.size, store=store
    )
    known = fit_cell(social)
    statuses = [f"known:{attempt.fit.status}" for attempt in known.attempts]
    result: dict[str, Any] = {
        "known": known_record(known),
        "free": None,
        "delta": None,
        "means": None,
        "seeds": None,
    }
    if not known.success:
        return {**result, "success": False, "attempts": statuses, "gap": "known"}
    free = fit_free(cell, seeds, store, sizes)
    statuses += [f"free:{attempt.status}" for attempt in free.attempts]
    parameters = known.final.fit.parameters
    social_train = social.profiles("train", sizes.train)
    social_check = social.profiles("check", sizes.check)
    known_check = social.profiles("check", sizes.check, parameters=parameters)
    arms = {"social": social_check, "known": known_check}
    contrasts = [
        contrast(
            social.profiles("train", sizes.train, parameters=parameters),
            social_train,
            known_check,
            social_check,
        )
    ]
    if free.success:
        point = free.point
        source = SignalShareSource(
            cell, seeds, signal=point.signal, size=sizes.size, store=store
        )
        free_check = source.profiles(
            "check", sizes.check, parameters=point.fit.parameters
        )
        arms["free"] = free_check
        contrasts.append(
            contrast(
                source.profiles("train", sizes.train, parameters=point.fit.parameters),
                social_train,
                free_check,
                social_check,
            )
        )
    networks = sizes.check // 2
    seed = seeds.seed("bootstrap", "resample", 0)
    draws = f.paired_network_bootstrap(
        [(n.reshape(networks, 2), s.reshape(networks, 2)) for n, s in contrasts],
        seed=seed,
        resamples=sizes.resamples,
    )
    areas = [auc(n, s) for n, s in contrasts]
    result["known"].update(auc=areas[0], interval_95=f.percentile_interval(draws[:, 0]))
    result["free"] = free_record(free)
    if free.success:
        result["free"].update(
            auc=areas[1], interval_95=f.percentile_interval(draws[:, 1])
        )
        result["delta"] = {
            "point": areas[1] - areas[0],
            "interval_95": f.percentile_interval(draws[:, 1] - draws[:, 0]),
        }
    result["means"] = {
        "set": "check panels, L1..L5 (profile columns 0:5)",
        **{arm: rows.mean(0).tolist() for arm, rows in arms.items()},
    }
    result["seeds"] = {"bootstrap": seed, "resamples": sizes.resamples}
    return {
        **result,
        "success": free.success,
        "attempts": statuses,
        "gap": None if free.success else "free",
    }


# Cell records ---------------------------------------------------------------------


def in_store(
    directory: Path, compute: Callable[[SealedStore], dict[str, Any]]
) -> tuple[dict[str, Any], str]:
    """``compute`` on a cell store with its output captured, then the seal.

    A sealed store is complete, so its checkpoints replay without writes.
    """
    store = SealedStore(directory)
    sealed = (store.root / "seal.json").exists()
    with ExitStack() as stack:
        if not sealed:
            stack.enter_context(store.capture_output())
        result = compute(store)
    if not sealed:
        store.seal()
    seal: dict[str, Any] = json.loads((store.root / "seal.json").read_bytes())
    return result, str(seal["sha256"])


def cell_identity(index: int, unit: f.SuccessorUnit, position: int) -> dict[str, Any]:
    cell = unit.cells[position]
    return {
        "index": index,
        "unit": unit.key,
        "position": position,
        "a": cell.share,
        "r": cell.reliability,
        "block": unit.block,
        "family": cell.family,
        "channel": cell.channel,
    }


def cell_record(
    kind: str,
    index: int,
    unit: f.SuccessorUnit,
    position: int,
    out: Path,
    digests: Mapping[str, str],
    sizes: dict[str, int],
    compute: Callable[[SealedStore], dict[str, Any]],
) -> dict[str, Any]:
    """One declared cell under ``out/<kind>-stores``; a ValueError is recorded
    and leaves the cell without a result."""
    stores = f.private_directory(out / f"{kind}-stores" / unit.key)
    ensure_provenance(SealedStore(stores), f.unit_provenance(kind, sizes["size"]))
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    result: dict[str, Any] = {"success": None, "attempts": []}
    seal, error = None, None
    try:
        computed, seal = in_store(stores / f"a{position}", compute)
        result.update(computed)
    except ValueError as failure:
        error = repr(failure)
    return {
        "schema": f"ic-study.v4-exploratory-{kind}-cell.v1",
        "label": f.LABEL,
        "cell": cell_identity(index, unit, position),
        "sizes": sizes,
        "verification_sha256": dict(digests),
        "error": error,
        **result,
        "seal_sha256": seal,
        "timing": {
            "started_utc": started,
            "finished_utc": utc_now(),
            "wall_seconds": time.perf_counter() - clock,
            "cpu_seconds": time.process_time() - cpu,
        },
    }


def x3_cell(
    index: int,
    out: Path,
    digests: Mapping[str, str],
    sizes: X3Sizes = DECLARED,
) -> dict[str, Any]:
    unit, position = CELLS[index]
    compute = partial(x3_contrasts, unit.cells[position], unit.seeds, sizes=sizes)
    return cell_record(
        "x3", index, unit, position, out, digests, asdict(sizes), compute
    )


def analyses(
    out: Path, digests: Mapping[str, str], sizes: X3Sizes = DECLARED
) -> dict[str, f.Analysis]:
    compute = partial(x3_cell, out=out, digests=digests, sizes=sizes)
    return {
        "x3": f.Analysis(
            "x3",
            len(CELLS),
            asdict(sizes),
            compute,
            MODULES,
            digests,
            [cell_identity(i, u, p) for i, (u, p) in enumerate(CELLS)],
        )
    }


# Bitwise preconditions --------------------------------------------------------------


def signal_share_cell(
    unit: f.SuccessorUnit, index: int, directory: Path, size: int
) -> None:
    """Successor side of ``x3-store``: X3's source at r_B = r in frozen pipeline."""
    f.execute_source_cell(unit, index, directory, _neutral_source, size=size)


def write_fit_record(
    directory: Path, compute: Callable[[], tuple[int, ProfileFit]]
) -> None:
    """A first-attempt fit record, arrays included, as a sealed store."""
    store = SealedStore(directory)
    if store.get_json("result") is not None:
        if not (store.root / "seal.json").exists():
            store.seal()
        return
    count, fit = compute()
    for key in FIT_ARRAYS:
        _put_array(store, key, getattr(fit, key))
    store.put_json(
        "result",
        {
            "success": fit.success,
            "attempts": [
                {
                    "matching_pairs": count,
                    "status": fit.status,
                    "evaluations": fit.evaluations,
                    "fitted_moments": fit.fitted_moments,
                }
            ],
        },
    )
    store.seal()


def frozen_first_fit(
    unit: f.SuccessorUnit, index: int, directory: Path, size: int
) -> None:
    """Frozen side of a fit-record precondition: frozen ``fit_cell``'s first try."""

    def compute() -> tuple[int, ProfileFit]:
        first = fit_cell(PanelSource(unit.cells[index], unit.seeds, size=size))
        return first.attempts[0].count, first.attempts[0].fit

    write_fit_record(directory, compute)


def first_outer_fit(
    unit: f.SuccessorUnit, index: int, directory: Path, size: int
) -> None:
    """Successor side of ``x3-fit``: the free fit's first outer evaluation."""

    def compute() -> tuple[int, ProfileFit]:
        context = matching(unit.cells[index], unit.seeds, size, None, MATCHING, 0)
        return MATCHING, solve_attempt(context, 1).points[0].fit

    write_fit_record(directory, compute)


STORE = f.Precondition(
    "x3-store", UNITS, STORE_CELLS, signal_share_cell, modules=MODULES
)
FIT = f.Precondition(
    "x3-fit", UNITS, FIT_CELLS, first_outer_fit, frozen_first_fit, MODULES, FIT_RULE
)


# Aggregate after the release ----------------------------------------------------------


def read_cell(record: Mapping[str, Any]) -> dict[str, Any]:
    """The declared per-cell reading, without multiplicity correction."""
    if record["error"] is not None:
        return {"reading": "error", "lost_crossing": None}
    if record["gap"] == "known":
        return {"reading": "gap", "lost_crossing": None}
    if record["gap"] == "free":
        status = record["free"]["attempts"][-1]["status"]
        return {"reading": "free-gap", "free_status": status, "lost_crossing": None}
    lower, upper = record["delta"]["interval_95"]
    if upper < 0:
        reading = "supports-objection"
    elif lower >= -MARGIN and upper <= MARGIN:
        reading = "against-objection"
    else:
        reading = "inconclusive"
    lost = record["known"]["auc"] >= PRIMARY and (
        record["free"]["interval_95"][1] < PRIMARY
    )
    return {"reading": reading, "lost_crossing": lost}


def aggregate(outs: Sequence[Path], sizes: X3Sizes = DECLARED) -> dict[str, Any]:
    release = f.require_release()
    records, incomplete, sources = f.union_complete_records(
        outs,
        "x3",
        len(CELLS),
        asdict(sizes),
        preconditions=SUITE.preconditions,
        identities=[cell_identity(i, u, p) for i, (u, p) in enumerate(CELLS)],
    )
    values = [records[index] for index in sorted(records)]
    cells = [
        {**{k: v for k, v in record.items() if k != "provenance"}, **read_cell(record)}
        for record in values
    ]
    readings: dict[str, int] = {}
    for cell in cells:
        readings[cell["reading"]] = readings.get(cell["reading"], 0) + 1
    return {
        "schema": "ic-study.v4-exploratory-x3.v1",
        "label": f.LABEL,
        "declaration": f.declaration_digests(),
        "release": release,
        "sources": sources,
        "sizes": asdict(sizes),
        "cells_declared": len(CELLS),
        "incomplete": incomplete,
        "summary": {
            "readings": readings,
            "lost_crossing": [
                [c["cell"]["a"], c["cell"]["r"]] for c in cells if c["lost_crossing"]
            ],
            "margin": MARGIN,
            "multiplicity": "none; per-cell readings only, no whole-curve claim",
        },
        "outer_rule": OUTER_RULE,
        "seeds": {**f.SEEDS, "analysis": "x3", "common_across_strengths": True},
        "code": f.shared_provenance(values, "code"),
        "host": f.shared_provenance(values, "host"),
        "timing": f.timing_summary(values),
        "cells": cells,
    }


# Timing probe ------------------------------------------------------------------------


def panel_rates(count: int) -> dict[str, float]:
    """CPU seconds per frozen null B panel and per tier-1 social panel.

    Probe seeds lie outside every namespace and the panels are discarded.
    """
    cell = Cell(0.3, 0.7)

    def null_panel(index: int) -> Floats:
        latent = null(
            SIZE,
            WAVES,
            f.probe_seed("state", index),
            f.probe_seed("null-state", index),
            family="B",
            phi=0.85,
            eta=0.2,
        )
        return observed_profile(
            latent,
            cell.reliability,
            f.probe_seed("mask", index),
            f.probe_seed("error", index),
        )

    def social_panel(index: int) -> Floats:
        return f.frozen_social_profile(cell, SIZE, f.probe_seed, 2 * index + 1, False)

    return {
        "null_panel_cpu_seconds": f.cpu_per_call(null_panel, count),
        "social_panel_cpu_seconds": f.cpu_per_call(social_panel, count),
    }


def cell_panels(
    inner: float = NOMINAL["inner_evaluations"],
    outer: float = NOMINAL["outer_evaluations"],
) -> dict[str, float]:
    """Null and social panels of one X3 cell without retries.

    The free fit's first outer evaluation replays the known fit's checkpoints.
    """
    known = inner * MATCHING + VALIDATION + 3 * MATCHING
    free = (outer - 1) * inner * MATCHING + VALIDATION
    contrasts = 2 * (DECLARED.train + DECLARED.check)
    social = MATCHING + VALIDATION + DECLARED.train + DECLARED.check
    return {"null": known + free + contrasts, "social": social}


def probe(count: int) -> dict[str, Any]:
    rates = panel_rates(count)
    panels = cell_panels()
    seconds = (
        panels["null"] * rates["null_panel_cpu_seconds"]
        + panels["social"] * rates["social_panel_cpu_seconds"]
    )
    return {
        "count": count,
        **rates,
        "nominal_cell_panels": panels,
        "nominal_cell_cpu_hours": seconds / 3600,
    }


SUITE = f.Suite(
    "x3",
    True,
    ("x3",),
    (STORE, FIT),
    analyses,
    lambda out: aggregate([out]),
    probe,
    MODULES,
    aggregate_union=aggregate,
)


def main(argv: Sequence[str] | None = None) -> int:
    return f.main(SUITE, argv)


if __name__ == "__main__":
    raise SystemExit(main())
