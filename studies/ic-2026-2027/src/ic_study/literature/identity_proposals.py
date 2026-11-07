"""Generate deterministic corpus-identity proposals for Research Owner review.

The generator reads the acquisition observations, the policy-2 deduplication
result (schema 3) and its identity queue, verifies each input's SHA-256 before
parsing, and assigns every work-pair card to one proposal tier. Its outputs are
proposals only: they contain no Owner decision, never touch the input evidence,
and are written once into a new private directory.

Choice lists use the shape of the C3 ``DedupeChoice`` (``candidate_id`` and
``disposition``) at observation-pair granularity, sorted and unique. Identifier
choices use the C3 ``IdentifierChoice`` shape for final merged groups. Every
rule is conjunctive; ``RULES`` states each one precisely and is copied into
the manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import re
import string
import subprocess
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any

Json = dict[str, Any]

FORMAT = "corpus-identity-resolution-proposals-1"
GENERATOR_VERSION = "3.2.0"

IDENTIFIER_AUTHOR_JACCARD = 0.8
VERSION_AUTHOR_JACCARD = 0.8
IDENTIFIER_YEAR_GAP = 1
VERSION_YEAR_GAP = 2
ABSTRACT_THRESHOLD = 0.3
ABSTRACT_SUPPORT = 0.5
MIN_ABSTRACT_TOKENS = 20
AUDIT_MAX_ERROR_RATE = 0.02
AUDIT_CONFIDENCE = 0.95

ARXIV_DOI_PREFIX = "doi:10.48550/arxiv."
REPOSITORY_DOI_PREFIXES = {
    "10.2139": "SSRN",
    "10.5281": "Zenodo",
    "10.6084": "figshare",
    "10.17605": "OSF",
    "10.17613": "Knowledge Commons",
    "10.20944": "Preprints.org",
    "10.21203": "Research Square",
    "10.22541": "Authorea",
    "10.31124": "Advance",
    "10.31219": "OSF Preprints",
    "10.31222": "MetaArXiv",
    "10.31234": "PsyArXiv",
    "10.31235": "SocArXiv",
    "10.32388": "Qeios",
    "10.32942": "EcoEvoRxiv",
    "10.33774": "APSA Preprints",
    "10.35542": "EdArXiv",
    "10.36227": "TechRxiv",
}
DATED_REPOSITORY_DOI_PREFIXES = {"10.1101": "bioRxiv/medRxiv (numeric suffix only)"}

PREPRINT_TYPES = frozenset({"preprint", "posted_content"})
CONFERENCE_TYPES = frozenset({"conference_paper", "proceedings_article"})
JOURNAL_TYPES = frozenset({"article", "journal_article"})
NAME_NOISE = frozenset(
    {"jr", "sr", "ii", "iii", "iv", "prof", "dr", "mr", "mrs", "ms", "phd", "dba"}
)
IDENTIFIER_CONTRADICTIONS = frozenset(
    {"distinct_registered_dois", "distinct_arxiv_ids", "distinct_dblp_publications"}
)

GENERIC_TITLE = re.compile(
    r"(?:abstracts?|acknowledg(?:e)?ments?|announcements?|back matter|"
    r"book reviews?|books received|call for papers|comments?|commentary|"
    r"conclusions?|contents|correction|corrigendum|discussion|editorial|"
    r"editorial board|editor s note|errat(?:a|um)|foreword|front matter|"
    r"guest editorial|in memoriam|index|introduction|letters?|"
    r"letter to the editor|new books|news|notes?|obituary|overview|preface|"
    r"reply|retraction(?: notice)?|reviewers|summary|table of contents|"
    r"untitled|withdrawn)(?: [0-9]+)?"
)

RULES: dict[str, str] = {
    "T1.shared_identifier": (
        "Merge. The two proposed works share at least one typed identifier "
        "(DOI, arXiv, DBLP key or OpenAlex ID normalized as in deduplication "
        "policy 2) AND share a title under both the ASCII and the "
        "script-preserving normalization AND both list authors whose surname "
        "sets have Jaccard >= 0.8 AND their publication years differ by at "
        "most 1 AND a linking identifier is carried on both sides by "
        "observations of the same manifestation class AND no DOI divergence "
        "AND no contradiction AND the best abstract Jaccard is "
        "unavailable or >= 0.3."
    ),
    "T1.arxiv_link": (
        "Merge. As T1.shared_identifier, except that the identifier evidence is "
        "an arXiv ID (version removed) of one work equal to the arXiv ID "
        "encoded by the other work's arXiv ID, 10.48550/arXiv DOI or DBLP CoRR "
        "key journals/corr/abs-YYMM-NNNNN."
    ),
    "T1.title_year_authors": (
        "Merge. An unambiguous title (not generic, reused or script-lossy) is "
        "shared AND publication years are equal AND the non-empty author "
        "surname sets are identical AND, if that set is a single surname, the "
        "best abstract Jaccard is >= 0.5 AND both works have the same "
        "manifestation class, other than repository copy, AND no DOI "
        "divergence AND no contradiction AND the best abstract Jaccard is "
        "unavailable or >= 0.3."
    ),
    "T2.version": (
        "Merge only under an Owner version policy. Not T1 AND an unambiguous "
        "title (not generic, reused or script-lossy) is shared AND publication "
        "years differ by at most 2 AND author surname sets have Jaccard >= 0.8 "
        "AND, unless an identifier links the works, they do not rest on a "
        "single shared surname without abstract Jaccard >= 0.5 AND no "
        "contradiction AND the best abstract Jaccard is unavailable or "
        ">= 0.3. Notes state why T1 did not apply: repository_copy, "
        "preprint_vs_published, year_gap, doi_divergence, author_list_variant. "
        "A T1 card also moves here (note mixed_manifestation_group) when its "
        "T1 merge group, closed transitively, would join two works with a DOI "
        "divergence, different manifestation classes or two repository copies "
        "not linked by a same-class identifier, or publication years 2 apart."
    ),
    "T3.disjoint_authors": (
        "Distinct. No shared or linked identifier AND both works list authors "
        "AND their name tokens of at least two letters are disjoint AND no "
        "surname of at least three letters occurs inside the other side's "
        "concatenated names AND the best abstract Jaccard is unavailable or "
        "< 0.3."
    ),
    "T3.generic_title_without_match": (
        "Distinct. No shared or linked identifier AND the matched title is "
        "generic or reused AND at least one work lists no author AND the best "
        "abstract Jaccard is unavailable or < 0.3 AND at least one "
        "distinguishing fact holds: a publication-year gap above 2, a "
        "contradiction, a DOI divergence or best abstract Jaccard "
        "< 0.3."
    ),
    "T4.contradicting_identifiers": (
        "Judgment. Distinct registered DOIs, distinct arXiv IDs or distinct "
        "DBLP publication keys on the two sides (evaluated first)."
    ),
    "T4.conference_vs_journal": (
        "Judgment. One side is conference-only and the other journal-only."
    ),
    "T4.identifier_link_mismatch": (
        "Judgment. A shared or linked identifier whose title, author, year, "
        "manifestation-class or abstract conditions fail."
    ),
    "T4.ambiguous_title": (
        "Judgment. The matched title is generic, reused or script-lossy and no "
        "merge or distinct rule applies."
    ),
    "T4.year_gap": "Judgment. Publication years unknown or more than 2 apart.",
    "T4.abstract_divergence": (
        "Judgment. Other evidence agrees but the best abstract Jaccard is < 0.3."
    ),
    "T4.single_author_title_match": (
        "Judgment. A title-only merge whose only author evidence is one shared "
        "surname and whose abstracts are not compared or have Jaccard < 0.5."
    ),
    "T4.partial_author_evidence": (
        "Judgment. Authors missing on a side or overlapping with surname "
        "Jaccard < 0.8 without being disjoint."
    ),
    "T4.transitive_merge_contradiction": (
        "Judgment. The card was a T1 merge (or a T2 merge in the T1+T2 scope) "
        "whose transitively closed merge group contains two works with a "
        "contradiction or strictly disjoint authors, or spans more than 2 "
        "publication years. Every such card of that group is withheld."
    ),
}

DEFINITIONS: dict[str, str] = {
    "normalized_title": (
        "NFKD casefold without combining marks; ASCII [a-z0-9]+ tokens joined "
        "by one space (deduplication policy 2), after replacing a literal "
        "backslash-n followed by whitespace with a space."
    ),
    "generic_title": (
        "A matched script title matching generic_title_pattern or with at most "
        "three tokens."
    ),
    "script_title": (
        "NFKD casefold without combining marks; Unicode \\w+ tokens joined by "
        "one space. Titles are matched, and judged generic or reused, on this "
        "key. A card is script-lossy when the ASCII titles of deduplication "
        "policy 2 match but these keys share nothing, e.g. titles differing "
        "only in CJK text."
    ),
    "reused_title": (
        "A script title carried by two proposed works anywhere in the "
        "corpus whose authors are strictly disjoint (T3.disjoint_authors test)."
    ),
    "author_surname": (
        "Last ASCII-folded letter token of each person in an author string "
        "(person_names): ';', 'and' and '&' separate people; three or more "
        "comma segments of two or more tokens are a list, otherwise the first "
        "comma segment is the family name; LaTeX accents and HTML entities are "
        "resolved; parenthetical remarks are removed; entries starting with a "
        "comma are affiliations; segments "
        "with URLs, e-mail, affiliation words, two or more "
        "digits or academic degrees are dropped; l-stroke, o-slash, d-stroke, "
        "eth, h-stroke, dotless i, thorn, ae and oe are transliterated; "
        "suffixes and honorifics are ignored. Sets are unions over the work's "
        "observations."
    ),
    "manifestation_class": (
        "An observation is a preprint when its type is preprint or "
        "posted_content, its source is arXiv, it is a DBLP observation whose "
        "DBLP keys are all CoRR keys, or it has no DBLP key and all of its DOIs "
        "are 10.48550 or repository DOIs. It is a repository copy when it is an "
        "OpenAlex observation without DOI or DBLP key "
        "whose venue is not an index or hosting platform (DOAJ, PubMed, "
        "Dialnet, Neliti, DergiPark, Project Muse, OAPEN, CyberLeninka) and "
        "either names a repository service (repository, ePrints, HAL, "
        "DSpace, Digital Commons, RePEc, LA Referencia, CONICET and the other "
        "terms of repository_venue_pattern), ends with an institutional "
        "parenthetical such as '(University of X)', or whose landing page is "
        "on a repository host (repository_host_pattern). Otherwise it is "
        "published. A work is published if any observation is, else a "
        "repository copy if any observation is, else a preprint. Title rules "
        "treat any class difference, and any repository copy, as a version "
        "question for T2; identifier rules compare the classes of the "
        "observations carrying the linking identifier (typed identifier or "
        "arXiv ID)."
    ),
    "registered_doi": (
        "A DOI outside 10.48550 and outside repository_doi_prefixes (10.1101 "
        "counts as repository only with a numeric suffix)."
    ),
    "doi_divergence": (
        "Both works carry copy identifiers and share none. Copy identifiers are "
        "DOIs other than 10.48550 plus arXiv IDs (from arXiv IDs, 10.48550 "
        "DOIs or DBLP CoRR keys), so an arXiv DOI and the same arXiv ID match. "
        "Between two registered DOIs this is also a contradiction."
    ),
    "contradiction": (
        "distinct_registered_dois, distinct_arxiv_ids, "
        "distinct_dblp_publications (both sides non-empty and disjoint), or "
        "conference_vs_journal (conference_paper/proceedings_article or DBLP "
        "conf/ key only on one side; article/journal_article or DBLP journals/ "
        "non-CoRR key only on the other)."
    ),
    "abstract_jaccard": (
        "Best Jaccard over observation pairs of the ASCII [a-z0-9]{3,} token "
        "sets of abstracts with at least 20 distinct tokens, rounded to 6 "
        "decimals."
    ),
    "adoption_units": (
        "T1-identifier (T1.shared_identifier, T1.arxiv_link), T1-title "
        "(T1.title_year_authors), T2 and T3 have separate choice files and "
        "audit samples. Identifier choices and transitive checks are computed "
        "for the scenarios T1-identifier, T1 (both T1 units) and T1+T2."
    ),
    "identifier_choice": (
        "For each final merged group (>= 2 proposed works) whose retained "
        "identifiers are plural for some kind, the C3 IdentifierConflict is "
        "computed exactly. same_work_identifiers is proposed only when the "
        "group holds at most one registered DOI, one arXiv ID and one DBLP "
        "publication key; other plural groups stay pending."
    ),
}

OWNER_POLICY = {
    "T1-identifier": (
        "The v4 protocol keeps title_only_auto_merge=false and "
        "fuzzy_match_requires_adjudication=true; each choice still needs an "
        "explicit Owner decision, informed by this unit's audit sample."
    ),
    "T1-title": (
        "These merges rest on title, year and identical author surnames without "
        "an identifier link, which title_only_auto_merge=false reserves for the "
        "Owner; adopt them only after this unit's own audit sample."
    ),
    "T2": (
        "Decide whether preprint/published versions, publication-year "
        "discrepancies up to 2 years, repository or DOI copies and author-list "
        "variants of one title count as one scholarly work."
    ),
    "T3": (
        "Decide whether rule-based distinct dispositions may be adopted, "
        "informed by the T3 audit sample."
    ),
    "T4": "Every T4 card needs an individual Owner judgment or an explicit defer.",
}

_ASCII_LOWER = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)
_DOI = re.compile(r"10\.[0-9]{4,9}/[^\s\x00-\x1f\x7f]+")
_ARXIV = re.compile(
    r"(?P<base>(?:[0-9]{2}(?:0[1-9]|1[0-2])\.[0-9]{4,5}|"
    r"[a-z][a-z.-]*/[0-9]{2}(?:0[1-9]|1[0-2])[0-9]{3}))(?:v[1-9][0-9]*)?"
)
_DBLP = re.compile(
    r"(?:books|conf|data|journals|master|phd|reference|series|tr|www)/[^\s:?#\\]+"
)
_OPENALEX = re.compile(r"W[1-9][0-9]*")
_CORR_ARXIV = re.compile(r"dblp:journals/corr/abs-([0-9]{4})-([0-9]{4,5})")
_TITLE_WORD = re.compile(r"[a-z0-9]+")
_SCRIPT_WORD = re.compile(r"\w+")
_ABSTRACT_WORD = re.compile(r"[a-z0-9]{3,}")
_NAME_WORD = re.compile(r"[a-z]+")
_ESCAPED_NEWLINE = re.compile(r"\\n(?=\s|$)")
_LATEX_ACCENT = re.compile(r"""\\[`'^"~=.]\s*\{?\s*([A-Za-z])\s*\}?""")
_HTML_ENTITY = re.compile(r"&#?[a-z0-9]+;", re.IGNORECASE)
_PARENTHETICAL = re.compile(r"\([^()]*\)")
_AND = re.compile(r"\s+(?:and|&)\s+", re.IGNORECASE)
_AFFILIATION = re.compile(
    r"https?:|www\.|\S@\S|\b(?:universit\w*|universidad\w*|dep(?:t|artment)\w*|"
    r"institut\w*|school|college|laborator\w*|faculty|centre|center|academy|"
    r"hospital|journal|inc|ltd|gmbh|corporation)\b",
    re.IGNORECASE,
)
_ADDRESS = re.compile(r"[0-9]{2,}")
_DEGREE = re.compile(r"(?:ph\.?\s?d\.?|dba|m\.?d\.?|m\.?sc\.?|jr\.?|sr\.?)", re.I)
_REPOSITORY_VENUE = re.compile(
    r"\b(?:repositor\w*|reposit[oó]rio\w*|e-?prints?|hal|lirias|escholarship|"
    r"digital library|digital commons|dspace\S*|scholarworks|scholarly ?commons|"
    r"scholar commons|research online|research portal|research information|"
    r"research archive|archive ouverte|document server|conicet|la referencia|"
    r"repec|econstor|centaur|explore bristol research|open access at|philpapers)\b",
    re.IGNORECASE,
)
_INSTITUTION_SUFFIX = re.compile(
    r"\([^()]*\b(?:universit\w*|college|institut\w*|school|academy|library|"
    r"foundation|laborator\w*|organi[sz]ation for)\b[^()]*\)\s*$",
    re.IGNORECASE,
)
_INDEX_OR_PLATFORM = re.compile(
    r"\b(?:doaj|pubmed|dialnet|neliti|dergipark|project muse|oapen|cyberleninka)\b",
    re.IGNORECASE,
)
_REPOSITORY_HOST = re.compile(
    r"(?:[^.]+\.)*(?:hal\.science|hal\.[a-z-]+\.fr|eprints\.[a-z0-9.-]+|"
    r"[a-z0-9.-]*repositor[a-z0-9.-]*|digitalcommons\.[a-z0-9.-]+|"
    r"scholarworks\.[a-z0-9.-]+|pure\.[a-z0-9.-]+|researchportal\.[a-z0-9.-]+|"
    r"research-information\.[a-z0-9.-]+|discovery\.ucl\.ac\.uk|ora\.ox\.ac\.uk|"
    r"ro\.uow\.edu\.au|arro\.anglia\.ac\.uk|archive-ouverte\.[a-z0-9.-]+|"
    r"hdl\.handle\.net|econstor\.eu|ideas\.repec\.org|econpapers\.repec\.org|"
    r"philarchive\.org)",
    re.IGNORECASE,
)
_UNDECOMPOSED_LETTERS = str.maketrans(
    {
        "\u0142": "l",
        "\u00f8": "o",
        "\u0111": "d",
        "\u00f0": "d",
        "\u0127": "h",
        "\u0131": "i",
        "\u00fe": "th",
        "\u00e6": "ae",
        "\u0153": "oe",
    }
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def typed_identifier(identifier: str) -> str | None:
    """Normalize one identifier exactly like deduplication policy 2."""
    kind, separator, value = identifier.partition(":")
    if not separator:
        return None
    if kind == "doi" and _DOI.fullmatch(value):
        return "doi:" + value.translate(_ASCII_LOWER)
    if kind == "arxiv" and (match := _ARXIV.fullmatch(value)):
        return "arxiv:" + match.group("base")
    if (
        kind == "dblp"
        and _DBLP.fullmatch(value)
        and all(part not in {"", ".", ".."} for part in value.split("/"))
    ):
        return identifier
    if kind == "openalex" and _OPENALEX.fullmatch(value):
        return identifier
    return None


def typed_work_id(record_ids: Sequence[str]) -> str:
    """Membership hash used by C3 for a final group."""
    return "work.v2." + _sha256(_canonical(sorted(record_ids)))[:24]


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(c for c in normalized if not unicodedata.combining(c))


def title_key(value: str) -> str:
    return " ".join(_TITLE_WORD.findall(_fold(_ESCAPED_NEWLINE.sub(" ", value))))


def _script_key(value: str) -> str:
    return " ".join(_SCRIPT_WORD.findall(_fold(_ESCAPED_NEWLINE.sub(" ", value))))


def _name_tokens(text: str) -> list[str]:
    folded = _fold(text).translate(_UNDECOMPOSED_LETTERS)
    return [part for part in _NAME_WORD.findall(folded) if part not in NAME_NOISE]


def person_names(raw: str) -> list[list[str]]:
    """Name tokens, in given-family order, of every person in one author string.

    Handles "Family, Given[, Initial]", ";"/"and"/"&"-separated and
    comma-joined lists (three or more multi-token segments), LaTeX accents,
    HTML entities and parenthetical remarks, and drops entries that start with
    a comma (affiliations)
    and affiliation, address, identifier and degree segments.
    """
    text = _LATEX_ACCENT.sub(r"\1", raw).replace("{", "").replace("}", "")
    text = _PARENTHETICAL.sub(" ", _HTML_ENTITY.sub(" ", text))
    names: list[list[str]] = []
    for chunk in text.split(";"):
        if "," not in chunk and _AFFILIATION.search(chunk):
            continue
        for part in _AND.split(chunk):
            if not part.split(",")[0].strip():
                continue
            segments = [
                segment.strip()
                for segment in part.split(",")
                if segment.strip()
                and not _AFFILIATION.search(segment)
                and not _ADDRESS.search(segment)
                and not _DEGREE.fullmatch(segment.strip())
            ]
            tokens = [_name_tokens(segment) for segment in segments]
            if len(segments) >= 3 and all(len(t) >= 2 for t in tokens):
                names.extend(tokens)
            elif len(segments) >= 2:
                names.append(_name_tokens(" ".join([*segments[1:], segments[0]])))
            elif segments:
                names.append(tokens[0])
    return [name for name in names if name]


def _is_generic(key: str) -> bool:
    return bool(GENERIC_TITLE.fullmatch(key)) or len(key.split()) <= 3


def _repository_doi(value: str) -> bool:
    prefix, _, suffix = value.removeprefix("doi:").partition("/")
    if prefix in DATED_REPOSITORY_DOI_PREFIXES:
        return suffix[:1].isdigit()
    return prefix in REPOSITORY_DOI_PREFIXES


def _arxiv_ids(identifiers: Iterable[str]) -> frozenset[str]:
    found = set()
    for value in identifiers:
        if value.startswith("arxiv:"):
            found.add(value.removeprefix("arxiv:"))
        elif value.startswith(ARXIV_DOI_PREFIX):
            if match := _ARXIV.fullmatch(value.removeprefix(ARXIV_DOI_PREFIX)):
                found.add(match.group("base"))
        elif match := _CORR_ARXIV.fullmatch(value):
            found.add(f"{match.group(1)}.{match.group(2)}")
    return frozenset(found)


def _host(url: str | None) -> str:
    match = re.match(r"https?://([^/:?#]+)", url or "")
    return match.group(1).lower() if match else ""


def _repository_copy(record: Json, identifiers: Sequence[str]) -> bool:
    """A DOI-less OpenAlex observation hosted by a repository, not a publisher."""
    if record["source_id"] != "openalex" or any(
        value.startswith(("doi:", "dblp:")) for value in identifiers
    ):
        return False
    venue = record.get("venue") or ""
    if _INDEX_OR_PLATFORM.search(venue):
        return False
    return bool(
        _REPOSITORY_VENUE.search(venue)
        or _INSTITUTION_SUFFIX.search(venue)
        or _REPOSITORY_HOST.fullmatch(_host(record.get("landing_page_url")))
    )


def _manifestation(record: Json, identifiers: Iterable[str]) -> str:
    """Class of one observation: "preprint", "repository" or "published"."""
    if record["publication_type"] in PREPRINT_TYPES or record["source_id"] == "arxiv":
        return "preprint"
    values = tuple(identifiers)
    if _repository_copy(record, values):
        return "repository"
    keys = [value for value in values if value.startswith("dblp:")]
    if keys:
        corr = record["source_id"] == "dblp" and all(
            key.startswith("dblp:journals/corr/") for key in keys
        )
        return "preprint" if corr else "published"
    dois = [value for value in values if value.startswith("doi:")]
    if dois and all(
        doi.startswith("doi:10.48550/") or _repository_doi(doi) for doi in dois
    ):
        return "preprint"
    return "published"


@dataclass(frozen=True)
class _Work:
    work_id: str
    title: str | None
    year: int | None
    types: tuple[str, ...]
    record_ids: tuple[str, ...]
    identifiers: tuple[str, ...]
    title_keys: frozenset[str]
    script_title_keys: frozenset[str]
    surnames: frozenset[str]
    name_tokens: frozenset[str]
    compact_names: tuple[str, ...]
    abstracts: frozenset[frozenset[str]]
    arxiv: frozenset[str]
    registered_dois: frozenset[str]
    copy_identifiers: frozenset[str]
    dblp_publications: frozenset[str]
    manifestation: str
    link_classes: frozenset[tuple[str, str]]
    conference: bool
    journal: bool
    source_artifacts: frozenset[str]


def _profile(
    work: Json, records: Mapping[str, Json], *, resolved_title: str | None = None
) -> _Work:
    members = [records[record_id] for record_id in work["manifestation_record_ids"]]
    typed_by_record = [
        {t for value in member["identifiers"] if (t := typed_identifier(value))}
        for member in members
    ]
    identifiers = tuple(sorted(set().union(*typed_by_record)))
    if list(identifiers) != sorted(work["identifiers"]):
        raise ValueError(
            f"{work['work_id']} identifiers differ from typed observation identifiers"
        )
    surnames: set[str] = set()
    tokens: set[str] = set()
    compact: set[str] = set()
    abstracts: set[frozenset[str]] = set()
    for member in members:
        for name in member["authors"] or ():
            for parts in person_names(name):
                surnames.add(parts[-1])
                tokens.update(p for p in parts if len(p) >= 2)
                compact.add("".join(parts))
        words = frozenset(_ABSTRACT_WORD.findall(_fold(member["abstract"] or "")))
        if len(words) >= MIN_ABSTRACT_TOKENS:
            abstracts.add(words)
    dois = {value for value in identifiers if value.startswith("doi:")}
    dblp = {value for value in identifiers if value.startswith("dblp:")}
    types = {member["publication_type"] for member in members}
    publications = {v for v in dblp if not v.startswith("dblp:journals/corr/")}
    classes = [
        _manifestation(member, typed)
        for member, typed in zip(members, typed_by_record, strict=True)
    ]
    links = {
        (key, kind)
        for typed, kind in zip(typed_by_record, classes, strict=True)
        for key in (*typed, *(f"arxiv-id:{x}" for x in _arxiv_ids(typed)))
    }
    return _Work(
        work_id=work["work_id"],
        title=work["canonical_title"],
        year=work["publication_year"],
        types=tuple(sorted(types)),
        record_ids=tuple(sorted(work["manifestation_record_ids"])),
        identifiers=identifiers,
        title_keys=frozenset(
            key
            for title in (*[m["title"] for m in members], resolved_title)
            if title and (key := title_key(title))
        ),
        script_title_keys=frozenset(
            key
            for title in (*[m["title"] for m in members], resolved_title)
            if title and (key := _script_key(title))
        ),
        surnames=frozenset(surnames),
        name_tokens=frozenset(tokens),
        compact_names=tuple(sorted(compact)),
        abstracts=frozenset(abstracts),
        arxiv=_arxiv_ids(identifiers),
        registered_dois=frozenset(
            d
            for d in dois
            if not d.startswith("doi:10.48550/") and not _repository_doi(d)
        ),
        copy_identifiers=frozenset(
            {d for d in dois if not d.startswith("doi:10.48550/")}
            | {f"arxiv:{x}" for x in _arxiv_ids(identifiers)}
        ),
        dblp_publications=frozenset(publications),
        manifestation=next(
            kind for kind in ("published", "repository", "preprint") if kind in classes
        ),
        link_classes=frozenset(links),
        conference=bool(types & CONFERENCE_TYPES)
        or any(v.startswith("dblp:conf/") for v in publications),
        journal=bool(types & JOURNAL_TYPES)
        or any(v.startswith("dblp:journals/") for v in publications),
        source_artifacts=frozenset(m["raw_artifact_sha256"] for m in members),
    )


def _authors_disjoint(left: _Work, right: _Work) -> bool:
    if not left.name_tokens or not right.name_tokens:
        return False
    if left.name_tokens & right.name_tokens:
        return False
    for first, second in ((left, right), (right, left)):
        for surname in first.surnames:
            if len(surname) >= 3 and any(
                surname in name for name in second.compact_names
            ):
                return False
    return True


def _contradictions(left: _Work, right: _Work) -> tuple[str, ...]:
    found = []
    for name, a, b in (
        ("distinct_registered_dois", left.registered_dois, right.registered_dois),
        ("distinct_arxiv_ids", left.arxiv, right.arxiv),
        (
            "distinct_dblp_publications",
            left.dblp_publications,
            right.dblp_publications,
        ),
    ):
        if a and b and not a & b:
            found.append(name)
    if (
        left.conference and not left.journal and right.journal and not right.conference
    ) or (
        right.conference and not right.journal and left.journal and not left.conference
    ):
        found.append("conference_vs_journal")
    return tuple(found)


def _doi_divergence(left: _Work, right: _Work) -> bool:
    return bool(
        left.copy_identifiers
        and right.copy_identifiers
        and not left.copy_identifiers & right.copy_identifiers
    )


def _mixed_manifestation(left: _Work, right: _Work) -> bool:
    different = (
        left.manifestation != right.manifestation or left.manifestation == "repository"
    )
    return different and not left.link_classes & right.link_classes


def _abstract_similarity(left: _Work, right: _Work) -> float | None:
    best: float | None = None
    for first in left.abstracts:
        for second in right.abstracts:
            value = len(first & second) / len(first | second)
            best = value if best is None else max(best, value)
    return None if best is None else round(best, 6)


@dataclass(frozen=True)
class Evidence:
    shared_identifiers: tuple[str, ...]
    linked_arxiv_ids: tuple[str, ...]
    matched_titles: tuple[str, ...]
    generic_title: bool
    reused_title: bool
    script_title_mismatch: bool
    year_gap: int | None
    surname_jaccard: float | None
    authors_disjoint: bool
    authors_missing: bool
    abstract_similarity: float | None
    contradictions: tuple[str, ...]
    doi_divergence: bool
    manifestations: tuple[str, str]
    linked_same_class: bool
    single_author: bool

    @property
    def linked(self) -> bool:
        return bool(self.shared_identifiers or self.linked_arxiv_ids)

    @property
    def ambiguous_title(self) -> bool:
        return self.generic_title or self.reused_title or self.script_title_mismatch


@dataclass(frozen=True)
class Card:
    work_ids: tuple[str, str]
    component_id: str
    candidate_ids: tuple[str, ...]
    tier: str
    rule: str
    notes: tuple[str, ...]
    evidence: Evidence

    def as_json(self) -> Json:
        return {
            "work_ids": list(self.work_ids),
            "component_id": self.component_id,
            "candidate_ids": list(self.candidate_ids),
            "tier": self.tier,
            "rule": self.rule,
            "notes": list(self.notes),
            "evidence": asdict(self.evidence),
        }


def _evidence(left: _Work, right: _Work, reused: set[str]) -> Evidence:
    titles = tuple(sorted(left.script_title_keys & right.script_title_keys))
    generic = any(_is_generic(key) for key in titles)
    jaccard = (
        round(
            len(left.surnames & right.surnames) / len(left.surnames | right.surnames), 6
        )
        if left.surnames and right.surnames
        else None
    )
    return Evidence(
        shared_identifiers=tuple(
            sorted(set(left.identifiers) & set(right.identifiers))
        ),
        linked_arxiv_ids=tuple(sorted(left.arxiv & right.arxiv)),
        matched_titles=titles,
        generic_title=generic,
        reused_title=any(key in reused for key in titles),
        script_title_mismatch=bool(left.title_keys & right.title_keys) and not titles,
        year_gap=abs(left.year - right.year)
        if left.year is not None and right.year is not None
        else None,
        surname_jaccard=jaccard,
        authors_disjoint=_authors_disjoint(left, right),
        authors_missing=not left.name_tokens or not right.name_tokens,
        abstract_similarity=_abstract_similarity(left, right),
        contradictions=_contradictions(left, right),
        doi_divergence=_doi_divergence(left, right),
        manifestations=(left.manifestation, right.manifestation),
        linked_same_class=bool(left.link_classes & right.link_classes),
        single_author=len(left.surnames | right.surnames) == 1,
    )


def _classify(e: Evidence) -> tuple[str, str, tuple[str, ...]]:
    compatible_abstract = (
        e.abstract_similarity is None or e.abstract_similarity >= ABSTRACT_THRESHOLD
    )
    divergent_abstract = not compatible_abstract
    repository = "repository" in e.manifestations
    mismatch = e.manifestations[0] != e.manifestations[1]
    same_manifestation = not mismatch and not repository and not e.doi_divergence
    author_evidence = (
        e.linked
        or not e.single_author
        or (
            e.abstract_similarity is not None
            and e.abstract_similarity >= ABSTRACT_SUPPORT
        )
    )
    jaccard = e.surname_jaccard
    gap = e.year_gap
    if (
        e.linked
        and e.matched_titles
        and jaccard is not None
        and jaccard >= IDENTIFIER_AUTHOR_JACCARD
        and gap is not None
        and gap <= IDENTIFIER_YEAR_GAP
        and e.linked_same_class
        and not e.doi_divergence
        and not e.contradictions
        and compatible_abstract
    ):
        rule = "T1.shared_identifier" if e.shared_identifiers else "T1.arxiv_link"
        return "T1", rule, ()
    specific = bool(e.matched_titles) and not e.ambiguous_title
    if (
        specific
        and gap == 0
        and jaccard == 1.0
        and author_evidence
        and same_manifestation
        and not e.contradictions
        and compatible_abstract
    ):
        return "T1", "T1.title_year_authors", ()
    if (
        specific
        and gap is not None
        and gap <= VERSION_YEAR_GAP
        and jaccard is not None
        and jaccard >= VERSION_AUTHOR_JACCARD
        and author_evidence
        and not e.contradictions
        and compatible_abstract
    ):
        notes = [
            name
            for name, present in (
                ("repository_copy", repository),
                ("preprint_vs_published", mismatch and not repository),
                ("year_gap", bool(gap)),
                ("doi_divergence", e.doi_divergence),
                ("author_list_variant", jaccard < 1.0),
            )
            if present
        ]
        return "T2", "T2.version", tuple(notes)
    if (
        not e.linked
        and e.authors_disjoint
        and (e.abstract_similarity is None or divergent_abstract)
    ):
        return "T3", "T3.disjoint_authors", ()
    distinguishing = (
        (gap is not None and gap > VERSION_YEAR_GAP)
        or bool(e.contradictions)
        or e.doi_divergence
        or divergent_abstract
    )
    if (
        not e.linked
        and e.matched_titles
        and (e.generic_title or e.reused_title)
        and e.authors_missing
        and (e.abstract_similarity is None or divergent_abstract)
        and distinguishing
    ):
        return "T3", "T3.generic_title_without_match", ()
    if set(e.contradictions) & IDENTIFIER_CONTRADICTIONS:
        return "T4", "T4.contradicting_identifiers", ()
    if e.contradictions:
        return "T4", "T4.conference_vs_journal", ()
    if e.linked:
        return "T4", "T4.identifier_link_mismatch", ()
    if e.ambiguous_title or not e.matched_titles:
        return "T4", "T4.ambiguous_title", ()
    if gap is None or gap > VERSION_YEAR_GAP:
        return "T4", "T4.year_gap", ()
    if divergent_abstract:
        return "T4", "T4.abstract_divergence", ()
    if not author_evidence:
        return "T4", "T4.single_author_title_match", ()
    return "T4", "T4.partial_author_evidence", ()


UNITS: dict[str, frozenset[str]] = {
    "T1-identifier": frozenset({"T1.shared_identifier", "T1.arxiv_link"}),
    "T1-title": frozenset({"T1.title_year_authors"}),
    "T2": frozenset({"T2.version"}),
    "T3": frozenset({"T3.disjoint_authors", "T3.generic_title_without_match"}),
}
UNIT_DISPOSITIONS = {
    "T1-identifier": "merge",
    "T1-title": "merge",
    "T2": "merge",
    "T3": "distinct",
}
SCENARIOS: dict[str, tuple[str, ...]] = {
    "T1-identifier": ("T1-identifier",),
    "T1": ("T1-identifier", "T1-title"),
    "T1+T2": ("T1-identifier", "T1-title", "T2"),
}
SCENARIO_FILES = {"T1-identifier": "t1-identifier", "T1": "t1", "T1+T2": "t1-t2"}
DEMOTION_SCOPES: dict[str, tuple[str, ...]] = {"T1": ("T1",), "T1+T2": ("T1", "T2")}


def unit_of(card: Card) -> str | None:
    """Separately adoptable unit of a proposal card; T4 cards have none."""
    return next((unit for unit, rules in UNITS.items() if card.rule in rules), None)


def _in_scenario(card: Card, scenario: str) -> bool:
    return unit_of(card) in SCENARIOS[scenario]


class _UnionFind:
    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, key: str) -> str:
        self._parent.setdefault(key, key)
        root = key
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[key] != root:
            self._parent[key], key = root, self._parent[key]
        return root

    def union(self, left: str, right: str) -> None:
        first, second = sorted((self.find(left), self.find(right)))
        if first != second:
            self._parent[second] = first

    def groups(self) -> tuple[tuple[str, ...], ...]:
        members: dict[str, list[str]] = defaultdict(list)
        for key in list(self._parent):
            members[self.find(key)].append(key)
        return tuple(
            sorted(tuple(sorted(group)) for group in members.values() if len(group) > 1)
        )


def _groups(pairs: Iterable[tuple[str, str]]) -> tuple[tuple[str, ...], ...]:
    sets = _UnionFind()
    for left, right in pairs:
        sets.union(left, right)
    return sets.groups()


def _group_conflict(members: Sequence[_Work], scenario: str) -> str | None:
    """Classify a transitively closed merge group of one scenario.

    "hard" groups join contradicting works and are withheld to T4. In the T1
    scenario, "version" groups only join different manifestations of one work
    (diverging copies, preprint with published, or a two-year spread), which is
    the question T2 asks the Owner.
    """
    years = [member.year for member in members if member.year is not None]
    spread = max(years) - min(years) if years else 0
    pairs = list(combinations(members, 2))
    if spread > VERSION_YEAR_GAP or any(
        _contradictions(left, right) or _authors_disjoint(left, right)
        for left, right in pairs
    ):
        return "hard"
    if scenario == "T1" and (
        spread > IDENTIFIER_YEAR_GAP
        or any(
            _doi_divergence(left, right) or _mixed_manifestation(left, right)
            for left, right in pairs
        )
    ):
        return "version"
    return None


def _enforce_transitivity(cards: list[Card], works: Mapping[str, _Work]) -> None:
    for scenario, tiers in DEMOTION_SCOPES.items():
        verdict = {
            work: conflict
            for group in _groups(card.work_ids for card in cards if card.tier in tiers)
            if (conflict := _group_conflict([works[w] for w in group], scenario))
            for work in group
        }
        for index, card in enumerate(cards):
            conflict = verdict.get(card.work_ids[0])
            if card.tier != tiers[-1] or conflict is None:
                continue
            if conflict == "hard":
                cards[index] = replace(
                    card,
                    tier="T4",
                    rule="T4.transitive_merge_contradiction",
                    notes=(*card.notes, f"withheld_{card.rule}"),
                )
            else:
                cards[index] = replace(
                    card,
                    tier="T2",
                    rule="T2.version",
                    notes=("mixed_manifestation_group", f"moved_{card.rule}"),
                )


def _demotion_stats(cards: Sequence[Card]) -> Json:
    def withheld(prefix: str) -> int:
        return sum(
            any(note.startswith(f"withheld_{prefix}") for note in card.notes)
            for card in cards
        )

    return {
        "T1": {
            "demoted_cards": withheld("T1."),
            "version_moved_cards": sum(
                "mixed_manifestation_group" in card.notes for card in cards
            ),
        },
        "T1+T2": {"demoted_cards": withheld("T2.")},
    }


def _merge_scenarios(
    cards: list[Card], works: Mapping[str, _Work]
) -> tuple[Json, dict[str, tuple[tuple[str, ...], ...]]]:
    """Close each adoption scenario, annotate joined cards and check invariants."""
    stats: Json = {}
    final: dict[str, tuple[tuple[str, ...], ...]] = {}
    for scenario in SCENARIOS:
        scope = "T1+T2" if scenario == "T1+T2" else "T1"
        final[scenario] = _groups(
            card.work_ids for card in cards if _in_scenario(card, scenario)
        )
        if any(
            _group_conflict([works[w] for w in group], scope)
            for group in final[scenario]
        ):
            raise RuntimeError(f"{scenario} merge groups still contain a contradiction")
        group_of = {w: i for i, group in enumerate(final[scenario]) for w in group}
        joined = 0
        for index, card in enumerate(cards):
            left, right = card.work_ids
            if _in_scenario(card, scenario) or left not in group_of:
                continue
            if group_of[left] != group_of.get(right):
                continue
            if card.tier == "T3":
                raise RuntimeError("a distinct proposal contradicts a transitive merge")
            cards[index] = replace(card, notes=(*card.notes, f"joined_by_{scenario}"))
            joined += 1
        stats[scenario] = {
            "merge_groups": len(final[scenario]),
            "merged_proposed_works": sum(len(group) for group in final[scenario]),
            "proposed_works_after_merges": len(works)
            - sum(len(group) - 1 for group in final[scenario]),
            "joined_pending_cards": joined,
        }
    return stats, final


def _conflicting_kinds(identifiers: Iterable[str]) -> list[str]:
    values: dict[str, set[str]] = defaultdict(set)
    for identifier in identifiers:
        if (normalized := typed_identifier(identifier)) is not None:
            values[normalized.partition(":")[0]].add(normalized)
    return sorted(kind for kind, items in values.items() if len(items) > 1)


def _identifier_proposals(
    scenario: str,
    groups: tuple[tuple[str, ...], ...],
    works: Mapping[str, _Work],
    cards: Sequence[Card],
) -> tuple[tuple[Json, ...], tuple[Json, ...]]:
    rules: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        if _in_scenario(card, scenario):
            for work in card.work_ids:
                rules[work].add(card.rule)
    proposed: list[Json] = []
    pending: list[Json] = []
    for group in groups:
        members = [works[w] for w in group]
        record_ids = sorted(r for member in members for r in member.record_ids)
        identifiers = sorted({i for member in members for i in member.identifiers})
        kinds = _conflicting_kinds(identifiers)
        if not kinds:
            continue
        conflict = {
            "work_id": typed_work_id(record_ids),
            "manifestation_record_ids": record_ids,
            "identifiers": identifiers,
            "conflicting_identifier_kinds": kinds,
            "source_artifact_sha256s": sorted(
                {sha for member in members for sha in member.source_artifacts}
            ),
        }
        registered = set().union(*(member.registered_dois for member in members))
        arxiv = set().union(*(member.arxiv for member in members))
        dblp = set().union(*(member.dblp_publications for member in members))
        if len(registered) > 1 or len(arxiv) > 1 or len(dblp) > 1:
            pending.append(conflict)
            continue
        joined_by = ", ".join(sorted(set().union(*(rules[w] for w in group))))
        proposed.append(
            {
                "conflict": conflict,
                "disposition": "same_work_identifiers",
                "rationale": (
                    f"Proposal generated by {FORMAT} {GENERATOR_VERSION} for "
                    f"scenario {scenario}; it is not an Owner decision. The "
                    f"{len(group)} proposed works of this final group are joined "
                    f"only by proposed merges ({joined_by}). The plural kinds "
                    f"({', '.join(kinds)}) hold at most one registered DOI, one "
                    "arXiv ID and one DBLP publication key. Every identifier is "
                    "retained and none is preferred."
                ),
            }
        )
    return (
        tuple(sorted(proposed, key=lambda item: item["conflict"]["work_id"])),
        tuple(sorted(pending, key=lambda item: item["work_id"])),
    )


def zero_failure_sample_size(
    population: int,
    max_error_rate: float = AUDIT_MAX_ERROR_RATE,
    confidence: float = AUDIT_CONFIDENCE,
) -> int:
    """Smallest sample whose zero observed errors bound the rate at confidence.

    Hypergeometric acceptance sampling: with D = ceil(population * rate)
    defective cards, the probability of drawing no defect in n cards without
    replacement must not exceed 1 - confidence.
    """
    if population <= 0:
        return 0
    rate = Fraction(str(max_error_rate))
    defects = max(1, math.ceil(population * rate))
    limit = float(1 - Fraction(str(confidence)))
    probability = 1.0
    for size in range(1, population + 1):
        probability *= max(0, population - defects - size + 1) / (population - size + 1)
        if probability <= limit:
            return size
    return population


def _allocate(populations: Mapping[str, int], total: int) -> dict[str, int]:
    size = sum(populations.values())
    quotas = {key: Fraction(count * total, size) for key, count in populations.items()}
    allocation = {key: math.floor(quota) for key, quota in quotas.items()}
    remainder = total - sum(allocation.values())
    by_fraction = sorted(populations, key=lambda k: (allocation[k] - quotas[k], k))
    for key in by_fraction[:remainder]:
        allocation[key] += 1
    return {
        key: min(populations[key], max(1, allocation[key]))
        for key in sorted(populations)
    }


def _stratum(card: Card) -> str:
    if card.tier == "T2":
        return f"{card.rule}:{card.notes[0]}"
    if card.rule == "T1.title_year_authors":
        compared = card.evidence.abstract_similarity is not None
        return f"{card.rule}:{'abstract' if compared else 'no_abstract'}"
    return card.rule


def _rng(seed: int, unit: str, stratum: str) -> random.Random:
    digest = hashlib.sha256(f"{seed}|{unit}|{stratum}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


AUDIT_METHOD = (
    "Per adoption unit (T1-identifier, T1-title, T2, T3): n is the smallest "
    "sample size for which zero observed errors bound the card error rate at "
    "<= 2% with 95% confidence (hypergeometric zero-acceptance, "
    "D = ceil(0.02 N)). Strata are rules; T1-title splits by whether abstracts "
    "were compared and T2 by its first note. n is allocated proportionally by "
    "largest remainder, at least one card per stratum and at most its "
    "population. Each stratum draws "
    "random.Random(int(sha256('seed|unit|stratum')[:8 bytes])).sample over its "
    "cards sorted by work_ids."
)


def _member(work: _Work, records: Mapping[str, Json]) -> Json:
    fields = (
        "record_id",
        "source_id",
        "search_id",
        "rank",
        "title",
        "authors",
        "publication_year",
        "publication_type",
        "venue",
        "landing_page_url",
        "identifiers",
        "raw_artifact_sha256",
    )
    return {
        "work_id": work.work_id,
        "canonical_title": work.title,
        "publication_year": work.year,
        "publication_types": list(work.types),
        "identifiers": list(work.identifiers),
        "observations": [
            {
                **{key: records[r].get(key) for key in fields},
                "abstract_available": bool(records[r].get("abstract")),
            }
            for r in work.record_ids
        ],
    }


def _review_card(
    card: Card, works: Mapping[str, _Work], records: Mapping[str, Json]
) -> Json:
    return {
        **card.as_json(),
        "members": [_member(works[w], records) for w in card.work_ids],
    }


def _audit_sample(
    cards: Sequence[Card],
    works: Mapping[str, _Work],
    records: Mapping[str, Json],
    seed: int,
) -> Json:
    units: Json = {}
    for unit in UNITS:
        strata: dict[str, list[Card]] = defaultdict(list)
        for card in cards:
            if unit_of(card) == unit:
                strata[_stratum(card)].append(card)
        population = sum(len(members) for members in strata.values())
        required = zero_failure_sample_size(population)
        allocation = (
            _allocate({k: len(v) for k, v in strata.items()}, required)
            if population
            else {}
        )
        chosen = []
        for stratum in sorted(strata):
            ordered = sorted(strata[stratum], key=lambda card: card.work_ids)
            for card in _rng(seed, unit, stratum).sample(ordered, allocation[stratum]):
                chosen.append(
                    {"stratum": stratum, **_review_card(card, works, records)}
                )
        units[unit] = {
            "population": population,
            "required_sample_size": required,
            "strata_population": {k: len(strata[k]) for k in sorted(strata)},
            "strata_allocation": allocation,
            "cards": sorted(
                chosen, key=lambda item: (item["stratum"], item["work_ids"])
            ),
        }
    return {
        "format": f"{FORMAT}/audit-sample",
        "seed": seed,
        "method": AUDIT_METHOD,
        "max_error_rate": AUDIT_MAX_ERROR_RATE,
        "confidence": AUDIT_CONFIDENCE,
        "units": units,
    }


@dataclass(frozen=True)
class InputFile:
    path: Path
    sha256: str


@dataclass(frozen=True)
class ScopeFile:
    """JSON list of proposed-work or observation ids, or an object holding one."""

    path: Path
    sha256: str
    key: str | None = None


@dataclass(frozen=True)
class GeneratorInputs:
    records: InputFile
    deduplication: InputFile
    queue: InputFile
    proposal_basis: InputFile | None = None

    def roles(self) -> tuple[tuple[str, InputFile], ...]:
        files = (
            ("records", self.records),
            ("deduplication", self.deduplication),
            ("queue", self.queue),
        )
        if self.proposal_basis is None:
            return files
        return (*files, ("proposal_basis", self.proposal_basis))


@dataclass(frozen=True)
class Proposals:
    inputs: GeneratorInputs
    seed: int
    cards: tuple[Card, ...]
    choices: Mapping[str, tuple[Json, ...]]
    identifier_choices: Mapping[str, tuple[Json, ...]]
    pending_identifier_conflicts: Mapping[str, tuple[Json, ...]]
    worklist: tuple[Json, ...]
    audit_sample: Json
    manifest_fields: Json
    groups: Mapping[str, tuple[tuple[str, ...], ...]]

    def merge_groups(self, scenario: str) -> tuple[tuple[str, ...], ...]:
        return self.groups[scenario]

    def files(self) -> dict[str, bytes]:
        def document(value: object) -> bytes:
            return _canonical(value) + b"\n"

        files = {
            "cards.json": document(
                {
                    "format": f"{FORMAT}/cards",
                    "cards": [card.as_json() for card in self.cards],
                }
            ),
            **{
                f"choices/{unit.lower()}-{UNIT_DISPOSITIONS[unit]}.json": document(
                    list(self.choices[unit])
                )
                for unit in UNITS
            },
            "t4-worklist.json": document(
                {"format": f"{FORMAT}/t4-worklist", "cards": list(self.worklist)}
            ),
            "audit-sample.json": document(self.audit_sample),
        }
        for scenario, name in SCENARIO_FILES.items():
            files[f"identifier-choices/{name}.json"] = document(
                list(self.identifier_choices[scenario])
            )
            files[f"identifier-conflicts-pending/{name}.json"] = document(
                list(self.pending_identifier_conflicts[scenario])
            )
        return files


def _read_verified(role: str, file: InputFile) -> bytes:
    raw = Path(file.path).read_bytes()
    if _sha256(raw) != file.sha256:
        raise ValueError(f"{role} input SHA-256 differs from the expected digest")
    return raw


def _check_lineage(
    inputs: GeneratorInputs,
    observations: Sequence[Json],
    deduplication: Json,
    queue: Json,
) -> None:
    if (queue.get("deduplication") or {}).get("sha256") != inputs.deduplication.sha256:
        raise ValueError("queue does not bind the deduplication input")
    if (queue.get("records") or {}).get("sha256") != inputs.records.sha256:
        raise ValueError("queue does not bind the records input")
    if queue.get("identity_candidates") != deduplication["adjudication_candidates"]:
        raise ValueError(
            "queue identity candidates differ from the deduplication result"
        )
    record_ids = [record["record_id"] for record in observations]
    members = [
        record_id
        for work in (*deduplication["titled_works"], *deduplication["untitled_works"])
        for record_id in work["manifestation_record_ids"]
    ]
    if len(set(record_ids)) != len(record_ids) or sorted(members) != sorted(record_ids):
        raise ValueError(
            "proposed works do not partition the observations exactly once"
        )
    candidate_ids = [
        c["candidate_id"] for c in deduplication["adjudication_candidates"]
    ]
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("deduplication candidate ids are not unique")


def _check_basis_lineage(inputs: GeneratorInputs, basis: Json) -> None:
    if basis.get("schema_version") != "corpus-identity-proposal-basis-1":
        raise ValueError("unsupported proposal basis schema version")
    for role in (
        "preparation",
        "metadata_resolution",
        "records",
        "deduplication",
        "queue",
        "metadata_projection",
    ):
        ref = basis.get(role)
        if not isinstance(ref, dict):
            raise ValueError(f"basis {role} artifact ref is invalid")
        digest = ref.get("sha256")
        if (
            not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
            or type(ref.get("size_bytes")) is not int
            or ref["size_bytes"] <= 0
            or not isinstance(ref.get("media_type"), str)
            or re.fullmatch(
                r"[a-z0-9][a-z0-9!#$&^_.+-]{0,126}/"
                r"[a-z0-9][a-z0-9!#$&^_.+-]{0,126}",
                ref["media_type"],
            )
            is None
            or ref.get("relative_path") != f"sha256/{digest[:2]}/{digest[2:4]}/{digest}"
            or ref.get("access_class") not in {"public", "internal", "restricted"}
        ):
            raise ValueError(f"basis {role} artifact ref is invalid")
    for role in ("records", "deduplication", "queue"):
        if basis[role]["sha256"] != getattr(inputs, role).sha256:
            raise ValueError(f"basis {role} does not bind the original input")
    sources = basis.get("source_artifact_sha256s")
    if (
        not isinstance(sources, list)
        or any(
            not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None
            for digest in sources
        )
        or sources != sorted(set(sources))
    ):
        raise ValueError("basis source artifact hashes are invalid")
    if (
        basis.get("proposal_only") is not True
        or basis.get("screening_ready") is not False
        or basis.get("scientific_eligibility_assessed") is not False
    ):
        raise ValueError("proposal basis claims unsupported scientific authority")


def _check_basis_metadata_partition(deduplication: Json, basis: Json) -> None:
    candidates = deduplication["metadata_review_candidates"]
    candidate_to_work = {
        candidate["candidate_id"]: candidate["work_id"] for candidate in candidates
    }
    untitled = {work["work_id"] for work in deduplication["untitled_works"]}
    if (
        len(candidate_to_work) != len(candidates)
        or len(set(candidate_to_work.values())) != len(candidates)
        or set(candidate_to_work.values()) != untitled
    ):
        raise ValueError("original metadata candidates do not cover untitled works")
    resolved = set(basis["resolved_title_work_ids"])
    explicit = set(basis["explicitly_untitled_work_ids"])
    unresolved = basis["unresolved_metadata_candidate_ids"]
    if (
        not isinstance(unresolved, list)
        or unresolved != sorted(set(unresolved))
        or set(unresolved)
        != {
            candidate_id
            for candidate_id, work_id in candidate_to_work.items()
            if work_id not in resolved | explicit
        }
    ):
        raise ValueError("basis metadata candidate partition is invalid")
    if not (resolved | explicit) <= untitled:
        raise ValueError("basis metadata title states include a non-candidate work")


def _check_basis_works(original: Sequence[Json], basis: Json) -> None:
    original_by_id = {work["work_id"]: work for work in original}
    supplied = basis["works"]
    supplied_by_id = {work["work_id"]: work for work in supplied}
    if (
        len(original_by_id) != len(original)
        or len(supplied_by_id) != len(supplied)
        or set(supplied_by_id) != set(original_by_id)
    ):
        raise ValueError("basis works do not preserve proposed work ids")
    resolved_ids = basis["resolved_title_work_ids"]
    explicit_ids = basis["explicitly_untitled_work_ids"]
    if (
        resolved_ids != sorted(set(resolved_ids))
        or explicit_ids != sorted(set(explicit_ids))
        or set(resolved_ids) & set(explicit_ids)
    ):
        raise ValueError("basis title-state work ids are not canonical")
    for work_id, work in original_by_id.items():
        overlaid = supplied_by_id[work_id]
        identity_fields = (
            "work_id",
            "manifestation_record_ids",
            "identifiers",
            "publication_year",
            "publication_types",
            "correction_status",
            "merge_basis",
        )
        if any(work.get(key) != overlaid.get(key) for key in identity_fields):
            raise ValueError(f"basis work identity differs for {work_id}")
        if work_id in resolved_ids:
            if (
                work["canonical_title"] is not None
                or not isinstance(overlaid["canonical_title"], str)
                or not overlaid["canonical_title"].strip()
                or overlaid.get("schema_version") != "1"
                or "metadata_status" in overlaid
            ):
                raise ValueError(f"basis resolved title is invalid for {work_id}")
        elif (
            overlaid.get("canonical_title") != work.get("canonical_title")
            or overlaid.get("schema_version") != work.get("schema_version")
            or overlaid.get("metadata_status") != work.get("metadata_status")
        ):
            raise ValueError(f"basis changes an unresolved title for {work_id}")
        if work_id in explicit_ids and work["canonical_title"] is not None:
            raise ValueError(f"basis explicit untitled id is not untitled: {work_id}")
    if (set(resolved_ids) | set(explicit_ids)) - set(original_by_id):
        raise ValueError("basis title-state ids contain an unknown work")


def _check_overlay_candidates(
    basis: Json,
    original: Sequence[Json],
    observations: Mapping[str, Json],
    original_candidates: Sequence[Json],
) -> None:
    work_by_record = {
        record_id: work["work_id"]
        for work in original
        for record_id in work["manifestation_record_ids"]
    }
    works = {work["work_id"]: work for work in original}
    known_pairs = {
        tuple(
            sorted(work_by_record[record_id] for record_id in candidate["record_ids"])
        )
        for candidate in original_candidates
    }
    candidate_ids = {candidate["candidate_id"] for candidate in original_candidates}
    resolved = set(basis["resolved_title_work_ids"])
    sources = set(basis["source_artifact_sha256s"])
    for overlay in basis["overlay_candidates"]:
        pair = overlay["pair"]
        record_ids = pair["record_ids"]
        if (
            len(record_ids) != 2
            or record_ids != sorted(set(record_ids))
            or any(record_id not in work_by_record for record_id in record_ids)
        ):
            raise ValueError("overlay pair has invalid record ids")
        work_ids = tuple(sorted(work_by_record[record_id] for record_id in record_ids))
        if (
            work_ids[0] == work_ids[1]
            or overlay["source_work_ids"] != list(work_ids)
            or not resolved.intersection(work_ids)
            or work_ids in known_pairs
        ):
            raise ValueError("overlay pair does not identify a new resolved work pair")
        known_pairs.add(work_ids)
        hashes = overlay["metadata_choice_sha256s"]
        expected_id = "dedupe.overlay." + _sha256(_canonical((work_ids, hashes)))[:24]
        if (
            not hashes
            or hashes != sorted(set(hashes))
            or pair["candidate_id"] != expected_id
            or pair["candidate_id"] in candidate_ids
            or pair.get("disposition") != "pending_human_adjudication"
        ):
            raise ValueError("overlay pair has invalid candidate evidence")
        candidate_ids.add(pair["candidate_id"])
        if (
            overlay.get("schema_version") != "corpus-overlay-identity-candidate-1"
            or overlay["metadata_resolution"] != basis["metadata_resolution"]
        ):
            raise ValueError("overlay pair is not bound to metadata resolution")
        expected_sources = sorted(
            {
                observations[record_id]["raw_artifact_sha256"]
                for work_id in work_ids
                for record_id in works[work_id]["manifestation_record_ids"]
            }
        )
        if (
            overlay["source_artifact_sha256s"] != expected_sources
            or not set(expected_sources) <= sources
        ):
            raise ValueError("overlay pair source artifacts differ from observations")


def _read_scope(scope: ScopeFile) -> frozenset[str]:
    value = json.loads(_read_verified("scope", InputFile(scope.path, scope.sha256)))
    if scope.key is not None:
        if not isinstance(value, dict) or scope.key not in value:
            raise ValueError(f"scope file has no key {scope.key!r}")
        value = value[scope.key]
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ValueError("scope must be a JSON list of work or observation ids")
    return frozenset(value)


def _reused_titles(works: Mapping[str, _Work], keys: set[str]) -> set[str]:
    wanted = {key for key in keys if not _is_generic(key)}
    carriers: dict[str, list[_Work]] = defaultdict(list)
    for work in works.values():
        if work.name_tokens:
            for key in work.script_title_keys & wanted:
                carriers[key].append(work)
    return {
        key
        for key, members in carriers.items()
        if any(_authors_disjoint(a, b) for a, b in combinations(members, 2))
    }


def generate(
    inputs: GeneratorInputs, *, seed: int, scope: ScopeFile | None = None
) -> Proposals:
    """Verify the inputs and derive every proposal in memory, without writes.

    With a scope, the full corpus is still classified and closed transitively;
    outputs are the projection onto cards touching the scoped works, with
    merge groups, identifier choices and the audit recomputed for them.
    """
    raw = {role: _read_verified(role, file) for role, file in inputs.roles()}
    observations = json.loads(raw["records"])
    deduplication = json.loads(raw["deduplication"])
    queue = json.loads(raw["queue"])
    _check_lineage(inputs, observations, deduplication, queue)
    records = {record["record_id"]: record for record in observations}
    original_works = (
        *deduplication["titled_works"],
        *deduplication["untitled_works"],
    )
    basis = json.loads(raw["proposal_basis"]) if inputs.proposal_basis else None
    if basis is not None:
        _check_basis_lineage(inputs, basis)
        _check_basis_works(original_works, basis)
        _check_basis_metadata_partition(deduplication, basis)
        _check_overlay_candidates(
            basis, original_works, records, deduplication["adjudication_candidates"]
        )
    basis_works = basis["works"] if basis else original_works
    resolved = set(basis["resolved_title_work_ids"]) if basis else set()
    works = {
        work["work_id"]: _profile(
            work,
            records,
            resolved_title=work["canonical_title"]
            if work["work_id"] in resolved
            else None,
        )
        for work in basis_works
    }
    work_of = {r: work.work_id for work in works.values() for r in work.record_ids}
    scope_ids = _read_scope(scope) if scope is not None else None
    scope_works: frozenset[str] | None = None
    if scope_ids is not None:
        unknown = scope_ids - set(works) - set(work_of)
        if unknown:
            raise ValueError(
                f"scope holds {len(unknown)} ids that are not works or observations"
            )
        scope_works = frozenset(i if i in works else work_of[i] for i in scope_ids)
    by_pair: dict[tuple[str, str], list[str]] = defaultdict(list)
    candidates = [*deduplication["adjudication_candidates"]]
    if basis:
        candidates.extend(item["pair"] for item in basis["overlay_candidates"])
    for candidate in candidates:
        left, right = sorted(work_of[r] for r in candidate["record_ids"])
        if left == right:
            raise ValueError("a candidate joins observations of one proposed work")
        by_pair[(left, right)].append(candidate["candidate_id"])
    shared_titles = {
        key
        for left, right in by_pair
        for key in works[left].script_title_keys & works[right].script_title_keys
    }
    reused = _reused_titles(works, shared_titles)
    component = {
        work: "identity-component." + _sha256(_canonical(list(group)))[:24]
        for group in _groups(by_pair)
        for work in group
    }
    cards = []
    for pair in sorted(by_pair):
        evidence = _evidence(works[pair[0]], works[pair[1]], reused)
        tier, rule, notes = _classify(evidence)
        cards.append(
            Card(
                work_ids=pair,
                component_id=component[pair[0]],
                candidate_ids=tuple(sorted(by_pair[pair])),
                tier=tier,
                rule=rule,
                notes=notes,
                evidence=evidence,
            )
        )
    _enforce_transitivity(cards, works)
    if scope_works is not None:
        cards = [card for card in cards if set(card.work_ids) & scope_works]
    transitive = _demotion_stats(cards)
    scenario_stats, groups = _merge_scenarios(cards, works)
    for scenario, values in scenario_stats.items():
        transitive.setdefault(scenario, {}).update(values)
    choices = {
        unit: tuple(
            {"candidate_id": candidate, "disposition": disposition}
            for candidate in sorted(
                c for card in cards if unit_of(card) == unit for c in card.candidate_ids
            )
        )
        for unit, disposition in UNIT_DISPOSITIONS.items()
    }
    identifier_choices = {}
    pending_conflicts = {}
    for scenario in SCENARIOS:
        identifier_choices[scenario], pending_conflicts[scenario] = (
            _identifier_proposals(scenario, groups[scenario], works, cards)
        )
    worklist = tuple(
        _review_card(card, works, records) for card in cards if card.tier == "T4"
    )
    audit = _audit_sample(cards, works, records, seed)
    listed = sorted(
        [item["candidate_id"] for tier in choices for item in choices[tier]]
        + [c for card in worklist for c in card["candidate_ids"]]
    )
    if listed != sorted(c for card in cards for c in card.candidate_ids) or (
        scope is None and listed != sorted(c["candidate_id"] for c in candidates)
    ):
        raise RuntimeError("proposal lists do not cover every candidate exactly once")
    counts = {
        "observations": len(records),
        "proposed_works": len(works),
        "cards": len(cards),
        "candidates": len(listed),
        "cards_by_tier": dict(sorted(Counter(card.tier for card in cards).items())),
        "candidates_by_tier": dict(
            sorted(
                Counter(card.tier for card in cards for _ in card.candidate_ids).items()
            )
        ),
        "cards_by_unit": dict(
            sorted(Counter(unit_of(card) or "T4" for card in cards).items())
        ),
        "candidates_by_unit": dict(
            sorted(
                Counter(
                    unit_of(card) or "T4" for card in cards for _ in card.candidate_ids
                ).items()
            )
        ),
        "cards_by_rule": dict(sorted(Counter(card.rule for card in cards).items())),
        "candidates_by_rule": dict(
            sorted(
                Counter(card.rule for card in cards for _ in card.candidate_ids).items()
            )
        ),
        "t2_notes": dict(
            sorted(
                Counter(
                    note
                    for card in cards
                    if card.tier == "T2"
                    for note in card.notes
                    if not note.startswith("joined_by_")
                ).items()
            )
        ),
    }
    manifest_fields: Json = {
        "format": f"{FORMAT}/manifest",
        "generator": {
            "module": __spec__.name if __spec__ else __name__,
            "version": GENERATOR_VERSION,
            "source_sha256": _sha256(Path(__file__).read_bytes()),
            "python": platform.python_version(),
        },
        "seed": seed,
        "scope": None
        if scope is None or scope_ids is None or scope_works is None
        else {
            "path": str(Path(scope.path).absolute()),
            "sha256": scope.sha256,
            "key": scope.key,
            "ids": len(scope_ids),
            "matched_proposed_works": len(scope_works),
            "cards": len(cards),
            "projection": (
                "Tiers and transitive withholding come from the full-corpus run; "
                "choices, groups, identifier choices, worklist and audit cover "
                "only cards touching the scoped works."
            ),
        },
        "decision_status": "proposals_only",
        "owner_decisions": [],
        "inputs": [
            {
                "role": role,
                "path": str(Path(file.path).absolute()),
                "sha256": file.sha256,
                "size_bytes": len(raw[role]),
            }
            for role, file in inputs.roles()
        ],
        "rules": RULES,
        "definitions": DEFINITIONS,
        "thresholds": {
            "identifier_author_jaccard": IDENTIFIER_AUTHOR_JACCARD,
            "version_author_jaccard": VERSION_AUTHOR_JACCARD,
            "identifier_year_gap": IDENTIFIER_YEAR_GAP,
            "version_year_gap": VERSION_YEAR_GAP,
            "abstract_jaccard": ABSTRACT_THRESHOLD,
            "abstract_support": ABSTRACT_SUPPORT,
            "min_abstract_tokens": MIN_ABSTRACT_TOKENS,
        },
        "generic_title_pattern": GENERIC_TITLE.pattern,
        "repository_venue_pattern": _REPOSITORY_VENUE.pattern,
        "institution_suffix_pattern": _INSTITUTION_SUFFIX.pattern,
        "index_or_platform_pattern": _INDEX_OR_PLATFORM.pattern,
        "repository_host_pattern": _REPOSITORY_HOST.pattern,
        "repository_doi_prefixes": {
            **REPOSITORY_DOI_PREFIXES,
            **DATED_REPOSITORY_DOI_PREFIXES,
        },
        "units": {unit: sorted(rules) for unit, rules in UNITS.items()},
        "scenarios": {name: list(units) for name, units in SCENARIOS.items()},
        "owner_policy_required": OWNER_POLICY,
        "counts": counts,
        "transitive": transitive,
        "identifier_choices": {
            scenario: {
                "proposed": len(identifier_choices[scenario]),
                "pending": len(pending_conflicts[scenario]),
            }
            for scenario in SCENARIOS
        },
        "audit": {
            "seed": seed,
            "method": AUDIT_METHOD,
            "units": {
                unit: {
                    key: value
                    for key, value in audit["units"][unit].items()
                    if key != "cards"
                }
                for unit in audit["units"]
            },
        },
    }
    if basis is not None and inputs.proposal_basis is not None:
        manifest_fields["proposal_basis"] = {
            "schema_version": basis["schema_version"],
            "sha256": inputs.proposal_basis.sha256,
            "preparation_sha256": basis["preparation"]["sha256"],
            "metadata_resolution_sha256": basis["metadata_resolution"]["sha256"],
            "metadata_projection_sha256": basis["metadata_projection"]["sha256"],
            "resolved_title_work_ids": basis["resolved_title_work_ids"],
            "explicitly_untitled_work_ids": basis["explicitly_untitled_work_ids"],
            "unresolved_metadata_candidate_ids": basis[
                "unresolved_metadata_candidate_ids"
            ],
            "overlay_candidates": len(basis["overlay_candidates"]),
            "source_artifact_sha256s": basis["source_artifact_sha256s"],
        }
    return Proposals(
        inputs=inputs,
        seed=seed,
        cards=tuple(cards),
        choices=choices,
        identifier_choices=identifier_choices,
        pending_identifier_conflicts=pending_conflicts,
        worklist=worklist,
        audit_sample=audit,
        manifest_fields=json.loads(_canonical(manifest_fields)),
        groups=groups,
    )


def _evidence_root(path: Path) -> Path:
    resolved = Path(path).resolve()
    for parent in resolved.parents:
        if parent.name == "sha256":
            return parent.parent.parent
    return resolved.parent


def _write_new(path: Path, raw: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    with os.fdopen(os.open(path, flags, 0o600), "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(path, 0o400)


def write(
    proposals: Proposals,
    output_dir: Path,
    *,
    revision: str,
    protected_roots: Sequence[Path] = (),
) -> Json:
    """Write every proposal file and the manifest into a new directory."""
    target = Path(output_dir).absolute()
    roots = [Path(root).resolve() for root in protected_roots] + [
        _evidence_root(file.path) for _, file in proposals.inputs.roles()
    ]
    resolved = target.resolve()
    for root in roots:
        if resolved.is_relative_to(root):
            raise ValueError(f"output directory is inside the protected root {root}")
    files = proposals.files()
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    target.mkdir(mode=0o700)
    outputs = []
    for relative in sorted(files):
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        _write_new(path, files[relative])
        outputs.append(
            {
                "path": relative,
                "sha256": _sha256(files[relative]),
                "size_bytes": len(files[relative]),
            }
        )
    manifest = {
        **proposals.manifest_fields,
        "git_revision": revision,
        "outputs": outputs,
    }
    raw = _canonical(manifest) + b"\n"
    _write_new(target / "manifest.json", raw)
    loaded: Json = json.loads(raw)
    return loaded


def _clean_revision() -> str:
    root = Path(__file__).resolve().parents[3]
    status = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root,
        text=True,
    )
    if status.strip():
        raise SystemExit("commit every change before a recorded proposal run")
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate corpus-identity proposals without recording decisions."
    )
    for role in ("records", "deduplication", "queue"):
        parser.add_argument(f"--{role}", type=Path, required=True)
        parser.add_argument(f"--{role}-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--protected-root", type=Path, action="append", default=[])
    parser.add_argument("--scope", type=Path)
    parser.add_argument("--scope-sha256")
    parser.add_argument("--scope-key")
    parser.add_argument("--proposal-basis", type=Path)
    parser.add_argument("--proposal-basis-sha256")
    args = parser.parse_args(argv)
    if (args.scope is None) != (args.scope_sha256 is None):
        parser.error("--scope and --scope-sha256 go together")
    if (args.proposal_basis is None) != (args.proposal_basis_sha256 is None):
        parser.error("--proposal-basis and --proposal-basis-sha256 go together")
    revision = _clean_revision()
    inputs = GeneratorInputs(
        records=InputFile(args.records, args.records_sha256),
        deduplication=InputFile(args.deduplication, args.deduplication_sha256),
        queue=InputFile(args.queue, args.queue_sha256),
        proposal_basis=InputFile(args.proposal_basis, args.proposal_basis_sha256)
        if args.proposal_basis is not None
        else None,
    )
    scope = (
        ScopeFile(args.scope, args.scope_sha256, args.scope_key)
        if args.scope is not None
        else None
    )
    manifest = write(
        generate(inputs, seed=args.seed, scope=scope),
        args.output,
        revision=revision,
        protected_roots=args.protected_root,
    )
    raw = (Path(args.output) / "manifest.json").read_bytes()
    summary = {
        "manifest_sha256": _sha256(raw),
        "git_revision": revision,
        "counts": manifest["counts"],
        "transitive": manifest["transitive"],
        "identifier_choices": manifest["identifier_choices"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
