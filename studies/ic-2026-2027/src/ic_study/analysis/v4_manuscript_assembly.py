"""Assemble reviewed shells from exported catalogs and sourced Owner facts.

Run with ``--audit-only`` to inspect decisions without copying a manuscript.
Missing evidence refuses assembly; no branch override or rounded-value verdict
is accepted. This module reads neither simulation stores nor SHP source data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any, cast

from ic_study.analysis.v4_manuscript_assembly_facts import (
    facts_sha256,
    facts_values,
    unique_object,
    validate_facts,
)

SCHEMA = "ic-study.v4-manuscript-assembly.v1"
RULES = Path(__file__).with_name("v4_manuscript_assembly_rules.json")
RESULT = re.compile(r"\\resultnum\{([^{}]+)\}\{([^{}]+)\}")
PLURAL = re.compile(r"\\resultplural\{([^{}]+)\}\{([^{}]*)\}\{([^{}]*)\}")
COMMENTS = re.compile(r"(?m)(?<!\\)((?:\\\\)*)%[^\n]*")
WORDS = re.compile(r"\b[\w]+(?:[-'][\w]+)*\b", re.UNICODE)
OPTIONAL_ORDER = (
    "A.B09.1",
    "A.B09.2",
    "A.B09.3",
    "A.B04",
    "A.B05",
    "A.B08",
    "A.B11",
    "A.B14",
)
Expr = bool | dict[str, Any]


def _permitted(path: Path) -> Path:
    for candidate in (path.absolute(), path.resolve()):
        parts = candidate.parts
        if any(p.startswith("sealed-v4-") or p == "restricted" for p in parts):
            raise ValueError("Forbidden input/output path")
        for index, part in enumerate(parts[:-1]):
            if part == "coord-20260925" and parts[index + 1] in {
                "v4-tier-logs",
                "v4-gate-logs",
                "v4-release",
            }:
                raise ValueError("Forbidden input/output path")
    return path.resolve()


def load_catalog(path: Path) -> dict[str, str]:
    """Read only the values of an exported catalog, without following provenance."""
    return _values(load_catalog_record(path)["values"])


def load_catalog_record(path: Path) -> dict[str, Any]:
    obj = json.loads(
        _permitted(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object
    )
    if not isinstance(obj, dict) or obj.get("schema") not in {
        "ic-study.v4-result-values.v1",
        "ic-study.v4-exploratory-result-values.v1",
        "ic-study.v4-merged-result-values.v1",
    }:
        raise ValueError("Expected an exported v4 result-values catalog")
    _values(obj.get("values"))
    return cast(dict[str, Any], obj)


def load_facts(path: Path) -> dict[str, Any]:
    obj = json.loads(
        _permitted(path).read_text(encoding="utf-8"), object_pairs_hook=unique_object
    )
    return validate_facts(obj)


def _values(obj: object) -> dict[str, str]:
    if not isinstance(obj, dict) or any(
        not isinstance(k, str) or not isinstance(v, str) for k, v in obj.items()
    ):
        raise ValueError("Catalog values must map IDs to formatted strings")
    return cast(dict[str, str], obj).copy()


def _merged(a: Mapping[str, str], x: Mapping[str, str]) -> dict[str, str]:
    values = _values(dict(a))
    extra = _values(dict(x))
    conflicts = sorted(k for k in values.keys() & extra.keys() if values[k] != extra[k])
    if conflicts:
        raise ValueError("Conflicting catalog IDs: " + ", ".join(conflicts))
    return values | extra


def _visible(source: str) -> str:
    return "\n".join(
        line for line in COMMENTS.sub(r"\1", source).splitlines() if line.strip()
    ).strip()


def visible_word_count(abstract: str) -> int:
    """The visible-abstract formula of pipeline/paper_check.py, decision 101."""
    visible = PLURAL.sub(lambda match: match[3], abstract)
    visible = RESULT.sub(lambda match: match[2], visible)
    return len(WORDS.findall(re.sub(r"\\[A-Za-z]+", "", visible)))


@dataclass(frozen=True)
class BudgetStep:
    id: str
    candidate_words: int
    included: bool


@dataclass(frozen=True)
class AbstractBudget:
    text: str
    words: int
    steps: tuple[BudgetStep, ...]


def first_fit(
    mandatory: Sequence[str],
    optional: Mapping[str, str],
    *,
    limit: int = 250,
    closing_sentences: int = 1,
) -> AbstractBudget:
    """Compose bound sentences, retaining the declared mandatory closing suffix.

    Mandatory consequences enter before testing any optional sentence. A rejected
    optional sentence leaves earlier selections in place; later ones still try.
    This text composer neither selects a scientific branch nor waives a refusal.
    """
    if not 1 <= closing_sentences <= len(mandatory) or set(optional) - set(
        OPTIONAL_ORDER
    ):
        raise ValueError("Expected mandatory sentences and decision-101 optional IDs")
    chosen = list(mandatory)
    if visible_word_count(" ".join(chosen)) > limit:
        raise ValueError("Mandatory abstract exceeds the word budget")
    steps = []
    for name in OPTIONAL_ORDER:
        if name not in optional:
            continue
        candidate = [
            *chosen[:-closing_sentences],
            optional[name],
            *chosen[-closing_sentences:],
        ]
        count = visible_word_count(" ".join(candidate))
        include = count <= limit
        steps.append(BudgetStep(name, count, include))
        if include:
            chosen = candidate
    text = " ".join(chosen)
    return AbstractBudget(text, visible_word_count(text), tuple(steps))


@dataclass(frozen=True)
class Evaluation:
    value: bool | None
    reasons: tuple[str, ...] = ()


class _Evaluator:
    def __init__(
        self,
        values: Mapping[str, str],
        expressions: Mapping[str, Expr],
        facts: Mapping[str, Any],
    ):
        self.values = values
        self.expressions = expressions
        self.facts = facts
        self.cache: dict[str, Evaluation] = {}
        self.visiting: set[str] = set()

    def named(self, name: str) -> Evaluation:
        if name not in self.expressions or name in self.visiting:
            raise ValueError("Unknown or cyclic rule reference: " + name)
        if name not in self.cache:
            self.visiting.add(name)
            self.cache[name] = self.evaluate(self.expressions[name])
            self.visiting.remove(name)
        return self.cache[name]

    def evaluate(self, expr: Expr) -> Evaluation:
        if isinstance(expr, bool):
            return Evaluation(expr)
        if len(expr) != 1:
            raise ValueError("A condition must have exactly one operator")
        op, arg = next(iter(expr.items()))
        if op == "ref":
            return self.named(str(arg))
        if op == "unsupported":
            return Evaluation(None, (str(arg),))
        if op in {"all", "any"}:
            items = [self.evaluate(item) for item in arg]
            decisive = op != "all"
            if any(item.value is decisive for item in items):
                return Evaluation(decisive)
            reasons = tuple(sorted({r for item in items for r in item.reasons}))
            if any(item.value is None for item in items):
                return Evaluation(None, reasons)
            return Evaluation(not decisive)
        if op == "not":
            item = self.evaluate(arg)
            return Evaluation(
                None if item.value is None else not item.value, item.reasons
            )
        if op in {"fact", "fact_eq", "fact_contains", "fact_recorded"}:
            key = arg if op in {"fact", "fact_recorded"} else arg[0]
            if key not in self.facts:
                return Evaluation(None, ("Missing assembly fact: " + key,))
            value = self.facts[key]
            if op == "fact_recorded":
                return Evaluation(True)
            if op == "fact":
                return Evaluation(cast(bool, value))
            return Evaluation(value == arg[1] if op == "fact_eq" else arg[1] in value)
        if op == "exists":
            return Evaluation(arg in self.values)
        if op == "matching_eq":
            pattern, expected = arg
            return Evaluation(
                any(
                    v == expected and fnmatchcase(k, pattern)
                    for k, v in self.values.items()
                )
            )
        if op == "labels":
            value = self.values.get(arg["id"])
            if value is None or value in arg["allowed"]:
                return Evaluation(True)
            return Evaluation(None, ("Unknown X6 machine label: " + value,))
        if op == "finite":
            try:
                finite_value = Decimal(self.values.get(arg, "NaN").replace(",", ""))
            except InvalidOperation:
                return Evaluation(False)
            return Evaluation(finite_value.is_finite())
        if op == "same":
            missing = [key for key in arg if key not in self.values]
            if missing:
                return Evaluation(None, ("Missing catalog ID: " + missing[0],))
            numbers = set()
            for key in arg:
                try:
                    number = Decimal(self.values[key].replace(",", ""))
                except InvalidOperation:
                    number = Decimal("NaN")
                if not number.is_finite():
                    return Evaluation(None, ("Non-numeric catalog ID: " + key,))
                numbers.add(number)
            return Evaluation(len(numbers) == 1)
        if op not in {"eq", "gt"}:
            raise ValueError("Unknown condition operator: " + op)
        key, expected = arg
        if key not in self.values:
            return Evaluation(None, ("Missing catalog ID: " + key,))
        value = self.values[key]
        if op == "eq":
            return Evaluation(value == expected)
        try:
            number = Decimal(value.replace(",", ""))
            threshold = Decimal(expected)
            if number.is_finite() and threshold.is_finite():
                return Evaluation(number > threshold)
        except InvalidOperation:
            pass
        return Evaluation(None, ("Non-numeric catalog ID: " + key,))


@dataclass(frozen=True)
class Decision:
    id: str
    source: str
    line: int
    end_line: int
    state: str
    reason: str
    text: str
    slot: str
    operation: str
    order: float
    optional: bool


@dataclass(frozen=True)
class AssemblyPlan:
    decisions: dict[str, Decision]
    values_sha256: str
    rules_sha256: str
    source_sha256: dict[str, str]
    facts: dict[str, Any] | None = None

    @property
    def refused(self) -> tuple[Decision, ...]:
        return tuple(d for d in self.decisions.values() if d.state == "refused")

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "status": "refused" if self.refused else "ready",
            "values_sha256": self.values_sha256,
            "rules_sha256": self.rules_sha256,
            "source_sha256": self.source_sha256,
            "facts": self.facts,
            "facts_sha256": facts_sha256(self.facts)
            if self.facts is not None
            else None,
            "counts": {
                state: sum(d.state == state for d in self.decisions.values())
                for state in ("selected", "excluded", "refused")
            },
            "decisions": [
                {k: v for k, v in asdict(d).items() if k != "text"}
                for d in self.decisions.values()
            ],
        }


class AssemblyRefusedError(ValueError):
    def __init__(self, report: AssemblyPlan):
        self.report = report
        super().__init__(
            "Assembly refused: "
            + "; ".join(
                f"{d.id} ({d.source}:{d.line}): {d.reason}" for d in report.refused
            )
        )


def _registry(manuscript: Path) -> tuple[dict[str, Any], dict[str, list[str]]]:
    obj: dict[str, Any] = json.loads(RULES.read_text(encoding="utf-8"))
    if obj.get("schema") != "ic-study.v4-manuscript-assembly-rules.v1":
        raise ValueError("Unsupported rule registry")
    root = _permitted(manuscript)
    lines = {}
    for name, source in obj["sources"].items():
        path = _permitted(root / source["path"])
        if not path.is_relative_to(root):
            raise ValueError("Shell outside the manuscript")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError(
                "Shell changed; review rules before assembly: " + source["path"]
            )
        lines[name] = raw.decode("utf-8").splitlines()
    names = [row["id"] for row in obj["rules"]]
    if len(names) != len(set(names)) or set(names) & obj["predicates"].keys():
        raise ValueError("Duplicate rule or predicate ID")
    return obj, lines


def shell_texts(*, manuscript: Path) -> dict[str, str]:
    """Source fragments for audit/test comparison; this does not select branches."""
    registry, sources = _registry(manuscript)
    texts = {}
    for row in registry["rules"]:
        lines = sources[row["source"]]
        start, end = row["line"], row["end_line"]
        if not 1 <= start <= end <= len(lines):
            raise ValueError("Invalid shell line range: " + row["id"])
        raw = "\n".join(lines[start - 1 : end])
        if row["source"] == "abstract":
            raw = raw.removeprefix("> ")
        texts[row["id"]] = _visible(raw)
    return texts


def bind(text: str, values: Mapping[str, str], *, locator: str = "block") -> str:
    """Bind numbers and plain-text agreement forms within one selected block."""
    bound_ids = {m[1] for m in RESULT.finditer(COMMENTS.sub(r"\1", text))}

    def agreement(match: re.Match[str]) -> str:
        key, singular, plural = match.groups()
        where = f"{locator}, text line {text.count(chr(10), 0, match.start()) + 1}"
        if key not in values:
            raise ValueError(f"{where}: Missing resultplural value: {key}")
        if key not in bound_ids:
            raise ValueError(
                f"{where}: resultplural ID is not bound in the same block: {key}"
            )
        value = values[key]
        if not re.fullmatch(r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.0+)?", value):
            raise ValueError(
                f"{where}: resultplural requires a nonnegative integer: {key}={value}"
            )
        return singular if Decimal(value.replace(",", "")) == 1 else plural

    resolved = PLURAL.sub(agreement, text)
    if re.search(r"\\resultplural\b", resolved):
        raise ValueError(
            f"{locator}: Malformed resultplural; expected plain-text forms"
        )
    missing = sorted(bound_ids - values.keys())
    if missing:
        raise ValueError("Missing text bindings: " + ", ".join(missing))
    return RESULT.sub(lambda m: rf"\resultnum{{{m[1]}}}{{{values[m[1]]}}}", resolved)


def _prose(value: str) -> str:
    escaped = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "#": r"\#",
        "$": r"\$",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(escaped.get(c, c) for c in value)


def _join_clauses(clauses: Sequence[str]) -> str:
    return (
        clauses[0]
        if len(clauses) == 1
        else ", ".join(clauses[:-1]) + " and " + clauses[-1]
    )


def _criterion_text(text: str, name: str, selected: Sequence[str]) -> str:
    if name == "B1b-G2c":
        if set(selected) == {"a010", "a003"}:
            return text
        body, _, suffix = text.rpartition(", against ")
        first, second = body.split(", and at ", 1)
        clauses = {
            "a010": first,
            "a003": "At " + second.replace("it was", "the variance ratio was", 1),
        }
        return (
            _join_clauses([clauses[k] for k in ("a010", "a003") if k in selected])
            + ", against "
            + suffix
        )
    prefix, _, body = text.partition("; ")
    if name == "B1b-G0":
        parts = body.removesuffix(".").split(", ", 2)
        keys = ("anchor", "budget", "implementation")
        parts[-1] = parts[-1].removeprefix("and ")
        lead = ""
    else:
        body = body.removeprefix("the stage recorded ").removesuffix(".")
        first, rest = body.split(", ", 1)
        second, third = rest.split(" and a standardized", 1)
        parts = [first, second, "a standardized" + third]
        keys = ("anchor", "pointwise", "mean")
        lead = "the stage recorded "
    clauses = dict(zip(keys, parts, strict=True))
    return (
        prefix
        + "; "
        + lead
        + _join_clauses([clauses[k] for k in keys if k in selected])
        + "."
    )


def _fragment_text(
    row: Mapping[str, Any],
    lines: Sequence[str],
    evaluator: _Evaluator,
    default: str,
) -> str:
    if "fragments" not in row:
        return default
    parts: list[str] = []
    for fragment in row["fragments"]:
        result = evaluator.evaluate(fragment["condition"])
        if result.value is None:
            raise ValueError("; ".join(result.reasons))
        if result.value:
            start, end = fragment["line"], fragment["end_line"]
            if not row["line"] <= start <= end <= row["end_line"]:
                raise ValueError("Fragment outside shell rule: " + row["id"])
            text = _visible("\n".join(lines[start - 1 : end]))
            if row["source"] == "abstract":
                text = text.removeprefix("> ")
            clause_spec = row.get("criteria_clauses", row.get("comparison_clauses"))
            if clause_spec and start == clause_spec["line"]:
                key = clause_spec["fact"]
                if key not in evaluator.facts:
                    raise ValueError("Missing assembly fact: " + key)
                text = _criterion_text(text, row["id"], evaluator.facts[key])
            for old, new in fragment.get("replace", {}).items():
                text = text.replace(old, new)
            if "reason_fact" in fragment:
                key = fragment["reason_fact"]
                if key not in evaluator.facts:
                    raise ValueError("Missing assembly fact: " + key)
                reason = _prose(evaluator.facts[key])
                text = text.replace("[reason in words]", reason)
                if "[reason in words]" not in _visible(
                    "\n".join(lines[start - 1 : end])
                ):
                    text += " Reason: " + reason + "."
            parts.extend(line for line in text.splitlines() if line.strip())
    return "\n".join(parts)


def plan(
    confirmatory: Mapping[str, str],
    exploratory: Mapping[str, str],
    *,
    manuscript: Path,
    facts: Mapping[str, Any] | None = None,
) -> AssemblyPlan:
    """Evaluate every reviewed rule with true/false/unknown, never missing=zero."""
    values = _merged(confirmatory, exploratory)
    compared = "v4.t3.n_pairs_compared"
    for counted in ("v4.t3.n_obs_exceeds", "v4.t3.n_channel_dependent"):
        if compared in values and counted in values:
            try:
                denominator = Decimal(values[compared].replace(",", ""))
                numerator = Decimal(values[counted].replace(",", ""))
                valid = (
                    denominator.is_finite()
                    and numerator.is_finite()
                    and 0 <= numerator <= denominator
                )
            except InvalidOperation:
                valid = False
            if not valid:
                raise ValueError(
                    f"Inconsistent channel counts: {counted}={values[counted]} "
                    f"must lie within {compared}={values[compared]}"
                )
    for key, value in values.items():
        if (
            ".verdict." in key
            and key.startswith("v4.gate.")
            and value not in {"0", "1"}
        ):
            raise ValueError("Invalid gate verdict ID: " + key)
    fact_record = validate_facts(dict(facts)) if facts is not None else None
    registry, sources = _registry(manuscript)
    texts = shell_texts(manuscript=manuscript)
    expressions = dict(registry["predicates"])
    expressions.update((r["id"], r["condition"]) for r in registry["rules"])
    evaluator = _Evaluator(
        values, expressions, facts_values(fact_record) if fact_record else {}
    )
    decisions = {}
    for row in registry["rules"]:
        name = row["id"]
        result = evaluator.named(name)
        state = {True: "selected", False: "excluded", None: "refused"}[result.value]
        reason = "; ".join(result.reasons)
        text = ""
        if state == "selected" and row["operation"] not in {"group", "retain"}:
            try:
                required = set(row.get("requires", [])) - values.keys()
                if required:
                    raise ValueError(
                        "Missing table catalog bindings: " + ", ".join(sorted(required))
                    )
                text = bind(
                    _fragment_text(row, sources[row["source"]], evaluator, texts[name]),
                    values,
                    locator=(
                        f"{name} ({registry['sources'][row['source']]['path']}:"
                        f"{row['line']}-{row['end_line']})"
                    ),
                )
                if not text and not row.get("allow_empty", False):
                    raise ValueError("Empty output fragment")
            except ValueError as error:
                state, reason = "refused", str(error)
        decisions[name] = Decision(
            name,
            registry["sources"][row["source"]]["path"],
            row["line"],
            row["end_line"],
            state,
            reason,
            text,
            row["slot"],
            row["operation"],
            row["order"],
            row.get("optional", False),
        )
    branches = [
        "B1a",
        "B1b-G0",
        "B1b-G1b",
        "B1b-G1c",
        "B1c",
        "B1b-G2",
        "B1b-G2c",
        "B1d",
    ]
    chosen = [name for name in branches if decisions[name].state == "selected"]
    if len(chosen) != 1 and not any(
        decisions[name].state == "refused" for name in branches
    ):
        raise ValueError("Expected exactly one terminal gate branch")
    if evaluator.named("PASS").value and evaluator.named("POST").value:
        x5_branches = ("D-X5-POST", "D-X5-POST-UNAVAILABLE")
        if not any(
            decisions[name].state in {"selected", "refused"} for name in x5_branches
        ):
            raise ValueError(
                "X5 supplied fact conflicts with the recorded share states"
            )
    raw = json.dumps(values, sort_keys=True, ensure_ascii=False).encode()
    report = AssemblyPlan(
        decisions,
        hashlib.sha256(raw).hexdigest(),
        hashlib.sha256(RULES.read_bytes()).hexdigest(),
        {s["path"]: s["sha256"] for s in registry["sources"].values()},
        fact_record,
    )
    if not report.refused:
        root = _permitted(manuscript)
        sources_text = {
            name: _permitted(root / name).read_text(encoding="utf-8")
            for name in (
                "main.tex",
                "sections/discussion.tex",
                "sections/conclusion.tex",
                "sections/supplement.tex",
            )
        }
        documents, _ = compose_documents(report, sources_text)
        for index, (source, line, reason) in enumerate(
            document_errors(root, documents), 1
        ):
            name = f"admissibility.{index}"
            decisions[name] = Decision(
                name,
                source,
                line,
                line,
                "refused",
                reason,
                "",
                "",
                "validate",
                0,
                False,
            )
    return report


def document_errors(
    root: Path, documents: Mapping[str, str]
) -> list[tuple[str, int, str]]:
    """Check the expanded document, including repeated occurrences of an input."""
    errors: list[tuple[str, int, str]] = []
    labels: dict[str, str] = {}
    visited: set[str] = set()
    commands = re.compile(r"\\(input|label)\s*\{([^{}]+)\}")
    root = _permitted(root)

    def visit(name: str, stack: tuple[str, ...], origin: tuple[str, int]) -> None:
        path = _permitted(root / name)
        if not path.is_relative_to(root) or (root / name).is_symlink():
            raise ValueError(
                "Document input must remain inside the manuscript: " + name
            )
        if name in stack:
            errors.append((*origin, "Recursive input: " + " -> ".join((*stack, name))))
            return
        if name not in documents and not path.is_file():
            errors.append((*origin, "Missing input: " + name))
            return
        text = (
            documents[name] if name in documents else path.read_text(encoding="utf-8")
        )
        visible = COMMENTS.sub(r"\1", text)
        visited.add(name)
        for match in commands.finditer(visible):
            line = visible.count("\n", 0, match.start()) + 1
            locator = f"{name}:{line} (via {' -> '.join((*stack, name))})"
            if match[1] == "label":
                label = match[2]
                if label in labels:
                    errors.append(
                        (
                            name,
                            line,
                            f"Duplicate label {label}: {labels[label]}; {locator}",
                        )
                    )
                else:
                    labels[label] = locator
            else:
                target = match[2]
                if not target.endswith(".tex"):
                    target += ".tex"
                visit(target, (*stack, name), (name, line))

    visit("main.tex", (), ("main.tex", 1))
    for name in sorted(documents.keys() - visited):
        visit(name, (), (name, 1))
    return errors


# A \par control word not escaped by a preceding backslash pair.
PAR = re.compile(r"(?<!\\)(?:\\\\)*\\par(?![A-Za-z])")


def _check_join(text: str, where: str, *, same_line: bool) -> None:
    """Refuse a join unless its text ends on a prose line that the join continues.

    A trailing % comment is refused when the joined text would follow on the
    same line, or when the comment is glued to the prose so that TeX would drop
    the space at the line end.
    """
    if not text.strip():
        raise ValueError(f"{where} join: no paragraph before the join point")
    last = text.rstrip().rsplit("\n", 1)[-1]
    match = COMMENTS.search(last)
    code = last[: match.start() + len(match[1])] if match else last
    if not code.strip():
        raise ValueError(f"{where} join: the text before it ends in a comment line")
    if match and (same_line or not code[-1].isspace()):
        raise ValueError(f"{where} join: the last prose line ends in a % comment")
    if PAR.search(code):
        raise ValueError(f"{where} join: \\par before the join point")


def _insert_discussion(
    source: str,
    additions: Mapping[str, str],
    joins: Mapping[str, str] | None = None,
) -> str:
    joins = joins or {}
    markers = list(re.finditer(r"(?m)^% (DS\d\d)\b[^\n]*\n", source))
    slots = {m[1] for m in markers}
    if (additions.keys() | joins.keys()) - slots:
        raise ValueError("Missing Discussion insertion slot")
    for index in range(len(markers) - 1, -1, -1):
        marker = markers[index]
        if marker[1] in additions or marker[1] in joins:
            end = (
                markers[index + 1].start() if index + 1 < len(markers) else len(source)
            )
            before = source[:end].rstrip()
            if marker[1] in joins:
                _check_join(source[marker.end() : end], marker[1], same_line=False)
                before += "\n" + joins[marker[1]]
            if marker[1] in additions:
                before += "\n\n" + additions[marker[1]]
            source = before + "\n\n" + source[end:]
    return source


def _abstract_span(main: str) -> tuple[int, int]:
    match = re.search(r"\\abstract\s*\{", main)
    if match is None:
        raise ValueError("Missing abstract command")
    depth = 1
    for index in range(match.end(), len(main)):
        if main[index - 1] == "\\":
            continue
        if main[index] == "{":
            depth += 1
        elif main[index] == "}":
            depth -= 1
            if depth == 0:
                return match.end(), index
    raise ValueError("Unbalanced abstract command")


def compose_documents(
    report: AssemblyPlan, sources: Mapping[str, str]
) -> tuple[dict[str, str], AbstractBudget]:
    """Apply only a fully decided plan; preserve the fixed Discussion and X5."""
    if report.refused:
        raise AssemblyRefusedError(report)
    selected = sorted(
        (d for d in report.decisions.values() if d.state == "selected" and d.text),
        key=lambda d: (d.order, d.id),
    )
    slots: dict[str, list[str]] = {}
    mandatory, optional = [], {}
    interval = report.decisions.get("D-X6-INTERVAL")
    for decision in selected:
        if decision.id == "D-X6-INTERVAL":
            continue
        text = decision.text
        if (
            decision.id == "D-X6-DENOMINATORS"
            and interval
            and interval.state == "selected"
        ):
            first, separator, rest = text.partition("\n")
            text = first + "\n" + interval.text + separator + rest
        if (
            decision.id in {"P5-b.range", "P5-b.single"}
            and report.decisions["B06"].state == "selected"
        ):
            text = re.sub(r", and at every value.*?equalled it\.", ".", text)
        if decision.slot == "abstract":
            if decision.optional:
                optional[decision.id] = text
            else:
                mandatory.append(text)
        else:
            slots.setdefault(decision.slot, []).append(text)
    abstract_mandatory = [
        d for d in selected if d.slot == "abstract" and not d.optional
    ]
    closing_sentences = (
        2
        if len(abstract_mandatory) >= 2
        and abstract_mandatory[-2].id == "A.new-seeds"
        and abstract_mandatory[-2].order
        > max((d.order for d in selected if d.optional), default=0)
        else 1
    )
    budget = first_fit(mandatory, optional, closing_sentences=closing_sentences)
    if not 150 <= budget.words <= 250:
        raise ValueError(f"JCSS visible abstract has {budget.words} words")
    # One slot is one paragraph; supplement blocks keep their own paragraphs.
    joined = {
        name: ("\n\n" if name in {"exploratory", "secondary"} else "\n").join(parts)
        for name, parts in slots.items()
    }
    results = "\n\n".join(
        text
        for name, text in joined.items()
        if name.startswith("P") or name.startswith("gate")
    )
    includes = {
        "tab:v4-T3": "gate-outcomes",
        "tab:v4-T4": "unit-status",
        "fig:v4-F1": "primary-boundary-figure",
        "fig:v4-F2B": "auc-profiles",
        "tab:v4-T1": "boundary-table",
        "fig:v4-F6": "shp-anchor",
    }
    seen: set[str] = set()
    paragraphs = []
    passed = report.decisions.get("B1a")
    display_order = (
        "primary-boundary-figure",
        "auc-profiles",
        "boundary-table",
        "gate-outcomes",
        "unit-status",
    )
    for paragraph in results.split("\n\n"):
        paragraphs.append(paragraph)
        if (
            passed
            and passed.state == "selected"
            and paragraph != joined.get("P1")
            and not seen.intersection(display_order)
            and any(
                label in paragraph for label in ("fig:v4-F1", "fig:v4-F2B", "tab:v4-T1")
            )
        ):
            paragraphs.extend(rf"\input{{generated/{name}}}" for name in display_order)
            seen.update(display_order)
        for label in re.findall(r"\\ref\{([^{}]+)\}", paragraph):
            filename = includes.get(label)
            if passed and passed.state == "selected" and filename in display_order:
                continue
            if filename and filename not in seen:
                paragraphs.append(rf"\input{{generated/{filename}}}")
                seen.add(filename)
    additions: dict[str, list[str]] = {}
    joins: dict[str, str] = {}
    for name, text in joined.items():
        if name.endswith("-join") and name.startswith("DS"):
            joins[name.removesuffix("-join")] = text
        elif name.startswith("DS"):
            # A dotted sub-slot is a further paragraph after the same marker.
            additions.setdefault(name.partition(".")[0], []).append(text)
    discussion = _insert_discussion(
        sources["sections/discussion.tex"],
        {k: "\n\n".join(v) for k, v in additions.items()},
        joins,
    )
    conclusion = sources["sections/conclusion.tex"]
    placeholders = list(re.finditer(r"\[(?:Insert|State whether)[^]]*\]", conclusion))
    if len(placeholders) != 3:
        raise ValueError("Expected exactly the three CN01 insertion markers")
    for marker, slot in reversed(
        list(zip(placeholders, ("C1", "C2", "C3"), strict=True))
    ):
        before = conclusion[: marker.start()]
        if slot == "C3" and slots.get("CN01-join"):
            # Joins the fixed CN01 paragraph that precedes C3, not a new paragraph.
            _check_join(before, "CN01", same_line=True)
            before = before.rstrip() + " " + " ".join(slots["CN01-join"]) + "\n\n"
        if slot == "C1" and joined.get("C1"):
            # The headline answers the opening question in the same paragraph.
            inline = not re.search(r"\n\s*$", before)
            _check_join(before, "C1", same_line=inline)
            before = re.sub(r"\n\s*\n\s*$", "\n", before)
        conclusion = before + joined.get(slot, "") + conclusion[marker.end() :]
    main = sources["main.tex"]
    start, end = _abstract_span(main)
    main = main[:start] + budget.text + main[end:]
    documents = {
        "sections/results.tex": "\n\n".join(paragraphs) + "\n",
        "sections/discussion.tex": discussion,
        "sections/conclusion.tex": conclusion,
        "main.tex": main,
    }
    if "exploratory" in joined:
        filename = "sections/supplement-exploratory-x3-x7.tex"
        documents[filename] = joined["exploratory"] + "\n"
        boundary_input = r"\input{generated/exploratory-x7-boundaries}"
        x7_input = r"\input{generated/exploratory-x7}"
        if main.count(boundary_input) == 1 and x7_input in documents[filename]:
            documents[filename] = documents[filename].replace(
                x7_input, x7_input + "\n" + boundary_input
            )
            main = main.replace(boundary_input + "\n", "")
        # X3-X7 follow X1a/X2 and X5, which the fixed exploratory file ends with.
        insertion = r"\input{sections/supplement-exploratory-x1-x2}"
        if main.count(insertion) != 1:
            raise ValueError("Missing or ambiguous supplement insertion slot")
        documents["main.tex"] = main.replace(
            insertion, insertion + "\n" + rf"\input{{{filename[:-4]}}}"
        )
    if "secondary" in joined:
        documents["sections/supplement.tex"] = (
            sources["sections/supplement.tex"].rstrip()
            + "\n\n"
            + joined["secondary"]
            + "\n"
        )
    return documents, budget


def assembled_values(
    manuscript: Path,
    catalog: Mapping[str, str],
    report: AssemblyPlan,
    catalog_records: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Restrict exporter values and provenance to the assembled document tree."""
    root = _permitted(manuscript)
    seen: set[Path] = set()
    used: set[str] = set()

    def visit(name: str) -> None:
        path = _permitted(root / name)
        if not path.is_relative_to(root) or (root / name).is_symlink():
            raise ValueError("Values input must remain inside manuscript: " + name)
        if path in seen:
            return
        seen.add(path)
        source = COMMENTS.sub(r"\1", path.read_text(encoding="utf-8"))
        for match in RESULT.finditer(source):
            key, shown = match.groups()
            line = source.count("\n", 0, match.start()) + 1
            if key not in catalog:
                raise ValueError(f"{name}:{line}: Missing cited catalog ID: {key}")
            if catalog[key] != shown:
                raise ValueError(
                    f"{name}:{line}: {key} shows {shown}, expected {catalog[key]}"
                )
            used.add(key)
        for target in re.findall(r"\\(?:input|include)\s*\{([^{}]+)\}", source):
            visit(target if target.endswith(".tex") else target + ".tex")

    visit("main.tex")
    sources: dict[str, Any] = {}
    for record in catalog_records:
        provenance = record.get("sources", {})
        if isinstance(provenance, dict):
            sources.update(
                {key: value for key, value in provenance.items() if key in used}
            )
    return {
        "schema": "ic-study.v4-merged-result-values.v1",
        "synthetic": bool(report.facts and report.facts["synthetic"])
        or any(record.get("synthetic") is True for record in catalog_records),
        "values": {key: catalog[key] for key in sorted(used)},
        "sources": sources,
        "components": [
            {
                key: value
                for key, value in record.items()
                if key not in {"values", "sources"}
            }
            for record in catalog_records
        ],
        "assembly": {
            "schema": SCHEMA,
            "values_sha256": report.values_sha256,
            "rules_sha256": report.rules_sha256,
            "facts_sha256": facts_sha256(report.facts) if report.facts else None,
            "assembler_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
    }


def assemble(
    confirmatory: Mapping[str, str],
    exploratory: Mapping[str, str],
    *,
    manuscript: Path,
    output: Path,
    facts: Mapping[str, Any] | None = None,
    values_output: Path | None = None,
    catalog_records: Sequence[Mapping[str, Any]] = (),
) -> AssemblyPlan:
    report = plan(confirmatory, exploratory, manuscript=manuscript, facts=facts)
    if report.refused:
        raise AssemblyRefusedError(report)
    root, destination = _permitted(manuscript), _permitted(output)
    values_path = _permitted(values_output) if values_output else None
    if values_path and (
        values_path.exists()
        or values_path.is_relative_to(root)
        or values_path == destination / "assembly-record.json"
        or values_path == destination
    ):
        raise ValueError("Values must be a new file outside source and assembly record")
    if (
        destination.exists()
        or destination.is_relative_to(root)
        or root.is_relative_to(destination)
    ):
        raise ValueError("Output must be a new copy outside the source manuscript")
    sources = {
        name: _permitted(root / name).read_text(encoding="utf-8")
        for name in (
            "main.tex",
            "sections/discussion.tex",
            "sections/conclusion.tex",
            "sections/supplement.tex",
        )
    }
    documents, budget = compose_documents(report, sources)

    def inspect(directory: str, names: list[str]) -> list[str]:
        for name in names:
            path = _permitted(Path(directory) / name)
            if not path.is_relative_to(root) or (Path(directory) / name).is_symlink():
                raise ValueError("Manuscript copy cannot follow symlinks")
        return []

    destination.mkdir(parents=True)
    created_values = False
    try:
        shutil.copytree(root, destination, ignore=inspect, dirs_exist_ok=True)
        for name, text in documents.items():
            (destination / name).write_text(text, encoding="utf-8")
        errors = document_errors(destination, documents)
        if errors:
            raise ValueError(
                "Assembly inadmissible: "
                + "; ".join(f"{name}:{line}: {reason}" for name, line, reason in errors)
            )
        receipt = report.as_dict() | {
            "abstract_words": budget.words,
            "abstract_first_fit": [asdict(step) for step in budget.steps],
            "outputs": {
                name: hashlib.sha256(text.encode()).hexdigest()
                for name, text in sorted(documents.items())
            },
        }
        values_raw = None
        if values_path:
            if values_path.exists():
                raise ValueError("Values path collides with a copied manuscript file")
            values_record = assembled_values(
                destination, _merged(confirmatory, exploratory), report, catalog_records
            )
            values_raw = (
                json.dumps(values_record, indent=2, sort_keys=True, ensure_ascii=False)
                + "\n"
            )
            receipt["values_output"] = {
                "file": str(values_path),
                "sha256": hashlib.sha256(values_raw.encode()).hexdigest(),
                "ids": len(values_record["values"]),
            }
        (destination / "assembly-record.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if values_path and values_raw:
            values_path.parent.mkdir(parents=True, exist_ok=True)
            with values_path.open("x", encoding="utf-8") as handle:
                created_values = True
                handle.write(values_raw)
    except Exception:
        if created_values and values_path:
            values_path.unlink()
        if destination.exists():
            shutil.rmtree(destination)
        raise
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirmatory-values", type=Path, required=True)
    parser.add_argument("--exploratory-values", type=Path)
    parser.add_argument("--assembly-facts", type=Path, required=True)
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--values", type=Path, help="Exporter-format values for cited IDs"
    )
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.audit_only and args.output is None:
        parser.error("--output is required unless --audit-only")
    if args.audit_only and args.values:
        parser.error("--values requires an assembled --output, without --audit-only")
    try:
        if args.report:
            report_path = _permitted(args.report)
            protected = {_permitted(args.confirmatory_values), RULES.resolve()}
            protected.add(_permitted(args.assembly_facts))
            if args.exploratory_values:
                protected.add(_permitted(args.exploratory_values))
            if (
                report_path.exists()
                or report_path in protected
                or report_path.is_relative_to(_permitted(args.manuscript))
                or (args.output and report_path.is_relative_to(_permitted(args.output)))
            ):
                raise ValueError(
                    "Report must be a new file outside the source manuscript "
                    "and catalogs"
                )
        if (
            args.values
            and args.report
            and _permitted(args.values) == _permitted(args.report)
        ):
            raise ValueError("Values and report must use different new files")
        records = [load_catalog_record(args.confirmatory_values)]
        if args.exploratory_values:
            records.append(load_catalog_record(args.exploratory_values))
        a = _values(records[0]["values"])
        x = _values(records[1]["values"]) if len(records) > 1 else {}
        facts = load_facts(args.assembly_facts)
        if args.audit_only:
            report = plan(a, x, manuscript=args.manuscript, facts=facts)
        else:
            try:
                report = assemble(
                    a,
                    x,
                    manuscript=args.manuscript,
                    output=args.output,
                    facts=facts,
                    values_output=args.values,
                    catalog_records=records,
                )
            except AssemblyRefusedError as error:
                report = error.report
        payload = json.dumps(report.as_dict(), ensure_ascii=False, indent=2) + "\n"
        if args.report:
            _permitted(args.report).write_text(payload, encoding="utf-8")
        print(payload, end="")
        return 2 if report.refused else 0
    except (OSError, ValueError) as error:
        print(json.dumps({"schema": SCHEMA, "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
