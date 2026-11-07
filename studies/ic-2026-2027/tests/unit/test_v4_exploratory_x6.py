"""X6 interior coverage: units, queue, T_pop precondition, records and readings."""

from __future__ import annotations

import ast
import hashlib
import json
import math
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import asdict, replace
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ic_study.analysis.detection_boundary import auc
from ic_study.analysis.redesign import fit_discriminant
from ic_study.simulation import detection_v4, v4_curve
from ic_study.simulation import v4_exploratory as x12
from ic_study.simulation import v4_exploratory_x3x7 as f
from ic_study.simulation import v4_exploratory_x6 as x6
from ic_study.simulation.detection_v4 import GRID, Cell, PanelSource, fit_cell
from ic_study.simulation.v4_curve import curve_units
from ic_study.simulation.v4_store import SealedStore

STUDY = Path(__file__).resolve().parents[2]
TINY = 60
SMALL = x6.X6Sizes(
    size=TINY,
    repetitions=2,
    truth_pipelines=2,
    population_pairs=1024,
    population_trainings=2,
    population_train=8,
    population_check=16,
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


def test_units_blocks_and_streams_follow_the_declaration() -> None:
    frozen = next(
        u for u in curve_units() if u.tier == 1 and u.cells[0].reliability == 0.7
    )
    assert x6.row(0.7) == frozen.cells
    assert tuple((a, 0.7) for a in GRID[1:]) == x6.X6A_TRUTH_CELLS
    assert [x6.cell_number(0.03, r) for r in (0.5, 0.7, 0.9)] == [4, 40, 76]
    repetition, index = x6.Job("repetition", None, 7).unit()
    assert index is None and repetition.cells == frozen.cells
    assert repetition.seeds == f.SuccessorSeedPlan(block=7, analysis="x6-rep")
    assert repetition.seeds.seed("match", "state", 1, attempt=1) == f.derive_seed(
        "x6-rep", 15, "match", "state", 1
    )
    single, index = x6.Job("repetition", (0.03, 0.9), 199).unit()
    assert index == GRID.index(0.03) and single.cells == x6.row(0.9)
    assert single.seeds.seed("check", "mask", 3) == f.derive_seed(
        "x6b-rep", 2 * (1000 * 76 + 199), "check", "mask", 3
    )
    truth, index = x6.Job("truth", (0.3, 0.7), 99).unit()
    assert index == GRID.index(0.3)
    assert truth.seeds.seed("train", "error", 0, attempt=1) == f.derive_seed(
        "x6-truth", 2 * (1000 * 42 + 99) + 1, "train", "error", 0
    )
    population, index = x6.Job("pop", (0.03, 0.5)).unit()
    assert index == 0 and population.cells == (Cell(0.03, 0.5),)
    assert population.seeds.seed("train", "state", 4001) == f.derive_seed(
        "x6-pop", 8, "train", "state", 4001
    )
    units = [job.unit()[0] for job in x6.queue("x6a") + x6.queue("x6b")]
    assert len(units) == 8 + 200 + 800 + 2 + 400 + 200
    assert len({unit.key for unit in units}) == len(units)
    assert len({(unit.analysis, unit.block) for unit in units}) == len(units)
    assert {unit.analysis for unit in units} == {
        "x6-rep",
        "x6b-rep",
        "x6-truth",
        "x6-pop",
    }


@pytest.mark.parametrize("analysis", ["x6a", "x6b"])
def test_queue_puts_population_cells_first_and_paces_the_rest(analysis: str) -> None:
    cells = x6.X6A_TRUTH_CELLS if analysis == "x6a" else x6.X6B_CELLS
    jobs = x6.queue(analysis)
    assert jobs[: len(cells)] == tuple(x6.Job("pop", cell) for cell in cells)
    body = jobs[len(cells) :]
    repetitions = 200 if analysis == "x6a" else 200 * len(cells)
    truths = 100 * len(cells)
    expected = [x6.Job("truth", c, k) for k in range(100) for c in cells]
    expected += (
        [x6.Job("repetition", None, i) for i in range(200)]
        if analysis == "x6a"
        else [x6.Job("repetition", c, i) for i in range(200) for c in cells]
    )
    assert Counter(body) == Counter(expected)
    done: Counter[str] = Counter()
    per_cell: Counter[tuple[float, float] | None] = Counter()
    for job in body:
        done[job.kind] += 1
        if job.kind == "truth":
            per_cell[job.cell] += 1
            assert job.number == per_cell[job.cell] - 1
            assert max(per_cell.values()) - min(per_cell[c] for c in cells) <= 1
        gap = done["repetition"] * truths - done["truth"] * repetitions
        assert abs(gap) <= max(repetitions, truths)
    with pytest.raises(ValueError, match="x6a and x6b"):
        x6.queue("x6c")


def test_population_fit_reproduces_the_first_frozen_attempt() -> None:
    """Both precondition sides at N = 60 on (0.03, 0.70): the T_pop wrapper at
    M = 1,024 against frozen fit_cell, through the harness and its verify."""
    spec = replace(x6.PRECONDITION, name="x6-pop-tiny", cells=x6.PRECONDITION_CELLS[:1])
    out = f.require_sealed_location(f.SEALED_ROOT / "tiny")
    records = [f.precondition_side(spec, out, 0, side, size=TINY) for side in f.SIDES]
    assert [record["error"] for record in records] == [None, None]
    result = f.verify(spec, out, size=TINY)
    cell = result["cells"][0]
    assert cell["equal"] and cell["result"], cell["differing_files"]
    assert set(cell["sha256"]) == {
        *(f"{name}.npy" for name in x6.FIT_ARRAYS),
        "result.json",
        "seal.json",
    }
    assert not result["passed"] and result["cells_reproduced_with_result"] == 1
    successor = spec.directory(out, "successor", 0)
    assert (successor.parent / f"{successor.name}-panels" / "seal.json").exists()
    record = json.loads((spec.directory(out, "frozen", 0) / "result.json").read_text())
    assert record["attempts"][0]["matching_pairs"] == 1024
    assert record["attempts"][0]["validation_pass"] is None


def test_population_fit_follows_the_frozen_family_limit_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    unit, _ = x6.Job("pop", (0.3, 0.7)).unit()
    for module in (detection_v4, x6):
        monkeypatch.setattr(module, "feasible_lag1", lambda *_, **__: False)
    frozen = fit_cell(PanelSource(unit.cells[0], unit.seeds, size=TINY)).attempts
    ours = x6.population_fit(PanelSource(unit.cells[0], unit.seeds, size=TINY), 1024)
    assert len(frozen) == 1 and frozen[0].count == 1024
    assert frozen[0].fit.status == ours.status
    assert ours.status.startswith("family-limit") and not ours.success
    for name in x6.FIT_ARRAYS:
        assert same_bits(getattr(frozen[0].fit, name), getattr(ours, name))
    assert (ours.evaluations, ours.fitted_moments) == (0, 2)


def test_population_trainings_use_disjoint_frozen_panels_and_checkpoints(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    unit, _ = x6.Job("pop", (0.03, 0.7)).unit()
    cell, theta = unit.cells[0], np.array([0.84, 0.05])
    store = SealedStore(tmp_path / "trainings")
    values = x6.population_trainings(cell, unit.seeds, theta, store, SMALL)
    source = PanelSource(cell, unit.seeds, size=TINY)
    train0 = source.profiles("train", 8, parameters=theta, start=8)[:, 2:5]
    train1 = source.profiles("train", 8, start=8)[:, 2:5]
    model = fit_discriminant(np.concatenate([train0, train1]), np.repeat([0, 1], 8))
    null = model.score(source.profiles("check", 16, parameters=theta, start=16)[:, 2:5])
    social = model.score(source.profiles("check", 16, start=16)[:, 2:5])
    assert values[1] == auc(null, social) and len(values) == 2
    assert (store.root / "seal.json").exists()
    monkeypatch.setattr(x6, "fit_discriminant", None)
    assert x6.population_trainings(cell, unit.seeds, theta, store, SMALL) == values


def test_population_unit_fits_once_and_resumes_from_its_stores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    out = f.require_sealed_location(f.SEALED_ROOT / "pop")
    job = x6.Job("pop", (0.03, 0.7))
    first = x6.run_job(job, out, {"x6-pop": "digest"}, SMALL)
    assert first["error"] is None and first["fit"]["matching_pairs"] == 1024
    assert first["success"] is True and len(first["trainings"]) == 2
    assert first["fit_resumed"] is False and first["fit_seal_sha256"]
    stores = out / "stores" / "x6-pop-c40"
    assert {path.name for path in stores.iterdir()} == {
        "provenance.json",
        "access.jsonl",
        "fit",
        "fit-panels",
        "trainings",
    }
    monkeypatch.setattr(x6, "profile_match", None)
    monkeypatch.setattr(x6, "fit_discriminant", None)
    again = x6.run_job(job, out, {"x6-pop": "digest"}, SMALL)
    assert again["fit_resumed"] is True
    assert {k: v for k, v in again.items() if k not in {"timing", "fit_resumed"}} == {
        k: v for k, v in first.items() if k not in {"timing", "fit_resumed"}
    }


def _synthetic(
    gaps: frozenset[int] = frozenset(), failing: frozenset[int] = frozenset()
) -> Callable[[f.SuccessorUnit, int, Path], None]:
    """Stands in for frozen execute_cell: a sealed cell store with its layout."""

    def execute(unit: f.SuccessorUnit, index: int, directory: Path) -> None:
        store = SealedStore(directory)
        if index in failing:
            raise ValueError("ill-conditioned local profile")
        rng = np.random.default_rng([unit.block, index])
        success = index not in gaps
        status = "interior" if success else "non-monotone-profile"
        attempt = {"status": status, "residual_se_units": [0.2, -0.1]}
        store.put_json(
            "result",
            {
                "success": success,
                "attempts": [{**attempt, "amplification": 0.3 if success else None}],
                "mean_shift": [0.001 * index] if success else [],
            },
        )
        if success:
            store.put_array("scores0", rng.normal(size=(2000, 2)))
            store.put_array("scores1", rng.normal(0.1 * index, 1, size=(2000, 2)))
            store.put_array("nuisance", rng.normal(0, 0.003, size=2000))
        store.seal()

    return execute


def _pointwise(point: float, se: float) -> list[float]:
    epsilon = 1 / 4000
    p = min(max(point, epsilon), 1 - epsilon)
    logit, scale = math.log(p / (1 - p)), max(se, epsilon) / (p * (1 - p))
    return [
        1 / (1 + math.exp(-logit + sign * x6.POINTWISE_CRITICAL * scale))
        for sign in (1, -1)
    ]


def test_x6a_repetition_recomputes_the_frozen_curve_intervals(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    out = f.require_sealed_location(f.SEALED_ROOT / "units")
    gaps = frozenset({1, 3, 5, 8})
    monkeypatch.setattr(v4_curve, "execute_cell", _synthetic(gaps))
    analysis = x6.analyses(out, {"x6-pop": "digest"}, SMALL)["x6a"]
    position = x6.queue("x6a", SMALL).index(x6.Job("repetition", None, 1))
    assert f.run_shard(analysis, out, only=[position]) == [position]
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [set(line) for line in lines] == [
        {"kind", "unit", "status", "wall_seconds", "cpu_seconds"}
    ]
    record: dict[str, Any] | None = SealedStore(out / "x6a").get_json(
        f.record_key("x6a", position)
    )
    assert record is not None
    assert record["job"]["seed_analysis"] == "x6-rep" and record["job"]["block"] == 1
    curve = record["curve"]
    assert curve["band_reproduced"] and not curve["band_complete"]
    assert curve["gap_count"] == 4 and record["success"] is False
    assert record["attempts"].count("non-monotone-profile") == 4
    stored = SealedStore(out / "stores" / "x6a-rep-001").get_json("curve")
    assert stored is not None and stored["lower"] == [
        cell["band"][0] for cell in record["cells"] if cell["success"]
    ]
    assert (out / "stores" / "x6a-rep-001" / "seal.json").exists()
    for index, cell in enumerate(record["cells"]):
        assert cell["a"] == GRID[index] and cell["success"] is (index not in gaps)
        if cell["success"]:
            assert cell["pointwise"] == pytest.approx(
                _pointwise(cell["point"], cell["se"]), abs=1e-12
            )
            assert cell["band"][0] <= cell["pointwise"][0]
            assert cell["mean_shift"] == pytest.approx(0.001 * index)
        else:
            assert "pointwise" not in cell and cell["result"]
    monkeypatch.setattr(v4_curve, "execute_cell", _synthetic(gaps, frozenset({2})))
    failed = x6.run_job(x6.Job("repetition", None, 0), out, {"x6-pop": "digest"}, SMALL)
    assert failed["curve"] is None and failed["success"] is None
    assert failed["error"].startswith("0.003: ValueError")
    assert not failed["cells"][2]["result"]
    assert all(cell["band"] is None for cell in failed["cells"] if cell["success"])
    assert not (out / "stores" / "x6a-rep-000" / "curve.json").exists()


def test_truth_pipeline_and_x6b_repetition_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    out = f.require_sealed_location(f.SEALED_ROOT / "cells")
    monkeypatch.setattr(v4_curve, "execute_cell", _synthetic())
    truth = x6.run_job(x6.Job("truth", (0.3, 0.7), 1), out, {}, SMALL)
    store = SealedStore(out / "stores" / "x6-truth-c42-k001" / "a6")
    null, social = store.get_array("scores0"), store.get_array("scores1")
    assert null is not None and social is not None
    assert truth["cells"][0]["point"] == auc(null.ravel(), social.ravel())
    assert "pointwise" not in truth["cells"][0] and truth["job"]["block"] == 42001
    single = x6.run_job(x6.Job("repetition", (0.03, 0.5), 0), out, {}, SMALL)
    cell = single["cells"][0]
    assert cell["pointwise"] == pytest.approx(
        _pointwise(cell["point"], cell["se"]), abs=1e-12
    )
    assert cell["band"] is None and single["job"]["seed_analysis"] == "x6b-rep"
    monkeypatch.setattr(v4_curve, "execute_cell", _synthetic(frozenset({4})))
    gap = x6.run_job(x6.Job("repetition", (0.03, 0.9), 0), out, {}, SMALL)
    assert gap["success"] is False and "point" not in gap["cells"][0]


def test_x6b_repetition_runs_the_frozen_executor_on_x6b_streams(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A complete frozen cell at N = 60; every seed material hashed while it
    runs leads with this namespace and the x6b-rep analysis."""
    captured: list[bytes] = []
    original = hashlib.sha256

    def recording(data: bytes = b"", **options: Any) -> Any:
        captured.append(bytes(data))
        return original(data, **options)

    out = f.require_sealed_location(f.SEALED_ROOT / "frozen")
    monkeypatch.setattr(v4_curve, "PanelSource", partial(PanelSource, size=TINY))
    monkeypatch.setattr(hashlib, "sha256", recording)
    record = x6.run_job(x6.Job("repetition", (0.03, 0.5), 1), out, {}, SMALL)
    monkeypatch.undo()
    seeds = [
        m for m in captured if b"|" in m and b"\n" not in m and not m.startswith(b"{")
    ]
    assert seeds and all(
        m.startswith(f"{f.NAMESPACE}|{f.ROOT}|x6b-rep|{2 * 4001}|".encode())
        or m.startswith(f"{f.NAMESPACE}|{f.ROOT}|x6b-rep|{2 * 4001 + 1}|".encode())
        for m in seeds
    )
    assert record["error"] is None and record["cells"][0]["result"]
    directory = out / "stores" / "x6b-rep-c04-001" / "a4"
    assert {"result.json", "seal.json", "provenance.json", "worker-output.log"} <= {
        path.name for path in directory.iterdir()
    }
    cell = record["cells"][0]
    assert record["success"] is True and cell["attempts"] == ["interior"]
    assert 0 < cell["point"] < 1 and cell["se"] > 0 and cell["band"] is None
    assert (directory / "scores0.npy").exists()


def _row(point: float, lower: float, upper: float, band: bool) -> dict[str, Any]:
    return {
        "error": None,
        "result": True,
        "success": True,
        "attempts": ["interior"],
        "retry": False,
        "mean_shift": 0.001,
        "residual_se_units": [0.5, -0.5],
        "amplification": 0.2,
        "point": point,
        "se": 0.02,
        "pointwise": [lower, upper],
        "band": [lower - 0.01, upper + 0.01] if band else None,
    }


def _records(sizes: x6.X6Sizes) -> dict[str, list[dict[str, Any]]]:
    """Synthetic records: truths 0.6 (T_pop 0.61) at every cell; repetition i
    covers T_D1 unless i % 10 == 9, and repetition 0 has a gap at a = 0.9."""
    records: dict[str, list[dict[str, Any]]] = {}
    for name in ("x6a", "x6b"):
        records[name] = []
        for job in x6.queue(name, sizes):
            body: dict[str, Any] = {"error": None, "success": True, "attempts": []}
            if job.kind == "pop":
                body.update(trainings=[0.6, 0.62], fit={"status": "interior"})
            elif job.kind == "truth":
                body["cells"] = [
                    {"success": True, "retry": job.number == 0, "point": 0.6}
                ]
            else:
                miss = job.number % 10 == 9
                cells = [
                    _row(
                        0.5 if a == 0 else 0.6,
                        0.45 if a == 0 else 0.62 if miss else 0.55,
                        0.55 if a == 0 else 0.7,
                        job.cell is None,
                    )
                    for a in (GRID if job.cell is None else (job.cell[0],))
                ]
                if job.cell is None and job.number == 0:
                    cells[-1] = {**cells[-1], "success": False}
                body["cells"] = cells
                body["curve"] = None
                if job.cell is None:
                    body["curve"] = {
                        "band_complete": job.number != 0,
                        "empirical_exceeds_floor": job.number % 4 == 0,
                        "band_reproduced": True,
                    }
            records[name].append(
                {
                    "job": job.describe(),
                    "sizes": asdict(sizes),
                    "verification_sha256": {"x6-pop": "digest"},
                    "timing": {
                        "started_utc": "2026-09-30T00:00:00+00:00",
                        "finished_utc": "2026-09-30T01:00:00+00:00",
                        "wall_seconds": 3600.0,
                        "cpu_seconds": 3500.0,
                    },
                    "provenance": {"code": {"commit": "c"}, "host": {"hostname": "h"}},
                    **body,
                }
            )
    return records


def test_aggregate_applies_the_declared_readings(synthetic_analysis: Any) -> None:
    sizes = replace(SMALL, repetitions=120, truth_pipelines=3)
    out = f.require_sealed_location(f.SEALED_ROOT / "aggregate")
    for name, values in _records(sizes).items():
        analysis = f.Analysis(name, len(values), asdict(sizes), values.__getitem__)
        f.run_shard(synthetic_analysis(out, analysis, x6.SUITE.preconditions), out)

    with pytest.raises(ValueError, match="Sealed until"):
        x6.aggregate_x6([out], sizes)
    f.private_directory(f.RELEASE_RECORD.parent)
    f.RELEASE_RECORD.write_text("{}")
    result = x6.aggregate_x6([out], sizes)
    assert result["x6a"]["incomplete_units"] == [] and result["x6a"]["units"] == 152
    truths = result["x6a"]["truths"]
    assert [t["d1"]["value"] for t in truths] == pytest.approx([0.6] * 8)
    assert truths[0]["d1"]["retry_fraction"] == pytest.approx(1 / 3)
    assert truths[0]["d1"]["mcse"] == 0
    assert truths[0]["pop"]["value"] == pytest.approx(0.61)
    zero, low, top = (result["x6a"]["strengths"][i] for i in (0, 1, 8))
    assert zero["truth_d1"]["by_construction"]
    assert zero["vs_d1"]["pointwise"]["covered"] == 119
    assert low["vs_d1"]["pointwise"] == {
        **low["vs_d1"]["pointwise"],
        "covered": 107,
        "total": 119,
        "reading": "subnominal",
    }
    assert low["vs_d1"]["band_interval"]["total"] == 119
    assert top["complete"] == 119 and top["gaps"] == 1
    assert top["vs_d1"]["pointwise_gaps_as_misses"]["total"] == 120
    assert low["vs_pop"]["pointwise"]["covered"] == 107
    assert top["vs_d1"]["pointwise_gaps_as_misses"]["covered"] == 107
    bias = low["matching_bias"]
    assert bias["empirical_bias"]["mean"] == pytest.approx(0.0)
    assert bias["truth_d1_minus_pop"]["value"] == pytest.approx(-0.01)
    assert bias["mse_to_mean_se2"] == pytest.approx(0.0)
    band = result["x6a"]["band"]
    assert band["band_complete"] == 119 and band["vs_d1"]["primary"]["covered"] == 107
    assert band["vs_d1"]["gaps_as_misses"]["total"] == 120
    assert band["empirical_max_t_above_floor"] == {"count": 30, "total": 120}
    cells = result["x6b"]["cells"]
    assert [c["vs_d1"]["pointwise"]["total"] for c in cells] == [120, 120]
    assert result["x6b"]["units"] == 2 + 240 + 6
    assert result["code"] == [f.code_provenance()]


def test_coverage_readings_and_standardized_errors() -> None:
    def reading(covered: int, total: int) -> dict[str, Any]:
        return x6.coverage([True] * covered + [False] * (total - covered))

    assert reading(190, 200)["wilson95"] == pytest.approx([0.9104, 0.9726], abs=5e-5)
    assert reading(190, 200)["reading"] == "adequate"
    assert reading(180, 200)["reading"] == "subnominal"
    assert reading(170, 200)["reading"] == "failure"
    assert not reading(200, 200)["conservative"]
    assert reading(1000, 1000)["conservative"]
    assert reading(99, 99)["reading"] == "no reading"
    assert x6.wilson(0, 0) is None
    assert x6.standardized(0.6, 0.02, 0.6) == 0
    assert x6.standardized(0.62, 0.02, 0.6) == pytest.approx(
        (math.log(0.62 / 0.38) - math.log(0.6 / 0.4)) / (0.02 / (0.62 * 0.38))
    )
    shifted = x6.z_summary([0.3 + 0.01 * (i % 3) for i in range(200)])
    assert shifted is not None and shifted["uncovered_bias"] == "positive"
    centered = x6.z_summary([(-1) ** i * 1.0 for i in range(200)])
    assert centered is not None and centered["uncovered_bias"] is None
    assert centered["below_minus_1_96"] == 0
    rows = [_row(0.6, 0.595, 0.605, False) for _ in range(150)]
    precise = x6.strength_summary(
        rows, {"value": 0.6, "mcse": 0.001}, x6.BY_CONSTRUCTION
    )
    assert "truth_precision" not in precise["vs_d1"]["pointwise"]
    loose = x6.strength_summary(rows, {"value": 0.6, "mcse": 0.003}, x6.BY_CONSTRUCTION)
    assert loose["vs_d1"]["pointwise"]["truth_precision"] == {
        "minus_2se": "failure",
        "plus_2se": "failure",
        "conservative": {"minus_2se": False, "plus_2se": False},
        "inconclusive": True,
    }


def test_probe_reports_cpu_times_only() -> None:
    result = x6.probe(1)
    assert set(result) == {
        "size",
        "count",
        "cpu_seconds_per_panel",
        "cpu_seconds_per_auc",
        "unit_cpu_hours",
    }
    assert set(result["unit_cpu_hours"]) == {
        "x6a-repetition",
        "truth-pipeline",
        "x6b-repetition",
        "population-fit",
        "population-trainings",
    }


def test_command_line_plans_the_precondition_and_seals_the_aggregate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert x6.main(["plan"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"x6-pop {cell} {side}" for cell in (0, 1) for side in f.SIDES
    ]
    output = tmp_path / "x6.json"
    arguments = ["aggregate", "--out", str(tmp_path), "--output", str(output)]
    with pytest.raises(ValueError, match="Sealed until"):
        x6.main(arguments)
    assert not output.exists()
    assert x6.SUITE.sealed and x6.SUITE.kinds == ("x6a", "x6b")


def test_module_imports_only_frozen_code_the_x1_utilities_and_the_foundation() -> None:
    tree = ast.parse(Path(x6.__file__).read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if not node.module.startswith("ic_study"):
                continue
            if (STUDY / "src" / node.module.replace(".", "/")).is_dir():
                imported |= {f"{node.module}.{alias.name}" for alias in node.names}
            else:
                imported.add(node.module)
    reused = {
        "ic_study.simulation.v4_exploratory",
        "ic_study.simulation.v4_exploratory_x1b",
        "ic_study.simulation.v4_exploratory_x3x7",
    }
    assert reused <= imported
    freeze = json.loads((STUDY / x12.FREEZE).read_text())["code"]
    for name in imported - reused:
        path = "src/" + name.replace(".", "/") + ".py"
        assert freeze[path] == hashlib.sha256((STUDY / path).read_bytes()).hexdigest()
    provenance = f.successor_provenance(x6.SUITE.modules)
    assert (
        "src/ic_study/simulation/v4_exploratory_x6.py" in provenance["successor_sha256"]
    )


def test_x6a_pointwise_requires_complete_units() -> None:
    records = _records(replace(SMALL, repetitions=101, truth_pipelines=3))["x6a"]
    for record in records:
        if record["job"]["kind"] == "repetition":
            record["cells"][-1]["success"] = False
            record["curve"]["band_complete"] = False
    result = x6.summarize("x6a", records)
    for strength in result["strengths"]:
        assert strength["vs_d1"]["pointwise"]["total"] == 0
        assert strength["vs_d1"]["pointwise"]["reading"] == "no reading"
        assert strength["vs_d1"]["pointwise_gaps_as_misses"]["reading"] == "no reading"


def test_secondary_coverage_and_bias_require_one_hundred_completes() -> None:
    rows = [_row(0.8, 0.7, 0.9, False)] + [{"success": False}] * 100
    result = x6.strength_summary(rows, x6.BY_CONSTRUCTION, x6.BY_CONSTRUCTION)
    secondary = result["vs_d1"]["pointwise_gaps_as_misses"]
    assert secondary["total"] == 101 and secondary["reading"] == "no reading"
    reps = [
        {
            "cells": [row],
            "curve": {
                "band_complete": i == 0,
                "empirical_exceeds_floor": False,
                "band_reproduced": True,
            },
        }
        for i, row in enumerate(rows)
    ]
    joint = x6.band_summary(reps, [x6.BY_CONSTRUCTION], [x6.BY_CONSTRUCTION])
    assert joint["vs_d1"]["gaps_as_misses"]["reading"] == "no reading"
    bias = x6.z_summary([0.4, 0.4])
    assert bias is not None and bias["uncovered_bias"] is None


def test_truth_precision_applies_to_secondary_pointwise_band_and_bias() -> None:
    rows = [_row(0.606, 0.595, 0.605, True) for _ in range(150)]
    for row in rows:
        row["band"] = [0.595, 0.605]
    truth = {"value": 0.6, "mcse": 0.003}
    result = x6.strength_summary(rows, truth, x6.BY_CONSTRUCTION)
    for key in ("pointwise", "pointwise_gaps_as_misses"):
        assert result["vs_d1"][key]["truth_precision"]["inconclusive"]
        assert result["vs_d1"][key]["reading"] == "inconclusive-truth-precision"
    bias = result["vs_d1"]["standardized_error"]
    assert bias["truth_precision"]["inconclusive"] and bias["uncovered_bias"] is None
    reps = [
        {
            "cells": [row],
            "curve": {
                "band_complete": True,
                "empirical_exceeds_floor": False,
                "band_reproduced": True,
            },
        }
        for row in rows
    ]
    band = x6.band_summary(reps, [truth], [x6.BY_CONSTRUCTION])
    assert band["vs_d1"]["gaps_as_misses"]["truth_precision"]["inconclusive"]


def test_truth_precision_includes_conservative_classification() -> None:
    rows = [_row(0.6, 0.59, 0.61, True) for _ in range(400)]
    rows[:2] = [_row(0.6, 0.599, 0.601, True) for _ in range(2)]
    truth = {"value": 0.6, "mcse": 0.003}
    result = x6.strength_summary(rows, truth, x6.BY_CONSTRUCTION)
    for key in ("pointwise", "pointwise_gaps_as_misses"):
        reading = result["vs_d1"][key]
        assert reading["truth_precision"]["inconclusive"]
        assert reading["reading"] == "inconclusive-truth-precision"
        assert not reading["conservative"]


@pytest.mark.parametrize("complete", [99, 100])
def test_secondary_reading_eligibility_uses_completes_at_the_boundary(
    complete: int,
) -> None:
    rows = [_row(0.8, 0.7, 0.9, False) for _ in range(complete)]
    result = x6.strength_summary(
        rows + [{"success": False}] * 100,
        x6.BY_CONSTRUCTION,
        x6.BY_CONSTRUCTION,
    )
    reading = result["vs_d1"]["pointwise_gaps_as_misses"]
    assert reading["complete"] == complete and reading["total"] == complete + 100
    assert reading["reading"] == ("no reading" if complete == 99 else "failure")
    bias = result["vs_d1"]["standardized_error"]
    assert bias["uncovered_bias"] == (None if complete == 99 else "positive")


def test_x6a_mixed_units_preserve_all_denominators_and_error_counts() -> None:
    records = _records(replace(SMALL, repetitions=102, truth_pipelines=3))["x6a"]
    repetitions = [r for r in records if r["job"]["kind"] == "repetition"]
    repetitions[-1]["error"] = "ValueError('terminal')"
    repetitions[-1]["success"] = None
    repetitions[-1]["curve"] = None
    result = x6.summarize("x6a", records)
    for strength in result["strengths"]:
        assert (strength["complete"], strength["gaps"], strength["errors"]) == (
            100,
            1,
            1,
        )
        for name in ("d1", "pop"):
            entry = strength[f"vs_{name}"]
            assert entry["pointwise"]["total"] == 100
            assert entry["band_interval"]["total"] == 100
            assert entry["pointwise_gaps_as_misses"]["total"] == 101
            assert entry["standardized_error"]["count"] == 100
        assert strength["matching_bias"]["d5_mean_shift"]["count"] == 100
    for name in ("d1", "pop"):
        assert result["band"][f"vs_{name}"]["primary"]["total"] == 100
        assert result["band"][f"vs_{name}"]["gaps_as_misses"]["total"] == 101


@pytest.mark.parametrize("kind", ["x6a", "x6b"])
def test_unknown_truth_precision_prevents_coverage_and_bias_readings(kind: str) -> None:
    records = _records(replace(SMALL, repetitions=102, truth_pipelines=1))[kind]
    for record in records:
        if record["job"]["kind"] == "repetition":
            for cell in record["cells"]:
                if "point" in cell:
                    cell["point"] += 0.02
    result = x6.summarize(kind, records)
    strengths = result["strengths"][1:] if kind == "x6a" else result["cells"]
    for strength in strengths:
        assert strength["truth_d1"]["mcse"] is None
        entry = strength["vs_d1"]
        for key in ("pointwise", "pointwise_gaps_as_misses"):
            assert entry[key]["reading"] == "inconclusive-truth-precision"
            assert not entry[key]["truth_precision"]["available"]
        assert entry["standardized_error"]["uncovered_bias"] is None
        assert not entry["standardized_error"]["truth_precision"]["available"]
        assert strength["matching_bias"]["empirical_bias"]["mcse"] is None
        assert strength["matching_bias"]["truth_d1_minus_pop"]["se"] is None
        assert (
            strength["vs_pop"]["pointwise"]["reading"] != "inconclusive-truth-precision"
        )
    if kind == "x6a":
        assert result["strengths"][0]["truth_d1"]["by_construction"]
        assert result["strengths"][0]["vs_d1"]["pointwise"]["reading"] == "adequate"
        for key in ("primary", "gaps_as_misses"):
            assert (
                result["band"]["vs_d1"][key]["reading"]
                == "inconclusive-truth-precision"
            )
            assert not result["band"]["vs_d1"][key]["truth_precision"]["available"]


def test_x6a_coverage_becomes_readable_only_in_the_host_union(
    synthetic_analysis: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    from datetime import datetime, tzinfo

    sizes = replace(SMALL, repetitions=120, truth_pipelines=3)
    outs = [f.SEALED_ROOT / name for name in ("icllm", "icmomat")]
    for shard, out in enumerate(outs):
        host = {"cpu": out.name, "system": "synthetic", "environment": "locked"}
        monkeypatch.setattr(f, "host_class", lambda host=host: host)
        for name, values in _records(sizes).items():
            jobs = x6.queue(name, sizes)
            analysis = f.Analysis(
                name,
                len(values),
                asdict(sizes),
                values.__getitem__,
                identities=tuple(job.describe() for job in jobs),
                identity_key="job",
            )
            f.run_shard(
                synthetic_analysis(out, analysis, x6.SUITE.preconditions),
                out,
                shard=shard,
                shards=2,
            )
    f.private_directory(f.RELEASE_RECORD.parent)
    f.RELEASE_RECORD.write_text("{}")
    result = x6.aggregate_x6(outs, sizes)
    assert result["x6a"]["incomplete_units"] == []
    assert result["x6b"]["incomplete_units"] == []
    assert result["x6a"]["band"]["band_complete"] == 119
    assert result["x6a"]["band"]["vs_d1"]["primary"]["reading"] == "subnominal"
    assert [source["accepted_units"] for source in result["sources"]] == [200, 200]

    class AfterClose(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> AfterClose:
            return cls.fromtimestamp(f.WINDOW_CLOSE.timestamp() + 1, tz=tz)

    monkeypatch.setattr(f, "datetime", AfterClose)
    for out in outs:
        partial = x6.aggregate_x6([out], sizes)
        band = partial["x6a"]["band"]
        assert band["band_complete"] < 100
        assert (
            band["vs_d1"] is None or band["vs_d1"]["primary"]["reading"] == "no reading"
        )
        readings = [
            strength["vs_d1"]["pointwise"]["reading"]
            for strength in partial["x6a"]["strengths"]
            if strength["vs_d1"] is not None
        ]
        assert readings and set(readings) == {"no reading"}
        assert partial["x6a"]["incomplete_units"]
