"""Review must supply a freeze record; this command never creates one."""

from __future__ import annotations

# ruff: noqa: E402 -- BLAS limits must precede NumPy imports in spawned workers.
import os

for variable in ("OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import hashlib
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from ic_study.simulation.v4_gate import (
    GapRateStopError,
    aggregate,
    allocation_preflight,
    authorize_stage,
    execute_task,
    g0_statuses,
    manifest,
    preflight,
)
from ic_study.simulation.v4_plan import G2_CELLS, gate_tasks
from ic_study.simulation.v4_store import DEFAULT_SEALED, SealedStore


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument(
        "--gate", choices=["G0", "G1b", "G1c", "G2", "G2c"], required=True
    )
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--aggregate-only", action="store_true")
    parser.add_argument("--allocation", type=Path)
    parser.add_argument("--criteria", type=Path)
    args = parser.parse_args()
    try:
        if not 0 <= args.shard < args.shards:
            raise ValueError("Invalid shard")
        study = Path(__file__).resolve().parents[3]
        freeze = preflight(args.freeze, study)
        identifier = hashlib.sha256(
            json.dumps(freeze["code"], sort_keys=True).encode()
        ).hexdigest()
        freeze_digest = hashlib.sha256(args.freeze.read_bytes()).hexdigest()
        root = SealedStore(DEFAULT_SEALED / identifier)
        criteria_path = args.criteria or Path(__file__).parent / "criteria-v43.json"
        if args.gate not in {"G2", "G2c"} and args.criteria is not None:
            raise ValueError("Recalibration applies only after G0")
        criteria_bytes = criteria_path.read_bytes()
        criteria = json.loads(criteria_bytes)
        cells = G2_CELLS
        binding_digest = freeze_digest
        if args.gate in {"G2", "G2c"}:
            if args.allocation is None:
                raise ValueError("Second binding required before G2")
            cells = allocation_preflight(
                args.allocation, freeze_digest, g0_statuses(root), criteria_bytes
            )
            binding_digest = hashlib.sha256(args.allocation.read_bytes()).hexdigest()
        if not criteria["joint_targets_met"]:
            raise ValueError("Artificial operating targets not met")
        authorize_stage(root, args.gate, freeze_digest, binding_digest, create=False)
        stages = ["G0", "G1b", "G1c", "G2", "G2c"]
        for stage in stages[: stages.index(args.gate)]:
            result = aggregate(
                stage,
                root.root,
                criteria,
                cells=cells,
                binding={
                    "freeze_sha256": freeze_digest,
                    "binding_sha256": binding_digest
                    if stage in {"G2", "G2c"}
                    else freeze_digest,
                },
            )
            if not result["pass"]:
                print(
                    json.dumps(
                        {"pass": False, "prerequisite_complete_and_passed": False}
                    )
                )
                return 2
        if not args.aggregate_only:
            authorize_stage(root, args.gate, freeze_digest, binding_digest)
            selected = [
                task
                for task in gate_tasks(args.gate, cells=cells)
                if task.index % args.shards == args.shard
            ]
            provenance = manifest(study)
            provenance["freeze_sha256"] = freeze_digest
            provenance["binding_sha256"] = binding_digest
            with ProcessPoolExecutor(
                max_workers=8, mp_context=multiprocessing.get_context("spawn")
            ) as pool:
                completed = failed = 0
                for outcome in pool.map(
                    execute_task,
                    [(task, str(root.root), provenance) for task in selected],
                    chunksize=1,
                ):
                    completed += outcome["completed"]
                    failed += outcome["failed"]
                    print(
                        json.dumps(
                            {"completed_count": completed, "failure_count": failed}
                        ),
                        flush=True,
                    )
        summary = aggregate(
            args.gate,
            root.root,
            criteria,
            cells=cells,
            binding={"freeze_sha256": freeze_digest, "binding_sha256": binding_digest},
        )
        root.append("criteria", summary)
        print(json.dumps(summary, allow_nan=False))
        return 0 if summary["pass"] else 1
    except GapRateStopError as exc:
        stop = {"pass": False, "stopped_before_G2": True, "g0_gap_binding": exc.report}
        root.append("criteria", stop)
        print(json.dumps(stop, allow_nan=False))
        return 2
    except Exception:
        # No traceback: a worker or NumPy exception can interpolate scientific data.
        print(json.dumps({"pass": False, "preflight_or_execution_failure_count": 1}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
