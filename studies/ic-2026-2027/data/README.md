# Data

Scientific bytes are external to Git. `manifests/` will track logical identity,
source, retrieval time, licence and access classification, content hash, size,
schema, and immutable storage locator.

Local `raw/`, `interim/`, and `processed/` directories are ignored. Raw data is
immutable; transformations create new identified artifacts.

The canonical artifact root is not configured. Follow
`../../../docs/artifact-storage.md`; local bytes remain disposable and cannot be
promoted until its durability gate is satisfied.
