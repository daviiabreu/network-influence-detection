from __future__ import annotations

import math
import random
from fractions import Fraction

import pytest

from ic_study.models.deffuant import Parameters, State, WeightedEdges, components
from ic_study.simulation.fragmentation import (
    CachedStop,
    diameter_accepts,
    effective_partition,
    separation_accepts,
    simulate,
)


def bridge_state() -> State:
    return State(
        [0.0, 0.009, 0.096, 0.105],
        [(0, 1), (0, 3), (2, 3)],
        Parameters(confidence=0.1),
    )


def test_constructed_bridge_reactivates_under_exact_and_float_updates() -> None:
    state = bridge_state()
    partition = effective_partition(state)
    assert partition == ((0, 1), (2, 3))
    assert diameter_accepts(state, partition, 0.01)
    assert not separation_accepts(state, partition)
    exact = list(map(Fraction, ["0", ".009", ".096", ".105"]))
    for edge_index in (0, 2):
        i, j = state.edges[edge_index]
        exact[i] = exact[j] = (exact[i] + exact[j]) / 2
        assert state.update(edge_index)
        assert state.opinions == pytest.approx(list(map(float, exact)), abs=1e-16)
    assert abs(exact[0] - exact[3]) == Fraction(".096") < Fraction(".1")
    assert effective_partition(state) == ((0, 1, 2, 3),)
    assert not diameter_accepts(state, effective_partition(state), 0.01)
    assert state.update(1)
    assert sum(state.opinions) == pytest.approx(0.21)


def test_strict_confidence_and_weight_rules() -> None:
    state = State([0, 0.25], [(0, 1)], Parameters(confidence=0.25))
    assert not state.update(0)
    assert state.opinions == [0, 0.25]
    assert state.weights.weight(0) == 0.25
    state = State([0.125, 0.25], [(0, 1)], Parameters(confidence=0.25))
    assert state.update(0)
    assert state.opinions == [0.1875, 0.1875]
    assert state.weights.weight(0) == 0.75


def test_tree_matches_cumulative_distribution_after_weight_replacements() -> None:
    sampler = WeightedEdges(5, 0.5)
    weights = [0.125, 0.25, 0.5, 0.75, 1.0]
    for i, value in enumerate(weights):
        sampler.replace(i, value)
    for k in range(1000):
        u = (k + 0.5) / 1000
        target = u * sum(weights)
        total = 0.0
        expected = -1
        for index, weight in enumerate(weights):
            total += weight
            if target < total:
                expected = index
                break
        assert sampler.select(u) == expected
    with pytest.raises(ArithmeticError, match="underflow"):
        sampler.replace(0, 0)


def test_separated_intervals_remain_separated_and_mean_is_conserved() -> None:
    state = State(
        [0.1, 0.109, 0.8, 0.809],
        [(0, 1), (0, 3), (2, 3)],
        Parameters(confidence=0.1, mu=0.3),
    )
    partition = effective_partition(state)
    initial_mean = sum(state.opinions) / 4
    rng = random.Random(3921)
    for _ in range(5000):
        state.step(rng)
        assert effective_partition(state) == partition
        assert separation_accepts(state, partition)
    assert sum(state.opinions) / 4 == pytest.approx(initial_mean, abs=1e-13)


def test_tree_residual_rounding_cannot_reach_padding() -> None:
    sampler = WeightedEdges(6, 0.5)
    for i, exponent in enumerate([54, 51, 43, 53, 21, 1]):
        sampler.replace(i, 2.0**-exponent)
    assert sampler.select(math.nextafter(1.0, 0.0)) == 5


def test_certificate_ignores_pairs_without_base_edges_and_handles_boundary() -> None:
    state = State([0, 0, 0.01], [(0, 1)], Parameters(confidence=0.1))
    assert components(3, state.edges) == ((0, 1), (2,))
    assert separation_accepts(state, effective_partition(state))
    state = State([0, 0.25], [(0, 1)], Parameters(confidence=0.25))
    assert separation_accepts(state, effective_partition(state), margin=0)
    assert not separation_accepts(state, effective_partition(state), margin=1e-12)


def test_seeded_trajectory_detects_crossing_after_reference_stop() -> None:
    result = simulate(bridge_state(), event_seed=1, max_attempts=2000)
    repeated = simulate(bridge_state(), event_seed=1, max_attempts=2000)
    assert result == repeated
    assert result.cached_stop is not None and result.cached_stop.attempt > 0
    assert result.diameter_stop is not None
    assert result.first_cross_cached is not None
    assert result.first_cross_diameter is not None
    assert result.certified_stop is not None
    assert result.cached_stop.partition == ((0, 1), (2, 3))
    assert result.certified_stop.partition == ((0, 1, 2, 3),)
    assert result.status == "certified"


def test_budget_exhaustion_is_not_certification() -> None:
    state = State([0, 0.8], [(0, 1)], Parameters(confidence=1, mu=0.1))
    result = simulate(state, event_seed=31, max_attempts=1)
    assert result.status == "right_censored"
    assert result.certified_stop is None
    assert result.cached_stop is None


def test_reference_check_keeps_cached_partition_after_it_is_established() -> None:
    state = State(
        [0, 0.009, 0.018, 0.12],
        [(0, 1), (1, 2), (2, 3)],
        Parameters(confidence=0.1),
    )
    monitor = CachedStop(0.01)
    assert monitor.check(state) is None
    assert monitor.partition == ((0, 1, 2), (3,))
    state.opinions = [0.01, 0.01, 0.01, 0.105]
    state.gaps = [abs(state.opinions[i] - state.opinions[j]) for i, j in state.edges]
    assert effective_partition(state) == ((0, 1, 2, 3),)
    assert monitor.check(state) == ((0, 1, 2), (3,))


def test_uniform_baseline_preserves_weights_and_complete_graph_consensus() -> None:
    rng = random.Random(444)
    opinions = [rng.random() for _ in range(20)]
    edges = [(i, j) for i in range(20) for j in range(i + 1, 20)]
    state = State(opinions, edges, Parameters(confidence=1, gamma=0, delta=1))
    result = simulate(state, event_seed=11, max_attempts=10000)
    assert result.status == "certified"
    assert len(result.endpoint_partition) == 1
    assert all(w == 0.5 for w in result.final_weights)
    assert result.mean_drift == pytest.approx(0, abs=1e-13)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -0.1, 0, 1.1])
def test_invalid_confidence_is_rejected(bad: float) -> None:
    with pytest.raises(ValueError):
        Parameters(confidence=bad)
