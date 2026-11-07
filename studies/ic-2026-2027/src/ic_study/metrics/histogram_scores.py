"""Three different loss targets on a shared ensemble of observed histograms."""

from __future__ import annotations

import math
from itertools import combinations

from ic_study.models.histogram_forecast import Counts, validate_counts

SCORES = ("mean_w1", "central_w1", "energy", "mean_l2", "central_l2")
type Vector = tuple[float, ...]


def frequencies(counts: Counts) -> Vector:
    validate_counts(counts)
    total = sum(counts)
    return tuple(c / total for c in counts)


def wasserstein(left: Vector, right: Vector) -> float:
    """W1 for probabilities at 0, .1, ..., 1; callers validate the simplex."""
    if len(left) != 11 or len(right) != 11:
        raise ValueError("Require eleven categories")
    cumulative = 0.0
    result = 0.0
    for x, y in zip(left[:-1], right[:-1], strict=True):
        cumulative += x - y
        result += abs(cumulative)
    return result / 10


def score_ensemble(ensemble: list[Counts], observed: Counts) -> dict[str, float]:
    if len(ensemble) < 2:
        raise ValueError("Fair energy estimation requires at least two members")
    xs = [frequencies(counts) for counts in ensemble]
    y = frequencies(observed)
    size = len(xs)
    center = tuple(math.fsum(x[k] for x in xs) / size for k in range(11))
    mean_l2 = math.fsum(math.dist(x, y) for x in xs) / size
    return {
        "mean_w1": math.fsum(wasserstein(x, y) for x in xs) / size,
        "central_w1": wasserstein(center, y),
        "energy": mean_l2
        - math.fsum(math.dist(x, z) for x, z in combinations(xs, 2))
        / (size * (size - 1)),
        "mean_l2": mean_l2,
        "central_l2": math.dist(center, y),
    }
