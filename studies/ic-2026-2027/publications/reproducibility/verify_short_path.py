"""Render public aggregates in a new directory and compare expected hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from ic_study.analysis.detection_v4_report import (
    Inputs,
    Loaded,
    add_input_arguments,
    load_inputs,
    parse_inputs,
    render,
)
from ic_study.analysis.v4_public_aggregates import (
    NOTICE,
    canonical,
    load_public,
    read_json,
)
from ic_study.analysis.v4_report_export import (
    PLACEHOLDERS,
    export,
    fill,
    result_values,
    used_ids,
    values_record,
    verified_manifest,
)

SCHEMA = "ic-study.v4-short-path-hashes.v1"


def normalization(path: str) -> str:
    if path == "report/manifest.json":
        return "report-provenance-v1"
    if path in {"values.json", "catalog.json"}:
        return "values-provenance-v1"
    if path.startswith("paper/generated/") and path.endswith(".tex"):
        return "generated-manifest-reference-v1"
    return "none"


def comparison_bytes(path: Path, mode: str) -> bytes:
    """Remove only machine provenance; never normalize numbers or figures."""
    if mode == "none":
        return path.read_bytes()
    if mode == "generated-manifest-reference-v1":
        raw = path.read_bytes()
        pattern = (
            rb"(?m)^% manifest SHA-256 [0-9a-f]{64}\. "
            rb"Export again instead of editing this file\.$"
        )
        normalized, count = re.subn(
            pattern,
            b"% manifest SHA-256 <provenance>. "
            b"Export again instead of editing this file.",
            raw,
        )
        if count != 1:
            raise ValueError("Missing or duplicate generated manifest reference")
        return normalized
    data = read_json(path)
    if mode == "report-provenance-v1":
        del data["code"]
        del data["inputs"]
    elif mode == "values-provenance-v1":
        del data["code"]
        del data["report_manifest_sha256"]
    else:
        raise ValueError(f"Unknown normalization: {mode}")
    return canonical(data)


def hashes(root: Path) -> dict[str, dict[str, str]]:
    output = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            name = path.relative_to(root).as_posix()
            mode = normalization(name)
            output[name] = {
                "sha256": hashlib.sha256(comparison_bytes(path, mode)).hexdigest(),
                "normalization": mode,
            }
    return output


def _export_minimal(inputs: Inputs, loaded: Loaded, report: Path, out: Path) -> None:
    paper = out / "paper"
    paper.mkdir()
    lines = [rf"\input{{generated/{name}}}" for name in PLACEHOLDERS]
    lines += [rf"\resultnum{{{key}}}{{[..]}}" for key in sorted(result_values(loaded))]
    (paper / "main.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = export(inputs, report, paper)
    fill(paper, result.catalog)
    for filename, ids in (
        ("values.json", used_ids(paper)),
        ("catalog.json", result.catalog),
    ):
        (out / filename).write_text(
            json.dumps(
                values_record(result, ids), indent=2, sort_keys=True, ensure_ascii=False
            )
            + "\n",
            encoding="utf-8",
        )


def run_short_path(projection: Path, out: Path, *, dpi: int = 300) -> None:
    """Call the same report and export functions with only the public input."""
    public = load_public(projection)
    out.mkdir(parents=True, exist_ok=False)
    inputs = Inputs(None, None, public_aggregates=projection)
    report = out / "report"
    render(inputs, report, dpi=dpi)
    _export_minimal(inputs, public.loaded, report, out)


def prepare(
    inputs: Inputs,
    report: Path,
    projection: Path,
    out: Path,
    manifest: Path,
    *,
    synthetic: bool = False,
) -> Path:
    """Build a new reference from authorized inputs and an existing rendering."""
    if inputs.public_aggregates is not None:
        raise ValueError(
            "Expected hashes require authorized inputs, never public replay"
        )
    if manifest.exists() or manifest.is_symlink():
        raise ValueError("Expected manifest already exists; choose a new file")
    if manifest.parent.resolve() != projection.parent.resolve():
        raise ValueError("Expected manifest must be beside the public projection")
    if out.exists() or out.is_symlink():
        raise ValueError("Reference output already exists; choose a new directory")
    if projection.is_symlink() or not projection.is_file():
        raise ValueError("Projection must be a regular file")
    if (report / "manifest.json").is_symlink():
        raise ValueError("Report manifest must be a regular file")
    loaded = load_inputs(inputs, synthetic=synthetic)
    metadata = verified_manifest(report, inputs, loaded)
    if metadata["synthetic"] is not synthetic:
        raise ValueError("Synthetic mode differs from the authorized report")
    public = load_public(projection)
    if public.synthetic is not synthetic:
        raise ValueError("Synthetic mode differs from the public projection")
    dpi = metadata["dpi"]
    if type(dpi) is not int or not 1 <= dpi <= 600:
        raise ValueError("Invalid render DPI")
    copies = {"manifest.json": (report / "manifest.json").read_bytes()}
    for name, expected in metadata["outputs"].items():
        if PurePosixPath(name).name != name or name in {".", ".."}:
            raise ValueError("Report output must be a file inside the report")
        path = report / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Report output must be a regular file")
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError(f"{name} differs from the authorized report")
        copies[name] = content
    out.mkdir(parents=True, exist_ok=False)
    target = out / "report"
    target.mkdir()
    for name, content in copies.items():
        (target / name).write_bytes(content)
    _export_minimal(inputs, loaded, target, out)
    record = {
        "schema": SCHEMA,
        "projection": {
            "file": projection.name,
            "sha256": hashlib.sha256(projection.read_bytes()).hexdigest(),
        },
        "dpi": dpi,
        "files": hashes(out),
    }
    with manifest.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return manifest


def _manifest(bundle: Path, path: Path) -> dict[str, Any]:
    data = read_json(path)
    if (
        set(data) != {"schema", "projection", "dpi", "files"}
        or data["schema"] != SCHEMA
    ):
        raise ValueError("Not a short-path expected-hash manifest")
    source = data["projection"]
    if not isinstance(source, dict) or set(source) != {"file", "sha256"}:
        raise ValueError("Invalid projection reference")
    name = source["file"]
    if (
        not isinstance(name, str)
        or PurePosixPath(name).name != name
        or name in {".", ".."}
    ):
        raise ValueError("Projection must be a file inside the bundle")
    projection = bundle / name
    if projection.is_symlink() or not projection.is_file():
        raise ValueError("Projection must be a regular file")
    if hashlib.sha256(projection.read_bytes()).hexdigest() != source["sha256"]:
        raise ValueError("Projection differs from expected SHA-256")
    if type(data["dpi"]) is not int or not 1 <= data["dpi"] <= 600:
        raise ValueError("Invalid render DPI")
    if not isinstance(data["files"], dict) or not data["files"]:
        raise ValueError("Expected files are missing")
    for name, spec in data["files"].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts or str(relative) != name:
            raise ValueError("Expected output path must be relative and confined")
        if not isinstance(spec, dict) or set(spec) != {"sha256", "normalization"}:
            raise ValueError(f"Invalid expected file: {name}")
        if (
            not isinstance(spec["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", spec["sha256"]) is None
        ):
            raise ValueError(f"Invalid expected SHA-256: {name}")
        if spec["normalization"] != normalization(name):
            raise ValueError(f"Unexpected normalization: {name}")
    return data


def verify(bundle: Path, manifest: Path, out: Path | None = None) -> int:
    try:
        expected = _manifest(bundle, manifest)
        if out is None:
            parent = Path(tempfile.mkdtemp(prefix="ic-v4-short-path-"))
            out = parent / "rendered"
        run_short_path(
            bundle / expected["projection"]["file"], out, dpi=expected["dpi"]
        )
        actual = hashes(out)
        failed = False
        for name in sorted(expected["files"].keys() | actual.keys()):
            wanted, received = expected["files"].get(name), actual.get(name)
            if wanted == received:
                assert received is not None
                print(f"OK   {name} ({received['normalization']})")
            else:
                failed = True
                print(f"FAIL {name}: expected {wanted}; received {received}")
        print(f"Rendered in {out}")
        print(NOTICE)
        return int(failed)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL {error}")
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preparation = commands.add_parser("prepare", help="Hash the authorized short path")
    add_input_arguments(preparation)
    preparation.add_argument("--report", type=Path, required=True)
    preparation.add_argument("--projection", type=Path, required=True)
    preparation.add_argument("--out", type=Path, required=True)
    preparation.add_argument("--manifest", type=Path, required=True)
    preparation.add_argument("--synthetic", action="store_true")
    verification = commands.add_parser("verify", help="Replay the public projection")
    verification.add_argument("--bundle", type=Path, required=True)
    verification.add_argument("--manifest", type=Path)
    verification.add_argument("--out", type=Path)
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0].startswith("-"):
        arguments.insert(0, "verify")
    args = parser.parse_args(arguments)
    if args.command == "prepare":
        try:
            path = prepare(
                parse_inputs(preparation, args),
                args.report,
                args.projection,
                args.out,
                args.manifest,
                synthetic=args.synthetic,
            )
        except (OSError, ValueError, KeyError, TypeError) as error:
            preparation.error(str(error))
        print(path)
        return 0
    return verify(
        args.bundle, args.manifest or args.bundle / "expected-hashes.json", args.out
    )


if __name__ == "__main__":
    raise SystemExit(main())
