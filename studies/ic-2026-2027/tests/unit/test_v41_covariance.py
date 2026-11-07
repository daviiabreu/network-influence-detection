"""First-order covariance diagnostic on a known Gaussian moment model."""

from pathlib import Path
from statistics import NormalDist

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import covariance_diagnostic


def test_covariance_direction_and_auc_derivatives_match_regeneration() -> None:
    rng = np.random.default_rng(44)
    train0, train1 = rng.normal(size=(80, 3)), rng.normal(0.3, size=(80, 3))
    ref0, ref1 = rng.normal(size=(100, 3)), rng.normal(0.3, size=(100, 3))
    derivative = np.stack([np.diag([0.2, -0.1, 0.1]), np.zeros((3, 3))])
    shifts = np.array([[0.001, 0.0], [-0.001, 0.0]])
    result = covariance_diagnostic(
        train0, train1, ref0, ref1, derivative, derivative, shifts, d5_se=1e-6
    )

    def regenerated(t: float) -> tuple[np.ndarray, float]:
        c0 = np.cov(train0, rowvar=False) + t * derivative[0]
        c1 = np.cov(train1, rowvar=False)
        delta = train1.mean(0) - train0.mean(0)
        pooled = (c0 + c1) / 2
        total_var = 79 / 160 * np.diag(c0 + c1) + delta**2 / 4
        w = np.linalg.solve(0.8 * pooled + 0.2 * np.diag(total_var), delta)
        variance = (
            w
            @ (
                np.cov(ref0, rowvar=False)
                + np.cov(ref1, rowvar=False)
                + t * derivative[0]
            )
            @ w
        )
        probability = NormalDist().cdf(
            float(w @ (ref1.mean(0) - ref0.mean(0)) / np.sqrt(variance))
        )
        return w, probability

    minus, plus = regenerated(-1e-5), regenerated(1e-5)
    np.testing.assert_allclose(
        result.direction_shifts[0], (plus[0] - minus[0]) / 2e-5 * 0.001, rtol=1e-6
    )
    assert result.auc_shifts[0] == pytest.approx(
        (plus[1] - minus[1]) / 2e-5 * 0.001, rel=1e-6
    )
    assert result.flagged
    zero = covariance_diagnostic(
        train0, train1, ref0, ref1, derivative * 0, derivative * 0, shifts, d5_se=0.01
    )
    assert not zero.flagged
    assert not zero.auc_shifts.any()


def test_covariance_stencils_are_opt_in_and_confined_to_train_reference() -> None:
    from ic_study.models.anchored_panel import Floats
    from ic_study.simulation.detection_v4 import (
        Cell,
        PanelSource,
        SeedPlan,
        covariance_stencils,
    )

    class SyntheticSource(PanelSource):
        def __init__(self, cell: Cell, seeds: SeedPlan, *, size: int) -> None:
            super().__init__(cell, seeds, size=size)
            self.phases: list[str] = []

        def profiles(
            self,
            phase: str,
            count: int,
            *,
            parameters: Floats | None = None,
            attempt: int = 0,
            start: int = 0,
        ) -> Floats:
            self.phases.append(phase)
            assert parameters is not None
            rng = np.random.default_rng(2)
            return np.asarray(rng.normal(size=(count, 5)) * parameters[0])

    source = SyntheticSource(Cell(0.03, 0.7), SeedPlan(2), size=6)
    point = np.array([0.5, 0.1])
    assert covariance_stencils(source, point, 0.01, enabled=False) is None
    assert source.phases == []
    result = covariance_stencils(source, point, 0.01, enabled=True)
    assert result is not None
    assert result[0].shape == result[1].shape == (2, 3, 3)
    assert set(source.phases) == {"train", "reference"}


def test_g2_reports_covariance_flags_without_changing_criteria(tmp_path: Path) -> None:
    import json
    from pathlib import Path

    from ic_study.simulation.v4_gate import aggregate
    from ic_study.simulation.v4_plan import gate_tasks
    from ic_study.simulation.v4_store import SealedStore

    criteria = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
        ).read_text()
    )
    cells = ((0.03, 0.7),)
    rng = np.random.default_rng(4103)
    points = rng.normal(0.6, 0.01, 100)
    reports = []
    for flagged in (False, True):
        root = tmp_path / str(flagged)
        SealedStore(root)
        for task in gate_tasks("G2", cells=cells):
            SealedStore(root / task.key).put_json(
                "result",
                dict(
                    success=True,
                    auc=float(points[task.index]),
                    se=0.01,
                    nuisance_variance=[0.00001] * 2,
                    mean_shift=[0.0] * 2,
                    covariance_diagnostics=[dict(flagged=flagged)] * 2,
                ),
            )
        reports.append(aggregate("G2", root, criteria, cells=cells))
    assert reports[0]["pass"] == reports[1]["pass"]
    assert reports[0]["covariance_flag_counts"] == [0]
    assert reports[1]["covariance_flag_counts"] == [100]
