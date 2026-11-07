# Independent review of cda3a92 (Claude, 2026-09-25)

I found three defects that should block the freeze, plus two cheap ones that are best fixed before it. All ranked findings are below, including the non-blocking ones.

I reviewed a clean export of `cda3a92`, because another agent is changing the worktree right now. **Tests:** `uv run --locked pytest -q` gives 274 passed. In my first run, two tests failed only because the export was not inside a git checkout. **Identity check:** I compared the v4 nulls against the freeze-time `influence_panel` from `9fe4264`, at full N with 1 and 24 steps. The latent panels are identical byte for byte for A, B, D and E.

### High severity (freeze-blocking)

**1. The code that builds the actual results is missing (D6/D9).** `pipeline` calls `score_uncertainty` with a single strength (`detection_v4.py:457`). Nothing combines the nine strengths of an r into one band, handles gap cells, applies the per-run a=0 gate, runs the tiers or writes the D9 unit statuses. `curve_report` has no caller. `preflight` hashes every file in src/tests (`v4_gate.py:40-70`), so adding this code after the gate breaks the frozen code binding.
- **Fix:** before the freeze, add and test a runner for each r × unit. It should stack scores to (2000,2,9) and nuisance deviations to (2000,9) under one seed plan, apply v1's gap rules and write the D9 statuses.

**2. The gate's pass probabilities ignore failures and the FD-step rule (D7).** `aggregate` fails G2, G2c or G1c on any single failed repetition (`v4_gate.py:374`). It also fails G2 if any one of 700 pipelines has a V_nuis ratio (0.005 vs 0.01) outside [0.8, 1.25] (`:478`). `criteria-v4.json` says the calibration "assumes zero technical failures" and a stable FD step. So P(pass | correct SE) ≈ 0.994 × (1−p_f)^840 × P(all 700 FD ratios in range). At a 0.5% gap rate that is about 0.015, not ≥0.95. D7 requires the artificial data to reproduce failure counting.
- **Fix:** declare a failure allowance counted in the denominators, calibrated against a stated bound on the gap rate.
- Bind G0's measured gap rate at the G2 cells in the R6 second record, with a stop rule if the resulting pass probability is below 0.95.
- Make the FD check one aggregate per cell (for example the median ratio) and include it in the calibration model.

**3. G2c compares two different variances.** The refit AUCs use a null reference drawn with fresh seeds for each repetition (`v4_gate.py:286`). D5's AUC_b uses the baseline's fixed null reference. So Var_refit also contains the null reference's sampling variance, about 1.2e-5 at AUC ≈ 0.75 and about 2e-5 near 0.59, which Var_D5 excludes by design. Compared with the nuisance scale seen in proposal A's refits (SD ≈ 0.013), this pushes the ratio down by roughly 7–20%. The calibration does not model this.
- **Fix:** regenerate the refit null reference at θ_refit using the baseline's seeds (`replace(seeds, repetition=0)`), as v1 did. Change the amendment wording to "regenerated at θ_refit with common random numbers".

### Medium severity (block the freeze; cheap to fix)

**4. The nuisance draws do not reproduce the boundary rule (D5 step 2).** `nuisance_draws` resamples centred differences (`detection_boundary_v4.py:381`), which drops the fitted residual. At a `boundary` fit the L2 residual can be several SE above zero, and the solver would keep η=0 on almost every resample. The linearised draws instead move about half of them into the interior. That inflates V_nuis and misreports the projected fraction exactly at small a, including the G2 cells (0.003, 0.70) and (0.01, 0.70).
- **Fix:** use `data.differences[indices_match].mean(0)` without centring. The AUC variance stays centred.

**5. Controls are not guarded when the observed fit fails.** `detection_v4.py:386` takes η from the observed fit even when that fit failed. Line 439 then indexes the empty `observed.nuisance` and crashes. G0 already handles this with a dependency gap; `pipeline` does not.
- **Fix:** if the observed fit failed or is missing, return a dependency-gap result.

### Non-blocking

**6. Identity tests are narrower than D2 asks.** Full panels are compared byte for byte only at the latent level. The channel test (`test_detection_v4.py:57-73`) compares five lag features from one realisation. Mobility, c=0.25, δ=0.10 and the c=0.50/δ=0.20 combination are not tested, and the mask and observed arrays are never compared.
- **Fix:** assert the bytes of mask, measured, observed and the selected features for every sensitivity at a=0.

**7. The solver accepts a bracket endpoint without a step.** It returns φ=0 or φ=0.999 as `interior` without a real solver step (lines 100–103, used at 157). Relabel these or require a step, as R2 states. Also, the retry gets a fresh 64-evaluation budget; the amendment should say so.

**8. The seed audit is incomplete.** It covers only 4 plans. Add the G1b, G1c and G2c plans and the stencil/nuisance/bootstrap namespaces.

**9. Sealing has one small gap.** The G2 summary prints `mean_shift`, in AUC units, to stdout (`v4_gate.py:487`). Move it to the sealed record or print only a ratio.

**10. A frozen file was edited.** `detection_panel.py` changed after the v1 freeze (SHA-256 a9d294e3… → aee84770…, commit `d33bf4e`), against D11's "untouched". The output is byte-identical (I verified this); record the change in the amendment.

### R1–R3 as revised
- **R1 is correct.** The residual variance is SE_fit² + SE_val², and the ≈14% false-failure rate reproduces. "SE_val ≤ 0.71·SE_fit" holds only for the M=1,024 attempt; on the M=4,096 retry it is 1.41.
- **R2:** the added error is 0.25² = 6.25% of the fit's variance, not "≤6%".
- **R3 is acceptable as a first-order approximation.** But G2c, the only check aimed at V_nuis, still passes 74.8% of the time when SE is understated by 20%, so G2 does most of the judging. R4's joint figure assumes V_nuis and total SE are understated by the same factor. G2 alone already meets the ≤0.20 target (4.67%).

### Verified correct
- **D2:** the null laws for B (iid normal trait), A, E, D and C.
- **D3/D10 seeds:** common random numbers only in matching and validation; independent classes; network clusters of two events; no way to derive confirmatory seeds; zero collisions in the audit as far as it goes.
- **D4 solver:** statuses, budget counting, the η=0 boundary check, one-parameter families, and controls holding η from the observed fit.
- **D5/D6 inference:**
  - projection onto the box;
  - V=0 and Δθ=0 at anchor-exact fits;
  - same resample indices across strengths;
  - band identical to the frozen rule (floor 2.7729 vs exact 2.77292);
  - logit floor 1/(2n).
- **D7:** the G0, G1b and G1c criteria.
- **D9:** the inventory is complete (46 × 81 = 3,726 rows).

**Freeze-blocking:** 1 (no curve runner), 2 (pass probabilities ignore failures and the FD rule), 3 (G2c reference mismatch), plus 4 (boundary residual in D5) and 5 (control guard), which are cheap to fix and should go in before the freeze.

**Non-blocking:** 6–10 and the R1/R2 wording notes.