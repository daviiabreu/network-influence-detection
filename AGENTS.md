# IC study repository instructions

Read `docs/architecture.md` before changing ownership or persisted artifacts.
Follow `studies/ic-2026-2027/AGENTS.md` for scientific work and read the relevant
phase protocol before producing or validating scientific evidence.

- This repository owns the IC compendium and its independently locked Python
  package. It contains no orchestration framework, provider runtime or sibling
  repository dependency.
- Preserve `studies/ic-2026-2027/` paths. Frozen code, specifications, protocol
  bytes, seeds, results and completed records retain their original identity.
  Corrections create linked successors rather than overwrite evidence.
- Raw/restricted inputs, sealed runs, private coordination, credentials and
  private holdouts stay outside Git and outside routine engineering checks.
- The original monorepo history is provenance, not the new repository's history.
  Do not rebind historical signatures or frozen hashes to the extraction.
- Run focused checks while editing and `just quality` once at integration.
  Report the hermetic gate separately from external and scientific gates.
- Never infer publication rights from a tracked path or a private remote. Apply
  the scope in `docs/publication-selection.md` before public release.
