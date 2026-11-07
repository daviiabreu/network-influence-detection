from __future__ import annotations

import math
from itertools import product

import pytest

from ic_study.metrics.histogram_scores import (
    frequencies,
    score_ensemble,
    wasserstein,
)
from ic_study.models.deffuant import Parameters, State
from ic_study.models.histogram_forecast import (
    BOUNDARIES,
    Dynamics,
    category,
    draw_histogram,
    exact_category,
    interact,
    seed_for,
)


def point(index: int) -> tuple[int, ...]:
    return tuple(int(k == index) for k in range(11))


def test_bins_tie_up_and_nextafter_down() -> None:
    assert category(0) == 0
    assert category(1) == 10
    for k, boundary in enumerate(BOUNDARIES):
        assert category(boundary) == k + 1
        assert category(math.nextafter(boundary, 0)) == k
    with pytest.raises(ValueError):
        category(float("nan"))


def test_ordered_transport_and_ensemble_center() -> None:
    left, right = point(0), point(10)
    assert wasserstein(frequencies(left), frequencies(right)) == pytest.approx(1)
    score = score_ensemble([left, right], tuple([1] + [0] * 9 + [1]))
    assert score["mean_w1"] == pytest.approx(0.5)
    assert score["central_w1"] == pytest.approx(0)
    assert score["energy"] == pytest.approx(0)


def test_fair_energy_expectation_and_strict_discrimination() -> None:
    left, right = point(0), point(10)
    expected_fair = (
        sum(
            score_ensemble([a, b], y)["energy"]
            for a, b, y in product([left, right], repeat=3)
        )
        / 8
    )
    expected_point = (
        sum(score_ensemble([left, left], y)["energy"] for y in (left, right)) / 2
    )
    assert expected_fair == pytest.approx(math.sqrt(2) / 4)
    assert expected_point == pytest.approx(math.sqrt(2) / 2)
    with pytest.raises(ValueError, match="at least two"):
        score_ensemble([left], right)


def test_complete_graph_core_matches_existing_dw_and_conserves_mean() -> None:
    ticks = 1 << 8
    opinions = [k * ticks for k in (1, 3, 6, 9)]
    edges = [(0, 1), (0, 2), (1, 2), (2, 3)]
    reference = State(
        [x / (10 * ticks) for x in opinions],
        edges,
        Parameters(confidence=0.35, gamma=0, delta=1),
    )
    for event in [0, 3, 1, 2, 0, 1, 2, 3]:
        interact(opinions, *edges[event], 7 * ticks, 2)
        reference.update(event)
        assert [x / (10 * ticks) for x in opinions] == pytest.approx(reference.opinions)
        assert sum(opinions) == 19 * ticks
    exact = [0, 25]
    interact(exact, 0, 1, 25, 1)
    assert exact == [0, 25]


@pytest.mark.parametrize(("left", "right", "expected"), [(3, 6, 5), (6, 7, 7)])
def test_dw_midpoint_enters_upper_bin_exactly(
    left: int, right: int, expected: int
) -> None:
    ticks = 1 << 150
    opinions = [left * ticks, right * ticks]
    interact(opinions, 0, 1, 7 * ticks, 2)
    assert exact_category(opinions[0], ticks) == expected
    assert exact_category(opinions[1], ticks) == expected
    assert exact_category(opinions[0] - 1, ticks) == expected - 1


def test_constant_point_and_drift_clipping() -> None:
    params = dict(population=50, sample_size=550, attempts=150, seed=7)
    assert draw_histogram(point(5), Dynamics(0), **params) == tuple(
        550 if k == 5 else 0 for k in range(11)
    )
    assert draw_histogram(point(10), Dynamics(0, drift=0.1), **params) == tuple(
        550 if k == 10 else 0 for k in range(11)
    )


def test_constant_observation_variance_includes_both_sampling_layers() -> None:
    samples = [
        draw_histogram(
            tuple([1] + [0] * 9 + [1]),
            Dynamics(0),
            population=10,
            sample_size=20,
            attempts=0,
            seed=seed_for("variance-check", r),
        )[0]
        / 20
        for r in range(3000)
    ]
    mean = sum(samples) / len(samples)
    variance = sum((x - mean) ** 2 for x in samples) / (len(samples) - 1)
    expected = 0.25 * (1 / 10 + (1 - 1 / 10) / 20)
    assert abs(mean - 0.5) < 0.02
    assert abs(variance - expected) < 0.004


def test_seed_parts_unambiguous_and_roles_distinct() -> None:
    assert seed_for("a", 12, 3) != seed_for("a", 1, 23)
    assert (
        len({seed_for(2, role) for role in ("initial", "events", "observation")}) == 3
    )
