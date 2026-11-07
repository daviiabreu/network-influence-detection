# ODD model description template (2020 second update)

Use this when the chosen paper contains an agent-based or individual-based simulation. Fill the complete description before writing a shorter paper summary. The seven numbered elements and their grouping follow [Grimm et al. (2020), JASSS 23(2), article 7, DOI 10.18564/jasss.4259](https://www.jasss.org/23/2/7.html). The [JASSS submission instructions](https://www.jasss.org/v02/page_content_includes/_include_submit.html) recommend ODD but explicitly do not require it; they still point to the older 2006 paper. The 2020 update is the chosen standard for this kit.

**Model name/version:** [ ]  **Code revision and release:** [ ]  **Protocol/run manifest:** [ ]  **Question and validity domain:** [ ]

## 1. Purpose and patterns

State the scientific purpose and what the model is meant to explain, predict, or demonstrate. List patterns chosen before analysis as evaluation criteria, their data/source locators and scale. Include patterns the model fails to reproduce; distinguish synthetic design targets from observations.

## 2. Entities, state variables and scales

List each agent, environment and aggregate entity; state variables versus fixed parameters; units, ranges, spatial/network and temporal scales; and what is observed versus latent. For opinion dynamics, specify opinion representation, network and measurement channel.

## 3. Process overview and scheduling

Give an ordered process list or pseudocode: contact selection, opinion update, rewiring, observation, data collection, and stopping. Specify synchronous/asynchronous steps, tie handling, random draws, and when state variables are committed.

## 4. Design concepts

For each concept, explain the implementation and rationale, or state N/A with a reason. The eleven concepts are: basic principles; emergence; adaptation; objectives; learning; prediction; sensing; interaction; stochasticity; collectives; observation. Identify which behavior is imposed and which arises from agent interaction. Record deviations from source models.

## 5. Initialization

Specify population size, initial state and network distributions, parameter values, seed namespaces, burn-in, and how initial conditions differ across experimental arms. State whether initial states are data-based or synthetic.

## 6. Input data

List external time-varying inputs, their sources, licences, preprocessing, hashes and access restrictions. If there are none, say so. Do not confuse experimental parameters or initialization with input data.

## 7. Submodels

Give equations or algorithms for each process, parameters and units, boundary behavior, numerical rules, and testable invariants. Explain calibration separately from the model definition. Provide enough information for conceptual reimplementation without access to code; link exact code and tests for executable reproduction.

## Simulation experiments (outside ODD)

After the model description, state design, comparison arms, outcomes, estimands, calibration/validation split, seeds, repetitions, uncertainty, failure handling and sensitivity analyses. [Grimm et al. (2020)](https://www.jasss.org/23/2/7.html) distinguish the model description from the experiments conducted with it.
