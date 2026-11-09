# Systematic mapping protocol

Current subject: [protocol v2](opinion-dynamics-systematic-map-v2.json).
Its immutable JSON retains `review_candidate`; the
[separate owner approval](approvals/opinion-dynamics-systematic-map-v2-20260909.toml)
authorizes search execution, following the
[dated continuation record](../../decisions/2026-09-09-systematic-map-v2-search-authorization.md).
This approval does not establish completed acquisition, human calibration or
scientific acceptance.

Current protocol checkpoint: status `review_candidate`; canonical SHA-256
`540ed755dd2ac4fe979975f737b89075945023f9fb14688e2010a773331f45ed`; 34
searches across 3 sources (`arxiv`, `dblp`, `openalex`).

The [review brief](opinion-dynamics-systematic-map-v2-review.md) and
[query-development matrix](../search-design/2026-09-07/results.md) explain the
search families, translations, volume estimates and diagnostic limits. The
publication cutoff remains 2026-09-07. Crossref is reserved for identifier
recovery; publisher exports and other supplementary routes require their own
registered evidence before integration.

[READINESS](../READINESS.md) records current execution state and scientific
dependencies. The [v1 subject](opinion-dynamics-systematic-map-v1.json) and its
development runs remain historical, unchanged and unapproved. Its four-query
Crossref/DBLP/OpenAlex plan is no longer the active acquisition subject.

Any semantic protocol edit creates a different approval subject and requires
a dated successor with exact hash, Git revision and owner authorization.
Validation and preparation remain network-free checks; only an authorized
acquisition dispatch may collect the registered sources.
