"""Read-only provenance/seed audit; does not regenerate any scientific data."""

import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
run = here / "matching-run-01"
manifest = json.loads((run / "manifest.json").read_text())
for path, expected in manifest["input_sha256"].items():
    data = subprocess.check_output(["git", "show", manifest["git_head"] + ":" + path])
    assert hashlib.sha256(data).hexdigest() == expected, path
current = set(json.loads((run / "seed-ledger.json").read_text()).values())
previous = set()
for name in ("redesign-calibration-v1", "reliability-correction-v1"):
    for line in (
        (here.parent / name / "run-01/panel-ledger.jsonl").read_text().splitlines()
    ):
        previous.update(json.loads(line)["seeds"].values())
previous.update(
    json.loads(
        (here.parent / "detection-boundary-v1/run-02/seed-ledger.json").read_text()
    ).values()
)
assert not current.intersection(previous)
report = {
    "input_hashes_verified": len(manifest["input_sha256"]),
    "current_unique_seeds": len(current),
    "previous_panel_seeds": len(previous),
    "intersection": 0,
    "confirmatory_seeds_generated": False,
    "scope": "Actual panel calibration ledgers; no regeneration of future reservations",
}
(run / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
