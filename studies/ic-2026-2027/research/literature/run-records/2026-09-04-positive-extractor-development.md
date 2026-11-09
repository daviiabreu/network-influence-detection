# Positive extractor development execution

Recorded on 2026-09-04. This is one public synthetic calibration case, separate
from the [complete nine-role v2 run](2026-09-04-complete-development-v2.md).
It is not a scholarly article, systematic search, included work, PRISMA count,
unseen holdout, model promotion, or scientific acceptance.

## Fixed configuration and evidence

The evaluated clean revision is
`26efebe785e32fda6b7c2c05cc9cfa71cec71a6a`, based on
`9bcff977ae3c0afe170274bc380be1b72023cf38`. The additional task is
`workbench/src/research_workbench/workflows/systematic_review/evals/live-dev/positive-extractor-v1/task.json`.
Its companion README records inspection criteria outside the candidate input;
its HTML source was authored solely for this calibration. Historical tasks and
the v2 suite are unchanged.

The task binds canonical protocol SHA-256
`f3560b0e8507816fa2932b8b316d54cac05af5b62b128bf2308a7a8139f0d2f7`
and the existing `model_family` / `validation_method` field IDs. The unchanged
extractor context supplies those exact protocol contents; the raw document
SHA-256 is
`a47dc65f6011626a4ec6f82d178bdf27f10fb020661c1310f9eb5d342aa1b08b`.
The canonical and raw hashes identify different encodings, not a version
conflict. The protocol remains `review_candidate` without approval.

Existing host HTML ingestion and evidence resolution reproduce both locators
under that protocol's full-text policy. Original HTML SHA-256:
`139dfa297cc407d6126d7082156805b4fc5f4f1567cfeed816ee4d99e4ec48cb`.
Projection SHA-256:
`2bfdcc7dc47da4f0b524445335e7217e1f704f640c8bea3cc5e32acb09b8cc4d`.
The permitted locators are logical page 1, lines 2 and 3, respectively. No
network acquisition, article lookup, or restricted source bytes were used.

No prompt, model, schema, manifest, registry, approval, or protocol was changed.
The unchanged generation schema remains
`999671125e4da6bdacf4bbf54aed0388afa0d183facdad451ee93ecff767899a`;
the canonical output schema remains
`edf5c98b104cc472e8928afca123fb7ea245930cd97c1ec9016fcefc15235953`.

## Actual single-candidate result

The existing `agent eval-candidate` command executed exactly one turn using
`codex-subscription/gpt-5.6-sol`, reasoning `high`, dedicated ChatGPT Pro
authentication, and SDK/runtime `0.147.0`. The preflight and completed receipt
agree. No API key, Platform billing, default Codex authentication, web tool,
or holdout was used. Reported usage: 15,373 input and 579 output tokens.

The decoded canonical result contains two nonempty scalar strings:

| Field | Actual canonical value | Status and evidence |
| --- | --- | --- |
| `model_family` | `Deffuant-Weisbuch bounded-confidence model` | `observed`; exact supplied line 2 locator |
| `validation_method` | `conservation-of-mean analytical check` | `observed`; exact supplied line 3 locator |

`unresolved_fields=[]`. Both meanings are explicitly stated in the respective
synthetic excerpts; the output adds no empirical validation result or accuracy
claim. Work, assignment, protocol, source and manifestation bindings match.

## Retained receipt and independent readback

The private CLI envelope is retained in an external owner-only directory with
0700 mode and 0600 files. The following hashes distinguish actual file bytes,
canonical models, context and provider response identity:

| Artifact | SHA-256 |
| --- | --- |
| Task file bytes | `b448ed3dd9d19d65bc557615830b0deab89a15eb3464904d1f1c81971f07619d` |
| Task canonical digest | `f50f87f555b24dc97408f64daf789f293b7b976844d9043b7112d3ef2e18c8f5` |
| Context pack digest | `75a2b801c07ae51855385eed4a0f5234d3cebabbb275a4d4a301a8ee541482da` |
| Reconstructed request | `abdabe80dfc25d0731cd85321be463a4848ca27d4770acb4508938faa2c5ee9b` |
| Provider response digest from receipt | `96124387918d85550d72fbaf094e5bc5f86b02076aaa74cba748bb4c3e4f7ca6` |
| Private CLI envelope file | `26bf0100e9bc78c6670be0f592d4890192ef9862eb1456ad1f077741b00b6145` |
| Canonical StepResult | `b8d371f87950015fb1d112556142da15574ecdd9bf331caae0548f10bd3d6389` |
| Canonical ExtractionResult | `0bb2db8965f4640d0b6758cd8813853e53fd04e47143cfe91eee9b32a59474a0` |
| Private readback report file | `253138a8e138b2e2b91252b4552e8fe84f8058ba8ddf44ba677971cf9da31597` |

A separate zero-model-call inspection reopened the receipt and rebuilt the
request from the exact clean revision using `build_agent_execution_request`.
It checked context/task/request/runtime/schema identities, one-turn/no-tool
execution, canonical `StepResult` and `ExtractionResult` validation, exact
task/output binding, the two actual values, and canonical readback. It passed.

The single-candidate CLI retains the response digest and host-decoded canonical
output, **not the original provider response bytes**. This inspection therefore
does not independently replay raw `value_json` decoding from the live response.
That stronger retention exists in the nine-role executed-evaluation command;
no new CLI or second model call was introduced for this bounded case.

## Focused validation and limits

The added public-interface regression binds the actual extractor context,
canonical protocol, original HTML, reproduced locators, typed JSON transport and
canonical readback. Its synthetic model response uses nonempty JSON arrays;
the actual model returned the faithful scalar strings shown above. Both
transport shapes are supported without changing the scientific values.

The positive case, extraction-codec, generated-output and repository review-spec
tests passed together: **78 passed in 4.97s**. Ruff format/lint passed for the
changed test and mypy reported no issues in that file. No repeated full suite or
Actions run was requested; integration validation belongs to the parent batch.

This closes the specific missing nonempty live-extractor development example.
It does not calibrate positive screening, difficult PDF/table/OCR extraction,
ambiguous evidence, all protocol fields, or general scientific accuracy.
Independent extraction verification, separately controlled holdout evaluation,
signed workflow-specific binding, scientific protocol acceptance and production
composition remain outstanding. All nine review bindings remain drafts.
