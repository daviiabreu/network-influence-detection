"""Scientific invariants for the anchored synthetic panel."""

import numpy as np

from ic_study.models.anchored_panel import normal_ranks


def test_matching_preserves_order_and_equalizes_marginals() -> None:
    left = normal_ranks(np.array([9.0, -1.0, 2.0, 4.0]))
    right = normal_ranks(np.array([0.0, 100.0, 30.0, -90.0]))
    np.testing.assert_array_equal(np.sort(left), np.sort(right))
    assert left[1] < left[2] < left[3] < left[0]
    assert abs(float(left.mean())) < 1e-12
    assert abs(float(left.var()) - 1) < 1e-12


def test_zero_influence_reduces_to_persistence_with_shared_streams() -> None:
    from ic_study.models.anchored_panel import latent_panel

    social = latent_panel(40, 11, 12, 13, 14, rho=0.85, strength=0.0)
    control = latent_panel(40, 11, 12, 99, 14, rho=0.85, strength=0.0)
    np.testing.assert_array_equal(social, control)
    for wave in social:
        np.testing.assert_array_equal(np.sort(wave), np.sort(social[0]))
    influenced = latent_panel(40, 11, 12, 13, 14, rho=0.85, strength=0.4)
    assert not np.array_equal(social, influenced)


def test_observation_is_separate_and_household_attrition_is_monotone() -> None:
    from ic_study.models.anchored_panel import observe, panel_mask

    latent = np.tile(normal_ranks(np.arange(120.0)), (11, 1))
    before = latent.copy()
    mask = panel_mask(120, 11, 42, retention=0.89)
    assert not mask[:5, 80:].any()
    assert mask[0, :80].all() and mask[5, 80:].all()
    np.testing.assert_array_equal(mask[:, ::2], mask[:, 1::2])
    assert np.all(np.diff(mask[:, :80].astype(int), axis=0) <= 0)
    observed = observe(latent, mask, 1.0, 15)
    assert observed.min() == -1 and observed.max() == 10
    assert np.unique(observed[0, :80]).size > 3
    noisy = observe(latent, mask, 0.5, 15)
    assert not np.array_equal(noisy, observed)
    np.testing.assert_array_equal(latent, before)
