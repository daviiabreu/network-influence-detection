# Detection boundary — successor amendment v4: adopted decision and implementation spec

Date: 2026-09-25. Status: delegated agent decision (decision log item 19), pending Davi's ratification. The frozen v1
protocol (`fd65d2a`, SHA-256 `fb6b4dcf43161a52c725e565bf2a4d2697423bec7d138ad1d30388547cfcd706`) and its artefacts stay
byte-identical. v4 is a linked successor. It changes only operational and statistical-validity aspects; the reasons
are the failed v1 coverage gate (`1d3c674`), identities at a=0, solver-failure analysis, Monte Carlo arithmetic and cost.
No interior AUC value was a criterion.

Inputs: proposal A (`038a6f3`), proposal B (scratchpad `amendment-b/`, including its §11 corrections), the coordinator's
synthesis draft, B's critique of A and the synthesis, and the Codex critique `9fbff6e`
(`amendment-critique-codex-on-synthesis.md`). Where they disagree, this spec records the choice and the reason.

## D1. Target (clarification)

AUC(a,r) is E over the declared matching draw (M=1,024) and training draw (1,000 networks × 2 events per class) of the
population AUC of the trained frozen LDA against the fitted null. The target is defined on successful fits. A fit that
fails validation (D4) makes the cell a gap under v1's gap rules; it is never averaged away. In gate G2, failures stay in
the denominators.

## D2. Null laws (shared transport)

Notation: `R_N` is the frozen normal-rank transport. `X_φ` is the influence arm's a=0 recursion: `x_0=R_N(ε_0)`,
`x_t=R_N(φ x_{t−1} + √(1−φ²) ε_t)`, using the same number of transports per wave as the alternative (1 in the main
design, 24 in the 24-step sensitivity).

- **B (confirmatory):** T_i ~ N(0,1) iid (not rank-transported, as in proposal A), independent of x.
  `z_t = R_N(√λ T + √(1−λ) x_t)`. λ ∈ [0, 0.8], φ ∈ [0, 0.999].
- **A:** B at λ=0.
- **E:** s_i ~ Bernoulli(π), `z_t = R_N(s_i x_0 + (1−s_i) x_t)`.
- **D:** unchanged; γ=0, ρ0=φ is identical to `X_φ`.
- **C:** A plus v1's heteroscedastic error and heaping, unchanged (no identity claimed).
- **Anchoring ω:** no identity claimed. ω=1 gets an explicit degeneracy case. The per-run a=0 gate applies.
- The Gaussian covariance identity `λ+(1−λ)φ^k` is no longer claimed. λ and π become nominal pre-transport weights. The
  amendment text states this change of finite law for B, A and E explicitly.
- At λ=π=γ=0 and φ=0.85, B, A, D and E coincide pathwise with the a=0 influence arm on shared seeds. This must be tested
  at full N, for every channel (main, c, δ) and for the 24-step variant.

## D3. Common random numbers

Target and null share the state, mask and error streams **only in the matching phase** (null index 2i+1 uses the same
`state` stream as the target). Components with no counterpart (T, s) use the `null-state` role. Train, test and reference
keep independent classes, disjoint phases and network clusters exactly as in v1. A seed-role collision audit covers the
new mapping.

## D4. Matching: profile solver, strict acceptance, independent validation

- **Solver.** A profile solver: for fixed η (λ, π or γ), solve L1 in φ; then solve L2 in η along the profile. Both 1-D
  searches are safeguarded root-finders (Brent or secant with bisection fallback) inside valid brackets. They must
  handle NaN, zero derivatives and degenerate secants. The budget counts evaluations actually executed: 64 per cell ×
  family × channel. The profile prioritises L1, and that priority is part of the definition. One-parameter families
  (A, C, and the control re-fits) solve only L1, with L2 as a diagnostic. For controls, the second parameter is held at
  its value from the observed fit of the same refit, as in v1.
- **Statuses:** `anchor-exact` (ḡ≡0 bytewise, a=0 identity families only), `interior`, `boundary`, `no-L1-root`,
  `non-monotone-profile`, `ill-conditioned`, `numerical-limit`, `family-limit-lower/upper`, `budget`. Any status other
  than anchor-exact, interior or boundary is a gap. It is never converted into "AUC below target", and it is never a
  certificate of impossibility.
- **Acceptance on the fitting draws.** For an interior root, require `|ḡ_k| ≤ min(5e-5, max(1e-6, 0.1·SE_k))` on each
  fitted moment, where `SE_k = sd(paired differences)/√M`. At least one real solver step is required, except for
  anchor-exact. Boundary: η=0 is accepted when the L1 root at η=0 satisfies the interior rule on L1 and the constrained
  profile is non-decreasing into the interior. That is verified by re-evaluating the derivative locally, not by a null
  projected step.
- **Independent validation (a rule, not a diagnostic).** Use 4,096 fresh coupled pairs at θ̂. The fit fails if
  `|res_k| > 4·SE_val,k` on any fitted moment. Also report A's equivalence statistic `|res_k|+2.2414·SE_val,k` against
  0.0003, and B's amplification diagnostic. On failure, make one pre-declared retry with M=4,096 for the fit, plus a
  fresh 4,096-pair validation. A second failure makes the cell a gap. Both attempts are recorded.
- **Reason for the 4σ test over A's 0.0003 equivalence.** Under coupling, SE_val is tiny at small a, so the test is
  strict exactly where mismatch would inflate the AUC. A 0.0003 residual still allows AUC 0.57–0.59 there. At large a,
  A's rule would create spurious gaps from legitimate matching noise (B's estimate: about 25% in L2 at a=0.3). The
  remaining matching noise is carried by the nuisance variance (D5).

## D5. Nuisance variance: local propagation (replaces the 40 refits)

- **At anchor-exact fits,** V_nuis = 0 analytically. The population AUC is exactly 0.5 for any independently trained
  score.
- **Elsewhere, take B=2,000 draws.** In each draw:
  1. Resample the matching pairs and solve the linearised shift Δθ_b from the fitted Jacobian.
  2. Project Δθ_b onto the parameter box, replicating the solver's boundary rule. If the solver's rule would return the
     boundary, the draw returns the boundary.
  3. Propagate to the null features of the training and reference sets by **per-realisation** linear drift, using CRN
     finite-difference stencils. The stencils cover matching, training and reference, one per parameter.
  4. Resample training networks within each class, keeping both events of a network together, and refit the frozen
     LDA.
  5. Compute AUC_b on the fixed reference. The social reference class may be reused.
- **Variance.** V_nuis is the **centred** variance of AUC_b. The mean shift mean(AUC_b − AUC_0), the MCSE of V_nuis via
  the fourth moment, and the fraction of projected draws are reported as diagnostics.
- **Max-t.** The max-t replicates add the same centred nuisance deviations, using the same resample indices across all
  strengths of an r. SE_total² = SE_scores² + V_nuis, with no division.
- **FD step.** Pre-declared at 0.01 per parameter in the confirmatory tiers. Gate G2 uses two steps, 0.01 and 0.005,
  to test stability. The step is never chosen by closeness to any benchmark.
- **Code path.** This needs an explicit successor code path. The frozen API accepting 30–50 refits is not reused with
  2,000 rows as if they were refits.

## D6. Scores, band and gates of the run itself

Frozen, unchanged:

- cluster-bootstrap on fixed scores (2,000 draws);
- logit studentisation with an SE floor at 1/(2n);
- per-r band with critical value **max(empirical max-t, 2.7729)**;
- inclusive inversion;
- sustained boundary;
- the per-run a=0 gate and its invalidation rules.

The run also reports how often the empirical max-t exceeds 2.7729.

## D7. Validation gate (all must pass before any v4 confirmatory seed is derived)

Code, criteria, allocation and hashes are fixed before the gate runs (freeze record). No rerun until pass. Failure means
documentation plus a new amendment. Criteria thresholds are **calibrated before the run on artificial data** that
reproduces the real denominators, dependence (LOO/pair structure, logit, heavy tails with kurtosis ≈8) and failure
counting. The target operating characteristics:

- P(pass | correct SE) ≥ 0.95;
- P(pass | SE understated by 20%) ≤ 0.20.

The gates:

- **G0, blind matching mask.** Covers 8 grids: B, A, C, D and E on the main channel, plus the three B controls. It runs
  on v4 calibration seeds with the D4 solver and validation. Outputs are statuses, evaluation counts, residuals in SE
  units and validation results only; no parameters, no AUCs. Passes if every a=0 fit of an identity family is
  anchor-exact, there are no `budget` statuses, and implementation-type statuses (numerical-limit, ill-conditioned) are
  ≤1% of fits. Family limits are gaps, not failures. Fits of the other families, channels and sensitivities are
  validated before their own training in the tiers.
- **G1a, identities.** Unit tests at full N as listed in D2, plus Δθ_b≡0 and V_nuis=0 at anchor-exact.
- **G1b, band mechanics on synthetic scores.** At production sizes: 2,000 networks × 2 events per class, 9 slots. It is
  a mechanics test, not an exactness claim. Scenarios:
  - ICC 0 and 0.5 Gaussian clusters;
  - non-Gaussian clusters;
  - ties;
  - dependence across slots.

  1,000 repetitions each. Pass: joint coverage ≥935/1,000 in each scenario.

- **G1c, end-to-end a=0.** The real pipeline (D2–D6), 50 repetitions at each of r ∈ {0.50, 0.70, 0.90}. Pass:
  - all fits anchor-exact;
  - ≤3/150 pointwise failures at 2.7729;
  - |mean AUC − 0.5| ≤ 3 SE;
  - tie rate reported.
- **G2, procedure-dispersion calibration.** Seven pre-declared cells: (0.003, 0.70), (0.01, 0.70), (0.03, 0.70),
  (0.10, 0.70), (0.30, 0.70), (0.03, 0.50) and (0.03, 0.90). Each gets 100 independent full pipelines (D4 + D5 with both
  FD steps + scores), arranged as 50 disjoint pairs.
  - **Primary statistic.** Per cell and pooled, the ratio of the empirical variance of the pairs' logit differences to
    the mean of SE_delta² (logit SEs). Two-sided criteria with bootstrap uncertainty: understated SE fails, and grossly
    inflated SE (>40%) fails. Thresholds come from the calibration above.
  - **Diagnostics.** The LOO-mean z-scores, tail counts at the 0.00556 level, FD-step stability (the V_nuis ratio for
    0.005 vs 0.01 must lie in [0.8, 1.25], otherwise fail) and the mean shift.
  - **Cells.** No fallback that drops cells. If G0 finds a G2 cell unattainable, the pre-declared substitute is the same
    a at the next eligible r toward 0.70, excluding r values already in G2; if none exists, the cell is dropped and the
    thresholds are recalibrated before the run.
  - **Scope.** G2 is not called a demonstration of absolute interior coverage.
- **G2c, local propagation vs full refits.** 100 full refits under the v4 solver and law at (0.10, 0.70) and 40 at
  (0.03, 0.70). Each refit comprises matching, validation, training and a fresh null reference. They are compared with
  the D5 V_nuis at those cells:
  - fail if the one-sided 95% bootstrap upper bound of Var_D5/Var_refit is < 0.8;
  - fail if its lower bound is > 2.0;
  - report the tails.
- **Sealing.**
  - Where results go: the G2 and G2c runners write per-repetition estimates, truths and SEs to a sealed JSONL file
    outside every git checkout. It sits under `~/.local/state/research-workbench/sealed-v4-gate/`, mode 0700, with its
    SHA-256 and an access log.
  - What may be printed: stdout, tracebacks and committed reports carry only criteria values, counts, ratios, MC SEs
    and pass/fail.
  - When it opens: unsealing only after the confirmatory results are committed.

## D8. Exposure and claims

Disclose cumulatively:

- the v1 exposures;
- AUC(0.30, 0.70) = 0.943912 under the v1 law (conditional on one fit and training set);
- the 26 v1 a=0 refit AUCs at r=0.70 (mean 0.530);
- proposal A's calibration values at r=0.70 under A's law and loose acceptance: 40 refits at a=0.10 had mean 0.756070
  (range 0.7317–0.7897), and one probe at a=0.03 gave 0.589413;
- proposal B's matching quantities at a>0;
- the G2 and G2c outcomes (criteria only).

These values do **not** determine a*(0.70) under v4. The grid has no monotonicity, and the law and algorithm changed.
They make r=0.70 **calibration-exposed**, and the global method was chosen after partial exposure. The paper describes
the v4 run as an evaluation, on new seeds, of a protocol amended after partial exposure, not as a fully blind
confirmation. The primary claim remains the whole curve over the full R grid, with provenance per r. The remaining eight
r values are not promoted to a new primary.

## D9. Inventory and execution window

- **Inventory.** The frozen inventory is kept in full, with no reduction. The tiers:
  - Tier 1: B on the main grid.
  - Tier 2: A, C, D and E.
  - Tier 3: the three controls × five nulls, plus mobility.
  - Tier 4: c=0.25/0.50, δ=0.10/0.20, and the exploratory c/δ combination.
  - Tier 5: b=0 and ω ∈ {0.25, 0.50, 0.75, 1}.
  - Tier 6: the 24-step sensitivity.

  A machine-readable inventory is committed (family × a × r × channel × sensitivity).

- **Dependencies.** Tier 1 alone supports only the comparison against B. Claims about interaction versus
  non-Gaussian persistence, error or mover–stayer require valid complete tier-2 grids.
- **Compute window.** It closes on **2026-10-18 23:59 America/Sao_Paulo (2026-10-19T02:59:00Z)**. The resources are 8
  local workers, plus optional shards on other hosts with the same code hash and a numerical-equivalence check. The
  tier order is fixed. It is never accelerated or reordered by AUC, width or invalidity.
- **Status at the close.** Each unit is recorded as `não iniciado`, `parcial por encerramento operacional`,
  `completo inválido` or `completo válido`, with all attempts preserved. Only planned complete units are reported as
  results, and the full inventory and absences are disclosed.
- **Supersession.** This window replaces v1's stop-and-amend-for-infeasibility rule.
- **Compute planning** (Codex critique, 8 dedicated workers, 25% reserve):
  - gate ≈ 65 h;
  - tiers 1–5 ≈ 139 h with four stencils, roughly 110 h with the two-stencil D5 choice;
  - tier 6 ≈ 94–118 h, a conservative scenario.

  Measure real cost in G0 before committing to the allocation.

## D10. Seeds

- New namespaces: `ic-detection-boundary-v4-calibration` (G0),
  `ic-detection-boundary-v4-gate-r{rep:04d}-calibration` (G1c, G2, G2c) and
  `ic-detection-boundary-v4-{nuisance,bootstrap,validation,stencil}-calibration`.
- Reserved, not executable before the gate passes and the release is recorded:
  `ic-detection-boundary-v4-{confirmatory,nuisance-confirmatory,bootstrap-confirmatory,validation-confirmatory,stencil-confirmatory}`.
- The v3 confirmatory reservation is retired.
- The material format and the collision audit are unchanged and extended to the new roles.
- The per-phase manifest records code, environment and host hashes.

## D11. Implementation requirements

- **Where the code lives.** One successor module (`ic_study/models/detection_panel_v4.py` and
  `ic_study/analysis/detection_boundary_v4.py`, or similar) plus gate runners. Frozen modules and runners stay untouched.
  Proposal A's byte-preserving transport optimisation is reused together with its tests.
- **Tests.** TDD is required.
  - identities (D2);
  - solver cases: known interior roots, every face and corner, beyond the family limits, a non-monotone profile,
    degenerate secants, NaN, budget counting, and the E6 and A block-7 stall regressions;
  - validation rule;
  - propagation: projection, Δθ≡0 at the anchor, linear shift within 5% of regenerated panels at a test point;
  - control propagation;
  - seed audit;
  - sealing (nothing sensitive on stdout).
- **Freeze.** The amendment document (PT-BR) and a freeze JSON record the SHA-256 of the amendment, the code and the
  calibrated criteria before any gate run.
