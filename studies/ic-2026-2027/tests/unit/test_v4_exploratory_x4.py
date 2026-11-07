"""X4 successor: single-panel power, its frozen part and its precondition."""

from __future__ import annotations

import ast
import hashlib
import json
from collections.abc import Iterator
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ic_study.models.detection_panel_v4 import null
from ic_study.simulation import v4_exploratory as x12
from ic_study.simulation import v4_exploratory_x3 as x3
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation import v4_exploratory_x4 as x4
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    Cell,
    PanelSource,
    ValidatedFit,
    fit_cell,
    pipeline,
)
from ic_study.simulation.v4_store import SealedStore

STUDY = Path(__file__).resolve().parents[2]
TINY = 60
SMALL = x4.X4Sizes(
    size=TINY,
    train=40,
    check=80,
    test=20,
    single=4,
    analyst=16,
    nulls=19,
    auc_resamples=50,
    power_resamples=50,
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
    return f.SuccessorSeedPlan(block=RELIABILITIES.index(reliability), analysis="x4")


def test_test_and_analyst_panels_follow_the_frozen_layouts() -> None:
    cell, plan = Cell(0.3, 0.7), _plan(0.7)
    source = PanelSource(cell, plan, size=TINY)

    def seed(phase: str) -> f.SeedFn:
        return lambda role, index: f.derive_seed("x4", 8, phase, role, index)

    test = source.profiles("test", 4)
    expected = [
        f.frozen_social_profile(cell, TINY, seed("test"), 2 * j + 1, False)
        for j in range(4)
    ]
    assert same_bits(test, np.stack(expected))
    parameters = np.array([0.8, 0.3])
    analyst = source.profiles("single-fit", 2, parameters=parameters, start=3000)
    rows = []
    for j in (3000, 3001):
        draw = seed("single-fit")
        latent = null(
            TINY,
            11,
            draw("state", 2 * j),
            draw("null-state", 2 * j),
            family="B",
            phi=0.8,
            eta=0.3,
        )
        rows.append(
            x12.observed_profile(latent, 0.7, draw("mask", 2 * j), draw("error", 2 * j))
        )
    assert same_bits(analyst, np.stack(rows))
    nulls = source.profiles("single-null", 2, parameters=parameters, start=3000)
    assert not np.array_equal(nulls, analyst)


def test_fit_precondition_wrapper_is_the_first_frozen_fit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Declared x4-fit rule on a tiny panel through the shared harness: the X4
    fitting wrapper on the frozen coupled target and evaluation at M = 1,024
    writes frozen fit_cell's first-attempt record byte for byte."""
    spec = replace(x4.FIT, cells=((0.03, 0.5),))
    out = f.require_sealed_location(f.SEALED_ROOT / "fit")
    records = [f.precondition_side(spec, out, 0, side, size=TINY) for side in f.SIDES]
    assert [record["error"] for record in records] == [None, None]
    cell = f.verify(spec, out, size=TINY)["cells"][0]
    assert cell["equal"], cell["differing_files"]
    assert cell["result"] and cell["attempts"] == ["interior"]
    assert cell["unit"].startswith("x4-t1-")


def test_wrapper_family_limit_is_the_frozen_first_attempt() -> None:
    class Infeasible:
        cell = Cell(0.9, 0.5)

        def profiles(self, phase: str, count: int, **_: Any) -> np.ndarray:
            return np.full((count, 5), 0.6)

    frozen = fit_cell(Infeasible()).attempts[0].fit  # type: ignore[arg-type]
    target = np.full((1024, 2), 0.6)
    wrapped = x4.single_panel_fit(Cell(0.9, 0.5), target, lambda phi, eta: target)
    assert frozen.status == wrapped.status == "family-limit-upper"
    for key in x3.FIT_ARRAYS:
        assert same_bits(getattr(frozen, key), getattr(wrapped, key))
    assert (frozen.evaluations, frozen.fitted_moments) == (0, 2)
    assert (wrapped.evaluations, wrapped.fitted_moments) == (0, 2)


def test_frozen_part_is_the_frozen_pipeline_code_path(tmp_path: Path) -> None:
    """At an anchor-exact tiny cell the frozen pipeline and the X4 frozen part
    read the same checkpoints and give the same scores bit for bit; the X4 part
    adds only its test phase."""
    cell, plan = Cell(0.0, 0.9), _plan(0.9)
    store = SealedStore(tmp_path / "cell")
    result = pipeline(
        PanelSource(cell, plan, size=TINY, store=store), compute_uncertainty=False
    )
    before = {p.name for p in store.root.glob("*.npy")}
    sizes = replace(x4.DECLARED, size=TINY, test=64)
    frozen = x4.reference(cell, plan, store, sizes)
    added = {p.name for p in store.root.glob("*.npy")} - before
    assert result.scores0 is not None and result.scores1 is not None
    assert frozen.null_check is not None and frozen.social_check is not None
    assert same_bits(frozen.null_check, result.scores0.ravel())
    assert same_bits(frozen.social_check, result.scores1.ravel())
    phases = [
        json.loads(line)["phase"]
        for line in (store.root / "phases.jsonl").read_text().splitlines()
    ]
    assert phases[-len(added) :] == ["test"] * len(added) and len(added) == 2
    assert frozen.fit.attempts[0].fit.status == "anchor-exact"


def test_power_statistics_follow_the_declared_rules() -> None:
    assert x4.normal_power(0.5) == pytest.approx(0.05, abs=1e-4)
    about = [x4.normal_power(a) for a in (0.6, 0.7, 0.8)]
    assert about == pytest.approx([0.10, 0.18, 0.33], abs=0.01)
    assert x4.normal_power(1.0) == 1.0 and x4.normal_power(0.0) == 0.0
    scores = np.arange(1, 101, dtype=float)
    assert x4.critical_score(scores) == pytest.approx(95.05)
    decisions = np.array([True, False] * 10)
    draws = x4.rate_bootstrap([decisions, ~decisions], seed=3, resamples=40)
    assert np.all(draws.sum(1) == 1) and np.all(draws[:, 0] == 0.5)
    shifted = x4.rate_bootstrap([decisions], seed=3, resamples=40)
    assert same_bits(shifted[:, 0], draws[:, 0])
    with pytest.raises(ValueError, match="same test networks"):
        x4.rate_bootstrap([decisions, decisions[:-2]], seed=3, resamples=2)


def _single(panel: int, status: str, reject: bool) -> dict[str, Any]:
    success = status == "interior"
    return {
        "panel": panel,
        "status": status,
        "success": success,
        "reject": reject and success,
        "p_value": 0.05 if success else None,
    }


def test_single_panel_failures_are_non_rejections_and_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[int] = []
    outcomes = [
        ("interior", True),
        ("budget", True),
        ("interior", False),
        ("interior", True),
    ]

    def single(
        cell: Cell, seeds: Any, frozen: x4.Reference, panel: int, sizes: Any
    ) -> dict[str, Any]:
        calls.append(panel)
        return _single(panel, *outcomes[panel])

    monkeypatch.setattr(x4, "single_panel", single)
    frozen = x4.Reference(
        ValidatedFit(()),
        null_check=np.linspace(0, 2, 100),
        test_scores=np.array([3.0, 0.0, 3.0, 0.0]),
    )
    store = SealedStore(tmp_path / "cell")
    sizes = replace(SMALL, single=4)
    result = x4.x4b_statistics(Cell(0.3, 0.7), _plan(0.7), frozen, store, sizes)
    assert calls == [0, 1, 2, 3]
    assert result["power_pu"] == 0.5 and result["fit_failures"] == 1
    assert result["failure_rate"] == 0.25
    assert result["power_pu_without_failures"] == pytest.approx(2 / 3)
    assert result["power_or_paired"] == 0.5 and result["difference"] == 0.0
    assert result["fit_statuses"] == {"interior": 3, "budget": 1}
    again = x4.x4b_statistics(Cell(0.3, 0.7), _plan(0.7), frozen, store, sizes)
    assert calls == [0, 1, 2, 3] and again == result


def test_cells_run_end_to_end_at_a_tiny_anchor_exact_cell() -> None:
    """X4a and X4b at a = 0 on tiny sizes: the frozen part, the oracle
    decisions, the single-panel fits and the p-value grid."""
    out = f.require_sealed_location(f.SEALED_ROOT / "cells")
    index = next(
        k for k, (u, i) in enumerate(x4.SINGLE_CELLS) if u.cells[i] == Cell(0.0, 0.9)
    )
    b_record = x4.x4b_cell(index, out, {"x4-fit": "0" * 64}, SMALL)
    json.dumps(b_record, allow_nan=False)
    assert b_record["error"] is None and b_record["success"] is True
    assert b_record["attempts"][0] == "anchor-exact"
    assert b_record["sizes"] == asdict(SMALL) and b_record["seal_sha256"]
    statistics = b_record["x4b"]
    assert len(statistics["panels"]) == 4 and statistics["test_panels"] == 4
    grid = {(1 + k) / 20 for k in range(20)}
    for panel in statistics["panels"]:
        assert panel["p_value"] is None or panel["p_value"] in grid
        assert panel["reject"] == (
            panel["p_value"] is not None and panel["p_value"] <= 0.05
        )
    a_index = x4.CELLS.index(x4.SINGLE_CELLS[index])
    a_record = x4.x4a_cell(a_index, out, {"x4-fit": "0" * 64}, SMALL)
    json.dumps(a_record, allow_nan=False)
    oracle = a_record["x4a"]
    assert oracle["test_panels"] == 20 and 0 <= oracle["power_or"] <= 1
    assert len(oracle["power_or_interval_95"]) == 2
    assert a_record["seeds"]["bootstrap_power_or"] == f.derive_seed(
        "x4", 16, "bootstrap", "resample", 1
    )


def test_cells_units_and_the_precondition_are_the_declared_ones() -> None:
    assert len(x4.CELLS) == 81 and len(x4.SINGLE_CELLS) == 27
    assert [u.cells[i].share for u, i in x4.CELLS[:9]] == list(GRID)
    assert {u.cells[i].reliability for u, i in x4.SINGLE_CELLS} == {0.5, 0.7, 0.9}
    assert all(u.key.startswith("x4-t1-") for u, _ in x4.CELLS)
    assert x4.FIT.cells == ((0.03, 0.5), (0.3, 0.6))
    assert x4.FIT.frozen is x3.frozen_first_fit
    assert x4.SUITE.sealed and x4.SUITE.kinds == ("x4a", "x4b")
    assert [spec.name for spec in x4.SUITE.preconditions] == ["x4-fit"]
    assert asdict(x4.DECLARED) == {
        "size": 10626,
        "train": 2000,
        "check": 4000,
        "test": 1000,
        "single": 200,
        "analyst": 256,
        "nulls": 199,
        "auc_resamples": 1000,
        "power_resamples": 2000,
    }
    analyses = x4.analyses(f.SEALED_ROOT, {})
    assert (analyses["x4a"].total, analyses["x4b"].total) == (81, 27)


def _record(kind: str, a: float, r: float, **statistics: Any) -> dict[str, Any]:
    return {
        "cell": {"a": a, "r": r},
        "sizes": asdict(x4.DECLARED),
        "error": None,
        kind: statistics,
        "timing": {
            "started_utc": x12.utc_now(),
            "finished_utc": x12.utc_now(),
            "wall_seconds": 1.0,
            "cpu_seconds": 1.0,
        },
        "provenance": {"code": {"commit": "c"}, "host": {"hostname": "h"}},
    }


@pytest.mark.parametrize("calibration", ["liberal", "conservative", "calibrated", None])
def test_declared_readings_and_the_sealed_aggregate(
    calibration: str | None, synthetic_analysis: Any
) -> None:
    assert x4.size_reading([0.03, 0.07]) == "calibrated"
    assert x4.size_reading([0.051, 0.09]) == "liberal"
    assert x4.size_reading([0.01, 0.049]) == "conservative"
    assert x4.normal_reading(0.2, [0.1, 0.3]) == "describes"
    assert x4.normal_reading(0.4, [0.1, 0.3]) == "overstates"
    assert x4.single_panel_reading([-0.2, -0.01]) == "removes-power"
    assert x4.single_panel_reading([-0.05, 0.05]) == "no-material-change"
    assert x4.single_panel_reading([-0.06, 0.02]) == "inconclusive"
    out = f.require_sealed_location(f.SEALED_ROOT / "aggregate")
    for kind, cells in (("x4a", x4.CELLS), ("x4b", x4.SINGLE_CELLS)):
        records = []
        for index, (unit, position) in enumerate(cells):
            cell = unit.cells[position]
            statistics = (
                {
                    "auc_ref": 0.7,
                    "normal_theory_power": {"at_auc_ref": 0.18},
                    "power_or_interval_95": [0.1, 0.3],
                }
                if kind == "x4a"
                else {
                    "power_pu_interval_95": [0.06, 0.12],
                    "difference_interval_95": [-0.2, -0.01],
                }
            )
            if cell.share == 0 and kind == "x4b":
                if calibration is None:
                    statistics = {}
                else:
                    statistics["power_pu_interval_95"] = {
                        "liberal": [0.06, 0.12],
                        "conservative": [0.01, 0.04],
                        "calibrated": [0.03, 0.07],
                    }[calibration]
            record = _record(kind, cell.share, cell.reliability, **statistics)
            record["cell"] = x3.cell_identity(index, unit, position)
            records.append(record)
        f.run_shard(
            synthetic_analysis(
                out,
                f.Analysis(kind, len(cells), asdict(x4.DECLARED), records.__getitem__),
                x4.SUITE.preconditions,
            ),
            out,
        )
    if not f.released():
        with pytest.raises(ValueError, match="Sealed until"):
            x4.aggregate([out])
    f.private_directory(f.RELEASE_RECORD.parent)
    f.RELEASE_RECORD.write_text("{}")
    result = x4.aggregate([out])
    summary = result["summary"]
    assert summary["size_at_a0"]["x4b"] == {
        "0.5": calibration,
        "0.7": calibration,
        "0.9": calibration,
    }
    assert summary["normal_theory_in_auc_range"] == {
        "range": [0.55, 0.95],
        "describes": 81,
    }
    expected = {"margin": 0.05}
    if calibration in ("calibrated", "conservative"):
        expected["removes-power"] = 27
    assert summary["single_panel_effect"] == expected
    assert {c["size_flag"] for c in result["x4b"]} == {calibration}
    if calibration in ("liberal", None):
        assert all(c["single_panel_reading"] is None for c in result["x4b"])
        assert all(c["quantity"] == "rejection-rate" for c in result["x4b"])
        assert result["x4b"][1]["x4b"]["difference_interval_95"] == [-0.2, -0.01]
    if calibration == "conservative":
        assert all(c["quantity"] == "power-lower-bound" for c in result["x4b"])
    assert result["incomplete"] == {"x4a": [], "x4b": []}


def test_module_imports_only_frozen_modules_the_foundation_x1_and_x3() -> None:
    tree = ast.parse(Path(x4.__file__).read_text())
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
        "ic_study.simulation.v4_exploratory_x3",
        "ic_study.simulation.v4_exploratory_x3x7",
    }
    assert {"ic_study.simulation.v4_exploratory_x3"} <= imported
    for name in imported - reused:
        path = "src/" + name.replace(".", "/") + ".py"
        assert freeze[path] == hashlib.sha256((STUDY / path).read_bytes()).hexdigest()
    provenance = f.successor_provenance(x4.MODULES)
    assert provenance["frozen_python_mismatched"] == []
    assert {
        "src/ic_study/simulation/v4_exploratory_x3.py",
        "src/ic_study/simulation/v4_exploratory_x4.py",
    } <= set(provenance["successor_sha256"])


def test_aggregate_unites_disjoint_hosts_for_both_kinds(
    synthetic_analysis: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    outs = [f.SEALED_ROOT / name for name in ("icllm", "homelab")]
    for shard, out in enumerate(outs):
        host = {"cpu": out.name, "system": "synthetic", "environment": "locked"}
        monkeypatch.setattr(f, "host_class", lambda host=host: host)
        for kind, cells in (("x4a", x4.CELLS), ("x4b", x4.SINGLE_CELLS)):
            records = []
            for index, (unit, position) in enumerate(cells):
                cell = unit.cells[position]
                statistics = (
                    {
                        "auc_ref": 0.7,
                        "normal_theory_power": {"at_auc_ref": 0.18},
                        "power_or_interval_95": [0.1, 0.3],
                    }
                    if kind == "x4a"
                    else {
                        "power_pu_interval_95": [0.03, 0.07],
                        "difference_interval_95": [-0.02, 0.02],
                    }
                )
                record = _record(kind, cell.share, cell.reliability, **statistics)
                record["cell"] = x3.cell_identity(index, unit, position)
                records.append(record)
            analysis = f.Analysis(
                kind,
                len(cells),
                asdict(x4.DECLARED),
                records.__getitem__,
                identities=tuple(
                    x3.cell_identity(i, *cell) for i, cell in enumerate(cells)
                ),
            )
            f.run_shard(
                synthetic_analysis(out, analysis, x4.SUITE.preconditions),
                out,
                shard=shard,
                shards=2,
            )
    f.private_directory(f.RELEASE_RECORD.parent)
    f.RELEASE_RECORD.write_text("{}")
    result = x4.aggregate(outs)
    assert result["incomplete"] == {"x4a": [], "x4b": []}
    assert len(result["x4a"]) == 81 and len(result["x4b"]) == 27
    assert [source["accepted_units"] for source in result["sources"]] == [55, 53]
    assert result["summary"]["single_panel_effect"] == {
        "margin": 0.05,
        "no-material-change": 27,
    }
