# Adversarial review kit

Use three independent reports on the same frozen manuscript PDF, claim ledger, validated results inventory, and venue checklist. Reviewers should cite page/line, ledger ID and artifact locator. Conceal the other reports until each is complete. This is an internal challenge, not journal peer review or Research Owner ratification. Assess the chosen paper question only after the Owner decides it.

The rubrics derive from [JCSS's criteria for consideration](https://link.springer.com/journal/42001/submission-guidelines) (method and analysis soundness, contribution, clarity and replication detail) and [JASSS's referee prompts](https://www.jasss.org/v02/page_content_includes/_include_submit.html) (overall assessment, editor rationale, constructive feedback, replicability and use of electronic publication). Score each criterion 0 = blocking/unsupported, 1 = major revision, 2 = minor revision, 3 = supported and clear, N/A = inapplicable with reason. A score is a diagnostic, not acceptance. Identify the cheapest decisive check for each major finding.

## Reviewer 1 — computational social science methods and statistics

| Criterion | Questions to test |
| --- | --- |
| Estimand and comparison | Is the question operationally defined? Are nulls, alternatives, observation channel and unit of inference aligned? Are identifiability limits stated? |
| Sampling and measurement | Are panel geometry, synthetic versus observed variables, reliability scenarios, missingness and dependence accounted for? |
| Calibration and validation | Were fitting, model choice and evaluation separated? Are gates prespecified and exposure disclosed? Do failure and censored cells remain visible? |
| Statistical inference | Are paired uncertainty, coverage, multiplicity, interval inversion and sensitivity supported by validation rather than asserted? Are effect sizes and uncertainty shown together? |
| Reproduction | Could the analysis be rerun from exact protocol, code, environment, seeds, input hashes and results manifests? |

## Reviewer 2 — opinion dynamics and ABM

| Criterion | Questions to test |
| --- | --- |
| Mechanism fidelity | Are update rules, network, schedule, bounded confidence, observation and comparator processes explicit and faithful to cited models? |
| ODD completeness | Can a reader reconstruct the model from the seven elements in `odd-2020-template.md`? Are design concepts addressed or marked inapplicable with reasons? |
| Validation | Are micro/macro patterns, baseline and alternative models, parameter calibration, sensitivity and negative results appropriate to the model's purpose? |
| Interpretation | Are simulated mechanism separation and causal claims kept distinct? Is transport from synthetic panels to real social influence justified or limited? |
| Replicability | Does the PDF give enough detail to understand the model without code, and do code/documentation links work for reviewers? |

## Reviewer 3 — skeptical editor

| Criterion | Questions to test |
| --- | --- |
| Contribution | What is the precise new knowledge relative to the closest verified works? Does the coverage of prior art actually support a novelty claim? |
| Significance and fit | Is the contribution of broad interdisciplinary interest for JCSS or a substantive social-simulation advance for JASSS? Is the research question owner-approved? |
| Clarity | Can a cross-disciplinary reader identify the question, design, main result, uncertainty and limits from abstract, figures and discussion? |
| Integrity and venue | Are sources, disclosures, data/code access, ethics, references, figures, supplement and word limits compliant with the chosen venue? |
| Decision | Would the present evidence justify external review? Name exact blockers, not an optimistic acceptance forecast. |

For JASSS, verify the current submission instructions before applying venue-specific scores. Its [official instructions](https://www.jasss.org/v02/page_content_includes/_include_submit.html) recommend ODD and code sharing but do not make ODD mandatory. The 2020 ODD template is this project's chosen documentation standard.
