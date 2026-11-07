"""Scientific invariants for the decision-14 successor."""

import hashlib

import numpy as np
import pytest

from ic_study.models.detection_panel import (
    bounded_drift,
    influence_panel,
    measurement,
    null_panel,
    ordinal_channel,
)
from ic_study.simulation.detection_calibration import calibration_seed


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (600, "4df3049105b63e6d546e64af471d8b381fdb43fc76877ec57fb853623ba2aca5"),
        (10626, "0bd67064acd8f37153373d67f69952f7f6ebd9f6cbeac05048761112e3900602"),
    ],
)
def test_zero_share_panel_keeps_frozen_calibration_bytes(
    size: int, expected: str
) -> None:
    panel = influence_panel(
        size,
        11,
        calibration_seed("match", "state", 1),
        calibration_seed("match", "network", 1),
        share=0.0,
        repulsion=0.25,
    )
    assert hashlib.sha256(panel.tobytes()).hexdigest() == expected


def test_boundary_is_assimilative_and_distant_repulsion_has_opposite_sign() -> None:
    # Node 0 sees gaps +1,+2: (1 - .5*2)/2 = 0.
    # Node 1 sees gaps -1,+1: zero; node 2 sees -2,-1: (.5*2-1)/2=0.
    values = np.array([0.0, 1.0, 2.0])
    partners = np.array([[1, 2], [0, 2], [0, 1]])
    np.testing.assert_allclose(bounded_drift(values, partners, 0.5), [0, 0, 0])
    np.testing.assert_allclose(bounded_drift(values, partners, 0.0), [0.5, 0, -0.5])
    # At b=1, the distant positive gap repels toward negative values.
    np.testing.assert_allclose(bounded_drift(values, partners, 1.0), [-0.5, 0, 0.5])


def test_continuous_reliability_and_equiprobable_categories() -> None:
    z = np.random.default_rng(81).normal(size=(2, 100_000))
    for r in (0.5, 0.7, 0.9, 1.0):
        w = measurement(z, r, 82)
        assert np.corrcoef(w.ravel(), z.ravel())[0, 1] ** 2 == pytest.approx(
            r, abs=0.006
        )
        y = ordinal_channel(w, np.ones(z.shape, dtype=bool))
        np.testing.assert_allclose(
            np.bincount(y.ravel(), minlength=11) / y.size,
            np.full(11, 1 / 11),
            atol=2e-5,
        )


@pytest.mark.parametrize("trait", [0.0, 0.3])
def test_null_has_stationary_unit_variance_and_trait_plus_ar_covariance(
    trait: float,
) -> None:
    z = null_panel(100_000, 6, 91, rho=0.6, trait=trait)
    np.testing.assert_allclose(z.mean(axis=1), 0, atol=0.012)
    np.testing.assert_allclose(z.var(axis=1), 1, atol=0.018)
    for lag in (1, 2, 4):
        covariance = np.mean(z[:-lag] * z[lag:])
        assert covariance == pytest.approx(trait + (1 - trait) * 0.6**lag, abs=0.012)


def test_heteroscedastic_reliability_and_midpoint_error() -> None:
    z = np.random.default_rng(12).normal(size=(2, 100_000))
    w = measurement(z, 0.7, 13, heteroscedastic=True)
    error = w - np.sqrt(0.7) * z
    assert error[np.abs(z) < 0.3].var() > 1.8 * error[np.abs(z) > 2].var()
    assert np.corrcoef(w.ravel(), z.ravel())[0, 1] ** 2 == pytest.approx(0.7, abs=0.006)


def test_hand_computed_pretransport_update_at_confidence_boundary() -> None:
    from ic_study.models.detection_panel import influence_update

    z = np.array([0.0, 1.0, 2.0])
    partners = np.array([[1, 2], [0, 2], [0, 1]])
    # b=1 gives drift [-.5,0,.5], SD=sqrt(1/6). Innovation share=.5.
    result = influence_update(z, partners, np.zeros(3), rho=0, share=0.5, repulsion=1)
    np.testing.assert_allclose(result, [-np.sqrt(3) / 2, 0, np.sqrt(3) / 2])


def test_rank_invariance_and_heaped_margins() -> None:
    from ic_study.analysis.detection_boundary import feature_channels

    z = null_panel(600, 11, 51, rho=0.7, trait=0)
    mask = np.ones(z.shape, dtype=bool)
    w = measurement(z, 0.7, 52, heteroscedastic=True)
    y = ordinal_channel(w, mask, midpoint_mass=0.1, heap_seed=53)
    expected = np.full(11, 0.9 / 11)
    expected[5] += 0.1
    np.testing.assert_allclose(np.bincount(y.ravel()) / y.size, expected, atol=0.002)
    original = feature_channels(z, y)
    changed = feature_channels(np.exp(z), y)
    np.testing.assert_allclose(original["latent_rank"], changed["latent_rank"])


def test_update_includes_persistence_and_nonzero_noise() -> None:
    from ic_study.models.detection_panel import influence_update

    z = np.array([0.0, 1.0, 2.0])
    partners = np.array([[1, 2], [0, 2], [0, 1]])
    # b=1 => normalized drift [-sqrt(1.5),0,sqrt(1.5)].
    # rho=.6, share=.5, noise=[1,-1,2]; sqrt(1-rho^2)=.8.
    result = influence_update(
        z, partners, np.array([1.0, -1.0, 2.0]), rho=0.6, share=0.5, repulsion=1.0
    )
    np.testing.assert_allclose(
        result,
        [
            0.8 * (1 - np.sqrt(1.5)) / np.sqrt(2),
            0.6 - 0.8 / np.sqrt(2),
            1.2 + 0.8 * (np.sqrt(1.5) + 2) / np.sqrt(2),
        ],
    )


def test_state_persistence_has_stable_tails_without_a_network() -> None:
    from ic_study.models.detection_panel import state_dependent_panel, state_persistence

    np.testing.assert_allclose(
        state_persistence(np.array([0.0, 1.0, -1.0]), 0.6, 1.0),
        [0.6, 1 - 0.4 * np.exp(-0.5), 1 - 0.4 * np.exp(-0.5)],
    )
    z = state_dependent_panel(6000, 11, 234, center=0.6, width=1.0)
    assert z.shape == (11, 6000)
    np.testing.assert_allclose(z.var(1), 1, atol=1e-12)
    change = np.abs(np.diff(z, axis=0))
    assert change[np.abs(z[:-1]) > 2].mean() < change[np.abs(z[:-1]) < 0.3].mean()


def test_correlated_response_error_and_tenure_reliability() -> None:
    from ic_study.models.detection_panel import tenure_reliability

    z = np.random.default_rng(42).normal(size=(11, 20000))
    w = measurement(z, 0.7, 54, error_correlation=0.5)
    residual = (w - np.sqrt(0.7) * z) / np.sqrt(0.3)
    assert np.corrcoef(residual[0], residual[7])[0, 1] == pytest.approx(0.5, abs=0.02)
    mask = np.array([[True, False], [True, True], [True, True]])
    np.testing.assert_allclose(
        tenure_reliability(mask, 0.7, 0.1), [[0.7, 0.7], [0.71, 0.7], [0.72, 0.71]]
    )


def test_mover_stayer_has_exact_stayers_and_mixture_covariance() -> None:
    from ic_study.models.detection_panel import mover_stayer_panel

    z = mover_stayer_panel(40000, 6, 765, rho=0.5, stayers=0.3)
    assert np.mean(np.all(np.diff(z, axis=0) == 0, axis=0)) == pytest.approx(
        0.3, abs=0.01
    )
    assert np.mean(z[0] * z[3]) == pytest.approx(0.3 + 0.7 * 0.5**3, abs=0.02)


def test_state_dependent_family_contains_active_updating_at_zero_heterogeneity() -> (
    None
):
    from ic_study.models.detection_panel import influence_panel, state_dependent_panel

    ar = influence_panel(600, 11, 72, 93, share=0, rho=0.8)
    nested = state_dependent_panel(600, 11, 72, center=0.8, heterogeneity=0)
    np.testing.assert_allclose(nested, ar, atol=1e-12)
