Online Resource 2: all simulation units

One row per unit (one comparison at one signal share) of the frozen inventory,
including controls and sensitivities.
This English copy preserves the original rows, columns, order and numeric strings.
The archived original CSV keeps the released Portuguese status labels.

Columns (in file order):
tier: inventory group (1 main B, 2 other models,
  3 measurement controls and mobility variants,
  4 response-channel sensitivities, 5 mechanism sensitivities, 6 24-step sensitivity).
family: persistence model (A autoregressive, B trait plus autoregressive,
  C autoregressive with an altered response channel, D state-dependent, E mover-stayer).
channel: observed, latent (error-free), ordinal_one (signal share one), or latent_rank.
  latent_rank: wave-wise mid-ranks of the error-free latent values.
sensitivity: scenario identifier; see the scenario legend below.
r: signal share in the continuous response before discretization.
exposure: the stored flag "calibration-exposed" marks r = 0.70, examined during
  calibration; otherwise blank.
main_curve_flag: main curve invalid when any main B unit is not complete and valid.
status: unit completion and validity at the operational close. Complete means all
  nine strength cells ran, including cells recorded as gaps; complete and valid
  additionally requires a fitted zero-strength cell whose band contains 0.5.
  Otherwise a complete unit is complete but invalid and its boundaries are suppressed.
null_gate: a unit passes only when its zero-strength cell is fitted and its AUC
  band covers 0.5.
gaps: total unavailable cells on the strength grid.
gaps_screened: family limits from the feasibility pre-check, without solver evaluations.
gaps_family_limit: family limits encountered while fitting the profile.
gaps_solver: other solver statuses preventing an accepted fit.
gaps_validation: accepted fits that failed validation.
gaps_dependency: controls whose observed-channel fit failed.
gaps_propagation: failed uncertainty propagation.
a_star: first grid strength whose point AUC reaches the primary target 0.70,
  reported only strictly below the first gap.
a_star_lower, a_star_upper: lower/upper ends of its inverted-band interval.
a_s_star: first grid strength from which the point AUC stays at or above 0.70
  at every higher strength, reported only strictly above the last gap.
a_s_star_lower, a_s_star_upper: lower/upper ends of its inverted-band interval.
region: small when the entire first-boundary interval lies within (0, 0.03];
  large when the entire interval lies above 0.03; indeterminate when the interval
  crosses 0.03, has a censored end or the boundary is zero; not attained when a
  full gap-free grid never reaches the target; censored (gap) when a fit gap prevents
  declaring the first boundary; NA for invalid or unfinished units.
derived_a_star_060: first boundary at secondary AUC target 0.60.
derived_a_star_060_lower, derived_a_star_060_upper: its interval ends.
derived_a_star_080: first boundary at secondary AUC target 0.80.
derived_a_star_080_lower, derived_a_star_080_upper: its interval ends.
nonmonotone_band: whether either band endpoint decreases along the available grid.
critical: maximum of the empirical max-t critical value and the 2.7729 floor.
max_t_above_floor: whether the empirical critical value exceeds that floor.

Scenario legend:
main: main specification.
mobility: mobility summaries in place of the lag features.
c025: Persistent response style (c = 0.25).
c050: Persistent response style (c = 0.50).
d010: Panel conditioning (delta = 0.10).
d020: Panel conditioning (delta = 0.20).
c050-d020-exploratory: Response style and conditioning (c=0.50, delta=0.20).
b000: Attraction only (b = 0).
omega025: Anchoring (omega = 0.25).
omega050: Anchoring (omega = 0.50).
omega075: Anchoring (omega = 0.75).
omega100: Complete anchoring (omega = 1).
steps24: 24 update steps per wave.

Mobility summaries measure mean absolute one-wave change within each tercile of
the starting wave's mid-rank position. The combined response-style and conditioning
scenario is exploratory.

Boundary intervals invert bands simultaneous over the strengths of one share,
without interpolation or smoothing. The first interval runs from the first
strength whose upper band reaches 0.70 to the first whose lower band does;
the sustained interval applies the same rule to all higher strengths.
First-boundary interval ends are reported only strictly below the first gap;
sustained-boundary interval ends only strictly above the last gap.
"not reached (>0.9)" and ">0.9" denote right censoring on the complete eligible
grid; for a point boundary this is not attained, while an interval end is censored.
"censored at gap a=x" identifies a fit gap, never evidence of not attaining the target.
"suppressed" means the null gate failed. "NA" means unavailable or inapplicable.

Status translation:
completo válido -> complete and valid
completo inválido -> complete but invalid
parcial por encerramento operacional -> partial at the operational close
não iniciado -> not started
