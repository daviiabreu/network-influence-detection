"""Proposal A prototypes: calibration only; no frozen runner imports this module."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from ic_study.models.anchored_panel import Floats, normal_ranks
from ic_study.models.detection_panel import influence_update


def transport_null(
    size: int, waves: int, seed: int, trait_seed: int, *, rho: float, trait: float
) -> Floats:
    if not 0 <= rho <= 0.999 or not 0 <= trait <= 0.8:
        raise ValueError("Invalid transport null parameters")
    state = fast_influence(size, waves, seed, 0, share=0, rho=rho)
    if trait == 0:
        return state
    fixed = np.random.default_rng(trait_seed).normal(size=size)
    return np.stack(
        [fast_ranks(np.sqrt(trait) * fixed + np.sqrt(1 - trait) * x) for x in state]
    )


@lru_cache(maxsize=8)
def rank_grid(size: int) -> Floats:
    grid = normal_ranks(np.arange(size, dtype=float))
    grid.flags.writeable = False
    return grid


def fast_ranks(values: Floats) -> Floats:
    out = np.empty_like(values)
    out[np.argsort(values, kind="stable")] = rank_grid(len(values))
    return out


def fast_influence(
    size: int,
    waves: int,
    seed: int,
    network_seed: int,
    *,
    share: float,
    rho: float = 0.85,
) -> Floats:
    if not 0 <= share < 1 or not 0 <= rho <= 0.999:
        raise ValueError("Invalid kernel parameters")
    rng = np.random.default_rng(seed)
    partners = None
    if share:
        network = np.random.default_rng(network_seed)
        partners = np.stack([network.permutation(size) for _ in range(8)], axis=1)
    z = fast_ranks(rng.normal(size=size))
    out = [z]
    for _ in range(1, waves):
        noise = rng.normal(size=size)
        updated = (
            rho * z + np.sqrt(1 - rho**2) * noise
            if partners is None
            else influence_update(
                z, partners, noise, rho=rho, share=share, repulsion=0.25
            )
        )
        z = fast_ranks(updated)
        out.append(z)
    return np.stack(out)


NAMESPACE = "ic-detection-boundary-amendment-a-20260925-calibration"


def seed_a(block: int, phase: str, role: str, index: int) -> int:
    import hashlib

    if phase not in {"match", "validate", "train", "check", "reference"}:
        raise ValueError("Only calibration phases are available")
    if (
        block < 0
        or index < 0
        or role not in {"state", "trait", "network", "mask", "error"}
    ):
        raise ValueError("Invalid calibration seed material")
    block = 0 if phase == "reference" else block
    material = f"{NAMESPACE}|{block}|{phase}|{role}|{index}"
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


def calibration_profiles(
    share: float,
    reliability: float,
    count: int,
    *,
    block: int,
    phase: str,
    rho: float | None = None,
    trait: float = 0,
    size: int = 10626,
    lags: int = 5,
    start: int = 0,
) -> Floats:
    from ic_study.models.anchored_panel import panel_mask
    from ic_study.models.detection_panel import measurement, ordinal_channel

    if count < 1 or not 1 <= lags <= 5:
        raise ValueError("Require panels and one to five lags")
    rows = np.empty((count, lags))
    for j in range(count):
        i = 2 * (j + start) + (
            1 if rho is None or phase in {"match", "validate"} else 0
        )
        state_seed = seed_a(block, phase, "state", i)
        z = (
            fast_influence(
                size,
                11,
                state_seed,
                seed_a(
                    block,
                    phase,
                    "network",
                    i if phase in {"match", "validate"} else i // 4,
                ),
                share=share,
            )
            if rho is None
            else transport_null(
                size,
                11,
                state_seed,
                seed_a(block, phase, "trait", i),
                rho=rho,
                trait=trait,
            )
        )
        mask = panel_mask(size, 11, seed_a(block, phase, "mask", i), retention=0.89)
        y = ordinal_channel(
            measurement(z, reliability, seed_a(block, phase, "error", i)), mask
        )
        for k in range(1, lags + 1):
            valid = mask[:-k] & mask[k:]
            left, right = y[:-k][valid], y[k:][valid]
            rows[j, k - 1] = np.corrcoef(left, right)[0, 1]
    return rows


@dataclass(frozen=True)
class ConstrainedMatch:
    rho: float
    trait: float
    residual: Floats
    mc_se: Floats
    tolerance: Floats
    evaluations: int
    success: bool


def constrained_match(
    target: Floats,
    evaluate: Callable[[float, float], Floats],
    *,
    mc_multiplier: float = 1,
    max_evaluations: int = 32,
    initial: tuple[float, float] = (0.85, 0.0),
) -> ConstrainedMatch:
    if target.ndim != 2 or target.shape[1] != 2 or len(target) < 256:
        raise ValueError("Require at least 256 two-moment panels")
    if not np.all(np.isfinite(target)) or mc_multiplier < 0 or max_evaluations < 8:
        raise ValueError("Invalid matching inputs")
    calls = 0

    def residual(p: Floats) -> tuple[Floats, Floats, Floats]:
        nonlocal calls
        values = evaluate(float(p[0]), float(p[1]))
        calls += 1
        if values.shape != target.shape or not np.all(np.isfinite(values)):
            raise ValueError("Invalid matching evaluations")
        delta = values - target
        se = delta.std(0, ddof=1) / np.sqrt(len(delta))
        tolerance = np.minimum(0.0003, np.maximum(0.00005, mc_multiplier * se))
        return delta.mean(0), se, tolerance

    p = np.array(initial)
    if np.any(p < 0) or np.any(p > [0.999, 0.8]) or not np.all(np.isfinite(p)):
        raise ValueError("Invalid initial matching parameters")
    error, se, tolerance = residual(p)
    while not np.all(np.abs(error) <= tolerance) and calls + 7 <= max_evaluations:
        jacobian = np.empty((2, 2))
        for j, bound in enumerate((0.999, 0.8)):
            trial = p.copy()
            trial[j] += 0.005 if p[j] + 0.005 <= bound else -0.005
            candidate, _, _ = residual(trial)
            jacobian[:, j] = (candidate - error) / (trial[j] - p[j])
        steps = [np.linalg.lstsq(jacobian, -error, rcond=None)[0]]
        for j in range(2):
            direction = np.zeros(2)
            denom = float(jacobian[:, j] @ jacobian[:, j])
            direction[j] = -float(jacobian[:, j] @ error) / max(denom, 1e-20)
            steps.append(direction)
        candidates = [steps[0], steps[0] / 2, steps[0] / 4, *steps[1:]]
        old_loss = float(error @ error)
        best = None
        for step in candidates:
            trial = np.clip(p + step, [0, 0], [0.999, 0.8])
            candidate, candidate_se, candidate_tolerance = residual(trial)
            loss = float(candidate @ candidate)
            if loss < old_loss:
                old_loss = loss
                best = trial, candidate, candidate_se, candidate_tolerance
            if np.all(np.abs(candidate) <= candidate_tolerance):
                best = trial, candidate, candidate_se, candidate_tolerance
                break
        if best is None:
            break
        p, error, se, tolerance = best
    return ConstrainedMatch(
        float(p[0]),
        float(p[1]),
        error,
        se,
        tolerance,
        calls,
        bool(np.all(np.abs(error) <= tolerance)),
    )


def cluster_auc_se(null: Floats, social: Floats) -> tuple[float, float]:
    if (
        null.ndim != 2
        or social.ndim != 2
        or min(len(null), len(social)) < 2
        or not np.all(np.isfinite(null))
        or not np.all(np.isfinite(social))
    ):
        raise ValueError("Require two finite network-by-event score arrays")
    left, right = np.sort(null.ravel()), np.sort(social.ravel())
    pos = (
        np.searchsorted(left, social, side="left")
        + np.searchsorted(left, social, side="right")
    ) / (2 * left.size)
    neg = 1 - (
        np.searchsorted(right, null, side="left")
        + np.searchsorted(right, null, side="right")
    ) / (2 * right.size)
    variance = pos.mean(1).var(ddof=1) / len(pos) + neg.mean(1).var(ddof=1) / len(neg)
    return float(pos.mean()), float(np.sqrt(variance))


def projected_linear_refit(point: Floats, jacobian: Floats, residual: Floats) -> Floats:
    """Exact box-constrained two-parameter least squares for a local moment map."""
    if point.shape != (2,) or jacobian.shape != (2, 2) or residual.shape != (2,):
        raise ValueError("Require two parameters and two moment equations")
    lower, upper = -point, np.array([0.999, 0.8]) - point
    candidates = [
        np.clip(np.linalg.lstsq(jacobian, -residual, rcond=None)[0], lower, upper)
    ]
    for j in range(2):
        k = 1 - j
        for bound in (lower[j], upper[j]):
            delta = np.zeros(2)
            delta[j] = bound
            col = jacobian[:, k]
            delta[k] = np.clip(
                -float(col @ (residual + jacobian[:, j] * bound))
                / max(float(col @ col), 1e-20),
                lower[k],
                upper[k],
            )
            candidates.append(delta)
    best = min(
        candidates, key=lambda delta: float(np.sum((residual + jacobian @ delta) ** 2))
    )
    return np.asarray(point + best)


def bonferroni_band(
    point: Floats, se: Floats, *, networks: int, cells: int = 9
) -> tuple[Floats, Floats]:
    from statistics import NormalDist

    if (
        point.shape != se.shape
        or networks < 2
        or cells < 1
        or np.any((point < 0) | (point > 1))
        or np.any(se < 0)
        or not np.all(np.isfinite(point))
        or not np.all(np.isfinite(se))
    ):
        raise ValueError("Invalid point estimates or standard errors")
    epsilon = 1 / (2 * networks)
    p = np.clip(point, epsilon, 1 - epsilon)
    logit = np.log(p / (1 - p))
    width = (
        NormalDist().inv_cdf(1 - 0.05 / (2 * cells))
        * np.maximum(se, epsilon)
        / (p * (1 - p))
    )
    low = 1 / (1 + np.exp(np.clip(-logit + width, -700, 700)))
    high = 1 / (1 + np.exp(np.clip(-logit - width, -700, 700)))
    return np.where(point == 0, 0, low), np.where(point == 1, 1, high)


@dataclass(frozen=True)
class LocalNuisance:
    parameters: Floats
    residuals: Floats
    jacobian: Floats
    null_train: Floats
    social_train: Floats
    null_reference: Floats
    social_reference: Floats
    train_derivative: Floats
    reference_derivative: Floats


def local_nuisance_draws(data: LocalNuisance, *, draws: int = 2000) -> Floats:
    """Projected moment bootstrap and linear feature transport, never a full refit."""
    from ic_study.analysis.detection_boundary import auc
    from ic_study.analysis.redesign import fit_discriminant

    if draws < 2 or len(data.residuals) < 256:
        raise ValueError("Require matching panels and at least two draws")
    n0, n1 = len(data.null_train), len(data.social_train)
    if min(n0, n1) < 4 or n0 % 2 or n1 % 2:
        raise ValueError("Training requires two events per network")
    if data.train_derivative.shape != (
        2,
        *data.null_train.shape,
    ) or data.reference_derivative.shape != (2, *data.null_reference.shape):
        raise ValueError("Derivatives must preserve feature geometry")
    rng = np.random.default_rng(seed_a(8000, "check", "state", 0))
    centered = data.residuals - data.residuals.mean(0)
    values = np.empty(draws)
    for b in range(draws):
        moment = centered[rng.integers(len(centered), size=len(centered))].mean(0)
        parameters = projected_linear_refit(data.parameters, data.jacobian, moment)
        delta = parameters - data.parameters
        null = data.null_train + np.einsum("i,ijk->jk", delta, data.train_derivative)
        indices0 = (2 * rng.integers(n0 // 2, size=(n0 // 2, 1)) + np.arange(2)).ravel()
        indices1 = (2 * rng.integers(n1 // 2, size=(n1 // 2, 1)) + np.arange(2)).ravel()
        model = fit_discriminant(
            np.concatenate((null[indices0], data.social_train[indices1])),
            np.repeat([0, 1], [n0, n1]),
        )
        reference = data.null_reference + np.einsum(
            "i,ijk->jk", delta, data.reference_derivative
        )
        values[b] = auc(model.score(reference), model.score(data.social_reference))
    return values


def fixed_jacobian_match(
    target: Floats,
    evaluate: Callable[[float, float], Floats],
    jacobian: Floats,
    *,
    initial: tuple[float, float],
    mc_multiplier: float = 2,
    max_evaluations: int = 12,
) -> ConstrainedMatch:
    """Refit independent moments using a separately calibrated local response map."""
    if target.ndim != 2 or target.shape[1] != 2 or len(target) < 256:
        raise ValueError("Require at least 256 paired two-moment panels")
    if not np.all(np.isfinite(target)) or max_evaluations < 1 or mc_multiplier < 0:
        raise ValueError("Invalid fixed-Jacobian matching inputs")
    p = np.asarray(initial, dtype=float)
    if np.any(p < 0) or np.any(p > [0.999, 0.8]):
        raise ValueError("Invalid initial parameters")
    best: ConstrainedMatch | None = None
    for calls in range(1, max_evaluations + 1):
        values = evaluate(float(p[0]), float(p[1]))
        if values.shape != target.shape or not np.all(np.isfinite(values)):
            raise ValueError("Invalid matching evaluations")
        delta = values - target
        error = delta.mean(0)
        se = delta.std(0, ddof=1) / np.sqrt(len(delta))
        tolerance = np.minimum(0.0003, np.maximum(0.00005, mc_multiplier * se))
        result = ConstrainedMatch(
            float(p[0]),
            float(p[1]),
            error,
            se,
            tolerance,
            calls,
            bool(np.all(np.abs(error) <= tolerance)),
        )
        if best is None or error @ error < best.residual @ best.residual:
            best = result
        if result.success:
            return result
        trial = projected_linear_refit(p, jacobian, error)
        if np.max(np.abs(trial - p)) < 1e-8:
            break
        p = trial
    assert best is not None
    return ConstrainedMatch(
        best.rho, best.trait, best.residual, best.mc_se, best.tolerance, calls, False
    )
