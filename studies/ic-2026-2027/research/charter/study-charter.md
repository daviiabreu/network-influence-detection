# Study charter

Status: review candidate pending the research owner's approval record. This
document is not an approval record.

## Administrative context

- Study identifier: `ic-2026-2027`.
- Initial discovery area: opinion dynamics.
- Final research question: selected only after the accepted systematic
  synthesis and gap map.
- Target venue: selected only after the accepted venue landscape.
- Research-owner identity, institutional requirements, working cadence, available
  compute, funding, and final calendar must be recorded before approval.

### Administrative register required for approval

| Constraint | Current value | Owner | Due | Blocks venue discovery? |
| --- | --- | --- | --- | --- |
| Research-owner identity | Davi Abreu da Silveira | research_owner | confirmed at charter review | no |
| Institution, rules, and ethics contact | Inteli; the applicable institutional procedure and ethics contact remain an accepted unknown owned by the research owner | research_owner | before acquiring human-subject or sensitive data, and no later than experiment registration | no |
| Working cadence and internal calendar | No weekly hour cap; quality gates govern progress; complete the research, reproducibility package, and submission-ready paper by 2026-10-31 | research_owner | confirmed at charter approval | no |
| Available local and VPS compute | Local development machine and user-managed VPS are available; exact CPU, memory, GPU, storage, and runtime limits remain an accepted inventory task | research_owner | before question feasibility assessment and experiment registration | no |
| Publication, travel, and registration budget | unknown; cannot justify a discovery exclusion | research_owner | before feasibility exclusions or target selection | no |
| Funding and reimbursement constraints | unknown; cannot justify a discovery exclusion | research_owner | before feasibility exclusions or target selection | no |
| Authorship expectations | Davi owns the research implementation and manuscript; any later coauthor inclusion and order must follow actual contribution and applicable institutional and venue rules | research_owner | reconfirm before submission | no |

The research owner replaces every `unknown` with an explicit value or an accepted
unknown plus an owner and dated resolution plan. This table is part of the
hash-bound charter subject; approval metadata cannot silently supply values
that are absent here.

An unknown administrative constraint is recorded as unknown; it is never filled
by an agent. A newly discovered constraint creates a dated charter amendment and
reopens every dependent decision it can change.

The internal deadline is a planning target, not permission to weaken evidence,
skip validation, or overstate completion. Internal completion means an accepted
research synthesis, selected question, implemented and validated experiments,
reproducible artifacts, and a submission-ready manuscript. Venue submission,
peer-review timing, acceptance, and publication dates remain external outcomes.

## Scientific ambition

The IC should aim at a falsifiable contribution that can survive international
peer review. A publishable outcome needs more than a new implementation: it must
identify a consequential gap, compare against appropriate baselines, expose its
assumptions, and provide evidence strong enough for the claims made.

The previous proposal is a seed for terminology, references, and possible
failure modes. It has no privileged status in question selection and cannot be
used as evidence of novelty.

## Publication preferences

Venue discovery scores scientific fit with the initial discovery area. Suitability
for the eventual article is assessed after its question, method, and contribution
are defined; those open choices do not cap the current area-fit score.

International publication is the primary venue objective. Author participation
scores 2–5 on the venue protocol's scale are desired, with higher scores
preferred. A fully online author path has the maximum logistical preference.
Strong ACM and IEEE venues, and ICML when scientifically appropriate, must be
investigated rather than assumed to fit.

These are ranking inputs, not hard discovery filters. Scientific fit, review
quality, eligibility, deadlines, fees, publication format, indexing, travel
requirements, and participation mode remain separate criteria. The venue
landscape must surface a materially better counterexample even when it does not
match the initial publisher preferences.

## Research lifecycle

The study follows the versioned lifecycle in
[`../../../../docs/process/research-lifecycle.md`](../../../../docs/process/research-lifecycle.md).
Each phase has an approved protocol, immutable inputs, staged machine outputs,
role-separated validation, an explicit research-owner decision, and a dated completion
gate. Findings may reopen an earlier phase without rewriting its history.

No agent selects the final research question, accepts evidence, changes a
protocol, promotes a record, or approves a publication target. Agents may
propose, extract, challenge, and validate within declared contracts.

## Evidence and reproducibility

- Source-located evidence outranks summaries and agent rationales.
- Search procedures, raw responses, source versions, exclusions, amendments,
  code revisions, environments, parameters, seeds, and validation decisions
  must be recoverable.
- Machine outputs enter append-only staging. Canonical acceptance is a distinct
  deterministic operation with a research-owner gate.
- A replay repeats recorded orchestration. A regeneration calls a model or
  source again and creates a successor run.
- Public release artifacts exclude restricted source bytes, secrets, private
  traces, and reviewer identities required to remain confidential.

## Independent challenge

Every consequential synthesis or recommendation receives an adversarial review
from a context-isolated role. The reviewer receives the candidate artifact,
atomic claims, cited evidence, and approved rubric, but no author rationale,
agent identity, previous rank, hidden chain of thought, or acceptance decision.
Blocking findings require correction or recorded research-owner adjudication. Agreement
between agents is not evidence of correctness.

## Ethics and research integrity

The study must not fabricate sources, citations, observations, or approvals;
circumvent access controls; publish copyrighted full text without permission;
or expose personal, restricted, or secret data to a model. Human-subjects data,
experiments involving people, or sensitive datasets require a separate ethics
determination before acquisition or execution.

Authorship follows actual scholarly contribution and applicable institutional
and venue rules. Agent use, automation, limitations, and material protocol
deviations are disclosed wherever the selected venue or research-integrity
policy requires them.

## Decision rules

A research question can be selected only when the accepted synthesis identifies
a gap with plausible novelty, importance, falsifiability, feasible baselines,
an adequate validation path, and resources compatible with recorded
constraints. A negative result remains valid when it follows a registered,
well-powered design and its claims match the evidence.

A material change in phenomenon, central assumptions, evaluation target, or
required evidence creates a new linked study version. A narrower operational
refinement may be a dated amendment when it preserves the original question and
does not invalidate accepted evidence.

## Approval gate

Approval requires the following material content and scope to be presented to
the research owner:

- administrative ownership, supervision, calendar, working cadence, compute,
  funding, authorship expectations, and institutional constraints;
- acceptance of the scientific ambition, evidence rules, adversarial-review
  requirement, ethics limits, and reopening rules;
- every remaining unknown, its owner, due date, and whether it blocks venue
  discovery.

After an unambiguous authorization, the agent creates the separate hash-bound
approval record under
`research/agents/approvals/`. Editing this file after approval invalidates the
gate and requires a successor approval. The final research question and target
venue are downstream outputs and do not block charter approval.
