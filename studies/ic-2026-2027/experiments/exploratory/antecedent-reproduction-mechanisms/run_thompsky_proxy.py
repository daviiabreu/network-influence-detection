"""Small independent proxy for Thompsky et al.; not their released code."""

from __future__ import annotations

import argparse
import json
import random
import time
from itertools import combinations
from pathlib import Path

from ic_study.models.deffuant import Parameters, State

SEEDS = tuple(range(101, 109))
CAP = 10000


def run(seed: int, topology: str, adaptive: bool) -> dict[str, object]:
    edges = (
        list(combinations(range(20), 2))
        if topology == "complete"
        else [(i, i + 1) for i in range(19)] + [(0, 19)]
    )
    initial = random.Random(seed).random
    opinions = [initial() for _ in range(20)]
    parameters = Parameters(
        confidence=0.2,
        mu=0.3,
        initial_weight=0.1,
        gamma=0.5 if adaptive else 0.0,
        delta=0.5 if adaptive else 1.0,
    )
    state = State(opinions, edges, parameters)
    rng = random.Random(seed + 10000)
    settled_at = None
    started = time.perf_counter()
    for step in range(1, CAP + 1):
        state.step(rng)
        if step % 100 == 0 and all(
            abs(state.opinions[i] - state.opinions[j]) < 0.001
            or abs(state.opinions[i] - state.opinions[j]) >= 0.2
            for i, j in edges
        ):
            settled_at = step
            break
    return {
        "seed": seed,
        "topology": topology,
        "adaptive": adaptive,
        "settled_at": settled_at,
        "censored": settled_at is None,
        "elapsed_seconds": time.perf_counter() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = [
        run(seed, topology, adaptive)
        for seed in SEEDS
        for topology in ("complete", "cycle")
        for adaptive in (False, True)
    ]
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(
            {"status": "exploratory_proxy", "rows": rows},
            stream,
            indent=2,
            sort_keys=True,
        )
        stream.write("\n")


if __name__ == "__main__":
    main()
