"""Symmetric fixed-graph DW dynamics with optional adaptive edge exposure."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

type Edge = tuple[int, int]


@dataclass(frozen=True)
class Parameters:
    confidence: float
    mu: float = 0.5
    initial_weight: float = 0.5
    gamma: float = 0.5
    delta: float = 0.5

    def __post_init__(self) -> None:
        if not 0 < self.confidence <= 1 or not 0 < self.mu <= 0.5:
            raise ValueError("Require 0 < confidence <= 1 and 0 < mu <= 0.5")
        if not 0 < self.initial_weight <= 1 or not 0 < self.delta <= 1:
            raise ValueError("Initial weight and delta must be in (0, 1]")
        if not 0 <= self.gamma <= 1:
            raise ValueError("Gamma must be in [0, 1]")


class WeightedEdges:
    """Binary sum tree, recomputing parent sums after each weight replacement."""

    def __init__(self, count: int, weight: float) -> None:
        if count < 1 or not 0 < weight <= 1:
            raise ValueError("Require nonempty positive weights")
        self.count = count
        self.offset = 1 << (count - 1).bit_length()
        self.tree = [0.0] * (2 * self.offset)
        self.tree[self.offset : self.offset + count] = [weight] * count
        for i in range(self.offset - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def weight(self, index: int) -> float:
        return self.tree[self.offset + index]

    def replace(self, index: int, weight: float) -> None:
        if not math.isfinite(weight) or weight <= 0:
            raise ArithmeticError("Edge weight underflow or invalid weight")
        i = self.offset + index
        self.tree[i] = weight
        while i > 1:
            i //= 2
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def select(self, unit_uniform: float) -> int:
        if not 0 <= unit_uniform < 1:
            raise ValueError("Require unit uniform in [0, 1)")
        value = min(
            unit_uniform * self.tree[1], math.nextafter(self.tree[1], -math.inf)
        )
        i = 1
        while i < self.offset:
            left = 2 * i
            if value < self.tree[left]:
                i = left
            else:
                value -= self.tree[left]
                i = left + 1
            value = min(value, math.nextafter(self.tree[i], -math.inf))
        index = i - self.offset
        if index >= self.count or self.weight(index) <= 0:
            raise ArithmeticError("Weighted selection reached an empty leaf")
        return index


class State:
    def __init__(
        self, opinions: list[float], edges: list[Edge], parameters: Parameters
    ) -> None:
        if not opinions or any(not 0 <= x <= 1 for x in opinions):
            raise ValueError("Require finite opinions in [0, 1]")
        if len(set(edges)) != len(edges) or any(
            not 0 <= i < j < len(opinions) for i, j in edges
        ):
            raise ValueError("Require unique ordered undirected edges")
        if not edges:
            raise ValueError("Simulation requires at least one base edge")
        self.opinions = opinions.copy()
        self.edges = edges.copy()
        self.parameters = parameters
        self.weights = WeightedEdges(len(edges), parameters.initial_weight)
        self.incident: list[list[int]] = [[] for _ in opinions]
        for k, (i, j) in enumerate(edges):
            self.incident[i].append(k)
            self.incident[j].append(k)
        self.gaps = [abs(opinions[i] - opinions[j]) for i, j in edges]

    def update(self, edge_index: int) -> bool:
        i, j = self.edges[edge_index]
        x, y = self.opinions[i], self.opinions[j]
        p = self.parameters
        receptive = abs(x - y) < p.confidence
        old_weight = self.weights.weight(edge_index)
        if receptive:
            self.opinions[i] = x + p.mu * (y - x)
            self.opinions[j] = y + p.mu * (x - y)
            self.weights.replace(edge_index, old_weight + p.gamma * (1 - old_weight))
            for node in (i, j):
                for k in self.incident[node]:
                    a, b = self.edges[k]
                    self.gaps[k] = abs(self.opinions[a] - self.opinions[b])
        else:
            self.weights.replace(edge_index, p.delta * old_weight)
        return receptive

    def step(self, rng: random.Random) -> bool:
        return self.update(self.weights.select(rng.random()))


def components(n: int, edges: list[Edge]) -> tuple[tuple[int, ...], ...]:
    parents = list(range(n))

    def root(i: int) -> int:
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    for i, j in edges:
        a, b = root(i), root(j)
        parents[b] = a
    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(root(i), []).append(i)
    return tuple(sorted(tuple(group) for group in groups.values()))
