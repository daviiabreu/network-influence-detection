"""Synthetic v4 release and gate records produced by the frozen emitters.

Only the numerical simulator is replaced. Every record is persisted by the
frozen runners (``execute_cell``, ``complete_curve``, ``released_curves``,
``execute_task``, ``authorize_stage``, ``aggregate``) and serialised by their
frozen helpers (``fit_record``, ``pipeline_record``, ``band``), so fixtures
carry exactly the schema that the confirmatory and gate code emits. Gate stages
run shard by shard and append one aggregate line per shard, as ``run_gate.py``
does, so ``criteria.jsonl`` holds mid-run ``pass: false`` snapshots. A passing
G1c aggregate cannot be appended, exactly as in the real run; ``stage_successor``
rebuilds it the way the documented successor record does. The values are
artificial and must never be read as results.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import NormalDist
from typing import Any
from unittest import mock

import numpy as np

from ic_study.analysis import detection_boundary_v4 as frozen_analysis
from ic_study.analysis.detection_boundary_v4 import (
    ACCEPTED,
    CovarianceDiagnostic,
    NuisanceResult,
    ProfileFit,
    Uncertainty,
    Validation,
    band,
)
from ic_study.analysis.v4_report_schema import SUCCESSOR_SCHEMA
from ic_study.simulation import v4_curve, v4_gate
from ic_study.simulation.detection_v4 import (
    GRID,
    Cell,
    FitAttempt,
    PipelineResult,
    ValidatedFit,
)
from ic_study.simulation.detection_v4 import pipeline as frozen_pipeline
from ic_study.simulation.v4_plan import G2_CELLS, GateTask, gate_tasks
from ic_study.simulation.v4_store import SealedStore

SYNTHETIC_MARK = "SYNTHETIC — not a result"
AFTER_CLOSE = v4_curve.CLOSE + timedelta(minutes=1)
GATE_STAGES = ("G0", "G1b", "G1c", "G2", "G2c")
NETWORKS = 2000
STUDY = Path(__file__).resolve().parents[3]
FROZEN_CRITERIA = (
    STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
)
FREEZE_DIGEST = "f" * 64
SUCCESSOR_REASON = (
    "frozen aggregate returns pass as numpy bool (mean_z <= 3 on float64); frozen "
    "SealedStore.append cannot serialize it, so run_gate exits 2 after all tasks "
    "are sealed"
)


@dataclass(frozen=True)
class UnitPlan:
    """Artificial AUC profile for one curve unit over the nine frozen strengths.

    Gap cells end in ``gap_status``; a family limit screened by the feasibility
    pre-check has ``gap_evaluations=0``, and an accepted status is a validation
    failure after the retry. Control units get the frozen dependency gap wherever
    their observed unit's cell failed or is missing. Cells in
    ``propagation_errors`` raise the frozen ``project_shift`` error during nuisance
    propagation, which only the amendment v4.4 worker records as a gap.
    """

    auc: tuple[float, ...]
    gaps: frozenset[int] = frozenset()
    gap_status: str = "no-L1-root"
    gap_evaluations: int = 18
    partial_cells: int | None = None  # started but interrupted by the close
    propagation_errors: frozenset[int] = frozenset()


# G0 outcomes beyond accepted fits: every final-status kind of the real mask.
G0_FAILURES: dict[tuple[str, float, float], tuple[str, int]] = {
    ("C", 0.3, 0.5): ("family-limit-upper", 1),  # limit met along the profile
    ("B", 0.9, 0.9): ("no-L1-root", 1),  # its three controls are dependency gaps
    ("E", 0.6, 0.5): ("non-monotone-profile", 1),
    ("A", 0.9, 0.85): ("ill-conditioned", 1),  # implementation status, < 1%
    ("D", 0.9, 0.55): ("interior", 2),  # validation failed in both attempts
}


@dataclass(frozen=True)
class GatePlan:
    stages: tuple[str, ...] = GATE_STAGES
    g1b_undercover: Mapping[str, float] = field(default_factory=dict)
    g2_se_scale: float = 1.0
    skip_tasks: frozenset[str] = frozenset()  # never executed: incomplete stage
    failed_tasks: frozenset[str] = frozenset()  # fit fails (G1c, G2, G2c tasks)
    running: Mapping[str, int] = field(default_factory=dict)  # sealed, no line yet
    pointwise_failures: frozenset[int] = frozenset({17})  # G1c task indices
    shards: int = 3  # run_gate.py appends one aggregate line per shard
    # Observed-channel G0 failures by (family, a, r): status and attempts.
    g0_failures: Mapping[tuple[str, float, float], tuple[str, int]] = field(
        default_factory=lambda: dict(G0_FAILURES)
    )


def logistic_profile(midpoint: float, *, floor: float = 0.5) -> tuple[float, ...]:
    """Monotone artificial AUC over the grid, rising around ``log10(midpoint)``."""
    values = []
    for a in GRID:
        if a == 0:
            values.append(floor)
            continue
        x = math.log10(a) - math.log10(midpoint)
        values.append(floor + (0.99 - floor) / (1 + math.exp(-2.2 * x)))
    return tuple(values)


def _seed(*parts: object) -> int:
    material = "|".join(str(p) for p in ("synthetic-v4-report", *parts))
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


def _fit(
    status: str,
    *,
    success: bool,
    rng: np.random.Generator,
    evaluations: int = 18,
    attempts: int = 1,
) -> ValidatedFit:
    """A frozen-shaped fit; ``profile_match`` spends one evaluation on anchor-exact."""
    made = []
    for count in (1024, 4096)[:attempts]:
        parameters = np.array([rng.uniform(0.3, 0.9), rng.uniform(0.0, 0.5)])
        residual = rng.normal(0, 1e-6, 2) if status != "anchor-exact" else np.zeros(2)
        se = np.full(2, 2e-5)
        validation = (
            Validation(
                passed=success,
                residual=residual,
                se=se,
                z=residual / se,
                equivalence=np.abs(residual) + 2.2414 * se,
                equivalence_passed=True,
                amplification=1.0 + float(rng.uniform(0, 0.2)),
            )
            if status in ACCEPTED
            else None
        )
        fit = ProfileFit(
            parameters,
            np.zeros((4, 2)),
            residual,
            se,
            np.full(2, 5e-5),
            1 if status == "anchor-exact" else evaluations,
            status,
            2,
        )
        made.append(FitAttempt(count, fit, validation))
    return ValidatedFit(tuple(made))


def _nuisance(rng: np.random.Generator, *, sd: float) -> NuisanceResult:
    centered = rng.normal(0, sd, NETWORKS)
    shifts = rng.normal(0, sd, (NETWORKS, 2))
    return NuisanceResult(
        0.5 + centered,
        centered,
        shifts,
        float(centered.var(ddof=1)),
        float(centered.mean()),
        float(sd**2 / math.sqrt(NETWORKS)),
        0.0,
    )


def _cell_lookup() -> dict[Cell, tuple[str, int]]:
    return {
        cell: (unit.key, index)
        for unit in v4_curve.curve_units()
        for index, cell in enumerate(unit.cells)
    }


@contextmanager
def _patched_curve(
    plans: Mapping[str, UnitPlan], *, draws: int
) -> Iterator[dict[Cell, tuple[str, int]]]:
    lookup = _cell_lookup()
    real_uncertainty = frozen_analysis.score_uncertainty

    def pipeline(source: Any, *, observed: Any = None, **kw: Any) -> PipelineResult:
        if source.cell.channel != "observed" and (
            observed is None or not observed.success
        ):
            # The frozen pipeline returns its dependency gap before simulating.
            return frozen_pipeline(source, observed=observed, **kw)
        key, index = lookup[source.cell]
        plan = plans[key]
        if index in plan.propagation_errors:
            # The frozen projection rejects a degenerate local profile.
            frozen_analysis.project_shift(np.zeros(2), np.zeros((2, 2)), np.zeros(2))
        rng = np.random.default_rng(_seed(key, index))
        if index in plan.gaps:
            fit = _fit(
                plan.gap_status,
                success=False,
                rng=rng,
                evaluations=plan.gap_evaluations,
                attempts=2 if plan.gap_status in ACCEPTED else 1,
            )
            return PipelineResult(fit, None, (), 0.0)
        anchor = source.cell.share == 0 and source.cell.family in "ABDE"
        shift = math.sqrt(2) * NormalDist().inv_cdf(plan.auc[index])
        return PipelineResult(
            _fit("anchor-exact" if anchor else "interior", success=True, rng=rng),
            None,
            (_nuisance(rng, sd=0.0 if anchor else 0.004),),
            float(rng.uniform(0, 0.01)),
            scores0=rng.normal(0, 1, (NETWORKS, 2)),
            scores1=rng.normal(shift, 1, (NETWORKS, 2)),
        )

    def uncertainty(
        null: np.ndarray, social: np.ndarray, nuisance: np.ndarray, *, seed: int
    ) -> Uncertainty:
        # Frozen inference with fewer bootstrap draws, for fixture speed only.
        return real_uncertainty(null, social, nuisance[:draws], seed=seed, draws=draws)

    with (
        mock.patch.object(v4_curve, "pipeline", pipeline),
        mock.patch.object(v4_curve, "score_uncertainty", uncertainty),
        mock.patch.object(v4_curve, "CLOSE", datetime.now(UTC) + timedelta(days=30)),
        mock.patch("os.fsync", lambda _fd: None),
    ):
        yield lookup


def build_release(
    root: Path,
    plans: Mapping[str, UnitPlan],
    *,
    draws: int = 200,
    worker: Callable[[v4_curve.CurveUnit, int, Path], None] | None = None,
) -> dict[str, object]:
    """Run the frozen confirmatory emitters on artificial panels, then release.

    Units run in the order of ``plans``: list an observed unit before the
    controls that reuse its fits. ``worker`` replaces the frozen
    ``execute_cell`` for every cell, as a worker passed to ``schedule`` does.
    """
    store = SealedStore(root)
    units = {unit.key: unit for unit in v4_curve.curve_units()}
    provenance = {"synthetic": True, "code": {"synthetic": "0" * 64}}
    execute = worker or v4_curve.execute_cell
    with _patched_curve(plans, draws=draws):
        for key, plan in plans.items():
            unit = units[key]
            directory = store.root / key
            unit_store = SealedStore(directory)
            if unit_store.get_json("provenance") is None:
                unit_store.put_json("provenance", provenance)
            cells = len(GRID) if plan.partial_cells is None else plan.partial_cells
            for index in range(cells):
                execute(unit, index, directory / f"a{index}")
            if plan.partial_cells is None:
                v4_curve.complete_curve(unit, directory)
    with mock.patch("os.fsync", lambda _fd: None):
        return v4_curve.released_curves(store, now=AFTER_CLOSE)


def write_release(path: Path, release: dict[str, object]) -> None:
    """Frozen curve bytes and a synthetic declared-close receipt for rehearsals."""
    path.write_text(json.dumps(release, allow_nan=False) + "\n", encoding="utf-8")
    record = {
        "schema": 1,
        "condition": "declared-close",
        "released_utc": AFTER_CLOSE.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "released_curves_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "amendment": {
            "path": "studies/ic-2026-2027/research/questions/exploration/"
            "2026-09-24-parallel/detection-boundary-v4-release-amendment.md",
            "commit": "428ca7cd6158244b494dcb520b9a69738b5bfae6",
        },
    }
    path.with_name("release-record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _g0_fit(
    family: str, channel: str, cell: Cell, rng: np.random.Generator, plan: GatePlan
) -> ValidatedFit:
    if cell.share == 0 and family != "C":
        return _fit("anchor-exact", success=True, rng=rng)
    if family == "C" and cell.share >= 0.6 and cell.reliability < 0.6:
        # Screened by the feasibility pre-check before any solver evaluation.
        return _fit("family-limit-upper", success=False, rng=rng, evaluations=0)
    evaluations = int(rng.integers(8, 40))
    failure = (
        plan.g0_failures.get((family, cell.share, cell.reliability))
        if channel == "observed"
        else None
    )
    if failure is not None:
        status, attempts = failure
        return _fit(
            status, success=False, rng=rng, evaluations=evaluations, attempts=attempts
        )
    status = "interior" if rng.uniform() > 0.03 else "boundary"
    return _fit(status, success=True, rng=rng, evaluations=evaluations)


def _g0_record(
    cell: Cell, rng: np.random.Generator, plan: GatePlan
) -> dict[str, object]:
    """Fits in the order and shape of the frozen ``run_task`` for G0."""
    fits: list[dict[str, object]] = []
    for family in "ABCDE":
        observed = _g0_fit(family, "observed", cell, rng, plan)
        fits.append(
            {"family": family, "channel": "observed", **v4_gate.fit_record(observed)}
        )
        if family != "B":
            continue
        for channel in ("latent", "ordinal_one", "latent_rank"):
            if not observed.success:
                fits.append(
                    {
                        "family": family,
                        "channel": channel,
                        "success": False,
                        "attempts": [],
                        "dependency_gap": True,
                    }
                )
                continue
            control = _g0_fit(family, channel, cell, rng, plan)
            fits.append(
                {"family": family, "channel": channel, **v4_gate.fit_record(control)}
            )
    return {"fits": fits, "success": True}


def _gate_record(
    task: GateTask, store: SealedStore, plan: GatePlan
) -> dict[str, object]:
    rng = np.random.default_rng(_seed(task.key))
    cell = task.cell
    if task.gate == "G0":
        return _g0_record(cell, rng, plan)
    if task.gate == "G1b":
        inflate = 1.0 - plan.g1b_undercover.get(task.scenario, 0.0)
        center = np.clip(0.5 + rng.normal(0, 0.006, 9), 0, 1)
        replicates = np.clip(center + rng.normal(0, 0.006, (NETWORKS, 9)), 0, 1)
        interval = band(
            Uncertainty(
                center, np.full(9, 0.006), np.full(9, 0.006 * inflate), replicates
            )
        )
        return {
            "success": True,
            "covered": bool(np.all((interval.lower <= 0.5) & (interval.upper >= 0.5))),
            "critical": interval.critical,
            "empirical_exceeds_floor": interval.empirical_exceeds_floor,
        }
    se = 0.01 * plan.g2_se_scale
    truth_auc = 0.5 if cell.share == 0 else 0.5 + min(0.45, 1.2 * cell.share**0.5)
    noise = 0.005 if task.gate == "G2c" else se
    point = float(np.clip(truth_auc + rng.normal(0, noise), 0, 1))
    status = "anchor-exact" if cell.share == 0 else "interior"
    reliable = task.baseline or task.gate == "G1c"
    success = task.key not in plan.failed_tasks and (reliable or rng.uniform() > 0.005)
    fit = _fit(status, success=success, rng=rng)
    if task.gate == "G2c" and not task.baseline:
        record = v4_gate.fit_record(fit)
        if fit.success:
            record["auc"] = point
        return record
    nuisance = tuple(
        _nuisance(rng, sd=0.0 if cell.share == 0 else 0.005 * (1 + 0.02 * k))
        for k in range(2 if task.gate == "G2" else 1)
    )
    if not fit.success:
        record = v4_gate.pipeline_record(PipelineResult(fit, None, (), 0.0))
        record["mechanism_degeneracy"] = cell.anchor == 1
        record["truth"] = None
        return record
    result = PipelineResult(
        fit,
        Uncertainty(
            np.array([point]), np.array([se]), np.array([se]), np.zeros((2, 1))
        ),
        nuisance,
        float(rng.uniform(0, 0.01)),
        covariance_diagnostics=(
            CovarianceDiagnostic(np.zeros(2), np.zeros(2), 0.001, False),
        )
        if task.gate == "G2"
        else (),
    )
    record = v4_gate.pipeline_record(result)
    record["mechanism_degeneracy"] = cell.anchor == 1
    record["truth"] = None
    if task.gate == "G1c":
        record["pointwise_failure"] = task.index in plan.pointwise_failures
        record["truth"] = 0.5
    if task.gate == "G2c" and store.get_array("nuisance-aucs") is None:
        store.put_array("nuisance-aucs", nuisance[0].aucs)
    return record


def allocation_record(
    root: Path, criteria: bytes, cells: tuple[tuple[float, float], ...] = G2_CELLS
) -> dict[str, object]:
    """Post-G0 second binding, built by the frozen G0 status and gap-rate code."""
    with mock.patch("os.fsync", lambda _fd: None):
        statuses = v4_gate.g0_statuses(SealedStore(root))
    return {
        "schema": 1,
        "stage": "post-G0-pre-G2",
        "freeze_sha256": FREEZE_DIGEST,
        "g0_statuses_sha256": v4_gate.status_digest(statuses),
        "criteria_sha256": hashlib.sha256(criteria).hexdigest(),
        "g0_gap_binding": v4_gate.g0_gap_binding(statuses, cells, json.loads(criteria)),
        "g2_cells": [list(cell) for cell in cells],
    }


def build_gate(
    root: Path,
    plan: GatePlan | None = None,
    *,
    cells: tuple[tuple[float, float], ...] = G2_CELLS,
    allocation: Path | None = None,
) -> Path:
    """Authorize, execute and aggregate gate stages with the frozen runner code.

    With ``allocation``, the second binding is written there before G2 and its
    digest binds G2 and G2c, as ``run_gate.py --allocation`` requires.
    """
    chosen = plan or GatePlan()
    criteria_bytes = FROZEN_CRITERIA.read_bytes()
    criteria = json.loads(criteria_bytes)
    store = SealedStore(root)
    binding = FREEZE_DIGEST

    def run(task: GateTask, sealed: SealedStore) -> dict[str, object]:
        return _gate_record(task, sealed, chosen)

    with (
        mock.patch.object(v4_gate, "run_task", run),
        mock.patch("os.fsync", lambda _fd: None),
    ):
        for stage in chosen.stages:
            if stage in {"G2", "G2c"} and allocation is not None:
                if not allocation.exists():
                    record = allocation_record(store.root, criteria_bytes, cells)
                    allocation.write_text(
                        json.dumps(record, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8",
                    )
                binding = hashlib.sha256(allocation.read_bytes()).hexdigest()
            if stage != "G2c" or (store.root / "authorization-G2.json").exists():
                v4_gate.authorize_stage(store, stage, FREEZE_DIGEST, binding)
            provenance: dict[str, object] = {
                "freeze_sha256": FREEZE_DIGEST,
                "binding_sha256": binding,
            }
            tasks = [
                task
                for task in gate_tasks(stage, cells=cells)
                if task.key not in chosen.skip_tasks
            ]
            if stage in chosen.running:
                # A shard still running has sealed tasks but appended no line.
                for task in tasks[: chosen.running[stage]]:
                    v4_gate.execute_task((task, str(store.root), provenance))
                continue
            for shard in range(chosen.shards):
                for task in tasks:
                    if task.index % chosen.shards == shard:
                        v4_gate.execute_task((task, str(store.root), provenance))
                summary = v4_gate.aggregate(
                    stage,
                    store.root,
                    criteria,
                    cells=cells,
                    binding={"freeze_sha256": FREEZE_DIGEST, "binding_sha256": binding},
                )
                try:
                    store.append("criteria", summary)
                except TypeError:
                    break  # numpy bool pass: run_gate exits 2, every task sealed
    return store.root


def stop_before_g2(
    root: Path, allocation: Path, cells: tuple[tuple[float, float], ...] = G2_CELLS
) -> dict[str, object] | None:
    """Run the frozen second-binding preflight as ``run_gate.py --gate G2`` does.

    When the G0 gap-rate check stops G2, append its economy-rule record to
    ``criteria.jsonl`` exactly as the runner does and return it.
    """
    criteria = FROZEN_CRITERIA.read_bytes()
    with mock.patch("os.fsync", lambda _fd: None):
        if not allocation.exists():
            record = allocation_record(root, criteria, cells)
            allocation.write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        store = SealedStore(root)
        statuses = v4_gate.g0_statuses(store)
        try:
            v4_gate.allocation_preflight(allocation, FREEZE_DIGEST, statuses, criteria)
        except v4_gate.GapRateStopError as exc:
            stop: dict[str, object] = {
                "pass": False,
                "stopped_before_G2": True,
                "g0_gap_binding": exc.report,
            }
            store.append("criteria", stop)
            return stop
    return None


def _plain(value: object) -> object:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_plain(item) for item in value]
    return value


def stage_successor(root: Path, stage: str = "G1c") -> dict[str, Any]:
    """Successor record for a stage whose complete line the frozen runner lost.

    Same schema as the documented G1c record: the frozen ``aggregate`` over the
    sealed tasks with numpy scalars converted to Python scalars, nothing else.
    """
    criteria = json.loads(FROZEN_CRITERIA.read_bytes())
    binding = {"freeze_sha256": FREEZE_DIGEST, "binding_sha256": FREEZE_DIGEST}
    with mock.patch("os.fsync", lambda _fd: None):
        summary = v4_gate.aggregate(stage, root, criteria, binding=binding)
    kind = type(summary["pass"])
    return {
        "schema": SUCCESSOR_SCHEMA,
        "stage": stage,
        "reason": SUCCESSOR_REASON,
        "frozen_code_location": (
            "src/ic_study/simulation/v4_gate.py:526 and "
            "src/ic_study/simulation/v4_store.py:65"
        ),
        "conversion": "numpy scalars converted to Python scalars; no other change",
        "freeze_sha256": FREEZE_DIGEST,
        "sealed_root_identifier": root.resolve().name,
        "computed_at_utc": "2026-09-28T00:00:00Z",
        "summary": _plain(summary),
        "pass_type_in_frozen_output": f"{kind.__module__}.{kind.__name__}",
    }


def shp_fixture(seed: int = 7, people: int = 400) -> dict[str, Any]:
    """Aggregate SHP anchor record from the frozen analysis on an artificial panel."""
    from ic_study.analysis.shp_reliability import YEARS, analyze_panel

    rng = np.random.default_rng(seed)
    latent = np.empty((people, len(YEARS)))
    latent[:, 0] = rng.normal(0, 1, people)
    for t in range(1, len(YEARS)):
        latent[:, t] = 0.9 * latent[:, t - 1] + math.sqrt(1 - 0.81) * rng.normal(
            0, 1, people
        )
    observed = latent + rng.normal(0, 0.65, latent.shape)
    panel = np.clip(np.round(5 + 1.8 * observed), 0, 10)
    panel[rng.uniform(size=panel.shape) < 0.08] = np.nan
    return analyze_panel(panel, YEARS)


def shp_successor_fixture(
    seed: int = 7, people: int = 1500, *, starts_admissible: bool = True
) -> dict[str, Any]:
    """SHP record with the successor-1 sections, from the analysis on artificial data.

    A third of the people enter in 2004. A stable trait makes STARTS admissible;
    without it, subtracting a fifth of each person's mean pulls long-lag
    covariances below any trait, so STARTS records its declared variance failure.
    """
    from ic_study.analysis.shp_reliability import YEARS, analyze_panel

    rng = np.random.default_rng(seed)
    state = np.empty((people, len(YEARS)))
    state[:, 0] = rng.normal(0, 1, people)
    for t in range(1, len(YEARS)):
        state[:, t] = 0.6 * state[:, t - 1] + 0.8 * rng.normal(0, 1, people)
    observed = state + rng.normal(0, 0.8, state.shape)
    if starts_admissible:
        observed += rng.normal(0, 1, (people, 1))
    else:
        observed -= 0.2 * observed.mean(axis=1, keepdims=True)
    panel = np.clip(np.round(5 + 1.3 * observed), 0, 10)
    panel[: people // 3, : YEARS.index(2004)] = np.nan
    panel[rng.uniform(size=panel.shape) < 0.08] = np.nan
    return analyze_panel(panel, YEARS, include_successor=True)


def crosswalk_fixture(seed: int = 13, *, spread: float = 0.012) -> dict[str, Any]:
    """Crosswalk aggregate serialised by ``shp_crosswalk`` from artificial values.

    Only the panel simulation and estimation are replaced: every cell of the
    declared plan gets artificial per-replicate estimates below its r, and one
    STARTS failure per B reference cell exercises the failure counts.
    """
    from ic_study.analysis import shp_crosswalk as crosswalk
    from ic_study.analysis.shp_reliability import STARTS_FAILURES

    rng = np.random.default_rng(seed)
    cells = crosswalk.plan_cells()
    plan = crosswalk.plan_record(
        crosswalk.REPLICATES, crosswalk.SEED_ROOT, crosswalk.SIZE
    )
    records = []
    for cell in cells:
        center = cell.r - 0.04 - 0.05 * (cell.eta or 0) + 0.02 * (cell.a or 0)
        rows = []
        for replicate in range(crosswalk.REPLICATES):
            values = {
                name: float(np.clip(center + rng.normal(0, spread), 0.01, 0.99))
                for name in crosswalk.estimator_names()
            }
            failures: dict[str, list[str]] = {}
            if cell.family == "B" and replicate == 0:
                del values[crosswalk.STARTS]
                failures[crosswalk.STARTS] = [STARTS_FAILURES[2]]
            rows.append(
                {
                    "replicate": replicate,
                    "values": values,
                    "failures": failures,
                    "cpu_seconds": 0.0,
                }
            )
        records.append(
            crosswalk.cell_record(
                cell,
                plan,
                rows,
                provenance={"synthetic": SYNTHETIC_MARK},
                cpu_seconds=0.0,
                wall_seconds=0.0,
            )
        )
    return crosswalk.aggregate_record(cells, plan, records)


def unit_keys(*, tier: int, family: str, channel: str = "observed") -> dict[float, str]:
    """Map r to the frozen unit key of a main-sensitivity unit on one channel."""
    return {
        unit.cells[0].reliability: unit.key
        for unit in v4_curve.curve_units()
        if unit.tier == tier
        and unit.cells[0].family == family
        and unit.cells[0].channel == channel
        and unit.cells[0].mobility is False
        and unit.cells[0].error_correlation == 0
        and unit.cells[0].gain == 0
        and unit.cells[0].repulsion == 0.25
        and unit.cells[0].anchor == 0
        and unit.cells[0].steps == 1
    }
