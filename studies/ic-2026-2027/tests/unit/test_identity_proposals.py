from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from itertools import pairwise
from pathlib import Path
from typing import Any

import pytest

from ic_study.literature import identity_proposals
from ic_study.literature.identity_proposals import (
    GeneratorInputs,
    InputFile,
    Proposals,
    ScopeFile,
    generate,
    write,
    zero_failure_sample_size,
)

Json = dict[str, Any]


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class Corpus:
    """Build a minimal records/deduplication/queue triple like result-3."""

    def __init__(self) -> None:
        self.records: list[Json] = []
        self.works: list[Json] = []
        self.candidates: dict[str, Json] = {}

    def work(
        self,
        title: str | None,
        year: int | None,
        authors: tuple[str, ...] = ("Ada Lovelace", "Charles Babbage"),
        identifiers: tuple[str, ...] = (),
        *,
        type_: str = "article",
        source: str = "openalex",
        abstract: str | None = None,
        venue: str | None = None,
        copies: int = 1,
        extra_titles: tuple[str, ...] = (),
        landing: str | None = None,
    ) -> str:
        record_ids = []
        for record_title in (title,) * copies + extra_titles:
            index = len(self.records)
            record_id = f"observation.{index:04d}"
            self.records.append(
                {
                    "abstract": abstract,
                    "authors": list(authors),
                    "identifiers": list(identifiers),
                    "landing_page_url": landing,
                    "language": None,
                    "publication_type": type_,
                    "publication_year": year,
                    "rank": 1,
                    "raw_artifact_sha256": _sha(f"raw-{index}".encode()),
                    "record_id": record_id,
                    "retrieved_at": "2026-09-12T00:00:00Z",
                    "schema_version": "1",
                    "search_id": "search.1",
                    "source_id": source,
                    "title": record_title,
                    "venue": venue,
                }
            )
            record_ids.append(record_id)
        work_id = "work.v2." + _sha(_canonical(sorted(record_ids)))[:24]
        self.works.append(
            {
                "canonical_title": title,
                "correction_status": "none_known",
                "identifiers": sorted(set(identifiers)),
                "manifestation_record_ids": sorted(record_ids),
                "merge_basis": "exact_identifier"
                if len(record_ids) > 1
                else "single_record",
                "publication_types": [type_],
                "publication_year": year,
                "schema_version": "2" if title is None else "1",
                "work_id": work_id,
                **({"metadata_status": "title_unavailable"} if title is None else {}),
            }
        )
        return work_id

    def merged_work(
        self,
        title: str,
        year: int,
        observations: list[tuple[str, str, tuple[str, ...]]],
        authors: tuple[str, ...] = ("Ada Lovelace", "Charles Babbage"),
    ) -> str:
        """Add one exact-identifier work whose observations differ in kind."""
        work_ids = [
            self.work(title, year, authors, ids, type_=kind, source=source)
            for source, kind, ids in observations
        ]
        parts = [w for w in self.works if w["work_id"] in work_ids]
        self.works = [w for w in self.works if w["work_id"] not in work_ids]
        record_ids = sorted(r for w in parts for r in w["manifestation_record_ids"])
        work_id = "work.v2." + _sha(_canonical(record_ids))[:24]
        self.works.append(
            {
                **parts[0],
                "identifiers": sorted({i for w in parts for i in w["identifiers"]}),
                "manifestation_record_ids": record_ids,
                "merge_basis": "exact_identifier",
                "publication_types": sorted({kind for _, kind, _ in observations}),
                "work_id": work_id,
            }
        )
        return work_id

    def pair(self, left: str, right: str) -> str:
        members = {w["work_id"]: w for w in self.works}
        record_ids = sorted(
            (
                members[left]["manifestation_record_ids"][0],
                members[right]["manifestation_record_ids"][0],
            )
        )
        by_record = {r["record_id"]: r for r in self.records}
        first, second = (by_record[r] for r in record_ids)
        signals = ["normalized_title_match"]
        if set(first["identifiers"]) & set(second["identifiers"]):
            signals.append("typed_work_identifier_match")
        candidate_id = "dedupe.v2." + _sha(_canonical(record_ids))[:24]
        self.candidates[candidate_id] = {
            "candidate_id": candidate_id,
            "disposition": "pending_human_adjudication",
            "record_ids": record_ids,
            "signals": sorted(signals),
        }
        return candidate_id

    def save(self, root: Path) -> GeneratorInputs:
        root.mkdir(parents=True, exist_ok=True)
        records = _canonical(self.records)
        titled: list[Json] = sorted(
            (w for w in self.works if w["canonical_title"] is not None),
            key=lambda w: str(w["work_id"]),
        )
        untitled: list[Json] = sorted(
            (w for w in self.works if w["canonical_title"] is None),
            key=lambda w: str(w["work_id"]),
        )
        by_record = {record["record_id"]: record for record in self.records}
        metadata_candidates: list[Json] = []
        for work in untitled:
            record_ids = work["manifestation_record_ids"]
            raw_hashes = sorted(
                {
                    by_record[record_id]["raw_artifact_sha256"]
                    for record_id in record_ids
                }
            )
            metadata_candidates.append(
                {
                    "candidate_id": "metadata.v1."
                    + _sha(
                        _canonical(
                            (work["work_id"], record_ids, ("title",), raw_hashes)
                        )
                    )[:24],
                    "work_id": work["work_id"],
                    "record_ids": record_ids,
                    "missing_fields": ["title"],
                    "raw_artifact_sha256s": raw_hashes,
                    "disposition": "pending_metadata_review",
                }
            )
        metadata_candidates.sort(key=lambda candidate: str(candidate["candidate_id"]))
        deduplication = _canonical(
            {
                "adjudication_candidates": [
                    self.candidates[key] for key in sorted(self.candidates)
                ],
                "algorithm_version": "2",
                "metadata_review_candidates": metadata_candidates,
                "schema_version": "3",
                "titled_works": titled,
                "untitled_works": untitled,
            }
        )
        queue = _canonical(
            {
                "deduplication": {"sha256": _sha(deduplication)},
                "identity_candidates": [
                    self.candidates[key] for key in sorted(self.candidates)
                ],
                "records": {"sha256": _sha(records)},
            }
        )
        files = {}
        for name, raw in (
            ("records", records),
            ("deduplication", deduplication),
            ("queue", queue),
        ):
            path = root / f"{name}.json"
            path.write_bytes(raw)
            files[name] = InputFile(path=path, sha256=_sha(raw))
        return GeneratorInputs(**files)


def _tiers(proposals: Proposals) -> dict[str, tuple[str, str]]:
    return {
        candidate: (card.tier, card.rule)
        for card in proposals.cards
        for candidate in card.candidate_ids
    }


def _run(corpus: Corpus, tmp_path: Path, seed: int = 7) -> Proposals:
    return generate(corpus.save(tmp_path / "inputs"), seed=seed)


def _ref(digest: str) -> Json:
    return {
        "sha256": digest,
        "size_bytes": 1,
        "media_type": "application/json",
        "relative_path": f"sha256/{digest[:2]}/{digest[2:4]}/{digest}",
        "access_class": "restricted",
    }


def _proposal_basis(
    corpus: Corpus,
    inputs: GeneratorInputs,
    root: Path,
    *,
    resolved: dict[str, str],
    overlay_pairs: tuple[tuple[str, str], ...],
) -> InputFile:
    original = json.loads(inputs.deduplication.path.read_bytes())
    works = {
        work["work_id"]: work
        for work in (*original["titled_works"], *original["untitled_works"])
    }
    for work_id, title in resolved.items():
        works[work_id] = {
            **{
                key: value
                for key, value in works[work_id].items()
                if key != "metadata_status"
            },
            "canonical_title": title,
            "schema_version": "1",
        }
    metadata_resolution = _ref(_sha(b"metadata-resolution"))
    records_by_id = {record["record_id"]: record for record in corpus.records}
    overlays = []
    for left, right in overlay_pairs:
        pair = tuple(sorted((left, right)))
        record_ids = sorted(
            works[work_id]["manifestation_record_ids"][0] for work_id in pair
        )
        choice_hash = _sha(b"metadata-choice")
        overlays.append(
            {
                "schema_version": "corpus-overlay-identity-candidate-1",
                "pair": {
                    "candidate_id": "dedupe.overlay."
                    + _sha(_canonical((pair, (choice_hash,))))[:24],
                    "disposition": "pending_human_adjudication",
                    "record_ids": record_ids,
                    "signals": [
                        "metadata_overlay_title_match",
                        "normalized_title_match",
                    ],
                },
                "source_work_ids": list(pair),
                "metadata_resolution": metadata_resolution,
                "metadata_choice_sha256s": [choice_hash],
                "source_artifact_sha256s": sorted(
                    records_by_id[record_id]["raw_artifact_sha256"]
                    for work_id in pair
                    for record_id in works[work_id]["manifestation_record_ids"]
                ),
            }
        )
    basis = {
        "schema_version": "corpus-identity-proposal-basis-1",
        "preparation": _ref(_sha(b"preparation")),
        "metadata_resolution": metadata_resolution,
        "records": _ref(inputs.records.sha256),
        "deduplication": _ref(inputs.deduplication.sha256),
        "queue": _ref(inputs.queue.sha256),
        "metadata_projection": _ref(_sha(b"metadata-projection")),
        "works": [works[key] for key in sorted(works)],
        "resolved_title_work_ids": sorted(resolved),
        "explicitly_untitled_work_ids": [],
        "unresolved_metadata_candidate_ids": sorted(
            candidate["candidate_id"]
            for candidate in original["metadata_review_candidates"]
            if candidate["work_id"] not in resolved
        ),
        "overlay_candidates": overlays,
        "source_artifact_sha256s": sorted(
            {record["raw_artifact_sha256"] for record in corpus.records}
        ),
        "proposal_only": True,
        "screening_ready": False,
        "scientific_eligibility_assessed": False,
    }
    raw = _canonical(basis)
    path = root / "proposal-basis.json"
    path.write_bytes(raw)
    return InputFile(path, _sha(raw))


ABSTRACT = " ".join(f"token{i}" for i in range(40))
OTHER_ABSTRACT = " ".join(f"other{i}" for i in range(40))
TITLE = "Bounded confidence dynamics on sparse random graphs"


def test_overlay_basis_adds_pair_for_resolved_title_without_changing_records(
    tmp_path: Path,
) -> None:
    corpus = Corpus()
    untitled = corpus.work(None, 2020, identifiers=("openalex:W1",))
    titled = corpus.work(TITLE, 2020, identifiers=("openalex:W2",))
    inputs = corpus.save(tmp_path / "inputs")
    original_records = inputs.records.path.read_bytes()
    assert generate(inputs, seed=7).cards == ()

    basis = _proposal_basis(
        corpus,
        inputs,
        tmp_path,
        resolved={untitled: TITLE},
        overlay_pairs=((untitled, titled),),
    )
    proposals = generate(replace(inputs, proposal_basis=basis), seed=7)

    assert len(proposals.cards) == 1
    assert proposals.cards[0].work_ids == tuple(sorted((untitled, titled)))
    assert proposals.cards[0].tier == "T1"
    assert proposals.cards[0].rule == "T1.title_year_authors"
    assert proposals.manifest_fields["proposal_basis"]["schema_version"] == (
        "corpus-identity-proposal-basis-1"
    )
    assert inputs.records.path.read_bytes() == original_records


def test_overlay_basis_must_bind_the_three_original_inputs(tmp_path: Path) -> None:
    corpus = Corpus()
    untitled = corpus.work(None, 2020, identifiers=("openalex:W1",))
    titled = corpus.work(TITLE, 2020, identifiers=("openalex:W2",))
    inputs = corpus.save(tmp_path / "inputs")
    basis = _proposal_basis(
        corpus,
        inputs,
        tmp_path,
        resolved={untitled: TITLE},
        overlay_pairs=((untitled, titled),),
    )
    value = json.loads(basis.path.read_bytes())
    value["deduplication"]["sha256"] = "0" * 64
    raw = _canonical(value)
    basis.path.write_bytes(raw)

    with pytest.raises(ValueError, match="basis deduplication"):
        generate(
            replace(inputs, proposal_basis=InputFile(basis.path, _sha(raw))), seed=7
        )


def test_overlay_basis_cannot_change_work_identity_fields(tmp_path: Path) -> None:
    corpus = Corpus()
    untitled = corpus.work(None, 2020, identifiers=("openalex:W1",))
    titled = corpus.work(TITLE, 2020, identifiers=("openalex:W2",))
    inputs = corpus.save(tmp_path / "inputs")
    basis = _proposal_basis(
        corpus,
        inputs,
        tmp_path,
        resolved={untitled: TITLE},
        overlay_pairs=((untitled, titled),),
    )
    value = json.loads(basis.path.read_bytes())
    next(work for work in value["works"] if work["work_id"] == untitled)[
        "publication_year"
    ] = 2021
    raw = _canonical(value)
    basis.path.write_bytes(raw)

    with pytest.raises(ValueError, match="basis work identity"):
        generate(
            replace(inputs, proposal_basis=InputFile(basis.path, _sha(raw))), seed=7
        )


def test_overlay_candidate_pair_must_match_source_works(tmp_path: Path) -> None:
    corpus = Corpus()
    untitled = corpus.work(None, 2020, identifiers=("openalex:W1",))
    titled = corpus.work(TITLE, 2020, identifiers=("openalex:W2",))
    inputs = corpus.save(tmp_path / "inputs")
    basis = _proposal_basis(
        corpus,
        inputs,
        tmp_path,
        resolved={untitled: TITLE},
        overlay_pairs=((untitled, titled),),
    )
    value = json.loads(basis.path.read_bytes())
    value["overlay_candidates"][0]["source_work_ids"] = [untitled, untitled]
    raw = _canonical(value)
    basis.path.write_bytes(raw)

    with pytest.raises(ValueError, match="overlay pair"):
        generate(
            replace(inputs, proposal_basis=InputFile(basis.path, _sha(raw))), seed=7
        )


def test_overlay_keeps_original_candidate_once(tmp_path: Path) -> None:
    corpus = Corpus()
    untitled = corpus.work(None, 2020, identifiers=("openalex:W1",))
    first = corpus.work(TITLE, 2020, identifiers=("openalex:W2",))
    second = corpus.work(TITLE, 2020, identifiers=("openalex:W3",))
    original_candidate = corpus.pair(first, second)
    inputs = corpus.save(tmp_path / "inputs")
    basis = _proposal_basis(
        corpus,
        inputs,
        tmp_path,
        resolved={untitled: TITLE},
        overlay_pairs=((untitled, first),),
    )

    proposals = generate(replace(inputs, proposal_basis=basis), seed=7)

    candidate_ids = [
        candidate_id for card in proposals.cards for candidate_id in card.candidate_ids
    ]
    assert len(proposals.cards) == 2
    assert len(candidate_ids) == len(set(candidate_ids)) == 2
    assert original_candidate in candidate_ids
    assert proposals.manifest_fields["counts"]["candidates"] == 2


def test_explicitly_untitled_basis_keeps_null_title(tmp_path: Path) -> None:
    corpus = Corpus()
    untitled = corpus.work(None, 2020, identifiers=("openalex:W1",))
    inputs = corpus.save(tmp_path / "inputs")
    basis = _proposal_basis(corpus, inputs, tmp_path, resolved={}, overlay_pairs=())
    value = json.loads(basis.path.read_bytes())
    value["explicitly_untitled_work_ids"] = [untitled]
    value["unresolved_metadata_candidate_ids"] = []
    raw = _canonical(value)
    basis.path.write_bytes(raw)

    proposals = generate(
        replace(inputs, proposal_basis=InputFile(basis.path, _sha(raw))), seed=7
    )

    assert proposals.cards == ()
    assert proposals.manifest_fields["proposal_basis"][
        "explicitly_untitled_work_ids"
    ] == [untitled]


def test_basis_rejects_falsely_omitted_unresolved_metadata_candidate(
    tmp_path: Path,
) -> None:
    corpus = Corpus()
    corpus.work(None, 2020, identifiers=("openalex:W1",))
    inputs = corpus.save(tmp_path / "inputs")
    basis = _proposal_basis(corpus, inputs, tmp_path, resolved={}, overlay_pairs=())
    value = json.loads(basis.path.read_bytes())
    value["unresolved_metadata_candidate_ids"] = []
    raw = _canonical(value)
    basis.path.write_bytes(raw)

    with pytest.raises(ValueError, match="metadata candidate partition"):
        generate(
            replace(inputs, proposal_basis=InputFile(basis.path, _sha(raw))), seed=7
        )


def test_basis_rejects_invalid_metadata_projection_ref(tmp_path: Path) -> None:
    corpus = Corpus()
    corpus.work(None, 2020, identifiers=("openalex:W1",))
    inputs = corpus.save(tmp_path / "inputs")
    basis = _proposal_basis(corpus, inputs, tmp_path, resolved={}, overlay_pairs=())
    value = json.loads(basis.path.read_bytes())
    value["metadata_projection"]["relative_path"] = "../projection.json"
    raw = _canonical(value)
    basis.path.write_bytes(raw)

    with pytest.raises(ValueError, match="basis metadata_projection artifact ref"):
        generate(
            replace(inputs, proposal_basis=InputFile(basis.path, _sha(raw))), seed=7
        )


def test_identifier_rules_merge_same_manifestation(tmp_path: Path) -> None:
    corpus = Corpus()
    shared_left = corpus.work(TITLE, 2020, identifiers=("doi:10.1000/a", "openalex:W1"))
    shared_right = corpus.work(
        TITLE, 2021, identifiers=("doi:10.1000/a", "openalex:W2")
    )
    shared = corpus.pair(shared_left, shared_right)
    preprint = corpus.work(
        TITLE + " revisited", 2019, identifiers=("arxiv:1901.00001",), type_="preprint"
    )
    arxiv_doi = corpus.work(
        TITLE + " revisited",
        2019,
        identifiers=("doi:10.48550/arxiv.1901.00001", "openalex:W3"),
        type_="preprint",
    )
    corr = corpus.work(
        TITLE + " revisited",
        2019,
        identifiers=("dblp:journals/corr/abs-1901-00001",),
        type_="other",
        source="dblp",
    )
    doi_link = corpus.pair(preprint, arxiv_doi)
    corr_link = corpus.pair(arxiv_doi, corr)

    published = corpus.work(
        TITLE + " extended",
        2021,
        identifiers=("doi:10.1103/pre.1",),
        type_="journal_article",
        source="crossref",
    )
    version_link = corpus.pair(
        published,
        corpus.work(
            TITLE + " extended",
            2021,
            identifiers=("arxiv:2101.00003", "doi:10.1103/pre.1"),
            type_="preprint",
            source="arxiv",
        ),
    )
    merged = corpus.merged_work(
        TITLE + " merged",
        2021,
        [
            ("arxiv", "preprint", ("arxiv:2104.03485", "doi:10.1109/cdc.1")),
            ("dblp", "other", ("dblp:conf/cdc/Gao21", "doi:10.1109/cdc.1")),
        ],
    )
    corr_duplicate = corpus.pair(
        merged,
        corpus.work(
            TITLE + " merged",
            2021,
            identifiers=("dblp:journals/corr/abs-2104-03485",),
            type_="other",
            source="dblp",
        ),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[shared] == ("T1", "T1.shared_identifier")
    assert tiers[doi_link] == ("T1", "T1.arxiv_link")
    assert tiers[corr_link] == ("T1", "T1.arxiv_link")
    assert tiers[version_link] == ("T2", "T2.version")
    assert tiers[corr_duplicate] == ("T1", "T1.arxiv_link")


def test_identifier_link_with_contradicting_evidence_needs_judgment(
    tmp_path: Path,
) -> None:
    corpus = Corpus()
    left = corpus.work(
        TITLE, 2020, identifiers=("arxiv:2001.00001", "doi:10.1000/a"), type_="preprint"
    )
    right = corpus.work(
        TITLE,
        2020,
        identifiers=("doi:10.48550/arxiv.2001.00001", "doi:10.2000/b"),
        type_="preprint",
    )
    contradicted = corpus.pair(left, right)
    renamed_left = corpus.work(
        "A study of voter models", 2020, identifiers=("doi:10.3000/c",)
    )
    renamed_right = corpus.work(
        "Polarization in echo chambers", 2020, identifiers=("doi:10.3000/c",)
    )
    renamed = corpus.pair(renamed_left, renamed_right)
    stranger = corpus.work(TITLE + " II", 2020, ("Grace Hopper",), ("doi:10.4000/d",))
    known = corpus.work(TITLE + " II", 2020, ("Ada Lovelace",), ("doi:10.4000/d",))
    strangers = corpus.pair(stranger, known)

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[contradicted] == ("T4", "T4.contradicting_identifiers")
    assert tiers[renamed] == ("T4", "T4.identifier_link_mismatch")
    assert tiers[strangers] == ("T4", "T4.identifier_link_mismatch")


def test_title_year_authors_rule_and_its_contradictions(tmp_path: Path) -> None:
    corpus = Corpus()
    authors = ("Ada Lovelace", "Charles Babbage")
    exact = corpus.pair(
        corpus.work(TITLE, 2020, authors, abstract=ABSTRACT),
        corpus.work(TITLE, 2020, ("Charles Babbage", "Ada Lovelace"), source="dblp"),
    )
    dblp_conflict = corpus.pair(
        corpus.work(TITLE + " A", 2020, authors, ("dblp:conf/x/A20",), type_="other"),
        corpus.work(TITLE + " A", 2020, authors, ("dblp:conf/y/A20",), type_="other"),
    )
    doi_conflict = corpus.pair(
        corpus.work(TITLE + " B", 2020, authors, ("doi:10.1000/x",)),
        corpus.work(TITLE + " B", 2020, authors, ("doi:10.2000/y",)),
    )
    venue_conflict = corpus.pair(
        corpus.work(TITLE + " C", 2020, authors, type_="conference_paper"),
        corpus.work(TITLE + " C", 2020, authors, type_="journal_article"),
    )
    generic = corpus.pair(
        corpus.work("Introduction", 2020, authors),
        corpus.work("Introduction", 2020, authors),
    )
    abstract_conflict = corpus.pair(
        corpus.work(TITLE + " D", 2020, authors, abstract=ABSTRACT),
        corpus.work(TITLE + " D", 2020, authors, abstract=OTHER_ABSTRACT),
    )

    cjk = "唐十郎作『安寿子の靴(1984)』の二人の「やすこ」記憶で理想化された"
    same_script = corpus.pair(
        corpus.work(cjk, 2026, ("Yasuko Kawahata", "Taro Yamada")),
        corpus.work(cjk, 2026, ("Yasuko Kawahata", "Taro Yamada")),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[exact] == ("T1", "T1.title_year_authors")
    assert tiers[same_script] == ("T1", "T1.title_year_authors")
    assert tiers[dblp_conflict] == ("T4", "T4.contradicting_identifiers")
    assert tiers[doi_conflict] == ("T4", "T4.contradicting_identifiers")
    assert tiers[venue_conflict] == ("T4", "T4.conference_vs_journal")
    assert tiers[generic] == ("T4", "T4.ambiguous_title")
    assert tiers[abstract_conflict] == ("T4", "T4.abstract_divergence")


def test_author_names_are_compared_by_family_name(tmp_path: Path) -> None:
    corpus = Corpus()
    inverted = corpus.pair(
        corpus.work(
            TITLE,
            2024,
            ("Romero Longar, Maria Celeste", "Saintier, Nicolas Bernard Claude"),
        ),
        corpus.work(TITLE, 2024, ("María Celeste Romero Longar", "Nicolas Saintier")),
    )
    stroked = corpus.pair(
        corpus.work(TITLE + " A", 2007, ("D. Stauffer", "K. Kułakowski")),
        corpus.work(TITLE + " A", 2007, ("Dietrich Stauffer", "Krzysztof Kulakowski")),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[inverted] == ("T1", "T1.title_year_authors")
    assert tiers[stroked] == ("T1", "T1.title_year_authors")


def test_version_rule_requires_policy_and_bounds(tmp_path: Path) -> None:
    corpus = Corpus()
    five = ("Ada Lovelace", "Alan Turing", "Grace Hopper", "Emmy Noether", "Kurt Godel")
    four = five[:4]
    preprint = corpus.pair(
        corpus.work(TITLE, 2020, five, ("arxiv:2001.00002",), type_="preprint"),
        corpus.work(TITLE, 2020, five, ("doi:10.1000/journal",)),
    )
    gap = corpus.pair(
        corpus.work(TITLE + " A", 2019, five, type_="preprint"),
        corpus.work(TITLE + " A", 2021, five, ("doi:10.1000/a",)),
    )
    variant = corpus.pair(
        corpus.work(TITLE + " B", 2020, five),
        corpus.work(TITLE + " B", 2020, four),
    )
    repository_copy = corpus.pair(
        corpus.work(TITLE + " E", 2025, five, ("doi:10.32628/ijsrset.1",)),
        corpus.work(TITLE + " E", 2025, five, ("doi:10.5281/zenodo.21579137",)),
    )
    too_late = corpus.pair(
        corpus.work(TITLE + " C", 2018, five, type_="preprint"),
        corpus.work(TITLE + " C", 2021, five),
    )
    partial = corpus.pair(
        corpus.work(TITLE + " D", 2020, five),
        corpus.work(TITLE + " D", 2020, five[:3]),
    )

    proposals = _run(corpus, tmp_path)
    tiers = _tiers(proposals)
    notes = {c: card.notes for card in proposals.cards for c in card.candidate_ids}

    assert tiers[preprint] == ("T2", "T2.version")
    assert "preprint_vs_published" in notes[preprint]
    assert tiers[gap] == ("T2", "T2.version")
    assert "year_gap" in notes[gap]
    assert tiers[variant] == ("T2", "T2.version")
    assert notes[variant] == ("author_list_variant",)
    assert tiers[repository_copy] == ("T2", "T2.version")
    assert notes[repository_copy] == ("preprint_vs_published", "doi_divergence")
    assert tiers[too_late] == ("T4", "T4.year_gap")
    assert tiers[partial] == ("T4", "T4.partial_author_evidence")
    assert proposals.manifest_fields["owner_policy_required"]["T2"]


def test_distinct_rules_are_conservative(tmp_path: Path) -> None:
    corpus = Corpus()
    disjoint = corpus.pair(
        corpus.work("The name game", 2010, ("Lorraine Midanik",)),
        corpus.work("The name game", 2015, ("David Newnham",)),
    )
    same_abstract = corpus.pair(
        corpus.work(TITLE, 2009, ("Kazimierz Slomczynski",), abstract=ABSTRACT),
        corpus.work(TITLE, 2009, ("Goldie Shabad",), abstract=ABSTRACT),
    )
    glued_names = corpus.pair(
        corpus.work(TITLE + " A", 2015, ("Caterina Liberati", "Furio Camillo")),
        corpus.work(TITLE + " A", 2015, ("LiberatiCaterina", "CamilloFurio")),
    )
    generic_apart = corpus.pair(
        corpus.work("Editorial", 2003, (), ("doi:10.1000/a",)),
        corpus.work("Editorial", 2012, (), ("doi:10.2000/b",)),
    )
    generic_same_issue = corpus.pair(
        corpus.work("Editorial", 2019, (), venue="Physica A"),
        corpus.work("Editorial", 2019, ("Ada Lovelace",), venue="Physica A"),
    )
    script_loss = corpus.pair(
        corpus.work(
            "ジオ分析 電話帳データ 2026 Kawahata series", 2026, ("Yasuko Kawahata",)
        ),
        corpus.work(
            "リサイクル店舗 電話帳データ 2026 Kawahata series",
            2026,
            ("Yasuko Kawahata",),
        ),
    )
    specific_without_authors = corpus.pair(
        corpus.work(TITLE + " B", 2003, ()),
        corpus.work(TITLE + " B", 2012, ()),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[disjoint] == ("T3", "T3.disjoint_authors")
    assert tiers[same_abstract][0] == "T4"
    assert tiers[glued_names][0] == "T4"
    assert tiers[generic_apart] == ("T3", "T3.generic_title_without_match")
    assert tiers[generic_same_issue] == ("T4", "T4.ambiguous_title")
    assert tiers[specific_without_authors][0] == "T4"
    assert tiers[script_loss] == ("T4", "T4.ambiguous_title")


def test_transitive_merge_contradiction_demotes_the_whole_group(
    tmp_path: Path,
) -> None:
    corpus = Corpus()
    left = corpus.work(TITLE, 2020, identifiers=("doi:10.1000/a",))
    middle = corpus.work(TITLE, 2020)
    right = corpus.work(TITLE, 2020, identifiers=("doi:10.2000/b",))
    first = corpus.pair(left, middle)
    second = corpus.pair(middle, right)
    direct = corpus.pair(left, right)
    clean_left = corpus.work(TITLE + " A", 2020)
    clean_right = corpus.work(TITLE + " A", 2020)
    clean = corpus.pair(clean_left, clean_right)

    proposals = _run(corpus, tmp_path)
    tiers = _tiers(proposals)

    assert tiers[direct] == ("T4", "T4.contradicting_identifiers")
    assert tiers[first] == ("T4", "T4.transitive_merge_contradiction")
    assert tiers[second] == ("T4", "T4.transitive_merge_contradiction")
    assert tiers[clean] == ("T1", "T1.title_year_authors")
    joined = proposals.manifest_fields["transitive"]
    assert joined["T1"]["demoted_cards"] == 2


def test_distinct_choices_never_contradict_proposed_merges(tmp_path: Path) -> None:
    corpus = Corpus()
    team = ("Ada Lovelace", "Alan Turing")
    a = corpus.work(TITLE, 2020, team, abstract=ABSTRACT)
    b = corpus.work(TITLE, 2020, team)
    c = corpus.work(TITLE, 2020, team, abstract=OTHER_ABSTRACT)
    d = corpus.work(TITLE + " (reply)", 2014, ("Grace Hopper",))
    for left, right in ((a, b), (b, c), (a, d), (c, d)):
        corpus.pair(left, right)
    implied = corpus.pair(a, c)

    proposals = _run(corpus, tmp_path)

    groups = proposals.merge_groups("T1+T2")
    group_of = {work: index for index, group in enumerate(groups) for work in group}
    distinct = [card for card in proposals.cards if card.tier == "T3"]
    assert len(distinct) == 2
    for card in distinct:
        left, right = card.work_ids
        assert left not in group_of or group_of[left] != group_of.get(right)
    (card,) = [card for card in proposals.cards if implied in card.candidate_ids]
    assert card.rule == "T4.abstract_divergence"
    assert {"joined_by_T1", "joined_by_T1+T2"} <= set(card.notes)
    assert proposals.manifest_fields["transitive"]["T1"]["joined_pending_cards"] == 1


def test_choice_lists_have_the_c3_pair_choice_shape(tmp_path: Path) -> None:
    corpus = Corpus()
    a = corpus.work(TITLE, 2020, copies=2)
    b = corpus.work(TITLE, 2020)
    corpus.pair(a, b)
    corpus.pair(
        corpus.work("The name game", 2010, ("Lorraine Midanik",)),
        corpus.work("The name game", 2015, ("David Newnham",)),
    )
    corpus.pair(
        corpus.work(TITLE + " A", 2019, type_="preprint"),
        corpus.work(TITLE + " A", 2020),
    )
    corpus.pair(corpus.work(TITLE + " B", 2001), corpus.work(TITLE + " B", 2020))

    proposals = _run(corpus, tmp_path)

    seen: list[str] = []
    for unit, disposition in (
        ("T1-identifier", "merge"),
        ("T1-title", "merge"),
        ("T2", "merge"),
        ("T3", "distinct"),
    ):
        choices = proposals.choices[unit]
        assert choices or unit == "T1-identifier"
        assert all(set(item) == {"candidate_id", "disposition"} for item in choices)
        assert {item["disposition"] for item in choices} <= {disposition}
        ids = [item["candidate_id"] for item in choices]
        assert ids == sorted(set(ids))
        seen.extend(ids)
    seen.extend(c for card in proposals.worklist for c in card["candidate_ids"])
    assert sorted(seen) == sorted(corpus.candidates)


def test_identifier_choices_follow_final_merged_groups(tmp_path: Path) -> None:
    corpus = Corpus()
    left = corpus.work(TITLE, 2020, identifiers=("doi:10.1000/a", "openalex:W1"))
    right = corpus.work(TITLE, 2020, identifiers=("doi:10.1000/a", "openalex:W2"))
    corpus.pair(left, right)
    plural = corpus.work(
        TITLE + " A", 2020, identifiers=("doi:10.1000/b", "doi:10.1000/c")
    )
    single = corpus.work(TITLE + " A", 2020, identifiers=("doi:10.1000/b",))
    corpus.pair(plural, single)

    proposals = _run(corpus, tmp_path)

    (choice,) = proposals.identifier_choices["T1"]
    conflict = choice["conflict"]
    records = sorted(
        r["record_id"]
        for r in corpus.records
        if r["identifiers"] and r["identifiers"][0] == "doi:10.1000/a"
    )
    assert conflict["work_id"] == "work.v2." + _sha(_canonical(records))[:24]
    assert conflict["manifestation_record_ids"] == records
    assert conflict["identifiers"] == ["doi:10.1000/a", "openalex:W1", "openalex:W2"]
    assert conflict["conflicting_identifier_kinds"] == ["openalex"]
    assert choice["disposition"] == "same_work_identifiers"
    assert choice["rationale"].strip() == choice["rationale"]
    (pending,) = proposals.pending_identifier_conflicts["T1"]
    assert pending["conflicting_identifier_kinds"] == ["doi"]


def _population(corpus: Corpus, count: int) -> None:
    for index in range(count):
        corpus.pair(
            corpus.work(f"{TITLE} {index}", 2020),
            corpus.work(f"{TITLE} {index}", 2020),
        )
    for index in range(count // 3):
        shared = f"doi:10.1000/v{index}"
        corpus.pair(
            corpus.work(
                f"Voter model {index} on lattices",
                2020,
                identifiers=(shared, f"openalex:W{2 * index + 1}"),
            ),
            corpus.work(
                f"Voter model {index} on lattices",
                2020,
                identifiers=(shared, f"openalex:W{2 * index + 2}"),
            ),
        )
        corpus.pair(
            corpus.work(
                f"Axelrod model {index} with noise",
                2019,
                identifiers=(f"arxiv:1901.{index:05d}",),
                type_="preprint",
            ),
            corpus.work(
                f"Axelrod model {index} with noise",
                2019,
                identifiers=(f"doi:10.48550/arxiv.1901.{index:05d}",),
                type_="preprint",
            ),
        )


def test_audit_sample_is_seeded_and_stratified(tmp_path: Path) -> None:
    corpus = Corpus()
    _population(corpus, 90)

    first = _run(corpus, tmp_path / "a", seed=11)
    again = _run(corpus, tmp_path / "b", seed=11)
    other = _run(corpus, tmp_path / "c", seed=12)

    units = first.audit_sample["units"]
    assert set(units) == {"T1-identifier", "T1-title", "T2", "T3"}
    sample = units["T1-identifier"]
    population = sum(sample["strata_population"].values())
    assert population == 60
    assert sample["required_sample_size"] == zero_failure_sample_size(population)
    assert sum(sample["strata_allocation"].values()) >= sample["required_sample_size"]
    assert set(sample["strata_allocation"]) == set(sample["strata_population"])
    assert set(sample["strata_population"]) == {"T1.arxiv_link", "T1.shared_identifier"}
    assert all(n >= 1 for n in sample["strata_allocation"].values())
    title = units["T1-title"]
    assert sum(title["strata_population"].values()) == 90
    assert title["required_sample_size"] == zero_failure_sample_size(90)
    cards = {card.work_ids: card for card in first.cards}
    for item in sample["cards"]:
        card = cards[tuple(item["work_ids"])]
        assert card.rule in {"T1.arxiv_link", "T1.shared_identifier"}
        assert card.rule == item["stratum"]
    for item in title["cards"]:
        assert cards[tuple(item["work_ids"])].rule == "T1.title_year_authors"
    assert first.audit_sample == again.audit_sample
    assert first.audit_sample["seed"] == 11
    assert other.audit_sample["units"]["T1-title"]["cards"] != title["cards"]


def test_zero_failure_sample_size_matches_hypergeometric_bound() -> None:
    assert zero_failure_sample_size(0) == 0
    assert zero_failure_sample_size(10) == 10
    assert zero_failure_sample_size(100) == 78
    sizes = [zero_failure_sample_size(n) for n in (1_000, 5_000, 50_000)]
    assert sizes == sorted(sizes)
    assert sizes[-1] <= 149


def test_outputs_are_deterministic_and_bound_by_the_manifest(tmp_path: Path) -> None:
    corpus = Corpus()
    _population(corpus, 12)
    inputs = corpus.save(tmp_path / "inputs")

    first = write(generate(inputs, seed=3), tmp_path / "out-a", revision="abc")
    second = write(generate(inputs, seed=3), tmp_path / "out-b", revision="abc")

    names = sorted(p.name for p in (tmp_path / "out-a").rglob("*") if p.is_file())
    assert "manifest.json" in names
    for path in (tmp_path / "out-a").rglob("*"):
        if path.is_file():
            twin = tmp_path / "out-b" / path.relative_to(tmp_path / "out-a")
            assert path.read_bytes() == twin.read_bytes()
    manifest = json.loads((tmp_path / "out-a" / "manifest.json").read_bytes())
    assert manifest == first == second
    assert manifest["git_revision"] == "abc"
    assert manifest["generator"]["module"] == "ic_study.literature.identity_proposals"
    assert manifest["owner_decisions"] == []
    assert {item["role"]: item["sha256"] for item in manifest["inputs"]} == {
        "records": inputs.records.sha256,
        "deduplication": inputs.deduplication.sha256,
        "queue": inputs.queue.sha256,
    }
    for item in manifest["outputs"]:
        raw = (tmp_path / "out-a" / item["path"]).read_bytes()
        assert item["sha256"] == _sha(raw)
        assert item["size_bytes"] == len(raw)
    listed = {item["path"] for item in manifest["outputs"]} | {"manifest.json"}
    on_disk = {
        str(p.relative_to(tmp_path / "out-a"))
        for p in (tmp_path / "out-a").rglob("*")
        if p.is_file()
    }
    assert listed == on_disk


def test_inputs_are_hash_verified_and_outputs_never_overwrite(tmp_path: Path) -> None:
    corpus = Corpus()
    _population(corpus, 3)
    inputs = corpus.save(tmp_path / "inputs")
    forged = GeneratorInputs(
        records=InputFile(inputs.records.path, "0" * 64),
        deduplication=inputs.deduplication,
        queue=inputs.queue,
    )
    with pytest.raises(ValueError, match="SHA-256"):
        generate(forged, seed=1)

    proposals = generate(inputs, seed=1)
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(FileExistsError):
        write(proposals, existing, revision="abc")
    assert list(existing.iterdir()) == []
    with pytest.raises(ValueError, match="protected"):
        write(proposals, tmp_path / "inputs" / "out", revision="abc")
    assert not (tmp_path / "inputs" / "out").exists()


def test_queue_must_match_the_deduplication_result(tmp_path: Path) -> None:
    corpus = Corpus()
    _population(corpus, 3)
    inputs = corpus.save(tmp_path / "inputs")
    queue = json.loads(inputs.queue.path.read_bytes())
    queue["identity_candidates"] = queue["identity_candidates"][1:]
    raw = _canonical(queue)
    inputs.queue.path.write_bytes(raw)
    tampered = GeneratorInputs(
        records=inputs.records,
        deduplication=inputs.deduplication,
        queue=InputFile(inputs.queue.path, _sha(raw)),
    )

    with pytest.raises(ValueError, match="queue"):
        generate(tampered, seed=1)


def test_t1_groups_never_mix_manifestations(tmp_path: Path) -> None:
    corpus = Corpus()
    team = ("Ada Lovelace", "Charles Babbage")
    ssrn = corpus.work(TITLE, 2020, team, ("doi:10.2139/ssrn.1",), type_="preprint")
    bare = corpus.work(TITLE, 2020, team, type_="preprint")
    osf = corpus.work(
        TITLE, 2020, team, ("doi:10.31219/osf.io/abcde",), type_="preprint"
    )
    first = corpus.pair(ssrn, bare)
    second = corpus.pair(bare, osf)
    copies = corpus.pair(ssrn, osf)
    title = TITLE + " revisited"
    loose = corpus.work(title, 2021, team, type_="preprint")
    arxiv = corpus.work(title, 2021, team, ("arxiv:2101.00009",), type_="preprint")
    published = corpus.merged_work(
        title,
        2021,
        [
            ("arxiv", "preprint", ("arxiv:2101.00009", "doi:10.1103/pre.9")),
            ("crossref", "journal_article", ("doi:10.1103/pre.9",)),
        ],
        team,
    )
    chained = corpus.pair(loose, arxiv)
    linked = corpus.pair(arxiv, published)
    versions = corpus.pair(loose, published)

    proposals = _run(corpus, tmp_path)
    by_candidate = {c: card for card in proposals.cards for c in card.candidate_ids}

    assert by_candidate[copies].tier == "T2"
    assert by_candidate[versions].tier == "T2"
    for moved in (first, second, chained, linked):
        assert by_candidate[moved].tier == "T2"
        assert "mixed_manifestation_group" in by_candidate[moved].notes
    assert not [
        card
        for card in proposals.cards
        if card.tier == "T2" and "joined_by_T1" in card.notes
    ]
    assert proposals.manifest_fields["transitive"]["T1"]["version_moved_cards"] == 4


def test_arxiv_and_repository_copies_are_preprint_like(tmp_path: Path) -> None:
    corpus = Corpus()
    team = ("Ada Lovelace", "Charles Babbage")
    typed_article = corpus.pair(
        corpus.work(
            TITLE,
            2021,
            team,
            ("doi:10.48550/arxiv.2101.00005", "openalex:W11"),
            type_="article",
        ),
        corpus.work(TITLE, 2021, team, ("doi:10.1038/s41598.1",), type_="article"),
    )
    zenodo_article = corpus.pair(
        corpus.work(TITLE + " A", 2021, team, ("doi:10.5281/zenodo.7",)),
        corpus.work(TITLE + " A", 2021, team, ("doi:10.1038/s41598.2",)),
    )
    arxiv_vs_square = corpus.pair(
        corpus.work(
            TITLE + " B",
            2021,
            team,
            ("arxiv:2101.00006",),
            type_="preprint",
            source="arxiv",
        ),
        corpus.work(
            TITLE + " B",
            2021,
            team,
            ("doi:10.21203/rs.3.rs-1/v1",),
            type_="preprint",
        ),
    )

    proposals = _run(corpus, tmp_path)
    by_candidate = {c: card for card in proposals.cards for c in card.candidate_ids}

    for candidate in (typed_article, zenodo_article):
        assert by_candidate[candidate].tier == "T2"
        assert "preprint_vs_published" in by_candidate[candidate].notes
    assert by_candidate[arxiv_vs_square].tier == "T2"
    assert by_candidate[arxiv_vs_square].notes == ("doi_divergence",)


def test_author_strings_and_titles_are_parsed_robustly(tmp_path: Path) -> None:
    corpus = Corpus()
    team = ("Ada Lovelace", "Charles Babbage")
    joined = corpus.pair(
        corpus.work(
            TITLE, 2025, ("Sukhdev Singh Dhanju, Dinesh Sharma, Payal Tangri",)
        ),
        corpus.work(
            TITLE, 2025, ("Sukhdev Singh Dhanju", "Dinesh Sharma", "Payal Tangri")
        ),
    )
    separated = corpus.pair(
        corpus.work(
            TITLE + " A",
            1990,
            ("Breen, Michael; Shoemaker, Pamela J. And Stamper, Marjorie",),
        ),
        corpus.work(
            TITLE + " A",
            1990,
            ("Michael Breen", "Pamela J. Shoemaker", "Marjorie Stamper"),
        ),
    )
    affiliation = corpus.pair(
        corpus.work(
            TITLE + " B",
            2002,
            (
                "Rainer Hegselmann",
                ",Bayreuth University, Universitaetsstrasse 30, 95440 Bayreuth",
                "Ulrich Krause",
                "Ossa, Ralph; https://orcid.org/0000-0003-4161-2567",
                ",Dept. of Mathematics, UCLA, Los Angeles, CA 90095-1555, USA",
            ),
        ),
        corpus.work(
            TITLE + " B", 2002, ("Rainer Hegselmann", "Ulrich Krause", "Ralph Ossa")
        ),
    )
    latex = corpus.pair(
        corpus.work(TITLE + " C", 2021, ('Neuh\\"auser, Leonie', "Michael T. Schaub")),
        corpus.work(TITLE + " C", 2021, ("Leonie Neuhäuser", "Michael T. Schaub")),
    )
    degrees = corpus.pair(
        corpus.work(
            TITLE + " D",
            2024,
            (
                "Prof. Dr. Yoesoep Edhie Rachmad, Ph.D, DBA",
                "Varma, Vineeth, S.",
                "Banducci, S, University of Exeter",
            ),
        ),
        corpus.work(
            TITLE + " D",
            2024,
            ("Yoesoep Edhie Rachmad", "Vineeth S. Varma", "Susan Banducci"),
        ),
    )
    parenthetical = corpus.pair(
        corpus.work(
            TITLE + " E",
            2019,
            (
                "Tomasz Radzik (5366132)",
                "Jennifer A. Clapp (University of Waterloo)",
                "Norrodzoh @ Nor Raudah Hj Siren",
            ),
        ),
        corpus.work(
            TITLE + " E",
            2019,
            ("Tomasz Radzik", "Jennifer Clapp", "Nor Raudah Siren"),
        ),
    )
    escaped = corpus.pair(
        corpus.work(
            "Noisy bounded confidence models: the effect of\\n boundary conditions",
            2023,
            team,
        ),
        corpus.work(
            "Noisy bounded confidence models: the effect of boundary conditions",
            2023,
            team,
        ),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    for candidate in (
        joined,
        separated,
        affiliation,
        latex,
        degrees,
        parenthetical,
        escaped,
    ):
        assert tiers[candidate] == ("T1", "T1.title_year_authors")


def test_title_only_merges_resting_on_one_surname_need_abstract_support(
    tmp_path: Path,
) -> None:
    corpus = Corpus()
    solo = ("Brian Hill",)
    bare = corpus.pair(corpus.work(TITLE, 2008, solo), corpus.work(TITLE, 2008, solo))
    supported = corpus.pair(
        corpus.work(TITLE + " A", 2008, solo, abstract=ABSTRACT),
        corpus.work(TITLE + " A", 2008, solo, abstract=ABSTRACT),
    )
    version = corpus.pair(
        corpus.work(TITLE + " B", 2008, solo, type_="preprint"),
        corpus.work(TITLE + " B", 2009, solo, ("doi:10.1007/s11225.1",)),
    )
    identifier = corpus.pair(
        corpus.work(TITLE + " C", 2008, solo, ("doi:10.1007/s11225.2", "openalex:W1")),
        corpus.work(TITLE + " C", 2008, solo, ("doi:10.1007/s11225.2", "openalex:W2")),
    )

    proposals = _run(corpus, tmp_path)
    tiers = _tiers(proposals)

    assert tiers[bare] == ("T4", "T4.single_author_title_match")
    assert tiers[version] == ("T4", "T4.single_author_title_match")
    assert tiers[supported] == ("T1", "T1.title_year_authors")
    assert tiers[identifier] == ("T1", "T1.shared_identifier")
    assert [c["candidate_id"] for c in proposals.choices["T1-title"]] == [supported]
    assert [c["candidate_id"] for c in proposals.choices["T1-identifier"]] == [
        identifier
    ]
    assert set(proposals.identifier_choices) == {"T1-identifier", "T1", "T1+T2"}


NATO = [
    "Alfa",
    "Bravo",
    "Charlie",
    "Delta",
    "Echo",
    "Foxtrot",
    "Golf",
    "Hotel",
    "India",
    "Juliett",
    "Kilo",
    "Lima",
    "Mike",
    "November",
    "Oscar",
    "Papa",
    "Quebec",
    "Romeo",
    "Sierra",
    "Tango",
]


def _drift_chain(corpus: Corpus) -> list[str]:
    """Eleven same-year works; neighbours share 9 of 10 authors and a title."""
    return [
        corpus.work(
            f"{TITLE} drift {index}",
            2020,
            tuple(NATO[index : index + 10]),
            extra_titles=(f"{TITLE} drift {index + 1}",),
        )
        for index in range(11)
    ]


def test_group_year_spread_is_a_version_or_a_contradiction(tmp_path: Path) -> None:
    corpus = Corpus()
    title = TITLE + " spread"
    a = corpus.work(title, 2019, identifiers=("arxiv:1901.00011",), type_="preprint")
    b = corpus.work(
        title,
        2020,
        identifiers=("doi:10.48550/arxiv.1901.00011", "openalex:W21"),
        type_="preprint",
    )
    c = corpus.work(title, 2021, identifiers=("openalex:W21",), type_="preprint")
    two_years = [corpus.pair(a, b), corpus.pair(b, c)]
    title = TITLE + " wide"
    d = corpus.work(title, 2018, identifiers=("arxiv:1801.00012",), type_="preprint")
    e = corpus.work(
        title,
        2019,
        identifiers=("doi:10.48550/arxiv.1801.00012", "openalex:W31"),
        type_="preprint",
    )
    f = corpus.work(
        title, 2020, identifiers=("openalex:W31", "openalex:W32"), type_="preprint"
    )
    g = corpus.work(title, 2021, identifiers=("openalex:W32",), type_="preprint")
    three_years = [corpus.pair(d, e), corpus.pair(e, f), corpus.pair(f, g)]
    title = TITLE + " versions"
    h = corpus.work(title, 2018, type_="preprint")
    i = corpus.work(title, 2020, identifiers=("doi:10.1103/pre.20",))
    j = corpus.work(title, 2022, type_="preprint")
    t2_chain = [corpus.pair(h, i), corpus.pair(i, j)]

    tiers = _tiers(_run(corpus, tmp_path))

    assert [tiers[c] for c in two_years] == [("T2", "T2.version")] * 2
    assert [tiers[c] for c in three_years] == [
        ("T4", "T4.transitive_merge_contradiction")
    ] * 3
    assert [tiers[c] for c in t2_chain] == [
        ("T4", "T4.transitive_merge_contradiction")
    ] * 2


def test_group_with_disjoint_ends_is_withheld(tmp_path: Path) -> None:
    corpus = Corpus()
    chain = _drift_chain(corpus)
    links = [corpus.pair(left, right) for left, right in pairwise(chain)]

    tiers = _tiers(_run(corpus, tmp_path))

    assert [tiers[c] for c in links] == [
        ("T4", "T4.transitive_merge_contradiction")
    ] * 10


def test_distinct_card_inside_a_merge_group_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    corpus = Corpus()
    chain = _drift_chain(corpus)
    for left, right in pairwise(chain):
        corpus.pair(left, right)
    corpus.pair(chain[0], chain[-1])
    monkeypatch.setattr(identity_proposals, "_group_conflict", lambda *_: None)

    with pytest.raises(RuntimeError, match="distinct proposal"):
        _run(corpus, tmp_path)


def test_title_reused_by_another_team_blocks_title_merges(tmp_path: Path) -> None:
    corpus = Corpus()
    title = TITLE + " reused"
    reused = corpus.pair(corpus.work(title, 2020), corpus.work(title, 2020))
    corpus.pair(
        corpus.work(title, 2011, ("Grace Hopper", "Alan Turing")),
        corpus.work(TITLE + " elsewhere", 2011, ("Grace Hopper", "Alan Turing")),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[reused] == ("T4", "T4.ambiguous_title")


def test_biorxiv_prefix_depends_on_the_suffix(tmp_path: Path) -> None:
    corpus = Corpus()
    journals = corpus.pair(
        corpus.work(TITLE, 2020, identifiers=("doi:10.1101/gr.1",)),
        corpus.work(TITLE, 2020, identifiers=("doi:10.1101/gr.2",)),
    )
    preprints = corpus.pair(
        corpus.work(
            TITLE + " A",
            2020,
            identifiers=("doi:10.1101/2020.01.01.1",),
            type_="preprint",
        ),
        corpus.work(
            TITLE + " A",
            2020,
            identifiers=("doi:10.1101/2020.02.02.2",),
            type_="preprint",
        ),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[journals] == ("T4", "T4.contradicting_identifiers")
    assert tiers[preprints] == ("T2", "T2.version")


def test_generic_title_pattern_blocks_title_merges(tmp_path: Path) -> None:
    corpus = Corpus()
    letter = corpus.pair(
        corpus.work("Letter to the editor", 2020),
        corpus.work("Letter to the editor", 2020),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[letter] == ("T4", "T4.ambiguous_title")


def test_identifier_rules_check_abstracts(tmp_path: Path) -> None:
    corpus = Corpus()
    divergent = corpus.pair(
        corpus.work(
            TITLE,
            2020,
            identifiers=("doi:10.1000/a", "openalex:W1"),
            abstract=ABSTRACT,
        ),
        corpus.work(
            TITLE,
            2020,
            identifiers=("doi:10.1000/a", "openalex:W2"),
            abstract=OTHER_ABSTRACT,
        ),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[divergent] == ("T4", "T4.identifier_link_mismatch")


def test_titles_must_match_in_their_original_script(tmp_path: Path) -> None:
    corpus = Corpus()
    ascii_part = "Social dynamics simulation report series volume twelve "
    lossy = corpus.pair(
        corpus.work(ascii_part + "電話帳", 2026),
        corpus.work(ascii_part + "店舗", 2026),
    )

    tiers = _tiers(_run(corpus, tmp_path))

    assert tiers[lossy] == ("T4", "T4.ambiguous_title")


def test_scope_projects_the_full_run_onto_cards_touching_it(tmp_path: Path) -> None:
    corpus = Corpus()
    left = corpus.work(TITLE, 2020, identifiers=("doi:10.1000/a", "openalex:W1"))
    right = corpus.work(TITLE, 2020, identifiers=("doi:10.1000/a", "openalex:W2"))
    focused = corpus.pair(left, right)
    third = corpus.work(TITLE, 2020, identifiers=("openalex:W2",))
    neighbour = corpus.pair(right, third)
    outside = corpus.pair(
        corpus.work(TITLE + " A", 2020), corpus.work(TITLE + " A", 2020)
    )
    inputs = corpus.save(tmp_path / "inputs")
    observation = next(
        r["record_id"] for r in corpus.records if r["identifiers"] == ["openalex:W2"]
    )
    raw = _canonical({"focus": [left, observation], "other": [right]})
    scope_path = tmp_path / "scope.json"
    scope_path.write_bytes(raw)

    full = generate(inputs, seed=5)
    scoped = generate(
        inputs, seed=5, scope=ScopeFile(scope_path, _sha(raw), key="focus")
    )

    full_cards = {card.work_ids: card for card in full.cards}
    assert {c for card in scoped.cards for c in card.candidate_ids} == {
        focused,
        neighbour,
    }
    for card in scoped.cards:
        assert (card.tier, card.rule) == (
            full_cards[card.work_ids].tier,
            full_cards[card.work_ids].rule,
        )
    listed = {c["candidate_id"] for unit in scoped.choices.values() for c in unit}
    assert outside not in listed
    assert scoped.manifest_fields["scope"]["key"] == "focus"
    assert scoped.manifest_fields["scope"]["sha256"] == _sha(raw)
    assert scoped.manifest_fields["scope"]["matched_proposed_works"] == 2
    assert scoped.manifest_fields["counts"]["cards"] == 2
    assert full.manifest_fields["scope"] is None
    (choice,) = scoped.identifier_choices["T1"]
    assert choice["conflict"]["conflicting_identifier_kinds"] == ["openalex"]
    with pytest.raises(ValueError, match="scope"):
        generate(inputs, seed=5, scope=ScopeFile(scope_path, _sha(raw), key="other2"))
    unknown = _canonical(["work.v2.unknown"])
    scope_path.with_name("bad.json").write_bytes(unknown)
    with pytest.raises(ValueError, match="scope"):
        generate(
            inputs,
            seed=5,
            scope=ScopeFile(scope_path.with_name("bad.json"), _sha(unknown)),
        )


def test_doi_less_repository_copies_are_preprint_like(tmp_path: Path) -> None:
    corpus = Corpus()
    copies = {
        "hal": ("HAL (Le Centre pour la Communication Scientifique Directe)", None),
        "suffix": ("Cardinal Scholar (Ball State University)", None),
        "network": (
            "LA Referencia (Red Federada de Repositorios Institucionales)",
            None,
        ),
        "host": (None, "https://ora.ox.ac.uk/objects/uuid:1"),
    }
    controls = {
        "index": ("DOAJ (DOAJ: Directory of Open Access Journals)", None),
        "journal": ("Archives of Sexual Behavior", None),
        "platform": ("DergiPark (Istanbul University)", None),
    }
    cards = {}
    for index, (name, (venue, landing)) in enumerate({**copies, **controls}.items()):
        title = f"{TITLE} {name}"
        cards[name] = corpus.pair(
            corpus.work(title, 2020, venue=venue, landing=landing),
            corpus.work(title, 2020, identifiers=(f"doi:10.1103/pre.{index}",)),
        )
    cards["dblp"] = corpus.pair(
        corpus.work(
            TITLE + " dblp",
            2020,
            identifiers=("dblp:journals/pre/X20",),
            type_="other",
            source="dblp",
        ),
        corpus.work(
            TITLE + " dblp",
            2020,
            identifiers=("doi:10.1103/pre.99", "dblp:journals/pre/X20"),
        ),
    )

    hal = "HAL (Le Centre pour la Communication Scientifique Directe)"
    cards["other_server"] = corpus.pair(
        corpus.work(
            TITLE + " deposit",
            2020,
            identifiers=("arxiv:2001.00077",),
            type_="preprint",
            source="arxiv",
        ),
        corpus.work(TITLE + " deposit", 2020, venue=hal),
    )
    cards["two_repositories"] = corpus.pair(
        corpus.work(TITLE + " twice", 2020, venue=hal),
        corpus.work(
            TITLE + " twice", 2020, venue="Cardinal Scholar (Ball State University)"
        ),
    )

    proposals = _run(corpus, tmp_path)
    by_candidate = {c: card for card in proposals.cards for c in card.candidate_ids}

    for name in (*copies, "other_server", "two_repositories"):
        card = by_candidate[cards[name]]
        assert (card.tier, card.notes) == ("T2", ("repository_copy",)), name
    for name in (*controls, "dblp"):
        assert by_candidate[cards[name]].tier == "T1", name


def test_t1_group_never_joins_two_repository_copies(tmp_path: Path) -> None:
    corpus = Corpus()
    title = TITLE + " deposits"
    hal = "HAL (Le Centre pour la Communication Scientifique Directe)"
    first = corpus.work(title, 2020, identifiers=("openalex:W41",), venue=hal)
    middle = corpus.work(
        title, 2020, identifiers=("openalex:W41", "openalex:W42"), venue=hal
    )
    second = corpus.work(
        title,
        2020,
        identifiers=("openalex:W42",),
        venue="Cardinal Scholar (Ball State University)",
    )
    links = [corpus.pair(first, middle), corpus.pair(middle, second)]

    by_candidate = {
        c: card for card in _run(corpus, tmp_path).cards for c in card.candidate_ids
    }

    for link in links:
        assert by_candidate[link].tier == "T2"
        assert "mixed_manifestation_group" in by_candidate[link].notes
