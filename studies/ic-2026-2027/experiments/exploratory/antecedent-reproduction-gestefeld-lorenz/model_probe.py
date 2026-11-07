"""Small independent implementation of the update rule in JASSS 26(4):9.

This probe uses published parameters. It does not load or fit survey data.
"""

import argparse
import json
import platform
import random
import sys
import time


def category(value: float) -> int:
    return min(10, max(0, int(value + 0.5)))


def histogram(opinions: list[float]) -> list[int]:
    counts = [0] * 11
    for opinion in opinions:
        counts[category(opinion)] += 1
    return counts


def simulate(seed: int, agents: int, steps: int, annual_steps: int) -> dict:
    rng = random.Random(seed)
    alpha, rho, theta, sigma, latitude, sharpness = 0.25, 0.5, 0.1, 2.0, 4.0, 2
    initial = [min(10.5, max(-0.5, rng.gauss(5.0, sigma))) for _ in range(agents)]
    opinions = initial.copy()
    order = list(range(agents))

    def step() -> None:
        rng.shuffle(order)
        for receiver in order:
            if rng.random() < theta:
                opinions[receiver] = initial[receiver]
                continue
            source = rng.randrange(agents - 1)
            if source >= receiver:
                source += 1
            discrepancy = abs(opinions[source] - opinions[receiver])
            factor = latitude**sharpness / (
                latitude**sharpness + discrepancy**sharpness
            )
            delta = (
                factor
                * alpha
                * ((opinions[source] - 5.0) - rho * (opinions[receiver] - 5.0))
            )
            opinions[receiver] = min(10.5, max(-0.5, opinions[receiver] + delta))

    for _ in range(steps):
        step()
    before = [category(value) for value in opinions]
    for _ in range(annual_steps):
        step()
    after = [category(value) for value in opinions]
    counts = histogram(opinions)
    return {
        "seed": seed,
        "agents": agents,
        "spinup_steps": steps,
        "annual_steps": annual_steps,
        "parameters": {
            "alpha": alpha,
            "rho": rho,
            "theta": theta,
            "sigma": sigma,
            "lambda": latitude,
            "k": sharpness,
        },
        "final_counts_0_to_10": counts,
        "final_mean": round(
            sum(i * count for i, count in enumerate(counts)) / agents, 6
        ),
        "changed_after_annual_steps": sum(
            a != b for a, b in zip(before, after, strict=True)
        ),
        "unchanged_or_plus_minus_one": sum(
            abs(a - b) <= 1 for a, b in zip(before, after, strict=True)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--agents", type=int, default=800)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--annual-steps", type=int, default=24)
    args = parser.parse_args()
    start = time.perf_counter()
    result = simulate(args.seed, args.agents, args.steps, args.annual_steps)
    result["environment"] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    result["runtime_seconds"] = round(time.perf_counter() - start, 3)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
