"""Release-day handoff: authorized copies, Owner facts and the cached handoff run.

``copy`` reads the ``awaiting-authorized-handoff`` status of the installed
post-release chain, copies every input the chain selected into a new directory
outside the protected roots and checks each file by SHA-256 against its source,
the chain checkpoints, the release record and the report manifest. It writes
``handoff.json`` (``ic-study.v4-post-export-handoff.v1``) and a receipt binding
every copy, the handoff and the checkpoints. ``owner-facts`` computes
``gate.at_close`` and ``post.x5_supplied`` from those copies and ``run`` starts
the automation's ``handoff`` mode with the cached compiler; both re-verify the
receipt first. Each step refuses instead of guessing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from itertools import pairwise
from pathlib import Path
from typing import IO, Any

from ic_study.analysis.v4_exploratory_comparisons import AVAILABLE, UNAVAILABLE
from ic_study.analysis.v4_exploratory_comparisons import SCHEMA as COMPARISONS
from ic_study.analysis.v4_manuscript_assembly_facts import FACTS_SCHEMA, validate_facts
from ic_study.simulation.detection_v4 import RELIABILITIES
from ic_study.simulation.v4_plan import CLOSE_UTC

HANDOFF_SCHEMA = "ic-study.v4-post-export-handoff.v1"
RECEIPT_SCHEMA = "ic-study.v4-authorized-handoff-copies.v1"
REPORT_SCHEMA = "ic-study.detection-v4-report-manifest.v1"
AWAITING = "awaiting-authorized-handoff"
X5_ABSENT = "agregado X5 não fornecido"
TECTONIC = (
    "/nix/store/pxrhhj0zcl8ywp8ym4jw6fj7rrckfvcc-tectonic-wrapped-0.17.0/bin/tectonic"
)
PROTECTED_COORD = {"v4-tier-logs", "v4-gate-logs", "v4-release"}
OPTIONAL = {
    "v4-allocation.json": "allocation",
    "G1c-aggregate-successor.json": "stage_successors",
    "shp-aggregate-successor-1.json": "shp",
}
STATUS_NAME = {"stage_successors": "stage_successor"}
REPORT_ROLES = (
    "curves",
    "release_record",
    "criteria",
    "allocation",
    "shp",
    "crosswalk",
)
INPUT_ORDER = (
    "curves",
    "release_record",
    "gate_root",
    "criteria",
    "allocation",
    "stage_successors",
    "shp",
    "crosswalk",
)
SPRINGER = ("sn-jnl.cls", "sn-mathphys-num.bst")
TREES = {"gate_root", "report", "generated"}
EXPLORATORY = ("x3", "x4", "x6", "x7")
THREADS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
Tree = tuple[dict[str, str], frozenset[str]]


class HandoffRefusalError(ValueError):
    """Evidence that would need a guess; nothing is promoted from it."""


def state_root() -> Path:
    return Path.home() / ".local/state/research-workbench"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def protected(path: Path) -> bool:
    for candidate in (path.absolute(), path.resolve()):
        parts = [part.casefold() for part in candidate.parts]
        if any(p.startswith("sealed-v4-") or p == "restricted" for p in parts):
            return True
        pairs = pairwise(parts)
        if any(a == "coord-20260925" and b in PROTECTED_COORD for a, b in pairs):
            return True
    return False


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_bytes())
    except (OSError, ValueError) as error:
        raise HandoffRefusalError(f"{path}: unreadable JSON ({error})") from error


@contextmanager
def create(path: Path) -> Iterator[IO[bytes]]:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        yield stream
        stream.flush()
        os.fsync(stream.fileno())


def write_json(path: Path, value: Any) -> None:
    with create(path) as stream:
        text = json.dumps(value, indent=2, ensure_ascii=False)
        stream.write((text + "\n").encode())


def private_directory(path: Path) -> None:
    if not path.is_dir():
        private_directory(path.parent)
        path.mkdir(mode=0o700)


def copy_file(source: Path, target: Path) -> str:
    if source.is_symlink() or not source.is_file():
        raise HandoffRefusalError(f"{source}: expected a regular file, not a symlink")
    private_directory(target.parent)
    digest = hashlib.sha256()
    with source.open("rb") as reader, create(target) as writer:
        for chunk in iter(lambda: reader.read(1 << 20), b""):
            digest.update(chunk)
            writer.write(chunk)
    copied = digest.hexdigest()
    if sha256(target) != copied or sha256(source) != copied:
        raise HandoffRefusalError(f"{source}: copy and source differ (SHA-256)")
    return copied


def copy_tree(source: Path, target: Path) -> Tree:
    if source.is_symlink() or not source.is_dir():
        raise HandoffRefusalError(f"{source}: expected a directory, not a symlink")
    private_directory(target.parent)
    target.mkdir(mode=0o700)
    files: dict[str, str] = {}
    directories: set[str] = set()
    for directory, dirs, names in os.walk(source):
        dirs.sort()
        for name in [*dirs, *sorted(names)]:
            path = Path(directory) / name
            relative = path.relative_to(source).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise HandoffRefusalError(f"{path}: symlink inside a source tree")
            if stat.S_ISDIR(mode):
                (target / relative).mkdir(mode=0o700)
                directories.add(relative)
            elif stat.S_ISREG(mode):
                files[relative] = copy_file(path, target / relative)
            else:
                raise HandoffRefusalError(f"{path}: special file inside a source tree")
    return files, frozenset(directories)


def manifest_entries(entries: str, prefix: str = "") -> Tree:
    """Files and directories under ``prefix`` in a chain checkpoint manifest."""
    files: dict[str, str] = {}
    directories: set[str] = set()
    for name, kind, *digest in json.loads(entries):
        if not name.startswith(prefix):
            continue
        if kind == "file":
            files[name.removeprefix(prefix)] = digest[0]
        elif kind == "directory":
            directories.add(name.removeprefix(prefix))
    return files, frozenset(directories)


def checkpoint(path: Path, root: object) -> dict[str, Any]:
    value = read_json(path)
    if (
        not isinstance(value, dict)
        or value.get("root") != root
        or not isinstance(value.get("inputs"), dict)
        or not isinstance(value.get("outputs"), str)
    ):
        raise HandoffRefusalError(f"{path}: not the checkpoint of {root}")
    return value


def source_path(inputs: dict[str, Any], role: str) -> Path:
    value = inputs.get(STATUS_NAME.get(role, role))
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise HandoffRefusalError(
            f"{role}: the chain status must name an absolute path"
        )
    return Path(value)


def plan_copies(
    status: dict[str, Any], key: dict[str, Any]
) -> list[tuple[str, Path, str]]:
    """Role, source and relative target of every input the chain selected."""
    inputs = status["inputs"]
    roles = ["curves", "release_record", "gate_root", "criteria"]
    for path in key["optional"]:
        role = OPTIONAL.get(Path(path).name)
        if role is None or str(source_path(inputs, role)) != path:
            raise HandoffRefusalError(
                f"{path}: status and checkpoint select other inputs"
            )
        roles.append(role)
    if "shp" in roles:
        roles.append("crosswalk")
    roles += ["report", "confirmatory_catalog", "merged_catalog"]
    plan = [(role, source_path(inputs, role), "") for role in roles]
    generated = source_path(inputs, "generated")
    plan.append(("generated", generated, "manuscript-exported/generated"))
    plan += [
        ("springer", generated.parent / name, f"manuscript-exported/{name}")
        for name in SPRINGER
    ]
    exploratory = inputs.get("exploratory")
    if not isinstance(exploratory, dict) or set(exploratory) != set(EXPLORATORY):
        raise HandoffRefusalError("exploratory: the status must list x3, x4, x6, x7")
    plan += [
        (name, source_path(exploratory, name), f"aggregates/{name}.json")
        for name in EXPLORATORY
    ]
    plan.append(("comparisons", source_path(inputs, "comparisons"), ""))
    plan = [(role, path, target or path.name) for role, path, target in plan]
    targets = [target for _, _, target in plan]
    if len(set(targets)) != len(targets):
        raise HandoffRefusalError("two selected inputs share a destination name")
    for role, path, _ in plan:
        kind = path.is_dir() if role in TREES else path.is_file()
        if path.is_symlink() or not kind:
            raise HandoffRefusalError(
                f"{role}: selected by the chain but missing: {path}"
            )
    return plan


def expected_trees(
    confirmed: str, exported: str, key: dict[str, Any], sources: dict[str, Path]
) -> dict[str, Tree]:
    """What the chain checkpoints recorded for each copied role."""
    made, _ = manifest_entries(confirmed)
    produced, _ = manifest_entries(exported)

    def single(digest: str) -> Tree:
        return {".": digest}, frozenset()

    expected = {
        "report": manifest_entries(confirmed, "report/"),
        "generated": manifest_entries(exported, "manuscript/generated/"),
        "gate_root": manifest_entries(key["gate"]),
        "confirmatory_catalog": single(made.get("result-catalog.json", "")),
        "merged_catalog": single(produced.get("catalog.json", "")),
        "comparisons": single(produced.get("comparisons.json", "")),
        "release_record": single(key["release"]),
        "springer": (
            {name: produced.get(f"manuscript/{name}", "") for name in SPRINGER},
            frozenset(),
        ),
    }
    for name in EXPLORATORY:
        expected[name] = single(produced.get(f"aggregates/{name}.json", ""))
    for role in ("allocation", "stage_successors", "shp"):
        if role in sources:
            expected[role] = single(key["optional"].get(str(sources[role]), ""))
    return expected


def verify_report(
    manifest: Any, copies: dict[str, Path], successors: list[Path], synthetic: bool
) -> int:
    if not isinstance(manifest, dict) or manifest.get("schema") != REPORT_SCHEMA:
        raise HandoffRefusalError("report: not a v4 report manifest")
    if manifest.get("synthetic") is not synthetic:
        raise HandoffRefusalError("report: synthetic marker differs from --synthetic")
    recorded = manifest.get("inputs")
    if not isinstance(recorded, dict):
        raise HandoffRefusalError("report: manifest has no input record")
    for role in REPORT_ROLES:
        entry, path = recorded.get(role), copies.get(role)
        if (entry is None) != (path is None):
            raise HandoffRefusalError(f"{role}: report and chain selection differ")
        if path is not None and (
            not isinstance(entry, dict)
            or entry.get("name") != path.name
            or entry.get("sha256") != sha256(path)
        ):
            raise HandoffRefusalError(f"{role}: report was rendered from another file")
    gate = recorded.get("gate_root")
    root = copies["gate_root"]
    if (
        not isinstance(gate, dict)
        or gate.get("identifier") != root.name
        or gate.get("criteria.jsonl") != sha256(root / "criteria.jsonl")
    ):
        raise HandoffRefusalError(
            "gate_root: report was rendered from another gate root"
        )
    listed = recorded.get("stage_successors") or []
    names = [
        (e.get("name"), e.get("sha256")) if isinstance(e, dict) else None
        for e in (listed if isinstance(listed, list) else [None])
    ]
    if names != [(p.name, sha256(p)) for p in successors]:
        raise HandoffRefusalError("stage_successors: report used other successors")
    dpi = manifest.get("dpi")
    if type(dpi) is not int or not 1 <= dpi <= 600:
        raise HandoffRefusalError("report: manifest DPI is invalid")
    return dpi


def catalog_values(path: Path) -> dict[str, Any]:
    value = read_json(path)
    values = value.get("values") if isinstance(value, dict) else None
    if not isinstance(values, dict):
        raise HandoffRefusalError(f"{path.name}: not a result catalog")
    return values


def prepare_copies(status_path: Path, out: Path, *, synthetic: bool) -> Path:
    """Copy the chain's selected inputs into ``out`` and write ``handoff.json``."""
    status_path, out = status_path.absolute(), out.absolute()
    status = read_json(status_path)
    if not isinstance(status, dict) or status.get("status") != AWAITING:
        raise HandoffRefusalError(f"{status_path}: status is not {AWAITING}")
    if not isinstance(status.get("inputs"), dict):
        raise HandoffRefusalError(f"{status_path}: status lists no inputs")
    if protected(out):
        raise HandoffRefusalError(f"{out}: destination inside a protected root")
    if out.exists() or out.is_symlink():
        raise HandoffRefusalError(f"{out}: choose a new directory")
    chain = status_path.parent
    roots = {
        "confirmatory": status.get("confirmatory"),
        "exploratory": status.get("exported_attempt"),
    }
    confirmed, exported = (
        checkpoint(chain / f"{name}-checkpoint.json", root)
        for name, root in roots.items()
    )
    key = exported["inputs"]
    shared = ("release", "report_commit", "automation", "gate", "optional")
    if any(confirmed["inputs"].get(k) != key.get(k) for k in shared):
        raise HandoffRefusalError("checkpoints belong to different releases or gates")
    if not (
        isinstance(key.get("gate"), str)
        and isinstance(key.get("release"), str)
        and isinstance(key.get("optional"), dict)
    ):
        raise HandoffRefusalError(
            "checkpoint: release, gate or optional inputs missing"
        )
    plan = plan_copies(status, key)
    sources = {role: path for role, path, _ in plan}
    report = read_json(sources["report"] / "manifest.json")
    marker = report.get("synthetic") if isinstance(report, dict) else None
    if marker is not synthetic:
        raise HandoffRefusalError(
            f"synthetic marker: the report says {marker}, --synthetic says "
            f"{synthetic}; it must be explicit and match"
        )
    out.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    out.mkdir(mode=0o700)
    try:
        copies: dict[str, Tree] = {}
        files: dict[str, dict[str, str]] = {}
        for role, source, target in plan:
            if source.is_dir():
                tree = copy_tree(source, out / target)
            else:
                tree = {".": copy_file(source, out / target)}, frozenset()
            for relative, digest in tree[0].items():
                name = (out / target / relative).relative_to(out).as_posix()
                files[name] = {
                    "role": role,
                    "source": str(source / relative),
                    "sha256": digest,
                }
            if role == "springer":
                previous = copies.get(role, ({}, frozenset()))[0]
                copies[role] = (previous | {source.name: tree[0]["."]}, frozenset())
            else:
                copies[role] = tree
        expected = expected_trees(
            confirmed["outputs"], exported["outputs"], key, sources
        )
        for role, recorded in expected.items():
            if copies.get(role) != recorded:
                raise HandoffRefusalError(f"{role} differs from the chain checkpoint")
        placed = {role: out / target for role, _, target in plan}
        record = read_json(placed["release_record"])
        bound = (
            record.get("released_curves_sha256") if isinstance(record, dict) else None
        )
        if bound != copies["curves"][0]["."]:
            raise HandoffRefusalError("curves differ from the release record")
        successors = [placed[r] for r in ("stage_successors",) if r in placed]
        manifest = read_json(placed["report"] / "manifest.json")
        dpi = verify_report(manifest, placed, successors, synthetic)
        confirmatory = catalog_values(placed["confirmatory_catalog"])
        merged = catalog_values(placed["merged_catalog"])
        if any(merged.get(k) != v for k, v in confirmatory.items()):
            raise HandoffRefusalError("merged catalog lacks the confirmatory values")
        inputs: dict[str, Any] = {
            role: [str(placed[role])]
            if role == "stage_successors"
            else str(placed[role])
            for role in INPUT_ORDER
            if role in placed
        }
        exploratory = {name: str(placed[name]) for name in EXPLORATORY}
        write_json(
            out / "handoff.json",
            {
                "schema": HANDOFF_SCHEMA,
                "synthetic": synthetic,
                "dpi": dpi,
                "inputs": inputs,
                "report": str(placed["report"]),
                "exported_manuscript": str(out / "manuscript-exported"),
                "confirmatory_catalog": str(placed["confirmatory_catalog"]),
                "merged_catalog": str(placed["merged_catalog"]),
                "exploratory": exploratory
                | {"comparisons": str(placed["comparisons"])},
            },
        )
        here = Path(__file__).resolve()
        checkpoints = {}
        for name, root in roots.items():
            path = chain / f"{name}-checkpoint.json"
            checkpoints[name] = {
                "path": str(path),
                "sha256": sha256(path),
                "root": root,
            }
        omitted = sorted({"allocation", "stage_successors", "shp"} - placed.keys())
        write_json(
            out / "copy-receipt.json",
            {
                "schema": RECEIPT_SCHEMA,
                "synthetic": synthetic,
                "status": {
                    "path": str(status_path),
                    "sha256": sha256(status_path),
                    "status": AWAITING,
                },
                "checkpoints": checkpoints,
                "tool": {"path": str(here), "sha256": sha256(here)},
                "omitted_optional": dict.fromkeys(omitted, "not selected by the chain"),
                "handoff": {
                    "path": "handoff.json",
                    "sha256": sha256(out / "handoff.json"),
                },
                "directories": sorted(
                    path.relative_to(out).as_posix()
                    for path in out.rglob("*")
                    if path.is_dir()
                ),
                "files": dict(sorted(files.items())),
            },
        )
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise
    return out / "handoff.json"


def handoff_paths(spec: Any) -> list[str]:
    """Every path ``handoff.json`` hands to the automation."""
    if not isinstance(spec, dict) or not isinstance(spec.get("inputs"), dict):
        raise HandoffRefusalError("handoff.json lists no inputs")
    values = [
        path
        for role, value in spec["inputs"].items()
        for path in (value if role == "stage_successors" else [value])
    ]
    names = ("report", "exported_manuscript", "confirmatory_catalog", "merged_catalog")
    values += [spec.get(name) for name in names]
    exploratory = spec.get("exploratory") or {}
    values += list(exploratory.values()) if isinstance(exploratory, dict) else [None]
    if not all(isinstance(value, str) for value in values):
        raise HandoffRefusalError("handoff.json names a path that is not a string")
    return values


def verify_receipt(handoff: Path) -> dict[str, Any]:
    """Re-hash the authorized copies, ``handoff.json`` and the chain checkpoints."""
    directory = handoff.parent
    receipt = read_json(directory / "copy-receipt.json")
    if not isinstance(receipt, dict) or receipt.get("schema") != RECEIPT_SCHEMA:
        raise HandoffRefusalError(f"{directory}: no copy receipt; run copy first")
    listed, bound = receipt.get("files"), receipt.get("handoff")
    if not isinstance(listed, dict) or not isinstance(bound, dict):
        raise HandoffRefusalError("copy receipt lists no authorized copies")
    if handoff.name != bound.get("path") or sha256(handoff) != bound.get("sha256"):
        raise HandoffRefusalError("handoff.json differs from the copy receipt")
    named = handoff_paths(read_json(handoff))
    inside = directory.resolve()
    for value in named:
        path = Path(value).resolve() if Path(value).is_absolute() else None
        if path is None or not path.is_relative_to(inside):
            raise HandoffRefusalError(
                f"handoff.json points outside its authorized directory: {value}"
            )
        relative = path.relative_to(inside).as_posix()
        if relative not in listed and not any(
            name.startswith(relative + "/") for name in listed
        ):
            raise HandoffRefusalError(f"handoff.json names an unreceipted {value}")
    directories = sorted(
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_dir() and not path.is_symlink()
    )
    if directories != receipt.get("directories"):
        raise HandoffRefusalError("authorized directories differ from the copy receipt")
    present = {
        path.relative_to(directory).as_posix(): path
        for path in directory.rglob("*")
        if path.is_symlink() or not path.is_dir()
    }
    present.pop("handoff.json", None)
    present.pop("copy-receipt.json", None)
    if present.keys() != listed.keys():
        unexpected = sorted(present.keys() ^ listed.keys())[:3]
        raise HandoffRefusalError(
            f"authorized directory and copy receipt list other files: {unexpected}"
        )
    for name, path in sorted(present.items()):
        entry = listed[name]
        if (
            path.is_symlink()
            or not isinstance(entry, dict)
            or sha256(path) != entry.get("sha256")
        ):
            raise HandoffRefusalError(f"{name}: differs from the copy receipt")
    checkpoints = receipt.get("checkpoints")
    if not isinstance(checkpoints, dict) or not checkpoints:
        raise HandoffRefusalError("copy receipt names no chain checkpoint")
    for name, entry in checkpoints.items():
        path = Path(entry.get("path", "")) if isinstance(entry, dict) else Path()
        if not path.is_file() or sha256(path) != entry.get("sha256"):
            raise HandoffRefusalError(
                f"{name} checkpoint changed after the copy; copy again"
            )
    return receipt


def close_observation(record: object, curves_sha256: str) -> tuple[bool, str]:
    """``gate.at_close`` from the authorized release record, never from a clock."""
    if (
        not isinstance(record, dict)
        or type(record.get("schema")) is not int
        or record["schema"] != 1
    ):
        raise HandoffRefusalError("release record: unsupported schema")
    condition = record.get("condition")
    if condition not in {"inventory-complete", "declared-close"}:
        raise HandoffRefusalError(f"release record: unknown condition {condition!r}")
    stamp = record.get("released_utc")
    try:
        if not isinstance(stamp, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", stamp
        ):
            raise ValueError(stamp)
        released = datetime.fromisoformat(stamp)
    except ValueError as error:
        raise HandoffRefusalError(
            "release record: released_utc is not a UTC timestamp"
        ) from error
    if record.get("released_curves_sha256") != curves_sha256:
        raise HandoffRefusalError("release record does not bind the authorized curves")
    at_close = condition == "declared-close"
    if at_close and released < datetime.fromisoformat(CLOSE_UTC):
        raise HandoffRefusalError(
            "release record: declared-close release precedes the close"
        )
    if not at_close and released >= datetime.fromisoformat(CLOSE_UTC):
        raise HandoffRefusalError(
            "release record: inventory-complete release after the close"
        )
    relation = ">=" if at_close else "<"
    return at_close, (
        f"/condition = {condition}; /released_utc = {stamp} {relation} close "
        f"{CLOSE_UTC}; /released_curves_sha256 binds the authorized curves"
    )


def x5_supply(
    comparisons: object, curves_sha256: str, record_sha256: str
) -> tuple[bool, str]:
    """``post.x5_supplied`` from comparison provenance and every by_r label."""
    if not isinstance(comparisons, dict) or comparisons.get("schema") != COMPARISONS:
        raise HandoffRefusalError("comparisons: unexpected schema")
    provenance = comparisons.get("provenance")
    inputs = provenance.get("inputs") if isinstance(provenance, dict) else None
    if not isinstance(inputs, dict) or "x5" not in inputs:
        raise HandoffRefusalError(
            "comparisons: provenance does not record the X5 input"
        )
    for name, digest in (("curves", curves_sha256), ("release_record", record_sha256)):
        bound = inputs.get(name)
        if not isinstance(bound, dict) or bound.get("sha256") != digest:
            raise HandoffRefusalError(f"comparisons: provenance binds other {name}")
    binding = inputs["x5"]
    if binding is not None and not (
        isinstance(binding, dict)
        and isinstance(binding.get("sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", binding["sha256"]) is not None
    ):
        raise HandoffRefusalError("comparisons: malformed X5 binding")
    supplied = binding is not None
    expected = (
        {"state": AVAILABLE, "reason": None}
        if supplied
        else {"state": UNAVAILABLE, "reason": X5_ABSENT}
    )
    rows = comparisons.get("by_r")
    if not isinstance(rows, dict) or set(rows) != {str(r) for r in RELIABILITIES}:
        raise HandoffRefusalError("comparisons: by_r must hold the nine reliabilities")
    for name in sorted(rows, key=float):
        row = rows[name]
        if not isinstance(row, dict) or row.get("x5_state") != expected:
            raise HandoffRefusalError(
                f"comparisons: by_r/{name}/x5_state contradicts the X5 binding"
            )
    detail = "null" if binding is None else f"{binding.get('name')} {binding['sha256']}"
    return supplied, (
        f"/provenance/inputs/x5 = {detail}; /by_r/*/x5_state = {expected['state']} "
        f"in all {len(rows)} rows; /provenance/inputs binds the authorized curves "
        "and release record"
    )


def write_owner_facts(handoff: Path, out: Path) -> dict[str, Any]:
    """Write a new Owner facts file computed only from receipted authorized copies."""
    handoff, out = handoff.absolute(), out.absolute()
    if protected(out):
        raise HandoffRefusalError(f"{out}: destination inside a protected root")
    if out.exists() or out.is_symlink():
        raise HandoffRefusalError(f"{out}: choose a new file")
    spec = read_json(handoff)
    if (
        not isinstance(spec, dict)
        or spec.get("schema") != HANDOFF_SCHEMA
        or type(spec.get("synthetic")) is not bool
    ):
        raise HandoffRefusalError(f"{handoff}: not a handoff with a synthetic marker")
    receipt = verify_receipt(handoff)
    if receipt.get("synthetic") is not spec["synthetic"]:
        raise HandoffRefusalError("copy receipt and handoff synthetic markers differ")
    listed = receipt["files"]

    def evidence(value: object, role: str) -> tuple[str, str, Path]:
        if not isinstance(value, str) or not Path(value).is_absolute():
            raise HandoffRefusalError(f"{role}: absent from the authorized handoff")
        path = Path(value)
        if protected(path) or not path.is_relative_to(handoff.parent):
            raise HandoffRefusalError(f"{role}: not an authorized copy: {path}")
        name = path.relative_to(handoff.parent).as_posix()
        entry = listed.get(name)
        digest = sha256(path)
        if (
            not isinstance(entry, dict)
            or entry.get("role") != role
            or entry.get("sha256") != digest
        ):
            raise HandoffRefusalError(f"{role}: differs from the copy receipt")
        return name, digest, path

    inputs = spec.get("inputs")
    if (
        not isinstance(inputs, dict)
        or not {"curves", "release_record"} <= inputs.keys()
    ):
        raise HandoffRefusalError(
            "gate.at_close: no authorized release record; an unreleased gate needs "
            "an Owner record sealed at the close (B1d)"
        )
    record, record_sha, record_path = evidence(
        inputs["release_record"], "release_record"
    )
    _, curves_sha, _ = evidence(inputs["curves"], "curves")
    at_close, close_locator = close_observation(read_json(record_path), curves_sha)
    exploratory = spec.get("exploratory")
    value = exploratory.get("comparisons") if isinstance(exploratory, dict) else None
    if value is None:
        raise HandoffRefusalError(
            "post.x5_supplied: no authorized comparisons; the fact needs the "
            "post-release comparisons"
        )
    comparison, comparison_sha, comparison_path = evidence(value, "comparisons")
    supplied, x5_locator = x5_supply(read_json(comparison_path), curves_sha, record_sha)
    facts = validate_facts(
        {
            "schema": FACTS_SCHEMA,
            "synthetic": spec["synthetic"],
            "facts": {
                "gate.at_close": {
                    "value": at_close,
                    "source": {
                        "record": record,
                        "locator": close_locator,
                        "sha256": record_sha,
                    },
                },
                "post.x5_supplied": {
                    "value": supplied,
                    "source": {
                        "record": comparison,
                        "locator": x5_locator,
                        "sha256": comparison_sha,
                    },
                },
            },
        }
    )
    write_json(out, facts)
    pending = [] if "shp" in inputs else ["shp.state", "shp.reason"]
    return {
        "owner_facts": str(out),
        "authorized": str(handoff.parent),
        "synthetic": spec["synthetic"],
        "facts": {name: fact["value"] for name, fact in facts["facts"].items()},
        "pending_owner": pending,
        "conditional_owner": {"shp.divergence": "when shp.state is pre-run-divergence"}
        if pending
        else {},
    }


def lower_priority() -> None:
    os.setpriority(os.PRIO_PROCESS, 0, max(15, os.getpriority(os.PRIO_PROCESS, 0)))


def identity(path: Path) -> tuple[int, int, int] | None:
    try:
        state = path.stat()
    except FileNotFoundError:
        return None
    return state.st_ino, state.st_mtime_ns, state.st_size


def run_handoff(arguments: argparse.Namespace) -> int:
    cache = (arguments.tectonic_cache or state_root() / "tectonic-cache").absolute()
    if not cache.is_dir() or not any(p.is_file() for p in cache.rglob("*")):
        raise HandoffRefusalError(
            f"Tectonic cache missing or empty: {cache}. The handoff compiles with "
            "--only-cached and cannot download; restore the warm cache first."
        )
    tectonic = Path(arguments.tectonic).absolute()
    if not tectonic.is_file() or not os.access(tectonic, os.X_OK):
        raise HandoffRefusalError(f"Tectonic executable missing: {tectonic}")
    automation = (
        arguments.automation or state_root() / "coord-20260925/v4_event_automation.py"
    ).absolute()
    handoff, facts_path = arguments.handoff.absolute(), arguments.owner_facts.absolute()
    out, checkout = arguments.out.absolute(), arguments.checkout.absolute()
    for path in (automation, handoff, facts_path):
        if not path.is_file():
            raise HandoffRefusalError(f"missing file: {path}")
    for path in (handoff, facts_path, out):
        if protected(path):
            raise HandoffRefusalError(f"{path}: inside a protected root")
    spec = read_json(handoff)
    synthetic = spec.get("synthetic") if isinstance(spec, dict) else None
    if synthetic is not arguments.synthetic:
        raise HandoffRefusalError(
            f"handoff.json says synthetic={synthetic}; --synthetic is only for "
            "rehearsals and must match"
        )
    receipt = verify_receipt(handoff)
    facts = validate_facts(read_json(facts_path))
    if receipt.get("synthetic") is not synthetic or facts["synthetic"] is not synthetic:
        raise HandoffRefusalError(
            "copy receipt, Owner facts and handoff synthetic markers differ"
        )
    environment = {k: v for k, v in os.environ.items() if k != "V4_ALLOW_UNNICE"}
    environment |= dict.fromkeys(THREADS, "1") | {
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "V4_SHORT_PATH": "1",
        "V4_TECTONIC": str(tectonic),
        "TECTONIC_CACHE_DIR": str(cache),
        "V4_OWNER_FACTS": str(facts_path),
    }
    argv = [sys.executable, str(automation), "handoff", str(checkout)]
    argv += ["--spec", str(handoff), "--out", str(out)]
    status_path = out / "chain-status.json"
    before = identity(status_path)
    code = subprocess.run(
        argv, env=environment, check=False, preexec_fn=lower_priority
    ).returncode
    if identity(status_path) in {None, before}:
        print(
            json.dumps(
                {"exit_code": code, "status": None, "note": "no new chain-status.json"}
            )
        )
        return code
    status = read_json(status_path)
    names = ("status", "exit_code", "assembly_ready", "missing_facts", "checks")
    summary = {name: status.get(name) for name in names}
    summary |= {
        "attempt": status.get("outputs", {}).get("attempt"),
        "pdf": status.get("pdf"),
        "error": status.get("error"),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    copy = commands.add_parser("copy", help="authorized copies and handoff.json")
    copy.add_argument("--status", type=Path, required=True)
    copy.add_argument("--out", type=Path, required=True)
    copy.add_argument("--synthetic", action="store_true")
    facts = commands.add_parser("owner-facts", help="gate.at_close, post.x5_supplied")
    facts.add_argument("--handoff", type=Path, required=True)
    facts.add_argument("--out", type=Path, required=True)
    run = commands.add_parser("run", help="automation handoff with the cached compiler")
    run.add_argument("--checkout", type=Path, required=True)
    run.add_argument("--handoff", type=Path, required=True)
    run.add_argument("--owner-facts", type=Path, required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--automation", type=Path)
    run.add_argument("--tectonic", default=TECTONIC)
    run.add_argument("--tectonic-cache", type=Path)
    run.add_argument("--synthetic", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "copy":
            path = prepare_copies(
                arguments.status, arguments.out, synthetic=arguments.synthetic
            )
            print(path)
            return 0
        if arguments.command == "owner-facts":
            summary = write_owner_facts(arguments.handoff, arguments.out)
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return 0
        return run_handoff(arguments)
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(f"refused: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
