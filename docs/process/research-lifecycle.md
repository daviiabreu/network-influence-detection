# Research lifecycle

This is the authoritative phase map. Detailed protocols are added and reviewed
inside the owning study before any phase executes.

```text
charter
  -> venue landscape
  -> review protocol
  -> reproducible search
  -> screening and extraction
  -> synthesis and gap map
  -> research question
  -> exploratory experiments
  -> registered validation
  -> robustness and reproduction
  -> publication package
```

Every transition requires explicit inputs, outputs, evidence, decision rules,
and a completion gate. A later phase may expose a problem in an earlier one;
the correction creates a new version with lineage rather than rewriting the
prior record.

Engineering checks follow [risk-based validation](engineering-validation.md):
focused checks during editing, one integration gate per implementation batch,
and independent work in parallel. Global 100-percent code coverage is not a
research-phase gate. Scientific acceptance still requires the evidence specified
by the owning protocol.

Research Owner authorization has no mandatory phrase. When the pending action
and its boundaries were already presented, an unambiguous instruction such as
“pode rodar”, “continue”, or “aprovado” is sufficient. The agent converts that
instruction into the dated, hash-bound repository record; it must not ask Davi
to reproduce hashes or boilerplate. Technical gates and scope boundaries remain
unchanged, and genuinely ambiguous or materially different actions still
require clarification.

An instruction to continue an already bounded workflow is standing operational
authorization for its remaining reversible transitions, including repairs,
re-evaluation, promotion, local execution, replay, and preparation of the next
declared phase. The agent records each transition only after its objective gates
pass and cites the owner's plain-language instruction as the authorization
basis; it does not imply that Davi manually inspected an artifact he was not
shown. Do not interrupt the workflow for repeated approval wording. Ask again
only for a material scientific choice, a scope/model/credential change not
already authorized, an irreversible or externally consequential action, or an
interaction only the owner can perform.
