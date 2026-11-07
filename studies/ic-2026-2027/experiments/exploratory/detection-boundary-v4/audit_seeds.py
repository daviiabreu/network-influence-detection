"""Audit calibration namespaces without generating panels or confirmatory seeds."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ic_study.simulation.detection_v4 import ROLES
from ic_study.simulation.v4_gate import task_seed_plan
from ic_study.simulation.v4_plan import gate_tasks

PHASES = (
    "match",
    "validate",
    "train",
    "check",
    "reference",
    "stencil",
    "nuisance",
    "bootstrap",
)


def audit() -> dict[str, object]:
    plans = {
        task_seed_plan(task)
        for gate in ("G0", "G1b", "G1c", "G2", "G2c")
        for task in gate_tasks(gate)
    }
    representatives = {
        task_seed_plan(gate_tasks(gate)[0])
        for gate in ("G0", "G1b", "G1c", "G2", "G2c")
    }
    total = (
        (len(plans) * 16 + len(representatives) * (8192 - 16))
        * len(PHASES)
        * len(ROLES)
        * 2
    )
    seeds = np.empty(total, dtype=np.uint64)
    materials = 0
    for plan in sorted(plans, key=lambda p: (p.gate, p.block, p.repetition)):
        for phase in PHASES:
            for role in sorted(ROLES):
                for attempt in (0, 1):
                    for index in range(8192 if plan in representatives else 16):
                        seeds[materials] = plan.seed(
                            phase, role, index, attempt=attempt
                        )
                        materials += 1
    seeds.sort()
    collisions = int(np.count_nonzero(seeds[1:] == seeds[:-1]))
    return {
        "kind": "calibration-seed-role-audit",
        "supersedes": "seed-role-audit.json",
        "materials": materials,
        "unique_seeds": materials - collisions,
        "collisions": collisions,
        "gate_plans": {
            gate: len({task_seed_plan(task) for task in gate_tasks(gate)})
            for gate in ("G0", "G1b", "G1c", "G2", "G2c")
        },
        "unique_plans": len(plans),
        "phases": PHASES,
        "roles": sorted(ROLES),
        "attempts": [0, 1],
        "indices_per_plan_role_phase_attempt": 16,
        "full_index_range_representatives": [
            asdict(plan)
            for plan in sorted(
                representatives, key=lambda p: (p.gate, p.block, p.repetition)
            )
        ],
        "indices_per_representative": 8192,
        "intentional_aliases": [
            "G0 cells share one seed plan",
            "matching and validation target/null share selected innovations",
            "stencils reuse base-phase innovations",
            "G2c null and social reference use baseline repetition zero",
        ],
        "confirmatory_seeds_derived": 0,
        "implementation_sha256": hashlib.sha256(
            Path(__file__)
            .parents[3]
            .joinpath("src/ic_study/simulation/detection_v4.py")
            .read_bytes()
        ).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    with args.output.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result))
    if result["collisions"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
