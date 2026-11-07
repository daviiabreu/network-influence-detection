# Exploratory experiments

Hypothesis generation, implementation probing, parameter discovery, and failed
attempts. Results from this directory cannot silently be relabeled as
confirmatory evidence.

## Executed pilots

- [Fragmentation stopping pilot](fragmentation-pilot-v1/README.md), 2026-09-12:
  112 primary trajectories plus cost, control and tolerance checks; one cached
  partition discrepancy, with four primary trajectories right-censored. The
  report keeps execution evidence separate from question selection.
- [Probabilistic histogram forecast pilot](probabilistic-forecast-pilot-v1/README.md),
  2026-09-12: 960 independent primary/confirmation trajectories, 480 repeated
  at higher ensemble precision and 32 cost checks. No dynamic cell met the
  predeclared continuation criterion; short training also exposed incorrect
  mechanism selection in the no-update control.
- [Mechanism antecedents and cheap controls](antecedent-reproduction-mechanisms/README.md),
  2026-09-24: bounded reproductions and small controls for two unselected
  mechanism candidates, with corrected successors and limited fidelity.

- [SHP anchor crosswalk](shp-anchor-crosswalk-v1/README.md), 2026-09-28:
  the frozen anchor estimators applied to 990 synthetic panels of known signal
  share from the frozen v4 generator (SHP successor 1, Addition 2); the
  quasi-simplex reads about 0.02-0.04 below the simulation r. Exploratory only.
- [v4 exploratory successors X1a and X2](detection-boundary-v4-exploratory/REPORT.md),
  2026-09-28, declared and run before any v4 confirmatory result: the
  interaction arm against its mean-field twin in 72 cells (network information
  separable for the fixed discriminant in 51, all with a ≥ 0.01) and the drift
  R² map in 36 conditions. Exploratory only; the frozen v4 protocol is
  unchanged.

## Declared, not yet executed

- [v4 exploratory X1b](detection-boundary-v4-exploratory/README.md), declared
  2026-09-28: the mean-field twin's own boundary against the null family, run
  only if a successor pipeline first reproduces the frozen pipeline bit for bit
  in at least two cells.
