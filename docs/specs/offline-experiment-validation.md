# Offline experiment validation

The study owns a read-only validator for the two executed exploratory pilot
formats. It consumes each unchanged `run-manifest.json`, adjacent `spec.json`,
`analysis-input.json` and `validation.json`, the review files bound by that
validation record, and the external JSONL artifacts. It produces a new,
deterministic `offline-experiment-validation-v1` receipt. This is an integrity
check, not regeneration, statistical reproduction, review acceptance or topic
selection. It neither imports a simulator nor accesses the network.

Run it through the study package:

```sh
python -m ic_study.validation.experiments \
  --study-root studies/ic-2026-2027 \
  --manifest studies/ic-2026-2027/experiments/exploratory/fragmentation-pilot-v1/run-manifest.json \
  --receipt /private/output/fragmentation-validation.json
```

The optional `--artifact-root` resolves objects by SHA-256, either directly or
under a two-character shard, instead of relying on historical machine paths.
Metadata and receipt inputs are regular local files. Receipts are create-only,
mode 0600, and written only after all checks pass. Missing bytes are reported as
operationally unavailable; invalid bytes are reported as integrity failures.
Reads consume at most the byte limit plus one, even if a file grows after the
initial metadata check. Oversized or excessively nested JSON numbers/structures
and malformed record shapes return an invalid diagnostic without a traceback.

## Closure

- Accept only the existing fragmentation and forecast manifest/spec/header
  formats, with unique run identities and declared phases/budgets.
- Verify artifact hash and size, exactly one header and completed footer,
  record kinds, declared counts, specification bytes and embedded value,
  environment and revision bindings.
- Verify every recorded source and the lock against the exact Git commit,
  requiring the complete tracked study Python source set, pyproject and lock.
  Current working-tree edits do not replace historical code. Git operations
  only read local objects; a missing revision never triggers a fetch.
- Fragmentation records cover the declared ordered design and seed identities;
  preserve certified, right-censored and numerical-failure counts separately.
  Model arms share inputs. These rows are not independent graph realizations.
- Forecast records cover each cell/replicate once with complete ordered waves.
  Each wave covers exactly the declared models, with its model-bound seed,
  the budgeted number of valid eleven-bin histograms, and the five finite
  numeric scores. Training selections name declared models for those scores.
  Overflowing JSON floats, including `1e999`, are rejected in every input.
  Data identity includes the specification's data group, cell and replicate;
  precision repeats the exact complete set of primary data identities and never
  increases the count of distinct
  analysis data trajectories. Matching identities must have identical observed
  data and seeds; confirmation data must be disjoint. This proves identity
  consistency, not statistical independence of pseudorandom draws.
- Verify the analysis-to-manifest hash and existing validation-to-review/input
  hashes, including equality between the supplied manifest bytes and the
  validation record's `run-manifest.json` binding. Report those documents as bound
  review evidence, never as a newly
  passed scientific or engineering gate. Do not re-evaluate their prose.

The receipt names all run hashes, phases, counts, source revisions and input
hashes. It explicitly sets scientific acceptance false and identifies excluded
checks: regenerated trajectories, recalculated scores, scientific claims,
novelty, and human approval. Historical manifests are never upgraded in place.

## Acceptance

Small fixtures exercise both historical formats through the public validator
and CLI. Tampering, duplicate/missing rows, absent footer, wrong counts,
unbound specs/revisions/sources/locks/reviews, invalid paths, and duplicate
forecast data identities fail closed. Tests demonstrate that censored rows and
precision repetitions cannot inflate successful or distinct-data counts.
The integration check reads the nine existing JSONL objects without simulation
and creates private successor receipts. No dependency or shared workbench
contract is introduced in this slice.
