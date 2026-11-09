# Primary acquisition of systematic-map v2

Preparation recorded on 2026-09-09. Search execution is authorized by the
[owner continuation record](../../decisions/2026-09-09-systematic-map-v2-search-authorization.md)
and its [machine-readable approval](../protocol/approvals/opinion-dynamics-systematic-map-v2-20260909.toml).
The protocol SHA-256 is
`540ed755dd2ac4fe979975f737b89075945023f9fb14688e2010a773331f45ed`;
its approved Git revision is `7c1e6940a7a38d436ff13534e81d1e0f85e22748`.

## Operational preparation

The 34 registered API queries retain the publication cutoff 2026-09-07.
The prior development runs remain independent. The second successor completed
all declared API searches and reproduced its report and lossless preparation
offline. This is not a deduplicated corpus or a completed systematic review;
no source failure is interpreted as scientific absence.

A read-only capacity check used the normalized pages selected by the final
development diagnostics: ten unrestricted OpenAlex sample records (one per
query, including the corrected Q03), 1,056 arXiv records and 1,401 DBLP records.
Weighting their current serialized sizes by the observed query totals gives
approximately 22,362 overlapping source observations and 243 pages. The estimated
acquisition report is 59,348,404 bytes; the lossless observation projection is
72,152,422 bytes and its separate record list is 30,552,179 bytes. These are
planning estimates from non-random samples, especially sparse for OpenAlex;
they do not assert the eventual corpus size or completeness.

The existing acquisition/replay CLI aggregate limit is increased from
50,000,000 to 100,000,000 bytes. Corpus preparation will use the same existing
artifact-store bound. The full pipeline's configurable `max_artifact_bytes`
must also be set explicitly to this value if it consumes these aggregates.
Individual HTTP response and source-access limits remain unchanged.

The durable acquisition adapter must preserve the provider's `Retry-After`
through checkpoints and replay. Historical failure envelopes without that
field retain their original backoff behavior. Exhausted attempts remain an
immutable incomplete outcome; unrecorded dispatches block automatic resumption.

The private runtime is
`/Users/davi/.local/state/research-workbench/primary-acquisition-20260909-v2`,
with run ID `opinion-dynamics-map-v2-primary-20260909`. It retains raw bytes,
normalized observations, journal entries and exact receipts outside Git.
Only metadata, counts, checks and content hashes belong in the public record.

## Next scientific boundary

Offline acquisition replay precedes corpus preparation. The existing corpus
runtime preserves exact-identifier groups, unresolved fuzzy candidates and
policy conflicts; an incomplete or owner-waiting corpus does not authorize
screening. Calibration reference judgments, adjudication and scientific
acceptance remain real owner actions. No model role is enabled by this search.

## First execution and source-host correction

The first execution started on 2026-09-09 with clean checkout
`898136ef95ec5089607cb2b6f4f48890b3b4afff`. The original approval and protocol
remain bound to `7c1e6940a7a38d436ff13534e81d1e0f85e22748`; that revision
identifies the approved subject, while the later revision identifies its host.

At 19:07 UTC, arXiv had retained 1,935 observations in 20 pages: Q01 and Q02
reached exhaustion, while Q03 retained two pages and Q04–Q10 retained none.
The eight incomplete searches exhausted four attempts each, retaining 32
transient-failure envelopes. The executor continued to DBLP and OpenAlex.
These failure envelopes preserve the delay but not the original HTTP status
or transport exception, so their cause cannot be reconstructed more precisely.

Inspection found that the production host paced DBLP but omitted arXiv pacing.
The [arXiv API terms](https://info.arxiv.org/help/api/tou.html#rate-limits),
checked on 2026-09-09, require one request at most every three seconds and one
connection at a time across the operator's machines. The bounded correction
adds a three-second interval after each arXiv call, including failures and
query transitions. DBLP retains its ten-second interval; HTTP byte limits,
queries, parser versions and retry budgets remain unchanged. No concurrent
arXiv acquisition is started by this task.

The missing interval is a demonstrated host defect, not proof of the cause of
these retained failures. A successor must preserve this first execution, link
its actual recorded checkpoints, and re-run under the corrected host after the
current acquisition has ended. A terminal receipt may only be linked when one
exists.

The separate [deduplication diagnostic](2026-09-09-deduplication-v1-category-diagnostic.md)
also prevents treating the collected observations as a screening-ready corpus.
It preserves the original metadata and requires a concrete identifier rule
before a versioned algorithm successor. The owner's response is pending.

## Interrupted first attempt

The first process exited with code 2 during `search.openalex.q01`, page index 2,
with `bibliographic provider response is invalid`. DBLP had completed all 14
queries (4,419 observations, 53 pages); OpenAlex had recorded two pages and
200 observations. Together with arXiv, the retained prefix has 6,554 source
observations in 75 pages. It is not a completed acquired corpus.

All 75 recorded pages reproduced from their raw bytes and exact requests.
The 32 transient-failure envelopes remain recorded. The prefix-verification
summary has SHA-256
`42b504700c99363f0656d5d92d44ddb8872027f71389ef99c274b789258acd7e`, under the
private `publish-20260909/primary-prefix-verification.json` preparation root.

No acquisition report or terminal acquisition receipt was created. The latest
acquisition event is the original `acquisition_bound`, SHA-256
`b5bc1c0cd98329972823ddc25e94784478fde82f21fd435ea7f296809ff4d447`.
The pending request event is
`65ed40bddf67a5cfd72ad8e33b19549c1e6c9f7cb616cf11c97054194e43faed`.
A successor links these actual checkpoints and the interrupted run; it must
not invent a terminal receipt or silently reconcile the missing response.

The [OpenAlex correction](2026-09-09-openalex-sparse-abstract-correction.md)
preserves an article with an unavailable sparse abstract while retaining its
raw index. It does not alter the original pending operation. Separately, one
checkpointed arXiv recovery probe returned the previously unavailable Q03
page index 2 with 30 records and exhaustion; its raw hash is
`412486ef9724dfa52a51a3f6c19e9d61bb2032c6a86b0cd2268ff45e15e64fa4`.
That diagnostic is not inserted into the interrupted acquisition.

## Interrupted first successor

Run `opinion-dynamics-map-v2-primary-20260909-successor-1` used clean host
`d3421cdad0f2a05483d0f7fd0d8635ed63440002`, retaining the same approved protocol,
queries and budgets. Its private runtime is
`/Users/davi/.local/state/research-workbench/primary-acquisition-20260909-v2-successor-1`.
It exited with code 2 at 20:20 UTC on 2026-09-09 during OpenAlex Q01 page index 43.

All ten arXiv queries completed: 2,545 observations in 31 pages. All fourteen
DBLP queries completed: 4,419 observations in 53 pages. OpenAlex retained 4,300
observations in 43 pages of Q01; that query and the remaining nine queries are
incomplete. No transient-failure envelope was recorded in this successor.

All 127 recorded pages reproduced from their exact requests and raw bytes,
retaining 11,264 source observations. The independent prefix verification has
SHA-256 `7e5e14089ad8cc6ce2ab33a6bfb00017292bbb5e916efa419dcfa9a17a0fec22`.
This verification is not a complete acquisition replay: no report or terminal
receipt exists. The sole acquisition event remains `acquisition_bound`, with
SHA-256 `b5bc1c0cd98329972823ddc25e94784478fde82f21fd435ea7f296809ff4d447`.
The pending request event has SHA-256
`40883b4c2e1155d6ca47547fd9d9b4fef017b7d982475118458b2a268092927b`.

A raw candidate saved after that dispatch contains 100 provider results and
has SHA-256 `ee2ad9e8e1ad3b8d6933c02a88fc5a0eb6d39bd3accb4e459565407789288d6e`
(560,754 bytes). It has no recorded response binding and remains separate from
the verified prefix. Independent normalization identified one missing title at
zero-based offset 98: OpenAlex `W3128425659`, DOI `10.5220/0010337101370148`,
with empty `display_name` and null `title`. The v1 record contract rejects that
absence. Neither a fabricated title nor silent removal is an acceptable repair.

A versioned acquisition representation retains the absent title and continues
pagination while preserving v1 replay. Lossless observation
preparation can retain incomplete metadata; canonical works and screening must
remain blocked until required metadata has evidence. The pending operation is
unchanged, and the next execution must use a distinct run identity linked to
these actual checkpoints.

## Missing-title correction and offline verification

The implementation at `370298286545e63c084c61aeb1e7301f5936b10e` adds the
explicit `acquire --normalization-version 2` option. The acquisition binding
and report use schema 3; search executions and the lossless projection use
schema 2. Unaffected pages and titled records retain their v1 representation.
The projection deterministically lists missing-title observation IDs and
canonicalization stops before deduplication. The original protocol and approval
remain unchanged. See the [acquisition procedure](../../../../../docs/process/systematic-review-acquisition.md#versioned-title-absence).

All 473 focused tests passed, together with Ruff and mypy. Historical schema
and serialization hashes are checked against the v1 base. An offline diagnostic
of the real unbound raw candidate retained all 100 positions, including the
missing title at rank 4,399, preserved the following cursor and reproduced the
page from raw bytes. The other 99 records retained schema 1. The original
runtime files remained unchanged, and v1 normalization still rejected the
missing title. The diagnostic used an explicitly artificial timestamp and did
not claim a retrieval, response binding, or completed acquisition.

The diagnostic summary SHA-256 is
`c4c086f6a5446de973fd1e2749d323ac88b9cf664ec3506eae78156818da1052`, retained
under the private `openalex-missing-title-offline-20260909` root. All 127 earlier
recorded pages also reproduced under the new code with the same prefix summary
SHA-256 `7e5e14089ad8cc6ce2ab33a6bfb00017292bbb5e916efa419dcfa9a17a0fec22`.
The [integrated validation](../../../../../docs/research/integrated-validation-2026-09-09.md)
records the macOS/Ubuntu matrix and its isolated assertion correction. A new
acquisition run remains a distinct gate; this diagnostic does not close either
interrupted attempt.

## Second successor: completed acquisition and preparation

Run `opinion-dynamics-map-v2-primary-20260909-successor-2` started on 2026-09-09
at 21:33 UTC in a clean, fixed checkout of
`8a4eba0a09229e34da42ee6e1771872a41da0a1f`, with explicit normalization version 2.
Its separate private root is
`/Users/davi/.local/state/research-workbench/primary-acquisition-20260909-v2-successor-2`.
The original protocol, approval, 34 queries and per-query budgets remain bound
to the approved subject. It performs new requests and copies no retained pages
from the interrupted attempts. Its execution metadata links the prior failure
summary and offline title-absence diagnostic by hash.

The process exited successfully at 22:06:25 UTC. All 34 searches exhausted
their pagination, with no transient failures or additional attempts. The report
status is `primary_search_complete`.

| Source | Completed queries | Pages | Source-record observations |
| --- | ---: | ---: | ---: |
| arXiv | 10/10 | 31 | 2,545 |
| DBLP | 14/14 | 53 | 4,419 |
| OpenAlex | 10/10 | 159 | 15,440 |
| Total | 34/34 | 243 | 22,404 |

These observations contain 20,086 distinct provider record identities. Neither
count is a number of deduplicated scholarly works or eligible studies. Provider
pagination exhaustion does not establish independent source coverage or a
transactional snapshot of a changing index.

Read-only replay reproduced the complete report from the retained requests and
raw responses, without network access or changes to runtime files. The report
has 86,034,682 bytes and SHA-256
`e2ca7d8d0bd8bc811962fc5d8290a23f812963e56f317354821571c0d365ebcc`.
Its terminal event SHA-256 is
`975e65d4fcabe1a3c1a240317c13d02b8acefae455352e3e60663de7f862121f`.
The private `publish-20260909/successor-2-acquisition-replay.json` summary has
SHA-256 `e1737014ad5d2895dda533e481998575b9224c0ff3e3da32787cb5b3c4c29df3`.

Lossless preparation retained every observation and also reproduced exactly
through read-only replay. The projection has 98,915,505 bytes, within the existing
100,000,000-byte aggregate bound, and SHA-256
`e8c65845a1de4e0226d72cb86a99b1727848452c7417bfe3fe5f3ff92dc6971c`.
The separate records artifact has 43,897,046 bytes and SHA-256
`f1136eda2f2a3a181f71b1372669b7ec7db0c4b521ec22e98ee3be35b69e2860`.
The preparation receipt artifact has SHA-256
`0cea386573e8c7d31ec4409ed35d7ddb675b5f192e442f5f2645a2d599531ae1`;
the private runtime's `corpus-preparation-summary.json` has SHA-256
`93e3a12705fa9683b968f8a0d5d37b76810483ab36bea59fc16c68d3e4a490b8`.

Two observations have no title. Both identify provider record
`openalex.c9aa697c335c7755b6efcc2b` in Q01, at ranks 4,399 and 4,401 in separate
pages. Their original raw hashes are, respectively,
`6506bea21622010d6b99136bd018266c3f7cc01ac30b2ed2fbb44dd069606c23` and
`ea71faaf8126318aea50724a8cb43efd9a129c062929f4f9f7e4f2882c14ef30`.
Both occurrences remain present; no title or explanation for the repetition is
invented. The projection explicitly identifies them as
`observation.8b1df74023eefdfd91807a630e74114cb2a56bb9211bce2bb549d0ac06cd8e99`
and `observation.ea43334e81a7abd8b2415b5edfaf94677dd9b503249c90bc5b75ae5ab6a902eb`
(the list is canonical by observation ID, not a rank-to-ID mapping).

The operators received independent read-only review before execution. Neither
operator called deduplication or corpus canonicalization. The next boundary is
the pending identifier-policy decision and evidence-backed recovery of the
absent title. Calibration, screening, manual supplements and scientific
acceptance remain separate. The two interrupted predecessors stay unchanged.
