"""Summarize immutable calibration receipts without selecting successful refits."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    matching = [
        json.loads(p.read_text()) for p in sorted(args.raw.glob("match-*.json"))
    ]
    match_summary = []
    for a in (0.0, 0.03, 0.1):
        for n in (256, 1024):
            rows = [r for r in matching if r["share"] == a and r["count"] == n]
            if not rows:
                continue
            residual = np.abs(np.array([r["residual"] for r in rows]))
            paired = np.array([r["mc_se"] for r in rows])
            result = dict(
                share=a,
                matching=n,
                repeats=len(rows),
                strict_success=sum(r["success"] for r in rows),
                fixed_0003=int(np.all(residual <= 0.0003, axis=1).sum()),
                mean_paired_se=paired.mean(0).tolist(),
                mean_target_se=np.mean([r["target_se"] for r in rows], axis=0).tolist(),
                mean_worker_seconds=float(np.mean([r["seconds"] for r in rows])),
                mean_cpu_seconds=float(np.mean([r["cpu_seconds"] for r in rows])),
            )
            for k in (1, 2):
                result[f"posthoc_{k}se"] = int(
                    np.all(
                        residual <= np.minimum(0.0003, np.maximum(0.00005, k * paired)),
                        axis=1,
                    ).sum()
                )
            match_summary.append(result)
    refits: dict[str, Any] = {}
    for a, total in ((0.1, 40), (0.03, 20)):
        rows = {
            int(p.stem.rsplit("-", 1)[1]): json.loads(p.read_text())
            for p in args.raw.glob(f"refit-{a}-*.json")
        }
        successful = [r for r in rows.values() if r.get("stage") == "complete"]
        prefixes = []
        # Block 1 supplied the map origin; do not call it independent of that map.
        for b in (10, 20, 30, 39, 40):
            ids = list(range(2, b + 2))
            valid = all(i in rows and rows[i].get("stage") == "complete" for i in ids)
            record: dict[str, Any] = dict(
                count=b, blocks=ids, status="complete" if valid else "unavailable"
            )
            if valid:
                values = np.array([rows[i]["auc"] for i in ids])
                record.update(
                    variance=float(values.var(ddof=1)),
                    mean=float(values.mean()),
                    normal_relative_mc_se=math.sqrt(2 / (b - 1)),
                )
            prefixes.append(record)
        raw_prefixes = []
        for b in (10, 20, 40):
            if all(
                i in rows and rows[i].get("stage") == "complete"
                for i in range(1, b + 1)
            ):
                vals = np.array([rows[i]["auc"] for i in range(1, b + 1)])
                raw_prefixes.append(
                    dict(
                        count=b,
                        variance=float(vals.var(ddof=1)),
                        includes_map_development_block=True,
                    )
                )
        info: dict[str, Any] = dict(
            planned=total,
            returned=len(rows),
            successful=len(successful),
            failed_blocks=[b for b, r in rows.items() if r.get("stage") != "complete"],
            missing_blocks=[b for b in range(1, total + 1) if b not in rows],
            prefixes=prefixes,
            raw_prefixes=raw_prefixes,
            variance_exclusion=(
                "Block 1 supplied the map origin; excludes no numerical failures."
            ),
        )
        if successful:
            for key in (
                "seconds",
                "cpu_seconds",
                "matching_seconds",
                "training_seconds",
                "reference_seconds",
                "reference_se",
                "auc",
            ):
                values = np.array([r[key] for r in successful])
                info[key] = dict(
                    mean=float(values.mean()),
                    min=float(values.min()),
                    max=float(values.max()),
                )
            independent = np.array(
                [
                    rows[i]["auc"]
                    for i in sorted(rows)
                    if i != 1 and rows[i].get("stage") == "complete"
                ]
            )
            if len(independent) > 3 and independent.var() > 0:
                kurtosis = float(
                    np.mean((independent - independent.mean()) ** 4)
                    / independent.var() ** 2
                )
                info["tail_diagnostic"] = dict(
                    count=len(independent),
                    kurtosis=kurtosis,
                    approximate_relative_variance_se=math.sqrt(
                        max(kurtosis - 1, 0) / len(independent)
                    ),
                    approximate_count_for_25pct=math.ceil(
                        max(kurtosis - 1, 0) / 0.25**2
                    ),
                    interpretation=(
                        "Fourth-moment planning diagnostic; "
                        "not a sample-size guarantee."
                    ),
                )
            info["first_evaluation_stops"] = sum(
                r["evaluations"] == 1 for r in successful
            )
            info["panels_per_refit_mean"] = float(
                np.mean([256 * (1 + r["evaluations"]) + 8000 for r in successful])
            )
        refits[str(a)] = info
    extras = {
        p.stem: json.loads(p.read_text())
        for p in sorted(args.raw.glob("*.json"))
        if p.stem.startswith(
            (
                "diagnostic-",
                "stage-",
                "matching-map-",
                "additional-refit-",
                "compute-budget",
                "local-probe",
                "seed-audit",
                "throughput",
            )
        )
    }
    hashes = {
        str(p.relative_to(args.raw)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(args.raw.iterdir())
        if p.is_file()
    }
    report = dict(
        status="calibration_only_not_adopted",
        matching=match_summary,
        refits=refits,
        receipts=extras,
        raw_directory=str(args.raw),
        raw_hashes=hashes,
        matching_code_revision="719a83c",
        matching_revision_note=(
            "Driver recorded HEAD at stage end. Launch revision shown instead."
        ),
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(matching=match_summary, refits=refits), indent=2))


if __name__ == "__main__":
    main()
