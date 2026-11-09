"""Prepare blind Claude adjudication packets and validate proposed references."""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path

from cohort_v2 import digest, read_json, write_private

DOUBLE_PREFIX = "calibration-cohort-v2-20260924:double:"


def double_sample(work_ids: list[str]) -> list[str]:
    if len(work_ids) != len(set(work_ids)):
        raise ValueError("duplicate work identity")
    count = math.ceil(len(work_ids) / 10)
    return sorted(
        work_ids, key=lambda wid: (digest((DOUBLE_PREFIX + wid).encode()), wid)
    )[:count]


def packet(task: dict, *, task_sha256: str, pilot: bool) -> dict:
    if task.get("schema_version") not in ({"2", "5"} if pilot else {"5"}) or task.get(
        "stage"
    ) not in {"title_abstract", "full_text"}:
        raise ValueError("ScreeningTaskV5 required")
    records = task.get("records", [])
    if not records or not task.get("work", {}).get("work_id"):
        raise ValueError("task lacks work or original records")
    return {
        "schema_version": "cohort-v2-claude-adjudication-task-1",
        "pilot_development_case": pilot,
        "status": "ready_for_independent_claude_adjudication"
        if not pilot
        else "pilot_ready_no_reference",
        "task_sha256": task_sha256,
        "work_id": task["work"]["work_id"],
        "stage": task["stage"],
        "protocol_sha256": task["protocol_sha256"],
        "criterion_ids": task["criterion_ids"],
        "record_sources": [
            {
                "record_id": row["record_id"],
                "raw_artifact_sha256": row["raw_artifact_sha256"],
                "fields": [
                    field
                    for field in ("title", "abstract", "publication_year", "language")
                    if row.get(field) is not None
                ],
            }
            for row in records
        ],
        "whole_text_locators": task["evidence_locators"]
        if task["stage"] == "full_text"
        else [],
        "task": task,
        "instructions": (
            "Claude: julgue apenas a tarefa vinculada. Cite campos de registros "
            "fornecidos em TA ou locadores exatos do pool em FT. Não consulte "
            "triadores GPT nem referências. Use include, exclude ou uncertain; "
            "incerteza é preferível a inferência sem fonte. Esta saída é proposta "
            "sob delegação, pendente de validação e adoção nativa."
        ),
    }


def validate(packet_value: dict, proposal: dict) -> None:
    task = packet_value["task"]
    if (
        proposal.get("schema_version") != "cohort-v2-claude-reference-proposal-1"
        or proposal.get("task_sha256") != packet_value["task_sha256"]
        or proposal.get("work_id") != packet_value["work_id"]
        or proposal.get("stage") != packet_value["stage"]
    ):
        raise ValueError("proposal is not bound to exact task")
    if proposal.get("model_family") != "Claude" or not proposal.get("model_id"):
        raise ValueError("reference producer must identify Claude model")
    if proposal.get("judgment") not in {"include", "exclude", "uncertain"}:
        raise ValueError("invalid judgment")
    if proposal.get("criterion_id") not in set(task["criterion_ids"]) | {None}:
        raise ValueError("criterion not in task")
    if (
        not isinstance(proposal.get("rationale"), str)
        or len(proposal["rationale"].strip()) < 20
    ):
        raise ValueError("source-bound rationale is required")
    citations = proposal.get("citations")
    if not isinstance(citations, list) or not citations:
        raise ValueError("at least one source citation is required")
    records = {row["record_id"]: row for row in task["records"]}
    for citation in citations:
        if task["stage"] == "title_abstract":
            record = records.get(citation.get("record_id"))
            field = citation.get("field")
            if (
                record is None
                or field not in {"title", "abstract", "publication_year", "language"}
                or record.get(field) is None
                or citation.get("raw_artifact_sha256") != record["raw_artifact_sha256"]
            ):
                raise ValueError("TA citation does not identify a supplied field")
        elif citation not in task["evidence_locators"]:
            raise ValueError("FT citation is not an exact supplied locator")
    if proposal.get("status") != "AI-proposed_pending_owner_adoption":
        raise ValueError("proposal must remain pending adoption")


def main() -> None:
    parser = argparse.ArgumentParser()
    command = parser.add_subparsers(dest="command", required=True)
    prepare = command.add_parser("prepare")
    prepare.add_argument("--task", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--pilot-development-case", action="store_true")
    prepare.add_argument("--c4-receipt", type=Path)
    prepare.add_argument("--order-manifest", type=Path)
    check = command.add_parser("validate")
    check.add_argument("--packet", type=Path, required=True)
    check.add_argument("--proposal", type=Path, required=True)
    args = parser.parse_args()
    os.umask(0o077)
    if args.command == "prepare":
        task, sha = read_json(args.task)
        if not args.pilot_development_case:
            if args.c4_receipt is None or args.order_manifest is None:
                raise ValueError("C4 receipt and frozen order are required")
            receipt, receipt_sha = read_json(args.c4_receipt)
            order, _ = read_json(args.order_manifest)
            if (
                receipt.get("schema_version") != "corpus-screening-bridge-2"
                or receipt.get("outcome", {}).get("status") != "completed"
                or order.get("inputs", {}).get("c4_receipt_sha256") != receipt_sha
                or task["work"]["work_id"]
                not in {wid for wave in order["waves"] for wid in wave}
            ):
                raise ValueError("task is not in a C4-bound frozen wave")
        print(
            write_private(
                args.output,
                packet(task, task_sha256=sha, pilot=args.pilot_development_case),
            )
        )
    else:
        source, _ = read_json(args.packet)
        proposal, _ = read_json(args.proposal)
        validate(source, proposal)
        print("valid")


if __name__ == "__main__":
    main()
