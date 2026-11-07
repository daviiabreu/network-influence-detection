T59 implements all four items in `batch-t59-spec.md` on
`fix/v4-t59-submission-structure-20261009`, based on `d60370f8`. Changes remain
uncommitted for the coordinator. No push, merge, real post-release chain,
simulation or model call was performed. The two handoff-runner tests blocked
by sandbox priority restrictions remain pending outside this sandbox.

`M/` below means `publications/jcss-manuscript/`, and all other file locators
are relative to `studies/ic-2026-2027/`. Scratch evidence paths are relative to
the authorized T59 scratch root named in the brief.

| Item | Change and locator | Kind | Verification |
| --- | --- | --- | --- |
| 1: order and numbering | `M/main.tex:114` places Appendix A before references; `:123` puts references before the entire supplementary block. `:125` flushes preceding floats, resets both counters and uses S-series numbers and guarded `supp.` hyperref anchors. Probes, conditional heading, every supplement include and the final clearpage follow the bibliography. | fixed | `tests/unit/test_v4_manuscript_assembly.py:617` checks all twelve compositions, the counter reset, anchor guards and unique insertion slot. Existing insertion and X7-order regressions pass. Final cached PDF compilation and visual inspection pass. |
| 1: citations and documentation | `M/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex:336,354,360` now identifies supplementary X5 and X6 tables. The existing Supplementary Table S1 call at `M/sections/methods.tex:112` is retained. `M/pipeline/ASSEMBLY.md:297` documents the new order, numbering and retained X7 move; the submission checklist update is at `M/pipeline/review/jcss-submission-checklist-2026-09-30.md:9`. | shell/docs | PDF calls render as Supplementary Table S1, S14, S16, S17, S26 and S29, and Supplementary Figs. S1–S4. The AUC translation remains main Table 1, including its Methods and Discussion calls. No existing `paper_check.py` rule assumes the former supplement order, so that checker is unchanged. |
| 2 | `M/sections/introduction.tex:42` removes “six-stage” from the gate-prerequisite sentence. `M/claim-evidence.md:500`, IN03, matches the new wording and distinguishes the five sealed stage records from G1a. Methods is otherwise unchanged. | fixed/ledger | Final PDF p3 contains the exact requested sentence; draft `paper_check` passes. |
| 3 | `M/references.bib:618` retains only the `doi` field in `shpgroup2026data`; its duplicate DOI URL field is removed. | fixed/bibliography | Final PDF p43, reference [59], contains `10.48573/haxy-c230` once, visually confirmed. Packaging and draft checker pass. |
| 4a | `tests/unit/conftest.py:49` verifies Wilson prose against the explicit unrounded aggregate endpoints, using three decimals unless an unequal endpoint rounds to a compared cut. Each additional decimal must be necessary; the first precision that separates all applicable cuts must be used. Exploratory fixture callers supply those endpoints at `tests/unit/test_v4_exploratory_export.py:536,727`. | test helper | `tests/unit/test_v4_exploratory_export.py:1340` covers the eight documented ordinary/boundary examples plus four rejected underprecision/overprecision examples. Existing numeric assertions and golden catalog pins are preserved. |
| 4b | `M/pipeline/drafts/2026-09-28/results-shells.tex:752` now ends the main-invalid/tier-valid explanation with “but both are required for comparing mechanisms.” | shell | The existing three-case permission regression at `tests/unit/test_v4_manuscript_assembly.py:2330` checks the changed Results wording while retaining the distinct Discussion and Conclusion wording. |

The repin receipt is `t59-shell-repin-receipt.json`; selection evidence is
`t59-selection-changes.json`. All 253 rule records, including conditions,
operations, bindings and locators, are unchanged. Only the results and
discussion source hashes change. Accepted visible spans are `B00`, `P6-a`,
`D-X5-POST` and `D-X6-DENOMINATORS`; `B00` overlaps the changed `P6-a` sentence.
All four shell pins and all 253 before/after span hashes were verified against
the base and current bytes. Rules SHA-256 changes from
`b4e040e7134eac51d731e47713f09f31f70b719f8706a16c83a0f17ba6c0a93d` to
`64ffae891b756b57f1743a760cec66f991340695d30bef76b3d91b13b3f065a1`.
The abstract and exploratory shells remain byte-identical; the existing T58
abstract budget remains valid, with a maximum mandatory composition of 250
words. All twelve synthetic cases compose with 150–250-word abstracts.

Validation used the direct study environment, without `uv` or network, with
all four required thread variables set to 1. Heavy commands requested
`nice -n 15`; the sandbox rejected the priority adjustment but the commands
ran. The results are:

| Check | Actual result |
| --- | --- |
| Structure/permission regressions before edits | 13 failed, 2 passed, 310 deselected; old ordering and main-invalid Results wording were reproduced. `structure-permission-red.log`. |
| New structure, permission and Wilson-proof regressions after edits | 27 passed, 380 deselected. |
| Focused batch | 866 passed, 2 failed in 281.92 s. `focused-tests.log`. |
| Final manuscript/placeholder/packaging rerun after restoring the main Table 1 citation | 397 passed in 15.82 s. `final-manuscript-tests.log`. Counts overlap the focused batch. |
| Ruff check and format check | Passed on all three edited Python files. |
| Mypy | Passed on all three edited Python files. |
| Diff, frozen closure and scope checks | `git diff --check` passed. No edited file belongs to the frozen code closure. Both exporters, the handoff runner and its tests are byte-identical to `d60370f8`. |

The focused batch ran `test_v4_manuscript_assembly.py`,
`test_paper_submission_placeholders.py`, `test_jcss_submission_package.py`,
`test_v4_exploratory_export.py`, `test_v4_public_aggregates.py`,
`test_release_handoff.py`, `test_v4_manuscript_assembly_derive.py`,
`test_v4_event_automation.py`, `test_v4_report_export.py` and
`test_v4_gate_only_shp.py`. This includes every test file found to reference
`main.tex`, the bibliography or the catalog-proof fixture.

The two failures are
`test_release_handoff.py::test_run_uses_the_durable_cache_and_the_cached_handoff_environment`
and `::test_run_reports_when_the_automation_writes_no_new_status`.
The unchanged `release_handoff.py:810` subprocess calls `lower_priority`
(`:752`) through `preexec_fn`. The sandbox denies its `os.setpriority` call,
raising `SubprocessError: Exception occurred in preexec_fn` before the fake
automation starts. An isolated call to the same priority-setting expression
also raises `PermissionError: [Errno 1] Operation not permitted`; evidence is
`priority-sandbox-probe.json`. No handoff code, test or priority assertion was
changed or bypassed. The coordinator must rerun these two tests in an
environment that permits process priority changes.

The final real-data rehearsal is a new scratch successor at `rehearsal-v2/`.
It uses only `release-handoff-20261008-t58/authorized/` and its associated
`owner-facts.json` as read-only inputs. The copied gate root was used only as
a program input; its raw contents were not listed, printed or inspected.
Derivation, assembly, exploratory export with `--fill`, the pinned Tectonic
0.17.0 with `--only-cached`, and draft `paper_check.py` all returned 0.
The supplied template class and bibliography style were copied into scratch.
`rehearsal-v2/commands.json` records exact commands and return codes; phase
logs, `closure-verification.json` and `pdf-verification.json` record the checks.
All 35,709 final catalog values exactly equal the authorized merged catalog.

The final PDF is `rehearsal-v2/manuscript-assembled/main.pdf`, SHA-256
`579367aaa1dbc2376c4b64832b54dd5099347e7377b42e5101b371169c6dff64`.
It has 95 pages. Appendix A begins on p28, references on p39, and Supplementary
Material on p44. Main floats are Tables 1–4 and Figs. 1–5; supplementary floats
are Tables S1–S29 and Figs. S1–S4. Continued tables preserve their S number
and have distinct destinations. The counter reset is after Appendix A and
references; this rehearsal contains no appendix float.

| Float | First rendered mention | Caption | Anchor |
| --- | --- | --- | --- |
| Main Table 1, AUC translation | p11 | p11 | `table.1` |
| Main Table 2, boundary records | p14 | p16 | `table.2` |
| Main Table 3 / Fig. 3, gate | p15 / p15 | p17 / p21 | `table.3` / `figure.3` |
| Main Table 4 / Fig. 4, inventory | p15 / p15 | p18 / p22 | `table.4` / `figure.4` |
| Supplementary Table S1, conventions | p10 | p45 | `table.supp.1` |
| Supplementary Table S14, X6 coverage | p27 | p73 | `table.supp.14` |
| Supplementary Tables S16/S17, X6 truth/precision | p27 | p75/p76 | `table.supp.16` / `table.supp.17` |
| Supplementary Tables S19/S20, X7 summary/boundaries | p58 | p80/p81 | `table.supp.19` / `table.supp.20` |
| Supplementary Table S26, X5 comparisons | p26 | p87 | `table.supp.26` |
| Supplementary Table S29, eligible domain | p20 | p95 | `table.supp.29` |
| Supplementary Figs. S1–S4, other-family profiles | p22 | p91–p94 | `figure.supp.1`–`figure.supp.4` |

Supplementary numbers follow display order within the supplement. Main-text
forward citations resolve to those S numbers, including the X6 tables cited
before the supplement's earlier X1a/X2 tables. Gate Table 3/Fig. 3 are cited
before inventory Table 4/Fig. 4 in the same Results page. The X1–X2 insertion
slot occurs once, and assembly still moves the X7 boundary include after the
X7 summary and before the post-release tables.

The PDF contains no “??”. The compiler output and final LaTeX log contain no
undefined reference/citation, duplicate hyperref destination, overfull box or
oversized-float warning. All 60 float destinations, including continued
parts, are distinct. Underfull-box warnings remain. Visual QA inspected
pages 3, 11, 27, 28, 43, 44, 45, 73, 81, 91 and 95: text, table captions,
plots, section transitions and numbering are legible, with no clipping or
overlap on those pages.

The Introduction on p3 reads: “The hash-bound validation gate is a
prerequisite for evaluation on reserved seeds.” Reference [59] on p43 reads:
“SHP Group: Living in Switzerland Waves 1–26 + Long File + Beta Version Wave
27. Version 12.0 [Data set], FORS data service (2026).
https://doi.org/10.48573/haxy-c230”. Its DOI appears once.

Draft `paper_check` reports 188 abstract words, six keywords, 61 cited keys,
80 bibliography entries and 5,704 bound IDs across 36 checked result files.
The existing AV03 placeholder remains permitted in draft mode. Full platform
and study integration gates, submission-mode validation, independent review
and scientific/editorial acceptance remain with the coordinator. No T59 item
was skipped; the two sandbox-blocked test results are explicitly outstanding.

Changed files, relative to the study:

- `publications/jcss-manuscript/claim-evidence.md`
- `publications/jcss-manuscript/main.tex`
- `publications/jcss-manuscript/pipeline/ASSEMBLY.md`
- `publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells.tex`
- `publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex`
- `publications/jcss-manuscript/pipeline/review/jcss-submission-checklist-2026-09-30.md`
- `publications/jcss-manuscript/pipeline/review/t59-report.md`
- `publications/jcss-manuscript/pipeline/review/t59-selection-changes.json`
- `publications/jcss-manuscript/pipeline/review/t59-shell-repin-receipt.json`
- `publications/jcss-manuscript/references.bib`
- `publications/jcss-manuscript/sections/introduction.tex`
- `src/ic_study/analysis/v4_manuscript_assembly_rules.json`
- `tests/unit/conftest.py`
- `tests/unit/test_v4_exploratory_export.py`
- `tests/unit/test_v4_manuscript_assembly.py`
