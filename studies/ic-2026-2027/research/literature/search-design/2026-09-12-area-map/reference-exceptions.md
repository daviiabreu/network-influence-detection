# Supplementary reference-identity checks

Checked on 2026-09-12 while the frozen v3 acquisition was running. These
checks do not amend its registered queries, add acquired observations, or
classify a reference as an eligible study. The original
[unresolved-link ledger](../2026-09-11-coverage/starnini-unresolved-reference-links.json)
remains unchanged.

Two Starnini reference links contain the DOI resolver prefix twice. A
primary-publisher search result independently binds each candidate DOI to a
title and publication metadata:

| Original reference | Candidate DOI | Publisher metadata match |
| --- | --- | --- |
| `bib.bib138` | `10.1016/j.physa.2006.06.018` | [Cascade dynamics of complex propagation](https://www.sciencedirect.com/science/article/abs/pii/S0378437106007679), Physica A, volume 374, issue 1, pages 449–456, January 2007 |
| `bib.bib492` | `10.1016/j.chaos.2025.116153` | [Complete aging in the noisy voter model enhances consensus formation](https://www.sciencedirect.com/science/article/abs/pii/S0960077925001663), Chaos, Solitons & Fractals, volume 194, article 116153, May 2025 |

The evidence is the search service's indexed projection of the publisher
pages, reported as crawled three months earlier. It is not an original HTTP
response, a Crossref deposit, a full-text reading, or a current-access claim.
The exact projection is retained privately as
`reference-exceptions-primary-search.txt` under the broad-research runtime;
its SHA-256 is
`9f4377fc722a5d5d014090505cff3206cd774f3e0a3e557991583a3770712f9f`.
The two DOI-resolver opens failed at the web tool's safe-open boundary and
were not retried. The publisher search used the two exact DOI strings and
was restricted to `sciencedirect.com`.

The separate Zenodo reference `bib.bib44`, DOI `10.5281/zenodo.13787981`,
remains unresolved in this check: the
[official record page](https://zenodo.org/records/13787981) returned HTTP 429.
No retry or alternative access route was attempted. The bibliographic DOI
alone does not establish the record's type, content, or eligibility.

All three identifiers were checked against the frozen v3 exact-query list
and are absent. The two publisher matches are supplementary identity leads
for a later registered continuation or manual reconciliation; they are not
silently inserted into the active run. Their original reference edges and
the acquisition's coverage denominator retain their recorded meanings.

## Registered DOI with an empty Crossref result

The active run's `metadata.crossref.doi.0883` query for
`10.21338/ess11e02_0` returned an exhausted first page at
2026-09-12 04:12:57 UTC. Its original 187-byte JSON response, SHA-256
`6ec0a900b362c5149fd8a58cf16525b414923941dd1284fb1f8083a4e7d54c97`,
reports `total-results: 0` and an empty `items` list. This is a completed
provider query with no metadata match, not evidence that the DOI or source
does not exist.

The [European Social Survey's own citation guidance](https://www.europeansocialsurvey.org/contact/disclaimer)
associates the exact DOI with its round 11 integrated dataset, edition 2.0.
This supports a dataset identity lead; it does not adjudicate the reference's
role in the review. The primary-page search projection was reported as
crawled 1.2 years earlier and is retained privately as
`ess-unmatched-doi-primary-search.txt`, SHA-256
`fd6c95ad960b9e28418d58a8e069de779fc9542c0e9575e7b9f3d7ab09fe992d`.
Direct opening of that guidance returned 502; a DOI registration-agency
lookup failed at the web tool's safe-open boundary. Neither response
establishes the registration agency, so the reason for Crossref's empty
match remains unassigned. No dataset was downloaded or added to the corpus.
