"""Coverage calibration must preserve seed and network-unit boundaries."""

from pathlib import Path
from typing import TypedDict

import numpy as np
import pytest

from ic_study.models.anchored_panel import Floats
from ic_study.simulation.detection_calibration import PilotSpec
from ic_study.simulation.detection_coverage_check import (
    CoveragePilot,
    match_observed,
    observed_features,
    run_refit,
)


def test_coverage_repetitions_and_refits_use_disjoint_calibration_seeds(
    tmp_path: Path,
) -> None:
    spec = PilotSpec(grid=(0.0,), size=600)
    baseline = CoveragePilot(spec, tmp_path / "baseline", repetition=0, block=0)
    refit = CoveragePilot(spec, tmp_path / "refit", repetition=0, block=1)
    repeat = CoveragePilot(spec, tmp_path / "repeat", repetition=1, block=0)
    assert baseline.seed("match", "state", 1) != refit.seed("match", "state", 1)
    assert baseline.seed("match", "state", 1) != repeat.seed("match", "state", 1)
    assert baseline.seed("reference", "state", 1) == refit.seed("reference", "state", 1)
    assert baseline.seed("reference", "state", 1) != repeat.seed(
        "reference", "state", 1
    )
    assert "confirmatory" not in baseline.namespace


def test_observed_only_coverage_features_are_byte_identical(tmp_path: Path) -> None:
    class PanelOptions(TypedDict, total=False):
        rho: float

    pilot = CoveragePilot(
        PilotSpec(grid=(0.0,), size=600), tmp_path / "panel", repetition=0, block=0
    )
    for label in (0, 1):
        options: PanelOptions = {"rho": 0.85} if label == 0 else {}
        full = pilot.panel("train", label, 0.0, **options)
        observed = pilot.panel("train", label, 0.0, observed_only=True, **options)
        np.testing.assert_array_equal(observed["observed"], full["observed"])


def test_coverage_matching_uses_both_observed_lags(tmp_path: Path) -> None:
    class KnownPilot(CoveragePilot):
        def panel(
            self,
            phase: str,
            i: int,
            share: float,
            *,
            rho: float | None = None,
            trait: float = 0,
            family: str = "B",
            observed_only: bool = False,
        ) -> dict[str, Floats]:
            rho, trait = (0.8, 0.2) if rho is None else (rho, trait)
            offset = (i // 2 - 127.5) * 0.00004
            return {
                "observed": np.array(
                    [
                        0.7 * (trait + (1 - trait) * rho) + offset,
                        0.65 * (trait + (1 - trait) * rho**2) + offset,
                    ]
                )
            }

    pilot = KnownPilot(
        PilotSpec(grid=(0.0,), size=600, matching=256),
        tmp_path / "match",
        repetition=0,
        block=0,
    )
    fit = match_observed(pilot, 0.0)
    assert fit.rho == pytest.approx(0.8, abs=0.003)
    assert fit.trait == pytest.approx(0.2, abs=0.01)


def test_observed_features_keep_two_events_per_network(tmp_path: Path) -> None:
    from ic_study.simulation.detection_calibration import CellFit

    pilot = CoveragePilot(
        PilotSpec(grid=(0.0,), size=600, training=4),
        tmp_path / "features",
        repetition=0,
        block=0,
    )
    fit = CellFit(0.85, 0.0, "observed", 0.5)
    features = observed_features(pilot, "train", 0.0, fit, 0, 4)
    expected = np.stack(
        [
            pilot.panel("train", 2 * i, 0.0, rho=fit.rho, trait=fit.trait)["observed"][
                2:5
            ]
            for i in range(4)
        ]
    )
    np.testing.assert_array_equal(features, expected)
    assert pilot.seed("train", "network", 0) != pilot.seed("train", "network", 1)


def test_refit_uses_fixed_reference_population(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ic_study.simulation import detection_coverage_check as module

    phases: list[str] = []

    class KnownPilot(CoveragePilot):
        def panel(
            self,
            phase: str,
            i: int,
            share: float,
            *,
            rho: float | None = None,
            trait: float = 0,
            family: str = "B",
            observed_only: bool = False,
        ) -> dict[str, Floats]:
            phases.append(phase)
            self.panels += 1
            label = float(rho is None)
            rho, trait = (0.8, 0.2) if rho is None else (rho, trait)
            offset = (i // 2 - 127.5) * 0.00004
            return {
                "observed": np.array(
                    [
                        0.7 * (trait + (1 - trait) * rho) + offset,
                        0.65 * (trait + (1 - trait) * rho**2) + offset,
                        0.1 + offset + 0.01 * label,
                        0.2 + offset + 0.02 * label,
                        0.3 + offset + 0.03 * label,
                    ]
                )
            }

    monkeypatch.setattr(module, "CoveragePilot", KnownPilot)
    spec = PilotSpec(
        grid=(0.0,),
        size=600,
        reliability=0.7,
        matching=256,
        training=4,
        checking=4,
        seconds=120,
    )
    social = np.ones((4, 3))
    result = run_refit(spec, 0, 1, 0.0, tmp_path / "refit", social)
    assert result.block == 1
    assert 0 <= result.auc <= 1
    assert result.panels >= 2 * spec.matching + 2 * spec.training + spec.checking
    assert set(phases) == {"match", "train", "reference"}
