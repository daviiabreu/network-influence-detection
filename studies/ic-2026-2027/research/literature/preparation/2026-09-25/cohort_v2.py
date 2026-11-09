"""Offline, fail-closed exposure inventory and post-C4 cohort ordering."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

SEED = 20260924
PREFIX = "calibration-cohort-v2-20260924:"
SUITE_SHA256 = "efaf237f3ab0b028bd82ca5a92c43bde25d350cf7ad2d308a4808b9ef5ae7f81"


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path, expected: str | None = None) -> tuple[dict, str]:
    raw = path.read_bytes()
    actual = digest(raw)
    if expected and actual != expected:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return json.loads(raw), actual


def write_private(path: Path, value: dict) -> str:
    if path.exists() or path.is_symlink():
        raise ValueError(f"create-once output exists: {path}")
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.parent.stat().st_mode & 0o077:
        raise ValueError("output directory must be mode 0700")
    raw = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as output:
        output.write(raw)
    return digest(raw)


def task_work(case: dict) -> dict:
    return case["task"]["payload"]["agent_task"]["work"]


def build_strata(receipt_path: Path, projection_path: Path, records_path: Path) -> dict:
    receipt, receipt_sha = read_json(receipt_path)
    projection, projection_sha = read_json(projection_path)
    records, records_sha = read_json(records_path)
    if (
        receipt.get("schema_version") != "corpus-screening-bridge-2"
        or receipt.get("outcome", {}).get("status") != "completed"
        or projection.get("schema_version") != "corpus-screening-projection-2"
        or receipt["projection"]["sha256"] != projection_sha
        or receipt["original_records"]["sha256"] != records_sha
        or receipt["work_count"] != len(projection["works"])
    ):
        raise ValueError("C4 receipt, projection, and original records differ")
    if not isinstance(records, list):
        raise ValueError("original records must be a native list")
    by_id = {row["record_id"]: row for row in records}
    if len(by_id) != len(records):
        raise ValueError("duplicate original record")
    representatives = []
    for work in projection["works"]:
        choices = []
        for record_id in work["manifestation_record_ids"]:
            row = by_id.get(record_id)
            if row is None:
                raise ValueError("C4 manifestation lacks original record")
            match = re.fullmatch(
                r"search\.(openalex|arxiv|dblp)\.q(\d{2})[abc]?",
                row["search_id"],
            )
            if match and 1 <= int(match[2]) <= 16:
                choices.append((match[2], match[1], record_id, row))
        if choices:
            family, source, record_id, row = min(choices)
        else:
            record_id = min(work["manifestation_record_ids"])
            row = by_id[record_id]
            family, source = None, row["source_id"]
        representatives.append(
            {
                "work_id": work["work_id"],
                "manifestation_record_id": record_id,
                "original_page_sha256": row["raw_artifact_sha256"],
                "bibliographic_page_sha256": sorted(
                    {
                        by_id[item]["raw_artifact_sha256"]
                        for item in work["manifestation_record_ids"]
                    }
                ),
                "family": f"Q{family}" if family else None,
                "source": source,
                "abstract_present": bool(row.get("abstract")),
                "underrepresented": bool(
                    row.get("publication_year") and int(row["publication_year"]) < 1995
                ),
                "identity_pending": False,
                "possible_alias": False,
                "full_text_sha256": [],
            }
        )
    return {
        "schema_version": "cohort-v2-c4-strata-1",
        "c4_receipt_sha256": receipt_sha,
        "c4_projection_sha256": projection_sha,
        "original_records_sha256": records_sha,
        "representatives": representatives,
    }


def build_inventory(
    suite_path: Path,
    extra_suites: list[Path],
    legacy_path: Path | None = None,
    dedup_path: Path | None = None,
    observations_path: Path | None = None,
) -> dict:
    sources = []
    exposures = defaultdict(
        lambda: {
            "identifiers": set(),
            "manifestations": set(),
            "bibliographic_page_sha256": set(),
            "full_text_sha256": set(),
            "tasks": [],
        }
    )
    for path in [suite_path, *extra_suites]:
        suite, sha = read_json(path, SUITE_SHA256 if path == suite_path else None)
        if path == suite_path and len(suite["cases"]) != 101:
            raise ValueError("development suite must contain 101 cases")
        sources.append(
            {"path": str(path), "sha256": sha, "case_count": len(suite["cases"])}
        )
        for case in suite["cases"]:
            task = case["task"]["payload"]["agent_task"]
            work = task_work(case)
            row = exposures[work["work_id"]]
            row["identifiers"].update(value.casefold() for value in work["identifiers"])
            row["manifestations"].update(work["manifestation_record_ids"])
            row["bibliographic_page_sha256"].update(
                record["raw_artifact_sha256"] for record in task.get("records", [])
            )
            if task.get("full_text_artifact_sha256"):
                row["full_text_sha256"].add(task["full_text_artifact_sha256"])
            row["tasks"].append(
                {
                    "source_sha256": sha,
                    "case_id": case["case_id"],
                    "role": case["role"],
                    "stage": task.get("stage", "extraction"),
                }
            )
    if legacy_path is not None:
        if dedup_path is None or observations_path is None:
            raise ValueError("legacy exposure requires deduplication and observations")
        legacy, legacy_sha = read_json(legacy_path)
        dedup, dedup_sha = read_json(dedup_path)
        observations, observations_sha = read_json(observations_path)
        by_id = {row["work_id"]: row for row in dedup["titled_works"]}
        by_observation = {
            row["observation_id"]: row for row in observations["observations"]
        }
        for case in legacy["cases"]:
            for wid in case["v3_all_manifestation_work_ids"]:
                work = by_id.get(wid)
                if work is None:
                    raise ValueError("legacy work absent from original deduplication")
                row = exposures[wid]
                row["identifiers"].update(x.casefold() for x in work["identifiers"])
                row["manifestations"].update(work["manifestation_record_ids"])
                row["bibliographic_page_sha256"].update(
                    by_observation[record_id]["origin"]["raw_artifact_sha256"]
                    for record_id in work["manifestation_record_ids"]
                )
                row["tasks"].append(
                    {
                        "source_sha256": legacy_sha,
                        "case_id": str(case.get("case_id", wid)),
                        "role": "legacy_calibration",
                        "stage": "title_abstract",
                    }
                )
        sources.extend(
            [
                {
                    "path": str(legacy_path),
                    "sha256": legacy_sha,
                    "case_count": len(legacy["cases"]),
                },
                {
                    "path": str(dedup_path),
                    "sha256": dedup_sha,
                    "kind": "identity_lookup",
                },
                {
                    "path": str(observations_path),
                    "sha256": observations_sha,
                    "kind": "page_lookup",
                },
            ]
        )
    rows = []
    for work_id, row in sorted(exposures.items()):
        rows.append(
            {
                "work_id": work_id,
                "identifiers": sorted(row["identifiers"]),
                "manifestations": sorted(row["manifestations"]),
                "bibliographic_page_sha256": sorted(row["bibliographic_page_sha256"]),
                "full_text_sha256": sorted(row["full_text_sha256"]),
                "tasks": sorted(
                    row["tasks"],
                    key=lambda value: (value["source_sha256"], value["case_id"]),
                ),
            }
        )
    return {
        "schema_version": "cohort-v2-exposure-inventory-1",
        "complete": False,
        "closure_reason": (
            "Other model-visible task stores and C4 identity successors require audit"
        ),
        "sources": sources,
        "works": rows,
    }


def sample(
    receipt_path: Path,
    projection_path: Path,
    records_path: Path,
    strata_path: Path,
    inventory_path: Path,
    output: Path,
) -> dict:
    receipt, receipt_sha = read_json(receipt_path)
    projection, projection_sha = read_json(projection_path)
    expected_strata = build_strata(receipt_path, projection_path, records_path)
    strata_input, strata_sha = read_json(strata_path)
    inventory, inventory_sha = read_json(inventory_path)
    if not inventory.get("complete"):
        raise ValueError("exposure inventory is not closed")
    if receipt.get("schema_version") != "corpus-screening-bridge-2":
        raise ValueError("native C4 bridge v2 receipt required")
    if receipt["projection"]["sha256"] != projection_sha or receipt[
        "work_count"
    ] != len(projection["works"]):
        raise ValueError("C4 projection does not match receipt")
    if projection.get("schema_version") != "corpus-screening-projection-2":
        raise ValueError("native C4 projection required")
    if receipt["outcome"]["status"] != "completed":
        raise ValueError("C4 must be completed")
    exposed = inventory["works"]
    exposed_ids = {row["work_id"] for row in exposed}
    exposed_identifiers = {item for row in exposed for item in row["identifiers"]}
    exposed_manifestations = {item for row in exposed for item in row["manifestations"]}
    exposed_pages = {
        item for row in exposed for item in row["bibliographic_page_sha256"]
    }
    joins = {row["work_id"]: row for row in projection["joins"]}
    if len(joins) != len(projection["works"]):
        raise ValueError("C4 joins are incomplete")
    if (
        strata_input.get("schema_version") != "cohort-v2-c4-strata-1"
        or strata_input.get("c4_receipt_sha256") != receipt_sha
        or strata_input.get("c4_projection_sha256") != projection_sha
        or strata_input.get("original_records_sha256")
        != expected_strata["original_records_sha256"]
    ):
        raise ValueError("source-bound C4 stratum input required")
    representatives = {row["work_id"]: row for row in strata_input["representatives"]}
    original_representatives = {
        row["work_id"]: row for row in expected_strata["representatives"]
    }
    if representatives.keys() != original_representatives.keys():
        raise ValueError("representative coverage or uniqueness differs from C4")
    source_fields = (
        "manifestation_record_id",
        "original_page_sha256",
        "bibliographic_page_sha256",
        "family",
        "source",
        "abstract_present",
        "underrepresented",
    )
    for wid, value in representatives.items():
        if any(
            value.get(field) != original_representatives[wid][field]
            for field in source_fields
        ):
            raise ValueError("stratum source differs from C4 original records")
    strata: dict[str, list[dict]] = defaultdict(list)
    refusals = []
    exposed_text = {item for row in exposed for item in row["full_text_sha256"]}
    for work in projection["works"]:
        wid = work["work_id"]
        reasons = []
        if wid in exposed_ids or set(joins[wid]["source_work_ids"]) & exposed_ids:
            reasons.append("exposed_identity")
        if {x.casefold() for x in work["identifiers"]} & exposed_identifiers:
            reasons.append("exposed_identifier")
        if set(work["manifestation_record_ids"]) & exposed_manifestations:
            reasons.append("exposed_manifestation")
        representative = representatives.get(wid)
        if representative is None:
            raise ValueError("C4 work lacks representative")
        if representative.get("identity_pending") or representative.get(
            "possible_alias"
        ):
            reasons.append("identity_or_alias_pending")
        if set(representative["bibliographic_page_sha256"]) & exposed_pages:
            reasons.append("exposed_bibliographic_page")
        if representative["family"] is None:
            reasons.append("no_Q01_Q16_representative")
        if set(representative.get("full_text_sha256", [])) & exposed_text:
            reasons.append("exposed_full_text")
        if reasons:
            refusals.append({"work_id": wid, "reasons": reasons})
            continue
        if (
            representative["manifestation_record_id"]
            not in work["manifestation_record_ids"]
        ):
            raise ValueError("representative is not a C4 manifestation")
        if not representative.get("original_page_sha256"):
            raise ValueError("representative lacks original page hash")
        family = representative["family"]
        source = representative["source"]
        abstract = "present" if representative["abstract_present"] else "absent"
        if family not in {f"Q{i:02d}" for i in range(1, 17)} or source not in {
            "openalex",
            "arxiv",
            "dblp",
        }:
            raise ValueError("invalid representative stratum")
        strata[f"{family}/{source}/{abstract}"].append(work)
    order = {
        key: [
            w["work_id"]
            for w in sorted(
                values,
                key=lambda w: (digest((PREFIX + w["work_id"]).encode()), w["work_id"]),
            )
        ]
        for key, values in sorted(strata.items())
    }
    source_targets = {"openalex": 52, "arxiv": 56, "dblp": 92}
    source_counts: Counter[str] = Counter()
    abstract_counts: Counter[bool] = Counter()
    chosen: list[str] = []
    chosen_set: set[str] = set()
    missing: dict[str, int] = {}

    def key_for(wid: str) -> tuple[str, str]:
        return digest((PREFIX + wid).encode()), wid

    def pick(options: list[str]) -> str:
        return min(
            options,
            key=lambda wid: (
                source_counts[representatives[wid]["source"]]
                / source_targets[representatives[wid]["source"]],
                abstract_counts[bool(representatives[wid]["abstract_present"])],
                *key_for(wid),
            ),
        )

    def add(wid: str) -> None:
        chosen.append(wid)
        chosen_set.add(wid)
        source_counts[representatives[wid]["source"]] += 1
        abstract_counts[bool(representatives[wid]["abstract_present"])] += 1

    for number in range(1, 17):
        family = f"Q{number:02d}"
        members = [
            wid
            for bucket in order.values()
            for wid in bucket
            if representatives[wid]["family"] == family
        ]
        for _ in range(12):
            available = [wid for wid in members if wid not in chosen_set]
            if not available:
                missing[family] = 12 - sum(
                    representatives[wid]["family"] == family for wid in chosen
                )
                break
            add(pick(available))
    extras = [
        wid
        for bucket in order.values()
        for wid in bucket
        if wid not in chosen_set and representatives[wid].get("underrepresented", False)
    ]
    underrepresented_selected = 0
    while extras and underrepresented_selected < 8:
        wid = pick(extras)
        add(wid)
        underrepresented_selected += 1
        extras.remove(wid)
    remaining = [
        wid for bucket in order.values() for wid in bucket if wid not in chosen_set
    ]
    remaining.sort(key=key_for)
    for wid in remaining:
        add(wid)
    waves = [chosen[index : index + 50] for index in range(0, len(chosen), 50)]
    manifest = {
        "schema_version": "cohort-v2-order-1",
        "seed": SEED,
        "ordering_rule": (
            'SHA-256("calibration-cohort-v2-20260924:" + work_id), '
            "work_id within each stratum"
        ),
        "inputs": {
            "c4_receipt_sha256": receipt_sha,
            "c4_projection_sha256": projection_sha,
            "original_records_sha256": expected_strata["original_records_sha256"],
            "strata_sha256": strata_sha,
            "exposure_inventory_sha256": inventory_sha,
        },
        "stratum_order": order,
        "refusals": refusals,
        "missing_family_slots": missing,
        "underrepresented_selected": underrepresented_selected,
        "missing_underrepresented_slots": max(0, 8 - underrepresented_selected),
        "observed_representatives_initial_200": dict(
            Counter(representatives[wid]["source"] for wid in chosen[:200])
        ),
        "observed_abstract_present_initial_200": sum(
            bool(representatives[wid]["abstract_present"]) for wid in chosen[:200]
        ),
        "waves": waves,
        "selection_status": "predeclared_waves_pending_reference_counts",
        "wave_size": 50,
        "targets": {
            "family_per_Q01_Q16": 12,
            "underrepresented": 8,
            "initial_total": 200,
            "representatives": source_targets,
            "abstract_fraction": 0.5,
        },
    }
    write_private(output, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory")
    inventory.add_argument("--development-suite", type=Path, required=True)
    inventory.add_argument("--extra-suite", action="append", type=Path, default=[])
    inventory.add_argument("--legacy-audit", type=Path)
    inventory.add_argument("--dedup", type=Path)
    inventory.add_argument("--observations", type=Path)
    inventory.add_argument("--output", type=Path, required=True)
    strata = commands.add_parser("strata")
    strata.add_argument("--c4-receipt", type=Path, required=True)
    strata.add_argument("--c4-projection", type=Path, required=True)
    strata.add_argument("--original-records", type=Path, required=True)
    strata.add_argument("--output", type=Path, required=True)
    sampler = commands.add_parser("sample")
    sampler.add_argument("--c4-receipt", type=Path, required=True)
    sampler.add_argument("--c4-projection", type=Path, required=True)
    sampler.add_argument("--original-records", type=Path, required=True)
    sampler.add_argument("--c4-strata", type=Path, required=True)
    sampler.add_argument("--inventory", type=Path, required=True)
    sampler.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    if args.command == "inventory":
        print(
            write_private(
                args.output,
                build_inventory(
                    args.development_suite,
                    args.extra_suite,
                    args.legacy_audit,
                    args.dedup,
                    args.observations,
                ),
            )
        )
    elif args.command == "strata":
        print(
            write_private(
                args.output,
                build_strata(
                    args.c4_receipt, args.c4_projection, args.original_records
                ),
            )
        )
    else:
        print(
            json.dumps(
                {
                    "strata": len(
                        sample(
                            args.c4_receipt,
                            args.c4_projection,
                            args.original_records,
                            args.c4_strata,
                            args.inventory,
                            args.output,
                        )["stratum_order"]
                    )
                }
            )
        )


if __name__ == "__main__":
    main()
