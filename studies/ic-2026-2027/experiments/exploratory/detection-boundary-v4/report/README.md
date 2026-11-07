# v4 a*(r) figures and tables

Reporting pipeline for the detection-boundary v4 paper (JCSS; JASSS as backup). It
reads only the released outputs. It never runs a gate stage or a confirmatory tier,
and it never writes into a sealed store.

## Render

```sh
cd studies/ic-2026-2027
uv run --frozen python -m ic_study.analysis.detection_v4_report \
    [--curves RELEASED.json] \
    --gate-root ~/.local/state/research-workbench/sealed-v4-gate/<id> \
    [--shp SHP_AGGREGATE.json] [--crosswalk CROSSWALK.json] \
    [--criteria experiments/exploratory/detection-boundary-v4/criteria-v43.json] \
    [--allocation v4-allocation.json] \
    [--stage-successor G1c-aggregate-successor.json] \
    --out OUTDIR
```

| Input | Source (frozen emitter) |
| --- | --- |
| `--curves` | stdout of `run_curve.py --release-at-close`, which is `released_curves(root)` from `simulation/v4_curve.py`. Without it (no release exists because the gate failed, stopped or did not finish), only T3 and F4 are written |
| `--gate-root` | sealed gate root: `criteria.jsonl` (the `aggregate` summaries appended by `run_gate.py`) plus the per-task `result.json` files sealed by `execute_task` (`simulation/v4_gate.py`) |
| `--shp` | `analyze_panel` report from `analysis/shp_reliability.py` (optional; F6 is skipped without it). Reports with the successor-1 sections add the STARTS sensitivity; older reports still load |
| `--crosswalk` | `crosswalk.json` from `analysis/shp_crosswalk.py` (optional, needs `--shp`; exploratory overlay on F6 only) |
| `--criteria` | `criteria-v43.json`, used only for the G2 threshold lines and text |
| `--allocation` | post-G0 second binding record read by `allocation_preflight`, required once the gate root's `authorization-G2.json` names a second binding. It labels the G2 cells with their (a, r). The report refuses it unless it is the binding recorded in `authorization-G2.json`, and refuses `--criteria` unless its SHA-256 is the binding's `criteria_sha256` |
| `--stage-successor` | repeatable; a documented stage-summary successor (`ic-study.v4-stage-summary-successor.v1`) holding the complete `aggregate` summary that the frozen runner could not append. Its `freeze_sha256` must match the stage authorization in the gate root, its `sealed_root_identifier` the root's name, and its `completed` count the sealed task records. It is used only when `criteria.jsonl` has no complete line for that stage, and T3 and F4 label it "successor record, frozen aggregate" |

For the v4 run, both records are private coordination files: the second binding is
`coord-20260925/v4-allocation.json`, and the G1c successor is
`coord-20260925/v4-gate-logs/G1c-aggregate-successor.json`. The frozen runner cannot
append the complete G1c line, because its aggregate returns `pass` as a NumPy boolean
(decision 46).

The command validates every input against the frozen schema before writing anything.
It then writes each figure as vector PDF and 300-dpi PNG, each table as CSV and
booktabs LaTeX, and `manifest.json`. The manifest records the SHA-256 of every input
(for the gate root, its identifier, `criteria.jsonl` plus a digest of the listing of
every task record read; for each stage successor, whether it was used) and of every
output. It also records the git commit and the SHA-256 of each
reporting module. Output bytes are deterministic: the PDFs carry no creation or
modification dates, and a test checks that two renders are byte-identical. Both
renders ran in the same environment.

Code: `src/ic_study/analysis/` contains `detection_v4_report.py` (CLI and manifest),
`v4_report_schema.py` (strict loaders), `v4_report_tables.py`, `v4_report_figures.py`
and `v4_report_synthetic.py` (fixtures built by the frozen emitters).

## Export to the manuscript

`python -m ic_study.analysis.v4_report_export` takes the rendered `OUTDIR` (`--report`)
and the same inputs, and refuses them unless they match its manifest. It writes every
`generated/*.tex` file of the JCSS manuscript: T3 with F4, T4 with F5, F1, F2 for B,
the T1 boundaries and F6 for the main text, and F2 for A, C, D and E, F3, the
secondary targets, the low-strength cell diagnostics and the gap domain for the
supplement. An output that does not exist gets a comment that says why. The export
copies the figure PDFs and the T1s CSV (the electronic supplementary material) beside
them, fills the `\resultnum` placeholders of the text and writes the
`{"values": ...}` JSON that `pipeline/paper_check.py --submission --result-values`
reads. Every numeral of a generated table is a `\resultnum` bound to its report cell;
the counts of the Results shells come from the same loaded records; and every protocol
constant the text cites is read by `v4_report_protocol.py` from the frozen sources. The
release-day sequence, rehearsed on synthetic inputs, is in
[RELEASE-RUNBOOK.md](RELEASE-RUNBOOK.md).

## Registered and exploratory outputs

| Output | Class | Basis |
| --- | --- | --- |
| F1 a*(r) by family | registered | PR estimands and inference; D6; D8; D9 |
| F2 AUC profiles (one figure per family) | registered | `auc`, `lower` and `upper` are released per available strength, so F2 is drawable |
| F3 family offsets vs B | **exploratory** | no registered contrast; descriptive grid-step offset only |
| F4 gate diagnostics | registered | D7 and v4.1 criteria; the G0 evaluation counts are reported under R2 |
| F5 inventory status | registered | D9 |
| F6 SHP anchor overlay | **exploratory illustration** | SHP preregistration: the anchor's position on the frozen curve is an illustration; Wald CI plus the Heise envelope, labelled "not a CI"; SHP successor 1 adds the STARTS sensitivity and the optional synthetic crosswalk |
| T1, T1s a*(r) grid | registered | PR; D6; D8; D9 |
| T2 contrasts | not emitted | the protocol defines no between-family contrast quantity |
| T3 gate summary | registered | D7 |
| T4 inventory | registered | D9 |

Two registered quantities need a derivation or an operational rule:
- **Secondary targets 0.60 and 0.80 (PR).** The frozen `curve_report` emits
  boundaries for 0.70 only. The frozen `boundary_report` accepts the target, so T1
  derives a\* and its interval at 0.60 and 0.80 from the released bands, then replays
  the frozen gap censoring. The columns are labelled `derived_…`.
- **The "IC amplo" (wide interval) region (PR).** It has no numeric threshold. By the
  coordinator's decision, T1 labels a unit "indeterminate" when a\* = 0 or its
  inverted interval crosses 0.03 or has a censored end; the estimand is unchanged.

An 81-cell simultaneous band (PR) is not drawn: it is only allowed as an explicitly
identified additional band, and none is emitted.

## Schema mismatches fixed (pre-freeze loader vs frozen emitters)

The pre-freeze `detection_v4_report.load_unit` accepted a hand-designed "schema
version 1" record that no frozen code emits. It would have rejected every real
record. The replacement loader accepts exactly the frozen shapes. The fixtures are
produced by the frozen `execute_cell`, `complete_curve`, `released_curves`,
`execute_task`, `aggregate`, `fit_record`, `pipeline_record` and `band`; only the
panel simulator is replaced, and the bootstrap runs with fewer draws.

1. **Identity.** The old loader required `schema_version`, `unit_id`, `tier`,
   `family`, `channel`, `sensitivity` and `r` in each record. The frozen curve carries
   only `unit` (for example `t1-u00-r4`). Metadata is now joined from
   `v4_plan.inventory()`.
2. **Grid alignment.** The old loader required nine-element `strengths`,
   `point_auc`, `band_lower` and `band_upper`. The frozen record has
   `available_strengths`, `auc`, `lower` and `upper` over the successful strengths
   only (length 9 − `gap_count`), and all of them are absent when no cell succeeded.
3. **`logit_se`.** The old loader required it; the frozen curve never emits it.
4. **Critical value.** `critical_value` became `critical`. The D6 flag
   `empirical_exceeds_floor` was ignored before and is now reported.
5. **Cell states.** The old loader used an invented vocabulary (`cell_statuses`
   valid/not_started/ineligible/…, `gap_reasons`). The frozen `cells` field holds nine
   full cell records with `success` and `attempts[].status`, using the D4 solver
   statuses.
6. **Attempts.** `attempt_statuses` used to be at most two strings per cell. The
   frozen attempts are objects (`matching_pairs`, `status`, `evaluations`,
   `residual_se_units`, `validation_*`, …).
7. **Null gate.** `null_gate` (pass/fail/not_evaluated) became the booleans
   `valid_null_gate` and `valid_curve`.
8. **Status and inventory.** `unit_status` became `status`. Units that are not started
   or partial have no curve record; they exist only in the release `inventory`, which
   the old loader did not know about.
9. **Boundaries.** `a_star_point`, `a_star_interval` and `sustained_a_star_*` became
   `first`, `first_interval`, `sustained` and `sustained_interval`.
10. **Censoring flags.** The boolean `a_star_censored` and
    `sustained_a_star_censored` became the string keys `first_censoring`,
    `sustained_censoring`, `first_interval_censoring` and
    `sustained_interval_censoring` ("gap at a=…"). They are present only for gap
    censoring. Right-censoring beyond the grid is `None` with no key.
11. **Validity rule.** The old loader required all nine cells to be valid for
    `completo válido`. In the frozen code, `completo válido` holds exactly when the
    a = 0 null gate is valid. Valid units may have gaps and censored boundaries.
12. **Inversion domain.** The old loader recomputed boundaries over the full nine
    strengths. The frozen code inverts over the gap-free available grid and then
    censors across gaps; the loader now replays exactly that.
13. **Unknown fields.** The old loader did not know `band_complete`, `gap_count`,
    `nonmonotone_band`, `cells` or `main_curve_valid` (added to tier-1 curves when the
    main curve is invalid).
14. **Provenance.** The old loader required `code_hash`, `seed_hash`,
    `seeds_namespace` and `host` in every record. The frozen release carries none of
    them; provenance lives in the sealed store.
15. **Strictness.** The old loader rejected any extra field, so it would have rejected
    every frozen record.
16. **Release wrapper.** The old loader expected unwrapped records. The frozen release
    is `{"inventory": {closed_utc, units, main_curve_valid}, "curves": [...]}`.
17. **Left-censored endpoints.** The old loader read a `None` interval endpoint only
    as right-censoring. After gap censoring, a frozen sustained interval can have
    `None` as its lower endpoint.
18. **Gate records.** The old loader never read the gate. The new loader reads
    `criteria.jsonl`, the stage authorization records at the gate root and the G0 and
    G1b task records, and verifies each directory seal by hashing. It deliberately
    avoids `SealedStore.get_json`, which appends to `access.jsonl`.

## Samples

`samples/` holds watermarked SYNTHETIC renders: 150-dpi PNG, tables and manifest,
with "synthetic" in every file name. Regenerate them with:

```sh
cd studies/ic-2026-2027
uv run --frozen python \
    experiments/exploratory/detection-boundary-v4/report/render_samples.py
```

The scenario is artificial. It covers:
- valid units;
- units not reached on the grid;
- gap censoring, including a sustained interval whose upper end is not reached above
  the last gap;
- every gap kind: family limits screened with zero evaluations and reached along the
  profile, solver and validation failures, and dependency gaps in a control unit;
- a failed null gate;
- an all-gap unit;
- partial and not-started units, so the main curve is invalid;
- a tier-4 sensitivity;
- gate records with one aggregate line per shard, G0 fits of every final-status kind,
  anchor-exact fits with one evaluation, a G1c stage whose complete line the frozen
  runner could not append plus its successor record, and a second binding record;
- an SHP record with the successor-1 sections (admissible STARTS) and a synthetic
  crosswalk overlay on F6.

The numbers mean nothing.

## Known constraints

- **The gate cannot be run from this branch.** `v4_gate.preflight` requires the whole
  code closure (every `.py` under `src/` and `tests/`, plus `pyproject.toml` and
  `uv.lock`) to equal the freeze record exactly. This branch was already outside that
  closure before the reporting work: commits 43bbe374 and 4c204d38 changed
  `pyproject.toml` and `uv.lock` and added modules. The gate and tiers must run from
  37513841. The test `test_frozen_files_are_untouched` checks that every other frozen
  file still matches its hash.
- **Python version.** `.python-version` pins 3.12.13. This environment had 3.12.3
  (`UV_PYTHON=/usr/bin/python3.12`), which satisfies `requires-python`, so the
  determinism check covers two renders in one environment only.
