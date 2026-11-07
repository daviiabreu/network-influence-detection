# Notes on the Results shells (2026-09-28)

Companion to `results-shells.tex`, `results-shells-ledger.md` and `results-shells-abstract.md`. Written while the v4 gate and the confirmatory tiers were still running. No result was seen, assumed or simulated. Paths are relative to `studies/ic-2026-2027/` unless they start with `pipeline/` or `sections/`, which are relative to `publications/jcss-manuscript/`.

The notes have four parts:

1. questions for the Owner, where the frozen rules do not fix the wording;
2. fields that a branch needs but that the release or other records do not carry;
3. mechanical and consistency issues;
4. the map from each result ID to its source field.

Each question states the choice the shell makes now, so the shell is usable if the Owner agrees. The Owner should answer every question **before** any result is opened. An answer given after the results would re-open the choice this exercise is meant to fix.

## 1. Questions for the Owner

**Q1. Venue and form of a gate-failure paper (branches B1b-\*, B1c, B1d).** **Resolved: decision 99; see [Coordinator decisions of 2026-09-30, before the G2 outcome](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-before-the-g2-outcome).** Integration log §8 defers Q10 until a gate outcome exists. Deciding after the outcome is known is exactly what pre-writing is meant to avoid. The shell writes the Results the same way for any venue. Will a gate-failure paper go to JCSS, JASSS or a methods note?

**Q2. The rest of the abstract after a gate failure.** **Resolved: decision 99; see [Coordinator decisions of 2026-09-30, before the G2 outcome](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-before-the-g2-outcome).** `results-shells-abstract.md` removes three passages and adds a gate sentence plus a closing sentence. The remaining abstract still describes the estimand and the curve as the design. Is that acceptable, or is the abstract rewritten as a report of a failed validation? The frozen rules say nothing about this.

**Q3. Gate unfinished at the close (B1d).** **Resolved: decision 99; see [Coordinator decisions of 2026-09-30, before the G2 outcome](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-before-the-g2-outcome).**

- The frozen documents set the close for the tiers: SPEC D9, AMD lines 257–262.
- They require every stage to pass before any confirmatory seed: SPEC D7.
- They do not say how to report a gate that is still running at the close, or whether it may continue afterwards.

The shell reports it as unfinished, with the stage and task counts, and says that no tier ran. Is that the intended reading? May the gate continue after the close without any confirmatory tier?

**Q4. Is the waste-guard stop a gate failure (B1c)?** **Resolved: decision 99; see [Coordinator decisions of 2026-09-30, before the G2 outcome](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-before-the-g2-outcome).**

- DRD "Correction to item 2" calls the guard an economy rule. The gate's own criteria carry validity.
- T3 prints the stop with verdict "fail".
- SPEC D7 ("Failure means documentation plus a new amendment") does not name the stop.

The shell says the stop is final under this freeze, because the bound records cannot change (RS02). It does not call the stop a failure of the bands. Confirm, or give the wording.

**Q5. Unsealing when no confirmatory result exists (B1b-G2, B1b-G2c).** **Resolved: decision 99; see [Coordinator decisions of 2026-09-30, before the G2 outcome](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-before-the-g2-outcome).** SPEC D7 opens the sealed G2 and G2c records "only after the confirmatory results are committed". If G2 or G2c fails, no confirmatory result will ever exist. The shell reports criteria only and leaves the records sealed. Should the sealed per-repetition values ever be released in that case, for example in a successor's exposure record?

**Q6. Secondary targets 0.60 and 0.80 (B03, and possibly P5).** **Resolved: decision 91 at `44b722dd`; section 8 governs.**

- v1 registers them as secondary: "Pergunta e estimandos", lines 50–51.
- The frozen `curve_report` emits boundaries only for 0.70.
- `report/README.md` says they can be derived from the released bands, with the frozen inversion and the gap-censoring replay, but "that needs a decision".

The B03 sentence is included only if the answer is yes. Should the paper report them? If so, only in B03, as the risk register suggests, or in every branch?

**Q7. The SHP anchor in a gate-failure paper.** **Resolved: decision 99; see [Coordinator decisions of 2026-09-30, before the G2 outcome](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-before-the-g2-outcome).**

- The SHP preregistration says the analysis is independent of the gate.
- It places the anchor on the v4 curve.
- F6 cannot render without a release.

The gate branches do not mention the anchor. Should a gate-failure paper report the anchor in its own section, without a curve, or omit it?

**Q8. What "tier 2 complete and valid" means for the headline (RS33, P6).** **Resolved: decision 91 at `44b722dd`; section 8 governs.** M79 pre-commits B and D side by side "whenever tier 2 is complete and valid". The frozen basis requires "grades completas e válidas dos nulos pertinentes": AMD lines 191–192 and SPEC D9. The shell applies the B/D reading **per r**, at every r where both units are `completo válido` **and** gap-free (`band_complete == true`). The reasoning is that a complete grid has no gap. The side-by-side sentence is written whenever at least one such r exists. The alternatives are to require all 36 tier-2 units, or all nine D units, to be complete valid. Which reading is intended?

**Q9. Row 4 thresholds and a\*=0 (B04).** **Resolved: decision 91 at `44b722dd`; section 8 governs.**

- The referee's "many r" has no frozen threshold. The shell triggers B04 at **any** r with a\* ∈ {0.001, 0.003}. Its sentences then only add diagnostics and cannot change a label.
- v1 regions start at 0 < a\*, so a\* = 0 with a passing null gate has no frozen label. The code labels it "a\*=0" (`v4_report_tables.py:region`). The shell reports such units with their intervals and no region.

Confirm both choices.

**Q10. "B ultrapassar o alvo" in the B/D rule.** **Resolved: decision 91 at `44b722dd`; section 8 governs.** v1 "Discriminador" line 259 uses "ultrapassar". v1 "Inferência" line 302 defines "ultrapassagem" by a lower band > 0.70, and M74 reserves "crossing" for that case. The shell reads the B/D condition as the lower band against B exceeding 0.70 at some strength (XING). The alternative is a finite point a\* (ATT). Which is intended?

**Q11. "D … tiver banda superior abaixo dele".** **Resolved: decision 91 at `44b722dd`; section 8 governs.** The v1 text does not say at which strengths. The shell requires D's upper band < 0.70 at **every** strength of a gap-free grid (BELOW). That is equivalent to D's inverted interval having no finite lower end. The alternatives are "at the strengths where B crosses" and "at B's a\*". The choice moves units between the frozen reading and "inconclusive". Which is intended?

**Q12. Both B and D cross (P6-d).** **Resolved: decision 91 at `44b722dd`; section 8 governs.** The frozen rules give a reading when D is below the target (non-Gaussian persistence) or spans it (inconclusive). They give none when D's lower band also exceeds 0.70. No between-family contrast is registered (T2 is not emitted, F3 is exploratory). The shell states the count and says that no reading about partner drift is attached. What wording does the Owner want?

**Q13. The "analogous rule" for E and C.** **Resolved: decision 91 at `44b722dd`; section 8 governs.** v1 line 262 says "Usar regra análoga para E/C", but the frozen label "compatible with non-Gaussian persistence" fits only D. The shell gives counts for E and C and calls them "the corresponding reading", with no label. What are the labels? Possible choices are:

- E: "compatible with mover–stayer heterogeneity, without specific evidence of interaction";
- C: "compatible with heteroscedastic error and heaping, without specific evidence of interaction".

**Q14. When the observed channel "exceeds" the control (B11).** **Resolved: decision 91 at `44b722dd`; section 8 governs.** v1 lines 253–257 give the reading, but not the test. The shell uses:

- **exceeds**: at some strength available in both units, the observed point AUC is greater than the latent or `ordinal_one` point AUC;
- **channel-dependent**: the observed unit attains a\*, and the gap-free valid control does not.

Open points:

- Should "exceeds" use bands rather than points?
- Should it be judged at a\* rather than at any strength?
- Should `latent_rank` count as a control? v1 lists it among the controls; the risk register names latent and `ordinal_one` only.

**Q15. r = 0.70 "stands apart" (B17-b).** **Resolved: decision 91 at `44b722dd`; section 8 governs.** No frozen rule defines this condition. The exposure sentence of B17 is unconditional, because D8 requires the mark at every r = 0.70 result. B17-b adds an interpretive disclaimer. It should be used only if the Owner fixes a criterion **now**, for example "its region differs from the regions at both r = 0.65 and r = 0.75". Otherwise it should be deleted. Which?

**Q16. The "wide interval" region.** **Resolved: decision 91 at `44b722dd`; section 8 governs.**

- v1 includes "IC amplo" among the causes of "censurada/indeterminada".
- It sets no width. `report/README.md` says no unit is labelled with it for that reason.
- The shell does not relabel a region by width; B09 reports width against the one-step precision target instead.

Should the one-step target also serve as the "wide interval" threshold? That would move units from "small" or "large" to "censored or indeterminate".

**Q17. Abstract trims.** **Resolved: decision 99; see [Coordinator decisions of 2026-09-30, before the G2 outcome](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-before-the-g2-outcome).**

- Every gate-passed abstract removes the gate-design sentence and the tier-2 clause.
- The largest mandatory composition also needs trim T1, which removes the estimand clause on sustained crossing, bands and censored cells.
- A gate-failure abstract also removes the "evaluation on new seeds" sentence.

Are these removals acceptable? If not, which other design sentence should be shortened?

**Q18. Ranges across r (B03 and P5-b).** **Resolved: decision 99; see [Coordinator decisions of 2026-09-30, before the G2 outcome](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-before-the-g2-outcome).** B03 reports the range of the upper band at a = 0.90 across r. P5-b reports the smallest and largest attained a\*. Neither selects an r, but v1 forbids summarizing the curve "pelo melhor valor". Are the ranges acceptable, or should the text point to Table T1 and Fig. F2 only?

**Q19. The B/D reading when the main curve is invalid (B02 with P6).** **Resolved: decision 91 at `44b722dd`; section 8 governs.** AMD D1 keeps the other units' boundaries "com a marca de invalidação principal". The shell therefore applies the per-r B/D reading at the valid r values and marks those sentences. Should a cross-mechanism sentence be written at all when the main curve is invalid?

**Q20. Protocol constants inside `results.tex`.** See N1. The shell prints the constants as literals (0.70, 0.5, 2.7729, 0.03, 414, 2004 …), and `paper_check.py --submission` will reject them. The options are:

- (a) bind each constant in the values JSON under protocol IDs, although they are not results;
- (b) define constant macros in the preamble;
- (c) teach the checker a list of protocol constants.

Which option?

**Q21. Label vocabulary.** "Use the frozen labels exactly" is applied as follows:

- **D9 statuses:** the Methods M45 English renderings, with the frozen Portuguese string at first use in P3.
- **Regions:** the M71 English labels ("small", "large", "not attained on a complete eligible grid", "censored or indeterminate").
- **B/D reading:** the M79 English wording.

The exporter prints different region labels: "not reached", "censored (gap)" and "a\*=0" (`v4_report_tables.py:region`). Should the tables be relabelled to M71 before rendering, or should the prose follow the tables?

**Q22. What counts as a sensitivity "reversing" the result (B12).** **Resolved: decision 91 at `44b722dd`; section 8 governs.** The shell uses a difference of region at the same r (REGION(k) ≠ REGION(B)). The alternative is attained versus not attained. Which one?

## 2. Records that a branch needs but the release does not carry

**M1. Secondary-target boundaries (B03, Q6).** The released curve has `first` and `sustained` for 0.70 only. Boundaries at 0.60 and 0.80 would be computed by reporting code from `auc`, `lower` and `upper`. That code lies outside the freeze closure; `v4_report_schema._expected_boundaries` already replays the inversion.

**M2. No render path without a release (every gate branch except B1a).**

- `detection_v4_report.render` requires `--curves` and calls `load_release` before anything else.
- If the gate fails, stops or is unfinished, no release exists, so T3 and F4 cannot be rendered.
- A gate-only mode, with `--gate-root` without `--curves`, is needed. It would be a report-code change, outside the freeze.

**M3. Records of G2 that the loader does not read.**

- B04 needs the G2 mean shift at the a = 0.003 cell. `aggregate` writes it only to the sealed `G2-auc-diagnostics.json` at the gate root: one `mean_shift` list per pipeline, in task order. `load_gate` does not read that file.
- The allocated G2 cell list (after any G0 substitution) is in the second binding record (`g2_cells`). The loader does not read it either, so T3 and F4 label G2 cells only as "cell 1…n".
- B1a and B1b-G2 describe cells by count, not by (a, r), for that reason.

**M4. Gap types and the eligible domain (B08).**

- Each released cell carries `attempts[].status`, `attempts[].evaluations`, `attempts[].validation_pass` and `dependency_gap`. That is enough to separate screened family-limit cells (zero evaluations) from profile family-limit, solver, validation and dependency gaps.
- No registered output separates them: F2 draws every gap as the same cross, and T1 gives only a count.
- The coordinator decided that the exporter will add this separation (log §8 Q11). Supplementary Table `tab:v4-sgaps` in the shell is that output. It does not exist yet.

**M5. Per-cell nuisance and fit diagnostics (B04, P9).** Each released cell carries:

- `mean_shift`, `nuisance_variance`, `nuisance_mcse`, `projected_fraction` and `tie_rate`;
- per attempt, `matching_pairs` (1,024 or 4,096, which shows retry use), `residual_se_units` and `amplification`.

`v4_report_schema.parse_curve` ignores these fields, and no registered table prints them. Supplementary Tables `tab:v4-slow` and `tab:v4-sdiag` in the shell would need new exporter code.

**M6. The SHP failure record (B14).**

- `shp_reliability.main` exits with status 2 and writes **no report** when a fit fails. The causes are: multi-wave optimizer not converged, information matrix not positive definite, triplet not converged or inadmissible, and too few complete respondents in a window.
- The message is printed to stderr only. For unexpected exceptions it reads "details withheld".
- So condition (a) of B14 and the value of `v4.shp.failure` have no field.
- The Owner's pre-run check of item, scale and mode divergence (SHP preregistration ¶1) is not recorded in any file.
- Neither the complete-case vs FIML disagreement nor the width of the Heise envelope has a threshold in the preregistration. The shell therefore does not branch on them.
- A failure record written before the aggregate report is needed. It would give the failing step and never any value.

**M7. The state of the gate at the close (B1d).** `criteria.jsonl` holds only aggregate lines. A stage that never aggregated leaves no line, and its progress can only be inferred from task directories. B1d needs a record, sealed at the close, of the last stage and its completed and planned counts.

**M8. G1a status (B1a).** G1a (unit-test identities) is not part of the sealed gate records. The shell refers to the Verification section for it.

**M9. Matching targets.** The referee's R1-M4 (E) item needs the interaction arm's L1 and L2 matching targets by cell. The released cells carry fitted `parameters` and residuals in SE units, but not the targets. No branch of the shell needs them. Recorded here because the referee report says they "come from the tier fits".

## 3. Mechanical and consistency issues

**N1. The result-file checker rejects protocol constants.**

- `pipeline/paper_check.py:result_consistency` scans `sections/results.tex` and `generated/*.tex` after removing comment lines and `\resultnum` macros.
- It reports every other numeral as an "unbound result number", including 0.70, 0.5, "$a=0$", 2.7729, 414, 2004 and "95\%".
- If this shell becomes `results.tex`, every constant will fail `--submission` (Q20).
- The shell spells counts as words where that reads naturally ("nine values of $r$").

**N2. `\resultnum` and the abstract count.**

- `paper_check.py` counts abstract words from the `main.tex` source, with command names stripped but arguments kept. Each `\resultnum{v4.t1.n_small}{0.812}` therefore counts its ID tokens as words.
- `results-shells-abstract.md` gives both counts. The printed count is the one the 250-word limit governs.
- The largest checker count exceeds the printed one by up to 28 words (H-BD).
- Either the checker should count the displayed value only, or the abstract should use short IDs.

Separately, `v4.gate.last_stage` (B1d) and `v4.shp.failure` (B14) are text, not numbers. The README convention expects numeric values. The checker's `str(values[key]) != shown` comparison would accept a string, but whether text results may be bound this way is for the Owner to decide.

**N3. Figure text and manuscript terminology.**

- F1, F2, F3 and F5 print "Influence strength a" and "Reliability r" as axis labels (`v4_report_figures.py`).
- The manuscript now says "partner drift" and "signal share", and reserves "reliability" for the anchor (log, R1 minor 6 and R2 minor 2).
- The captions in `report/captions.md` also use "influence strength".
- Both should be aligned before rendering. Both are report code, outside the freeze.

**N4. The solver budget in the F4 caption.** `report/captions.md`, F4(b), says "against the budget of 64". The frozen budget is 96 (AMD D2/D3/D4, line 141). The figure reads 96 from `profile_match`'s default. The caption needs correcting.

**N5. The placeholders in `generated/*.tex` do not match the registered outputs.** Proposed mapping:

| Placeholder | Registered output |
| --- | --- |
| `gate-outcomes` | T3, with F4 |
| `unit-status` | T4, with F5 |
| `primary-boundary-figure` | F1 |
| `point-vs-sustained-boundary` | T1, whose columns carry both boundaries |
| `auc-heatmaps` | F2 profiles |

"AUC heatmaps" is not a registered figure. The shell uses new labels `fig:v4-F1`… and `tab:v4-T1`…. When the shell is integrated, the old labels (`fig:primary-boundary`, `tab:gate-outcomes`, …) must be replaced or aliased.

**N6. Pointers in integration log §8 that do not resolve.**

- The log cites the exploratory declarations in `experiments/exploratory/detection-boundary-v4-exploratory/` (commit `12ef78f1`) and SHP preregistration successor 1 (commit `fd37e701`).
- Neither commit is in this repository (`git log --all`), and the folder does not exist. `sections/appendix-odd.tex` ODD39 and `sections/discussion.tex` DS10 depend on them.
- The shells therefore use neither the STARTS sensitivity nor the synthetic crosswalk. B13–B15 would need one sentence each for the STARTS value once the successor resolves.

**N7. Supplementary tables that are not registered outputs.** They are:

- `tab:v4-sec` (Q6, M1);
- `tab:v4-slow` and `tab:v4-sdiag` (M5);
- `tab:v4-sgaps` (M4).

All other referenced outputs are registered: F1, F2 per family, F3 (exploratory), F4, F5, F6, T1, T1s, T3 and T4.

**N8. Main-curve rule, frozen text and code.**

- The frozen text says B failing "at any eligible r" (v1, AMD D1, DRD).
- The frozen code invalidates on any tier-1 unit that is not `completo válido`, including units not started or partial (`_close_inventory`).
- The coordinator records this as a deviation (log §8 Q13). The shell follows the code (RS16) and names the mechanism of each invalid unit (B02).

## 4. Result IDs and their sources

The exporter must produce every ID below from the named records, and nothing else. "GATE", "STOP", "REL", "CV", "U", "SHP" and the predicates are defined in the header of `results-shells.tex`. Counts over "r" range over the nine tier-1 keys `t1-u00-r0` … `t1-u00-r8`, unless stated otherwise.

| ID | Source |
| --- | --- |
| `v4.gate.G0.{planned, failures, fits, anchor_failures, budget_statuses, implementation_statuses}` | the same-named fields of GATE[G0] |
| `v4.gate.G0.implementation_share` | implementation_statuses / fits |
| `v4.gate.G1b.{planned, completed, failures}` | GATE[G1b] |
| `v4.gate.G1b.exceeds_floor_count` | GATE[G1b].empirical_exceeds_floor_count |
| `v4.gate.G1b.coverage_min` | min of GATE[G1b].coverage_counts |
| `v4.gate.G1b.n_scenarios_below` | number of coverage_counts < 935 |
| `v4.gate.G1c.{planned, failures, anchor_count, pointwise_failures, mean_z, tie_rate}` | GATE[G1c] |
| `v4.gate.G2.{planned, failures}` | GATE[G2] |
| `v4.gate.G2.{pooled_ratio, pooled_lower, pooled_upper}` | GATE[G2] |
| `v4.gate.G2.n_cells` | len(GATE[G2].cell_ratios), or len(cell_failure_counts) |
| `v4.gate.G2.max_cell_failures` | max(cell_failure_counts) |
| `v4.gate.G2.n_cells_above` | number of c with cell_lower[c] > thresholds.cell_upper |
| `v4.gate.G2.n_cells_below` | number of c with cell_upper[c] < thresholds.cell_lower (`criteria-v43.json`) |
| `v4.gate.G2.{fd_median_min, fd_median_max}` | min and max of fd_ratio_median_by_cell |
| `v4.gate.G2.n_cells_fd_outside` | medians outside [0.8, 1.25] or null |
| `v4.gate.G2.covariance_flags` | sum of covariance_flag_counts |
| `v4.gate.G2.mean_shift_median.a0003` | median of `G2-auc-diagnostics.json` mean_shift, first FD step, over the 100 pipelines of the allocated cell with a = 0.003 (M3) |
| `v4.gate.G2c.a010.*`, `v4.gate.G2c.a003.*` | GATE[G2c].comparisons[0] and [1]: ratio, lower, upper, failure_count |
| `v4.gate.stop.gaps`, `v4.gate.stop.pass_probability` | STOP.g0_gap_binding |
| `v4.gate.last_stage`, `.completed`, `.planned` | M7; text value for the stage |
| `v4.inv.{n_valid, n_invalid, n_partial, n_not_started}` | counts of U over all 414 units |
| `v4.inv.t2.n_invalid` | count of U = `completo inválido` in tier 2 |
| `v4.inv.t{3,4,5,6}.n_valid` | count of U = `completo válido` in that tier |
| `v4.inv.t3.n_incomplete` | tier-3 count of `não iniciado` plus `parcial por encerramento operacional` |
| `v4.t1.{n_small, n_large, n_not_attained, n_censored}` | counts of REGION over VALID tier-1 units |
| `v4.t1.n_attained` | count of ATT |
| `v4.t1.n_crossing` | count of XING |
| `v4.t1.first_min`, `v4.t1.first_max` | min and max of CV.first over ATT |
| `v4.t1.n_resolved` | count of RES |
| `v4.t1.n_wide` | ATT and not RES |
| `v4.t1.n_first_ne_sustained` | VALID units whose first and sustained tuples differ (B06) |
| `v4.t1.n_sustained_gap` | VALID with sustained_censoring present |
| `v4.t1.n_first_gap` | VALID with first_censoring present |
| `v4.t1.n_dip` | ATT, no censoring keys, sustained ≠ first |
| `v4.t1.n_nonmonotone_band` | CV.nonmonotone_band true |
| `v4.t1.n_first_low` | ATT with first ∈ {0.001, 0.003} |
| `v4.t1.n_first_zero` | VALID with first = 0 |
| `v4.t1.gap_cells` | sum of gap_count over released tier-1 curves |
| `v4.t1.n_gap_units` | count with gap_count > 0 |
| `v4.t1.gap.{screened, profile_limit, solver, validation}` | B08 classification of the last attempt of each failed cell |
| `v4.t3.gap.dependency` | tier-3 cells with dependency_gap true |
| `v4.t1.n_not_valid` | nine minus the count of VALID |
| `v4.t1.n_invalid_gate`, `v4.t1.n_invalid_a0gap`, `v4.t1.n_clock` | B02 mechanisms |
| `v4.t1.n_interval_lower_finite` | first_interval[0] non-null |
| `v4.t1.upper_a090_{min, max}` | min and max over r of CV.upper at a = 0.90 (all nine units FULL in B03) |
| `v4.t1.n_exceeds_floor` | count of empirical_exceeds_floor true |
| `v4.t1.sec060.n_attained`, `v4.t1.sec080.n_attained` | M1 derivation, only if Q6 is answered yes |
| `v4.t2.D.{n_small, n_large, n_not_attained, n_censored}` | REGION over VALID `t2-u03-r{i}` |
| `v4.bd.n_eligible` | i with FULL(B_i) and FULL(D_i) |
| `v4.bd.n_persistence` | eligible i with XING(B_i) and BELOW(D_i) |
| `v4.bd.n_inconclusive` | eligible i with XING(B_i) and SPAN(D_i) |
| `v4.bd.n_both` | eligible i with XING(B_i) and XING(D_i) |
| `v4.bd.n_no_b_crossing` | eligible i with not XING(B_i) |
| `v4.bd.n_other` | n_inconclusive + n_both |
| `v4.be.n_persistence`, `v4.bc.n_persistence` | as `v4.bd.n_persistence`, with `t2-u04` (E) and `t2-u02` (C) |
| `v4.low.{n_cells, n_retry, projected_fraction_max, amplification_max}` | over cells at a ∈ {0.001, 0.003} of units counted in `n_first_low`: count; attempts with matching_pairs = 4096; max projected_fraction[0]; max amplification over attempts (M5) |
| `v4.t3.{n_pairs_compared, n_obs_exceeds, n_channel_dependent}` | B11 definitions (Q14) |
| `v4.sens.{n_pairs_compared, n_region_differs}` | B12 definitions (Q22) |
| `v4.shp.{estimate, wald_lo, wald_hi}` | SHP.anchor.estimate and wald_95_interval |
| `v4.shp.{env_lo, env_hi}` | SHP.sensitivity_envelope |
| `v4.shp.n_r_in_interval` | grid r values inside wald_95_interval |
| `v4.shp.n_status_classes` | distinct (U, REGION) pairs of B over those r |
| `v4.shp.failure` | M6; text |
| `v4.all.n_curves`, `v4.all.n_exceeds_floor` | count of REL.curves, and of those with empirical_exceeds_floor true |

## 5. What was checked

- **Markers.** A search of `results-shells.tex` finds RS01–RS57 with no gaps, and each has one ledger row.
- **Result IDs.** Every `\resultnum` ID in `results-shells.tex` and `results-shells-abstract.md` appears in section 4.
- **Abstract counts.** They were computed with `paper_check.word_count`.
- **Not done.** The shell was not compiled, and `paper_check.py` was not run on it.
- **Scope.** No existing file was changed.

## 6. Resolutions (2026-09-28)

The coordinator took these decisions under the Owner's delegation, after the synthetic release rehearsal. They are implemented in `src/ic_study/analysis/v4_report_protocol.py`, `v4_report_export.py` and `v4_report_schema.py`, and rehearsed in `experiments/exploratory/detection-boundary-v4/report/RELEASE-RUNBOOK.md`.

**Q20 and N1: option (a).** The export reads every protocol constant that the shells cite and binds it as `v4.protocol.*`. Nothing is retyped. Module constants and plan functions come from the frozen v4 tree. Literals of frozen functions are parsed from their source only after the module's SHA-256 matches `freeze-v4.json`. Criteria come from the frozen `criteria-v43.json`, and the Wald level and anchor year from the frozen SHP preregistration. The region cut and secondary targets are read from the frozen v1 preregistration after verification against its freeze record; the schema and T3 use the same protocol reader as the catalog. All 121 constants of the shells are now bound: 90 in the gate-passed branches and 31 in the gate-failure branches. The stray "03" of `\le0.03` is gone. The abstract shells keep literal constants: `paper_check.py` does not scan the abstract for them, and each `\resultnum` there would add its ID tokens to the checker's word count (N2).

| ID | Source |
| --- | --- |
| `v4.protocol.a.*`, `v4.protocol.r.*` | `GRID` and `RELIABILITIES` of `simulation/detection_v4.py` |
| `v4.protocol.grid_cells` | the product of their lengths |
| `v4.protocol.units.*`, `v4.protocol.tier.*`, `v4.protocol.steps`, `v4.protocol.omega_full` | `inventory()` of `simulation/v4_plan.py` |
| `v4.protocol.close_local` | `CLOSE_UTC` of `v4_plan.py` in America/Sao_Paulo |
| `v4.protocol.target` | default `target` of `boundary_report` (`analysis/detection_boundary.py`) |
| `v4.protocol.null_auc` | the value `boundary_report` compares `lower[0]` with |
| `v4.protocol.critical_floor` | the value `band` compares `empirical` with (`analysis/detection_boundary_v4.py`) |
| `v4.protocol.chance_invalidation` | METH M75 formula from the floor and the tier-1 units |
| `v4.protocol.g0.implementation_limit`, `g1b.pass_mark`, `g1c.mean_z_limit`, `g1c.pointwise_limit` | comparisons in `aggregate` (`simulation/v4_gate.py`) |
| `v4.protocol.g1b.repetitions`, `g1c.fits`, `g1c.r.*`, `g2c.refits.*` | `gate_tasks` of `v4_plan.py` |
| `v4.protocol.g2.fd_step.*` | the steps `finite_differences` accepts |
| `v4.protocol.g2.pipelines_per_cell`, `g2.fd_range.*`, `g2.joint_pass_*`, `g2c.upper_minimum`, `g2c.lower_maximum` | `criteria-v43.json` |
| `v4.protocol.g2c.bound_level` | the quantiles of `refit_ratio` (`simulation/v4_criteria.py`) |
| `v4.protocol.retry_pairs` | the pair counts of `fit_cell` (`detection_v4.py`) |
| `v4.protocol.equivalence_margin` | the margin of `validate_fit` |
| `v4.protocol.shp.wald_level`, `shp.anchor_year` | `primary` of `shp-reliability-preregistration.json` |
| `v4.protocol.small_cut`, `secondary_target.*` | `detection-boundary-preregistration-frozen.md`, verified against `detection-boundary-freeze.json` |

**M3.** `v4.gate.G2.mean_shift_median.a0003` is not exported. The mean shifts are only in the sealed `G2-auc-diagnostics.json`, which the report does not read and which opens only after the confirmatory results are committed. The B04 sentence that cited it was removed, and a comment marks the place.

**M4.** Supplementary Table `tab:v4-sgaps` is built from the released curves (`generated/supplement-gap-domain.tex`). For every B unit it gives the strengths not excluded by the feasibility screen and the gap cells by kind.

**M5.** The report's curve loader now keeps the released per-cell diagnostics. `v4.low.n_cells`, `v4.low.n_retry`, `v4.low.projected_fraction_max`, `v4.low.amplification_max` and Supplementary Table `tab:v4-slow` (`generated/supplement-low-strength-cells.tex`) come from them. A cell uses the retry when one of its attempts has the retry pair count. `tab:v4-sdiag` had no defined summary, so P9 no longer cites it.

**M6.** `v4.shp.failure` is not exported. A failed primary SHP fit writes no aggregate report, and successor 1 records only the STARTS sensitivity. B14 now states the failure without a bound value, and the cause is named in words from the SHP run record. Its condition (b) now names the field the report has, `multiwave.at_parameter_bound`.

**Q21 and REGION.** The header defines REGION as the region column of T1. `v4.t1.n_censored` and `v4.t2.D.n_censored` add "censored (gap)" and "indeterminate", as the sentence "censored or indeterminate" reads.

**N5.** The generated files have accurate names. `auc-heatmaps` became `auc-profiles` (F2 for B), and `point-vs-sustained-boundary` became `boundary-table` (T1). Every generated file keeps a placeholder until release day, and the export writes a comment-only file for an output that does not exist.

**T1s.** The export writes T1s as the CSV of the electronic supplementary material. The six references use `\allunitsresource`, defined in `main.tex` as Online Resource 1.

**RS46 and RS52.** The AUC range 0.57 to 0.59 of B04 has no machine-readable source, so the sentence keeps the bound equivalence margin and says that the residual still allows an AUC above the null value. The 4.9% of B02 is bound, computed from the frozen floor and the nine tier-1 units by the formula of METH M75.

Section 4 still lists `v4.gate.G2.mean_shift_median.a0003` and `v4.shp.failure`. They are no longer cited.


## 7. Release-pipeline corrections (2026-09-29)

The curves require `release-record.json`, whose digest must match the exact curve bytes. The report manifest binds the receipt, its effective UTC time and its trigger. An inventory-complete receipt must precede the nominal close and carry all 414 completed units; a declared-close receipt must be at or after that close. B00 describes the effective release rather than assuming release at the nominal close.

| ID | Source |
| --- | --- |
| `v4.release.effective_local` | receipt `released_utc`, converted to America/Sao_Paulo, including seconds |
| `v4.release.effective_utc` | receipt `released_utc` |
| `v4.release.condition` | receipt `condition`: completion of the full inventory or the declared close |
| `v4.protocol.close_local` | frozen nominal close, retained independently of the effective release |

T3 reads its gate criteria from the same hash-verified frozen source reader as the catalog, including G0, G1b, G1c, G2 failure allowances and FD interval, and G2c refit allowances. No fallback numerical literal is needed for these criteria or for the region cut and secondary targets. Production G1c successors additionally require the independently approved digest from Owner decision 46; synthetic rehearsals explicitly use `--synthetic` and still enforce summary consistency.

## 8. Decision 91: resolutions after the cross-family review

Authority: [Coordinator decisions of 2026-09-30](results-interpretation-decisions-2026-09-29.md#coordinator-decisions-of-2026-09-30-after-the-cross-family-review), present at base commit `44b722dd` (integration/ic-20260928). These resolutions supersede the historical questions and the earlier per-r Q8 answer. No result was opened to choose them.

| Question / application | Closed decision at `44b722dd` | Implementation |
| --- | --- | --- |
| Q8 and Q19 | Require all 36 tier-2 units complete valid and a valid main curve. No cross-mechanism sentence anywhere otherwise. Valid units remain in tables and figures. | `v4_report_export.cross_mechanism_allowed`; `v4.mechanisms.allowed`; global shell guard and P6-a. |
| Q8, common denominator | B and D are beside each other at every r when permitted. The frozen reading and paired regional counts use the same gap-free B/D mask, with its size and r list. E/C each use their own common mask with B. | `v4.{bd,be,bc}.n_eligible`, `.r_eligible`, `.n_side_by_side`, `.r_side_by_side`, `.{B,D/E/C}.n_*`; H-BD and P6. |
| Q10 and Q11 | Crossing is strict lower band > target; D below means its upper band stays strictly below target over the whole gap-free grid. | `_crossing`, `_below`, B10 and P6. |
| Q12 | Both crossings have no registered reading about partner drift; no relative boundary is promoted. | P6-d, under the global permission. |
| Q13 | E: compatible with mover–stayer heterogeneity, without specific evidence of interaction. C: compatible with heteroscedastic error and heaping, without specific evidence of interaction. | Separate E/C clauses of B10. |
| Q14 / B11 | Exceeds remains pointwise on strengths shared by observed and control. Include masked latent, ordinal r = 1 and latent_rank. Channel-dependent requires a finite observed first boundary and no finite first boundary in any of the three valid gap-free controls. Any invalid, absent or gapped control makes that label not assessed. | `_channel_values`, `v4.t3.n_channel_not_assessed`, B11 and P7-c. |
| Q6 | Derived targets 0.60/0.80 belong in the supplement at every r with a curve, in every release branch including non-attainment and main invalidation. Never in a headline. | `supplement-secondary-targets`, unconditional SECONDARY-SUPPLEMENT block in `sections/supplement.tex`; B03 no longer controls inclusion. Its B rows and caption retain the main-invalidation mark. |
| Q15 / B17-b | Remove the neighbour-comparison sentence; keep the exposure mark at r = 0.70 unconditionally. | B17. |
| Q9 and Q16 / B04, B04z | First strengths do not imply a small region. Use `region()` including indeterminate intervals; a* = 0 is indeterminate, as in T1. No width threshold changes a region. | `v4.t1.low.n_*`, B04 and B04z. |
| Q16 / B09 | Separate finite width exceeding one step, an endpoint beyond the grid, and an endpoint censored by a gap. | `v4.t1.n_interval_wide_finite`, `.n_interval_beyond_grid`, `.n_interval_gap`; B09 and its abstract clauses. |
| Q22 / B12 | A descriptive region difference or any sensitivity status other than complete valid triggers B12. No reversal claim. Name full anchoring at omega = 1 as degeneracy. | `v4.sens.n_not_valid`, `.use_b12`, B12 and guarded P7-d. |
| Exploratory consequence | Primary X6a band reading against D1 of failure/subnominal requires the abstract's below-nominal interior-coverage clause and discussion expansion. Inconclusive/no reading requires discussion of coverage not established. Preserve original labels and restricted wording. | Explicit trigger `v4x.x6.x6a.band.vs_d1.primary.reading`, bound in the abstract shell on 2026-09-30. |
| Decision 89, domain | X3 at a = 0 and X4b outside r in {0.50, 0.70, 0.90} have their own outside-declared-domain state, even without an aggregate, and never select a neighbour. | `v4_exploratory_comparisons`, including X4b calibration. |

The B04 regression uses first boundary 0.003 with interval [0.001, 0.10], classified indeterminate. The B12 regression holds all sensitivity regions equal except for one complete invalid unit. The B/D regression places gaps at different r in the two families: all nine rows remain visible, but paired counts use only the seven shared gap-free r. These are the cross-family review's application counterexamples, expressed as synthetic inputs.

The trigger ID is `v4x.x6.x6a.band.vs_d1.primary.reading` from the exploratory exporter, merged in integration on 2026-09-30.
