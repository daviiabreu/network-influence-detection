# Abstract sentences for each Results branch

Decision 91 of 2026-09-30, at base `44b722dd`, supersedes the earlier composition. These are shells, not results. Bind counts with the confirmatory export; do not choose a sentence after examining a different result.

## Composition and budget

Use one gate sentence, the applicable boundary sentence, the frozen B/D reading when positive and permitted, a first/sustained difference when present, and the mandatory X6 clause when its condition holds. The single permission `v4.mechanisms.allowed` governs H-BD, D-after-B03, B10 and every other cross-mechanism clause, locally and in the headline. When it is zero, use B only; B02 additionally marks an invalid main curve. All valid units remain in the full tables and figures.

With permission, B/D appear beside each other at every r in Results. All abstract counts comparing the families use `v4.bd.n_eligible` and the explicit `v4.bd.r_eligible` list, and the paired regional IDs, never the separate unmasked family totals. When this common gap-free set is empty, use H-B and say that no frozen reading was assessed, retaining all B/D rows in Results.

The previous worst-case composition included B02 and H-BD together; Q19 now forbids that composition. For the word budget, replace the verbose design passages with the following concise baseline, retaining the chosen sentences between its design and limitation passages. Count the filled abstract with `paper_check.py`, including the displayed r list, before submission; optional sentences are omitted if the total exceeds 250. The X6 consequence is mandatory and takes priority over optional sentences.

> When exposure is unobserved, opinion panels can show patterns consistent with partner drift or persistence. We map the nominal partner-drift strength $a$ that a fixed lag-based discriminator needs to separate synthetic panels from matched no-network persistence. Eleven-wave panels approximate the Swiss Household Panel's observation pattern. Both processes share a known response signal share $r$, and persistence is matched to drift on short-lag population correlations. The detection boundary $a^*(r)$ is the first grid strength at which the expected panel-level area under the receiver operating characteristic curve (AUC), given a validated fit, reaches 0.70 against trait-plus-autoregressive persistence. Small and large denote interval-based regions divided at 0.03.

This is the design baseline of `main.tex` (AB01, AB02, AB04, AB05, AB09 and AB10 in `claim-evidence.md`), with the expected AUC qualified as conditional on a validated fit (T57c); the unassembled draft abstract in `main.tex` should carry the same qualification. It has 107 words under `paper_check.py`. The 0.03 cutoff is the frozen region convention, not a substantive effect-size threshold; interval and censoring rules remain those of decision 91 Q16. The longer-lag interpretation is developed in the introduction and related work rather than added as a result-independent abstract conclusion.

Gate-passed abstracts retain this caveat after all result sentences and before the limitation (T41d amendment to decisions 91/101):

> After partial calibration exposure and protocol amendment, evaluation used new seeds.

Gate-failure abstracts additionally retain:

> Every gate stage must pass before any evaluation on the reserved seeds.

Every branch retains:

> Separation is conditional on the declared laws, response channel and discriminator and does not identify causal social influence.

## Gate passed

**G**:

> The validation gate passed; \resultnum{v4.inv.n_valid}{[n]} of 414 units \resultplural{v4.inv.n_valid}{was}{were} complete and valid.

**B02**, only when the main curve is invalid:

> The main curve was not validated: not all nine of its units finished complete and valid.

**H-BD**, only with permission and a nonempty common gap-free set:

> At the \resultnum{v4.bd.n_eligible}{[n]} \resultplural{v4.bd.n_eligible}{share}{shares} with both comparisons gap-free ($r=$ \resultnum{v4.bd.r_eligible}{[r list]}), the first boundary was small at \resultnum{v4.bd.B.n_small}{[n]} against trait-plus-autoregressive persistence and \resultnum{v4.bd.D.n_small}{[n]} against state-dependent persistence, large at \resultnum{v4.bd.B.n_large}{[n]} and \resultnum{v4.bd.D.n_large}{[n]}, not attained at \resultnum{v4.bd.B.n_not_attained}{[n]} and \resultnum{v4.bd.D.n_not_attained}{[n]}, and censored or indeterminate at \resultnum{v4.bd.B.n_censored}{[n]} and \resultnum{v4.bd.D.n_censored}{[n]}.

**H-B**, when the cross-mechanism permission is zero or no gap-free pair qualifies:

> Against trait-plus-autoregressive persistence, the first boundary was small at \resultnum{v4.t1.n_small}{[n]} \resultplural{v4.t1.n_small}{share}{shares}, large at \resultnum{v4.t1.n_large}{[n]}, not attained at \resultnum{v4.t1.n_not_attained}{[n]} and censored or indeterminate at \resultnum{v4.t1.n_censored}{[n]}.
> Against trait-plus-autoregressive persistence, the first boundary was small at all \resultnum{v4.t1.n_small}{[n]} \resultplural{v4.t1.n_small}{share}{shares}; none was large, not attained, censored or indeterminate.
> Against trait-plus-autoregressive persistence, the first boundary was large at all \resultnum{v4.t1.n_large}{[n]} \resultplural{v4.t1.n_large}{share}{shares}; none was small, not attained, censored or indeterminate.
> Against trait-plus-autoregressive persistence, the first boundary was not attained at all \resultnum{v4.t1.n_not_attained}{[n]} \resultplural{v4.t1.n_not_attained}{share}{shares}; none was small, large, censored or indeterminate.
> Against trait-plus-autoregressive persistence, the first boundary was censored or indeterminate at all \resultnum{v4.t1.n_censored}{[n]} \resultplural{v4.t1.n_censored}{share}{shares}; none was small, large or not attained.

**P6-a**, no permission:

> The prespecified conditions for comparing separation across persistence models were not met.

**P6-empty**, permission but no common gap-free pair:

> No share had gap-free comparisons against both trait-plus-autoregressive and state-dependent persistence, so the prespecified cross-model reading was not assessed.

**B03**, complete valid B grids without point attainment, replaces H-B:

> Against trait-plus-autoregressive persistence, the point AUC did not reach 0.70 at any strength on any of the nine complete grids; stronger discriminators remain untested.

**D-after-B03**, only with permission and a nonempty common gap-free set; use alongside B03 instead of H-BD:

> At the \resultnum{v4.bd.n_eligible}{[n]} \resultplural{v4.bd.n_eligible}{share}{shares} where the comparisons against trait-plus-autoregressive and state-dependent persistence were both gap-free ($r=$ \resultnum{v4.bd.r_eligible}{[r list]}), the first boundary against state-dependent persistence was small at \resultnum{v4.bd.D.n_small}{[n]} \resultplural{v4.bd.D.n_small}{share}{shares}, large at \resultnum{v4.bd.D.n_large}{[n]}, not attained at \resultnum{v4.bd.D.n_not_attained}{[n]} and censored or indeterminate at \resultnum{v4.bd.D.n_censored}{[n]}.

**B10**, only with permission and a positive n_persistence:

> At \resultnum{v4.bd.n_persistence}{[n]} of those shares the trait-plus-autoregressive band exceeded the target and the state-dependent band stayed below it, compatible with non-Gaussian persistence without specific evidence of interaction.

**B06**, when first and sustained differ and v4.t1.n_first_ne_sustained is positive (abstract selection only):

> First and sustained boundaries differed at \resultnum{v4.t1.n_first_ne_sustained}{[n]} \resultplural{v4.t1.n_first_ne_sustained}{share}{shares}.

**X6**, mandatory conditional consequence:

Condition: the primary X6a joint-band reading against the D1 procedural truth is `failure` or `subnominal` after the aggregate's reference-precision sensitivity. An effective `inconclusive` reading never triggers this abstract clause. Select from the validated exploratory aggregate and preserve its machine label. Do not use X6b, pointwise coverage, population truth or a secondary gaps-as-misses reading to trigger this clause.

> An exploratory check at $r=0.70$ found below-nominal interior coverage.

The trigger ID is `v4x.x6.x6a.band.vs_d1.primary.reading`, emitted by the exploratory exporter (`src/ic_study/analysis/v4_exploratory_export.py`, joint-band rows of the X6 table); the clause is written only when that machine reading is `failure` or `subnominal`. The discussion must expand failure/subnominal. For inconclusive or no reading, it states that interior coverage was not established. Other readings retain the restrictions in `pipeline/review/x3-x7-reading-restrictions-2026-09-29.md`.

X3, X4 and X7 never add abstract clauses. X5 stays in discussion and conclusion whatever its curve. A negative X3 interval inside the ±0.02 margin is reported with magnitude there. Derived 0.60/0.80 targets never enter the abstract.

## Optional clauses

Include only while the filled abstract stays within the word budget. Every cross-mechanism optional clause requires the same permission and common r set as H-BD. Decision 101's order remains the three B09 clauses, B04, B05, B08, B11 and B14: add each if it fits, otherwise skip it without removing an earlier clause. Count only visible text, including the filled r list, with the current `paper_check.py`.

**B09**: select each clause independently for a positive count. Do not treat a censored or beyond-grid end as a measured finite width.

> Finite boundary intervals spanned more than one grid step at \resultnum{v4.t1.n_interval_wide_finite}{[n]} \resultplural{v4.t1.n_interval_wide_finite}{share}{shares}.

> At \resultnum{v4.t1.n_interval_beyond_grid}{[n]} \resultplural{v4.t1.n_interval_beyond_grid}{share}{shares} an interval end lay beyond the grid.

> At \resultnum{v4.t1.n_interval_gap}{[n]} \resultplural{v4.t1.n_interval_gap}{share}{shares} a gap censored an interval end.

**B04**, only when v4.t1.n_first_low is positive (abstract selection only):

> At \resultnum{v4.t1.n_first_low}{[n]} \resultplural{v4.t1.n_first_low}{share}{shares} the first boundary lay at one of the two smallest positive strengths; \resultplural{v4.t1.n_first_low}{its region}{their regions} still follow the tabulated intervals.

**B05**:
Select only when the point estimate dips (v4.t1.n_dip > 0); a band flag alone does not select this sentence.

> At \resultnum{v4.t1.n_dip}{[n]} \resultplural{v4.t1.n_dip}{share}{shares} the AUC dropped below 0.70 again above the first boundary.

**B08**, only when both displayed counts v4.t1.n_first_gap and v4.t1.n_sustained_gap are positive (abstract selection only):

> Gaps (failed or excluded fits) censored \resultnum{v4.t1.n_first_gap}{[n]} first \resultplural{v4.t1.n_first_gap}{boundary}{boundaries} and \resultnum{v4.t1.n_sustained_gap}{[n]} sustained \resultplural{v4.t1.n_sustained_gap}{boundary}{boundaries}.

**B11**:
Select only when v4.t3.n_channel_dependent > 0; non-assessment does not select this sentence.

> Separation was channel-dependent at \resultnum{v4.t3.n_channel_dependent}{[n]} \resultplural{v4.t3.n_channel_dependent}{pair}{pairs} of null family and signal share.

**B14**:

> The preregistered reliability anchor for the Swiss Household Panel trust item failed its diagnostics and is not reported as a point estimate.

B07, B12, B15, B16 and B17 add no abstract sentence. The calibration-exposure statement stays unconditional for released results; the neighbour clause of B17-b is removed.

## Gate failed, stopped or unfinished (B1b-\*, B1c, B1d)

Use the concise design baseline, the additional gate-failure design sentence, one gate sentence and the closing sentence X. With the every-branch limitation, G0 has 179 visible words under the checker. The 46 distinct mandatory predicate compositions have at most 250 words, including first/sustained interval-only differences under B03; B03 with a positive B10 reading is impossible. The authorized fallbacks were applied in order: B10 without the appositive, X6 without "of the AUC bands", and the original interval-region sentence in the opening. T57c replaced the earlier elliptical H-BD ending with counts paired by region, B before D, and kept the AUC qualification to four words because the H-BD composition with B10, B06 and X6 reaches exactly 250 (the B03 composition with B06 and X6 now has 245). These are synthetic budget checks, not outcomes. Mandatory clauses stay; positive-count optional clauses enter by decision 101's first-fit rule up to 250 words, before the new-seed caveat and limitation. Recount the actual filled abstract before submission. See pipeline/review/t57g-abstract-budget.json.

**B1b-G0** (24 / 24):

> The six-stage validation gate failed at its first stage, the blind matching mask, so no confirmatory seed was derived and no curve was estimated.

**B1b-G1b** (26 / 30):

> The six-stage validation gate failed at its band-mechanics stage, where coverage fell below 935 of 1,000 in \resultnum{v4.gate.G1b.n_scenarios_below}{[n]} synthetic \resultplural{v4.gate.G1b.n_scenarios_below}{scenario}{scenarios}, so no curve was estimated.

**B1b-G1c** (21 / 21):

> The six-stage validation gate failed at its end-to-end zero-strength stage, so no confirmatory seed was derived and no curve was estimated.

**B1c** (41 / 49):

> Execution stopped before the dispersion stage of the validation gate because \resultnum{v4.gate.stop.gaps}{[n]} of 54 relevant matching fits failed, which put the predicted probability of meeting the failure allowances at \resultnum{v4.gate.stop.pass_probability}{[p]}, below the prespecified minimum of 0.80; no curve was estimated.

**B1b-G2** (29 / 29):

> The six-stage validation gate failed at its procedure-dispersion stage, which compares observed with model-implied variability of the AUC, so no confirmatory seed was derived and no curve was estimated.

**B1b-G2c** (28 / 28):

> The six-stage validation gate failed at its last stage, which compares local nuisance propagation with full refits, so no confirmatory seed was derived and no curve was estimated.

**B1d** (24 / 24):

> The six-stage validation gate had not finished when the fixed compute window closed, so no confirmatory tier was run and no curve was estimated.

**X**, closing sentence for every gate branch except B1a (15 / 15):

> Under the prespecified rules, any continuation requires a new, separately frozen protocol that carries forward the cumulative exposure.

The last abstract sentence, "Any separation is conditional on …", is still accurate in a gate-failure abstract. A gate-failure abstract is not rewritten as a report of a failed validation (notes Q2, decision 99).
