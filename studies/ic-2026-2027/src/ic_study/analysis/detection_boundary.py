"""Continuous-score detection boundaries and observed-scale nuisance matching."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

from ic_study.models.anchored_panel import Floats, Integers
from ic_study.models.detection_panel import ordinal_channel


def auc(null_scores: Floats, influence_scores: Floats) -> float:
    """Mann-Whitney probability; large scores mean the influence-like arm."""
    if not len(null_scores) or not len(influence_scores):
        raise ValueError("Both score samples required")
    ordered = np.sort(null_scores)
    lower = np.searchsorted(ordered, influence_scores, side="left")
    upper = np.searchsorted(ordered, influence_scores, side="right")
    return float(np.mean((lower + upper) / (2 * len(ordered))))


def boundary(grid: Floats, values: Floats, target: float = 0.7) -> float | None:
    if grid.shape != values.shape or np.any(np.diff(grid) <= 0):
        raise ValueError("Require a strictly increasing paired grid")
    hit = np.flatnonzero(values >= target)
    return float(grid[hit[0]]) if len(hit) else None


def lag_profile(panel: Floats) -> Floats:
    out = []
    for lag in range(1, min(6, len(panel))):
        x, y = panel[:-lag].ravel(), panel[lag:].ravel()
        valid = np.isfinite(x) & np.isfinite(y)
        out.append(float(np.corrcoef(x[valid], y[valid])[0, 1]))
    return np.array(out)


def midranks(panel: Floats) -> Floats:
    out = np.full_like(panel, np.nan)
    for t, row in enumerate(panel):
        valid = np.isfinite(row)
        _, inverse, counts = np.unique(
            row[valid], return_inverse=True, return_counts=True
        )
        ranks = (np.cumsum(counts) - counts / 2) / counts.sum()
        out[t, valid] = ranks[inverse]
    return out


def _finite_mean(values: Floats) -> float:
    finite = values[np.isfinite(values)]
    return float(finite.mean()) if len(finite) else float("nan")


def feature_channels(
    latent: Floats,
    observed: Integers,
    *,
    midpoint_mass: float = 0,
) -> dict[str, Floats]:
    """Lag decay and mobility are separate; lag 1 is reserved for matching."""
    mask = observed >= 0
    ordinal_one = ordinal_channel(latent, mask, midpoint_mass=midpoint_mass)
    scales = {
        "latent": np.where(mask, latent, np.nan),
        "ordinal_one": np.where(mask, ordinal_one, np.nan),
        "observed": np.where(mask, observed, np.nan),
    }
    out = {key: lag_profile(values) for key, values in scales.items()}
    out["latent_rank"] = lag_profile(midranks(scales["latent"]))
    for key, values in scales.items():
        position = midranks(values)[:-1]
        change = np.abs(values[1:] - values[:-1])
        out[key + "_mobility"] = np.array(
            [
                _finite_mean(change[(position >= lo) & (position < hi)])
                for lo, hi in ((0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.01))
            ]
        )
    return out


@dataclass(frozen=True)
class Match:
    rho: float
    values: Floats
    tolerance: float
    evaluations: int


def match_lag1(
    target: Floats,
    evaluate: Callable[[float], Floats],
    bracket: tuple[float, float],
    *,
    max_evaluations: int = 16,
) -> Match:
    """Common-realisation root search on the EXACT observed per-panel lag 1.

    A failed bracket or exhausted fixed budget fails closed. No accuracy is
    available to this routine. Matching uncertainty remains in target/values.
    """
    if len(target) < 256:
        raise ValueError("Require at least 256 matching realisations")
    lo, hi = bracket
    target_mean = float(target.mean())
    lower_error, upper_error = 0.0, 0.0
    for iteration in range(max_evaluations):
        if iteration == 0:
            rho = lo
        elif iteration == 1:
            rho = hi
        else:
            rho = lo + (hi - lo) * (-lower_error) / (upper_error - lower_error)
        values = evaluate(rho)
        if values.shape != target.shape:
            raise ValueError("Matching realisations must have equal counts")
        tolerance = min(
            0.0003, 0.1 * float(target.std(ddof=1)), 0.1 * float(values.std(ddof=1))
        )
        difference = float(values.mean()) - target_mean
        if abs(difference) <= tolerance:
            return Match(rho, values, tolerance, iteration + 1)
        if (iteration == 0 and difference > 0) or (iteration == 1 and difference < 0):
            raise ValueError("Matching target outside bracket")
        if difference > 0:
            hi, upper_error = rho, difference
        else:
            lo, lower_error = rho, difference
    raise ValueError("Observed lag-1 matching did not reach protocol tolerance")


def studentised_band(
    estimate: Floats,
    standard_error: Floats,
    replicates: Floats,
    replicate_se: Floats,
    *,
    coverage: float = 0.95,
    effective_n: int = 2000,
) -> tuple[Floats, Floats]:
    """Logit max-t over strengths (last axis), separately for each reliability.

    SE floor 1/(2n) is on the AUC scale, before the delta-method logit transform.
    The Bonferroni-normal critical floor prevents a degenerate bootstrap from
    collapsing an interval even when all scores/replicates are tied or saturated.
    """
    if effective_n < 2 or not 0 < coverage < 1:
        raise ValueError("Invalid effective network count or coverage")
    if replicates.shape != replicate_se.shape or replicates.shape[1:] != estimate.shape:
        raise ValueError("Bootstrap arrays do not align")
    if any(
        not np.all(np.isfinite(v))
        for v in (estimate, standard_error, replicates, replicate_se)
    ):
        raise ValueError("Nonfinite inference input")
    floor = 1 / (2 * effective_n)
    point = np.clip(estimate, floor, 1 - floor)
    draws = np.clip(replicates, floor, 1 - floor)
    logit = np.log(point / (1 - point))
    logit_draws = np.log(draws / (1 - draws))
    se = np.maximum(standard_error, floor) / (point * (1 - point))
    draw_se = np.maximum(replicate_se, floor) / (draws * (1 - draws))
    maximum = np.max(np.abs(logit_draws - logit) / draw_se, axis=-1)
    empirical = np.quantile(maximum, coverage, axis=0, method="higher")
    normal_floor = NormalDist().inv_cdf(1 - (1 - coverage) / (2 * estimate.shape[-1]))
    critical = np.maximum(empirical, normal_floor)[..., None]
    low = 1 / (1 + np.exp(np.clip(-logit + critical * se, -700, 700)))
    high = 1 / (1 + np.exp(np.clip(-logit - critical * se, -700, 700)))
    return np.asarray(np.where(estimate == 0, 0, low)), np.asarray(
        np.where(estimate == 1, 1, high)
    )


@dataclass(frozen=True)
class JointMatch:
    rho: float
    trait: float
    values: Floats
    tolerance: Floats
    evaluations: int


def match_observed_lags(
    target: Floats,
    evaluate: Callable[[float, float], Floats],
    *,
    max_evaluations: int = 64,
) -> JointMatch:
    """Bounded two-moment numerical fit with common-random-number evaluations.

    Both columns are protocol-scale per-panel correlations, never latent
    proxies for an observed target. No classifier or accuracy is accessible.
    """
    if target.ndim != 2 or target.shape[0] < 256 or target.shape[1] != 2:
        raise ValueError("Require >=256 paired lag-1/lag-2 realisations")
    base_tolerance = np.minimum(0.0003, 0.1 * target.std(axis=0, ddof=1))
    if not np.all(np.isfinite(target)) or np.any(base_tolerance <= 0):
        raise ValueError("Degenerate matching target")
    calls = 0

    def residual(parameters: Floats) -> tuple[Floats, Floats, Floats]:
        nonlocal calls
        if calls >= max_evaluations:
            raise ValueError("Joint observed matching exhausted its fixed budget")
        values = evaluate(float(parameters[0]), float(parameters[1]))
        calls += 1
        if values.shape != target.shape or not np.all(np.isfinite(values)):
            raise ValueError("Invalid observed matching realisations")
        tolerance = np.minimum(base_tolerance, 0.1 * values.std(axis=0, ddof=1))
        if np.any(tolerance <= 0):
            raise ValueError("Degenerate matching dispersion")
        return values.mean(0) - target.mean(0), values, tolerance

    parameters = np.array([0.8, 0.1])
    error, values, tolerance = residual(parameters)
    while True:
        if np.all(np.abs(error) <= tolerance):
            return JointMatch(
                float(parameters[0]), float(parameters[1]), values, tolerance, calls
            )
        jacobian = np.empty((2, 2))
        for j, bound in enumerate((0.999, 0.8)):
            trial = parameters.copy()
            trial[j] += 0.005 if parameters[j] + 0.005 <= bound else -0.005
            trial_error, _, _ = residual(trial)
            jacobian[:, j] = (trial_error - error) / (trial[j] - parameters[j])
        step = np.linalg.lstsq(jacobian, -error, rcond=None)[0]
        old_loss = float(np.sum((error / tolerance) ** 2))
        improved = False
        for weight in (1.0, 0.5, 0.25, 0.125):
            trial = np.clip(parameters + weight * step, [0, 0], [0.999, 0.8])
            candidate, candidate_values, candidate_tolerance = residual(trial)
            if float(np.sum((candidate / candidate_tolerance) ** 2)) < old_loss:
                parameters, error = trial, candidate
                values, tolerance = candidate_values, candidate_tolerance
                improved = True
                break
        if not improved:
            raise ValueError("Joint observed matching cannot meet both tolerances")


def sustained_boundary(
    grid: Floats, values: Floats, target: float = 0.7
) -> float | None:
    return boundary(grid, np.minimum.accumulate(values[::-1])[::-1], target)


def boundary_report(
    grid: Floats,
    estimate: Floats,
    lower: Floats,
    upper: Floats,
    target: float = 0.7,
) -> dict[str, object]:
    if grid[0] != 0 or not (grid.shape == estimate.shape == lower.shape == upper.shape):
        raise ValueError("Aligned strength grid must start at zero")
    valid = bool(lower[0] <= 0.5 <= upper[0])
    report: dict[str, object] = {
        "valid_null_gate": valid,
        "nonmonotone_band": bool(
            np.any(np.diff(lower) < 0) or np.any(np.diff(upper) < 0)
        ),
        "first": None,
        "sustained": None,
        "first_interval": None,
        "sustained_interval": None,
    }
    if valid:
        report.update(
            {
                "first": boundary(grid, estimate, target),
                "sustained": sustained_boundary(grid, estimate, target),
                "first_interval": (
                    boundary(grid, upper, target),
                    boundary(grid, lower, target),
                ),
                "sustained_interval": (
                    sustained_boundary(grid, upper, target),
                    sustained_boundary(grid, lower, target),
                ),
            }
        )
    return report


@dataclass(frozen=True)
class ScoreUncertainty:
    point: Floats
    conditional_se: Floats
    se: Floats
    replicates: Floats


def fixed_score_uncertainty(
    null_scores: Floats,
    influence_scores: Floats,
    nuisance: Floats,
    *,
    seed: int,
    draws: int = 2000,
) -> ScoreUncertainty:
    """Network-cluster bootstrap plus independent rematch/retrain dispersion.

    Score shape: (network, event, strength); nuisance: (30..50 refits, strength).
    Each nuisance row is evaluated on the same large reference seed population,
    regenerated under its fitted null; it must not contain fresh test sampling.
    The nuisance variance is NOT divided by the number of nuisance refits.
    """
    if (
        null_scores.ndim != 3
        or influence_scores.ndim != 3
        or null_scores.shape[-1] != influence_scores.shape[-1]
        or min(len(null_scores), len(influence_scores)) < 2
        or draws < 2
    ):
        raise ValueError("Require independent networks, events, and paired cells")
    if (
        nuisance.ndim != 2
        or not 30 <= len(nuisance) <= 50
        or nuisance.shape[1] != null_scores.shape[2]
    ):
        raise ValueError("Require 30 to 50 independent nuisance refits")
    rng = np.random.default_rng(seed)
    count = null_scores.shape[-1]
    point = np.array(
        [
            auc(null_scores[..., k].ravel(), influence_scores[..., k].ravel())
            for k in range(count)
        ]
    )
    fixed = np.empty((draws, count))
    for b in range(draws):
        left = null_scores[rng.integers(len(null_scores), size=len(null_scores))]
        right = influence_scores[
            rng.integers(len(influence_scores), size=len(influence_scores))
        ]
        fixed[b] = [
            auc(left[..., k].ravel(), right[..., k].ravel()) for k in range(count)
        ]
    conditional = fixed.std(axis=0, ddof=1)
    se = np.sqrt(conditional**2 + nuisance.var(axis=0, ddof=1))
    deviations = (nuisance - nuisance.mean(0)) * np.sqrt(
        len(nuisance) / (len(nuisance) - 1)
    )
    replicates = (
        point
        + fixed
        - fixed.mean(0)
        + deviations[rng.integers(len(nuisance), size=draws)]
    )
    return ScoreUncertainty(point, conditional, se, np.clip(replicates, 0, 1))


def feasible_lag1(
    target: float,
    reliability: float,
    *,
    next_reliability: float | None = None,
    error_correlation: float = 0,
) -> bool:
    """Continuous-channel bound; conservative protocol rule on ordinal targets.

    It is not a universal theorem for arbitrary nonlinear marginal transport.
    Correlated response styles change the bound and must not use the iid cap.
    """
    other = reliability if next_reliability is None else next_reliability
    if (
        not 0 < reliability <= 1
        or not 0 < other <= 1
        or not 0 <= error_correlation <= 1
    ):
        raise ValueError("Invalid reliability bound")
    cap = np.sqrt(reliability * other) + error_correlation * np.sqrt(
        (1 - reliability) * (1 - other)
    )
    return bool(abs(target) <= cap)
