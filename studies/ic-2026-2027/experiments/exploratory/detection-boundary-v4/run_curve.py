"""Execute reviewed confirmatory tiers only after every coverage stage has passed."""

from __future__ import annotations

# ruff: noqa: E402 -- BLAS limits must precede NumPy imports.
import os

for variable in ("OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import hashlib
import json
import time
from pathlib import Path

from ic_study.simulation.v4_curve import released_curves, schedule
from ic_study.simulation.v4_gate import (
    aggregate,
    allocation_preflight,
    g0_statuses,
    manifest,
    preflight,
)
from ic_study.simulation.v4_store import DEFAULT_SEALED, SealedStore


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--allocation", type=Path, required=True)
    parser.add_argument("--criteria", type=Path)
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, default=8)
    parser.add_argument("--release-at-close", action="store_true")
    args = parser.parse_args()
    try:
        study = Path(__file__).resolve().parents[3]
        freeze = preflight(args.freeze, study)
        if args.shards != freeze["shards"]:
            raise ValueError("Confirmatory shard count differs from freeze")
        freeze_digest = hashlib.sha256(args.freeze.read_bytes()).hexdigest()
        identifier = hashlib.sha256(
            json.dumps(freeze["code"], sort_keys=True).encode()
        ).hexdigest()
        gate = SealedStore(DEFAULT_SEALED / identifier)
        criteria_bytes = (
            args.criteria or Path(__file__).with_name("criteria-v43.json")
        ).read_bytes()
        criteria = json.loads(criteria_bytes)
        cells = allocation_preflight(
            args.allocation, freeze_digest, g0_statuses(gate), criteria_bytes
        )
        binding = hashlib.sha256(args.allocation.read_bytes()).hexdigest()
        for stage in ("G0", "G1b", "G1c", "G2", "G2c"):
            result = aggregate(
                stage,
                gate.root,
                criteria,
                cells=cells,
                binding={
                    "freeze_sha256": freeze_digest,
                    "binding_sha256": binding
                    if stage in {"G2", "G2c"}
                    else freeze_digest,
                },
            )
            if not result["pass"]:
                raise ValueError("Coverage prerequisite incomplete or failed")
        root = SealedStore(
            DEFAULT_SEALED.parent / "sealed-v4-confirmatory" / identifier
        )
        provenance = manifest(study)
        provenance.update(freeze_sha256=freeze_digest, binding_sha256=binding)
        if args.release_at_close:
            print(json.dumps(released_curves(root), allow_nan=False))
        else:
            while True:
                outcome = schedule(
                    root, provenance, shard=args.shard, shards=args.shards
                )
                print(json.dumps(outcome), flush=True)
                if not outcome["tier_blocked"]:
                    break
                time.sleep(1)
        return 0
    except Exception:
        print(json.dumps({"preflight_or_execution_failure_count": 1}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
