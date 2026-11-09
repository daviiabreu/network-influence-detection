"""Acquire a provisional CC BY/CC0 arXiv PDF pool without model execution."""

from __future__ import annotations

import argparse
import html
import io
import os
import re
import unicodedata
import urllib.request
from pathlib import Path

from cohort_v2 import PREFIX, digest, read_json, write_private
from pypdf import PdfReader

DEDUP = "41a54060be2206d88b13aa8d0026acca6b6f27342cb77391c8c3462f97b66a53"
OBSERVATIONS = "93c8086aa6b0231fd019291f9bb3984e5e436e629c4424e95ae499729957cc85"
LICENSES = (
    "creativecommons.org/licenses/by/4.0/",
    "creativecommons.org/publicdomain/zero/1.0/",
)
HEADERS = {
    "User-Agent": "research-workbench-cohort-prep/1.0 (academic source verification)"
}


def norm(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split()).strip(" .")


def meta(page: str, name: str) -> str | None:
    match = re.search(
        r'<meta\s+name="' + re.escape(name) + r'"\s+content="([^"]+)"', page
    )
    return html.unescape(match.group(1)) if match else None


def fetch(url: str, limit: int) -> tuple[bytes, str]:
    with urllib.request.urlopen(
        urllib.request.Request(url, headers=HEADERS), timeout=30
    ) as response:
        if response.status != 200 or not response.geturl().startswith(
            "https://arxiv.org/"
        ):
            raise ValueError("source response was not arXiv 200")
        raw = response.read(limit + 1)
        if len(raw) > limit:
            raise ValueError("source exceeds byte limit")
        return raw, response.geturl()


def candidates(cas: Path, inventory: dict) -> list[tuple[dict, dict, str]]:
    dedup, _ = read_json(cas / "41/a5" / DEDUP, DEDUP)
    observations, _ = read_json(cas / "93/c8" / OBSERVATIONS, OBSERVATIONS)
    by_id = {row["observation_id"]: row for row in observations["observations"]}
    exposed_ids = {row["work_id"] for row in inventory["works"]}
    exposed_identifiers = {
        item for row in inventory["works"] for item in row["identifiers"]
    }
    exposed_manifestations = {
        item for row in inventory["works"] for item in row["manifestations"]
    }
    exposed_pages = {
        item
        for row in inventory["works"]
        for item in row.get("bibliographic_page_sha256", [])
    }
    pending = {
        item
        for queue in dedup["adjudication_candidates"]
        for item in queue["record_ids"]
    }
    chosen = []
    for work in dedup["titled_works"]:
        ids = work["manifestation_record_ids"]
        if (
            work["work_id"] in exposed_ids
            or set(ids) & (pending | exposed_manifestations)
            or {x.casefold() for x in work["identifiers"]} & exposed_identifiers
        ):
            continue
        arxiv_ids = [
            x.removeprefix("arxiv:")
            for x in work["identifiers"]
            if x.startswith("arxiv:")
        ]
        if len(arxiv_ids) != 1:
            continue
        rows = [by_id[x] for x in ids]
        if any(row["origin"]["raw_artifact_sha256"] in exposed_pages for row in rows):
            continue
        representatives = [
            row
            for row in rows
            if re.fullmatch(r"search\.arxiv\.q\d{2}[abc]?", row["origin"]["search_id"])
        ]
        if not representatives:
            continue
        chosen.append(
            (
                work,
                min(representatives, key=lambda r: r["observation_id"]),
                arxiv_ids[0],
            )
        )
    return sorted(
        chosen,
        key=lambda x: (digest((PREFIX + x[0]["work_id"]).encode()), x[0]["work_id"]),
    )


def acquire(cas: Path, inventory_path: Path, output: Path, target: int) -> dict:
    inventory, inventory_sha = read_json(inventory_path)
    exposed_text = {
        value for row in inventory["works"] for value in row["full_text_sha256"]
    }
    output.mkdir(mode=0o700, parents=True, exist_ok=True)
    if output.stat().st_mode & 0o077:
        raise ValueError("private output directory requires mode 0700")
    manifest_path = output / "manifest.json"
    if manifest_path.exists():
        raise ValueError("create-once manifest already exists")
    accepted = []
    attempts = []
    for work, row, arxiv_id in candidates(cas, inventory):
        if len(accepted) >= target:
            break
        landing = f"https://arxiv.org/abs/{arxiv_id}"
        try:
            page_bytes, final_landing = fetch(landing, 1_000_000)
            page = page_bytes.decode("utf-8")
            license_match = re.search(
                r'<div class="abs-license"[^>]*>\s*<a href="([^"]+)', page
            )
            license_url = (
                license_match.group(1).replace("http://", "https://")
                if license_match
                else ""
            )
            if not any(
                license_url.startswith("https://" + license_name)
                for license_name in LICENSES
            ):
                attempts.append(
                    {"work_id": work["work_id"], "reason": "license_not_allowlisted"}
                )
                continue
            title = meta(page, "citation_title")
            pdf_url = meta(page, "citation_pdf_url")
            cited_id = meta(page, "citation_arxiv_id")
            if (
                not title
                or not pdf_url
                or cited_id != arxiv_id
                or norm(title) != norm(work["canonical_title"])
            ):
                attempts.append(
                    {"work_id": work["work_id"], "reason": "source_identity_mismatch"}
                )
                continue
            if not pdf_url.startswith("https://arxiv.org/pdf/"):
                raise ValueError("PDF URL leaves arXiv")
            pdf, final_pdf = fetch(pdf_url, 20_000_000)
            if not pdf.startswith(b"%PDF-"):
                raise ValueError("not a PDF")
            reader = PdfReader(io.BytesIO(pdf), strict=True)
            pages = [page.extract_text() or "" for page in reader.pages]
            if not pages or any(not page.strip() for page in pages):
                raise ValueError("incomplete native text projection")
            pdf_sha = digest(pdf)
            if pdf_sha in exposed_text:
                attempts.append(
                    {"work_id": work["work_id"], "reason": "exposed_full_text_sha256"}
                )
                continue
            pdf_path = output / "sha256" / pdf_sha[:2] / pdf_sha[2:4] / pdf_sha
            pdf_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            if not pdf_path.exists():
                fd = os.open(pdf_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(fd, "wb") as handle:
                    handle.write(pdf)
            if digest(pdf_path.read_bytes()) != pdf_sha:
                raise ValueError("retained PDF hash mismatch")
            landing_sha = digest(page_bytes)
            landing_path = (
                output
                / "landing-sha256"
                / landing_sha[:2]
                / landing_sha[2:4]
                / landing_sha
            )
            landing_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            if not landing_path.exists():
                fd = os.open(landing_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(fd, "wb") as handle:
                    handle.write(page_bytes)
            if digest(landing_path.read_bytes()) != landing_sha:
                raise ValueError("retained landing page hash mismatch")
            accepted.append(
                {
                    "work_id_provisional": work["work_id"],
                    "identifiers": work["identifiers"],
                    "manifestation_record_ids": work["manifestation_record_ids"],
                    "representative_observation_id": row["observation_id"],
                    "representative_search_id": row["origin"]["search_id"],
                    "landing_url": final_landing,
                    "landing_sha256": landing_sha,
                    "license_url": license_url,
                    "pdf_url": final_pdf,
                    "pdf_sha256": pdf_sha,
                    "pdf_bytes": len(pdf),
                    "pdf_pages": len(pages),
                    "page_text_sha256": [digest(page.encode()) for page in pages],
                    "parser": (
                        f"pypdf {__import__('pypdf').__version__} strict native text"
                    ),
                    "status": "provisional_pre_C4_not_a_cohort_item",
                }
            )
        except Exception as error:
            attempts.append(
                {
                    "work_id": work["work_id"],
                    "reason": type(error).__name__ + ": " + str(error)[:100],
                }
            )
    manifest = {
        "schema_version": "cohort-v2-provisional-oa-pool-1",
        "source_dedup_sha256": DEDUP,
        "source_observations_sha256": OBSERVATIONS,
        "exposure_inventory_sha256": inventory_sha,
        "target": target,
        "accepted_count": len(accepted),
        "accepted": accepted,
        "attempts": attempts,
        "scope": (
            "provisional CC BY or CC0 arXiv PDFs, pending C4 identity "
            "and native FullTextRecord import"
        ),
    }
    write_private(manifest_path, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cas", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target", type=int, default=50)
    args = parser.parse_args()
    os.umask(0o077)
    result = acquire(args.cas, args.inventory, args.output, args.target)
    print(f"accepted={result['accepted_count']} attempts={len(result['attempts'])}")


if __name__ == "__main__":
    main()
