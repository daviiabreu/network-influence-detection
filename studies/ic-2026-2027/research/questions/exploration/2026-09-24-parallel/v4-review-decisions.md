# Coordinator decisions on the independent review of cda3a92 (2026-09-25)

All ten findings are accepted. Implement them before the freeze:

1. **Curve runner.** Per r × inventory unit, stack the scores to (2000,2,9) and the nuisance deviations to (2000,9)
   under one seed plan. Apply the frozen band rule, v1's gap and censoring rules, the per-run a=0 gate and its
   invalidation rules, and the sustained boundary. Write the D9 unit statuses (`não iniciado`,
   `parcial por encerramento operacional`, `completo inválido`, `completo válido`). Add a tier scheduler, fixed order
   and resumable, with shard manifests and the close-time rule. Sealing applies to confirmatory outputs until the
   close. Everything goes under the preflight hash.

2. **Failure accounting in the gate.**
   - A technical failure (any gap status) counts in the denominators.
   - G2's ratio statistics use successful pairs; a pair with a failure is dropped from the ratio but counted.
   - The gate adds a pre-declared failure allowance: ≤5 of 100 per cell and ≤14 of 700 pooled for G2; ≤3 of 100 and
     ≤2 of 40 for G2c; G1c unchanged (all fits must be anchor-exact).
   - The FD-step check is one aggregate per cell: the median V_nuis ratio for 0.005 vs 0.01 must lie in [0.8, 1.25].
   - Recalibrate the thresholds with artificial data that include failures at a declared rate of 1% and the per-cell
     FD aggregate. Target: P(pass | correct SE, 1% failures) ≥ 0.95 and P(pass | SE×0.8) ≤ 0.20.
   - The R6 second record binds G0's measured gap rate at the G2 cells. If the implied pass probability is below 0.95,
     stop before G2 and document; do not proceed.

3. **G2c reference.** Regenerate the refit null reference at θ_refit with the baseline's seeds
   (`replace(seeds, repetition=0)`, common random numbers), as v1 did. Amend the wording.

4. **D5 boundary.** Resample the matching differences **uncentred** (`data.differences[indices].mean(0)`), so that the
   linearised draws replicate the solver's boundary rule. The AUC variance stays centred.

5. **Controls.** If the observed fit failed or is missing, the control returns a dependency gap, in the pipeline as in
   G0.

6. **Identity tests.** At a=0, compare the bytes of the mask, measured, observed and selected features for the main
   channel, mobility, c=0.25/0.50, δ=0.10/0.20 and the combination, at full N.

7. **Solver endpoints.** A bracket endpoint accepted without a real step is labelled `boundary`, never `interior`,
   unless a step was taken. The amendment states that the retry has its own 64-evaluation budget.

8. **Seed audit.** Extend it to the G1b, G1c and G2c plans and to the stencil, nuisance, bootstrap and validation
   namespaces.

9. **Sealing.** Move `mean_shift` in AUC units to the sealed record. Stdout prints only ratios or criteria.

10. **Frozen file.** Record in the amendment the post-freeze edit of `detection_panel.py` (`d33bf4e`; SHA-256
    a9d294e3… → aee84770…) and the byte-identity evidence, with the reason (skipping unused work at zero share).

**Wording.**
- R2: "0.25² = 6.25% of the fit's sampling variance".
- R1: SE_val ≤ 0.71·SE_fit holds for the M=1,024 attempt; on the M=4,096 retry the ratio is 1.41. The rule's
  combined-variance form stays valid for both.
- R4: G2 alone meets the ≤0.20 target; G2c is a complementary check aimed at V_nuis.

## Item 11 (verbatim record of the instruction given on 2026-09-25 with the review decisions)

Solver efficiency and budget are operational changes only. Measured evaluations reached 49–63 at a=0.30 against a
budget of 64, so budget exhaustion at a=0.6/0.9 would create gaps.
- (a) Measure matching-only evaluation counts and validation outcomes, with no training and no AUC.
- (b) Improve the solver without changing acceptance, validation or statuses:
  - a warm start from a linear prediction using the finite-difference Jacobian at the anchor, and/or the previous
    strength's solution within the same r and family (deterministic, matching-only information);
  - inexact inner solves that tighten to the acceptance tolerance near the outer root;
  - Illinois or Brent in the outer step.
- (c) Set the evaluation budget to 96 per attempt; the retry at M=4,096 keeps its own budget.
- Record the change and its reason in the amendment.
