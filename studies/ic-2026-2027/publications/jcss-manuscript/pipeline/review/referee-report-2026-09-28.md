# Adversarial pre-submission review before results — 2026-09-28

Two independent referee reports, followed by a pre-results risk register, a ranked list of changes and a list of factual inconsistencies. This is an internal challenge under `adversarial-review.md`, not journal peer review and not Research Owner ratification.

## Scope and conventions

- **Venue assessed:** JCSS (primary), JASSS (alternative). The guideline pages were not re-read for this review; `author-guidelines.md` and `pipeline/venue-compliance-checklist.md` are taken as given.
- **Source revision:** branch `integration/ic-20260928`, commit `8d286190`. `main.tex` SHA-256 prefix `f500f172eb5e84c1`. No PDF was compiled, because `sn-jnl.cls` is not in the repository. Section locators therefore refer to `.tex` files and their `\subsection`/`\paragraph` headings, not to page and line.
- **Result state:** the v4 gate (G0–G2c) and the confirmatory tiers are still running. No gate outcome, AUC, boundary or SHP anchor value is assumed anywhere below. Numbers quoted from the repository are protocol constants, engineering measurements or validation-study outputs, and each is labelled as such.
- **Frozen design:** nothing below proposes to change `freeze-v4.json` (`37513841`, record SHA-256 `99c42772…0837`), the amendment, D1–D11, R1–R8 or the review decisions. Anything that would change the confirmatory analysis is marked **(S)** and must be run and reported as a labelled exploratory or successor analysis.
- **Classification of each concern:**
  - **(T)** fixable by text;
  - **(E)** answerable from outputs the frozen design already produces;
  - **(S)** needs a successor or exploratory analysis, labelled as such;
  - **(X)** a limitation to state honestly.
- **Read for this review:**
  - the manuscript: `main.tex`, all 13 files in `sections/`, `claim-evidence.md`, `README.md`, the generated placeholders, and `pipeline/review/*`;
  - the v4 folder: `README.md` and `freeze-v4.json`, with every bound hash recomputed (see "Replication attempt");
  - the frozen documents: the amendment v4.3, D1–D11, R1–R8, the review findings and both decision records;
  - the frozen v1 preregistration and the v1 coverage-check report;
  - the three `validation/*/REPORT.md` files and the brief `v4-technical-validation.md`;
  - the positioning dossier;
  - the three SHP reliability files and the SHP guide;
  - selected code: `v4_curve.py`, `v4_plan.py:gate_tasks`, `v4_gate.py:source_hashes/preflight`, and a search of `detection_boundary_v4.py`, `detection_v4.py` and `detection_panel_v4.py`.
- **Not read:** `inventory.json` row by row; the large cost and verification JSONs; the full test suite; the related-work draft in the positioning folder.

### Replication attempt

- **Hashes.** Recomputing the SHA-256 of the files bound by `freeze-v4.json` on `8d286190` gives:
  - all six protocol-document hashes match;
  - `criteria-v43.json` and `inventory.json` match;
  - 80 of the 82 code hashes match. `pyproject.toml` and `uv.lock` differ.
- **Extra files.** `source_hashes()` (`src/ic_study/simulation/v4_gate.py:42`) would also pick up nine `.py` files that are not in the freeze closure (see F11). So `preflight` cannot pass on this branch; it passes only on the frozen tree.
- **Freeze record.** The SHA-256 of `freeze-v4.json` is `99c4277235d4…0837`, which matches the value printed in `methods.tex`, "Protocol history".
- **Not run.** No simulation, test or gate was run. The docking reports are the only independent execution evidence.

---

## Referee 1 — agent-based models of opinion dynamics and their empirical validation

### How I understand the paper

The authors build a synthetic 11-wave panel with SHP-like geometry. It has 10,626 people in two-person households, entry at waves 0 and 5, retention 0.89, and latent states that evolve while people are unobserved.

- **Interaction arm.** Each person has eight random directed in-partners, formed by eight uniform permutations. The drift is bounded-confidence-with-repulsion (attraction within distance 1, repulsion −0.25g beyond) and is standardized across the population. A nominal share $a$ of an AR(0.85) innovation goes to this drift, and the whole population is rank-transported to fixed normal quantiles at every step.
- **Nulls.** Five no-network families (A–E) share the same transport. At $a=0$, A, B, D and E coincide with the interaction arm path by path.
- **Observation.** Both arms pass through $w=\sqrt r z+\sqrt{1-r}e$ and are then rank-allocated to 11 equiprobable categories per wave.
- **Matching.** Each null is fitted to the interaction arm's mean pooled lag-1 (and lag-2) correlation, over 1,024 coupled panels.
- **Discrimination.** A fixed shrinkage LDA on pooled lag-3–5 correlations separates whole panels. The target is the expected population AUC.
- **Estimand.** The primary result is the whole curve $a^*(r)$: the first grid strength at which the AUC reaches 0.70 against the trait-plus-AR null B, for nine values of $r$. It is reported with a sustained-crossing variant, within-$r$ simultaneous bands, gaps and censoring.
- **History.** The design is a successor (v4) of a v1 protocol whose zero-strength gate failed. It is being executed after partial exposure at $r=0.70$.
- **Empirical content.** None yet. An SHP reliability anchor is preregistered separately and will be drawn as a point over the grid.

### Editor-only rationale

The protocol engineering is unusually careful: freeze records, sealing, failure accounting and two clean-room dockings. None of that is the problem. The problem is that the scientific object is narrower than the framing.

Given this generator (a random network with no structure, rank transport at every step, standardized drift), the "interaction" signal that the fixed discriminator can see is, to first order, a nonlinear dependence of change on a person's own state. A no-network process can produce that. The paper therefore measures when a lag-3–5 LDA can tell a specific S-shaped nonlinear persistence process from trait-plus-AR under a known response channel. That may be a useful methods result for JASSS. For JCSS it will read as a narrow simulation exercise with no empirical anchor, unless the paper states what $a$ means in observable terms and what an analyst holding one real panel could conclude.

**Recommendation in current form:** reject; major revision if items 1–5 of the ranked list are done. Results are absent, so this judges the design and the text only.

### Rubric (reviewer-2 criteria of `adversarial-review.md`, opinion dynamics and ABM)

| Criterion | Score | Evidence locator | Reason and decisive check |
| --- | --- | --- | --- |
| Mechanism fidelity | 1 | `methods.tex` "Design, panel and observation"; `appendix-odd.tex` Submodel 3 | The rules are explicit and dock bit for bit. Calling the mechanism "bounded confidence" is misleading once $R_N$ is applied every step (M2), and its mean-field content is unstated (M1). Check: mean-field twin null (S). |
| ODD completeness | 2 | `appendix-odd.tex` | Complete and reimplementable, as the docking confirms. It needs the band-studentization reading and the unstated consequences listed below. |
| Validation | 0 | `results.tex`, `ODD03` | No empirical pattern is reproduced or tested. The patterns P1–P4 are imposed design targets. The SHP anchor places $r$, not the mechanism. |
| Interpretation | 1 | `discussion.tex`, `related-work.tex` last ¶ | Causal language is well guarded. The "interaction versus persistence" framing still overstates what B-only separation means (M1, M5). |
| Replicability | 2 | `verification.tex`, `validation/*` | Excellent provenance. Platform dependence and branch-level preflight failure are not disclosed (F10, F11). |

### Major concerns

**R1-M1. The interaction arm is, to first order, a no-network nonlinear individual process. The paper never says so.**

- **Location:**
  - `methods.tex` "Design, panel and observation", ¶2;
  - `appendix-odd.tex` Submodel 3 (`ODD20`) and ODD05;
  - `introduction.tex` ¶5 ("interaction-like generator … no-network updating");
  - `discussion.tex` ¶1–2.
- **Concern:** The partners are eight uniform random permutations of $N=10{,}626$. The network has no clustering, no homophily and no locality. Every step re-imposes an exact $N(0,1)$ rank marginal.
  - Conditional on $z_i$, the drift $D_i=\frac18\sum_k f(z_{\pi_k(i)}-z_i)$ therefore has expectation $m(z_i)=\mathbb E_Z f(Z-z_i)$, plus neighbour-sampling noise of variance about $\mathrm{Var}f(Z-z_i)/8$.
  - Correlation between neighbours builds only slowly on a locally tree-like graph.
  - Near the centre, $m(z)$ pulls a person toward the mean, because most partners are within distance 1. In the tails it pushes the person further out, because most partners are beyond distance 1 and the repulsion $-b g$ acts.
  - So the interaction arm is approximately an individual AR process whose conditional mean depends on the person's own state through an S-shaped function. Its innovation variance also depends on that state.
  - This is the class that null D ("stable tails, volatile centre") targets, with a different functional form.
  - The fixed discriminator sees only pooled lag correlations. It cannot use anything that is specifically social, such as correlation between partners' changes, because partners are never observed.
- **Why it matters:**
  - A referee will say that $a^*(r)$ against B measures detectability of nonlinearity or non-Gaussian persistence, not of interaction.
  - It also bears on the title ("distinguish interaction-like updating from persistence").
  - The linear analytic control in the frozen v1 protocol ("Mecanismos e significado de a", last ¶) already shows that linear global assimilation is exactly AR. The authors know that only the nonlinearity creates separation, but the manuscript does not carry that argument.
- **Already answered?** Partly.
  - The v1 preregistration says "kernel não linear pode produzir copulas e decaimentos não reproduzidos pelo AR gaussiano … não garante que ela exista contra nulos mais flexíveis".
  - The rule "B crosses, D below target ⇒ compatible with non-Gaussian persistence" is in v1 "Discriminador e interpretação dos canais" and is paraphrased in `discussion.tex` ¶2.
  - This is inadequate. The manuscript never gives the mean-field argument, never presents the linear-control non-attainment, and treats D as a secondary refinement rather than the natural competitor.
- **Classification:**
  - (T) Add the mean-field argument and the linear-control result to Methods, and reframe the title and abstract.
  - (X) State the limitation.
  - (S) Exploratory "mean-field twin" null, labelled as a successor analysis: replace the network drift by $\bar m(z_i)$ plus independent noise with matched variance, with no network. Report its AUC against the interaction arm at the tier-1 cells. If the AUC is near 0.5, the network contributes nothing identifiable, and the paper should say so.

**R1-M2. "Bounded confidence with repulsion" is nominal under per-step rank transport and standardized drift.**

- **Location:** `methods.tex` "Design", ¶2; `appendix-odd.tex` ODD08, ODD20; `background.tex` C16–C24, A04–A05.
- **Concern:**
  - $R_N$ re-imposes the same marginal at every step, and the drift is standardized to unit variance before entering the update.
  - The model therefore cannot produce clustering, fragmentation or bipolarization. These are the macro signatures that define bounded-confidence and repulsion models in the literature the background reviews (C17, C20, C23).
  - The confidence distance is 1 on a unit-variance scale that is re-imposed every step, so the share of partners within the bound is fixed at about $P(|N(0,2)|\le1)\approx0.52$ for everyone and every wave.
  - Background A04/A05 argue that marginals do not identify mechanisms, which is true. But here marginals are identical by construction, so the manuscript's long discussion of macro outcomes is irrelevant to the design.
- **Why it matters:** An opinion-dynamics referee will object that the generator is bounded confidence only in the local sign of the kernel. Transport of $a^*$ to BC models as usually understood (Deffuant–Weisbuch, Hegselmann–Krause) is not justified.
- **Already answered?** `v1` "Painel e canal" says the transport "retira informação marginal". That concerns the observation channel, not the latent dynamics. Inadequate.
- **Classification:** (T) Describe the generator as "a rank-transported AR process with a bounded-confidence-shaped, standardized partner drift" and state the lost macro behaviour. (X).

**R1-M3. The strength $a$ has no observable meaning, and the promised mapping is not produced.**

- **Location:**
  - `methods.tex` "Design", ¶2 ("nominal pre-transport innovation share");
  - `supplement.tex` "Panel channels and null mechanics" ("A diagnostic reports the incremental partial $R^2$ of drift beyond the previous state");
  - v1 frozen protocol, "Mecanismos e significado de a" ("Reportar o mesmo mapeamento R² por a/etapa/b no futuro estudo").
- **Concern:**
  - Readers need to know whether $a^*=0.10$ is large or small in substantive terms.
  - v1 committed to reporting a realized partial-$R^2$ map. The supplement asserts it is reported.
  - No such computation exists in the frozen v4 code path. I searched `detection_v4.py`, `detection_panel_v4.py`, `v4_curve.py`, `v4_gate.py` and `v4_plan.py`, and none contains it (F4).
  - The v1 diagnostic value $\approx0.77a$–$0.96a$ was measured at $b=0$ under the v1 law, and the protocol itself forbids transferring it.
- **Why it matters:** Without this map, no reader can relate $a^*(r)$ to any fitted opinion-dynamics parameter, for example Gestefeld–Lorenz, or to a realized share of change.
- **Classification:**
  - (T) Remove the false sentence from `supplement.tex` now.
  - (S) Run the partial-$R^2$ map as a labelled successor diagnostic on fresh non-confirmatory seeds. It needs no training and no AUC, so it cannot contaminate the confirmatory analysis. Report it by $a$, $b$ and step count.

**R1-M4. One fixed generator configuration; the realism rests on geometry only.**

- **Location:** `appendix-odd.tex` ODD06, ODD15; `methods.tex` "Design".
- **Concern:**
  - $\rho=0.85$, $b=0.25$, degree 8, random topology, no burn-in and one step per wave are all fixed.
  - Only $b=0$, anchoring $\omega$ and 24 steps are varied.
  - The interaction arm's lag profile is never compared with the SHP item's lag profile. v1 deliberately "não inventa ACF empírica". So the synthetic panel may sit far from SHP in persistence even though its geometry matches.
  - The 24-step sensitivity uses the same per-step $\rho$. The effective annual latent persistence without drift then falls to roughly $0.85^{24}\approx0.02$. This changes the dynamics wholesale; it is not a change of "temporal resolution" with the dynamics held fixed. It will likely produce low-$L_1$ targets, infeasible cells and family-limit gaps.
- **Why it matters:** An ABM referee will ask whether the boundary is specific to one arbitrary parameter point. The "SHP-like" label invites a comparison the paper does not make.
- **Already answered?** v1 "Mecanismos" motivates the 24 steps by Gestefeld–Lorenz's approximately 24 steps a year. It does not address the persistence change. Inadequate.
- **Classification:**
  - (X) Single configuration.
  - (T) Explain what the 24-step scenario changes.
  - (E) Once the SHP anchor exists, compare its fitted $\hat\phi$ and observed lag-1 with the interaction arm's matching targets by cell. The targets are among the matching outputs; G0 publishes only statuses and residuals in SE units, so the targets come from the tier fits.
  - (S) Any calibration of $\rho$ to SHP is a successor.

**R1-M5. The confirmatory null is the weakest relevant competitor, and the only tier guaranteed to finish supports a claim only about it.**

- **Location:** `methods.tex` "Inventory and execution status" ("Tier 1 supports a claim only about B"); spec D9; `discussion.tex` ¶2.
- **Concern:**
  - Given R1-M1, D (and plausibly E) is the natural no-network competitor. B is not.
  - According to `compute-projection-v42.json`, tier 1 costs 3.5 h in the "measured" scenario and 10.4 h with 25% retries, while tier 2 costs 12.5–35.9 h. So tier 2 is likely to complete if the gate passes, but nothing guarantees it.
  - A paper whose headline is "B-separable" while D is inconclusive or absent says little about interaction.
- **Why it matters:** This decides whether the paper has a substantive result at all.
- **Classification:** (X) The frozen primacy of B cannot change. (T) Pre-commit in the text that the headline sentence will report B and D side by side whenever tier 2 is complete and valid. (E) The tier-2 outputs.

**R1-M6. No empirical validation, and unused household information in the SHP.**

- **Location:** `methods.tex` "Design", ¶1 ("No exposure network is observed in that panel"); `appendix-odd.tex` ODD05, ODD13 (households matter only for attrition).
- **Concern:**
  - The SHP interviews every household member aged 14 and over, so co-resident partners answer the same trust item.
  - That is a partial, observed exposure structure: the dyad. The actor–partner literature the paper already cites (Kim & Kim 2024) exploits exactly this.
  - The synthetic households carry no opinion coupling, and the manuscript's statement that no exposure is observed is too strong for the SHP.
- **Why it matters:** For JCSS, a referee will ask why the one observable social tie in the motivating data is ignored while the paper argues that exposure is unobserved. For JASSS, the purely synthetic scope is acceptable if it is explicit.
- **Classification:** (T) Qualify the sentence: "no network beyond co-residence". (X). (S) A household-coupled generator and a dyadic discriminator are future work and should be named as such.

**R1-M7. The "upper bound on the optimal discriminator" statement is correct but almost uninformative.**

- **Location:** `related-work.tex` last ¶; `appendix-odd.tex` ODD08; `claim-evidence.md` R21.
- **Concern:**
  - Population LDA AUC ≤ Bayes AUC, so a crossing $a^*$ upper-bounds the optimal first crossing on the same grid. That holds.
  - But the Bayes-optimal procedure uses person-level trajectories of 10,626 people, not three pooled correlations. It is probably far more powerful, so the bound says little about fundamental detectability.
  - The inequality holds for population quantities. The estimated $\hat a^*$ and its band inversion are not bounds.
- **Why it matters:** Readers will over-read "upper bound" as "conservative estimate of the detection limit".
- **Classification:** (T) State that the bound applies to population quantities and is likely loose. (X).

### Minor concerns

1. **Off-topic background.** `background.tex` "Discrete states and group influence" (C08–C15) and most of "Social impact, networks, and outcomes" (C25–C30) do not bear on the design. Voter, Sznajd and $q$-voter dynamics are not used. The space is better spent on trait–state measurement models (see R2-M1). (T)
2. **Unrelated supplement material.** `supplement.tex` begins with `\input{sections/systematic-map}`, `systematic-map-background` and `systematic-map-flow`: a 43,906-proposal broad map with red `[TBD]` placeholders, unrelated to this paper. The manuscript README says the map is "entrega separada". Remove it. (T)
3. **Missing interpretation regions.** The frozen v1 interpretation regions are absent from the manuscript: small $0<a^*\le0.03$, large $0.03<a^*\le0.90$, not attained on a complete eligible grid, and censored or indeterminate (v1 "Pergunta e estimandos", ¶3). `discussion.tex` ¶1 speaks of "a small attained boundary" and "a larger attained boundary" without the frozen cut. Use the frozen labels and say that 0.03 is an internal convention. (T)
4. **Coarse grid.** Between 0.10, 0.30, 0.60 and 0.90 the grid is coarse. The v1 precision planning (v1 "Poder para resolução…") gives a 43.9%/19.2% probability of a one-step interval when the AUCs bracketing the boundary are 0.66/0.74. Say in advance that intervals spanning several grid points are expected, and that $a^*$ values are grid indices, not continuous estimates. (T/X)
5. **Anchoring $\omega=1$.** This is declared a degeneracy in which latent states never change whatever $a$ is. Pre-state how a unit that is complete-valid or complete-invalid at $\omega=1$ will be read. It is not informative about $a$. (T)
6. **Terminology.** "interaction-like updating", "interaction-driven innovation", "reorganization" and "influence" are used interchangeably across the abstract, introduction, ODD02 and v1. Fix one term. (T)
7. **Late tiers.** The measured-scenario total of 256 h fits the roughly 550 h window between the freeze (25 Sep) and the close (18 Oct). The 25%-retry scenario (726 h) does not. Tier 3 alone is 93–270 h. The paper should expect tiers 3–6 to be partial and should not promise the controls in the introduction ("It separates latent, error-free ordinal and observed channels…"). (T/X)
8. **Unanchored title.** The title's "When do…" promises conditions that a single generator and a single discriminator cannot deliver. Consider "How much nominal drift…" or similar. (T)

---

## Referee 2 — survey methodology: panel reliability, measurement error, longitudinal models

### How I understand the paper

The authors ask at what nominal strength a specific simulated influence process becomes separable from matched no-influence persistence models. The data are an 11-wave panel with SHP-like attrition and refreshment, and the observed responses are $w=\sqrt r z+\sqrt{1-r}e$ with $r$ fixed on a grid from 0.50 to 0.90, then rank-coded into 11 equiprobable categories.

- **Confirmatory null (B).** A latent trait plus AR(1) process, rank-transported. With the classical error channel added, B is a trait–state–error (STARTS-like) data-generating process.
- **Matching.** B is matched by two parameters $(\phi,\lambda)$ to the mean pooled lag-1 and lag-2 correlations of 1,024 simulated interaction panels. Both arms use the same, known $r$.
- **Discrimination and uncertainty.** A pooled lag-3–5 LDA separates whole panels. Uncertainty combines a network-cluster score bootstrap with a linearized "nuisance" variance for matching and training. Bands are simultaneous within each $r$.
- **Gates.** The gate checks exact identities at $a=0$, band mechanics on synthetic scores, and dispersion of standard errors at seven cells.
- **SHP anchor.** A separately frozen quasi-simplex FIML model will estimate the 2004 reliability of the SHP trust item. It will be drawn over the $r$ grid.

### Editor-only rationale

From a panel-measurement standpoint, the design assumes away the two things that make the empirical question hard. First, reliability is known and identical in both arms; the null is never allowed to trade error variance against trait variance. Second, the null is matched to the population moments of the alternative, not to one observed panel. On top of that, the chosen target (AUC 0.70 across replicate panels) corresponds to weak single-panel power, and the features differ by fractions of a hundredth of a correlation.

The empirical anchor is a model without a trait. Under the paper's own confirmatory null, such a model is biased, and it is defined on a different scale from the simulation's $r$. As written, the curve cannot be read at the anchor.

All of this can be fixed with text, disclosure and three labelled exploratory analyses. None requires touching the frozen design. **Recommendation in current form:** reject. Major revision is feasible.

### Rubric (reviewer-1 criteria of `adversarial-review.md`, methods and statistics)

| Criterion | Score | Evidence locator | Reason and decisive check |
| --- | --- | --- | --- |
| Estimand and comparison | 1 | `methods.tex` "Boundary…"; spec D1 | Operationally precise. The estimand depends on the procedure (oracle $r$, oracle target, $M$) in ways the text does not state (M1, M2, M9). |
| Sampling and measurement | 1 | `methods.tex` "Design…"; SHP prereg | Attrition is assumed MCAR and waves stationary. Simulation $r$ and anchor $r$ are different estimands (M4, M5). |
| Calibration and validation | 2 | Methods "Protocol history"; D7/D8 | Exposure disclosure and gate discipline are strong. The disclosure is incomplete after 27 Sep (F9). |
| Statistical inference | 1 | Methods "Boundary, uncertainty…"; `inference-docking-v4/REPORT.md` §6 | Interior coverage is untested. The band's studentization reading is undocumented in Methods. The whole-curve shape is not covered by any simultaneous band (M6, M7). |
| Reproduction | 2 | `freeze-v4.json`; `validation/host-equivalence-homelab/REPORT.md` | Exact on macOS arm64 only (F10, F11). |

### Major concerns

**R2-M1. The null is given the true reliability; the trait–error trade-off that drives identifiability in real panels is removed.**

- **Location:** `methods.tex` "Design", ¶3 and "Matched null families", ¶1–2; `appendix-odd.tex` Submodel 5 and ODD26; `introduction.tex` ¶5 ("Reliability is fixed outside the outcome analysis").
- **Concern:**
  - In both arms $r$ is the same known constant. B can move only $(\phi,\lambda)$ and is matched only on $L_1$ and $L_2$.
  - In the trait–state–error literature, the error share, the trait share and the autoregression are notoriously hard to separate in panels of this length:
    - Kenny and Zautra's STARTS;
    - Cole, Martin and Steiger's trait–state–occasion model;
    - Lüdtke, Robitzsch and Wagner (2018) on STARTS estimation problems;
    - Lucas and Donnellan (2012), whom the paper already cites for an SHP item.
  - A B-type null that may also choose its own error variance (three parameters, matched on $L_1$–$L_3$) could absorb part of the lag-3–5 signal that the fixed LDA uses.
  - The curve therefore answers "detectability given that the analyst knows $r$ exactly". An analyst holding the SHP has at best the anchor's interval, whose value depends on the model.
- **Why it matters:** This is the central identification issue for a survey audience. Without it stated, a methods referee will read the curve as optimistic by construction.
- **Already answered?** Partly. v1 "Painel e canal" and `related-work.tex` ¶4 say $r$ is "a sensitivity parameter, not an empirical estimate". That is about transportability, not about the null's lack of freedom over $r$. Inadequate.
- **Classification:**
  - (X) State it in the Discussion as a structural limitation.
  - (T) Rename the estimand in prose to "detectability at known response reliability".
  - (S) Exploratory successor: a "free-$r$ B" null (trait + AR + error, three parameters, matched on $L_1$–$L_3$, discriminator on $L_4$–$L_5$, or the frozen LDA with $L_3$ dropped) at the tier-1 cells. Label it as not part of the confirmatory curve.

**R2-M2. The null is fitted to the alternative's population moments (an oracle target), not to one observed panel.**

- **Location:** `methods.tex` "Matched null families", ¶2 ("matched … averaged across panels"); `supplement.tex` "Profile fit and validation details"; spec D4 ("A 0.0003 residual still allows AUC 0.57–0.59").
- **Concern:**
  - Matching uses the mean of $L_1$ and $L_2$ over $M=1{,}024$ (or 4,096) interaction panels, and $V_{nuis}$ propagates only that matching noise.
  - An analyst with one SHP panel fits the null to one realization. The standard error of the target is then about $\sqrt{1024}=32$ times larger, and the matching error would dominate.
  - The spec's own remark shows how sensitive the AUC is: a lag-correlation residual of $3\times10^{-4}$ can move the AUC to 0.57–0.59.
  - The estimand is thus a property of two laws. It is not a property of a test an empirical researcher could run.
- **Why it matters:** The introduction motivates the paper by what an annual survey can reveal (¶3–4). The design answers a different question.
- **Classification:**
  - (X) State the population-level scope explicitly.
  - (T) Remove any wording implying that a single panel is being tested.
  - (S) Exploratory successor: a single-panel parametric-bootstrap test. Fit B to one interaction panel, simulate the null distribution of the LDA score, and record the rejection rate. This directly gives single-panel power at the tier-1 cells.

**R2-M3. AUC 0.70 across replicate panels corresponds to weak single-panel power and minuscule feature differences.**

- **Location:** `methods.tex` "Boundary, uncertainty and validation" (target 0.70); `discussion.tex` ¶1.
- **Concern:**
  - Under equal-variance normal scores, $\mathrm{AUC}=\Phi(\delta/\sqrt2)$. The primary target 0.70 corresponds to $\delta\approx0.74$ SD of the panel-level score.
  - A one-sided single-panel test at $\alpha=0.05$ with a known null distribution then has power $\Phi(0.74-1.645)\approx0.18$. The secondary targets give about 0.10 at AUC 0.60 and about 0.33 at AUC 0.80.
  - In feature units the differences are tiny. At $N=1{,}002$ the docking study's 0.20 SD margin equals about 0.002–0.005 correlation units (`validation/docking-v4/REPORT.md` §5, "Resolução"). At $N=10{,}626$ the panel-level SD is smaller still.
  - Such differences are far below plausible misspecification in the real item: wave-specific reliability, mode, MNAR attrition, period effects in trust, and heaping at 5 and at the extremes.
- **Why it matters:** A reader will take "detectable at $a^*$" to mean "an analyst would detect it". The target does not support that reading.
- **Already answered?** No. v1 notes that N changes separability and stays fixed. That is not a power translation.
- **Classification:**
  - (T) Report the normal-theory translation of 0.60/0.70/0.80 into $\delta$ and single-panel power in Methods.
  - (E) Apply the same transformation to the released AUC point estimates and bands as a clearly labelled descriptive re-expression. The released curve records contain `auc`, `lower` and `upper` (`v4_curve.py:complete_curve`).
  - (X) Say that the scores are not guaranteed to be normal.

**R2-M4. The SHP anchor and the simulation's $r$ are different estimands, and the anchor model omits the trait that the confirmatory null contains.**

- **Location:** `appendix-odd.tex` ODD17; SHP prereg "Pergunta, população e estimando" and "Relação com a curva v4"; brief item 12.
- **Concern:**
  1. **No trait in the anchor model.** The anchor is a quasi-simplex latent AR(1) with no stable trait. If the true process contains a trait, as B assumes, simplex-type estimators misattribute the long-lag plateau.
     - For example, with latent correlations $\lambda+(1-\lambda)\phi^k$, $\lambda=0.5$, $\phi=0.5$ and $r=0.7$, observed $L_1=0.525$ and $L_2=0.4375$.
     - Heise's $L_1^2/L_2$ is then about 0.63, not 0.70.
     - An 11-wave simplex is pulled further, because it must fit the plateau with a high $\phi$.
     - All three frozen sensitivities (Heise, Wiley–Wiley, polychoric Heise) belong to the same simplex family.
  2. **Different scales.** The simulation's $r$ is a signal share before an equiprobable 11-category rank discretization, which adds its own error. The anchor treats the heaped and skewed 0–10 responses as continuous.
  3. **Anchor year.** The 2004 anchor wave is the SHP refreshment wave (wave 5 in the synthetic geometry as well). Roughly half of the respondents give their first interview then. This mixes tenure, which is the very effect the conditioning sensitivity models.
- **Why it matters:** Drawing $\hat r_{2004}$ over the grid invites the reader to read off $a^*$ at the SHP's reliability. With a downward-biased anchor on a different scale, that reading can be wrong by several grid steps of $r$.
- **Already answered?**
  - ODD17 says the two are "comparable only approximately".
  - The SHP prereg forbids extrapolation and forbids choosing $r$ after results.
  - Both are necessary but not sufficient. Neither addresses the trait bias or offers a crosswalk.
- **Classification:**
  - (S) Crosswalk, exploratory and cheap, with no LDA. Apply the frozen anchor estimators (the 11-wave quasi-simplex and the Heise triplets) to synthetic observed panels from B and from the interaction arm at each $(a,r)$ cell, using fresh non-confirmatory seeds. Report $\hat r_{\text{anchor}}$ as a function of the simulation's $r$. Then draw the anchor through that map, alongside the raw placement.
  - (S) A linked successor to the SHP prereg adding a trait–state–error (STARTS) sensitivity. It must be registered before the SHP result is seen, or declared post hoc.
  - (T) Discuss the 2004 refreshment wave.

**R2-M5. All nulls and the alternative are stationary, MCAR and correctly specified; there is no robustness to measurement-model misspecification.**

- **Location:** `methods.tex` "Design", ¶1 (attrition independent of opinion); `appendix-odd.tex` Submodel 2; SHP prereg "Amostragem, ausência e modo" (which itself anticipates MNAR).
- **Concern:**
  - Both arms share the same exact channel, mask and marginal. The only permitted mismatch is the mechanism.
  - Real panels violate this in ways that change $L_3$–$L_5$ by far more than 0.005: attrition related to political trust, time-varying reliability, mode or wording changes, period shocks, and the 2004 refreshment sample differing in composition.
  - The declared channels C, $c$ and $\delta$ apply to both arms (except C's null arm), so they test robustness to a shared channel, not to a mismatch between the arms.
- **Why it matters:** If a small misspecification of the null separates the arms as easily as interaction does, the boundary says nothing about real data.
- **Classification:**
  - (X) State it.
  - (S) An exploratory stress test: B with wave-varying $r$, or with MNAR attrition, against a correctly specified B at $a=0$. That is, compute the "AUC of misspecification" and compare it with the frozen curve. Label it as exploratory.

**R2-M6. Validity of the interior inference is not established, and the implemented band rule is not described in Methods.**

- **Location:**
  - `methods.tex` "Boundary, uncertainty and validation", ¶3–4;
  - `verification.tex` "Gates";
  - `appendix-odd.tex` ODD33;
  - `validation/inference-docking-v4/REPORT.md` §6;
  - brief item 1.
- **Concern:**
  1. **The zero-strength checks are nearly guaranteed to pass.** At $a=0$, A, B, D and E are anchor-exact by construction, so the per-run null gate and G1c test only score-band mechanics. They cannot detect the main interior risk: AUC inflation from matching bias. That bias is bounded at $0.25\,\mathrm{SE}_{fit}$ and is deliberately excluded from $V_{nuis}$ (R2).
  2. **G2 checks dispersion only.** G2 compares standard-error dispersion at seven cells. It does not test coverage of the true AUC, and "truth" is unknown at $a>0$ (amendment, "Selamento").
  3. **G1b runs with zero nuisance.** The joint coverage of the max-$t$ band with a non-zero $V_{nuis}$ added is therefore never tested.
  4. **The band reading is undocumented in Methods.** The critical value uses the logit standard error studentized in each replicate, centred on the point estimate, with the `higher` quantile. The inference docking shows that a plug-in reading gives critical values up to 2.1 times larger (7.15 against 3.37 in its case 4). v1's wording ("SE plug-in total é transportado aos draws") admits both readings. ODD33 describes the implemented reading, but Methods does not.
  5. **The calibration target is not demonstrably met.** The joint pass probability is 95.17% (MCSE 0.39 percentage points; amendment lines 409–412), which is not shown to be at least 0.95. Methods states only the target.
- **Why it matters:** A methods referee will ask for evidence that the bands cover at $a>0$. They will also notice that the width of the band depends on an implementation choice.
- **Already answered?** Partly. Methods says "G2 tests dispersion, not absolute interior coverage", and ODD33 gives the formula. The disclosure is honest but scattered, and Methods lacks the studentization choice and its sensitivity.
- **Classification:**
  - (T) In Methods, describe the implemented studentization, the zero-nuisance scope of G1b, the achieved 95.17% ± 0.39 pp, and bias outside the variance.
  - (E) Report the frozen diagnostics:
    - the frequency with which the empirical max-$t$ exceeds 2.7729 (D6);
    - the covariance-Jacobian flags (G2);
    - the per-cell FD medians;
    - the projected-draw fraction;
    - after unsealing, the G2 `mean_shift`.
  - (X) Absolute interior coverage is unverified.

**R2-M7. Whole-curve claims have no joint inference.**

- **Location:** `methods.tex` "Boundary…", ¶4 ("simultaneous within each $r$, not across all 81 cells"); v1 "Inferência viável e validade" ("Qualquer afirmação simultânea da curva inteira exige banda adicional de 81 células").
- **Concern:**
  - The primary estimand is the whole curve, yet no simultaneous statement over $r$ is prespecified.
  - "a* decreases with r", "a* is finite for $r\ge0.7$" and similar shape statements are therefore descriptive only.
  - In the tiers, seeds are independent across $r$ (brief item 4; `v4_curve.py:CurveUnit.seeds`). So apparent non-monotonicity in $r$ can be pure noise.
- **Classification:** (T) Pre-commit that shape-in-$r$ statements are descriptive. (X). (S) An 81-cell band, if wanted, must be labelled post hoc.

**R2-M8. The primary curve can be invalidated by chance or by the clock.**

- **Location:** `methods.tex` "Boundary…", ¶4 ("failure of B at any eligible $r$ blocks validation of the primary curve"); `simulation/v4_curve.py:_close_inventory`; brief item 8.
- **Concern:**
  - With a correct procedure and a critical value of at least 2.7729, the pointwise probability that the $a=0$ band misses 0.5 is at most 0.0056. Across nine B units, the chance that at least one misses is up to about 4.9%, which would invalidate the primary curve with no substantive cause.
  - Separately, the code invalidates the main curve if any tier-1 unit is not complete-valid at the close, including units not started. Methods does not say this (F20).
- **Classification:** (T) Disclose both mechanisms and their approximate probabilities in advance. (X).

**R2-M9. The estimand depends on the procedure and is conditional on success.**

- **Location:** `methods.tex` "Boundary…", ¶1; D1.
- **Concern:**
  - $\mathcal A(a,r)$ is an expectation over the matching draw with $M=1{,}024$. A cell that needs the retry is evaluated under $M=4{,}096$, which is a different matching distribution and hence a different target.
  - The expectation is also conditional on successful fits. If fit failure depends on the draw, the conditional mean differs from the unconditional one.
  - Acceptance tolerance leaves a bias of up to $0.25\,\mathrm{SE}_{fit}$ in the fitted moments.
- **Classification:** (T) State these dependencies. (E) Report retry use and gap rates per cell next to each AUC, from the fit records. (X).

### Minor concerns

1. **Pooled Pearson features.** Pearson correlations on rank-coded equiprobable categories, pooled over persons, waves and two entry cohorts, are the features. A polychoric or rank-based alternative is not needed for the frozen design, but the text should say that the features ignore ordinal structure. (T)
2. **Wording of $r$.** Call $r$ "signal share of the continuous response channel" everywhere, and reserve "reliability" for the anchor. Currently `abstract`, `introduction.tex` ¶5 and the keywords say "measurement reliability". (T)
3. **Conditioning model.** $r_{it}=\min(0.95,r+\delta\tau/10)$ makes reliability rise linearly with tenure. The cited effect (Kraemer et al. 2025) also contains true stabilization, as v1 admits. The text should say that this sensitivity is not a panel-conditioning model. (T)
4. **Anchor standard errors.** The anchor uses model-based Wald standard errors for a ratio near a boundary. The SHP prereg notes that these are not design-based standard errors. A profile or delta-method interval is preferable, but it is not frozen. State the limitation. (X)
5. **Waste guard.** It is sharp. With one gap in 54 G0 fits the predictive probability is about 0.445, so the study stops before G2 (`inference-docking-v4/REPORT.md` §7). The paper should say that a single numerical failure at the relevant cells ends the confirmatory study under the frozen rules. (T/X)
6. **Missing survey-methods literature.** `related-work.tex` cites Mulder, Dang–Ma and Lucas 2023, but not the trait–state–error identifiability literature (STARTS, TSO, Lüdtke et al. 2018, Hamaker et al. 2015 on RI-CLPM). The positioning dossier admits that survey methodology was not searched ("Limites deste dossiê"). (T)
7. **Tie rate.** Report the tie rate of the panel scores with the AUC (G1c requires it). Rank-coded categories can produce ties in low-$r$ cells. (E)

---

## Pre-results risk register

Frozen locators:

- **v1**: `detection-boundary-preregistration-frozen.md`;
- **AMD**: `detection-boundary-amendment-v4.md`;
- **SPEC**: `amendment-v4-decision-spec.md`;
- **DRD**: `v4-delta-review-decisions.md`;
- **SHP**: `shp-reliability-preregistration.md`.

Standard figures used below:

- **Fig. A:** nine small multiples of AUC against $a$ (categorical axis over $G$), one per $r$. Each shows the point estimate, the simultaneous band and the 0.70 line (and 0.60/0.80 as thin lines), with gap cells and family-limit cells drawn as distinct symbols and the $a=0$ gate marked.
- **Fig. B:** $a^*(r)$ and $a_s^*(r)$ with inverted intervals, right-censoring arrows, "gap at a=…" markers and invalid-unit shading. The SHP anchor is drawn as a vertical band, placed both raw and through the crosswalk if one exists.
- **Table U:** the full 414-unit status inventory, by tier.

| # | Result pattern | What the frozen rules require | What the paper must contain |
| --- | --- | --- | --- |
| 1 | **Gate fails** at any stage (G0 identity or budget, G1b, G1c, G2 dispersion or FD median, G2c), or the waste guard stops before G2 | SPEC D7: "No rerun until pass. Failure means documentation plus a new amendment". DRD "Correction to item 2": stop if P < 0.80 and record it in the second binding record. No confirmatory seed may be derived. | A negative methods paper: the gate table (criteria, counts, pass or fail, not sealed values), the stage at which it failed, the failure accounting, and why no curve exists. Abstract and conclusion rewritten; Results holds `gate-outcomes` only. A successor, if any, is a new protocol and cannot be folded into this paper's confirmatory claim. **Decide now** whether a gate-failure paper is still submitted to JCSS; JASSS or a methods note is more realistic. |
| 2 | **Primary curve invalid**: some B unit's $a=0$ band misses 0.5 (≤ about 4.9% by chance), or the $a=0$ cell is a gap, or a tier-1 unit is incomplete at close | v1 "Inferência viável": B failure at an eligible $r$ "impede aceitar a curva principal como validada". AMD D1: other units' boundaries are "relatadas com a marca de invalidação principal". `_close_inventory` also invalidates on incompleteness. | Fig. B with every $r$ drawn and the invalid ones shaded; a sentence stating that the whole curve is not validated; no headline $a^*$. Table U must show which mechanism caused the invalidation (null gate or clock). Pre-write the chance-failure probability now (R2-M8). |
| 3 | **$a^*(r)$ right-censored at every $r$** on complete valid grids | v1 "Pergunta e estimandos": "Não-atingimento é resultado registrado, não licença para ampliar a grade ou promover um secundário". v1 "Discriminador": non-attainment does not prove indistinguishability. D8: no new primary. | Fig. A and B with censoring arrows; the statement "the fixed LDA did not reach AUC 0.70 up to $a=0.90$ at any $r$". The 0.60 and 0.80 secondary boundaries (E: derived from the released bands; the curve runner computes only 0.70); the upper band at $a=0.90$ per $r$ (how close it came); an explicit sentence that stronger discriminators are unresolved. No grid extension. |
| 4 | **Crossing at the first positive grid point** ($a=0.001$ or $0.003$) at many $r$ | v1 regions: "pequena" if $0<a^*\le0.03$, and 0.03 "é convenção interna". A crossing just after a valid $a=0$ gate is admissible. | Must be pre-framed as suspicious. Report retry use, the projected fraction, the amplification diagnostic and $V_{nuis}$ at those cells. Discuss matching bias (up to $0.25\,\mathrm{SE}_{fit}$, outside the variance) and the "0.0003 residual → AUC 0.57–0.59" sensitivity from SPEC D4. Show the result does not come from the fit: the G2 `mean_shift` after unsealing (E). |
| 5 | **Non-monotone AUC in $a$** (a point crossing followed by a drop below 0.70) | v1: "Relatar não monotonicidade, sem consertá-la por PAVA"; "Sinalizar qualquer diminuição entre limites … consecutivos da banda". The curve report emits `nonmonotone_band`. | Fig. A with the dip visible, and $a^*$ and $a_s^*$ reported separately with both intervals. A mechanistic hypothesis (for example, repulsion-driven tail persistence mimicking trait persistence at large $a$) must be labelled conjecture. Never interpolate. |
| 6 | **First and sustained boundaries disagree** at some $r$, or the sustained boundary is censored by a gap above it | AMD D1 / DRD 1: first boundary declared only before the first gap, sustained only above the last gap with all higher strengths available; otherwise "gap at a=…". The inference docking (§6, C03/C10) confirms that the project censors conservatively. | A table per $r$ with first boundary, interval, sustained boundary, interval and censoring reason. Say which one the abstract reports; pre-commit that it reports both. |
| 7 | **Non-monotone in $r$**, e.g. finite $a^*$ at 0.60 but censored at 0.75 | v1: no "existe algum r significativo" claim; the whole curve is primary; an 81-cell claim needs an extra band. Seeds are independent across $r$ in the tiers. | Fig. B unchanged. Text: "shape across $r$ is descriptive; bands are simultaneous only within $r$". No smoothing over $r$. |
| 8 | **Gaps** (fit failures, family limits, infeasible low-$r$ cells) that censor boundaries | SPEC D4: gaps "never converted into AUC below target … never a certificate of impossibility". v1: infeasible cells are gaps. Brief item 5: family-limit cells carry zero evaluations. | Fig. A must distinguish infeasible (bound-screen) cells, solver failures and dependency gaps. Table of statuses by cell (E: fit records). If low $r$ is mostly infeasible, state the eligible domain explicitly. |
| 9 | **Wide bands**: the $a^*$ interval spans more than one grid step at most $r$ | v1 precision target: at most one grid step, stated as "não é poder empírico nem promessa". No N or grid increase allowed after results. | Report the interval widths and the achieved precision against the v1 target; call $a^*$ resolved only where the interval is one step. |
| 10 | **B crosses, D (or E or C) does not** on complete valid grids | v1 "Discriminador": "compatível com persistência não gaussiana, sem evidência específica de interação". If D's band spans the target: inconclusive. SPEC D9: tier 2 is needed for cross-mechanism claims. | This is the most likely substantive branch given R1-M1. The headline must use the frozen wording. Fig. B needs one panel per null family on shared axes. If tier 2 is incomplete, Table U states it and no cross-mechanism sentence is written. |
| 11 | **Observed-channel separation exceeds the latent or `ordinal_one` control** | v1 "Discriminador": read as sensitivity to transformation and rematched generators, "não como informação criada pelo ruído"; "Separação somente no observado será rotulada dependente do canal". | Label it "channel-dependent" and explain it with the rematched nuisance. Tier 3 may be partial at the close, in which case say so. |
| 12 | **Sensitivities reverse conclusions** ($c$, $\delta$, $b=0$, $\omega$, 24 steps), or are absent at the close | D9: fixed tier order; nothing reordered by AUC. D8: sensitivities are not promoted. | A supplementary table by scenario with status. Any reversal is reported without re-weighting the primary result. Pre-state that the 24-step scenario changes the annual persistence (R1-M4). |
| 13 | **SHP anchor falls outside the grid** ($\hat r_{2004}<0.50$ or $>0.90$), or its interval does | SHP "Relação com a curva v4": "mostrar fora dela sem extrapolar a*(r)"; the grid and rules are unchanged. | Fig. B with the anchor drawn beyond the axis limit and an explicit sentence that the curve is uninformative at the SHP's estimated reliability. **Plausible in advance:** single-item political-trust reliabilities and a trait-biased simplex estimator (R2-M4) both push low. Prepare the text now. |
| 14 | **SHP anchor fails diagnostics**: inadmissible triplets, non-convergence, a wide Heise envelope, or complete-case and FIML disagreeing | SHP: failures "nunca truncadas"; "não publicar um ponto empírico único até revisão vinculada". The Heise envelope is not a confidence interval. | Report the failure, not a point. Draw the envelope, if any, as a specification range. The crosswalk (S) cannot rescue a failed anchor. |
| 15 | **Anchor interval spans $r$ values with different boundary statuses** | SHP: no rounding to a grid cell; no selection of $r$. | Show the range of $a^*$ statuses over the anchor interval; no single "SHP boundary". |
| 16 | **Diagnostics flag**: the empirical max-$t$ often exceeds 2.7729; G2 covariance-Jacobian corrections exceed $0.1\sqrt{V_{nuis}}$; FD medians near the edge of [0.8, 1.25] | D6: report the frequency of exceedance. R3/AMD: flags do not change the criteria. | A supplementary diagnostic table. Methods states that the flags do not alter the pass criteria. |
| 17 | **The $r=0.70$ result stands apart** from its neighbours | D8: $r=0.70$ is calibration-exposed; provenance by $r$; the other eight are not promoted. | Mark $r=0.70$ in every figure as exposure-affected. The text must not interpret it alone. |

---

## Ten changes most likely to move the paper from reject to major revision

Ranked by expected effect on referee decisions. Effort is in author-days of focused work, excluding wall-clock compute. "Frozen?" says whether the change touches the frozen v4 design: none may, and all analyses marked (S) are labelled successor or exploratory.

| Rank | Change | Class | Effort | Frozen? |
| --- | --- | --- | --- | --- |
| 1 | **Reframe what is identified.** Add the mean-field argument (R1-M1) and the v1 linear-control non-attainment. Describe the generator honestly (R1-M2). Retitle around "nominal nonlinear drift versus matched persistence at known response reliability". Make "B and D side by side" the pre-committed headline. | T | 2–3 | No |
| 2 | **State the oracle assumptions and translate the target** (R2-M1, M2, M3). Known $r$, a population-moment matching target, and the AUC → δ → single-panel power table for 0.60/0.70/0.80. Re-express the released AUCs the same way, labelled descriptive. | T + E | 2 | No |
| 3 | **SHP crosswalk** (R2-M4). Run the frozen anchor estimators on synthetic panels across $(a,r)$ with fresh seeds, then draw the anchor both raw and through the map. Pair it with a dated SHP-prereg successor adding a STARTS/trait sensitivity, registered before the anchor value is opened. | S | 4–6 (plus modest compute; no LDA) | No (new, separate records) |
| 4 | **Mean-field twin null** (R1-M1, R1-M5). Replace the network drift by its own-state conditional mean plus matched noise, then compute the AUC against the interaction arm at the tier-1 cells. This tells readers whether the network matters at all. | S | 5–8 (plus tier-1-scale compute) | No |
| 5 | **Make $a$ interpretable** (R1-M3). The partial-$R^2$ map of drift by $a$, $b$ and steps that v1 promised. Delete the supplement sentence claiming it exists until it does. | S + T | 2–3 | No |
| 6 | **Pre-write every branch of the risk register.** Produce Fig. A, Fig. B and Table U from synthetic fixtures. `v4_report_*` modules exist on this branch; check them against the risk-register branches. Include both boundaries, all censoring reasons, the invalidation mechanisms and the frozen region labels. | T | 3 | No |
| 7 | **Factual-consistency sweep** (all items under "Factual inconsistencies"). Fix the supplement's 0.95 and "draft" statements, the "in progress" docking statement, the shard statement, the model names and the stale ledger rows. Complete the exposure list with the docking Part C AUCs. | T | 1 | No |
| 8 | **Inference disclosure** (R2-M6, M7, M8, M9). Describe the implemented studentization and its sensitivity, G1b's zero-nuisance scope, the achieved 95.17% ± 0.39 pp, bias outside the variance, chance and clock invalidation, and whole-curve shape statements as descriptive. | T (+E diagnostics) | 1–2 | No |
| 9 | **Cut and re-aim the literature** (R1 minor 1–2; R2 minor 6). Remove the voter/Sznajd/$q$-voter and macro-outcome material and the systematic-map supplement. Add the trait–state–error identifiability literature and position against Moor-Smith–Carpentras, Mulder, Dang–Ma and Ureña-Carrion as the dossier advises. | T | 3–4 | No |
| 10 | **Reproducibility and accountability.** Release the frozen tree `37513841` as the confirmatory code, separate from the report code. Disclose that bitwise reproduction is macOS-arm64 only, the three Linux test failures and the failed host equivalence. Record human scientific ratification of v1/v4 and of the agent-frozen decisions before submission, or state plainly that it is absent (`main.tex` title comment; spec header "pending Davi's ratification"). | T + X | 2 | No |

Not in the top ten, but cheap: report the 0.60/0.80 secondary boundaries from the released bands (E, under 1 day), and qualify "no exposure observed" for SHP co-residents (T, minutes).

---

## Factual inconsistencies (manuscript, frozen documents, code)

| # | Inconsistency | Exact locators | Fix |
| --- | --- | --- | --- |
| F1 | **Wrong stop-rule threshold in the supplement.** The supplement says "a projected pass probability below 0.95 stops before G2". The frozen rule is 0.80. Commit `b04d80f3` corrected `methods.tex` and `README.md` but not the supplement. | `sections/supplement.tex`, "Gate accounting and execution", ¶3. The rule is in `detection-boundary-amendment-v4.md` lines 321 and 423–425, `v4-delta-review-decisions.md` "Correction to item 2", `methods.tex` "Boundary…", ¶5, and `appendix-odd.tex` ODD35. | T |
| F2 | **The supplement says the amendment is still a draft.** It reads "the current amendment remains a draft awaiting freeze and gates". It was frozen at `37513841`. | `sections/supplement.tex`, "Protocol provenance and exposure", end of ¶1. Compare `methods.tex` "Protocol history" ¶1 and `freeze-v4.json` `"status": "frozen"`. | T |
| F3 | **Docking described as in progress.** Two clean-room docking studies were completed on 27 September. | `sections/verification.tex`, "Independent docking" (VER05); `claim-evidence.md` VER05. Compare `validation/docking-v4/REPORT.md` and `validation/inference-docking-v4/REPORT.md`, and the brief's "Estudos de verificação concluídos". | T |
| F4 | **Claimed diagnostic does not exist.** The supplement asserts that a partial-$R^2$ drift diagnostic is reported. The frozen v4 code computes none. | `sections/supplement.tex`, "Panel channels and null mechanics", ¶1, sentence 3. Promised in v1 "Mecanismos e significado de a", last ¶. Absent from `simulation/detection_v4.py`, `models/detection_panel_v4.py`, `simulation/v4_curve.py`, `v4_gate.py` and `v4_plan.py`. | T now; S to produce it |
| F5 | **Shards on other hosts.** The manuscript allows "numerically equivalent same-code-hash shards". The Owner dropped multi-host execution, the shard count is bound to eight local workers, and host equivalence failed. The frozen amendment still mentions other hosts, so the frozen documents are inconsistent with each other. | `methods.tex` "Inventory and execution status", ¶1; `v4-delta-review-decisions.md` item 4; `validation/host-equivalence-homelab/REPORT.md` "Equivalência geral: falhou"; `detection-boundary-amendment-v4.md` lines 261 and 522–524; `freeze-v4.json` `"shards": 8`. | T (explain that the delta decision prevails) |
| F6 | **Model identities inconsistent** within the same manuscript. Methods names "GPT-6 through Codex". The map section names `gpt-5.6-luna`, `gpt-5.6-sol`, "GPT Astra", `claude-fable-5-1` and `claude-opus-5-5`. | `methods.tex` "Use of generative AI"; `systematic-map.tex` "Prioritization and screening" and "Calibration and reference judgments". | T (list the exact model identifiers per role) |
| F7 | **Ledger cites a sentence that no longer exists.** R21 cites the Methods sentence "Population AUC from this LDA is bounded above by Bayes-optimal AUC". That sentence is not in `methods.tex`; the claim appears only in ODD08 and `related-work.tex`. | `claim-evidence.md` R21; `sections/methods.tex` (absent); `appendix-odd.tex` line 83; `related-work.tex` ¶5. | T |
| F8 | **Documents that describe v4 as unfrozen.** The v4 README opens with "Não contém congelamento v4" but later says "Há um freeze v4". The hash-bound amendment itself says "Sem congelamento v4" (lines 3–4). Its bytes cannot change, so the paper must explain that the bound amendment predates its own freeze record. | `experiments/exploratory/detection-boundary-v4/README.md` ¶1 and "Verificação histórica" last ¶; `detection-boundary-amendment-v4.md` lines 3–4; `freeze-v4.json`. | T (README successor note; a manuscript footnote) |
| F9 | **Exposure disclosure incomplete.** The docking studies computed AUCs under the v4 law at $a>0$ after the freeze: 0.6771 at $(a,r)=(0.30,0.70)$ and 0.5072 at $(0.03,0.50)$. These used $N=1{,}002$ and reduced training sizes, so they are not estimates of the estimand. They are also at the exposed $r=0.70$, and D8 requires cumulative disclosure. A timing probe printed L1–L5 means before the docking pre-declaration. | `methods.tex` "Protocol history" ¶2; `supplement.tex` "Protocol provenance and exposure". Source: `validation/docking-v4/REPORT.md` §1 item 2 and §3 "Parte C". Rule: SPEC D8; AMD lines 39–48. | T |
| F10 | **Platform dependence not disclosed.** Verification implies that the frozen test battery passes. On Linux x86-64, three tests fail on a clean `37513841` tree: `test_zero_share_panel_keeps_frozen_calibration_bytes` (two cases) and `test_v42_solver.py::test_inner_updates_slope_when_trait_weight_attenuates_phi_derivative`. Bitwise identity holds on macOS arm64 only. | `sections/verification.tex` "Test suite"; `validation/docking-v4/REPORT.md` §4 "Achado de ambiente"; brief "Reprodutibilidade entre plataformas". | T/X |
| F11 | **Preflight cannot pass on this branch.** The ledger says only `pyproject.toml` and `uv.lock` differ from the freeze. On `integration/ic-20260928` (`8d286190`), nine further `.py` files that are not in the freeze closure would enter `source_hashes()`: `analysis/detection_v4_report.py`, `analysis/shp_reliability.py`, `analysis/v4_report_{figures,schema,synthetic,tables}.py`, `tests/integration/test_reproducibility_example.py`, `tests/unit/test_detection_v4_report.py` and `tests/unit/test_shp_reliability.py`. | `claim-evidence.md` ODD38; `src/ic_study/simulation/v4_gate.py:42-52`; `freeze-v4.json` `code` (82 entries). | T (Code availability must name the frozen tree) |
| F12 | **Stop point of the waste guard.** Methods says a low probability "stops before the remaining gates". The frozen rule stops before G2; G1b and G1c are not conditioned on the second record. | `methods.tex` "Boundary…", ¶5; `detection-boundary-amendment-v4.md` line 321; `README.md` (v4) "Execução futura". | T |
| F13 | **Calibration target stated as met.** Methods states the 0.95 target as if achieved. The verified joint pass probability is 95.17% with an MCSE of 0.39 pp, and the amendment says this "não constitui prova" that the true value exceeds 0.95. | `methods.tex` "Boundary…", ¶5; `detection-boundary-amendment-v4.md` lines 403–412. | T |
| F14 | **v1 gate language in the introduction.** The introduction says "A zero-strength coverage gate must pass before confirmatory execution". v4 has a six-stage gate that includes dispersion at $a>0$. | `introduction.tex` ¶7; compare `methods.tex` "Boundary…", ¶5. | T |
| F15 | **Ledger paths that do not resolve.** Some ledger rows point to `coord-20260925/review-v4/decisions.md` and `ic-boundary-v4/…` and `ic-study-version/…` paths that are not in this repository. The controlling files are `v4-review-decisions.md` and `v4-delta-review-decisions.md`. | `claim-evidence.md`, "Successor v4 manuscript claims", intro ¶ and V21. | T |
| F16 | **Strict or inclusive crossing?** The v1 protocol requires a strict lower band above 0.70 for a "crossing" claim, while the frozen code inverts inclusively. Methods states both without saying which governs the reported $a^*$. | `methods.tex` "Boundary…", ¶4; v1 "Inferência viável e validade" ("Uma regra unilateral…"); `claim-evidence.md` "Eligibility, estimands and inference" row. | T |
| F17 | **Tier-1 incompleteness not mentioned.** The code invalidates the main curve if any tier-1 unit is not complete-valid at close, including units never started. Methods mentions only null-gate failure. | `methods.tex` "Boundary…", ¶4 and "Inventory…"; `simulation/v4_curve.py:_close_inventory`; brief item 8. | T |
| F18 | **G2 substitution wording differs across frozen documents.** D7 says "excluding r values already in G2". The amendment and ODD35 say "without duplicating the same cell". The code follows the latter. | `amendment-v4-decision-spec.md` D7 "Cells"; `detection-boundary-amendment-v4.md` lines 354–356; `appendix-odd.tex` ODD35; `simulation/v4_plan.py:substitute_cells`. | T (state that the later decisions prevail) |
| F19 | **Scope of the supplement.** It includes the broad systematic map (with red `[TBD]` cells), which the README describes as a separate deliverable and which this paper's claims do not use. | `sections/supplement.tex` lines 1–4; `README.md` status ¶. | T |

**Checked and consistent** (no action):

- the v1 SHA-256 and the v4 freeze-record SHA-256 in Methods;
- the panel geometry (7,084/3,542, retention 0.89);
- the $G$ and $R$ grids;
- the matching tolerance, the 2,048/4,096-pair validation and retry, and the 96-evaluation budget;
- the G1b, G1c, G2 and G2c constants in ODD34/35 against the amendment and `criteria-v43.json` thresholds;
- the tier list and the 3,726-cell/414-unit inventory;
- the exposure numbers from D8 (0.943912, 0.530, 0.756070, 0.7317–0.7897, 0.589413);
- the 14/40 failed v1 refits against `detection-boundary-coverage-check.md`.
