"""V4.1 projection from cost-only measurements, with unchanged inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean


def panel_budget(
    *,
    evaluations,
    matching,
    dimensions,
    fit_dimensions=None,
    identity=False,
    kind="pipeline",
    g2=False,
):
    fit_dimensions = dimensions if fit_dimensions is None else fit_dimensions
    if identity:
        count = matching + 2048 + (0 if kind == "match" else 6000)
        return dict(social=count, null=count)
    social = matching + 2048
    null = (evaluations + fit_dimensions) * matching + 2048
    if kind == "refit":
        social += 6000
        null += 6000
    elif kind == "pipeline":
        social += 10000
        null += 10000 + (dimensions - fit_dimensions) * matching
        if g2:
            null += dimensions * matching + 2 * dimensions * 6000
    return dict(social=social, null=null)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).parent
    paths = [
        here / n
        for n in ("panel-cost-v41.json", "cost-fits-v41.json", "inventory.json")
    ]
    panels, fits, inventory = [json.loads(p.read_text()) for p in paths]
    rates = {
        r["operation"]: r["cpu_seconds"] / r["panels"] for r in panels["measurements"]
    }
    rows = fits["measurements"]
    first = [r["attempts"][0]["evaluations"] for r in rows]
    retries = [r["attempts"][1]["evaluations"] for r in rows if len(r["attempts"]) == 2]
    e0 = mean(first)
    e1 = mean(retries) if retries else 64
    empirical_retry = len(retries) / len(rows)
    factor = 1.25 / (8 * 3600)

    def cost(
        social,
        null,
        *,
        identity=False,
        dimensions=2,
        fit_dimensions=None,
        retry_rate=0,
        kind="pipeline",
        g2=False,
    ):
        counts = panel_budget(
            evaluations=e0,
            matching=1024,
            dimensions=dimensions,
            fit_dimensions=fit_dimensions,
            identity=identity,
            kind=kind,
            g2=g2,
        )
        total = counts["social"] * social + counts["null"] * null
        if not identity:
            extra = panel_budget(
                evaluations=e1,
                matching=4096,
                dimensions=dimensions,
                fit_dimensions=fit_dimensions,
                kind="match",
            )
            # Matching derivatives after a selected retry use M=4096, not 1024.
            fit_dim = dimensions if fit_dimensions is None else fit_dimensions
            if kind == "pipeline":
                extra["null"] += (
                    dimensions - fit_dim + (dimensions if g2 else 0)
                ) * 3072
            total += retry_rate * (extra["social"] * social + extra["null"] * null)
        return total * factor

    def rate(family, channel="observed", mobility=False):
        key = f"{family}:{channel}:{'mobility' if mobility else 'lags'}:"
        return rates[key + "social"], rates[key + "null"]

    scenarios = {}
    for label, retry_rate in (
        ("measured", empirical_retry),
        ("0.25", 0.25),
        ("1.0", 1.0),
    ):
        tiers = {str(t): 0.0 for t in range(1, 7)}
        for row in inventory["rows"]:
            options = row["options"]
            social, null = rate(
                row["family"], row["channel"], options.get("mobility", False)
            )
            if row["tier"] == 6:
                social, null = rates["steps24-social"], rates["steps24-null"]
            elif row["tier"] == 4:
                social = max(social, rates["c050"], rates["delta020"])
            elif row["tier"] == 5:
                social = max(social, rates["omega100"])
            dimensions = 1 if row["family"] in "AC" else 2
            tiers[str(row["tier"])] += cost(
                social,
                null,
                identity=row["a"] == 0
                and row["family"] != "C"
                and not options.get("anchor", 0),
                dimensions=dimensions,
                fit_dimensions=1 if row["channel"] != "observed" else dimensions,
                retry_rate=retry_rate,
            )
        gate = {"G0": 0.0}
        for family, channel in [(f, "observed") for f in "ABCDE"] + [
            ("B", c) for c in ("latent", "ordinal_one", "latent_rank")
        ]:
            social, null = rate(family, channel)
            for identity, count in ((False, 72), (family != "C", 9)):
                gate["G0"] += count * cost(
                    social,
                    null,
                    identity=identity,
                    dimensions=1 if family in "AC" or channel != "observed" else 2,
                    kind="match",
                    retry_rate=retry_rate,
                )
        social, null = rate("B")
        gate["G1b"] = factor * 5000 * 15.70
        gate["G1c"] = 150 * cost(rates["anchor-social"], rate("A")[1], identity=True)
        gate["G2"] = 700 * cost(social, null, retry_rate=retry_rate, g2=True)
        gate["G2c"] = 140 * cost(
            social, null, retry_rate=retry_rate, kind="refit"
        ) + 2 * cost(social, null, retry_rate=retry_rate)
        gate["score_bootstrap"] = factor * (852 / 9) * 15.70
        tiers["score_bootstrap"] = factor * 414 * 15.70
        scenarios[label] = dict(
            retry_fraction_assumed=retry_rate,
            gate_hours=gate,
            gate_total_hours=sum(gate.values()),
            tier_hours=tiers,
            tiers_1_5_hours=sum(tiers[str(t)] for t in range(1, 6)),
            total_hours=sum(gate.values()) + sum(tiers.values()),
        )
    result = dict(
        kind="v4.1-conditional-projection-not-allocation",
        supersedes="compute-projection-v41-pre-audit.json",
        correction=(
            "Charge the fixed social reference regenerated in each G2c task; "
            "seeds are shared, checkpoints are not."
        ),
        workers=8,
        reserve_fraction=0.25,
        close_utc="2026-10-19T02:59:00Z",
        rows=len(inventory["rows"]),
        comparison_r_units=414,
        solver_evaluations_assumed=[e0, e1],
        empirical_retry_fraction=empirical_retry,
        retry_evaluations_source="measured"
        if retries
        else "unobserved: conservative budget 64",
        cpu_seconds_per_panel=rates,
        scenarios=scenarios,
        inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limitations=[
            (
                "24 B fits at r=.70 proxy other cells, families and channels; zero "
                "retries does not imply zero study retry probability."
            ),
            (
                "8 dedicated workers, CPU/8 and 25% reserve; measured "
                "worker/coordinator wall times remain separate."
            ),
            (
                "Sealed panel checkpoints reuse fit baselines and the .01 matching "
                "stencil, verified by checkpoint tests; no sharing between distinct "
                "channel units."
            ),
            (
                "G2-only covariance stencils cost 24000 null panels per pipeline; "
                "confirmatory D5 has matching mean stencils only."
            ),
            (
                "D5 resampling/LDA and I/O/hashes/scheduling are not measured here; "
                "reserve is an assumption, not demonstrated overhead."
            ),
            (
                "Score bootstrap uses historical 15.70 seconds per nine slots; "
                "sensitivities use measured main null proxies."
            ),
            (
                "No tiers removed. Coordinator provisions same-code shards with "
                "numerical equivalence if needed; incomplete work follows D9."
            ),
        ],
    )
    with args.output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(scenarios, indent=2))


if __name__ == "__main__":
    main()
