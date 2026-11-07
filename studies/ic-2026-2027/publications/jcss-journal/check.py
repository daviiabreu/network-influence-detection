#!/usr/bin/env python3
"""Mechanical checks for the JCSS article (main.tex) and Online Resource 1 (esm.tex)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VALUE_FILES = (
    "values/result-values-final.json",
    "values/journal-values.json",
    "values/journal-transcribed.json",
)
BODY = (
    "introduction",
    "background",
    "methods",
    "ai-use",
    "results",
    "discussion",
    "conclusion",
)
STRICT = re.compile(
    r"^(sections/(results|table-exploratory|front-matter)\.tex|generated/journal-.*\.tex)$"
)
RESULT_MACRO = re.compile(r"\\resultnum\{([^{}]+)\}\{([^{}]*)\}")
PLURAL_MACRO = re.compile(r"\\resultplural\{([^{}]+)\}\{([^{}]*)\}\{([^{}]*)\}")
INPUT = re.compile(r"\\input\{([^{}]+)\}")
CITE = re.compile(r"\\cite\w*\s*(?:\[[^]]*\]\s*)?\{([^{}]+)\}")
NUMBER = re.compile(
    r"(?<![A-Za-z0-9.])[-+]?(?:\d+\.\d+|\d{1,3}(?:,\d{3})+|\d+)(?![A-Za-z0-9])"
)
PLACEHOLDER = re.compile(
    r"\\placeholder\s*\{"
    r"|\[\s*(?:to\s+be\s+filled\b|OWNER\s*:|Insert\b|Generated values pending"
    r"|AT SUBMISSION)[^]]*\]"
    r"|(?<!j\.)\b(?:TODO|FIXME|TBD)\b",
    re.IGNORECASE,
)
DESIGN_CONSTANTS = {
    *("0", "0.001", "0.003", "0.01", "0.03", "0.1", "0.10", "0.3", "0.30"),
    *("0.6", "0.60", "0.9", "0.90", "0.5", "0.70", "0.80", "1"),
    *(f"0.{n}" for n in (50, 55, 60, 65, 70, 75, 80, 85, 90)),
    *(str(n) for n in range(13)),
    *("24", "81", "414", "1,024", "2,000", "4,096", "10,626", "2.7729", "0.85"),
}
MAIN_FORBIDDEN = {
    "Portuguese label": r"\b(?:válid|inválid|parcial|disponível|não\b|Registro|completo"
    r"|encerramento|iniciado)\w*",
    "partner wording": r"\bpartners?\b",
    "gate code": r"\bG(?:0|1[abc]?|2c?)\b",
    "exploratory code": r"\bX[1-7][ab]?\b",
    "tier": r"\b[Tt]iers?\b",
    "version code": r"\bv[1-5](?:\.\d+)?\b",
    "decision code": r"\b(?:D[1-9]|Q\d{1,2}|DS\d{2})\b",
    "preregistration wording": r"\b[Pp]reregist\w*",
}
BRITISH_STEMS = (
    "organis|recognis|optimis|normalis|standardis|parametris|summaris|characteris"
    "|emphasis|minimis|maximis|generalis|randomis|stabilis|utilis"
)
BRITISH = (
    r"\b(?:centre[sd]?|centring|modell\w*|labell\w*|favour\w*|programmes?|behaviour\w*"
    r"|analys(?:e|ed|ing)\b|colour\w*|travell\w*|artefact\w*|catalogue\w*"
    rf"|(?:{BRITISH_STEMS})(?:e|ed|es|ing|ation|ations)\b)"
)


def visible(source: str) -> str:
    return re.sub(r"(?m)(?<!\\)((?:\\\\)*)%[^\n]*", r"\1", source)


def tex_tree(document: str, missing: list[str]) -> dict[str, str]:
    found: dict[str, str] = {}

    def visit(relative: str) -> None:
        name = relative if relative.endswith(".tex") else relative + ".tex"
        if name in found:
            return
        path = ROOT / name
        if not path.is_file():
            missing.append(f"{document}: input {name} does not exist")
            return
        source = path.read_text()
        found[name] = source
        for child in INPUT.findall(visible(source)):
            visit(child)

    visit(document)
    return found


def load_values() -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    errors: list[str] = []
    for relative in VALUE_FILES:
        path = ROOT / relative
        if not path.is_file():
            continue
        payload = json.loads(path.read_text())["values"]
        for key, value in payload.items():
            if key in values and values[key] != str(value):
                errors.append(f"{relative}: {key} conflicts with an earlier value")
            values[key] = str(value)
    return values, errors


def bindings(
    tree: dict[str, str], values: dict[str, str], submission: bool
) -> tuple[list[str], list[str], set[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    used: set[str] = set()
    for name, source in tree.items():
        text = visible(source)
        for match in RESULT_MACRO.finditer(text):
            key, shown = match.groups()
            used.add(key)
            line = text.count("\n", 0, match.start()) + 1
            if key.startswith("j.TODO."):
                (errors if submission else warnings).append(
                    f"{name}:{line}: unresolved journal key {key}"
                )
            elif key not in values:
                errors.append(f"{name}:{line}: missing result value {key}")
            elif values[key] != shown:
                errors.append(
                    f"{name}:{line}: {key} shows {shown}, expected {values[key]}"
                )
    return errors, warnings, used


def unbound_numbers(name: str, source: str) -> list[str]:
    text = visible(source)
    text = RESULT_MACRO.sub(" ", text)
    text = PLURAL_MACRO.sub(" ", text)
    text = re.sub(
        r"\\(?:label|ref|eqref|cite\w*|input|begin|end|includegraphics|hyperref"
        r"|url|code|texttt)\s*(?:\[[^]]*\])?\s*\{[^{}]*\}",
        " ",
        text,
    )
    text = re.sub(r"\\begin\{(?:tabular|tabularx)\}\{[^{}]*\}", " ", text)
    text = re.sub(r"[-+]?\d*\.?\d+\s*\\(?:line|text|column)width\b", " ", text)
    text = re.sub(r"[-+]?\d*\.?\d+\s*(?:pt|cm|mm|in|em|ex)\b", " ", text)
    text = re.sub(r"\\\\\[[^]]*\]", " ", text)
    found = []
    for match in NUMBER.finditer(text):
        number = match.group().lstrip("+-")
        if number in DESIGN_CONSTANTS:
            continue
        line = text.count("\n", 0, match.start()) + 1
        found.append(f"{name}:{line}: unbound number {match.group()}")
    return found


def terms(name: str, source: str, patterns: dict[str, str]) -> list[str]:
    text = RESULT_MACRO.sub(r"\2", visible(source))
    text = PLURAL_MACRO.sub(r"\2 \3", text)
    text = re.sub(r"\\(?:cite\w*|label|ref|url|input)\s*\{[^{}]*\}", " ", text)
    text = re.sub(r"actor\s*(?:--|\u2013|-)\s*partner", "actor-dyad", text)
    found = []
    for label, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            line = text.count("\n", 0, match.start()) + 1
            found.append(f"{name}:{line}: {label}: {match.group()}")
    return found


def words(source: str) -> int:
    text = visible(source)
    text = re.sub(
        r"\\begin\{(table\*?|figure\*?)\}.*?\\end\{\1\}", " ", text, flags=re.DOTALL
    )
    text = RESULT_MACRO.sub(r"\2", text)
    text = re.sub(r"\\(?:cite\w*|label|ref|eqref|input)\s*\{[^{}]*\}", " ", text)
    text = re.sub(r"\$[^$]*\$", " x ", text)
    text = re.sub(r"\\[A-Za-z]+\*?", " ", text)
    text = re.sub(r"[{}\[\]~]", " ", text)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\u2019.,:;()\u2013-]*", text))


def balanced_argument(source: str, command: str) -> str | None:
    match = re.search(r"\\" + command + r"\s*\{", source)
    if not match:
        return None
    depth = 1
    for index in range(match.end(), len(source)):
        if source[index] == "{" and source[index - 1] != "\\":
            depth += 1
        elif source[index] == "}" and source[index - 1] != "\\":
            depth -= 1
            if depth == 0:
                return source[match.end() : index]
    return None


def citations(trees: list[dict[str, str]]) -> list[str]:
    keys: set[str] = set()
    for tree in trees:
        for source in tree.values():
            for group in CITE.findall(visible(source)):
                keys.update(key.strip() for key in group.split(","))
    bib = (ROOT / "references.bib").read_text()
    defined = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib)
    errors = [
        f"duplicate BibTeX key {key}"
        for key in sorted(set(defined))
        if defined.count(key) > 1
    ]
    errors += [f"unresolved citation key {key}" for key in sorted(keys - set(defined))]
    return errors


def log_problems(build: Path, document: str) -> list[str]:
    log = build / f"{document}.log"
    if not log.is_file():
        return [f"{document}.log missing in {build}"]
    text = log.read_text(errors="replace")
    problems = sorted(
        set(
            re.findall(r"Reference `([^']+)' on page \d+ undefined", text)
            + re.findall(r"Citation `([^']+)' on page \d+ undefined", text)
        )
    )
    found = [
        f"{document}.pdf: undefined reference or citation {item}" for item in problems
    ]
    found += [
        f"{document}.pdf: label {label} multiply defined"
        for label in sorted(set(re.findall(r"Label `([^']+)' multiply defined", text)))
    ]
    return found


def pdf_pages(pdf: Path) -> int:
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    match = re.search(r"Pages:\s+(\d+)", info.stdout)
    return int(match.group(1)) if match else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, help="build directory from build.py")
    parser.add_argument("--submission", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    main_tree = tex_tree("main.tex", warnings)
    esm_tree = tex_tree("esm.tex", warnings)
    values, conflicts = load_values()
    errors += conflicts
    used: set[str] = set()
    for tree in (main_tree, esm_tree):
        found_errors, found_warnings, keys = bindings(tree, values, args.submission)
        errors += found_errors
        warnings += found_warnings
        used |= keys
    print(f"result values: {len(used)} keys bound; {len(values)} available")

    for name, source in main_tree.items():
        numbers = unbound_numbers(name, source)
        (errors if STRICT.match(name) else warnings).extend(numbers)
        errors += terms(name, source, MAIN_FORBIDDEN)
        warnings += terms(name, source, {"British spelling": BRITISH})
    for name, source in esm_tree.items():
        errors += terms(
            name, source, {"Portuguese label": MAIN_FORBIDDEN["Portuguese label"]}
        )
        warnings += terms(name, source, {"British spelling": BRITISH})

    for tree in (main_tree, esm_tree):
        for name, source in tree.items():
            text = visible(source)
            for match in PLACEHOLDER.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                (errors if args.submission else warnings).append(
                    f"{name}:{line}: placeholder {match.group()}"
                )
    errors += citations([main_tree, esm_tree])

    front = main_tree.get("sections/front-matter.tex", "")
    abstract = balanced_argument(front, "abstract") or ""
    keywords = balanced_argument(front, "keywords") or ""
    abstract_words = words(abstract)
    keyword_count = len([k for k in keywords.split(",") if k.strip()])
    if not 150 <= abstract_words <= 250:
        errors.append(f"abstract has {abstract_words} words; JCSS requires 150-250")
    if not 4 <= keyword_count <= 6:
        errors.append(f"{keyword_count} keywords; JCSS requires 4-6")
    print(f"abstract: {abstract_words} words; keywords: {keyword_count}")
    total = 0
    for section in BODY:
        count = words(main_tree.get(f"sections/{section}.tex", ""))
        total += count
        print(f"words {section}: {count}")
    print(f"words body total: {total}")

    if args.build:
        build = args.build.resolve()
        for document in ("main", "esm"):
            errors += log_problems(build, document)
            print(f"{document}.pdf: {pdf_pages(build / f'{document}.pdf')} pages")

    for warning in warnings:
        print("WARNING: " + warning)
    for error in errors:
        print("ERROR: " + error, file=sys.stderr)
    print(
        "PASS"
        if not errors
        else f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)"
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
