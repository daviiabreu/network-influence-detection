"""Submission checks use artificial manuscript text and no scientific runs."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest

CHECKER = (
    Path(__file__).resolve().parents[2]
    / "publications/jcss-manuscript/pipeline/paper_check.py"
)


@pytest.fixture
def checker(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spec = importlib.util.spec_from_file_location("paper_check", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "pdf_metrics", lambda _pdf: (1, 6000))
    return module


@pytest.fixture
def manuscript(tmp_path: Path) -> Path:
    (tmp_path / "sections").mkdir()
    (tmp_path / "main.tex").write_text(
        "\\abstract{" + " ".join(["design"] * 150) + "}\n"
        "\\keywords{one,two,three,four}\n"
        "Data and code availability\n"
        "\\subsection{Use of generative AI}\n"
        "Other declarations\n"
        "\\input{sections/results}\n"
        "\\input{sections/discussion}\n"
        "\\input{sections/declarations}\n",
        encoding="utf-8",
    )
    (tmp_path / "sections/results.tex").write_text(
        "\\resultnum{synthetic.example}{0.7}\n", encoding="utf-8"
    )
    for name in ("discussion", "declarations"):
        (tmp_path / f"sections/{name}.tex").write_text("", encoding="utf-8")
    (tmp_path / "references.bib").write_text("", encoding="utf-8")
    (tmp_path / "values.json").write_text(
        json.dumps({"synthetic": True, "values": {"synthetic.example": "0.7"}}),
        encoding="utf-8",
    )
    return tmp_path


def check(checker: ModuleType, root: Path, *, submission: bool = True) -> list[str]:
    return cast(
        list[str],
        checker.check(
            "jcss", root / "artificial.pdf", root, root / "values.json", submission
        ),
    )


def test_nested_caption_reference_does_not_hide_numbers_outside_the_caption(
    checker: ModuleType, manuscript: Path
) -> None:
    (manuscript / "sections/results.tex").write_text(
        r"\caption{Grid limit $>0.9$; Table~\ref{tab:synthetic2}. "
        "(continued, part 2 of 2)}\n"
        r"\resultnum{synthetic.example}{0.7}"
        "\nAn unbound result is 0.8.\n"
    )
    assert check(checker, manuscript) == [
        "sections/results.tex:3: unbound result number 0.8"
    ]


@pytest.mark.parametrize(
    "marker",
    [
        "[to be filled from the validated final package]",
        "[TO BE FILLED after verification]",
        "[to\nbe filled after verification]",
        "[ OWNER : verified author contributions]",
        "[owner:\nverified funding]",
        "[Insert verified availability]",
        "[Generated values pending release]",
        "[data location pending]",
        "[code release pending]",
        "[run and figure manifests pending]",
        r"\placeholder{verified facts}",
        "TODO",
        "FIXME",
        "TBD",
    ],
)
@pytest.mark.parametrize(
    "relative", ["main.tex", "sections/discussion.tex", "sections/declarations.tex"]
)
def test_submission_rejects_editorial_facts_in_reachable_sources(
    checker: ModuleType, manuscript: Path, marker: str, relative: str
) -> None:
    path = manuscript / relative
    with path.open("a", encoding="utf-8") as stream:
        stream.write("\n" + marker + "\n")
    errors = check(checker, manuscript)
    assert len(errors) == 1
    assert errors[0].startswith(relative + ":")
    assert errors[0].endswith(": unresolved placeholder")
    assert check(checker, manuscript, submission=False) == []


@pytest.mark.parametrize(
    "text",
    [
        r"$r \in [0,1]$ and $[a,b]$, $[0.57,0.64]$, $[>0.9,\infty)$.",
        r"\[a^*(r) = \inf\{a: A(a,r) \geq 0.70\}\]",
        r"\cite[pp. 2--3]{reference} and references [1, 2, 3].",
        "[unavailable: no D1 truth] [not attained] [censored by gap]",
        "% [OWNER: comment only]\n  % [to be filled comment only]",
        "Verified declaration. % [to be filled comment only]",
        r"Verified declaration. \\% [OWNER: comment after a line break]",
    ],
)
def test_legitimate_brackets_and_comments_do_not_block_submission(
    checker: ModuleType, manuscript: Path, text: str
) -> None:
    (manuscript / "sections/discussion.tex").write_text(text, encoding="utf-8")
    (manuscript / "references.bib").write_text(
        "@article{reference, title={Artificial reference}}", encoding="utf-8"
    )
    assert check(checker, manuscript) == []


def test_escaped_percent_does_not_hide_editorial_placeholder(
    checker: ModuleType, manuscript: Path
) -> None:
    (manuscript / "sections/declarations.tex").write_text(
        r"A 95\% statement [OWNER: verify].", encoding="utf-8"
    )
    assert check(checker, manuscript) == [
        "sections/declarations.tex:1: unresolved placeholder"
    ]


def test_nested_include_is_checked_but_disconnected_draft_is_not(
    checker: ModuleType, manuscript: Path
) -> None:
    (manuscript / "draft.tex").write_text("[OWNER: disconnected]", encoding="utf-8")
    (manuscript / "sections/discussion.tex").write_text(
        "\\include{sections/nested}\n", encoding="utf-8"
    )
    (manuscript / "sections/nested.tex").write_text(
        "% comment\n[to be filled after verification]\n", encoding="utf-8"
    )
    assert check(checker, manuscript) == [
        "sections/nested.tex:2: unresolved placeholder"
    ]


def test_commented_inputs_do_not_open_unreachable_resources(
    checker: ModuleType, manuscript: Path
) -> None:
    (manuscript / "sections/discussion.tex").write_text(
        "% \\input{missing}\nVerified. % \\include{missing}\n",
        encoding="utf-8",
    )
    assert check(checker, manuscript) == []


@pytest.mark.parametrize("name", ["missing", "../outside"])
def test_reachable_resource_must_exist_inside_manuscript(
    checker: ModuleType, manuscript: Path, name: str
) -> None:
    (manuscript / "sections/discussion.tex").write_text(
        f"\\include{{{name}}}\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="missing or outside manuscript"):
        check(checker, manuscript)


def test_result_binding_rule_is_preserved(
    checker: ModuleType, manuscript: Path
) -> None:
    assert check(checker, manuscript) == []
    results = manuscript / "sections/results.tex"
    results.write_text("\\resultnum{synthetic.example}{0.7}\n0.8\n", encoding="utf-8")
    assert check(checker, manuscript) == [
        "sections/results.tex:2: unbound result number 0.8"
    ]
    results.write_text("\\resultnum{synthetic.example}{0.8}\n", encoding="utf-8")
    assert check(checker, manuscript) == [
        "sections/results.tex: synthetic.example shows 0.8, expected 0.7"
    ]
    assert checker.result_consistency(
        manuscript, checker.tex_sources(manuscript), None, True
    ) == ["result values JSON is required for submission"]


def test_abstract_counts_the_visible_value_of_each_bound_number(
    checker: ModuleType, manuscript: Path
) -> None:
    key = "v4.abstract.count.of.shares"
    main = manuscript / "main.tex"
    main.write_text(
        main.read_text(encoding="utf-8").replace(
            " ".join(["design"] * 150),
            " ".join(["design"] * 249) + f" \\resultnum{{{key}}}{{7}}",
        ),
        encoding="utf-8",
    )
    values = json.loads((manuscript / "values.json").read_text(encoding="utf-8"))
    values["values"][key] = "7"
    (manuscript / "values.json").write_text(json.dumps(values), encoding="utf-8")
    assert check(checker, manuscript) == []
