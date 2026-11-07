"""Protocol statistics, censoring, and inference rather than threshold accuracy."""

import numpy as np
import pytest

from ic_study.analysis.detection_boundary import (
    auc,
    boundary,
    feature_channels,
    match_lag1,
    studentised_band,
)
from ic_study.analysis.redesign import lag_correlation
from ic_study.models.anchored_panel import Floats


def test_auc_uses_all_pairwise_orderings_and_half_ties() -> None:
    assert auc(np.array([0.0, 2.0]), np.array([1.0, 2.0])) == 0.625
    assert auc(np.ones(3), np.ones(5)) == 0.5
    assert auc(np.array([0.0, 1.0]), np.array([2.0, 3.0])) == 1


def test_boundary_is_first_grid_hit_with_right_censoring() -> None:
    grid = np.array([0.0, 0.01, 0.1, 0.9])
    assert boundary(grid, np.array([0.5, 0.6, 0.8, 0.9])) == 0.1
    assert boundary(grid, np.array([0.5, 0.6, 0.65, 0.69])) is None
    assert boundary(grid, np.array([0.7, 0.6, 0.8, 0.9])) == 0


def test_matching_uses_pooled_masked_protocol_statistic_and_strict_tolerance() -> None:
    panel = np.array([[0, 3, -1, 2], [1, 1, 0, -1], [3, 2, 1, 0]])
    channels = feature_channels(panel.astype(float), panel)
    assert channels["observed"][0] == pytest.approx(
        lag_correlation(panel, 1, missing=True)
    )
    offsets = np.linspace(-0.006, 0.006, 256)
    target = 0.61 + offsets
    result = match_lag1(target, lambda rho: rho + offsets, (0.2, 0.9))
    assert abs(result.values.mean() - target.mean()) <= result.tolerance
    assert result.tolerance <= 0.0003
    assert result.tolerance <= 0.1 * target.std(ddof=1)
    with pytest.raises(ValueError, match="256"):
        match_lag1(target[:255], lambda rho: rho + offsets[:255], (0.2, 0.9))


def test_logit_band_handles_zero_se_and_saturated_cells() -> None:
    estimate = np.array([[0.5, 1.0, 0.0]])
    se = np.zeros_like(estimate)
    reps = np.broadcast_to(estimate, (20, 1, 3)).copy()
    low, high = studentised_band(
        estimate, se, reps, np.zeros_like(reps), effective_n=100
    )
    assert np.all(np.isfinite(low)) and np.all(np.isfinite(high))
    assert np.all(high > low)
    assert low[0, 0] < 0.5 < high[0, 0]
    assert 0 <= low.min() < high.max() <= 1
    assert high[0, 1] == 1 and low[0, 2] == 0


def test_logit_band_is_per_reliability_not_across_reliabilities() -> None:
    estimate = np.array([[0.5, 0.6], [0.5, 0.6]])
    reps = np.tile(estimate, (40, 1, 1))
    reps[:, 1] += np.linspace(-0.2, 0.2, 40)[:, None]
    errors = np.full_like(reps, 0.03)
    low, high = studentised_band(
        estimate, np.full_like(estimate, 0.03), reps, errors, effective_n=100
    )
    single = studentised_band(
        estimate[:1], np.full((1, 2), 0.03), reps[:, :1], errors[:, :1], effective_n=100
    )
    np.testing.assert_allclose(low[:1], single[0])
    np.testing.assert_allclose(high[:1], single[1])


def test_matching_jointly_recovers_observed_lags_without_latent_input() -> None:
    from ic_study.analysis.detection_boundary import match_observed_lags

    offsets = np.linspace(-0.005, 0.005, 256)

    def observed(rho: float, trait: float) -> Floats:
        # Ordinal-like attenuation is deliberately different at each lag.
        return np.column_stack(
            (
                0.7 * (trait + (1 - trait) * rho) + offsets,
                0.65 * (trait + (1 - trait) * rho**2) + offsets,
            )
        )

    target = observed(0.8, 0.2)
    fit = match_observed_lags(target, observed)
    np.testing.assert_allclose(fit.values.mean(0), target.mean(0), atol=0.0003)
    assert np.max(np.abs(fit.values.mean(0) - target.mean(0)) / fit.tolerance) <= 1
    assert fit.rho == pytest.approx(0.8, abs=0.003)
    assert fit.trait == pytest.approx(0.2, abs=0.01)


def test_feature_channels_drops_observed_rank_but_keeps_latent_rank() -> None:
    from ic_study.models.detection_panel import null_panel, ordinal_channel

    z = null_panel(600, 11, 73, rho=0.7, trait=0.1)
    y = ordinal_channel(z, np.ones(z.shape, dtype=bool))
    channels = feature_channels(z, y)
    assert "rank" not in channels
    assert "latent_rank" in channels


def test_sustained_boundary_and_null_gate_do_not_select_an_isolated_peak() -> None:
    from ic_study.analysis.detection_boundary import boundary_report

    grid = np.array([0.0, 0.01, 0.1, 0.3])
    curve = np.array([0.5, 0.8, 0.6, 0.85])
    report = boundary_report(grid, curve, curve - 0.04, curve + 0.04)
    assert report["first"] == 0.01
    assert report["sustained"] == 0.3
    assert report["nonmonotone_band"] is True
    assert report["valid_null_gate"] is True
    invalid = boundary_report(grid, curve, np.array([0.51, 0.7, 0.5, 0.8]), curve + 0.1)
    assert invalid["valid_null_gate"] is False
    assert invalid["first"] is None and invalid["sustained"] is None


def test_cluster_bootstrap_adds_nuisance_variance_without_dividing_by_refits() -> None:
    from ic_study.analysis.detection_boundary import fixed_score_uncertainty

    # All events in every network tie: fixed-score variance is exactly zero.
    scores = np.zeros((20, 2, 2))
    nuisance = np.column_stack([np.tile([-0.1, 0.1], 20), np.tile([-0.2, 0.2], 20)])
    result = fixed_score_uncertainty(scores, scores, nuisance, seed=901, draws=100)
    np.testing.assert_allclose(result.point, [0.5, 0.5])
    np.testing.assert_allclose(result.se, nuisance.std(0, ddof=1))
    assert result.replicates.shape == (100, 2)
    assert result.conditional_se.max() == 0


def test_feasibility_mask_accounts_for_correlated_error() -> None:
    from ic_study.analysis.detection_boundary import feasible_lag1

    assert feasible_lag1(0.60, 0.50) is False
    assert feasible_lag1(0.50, 0.50) is True
    assert feasible_lag1(0.60, 0.50, error_correlation=0.5) is True
    # The sqrt(r_t*r_s) bound generalises the constant-reliability case.
    assert feasible_lag1(0.65, 0.5, next_reliability=0.8) is False
