"""Compare derived facts with 24 public synthetic rehearsals; never edit oracles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from ic_study.analysis.detection_v4_report import Inputs, load_inputs
from ic_study.analysis.v4_manuscript_assembly import _permitted, load_facts
from ic_study.analysis.v4_manuscript_assembly_derive import SHELL_BLOCKS, derive_facts
from ic_study.analysis.v4_manuscript_assembly_facts import DERIVABLE_FACTS

STUDY = Path(__file__).resolve().parents[4]
FIXTURES = STUDY / "tests/fixtures/v4_manuscript_assembly"
CRITERIA = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
RELEASE = Path("/private/tmp/release-day-combined.ya7qxzen")
G2C = Path("/private/tmp/g2c-failure-rehearsal.6Yk8Sb")
DRESS = Path("/private/tmp/dress-rehearsal.PFgUyQ")
NAMES = [
    r["name"]
    for r in json.loads((FIXTURES / "manual_oracles.json").read_text())["cases"]
]


def rehearsal_inputs(case: Path) -> Inputs:
    case = _permitted(case)
    paths: dict[str, Path] = {"gate-root": case / "gate"}
    record = case / "input-arguments.json"
    if record.exists():
        args = json.loads(_permitted(record).read_bytes())["a"]
    elif (record := case / "a-arguments.json").exists():
        args = json.loads(_permitted(record).read_bytes())
    else:
        args = []
        if (case / "G1c-successor.json").exists():
            paths["stage-successor"] = case / "G1c-successor.json"
    for i in range(0, len(args), 2):
        paths[args[i].removeprefix("--")] = _permitted(Path(args[i + 1]))
    return Inputs(
        paths.get("curves"),
        paths.get("gate-root"),
        paths.get("shp"),
        CRITERIA,
        paths.get("crosswalk"),
        (paths["stage-successor"],) if "stage-successor" in paths else (),
        paths.get("allocation"),
        paths.get("release-record"),
    )


def _hash(path: Path) -> str:
    return hashlib.sha256(_permitted(path).read_bytes()).hexdigest()


def compact_text(compact: dict[str, Any]) -> str:
    lines = ["{", '  "synthetic": true,']
    collections = ("cases", "gates", "profiles", "releases", "shp")
    for key in collections:
        lines.append(f'  "{key}": [')
        lines.append(
            ",\n".join(
                "    " + json.dumps(row, ensure_ascii=False, sort_keys=True)
                for row in compact[key]
            )
        )
        lines.append("  ]" + ("," if key != collections[-1] else ""))
    return "\n".join([*lines, "}", ""])


def audit() -> tuple[dict[str, Any], dict[str, Any]]:
    cases, differences = [], []
    compact: dict[str, Any] = {
        "synthetic": True,
        "profiles": [],
        "releases": [],
        "gates": [],
        "shp": [],
        "cases": [],
    }

    def intern(collection: str, obj: Any) -> int:
        rows = compact[collection]
        if obj not in rows:
            rows.append(obj)
        return int(rows.index(obj))

    for dataset, root, names in (
        ("release-day", RELEASE, [n for n in NAMES if "comparison" not in n]),
        ("g2c-failure", G2C, [n for n in NAMES if "comparison" in n]),
        ("dress", DRESS, NAMES),
    ):
        for name in names:
            inputs = rehearsal_inputs(root / name)
            derived = derive_facts(inputs, synthetic=True)
            fixture = FIXTURES / dataset / name / "assembly-facts.json"
            manual = load_facts(fixture)
            compared = []
            for fact, entry in derived["facts"].items():
                expected = manual["facts"].get(fact)
                compared.append(fact)
                if expected is None or expected["value"] != entry["value"]:
                    differences.append(
                        {
                            "dataset": dataset,
                            "case": name,
                            "fact": fact,
                            "manual": None if expected is None else expected["value"],
                            "derived": entry["value"],
                            "shell": "pipeline/drafts/2026-09-28/results-shells.tex",
                            "block": SHELL_BLOCKS[fact],
                        }
                    )
            loaded = load_inputs(inputs, synthetic=True)
            assert loaded.gate is not None
            summaries = list(loaded.gate.summaries.values())
            # Counts and aggregate predicates suffice; G0 per-fit diagnostic rows
            # are irrelevant to these facts and are not copied into the tests.
            summaries = [
                {k: v for k, v in s.items() if k != "matching_mask"} for s in summaries
            ]
            gate_id = intern("gates", summaries)
            release_id = shp_id = None
            if inputs.curves is not None:
                raw = json.loads(_permitted(inputs.curves).read_bytes())
                profiles = {}
                for curve in raw["curves"]:
                    record = {
                        k: v
                        for k, v in curve.items()
                        if k not in {"unit", "main_curve_valid", "cells"}
                    }
                    record["cells"] = [
                        {
                            "success": c["success"],
                            "attempts": [
                                {k: a[k] for k in ("status", "evaluations")}
                                for a in c["attempts"]
                            ],
                            **(
                                {"dependency_gap": c["dependency_gap"]}
                                if "dependency_gap" in c
                                else {}
                            ),
                        }
                        for c in curve["cells"]
                    ]
                    profiles[curve["unit"]] = intern("profiles", record)
                release_id = intern(
                    "releases",
                    {
                        "profiles": profiles,
                        "incomplete": {
                            r["unit"]: r["status"]
                            for r in raw["inventory"]["units"]
                            if r["unit"] not in profiles
                            and r["status"] != "não iniciado"
                        },
                    },
                )
            if inputs.shp is not None:
                raw = json.loads(_permitted(inputs.shp).read_bytes())
                shp_id = intern(
                    "shp",
                    {k: raw[k] for k in ("analysis", "anchor", "sensitivity_envelope")}
                    | {
                        "multiwave": {
                            k: raw["multiwave"][k]
                            for k in ("converged", "at_parameter_bound")
                        }
                    },
                )
            compact["cases"].append(
                {
                    "dataset": dataset,
                    "case": name,
                    "gate": gate_id,
                    "release": release_id,
                    "shp": shp_id,
                }
            )
            input_hashes = (
                {"gate/criteria.jsonl": _hash(inputs.gate_root / "criteria.jsonl")}
                if inputs.gate_root
                else {}
            )
            for path in (
                inputs.curves,
                inputs.release_record,
                inputs.shp,
                inputs.criteria,
                inputs.allocation,
                *inputs.successors,
            ):
                if path is not None:
                    input_hashes[path.name] = _hash(path)
            cases.append(
                {
                    "dataset": dataset,
                    "case": name,
                    "fixture_sha256": _hash(fixture),
                    "input_sha256": input_hashes,
                    "compared": compared,
                    "not_applicable": sorted(
                        (manual["facts"].keys() & DERIVABLE_FACTS)
                        - derived["facts"].keys()
                    ),
                    "derived": derived,
                }
            )
    here = Path(__file__).resolve()
    module = here.parents[4] / "src/ic_study/analysis/v4_manuscript_assembly_derive.py"
    return {
        "schema": "ic-study.v4-manuscript-assembly-derive-audit.v1",
        "synthetic": True,
        "scientific_acceptance": False,
        "auditor_sha256": _hash(here),
        "derivation_sha256": _hash(module),
        "facts_validator_sha256": _hash(
            module.with_name("v4_manuscript_assembly_facts.py")
        ),
        "synthetic_inputs_sha256": _hash(FIXTURES / "synthetic_inputs.json")
        if (FIXTURES / "synthetic_inputs.json").exists()
        else None,
        "shell_sha256": _hash(here.parents[1] / "drafts/2026-09-28/results-shells.tex"),
        "cases": cases,
        "case_count": len(cases),
        "comparison_count": sum(len(c["compared"]) for c in cases),
        "divergences": differences,
    }, compact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--write-synthetic-inputs", type=Path)
    args = parser.parse_args()
    report, compact = audit()
    for path, obj in [
        (args.report, report),
        *(
            ([(args.write_synthetic_inputs, compact)])
            if args.write_synthetic_inputs
            else []
        ),
    ]:
        with _permitted(path).open("x", encoding="utf-8") as stream:
            stream.write(
                compact_text(obj)
                if path == args.write_synthetic_inputs
                else json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            )
    print(
        json.dumps(
            {
                "report": str(args.report),
                "case_count": report["case_count"],
                "comparison_count": report["comparison_count"],
                "divergences": report["divergences"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
