"""Run the bounded exploratory pilot and preserve complete per-trial inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ic_study.models.deffuant import Edge, Parameters, State, components
from ic_study.simulation.fragmentation import simulate


def make_edges(profile: dict[str, Any], seed: int) -> list[Edge]:
    n = int(profile["n"])
    kind = profile["kind"]
    rng = random.Random(seed)
    if kind == "complete":
        return [(i, j) for i in range(n) for j in range(i + 1, n)]
    if kind == "er":
        probability = float(profile["mean_degree"]) / (n - 1)
        return [
            (i, j)
            for i in range(n)
            for j in range(i + 1, n)
            if rng.random() < probability
        ]
    if kind != "modular" or n % 2:
        raise ValueError("Unknown graph family or odd modular size")
    half = n // 2
    probability = float(profile["within_mean_degree"]) / (half - 1)
    edges = [
        (i, j)
        for start in (0, half)
        for i in range(start, start + half)
        for j in range(i + 1, start + half)
        if rng.random() < probability
    ]
    bridges = rng.sample(range(half * half), int(profile["bridges"]))
    edges.extend((k // half, half + k % half) for k in bridges)
    return sorted(edges)


def trial_inputs(spec: dict[str, Any], phase: str) -> list[dict[str, Any]]:
    trials = []
    phase_spec = spec["phases"][phase]
    for profile_id in phase_spec["profiles"]:
        profile = spec["profiles"][profile_id]
        profile_index = int(profile["seed_index"])
        for confidence in phase_spec["confidences"]:
            for graph_rep in range(phase_spec["graph_replicates"]):
                for opinion_rep in range(phase_spec["opinion_replicates"]):
                    seed_base = (
                        spec["seed_base"]
                        + phase_spec["seed_offset"]
                        + profile_index * 10000
                        + graph_rep * 100
                    )
                    for model in ("uniform", "adaptive"):
                        trials.append(
                            {
                                "profile_id": profile_id,
                                "profile": profile,
                                "confidence": confidence,
                                "graph_rep": graph_rep,
                                "opinion_rep": opinion_rep,
                                "model": model,
                                "graph_seed": seed_base,
                                "opinion_seed": seed_base + 10 + opinion_rep,
                                "event_seed": seed_base + 20 + opinion_rep,
                            }
                        )
    if phase == "benchmark":
        return trials[:10]
    return trials


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, float, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["profile_id"], row["confidence"], row["model"])
        groups.setdefault(key, []).append(row["result"])
    summaries = []
    for (profile_id, confidence, model), results in groups.items():
        group: dict[str, Any] = {
            "profile_id": profile_id,
            "confidence": confidence,
            "model": model,
            "trials": len(results),
            "certified": sum(r["status"] == "certified" for r in results),
            "right_censored": sum(r["status"] == "right_censored" for r in results),
            "numerical_failures": sum(
                r["status"] == "numerical_failure" for r in results
            ),
        }
        for criterion in ("cached", "diameter"):
            stops = [r for r in results if r[f"{criterion}_stop"] is not None]
            group[criterion] = {
                "stops_observed": len(stops),
                "cross_interactions_observed": sum(
                    r[f"first_cross_{criterion}"] is not None for r in stops
                ),
                "different_endpoint_partitions": sum(
                    r[f"{criterion}_stop"]["partition"] != r["endpoint_partition"]
                    for r in stops
                ),
                "uncertified_without_observed_crossing": sum(
                    r["status"] != "certified" and r[f"first_cross_{criterion}"] is None
                    for r in stops
                ),
            }
        summaries.append(group)
    return summaries


def execute(spec_path: Path, phase: str, output: Path, max_attempts: int) -> None:
    spec_bytes = spec_path.read_bytes()
    spec = json.loads(spec_bytes)
    if max_attempts not in spec["phases"][phase]["allowed_max_attempts"]:
        raise ValueError("Attempt cap is outside the frozen phase specification")
    package = Path(__file__).resolve().parents[1]
    study = package.parent.parent
    source_paths = [
        *sorted(package.rglob("*.py")),
        study / "pyproject.toml",
        study / "uv.lock",
    ]
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=study, text=True
    ).strip()
    header = {
        "record": "header",
        "format": "fragmentation-exploratory-run-v1",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "code_revision": revision,
        "source_sha256": {
            str(p.relative_to(study)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in source_paths
        },
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "spec": spec,
        "phase": phase,
        "max_attempts": max_attempts,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "rng": "random.Random MT19937; three explicit seed streams",
        },
    }
    rows = []
    started = time.perf_counter()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        stream.write(json.dumps(header, sort_keys=True) + "\n")
        stream.flush()
        trials = trial_inputs(spec, phase)
        for index, trial in enumerate(trials):
            trial_started = time.perf_counter()
            edges = make_edges(trial["profile"], trial["graph_seed"])
            rng = random.Random(trial["opinion_seed"])
            opinions = [rng.random() for _ in range(trial["profile"]["n"])]
            model = spec["models"][trial["model"]]
            state = State(
                opinions,
                edges,
                Parameters(confidence=trial["confidence"], **model),
            )
            result = simulate(
                state,
                event_seed=trial["event_seed"],
                max_attempts=max_attempts,
                tolerance=spec["phases"][phase]["tolerance"],
                margin=spec["certificate_margin"],
            )
            row = {
                "record": "trial",
                "trial_index": index,
                **trial,
                "initial_opinions": opinions,
                "base_edges": edges,
                "base_components": components(len(opinions), edges),
                "result": result.to_dict(),
                "elapsed_seconds": time.perf_counter() - trial_started,
            }
            stream.write(json.dumps(row, sort_keys=True) + "\n")
            stream.flush()
            rows.append(row)
            print(
                f"{phase} {index + 1}/{len(trials)} {trial['profile_id']} "
                f"c={trial['confidence']} {trial['model']}: {result.status}, "
                f"attempts={result.attempts}, "
                f"cross={result.first_cross_cached}/{result.first_cross_diameter}",
                flush=True,
            )
        footer = {
            "record": "completed",
            "completed_at_utc": datetime.now(UTC).isoformat(),
            "elapsed_seconds": time.perf_counter() - started,
            "trials": len(rows),
            "summary": summarize(rows),
        }
        stream.write(json.dumps(footer, sort_keys=True) + "\n")
    print(f"sha256={hashlib.sha256(output.read_bytes()).hexdigest()}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument(
        "--phase",
        choices=["benchmark", "pilot", "sensitivity", "control"],
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-attempts", type=int, required=True)
    args = parser.parse_args()
    execute(args.spec, args.phase, args.output, args.max_attempts)


if __name__ == "__main__":
    main()
