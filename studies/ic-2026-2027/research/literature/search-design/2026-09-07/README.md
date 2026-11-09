# Query-design measurements

These inputs continue the query-design work interrupted on 2026-09-07. They
are separate diagnostic protocols, not the protocol for primary acquisition.
The frozen review cutoff remains 2026-09-07 even when measurement takes place
later. The original `opinion-dynamics-systematic-map-v1` is unchanged.

`seeds.json` transcribes the 16 proposed works in the
[seed ledger](../../../../../../docs/research/systematic-search-successor-preparation-2026-09-06.md#seed-ledger-for-recall-calibration).
Its OpenAlex IDs come from the interrupted diagnostic; exact DOI and title
agreement must be checked against the newly retained responses before relying
on those mappings. Hegselmann and Krause is deliberately DOI-less. Twelve
seeds test primary-model coverage, three test secondary-study snowballing, and
Clifford and Sudbury is a lineage sentinel with an expected eligibility
exclusion. They are query-development cases, not an unseen verification set.

`openalex-membership-v2.json` combines each corrected query with a filter over
the 16 declared OpenAlex work IDs. This measures membership in a query's result
set with bounded requests. Returned ranks apply only inside the seed-restricted
query; they are not ranks in the full discovery query and do not establish
retrieval before a full-search page cap. The matrix is not screening recall,
precision, human calibration, scientific inclusion or an approved search.

OpenAlex documents [OR within a filter, intersected with other filters](https://help.openalex.org/api/filtering/)
and [batching up to 100 IDs with `per_page=100`](https://help.openalex.org/api/authentication/).
The query vocabulary uses the
[documented search fields and Boolean grammar](https://help.openalex.org/api/searching/).
The type filter includes conference papers and acquisition has no metadata
language filter. A minimum set covering these known seeds is a diagnostic,
not sufficient grounds to remove model families or recent research routes.

Run from the repository root using the existing dedicated credential:

```bash
uv run --project workbench --locked python scripts/measure_seed_recall.py \
  --protocol studies/ic-2026-2027/research/literature/search-design/2026-09-07/openalex-membership-v2.json \
  --seeds studies/ic-2026-2027/research/literature/search-design/2026-09-07/seeds.json \
  --run-root "$HOME/.local/state/research-workbench/claude-handoff-20260907/openalex-membership-v2" \
  --openalex-auth-file "$HOME/.local/state/research-workbench/credentials/openalex-token"
```

Each successful page and provider failure is journaled before the next request.
Repeating the command revalidates retained pages from raw bytes and reproduces
the bounded failure sequence; only missing attempts make network calls or incur
the provider pacing delay. Failure checkpoints retain retry classification and
delay, never exception text that could expose a credential. An interruption
before a GET response is checkpointed can repeat that read-only GET; it does
not create a scientific record. Changed protocol or seed bytes require a new
run root. Add `--offline` and omit the credential to replay entirely from
retained bytes. A failed provider response never becomes evidence of absence.
To retry a completed failed measurement, create a linked successor rather than
overwriting its failure history. Outputs are content-addressed derived reports;
the immutable page journals and their raw sources are the evidence.

The [measured matrix](results.md) compares each seed across the three sources
with the different measurement methods stated explicitly. The
[DBLP projection](dblp-evidence-combined.json) selects the seven unaffected
queries from v2, five successful subblocks from v3, Q06a from v4 and Q04b from
v5. Every selected query points to its own result digest. It is a rebuildable
cross-measurement view, not a new acquisition report or primary study corpus.
The original failed runs remain unchanged and reproduce their original failures.
