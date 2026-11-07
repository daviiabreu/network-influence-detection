"""Thin exploratory caller: parameters here, scientific implementation in src."""

import argparse
import hashlib
import json
import platform
import subprocess
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from ic_study.simulation.detection_calibration import DetectionPilot, PilotSpec

here = Path(__file__).resolve().parent
root = here.parents[4]
parser = argparse.ArgumentParser()
parser.add_argument("--output", default="run-01")
parser.add_argument("--seconds", type=int, default=600)
args = parser.parse_args()
spec = PilotSpec(**json.loads((here / "spec.json").read_text()))
spec = replace(spec, seconds=min(spec.seconds, args.seconds))
pilot = DetectionPilot(spec, here / args.output)
inputs = [here / "spec.json", Path(__file__), root / "studies/ic-2026-2027/uv.lock"]
inputs += list((root / "studies/ic-2026-2027/src/ic_study").rglob("*.py"))
inputs += [
    root
    / "studies/ic-2026-2027/research/questions/exploration/2026-09-24-parallel"
    / "detection-boundary-preregistration-draft.md"
]
manifest = {
    "git_head": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip(),
    "python": platform.python_version(),
    "numpy": np.__version__,
    "platform": platform.platform(),
    "input_sha256": {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in inputs
    },
    "confirmatory_execution": False,
    "effective_spec": asdict(spec),
}
(pilot.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(pilot.run(), indent=2))
