"""Amendment v4.4 propagation gaps through the v4 report, from the successor worker."""

from __future__ import annotations

import copy
import functools
import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import pytest
from matplotlib.figure import Figure

from ic_study.analysis import v4_report_figures
from ic_study.analysis.detection_v4_report import Inputs, Loaded, load_inputs
from ic_study.analysis.v4_public_aggregates import (
    _parse_public,
    digest,
    load_public,
    project,
)
from ic_study.analysis.v4_report_export import CAPTION_T4, generated_files
from ic_study.analysis.v4_report_figures import (
    _GAP_LABEL,
    GAP_COLOR,
    OKABE_ITO,
    Render,
    figure_profiles,
)
from ic_study.analysis.v4_report_schema import (
    GAP_KINDS,
    INVALID,
    VALID,
    CellDiagnostics,
    Release,
    SchemaError,
    _fit_outcome,
    gap_kind,
    parse_curve,
    parse_release,
    unit_catalog,
)
from ic_study.analysis.v4_report_synthetic import (
    GatePlan,
    UnitPlan,
    build_gate,
    build_release,
    logistic_profile,
    write_release,
)
from ic_study.analysis.v4_report_tables import table_t1_full, table_t4
from ic_study.simulation import v4_curve
from ic_study.simulation.detection_v4 import RELIABILITIES
from ic_study.simulation.v4_store import SealedStore

STUDY = Path(__file__).resolve().parents[2]
RUNNER = (
    STUDY
    / "experiments/exploratory/detection-boundary-v4-successor-v44/v44_run_curve.py"
)
CRITERIA = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
INCIDENT = "t2-u03-r2"  # D at r = 0.60, whose cell a = 0.003 raised the error
NULL = "t2-u03-r0"  # the same error at a = 0
MIXED = "t2-u03-r3"  # the same error beside a solver gap
Cell = dict[str, Any]


@pytest.fixture(scope="module")
def successor() -> ModuleType:
    spec = importlib.util.spec_from_file_location("v44_run_curve_for_report", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def released(
    tmp_path_factory: pytest.TempPathFactory, successor: ModuleType
) -> dict[str, Any]:
    """Frozen curve emitters, with the amendment v4.4 worker for every cell."""
    root = tmp_path_factory.mktemp("v44-report")
    profile = logistic_profile(0.015)
    plans = {
        INCIDENT: UnitPlan(profile, propagation_errors=frozenset({2})),
        NULL: UnitPlan(profile, propagation_errors=frozenset({0})),
        MIXED: UnitPlan(
            profile, gaps=frozenset({5}), propagation_errors=frozenset({3})
        ),
    }
    worker = functools.partial(
        successor.successor_worker,
        execute_cell=v4_curve.execute_cell,
        store_type=SealedStore,
    )
    curves = root / "released_curves.json"
    write_release(
        curves, build_release(root / "confirmatory", plans, draws=40, worker=worker)
    )
    return {"curves": curves, "raw": json.loads(curves.read_text(encoding="utf-8"))}


@pytest.fixture(scope="module")
def release(released: dict[str, Any]) -> Release:
    return parse_release(copy.deepcopy(released["raw"]))


def _curve(raw: dict[str, Any], key: str) -> dict[str, Any]:
    return copy.deepcopy(next(c for c in raw["curves"] if c["unit"] == key))


def test_successor_record_is_read_as_a_propagation_gap(
    released: dict[str, Any], release: Release, successor: ModuleType
) -> None:
    record = _curve(released["raw"], INCIDENT)["cells"][2]
    assert record == successor.gap_record()
    curve = release.curves[INCIDENT]
    assert curve.cell_gap == (None, None, "propagation", *(None,) * 6)
    assert curve.cell_success[2] is False and curve.cell_final_status[2] is None
    assert curve.gap_count == 1 and not curve.band_complete
    assert curve.diagnostics[2] == CellDiagnostics((), (), None, None, None, None, None)
    # A positive-strength gap censors boundaries and keeps the unit valid.
    assert curve.status == VALID
    assert curve.first.point is None and curve.first.censored_at == 0.003
    # At a = 0 the unit loses its null gate, as with any other gap there.
    null = release.curves[NULL]
    assert null.cell_gap[0] == "propagation" and null.status == INVALID


def test_gap_kind_recognizes_exactly_the_amendment_record(
    successor: ModuleType,
) -> None:
    gap = successor.gap_record()["successor_gap"]
    assert gap_kind(False, [], False, gap) == "propagation"
    for success, attempts, dependency in (
        (True, [], False),
        (False, [{"status": "no-L1-root", "evaluations": 18}], False),
        (False, [], True),
    ):
        with pytest.raises(SchemaError, match=r"amendment v4\.4"):
            gap_kind(success, attempts, dependency, gap)
    # Without a successor record nothing changes.
    assert gap_kind(False, [], True) == "dependency"
    with pytest.raises(SchemaError, match="must be a dependency gap"):
        gap_kind(False, [], False)


def _set(field: str, value: object) -> Callable[[Cell], None]:
    return lambda cell: cell["successor_gap"].update({field: value})


MALFORMED: dict[str, Callable[[Cell], None]] = {
    "extra field": _set("note", "x"),
    "missing field": lambda cell: cell["successor_gap"].pop("function"),
    "other amendment": _set("amendment", "v4.3"),
    "other kind": _set("kind", "solver"),
    "other error": _set("error", "singular matrix"),
    "other function": _set("function", "profile_match"),
    "uppercase digest": _set("successor_sha256", "A" * 64),
    "short digest": _set("successor_sha256", "a" * 63),
    "digest not text": _set("successor_sha256", None),
    "null record": lambda cell: cell.update(successor_gap=None),
    "record not an object": lambda cell: cell.update(successor_gap=[]),
    "successful cell": lambda cell: cell.update(success=True),
    "cell with attempts": lambda cell: cell.update(
        attempts=[{"status": "no-L1-root", "evaluations": 18}]
    ),
    "dependency gap": lambda cell: cell.update(dependency_gap=True),
    "extra cell field": lambda cell: cell.update(nuisance_variance=[0.1]),
    "no dependency flag": lambda cell: cell.pop("dependency_gap"),
}


@pytest.mark.parametrize("mutate", MALFORMED.values(), ids=list(MALFORMED))
def test_malformed_successor_records_are_refused(
    released: dict[str, Any], mutate: Callable[[Cell], None]
) -> None:
    meta = unit_catalog()[INCIDENT]
    record = _curve(released["raw"], INCIDENT)
    parse_curve(copy.deepcopy(record), meta)
    mutate(record["cells"][2])
    with pytest.raises(SchemaError, match=r"successor_gap|amendment v4\.4"):
        parse_curve(record, meta)


def test_failed_cells_without_the_record_keep_the_frozen_rule(
    released: dict[str, Any], successor: ModuleType
) -> None:
    record = _curve(released["raw"], INCIDENT)
    del record["cells"][2]["successor_gap"]
    with pytest.raises(SchemaError, match="must be a dependency gap"):
        parse_curve(record, unit_catalog()[INCIDENT])
    # The gate runner was not amended: a G0 fit never becomes a propagation gap.
    with pytest.raises(SchemaError, match="must be a dependency gap"):
        _fit_outcome(successor.gap_record())


def test_counts_by_kind_include_propagation(release: Release) -> None:
    assert release.curves[MIXED].gap_counts() == dict.fromkeys(GAP_KINDS, 0) | {
        "solver": 1,
        "propagation": 1,
    }
    t1s = table_t1_full(release)
    row = dict(
        zip(t1s.header, t1s.rows[list(unit_catalog()).index(MIXED)], strict=True)
    )
    assert (row["gaps"], row["gaps_solver"], row["gaps_propagation"]) == ("2", "1", "1")
    t4 = table_t4(release)
    totals = {row[:4]: dict(zip(t4.header, row, strict=True)) for row in t4.rows}
    for scope in (("2", "all", "all", "all"), ("all", "all", "all", "all")):
        assert totals[scope]["gap_cells_propagation"] == "3"
        assert totals[scope]["gap_cells_solver"] == "1"
    assert totals[("1", "all", "all", "all")]["gap_cells_propagation"] == "0"


def test_t4_export_adds_the_propagation_column_and_caption(release: Release) -> None:
    loaded = Loaded(release, None, None, None, None, None)
    files, cells = generated_files(loaded, lambda stem: stem + ".pdf", True)
    lines = files["unit-status"]
    spec = next(line for line in lines if line.startswith(r"\begin{tabular}"))
    header = next(line for line in lines if line.startswith("Tier & "))
    assert header.endswith(r"& dep. & prop. \\")
    assert len(spec.removeprefix(r"\begin{tabular}{").rstrip("}")) == (
        header.count("&") + 1
    )
    assert cells["v4.tab.T4.2-all-all-all.gaps_propagation"] == "3"
    assert cells["v4.tab.T4.all-all-all-all.gaps_propagation"] == "3"
    assert cells["v4.tab.T4.1-all-all-all.gaps_propagation"] == "0"
    explanation = (
        "dep. control whose observed fit failed, prop. ill-conditioned nuisance "
        "propagation recorded as a gap by amendment v4.4. Family limits"
    )
    assert explanation in CAPTION_T4
    assert any(explanation in line for line in lines if line.startswith(r"\caption"))


def test_figures_give_the_propagation_gap_its_own_colour_and_label() -> None:
    assert set(GAP_COLOR) == {None, *GAP_KINDS} == {None, *_GAP_LABEL}
    assert GAP_COLOR["propagation"] in OKABE_ITO.values()
    assert len(set(GAP_COLOR.values())) == len(GAP_COLOR)
    assert _GAP_LABEL["propagation"] == "propagation gap (amendment v4.4)"


def test_f2_marks_the_propagation_gap_and_its_censoring(
    release: Release, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    drawn: dict[str, Figure] = {}
    real = v4_report_figures.save

    def spy(fig: Figure, options: Render, name: str) -> list[Path]:
        drawn[name] = fig
        return real(fig, options, name)

    monkeypatch.setattr(v4_report_figures, "save", spy)
    figure_profiles(release, Render(tmp_path, dpi=40, formats=()), "D")
    panel = drawn["F2_auc_profiles_D"].axes[RELIABILITIES.index(0.6)]
    crosses = [
        (np.asarray(line.get_xdata()).tolist(), np.asarray(line.get_ydata()).tolist())
        for line in panel.lines
        if line.get_marker() == "x"
    ]
    assert crosses == [([2], [0.47])]
    assert "a* censored at gap a=0.003" in panel.texts[0].get_text()


def _rehash(data: dict[str, Any]) -> None:
    data["objects_sha256"] = {k: digest(v) for k, v in data["objects"].items()}
    data["sha256"] = digest({k: v for k, v in data.items() if k != "sha256"})


def test_public_aggregates_carry_propagation_gaps_only_in_curve_cells(
    released: dict[str, Any], tmp_path: Path
) -> None:
    gate = build_gate(tmp_path / "gate", GatePlan(stages=("G0",)))
    inputs = Inputs(released["curves"], gate, criteria=CRITERIA)
    authorized = load_inputs(inputs, synthetic=True)
    projection = project(inputs, tmp_path / "public-aggregates.json", synthetic=True)
    public = load_public(projection).loaded
    assert authorized.release is not None and public.release is not None
    for key, curve in authorized.release.curves.items():
        assert public.release.curves[key].cell_gap == curve.cell_gap
    assert public.release.curves[INCIDENT].gap_counts()["propagation"] == 1
    data = json.loads(projection.read_text(encoding="utf-8"))
    fits = copy.deepcopy(data)
    fits["objects"]["gate"]["g0_fits"][0]["gap"] = "propagation"
    cells = copy.deepcopy(data)
    cells["objects"]["release"]["curves"][INCIDENT]["cell_gap"][2] = "nuisance"
    for tampered, message in (
        (fits, "Unknown fit category"),
        (cells, "Unknown public cell category"),
    ):
        _rehash(tampered)
        with pytest.raises(SchemaError, match=message):
            _parse_public(tampered)
