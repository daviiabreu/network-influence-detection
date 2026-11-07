"""Small deterministic mechanisms for exploratory contrasts only."""

from __future__ import annotations

import math
from collections.abc import Sequence

type TopicState = tuple[float, float]
type Edge = tuple[int, int]
type Trio = tuple[int, int, int]


def exposure_weights(
    states: Sequence[TopicState], edges: Sequence[Edge], homophily: float
) -> tuple[float, ...]:
    if not edges or homophily < 0:
        raise ValueError("Require edges and nonnegative homophily")
    weights = [
        math.exp(-homophily * abs(states[i][0] - states[j][0])) for i, j in edges
    ]
    total = sum(weights)
    return tuple(weight / total for weight in weights)


def expected_exposure(
    calibration_states: Sequence[Sequence[TopicState]],
    edges: Sequence[Edge],
    homophily: float,
) -> tuple[float, ...]:
    if not calibration_states:
        raise ValueError("Require independent calibration states")
    probabilities = [
        exposure_weights(states, edges, homophily) for states in calibration_states
    ]
    return tuple(
        sum(row[i] for row in probabilities) / len(probabilities)
        for i in range(len(edges))
    )


def pair_step(
    states: Sequence[TopicState],
    edge: Edge,
    *,
    pair_gain: float,
    coupling: float,
    source_recipients: Sequence[int],
    source_value: float,
    source_gain: float,
) -> tuple[TopicState, ...]:
    if not 0 <= pair_gain <= 0.5 or not 0 <= coupling <= 1:
        raise ValueError("Pair gain and coupling out of range")
    if not 0 <= source_gain <= 1 or not 0 <= source_value <= 1:
        raise ValueError("Source gain or value out of range")
    i, j = edge
    result = [list(state) for state in states]
    for topic in (0, 1):
        delta = (
            pair_gain
            * (coupling if topic == 1 else 1.0)
            * (states[j][topic] - states[i][topic])
        )
        result[i][topic] += delta
        result[j][topic] -= delta
    for recipient in source_recipients:
        delta = source_gain * (source_value - result[recipient][0])
        result[recipient][0] += delta
        result[recipient][1] += coupling * delta
    return tuple(
        (min(1.0, max(0.0, row[0])), min(1.0, max(0.0, row[1]))) for row in result
    )


def trio_step(
    states: Sequence[float],
    trio: Trio,
    *,
    gain: float,
    nonlinear: bool,
    projected: bool,
    source_recipients: Sequence[int],
    source_gain: float,
    truth: float = 1.0,
    reinforcement: float = 1.0,
    reference_gap: float = 0.25,
) -> tuple[float, ...]:
    if not 0 <= gain <= 1 / 3 or not 0 <= source_gain <= 1:
        raise ValueError("Gain out of range")
    if reinforcement < 0 or reference_gap <= 0:
        raise ValueError("Invalid reinforcement or reference gap")
    changes = [0.0] * len(states)
    if projected:
        scale = math.exp(-reinforcement * reference_gap) if nonlinear else 1.0
        for position, i in enumerate(trio):
            for j in trio[position + 1 :]:
                delta = gain * scale * (states[j] - states[i])
                changes[i] += delta
                changes[j] -= delta
    else:
        for i in trio:
            j, k = (node for node in trio if node != i)
            scale = (
                math.exp(-reinforcement * abs(states[j] - states[k]))
                if nonlinear
                else 1.0
            )
            changes[i] = gain * scale * (states[j] + states[k] - 2 * states[i])
    result = [min(1.0, max(0.0, value + changes[i])) for i, value in enumerate(states)]
    for recipient in source_recipients:
        result[recipient] += source_gain * (truth - result[recipient])
    return tuple(result)
