"""Exploratory X4: single-panel power by parametric bootstrap (R2-M2 with R2-M3).

Declared on 2026-09-28 in
``experiments/exploratory/detection-boundary-v4-exploratory/README-x3-x7.md``
before any confirmatory result. In each tier-1 cell the frozen part runs as
frozen ``pipeline`` runs it, on the successor seed plan: frozen ``fit_cell``,
the frozen train phase and LDA on L3 to L5 (the oracle direction), the frozen
check phase with the reference AUC and the null scores, then 1,000 fresh
interaction panels in phase ``test``. X4a rejects B when a test score exceeds
the 0.95 quantile of the check null scores (81 cells). X4b fits B to the L1 and
L2 of one test panel alone with frozen ``profile_match`` on analyst panels of
frozen ``PanelSource`` and rejects it with a parametric bootstrap of 199 null
panels (the first 200 test panels of 27 cells). Every stream comes from the
``v4-exploratory-x3-x7`` namespace. Results stay sealed until the
confirmatory release and are never promoted to confirmatory evidence.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from functools import partial
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ic_study.analysis.detection_boundary import auc, feasible_lag1
from ic_study.analysis.detection_boundary_v4 import ProfileFit, profile_match
from ic_study.analysis.redesign import Discriminant, fit_discriminant
from ic_study.models.anchored_panel import Floats
from ic_study.simulation import v4_exploratory_x3 as x3
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation.detection_v4 import (
    Cell,
    PanelSource,
    SeedPlan,
    ValidatedFit,
    fit_cell,
)
from ic_study.simulation.v4_exploratory import SIZE
from ic_study.simulation.v4_store import SealedStore

MODULES = (Path(__file__).resolve(), *x3.MODULES)
UNITS = f.tier1_units("x4")
CELLS = tuple((unit, index) for unit in UNITS for index in range(len(unit.cells)))
SINGLE_RELIABILITIES = (0.5, 0.7, 0.9)
SINGLE_CELLS = tuple(
    (unit, index)
    for unit, index in CELLS
    if unit.cells[index].reliability in SINGLE_RELIABILITIES
)
FIT_CELLS = ((0.03, 0.5), (0.3, 0.6))
LEVEL = 0.05
NORMAL_CRITICAL = 1.6449
STRIDE = 1000
MARGIN = 0.05
AUC_RANGE = (0.55, 0.95)
CRITICAL_RULE = (
    "NumPy default (linear) 0.95 quantile of the 4,000 check null scores; "
    "a test panel rejects B when its score is strictly above it"
)
P_VALUE_RULE = (
    "p = (1 + #{null scores >= observed score}) / (nulls + 1); reject when "
    "p <= 0.05; a failed single-panel fit is a non-rejection"
)
SINGLE_INDEX = (
    "analyst panel j = 1000 * test panel + simulated panel in the frozen "
    "uncoupled null layout (seed index 2j), phases single-fit and single-null"
)


@dataclass(frozen=True)
class X4Sizes:
    size: int = SIZE
    train: int = 2000
    check: int = 4000
    test: int = 1000
    single: int = 200
    analyst: int = 256
    nulls: int = 199
    auc_resamples: int = 1000
    power_resamples: int = 2000


DECLARED = X4Sizes()


# Frozen part and the single-panel fitting wrapper -------------------------------


@dataclass(frozen=True)
class Reference:
    """The frozen part of one X4 cell; empty after a failed frozen fit."""

    fit: ValidatedFit
    model: Discriminant | None = None
    null_check: Floats | None = None
    social_check: Floats | None = None
    test: Floats | None = None
    test_scores: Floats | None = None


def reference(
    cell: Cell, seeds: SeedPlan, store: SealedStore | None, sizes: X4Sizes
) -> Reference:
    """Frozen ``fit_cell``, train, LDA and check as frozen ``pipeline`` calls
    them, then the interaction panels of phase ``test``."""
    source = PanelSource(cell, seeds, size=sizes.size, store=store)
    fit = fit_cell(source)
    if not fit.success:
        return Reference(fit)
    parameters = fit.final.fit.parameters
    train0 = source.profiles("train", sizes.train, parameters=parameters)[:, 2:5]
    train1 = source.profiles("train", sizes.train)[:, 2:5]
    model = fit_discriminant(
        np.concatenate([train0, train1]), np.repeat([0, 1], sizes.train)
    )
    null_check = model.score(
        source.profiles("check", sizes.check, parameters=parameters)[:, 2:5]
    )
    social_check = model.score(source.profiles("check", sizes.check)[:, 2:5])
    test = source.profiles("test", sizes.test)
    return Reference(
        fit, model, null_check, social_check, test, model.score(test[:, 2:5])
    )


def single_panel_fit(
    cell: Cell, target: Floats, evaluate: Callable[[float, float], Floats]
) -> ProfileFit:
    """Frozen ``fit_cell``'s first-attempt solve for a tier-1 cell, no validation.

    The frozen continuous-channel check on the target's mean L1, then frozen
    ``profile_match`` with the frozen arguments and budget.
    """
    mean = float(target[:, 0].mean())
    if not feasible_lag1(
        mean, cell.reliability, error_correlation=cell.error_correlation
    ):
        return ProfileFit(
            np.array([0.85, 0.0]),
            np.zeros_like(target),
            np.zeros(2),
            np.zeros(2),
            np.zeros(2),
            0,
            "family-limit-upper" if mean > 0 else "family-limit-lower",
            2,
        )
    return profile_match(target, evaluate, identity=cell.identity)


# Statistics --------------------------------------------------------------------


def normal_power(area: float) -> float:
    """R2-M3's normal-theory power: Phi(sqrt(2) Phi^-1(AUC) - 1.6449)."""
    if not 0 < area < 1:
        return float(area >= 1)
    normal = NormalDist()
    return normal.cdf(math.sqrt(2) * normal.inv_cdf(area) - NORMAL_CRITICAL)


def critical_score(null_scores: Floats) -> float:
    return float(np.quantile(null_scores, 1 - LEVEL))


def rate_bootstrap(
    decisions: Sequence[NDArray[np.bool_]], *, seed: int, resamples: int
) -> Floats:
    """Rejection-rate replicates over test networks of two events, paired.

    Every decision set is resampled with the same network indices.
    """
    rows = [
        np.asarray(decision, dtype=np.float64).reshape(-1, 2) for decision in decisions
    ]
    if len({len(row) for row in rows}) != 1:
        raise ValueError("Paired decisions need the same test networks")
    networks = len(rows[0])
    rng = np.random.default_rng(seed)
    draws = np.empty((resamples, len(rows)))
    for b in range(resamples):
        indices = rng.integers(networks, size=networks)
        draws[b] = [row[indices].mean() for row in rows]
    return draws


def _oracle(frozen: Reference) -> NDArray[np.bool_]:
    if frozen.null_check is None or frozen.test_scores is None:
        raise ValueError("A failed frozen fit leaves the cell without X4")
    return np.asarray(frozen.test_scores > critical_score(frozen.null_check))


def x4a_statistics(
    frozen: Reference, seeds: SeedPlan, sizes: X4Sizes
) -> dict[str, Any]:
    if frozen.null_check is None or frozen.social_check is None:
        raise ValueError("A failed frozen fit leaves the cell without X4")
    reject = _oracle(frozen)
    networks = sizes.check // 2
    area = auc(frozen.null_check, frozen.social_check)
    areas = f.paired_network_bootstrap(
        [
            (
                frozen.null_check.reshape(networks, 2),
                frozen.social_check.reshape(networks, 2),
            )
        ],
        seed=seeds.seed("bootstrap", "resample", 0),
        resamples=sizes.auc_resamples,
    )[:, 0]
    interval = f.percentile_interval(areas)
    power = rate_bootstrap(
        [reject],
        seed=seeds.seed("bootstrap", "resample", 1),
        resamples=sizes.power_resamples,
    )[:, 0]
    return {
        "auc_ref": area,
        "auc_ref_interval_95": interval,
        "normal_theory_power": {
            "at_auc_ref": normal_power(area),
            "at_interval_95": [normal_power(value) for value in interval],
        },
        "critical_score": critical_score(frozen.null_check),
        "critical_rule": CRITICAL_RULE,
        "test_panels": len(reject),
        "rejections": int(reject.sum()),
        "power_or": float(reject.mean()),
        "power_or_interval_95": f.percentile_interval(power),
    }


def single_panel(
    cell: Cell, seeds: SeedPlan, frozen: Reference, panel: int, sizes: X4Sizes
) -> dict[str, Any]:
    """X4b on one test panel: B fitted to its L1 and L2 alone, then the
    parametric bootstrap with the oracle LDA."""
    if frozen.model is None or frozen.test is None or frozen.test_scores is None:
        raise ValueError("A failed frozen fit leaves the cell without X4")
    analyst = PanelSource(cell, seeds, size=sizes.size)
    start = STRIDE * panel
    target = np.repeat(frozen.test[panel : panel + 1, :2], sizes.analyst, axis=0)

    def evaluate(phi: float, eta: float) -> Floats:
        return analyst.profiles(
            "single-fit", sizes.analyst, parameters=np.array([phi, eta]), start=start
        )[:, :2]

    fit = single_panel_fit(cell, target, evaluate)
    record: dict[str, Any] = {
        "panel": panel,
        "status": fit.status,
        "evaluations": fit.evaluations,
        "success": fit.success,
        "parameters": x3.finite(fit.parameters),
        "residual_se_units": x3.se_units(fit.residual, fit.se),
        "exceedances": None,
        "p_value": None,
        "reject": False,
    }
    if not fit.success:
        return record
    scores = frozen.model.score(
        analyst.profiles(
            "single-null", sizes.nulls, parameters=fit.parameters, start=start
        )[:, 2:5]
    )
    exceedances = int(np.sum(scores >= frozen.test_scores[panel]))
    p_value = (1 + exceedances) / (sizes.nulls + 1)
    return {
        **record,
        "exceedances": exceedances,
        "p_value": p_value,
        "reject": p_value <= LEVEL,
    }


def x4b_statistics(
    cell: Cell, seeds: SeedPlan, frozen: Reference, store: SealedStore, sizes: X4Sizes
) -> dict[str, Any]:
    """P_pu over the first test panels, paired with their X4a decisions.

    Each panel's record is a checkpoint of the cell store, so an interrupted
    cell resumes at the next panel.
    """
    panels = []
    for panel in range(sizes.single):
        key = f"panel-{panel:03d}"
        record = store.get_json(key)
        if record is None:
            record = single_panel(cell, seeds, frozen, panel, sizes)
            store.put_json(key, record)
        panels.append(record)
    reject = np.array([bool(p["reject"]) for p in panels])
    success = np.array([bool(p["success"]) for p in panels])
    oracle = _oracle(frozen)[: sizes.single]
    draws = rate_bootstrap(
        [reject, oracle],
        seed=seeds.seed("bootstrap", "resample", 2),
        resamples=sizes.power_resamples,
    )
    statuses: dict[str, int] = {}
    for p in panels:
        statuses[str(p["status"])] = statuses.get(str(p["status"]), 0) + 1
    return {
        "test_panels": sizes.single,
        "p_value_rule": P_VALUE_RULE,
        "single_index": SINGLE_INDEX,
        "fit_statuses": statuses,
        "fit_failures": int((~success).sum()),
        "failure_rate": float((~success).mean()),
        "power_pu": float(reject.mean()),
        "power_pu_interval_95": f.percentile_interval(draws[:, 0]),
        "power_pu_without_failures": float(reject[success].mean())
        if success.any()
        else None,
        "power_or_paired": float(oracle.mean()),
        "power_or_paired_interval_95": f.percentile_interval(draws[:, 1]),
        "difference": float(reject.mean() - oracle.mean()),
        "difference_interval_95": f.percentile_interval(draws[:, 0] - draws[:, 1]),
        "panels": panels,
    }


# Cell records ------------------------------------------------------------------


def frozen_record(frozen: Reference) -> dict[str, Any]:
    return {
        "success": frozen.fit.success,
        "attempts": [attempt.fit.status for attempt in frozen.fit.attempts],
        "fit": x3.known_record(frozen.fit),
    }


def _seeds(seeds: SeedPlan, sizes: X4Sizes) -> dict[str, Any]:
    return {
        "bootstrap_auc_ref": seeds.seed("bootstrap", "resample", 0),
        "bootstrap_power_or": seeds.seed("bootstrap", "resample", 1),
        "bootstrap_paired": seeds.seed("bootstrap", "resample", 2),
        "auc_resamples": sizes.auc_resamples,
        "power_resamples": sizes.power_resamples,
        "single_index": SINGLE_INDEX,
    }


def x4a_result(
    cell: Cell, seeds: SeedPlan, store: SealedStore | None, *, sizes: X4Sizes
) -> dict[str, Any]:
    frozen = reference(cell, seeds, store, sizes)
    result = frozen_record(frozen)
    if frozen.model is None:
        return {**result, "x4a": None, "seeds": None}
    return {
        **result,
        "x4a": x4a_statistics(frozen, seeds, sizes),
        "seeds": _seeds(seeds, sizes),
    }


def x4b_result(
    cell: Cell, seeds: SeedPlan, store: SealedStore, *, sizes: X4Sizes
) -> dict[str, Any]:
    frozen = reference(cell, seeds, store, sizes)
    result = frozen_record(frozen)
    if frozen.model is None:
        return {**result, "x4b": None, "seeds": None}
    statistics = x4b_statistics(cell, seeds, frozen, store, sizes)
    return {
        **result,
        "attempts": result["attempts"]
        + [f"single:{p['status']}" for p in statistics["panels"]],
        "x4b": statistics,
        "seeds": _seeds(seeds, sizes),
    }


def x4a_cell(
    index: int, out: Path, digests: Mapping[str, str], sizes: X4Sizes = DECLARED
) -> dict[str, Any]:
    unit, position = CELLS[index]
    compute = partial(x4a_result, unit.cells[position], unit.seeds, sizes=sizes)
    return x3.cell_record(
        "x4a", index, unit, position, out, digests, asdict(sizes), compute
    )


def x4b_cell(
    index: int, out: Path, digests: Mapping[str, str], sizes: X4Sizes = DECLARED
) -> dict[str, Any]:
    unit, position = SINGLE_CELLS[index]
    compute = partial(x4b_result, unit.cells[position], unit.seeds, sizes=sizes)
    return x3.cell_record(
        "x4b", index, unit, position, out, digests, asdict(sizes), compute
    )


def analyses(
    out: Path, digests: Mapping[str, str], sizes: X4Sizes = DECLARED
) -> dict[str, f.Analysis]:
    return {
        "x4a": f.Analysis(
            "x4a",
            len(CELLS),
            asdict(sizes),
            partial(x4a_cell, out=out, digests=digests, sizes=sizes),
            MODULES,
            digests,
            [x3.cell_identity(i, u, p) for i, (u, p) in enumerate(CELLS)],
        ),
        "x4b": f.Analysis(
            "x4b",
            len(SINGLE_CELLS),
            asdict(sizes),
            partial(x4b_cell, out=out, digests=digests, sizes=sizes),
            MODULES,
            digests,
            [x3.cell_identity(i, u, p) for i, (u, p) in enumerate(SINGLE_CELLS)],
        ),
    }


# Bitwise precondition -------------------------------------------------------------


def wrapper_first_fit(
    unit: f.SuccessorUnit, index: int, directory: Path, size: int
) -> None:
    """Successor side of ``x4-fit``: the X4 fitting wrapper on the frozen coupled
    target and the frozen evaluation at M = 1,024."""

    def compute() -> tuple[int, ProfileFit]:
        cell = unit.cells[index]
        source = PanelSource(cell, unit.seeds, size=size)
        target = source.profiles("match", x3.MATCHING, attempt=0)[:, :2]

        def evaluate(phi: float, eta: float) -> Floats:
            return source.profiles(
                "match", x3.MATCHING, parameters=np.array([phi, eta]), attempt=0
            )[:, :2]

        return x3.MATCHING, single_panel_fit(cell, target, evaluate)

    x3.write_fit_record(directory, compute)


FIT = f.Precondition(
    "x4-fit",
    UNITS,
    FIT_CELLS,
    wrapper_first_fit,
    x3.frozen_first_fit,
    MODULES,
    x3.FIT_RULE,
)


# Aggregate after the release ----------------------------------------------------------


def size_reading(interval: Sequence[float]) -> str:
    lower, upper = interval
    if lower > LEVEL:
        return "liberal"
    if upper < LEVEL:
        return "conservative"
    return "calibrated"


def normal_reading(power: float, interval: Sequence[float]) -> str:
    lower, upper = interval
    if power > upper:
        return "overstates"
    if power < lower:
        return "understates"
    return "describes"


def single_panel_reading(interval: Sequence[float]) -> str:
    lower, upper = interval
    if upper < 0:
        return "removes-power"
    if lower >= -MARGIN and upper <= MARGIN:
        return "no-material-change"
    return "inconclusive"


def _sizes_by_r(
    records: Sequence[Mapping[str, Any]], kind: str, key: str
) -> dict[float, str | None]:
    readings: dict[float, str | None] = {}
    for record in records:
        if record["cell"]["a"] != 0:
            continue
        statistics = record.get(kind)
        readings[record["cell"]["r"]] = (
            None if not statistics else size_reading(statistics[key])
        )
    return readings


def aggregate(outs: Sequence[Path], sizes: X4Sizes = DECLARED) -> dict[str, Any]:
    release = f.require_release()
    loaded = {}
    sources: dict[str, dict[str, Any]] = {}
    for kind, cells in (("x4a", CELLS), ("x4b", SINGLE_CELLS)):
        records, incomplete, accepted_sources = f.union_complete_records(
            outs,
            kind,
            len(cells),
            asdict(sizes),
            preconditions=SUITE.preconditions,
            identities=[x3.cell_identity(i, u, p) for i, (u, p) in enumerate(cells)],
        )
        for source in accepted_sources:
            key = source["out"]
            if key in sources:
                sources[key]["accepted_units"] += source["accepted_units"]
            else:
                sources[key] = source
        loaded[kind] = ([records[index] for index in sorted(records)], incomplete)
    x4a, x4b = loaded["x4a"][0], loaded["x4b"][0]
    size = {
        "x4a": _sizes_by_r(x4a, "x4a", "power_or_interval_95"),
        "x4b": _sizes_by_r(x4b, "x4b", "power_pu_interval_95"),
    }
    x4a_cells, x4b_cells = [], []
    normal: dict[str, int] = {}
    for record in x4a:
        statistics = record.get("x4a")
        reading = None
        if statistics:
            reading = normal_reading(
                statistics["normal_theory_power"]["at_auc_ref"],
                statistics["power_or_interval_95"],
            )
            if AUC_RANGE[0] <= statistics["auc_ref"] <= AUC_RANGE[1]:
                normal[reading] = normal.get(reading, 0) + 1
        x4a_cells.append(
            {
                **{k: v for k, v in record.items() if k != "provenance"},
                "normal_theory_reading": reading,
            }
        )
    effects: dict[str, int] = {}
    for record in x4b:
        statistics = record.get("x4b")
        flag = size["x4b"].get(record["cell"]["r"])
        reading = None
        if statistics and flag in ("calibrated", "conservative"):
            reading = single_panel_reading(statistics["difference_interval_95"])
            effects[reading] = effects.get(reading, 0) + 1
        x4b_cells.append(
            {
                **{k: v for k, v in record.items() if k != "provenance"},
                "single_panel_reading": reading,
                "size_flag": flag,
                "quantity": "power"
                if flag == "calibrated"
                else "power-lower-bound"
                if flag == "conservative"
                else "rejection-rate",
            }
        )
    values = x4a + x4b
    return {
        "schema": "ic-study.v4-exploratory-x4.v1",
        "label": f.LABEL,
        "declaration": f.declaration_digests(),
        "release": release,
        "sources": list(sources.values()),
        "sizes": asdict(sizes),
        "incomplete": {kind: loaded[kind][1] for kind in loaded},
        "summary": {
            "size_at_a0": {
                kind: {str(r): v for r, v in readings.items()}
                for kind, readings in size.items()
            },
            "normal_theory_in_auc_range": {"range": list(AUC_RANGE), **normal},
            "single_panel_effect": {"margin": MARGIN, **effects},
            "oracle": "both powers bound from above an analyst who estimates "
            "the direction; nothing about the optimal single-panel test",
        },
        "rules": {"critical": CRITICAL_RULE, "p_value": P_VALUE_RULE},
        "seeds": {**f.SEEDS, "analysis": "x4", "single_index": SINGLE_INDEX},
        "code": f.shared_provenance(values, "code"),
        "host": f.shared_provenance(values, "host"),
        "timing": f.timing_summary(values),
        "x4a": x4a_cells,
        "x4b": x4b_cells,
    }


# Timing probe ------------------------------------------------------------------------


def cell_panels(
    inner: float = x3.NOMINAL["inner_evaluations"], single_inner: float = 23
) -> dict[str, dict[str, float]]:
    """Null and social panels of one X4a and one X4b cell without retries."""
    fit = inner * x3.MATCHING + x3.VALIDATION + 3 * x3.MATCHING
    frozen = {
        "null": fit + DECLARED.train + DECLARED.check,
        "social": x3.MATCHING
        + x3.VALIDATION
        + DECLARED.train
        + DECLARED.check
        + DECLARED.test,
    }
    single = DECLARED.single * (single_inner * DECLARED.analyst + DECLARED.nulls)
    return {"x4a": frozen, "x4b": {**frozen, "null": frozen["null"] + single}}


def probe(count: int) -> dict[str, Any]:
    rates = x3.panel_rates(count)
    panels = cell_panels()
    hours = {
        kind: (
            counts["null"] * rates["null_panel_cpu_seconds"]
            + counts["social"] * rates["social_panel_cpu_seconds"]
        )
        / 3600
        for kind, counts in panels.items()
    }
    return {
        "count": count,
        **rates,
        "nominal_cell_panels": panels,
        "nominal_cell_cpu_hours": hours,
    }


SUITE = f.Suite(
    "x4",
    True,
    ("x4a", "x4b"),
    (FIT,),
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
