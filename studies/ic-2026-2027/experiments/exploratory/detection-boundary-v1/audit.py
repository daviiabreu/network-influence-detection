"""Audit completed calibration provenance and existing seed reservations only."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
parser = argparse.ArgumentParser()
parser.add_argument("run", nargs="?", default="run-02")
args = parser.parse_args()
run = here / args.run
manifest = json.loads((run / "manifest.json").read_text())
for name, digest in manifest["input_sha256"].items():
    committed = subprocess.check_output(
        ["git", "show", manifest["git_head"] + ":" + name]
    )
    if hashlib.sha256(committed).hexdigest() != digest:
        raise ValueError(f"Input differs from recorded revision: {name}")
new = set(json.loads((run / "seed-ledger.json").read_text()).values())
old = set()
for folder in ("redesign-calibration-v1", "reliability-correction-v1"):
    ledger = here.parent / folder / "run-01/panel-ledger.jsonl"
    for line in ledger.read_text().splitlines():
        old.update(json.loads(line)["seeds"].values())


def old_seed(phase: str, role: str, index: int) -> int:
    name = f"ic-redesign-v1|{phase}|{role}|{index}"
    return int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "big")


for phase in ("dose-calibration", "dose-check"):
    for role in ("network", "state", "source"):
        old.update(old_seed(phase, role, i) for i in range(48))
reserved = set()
for phase, number in (
    ("confirm-train", 4000),
    ("confirm-validation", 800),
    ("confirm-test", 1000),
):
    for role in ("network", "state", "events", "mask", "error"):
        size = 500 if phase == "confirm-test" and role == "network" else number
        reserved.update(old_seed(phase, "panel/" + role, i) for i in range(size))
for role, number in (("network", 500), ("state", 1000), ("source", 1000)):
    reserved.update(old_seed("confirm-test", "dose/" + role, i) for i in range(number))
for candidate in ("panel", "dose"):
    reserved.add(old_seed("confirm-bootstrap", candidate + "/resampling", 0))
if new & old or new & reserved:
    raise ValueError("Seed collision")
report = {
    "verified_input_hashes": len(manifest["input_sha256"]),
    "new_calibration_unique_seeds": len(new),
    "previous_calibration_unique_seeds": len(old),
    "previous_reserved_confirmatory_seeds": len(reserved),
    "intersection_count": 0,
    "new_confirmatory_seed_generation": False,
    "confirmatory_simulations": 0,
    "scope": (
        "Actual previous pilot ledgers plus prior reservations; "
        "review scripts have separate namespaces but no execution ledgers were supplied"
    ),
}
if args.run == "run-02":
    first = here / "run-01/seed-ledger.json"
    same = first.read_bytes() == (run / "seed-ledger.json").read_bytes()
    if not same:
        raise ValueError("Replay seed ledger differs from original attempt")
    report["replay_seed_ledger_byte_identical"] = same
(run / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
