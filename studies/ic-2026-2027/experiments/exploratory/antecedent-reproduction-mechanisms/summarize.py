"""Summarize immutable exploratory JSON outputs without changing them."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def mean(values: list[float]) -> float:
    return statistics.mean(values)


def runtime(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "median": statistics.median(ordered),
        "p95_nearest_rank": ordered[(95 * len(ordered) + 99) // 100 - 1],
        "maximum": ordered[-1],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    directory = args.directory
    controls = json.loads((directory / "controls-results-v3.json").read_text())
    antecedents = json.loads((directory / "antecedents-results-v2.json").read_text())
    thompsky = json.loads((directory / "thompsky-proxy-results.json").read_text())
    pairs: list[dict[str, Any]] = controls["pairs"]
    trios: list[dict[str, Any]] = controls["trios"]
    pair_summary = []
    for coupling in (0.0, 0.4):
        for mode in ("uniform", "expected", "adaptive"):
            rows = [
                row
                for row in pairs
                if row["coupling"] == coupling and row["mode"] == mode
            ]
            pair_summary.append(
                {
                    "coupling": coupling,
                    "mode": mode,
                    "mse_topic2_wrong_mean": mean(
                        [row["mse_topic2_wrong"] for row in rows]
                    ),
                    "between_contacts_mean": mean(
                        [row["between_contacts"] for row in rows]
                    ),
                    "runtime_seconds": runtime(
                        [row["elapsed_seconds"] for row in rows]
                    ),
                }
            )
    trio_summary = []
    for wrong in (True, False):
        for source in (False, True):
            for nonlinear in (False, True):
                for projected in (False, True):
                    rows = [
                        row
                        for row in trios
                        if row["wrong_majority"] == wrong
                        and row["source"] == source
                        and row["nonlinear"] == nonlinear
                        and row["projected"] == projected
                    ]
                    trio_summary.append(
                        {
                            "wrong_majority": wrong,
                            "source": source,
                            "nonlinear": nonlinear,
                            "projected": projected,
                            "mse_mean": mean([row["mse"] for row in rows]),
                            "mean_opinion": mean([row["mean"] for row in rows]),
                            "variance_mean": mean([row["variance"] for row in rows]),
                            "runtime_seconds": runtime(
                                [row["elapsed_seconds"] for row in rows]
                            ),
                        }
                    )
    proxy_summary = []
    for topology in ("complete", "cycle"):
        for adaptive in (False, True):
            rows = [
                row
                for row in thompsky["rows"]
                if row["topology"] == topology and row["adaptive"] == adaptive
            ]
            observed = [
                row["settled_at"] for row in rows if row["settled_at"] is not None
            ]
            proxy_summary.append(
                {
                    "topology": topology,
                    "adaptive": adaptive,
                    "settled_mean": mean(observed) if observed else None,
                    "censored": len(rows) - len(observed),
                    "runtime_seconds": runtime(
                        [row["elapsed_seconds"] for row in rows]
                    ),
                }
            )
    dong_rows = antecedents["dong"]["results"]
    result = {
        "status": "exploratory_summary",
        "pair": pair_summary,
        "trio": trio_summary,
        "thompsky_proxy": proxy_summary,
        "dong": [
            {
                "p": p,
                "P_mean": mean([row["P"] for row in dong_rows if row["p"] == p]),
                "absC_mean": mean([row["absC"] for row in dong_rows if row["p"] == p]),
                "runtime_seconds": runtime(
                    [row["elapsed_seconds"] for row in dong_rows if row["p"] == p]
                ),
            }
            for p in (1, 2)
        ],
        "neuhauser": antecedents["neuhauser"],
        "abed": antecedents["abed"],
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
