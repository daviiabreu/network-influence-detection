"""Gate-failure manuscript exports using only artificial v4 and SHP records."""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from ic_study.analysis.detection_v4_report import Inputs, load_inputs, render
from ic_study.analysis.detection_v4_report import main as report_main
from ic_study.analysis.v4_report_export import export, generated_files, result_values
from ic_study.analysis.v4_report_export import main as export_main
from ic_study.analysis.v4_report_schema import FAIL, load_shp
from ic_study.analysis.v4_report_synthetic import (
    GatePlan,
    UnitPlan,
    build_gate,
    build_release,
    logistic_profile,
    shp_successor_fixture,
    unit_keys,
    write_release,
)

STUDY = Path(__file__).resolve().parents[2]
MANUSCRIPT = STUDY / "publications/jcss-manuscript"
CRITERIA = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
SHP_IDS = {
    "v4.shp." + name for name in ("estimate", "wald_lo", "wald_hi", "env_lo", "env_hi")
}


def synthetic_inputs(root: Path) -> dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    gate = build_gate(
        root / "gate",
        GatePlan(stages=("G2", "G2c"), failed_tasks=frozenset({"G2c-00000"})),
    )
    shp = root / "shp.json"
    shp.write_text(json.dumps(shp_successor_fixture()) + "\n", encoding="utf-8")
    curves = root / "released_curves.json"
    key = unit_keys(tier=1, family="B")[0.5]
    write_release(
        curves,
        build_release(
            root / "confirmatory", {key: UnitPlan(logistic_profile(0.02))}, draws=40
        ),
    )
    return {"gate": gate, "shp": shp, "curves": curves}


@pytest.fixture(scope="module")
def case(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    return synthetic_inputs(tmp_path_factory.mktemp("gate-only-shp"))


def gate_inputs(case: dict[str, Path], *, shp: bool = True) -> Inputs:
    return Inputs(None, case["gate"], case["shp"] if shp else None, CRITERIA)


def b1_shp_manuscript(root: Path) -> Path:
    source = (MANUSCRIPT / "pipeline/drafts/2026-09-28/results-shells.tex").read_text(
        "utf-8"
    )
    block = source.split("% BEGIN BLOCK B1-SHP", 1)[1].split("% END BLOCK B1-SHP", 1)[0]
    sentences = block.split("% (a)\n", 1)[1].split("% (b)\n", 1)[0]
    (root / "sections").mkdir(parents=True)
    (root / "sections/results.tex").write_text(sentences, "utf-8")
    (root / "main.tex").write_text(
        "\\input{sections/results}\n\\input{generated/gate-outcomes}\n", "utf-8"
    )
    return root


def test_gate_only_shp_exports_five_ids_with_aggregate_provenance(
    case: dict[str, Path], tmp_path: Path
) -> None:
    inputs = gate_inputs(case)
    loaded = load_inputs(inputs, synthetic=True)
    assert loaded.release is None and loaded.gate is not None
    assert loaded.gate.verdict("G2c") == FAIL
    report = tmp_path / "report"
    manifest = json.loads(
        render(inputs, report, dpi=40, synthetic=True, formats=("pdf",)).read_bytes()
    )
    assert manifest["inputs"]["shp"] == {
        "name": case["shp"].name,
        "sha256": hashlib.sha256(case["shp"].read_bytes()).hexdigest(),
    }
    assert set(manifest["outputs"]) == {
        "F4_gate_diagnostics_synthetic.pdf",
        "T3_gate_summary_synthetic.csv",
        "T3_gate_summary_synthetic.tex",
    }
    result = export(inputs, report, b1_shp_manuscript(tmp_path / "manuscript"))
    assert {key for key in result.catalog if key.startswith("v4.shp.")} == SHP_IDS
    assert {key: result.catalog[key] for key in SHP_IDS} == {
        "v4.shp.estimate": "0.646",
        "v4.shp.wald_lo": "0.625",
        "v4.shp.wald_hi": "0.668",
        "v4.shp.env_lo": "0.619",
        "v4.shp.env_hi": "0.718",
    }
    assert not any(
        key.startswith(("v4.t1.", "v4.bd.", "v4.inv.")) for key in result.catalog
    )
    assert (
        result.manifest_sha256
        == hashlib.sha256((report / "manifest.json").read_bytes()).hexdigest()
    )
    assert b"F6" not in (tmp_path / "manuscript/generated/shp-anchor.tex").read_bytes()


def test_gate_only_catalog_includes_the_shp_anchor(case: dict[str, Path]) -> None:
    loaded = dataclasses.replace(
        load_inputs(gate_inputs(case, shp=False), synthetic=True),
        shp=load_shp(case["shp"]),
    )
    assert {
        key for key in result_values(loaded) if key.startswith("v4.shp.")
    } == SHP_IDS


def test_gate_only_cli_fills_b1_shp_for_submission(
    case: dict[str, Path], tmp_path: Path
) -> None:
    report = tmp_path / "report"
    arguments = [
        "--gate-root",
        str(case["gate"]),
        "--shp",
        str(case["shp"]),
        "--criteria",
        str(CRITERIA),
    ]
    assert (
        report_main([*arguments, "--out", str(report), "--dpi", "40", "--synthetic"])
        == 0
    )
    manuscript = b1_shp_manuscript(tmp_path / "manuscript")
    values = tmp_path / "values.json"
    assert (
        export_main(
            [
                *arguments,
                "--report",
                str(report),
                "--manuscript",
                str(manuscript),
                "--values",
                str(values),
                "--fill",
            ]
        )
        == 0
    )
    bound = json.loads(values.read_bytes())["values"]
    assert bound.keys() >= SHP_IDS
    spec = importlib.util.spec_from_file_location(
        "paper_check", MANUSCRIPT / "pipeline/paper_check.py"
    )
    assert spec is not None and spec.loader is not None
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    assert (
        checker.result_consistency(
            manuscript, checker.tex_sources(manuscript), values, True
        )
        == []
    )


def test_gate_only_without_shp_keeps_its_outputs_and_catalog(
    case: dict[str, Path], tmp_path: Path
) -> None:
    without = gate_inputs(case, shp=False)
    with_shp = gate_inputs(case)
    reports = {name: tmp_path / name for name in ("without", "with")}
    for name, inputs in (("without", without), ("with", with_shp)):
        render(inputs, reports[name], dpi=40, synthetic=True, formats=("pdf",))
    before = {
        p.name: p.read_bytes()
        for p in reports["without"].iterdir()
        if p.name != "manifest.json"
    }
    after = {
        p.name: p.read_bytes()
        for p in reports["with"].iterdir()
        if p.name != "manifest.json"
    }
    assert before == after
    catalogs = [
        result_values(load_inputs(inputs, synthetic=True))
        for inputs in (without, with_shp)
    ]
    assert catalogs[0] == {
        key: value for key, value in catalogs[1].items() if key not in SHP_IDS
    }
    assert not any(key.startswith("v4.shp.") for key in catalogs[0])


def test_released_shp_keeps_all_its_existing_ids(case: dict[str, Path]) -> None:
    loaded = load_inputs(
        dataclasses.replace(gate_inputs(case), curves=case["curves"]), synthetic=True
    )
    values = result_values(loaded)
    assert {key for key in values if key.startswith("v4.shp.")} == SHP_IDS | {
        "v4.shp.year",
        "v4.shp.standard_error",
        "v4.shp.n_r_in_interval",
        "v4.shp.n_status_classes",
        "v4.shp.starts.estimate",
        "v4.shp.starts.wald_lo",
        "v4.shp.starts.wald_hi",
    }


@pytest.mark.parametrize(
    ("release", "expected"),
    [
        (
            False,
            (
                "2c5a81d90a729edc8a2a16293f17cf5c54492ce8b59b7f56b5b83093457d6be5",
                "80a90e347b69fc764f69b7671ebe69784265fa5f1b96b37e761fe67b0468530e",
                "b8e38c50fcbf2aa49fd0138adf3627cd1304a9d92825f85f2273f64526853c56",
            ),
        ),
        (
            True,
            (
                "dfa9e0f3adad3c1fd304a05f86b7ee5c1fd801bf93e0015c5614a96ab68cfa07",
                "4495ec63e8e6b1e04f30008299c0786859031bfac64785344f79cd6075aa95d1",
                "59de678b193aabe480e03be054028ff828979b8ea867036b867f9af9cbb3f1a3",
            ),
        ),
    ],
)
def test_exports_match_the_prechange_synthetic_bytes(
    case: dict[str, Path], release: bool, expected: tuple[str, str, str]
) -> None:
    inputs = gate_inputs(case, shp=release)
    if release:
        inputs = dataclasses.replace(inputs, curves=case["curves"])
    loaded = load_inputs(inputs, synthetic=True)
    files, cells = generated_files(
        loaded, lambda stem: f"generated/{stem}_synthetic.pdf", True
    )
    # Captured from 00c8dc3d before changing either reporting module. The release
    # files digest was renewed when the F1, F2, T1 and F6 captions were revised;
    # those caption lines are the only difference in the generated files. The
    # release files and cells digests were renewed for amendment v4.4: the T4
    # gaps_propagation column and its caption entry are the only difference.
    # T57 renewed the release files digest when the F1 caption renamed null B
    # trait-plus-autoregressive persistence; pipeline/review/
    # t57-caption-digest-proof.json shows that this name is the only difference.
    # T57b renewed it again for the SHP licence's source line in the F6 caption;
    # pipeline/review/t57b-caption-digest-proof.json shows that this sentence is
    # the only difference. T57e renewed it for the F1 caption's E label,
    # mover--stayer persistence; pipeline/review/t57e-caption-digest-proof.json
    # shows that this label is the only difference. T58 renewed it for the T1
    # caption's censored (gap) and NA definitions and for F3 becoming a comment
    # without the MECHANISMS permission; pipeline/review/
    # t58-caption-digest-proof.json shows that these are the only differences.
    values = result_values(loaded)
    verdict_ids = {
        f"v4.gate.{stage}.verdict.{name}"
        for stage in ("G0", "G1b", "G1c", "G2", "G2c")
        for name in ("complete", "approved", "stop")
    }
    assert verdict_ids <= values.keys()
    legacy_values = {k: v for k, v in values.items() if k not in verdict_ids}
    actual = tuple(
        hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        for record in (legacy_values, files, cells)
    )
    assert actual == expected


@pytest.mark.parametrize("release", [False, True])
def test_only_the_shp_figure_caption_credits_the_swiss_household_panel(
    case: dict[str, Path], release: bool
) -> None:
    inputs = gate_inputs(case, shp=True)
    if release:
        inputs = dataclasses.replace(inputs, curves=case["curves"])
    files, _ = generated_files(
        load_inputs(inputs, synthetic=True), lambda stem: f"generated/{stem}.pdf", True
    )
    credited = sorted(
        name
        for name, lines in files.items()
        if any("Source: Swiss Household Panel (SHP)." in line for line in lines)
    )
    assert credited == (["shp-anchor"] if release else [])


@pytest.mark.parametrize("shp", [False, True])
@pytest.mark.parametrize("interface", ["loader", "report", "export"])
def test_crosswalk_without_curves_is_refused(
    case: dict[str, Path],
    tmp_path: Path,
    shp: bool,
    interface: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    crosswalk = tmp_path / "unread-crosswalk.json"
    inputs = dataclasses.replace(gate_inputs(case, shp=shp), crosswalk=crosswalk)
    if interface == "loader":
        with pytest.raises(ValueError, match="crosswalk"):
            load_inputs(inputs, synthetic=True)
    else:
        arguments = ["--gate-root", str(case["gate"]), "--crosswalk", str(crosswalk)]
        if shp:
            arguments += ["--shp", str(case["shp"])]
        cli = report_main if interface == "report" else export_main
        outputs = (
            ["--out", str(tmp_path / "out")]
            if interface == "report"
            else [
                "--report",
                str(tmp_path / "report"),
                "--manuscript",
                str(tmp_path / "manuscript"),
                "--values",
                str(tmp_path / "values.json"),
            ]
        )
        with pytest.raises(SystemExit) as failure:
            cli([*arguments, *outputs])
        assert failure.value.code == 2
        requirement = "--curves" if shp else "--shp"
        assert f"error: --crosswalk needs {requirement}" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()
    assert not (tmp_path / "values.json").exists()
