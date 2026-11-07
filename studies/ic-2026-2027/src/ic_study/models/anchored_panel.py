"""Rank-normalized social and persistence kernels with a separate survey channel."""

from __future__ import annotations

from functools import lru_cache
from statistics import NormalDist

import numpy as np
from numpy.typing import NDArray

type Floats = NDArray[np.float64]
type Integers = NDArray[np.int64]


@lru_cache(maxsize=8)
def _normal_grid(size: int) -> Floats:
    if size < 4:
        raise ValueError("At least four people required")
    grid = np.array([NormalDist().inv_cdf((i + 0.5) / size) for i in range(size)])
    grid /= grid.std()
    grid.flags.writeable = False
    return grid


def normal_ranks(values: Floats) -> Floats:
    """Keep ranks while assigning the same standardized normal grid each wave."""
    return _normal_grid(len(values))[np.argsort(np.argsort(values, kind="stable"))]


def latent_panel(
    size: int,
    waves: int,
    initial_seed: int,
    network_seed: int,
    event_seed: int,
    *,
    rho: float,
    strength: float,
    repulsion: float = 0.0,
) -> Floats:
    """One synchronous social step per year on a fixed random directed network.

    Each node has eight distinct non-self partners. Rank normalization is part
    of the defined mechanism, not post-hoc adjustment of evaluation data.
    """
    if size < 10 or waves < 2 or not 0 <= rho <= 1 or strength < 0:
        raise ValueError("Invalid panel geometry or kernel")
    if repulsion < 0:
        raise ValueError("Repulsion must be nonnegative")
    network = np.random.default_rng(network_seed)
    offsets = np.empty((size, 8), dtype=np.int64)
    for i in range(size):
        offsets[i] = network.choice(size - 1, 8, replace=False) + 1
    partners = (np.arange(size)[:, None] + offsets) % size
    events = np.random.default_rng(event_seed)
    values = normal_ranks(np.random.default_rng(initial_seed).normal(size=size))
    result = [values]
    for _ in range(waves - 1):
        gap = values[partners] - values[:, None]
        drift = np.where(np.abs(gap) <= 1, gap, -repulsion * gap).mean(axis=1)
        values = normal_ranks(
            rho * values
            + strength * drift
            + np.sqrt(1 - rho**2) * events.normal(size=size)
        )
        result.append(values)
    return np.stack(result)


def panel_mask(
    size: int, waves: int, seed: int, *, retention: float
) -> NDArray[np.bool_]:
    """Two-person household dropout; two thirds enter at 0, remainder at 5."""
    if size % 6 or waves < 6 or not 0 <= retention <= 1:
        raise ValueError("Require size divisible by six and at least six waves")
    rng = np.random.default_rng(seed)
    household_count = size // 2
    entry = np.where(np.arange(household_count) < size // 3, 0, 5)
    active = np.zeros(household_count, dtype=bool)
    mask = []
    for wave in range(waves):
        active &= rng.random(household_count) < retention
        active |= entry == wave
        mask.append(np.repeat(active, 2))
    return np.stack(mask)


def observe(
    latent: Floats, mask: NDArray[np.bool_], reliability: float, seed: int
) -> Integers:
    """Classical Gaussian measurement error, followed by fixed ordinal cutpoints."""
    if not 0 < reliability <= 1 or latent.shape != mask.shape:
        raise ValueError("Invalid reliability or observation mask")
    noise = np.random.default_rng(seed).normal(size=latent.shape)
    measured = latent + np.sqrt((1 - reliability) / reliability) * noise
    thresholds = np.array([NormalDist().inv_cdf(i / 11) for i in range(1, 11)])
    response = np.searchsorted(thresholds, measured * np.sqrt(reliability))
    return np.where(mask, response, -1).astype(np.int64)
