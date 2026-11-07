from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

STUDY = Path(__file__).resolve().parents[2]
REPO = STUDY.parents[1]
EXAMPLE = STUDY / "publications/reproducibility/regenerate_fragmentation.py"
ARTIFACT_ROOT = Path(
    os.environ.get(
        "IC_REPRO_ARTIFACT_ROOT",
        str(
            Path.home()
            / ".local/state/research-workbench"
            / "fragmentation-pilot-20260912/artifacts/sha256"
        ),
    )
)
PILOT = STUDY / "experiments/exploratory/fragmentation-pilot-v1"


def test_retained_fragmentation_case_regenerates_after_offline_validation(
    tmp_path: Path,
) -> None:
    manifest = json.loads((PILOT / "run-manifest.json").read_text())
    digest = manifest["phases"]["pilot"]["sha256"]
    if not (ARTIFACT_ROOT / digest[:2] / digest).is_file():
        pytest.skip("Retained pilot artifacts are not available on this machine")

    output = tmp_path / "successor"
    result = subprocess.run(
        [
            sys.executable,
            str(EXAMPLE),
            "--study-root",
            str(STUDY),
            "--artifact-root",
            str(ARTIFACT_ROOT),
            "--output-dir",
            str(output),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    receipt = json.loads((output / "offline-validation.json").read_text())
    successor = json.loads((output / "regenerated-case-35.json").read_text())
    assert receipt["format"] == "offline-experiment-validation-v1"
    assert receipt["scientific_acceptance"] is False
    assert successor["matches_retained_scientific_result"] is True
    assert successor["cached_groups"] == 13
    assert successor["current_groups_at_cached_stop"] == 12
