"""Fresh calibration namespace and one-bit disclosure boundary."""

from pathlib import Path

import numpy as np
import pytest

from ic_study.models.anchored_panel import Floats
from ic_study.simulation.detection_calibration import calibration_seed, disclosure


def test_only_calibration_roles_are_available_and_seeds_are_disjoint() -> None:
    seeds = {
        calibration_seed(phase, role, i)
        for phase in ("match", "train", "check")
        for role in ("state", "network", "mask", "error")
        for i in range(10)
    }
    assert len(seeds) == 120
    with pytest.raises(ValueError, match="calibration"):
        calibration_seed("confirm-test", "state", 0)


def test_disclosure_contains_only_interior_boolean_not_boundary_or_curve() -> None:
    grid = np.array([0.0, 0.01, 0.1, 0.9])
    assert disclosure(grid, np.array([0.5, 0.6, 0.8, 0.9])) == {
        "interior_at_r070": True
    }
    assert disclosure(grid, np.array([0.5, 0.6, 0.65, 0.69])) == {
        "interior_at_r070": False
    }
    assert disclosure(grid, np.array([0.8, 0.8, 0.9, 0.9])) == {
        "interior_at_r070": False
    }


def test_coarse_disclosure_serialises_to_json_without_numpy_scalars() -> None:
    import json

    result = disclosure(np.array([0.0, 0.01, 0.1]), np.array([0.5, 0.8, 0.9]))
    assert json.loads(json.dumps(result)) == {"interior_at_r070": True}


def test_runner_matches_observed_not_latent_and_rematches_each_control(
    tmp_path: Path,
) -> None:
    from ic_study.simulation.detection_calibration import DetectionPilot, PilotSpec

    class KnownChannels(DetectionPilot):
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
            # Latent and observed targets deliberately cannot be interchanged.
            observed = (
                np.array(
                    [
                        0.7 * (trait + (1 - trait) * rho),
                        0.65 * (trait + (1 - trait) * rho**2),
                        0.2,
                        0.1,
                        0.05,
                    ]
                )
                + offset
            )
            latent = observed + np.array([0.18, 0.22, 0.1, 0.1, 0.1])
            return {"observed": observed, "latent": latent}

    pilot = KnownChannels(PilotSpec(grid=(0.0,), size=66), tmp_path / "run")
    fitted = pilot.match_cell(0.0, family="B", channel="observed")
    assert fitted.rho == pytest.approx(0.8, abs=0.003)
    assert fitted.trait == pytest.approx(0.2, abs=0.01)
    control = pilot.match_cell(0.0, family="B", channel="latent")
    assert control.channel == "latent"
    assert control.target_lag1 == pytest.approx(0.7 * (0.2 + 0.8 * 0.8) + 0.18)


def test_runner_wires_heaping_null_and_all_distinct_channels(tmp_path: Path) -> None:
    from ic_study.simulation.detection_calibration import DetectionPilot, PilotSpec

    pilot = DetectionPilot(PilotSpec(grid=(0.0,), size=660), tmp_path / "run")
    ordinary = pilot.panel("match", 0, 0.0, rho=0.8, family="A")
    heaped = pilot.panel("match", 0, 0.0, rho=0.8, family="C")
    state = pilot.panel("match", 0, 0.0, rho=0.6, family="D")
    assert {"observed", "latent", "ordinal_one", "latent_rank"} <= heaped.keys()
    assert "rank" not in heaped
    np.testing.assert_allclose(ordinary["latent"], heaped["latent"])
    assert not np.allclose(ordinary["observed"], heaped["observed"])
    assert not np.allclose(state["latent"], ordinary["latent"])


def test_refits_have_independent_matching_but_common_reference_draws() -> None:
    assert calibration_seed("match", "state", 3, replicate=1) != calibration_seed(
        "match", "state", 3, replicate=2
    )
    assert calibration_seed("reference", "state", 3, replicate=1) == calibration_seed(
        "reference", "state", 3, replicate=2
    )


def test_scores_exclude_both_matched_lags(tmp_path: Path) -> None:
    from ic_study.simulation.detection_calibration import (
        CellFit,
        DetectionPilot,
        PilotSpec,
    )

    class MatchedOnly(DetectionPilot):
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
            label = float(rho is None)
            return {"observed": np.array([label, label, 0.2, 0.1, 0.05])}

    pilot = MatchedOnly(
        PilotSpec(grid=(0.0,), size=66, training=4, checking=4), tmp_path / "run"
    )
    scores = pilot.scores(0.0, CellFit(0.8, 0.1, "observed", 0.6), family="B")
    np.testing.assert_array_equal(scores, np.zeros((2, 4)))


def test_observed_only_panel_preserves_calibration_profile(tmp_path: Path) -> None:
    from ic_study.simulation.detection_calibration import DetectionPilot, PilotSpec

    pilot = DetectionPilot(PilotSpec(grid=(0.0,), size=600), tmp_path / "run")
    full = pilot.panel("match", 1, 0.0, family="B")
    optimized = pilot.panel("match", 1, 0.0, family="B", observed_only=True)
    np.testing.assert_array_equal(optimized["observed"], full["observed"])
    assert set(optimized) == {"observed"}
