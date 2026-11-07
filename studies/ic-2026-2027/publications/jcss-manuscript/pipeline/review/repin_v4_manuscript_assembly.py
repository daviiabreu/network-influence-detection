"""Remap reviewed shell locators; visible edits require explicit rule-ID acceptance."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Mapping, Sequence
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from ic_study.analysis.v4_manuscript_assembly import (
    COMMENTS,
    RESULT,
    RULES,
    _permitted,
    _visible,
)
from ic_study.analysis.v4_manuscript_assembly_facts import unique_object

STUDY = Path(__file__).resolve().parents[4]
MANUSCRIPT = STUDY / "publications/jcss-manuscript"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encoded(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode()


def rules_bytes(obj: Mapping[str, Any]) -> bytes:
    header = json.dumps({k: v for k, v in obj.items() if k != "rules"}, indent=2)
    rows = ",\n".join(
        "    " + json.dumps(row, ensure_ascii=False) for row in obj["rules"]
    )
    return (header[:-2] + ',\n  "rules": [\n' + rows + "\n  ]\n}\n").encode()


class LineMap:
    def __init__(self, before: str, after: str):
        self.before = before.splitlines()
        self.after = after.splitlines()
        opcodes = SequenceMatcher(
            None, self.before, self.after, autojunk=False
        ).get_opcodes()
        self.opcodes: list[tuple[str, int, int, int, int]] = []
        for tag, a, b, c, d in opcodes:

            def identity(line: str) -> tuple[tuple[tuple[str, str], ...], str]:
                comment = COMMENTS.search(line)
                return tuple(RESULT.findall(line)), comment[0] if comment else ""

            anchors = [identity(line) for line in self.before[a:b]]
            if (
                tag == "replace"
                and b - a == d - c
                and all(bindings or markers for bindings, markers in anchors)
                and anchors == [identity(line) for line in self.after[c:d]]
            ):
                self.opcodes.extend(
                    (tag, i, i + 1, j, j + 1)
                    for i, j in zip(range(a, b), range(c, d), strict=True)
                )
            else:
                self.opcodes.append((tag, a, b, c, d))

    def span(self, start: int, end: int) -> tuple[int, int]:
        if not 1 <= start <= end <= len(self.before):
            raise ValueError(f"Invalid old locator: {start}-{end}")
        lo, hi = start - 1, end
        mapped: list[int] = []
        for tag, a, b, c, d in self.opcodes:
            if tag == "equal" and max(lo, a) < min(hi, b):
                mapped.extend(range(c + max(lo, a) - a, c + min(hi, b) - a))
            elif tag == "insert" and lo < a < hi:
                mapped.extend(range(c, d))
            elif tag == "replace" and max(lo, a) < min(hi, b):
                # A hunk straddling a locator cannot be split by guesswork.
                if a < lo or b > hi:
                    raise ValueError(f"Ambiguous replacement: {start}-{end}")
                mapped.extend(range(c, d))
        if not mapped:
            raise ValueError(f"Removed fragment: {start}-{end}")
        return min(mapped) + 1, max(mapped) + 1

    def text(self, start: int, end: int, *, old: bool = False) -> str:
        return "\n".join((self.before if old else self.after)[start - 1 : end])


def remap_locators(obj: Any, mapping: LineMap) -> None:
    if isinstance(obj, dict):
        if "line" in obj:
            end_line = obj["end_line"] if "end_line" in obj else obj["line"]
            start, end = mapping.span(obj["line"], end_line)
            obj["line"] = start
            if "end_line" in obj:
                obj["end_line"] = end
            elif start != end:
                raise ValueError(
                    "Single-line clause became multiline; review its action"
                )
        for key, value in obj.items():
            if key != "scope_locator":
                remap_locators(value, mapping)
    elif isinstance(obj, list):
        for value in obj:
            remap_locators(value, mapping)


def repin_registry(
    registry: Mapping[str, Any],
    old_sources: Mapping[str, bytes],
    new_sources: Mapping[str, bytes],
    accepted: set[str],
    locator_overrides: Mapping[str, tuple[int, int]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    result = copy.deepcopy(dict(registry))
    ids = {row["id"] for row in result["rules"]}
    if accepted - ids:
        raise ValueError("Unknown acceptance IDs: " + ", ".join(sorted(accepted - ids)))
    overrides = dict(locator_overrides or {})
    if overrides.keys() - accepted:
        raise ValueError("Locator override needs explicit ID acceptance")
    mappings = {}
    sources = {}
    for name, source in result["sources"].items():
        old, new = old_sources[name], new_sources[name]
        if sha(old) != source["sha256"]:
            raise ValueError("Old shell does not match pinned digest: " + name)
        mappings[name] = LineMap(old.decode(), new.decode())
        source["sha256"] = sha(new)
        sources[name] = {"path": source["path"], "before": sha(old), "after": sha(new)}
    records, needs_acceptance = [], []
    for row in result["rules"]:
        original = copy.deepcopy(row)
        mapping = mappings[row["source"]]
        try:
            remap_locators(row, mapping)
            if "scope_locator" in row:
                remap_locators(
                    row["scope_locator"], mappings[row["scope_locator"]["source"]]
                )
        except ValueError as exc:
            raise ValueError(row["id"] + ": " + str(exc)) from exc
        candidate_locator = [row["line"], row["end_line"]]
        if row["id"] in overrides:
            start, end = overrides[row["id"]]
            if not row["line"] <= start <= end <= row["end_line"]:
                raise ValueError("Override outside diff candidate: " + row["id"])
            if row.get("fragments"):
                raise ValueError("Override of a fragmented rule needs manual review")
            row["line"], row["end_line"] = start, end
        before = mapping.text(original["line"], original["end_line"], old=True)
        after = mapping.text(row["line"], row["end_line"])
        visible_changed = " ".join(_visible(before).split()) != " ".join(
            _visible(after).split()
        )
        if _visible(before) and not _visible(after):
            raise ValueError("Removed fragment: " + row["id"])
        kind = (
            "visible-text"
            if visible_changed
            else "comment-only"
            if before != after
            else "displacement"
            if original != row
            else "unchanged"
        )
        if visible_changed and row["id"] not in accepted:
            needs_acceptance.append(row["id"])
        records.append(
            {
                "id": row["id"],
                "source": row["source"],
                "kind": kind,
                "old_locator": [original["line"], original["end_line"]],
                "new_locator": [row["line"], row["end_line"]],
                "diff_candidate_locator": candidate_locator,
                "before_sha256": sha(before.encode()),
                "after_sha256": sha(after.encode()),
                "before_visible": _visible(before) if visible_changed else None,
                "after_visible": _visible(after) if visible_changed else None,
                "explicit_acceptance": row["id"] in accepted,
                "condition_unchanged": original["condition"] == row["condition"],
                "action_unchanged": original["operation"] == row["operation"],
            }
        )
    if needs_acceptance:
        raise ValueError(
            "Visible edits require --accept-visible: " + ", ".join(needs_acceptance)
        )
    return result, {
        "schema": "ic-study.v4-manuscript-assembly-repin.v1",
        "sources": sources,
        "rules": records,
        "before_rules_sha256": sha(rules_bytes(registry)),
        "after_rules_sha256": sha(rules_bytes(result)),
        "accepted_visible_ids": sorted(accepted),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", type=Path, default=RULES)
    parser.add_argument("--manuscript", type=Path, default=MANUSCRIPT)
    parser.add_argument("--old-shell", action="append", default=[], metavar="NAME=REV")
    parser.add_argument("--accept-visible", action="append", default=[], metavar="ID")
    parser.add_argument(
        "--locator", action="append", default=[], metavar="ID=START:END"
    )
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        rules_path, receipt_path = _permitted(args.rules), _permitted(args.receipt)
        if receipt_path.exists() or receipt_path == rules_path:
            raise ValueError("Receipt must be a new file outside the rules and shells")
        registry = json.loads(rules_path.read_text(), object_pairs_hook=unique_object)
        revisions = {}
        for item in args.old_shell:
            name, sep, revision = item.partition("=")
            if not sep or name in revisions or name not in registry["sources"]:
                raise ValueError("Expected unique known shell NAME=REV")
            revisions[name] = revision
        root = _permitted(args.manuscript)
        old_sources, new_sources = {}, {}
        for name, source in registry["sources"].items():
            path = _permitted(root / source["path"])
            if not path.is_relative_to(root) or receipt_path == path:
                raise ValueError(
                    "Shell outside manuscript or receipt collides with shell"
                )
            new_sources[name] = path.read_bytes()
            if name in revisions:
                revision = subprocess.run(
                    ["git", "rev-parse", "--verify", revisions[name] + "^{commit}"],
                    cwd=STUDY,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                revisions[name] = revision
                relative = path.relative_to(STUDY.parent.parent).as_posix()
                old_sources[name] = subprocess.run(
                    ["git", "show", revision + ":" + relative],
                    cwd=STUDY,
                    check=True,
                    capture_output=True,
                ).stdout
            else:
                old_sources[name] = new_sources[name]
        overrides = {}
        for item in args.locator:
            name, sep, span = item.partition("=")
            bounds = span.split(":")
            if not sep or len(bounds) != 2 or name in overrides:
                raise ValueError("Expected unique locator ID=START:END")
            overrides[name] = (int(bounds[0]), int(bounds[1]))
        result, receipt = repin_registry(
            registry, old_sources, new_sources, set(args.accept_visible), overrides
        )
        receipt["old_revisions"] = revisions
        receipt["script_sha256"] = sha(Path(__file__).read_bytes())
        receipt["before_rules_sha256"] = sha(rules_path.read_bytes())
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        # Validate everything before either persisted artifact is written.
        receipt_path.write_bytes(encoded(receipt))
        rules_path.write_bytes(rules_bytes(result))
        print(json.dumps({"receipt": str(receipt_path), "rules": len(result["rules"])}))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
