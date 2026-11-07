"""Frozen small exploratory controls; writes one new JSON result file."""

from __future__ import annotations

import argparse
import json
import random
import time
from itertools import combinations
from pathlib import Path

from ic_study.models.mechanism_controls import (
    expected_exposure,
    exposure_weights,
    pair_step,
    trio_step,
)

SEEDS = tuple(range(101, 109))
CALIBRATION_SEEDS = tuple(range(9001, 9033))
EDGES = tuple(combinations(range(6), 2))
TRIOS = ((0, 1, 4), (1, 2, 5), (2, 3, 4), (0, 3, 5))
STEPS = 120


def initial_pair(seed: int) -> tuple[tuple[float, float], ...]:
    rng = random.Random(seed)
    return tuple(
        ((0.15 if i < 3 else 0.85) + rng.uniform(-0.02, 0.02), rng.uniform(0.2, 0.8))
        for i in range(6)
    )


def select(probabilities: tuple[float, ...], unit: float) -> int:
    cumulative = 0.0
    for i, probability in enumerate(probabilities):
        cumulative += probability
        if unit < cumulative:
            return i
    return len(probabilities) - 1


def run_pair(
    seed: int, mode: str, coupling: float, static_weights: tuple[float, ...]
) -> dict[str, object]:
    states = initial_pair(seed)
    uniforms = random.Random(seed + 10000)
    counts = [0] * len(EDGES)
    started = time.perf_counter()
    for _ in range(STEPS):
        weights = (
            exposure_weights(states, EDGES, 4.0)
            if mode == "adaptive"
            else static_weights
            if mode == "expected"
            else (1 / len(EDGES),) * len(EDGES)
        )
        chosen = select(weights, uniforms.random())
        counts[chosen] += 1
        states = pair_step(
            states,
            EDGES[chosen],
            pair_gain=0.15,
            coupling=coupling,
            source_recipients=(0, 3),
            source_value=1.0,
            source_gain=0.03,
        )
    elapsed = time.perf_counter() - started
    between = sum(
        count for (i, j), count in zip(EDGES, counts, strict=True) if (i < 3) != (j < 3)
    )
    return {
        "seed": seed,
        "mode": mode,
        "coupling": coupling,
        "mse_topic2_wrong": sum((1 - states[i][1]) ** 2 for i in range(3)) / 3,
        "mse_topic2_all": sum((1 - x[1]) ** 2 for x in states) / 6,
        "between_contacts": between,
        "source_signals": STEPS * 2,
        "elapsed_seconds": elapsed,
    }


def initial_trio(seed: int, wrong_majority: bool) -> tuple[float, ...]:
    rng = random.Random(seed)
    return tuple(
        (
            (0.2 if wrong_majority else 0.8)
            if i < 4
            else (0.8 if wrong_majority else 0.2)
        )
        + rng.uniform(-0.02, 0.02)
        for i in range(6)
    )


def run_trio(
    seed: int, wrong_majority: bool, source: bool, nonlinear: bool, projected: bool
) -> dict[str, object]:
    states = initial_trio(seed, wrong_majority)
    started = time.perf_counter()
    for step in range(STEPS):
        states = trio_step(
            states,
            TRIOS[step % len(TRIOS)],
            gain=0.08,
            nonlinear=nonlinear,
            projected=projected,
            source_recipients=(0, 4) if source else (),
            source_gain=0.03,
        )
    elapsed = time.perf_counter() - started
    mean = sum(states) / 6
    return {
        "seed": seed,
        "wrong_majority": wrong_majority,
        "source": source,
        "nonlinear": nonlinear,
        "projected": projected,
        "mean": mean,
        "variance": sum((x - mean) ** 2 for x in states) / 6,
        "mse": sum((1 - x) ** 2 for x in states) / 6,
        "source_signals": STEPS * 2 if source else 0,
        "elapsed_seconds": elapsed,
    }


def calibrate_expected_weights() -> tuple[float, ...]:
    calibration_states = []
    for seed in CALIBRATION_SEEDS:
        states = initial_pair(seed)
        uniforms = random.Random(seed + 10000)
        for _ in range(STEPS):
            probabilities = exposure_weights(states, EDGES, 4.0)
            calibration_states.append(states)
            chosen = select(probabilities, uniforms.random())
            states = pair_step(
                states,
                EDGES[chosen],
                pair_gain=0.15,
                coupling=0.4,
                source_recipients=(0, 3),
                source_value=1.0,
                source_gain=0.03,
            )
    return expected_exposure(calibration_states, EDGES, homophily=4.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    calibrated = calibrate_expected_weights()
    pairs = [
        run_pair(seed, mode, coupling, calibrated)
        for seed in SEEDS
        for coupling in (0.0, 0.4)
        for mode in ("uniform", "expected", "adaptive")
    ]
    trios = [
        run_trio(seed, wrong, source, nonlinear, projected)
        for seed in SEEDS
        for wrong in (True, False)
        for source in (False, True)
        for nonlinear in (False, True)
        for projected in (False, True)
    ]
    result = {
        "status": "exploratory",
        "seeds": SEEDS,
        "calibration_seeds": CALIBRATION_SEEDS,
        "expected_weights": calibrated,
        "pairs": pairs,
        "trios": trios,
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
