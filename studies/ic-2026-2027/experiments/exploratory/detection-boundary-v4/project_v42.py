"""V4.2 projection from optimized fits and historical panel timings."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import mean

EXPECTED_CELLS = {
    (0.6, 0.7),
    (0.9, 0.7),
    (0.03, 0.5),
    (0.3, 0.5),
    (0.03, 0.9),
    (0.3, 0.9),
}


def fit_accounting(rows):
    successes = sum(row["success"] for row in rows)
    return dict(
        planned=len(rows),
        validated_successes=successes,
        failures=len(rows) - successes,
        final_statuses=dict(
            sorted(Counter(row["attempts"][-1]["status"] for row in rows).items())
        ),
        attempt_statuses=dict(
            sorted(
                Counter(
                    attempt["status"] for row in rows for attempt in row["attempts"]
                ).items()
            )
        ),
    )


def evaluation_assumption(rows):
    all_mean = mean(row["attempts"][0]["evaluations"] for row in rows)
    successful = [row["attempts"][0]["evaluations"] for row in rows if row["success"]]
    successful_mean = mean(successful) if successful else None
    assumed = max(all_mean, successful_mean) if successful_mean is not None else 96
    return dict(
        all_planned_initial_mean=all_mean,
        final_validated_initial_mean=successful_mean,
        projected_initial_evaluations=assumed,
        policy="max(all-planned mean, final-validated mean); budget 96 if no successes",
    )


def paired_success_comparison(before, after):
    old = {(row["a"], row["r"], row["block"]): row for row in before}
    new = {(row["a"], row["r"], row["block"]): row for row in after}
    if old.keys() != new.keys():
        raise ValueError("Paired comparison requires identical planned blocks")
    pairs = [key for key in sorted(old) if old[key]["success"] and new[key]["success"]]

    def summary(keys, planned):
        return dict(
            planned_pairs=planned,
            validated_pairs=len(keys),
            excluded_pairs=planned - len(keys),
            before_initial_mean=mean(
                old[key]["attempts"][0]["evaluations"] for key in keys
            )
            if keys
            else None,
            after_initial_mean=mean(
                new[key]["attempts"][0]["evaluations"] for key in keys
            )
            if keys
            else None,
            before_total_mean=mean(
                sum(a["evaluations"] for a in old[key]["attempts"]) for key in keys
            )
            if keys
            else None,
            after_total_mean=mean(
                sum(a["evaluations"] for a in new[key]["attempts"]) for key in keys
            )
            if keys
            else None,
        )

    cells = {}
    for a, r in sorted({key[:2] for key in old}):
        keys = [key for key in pairs if key[:2] == (a, r)]
        cells[f"a={a:g},r={r:g}"] = dict(
            blocks=[key[2] for key in keys],
            **summary(keys, sum(key[:2] == (a, r) for key in old)),
        )
    return dict(
        **summary(pairs, len(old)),
        cells=cells,
        interpretation=(
            "Conditional comparison on paired final validations; gaps remain counted"
        ),
    )


def summarize_fits(rows):
    cells = {}
    for row in rows:
        key = f"a={row['a']:g},r={row.get('r', 0.7):g}"
        cells.setdefault(key, []).append(row)
    summary = {}
    for key, group in sorted(cells.items()):
        evaluations = [row["attempts"][0]["evaluations"] for row in group]
        summary[key] = dict(
            blocks=len(group),
            first_attempt_evaluations=evaluations,
            mean_evaluations=mean(evaluations),
            min_evaluations=min(evaluations),
            max_evaluations=max(evaluations),
            validation_successes=sum(row["success"] for row in group),
            outcome_accounting=fit_accounting(group),
            retries=sum(len(row["attempts"]) > 1 for row in group),
        )
    return summary


def validate_complete_comparison(before, after):
    key_sets = []
    for record in (before, after):
        rows = record["measurements"]
        keys = [(row["a"], row["r"], row["block"]) for row in rows]
        if len(set(keys)) != len(keys):
            raise ValueError("Duplicate matching block")
        if {(key[0], key[1]) for key in keys} != EXPECTED_CELLS:
            raise ValueError("Matching comparison must contain all six declared cells")
        if any(sum(key[:2] == cell for key in keys) < 4 for cell in EXPECTED_CELLS):
            raise ValueError("Matching comparison needs at least four blocks per cell")
        if record.get("classifiers_trained") != 0:
            raise ValueError("Projection requires matching-only measurements")
        key_sets.append(set(keys))
    if key_sets[0] != key_sets[1]:
        raise ValueError("Before/after matching blocks must be paired")


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


def build_projection(here):
    paths = [
        here / n
        for n in (
            "panel-cost-v41.json",
            "cost-fits-v42-after.json",
            "inventory.json",
            "cost-fits-v42-before.json",
            "cost-fits-v41.json",
        )
    ]
    panels, fits, inventory, before, historical = [
        json.loads(p.read_text()) for p in paths
    ]
    validate_complete_comparison(before, fits)
    rates = {
        r["operation"]: r["cpu_seconds"] / r["panels"] for r in panels["measurements"]
    }
    rows = fits["measurements"]
    retries = [r["attempts"][1]["evaluations"] for r in rows if len(r["attempts"]) == 2]
    assumption = evaluation_assumption(rows)
    e0 = assumption["projected_initial_evaluations"]
    e1 = mean(retries) if retries else 96
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
        kind="v4.2-conditional-projection-not-allocation",
        schema_version=2,
        supersedes="compute-projection-v41.json",
        correction=(
            "Use optimized matching evaluations only and budget 96 per attempt; "
            "charge both G2c references regenerated with baseline seeds."
        ),
        workers=8,
        reserve_fraction=0.25,
        close_utc="2026-10-19T02:59:00Z",
        rows=len(inventory["rows"]),
        comparison_r_units=414,
        solver_evaluations_assumed=[e0, e1],
        initial_evaluation_assumption=assumption,
        all_planned_outcomes=dict(
            before=fit_accounting(before["measurements"]), after=fit_accounting(rows)
        ),
        paired_success_comparison=paired_success_comparison(
            before["measurements"], rows
        ),
        solver_evaluation_budget_per_attempt=96,
        optimized_matching_summary=summarize_fits(rows),
        before_matching_summary=summarize_fits(before["measurements"]),
        historical_matching_summary=summarize_fits(historical["measurements"]),
        panel_timing_source="panel-cost-v41.json",
        evaluation_count_source="cost-fits-v42-after.json",
        matching_panel_accounting=dict(
            measured_uncached_null_overhead_per_attempt=3,
            projected_cached_null_overhead_per_attempt="fit_dimensions",
            solver_finite_difference_evaluations="included in measured evaluations",
            cached_final_fit_baseline="already counted among solver evaluations",
        ),
        empirical_retry_fraction=empirical_retry,
        retry_evaluations_source="measured"
        if retries
        else "unobserved: conservative budget 96",
        cpu_seconds_per_panel=rates,
        scenarios=scenarios,
        inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        limitations=[
            (
                "Projected successful work uses the larger initial-evaluation mean "
                "across all planned fits and final-validated fits; no successful "
                "fits implies budget 96. Early gaps cannot discount successful work."
            ),
            (
                "24 optimized B fits, 4 blocks at each of six declared cells, proxy "
                "unmeasured strengths, families and channels; zero retries does not "
                "imply zero study retry probability. Old evaluations are not pooled."
            ),
            (
                "Historical panel CPU rates remain separate from optimized "
                "evaluations. "
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
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_projection(Path(__file__).parent)
    with args.output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["scenarios"], indent=2))


if __name__ == "__main__":
    main()
