# Limits of Detecting Network Influence in Attitude Panels

Code, protocols, experiment records and manuscript sources for the paper
_Limits of Detecting Network Influence in Attitude Panels_ by Davi Abreu da
Silveira and Henrique Mohallem Paiva (Inteli), submitted to the _Journal of
Computational Social Science_.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23418473.svg)](https://doi.org/10.5281/zenodo.23418473)

## The question

Attitude panels such as the Swiss Household Panel ask the same people the same
questions year after year, but they never observe who talks to whom. When
answers stay correlated over long lags, is that a trace of social influence
through an unseen network, or just individual persistence plus measurement
noise? This study asks how strong network influence has to be before the two
explanations can be told apart from panel data alone.

## What we did

We ran a prespecified simulation. Synthetic panels match the size and
refreshment design of the Swiss Household Panel, with an unobserved contact
network and explicit measurement error at a known response reliability _r_. A
fixed classifier compares the panels' long-lag correlations with those of
persistence-only models matched to the same short-term stability. The
protocol, criteria and random seeds were frozen before the confirmatory run.

## What we found

Against a trait-plus-autoregressive persistence model, the classifier first
reached the target AUC of 0.70 when contacts carried 10% of the innovation
variance (_a_ = 0.10) for reliabilities between 0.55 and 0.90, and only at
_a_ = 0.30 for _r_ = 0.50. The prespecified comparison across persistence
models was not interpretable under its own eligibility rules, and we report it
as such.

Labelled exploratory analyses show how fragile that boundary is. A changing
response channel separated panels with no influence at all, while letting the
persistence model fit reliability and one extra lag absorbed most of the
separation. Distinguishing simulated panel distributions is therefore not, by
itself, evidence of social influence in real panels.

## Repository layout

```text
studies/ic-2026-2027/
├── src/ic_study/        scientific package: models, simulation, metrics, analysis
├── experiments/         experiment specifications, frozen protocols and released records
├── research/            research questions, preregistration, amendments, positioning
├── publications/
│   ├── jcss-journal/    current manuscript (LaTeX) and Online Resource 1
│   ├── jcss-manuscript/ earlier rule-assembled manuscript and its review trail
│   └── reproducibility/ release manifest and regeneration scripts
├── validation/          independent re-implementations used to check the results
└── tests/               unit, property, regression and reproduction tests
docs/                    architecture, reproducibility and toolchain guides
scripts/, justfile       repository checks
```

The study keeps its original `studies/ic-2026-2027/` prefix because frozen
manifests and hashes refer to those paths. The main (v4) experiment lives in
[`experiments/exploratory/detection-boundary-v4/`](studies/ic-2026-2027/experiments/exploratory/detection-boundary-v4/)
and its preregistration in
[`research/questions/exploration/2026-09-24-parallel/`](studies/ic-2026-2027/research/questions/exploration/2026-09-24-parallel/).

Many working records (decision memos, experiment notes, review logs) were
written in Portuguese during the project. They are kept unchanged because
their bytes are part of the frozen record; the manuscript, code and entry-point
documentation are in English.

## Running it

You need Python 3.12, [uv](https://docs.astral.sh/uv/), [just](https://just.systems/)
and ShellCheck.

```sh
just sync      # install the locked environment for studies/ic-2026-2027
just quality   # structure, lint, types, hermetic tests and a wheel smoke test
```

The test suite runs on reduced cases and synthetic fixtures; it does not rerun
the full experiments. The empirical reliability anchor also needs the Swiss
Household Panel microdata, which are available from FORS under its own
data-use contract and are not distributed here. To rebuild the manuscript PDF,
see the [publication toolchain guide](docs/publication-toolchain.md).

[Reproducibility and provenance](docs/reproducibility.md) explains what can and
cannot be regenerated from this repository and from the Zenodo archive.

## Data

The [Zenodo archive](https://doi.org/10.5281/zenodo.23418473) holds the frozen
confirmatory code, the released simulation outputs and the rule-assembled
manuscript. Swiss Household Panel microdata, restricted inputs and run state
are not distributed here. The
[public selection notes](docs/publication-selection.md) describe what was left
out and why.

## Licences

The same terms as the Zenodo archive apply:

- Code, data and documentation are under the [MIT License](LICENSE).
- Manuscript texts and figures under `studies/ic-2026-2027/publications/`
  (the LaTeX text files and the figure files with their captions) are under
  [CC BY 4.0](LICENSES/CC-BY-4.0.txt).

Short quotations from third-party sources in the literature and venue records
remain their authors' and are reproduced for citation. The Springer template
and the Swiss Household Panel data are not included and keep their own terms.

## How this was built

The research was carried out with an agent-assisted workflow (protocol-bound
literature mapping, blinded reviews and validation gates) that is maintained
separately and is not needed to install or check this repository. The
manuscript's _AI use_ statement describes the role those tools played.

## Citation

To cite the paper, use: Abreu da Silveira D, Paiva HM. _Limits of Detecting
Network Influence in Attitude Panels_. Manuscript submitted to the Journal of
Computational Social Science, 2026. To cite the code and data:

```bibtex
@misc{abreu2026limits,
  author    = {Abreu da Silveira, Davi and Paiva, Henrique Mohallem},
  title     = {Reproducibility package for ``Limits of Detecting Network
               Influence in Attitude Panels''},
  year      = {2026},
  publisher = {Zenodo},
  version   = {1.0.0},
  doi       = {10.5281/zenodo.23418473}
}
```
