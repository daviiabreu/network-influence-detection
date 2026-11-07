"""Analytic panel source exercises retry orchestration without a classifier."""

from typing import Any, cast

import numpy as np
import pytest

from ic_study.models.anchored_panel import Floats
from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan, fit_cell


class AnalyticPanels(PanelSource):
    def __init__(self, *, pass_retry: bool) -> None:
        super().__init__(Cell(0.03, 0.7, family="A"), SeedPlan(1), size=60)
        self.pass_retry = pass_retry
        self.calls: list[tuple[str, int, int]] = []

    def profiles(
        self,
        phase: str,
        count: int,
        *,
        parameters: Floats | None = None,
        attempt: int = 0,
        start: int = 0,
    ) -> Floats:
        self.calls.append((phase, count, attempt))
        result = np.zeros((count, 5))
        if parameters is not None:
            result[:, 0] = parameters[0] - 0.4
            if phase == "validate":
                result[:, 0] = 0.001 if attempt == 0 or not self.pass_retry else 0.0
        return result


@pytest.mark.parametrize("pass_retry", [True, False])
def test_one_fresh_validation_retry_preserves_both_attempts(pass_retry: bool) -> None:
    source = AnalyticPanels(pass_retry=pass_retry)
    result = fit_cell(source)
    assert result.success is pass_retry
    assert [attempt.count for attempt in result.attempts] == [1024, 4096]
    assert result.attempts[0].validation is not None
    assert not result.attempts[0].validation.passed
    assert {entry for entry in source.calls if entry[0] == "validate"} == {
        ("validate", 2048, 0),
        ("validate", 2048, 1),
    }
    assert not any(
        phase in {"train", "check", "reference"} for phase, _, _ in source.calls
    )


def test_validation_combines_fit_and_validation_sampling_error() -> None:
    from ic_study.analysis.detection_boundary_v4 import validate_fit

    rng = np.random.default_rng(4101)
    old_failures = new_failures = 0
    for _ in range(3000):
        fitting = rng.normal(size=(1024, 2))
        fitted_mean = fitting.mean(0)
        fresh = rng.normal(size=(4096, 2)) - fitted_mean
        old_failures += bool(
            np.any(np.abs(fresh.mean(0)) > 4 * fresh.std(0, ddof=1) / 64)
        )
        revised = validate_fit(fresh[:2048], 2, fitting.std(0, ddof=1) / 32)
        new_failures += not revised.passed
    assert 0.11 < old_failures / 3000 < 0.17
    assert new_failures / 3000 < 0.003


def test_matching_report_labels_combined_validation_error_and_keeps_diagnostics() -> (
    None
):
    from ic_study.simulation.v4_gate import fit_record

    result = fit_cell(AnalyticPanels(pass_retry=True))
    report = fit_record(result)
    first, second = cast(list[dict[str, Any]], report["attempts"])
    z = first["validation_combined_se_units"][0]
    assert z is None or z > 4
    assert first["validation_combined_se_units"][1] == 0.0
    assert second["equivalence_statistic"] == [0.0, 0.0]
    assert second["amplification"] == 0.0
