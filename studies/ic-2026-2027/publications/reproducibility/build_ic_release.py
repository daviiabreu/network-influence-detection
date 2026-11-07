"""Allowlisted scientific release packaging and offline integrity verification.

Only plan/build consult a local repository. No command runs scientific code,
fetches Git objects, or discovers data roots. Input hashes must be supplied before
build; a release plan is a selection record, never Research Owner approval.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
import zlib
from pathlib import Path, PurePosixPath
from typing import Any

PREFIX = "studies/ic-2026-2027/"
QUESTIONS = "research/questions/exploration/2026-09-24-parallel/"
V4 = "experiments/exploratory/detection-boundary-v4/"
V44 = "experiments/exploratory/detection-boundary-v4-successor-v44/"
EXPLORATORY = "experiments/exploratory/detection-boundary-v4-exploratory/"
PINNED = {
    "confirmatory": "375138418f7f9e4528f0c2466f4600a76fee1bad",
    "x3-x7": "3334ac0f96268a76d62c3b68a9705cb7fe05587e",
    "legacy-x5-x7": "c8e4861fdba24700d3ca802e337f81f103d65c57",
    "shp-code": "17a0dbedc06fbcabd2ebfe907b3c96c13a743f6b",
    "shp-freeze": "703c51142b56421313fd6ed076f6ac121bc7293e",
    "v44-successor": "7a1b8132f0dba9b365f678d2a5dd881cea39a9b7",
}
ROLES = (*PINNED, "release-wrapper", "bridge", "reporting-export")
ENVIRONMENT = ("README.md", ".python-version", "pyproject.toml", "uv.lock")
SOURCE_ALLOWLIST = (
    "experiments/exploratory/detection-boundary-v4/audit_seeds.py",
    "experiments/exploratory/detection-boundary-v4/calibrate_criteria.py",
    "experiments/exploratory/detection-boundary-v4/measure_cost.py",
    "experiments/exploratory/detection-boundary-v4/measure_panels.py",
    "experiments/exploratory/detection-boundary-v4/measure_v41.py",
    "experiments/exploratory/detection-boundary-v4/measure_v42.py",
    "experiments/exploratory/detection-boundary-v4/project_compute.py",
    "experiments/exploratory/detection-boundary-v4/project_v41.py",
    "experiments/exploratory/detection-boundary-v4/project_v42.py",
    "experiments/exploratory/detection-boundary-v4/run_curve.py",
    "experiments/exploratory/detection-boundary-v4/run_gate.py",
    "experiments/exploratory/detection-boundary-v4/verify_v41.py",
    "experiments/exploratory/detection-boundary-v4/verify_v42.py",
    "experiments/exploratory/detection-boundary-v4-successor-v44/v44_run_curve.py",
    "src/ic_study/__init__.py",
    "src/ic_study/analysis/__init__.py",
    "src/ic_study/analysis/detection_boundary.py",
    "src/ic_study/analysis/detection_boundary_v4.py",
    "src/ic_study/analysis/detection_v4_report.py",
    "src/ic_study/analysis/forecast_pilot.py",
    "src/ic_study/analysis/fragmentation_pilot.py",
    "src/ic_study/analysis/map_saturation_figures.py",
    "src/ic_study/analysis/redesign.py",
    "src/ic_study/analysis/shp_crosswalk.py",
    "src/ic_study/analysis/shp_reliability.py",
    "src/ic_study/analysis/v4_exploratory_comparisons.py",
    "src/ic_study/analysis/v4_exploratory_export.py",
    "src/ic_study/analysis/v4_public_aggregates.py",
    "src/ic_study/analysis/v4_manuscript_assembly.py",
    "src/ic_study/analysis/v4_manuscript_assembly_derive.py",
    "src/ic_study/analysis/v4_manuscript_assembly_facts.py",
    "src/ic_study/analysis/v4_manuscript_assembly_rules.json",
    "src/ic_study/analysis/v4_manuscript_assembly_facts.schema.json",
    "src/ic_study/analysis/v4_report_export.py",
    "src/ic_study/analysis/v4_report_figures.py",
    "src/ic_study/analysis/v4_report_protocol.py",
    "src/ic_study/analysis/v4_report_schema.py",
    "src/ic_study/analysis/v4_report_synthetic.py",
    "src/ic_study/analysis/v4_report_tables.py",
    "src/ic_study/literature/__init__.py",
    "src/ic_study/literature/identity_proposals.py",
    "src/ic_study/metrics/__init__.py",
    "src/ic_study/metrics/histogram_scores.py",
    "src/ic_study/models/__init__.py",
    "src/ic_study/models/anchored_panel.py",
    "src/ic_study/models/critical_dose.py",
    "src/ic_study/models/deffuant.py",
    "src/ic_study/models/detection_panel.py",
    "src/ic_study/models/detection_panel_v4.py",
    "src/ic_study/models/histogram_forecast.py",
    "src/ic_study/models/mechanism_controls.py",
    "src/ic_study/py.typed",
    "src/ic_study/simulation/__init__.py",
    "src/ic_study/simulation/amendment_a.py",
    "src/ic_study/simulation/detection_calibration.py",
    "src/ic_study/simulation/detection_coverage_check.py",
    "src/ic_study/simulation/detection_v4.py",
    "src/ic_study/simulation/fragmentation.py",
    "src/ic_study/simulation/redesign_calibration.py",
    "src/ic_study/simulation/v4_criteria.py",
    "src/ic_study/simulation/v4_curve.py",
    "src/ic_study/simulation/v4_exploratory.py",
    "src/ic_study/simulation/v4_exploratory_x1b.py",
    "src/ic_study/simulation/v4_exploratory_x3.py",
    "src/ic_study/simulation/v4_exploratory_x3x7.py",
    "src/ic_study/simulation/v4_exploratory_x4.py",
    "src/ic_study/simulation/v4_exploratory_x5.py",
    "src/ic_study/simulation/v4_exploratory_x6.py",
    "src/ic_study/simulation/v4_exploratory_x7.py",
    "src/ic_study/simulation/v4_gate.py",
    "src/ic_study/simulation/v4_plan.py",
    "src/ic_study/simulation/v4_store.py",
    "src/ic_study/validation/__init__.py",
    "src/ic_study/validation/experiments.py",
    "tests/integration/test_experiment_validation.py",
    "tests/integration/test_forecast_pilot.py",
    "tests/integration/test_fragmentation_pilot.py",
    "tests/scientific/test_fragmentation.py",
    "tests/scientific/test_histogram_forecast.py",
    "tests/scientific/test_mechanism_controls.py",
    "tests/test_package.py",
    "tests/unit/test_amendment_a.py",
    "tests/unit/test_anchored_panel.py",
    "tests/unit/test_critical_dose.py",
    "tests/unit/test_detection_boundary.py",
    "tests/unit/test_detection_calibration.py",
    "tests/unit/test_detection_coverage_check.py",
    "tests/unit/test_detection_panel.py",
    "tests/unit/test_detection_v4.py",
    "tests/unit/test_identity_proposals.py",
    "tests/unit/test_redesign_analysis.py",
    "tests/unit/test_v41_binding.py",
    "tests/unit/test_v41_channels.py",
    "tests/unit/test_v41_cost.py",
    "tests/unit/test_v41_covariance.py",
    "tests/unit/test_v42_cost.py",
    "tests/unit/test_v42_gate.py",
    "tests/unit/test_v42_identity.py",
    "tests/unit/test_v42_solver.py",
    "tests/unit/test_v42_verification.py",
    "tests/unit/test_v44_successor_runner.py",
    "tests/unit/test_v4_criteria.py",
    "tests/unit/test_v4_curve.py",
    "tests/unit/test_v4_inventory.py",
    "tests/unit/test_v4_propagation.py",
    "tests/unit/test_v4_runners.py",
    "tests/unit/test_v4_sealing.py",
    "tests/unit/test_v4_solver.py",
    "tests/unit/test_v4_validation_pipeline.py",
)
PUBLIC_ALLOWLIST = (
    "publications/reproducibility/README.md",
    "publications/reproducibility/Makefile",
    "publications/reproducibility/build_ic_release.py",
    "publications/reproducibility/verify_short_path.py",
    "publications/reproducibility/ic-release-manifest.schema.json",
    "publications/jcss-manuscript/pipeline/ASSEMBLY.md",
    "publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells.tex",
    "publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells-abstract.md",
    "publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex",
    "publications/jcss-manuscript/pipeline/drafts/2026-09-30/exploratory-results-shells.tex",
    V4 + "freeze-v4.json",
    V4 + "criteria-v43.json",
    V4 + "inventory.json",
    V4 + "run_gate.py",
    V4 + "run_curve.py",
    V4 + "release_on_completion.py",
    V4 + "report/README.md",
    V4 + "report/RELEASE-RUNBOOK.md",
    V44 + "AMENDMENT-v4.4.md",
    V44 + "freeze-v44.json",
    EXPLORATORY + "declaration.json",
    EXPLORATORY + "declaration-x3-x7.json",
    EXPLORATORY + "compatibility-c8e4861f.json",
    EXPLORATORY + "README.md",
    EXPLORATORY + "README-x3-x7.md",
    EXPLORATORY + "run-x3x7-stages.sh",
    EXPLORATORY + "launch-x3x7.sh",
    "experiments/exploratory/shp-anchor-crosswalk-v1/crosswalk.json",
    "experiments/exploratory/shp-anchor-crosswalk-v1/README.md",
    *(
        QUESTIONS + name
        for name in (
            "detection-boundary-freeze.json",
            "detection-boundary-preregistration-frozen.md",
            "detection-boundary-amendment-v4.md",
            "amendment-v4-1-revision.md",
            "amendment-v4-decision-spec.md",
            "v4-review-findings.md",
            "v4-review-decisions.md",
            "v4-delta-review-decisions.md",
            "detection-boundary-v4-release-amendment.md",
            "shp-reliability-preregistration.md",
            "shp-reliability-preregistration.json",
            "shp-reliability-freeze.json",
            "shp-reliability-successor-1.md",
            "shp-reliability-successor-1.json",
            "shp-reliability-successor-1-freeze.json",
            "shp-reliability-guide.md",
        )
    ),
)
REQUIRED = {
    "confirmatory": (V4 + "freeze-v4.json",),
    "release-wrapper": (
        V4 + "release_on_completion.py",
        QUESTIONS + "detection-boundary-v4-release-amendment.md",
    ),
    "x3-x7": (
        "src/ic_study/simulation/v4_exploratory_x3x7.py",
        EXPLORATORY + "declaration-x3-x7.json",
    ),
    "legacy-x5-x7": (EXPLORATORY + "declaration-x3-x7.json",),
    "shp-code": (
        "src/ic_study/analysis/shp_reliability.py",
        "src/ic_study/analysis/shp_crosswalk.py",
    ),
    "shp-freeze": (QUESTIONS + "shp-reliability-successor-1-freeze.json",),
    "v44-successor": (
        V44 + "AMENDMENT-v4.4.md",
        V44 + "freeze-v44.json",
        V44 + "v44_run_curve.py",
        "tests/unit/test_v44_successor_runner.py",
    ),
    "bridge": ("experiments/exploratory/shp-anchor-crosswalk-v1/crosswalk.json",),
    "reporting-export": (
        "publications/reproducibility/README.md",
        "publications/reproducibility/Makefile",
        "src/ic_study/analysis/detection_v4_report.py",
        "src/ic_study/analysis/v4_report_export.py",
        "src/ic_study/analysis/v4_exploratory_export.py",
        "src/ic_study/analysis/v4_public_aggregates.py",
        "publications/reproducibility/verify_short_path.py",
        "src/ic_study/analysis/v4_manuscript_assembly.py",
        "src/ic_study/analysis/v4_manuscript_assembly_derive.py",
        "src/ic_study/analysis/v4_manuscript_assembly_facts.py",
        "src/ic_study/analysis/v4_manuscript_assembly_rules.json",
        "src/ic_study/analysis/v4_manuscript_assembly_facts.schema.json",
        "publications/jcss-manuscript/pipeline/ASSEMBLY.md",
        "publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells.tex",
        "publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells-abstract.md",
        "publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex",
        "publications/jcss-manuscript/pipeline/drafts/2026-09-30/exploratory-results-shells.tex",
    ),
}
REPORT_OUTPUTS = (
    *(
        f"report/{name}.{extension}"
        for name in (
            "T1_a_star_grid",
            "T1s_a_star_all_units",
            "T3_gate_summary",
            "T4_inventory",
        )
        for extension in ("csv", "tex")
    ),
    *(
        f"report/{name}.{extension}"
        for name in (
            "F1_a_star_by_family",
            "F2_auc_profiles_A",
            "F2_auc_profiles_B",
            "F2_auc_profiles_C",
            "F2_auc_profiles_D",
            "F2_auc_profiles_E",
            "F3_exploratory_family_offsets_vs_B",
            "F4_gate_diagnostics",
            "F5_inventory_status",
            "F6_a_star_shp_anchor",
        )
        for extension in ("pdf", "png")
    ),
)
RELEASE_ALLOWLIST = frozenset(
    {
        "released-curves.json",
        "release-record.json",
        "v4-allocation.json",
        "G1c-aggregate-successor.json",
        "shp-aggregate-successor-1.json",
        "x1a.json",
        "x1b.json",
        "x2.json",
        "x3.json",
        "x4.json",
        "x5.json",
        "x6.json",
        "x7.json",
        "legacy-x5.json",
        "legacy-x7.json",
        "comparisons.json",
        "result-values.json",
        "result-catalog.json",
        "public-aggregates.json",
        "expected-hashes.json",
        "owner-facts.json",
        "assembly-facts.json",
        "assembly-record.json",
        "report/manifest.json",
        *REPORT_OUTPUTS,
    }
)
SYNTHETIC_RELEASE_ALLOWLIST = frozenset(
    str(Path(name).with_name(Path(name).stem + "_synthetic" + Path(name).suffix))
    for name in REPORT_OUTPUTS
)
MODES = ("source-only", "approved-release", "synthetic")
PLAN_SCHEMA = "ic-release-plan-v3"
MANIFEST_SCHEMA = "ic-release-manifest-v2"
RULES_SCHEMA = "ic-redaction-rules-v1"
LICENSE = "MIT"
LICENSE_STATES = (LICENSE, "metadata-only")
WITHHELD_REASONS = (
    "excluded-by-decision",
    "private-address",
    "private-host-name",
    "absolute-home-path",
    "non-allowed-email",
    "access-credential",
    "coordination-path",
)
PLACEHOLDERS = {
    "private-address": b"[private-address]",
    "private-host-name": b"[private-host]",
    "absolute-home-path": b"[home]",
    "non-allowed-email": b"[private-email]",
    "access-credential": b"[credential]",
    "coordination-path": b"[coordination-dir]",
}
CODE_FORM = (b'Path("', b'Path.home().joinpath("')
REDACTED_FIELDS = {
    "role",
    "path",
    "original_git_blob",
    "original_sha256",
    "redacted_sha256",
    "redacted_bytes",
    "replacements",
}
REDACTION_NOTICE = b"""# Redacted public copies

Each file under redacted/ROLE/PATH is a new public copy of a source that
plan.json withholds for ROLE: the historical file at PATH in that role's
revision, with every private span replaced by the fixed placeholder of its
category. Historical bytes are never edited; sources/ and history/ hold no
redacted bytes.

| Placeholder          | Replaced span                                         |
| -------------------- | ----------------------------------------------------- |
| `[private-host]`     | private host or tailnet name                          |
| `[home]`             | absolute home directory, also in its encoded form     |
| `[coordination-dir]` | private coordination or agent working directory       |
| `[private-email]`    | e-mail address outside the published authors          |
| `[private-address]`  | network address                                       |
| `[credential]`       | key or token                                          |

In Python code, a plan may instead rewrite a home directory that opens a
Path("...") literal as Path.home().joinpath("..."), counted under the home
category, so that a default path still resolves under the user's home.

For each copy, the "redacted" list in plan.json records the original Git blob
identifier and SHA-256, the copy's SHA-256 and size, and the number of
replacements per category; it never records the replaced text. verify checks
each copy's digest and placeholder counts, and checks the original blob
identifier against the role's tree in history.

Copies are for reading. Their bytes differ from the originals, so freeze,
declaration and closure checks use the original SHA-256 recorded in plan.json,
which the canonical clone reproduces with git show REV:PATH. JSON copies still
parse, and Python copies keep the original syntax tree except for the values
of string literals and the Path.home() form above; the builder refuses any
other redaction. A placeholder inside a path literal leaves a relative path
that names no real directory; pass such a location explicitly.
"""
Rule = tuple[str, re.Pattern[bytes], bool]
LICENSE_TEXT = b"""MIT License

Copyright (c) 2026 Davi Abreu da Silveira

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
MAX_BYTES = 128 * 1024 * 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def relative(value: str) -> str:
    path = PurePosixPath(value)
    require(
        bool(value)
        and not path.is_absolute()
        and ".." not in path.parts
        and path.as_posix() == value
        and "\\" not in value
        and not any(ord(c) < 32 for c in value),
        "Unsafe relative path",
    )
    forbid(path)
    return value


def forbid(path: PurePosixPath | Path) -> None:
    for part in path.parts:
        name = part.lower()
        require(
            not (
                name.startswith(("sealed-", "v4-tier-logs", "v4-gate-logs"))
                or name in {"restricted", ".env", ".ssh", ".aws", "secrets"}
            ),
            "Forbidden path",
        )


def reject_symlink_path(path: Path) -> None:
    for component in (path, *path.parents):
        require(not component.is_symlink(), "Symlink is not permitted")


def confined(root: Path, name: str) -> Path:
    relative(name)
    forbid(root)
    reject_symlink_path(root)
    require(root.is_dir() and not root.is_symlink(), "Root must be a real directory")
    base = root.resolve()
    path = root / name
    for component in (path, *path.parents):
        require(not component.is_symlink(), "Symlink is not permitted")
        if component == root:
            break
    require(path.resolve().is_relative_to(base), "Path escapes root")
    return path


def read_file(path: Path) -> bytes:
    forbid(path)
    reject_symlink_path(path)
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode), "Expected regular file")
    require(info.st_size <= MAX_BYTES, "File exceeds byte limit")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        require(
            (info.st_dev, info.st_ino) == (opened.st_dev, opened.st_ino),
            "File changed before read",
        )
        content = stream.read(MAX_BYTES + 1)
    require(len(content) <= MAX_BYTES, "File exceeds byte limit")
    return content


def json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def json_object(content: bytes) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result

    def invalid(value: str) -> None:
        raise ValueError(f"Invalid JSON constant: {value}")

    value = json.loads(content, object_pairs_hook=pairs, parse_constant=invalid)
    require(isinstance(value, dict), "Expected JSON object")
    return dict(value)


def git(repository: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    forbid(repository)
    reject_symlink_path(repository)
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env.update(
        GIT_NO_LAZY_FETCH="1",
        GIT_TERMINAL_PROMPT="0",
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=os.devnull,
    )
    result = subprocess.run(
        ["git", "-C", str(repository), *args],
        env=env,
        capture_output=True,
        check=False,
        input=input_bytes,
    )
    require(result.returncode == 0, "Required local Git revision/object missing")
    return result.stdout


def oid(value: str) -> bool:
    return re.fullmatch(r"[0-9a-f]{40}", value) is not None


def allow_source(path: str) -> bool:
    return path.startswith(PREFIX) and path.removeprefix(PREFIX) in (
        *ENVIRONMENT,
        *SOURCE_ALLOWLIST,
        *PUBLIC_ALLOWLIST,
    )


def sha256_value(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def validate_plan(plan: dict[str, Any]) -> None:
    require(
        set(plan) == {"schema", "mode", "revisions", "files", "withheld", "redacted"},
        "Unknown or missing plan fields",
    )
    require(
        plan["schema"] == PLAN_SCHEMA and plan["mode"] in MODES,
        "Invalid plan schema/mode",
    )
    revisions = plan["revisions"]
    require(
        isinstance(revisions, dict) and set(revisions) == set(ROLES),
        "Required revision roles missing",
    )
    require(
        all(isinstance(v, str) and oid(v) for v in revisions.values()),
        "Use full Git commit revisions",
    )
    if plan["mode"] != "synthetic":
        require(
            all(revisions[k] == v for k, v in PINNED.items()),
            "Pinned historical revision mismatch",
        )
    require(
        isinstance(plan["files"], list) and bool(plan["files"]), "No files selected"
    )
    selected: set[tuple[str, str, str]] = set()
    for entry in plan["files"]:
        require(
            isinstance(entry, dict)
            and set(entry)
            == {
                "root",
                "role",
                "path",
                "sha256",
                "bytes",
                "license_status",
            },
            "Invalid file entry fields",
        )
        name = relative(entry["path"])
        require(
            isinstance(entry["sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is not None,
            "Expected SHA-256",
        )
        require(
            type(entry["bytes"]) is int and 0 <= entry["bytes"] <= MAX_BYTES,
            "Invalid byte size",
        )
        require(entry["license_status"] in LICENSE_STATES, "Invalid license status")
        root, role = entry["root"], entry["role"]
        if root == "repository":
            require(role in ROLES and allow_source(name), "Source outside allowlist")
        else:
            require(
                root == "release"
                and role == "approved-artifact"
                and (
                    name in RELEASE_ALLOWLIST
                    or (
                        plan["mode"] == "synthetic"
                        and name in SYNTHETIC_RELEASE_ALLOWLIST
                    )
                )
                and plan["mode"] != "source-only",
                "Artifact outside allowlist",
            )
        key = (root, role, name)
        require(key not in selected, "Duplicate file selection")
        selected.add(key)
    require(isinstance(plan["withheld"], list), "Invalid withheld list")
    withheld: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in plan["withheld"]:
        require(
            isinstance(entry, dict)
            and set(entry)
            == {"role", "path", "git_blob", "sha256", "bytes", "reasons"},
            "Invalid withheld entry fields",
        )
        name = relative(entry["path"])
        require(
            entry["role"] in ROLES and allow_source(name),
            "Withheld source outside allowlist",
        )
        require(
            isinstance(entry["git_blob"], str)
            and oid(entry["git_blob"])
            and isinstance(entry["sha256"], str)
            and re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is not None
            and type(entry["bytes"]) is int
            and 0 <= entry["bytes"] <= MAX_BYTES,
            "Invalid withheld identity",
        )
        reasons = entry["reasons"]
        require(
            isinstance(reasons, list)
            and bool(reasons)
            and reasons == sorted(set(reasons))
            and all(reason in WITHHELD_REASONS for reason in reasons),
            "Invalid withholding reasons",
        )
        source = (str(entry["role"]), name)
        require(
            source not in withheld and ("repository", *source) not in selected,
            "Withheld source is duplicated or selected",
        )
        withheld[source] = entry
    require(isinstance(plan["redacted"], list), "Invalid redacted list")
    redacted: set[tuple[str, str]] = set()
    for entry in plan["redacted"]:
        require(
            isinstance(entry, dict) and set(entry) == REDACTED_FIELDS,
            "Invalid redacted entry fields",
        )
        source = (entry["role"], relative(entry["path"]))
        original = withheld.get(source)
        require(
            original is not None
            and source not in redacted
            and entry["original_git_blob"] == original["git_blob"]
            and entry["original_sha256"] == original["sha256"],
            "Redacted copy is not bound to one withheld source",
        )
        assert original is not None
        require(
            "excluded-by-decision" not in original["reasons"],
            "A source excluded by decision cannot be redacted",
        )
        require(
            sha256_value(entry["redacted_sha256"])
            and type(entry["redacted_bytes"]) is int
            and 0 <= entry["redacted_bytes"] <= MAX_BYTES,
            "Invalid redacted identity",
        )
        replacements = entry["replacements"]
        require(
            isinstance(replacements, dict)
            and all(
                category in PLACEHOLDERS
                and category in original["reasons"]
                and type(count) is int
                and count > 0
                for category, count in replacements.items()
            ),
            "Invalid redaction counts",
        )
        redacted.add(source)
    for role in ROLES:
        require(
            all(
                ("repository", role, PREFIX + name) in selected
                for name in (*ENVIRONMENT, "src/ic_study/__init__.py")
            ),
            f"Incomplete source/environment selection: {role}",
        )
        if plan["mode"] != "synthetic":
            require(
                all(
                    ("repository", role, PREFIX + name) in selected
                    or (role, PREFIX + name) in withheld
                    for name in REQUIRED[role]
                ),
                f"Incomplete source/environment selection: {role}",
            )


def snapshot(
    repository: Path,
    revision: str,
    candidates: list[str],
    published: set[str] | None = None,
) -> tuple[dict[str, tuple[bytes, str]], dict[str, bytes]]:
    """Return candidate contents and the commit, tree and blob objects to publish.

    Blobs are published only for ``published`` names (default: every candidate);
    trees along every candidate path keep the identity of withheld blobs.
    """
    require(oid(revision), "Use full Git commit revisions")
    listing = git(repository, "ls-tree", "-r", "-t", "-z", revision, "--", *candidates)
    entries = {}
    ids = {revision, revision + "^{tree}"}
    for line in listing.split(b"\0"):
        if not line:
            continue
        metadata, raw_name = line.split(b"\t", 1)
        mode, kind, object_id = metadata.decode().split()
        name = raw_name.decode()
        if kind == "tree":
            ids.add(object_id)
        else:
            require(
                name in candidates and mode in {"100644", "100755"} and kind == "blob",
                "Source must be regular; symlinks are forbidden",
            )
            entries[name] = object_id
    names = set(entries) if published is None else published & set(entries)
    shown = {entries[name] for name in names}
    hidden = set(entries.values()) - shown
    requested = sorted(ids | set(entries.values()))
    batch = io.BytesIO(
        git(
            repository,
            "cat-file",
            "--batch",
            input_bytes=("\n".join(requested) + "\n").encode(),
        )
    )
    objects = {}
    contents = {}
    for request in requested:
        header = batch.readline().decode().strip().split()
        require(len(header) == 3, "Required local Git revision/object missing")
        object_id, kind, size = header
        require(
            kind in {"commit", "tree", "blob"} and int(size) <= MAX_BYTES,
            "Unsupported Git object",
        )
        require(request != revision or kind == "commit", "Revision is not a commit")
        content = batch.read(int(size))
        require(
            len(content) == int(size) and batch.read(1) == b"\n",
            "Truncated Git object batch",
        )
        raw = f"{kind} {len(content)}\0".encode() + content
        require(
            hashlib.sha1(raw).hexdigest() == object_id, "Git object identity mismatch"
        )
        if object_id not in hidden:
            objects[object_id] = raw
        contents[object_id] = content
    return {
        name: (contents[object_id], object_id) for name, object_id in entries.items()
    }, objects


def redaction_rules(path: Path) -> list[Rule]:
    """Load the private span patterns; they never enter a plan or bundle."""
    record = json_object(read_file(path))
    rules = record.get("rules")
    require(
        set(record) == {"schema", "rules"}
        and record["schema"] == RULES_SCHEMA
        and isinstance(rules, list)
        and bool(rules),
        "Invalid redaction rules",
    )
    assert isinstance(rules, list)
    loaded = []
    for rule in rules:
        require(
            isinstance(rule, dict)
            and set(rule) - {"form"} == {"category", "pattern"}
            and rule["category"] in PLACEHOLDERS
            and isinstance(rule["pattern"], str)
            and bool(rule["pattern"])
            and rule.get("form", "placeholder") in {"placeholder", "code"}
            and (
                rule.get("form") != "code" or rule["category"] == "absolute-home-path"
            ),
            "Invalid redaction rule",
        )
        try:
            pattern = re.compile(rule["pattern"].encode())
        except re.error:
            raise ValueError("Invalid redaction pattern") from None
        loaded.append((str(rule["category"]), pattern, rule.get("form") == "code"))
    return loaded


def placeholder_counts(content: bytes) -> dict[str, int]:
    """Count each category's fixed forms; the Path.home() form counts as home."""
    counts = {
        category: content.count(token) for category, token in PLACEHOLDERS.items()
    }
    counts["absolute-home-path"] += content.count(CODE_FORM[1])
    return {category: count for category, count in sorted(counts.items()) if count}


def redact_spans(
    content: bytes, rules: list[Rule], python: bool
) -> tuple[bytes, dict[str, int]]:
    """Replace each private span by its category's fixed form in one pass.

    Code-form rules apply only to Python sources, where a span ``Path("HOME/``
    becomes ``Path.home().joinpath("``.
    """
    require(
        not placeholder_counts(content),
        "Original already contains a redaction placeholder",
    )
    active = [rule for rule in rules if python or not rule[2]]
    output = bytearray()
    counts: dict[str, int] = {}
    position = 0
    while True:
        found = [
            (match.start(), index, match)
            for index, (_, pattern, _) in enumerate(active)
            if (match := pattern.search(content, position))
        ]
        if not found:
            break
        start, index, match = min(found, key=lambda item: item[:2])
        require(match.end() > start, "Empty redaction match")
        category, _, code = active[index]
        span, before = match.group(0), content[start - 1 : start]
        require(
            not code
            or (
                span.startswith(CODE_FORM[0])
                and span.endswith(b"/")
                and not (before.isalnum() or before == b"_")
            ),
            "Code form span must open a Path literal and end with a slash",
        )
        output += content[position:start]
        output += CODE_FORM[1] if code else PLACEHOLDERS[category]
        counts[category] = counts.get(category, 0) + 1
        position = match.end()
    copy = bytes(output + content[position:])
    require(
        not any(pattern.search(copy) for _, pattern, _ in rules),
        "Redaction left a private span",
    )
    return copy, dict(sorted(counts.items()))


def code_shape(source: bytes) -> str:
    """Syntax tree of Python source with string and bytes literal values blanked."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str | bytes):
            node.value = ""
    return ast.dump(tree)


def redacted_copy(
    role: str, name: str, content: bytes, blob: str, rules: list[Rule]
) -> tuple[dict[str, Any], bytes]:
    """Redact one withheld source; code and JSON copies must still parse.

    A Python copy must keep the original syntax tree apart from literal values
    and the Path.home() form, so no placeholder can land in executable code.
    """
    python = name.endswith(".py")
    copy, counts = redact_spans(content, rules, python)
    same = True
    try:
        if python:
            compile(copy, name, "exec", dont_inherit=True)
            same = code_shape(content) == code_shape(
                copy.replace(CODE_FORM[1], CODE_FORM[0])
            )
        elif name.endswith(".json"):
            json.loads(copy)
    except (SyntaxError, ValueError):
        raise ValueError("Redacted copy no longer parses") from None
    require(same, "Redaction changed code outside string literals")
    record = {
        "role": role,
        "path": name,
        "original_git_blob": blob,
        "original_sha256": digest(content),
        "redacted_sha256": digest(copy),
        "redacted_bytes": len(copy),
        "replacements": counts,
    }
    return record, copy


def plan_sources(
    repository: Path,
    mode: str,
    revisions: dict[str, str],
    withhold: dict[str, list[str]] | None = None,
    redact: dict[str, list[str]] | None = None,
    rules: list[Rule] | None = None,
) -> dict[str, Any]:
    redact = redact or {}
    withhold = withhold or {}
    require(not set(withhold) & set(redact), "Duplicate withheld path")
    covered = {rule[0] for rule in rules or []}
    require(
        all(set(reasons) <= covered for reasons in redact.values()),
        "Redaction rules required for every declared reason",
    )
    hidden = withhold | redact
    files, withheld, redacted = [], [], []
    candidates = sorted(
        {
            PREFIX + name
            for name in (
                *ENVIRONMENT,
                *SOURCE_ALLOWLIST,
                *PUBLIC_ALLOWLIST,
            )
        }
    )
    snapshots = {
        revision: snapshot(repository, revision, candidates)[0]
        for revision in set(revisions.values())
    }
    for role, revision in revisions.items():
        for name, (content, blob) in sorted(snapshots[revision].items()):
            if name in hidden:
                withheld.append(
                    {
                        "role": role,
                        "path": name,
                        "git_blob": blob,
                        "sha256": digest(content),
                        "bytes": len(content),
                        "reasons": sorted(set(hidden[name])),
                    }
                )
                if name in redact:
                    assert rules is not None
                    redacted.append(redacted_copy(role, name, content, blob, rules)[0])
                continue
            files.append(
                {
                    "root": "repository",
                    "role": role,
                    "path": name,
                    "sha256": digest(content),
                    "bytes": len(content),
                    "license_status": LICENSE,
                }
            )
    require(
        set(hidden) <= {entry["path"] for entry in withheld},
        "Withheld source absent from every revision",
    )
    plan = {
        "schema": PLAN_SCHEMA,
        "mode": mode,
        "revisions": revisions,
        "files": files,
        "withheld": withheld,
        "redacted": redacted,
    }
    validate_plan(plan)
    return plan


def write_new(path: Path, content: bytes) -> None:
    forbid(path)
    reject_symlink_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(content)


def check_release_pair(stage: Path, plan: dict[str, Any]) -> None:
    names = {entry["path"] for entry in plan["files"] if entry["root"] == "release"}
    pair = {"release-record.json", "released-curves.json"}
    require(not (names & pair) or pair.issubset(names), "Release pair incomplete")
    if pair.issubset(names):
        receipt = json_object(read_file(stage / "artifacts/release-record.json"))
        require(
            receipt.get("released_curves_sha256")
            == digest(read_file(stage / "artifacts/released-curves.json")),
            "Release receipt hash mismatch",
        )
        require(
            receipt.get("condition") in {"inventory-complete", "declared-close"},
            "Release condition missing",
        )
        require(isinstance(receipt.get("released_utc"), str), "Release time missing")
        synthetic = plan["mode"] == "synthetic"
        role = "reporting-export" if synthetic else "release-wrapper"
        name = (
            "src/ic_study/analysis/v4_report_synthetic.py"
            if synthetic
            else V4 + "release_on_completion.py"
        )
        require(
            any(
                entry["root"] == "repository"
                and entry["role"] == role
                and entry["path"] == PREFIX + name
                for entry in plan["files"]
            ),
            "Release producer source is not selected",
        )
        script = stage / "sources" / role / PREFIX / name
        require(
            receipt.get("script_sha256") == digest(read_file(script)),
            "Synthetic release generator differs from selected source"
            if synthetic
            else "Executed release wrapper differs from selected source",
        )


def source_digest(bundle: Path, plan: dict[str, Any], role: str, name: str) -> str:
    """Digest of a role's source: bundled bytes, or the withheld record."""
    for entry in plan["withheld"]:
        if entry["role"] == role and entry["path"] == PREFIX + name:
            return str(entry["sha256"])
    return digest(read_file(confined(bundle / "sources" / role / PREFIX, name)))


def check_successor(bundle: Path, plan: dict[str, Any]) -> None:
    """Bind amendment v4.4 to its runner, tests and the confirmatory freeze."""
    record = json_object(
        read_file(bundle / "sources/v44-successor" / PREFIX / V44 / "freeze-v44.json")
    )
    runner = record["successor_runner"]
    tests = record["tests"]
    base = record["base_freeze"]
    successor = "v44-successor"
    require(
        record.get("status") == "frozen"
        and record["amendment_sha256"]
        == source_digest(bundle, plan, successor, V44 + "AMENDMENT-v4.4.md")
        and runner["path"] == V44 + "v44_run_curve.py"
        and runner["sha256"] == source_digest(bundle, plan, successor, runner["path"])
        and tests["sha256"] == source_digest(bundle, plan, successor, tests["path"])
        and base["sha256"]
        == source_digest(bundle, plan, "confirmatory", V4 + "freeze-v4.json")
        and record["frozen_runner_sha256"]
        == source_digest(bundle, plan, "confirmatory", V4 + "run_curve.py"),
        "Amendment v4.4 successor binding mismatch",
    )


def environments(stage: Path, plan: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for role in ROLES:
        study = stage / "sources" / role / PREFIX
        lock = read_file(study / "uv.lock")
        parsed = tomllib.loads(lock.decode())
        packages: dict[str, str] = {}
        for package in parsed.get("package", []):
            if "version" in package:
                name, version = package["name"], package["version"]
                require(
                    name not in packages or packages[name] == version,
                    "Conflicting locked versions for one package",
                )
                packages[name] = version
        python_version = read_file(study / ".python-version").decode().strip()
        require(bool(python_version), "Python version missing")
        result[role] = {
            "python": python_version,
            "lock_sha256": digest(lock),
            "pyproject_sha256": digest(read_file(study / "pyproject.toml")),
            "packages": packages,
        }
    if plan["mode"] != "synthetic":
        study = stage / "sources/confirmatory" / PREFIX
        freeze = json_object(read_file(study / V4 / "freeze-v4.json"))
        require(freeze.get("shards") == 8, "Frozen shard count mismatch")
        for name, expected in freeze["code"].items():
            require(
                source_digest(stage, plan, "confirmatory", name) == expected,
                "Frozen code/lock closure mismatch",
            )
        result["confirmatory"]["frozen_environment"] = freeze["environment"]
        check_successor(stage, plan)
    return result


def reproduce_text() -> bytes:
    return b"""# Reproduction entry points

From this directory, with Python 3.12 (no dependencies or network required):

```sh
python3.12 verify_ic_release.py verify --bundle .
```

Check the printed manifest digest against the ic-release-manifest.sha256 file
published beside this bundle; --manifest-sha256 DIGEST enforces it. LICENSE
(MIT) covers the study's own material in this bundle. No third-party material
is redistributed. No synthetic approval authorizes scientific work. synthetic
mode is artificial.

plan.json lists every selected file with its role, original revision, size,
digest and license, and every withheld file with its Git blob identifier,
digest and reason category. Files are withheld when their historical bytes
contain private details such as host names, home paths, e-mail addresses or
coordination paths; historical bytes are never edited. A withheld file may
have a new redacted public copy under redacted/ROLE/PATH, bound in plan.json to
the original blob and digest and described in redacted/README.md.
ic-release-manifest.json records dependency versions and inventories every
bundle file.
sources/v44-successor holds amendment v4.4, whose freeze record binds the
successor tier runner, its tests and the confirmatory freeze.

Historical Git queries work offline on selected paths, for example:

```sh
git -C history show refs/repro/confirmatory:studies/ic-2026-2027/uv.lock
git -C history show refs/repro/reporting-export:studies/ic-2026-2027/uv.lock
```

history is a read-only object projection, not a checkout or complete Git clone.
Each role's commit and the trees along its selected and withheld paths keep
their original identities, so a withheld file's blob identifier is bound to the
commit. Only selected blobs are present; withheld and unselected paths and
ancestry operations fail. Set no Git alternates or remotes. Each sources/ROLE
contains its own study, lock and code. For pilot validators requiring a
complete checkout, or for withheld files, use the canonical full clone at the
recorded revision; never substitute a different revision, a redacted copy or
a different source hash.

Read sources/reporting-export/studies/ic-2026-2027/publications/reproducibility/
README.md for reporting/export CLIs and prerequisites. No command here launches
gates, tiers, release, a model or analysis. Dependencies need an existing local
wheel cache for offline uv sync --locked --offline; wheel bytes are not included.

The current reporting gate reader requires sealed evidence. A public bundle
without that evidence cannot claim full reporting replay. Do not synthesize
missing tasks, approvals or seals. Only the coordinator may run the authorized
chain and select public release artifacts. The source LaTeX package is separate.
Replay, regeneration, technical verification and scientific acceptance remain
distinct; only packaging integrity was performed by this tool.
"""


def inventory(stage: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": p.relative_to(stage).as_posix(),
            "sha256": digest(read_file(p)),
            "bytes": p.stat().st_size,
        }
        for p in sorted(stage.rglob("*"))
        if p.is_file()
    ]


def check_history(
    bundle: Path,
    plan: dict[str, Any],
    names: set[str],
) -> None:
    objects = {}
    for name in names:
        require(
            re.fullmatch(r"history/\.git/objects/[0-9a-f]{2}/[0-9a-f]{38}", name)
            is not None,
            "Inventory file outside history allowlist",
        )
        decoder = zlib.decompressobj()
        raw = decoder.decompress(read_file(confined(bundle, name)), MAX_BYTES + 1)
        require(
            decoder.eof and len(raw) <= MAX_BYTES and not decoder.unused_data,
            "Invalid or oversized history object",
        )
        object_id = name.split("/")[-2] + name.split("/")[-1]
        require(
            hashlib.sha1(raw).hexdigest() == object_id, "History object hash mismatch"
        )
        header, body = raw.split(b"\0", 1)
        kind, size = header.decode().split()
        require(
            kind in {"commit", "tree", "blob"} and int(size) == len(body),
            "Invalid history object header",
        )
        objects[object_id] = (kind, body)
    expected = set()

    def get(object_id: str, kind: str) -> bytes:
        require(
            object_id in objects and objects[object_id][0] == kind,
            "Required history revision/tree/blob missing",
        )
        expected.add(object_id)
        return objects[object_id][1]

    def child(tree: str, name: str) -> tuple[str, str]:
        content = get(tree, "tree")
        offset = 0
        while offset < len(content):
            end = content.index(b"\0", offset)
            mode, entry_name = content[offset:end].split(b" ", 1)
            object_id = content[end + 1 : end + 21].hex()
            if entry_name.decode() == name:
                return mode.decode(), object_id
            offset = end + 21
        raise ValueError("Selected path missing in history tree")

    def resolve(role: str, path: str) -> str:
        commit = get(plan["revisions"][role], "commit")
        first = commit.split(b"\n", 1)[0].decode().split()
        require(
            len(first) == 2 and first[0] == "tree" and oid(first[1]),
            "Invalid history commit tree",
        )
        tree = first[1]
        components = PurePosixPath(path).parts
        for component in components[:-1]:
            mode, tree = child(tree, component)
            require(mode == "40000", "History path is not a directory")
        mode, blob = child(tree, components[-1])
        require(mode in {"100644", "100755"}, "History symlink is forbidden")
        return blob

    for entry in plan["files"]:
        if entry["root"] != "repository":
            continue
        content = get(resolve(entry["role"], entry["path"]), "blob")
        require(
            digest(content) == entry["sha256"] and len(content) == entry["bytes"],
            "History blob differs from selection",
        )
    for entry in plan["withheld"]:
        require(
            resolve(entry["role"], entry["path"]) == entry["git_blob"],
            "History tree differs from withheld record",
        )
    require(set(objects) == expected, "Unselected history object")


def build(
    repository: Path,
    plan: dict[str, Any],
    output: Path,
    release_root: Path | None,
    rules: list[Rule] | None = None,
) -> dict[str, Any]:
    require(not output.exists() and not output.is_symlink(), "Output already exists")
    forbid(output)
    reject_symlink_path(output)
    validate_plan(plan)
    require(rules is not None or not plan["redacted"], "Redaction rules required")
    snapshots = {}
    for revision in set(plan["revisions"].values()):
        roles = {role for role, value in plan["revisions"].items() if value == revision}
        selected = {
            entry["path"]
            for entry in plan["files"]
            if entry["root"] == "repository" and entry["role"] in roles
        }
        withheld = [entry for entry in plan["withheld"] if entry["role"] in roles]
        entries, objects = snapshot(
            repository,
            revision,
            sorted(selected | {entry["path"] for entry in withheld}),
            selected,
        )
        for entry in withheld:
            require(entry["path"] in entries, "Withheld source missing at revision")
            content, blob = entries[entry["path"]]
            require(
                blob == entry["git_blob"]
                and digest(content) == entry["sha256"]
                and len(content) == entry["bytes"],
                "Withheld source identity mismatch",
            )
        snapshots[revision] = (entries, objects)
    copies = {}
    for entry in plan["redacted"]:
        assert rules is not None
        role, name = entry["role"], entry["path"]
        content, blob = snapshots[plan["revisions"][role]][0][name]
        record, copy = redacted_copy(role, name, content, blob, rules)
        require(record == entry, "Redacted copy differs from plan")
        copies[f"redacted/{role}/{name}"] = copy
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ic-release-", dir=output.parent) as tmp:
        stage = Path(tmp)
        history = stage / "history"
        for _, objects in snapshots.values():
            for object_id, raw in objects.items():
                target = history / ".git/objects" / object_id[:2] / object_id[2:]
                if not target.exists():
                    write_new(target, zlib.compress(raw))
        for entry in plan["files"]:
            if entry["root"] == "repository":
                revision = plan["revisions"][entry["role"]]
                require(
                    entry["path"] in snapshots[revision][0],
                    "Required source missing at revision",
                )
                content, _ = snapshots[revision][0][entry["path"]]
                destination = stage / "sources" / entry["role"] / entry["path"]
            else:
                require(
                    release_root is not None, "Explicit approved release root required"
                )
                assert release_root is not None
                content = read_file(confined(release_root, entry["path"]))
                destination = stage / "artifacts" / entry["path"]
            require(
                len(content) == entry["bytes"] and digest(content) == entry["sha256"],
                "Selected file hash/size mismatch",
            )
            write_new(destination, content)
        for name, copy in copies.items():
            write_new(stage / name, copy)
        if copies:
            write_new(stage / "redacted/README.md", REDACTION_NOTICE)
        write_new(
            history / ".git/config",
            b"[core]\nrepositoryformatversion = 0\nbare = false\n",
        )
        write_new(history / ".git/HEAD", b"ref: refs/repro/reporting-export\n")
        for role, revision in plan["revisions"].items():
            write_new(history / ".git/refs/repro" / role, (revision + "\n").encode())
        check_release_pair(stage, plan)
        env = environments(stage, plan)
        write_new(stage / "LICENSE", LICENSE_TEXT)
        write_new(stage / "plan.json", json_bytes(plan))
        write_new(stage / "REPRODUCE.md", reproduce_text())
        write_new(stage / "verify_ic_release.py", read_file(Path(__file__).resolve()))
        write_new(
            stage / "ic-release-manifest.schema.json",
            read_file(Path(__file__).with_name("ic-release-manifest.schema.json")),
        )
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "mode": plan["mode"],
            "revisions": plan["revisions"],
            "environments": env,
            "scientific_acceptance": False,
            "regeneration_performed": False,
            "scientific_replay_performed": False,
            "license_decisions": LICENSE,
            "files": inventory(stage),
        }
        raw = json_bytes(manifest)
        write_new(stage / "ic-release-manifest.json", raw)
        write_new(stage / "ic-release-manifest.sha256", (digest(raw) + "\n").encode())
        result = verify(stage)
        output.mkdir()
        try:
            for child in stage.iterdir():
                child.rename(output / child.name)
        except BaseException:
            shutil.rmtree(output)
            raise
        return result


def verify(bundle: Path, expected_digest: str | None = None) -> dict[str, Any]:
    manifest_raw = read_file(confined(bundle, "ic-release-manifest.json"))
    manifest_digest = digest(manifest_raw)
    local_digest = (
        read_file(confined(bundle, "ic-release-manifest.sha256")).decode().strip()
    )
    require(manifest_digest == local_digest, "Manifest hash mismatch")
    require(
        expected_digest is None or manifest_digest == expected_digest,
        "External manifest hash mismatch",
    )
    manifest = json_object(manifest_raw)
    require(
        set(manifest)
        == {
            "schema",
            "mode",
            "revisions",
            "environments",
            "files",
            "scientific_acceptance",
            "regeneration_performed",
            "scientific_replay_performed",
            "license_decisions",
        },
        "Invalid manifest fields",
    )
    require(
        manifest["schema"] == MANIFEST_SCHEMA
        and manifest["scientific_acceptance"] is False
        and manifest["regeneration_performed"] is False
        and manifest["scientific_replay_performed"] is False
        and manifest["license_decisions"] == LICENSE,
        "Invalid packaging-only status",
    )
    selected: set[str] = set()
    for entry in manifest["files"]:
        require(set(entry) == {"path", "sha256", "bytes"}, "Invalid inventory entry")
        name = relative(entry["path"])
        require(name not in selected, "Duplicate inventory path")
        selected.add(name)
        content = read_file(confined(bundle, name))
        require(
            len(content) == entry["bytes"] and digest(content) == entry["sha256"],
            "Bundle file hash/size mismatch",
        )
    allowed = selected | {"ic-release-manifest.json", "ic-release-manifest.sha256"}
    for path in bundle.rglob("*"):
        require(not path.is_symlink(), "Symlink in bundle")
        forbid(path)
        if not path.is_dir():
            require(
                path.relative_to(bundle).as_posix() in allowed, "Unexpected bundle file"
            )
    plan = json_object(read_file(confined(bundle, "plan.json")))
    validate_plan(plan)
    require(
        manifest["revisions"] == plan["revisions"] and manifest["mode"] == plan["mode"],
        "Manifest/plan revision mismatch",
    )
    permitted = {
        "LICENSE",
        "plan.json",
        "REPRODUCE.md",
        "verify_ic_release.py",
        "ic-release-manifest.schema.json",
        "history/.git/config",
        "history/.git/HEAD",
        *("history/.git/refs/repro/" + r for r in ROLES),
    }
    for entry in plan["files"]:
        name = (
            f"sources/{entry['role']}/{entry['path']}"
            if entry["root"] == "repository"
            else f"artifacts/{entry['path']}"
        )
        permitted.add(name)
        content = read_file(confined(bundle, name))
        require(
            digest(content) == entry["sha256"] and len(content) == entry["bytes"],
            "Bundled selection differs from plan",
        )
    for entry in plan["redacted"]:
        name = f"redacted/{entry['role']}/{entry['path']}"
        permitted.add(name)
        content = read_file(confined(bundle, name))
        require(
            digest(content) == entry["redacted_sha256"]
            and len(content) == entry["redacted_bytes"],
            "Bundled redaction differs from plan",
        )
        require(
            placeholder_counts(content) == entry["replacements"],
            "Redaction placeholders differ from plan",
        )
    if plan["redacted"]:
        permitted.add("redacted/README.md")
        require(
            read_file(confined(bundle, "redacted/README.md")) == REDACTION_NOTICE,
            "Unexpected redaction notice",
        )
    require(permitted.issubset(selected), "Required bundle file missing from inventory")
    require(
        read_file(confined(bundle, "LICENSE")) == LICENSE_TEXT,
        "Unexpected license text",
    )
    check_history(bundle, plan, selected - permitted)
    require(
        read_file(bundle / "history/.git/config")
        == b"[core]\nrepositoryformatversion = 0\nbare = false\n",
        "Unexpected history configuration",
    )
    require(
        read_file(bundle / "history/.git/HEAD")
        == b"ref: refs/repro/reporting-export\n",
        "Unexpected history HEAD",
    )
    for role, revision in plan["revisions"].items():
        require(
            read_file(confined(bundle, "history/.git/refs/repro/" + role))
            .decode()
            .strip()
            == revision,
            "Historical revision ref mismatch",
        )
        require(
            (bundle / "history/.git/objects" / revision[:2] / revision[2:]).is_file(),
            "Historical revision missing",
        )
    require(
        environments(bundle, plan) == manifest["environments"],
        "Environment record mismatch",
    )
    check_release_pair(bundle, plan)
    return {
        "status": "integrity_verified",
        "manifest_sha256": manifest_digest,
        "files": len(selected),
        "mode": plan["mode"],
        "scientific_acceptance": False,
        "scientific_replay_performed": False,
        "regeneration_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser(
        "plan", help="Select code only from explicit allowlist"
    )
    prepare.add_argument("--repository", type=Path, required=True)
    prepare.add_argument("--mode", choices=MODES, default="source-only")
    prepare.add_argument("--revision", action="append", default=[])
    prepare.add_argument(
        "--withhold",
        action="append",
        default=[],
        metavar="PATH=REASON[,REASON]",
        help="Record an allowlisted path in every role without publishing it",
    )
    prepare.add_argument(
        "--redact",
        action="append",
        default=[],
        metavar="PATH=REASON[,REASON]",
        help="Withhold a path like --withhold and publish a redacted copy",
    )
    prepare.add_argument(
        "--redaction-rules",
        type=Path,
        help="Private span patterns; required with --redact, never published",
    )
    prepare.add_argument("--output", type=Path, required=True)
    package = commands.add_parser(
        "build", help="Package exactly the hash-bound selection"
    )
    package.add_argument("--repository", type=Path, required=True)
    package.add_argument("--plan", type=Path, required=True)
    package.add_argument("--release-root", type=Path)
    package.add_argument(
        "--redaction-rules",
        type=Path,
        help="The plan's private span patterns; required when it redacts",
    )
    package.add_argument("--output", type=Path, required=True)
    check = commands.add_parser(
        "verify", help="Verify an existing bundle without network"
    )
    check.add_argument("--bundle", type=Path, required=True)
    check.add_argument("--manifest-sha256")
    args = parser.parse_args(argv)
    try:
        rules = (
            redaction_rules(args.redaction_rules)
            if args.command != "verify" and args.redaction_rules
            else None
        )
        if args.command == "plan":
            revisions = {} if args.mode == "synthetic" else dict(PINNED)
            seen = set()
            for item in args.revision:
                role, revision = item.split("=", 1)
                require(
                    role in ROLES and role not in seen,
                    "Invalid/duplicate revision role",
                )
                seen.add(role)
                revisions[role] = revision
            require(set(revisions) == set(ROLES), "Supply all required revision roles")
            withhold: dict[str, list[str]] = {}
            redact: dict[str, list[str]] = {}
            for decision, items in ((withhold, args.withhold), (redact, args.redact)):
                for item in items:
                    path, reasons = item.split("=", 1)
                    require(
                        path not in withhold and path not in redact,
                        "Duplicate withheld path",
                    )
                    decision[path] = reasons.split(",")
            plan = plan_sources(
                args.repository, args.mode, revisions, withhold, redact, rules
            )
            write_new(args.output, json_bytes(plan))
            result = {
                "status": "source_selection_prepared",
                "files": len(plan["files"]),
                "withheld": len(plan["withheld"]),
                "redacted": len(plan["redacted"]),
            }
        elif args.command == "build":
            result = build(
                args.repository,
                json_object(read_file(args.plan)),
                args.output,
                args.release_root,
                rules,
            )
        else:
            result = verify(args.bundle, args.manifest_sha256)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, zlib.error) as error:
        print(json.dumps({"status": "invalid", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
