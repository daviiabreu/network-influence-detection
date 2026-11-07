# IC Study

The study context owns the scientific record from discovery through experiment
and publication.

## Governance

**Research Owner**:
Davi Abreu da Silveira, the sole human authority who approves readiness gates,
adjudicates blocking conflicts, authorizes agent promotion, and accepts
canonical research artifacts.
_Avoid_: Advisor approval, agent approval

**Agent Review Evidence**:
A hash-bound analysis produced by an agent in a declared role and isolated
context. It may satisfy a review requirement but never constitutes a Governance
Approval.
_Avoid_: Approval, independent human review

**Governance Approval**:
A dated, hash-bound record generated from an unambiguous Research Owner
authorization over one exact Git revision and declared scope. The owner need not
repeat hashes or fixed wording; the repository record supplies that structure.
_Avoid_: Agent consensus, informal confirmation

**Role-Separated Holdout**:
An unseen evaluation suite whose `holdout_author`, `candidate_evaluator`, and
`holdout_verifier` use distinct identities and isolated contexts. This is
procedural separation, not a claim of external institutional independence.
_Avoid_: External holdout, independent-person holdout

## Literature

**Scholarly Work**:
The intellectual contribution shared by all of its published forms.
_Avoid_: Paper, record

**Manifestation**:
A specific retrievable form of a Scholarly Work, such as a preprint, conference
version, journal extension, correction, or retraction notice.
_Avoid_: Duplicate paper, version row

**Search Snapshot**:
An immutable result bundle produced by one exact query, source, filter set, and
retrieval time.
_Avoid_: Search results, corpus

**Screening Decision**:
A protocol-bound inclusion or exclusion judgment with reviewer and reason.
_Avoid_: Label

**Extraction**:
A source-located structured observation from one Manifestation.
_Avoid_: Summary, note

**Synthesis**:
A reasoned view derived from accepted Extractions, including conflicts and
uncertainty.
_Avoid_: Literature dump

## Venues

**Publication Venue**:
The stable conference or journal identity across time.
_Avoid_: Conference edition, call for papers

**Venue Edition**:
One dated occurrence or volume of a Publication Venue.
_Avoid_: Venue

**Policy Snapshot**:
Dated evidence of a Venue Edition's rules, deadlines, participation mode, and
submission requirements.
_Avoid_: Venue policy

## Experiments and publication

**Research Question**:
A falsifiable scientific question selected from the accepted synthesis and
feasibility evidence.
_Avoid_: Topic, idea

**Experiment Spec**:
A versioned declaration of purpose, inputs, parameters, outcomes, and stopping
rules.
_Avoid_: Script, run

**Run Manifest**:
The immutable identity and provenance of one executed Experiment Spec.
_Avoid_: Results folder, log

**Claim-Evidence Map**:
The explicit relationship between manuscript claims and the accepted evidence
that supports, limits, or contradicts them.
_Avoid_: Bibliography, citations list
