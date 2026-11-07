"""Shared X3-X7 successor machinery: seeds, source, harness, runner and sealing."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import stat
from collections.abc import Callable, Iterator
from datetime import timedelta
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import Uncertainty, band
from ic_study.simulation import detection_v4, v4_curve
from ic_study.simulation import v4_exploratory as x12
from ic_study.simulation import v4_exploratory_x1b as b
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    Cell,
    PanelSource,
    SeedPlan,
)
from ic_study.simulation.v4_curve import ConfirmatorySeedPlan, curve_units
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


def test_seed_material_layout_and_refusals() -> None:
    material = b"v4-exploratory-x3-x7|20260928|x5|3|match|state|7"
    expected = int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
    assert f.derive_seed("x5", 3, "match", "state", 7) == expected
    plan = f.SuccessorSeedPlan(block=2, analysis="x7")
    assert plan.seed("check", "mask", 5, attempt=1) == f.derive_seed(
        "x7", 5, "check", "mask", 5
    )
    assert f.derive_seed("x4", 0, "single-fit", "state", 1001) > 0
    assert f.derive_seed("x3", 0, "bootstrap", "resample", 0) > 0
    for analysis, phase, role, index in (
        ("x1b", "match", "state", 0),
        ("x6", "match", "state", 0),
        ("x5", "test", "state", 0),
        ("x7", "replicate", "state", 0),
        ("x7", "match", "xi", 0),
        ("x7", "match", "state", -1),
    ):
        with pytest.raises(ValueError, match="Invalid successor seed"):
            f.derive_seed(analysis, 0, phase, role, index)
    for refused in (
        f.SuccessorSeedPlan(block=0, analysis="x7", gate=True),
        f.SuccessorSeedPlan(block=0, analysis="x7", repetition=1),
    ):
        with pytest.raises(ValueError, match="no gate"):
            refused.seed("train", "state", 0)
    with pytest.raises(ValueError, match="no gate"):
        plan.seed("train", "state", 0, attempt=2)
    with pytest.raises(ValueError, match="Invalid successor seed"):
        f.SuccessorSeedPlan(block=0).seed("train", "state", 0)


def test_units_are_the_frozen_tier_one_units_with_successor_streams() -> None:
    frozen = [unit for unit in curve_units() if unit.tier == 1]
    units = f.tier1_units("x7")
    assert [u.cells for u in units] == [u.cells for u in frozen]
    assert [u.key for u in units] == [f"x7-{u.key}" for u in frozen]
    assert f.tier1_units("x7", "x7-rich")[0].key == "x7-rich-t1-u00-r0"
    assert all(c == Cell(c.share, c.reliability) for u in units for c in u.cells)
    for block, unit in enumerate(units):
        assert unit.cells[0].reliability == RELIABILITIES[block]
        assert tuple(c.share for c in unit.cells) == GRID
        assert unit.seeds == f.SuccessorSeedPlan(block=block, analysis="x7")
        assert unit.seeds.seed("bootstrap", "state", 0) == f.derive_seed(
            "x7", 2 * block, "bootstrap", "state", 0
        )
    assert f.find_cell(units, 0.3, 0.6) == (units[2], GRID.index(0.3))
    with pytest.raises(ValueError, match="outside"):
        f.find_cell(units, 0.2, 0.6)


def test_successor_seeds_are_disjoint_from_every_other_namespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every seed in the study is the first eight bytes of SHA-256 over a
    '|'-joined material whose first field is a namespace. The frozen plans,
    the X1b plan and ``v4_exploratory.derive_seed`` are enumerated over their
    whole phase and role domain; their materials never lead with this
    namespace, and the seed sets are disjoint. Frozen seeds are computed only
    for comparison and never reach a generator."""
    captured: list[bytes] = []
    original = hashlib.sha256

    def recording(data: bytes = b"", **options: Any) -> Any:
        captured.append(bytes(data))
        return original(data, **options)

    monkeypatch.setattr(hashlib, "sha256", recording)
    plans: list[SeedPlan] = [SeedPlan(block=k) for k in range(9)]
    plans += [
        SeedPlan(repetition=r, block=k, gate=True) for r in (0, 1) for k in (0, 1)
    ]
    plans += [ConfirmatorySeedPlan(block=k) for k in range(9)]
    plans += [b.ExploratorySeedPlan(block=k) for k in range(9)]
    theirs = {
        plan.seed(phase, role, index, attempt=attempt)
        for plan in plans
        for phase in sorted(f.FROZEN_PHASES)
        for role in sorted(detection_v4.ROLES)
        for index in range(24)
        for attempt in (0, 1)
    }
    theirs |= {
        x12.derive_seed(analysis, block, phase, role, index)
        for analysis in ("x1a", "x2")
        for block in range(9)
        for phase in x12.PHASES[analysis]
        for role in sorted(x12.ROLES)
        for index in range(24)
    }
    other = set(captured)
    captured.clear()
    ours = {
        f.derive_seed(analysis, block, phase, role, index)
        for analysis, phases in f.ANALYSES.items()
        for block in range(18)
        for phase in sorted(phases)
        for role in sorted(f.ROLES)
        for index in range(24)
    }
    mine = set(captured)
    monkeypatch.undo()
    prefix = f"{f.NAMESPACE}|{f.ROOT}|".encode()
    assert all(m.startswith(prefix) for m in mine) and len(mine) == len(ours)
    assert not any(m.startswith(f.NAMESPACE.encode()) for m in other)
    assert {m.split(b"|")[0] for m in other} >= {
        b"ic-detection-boundary-v4-calibration",
        b"ic-detection-boundary-v4-gate-r0000-calibration",
        b"ic-detection-boundary-v4-confirmatory",
        b"v4-exploratory-x1-x2",
    }
    assert "|" not in f.NAMESPACE and f.NAMESPACE != x12.NAMESPACE
    assert other.isdisjoint(mine) and theirs.isdisjoint(ours)
    assert max(ours) < 2**64


def test_successor_seeds_are_outside_the_shp_crosswalk_range() -> None:
    crosswalk = pytest.importorskip("ic_study.analysis.shp_crosswalk")
    theirs = {
        crosswalk.crosswalk_seed(crosswalk.SEED_ROOT, block, replicate, role)
        for block in range(len(RELIABILITIES))
        for replicate in range(crosswalk.REPLICATES)
        for role in crosswalk.ROLES
    }
    ours = {
        f.derive_seed(analysis, block, "match", role, index)
        for analysis in f.ANALYSES
        for block in range(18)
        for role in sorted(f.ROLES)
        for index in range(16)
    }
    assert crosswalk.NAMESPACE != f.NAMESPACE
    assert min(theirs) >= 2**64 and max(ours) < 2**64


@pytest.mark.parametrize("attempt", [0, 1])
@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("share,reliability", [(0.03, 0.5), (0.9, 0.9)])
def test_frozen_social_profile_reproduces_panel_source_bitwise(
    share: float, reliability: float, phase: str, attempt: int
) -> None:
    cell = Cell(share, reliability)
    plan = f.SuccessorSeedPlan(block=RELIABILITIES.index(reliability), analysis="x3")
    frozen = PanelSource(cell, plan, size=TINY)
    successor = f.SuccessorSource(cell, plan, size=TINY)
    for parameters in (None, np.array([0.8, 0.3])):
        expected = frozen.profiles(
            phase, 3, parameters=parameters, attempt=attempt, start=2
        )
        actual = successor.profiles(
            phase, 3, parameters=parameters, attempt=attempt, start=2
        )
        assert same_bits(actual, expected)
    assert successor.panels == frozen.panels == 6


def test_successor_source_refuses_other_cells_and_plans() -> None:
    plan = f.SuccessorSeedPlan(block=0, analysis="x3")
    with pytest.raises(ValueError, match="tier-1"):
        f.SuccessorSource(Cell(0.3, 0.5, gain=0.1), plan)
    for other in (SeedPlan(), ConfirmatorySeedPlan(), b.ExploratorySeedPlan()):
        with pytest.raises(ValueError, match="successor seeds only"):
            f.SuccessorSource(Cell(0.3, 0.5), other)


def test_source_cell_executor_reproduces_the_frozen_cell_bitwise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The harness on a tiny interior cell: a = 0.03 and r = 0.5 fit at N = 60
    with X3 streams, so every stage down to the nuisance draws is compared.
    The seed calls of this complete cell, replayed on the frozen, gate,
    confirmatory and X1b plans, never hash a material of this namespace, and
    no material hashed while the cell ran leads with another namespace."""
    captured: list[bytes] = []
    calls: set[tuple[int, str, str, int, int]] = set()
    original = hashlib.sha256
    seed = f.SuccessorSeedPlan.seed

    def recording(data: bytes = b"", **options: Any) -> Any:
        captured.append(bytes(data))
        return original(data, **options)

    def listening(
        plan: f.SuccessorSeedPlan,
        phase: str,
        role: str,
        index: int,
        *,
        attempt: int = 0,
    ) -> int:
        calls.add((plan.block, phase, role, index, attempt))
        return seed(plan, phase, role, index, attempt=attempt)

    monkeypatch.setattr(v4_curve, "PanelSource", partial(PanelSource, size=TINY))
    monkeypatch.setattr(hashlib, "sha256", recording)
    monkeypatch.setattr(f.SuccessorSeedPlan, "seed", listening)
    spec = f.Precondition(
        "x3-tiny",
        f.tier1_units("x3"),
        ((0.03, 0.5),),
        lambda unit, index, directory, size: f.execute_source_cell(
            unit,
            index,
            directory,
            lambda cell, plan, store, size: f.SuccessorSource(
                cell, plan, size=size, store=store
            ),
            size=size,
        ),
    )
    out = f.require_sealed_location(f.SEALED_ROOT / "tiny")
    records = [f.precondition_side(spec, out, 0, side, size=TINY) for side in f.SIDES]
    monkeypatch.undo()
    assert [record["error"] for record in records] == [None, None]
    comparison = b.compare_cells(
        spec.directory(out, "frozen", 0), spec.directory(out, "successor", 0)
    )
    assert comparison["equal"], comparison["differing_files"]
    assert {"result.json", "scores0.npy", "nuisance.npy", "eta-shifts.npy"} <= set(
        comparison["sha256"]
    )
    result = json.loads((spec.directory(out, "frozen", 0) / "result.json").read_text())
    assert result["success"] is True
    assert result["attempts"][0]["status"] == "interior"
    seeds = [
        m for m in captured if b"|" in m and b"\n" not in m and not m.startswith(b"{")
    ]
    assert seeds and all(
        m.startswith(f"{f.NAMESPACE}|{f.ROOT}|x3|".encode()) for m in seeds
    )
    assert {phase for _, phase, _, _, _ in calls} >= {
        "match",
        "validate",
        "train",
        "check",
        "reference",
        "nuisance",
    }
    replayed: list[bytes] = []

    def replaying(data: bytes = b"", **options: Any) -> Any:
        replayed.append(bytes(data))
        return original(data, **options)

    monkeypatch.setattr(hashlib, "sha256", replaying)
    for block, phase, role, index, attempt in sorted(calls):
        for plan in (
            SeedPlan(block=block),
            SeedPlan(block=block, gate=True),
            ConfirmatorySeedPlan(block=block),
            b.ExploratorySeedPlan(block=block),
        ):
            if role in detection_v4.ROLES:
                plan.seed(phase, role, index, attempt=attempt)
    monkeypatch.undo()
    assert replayed and not any(m.startswith(f.NAMESPACE.encode()) for m in replayed)


def _fake(
    value: float, failing: frozenset[tuple[str, int]] = frozenset()
) -> Callable[[f.SuccessorUnit, int, Path, int], None]:
    def execute(unit: f.SuccessorUnit, index: int, directory: Path, _: int) -> None:
        SealedStore(directory.parent)
        store = SealedStore(directory)
        store.put_array("f" * 64, np.full(3, value))
        if (unit.key, index) in failing:
            raise ValueError("ill-conditioned local profile")
        store.put_json(
            "result", {"success": True, "attempts": [{"status": "interior"}]}
        )
        store.seal()

    return execute


def _spec(frozen: Any, successor: Any) -> f.Precondition:
    return f.Precondition(
        "fake",
        f.tier1_units("x5"),
        ((0.0, 0.5), (0.03, 0.5), (0.3, 0.6)),
        successor,
        frozen,
    )


def _run(spec: f.Precondition, out: Path) -> dict[str, Any]:
    for position in range(len(spec.cells)):
        for side in f.SIDES:
            f.precondition_side(spec, out, position, side, size=TINY)
    return f.verify(spec, out, size=TINY)


def test_verification_needs_identical_stores_two_results_and_this_host_class(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = f.require_sealed_location(f.SEALED_ROOT)
    same_spec = _spec(_fake(0.0), _fake(0.0))
    same = _run(same_spec, root / "same")
    assert same["passed"] and same["cells_reproduced_with_result"] == 3
    assert all(cell["unit_provenance_equal"] for cell in same["cells"])
    assert same["cells"][1]["attempts"] == ["interior"]
    path = same_spec.verification(root / "same")
    f.write_private_json(path, same)
    assert f.require_verification(same_spec, path, size=TINY) == (
        hashlib.sha256(path.read_bytes()).hexdigest()
    )
    assert f.verify(same_spec, root / "same", size=TINY)["passed"]
    with pytest.raises(ValueError, match="passing precondition"):
        f.require_verification(same_spec, path)
    with pytest.raises(ValueError, match="passing precondition"):
        f.require_verification(
            f.Precondition("other", same_spec.units, same_spec.cells, _fake(0.0)),
            path,
            size=TINY,
        )
    monkeypatch.setattr(f, "host_class", lambda: {"cpu": "another"})
    with pytest.raises(ValueError, match="passing precondition"):
        f.require_verification(same_spec, path, size=TINY)
    monkeypatch.undo()
    assert not _run(_spec(_fake(0.0), _fake(-0.0)), root / "flip")["passed"]
    keys = [same_spec.cell(k) for k in range(3)]
    one = _fake(0.0, frozenset({(keys[1][0].key, keys[1][1])}))
    alone = _run(_spec(_fake(0.0), one), root / "alone")
    assert not alone["passed"] and not alone["cells"][1]["equal"]
    assert alone["cells"][1]["errors"]["successor"].startswith("ValueError")
    two = _fake(0.0, frozenset((unit.key, index) for unit, index in keys[1:]))
    shared = _run(_spec(two, two), root / "shared")
    assert all(cell["equal"] for cell in shared["cells"])
    assert shared["cells_reproduced_with_result"] == 1 and not shared["passed"]


def test_cli_describes_checks_and_probes_a_suite(
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = f.require_sealed_location(f.SEALED_ROOT / "cli")
    spec = _spec(_fake(0.0), _fake(0.0))
    suite = f.Suite(
        "x9",
        True,
        ("x9", "x9b"),
        (spec,),
        lambda out, digests: {"x9": _analysis([])},
        lambda out: {},
        lambda count: {"count": count},
    )
    assert f.main(suite, ["describe"]) == 0
    assert capsys.readouterr().out == "x9 sealed x9,x9b\n"
    assert f.main(suite, ["check", "--out", str(root)]) == 1
    for position in range(len(spec.cells)):
        for side in f.SIDES:
            f.precondition_side(spec, root, position, side)
    f.write_private_json(spec.verification(root), f.verify(spec, root))
    capsys.readouterr()
    assert f.main(suite, ["check", "--out", str(root)]) == 0
    assert json.loads(capsys.readouterr().out) == {"fake": True}
    assert f.main(suite, ["probe", "--count", "3"]) == 0
    assert json.loads(capsys.readouterr().out) == {"analysis": "x9", "count": 3}


def _analysis(calls: list[int]) -> f.Analysis:
    def compute(index: int) -> dict[str, Any]:
        calls.append(index)
        return {
            "sizes": {"size": TINY},
            "auc": 0.123456,
            "error": "ValueError('x')" if index == 3 else None,
            "success": index != 4,
            "attempts": ["interior"],
            "timing": {
                "started_utc": x12.utc_now(),
                "finished_utc": x12.utc_now(),
                "wall_seconds": 1.0,
                "cpu_seconds": 1.0,
            },
        }

    return f.Analysis("x9", 7, {"size": TINY}, compute)


def test_runner_claims_units_in_order_resumes_and_prints_no_statistic(
    capsys: pytest.CaptureFixture[str],
) -> None:
    out = f.SEALED_ROOT / "run"
    calls: list[int] = []
    analysis = _analysis(calls)
    with pytest.raises(ValueError, match="must lie under"):
        f.run_shard(analysis, out.parent.parent / "elsewhere")
    locks = f.private_directory(f.require_sealed_location(out) / "locks")
    with f.claim(locks / f"{f.record_key('x9', 2)}.lock") as held:
        assert held
        assert f.run_shard(analysis, out, shard=0, shards=2) == [0, 4, 6]
    assert f.run_shard(analysis, out, only=[1, 5]) == [1, 5]
    assert f.run_shard(analysis, out) == [2, 3] and calls == [0, 4, 6, 1, 5, 2, 3]
    assert f.run_shard(analysis, out) == []
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert {frozenset(line) for line in lines} == {
        frozenset({"kind", "unit", "status", "wall_seconds", "cpu_seconds"})
    }
    assert [line["status"] for line in lines if line["unit"] == 3] == ["error"]
    records = out / "x9"
    assert stat.S_IMODE(records.stat().st_mode) == 0o700
    assert stat.S_IMODE((records / "x9-0000.json").stat().st_mode) == 0o600
    assert stat.S_IMODE(f.SEALED_ROOT.stat().st_mode) == 0o700
    record = SealedStore(records).get_json("x9-0000")
    assert record is not None
    provenance = record["provenance"]
    assert isinstance(provenance, dict)
    assert provenance["successor"]["frozen_python_mismatched"] == []
    assert provenance["successor"]["frozen_python_files"] == 80
    summary = f.status(out, "x9", 7)
    assert summary["errors"] == 1 and summary["fit_failures"] == 1
    assert summary["attempt_statuses"] == {"interior": 7} and summary["sealed"]
    changed = f.Analysis("x9", 7, {"size": 66}, analysis.compute)
    with pytest.raises(ValueError, match="different sizes"):
        f.run_shard(changed, out)
    fresh = f.SEALED_ROOT / "late"
    closed = f.run_shard(analysis, fresh, now=lambda: f.WINDOW_CLOSE)
    assert closed == [] and capsys.readouterr().out.strip() == (
        '{"kind": "x9", "status": "window-closed"}'
    )


def test_complete_records_report_incomplete_units_only_after_the_window() -> None:
    out = f.SEALED_ROOT / "partial"
    analysis = _analysis([])
    f.run_shard(analysis, out, only=[0, 1, 2])
    with pytest.raises(ValueError, match="Missing x9 units"):
        f.complete_records(out, "x9", 7, {"size": TINY})
    late = f.WINDOW_CLOSE + timedelta(seconds=1)
    kept, incomplete = f.complete_records(out, "x9", 7, {"size": TINY}, now=late)
    assert sorted(kept) == [0, 1, 2] and incomplete == [3, 4, 5, 6]
    with pytest.raises(ValueError, match="requested sizes"):
        f.complete_records(out, "x9", 7, {"size": 66}, now=late)


def test_sealed_aggregates_wait_for_the_release(tmp_path: Path) -> None:
    before = v4_curve.CLOSE - timedelta(seconds=1)
    assert not f.released(now=before)
    with pytest.raises(ValueError, match="Sealed until"):
        f.require_release(now=before)
    assert f.released(now=v4_curve.CLOSE)
    suite = f.Suite(
        "x9",
        True,
        ("x9",),
        (),
        lambda out, digests: {"x9": _analysis([])},
        lambda out: {"opened": True},
        lambda count: {},
    )
    output = tmp_path / "aggregate.json"
    arguments = ["aggregate", "--out", str(tmp_path), "--output", str(output)]
    if not f.released():
        with pytest.raises(ValueError, match="Sealed until"):
            f.main(suite, arguments)
        assert not output.exists()
    f.private_directory(f.RELEASE_RECORD.parent)
    f.RELEASE_RECORD.write_text("{}")
    assert f.released(now=before)
    assert f.require_release(now=before)["release_record_sha256"] == (
        hashlib.sha256(b"{}").hexdigest()
    )
    assert f.main(suite, arguments) == 0
    assert json.loads(output.read_text()) == {"opened": True}


def test_fixed_band_is_the_frozen_band_formula() -> None:
    rng = np.random.default_rng(5)
    point = np.array([0.5, 0.62, 0.71, 0.93, 1.0])
    replicates = np.clip(point + rng.normal(0, 0.02, (2000, 5)), 0, 1)
    uncertainty = Uncertainty(point, np.full(5, 0.02), np.full(5, 0.025), replicates)
    frozen = band(uncertainty)
    lower, upper = f.fixed_band(uncertainty, frozen.critical)
    assert same_bits(lower, frozen.lower) and same_bits(upper, frozen.upper)
    narrow = f.fixed_band(uncertainty, 1.96)
    assert np.all(narrow[0] >= frozen.lower) and np.all(narrow[1] <= frozen.upper)


def test_paired_bootstrap_is_the_frozen_network_resampling() -> None:
    rng = np.random.default_rng(8)
    null, social = rng.normal(size=(40, 2)), rng.normal(0.4, 1, size=(40, 2))
    single = f.paired_network_bootstrap([(null, social)], seed=99, resamples=50)
    assert same_bits(
        single[:, 0], x12.network_bootstrap(null, social, seed=99, resamples=50)
    )
    shifted = f.paired_network_bootstrap(
        [(null, social), (null, social + 10)], seed=99, resamples=50
    )
    assert same_bits(shifted[:, 0], single[:, 0]) and np.all(shifted[:, 1] == 1)
    with pytest.raises(ValueError, match="aligned"):
        f.paired_network_bootstrap(
            [(null, social), (null[:-1], social)], seed=1, resamples=2
        )
    assert f.percentile_interval(np.arange(101.0)) == [2.5, 97.5]


def test_indices_accept_lists_and_ranges() -> None:
    assert f.parse_indices(None) is None
    assert f.parse_indices("0-3,7,9-10") == [0, 1, 2, 3, 7, 9, 10]


def test_foundation_imports_only_frozen_modules_and_the_x1_utilities() -> None:
    tree = ast.parse(Path(f.__file__).read_text())
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
    }
    assert reused <= imported
    for name in imported - reused:
        path = "src/" + name.replace(".", "/") + ".py"
        assert freeze[path] == hashlib.sha256((STUDY / path).read_bytes()).hexdigest()
    provenance = f.successor_provenance()
    assert provenance["frozen_python_mismatched"] == []
    assert set(provenance["successor_sha256"]) == {
        "src/ic_study/simulation/v4_exploratory_x3x7.py",
        "src/ic_study/simulation/v4_exploratory.py",
        "src/ic_study/simulation/v4_exploratory_x1b.py",
    }
    assert set(provenance["declaration"]) == {"readme_sha256", "declaration_sha256"}


@pytest.mark.parametrize(
    "field", ["commit", "host", "size", "hash", "error", "provenance"]
)
def test_verify_rejects_identical_stores_with_incompatible_evidence(field: str) -> None:
    out = f.require_sealed_location(f.SEALED_ROOT / field)
    spec = _spec(_fake(0.0), _fake(0.0))
    assert _run(spec, out)["passed"]
    path = spec.run_record(out, "successor", 0)
    record = json.loads(path.read_bytes())
    if field == "commit":
        record["code"]["commit"] = "other"
    elif field == "host":
        record["host_class"] = {"cpu": "other"}
    elif field == "size":
        record["size"] = 1
    elif field == "hash":
        record["successor"]["successor_sha256"] = {}
    elif field == "error":
        record["error"] = "ValueError('terminal')"
    else:
        provenance = spec.directory(out, "successor", 0).parent / "provenance.json"
        provenance.write_text("{}")
    path.write_text(json.dumps(record))
    result = f.verify(spec, out, size=TINY)
    assert not result["passed"]
    assert not result["cells"][0]["equal"]


@pytest.mark.parametrize("field", ["commit", "successor", "identity", "verification"])
def test_resume_and_aggregate_reject_foreign_records(field: str) -> None:
    out = f.SEALED_ROOT / "foreign"
    analysis = _analysis([])
    f.run_shard(analysis, out, only=[0])
    path = out / "x9/x9-0000.json"
    record = json.loads(path.read_bytes())
    if field == "commit":
        record["provenance"]["code"]["commit"] = "foreign"
    elif field == "successor":
        record["provenance"]["successor"] = {}
    elif field == "identity":
        record["run_identity"] = {"kind": "x9", "index": 1}
    else:
        record["verification_sha256"] = {"fake": "foreign"}
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="x9-0000"):
        f.run_shard(analysis, out, only=[0])
    with pytest.raises(ValueError, match="x9-0000"):
        f.complete_records(out, "x9", 7, analysis.sizes, now=f.WINDOW_CLOSE)


def test_output_manifest_rejects_revision_change_before_resume(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    out = f.SEALED_ROOT / "changed-code"
    analysis = _analysis([])
    f.run_shard(analysis, out, only=[0])
    old = f.code_provenance()
    monkeypatch.setattr(f, "code_provenance", lambda: {**old, "commit": "foreign"})
    with pytest.raises(ValueError, match="manifest"):
        f.run_shard(analysis, out, only=[0, 1])


@pytest.mark.parametrize("kind", ["x5", "x7"])
@pytest.mark.parametrize(
    "damage",
    [
        None,
        "success",
        "commit",
        "hash",
        "identity",
        "verification",
        "false-pass",
        "unknown-rich",
        "host",
        "seeds",
        "declaration",
        "results",
        "errors",
    ],
)
def test_legacy_aggregate_accepts_only_pinned_complete_evidence(
    kind: str, damage: str | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dataclasses import asdict

    from ic_study.simulation import v4_exploratory_x5 as x5
    from ic_study.simulation import v4_exploratory_x7 as x7

    module = x5 if kind == "x5" else x7
    sizes = asdict(x5.DECLARED_X5 if kind == "x5" else x7.DECLARED_X7)
    pin = json.loads((f.DECLARATION / "compatibility-c8e4861f.json").read_bytes())
    out = f.require_sealed_location(f.SEALED_ROOT / f"legacy-{kind}")
    evidence: dict[str, Any] = {
        "schema": f.PRECONDITION_SCHEMA,
        "name": kind,
        "passed": True,
        "code": pin["code"],
        "successor": pin["successors"][kind],
        "host_class": {"cpu": "legacy-host"},
        "size": sizes["size"],
        "declaration": pin["declaration"],
        "seeds": f.SEEDS,
        "cells": [
            {
                "a": a,
                "r": r,
                "equal": True,
                "result": True,
                "same_commit_size_successor_and_host_class": True,
                "unit_provenance_equal": True,
                "errors": {"frozen": None, "successor": None},
            }
            for a, r in module.PRECONDITION.cells
        ],
    }
    if damage == "false-pass":
        evidence["cells"][0]["same_commit_size_successor_and_host_class"] = False
    elif damage == "seeds":
        evidence["seeds"] = {**f.SEEDS, "root": 1}
    elif damage == "declaration":
        evidence["declaration"] = {}
    elif damage == "results":
        for cell in evidence["cells"]:
            cell["result"] = False
    elif damage == "errors":
        evidence["cells"][0]["errors"]["frozen"] = "ValueError('terminal')"
    path = out / f"{kind}-precondition.json"
    path.write_text(json.dumps(evidence))
    record: dict[str, Any] = {
        "schema": f"ic-study.v4-exploratory-{kind}-cell.v1",
        "sizes": sizes,
        "cell": module.cell_identity(0),
        "verification_sha256": {kind: hashlib.sha256(path.read_bytes()).hexdigest()},
        "provenance": {
            "code": pin["code"],
            "successor": pin["successors"][kind],
            "host_class": evidence["host_class"],
            "host": {"hostname": "old"},
        },
        "error": "ValueError('original')",
        "success": None,
        "attempts": [],
        "fit": None,
        "estimate": None,
        "rich_error": None,
        "rich_success": None,
        "timing": {
            "started_utc": "2026-09-29T00:00:00+00:00",
            "finished_utc": "2026-09-29T01:00:00+00:00",
            "cpu_seconds": 1.0,
            "wall_seconds": 1.0,
        },
    }
    if damage == "commit":
        record["provenance"]["code"] = {**pin["code"], "commit": "foreign"}
    elif damage == "hash":
        record["provenance"]["successor"] = {}
    elif damage == "identity":
        record["cell"]["index"] = 1
    elif damage == "verification":
        record["verification_sha256"][kind] = "bad"
    elif damage == "host":
        record["provenance"]["host_class"] = {"cpu": "foreign-host"}
    elif damage == "unknown-rich" and kind == "x7":
        record["error"] = None
        record["success"] = True
    records = [record]
    if damage == "success":
        record.update(error=None, success=True, attempts=["interior"])
        if kind == "x5":
            record["estimate"] = {
                "auc": 0.6,
                "interval_95": [0.55, 0.65],
                "interval_27729": [0.5, 0.7],
            }
        else:
            records = []
            monkeypatch.setattr(x7, "RESAMPLES", 20)
            points = np.linspace(0.5, 0.95, 9)
            monkeypatch.setattr(
                v4_curve,
                "score_uncertainty",
                lambda *_, **__: Uncertainty(
                    points,
                    np.full(9, 0.001),
                    np.full(9, 0.001),
                    np.tile(points, (2000, 1)),
                ),
            )
            for index in range(9):
                cell_record = json.loads(json.dumps(record))
                cell_record.update(
                    cell=x7.cell_identity(index), rich_success=True, rich_gap=None
                )
                seals = {}
                rng = np.random.default_rng(index)
                scores = (
                    rng.normal(size=(2000, 2)),
                    rng.normal(0.3 * index, 1, size=(2000, 2)),
                )
                for label, unit in (
                    ("x7", x7.x7_units()[0]),
                    ("x7-rich", x7.rich_units()[0]),
                ):
                    store = SealedStore(
                        f.private_directory(out / "stores" / unit.key / f"a{index}")
                    )
                    store.put_array("scores0", scores[0])
                    store.put_array("scores1", scores[1])
                    store.put_array("nuisance", np.zeros(2000))
                    store.put_json(
                        "result",
                        {"success": True, "attempts": [{"status": "interior"}]},
                    )
                    store.seal()
                    seals[label] = json.loads((store.root / "seal.json").read_bytes())[
                        "sha256"
                    ]
                cell_record["seal_sha256"] = seals
                records.append(cell_record)
    record_store = SealedStore(f.private_directory(out / kind))
    for index, member in enumerate(records):
        record_store.put_json(f.record_key(kind, index), member)
    before = {p.name: p.read_bytes() for p in (out / kind).glob("*.json")}
    if damage not in (None, "success") and not (
        damage == "unknown-rich" and kind == "x5"
    ):
        with pytest.raises(ValueError, match=r"legacy|Legacy"):
            x5.aggregate_x5(
                out, now=v4_curve.CLOSE
            ) if kind == "x5" else x7.aggregate_x7(out, now=v4_curve.CLOSE)
    else:
        result = (
            x5.aggregate_x5(out, now=v4_curve.CLOSE)
            if kind == "x5"
            else x7.aggregate_x7(out, now=v4_curve.CLOSE)
        )
        assert result["compatibility"]["source_commit"] == pin["code"]["commit"]
        assert result["compatibility"]["mode"] == "aggregate-only"
        assert result["code"] == [pin["code"]]
        assert {p.name: p.read_bytes() for p in (out / kind).glob("*.json")} == before
        if damage == "success":
            if kind == "x5":
                assert result["cells"][0]["reading"] == "intermediate"
            else:
                group = result["units"][0]
                assert group["reading"] == "close" and len(group["delta_auc"]) == 9
                assert all(
                    delta["interval"] == [0.0, 0.0] for delta in group["delta_auc"]
                )
        with pytest.raises(ValueError, match="manifest"):
            f.run_shard(module.analyses(out, {kind: "digest"})[kind], out, only=[0])


@pytest.mark.parametrize("kind", ["x3", "x4a", "x4b", "x5", "x6a", "x6b", "x7"])
def test_runner_rejects_mislabelled_cell_or_job(kind: str) -> None:
    from dataclasses import replace

    from ic_study.simulation import v4_exploratory_x3 as x3
    from ic_study.simulation import v4_exploratory_x4 as x4
    from ic_study.simulation import v4_exploratory_x5 as x5
    from ic_study.simulation import v4_exploratory_x6 as x6
    from ic_study.simulation import v4_exploratory_x7 as x7

    out = f.SEALED_ROOT / kind
    module = {"x3": x3, "x4a": x4, "x4b": x4, "x5": x5, "x6a": x6, "x6b": x6, "x7": x7}[
        kind
    ]
    analysis = module.analyses(out, {})[kind]
    record = _analysis([]).compute(0)
    record["sizes"] = analysis.sizes
    record["job" if kind.startswith("x6") else "cell"] = {"unit": "foreign", "index": 0}
    analysis = replace(analysis, compute=lambda _: record)
    with pytest.raises(ValueError, match="Incompatible record"):
        f.run_shard(analysis, out, only=[0])


def test_verification_copy_is_atomic_and_accepts_a_concurrent_winner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, target = tmp_path / "source.json", tmp_path / "target.json"
    source.write_bytes(b'{"verified": true}\n')
    original = os.link

    def interrupted(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("interrupted before publication")

    monkeypatch.setattr(os, "link", interrupted)
    with pytest.raises(RuntimeError, match="interrupted"):
        f.copy_verification(source, target)
    assert not target.exists()

    def winner(src: Any, dst: Any) -> None:
        target.write_bytes(source.read_bytes())
        original(src, dst)

    monkeypatch.setattr(os, "link", winner)
    f.copy_verification(source, target)
    assert target.read_bytes() == source.read_bytes()
    monkeypatch.setattr(os, "link", original)
    target.write_bytes(b"foreign")
    with pytest.raises(ValueError, match="different verification"):
        f.copy_verification(source, target)


@pytest.mark.parametrize("damage", ["hashes", "verification"])
def test_aggregate_rejects_omitted_provenance(
    damage: str, synthetic_analysis: Any
) -> None:
    out = f.SEALED_ROOT / "omitted"
    spec = _spec(_fake(0.0), _fake(0.0))
    analysis = synthetic_analysis(out, _analysis([]), (spec,))
    f.run_shard(analysis, out, only=[0])
    path = out / "manifest-x9.json"
    binding = json.loads(path.read_bytes())
    record_path = out / "x9/x9-0000.json"
    record = json.loads(record_path.read_bytes())
    if damage == "hashes":
        binding["successor"]["successor_sha256"] = {}
        record["provenance"]["successor"] = binding["successor"]
    else:
        binding["verification_required"] = False
        binding["verification_sha256"] = {}
        record["verification_sha256"] = {}
    path.write_text(json.dumps(binding))
    record_path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="manifest"):
        f.complete_records(
            out, "x9", 7, analysis.sizes, now=f.WINDOW_CLOSE, preconditions=(spec,)
        )


@pytest.mark.real_clock
def test_supervisor_stops_a_running_worker_and_preserves_checkpoints(
    tmp_path: Path,
) -> None:
    import sys
    import time
    from datetime import UTC, datetime

    checkpoint = tmp_path / "checkpoint.json"
    receipt = tmp_path / "cutoff.json"
    script = (
        "import pathlib, signal, time; "
        "signal.signal(signal.SIGALRM, lambda *_: None); "
        "signal.setitimer(signal.ITIMER_REAL, 3600); "
        f"pathlib.Path({str(checkpoint)!r}).write_text('durable'); "
        "time.sleep(30)"
    )
    start = time.monotonic()
    exit_code = f.supervise_until_close(
        [sys.executable, "-c", script],
        receipt,
        close=datetime.now(UTC) + timedelta(seconds=0.5),
    )
    assert exit_code == 124 and time.monotonic() - start < 3
    assert checkpoint.read_text() == "durable"
    result = json.loads(receipt.read_bytes())
    assert result["status"] == "incomplete" and result["scientific_failure"] is False


def test_supervisor_does_not_start_after_close(tmp_path: Path) -> None:
    receipt = tmp_path / "cutoff.json"
    assert (
        f.supervise_until_close(
            ["must-not-start"],
            receipt,
            close=f.WINDOW_CLOSE,
            now=lambda: f.WINDOW_CLOSE,
        )
        == 124
    )
    assert json.loads(receipt.read_bytes())["started"] is False


@pytest.mark.parametrize("command", ["run", "precondition"])
def test_cli_enforces_the_exploratory_cutoff(
    command: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ic_study.simulation import v4_exploratory_x6 as x6

    out = f.SEALED_ROOT / command
    monkeypatch.setattr(f, "WINDOW_CLOSE", f.WINDOW_CLOSE - timedelta(days=365))

    def forbidden_execution() -> None:
        pytest.fail("Closed command reached execution setup")

    monkeypatch.setattr(f, "require_clean_tree", forbidden_execution)
    arguments = [command, "--out", str(out)]
    arguments += (
        ["--kind", "x6a"]
        if command == "run"
        else ["--name", "x6-pop", "--cell", "0", "--side", "frozen"]
    )
    assert f.main(x6.SUITE, arguments) == 124
    receipts = list((out / "operational").glob("*.json"))
    assert (
        len(receipts) == 1 and json.loads(receipts[0].read_bytes())["started"] is False
    )
    assert not (out / "x6a").exists()


@pytest.mark.parametrize("kind", ["x5", "x7"])
def test_legacy_analyses_reject_multiple_cli_output_directories(
    kind: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from ic_study.simulation import v4_exploratory_x5 as x5
    from ic_study.simulation import v4_exploratory_x7 as x7

    suite = x5.SUITE if kind == "x5" else x7.SUITE
    with pytest.raises(SystemExit) as error:
        f.main(
            suite,
            [
                "aggregate",
                "--out",
                str(tmp_path / "first"),
                "--out",
                str(tmp_path / "second"),
                "--output",
                str(tmp_path / "union.json"),
            ],
        )
    assert error.value.code == 2
    assert f"{kind} aggregate accepts exactly one --out" in capsys.readouterr().err
    assert not (tmp_path / "union.json").exists()


def test_union_rejects_different_identity_bindings_between_valid_sources() -> None:
    outs = [f.SEALED_ROOT / name for name in ("first", "second")]
    for shard, out in enumerate(outs):
        analysis = _analysis([])
        f.run_shard(analysis, out, shard=shard, shards=2)
    binding_path = outs[1] / "manifest-x9.json"
    binding = json.loads(binding_path.read_bytes())
    binding["identity_key"] = "job"
    binding_path.write_text(json.dumps(binding))
    with pytest.raises(ValueError, match="Incompatible source manifests"):
        f.union_complete_records(outs, "x9", 7, {"size": TINY})


def test_union_marks_missing_and_late_units_after_the_close() -> None:
    outs = [f.SEALED_ROOT / name for name in ("first", "second")]
    for shard, out in enumerate(outs):
        f.run_shard(_analysis([]), out, shard=shard, shards=2)
    (outs[0] / "x9/x9-0006.json").unlink()
    path = outs[1] / "x9/x9-0005.json"
    record = json.loads(path.read_bytes())
    record["timing"]["finished_utc"] = (
        f.WINDOW_CLOSE + timedelta(seconds=1)
    ).isoformat()
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="Missing x9 units: \\[6\\]"):
        f.union_complete_records(outs, "x9", 7, {"size": TINY})
    records, incomplete, sources = f.union_complete_records(
        outs,
        "x9",
        7,
        {"size": TINY},
        now=f.WINDOW_CLOSE,
    )
    assert sorted(records) == [0, 1, 2, 3, 4]
    assert incomplete == [5, 6]
    assert [source["accepted_units"] for source in sources] == [3, 2]
