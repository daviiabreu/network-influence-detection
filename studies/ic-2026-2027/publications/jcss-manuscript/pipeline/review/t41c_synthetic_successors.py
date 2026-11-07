"""Linked corrections of public rehearsal fixtures; never change an original."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from ic_study.analysis.v4_exploratory_export import NAMES
from ic_study.analysis.v4_manuscript_assembly import _permitted
from ic_study.simulation.v4_exploratory_x6 import coverage


def corrected_inputs(
    case: Path, destination: Path
) -> tuple[dict[str, Path], dict[str, Any]]:
    inputs: dict[str, Path] = {}
    receipt: dict[str, Any] = {
        "synthetic": True,
        "scientific_acceptance": False,
        "original": str(case),
        "changes": [],
        "inputs": {},
    }
    if not (case / "aggregates").is_dir():
        return inputs, receipt
    destination.mkdir(parents=True)
    for name in NAMES:
        source = _permitted(case / "aggregates" / f"{name}.json")
        raw = source.read_bytes()
        data = json.loads(raw)
        original = copy.deepcopy(data)
        assert data.get("synthetic") is True, "Only explicitly synthetic inputs"

        def replace(
            parent: dict[str, Any],
            key: str,
            value: Any,
            locator: str,
            input_name: str = name,
        ) -> None:
            if parent[key] != value:
                receipt["changes"].append(
                    {
                        "input": input_name,
                        "locator": locator,
                        "before": parent[key],
                        "after": value,
                    }
                )
                parent[key] = value

        if name == "x6":
            section = data["x6a"]
            for truth in ("vs_d1", "vs_pop"):
                if section["band"][truth] is None:
                    continue
                primary = section["band"][truth]["primary"]
                covered, complete = primary["covered"], primary["complete"]
                misses = section["band"][truth]["gaps_as_misses"]
                if misses["covered"] != covered:
                    replace(
                        section["band"][truth],
                        "gaps_as_misses",
                        coverage(
                            [True] * covered + [False] * (misses["total"] - covered),
                            complete_count=complete,
                        ),
                        f"/x6a/band/{truth}/gaps_as_misses",
                    )
                # The artificial joint failure is assigned to the a=0 marginal.
                # All other marginals keep their original complete-set coverage.
                marginals = [
                    row[truth]["band_interval"] for row in section["strengths"]
                ]
                if (
                    all(
                        m["complete"] == complete and m["covered"] == complete
                        for m in marginals
                    )
                    and covered < complete
                ):
                    local = section["strengths"][0][truth]
                    replace(
                        local,
                        "band_interval",
                        copy.deepcopy(primary),
                        f"/x6a/strengths/0/{truth}/band_interval",
                    )
                    replace(
                        local,
                        "pointwise",
                        copy.deepcopy(primary),
                        f"/x6a/strengths/0/{truth}/pointwise",
                    )
                    replace(
                        local,
                        "pointwise_gaps_as_misses",
                        coverage(
                            [True] * covered
                            + [False]
                            * (local["pointwise_gaps_as_misses"]["total"] - covered),
                            complete_count=complete,
                        ),
                        f"/x6a/strengths/0/{truth}/pointwise_gaps_as_misses",
                    )
        if name == "x7":
            for index, unit in enumerate(data["units"]):
                rich = unit.get("rich")
                if (
                    rich
                    and rich.get("first") == 0.03
                    and rich.get("first_interval") == [0.001, 0.01]
                    and rich.get("first_censoring") is None
                ):
                    replace(rich, "first", 0.003, f"/units/{index}/rich/first")
            assert [u.get("reading") for u in original["units"]] == [
                u.get("reading") for u in data["units"]
            ]
            receipt["x7_readings_unchanged"] = True
        if name == "x6":
            assert all(
                original["x6a"]["band"][truth] is None
                or original["x6a"]["band"][truth]["primary"]
                == data["x6a"]["band"][truth]["primary"]
                for truth in ("vs_d1", "vs_pop")
            )
            receipt["x6_primary_records_unchanged"] = True
        path = destination / f"{name}.json"
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        inputs[name] = path
        receipt["inputs"][name] = {
            "source": str(source),
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "successor": str(path),
            "successor_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    return inputs, receipt
