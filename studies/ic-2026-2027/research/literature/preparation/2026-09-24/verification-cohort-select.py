"""Prepare an unlabelled, source-bound candidate cohort from retained v3 bytes.

This script makes no research decisions and never calls an executor or network.
Outputs are create-once private files; rerun with a fresh output directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import unicodedata
from collections import Counter
from pathlib import Path

DEDUP_SHA = "41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53"
PROJECTION_SHA = "93c8086aa6b0231fd019291f9bb3984e5e436e629c4424e95ae499729957cc85"
REPORT_SHA = "edfa48474097d7c81e441fdbe5089a924d514deabbb6baf3bbaf60e0df220a11"
SEED = "20260924-verification-candidates-v1"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def normalized_title(value: str | None) -> str:
    return " ".join(unicodedata.normalize("NFKC", value or "").casefold().split())


def load_json(path: Path, expected_sha: str | None = None):
    raw = path.read_bytes()
    if expected_sha is not None and sha(raw) != expected_sha:
        raise ValueError(f"source hash mismatch: {path}")
    return json.loads(raw), sha(raw)


def load_cas(root: Path, digest: str):
    return load_json(root / "sha256" / digest[:2] / digest[2:4] / digest, digest)[0]


def write_once(path: Path, value) -> str:
    raw = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw)
    return sha(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--private-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repository_root.resolve(strict=True)
    base = args.private_root.resolve(strict=True)
    out = args.output
    if (
        out.exists()
        or out.is_symlink()
        or out.parent.resolve(strict=True) != Path("/private/tmp")
    ):
        raise ValueError("output must be a new direct child of /private/tmp")
    os.umask(0o077)

    cas = base / "acquisition-v3" / "artifacts"
    dedup = load_cas(cas, DEDUP_SHA)
    projection = load_cas(cas, PROJECTION_SHA)
    report = load_cas(cas, REPORT_SHA)
    prior_path = (
        base
        / "calibration-preparation-v3-extraction-20260913"
        / "corpus-selection.json"
    )
    prior, prior_sha = load_json(prior_path)
    legacy_path = base / "calibration-rebinding-audit-20260913.json"
    legacy, legacy_sha = load_json(legacy_path)
    suite_path = (
        base.parent
        / "autonomous-review-20260915"
        / "development-calibration-3044d04"
        / "suite.json"
    )
    suite, suite_sha = load_json(suite_path)
    if suite_sha != "efaf237f3ab0b028bd82ca5a92c43bde25d350cf7ad2d308a4808b9ef5ae7f81":
        raise ValueError("development suite hash changed")
    prior_ids = {entry["work"]["work_id"] for entry in prior["entries"]}
    suite_ids = {
        case["task"]["payload"]["agent_task"]["work"]["work_id"]
        for case in suite["cases"]
    }
    if suite_ids != prior_ids or len(suite_ids) != 50:
        raise ValueError("development suite and prior selection differ")
    legacy_ids = {
        work_id
        for case in legacy["cases"]
        for work_id in case["v3_all_manifestation_work_ids"]
    }
    if len(legacy["cases"]) != 50:
        raise ValueError("legacy reservation count changed")
    exposed_ids = prior_ids | legacy_ids
    by_id = {row["observation_id"]: row for row in projection["observations"]}
    if len(by_id) != len(projection["observations"]):
        raise ValueError("duplicate observation ID")
    works = dedup["titled_works"]
    works_by_id = {work["work_id"]: work for work in works}
    if len(works_by_id) != len(works):
        raise ValueError("duplicate proposed work ID")
    if not exposed_ids <= works_by_id.keys():
        raise ValueError("exposed work missing from retained deduplication")

    exposed_pages = {
        by_id[record_id]["origin"]["raw_artifact_sha256"]
        for work_id in exposed_ids
        for record_id in works_by_id[work_id]["manifestation_record_ids"]
    }
    exposed_records = {
        record_id
        for work_id in exposed_ids
        for record_id in works_by_id[work_id]["manifestation_record_ids"]
    }
    exposed_identifiers = {
        identifier.casefold()
        for work_id in exposed_ids
        for identifier in works_by_id[work_id]["identifiers"]
    }
    exposed_titles = {
        normalized_title(works_by_id[work_id]["canonical_title"])
        for work_id in exposed_ids
    }
    pending_records = {
        record_id
        for candidate in dedup["adjudication_candidates"]
        for record_id in candidate["record_ids"]
    }
    challenge_path = (
        repo / "studies/ic-2026-2027/research/literature/search-design/"
        "2026-09-11-coverage/baseline-challenge-64.json"
    )
    seeds_path = (
        repo
        / "studies/ic-2026-2027/research/literature/search-design/2026-09-07/seeds.json"
    )
    challenge, challenge_sha = load_json(challenge_path)
    seeds, seeds_sha = load_json(seeds_path)
    reserved_identifiers = (
        exposed_identifiers
        | {
            f"doi:{item['doi'].casefold()}"
            for item in challenge["candidates"]
            if item.get("doi")
        }
        | {f"doi:{item['doi'].casefold()}" for item in seeds if item.get("doi")}
        | {
            identifier.casefold()
            for item in seeds
            for identifier in item.get("declared_identifiers", [])
        }
    )
    reserved_titles = (
        exposed_titles
        | {
            normalized_title(title)
            for item in challenge["candidates"]
            for title in item.get("title", [])
        }
        | {normalized_title(item["declared_title"]) for item in seeds}
    )

    eligible = []
    rejected = Counter()
    for work in works:
        ids = work["manifestation_record_ids"]
        rows = [by_id[record_id] for record_id in ids]
        reasons = set()
        if work["work_id"] in exposed_ids:
            reasons.add("exposed_work_id")
        if any(record_id in pending_records for record_id in ids):
            reasons.add("identity_queue")
        if any(row["origin"]["raw_artifact_sha256"] in exposed_pages for row in rows):
            reasons.add("exposed_page")
        if any(
            identifier.casefold() in reserved_identifiers
            for identifier in work["identifiers"]
        ):
            reasons.add("reserved_identifier")
        if normalized_title(work["canonical_title"]) in reserved_titles:
            reasons.add("reserved_title")
        if reasons:
            rejected.update(reasons)
            continue
        representatives = []
        for row in rows:
            origin = row["origin"]
            match = re.fullmatch(
                r"search\.(openalex|arxiv|dblp)\.q(\d{2})[abc]?", origin["search_id"]
            )
            if match and row["projected_record"]["title"] and 1 <= int(match[2]) <= 16:
                representatives.append((row, match[1], match[2]))
        if representatives:
            eligible.append((work, rows, representatives))

    chosen = []
    seen = set()
    for family in range(1, 17):
        for preferred in ("openalex", "arxiv", "dblp"):
            pool = [
                (work, rows, row, source, query_family)
                for work, rows, representatives in eligible
                for row, source, query_family in representatives
                if query_family == f"{family:02d}" and work["work_id"] not in seen
            ]
            pool.sort(
                key=lambda item: (
                    item[3] != preferred,
                    sha(
                        f"{SEED}|{family}|{preferred}|{item[0]['work_id']}|{item[2]['observation_id']}".encode()
                    ),
                )
            )
            if pool:
                chosen.append(pool[0])
                seen.add(pool[0][0]["work_id"])
    early = [
        (work, rows, row, source, family)
        for work, rows, representatives in eligible
        for row, source, family in representatives
        if work["work_id"] not in seen
        and work["publication_year"] is not None
        and 1970 <= work["publication_year"] < 1995
    ]
    early.sort(
        key=lambda item: (
            item[0]["publication_year"],
            sha(
                f"{SEED}|early|{item[0]['work_id']}|{item[2]['observation_id']}".encode()
            ),
        )
    )
    early_added = 0
    for item in early:
        if item[0]["work_id"] not in seen:
            chosen.append(item)
            seen.add(item[0]["work_id"])
            early_added += 1
        if early_added == 2 or len(chosen) == 50:
            break
    remaining = [
        (work, rows, row, source, family)
        for work, rows, representatives in eligible
        for row, source, family in representatives
        if work["work_id"] not in seen
    ]
    remaining.sort(
        key=lambda item: sha(
            f"{SEED}|fill|{item[0]['work_id']}|{item[2]['observation_id']}".encode()
        )
    )
    for item in remaining:
        if item[0]["work_id"] not in seen:
            chosen.append(item)
            seen.add(item[0]["work_id"])
        if len(chosen) == 50:
            break
    if len(chosen) != 50:
        raise ValueError("fewer than 50 distinct candidates")

    selected_rows = [row for _, rows, _, _, _ in chosen for row in rows]
    request_ids = {row["origin"]["request_sha256"] for row in selected_rows}
    report_pages = {
        page["request_sha256"]: page
        for search in report["searches"]
        for page in search["pages"]
        if page["request_sha256"] in request_ids
    }
    if set(report_pages) != request_ids:
        raise ValueError("retained report lacks a selected request")
    if any(
        page["raw_artifact"]["access_class"] != "public"
        for page in report_pages.values()
    ):
        raise ValueError("selected source is not public")
    for request_id, page in report_pages.items():
        if page["raw_artifact"]["sha256"] not in {
            row["origin"]["raw_artifact_sha256"]
            for row in selected_rows
            if row["origin"]["request_sha256"] == request_id
        }:
            raise ValueError("request/page origin mismatch")

    selected_ids = {work["work_id"] for work, _, _, _, _ in chosen}
    selected_record_ids = {row["observation_id"] for row in selected_rows}
    selected_pages = {row["origin"]["raw_artifact_sha256"] for row in selected_rows}
    selected_identifiers = {
        identifier.casefold()
        for work, _, _, _, _ in chosen
        for identifier in work["identifiers"]
    }
    selected_titles = {
        normalized_title(work["canonical_title"]) for work, _, _, _, _ in chosen
    }
    disjointness = {
        "exposed_work_id_intersection": sorted(selected_ids & exposed_ids),
        "exposed_record_id_intersection": sorted(selected_record_ids & exposed_records),
        "exposed_page_sha256_intersection": sorted(selected_pages & exposed_pages),
        "reserved_identifier_intersection": sorted(
            selected_identifiers & reserved_identifiers
        ),
        "reserved_normalized_title_intersection": sorted(
            selected_titles & reserved_titles
        ),
        "pending_identity_record_intersection": sorted(
            selected_record_ids & pending_records
        ),
    }
    if len(selected_ids) != 50 or any(disjointness.values()):
        raise ValueError("candidate cohort is not 50 works disjoint from reservations")

    source_selection = {
        "schema_version": "calibration-corpus-selection-2",
        "screening_task_version": "2",
        "screening_manifests": {
            role: (
                f"studies/ic-2026-2027/research/agents/systematic-review/{role}_v2.toml"
            )
            for role in ("screener_a", "screener_b")
        },
        "extraction_manifest": (
            "studies/ic-2026-2027/research/agents/systematic-review/extractor_v3.toml"
        ),
        "entries": [
            {
                "work": work,
                "records": [row["projected_record"] for row in rows],
                "full_text": None,
                "include_extraction": False,
            }
            for work, rows, _, _, _ in chosen
        ],
        "bibliographic_sources": [
            {"request": load_cas(cas, request_id), "page": report_pages[request_id]}
            for request_id in sorted(request_ids)
        ],
    }
    manifest = {
        "schema_version": "verification-cohort-candidates-1",
        "status": "unlabelled_candidate_only",
        "source_protocol_id": "opinion-dynamics-systematic-map-v3",
        "source_hashes": {
            "deduplication_sha256": DEDUP_SHA,
            "projection_sha256": PROJECTION_SHA,
            "report_sha256": REPORT_SHA,
            "development_suite_sha256": suite_sha,
            "development_selection_sha256": prior_sha,
            "legacy_rebinding_sha256": legacy_sha,
            "challenge_sha256": challenge_sha,
            "seeds_sha256": seeds_sha,
        },
        "sampling_seed": SEED,
        "metrics": {
            "titled_proposed_works": len(works),
            "development_exposed_works": len(prior_ids),
            "legacy_reserved_works": len(legacy_ids),
            "all_reserved_work_ids": len(exposed_ids),
            "exposed_source_pages": len(exposed_pages),
            "identity_queue_records": len(pending_records),
            "eligible_proposed_works_after_filters": len(eligible),
            "rejection_reasons_overlapping": dict(sorted(rejected.items())),
            "selected_works": len(chosen),
            "selected_observations": len(selected_rows),
            "selected_source_pages": len(selected_pages),
            "selected_requests": len(request_ids),
            "representative_sources": dict(
                sorted(Counter(source for _, _, _, source, _ in chosen).items())
            ),
            "representative_query_families": dict(
                sorted(Counter(f"Q{family}" for _, _, _, _, family in chosen).items())
            ),
            "representatives_without_abstract": sum(
                not row["projected_record"]["abstract"] for _, _, row, _, _ in chosen
            ),
            "full_text_records": 0,
            "owner_reference_labels": 0,
        },
        "disjointness": disjointness,
        "candidates": [
            {
                "slot": f"VC-{index:02d}",
                "work_id": work["work_id"],
                "canonical_title": work["canonical_title"],
                "identifiers": work["identifiers"],
                "manifestation_record_ids": work["manifestation_record_ids"],
                "representative_observation_id": row["observation_id"],
                "representative_source_id": source,
                "query_family": f"Q{family}",
                "source_bindings": [
                    {
                        "observation_id": observation["observation_id"],
                        "request_sha256": observation["origin"]["request_sha256"],
                        "raw_artifact_sha256": observation["origin"][
                            "raw_artifact_sha256"
                        ],
                        "search_id": observation["origin"]["search_id"],
                        "source_id": observation["origin"]["source_id"],
                    }
                    for observation in rows
                ],
            }
            for index, (work, rows, row, source, family) in enumerate(chosen, 1)
        ],
    }
    out.mkdir(mode=0o700)
    selection_sha = write_once(out / "corpus-selection.json", source_selection)
    manifest["native_selection_sha256"] = selection_sha
    manifest_sha = write_once(out / "candidate-manifest.json", manifest)
    print(
        json.dumps(
            {
                "output": str(out),
                "native_selection_sha256": selection_sha,
                "candidate_manifest_sha256": manifest_sha,
                "metrics": manifest["metrics"],
                "disjointness": manifest["disjointness"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
