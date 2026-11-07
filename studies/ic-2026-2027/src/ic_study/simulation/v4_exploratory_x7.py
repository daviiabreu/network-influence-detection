"""Exploratory X7: the discriminator ceiling with rich panel features.

Declared on 2026-09-28 in
``experiments/exploratory/detection-boundary-v4-exploratory/README-x3-x7.md``
(objection R1-M7). The arms, the frozen B fit on L1 and L2 and the frozen LDA
code stay; the discriminant sees a fixed 36-feature vector of each panel
instead of the three frozen correlations. The X7 pipeline is the frozen
pipeline generalized by a feature extractor. With the frozen extractor
(profile columns 2:5) it must reproduce the frozen ``execute_cell`` store
byte for byte, which the declared precondition checks. In a run every panel
is generated once and gives both feature sets: the frozen-feature stores
yield a*_x7(r) and the rich stores a*_rich(r), both through the frozen
``complete_curve``. X7 is sealed until the confirmatory release.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
import warnings
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.analysis.detection_boundary import auc
from ic_study.analysis.detection_boundary_v4 import (
    NuisanceInput,
    anchor_nuisance,
    mean_feature_jacobian,
    nuisance_draws,
)
from ic_study.analysis.redesign import fit_discriminant
from ic_study.models.anchored_panel import Floats, Integers, panel_mask
from ic_study.models.detection_panel import measurement, ordinal_channel
from ic_study.models.detection_panel_v4 import null
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation.detection_v4 import (
    GRID,
    Cell,
    PanelSource,
    PipelineResult,
    SeedPlan,
    ValidatedFit,
    fit_cell,
    selected_features,
)
from ic_study.simulation.v4_curve import _put_array, complete_curve, deadline
from ic_study.simulation.v4_exploratory import SIZE, WAVES, utc_now
from ic_study.simulation.v4_exploratory_x1b import ensure_provenance, original_generator
from ic_study.simulation.v4_gate import pipeline_record
from ic_study.simulation.v4_store import SealedStore

MODULE = Path(__file__).resolve()
PRECONDITION_CELLS = ((0.0, 0.9), (0.003, 0.7), (0.03, 0.5), (0.3, 0.6))
RICH_PHASES = frozenset({"train", "check", "reference"})
GROUPS = np.array([0, 0, 1, 1, 2, 2, 2, 3, 3, 4, 4])
PERSON_QUANTILES = (0.1, 0.25, 0.5, 0.75, 0.9)
RICH_WIDTH = 36
MARGIN = 0.02
RESAMPLES = 1000


# Rich features ---------------------------------------------------------------------


def rich_features(latent: Floats, observed: Integers) -> Floats:
    """The declared 36 features of one panel, in the declared order.

    L3..L10 by the frozen ``lag_profile`` formula (8); the frozen mobility
    summary of ``selected_features`` (3); lag-1 transition frequencies between
    the category groups {0,1}, {2,3}, {4,5,6}, {7,8}, {9,10}, row-conditional
    over all consecutive observed pairs, last column dropped (20); the 0.1,
    0.25, 0.5, 0.75 and 0.9 quantiles (NumPy linear) of the within-person
    standard deviation (NumPy default, ddof 0) of the observed categories among
    persons with at least six observed waves (5). Non-finite values are kept
    so that the caller can record the numerical gap.
    """
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        values = np.where(observed >= 0, observed, np.nan)
        lags = []
        for lag in range(3, WAVES):
            x, y = values[:-lag].ravel(), values[lag:].ravel()
            valid = np.isfinite(x) & np.isfinite(y)
            lags.append(float(np.corrcoef(x[valid], y[valid])[0, 1]))
        mobility = selected_features(
            latent, observed, channel="observed", mobility=True
        )[2:5]
        before, after = observed[:-1], observed[1:]
        pairs = (before >= 0) & (after >= 0)
        counts = np.bincount(
            5 * GROUPS[before[pairs]] + GROUPS[after[pairs]], minlength=25
        ).reshape(5, 5)
        transitions = (counts / counts.sum(1, keepdims=True))[:, :4].ravel()
        eligible = (observed >= 0).sum(0) >= 6
        person = np.full(len(PERSON_QUANTILES), np.nan)
        if eligible.any():
            spread = np.nanstd(values[:, eligible], axis=0)
            person = np.quantile(spread, PERSON_QUANTILES)
    return np.concatenate([lags, mobility, transitions, person])


def observed_channel(
    latent: Floats, reliability: float, mask_seed: int, error_seed: int
) -> Integers:
    """The frozen tier-1 observed channel of ``PanelSource._profiles``."""
    mask = panel_mask(latent.shape[1], WAVES, mask_seed, retention=0.89)
    measured = measurement(
        latent, reliability, error_seed, heteroscedastic=False, error_correlation=0
    )
    return ordinal_channel(measured, mask, midpoint_mass=0, heap_seed=None)


def frozen_profile(latent: Floats, observed: Integers) -> Floats:
    return selected_features(
        latent, observed, channel="observed", mobility=False, midpoint_mass=0
    )


class FeatureSource(PanelSource):
    """Frozen ``PanelSource`` of a tier-1 cell whose panels also give rich rows.

    Each panel is drawn once, by the frozen social generator or null law and
    the frozen observed channel. Its frozen profile becomes the frozen store's
    checkpoint; in train, check and reference its rich row goes to the rich
    store under the same checkpoint key. Matching panels get rich rows only on
    request, by regeneration.
    """

    def __init__(
        self,
        cell: Cell,
        seeds: SeedPlan,
        *,
        size: int = SIZE,
        store: SealedStore | None = None,
        rich: SealedStore | None = None,
    ) -> None:
        if cell != Cell(cell.share, cell.reliability):
            raise ValueError("The successor covers tier-1 cells only")
        if not isinstance(seeds, f.SuccessorSeedPlan):
            raise ValueError("The successor draws successor seeds only")
        super().__init__(cell, seeds, size=size, store=store)
        self.rich = rich
        self.rich_provenance = (
            {} if rich is None else (rich.get_json("provenance") or {})
        )

    def key(
        self,
        phase: str,
        count: int,
        start: int,
        attempt: int,
        parameters: Floats | None,
    ) -> str:
        """The frozen checkpoint key of one chunk."""
        material = dict(
            cell=asdict(self.cell),
            seeds=asdict(self.seeds),
            size=self.size,
            phase=phase,
            count=count,
            start=start,
            attempt=attempt,
            parameters=None if parameters is None else parameters.tolist(),
        )
        return hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()

    def panel(
        self, phase: str, j: int, parameters: Floats | None, attempt: int
    ) -> tuple[Floats, Integers]:
        coupled = phase in {"match", "validate"}
        index = 2 * j + (1 if coupled or parameters is None else 0)

        def seed(role: str, i: int = index) -> int:
            return self.seeds.seed(phase, role, i, attempt=attempt)

        if parameters is None:
            latent = original_generator(self.cell, self.size, seed, index, coupled)
        else:
            latent = null(
                self.size,
                WAVES,
                seed("state"),
                seed("null-state"),
                family=self.cell.family,
                phi=float(parameters[0]),
                eta=float(parameters[1]),
                steps=self.cell.steps,
            )
        observed = observed_channel(
            latent, self.cell.reliability, seed("mask"), seed("error")
        )
        return latent, observed

    def rows(
        self,
        phase: str,
        count: int,
        *,
        parameters: Floats | None,
        attempt: int,
        start: int,
        rich: bool,
    ) -> tuple[Floats, Floats]:
        frozen, extra = [], []
        for j in range(start, start + count):
            latent, observed = self.panel(phase, j, parameters, attempt)
            frozen.append(frozen_profile(latent, observed))
            if rich:
                extra.append(rich_features(latent, observed))
            self.panels += 1
        return np.stack(frozen), np.stack(extra) if rich else np.empty((count, 0))

    def _profiles(
        self,
        phase: str,
        count: int,
        *,
        parameters: Floats | None = None,
        attempt: int = 0,
        start: int = 0,
    ) -> Floats:
        rich = self.rich is not None and phase in RICH_PHASES
        frozen, extra = self.rows(
            phase, count, parameters=parameters, attempt=attempt, start=start, rich=rich
        )
        if rich:
            key = self.key(phase, count, start, attempt, parameters)
            self._put_rich(key, extra, phase, attempt)
        return frozen

    def rich_profiles(
        self,
        phase: str,
        count: int,
        *,
        parameters: Floats | None = None,
        attempt: int = 0,
        start: int = 0,
    ) -> Floats:
        """Rich rows in the frozen chunk layout, regenerated where missing."""
        if self.rich is None:
            raise ValueError("Rich features need a rich store")
        chunks = []
        for offset in range(start, start + count, 32):
            length = min(32, start + count - offset)
            key = self.key(phase, length, offset, attempt, parameters)
            values = self.rich.get_array(key)
            if values is None:
                _, values = self.rows(
                    phase,
                    length,
                    parameters=parameters,
                    attempt=attempt,
                    start=offset,
                    rich=True,
                )
                self._put_rich(key, values, phase, attempt)
            chunks.append(values)
        return np.concatenate(chunks)

    def _put_rich(self, key: str, values: Floats, phase: str, attempt: int) -> None:
        if self.rich is None or (self.rich.root / f"{key}.npy").exists():
            return
        self.rich.put_array(key, values)
        self.rich.append(
            "phases",
            {
                "phase": phase,
                "attempt": attempt,
                "features": "rich",
                "seed_material_sha256": key,
                "code_sha256": self.rich_provenance.get("code_sha256"),
                "environment_sha256": self.rich_provenance.get("environment_sha256"),
                "host_sha256": self.rich_provenance.get("host_sha256"),
                "panels": len(values),
            },
        )


# The frozen pipeline generalized by a feature extractor ----------------------------


@dataclass(frozen=True)
class Extractor:
    """Discriminant features: rows from the frozen or the rich checkpoints."""

    name: str
    columns: slice
    rich: bool

    def rows(
        self,
        source: FeatureSource,
        phase: str,
        count: int,
        parameters: Floats | None = None,
        attempt: int = 0,
    ) -> Floats:
        if self.rich:
            return source.rich_profiles(
                phase, count, parameters=parameters, attempt=attempt
            )
        return source.profiles(phase, count, parameters=parameters, attempt=attempt)


FROZEN_FEATURES = Extractor("frozen", slice(2, 5), False)
RICH_FEATURES = Extractor("rich", slice(0, RICH_WIDTH), True)


class NonFiniteFeatureError(Exception):
    """A rich feature is not finite in some panel: a recorded numerical gap."""


def feature_pass(
    source: FeatureSource,
    fit: ValidatedFit,
    extractor: Extractor,
    moments: Floats | None = None,
) -> tuple[PipelineResult, Floats | None]:
    """Frozen ``pipeline`` after a successful fit, with the extractor's features.

    The calls, their order and the arithmetic are the frozen ones for tier-1
    cells (one step of 0.01, no control dependency, no G2 diagnostic, no
    uncertainty). The moment Jacobian of L1 and L2 comes from the frozen
    profiles; the frozen extractor computes it, the rich one receives it.
    """
    final = fit.final.fit
    attempt = len(fit.attempts) - 1

    def features(phase: str, count: int, parameters: Floats | None = None) -> Floats:
        values = extractor.rows(source, phase, count, parameters)[:, extractor.columns]
        if extractor.rich and not np.all(np.isfinite(values)):
            raise NonFiniteFeatureError(phase)
        return values

    train0 = features("train", 2000, final.parameters)
    train1 = features("train", 2000)
    model = fit_discriminant(np.concatenate([train0, train1]), np.repeat([0, 1], 2000))
    test0 = model.score(features("check", 4000, final.parameters))
    test1 = model.score(features("check", 4000))
    if final.status == "anchor-exact":
        nuisance = anchor_nuisance()
    else:
        reference0 = features("reference", 4000, final.parameters)
        reference1 = features("reference", 4000)
        count = fit.final.count

        def evaluate(p: Floats) -> Floats:
            return extractor.rows(source, "match", count, p, attempt)

        match0 = evaluate(final.parameters)
        derivative = mean_feature_jacobian(
            evaluate, final.parameters, 0.01, match0, parameters=2
        )
        if moments is None:
            if extractor.rich:
                raise ValueError("Rich features take the frozen moment Jacobian")
            moments = derivative[:, :2].T
        mean_derivative = derivative[:, extractor.columns]
        if extractor.rich and not (
            np.all(np.isfinite(match0)) and np.all(np.isfinite(mean_derivative))
        ):
            raise NonFiniteFeatureError("match")
        nuisance = nuisance_draws(
            NuisanceInput(
                final.parameters,
                final.differences,
                moments,
                train0,
                train1,
                reference0,
                reference1,
                mean_derivative,
            ),
            seed=source.seeds.seed("nuisance", "state", 0),
            inherited_eta=None,
        )
    ordered = np.sort(test0)
    ties = np.searchsorted(ordered, test1, side="right") - np.searchsorted(
        ordered, test1, side="left"
    )
    result = PipelineResult(
        fit,
        None,
        (nuisance,),
        float(ties.sum() / (len(test0) * len(test1))),
        (),
        test0.reshape(2000, 2),
        test1.reshape(2000, 2),
    )
    return result, moments


def cell_record(result: PipelineResult) -> dict[str, object]:
    """The frozen ``execute_cell`` record of a pipeline result."""
    record = pipeline_record(result)
    record.update(
        dependency_gap=result.dependency_gap,
        nuisance_variance=[n.variance for n in result.nuisance],
        nuisance_mcse=[n.mcse for n in result.nuisance],
        mean_shift=[n.mean_shift for n in result.nuisance],
        projected_fraction=[n.projected_fraction for n in result.nuisance],
    )
    return record


def _inherit_provenance(parent: SealedStore, store: SealedStore) -> None:
    parent_provenance = parent.get_json("provenance")
    if parent_provenance is not None and store.get_json("provenance") is None:
        code = json.dumps(parent_provenance.get("code", {}), sort_keys=True)
        store.put_json(
            "provenance",
            {
                **parent_provenance,
                "code_sha256": hashlib.sha256(code.encode()).hexdigest(),
            },
        )


def rich_outcome(rich: SealedStore) -> str | None:
    outcome = rich.get_json("outcome")
    if outcome is None:
        if rich.get_json("result") is None:
            raise ValueError("Frozen result has no durable rich outcome")
        outcome = {"error": None}
        if not (rich.root / "seal.json").exists():
            rich.put_json("outcome", outcome)
    if not (rich.root / "seal.json").exists():
        rich.seal()
    error = outcome["error"]
    return None if error is None else str(error)


def _rich_cell(
    source: FeatureSource,
    fit: ValidatedFit,
    moments: Floats | None,
    rich: SealedStore,
) -> str | None:
    """Persist the terminal outcome before finalizing the paired frozen cell."""
    if rich.get_json("outcome") is not None or rich.get_json("result") is not None:
        return rich_outcome(rich)
    error = None
    with rich.capture_output():
        record = cell_record(PipelineResult(fit, None, (), 0))
        record["success"] = False
        if fit.success:
            try:
                result, _ = feature_pass(source, fit, RICH_FEATURES, moments)
                if result.scores0 is None or result.scores1 is None:
                    raise ValueError("Pipeline omitted curve scores")
                record = cell_record(result)
                _put_array(rich, "scores0", result.scores0)
                _put_array(rich, "scores1", result.scores1)
                _put_array(rich, "nuisance", result.nuisance[0].centered)
                record["success"] = True
            except NonFiniteFeatureError as gap:
                record["numerical_gap"] = f"non-finite rich feature in {gap}"
            except ValueError as failure:
                error = repr(failure)
        if error is None:
            record["features"] = f"rich-{RICH_WIDTH}"
            rich.put_json("result", record)
        rich.put_json("outcome", {"error": error})
    rich.seal()
    return error


def execute_feature_cell(
    unit: f.SuccessorUnit,
    index: int,
    directory: Path,
    *,
    rich_directory: Path | None = None,
    size: int = SIZE,
) -> str | None:
    """Frozen ``execute_cell`` with the pipeline generalized by the extractors.

    The frozen-feature store gets the frozen layout. With ``rich_directory``
    the same panels also fill the rich store, which is finished before the
    frozen result, so a frozen result implies a finished rich cell. Returns
    the rich pass's ValueError, recorded; one from the frozen pass propagates.
    """
    parent = SealedStore(directory.parent)
    store = SealedStore(directory)
    if store.get_json("result") is not None:
        if not (directory / "seal.json").exists():
            store.seal()
        return (
            None
            if rich_directory is None
            else rich_outcome(SealedStore(rich_directory))
        )
    _inherit_provenance(parent, store)
    rich = None
    if rich_directory is not None:
        rich = SealedStore(rich_directory)
        _inherit_provenance(SealedStore(rich_directory.parent), rich)
    rich_error = None
    cell = unit.cells[index]
    with store.capture_output():
        with deadline():
            source = FeatureSource(cell, unit.seeds, size=size, store=store, rich=rich)
            fit = fit_cell(source)
            result, moments = PipelineResult(fit, None, (), 0), None
            if fit.success:
                result, moments = feature_pass(source, fit, FROZEN_FEATURES)
            record = cell_record(result)
            if fit.success:
                if result.scores0 is None or result.scores1 is None:
                    raise ValueError("Pipeline omitted curve scores")
                _put_array(store, "scores0", result.scores0)
                _put_array(store, "scores1", result.scores1)
                _put_array(store, "nuisance", result.nuisance[0].centered)
                _put_array(store, "eta-shifts", result.nuisance[0].shifts[:, 1])
            record["success"] = fit.success
            if rich is not None:
                rich_error = _rich_cell(source, fit, moments, rich)
        store.put_json("result", record)
    store.seal()
    return rich_error


# Units, precondition and cells ------------------------------------------------------


def x7_units() -> tuple[f.SuccessorUnit, ...]:
    return f.tier1_units("x7")


def rich_units() -> tuple[f.SuccessorUnit, ...]:
    """The rich-feature curve units: same cells and streams, their own stores."""
    return f.tier1_units("x7", "x7-rich")


def x7_cells() -> tuple[tuple[f.SuccessorUnit, int], ...]:
    return tuple((unit, index) for unit in x7_units() for index in range(len(GRID)))


def frozen_extractor_executor(
    unit: f.SuccessorUnit, index: int, directory: Path, size: int
) -> None:
    execute_feature_cell(unit, index, directory, size=size)


PRECONDITION = f.Precondition(
    "x7", x7_units(), PRECONDITION_CELLS, frozen_extractor_executor, modules=(MODULE,)
)


@dataclass(frozen=True)
class X7Sizes:
    size: int = SIZE


DECLARED_X7 = X7Sizes()


def _read(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_bytes()) if path.exists() else None


def cell_identity(index: int) -> dict[str, Any]:
    unit, position = x7_cells()[index]
    rich_unit = rich_units()[unit.block]
    cell = unit.cells[position]
    return {
        "index": index,
        "unit": unit.key,
        "rich_unit": rich_unit.key,
        "position": position,
        "a": cell.share,
        "r": cell.reliability,
        "block": unit.block,
        "family": cell.family,
        "channel": cell.channel,
    }


def x7_cell(
    index: int,
    out: Path,
    verification: Mapping[str, str],
    sizes: X7Sizes = DECLARED_X7,
) -> dict[str, Any]:
    """One tier-1 cell into the frozen-feature and rich stores; sealed record."""
    unit, position = x7_cells()[index]
    rich_unit = rich_units()[unit.block]
    stores = out / "stores"
    directories = {}
    for label, member in (("x7", unit), ("x7-rich", rich_unit)):
        directory = f.private_directory(stores / member.key)
        ensure_provenance(SealedStore(directory), f.unit_provenance(label, sizes.size))
        directories[label] = directory / f"a{position}"
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    error = rich_error = None
    try:
        rich_error = execute_feature_cell(
            unit,
            position,
            directories["x7"],
            rich_directory=directories["x7-rich"],
            size=sizes.size,
        )
    except ValueError as failure:
        error = repr(failure)
    frozen = _read(directories["x7"] / "result.json")
    rich = _read(directories["x7-rich"] / "result.json")
    seals = {}
    for label, directory in directories.items():
        seal = _read(directory / "seal.json")
        seals[label] = None if seal is None else seal["sha256"]
    return {
        "schema": "ic-study.v4-exploratory-x7-cell.v1",
        "cell": cell_identity(index),
        "sizes": asdict(sizes),
        "verification_sha256": dict(verification),
        "error": error,
        "rich_error": rich_error,
        "success": None if frozen is None else frozen["success"],
        "rich_success": None if rich is None else rich["success"],
        "rich_gap": None if rich is None else rich.get("numerical_gap"),
        "attempts": []
        if frozen is None
        else [attempt["status"] for attempt in frozen["attempts"]],
        "seal_sha256": seals,
        "timing": {
            "started_utc": started,
            "finished_utc": utc_now(),
            "wall_seconds": time.perf_counter() - clock,
            "cpu_seconds": time.process_time() - cpu,
        },
    }


def analyses(out: Path, verification: Mapping[str, str]) -> dict[str, f.Analysis]:
    return {
        "x7": f.Analysis(
            "x7",
            len(x7_cells()),
            asdict(DECLARED_X7),
            lambda index: x7_cell(index, out, verification),
            (MODULE,),
            verification,
            [cell_identity(i) for i in range(len(x7_cells()))],
        )
    }


# Declared reading and aggregate after the release ----------------------------------


def x7_reading(
    frozen: Mapping[str, Any] | None,
    rich: Mapping[str, Any] | None,
    deltas: Mapping[float, Mapping[str, Any]],
) -> str:
    """The declared reading of one r.

    ``far``: the upper end of the a*_rich interval lies below the point
    a*_x7 (a boundary not reached on the grid counts as beyond it), or the
    ΔAUC intervals are above zero at every strength from a*_rich up to, not
    including, a*_x7. ``close``: both boundaries are the same grid strength
    and the ΔAUC intervals there and at its grid neighbours lie inside
    [-0.02, 0.02]. A curve with an invalid null gate makes the r ``invalid``;
    censoring blocks only rules that need the affected first crossing or
    interval. Sustained-boundary censoring is reported separately.
    """
    if frozen is None or rich is None:
        return "unavailable"
    if not (frozen["valid_null_gate"] and rich["valid_null_gate"]):
        return "invalid"
    boundary, ceiling = frozen["first"], rich["first"]
    interval = rich["first_interval"]
    beyond = math.inf if boundary is None else boundary
    upper = None if interval is None else interval[1]
    between = [a for a in GRID if ceiling is not None and ceiling <= a < beyond]
    point_censored = bool(frozen.get("first_censoring") or rich.get("first_censoring"))
    if (
        not frozen.get("first_censoring")
        and not rich.get("first_interval_censoring")
        and upper is not None
        and upper < beyond
    ):
        return "far"
    if (
        not point_censored
        and between
        and all(a in deltas and deltas[a]["interval"][0] > 0 for a in between)
    ):
        return "far"
    if not point_censored and boundary is not None and ceiling == boundary:
        position = GRID.index(boundary)
        around = GRID[max(position - 1, 0) : position + 2]
        if all(
            a in deltas
            and deltas[a]["interval"][0] >= -MARGIN
            and deltas[a]["interval"][1] <= MARGIN
            for a in around
        ):
            return "close"
    if point_censored or rich.get("first_interval_censoring"):
        return "censored"
    return "inconclusive"


def _curve(unit: f.SuccessorUnit, directory: Path) -> dict[str, object]:
    curve = complete_curve(unit, directory)
    if not (directory / "seal.json").exists():
        SealedStore(directory).seal()
    return curve


def _scores(directory: Path) -> tuple[Floats, Floats]:
    store = SealedStore(directory)
    left, right = store.get_array("scores0"), store.get_array("scores1")
    if left is None or right is None:
        raise ValueError("Successful cell has missing curve scores")
    return left, right


def paired_deltas(
    unit: f.SuccessorUnit,
    rich_unit: f.SuccessorUnit,
    stores: Path,
    records: list[dict[str, Any]],
) -> dict[float, dict[str, Any]]:
    """ΔAUC = AUC_rich - AUC_x7 per strength with a paired network bootstrap.

    The resampled network indices are the same in both contrasts and, from
    the unit's own stream, at every strength of the r.
    """
    deltas = {}
    seed = unit.seeds.seed("bootstrap", "resample", 0)
    for record in records:
        if not (record["success"] and record["rich_success"]):
            continue
        position = record["cell"]["position"]
        frozen = _scores(stores / unit.key / f"a{position}")
        rich = _scores(stores / rich_unit.key / f"a{position}")
        draws = f.paired_network_bootstrap(
            [frozen, rich], seed=seed, resamples=RESAMPLES
        )
        point = auc(rich[0].ravel(), rich[1].ravel()) - auc(
            frozen[0].ravel(), frozen[1].ravel()
        )
        deltas[record["cell"]["a"]] = {
            "delta": point,
            "interval": f.percentile_interval(draws[:, 1] - draws[:, 0]),
            "auc_x7": auc(frozen[0].ravel(), frozen[1].ravel()),
            "auc_rich": auc(rich[0].ravel(), rich[1].ravel()),
        }
    return deltas


BOUNDARY_KEYS = (
    "status",
    "valid_null_gate",
    "gap_count",
    "first",
    "first_interval",
    "sustained",
    "sustained_interval",
    "first_censoring",
    "first_interval_censoring",
    "sustained_censoring",
    "sustained_interval_censoring",
    "available_strengths",
    "auc",
    "lower",
    "upper",
)


def validate_store_seals(out: Path, records: Mapping[int, Mapping[str, Any]]) -> None:
    for index, record in records.items():
        unit, position = x7_cells()[index]
        rich = rich_units()[unit.block]
        for label, member, success, error in (
            ("x7", unit, record.get("success"), record.get("error")),
            ("x7-rich", rich, record.get("rich_success"), record.get("rich_error")),
        ):
            if success is None or error:
                continue
            path = out / "stores" / member.key / f"a{position}" / "seal.json"
            seal = _read(path)
            expected = record.get("seal_sha256", {}).get(label)
            if (
                seal is None
                or not expected
                or seal["sha256"] != expected
                or hashlib.sha256(
                    json.dumps(seal["files"], sort_keys=True).encode()
                ).hexdigest()
                != expected
            ):
                raise ValueError(f"Incompatible store seal {label} cell {index}")


def aggregate_x7(
    out: Path, sizes: X7Sizes = DECLARED_X7, *, now: datetime | None = None
) -> dict[str, Any]:
    """Frozen ``complete_curve`` on both store sets per r, ΔAUC and the reading."""
    release = f.require_release(now=now)
    cells = x7_cells()
    records, incomplete = f.complete_records(
        out,
        "x7",
        len(cells),
        asdict(sizes),
        now=now,
        legacy_spec=PRECONDITION,
        preconditions=SUITE.preconditions,
        identities=[cell_identity(i) for i in range(len(cells))],
    )
    validate_store_seals(out, records)
    stores = out / "stores"
    rows = []
    for unit, rich_unit in zip(x7_units(), rich_units(), strict=True):
        group = [records.get(9 * unit.block + k) for k in range(len(GRID))]
        row: dict[str, Any] = {"r": unit.cells[0].reliability, "unit": unit.key}
        present = [record for record in group if record is not None]
        if len(present) < len(GRID):
            rows.append({**row, "status": "incomplete"})
            continue
        errors = {r["cell"]["a"]: r["error"] for r in present if r["error"]}
        rich_errors = {
            r["cell"]["a"]: r["rich_error"] for r in present if r["rich_error"]
        }
        frozen = None if errors else _curve(unit, stores / unit.key)
        rich = (
            None if errors or rich_errors else _curve(rich_unit, stores / rich_unit.key)
        )
        deltas = paired_deltas(unit, rich_unit, stores, present) if frozen else {}
        rows.append(
            {
                **row,
                "errors": errors,
                "rich_errors": rich_errors,
                "rich_gaps": {
                    r["cell"]["a"]: r["rich_gap"] for r in present if r["rich_gap"]
                },
                "x7": None
                if frozen is None
                else {k: frozen.get(k) for k in BOUNDARY_KEYS},
                "rich": None
                if rich is None
                else {k: rich.get(k) for k in BOUNDARY_KEYS},
                "delta_auc": [{"a": a, **value} for a, value in sorted(deltas.items())],
                "reading": x7_reading(frozen, rich, deltas),
            }
        )
    values = list(records.values())
    return {
        "schema": "ic-study.v4-exploratory-x7.v1",
        "compatibility": f.compatibility_summary(out),
        "label": f.LABEL,
        "estimands": {
            "x7": "a*_x7(r): frozen LDA on L3..L5, frozen rules, exploratory seeds",
            "rich": "a*_rich(r): frozen LDA code on the 36 declared features",
        },
        "release": release,
        "declaration": f.declaration_digests(),
        "sizes": asdict(sizes),
        "bootstrap": {"resamples": RESAMPLES, "paired": True, "margin": MARGIN},
        "summary": [
            {k: row.get(k) for k in ("r", "unit", "status", "reading")} for row in rows
        ],
        "incomplete": incomplete,
        "seeds": {**f.SEEDS, "analysis": "x7", "common_across_strengths": True},
        "verification_sha256": sorted(
            {json.dumps(r["verification_sha256"], sort_keys=True) for r in values}
        ),
        "code": f.shared_provenance(values, "code"),
        "successor": f.shared_provenance(values, "successor"),
        "host": f.shared_provenance(values, "host"),
        "timing": f.timing_summary(values),
        "units": rows,
        "cells": [{k: v for k, v in r.items() if k != "provenance"} for r in values],
    }


# Timing probe -------------------------------------------------------------------------


def probe(count: int) -> dict[str, Any]:
    """CPU seconds per panel with seeds outside every namespace; panels discarded."""
    seed = f.probe_seed

    def null_panel(index: int) -> tuple[Floats, Integers]:
        latent = null(
            SIZE,
            WAVES,
            seed("state", index),
            seed("null-state", index),
            family="B",
            phi=0.85,
            eta=0.1,
        )
        return latent, observed_channel(
            latent, 0.7, seed("mask", index), seed("error", index)
        )

    panels = [null_panel(index) for index in range(count)]
    return {
        "size": SIZE,
        "count": count,
        "cpu_seconds_per_panel": {
            "null-B-frozen-profile": f.cpu_per_call(
                lambda i: frozen_profile(*null_panel(i)), count
            ),
            "rich-extraction": f.cpu_per_call(
                lambda i: rich_features(*panels[i]), count
            ),
        },
    }


SUITE = f.Suite(
    "x7",
    True,
    ("x7",),
    (PRECONDITION,),
    analyses,
    aggregate_x7,
    probe,
    (MODULE,),
)


def main(argv: list[str] | None = None) -> int:
    return f.main(SUITE, argv)


if __name__ == "__main__":
    raise SystemExit(main())
