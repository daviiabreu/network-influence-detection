"""Assemble a private, hash-inventoried JCSS source package without uploading.

From the study directory::

    uv run --locked python experiments/package_jcss_submission.py \
        --out /private/tmp/jcss-source-package \
        --template ~/.local/state/research-workbench/springer-template \
        --pdf /private/tmp/compiled-manuscript/main.pdf

Only reachable TeX sources, their bibliography/graphics, generated vector
figures, T1s CSVs and local TeX dependencies are copied. Missing final assets
and draft markers remain explicit in the manifest; assembly is not release
validation. Synthetic review samples are not substituted for missing results.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import TypedDict

STUDY = Path(__file__).resolve().parents[1]
MANUSCRIPT = STUDY / "publications/jcss-manuscript"
TEMPLATE_FILES = ("sn-jnl.cls", "sn-mathphys-num.bst")
VECTOR_SUFFIXES = {".pdf", ".eps"}
GRAPHIC_SUFFIXES = (".pdf", ".png", ".eps", ".jpg", ".jpeg")
DRAFT_MARKER = re.compile(
    r"\\placeholder\s*\{|\[(?:Insert|Generated values pending|to be filled|OWNER)"
    r"[^]]*\]|\b(?:TODO|FIXME|TBD)\b",
    re.IGNORECASE,
)


class DraftMarker(TypedDict):
    file: str
    line: int
    marker: str


def bibliography_style(content: bytes) -> bytes:
    """Keep journal/book title macros in fallback references; no space after DOIs."""
    start = content.find(b"FUNCTION {make.tag}")
    if start < 0:
        raise ValueError("unsupported Springer style: make.tag not found")
    end = content.find(b"FUNCTION", start + len(b"FUNCTION {make.tag}"))
    if end < 0:
        raise ValueError("unsupported Springer style: make.tag boundary not found")
    block = content[start:end]
    original = b"bother #0 ="
    adjusted = b'bother #0 = t "jtitle" = not and t "btitle" = not and'
    if adjusted not in block:
        if block.count(original) != 1:
            raise ValueError("unsupported Springer style: fallback condition changed")
        content = content[:start] + block.replace(original, adjusted) + content[end:]
    doi_original = b'"\\doiurl{" process.doi * "} " *'
    doi_adjusted = b'"\\doiurl{" process.doi * "}" *'
    if doi_adjusted in content:
        return content
    if content.count(doi_original) != 1:
        raise ValueError("unsupported Springer style: DOI format changed")
    return content.replace(doi_original, doi_adjusted)


def _permitted(path: Path) -> None:
    if any(
        part == "restricted"
        or part.startswith("sealed-")
        or part in {"v4-tier-logs", "v4-gate-logs", "v4-release"}
        for part in path.parts
    ):
        raise ValueError(f"restricted input path: {path}")


def _source(root: Path, name: str) -> Path:
    if any(
        part in {"pipeline", "drafts", "scratch", "logs", "data", "datasets"}
        for part in Path(name).parts
    ):
        raise ValueError(f"internal manuscript input: {name}")
    candidate = root / name
    _permitted(candidate)
    if ".." in Path(name).parts:
        raise ValueError(f"parent traversal in manuscript input: {name}")
    path = candidate.resolve()
    _permitted(path)
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"missing or outside manuscript: {name}")
    if any(
        parent.is_symlink()
        for parent in (candidate, *candidate.parents)
        if parent.is_relative_to(root)
    ):
        raise ValueError(f"source symlinks are unsupported: {name}")
    return path


def sources(root: Path) -> tuple[set[Path], list[DraftMarker]]:
    files: set[Path] = set()
    markers: list[DraftMarker] = []
    queue = ["main.tex"]
    while queue:
        path = _source(root, queue.pop())
        if path in files:
            continue
        files.add(path)
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?m)(?<!\\)%.*$", "", text)
        for match in DRAFT_MARKER.finditer(text):
            markers.append(
                {
                    "file": path.relative_to(root).as_posix(),
                    "line": text.count("\n", 0, match.start()) + 1,
                    "marker": match.group(),
                }
            )
        for name in re.findall(r"\\(?:input|include)\s*\{([^{}]+)\}", text):
            queue.append(name if name.endswith(".tex") else name + ".tex")
        for group in re.findall(r"\\bibliography\s*\{([^{}]+)\}", text):
            for name in group.split(","):
                files.add(_source(root, name.strip() + ".bib"))
        for name in re.findall(
            r"\\includegraphics\s*(?:\[[^]]*\]\s*)?\{([^{}]+)\}", text
        ):
            if Path(name).suffix:
                files.add(_source(root, name))
            else:
                for suffix in GRAPHIC_SUFFIXES:
                    if (root / (name + suffix)).is_file():
                        files.add(_source(root, name + suffix))
                        break
                else:
                    raise ValueError(f"missing graphic: {name}")
    return files, sorted(markers, key=lambda row: (row["file"], row["line"]))


def assemble(
    manuscript: Path,
    template: Path,
    out: Path,
    pdf: Path | None = None,
    *,
    synthetic: bool = False,
) -> Path:
    _permitted(manuscript)
    root = manuscript.resolve()
    _permitted(root)
    _permitted(out)
    destination = out.resolve()
    _permitted(destination)
    if destination.is_relative_to(root):
        raise ValueError("output must be outside the manuscript")
    if any(
        (parent / ".git").exists() for parent in (destination, *destination.parents)
    ):
        raise ValueError("output must be outside every Git working tree")
    if destination.exists():
        raise ValueError("output already exists; choose a new private directory")
    files, markers = sources(root)
    generated = root / "generated"
    if generated.is_dir():
        for path in generated.iterdir():
            if path.suffix in VECTOR_SUFFIXES or (
                path.name.startswith("T1s") and path.suffix == ".csv"
            ):
                if "synthetic" in path.name.lower() and not synthetic:
                    raise ValueError("synthetic generated assets are review-only")
                files.add(_source(root, path.relative_to(root).as_posix()))
    for path in root.iterdir():
        if path.suffix in {".sty", ".bst", ".cls"}:
            files.add(_source(root, path.name))
    plan = {path.relative_to(root).as_posix(): path for path in files}
    if any("synthetic" in name.lower() for name in plan) and not synthetic:
        raise ValueError("synthetic generated assets are review-only")
    for name in TEMPLATE_FILES:
        if name not in plan:
            _permitted(template / name)
            path = (template / name).resolve()
            _permitted(path)
            if not path.is_file():
                raise ValueError(f"missing template dependency: {name}")
            plan[name] = path
    if pdf is not None:
        _permitted(pdf)
        path = pdf.resolve()
        _permitted(path)
        if path.suffix != ".pdf" or not path.is_file():
            raise ValueError("compiled PDF must be an existing .pdf file")
        plan["main.pdf"] = path
    inventory: dict[str, dict[str, object]] = {}
    pending = []
    csv = "generated/T1s_a_star_all_units"
    if csv + ".csv" not in plan and not (synthetic and csv + "_synthetic.csv" in plan):
        pending.append("generated/T1s_a_star_all_units.csv absent")
    vectors = sorted(
        name
        for name in plan
        if name.startswith("generated/") and Path(name).suffix in VECTOR_SUFFIXES
    )
    if not vectors:
        pending.append("generated final vector figures absent")
    if pdf is None:
        pending.append("compiled manuscript PDF not supplied")
    bibliography_style(plan["sn-mathphys-num.bst"].read_bytes())
    destination.mkdir(mode=0o700, parents=True)
    for name, path in sorted(plan.items()):
        original = path.read_bytes()
        content = (
            bibliography_style(original)
            if name.endswith("sn-mathphys-num.bst")
            else original
        )
        target = destination / name
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(0o600)
        inventory[name] = {
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
            "origin": "manuscript" if path.is_relative_to(root) else "external",
        }
        if content != original:
            inventory[name]["original_sha256"] = hashlib.sha256(original).hexdigest()
            inventory[name]["transformation"] = (
                "retain jtitle/btitle tags in fallback references; no space after DOIs"
            )
    revision = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    manifest = {
        "schema": "ic-study.jcss-submission-source-package.v1",
        "purpose": "local staging only; no upload or scientific release approval",
        "synthetic": synthetic,
        "source_revision": revision.stdout.strip()
        if revision.returncode == 0
        else None,
        "files": inventory,
        "draft_markers": markers,
        "pending_assets": pending,
        "generated_vector_figures": vectors,
    }
    manifest_path = destination / "source-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    manifest_path.chmod(0o600)
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manuscript", type=Path, default=MANUSCRIPT)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path.home() / ".local/state/research-workbench/springer-template",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument(
        "--synthetic", action="store_true", help="Artificial inputs; local staging only"
    )
    args = parser.parse_args()
    try:
        manifest = assemble(
            args.manuscript, args.template, args.out, args.pdf, synthetic=args.synthetic
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
