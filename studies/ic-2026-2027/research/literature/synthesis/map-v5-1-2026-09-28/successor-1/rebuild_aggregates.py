"""Reconcile and reaggregate existing decisions; publish aggregate numbers only."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPOSITORY = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPOSITORY))
sys.path.insert(0, str(REPOSITORY / "workbench/src"))

from research_workbench.workflows.systematic_review.prioritized_stopping import (  # noqa: E402
    MappingSnapshot,
    assess_stopping,
    wilson_interval,
)
from research_workbench.workflows.systematic_review.v5_calibration_gate import (  # noqa: E402
    calculate_gate,
)
from research_workbench.workflows.systematic_review.v5_production import (  # noqa: E402
    category_report,
)

from scripts import v5_production as production  # noqa: E402

PACKAGE = Path(__file__).resolve().parent.parent
EXCLUSION_CODES = {
    "no_computational_model",
    "no_scholarly_product",
    "not_human_opinion_domain",
    "outside_date_or_language",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def rebuild(state_root: Path, coordinator: Path, output: Path) -> None:
    state = state_root / "production-v5-1"
    inputs: dict[Path, str] = {}

    def read_bytes(path: Path) -> bytes:
        path = path.resolve()
        if any(
            part.startswith("sealed-v4-") or part == "restricted" for part in path.parts
        ):
            raise ValueError("forbidden input")
        if not (
            path.is_relative_to(state_root)
            or (path.parent == coordinator and path.name.startswith("v5r2-"))
            or path.is_relative_to(PACKAGE)
        ):
            raise ValueError("input outside authorized roots")
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if path in inputs and inputs[path] != digest:
            raise ValueError("input changed during counting")
        inputs[path] = digest
        return raw

    def read_json(path: Path) -> Any:
        return json.loads(read_bytes(path))

    def read_rows(path: Path) -> list[dict[str, Any]]:
        return [json.loads(line) for line in read_bytes(path).splitlines() if line]

    def tracked_sha(path: Path) -> str:
        return hashlib.sha256(read_bytes(path)).hexdigest()

    production.PREPARATION = state_root / "preparation-conceptual-v5"
    production.read = read_json
    production.rows = read_rows
    production.sha = tracked_sha
    originals = {
        path: sha(path)
        for path in PACKAGE.rglob("*")
        if path.is_file() and not path.is_relative_to(PACKAGE / "successor-1")
    }
    run_record = (
        PACKAGE.parents[1] / "run-records/2026-09-28-broad-map-v5-1-production.md"
    )
    originals[run_record] = sha(run_record)
    historical = read_json(PACKAGE / "series.json")
    frame = {field: tuple(codes) for field, codes in historical["frame"].items()}
    if production.frame_codes(state) != frame:
        raise ValueError("production frame differs from published frame")
    phases = [
        state / "calibration-cohorts",
        state / "layer0",
        *(state / f"batch-{index:04}" for index in range(1, 15)),
        state / "remainder",
    ]
    adopted = {phase.name: production.effective_adopted(phase) for phase in phases}
    selected: set[str] = set()
    for phase in phases:
        ids = {row["work_id"] for row in adopted[phase.name]}
        if len(ids) != len(adopted[phase.name]) or selected & ids:
            raise ValueError("duplicate or overlapping phase selections")
        if phase.name != "calibration-cohorts":
            selection = read_json(phase / "selection.json")["items"]
            if len(selection) != len(ids) or {r["work_id"] for r in selection} != ids:
                raise ValueError("selection and adoption differ")
        selected.update(ids)
    for path in sorted(state.glob("identity-*/audit.json")):
        read_bytes(path)
        read_bytes(path.with_name("owner-decision.json"))
    included = {
        row["work_id"]
        for records in adopted.values()
        for row in records
        if row["judgment"] == "include"
    }
    mapping = production.resolved_work_ids(state, included)
    seen: set[str] = set()
    totals: Counter[str] = Counter()
    phase_counts = []
    for phase in phases:
        counts = Counter(row["judgment"] for row in adopted[phase.name])
        raw = Counter(row["judgment"] for row in read_rows(phase / "adopted.jsonl"))
        distinct = {
            mapping[row["work_id"]]
            for row in adopted[phase.name]
            if row["judgment"] == "include"
        }
        fresh = distinct - seen
        phase_counts.append(
            {
                "phase": phase.name,
                "screened": sum(counts.values()),
                "included_proposals": counts["include"],
                "excluded_proposals": counts["exclude"],
                "uncertain_proposals": counts["uncertain"],
                "within_phase_identity_reduction": counts["include"] - len(distinct),
                "overlap_with_prior_phases": len(distinct & seen),
                "identity_reduction": counts["include"] - len(fresh),
                "new_distinct_included": len(fresh),
                "cumulative_distinct_included": len(seen | distinct),
                "before_existing_recovery": dict(raw),
            }
        )
        totals.update(counts)
        seen.update(distinct)
    if (
        sum(totals.values()),
        totals["include"],
        len(seen),
        totals["exclude"],
        totals["uncertain"],
    ) != (8817, 4724, 4167, 1820, 2273):
        raise ValueError("production no longer reproduces historical flow")

    merged: dict[str, dict[str, Any]] = {}
    filtered_history: list[MappingSnapshot] = []
    successor_batches = []
    denominator_comparison = []
    batch_extractions = {}
    for phase in phases[2:-1]:
        extracts = read_rows(phase / "extractions.jsonl")
        recovery = phase.with_name(phase.name + "-recovery")
        if (recovery / "adopted.jsonl").exists():
            extracts += read_rows(recovery / "extractions.jsonl")
        batch_extractions[phase.name] = extracts
    secondary = {
        mapping[row["work_id"]]
        for extracts in batch_extractions.values()
        for row in extracts
        if "secondary" in row["fields"]["study_design"]["codes"]
    }
    if len(secondary) != 70:
        raise ValueError("final secondary cohort differs from published count")
    for index, phase in enumerate(phases[2:-1], 1):
        extracts = batch_extractions[phase.name]
        expected = {
            r["work_id"] for r in adopted[phase.name] if r["judgment"] == "include"
        }
        if (
            len(extracts) != len(expected)
            or {r["work_id"] for r in extracts} != expected
        ):
            raise ValueError("extraction coverage differs from adopted inclusions")
        for row in extracts:
            key = mapping[row["work_id"]]
            if key not in merged:
                merged[key] = {
                    "work_id": key,
                    "fields": {f: {"codes": []} for f in frame},
                }
            for field in frame:
                codes = set(merged[key]["fields"][field]["codes"])
                merged[key]["fields"][field]["codes"] = sorted(
                    codes | set(row["fields"][field]["codes"])
                )
        original_report = category_report(list(merged.values()), frame)
        original_counts = {
            f: {c: v["count"] for c, v in values.items()}
            for f, values in original_report.items()
        }
        original_batch = historical["batches"][index - 1]
        if (
            len(merged) != original_batch["included_primary"]
            or original_counts != original_batch["category_counts"]
        ):
            raise ValueError("reaggregation differs from original series")
        retained = [r for r in merged.values() if r["work_id"] not in secondary]
        filtered_report = category_report(retained, frame)
        filtered_counts = {
            f: {c: v["count"] for c, v in values.items()}
            for f, values in filtered_report.items()
        }
        filtered_history.append(
            MappingSnapshot(
                batch_index=index,
                frame_version=original_batch["frame_version"],
                included_work_ids=tuple(sorted(r["work_id"] for r in retained)),
                category_counts=filtered_counts,
                complete=True,
            )
        )
        successor_batches.append(
            {
                **original_batch,
                "included_primary": len(retained),
                "category_counts": filtered_counts,
            }
        )
        denominator_comparison.append(
            {
                "batch": index,
                "original": len(merged),
                "without_secondary": len(retained),
                "removed_secondary": len(merged) - len(retained),
            }
        )
    if (len(merged), len(retained)) != (4056, 3986):
        raise ValueError("secondary filter differs from reviewed denominator")
    comparisons = [
        {
            "field": field,
            "code": code,
            "original_count": original_report[field][code]["count"],
            "successor_count": value["count"],
            "original_denominator": 4056,
            "successor_denominator": 3986,
            "original_share": original_report[field][code]["proportion"],
            "successor_share": value["proportion"],
            "delta_pp": 100
            * (value["proportion"] - original_report[field][code]["proportion"]),
            "original_ci95": original_report[field][code]["ci95"],
            "successor_ci95": value["ci95"],
        }
        for field, values in filtered_report.items()
        for code, value in values.items()
    ]
    transitions = []
    for end in range(2, 15):
        result = assess_stopping(
            tuple(filtered_history[:end]), dimensions=tuple(frame), remainder_ids=()
        )
        transitions.append(
            {
                "from_batch": end - 1,
                "to_batch": end,
                "maximum_shift_pp": 100 * result.maximum_proportion_shifts[-1],
                "conditions_1_2": not (
                    set(result.reasons) - {"random_remainder_audit_required"}
                ),
            }
        )

    uncertain: Counter[str] = Counter()
    exclusion_reasons: Counter[str] = Counter()
    for phase in phases:
        if phase.name == "calibration-cohorts":
            availability = {
                r["work"]["work_id"]: any(item.get("abstract") for item in r["records"])
                for r in read_rows(coordinator / "v5r2-screener-tasks-a.jsonl")
            }
            screeners: dict[str, dict[str, Any]] = {}
            other_screeners: dict[str, dict[str, Any]] = {}
        else:
            availability = {
                r["work"]["work_id"]: any(item.get("abstract") for item in r["records"])
                for r in read_rows(phase / f"{phase.name}-screener-tasks-a.jsonl")
            }
            screeners = {r["work_id"]: r for r in read_rows(phase / "screener-a.jsonl")}
            other_screeners = {
                r["work_id"]: r for r in read_rows(phase / "screener-b.jsonl")
            }
            recovery = phase.with_name(phase.name + "-recovery")
            if (recovery / "adopted.jsonl").exists():
                tasks = read_rows(recovery / f"{recovery.name}-screener-tasks-a.jsonl")
                availability.update(
                    {
                        r["work"]["work_id"]: any(
                            item.get("abstract") for item in r["records"]
                        )
                        for r in tasks
                    }
                )
                screeners.update(
                    {r["work_id"]: r for r in read_rows(recovery / "screener-a.jsonl")}
                )
                other_screeners.update(
                    {r["work_id"]: r for r in read_rows(recovery / "screener-b.jsonl")}
                )
        for row in adopted[phase.name]:
            wid = row["work_id"]
            if row["judgment"] == "uncertain":
                group = (
                    "availability_unverified"
                    if wid not in availability
                    else "abstract_present"
                    if availability[wid]
                    else "no_abstract_in_bound_task"
                )
                uncertain[group] += 1
            if row["judgment"] == "exclude":
                a, b = screeners.get(wid, {}), other_screeners.get(wid, {})
                reason = a.get("decision", {}).get("reason_code")
                common = (
                    row.get("basis") == "A/B agreement"
                    and a.get("judgment") == b.get("judgment") == "exclude"
                    and reason == b.get("decision", {}).get("reason_code")
                    and reason in EXCLUSION_CODES
                )
                exclusion_reasons[
                    reason if common else "final_reason_not_verified"
                ] += 1

    references = read_rows(coordinator / "v5r2-references-adopted.jsonl")
    screener_a_rows = read_rows(coordinator / "v5r2-screener-a.jsonl")
    screener_b_rows = read_rows(coordinator / "v5r2-screener-b.jsonl")
    gate = json.loads(
        json.dumps(
            calculate_gate(
                [r["work_id"] for r in references],
                references,
                screener_a_rows,
                screener_b_rows,
            )
        )
    )
    if gate != read_json(coordinator / "v5r2-calibration-gate.json"):
        raise ValueError("calibration aggregate differs from recorded gate")
    positive_ids = {r["work_id"] for r in references if r["judgment"] == "include"}
    for role, predictions in [
        ("screener_a", screener_a_rows),
        ("screener_b", screener_b_rows),
    ]:
        exact = sum(
            r["work_id"] in positive_ids and r["judgment"] == "include"
            for r in predictions
        )
        gate["metrics"][role]["exact_include_count"] = exact
        gate["metrics"][role]["exact_include_wilson_95"] = wilson_interval(
            exact, len(positive_ids)
        )
    gate["reference_counts"] = dict(Counter(r["judgment"] for r in references))
    gate["by_decile"] = []
    cohort = read_json(coordinator / "v5r2-cohort.json")
    if len(cohort["items"]) != 200 or {item["work_id"] for item in cohort["items"]} != {
        r["work_id"] for r in references
    }:
        raise ValueError("calibration cohort differs from adopted references")
    for decile in sorted({item["decile"] for item in cohort["items"]}):
        ids = {item["work_id"] for item in cohort["items"] if item["decile"] == decile}
        stratum: dict[str, Any] = {
            "decile": decile,
            "works": len(ids),
            "reference_counts": dict(
                Counter(r["judgment"] for r in references if r["work_id"] in ids)
            ),
        }
        for role, rows in [
            ("screener_a", screener_a_rows),
            ("screener_b", screener_b_rows),
        ]:
            positives = {
                r["work_id"]
                for r in references
                if r["work_id"] in ids and r["judgment"] == "include"
            }
            stratum[role] = {
                "predicted_counts": dict(
                    Counter(r["judgment"] for r in rows if r["work_id"] in ids)
                ),
                "positive_predictions": dict(
                    Counter(r["judgment"] for r in rows if r["work_id"] in positives)
                ),
            }
        gate["by_decile"].append(stratum)

    scenarios = [
        {
            "numerator": found,
            "sample": 400,
            "remaining_unscreened": 35089,
            "point": 35089 * found / 400,
            "wilson95_scaled": [35089 * x for x in wilson_interval(found, 400)],
        }
        for found in (17, 118)
    ]
    if any(sha(path) != digest for path, digest in inputs.items()) or any(
        sha(path) != digest for path, digest in originals.items()
    ):
        raise ValueError("inputs or completed originals changed")
    output.mkdir(parents=True, exist_ok=False)
    save(
        output / "flow-reconciliation.json",
        {
            "phases": phase_counts,
            "totals": dict(totals),
            "included_distinct": len(seen),
            "identity_reduction": totals["include"] - len(seen),
            "uncertainty_availability": dict(uncertain),
            "exclusion_reasons": dict(exclusion_reasons),
            "proposals": 43906,
            "not_screened": 35089,
        },
    )
    save(
        output / "series-without-secondary.json",
        {
            **historical,
            "source": (
                "Existing adopted batch extractions; identity union then removal "
                "of the final secondary cohort from every prefix; "
                "eligibility corrections pending."
            ),
            "generated_for": (
                "successor-1, 2026-09-30; included_primary is an inherited "
                "schema key, not certified eligibility"
            ),
            "batches": successor_batches,
        },
    )
    save(output / "category-shares-without-secondary.json", filtered_report)
    save(output / "denominators-comparison.json", denominator_comparison)
    save(
        output / "stopping-comparison.json",
        {
            "transitions": transitions,
            "minimum_500_first_batch": next(
                s.batch_index
                for s in filtered_history
                if len(s.included_work_ids) >= 500
            ),
            "conditions_1_2_first_window_end": next(
                t["to_batch"] for t in transitions if t["conditions_1_2"]
            ),
            "condition_3_revalidated": False,
            "historical_audit_unresolved": 101,
            "stop": False,
            "audit_binding": (
                "historical snapshot only; not rebound to the filtered series"
            ),
            "remainder_scenarios": scenarios,
        },
    )
    save(output / "calibration-round2-aggregates.json", gate)
    with (output / "category-comparison.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)
    private_hashes = {}
    for path, digest in inputs.items():
        if path.is_relative_to(state_root):
            private_hashes["state/" + str(path.relative_to(state_root))] = digest
        elif path.parent == coordinator:
            private_hashes["coordinator/" + path.name] = digest
    save(
        output / "provenance.json",
        {
            "base_commit": "8c3f667d2c972126a4d8d943f8a3b615880eafc4",
            "script_sha256": sha(Path(__file__)),
            "integrated_modules_sha256": {
                name: sha(REPOSITORY / name)
                for name in [
                    "scripts/v5_production.py",
                    "scripts/v5_identity.py",
                    "workbench/src/research_workbench/workflows/systematic_review/v5_production.py",
                    "workbench/src/research_workbench/workflows/systematic_review/prioritized_stopping.py",
                    "workbench/src/research_workbench/workflows/systematic_review/prioritized_batches.py",
                    "workbench/src/research_workbench/workflows/systematic_review/v5_calibration_gate.py",
                ]
            },
            "private_inputs_sha256": private_hashes,
            "originals_sha256": {
                str(path.relative_to(REPOSITORY)): digest
                for path, digest in originals.items()
                if path.name != "README.md"
            },
            "private_inputs_unchanged": True,
            "originals_unchanged_during_counting": True,
            "original_series_reproduced": True,
            "outputs_sha256": {p.name: sha(p) for p in output.iterdir() if p.is_file()},
        },
    )
    print(
        json.dumps(
            {
                "screened": 8817,
                "included_proposals": 4724,
                "included_distinct": 4167,
                "identity_reduction": 557,
                "original_mapped": 4056,
                "without_secondary": 3986,
                "maximum_share_change_pp": max(abs(r["delta_pp"]) for r in comparisons),
                "last_two_shift_pp": [t["maximum_shift_pp"] for t in transitions[-2:]],
            }
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--coordinator", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rebuild(
        args.state_root.resolve(), args.coordinator.resolve(), args.output.resolve()
    )


if __name__ == "__main__":
    main()
