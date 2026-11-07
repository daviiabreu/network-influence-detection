"""Observable estimator contracts, including censoring and information guards."""

import numpy as np
import pytest

from ic_study.analysis.redesign import critical_dose


def test_dose_estimator_interpolates_and_never_extrapolates() -> None:
    assert critical_dose([0, 0.2, 0.4], [1, 0.5, 0]) == pytest.approx(0.2)
    assert critical_dose([0, 0.2], [0.8, 0.2]) == pytest.approx(0.1)
    assert critical_dose([0, 0.2, 0.4], [0.9, 0.7, 0.8]) is None
    assert critical_dose([0, 0.2, 0.4], [0.4, 0.3, 0.1]) is None
    assert critical_dose([0, 1, 2, 3], [1, 0.4, 0.6, 0]) == pytest.approx(1)


def test_discriminator_ties_score_half_and_lags_ignore_missing() -> None:
    from ic_study.analysis.redesign import (
        balanced_accuracy,
        fit_discriminant,
        lag_features,
    )

    x = np.zeros((8, 4))
    labels = np.array([0, 1] * 4, dtype=np.int64)
    model = fit_discriminant(x, labels)
    assert balanced_accuracy(model.score(x), labels) == 0.5
    ordered = np.tile(np.arange(12, dtype=np.int64) % 11, (11, 1))
    ordered[5:, :2] = -1
    np.testing.assert_allclose(lag_features(ordered), np.ones(4))
    with pytest.raises(ValueError, match="pairs"):
        lag_features(np.full((11, 12), -1, dtype=np.int64))
    separable = np.array([[-2.0], [-1.0], [1.0], [2.0]])
    truth = np.array([0, 0, 1, 1], dtype=np.int64)
    assert (
        balanced_accuracy(fit_discriminant(separable, truth).score(separable), truth)
        == 1
    )


def test_operating_choice_is_blind_and_seeds_are_isolated() -> None:
    from ic_study.simulation.redesign_calibration import operating_choice, pilot_seed

    assert (
        operating_choice([(0.05, 0.6, 0.001), (0.1, 0.72, 0.002), (0.2, 0.8, 0)]) == 0.1
    )
    assert operating_choice([(0.05, 0.99, 0), (0.1, 0.75, 0.02)]) is None
    assert pilot_seed("match", "state", 2) != pilot_seed("primary-check", "state", 2)
    assert pilot_seed("match", "state", 2) != pilot_seed("match", "network", 2)
    with pytest.raises(ValueError, match="confirmatory"):
        pilot_seed("confirm-test", "state", 0)


def test_primary_pilot_reports_only_coarse_gates() -> None:
    from ic_study.simulation.redesign_calibration import dose_gate, panel_gate

    assert panel_gate(0.73) == {"non_floor_non_ceiling": True}
    assert panel_gate(0.99) == {"non_floor_non_ceiling": False}
    assert dose_gate([0, 0.1, 0.2], [[1, 0.5, 0], [1, 0.6, 0]]) == {
        "each_arm_has_interior_cell": True,
        "both_cross_half": True,
    }
    assert not dose_gate([0, 0.1], [[1, 1], [0, 0]])["both_cross_half"]


def test_completed_output_cannot_be_reused_and_budget_stops_before_simulation(
    tmp_path: object,
) -> None:
    import json
    from pathlib import Path

    from ic_study.simulation.redesign_calibration import CalibrationRun, CalibrationSpec

    spec_path = (
        Path(__file__).parents[2]
        / "experiments/exploratory/redesign-calibration-v1/spec.json"
    )
    spec = CalibrationSpec(**json.loads(spec_path.read_text()))
    destination = Path(str(tmp_path)) / "run"
    run = CalibrationRun(spec, destination)
    with pytest.raises(FileExistsError):
        CalibrationRun(spec, destination)
    run.started -= 1201
    with pytest.raises(TimeoutError):
        run.panel("primary-check", 0, 0.1, 0.85)
    assert run.simulations == 0
