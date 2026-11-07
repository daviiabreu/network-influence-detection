#!/usr/bin/env python3
"""Create and verify a self-contained local JCSS submission kit; never upload."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from toolchain import Toolchain, arguments, configured

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parents[1]
MARKER = re.compile(r"\[AT SUBMISSION\b[^]]*\]", re.DOTALL)
COMMAND = re.compile(r"\\([A-Za-z@]+)\*?")


class Rewrite(Protocol):
    def __call__(self, name: str, text: str, end: int) -> tuple[str, int] | None: ...


sys.path.insert(0, str(STUDY / "experiments"))
from package_jcss_submission import bibliography_style  # noqa: E402


@dataclass
class Counts:
    comments: int = 0
    esm_refs: int = 0
    inputs: int = 0
    resultnums: int = 0
    resultplurals: int = 0


def escaped(text: str, index: int) -> bool:
    start = index
    while start and text[start - 1] == "\\":
        start -= 1
    return (index - start) % 2 == 1


def argument(text: str, index: int, opening: str = "{") -> tuple[str, int]:
    while index < len(text) and text[index].isspace():
        index += 1
    closing = "}" if opening == "{" else "]"
    if index >= len(text) or text[index] != opening:
        raise ValueError(
            f"expected {opening} argument near {text[index : index + 60]!r}"
        )
    start, depth = index + 1, 1
    for end in range(start, len(text)):
        if escaped(text, end):
            continue
        if text[end] == opening:
            depth += 1
        elif text[end] == closing:
            depth -= 1
            if not depth:
                return text[start:end], end + 1
    raise ValueError("unclosed TeX argument")


def optional(text: str, index: int) -> tuple[str | None, int]:
    start = index
    while index < len(text) and text[index].isspace():
        index += 1
    return (
        argument(text, index, "[") if text[index : index + 1] == "[" else (None, start)
    )


def protected_end(text: str, index: int) -> int | None:
    if text[index] == "%" and not escaped(text, index):
        end = text.find("\n", index)
        return end if end >= 0 else len(text)
    environment = re.match(
        r"\\begin\{(verbatim\*?|Verbatim|lstlisting|minted)\}", text[index:]
    )
    if environment:
        closing = "\\end{" + environment[1] + "}"
        end = text.find(closing, index + environment.end())
        if end < 0:
            raise ValueError("unclosed verbatim environment")
        return end + len(closing)
    verb = re.match(r"\\verb\*?([^A-Za-z\s])", text[index:])
    if verb:
        end = text.find(verb[1], index + verb.end())
        if end < 0:
            raise ValueError("unclosed inline verbatim")
        return end + 1
    url = re.match(r"\\(?:url|burl|code|path|href)\b", text[index:])
    if url and text[index + url.end() :].lstrip().startswith("{"):
        return argument(text, index + url.end())[1]
    return None


def commands(text: str) -> Iterator[tuple[str, int, int]]:
    index = 0
    while index < len(text):
        protected = protected_end(text, index)
        if protected is not None:
            index = protected
            continue
        match = COMMAND.match(text, index)
        if match and not escaped(text, index):
            yield match[1], index, match.end()
            index = match.end()
        else:
            index += 1


def rewrite(text: str, transform: Rewrite) -> str:
    parts: list[str] = []
    consumed = 0
    for name, start, end in commands(text):
        if start < consumed:
            continue
        replacement = transform(name, text, end)
        if replacement is not None:
            value, next_index = replacement
            parts.extend((text[consumed:start], value))
            consumed = next_index
    return "".join((*parts, text[consumed:]))


def strip_comments(text: str, counts: Counts) -> str:
    parts: list[str] = []
    index = 0
    while index < len(text):
        protected = protected_end(text, index)
        if protected is not None:
            if text[index] == "%":
                prefix = text[text.rfind("\n", 0, index) + 1 : index]
                full_line = not prefix.strip()
                if full_line or (index and text[index - 1].isspace()):
                    counts.comments += 1
                    if full_line:
                        for _ in prefix:
                            parts.pop()
                        index = protected + (protected < len(text))
                    else:
                        index = protected
                    continue
            parts.append(text[index:protected])
            index = protected
        else:
            parts.append(text[index])
            index += 1
    return "".join(parts)


def source_file(root: Path, name: str) -> Path:
    candidate = root / name
    path = candidate.resolve()
    if any(
        part == "restricted" or part.startswith("sealed-") or part == "v4-tier-logs"
        for part in (*candidate.parts, *path.parts)
    ):
        raise ValueError(f"restricted source path: {name}")
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"missing or outside source folder: {name}")
    return path


def aux_labels(path: Path, command: str = "newlabel") -> dict[str, str]:
    labels: dict[str, str] = {}
    text = path.read_text()
    for name, _, end in commands(text):
        if name != command or not text[end:].lstrip().startswith("{"):
            continue
        key, end = argument(text, end)
        payload, _ = argument(text, end)
        number, _ = argument(payload, 0)
        if key in labels and labels[key] != number:
            raise ValueError(f"conflicting auxiliary label: {key}")
        labels[key] = number
    return labels


def flatten(root: Path, esm_labels: dict[str, str], counts: Counts) -> str:
    main = source_file(root, "main.tex").read_text()
    main = strip_comments(main, counts)
    for name, arity, body in (("resultnum", 2, "#2"), ("resultplural", 3, "#3")):
        pattern = re.compile(
            r"\\newcommand\s*\{\\"
            + name
            + r"\}\s*\["
            + str(arity)
            + r"\]\s*\{\s*"
            + re.escape(body)
            + r"\s*\}"
        )
        main, removed = pattern.subn("", main)
        if removed != 1:
            raise ValueError(f"unsupported {name} definition; expected {body}")

    def expand(text: str, stack: tuple[Path, ...]) -> str:
        def replace(name: str, text: str, end: int) -> tuple[str, int] | None:
            if name == "input":
                child, end = argument(text, end)
                path = source_file(
                    root, child if child.endswith(".tex") else child + ".tex"
                )
                if path in stack:
                    raise ValueError(f"input cycle: {path.name}")
                counts.inputs += 1
                return expand(
                    strip_comments(path.read_text(), counts), (*stack, path)
                ), end
            if name == "IfFileExists":
                guard, end = argument(text, end)
                yes, end = argument(text, end)
                no, end = argument(text, end)
                source_file(root, guard)
                if no.strip() or not re.fullmatch(r"\s*\\input\s*\{[^{}]+\}\s*", yes):
                    raise ValueError("unsupported input guard")
                return expand(yes, stack), end
            if name == "externaldocument":
                _, end = optional(text, end)
                _, end = argument(text, end)
                return "", end
            if name == "usepackage":
                _, options_end = optional(text, end)
                packages, end = argument(text, options_end)
                kept = [
                    item.strip()
                    for item in packages.split(",")
                    if item.strip() != "xr-hyper"
                ]
                if len(kept) != len(packages.split(",")):
                    return ("\\usepackage{" + ",".join(kept) + "}" if kept else ""), end
            if name in {"ref", "hyperref"}:
                label, after_label = argument(
                    text, end, "[" if name == "hyperref" else "{"
                )
                if label.startswith("esm-"):
                    key = label.removeprefix("esm-")
                    if key not in esm_labels:
                        raise ValueError(f"missing ESM label: {key}")
                    counts.esm_refs += 1
                    if name == "hyperref":
                        value, end = argument(text, after_label)
                        return expand(value, stack), end
                    return esm_labels[key], after_label
            if name in {"resultnum", "resultplural"}:
                _, end = argument(text, end)
                value, end = argument(text, end)
                if name == "resultplural":
                    value, end = argument(text, end)
                    counts.resultplurals += 1
                else:
                    counts.resultnums += 1
                return expand(value, stack), end
            return None

        return rewrite(text, replace)

    return expand(main, (root.resolve() / "main.tex",))


def copy_figures(text: str, root: Path, out: Path) -> str:
    destinations: dict[str, Path] = {}

    def replace(name: str, text: str, end: int) -> tuple[str, int] | None:
        if name != "includegraphics":
            return None
        options, end = optional(text, end)
        graphic, end = argument(text, end)
        candidates = (
            [graphic]
            if Path(graphic).suffix
            else [
                graphic + suffix for suffix in (".pdf", ".png", ".jpg", ".jpeg", ".eps")
            ]
        )
        path = next(
            (root / item for item in candidates if (root / item).is_file()), None
        )
        if path is None:
            raise ValueError(f"missing figure: {graphic}")
        path = source_file(root, path.relative_to(root).as_posix())
        target = "Fig2.pdf" if path.name == "J2_auc_profiles_B.pdf" else path.name
        if target in destinations and destinations[target] != path:
            raise ValueError(f"flat figure filename collision: {target}")
        if (out / target).exists() and target not in destinations:
            raise ValueError(f"figure collides with source file: {target}")
        destinations[target] = path
        shutil.copy2(path, out / target)
        prefix = "\\includegraphics" + (f"[{options}]" if options is not None else "")
        return prefix + "{" + target + "}", end

    return rewrite(text, replace)


def run(
    command: list[str], cwd: Path | None = None, toolchain: Toolchain | None = None
) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=(toolchain or Toolchain.defaults()).environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(
            f"command failed: {command[0]}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


def pdf_text(path: Path, *, raw: bool = False) -> str:
    return run(["pdftotext", *(["-raw"] if raw else []), str(path), "-"])


def whitespace(text: str) -> str:
    return " ".join(text.split())


def compile_source(
    source: Path, scratch: Path, original: Path, toolchain: Toolchain
) -> tuple[Path, str]:
    shutil.copytree(source, scratch)
    run(
        toolchain.command("main.tex"),
        scratch,
        toolchain,
    )
    log = (scratch / "main.log").read_text(errors="replace")
    if re.search(
        r"(?:reference|citation)[^\n]*undefined|undefined[^\n]*(?:reference|citation)",
        log,
        re.IGNORECASE,
    ):
        raise ValueError("compile log contains undefined references or citations")
    pdf = scratch / "main.pdf"
    actual, expected = whitespace(pdf_text(pdf)), whitespace(pdf_text(original))
    if "??" in actual:
        raise ValueError("manuscript.pdf contains ??")
    if actual != expected:
        first = next(
            (
                i
                for i in range(min(len(actual), len(expected)))
                if actual[i] != expected[i]
            ),
            min(len(actual), len(expected)),
        )
        raise ValueError(
            f"PDF text mismatch at {first}: kit {actual[first : first + 100]!r}; "
            f"build {expected[first : first + 100]!r}"
        )
    return pdf, log


def plain_tex(text: str, labels: dict[str, str], citations: dict[str, str]) -> str:
    def replace(name: str, text: str, end: int) -> tuple[str, int] | None:
        if name in {"unboldmath", "noindent"}:
            return "", end
        if name in {"esmresource", "allunitsresource"}:
            return "Online Resource " + ("1" if name == "esmresource" else "2"), end
        if name == "ref":
            key, end = argument(text, end)
            if key not in labels:
                raise ValueError(f"missing manuscript label: {key}")
            return labels[key], end
        if name == "cite":
            keys, end = argument(text, end)
            return "[" + ", ".join(
                citations[key.strip()] for key in keys.split(",")
            ) + "]", end
        if name in {
            "textbf",
            "textit",
            "emph",
            "texttt",
            "fnm",
            "sur",
            "orgname",
            "orgaddress",
            "city",
            "state",
            "country",
        }:
            value, end = argument(text, end)
            return plain_tex(value, labels, citations), end
        raise ValueError(f"unsupported portal-field command: \\{name}")

    # URL arguments must retain percent escapes and their complete visible value.
    text = re.sub(r"\\(?:url|burl|code)\{([^{}]*)\}", lambda match: match[1], text)
    text = rewrite(text, replace)
    superscripts = str.maketrans("0123456789+-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻")
    text = re.sub(
        r"\^\{([^{}]*)\}", lambda match: match[1].translate(superscripts), text
    )
    text = text.replace("\\%", "%").replace("\\_", "_").replace("\\ ", " ")
    text = text.replace("---", "\u2014").replace("--", "\u2013").replace("~", " ")
    text = text.replace("$", "").replace("{", "").replace("}", "")
    return whitespace(text)


def field_matches(field: str, pdf: str) -> bool:
    def comparable(text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        text = text.translate(str.maketrans("\u2019\u2212", "'-"))
        return "".join(text.split())

    pdf = re.sub(r"(?m)^\d+\f", "", pdf)
    pdf = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "\x00", pdf)
    letters = [
        "(?:-|\x00)" if char == "-" else re.escape(char) for char in comparable(field)
    ]
    pattern = "\x00?".join(letters)
    return re.search(pattern, comparable(pdf)) is not None


def cover_letter(root: Path) -> str:
    pieces = re.split(r"(?m)^---\s*$", (root / "cover-letter.md").read_text())
    if len(pieces) != 3:
        raise ValueError("cover letter must contain exactly two horizontal rules")
    text = pieces[1].strip()
    text = re.sub(r"\[([^]]+)\]\([^\n)]+\)", r"\1", text)
    text = re.sub(r"(?m)^#{1,6}\s+", "", text)
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"(?<!\w)[*_]([^*_\n]+)[*_](?!\w)", r"\1", text)
    return text.replace("--", "\u2013") + "\n"


def portal_fields(text: str, build: Path, pdf: Path) -> tuple[str, list[str]]:
    labels, cites = (
        aux_labels(build / "main.aux"),
        aux_labels(build / "main.aux", "bibcite"),
    )
    fields: list[tuple[str, str]] = []
    running = ""
    for name, _, end in commands(text):
        if name == "title":
            short, end = optional(text, end)
            title, _ = argument(text, end)
            fields.append(("Title", plain_tex(title, labels, cites)))
            running = plain_tex(short or title, labels, cites)
        elif name in {"abstract", "keywords", "author", "affil", "email"}:
            _, end = optional(text, end)
            value, _ = argument(text, end)
            heading = {
                "abstract": "Abstract",
                "keywords": "Keywords",
                "author": "Author",
                "affil": "Affiliation",
                "email": "Email",
            }[name]
            fields.append((heading, plain_tex(value, labels, cites)))
    declaration = re.compile(r"\\noindent\\(?:textbf|emph)\{([^{}]+)\}")
    declarations = list(declaration.finditer(text))
    required = {
        "Data and code availability.",
        "Funding.",
        "Competing interests.",
        "Ethics approval and consent.",
        "Author contributions.",
    }
    for index, match in enumerate(declarations):
        if match[1] not in required:
            continue
        end = (
            declarations[index + 1].start()
            if index + 1 < len(declarations)
            else text.index("\\phantomsection", match.end())
        )
        fields.append(
            (
                match[1].removesuffix("."),
                plain_tex(text[match.end() : end], labels, cites),
            )
        )
    if len([key for key, _ in fields if key + "." in required]) != len(required):
        raise ValueError("missing required declaration field")
    rendered = pdf_text(pdf, raw=True)
    checks: list[str] = []
    paragraphs = ["# Portal fields", ""]
    for name, value in fields:
        if not field_matches(value, rendered):
            raise ValueError(f"portal field differs from PDF: {name}: {value[:120]}")
        checks.append(f"PASS portal field against PDF: {name}")
        paragraphs.extend((f"## {name}", "", value, ""))
    if not running:
        raise ValueError("missing running title")
    if field_matches(running, rendered):
        checks.append("PASS portal field against PDF: Running title")
        note = "Verified against the PDF text."
    else:
        checks.append("SOURCE ONLY running title: not printed by the Springer class")
        note = (
            "Verified against the source title argument. "
            "The Springer class does not print it in this PDF."
        )
    paragraphs.extend(("## Running title", "", running, "", note, ""))
    return "\n".join(paragraphs), checks


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assemble(build: Path, out: Path, toolchain: Toolchain | None = None) -> Path:
    if out.exists() or out.is_symlink():
        raise ValueError(f"output already exists: {out}")
    for name in ("main.pdf", "esm.pdf", "main.aux", "esm.aux", "main.bbl"):
        if not (build / name).is_file():
            raise ValueError(f"unfinished build: missing {name}")
    toolchain = toolchain or Toolchain.defaults()
    toolchain.validate()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".jcss-kit-", dir=out.parent) as temporary:
        staging = Path(temporary) / "kit"
        source = staging / "source"
        source.mkdir(parents=True)
        counts = Counts()
        text = flatten(build, aux_labels(build / "esm.aux"), counts)
        text = copy_figures(text, build, source)
        (source / "main.tex").write_text(text)
        for origin, name in (
            (build / "references.bib", "references.bib"),
            (build / "main.bbl", "main.bbl"),
            (toolchain.template / "sn-jnl.cls", "sn-jnl.cls"),
        ):
            shutil.copy2(origin, source / name)
        (source / "sn-mathphys-num.bst").write_bytes(
            bibliography_style(
                (toolchain.template / "sn-mathphys-num.bst").read_bytes()
            )
        )
        pdf, log = compile_source(
            source, Path(temporary) / "compile", build / "main.pdf", toolchain
        )
        shutil.copy2(pdf, staging / "manuscript.pdf")
        for origin, name in (
            (build / "esm.pdf", "ESM_1.pdf"),
            (build / "generated/online-resource-2-units.csv", "ESM_2.csv"),
            (build / "generated/online-resource-2-README.txt", "ESM_2-README.txt"),
        ):
            shutil.copy2(origin, staging / name)
        letter = cover_letter(ROOT)
        (staging / "cover-letter.txt").write_text(letter)
        portal, field_checks = portal_fields(text, build, pdf)
        markers = sorted(
            {whitespace(match[0]) for match in MARKER.finditer(text + "\n" + letter)}
        )
        portal += (
            "\n## Remaining submission markers\n\n"
            + "\n".join("- " + marker for marker in markers)
            + "\n"
        )
        (staging / "portal-fields.md").write_text(portal)
        commit = run(["git", "rev-parse", "HEAD"], ROOT).strip()
        journal_commit = run(
            ["git", "log", "-1", "--format=%H", "--", "."], ROOT
        ).strip()
        status = run(["git", "status", "--porcelain", "--", "."], ROOT).strip()
        checks = [
            "PASS offline compilation from a scratch copy of source/ (no ESM aux)",
            "PASS PDF text equality after collapsing whitespace (pdftotext)",
            "PASS compile log: no undefined reference or citation",
            "PASS manuscript PDF: no ??",
            *field_checks,
            f"ESM references replaced: {counts.esm_refs}",
            f"Comments removed: {counts.comments}",
            f"Inputs flattened: {counts.inputs}",
            f"Result numbers resolved: {counts.resultnums}",
            f"Result plurals resolved: {counts.resultplurals}",
            f"Remaining submission markers: {len(markers)}",
            *("MARKER " + marker for marker in markers),
        ]
        manifest = [
            "JCSS submission kit (local staging; no submission or author approval)",
            f"Source commit: {commit}",
            f"Last journal source commit: {journal_commit}",
            f"Journal working tree has changes: {bool(status)}",
            f"Build main.pdf SHA-256: {sha256(build / 'main.pdf')}",
            f"Final compile log SHA-256: {hashlib.sha256(log.encode()).hexdigest()}",
            "",
            *checks,
            "",
            "SHA-256 inventory (all payload files; this manifest excludes itself)",
        ]
        manifest.extend(
            f"{sha256(path)}  {path.relative_to(staging).as_posix()}"
            for path in sorted(staging.rglob("*"))
            if path.is_file()
        )
        (staging / "MANIFEST.txt").write_text("\n".join(manifest) + "\n")
        out.mkdir(mode=0o700)
        for path in staging.iterdir():
            shutil.move(str(path), out / path.name)
    return out / "MANIFEST.txt"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    arguments(parser)
    args = parser.parse_args()
    try:
        manifest = assemble(args.build.resolve(), args.out.absolute(), configured(args))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(manifest.read_text())
    print(f"Kit written: {manifest.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
