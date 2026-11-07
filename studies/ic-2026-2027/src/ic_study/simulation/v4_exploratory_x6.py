"""Exploratory X6: interior coverage of the frozen intervals and band (R2-M6).

Declared on 2026-09-28 in
``experiments/exploratory/detection-boundary-v4-exploratory/README-x3-x7.md``
before any confirmatory result. X6a repeats the whole r = 0.70 tier-1 unit 200
times with frozen ``execute_cell`` and ``complete_curve``; X6b repeats each of
the two other G2 cells, (0.03, 0.50) and (0.03, 0.90), 200 times at one
strength. The primary truth T_D1 is the frozen D1 estimand, the mean of 100
independent frozen pipelines per cell. The secondary truth T_pop is the mean
AUC of 50 frozen LDAs trained at the null fitted by frozen ``profile_match`` to
16,384 coupled matching pairs. Repetitions and truth pipelines run the frozen
executor unchanged; only the T_pop fit recombines frozen parts, and at
M = 1,024 its wrapper must reproduce the first frozen ``fit_cell`` attempt bit
for bit. Every record stays sealed until the confirmatory release. Outputs are
exploratory and never promoted to confirmatory evidence.

A cell's number is its frozen tier-1 inventory position, 9 * r index + a index.
Blocks follow the declaration: ``x6-rep`` 2 * repetition + attempt, ``x6b-rep``
2 * (1000 * cell + repetition) + attempt, ``x6-truth`` 2 * (1000 * cell + k) +
attempt and ``x6-pop`` 2 * cell + attempt, where T_pop training k draws panels
[k n, (k + 1) n) of the frozen train and check phases.
"""

from __future__ import annotations

import json
import math
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.analysis.detection_boundary import auc, feasible_lag1
from ic_study.analysis.detection_boundary_v4 import (
    Band,
    ProfileFit,
    Uncertainty,
    band,
    profile_match,
    score_uncertainty,
)
from ic_study.analysis.redesign import fit_discriminant
from ic_study.models.anchored_panel import Floats
from ic_study.simulation import v4_curve
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    Cell,
    FitAttempt,
    PanelSource,
    SeedPlan,
    ValidatedFit,
    fit_cell,
)
from ic_study.simulation.v4_curve import _put_array
from ic_study.simulation.v4_exploratory import SIZE, utc_now
from ic_study.simulation.v4_exploratory_x1b import ensure_provenance
from ic_study.simulation.v4_gate import fit_record
from ic_study.simulation.v4_store import SealedStore

MODULE = Path(__file__).resolve()
SCHEMA = "ic-study.v4-exploratory-x6-unit.v1"
AGGREGATE_SCHEMA = "ic-study.v4-exploratory-x6.v1"
X6A_RELIABILITY = 0.7
X6A_TRUTH_CELLS = tuple((a, X6A_RELIABILITY) for a in GRID if a > 0)
X6B_CELLS = ((0.03, 0.5), (0.03, 0.9))
PRECONDITION_CELLS = ((0.03, 0.7), (0.3, 0.7))
FROZEN_PAIRS = 1024
POINTWISE_CRITICAL = 1.959964
NETWORKS = 2000
TRUTH_SE_TARGET = 0.002
MINIMUM_COMPLETE = 100
TRUTH_FAILURE_FLAG = 0.05
UNCOVERED_BIAS = 0.25
FIT_ARRAYS = ("parameters", "differences", "residual", "se", "tolerance")
INTERIOR_PANELS = {"social": 13072, "null": 37800}
ANCHOR_PANELS = {"social": 9072, "null": 9072}
FIT_EVALUATIONS = 23.2
SEEDS = {
    **f.SEEDS,
    "cell_number": "9 * reliability index + strength index (frozen tier-1 inventory)",
    "blocks": {
        "x6-rep": "2 * repetition + attempt",
        "x6b-rep": "2 * (1000 * cell + repetition) + attempt",
        "x6-truth": "2 * (1000 * cell + k) + attempt",
        "x6-pop": "2 * cell + attempt; training k takes panels [k n, (k + 1) n)",
    },
    "common_across_strengths": "the nine strengths of one X6a repetition",
}


@dataclass(frozen=True)
class X6Sizes:
    size: int = SIZE
    repetitions: int = 200
    truth_pipelines: int = 100
    population_pairs: int = 16384
    population_trainings: int = 50
    population_train: int = 2000
    population_check: int = 4000


DECLARED = X6Sizes()


# Cells, units and the declared queue -------------------------------------------------


def cell_number(share: float, reliability: float) -> int:
    return len(GRID) * RELIABILITIES.index(reliability) + GRID.index(share)


@cache
def row(reliability: float) -> tuple[Cell, ...]:
    """The nine cells of the frozen tier-1 unit at ``reliability``."""
    return f.tier1_units("x6-rep")[RELIABILITIES.index(reliability)].cells


@dataclass(frozen=True)
class Job:
    """One X6 unit: a T_pop cell, a T_D1 pipeline or a coverage repetition.

    ``cell`` is None for an X6a repetition, which runs the whole r = 0.70
    unit; ``number`` is the truth pipeline k or the repetition.
    """

    kind: str
    cell: tuple[float, float] | None
    number: int = 0

    def unit(self) -> tuple[f.SuccessorUnit, int | None]:
        """The successor unit and the strength it runs (None: all nine)."""
        if self.cell is None:
            key = f"x6a-rep-{self.number:03d}"
            cells = row(X6A_RELIABILITY)
            return f.SuccessorUnit(key, 1, cells, "x6-rep", self.number), None
        share, reliability = self.cell
        number = cell_number(share, reliability)
        cells, index = row(reliability), GRID.index(share)
        if self.kind == "pop":
            key = f"x6-pop-c{number:02d}"
            return f.SuccessorUnit(key, 1, (cells[index],), "x6-pop", number), 0
        analysis, key = {
            "truth": ("x6-truth", f"x6-truth-c{number:02d}-k{self.number:03d}"),
            "repetition": ("x6b-rep", f"x6b-rep-c{number:02d}-{self.number:03d}"),
        }[self.kind]
        block = 1000 * number + self.number
        return f.SuccessorUnit(key, 1, cells, analysis, block), index

    def describe(self) -> dict[str, Any]:
        unit, index = self.unit()
        return {
            "kind": self.kind,
            "cell": None if self.cell is None else list(self.cell),
            "cell_number": None if self.cell is None else cell_number(*self.cell),
            "number": self.number,
            "unit": unit.key,
            "index": index,
            "seed_analysis": unit.analysis,
            "block": unit.block,
        }


def queue(analysis: str, sizes: X6Sizes = DECLARED) -> tuple[Job, ...]:
    """The declared, result-independent unit order of X6a or X6b.

    T_pop cells come first, each one long unit. Repetitions and truth
    pipelines then interleave at their count ratio, so both reach the same
    fraction of their totals together: in X6a each repetition is followed by
    four truth pipelines, in X6b every two repetitions by one. Truth pipelines
    and X6b repetitions cycle over the cells.
    """
    if analysis not in ("x6a", "x6b"):
        raise ValueError("X6 has the analyses x6a and x6b")
    cells = X6A_TRUTH_CELLS if analysis == "x6a" else X6B_CELLS
    truths = [
        Job("truth", cells[t % len(cells)], t // len(cells))
        for t in range(len(cells) * sizes.truth_pipelines)
    ]
    repetitions = (
        [Job("repetition", None, i) for i in range(sizes.repetitions)]
        if analysis == "x6a"
        else [
            Job("repetition", cells[t % len(cells)], t // len(cells))
            for t in range(len(cells) * sizes.repetitions)
        ]
    )
    paced = sorted(
        [(i * len(truths), 0, i, job) for i, job in enumerate(repetitions)]
        + [(t * len(repetitions), 1, t, job) for t, job in enumerate(truths)],
        key=lambda item: item[:3],
    )
    return (*(Job("pop", cell) for cell in cells), *(item[3] for item in paced))


# T_pop: the population-matched null ----------------------------------------------


def population_fit(source: PanelSource, pairs: int) -> ProfileFit:
    """The first ``fit_cell`` attempt's solver step on ``pairs`` coupled pairs.

    A tier-1 cell has no fixed eta, the lag-1 feasibility cap r and frozen
    ``profile_match`` on the coupled target and CRN evaluations of frozen
    ``PanelSource.profiles`` at attempt 0. No validation is declared for T_pop.
    """
    cell = source.cell
    if cell != Cell(cell.share, cell.reliability):
        raise ValueError("The population fit covers tier-1 cells only")
    target = source.profiles("match", pairs)[:, :2]
    if not feasible_lag1(
        float(target[:, 0].mean()),
        cell.reliability,
        error_correlation=cell.error_correlation,
    ):
        status = (
            "family-limit-upper" if target[:, 0].mean() > 0 else "family-limit-lower"
        )
        zeros = np.zeros(2)
        return ProfileFit(
            np.array([0.85, 0]),
            np.zeros_like(target),
            zeros,
            zeros,
            zeros,
            0,
            status,
            2,
        )

    def evaluate(phi: float, eta: float) -> Floats:
        return source.profiles("match", pairs, parameters=np.array([phi, eta]))[:, :2]

    return profile_match(target, evaluate, identity=cell.identity)


def write_fit(store: SealedStore, pairs: int, fit: ProfileFit) -> None:
    """One fit attempt's arrays and frozen ``fit_record`` entry, then the seal."""
    for name in FIT_ARRAYS:
        _put_array(store, name, getattr(fit, name))
    attempts = fit_record(ValidatedFit((FitAttempt(pairs, fit, None),)))["attempts"]
    store.put_json(
        "result",
        {
            "success": fit.success,
            "fitted_moments": fit.fitted_moments,
            "attempts": attempts,
        },
    )
    store.seal()


def fit_population(
    cell: Cell, seeds: SeedPlan, directory: Path, *, size: int, pairs: int
) -> None:
    """``population_fit`` into ``directory``, resumable from panel checkpoints.

    Frozen ``PanelSource`` checkpoints the matching panels in the sibling
    store ``<directory>-panels``; a finished fit is never recomputed.
    """
    store = SealedStore(directory)
    panels = SealedStore(directory.with_name(f"{directory.name}-panels"))
    if store.get_json("result") is None:
        source = PanelSource(cell, seeds, size=size, store=panels)
        write_fit(store, pairs, population_fit(source, pairs))
    for sealed in (store, panels):
        if not (sealed.root / "seal.json").exists():
            sealed.seal()


def frozen_first_attempt(
    unit: f.SuccessorUnit, index: int, directory: Path, size: int
) -> None:
    """Precondition, frozen side: the first attempt of frozen ``fit_cell``."""
    first = fit_cell(PanelSource(unit.cells[index], unit.seeds, size=size)).attempts[0]
    write_fit(SealedStore(directory), first.count, first.fit)


def population_first_attempt(
    unit: f.SuccessorUnit, index: int, directory: Path, size: int
) -> None:
    """Precondition, successor side: the T_pop fit path at M = 1,024."""
    fit_population(
        unit.cells[index], unit.seeds, directory, size=size, pairs=FROZEN_PAIRS
    )


def population_units() -> tuple[f.SuccessorUnit, ...]:
    return tuple(Job("pop", cell).unit()[0] for cell in (*X6A_TRUTH_CELLS, *X6B_CELLS))


PRECONDITION = f.Precondition(
    "x6-pop",
    population_units(),
    PRECONDITION_CELLS,
    population_first_attempt,
    frozen_first_attempt,
    (MODULE,),
    rule=(
        "the T_pop fit wrapper at M = 1,024 and frozen fit_cell, same successor "
        "unit and x6-pop seeds, declared panel size, separate processes on one "
        "host and commit; each side writes its first attempt's arrays (parameters, "
        "differences, residual, se, tolerance) and frozen fit_record entry "
        "without validation; every file equal byte for byte except access.jsonl, "
        "whose (action, key) sequence must be equal"
    ),
)


def population_trainings(
    cell: Cell, seeds: SeedPlan, theta: Floats, store: SealedStore, sizes: X6Sizes
) -> list[float]:
    """AUCs of independent frozen LDAs trained and checked at ``theta``.

    Training k takes panels [k n, (k + 1) n) of the frozen train phase (n per
    class) and of the check phase from frozen ``PanelSource.profiles``, then
    the frozen discriminant, scoring and AUC; scores are checkpointed.
    """
    source = PanelSource(cell, seeds, size=sizes.size)
    train, check = sizes.population_train, sizes.population_check
    labels = np.repeat([0, 1], train)
    values = []
    for k in range(sizes.population_trainings):
        keys = f"k{k:02d}-null", f"k{k:02d}-social"
        null, social = (store.get_array(key) for key in keys)
        if null is None or social is None:
            train0 = source.profiles("train", train, parameters=theta, start=k * train)
            train1 = source.profiles("train", train, start=k * train)
            check0 = source.profiles("check", check, parameters=theta, start=k * check)
            check1 = source.profiles("check", check, start=k * check)
            features = np.concatenate([train0[:, 2:5], train1[:, 2:5]])
            model = fit_discriminant(features, labels)
            null, social = model.score(check0[:, 2:5]), model.score(check1[:, 2:5])
            _put_array(store, keys[0], null)
            _put_array(store, keys[1], social)
        values.append(auc(null, social))
    if not (store.root / "seal.json").exists():
        store.seal()
    return values


def population(unit: f.SuccessorUnit, stores: Path, sizes: X6Sizes) -> dict[str, Any]:
    cell = unit.cells[0]
    directory = stores / "fit"
    resumed = (directory / "result.json").exists()
    try:
        fit_population(
            cell,
            unit.seeds,
            directory,
            size=sizes.size,
            pairs=sizes.population_pairs,
        )
    except ValueError as failure:
        return {
            "error": repr(failure),
            "success": None,
            "attempts": [],
            "fit": None,
            "trainings": [],
        }
    store = SealedStore(directory)
    result: dict[str, Any] | None = store.get_json("result")
    parameters = store.get_array("parameters")
    if result is None or parameters is None:
        raise ValueError("Population fit omitted its record")
    attempt = result["attempts"][0]
    body: dict[str, Any] = {
        "error": None,
        "success": result["success"],
        "attempts": [attempt["status"]],
        "fit": {**attempt, "parameters": parameters.tolist()},
        "fit_resumed": resumed,
        "fit_seal_sha256": _seal(directory),
        "trainings": [],
    }
    if result["success"]:
        trainings = SealedStore(stores / "trainings")
        try:
            body["trainings"] = population_trainings(
                cell, unit.seeds, parameters, trainings, sizes
            )
        except ValueError as failure:
            body["error"] = repr(failure)
        body["trainings_seal_sha256"] = _seal(trainings.root)
    return body


# Frozen repetitions and truth pipelines ---------------------------------------------


def _seal(directory: Path) -> str | None:
    seal = directory / "seal.json"
    return str(json.loads(seal.read_bytes())["sha256"]) if seal.exists() else None


def frozen_cell(unit: f.SuccessorUnit, index: int, stores: Path) -> str | None:
    """Frozen ``v4_curve.execute_cell``; a ValueError is returned, not hidden."""
    try:
        v4_curve.execute_cell(unit, index, stores / f"a{index}")
    except ValueError as failure:
        return repr(failure)
    return None


def cell_outcome(directory: Path, cell: Cell, error: str | None) -> dict[str, Any]:
    """Fit statuses and diagnostics from a frozen cell's ``result.json``."""
    outcome: dict[str, Any] = {
        "a": cell.share,
        "r": cell.reliability,
        "error": error,
        "result": False,
        "success": None,
        "attempts": [],
    }
    result: dict[str, Any] | None = SealedStore(directory).get_json("result")
    if result is None:
        return outcome
    attempts = result["attempts"]
    final = attempts[-1]
    outcome.update(
        result=True,
        success=result["success"],
        attempts=[attempt["status"] for attempt in attempts],
        retry=len(attempts) > 1,
        mean_shift=result["mean_shift"][0] if result["mean_shift"] else None,
        residual_se_units=final["residual_se_units"],
        amplification=final["amplification"],
        seal_sha256=_seal(directory),
    )
    return outcome


def stored_uncertainty(
    unit: f.SuccessorUnit, directories: Sequence[Path]
) -> Uncertainty:
    """Frozen ``score_uncertainty`` on stored arrays stacked as ``complete_curve``."""
    arrays: dict[str, list[Floats]] = {"scores0": [], "scores1": [], "nuisance": []}
    for directory in directories:
        store = SealedStore(directory)
        for name, values in arrays.items():
            value = store.get_array(name)
            if value is None:
                raise ValueError("Successful cell has missing numerical checkpoints")
            values.append(value)
    return score_uncertainty(
        np.stack(arrays["scores0"], axis=-1),
        np.stack(arrays["scores1"], axis=-1),
        np.stack(arrays["nuisance"], axis=-1),
        seed=unit.seeds.seed("bootstrap", "state", 0),
    )


def _intervals(
    cells: Sequence[dict[str, Any]],
    positions: Sequence[int],
    uncertainty: Uncertainty,
    frozen: Band | None,
) -> None:
    lower, upper = f.fixed_band(uncertainty, POINTWISE_CRITICAL)
    for j, position in enumerate(positions):
        cells[position].update(
            point=float(uncertainty.point[j]),
            se=float(uncertainty.se[j]),
            conditional_se=float(uncertainty.conditional_se[j]),
            pointwise=[float(lower[j]), float(upper[j])],
            band=None
            if frozen is None
            else [float(frozen.lower[j]), float(frozen.upper[j])],
        )


def whole_unit(unit: f.SuccessorUnit, stores: Path) -> dict[str, Any]:
    """An X6a repetition: frozen cells, frozen curve, recomputed intervals.

    The pointwise interval is the frozen band formula at the fixed critical
    1.959964 on the ``score_uncertainty`` that ``complete_curve`` computes
    internally; the band is frozen ``band`` on the same object.
    """
    errors = [frozen_cell(unit, index, stores) for index in range(len(unit.cells))]
    cells = [
        cell_outcome(stores / f"a{index}", cell, error)
        for index, (cell, error) in enumerate(zip(unit.cells, errors, strict=True))
    ]
    failures = {str(unit.cells[i].share): e for i, e in enumerate(errors) if e}
    curve = None
    if not failures:
        try:
            curve = v4_curve.complete_curve(unit, stores)
        except ValueError as failure:
            failures["curve"] = repr(failure)
    available = [i for i, cell in enumerate(cells) if cell["success"]]
    summary = None
    try:
        if available:
            directories = [stores / f"a{i}" for i in available]
            uncertainty = stored_uncertainty(unit, directories)
            frozen = None if curve is None else band(uncertainty)
            _intervals(cells, available, uncertainty, frozen)
            if curve is not None and frozen is not None:
                summary = {
                    "band_complete": curve["band_complete"],
                    "gap_count": curve["gap_count"],
                    "critical": float(frozen.critical),
                    "empirical_exceeds_floor": bool(frozen.empirical_exceeds_floor),
                    "band_reproduced": curve.get("auc") == uncertainty.point.tolist()
                    and curve.get("lower") == frozen.lower.tolist()
                    and curve.get("upper") == frozen.upper.tolist(),
                }
    except ValueError as failure:
        failures["intervals"] = repr(failure)
    unit_store = SealedStore(stores)
    if curve is not None and not (stores / "seal.json").exists():
        unit_store.seal()
    return {
        "error": "; ".join(f"{key}: {value}" for key, value in failures.items())
        or None,
        "errors": failures,
        "success": None if failures else all(cell["success"] for cell in cells),
        "attempts": [status for cell in cells for status in cell["attempts"]],
        "cells": cells,
        "curve": summary,
        "unit_seal_sha256": _seal(stores),
    }


def one_cell(
    unit: f.SuccessorUnit, index: int, stores: Path, *, intervals: bool
) -> dict[str, Any]:
    """A truth pipeline (point only) or an X6b repetition (pointwise interval)."""
    error = frozen_cell(unit, index, stores)
    directory = stores / f"a{index}"
    cell = cell_outcome(directory, unit.cells[index], error)
    try:
        if cell["success"] and intervals:
            _intervals([cell], [0], stored_uncertainty(unit, [directory]), None)
        elif cell["success"]:
            store = SealedStore(directory)
            null, social = store.get_array("scores0"), store.get_array("scores1")
            if null is None or social is None:
                raise ValueError("Successful cell has missing numerical checkpoints")
            cell["point"] = auc(null.ravel(), social.ravel())
    except ValueError as failure:
        error = repr(failure)
    return {
        "error": error,
        "success": cell["success"],
        "attempts": cell["attempts"],
        "cells": [cell],
    }


def run_job(
    job: Job, out: Path, verification: Mapping[str, str], sizes: X6Sizes
) -> dict[str, Any]:
    """One unit of the queue into ``out/stores/<unit key>``; sealed record."""
    unit, index = job.unit()
    stores = f.private_directory(out / "stores" / unit.key)
    ensure_provenance(SealedStore(stores), f.unit_provenance(unit.analysis, sizes.size))
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    if job.kind == "pop":
        body = population(unit, stores, sizes)
    elif index is None:
        body = whole_unit(unit, stores)
    else:
        body = one_cell(unit, index, stores, intervals=job.kind == "repetition")
    return {
        "schema": SCHEMA,
        "label": f.LABEL,
        "job": job.describe(),
        "sizes": asdict(sizes),
        "verification_sha256": dict(verification),
        **body,
        "timing": {
            "started_utc": started,
            "finished_utc": utc_now(),
            "wall_seconds": time.perf_counter() - clock,
            "cpu_seconds": time.process_time() - cpu,
        },
    }


def analyses(
    out: Path, verification: Mapping[str, str], sizes: X6Sizes = DECLARED
) -> dict[str, f.Analysis]:
    def analysis(name: str) -> f.Analysis:
        jobs = queue(name, sizes)
        return f.Analysis(
            name,
            len(jobs),
            asdict(sizes),
            lambda index: run_job(jobs[index], out, verification, sizes),
            (MODULE,),
            verification,
            [job.describe() for job in jobs],
            "job",
        )

    return {name: analysis(name) for name in ("x6a", "x6b")}


# Declared statistics and readings -----------------------------------------------------


def wilson(covered: int, total: int) -> list[float] | None:
    """Wilson 95% interval of a coverage fraction."""
    if not total:
        return None
    z2 = POINTWISE_CRITICAL**2
    fraction = covered / total
    scale = 1 + z2 / total
    center = (fraction + z2 / (2 * total)) / scale
    half = (
        POINTWISE_CRITICAL
        * math.sqrt(fraction * (1 - fraction) / total + z2 / (4 * total**2))
        / scale
    )
    return [center - half, center + half]


def coverage(
    flags: Sequence[bool], *, complete_count: int | None = None
) -> dict[str, Any]:
    """Declared reading: adequate when the Wilson upper bound is at least 0.95,
    failure below 0.90, subnominal between; conservative when the lower bound
    exceeds 0.99; no reading below 100 complete repetitions."""
    covered, total = int(sum(flags)), len(flags)
    eligible = total if complete_count is None else complete_count
    interval = wilson(covered, total)
    reading = "no reading"
    if interval is not None and eligible >= MINIMUM_COMPLETE:
        reading = (
            "failure"
            if interval[1] < 0.90
            else "subnominal"
            if interval[1] < 0.95
            else "adequate"
        )
    return {
        "complete": eligible,
        "covered": covered,
        "total": total,
        "fraction": covered / total if total else None,
        "wilson95": interval,
        "reading": reading,
        "conservative": reading != "no reading"
        and interval is not None
        and interval[0] > 0.99,
    }


def contains(interval: Sequence[float] | None, value: float) -> bool:
    return interval is not None and interval[0] <= value <= interval[1]


def standardized(point: float, se: float, truth: float) -> float:
    """(logit p - logit T) / SE_logit with the frozen band's floor 1/(2n)."""
    epsilon = 1 / (2 * NETWORKS)
    p = min(max(point, epsilon), 1 - epsilon)
    t = min(max(truth, epsilon), 1 - epsilon)
    return (math.log(p / (1 - p)) - math.log(t / (1 - t))) / (
        max(se, epsilon) / (p * (1 - p))
    )


def z_summary(values: Sequence[float]) -> dict[str, Any] | None:
    if len(values) < 2:
        return None
    z = np.asarray(values)
    mean, sd = float(z.mean()), float(z.std(ddof=1))
    half = POINTWISE_CRITICAL * sd / math.sqrt(len(z))
    uncovered = (
        len(z) >= MINIMUM_COMPLETE
        and not -half <= mean <= half
        and abs(mean) > UNCOVERED_BIAS
    )
    return {
        "count": len(z),
        "mean": mean,
        "sd": sd,
        "mean_interval95": [mean - half, mean + half],
        "below_minus_1_96": float(np.mean(z < -POINTWISE_CRITICAL)),
        "above_1_96": float(np.mean(z > POINTWISE_CRITICAL)),
        "uncovered_bias": ("positive" if mean > 0 else "negative")
        if uncovered
        else None,
    }


def truth_summary(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """T_D1: mean of the successful truth pipelines, conditional on success."""
    cells = [record["cells"][0] for record in records]
    points = [cell["point"] for cell in cells if cell["success"] and "point" in cell]
    failed = len(records) - len(points)
    se = (
        float(np.std(points, ddof=1) / math.sqrt(len(points)))
        if len(points) > 1
        else None
    )
    return {
        "value": float(np.mean(points)) if points else None,
        "mcse": se,
        "pipelines": len(records),
        "successful": len(points),
        "gaps": sum(cell["success"] is False for cell in cells),
        "errors": sum(bool(record["error"]) for record in records),
        "retry_fraction": float(
            np.mean([cell["retry"] for cell in cells if "point" in cell])
        )
        if points
        else None,
        "failure_flag": failed > TRUTH_FAILURE_FLAG * len(records),
        "precision_met": se is not None and se <= TRUTH_SE_TARGET,
    }


def population_summary(record: Mapping[str, Any] | None) -> dict[str, Any]:
    """T_pop: mean of the trainings at theta*; its fit residual is not in the SE."""
    if record is None:
        return {"value": None, "mcse": None, "trainings": 0, "fit": None}
    aucs = record["trainings"]
    return {
        "value": float(np.mean(aucs)) if aucs else None,
        "mcse": float(np.std(aucs, ddof=1) / math.sqrt(len(aucs)))
        if len(aucs) > 1
        else None,
        "trainings": len(aucs),
        "success": record["success"],
        "error": record["error"],
        "fit": record["fit"],
    }


BY_CONSTRUCTION = {"value": 0.5, "mcse": 0.0, "by_construction": True}


def _moments(values: Sequence[float]) -> dict[str, Any] | None:
    if not values:
        return None
    array = np.asarray(values, dtype=float)
    return {
        "count": len(array),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "max": float(array.max()),
    }


def matching_bias(
    rows: Sequence[Mapping[str, Any]],
    truth: Mapping[str, Any],
    population: Mapping[str, Any],
) -> dict[str, Any] | None:
    """The five declared forms of the matching-bias component at one cell."""
    value = truth["value"]
    if value is None or len(rows) < 2:
        return None
    errors = np.array([row["point"] - value for row in rows])
    squares = np.array([row["se"] ** 2 for row in rows])
    residuals = np.array(
        [
            row["residual_se_units"]
            for row in rows
            if row["residual_se_units"] is not None
            and None not in row["residual_se_units"]
        ],
        dtype=float,
    )
    pop, pop_se = population.get("value"), population.get("mcse")
    return {
        "d5_mean_shift": _moments(
            [row["mean_shift"] for row in rows if row["mean_shift"] is not None]
        ),
        "empirical_bias": {
            "mean": float(errors.mean()),
            "mcse": None
            if truth["mcse"] is None
            else math.sqrt(
                float(errors.var(ddof=1)) / len(errors) + truth["mcse"] ** 2
            ),
        },
        "truth_d1_minus_pop": None
        if pop is None
        else {
            "value": value - pop,
            "se": None
            if truth["mcse"] is None or pop_se is None
            else math.hypot(truth["mcse"], pop_se),
        },
        "fit_residual_se_units": None
        if not len(residuals)
        else {
            "count": len(residuals),
            "mean": residuals.mean(0).tolist(),
            "sd": residuals.std(0, ddof=1).tolist() if len(residuals) > 1 else None,
            "mean_absolute": np.abs(residuals).mean(0).tolist(),
        },
        "amplification": _moments(
            [row["amplification"] for row in rows if row["amplification"] is not None]
        ),
        "mse_to_mean_se2": float(np.mean(errors**2) / squares.mean())
        if squares.mean() > 0
        else None,
    }


def _read(
    flags: Callable[[int], list[bool]],
    se: float | None,
    *,
    precision: bool,
    complete_count: int | None = None,
    gaps: int = 0,
) -> dict[str, Any]:
    """A coverage reading, redone at T -/+ 2 SE when SE(T_D1) exceeds 0.002."""
    result = coverage(flags(0) + [False] * gaps, complete_count=complete_count)
    if precision and se is None:
        result["truth_precision"] = {"available": False, "inconclusive": True}
        if result["reading"] != "no reading":
            result["nominal_reading"] = result["reading"]
            result["reading"] = "inconclusive-truth-precision"
        result["conservative"] = False
    if precision and se is not None and se > TRUTH_SE_TARGET:
        shifted = {
            name: coverage(flags(sign) + [False] * gaps, complete_count=complete_count)
            for name, sign in (("minus_2se", -1), ("plus_2se", 1))
        }
        result["truth_precision"] = {
            **{name: value["reading"] for name, value in shifted.items()},
            "conservative": {
                name: value["conservative"] for name, value in shifted.items()
            },
            "inconclusive": any(
                value[key] != result[key]
                for value in shifted.values()
                for key in ("reading", "conservative")
            ),
        }
        if result["truth_precision"]["inconclusive"]:
            result["nominal_reading"] = result["reading"]
            result["reading"] = "inconclusive-truth-precision"
            result["conservative"] = False
    return result


def _shifted(
    rows: Sequence[Mapping[str, Any]], key: str, value: float, se: float | None
) -> Callable[[int], list[bool]]:
    def flags(sign: int) -> list[bool]:
        return [contains(row.get(key), value + 2 * sign * (se or 0.0)) for row in rows]

    return flags


def _joint(
    repetitions: Sequence[Mapping[str, Any]], references: Sequence[Mapping[str, Any]]
) -> Callable[[int], list[bool]]:
    def flags(sign: int) -> list[bool]:
        return [
            all(
                contains(
                    cell.get("band"), ref["value"] + 2 * sign * (ref["mcse"] or 0.0)
                )
                for cell, ref in zip(rep["cells"], references, strict=True)
            )
            for rep in repetitions
        ]

    return flags


def strength_summary(
    rows: Sequence[Mapping[str, Any]],
    truth: Mapping[str, Any],
    population: Mapping[str, Any],
    band_rows: Sequence[Mapping[str, Any]] | None = None,
    *,
    unit_gaps: int | None = None,
) -> dict[str, Any]:
    """Pointwise (and band-interval) coverage of one cell against both truths.

    Primary denominators hold complete cells in X6b and complete units in X6a;
    secondary readings count gap repetitions as misses with the same minimum.
    A cell without an estimate that is not a gap is an error, outside both
    denominators.
    """
    complete = [row for row in rows if row["success"] and "point" in row]
    cell_complete = len(complete)
    if band_rows is not None:
        complete = list(band_rows)
    gaps = (
        sum(row["success"] is False for row in rows) if unit_gaps is None else unit_gaps
    )
    summary: dict[str, Any] = {
        "repetitions": len(rows),
        "complete": len(complete),
        "gaps": gaps,
        "cell_complete": cell_complete,
        "errors": len(rows) - len(complete) - gaps,
        "retry_fraction": float(np.mean([row["retry"] for row in complete]))
        if complete
        else None,
        "truth_d1": dict(truth),
        "truth_pop": dict(population),
    }
    for name, reference in (("d1", truth), ("pop", population)):
        value, se = reference["value"], reference["mcse"]
        if value is None:
            summary[f"vs_{name}"] = None
            continue
        primary = name == "d1"
        entry: dict[str, Any] = {
            "pointwise": _read(
                _shifted(complete, "pointwise", value, se), se, precision=primary
            ),
            "pointwise_gaps_as_misses": _read(
                _shifted(complete, "pointwise", value, se),
                se,
                precision=primary,
                complete_count=len(complete),
                gaps=gaps,
            ),
            "standardized_error": z_summary(
                [standardized(row["point"], row["se"], value) for row in complete]
            ),
        }
        bias = entry["standardized_error"]
        if primary and bias is not None and se is None:
            bias["truth_precision"] = {"available": False, "inconclusive": True}
            bias["nominal_uncovered_bias"] = bias["uncovered_bias"]
            bias["uncovered_bias"] = None
        if primary and bias is not None and se is not None and se > TRUTH_SE_TARGET:
            shifted = {}
            for name_shift, sign in (("minus_2se", -1), ("plus_2se", 1)):
                shifted_bias = z_summary(
                    [
                        standardized(row["point"], row["se"], value + 2 * sign * se)
                        for row in complete
                    ]
                )
                shifted[name_shift] = (
                    None if shifted_bias is None else shifted_bias["uncovered_bias"]
                )
            inconclusive = any(v != bias["uncovered_bias"] for v in shifted.values())
            bias["truth_precision"] = {**shifted, "inconclusive": inconclusive}
            if inconclusive:
                bias["nominal_uncovered_bias"] = bias["uncovered_bias"]
                bias["uncovered_bias"] = None
        if band_rows is not None:
            entry["band_interval"] = _read(
                _shifted(band_rows, "band", value, se), se, precision=primary
            )
        summary[f"vs_{name}"] = entry
    summary["matching_bias"] = matching_bias(complete, truth, population)
    return summary


def complete_units(repetitions: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [
        rep
        for rep in repetitions
        if not rep.get("error")
        and rep["curve"] is not None
        and rep["curve"]["band_complete"]
        and all(row["success"] and "point" in row for row in rep["cells"])
    ]


def band_summary(
    repetitions: Sequence[Mapping[str, Any]],
    truths: Sequence[Mapping[str, Any]],
    populations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Joint band coverage over every strength, a = 0 included.

    Primary: repetitions with a complete band. Secondary: every repetition with
    a curve, a band with a gap counting as a miss.
    """
    curves = [rep for rep in repetitions if rep["curve"] is not None]
    complete = complete_units(curves)
    summary: dict[str, Any] = {
        "with_curve": len(curves),
        "band_complete": len(complete),
        "empirical_max_t_above_floor": {
            "count": sum(rep["curve"]["empirical_exceeds_floor"] for rep in curves),
            "total": len(curves),
        },
        "band_reproduced": all(rep["curve"]["band_reproduced"] for rep in curves),
    }
    for name, references in (("d1", truths), ("pop", populations)):
        if any(reference["value"] is None for reference in references):
            summary[f"vs_{name}"] = None
            continue
        se = (
            None
            if any(reference["mcse"] is None for reference in references)
            else max(reference["mcse"] for reference in references)
        )
        summary[f"vs_{name}"] = {
            "primary": _read(_joint(complete, references), se, precision=name == "d1"),
            "gaps_as_misses": _read(
                _joint(complete, references),
                se,
                precision=name == "d1",
                complete_count=len(complete),
                gaps=len(curves) - len(complete),
            ),
        }
    return summary


def _grouped(
    records: Sequence[Mapping[str, Any]], kind: str
) -> dict[tuple[float, float] | None, list[Mapping[str, Any]]]:
    groups: dict[tuple[float, float] | None, list[Mapping[str, Any]]] = {}
    for record in records:
        job = record["job"]
        if job["kind"] == kind:
            cell = None if job["cell"] is None else (job["cell"][0], job["cell"][1])
            groups.setdefault(cell, []).append(record)
    return groups


def summarize(analysis: str, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    cells = X6A_TRUTH_CELLS if analysis == "x6a" else X6B_CELLS
    truth_groups = _grouped(records, "truth")
    pop_groups = _grouped(records, "pop")
    truths = {cell: truth_summary(truth_groups.get(cell, [])) for cell in cells}
    populations = {
        cell: population_summary(pop_groups[cell][0] if cell in pop_groups else None)
        for cell in cells
    }
    repetitions = _grouped(records, "repetition")
    result: dict[str, Any] = {
        "truths": [
            {"a": cell[0], "r": cell[1], "d1": truths[cell], "pop": populations[cell]}
            for cell in cells
        ]
    }
    if analysis == "x6b":
        result["cells"] = [
            {
                "a": cell[0],
                "r": cell[1],
                **strength_summary(
                    [rep["cells"][0] for rep in repetitions.get(cell, [])],
                    truths[cell],
                    populations[cell],
                ),
            }
            for cell in cells
        ]
        return result
    units = repetitions.get(None, [])
    references = [
        BY_CONSTRUCTION if a == 0 else truths[(a, X6A_RELIABILITY)] for a in GRID
    ]
    secondary = [
        BY_CONSTRUCTION if a == 0 else populations[(a, X6A_RELIABILITY)] for a in GRID
    ]
    band_complete = complete_units(units)
    unit_gaps = sum(rep["curve"] is not None for rep in units) - len(band_complete)
    result["strengths"] = [
        {
            "a": a,
            "r": X6A_RELIABILITY,
            **strength_summary(
                [rep["cells"][i] for rep in units],
                references[i],
                secondary[i],
                [rep["cells"][i] for rep in band_complete],
                unit_gaps=unit_gaps,
            ),
        }
        for i, a in enumerate(GRID)
    ]
    result["band"] = band_summary(units, references, secondary)
    result["repetitions"] = {
        "recorded": len(units),
        "errors": sum(bool(rep["error"]) for rep in units),
        "with_gap": sum(rep["success"] is False for rep in units),
    }
    return result


def aggregate_x6(outs: Sequence[Path], sizes: X6Sizes = DECLARED) -> dict[str, Any]:
    """X6 after the confirmatory release, from the sealed per-unit records."""
    release = f.require_release()
    sources: dict[str, dict[str, Any]] = {}
    sections: dict[str, Any] = {}
    everything: list[dict[str, Any]] = []
    for name in ("x6a", "x6b"):
        jobs = queue(name, sizes)
        records, incomplete, accepted_sources = f.union_complete_records(
            outs,
            name,
            len(jobs),
            asdict(sizes),
            identities=[job.describe() for job in jobs],
            identity_key="job",
            preconditions=SUITE.preconditions,
        )
        for source in accepted_sources:
            key = source["out"]
            if key in sources:
                sources[key]["accepted_units"] += source["accepted_units"]
            else:
                sources[key] = source
        values = [records[index] for index in sorted(records)]
        everything += values
        sections[name] = {
            "units": len(jobs),
            "recorded": len(values),
            "incomplete_units": incomplete,
            "timing": f.timing_summary(values),
            **summarize(name, values),
        }
    return {
        "schema": AGGREGATE_SCHEMA,
        "label": f.LABEL,
        "declaration": f.declaration_digests(),
        "release": release,
        "sources": list(sources.values()),
        "sizes": asdict(sizes),
        "seeds": SEEDS,
        "pointwise_critical": POINTWISE_CRITICAL,
        "truth_se_target": TRUTH_SE_TARGET,
        "minimum_complete_repetitions": MINIMUM_COMPLETE,
        "verification_sha256": [
            json.loads(value)
            for value in sorted(
                {
                    json.dumps(r["verification_sha256"], sort_keys=True)
                    for r in everything
                }
            )
        ],
        "code": f.shared_provenance(everything, "code"),
        "host": f.shared_provenance(everything, "host"),
        **sections,
    }


# Timing probe and command line ------------------------------------------------------


@dataclass(frozen=True)
class _ProbePlan(SeedPlan):
    def seed(self, phase: str, role: str, index: int, *, attempt: int = 0) -> int:
        return f.probe_seed(role, index)


def probe(count: int) -> dict[str, Any]:
    """CPU seconds per frozen panel and AUC, seeds outside every namespace.

    Unit estimates use the declared panel counts: an interior cell has 13,072
    social and about 37,800 null panels, an anchor-exact cell 9,072 of each,
    and the T_pop fit 23.2 evaluations of 16,384 null panels.
    """
    source = PanelSource(Cell(0.3, X6A_RELIABILITY), _ProbePlan())
    theta = np.array([0.85, 0.1])
    null = f.cpu_per_call(
        lambda j: source.profiles("check", 1, parameters=theta, start=j), count
    )
    social = f.cpu_per_call(lambda j: source.profiles("check", 1, start=j), count)
    scores = np.random.default_rng(f.probe_seed("state", 0)).normal(size=(2, 4000))
    per_auc = f.cpu_per_call(lambda _: auc(scores[0], scores[1]), 50 * count)

    def panels(counts: Mapping[str, float]) -> float:
        return counts["social"] * social + counts["null"] * null

    interior, anchor = panels(INTERIOR_PANELS), panels(ANCHOR_PANELS)
    grid = len(GRID)
    trainings = DECLARED.population_train + DECLARED.population_check
    estimates = {
        "x6a-repetition": anchor
        + (grid - 1) * interior
        + 2 * NETWORKS * grid * per_auc,
        "truth-pipeline": interior,
        "x6b-repetition": interior + NETWORKS * per_auc,
        "population-fit": DECLARED.population_pairs * (social + FIT_EVALUATIONS * null),
        "population-trainings": DECLARED.population_trainings
        * trainings
        * (social + null),
    }
    return {
        "size": SIZE,
        "count": count,
        "cpu_seconds_per_panel": {"null-B": null, "frozen-social": social},
        "cpu_seconds_per_auc": per_auc,
        "unit_cpu_hours": {key: value / 3600 for key, value in estimates.items()},
    }


SUITE = f.Suite(
    "x6",
    True,
    ("x6a", "x6b"),
    (PRECONDITION,),
    analyses,
    lambda out: aggregate_x6([out]),
    probe,
    (MODULE,),
    aggregate_union=aggregate_x6,
)


def main(argv: list[str] | None = None) -> int:
    return f.main(SUITE, argv)


if __name__ == "__main__":
    raise SystemExit(main())
