# Draft captions: a*(r) detection-boundary paper (v4)

Draft English captions for the figures and tables rendered by
`python -m ic_study.analysis.detection_v4_report`. Rule names refer to the frozen
preregistration (`detection-boundary-preregistration-frozen.md`, "PR"), the v4
decision spec (`amendment-v4-decision-spec.md`, D1–D11), its v4.1 revision (R1–R8),
the SHP reliability preregistration ("SHP-PR") and its successor 1 ("SHP-S1"). Anything
in square brackets must be filled in from the released run.

## Figure 1: `F1_a_star_by_family`

**Detection boundary a\*(r) for the confirmatory null family B and the secondary
families A, C, D and E.** Each panel shows one null family on the main observed
grid (tier 1 for B, tier 2 for A, C, D and E; D9). The horizontal axis is continuous
response signal share r; the vertical axis is nominal partner-drift strength a on
ordinal grid positions. Equal spacing does not imply equal increments of a. Family
names identify the declared persistence laws; the repeated B markers are descriptive
references without between-family inference. R = {0.50, …, 0.90} and
G = {0, 0.001, …, 0.90} are frozen, and nothing is interpolated (PR, estimands). Filled circles give the first
boundary a\*(r) = min{a ∈ G : AUC(a, r) ≥ 0.70}. Vertical bars give its interval,
obtained by inclusive inversion of the per-r band (PR, inference; D6). For B, open
circles give the sustained boundary a\*ₛ(r), with its interval inverted the same way.
The per-r bands are simultaneous over the nine strengths of one r only, not over the
81 cells, so no statement is made jointly across r (PR). The special markers are:

- Triangles in the top row "> 0.9": the target was not reached on the complete
  eligible grid, or an interval end lies beyond it. These are right-censored and kept
  as such (PR: "preservar None como censura à direita"). Every strength above the last
  gap is available, so when the lower end of a sustained interval lies above the last
  gap, a missing upper end means that the lower band never stays above 0.70 up to
  a = 0.90: the bar runs up to this row, never down to the gap.
- Open squares: the boundary was censored at a gap. They sit at the gap strength,
  because the rule forbids declaring a boundary across an infeasible cell (PR).
- The "status" strip: units without a valid curve. Crosses mark `complete invalid`:
  the a = 0 band excludes 0.5, so the null gate fails and the boundaries are
  suppressed (PR, null gate). Open diamonds mark `partial at operational close`.
  Grey dots mark `not started` (D9).

Grey circles in panels A, C, D and E repeat B's a\* for reference; they carry no
contrast inference. The dashed line at a = 0.03 separates the registered "small"
(0 < a\* ≤ 0.03) and "large" (0.03 < a\* ≤ 0.90) operational regions (PR); Table 1
gives each unit's region. The shaded column and the dagger mark r = 0.70, which is
calibration-exposed (D8). When some tier-1 unit is not `complete valid`, the main
curve is invalid: panel B then carries the mark "main curve invalid", and its
boundaries stay drawn and reported with that mark (amendment v4). Every unit of
the main grid is shown; Figure 5 discloses the full frozen inventory.

## Figure 2: `F2_auc_profiles_<family>` (one figure per family; B in the main text)

**Released panel-level AUC profiles of the fixed discriminator behind a\*(r),
family [B].** There is one panel per response signal share r in R; no r is selected
(PR: "não escolher r"). Circles give the point AUC at each
successfully fitted strength. Bars give the per-r 95% band: the critical value is
max(empirical max-t, 2.7729), with logit studentisation and an SE floor of 1/(2n)
(D6). The dashed line is the 0.70 target and the dotted line the 0.5 null value. The
solid vertical line marks the estimated a\*. The shaded span is its interval by
inclusive band inversion, with right-censored ends running to the grid edge (PR).
Strength positions are ordinal. The band is simultaneous over strengths at one r
only, with no joint coverage across r, families or channels.
Crosses at the bottom mark gap cells: cells without an accepted, validated fit. A gap
is a family limit (screened by the feasibility pre-check before any solver evaluation,
or reached along the profile), a solver or validation failure, a dependency gap of a
control whose observed fit failed, or a propagation gap (ill-conditioned nuisance
propagation, amendment v4.4). Family limits are gaps, not failures (D7); Table 1
counts gaps; T1s gives each kind. The curve is not interpolated across gaps. Panels
for `complete invalid` units draw the profile in grey and suppress the boundaries
(PR, null gate).
Panels for units without a released curve name their D9 status. Non-monotone bands are
not repaired (no PAVA; PR); they are flagged in T1s. When the main curve is invalid,
the figure for B carries the "main curve invalid" mark at the top (amendment v4).

## Figure 3: `F3_exploratory_family_offsets_vs_B` (EXPLORATORY)

**Exploratory, descriptive: position of each secondary family's a\* relative to B, in
grid steps.** For every r at which both units are `complete valid` and both reach
the target, the point is the difference between the grid indices of a\*_X(r) and
a\*_B(r). The protocol registers no between-family contrast (D9: tier 1 alone
supports only the comparison against B, and claims across families require complete
valid tier-2 grids), so this quantity has no interval, test or registered
interpretation. Censored, invalid and unfinished units are omitted; Figure 1 shows
them. r = 0.70 is calibration-exposed (D8).

## Figure 4: `F4_gate_diagnostics`

**Validation-gate diagnostics from the sealed gate records (D7; only criteria values,
counts, ratios and pass/fail).**
- (a) G0: final status of every fit on the blind matching mask, covering B, A, C, D
  and E plus the three B controls, with colours keyed on the final attempt. Green
  statuses are accepted. Yellow marks family limits screened by the feasibility
  pre-check with zero solver evaluations, and orange family limits reached along the
  profile; both are gaps, not failures (D7). Vermillion marks solver failures
  (no-L1-root, non-monotone-profile, numerical-limit, ill-conditioned, budget). Reddish
  purple marks an accepted status that failed validation in both attempts. Blue marks
  dependency gaps: B controls whose observed fit failed, so no control fit ran. Pass
  requires every a = 0 identity fit to be anchor-exact, no budget statuses, and
  implementation-type statuses (numerical-limit, ill-conditioned) in at most 1% of
  fits.
- (b) G0: solver evaluations per attempt against the budget of 96, the frozen solver
  default, as reported under R2.
- (c) G1b: joint band coverage in each synthetic-score scenario (1,000 repetitions
  each) against the nominal 0.95. The pass criterion is ≥ 935/1,000 per scenario.
- (d) G1b: band critical value per repetition against the 2.7729 floor. The share of
  repetitions above the floor is the frequency that D6 requires to be reported.
- (e) G2: per-cell and pooled procedure-dispersion ratios, with bootstrap intervals,
  for cells in allocation order, labelled with their (a, r) from the second binding
  record when it is given. The shaded region and the pooled bar show the calibrated
  thresholds in `criteria-v43.json`. A cell passes when its interval overlaps the
  region. When a cell keeps fewer than two intact pairs, the frozen criteria return no
  ratio; the panel then says "not estimable" and gives the successful pairs per cell.
- (f) G2c: Var_D5/Var_refit at a = 0.10 (100 refits) and a = 0.03 (40 refits), with
  one-sided 95% bootstrap bounds. Dashed lines give the cut-offs 0.8 (upper bound) and
  2.0 (lower bound). A failed baseline leaves no comparison, and the panel names it.
- (g) Stages: tasks completed out of those planned, and the verdict. A stage passes or
  fails only once every planned task is aggregated; before that it is "in progress".
  Each stage uses the line of `criteria.jsonl` with the most completed tasks, because
  the frozen runner appends one line per shard and the mid-run lines carry pass =
  false. A stage whose complete summary the frozen runner could not append is read
  from its documented successor record and labelled "successor record, frozen
  aggregate". A stage with sealed task records and no aggregate line yet is counted
  from those records and marked "no aggregate line yet". The economy rule that stops
  execution before G2 has its own row, "pre-G2 stop", and is not a stage verdict.

G2 is not a demonstration of absolute interior coverage (D7). Panels whose stage is
absent, in progress or failed without criteria in the sealed records say so.

## Figure 5: `F5_inventory_status`

**Status of every unit of the frozen inventory at the close of the compute window
(2026-10-19T02:59:00Z; D9).** Rows are the frozen configurations: tier, null family,
control channel and sensitivity. Columns are the r grid. Colours give the four
registered statuses `not started`, `partial at operational close`,
`complete invalid` and `complete valid`, with counts in the legend. The full
inventory and every absence are disclosed. Tier order was fixed and never changed by
results (D9).

## Figure 6: `F6_a_star_shp_anchor` (EXPLORATORY ILLUSTRATION)

**Exploratory positioning of distinct quantities, without an empirically calibrated
equivalence to r or an item-specific boundary.** Figure 1's boundaries are shown
with the SHP quasi-simplex anchor for [2004] (dashed blue line; SHP-PR). The
quasi-simplex anchor and r are distinct quantities; this placement is uncalibrated.
The blue shading is its model-based Wald 95% interval. The hatched region is the
min–max envelope of the nine Heise triplet estimates: a specification envelope,
not a confidence interval (SHP-PR). The anchor is placed without choosing or
rounding to a value of r and without interpolating or extrapolating a\*(r). It
chooses no grid, strength, target or rule and does not validate the social mechanism
(SHP-PR). As in Figure 1, panel B carries the "main curve invalid" mark when the
main curve is invalid.

The dotted vermillion line and the diamond with bars in the top row give the
trait–state–error (STARTS) reliability for [2004] with its Wald 95% interval, a
sensitivity to a stable trait that the quasi-simplex lacks (SHP-S1, Addition 1). It is a
diagnostic of the anchor's dependence on the trait, not a model choice. When STARTS
meets a declared failure rule, nothing is drawn and the legend states the failure. When
given, the "crosswalk" row marks the grid r values whose range over [10] synthetic
panels of the quasi-simplex r at 2004 contains the SHP value, for the interaction arm at
a = 0 (circles) and null family B with φ = 0.85 and trait weight η = 0.25 (triangles)
or 0.50 (squares) (SHP-S1, Addition 2). The panels come from the frozen v4 generator
with the SHP geometry. This synthetic crosswalk is exploratory: it neither replaces the
raw placement nor chooses r nor alters the curve. Its descriptive ranges do not
propagate the uncertainty of the empirical anchor. All other elements are as in
Figure 1. Source: Swiss Household Panel (SHP).

## Table 1: `T1_a_star_grid` (main) and `T1s_a_star_all_units` (supplement)

**First and sustained boundaries on the main grid at the primary AUC target 0.70.**
T1 displays status, null gate, gap count, first and sustained boundaries with
intervals, and region at the primary AUC target 0.70. Tier 1 contains B
(confirmatory); tier 2 contains A, C, D and E. B and D retain every r, and any paired
reading uses the authorized common gap-free denominator. The main-text columns are:

- D9 status at the operational close and the per-run a = 0 null gate;
- the total gap count;
- a\* and a\*ₛ with their inclusive band-inversion intervals in brackets:
  ">0.9" means not reached on the complete eligible grid, "gap x" means censored at
  the gap at a = x, and "suppressed" means a failed null gate. A missing upper end
  of a sustained interval whose lower end lies above the last gap is ">0.9", not
  gap-censored;
- the registered region of a\*: "small" (0 < a\* ≤ 0.03), "large"
  (0.03 < a\* ≤ 0.90), "not attained", "censored (gap)" or "indeterminate".
  Indeterminate applies when a\* = 0 or the interval crosses 0.03 or has a censored
  end; it does not change the estimand (PR).

The dagger marks calibration-exposed r = 0.70 (D8). The double dagger marks
"main curve invalid" on every B row when any tier-1 unit is not complete valid;
B boundaries stay reported with that mark (amendment v4). Status labels
valid, invalid, partial and not started retain their inventory definitions. Bands
are simultaneous over G at one r only, not jointly across the 81 cells.

**T1s: full inventory records (supplement/online resource).** Full inventory, gap
types and diagnostics remain in T1s, including absent and invalid units, controls,
sensitivities, both boundary records, the non-monotone-band flag, the per-r critical
value and whether empirical max-t exceeded 2.7729. Gap types distinguish screened
family limits, profile family limits, solver failures, failed validation, dependency
gaps and propagation gaps (ill-conditioned nuisance propagation, amendment v4.4);
family limits are gaps, not failures (D7). The report CSVs retain the complete schema
and all values.

**Supplementary secondary-target table.** Derived targets 0.60 and 0.80 appear only
in this supplementary display, never in T1, Results or the headline. It contains B
boundaries at every r with a curve, with intervals derived from released bands by
the same frozen inclusive inversion and gap-censoring rules. Invalid units remain
suppressed and whole-curve invalidation remains marked. The frozen release emits
only the 0.70 boundaries; these targets do not replace that primary target.

## Table 2: not emitted

The frozen protocol defines no between-family contrast statistic, so there is no
registered Table 2; see `README.md`.

## Table 3: `T3_gate_summary`

**Gate summary (D7; v4.1).** For each stage G0, G1b, G1c, G2 and G2c, the table lists
the completed and planned tasks, the task failures, the criterion values, the
registered criterion and the stage verdict. Each stage uses the line of the sealed
`criteria.jsonl` with the most completed tasks, because the frozen runner appends one
line per shard and the mid-run lines carry pass = false. The verdict is "in progress"
while fewer tasks are complete than planned. A complete stage without criteria names
its failure reason: a failed task in G0, G1b or G1c (task failures must be 0) or a
failed G2c baseline. A stage whose complete summary the frozen runner could not append
comes from its documented successor record, labelled "successor record, frozen
aggregate", whose SHA-256 is in the manifest. The G2 rows name each cell's (a, r) from
the second binding record, and a cell with fewer than two intact pairs is "not
estimable", with the successful pairs per cell. The economy rule that stops execution
before G2 is a separate row, not a G0 verdict.

## Table 4: `T4_inventory`

**Inventory at the close (D9).** Unit counts by D9 status for each frozen
configuration, each tier and in total, the gap cells of the released curves by kind as
in T1s, and whether the main curve (every tier-1 B unit `complete valid`) is valid
(PR: a failure of B at any eligible r prevents accepting the main curve as validated).
