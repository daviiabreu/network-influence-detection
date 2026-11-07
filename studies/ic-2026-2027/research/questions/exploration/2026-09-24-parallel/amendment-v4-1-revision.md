# v4.1 revision of the v4 decision specification (before any freeze or gate run)

Date: 2026-09-25. Author: coordinator (delegated decision, log item 19 addendum). Scope: corrections found by the v4
implementation (`cda3a92`, "Interpretações e desvios" §1–8 and the cost projection), before any freeze, gate run,
classifier training at a>0 or AUC. Justification basis: a specification error, measured cost and measured
approximation behaviour. No AUC was computed or consulted.

R1. **Validation test (D4), specification error corrected.** The fitted θ̂ carries sampling error from the fitting
draws, so fresh-pair residuals have variance SE_fit² + SE_val², not SE_val². The v4 rule `|res_k| > 4·SE_val,k` rejects
correct fits at a material rate: with M=1,024 and 4,096 validation pairs it is ≈14% per fit before nonlinearity. That
is consistent with the failed first validation at (0.03, 0.70). The corrected rule is: fail if
`|res_k| > 4·√(SE_fit,k² + SE_val,k²)` on any fitted moment. SE_fit,k is the paired SE on the fitting draws at θ̂. A's
equivalence statistic and B's amplification diagnostic remain reported. Validation size is 2,048 fresh coupled pairs:
under the corrected rule, power is governed by SE_fit, and 2,048 keeps SE_val ≤ 0.71·SE_fit. The one pre-declared retry
at M=4,096 with fresh validation stays.

R2. **Acceptance tolerance (D4).** Interior acceptance on the fitting draws becomes
`|ḡ_k| ≤ min(5e-5, max(1e-6, 0.25·SE_fit,k))`. The residual is a bias that D5's centred variance does not carry, so it is
bounded at 0.25 SE. Compared with 0.1 SE, the added mean-square error is ≤6% of the fit's sampling variance. The
requirement of at least one real solver step (except anchor-exact) stays. The budget stays at 64. Reason: the measured
32 evaluations at 0.1 SE are driven by rank discreteness of ḡ near the root. Report the evaluation counts in G0.

R3. **Propagation (D5): mean-shift instead of per-realisation drift.** The probe showed per-realisation shifts with 46%
relative error against regenerated shifts, while the vector error was 0.087%. Rank and category discreteness make the
per-realisation map discontinuous, so per-realisation drift has no fidelity advantage that would justify ~28,000
stencil panels per cell. D5 step 3 becomes:

- Shift the null training and reference features by `D·Δθ_b`, where D is the Jacobian of the **mean** L3–L5 features,
  estimated by CRN finite differences on the matching realisations: one step per parameter, 0.01, pre-declared.
- In G2 cells only, also estimate the **covariance** Jacobian by stencils on training and reference. Report the implied
  first-order change of the LDA direction and of the AUC under the shift. If it exceeds 10% of the D5 standard error,
  report it as a diagnostic flag. The gate criteria (G2, G2c) decide adequacy, because they compare the D5 variance
  with actual procedure dispersion and with full refits.
- The D11 test becomes: at a fixed test point, the mean-feature shift predicted by D matches the regenerated
  mean-feature shift within 5% (vector level), and Δθ_b ≡ 0 at anchor-exact. Per-realisation accuracy is not required.

R4. **G2c power (deviation §3).** Accept that G2c alone does not meet the operating characteristic and that G2 plus G2c
jointly do (3.37% pass at SE×0.8 in the artificial model). The cut-offs 0.8/2.0 and the 100/40 refits stay. The
amendment text states this explicitly.

R5. **D3/D4 (deviation §1).** CRN applies in matching **and in matching validation**. Train, test and reference keep
independent classes. Clarify D3's text accordingly.

R6. **Allocation (deviation §2).** The freeze record fixes the rules, code, criteria and seeds. The G0 output (statuses
only) and the resulting G2 cell list, with any recalibration, are bound by SHA-256 in a second record **before** G2
runs. This two-stage binding is declared in the freeze record.

R7. **Cost engineering (no scientific change).** The control-channel extraction path (0.0477 vs 0.0198 CPU-s per
panel) must compute only the features and summaries each unit needs. Byte-identical outputs are verified by tests
against the current path. Re-measure all per-panel rates, the matching evaluation count under R2, and the retry rate
over at least 8 blocks at 3 cells: (0.003, 0.70), (0.03, 0.70), (0.30, 0.70). No training or AUC. Update the
projection.

R8. **Execution.** If the updated projection for gate + tiers 1–5 still exceeds the local window, the tiers stay as
declared (no scope reduction). The coordinator provisions shards (homelab, VPS) under the same code hash with a
numerical-equivalence check. Anything not completed by the close is reported per D9.
