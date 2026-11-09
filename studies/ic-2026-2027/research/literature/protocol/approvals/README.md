# Protocol approvals

The v3 acquisition approval and its v4/v5 successors are recorded here.
Authorization follows the standing rules in
`../../../../../../docs/process/research-lifecycle.md`. The v5 editorial
approval allows the documented bibliographic-identification policy; it does
not adopt individual metadata choices or authorize a new acquisition.

An approval is created only after the material protocol and acquisition scope
have been presented to Davi and he has authorized them unambiguously. The agent,
not Davi, computes and records the protocol path, id, semantic version,
canonical SHA-256, Git commit, aware timestamp, authorization
`systematic_review_search_execution`, and exactly one `research_owner` approver
using the `SystematicReviewProtocolApproval` contract.

The absence of an approval TOML is a fail-closed gate, not a missing
placeholder. Venue readiness approvals do not authorize literature acquisition.
