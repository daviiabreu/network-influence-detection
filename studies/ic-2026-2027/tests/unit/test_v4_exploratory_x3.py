"""X3 successor: null B with a free signal share, its fit and its preconditions."""

from __future__ import annotations

import ast
import hashlib
import json
from collections.abc import Callable, Iterator
from dataclasses import asdict, replace
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import (
    ProfileFit,
    Validation,
    validate_fit,
)
from ic_study.simulation import v4_curve
from ic_study.simulation import v4_exploratory as x12
from ic_study.simulation import v4_exploratory_x1b as b
from ic_study.simulation import v4_exploratory_x3 as x3
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    Cell,
    FitAttempt,
    PanelSource,
    SeedPlan,
    ValidatedFit,
)
from ic_study.simulation.v4_store import SealedStore

STUDY = Path(__file__).resolve().parents[2]
PHASES = ("match", "validate", "train", "check", "reference")
TINY = 60
SMALL = x3.X3Sizes(
    size=TINY, matching=64, retry_matching=128, train=40, check=80, resamples=50
)


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


def _plan(reliability: float) -> f.SuccessorSeedPlan:
    return f.SuccessorSeedPlan(block=RELIABILITIES.index(reliability), analysis="x3")


@pytest.mark.parametrize("attempt", [0, 1])
@pytest.mark.parametrize("phase", PHASES)
def test_source_at_the_cell_share_is_the_frozen_source(
    phase: str, attempt: int
) -> None:
    cell = Cell(0.03, 0.5)
    frozen = PanelSource(cell, _plan(0.5), size=TINY)
    neutral = x3.SignalShareSource(cell, _plan(0.5), signal=0.5, size=TINY)
    for parameters in (None, np.array([0.8, 0.3])):
        expected = frozen.profiles(
            phase, 3, parameters=parameters, attempt=attempt, start=2
        )
        actual = neutral.profiles(
            phase, 3, parameters=parameters, attempt=attempt, start=2
        )
        assert same_bits(actual, expected)
    assert neutral.panels == frozen.panels == 6


def test_free_share_moves_only_the_null_channel() -> None:
    cell = Cell(0.3, 0.6)
    plan = _plan(0.6)
    free = x3.SignalShareSource(cell, plan, signal=0.8, size=TINY)
    null = np.array([0.7, 0.2])
    for phase in ("match", "check"):
        assert same_bits(
            free.profiles(phase, 3, parameters=null, attempt=1),
            PanelSource(replace(cell, reliability=0.8), plan, size=TINY).profiles(
                phase, 3, parameters=null, attempt=1
            ),
        )
        assert same_bits(
            free.profiles(phase, 3, attempt=1),
            PanelSource(cell, plan, size=TINY).profiles(phase, 3, attempt=1),
        )
    assert not np.array_equal(
        free.profiles("match", 3, parameters=null),
        PanelSource(cell, plan, size=TINY).profiles("match", 3, parameters=null),
    )
    with pytest.raises(ValueError, match="successor seeds only"):
        x3.SignalShareSource(cell, SeedPlan(), signal=0.8)


def test_neutral_source_writes_the_frozen_checkpoints_and_keys_carry_the_share(
    tmp_path: Path,
) -> None:
    cell = Cell(0.03, 0.5)
    calls = (
        ("match", 40, None, 0),
        ("match", 40, [0.85, 0.1], 0),
        ("validate", 8, None, 1),
        ("validate", 8, [0.8, 0.3], 1),
        ("train", 6, None, 0),
        ("check", 6, [0.9, 0.0], 0),
        ("reference", 6, None, 0),
    )
    makers: dict[str, Callable[[SealedStore], PanelSource]] = {
        "frozen": lambda store: PanelSource(cell, _plan(0.5), size=TINY, store=store),
        "successor": lambda store: x3.SignalShareSource(
            cell, _plan(0.5), signal=0.5, size=TINY, store=store
        ),
    }
    for side, make in makers.items():
        store = SealedStore(tmp_path / side)
        source = make(store)
        for phase, count, parameters, attempt in calls:
            source.profiles(
                phase,
                count,
                parameters=None if parameters is None else np.array(parameters),
                attempt=attempt,
            )
        store.seal()
    comparison = b.compare_cells(tmp_path / "frozen", tmp_path / "successor")
    assert comparison["equal"], comparison["differing_files"]
    assert comparison["checkpoints"] == 9
    shared = SealedStore(tmp_path / "shared")
    for signal in (0.5, 0.51, 0.5):
        x3.SignalShareSource(
            cell, _plan(0.5), signal=signal, size=TINY, store=shared
        ).profiles("match", 4, parameters=np.array([0.85, 0.1]))
    assert len(list(shared.root.glob("*.npy"))) == 2


def test_store_precondition_reproduces_the_frozen_cell_bitwise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Declared x3-store rule on a tiny panel through the shared harness, at the
    anchor-exact cell (0, 0.9): X3's source at r_B = r inside frozen pipeline."""
    monkeypatch.setattr(v4_curve, "PanelSource", partial(PanelSource, size=TINY))
    spec = replace(x3.STORE, cells=((0.0, 0.9),))
    out = f.require_sealed_location(f.SEALED_ROOT / "store")
    records = [f.precondition_side(spec, out, 0, side, size=TINY) for side in f.SIDES]
    assert [record["error"] for record in records] == [None, None]
    cell = f.verify(spec, out, size=TINY)["cells"][0]
    assert cell["equal"], cell["differing_files"]
    assert cell["attempts"] == ["anchor-exact"] and cell["success"] is True
    assert {"result.json", "scores0.npy", "eta-shifts.npy", "phases.jsonl"} <= set(
        cell["sha256"]
    )


def test_fit_precondition_first_outer_evaluation_is_the_first_frozen_fit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Declared x3-fit rule on a tiny panel: the free fit's first outer
    evaluation, at r_B = r, and frozen fit_cell's first attempt write the same
    record store byte for byte. No material hashed on the way leads with a
    frozen v4 namespace."""
    captured: list[bytes] = []
    original = hashlib.sha256

    def recording(data: bytes = b"", **options: Any) -> Any:
        captured.append(bytes(data))
        return original(data, **options)

    spec = replace(x3.FIT, cells=((0.03, 0.5),))
    out = f.require_sealed_location(f.SEALED_ROOT / "fit")
    monkeypatch.setattr(hashlib, "sha256", recording)
    records = [f.precondition_side(spec, out, 0, side, size=TINY) for side in f.SIDES]
    monkeypatch.undo()
    assert [record["error"] for record in records] == [None, None]
    cell = f.verify(spec, out, size=TINY)["cells"][0]
    assert cell["equal"], cell["differing_files"]
    assert cell["attempts"] == ["interior"] and cell["result"]
    assert set(cell["sha256"]) == {
        "differences.npy",
        "parameters.npy",
        "residual.npy",
        "se.npy",
        "tolerance.npy",
        "result.json",
        "seal.json",
    }
    seeds = [m for m in captured if m.startswith(f.NAMESPACE.encode())]
    assert seeds and all(
        m.startswith(f"{f.NAMESPACE}|{f.ROOT}|x3|".encode()) for m in seeds
    )
    assert not any(m.startswith(b"ic-detection-boundary-v4") for m in captured)


def _fit(
    status: str = "interior", parameters: tuple[float, float] = (0.8, 0.1)
) -> ProfileFit:
    return ProfileFit(
        np.array(parameters),
        np.zeros((4, 2)),
        np.zeros(2),
        np.full(2, 1e-3),
        np.full(2, 1e-4),
        7,
        status,
        2,
    )


def _points(
    residual: Callable[[float], float],
    tolerance: float = 1e-4,
    failing: Callable[[float], bool] = lambda _: False,
) -> tuple[Callable[[float], x3.OuterPoint], list[float]]:
    seen: list[float] = []

    def evaluate(signal: float) -> x3.OuterPoint:
        seen.append(signal)
        if failing(signal):
            return x3.OuterPoint(signal, _fit("no-L1-root"), np.nan, np.nan, np.nan)
        return x3.OuterPoint(signal, _fit(), residual(signal), 1e-3, tolerance)

    return evaluate, seen


def test_outer_solver_secant_reaches_roots_from_the_cell_share() -> None:
    evaluate, seen = _points(lambda s: 2 * (s - 0.75))
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "interior" and seen[:2] == [0.7, pytest.approx(0.71)]
    assert len(points) == 3 and abs(points[-1].signal - 0.75) < 1e-9
    evaluate, seen = _points(lambda s: 0.6 - s)
    assert x3.solve_signal(evaluate, 0.7, 0.3, budget=12)[0] == "interior"
    evaluate, seen = _points(lambda s: 0.0)
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "interior" and seen == [0.7]
    evaluate, seen = _points(lambda s: s - 0.9985)
    assert x3.solve_signal(evaluate, 0.995, 0.3, budget=12)[0] == "interior"
    assert seen[1] == pytest.approx(0.985)


def test_outer_solver_illinois_straddle_stays_inside_the_bracket() -> None:
    evaluate, seen = _points(lambda s: float(np.expm1(10 * (s - 0.8))), 1e-3)
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "interior" and abs(points[-1].residual) <= 1e-3
    assert all(0.3 <= s <= x3.UPPER for s in seen) and len(seen) <= 12
    evaluate, seen = _points(
        lambda s: float(np.sign(s - 0.8) * abs(s - 0.8) ** 0.1), 1e-9
    )
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "budget" and len(points) == 12
    outside = [s for s in seen[3:] if not 0.7 < s < 1]
    assert not outside


def test_outer_solver_reports_family_limit_inner_failure_and_budget() -> None:
    evaluate, seen = _points(lambda s: s + 1)
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "budget" and len(seen) == 12 and 0.3 in seen
    evaluate, seen = _points(lambda s: s - 2)
    status, _ = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "budget" and x3.UPPER in seen
    evaluate, seen = _points(lambda s: 2 * (s - 0.75), failing=lambda s: s > 0.705)
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "inner-failure" and len(points) == 2
    assert points[-1].fit.status == "no-L1-root"
    evaluate, seen = _points(lambda s: 2 * (s - 0.75))
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=2)
    assert status == "budget" and len(points) == 2


def test_attempt_starts_at_the_cell_share_inside_the_continuous_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    starts: list[tuple[float, float]] = []

    def solve(
        evaluate: Callable[[float], x3.OuterPoint], start: float, lower: float, **_: Any
    ) -> tuple[str, tuple[x3.OuterPoint, ...]]:
        starts.append((start, lower))
        return "budget", ()

    monkeypatch.setattr(x3, "solve_signal", solve)
    for mean, expected in ((0.4, 0.5), (-0.55, 0.55)):
        target = np.full((8, 3), mean)
        context = x3.Matching(Cell(0.3, 0.5), _plan(0.5), TINY, None, 8, 0, target)
        attempt = x3.solve_attempt(context, 12)
        assert attempt.start == expected and attempt.lower == abs(mean)
    assert starts == [(0.5, 0.4), (0.55, 0.55)]


def _known(success: bool) -> ValidatedFit:
    if not success:
        return ValidatedFit((FitAttempt(1024, _fit("family-limit-upper"), None),))
    validation = Validation(
        True, np.zeros(2), np.ones(2), np.zeros(2), np.zeros(2), True, 0.0
    )
    return ValidatedFit((FitAttempt(1024, _fit(parameters=(0.85, 0.1)), validation),))


def _free(status: str, point: x3.OuterPoint, passed: bool | None) -> x3.FreeFit:
    return x3.FreeFit((x3.FreeAttempt(64, status, 0.4, 0.6, (point,), None, passed),))


def test_gaps_follow_the_declared_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    cell = Cell(0.3, 0.6)
    monkeypatch.setattr(x3, "fit_cell", lambda source: _known(False))
    result = x3.x3_contrasts(cell, _plan(0.6), None, SMALL)
    assert result["gap"] == "known" and result["success"] is False
    assert result["free"] is None and result["delta"] is None
    assert result["attempts"] == ["known:family-limit-upper"]
    monkeypatch.setattr(x3, "fit_cell", lambda source: _known(True))
    point = x3.OuterPoint(0.6, _fit(), 0.1, 1e-3, 1e-4)
    monkeypatch.setattr(x3, "fit_free", lambda *_: _free("family-limit", point, None))
    result = x3.x3_contrasts(cell, _plan(0.6), None, SMALL)
    assert result["gap"] == "free" and result["delta"] is None
    assert result["attempts"] == ["known:interior", "free:family-limit"]
    assert 0 <= result["known"]["auc"] <= 1 and len(result["known"]["interval_95"]) == 2
    assert result["free"]["success"] is False and "auc" not in result["free"]
    assert set(result["means"]) == {"set", "social", "known"}
    json.dumps(result, allow_nan=False)


def test_both_contrasts_share_the_social_panels_and_pair_the_bootstrap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cell, plan = Cell(0.3, 0.6), _plan(0.6)
    point = x3.OuterPoint(0.7, _fit(parameters=(0.75, 0.2)), 0.0, 1e-3, 1e-4)
    monkeypatch.setattr(x3, "fit_cell", lambda source: _known(True))
    monkeypatch.setattr(x3, "fit_free", lambda *_: _free("interior", point, True))
    calls: list[tuple[np.ndarray, ...]] = []
    original = x3.contrast

    def recording(*arrays: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        calls.append(arrays)
        return original(*arrays)

    monkeypatch.setattr(x3, "contrast", recording)
    result = x3.x3_contrasts(cell, plan, None, SMALL)
    (_, social_train, _, social_check), free = calls
    assert free[1] is social_train and free[3] is social_check
    expected = PanelSource(replace(cell, reliability=0.7), plan, size=TINY)
    assert same_bits(
        free[0], expected.profiles("train", 40, parameters=np.array([0.75, 0.2]))
    )
    assert same_bits(
        social_check, PanelSource(cell, plan, size=TINY).profiles("check", 80)
    )
    scores = [original(*arrays) for arrays in calls]
    draws = f.paired_network_bootstrap(
        [(n.reshape(40, 2), s.reshape(40, 2)) for n, s in scores],
        seed=plan.seed("bootstrap", "resample", 0),
        resamples=SMALL.resamples,
    )
    assert result["delta"]["interval_95"] == f.percentile_interval(
        draws[:, 1] - draws[:, 0]
    )
    assert result["free"]["parameters"] == {"phi": 0.75, "eta": 0.2, "signal": 0.7}
    assert result["success"] is True and result["gap"] is None
    assert result["seeds"]["bootstrap"] == f.derive_seed(
        "x3", 4, "bootstrap", "resample", 0
    )


def test_free_fit_iterates_on_real_panels_at_each_share(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The outer search on real tiny panels, with the inner solve replaced by
    one frozen evaluation at fixed (phi, eta): each point's L3 residual is the
    frozen formula on the B_r panels at its own share."""
    fixed = np.array([0.85, 0.1])

    def inner(target: np.ndarray, evaluate: Any, **_: Any) -> ProfileFit:
        differences = evaluate(*fixed) - target
        se = differences.std(0, ddof=1) / np.sqrt(len(target))
        return ProfileFit(
            fixed, differences, differences.mean(0), se, 0.25 * se, 1, "interior", 2
        )

    monkeypatch.setattr(x3, "profile_match", inner)
    cell, plan = Cell(0.03, 0.5), _plan(0.5)
    fit = x3.fit_free(cell, plan, None, SMALL)
    first = fit.attempts[0]
    assert first.count == 64 and first.start == 0.5 and first.points[0].signal == 0.5
    assert first.status in {"interior", "family-limit", "budget"}
    assert all(first.lower <= p.signal <= x3.UPPER for p in first.points)
    assert len(first.points) > 2
    target = PanelSource(cell, plan, size=TINY).profiles("match", 64)[:, :3]
    for point in first.points[:3]:
        rows = PanelSource(
            replace(cell, reliability=point.signal), plan, size=TINY
        ).profiles("match", 64, parameters=fixed)[:, :3]
        differences = rows - target
        assert point.residual == differences.mean(0)[2]
        assert point.se == (differences.std(0, ddof=1) / 8)[2]
    record = x3.free_record(fit)
    json.dumps(record, allow_nan=False)
    assert record["attempts"][0]["outer_evaluations"] == len(first.points)


def test_free_validation_is_the_frozen_rule_on_three_moments(tmp_path: Path) -> None:
    cell, plan = Cell(0.3, 0.6), _plan(0.6)
    store = SealedStore(tmp_path / "validation")
    context = x3.matching(cell, plan, TINY, store, 8, 1)
    parameters = np.array([0.8, 0.2])
    point = x3.OuterPoint(0.7, _fit(parameters=(0.8, 0.2)), 0.0, 2e-3, 5e-5)
    validation, passed = x3.validate_free(context, point)
    files = sorted(p.name for p in store.root.iterdir())
    social = PanelSource(cell, plan, size=TINY, store=store).profiles(
        "validate", 2048, attempt=1
    )[:, :3]
    rows = PanelSource(
        replace(cell, reliability=0.7), plan, size=TINY, store=store
    ).profiles("validate", 2048, parameters=parameters, attempt=1)[:, :3]
    assert sorted(p.name for p in store.root.iterdir()) == files
    se = np.array([1e-3, 1e-3, 2e-3])
    frozen = validate_fit(rows - social, 2, se)
    assert same_bits(validation.residual, frozen.residual)
    assert same_bits(validation.z, frozen.z)
    total = np.hypot(se, frozen.se)
    assert passed == bool(
        np.all(np.abs(frozen.residual) <= 4 * total) and frozen.passed
    )


def test_free_fit_retries_once_and_only_after_a_failed_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runs: list[tuple[int, int]] = []
    point = x3.OuterPoint(0.6, _fit(), 0.0, 1e-3, 1e-4)
    outcomes: dict[str, list[bool]] = {}

    def solve(context: x3.Matching, budget: int) -> x3.FreeAttempt:
        runs.append((context.count, context.attempt))
        return x3.FreeAttempt(context.count, status, 0.4, 0.6, (point,))

    def validate(context: x3.Matching, point: x3.OuterPoint) -> tuple[Any, bool]:
        return None, outcomes[status].pop(0)

    monkeypatch.setattr(x3, "solve_attempt", solve)
    monkeypatch.setattr(x3, "validate_free", validate)
    monkeypatch.setattr(
        x3,
        "matching",
        lambda cell, seeds, size, store, count, attempt: x3.Matching(
            cell, seeds, size, store, count, attempt, np.zeros((2, 3))
        ),
    )
    cell, plan = Cell(0.3, 0.6), _plan(0.6)
    for status, results, expected in (
        ("interior", [True], [(64, 0)]),
        ("interior", [False, True], [(64, 0), (128, 1)]),
        ("interior", [False, False], [(64, 0), (128, 1)]),
        ("budget", [], [(64, 0)]),
    ):
        runs.clear()
        outcomes[status] = list(results)
        fit = x3.fit_free(cell, plan, None, SMALL)
        assert runs == expected
        assert fit.success == (status == "interior" and results[-1])


def test_cell_record_seals_replays_and_records_errors() -> None:
    out = f.require_sealed_location(f.SEALED_ROOT / "cells")
    unit, position = x3.CELLS[0]
    digests = {"x3-fit": "0" * 64}

    def compute(store: SealedStore) -> dict[str, Any]:
        if store.get_array("f" * 64) is None:
            store.put_array("f" * 64, np.zeros(3))
        return {"success": True, "attempts": ["known:interior"], "value": 1}

    record = x3.cell_record(
        "x3", 0, unit, position, out, digests, {"size": TINY}, compute
    )
    assert record["error"] is None and record["value"] == 1 and record["seal_sha256"]
    assert record["cell"] == {
        "index": 0,
        "unit": unit.key,
        "position": position,
        "a": GRID[position],
        "r": 0.5,
        "block": 0,
        "family": "B",
        "channel": "observed",
    }
    again = x3.cell_record(
        "x3", 0, unit, position, out, digests, {"size": TINY}, compute
    )
    assert again["seal_sha256"] == record["seal_sha256"]

    def failing(store: SealedStore) -> dict[str, Any]:
        raise ValueError("ill-conditioned local profile")

    unit, position = x3.CELLS[1]
    broken = x3.cell_record("x3", 1, unit, position, out, {}, {"size": TINY}, failing)
    assert broken["error"].startswith("ValueError") and broken["success"] is None
    assert broken["seal_sha256"] is None and broken["attempts"] == []


def test_cells_units_and_preconditions_are_the_declared_ones() -> None:
    assert len(x3.CELLS) == 72 and len(x3.UNITS) == 9
    assert [unit.cells[i].share for unit, i in x3.CELLS[:8]] == list(GRID[1:])
    assert [unit.cells[i].reliability for unit, i in x3.CELLS[::8]] == list(
        RELIABILITIES
    )
    assert all(unit.key.startswith("x3-t1-") for unit, _ in x3.CELLS)
    assert all(unit.seeds.analysis == "x3" for unit in x3.UNITS)
    assert x3.STORE.cells == ((0.0, 0.9), (0.03, 0.5), (0.3, 0.6))
    assert x3.FIT.cells == ((0.03, 0.5), (0.3, 0.6))
    assert x3.STORE.frozen is f.frozen_cell_executor
    assert x3.SUITE.sealed and x3.SUITE.kinds == ("x3",)
    assert [spec.name for spec in x3.SUITE.preconditions] == ["x3-store", "x3-fit"]
    assert asdict(x3.DECLARED) == {
        "size": 10626,
        "matching": 1024,
        "retry_matching": 4096,
        "train": 2000,
        "check": 4000,
        "resamples": 1000,
        "outer_budget": 12,
    }
    analysis = x3.analyses(f.SEALED_ROOT, {})["x3"]
    assert analysis.total == 72 and analysis.sizes == asdict(x3.DECLARED)
    assert analysis.modules == x3.MODULES


def _record(index: int, **fields: Any) -> dict[str, Any]:
    return {
        "cell": x3.cell_identity(index, *x3.CELLS[index]),
        "sizes": asdict(x3.DECLARED),
        "error": None,
        "gap": None,
        "known": {"auc": 0.72, "interval_95": [0.70, 0.74]},
        "free": {
            "auc": 0.69,
            "interval_95": [0.67, 0.71],
            "attempts": [{"status": "interior"}],
        },
        "delta": {"point": -0.03, "interval_95": [-0.05, -0.01]},
        "timing": {
            "started_utc": x12.utc_now(),
            "finished_utc": x12.utc_now(),
            "wall_seconds": 1.0,
            "cpu_seconds": 1.0,
        },
        "provenance": {"code": {"commit": "c"}, "host": {"hostname": "h"}},
        **fields,
    }


def test_declared_readings_and_the_sealed_aggregate(synthetic_analysis: Any) -> None:
    assert x3.read_cell(_record(0)) == {
        "reading": "supports-objection",
        "lost_crossing": False,
    }
    free = {"auc": 0.68, "interval_95": [0.66, 0.695], "attempts": []}
    lost = x3.read_cell(_record(0, free=free))
    assert lost["lost_crossing"] is True
    inside = _record(0, delta={"point": 0.0, "interval_95": [-0.02, 0.02]})
    assert x3.read_cell(inside)["reading"] == "against-objection"
    wide = _record(0, delta={"point": 0.0, "interval_95": [-0.03, 0.01]})
    assert x3.read_cell(wide)["reading"] == "inconclusive"
    gap = _record(0, gap="free", free={"attempts": [{"status": "budget"}]})
    assert x3.read_cell(gap) == {
        "reading": "free-gap",
        "free_status": "budget",
        "lost_crossing": None,
    }
    assert x3.read_cell(_record(0, gap="known"))["reading"] == "gap"
    assert x3.read_cell(_record(0, error="ValueError('x')"))["reading"] == "error"
    out = f.require_sealed_location(f.SEALED_ROOT / "aggregate")
    f.run_shard(
        synthetic_analysis(
            out,
            f.Analysis("x3", len(x3.CELLS), asdict(x3.DECLARED), _record),
            x3.SUITE.preconditions,
        ),
        out,
    )
    with pytest.raises(ValueError, match="Sealed until"):
        x3.aggregate([out])
    f.private_directory(f.RELEASE_RECORD.parent)
    f.RELEASE_RECORD.write_text("{}")
    result = x3.aggregate([out])
    assert result["summary"]["readings"] == {"supports-objection": 72}
    assert result["incomplete"] == [] and len(result["cells"]) == 72
    assert "provenance" not in result["cells"][0]


def test_probe_counts_panels_with_probe_seeds_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(x3, "SIZE", TINY)
    result = x3.probe(2)
    assert result["count"] == 2 and result["nominal_cell_cpu_hours"] > 0
    assert result["nominal_cell_panels"]["social"] == 9072
    assert f.probe_seed("state", 0) >= f.PROBE_BASE


def test_module_imports_only_frozen_modules_the_foundation_and_x1_utilities() -> None:
    tree = ast.parse(Path(x3.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if not node.module.startswith("ic_study"):
                continue
            if (STUDY / "src" / node.module.replace(".", "/")).is_dir():
                imported |= {f"{node.module}.{alias.name}" for alias in node.names}
            else:
                imported.add(node.module)
    freeze = json.loads((STUDY / x12.FREEZE).read_text())["code"]
    reused = {
        "ic_study.simulation.v4_exploratory",
        "ic_study.simulation.v4_exploratory_x1b",
        "ic_study.simulation.v4_exploratory_x3x7",
    }
    assert reused <= imported
    for name in imported - reused:
        path = "src/" + name.replace(".", "/") + ".py"
        assert freeze[path] == hashlib.sha256((STUDY / path).read_bytes()).hexdigest()
    provenance = f.successor_provenance(x3.MODULES)
    assert provenance["frozen_python_mismatched"] == []
    assert (
        "src/ic_study/simulation/v4_exploratory_x3.py" in provenance["successor_sha256"]
    )


def test_outer_solver_searches_beyond_an_initial_plateau() -> None:
    evaluate, seen = _points(lambda s: max(s - 0.8, -0.05))
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "interior"
    assert points[-1].signal == pytest.approx(0.8, abs=1e-4)
    assert len(seen) <= 12 and len(set(seen)) == len(seen)


def test_outer_solver_does_not_infer_no_root_from_equal_samples() -> None:
    evaluate, seen = _points(lambda _: 0.05)
    status, points = x3.solve_signal(evaluate, 0.7, 0.3, budget=12)
    assert status == "budget" and len(points) == 12
    assert 0.3 in seen and x3.UPPER in seen
    evaluate, _ = _points(lambda _: 0.05)
    assert (
        x3.solve_signal(evaluate, 0.7, 0.7, upper=0.7, budget=12)[0] == "family-limit"
    )


@pytest.fixture
def sharded_x3_outputs(monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    outs = [f.SEALED_ROOT / name for name in ("icllm", "homelab")]
    for shard, out in enumerate(outs):
        host = {"cpu": out.name, "system": "synthetic", "environment": "locked"}
        monkeypatch.setattr(f, "host_class", lambda host=host: host)
        f.require_sealed_location(out)
        for spec in x3.SUITE.preconditions:
            f.write_private_json(spec.verification(out), {"synthetic_host": host})
        digests = {
            spec.name: f._digest(spec.verification(out))
            for spec in x3.SUITE.preconditions
        }

        def compute(
            index: int, verification: dict[str, str] = digests
        ) -> dict[str, Any]:
            return _record(index, verification_sha256=verification)

        analysis = f.Analysis(
            "x3",
            len(x3.CELLS),
            asdict(x3.DECLARED),
            compute,
            modules=x3.MODULES,
            verification=digests,
            identities=tuple(
                x3.cell_identity(i, *cell) for i, cell in enumerate(x3.CELLS)
            ),
        )
        f.run_shard(analysis, out, shard=shard, shards=2)
    f.private_directory(f.RELEASE_RECORD.parent)
    f.RELEASE_RECORD.write_text("{}")
    return outs


def test_cli_aggregates_disjoint_hosts_and_records_source_metadata(
    sharded_x3_outputs: list[Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    outs = sharded_x3_outputs
    capsys.readouterr()
    output = tmp_path / "union.json"
    assert (
        x3.main(
            [
                "aggregate",
                "--out",
                str(outs[0]),
                "--out",
                str(outs[1]),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert capsys.readouterr().out == ""
    result = json.loads(output.read_bytes())
    assert result["incomplete"] == [] and len(result["cells"]) == 72
    assert result["sources"] == [
        {
            "out": str(out),
            "run_manifest_sha256": f._digest(out / "run-manifest.json"),
            "host_class": json.loads((out / "run-manifest.json").read_bytes())[
                "host_class"
            ],
            "accepted_units": 36,
        }
        for out in outs
    ]
    assert len({source["run_manifest_sha256"] for source in result["sources"]}) == 2


@pytest.mark.parametrize(
    "damage",
    [
        "duplicate",
        "commit",
        "lock",
        "successor",
        "seeds",
        "window",
        "sizes",
        "total",
        "identities",
        "verification",
        "record-host",
        "missing-manifest",
    ],
)
def test_union_rejects_conflicting_or_unbound_sources(
    damage: str, sharded_x3_outputs: list[Path]
) -> None:
    outs = sharded_x3_outputs
    if damage == "duplicate":
        record = json.loads((outs[0] / "x3/x3-0000.json").read_bytes())
        manifest = json.loads((outs[1] / "run-manifest.json").read_bytes())
        binding = json.loads((outs[1] / "manifest-x3.json").read_bytes())
        record["run_manifest_sha256"] = binding["run_manifest_sha256"]
        record["verification_sha256"] = binding["verification_sha256"]
        record["provenance"]["host_class"] = manifest["host_class"]
        f.write_private_json(outs[1] / "x3/x3-0000.json", record)
        expected = "Duplicate.*x3-0000"
    elif damage in ("commit", "lock", "successor", "seeds", "window"):
        path = outs[1] / "run-manifest.json"
        manifest = json.loads(path.read_bytes())
        if damage == "commit":
            manifest["code"]["commit"] = "foreign"
        elif damage == "lock":
            manifest["code"]["lock_sha256"] = "foreign"
        elif damage == "successor":
            manifest["successor"]["successor_sha256"] = {}
        elif damage == "seeds":
            manifest["seeds"]["root"] = 1
        else:
            manifest["window_close"] = "2026-10-11T02:59:00+00:00"
        path.write_text(json.dumps(manifest))
        expected = "manifest"
    elif damage in ("sizes", "total", "identities"):
        path = outs[1] / "manifest-x3.json"
        binding = json.loads(path.read_bytes())
        if damage == "sizes":
            binding["sizes"]["size"] = 1
        elif damage == "total":
            binding["total"] = 1
        else:
            binding["identities"][0]["a"] = 0.123
        path.write_text(json.dumps(binding))
        expected = "manifest"
    elif damage == "verification":
        (outs[1] / "x3-fit-precondition.json").write_text("{}")
        expected = "verification"
    elif damage == "record-host":
        path = outs[1] / "x3/x3-0001.json"
        record = json.loads(path.read_bytes())
        record["provenance"]["host_class"] = {"cpu": "foreign"}
        path.write_text(json.dumps(record))
        expected = "record"
    else:
        (outs[1] / "run-manifest.json").unlink()
        expected = "manifest"
    with pytest.raises(ValueError, match=expected):
        x3.aggregate(outs)
