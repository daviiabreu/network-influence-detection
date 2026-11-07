# Engineering validation

Use focused checks while editing and run the independent integration matrix
once for a completed implementation batch. Repeat a failed or affected check
after a repair; broaden only for a new change or unresolved concern. There is
no global coverage threshold. Never suppress a valid regression to claim a
successful delivery.

| Gate | Command | Scope |
| --- | --- | --- |
| Install | `just sync` | Study lockfile and development tools |
| Structure | `just structure` | Study metadata, imports and active documentation |
| Lint | `just lint` | Study and its small maintenance scripts |
| Types | `just typecheck` | Scientific source/tests and selected packaging tools |
| Hermetic tests | `just test` | Synthetic fixtures, reduced scientific invariants and packaging behavior |
| Build and smoke | `just build` | Wheel installed in a disposable environment; imports outside checkout |
| Integrated matrix | `just quality` | Structure, lint, types, hermetic tests, build and smoke |

`just test` uses an isolated temporary home and cache. Large experiments and
retained real output replay are not engineering tests. The default pytest
collection excludes the retained fragmentation replay before importing it.
Three existing tests are deselected with explicit `external_state` or
`external_toolchain` markers: the installed coordination-automation check and
the two event-chain cases requiring a local Springer template. Synthetic
sealing fixtures exercise temporary files; they do not read real sealed runs.

Historical orchestration tests use explicit phase clocks through fixtures:
synthetic confirmatory execution precedes its frozen close and exploratory
records precede their frozen window. Release and closure assertions still use
their declared instants or synthetic release records. The process-supervision
case marked `real_clock` retains actual elapsed time. No scientific deadline,
seed, result or implementation is changed by these fixtures.

Direct pytest has the same external-gate selection. An operator may explicitly
pass `--run-external-gates` only under the owning protocol and after checking
the required data/tool licences and authorization. `scientific_replay` marks
the retained fragmentation case when opted in. External gates are not run by
CI, `just quality` or this extraction. A deselected test is not a passing gate.
Bitwise pins defined on the original macOS arm64 host keep their existing
platform skips on other hosts; report those skips separately.

Historical framework/IC contracts and private governance remain only in the
private preservation archive, outside this public compendium. They require the
original monorepo revision, corresponding framework, Git history, signatures
and external inputs. Their original contracts must not be weakened to fit the
new repository. The independent test matrix is not the original-monorepo suite.

For prose or path changes, inspect the diff and affected links/hashes. For code
changes, exercise the affected behavior and relevant lint/types. Scientific
implementation checks should cover analytical cases, baselines, numerical
stability, seeds and sensitivity. A technical pass does not establish
scientific acceptance, research-owner authorization, data access or permission
to submit a publication. Keep current engineering receipts distinct from
historical scientific receipts.

The Ubuntu workflow runs this same independent matrix. Account-side runner
failures are not code test results; record hosted CI as unavailable until its
actual result exists. Editorial PDF compilation and kit generation are
separate optional toolchain gates, described in
[`../publication-toolchain.md`](../publication-toolchain.md).
