# Literature review

The systematic review is split by scientific responsibility:

- `protocol/`: reviewed methods and dated amendments;
- `searches/`: exact queries, engines, dates, exports, and result hashes;
- `search-design/`: frozen diagnostic queries and seed-development evidence;
- `screening/`: deduplication and inclusion decisions;
- `corpus/`: canonical work and manifestation records;
- `extractions/`: structured facts and quality appraisal;
- `synthesis/`: evidence tables, gap map, and supported conclusions.

Raw or restricted article bytes remain outside Git. Their manifests preserve
identity, access status, licence, source, and content hash.

`READINESS.md` is the operational handoff: it records protocol versions,
executed searches, implemented controls and remaining scientific gates.
The independent repository audit is recorded in
`docs/research/systematic-review-live-readiness-audit-2026-09-03.md`.

The initial product is a systematic mapping study. The current broad execution
uses the [v3 protocol](protocol/opinion-dynamics-systematic-map-v3.json), its
[readable amendment](protocol/opinion-dynamics-systematic-map-v3-review.md) and
[separate approval](protocol/approvals/opinion-dynamics-systematic-map-v3-20260911.toml).
The [new acquisition record](run-records/2026-09-11-broad-acquisition-v3.md) binds
60 thematic searches and 967 identifier lookups to the cutoff 2026-09-11.
The [coverage audit](search-design/2026-09-11-coverage/README.md) records three
reference graphs and a separately frozen 64-work diagnostic. It does not claim
that search coverage or scientific screening is complete.

The [exploratory area map](search-design/2026-09-12-area-map/README.md) explains
11 model families and comparison axes using 14 sources, with mechanisms,
observables and examples of empirical validation. Its exact query mapping and
dated execution snapshot distinguish planned coverage from acquired evidence.
It is orientation before screening, not a synthesis of included studies.
The [supplementary reference checks](search-design/2026-09-12-area-map/reference-exceptions.md)
retain two malformed-link identity leads, the Zenodo access limit, and the
ESS dataset DOI that returned no Crossref match, without changing the run.
The [editorial metadata check](search-design/2026-09-12-area-map/missing-title-evidence.md)
documents seven observations from the interrupted prefix lacking a titled
companion, including verified titles, explicitly untitled reviews and an access limit. It supplies separate
resolution evidence without amending the acquired observations or eligibility.
The [final preparation diagnostic](searches/2026-09-12-v3-preparation-diagnostic.json)
records all 54,570 observations, including ten without a title and nine without
a directly linked titled companion. The native corpus stage stopped before
producing a deduplication result. Its [64-work comparison](searches/2026-09-12-v3-challenge-64-results.json)
is a post-expansion coverage regression, not independent recall.
The [corpus-metadata successor](run-records/2026-09-12-corpus-metadata-successor.md)
subsequently retained every observation in 46,400 proposed works and a complete
metadata/identity review queue. Its receipt remains incomplete; scientific
adjudication, calibration and screening readiness are still pending.

The historical v2 JSON protocol retains
`review_candidate` in the immutable subject; its
[separate approval](protocol/approvals/opinion-dynamics-systematic-map-v2-20260909.toml)
authorizes search execution. It has a [readable review brief](protocol/opinion-dynamics-systematic-map-v2-review.md)
and [measured query-development matrix](search-design/2026-09-07/results.md).
OpenAlex, arXiv and DBLP provide discovery; Crossref supplies identifier recovery.
Controlled publisher exports and real human calibration remain pending. See
`docs/process/systematic-review.md` for the gate sequence and the explicit
limits on agent reviewers and Google Scholar.

The prioritized v5.1 map closed on 2026-09-28 with 4,056 mapped primary works:
see its [production record](run-records/2026-09-28-broad-map-v5-1-production.md)
and [aggregate outputs](synthesis/map-v5-1-2026-09-28/README.md). Conditions 1
and 2 of the stopping rule held at batches 13 and 14; the random-remainder audit
stayed incomplete because 101 of 400 sampled records lack abstracts. The IC theme
decision that used this map is in
[`research/decisions`](../decisions/2026-09-28-theme-decision.md).
