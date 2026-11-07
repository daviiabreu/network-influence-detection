import math

import pytest

from ic_study.models.mechanism_controls import (
    expected_exposure,
    pair_step,
    trio_step,
)


def test_expected_exposure_uses_separate_calibration_states() -> None:
    edges = ((0, 1), (0, 2))
    calibration = (((0.0, 0.4), (0.0, 0.6), (1.0, 0.5)),)
    weights = expected_exposure(calibration, edges, homophily=2.0)
    expected = (1 / (1 + math.exp(-2)), math.exp(-2) / (1 + math.exp(-2)))
    assert weights == pytest.approx(expected)


def test_pair_step_zero_coupling_leaves_uninformed_topic_unchanged() -> None:
    states = ((0.1, 0.2), (0.9, 0.8))
    result = pair_step(
        states,
        (0, 1),
        pair_gain=0.2,
        coupling=0.0,
        source_recipients=(0,),
        source_value=1.0,
        source_gain=0.1,
    )
    assert result[0][1] == pytest.approx(0.2)
    assert result[1][1] == pytest.approx(0.8)
    no_source = pair_step(
        states,
        (0, 1),
        pair_gain=0.2,
        coupling=0.0,
        source_recipients=(),
        source_value=1.0,
        source_gain=0.1,
    )
    assert result[0][1] == no_source[0][1]


def test_linear_trio_equals_incidence_projection() -> None:
    states = (0.1, 0.4, 0.8)
    trio = trio_step(
        states,
        (0, 1, 2),
        gain=0.1,
        nonlinear=False,
        projected=False,
        source_recipients=(0,),
        source_gain=0.2,
    )
    pairs = trio_step(
        states,
        (0, 1, 2),
        gain=0.1,
        nonlinear=False,
        projected=True,
        source_recipients=(0,),
        source_gain=0.2,
    )
    assert trio == pytest.approx(pairs)


def test_nonlinear_and_projection_match_declared_reference_only() -> None:
    reference = (0.25, 0.5, 0.75)
    nonlinear = trio_step(
        reference,
        (0, 1, 2),
        gain=0.1,
        nonlinear=True,
        projected=False,
        source_recipients=(),
        source_gain=0.0,
    )
    projected = trio_step(
        reference,
        (0, 1, 2),
        gain=0.1,
        nonlinear=True,
        projected=True,
        source_recipients=(),
        source_gain=0.0,
    )
    assert nonlinear == pytest.approx(projected)
    off_reference = (0.0, 0.0, 1.0)
    nonlinear = trio_step(
        off_reference,
        (0, 1, 2),
        gain=0.1,
        nonlinear=True,
        projected=False,
        source_recipients=(),
        source_gain=0.0,
    )
    projected = trio_step(
        off_reference,
        (0, 1, 2),
        gain=0.1,
        nonlinear=True,
        projected=True,
        source_recipients=(),
        source_gain=0.0,
    )
    assert nonlinear != pytest.approx(projected)
