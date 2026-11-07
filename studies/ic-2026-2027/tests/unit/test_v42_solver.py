"""Operational solver changes retain scientific acceptance and validation."""

from dataclasses import replace

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import (
    NuisanceInput,
    nuisance_draws,
    profile_match,
    validate_fit,
)
from ic_study.models.anchored_panel import Floats
from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan, pipeline


@pytest.mark.parametrize("eta", [0.001, 0.05, 0.3, 0.6, 0.79])
def test_warm_profile_and_inexact_steps_finish_at_original_tolerance(
    eta: float,
) -> None:
    rng = np.random.default_rng(4201)
    noise = rng.normal(0, 0.001, (1024, 2))

    def evaluate(phi: float, weight: float) -> Floats:
        return np.asarray(
            noise + np.array([phi + 0.1 * weight, phi**2 + weight + weight**2])
        )

    result = profile_match(evaluate(0.63, eta), evaluate)
    assert result.success, result.status
    np.testing.assert_allclose(result.parameters, [0.63, eta], atol=2e-6)
    assert np.all(np.abs(result.residual) <= result.tolerance)
    np.testing.assert_array_equal(
        result.tolerance, np.minimum(5e-5, np.maximum(1e-6, 0.25 * result.se))
    )
    assert result.evaluations < 40
    independent = rng.normal(0, 0.001, (2048, 2)) + result.residual
    assert validate_fit(independent, 2, result.se).passed


@pytest.mark.parametrize("phi", [0.0, 0.999])
def test_endpoint_prediction_without_solver_step_is_boundary(phi: float) -> None:
    target = np.zeros((1024, 2))
    result = profile_match(
        target,
        lambda p, e: target + np.array([p - phi, 0]),
        fixed_eta=0,
    )
    assert result.success
    assert result.status == "boundary"


def test_budget_96_counts_actual_calls_and_rejects_larger_budget() -> None:
    target = np.zeros((16, 2))
    calls = []

    def evaluate(phi: float, eta: float) -> Floats:
        calls.append((phi, eta))
        return np.asarray(target + np.array([phi - 0.4, eta - 0.3]))

    fit = profile_match(target, evaluate, budget=96)
    assert fit.success
    assert fit.evaluations == len(calls)
    with pytest.raises(ValueError, match="budget"):
        profile_match(target, evaluate, budget=97)


def test_boundary_draws_keep_uncentred_matching_residual() -> None:
    rng = np.random.default_rng(42)
    data = NuisanceInput(
        np.array([0.6, 0.0]),
        np.column_stack((np.zeros(1024), np.full(1024, 0.01))),
        np.array([[1.0, 0.2], [1.0, 1.0]]),
        rng.normal(size=(20, 3)),
        rng.normal(size=(20, 3)),
        rng.normal(size=(30, 3)),
        rng.normal(size=(30, 3)),
        rng.normal(size=(2, 3)),
    )
    result = nuisance_draws(data, seed=4202, draws=100)
    assert not np.any(result.shifts[:, 1])
    assert result.projected_fraction == 1
    assert abs(result.centered.mean()) < 1e-14
    interior = nuisance_draws(
        replace(data, differences=-data.differences), seed=4202, draws=100
    )
    assert np.all(interior.shifts[:, 1] > 0)


def test_control_missing_or_failed_dependency_does_no_simulation() -> None:
    control = PanelSource(Cell(0.03, 0.7, channel="latent"), SeedPlan(4203))
    missing = pipeline(control)
    failed = pipeline(control, observed=missing)
    assert missing.dependency_gap and failed.dependency_gap
    assert not missing.fit.success and not failed.fit.success
    assert missing.fit.final.fit.status == "dependency-gap"
    assert control.panels == 0


def test_cached_nonidentity_anchor_requires_a_real_step() -> None:
    target = np.zeros((256, 2))
    points = []

    def evaluate(phi: float, eta: float) -> Floats:
        points.append((phi, eta))
        return np.asarray(target + np.array([phi - 0.85, eta]))

    fit = profile_match(target, evaluate, fixed_eta=0)
    assert fit.success and fit.status == "interior"
    assert fit.evaluations > 2
    assert len(points) == fit.evaluations
    assert any(p not in {0.85, 0.86} for p, _ in points)
    assert np.all(np.abs(fit.residual) <= fit.tolerance)


def test_inner_updates_slope_when_trait_weight_attenuates_phi_derivative() -> None:
    target = np.zeros((1024, 2))

    def evaluate(phi: float, eta: float) -> Floats:
        return np.asarray(
            target + np.array([(1 - eta) * phi, (1 - eta) * phi**2 + eta])
        )

    fit = profile_match(evaluate(0.63, 0.75), evaluate)
    assert fit.success, fit.status
    assert fit.evaluations < 35
    np.testing.assert_allclose(fit.parameters, [0.63, 0.75], atol=1e-5)
    assert np.all(np.abs(fit.residual) <= fit.tolerance)


def test_weak_profile_derivative_is_checked_after_refining_l1() -> None:
    noise = np.tile([-0.002, 0.002], 128)[:, None] * np.ones((1, 2))

    def moments(phi: float, eta: float) -> Floats:
        lag1 = phi**2 + 0.1 * eta
        return np.array([lag1, 1.8 * lag1 + 0.001 * eta**2 + 0.0001 * eta])

    target = np.tile(moments(0.8, 0.4), (256, 1))
    fit = profile_match(target, lambda p, e: noise + moments(p, e))
    assert fit.success, fit.status
    assert fit.evaluations <= 96
    assert np.all(np.abs(fit.residual) <= fit.tolerance)
