"""Independent small checks plus a local-only invocation of Dong's cached code."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import itertools
import json
import math
import sys
import time
from pathlib import Path

DONG_SHA256 = "57afbe543032e2138c23622f81ed48b72b37310e4f4c2ef14594e7cb3c9ad4ae"


def abed_example_one() -> dict[str, object]:
    """Equation (1), Example 1, independent scalar loops (no author code)."""

    def iterate(cross_topic_source: bool) -> tuple[list[list[float]], float, int]:
        state = [[0.0, 0.0], [0.0, 0.5]]
        innate = ((0.0, 0.0), (0.0, 0.5))
        last_gap = 0.0
        for _step in range(1, 501):
            next_state = [[0.0, 0.0], [0.0, 0.0]]
            for agent in range(2):
                for topic in range(2):
                    other = 1 - topic
                    weight = 0.05 if cross_topic_source else 0.0
                    mismatch = (1 - weight) * abs(
                        1 - state[agent][topic]
                    ) + weight * abs(1 - state[agent][other])
                    source = 0.24 * (1 - mismatch)
                    peer = (state[0][topic] + state[1][topic]) / 2
                    next_state[agent][topic] = (1 - 0.8 * (1 + source)) * innate[agent][
                        topic
                    ] + 0.8 * (peer + source)
            last_gap = max(
                abs(next_state[i][t] - state[i][t]) for i in range(2) for t in range(2)
            )
            state = next_state
            if last_gap < 1e-10:
                break
        return state, last_gap, _step

    full, full_gap, full_steps = iterate(True)
    decoupled, decoupled_gap, decoupled_steps = iterate(False)
    return {
        "full": full,
        "decoupled": decoupled,
        "full_gap": full_gap,
        "decoupled_gap": decoupled_gap,
        "full_steps": full_steps,
        "decoupled_steps": decoupled_steps,
        "source": "https://arxiv.org/html/2603.21081#S3",
    }


def neuhauser_mean_shift() -> dict[str, object]:
    """Equation (3CM) on a small complete hypergraph, qualitative Fig. 3 check."""
    outcomes = []
    for lam in (-1.0, 0.0, 1.0):
        states = [0.0] * 8 + [1.0] * 2
        for _ in range(500):
            change = [0.0] * 10
            for trio in itertools.combinations(range(10), 3):
                for i in trio:
                    j, k = (node for node in trio if node != i)
                    change[i] += math.exp(lam * abs(states[j] - states[k])) * (
                        states[j] + states[k] - 2 * states[i]
                    )
            states = [x + 0.001 * dx for x, dx in zip(states, change, strict=True)]
        outcomes.append(
            {
                "lambda": lam,
                "initial_mean": 0.2,
                "final_mean": sum(states) / len(states),
            }
        )
    return {
        "outcomes": outcomes,
        "source": "https://arxiv.org/html/1910.09226v1#S4.SS4",
    }


def dong_check(cache: Path) -> dict[str, object]:
    archive = cache / "Code_Public.zip"
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != DONG_SHA256:
        raise ValueError("Dong archive SHA-256 mismatch")
    sys.path.insert(0, str(cache / "Code_Public" / "src"))
    model_module = importlib.import_module("opinion_dynamics.model")
    model_type = model_module.OpinionDynamicsModel
    results = []
    for seed in (42, 43):
        probe = model_type(
            N=40,
            T=2,
            alpha=1.0,
            phi=0.3,
            gamma=1.5,
            K=1.0,
            graph_param=3,
            mean_hdeg=3,
            he_sizes=(3, 8),
            seed=seed,
            init_scale=0.1,
        )
        linear_threshold = 1 / ((1 + 1.5 * probe.d_star_mean) * 1.3)
        nonlinear_threshold = 1 / 1.3
        alpha = (linear_threshold + nonlinear_threshold) / 2
        for p in (1, 2):
            started = time.perf_counter()
            model = model_type(
                N=40,
                T=2,
                alpha=alpha,
                phi=0.3,
                gamma=1.5,
                K=1.0,
                graph_param=3,
                mean_hdeg=3,
                he_sizes=(3, 8),
                seed=seed,
                init_scale=0.1,
                p=p,
            )
            observed = model.run(steps=800, dt=0.02)
            results.append(
                {
                    "seed": seed,
                    "p": p,
                    "alpha": alpha,
                    "linear_threshold": linear_threshold,
                    "nonlinear_threshold": nonlinear_threshold,
                    "P": observed["P"],
                    "absC": observed["absC"],
                    "elapsed_seconds": time.perf_counter() - started,
                }
            )
    return {
        "archive_sha256": digest,
        "source": "https://zenodo.org/api/records/21820152/files/Code_Public.zip/content",
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--dong-cache", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    results = {
        "status": "exploratory",
        "abed": abed_example_one(),
        "neuhauser": neuhauser_mean_shift(),
        "dong": dong_check(args.dong_cache),
    }
    results["elapsed_seconds"] = time.perf_counter() - started
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(results, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
