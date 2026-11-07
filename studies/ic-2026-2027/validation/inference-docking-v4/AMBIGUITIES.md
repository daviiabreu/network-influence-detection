# Spec ambiguities and chosen readings (Phase 1, clean-room)

Sources read before Phase 1 was committed: the seven documents named in the
docking brief. No `src/`, `tests/` or experiment scripts were opened. Tags
`Axx` are referenced from `docking_v4.py`. Items added after Phase 1 are
marked "(Phase 2)".

| Tag | Point | Chosen reading | Alternatives |
|---|---|---|---|
| A01 | `SE_k = sd(paired differences)/√M`: ddof | sample sd, ddof=1 | ddof=0 (relative difference ≈ 1/(2M) ≈ 5e-4) |
| A02 | Solver budget | 96 evaluations actually executed per attempt; cache hits are free; Jacobian evaluations used by the search count (v4.3). D4's 64 and R2's "stays 64" are superseded by item 11(c). | 64 |
| A03 | Sign convention and family-limit labels | residual = null − target, and L1 increases in φ. At the face used for the limits (η at its lower bound, or the one-parameter η), same-sign residuals at φ∈{0, 0.999}: positive → `family-limit-lower`, negative → `family-limit-upper`. At any other η the same situation is `no-L1-root`. | limits also classified at interior η |
| A04 | Lower-face rule | h(0)=L2 on the L1 profile. If `|h(0)|≤tol`, the endpoint is accepted without a step → `boundary`. If h(0)>tol, re-evaluate the profile at η=0.01: `h(0.01) ≥ h(0)` → `boundary` at η=0, otherwise `non-monotone-profile`. | a derivative threshold instead of ≥ |
| A05 | Degenerate secant or collapsing bracket | secant with fa==fb, or a step outside [a+10⁻³w, b−10⁻³w] → bisection. A bracket narrower than 1e-12 without acceptance → `ill-conditioned`. | `numerical-limit` |
| A06 | "Profile checked at every evaluated point" | the evaluated profile points, sorted by η, must be strictly increasing. Any decrease → `non-monotone-profile`; an exact tie → `ill-conditioned` (singular derivative). | a noise-tolerant check |
| A07 | Flat L2 profile (constant h) | zero derivative → `ill-conditioned`, even when h(η_max)<0 would otherwise mean `family-limit-upper` | `family-limit-upper` |
| A08 | NaN in validation or evaluation | any NaN evaluation → `numerical-limit`; a NaN validation residual fails validation | — |
| A09 | Retry trigger | only a validation failure triggers the M=4,096 retry. A solver gap is final (v4.3: "Falha de solver não ganha reinícios oportunistas"). The final status after two validation failures is a gap, called `validation-failed` here. | a gap also triggers the retry |
| A10 | FD stencil | one-sided forward step of +h, or −h when θ+h exceeds the upper bound ("sentido para dentro junto à face superior") | central differences |
| A11 | D5 projection | when η_b leaves [lo, hi], set η_b to the face and re-solve L1 linearly for φ (L1 priority); then clip φ to [0, 0.999]. Either event counts as "projected". | clip only |
| A12 | LDA inside D5 | not under comparison (it was docked in study 1). Phase 2 injects the project's AUC/LDA callable where needed, so that only the propagation is compared. | — |
| A13 | "Centred variance" V_nuis: ddof | ddof=1. MCSE = sqrt((m4 − m2²)/B), using central moments. | ddof=0 |
| A14 | SE_scores | sd of the bootstrap AUCs, ddof=1 | ddof=0 |
| A15 | Max-t quantile | `np.quantile(max_t, 0.95)`, linear interpolation. t = \|logit(clip(AUC_b + dev_b)) − logit(clip(AUĈ))\| / SE_logit, with the plug-in SE_logit carried to the draws. | other quantile definitions; not centring |
| A16 | 0/1 estimates | the band keeps the 0 (or 1) endpoint. The other endpoint uses the clipped logit. | — |
| A17 | "Before the first gap" | the first boundary and each inverted end must be at a grid index strictly below the first gap. Otherwise the result is None with reason `gap at a=<g>`, formatted `%g`. Without a crossing the reason is `not reached`. | — |
| A18 | Sustained boundary next to a gap | literal reading: the sustained boundary is declared when it lies above the last gap and every strength above it is available, even when the slot just below it is a gap. A top slot that is a gap → None with reason `gap`. | censor when the boundary sits directly above a gap |
| A19 | Sustained test "limite inferior >0,70" (v1) vs the inclusive inversion (≥) | inclusive ≥ throughout, per D6 ("inclusive inversion") | strict > for the sustained upper end |
| A20 | Jeffreys predictive | one failure rate p ~ Beta(0.5+k, 0.5+54−k) per simulated world, shared by all G2 cells and both G2c refit sets. Each count is Binomial(n, p) independently given p. The G2 pooled limit is ceil(0.02·100·cells). The seed and stream of the simulation are not specified, so it can only be compared in distribution. | independent p per stage |
| A21 | Validation residual at a face | the raw mean of the fresh pairs at θ̂ for every fitted moment, L2 at the face included (v4.3 text). A face whose L2 gap is large therefore fails validation. | residual measured against the fitted ḡ |

## Added in Phase 2 (after comparison with the project; the docking code was not changed)

| Tag | Point | Project reading (file:line) | Docking reading | Class |
|---|---|---|---|---|
| A22 | Logit SE inside the max-t draws | `se/(draw(1−draw))` evaluated at each draw (`analysis/detection_boundary_v4.py:624`), the same as frozen v1 (`analysis/detection_boundary.py:166`) | plug-in SE_logit at p̂ carried to every draw | (a). Material: the critical value differs by up to 2.1× (G01) |
| A23 | Replicate centring | `point + fixed − fixed.mean(0) + nuisance`, clipped to [0, 1] (`detection_boundary_v4.py:606`) | uncentred bootstrap AUC + centred nuisance | (a) |
| A15b | Max-t quantile | `method="higher"` (`detection_boundary_v4.py:626`, v1:168) | linear | (a) |
| A18b | Sustained boundary next to a gap | computed on the available grid (skipping gaps), then censored unless > last gap (`detection_boundary_v4.py:698-715`). More conservative. | run downward from the top, stopped at the gap | (a). The project reading is preferable |
| A03b | Family-limit labels | `profile_match` returns `no-L1-root` for φ beyond the box (face and one-parameter). Family limits come only from the feasibility pre-check in `fit_cell` (`simulation/detection_v4.py:325-345`), on the observed channel. | `family-limit-*` from same-sign residuals at the φ ends | (a). All are gaps; G0 counts neither label as implementation-type |
| A05b | Collapsing bracket | `numerical-limit` (`detection_boundary_v4.py:154`) | `ill-conditioned` | (a). Both are implementation-type in G0 |
| A06b | Monotonicity check | a decrease must exceed the larger tolerance and survive refinement; only sampled points are checked (`:205-217`) | strict at every sampled point; the docking samples η=0.8 early | (a). Path dependent (S09) |
| A24 | Label of a near-endpoint root | an interior secant iterate within tolerance → `interior` | endpoint checked first → `boundary` | (a). Both accepted; no gap impact (S21) |
| A25 | FD stability with a 0/0 ratio | ratio := 1 (`simulation/v4_criteria.py:183`) | NaN median | (a) |
| A26 | Projection with a non-positive Schur slope | `ValueError` (`detection_boundary_v4.py:441`) | solves the linear system | (a). The project's behaviour matches "a non-positive derivative is a failure" |
| A27 | MCSE of V_nuis | `(m4 − (B−3)/(B−1)·v²)/B` | `(m4 − m2²)/B` | (a). Relative difference ~5e-6 |
| A28 | z-scores of the validation diagnostic at 0/0 or NaN | 0 and inf | NaN | (a). Reporting only; pass/fail agree |
