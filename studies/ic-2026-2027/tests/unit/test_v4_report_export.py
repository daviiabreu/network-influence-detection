"""Release-day export of the v4 report into the JCSS manuscript, synthetic inputs."""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path
from types import ModuleType
from typing import Any, cast
from unittest import mock

import pytest

from ic_study.analysis import v4_report_figures, v4_report_tables
from ic_study.analysis.detection_v4_report import Inputs, Loaded, load_inputs, render
from ic_study.analysis.v4_report_export import (
    CAPTION_F1,
    NUMBER,
    PLACEHOLDERS,
    RESULT,
    Binder,
    LowCell,
    export,
    fill,
    generated_files,
    grid_runs,
    main,
    result_values,
    used_ids,
)
from ic_study.analysis.v4_report_protocol import _verified, protocol_values
from ic_study.analysis.v4_report_schema import (
    INVALID,
    NOT_STARTED,
    TARGET,
    VALID,
    Boundary,
    CellDiagnostics,
    Release,
    parse_release,
    unit_catalog,
)
from ic_study.analysis.v4_report_synthetic import (
    G0_FAILURES,
    GatePlan,
    UnitPlan,
    build_gate,
    build_release,
    logistic_profile,
    stage_successor,
    stop_before_g2,
    unit_keys,
    write_release,
)
from ic_study.analysis.v4_report_tables import table_t1

STUDY = Path(__file__).resolve().parents[2]
CRITERIA = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
MANUSCRIPT = STUDY / "publications/jcss-manuscript"
SHELLS = MANUSCRIPT / "pipeline/drafts/2026-09-28/results-shells.tex"
B = unit_keys(tier=1, family="B")
D = unit_keys(tier=2, family="D")
FLAT = (0.5,) * 9
PLATEAU = (0.5, 0.52, 0.55, 0.58, 0.62, 0.66, 0.69, 0.705, 0.705)
RISING = logistic_profile(0.02)


def synthetic_loaded(tmp_path: Path, plans: dict[str, UnitPlan]) -> Loaded:
    with mock.patch("os.fsync", lambda _fd: None):
        release = parse_release(build_release(tmp_path / "curves", plans, draws=40))
    return Loaded(release, None, None, None, None, None)


def main_plans() -> dict[str, UnitPlan]:
    return {
        key: UnitPlan(RISING if family == "B" else FLAT)
        for family, tier in (("B", 1), ("A", 2), ("C", 2), ("D", 2), ("E", 2))
        for key in unit_keys(tier=tier, family=family).values()
    }


@pytest.mark.parametrize(
    "released,expected",
    [
        # Renewed for amendment v4.4: only the T4 gaps_propagation cells were added.
        # Renewed in T57f: only the r lists changed
        # (pipeline/review/t57f-r-list-digest-proof.json).
        (True, "88cccbca8b5277a0773f152ccc23aa9c809d8cebcffc8449c24e9461c33721eb"),
        (False, "31f322512701c66129b544bdbc1e84384eadcad275f4a9db089360b67bb44aeb"),
    ],
)
def test_layout_preserves_pre_change_synthetic_catalogs(
    tmp_path: Path, released: bool, expected: str, catalog_presentation_proof: Any
) -> None:
    if released:
        loaded = synthetic_loaded(tmp_path, main_plans())
    else:
        inputs = Inputs(
            None,
            build_gate(tmp_path / "gate", GatePlan(stages=("G0",))),
            criteria=CRITERIA,
        )
        loaded = load_inputs(inputs, synthetic=True)
    _, cells = generated_files(loaded, lambda stem: stem + ".pdf", True)
    catalog = result_values(loaded) | cells
    additions = {k: v for k, v in catalog.items() if ".verdict." in k}
    assert len(additions) == (0 if released else 15)
    catalog = {k: v for k, v in catalog.items() if k not in additions}
    catalog_presentation_proof(catalog, expected, loaded.gate)


def test_real_manuscript_keeps_the_x1_x2_destination_in_every_results_branch() -> None:
    source = (MANUSCRIPT / "main.tex").read_text()
    inputs = source.splitlines()
    assert r"\input{sections/supplement-exploratory-x1-x2}" in inputs
    supplement = (MANUSCRIPT / "sections/supplement-exploratory-x1-x2.tex").read_text()
    assert r"\label{supp:x1-x2}" in supplement
    assert source.index(r"\fi", source.index(r"\ifsupplementcontent")) < source.index(
        r"\input{sections/supplement-exploratory-x1-x2}"
    )


@pytest.mark.parametrize(
    "name", ["exploratory-x1b-boundaries", "exploratory-x7-boundaries"]
)
def test_full_exploratory_boundaries_use_the_supplement_content_guard(
    name: str,
) -> None:
    source = (MANUSCRIPT / "main.tex").read_text()
    check = rf"\checksupplementcontent{{generated/{name}}}"
    include = rf"\input{{generated/{name}}}"
    title_guard = source.index("\n\\ifsupplementcontent\n")
    assert source.index(check) < title_guard
    assert source.index(include) > source.index(r"\fi", title_guard)
    stub = MANUSCRIPT / "generated" / (name + ".tex")
    assert stub.is_file()
    assert "v4_exploratory_export" in stub.read_text()
    assert not RESULT.findall(stub.read_text())


@pytest.mark.parametrize("defect", ["none", "missing", "partial", "invalid", "main"])
def test_cross_mechanism_permission_requires_all_tier2_and_valid_main(
    tmp_path: Path, defect: str
) -> None:
    plans = main_plans()
    key = unit_keys(tier=2, family="A")[0.9]
    if defect == "missing":
        del plans[key]
    elif defect == "partial":
        plans[key] = UnitPlan(FLAT, partial_cells=3)
    elif defect == "invalid":
        plans[key] = UnitPlan((0.8,) * 9)
    elif defect == "main":
        plans[B[0.9]] = UnitPlan((0.8,) * 9)
    loaded = synthetic_loaded(tmp_path, plans)
    values = result_values(loaded)
    assert values["v4.mechanisms.allowed"] == str(int(defect == "none"))
    assert values["v4.bd.n_eligible"] == ("9" if defect == "none" else "0")
    assert values["v4.bd.n_persistence"] == ("9" if defect == "none" else "0")
    files, _ = generated_files(loaded, lambda stem: stem + ".pdf", True)
    offsets = "\n".join(files["supplement-family-offsets"])
    if defect == "none":
        assert r"\label{fig:v4-F3}" in offsets
    else:
        assert all(line.startswith("%") for line in offsets.splitlines())
        assert r"\includegraphics" not in offsets


def test_gate_status_rows_account_for_dependency_gaps(tmp_path: Path) -> None:
    gate = build_gate(
        tmp_path / "gate",
        GatePlan(
            stages=("G0",), g0_failures={k: (s, 1) for k, (s, _) in G0_FAILURES.items()}
        ),
    )
    loaded = load_inputs(Inputs(None, gate, criteria=CRITERIA), synthetic=True)
    assert loaded.gate is not None
    files, catalog = generated_files(loaded, lambda stem: stem + ".pdf", True)
    statuses = {
        key: value
        for key, value in catalog.items()
        if key.startswith("v4.tab.T3.G0.status-") and key.endswith(".value")
    }
    assert sum(int(value) for value in statuses.values()) == len(loaded.gate.g0_fits)
    dependency = sum(fit.gap == "dependency" for fit in loaded.gate.g0_fits)
    assert dependency > 0
    assert catalog["v4.tab.T3.G0.status-dependency-gap.value"] == str(dependency)
    assert "status dependency gap" in "\n".join(files["gate-outcomes"])


# One r per reading of B against D on grids complete and valid for both; at
# r = 0.70 a gap in B makes the pair ineligible, and at r = 0.75 a* is 0.003.
PLANS = {
    B[0.5]: UnitPlan(RISING),
    D[0.5]: UnitPlan(FLAT),
    B[0.55]: UnitPlan(RISING),
    D[0.55]: UnitPlan(RISING),
    B[0.6]: UnitPlan(RISING),
    D[0.6]: UnitPlan(PLATEAU),
    B[0.65]: UnitPlan(FLAT),
    D[0.65]: UnitPlan(RISING),
    B[0.7]: UnitPlan(logistic_profile(0.1), gaps=frozenset({2})),
    D[0.7]: UnitPlan(RISING),
    B[0.75]: UnitPlan(logistic_profile(0.002)),
}


def _paper_check() -> ModuleType:
    path = MANUSCRIPT / "pipeline/paper_check.py"
    spec = importlib.util.spec_from_file_location("paper_check", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def env(
    tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest
) -> dict[str, Any]:
    root = tmp_path_factory.mktemp("v4export")
    curves = root / "released_curves.json"
    write_release(curves, build_release(root / "confirmatory", PLANS, draws=40))
    gate = build_gate(root / "gate", GatePlan(stages=("G0", "G1c")))
    successor = root / "G1c-aggregate-successor.json"
    successor.write_text(
        json.dumps(stage_successor(gate), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    from ic_study.analysis import v4_report_schema

    patch = pytest.MonkeyPatch()
    patch.setattr(
        v4_report_schema,
        "APPROVED_G1C_SHA256",
        hashlib.sha256(successor.read_bytes()).hexdigest(),
        raising=False,
    )
    request.addfinalizer(patch.undo)

    inputs = Inputs(curves, gate, criteria=CRITERIA, successors=(successor,))
    report = root / "report"
    render(inputs, report, dpi=40, formats=("pdf",))
    arguments = [
        "--curves",
        str(curves),
        "--gate-root",
        str(gate),
        "--criteria",
        str(CRITERIA),
        "--stage-successor",
        str(successor),
    ]
    return {"inputs": inputs, "report": report, "arguments": arguments}


@pytest.fixture(scope="module")
def loaded(env: dict[str, Any]) -> Loaded:
    return load_inputs(env["inputs"])


@pytest.fixture(scope="module")
def predicate_loaded(tmp_path_factory: pytest.TempPathFactory) -> Loaded:
    return synthetic_loaded(
        tmp_path_factory.mktemp("predicates"),
        {
            B[0.5]: UnitPlan(RISING),
            D[0.5]: UnitPlan(FLAT),
            B[0.7]: PLANS[B[0.7]],
        },
    )


def complete_main(loaded: Loaded) -> Loaded:
    assert loaded.release is not None
    release = loaded.release
    templates = {"B": release.curves[B[0.5]], "other": release.curves[D[0.5]]}
    curves = {
        key: dataclasses.replace(
            templates["B" if meta.family == "B" else "other"],
            meta=meta,
            main_curve_valid=None,
        )
        for key, meta in unit_catalog().items()
        if meta.tier <= 2
    }
    statuses = dict(release.statuses)
    statuses.update(dict.fromkeys(curves, VALID))
    return dataclasses.replace(
        loaded, release=Release(release.closed_utc, True, statuses, curves)
    )


def test_family_region_counts_use_one_common_gap_free_r_mask(
    predicate_loaded: Loaded,
) -> None:
    loaded = predicate_loaded
    complete = complete_main(loaded)
    assert complete.release is not None and loaded.release is not None
    curves = dict(complete.release.curves)
    gap = loaded.release.curves[B[0.7]]
    curves[B[0.7]] = gap
    curves[D[0.75]] = dataclasses.replace(gap, meta=unit_catalog()[D[0.75]])
    masked = dataclasses.replace(
        complete, release=dataclasses.replace(complete.release, curves=curves)
    )
    values = result_values(masked)
    assert values["v4.bd.n_eligible"] == "7"
    assert values["v4.bd.r_eligible"] == "0.50--0.65 and 0.80--0.90"
    assert values["v4.bd.B.n_small"] == "7"
    assert values["v4.bd.D.n_not_attained"] == "7"
    assert values["v4.bd.n_side_by_side"] == "9"
    assert values["v4.bd.r_side_by_side"] == "0.50--0.90"


@pytest.mark.parametrize(
    ("case", "dependent", "not_assessed"),
    [
        ("all-flat", "1", "0"),
        ("rank-crosses", "0", "0"),
        ("ordinal-invalid", "0", "1"),
        ("latent-gap", "0", "1"),
        ("rank-missing", "0", "1"),
        ("rank-only-exceeded", "0", "0"),
    ],
)
def test_channel_reading_requires_all_three_gap_free_controls(
    predicate_loaded: Loaded, case: str, dependent: str, not_assessed: str
) -> None:
    loaded = predicate_loaded
    assert loaded.release is not None
    source = loaded.release
    observed = source.curves[B[0.5]]
    curves = {B[0.5]: observed}
    for key, meta in unit_catalog().items():
        if (meta.tier, meta.family, meta.r, meta.sensitivity) != (3, "B", 0.5, "main"):
            continue
        if meta.channel not in ("latent", "ordinal_one", "latent_rank"):
            continue
        if case == "rank-missing" and meta.channel == "latent_rank":
            continue
        template = source.curves[D[0.5]]
        if case == "rank-crosses" and meta.channel == "latent_rank":
            template = observed
        elif case == "latent-gap" and meta.channel == "latent":
            template = source.curves[B[0.7]]
        elif case == "rank-only-exceeded" and meta.channel != "latent_rank":
            template = observed
        curve = dataclasses.replace(template, meta=meta, main_curve_valid=None)
        if case == "ordinal-invalid" and meta.channel == "ordinal_one":
            curve = dataclasses.replace(curve, status=INVALID)
        curves[key] = curve
    statuses = dict.fromkeys(source.statuses, NOT_STARTED)
    statuses.update({key: c.status for key, c in curves.items()})
    values = result_values(
        dataclasses.replace(
            loaded, release=Release(source.closed_utc, False, statuses, curves)
        )
    )
    assert values["v4.t3.n_channel_dependent"] == dependent
    assert values["v4.t3.n_channel_not_assessed"] == not_assessed
    assert values["v4.t3.n_pairs_compared"] == "1"
    assert values["v4.t3.n_obs_exceeds"] == "1"


def test_one_invalid_sensitivity_selects_b12_even_without_region_difference(
    predicate_loaded: Loaded,
) -> None:
    loaded = predicate_loaded
    complete = complete_main(loaded)
    assert complete.release is not None
    release = complete.release
    curves = dict(release.curves)
    for key, meta in unit_catalog().items():
        if meta.tier >= 4:
            curves[key] = dataclasses.replace(curves[B[0.5]], meta=meta)
    invalid = next(key for key, meta in unit_catalog().items() if meta.tier == 4)
    curves[invalid] = dataclasses.replace(curves[invalid], status=INVALID)
    statuses = dict(release.statuses)
    statuses.update({key: c.status for key, c in curves.items()})
    values = result_values(
        dataclasses.replace(
            complete,
            release=dataclasses.replace(release, curves=curves, statuses=statuses),
        )
    )
    assert values["v4.sens.n_region_differs"] == "0"
    assert values["v4.sens.n_not_valid"] == "1"
    assert values["v4.sens.use_b12"] == "1"


def test_low_positive_boundary_uses_interval_region_instead_of_point_only(
    predicate_loaded: Loaded,
) -> None:
    assert predicate_loaded.release is not None
    release = predicate_loaded.release
    curves = dict(release.curves)
    curves[B[0.5]] = dataclasses.replace(
        curves[B[0.5]], first=Boundary(0.003, (0.001, 0.1), None, None)
    )
    values = result_values(
        dataclasses.replace(
            predicate_loaded, release=dataclasses.replace(release, curves=curves)
        )
    )
    assert values["v4.t1.n_first_low"] == "1"
    assert values["v4.t1.low.n_small"] == "0"
    assert values["v4.t1.low.n_indeterminate"] == "1"


def test_precision_counts_separate_finite_width_beyond_grid_and_gap(
    predicate_loaded: Loaded,
) -> None:
    assert predicate_loaded.release is not None
    release = predicate_loaded.release
    curves = dict(release.curves)
    for r, boundary in (
        (0.5, Boundary(0.003, (0.001, 0.1), None, None)),
        (0.55, Boundary(0.1, (0.03, None), None, None)),
        (0.6, Boundary(0.03, (0.01, None), None, "gap at a=0.1")),
    ):
        curves[B[r]] = dataclasses.replace(
            curves[B[0.5]], meta=unit_catalog()[B[r]], first=boundary
        )
    statuses = dict(release.statuses)
    statuses.update(dict.fromkeys(curves, VALID))
    values = result_values(
        dataclasses.replace(
            predicate_loaded,
            release=dataclasses.replace(release, curves=curves, statuses=statuses),
        )
    )
    assert values["v4.t1.n_wide"] == "3"
    assert values["v4.t1.n_interval_wide_finite"] == "1"
    assert values["v4.t1.n_interval_beyond_grid"] == "1"
    assert values["v4.t1.n_interval_gap"] == "1"


def test_frozen_reading_lists_identify_each_shared_r(predicate_loaded: Loaded) -> None:
    values = result_values(complete_main(predicate_loaded))
    assert values["v4.bd.r_persistence"] == "0.50--0.90"
    assert values["v4.bd.r_both"] == "none"
    assert values["v4.bd.r_inconclusive"] == "none"
    assert values["v4.bd.r_no_b_crossing"] == "none"


@pytest.mark.parametrize(
    ("decision", "document", "required", "forbidden"),
    [
        (
            "Q8-Q19",
            "results-shells.tex",
            "% MECHANISMS := v4.mechanisms.allowed == 1",
            "% P6-a: select when no i has FULL",
        ),
        (
            "common-mask",
            "results-shells-abstract.md",
            "v4.bd.B.n_small",
            "v4.t2.D.n_small",
        ),
        (
            "Q13-E",
            "results-shells.tex",
            "compatible with mover--stayer heterogeneity",
            "the corresponding reading against E",
        ),
        (
            "Q13-C",
            "results-shells.tex",
            "compatible with heteroscedastic error and heaping",
            "the corresponding reading against E",
        ),
        (
            "Q6",
            "results-shells.tex",
            "% SUPPLEMENT: every B1a branch with curves",
            '% Include only if the Owner answers notes Q6 "yes".',
        ),
        (
            "B04",
            "results-shells.tex",
            "v4.t1.low.n_indeterminate",
            "These boundaries fall in the region ``small''",
        ),
        (
            "B04z",
            "results-shells.tex",
            "``indeterminate'' and reports",
            "without a region",
        ),
        ("B09", "results-shells-abstract.md", "v4.t1.n_interval_gap", "v4.t1.n_wide"),
        (
            "B11",
            "results-shells.tex",
            "v4.t3.n_channel_not_assessed",
            "while the complete control did not attain it",
        ),
        (
            "B12",
            "results-shells.tex",
            "% SELECT WHEN: B1a selected and v4.sens.use_b12 == 1",
            "or (b) some U(k) of tiers 4-6 is",
        ),
        (
            "B17-b",
            "results-shells.tex",
            "was exposed during calibration and is marked",
            "Its boundary differs from those at the neighbouring",
        ),
        (
            "X6",
            "results-shells-abstract.md",
            "v4x.x6.x6a.band.vs_d1.primary.reading",
            "X6-PRIMARY-D1-ID-PENDING",
        ),
    ],
)
def test_shell_decision91_predicates(
    decision: str,
    document: str,
    required: str,
    forbidden: str,
) -> None:
    source = (SHELLS.parent / document).read_text(encoding="utf-8")
    assert required in source, decision
    if forbidden:
        assert forbidden not in source, decision


def test_gate_failure_abstract_baseline_meets_jcss_word_budget() -> None:
    source = (SHELLS.parent / "results-shells-abstract.md").read_text("utf-8")

    def quote(heading: str) -> str:
        start = source.index(heading)
        return next(
            line[2:] for line in source[start:].splitlines() if line.startswith("> ")
        )

    sentences = [
        quote("## Composition and budget"),
        quote("**B1b-G0**"),
        quote("**X**,"),
        quote("Every branch retains:"),
    ]
    if "Gate-failure abstracts additionally retain:" in source:
        sentences.append(quote("Gate-failure abstracts additionally retain:"))
    assert 150 <= _paper_check().word_count(" ".join(sentences)) <= 250


def test_secondary_counts_belong_to_supplement_block_in_every_release_branch() -> None:
    source = SHELLS.read_text("utf-8")
    main = source.split("% BEGIN BRANCH B00", 1)[1].split("% END BRANCH B00", 1)[0]
    assert "v4.t1.sec060" not in main
    assert "v4.t1.sec080" not in main
    supplement = source.split("% BEGIN BLOCK SECONDARY-SUPPLEMENT", 1)[1]
    assert "v4.t1.sec060" in supplement
    assert "v4.t1.sec080" in supplement


@pytest.mark.parametrize(
    "branch", ["nonattainment", "incomplete-tier2", "invalid-main"]
)
def test_secondary_supplement_keeps_every_r_and_valid_outputs_in_every_branch(
    predicate_loaded: Loaded,
    branch: str,
) -> None:
    loaded = complete_main(predicate_loaded)
    assert loaded.release is not None
    release = loaded.release
    curves, statuses = dict(release.curves), dict(release.statuses)
    if branch == "nonattainment":
        for key in B.values():
            curves[key] = dataclasses.replace(curves[D[0.5]], meta=unit_catalog()[key])
    elif branch == "incomplete-tier2":
        key = unit_keys(tier=2, family="A")[0.9]
        del curves[key]
        statuses[key] = NOT_STARTED
    else:
        curves[B[0.9]] = dataclasses.replace(curves[B[0.9]], status=INVALID)
        statuses[B[0.9]] = INVALID
    release = dataclasses.replace(
        release,
        curves=curves,
        statuses=statuses,
        main_curve_valid=branch != "invalid-main",
    )
    files, bound = generated_files(
        dataclasses.replace(loaded, release=release), lambda stem: f"{stem}.pdf", True
    )
    assert "Derived first boundaries" in "\n".join(
        files["supplement-secondary-targets"]
    )
    assert {f"v4.tab.T1sec.B.r{round(r * 100):03d}.r" for r in B} <= bound.keys()
    assert "F1_a_star_by_family.pdf" in "\n".join(files["primary-boundary-figure"])
    if branch == "invalid-main":
        assert "Main curve invalid" in "\n".join(files["boundary-table"])
        secondary = "\n".join(files["supplement-secondary-targets"])
        assert "Main curve invalid" in secondary
        assert secondary.count(r"\ddag{}") == 9


def test_export_binds_every_number_of_the_manuscript_for_its_checker(
    env: dict[str, Any], tmp_path: Path
) -> None:
    manuscript = tmp_path / "manuscript"
    shutil.copytree(MANUSCRIPT, manuscript)
    results = manuscript / "sections/results.tex"
    results.write_text(
        results.read_text(encoding="utf-8")
        + "At the close, \\resultnum{v4.inv.n_valid}{[n]} units were complete valid"
        " and \\resultnum{v4.bd.n_persistence}{[n]} values of $r$ read as"
        " persistence.\n",
        encoding="utf-8",
    )
    values = tmp_path / "result-values.json"
    code = main(
        [
            *env["arguments"],
            "--report",
            str(env["report"]),
            "--manuscript",
            str(manuscript),
            "--values",
            str(values),
            "--fill",
        ]
    )
    assert code == 0
    check = _paper_check()
    root = manuscript.resolve()
    assert check.result_consistency(root, check.tex_sources(root), values, True) == []
    bound = json.loads(values.read_text(encoding="utf-8"))["values"]
    assert set(bound) == used_ids(manuscript)
    assert bound["v4.inv.n_valid"] == str(len(PLANS))
    assert r"\resultnum{v4.bd.n_persistence}{0}" in results.read_text(encoding="utf-8")
    generated = manuscript / "generated"
    for name in PLACEHOLDERS:
        assert "Placeholder" not in (generated / f"{name}.tex").read_text("utf-8")
    boundaries = (generated / "boundary-table.tex").read_text(encoding="utf-8")
    assert r"\label{tab:v4-T1}" in boundaries
    labels = {
        "supplement-low-strength-cells": "tab:v4-slow",
        "supplement-gap-domain": "tab:v4-sgaps",
    }
    for name, label in labels.items():
        content = (generated / f"{name}.tex").read_text(encoding="utf-8")
        assert rf"\label{{{label}}}" in content
    for name in ("F1_a_star_by_family.pdf", "T1s_a_star_all_units.csv"):
        assert (generated / name).read_bytes() == (env["report"] / name).read_bytes()


def test_values_apply_the_frozen_readings_and_match_the_t1_regions(
    loaded: Loaded,
) -> None:
    release = loaded.release
    assert release is not None
    curves = release.curves
    assert all(max(curves[B[r]].lower) > TARGET for r in (0.5, 0.55, 0.6))
    assert max(curves[B[0.65]].lower) <= TARGET
    assert max(curves[D[0.5]].upper) < TARGET
    assert max(curves[D[0.6]].lower) <= TARGET <= max(curves[D[0.6]].upper)
    values = result_values(loaded)
    readings = ("n_eligible", "n_persistence", "n_both", "n_inconclusive")
    assert values["v4.mechanisms.allowed"] == "0"
    assert [values[f"v4.bd.{name}"] for name in readings] == ["0"] * 4
    complete = complete_main(loaded)
    assert complete.release is not None
    paired_curves = {**complete.release.curves, **curves}
    paired = result_values(
        dataclasses.replace(
            complete,
            release=dataclasses.replace(complete.release, curves=paired_curves),
        )
    )
    assert [paired[f"v4.bd.{name}"] for name in readings] == ["8", "5", "1", "1"]
    assert paired["v4.bd.n_no_b_crossing"] == "1"
    assert paired["v4.bd.n_other"] == "2"
    assert paired["v4.bd.r_both"] == "0.55"
    assert paired["v4.bd.r_inconclusive"] == "0.60"
    t1 = table_t1(release)
    rows = [dict(zip(t1.header, row, strict=True)) for row in t1.rows]
    regions = [r["region"] for r in rows if r["family"] == "B" and r["status"] == VALID]
    assert values["v4.t1.n_small"] == str(regions.count("small"))
    assert values["v4.t1.n_large"] == str(regions.count("large"))
    assert values["v4.t1.n_not_attained"] == str(regions.count("not attained"))
    censored = regions.count("censored (gap)") + regions.count("indeterminate")
    assert values["v4.t1.n_censored"] == str(censored)
    assert values["v4.t1.n_first_gap"] == "1"
    assert (values["v4.t1.n_valid"], values["v4.t1.n_clock"]) == ("6", "3")
    assert (values["v4.t1.n_first_low"], values["v4.low.n_cells"]) == ("1", "2")
    assert values["v4.low.n_retry"] == "0"
    assert {"v4.low.projected_fraction_max", "v4.low.amplification_max"} <= set(values)
    assert values["v4.inv.n_not_started"] == str(414 - len(PLANS))
    assert values["v4.gate.G1c.anchor_count"] == "150"


def test_export_refuses_a_report_rendered_from_other_inputs(
    env: dict[str, Any], tmp_path: Path
) -> None:
    other = tmp_path / "released_curves.json"
    other.write_text(
        env["inputs"].curves.read_text(encoding="utf-8") + "\n", encoding="utf-8"
    )
    receipt = other.with_name("release-record.json")
    side = json.loads(
        env["inputs"].curves.with_name("release-record.json").read_bytes()
    )
    side["released_curves_sha256"] = hashlib.sha256(other.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(side))
    manuscript = tmp_path / "manuscript"
    with pytest.raises(ValueError, match="other inputs"):
        export(
            dataclasses.replace(env["inputs"], curves=other), env["report"], manuscript
        )
    assert not manuscript.exists()


def test_export_refuses_a_table_edited_after_rendering(
    env: dict[str, Any], tmp_path: Path
) -> None:
    report = tmp_path / "report"
    shutil.copytree(env["report"], report)
    table = report / "T4_inventory.csv"
    table.write_text(
        table.read_text(encoding="utf-8").replace(",9,", ",8,", 1), encoding="utf-8"
    )
    with pytest.raises(ValueError, match=r"T4_inventory\.csv"):
        export(env["inputs"], report, tmp_path / "manuscript")


def test_without_a_release_only_the_gate_is_reported_and_exported(
    tmp_path: Path,
) -> None:
    budget = {("B", 0.3, 0.7): ("budget", 1)}
    plan = GatePlan(stages=("G0",), g0_failures={**G0_FAILURES, **budget})
    inputs = Inputs(None, build_gate(tmp_path / "gate", plan), criteria=CRITERIA)
    report = tmp_path / "report"
    render(inputs, report, dpi=40, formats=("pdf",))
    assert sorted(path.name for path in report.iterdir()) == [
        "F4_gate_diagnostics.pdf",
        "T3_gate_summary.csv",
        "T3_gate_summary.tex",
        "manifest.json",
    ]
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "main.tex").write_text("\\input{generated/gate-outcomes}\n", "utf-8")
    result = export(inputs, report, manuscript)
    assert [path.stem for path in result.written] == list(PLACEHOLDERS)
    for path in result.written[1:]:
        lines = path.read_text(encoding="utf-8").splitlines()
        assert all(line.startswith("%") for line in lines), path.name
    assert not list((manuscript / "generated").glob("*.csv"))
    assert result.catalog["v4.gate.G0.budget_statuses"] == "1"
    assert "v4.gate.last_stage" not in result.catalog
    assert not any(key.startswith("v4.inv.") for key in result.catalog)
    assert used_ids(manuscript) <= result.catalog.keys()


def test_an_unfinished_stage_is_named_with_its_progress(tmp_path: Path) -> None:
    plan = GatePlan(stages=("G0", "G1b"), running={"G1b": 7})
    values = result_values(load_inputs(Inputs(None, build_gate(tmp_path / "g", plan))))
    assert values["v4.gate.last_stage"] == "G1b"
    progress = (
        values["v4.gate.last_stage.completed"],
        values["v4.gate.last_stage.planned"],
    )
    assert progress == ("7", "5000")


def test_a_stop_before_g2_is_reported_with_its_gap_binding(tmp_path: Path) -> None:
    gaps = {("B", 0.001, r): ("no-L1-root", 1) for r in (0.5, 0.55)}
    plan = GatePlan(stages=("G0",), g0_failures={**G0_FAILURES, **gaps})
    root = build_gate(tmp_path / "gate", plan)
    stop = stop_before_g2(root, tmp_path / "v4-allocation.json")
    assert stop is not None
    binding = cast(dict[str, Any], stop["g0_gap_binding"])
    values = result_values(load_inputs(Inputs(None, root)))
    probability = f"{binding['pass_probability']:.3f}"
    assert values["v4.gate.stop.gaps"] == str(binding["gaps"])
    assert values["v4.gate.stop.pass_probability"] == probability
    assert "v4.gate.last_stage" not in values


def test_a_low_cell_used_the_retry_when_an_attempt_had_the_retry_pairs() -> None:
    def cell(pairs: tuple[int, ...]) -> LowCell:
        found = CellDiagnostics(pairs, (), None, None, None, None, None)
        return LowCell(0.75, 0.003, found)

    assert cell((1024, 4096)).retry
    assert not cell((1024,)).retry


def test_protocol_constants_are_read_from_the_frozen_sources() -> None:
    values = protocol_values()
    expected = {
        "v4.protocol.target": "0.70",
        "v4.protocol.null_auc": "0.5",
        "v4.protocol.critical_floor": "2.7729",
        "v4.protocol.g1b.pass_mark": "935",
        "v4.protocol.g1b.repetitions": "1,000",
        "v4.protocol.g1c.fits": "150",
        "v4.protocol.g1c.mean_z_limit": "3",
        "v4.protocol.g0.implementation_limit": "1",
        "v4.protocol.g2.fd_step.small": "0.005",
        "v4.protocol.g2c.bound_level": "95",
        "v4.protocol.g2c.refits.a003": "40",
        "v4.protocol.retry_pairs": "4,096",
        "v4.protocol.units.all": "414",
        "v4.protocol.tier.last_sensitivity": "6",
        "v4.protocol.close_local": "18 October 2026 at 23:59",
        "v4.protocol.chance_invalidation": "4.9",
        "v4.protocol.shp.wald_level": "95",
    }
    assert {key: values[key] for key in expected} == expected


def test_a_frozen_source_that_drifted_is_refused(tmp_path: Path) -> None:
    freeze = json.loads(
        (
            STUDY / "experiments/exploratory/detection-boundary-v4/freeze-v4.json"
        ).read_text(encoding="utf-8")
    )
    relative = "src/ic_study/simulation/v4_gate.py"
    copy = tmp_path / "v4_gate.py"
    copy.write_bytes((STUDY / relative).read_bytes() + b"\n")
    with pytest.raises(ValueError, match="freeze record"):
        _verified(copy, freeze["code"][relative])


def test_results_shells_bind_every_number_to_the_export() -> None:
    check = _paper_check()
    body = [
        line.split(" % RS")[0]
        for line in SHELLS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("%")
    ]
    protocol = protocol_values()
    for line in body:
        for key, shown in check.RESULT_MACRO.findall(line):
            if key.startswith("v4.protocol."):
                assert protocol[key] == shown, key
            else:
                assert shown.startswith("["), key
        stripped = check.RESULT_MACRO.sub("", line)
        stripped = re.sub(r"\\(?:ref|texttt)\s*\{[^{}]*\}", "", stripped)
        assert check.RESULT_NUMBER.search(stripped) is None, line


def test_bound_cells_leave_no_number_for_the_checker() -> None:
    check = _paper_check()
    assert NUMBER.pattern == check.RESULT_NUMBER.pattern
    assert RESULT.pattern == check.RESULT_MACRO.pattern
    binder = Binder()
    cells = {
        "a": "1/648 = 0.0015",
        "b": "a=0 identity fits",
        "c": "gap 0.003 [gap 0.003, >0.9]",
        "d": "gaussian-icc05, 1,000 draws, -0.5 and 1e-05",
    }
    text = " & ".join(binder.cell(value, key) for key, value in cells.items())
    assert check.RESULT_NUMBER.search(check.RESULT_MACRO.sub("", text)) is None
    assert binder.values == {
        "a.1": "1",
        "a.2": "648",
        "a.3": "0.0015",
        "b": "0",
        "c.1": "0.003",
        "c.2": "0.003",
        "c.3": "0.9",
        "d.1": "1,000",
        "d.2": "-0.5",
        "d.3": "05",
    }


def test_fill_replaces_only_the_placeholders_of_known_ids(tmp_path: Path) -> None:
    (tmp_path / "sections").mkdir()
    (tmp_path / "main.tex").write_text("\\input{sections/results}\n", "utf-8")
    results = tmp_path / "sections/results.tex"
    results.write_text(
        r"\resultnum{a}{[n]} \resultnum{b}{[x]} \resultnum{c}{7}" + "\n", "utf-8"
    )
    fill(tmp_path, {"a": "3", "c": "9"})
    assert results.read_text("utf-8") == (
        r"\resultnum{a}{3} \resultnum{b}{[x]} \resultnum{c}{7}" + "\n"
    )
    assert used_ids(tmp_path) == {"a", "b", "c"}


def test_frozen_preregistration_drift_is_refused_by_the_shared_reader(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ic_study.analysis import v4_report_protocol as reader

    path = tmp_path / "preregistration.md"
    path.write_text("Alvos 0,60 e 0,80 são secundários. pequena, `0<a*≤0,04`")
    reader.protocol.cache_clear()
    try:
        with monkeypatch.context() as patch:
            patch.setattr(reader, "PREREGISTRATION", path, raising=False)
            with pytest.raises(ValueError, match="freeze record"):
                protocol_values()
    finally:
        reader.protocol.cache_clear()


def test_t3_reads_criteria_from_the_same_protocol_as_the_catalog(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from ic_study.analysis import v4_report_protocol, v4_report_tables
    from ic_study.analysis.v4_report_schema import load_gate

    gate = build_gate(tmp_path / "gate", GatePlan(stages=("G1b", "G1c")))
    with (gate / "criteria.jsonl").open("a") as handle:
        handle.write(json.dumps(stage_successor(gate)["summary"]) + "\n")
    p = dataclasses.replace(
        v4_report_protocol.protocol(),
        g1b_pass_mark=934,
        g1b_repetitions=999,
        g1c_fits=149,
        g1c_mean_z_limit=2.5,
        g1c_pointwise_limit=2,
    )
    monkeypatch.setattr(v4_report_tables, "protocol", lambda: p, raising=False)
    rows = v4_report_tables.table_t3(load_gate(gate), None).rows
    assert any(row[3] == ">= 934/999" for row in rows)
    assert any(row[3] == "= 149/149" for row in rows)
    assert any(row[3] == "<= 2.5" for row in rows)
    assert any(row[3] == "<= 2" for row in rows)


def test_shells_distinguish_effective_release_from_nominal_close() -> None:
    source = SHELLS.read_text(encoding="utf-8")
    assert "released at the close" not in source
    assert "At the close on" not in source
    assert r"\resultnum{v4.release.effective_local}{[time]}" in source
    assert r"\resultnum{v4.release.condition}{[condition]}" in source
    assert r"\resultnum{v4.protocol.close_local}{18 October 2026 at 23:59}" in source


def test_export_keeps_effective_release_time_and_trigger(loaded: Loaded) -> None:
    receipt = loaded.release_record
    assert receipt is not None
    early = dataclasses.replace(
        receipt, released_utc="2026-10-08T12:34:56Z", condition="inventory-complete"
    )
    values = result_values(dataclasses.replace(loaded, release_record=early))
    assert values["v4.release.effective_local"] == "8 October 2026 at 09:34:56"
    assert values["v4.release.effective_utc"] == "2026-10-08T12:34:56Z"
    assert values["v4.release.condition"] == "completion of the full inventory"
    assert values["v4.protocol.close_local"] == "18 October 2026 at 23:59"
    assert result_values(loaded)["v4.release.condition"] == "the declared close"


@pytest.mark.parametrize("stage", ["G0", "G1b", "G1c", "G2", "G2c"])
@pytest.mark.parametrize("state", ["absent", "partial", "passed", "failed", "stop"])
def test_gate_verdict_ids_use_complete_records_and_never_promote_partial_pass(
    stage: str, state: str
) -> None:
    from ic_study.analysis.v4_report_export import gate_values
    from ic_study.analysis.v4_report_schema import GateRecords

    summaries = {}
    if state not in {"absent", "stop"}:
        summary: dict[str, Any] = {
            "gate": stage,
            "planned": 10,
            "completed": 9 if state == "partial" else 10,
            "failures": 1 if state == "failed" else 0,
            "pass": state != "failed",
        }
        if stage == "G1c" and state == "passed":
            summary |= {
                "planned": 150,
                "completed": 150,
                "anchor_count": 150,
                "pointwise_failures": 0,
                "mean_z": 0.0,
                "tie_rate": 0.0,
            }
        summaries[stage] = summary
    stop = (
        {
            "g0_gap_binding": {
                "gaps": 2,
                "denominator": 54,
                "pass_probability": 0.4,
                "minimum": 0.8,
            }
        }
        if state == "stop"
        else None
    )
    gate = GateRecords(
        summaries,
        {},
        stop,
        (),
        (),
        (),
        (),
        None,
        {},
        {s: 10 for s in ("G0", "G1b", "G1c", "G2", "G2c")},
    )
    values = gate_values(gate, None)
    assert values[f"v4.gate.{stage}.verdict.complete"] == str(
        int(state in {"passed", "failed"})
    )
    assert values[f"v4.gate.{stage}.verdict.approved"] == str(int(state == "passed"))
    assert values[f"v4.gate.{stage}.verdict.stop"] == str(
        int(state == "stop" and stage == "G2")
    )
    assert sum(".verdict." in key for key in values) == 15


def test_family_e_is_named_mover_stayer_persistence_in_every_display() -> None:
    assert "E (mover--stayer persistence)" in CAPTION_F1
    assert any(
        "E = mover--stayer persistence" in note for note in v4_report_tables._T1_NOTES
    )
    assert v4_report_figures.FAMILY_LABEL["E"] == "E: mover\u2013stayer persistence"
    labels = (
        CAPTION_F1,
        *v4_report_tables._T1_NOTES,
        *v4_report_figures.FAMILY_LABEL.values(),
    )
    assert not any("stayer-mover" in text for text in labels)


@pytest.mark.parametrize(
    ("rs", "listed"),
    [
        ((0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9), "0.50--0.90"),
        ((0.7,), "0.70"),
        ((0.5, 0.55), "0.50 and 0.55"),
        ((0.5, 0.55, 0.6, 0.65, 0.75, 0.85, 0.9), "0.50--0.65, 0.75, 0.85 and 0.90"),
        ((0.9, 0.5, 0.6, 0.65, 0.7), "0.50, 0.60--0.70 and 0.90"),
        ((0.55, 0.6, 0.7, 0.75, 0.85), "0.55, 0.60, 0.70, 0.75 and 0.85"),
        ((), "none"),
    ],
)
def test_r_lists_are_runs_on_the_declared_grid(
    rs: tuple[float, ...], listed: str
) -> None:
    assert grid_runs(rs) == listed


def test_r_lists_absorb_float_noise_on_a_grid_value() -> None:
    assert grid_runs((0.6500000000000001,)) == "0.65"
    assert grid_runs((0.7 - 0.05,)) == "0.65"
    with pytest.raises(ValueError, match="not on the declared grid"):
        grid_runs((0.66,))


@pytest.mark.parametrize(
    "rs", [(0.5, 0.52), (0.504,), (0.549, 0.599, 0.649), (0.9, 0.91)]
)
def test_r_lists_refuse_a_value_off_the_declared_grid(
    rs: tuple[float, ...],
) -> None:
    with pytest.raises(ValueError, match="not on the declared grid"):
        grid_runs(rs)
