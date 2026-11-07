"""X7 successor: the frozen pipeline generalized by a feature extractor."""

from __future__ import annotations

import ast
import hashlib
import json
from collections.abc import Iterator
from dataclasses import asdict
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ic_study.analysis.detection_boundary import lag_profile
from ic_study.analysis.detection_boundary_v4 import Uncertainty
from ic_study.models.detection_panel_v4 import null
from ic_study.simulation import v4_curve
from ic_study.simulation import v4_exploratory as x12
from ic_study.simulation import v4_exploratory_x1b as b
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation import v4_exploratory_x7 as x7
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    Cell,
    PanelSource,
    selected_features,
)
from ic_study.simulation.v4_store import SealedStore

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


def a_panel(size: int = 120) -> tuple[np.ndarray, np.ndarray]:
    latent = null(size, 11, 1, 2, family="B", phi=0.85, eta=0.2)
    return latent, x7.observed_channel(latent, 0.7, 5, 6)


def test_rich_features_follow_the_declared_definitions() -> None:
    latent, observed = a_panel()
    rich = x7.rich_features(latent, observed)
    assert rich.shape == (36,) and np.all(np.isfinite(rich))
    values = np.where(observed >= 0, observed, np.nan)
    assert same_bits(rich[:3], lag_profile(values)[2:5])
    for k, lag in enumerate(range(6, 11)):
        x, y = values[:-lag].ravel(), values[lag:].ravel()
        valid = np.isfinite(x) & np.isfinite(y)
        assert rich[3 + k] == np.corrcoef(x[valid], y[valid])[0, 1]
    mobility = selected_features(latent, observed, channel="observed", mobility=True)
    assert same_bits(rich[8:11], mobility[2:5])
    groups = {
        c: g
        for g, members in enumerate(((0, 1), (2, 3), (4, 5, 6), (7, 8), (9, 10)))
        for c in members
    }
    counts = np.zeros((5, 5))
    for person in range(observed.shape[1]):
        for wave in range(10):
            before, after = observed[wave, person], observed[wave + 1, person]
            if before >= 0 and after >= 0:
                counts[groups[before], groups[after]] += 1
    frequencies = counts / counts.sum(1, keepdims=True)
    np.testing.assert_allclose(
        rich[11:31], frequencies[:, :4].ravel(), rtol=0, atol=1e-15
    )
    spreads = [
        np.std(observed[observed[:, person] >= 0, person])
        for person in range(observed.shape[1])
        if (observed[:, person] >= 0).sum() >= 6
    ]
    np.testing.assert_allclose(
        rich[31:], np.quantile(spreads, [0.1, 0.25, 0.5, 0.75, 0.9]), rtol=0, atol=1e-12
    )


def test_rich_features_keep_non_finite_values_for_the_gap_rule() -> None:
    latent, observed = a_panel()
    squeezed = np.where(observed >= 0, observed % 2, -1)
    rich = x7.rich_features(latent, squeezed)
    assert rich.shape == (36,) and not np.all(np.isfinite(rich[11:31]))


@pytest.mark.parametrize("attempt", [0, 1])
@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("share,reliability", [(0.0, 0.9), (0.03, 0.5), (0.9, 0.9)])
def test_feature_source_reproduces_panel_source_bitwise(
    share: float, reliability: float, phase: str, attempt: int
) -> None:
    cell = Cell(share, reliability)
    plan = f.SuccessorSeedPlan(block=RELIABILITIES.index(reliability), analysis="x7")
    frozen = PanelSource(cell, plan, size=TINY)
    successor = x7.FeatureSource(cell, plan, size=TINY)
    for parameters in (None, np.array([0.8, 0.3])):
        expected = frozen.profiles(
            phase, 3, parameters=parameters, attempt=attempt, start=1
        )
        actual = successor.profiles(
            phase, 3, parameters=parameters, attempt=attempt, start=1
        )
        assert same_bits(actual, expected)
    assert successor.panels == frozen.panels == 6


def test_feature_source_draws_each_panel_once_for_both_feature_sets() -> None:
    cell = Cell(0.03, 0.7)
    plan = f.SuccessorSeedPlan(block=4, analysis="x7")
    root = f.require_sealed_location(f.SEALED_ROOT / "source")
    store, rich = SealedStore(root / "frozen"), SealedStore(root / "rich")
    source = x7.FeatureSource(cell, plan, size=TINY, store=store, rich=rich)
    reference = PanelSource(cell, plan, size=TINY)
    theta = np.array([0.8, 0.2])
    frozen_rows = source.profiles("train", 40, parameters=theta)
    assert same_bits(frozen_rows, reference.profiles("train", 40, parameters=theta))
    keys = [source.key("train", n, s, 0, theta) for n, s in ((32, 0), (8, 32))]
    assert all((rich.root / f"{key}.npy").exists() for key in keys)
    drawn = source.panels
    rich_rows = source.rich_profiles("train", 40, parameters=theta)
    assert source.panels == drawn and rich_rows.shape == (40, 36)
    latent, observed = source.panel("train", 33, theta, 0)
    assert same_bits(rich_rows[33], x7.rich_features(latent, observed))
    assert same_bits(frozen_rows[33], x7.frozen_profile(latent, observed))
    source.profiles("match", 5, parameters=theta, attempt=1)
    assert not (rich.root / f"{source.key('match', 5, 0, 1, theta)}.npy").exists()
    drawn = source.panels
    matching = source.rich_profiles("match", 5, parameters=theta, attempt=1)
    assert source.panels == drawn + 5 and matching.shape == (5, 36)
    with pytest.raises(ValueError, match="successor seeds only"):
        x7.FeatureSource(cell, b.ExploratorySeedPlan(block=4))


def test_frozen_extractor_reproduces_the_frozen_cell_and_a_rich_run_keeps_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The declared precondition on a tiny interior cell, (0.03, 0.5) with X7
    streams at N = 60, then the X7 cell itself: its frozen-feature store is
    the frozen store except for the unit provenance and the seal, and the
    same panels filled the rich store. At N = 60 the longest lags can lack
    pairs, so this plumbing check zero-fills undefined features; the gap rule
    has its own test."""
    monkeypatch.setattr(v4_curve, "PanelSource", partial(PanelSource, size=TINY))
    rich_features = x7.rich_features
    monkeypatch.setattr(
        x7, "rich_features", lambda *panel: np.nan_to_num(rich_features(*panel))
    )
    out = f.require_sealed_location(f.SEALED_ROOT / "x7")
    spec = x7.PRECONDITION
    position = x7.PRECONDITION_CELLS.index((0.03, 0.5))
    runs = [f.precondition_side(spec, out, position, s, size=TINY) for s in f.SIDES]
    assert [run["error"] for run in runs] == [None, None]
    frozen_directory = spec.directory(out, "frozen", position)
    comparison = b.compare_cells(
        frozen_directory, spec.directory(out, "successor", position)
    )
    assert comparison["equal"], comparison["differing_files"]
    assert {"scores0.npy", "nuisance.npy", "eta-shifts.npy"} <= set(
        comparison["sha256"]
    )
    result = json.loads((frozen_directory / "result.json").read_text())
    assert result["success"] and result["attempts"][0]["status"] == "interior"
    unit, index = spec.cell(position)
    record = x7.x7_cell(
        x7.x7_cells().index((unit, index)), out, {"x7": "0" * 64}, x7.X7Sizes(TINY)
    )
    assert record["error"] is None and record["rich_error"] is None
    assert record["success"] is True and record["rich_success"] is True
    assert record["attempts"] == ["interior"] and all(record["seal_sha256"].values())
    run = out / "stores" / unit.key / f"a{index}"
    kept = b.compare_cells(frozen_directory, run)
    assert kept["differing_files"] == ["provenance.json", "seal.json"]
    assert kept["access_sequence_equal"]
    rich = out / "stores" / record["cell"]["rich_unit"] / f"a{index}"
    rich_result = json.loads((rich / "result.json").read_text())
    assert rich_result["success"] and rich_result["features"] == "rich-36"
    assert rich_result["attempts"] == result["attempts"]
    store = SealedStore(rich)
    scores = store.get_array("scores0")
    nuisance = store.get_array("nuisance")
    assert scores is not None and scores.shape == (2000, 2)
    assert nuisance is not None and nuisance.shape == (2000,)
    checkpoints = [p for p in rich.iterdir() if len(p.name) == 68]
    assert len(checkpoints) == 2 * 63 + 4 * 125 + 3 * 32


def test_non_finite_rich_features_make_a_recorded_rich_gap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(x7, "rich_features", lambda *_: np.full(36, np.nan))
    out = f.require_sealed_location(f.SEALED_ROOT / "gap")
    unit = x7.x7_units()[RELIABILITIES.index(0.9)]
    record = x7.x7_cell(
        x7.x7_cells().index((unit, 0)), out, {"x7": "0" * 64}, x7.X7Sizes(TINY)
    )
    assert record["success"] is True and record["attempts"] == ["anchor-exact"]
    assert record["rich_success"] is False and record["rich_error"] is None
    assert record["rich_gap"] == "non-finite rich feature in train"


def _curve(first: float | None, interval: list[float | None] | None) -> dict[str, Any]:
    return {"valid_null_gate": True, "first": first, "first_interval": interval}


def _deltas(values: dict[float, tuple[float, float]]) -> dict[float, dict[str, Any]]:
    return {a: {"interval": list(bounds)} for a, bounds in values.items()}


def test_x7_reading_follows_the_declared_rule() -> None:
    wide = _deltas({a: (-0.01, 0.01) for a in GRID})
    assert (
        x7.x7_reading(_curve(0.1, [0.03, 0.3]), _curve(0.01, [0.003, 0.03]), wide)
        == "far"
    )
    positive = _deltas({a: (0.01, 0.05) for a in GRID})
    assert (
        x7.x7_reading(_curve(0.1, [0.03, 0.3]), _curve(0.01, [0.003, 0.3]), positive)
        == "far"
    )
    assert x7.x7_reading(_curve(None, None), _curve(0.3, [0.1, 0.6]), wide) == "far"
    assert (
        x7.x7_reading(_curve(0.1, [0.03, 0.3]), _curve(0.1, [0.03, 0.3]), wide)
        == "close"
    )
    loose = _deltas({a: (-0.03, 0.01) for a in GRID})
    assert (
        x7.x7_reading(_curve(0.1, [0.03, 0.3]), _curve(0.1, [0.03, 0.3]), loose)
        == "inconclusive"
    )
    assert (
        x7.x7_reading(
            _curve(0.1, None), {**_curve(0.1, None), "valid_null_gate": False}, wide
        )
        == "invalid"
    )
    censored = {**_curve(None, None), "first_censoring": "gap at a=0.3"}
    assert x7.x7_reading(_curve(0.1, [0.03, 0.3]), censored, wide) == "censored"
    assert x7.x7_reading(None, _curve(0.1, None), wide) == "unavailable"


def _fake_cell(
    _unit: f.SuccessorUnit,
    index: int,
    directory: Path,
    *,
    rich_directory: Path | None = None,
    **_: Any,
) -> None:
    rng = np.random.default_rng(index)
    scores = rng.normal(size=(2000, 2)), rng.normal(0.3 * index, 1, size=(2000, 2))
    assert rich_directory is not None
    for target in (directory, rich_directory):
        SealedStore(target.parent)
        store = SealedStore(target)
        store.put_array("scores0", scores[0])
        store.put_array("scores1", scores[1])
        store.put_array("nuisance", np.zeros(2000))
        store.put_json(
            "result", {"success": True, "attempts": [{"status": "interior"}]}
        )
        store.seal()
    return None


def test_x7_aggregate_waits_for_the_release_and_pairs_both_curves(
    monkeypatch: pytest.MonkeyPatch,
    synthetic_analysis: Any,
) -> None:
    monkeypatch.setattr(x7, "execute_feature_cell", _fake_cell)
    monkeypatch.setattr(x7, "RESAMPLES", 20)
    points = np.linspace(0.5, 0.95, 9)
    monkeypatch.setattr(
        v4_curve,
        "score_uncertainty",
        lambda *_, **__: Uncertainty(
            points, np.full(9, 0.001), np.full(9, 0.001), np.tile(points, (2000, 1))
        ),
    )
    out = f.SEALED_ROOT / "aggregate"
    analysis = f.Analysis(
        "x7",
        81,
        asdict(x7.DECLARED_X7),
        lambda i: x7.x7_cell(i, f.require_sealed_location(out), {"x7": "0" * 64}),
        verification={"x7": "0" * 64},
    )
    f.run_shard(synthetic_analysis(out, analysis, x7.SUITE.preconditions), out)
    with pytest.raises(ValueError, match="Sealed until"):
        x7.aggregate_x7(out)
    f.private_directory(f.RELEASE_RECORD.parent)
    f.RELEASE_RECORD.write_text("{}")
    result = x7.aggregate_x7(out)
    assert [row["r"] for row in result["summary"]] == list(RELIABILITIES)
    assert {row["reading"] for row in result["summary"]} == {"close"}
    unit = result["units"][0]
    assert unit["x7"]["first"] == unit["rich"]["first"] == 0.03
    assert [d["delta"] for d in unit["delta_auc"]] == [0.0] * 9
    assert all(d["interval"] == [0.0, 0.0] for d in unit["delta_auc"])
    assert all(
        (out / "stores" / key / "curve.json").exists()
        for key in ("x7-t1-u00-r0", "x7-rich-t1-u00-r0")
    )
    assert (
        result["release"]["release_record_sha256"] == hashlib.sha256(b"{}").hexdigest()
    )
    json.dumps(result, allow_nan=False)


def test_plan_lists_every_precondition_job(capsys: pytest.CaptureFixture[str]) -> None:
    assert x7.main(["plan"]) == 0
    jobs = [line.split() for line in capsys.readouterr().out.splitlines()]
    assert jobs == [["x7", str(k), side] for k in range(4) for side in f.SIDES]
    cells = x7.x7_cells()
    assert (
        len(cells) == 81 and [u.key for u in x7.rich_units()][4] == "x7-rich-t1-u00-r4"
    )
    assert all(
        unit.seeds == rich.seeds
        for unit, rich in zip(x7.x7_units(), x7.rich_units(), strict=True)
    )


def test_x7_imports_only_frozen_and_successor_modules() -> None:
    tree = ast.parse(Path(x7.__file__).read_text())
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
    digests = f.successor_provenance(x7.SUITE.modules)["successor_sha256"]
    assert "src/ic_study/simulation/v4_exploratory_x7.py" in digests


def test_aggregate_rejects_a_substituted_sealed_store(
    monkeypatch: pytest.MonkeyPatch,
    synthetic_analysis: Any,
) -> None:
    monkeypatch.setattr(x7, "execute_feature_cell", _fake_cell)
    out = f.SEALED_ROOT / "substituted"
    analysis = f.Analysis(
        "x7", 81, asdict(x7.DECLARED_X7), lambda i: x7.x7_cell(i, out, {})
    )
    f.run_shard(
        synthetic_analysis(out, analysis, x7.SUITE.preconditions), out, only=[0]
    )
    directory = out / "stores" / x7.rich_units()[0].key / "a0"
    (directory / "seal.json").unlink()
    (directory / "scores0.npy").unlink()
    store = SealedStore(directory)
    store.put_array("scores0", np.zeros((2000, 2)))
    store.seal()
    with pytest.raises(ValueError, match="seal"):
        x7.aggregate_x7(out, now=v4_curve.CLOSE)


@pytest.mark.parametrize("crash_at", ["rich-seal", "frozen-seal"])
def test_rich_terminal_error_survives_interruption_and_resume(
    monkeypatch: pytest.MonkeyPatch,
    crash_at: str,
) -> None:
    from types import SimpleNamespace

    calls = []
    fit = SimpleNamespace(success=True)
    result = SimpleNamespace(
        scores0=np.zeros((2, 2)),
        scores1=np.ones((2, 2)),
        nuisance=[SimpleNamespace(centered=np.zeros(2), shifts=np.zeros((2, 2)))],
    )
    monkeypatch.setattr(x7, "fit_cell", lambda _: fit)
    monkeypatch.setattr(x7, "cell_record", lambda _: {"success": True, "attempts": []})

    def feature_pass(*args: Any) -> tuple[Any, None]:
        if args[2].rich:
            calls.append("rich")
            raise ValueError("original terminal failure")
        return result, None

    monkeypatch.setattr(x7, "feature_pass", feature_pass)
    original_seal = SealedStore.seal
    interrupted = False

    def seal(store: SealedStore) -> None:
        nonlocal interrupted
        rich = "x7-rich" in str(store.root)
        if not interrupted and rich == (crash_at == "rich-seal"):
            interrupted = True
            raise RuntimeError("interrupted")
        original_seal(store)

    monkeypatch.setattr(SealedStore, "seal", seal)
    out = f.require_sealed_location(f.SEALED_ROOT / crash_at)
    with pytest.raises(RuntimeError, match="interrupted"):
        x7.x7_cell(0, out, {}, x7.X7Sizes(TINY))
    record = x7.x7_cell(0, out, {}, x7.X7Sizes(TINY))
    assert record["rich_error"] == "ValueError('original terminal failure')"
    assert record["success"] is True and record["rich_success"] is None
    assert calls == ["rich"]
    assert all(record["seal_sha256"].values())


@pytest.mark.parametrize(
    "key",
    ["sustained_censoring", "sustained_interval_censoring", "first_interval_censoring"],
)
def test_first_crossing_rules_ignore_unrelated_censoring(key: str) -> None:
    frozen = {**_curve(0.1, [0.03, 0.3]), key: "gap at a=0.6"}
    rich = _curve(0.01, [0.003, 0.03])
    assert x7.x7_reading(frozen, rich, {}) == "far"
    if key.startswith("sustained"):
        rich[key] = "gap at a=0.6"
        assert x7.x7_reading(frozen, rich, {}) == "far"
    assert frozen[key] == "gap at a=0.6"


def test_delta_and_close_rules_do_not_require_boundary_intervals() -> None:
    frozen = _curve(0.1, None)
    rich = {**_curve(0.01, None), "first_interval_censoring": "gap at a=0.3"}
    positive = _deltas({a: (0.01, 0.05) for a in GRID})
    assert x7.x7_reading(frozen, rich, positive) == "far"
    rich["first"] = 0.1
    neutral = _deltas({a: (-0.01, 0.01) for a in GRID})
    assert x7.x7_reading(frozen, rich, neutral) == "close"
    rich["first_censoring"] = "gap at a=0.03"
    assert x7.x7_reading(frozen, rich, neutral) == "censored"


def test_interval_rule_uses_only_its_two_uncensored_quantities() -> None:
    frozen = _curve(0.1, None)
    rich = {**_curve(None, [0.003, 0.03]), "first_censoring": "gap at a=0.6"}
    assert x7.x7_reading(frozen, rich, {}) == "far"
    frozen["first_censoring"] = "gap at a=0.03"
    assert x7.x7_reading(frozen, rich, {}) == "censored"
