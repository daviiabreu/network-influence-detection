"""Record the approved eight-choice C2 v2 successor in private native stores."""

import argparse
import hashlib
import json
import os
import secrets
import stat
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from pydantic import TypeAdapter
from research_workbench.core.contracts import AccessClass
from research_workbench.orchestration.review_acquisition import ReviewAcquisitionRuntime
from research_workbench.orchestration.review_corpus import (
    ReviewCorpusPreparationRuntime,
)
from research_workbench.orchestration.review_corpus_identity_resolution import (
    ReviewCorpusIdentityResolutionRuntime,
)
from research_workbench.orchestration.review_corpus_metadata import (
    CorpusMetadataStageReceipt,
    ReviewCorpusMetadataStageRuntime,
)
from research_workbench.orchestration.review_corpus_metadata_resolution_v2 import (
    CorpusMetadataResolutionV2Inputs,
    ReviewCorpusMetadataResolutionV2Runtime,
)
from research_workbench.orchestration.systematic_review import (
    OwnerDecision,
    ReviewStageContext,
)
from research_workbench.workflows.systematic_review.artifacts import (
    ContentAddressedArtifactStore,
)
from research_workbench.workflows.systematic_review.executed_evaluation import (
    canonical_review_eval_json,
)
from research_workbench.workflows.systematic_review.metadata_resolution_v2 import (
    CorpusMetadataResolutionV2Request,
    MetadataChoiceV2,
)
from research_workbench.workflows.systematic_review.protocol import ReviewProtocol

BASE = Path("/Users/davi/.local/state/research-workbench")
PRIVATE = BASE / "research-area-20260924-c2-v2-52e45005"
PROPOSALS = BASE / "autonomous-review-20260915/metadata-source-bound-proposals-20260916"
BROAD = BASE / "broad-research-20260911"
REQUEST_SHA = "52e450054c46b9a506c399baabc43cf6c327a811d622031433fe494d10d6a509"
PROOF_SHA = "816bc7c5076b9d558239e1462c949381072a2d73dbafd72e7c9b67a757821e24"
CHOICES_SHA = "eeff79017bbf1bd25a7f886128e87916713a3e383eca249422d151ef48264553"
APPROVAL_COMMIT = "a952582f47798c80404dbd39ae8b79fe82a02657"
AFRICA = "metadata.v1.ea8185255c7dc5d57ab30655"
OWNER = "Davi Abreu da Silveira"


class RoutedStore(ContentAddressedArtifactStore):
    def __init__(self, primary, sources, *, writable):
        super().__init__(primary.root, max_bytes=512_000_000)
        self.primary = primary
        self.sources = sources
        self.writable = writable

    def read(self, ref):
        for source in self.sources:
            if (source.root / ref.relative_path).exists():
                return source.read(ref)
        raise FileNotFoundError(ref.sha256)

    def put(self, content, media_type, access_class):
        if not self.writable:
            raise RuntimeError("read-only preflight cannot publish artifacts")
        return self.primary.put(content, media_type, access_class)


def require_private(path, *, mode):
    if path.is_symlink() or stat.S_IMODE(path.stat().st_mode) != mode:
        raise ValueError(f"private path has unsafe mode or link: {path}")


def require_hash(path, digest):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError(f"private artifact digest changed: {path}")
    return raw


def publish(path, raw):
    temporary = path.with_name(f".{path.name}.{secrets.token_hex(8)}.tmp")
    try:
        with os.fdopen(
            os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb"
        ) as stream:
            stream.write(raw)
            stream.flush()
            os.fchmod(stream.fileno(), 0o400)
            os.fsync(stream.fileno())
        os.link(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)
    if path.read_bytes() != raw:
        raise ValueError(f"private artifact changed after publication: {path}")


def stores(*, output=None, writable=False):
    original = ContentAddressedArtifactStore(
        BROAD / "acquisition-v3/artifacts", max_bytes=512_000_000
    )
    proposed = ContentAddressedArtifactStore(
        PROPOSALS / "artifacts", max_bytes=25_000_000
    )
    policy = ContentAddressedArtifactStore(
        PRIVATE / "policy-artifacts", max_bytes=25_000_000
    )
    sources = (policy, proposed, original)
    if output is None:
        return RoutedStore(policy, sources, writable=False)
    target = ContentAddressedArtifactStore(output, max_bytes=512_000_000)
    return RoutedStore(target, (target, *sources), writable=writable)


def runtimes(repository, store, *, operation_root, read_only):
    acquisition = ReviewAcquisitionRuntime(
        BROAD / "acquisition-v3/operations", store, read_only=True
    )
    preparation = ReviewCorpusPreparationRuntime(
        BROAD / "corpus-v3-interrupted-successor-1/preparation",
        store,
        acquisition,
        read_only=True,
    )
    metadata = ReviewCorpusMetadataStageRuntime(
        BROAD / "corpus-v3-metadata-successor-1/stage",
        store,
        preparation,
        read_only=True,
    )
    resolution = ReviewCorpusMetadataResolutionV2Runtime(
        operation_root,
        store,
        metadata,
        repository_root=repository,
        read_only=read_only,
    )
    return preparation, resolution


def preflight(repository):
    require_private(PRIVATE, mode=0o700)
    require_private(PRIVATE / "policy-artifacts", mode=0o700)
    require_private(PRIVATE / "request.json", mode=0o400)
    require_private(PRIVATE / "preparation-proof.json", mode=0o400)
    raw = require_hash(PRIVATE / "request.json", REQUEST_SHA)
    proof_raw = require_hash(PRIVATE / "preparation-proof.json", PROOF_SHA)
    request = CorpusMetadataResolutionV2Request.model_validate_json(raw)
    proof = json.loads(proof_raw)
    source_raw = require_hash(PROPOSALS / "choices.json", CHOICES_SHA)
    source_choices = TypeAdapter(tuple[MetadataChoiceV2, ...]).validate_json(source_raw)
    deferred = tuple(
        choice for choice in source_choices if choice.disposition == "defer"
    )
    selected = tuple(
        sorted(
            (choice for choice in source_choices if choice.disposition != "defer"),
            key=lambda choice: choice.candidate_id,
        )
    )
    if (
        request.digest != REQUEST_SHA
        or request.previous is not None
        or len(source_choices) != 9
        or len(selected) != 8
        or len(deferred) != 1
        or deferred[0].candidate_id != AFRICA
        or request.choices != selected
        or sum(choice.disposition == "title_resolved" for choice in selected) != 4
        or sum(choice.disposition == "explicitly_untitled" for choice in selected) != 4
        or proof["request_sha256"] != REQUEST_SHA
        or proof["choices_sha256"] != CHOICES_SHA
        or proof["action_id"] != request.action_id
        or proof["required_evidence_sha256s"] != list(request.required_evidence_sha256s)
        or len(request.required_evidence_sha256s) != 15
        or proof["omitted_deferred_candidate"] != AFRICA
    ):
        raise ValueError("C2 request, proof or approved choice set differs")
    store = stores()
    _, runtime = runtimes(
        repository,
        store,
        operation_root=PRIVATE / "policy-artifacts",
        read_only=True,
    )
    reproduced = runtime.prepare_request(
        request.metadata,
        request.choices,
        policy_chain=request.policy_chain,
        recorded_at=request.prepared_at,
        previous=request.previous,
    )
    if reproduced != request:
        raise ValueError("native read-only request replay differs")
    parent = CorpusMetadataStageReceipt.model_validate_json(
        store.read(request.metadata)
    )
    final_approval = tomllib.loads(
        store.read(request.policy_chain[-1].approval).decode()
    )
    protocol = ReviewProtocol.model_validate_json(
        store.read(request.policy_chain[-1].protocol)
    )
    if (
        final_approval["repository_commit"] != APPROVAL_COMMIT
        or protocol.research_owner != OWNER
        or request.protocol_sha256 != request.policy_chain[-1].protocol.sha256
        or request.metadata.sha256 != proof["metadata_receipt_sha256"]
    ):
        raise ValueError("C2 protocol, owner or parent binding differs")
    return request, parent, protocol


def execution_summary(result, request, decision_ref, basis_sha=None):
    eligibility_assessed = result.receipt.scientific_eligibility_assessed
    return {
        "schema_version": "c2-v2-execution-summary-1",
        "request_sha256": request.digest,
        "action_id": request.action_id,
        "owner_decision_sha256": decision_ref.sha256,
        "receipt_sha256": result.artifact.sha256,
        "projection_sha256": result.receipt.projection.sha256,
        "metadata_status": result.receipt.metadata_status,
        "outcome": result.receipt.outcome.status.value,
        "screening_ready": result.receipt.screening_ready,
        "scientific_eligibility_assessed": eligibility_assessed,
        "resolved_titles": len(
            [
                choice
                for choice in result.projection.choices
                if choice.disposition == "title_resolved"
            ]
        ),
        "explicitly_untitled": len(result.projection.explicitly_untitled_work_ids),
        "unresolved_candidates": len(result.projection.unresolved_candidate_ids),
        "africa_today_unresolved": AFRICA in result.projection.unresolved_candidate_ids,
        "proposal_basis_sha256": basis_sha,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument(
        "--mode", choices=("preflight", "execute", "replay", "basis"), required=True
    )
    args = parser.parse_args()
    repository = args.repository.resolve(strict=True)
    request, parent, protocol = preflight(repository)
    execution = PRIVATE / "execution"
    if args.mode == "preflight":
        print(
            json.dumps(
                {
                    "request_sha256": request.digest,
                    "choices": len(request.choices),
                    "required_evidence": len(request.required_evidence_sha256s),
                    "destination_absent": not execution.exists(),
                },
                sort_keys=True,
            )
        )
        return
    if args.mode == "execute":
        if execution.exists():
            raise ValueError(
                "C2 execution root exists; inspect or replay, never retry blindly"
            )
        execution.mkdir(mode=0o700)
        (execution / "artifacts").mkdir(mode=0o700)
        (execution / "operations").mkdir(mode=0o700)
        store = stores(output=execution / "artifacts", writable=True)
        _, runtime = runtimes(
            repository, store, operation_root=execution / "operations", read_only=False
        )
        decided_at = datetime.now(UTC)
        decision = OwnerDecision(
            protocol_sha256=request.protocol_sha256,
            action_id=request.action_id,
            decision="approve",
            decided_by=OWNER,
            decided_at=decided_at,
            rationale=(
                "Davi explicitly answered 'tudo aprovado' to the presented "
                "three-item question. This decision adopts only the eight C2 "
                "metadata-identification choices shown in the 75375d3 brief "
                "and exact request; it excludes Africa Today and does not assert "
                "personal inspection of restricted excerpts, identity choices, "
                "eligibility or scientific acceptance."
            ),
            evidence_artifact_sha256s=request.required_evidence_sha256s,
        )
        request_ref = store.put(
            canonical_review_eval_json(request.model_dump(mode="json")),
            "application/json",
            AccessClass.RESTRICTED,
        )
        decision_ref = store.put(
            canonical_review_eval_json(decision.model_dump(mode="json")),
            "application/json",
            AccessClass.RESTRICTED,
        )
        if request_ref.sha256 != REQUEST_SHA:
            raise ValueError("published request differs")
        inputs = CorpusMetadataResolutionV2Inputs(
            metadata=request.metadata,
            request=request_ref,
            owner_decision=decision_ref,
        )
        context = ReviewStageContext.model_validate(
            {
                **parent.context.model_dump(mode="json"),
                "run_id": "opinion-dynamics-map-v3-c2-v2-52e45005-1",
                "idempotency_key": "corpus.metadata-resolution-v2.52e45005.20260924",
                "protocol_id": protocol.protocol_id,
                "protocol_sha256": request.protocol_sha256,
                "repository_commit": APPROVAL_COMMIT,
                "prior_artifact_sha256s": request.prior_artifact_sha256s,
            }
        )
        recorded_at = datetime.now(UTC)
        manifest = {
            "schema_version": "c2-v2-execution-manifest-1",
            "context": context.model_dump(mode="json"),
            "inputs": inputs.model_dump(mode="json"),
            "recorded_at": recorded_at.isoformat(),
            "decision_decided_at": decided_at.isoformat(),
        }
        publish(
            execution / "execution-manifest.json", canonical_review_eval_json(manifest)
        )
        result = runtime.execute(context, inputs, recorded_at=recorded_at)
    else:
        require_private(execution, mode=0o700)
        require_private(execution / "execution-manifest.json", mode=0o400)
        manifest = json.loads((execution / "execution-manifest.json").read_bytes())
        context = ReviewStageContext.model_validate(manifest["context"])
        inputs = CorpusMetadataResolutionV2Inputs.model_validate(manifest["inputs"])
        recorded_at = datetime.fromisoformat(manifest["recorded_at"])
        store = stores(output=execution / "artifacts")
        decision = OwnerDecision.model_validate_json(store.read(inputs.owner_decision))
        if (
            inputs.metadata != request.metadata
            or inputs.request.sha256 != REQUEST_SHA
            or store.read(inputs.request)
            != canonical_review_eval_json(request.model_dump(mode="json"))
            or decision.protocol_sha256 != request.protocol_sha256
            or decision.action_id != request.action_id
            or decision.decision != "approve"
            or decision.decided_by != OWNER
            or decision.evidence_artifact_sha256s != request.required_evidence_sha256s
            or decision.decided_at.isoformat() != manifest["decision_decided_at"]
            or context.protocol_id != protocol.protocol_id
            or context.protocol_sha256 != request.protocol_sha256
            or context.repository_commit != APPROVAL_COMMIT
            or context.prior_artifact_sha256s != request.prior_artifact_sha256s
        ):
            raise ValueError("retained C2 manifest differs from approved request")
        _, runtime = runtimes(
            repository, store, operation_root=execution / "operations", read_only=True
        )
        result = runtime.replay(context, inputs, recorded_at=recorded_at)
        decision_ref = inputs.owner_decision
    if result.receipt.metadata_status != "incomplete" or (
        result.receipt.inputs.request.sha256 != REQUEST_SHA
        or result.projection.choices != request.choices
        or len(result.projection.unresolved_candidate_ids) != 1
        or AFRICA not in result.projection.unresolved_candidate_ids
        or len(result.projection.explicitly_untitled_work_ids) != 4
        or result.receipt.screening_ready
        or result.receipt.scientific_eligibility_assessed
    ):
        raise ValueError("C2 partial successor breached its approved boundary")
    if args.mode == "execute":
        _, readonly = runtimes(
            repository, store, operation_root=execution / "operations", read_only=True
        )
        if readonly.replay(context, inputs, recorded_at=recorded_at) != result:
            raise ValueError("independent C2 replay differs")
        summary = execution_summary(result, request, decision_ref)
        publish(
            execution / "execution-result.json", canonical_review_eval_json(summary)
        )
        print(json.dumps(summary, sort_keys=True))
        return
    if args.mode == "basis":
        preparation, _ = runtimes(
            repository, store, operation_root=execution / "operations", read_only=True
        )
        identity = ReviewCorpusIdentityResolutionRuntime(
            execution / "operations",
            store,
            preparation,
            metadata_resolution_v2=runtime,
            read_only=True,
        )
        basis = identity.proposal_basis_v2(
            parent.inputs.preparation,
            metadata_resolution=result.artifact,
        )
        raw = canonical_review_eval_json(basis.model_dump(mode="json"))
        digest = hashlib.sha256(raw).hexdigest()
        publish(execution / "proposal-basis-v2.json", raw)
        print(
            json.dumps(
                execution_summary(result, request, decision_ref, digest), sort_keys=True
            )
        )
        return
    print(json.dumps(execution_summary(result, request, decision_ref), sort_keys=True))


if __name__ == "__main__":
    main()
