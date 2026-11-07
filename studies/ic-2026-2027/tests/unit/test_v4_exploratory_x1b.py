"""X1b successor: the frozen tier-1 curve with only the social generator swapped."""

from __future__ import annotations

import ast
import hashlib
import json
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import Uncertainty
from ic_study.simulation import v4_curve
from ic_study.simulation import v4_exploratory as x
from ic_study.simulation import v4_exploratory_x1b as b
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    Cell,
    PanelSource,
    SeedPlan,
)
from ic_study.simulation.v4_curve import VALID, ConfirmatorySeedPlan, curve_units
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


@pytest.mark.parametrize("attempt", [0, 1])
@pytest.mark.parametrize("phase", PHASES)
@pytest.mark.parametrize("share,reliability", [(0.03, 0.5), (0.9, 0.9)])
def test_original_generator_reproduces_panel_source_bitwise(
    share: float, reliability: float, phase: str, attempt: int
) -> None:
    cell = Cell(share, reliability)
    plan = b.ExploratorySeedPlan(block=RELIABILITIES.index(reliability))
    frozen = PanelSource(cell, plan, size=TINY)
    swapped = b.SwappedSource(cell, plan, generator=b.original_generator, size=TINY)
    for parameters in (None, np.array([0.8, 0.3])):
        expected = frozen.profiles(
            phase, 5, parameters=parameters, attempt=attempt, start=2
        )
        actual = swapped.profiles(
            phase, 5, parameters=parameters, attempt=attempt, start=2
        )
        assert same_bits(actual, expected)
    assert swapped.panels == frozen.panels == 10


def test_twin_generator_swaps_only_the_social_arm() -> None:
    cell = Cell(0.6, 0.7)
    plan = b.ExploratorySeedPlan(block=4)
    frozen = PanelSource(cell, plan, size=TINY)
    twin = b.SwappedSource(cell, plan, generator=b.twin_generator, size=TINY)
    null = np.array([0.85, 0.2])
    assert same_bits(
        twin.profiles("train", 3, parameters=null),
        frozen.profiles("train", 3, parameters=null),
    )
    social = twin.profiles("train", 3)
    assert not np.array_equal(social, frozen.profiles("train", 3))

    def seed(role: str, index: int) -> int:
        return x.derive_seed("x1b", 8, "train", role, index)

    expected = [
        x.observed_profile(
            x.mean_field_path(
                TINY, 11, seed("state", i), seed("xi", i), share=0.6, repulsion=0.25
            ).path,
            0.7,
            seed("mask", i),
            seed("error", i),
        )
        for i in (1, 3, 5)
    ]
    assert same_bits(social, np.stack(expected))


@pytest.mark.parametrize("phase", PHASES)
def test_twin_is_the_original_generator_without_drift(phase: str) -> None:
    cell = Cell(0.0, 0.8)
    plan = b.ExploratorySeedPlan(block=6)
    frozen = PanelSource(cell, plan, size=TINY)
    twin = b.SwappedSource(cell, plan, generator=b.twin_generator, size=TINY)
    assert same_bits(
        twin.profiles(phase, 4, attempt=1), frozen.profiles(phase, 4, attempt=1)
    )


def test_successor_is_limited_to_tier_one_cells_and_exploratory_seeds() -> None:
    plan = b.ExploratorySeedPlan(block=0)
    with pytest.raises(ValueError, match="tier-1"):
        b.SwappedSource(Cell(0.3, 0.5, steps=24), plan, generator=b.twin_generator)
    for frozen in (SeedPlan(), ConfirmatorySeedPlan()):
        with pytest.raises(ValueError, match="exploratory seeds only"):
            b.SwappedSource(Cell(0.3, 0.5), frozen, generator=b.twin_generator)
    with pytest.raises(ValueError, match="no gate"):
        b.ExploratorySeedPlan(block=0, gate=True).seed("train", "state", 0)
    with pytest.raises(ValueError, match="no gate"):
        plan.seed("train", "state", 0, attempt=2)
    with pytest.raises(ValueError, match="Invalid exploratory seed"):
        plan.seed("replicate", "state", 0)
    assert plan.seed("match", "state", 3, attempt=1) == x.derive_seed(
        "x1b", 1, "match", "state", 3
    )


def test_units_are_the_frozen_tier_one_units_with_exploratory_streams() -> None:
    frozen = [unit for unit in curve_units() if unit.tier == 1]
    units = b.x1b_units()
    assert [u.cells for u in units] == [u.cells for u in frozen]
    assert [u.key for u in units] == [f"x1b-{u.key}" for u in frozen]
    assert all(c == Cell(c.share, c.reliability) for u in units for c in u.cells)
    assert tuple(c.share for c in units[0].cells) == GRID
    for block, unit in enumerate(units):
        assert unit.cells[0].reliability == RELIABILITIES[block]
        assert unit.seeds == b.ExploratorySeedPlan(block=block)
        assert unit.seeds.seed("bootstrap", "state", 0) == x.derive_seed(
            "x1b", 2 * block, "bootstrap", "state", 0
        )
    assert len(b.x1b_cells()) == 81
    declared = [b.precondition_cell(k) for k in range(len(b.PRECONDITION_CELLS))]
    assert [unit.cells[i] for unit, i in declared] == [
        Cell(a, r) for a, r in b.PRECONDITION_CELLS
    ]


def test_successor_reproduces_the_frozen_cell_executor_bitwise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Declared precondition on a tiny panel: a = 0.03 and r = 0.5 fit at N = 60,
    so every stage down to the curve scores is compared, file by file. No
    material hashed on the way leads with a frozen v4 seed namespace."""
    captured: list[bytes] = []
    original = hashlib.sha256

    def recording(data: bytes = b"", **options: Any) -> Any:
        captured.append(bytes(data))
        return original(data, **options)

    monkeypatch.setattr(v4_curve, "PanelSource", partial(PanelSource, size=TINY))
    monkeypatch.setattr(hashlib, "sha256", recording)
    position = b.PRECONDITION_CELLS.index((0.03, 0.5))
    records = [b.precondition_side(tmp_path, position, s, size=TINY) for s in b.SIDES]
    monkeypatch.undo()
    assert [record["error"] for record in records] == [None, None]
    unit, index = b.precondition_cell(position)
    frozen, successor = (
        tmp_path / "precondition" / side / unit.key / f"a{index}" for side in b.SIDES
    )
    comparison = b.compare_cells(frozen, successor)
    assert comparison["equal"], comparison["differing_files"]
    assert {"result.json", "scores0.npy", "scores1.npy", "nuisance.npy"} <= set(
        comparison["sha256"]
    )
    assert {"eta-shifts.npy", "phases.jsonl", "provenance.json", "seal.json"} <= set(
        comparison["sha256"]
    )
    assert comparison["checkpoints"] > 1000
    assert json.loads((frozen / "result.json").read_text())["success"] is True
    assert not any(m.startswith(b"ic-detection-boundary-v4") for m in captured)
    assert any(m.startswith(f"{x.NAMESPACE}|{x.ROOT}|x1b|".encode()) for m in captured)


def test_twin_cell_without_drift_is_the_frozen_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(v4_curve, "PanelSource", partial(PanelSource, size=TINY))
    position = b.PRECONDITION_CELLS.index((0.0, 0.9))
    assert b.precondition_side(tmp_path, position, "frozen", size=TINY)["error"] is None
    unit, index = b.precondition_cell(position)
    record = b.x1b_cell(
        b.x1b_cells().index((unit, index)), tmp_path, "0" * 64, b.X1bSizes(TINY)
    )
    assert record["error"] is None and record["success"] is True
    assert record["attempts"] == ["anchor-exact"]
    comparison = b.compare_cells(
        tmp_path / "precondition" / "frozen" / unit.key / f"a{index}",
        tmp_path / "stores" / unit.key / f"a{index}",
    )
    assert comparison["differing_files"] == ["provenance.json", "seal.json"]
    assert comparison["access_sequence_equal"]


def _store(root: Path, value: float) -> Path:
    store = SealedStore(root)
    store.put_json("result", {"success": True})
    store.put_array("f" * 64, np.full((2, 5), value))
    store.seal()
    return store.root


def test_compare_cells_ignores_only_access_times(tmp_path: Path) -> None:
    left, right = _store(tmp_path / "left", 0.0), _store(tmp_path / "right", 0.0)
    same = b.compare_cells(left, right)
    assert same["equal"] and same["checkpoints"] == 1 and same["files"] == 3
    signed = b.compare_cells(left, _store(tmp_path / "signed", -0.0))
    assert not signed["equal"]
    assert signed["differing_files"] == ["f" * 64 + ".npy", "seal.json"]
    SealedStore(right).get_json("result")
    reread = b.compare_cells(left, right)
    assert not reread["equal"] and not reread["access_sequence_equal"]


def _executor(
    value: float, failing: frozenset[tuple[str, int]] = frozenset()
) -> Callable[..., None]:
    def execute(
        unit: b.ExploratoryUnit, index: int, directory: Path, *_: Any, **__: Any
    ) -> None:
        SealedStore(directory.parent)
        store = SealedStore(directory)
        store.put_array("f" * 64, np.full(3, value))
        if (unit.key, index) in failing:
            raise ValueError("ill-conditioned local profile")
        store.put_array("scores0", np.zeros((2000, 2)))
        store.put_array("scores1", np.ones((2000, 2)))
        store.put_array("nuisance", np.zeros(2000))
        store.put_json(
            "result", {"success": True, "attempts": [{"status": "interior"}]}
        )
        store.seal()

    return execute


def _verify(
    out: Path,
    monkeypatch: pytest.MonkeyPatch,
    frozen: Callable[..., None],
    successor: Callable[..., None],
) -> dict[str, Any]:
    monkeypatch.setattr(v4_curve, "execute_cell", frozen)
    monkeypatch.setattr(b, "execute_swapped_cell", successor)
    for position in range(len(b.PRECONDITION_CELLS)):
        for side in b.SIDES:
            b.precondition_side(out, position, side, size=TINY)
    return b.verify(out, size=TINY)


def test_verification_passes_only_on_identical_stores_with_two_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    same = _verify(tmp_path / "same", monkeypatch, _executor(0.0), _executor(0.0))
    assert same["passed"] and same["cells_reproduced_with_result"] == 4
    assert all(cell["unit_provenance_equal"] for cell in same["cells"])
    path = tmp_path / "verification.json"
    x.write_json(path, same)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert b.require_verification(path, TINY) == digest
    with pytest.raises(ValueError, match="passing precondition"):
        b.require_verification(path, x.SIZE)
    with pytest.raises(ValueError, match="passing precondition"):
        b.main(["x1b", "--out", str(tmp_path), "--verification", str(path)])

    flipped = _verify(tmp_path / "flip", monkeypatch, _executor(0.0), _executor(-0.0))
    assert not flipped["passed"]
    assert not any(cell["equal"] for cell in flipped["cells"])

    cells = [b.precondition_cell(k) for k in range(len(b.PRECONDITION_CELLS))]
    keys = [(unit.key, index) for unit, index in cells]
    one = _executor(0.0, frozenset(keys[1:2]))
    alone = _verify(tmp_path / "alone", monkeypatch, _executor(0.0), one)
    assert not alone["passed"] and not alone["cells"][1]["equal"]
    assert alone["cells"][1]["errors"]["successor"].startswith("ValueError")

    three = _executor(0.0, frozenset(keys[1:]))
    shared = _verify(tmp_path / "shared", monkeypatch, three, three)
    assert all(cell["equal"] for cell in shared["cells"])
    assert shared["cells_reproduced_with_result"] == 1 and not shared["passed"]


def test_twin_curves_resume_in_shards_and_use_the_frozen_band(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    broken = b.x1b_units()[1]
    monkeypatch.setattr(
        b, "execute_swapped_cell", _executor(0.0, frozenset({(broken.key, 3)}))
    )
    seeds: list[int] = []

    def uncertainty(
        left: np.ndarray, right: np.ndarray, nuisance: np.ndarray, *, seed: int
    ) -> Uncertainty:
        assert left.shape == right.shape == (2000, 2, 9)
        seeds.append(seed)
        point = np.linspace(0.5, 0.95, 9)
        return Uncertainty(
            point, np.full(9, 0.01), np.full(9, 0.01), np.tile(point, (2000, 1))
        )

    monkeypatch.setattr(v4_curve, "score_uncertainty", uncertainty)
    analysis = b.x1b_analysis(tmp_path, "0" * 64, b.X1bSizes(TINY))
    done = [x.run_shard(analysis, tmp_path, shard=k, shards=3) for k in range(3)]
    assert sorted(i for part in done for i in part) == list(range(81))
    assert x.run_shard(analysis, tmp_path, shard=0, shards=3) == []
    with pytest.raises(ValueError, match="requested sizes"):
        b.aggregate_x1b(tmp_path)
    result = b.aggregate_x1b(tmp_path, b.X1bSizes(TINY))
    rows = result["summary"]
    assert [row["r"] for row in rows] == list(RELIABILITIES)
    assert rows[1]["status"] == "cell errors" and rows[1]["first"] is None
    assert all(row["status"] == VALID for k, row in enumerate(rows) if k != 1)
    assert {row["first"] for k, row in enumerate(rows) if k != 1} == {0.03}
    assert seeds == [
        x.derive_seed("x1b", 2 * block, "bootstrap", "state", 0)
        for block in range(9)
        if block != 1
    ]
    assert result["verification_sha256"] == ["0" * 64]
    assert b.aggregate_x1b(tmp_path, b.X1bSizes(TINY))["curves"] == result["curves"]
    with pytest.raises(ValueError, match="provenance changed"):
        b.ensure_provenance(
            SealedStore(tmp_path / "stores" / broken.key),
            b.unit_provenance("x1b", "original", TINY),
        )


def test_successor_imports_only_frozen_study_modules_and_the_exploratory_one() -> None:
    tree = ast.parse(Path(b.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        if not node.module.startswith("ic_study"):
            continue
        if (STUDY / "src" / node.module.replace(".", "/")).is_dir():
            imported |= {f"{node.module}.{alias.name}" for alias in node.names}
        else:
            imported.add(node.module)
    freeze = json.loads((STUDY / x.FREEZE).read_text())["code"]
    assert "ic_study.simulation.v4_curve" in imported
    assert "ic_study.simulation.v4_exploratory" in imported
    for name in imported - {"ic_study.simulation.v4_exploratory"}:
        path = "src/" + name.replace(".", "/") + ".py"
        digest = hashlib.sha256((STUDY / path).read_bytes()).hexdigest()
        assert freeze[path] == digest
    assert b.successor_provenance()["frozen_python_mismatched"] == []
