"""Public rendering equals authorized rendering on frozen-emitter fixtures."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import pytest

from ic_study.analysis.detection_boundary_v4 import Uncertainty, band
from ic_study.analysis.detection_v4_report import (
    Inputs,
    Loaded,
    load_inputs,
    main,
    render,
)
from ic_study.analysis.v4_public_aggregates import (
    _parse_public,
    canonical,
    digest,
    load_public,
    project,
    read_json,
)
from ic_study.analysis.v4_report_export import (
    PLACEHOLDERS,
    export,
    fill,
    result_values,
    used_ids,
    values_record,
)
from ic_study.analysis.v4_report_export import (
    main as export_main,
)
from ic_study.analysis.v4_report_synthetic import (
    NETWORKS,
    GatePlan,
    UnitPlan,
    build_gate,
    build_release,
    crosswalk_fixture,
    logistic_profile,
    shp_fixture,
    stage_successor,
    unit_keys,
    write_release,
)
from ic_study.simulation.v4_plan import gate_tasks

STUDY = Path(__file__).resolve().parents[2]
CRITERIA = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
# Recorded from the authorized exporter before this change, including all IDs.
# "full" was renewed for amendment v4.4: only the T4 gaps_propagation cells were added.
PRE_CHANGE_CATALOGS = {
    "gate-only": "265e6f0ca927c985d3e3ff6c7be081cca12f0f2ef7ad4348509fc3274f300842",
    # Renewed in T57f: only the r lists changed
    # (publications/jcss-manuscript/pipeline/review/t57f-r-list-digest-proof.json).
    "full": "d4b65e73e59899beaaec0595fe16160303066f5bb444e8c604480a6ad79caff8",
    "failed": "cd6edd311bfd7e0003bb202890e04a85859966e6a50f910fb38675fca77439c4",
}


@pytest.fixture(scope="module")
def verifier() -> ModuleType:
    path = STUDY / "publications/reproducibility/verify_short_path.py"
    spec = importlib.util.spec_from_file_location("short_path_verifier", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture(root: Path, case: str) -> Inputs:
    root.mkdir(parents=True)
    if case == "gate-only":
        gate = build_gate(root / "gate", GatePlan(stages=("G0",)))
        return Inputs(None, gate, criteria=CRITERIA)
    if case == "failed":
        failed = frozenset({gate_tasks("G1c")[0].key})
        gate = build_gate(root / "gate", GatePlan(stages=("G1c",), failed_tasks=failed))
        return Inputs(None, gate, criteria=CRITERIA)
    allocation = root / "allocation.json"
    gate = build_gate(root / "gate", allocation=allocation)
    successor = root / "G1c-successor.json"
    successor.write_text(json.dumps(stage_successor(gate)) + "\n", encoding="utf-8")
    curves = root / "curves.json"
    plans = {
        key: UnitPlan(logistic_profile(0.02) if family == "B" else (0.5,) * 9)
        for family, tier in (("B", 1), ("A", 2), ("C", 2), ("D", 2), ("E", 2))
        for key in unit_keys(tier=tier, family=family).values()
    }
    write_release(curves, build_release(root / "curve-source", plans, draws=40))
    shp = root / "shp.json"
    shp.write_text(json.dumps(shp_fixture()) + "\n", encoding="utf-8")
    bridge = root / "crosswalk.json"
    bridge.write_text(json.dumps(crosswalk_fixture()) + "\n", encoding="utf-8")
    return Inputs(
        curves,
        gate,
        shp=shp,
        criteria=CRITERIA,
        crosswalk=bridge,
        successors=(successor,),
        allocation=allocation,
    )


@pytest.fixture(scope="module", params=tuple(PRE_CHANGE_CATALOGS))
def rehearsal(
    request: pytest.FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
    verifier: ModuleType,
) -> dict[str, Any]:
    case = str(request.param)
    root = tmp_path_factory.mktemp(f"public-v4-{case}")
    inputs = _fixture(root / "source", case)
    loaded = load_inputs(inputs, synthetic=True)
    projection = root / "public-aggregates.json"
    project(inputs, projection, synthetic=True)
    authorized = root / "authorized"
    authorized.mkdir()
    render(inputs, authorized / "report", synthetic=True, dpi=40)
    paper = authorized / "paper"
    paper.mkdir()
    lines = [rf"\input{{generated/{name}}}" for name in PLACEHOLDERS]
    lines += [rf"\resultnum{{{key}}}{{[..]}}" for key in sorted(result_values(loaded))]
    (paper / "main.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = export(inputs, authorized / "report", paper)
    fill(paper, result.catalog)
    for filename, ids in (
        ("values.json", used_ids(paper)),
        ("catalog.json", result.catalog),
    ):
        (authorized / filename).write_text(
            json.dumps(
                values_record(result, ids), indent=2, sort_keys=True, ensure_ascii=False
            )
            + "\n",
            encoding="utf-8",
        )
    expected = {
        "schema": verifier.SCHEMA,
        "projection": {
            "file": projection.name,
            "sha256": hashlib.sha256(projection.read_bytes()).hexdigest(),
        },
        "dpi": 40,
        "files": verifier.hashes(authorized),
    }
    manifest = root / "expected-hashes.json"
    manifest.write_text(json.dumps(expected) + "\n", encoding="utf-8")
    # Hide every authorized input; the public path must work independently.
    (root / "source").rename(root / "source-unavailable")
    return {
        "case": case,
        "root": root,
        "projection": projection,
        "manifest": manifest,
        "loaded": loaded,
        "catalog": result.catalog,
        "authorized": authorized,
    }


def test_short_path_equals_authorized_rendering(
    rehearsal: dict[str, Any], verifier: ModuleType, catalog_presentation_proof: Any
) -> None:
    public_out = rehearsal["root"] / "public-rendered"
    assert verifier.verify(rehearsal["root"], rehearsal["manifest"], public_out) == 0
    authorized = rehearsal["authorized"]
    for path in authorized.rglob("*"):
        if path.is_file():
            name = path.relative_to(authorized).as_posix()
            other = public_out / name
            if verifier.normalization(name) == "none":
                assert path.read_bytes() == other.read_bytes(), name
    catalog = rehearsal["catalog"]
    catalog_presentation_proof(
        catalog, PRE_CHANGE_CATALOGS[rehearsal["case"]], rehearsal["loaded"].gate
    )
    if rehearsal["case"] == "full":
        assert (public_out / "report/F6_a_star_shp_anchor_synthetic.pdf").is_file()
        public = load_public(rehearsal["projection"])
        assert public.loaded.shp is not None and public.loaded.crosswalk is not None
    else:
        emitted = {p.stem for p in (public_out / "report").glob("*.csv")}
        assert emitted == {"T3_gate_summary_synthetic"}
    if rehearsal["case"] == "failed":
        assert catalog["v4.gate.G1c.verdict.approved"] == "0"


def _rehash(data: dict[str, Any]) -> None:
    data["objects_sha256"] = {k: digest(v) for k, v in data["objects"].items()}
    data["sha256"] = digest({k: v for k, v in data.items() if k != "sha256"})


@pytest.mark.parametrize(
    "location", ["root", "object", "gate", "summary", "code", "sources", "fit"]
)
def test_unknown_fields_fail_even_with_recomputed_hashes(
    rehearsal: dict[str, Any], tmp_path: Path, location: str
) -> None:
    data = read_json(rehearsal["projection"])
    gate = data["objects"]["gate"]
    if location == "root":
        data["extra"] = 1
    elif location == "object":
        data["objects"]["extra"] = 1
    elif location == "gate":
        gate["binding_sha256"] = "f" * 64
    elif location == "summary":
        next(iter(gate["summaries"].values()))["matching_mask"] = []
    elif location == "code":
        data["code"]["host"] = "private"
    elif location == "sources":
        data["source_hashes"]["/absolute/file"] = ["f" * 64]
    else:
        gate["g0_fits"] = [{"status": "interior", "gap": None, "count": 1, "seed": 7}]
    _rehash(data)
    path = tmp_path / "tampered.json"
    path.write_bytes(canonical(data))
    with pytest.raises(ValueError):
        load_public(path)


@pytest.mark.parametrize(
    "tamper",
    [
        "self-hash",
        "object-hash",
        "duplicate-root",
        "duplicate-nested",
        "nonfinite",
        "invalid-type",
        "bad-source-hash",
    ],
)
def test_corruption_and_invalid_json_are_refused(
    rehearsal: dict[str, Any], tmp_path: Path, tamper: str
) -> None:
    data = read_json(rehearsal["projection"])
    if tamper == "self-hash":
        data["sha256"] = "f" * 64
    elif tamper == "object-hash":
        data["objects_sha256"]["gate"] = "f" * 64
        data["sha256"] = digest({k: v for k, v in data.items() if k != "sha256"})
    elif tamper == "invalid-type":
        data["synthetic"] = "true"
        _rehash(data)
    elif tamper == "bad-source-hash":
        data["source_hashes"]["criteria"] = ["not-a-hash"]
        _rehash(data)
    raw = canonical(data)
    if tamper == "duplicate-root":
        raw = raw[:-1] + b',"synthetic":true}'
    elif tamper == "duplicate-nested":
        raw = raw.replace(
            b'"schema":', b'"code":{"commit":null,"commit":null},"schema":', 1
        )
    elif tamper == "nonfinite":
        raw = raw.replace(b'"synthetic":true', b'"synthetic":NaN')
    path = tmp_path / "tampered.json"
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        load_public(path)


def test_projection_contains_no_private_bindings_or_raw_records(
    rehearsal: dict[str, Any],
) -> None:
    raw = rehearsal["projection"].read_text()
    for forbidden in (
        "/Users/",
        "/private/",
        "seed",
        "task_records",
        "matching_mask",
        "sealed_root_identifier",
        "binding_sha256",
        "nuisance-aucs",
        "authorization-",
    ):
        assert forbidden not in raw
    public = load_public(rehearsal["projection"])
    assert public.synthetic
    assert result_values(public.loaded) == result_values(rehearsal["loaded"])
    assert public.loaded.allocation is None
    assert public.loaded.gate is not None
    assert public.loaded.gate.task_digests == ()


@pytest.mark.parametrize(
    "option",
    [
        "--curves",
        "--gate-root",
        "--criteria",
        "--allocation",
        "--shp",
        "--crosswalk",
        "--release-record",
        "--stage-successor",
    ],
)
def test_public_cli_excludes_each_authorized_input(tmp_path: Path, option: str) -> None:
    public = ["--public-aggregates", "public.json", option, "authorized"]
    with pytest.raises(SystemExit) as error:
        main([*public, "--out", str(tmp_path / "report")])
    assert error.value.code == 2
    with pytest.raises(SystemExit):
        export_main(
            [
                *public,
                "--report",
                "report",
                "--manuscript",
                "paper",
                "--values",
                "values.json",
            ]
        )


def test_direct_public_input_also_excludes_authorized_sources(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="exclude"):
        load_inputs(Inputs(None, tmp_path, public_aggregates=tmp_path / "public.json"))


def test_existing_projection_is_never_overwritten(tmp_path: Path) -> None:
    inputs = _fixture(tmp_path / "source", "failed")
    path = tmp_path / "public.json"
    project(inputs, path, synthetic=True)
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        project(inputs, path, synthetic=True)
    assert path.read_bytes() == before
    with pytest.raises(ValueError, match="authorized"):
        project(replace(inputs, public_aggregates=path), tmp_path / "other.json")


def test_verifier_refuses_mismatch_existing_output_and_unsafe_paths(
    rehearsal: dict[str, Any], verifier: ModuleType, tmp_path: Path
) -> None:
    data = read_json(rehearsal["manifest"])
    data["projection"]["sha256"] = "f" * 64
    manifest = tmp_path / "manifest.json"
    manifest.write_bytes(canonical(data))
    assert verifier.verify(rehearsal["root"], manifest, tmp_path / "bad-hash") == 1
    data = read_json(rehearsal["manifest"])
    data["files"]["../escape"] = {"sha256": "f" * 64, "normalization": "none"}
    manifest.write_bytes(canonical(data))
    assert verifier.verify(rehearsal["root"], manifest, tmp_path / "unsafe") == 1
    assert not (tmp_path / "unsafe").exists()
    assert verifier.verify(rehearsal["root"], rehearsal["manifest"], tmp_path) == 1


def test_verifier_detects_a_changed_scientific_value(
    tmp_path: Path, verifier: ModuleType
) -> None:
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    record = {
        "code": {},
        "report_manifest_sha256": "a" * 64,
        "values": {"v4.example": "1"},
    }
    first.write_bytes(canonical(record))
    record["values"] = {"v4.example": "2"}
    second.write_bytes(canonical(record))
    assert verifier.comparison_bytes(
        first, "values-provenance-v1"
    ) != verifier.comparison_bytes(second, "values-provenance-v1")


@pytest.mark.parametrize(
    "defect",
    [
        "shp-estimate",
        "shp-wald",
        "shp-starts",
        "bridge-duplicate",
        "bridge-count",
        "overflow",
        "raw-diagnostic",
        "critical-floor",
        "null-gate",
        "secondary",
        "band",
    ],
)
def test_invalid_public_objects_fail_after_rehash(
    rehearsal: dict[str, Any], defect: str
) -> None:
    if rehearsal["case"] != "full":
        return
    data = read_json(rehearsal["projection"])
    if defect == "shp-estimate":
        data["objects"]["shp"]["estimate"] = 2
    elif defect == "shp-wald":
        data["objects"]["shp"]["wald_95_interval"] = [0, 0.01]
    elif defect == "shp-starts":
        data["objects"]["shp"]["starts"] = {
            "year": None,
            "estimate": None,
            "standard_error": None,
            "wald_95_interval": None,
            "failure_reasons": ["unknown"],
        }
    elif defect == "bridge-duplicate":
        data["objects"]["crosswalk"]["ranges"].append(
            data["objects"]["crosswalk"]["ranges"][0]
        )
    elif defect == "bridge-count":
        data["objects"]["crosswalk"]["ranges"][0]["failures"] = -1
    elif defect == "overflow":
        data["objects"]["thresholds"]["cell_lower"] = 10**400
    elif defect == "critical-floor":
        next(iter(data["objects"]["release"]["curves"].values()))["critical"] = 0
    elif defect == "null-gate":
        next(iter(data["objects"]["release"]["curves"].values()))["valid_null_gate"] = (
            False
        )
    elif defect == "secondary":
        next(iter(data["objects"]["release"]["curves"].values()))["secondary"][0][
            "point"
        ] = 0.9
    elif defect == "band":
        curve = next(iter(data["objects"]["release"]["curves"].values()))
        curve["auc"][0] = curve["upper"][0] + 0.01
    else:
        next(iter(data["objects"]["release"]["curves"].values()))[
            "cell_final_status"
        ] = [None] * 9
    _rehash(data)
    with pytest.raises(ValueError):
        _parse_public(data)


def test_public_band_may_lie_below_a_point_near_one(rehearsal: dict[str, Any]) -> None:
    if rehearsal["case"] != "full":
        return
    data = read_json(rehearsal["projection"])
    key = unit_keys(tier=1, family="B")[0.5]
    curve = data["objects"]["release"]["curves"][key]
    point = 1 - 1 / (2 * NETWORKS) ** 2
    interval = band(
        Uncertainty(np.array([point]), np.zeros(1), np.zeros(1), np.full((2, 1), point))
    )
    curve["auc"][-1] = point
    curve["lower"][-1] = float(interval.lower[0])
    curve["upper"][-1] = float(interval.upper[0])
    _rehash(data)
    parsed = _parse_public(data).loaded.release
    assert parsed is not None
    assert parsed.curves[key].upper[-1] < parsed.curves[key].auc[-1]


def test_only_published_low_diagnostics_are_projected(tmp_path: Path) -> None:
    curves = tmp_path / "curves.json"
    b = unit_keys(tier=1, family="B")[0.75]
    other = unit_keys(tier=2, family="D")[0.75]
    write_release(
        curves,
        build_release(
            tmp_path / "curve-source",
            {b: UnitPlan(logistic_profile(0.002)), other: UnitPlan((0.5,) * 9)},
            draws=40,
        ),
    )
    inputs = Inputs(curves, None)
    loaded = load_inputs(inputs, synthetic=True)
    projection = tmp_path / "public.json"
    project(inputs, projection, synthetic=True)
    objects = read_json(projection)["objects"]["release"]["curves"]
    assert all(v is None for v in objects[other]["diagnostics"])
    assert [i for i, v in enumerate(objects[b]["diagnostics"]) if v is not None] == [
        1,
        2,
    ]
    assert "retry" in objects[b]["diagnostics"][1]
    assert "matching_pairs" not in objects[b]["diagnostics"][1]
    public = load_public(projection)
    assert result_values(public.loaded) == result_values(loaded)
    authorized = export_generated(loaded)
    assert export_generated(public.loaded) == authorized


def export_generated(loaded: Loaded) -> tuple[dict[str, list[str]], dict[str, str]]:
    from ic_study.analysis.v4_report_export import generated_files

    return generated_files(loaded, lambda stem: stem + ".pdf", True)
