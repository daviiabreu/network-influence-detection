"""Assembly decisions use exported synthetic values, never sealed records."""

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import pytest

from ic_study.analysis.detection_v4_report import Loaded
from ic_study.analysis.v4_manuscript_assembly import (
    OPTIONAL_ORDER,
    RULES,
    AssemblyPlan,
    AssemblyRefusedError,
    Decision,
    _Evaluator,
    _fragment_text,
    assemble,
    assembled_values,
    bind,
    compose_documents,
    document_errors,
    first_fit,
    load_catalog,
    load_facts,
    main,
    plan,
    shell_texts,
    visible_word_count,
)
from ic_study.analysis.v4_manuscript_assembly_facts import FACTS_SCHEMA, validate_facts
from ic_study.analysis.v4_report_export import result_values
from ic_study.analysis.v4_report_schema import parse_release
from ic_study.analysis.v4_report_synthetic import UnitPlan, build_release, unit_keys

STUDY = Path(__file__).resolve().parents[2]
MANUSCRIPT = STUDY / "publications/jcss-manuscript"
ORACLES = STUDY / "tests/fixtures/v4_manuscript_assembly/manual_oracles.json"
ORACLE_DATA: dict[str, Any] = json.loads(ORACLES.read_text())
CURRENT_ORACLE_DATA: dict[str, Any] = json.loads(
    (ORACLES.parent / "current_shell_oracles.json").read_text()
)
CURRENT_ORACLES: dict[str, str] = json.loads(
    (ORACLES.parent / "t58-abstract-oracles.json").read_text()
)["abstracts"]
CASES = {row["name"]: row for row in ORACLE_DATA["cases"]}
READING = "v4x.x6.x6a.band.vs_d1.primary.reading"
# Exploratory detail that T57c keeps out of the Discussion (X6 reuses X3 sizes).
EXPLORATORY_DETAIL = re.compile(
    r"\\resultnum\{v4x\.(?:x3\.(?!sizes)|x4|x7|comparisons\."
    r"(?:count\.(?:x1b|x3|x4)|by_r\.[0-9-]+\.(?:x1b|x3|x4)))"
)


@pytest.fixture(scope="module", autouse=True)
def exported_manuscript(tmp_path_factory: pytest.TempPathFactory) -> Iterator[None]:
    global MANUSCRIPT
    original = MANUSCRIPT
    MANUSCRIPT = tmp_path_factory.mktemp("public-export") / "manuscript"
    shutil.copytree(original, MANUSCRIPT)
    shutil.copytree(
        ORACLES.parent / "exported_generated",
        MANUSCRIPT / "generated",
        dirs_exist_ok=True,
    )
    try:
        yield
    finally:
        MANUSCRIPT = original


def test_document_admissibility_reports_missing_input_and_duplicate_expansion(
    tmp_path: Path,
) -> None:
    generated = tmp_path / "generated"
    generated.mkdir()
    (generated / "table.tex").write_text(r"\label{tab:one}")
    documents = {
        "main.tex": (
            "% \\input{generated/commented}\n"
            "\\input{generated/missing}\n"
            "\\input{generated/table}\n\\input{generated/table}\n"
        )
    }
    errors = document_errors(tmp_path, documents)
    assert errors[0] == ("main.tex", 2, "Missing input: generated/missing.tex")
    assert len(errors) == 2
    assert "Duplicate label tab:one" in errors[1][2]
    assert "generated/table.tex:1" in errors[1][2]


def test_missing_generated_input_refuses_ready_and_leaves_no_copy(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    shutil.copytree(MANUSCRIPT, source)
    (source / "generated/exploratory-x1b-boundaries.tex").unlink()
    values, facts = complete_values("passed-shp"), owner_facts("passed-shp")
    report = plan(values, {}, manuscript=source, facts=facts)
    assert report.as_dict()["status"] == "refused"
    assert any("exploratory-x1b-boundaries.tex" in d.reason for d in report.refused)
    with pytest.raises(AssemblyRefusedError, match=r"main.tex:\d+.*Missing input"):
        assemble(values, {}, manuscript=source, facts=facts, output=tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_duplicate_x7_display_refuses_the_whole_assembly(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shutil.copytree(MANUSCRIPT, source)
    main_path = source / "main.tex"
    main_path.write_text(
        main_path.read_text() + "\n\\input{generated/exploratory-x7-boundaries}\n"
    )
    with pytest.raises(AssemblyRefusedError, match="Duplicate label"):
        assemble(
            complete_values("passed-shp"),
            {},
            manuscript=source,
            facts=owner_facts("passed-shp"),
            output=tmp_path / "out",
        )
    assert not (tmp_path / "out").exists()


def test_zero_comparisons_and_band_flags_supply_no_positive_channel_or_dip_text() -> (
    None
):
    report = plan(
        complete_values("invalid-main"),
        {},
        manuscript=MANUSCRIPT,
        facts=owner_facts("invalid-main"),
    )
    assert report.decisions["A.B05"].state == "excluded"
    assert "band endpoints" in report.decisions["B05"].text
    assert "so the sustained boundary" not in report.decisions["B05"].text
    assert report.decisions["A.B11"].state == "excluded"
    assert "not assessed" in report.decisions["B11"].text
    assert "sensitivity of the lag" not in report.decisions["B11"].text
    assert "labelled channel-dependent" not in report.decisions["B11"].text
    assert report.decisions["P7-c1"].state == "selected"


@pytest.mark.parametrize("count", ["n_obs_exceeds", "n_channel_dependent"])
def test_zero_comparisons_refuse_a_contradictory_positive_channel_count(
    count: str,
) -> None:
    values = complete_values("passed-shp")
    values["v4.t3.n_pairs_compared"] = "0"
    values["v4.t3." + count] = "1"
    with pytest.raises(ValueError, match="Inconsistent channel counts"):
        plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))


def test_first_and_sustained_sentences_state_only_positive_counts() -> None:
    values = complete_values("passed-shp")
    facts = owner_facts("passed-shp")
    values["v4.t1.n_first_ne_sustained"] = "2"
    text = plan(values, {}, manuscript=MANUSCRIPT, facts=facts).decisions["B06"].text
    assert r"differ at \resultnum{v4.t1.n_first_ne_sustained}{2} values of $r$" in text
    assert "censored at a gap" not in text
    values["v4.t1.n_sustained_gap"] = "1"
    text = plan(values, {}, manuscript=MANUSCRIPT, facts=facts).decisions["B06"].text
    assert "Where a sustained boundary is censored at a gap" in text
    assert "of them" not in text
    values["v4.t1.n_first_ne_sustained"] = values["v4.t1.n_sustained_gap"] = "0"
    facts["facts"]["tier2.boundaries_differ"]["value"] = True
    decision = plan(values, {}, manuscript=MANUSCRIPT, facts=facts).decisions["B06"]
    assert decision.state == "selected"
    assert decision.text.startswith(r"Table~\ref{tab:v4-T1} gives")
    assert "differ at" not in decision.text
    assert decision.text.endswith("the abstract states at how many shares they differ.")


def test_nonmonotone_boundary_excludes_only_a_global_existence_claim() -> None:
    facts = owner_facts("passed-shp")
    facts["facts"]["main.boundary_nonmonotone"]["value"] = True
    report = plan(complete_values("passed-shp"), {}, manuscript=MANUSCRIPT, facts=facts)
    text = report.decisions["B07"].text
    assert "no global claim is made that separation holds at some value of $r$." in text
    assert "whole-curve claim" not in text


def composed_documents(
    case: str, values: dict[str, str] | None = None
) -> tuple[AssemblyPlan, dict[str, str]]:
    report = plan(
        complete_values(case) if values is None else values,
        {},
        manuscript=MANUSCRIPT,
        facts=owner_facts(case),
    )
    sources = {
        name: (MANUSCRIPT / name).read_text()
        for name in (
            "main.tex",
            "sections/discussion.tex",
            "sections/conclusion.tex",
            "sections/supplement.tex",
        )
    }
    documents, _ = compose_documents(report, sources)
    return report, documents


def test_discussion_points_to_the_exploratory_supplement_instead_of_repeating_it() -> (
    None
):
    report, documents = composed_documents("passed-shp")
    pointer = report.decisions["D-EXPLORATORY-SUPPLEMENT"]
    assert pointer.state == report.decisions["E.status-and-scope"].state == "selected"
    discussion = documents["sections/discussion.tex"]
    assert discussion.count(pointer.text) == 1
    # The pointer closes the fixed DS10 paragraph rather than standing alone.
    start = discussion.index(pointer.text)
    assert discussion[start - 1] == "\n" and discussion[start - 2] != "\n"
    for label, name in (
        ("supp:x1-x2", "the mean-field and drift analyses"),
        ("supp:x5", "the misspecification analysis"),
        ("supp:x3-x7", "the fitting, rejection, coverage and feature analyses"),
        ("supp:x1b-release", "the twin and expanded-feature boundaries"),
    ):
        assert rf"\hyperref[{label}]{{{name}}}" in pointer.text
    assert (
        r"\phantomsection\label{supp:x1b-release}"
        in (documents["sections/supplement-exploratory-x3-x7.tex"])
    )
    assert not EXPLORATORY_DETAIL.search(discussion)
    for kept in ("D-X6-DENOMINATORS", "D-X5-POST-UNAVAILABLE"):
        assert report.decisions[kept].text.split("\n")[0] in discussion
    assert documents["sections/supplement-exploratory-x3-x7.tex"].startswith(
        r"\subsection*{Exploratory analyses of fitting, rejection, coverage and "
        r"features}\label{supp:x3-x7}"
    )


def test_pointer_names_the_twin_paragraph_only_when_it_is_assembled() -> None:
    values = complete_values("passed-shp") | {
        "v4x.comparisons.count.x1b.available": "0",
        "v4x.comparisons.count.x1b.unavailable": "0",
    }
    report, documents = composed_documents("passed-shp", values)
    assert (
        report.decisions["E.twin-and-expanded-feature-boundaries"].state == "excluded"
    )
    pointer = report.decisions["D-EXPLORATORY-SUPPLEMENT"]
    assert pointer.state == "selected"
    assert "supp:x1b-release" not in pointer.text
    assert r"and X3, X4, X6 and X7 in \hyperref[supp:x3-x7]" in pointer.text
    assert (
        "supp:x1b-release"
        not in (documents["sections/supplement-exploratory-x3-x7.tex"])
    )


def test_without_the_exploratory_section_the_discussion_adds_no_pointer() -> None:
    report, documents = composed_documents("failed-G0")
    assert report.decisions["E.status-and-scope"].state == "excluded"
    assert report.decisions["D-EXPLORATORY-SUPPLEMENT"].state == "excluded"
    assert "supp:x3-x7" not in documents["sections/discussion.tex"]
    assert "sections/supplement-exploratory-x3-x7.tex" not in documents


def test_x3_and_x7_supplement_paragraphs_state_design_and_common_limits_once() -> None:
    report, documents = composed_documents("passed-shp")
    supplement = documents["sections/supplement-exploratory-x3-x7.tex"]
    design = report.decisions["E.x3-design"]
    assert design.state == report.decisions["E.x7-scope"].state == "selected"
    assert "lag-four and lag-five features only" in design.text
    assert "lags three to five" in design.text
    assert supplement.index(design.text) < supplement.index(
        report.decisions["E.x3-reduced-separation"].text
    )
    for phrase in (
        "conditional on the accepted fit",
        "conditional on fitting and training",
        "three-parameter matching",
        "estimation and regularization",
        "Bayes optimality",
        "isolate network dependence",
    ):
        assert supplement.count(phrase) == (
            0 if phrase == "conditional on fitting and training" else 1
        ), phrase


def b03_values(case: str = "passed-shp") -> dict[str, str]:
    values = complete_values(case)
    values |= {
        "v4.t1.n_not_attained": "9",
        "v4.t1.n_small": "0",
        "v4.t1.n_attained": "0",
    }
    # Without a B crossing no persistence reading can apply.
    values |= {f"v4.{pair}.n_persistence": "0" for pair in ("bd", "be", "bc")}
    return values


@pytest.mark.parametrize(
    ("case", "b03", "headline"),
    [
        ("passed-shp", False, "C-H-BD"),
        ("incomplete-tier2", False, "C-H-B"),
        ("invalid-main", False, "C-B02"),
        ("passed-shp", True, "C-D-AFTER-B03"),
        ("failed-G0", False, None),
    ],
)
def test_counts_stay_in_results_and_each_reading_appears_once(
    case: str, b03: bool, headline: str | None
) -> None:
    report, documents = composed_documents(case, b03_values() if b03 else None)
    if headline is not None:
        assert report.decisions[headline].state == "selected"
    persistence = report.decisions["D-BD-PERSISTENCE"].state == "selected"
    # T57e: only the Conclusion's B/D headline and persistence reading count.
    counted = {
        key
        for name in ("C-H-BD", "C-BD-PERSISTENCE")
        if report.decisions[name].state == "selected"
        for key in re.findall(r"\\resultnum\{([^{}]+)\}", report.decisions[name].text)
    }
    for name in ("sections/discussion.tex", "sections/conclusion.tex"):
        assembled, fixed = documents[name], (MANUSCRIPT / name).read_text()
        shown = set(re.findall(r"\\resultnum\{(v4\.b[dec]\.[^{}]+)\}", assembled))
        assert shown == (counted if name.endswith("conclusion.tex") else set())
        # The fixed DS02 text states the rule; the selected blocks apply it once.
        reading = "non-Gaussian persistence"
        assert assembled.count(reading) - fixed.count(reading) == persistence
        if headline == "C-H-BD":
            assert "reported in Results" not in assembled
    assert documents["sections/conclusion.tex"].count("comparison of rival") <= 1


B_ONLY_COUNTS = (
    "v4.t1.n_small",
    "v4.t1.n_large",
    "v4.t1.n_not_attained",
    "v4.t1.n_censored",
    "v4.t1.n_interval_lower_finite",
    "v4.t1.upper_a090_min",
    "v4.t1.upper_a090_max",
)


@pytest.mark.parametrize(
    ("case", "variant", "headline", "home"),
    [
        ("incomplete-tier2", None, "D-H-B", "P5-a.1"),
        ("invalid-main", None, "D-H-B", "P5-a.1"),
        ("passed-shp", "empty-pairs", "D-H-B", "P5-a.1"),
        ("passed-shp", "b03", "D-B03", "B03"),
        ("incomplete-tier2", "b03", "D-B03", "B03"),
    ],
)
def test_b_only_headline_counts_stay_in_results(
    case: str, variant: str | None, headline: str, home: str
) -> None:
    values = b03_values(case) if variant == "b03" else complete_values(case)
    if variant == "empty-pairs":
        values |= {"v4.bd.n_eligible": "0", "v4.bd.n_persistence": "0"}
    report, documents = composed_documents(case, values)
    assert report.decisions[headline].state == report.decisions[home].state
    assert report.decisions[headline].state == "selected"
    shown = [
        i for i in B_ONLY_COUNTS if rf"\resultnum{{{i}}}" in report.decisions[home].text
    ]
    assert shown
    for key in shown:
        assert rf"\resultnum{{{key}}}" in documents["sections/results.tex"]
    for name in ("sections/discussion.tex", "sections/conclusion.tex"):
        expected = (
            report.decisions["C-H-B"].text if name.endswith("conclusion.tex") else ""
        )
        assert {
            i for i in B_ONLY_COUNTS if rf"\resultnum{{{i}}}" in documents[name]
        } == {i for i in B_ONLY_COUNTS if rf"\resultnum{{{i}}}" in expected}
        assert "These counts" not in documents[name]
    assert "Results" in report.decisions[headline].text
    if case == "invalid-main":
        assert report.decisions["C-B02"].state == "selected"
        assert r"\resultnum{v4.t1.n_not_valid}" in documents["sections/conclusion.tex"]


def test_evaluation_clause_joins_the_exposure_paragraph_of_the_conclusion() -> None:
    _, documents = composed_documents("passed-shp")
    conclusion = documents["sections/conclusion.tex"]
    assert re.search(r"[^\n] Evaluation used new seeds\.\n\n", conclusion)
    assert "\n\nEvaluation used new seeds." not in conclusion
    _, documents = composed_documents("failed-G0")
    assert re.search(
        r"[^\n] Every stage must pass before any evaluation on reserved seeds\.\n\n",
        documents["sections/conclusion.tex"],
    )


def test_t57c_wording_fixes_reach_the_assembled_sections() -> None:
    _, documents = composed_documents("passed-shp")
    results = documents["sections/results.tex"]
    assert results.startswith(
        "This section reports the hash-bound gate records, the released curves "
        "and the complete unit inventory, as fixed by the release receipt."
    )
    assert "records these four statuses in Portuguese" in results
    assert r"complete and valid (\texttt{completo" not in results
    assert "did not reach the target against D on this grid" in results
    discussion = documents["sections/discussion.tex"]
    assert "The raw anchor, STARTS sensitivity" not in discussion
    assert "planned comparison with the released B curve is not reported" in discussion
    assert "remains to be declared" not in documents["sections/conclusion.tex"]


def test_x4_supplement_states_the_declared_x4b_domain() -> None:
    report = plan(
        complete_values("passed-shp"),
        {},
        manuscript=MANUSCRIPT,
        facts=owner_facts("passed-shp"),
    )
    text = report.decisions["E.x4-conditional-rejection-references"].text
    assert r"declared only at the three response signal shares of Table" in text
    assert "values outside this domain are not missing in-domain estimates" in text


RESULTS_HEADINGS = (
    "Validation gate",
    "Release and unit inventory",
    "Boundaries against B",
    "Other null families",
    "Controls and sensitivities",
    "Empirical reliability anchor",
    "Diagnostics and descriptive scope",
)
SENTENCE_BREAK = re.compile(r"(?<=[.?!])\s+(?=[A-Z\\$])")


def short_paragraph_pairs(text: str) -> list[tuple[str, str]]:
    """Adjacent paragraphs of at most two sentences; a heading ends the run."""
    pairs, previous = [], None
    for block in re.split(r"\n\s*\n|\\par\b", text):
        visible = " ".join(re.sub(r"(?m)(?<!\\)%.*$", "", block).split())
        if not visible or visible.startswith((r"\input", r"\begin", r"\end")):
            continue
        heading = re.match(r"\\subsection\*?\{[^{}]*\}(?:\\label\{[^{}]*\})?", visible)
        if heading:
            previous = None
            visible = visible[heading.end() :].strip()
            if not visible:
                continue
        short = len(SENTENCE_BREAK.split(visible)) <= 2
        if short and previous is not None:
            pairs.append((previous[:60], visible[:60]))
        previous = visible if short else None
    return pairs


@pytest.mark.parametrize(
    "variant",
    [*CASES, "passed-shp+b03", "incomplete-tier2+b03", "passed-shp+empty-pairs"],
)
def test_composed_sections_have_no_run_of_short_paragraphs(variant: str) -> None:
    case, _, kind = variant.partition("+")
    values = None
    if kind == "b03":
        values = b03_values(case)
    elif kind == "empty-pairs":
        values = complete_values(case)
        values |= {"v4.bd.n_eligible": "0", "v4.bd.n_persistence": "0"}
    _, documents = composed_documents(case, values)
    for name in ("results", "discussion", "conclusion"):
        assert short_paragraph_pairs(documents[f"sections/{name}.tex"]) == [], name


@pytest.mark.parametrize("case", list(CASES))
def test_results_headings_mark_the_paragraph_groups_only_after_a_passed_gate(
    case: str,
) -> None:
    report, documents = composed_documents(case)
    results = documents["sections/results.tex"]
    headings = re.findall(r"\\subsection\{([^{}]*)\}", results)
    if report.decisions["B1a"].state != "selected":
        assert headings == []
        return
    anchor = any(
        report.decisions[name].state == "selected" and report.decisions[name].text
        for name in ("P8.1", "B13", "B14", "B15")
    )
    assert (report.decisions["P8.heading"].state == "selected") == anchor
    assert headings == [
        h for h in RESULTS_HEADINGS if anchor or h != "Empirical reliability anchor"
    ]
    assert results.startswith("This section reports")
    assert results.index(r"\subsection{Validation gate}") < results.index(
        report.decisions["B1a"].text
    )


def test_conclusion_answers_the_question_with_the_paired_regions() -> None:
    report, documents = composed_documents("passed-shp")
    paragraphs = documents["sections/conclusion.tex"].split("\n\n")
    headline = report.decisions["C-H-BD"].text
    assert headline in next(p for p in paragraphs if "The amended design asks" in p)
    for family in ("B", "D"):
        for region in ("n_small", "n_large", "n_not_attained", "n_censored"):
            assert rf"\resultnum{{v4.bd.{family}.{region}}}" in headline
    permission = report.decisions["C-PERMISSION"].text
    persistence = report.decisions["C-BD-PERSISTENCE"].text
    second = next(p for p in paragraphs if permission in p)
    assert second.index(permission) < second.index(persistence)
    assert r"\resultnum{v4.bd.n_persistence}" in persistence


@pytest.mark.parametrize("count", ["1", "2"])
def test_anchor_status_sentence_names_its_table_without_an_implicit_comparator(
    count: str,
) -> None:
    values = complete_values("passed-shp") | {"v4.shp.n_r_in_interval": count}
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    sentence = report.decisions["P8.3"]
    assert sentence.state == "selected"
    assert "the same" not in sentence.text
    assert sentence.text.endswith(r"Table~\ref{tab:v4-T1}.")
    assert (
        "The execution status and boundary region of the B unit at this value are "
        "reported in"
        if count == "1"
        else "The B units at these values share one execution status and boundary "
        "region, reported in"
    ) in sentence.text


def test_t57e_wording_reaches_the_assembled_sections() -> None:
    report, documents = composed_documents("passed-shp")
    results = documents["sections/results.tex"]
    assert (
        "estimates stayed sealed throughout the confirmatory run and are not "
        "analysed here"
    ) in results
    assert "ordinal with a response signal share of one" in results
    texts = shell_texts(manuscript=MANUSCRIPT)
    assert not any("ordinal at unit" in text for text in texts.values())
    abstract = documents["main.tex"]
    assert (
        "the trait-plus-autoregressive band exceeded the target and the "
        "state-dependent band stayed below it"
    ) in abstract
    assert "was separated" not in abstract
    discussion = documents["sections/discussion.tex"]
    fixed = (MANUSCRIPT / "sections/discussion.tex").read_text()
    phrase = "specific evidence of interaction"
    # T57g: each applied frozen reading keeps the caveat, as the rule states it.
    readings = sum(
        report.decisions[f"D-{pair}-PERSISTENCE"].state == "selected"
        for pair in ("BD", "BE", "BC")
    )
    assert readings == 3
    assert discussion.count(phrase) == fixed.count(phrase) + readings
    for name in ("D-H-BD", "D-PERMISSION", "D-BD-PERSISTENCE"):
        assert "reported in Results" not in report.decisions[name].text


AGREEMENT = {
    "E.x3-execution-errors": (
        "The affected cell provides",
        "The affected cells provide",
    ),
    "E.x7-invalid-comparison": ("Its status", "Their status"),
    "C-T2-INCOMPLETE": (
        "This absence is an operational limit and provides",
        "These absences are operational limits and provide",
    ),
}


@pytest.mark.parametrize("count", ["1", "2"])
def test_count_dependent_subjects_agree_with_their_counts(count: str) -> None:
    texts = shell_texts(manuscript=MANUSCRIPT)
    for name, forms in AGREEMENT.items():
        values = dict.fromkeys(
            re.findall(r"\\resultnum\{([^{}]+)\}", texts[name]), count
        )
        assert forms[count != "1"] in bind(texts[name], values), name


def test_exploratory_supplement_follows_x1_x2_and_x5_under_its_headings() -> None:
    report, documents = composed_documents("passed-shp")
    main = documents["main.tex"]
    assert (
        main.index(r"\input{sections/supplement-exploratory-x1-x2}")
        < main.index(r"\input{sections/supplement-exploratory-x3-x7}")
        < main.index(r"\input{generated/exploratory-x1b-boundaries}")
    )
    supplement = documents["sections/supplement-exploratory-x3-x7.tex"]
    heading = r"\subsection*{Exploratory readings beside the released boundary}"
    assert report.decisions["E.post-release-heading"].state == "selected"
    assert supplement.count(heading) == 1
    assert (
        supplement.index(report.decisions["E.status-and-scope"].text)
        < supplement.index(heading)
        < supplement.index(report.decisions["E.available-local-readings"].text)
    )
    values = complete_values("passed-shp")
    values |= {key: "0" for key in values if key.startswith("v4x.comparisons.count.")}
    report, documents = composed_documents("passed-shp", values)
    assert report.decisions["E.post-release-heading"].state == "excluded"
    assert heading not in documents["sections/supplement-exploratory-x3-x7.tex"]


@pytest.mark.parametrize("case", CASES)
def test_supplement_follows_references_with_separate_float_numbers(case: str) -> None:
    _, documents = composed_documents(case)
    main = documents["main.tex"]
    references = main.index(r"\bibliography{references}")
    reset = main.index(r"\setcounter{table}{0}")
    assert (
        main.index(r"\section*{Statements and Declarations}")
        < main.index(r"\begin{appendices}")
        < main.index(r"\end{appendices}")
        < references
        < reset
        < main.index(r"\checksupplementcontent{sections/supplement}")
        < main.index(r"\section*{Supplementary Material}")
        < main.index(r"\input{sections/supplement}")
    )
    assert r"\clearpage" in main[references:reset]
    assert r"\setcounter{figure}{0}" in main[reset:]
    for kind in ("table", "figure"):
        assert rf"\renewcommand{{\the{kind}}}{{S\arabic{{{kind}}}}}" in main
        assert (
            rf"\ifdefined\theH{kind}"
            + "\n"
            + rf"  \renewcommand{{\theH{kind}}}{{supp.\arabic{{{kind}}}}}"
            + "\n"
            + r"\fi"
        ) in main
    assert main.count(r"\input{sections/supplement-exploratory-x1-x2}") == 1
    assert main.rstrip().endswith("\\clearpage\n\n\\end{document}")


def test_long_gate_paragraphs_break_at_stage_boundaries() -> None:
    report, documents = composed_documents("passed-shp")
    gate = report.decisions["B1a"].text
    assert gate.count("\\par ") == 2
    assert "\n\\par In G1b, joint coverage" in gate
    assert "\n\\par In G2, across the" in gate
    results = documents["sections/results.tex"]
    assert all(
        len(SENTENCE_BREAK.split(" ".join(part.split()))) <= 10
        for part in gate.split("\\par ")
    )
    assert gate in results
    texts = shell_texts(manuscript=MANUSCRIPT)
    assert (
        "\n\\par The bootstrap interval for the dispersion ratio lay above"
        in (texts["B1b-G2"])
    )


@pytest.mark.parametrize(
    ("first_max", "b06", "selected"),
    [
        ("0.03", False, "P5-b.single"),
        ("0.1", False, "P5-b.range"),
        ("0.03", True, "P5-b.single"),
        ("0.1", True, "P5-b.range"),
    ],
)
def test_attained_boundary_strengths_read_as_one_value_or_a_range(
    first_max: str, b06: bool, selected: str
) -> None:
    values = complete_values("passed-shp") | {"v4.t1.first_max": first_max}
    if b06:
        values["v4.t1.n_first_ne_sustained"] = "1"
    report, documents = composed_documents("passed-shp", values)
    other = ({"P5-b.single", "P5-b.range"} - {selected}).pop()
    assert report.decisions[selected].state == "selected"
    assert report.decisions[other].state == "excluded"
    assert report.decisions["B06"].state == ("selected" if b06 else "excluded")
    results = documents["sections/results.tex"]
    lead = (
        "Every attained first boundary was at $a="
        if selected == "P5-b.single"
        else "The attained first boundaries ranged from $a="
    )
    assert lead in results
    assert ("the sustained boundary equalled it" in results) is not b06


def test_single_strength_reading_refuses_a_missing_range_bound() -> None:
    values = complete_values("passed-shp")
    del values["v4.t1.first_max"]
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    assert report.decisions["P5-b.single"].state == "refused"
    assert (
        "Missing catalog ID: v4.t1.first_max" in report.decisions["P5-b.single"].reason
    )


def test_paired_counts_say_censored_or_indeterminate() -> None:
    texts = shell_texts(manuscript=MANUSCRIPT)
    assert not any("censored/indeterminate" in text for text in texts.values())
    assert texts["P6.counts"].count("censored or indeterminate") == 2


def test_paragraph_pairs_read_the_prose_that_follows_a_heading() -> None:
    text = "\\subsection{Heading}\nFirst short paragraph.\n\nSecond short paragraph."
    assert short_paragraph_pairs(text) == [
        ("First short paragraph.", "Second short paragraph.")
    ]
    assert short_paragraph_pairs("One.\n\n\\subsection{Next}\nTwo.") == []


JOIN_SHAPES = {
    "no paragraph": "",
    "comment line": "First.\n\n% provenance\n\n",
    "only a comment": "% only a comment\n",
    "glued comment": "First.% RS\n\n",
    "par": "First.\\par\n\n",
    "par line": "First.\n\\par\n\n",
}
JOIN_ERRORS = {
    "no paragraph": "no paragraph before the join point",
    "comment line": "ends in a comment line",
    "only a comment": "ends in a comment line",
    "glued comment": "ends in a % comment",
    "spaced comment": "ends in a % comment",
    "par": "par before the join point",
    "par line": "par before the join point",
    "inline par": "par before the join point",
}


def join_sources(site: str, body: str) -> tuple[dict[str, Decision], dict[str, str]]:
    decisions = [mechanics_decision("design", " ".join(["word"] * 150), "abstract", 0)]
    discussion = "% DS10\nFixed.\n\n% DS11\nX5.\n"
    conclusion = "Question.\n\n[Insert headline.]\n\n[State whether boundary.]\n\n"
    tail = "[Insert implication.]"
    if site == "DS10":
        decisions.append(mechanics_decision("D", "Joined sentence.", "DS10-join", 1))
        discussion = "% DS10\n" + body + "% DS11\nX5.\n"
    elif site == "C1":
        decisions.append(mechanics_decision("C1", "Joined sentence.", "C1", 1))
        conclusion = body + conclusion.removeprefix("Question.\n\n")
    else:
        decisions.append(mechanics_decision("E", "Joined sentence.", "CN01-join", 1))
        conclusion += body.replace("First.", "Exposure.")
    sources = {
        "main.tex": r"\abstract{Old.}",
        "sections/discussion.tex": discussion,
        "sections/conclusion.tex": conclusion + tail,
    }
    return {d.id: d for d in decisions}, sources


@pytest.mark.parametrize(
    ("site", "shape", "body"),
    [
        *[("DS10", shape, body) for shape, body in JOIN_SHAPES.items()],
        *[("C1", shape, body) for shape, body in JOIN_SHAPES.items()],
        ("C1", "inline par", "Question.\\par "),
        *[
            ("CN01", shape, body)
            for shape, body in JOIN_SHAPES.items()
            if shape != "no paragraph"
        ],
        ("CN01", "spaced comment", "First. % RS\n\n"),
    ],
)
def test_explicit_joins_refuse_a_boundary_they_cannot_continue(
    site: str, shape: str, body: str
) -> None:
    decisions, sources = join_sources(site, body)
    with pytest.raises(ValueError, match=f"{site} join: .*{JOIN_ERRORS[shape]}"):
        compose_documents(AssemblyPlan(decisions, "a", "b", {}), sources)


def test_explicit_joins_keep_the_real_paragraphs_and_escaped_text() -> None:
    _, documents = composed_documents("passed-shp")
    assert (
        "labels unchanged. % DS10 RC29\nThe exploratory denominators"
        in (documents["sections/discussion.tex"])
    )
    conclusion = documents["sections/conclusion.tex"]
    assert (
        "matched persistence laws.\nOn the \\resultnum{v4.bd.n_eligible}{9} response"
    ) in conclusion
    assert "calibration exposure. Evaluation used new seeds.\n\n" in conclusion
    for site in ("DS10", "C1", "CN01"):
        decisions, sources = join_sources(site, "First. \\\\par\n\n")
        documents, _ = compose_documents(AssemblyPlan(decisions, "a", "b", {}), sources)
        joined = "\n".join(documents.values())
        assert "First. \\\\par" in joined or "Exposure. \\\\par" in joined
        assert "Joined sentence." in joined


@pytest.mark.parametrize(
    ("first_min", "first_max", "selected"),
    [("0.03", "0.030", "P5-b.single"), ("0.03", "0.1", "P5-b.range")],
)
def test_one_strength_is_read_numerically(
    first_min: str, first_max: str, selected: str
) -> None:
    values = complete_values("passed-shp")
    values |= {"v4.t1.first_min": first_min, "v4.t1.first_max": first_max}
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    assert report.decisions[selected].state == "selected"
    values["v4.t1.first_max"] = "n/a"
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    assert report.decisions["P5-b.single"].state == "refused"
    assert (
        "Non-numeric catalog ID: v4.t1.first_max"
        in report.decisions["P5-b.single"].reason
    )


@pytest.mark.parametrize(
    ("count", "lead"), [("1", "The attained"), ("9", "Every attained")]
)
def test_one_strength_sentence_agrees_with_the_attained_count(
    count: str, lead: str
) -> None:
    values = complete_values("passed-shp") | {"v4.t1.n_attained": count}
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    text = report.decisions["P5-b.single"].text
    assert text.startswith(lead + " first boundary was at $a=")
    assert text.count("first boundary was at") == 1


def test_t57g_wording_reaches_the_assembled_sections() -> None:
    report, documents = composed_documents("passed-shp")
    assert "where the comparisons against B and D were both gap-free" in (
        report.decisions["C-H-BD"].text
    )
    assert "The readings above concern the fixed" in documents["sections/results.tex"]
    texts = shell_texts(manuscript=MANUSCRIPT)
    assert r"The upper-band range that Results report at $a=" in texts["D-B03"]
    assert "a sustained boundary that lies below the last gap" in texts["B06"]
    assert not any("sustained crossing" in text for text in texts.values())
    for name in ("D-BD-PERSISTENCE", "D-BE-PERSISTENCE", "D-BC-PERSISTENCE"):
        assert (
            texts[name].rstrip().endswith(", without specific evidence of interaction.")
        ), name


def test_x7_has_one_display_and_roadmap_does_not_move_it_before_validation() -> None:
    report = plan(
        complete_values("passed-shp"),
        {},
        manuscript=MANUSCRIPT,
        facts=owner_facts("passed-shp"),
    )
    sources = {
        name: (MANUSCRIPT / name).read_text()
        for name in (
            "main.tex",
            "sections/discussion.tex",
            "sections/conclusion.tex",
            "sections/supplement.tex",
        )
    }
    documents, _ = compose_documents(report, sources)
    assert (
        sum(
            text.count(r"\input{generated/exploratory-x7-boundaries}")
            for text in documents.values()
        )
        == 1
    )
    results = documents["sections/results.tex"]
    assert results.index(report.decisions["B1a"].text) < results.index(
        r"\input{generated/primary-boundary-figure}"
    )
    assert "Figures~\\ref{fig:v4-F1}" in results


def oracle_values(name: str) -> dict[str, str]:
    row = CASES[name]
    base = cast(dict[str, str], ORACLE_DATA["base_values"])
    changes = cast(dict[str, str], row["value_changes"])
    return presentation_values(
        {k: v for k, v in base.items() if k not in row["removed_ids"]} | changes
    )


def complete_values(name: str) -> dict[str, str]:
    verdicts = json.loads((ORACLES.parent / "verdicts.json").read_text())
    values = (
        oracle_values(name)
        | cast(dict[str, str], verdicts["cases"][name]["values"])
        | cast(dict[str, str], CURRENT_ORACLE_DATA["catalog_additions"][name]["values"])
    )
    return presentation_values(values)


def presentation_values(values: dict[str, str]) -> dict[str, str]:
    values = values | {
        "v4.protocol.units.t6": "9",
        "v4x.x4.summary.normal_theory_in_auc_range.range.i000": "0.55",
        "v4x.x4.summary.normal_theory_in_auc_range.range.i001": "0.95",
    }
    for key in ("completed", "exceeds_floor_count"):
        ident = "v4.gate.G1b." + key
        if ident in values:
            values[ident + "_prose"] = f"{int(values[ident]):,}"
    for key in (
        "x3.sizes.matching",
        "x3.sizes.retry_matching",
        "x4.sizes.check",
        "x6.x6a.recorded",
        "x6.x6a.units",
        "x6.sizes.population_pairs",
    ):
        ident = "v4x." + key
        if ident in values:
            values[ident + "_prose"] = f"{int(values[ident]):,}"
    for index, label in enumerate(("lower", "upper")):
        ident = f"v4x.x6.x6a.band.vs_d1.primary.wilson95.i{index:03d}"
        if ident in values and values[ident] != "unavailable":
            values[ident.rsplit(".", 1)[0] + ".prose_" + label] = (
                f"{float(values[ident]):.3f}"
            )
    return values


def owner_facts(name: str) -> dict[str, Any]:
    dataset = "g2c-failure" if "comparison" in name else "release-day"
    return load_facts(ORACLES.parent / dataset / name / "assembly-facts.json")


def empty_facts_file(path: Path) -> str:
    path.write_text(
        json.dumps({"schema": FACTS_SCHEMA, "synthetic": True, "facts": {}})
    )
    return str(path)


def test_catalog_cannot_certify_gate_and_refusal_leaves_copy_absent(
    tmp_path: Path,
) -> None:
    release = parse_release(build_release(tmp_path / "synthetic", {}, draws=2))
    values = result_values(Loaded(release, None, None, None, None, None))
    report = plan(values, {}, manuscript=MANUSCRIPT)
    assert report.decisions["B1a"].state == "refused"
    assert "verdict" in report.decisions["B1a"].reason
    assert report.decisions["D-X6-ABSENT"].state == "selected"
    destination = tmp_path / "assembled"
    with pytest.raises(AssemblyRefusedError, match="B1a"):
        assemble(values, {}, manuscript=MANUSCRIPT, output=destination)
    assert not destination.exists()


@pytest.mark.parametrize("case", list(CASES))
def test_manual_rehearsals_select_the_same_exploratory_paragraphs(case: str) -> None:
    report = plan(
        complete_values(case), {}, manuscript=MANUSCRIPT, facts=owner_facts(case)
    )
    selected = [
        title
        for d in report.decisions.values()
        if d.id.startswith("E.") and d.state == "selected"
        for title in re.findall(r"\\paragraph\{([^}]+)\}", d.text)
    ]
    expected = list(CASES[case]["exploratory_titles"])
    # T57c adds the X3 design and X7 scope paragraphs to the historical oracle.
    values = complete_values(case)
    if expected and "v4x.x3.recorded" in values:
        expected.insert(
            expected.index("Status and scope.") + 1, "X3: design and common limits."
        )
    if expected and "v4x.x7.count.far" in values:
        expected.insert(expected.index("X6: matching diagnostics.") + 1, "X7: scope.")
    assert selected == expected


@pytest.mark.parametrize("case", list(CASES))
def test_manual_gate_choices_are_refused_without_inventing_verdicts(case: str) -> None:
    report = plan(oracle_values(case), {}, manuscript=MANUSCRIPT)
    expected = (
        "B1b-G2c"
        if "comparison" in case
        else ("B1b-G0" if case == "failed-G0" else "B1a")
    )
    assert report.decisions[expected].state == "refused"
    assert "verdict" in report.decisions[expected].reason
    assert report.decisions["D-X5"].state == "selected"
    assert report.decisions["C-X5"].state == "selected"


@pytest.mark.parametrize(
    "case,branch",
    [
        ("passed-shp", "ADEQUATE"),
        ("unavailable", "ABSENT"),
        ("x6-no-reading", "NO-READING"),
        ("x6-subnominal", "SUBNOMINAL"),
        ("x6-failure", "FAILURE"),
        ("x6-inconclusive", "INCONCLUSIVE"),
    ],
)
def test_x6_uses_effective_primary_reading_from_the_manual_catalog(
    case: str, branch: str
) -> None:
    report = plan(oracle_values(case), {}, manuscript=MANUSCRIPT)
    options = {
        "FAILURE",
        "SUBNOMINAL",
        "INCONCLUSIVE",
        "NO-READING",
        "ABSENT",
        "ADEQUATE",
    }
    assert [
        label
        for label in sorted(options)
        if report.decisions["D-X6-" + label].state == "selected"
    ] == [branch]
    assert not any(
        report.decisions["D-X6-" + label].state == "refused" for label in options
    )


def test_synthetic_invalid_curve_cannot_promote_a_cross_mechanism_clause(
    tmp_path: Path,
) -> None:
    key = unit_keys(tier=1, family="B")[0.5]
    release = parse_release(
        build_release(tmp_path / "synthetic", {key: UnitPlan((0.8,) * 9)}, draws=2)
    )
    values = result_values(Loaded(release, None, None, None, None, None))
    assert values["v4.t1.n_invalid_gate"] == "1"
    report = plan(values, {}, manuscript=MANUSCRIPT)
    assert report.decisions["D-H-BD"].state == "excluded"
    assert report.decisions["B10"].state == "excluded"
    assert report.decisions["B02.gate"].state == "refused"


def test_missing_count_is_refused_and_never_used_as_zero() -> None:
    values = oracle_values("passed-shp")
    del values["v4x.x3.count.supports-objection"]
    report = plan(values, {}, manuscript=MANUSCRIPT)
    decision = report.decisions["E.x3-reduced-separation"]
    assert decision.state == "refused"
    assert "Missing catalog ID" in decision.reason


def test_other_truths_and_nominal_reading_do_not_select_x6_consequence() -> None:
    values = oracle_values("x6-inconclusive")
    values["v4x.x6.x6a.band.vs_pop.primary.reading"] = "failure"
    values["v4x.x6.x6b.count.failure"] = "100"
    values["v4x.x6.x6a.band.vs_d1.primary.nominal_reading"] = "failure"
    report = plan(values, {}, manuscript=MANUSCRIPT)
    assert report.decisions["D-X6-INCONCLUSIVE"].state == "selected"
    assert report.decisions["C-X6-UNDERCOVERAGE"].state == "excluded"


def test_optional_eligibility_requires_its_own_positive_evidence() -> None:
    report = plan(oracle_values("invalid-main"), {}, manuscript=MANUSCRIPT)
    assert report.decisions["B05"].state == "refused"
    assert report.decisions["B11"].state == "refused"
    assert report.decisions["A.B05"].state == "excluded"
    assert report.decisions["A.B11"].state == "excluded"
    absent = plan(oracle_values("unavailable"), {}, manuscript=MANUSCRIPT)
    assert absent.decisions["A.X6"].state == "excluded"
    failure = plan(oracle_values("x6-failure"), {}, manuscript=MANUSCRIPT)
    assert failure.decisions["A.X6"].state == "selected"


@pytest.mark.parametrize(
    "case,optional_ids,words",
    [
        ("passed-shp", ("A.B11",), 222),
        ("invalid-main", ("A.B05", "A.B11"), 200),
        ("incomplete-tier2", ("A.B11",), 180),
        ("unavailable", ("A.B11",), 222),
        ("x6-no-reading", ("A.B11",), 222),
        ("x6-subnominal", ("A.B11",), 233),
        ("x6-failure", ("A.B11",), 233),
        ("x6-inconclusive", ("A.B11",), 222),
    ],
)
def test_zero_count_optional_clauses_are_excluded_from_the_assembled_abstract(
    case: str, optional_ids: tuple[str, ...], words: int
) -> None:
    report = plan(
        complete_values(case), {}, manuscript=MANUSCRIPT, facts=owner_facts(case)
    )
    assert not report.refused
    for name in optional_ids:
        assert report.decisions[name].state == "excluded"
    assert visible_word_count(CURRENT_ORACLES[case]) == words


def test_unknown_x6_machine_label_is_refused() -> None:
    values = oracle_values("x6-failure")
    values[READING] = "new-label"
    report = plan(values, {}, manuscript=MANUSCRIPT)
    assert any("X6" in d.id and "Unknown" in d.reason for d in report.refused)


def test_first_fit_skips_a_long_clause_then_accepts_a_later_short_one() -> None:
    baseline = " ".join(["word"] * 230)
    mandatory = [baseline, "The mandatory X6 consequence remains.", "Last limitation."]
    optional = {"A.B04": "Short clause.", "A.B09.1": " ".join(["long"] * 30)}
    result = first_fit(mandatory, optional)
    assert [(s.id, s.included) for s in result.steps] == [
        ("A.B09.1", False),
        ("A.B04", True),
    ]
    assert "mandatory X6" in result.text
    assert result.text.endswith("Short clause. Last limitation.")
    assert result.words == 239


def test_abstract_positive_counts_and_new_seeds_after_all_results() -> None:
    values = complete_values("passed-shp") | {
        "v4.t1.n_interval_wide_finite": "1",
        "v4.t1.n_first_low": "0",
        "v4.t1.n_first_zero": "1",
        "v4.t1.n_first_ne_sustained": "0",
        "v4.t1.n_first_gap": "0",
        "v4.t1.n_sustained_gap": "1",
    }
    facts = owner_facts("passed-shp")
    facts["facts"]["tier2.boundaries_differ"]["value"] = True
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert not report.refused
    for name in ("A.B04", "A.B05", "A.B06", "A.B08", "A.B11"):
        assert report.decisions[name].state == "excluded"
    assert report.decisions["B04"].state == "selected"
    assert report.decisions["B06"].state == "selected"
    sources = {
        name: (MANUSCRIPT / name).read_text()
        for name in (
            "main.tex",
            "sections/discussion.tex",
            "sections/conclusion.tex",
            "sections/supplement.tex",
        )
    }
    _, budget = compose_documents(report, sources)
    assert any(step.id == "A.B09.1" and step.included for step in budget.steps)
    assert budget.text.index(report.decisions["A.B09.1"].text) < budget.text.index(
        report.decisions["A.new-seeds"].text
    )
    assert budget.text.endswith(
        report.decisions["A.new-seeds"].text
        + " "
        + report.decisions["A.limitation"].text
    )


def test_values_output_is_restricted_and_accepted_by_paper_checker(
    tmp_path: Path,
) -> None:
    values = complete_values("passed-shp")
    for table in (MANUSCRIPT / "generated").glob("*.tex"):
        source = table.read_text()
        for key, shown in re.findall(r"\\resultnum\{([^{}]+)\}\{([^{}]+)\}", source):
            values.setdefault(key, shown)
    values["unused.synthetic"] = "123"
    output = tmp_path / "assembled"
    path = tmp_path / "catalog.json"
    catalog = {
        "schema": "ic-study.v4-merged-result-values.v1",
        "synthetic": True,
        "values": values,
        "sources": {"unused.synthetic": {"record": "not-followed"}},
        "components": [
            {
                "schema": "ic-study.v4-result-values.v1",
                "report_manifest_sha256": "a" * 64,
            }
        ],
    }
    path.write_text(json.dumps(catalog))
    facts = tmp_path / "facts.json"
    facts.write_text(json.dumps(owner_facts("passed-shp")))
    destination = output / "assembled-values.json"
    assert (
        main(
            [
                "--confirmatory-values",
                str(path),
                "--assembly-facts",
                str(facts),
                "--manuscript",
                str(MANUSCRIPT),
                "--output",
                str(output),
                "--values",
                str(destination),
            ]
        )
        == 0
    )
    record = json.loads(destination.read_text())
    assert record["synthetic"] is True
    assert "unused.synthetic" not in record["values"]
    assert record["sources"] == {}
    assert record["components"][0]["components"] == catalog["components"]
    receipt = json.loads((output / "assembly-record.json").read_text())
    assert (
        receipt["values_output"]["sha256"]
        == hashlib.sha256(destination.read_bytes()).hexdigest()
    )
    spec = importlib.util.spec_from_file_location(
        "assembly_values_checker", MANUSCRIPT / "pipeline/paper_check.py"
    )
    assert spec and spec.loader
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    assert (
        checker.result_consistency(
            output, checker.tex_sources(output), destination, False
        )
        == []
    )


@pytest.mark.parametrize("mutation", ["missing", "mismatch"])
def test_values_refuse_missing_or_inconsistent_cited_binding(
    tmp_path: Path, mutation: str
) -> None:
    (tmp_path / "main.tex").write_text("% \\resultnum{commented}{9}\n\\input{nested}\n")
    (tmp_path / "nested.tex").write_text(r"\resultnum{visible}{3}")
    report = plan(
        complete_values("passed-shp"),
        {},
        manuscript=MANUSCRIPT,
        facts=owner_facts("passed-shp"),
    )
    with pytest.raises(ValueError, match=r"nested.tex:1.*visible"):
        assembled_values(
            tmp_path, {} if mutation == "missing" else {"visible": "4"}, report
        )
    assert assembled_values(tmp_path, {"visible": "3", "unused": "0"}, report)[
        "values"
    ] == {"visible": "3"}


def test_repin_maps_adjacent_edits_by_preserved_bindings_and_markers() -> None:
    module = repinner()
    before = (
        "Old \\resultnum{first}{[n]}. % RS01\nOld \\resultnum{second}{[n]}. % RS02\n"
    )
    after = before.replace("Old", "Revised")
    registry = {
        "sources": {
            "results": {
                "path": "shell.tex",
                "sha256": hashlib.sha256(before.encode()).hexdigest(),
            }
        },
        "rules": [
            {
                "id": "R",
                "source": "results",
                "line": 1,
                "end_line": 1,
                "condition": True,
                "operation": "append",
            }
        ],
    }
    with pytest.raises(ValueError, match="--accept-visible"):
        module.repin_registry(
            registry, {"results": before.encode()}, {"results": after.encode()}, set()
        )
    updated, receipt = module.repin_registry(
        registry, {"results": before.encode()}, {"results": after.encode()}, {"R"}
    )
    assert updated["rules"][0]["end_line"] == 1
    assert receipt["rules"][0]["explicit_acceptance"] is True
    with pytest.raises(ValueError, match="Ambiguous replacement"):
        module.LineMap(before, "\n".join(after.splitlines()[::-1])).span(1, 1)


def test_all_abstract_predicate_classes_fit_including_interval_only_differences() -> (
    None
):
    script = (
        STUDY
        / "publications/jcss-manuscript/pipeline/review/check_v4_abstract_budget.py"
    )
    spec = importlib.util.spec_from_file_location("assembly_budget_checker", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    proof = module.proof()
    assert proof["maximum_mandatory_words"] == 250
    assert [row["maximum"] for row in proof["fallbacks_in_order"]] == [
        263,
        261,
        257,
        250,
    ]
    assert any(
        {"A.B03", "A.D-after-B03", "A.B06", "A.X6"}.issubset(row["ids"])
        and "A.B10" not in row["ids"]
        for row in proof["compositions"]
    )


def test_values_failure_leaves_no_partial_copy_and_preserves_existing_output(
    tmp_path: Path,
) -> None:
    output = tmp_path / "assembled"
    values_path = tmp_path / "values.json"
    values_path.write_text("existing")
    with pytest.raises(ValueError, match="new file"):
        assemble(
            complete_values("passed-shp"),
            {},
            manuscript=MANUSCRIPT,
            output=output,
            facts=owner_facts("passed-shp"),
            values_output=values_path,
        )
    assert values_path.read_text() == "existing"
    assert not output.exists()
    values_path.unlink()
    with pytest.raises(ValueError, match="Missing cited catalog ID"):
        assemble(
            complete_values("passed-shp"),
            {},
            manuscript=MANUSCRIPT,
            output=output,
            facts=owner_facts("passed-shp"),
            values_output=values_path,
        )
    assert not output.exists() and not values_path.exists()


@pytest.mark.parametrize("case", list(CASES))
def test_visible_count_matches_the_real_paper_checker(case: str) -> None:
    spec = importlib.util.spec_from_file_location(
        "assembly_paper_check", MANUSCRIPT / "pipeline/paper_check.py"
    )
    assert spec is not None and spec.loader is not None
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    text = CASES[case]["abstract"]
    visible = checker.RESULT_MACRO.sub(lambda m: m[2], text)
    expected = checker.word_count(re.sub(r"\\[A-Za-z]+", "", visible))
    assert visible_word_count(text) == expected


@pytest.mark.parametrize(
    "case,ids,words",
    [
        ("passed-shp", ("design", "G", "H-BD", "B10", "new-seeds"), 222),
        ("failed-G0", ("design", "every-stage", "B1b-G0", "X"), 179),
        ("invalid-main", ("design", "G", "B02", "H-B", "P6-a", "new-seeds"), 200),
        ("incomplete-tier2", ("design", "G", "H-B", "P6-a", "new-seeds"), 180),
        ("unavailable", ("design", "G", "H-BD", "B10", "new-seeds"), 222),
        ("x6-no-reading", ("design", "G", "H-BD", "B10", "new-seeds"), 222),
        ("x6-subnominal", ("design", "G", "H-BD", "B10", "X6", "new-seeds"), 233),
        ("x6-failure", ("design", "G", "H-BD", "B10", "X6", "new-seeds"), 233),
        ("x6-inconclusive", ("design", "G", "H-BD", "B10", "new-seeds"), 222),
        ("i-comparison-failed", ("design", "every-stage", "B1b-G2c", "X"), 183),
        ("ii-comparison-no-ratio", ("design", "every-stage", "B1b-G2c", "X"), 183),
        ("iii-comparisons-absent", ("design", "every-stage", "B1b-G2c", "X"), 183),
    ],
)
def test_abstract_composition_rebases_the_manual_choices_on_t41d(
    case: str, ids: tuple[str, ...], words: int
) -> None:
    # The branch IDs above are the independent manual oracle. They are not a
    # production branch override: its missing gate evidence is tested separately.
    texts = shell_texts(manuscript=MANUSCRIPT)
    values = oracle_values(case)
    registry = json.loads(RULES.read_text())
    for row in registry["rules"]:
        if row["id"] in {"A." + name for name in ids} and row.get("fragments"):
            source = MANUSCRIPT / registry["sources"][row["source"]]["path"]
            texts[row["id"]] = _fragment_text(
                row,
                source.read_text().splitlines(),
                _Evaluator(values, registry["predicates"], {}),
                texts[row["id"]],
            )
    sentences = [bind(texts["A." + name], values) for name in (*ids, "limitation")]
    result = first_fit(sentences, {})
    assert result.words == words
    assert " ".join(result.text.split()) == " ".join(CURRENT_ORACLES[case].split())
    assert CURRENT_ORACLES[case] != CASES[case]["abstract"]


def test_rehearsal_notes_overcount_identifiers_but_manuscript_count_is_visible() -> (
    None
):
    expected = {
        "passed-shp": (228, 184),
        "invalid-main": (174, 159),
        "incomplete-tier2": (168, 153),
        "unavailable": (228, 184),
        "x6-no-reading": (228, 184),
        "x6-subnominal": (239, 195),
        "x6-failure": (239, 195),
        "x6-inconclusive": (228, 184),
    }
    for case, (old, visible) in expected.items():
        assert f"; {old} words" in CASES[case]["notes"]
        assert visible_word_count(CASES[case]["abstract"]) == visible


def test_manual_x5_removal_diverges_from_the_frozen_retention_actions() -> None:
    for case, row in CASES.items():
        preserved = (
            "all 72 cells finished" in row["discussion"]
            and "all 36 cells with estimates" in row["conclusion"]
        )
        assert preserved == ("comparison" in case)
        report = plan(oracle_values(case), {}, manuscript=MANUSCRIPT)
        assert report.decisions["D-X5"].operation == "retain"
        assert report.decisions["C-X5"].operation == "retain"


def test_copy_refusal_does_not_accept_an_invented_gate_pass_id() -> None:
    values = oracle_values("passed-shp") | {"v4.gate.G0.pass": "true"}
    assert plan(values, {}, manuscript=MANUSCRIPT).decisions["B1a"].state == "refused"


def test_cli_report_cannot_overwrite_an_input(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    catalog = tmp_path / "catalog.json"
    original = json.dumps({"schema": "ic-study.v4-result-values.v1", "values": {}})
    catalog.write_text(original)
    assert (
        main(
            [
                "--confirmatory-values",
                str(catalog),
                "--assembly-facts",
                empty_facts_file(tmp_path / "assembly-facts.json"),
                "--manuscript",
                str(MANUSCRIPT),
                "--report",
                str(catalog),
                "--audit-only",
            ]
        )
        == 2
    )
    assert "new file" in capsys.readouterr().out
    assert catalog.read_text() == original


def test_rule_registry_covers_every_shell_block_and_quote_with_a_locator() -> None:
    registry = json.loads(RULES.read_text())
    texts = shell_texts(manuscript=MANUSCRIPT)
    rows = registry["rules"]
    assert len(texts) == len(rows)
    for source_name, source in registry["sources"].items():
        path = MANUSCRIPT / source["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]
        lines = path.read_text().splitlines()
        covered = {
            number
            for r in rows
            if r["source"] == source_name
            for number in range(r["line"], r["end_line"] + 1)
        }
        for number, line in enumerate(lines, 1):
            if line.startswith(("% BEGIN ", "> ", r"\paragraph{")):
                assert number in covered, (source_name, number)
    assert [r["id"] for r in rows if r.get("optional")] == list(OPTIONAL_ORDER)
    assert all(
        texts[r["id"]] for r in rows if r["operation"] not in {"group", "retain"}
    )


def test_catalog_validation_conflicts_and_order_independence(tmp_path: Path) -> None:
    values = oracle_values("passed-shp")
    path = tmp_path / "values.json"
    path.write_text(
        json.dumps({"schema": "ic-study.v4-merged-result-values.v1", "values": values})
    )
    assert load_catalog(path) == values
    a = plan(values, {}, manuscript=MANUSCRIPT).as_dict()
    b = plan(dict(reversed(list(values.items()))), {}, manuscript=MANUSCRIPT).as_dict()
    assert a == b
    with pytest.raises(ValueError, match="Conflicting"):
        plan(values, {"v4.mechanisms.allowed": "0"}, manuscript=MANUSCRIPT)
    path.write_text('{"schema":"unknown","values":{}}')
    with pytest.raises(ValueError, match="exported"):
        load_catalog(path)
    path.write_text('{"schema":"ic-study.v4-result-values.v1","values":{"id":NaN}}')
    with pytest.raises(ValueError, match="strings"):
        load_catalog(path)


def test_shell_drift_requires_rule_review(tmp_path: Path) -> None:
    copy = tmp_path / "source"
    shutil.copytree(MANUSCRIPT / "pipeline/drafts", copy / "pipeline/drafts")
    shell = copy / "pipeline/drafts/2026-09-28/results-shells.tex"
    shell.write_text(shell.read_text() + "\n% changed\n")
    with pytest.raises(ValueError, match="review rules"):
        plan({}, {}, manuscript=copy)


def test_cli_emits_refusal_and_preserves_source_and_existing_destination(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    values = tmp_path / "catalog.json"
    values.write_text(
        json.dumps(
            {
                "schema": "ic-study.v4-result-values.v1",
                "values": oracle_values("passed-shp"),
            }
        )
    )
    destination = tmp_path / "copy"
    destination.mkdir()
    marker = destination / "keep.txt"
    marker.write_text("keep")
    report = tmp_path / "audit.json"
    assert (
        main(
            [
                "--confirmatory-values",
                str(values),
                "--assembly-facts",
                empty_facts_file(tmp_path / "assembly-facts.json"),
                "--manuscript",
                str(MANUSCRIPT),
                "--output",
                str(destination),
                "--report",
                str(report),
            ]
        )
        == 2
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "refused"
    assert payload == json.loads(report.read_text())
    assert marker.read_text() == "keep"


@pytest.mark.parametrize(
    "part",
    [
        "sealed-v4-any",
        "sealed-v4-exploratory-x3-x7",
        "restricted",
        "coord-20260925/v4-release",
        "coord-20260925/v4-tier-logs",
        "coord-20260925/v4-gate-logs",
    ],
)
def test_forbidden_paths_are_rejected_before_open(tmp_path: Path, part: str) -> None:
    with pytest.raises(ValueError, match="Forbidden"):
        load_catalog(tmp_path / part / "catalog.json")


def mechanics_decision(name: str, text: str, slot: str, order: float) -> Decision:
    return Decision(
        name,
        "synthetic-shell",
        1,
        1,
        "selected",
        "",
        text,
        slot,
        "append",
        order,
        False,
    )


def test_document_composer_preserves_fixed_text_and_inserts_into_exact_slots() -> None:
    decisions = {
        d.id: d
        for d in [
            mechanics_decision("design", " ".join(["design"] * 150), "abstract", 0),
            mechanics_decision("limitation", "Fixed limitation.", "abstract", 10000),
            mechanics_decision("R", r"Result \resultnum{id}{3}.", "P1", 1),
            mechanics_decision("D", "Selected interpretation.", "DS02", 2),
            mechanics_decision("C1", "Headline.", "C1", 3),
            mechanics_decision("C2", "Boundary.", "C2", 4),
            mechanics_decision("C3", "Implication.", "C3", 5),
        ]
    }
    report = AssemblyPlan(decisions, "a", "b", {})
    sources = {
        "main.tex": r"\abstract{Old {nested} text.}" + "\n",
        "sections/discussion.tex": "% DS02\nFixed discussion.\n\n% DS11\nFixed X5.\n",
        "sections/conclusion.tex": (
            "Fixed CN01. [Insert headline.] [State whether boundaries.] "
            "[Insert implication.]\nFixed X5 conclusion.\n"
        ),
    }
    documents, budget = compose_documents(report, sources)
    assert (
        documents["sections/discussion.tex"]
        == "% DS02\nFixed discussion.\n\nSelected interpretation.\n\n"
        "% DS11\nFixed X5.\n"
    )
    assert (
        documents["sections/conclusion.tex"]
        == "Fixed CN01. Headline. Boundary. Implication.\nFixed X5 conclusion.\n"
    )
    assert "Old" not in documents["main.tex"]
    assert budget.words == 152
    refused = replace(decisions["D"], state="refused", reason="Unavailable condition")
    with pytest.raises(AssemblyRefusedError):
        compose_documents(
            replace(report, decisions=decisions | {"D": refused}), sources
        )


def test_bound_text_refuses_missing_values_and_counts_visible_lists() -> None:
    with pytest.raises(ValueError, match="Missing text bindings"):
        bind(r"\resultnum{missing}{[n]}", {})
    text = bind(
        r"Shares: \resultnum{long.identifier}{0}.",
        {"long.identifier": "0.50, 0.70, 0.90"},
    )
    assert visible_word_count(text) == 7


@pytest.mark.parametrize(
    "count,verb,noun,pronoun",
    [
        ("0", "were", "units", "they"),
        ("1", "was", "unit", "it"),
        ("2", "were", "units", "they"),
        ("1.0", "was", "unit", "it"),
        ("1,000", "were", "units", "they"),
    ],
)
def test_number_agreement_uses_the_bound_integer(
    count: str, verb: str, noun: str, pronoun: str
) -> None:
    source = (
        r"There \resultplural{n}{was}{were} \resultnum{n}{[n]} "
        r"\resultplural{n}{unit}{units}; \resultplural{n}{it}{they} failed."
    )
    assert bind(source, {"n": count}) == (
        rf"There {verb} \resultnum{{n}}{{{count}}} {noun}; {pronoun} failed."
    )


@pytest.mark.parametrize("count", ["1.5", "-1", "NaN", "Infinity", "1,2", "missing"])
def test_number_agreement_refuses_invalid_counts_with_locator(count: str) -> None:
    with pytest.raises(ValueError, match=r"shell.tex:41, text line 2:.*integer.*n="):
        bind(
            "Heading.\n" + r"\resultnum{n}{[n]} \resultplural{n}{unit}{units}",
            {"n": count},
            locator="shell.tex:41",
        )


@pytest.mark.parametrize(
    "values,reason",
    [({}, "Missing resultplural value"), ({"n": "1"}, "not bound in the same block")],
)
def test_number_agreement_requires_a_local_binding(
    values: dict[str, str], reason: str
) -> None:
    with pytest.raises(ValueError, match="block B, text line 1: .*" + reason):
        bind(r"\resultplural{n}{unit}{units}", values, locator="block B")
    with pytest.raises(ValueError, match="not bound in the same block"):
        bind(
            "% \\resultnum{n}{[n]}\n" + r"\resultplural{n}{unit}{units}",
            {"n": "1"},
        )


def test_number_agreement_refuses_malformed_forms() -> None:
    with pytest.raises(ValueError, match=r"shell\.tex:7: Malformed resultplural"):
        bind(
            r"\resultnum{n}{[n]} \resultplural{n}{unit}{units",
            {"n": "1"},
            locator="shell.tex:7",
        )


@pytest.mark.parametrize("count", ["0", "1", "2"])
def test_number_agreement_resolves_before_the_abstract_budget(count: str) -> None:
    source = (
        r"\resultnum{count.with.a.long.ID}{[n]} "
        r"\resultplural{count.with.a.long.ID}{unit was}{units were} observed."
    )
    text = bind(source, {"count.with.a.long.ID": count})
    budget = first_fit(["word " * 246, text], {})
    assert budget.words == 250
    with pytest.raises(ValueError, match="Mandatory abstract exceeds"):
        first_fit(["word " * 247, text], {})
    spec = importlib.util.spec_from_file_location(
        "plural_paper_check", MANUSCRIPT / "pipeline/paper_check.py"
    )
    assert spec and spec.loader
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    assert checker.abstract_word_count(source) == visible_word_count(source) == 4
    assert checker.abstract_word_count(budget.text) == 250


def test_synthetic_assembly_renders_one_invalid_unit_in_the_singular(
    tmp_path: Path,
) -> None:
    values = complete_values("invalid-main")
    assert values["v4.t1.n_not_valid"] == values["v4.t1.n_invalid_gate"] == "1"
    output = tmp_path / "assembled"
    assemble(
        values,
        {},
        manuscript=MANUSCRIPT,
        output=output,
        facts=owner_facts("invalid-main"),
    )
    results = (output / "sections/results.tex").read_text()
    discussion = (output / "sections/discussion.tex").read_text()
    assert (
        r"\resultnum{v4.t1.n_not_valid}{1} of the nine tier-"
        r"\resultnum{v4.protocol.tier.main_B}{1} units was not both complete and valid"
        in results
    )
    assert (
        r"\resultnum{v4.t1.n_not_valid}{1} unit was not both complete and valid"
        in discussion
    )
    assert (
        r"This included \resultnum{v4.t1.n_invalid_gate}{1} zero-strength gate failure"
        in discussion
    )
    for filename in (
        "main.tex",
        "sections/results.tex",
        "sections/discussion.tex",
        "sections/conclusion.tex",
        "sections/supplement-exploratory-x3-x7.tex",
    ):
        assert r"\resultplural{" not in (output / filename).read_text()


def test_plan_records_the_block_and_source_of_invalid_agreement() -> None:
    values = complete_values("invalid-main") | {"v4.t1.n_not_valid": "1.5"}
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("invalid-main"))
    decision = report.decisions["B02.lead"]
    assert decision.state == "refused"
    assert "B02.lead (pipeline/drafts/2026-09-28/results-shells.tex:" in decision.reason
    assert "requires a nonnegative integer: v4.t1.n_not_valid=1.5" in decision.reason


@pytest.mark.parametrize("count", ["0", "1", "2"])
def test_every_shell_agreement_has_its_binding_in_the_same_rule(count: str) -> None:
    for name, text in shell_texts(manuscript=MANUSCRIPT).items():
        values = dict.fromkeys(re.findall(r"\\resultnum\{([^{}]+)\}", text), count)
        resolved = bind(text, values, locator=name)
        assert r"\resultplural{" not in resolved
    text = shell_texts(manuscript=MANUSCRIPT)["P7-b"]
    values = dict.fromkeys(re.findall(r"\\resultnum\{([^{}]+)\}", text), count)
    resolved = bind(text, values)
    noun, verb = ("unit", "is") if count == "1" else ("units", "are")
    assert f"There {verb}" in resolved
    assert f"complete but invalid {noun} in tier" in resolved


def test_x6_wilson_sentence_is_inserted_after_the_first_denominator_sentence() -> None:
    decisions = {
        d.id: d
        for d in [
            mechanics_decision("design", " ".join(["word"] * 150), "abstract", 0),
            mechanics_decision(
                "D-X6-DENOMINATORS",
                "First denominator.\nRemaining denominators.",
                "DS06",
                1,
            ),
            mechanics_decision("D-X6-INTERVAL", "Wilson interval.", "DS06", 2),
        ]
    }
    documents, _ = compose_documents(
        AssemblyPlan(decisions, "a", "b", {}),
        {
            "main.tex": r"\abstract{Old.}",
            "sections/discussion.tex": "% DS06\nFixed discussion.\n",
            "sections/conclusion.tex": (
                "[Insert result.] [State whether boundary.] [Insert implication.]"
            ),
        },
    )
    assert (
        "First denominator.\nWilson interval.\nRemaining denominators."
        in documents["sections/discussion.tex"]
    )


@pytest.mark.parametrize("case", list(CASES))
def test_sourced_facts_and_exported_verdicts_complete_each_rehearsal(case: str) -> None:
    report = plan(
        complete_values(case), {}, manuscript=MANUSCRIPT, facts=owner_facts(case)
    )
    assert not report.refused
    branch = (
        "B1b-G2c"
        if "comparison" in case
        else "B1b-G0"
        if case == "failed-G0"
        else "B1a"
    )
    assert report.decisions[branch].state == "selected"
    sources = {
        name: (MANUSCRIPT / name).read_text()
        for name in (
            "main.tex",
            "sections/discussion.tex",
            "sections/conclusion.tex",
            "sections/supplement.tex",
        )
    }
    documents, budget = compose_documents(report, sources)
    assert 150 <= budget.words <= 250
    assert "[reason in words]" not in documents["sections/results.tex"]
    assert "all 72 cells finished" in documents["sections/discussion.tex"]
    assert "all 36 cells with estimates" in documents["sections/conclusion.tex"]
    if case == "passed-shp":
        positions = [
            documents["sections/results.tex"].index(report.decisions[name].text)
            for name in (
                "P1.1",
                "B1a",
                "P3.1",
                "P4",
                "P5-a.1",
                "P6.lead",
                "P7-a",
                "P8.1",
                "B16",
                "P10",
            )
        ]
        assert positions == sorted(positions)
    if branch == "B1a":
        assert re.findall(
            r"\\input\{generated/([^{}]+)\}", documents["sections/results.tex"]
        )[:5] == [
            "primary-boundary-figure",
            "auc-profiles",
            "boundary-table",
            "gate-outcomes",
            "unit-status",
        ]
    assert ("Evaluation used new seeds." in documents["sections/conclusion.tex"]) == (
        branch == "B1a"
    )
    assert (
        "Every stage must pass before any evaluation on reserved seeds."
        in documents["sections/conclusion.tex"]
    ) == (branch != "B1a")
    assert "draft status" not in documents["sections/discussion.tex"]


def repinner() -> Any:
    path = MANUSCRIPT / "pipeline/review/repin_v4_manuscript_assembly.py"
    spec = importlib.util.spec_from_file_location("assembly_repinner", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_registry(before: bytes) -> dict[str, Any]:
    return {
        "schema": "ic-study.v4-manuscript-assembly-rules.v1",
        "sources": {
            "results": {
                "path": "shell.tex",
                "sha256": hashlib.sha256(before).hexdigest(),
            }
        },
        "predicates": {},
        "rules": [
            {
                "id": "R",
                "source": "results",
                "line": 2,
                "end_line": 5,
                "condition": True,
                "slot": "P1",
                "operation": "append",
                "order": 1,
                "fragments": [{"line": 3, "end_line": 4, "condition": True}],
            }
        ],
    }


@pytest.mark.parametrize("edit", ["before", "comment", "visible", "remove"])
def test_repin_command_requires_explicit_visible_acceptance_and_preserves_fragments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    edit: str,
) -> None:
    module = repinner()
    before = b"Head.\n% BEGIN BLOCK R\nFirst.\nSecond.\n% END BLOCK R\nTail.\n"
    after = {
        "before": b"% inserted\n" + before,
        "comment": before.replace(b"First.\n", b"First.\n% comment inside\n"),
        "visible": before.replace(b"First.", b"Changed wording."),
        "remove": b"Head.\nTail.\n",
    }[edit]
    study = tmp_path / "studies/study"
    manuscript = study / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "shell.tex").write_bytes(after)
    rules = study / "rules.json"
    rules.write_bytes(module.rules_bytes(synthetic_registry(before)))
    original = rules.read_bytes()
    receipt = study / "receipt.json"
    monkeypatch.setattr(module, "STUDY", study)

    def git(args: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[Any]:
        return subprocess.CompletedProcess(
            args,
            0,
            stdout="a" * 40 if args[1] == "rev-parse" else before,
        )

    monkeypatch.setattr(module.subprocess, "run", git)
    args = [
        "--rules",
        str(rules),
        "--manuscript",
        str(manuscript),
        "--old-shell",
        "results=old",
        "--receipt",
        str(receipt),
    ]
    if edit in {"visible", "remove"}:
        assert module.main(args) == 2
        assert rules.read_bytes() == original and not receipt.exists()
        args += ["--accept-visible", "R"]
        if edit == "remove":
            assert module.main(args) == 2
            assert rules.read_bytes() == original and not receipt.exists()
            return
    assert module.main(args) == 0
    updated = json.loads(rules.read_text())
    proof = json.loads(receipt.read_text())
    row = updated["rules"][0]
    assert row["line"] == (3 if edit == "before" else 2)
    assert row["end_line"] == (6 if edit in {"before", "comment"} else 5)
    assert row["fragments"][0]["end_line"] == (
        5 if edit in {"before", "comment"} else 4
    )
    assert proof["after_rules_sha256"] == hashlib.sha256(rules.read_bytes()).hexdigest()
    assert updated["sources"]["results"]["sha256"] == hashlib.sha256(after).hexdigest()
    assert (
        proof["rules"][0]["kind"]
        == {
            "before": "displacement",
            "comment": "comment-only",
            "visible": "visible-text",
        }[edit]
    )


def test_repin_rejects_a_removed_nested_fragment_even_with_acceptance() -> None:
    module = repinner()
    before = b"Head.\n% BEGIN BLOCK R\nFirst.\nSecond.\n% END BLOCK R\nTail.\n"
    registry = synthetic_registry(before)
    registry["rules"][0]["fragments"][0]["end_line"] = 3
    with pytest.raises(ValueError, match="Removed fragment"):
        module.repin_registry(
            registry,
            {"results": before},
            {"results": before.replace(b"First.\n", b"")},
            {"R"},
        )


def test_repin_refuses_unbound_old_revision_and_unknown_acceptance() -> None:
    module = repinner()
    before = b"Head.\n% BEGIN BLOCK R\nFirst.\nSecond.\n% END BLOCK R\nTail.\n"
    registry = synthetic_registry(before)
    with pytest.raises(ValueError, match="pinned digest"):
        module.repin_registry(
            registry, {"results": before + b"extra"}, {"results": before}, set()
        )
    with pytest.raises(ValueError, match="Unknown acceptance"):
        module.repin_registry(
            registry, {"results": before}, {"results": before}, {"unknown"}
        )


def test_repin_explicit_locator_excludes_editorial_prose_from_a_quote() -> None:
    module = repinner()
    before = b"Head.\n% BEGIN BLOCK R\n> Original quote.\nSecond.\n% END BLOCK R\n"
    after = before.replace(b"> Original quote.\n", b"> New quote.\n\nEditorial note.\n")
    registry = synthetic_registry(before)
    row = registry["rules"][0]
    row["line"] = row["end_line"] = 3
    del row["fragments"]
    updated, receipt = module.repin_registry(
        registry, {"results": before}, {"results": after}, {"R"}, {"R": (3, 3)}
    )
    assert updated["rules"][0]["end_line"] == 3
    assert receipt["rules"][0]["diff_candidate_locator"] == [3, 5]
    with pytest.raises(ValueError, match="explicit ID acceptance"):
        module.repin_registry(
            registry, {"results": before}, {"results": after}, set(), {"R": (3, 3)}
        )


def test_x5_supply_requires_sourced_provenance_and_all_share_states() -> None:
    values, facts = complete_values("passed-shp"), owner_facts("passed-shp")
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert report.decisions["D-X5-POST"].state == "excluded"
    assert report.decisions["D-X5-POST-UNAVAILABLE"].state == "selected"
    del facts["facts"]["post.x5_supplied"]
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert report.decisions["D-X5-POST-UNAVAILABLE"].state == "refused"
    facts = owner_facts("passed-shp")
    facts["facts"]["post.x5_supplied"]["value"] = True
    for key in values:
        if key.endswith(".x5_state.state"):
            values[key] = "disponível"
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert report.decisions["D-X5-POST"].state == "selected"
    assert "first point-AUC attainments" in report.decisions["D-X5-POST"].text
    assert report.decisions["D-X5-POST-UNAVAILABLE"].state == "excluded"
    values["v4x.comparisons.by_r.0-9.x5_state.state"] = "indisponível"
    with pytest.raises(ValueError, match="conflicts"):
        plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    values.pop("v4x.comparisons.by_r.0-9.x5_state.state")
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert report.decisions["D-X5-POST"].state == "refused"


@pytest.mark.parametrize(
    "name",
    [
        "shp.state",
        "shp.grid_position",
        "tier2.boundaries_differ",
        "main.boundary_nonmonotone",
    ],
)
def test_missing_required_fact_refuses_instead_of_inferring_from_display(
    name: str,
) -> None:
    facts = owner_facts("passed-shp")
    del facts["facts"][name]
    report = plan(complete_values("passed-shp"), {}, manuscript=MANUSCRIPT, facts=facts)
    assert any("Missing assembly fact: " + name in d.reason for d in report.refused)


@pytest.mark.parametrize(
    "state", ["not-run", "failed", "pre-run-divergence", "parameter-bound"]
)
def test_shp_states_require_a_source_and_cause_without_fabricating_an_anchor(
    state: str,
) -> None:
    facts = owner_facts("passed-shp")
    origin = facts["facts"]["shp.state"]["source"]
    facts["facts"]["shp.state"]["value"] = state
    facts["facts"]["shp.reason"] = {
        "value": "Artificial cause & public record",
        "source": origin,
    }
    if state == "pre-run-divergence":
        facts["facts"]["shp.divergence"] = {
            "value": {
                "kind": "item",
                "recorded_utc": "2026-09-28T10:00:00Z",
                "execution_started_utc": "2026-09-28T11:00:00Z",
            },
            "source": origin,
        }
    del facts["facts"]["shp.grid_position"]
    values = complete_values("passed-shp")
    if state != "parameter-bound":
        values = {k: v for k, v in values.items() if not k.startswith("v4.shp.")}
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert not report.refused
    assert report.decisions["D-SHP-ADMISSIBLE"].state == "excluded"
    expected = "D-SHP-NOT-RUN" if state == "not-run" else "D-B14"
    assert r"Artificial cause \& public record" in report.decisions[expected].text
    assert report.decisions["D-B14-ENVELOPE"].state == (
        "selected" if state == "parameter-bound" else "excluded"
    )
    del facts["facts"]["shp.reason"]
    refused = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert any("shp.reason" in d.reason for d in refused.refused)


@pytest.mark.parametrize("position", ["below", "above", "interval-outside"])
def test_raw_grid_fact_replaces_default_anchor_without_using_rounded_values(
    position: str,
) -> None:
    facts = owner_facts("passed-shp")
    facts["facts"]["shp.grid_position"]["value"] = position
    report = plan(complete_values("passed-shp"), {}, manuscript=MANUSCRIPT, facts=facts)
    assert not report.refused
    assert report.decisions["B13"].state == "selected"
    assert report.decisions["P8.1"].state == "excluded"
    if position == "above":
        assert (
            r"above the largest grid value, \resultnum{v4.protocol.r.090}{0.90}"
            in report.decisions["B13"].text
        )
    if position == "interval-outside":
        assert "estimate lies below" not in report.decisions["B13"].text
        assert report.decisions["D-B13-PART"].state == "selected"


def test_gate_subcases_copy_only_applicable_clauses() -> None:
    facts = owner_facts("failed-G0")
    report = plan(complete_values("failed-G0"), {}, manuscript=MANUSCRIPT, facts=facts)
    text = report.decisions["B1b-G0"].text
    assert "budget_statuses" in text and "anchor_failures" not in text
    assert "did not reach its criteria" not in text
    for name in ["ii-comparison-no-ratio", "iii-comparisons-absent"]:
        report = plan(
            complete_values(name), {}, manuscript=MANUSCRIPT, facts=owner_facts(name)
        )
        text = report.decisions["B1b-G2c"].text
        assert "comparison could not be evaluated" in text
        assert "the variance ratio was" not in text
    name = "i-comparison-failed"
    facts = owner_facts(name)
    facts["facts"]["gate.G2c.failed_comparisons"]["value"] = ["a003"]
    report = plan(complete_values(name), {}, manuscript=MANUSCRIPT, facts=facts)
    text = report.decisions["B1b-G2c"].text
    assert "a003.ratio" in text and "a010.ratio" not in text
    assert "comparison could not be evaluated" not in text


@pytest.mark.parametrize("value", ["true", "2", "NaN"])
def test_malformed_gate_verdict_is_rejected(value: str) -> None:
    values = complete_values("passed-shp") | {"v4.gate.G2.verdict.approved": value}
    with pytest.raises(ValueError, match="Invalid gate verdict"):
        plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))


@pytest.mark.parametrize(
    "mutation",
    ["unknown-fact", "no-source", "bad-digest", "wrong-type", "unknown-state"],
)
def test_facts_schema_rejects_untraceable_or_ambiguous_inputs(mutation: str) -> None:
    facts = owner_facts("passed-shp")
    entry = facts["facts"]["shp.state"]
    if mutation == "unknown-fact":
        facts["facts"]["branch-override"] = entry
    elif mutation == "no-source":
        del entry["source"]
    elif mutation == "bad-digest":
        entry["source"]["sha256"] = "invented"
    elif mutation == "wrong-type":
        facts["facts"]["main.boundary_nonmonotone"]["value"] = 0
    else:
        entry["value"] = "unknown"
    with pytest.raises(ValueError):
        validate_facts(facts)


def test_duplicate_fact_keys_and_forbidden_fact_paths_are_rejected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "assembly-facts.json"
    path.write_text('{"schema":"a","schema":"b"}')
    with pytest.raises(ValueError, match="Duplicate"):
        load_facts(path)
    with pytest.raises(ValueError, match="Forbidden"):
        load_facts(tmp_path / "restricted/assembly-facts.json")


def test_cli_completes_a_copy_and_binds_facts_to_its_receipt(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "catalog.json"
    path.write_text(
        json.dumps(
            {
                "schema": "ic-study.v4-result-values.v1",
                "values": complete_values("passed-shp"),
            }
        )
    )
    facts_path = tmp_path / "assembly-facts.json"
    facts = owner_facts("passed-shp")
    facts_path.write_text(json.dumps(facts))
    output = tmp_path / "assembled"
    original = hashlib.sha256((MANUSCRIPT / "main.tex").read_bytes()).hexdigest()
    args = [
        "--confirmatory-values",
        str(path),
        "--assembly-facts",
        str(facts_path),
        "--manuscript",
        str(MANUSCRIPT),
        "--output",
        str(output),
    ]
    assert main(args) == 0
    report = json.loads(capsys.readouterr().out)
    receipt = json.loads((output / "assembly-record.json").read_text())
    assert report["status"] == "ready"
    assert receipt["facts"] == facts
    assert receipt["facts_sha256"] == report["facts_sha256"]
    assert (
        hashlib.sha256((MANUSCRIPT / "main.tex").read_bytes()).hexdigest() == original
    )
    assert main(args) == 2
    assert "new copy" in capsys.readouterr().out


def test_post_execution_divergence_cannot_be_promoted_to_a_pre_run_fact() -> None:
    facts = owner_facts("passed-shp")
    facts["facts"]["shp.divergence"] = {
        "value": {
            "kind": "scale",
            "recorded_utc": "2026-09-28T12:00:00Z",
            "execution_started_utc": "2026-09-28T11:00:00Z",
        },
        "source": facts["facts"]["shp.state"]["source"],
    }
    with pytest.raises(ValueError, match="Invalid assembly fact"):
        validate_facts(facts)


def interrupted_values(stage: str, *, failed: bool) -> dict[str, str]:
    values = complete_values("passed-shp")
    stages = ["G0", "G1b", "G1c", "G2", "G2c"]
    for later in stages[stages.index(stage) + 1 :]:
        values = {
            k: v for k, v in values.items() if not k.startswith(f"v4.gate.{later}.")
        }
        values |= {
            f"v4.gate.{later}.verdict.{name}": "0"
            for name in ("complete", "approved", "stop")
        }
    values[f"v4.gate.{stage}.verdict.complete"] = str(int(failed))
    values[f"v4.gate.{stage}.verdict.approved"] = "0"
    if not failed:
        if stage == "G2c":
            values["v4.gate.G2c.planned"] = "142"
        values[f"v4.gate.{stage}.completed"] = "7"
        values |= {
            "v4.gate.last_stage": stage,
            "v4.gate.last_stage.completed": "7",
            "v4.gate.last_stage.planned": values[f"v4.gate.{stage}.planned"],
        }
    return values


@pytest.mark.parametrize("stage", ["G0", "G1b", "G1c", "G2", "G2c"])
def test_each_complete_failure_selects_only_its_frozen_gate_branch(stage: str) -> None:
    facts = owner_facts("failed-G0")
    origin = facts["facts"]["shp.state"]["source"]
    if stage == "G1c":
        facts["facts"]["gate.G1c.failed_criteria"] = {
            "value": ["anchor"],
            "source": origin,
        }
    if stage == "G2":
        facts["facts"]["gate.G2.failed_criteria"] = {
            "value": ["allowance"],
            "source": origin,
        }
    if stage == "G2c":
        facts["facts"]["gate.G2c.failed_comparisons"] = {
            "value": ["a010"],
            "source": origin,
        }
    report = plan(
        interrupted_values(stage, failed=True), {}, manuscript=MANUSCRIPT, facts=facts
    )
    assert not report.refused
    assert report.decisions["B1b-" + stage].state == "selected"
    assert report.decisions["B1a"].state == "excluded"
    assert report.decisions["B1d"].state == "excluded"
    assert all(
        d.state == "excluded"
        for d in report.decisions.values()
        if d.id.startswith("E.")
    )


@pytest.mark.parametrize("stage", ["G0", "G1b", "G1c", "G2", "G2c"])
def test_an_incomplete_gate_requires_explicit_close_evidence(stage: str) -> None:
    facts = owner_facts("failed-G0")
    values = interrupted_values(stage, failed=False)
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert not report.refused
    assert report.decisions["B1d"].state == "selected"
    del facts["facts"]["gate.at_close"]
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert report.decisions["B1d"].state == "refused"


def test_recorded_waste_guard_selects_stop_without_rounding_its_probability() -> None:
    values = interrupted_values("G2", failed=False)
    values = {k: v for k, v in values.items() if not k.startswith("v4.gate.G2.")}
    values |= {
        "v4.gate.G2.verdict.complete": "0",
        "v4.gate.G2.verdict.approved": "0",
        "v4.gate.G2.verdict.stop": "1",
        "v4.gate.stop.gaps": "2",
        "v4.gate.stop.denominator": "54",
        "v4.gate.stop.pass_probability": "0.800",
        "v4.gate.stop.minimum": "0.80",
    }
    facts = owner_facts("failed-G0")
    del facts["facts"]["gate.at_close"]
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=facts)
    assert not report.refused
    assert report.decisions["B1c"].state == "selected"
    assert report.decisions["B1d"].state == "excluded"


@pytest.mark.parametrize(
    "main_invalid,tier_failed", [(False, True), (True, False), (True, True)]
)
def test_permission_explanation_identifies_each_failed_requirement(
    main_invalid: bool, tier_failed: bool
) -> None:
    values = complete_values("passed-shp") | {
        "v4.mechanisms.allowed": "0",
        "v4.t1.n_not_valid": str(int(main_invalid)),
        "v4.inv.t2.n_incomplete": "0",
        "v4.inv.t2.n_invalid": str(int(tier_failed)),
    }
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    tier = r"\resultnum{v4.protocol.tier.main_others}{2}"
    if main_invalid and tier_failed:
        reason = (
            f"The main curve was invalid, and tier {tier} "
            "was not entirely complete and valid."
        )
    elif main_invalid:
        reason = (
            f"The main curve was invalid; tier {tier} was entirely "
            "complete and valid, but both are required."
        )
    else:
        reason = (
            f"Tier {tier} was not entirely complete and valid; "
            "the main curve was valid, but both are required."
        )
    requirement = (
        "A comparison across mechanisms requires both a valid main B curve "
        f"and an entirely complete valid tier {tier}."
    )
    expected = {
        "P6-a": (
            reason.replace(
                "both are required.", "both are required for comparing mechanisms."
            )
        )
        + " Mechanisms are therefore not compared, either locally or in the headline. "
        "Valid units remain displayed.",
        "D-NO-PERMISSION": requirement
        + " "
        + reason
        + "\nValid units remain displayed, but neither local comparisons nor "
        "the headline can be interpreted across mechanisms in this release.",
        "C-NO-PERMISSION": "No comparison is interpreted across mechanisms. "
        + reason
        + " An available local pair does not restore the cross-mechanism permission.",
    }
    _, documents = composed_documents("passed-shp", values)
    for name, text in expected.items():
        decision = report.decisions[name]
        assert decision.state == "selected"
        neighbours = sorted(
            (
                d
                for d in report.decisions.values()
                if d.state == "selected" and d.slot == decision.slot and d.text
            ),
            key=lambda d: (d.order, d.id),
        )
        paragraph = "\n".join(text if d.id == name else d.text for d in neighbours)
        section = (
            "results"
            if name == "P6-a"
            else "discussion"
            if name.startswith("D-")
            else "conclusion"
        )
        actual = next(
            p
            for p in documents[f"sections/{section}.tex"].split("\n\n")
            if decision.text in p
        )
        assert " ".join(actual.split()) == " ".join(paragraph.split())


@pytest.mark.parametrize("case", CASES)
def test_real_shells_preserve_pre_t58_discussion_and_conclusion_paragraphs(
    case: str,
) -> None:
    report, documents = composed_documents(case)
    expected = {
        "failed-G0": (13, 4),
        "unavailable": (16, 5),
        "i-comparison-failed": (14, 4),
        "ii-comparison-no-ratio": (14, 4),
        "iii-comparisons-absent": (14, 4),
    }.get(case, (17, 5))
    for name, count in zip(("discussion", "conclusion"), expected, strict=True):
        paragraphs = [
            p for p in documents[f"sections/{name}.tex"].split("\n\n") if p.strip()
        ]
        assert len(paragraphs) == count, (case, name)
    if report.decisions["D-X6-INTERVAL"].state == "selected":
        paragraph = next(
            p
            for p in documents["sections/discussion.tex"].split("\n\n")
            if "The primary Wilson interval was" in p
        )
        assert re.search(
            r"jointly covered the primary procedural truth, D1 .*?\.\n"
            r"The primary Wilson interval was .*?\.\nJoint coverage requires",
            paragraph,
        )


@pytest.mark.parametrize("category", ["small", "large", "not_attained", "censored"])
@pytest.mark.parametrize("count", [1, 8, 9])
def test_single_boundary_category_omits_zero_lists_with_matching_headlines(
    category: str, count: int
) -> None:
    values = complete_values("passed-shp") | {
        "v4.mechanisms.allowed": "0",
        "v4.t1.n_valid": str(count),
        "v4.t1.n_not_valid": str(9 - count),
        "v4.t1.n_attained": str(count if category in {"small", "large"} else 0),
        **{
            "v4.t1.n_" + c: str(count if c == category else 0)
            for c in ("small", "large", "not_attained", "censored")
        },
    }
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    if category == "not_attained" and count == 9:
        assert report.decisions["A.B03"].state == "selected"
        assert report.decisions["A.H-B"].state == "excluded"
        return
    for name in ("A.H-B", "P5-a.1", "C-H-B"):
        decision = report.decisions[name]
        assert decision.state == "selected"
        assert ("at all " in decision.text) == (count == 9)
        assert ("none was" in decision.text) == (count == 9)
        assert rf"\resultnum{{v4.t1.n_{category}}}{{{count}}}" in decision.text
        if count == 9:
            assert not re.search(r"\\resultnum\{v4\.t1\.n_[^{}]+\}\{0\}", decision.text)


def test_zero_unavailability_omits_reasons_and_unattained_boundary_clause() -> None:
    values = complete_values("passed-shp") | {
        "v4x.comparisons.count.x1b.unavailable": "0",
        "v4x.comparisons.count.x1b.available": "9",
        "v4x.comparisons.count.x3.unavailable": "0",
        "v4x.comparisons.count.x4.unavailable": "0",
        "v4x.comparisons.count.x4.partial": "1",
        "v4.t1.n_not_attained": "0",
        "v4x.comparisons.count.x5.equivalent.unavailable": "1",
        "v4x.comparisons.count.x5.interval.unavailable": "1",
        "v4.inv.t3.n_incomplete": "0",
    }
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    texts = {name: decision.text for name, decision in report.decisions.items()}
    assert "at the other" not in next(
        text for name, text in texts.items() if "twin-and-expanded" in name
    )
    partial = next(
        text for name, text in texts.items() if "partial-and-unavailable" in name
    )
    assert "Reasons distinguish" not in partial
    assert "confirmatory first boundary is not attained" not in "\n".join(
        texts.values()
    )
    assert "Unfinished units are absent" not in texts["P7-c"]


def test_x6_retry_and_precision_clauses_require_positive_recorded_evidence() -> None:
    values = complete_values("passed-shp")
    key = "v4x.x6.x6a.strengths.r070.a0010.truth_d1.retry_fraction"
    nominal = "v4x.x6.x6a.strengths.r070.a0010.vs_d1.band_interval.nominal_reading"
    for retry in ("0", "0.25"):
        supplied = values | {key: retry}
        report = plan(
            supplied, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp")
        )
        text = report.decisions["D-X6-DENOMINATORS"].text
        assert ("-pair retries" in text) == (retry != "0")
        assert "original nominal readings" not in text
    report = plan(
        values
        | {
            nominal: "adequate",
            nominal.replace("nominal_reading", "truth_precision.minus_2se"): "failure",
            nominal.replace("nominal_reading", "truth_precision.plus_2se"): "adequate",
        },
        {},
        manuscript=MANUSCRIPT,
        facts=owner_facts("passed-shp"),
    )
    assert "original nominal readings" in report.decisions["D-X6-DENOMINATORS"].text


def test_x7_display_follows_its_summary_and_precedes_post_release_tables() -> None:
    _, documents = composed_documents("passed-shp")
    text = documents["sections/supplement-exploratory-x3-x7.tex"]
    assert (
        text.index(r"\input{generated/exploratory-x7}")
        < text.index(r"\input{generated/exploratory-x7-boundaries}")
        < text.index(r"\input{generated/exploratory-comparisons}")
    )
    assert r"\input{generated/exploratory-x7-boundaries}" not in documents["main.tex"]


def test_all_nine_large_boundaries_share_the_abstract_and_conclusion_headline() -> None:
    values = complete_values("passed-shp") | {
        "v4.mechanisms.allowed": "0",
        "v4.t1.n_not_valid": "0",
        "v4.t1.n_large": "9",
        "v4.t1.n_small": "0",
        "v4.t1.n_not_attained": "0",
        "v4.t1.n_censored": "0",
    }
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    for name in ("A.H-B", "C-H-B", "P5-a.1"):
        text = report.decisions[name].text
        assert "large at all \\resultnum{v4.t1.n_large}{9}" in text
        assert "none was small, not attained, censored or indeterminate" in text


@pytest.mark.parametrize("count", [0, 1, 9])
def test_sensitivity_inventory_and_partial_readings_use_natural_count_agreement(
    count: int,
) -> None:
    values = complete_values("passed-shp") | {
        "v4.sens.use_b12": "1",
        "v4.inv.t6.n_valid": str(count),
        "v4x.comparisons.count.x4.partial": str(count),
        "v4x.comparisons.count.x4.unavailable": "0",
        "v4x.comparisons.count.x3.unavailable": str(int(count == 0)),
    }
    report, documents = composed_documents("passed-shp", values)
    agreement = "was" if count == 1 else "were"
    sensitivity = report.decisions["B12.inventory"].text
    assert (
        f"{{v4.inv.t6.n_valid}}{{{count}}} {agreement} complete and valid"
        in sensitivity
    )
    partial = report.decisions["E.partial-and-unavailable-readings"].text
    assert report.decisions["E.partial-and-unavailable-readings"].state == "selected"
    assert ("Reasons distinguish" in partial) == (count == 0)
    form = "share had" if count == 1 else "shares had"
    assert (
        rf"\resultnum{{v4x.comparisons.count.x4.partial}}{{{count}}} "
        f"response signal {form} a partial reading"
    ) in partial
    assert "count was" not in partial
    assert partial in documents["sections/supplement-exploratory-x3-x7.tex"]


def test_no_available_twin_boundary_has_a_standalone_zero_variant() -> None:
    values = complete_values("passed-shp") | {
        "v4x.comparisons.count.x1b.available": "0",
        "v4x.comparisons.count.x1b.unavailable": "9",
    }
    report, documents = composed_documents("passed-shp", values)
    text = report.decisions["E.twin-and-expanded-feature-boundaries"].text
    assert (
        "In the supplied post-release aggregate, no twin first boundary was available."
        in text
    )
    assert "at the other" not in text
    assert "available at" not in text
    assert text in documents["sections/supplement-exploratory-x3-x7.tex"]


@pytest.mark.parametrize(
    "reading,upper,prose",
    [
        ("failure", "0.899999", "0.899999"),
        ("subnominal", "0.949999", "0.949999"),
        ("failure", "0.8996", "0.8996"),
        ("subnominal", "0.9496", "0.9496"),
        ("adequate", "0.99059", "0.991"),
    ],
)
def test_interval_and_comparisons_use_the_same_wilson_prose_endpoint(
    reading: str,
    upper: str,
    prose: str,
) -> None:
    key = "v4x.x6.x6a.band.vs_d1.primary.wilson95."
    values = complete_values("passed-shp") | {
        READING: reading,
        key + "i000": "0.800",
        key + "prose_lower": "0.800",
        key + "i001": upper,
        key + "prose_upper": prose,
    }
    report, documents = composed_documents("passed-shp", values)
    assert (
        rf"\resultnum{{{key}prose_upper}}{{{prose}}}"
        in report.decisions["D-X6-" + reading.upper()].text
    )
    assert (
        rf"\resultnum{{{key}prose_upper}}{{{prose}}}"
        in report.decisions["D-X6-INTERVAL"].text
    )
    assert rf"\resultnum{{{key}i001}}" not in documents["sections/discussion.tex"]


def test_gate_citations_stay_in_validation_and_displays_control_numbering() -> None:
    _, documents = composed_documents("passed-shp")
    results = documents["sections/results.tex"]
    validation = results.split(r"\subsection{Validation gate}", 1)[1].split(
        r"\subsection", 1
    )[0]
    assert r"\ref{tab:v4-T3}" in validation
    assert r"\ref{fig:v4-F4}" in validation
    assert results.index(r"\input{generated/gate-outcomes}") < results.index(
        r"\input{generated/unit-status}"
    )
    counters = {"table": 0, "figure": 0}
    numbers = {}
    expanded = re.sub(
        r"\\input\{(generated/[^{}]+)\}",
        lambda match: (MANUSCRIPT / (match[1] + ".tex")).read_text(),
        results,
    )
    visible = "\n".join(line.split("%", 1)[0] for line in expanded.splitlines())
    for match in re.finditer(
        r"\\begin\{(table|figure)\*?\}|\\label\{((?:tab|fig):[^{}]+)\}", visible
    ):
        if match[1]:
            counters[match[1]] += 1
        else:
            kind = "table" if match[2].startswith("tab:") else "figure"
            numbers[match[2]] = counters[kind]
    for gate, inventory in (("tab:v4-T3", "tab:v4-T4"), ("fig:v4-F4", "fig:v4-F5")):
        assert results.index(r"\ref{" + gate + "}") < results.index(
            r"\ref{" + inventory + "}"
        )
        assert numbers[gate] < numbers[inventory]
    twin = documents["sections/supplement-exploratory-x3-x7.tex"].split(
        r"\paragraph{Twin and expanded-feature boundaries.}", 1
    )[1]
    labels = (
        "comparison-states",
        "boundary-comparisons",
        "stress-comparisons",
        "x1b-boundaries",
    )
    positions = [twin.index(r"\ref{tab:v4x-" + label + "}") for label in labels]
    assert positions == sorted(positions)


def test_interval_and_conservative_comparison_use_the_same_wilson_prose_endpoint() -> (
    None
):
    key = "v4x.x6.x6a.band.vs_d1.primary.wilson95."
    values = complete_values("passed-shp") | {
        "v4x.x6.x6a.band.vs_d1.primary.conservative": "true",
        key + "i000": "0.9900004",
        key + "prose_lower": "0.9900004",
        key + "i001": "0.999999",
        key + "prose_upper": "1.000",
    }
    report, documents = composed_documents("passed-shp", values)
    text = report.decisions["D-X6-CONSERVATIVE"].text
    endpoint = rf"\resultnum{{{key}prose_lower}}{{0.9900004}}"
    assert endpoint in text
    assert endpoint in report.decisions["D-X6-INTERVAL"].text
    assert rf"\resultnum{{{key}i000}}" not in documents["sections/discussion.tex"]
    assert text in documents["sections/discussion.tex"]


def test_x6_no_reading_states_the_d1_reference_once() -> None:
    _, documents = composed_documents("x6-no-reading")
    paragraph = (
        documents["sections/supplement-exploratory-x3-x7.tex"]
        .split(r"\paragraph{X6: no reading.}", 1)[1]
        .split(r"\paragraph", 1)[0]
    )
    assert "X6b D1" not in paragraph
    assert "against D1" in paragraph


@pytest.mark.parametrize("unfinished", [0, 1])
@pytest.mark.parametrize("controls_compared", [False, True])
def test_controls_caveat_requires_an_unfinished_unit_in_either_branch(
    unfinished: int, controls_compared: bool
) -> None:
    values = complete_values("passed-shp") | {
        "v4.inv.t3.n_incomplete": str(unfinished),
        "v4.t3.n_pairs_compared": str(int(controls_compared)),
        "v4.t3.n_obs_exceeds": str(int(controls_compared)),
        "v4.t3.n_channel_dependent": "0",
        "v4.t3.n_channel_not_assessed": "0",
    }
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    decision = report.decisions["B11" if controls_compared else "P7-c"]
    assert decision.state == "selected"
    assert ("Unfinished units are absent" in decision.text) == (unfinished > 0)


@pytest.mark.parametrize("missing_tier", [None, 4, 5, 6])
def test_sensitivity_caveat_requires_a_unit_outside_the_valid_inventory(
    missing_tier: int | None,
) -> None:
    values = complete_values("passed-shp") | {
        "v4.sens.use_b12": "1",
        **{
            f"v4.inv.t{tier}.n_valid": str(total - int(tier == missing_tier))
            for tier, total in ((4, 45), (5, 45), (6, 9))
        },
    }
    report = plan(values, {}, manuscript=MANUSCRIPT, facts=owner_facts("passed-shp"))
    decision = report.decisions["B12.inventory"]
    assert decision.state == "selected"
    assert ("Remaining units retain" in decision.text) == (missing_tier is not None)
