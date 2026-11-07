"""Reporting pipeline for the v4 a*(r) paper, on fixtures from frozen emitters."""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from matplotlib.colors import to_hex
from matplotlib.figure import Figure
from matplotlib.text import Text
from numpy.typing import NDArray

from ic_study.analysis import v4_report_figures
from ic_study.analysis.detection_boundary import boundary
from ic_study.analysis.detection_boundary_v4 import Uncertainty, band
from ic_study.analysis.detection_v4_report import Inputs, main, render
from ic_study.analysis.shp_crosswalk import QUASI_SIMPLEX
from ic_study.analysis.shp_reliability import STARTS_FAILURES
from ic_study.analysis.v4_report_figures import (
    BEYOND_Y,
    GAP_COLOR,
    SOLVER_BUDGET,
    Render,
    _shp_handles,
    figure_gate,
    figure_inventory,
    figure_names,
)
from ic_study.analysis.v4_report_schema import (
    BAND_MARGIN,
    CROSSWALK_REFERENCES,
    GAP_KINDS,
    IN_PROGRESS,
    INVALID,
    MAIN_CURVE_INVALID,
    NOT_STARTED,
    PARTIAL,
    PROPAGATION,
    STATUSES,
    SUCCESSOR_SOURCE,
    VALID,
    Boundary,
    GateRecords,
    Release,
    SchemaError,
    band_contains_point,
    load_allocation,
    load_crosswalk,
    load_gate,
    load_release,
    load_shp,
    parse_crosswalk,
    parse_release,
    parse_shp,
    parse_summary,
)
from ic_study.analysis.v4_report_synthetic import (
    G0_FAILURES,
    NETWORKS,
    GatePlan,
    UnitPlan,
    build_gate,
    build_release,
    crosswalk_fixture,
    logistic_profile,
    shp_fixture,
    shp_successor_fixture,
    stage_successor,
    stop_before_g2,
    unit_keys,
    write_release,
)
from ic_study.analysis.v4_report_tables import _TEX, region, table_t3
from ic_study.simulation.detection_v4 import GRID
from ic_study.simulation.v4_criteria import dispersion, dispersion_pass, refit_ratio
from ic_study.simulation.v4_plan import G2_CELLS
from ic_study.simulation.v4_store import SealedStore

STUDY = Path(__file__).resolve().parents[2]
V4 = STUDY / "experiments/exploratory/detection-boundary-v4"
CRITERIA = V4 / "criteria-v43.json"
CAPTIONS = V4 / "report/captions.md"
B = unit_keys(tier=1, family="B")
C = unit_keys(tier=2, family="C")
D = unit_keys(tier=2, family="D")
E = unit_keys(tier=2, family="E")
B_LATENT = unit_keys(tier=3, family="B", channel="latent")
# The band straddles 0.70 at the top strengths, so the sustained interval's lower
# end lies above the gap at a=0.003 and its upper end is None.
PLATEAU = (0.5, 0.52, 0.55, 0.58, 0.62, 0.66, 0.69, 0.705, 0.705)


def _plans() -> dict[str, UnitPlan]:
    return {
        B[0.5]: UnitPlan(logistic_profile(0.02)),
        B[0.55]: UnitPlan(logistic_profile(0.9), gaps=frozenset({6})),
        B[0.6]: UnitPlan(logistic_profile(9.0)),
        B[0.65]: UnitPlan(PLATEAU, gaps=frozenset({2})),
        C[0.5]: UnitPlan((0.575, *logistic_profile(2.0)[1:])),
        C[0.55]: UnitPlan(
            logistic_profile(0.1),
            gaps=frozenset({7, 8}),
            gap_status="family-limit-upper",
            gap_evaluations=0,
        ),
        C[0.6]: UnitPlan(
            logistic_profile(0.1), gaps=frozenset({8}), gap_status="family-limit-upper"
        ),
        D[0.5]: UnitPlan(logistic_profile(0.1), partial_cells=3),
        D[0.55]: UnitPlan(
            logistic_profile(0.1), gaps=frozenset({5}), gap_status="interior"
        ),
        E[0.5]: UnitPlan(logistic_profile(0.1), gaps=frozenset(range(9))),
        # Reuses B's observed fits: a dependency gap where B at r=0.55 has its gap.
        B_LATENT[0.55]: UnitPlan(logistic_profile(0.9)),
    }


def _write_json(path: Path, record: dict[str, Any]) -> None:
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", "utf-8")


def _release(root: Path, plans: dict[str, UnitPlan]) -> Path:
    path = root / "released_curves.json"
    write_release(path, build_release(root / "confirmatory", plans, draws=40))
    return path


@pytest.fixture(scope="module")
def env(
    tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest
) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("v4report")
    shp = root / "shp.json"
    shp.write_text(json.dumps(shp_fixture()), encoding="utf-8")
    allocation = root / "v4-allocation.json"
    gate = build_gate(root / "gate", allocation=allocation)
    successor = root / "G1c-aggregate-successor.json"
    _write_json(successor, stage_successor(gate))
    from ic_study.analysis import v4_report_schema

    patch = pytest.MonkeyPatch()
    patch.setattr(
        v4_report_schema,
        "APPROVED_G1C_SHA256",
        hashlib.sha256(successor.read_bytes()).hexdigest(),
        raising=False,
    )
    request.addfinalizer(patch.undo)

    return {
        "curves": _release(root, _plans()),
        "gate": gate,
        "shp": shp,
        "allocation": allocation,
        "successor": successor,
        "root": root,
    }


@pytest.fixture(scope="module")
def release(env: dict[str, Path]) -> Release:
    return load_release(env["curves"])


def _env_gate(env: dict[str, Path], *successors: Path) -> GateRecords:
    return load_gate(
        env["gate"],
        successors=successors,
        allocation=load_allocation(env["allocation"]),
    )


@contextmanager
def _captured_figures() -> Iterator[dict[str, Figure]]:
    figures: dict[str, Figure] = {}
    real = v4_report_figures.save

    def spy(fig: Figure, options: Render, name: str) -> list[Path]:
        figures[name] = fig
        return real(fig, options, name)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(v4_report_figures, "save", spy)
        yield figures


def _full_inputs(env: dict[str, Path]) -> Inputs:
    return Inputs(
        env["curves"],
        env["gate"],
        env["shp"],
        CRITERIA,
        successors=(env["successor"],),
        allocation=env["allocation"],
    )


@pytest.fixture(scope="module")
def report(env: dict[str, Path]) -> dict[str, Any]:
    """One render with every input, keeping the drawn figures for inspection."""
    out = env["root"] / "report"
    with _captured_figures() as figures:
        render(_full_inputs(env), out, dpi=60)
    return {"out": out, "figures": figures}


def _table(directory: Path, name: str) -> list[dict[str, str]]:
    text = (directory / f"{name}.csv").read_text(encoding="utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def _texts(fig: Figure) -> list[str]:
    return [t.get_text() for t in fig.findobj(Text)]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _raw(env: dict[str, Path]) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(env["curves"].read_text(encoding="utf-8"))
    return data


def _curve(data: dict[str, Any], key: str) -> dict[str, Any]:
    return next(c for c in data["curves"] if c["unit"] == key)


# Schema fidelity -----------------------------------------------------------


def test_loader_accepts_frozen_release_and_maps_every_state(
    env: dict[str, Path], release: Release
) -> None:
    assert len(release.statuses) == 414
    assert release.statuses[B[0.5]] == VALID
    assert release.statuses[C[0.5]] == INVALID
    assert release.statuses[D[0.5]] == PARTIAL
    assert release.statuses[B[0.7]] == NOT_STARTED
    assert release.main_curve_valid is False
    reached = release.curves[B[0.5]]
    assert reached.first.point is not None and reached.critical is not None
    censored = release.curves[B[0.55]]
    assert censored.first.point is None and censored.first.censored_at == 0.3
    assert censored.available == (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.6, 0.9)
    beyond = release.curves[B[0.6]]
    assert beyond.first.point is None and beyond.first.censoring is None
    invalid = release.curves[C[0.5]]
    assert not invalid.valid_null_gate and invalid.first.interval is None
    no_estimates = release.curves[E[0.5]]
    assert no_estimates.status == INVALID and no_estimates.auc == ()
    assert no_estimates.cell_final_status == ("no-L1-root",) * 9
    assert no_estimates.cell_gap == ("solver",) * 9
    assert release.curves[C[0.55]].cell_gap[7:] == ("screened", "screened")
    assert release.curves[C[0.6]].cell_gap[8] == "family_limit"
    assert release.curves[D[0.55]].cell_gap[5] == "validation"
    control = release.curves[B_LATENT[0.55]]
    assert control.cell_gap[6] == "dependency" and control.gap_count == 1
    anchor = _curve(_raw(env), B[0.5])["cells"][0]["attempts"][-1]
    assert (anchor["status"], anchor["evaluations"]) == ("anchor-exact", 1)


def _mutations() -> list[tuple[str, Any]]:
    def extra(d: dict[str, Any]) -> None:
        _curve(d, B[0.5])["schema_version"] = 1

    def missing(d: dict[str, Any]) -> None:
        del _curve(d, B[0.5])["cells"]

    def short_auc(d: dict[str, Any]) -> None:
        _curve(d, B[0.5])["auc"].pop()

    def moved_boundary(d: dict[str, Any]) -> None:
        curve = _curve(d, B[0.5])
        curve["first"] = 0.9 if curve["first"] != 0.9 else 0.6

    def off_grid(d: dict[str, Any]) -> None:
        _curve(d, B[0.5])["first"] = 0.05

    def status(d: dict[str, Any]) -> None:
        _curve(d, C[0.5])["status"] = VALID

    def gate(d: dict[str, Any]) -> None:
        _curve(d, C[0.5])["valid_null_gate"] = True

    def dropped_censoring(d: dict[str, Any]) -> None:
        del _curve(d, B[0.55])["first_censoring"]

    def truncated(d: dict[str, Any]) -> None:
        d["inventory"]["units"].pop()

    def close(d: dict[str, Any]) -> None:
        d["inventory"]["closed_utc"] = "2026-10-20T00:00:00Z"

    def main_flag(d: dict[str, Any]) -> None:
        d["inventory"]["main_curve_valid"] = True

    def unknown_status(d: dict[str, Any]) -> None:
        d["inventory"]["units"][0]["status"] = "complete"

    def unreleased(d: dict[str, Any]) -> None:
        d["curves"] = [c for c in d["curves"] if c["unit"] != C[0.5]]

    def gap_count(d: dict[str, Any]) -> None:
        _curve(d, B[0.55])["gap_count"] = 0

    def unknown_solver_status(d: dict[str, Any]) -> None:
        _curve(d, E[0.5])["cells"][0]["attempts"][-1]["status"] = "gave-up"

    return [
        (f.__name__, f)
        for f in (
            extra,
            missing,
            short_auc,
            moved_boundary,
            off_grid,
            status,
            gate,
            dropped_censoring,
            truncated,
            close,
            main_flag,
            unknown_status,
            unreleased,
            gap_count,
            unknown_solver_status,
        )
    ]


@pytest.mark.parametrize(("name", "mutate"), _mutations())
def test_loader_rejects_drift_from_frozen_schema(
    env: dict[str, Path], name: str, mutate: Any
) -> None:
    data = copy.deepcopy(_raw(env))
    parse_release(copy.deepcopy(data))
    mutate(data)
    with pytest.raises(SchemaError):
        parse_release(data)


def test_pre_freeze_record_shape_is_rejected() -> None:
    with pytest.raises(SchemaError):
        parse_release({"schema_version": 1, "unit_id": "B-main-r070"})


def _frozen_band(point: float, se: float = 0.0) -> tuple[float, float]:
    interval = band(
        Uncertainty(
            np.array([point]), np.zeros(1), np.array([se]), np.full((2, 1), point)
        )
    )
    return float(interval.lower[0]), float(interval.upper[0])


def _near_one(data: dict[str, Any]) -> dict[str, Any]:
    """B at r=0.5 ends as real runs did: one discordant pair, point above the band."""
    curve = _curve(data, B[0.5])
    point = 1 - 1 / (2 * NETWORKS) ** 2
    curve["auc"][-1] = point
    curve["lower"][-1], curve["upper"][-1] = _frozen_band(point)
    return data


@pytest.mark.parametrize(
    "point", [0.0, 1e-9, BAND_MARGIN, 0.3, 1 - BAND_MARGIN, 1 - 1e-7, 1.0]
)
@pytest.mark.parametrize("se", [0.0, 1e-6, 0.01])
def test_band_check_accepts_every_frozen_band(point: float, se: float) -> None:
    lower, upper = _frozen_band(point, se)
    assert band_contains_point(lower, point, upper)


def test_band_check_refuses_an_exact_endpoint_off_its_band() -> None:
    near_one = _frozen_band(1 - BAND_MARGIN / 2)
    near_zero = _frozen_band(BAND_MARGIN / 2)
    assert not band_contains_point(near_one[0], 1.0, near_one[1])
    assert not band_contains_point(near_zero[0], 0.0, near_zero[1])


def test_loader_accepts_the_frozen_band_below_a_point_near_one(
    env: dict[str, Path],
) -> None:
    curve = parse_release(_near_one(copy.deepcopy(_raw(env)))).curves[B[0.5]]
    assert curve.upper[-1] < curve.auc[-1] < 1


def test_loader_rejects_a_point_outside_the_clipped_band(env: dict[str, Path]) -> None:
    data = copy.deepcopy(_raw(env))
    curve = _curve(data, B[0.5])
    curve["auc"][0] = curve["upper"][0] + 0.01
    with pytest.raises(SchemaError, match="band must contain point AUC"):
        parse_release(data)


def test_profiles_draw_the_released_band_and_point_apart(
    env: dict[str, Path], tmp_path: Path
) -> None:
    release = parse_release(_near_one(copy.deepcopy(_raw(env))))
    curve = release.curves[B[0.5]]
    with _captured_figures() as figures:
        v4_report_figures.figure_profiles(release, Render(tmp_path, formats=()), "B")
    panel = figures["F2_auc_profiles_B"].axes[0]
    x = len(GRID) - 1
    assert any(
        np.allclose(segment, [[x, curve.lower[-1]], [x, curve.upper[-1]]], rtol=0)
        for collection in panel.collections
        if isinstance(collection, LineCollection)
        for segment in collection.get_segments()
    )
    marker = next(line for line in panel.lines if line.get_marker() == "o")
    assert any(
        px == x and py == curve.auc[-1]
        for px, py in cast(NDArray[np.float64], marker.get_xydata())
    )
    assert all(
        line.get_zorder() < marker.get_zorder()
        for line in panel.lines
        if line is not marker
    )


def _g0_fits(root: Path, key: str) -> list[dict[str, Any]]:
    fits: list[dict[str, Any]] = json.loads((root / key / "result.json").read_text())[
        "fits"
    ]
    return fits


def test_gate_loader_reads_sealed_records_without_writing(env: dict[str, Path]) -> None:
    before = sorted((p, p.stat().st_mtime_ns) for p in env["gate"].rglob("*"))
    gate = _env_gate(env, env["successor"])
    assert sorted(gate.summaries) == ["G0", "G1b", "G1c", "G2", "G2c"]
    assert all(s["completed"] == s["planned"] for s in gate.summaries.values())
    assert all(count >= 2 for count in gate.summary_counts.values())
    assert len(gate.g1b_critical) == 5000 and min(gate.g1b_critical) >= 2.7729
    assert gate.g0_evaluations and len(gate.task_digests) == 81 + 5000
    # Amendment v4.4 propagation gaps are curve cells, never G0 fits.
    assert set(GAP_KINDS) - {PROPAGATION} <= {fit.gap for fit in gate.g0_fits}
    after = sorted((p, p.stat().st_mtime_ns) for p in env["gate"].rglob("*"))
    assert before == after


def test_gate_fixture_has_the_real_g0_shapes(env: dict[str, Path]) -> None:
    lines = [
        json.loads(line)
        for line in (env["gate"] / "criteria.jsonl").read_text().splitlines()
    ]
    g0 = [line for line in lines if line["gate"] == "G0"]
    assert [line["completed"] for line in g0] == [27, 54, 81]
    assert [line["pass"] for line in g0[:-1]] == [False, False]
    identity = [f for f in _g0_fits(env["gate"], "G0-00000") if f["family"] != "C"]
    assert {
        (f["attempts"][-1]["status"], f["attempts"][-1]["evaluations"])
        for f in identity
    } == {("anchor-exact", 1)}
    controls = [
        f
        for f in _g0_fits(env["gate"], "G0-00080")
        if f["family"] == "B" and f["channel"] != "observed"
    ]
    assert len(controls) == 3
    assert all(f["attempts"] == [] and f["dependency_gap"] for f in controls)
    (screened,) = [f for f in _g0_fits(env["gate"], "G0-00008") if f["family"] == "C"]
    final = screened["attempts"][-1]
    assert (screened["success"], final["status"], final["evaluations"]) == (
        False,
        "family-limit-upper",
        0,
    )


def test_gate_loader_detects_seal_mismatch(tmp_path: Path) -> None:
    root = build_gate(tmp_path / "gate", GatePlan(stages=("G0",)))
    load_gate(root)
    target = root / "G0-00000" / "result.json"
    record = json.loads(target.read_text())
    record["success"] = False
    target.write_text(json.dumps(record))
    with pytest.raises(SchemaError, match="sealed digest"):
        load_gate(root)


def test_shp_loader_uses_frozen_output(env: dict[str, Path]) -> None:
    data = json.loads(env["shp"].read_text())
    anchor = parse_shp(data)
    assert anchor.wald_95_interval[0] <= anchor.estimate <= anchor.wald_95_interval[1]
    assert anchor.starts is None  # reports written before successor 1 still load
    data["anchor"]["wald_95_interval"][1] += 0.01
    with pytest.raises(SchemaError):
        parse_shp(data)


@pytest.fixture(scope="module")
def successor(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    root = tmp_path_factory.mktemp("successor")
    records = {
        "admissible": shp_successor_fixture(),
        "failed": shp_successor_fixture(starts_admissible=False),
        "crosswalk": crosswalk_fixture(),
    }
    paths = {}
    for name, record in records.items():
        paths[name] = root / f"{name}.json"
        paths[name].write_text(json.dumps(record, allow_nan=False), encoding="utf-8")
    return paths


def _successor_mutations() -> list[tuple[str, str, Any]]:
    def wald(d: dict[str, Any]) -> None:
        d["successor_1"]["starts_sensitivity"]["anchor"]["wald_95_interval"][1] += 0.01

    def year(d: dict[str, Any]) -> None:
        d["successor_1"]["starts_sensitivity"]["anchor"]["year"] = 2003

    def status(d: dict[str, Any]) -> None:
        d["successor_1"]["starts_sensitivity"]["status"] = "clipped"

    def specification(d: dict[str, Any]) -> None:
        d["successor_1"]["specification"] = "shp-reliability-successor-2"

    def estimate_on_failure(d: dict[str, Any]) -> None:
        d["successor_1"]["starts_sensitivity"]["anchor"] = d["anchor"]

    def undeclared_reason(d: dict[str, Any]) -> None:
        d["successor_1"]["starts_sensitivity"]["reasons"] = ["trait near zero"]

    def no_reason(d: dict[str, Any]) -> None:
        d["successor_1"]["starts_sensitivity"]["reasons"] = []

    admissible = [wald, year, status, specification]
    failed = [estimate_on_failure, undeclared_reason, no_reason]
    return [("admissible", f.__name__, f) for f in admissible] + [
        ("failed", f.__name__, f) for f in failed
    ]


def test_shp_loader_reads_the_successor_starts_record(
    successor: dict[str, Path],
) -> None:
    admissible = load_shp(successor["admissible"])
    starts = admissible.starts
    assert starts is not None and starts.estimate is not None
    assert starts.year == admissible.year == 2004 and not starts.failure_reasons
    assert starts.wald_95_interval is not None
    assert starts.wald_95_interval[0] < starts.estimate < starts.wald_95_interval[1]
    failed = load_shp(successor["failed"]).starts
    assert failed is not None and failed.estimate is None
    assert failed.wald_95_interval is None
    assert failed.failure_reasons == (STARTS_FAILURES[2],)


@pytest.mark.parametrize(("source", "name", "mutate"), _successor_mutations())
def test_shp_loader_rejects_drift_in_the_successor_record(
    successor: dict[str, Path], source: str, name: str, mutate: Any
) -> None:
    data = json.loads(successor[source].read_text())
    parse_shp(copy.deepcopy(data))
    mutate(data)
    with pytest.raises(SchemaError):
        parse_shp(data)


def _reference(cell: dict[str, Any]) -> str | None:
    if cell["family"] == "B":
        return f"B η = {cell['eta']:.2f}"
    return "a = 0" if cell["a"] == 0 else None


def test_crosswalk_loader_keeps_reference_ranges_and_containment(
    successor: dict[str, Path],
) -> None:
    data = json.loads(successor["crosswalk"].read_text())
    crosswalk = parse_crosswalk(data)
    assert crosswalk.declared_plan and crosswalk.replicates == 10
    assert crosswalk.missing == 0 and len(crosswalk.ranges) == 27
    for probe in (0.64, 0.73):
        expected = {
            reference: tuple(
                c["r"]
                for c in data["cells"]
                if _reference(c) == reference
                and c["estimators"][QUASI_SIMPLEX]["min"]
                <= probe
                <= c["estimators"][QUASI_SIMPLEX]["max"]
            )
            for reference in CROSSWALK_REFERENCES
        }
        assert crosswalk.containing(probe) == expected
        assert any(expected.values())
    edge = next(c for c in data["cells"] if _reference(c) == "a = 0" and c["r"] == 0.5)
    summary = edge["estimators"][QUASI_SIMPLEX]
    assert parse_crosswalk(data).containing(summary["min"])["a = 0"][0] == 0.5
    summary["failures"] += 1
    with pytest.raises(SchemaError, match="replicate counts"):
        parse_crosswalk(data)
    summary["failures"] -= 1
    data["cells"].append(copy.deepcopy(edge))
    with pytest.raises(SchemaError, match="duplicate"):
        parse_crosswalk(data)
    data["cells"].pop()
    edge["r"] = 0.52
    with pytest.raises(SchemaError):
        parse_crosswalk(data)


def test_f6_draws_starts_and_crosswalk_or_notes_a_starts_failure(
    env: dict[str, Path], successor: dict[str, Path], tmp_path: Path
) -> None:
    crosswalk = load_crosswalk(successor["crosswalk"])
    figures = {}
    for name in ("admissible", "failed"):
        inputs = Inputs(
            env["curves"], None, successor[name], None, successor["crosswalk"]
        )
        with _captured_figures() as drawn:
            manifest = json.loads(render(inputs, tmp_path / name, dpi=40).read_text())
        fig = drawn["F6_a_star_shp_anchor"]
        fig.canvas.draw()
        panel = fig.axes[0]
        mark = next(t for t in panel.texts if t.get_text() == MAIN_CURVE_INVALID)
        background = mark.get_bbox_patch()
        assert background is not None
        box = background.get_window_extent()
        assert not any(
            box.overlaps(line.get_window_extent())
            for line in panel.lines
            if line.get_marker() == "D"
        )
        assert (
            manifest["inputs"]["crosswalk"]["sha256"]
            == hashlib.sha256(successor["crosswalk"].read_bytes()).hexdigest()
        )
        assert manifest["classification"]["F6_a_star_shp_anchor"].startswith(
            "exploratory illustration"
        )
        figures[name] = (tmp_path / name / "F6_a_star_shp_anchor.png").read_bytes()
    assert figures["admissible"] != figures["failed"]
    admissible = [
        str(h.get_label())
        for h in _shp_handles(load_shp(successor["admissible"]), None)
    ]
    assert any(
        "STARTS sensitivity 2004\n(distinct from r)" in label for label in admissible
    )
    assert not any("≈" in label for label in admissible)
    assert not any("failed" in label or "crosswalk" in label for label in admissible)
    failed = [
        str(h.get_label())
        for h in _shp_handles(load_shp(successor["failed"]), crosswalk)
    ]
    assert any("STARTS" in label and "failed" in label for label in failed)
    assert sum("synthetic crosswalk, exploratory" in label for label in failed) == 3


def test_crosswalk_overlay_needs_the_shp_report(
    env: dict[str, Path], successor: dict[str, Path], tmp_path: Path
) -> None:
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="SHP"):
        render(Inputs(env["curves"], None, crosswalk=successor["crosswalk"]), out)
    with pytest.raises(SystemExit):
        main(
            [
                "--curves",
                str(env["curves"]),
                "--gate-root",
                str(env["gate"]),
                "--crosswalk",
                str(successor["crosswalk"]),
                "--out",
                str(out),
            ]
        )
    assert not out.exists()


# Rendering -----------------------------------------------------------------


def _outputs(directory: Path) -> dict[str, bytes]:
    return {p.name: p.read_bytes() for p in sorted(directory.iterdir())}


def test_full_render_is_complete_and_byte_deterministic(
    env: dict[str, Path], report: dict[str, Any], tmp_path: Path
) -> None:
    second = render(_full_inputs(env), tmp_path / "two", dpi=60)
    one, two = _outputs(report["out"]), _outputs(second.parent)
    assert one == two
    for name in figure_names():
        assert {f"{name}.pdf", f"{name}.png"} <= set(one)
    for table in (
        "T1_a_star_grid",
        "T1s_a_star_all_units",
        "T3_gate_summary",
        "T4_inventory",
    ):
        assert {f"{table}.csv", f"{table}.tex"} <= set(one)
    assert not any(n.startswith("T2") for n in one)
    for name, content in one.items():
        if name.endswith(".pdf"):
            assert b"/CreationDate" not in content and b"/ModDate" not in content
    manifest = json.loads(one["manifest.json"])
    assert manifest["outputs"] == {
        n: hashlib.sha256(c).hexdigest() for n, c in one.items() if n != "manifest.json"
    }
    inputs = manifest["inputs"]
    assert inputs["curves"]["sha256"] == _sha256(env["curves"])
    assert inputs["shp"]["sha256"]
    assert inputs["gate_root"]["task_records"] == 5081
    assert inputs["gate_root"]["identifier"] == env["gate"].name
    assert inputs["allocation"]["sha256"] == _sha256(env["allocation"])
    assert (
        manifest["classification"]["F3_exploratory_family_offsets_vs_B"]
        == "exploratory"
    )
    assert "commit" in manifest["code"]


def _tex_rows(text: str) -> list[list[str]]:
    reverse = sorted(((v, k) for k, v in _TEX.items()), key=lambda x: -len(x[0]))
    rows = []
    for line in text.splitlines():
        if not line.endswith(r" \\"):
            continue
        cells = []
        for cell in line[: -len(r" \\")].split(" & "):
            for escaped, raw in reverse:
                cell = cell.replace(escaped, raw)
            cells.append(cell)
        rows.append(cells)
    return rows


def test_latex_and_csv_tables_carry_identical_values(report: dict[str, Any]) -> None:
    out = report["out"]
    tables = sorted(out.glob("T*.csv"))
    assert len(tables) == 4
    for path in tables:
        rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
        tex = _tex_rows(path.with_suffix(".tex").read_text(encoding="utf-8"))
        assert rows == tex, path.name
    t1 = _table(out, "T1_a_star_grid")
    by_r = {row["r"]: row for row in t1 if row["family"] == "B"}
    assert by_r["0.55"]["a_star"] == "censored at gap a=0.3"
    assert by_r["0.60"]["a_star"] == "not reached (>0.9)"
    assert by_r["0.70"]["exposure"] == "calibration-exposed"
    assert by_r["0.70"]["status"] == NOT_STARTED
    c = next(r for r in t1 if r["family"] == "C" and r["r"] == "0.50")
    assert (c["null_gate"], c["a_star"]) == ("fail", "suppressed")


# Defect 1: the main-curve invalidation mark.


def test_main_curve_invalidation_is_marked_in_t1_and_on_b(
    report: dict[str, Any], release: Release
) -> None:
    assert release.main_curve_valid is False
    t1 = _table(report["out"], "T1_a_star_grid")
    flags = {(row["family"], row["main_curve_flag"]) for row in t1}
    assert flags == {("B", MAIN_CURVE_INVALID), *((f, "") for f in "ACDE")}
    b = {row["r"]: row for row in t1 if row["family"] == "B"}
    assert b["0.50"]["a_star"] == f"{release.curves[B[0.5]].first.point:g}"
    figures = report["figures"]
    for name in ("F1_a_star_by_family", "F6_a_star_shp_anchor"):
        fig = figures[name]
        fig.canvas.draw()
        b_panel, *others = fig.axes
        mark = next(t for t in b_panel.texts if t.get_text() == MAIN_CURVE_INVALID)
        box = mark.get_window_extent()
        assert b_panel.bbox.contains(box.x0, box.y0)
        assert b_panel.bbox.contains(box.x1, box.y1)
        assert not box.overlaps(b_panel.texts[0].get_window_extent())
        assert mark.get_fontweight() == "bold"
        background = mark.get_bbox_patch()
        assert background is not None
        assert to_hex(background.get_facecolor()) == "#ffffff"
        assert not any(
            MAIN_CURVE_INVALID in t.get_text() for ax in others for t in ax.texts
        )
    assert any(MAIN_CURVE_INVALID in t for t in _texts(figures["F2_auc_profiles_B"]))
    assert not any(
        MAIN_CURVE_INVALID in t for t in _texts(figures["F2_auc_profiles_C"])
    )


def test_offsets_without_paired_boundaries_show_an_explicit_empty_state(
    release: Release, tmp_path: Path
) -> None:
    with _captured_figures() as figures:
        v4_report_figures.figure_offsets(
            replace(release, curves={}), Render(tmp_path, formats=())
        )
    panel = figures["F3_exploratory_family_offsets_vs_B"].axes[0]
    assert not panel.axison
    assert not panel.lines
    assert panel.get_legend() is None
    assert any(
        "no paired valid point boundaries" in text.get_text() for text in panel.texts
    )


def test_secondary_boundary_panels_have_room_for_ordinal_ticks(
    report: dict[str, Any],
) -> None:
    for name in ("F1_a_star_by_family", "F6_a_star_shp_anchor"):
        figure = report["figures"][name]
        figure.canvas.draw()
        for panel in figure.axes[1:]:
            height = panel.get_position().height * figure.get_figheight()
            assert height >= 40 * v4_report_figures.MM
            assert panel.get_xlabel() == ""


# Defect 2: stage verdicts in T3.


def test_incomplete_stages_are_in_progress_not_failed(tmp_path: Path) -> None:
    plan = GatePlan(
        stages=("G0", "G2"), skip_tasks=frozenset({"G0-00080"}), running={"G2": 3}
    )
    gate = build_gate(tmp_path / "gate", plan)
    curves = _release(tmp_path, {B[0.5]: UnitPlan(logistic_profile(0.05))})
    out = tmp_path / "out"
    with _captured_figures() as figures:
        code = main(
            ["--curves", str(curves), "--gate-root", str(gate), "--out", str(out)]
        )
    assert code == 0
    rows = _table(out, "T3_gate_summary")
    by_stage: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        by_stage.setdefault(row["stage"], {})[row["item"]] = row
    assert {r["stage_pass"] for r in by_stage["G0"].values()} == {IN_PROGRESS}
    assert by_stage["G0"]["tasks completed"]["value"] == "80/81"
    assert {r["stage_pass"] for r in by_stage["G2"].values()} == {IN_PROGRESS}
    assert by_stage["G2"]["tasks completed"]["value"] == "3/700"
    assert by_stage["G1b"]["availability"]["stage_pass"] == "NA"
    texts = _texts(figures["F4_gate_diagnostics"])
    assert "G2 in progress: 3/700 tasks" in texts
    assert "3/700 tasks · in progress · no aggregate line yet" in texts
    assert (out / "F4_gate_diagnostics.pdf").exists()


def test_t3_reports_the_line_with_most_completed_tasks(tmp_path: Path) -> None:
    root = build_gate(tmp_path / "gate", GatePlan(stages=("G0",)))
    first = json.loads((root / "criteria.jsonl").read_text().splitlines()[0])
    assert first["completed"] < first["planned"] and first["pass"] is False
    # A slower shard's mid-run snapshot, appended after the complete line.
    SealedStore(root).append("criteria", first)
    gate = load_gate(root)
    assert gate.summary_counts["G0"] == 4
    assert gate.summaries["G0"]["completed"] == 81
    assert {row[4] for row in table_t3(gate, None).rows if row[0] == "G0"} == {"pass"}


@pytest.fixture(scope="module")
def failures(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Complete stages without criteria, and G2 ratios with no estimable cell."""
    broken = frozenset(f"G2-{i:05}" for i in range(0, 98, 2))  # 49 pairs, cell 1
    plan = GatePlan(
        stages=("G1c", "G2", "G2c"),
        failed_tasks=frozenset({"G1c-00007", "G2c-00000"}) | broken,
        shards=2,
    )
    return build_gate(tmp_path_factory.mktemp("failures") / "gate", plan)


def test_complete_stages_without_criteria_name_their_failure(failures: Path) -> None:
    rows = {(row[0], row[1]): row for row in table_t3(load_gate(failures), None).rows}
    assert rows[("G1c", "task failures")][2:] == ("1", "= 0", "fail")
    assert rows[("G1c", "failure reason")][2].startswith("1 failed task;")
    g2c = rows[("G2c", "failure reason")]
    assert "baseline" in g2c[2] and g2c[4] == "fail"


# Defect 8: the stop before G2 is an economy rule, not a G0 verdict.


def test_stop_before_g2_is_its_own_economy_rule_row(tmp_path: Path) -> None:
    gaps = {("B", 0.001, r): ("no-L1-root", 1) for r in (0.5, 0.55)}
    plan = GatePlan(stages=("G0",), g0_failures={**G0_FAILURES, **gaps})
    root = build_gate(tmp_path / "gate", plan)
    assert stop_before_g2(root, tmp_path / "v4-allocation.json") is not None
    gate = load_gate(root)
    rows = table_t3(gate, None).rows
    stops = [row for row in rows if row[4] == "stopped"]
    assert len(stops) == 1
    assert stops[0][0] == "pre-G2 stop" and "economy rule" in stops[0][1]
    assert {row[4] for row in rows if row[0] == "G0"} == {"pass"}
    with _captured_figures() as figures:
        figure_gate(gate, Render(tmp_path, dpi=40), None)
    strip = figures["F4_gate_diagnostics"].axes[-1]
    labels = [label.get_text() for label in strip.get_yticklabels()]
    assert labels == ["G0", "G1b", "G1c", "pre-G2 stop", "G2", "G2c"]


# Addition after the G1c defect: G1c from the documented successor record.


def test_g1c_comes_from_the_successor_when_no_line_is_complete(
    env: dict[str, Path], report: dict[str, Any]
) -> None:
    lines = (env["gate"] / "criteria.jsonl").read_text().splitlines()
    g1c = [json.loads(line) for line in lines if '"gate": "G1c"' in line]
    assert g1c and all(line["completed"] < line["planned"] for line in g1c)
    sealed_only = _env_gate(env)
    assert sealed_only.verdict("G1c") == IN_PROGRESS
    assert ("G1c", "task records sealed", "150/150", "", IN_PROGRESS) in (
        table_t3(sealed_only, None).rows
    )
    t3 = {
        row["item"]: row
        for row in _table(report["out"], "T3_gate_summary")
        if row["stage"] == "G1c"
    }
    assert t3["tasks completed"]["value"] == "150/150"
    assert t3["summary source"]["value"] == SUCCESSOR_SOURCE
    assert {row["stage_pass"] for row in t3.values()} == {"pass"}
    manifest = json.loads((report["out"] / "manifest.json").read_text())
    assert manifest["inputs"]["stage_successors"] == [
        {
            "name": env["successor"].name,
            "sha256": _sha256(env["successor"]),
            "stage": "G1c",
            "used": True,
        }
    ]
    strip = [
        " ".join(text.split())
        for text in _texts(report["figures"]["F4_gate_diagnostics"])
    ]
    assert f"150/150 tasks · pass · {SUCCESSOR_SOURCE}" in strip


def _successor_record_mutations() -> list[tuple[str, Any, str]]:
    def identifier(d: dict[str, Any]) -> None:
        d["sealed_root_identifier"] = "0" * 64

    def freeze(d: dict[str, Any]) -> None:
        d["freeze_sha256"] = "0" * 64

    def schema(d: dict[str, Any]) -> None:
        d["schema"] = "ic-study.v4-stage-summary-successor.v2"

    def incomplete(d: dict[str, Any]) -> None:
        d["summary"]["completed"] = 149

    def stage(d: dict[str, Any]) -> None:
        d["stage"] = "G1b"

    def undocumented(d: dict[str, Any]) -> None:
        d["note"] = "edited by hand"

    return [
        (f.__name__, f, match)
        for f, match in (
            (identifier, "another sealed gate root"),
            (freeze, "freeze differs"),
            (schema, "not a v4 stage-summary successor"),
            (incomplete, "incomplete"),
            (stage, "another stage"),
            (undocumented, "documented schema"),
        )
    ]


@pytest.mark.parametrize(("name", "mutate", "match"), _successor_record_mutations())
def test_successor_record_must_match_the_gate_root(
    env: dict[str, Path], tmp_path: Path, name: str, mutate: Any, match: str
) -> None:
    data = json.loads(env["successor"].read_text())
    mutate(data)
    path = tmp_path / "successor.json"
    _write_json(path, data)
    with pytest.raises(SchemaError, match=match):
        _env_gate(env, path)


def test_successor_must_match_the_sealed_task_records(
    env: dict[str, Path], tmp_path: Path
) -> None:
    plan = GatePlan(stages=("G1c",), skip_tasks=frozenset({"G1c-00149"}))
    root = build_gate(tmp_path / env["gate"].name, plan)
    with pytest.raises(SchemaError, match="sealed G1c task records"):
        load_gate(root, successors=[env["successor"]])


def test_a_complete_sealed_line_takes_precedence_over_a_successor(
    failures: Path, tmp_path: Path
) -> None:
    path = tmp_path / "successor.json"
    _write_json(path, stage_successor(failures))
    gate = load_gate(failures, successors=[path], synthetic=True)
    assert gate.from_successor == frozenset()
    assert gate.summaries["G1c"]["failures"] == 1


# Defect 3: sustained interval whose lower end lies above the last gap.


def test_sustained_upper_end_above_the_last_gap_is_not_reached(
    report: dict[str, Any], release: Release
) -> None:
    sustained = release.curves[B[0.65]].sustained
    assert sustained.interval is not None
    lower, upper = sustained.interval
    assert upper is None and lower is not None and lower > 0.003
    assert sustained.interval_censoring == "gap at a=0.003"  # frozen flag
    row = next(
        r
        for r in _table(report["out"], "T1_a_star_grid")
        if r["family"] == "B" and r["r"] == "0.65"
    )
    assert (row["a_s_star_lower"], row["a_s_star_upper"]) == (f"{lower:g}", ">0.9")
    figure = report["figures"]["F6_a_star_shp_anchor"]
    x = 0.65 + 0.009
    ax = figure.axes[0]
    bars = [
        line
        for line in ax.lines
        if len(line.get_xdata()) == 2 and np.allclose(line.get_xdata(), x)
    ]
    assert len(bars) == 1 and list(bars[0].get_ydata())[1] == BEYOND_Y
    assert any(
        line.get_marker() == "^"
        and np.allclose(line.get_xdata(), x)
        and np.allclose(line.get_ydata(), BEYOND_Y)
        for line in ax.lines
    )
    for panel in figure.axes:
        for line in panel.lines:
            xs, ys = list(line.get_xdata()), list(line.get_ydata())
            if len(xs) == 2 and xs[0] == xs[1]:
                assert ys[0] <= ys[1], "an interval bar is drawn downward"


# Defect 4: the caption states the frozen solver budget.


def test_gate_figure_marks_the_frozen_solver_budget() -> None:
    assert SOLVER_BUDGET == 96


def test_captions_state_the_frozen_solver_budget() -> None:
    text = CAPTIONS.read_text(encoding="utf-8")
    assert set(re.findall(r"budget of (\d+)", text)) == {str(SOLVER_BUDGET)}


# Defect 5: G2 placeholders when a cell keeps fewer than two intact pairs.


def test_inestimable_g2_ratios_are_neither_printed_nor_plotted(
    failures: Path, tmp_path: Path
) -> None:
    gate = load_gate(failures)
    summary = gate.summaries["G2"]
    assert summary["cell_ratios"] == [] and summary["pooled_ratio"] == 0
    rows = {row[1]: row for row in table_t3(gate, None).rows if row[0] == "G2"}
    assert rows["dispersion ratio"][2] == "not estimable"
    pairs = " ".join(map(str, summary["successful_pair_counts"]))
    assert rows["successful pairs by cell"][2] == pairs and pairs.startswith("1 ")
    assert not any("0.000 [0.000, 0.000]" in row[2] for row in rows.values())
    with _captured_figures() as figures:
        figure_gate(gate, Render(tmp_path, dpi=40), None)
    texts = "\n".join(_texts(figures["F4_gate_diagnostics"]))
    assert "not estimable" in texts and pairs in texts


def _gate_with_summary(tmp_path: Path, summary: dict[str, Any]) -> GateRecords:
    gate = load_gate(build_gate(tmp_path / "gate", GatePlan(stages=())))
    stage = summary["gate"]
    return replace(
        gate,
        summaries={stage: parse_summary(summary)},
        summary_counts={stage: 1},
        sealed={stage: summary["completed"]},
        g2_cells=G2_CELLS,
    )


def _assert_ratio_geometry(
    panel: Axes, point: float, lower: float, upper: float, y: int
) -> None:
    assert any(
        line.get_marker() == "o"
        and any(
            x == point and row == y
            for x, row in cast(NDArray[np.float64], line.get_xydata())
        )
        for line in panel.lines
    )
    assert any(
        np.array_equal(segment, [[lower, y], [upper, y]])
        for collection in panel.collections
        if isinstance(collection, LineCollection)
        for segment in collection.get_segments()
    )
    for end in (lower, upper):
        assert any(
            line.get_marker() == "|"
            and any(
                x == end and row == y
                for x, row in cast(NDArray[np.float64], line.get_xydata())
            )
            for line in panel.lines
        )


def test_f4_preserves_percentile_dispersion_interval_outside_point(
    tmp_path: Path,
) -> None:
    pair = np.array([[0.507, 0.493], [0.493, 0.507]])
    estimates = np.tile(pair.ravel(), 25)[None, :].repeat(7, axis=0)
    report = dispersion(
        estimates,
        np.full_like(estimates, 0.01),
        np.ones_like(estimates, dtype=bool),
        seed=80925,
    )
    thresholds = json.loads(CRITERIA.read_bytes())["thresholds"]
    assert dispersion_pass(report, thresholds)
    assert report["pooled_upper"] < report["pooled_ratio"]
    gate = _gate_with_summary(
        tmp_path,
        {"gate": "G2", "planned": 700, "completed": 700, "pass": True, **report},
    )
    before = copy.deepcopy(gate.summaries)
    with _captured_figures() as figures:
        figure_gate(gate, Render(tmp_path, formats=()), thresholds)
    _assert_ratio_geometry(
        figures["F4_gate_diagnostics"].axes[4],
        0.99973867349666,
        0.9535793107432141,
        0.9953969512574744,
        7,
    )
    assert gate.summaries == before


@pytest.mark.parametrize("lower,upper", [(0.9, 0.95), (1.05, 1.1)])
def test_f4_preserves_refit_interval_on_either_side_of_point(
    tmp_path: Path, lower: float, upper: float
) -> None:
    comparison = {"ratio": 1.0, "lower": lower, "upper": upper}
    gate = _gate_with_summary(
        tmp_path,
        {
            "gate": "G2c",
            "planned": 142,
            "completed": 142,
            "failures": 0,
            "pass": True,
            "comparisons": [comparison, comparison.copy()],
        },
    )
    before = copy.deepcopy(gate.summaries)
    with _captured_figures() as figures:
        figure_gate(gate, Render(tmp_path, formats=()), None)
    for y in (0, 1):
        _assert_ratio_geometry(
            figures["F4_gate_diagnostics"].axes[5], 1.0, lower, upper, y
        )
    assert gate.summaries == before


@pytest.mark.parametrize("missing", [0, 1])
def test_f4_keeps_each_estimable_g2c_comparison_on_its_row(
    tmp_path: Path, missing: int
) -> None:
    local = np.tile([-0.1, 0.1], 1000)
    comparisons = [
        refit_ratio(local, np.tile([-0.1, 0.1], 50), seed=80925),
        refit_ratio(local, np.tile([-0.1, 0.1], 20), seed=80925),
    ]
    count = 100 if missing == 0 else 40
    comparisons[missing] = refit_ratio(
        local, np.array([0.1, *([float("nan")] * (count - 1))]), seed=80925
    )
    gate = _gate_with_summary(
        tmp_path,
        {
            "gate": "G2c",
            "planned": 142,
            "completed": 142,
            "failures": count - 1,
            "pass": False,
            "comparisons": comparisons,
        },
    )
    before = copy.deepcopy(gate.summaries)
    with _captured_figures() as figures:
        figure_gate(gate, Render(tmp_path, formats=()), None)
    panel = figures["F4_gate_diagnostics"].axes[5]
    good = comparisons[1 - missing]
    _assert_ratio_geometry(
        panel,
        cast(float, good["ratio"]),
        cast(float, good["lower"]),
        cast(float, good["upper"]),
        1 - missing,
    )
    assert [tick.get_text() for tick in panel.get_yticklabels()] == [
        "a=0.10 (100)",
        "a=0.03 (40)",
    ]
    assert any(
        "not estimable" in text.get_text() and text.get_position()[1] == missing
        for text in panel.texts
    )
    assert gate.summaries == before


# Defect 6: family limits separated from fit failures.


def test_gap_kinds_are_separate_in_t1_t4_and_f4(report: dict[str, Any]) -> None:
    t1s = {
        (row["tier"], row["family"], row["channel"], row["r"]): row
        for row in _table(report["out"], "T1s_a_star_all_units")
        if row["sensitivity"] == "main"
    }

    def kinds(tier: str, family: str, channel: str, r: str) -> dict[str, int]:
        row = t1s[(tier, family, channel, r)]
        counts = {kind: int(row[f"gaps_{kind}"]) for kind in GAP_KINDS}
        assert sum(counts.values()) == int(row["gaps"])
        return {kind: n for kind, n in counts.items() if n}

    assert kinds("2", "C", "observed", "0.55") == {"screened": 2}
    assert kinds("2", "C", "observed", "0.60") == {"family_limit": 1}
    assert kinds("2", "D", "observed", "0.55") == {"validation": 1}
    assert kinds("2", "E", "observed", "0.50") == {"solver": 9}
    assert kinds("3", "B", "latent", "0.55") == {"dependency": 1}
    t4 = {
        (row["tier"], row["family"], row["channel"], row["sensitivity"]): row
        for row in _table(report["out"], "T4_inventory")
    }
    total = t4[("all", "all", "all", "all")]
    # 11 solver gaps: E at r=0.50 (9) and B at r=0.55 and 0.65 (1 each).
    assert {kind: total[f"gap_cells_{kind}"] for kind in GAP_KINDS} == {
        "screened": "2",
        "family_limit": "1",
        "solver": "11",
        "validation": "1",
        "dependency": "1",
        "propagation": "0",
    }
    panel = report["figures"]["F4_gate_diagnostics"].axes[0]
    colors = {
        label.get_text(): to_hex(bar.get_facecolor()).upper()
        for label, bar in zip(panel.get_yticklabels(), panel.patches, strict=True)
    }
    assert colors["family-limit-upper, screened"] == GAP_COLOR["screened"]
    assert colors["family-limit-upper, profile"] == GAP_COLOR["family_limit"]
    assert colors["no-L1-root"] == colors["non-monotone-profile"] == GAP_COLOR["solver"]
    assert colors["interior, validation failed"] == GAP_COLOR["validation"]
    assert colors["dependency gap"] == GAP_COLOR["dependency"]
    assert len({GAP_COLOR[kind] for kind in (None, *GAP_KINDS)}) == 7


# Design decision: frozen v1 regions, with the interval deciding "IC amplo".


@pytest.mark.parametrize(
    ("first", "expected"),
    [
        (Boundary(0.01, (0.003, 0.03), None, None), "small"),
        (Boundary(0.1, (0.1, 0.3), None, None), "large"),
        (Boundary(0.03, (0.01, 0.1), None, None), "indeterminate"),
        (Boundary(0.1, (0.03, 0.3), None, None), "indeterminate"),
        (Boundary(0.3, (0.1, None), None, None), "indeterminate"),
        (Boundary(0.01, (0.003, None), None, "gap at a=0.3"), "indeterminate"),
        (Boundary(0.0, (0.0, 0.01), None, None), "indeterminate"),
        (Boundary(None, None, None, None), "not attained"),
        (
            Boundary(None, (None, None), "gap at a=0.3", "gap at a=0.3"),
            "censored (gap)",
        ),
    ],
)
def test_region_uses_frozen_regions_and_the_interval(
    release: Release, first: Boundary, expected: str
) -> None:
    assert region(replace(release.curves[B[0.5]], first=first)) == expected


# Design decision: the second binding labels G2 and binds the criteria.


def test_g2_cells_come_from_the_binding_that_also_binds_the_criteria(
    env: dict[str, Path], report: dict[str, Any], tmp_path: Path
) -> None:
    a, r = load_allocation(env["allocation"]).cells[0]
    items = [
        row["item"]
        for row in _table(report["out"], "T3_gate_summary")
        if row["stage"] == "G2"
    ]
    assert f"dispersion ratio, cell 1 (a={a:g}, r={r:.2f})" in items
    panel = report["figures"]["F4_gate_diagnostics"].axes[4]
    assert panel.get_yticklabels()[0].get_text() == f"a={a:g}, r={r:.2f}"
    other = tmp_path / "criteria-v43.json"
    data = json.loads(CRITERIA.read_text(encoding="utf-8"))
    data["thresholds"]["cell_lower"] = 0.4
    other.write_text(json.dumps(data), encoding="utf-8")
    out = tmp_path / "out"
    inputs = Inputs(
        env["curves"], env["gate"], None, other, allocation=env["allocation"]
    )
    with pytest.raises(SchemaError, match="not the criteria bound"):
        render(inputs, out)
    assert not out.exists()
    moved = json.loads(env["allocation"].read_text(encoding="utf-8"))
    moved["g2_cells"] = moved["g2_cells"][::-1]
    _write_json(tmp_path / "moved.json", moved)
    with pytest.raises(SchemaError, match="authorized G2"):
        load_gate(env["gate"], allocation=load_allocation(tmp_path / "moved.json"))
    unbound = tmp_path / "unbound"
    with pytest.raises(SchemaError, match="second binding"):
        render(Inputs(env["curves"], env["gate"], None, CRITERIA), unbound)
    assert not unbound.exists()


# Design decision: secondary targets derived from the released bands.


def test_secondary_targets_are_derived_from_released_bands(
    report: dict[str, Any], release: Release
) -> None:
    t1 = {(r["family"], r["r"]): r for r in _table(report["out"], "T1_a_star_grid")}
    curve = release.curves[B[0.5]]
    grid, auc, lower, upper = (
        np.array(values)
        for values in (curve.available, curve.auc, curve.lower, curve.upper)
    )
    for target, label in ((0.6, "060"), (0.8, "080")):
        expected = [boundary(grid, band, target) for band in (auc, upper, lower)]
        cells = [
            t1[("B", "0.50")][f"derived_a_star_{label}{s}"]
            for s in ("", "_lower", "_upper")
        ]
        assert cells == [">0.9" if v is None else f"{v:g}" for v in expected]
    # Gap at a=0.3: the 0.60 crossing lies beyond it, so it is censored there.
    assert t1[("B", "0.55")]["derived_a_star_060"] == "censored at gap a=0.3"


# Edge renders -----------------------------------------------------------------


def _edge_render(root: Path, plans: dict[str, UnitPlan], **kw: Any) -> dict[str, Any]:
    curves = _release(root, plans)
    out = root / "out"
    with _captured_figures() as figures:
        render(Inputs(curves, kw.get("gate"), kw.get("shp")), out, dpi=40)
    return {
        "files": set(_outputs(out)),
        "t1": _table(out, "T1_a_star_grid"),
        "figures": figures,
    }


def test_all_censored_curve(tmp_path: Path) -> None:
    plans = {
        k: UnitPlan(logistic_profile(0.3), gaps=frozenset({4})) for k in B.values()
    }
    result = _edge_render(tmp_path, plans)
    rows = [r for r in result["t1"] if r["family"] == "B"]
    assert {r["region"] for r in rows} == {"censored (gap)"}
    assert all(r["a_star"] == "censored at gap a=0.03" for r in rows)
    # Every tier-1 unit is valid: the main curve carries no invalidation mark.
    assert {r["main_curve_flag"] for r in rows} == {""}
    assert not any(
        MAIN_CURVE_INVALID in text
        for fig in result["figures"].values()
        for text in _texts(fig)
    )


def test_all_invalid_curve(tmp_path: Path) -> None:
    plans = {k: UnitPlan((0.58, *logistic_profile(0.05)[1:])) for k in B.values()}
    result = _edge_render(tmp_path, plans)
    rows = [r for r in result["t1"] if r["family"] == "B"]
    assert {(r["status"], r["null_gate"], r["a_star"]) for r in rows} == {
        (INVALID, "fail", "suppressed")
    }
    assert "F1_a_star_by_family.pdf" in result["files"]


def test_missing_family_partial_units_and_absent_shp_and_gate(tmp_path: Path) -> None:
    plans = {B[0.5]: UnitPlan(logistic_profile(0.05))}
    plans |= {k: UnitPlan(logistic_profile(0.05), partial_cells=2) for k in C.values()}
    result = _edge_render(tmp_path, plans)
    assert "F2_auc_profiles_D.png" in result["files"]
    assert not any(n.startswith(("F6", "F4", "T3")) for n in result["files"])
    statuses = {r["status"] for r in result["t1"] if r["family"] == "C"}
    assert statuses == {PARTIAL}


def test_inventory_legend_lies_inside_the_figure(
    release: Release, tmp_path: Path
) -> None:
    with _captured_figures() as figures:
        figure_inventory(release, Render(tmp_path, dpi=40))
    fig = figures["F5_inventory_status"]
    box = fig.legends[0].get_window_extent()
    assert fig.bbox.x0 <= box.x0 and box.x1 <= fig.bbox.x1


# Freeze guard --------------------------------------------------------------


# Dependency edits made on this branch before the reporting work (43bbe374 added
# matplotlib; 4c204d38 added pyreadstat/scipy). The gate runs from 37513841.
KNOWN_PRE_EXISTING_DRIFT = frozenset({"pyproject.toml", "uv.lock"})


def test_frozen_files_are_untouched() -> None:
    freeze = json.loads((V4 / "freeze-v4.json").read_text())
    drift = {
        relative
        for relative, digest in freeze["code"].items()
        if hashlib.sha256((STUDY / relative).read_bytes()).hexdigest() != digest
    }
    assert drift == KNOWN_PRE_EXISTING_DRIFT
    shp = json.loads(
        (
            STUDY
            / "research/questions/exploration/2026-09-24-parallel"
            / "shp-reliability-freeze.json"
        ).read_text()
    )
    for record in shp["preregistration"].values():
        path = STUDY.parents[1] / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]


def test_production_report_requires_the_release_receipt(tmp_path: Path) -> None:
    from ic_study.analysis.detection_v4_report import load_inputs

    curves = _release(tmp_path, {})
    curves.with_name("release-record.json").unlink(missing_ok=True)
    with pytest.raises(SchemaError, match="release-record"):
        load_inputs(Inputs(curves, None))


def _receipt(curves: Path, **changes: Any) -> Path:
    record = curves.with_name("release-record.json")
    _write_json(
        record,
        {
            "schema": 1,
            "condition": "declared-close",
            "released_utc": "2026-10-19T03:00:00Z",
            "released_curves_sha256": _sha256(curves),
            "script_sha256": "1" * 64,
            "amendment": {
                "path": "studies/ic-2026-2027/research/questions/exploration/"
                "2026-09-24-parallel/detection-boundary-v4-release-amendment.md",
                "commit": "428ca7cd6158244b494dcb520b9a69738b5bfae6",
            },
            **changes,
        },
    )
    return record


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"released_curves_sha256": "0" * 64}, "SHA-256"),
        ({"condition": "manual"}, "condition"),
        ({"released_utc": "2026-10-08T12:00:00Z"}, "close"),
        ({"released_utc": "2026-10-19T03:00:00"}, "UTC"),
        ({"released_utc": "not a timestamp"}, "UTC"),
        (
            {"condition": "inventory-complete", "released_utc": "2026-10-08T12:00:00Z"},
            "414",
        ),
        ({"condition": "inventory-complete"}, "close"),
    ],
)
def test_receipt_must_bind_bytes_time_condition_and_completeness(
    tmp_path: Path, changes: dict[str, Any], message: str
) -> None:
    from ic_study.analysis.detection_v4_report import load_inputs

    curves = _release(tmp_path, {})
    receipt = _receipt(curves, **changes)
    with pytest.raises(SchemaError, match=message):
        load_inputs(Inputs(curves, None, release_record=receipt))


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"mean_z": 999.0}, "G1c.*predicate"),
        ({"pointwise_failures": 150}, "G1c.*predicate"),
        ({"anchor_count": 149}, "G1c.*predicate"),
        ({"pass": False}, "G1c.*predicate"),
        ({"failures": 1}, "G1c.*predicate"),
    ],
)
def test_g1c_successor_rejects_inconsistent_frozen_predicate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    changes: dict[str, Any],
    message: str,
) -> None:
    from ic_study.analysis import v4_report_schema

    gate = build_gate(tmp_path / "gate", GatePlan(stages=("G1c",)))
    data = stage_successor(gate)
    data["summary"].update(changes)
    path = tmp_path / "successor.json"
    _write_json(path, data)
    monkeypatch.setattr(
        v4_report_schema, "APPROVED_G1C_SHA256", _sha256(path), raising=False
    )
    with pytest.raises(SchemaError, match=message):
        load_gate(gate, successors=(path,))


def test_production_g1c_requires_the_independently_approved_digest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ic_study.analysis import v4_report_schema

    monkeypatch.setattr(
        v4_report_schema,
        "APPROVED_G1C_SHA256",
        "a945e8484791f886289d51b083886854b4f540f6b26dcf1463d8d4c9dcd9a4d6",
        raising=False,
    )
    gate = build_gate(tmp_path / "gate", GatePlan(stages=("G1c",)))
    path = tmp_path / "successor.json"
    _write_json(path, stage_successor(gate))
    with pytest.raises(SchemaError, match=r"approved.*digest"):
        load_gate(gate, successors=(path,))


def test_consistent_g1c_with_the_approved_digest_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ic_study.analysis import v4_report_schema

    gate = build_gate(tmp_path / "gate", GatePlan(stages=("G1c",)))
    path = tmp_path / "successor.json"
    _write_json(path, stage_successor(gate))
    monkeypatch.setattr(
        v4_report_schema, "APPROVED_G1C_SHA256", _sha256(path), raising=False
    )
    assert load_gate(gate, successors=(path,)).verdict("G1c") == "pass"


def test_complete_early_receipt_is_accepted_and_bound_to_manifest(
    tmp_path: Path,
) -> None:
    from ic_study.analysis.detection_v4_report import input_record, load_inputs
    from ic_study.analysis.v4_report_schema import unit_catalog

    curves = _release(
        tmp_path, {B[0.5]: UnitPlan((0.5,) * 9, gaps=frozenset(range(9)))}
    )
    data = json.loads(curves.read_bytes())
    template = data["curves"][0]
    data["curves"] = []
    for row in data["inventory"]["units"]:
        row["status"] = INVALID
        curve = copy.deepcopy(template)
        curve["unit"] = row["unit"]
        if unit_catalog()[row["unit"]].tier != 1:
            curve.pop("main_curve_valid", None)
        data["curves"].append(curve)
    _write_json(curves, data)
    receipt = _receipt(
        curves, condition="inventory-complete", released_utc="2026-10-08T12:00:00Z"
    )
    inputs = Inputs(curves, None, release_record=receipt)
    loaded = load_inputs(inputs)
    assert loaded.release is not None and len(loaded.release.curves) == 414
    assert input_record(inputs, loaded)["release_record"] == {
        "name": receipt.name,
        "sha256": _sha256(receipt),
        "condition": "inventory-complete",
        "released_utc": "2026-10-08T12:00:00Z",
    }


def test_publication_figures_preserve_minimum_type_at_print_size(
    report: dict[str, Any],
) -> None:
    from matplotlib.text import Text

    from ic_study.analysis.v4_report_figures import MM

    for fig in report["figures"].values():
        width, height = fig.get_size_inches()
        assert width == pytest.approx(76 * MM) or width == pytest.approx(160 * MM)
        assert height <= 175 * MM
        assert all(
            text.get_fontsize() >= 8
            for text in fig.findobj(Text)
            if text.get_visible() and text.get_text()
        )
    assert (
        "nominal strength"
        in report["figures"]["F6_a_star_shp_anchor"].axes[0].get_ylabel()
    )
    assert (
        "signal share" in report["figures"]["F6_a_star_shp_anchor"].axes[0].get_xlabel()
    )
    for name, note_texts in (
        ("F2_auc_profiles_B", report["figures"]["F2_auc_profiles_B"].texts),
        (
            "F4_gate_diagnostics",
            report["figures"]["F4_gate_diagnostics"].axes[-1].texts,
        ),
    ):
        fig = report["figures"][name]
        fig.canvas.draw()
        for text in note_texts:
            box = text.get_window_extent()
            assert fig.bbox.x0 <= box.x0 and box.x1 <= fig.bbox.x1
            assert fig.bbox.y0 <= box.y0 and box.y1 <= fig.bbox.y1


def test_inventory_statuses_have_noncolour_symbols(report: dict[str, Any]) -> None:
    texts = report["figures"]["F5_inventory_status"].axes[0].texts
    assert {text.get_text() for text in texts} == {"N", "P", "I", "V"}


def test_inventory_status_labels_are_english_in_all_figures(
    report: dict[str, Any],
) -> None:
    texts = {
        name: " ".join(" ".join(_texts(fig)).split())
        for name, fig in report["figures"].items()
    }
    for text in texts.values():
        assert not any(status in text for status in STATUSES)
    for name in ("F1_a_star_by_family", "F6_a_star_shp_anchor"):
        for label in (
            "complete invalid",
            "partial at operational close",
            "not started",
        ):
            assert label in texts[name]
    assert "complete valid" in texts["F2_auc_profiles_B"]
    assert "not started" in texts["F2_auc_profiles_B"]
    assert "complete invalid; a* suppressed" in texts["F2_auc_profiles_C"]
    assert "partial at operational close" in texts["F2_auc_profiles_D"]
    for label in (
        "N: not started",
        "P: partial at operational close",
        "I: complete invalid",
        "V: complete valid",
    ):
        assert label in texts["F5_inventory_status"]
