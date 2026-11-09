# Corpus proposals with explicit metadata gaps

Run `opinion-dynamics-map-v3-broad-corpus-20260911-metadata-1` executed from
**2026-09-12 18:29:05 to 18:32:00 UTC**, using clean code revision
`51e45ce5a725d0a9c83eae5d96ea04c070de078c`. The operator exited successfully
after native execution and read-only replay. Its scientific stage disposition
is **`incomplete`**, with metadata resolution, identifier conflicts and identity
adjudication still required. Screening and scientific eligibility were not run.

This successor replays the preparation retained after the
[initial corpus-stage failure](2026-09-11-broad-acquisition-v3.md). It preserves
the approved v3 protocol, repository binding and deduplication algorithm 2.
The repair changes the proposed-work representation: output 3 retains titled
and untitled proposals separately, with the same grouping, membership-derived
IDs and candidate edges. It does not fill absent titles, import editorial notes,
exclude observations or create human decisions. Davi's standing broad execution
instruction and subsequent “continue” authorize this reversible repair.

| Result | Count |
| --- | ---: |
| Preserved source observations | 54,570 |
| Distinct provider-record identities | 49,333 |
| Proposed works | 46,400 |
| Titled proposals | 46,391 |
| Untitled proposals / metadata-review candidates | 9 |
| Source observations without title | 10 |
| Identity candidates at record-pair level | 20,964 |
| Distinct proposed-work pairs in those candidates | 10,754 |
| Connected components of candidate work pairs | 4,990 |
| Proposed works in those components | 12,025 |
| Proposals with unresolved identifier conflicts | 10 |

Every observation occurs in exactly one proposal. One titleless observation
belongs to a proposal with titled manifestations; the other nine remain
metadata-review candidates. The component counts are a view of the candidate
graph, not merge decisions, confirmed duplicates or a count of required human
actions. The proposed-work total is not an accepted count of unique papers.

The [public result metadata](../searches/2026-09-12-v3-corpus-proposals.json)
binds these counts to the native receipt, complete deduplication output and
review queue. The [metadata and identifier-conflict inventory](../searches/2026-09-12-v3-corpus-pending-metadata.json)
retains proposed IDs, source-record memberships and raw hashes. Full records,
source responses and the complete candidate queue stay in private storage.
The earlier [ten-observation diagnostic](../searches/2026-09-12-v3-missing-title-records.json)
provides original query, page and rank locations without replacing the native
preparation. The [editorial notes](../search-design/2026-09-12-area-map/missing-title-evidence.md)
and [two-case supplement](../search-design/2026-09-12-area-map/additional-missing-title-evidence.md)
remain separate metadata evidence.

The new schema-2 stage receipt is explicitly incomplete and cannot substitute
for the resolved schema-1 corpus consumed by screening. Its queue contains
proposals for metadata and identity review; it is not an owner-adjudication
receipt. A subsequent recorded transition must resolve the pending evidence
and decisions before a corpus can become ready. Real human calibration,
calibrated screening and audits, full-text eligibility, extraction and synthesis
remain subsequent scientific work, as recorded in [READINESS](../READINESS.md).

Native replay reproduced the complete receipt and both outputs. All **11,804
pre-existing files** under the protected acquisition and preceding corpus roots
retained their hashes, sizes, modification times and modes. Exactly six new
content-addressed files were added to the shared CAS. Replay and the subsequent
diagnostic did not alter their protected inventories. The original acquisition,
preparation, interrupted runs and failed corpus stage remain intact.

| Evidence | SHA-256 |
| --- | --- |
| Acquisition receipt | `5aa52db3b98487a17a5c50d246c23e4c97d611a4a1c6c589119c2cf8d29bc675` |
| Previous preparation receipt | `fa934b8b065880228373d76040527a76fc7cdced9c92ebb69a31891485ccf4fa` |
| New corpus-metadata receipt | `6b16e1cb9954ee505a592121d697fb58c56b444e3c430c8360301625ceb4dd82` |
| Complete deduplication output 3 | `41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53` |
| Complete review queue | `f979fdc89063fe3f38ce63dd828540b2a756cacedf68f9066e9b64275d0b9e41` |
| Private result summary | `e07e53e4484e43026addf46ffd31507440e0300d677f206d54bd965e93c1899c` |
| Reviewed operator | `1eab283614ffbd907ad998adb0019246b086ffd0f19333cbd2ae7499a8129b60` |
| Protected-file baseline | `2b0cc3347f9dc102805f96c508c969740d0de1e27f574ee2d62197245299007f` |
| Read-only replay inventory | `30a482af6215b6c93bedb8399e8ba4d81b79990fe42ee6cff78768c9019c1b1d` |

Before dispatch, the exact execution revision passed the full macOS and Ubuntu
matrices: **3,498 workbench tests and six study tests in each environment**,
seven structure checks, complete lint/type checks and both wheel smokes.
The preceding integration stopped at seven type-check diagnostics in the new
tests; revision `51e45ce5` corrected those tests without changing production
code. Independent review found no actionable defect in the representation,
lineage/replay boundary or private operator. This is engineering evidence,
not hosted-CI success or scientific acceptance.

The macOS log has SHA-256
`cab87f67513a9809727645d6485b2f63c4f84e6ee47f66b96082e47b4c6c4d7b`;
the Ubuntu log has
`4d6409fc6681a2a97221994d1a58dc2604b1c0e3dee1a634c9c3f65a254ada3c`.
The combined private quality record has
`8c0fb7ce57876b1142b90e646743c91be1df247c1453b69f663b8a449281fffc`.
The private runtime is
`/Users/davi/.local/state/research-workbench/broad-research-20260911/corpus-v3-metadata-successor-1/`;
the shared CAS remains under sibling `acquisition-v3/artifacts/`.
