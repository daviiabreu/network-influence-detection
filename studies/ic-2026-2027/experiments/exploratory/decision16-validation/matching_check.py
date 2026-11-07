"""Blind a=0 matching check only; no discriminator or scientific contrasts."""

import hashlib
import json
import platform
import subprocess
from dataclasses import asdict
from pathlib import Path

import numpy as np

from ic_study.simulation.detection_calibration import DetectionPilot, PilotSpec

here = Path(__file__).resolve().parent
root = here.parents[4]
spec = PilotSpec(grid=(0.0,), seconds=300)
pilot = DetectionPilot(spec, here / "matching-run-01")
inputs = [Path(__file__), root / "studies/ic-2026-2027/uv.lock"]
inputs += list((root / "studies/ic-2026-2027/src/ic_study").rglob("*.py"))
manifest = {
    "git_head": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip(),
    "spec": asdict(spec),
    "python": platform.python_version(),
    "numpy": np.__version__,
    "input_sha256": {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in inputs
    },
    "scope": "a=0 nuisance matching only; no AUC, no primary contrast",
}
(pilot.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(pilot.run(), indent=2))
