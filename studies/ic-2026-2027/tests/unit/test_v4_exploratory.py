"""Exploratory X1a/X2 successors; frozen v4 code is the oracle wherever it exists."""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from scipy.interpolate import CubicSpline

from ic_study.analysis.detection_boundary_v4 import score_uncertainty
from ic_study.models.detection_panel import bounded_drift, influence_update
from ic_study.models.detection_panel_v4 import influence
from ic_study.simulation import detection_v4
from ic_study.simulation import v4_exploratory as x
from ic_study.simulation.amendment_a import fast_ranks, rank_grid
from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan
from ic_study.simulation.v4_curve import ConfirmatorySeedPlan

STUDY = Path(__file__).resolve().parents[2]


def brute_moments(values: np.ndarray, repulsion: float) -> tuple[Any, Any]:
    gap = values[None, :] - values[:, None]
    kernel = np.where(np.abs(gap) <= 1, gap, -repulsion * gap)
    mean = kernel.mean(axis=1)
    return mean, (kernel**2).mean(axis=1) - mean**2


# Floating-point pairs where fl(z_j - z) sits on the window edge although
# z_j compares differently with fl(z -/+ 1): a plain searchsorted misplaces them.
ULP_EDGES = [
    0.6404226504432821,
    -0.35957734955671805,
    -0.359577349556718,
    -0.7037352358069926,
    0.29626476419300746,
    0.2962647641930075,
]


@pytest.mark.parametrize("repulsion", [0.25, 0.0])
@pytest.mark.parametrize(
    "values",
    [
        np.random.default_rng(11).normal(size=97),
        np.array([-2, -1, -1, -0.5, 0, 0, 0.5, 1, 1, 2, 3.0]),
        np.array([*ULP_EDGES, 0.5, -1.2, 1.9]),
        np.array([0.3]),
        np.full(7, -0.4),
    ],
    ids=["normal", "exact-edges-and-ties", "ulp-edges", "single", "all-equal"],
)
def test_mean_field_moments_match_brute_force(
    values: np.ndarray, repulsion: float
) -> None:
    mean, variance = x.mean_field_moments(values, repulsion)
    expected_mean, expected_variance = brute_moments(values, repulsion)
    np.testing.assert_allclose(mean, expected_mean, rtol=0, atol=1e-13)
    np.testing.assert_allclose(
        variance, np.maximum(expected_variance, 0), rtol=0, atol=1e-13
    )


def test_first_index_is_exact_whatever_the_guess() -> None:
    rng = np.random.default_rng(3)
    ordered = np.sort(np.round(rng.normal(size=200), 1))
    values = rng.normal(size=300)

    def accept(z_j: np.ndarray, z: np.ndarray) -> Any:
        return z_j - z >= -1

    expected = np.array(
        [np.argmax(np.append(accept(ordered, v), True)) for v in values]
    )
    for guess in (
        np.zeros(len(values), dtype=np.int64),
        rng.integers(0, len(ordered) + 1, size=len(values)),
        np.searchsorted(ordered, values - 1),
    ):
        np.testing.assert_array_equal(
            x.first_index(ordered, values, accept, guess), expected
        )


def test_ulp_edges_defeat_a_plain_searchsorted() -> None:
    values = np.array(ULP_EDGES)
    ordered = np.sort(values)
    start = np.zeros(len(values), dtype=np.int64)
    lower = x.first_index(ordered, values, lambda a, b: a - b >= -1, start)
    upper = x.first_index(ordered, values, lambda a, b: a - b > 1, start)
    assert not np.array_equal(lower, np.searchsorted(ordered, values - 1, "left"))
    assert not np.array_equal(upper, np.searchsorted(ordered, values + 1, "right"))


def test_mean_field_moments_are_the_network_drift_moments() -> None:
    """Uniform permutation partners make m and v/8 the conditional mean and
    variance of the frozen network drift at a fresh network draw."""
    size, networks = 120, 4000
    state = fast_ranks(np.random.default_rng(5).normal(size=size))
    mean, variance = x.mean_field_moments(state, 0.25)
    rng = np.random.default_rng(6)
    draws = np.stack(
        [
            bounded_drift(
                state, np.stack([rng.permutation(size) for _ in range(8)], 1), 0.25
            )
            for _ in range(networks)
        ]
    )
    error = np.sqrt(variance / 8 / networks)
    assert np.max(np.abs(draws.mean(0) - mean) / error) < 5
    np.testing.assert_allclose(draws.var(0, ddof=1), variance / 8, rtol=0.15)


@pytest.mark.parametrize("anchor", [0, 0.5])
@pytest.mark.parametrize("repulsion", [0.25, 0])
@pytest.mark.parametrize("steps", [1, 24])
@pytest.mark.parametrize("share", [0, 0.001, 0.3, 0.9])
def test_interaction_path_reproduces_frozen_influence_bitwise(
    share: float, steps: int, repulsion: float, anchor: float
) -> None:
    path = x.interaction_path(
        60, 11, 41, 43, share=share, repulsion=repulsion, anchor=anchor, steps=steps
    )
    frozen = influence(
        60, 11, 41, 43, share=share, repulsion=repulsion, anchor=anchor, steps=steps
    )
    assert np.array_equal(path.path, frozen)
    assert path.states.shape == ((11 - 1) * steps + 1, 60)
    assert path.drift.shape == ((11 - 1) * steps, 60)


@pytest.mark.parametrize("share", [0, 0.3])
def test_exposed_drift_is_the_one_each_step_uses(share: float) -> None:
    size, anchor, repulsion = 60, 0.5, 0.25
    path = x.interaction_path(
        size, 3, 7, 9, share=share, repulsion=repulsion, anchor=anchor, steps=4
    )
    partners = x.network_partners(size, 9)
    rng = np.random.default_rng(7)
    initial = fast_ranks(rng.normal(size=size))
    for k, drift in enumerate(path.drift):
        before, noise = path.states[k], rng.normal(size=size)
        raw = bounded_drift(before, partners, repulsion)
        assert np.array_equal(drift, (raw - raw.mean()) / raw.std())
        update = (
            influence_update(
                before, partners, noise, rho=0.85, share=share, repulsion=repulsion
            )
            if share
            else 0.85 * before + np.sqrt(1 - 0.85**2) * noise
        )
        expected = fast_ranks((1 - anchor) * update + anchor * initial)
        assert np.array_equal(path.states[k + 1], expected)


@pytest.mark.parametrize(
    "steps,repulsion,anchor", [(1, 0.25, 0), (24, 0, 0), (1, 0.25, 0.5)]
)
def test_mean_field_twin_invariants(
    steps: int, repulsion: float, anchor: float
) -> None:
    size, share = 90, 0.6
    twin = x.mean_field_path(
        size, 11, 21, 22, share=share, repulsion=repulsion, anchor=anchor, steps=steps
    )
    assert twin.path.shape == (11, size)
    assert twin.drift.shape == (10 * steps, size)
    grid = rank_grid(size)
    assert all(np.array_equal(np.sort(row), grid) for row in twin.states)
    np.testing.assert_allclose(twin.drift.mean(1), 0, atol=1e-12)
    np.testing.assert_allclose(twin.drift.std(1), 1, atol=1e-12)
    again = x.mean_field_path(
        size, 11, 21, 22, share=share, repulsion=repulsion, anchor=anchor, steps=steps
    )
    assert np.array_equal(again.states, twin.states)
    other = x.mean_field_path(
        size, 11, 21, 23, share=share, repulsion=repulsion, anchor=anchor, steps=steps
    )
    assert not np.array_equal(other.drift, twin.drift)


def test_twin_drift_is_the_declared_mean_field_draw() -> None:
    size, share, anchor, repulsion = 60, 0.3, 0.5, 0.25
    twin = x.mean_field_path(
        size, 3, 31, 32, share=share, repulsion=repulsion, anchor=anchor, steps=2
    )
    state_rng, xi = np.random.default_rng(31), np.random.default_rng(32)
    initial = fast_ranks(state_rng.normal(size=size))
    for k, drift in enumerate(twin.drift):
        before, noise = twin.states[k], state_rng.normal(size=size)
        mean, variance = x.mean_field_moments(before, repulsion)
        raw = mean + xi.normal(size=size) * np.sqrt(variance / 8)
        assert np.array_equal(drift, (raw - raw.mean()) / raw.std())
        innovation = np.sqrt(share) * drift + np.sqrt(1 - share) * noise
        update = 0.85 * before + np.sqrt(1 - 0.85**2) * innovation
        expected = fast_ranks((1 - anchor) * update + anchor * initial)
        assert np.array_equal(twin.states[k + 1], expected)


@dataclass(frozen=True)
class ExploratoryPlan(SeedPlan):
    """Frozen PanelSource driven by exploratory seeds, so no v4 stream is used."""

    def seed(self, phase: str, role: str, index: int, *, attempt: int = 0) -> int:
        return x.derive_seed("x1a", self.block, phase, role, index)


@pytest.mark.parametrize("phase", ["train", "reference"])
@pytest.mark.parametrize("share,reliability", [(0.001, 0.5), (0.9, 0.9)])
def test_arm_profiles_reproduce_panel_source_bitwise(
    share: float, reliability: float, phase: str
) -> None:
    block = detection_v4.RELIABILITIES.index(reliability)
    source = PanelSource(
        Cell(share, reliability), ExploratoryPlan(block=block), size=60
    )
    expected = source.profiles(phase, 5, start=3)

    def seed(role: str, index: int) -> int:
        return x.derive_seed("x1a", block, phase, role, index)

    actual = x.arm_profiles(share, reliability, 5, seed, twin=False, size=60, start=3)
    assert np.array_equal(actual, expected)


def test_arms_use_the_frozen_index_layout_and_their_own_streams() -> None:
    used: list[tuple[str, int]] = []

    def seed(role: str, index: int) -> int:
        used.append((role, index))
        return x.derive_seed("x1a", 0, "train", role, index)

    x.arm_profiles(0.3, 0.5, 4, seed, twin=False, size=60)
    arm = list(used)
    used.clear()
    x.arm_profiles(0.3, 0.5, 4, seed, twin=True, size=60)
    assert [i for r, i in arm if r == "state"] == [1, 3, 5, 7]
    assert [i for r, i in arm if r == "network"] == [0, 0, 1, 1]
    assert [i for r, i in used if r == "state"] == [0, 2, 4, 6]
    assert [i for r, i in used if r == "xi"] == [0, 2, 4, 6]
    assert {r for r, _ in used} == {"state", "xi", "mask", "error"}


def test_network_bootstrap_matches_frozen_resampling() -> None:
    rng = np.random.default_rng(8)
    twin, arm = rng.normal(size=(50, 2)), rng.normal(0.4, 1, size=(50, 2))
    draws = x.network_bootstrap(twin, arm, seed=99, resamples=300)
    frozen = score_uncertainty(
        twin[..., None], arm[..., None], np.zeros((300, 1)), seed=99, draws=300
    )
    assert frozen.se[0] == pytest.approx(draws.std(ddof=1), rel=1e-12)
    np.testing.assert_allclose(
        frozen.replicates[:, 0] - frozen.point[0], draws - draws.mean(), atol=1e-12
    )


KNOTS = np.array([-1.6, -0.6, 0.0, 0.6, 1.6])


def _residual(design: np.ndarray, target: np.ndarray) -> float:
    fitted = design @ np.linalg.lstsq(design, target, rcond=None)[0]
    return float(np.max(np.abs(target - fitted)))


def test_natural_spline_is_linear_beyond_and_cubic_between_knots() -> None:
    for lo, hi, degree in [(-4, KNOTS[0], 1), (KNOTS[-1], 4, 1)] + [
        (KNOTS[k], KNOTS[k + 1], 3) for k in range(len(KNOTS) - 1)
    ]:
        points = np.linspace(lo, hi, 25)
        basis = x.natural_cubic_basis(points, KNOTS)
        powers = np.vander(points, degree + 1)
        assert all(_residual(powers, column) < 1e-10 for column in basis.T)
    below = np.linspace(-4, KNOTS[-1] - 0.01, 50)
    powers = np.vander(below, 2)
    assert _residual(powers, x.natural_cubic_basis(below, KNOTS)[:, 2]) > 1e-3


def test_natural_spline_spans_exactly_the_natural_cubic_splines() -> None:
    points = np.linspace(-4, 4, 401)
    basis = x.natural_cubic_basis(points, KNOTS)
    assert np.linalg.matrix_rank(basis) == len(KNOTS)
    # Truncated-power splines are natural iff sum(theta) = sum(theta * knot) = 0.
    constraints = np.vstack([np.ones_like(KNOTS), KNOTS])
    null = np.linalg.svd(constraints)[2][2:]
    theta = null.T @ np.random.default_rng(4).normal(size=len(null))
    spline = 0.7 - 1.3 * points + np.maximum(points[:, None] - KNOTS, 0) ** 3 @ theta
    assert _residual(basis, spline) < 1e-9
    assert _residual(basis, points**2) > 1e-2
    assert _residual(basis, points**3) > 1e-2
    inside = np.linspace(KNOTS[0], KNOTS[-1], 101)
    heights = np.array([0.3, -1.0, 0.5, 2.0, -0.4])
    coefficients = np.linalg.solve(x.natural_cubic_basis(KNOTS, KNOTS), heights)
    np.testing.assert_allclose(
        x.natural_cubic_basis(inside, KNOTS) @ coefficients,
        CubicSpline(KNOTS, heights, bc_type="natural")(inside),
        atol=1e-12,
    )


def test_r2_gain_separates_partial_and_incremental_shares() -> None:
    rng = np.random.default_rng(12)
    z, drift, noise = rng.normal(size=(3, 20000))
    base = np.column_stack([np.ones_like(z), z])
    exact = x.r2_gain(1 + 2 * z + drift, base, drift)
    assert exact["partial_r2"] == pytest.approx(1)
    mixed = x.r2_gain(z + drift + noise, base, drift)
    assert mixed["partial_r2"] == pytest.approx(0.5, abs=0.02)
    assert mixed["incremental_r2"] == pytest.approx(1 / 3, abs=0.02)
    assert mixed["partial_r2"] == pytest.approx(
        mixed["incremental_r2"] / (1 - mixed["r2_reduced"])
    )
    unrelated = x.r2_gain(z + noise, base, drift)
    assert unrelated["partial_r2"] < 1e-3


def test_x2_replicate_verifies_frozen_path_and_reports_both_statistics() -> None:
    sizes = x.X2Sizes(size=60, waves=11, replicates=2)
    conditions = x.x2_conditions()
    baseline = conditions.index((0.0, 0.25, 1))
    strong = conditions.index((0.9, 0.25, 24))
    low = x.x2_replicate(baseline * 2, sizes)
    high = x.x2_replicate(strong * 2 + 1, sizes)
    assert low["bitwise_equal_to_frozen_influence"] is True
    assert low["observations"] == 10 * 60 and high["observations"] == 240 * 60
    assert low["x2a"]["value"] < 0.05 < 0.3 < high["x2a"]["value"] <= 1
    assert 0 <= high["x2b"]["value"] <= 1
    assert len(high["x2b"]["knots"]) == 5
    assert low["seeds"] == x.x2_replicate(strong * 2, sizes)["seeds"]
    json.dumps(high, allow_nan=False)


def test_x1a_cell_shares_seeds_across_strengths_of_one_reliability() -> None:
    sizes = x.X1aSizes(size=60, train=6, networks=4, resamples=40)
    first, second = x.x1a_cell(0, sizes), x.x1a_cell(1, sizes)
    assert (first["cell"]["a"], first["cell"]["r"]) == (0.001, 0.5)
    assert (second["cell"]["a"], second["cell"]["r"]) == (0.003, 0.5)
    assert first["seeds"] == second["seeds"]
    assert first["seeds"]["train_count"] == 2 * 6 * 4
    lower, upper = first["interval_95"]
    assert 0 <= lower <= upper <= 1 and 0 <= first["auc"] <= 1
    assert first["excludes_half"] == (lower > 0.5 or upper < 0.5)
    assert len(first["lags"]["arm_minus_twin"]) == 5
    json.dumps(first, allow_nan=False)
    assert x.x1a_cell(0, sizes)["auc"] == first["auc"]


def test_sharded_runs_resume_and_aggregate(tmp_path: Path) -> None:
    sizes = x.X2Sizes(size=60, waves=11, replicates=2)
    analysis = x.x2_analysis(sizes)
    done = [x.run_shard(analysis, tmp_path, shard=k, shards=3) for k in range(3)]
    assert sorted(i for part in done for i in part) == list(range(analysis.total))
    assert all(i % 3 == k for k, part in enumerate(done) for i in part)
    assert x.run_shard(analysis, tmp_path, shard=0, shards=3) == []
    result = x.aggregate_x2(tmp_path, sizes)
    assert len(result["conditions"]) == 36
    assert result["bitwise_equal_to_frozen_influence"] is True
    row = result["conditions"][0]
    values = [r["x2a"]["value"] for r in row["replicates"]]
    assert row["x2a"]["sd"] == pytest.approx(np.std(values, ddof=1))
    with pytest.raises(ValueError, match="requested sizes"):
        x.aggregate_x2(tmp_path, x.X2Sizes(size=66, waves=11, replicates=2))
    with pytest.raises(ValueError, match="Missing x2 units"):
        x.aggregate_x2(tmp_path)
    with pytest.raises(ValueError, match="different sizes"):
        x.run_shard(x.x2_analysis(), tmp_path, shard=0, shards=360)


def test_x1a_cli_writes_resumable_cells_and_refuses_partial_aggregates(
    tmp_path: Path,
) -> None:
    arguments = ["x1a", "--out", str(tmp_path), "--only", "5", "--size", "60"]
    small = ["--train", "4", "--networks", "2", "--resamples", "10"]
    assert x.main([*arguments, *small]) == 0
    record = json.loads((tmp_path / "x1a" / "x1a-005.json").read_text())
    output = tmp_path / "aggregate.json"
    assert record["cell"]["index"] == 5
    assert record["provenance"]["code"]["frozen_sources_match_freeze"] is True
    with pytest.raises(ValueError, match="Missing x1a units"):
        x.main(["aggregate", "x1a", "--out", str(tmp_path), "--output", str(output)])
    assert not output.exists()


def test_imported_study_modules_are_all_frozen() -> None:
    tree = ast.parse(Path(x.__file__).read_text())
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module
        and node.module.startswith("ic_study")
    }
    paths = {"src/" + name.replace(".", "/") + ".py" for name in imported}
    assert paths == set(x.FROZEN_SOURCES)
    freeze = json.loads((STUDY / x.FREEZE).read_text())["code"]
    for path in paths:
        digest = hashlib.sha256((STUDY / path).read_bytes()).hexdigest()
        assert freeze[path] == digest


def test_exploratory_seeds_are_disjoint_from_frozen_plans(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No exploratory seed can coincide with a frozen v4 seed.

    Every seed in the study is the first eight bytes of SHA-256 over a
    '|'-joined material whose first field is a namespace. The test records
    the materials that frozen ``SeedPlan`` (calibration and gate plans) and
    ``ConfirmatorySeedPlan`` hash across their whole phase and role domain,
    and those that ``derive_seed`` hashes for X1a, X1b and X2. Frozen materials
    lead with an ``ic-detection-boundary-v4`` namespace; exploratory ones
    lead with ``v4-exploratory-x1-x2|20260928|``. No namespace contains '|',
    so the first fields differ and the two preimage sets are disjoint.
    Distinct preimages share a truncated 64-bit digest only by chance, with
    probability 2**-64 per pair; the concrete seeds are also intersected over
    a common index range. Unoffset 8-byte digests are all below 2**64, which
    the crosswalk test below relies on. Frozen seeds are computed here only
    for comparison and never reach a generator.
    """
    captured: list[bytes] = []
    original = hashlib.sha256

    def recording(data: bytes = b"", **options: Any) -> Any:
        captured.append(bytes(data))
        return original(data, **options)

    monkeypatch.setattr(hashlib, "sha256", recording)
    plans = [SeedPlan(block=b) for b in range(9)]
    plans += [
        SeedPlan(repetition=r, block=b, gate=True) for r in (0, 1) for b in (0, 1)
    ]
    plans += [ConfirmatorySeedPlan(block=b) for b in range(9)]
    phases = ["match", "validate", "train", "check", "reference"]
    phases += ["nuisance", "bootstrap", "stencil"]
    frozen_seeds = {
        plan.seed(phase, role, index, attempt=attempt)
        for plan in plans
        for phase in phases
        for role in sorted(detection_v4.ROLES)
        for index in range(48)
        for attempt in (0, 1)
    }
    frozen = set(captured)
    captured.clear()
    ours = {
        x.derive_seed(analysis, block, phase, role, index)
        for analysis, blocks in (
            ("x1a", range(9)),
            ("x1b", range(18)),
            ("x2", range(1)),
        )
        for block in blocks
        for phase in x.PHASES[analysis]
        for role in sorted(x.ROLES)
        for index in range(48)
    }
    exploratory = set(captured)
    monkeypatch.undo()
    assert {
        m.split(b"|")[0].startswith(b"ic-detection-boundary-v4") for m in frozen
    } == {True}
    prefix = f"{x.NAMESPACE}|{x.ROOT}|".encode()
    assert all(m.startswith(prefix) for m in exploratory)
    assert x.NAMESPACE.encode() not in {m.split(b"|")[0] for m in frozen}
    assert "|" not in x.NAMESPACE
    assert frozen.isdisjoint(exploratory)
    assert frozen_seeds.isdisjoint(ours)
    assert len(ours) == len(exploratory)
    assert max(ours | frozen_seeds) < 2**64


def test_exploratory_seeds_are_disjoint_from_shp_crosswalk() -> None:
    """``shp-crosswalk-v1`` shares the root 20260928 but not the seed range.

    Its derivation (``research/shp-anchor-successor-1``, commit ``c4d683da``,
    also on ``integration/ic-20260928``) leads the material with its own
    namespace and adds 2**64 to the 8-byte digest, so its seeds lie in
    [2**64, 2**65) while every exploratory seed is an unoffset digest below
    2**64. The module is absent from this branch, so this test runs where the
    two meet: it enumerates the crosswalk's seeds for every reliability,
    replicate and role and checks the range and the disjointness directly.
    """
    crosswalk = pytest.importorskip("ic_study.analysis.shp_crosswalk")
    theirs = {
        crosswalk.crosswalk_seed(crosswalk.SEED_ROOT, block, replicate, role)
        for block in range(len(detection_v4.RELIABILITIES))
        for replicate in range(crosswalk.REPLICATES)
        for role in crosswalk.ROLES
    }
    ours = {
        x.derive_seed(analysis, block, phase, role, index)
        for analysis, blocks in (
            ("x1a", range(9)),
            ("x1b", range(18)),
            ("x2", range(1)),
        )
        for block in blocks
        for phase in x.PHASES[analysis]
        for role in sorted(x.ROLES)
        for index in range(16)
    }
    assert crosswalk.NAMESPACE != x.NAMESPACE
    assert min(theirs) >= 2**64 and max(theirs) < 2**65
    assert max(ours) < 2**64 and theirs.isdisjoint(ours)
