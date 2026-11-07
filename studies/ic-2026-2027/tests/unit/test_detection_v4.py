"""Observable successor contracts; frozen implementation is an independent oracle."""

from pathlib import Path

import numpy as np
import pytest

from ic_study.models.detection_panel import influence_panel
from ic_study.models.detection_panel_v4 import influence, null


@pytest.mark.parametrize("steps", [1, 24])
@pytest.mark.parametrize("family", ["A", "B", "D", "E"])
def test_full_n_identity(family: str, steps: int) -> None:
    expected = influence_panel(
        10626, 11, 321, 987, share=0, repulsion=0.25, interactions=steps
    )
    actual = null(10626, 11, 321, 654, family=family, phi=0.85, eta=0, steps=steps)
    assert actual.tobytes() == expected.tobytes()


@pytest.mark.parametrize(
    "steps,anchor,repulsion", [(1, 0, 0.25), (24, 0, 0), (1, 1, 0.25)]
)
def test_optimized_alternative_preserves_frozen_bytes(
    steps: int, anchor: float, repulsion: float
) -> None:
    expected = influence_panel(
        10626,
        11,
        321,
        987,
        share=0.03,
        repulsion=repulsion,
        anchor=anchor,
        interactions=steps,
    )
    actual = influence(
        10626,
        11,
        321,
        987,
        share=0.03,
        repulsion=repulsion,
        anchor=anchor,
        steps=steps,
    )
    np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize(
    "channel", ["observed", "latent", "ordinal_one", "latent_rank"]
)
@pytest.mark.parametrize(
    "c,delta,steps", [(0, 0, 1), (0.5, 0, 1), (0, 0.2, 1), (0, 0, 24)]
)
def test_identity_survives_channels_and_matching_validation_coupling(
    channel: str,
    c: float,
    delta: float,
    steps: int,
) -> None:
    from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan

    cell = Cell(0, 0.7, channel=channel, error_correlation=c, gain=delta, steps=steps)
    source = PanelSource(cell, SeedPlan(7))
    for family in ("A", "B", "D", "E"):
        from dataclasses import replace

        source = PanelSource(replace(cell, family=family), SeedPlan(7))
        for phase in ("match", "validate"):
            left = source.profiles(phase, 1, parameters=np.array([0.85, 0]))
            right = source.profiles(phase, 1)
            assert left.tobytes() == right.tobytes()
    for phase in ("train", "check", "reference"):
        assert not np.array_equal(
            source.profiles(phase, 1),
            source.profiles(phase, 1, parameters=np.array([0.85, 0])),
        )


def test_seed_audit_phase_disjointness_and_confirmatory_reservation() -> None:
    from ic_study.simulation.detection_v4 import SeedPlan

    plan = SeedPlan(4)
    seeds = [
        plan.seed(phase, role, index)
        for phase in ("match", "validate", "train", "check", "reference")
        for role in ("state", "null-state", "network", "mask", "error", "heap")
        for index in range(16)
    ]
    assert len(set(seeds)) == len(seeds)
    assert plan.seed("train", "state", 0) != SeedPlan(5).seed("train", "state", 0)
    with pytest.raises(ValueError, match="reserved"):
        plan.seed("confirmatory", "state", 0)


def test_b_iid_trait_and_e_stayer_laws_follow_declared_transport() -> None:
    from ic_study.models.anchored_panel import normal_ranks

    state = influence(600, 11, 321, 0, share=0, phi=0.8)
    iid = np.random.default_rng(654).normal(size=600)
    expected_b = np.stack(
        [normal_ranks(np.sqrt(0.2) * iid + np.sqrt(0.8) * row) for row in state]
    )
    np.testing.assert_array_equal(
        null(600, 11, 321, 654, family="B", phi=0.8, eta=0.2), expected_b
    )
    stayers = np.random.default_rng(654).random(600) < 0.2
    expected_e = np.stack(
        [normal_ranks(np.where(stayers, state[0], row)) for row in state]
    )
    np.testing.assert_array_equal(
        null(600, 11, 321, 654, family="E", phi=0.8, eta=0.2), expected_e
    )


def test_omega_one_is_strength_independent_degeneracy_without_identity_claim() -> None:
    from ic_study.simulation.detection_v4 import Cell

    first = influence(600, 11, 31, 91, share=0.001, anchor=1)
    last = influence(600, 11, 31, 91, share=0.9, anchor=1)
    np.testing.assert_array_equal(first, last)
    np.testing.assert_array_equal(first, np.repeat(first[:1], 11, axis=0))
    assert not Cell(0, 0.7, anchor=1).identity


def test_matching_checkpoint_resume_avoids_regeneration(tmp_path: Path) -> None:
    from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan
    from ic_study.simulation.v4_store import SealedStore

    store = SealedStore(tmp_path / "sealed")
    source = PanelSource(Cell(0, 0.7), SeedPlan(2), size=60, store=store)
    values = source.profiles("match", 34)
    assert source.panels == 34
    resumed = PanelSource(Cell(0, 0.7), SeedPlan(2), size=60, store=store)
    np.testing.assert_array_equal(resumed.profiles("match", 34), values)
    assert resumed.panels == 0


def test_seed_reservation_domains_do_not_alias_validation() -> None:
    from ic_study.simulation.detection_v4 import SeedPlan

    for phase in ("validate", "nuisance", "bootstrap", "stencil"):
        assert SeedPlan(0).seed(phase, "state", 0) != SeedPlan(0, gate=True).seed(
            phase, "state", 0
        )
    with pytest.raises(ValueError):
        SeedPlan(10000).seed("validate", "state", 0)


def test_v1_protocol_hash_is_unchanged() -> None:
    import hashlib

    study = Path(__file__).resolve().parents[2]
    frozen = (
        study
        / "research/questions/exploration/2026-09-24-parallel"
        / "detection-boundary-preregistration-frozen.md"
    )
    assert (
        hashlib.sha256(frozen.read_bytes()).hexdigest()
        == "fb6b4dcf43161a52c725e565bf2a4d2697423bec7d138ad1d30388547cfcd706"
    )
