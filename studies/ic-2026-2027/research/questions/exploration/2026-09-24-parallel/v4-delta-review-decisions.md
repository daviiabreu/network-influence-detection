# Coordinator decisions on the delta review of 9effe1c5 (2026-09-25)

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

## Blocking fixes

1. **Gap rule, restoring v1.** A gap only prevents declaring a boundary across it.
   - **Band:** computed over the available strengths.
   - **First boundary:** the first boundary, and each end of its inverted interval, are declared only if they fall before
     the first gap. Otherwise the result is None with the censoring reason "gap at a=…".
   - **Sustained boundary:** declared only if it lies above the last gap and every strength above it is available.
     Otherwise censored with the reason.
   - **Unit status:** `completo inválido` comes only from the per-run a=0 gate, including an infeasible or unmatched a=0
     cell. Otherwise it is `completo válido`, with the censoring reported.
   - **Main curve:** `main_curve_valid` is a flag driven by the tier-1 null gates, per v1 ("B failing at any eligible r
     blocks validation of the main curve"). It does not delete boundaries at other r values; they are reported and
     flagged.
   - **Tests and amendment:** update both tests and the amendment text.
2. **Stop rule before G2, using an allocation-independent estimator.**
   - Pool all of G0's B/observed a>0 fits (72).
   - The gap rate is the one-sided 95% Clopper–Pearson upper bound of (gaps / 72).
   - Apply it to every allocated G2 cell in the implied pass-probability calculation.
   - Stop before G2 if the implied joint pass probability is below 0.95.
   - Record this in the amendment, and add a test in which G0 produces realistic gaps.

## Non-blocking fixes (do them before the freeze)

3. **Item 11.** Append it verbatim, as above, to `v4-review-decisions.md`.
4. **Shards.** Machine parallelism was dropped by the Owner, so bind the shard count to 8 local workers in the freeze
   record. Keep the cap and state it in the amendment.
5. **Infrastructure errors fail closed.** I/O errors, MemoryError, the resume nondeterminism check and interrupts stop the
   run and allow resume; they must not be recorded as a permanent `technical-gap`. Only the declared scientific and
   numerical statuses become gaps.
6. **Spec binding.** Hash-bind the spec (D1–D11), the revision, the review findings and the decisions files in preflight.
7. **Pooled allowance.** It scales with the number of G2 cells actually run: ≤ ceil(0.02 × pipelines). The per-cell limit
   stays at 5/100. Recalibrate if the cell count changes.
8. **Identity tests.** Byte-level identity for the control channels (latent, ordinal_one, latent_rank) and for mobility
   controls at a=0.

## Correction to item 2 (2026-09-25, 14:35 UTC; coordinator)

As specified, item 2 is self-defeating. With 0 gaps in 72 fits, the one-sided 95% Clopper–Pearson upper bound is 0.0408.
Against the pooled allowance of 14/700, that implies a pass probability of 0.0017, so the rule would always stop before
G2. The replacement rule:
- **Purpose.** It is a waste guard; the gate's own criteria carry validity.
- **Estimate.** Pool G0's B/observed fits at the strengths G2 uses (0 < a ≤ 0.30; all nine r values, 54 fits). Put a
  Jeffreys prior Beta(0.5, 0.5) on the per-pipeline technical-failure rate.
- **Prediction.** Compute the posterior predictive probability that G2 meets both allowances: ≤5 of 100 in every cell
  and ≤ ceil(0.02 × pipelines) pooled. Use the beta-binomial by simulation with a fixed seed, and include the G2c
  allowances.
- **Stop.** Stop before G2 if that probability is below 0.80. Record the numbers in the R6 second-stage binding.
