"""X5 successor: the frozen pipeline against a misspecified observed channel."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from collections.abc import Iterator
from datetime import timedelta
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ic_study.models.anchored_panel import panel_mask
from ic_study.models.detection_panel import tenure_reliability
from ic_study.simulation import v4_curve
from ic_study.simulation import v4_exploratory as x12
from ic_study.simulation import v4_exploratory_x1b as b
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation import v4_exploratory_x5 as x5
from ic_study.simulation.amendment_a import fast_ranks
from ic_study.simulation.detection_v4 import RELIABILITIES, Cell, PanelSource

STUDY = Path(__file__).resolve().parents[2]
PHASES = ("match", "validate", "train", "check", "reference")
TINY = 60


def same_bits(left: np.ndarray, right: np.ndarray) -> bool:
    return (
        left.dtype == right.dtype
        and left.shape == right.shape
        and left.tobytes() == right.tobytes()
    )


@pytest.fixture(autouse=True)
def sealed_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    root = tmp_path / "sealed"
    monkeypatch.setattr(f, "SEALED_ROOT", root)
    monkeypatch.setattr(f, "RELEASE_RECORD", tmp_path / "release" / "record.json")
    yield root


def latent_panel(size: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.stack([fast_ranks(rng.normal(size=size)) for _ in range(11)])


@pytest.mark.parametrize("size", [60, 120])
@pytest.mark.parametrize("seed", [0, 7, 2**63 + 11])
def test_attrition_without_beta_is_the_frozen_mask(size: int, seed: int) -> None:
    mask = x5.attrition_mask(latent_panel(size, seed % 97), seed, beta=0.0)
    assert same_bits(mask, panel_mask(size, 11, seed, retention=0.89))


def test_attrition_keeps_the_frozen_uniforms_and_calibrates_retention() -> None:
    size, seed, beta = 600, 12345, math.log(2)
    latent = latent_panel(size, 3)
    mask = x5.attrition_mask(latent, seed, beta=beta)
    rng = np.random.default_rng(seed)
    households = size // 2
    entry = np.where(np.arange(households) < size // 3, 0, 5)
    active = np.zeros(households, dtype=bool)
    for wave in range(11):
        uniforms = rng.random(households)
        if wave:
            pairs = latent[wave - 1].reshape(households, 2).mean(1)
            p = x5.retention_probabilities(pairs, active, beta)
            assert abs(p[active].mean() - 0.89) < 1e-12
            assert np.all(np.diff(p[np.argsort(pairs)]) >= 0)
            active &= uniforms < p
        active |= entry == wave
        assert np.array_equal(mask[wave], np.repeat(active, 2))
    frozen = panel_mask(size, 11, seed, retention=0.89)
    assert not np.array_equal(mask, frozen)
    late = 2 * size // 3
    assert np.array_equal(mask[0], frozen[0]) and not mask[:5, late:].any()
    assert np.all(mask[5, late:]) and np.all(frozen[5, late:])


def test_declared_attrition_arithmetic() -> None:
    """With normal zbar of SD 0.71: about 15% against 7.5% annual dropout in the
    bottom and top household quintiles at ln 1.5, 18.5% against 5.5% at ln 2."""
    zbar = np.random.default_rng(1).normal(scale=0.71, size=400_000)
    active = np.ones(len(zbar), dtype=bool)
    bottom, top = zbar <= np.quantile(zbar, 0.2), zbar >= np.quantile(zbar, 0.8)
    for beta, expected in (
        (math.log(1.5), (0.15, 0.075)),
        (math.log(2), (0.185, 0.055)),
    ):
        p = x5.retention_probabilities(zbar, active, beta)
        assert abs(p.mean() - 0.89) < 1e-12
        assert 1 - p[bottom].mean() == pytest.approx(expected[0], abs=0.004)
        assert 1 - p[top].mean() == pytest.approx(expected[1], abs=0.004)


def test_channel_reliabilities_follow_the_declared_rules() -> None:
    mask = panel_mask(TINY, 11, 3, retention=0.89)
    waves = np.arange(11)
    neutral = x5.wave_reliability(mask, 0.7, x5.NEUTRAL)
    assert neutral.dtype == np.float64 and np.all(neutral == 0.7)
    trend = x5.wave_reliability(mask, 0.7, x5.CONDITIONS[1])
    np.testing.assert_allclose(trend[:, 0], 0.7 + 0.08 * (waves - 5) / 5, atol=1e-15)
    np.testing.assert_allclose(trend.mean(0), 0.7, atol=1e-15)
    step = x5.wave_reliability(mask, 0.7, x5.CONDITIONS[3])
    assert np.all(step[:5] == 0.7 - 0.08) and np.all(step[5:] == 0.7 + 0.08)
    tenure = x5.wave_reliability(mask, 0.7, x5.CONDITIONS[5])
    assert same_bits(tenure, tenure_reliability(mask, 0.7, 0.2))
    assert [c.name for c in x5.CONDITIONS] == [
        "trend-003",
        "trend-008",
        "step-003",
        "step-008",
        "tenure-010",
        "tenure-020",
        "mnar-ln15",
        "mnar-ln2",
    ]


@pytest.mark.parametrize("attempt", [0, 1])
@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("share,reliability", [(0.0, 0.5), (0.03, 0.5), (0.9, 0.9)])
def test_neutral_channel_reproduces_the_frozen_source_bitwise(
    share: float, reliability: float, phase: str, attempt: int
) -> None:
    cell = Cell(share, reliability)
    plan = f.SuccessorSeedPlan(block=RELIABILITIES.index(reliability), analysis="x5")
    frozen = PanelSource(cell, plan, size=TINY)
    successor = f.SuccessorSource(
        cell, plan, social=x5.misspecified_social(x5.NEUTRAL), size=TINY
    )
    for parameters in (None, np.array([0.8, 0.3])):
        expected = frozen.profiles(
            phase, 3, parameters=parameters, attempt=attempt, start=1
        )
        actual = successor.profiles(
            phase, 3, parameters=parameters, attempt=attempt, start=1
        )
        assert same_bits(actual, expected)


@pytest.mark.parametrize("channel", x5.CONDITIONS, ids=lambda c: c.name)
def test_departures_change_only_the_data_arm(channel: x5.Channel) -> None:
    cell = Cell(0.0, 0.7)
    plan = f.SuccessorSeedPlan(block=4, analysis="x5")
    frozen = PanelSource(cell, plan, size=TINY)
    successor = f.SuccessorSource(
        cell, plan, social=x5.misspecified_social(channel), size=TINY
    )
    null = np.array([0.85, 0.2])
    assert same_bits(
        successor.profiles("check", 4, parameters=null),
        frozen.profiles("check", 4, parameters=null),
    )
    data = successor.profiles("check", 4)
    assert not np.array_equal(data, frozen.profiles("check", 4))
    if channel.tenure:
        tier4 = PanelSource(Cell(0.0, 0.7, gain=channel.tenure), plan, size=TINY)
        assert same_bits(data, tier4.profiles("check", 4))


def test_cells_share_streams_across_the_conditions_of_one_r() -> None:
    cells = x5.x5_cells()
    assert len(cells) == 72
    assert [channel for _, channel in cells[:8]] == list(x5.CONDITIONS)
    for index, (unit, channel) in enumerate(cells):
        assert unit.cells[0] == Cell(0.0, RELIABILITIES[index // 8])
        assert unit.seeds == f.SuccessorSeedPlan(block=index // 8, analysis="x5")
        assert channel == x5.CONDITIONS[index % 8]
    for position, (share, reliability) in enumerate(x5.PRECONDITION_CELLS):
        unit, strength = x5.PRECONDITION.cell(position)
        assert unit.cells[strength] == Cell(share, reliability)


def test_neutral_executor_reproduces_the_frozen_cell_bitwise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The declared precondition on a tiny panel: (0, 0.5) takes the
    anchor-exact branch and (0.03, 0.5) fits at N = 60 with X5 streams, so the
    interior fit, validation, stencil, reference and nuisance are compared."""
    monkeypatch.setattr(v4_curve, "PanelSource", partial(PanelSource, size=TINY))
    out = f.require_sealed_location(f.SEALED_ROOT / "precondition")
    spec = x5.PRECONDITION
    for position, status in ((0, "anchor-exact"), (2, "interior")):
        runs = [f.precondition_side(spec, out, position, s, size=TINY) for s in f.SIDES]
        assert [run["error"] for run in runs] == [None, None]
        comparison = b.compare_cells(
            spec.directory(out, "frozen", position),
            spec.directory(out, "successor", position),
        )
        assert comparison["equal"], comparison["differing_files"]
        result = json.loads(
            (spec.directory(out, "frozen", position) / "result.json").read_text()
        )
        assert result["success"] and result["attempts"][0]["status"] == status
    assert "nuisance.npy" in comparison["sha256"] and comparison["checkpoints"] > 1000


def test_x5_cell_records_the_estimate_and_resumes_from_its_store() -> None:
    out = f.require_sealed_location(f.SEALED_ROOT / "cells")
    index = 8 * RELIABILITIES.index(0.7) + 1
    sizes = x5.X5Sizes(TINY)
    record = x5.x5_cell(index, out, {"x5": "0" * 64}, sizes)
    assert record["error"] is None and record["success"] is True
    assert record["cell"]["channel"]["name"] == "trend-008"
    assert record["attempts"] == ["interior"] and record["seal_sha256"]
    estimate = record["estimate"]
    lower, upper = estimate["interval_95"]
    floor = estimate["interval_27729"]
    assert floor[0] <= lower <= estimate["auc"] <= upper <= floor[1]
    assert estimate["se"] >= estimate["score_se"] > 0
    assert len(estimate["lags"]["data_mean"]) == len(estimate["lags"]["null_mean"]) == 5
    again = x5.x5_cell(index, out, {"x5": "0" * 64}, sizes)
    assert (
        again["estimate"] == estimate and again["seal_sha256"] == record["seal_sha256"]
    )
    json.dumps(record, allow_nan=False)


def _record(index: int, **changes: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "cell": x5.cell_identity(index),
        "sizes": {"size": x12.SIZE},
        "verification_sha256": {"x5": "0" * 64},
        "error": None,
        "success": True,
        "attempts": ["interior"],
        "fit": {"parameters": [0.8, 0.1]},
        "estimate": {
            "auc": 0.6,
            "interval_95": [0.55, 0.65],
            "interval_27729": [0.5, 0.7],
        },
        "timing": {
            "started_utc": x12.utc_now(),
            "finished_utc": x12.utc_now(),
            "wall_seconds": 1.0,
            "cpu_seconds": 1.0,
        },
    }
    record.update(changes)
    return record


def test_aggregate_applies_the_declared_reading(synthetic_analysis: Any) -> None:
    cases: dict[int, dict[str, Any]] = {
        0: {"estimate": {"interval_95": [0.72, 0.8], "interval_27729": [0.7, 0.82]}},
        1: {"estimate": {"interval_95": [0.65, 0.75], "interval_27729": [0.6, 0.8]}},
        2: {"estimate": {"interval_95": [0.5, 0.58], "interval_27729": [0.48, 0.6]}},
        3: {},
        4: {"success": False, "estimate": None, "attempts": ["family-limit-upper"]},
        5: {"error": "ValueError('ill-conditioned local profile')", "success": None},
    }
    out = f.SEALED_ROOT / "aggregate"
    analysis = f.Analysis(
        "x5",
        72,
        {"size": x12.SIZE},
        lambda index: _record(index, **cases[index]),
        verification={"x5": "0" * 64},
    )
    f.run_shard(
        synthetic_analysis(out, analysis, x5.SUITE.preconditions), out, only=list(cases)
    )
    with pytest.raises(ValueError, match="Missing x5 units"):
        x5.aggregate_x5(out)
    result = x5.aggregate_x5(out, now=f.WINDOW_CLOSE + timedelta(seconds=1))
    readings = [row["reading"] for row in result["cells"]]
    assert readings == [
        "crosses-primary",
        "crosses-secondary",
        "below-targets",
        "intermediate",
        "fit-failure",
        "error",
    ]
    assert result["summary"]["null_gate_would_invalidate"] == [
        ["trend-003", 0.5],
        ["trend-008", 0.5],
    ]
    assert result["summary"]["incomplete"] == list(range(6, 72))
    assert result["cells"][4]["statement"] == x5.FIT_FAILURE
    json.dumps(result, allow_nan=False)


def test_plan_lists_every_precondition_job(capsys: pytest.CaptureFixture[str]) -> None:
    assert x5.main(["plan"]) == 0
    jobs = [line.split() for line in capsys.readouterr().out.splitlines()]
    assert jobs == [["x5", str(k), side] for k in range(4) for side in f.SIDES]


def test_x5_imports_only_frozen_and_successor_modules() -> None:
    tree = ast.parse(Path(x5.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if not node.module.startswith("ic_study"):
                continue
            if (STUDY / "src" / node.module.replace(".", "/")).is_dir():
                imported |= {f"{node.module}.{alias.name}" for alias in node.names}
            else:
                imported.add(node.module)
    successors = {
        "ic_study.simulation.v4_exploratory",
        "ic_study.simulation.v4_exploratory_x1b",
        "ic_study.simulation.v4_exploratory_x3x7",
    }
    freeze = json.loads((STUDY / x12.FREEZE).read_text())["code"]
    for name in imported - successors:
        path = "src/" + name.replace(".", "/") + ".py"
        assert freeze[path] == hashlib.sha256((STUDY / path).read_bytes()).hexdigest()
    digests = f.successor_provenance(x5.SUITE.modules)["successor_sha256"]
    assert "src/ic_study/simulation/v4_exploratory_x5.py" in digests
