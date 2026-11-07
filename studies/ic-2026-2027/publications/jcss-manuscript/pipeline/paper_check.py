#!/usr/bin/env python3
"""Mechanical checks for a compiled JCSS/JASSS manuscript."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(
    r"\\placeholder\s*\{"
    r"|\[\s*(?:to\s+be\s+filled\b|OWNER\s*:|"
    r"Insert\b|Generated values pending|data location|code release|"
    r"run and figure manifests)[^]]*\]"
    r"|\b(?:TODO|FIXME|TBD)\b",
    re.IGNORECASE,
)
RESULT_NUMBER = re.compile(
    r"(?<![A-Za-z0-9])[-+]?(?:\d+\.\d+|\d{1,3}(?:,\d{3})+|\d+)(?![A-Za-z0-9])"
)
RESULT_MACRO = re.compile(r"\\resultnum\{([^{}]+)\}\{([^{}]+)\}")
PLURAL_MACRO = re.compile(r"\\resultplural\{([^{}]+)\}\{([^{}]*)\}\{([^{}]*)\}")


def without_comments(source: str) -> str:
    return re.sub(r"(?m)(?<!\\)((?:\\\\)*)%[^\n]*", r"\1", source)


def balanced_argument(source: str, command: str) -> str | None:
    match = re.search(r"\\" + command + r"\s*\{", source)
    if not match:
        return None
    start = match.end()
    depth = 1
    for index in range(start, len(source)):
        if source[index] == "{" and source[index - 1] != "\\":
            depth += 1
        elif source[index] == "}" and source[index - 1] != "\\":
            depth -= 1
            if depth == 0:
                return source[start:index]
    return None


def tex_sources(root: Path) -> dict[Path, str]:
    found: dict[Path, str] = {}

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in found:
            return
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError(f"missing or outside manuscript: {path}")
        source = path.read_text()
        found[path] = source
        for name in re.findall(
            r"\\(?:input|include)\s*\{([^{}]+)\}", without_comments(source)
        ):
            visit(root / (name if name.endswith(".tex") else name + ".tex"))

    visit(root / "main.tex")
    return found


def without_captions(source: str) -> str:
    for match in reversed(list(re.finditer(r"\\caption\s*\{", source))):
        argument = balanced_argument(source[match.start() :], "caption")
        if argument is not None:
            end = match.end() + len(argument) + 1
            source = (
                source[: match.start()]
                + "\n" * source[match.start() : end].count("\n")
                + source[end:]
            )
    return source


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", text, re.UNICODE))


def abstract_word_count(abstract: str) -> int:
    visible = PLURAL_MACRO.sub(lambda match: match[3], abstract)
    visible = RESULT_MACRO.sub(lambda match: match[2], visible)
    return word_count(re.sub(r"\\[A-Za-z]+", "", visible))


def pdf_metrics(pdf: Path) -> tuple[int, int]:
    info = subprocess.run(
        ["pdfinfo", str(pdf)], check=True, capture_output=True, text=True
    ).stdout
    match = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    if not match:
        raise ValueError("pdfinfo did not report Pages")
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return int(match.group(1)), word_count(text)


def citations(sources: dict[Path, str], root: Path) -> list[str]:
    errors: list[str] = []
    keys: set[str] = set()
    for source in sources.values():
        for group in re.findall(r"\\cite\w*\s*(?:\[[^]]*\]\s*)?\{([^{}]+)\}", source):
            keys.update(key.strip() for key in group.split(","))
    bib = (root / "references.bib").read_text()
    defined = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib)
    duplicates = sorted(key for key in set(defined) if defined.count(key) > 1)
    if duplicates:
        errors.append("duplicate BibTeX keys: " + ", ".join(duplicates))
    missing = sorted(keys - set(defined))
    if missing:
        errors.append("unresolved citation keys: " + ", ".join(missing))
    print(f"citations: {len(keys)} used keys; {len(defined)} bibliography entries")
    return errors


def result_consistency(
    root: Path, sources: dict[Path, str], values_path: Path | None, submission: bool
) -> list[str]:
    errors: list[str] = []
    result_files = [
        path
        for path in sources
        if path.parent.name == "generated" or path.name == "results.tex"
    ]
    if values_path is None:
        return ["result values JSON is required for submission"] if submission else []
    try:
        payload = json.loads(values_path.read_text())
        values = payload["values"]
        if not isinstance(values, dict):
            raise ValueError("values must be an object")
    except (OSError, ValueError, KeyError) as exc:
        return [f"invalid result values JSON: {exc}"]
    used: set[str] = set()
    for path, source in sources.items():
        for match in RESULT_MACRO.finditer(source):
            key, shown = match.groups()
            used.add(key)
            if key not in values:
                errors.append(f"{path.relative_to(root)}: missing result value {key}")
            elif str(values[key]) != shown:
                location = path.relative_to(root)
                errors.append(
                    f"{location}: {key} shows {shown}, expected {values[key]}"
                )
    for path in result_files:
        source = re.sub(r"(?m)^\s*%.*$", "", sources[path])
        unbound = without_captions(RESULT_MACRO.sub("", source))
        unbound = re.sub(
            r"\\(?:label|ref|input|caption|begin|end|subsection|texttt)\s*\{[^{}]*\}",
            "",
            unbound,
        )
        unbound = re.sub(r"\d*\.?\d+\s*\\(?:line|text|column)width\b", "", unbound)
        unbound = re.sub(r"\d*\.?\d+\s*(?:pt|cm|mm|in|em|ex)\b", "", unbound)
        for match in RESULT_NUMBER.finditer(unbound):
            line = unbound.count("\n", 0, match.start()) + 1
            location = path.relative_to(root)
            errors.append(f"{location}:{line}: unbound result number {match.group()}")
    if submission and not used:
        errors.append("no result numbers bound to a generated results JSON")
    for key in sorted(set(values) - used):
        errors.append(f"unused result value: {key}")
    print(f"result values: {len(used)} bound IDs across manuscript")
    print(f"result files scanned for unbound numbers: {len(result_files)}")
    return errors


def check(
    venue: str, pdf: Path, root: Path, values: Path | None, submission: bool
) -> list[str]:
    sources = tex_sources(root)
    main = sources[(root / "main.tex").resolve()]
    pages, words = pdf_metrics(pdf)
    abstract = balanced_argument(main, "abstract")
    keywords = balanced_argument(main, "keywords")
    abstract_words = abstract_word_count(abstract or "")
    keyword_count = len(keywords.split(",")) if keywords else 0
    print(f"venue: {venue}; PDF: {pages} pages, {words} extracted words")
    print(f"abstract: {abstract_words} words; keywords: {keyword_count}")
    errors: list[str] = []
    if venue == "jcss":
        if not 150 <= abstract_words <= 250:
            errors.append("JCSS abstract must have 150-250 words")
        if not 4 <= keyword_count <= 6:
            errors.append("JCSS requires 4-6 keywords")
    else:
        if not 200 <= abstract_words <= 300:
            errors.append(
                "JASSS detailed instructions specify 200-300 abstract words; "
                "verify the conflicting short instruction"
            )
        if not 3 <= keyword_count <= 6:
            errors.append(
                "JASSS detailed instructions specify 3-6 keywords; "
                "verify the conflicting short instruction"
            )
        if not 5000 <= words <= 8000:
            print(
                "advisory: JASSS says research articles are typically 5,000-8,000 words"
            )
    combined = "\n".join(sources.values())
    for label, pattern in {
        "data and code availability statement": r"Data and code availability",
        "generative AI disclosure in Methods": r"\\subsection\{Use of generative AI\}",
        "other declarations": r"Other declarations",
    }.items():
        if not re.search(pattern, combined, re.IGNORECASE):
            errors.append("missing " + label)
    errors.extend(citations(sources, root))
    placeholders: list[str] = []
    for path, source in sources.items():
        visible = without_comments(source)
        lines = sorted(
            {
                visible.count("\n", 0, match.start()) + 1
                for match in PLACEHOLDER.finditer(visible)
            }
        )
        placeholders.extend(
            f"{path.relative_to(root)}:{number}: unresolved placeholder"
            for number in lines
        )
    print(f"placeholders: {len(placeholders)}")
    if submission:
        errors.extend(placeholders)
    errors.extend(result_consistency(root, sources, values, submission))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--venue", choices=("jcss", "jasss"), default="jcss")
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--result-values",
        type=Path,
        help="JSON object with a values map generated from validated results",
    )
    parser.add_argument(
        "--submission",
        action="store_true",
        help="fail on placeholders and absent result bindings",
    )
    args = parser.parse_args()
    try:
        errors = check(
            args.venue,
            args.pdf,
            args.root.resolve(),
            args.result_values,
            args.submission,
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        errors = [str(exc)]
    for error in errors:
        print("ERROR: " + error, file=sys.stderr)
    print("PASS" if not errors else f"FAIL: {len(errors)} issue(s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
