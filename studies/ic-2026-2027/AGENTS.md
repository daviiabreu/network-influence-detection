# IC study agent instructions

Read `../../docs/process/research-lifecycle.md` before changing research state.
Read the protocol inside the relevant `research/` phase before producing or
validating evidence for that phase.

Reusable scientific behavior belongs in `src/ic_study/`; experiment parameters
belong in `experiments/`; notebooks are exploratory callers. A claim may use an
output only when its code revision, environment, inputs, parameters, random
seeds, and validation state are recorded.

Preserve raw inputs and completed experiment outputs. Corrections create a
successor linked to the superseded record. Keep restricted bytes outside Git and
track only approved metadata, location, licence, and content hash.

Keep exploratory and registered work distinct. Protocol amendments are dated,
reasoned, and linked to affected evidence.

Read `../../docs/process/engineering-validation.md` before validating a
change: run focused checks for the affected behavior while editing, the
complete matrix once at integration, and repeat or broaden only for a new
change, a failure, or an open question.

A phase is complete when the delivery it was requested for is met, not when
one commit's checks are green; a correction still creates the successor
required above. Replay is not a new model inference.
