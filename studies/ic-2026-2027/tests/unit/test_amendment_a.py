"""Isolated successor experiments cannot mutate the frozen scientific paths."""

from pathlib import Path

import numpy as np
import pytest

from ic_study.models.anchored_panel import Floats
from ic_study.models.detection_panel import influence_panel
from ic_study.simulation.amendment_a import transport_null


def test_zero_trait_null_equals_zero_share_influence_pathwise() -> None:
    expected = influence_panel(600, 11, 321, 987, share=0, repulsion=0.25)
    actual = transport_null(600, 11, 321, 654, rho=0.85, trait=0)
    np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize("share", [0.0, 0.03, 0.1])
def test_fast_transport_preserves_full_size_frozen_panels(share: float) -> None:
    from ic_study.simulation.amendment_a import fast_influence

    expected = influence_panel(10626, 11, 321, 987, share=share, repulsion=0.25)
    actual = fast_influence(10626, 11, 321, 987, share=share)
    np.testing.assert_array_equal(actual, expected)


def test_matching_couples_zero_arms_but_evaluation_keeps_classes_independent() -> None:
    from ic_study.simulation.amendment_a import calibration_profiles, seed_a

    null = calibration_profiles(0, 0.7, 4, block=1, phase="match", rho=0.85, size=600)
    social = calibration_profiles(0, 0.7, 4, block=1, phase="match", size=600)
    np.testing.assert_array_equal(null, social)
    check = calibration_profiles(0, 0.7, 4, block=1, phase="check", size=600)
    other = calibration_profiles(0, 0.7, 4, block=1, phase="check", rho=0.85, size=600)
    assert not np.array_equal(check, other)
    assert seed_a(1, "reference", "state", 0) == seed_a(2, "reference", "state", 0)
    with pytest.raises(ValueError, match="calibration"):
        seed_a(0, "test", "state", 0)


def test_constrained_match_reports_unattainable_targets_without_dropping_them() -> None:
    from ic_study.simulation.amendment_a import constrained_match

    noise = np.arange(256)[:, None] * np.array([[1e-5, 2e-5]])

    def evaluate(rho: float, trait: float) -> Floats:
        return np.asarray(
            noise + np.array([rho + trait, rho + 2 * trait]), dtype=np.float64
        )

    good = constrained_match(noise + np.array([0.85, 0.85]), evaluate)
    assert good.success
    assert good.trait == 0
    bad = constrained_match(noise + np.array([0.85, 0.80]), evaluate)
    assert not bad.success
    assert bad.trait == 0
    assert bad.evaluations <= 32
    assert np.max(np.abs(bad.residual)) > 0.02


def test_cluster_auc_variance_counts_networks_and_ties() -> None:
    from ic_study.simulation.amendment_a import cluster_auc_se

    point, se = cluster_auc_se(
        np.array([[0.0, 0.0], [2.0, 2.0]]), np.array([[1.0, 1.0], [3.0, 3.0]])
    )
    assert point == 0.75
    assert se == pytest.approx(np.sqrt(0.125))
    assert cluster_auc_se(np.zeros((3, 2)), np.zeros((3, 2))) == (0.5, 0.0)


def test_projected_linear_refit_reoptimizes_free_parameter_at_trait_boundary() -> None:
    from ic_study.simulation.amendment_a import projected_linear_refit

    # Minimizing (drho - 0.1)^2 + (drho + dtrait + 0.1)^2 gives (0, 0).
    result = projected_linear_refit(
        np.array([0.5, 0.0]), np.array([[1.0, 0.0], [1.0, 1.0]]), np.array([-0.1, 0.1])
    )
    np.testing.assert_allclose(result, [0.5, 0.0], atol=1e-12)
    interior = projected_linear_refit(
        np.array([0.5, 0.2]), np.eye(2), np.array([-0.1, 0.1])
    )
    np.testing.assert_allclose(interior, [0.6, 0.1])


def test_successor_band_uses_nine_cell_correction_and_keeps_endpoints() -> None:
    from ic_study.simulation.amendment_a import bonferroni_band

    low, high = bonferroni_band(np.array([0.0, 0.5, 1.0]), np.zeros(3), networks=2000)
    assert low[0] == 0
    assert high[2] == 1
    assert low[1] < 0.5 < high[1]
    low, high = bonferroni_band(np.array([0.5]), np.array([0.1]), networks=2000)
    assert low[0] == pytest.approx(0.248031, abs=1e-5)
    assert high[0] == pytest.approx(0.751969, abs=1e-5)


def test_constrained_match_accepts_a_declared_interior_restart() -> None:
    from ic_study.simulation.amendment_a import constrained_match

    noise = np.arange(256)[:, None] * np.array([[1e-5, 2e-5]])
    fit = constrained_match(
        noise + np.array([0.8, 0.2]),
        lambda rho, trait: noise + np.array([rho, trait]),
        initial=(0.8, 0.1),
    )
    assert fit.success
    assert fit.rho == pytest.approx(0.8)
    assert fit.trait == pytest.approx(0.2)


def test_local_nuisance_draws_do_not_invent_uncertainty_for_exact_separation() -> None:
    from ic_study.simulation.amendment_a import LocalNuisance, local_nuisance_draws

    fixture = LocalNuisance(
        parameters=np.array([0.8, 0.2]),
        residuals=np.zeros((256, 2)),
        jacobian=np.eye(2),
        null_train=np.zeros((4, 3)),
        social_train=np.ones((4, 3)),
        null_reference=np.zeros((6, 3)),
        social_reference=np.ones((6, 3)),
        train_derivative=np.zeros((2, 4, 3)),
        reference_derivative=np.zeros((2, 6, 3)),
    )
    np.testing.assert_array_equal(local_nuisance_draws(fixture, draws=20), np.ones(20))


def test_local_nuisance_propagates_matching_variation_to_reference_law() -> None:
    from ic_study.simulation.amendment_a import LocalNuisance, local_nuisance_draws

    residuals = np.zeros((256, 2))
    residuals[:128, 0], residuals[128:, 0] = -0.1, 0.1
    derivative = np.zeros((2, 6, 3))
    derivative[0] = 1
    fixture = LocalNuisance(
        parameters=np.array([0.8, 0.2]),
        residuals=residuals,
        jacobian=np.eye(2),
        null_train=np.zeros((4, 3)),
        social_train=np.ones((4, 3)),
        null_reference=np.zeros((6, 3)),
        social_reference=np.zeros((6, 3)),
        train_derivative=np.zeros((2, 4, 3)),
        reference_derivative=derivative,
    )
    draws = local_nuisance_draws(fixture, draws=100)
    assert set(draws) <= {0.0, 0.5, 1.0}
    assert draws.std() > 0.4


def test_successor_profiles_preserve_frozen_observed_statistics(tmp_path: Path) -> None:
    from ic_study.simulation.amendment_a import calibration_profiles, seed_a
    from ic_study.simulation.detection_calibration import DetectionPilot, PilotSpec

    class MatchedSeeds(DetectionPilot):
        def seed(self, phase: str, role: str, i: int) -> int:
            return seed_a(1, phase, role, i)

    frozen = MatchedSeeds(PilotSpec(grid=(0.03,), size=10626), tmp_path / "frozen")
    expected = frozen.panel("train", 1, 0.03, observed_only=True)["observed"]
    actual = calibration_profiles(0.03, 0.7, 1, block=1, phase="train")[0]
    np.testing.assert_array_equal(actual, expected)


def test_fixed_jacobian_matching_refits_new_moments_without_new_derivative_panels() -> (
    None
):
    from ic_study.simulation.amendment_a import fixed_jacobian_match

    noise = np.arange(256)[:, None] * np.array([[1e-5, 2e-5]])
    target = noise + np.array([0.85, 0.9])
    fit = fixed_jacobian_match(
        target,
        lambda rho, trait: np.asarray(noise + np.array([rho, rho + trait])),
        np.array([[1.0, 0.0], [1.0, 1.0]]),
        initial=(0.8, 0.1),
    )
    assert fit.success
    assert fit.rho == pytest.approx(0.85)
    assert fit.trait == pytest.approx(0.05)
    assert fit.evaluations == 2
