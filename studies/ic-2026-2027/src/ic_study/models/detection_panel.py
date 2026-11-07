"""Decision-14 dynamic kernels and explicitly separate observation channels."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ic_study.models.anchored_panel import Floats, Integers, normal_ranks


def bounded_drift(values: Floats, partners: Integers, repulsion: float) -> Floats:
    gap = values[partners] - values[:, None]
    return np.where(np.abs(gap) <= 1, gap, -repulsion * gap).mean(axis=1)


def null_panel(size: int, waves: int, seed: int, *, rho: float, trait: float) -> Floats:
    """Stationary Gaussian Z=sqrt(trait)*T+sqrt(1-trait)*AR(rho)."""
    if not 0 <= trait < 1 or not 0 <= rho < 1:
        raise ValueError("Invalid stationary null")
    rng = np.random.default_rng(seed)
    fixed, state = rng.normal(size=(2, size))
    out = np.empty((waves, size))
    for t in range(waves):
        if t:
            state = rho * state + np.sqrt(1 - rho**2) * rng.normal(size=size)
        out[t] = np.sqrt(trait) * fixed + np.sqrt(1 - trait) * state
    return out


def influence_update(
    values: Floats,
    partners: Integers,
    noise: Floats,
    *,
    rho: float,
    share: float,
    repulsion: float,
) -> Floats:
    drift = bounded_drift(values, partners, repulsion)
    scale = float(drift.std())
    if share > 0 and scale < 1e-12:
        raise ValueError("Degenerate drift cannot receive a variance share")
    drift = (drift - drift.mean()) / max(scale, 1e-12)
    innovation = np.sqrt(share) * drift + np.sqrt(1 - share) * noise
    return np.asarray(rho * values + np.sqrt(1 - rho**2) * innovation, dtype=np.float64)


def influence_panel(
    size: int,
    waves: int,
    state_seed: int,
    network_seed: int,
    *,
    share: float,
    rho: float = 0.85,
    repulsion: float = 0,
    anchor: float = 0,
    interactions: int = 1,
) -> Floats:
    """Allocate the innovation budget between standardized drift and fresh noise.

    Share is defined before marginal transport; it is not a fitted classifier
    parameter or the fraction of total post-transport change variance.
    """
    if not 0 <= share < 1 or not 0 <= anchor <= 1 or interactions < 1:
        raise ValueError("Invalid innovation share or anchoring")
    rng = np.random.default_rng(state_seed)
    partners = None
    if share:
        network = np.random.default_rng(network_seed)
        # Eight independent permutations; self-loops and repeated partners are allowed.
        partners = np.stack([network.permutation(size) for _ in range(8)], axis=1)
    z = normal_ranks(rng.normal(size=size))
    initial = z.copy()
    out = [z]
    for _ in range(1, waves):
        for _ in range(interactions):
            noise = rng.normal(size=size)
            if partners is None:
                updated = rho * z + np.sqrt(1 - rho**2) * noise
            else:
                updated = influence_update(
                    z,
                    partners,
                    noise,
                    rho=rho,
                    share=share,
                    repulsion=repulsion,
                )
            z = normal_ranks((1 - anchor) * updated + anchor * initial)
        out.append(z)
    return np.stack(out)


def measurement(
    latent: Floats,
    reliability: float | Floats,
    seed: int,
    *,
    heteroscedastic: bool = False,
    error_correlation: float = 0,
) -> Floats:
    if (
        np.any(np.asarray(reliability) <= 0)
        or np.any(np.asarray(reliability) > 1)
        or not 0 <= error_correlation <= 1
    ):
        raise ValueError("Invalid reliability")
    scale = np.ones_like(latent)
    if heteroscedastic:
        scale = 1 + 2 * np.exp(-(latent**2) / 2)
        scale /= np.sqrt(np.mean(scale**2))
    rng = np.random.default_rng(seed)
    noise = rng.normal(size=latent.shape)
    if error_correlation:
        style = rng.normal(size=latent.shape[1])
        noise = (
            np.sqrt(1 - error_correlation) * noise + np.sqrt(error_correlation) * style
        )
    return np.asarray(
        np.sqrt(reliability) * latent + np.sqrt(1 - reliability) * scale * noise,
        dtype=np.float64,
    )


def ordinal_channel(
    measured: Floats,
    mask: NDArray[np.bool_],
    *,
    midpoint_mass: float = 0,
    heap_seed: int | None = None,
) -> Integers:
    """Observed-wave quantile transport to common margins, with optional heaping.

    Midpoint mass defines the common target for BOTH arms in the heaping
    comparison. Only the heaping null receives a heap_seed (10% at w=0).
    Ties are shuffled independently before stable sorting.
    """
    if measured.shape != mask.shape or not 0 <= midpoint_mass < 1:
        raise ValueError("Invalid observation geometry")
    rng = np.random.default_rng(heap_seed) if heap_seed is not None else None
    probabilities = np.full(11, (1 - midpoint_mass) / 11)
    probabilities[5] += midpoint_mass
    cuts = np.cumsum(probabilities)[:-1]
    out = np.full(measured.shape, -1, dtype=np.int64)
    for t, row in enumerate(measured):
        indices = np.flatnonzero(mask[t])
        values = row[indices].copy()
        if rng is not None:
            values[rng.random(len(values)) < 0.1] = 0
            shuffle = rng.permutation(len(values))
        else:
            shuffle = np.arange(len(values))
        order = shuffle[np.argsort(values[shuffle], kind="stable")]
        categories = np.searchsorted(cuts, (np.arange(len(values)) + 0.5) / len(values))
        out[t, indices[order]] = categories
    return out


def state_persistence(values: Floats, center: float, width: float) -> Floats:
    """Persistence increases away from the midpoint, with no network exposure."""
    if not 0 <= center < 1 or width <= 0:
        raise ValueError("Invalid state-dependent persistence")
    return np.asarray(1 - (1 - center) * np.exp(-(values**2) / (2 * width**2)))


def state_dependent_panel(
    size: int,
    waves: int,
    seed: int,
    *,
    center: float,
    width: float = 1,
    heterogeneity: float = 1,
) -> Floats:
    rng = np.random.default_rng(seed)
    z = normal_ranks(rng.normal(size=size))
    out = [z]
    for _ in range(1, waves):
        if not 0 <= heterogeneity <= 1:
            raise ValueError("Invalid persistence heterogeneity")
        persistence = center + heterogeneity * (
            state_persistence(z, center, width) - center
        )
        z = normal_ranks(
            persistence * z + np.sqrt(1 - persistence**2) * rng.normal(size=size)
        )
        out.append(z)
    return np.stack(out)


def tenure_reliability(mask: NDArray[np.bool_], baseline: float, gain: float) -> Floats:
    """Gain per ten completed annual interviews, resetting at cohort entry."""
    if not 0 < baseline <= 1 or gain < 0:
        raise ValueError("Invalid tenure reliability")
    tenure = np.maximum(np.cumsum(mask, axis=0) - 1, 0)
    return np.asarray(np.minimum(0.95, baseline + gain * tenure / 10), dtype=np.float64)


def mover_stayer_panel(
    size: int,
    waves: int,
    seed: int,
    *,
    rho: float,
    stayers: float,
) -> Floats:
    if not 0 <= stayers <= 1 or not 0 <= rho < 1:
        raise ValueError("Invalid mover-stayer parameters")
    rng = np.random.default_rng(seed)
    stable = rng.random(size) < stayers
    z = rng.normal(size=size)
    out = [z]
    for _ in range(1, waves):
        z = np.where(stable, z, rho * z + np.sqrt(1 - rho**2) * rng.normal(size=size))
        out.append(z)
    return np.stack(out)
