# Notes on the exploratory Results shells (2026-09-30)

Prepared at base `b6b0d107`, without opening any sealed or restricted input. The prose follows `pipeline/review/x3-x7-reading-restrictions-2026-09-29.md`; the older README labels are retained as machine labels alongside the restricted wording. No source, freeze, declaration, confirmatory shell or release runbook is changed. The shells are not connected to `main.tex`.

## Assembly and display

After release, aggregate at `3334ac0f` and build comparisons with `v4_exploratory_comparisons`. The exporter imports no X3–X7 aggregator and opens no store. The fixture envelope follows that commit; tests use its identical pure X3/X4/X6/X7 reading and summary functions or public-shape JSON. Synthetic output remains marked in JSON and in every generated table caption.

Copy applicable paragraphs and their table inputs to a manuscript copy. Omit zero-count branches and apply the conditions in the comments. The rehearsal includes every option only to test bindings and layout. For an unavailable D1 truth, remove references to its absent coverage numerator/denominator and select the unavailable-truth paragraph. The exporter refuses an unresolved manuscript ID instead of replacing it with zero.

Finite floats display six significant digits; integers remain exact. Machine readings are copied and are never recalculated from rounded values. JSON null displays `unavailable`; its interpretation still comes from the adjacent state, reason and censoring fields. An absent table field uses a distinct `v4x.unavailable.*` ID, so it does not fabricate a scientific estimate or denominator. First-boundary interval endpoints without a finite value require their accompanying censoring record; they must not be read as zero. States and counts are bound just like estimates.

`--catalog` is the complete map, including JSON Pointers and explicit count derivations. `--values` is the exact subset used by the input tree. `--confirmatory-values` merges a confirmatory values/catalog file and rejects every collision, including equal-valued collisions. A mixed synthetic export remains synthetic in its values record. Comparison provenance, when supplied, must bind the exact X3/X4 input bytes.

Incomplete indices at the declared operational cut are reportable only when all declared indices/jobs are accounted for by recorded plus incomplete records. Missing unaccounted cells/jobs, duplicate identities, incomplete X6 grids, invalid coverage denominators and readings below the declared complete-repetition minimum are rejected. Recorded jobs include independent truth jobs; they are not coverage repetitions. Error and gap counts are distinct. X6a without-curve repetitions and errors are reported outside the computed coverage denominators.

## Coordinator choices

The coordinator chooses the assembly destination and integrates the supplement after release; these drafts remain disconnected. Retain the conditional wording and select branches from the original machine state, including partial/unavailable comparisons. Normal-reference counts use only the declaration's reference-AUC range from the aggregate; all original per-cell readings remain available in the table and catalog. X6 reading counts count tabulated D1 references (including the separately labelled primary and gaps-as-misses references), never independent repetitions or pooled cells.

Choose whether the full per-cell/diagnostic tables remain in the typeset supplement or move to an electronic resource before assembly; update the references consistently and regenerate the exact used-ID values file. The current draft includes the complete tables, split into successive floats with fixed filenames. Choose any narrative examples by a rule fixed before reading outcomes; none is preselected here. A claim of demonstrated free-share infeasibility would need a bound/proof for the actual target and domain; these shells supply only search/validation wording and do not add such a claim. The coordinator also supplies the existing author, availability and other editorial fields; the synthetic submission check deliberately retains those placeholders.

No numerical threshold, estimand, seed, execution window, retry rule or scientific reading is left for an exporter decision. The export does not validate scientific closure or authorize submission.

## Source of every prose ID

Paths refer to the public aggregate JSONs or the fixed declaration. Counts use only recorded fields and keep the specified conditioning. The runtime catalog binds the input SHA-256 and the exact pointer/derivation for each generated-table ID as well.

| ID | Input | Source field or derivation |
| --- | --- | --- |
| `v4x.comparisons.count.x1b.available` | `comparisons` | `count /by_r/x1b/state=disponível` |
| `v4x.comparisons.count.x1b.unavailable` | `comparisons` | `count /by_r/x1b/state=indisponível` |
| `v4x.comparisons.count.x3.available` | `comparisons` | `count /by_r/x3/state=disponível` |
| `v4x.comparisons.count.x3.unavailable` | `comparisons` | `count /by_r/x3/state=indisponível` |
| `v4x.comparisons.count.x4.available` | `comparisons` | `count /by_r/x4/state=disponível` |
| `v4x.comparisons.count.x4.partial` | `comparisons` | `count /by_r/x4/state=parcial` |
| `v4x.comparisons.count.x4.unavailable` | `comparisons` | `count /by_r/x4/state=indisponível` |
| `v4x.comparisons.count.x5.equivalent.above-grid` | `comparisons` | `count X5 condition/r entries with /equivalent_strength/state=acima da grade` |
| `v4x.comparisons.count.x5.equivalent.available` | `comparisons` | `count X5 condition/r entries with /equivalent_strength/state=disponível` |
| `v4x.comparisons.count.x5.equivalent.censored` | `comparisons` | `count X5 condition/r entries with /equivalent_strength/state=censurada` |
| `v4x.comparisons.count.x5.equivalent.unavailable` | `comparisons` | `count X5 condition/r entries with /equivalent_strength/state=indisponível` |
| `v4x.comparisons.count.x5.interval.above` | `comparisons` | `count X5 condition/r entries with /interval_comparison/relation=acima` |
| `v4x.comparisons.count.x5.interval.below` | `comparisons` | `count X5 condition/r entries with /interval_comparison/relation=abaixo` |
| `v4x.comparisons.count.x5.interval.overlap` | `comparisons` | `count X5 condition/r entries with /interval_comparison/relation=sobrepõe` |
| `v4x.comparisons.count.x5.interval.unavailable` | `comparisons` | `count X5 condition/r entries with /interval_comparison/relation=None` |
| `v4x.protocol.grid_strengths` | `declaration` | `length of frozen GRID` |
| `v4x.protocol.target` | `declaration` | `declaration /x3_free_signal_share_null/reading/lost_crossing` |
| `v4x.protocol.x4.level` | `declaration` | `declaration /x4_single_panel_power/x4b/rule` |
| `v4x.protocol.x6.conservative` | `declaration` | `declaration /x6_interior_coverage/reading/conservative` |
| `v4x.protocol.x6.failure` | `declaration` | `declaration /x6_interior_coverage/reading/failure_of_interior_inference` |
| `v4x.protocol.x6.nominal` | `declaration` | `declaration /x6_interior_coverage/reading/adequate` |
| `v4x.protocol.zero` | `declaration` | `first frozen GRID entry` |
| `v4x.x3.count.against-objection` | `x3` | `count /cells with reading/status=against-objection` |
| `v4x.x3.count.error` | `x3` | `count /cells with reading/status=error` |
| `v4x.x3.count.free-gap` | `x3` | `count /cells with reading/status=free-gap` |
| `v4x.x3.count.gap` | `x3` | `count /cells with reading/status=gap` |
| `v4x.x3.count.inconclusive` | `x3` | `count /cells with reading/status=inconclusive` |
| `v4x.x3.count.lost_crossing` | `x3` | `count /cells/lost_crossing=true` |
| `v4x.x3.count.supports-objection` | `x3` | `count /cells with reading/status=supports-objection` |
| `v4x.x3.errors` | `x3` | `count of errors records; errors and gaps are distinct` |
| `v4x.x3.gaps` | `x3` | `count of gaps records; errors and gaps are distinct` |
| `v4x.x3.incomplete` | `x3` | `count of incomplete records; errors and gaps are distinct` |
| `v4x.x3.recorded` | `x3` | `count of recorded records; errors and gaps are distinct` |
| `v4x.x3.sizes.matching` | `x3` | `/sizes/matching` |
| `v4x.x3.sizes.retry_matching` | `x3` | `/sizes/retry_matching` |
| `v4x.x3.summary.margin` | `x3` | `/summary/margin` |
| `v4x.x4.sizes.analyst` | `x4` | `/sizes/analyst` |
| `v4x.x4.sizes.check` | `x4` | `/sizes/check` |
| `v4x.x4.sizes.nulls` | `x4` | `/sizes/nulls` |
| `v4x.x4.summary.single_panel_effect.margin` | `x4` | `/summary/single_panel_effect/margin` |
| `v4x.x4a.count.calibrated` | `x4` | `count /summary/size_at_a0/x4a=calibrated` |
| `v4x.x4a.count.conservative` | `x4` | `count /summary/size_at_a0/x4a=conservative` |
| `v4x.x4a.count.describes` | `x4` | `count /x4a/normal_theory_reading=describes; within /summary/normal_theory_in_auc_range/range` |
| `v4x.x4a.count.liberal` | `x4` | `count /summary/size_at_a0/x4a=liberal` |
| `v4x.x4a.count.overstates` | `x4` | `count /x4a/normal_theory_reading=overstates; within /summary/normal_theory_in_auc_range/range` |
| `v4x.x4a.count.understates` | `x4` | `count /x4a/normal_theory_reading=understates; within /summary/normal_theory_in_auc_range/range` |
| `v4x.x4a.errors` | `x4` | `count of errors records; errors and gaps are distinct` |
| `v4x.x4a.gaps` | `x4` | `count of gaps records; errors and gaps are distinct` |
| `v4x.x4a.incomplete` | `x4` | `count of incomplete records; errors and gaps are distinct` |
| `v4x.x4a.recorded` | `x4` | `count of recorded records; errors and gaps are distinct` |
| `v4x.x4b.count.calibrated` | `x4` | `count /summary/size_at_a0/x4b=calibrated` |
| `v4x.x4b.count.conservative` | `x4` | `count /summary/size_at_a0/x4b=conservative` |
| `v4x.x4b.count.inconclusive` | `x4` | `count /x4b/single_panel_reading=inconclusive; recorded non-null readings with their original size conditioning` |
| `v4x.x4b.count.liberal` | `x4` | `count /summary/size_at_a0/x4b=liberal` |
| `v4x.x4b.count.no-material-change` | `x4` | `count /x4b/single_panel_reading=no-material-change; recorded non-null readings with their original size conditioning` |
| `v4x.x4b.count.removes-power` | `x4` | `count /x4b/single_panel_reading=removes-power; recorded non-null readings with their original size conditioning` |
| `v4x.x4b.errors` | `x4` | `count of errors records; errors and gaps are distinct` |
| `v4x.x4b.gaps` | `x4` | `count of gaps records; errors and gaps are distinct` |
| `v4x.x4b.incomplete` | `x4` | `count of incomplete records; errors and gaps are distinct` |
| `v4x.x4b.recorded` | `x4` | `count of recorded records; errors and gaps are distinct` |
| `v4x.x6.minimum_complete_repetitions` | `x6` | `/minimum_complete_repetitions` |
| `v4x.x6.sizes.population_pairs` | `x6` | `/sizes/population_pairs` |
| `v4x.x6.truth_se_target` | `x6` | `/truth_se_target` |
| `v4x.x6.x6a.band.vs_d1.gaps_as_misses.covered` | `x6` | `/x6a/band/vs_d1/gaps_as_misses/covered` |
| `v4x.x6.x6a.band.vs_d1.gaps_as_misses.total` | `x6` | `/x6a/band/vs_d1/gaps_as_misses/total` |
| `v4x.x6.x6a.band.vs_d1.primary.covered` | `x6` | `/x6a/band/vs_d1/primary/covered` |
| `v4x.x6.x6a.band.vs_d1.primary.total` | `x6` | `/x6a/band/vs_d1/primary/total` |
| `v4x.x6.x6a.count.adequate` | `x6` | `count D1 coverage references in x6a; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6a.count.conservative` | `x6` | `count D1 coverage references with conservative=true in x6a` |
| `v4x.x6.x6a.count.failure` | `x6` | `count D1 coverage references in x6a; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6a.count.inconclusive-truth-precision` | `x6` | `count D1 coverage references in x6a; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6a.count.no-reading` | `x6` | `count D1 coverage references in x6a; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6a.count.subnominal` | `x6` | `count D1 coverage references in x6a; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6a.incomplete` | `x6` | `length /incomplete_units` |
| `v4x.x6.x6a.recorded` | `x6` | `/x6a/recorded` |
| `v4x.x6.x6a.repetitions.errors` | `x6` | `/x6a/repetitions/errors` |
| `v4x.x6.x6a.units` | `x6` | `/x6a/units` |
| `v4x.x6.x6a.without_curve` | `x6` | `/x6a/repetitions/recorded minus /x6a/band/with_curve` |
| `v4x.x6.x6b.count.adequate` | `x6` | `count D1 coverage references in x6b; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6b.count.conservative` | `x6` | `count D1 coverage references with conservative=true in x6b` |
| `v4x.x6.x6b.count.failure` | `x6` | `count D1 coverage references in x6b; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6b.count.inconclusive-truth-precision` | `x6` | `count D1 coverage references in x6b; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6b.count.no-reading` | `x6` | `count D1 coverage references in x6b; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6b.count.subnominal` | `x6` | `count D1 coverage references in x6b; primary and gaps-as-misses separately tabulated` |
| `v4x.x6.x6b.incomplete` | `x6` | `length /incomplete_units` |
| `v4x.x6.x6b.recorded` | `x6` | `/x6b/recorded` |
| `v4x.x6.x6b.units` | `x6` | `/x6b/units` |
| `v4x.x7.bootstrap.margin` | `x7` | `/bootstrap/margin` |
| `v4x.x7.count.censored` | `x7` | `count /units with reading/status=censored` |
| `v4x.x7.count.close` | `x7` | `count /units with reading/status=close` |
| `v4x.x7.count.far` | `x7` | `count /units with reading/status=far` |
| `v4x.x7.count.incomplete` | `x7` | `count /units with reading/status=incomplete` |
| `v4x.x7.count.inconclusive` | `x7` | `count /units with reading/status=inconclusive` |
| `v4x.x7.count.invalid` | `x7` | `count /units with reading/status=invalid` |
| `v4x.x7.count.unavailable` | `x7` | `count /units with reading/status=unavailable` |
| `v4x.x7.inventory.errors` | `x7` | `count of errors records; errors and gaps are distinct` |
| `v4x.x7.inventory.gaps` | `x7` | `count of gaps records; errors and gaps are distinct` |
| `v4x.x7.inventory.incomplete` | `x7` | `count of incomplete records; errors and gaps are distinct` |
| `v4x.x7.inventory.recorded` | `x7` | `count of recorded records; errors and gaps are distinct` |

## Generated table IDs

Every table cell uses the same catalog as the prose. `rNNN` is the reliability multiplied by one hundred, `aNNNN` is strength multiplied by ten thousand, and `iNNN` is the original list position for intervals, attempts and arrays. X5 additionally carries its channel name to prevent collisions between conditions in the same cell. These are identifiers, not new measurements.

| ID family | Original source |
| --- | --- |
| `v4x.x3.cells.r*.a*.*` | X3 `cells[]`: cell identity, known/free estimates, paired delta, means, both recorded attempt objects and last `free_status` |
| `v4x.x4.x4a.r*.a*.*`, `v4x.x4.x4b.r*.a*.*` | X4 `x4a[]` and `x4b[]`: original statistics, panel denominators, intervals, failures, paired difference, calibration flags and machine quantity; raw per-panel records are not exported |
| `v4x.x4.x4b.r*.a*.successful_panels` | `test_panels - fit_failures`, the denominator of the original success-conditioned reference |
| `v4x.x4.summary.*` | X4 original size flags, normal-theory AUC-range summary and single-panel-effect summary |
| `v4x.x6.x6a.*`, `v4x.x6.x6b.*` | X6 original job inventory, band, strengths/cells, D1/pop truths, MC errors, retry fractions, complete/gap/error counts, Wilson intervals, precision sensitivity, standardized errors and matching-bias summaries |
| `v4x.x7.units.r*.*`, `v4x.x7.cells.r*.a*.*` | X7 first/sustained boundaries for both arms, inverted intervals, point/interval censoring, gate validity, paired deltas, errors and rich numerical gaps |
| `v4x.comparisons.by_r.*` | Comparisons `by_r`: released main status/global validity, X1b first/sustained boundaries, X3 selected-cell contrast, P_or/P_pu and local calibration, X5 equivalent strength and interval relation with original reasons |
| `v4x.unavailable.*` | A requested display field absent from its original object, explicitly labelled unavailable; the scientific field itself is not added |

The post-release boundary display joins X7 by r from `x7.json`; X7 is not an input to the comparisons module. Its paired frozen-feature reference uses the same exploratory seeds as its expanded-feature curve; it is not paired with the confirmatory release. X1b and X7 keep their own intervals/censoring in the catalog and tables, without an added between-curve test.

## Verification record

The first test failed on the absent exporter module. Denominator/merge tests then failed before their implementation. Byte-provenance, bound-unavailability, the declared normal-reference AUC range and TeX control-word separation also showed their expected red before correction. Rehearsal commands and focused quality gates are in the new section of `experiments/exploratory/detection-boundary-v4-exploratory/POST-RELEASE.md`. All synthetic artifacts are external to Git.

The final synthetic rehearsal generated 23 fixed-name table files and compiled with the local Springer class into 85 pages. It bound 4,587 distinct IDs: 3,707 exploratory IDs and 880 confirmatory IDs. All 99 distinct prose IDs have explicit sources above. There were zero unresolved `resultnum` slots and three existing editorial placeholders. The draft `paper_check` passed (exit zero); `--submission` failed (exit one) only at `main.tex:26`, `main.tex:91` and `sections/conclusion.tex:1`. This is a mechanical rehearsal that includes every prose option, including zero-count options, and cannot serve as a scientific supplement or submission.

Ruff check and format check passed for the two Python files. Mypy passed on 106 source files. The new exporter tests and the existing comparisons/report-export tests passed together: 81 tests, without xdist, in one sequential parent process with all four requested numerical thread limits set to one. X3–X7 module hashes were unchanged, X3/X4/X6/X7 remained byte-identical to `3334ac0f`, and all 80 frozen Python sources still matched `freeze-v4.json`. The protected declaration, freeze, README, confirmatory shells, release runbook and `main.tex` remained unchanged. No full suite or commit was run.

The rehearsal directory is `/private/tmp/exploratory-shells-rehearsal.8ws8rj`; it contains the input aggregates, merged catalog/values, PDF, checker logs and `counts.json`. Focused gate output is `/private/tmp/exploratory-shells-final-gates.log`. The final LaTeX log contains no overfull box, oversized float or undefined-reference warning. Rendered examples of X3, X4 calibration, X6 coverage/diagnostics, X7 boundaries and post-release states/stress tables were inspected without clipping or overlap. These temporary artifacts may be removed after review; the commands above reproduce them.
