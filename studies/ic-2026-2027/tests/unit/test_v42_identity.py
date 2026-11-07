"""Full-population byte identity through every observed-channel transformation."""

from collections.abc import Callable
from dataclasses import replace
from typing import Any

import numpy as np
import pytest

from ic_study.simulation import detection_v4
from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan


@pytest.mark.parametrize("family", ["A", "B", "D", "E"])
@pytest.mark.parametrize("phase", ["match", "validate"])
@pytest.mark.parametrize("attempt", [0, 1])
@pytest.mark.parametrize(
    "cell",
    [
        Cell(0, 0.7),
        Cell(0, 0.7, mobility=True),
        Cell(0, 0.7, error_correlation=0.25),
        Cell(0, 0.7, error_correlation=0.5),
        Cell(0, 0.7, gain=0.1),
        Cell(0, 0.7, gain=0.2),
        Cell(0, 0.7, error_correlation=0.5, gain=0.2),
        Cell(0, 0.7, steps=24),
    ],
    ids=["main", "mobility", "c025", "c050", "d010", "d020", "combined", "24-step"],
)
def test_full_n_anchor_identity_at_every_channel_stage(
    monkeypatch: pytest.MonkeyPatch,
    cell: Cell,
    family: str,
    phase: str,
    attempt: int,
) -> None:
    captured: dict[str, list[bytes]] = {}

    def record(name: str, original: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            result = original(*args, **kwargs)
            if name != "selected_features":
                assert result.shape == (11, 10626)
            captured.setdefault(name, []).append(result.tobytes())
            return result

        return wrapped

    for name in ("panel_mask", "measurement", "ordinal_channel", "selected_features"):
        monkeypatch.setattr(
            detection_v4, name, record(name, getattr(detection_v4, name))
        )

    source = PanelSource(replace(cell, family=family), SeedPlan(7, block=3))
    alternative = source.profiles(phase, 1, attempt=attempt)
    anchored_null = source.profiles(
        phase, 1, parameters=np.array([0.85, 0.0]), attempt=attempt
    )
    assert alternative.tobytes() == anchored_null.tobytes()
    for stage, values in captured.items():
        assert len(values) == 2, stage
        assert values[0] == values[1], stage


@pytest.mark.parametrize(
    ("channel", "mobility"),
    [
        ("latent", False),
        ("ordinal_one", False),
        ("latent_rank", False),
        ("observed", True),
        ("latent", True),
        ("ordinal_one", True),
    ],
)
@pytest.mark.parametrize("phase", ["match", "validate"])
@pytest.mark.parametrize("attempt", [0, 1])
def test_full_n_control_channel_anchor_identity(
    channel: str, mobility: bool, phase: str, attempt: int
) -> None:
    source = PanelSource(
        Cell(0, 0.7, family="B", channel=channel, mobility=mobility),
        SeedPlan(17, block=2),
    )
    alternative = source.profiles(phase, 1, attempt=attempt)
    anchored = source.profiles(
        phase, 1, parameters=np.array([0.85, 0.0]), attempt=attempt
    )
    assert alternative.tobytes() == anchored.tobytes()
