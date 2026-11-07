"""Fixed low-dimensional discriminant and non-extrapolating dose estimator."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise

import numpy as np

from ic_study.models.anchored_panel import Floats, Integers


def critical_dose(
    doses: Sequence[float], probabilities: Sequence[float]
) -> float | None:
    """Equal-weight decreasing PAVA; first interpolated crossing of one half."""
    if len(doses) != len(probabilities) or len(doses) < 2:
        raise ValueError("Require paired doses and rates")
    if any(b <= a for a, b in pairwise(doses)):
        raise ValueError("Doses must increase strictly")
    if any(not 0 <= p <= 1 for p in probabilities):
        raise ValueError("Invalid probability")
    blocks: list[tuple[float, int]] = []
    for value in probabilities:
        blocks.append((float(value), 1))
        while len(blocks) > 1 and blocks[-2][0] < blocks[-1][0]:
            right, nr = blocks.pop()
            left, nl = blocks.pop()
            blocks.append(((left * nl + right * nr) / (nl + nr), nl + nr))
    fitted = [p for p, n in blocks for _ in range(n)]
    if fitted[0] < 0.5 or fitted[-1] > 0.5:
        return None
    for i, value in enumerate(fitted):
        if value == 0.5:
            return doses[i]
        if value < 0.5:
            fraction = (fitted[i - 1] - 0.5) / (fitted[i - 1] - value)
            return doses[i - 1] + fraction * (doses[i] - doses[i - 1])
    return None


def lag_correlation(panel: Floats | Integers, lag: int, *, missing: bool) -> float:
    left, right = panel[:-lag].ravel(), panel[lag:].ravel()
    valid = (left >= 0) & (right >= 0) if missing else np.ones(len(left), dtype=bool)
    if valid.sum() < 3:
        raise ValueError("Insufficient observed pairs")
    a, b = left[valid], right[valid]
    if a.std() == 0 or b.std() == 0:
        raise ValueError("Degenerate observed pairs")
    return float(np.corrcoef(a, b)[0, 1])


def lag_features(panel: Integers) -> Floats:
    return np.array([lag_correlation(panel, lag, missing=True) for lag in range(2, 6)])


@dataclass(frozen=True)
class Discriminant:
    center: Floats
    scale: Floats
    direction: Floats
    midpoint: Floats

    def score(self, features: Floats) -> Floats:
        return ((features - self.center) / self.scale - self.midpoint) @ self.direction


def fit_discriminant(features: Floats, labels: Integers) -> Discriminant:
    if set(labels) != {0, 1} or any(np.sum(labels == k) < 2 for k in (0, 1)):
        raise ValueError("Require two examples from each mechanism")
    center, scale = features.mean(axis=0), features.std(axis=0)
    scale = np.where(scale > 1e-12, scale, 1.0)
    standardized = (features - center) / scale
    means = np.stack([standardized[labels == k].mean(axis=0) for k in (0, 1)])
    residual = standardized - means[labels]
    covariance = residual.T @ residual / (len(features) - 2)
    covariance = 0.8 * covariance + 0.2 * np.eye(features.shape[1])
    direction = np.linalg.solve(covariance, means[1] - means[0])
    return Discriminant(center, scale, direction, means.mean(axis=0))


def balanced_accuracy(scores: Floats, labels: Integers) -> float:
    if set(labels) != {0, 1}:
        raise ValueError("Both classes required")
    correct = np.where(scores == 0, 0.5, (scores > 0) == labels)
    return float(np.mean([correct[labels == k].mean() for k in (0, 1)]))
