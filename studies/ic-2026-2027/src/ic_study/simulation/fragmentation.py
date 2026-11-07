"""Observe three stopping rules on a single uninterrupted DW trajectory."""

from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass

from ic_study.models.deffuant import State, components

type Partition = tuple[tuple[int, ...], ...]


def effective_partition(state: State) -> Partition:
    return components(
        len(state.opinions),
        [
            edge
            for edge, gap in zip(state.edges, state.gaps, strict=True)
            if gap < state.parameters.confidence
        ],
    )


def intervals(state: State, partition: Partition) -> list[tuple[float, float]]:
    return [
        (min(state.opinions[i] for i in group), max(state.opinions[i] for i in group))
        for group in partition
    ]


def diameter_accepts(state: State, partition: Partition, tolerance: float) -> bool:
    return all(high - low < tolerance for low, high in intervals(state, partition))


def separation_accepts(
    state: State, partition: Partition, margin: float = 1e-12
) -> bool:
    bounds = intervals(state, partition)
    membership = [0] * len(state.opinions)
    for k, group in enumerate(partition):
        for i in group:
            membership[i] = k
    for i, j in state.edges:
        a, b = membership[i], membership[j]
        if a == b:
            continue
        low_a, high_a = bounds[a]
        low_b, high_b = bounds[b]
        gap = max(0.0, low_a - high_b, low_b - high_a)
        if gap < state.parameters.confidence + margin:
            return False
    return True


class CachedStop:
    """Independent implementation of the reference code's latched checks."""

    def __init__(self, tolerance: float) -> None:
        self.tolerance = tolerance
        self.first_passed = False
        self.partition: Partition | None = None

    def check(self, state: State) -> Partition | None:
        c = state.parameters.confidence
        if not self.first_passed:
            self.first_passed = not any(self.tolerance <= gap < c for gap in state.gaps)
        if self.first_passed and self.partition is None:
            candidate = effective_partition(state)
            if diameter_accepts(state, candidate, c):
                self.partition = candidate
        if self.partition is not None and diameter_accepts(
            state, self.partition, self.tolerance
        ):
            return self.partition
        return None


@dataclass(frozen=True)
class Snapshot:
    attempt: int
    partition: Partition
    opinions: tuple[float, ...]
    interval_separated: bool


@dataclass(frozen=True)
class Result:
    status: str
    attempts: int
    receptive_events: int
    opinion_changing_events: int
    cached_stop: Snapshot | None
    diameter_stop: Snapshot | None
    certified_stop: Snapshot | None
    first_cross_cached: int | None
    first_cross_diameter: int | None
    endpoint_partition: Partition
    final_opinions: tuple[float, ...]
    final_weights: tuple[float, ...]
    mean_drift: float
    numerical_error: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def simulate(
    state: State,
    *,
    event_seed: int,
    max_attempts: int,
    tolerance: float = 0.01,
    margin: float = 1e-12,
    fixed_check_interval: int | None = None,
    minimum_attempt: int = 0,
) -> Result:
    if not 0 < tolerance < state.parameters.confidence:
        raise ValueError("Require 0 < tolerance < confidence")
    if max_attempts < 1 or minimum_attempt < 0:
        raise ValueError("Invalid attempt budget")
    if not math.isfinite(margin) or margin < 0:
        raise ValueError("Invalid certificate margin")
    if fixed_check_interval is not None and fixed_check_interval < 1:
        raise ValueError("Check interval must be positive")
    initial_mean = math.fsum(state.opinions) / len(state.opinions)
    rng = random.Random(event_seed)
    cached = CachedStop(tolerance)
    cached_stop = diameter_stop = certified_stop = None
    receptive_events = opinion_changing_events = since_check = 0
    changed_since_check = False
    interval: float = fixed_check_interval or 0
    numerical_error = None
    first_cross_cached = first_cross_diameter = None
    cached_membership: list[int] | None = None
    diameter_membership: list[int] | None = None

    def membership(partition: Partition) -> list[int]:
        labels = [0] * len(state.opinions)
        for k, group in enumerate(partition):
            for node in group:
                labels[node] = k
        return labels

    def snapshot(attempt: int, partition: Partition) -> Snapshot:
        return Snapshot(
            attempt,
            partition,
            tuple(state.opinions),
            separation_accepts(state, partition, margin),
        )

    for attempt in range(1, max_attempts + 1):
        try:
            selected = state.weights.select(rng.random())
            i, j = state.edges[selected]
            previous = (state.opinions[i], state.opinions[j])
            receptive = state.update(selected)
        except ArithmeticError as exc:
            numerical_error = str(exc)
            break
        receptive_events += receptive
        opinion_changing_events += previous != (state.opinions[i], state.opinions[j])
        if receptive:
            if (
                cached_membership is not None
                and first_cross_cached is None
                and cached_membership[i] != cached_membership[j]
            ):
                first_cross_cached = attempt
            if (
                diameter_membership is not None
                and first_cross_diameter is None
                and diameter_membership[i] != diameter_membership[j]
            ):
                first_cross_diameter = attempt
        changed_since_check |= receptive
        since_check += 1
        if not (
            changed_since_check
            and since_check >= interval
            and attempt > minimum_attempt
        ):
            continue
        if fixed_check_interval is None:
            interval = 10 ** (math.floor(math.log10(attempt)) - 3)
        since_check = 0
        changed_since_check = False
        if cached_stop is None:
            cached_partition = cached.check(state)
            if cached_partition is not None:
                cached_stop = snapshot(attempt, cached_partition)
                cached_membership = membership(cached_partition)
        if any(tolerance <= gap < state.parameters.confidence for gap in state.gaps):
            continue
        partition = effective_partition(state)
        if not diameter_accepts(state, partition, tolerance):
            continue
        if diameter_stop is None:
            diameter_stop = snapshot(attempt, partition)
            diameter_membership = membership(partition)
        if separation_accepts(state, partition, margin):
            certified_stop = snapshot(attempt, partition)
            break

    drift = math.fsum(state.opinions) / len(state.opinions) - initial_mean
    if abs(drift) > 1e-10:
        numerical_error = "Mean conservation exceeded 1e-10"
    if numerical_error:
        status = "numerical_failure"
    elif certified_stop is not None:
        status = "certified"
    else:
        status = "right_censored"
    return Result(
        status,
        attempt,
        receptive_events,
        opinion_changing_events,
        cached_stop,
        diameter_stop,
        certified_stop,
        first_cross_cached,
        first_cross_diameter,
        effective_partition(state),
        tuple(state.opinions),
        tuple(state.weights.weight(k) for k in range(len(state.edges))),
        drift,
        numerical_error,
    )
