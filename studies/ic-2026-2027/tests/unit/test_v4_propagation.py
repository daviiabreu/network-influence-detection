"""Local inference preserves the profile estimator and network sampling unit."""

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import project_shift
from ic_study.models.anchored_panel import Floats


def test_projection_prioritizes_l1_and_preserves_observed_control_weight() -> None:
    point = np.array([0.5, 0.0])
    jacobian = np.array([[1.0, 1.0], [1.0, 2.0]])
    shift, projected = project_shift(point, jacobian, np.array([-0.1, 0.1]))
    np.testing.assert_allclose(shift, [0.1, 0])
    assert projected
    control, _ = project_shift(
        point, jacobian, np.array([-0.1, 0.1]), inherited_eta_shift=0.05
    )
    np.testing.assert_allclose(control, [0.05, 0.05])
    with pytest.raises(ValueError, match="ill-conditioned"):
        project_shift(point, np.zeros((2, 2)), np.ones(2))


def test_analytic_anchor_has_zero_shifts_variance_and_mcse() -> None:
    from ic_study.analysis.detection_boundary_v4 import anchor_nuisance

    result = anchor_nuisance(2000)
    assert result.variance == result.mean_shift == result.mcse == 0
    assert not np.any(result.shifts)
    assert not np.any(result.centered)


def test_variance_is_centered_not_mse_and_uses_independent_cluster_draws() -> None:
    from ic_study.analysis.detection_boundary_v4 import NuisanceInput, nuisance_draws

    rng = np.random.default_rng(11)
    data = NuisanceInput(
        np.array([0.5, 0.1]),
        np.zeros((32, 2)),
        np.eye(2),
        rng.normal(size=(40, 3)),
        rng.normal(0.2, size=(40, 3)),
        rng.normal(size=(60, 3)),
        rng.normal(0.2, size=(60, 3)),
        np.zeros((2, 3)),
    )
    result = nuisance_draws(data, seed=9, draws=100)
    assert result.variance == pytest.approx(result.aucs.var(ddof=1))
    assert result.variance > 0
    assert abs(result.centered.mean()) < 1e-14
    assert not np.any(result.shifts)


def test_successor_uncertainty_accepts_2000_local_draws_without_refit_api() -> None:
    from ic_study.analysis.detection_boundary_v4 import band, score_uncertainty

    null = np.zeros((5, 2, 9))
    social = null.copy()
    nuisance = np.zeros((2000, 9))
    nuisance[:, 3] = np.tile([-0.1, 0.1], 1000)
    result = score_uncertainty(null, social, nuisance, seed=5)
    assert result.se[3] == pytest.approx(np.std(nuisance[:, 3], ddof=1))
    assert result.se[0] == 0
    interval = band(result, networks=2000)
    assert interval.critical >= 2.7729
    assert np.all(interval.lower < 0.5)
    assert np.all(interval.upper > 0.5)


def test_per_realisation_stencils_and_control_uncertainty() -> None:
    from ic_study.analysis.detection_boundary_v4 import finite_differences

    base = np.arange(30, dtype=float).reshape(10, 3) / 30
    slopes = np.stack([base, base[::-1] * 2])

    def generate(point: Floats) -> Floats:
        return np.asarray(base + np.einsum("p,pnf->nf", point, slopes))

    point = np.array([0.4, 0.8])
    actual = finite_differences(generate, point, 0.01, generate(point))
    np.testing.assert_allclose(actual, slopes, atol=1e-12)
    predicted = generate(point) + np.einsum(
        "p,pnf->nf", np.array([0.002, -0.003]), actual
    )
    np.testing.assert_allclose(
        predicted, generate(point + np.array([0.002, -0.003])), rtol=0.05
    )


def test_retry_matching_size_does_not_change_training_cluster_resamples() -> None:
    from dataclasses import replace

    from ic_study.analysis.detection_boundary_v4 import NuisanceInput, nuisance_draws

    rng = np.random.default_rng(87)
    data = NuisanceInput(
        np.array([0.6, 0.2]),
        np.zeros((1024, 2)),
        np.eye(2),
        rng.normal(size=(12, 3)),
        rng.normal(size=(12, 3)),
        rng.normal(size=(20, 3)),
        rng.normal(size=(20, 3)),
        np.zeros((2, 3)),
    )
    original = nuisance_draws(data, seed=8, draws=10)
    retry = nuisance_draws(
        replace(data, differences=np.zeros((4096, 2))), seed=8, draws=10
    )
    np.testing.assert_array_equal(original.aucs, retry.aucs)


def test_curve_gaps_censor_crossing_boundaries_and_keep_null_gate() -> None:
    from ic_study.analysis.detection_boundary_v4 import Uncertainty, curve_report
    from ic_study.simulation.detection_v4 import GRID

    point = np.array([0.5, 0.6, 0.61, 0.65, 0.71, 0.8, 0.85, 0.9, 0.95])
    result = Uncertainty(
        point, np.full(9, 0.01), np.full(9, 0.01), np.tile(point, (2000, 1))
    )
    valid = curve_report(np.array(GRID), result, np.ones(9, dtype=bool))
    assert valid["valid_null_gate"]
    assert valid["first"] == 0.03
    mask = np.ones(9, dtype=bool)
    mask[2] = False
    available = Uncertainty(
        point[mask],
        np.full(8, 0.01),
        np.full(8, 0.01),
        np.tile(point[mask], (2000, 1)),
    )
    censored = curve_report(np.array(GRID), available, mask)
    assert censored["valid_null_gate"]
    assert censored["first"] is None
    assert censored["first_censoring"] == "gap at a=0.003"
    assert censored["sustained"] == 0.03
    assert censored["gap_count"] == 1


def test_first_boundary_and_interval_ends_are_censored_independently() -> None:
    from ic_study.analysis.detection_boundary_v4 import Uncertainty, curve_report
    from ic_study.simulation.detection_v4 import GRID

    point = np.array([0.5, 0.55, 0.69, 0.71, 0.8, 0.85, 0.9, 0.92])
    mask = np.ones(9, dtype=bool)
    mask[4] = False
    result = curve_report(
        np.array(GRID),
        Uncertainty(
            point, np.full(8, 0.01), np.full(8, 0.01), np.tile(point, (2000, 1))
        ),
        mask,
    )
    assert result["first"] == 0.01
    assert result["first_interval"] == (0.003, None)
    assert result["first_interval_censoring"] == "gap at a=0.03"


def test_real_feature_prediction_and_shift_counterexample() -> None:
    from ic_study.analysis.detection_boundary_v4 import finite_differences
    from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan

    source = PanelSource(Cell(0.03, 0.7), SeedPlan(9100))
    point = np.array([0.85, 0.15])
    delta = np.array([0.001, -0.001])
    baseline = source.profiles("reference", 8, parameters=point)[:, 2:5]
    derivative = finite_differences(
        lambda p: source.profiles("reference", 8, parameters=p)[:, 2:5],
        point,
        0.01,
        baseline,
    )
    regenerated = source.profiles("reference", 8, parameters=point + delta)[:, 2:5]
    predicted = baseline + np.einsum("p,pnf->nf", delta, derivative)
    relative_error = np.linalg.norm(predicted - regenerated, axis=1) / np.linalg.norm(
        regenerated, axis=1
    )
    assert np.max(relative_error) < 0.05
    relative_shift_error = np.linalg.norm(
        predicted - regenerated, axis=1
    ) / np.linalg.norm(regenerated - baseline, axis=1)
    assert np.max(relative_shift_error) > 0.05
    assert np.any(derivative.std(axis=1) > 0)


def test_mean_shift_propagation_rejects_per_realisation_drift() -> None:
    from ic_study.analysis.detection_boundary_v4 import NuisanceInput, nuisance_draws

    rng = np.random.default_rng(4103)
    data = NuisanceInput(
        np.array([0.6, 0.2]),
        rng.normal(0, 0.01, (64, 2)),
        np.array([[1.0, 0.0], [0.0, 1.0]]),
        rng.normal(size=(20, 3)),
        rng.normal(size=(20, 3)),
        rng.normal(size=(30, 3)),
        rng.normal(size=(30, 3)),
        np.array([[1.0, 2.0, 3.0], [3.0, 2.0, 1.0]]),
    )
    result = nuisance_draws(data, seed=4, draws=12)
    assert np.any(result.shifts)
    assert np.isfinite(result.aucs).all()
    from dataclasses import replace

    with pytest.raises(ValueError, match="mean"):
        nuisance_draws(
            replace(data, mean_derivative=np.zeros((2, 20, 3))), seed=4, draws=12
        )


def test_matching_mean_shift_matches_regenerated_vector() -> None:
    from ic_study.analysis.detection_boundary_v4 import mean_feature_jacobian
    from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan

    source = PanelSource(Cell(0.03, 0.7), SeedPlan(9100))
    point = np.array([0.85, 0.15])
    delta = np.array([0.001, -0.001])

    def generate(p: Floats) -> Floats:
        return source.profiles("match", 64, parameters=p)

    baseline = generate(point)
    derivative = mean_feature_jacobian(generate, point, 0.01, baseline)
    actual_shift = (generate(point + delta)[:, 2:5] - baseline[:, 2:5]).mean(0)
    predicted_shift = delta @ derivative[:, 2:5]
    assert (
        np.linalg.norm(predicted_shift - actual_shift) / np.linalg.norm(actual_shift)
        < 0.05
    )
