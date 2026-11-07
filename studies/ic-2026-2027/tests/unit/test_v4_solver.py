"""Known moment maps exercise the profile estimator independently of simulation."""

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import profile_match
from ic_study.models.anchored_panel import Floats


@pytest.mark.parametrize(
    "phi,eta",
    [
        (0.6, 0.2),
        (0, 0.2),
        (0.999, 0.2),
        (0.6, 0),
        (0.6, 0.8),
        (0, 0),
        (0.999, 0),
        (0, 0.8),
        (0.999, 0.8),
    ],
)
def test_profile_roots_on_every_face_and_corner(phi: float, eta: float) -> None:
    noise = np.random.default_rng(3).normal(0, 0.01, (256, 2))

    def evaluate(p: float, e: float) -> Floats:
        return np.asarray(noise + np.array([p, p + e]))

    fit = profile_match(evaluate(phi, eta), evaluate)
    assert fit.success, fit.status
    np.testing.assert_allclose(fit.parameters, [phi, eta], atol=1e-5)
    assert fit.evaluations >= 3


def test_anchor_requires_bytewise_paired_identity_and_eligibility() -> None:
    target = np.zeros((256, 2))
    fit = profile_match(
        target, lambda p, e: np.full((256, 2), p - 0.85 + e), identity=True
    )
    assert fit.status == "anchor-exact"
    assert fit.evaluations == 1
    different = target.copy()
    different[:128] = 0.01
    different[128:] = -0.01
    fit = profile_match(
        target, lambda p, e: different + np.array([p - 0.85, e]), identity=True
    )
    assert fit.status != "anchor-exact"


def test_impossible_l1_nan_and_exact_budget_counts() -> None:
    target = np.zeros((256, 2))
    assert (
        profile_match(target, lambda p, e: target + np.array([p + 1, e])).status
        == "no-L1-root"
    )
    assert (
        profile_match(target, lambda p, e: target * np.nan).status == "numerical-limit"
    )
    calls = []

    def evaluate(p: float, e: float) -> Floats:
        calls.append((p, e))
        return np.asarray(target + np.array([p - 0.3, e - 0.3]))

    fit = profile_match(target, evaluate, budget=2)
    assert fit.status == "budget"
    assert fit.evaluations == len(calls) == 2


def test_nonmonotone_flat_profile_and_beyond_family_limit() -> None:
    target = np.zeros((256, 2))
    assert (
        profile_match(
            target, lambda p, e: target + np.array([p - 0.5, -e - 0.1])
        ).status
        == "non-monotone-profile"
    )
    assert (
        profile_match(target, lambda p, e: target + np.array([p - 0.5, 0.1])).status
        == "ill-conditioned"
    )
    assert (
        profile_match(target, lambda p, e: target + np.array([p - 0.5, e - 0.9])).status
        == "family-limit-upper"
    )


def test_lower_boundary_prioritizes_l1_instead_of_projected_zero_step() -> None:
    target = np.zeros((256, 2))
    result = profile_match(
        target, lambda p, e: target + np.array([p - 0.61 + e, p - 0.61 + 2 * e + 0.003])
    )
    assert result.status == "boundary"
    np.testing.assert_allclose(result.parameters, [0.61, 0], atol=1e-8)
    assert result.residual[1] > 0.0029


def test_independent_validation_is_not_equivalence_diagnostic() -> None:
    from ic_study.analysis.detection_boundary_v4 import validate_fit

    small = np.tile([-1e-7, 1e-7], 1024)[:, None] + np.array([[1e-6, 1e-6]])
    validation = validate_fit(small, 2, np.zeros(2))
    assert not validation.passed
    assert validation.equivalence_passed
    assert validate_fit(np.zeros((2048, 2)), 2, np.zeros(2)).passed
    large = np.tile([-0.02, 0.02], 1024)[:, None] + np.array([[0.0001, 0.0001]])
    validation = validate_fit(large, 2, np.zeros(2))
    assert validation.passed
    assert not validation.equivalence_passed


def test_e6_recentred_boundary_surrogate_does_not_stall() -> None:
    # B E6's published kappa values; a negative unconstrained eta is a KKT face.
    kappa = np.array([0.6943, 0.6834])
    target = np.zeros((1024, 2))
    desired = kappa * np.array([0.85, 0.85**2]) - np.array([0, 0.00005])

    def evaluate(phi: float, eta: float) -> Floats:
        return np.asarray(
            target + kappa * (eta + (1 - eta) * np.array([phi, phi**2])) - desired
        )

    result = profile_match(target, evaluate)
    assert result.status == "boundary"
    assert abs(result.residual[0]) <= result.tolerance[0]
    assert result.evaluations <= 64


def test_a_block7_residual_regression_takes_real_profile_steps() -> None:
    # The archived stall point and residual, paired with a declared local map.
    # This tests the numerical stall, not a replay of all 1024 archived panels.
    center = np.array([0.863082247455512, 0.0])
    residual = np.array([0.0003751736152286482, -0.00021796667182354986])
    jacobian = np.array([[0.7, 0.1], [1.0, 0.3]])
    target = np.zeros((1024, 2))
    fit = profile_match(
        target, lambda p, e: target + residual + jacobian @ (np.array([p, e]) - center)
    )
    assert fit.status == "interior"
    assert np.all(np.abs(fit.residual) <= fit.tolerance)
    assert fit.evaluations > 1


def test_degenerate_secant_uses_bisection_and_ends_without_fake_success() -> None:
    target = np.zeros((256, 2))
    fit = profile_match(
        target,
        lambda p, e: target + np.array([1.0 if p > 0.31 else -1.0, e - 0.1]),
        fixed_eta=0.0,
    )
    assert fit.status in {"numerical-limit", "budget"}
    assert not fit.success


def test_amplification_propagates_moment_error_to_mahalanobis_feature_distance() -> (
    None
):
    from ic_study.analysis.detection_boundary_v4 import amplification

    jacobian = np.array([[1.0, 0.0], [0.0, 1.0], [0.0, 2.0], [0.0, 3.0], [0.0, 6.0]])
    assert amplification(jacobian, np.array([0.0, 0.1]), np.eye(3), 2) == pytest.approx(
        0.7
    )


@pytest.mark.parametrize(
    "phi,eta", [(0.0, 0.2), (0.999, 0.2), (0, 0), (0.999, 0), (0, 0.8), (0.999, 0.8)]
)
def test_coupled_profile_faces_with_changing_l1_domain(phi: float, eta: float) -> None:
    noise = np.zeros((256, 2))

    def evaluate(p: float, e: float) -> Floats:
        return np.asarray(noise + np.array([p + e, p + 2 * e]))

    fit = profile_match(evaluate(phi, eta), evaluate)
    assert fit.success, fit.status
    np.testing.assert_allclose(fit.parameters, [phi, eta], atol=1e-5)


def test_acceptance_bounds_bias_at_quarter_of_fitting_se() -> None:
    target = np.zeros((1024, 2))
    noise = np.tile([-0.001, 0.001], 512)
    fit = profile_match(
        target,
        lambda p, e: np.column_stack((p - 0.4 + noise, e + noise)),
        fixed_eta=0.0,
    )
    assert fit.success
    assert fit.evaluations >= 3
    assert fit.tolerance[0] == pytest.approx(0.000007816317493509032)
    assert abs(fit.residual[0]) <= fit.tolerance[0]
