"""Rebuild a cost projection without simulations or access to sealed gate data."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).parent
    panel_path = here / "panel-cost-final-code.json"
    solver_path = here / "cost-measurements-with-retry.json"
    inventory_path = here / "inventory.json"
    panel = json.loads(panel_path.read_text())
    solver = json.loads(solver_path.read_text())
    inventory = json.loads(inventory_path.read_text())["rows"]
    q = {r["operation"]: r["cpu_seconds"] / r["panels"] for r in panel["panels"]}
    e0, e1 = [r["evaluations"] for r in solver["solver_attempts"]]
    factor = 1.25 / (8 * 3600)

    def cost(
        social: float,
        null: float,
        *,
        identity: bool = False,
        dimensions: int = 2,
        retry_rate: float = 0,
        kind: str = "pipeline",
        fd_steps: int = 1,
    ) -> float:
        if identity:
            base = 5120 * social + 5120 * null
            return base if kind == "match" else base + 6000 * (social + null)
        # Diagnostic matching stencils are included even when no D5 follows.
        matching = (1024 + 4096) * social + (
            e0 * 1024 + 4096 + dimensions * 1024
        ) * null
        retry = (4096 + 4096) * social + (e1 * 4096 + 4096 + dimensions * 4096) * null
        if kind == "match":
            return matching + retry_rate * retry
        if kind == "refit":
            return matching + retry_rate * retry + 2000 * social + 6000 * null
        phases = 10000 * (social + null)
        # First matching stencil already counted. Second step also covers matching.
        remaining = dimensions * (6000 * fd_steps + 1024 * (fd_steps - 1)) * null
        # Extra matching panels in the second-step stencil when retry selected M=4096.
        remaining += retry_rate * dimensions * 3072 * (fd_steps - 1) * null
        return matching + retry_rate * retry + phases + remaining

    scenarios = {}
    for retry_rate in (0, 0.25, 1):
        tiers = {str(t): 0.0 for t in range(1, 7)}
        for row in inventory:
            options = row["options"]
            extended = row["channel"] != "observed" or options.get("mobility", False)
            dimensions = 1 if row["family"] in {"A", "C"} else 2
            identity = (
                row["a"] == 0 and row["family"] != "C" and not options.get("anchor", 0)
            )
            if row["tier"] == 6:
                social, null = q["steps24-social"], q["steps24-null"]
            elif extended:
                social, null = q["control-social"], q["control-null"]
            else:
                social = q["anchor-social"] if row["a"] == 0 else q["main-social"]
                null = q["main-null-" + row["family"]]
            tiers[str(row["tier"])] += factor * cost(
                social,
                null,
                identity=identity,
                dimensions=dimensions,
                retry_rate=retry_rate,
            )
        gate = {"G0": 0.0}
        for family, control in [(f, False) for f in "ABCDE"] + [("B", True)] * 3:
            for anchor, cells in ((False, 72), (True, 9)):
                social = (
                    q["control-social"]
                    if control
                    else q["anchor-social"]
                    if anchor
                    else q["main-social"]
                )
                null = q["control-null"] if control else q["main-null-" + family]
                gate["G0"] += (
                    factor
                    * cells
                    * cost(
                        social,
                        null,
                        identity=anchor and family != "C",
                        dimensions=1 if control or family in {"A", "C"} else 2,
                        kind="match",
                        retry_rate=retry_rate,
                    )
                )
        # Frozen measured 15.70 worker seconds per 9-slot score bootstrap is a proxy.
        gate["G1b"] = factor * 5000 * 15.70
        gate["G1c"] = (
            factor * 150 * cost(q["anchor-social"], q["main-null-A"], identity=True)
        )
        gate["G2"] = (
            factor
            * 700
            * cost(
                q["main-social"], q["main-null-B"], retry_rate=retry_rate, fd_steps=2
            )
        )
        gate["G2c"] = factor * (
            140
            * cost(
                q["main-social"], q["main-null-B"], retry_rate=retry_rate, kind="refit"
            )
            + 2 * cost(q["main-social"], q["main-null-B"], retry_rate=retry_rate)
            + 8000 * q["main-social"]
        )
        gate["score_bootstrap_G1c_G2_G2c"] = factor * (852 / 9) * 15.70
        tiers["score_bootstrap"] = factor * 414 * 15.70
        scenarios[str(retry_rate)] = {
            "retry_fraction_assumed": retry_rate,
            "gate_hours": gate,
            "gate_total_hours": sum(gate.values()),
            "tier_hours": tiers,
            "tiers_1_5_hours": sum(tiers[str(t)] for t in range(1, 6)),
            "tiers_total_hours": sum(tiers.values()),
            "total_hours": sum(gate.values()) + sum(tiers.values()),
        }
    result = {
        "kind": "conditional-compute-projection-not-allocation",
        "workers": 8,
        "reserve_fraction": 0.25,
        "close_utc": "2026-10-19T02:59:00Z",
        "rows": len(inventory),
        "comparison_r_units": 414,
        "cpu_seconds_per_panel": q,
        "solver_evaluations_assumed": [e0, e1],
        "scenarios": scenarios,
        "limitations": [
            (
                "One B cell measured for solver; evaluation counts are proxies for "
                "other cells/families."
            ),
            (
                "CPU time divided by eight assumes dedicated workers; wall contention "
                "is not multiplied a second time."
            ),
            (
                "Controls use the observed PipelineResult already computed in tiers "
                "1/2; no panel sharing discount between channels."
            ),
            (
                "Mobility is fully charged as separate feature pipelines; "
                "hypothetical panel reuse is not a saving."
            ),
            (
                "D5 resampling/LDA, I/O, hashing and scheduling remain within the 25% "
                "reserve only if measured overhead fits."
            ),
            (
                "Score bootstrap uses the frozen 15.70-second nine-slot measurement, "
                "not a new benchmark."
            ),
            (
                "Retries in matching use 4096; G2 uses both FD steps. Diagnostic "
                "stencils are additional in G0/G2c."
            ),
            (
                "The single retry observation does not estimate a population retry "
                "frequency."
            ),
            (
                "Full inventory may exceed the time window; incomplete units follow "
                "D9, without outcome-driven reordering."
            ),
        ],
        "inputs": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (panel_path, solver_path, inventory_path)
        },
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    with args.output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {key: round(value["total_hours"], 2) for key, value in scenarios.items()}
        )
    )


if __name__ == "__main__":
    main()
