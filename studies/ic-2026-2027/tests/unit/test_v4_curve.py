"""Confirmatory orchestration uses fixtures only: no gate or scientific run."""

import fcntl
import signal
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import Uncertainty
from ic_study.models.anchored_panel import Floats
from ic_study.simulation import v4_curve
from ic_study.simulation.detection_v4 import (
    GRID,
    ControlDependency,
    PanelSource,
    SeedPlan,
)
from ic_study.simulation.v4_curve import (
    CLOSE,
    INVALID,
    NOT_STARTED,
    PARTIAL,
    VALID,
    ConfirmatorySeedPlan,
    CurveUnit,
    OperationalClose,
    close_inventory,
    complete_curve,
    curve_units,
    execute_cell,
    observed_unit,
    released_curves,
    schedule,
)
from ic_study.simulation.v4_store import SealedStore


def seed_cell(root: Path, index: int, *, success: bool = True) -> None:
    store = SealedStore(root / f"a{index}")
    if success:
        store.put_array("scores0", np.full((2000, 2), index, dtype=float))
        store.put_array("scores1", np.full((2000, 2), index + 1, dtype=float))
        store.put_array("nuisance", np.arange(2000, dtype=float) + index)
    store.put_json("result", {"success": success})
    store.seal()


def test_inventory_and_seed_alignment_isolation() -> None:
    units = curve_units()
    assert len(units) == 414
    assert [u.tier for u in units] == sorted(u.tier for u in units)
    assert all(tuple(c.share for c in u.cells) == GRID for u in units)
    plan = units[0].seeds
    phases = (
        "match",
        "validate",
        "train",
        "check",
        "reference",
        "bootstrap",
        "nuisance",
        "stencil",
    )
    seeds = {plan.seed(p, "state", 0) for p in phases}
    assert len(seeds) == len(phases)
    assert not seeds & {SeedPlan().seed(p, "state", 0) for p in phases}
    assert plan.seed("match", "state", 0) != plan.seed("match", "state", 0, attempt=1)
    with pytest.raises(ValueError):
        ConfirmatorySeedPlan(gate=True).seed("match", "state", 0)


@pytest.mark.parametrize(
    "null_auc,final_auc,status",
    [(0.5, 0.9, VALID), (0.7, 0.9, INVALID), (0.5, 0.6, VALID)],
)
def test_nine_strength_stack_band_null_gate_and_censoring(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    null_auc: float,
    final_auc: float,
    status: str,
) -> None:
    unit = curve_units()[0]
    for index in range(9):
        seed_cell(tmp_path, index)
    point = np.linspace(null_auc, final_auc, 9)

    def uncertainty(
        left: Floats, right: Floats, nuisance: Floats, *, seed: int
    ) -> Uncertainty:
        assert left.shape == right.shape == (2000, 2, 9)
        assert nuisance.shape == (2000, 9)
        np.testing.assert_array_equal(left[0, 0], np.arange(9))
        np.testing.assert_array_equal(nuisance[:, 1] - nuisance[:, 0], np.ones(2000))
        assert seed == unit.seeds.seed("bootstrap", "state", 0)
        return Uncertainty(
            point, np.full(9, 0.01), np.full(9, 0.01), np.tile(point, (2000, 1))
        )

    monkeypatch.setattr(v4_curve, "score_uncertainty", uncertainty)
    result = complete_curve(unit, tmp_path)
    assert result["status"] == status
    assert complete_curve(unit, tmp_path) == result
    if status == INVALID or final_auc < 0.7:
        assert result["sustained"] is None
    else:
        assert result["sustained"] in GRID
    if status == INVALID:
        assert result["sustained_interval"] is None


def test_gap_censors_only_boundaries_crossing_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for index in range(9):
        seed_cell(tmp_path, index, success=index != 4)

    def available_only(
        left: Floats, right: Floats, nuisance: Floats, *, seed: int
    ) -> Uncertainty:
        assert left.shape == (2000, 2, 8)
        assert 4 not in left[0, 0]
        point = np.linspace(0.5, 0.9, 8)
        return Uncertainty(
            point, np.full(8, 0.01), np.full(8, 0.01), np.tile(point, (2000, 1))
        )

    monkeypatch.setattr(v4_curve, "score_uncertainty", available_only)
    result = complete_curve(curve_units()[0], tmp_path)
    assert result["status"] == VALID
    assert result["gap_count"] == 1
    assert result["valid_null_gate"] is True
    assert result["band_complete"] is False
    assert result["first"] is None
    assert result["first_censoring"] == "gap at a=0.03"
    assert result["sustained"] == 0.1


def test_null_gap_alone_invalidates_unit_and_other_boundaries_survive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for index in range(9):
        seed_cell(tmp_path, index, success=index != 8)

    def available_only(
        left: Floats, right: Floats, nuisance: Floats, *, seed: int
    ) -> Uncertainty:
        point = np.array([0.5, 0.6, 0.75, 0.8, 0.82, 0.84, 0.86, 0.88])
        return Uncertainty(
            point, np.full(8, 0.01), np.full(8, 0.01), np.tile(point, (2000, 1))
        )

    monkeypatch.setattr(v4_curve, "score_uncertainty", available_only)
    result = complete_curve(curve_units()[0], tmp_path)
    assert result["status"] == VALID
    assert result["first"] == 0.003
    assert result["first_interval"] == [0.003, 0.003]
    assert result["sustained"] is None
    assert result["sustained_censoring"] == "gap at a=0.9"


def test_cell_calls_pipeline_and_preserves_control_dependency(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []
    unit = next(u for u in curve_units() if u.cells[0].channel == "latent")
    result = SimpleNamespace(
        fit=SimpleNamespace(success=True),
        uncertainty=None,
        scores0=np.zeros((2000, 2)),
        scores1=np.ones((2000, 2)),
        dependency_gap=False,
        nuisance=(
            SimpleNamespace(
                centered=np.zeros(2000),
                shifts=np.zeros((2000, 2)),
                variance=0.0,
                mcse=0.0,
                mean_shift=0.0,
                projected_fraction=0.0,
            ),
        ),
    )
    dependency = observed_unit(unit)
    assert dependency is not None
    prior = SealedStore(tmp_path / dependency.key / "a0")
    prior.put_array("eta-shifts", np.arange(2000, dtype=float))
    prior.put_json("result", {"success": True, "parameters": [0.7, 0.2]})
    prior.seal()

    def pipeline(
        source: PanelSource,
        *,
        observed: ControlDependency | None = None,
        compute_uncertainty: bool = True,
    ) -> SimpleNamespace:
        assert not compute_uncertainty
        calls.append((source.cell.channel, source.seeds, observed))
        return result

    monkeypatch.setattr(v4_curve, "pipeline", pipeline)
    monkeypatch.setattr(v4_curve, "pipeline_record", lambda _r: {"success": True})
    execute_cell(unit, 0, tmp_path / unit.key / "a0")
    execute_cell(unit, 0, tmp_path / unit.key / "a0")
    assert len(calls) == 1
    assert calls[0][0] == "latent"
    inherited = calls[0][2]
    assert inherited is not None and inherited.success
    np.testing.assert_array_equal(inherited.parameters, [0.7, 0.2])
    np.testing.assert_array_equal(inherited.eta_shifts[0], np.arange(2000))


def test_cell_infrastructure_error_leaves_resumable_checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    unit = curve_units()[0]

    def broken(*_args: object, **_kwargs: object) -> None:
        raise MemoryError

    monkeypatch.setattr(v4_curve, "pipeline", broken)
    path = tmp_path / unit.key / "a0"
    with pytest.raises(MemoryError):
        execute_cell(unit, 0, path)
    assert SealedStore(path).get_json("result") is None
    assert not (path / "seal.json").exists()


def test_schedule_resumes_fixed_order_and_stops_at_tier_barrier(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = curve_units()[0]
    units = (base, replace(base, key="second"), replace(base, key="third", tier=2))
    monkeypatch.setattr(v4_curve, "curve_units", lambda: units)
    calls = []

    def worker(unit: CurveUnit, index: int, path: Path) -> None:
        calls.append((unit.key, index))
        seed_cell(path.parent, index, success=False)

    root = SealedStore(tmp_path / "run")
    result = schedule(
        root,
        {},
        shard=0,
        shards=2,
        worker=worker,
        now=lambda: CLOSE - timedelta(days=1),
    )
    assert result["tier_blocked"] == 1
    assert calls == [(base.key, i) for i in range(9)]
    calls.clear()
    schedule(
        root,
        {},
        shard=1,
        shards=2,
        worker=worker,
        now=lambda: CLOSE - timedelta(days=1),
    )
    schedule(
        root,
        {},
        shard=0,
        shards=2,
        worker=worker,
        now=lambda: CLOSE - timedelta(days=1),
    )
    assert calls == [("second", i) for i in range(9)] + [("third", i) for i in range(9)]
    assert schedule(root, {}, shard=0, shards=2, worker=worker)["completed"] == 0
    with pytest.raises(ValueError, match="provenance"):
        schedule(root, {"changed": True}, shards=2)


def test_close_preserves_partial_and_never_releases_early(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = curve_units()[0]
    units = (base, replace(base, key="not-started"))
    monkeypatch.setattr(v4_curve, "curve_units", lambda: units)
    root = SealedStore(tmp_path / "run")

    def interrupted(unit: CurveUnit, index: int, path: Path) -> None:
        seed_cell(path.parent, index, success=False)
        raise OperationalClose

    assert schedule(root, {}, worker=interrupted)["closed"] == 1
    with pytest.raises(ValueError, match="until close"):
        released_curves(root, now=CLOSE - timedelta(seconds=1))
    result = close_inventory(root, now=CLOSE)
    rows = cast(list[dict[str, object]], result["units"])
    assert [r["status"] for r in rows] == [PARTIAL, NOT_STARTED]
    assert result["main_curve_valid"] is False
    assert released_curves(root, now=CLOSE)["curves"] == []
    assert close_inventory(root, now=CLOSE) == result


def test_deadline_interrupt_keeps_checkpoint_for_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    unit = curve_units()[0]
    directory = tmp_path / "cell"

    def interrupted(
        source: PanelSource,
        *,
        observed: ControlDependency | None = None,
        compute_uncertainty: bool = True,
    ) -> None:
        assert source.store is not None
        source.store.put_array("checkpoint", np.ones((2, 2)))
        signal.raise_signal(signal.SIGALRM)

    monkeypatch.setattr(v4_curve, "pipeline", interrupted)
    with pytest.raises(OperationalClose):
        execute_cell(unit, 0, directory)
    store = SealedStore(directory)
    assert store.get_json("result") is None
    np.testing.assert_array_equal(store.get_array("checkpoint"), np.ones((2, 2)))
    result = SimpleNamespace(
        fit=SimpleNamespace(success=False),
        uncertainty=None,
        nuisance=(),
        dependency_gap=False,
    )
    monkeypatch.setattr(v4_curve, "pipeline", lambda *_a, **_k: result)
    monkeypatch.setattr(v4_curve, "pipeline_record", lambda _r: {"success": False})
    execute_cell(unit, 0, directory)
    record = store.get_json("result")
    assert record is not None and record["success"] is False


def test_corrupt_sealed_cell_fails_closed(tmp_path: Path) -> None:
    for index in range(9):
        seed_cell(tmp_path, index, success=False)
    (tmp_path / "a0" / "result.json").write_text('{"success": true}')
    with pytest.raises(ValueError, match="digest"):
        complete_curve(curve_units()[0], tmp_path)


def test_main_failure_suppresses_released_main_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = curve_units()[0]
    other = replace(base, key="other")
    monkeypatch.setattr(v4_curve, "curve_units", lambda: (base, other))
    root = SealedStore(tmp_path / "run")
    SealedStore(root.root / base.key).put_json(
        "curve", {"status": VALID, "first": 0.1, "sustained": 0.1}
    )
    SealedStore(root.root / other.key).put_json(
        "curve", {"status": INVALID, "first": None, "sustained": None}
    )
    result = released_curves(root, now=CLOSE)
    inventory = cast(dict[str, object], result["inventory"])
    curves = cast(list[dict[str, object]], result["curves"])
    assert inventory["main_curve_valid"] is False
    assert curves[0]["sustained"] == 0.1
    assert curves[0]["main_curve_valid"] is False


def test_curve_bootstrap_deadline_preserves_complete_cells_as_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    unit = curve_units()[0]
    monkeypatch.setattr(v4_curve, "curve_units", lambda: (unit,))
    root = SealedStore(tmp_path / "run")

    def worker(unit: CurveUnit, index: int, path: Path) -> None:
        seed_cell(path.parent, index)

    def bootstrap(
        left: Floats, right: Floats, nuisance: Floats, *, seed: int
    ) -> Uncertainty:
        signal.raise_signal(signal.SIGALRM)
        raise AssertionError("Deadline failed to interrupt bootstrap")

    monkeypatch.setattr(v4_curve, "score_uncertainty", bootstrap)
    outcome = schedule(root, {}, worker=worker)
    assert outcome == {"completed": 0, "closed": 1, "tier_blocked": 0}
    assert len(list((root.root / unit.key).glob("a*/result.json"))) == 9
    assert not (root.root / unit.key / "curve.json").exists()
    closed = close_inventory(root, now=CLOSE)
    rows = cast(list[dict[str, object]], closed["units"])
    assert rows[0]["status"] == PARTIAL


def test_same_tier_mobility_control_waits_for_observed_unit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    units = curve_units()
    observed = next(
        u for u in units if u.cells[0].mobility and u.cells[0].channel == "observed"
    )
    control = next(u for u in units if observed_unit(u) == observed)
    monkeypatch.setattr(v4_curve, "curve_units", lambda: (observed, control))
    root = SealedStore(tmp_path / "run")
    calls: list[str] = []

    def worker(unit: CurveUnit, index: int, path: Path) -> None:
        calls.append(unit.key)
        seed_cell(path.parent, index, success=False)

    assert schedule(root, {}, shard=1, shards=2, worker=worker)["tier_blocked"] == 1
    assert calls == []
    schedule(root, {}, shard=0, shards=2, worker=worker)
    assert schedule(root, {}, shard=1, shards=2, worker=worker)["completed"] == 1
    assert calls == [observed.key] * 9 + [control.key] * 9


def test_failed_observed_dependency_is_reused_as_gap_without_refitting(
    tmp_path: Path,
) -> None:
    unit = next(u for u in curve_units() if u.cells[0].channel == "latent")
    observed = observed_unit(unit)
    assert observed is not None
    seed_cell(tmp_path / observed.key, 0, success=False)
    execute_cell(unit, 0, tmp_path / unit.key / "a0")
    record = SealedStore(tmp_path / unit.key / "a0").get_json("result")
    assert record is not None and record["dependency_gap"] is True
    assert record["success"] is False
    assert not (tmp_path / unit.key / "a0" / "phases.jsonl").exists()


def test_curve_pipeline_skips_scalar_bootstrap_and_retains_scores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ic_study.analysis.detection_boundary_v4 import profile_match, validate_fit
    from ic_study.simulation import detection_v4
    from ic_study.simulation.detection_v4 import Cell, FitAttempt, ValidatedFit

    target = np.zeros((1024, 2))
    fit = profile_match(target, lambda _p, _e: target, identity=True)
    validated = ValidatedFit(
        (FitAttempt(1024, fit, validate_fit(np.zeros((2048, 2)), 2, np.zeros(2))),)
    )
    monkeypatch.setattr(detection_v4, "fit_cell", lambda *_a, **_k: validated)
    source = PanelSource(Cell(0, 0.7), SeedPlan())

    def profiles(
        phase: str,
        count: int,
        *,
        parameters: Floats | None = None,
        attempt: int = 0,
        start: int = 0,
    ) -> Floats:
        return np.random.default_rng(count + (parameters is None)).normal(
            size=(count, 5)
        )

    monkeypatch.setattr(source, "profiles", profiles)
    monkeypatch.setattr(
        detection_v4,
        "score_uncertainty",
        lambda *_a, **_k: pytest.fail("Scalar bootstrap repeated in curve pipeline"),
    )
    result = detection_v4.pipeline(source, compute_uncertainty=False)
    assert result.fit.success and result.uncertainty is None
    assert result.scores0 is not None and result.scores0.shape == (2000, 2)
    assert result.scores1 is not None and result.scores1.shape == (2000, 2)
    assert result.nuisance[0].centered.shape == (2000,)


def test_close_cannot_miss_a_shard_being_registered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    unit = curve_units()[0]
    monkeypatch.setattr(v4_curve, "curve_units", lambda: (unit,))
    root = SealedStore(tmp_path / "run")
    registering, proceed, working, finish = (Event() for _ in range(4))
    original_store = SealedStore

    def store(path: Path) -> SealedStore:
        if path.name == "shard-0":
            registering.set()
            assert proceed.wait(5)
        return original_store(path)

    def worker(unit: CurveUnit, index: int, path: Path) -> None:
        working.set()
        assert finish.wait(5)
        raise OperationalClose

    monkeypatch.setattr(v4_curve, "SealedStore", store)
    with ThreadPoolExecutor(max_workers=1) as pool:
        running = pool.submit(schedule, root, {}, worker=worker)
        try:
            assert registering.wait(5)
            # Registration still owns the root mutex, so close cannot snapshot
            # the lock inventory before this shard is visible and locked.
            with pytest.raises(BlockingIOError):
                close_inventory(root, now=CLOSE)
            proceed.set()
            assert working.wait(5)
            # Once registered, close acquires root but must see the active shard.
            with pytest.raises(BlockingIOError):
                close_inventory(root, now=CLOSE)
            assert not (root.root / "seal.json").exists()
        finally:
            proceed.set()
            finish.set()
        assert running.result(timeout=5)["closed"] == 1
    assert close_inventory(root, now=CLOSE)["main_curve_valid"] is False
    with pytest.raises(ValueError, match="already closed"):
        schedule(root, {})


def test_close_locks_root_before_discovering_shards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = SealedStore(tmp_path / "run")
    original_glob = Path.glob
    inspected = []

    def glob(path: Path, pattern: str) -> object:
        if path == root.root and pattern == "shard-*/lock":
            with (
                (root.root / "lock").open("a") as competing,
                pytest.raises(BlockingIOError),
            ):
                fcntl.flock(competing, fcntl.LOCK_EX | fcntl.LOCK_NB)
            inspected.append(True)
        return original_glob(path, pattern)

    monkeypatch.setattr(Path, "glob", glob)
    close_inventory(root, now=CLOSE)
    assert inspected == [True]
