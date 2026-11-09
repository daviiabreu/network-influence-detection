# Executed development evaluation and extractor diagnosis

Date: 2026-09-04. These are public synthetic development cases, not papers,
search results, a complete passing suite, or scientific acceptance. Dedicated
ChatGPT subscription authentication was used with `gpt-5.6-sol`, reasoning
`high`, SDK/runtime `0.147.0`; no API key or Platform billing was used.

## Preserved original run and bounded follow-ups

The original suite at revision `3173c0d208f38d5b56cb790693229512a89bd684`
has canonical SHA-256
`9f535734cd9510a4f4d0045fc3bb7bb839d2ba534ddddb5426cd7bdfc3564c78`.
It completed three cases before the extractor failed. Its original failure
record did not preserve a provider cause; no later diagnosis retroactively
changes that record. Five individual development follow-ups at the same
revision completed without repeating those three cases.

Independent read-only inspection checked all eight retained response hashes
and compared outputs with the original v1 assertions:

| Role | Observed result | Original limited assertions |
| --- | --- | --- |
| adversarial_reviewer | revision required; protocol/provenance/support conflicts | matched |
| evidence_synthesizer | no claims or novelty; explicit limitations | matched; not positive synthesis |
| extraction_verifier | rejected, no verified fields, adjudication required | matched |
| quality_appraiser | no answers, unresolved reproducibility, adjudication | matched |
| screener_a | uncertain, adjudication, incompatible criteria | disagreed with defective `include` oracle |
| screener_b | uncertain, adjudication, incompatible protocol/criteria | disagreed with defective `include` oracle |
| search_strategy_proposer | mark incomplete, approval required, protocol conflict | matched |
| search_strategy_critic | reject, owner action, incompatible protocol | matched |

These are six matches to narrow assertions and two oracle defects, not eight
scientifically validated roles or a combined successful run. All eight responses
passed host reconstruction, which establishes execution integrity, not the
truth or sufficiency of their scientific content.

The public v2 suite introduced by `8c91ef222eac78caaac9777e084490ad118bd1f2`
keeps the task bytes and explicitly classifies the two screening tasks as
protocol-version-conflict regressions. It requires uncertainty and human
adjudication without matching an incidental reason-code phrase. Historical v1
loading retains its original assertions. No old report was rewritten or
reclassified as passing. A version-consistent positive screening case remains
necessary; canonical protocol hashes and raw document-byte hashes have
different meanings and must not be compared interchangeably.

## Artifact integrity

All raw responses, excerpts, receipts and diagnostics remain private, outside
Git. The first three hashes below bind complete `dev.<role>.json` envelopes in
the original run; the other five bind individual `step-result.json` artifacts.

| Role | SHA-256 |
| --- | --- |
| adversarial_reviewer | `332f74793c092564f09975dae9489bf44cde49011f0467ded69ac72bd80b2064` |
| evidence_synthesizer | `867d9f8e8b88cec2b709f1620f2b9e077a634f2194ea68f4995bd0287e425649` |
| extraction_verifier | `1c496d501f204965b6578044ba6cf54662b222dbe5b72087911518469e3b17da` |
| quality_appraiser | `0bd9d522cd0861af0113585fd31f24c063b75a30bdc3fd494da7787669587b3f` |
| screener_a | `d42a3de292a662ea155785de0992f08be03def95293a26a7eeca8cbe71999e7f` |
| screener_b | `e52a663bfc76c37059b692053207f2c08e1ba067f9006a4ef79896d8e329d9c4` |
| search_strategy_proposer | `b098e63a017f9822606e3def3500bf288c120fb3f9d2aa9179662c40906018a7` |
| search_strategy_critic | `3da865cad27e2081a22b666a0ba75605f194fb816e78029c8bb4ff17f69a285a` |

## Extractor failure diagnosis

A follow-up on clean revision `b7b135193fac8ba0ebb0b58f021c5904692946e2`
retained the closed SDK error code `other`, before any completed receipt.
A separately instrumented follow-up on the same revision captured the terminal
provider error privately: HTTP 400, `invalid_request_error`,
`invalid_json_schema`, parameter `text.format.schema`, missing schema type.
The private diagnostic SHA-256 is
`e6ac8c614600bfd9199176812a00ba2b2614f9b4ab79af8d12da30ed2bec0785`.
Only that bounded diagnostic exposed provider prose; ordinary exceptions and
public CLI output continue to retain only closed error codes.

Offline inspection reproduces the invalid generation schema: the canonical
`ExtractionResult` contains arbitrary `JsonValue`, rendered as the unconstrained
empty definition `$defs.JsonValue = {}`. This is a request/interface failure,
not evidence that a model extracted a paper incorrectly, and not proof that
earlier discarded provider failures had the same cause. The planned repair
uses a model-only JSON-string transport with strict host decoding while leaving
the scientific `ExtractionResult` contract intact. A new completed extraction
must be recorded separately; none is presumed here.

## Codec correction and separately completed successor

Correction `399093153b640662ae1cfeee55923c3b07d5123a` introduces the
model-only `ExtractionDraftOutput` with bounded `value_json` strings and strict
host decoding. Duplicate keys, malformed JSON, non-finite numbers and excessive
size/depth are rejected. Explicit generation-schema binding distinguishes the
transport from historical canonical outputs; scientific strings are never
silently reinterpreted. The canonical `ExtractionResult` schema is unchanged.
TDD and the provider diagnostic kept this repair at the failed transport boundary.
The generation schema SHA-256 is
`999671125e4da6bdacf4bbf54aed0388afa0d183facdad451ee93ecff767899a`.

The first successor on that exact revision stopped before model execution when
the runtime could not prove subscription authentication. It retained no invented
receipt. A separate read-only subscription preflight then passed: ChatGPT Pro,
SDK/runtime `0.147.0`. No credential was changed or device login attempted.

A new successor directory on the same clean correction revision completed the
actual extractor turn and host reconstruction. Its output had `values=[]` and
`unresolved_fields=["model_family", "validation_method"]`, satisfying the
case's limited uncertainty assertions without inventing support. Its canonical
output schema SHA-256 remains
`edf5c98b104cc472e8928afca123fb7ea245930cd97c1ec9016fcefc15235953`.
Retained StepResult SHA-256:
`c5b0ee2221c0c95bfd5ad122217c0e9bdb46101040d8b623e8f6d3db5c247212`.
Retained raw receipt file SHA-256:
`f86ce0c1cfa264648f21905f47c9b27d7de496a99cd752427d87b5daf433f0c4`.

All nine roles now have separately retained completed development responses,
across different runs/revisions. They must not be presented as one passing
nine-role suite. This missing-evidence case proves successful transport and
bounded uncertainty behavior, not positive extraction fidelity on real papers.

Integrated revision `b0dbb51b8d77df7edae763df3ef1578446e8aaea` passed
`just quality` on macOS: 1,955 workbench tests in 193.67s, six study tests,
structure, shell, Ruff, mypy (141 workbench/script and seven study files), both
builds and installed-wheel smokes. The equivalent clean Ubuntu 24.04 aarch64
matrix passed 1,955 workbench tests in 38.46s and six study tests in 0.01s,
with all other checks and both wheel smokes passing. Both had only the
intentional duplicate-entry hostile-archive warning. Image/recipe match the
venue promotion run record. No 100-percent coverage quota was imposed.
