"""Validate retained pilot bytes, then regenerate its documented case 35."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from ic_study.models.deffuant import Parameters, State
from ic_study.simulation.fragmentation import effective_partition, simulate
from ic_study.validation.experiments import main as validate_offline


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    study = args.study_root.resolve()
    pilot = study / "experiments/exploratory/fragmentation-pilot-v1"
    manifest = pilot / "run-manifest.json"
    args.output_dir.mkdir(parents=True)
    receipt = args.output_dir / "offline-validation.json"
    code = validate_offline(
        [
            "--study-root",
            str(study),
            "--manifest",
            str(manifest),
            "--artifact-root",
            str(args.artifact_root),
            "--receipt",
            str(receipt),
        ]
    )
    if code:
        return code

    metadata: dict[str, Any] = json.loads(manifest.read_text())
    phase = metadata["phases"]["pilot"]
    digest = phase["sha256"]
    direct = args.artifact_root / digest
    artifact = direct if direct.is_file() else args.artifact_root / digest[:2] / digest
    with artifact.open() as stream:
        header = json.loads(stream.readline())
        for index, line in enumerate(stream):
            if index == 35:
                case = json.loads(line)
                break
        else:
            raise ValueError("Retained case 35 is absent")

    if case["record"] != "trial" or case["trial_index"] != 35:
        raise ValueError("Retained case 35 has a different identity")
    params = Parameters(
        confidence=case["confidence"],
        **header["spec"]["models"][case["model"]],
    )
    state = State(
        case["initial_opinions"],
        [tuple(edge) for edge in case["base_edges"]],
        params,
    )
    result = simulate(
        state,
        event_seed=case["event_seed"],
        max_attempts=header["max_attempts"],
        tolerance=header["spec"]["phases"]["pilot"]["tolerance"],
        margin=header["spec"]["certificate_margin"],
    )
    regenerated = json.loads(json.dumps(result.to_dict()))
    if regenerated != case["result"]:
        raise ValueError("Regenerated scientific result differs from retained case 35")
    stop = regenerated["cached_stop"]
    at_stop = State(stop["opinions"], state.edges, params)
    output = {
        "format": "fragmentation-case-regeneration-v1",
        "source_manifest_sha256": json.loads(receipt.read_text())["manifest_sha256"],
        "source_artifact_sha256": digest,
        "case_index": 35,
        "source_code_revision": phase["code_revision"],
        "regeneration_code_revision": subprocess.check_output(
            ["git", "-C", str(study), "rev-parse", "HEAD"], text=True
        ).strip(),
        "matches_retained_scientific_result": True,
        "cached_groups": len(stop["partition"]),
        "current_groups_at_cached_stop": len(effective_partition(at_stop)),
        "result": regenerated,
    }
    with (args.output_dir / "regenerated-case-35.json").open("x") as stream:
        json.dump(output, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print("Case 35 regenerated: scientific result matches retained record")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
