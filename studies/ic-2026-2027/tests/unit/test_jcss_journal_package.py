"""The journal kit preserves TeX spacing and resolves external dependencies."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

JOURNAL = Path(__file__).resolve().parents[2] / "publications/jcss-journal"
sys.path.insert(0, str(JOURNAL))
import package as journal_package  # noqa: E402

MACROS = (
    r"\newcommand{\resultnum}[2]{#2}"
    "\n"
    r"\newcommand{\resultplural}[3]{#3}"
    "\n"
)


class FlattenTests(unittest.TestCase):
    def flatten(self, body: str) -> tuple[str, journal_package.Counts]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "main.tex").write_text(MACROS + body)
            (root / "display.tex").write_text(
                r"Value \resultnum{toy.key}{0.70}; \resultplural{n}{item}{items}."
            )
            aux = root / "esm.aux"
            aux.write_text(r"\newlabel{tab:toy}{{S12}{4}{Nested {caption}}{}{}}")
            counts = journal_package.Counts()
            text = journal_package.flatten(
                root, journal_package.aux_labels(aux), counts
            )
            return text, counts

    def test_guard_input_labels_and_result_macros(self) -> None:
        text, counts = self.flatten(
            r"\usepackage{xr-hyper}"
            "\n"
            r"\externaldocument[esm-]{esm}"
            "\n"
            r"\IfFileExists{display.tex}{\input{display}}{}"
            "\n"
            r"Table~\ref{esm-tab:toy}; \hyperref[esm-tab:toy]{the table}."
        )
        self.assertIn("Value 0.70; items.", text)
        self.assertIn("Table~S12; the table.", text)
        for removed in ("\\input", "IfFileExists", "externaldocument", "xr-hyper"):
            self.assertNotIn(removed, text)
        self.assertEqual(counts.esm_refs, 2)

    def test_comment_rules_and_protected_text(self) -> None:
        body = (
            "  % internal record\n"
            "text % removable comment\n"
            "token%suppresses space\n"
            r"escaped \% remains"
            "\n"
            r"\url{https://example.org/a%20b}"
            "\n"
            r"\code{https://example.org/a % b}"
            "\n"
            r"\verb|a % b|"
            "\n"
            "\\begin{verbatim}\n% verbatim\n\\input{missing}\n\\end{verbatim}\n"
        )
        text, counts = self.flatten(body)
        self.assertNotIn("internal record", text)
        self.assertNotIn("removable comment", text)
        self.assertIn("token%suppresses space\n", text)
        self.assertIn(r"escaped \% remains", text)
        self.assertIn(r"\url{https://example.org/a%20b}", text)
        self.assertIn(r"\code{https://example.org/a % b}", text)
        self.assertIn(r"\verb|a % b|", text)
        self.assertIn("% verbatim\n\\input{missing}", text)
        self.assertEqual(counts.comments, 2)

    def test_missing_guarded_input_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing"):
            self.flatten(r"\IfFileExists{missing.tex}{\input{missing}}{}")

    def test_missing_external_label_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing ESM label"):
            self.flatten(r"\ref{esm-absent}")

    def test_nested_inputs_and_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "main.tex").write_text(MACROS + r"\input{child}")
            (root / "child.tex").write_text(r"\input{display}")
            (root / "display.tex").write_text("nested")
            self.assertIn(
                "nested", journal_package.flatten(root, {}, journal_package.Counts())
            )
            (root / "display.tex").write_text(r"\input{main}")
            with self.assertRaisesRegex(ValueError, "cycle"):
                journal_package.flatten(root, {}, journal_package.Counts())

    def test_changed_result_macro_definition_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "main.tex").write_text(MACROS.replace("{#2}", "{#1}"))
            with self.assertRaisesRegex(ValueError, "resultnum definition"):
                journal_package.flatten(root, {}, journal_package.Counts())

    def test_comments_after_tokens_are_not_executed(self) -> None:
        text, _ = self.flatten("x%\\input{missing}\n" + r"\input{display}")
        self.assertIn("x%\\input{missing}\n", text)
        self.assertIn("Value 0.70", text)

    def test_real_auxiliary_preamble_is_not_a_label(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            aux = Path(temporary) / "esm.aux"
            aux.write_text(
                r"\let\oldnewlabel\newlabel"
                "\n"
                r"\gdef\newlabel#1#2{\newlabelxx{#1}#2}"
                "\n"
                r"\newlabel{sec:toy}{{S3.2}{8}{Caption}{}{}}"
            )
            self.assertEqual(journal_package.aux_labels(aux), {"sec:toy": "S3.2"})

    def test_existing_output_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            sentinel = out / "sentinel"
            sentinel.write_text("preserve")
            with self.assertRaisesRegex(ValueError, "already exists"):
                journal_package.assemble(out / "absent-build", out)
            self.assertEqual(sentinel.read_text(), "preserve")

    def test_portal_fields_allow_pdf_wraps_but_reject_changed_content(self) -> None:
        field = "standard-error components and simulated panels at 0.70"
        pdf = "standard-\nerror components and sim-\nulated panels\n18\fat 0.70"
        self.assertTrue(journal_package.field_matches(field, pdf))
        self.assertFalse(
            journal_package.field_matches(field.replace("0.70", "0.71"), pdf)
        )
        self.assertFalse(
            journal_package.field_matches(field.replace("simulated", "real"), pdf)
        )
        self.assertFalse(journal_package.field_matches("10-11", "1011"))


if __name__ == "__main__":
    unittest.main()
