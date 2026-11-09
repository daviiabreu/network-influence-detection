# Broad systematic-map acquisition v3

Execution began at **2026-09-12 02:42:51 UTC** (2026-09-11 23:42:51 BRT).
This is a new network acquisition under the
[dated owner instruction](../../decisions/2026-09-11-broad-research-execution.md),
[v3 approval](../protocol/approvals/opinion-dynamics-systematic-map-v3-20260911.toml)
and [readable protocol amendment](../protocol/opinion-dynamics-systematic-map-v3-review.md).
The historical v2 acquisition and all its interrupted attempts remain unchanged.

## Effective successor: search closed, preparation retained

The interrupted-prefix successor `opinion-dynamics-map-v3-broad-20260911-interrupted-1`
finished at **2026-09-12 06:02:23 UTC** with `primary_search_complete`.
All 1,027 registered queries are closed: 60 thematic searches and 967 identifier
lookups. Its 2,473 pages contain 54,570 observations and 49,333 distinct provider
record identities. These are neither deduplicated works nor eligible studies.
The [per-query metadata](../searches/2026-09-12-v3-acquisition-results.json)
retains every query's status, counts, attempt history and reuse status.

| Source | Thematic queries | Identifier queries | Pages | Observations |
| --- | ---: | ---: | ---: | ---: |
| arXiv | 17 | 31 | 90 | 4,917 |
| Crossref | 0 | 936 | 1,871 | 935 |
| DBLP | 25 | 0 | 77 | 6,153 |
| OpenAlex | 18 | 0 | 435 | 42,565 |

The successor reused 997 complete searches through explicit offline normalization
3 to 4. It restarted 29 arXiv lookups and OpenAlex q16 in a new namespace; all
59 fresh requests succeeded without a new failure. The arXiv requests used at
least 15 seconds between attempts. Two queries returned zero observations:
`metadata.crossref.doi.0883` and `search.dblp.q03c`. A zero result is retained
source evidence, not an exclusion decision.

Native read-only replay reproduced the report. Baseline checks verified that
all 11,525 pre-existing files in the CAS and operation journals retained their
bytes, size, modification time and mode. The interrupted parent, its uncertain
operation and orphan raw page remain unchanged and have no manufactured terminal.

| Binding or evidence | SHA-256 / revision |
| --- | --- |
| Execution code revision | `c8461e11b9d9d7faec9cda7ccb7bf9106fe953f0` |
| Interrupted prefix | `7c354780824577d338ba89845b16e9e6ffbfcf5bf6342ee679c0bc11a6667d7d` |
| Acquisition report, schema 5 | `edfa48474097d7c81e441fdbe5089a924d514deabbb6baf3bbaf60e0df220a11` |
| Acquisition receipt | `5aa52db3b98487a17a5c50d246c23e4c97d611a4a1c6c589119c2cf8d29bc675` |
| Recovery operator | `123d575d874707d06234f544d4eb294c6be85fe22af719b69564525596004072` |
| Preparation receipt | `fa934b8b065880228373d76040527a76fc7cdced9c92ebb69a31891485ccf4fa` |
| Lossless observation projection | `93c8086aa6b0231fd019291f9bb3984e5e436e629c4424e95ae499729957cc85` |
| Projected records | `772afb69e868ef3fc6cf94e79d3c1b422f11f8fba453621c0092fc65028fa5a1` |

The native preparation retains all 54,570 observations. At **06:07:06 UTC** the
subsequent corpus stage raised `IncompleteBibliographicMetadataError` because
an entire identity group has no titled manifestation. It produced no stage
receipt, deduplication result or adjudication queue. Work and adjudication counts
are unavailable. The [editorial metadata investigation](../search-design/2026-09-12-area-map/missing-title-evidence.md)
is separate evidence and was not injected into the approved acquisition.
The later [corpus-metadata successor](2026-09-12-corpus-metadata-successor.md)
retained all observations in a complete proposed-work representation and an
explicitly incomplete review queue; this initial failure remains unchanged.

The [read-only preparation diagnostic](../searches/2026-09-12-v3-preparation-diagnostic.json)
finished at 06:08:57 UTC. Native acquisition and preparation replay agreed with
their retained outputs, and the protected files retained their bytes and file
metadata. Ten observations have no title; nine lack a directly linked titled
companion. Their [source-located inventory](../searches/2026-09-12-v3-missing-title-records.json)
adds two q16 identities to the seven unresolved leads from the parent prefix.
There are also 14,878 observations without an abstract. No missing field became
an exclusion or a fabricated title. The diagnostic did not attempt deduplication
again; the native corpus stage above had already attempted and failed.

All [64 frozen challenge DOIs](../searches/2026-09-12-v3-challenge-64-results.json)
now match: 59 through thematic searches and five through identifier recovery
only. This measures the response to deliberate expansion, not independent
recall, sensitivity or the number of eligible studies. The private diagnostic
summary SHA-256 is `3a30917bf50eef60d45d0326eafe715604b2f2d4c04f1e59aa9689e6838bd3a5`;
its reviewed operator SHA-256 is
`1442ae4fa629bffdb7186e0bb03d930c906ef1783fcc4a2d658c048e802d0092`.

An [audit of every OpenAlex page](../searches/2026-09-12-openalex-pagination-audit.json)
verified all 435 raw pages and exact ordered raw-to-normalized ID correspondence.
Fifteen queries contain 84 repeated occurrences between pages, with none within
a page. Six queries have distinct-ID counts different from stable `meta.count`:
q01 (7,616 / 7,626), q11 (6,632 / 6,638), q12 (2,394 / 2,396), q14b
(2,348 / 2,349), q14c (8,730 / 8,733) and q16 (2,955 / 2,956). The repeated
occurrences already exist in provider responses. These discrepancies do not
identify missing studies or measure recall. The private all-query audit has
SHA-256 `6bf58336f9248a37a72decb630828c804b19be2a8bc22a253202e266de7db21a`.

Before this successor, both macOS and clean Ubuntu passed **3,469 workbench
tests and six study tests**, seven structure checks, complete lint/type checks
and both wheel installation smokes at the exact execution revision. Independent
review covered the changed normalization/recovery boundary and private operators.
The macOS log SHA-256 is
`21c6cb24bc9bc7ce9a816be4c19d1cb15a0a286f7c2f4db478146fec25706db7`;
the Ubuntu log is
`d3613969244ae19e38bcdd311727b4b3d21e1e9ce1a262f5fc3071ee5357596a`.
This is local engineering evidence, not a claim about hosted CI or scientific
acceptance. Raw evidence remains in the private runtime named below. The new
operator metadata is in sibling `acquisition-v3-interrupted-successor-1/` and
`corpus-v3-interrupted-successor-1/` directories.

## Interrupted parent, 2026-09-12 05:09 UTC

The operator exited with `BibliographicSearchError` at OpenAlex
`search.openalex.q16`, page index 23. There is no terminal acquisition receipt.
The dependent driver also exited before corpus preparation or selective recovery;
neither downstream operator ran. The stopped attempt remains intact.

Its closed progress log records 2,437 accepted pages and 53,882 normalized
source-record observations. These are interrupted-run counts, not a canonical
corpus or scientific eligibility count:

| Source | Accepted pages | Observations |
| --- | ---: | ---: |
| arXiv | 61 | 4,888 |
| Crossref | 1,871 | 935 |
| DBLP | 77 | 6,153 |
| OpenAlex | 428 | 41,906 |

All 1,027 query IDs were reached. The log contains an exhausted page for 997;
29 arXiv identifier lookups exhausted their retry budgets, and the final
OpenAlex query was interrupted. The log SHA-256 is
`943fcec803ecc2e1fcdf34b4a2ee083c764ed466a6c267e2fa854753fd6ea3a9`.
The arXiv total includes 4,886 observations from its 17 thematic searches and
two identifier responses. Its successful thematic requests do not erase the
separate identifier failures.

The failed raw OpenAlex page was retained, SHA-256
`9d8a907bb41b3d3de23af997d883698ac32b1c6b8a60aa84a3f1430830decbda`.
At `results[60]`, work `W2737956477` supplies the optional DOI URL
`https://doi.org/10.46901/revistadadpu.i08.p%p`. Normalization 3 rejects its
malformed percent escape. The raw page has no completed normalized response
operation and is excluded from the accepted-page counts above. Its metadata
does not establish that this source is an eligible study.

The versioned correction and interrupted-predecessor recovery described above
retain the original DOI literal as unresolved metadata, preserve versions 1–3,
validate the original operation prefix, and restart unfinished queries in a
new namespace. No artificial terminal receipt was created for this parent.
The effective successor has its own verified code revision and recorded lineage.

### OpenAlex count discrepancy, independently reproduced offline

The first OpenAlex query has 77 distinct requests and raw pages. Every request
used the exact cursor returned by its predecessor, with other query fields
unchanged. All 7,640 normalized IDs occur in the same order in the raw JSONs.
There are 24 repeated occurrences across adjacent pages, leaving 7,616 distinct
OpenAlex IDs; every page declares `meta.count=7626`. The difference of ten
does not identify ten missing studies or measure scientific recall.

The last raw page contains 40 results with `next_cursor=null`. Thus navigation
ended on the provider's cursor signal; it did not demonstrate the null-cursor
plus empty-results condition described in the
[official pagination documentation](https://help.openalex.org/api/paging/).
The [sorting documentation](https://help.openalex.org/api/sorting/) allows
multiple keys but does not establish a stable population across this capture.
No local page reuse or cursor substitution was found; the internal provider
cause and bibliographic completeness remain undetermined.

The independent audit checked 231 CAS objects (77 requests, normalized responses
and raw pages), all 76 cursor links, and JSON-Pointer locations for every repeat.
Its private `openalex-q01-independent-audit/manifest.json` has SHA-256
`efe516a2a4970efd039090ded01f6eaa70a3b8d57ab1260c51a31b8dc1c79fb8`.
`diagnostic.json` has SHA-256
`3fb259bf75540b9887994754004e3e80fc2e1971a4013cbf19e4280cc0d27f43`;
the documentation-projection manifest has SHA-256
`e0cf133627674ff5943f392fb257f34ba9b3e70a4b73195222a0e8a65930ba62`.
No additional bibliographic API request or dataset download was used in this
audit, and no provider inconsistency was converted into a scientific exclusion.

## Registered coverage

The publication window is 1970-01-01 through 2026-09-11. The 1,027 strategies
comprise **60 thematic searches** (17 arXiv, 25 DBLP, 18 OpenAlex) and
**967 identifier lookups** (936 Crossref DOI, 31 arXiv ID). Identifier recovery
is not counted as an additional thematic search. Broadening includes six new
query families and three reference graphs, with 1,194 reference entries and
950 distinct deposited DOI names before source-specific registration and
validation. See the [coverage audit](../search-design/2026-09-11-coverage/README.md).

The 64-work challenge set was frozen before baseline comparison. The baseline's 38 exact
DOI matches, two title-only leads and 24 unmatched identifiers describe that
diagnostic; they are not an eligibility assessment or a measured recall rate.
Controlled publisher exports, unresolved reference identities and later
eligible-study citation chasing remain separate coverage questions.

## Frozen execution

| Binding | Value |
| --- | --- |
| Run ID | `opinion-dynamics-map-v3-broad-20260911` |
| Approved protocol commit | `3b71a915252c7986f3dbf5310117eace4c8fa98f` |
| Protocol canonical SHA-256 | `fa280dff232ec122355755e67785f7f4da8709c2429da7dfb0c6148ec9e25d6f` |
| Approval file SHA-256 | `135e44b462f7001b3ca4c9088be3829d6fe1633b34547fb612f937dc0601b774` |
| Execution code commit | `4371032fc550b08ac63af276b3543f81524184c7` |
| Operator SHA-256 | `6234f6d3df7493a25f311e522f8ce5e0bd897c23b4125857ec634ae70225d520` |
| Normalization | `3` |
| Deduplication policy | `2`, explicit typed-identifier allowlist |
| Artifact size ceiling | 512,000,000 bytes per artifact |

The private runtime is
`/Users/davi/.local/state/research-workbench/broad-research-20260911/acquisition-v3`.
It contains the execution metadata, native operation journal, CAS and a safe
network progress log. The operator asserts the clean execution commit and
Python import provenance. Raw pages are acquired anew; no historical pages
are relabelled or copied into this run. Individual response bounds and
source-host restrictions remain enforced by the native adapter. The existing
dedicated OpenAlex credential stays outside Git and is sent only to its host.

Crossref requests use the exact DOI filter without the additional text query:
a retained live diagnostic showed that the old combination could suppress an
existing DOI. Normalization 3 preserves literal DOI suffixes, including SICI
angle brackets; parsers 1 and 2 retain their historical replay behavior.
Crossref attempts are separated by at least one second. Native arXiv/DBLP
pacing, bounded retries and uncertain-dispatch protection remain enabled.

## Engineering evidence

The integrated macOS and Ubuntu matrices first exposed a legacy screening
type error, then an obsolete repository test that allowed only the retained
v2 authorization. Both were corrected before dispatch. On commit `9b68723`,
each OS passed 3,325 workbench tests and failed that one authorization-list
test. Commit `4371032` changes only that test, validates both authorizations,
and passed its eight contract tests on both OSes. Both study suites passed
all six tests, and both project wheels built and passed installation smoke
checks. Structure, lint and full type checks passed in the recorded matrix
and affected continuations. Failed runs remain retained; this is a combined
matrix with affected checks resumed after corrections, not a claim that the
first invocation passed.

Ubuntu used the existing Ubuntu 24.04 arm64 image
`sha256:735dcd779b8552596ab34af6db18ef34be4fa158d3804bdbf14da966f145b75f`,
Python 3.12.13 and uv 0.10.9. This local evidence does not report hosted CI as
passed. Private log SHA-256 values:

| Log | SHA-256 |
| --- | --- |
| macOS full tests on `9b68723` | `b1789db55b6645ca78341f9a105ee27da033882d38e3712a5b5984f0fd869158` |
| macOS remaining checks on `4371032` | `84bbcf281ce268d45d3087508c2fc74eda2de2d5a9e9ec11e4df3cfc63e7191f` |
| Ubuntu full tests on `9b68723` | `c8218c0a97699b4f7062d51f6722c765ceda97efbfcc0f43e46266b96c07dc46` |
| Ubuntu remaining checks on `4371032` | `3421cfeec0c5161cee5ffa7b0aab163054ff471f7ea1396f0549b014ff8332c8` |

### Subsequent corpus, calibration and recovery batch

Commit `6d13f07a278cae292267ca2965f181eb7befa5e0` passed the full combined
matrix on macOS and clean Ubuntu 24.04 arm64: 3,413 workbench tests and six
study tests on each OS, structure, Ruff, mypy, and both wheel installation
smokes. The single pytest warning came from the deliberate duplicate-entry
archive security fixture; it was not a failed check. The frozen checkout is
the private sibling `execution-host-v4`. This batch does not change the
already running acquisition's execution revision.

The changes retain incomplete metadata manifestations for screening, bind the
full protocol as searchable context with an exact compact inline projection,
and permit title/abstract calibration from original API evidence. These new
calibration and agent drafts do not supply human reference decisions or approve
a model. Acquisition successors can reuse complete searches only after
reproducing their predecessor receipt; incomplete searches restart under a new
run ID with the same approved protocol and bounded budgets. Independent source
integrity review and 26 focused successor tests passed before integration.

| Full combined matrix | Log SHA-256 |
| --- | --- |
| macOS `just quality`, exit 0 | `be1cf0ffc0bf84c4855aefabd301821e8112421c024a26ba19d4d4a77d6906ee` |
| Ubuntu equivalent matrix, exit 0 | `be2ecf65f97a7aa6c63f2b30ee24d3dcdfecea9de5ae795b2f036d17eb8b1a78` |

## Recorded state at dispatch

Acquisition is running. The first arXiv identifier requests returned recorded
transient failures. The retained failure envelope does not distinguish an HTTP
5xx/429 response from a transport error, so no specific provider outage cause
is asserted. Exhausted retries remain incomplete searches, not negative
scientific results. Native execution advances to subsequent registered searches.

At 2026-09-12 03:35:28 UTC, after the initial arXiv identifier phase had
finished, one separate diagnostic requested the exact URL of
`metadata.arxiv.id.0001` through the native source fetcher. It returned HTTP
429 without a `Retry-After` header. The 14-byte response has SHA-256
`467622e2f17f01d302d6c790b13078569f17d71cd83910558535019a594e07c1`;
the snapshot and diagnostic metadata are retained in the private sibling
directory `arxiv-diagnostic-1`. This establishes the response to that diagnostic
only, not the cause of every earlier failure. It is not an acquired protocol
page and does not contribute to the corpus. No further diagnostic request was
sent. Crossref collection continued independently.

After terminal acquisition, read-only replay precedes lossless preparation and
typed deduplication. Any unresolved work-identity queue remains visible for
adjudication. Real human calibration references, screening audits, full-text
eligibility, extraction validation and scientific acceptance are not supplied
by this authorization or by a successful engineering gate. No canonical eligible
study count, saturation claim, or completed systematic review is asserted here.
