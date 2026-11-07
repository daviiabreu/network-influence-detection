"""Overlapping trio and projected-neighborhood operators with external dose."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ic_study.models.anchored_panel import Floats, Integers


def _partners(size: int, groups: Integers) -> Integers:
    rows: list[list[list[int]]] = [[] for _ in range(size)]
    for group in groups:
        if len(group) != 3 or len(set(group)) != 3:
            raise ValueError("Require distinct members of each trio")
        for node in group:
            if not 0 <= node < size:
                raise ValueError("Invalid node")
            rows[node].append([int(j) for j in group if j != node])
    if not rows[0] or len({len(row) for row in rows}) != 1:
        raise ValueError("Require positive regular incidence")
    return np.array(rows, dtype=np.int64)


def _step(
    values: Floats, partners: Integers, coefficient: float, projected: bool
) -> Floats:
    neighbors = values[partners]
    if projected:
        flat = partners.reshape(len(values), -1)
        opinions = values[flat]
        a, b = np.triu_indices(flat.shape[1], 1)
        distinct = flat[:, a] != flat[:, b]
        gaps = np.abs(opinions[:, a] - opinions[:, b])
        gap = (gaps * distinct).sum(axis=1) / distinct.sum(axis=1)
        drift = np.exp(coefficient * gap) * (opinions.mean(axis=1) - values)
    else:
        gap = np.abs(neighbors[:, :, 0] - neighbors[:, :, 1])
        drift = (
            np.exp(coefficient * gap) * (neighbors.mean(axis=2) - values[:, None])
        ).mean(axis=1)
    return np.asarray(values + 0.1 * drift, dtype=np.float64)


def social_step(
    values: Floats, groups: Integers, coefficient: float, *, projected: bool
) -> Floats:
    if not -2 <= coefficient <= 1 or np.any((values < 0) | (values > 1)):
        raise ValueError("Outside the declared convex operator family")
    return _step(values, _partners(len(values), groups), coefficient, projected)


def make_groups(size: int, seed: int, *, overlap: bool = True) -> Integers:
    """Two random partitions, conditioned on unique trios and connectivity."""
    if size % 3 or size < 6:
        raise ValueError("Require a multiple of three, at least six nodes")
    rng = np.random.default_rng(seed)
    for _ in range(10000):
        groups = np.concatenate(
            [rng.permutation(size).reshape(-1, 3) for _ in range(2 if overlap else 1)]
        )
        if len({tuple(sorted(g)) for g in groups}) != len(groups):
            continue
        partners = _partners(size, groups).reshape(size, -1)
        seen = {0}
        pending = [0]
        while pending:
            for node in partners[pending.pop()]:
                if int(node) not in seen:
                    seen.add(int(node))
                    pending.append(int(node))
        if not overlap or len(seen) == size:
            return groups
    raise RuntimeError("Network rejection budget exhausted")


def classify_window(window: Floats) -> str:
    if np.all((window < 0.5).mean(axis=1) >= 0.5):
        return "locked"
    if np.all((window > 0.75).mean(axis=1) >= 0.9):
        return "resolved"
    return "unresolved"


@dataclass(frozen=True)
class DoseOutcome:
    status: str
    final_mean: float


def run_dose(
    initial: Floats,
    groups: Integers,
    recipients: Integers,
    dose: float,
    coefficient: float,
    *,
    projected: bool,
    horizon: int = 100,
) -> DoseOutcome:
    if not 0 <= dose <= 1 or horizon < 5 or not -2 <= coefficient <= 1:
        raise ValueError("Invalid dose, horizon or nonlinearity")
    partners = _partners(len(initial), groups)
    values = initial.copy()
    window = []
    for step in range(horizon):
        values = _step(values, partners, coefficient, projected)
        values[recipients] += dose * (1 - values[recipients])
        if step >= horizon - max(1, horizon // 5):
            window.append(values.copy())
    return DoseOutcome(classify_window(np.stack(window)), float(values.mean()))
