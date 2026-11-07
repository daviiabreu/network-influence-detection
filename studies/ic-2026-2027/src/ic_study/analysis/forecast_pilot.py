"""Execute and summarize a bounded synthetic one-step forecast experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import statistics
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ic_study.metrics.histogram_scores import SCORES, score_ensemble
from ic_study.models.histogram_forecast import Dynamics, draw_histogram, seed_for


def cells(spec: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"{truth}-a{attempts}-n{sample_size}",
            "truth": truth,
            "attempts": attempts,
            "sample_size": sample_size,
        }
        for truth in spec["truths"]
        for attempts in spec["attempts"]
        for sample_size in spec["sample_sizes"]
    ]


def trajectory(
    spec: dict[str, Any],
    cell: dict[str, Any],
    replicate: int,
    phase: str,
    members: int,
    timings: dict[str, float] | None = None,
) -> dict[str, Any]:
    phase_spec = spec["phases"][phase]
    truth = Dynamics(**spec["models"][cell["truth"]])
    observed = tuple([cell["sample_size"] // 11] * 11)
    if sum(observed) != cell["sample_size"]:
        raise ValueError("Initial uniform histogram requires size divisible by eleven")
    waves: list[dict[str, Any]] = []
    for wave in range(spec["train_steps"] + spec["test_steps"]):
        data_seed = seed_for(
            spec["seed"], "truth", phase_spec["data_group"], cell["id"], replicate, wave
        )
        shared = {
            "population": spec["population"],
            "sample_size": cell["sample_size"],
            "attempts": cell["attempts"],
        }
        outcome = draw_histogram(observed, truth, **shared, seed=data_seed)
        forecasts: dict[str, Any] = {}
        for model in spec["model_order"]:
            model_seed = seed_for(
                spec["seed"], "forecast", phase, cell["id"], replicate, wave, model
            )
            dynamics = Dynamics(**spec["models"][model])
            generation_started = time.perf_counter()
            ensemble = [
                draw_histogram(
                    observed,
                    dynamics,
                    **shared,
                    seed=seed_for(model_seed, member),
                )
                for member in range(members)
            ]
            scoring_started = time.perf_counter()
            scores = score_ensemble(ensemble, outcome)
            if timings is not None:
                timings["generation"] += scoring_started - generation_started
                timings["scoring"] += time.perf_counter() - scoring_started
            forecasts[model] = {
                "seed": model_seed,
                "ensemble": ensemble,
                "scores": scores,
            }
        waves.append(
            {
                "wave": wave,
                "split": "train" if wave < spec["train_steps"] else "test",
                "observed": observed,
                "outcome": outcome,
                "data_seed": data_seed,
                "forecasts": forecasts,
            }
        )
        observed = outcome
    selected = {
        score: min(
            spec["model_order"],
            key=lambda model: math.fsum(
                w["forecasts"][model]["scores"][score]
                for w in waves[: spec["train_steps"]]
            ),
        )
        for score in SCORES
    }
    return {
        "record": "trajectory",
        "cell": cell,
        "replicate": replicate,
        "waves": waves,
        "selected_on_train": selected,
    }


def interval(values: list[float], critical_value: float) -> dict[str, Any]:
    mean = statistics.mean(values)
    se = statistics.stdev(values) / math.sqrt(len(values)) if len(values) > 1 else None
    return {
        "n": len(values),
        "mean": mean,
        "standard_error": se,
        "interval": None
        if se is None
        else [mean - critical_value * se, mean + critical_value * se],
    }


def summarize(rows: list[dict[str, Any]], spec: dict[str, Any]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row["cell"]["id"], []).append(row)
    summaries = []
    for group in groups.values():
        cell = group[0]["cell"]
        scores = {}
        for score in SCORES:
            values: dict[str, list[float]] = {m: [] for m in spec["model_order"]}
            values["selected"] = []
            for row in group:
                heldout = [w for w in row["waves"] if w["split"] == "test"]
                for model in spec["model_order"]:
                    values[model].append(
                        statistics.mean(
                            w["forecasts"][model]["scores"][score] for w in heldout
                        )
                    )
                values["selected"].append(values[row["selected_on_train"][score]][-1])
            differences = {
                model: interval(
                    [x - y for x, y in zip(losses, values["constant"], strict=True)],
                    spec["interval_critical_value"],
                )
                for model, losses in values.items()
                if model != "constant"
            }
            scores[score] = {
                "losses": {
                    model: interval(losses, spec["interval_critical_value"])
                    for model, losses in values.items()
                },
                "difference_from_constant": differences,
                "selected_model_counts": dict(
                    Counter(row["selected_on_train"][score] for row in group)
                ),
            }
        summaries.append({"cell": cell, "trajectories": len(group), "scores": scores})
    return summaries


def execute(spec_path: Path, phase: str, members: int, output: Path) -> None:
    spec_bytes = spec_path.read_bytes()
    spec = json.loads(spec_bytes)
    if members not in spec["phases"][phase]["allowed_members"]:
        raise ValueError("Ensemble size is outside the frozen phase specification")
    package = Path(__file__).resolve().parents[1]
    study = package.parent.parent
    source_paths = [
        *sorted(package.rglob("*.py")),
        study / "pyproject.toml",
        study / "uv.lock",
    ]
    header = {
        "record": "header",
        "format": "probabilistic-forecast-exploratory-v1",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "code_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=study, text=True
        ).strip(),
        "source_sha256": {
            str(p.relative_to(study)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in source_paths
        },
        "spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "spec": spec,
        "phase": phase,
        "members": members,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "rng": "random.Random MT19937; SHA256-derived independent role seeds",
        },
    }
    rows = []
    timings = {"generation": 0.0, "scoring": 0.0}
    started = time.perf_counter()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        stream.write(json.dumps(header, sort_keys=True) + "\n")
        stream.flush()
        for cell in cells(spec):
            for replicate in range(spec["phases"][phase]["replicates"]):
                row = trajectory(spec, cell, replicate, phase, members, timings)
                stream.write(json.dumps(row, sort_keys=True) + "\n")
                stream.flush()
                rows.append(row)
            print(f"{phase}: {cell['id']} completed", flush=True)
        footer = {
            "record": "completed",
            "completed_at_utc": datetime.now(UTC).isoformat(),
            "elapsed_seconds": time.perf_counter() - started,
            "timing_seconds": timings,
            "trajectories": len(rows),
            "summary": summarize(rows, spec),
        }
        stream.write(json.dumps(footer, sort_keys=True) + "\n")
    print(f"sha256={hashlib.sha256(output.read_bytes()).hexdigest()}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--members", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    execute(args.spec, args.phase, args.members, args.output)


if __name__ == "__main__":
    main()
