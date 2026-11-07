"""Calibration-only orchestration for the D1--D6 successor."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace

import numpy as np

from ic_study.analysis.detection_boundary import (
    feasible_lag1,
    lag_profile,
    midranks,
)
from ic_study.analysis.detection_boundary_v4 import (
    CovarianceDiagnostic,
    NuisanceInput,
    NuisanceResult,
    ProfileFit,
    Uncertainty,
    Validation,
    amplification,
    anchor_nuisance,
    covariance_diagnostic,
    finite_differences,
    mean_feature_jacobian,
    nuisance_draws,
    profile_match,
    score_uncertainty,
    validate_fit,
)
from ic_study.models.anchored_panel import Floats, Integers, panel_mask
from ic_study.models.detection_panel import (
    measurement,
    ordinal_channel,
    tenure_reliability,
)
from ic_study.models.detection_panel_v4 import influence, null
from ic_study.simulation.v4_store import SealedStore

GRID = (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 0.6, 0.9)
RELIABILITIES = (0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9)
ROLES = {"state", "null-state", "network", "mask", "error", "heap"}


@dataclass(frozen=True)
class SeedPlan:
    repetition: int = 0
    block: int = 0
    gate: bool = False

    def seed(self, phase: str, role: str, index: int, *, attempt: int = 0) -> int:
        if phase not in {
            "match",
            "validate",
            "train",
            "check",
            "reference",
            "nuisance",
            "bootstrap",
            "stencil",
        }:
            raise ValueError("Unknown or reserved confirmatory phase")
        if (
            role not in ROLES
            or min(index, self.repetition, self.block, attempt) < 0
            or self.block >= 10000
            or self.repetition >= 10000
            or attempt > 1
        ):
            raise ValueError("Invalid seed material")
        prefix = "ic-detection-boundary-v4"
        if phase in {"validate", "nuisance", "bootstrap", "stencil"}:
            purpose = "validation" if phase == "validate" else phase
            namespace = f"{prefix}-{purpose}-calibration"
            block = (
                int(self.gate) * 100000000 + self.repetition * 10000 + self.block
            ) * 2 + attempt
        else:
            namespace = (
                f"{prefix}-gate-r{self.repetition:04d}-calibration"
                if self.gate
                else f"{prefix}-calibration"
            )
            block = (
                self.block if self.gate else self.repetition * 10000 + self.block
            ) * 2 + attempt
        material = f"{namespace}|{block}|{phase}|{role}|{index}"
        return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


@dataclass(frozen=True)
class Cell:
    share: float
    reliability: float
    family: str = "B"
    channel: str = "observed"
    error_correlation: float = 0
    gain: float = 0
    repulsion: float = 0.25
    anchor: float = 0
    steps: int = 1
    mobility: bool = False

    @property
    def identity(self) -> bool:
        return (
            self.share == 0 and self.family in {"A", "B", "D", "E"} and self.anchor == 0
        )


def selected_features(
    latent: Floats,
    observed: Integers,
    *,
    channel: str,
    mobility: bool = False,
    midpoint_mass: float = 0,
) -> Floats:
    """Extract only the unit's scale and summary; preserve frozen arithmetic."""
    mask = observed >= 0
    if channel == "ordinal_one":
        values = np.where(
            mask, ordinal_channel(latent, mask, midpoint_mass=midpoint_mass), np.nan
        )
    elif channel in {"latent", "latent_rank"}:
        values = np.where(mask, latent, np.nan)
    elif channel == "observed":
        values = np.where(mask, observed, np.nan)
    else:
        raise ValueError("Unknown feature channel")
    if channel == "latent_rank":
        if mobility:
            raise ValueError("Rank mobility is not in the declared inventory")
        values = midranks(values)
    if not mobility:
        return lag_profile(values)
    lags = []
    for lag in (1, 2):
        x, y = values[:-lag].ravel(), values[lag:].ravel()
        valid = np.isfinite(x) & np.isfinite(y)
        lags.append(float(np.corrcoef(x[valid], y[valid])[0, 1]))
    position = midranks(values)[:-1]
    change = np.abs(values[1:] - values[:-1])
    summaries = []
    for lo, hi in ((0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.01)):
        selected = change[(position >= lo) & (position < hi)]
        finite = selected[np.isfinite(selected)]
        summaries.append(float(finite.mean()) if len(finite) else float("nan"))
    return np.concatenate((lags[:2], np.array(summaries)))


class PanelSource:
    def __init__(
        self,
        cell: Cell,
        seeds: SeedPlan,
        *,
        size: int = 10626,
        store: SealedStore | None = None,
    ) -> None:
        if size % 6 or size < 6:
            raise ValueError("Panel size must be divisible by six")
        self.cell, self.seeds, self.size = cell, seeds, size
        self.panels = 0
        self.store = store
        self.provenance = {} if store is None else (store.get_json("provenance") or {})

    def profiles(
        self,
        phase: str,
        count: int,
        *,
        parameters: Floats | None = None,
        attempt: int = 0,
        start: int = 0,
    ) -> Floats:
        if self.store is None:
            return self._profiles(
                phase, count, parameters=parameters, attempt=attempt, start=start
            )
        chunks = []
        for offset in range(start, start + count, 32):
            length = min(32, start + count - offset)
            material = dict(
                cell=asdict(self.cell),
                seeds=asdict(self.seeds),
                size=self.size,
                phase=phase,
                count=length,
                start=offset,
                attempt=attempt,
                parameters=None if parameters is None else parameters.tolist(),
            )
            key = hashlib.sha256(
                json.dumps(material, sort_keys=True).encode()
            ).hexdigest()
            values = self.store.get_array(key)
            if values is None:
                values = self._profiles(
                    phase, length, parameters=parameters, attempt=attempt, start=offset
                )
                self.store.put_array(key, values)
                self.store.append(
                    "phases",
                    {
                        "phase": phase,
                        "attempt": attempt,
                        "seed_material_sha256": key,
                        "code_sha256": self.provenance.get("code_sha256"),
                        "environment_sha256": self.provenance.get("environment_sha256"),
                        "host_sha256": self.provenance.get("host_sha256"),
                        "panels": length,
                    },
                )
            chunks.append(values)
        return np.concatenate(chunks)

    def _profiles(
        self,
        phase: str,
        count: int,
        *,
        parameters: Floats | None = None,
        attempt: int = 0,
        start: int = 0,
    ) -> Floats:
        cell = self.cell
        rows = []
        for j in range(start, start + count):
            coupled = phase in {"match", "validate"}
            index = 2 * j + (1 if coupled or parameters is None else 0)

            def seed(role: str, i: int = index) -> int:
                return self.seeds.seed(phase, role, i, attempt=attempt)

            if parameters is None:
                latent = influence(
                    self.size,
                    11,
                    seed("state"),
                    seed("network", index if coupled else index // 4),
                    share=cell.share,
                    repulsion=cell.repulsion,
                    anchor=cell.anchor,
                    steps=cell.steps,
                )
            else:
                latent = null(
                    self.size,
                    11,
                    seed("state"),
                    seed("null-state"),
                    family=cell.family,
                    phi=float(parameters[0]),
                    eta=float(parameters[1]),
                    steps=cell.steps,
                )
            mask = panel_mask(self.size, 11, seed("mask"), retention=0.89)
            if cell.channel in {"latent", "latent_rank", "ordinal_one"}:
                observed = np.where(mask, 0, -1)
            else:
                reliability: float | Floats = cell.reliability
                if cell.gain:
                    reliability = tenure_reliability(mask, cell.reliability, cell.gain)
                measured = measurement(
                    latent,
                    reliability,
                    seed("error"),
                    heteroscedastic=cell.family == "C" and parameters is not None,
                    error_correlation=cell.error_correlation,
                )
                observed = ordinal_channel(
                    measured,
                    mask,
                    midpoint_mass=0.1 if cell.family == "C" else 0,
                    heap_seed=seed("heap")
                    if cell.family == "C" and parameters is not None
                    else None,
                )
            values = selected_features(
                latent,
                observed,
                channel=cell.channel,
                mobility=cell.mobility,
                midpoint_mass=0.1 if cell.family == "C" else 0,
            )
            rows.append(values)
            self.panels += 1
        return np.stack(rows)


@dataclass(frozen=True)
class FitAttempt:
    count: int
    fit: ProfileFit
    validation: Validation | None


@dataclass(frozen=True)
class ValidatedFit:
    attempts: tuple[FitAttempt, ...]

    @property
    def final(self) -> FitAttempt:
        return self.attempts[-1]

    @property
    def success(self) -> bool:
        return (
            self.final.fit.success
            and self.final.validation is not None
            and self.final.validation.passed
        )


def fit_cell(source: PanelSource, *, fixed_eta: float | None = None) -> ValidatedFit:
    if source.cell.family in {"A", "C"}:
        fixed_eta = 0.0
    attempts = []
    for attempt, count in enumerate((1024, 4096)):
        target = source.profiles("match", count, attempt=attempt)[:, :2]
        cell = source.cell
        cap = min(0.95, cell.reliability + cell.gain) if cell.gain else cell.reliability
        if cell.channel == "observed" and not feasible_lag1(
            float(target[:, 0].mean()), cap, error_correlation=cell.error_correlation
        ):
            status = (
                "family-limit-upper"
                if target[:, 0].mean() > 0
                else "family-limit-lower"
            )
            failure = ProfileFit(
                np.array([0.85, fixed_eta or 0]),
                np.zeros_like(target),
                np.zeros(2),
                np.zeros(2),
                np.zeros(2),
                0,
                status,
                1 if fixed_eta is not None else 2,
            )
            attempts.append(FitAttempt(count, failure, None))
            break

        def evaluate(
            phi: float, eta: float, *, count: int = count, attempt: int = attempt
        ) -> Floats:
            return source.profiles(
                "match", count, parameters=np.array([phi, eta]), attempt=attempt
            )[:, :2]

        fit = profile_match(
            target,
            evaluate,
            identity=source.cell.identity,
            fixed_eta=fixed_eta,
        )
        validation = None
        if fit.success:
            target_validation = source.profiles("validate", 2048, attempt=attempt)
            null_validation = source.profiles(
                "validate", 2048, parameters=fit.parameters, attempt=attempt
            )
            validation = validate_fit(
                (null_validation - target_validation)[:, :2], fit.fitted_moments, fit.se
            )
            if fit.status == "anchor-exact":
                validation = replace(validation, amplification=0.0)
            else:
                base = source.profiles(
                    "match", count, parameters=fit.parameters, attempt=attempt
                )

                def evaluate_stencil(
                    p: Floats, *, count: int = count, attempt: int = attempt
                ) -> Floats:
                    return source.profiles(
                        "match", count, parameters=p, attempt=attempt
                    )

                stencils = finite_differences(
                    evaluate_stencil,
                    fit.parameters,
                    0.01,
                    base,
                    parameters=fit.fitted_moments,
                )
                covariance = (
                    np.cov(null_validation[:, 2:5], rowvar=False)
                    + np.cov(target_validation[:, 2:5], rowvar=False)
                ) / 2
                validation = replace(
                    validation,
                    amplification=amplification(
                        stencils.mean(1).T,
                        validation.residual,
                        covariance,
                        fit.fitted_moments,
                    ),
                )
        attempts.append(FitAttempt(count, fit, validation))
        # D4 retry is for independent-validation failure only, not solver failure.
        if not fit.success or (validation is not None and validation.passed):
            break
    return ValidatedFit(tuple(attempts))


@dataclass(frozen=True)
class PipelineResult:
    fit: ValidatedFit
    uncertainty: Uncertainty | None
    nuisance: tuple[NuisanceResult, ...]
    tie_rate: float
    covariance_diagnostics: tuple[CovarianceDiagnostic, ...] = ()
    scores0: Floats | None = None
    scores1: Floats | None = None
    dependency_gap: bool = False


@dataclass(frozen=True)
class ControlDependency:
    """Observed fit and aligned nuisance coordinates reused by declared controls."""

    parameters: Floats
    eta_shifts: tuple[Floats, ...]
    success: bool


def pipeline(
    source: PanelSource,
    *,
    steps: tuple[float, ...] = (0.01,),
    observed: PipelineResult | ControlDependency | None = None,
    g2_diagnostic: bool = False,
    compute_uncertainty: bool = True,
) -> PipelineResult:
    """Full production denominators; caller must enforce D7's freeze authorization."""
    from ic_study.analysis.redesign import fit_discriminant

    if isinstance(observed, PipelineResult):
        observed = ControlDependency(
            observed.fit.final.fit.parameters,
            tuple(result.shifts[:, 1] for result in observed.nuisance),
            observed.fit.success,
        )
    if source.cell.channel != "observed" and (
        observed is None
        or not observed.success
        or len(observed.eta_shifts) != len(steps)
    ):
        failure = ProfileFit(
            np.array([0.85, 0.0]),
            np.zeros((0, 2)),
            np.zeros(2),
            np.zeros(2),
            np.zeros(2),
            0,
            "dependency-gap",
            1,
        )
        return PipelineResult(
            ValidatedFit((FitAttempt(0, failure, None),)),
            None,
            (),
            0,
            dependency_gap=True,
        )
    inherited = observed.parameters[1] if observed is not None else None
    fit = fit_cell(source, fixed_eta=None if inherited is None else float(inherited))
    if not fit.success:
        return PipelineResult(fit, None, (), 0)
    final = fit.final.fit
    attempt = len(fit.attempts) - 1
    train0 = source.profiles("train", 2000, parameters=final.parameters)[:, 2:5]
    train1 = source.profiles("train", 2000)[:, 2:5]
    model = fit_discriminant(np.concatenate([train0, train1]), np.repeat([0, 1], 2000))
    test0 = model.score(
        source.profiles("check", 4000, parameters=final.parameters)[:, 2:5]
    )
    test1 = model.score(source.profiles("check", 4000)[:, 2:5])
    nuisance_results = []
    covariance_results = []
    if final.status == "anchor-exact":
        nuisance_results = [anchor_nuisance() for _ in steps]
    else:
        reference0 = source.profiles("reference", 4000, parameters=final.parameters)[
            :, 2:5
        ]
        reference1 = source.profiles("reference", 4000)[:, 2:5]
        match0 = source.profiles(
            "match", fit.final.count, parameters=final.parameters, attempt=attempt
        )
        for index, step in enumerate(steps):
            dimensions = 1 if source.cell.family in {"A", "C"} else 2
            match_derivative = mean_feature_jacobian(
                lambda p: source.profiles(
                    "match", fit.final.count, parameters=p, attempt=attempt
                ),
                final.parameters,
                step,
                match0,
                parameters=dimensions,
            )
            inherited_eta = None
            if dimensions == 1:
                inherited_eta = np.zeros(2000)
            elif observed is not None:
                inherited_eta = observed.eta_shifts[index]
            nuisance_results.append(
                nuisance_draws(
                    NuisanceInput(
                        final.parameters,
                        final.differences,
                        match_derivative[:, :2].T,
                        train0,
                        train1,
                        reference0,
                        reference1,
                        match_derivative[:, 2:5],
                    ),
                    seed=source.seeds.seed("nuisance", "state", 0),
                    inherited_eta=inherited_eta,
                )
            )
            covariance = covariance_stencils(
                source,
                final.parameters,
                step,
                enabled=g2_diagnostic,
                dimensions=dimensions,
            )
            if covariance is not None:
                covariance_results.append(
                    covariance_diagnostic(
                        train0,
                        train1,
                        reference0,
                        reference1,
                        *covariance,
                        nuisance_results[-1].shifts,
                        d5_se=float(np.sqrt(nuisance_results[-1].variance)),
                    )
                )
    uncertainty = None
    if compute_uncertainty:
        uncertainty = score_uncertainty(
            test0.reshape(2000, 2, 1),
            test1.reshape(2000, 2, 1),
            nuisance_results[0].centered[:, None],
            seed=source.seeds.seed("bootstrap", "state", 0),
        )
    ordered = np.sort(test0)
    ties = np.searchsorted(ordered, test1, side="right") - np.searchsorted(
        ordered, test1, side="left"
    )
    return PipelineResult(
        fit,
        uncertainty,
        tuple(nuisance_results),
        float(ties.sum() / (len(test0) * len(test1))),
        tuple(covariance_results),
        test0.reshape(2000, 2),
        test1.reshape(2000, 2),
    )


def covariance_stencils(
    source: PanelSource,
    point: Floats,
    step: float,
    *,
    enabled: bool,
    dimensions: int = 2,
) -> tuple[Floats, Floats] | None:
    """Only G2 requests these additional CRN panels; no per-panel drift is retained."""
    if not enabled:
        return None
    results = []
    for phase, count in (("train", 2000), ("reference", 4000)):

        def evaluate(p: Floats, *, phase: str = phase, count: int = count) -> Floats:
            return np.asarray(
                np.cov(
                    source.profiles(phase, count, parameters=p)[:, 2:5], rowvar=False
                )
            )

        baseline = evaluate(point)
        results.append(
            finite_differences(evaluate, point, step, baseline, parameters=dimensions)
        )
    return results[0], results[1]
