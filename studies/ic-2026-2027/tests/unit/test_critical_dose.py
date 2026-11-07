"""Projection identities and finite-horizon dose estimation."""

import numpy as np

from ic_study.models.critical_dose import social_step


def test_linear_projection_and_disjoint_nonlinearity_are_exact_controls() -> None:
    state = np.array([0.1, 0.7, 0.9, 0.3, 0.2, 0.8])
    disjoint = np.array([[0, 1, 2], [3, 4, 5]])
    overlap = np.array([[0, 1, 2], [3, 4, 5], [0, 3, 4], [1, 2, 5]])
    for groups, coefficient in ((disjoint, -1.0), (overlap, 0.0)):
        np.testing.assert_allclose(
            social_step(state, groups, coefficient, projected=False),
            social_step(state, groups, coefficient, projected=True),
            atol=1e-14,
        )
    expected = np.array([0.17, 0.68, 0.85, 0.32, 0.235, 0.745])
    np.testing.assert_allclose(
        social_step(state, disjoint, 0, projected=False), expected
    )


def test_finite_horizon_distinguishes_lock_resolution_and_unresolved() -> None:
    from ic_study.models.critical_dose import classify_window, make_groups, run_dose

    assert classify_window(np.full((20, 6), 0.2)) == "locked"
    assert classify_window(np.full((20, 6), 0.9)) == "resolved"
    assert classify_window(np.full((20, 6), 0.6)) == "unresolved"
    groups = make_groups(60, 25)
    np.testing.assert_array_equal(np.bincount(groups.ravel()), np.full(60, 2))
    assert len({tuple(sorted(g)) for g in groups}) == 40
    state = np.full(60, 0.2)
    recipients = np.arange(60, dtype=np.int64)
    assert run_dose(state, groups, recipients, 0, -1, projected=True).status == "locked"
    assert (
        run_dose(state, groups, recipients, 1, -1, projected=True).status == "resolved"
    )
