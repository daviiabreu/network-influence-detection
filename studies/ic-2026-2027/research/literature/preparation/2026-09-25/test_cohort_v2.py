"""Boundary tests for pre-C4 ordering and source-bound adjudication."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from adjudication import double_sample, packet, validate
from cohort_v2 import build_strata, digest, sample


def save(path: Path, value: dict) -> str:
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.write_bytes(raw)
    return digest(raw)


class CohortV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        os.chmod(self.root, 0o700)

    def test_sampler_requires_closed_exposure_and_c4_binding(self) -> None:
        inventory = {
            "complete": False,
            "works": [
                {
                    "work_id": "old",
                    "identifiers": ["arxiv:old"],
                    "manifestations": ["old-record"],
                    "bibliographic_page_sha256": ["b" * 64],
                    "full_text_sha256": ["a" * 64],
                }
            ],
        }
        inventory_path = self.root / "inventory.json"
        save(inventory_path, inventory)
        works = [
            {
                "work_id": wid,
                "identifiers": [f"arxiv:{wid}"],
                "manifestation_record_ids": [f"record-{wid}"],
            }
            for wid in ("new", "old")
        ]
        projection = {
            "schema_version": "corpus-screening-projection-2",
            "works": works,
            "joins": [
                {"work_id": wid, "source_work_ids": [wid]} for wid in ("new", "old")
            ],
        }
        projection_path = self.root / "projection.json"
        projection_sha = save(projection_path, projection)
        records_path = self.root / "records.json"
        records_sha = save(
            records_path,
            [
                {
                    "record_id": f"record-{wid}",
                    "search_id": "search.arxiv.q01",
                    "source_id": "arxiv",
                    "raw_artifact_sha256": page * 64,
                    "abstract": "Evidence",
                    "publication_year": 2000,
                }
                for wid, page in (("new", "c"), ("old", "b"))
            ],
        )
        receipt = {
            "schema_version": "corpus-screening-bridge-2",
            "projection": {"sha256": projection_sha},
            "original_records": {"sha256": records_sha},
            "work_count": 2,
            "outcome": {"status": "completed"},
        }
        receipt_path = self.root / "receipt.json"
        save(receipt_path, receipt)
        strata = build_strata(receipt_path, projection_path, records_path)
        strata_path = self.root / "strata.json"
        save(strata_path, strata)
        with self.assertRaisesRegex(ValueError, "not closed"):
            sample(
                receipt_path,
                projection_path,
                records_path,
                strata_path,
                inventory_path,
                self.root / "out.json",
            )
        inventory["complete"] = True
        save(inventory_path, inventory)
        result = sample(
            receipt_path,
            projection_path,
            records_path,
            strata_path,
            inventory_path,
            self.root / "out.json",
        )
        self.assertEqual(result["waves"][0], ["new"])
        self.assertEqual(result["refusals"][0]["work_id"], "old")
        strata["representatives"][0]["bibliographic_page_sha256"] = ["b" * 64]
        save(strata_path, strata)
        with self.assertRaisesRegex(ValueError, "source differs"):
            sample(
                receipt_path,
                projection_path,
                records_path,
                strata_path,
                inventory_path,
                self.root / "blocked.json",
            )
        receipt["projection"]["sha256"] = "0" * 64
        save(receipt_path, receipt)
        with self.assertRaisesRegex(ValueError, "projection"):
            sample(
                receipt_path,
                projection_path,
                records_path,
                strata_path,
                inventory_path,
                self.root / "out2.json",
            )

    def test_claude_reference_must_cite_supplied_record(self) -> None:
        task = {
            "schema_version": "5",
            "stage": "title_abstract",
            "work": {"work_id": "w"},
            "records": [
                {"record_id": "r", "raw_artifact_sha256": "a" * 64, "title": "A study"}
            ],
            "criterion_ids": ["criterion"],
            "protocol_sha256": "b" * 64,
            "evidence_locators": [],
        }
        source = packet(task, task_sha256="c" * 64, pilot=False)
        proposal = {
            "schema_version": "cohort-v2-claude-reference-proposal-1",
            "task_sha256": "c" * 64,
            "work_id": "w",
            "stage": "title_abstract",
            "model_family": "Claude",
            "model_id": "claude-test",
            "judgment": "uncertain",
            "criterion_id": "criterion",
            "rationale": "The supplied title alone cannot establish the criterion.",
            "citations": [
                {"record_id": "r", "raw_artifact_sha256": "a" * 64, "field": "title"}
            ],
            "status": "AI-proposed_pending_owner_adoption",
        }
        validate(source, proposal)
        proposal["citations"][0]["raw_artifact_sha256"] = "d" * 64
        with self.assertRaisesRegex(ValueError, "citation"):
            validate(source, proposal)
        self.assertEqual(len(double_sample([f"w{i}" for i in range(101)])), 11)

    def test_strata_are_derived_from_c4_original_record(self) -> None:
        records = [
            {
                "record_id": "r",
                "search_id": "search.arxiv.q03",
                "source_id": "arxiv",
                "raw_artifact_sha256": "a" * 64,
                "abstract": "Evidence",
                "publication_year": 1990,
            }
        ]
        record_path = self.root / "records.json"
        record_sha = save(record_path, records)
        projection_path = self.root / "projection.json"
        projection_sha = save(
            projection_path,
            {
                "schema_version": "corpus-screening-projection-2",
                "works": [{"work_id": "w", "manifestation_record_ids": ["r"]}],
            },
        )
        receipt_path = self.root / "receipt.json"
        save(
            receipt_path,
            {
                "schema_version": "corpus-screening-bridge-2",
                "outcome": {"status": "completed"},
                "projection": {"sha256": projection_sha},
                "original_records": {"sha256": record_sha},
                "work_count": 1,
            },
        )
        row = build_strata(receipt_path, projection_path, record_path)[
            "representatives"
        ][0]
        self.assertEqual((row["family"], row["source"]), ("Q03", "arxiv"))
        self.assertTrue(row["abstract_present"])
        self.assertTrue(row["underrepresented"])


if __name__ == "__main__":
    unittest.main()
