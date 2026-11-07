"""Run bounded comparisons using Thompsky et al.'s DW routine."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
from pathlib import Path
from types import ModuleType

import igraph
import numpy as np

SOURCE_SHA256 = "a2b352c590825a8b4c4491af661ed18772bb8f461f0b5fd54ea3cf0c1db64cae"
SOURCE_COMMIT = "5e33664982bda6b7576074ff47772791459ea22c"
CONFIDENCE = (0.1, 0.2, 0.3, 0.5)
SEEDS = tuple(range(101, 121))


def load_author_code(source: Path) -> ModuleType:
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("Thompsky source SHA-256 mismatch")
    text = raw.decode("utf-8")
    unused_import = "from scipy import io, stats\n"
    if text.count(unused_import) != 1:
        raise ValueError("Expected one unused scipy import")
    module = ModuleType("thompsky_dw")
    module.__file__ = str(source)
    exec(compile(text.replace(unused_import, ""), str(source), "exec"), module.__dict__)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--author-source", required=True, type=Path)
    parser.add_argument("--gamma", type=float, default=0.5)
    parser.add_argument("--delta", type=float, default=0.5)
    args = parser.parse_args()
    if not 0 <= args.gamma <= 1 or not 0 <= args.delta <= 1:
        raise ValueError("Gamma and delta must be in [0, 1]")
    author = load_author_code(args.author_source)
    rows = []
    for confidence in CONFIDENCE:
        for seed in SEEDS:
            opinions = np.random.default_rng(seed).uniform(size=100).tolist()
            for adaptive in (False, True):
                graph = igraph.Graph.Full(100)
                graph.vs["opinion"] = opinions
                started = time.perf_counter()
                result = author.DW(
                    graph,
                    confidence,
                    0.3,
                    0.1 if adaptive else 0.5,
                    args.gamma if adaptive else 0.0,
                    args.delta if adaptive else 1.0,
                    tol=0.01,
                    Tmax=100_000_000,
                    random_seed=seed + 10_000,
                )
                rows.append(
                    {
                        "confidence": confidence,
                        "seed": seed,
                        "adaptive": adaptive,
                        "T": result["T"],
                        "bailout": result["bailout"],
                        "elapsed_seconds": time.perf_counter() - started,
                    }
                )
    summary = []
    for confidence in CONFIDENCE:
        for adaptive in (False, True):
            subset = [
                row
                for row in rows
                if row["confidence"] == confidence and row["adaptive"] == adaptive
            ]
            times = [row["T"] for row in subset if not row["bailout"]]
            summary.append(
                {
                    "confidence": confidence,
                    "adaptive": adaptive,
                    "mean_log_T": statistics.mean(math.log(t) for t in times),
                    "mean_log10_T": statistics.mean(math.log10(t) for t in times),
                    "mean_T": statistics.mean(times),
                    "bailouts": sum(row["bailout"] for row in subset),
                }
            )
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(
            {
                "status": "exploratory_author_code_subset",
                "source_commit": SOURCE_COMMIT,
                "source_sha256": SOURCE_SHA256,
                "source_transform": (
                    "Removed one unused scipy.io/stats import at load time"
                ),
                "parameters": {
                    "N": 100,
                    "mu": 0.3,
                    "tol": 0.01,
                    "Tmax": 100_000_000,
                    "gamma_adaptive": args.gamma,
                    "delta_adaptive": args.delta,
                    "z_adaptive": 0.1,
                    "gamma_baseline": 0.0,
                    "delta_baseline": 1.0,
                    "z_baseline": 0.5,
                },
                "rows": rows,
                "summary": summary,
            },
            stream,
            indent=2,
            sort_keys=True,
        )
        stream.write("\n")


if __name__ == "__main__":
    main()
