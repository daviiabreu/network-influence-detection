"""Runner authorization and synthetic mechanics, without executing a gate."""

from pathlib import Path

import numpy as np
import pytest

from ic_study.simulation.v4_gate import preflight, synthetic_scores


def test_gate_refuses_execution_without_freeze_record(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="freeze"):
        preflight(tmp_path / "absent.json", tmp_path)


@pytest.mark.parametrize(
    "scenario",
    ["gaussian-icc0", "gaussian-icc05", "non-gaussian", "ties", "dependent-slots"],
)
def test_synthetic_mechanics_shapes_ties_and_slot_dependence(scenario: str) -> None:
    left, right = synthetic_scores(scenario, seed=5, networks=30)
    assert left.shape == right.shape == (30, 2, 9)
    assert not np.array_equal(left, right)
    if scenario == "ties":
        assert np.all(left == left.astype(int))
    if scenario == "dependent-slots":
        assert np.corrcoef(left[..., 0].ravel(), left[..., 1].ravel())[0, 1] > 0.5
