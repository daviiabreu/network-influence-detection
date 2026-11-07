# Architecture

This repository owns one scientific study. The extracted compendium remains at
`studies/ic-2026-2027/` because frozen manifests and publication tooling use that
prefix. Moving it would change artifact identities without improving its
independent installation.

| Path | Ownership |
| --- | --- |
| `studies/ic-2026-2027/src/ic_study/` | Scientific implementation |
| `studies/ic-2026-2027/experiments/` | Experiment specifications and retained records |
| `studies/ic-2026-2027/research/` | Scientific protocols, evidence and decisions |
| `studies/ic-2026-2027/publications/` | Current and historical publication sources |
| `studies/ic-2026-2027/tests/` | Scientific and packaging verification |
| `docs/` | Study maintenance, selected evidence and provenance guidance |
| `scripts/`, `justfile`, `.github/` | Study-only engineering gates |

There is no root Python project, uv workspace, workbench package, model runtime
or live workflow controller. `ic_study` installs from its own locked project.
Its scientific modules own models, simulation, metrics, analysis and validation;
experiment parameters remain outside the package. Notebooks call the package.

The external workflow framework may produce versioned files accepted by the
study protocol. That file interface is the seam: no Python import or relative
path to another repository is required. Historical agent bindings and private
governance remain only in the private preservation archive.

The maintainer interface is `just quality`. It hides environment setup, safe
test selection and wheel installation behind a small set of recipes. Editorial
build and package commands share one toolchain configuration module rather
than embed host-specific executable and cache locations in each caller.

Restricted raw bytes and completed external runs remain outside Git. Canonical
records preserve provenance; derived indexes and scratch builds are disposable.
An engineering pass does not authorize scientific execution or acceptance.
