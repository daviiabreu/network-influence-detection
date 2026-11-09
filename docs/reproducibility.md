# Reproducibility and provenance

This repository is an extraction of the study compendium under
`studies/ic-2026-2027/`, taken at commit `cbf7d721` of the private
`research-workbench` history. It starts its own maintenance history. Historical
commits, signatures, approvals and hashes still identify their original
objects; they were not re-signed or turned into evidence about this repository.

Study paths were kept unchanged so that protocols, specifications, frozen
records and manuscript sources keep their identifiers. The
[extraction map](../provenance/origin-map.json) lists the selected, omitted and
adapted files. Checks that depend on old Git objects still need the private
copy of the original history.

## What you can reproduce without external data

Running `uv sync --locked --group dev` in `studies/ic-2026-2027/` installs the
scientific package with Python 3.12. `just quality` checks structure, lint,
types, hermetic tests on reduced cases and synthetic fixtures, and installation
of the wheel outside the checkout. These commands do not run agent workflows,
model providers, full experiments or a replay of the real results.

The sources in `publications/jcss-journal/` can be compiled and checked with an
external editorial toolchain described in the
[toolchain guide](publication-toolchain.md). Compiling and packaging verify the
editorial deliverable; they do not redo the analysis behind the published
numbers.

The [Zenodo archive](https://doi.org/10.5281/zenodo.23418473) contains the
frozen confirmatory code and the released simulation outputs. Its scripts
regenerate every result table and figure of the article except the exploratory
summary table, whose values are transcribed from archived records. The exact
scope is documented in Online Resource 1 of the manuscript.

## What stays external

Swiss Household Panel microdata require their own access agreement and
licence. Raw, interim and processed data, restricted content, private holdouts,
sealed runs, credentials and private coordination are not distributed. The
manifests and hashes recorded in the study state the expected identity of those
bytes; they do not grant access to them and do not show that a replay was run
during the extraction.

Paths under `.local/state/research-workbench/` and Nix store paths cited in
frozen sources describe the original environment. They are not dependencies of
the wheel. Older scientific code still accepts explicit inputs where its
interfaces offer them; future portability changes should preserve frozen
sources or create a documented successor.

IC-specific coordinators and runtime contracts, private approvals and agent
histories remain only in the private preservation of the original monorepo.
They are not dependencies of this compendium. Reproducing them requires the
original checkout, the matching framework version and the original inputs and
authorizations; none of that was run during the extraction.

## Evidence and licences

Results and numerical claims remain bound to the historical sources and
receipts referenced by the publications. A current engineering check does not
replace the scientific gates, a data licence, an ethics decision or a
submission approval. A new run must produce its own manifest with code,
environment, inputs, parameters, seeds and validation state.

This repository is licensed like the Zenodo archive (see the
[README](../README.md#licences)). Those licences do not cover third-party
texts, Springer templates, Swiss Household Panel data or source snapshots. See
the [public selection notes](publication-selection.md).
