"""Prepare the eight retained proposals through native read-only C2 v2 replay."""

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from pydantic import TypeAdapter
from research_workbench.core.contracts import AccessClass
from research_workbench.orchestration.review_acquisition import ReviewAcquisitionRuntime
from research_workbench.orchestration.review_corpus import (
    ReviewCorpusPreparationRuntime,
)
from research_workbench.orchestration.review_corpus_metadata import (
    CorpusMetadataStageReceipt,
    ReviewCorpusMetadataStageRuntime,
)
from research_workbench.orchestration.review_corpus_metadata_resolution_v2 import (
    ReviewCorpusMetadataResolutionV2Runtime,
)
from research_workbench.workflows.systematic_review.artifacts import (
    ArtifactRef,
    ContentAddressedArtifactStore,
)
from research_workbench.workflows.systematic_review.corpus_screening_bridge import (
    ProtocolFieldCompatibility,
)
from research_workbench.workflows.systematic_review.executed_evaluation import (
    canonical_review_eval_json,
)
from research_workbench.workflows.systematic_review.metadata_resolution_v2 import (
    MetadataChoiceV2,
    MetadataPolicyApproval,
)
from research_workbench.workflows.systematic_review.protocol import ReviewProtocol

BASE = Path("/Users/davi/.local/state/research-workbench")
PROPOSALS = BASE / "autonomous-review-20260915/metadata-source-bound-proposals-20260916"
BROAD = BASE / "broad-research-20260911"
CHOICES_SHA = "eeff79017bbf1bd25a7f886128e87916713a3e383eca249422d151ef48264553"
PARENT_SHA = "6b16e1cb9954ee505a592121d697fb58c56b444e3c430c8360301625ceb4dd82"
AFRICA = "metadata.v1.ea8185255c7dc5d57ab30655"


class ReadOnlyUnion(ContentAddressedArtifactStore):
    """Route reads to native CAS stores without copying or altering their bytes."""

    def __init__(self, stores):
        self.stores = stores
        super().__init__(stores[0].root, max_bytes=512_000_000)

    def read(self, ref):
        for store in self.stores:
            if (store.root / ref.relative_path).exists():
                return store.read(ref)
        raise FileNotFoundError(ref.sha256)

    def put(self, *args, **kwargs):
        raise RuntimeError("Read-only preparation must not publish runtime artifacts")


def snapshot(roots):
    return {
        str(path): (path.stat().st_size, path.stat().st_mtime_ns)
        for root in roots
        for path in root.rglob("*")
        if path.is_file()
    }


def publish(path, raw):
    with os.fdopen(
        os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"
    ) as stream:
        stream.write(raw)
    path.chmod(0o400)
    if path.read_bytes() != raw:
        raise ValueError(f"prepared artifact differs after writing: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--prepared-at", type=datetime.fromisoformat)
    args = parser.parse_args()
    repo = args.repository.resolve(strict=True)
    at = args.prepared_at or datetime.now(UTC)
    output = Path(tempfile.mkdtemp(prefix="c2-v2-20260924-", dir="/private/tmp"))
    print(json.dumps({"private_output": str(output)}), flush=True)
    operation_root = output / "unused-operations"
    operation_root.mkdir(mode=0o700)
    overlay_root = output / "policy-artifacts"
    overlay_root.mkdir(mode=0o700)
    original = ContentAddressedArtifactStore(
        BROAD / "acquisition-v3/artifacts", max_bytes=512_000_000
    )
    proposed = ContentAddressedArtifactStore(
        PROPOSALS / "artifacts", max_bytes=25_000_000
    )
    overlay = ContentAddressedArtifactStore(overlay_root, max_bytes=25_000_000)
    store = ReadOnlyUnion((overlay, proposed, original))
    roots = (
        BROAD / "acquisition-v3/operations",
        BROAD / "corpus-v3-interrupted-successor-1/preparation",
        BROAD / "corpus-v3-metadata-successor-1/stage",
        original.root,
        PROPOSALS,
    )
    before = snapshot(roots)
    raw = (PROPOSALS / "choices.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != CHOICES_SHA:
        raise ValueError("source-bound choices changed")
    all_choices = TypeAdapter(tuple[MetadataChoiceV2, ...]).validate_json(raw)
    if len(all_choices) != 9:
        raise ValueError("expected nine source-bound proposals")
    deferred = tuple(choice for choice in all_choices if choice.disposition == "defer")
    if len(deferred) != 1 or deferred[0].candidate_id != AFRICA:
        raise ValueError("Africa Today must be the sole deferred proposal")
    choices = tuple(
        sorted(
            (choice for choice in all_choices if choice.disposition != "defer"),
            key=lambda choice: choice.candidate_id,
        )
    )
    if len(choices) != 8:
        raise ValueError("expected eight source-bound choices")
    relative = f"sha256/{PARENT_SHA[:2]}/{PARENT_SHA[2:4]}/{PARENT_SHA}"
    ref = ArtifactRef(
        sha256=PARENT_SHA,
        relative_path=relative,
        size_bytes=(original.root / relative).stat().st_size,
        media_type="application/json",
        access_class=AccessClass.RESTRICTED,
    )
    parent = CorpusMetadataStageReceipt.model_validate_json(store.read(ref))
    predecessor = ReviewProtocol.model_validate_json(store.read(parent.protocol))
    chain = []
    literature = Path("studies/ic-2026-2027/research/literature/protocol")
    for approval_name in (
        "opinion-dynamics-systematic-map-v4-20260914.toml",
        "opinion-dynamics-systematic-map-v5-20260924.toml",
    ):
        approval_path = literature / "approvals" / approval_name
        approval_raw = (repo / approval_path).read_bytes()
        approval = tomllib.loads(approval_raw.decode())
        successor = ReviewProtocol.model_validate_json(
            (repo / approval["subject_path"]).read_bytes()
        )
        before_policy, after_policy = (
            predecessor.model_dump(mode="json"),
            successor.model_dump(mode="json"),
        )
        compatibility = tuple(
            ProtocolFieldCompatibility(
                field=key,
                predecessor=before_policy.get(key),
                successor=after_policy.get(key),
                rationale=(
                    "Exact approved successor field change; "
                    "unchanged acquisition and eligibility scope."
                ),
            )
            for key in sorted(before_policy.keys() | after_policy.keys())
            if before_policy.get(key) != after_policy.get(key)
        )
        chain.append(
            MetadataPolicyApproval(
                protocol=overlay.put(
                    canonical_review_eval_json(after_policy),
                    "application/json",
                    AccessClass.RESTRICTED,
                ),
                approval=overlay.put(
                    approval_raw, "application/toml", AccessClass.RESTRICTED
                ),
                approval_path=str(approval_path),
                compatibility=compatibility,
            )
        )
        predecessor = successor
    acquisition = ReviewAcquisitionRuntime(roots[0], store, read_only=True)
    preparation = ReviewCorpusPreparationRuntime(
        roots[1], store, acquisition, read_only=True
    )
    metadata = ReviewCorpusMetadataStageRuntime(
        roots[2], store, preparation, read_only=True
    )
    runtime = ReviewCorpusMetadataResolutionV2Runtime(
        operation_root, store, metadata, repository_root=repo, read_only=True
    )
    request = runtime.prepare_request(
        ref, choices, policy_chain=tuple(chain), recorded_at=at
    )
    if snapshot(roots) != before:
        raise ValueError("read-only preparation changed an existing artifact")
    if list(operation_root.iterdir()):
        raise ValueError("read-only preparation wrote an operation")
    request_raw = canonical_review_eval_json(request.model_dump(mode="json"))
    if hashlib.sha256(request_raw).hexdigest() != request.digest:
        raise ValueError("prepared request digest mismatch")
    publish(output / "request.json", request_raw)
    proof = {
        "schema_version": "c2-v2-readonly-preparation-1",
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo, text=True
        ).strip(),
        "prepared_at": at.isoformat(),
        "metadata_receipt_sha256": PARENT_SHA,
        "choices_sha256": CHOICES_SHA,
        "request_sha256": request.digest,
        "action_id": request.action_id,
        "required_evidence_sha256s": request.required_evidence_sha256s,
        "choice_count": len(choices),
        "omitted_deferred_candidate": AFRICA,
        "protected_files_unchanged": len(before),
        "owner_decision_created": False,
        "canonical_transition_executed": False,
        "scientific_acceptance": False,
    }
    publish(output / "preparation-proof.json", canonical_review_eval_json(proof))
    print(json.dumps(proof), flush=True)


if __name__ == "__main__":
    main()
