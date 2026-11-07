"""Synthetic release-day rehearsal: chain state, authorized copies, facts and PDF.

Builds, under a new ``--root``, the state the installed post-release chain
leaves at ``awaiting-authorized-handoff``, calling the same modules with the
same arguments (plus ``--synthetic``). Curves, gate, second binding, G1c
successor, X1b/X3-X7 aggregates and comparisons are synthetic; the SHP
aggregate is the synthetic fixture unless ``--shp`` names an aggregate-only
file. Then it runs ``release_handoff.py`` copy, owner-facts and run, first with
``facts: {}`` and then with the generated facts, and checks the statuses. The
chain's own compile check uses ``nix shell nixpkgs#tectonic`` and the network,
on a copy of the Tectonic cache; the handoff compiles only from the cache.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import runpy
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

STUDY = Path(__file__).resolve().parents[4]
TOOL = Path(__file__).with_name("release_handoff.py")
CHAIN_COMPILE = ["nix", "shell", "nixpkgs#tectonic", "--command", "tectonic"]
STATE = Path.home() / ".local/state/research-workbench"
HOSTS = ("icmomat", "icllm", "homelab")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flags(directory: Path, names: tuple[str, ...]) -> list[str]:
    return [a for n in names for a in (f"--{n}", str(directory / f"{n}.json"))]


class Rehearsal:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.timings: list[dict[str, Any]] = []
        self.env = os.environ | {"UV_OFFLINE": "1", "PYTHONDONTWRITEBYTECODE": "1"}

    def call(self, name: str, argv: list[str], *, cwd: Path = STUDY, **env: str) -> int:
        started = time.time()
        with (self.root / "logs" / f"{name}.log").open("xb") as stream:
            code = subprocess.run(
                argv,
                cwd=cwd,
                env=self.env | env,
                stdout=stream,
                stderr=stream,
                check=False,
            ).returncode
        seconds = round(time.time() - started, 1)
        self.timings.append({"step": name, "exit": code, "seconds": seconds})
        return code

    def scientific(self, name: str, module: str, arguments: list[str]) -> None:
        argv = ["uv", "run", "--locked", "python", "-m", module, *arguments]
        if self.call(name, argv):
            raise SystemExit(f"{name} failed; see {self.root / 'logs' / name}.log")


def chain_state(run: Rehearsal, automation: Any, args: argparse.Namespace) -> Path:
    """The files, checkpoints and status the chain writes before the handoff."""
    from ic_study.analysis.v4_report_synthetic import (
        UnitPlan,
        build_gate,
        build_release,
        logistic_profile,
        shp_successor_fixture,
        stage_successor,
        unit_keys,
        write_release,
    )

    state = run.root / "synthetic-state"
    coord, gate = state / "coord-20260925", state / "sealed-v4-gate/gate"
    out = coord / "v4-release"
    out.mkdir(mode=0o700, parents=True)
    gate.parent.mkdir()
    plans = {
        key: UnitPlan(logistic_profile(0.02) if family == "B" else (0.5,) * 9)
        for family, tier in (("B", 1), ("A", 2), ("C", 2), ("D", 2), ("E", 2))
        for key in unit_keys(tier=tier, family=family).values()
    }
    curves, record = out / "released-curves.json", out / "release-record.json"
    write_release(curves, build_release(state / "curve-store", plans, draws=40))
    allocation = coord / "v4-allocation.json"
    build_gate(gate, allocation=allocation)
    successor = coord / "v4-gate-logs/G1c-aggregate-successor.json"
    successor.parent.mkdir(mode=0o700)
    successor.write_text(json.dumps(stage_successor(gate)))
    shp = coord / "shp-aggregate-successor-1.json"
    if args.shp is None:
        shp.write_text(json.dumps(shp_successor_fixture()))
    else:
        shutil.copyfile(args.shp, shp)
        (run.root / "PRIVATE-REAL-SHP-AGGREGATE").write_text(
            f"{args.shp} feeds F6, the anchor IDs and the public candidate here. "
            "Keep this rehearsal private and never deposit its outputs.\n"
        )
    optional = [allocation, successor, shp]
    key: dict[str, Any] = {
        "release": sha(record),
        "report_commit": automation.clean_revision(STUDY.parents[1]),
        "automation": sha(args.automation),
        "gate": automation.manifest(gate).decode(),
        "optional": {str(path): sha(path) for path in optional},
    }
    criteria = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
    crosswalk = STUDY / "experiments/exploratory/shp-anchor-crosswalk-v1/crosswalk.json"
    inputs = ["--gate-root", str(gate), "--criteria", str(criteria)]
    inputs += ["--curves", str(curves), "--release-record", str(record)]
    inputs += ["--allocation", str(allocation), "--stage-successor", str(successor)]
    inputs += ["--shp", str(shp), "--crosswalk", str(crosswalk)]
    confirmed = automation.attempt(out, "confirmatory")
    report = confirmed / "report"
    run.scientific(
        "chain-report",
        "ic_study.analysis.detection_v4_report",
        [*inputs, "--out", str(report), "--synthetic"],
    )
    manuscript = confirmed / "manuscript"
    shutil.copytree(STUDY / "publications/jcss-manuscript", manuscript)
    for name in ("sn-jnl.cls", "sn-mathphys-num.bst"):
        shutil.copy2(args.springer / name, manuscript / name)
    results = manuscript / "sections/results.tex"
    text = results.read_text()
    start = text.index("This section is reserved")
    end = text.index("\\subsection", start)
    waiting = "This automated assembly awaits human review against the hash-bound v4"
    automation.atomic(
        results, (text[:start] + waiting + " report.\n\n" + text[end:]).encode()
    )
    values, catalog = (
        confirmed / "result-values.json",
        confirmed / "result-catalog.json",
    )
    run.scientific(
        "chain-export-confirmatory",
        "ic_study.analysis.v4_report_export",
        [
            *inputs,
            *("--report", str(report), "--manuscript", str(manuscript)),
            *("--values", str(values), "--catalog", str(catalog), "--fill"),
        ],
    )
    compile_cache = run.root / "tectonic-cache-chain"
    shutil.copytree(args.tectonic_cache, compile_cache)
    compiled = run.call(
        "chain-compile",
        [*CHAIN_COMPILE, "main.tex"],
        cwd=manuscript,
        TECTONIC_CACHE_DIR=str(compile_cache),
    )
    if compiled:
        raise SystemExit("chain compile_check failed; see logs/chain-compile.log")
    checker = STUDY / "publications/jcss-manuscript/pipeline/paper_check.py"
    checks = {}
    for mode in ("draft", "submission"):
        argv = ["uv", "run", "--locked", "python", str(checker), "--root"]
        argv += [str(manuscript), "--venue", "jcss", "--pdf"]
        argv += [str(manuscript / "main.pdf"), "--result-values", str(values)]
        argv += ["--submission"] if mode == "submission" else []
        checks[mode] = run.call(f"chain-paper-check-{mode}", argv)
    automation.record(confirmed / "paper-check-status.json", checks)
    automation.save_checkpoint(out / "confirmatory-checkpoint.json", key, confirmed)

    roots = [state / f"sealed-v4-exploratory-x3-x7/3334ac0f/{host}" for host in HOSTS]
    runs = {name: state / f"{name}-run" for name in ("x5", "x7")}
    for directory in [*roots, *runs.values()]:
        directory.mkdir(parents=True)
        (directory / "SYNTHETIC").write_text("synthetic placeholder\n")
    tests = STUDY / "tests/unit"
    fixtures = runpy.run_path(str(tests / "test_v4_exploratory_export.py"))
    x5_input = runpy.run_path(str(tests / "test_v4_exploratory_comparisons.py"))
    x1b = state / "x1b.json"
    x1b_value = {"schema": "ic-study.v4-exploratory-x1b.v1", "synthetic": True}
    x1b.write_text(json.dumps(x1b_value | fixtures["synthetic_x1b"](), indent=2))
    key |= {
        "exports": [automation.manifest(root).decode() for root in roots],
        "x5": automation.manifest(runs["x5"]).decode(),
        "x7": automation.manifest(runs["x7"]).decode(),
        "x1b": sha(x1b),
    }
    final = automation.attempt(out, "exploratory")
    aggregates = final / "aggregates"
    aggregates.mkdir(mode=0o700)
    data = {name: fixtures[f"synthetic_{name}"]() for name in ("x3", "x4", "x6", "x7")}
    data["x5"] = {"synthetic": True, **x5_input["x5_input"]()}
    for name, value in data.items():
        text = json.dumps(value, indent=2, sort_keys=True) + "\n"
        (aggregates / f"{name}.json").write_text(text)
    comparisons = final / "comparisons.json"
    run.scientific(
        "chain-comparisons",
        "ic_study.analysis.v4_exploratory_comparisons",
        [
            *("--curves", str(curves), "--release-record", str(record)),
            *("--x1b", str(x1b), *flags(aggregates, ("x5", "x3", "x4"))),
            *("--output", str(comparisons)),
        ],
    )
    marked = json.loads(comparisons.read_bytes()) | {"synthetic": True}
    comparisons.write_text(json.dumps(marked, indent=2, sort_keys=True) + "\n")
    shutil.copytree(manuscript, final / "manuscript")
    run.scientific(
        "chain-export-exploratory",
        "ic_study.analysis.v4_exploratory_export",
        [
            *flags(aggregates, ("x3", "x4", "x6", "x7")),
            *("--comparisons", str(comparisons), "--confirmatory-values", str(catalog)),
            *("--manuscript", str(final / "manuscript")),
            *("--values", str(final / "result-values.json")),
            *("--catalog", str(final / "catalog.json")),
        ],
    )
    automation.save_checkpoint(out / "exploratory-checkpoint.json", key, final)
    status = out / "chain-status.json"
    automation.record(
        status,
        {
            "status": "awaiting-authorized-handoff",
            "assembly_ready": False,
            "confirmatory": str(confirmed),
            "exported_attempt": str(final),
            "inputs": {
                "curves": str(curves),
                "release_record": str(record),
                "gate_root": str(gate),
                "criteria": str(criteria),
                "allocation": str(allocation),
                "stage_successor": str(successor),
                "shp": str(shp),
                "crosswalk": str(crosswalk),
                "confirmatory_catalog": str(catalog),
                "merged_catalog": str(final / "catalog.json"),
                "generated": str(final / "manuscript/generated"),
                "report": str(report),
                "exploratory": {
                    name: str(aggregates / f"{name}.json")
                    for name in ("x3", "x4", "x6", "x7")
                },
                "comparisons": str(comparisons),
                "owner_facts": None,
            },
            "catalog_semantics": (
                "catalog.json is the merged confirmatory and exploratory catalog"
            ),
        },
    )
    return status


def handoff(run: Rehearsal, status: Path, args: argparse.Namespace) -> dict[str, Any]:
    python = sys.executable
    authorized, owner = run.root / "authorized", run.root / "owner"
    owner.mkdir()
    copied = run.call(
        "copy",
        [
            *(python, str(TOOL), "copy", "--synthetic"),
            *("--status", str(status), "--out", str(authorized)),
        ],
    )
    spec = authorized / "handoff.json"
    facts = owner / "owner-facts.json"
    generated = run.call(
        "owner-facts",
        [python, str(TOOL), "owner-facts", "--handoff", str(spec), "--out", str(facts)],
    )
    if copied or generated:
        raise SystemExit("copy or owner-facts refused; see logs/")
    empty = owner / "owner-facts-empty.json"
    schema = "ic-study.v4-manuscript-assembly-facts.v1"
    empty.write_text(json.dumps({"schema": schema, "synthetic": True, "facts": {}}))
    attempts = run.root / "handoff-attempts"
    statuses = {}
    for name, file in (("handoff-empty-facts", empty), ("handoff-facts", facts)):
        argv = [python, str(TOOL), "run", "--checkout", str(args.checkout)]
        argv += ["--handoff", str(spec), "--owner-facts", str(file)]
        argv += ["--out", str(attempts), "--automation", str(args.automation)]
        argv += ["--tectonic", args.tectonic, "--tectonic-cache"]
        argv += [str(args.tectonic_cache), "--synthetic"]
        code = run.call(name, argv)
        statuses[name] = json.loads((attempts / "chain-status.json").read_bytes())
        statuses[name]["exit"] = code
    missing, complete = statuses["handoff-empty-facts"], statuses["handoff-facts"]
    checks = complete.get("checks", {})
    expected = (
        missing["exit"] == 2
        and missing["missing_facts"] == ["post.x5_supplied"]
        and complete["exit"] == 1
        and complete["status"] == "awaiting-human-review"
        and complete["assembly_ready"] is True
        and all(
            checks.get(step) == 0
            for step in (
                "tectonic",
                "paper_check_draft",
                "prepare_short_path",
                "verify_short_path",
            )
        )
    )
    return {"passed": expected, "missing": missing, "complete": complete}


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--automation", type=Path, required=True)
    parser.add_argument("--checkout", type=Path, default=STUDY.parents[1])
    parser.add_argument("--shp", type=Path)
    parser.add_argument("--springer", type=Path, default=STATE / "springer-template")
    parser.add_argument("--tectonic", default=runpy.run_path(str(TOOL))["TECTONIC"])
    parser.add_argument("--tectonic-cache", type=Path, default=STATE / "tectonic-cache")
    args = parser.parse_args()
    args.root = args.root.absolute()
    args.root.mkdir(parents=True)
    (args.root / "logs").mkdir()
    (args.root / "SYNTHETIC").write_text("Synthetic release-day rehearsal.\n")
    spec = importlib.util.spec_from_file_location("automation", args.automation)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {args.automation}")
    automation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(automation)
    run = Rehearsal(args.root)
    result = handoff(run, chain_state(run, automation, args), args)
    result["timings"] = run.timings
    summary = args.root / "rehearsal-results.json"
    summary.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"passed": result["passed"], "timings": run.timings}, indent=1))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
