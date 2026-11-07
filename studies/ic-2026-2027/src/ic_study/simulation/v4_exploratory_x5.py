"""Exploratory X5: the frozen pipeline against a misspecified observed channel.

Declared on 2026-09-28 in
``experiments/exploratory/detection-boundary-v4-exploratory/README-x3-x7.md``
(objection R2-M5). At a = 0 the data arm is the frozen interaction arm, the
rank-transported AR(0.85) path identical to B(0.85, 0), observed through a
channel that departs from the assumed one in one declared way. The null is
frozen B with the assumed channel (constant r, MCAR household mask with
retention 0.89), fitted by frozen ``fit_cell`` to the data arm's L1 and L2;
validation, D4 retry, training, checking, reference and D5 nuisance are the
frozen pipeline as ``execute_cell`` calls it. The successor source swaps only
the data arm's channel. With every departure at zero it is the frozen source
bit for bit, which the declared precondition checks on four cells. X5
estimates no point of the curve and is readable when complete.
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ic_study.analysis.detection_boundary_v4 import score_uncertainty
from ic_study.models.anchored_panel import Floats
from ic_study.models.detection_panel import (
    measurement,
    ordinal_channel,
    tenure_reliability,
)
from ic_study.models.detection_panel_v4 import null
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation.detection_v4 import Cell, PanelSource, selected_features
from ic_study.simulation.v4_exploratory import (
    SIZE,
    WAVES,
    observed_profile,
    utc_now,
)
from ic_study.simulation.v4_exploratory_x1b import ensure_provenance, original_generator
from ic_study.simulation.v4_store import SealedStore

MODULE = Path(__file__).resolve()
RETENTION = 0.89
PRECONDITION_CELLS = ((0.0, 0.5), (0.0, 0.9), (0.03, 0.5), (0.3, 0.6))
POINTWISE_CRITICAL = 1.96
FROZEN_CRITICAL = 2.7729
PRIMARY, SECONDARY = 0.70, 0.60
FIT_FAILURE = (
    "the correctly specified B does not reproduce the misspecified L1 and L2 "
    "at this r; information, not an AUC"
)


@dataclass(frozen=True)
class Channel:
    """Departures of the data arm's channel; all zero is the assumed channel.

    ``trend`` gives r_t = r + A (t - 5) / 5, ``step`` gives r - A before wave 5
    and r + A from it, ``tenure`` is the frozen tenure gain in the data arm
    only and ``attrition`` is beta of the trust-dependent household retention.
    """

    name: str
    trend: float = 0.0
    step: float = 0.0
    tenure: float = 0.0
    attrition: float = 0.0


NEUTRAL = Channel("neutral")
CONDITIONS = (
    Channel("trend-003", trend=0.03),
    Channel("trend-008", trend=0.08),
    Channel("step-003", step=0.03),
    Channel("step-008", step=0.08),
    Channel("tenure-010", tenure=0.1),
    Channel("tenure-020", tenure=0.2),
    Channel("mnar-ln15", attrition=math.log(1.5)),
    Channel("mnar-ln2", attrition=math.log(2)),
)


# Misspecified channel -----------------------------------------------------------


def retention_probabilities(
    zbar: Floats, active: NDArray[np.bool_], beta: float, retention: float = RETENTION
) -> Floats:
    """logit p = alpha + beta zbar, with the active mean of p equal to ``retention``.

    Alpha comes from a safeguarded Newton inside the bracket that the extreme
    zbar fixes.
    """
    z = zbar[active]
    centre = math.log(retention / (1 - retention))
    spread = abs(beta) * float(np.max(np.abs(z), initial=0.0))
    lo, hi, alpha = centre - spread, centre + spread, centre
    for _ in range(200):
        p = 1 / (1 + np.exp(-(alpha + beta * z)))
        gap = float(p.mean()) - retention if len(z) else 0.0
        if gap == 0:
            break
        if gap < 0:
            lo = alpha
        else:
            hi = alpha
        trial = alpha - gap / float(np.mean(p * (1 - p)))
        following = trial if lo < trial < hi else (lo + hi) / 2
        if following == alpha:
            break
        alpha = following
    return np.asarray(1 / (1 + np.exp(-(alpha + beta * zbar))), dtype=np.float64)


def attrition_mask(
    latent: Floats, seed: int, *, beta: float, retention: float = RETENTION
) -> NDArray[np.bool_]:
    """Frozen ``panel_mask`` with trust-dependent household retention.

    The uniforms are those of ``panel_mask``, same seed and draw order. A
    household active at t - 1 stays at t when its uniform is below p_ht, with
    zbar the mean latent state of its two members at t - 1. Entries at waves 0
    and 5 and permanent exit are unchanged; beta = 0 is the frozen comparison
    with the retention itself.
    """
    waves, size = latent.shape
    if size % 6 or waves < 6 or not 0 <= retention <= 1:
        raise ValueError("Require size divisible by six and at least six waves")
    rng = np.random.default_rng(seed)
    households = size // 2
    entry = np.where(np.arange(households) < size // 3, 0, 5)
    active = np.zeros(households, dtype=bool)
    mask = []
    for wave in range(waves):
        uniforms = rng.random(households)
        threshold: float | Floats = retention
        if beta and wave:
            pairs = latent[wave - 1].reshape(households, 2).mean(1)
            threshold = retention_probabilities(pairs, active, beta, retention)
        active &= uniforms < threshold
        active |= entry == wave
        mask.append(np.repeat(active, 2))
    return np.stack(mask)


def wave_reliability(
    mask: NDArray[np.bool_], reliability: float, channel: Channel
) -> Floats:
    """Per-wave and per-person signal share of the data arm's channel."""
    waves = np.arange(len(mask), dtype=np.float64)
    offset = channel.trend * (waves - 5) / 5
    offset = offset + channel.step * np.where(waves >= 5, 1.0, -1.0)
    return tenure_reliability(mask, reliability, channel.tenure) + offset[:, None]


def data_profile(
    latent: Floats,
    reliability: float,
    mask_seed: int,
    error_seed: int,
    channel: Channel,
) -> Floats:
    """The data arm's observed row; the neutral channel is the frozen one."""
    if latent.shape[0] != WAVES:
        raise ValueError("Tier-1 panels have eleven waves")
    mask = attrition_mask(latent, mask_seed, beta=channel.attrition)
    measured = measurement(
        latent,
        wave_reliability(mask, reliability, channel),
        error_seed,
        heteroscedastic=False,
        error_correlation=0,
    )
    observed = ordinal_channel(measured, mask, midpoint_mass=0, heap_seed=None)
    return selected_features(
        latent, observed, channel="observed", mobility=False, midpoint_mass=0
    )


def misspecified_social(channel: Channel) -> f.SocialProfile:
    def social(
        cell: Cell, size: int, seed: f.SeedFn, index: int, coupled: bool
    ) -> Floats:
        latent = original_generator(cell, size, seed, index, coupled)
        return data_profile(
            latent, cell.reliability, seed("mask", index), seed("error", index), channel
        )

    return social


def x5_source(channel: Channel) -> f.SourceFactory:
    social = misspecified_social(channel)

    def source(
        cell: Cell, seeds: f.SuccessorSeedPlan, store: SealedStore, size: int
    ) -> PanelSource:
        return f.SuccessorSource(cell, seeds, social=social, size=size, store=store)

    return source


# Units, precondition and cells ------------------------------------------------------


def x5_units() -> tuple[f.SuccessorUnit, ...]:
    return f.tier1_units("x5")


def x5_cells() -> tuple[tuple[f.SuccessorUnit, Channel], ...]:
    """Eight conditions within each r; the conditions of one r share streams."""
    return tuple((unit, channel) for unit in x5_units() for channel in CONDITIONS)


def neutral_executor(
    unit: f.SuccessorUnit, index: int, directory: Path, size: int
) -> None:
    f.execute_source_cell(unit, index, directory, x5_source(NEUTRAL), size=size)


PRECONDITION = f.Precondition(
    "x5", x5_units(), PRECONDITION_CELLS, neutral_executor, modules=(MODULE,)
)


@dataclass(frozen=True)
class X5Sizes:
    size: int = SIZE


DECLARED_X5 = X5Sizes()


def misspecification(
    unit: f.SuccessorUnit,
    channel: Channel,
    store: SealedStore,
    result: Mapping[str, Any],
    size: int,
) -> dict[str, Any]:
    """Frozen ``score_uncertainty`` on the stored arrays with the plan's
    bootstrap seed, as the pipeline computes it with ``compute_uncertainty``,
    and the mean lags of the stored check panels."""
    arrays = {key: store.get_array(key) for key in ("scores0", "scores1", "nuisance")}
    if any(value is None for value in arrays.values()):
        raise ValueError("Successful cell has missing numerical checkpoints")
    scores0, scores1, nuisance = (np.asarray(value) for value in arrays.values())
    uncertainty = score_uncertainty(
        scores0.reshape(2000, 2, 1),
        scores1.reshape(2000, 2, 1),
        nuisance[:, None],
        seed=unit.seeds.seed("bootstrap", "state", 0),
    )
    pointwise = f.fixed_band(uncertainty, POINTWISE_CRITICAL)
    floor = f.fixed_band(uncertainty, FROZEN_CRITICAL)
    source = x5_source(channel)(unit.cells[0], unit.seeds, store, size)
    null_check = source.profiles(
        "check", 4000, parameters=np.asarray(result["parameters"], dtype=float)
    )
    data_check = source.profiles("check", 4000)
    return {
        "auc": float(uncertainty.point[0]),
        "se": float(uncertainty.se[0]),
        "score_se": float(uncertainty.conditional_se[0]),
        "nuisance_variance": result["nuisance_variance"][0],
        "nuisance_mcse": result["nuisance_mcse"][0],
        "mean_shift": result["mean_shift"][0],
        "projected_fraction": result["projected_fraction"][0],
        "interval_95": [float(pointwise[0][0]), float(pointwise[1][0])],
        "interval_27729": [float(floor[0][0]), float(floor[1][0])],
        "lags": {
            "set": "check panels, L1..L5 (profile columns 0:5)",
            "null_mean": null_check.mean(0).tolist(),
            "data_mean": data_check.mean(0).tolist(),
            "data_minus_null": (data_check.mean(0) - null_check.mean(0)).tolist(),
        },
    }


def cell_identity(index: int) -> dict[str, Any]:
    unit, channel = x5_cells()[index]
    return {
        "index": index,
        "unit": unit.key,
        "a": unit.cells[0].share,
        "r": unit.cells[0].reliability,
        "block": unit.block,
        "family": "B",
        "channel": asdict(channel),
    }


def x5_cell(
    index: int,
    out: Path,
    verification: Mapping[str, str],
    sizes: X5Sizes = DECLARED_X5,
) -> dict[str, Any]:
    """One condition at a = 0 into the frozen store layout under ``out/stores``.

    A ValueError from the frozen pipeline leaves the cell without a result and
    is recorded; a fit gap is a result with ``success`` false.
    """
    unit, channel = x5_cells()[index]
    stores = f.private_directory(out / "stores" / unit.key)
    ensure_provenance(SealedStore(stores), f.unit_provenance("x5", sizes.size))
    directory = stores / channel.name
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    error = None
    try:
        f.execute_source_cell(unit, 0, directory, x5_source(channel), size=sizes.size)
    except ValueError as failure:
        error = repr(failure)
    store = SealedStore(directory)
    result: dict[str, Any] | None = store.get_json("result")
    estimate = None
    if result is not None and result["success"]:
        estimate = misspecification(unit, channel, store, result, sizes.size)
    seal = directory / "seal.json"
    attempts = [] if result is None else result["attempts"]
    return {
        "schema": "ic-study.v4-exploratory-x5-cell.v1",
        "cell": cell_identity(index),
        "sizes": asdict(sizes),
        "verification_sha256": dict(verification),
        "error": error,
        "success": None if result is None else result["success"],
        "attempts": [attempt["status"] for attempt in attempts],
        "fit": None
        if result is None
        else {key: result[key] for key in ("parameters", "attempts", "tie_rate")},
        "estimate": estimate,
        "seal_sha256": json.loads(seal.read_bytes())["sha256"]
        if seal.exists()
        else None,
        "timing": {
            "started_utc": started,
            "finished_utc": utc_now(),
            "wall_seconds": time.perf_counter() - clock,
            "cpu_seconds": time.process_time() - cpu,
        },
    }


def analyses(out: Path, verification: Mapping[str, str]) -> dict[str, f.Analysis]:
    return {
        "x5": f.Analysis(
            "x5",
            len(x5_cells()),
            asdict(DECLARED_X5),
            lambda index: x5_cell(index, out, verification),
            (MODULE,),
            verification,
            [cell_identity(i) for i in range(len(x5_cells()))],
        )
    }


# Declared reading and aggregate -----------------------------------------------------


def reading(record: Mapping[str, Any]) -> dict[str, Any]:
    """The declared per-cell reading of the AUC of misspecification."""
    if record["error"]:
        return {"reading": "error", "error": record["error"]}
    if not record["success"]:
        return {"reading": "fit-failure", "statement": FIT_FAILURE}
    lower, upper = record["estimate"]["interval_95"]
    floor = record["estimate"]["interval_27729"]
    if lower > PRIMARY:
        category = "crosses-primary"
    elif lower > SECONDARY:
        category = "crosses-secondary"
    elif upper < SECONDARY:
        category = "below-targets"
    else:
        category = "intermediate"
    return {
        "reading": category,
        "null_gate_would_invalidate": not floor[0] <= 0.5 <= floor[1],
    }


def aggregate_x5(
    out: Path, sizes: X5Sizes = DECLARED_X5, *, now: datetime | None = None
) -> dict[str, Any]:
    cells = x5_cells()
    records, incomplete = f.complete_records(
        out,
        "x5",
        len(cells),
        asdict(sizes),
        now=now,
        legacy_spec=PRECONDITION,
        preconditions=SUITE.preconditions,
        identities=[cell_identity(i) for i in range(len(cells))],
    )
    rows = []
    for _, record in sorted(records.items()):
        rows.append(
            {
                **record["cell"],
                "success": record["success"],
                "attempts": record["attempts"],
                "parameters": None
                if record["fit"] is None
                else record["fit"]["parameters"],
                **reading(record),
                "estimate": record["estimate"],
            }
        )
    counts: dict[str, dict[str, int]] = {}
    for row in rows:
        by_condition = counts.setdefault(row["channel"]["name"], {})
        by_condition[row["reading"]] = by_condition.get(row["reading"], 0) + 1
    values = list(records.values())
    return {
        "schema": "ic-study.v4-exploratory-x5.v1",
        "compatibility": f.compatibility_summary(out),
        "label": f.LABEL,
        "question": "AUC of misspecification: frozen pipeline at a = 0 against a "
        "correctly specified B fitted to a misspecified data arm",
        "declaration": f.declaration_digests(),
        "sizes": asdict(sizes),
        "conditions": [asdict(channel) for channel in CONDITIONS],
        "rule": {
            "crosses-primary": "95% lower bound above 0.70",
            "crosses-secondary": "95% lower bound above 0.60",
            "below-targets": "95% upper bound below 0.60",
            "intermediate": "every other case",
            "null_gate_would_invalidate": "interval at critical 2.7729 excludes 0.5",
            "intervals": "frozen band formula (logit, floor 1/4000) at critical "
            "1.96 and 2.7729 on the frozen total SE",
        },
        "summary": {
            "cells": len(cells),
            "complete": len(values),
            "incomplete": incomplete,
            "readings": dict(sorted(Counter(row["reading"] for row in rows).items())),
            "by_condition": counts,
            "null_gate_would_invalidate": [
                [row["channel"]["name"], row["r"]]
                for row in rows
                if row.get("null_gate_would_invalidate")
            ],
        },
        "seeds": {**f.SEEDS, "analysis": "x5", "common_across_conditions": True},
        "verification_sha256": sorted(
            {json.dumps(r["verification_sha256"], sort_keys=True) for r in values}
        ),
        "code": f.shared_provenance(values, "code"),
        "successor": f.shared_provenance(values, "successor"),
        "host": f.shared_provenance(values, "host"),
        "timing": f.timing_summary(values),
        "cells": rows,
    }


# Timing probe -------------------------------------------------------------------------


def probe(count: int) -> dict[str, Any]:
    """CPU seconds per panel with seeds outside every namespace; panels discarded."""
    cell = Cell(0.0, 0.7)
    seed = f.probe_seed

    def null_row(index: int) -> object:
        latent = null(
            SIZE,
            WAVES,
            seed("state", index),
            seed("null-state", index),
            family="B",
            phi=0.85,
            eta=0.1,
        )
        return observed_profile(latent, 0.7, seed("mask", index), seed("error", index))

    rates = {
        "null-B": f.cpu_per_call(null_row, count),
        "frozen-social": f.cpu_per_call(
            lambda i: f.frozen_social_profile(cell, SIZE, seed, i, False), count
        ),
    }
    for channel in (CONDITIONS[1], CONDITIONS[5], CONDITIONS[7]):
        social = misspecified_social(channel)

        def data_row(index: int, social: f.SocialProfile = social) -> object:
            return social(cell, SIZE, seed, index, False)

        rates[channel.name] = f.cpu_per_call(data_row, count)
    return {"size": SIZE, "count": count, "cpu_seconds_per_panel": rates}


SUITE = f.Suite(
    "x5",
    False,
    ("x5",),
    (PRECONDITION,),
    analyses,
    aggregate_x5,
    probe,
    (MODULE,),
)


def main(argv: list[str] | None = None) -> int:
    return f.main(SUITE, argv)


if __name__ == "__main__":
    raise SystemExit(main())
