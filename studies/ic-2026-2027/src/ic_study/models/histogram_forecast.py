"""Conditional synthetic forecasts of eleven-bin observed opinion histograms."""

from __future__ import annotations

import hashlib
import json
import random
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction

type Counts = tuple[int, ...]
BOUNDARIES = tuple((k + 0.5) / 10 for k in range(10))


def seed_for(*parts: str | int) -> int:
    payload = json.dumps(parts, ensure_ascii=True, separators=(",", ":")).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:16], "big")


def category(opinion: float) -> int:
    if not 0 <= opinion <= 1:
        raise ValueError("Opinion must be finite and in [0, 1]")
    return bisect_right(BOUNDARIES, opinion)


def validate_counts(counts: Counts) -> None:
    if (
        len(counts) != 11
        or any(type(c) is not int or c < 0 for c in counts)
        or sum(counts) < 1
    ):
        raise ValueError("Require eleven nonnegative integer counts with positive sum")


@dataclass(frozen=True)
class Dynamics:
    activation: float
    drift: float = 0.0
    confidence: float = 0.35
    mu: float = 0.5

    def __post_init__(self) -> None:
        if not 0 <= self.activation <= 1 or self.drift not in (-0.1, 0.0, 0.1):
            raise ValueError("Invalid activation probability or drift")
        if not 0 < self.confidence <= 1 or self.mu != 0.5:
            raise ValueError("Require valid confidence and fixed mu=0.5")
        if self.activation and self.drift:
            raise ValueError("This pilot separates interaction from exogenous drift")


def interact(
    opinions: list[int], i: int, j: int, cutoff_numerator: int, cutoff_denominator: int
) -> None:
    """Exact midpoint in dyadic units; the caller budgets enough powers of two."""
    x, y = opinions[i], opinions[j]
    if abs(x - y) * cutoff_denominator < cutoff_numerator:
        if (x + y) % 2:
            raise ArithmeticError("Insufficient dyadic precision for exact midpoint")
        opinions[i] = opinions[j] = (x + y) // 2


def exact_category(value: int, ticks_per_category: int) -> int:
    if ticks_per_category < 1 or not 0 <= value <= 10 * ticks_per_category:
        raise ValueError("Opinion must be in the declared exact scale")
    return (2 * value + ticks_per_category) // (2 * ticks_per_category)


def draw_histogram(
    observed: Counts,
    dynamics: Dynamics,
    *,
    population: int,
    sample_size: int,
    attempts: int,
    seed: int,
) -> Counts:
    """Draw from the reset kernel, without access to a latent previous population."""
    validate_counts(observed)
    if population < 2 or sample_size < 1 or attempts < 0:
        raise ValueError("Invalid population, observation size or event budget")
    initial_rng = random.Random(seed_for(seed, "initial"))
    event_rng = random.Random(seed_for(seed, "events"))
    sample_rng = random.Random(seed_for(seed, "observation"))
    ticks = 1 << attempts
    opinions = [
        k * ticks
        for k in initial_rng.choices(range(11), weights=observed, k=population)
    ]
    confidence = Fraction(str(dynamics.confidence))
    cutoff_numerator = 10 * ticks * confidence.numerator
    if event_rng.random() < dynamics.activation:
        for _ in range(attempts):
            i = event_rng.randrange(population)
            j = event_rng.randrange(population - 1)
            if j >= i:
                j += 1
            interact(opinions, i, j, cutoff_numerator, confidence.denominator)
    if dynamics.drift:
        shift = ticks if dynamics.drift > 0 else -ticks
        opinions = [min(10 * ticks, max(0, x + shift)) for x in opinions]
    population_bins = [exact_category(x, ticks) for x in opinions]
    counts = [0] * 11
    for k in sample_rng.choices(population_bins, k=sample_size):
        counts[k] += 1
    return tuple(counts)
