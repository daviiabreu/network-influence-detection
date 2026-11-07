"""Selective extraction preserves the pre-revision feature bytes."""

import numpy as np
import pytest

from ic_study.analysis.detection_boundary import feature_channels
from ic_study.models.anchored_panel import panel_mask
from ic_study.models.detection_panel import measurement, ordinal_channel
from ic_study.models.detection_panel_v4 import null
from ic_study.simulation.detection_v4 import selected_features


@pytest.mark.parametrize("family", list("ABCDE"))
@pytest.mark.parametrize(
    "channel,mobility",
    [
        (channel, mobility)
        for channel in ("observed", "latent", "ordinal_one", "latent_rank")
        for mobility in (False, True)
        if not (mobility and channel == "latent_rank")
    ],
)
def test_selected_features_are_byte_identical(
    family: str, channel: str, mobility: bool
) -> None:
    latent = null(
        10626, 11, 31, 32, family=family, phi=0.85, eta=0 if family in "AC" else 0.1
    )
    mask = panel_mask(10626, 11, 33, retention=0.89)
    mass = 0.1 if family == "C" else 0.0
    observed = ordinal_channel(
        measurement(latent, 0.7, 34, heteroscedastic=family == "C"),
        mask,
        midpoint_mass=mass,
        heap_seed=35 if family == "C" else None,
    )
    old = feature_channels(latent, observed, midpoint_mass=mass)
    expected = old[channel]
    if mobility:
        expected = np.concatenate((expected[:2], old[channel + "_mobility"]))
    actual = selected_features(
        latent, observed, channel=channel, mobility=mobility, midpoint_mass=mass
    )
    assert actual.tobytes() == expected.tobytes()
