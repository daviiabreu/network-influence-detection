# Scientific tests

The suite exercises the scientific package through deterministic local cases,
analytical expectations, reduced integrations and synthetic evidence fixtures.
Large stochastic experiments and replay of retained real outputs are separate
scientific gates.

Run `just test` from the repository root for the hermetic suite, or pass pytest
paths and selectors to that recipe. Its temporary home and caches keep the
suite independent of the original research installation. External-state and
editorial-template cases are explicitly deselected; the real fragmentation
replay is excluded before collection. Historical phase clocks are scoped to
the eight orchestration test files that need them, with real elapsed time kept
for the process-supervision case.

The [validation policy](../../../docs/process/engineering-validation.md)
describes the independent matrix, external markers and scientific limits.
The existing platform-specific bitwise pins remain defined on the frozen
macOS arm64 host. A technical test result does not establish research-owner
approval or acceptance of a scientific claim.
