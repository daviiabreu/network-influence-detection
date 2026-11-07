"""Compare the three affected deterministic fixture catalogs with pre-T41 bytes."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

STUDY = Path(__file__).resolve().parents[4]
BEFORE = Path("/private/tmp/claude-501/pre-t41-6fce4b50/studies/ic-2026-2027")
CASES = [("gate", False), ("gate+exploratory", False), ("gate+exploratory", True)]


def encoded(obj: Any) -> bytes:
    return (
        json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    ).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def capture(study: Path, output: Path) -> None:
    if study not in {STUDY, BEFORE}:
        raise ValueError("Only the named public checkouts are permitted")
    sys.path[:0] = [str(study / "src"), str(study)]
    path = study / "tests/unit/test_v4_exploratory_export.py"
    spec = importlib.util.spec_from_file_location("verdict_catalog_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = []
    expected = (
        module.test_x1b_presentation_preserves_pre_change_catalog_bytes.pytestmark[
            0
        ].args[1]
    )
    for scenario, with_x1b in CASES:
        key = scenario + ("-x1b" if with_x1b else "")
        directory = output / key
        directory.mkdir(parents=True)
        values = module.synthetic_catalog(directory, scenario, with_x1b)
        raw = encoded(values)
        (directory / "values.json").write_bytes(raw)
        rows.append(
            {
                "case": key,
                "digest": digest(raw),
                "expected": next(
                    row[2] for row in expected if row[:2] == (scenario, with_x1b)
                ),
                "values": values,
            }
        )
    (output / "capture.json").write_bytes(encoded(rows))


def prove(output: Path) -> None:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=BEFORE,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=BEFORE,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if not revision.startswith("6fce4b50") or status:
        raise ValueError("Pre-T41 worktree must be clean at 6fce4b50")
    root = Path(tempfile.mkdtemp(prefix="t41b-verdict-proof-", dir="/private/tmp"))
    captures = []
    for label, study in (("before", BEFORE), ("after", STUDY)):
        directory = root / label
        directory.mkdir()
        env = os.environ | {"PYTHONPATH": str(study / "src") + os.pathsep + str(study)}
        subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--capture",
                str(study),
                "--output",
                str(directory),
            ],
            cwd=study,
            env=env,
            check=True,
        )
        captures.append(json.loads((directory / "capture.json").read_text()))
    ids = {
        f"v4.gate.{stage}.verdict.{kind}"
        for stage in ("G0", "G1b", "G1c", "G2", "G2c")
        for kind in ("complete", "approved", "stop")
    }
    proofs = []
    for before, after in zip(*captures, strict=True):
        old, new = before["values"], after["values"]
        projected = {k: v for k, v in new.items() if k not in ids}
        if (
            new.keys() - old.keys() != ids
            or before["digest"] != before["expected"]
            or encoded(old) != encoded(projected)
        ):
            raise ValueError(
                "Additional catalog change; do not update digest: " + before["case"]
            )
        proofs.append(
            {
                "case": before["case"],
                "old_ids": len(old),
                "added_values": {k: new[k] for k in sorted(ids)},
                "old_sha256": before["digest"],
                "new_sha256": after["digest"],
                "projected_sha256": digest(encoded(projected)),
                "old_ids_bytes_equal": True,
                "old_expected_digest_matches": True,
            }
        )
    output.write_bytes(
        encoded(
            {
                "schema": "ic-study.v4-verdict-catalog-proof.v1",
                "baseline": revision,
                "baseline_clean": True,
                "python": sys.executable,
                "captures": str(root),
                "serialization": (
                    "json.dumps(sort_keys=True, ensure_ascii=False, indent=2) + LF"
                ),
                "cases": proofs,
            }
        )
    )
    print(json.dumps({"proof": str(output), "cases": len(proofs)}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.capture:
        capture(args.capture, args.output)
    else:
        prove(args.output)


if __name__ == "__main__":
    main()
