"""Artificial denominators and failures cannot be removed by aggregation."""

import numpy as np
import pytest

from ic_study.simulation.v4_criteria import Thresholds, dispersion, refit_ratio


def test_pair_variance_is_on_logit_scale_and_failures_stay_in_denominator() -> None:
    rng = np.random.default_rng(53)
    logits = rng.normal(0, 0.02, (7, 100))
    estimates = 1 / (1 + np.exp(-logits))
    se = 0.02 * estimates * (1 - estimates)
    report = dispersion(
        estimates, se, np.ones((7, 100), dtype=bool), seed=7, bootstraps=100
    )
    assert 0.75 < report["pooled_ratio"] < 1.3
    failed = np.ones((7, 100), dtype=bool)
    failed[0, 0] = False
    report = dispersion(estimates, se, failed, seed=7, bootstraps=100)
    assert report["failures"] == 1
    assert report["denominator"] == 700
    assert report["complete"] is False


def test_refit_comparison_fails_when_d5_is_far_too_small_or_large() -> None:
    rng = np.random.default_rng(16)
    reference = rng.normal(size=100)
    draws = rng.normal(size=2000)
    assert refit_ratio(draws * 0.01, reference, seed=1)["pass"] is False
    assert refit_ratio(draws * 10, reference, seed=1)["pass"] is False


def test_zero_score_se_uses_frozen_floor_instead_of_discarding_pipeline() -> None:
    report = dispersion(
        np.full((7, 100), 0.5),
        np.zeros((7, 100)),
        np.ones((7, 100), dtype=bool),
        seed=7,
        bootstraps=20,
    )
    assert report["complete"]
    assert report["failures"] == 0
    assert report["denominator"] == 700
    assert report["pooled_ratio"] == 0


def test_pooled_bootstrap_resamples_heterogeneous_denominators_together() -> None:
    rng = np.random.default_rng(114)
    logits = rng.normal(0, 0.025, (7, 100))
    point = 1 / (1 + np.exp(-logits))
    se = 0.025 * np.exp(rng.normal(0, 1, (7, 100))) * point * (1 - point)
    result = dispersion(point, se, np.ones((7, 100), dtype=bool), seed=123)
    # Independent scalar enumeration: sum stratum variances / sum sampled SE².
    assert result["pooled_lower"] == pytest.approx(0.0739608769, abs=1e-7)
    assert result["pooled_upper"] == pytest.approx(0.1530459574, abs=1e-7)


def test_gaps_drop_intact_pairs_but_allowance_uses_all_attempts() -> None:
    from ic_study.simulation.v4_criteria import dispersion_pass

    rng = np.random.default_rng(87)
    logits = rng.normal(0, 0.02, (7, 100))
    point = 1 / (1 + np.exp(-logits))
    se = 0.02 * point * (1 - point)
    success = np.ones((7, 100), dtype=bool)
    success[0, :5] = False
    thresholds: Thresholds = dict(
        cell_lower=0.01, cell_upper=10.0, pooled_lower=0.01, pooled_upper=10.0
    )
    report = dispersion(point, se, success, seed=7, bootstraps=20)
    assert report["denominator"] == 700
    assert report["successful_pair_counts"][0] == 47
    assert report["cell_failure_counts"] == [5, 0, 0, 0, 0, 0, 0]
    assert dispersion_pass(report, thresholds)
    success[0, 5] = False
    assert not dispersion_pass(
        dispersion(point, se, success, seed=7, bootstraps=20), thresholds
    )
    success[:] = True
    success[:3, :5] = False
    assert not dispersion_pass(
        dispersion(point, se, success, seed=7, bootstraps=20), thresholds
    )


@pytest.mark.parametrize(("count", "allowance"), [(100, 3), (40, 2)])
def test_refit_allowance_preserves_original_denominator(
    count: int, allowance: int
) -> None:
    rng = np.random.default_rng(10)
    local = rng.normal(size=2000)
    refits = rng.normal(size=count)
    refits[:allowance] = np.nan
    report = refit_ratio(local, refits, seed=7)
    assert report["denominator"] == count
    assert report["failure_count"] == allowance
    assert report["pass"]
    refits[allowance] = np.nan
    assert not refit_ratio(local, refits, seed=7)["pass"]


def test_fd_check_is_one_median_per_cell_and_excludes_gaps() -> None:
    from ic_study.simulation.v4_criteria import fd_stability

    variances = np.ones((7, 100, 2))
    variances[:, :40, 1] = 10
    success = np.ones((7, 100), dtype=bool)
    variances[0, 50] = np.nan
    success[0, 50] = False
    result = fd_stability(variances, success)
    assert result["fd_stable"]
    assert result["fd_ratio_median_by_cell"] == [1] * 7
    variances[0, 40:60, 1] = 10
    assert not fd_stability(variances, success)["fd_stable"]


def test_failure_allowance_probability_includes_pooled_constraint() -> None:
    from ic_study.simulation.v4_criteria import failure_allowance_probability

    assert failure_allowance_probability([0] * 7) == 1
    assert failure_allowance_probability([1] * 7) == 0
    assert 0.98 < failure_allowance_probability([0.01] * 7) < 1
    assert failure_allowance_probability([0.05] * 7) < 0.01


def test_pooled_allowance_scales_with_allocated_cells() -> None:
    import math

    from ic_study.simulation.v4_criteria import failure_allowance_probability

    assert math.ceil(0.02 * 600) == 12
    rng = np.random.default_rng(31)
    point = rng.normal(0.5, 0.01, (6, 100))
    se = np.full((6, 100), 0.01)
    success = np.ones((6, 100), dtype=bool)
    success[:2, :5] = False
    success[2, :3] = False
    result = dispersion(point, se, success, seed=7, bootstraps=20)
    assert not result["failure_allowance_met"]
    assert failure_allowance_probability([0.01] * 6) == pytest.approx(0.989133900750301)
