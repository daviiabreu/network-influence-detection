"""Bind matching-only measurements, seed audit and preserved review evidence."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import subprocess
import types
from collections import Counter
from pathlib import Path

from ic_study.simulation.detection_calibration import calibration_seed

REVIEW_ROOT = Path(
    "/private/tmp/claude-501/-Users-davi-Documents-github-research-workbench/"
    "ccea0cfa-cbfe-40e0-a2a0-91e611807839/scratchpad/review-v4"
)
REVIEW_HASHES = {
    "findings": "fadc8d293fb36d56b66816558545321743ba34583d1e5508919eab8c17b80595",
    "decisions": "866a67d23a124557994d422b03bcf31ee588f472e19a8097813dd6aa0b654f7a",
}
MATCHING_NODES = {
    "analysis/detection_boundary_v4.py": (
        "ACCEPTED",
        "ProfileFit",
        "_SolverError",
        "profile_match",
        "Validation",
        "validate_fit",
        "finite_differences",
        "amplification",
    ),
    "simulation/detection_v4.py": (
        "ROLES",
        "SeedPlan",
        "Cell",
        "selected_features",
        "PanelSource",
        "FitAttempt",
        "ValidatedFit",
        "fit_cell",
    ),
}
MATCHING_DEPENDENCIES = (
    "models/anchored_panel.py",
    "models/detection_panel.py",
    "models/detection_panel_v4.py",
    "analysis/detection_boundary.py",
    "simulation/v4_store.py",
)
SOURCE_FILES = (
    *MATCHING_NODES,
    *MATCHING_DEPENDENCIES,
    "simulation/v4_gate.py",
    "simulation/v4_plan.py",
)


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def node(code, name):
    tree = ast.parse(code)
    for part in name.split("."):
        candidates = [
            child
            for child in tree.body
            if getattr(child, "name", None) == part
            or (
                isinstance(child, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == part for t in child.targets)
            )
        ]
        if len(candidates) != 1:
            raise ValueError(f"Require exactly one AST node for {name}")
        tree = candidates[0]
    return ast.dump(tree, include_attributes=False)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def recorded_source_hash(measurement, relative):
    suffix = "/src/ic_study/" + relative
    matches = [
        value
        for key, value in measurement["code"].items()
        if key.endswith(suffix) or key == suffix.removeprefix("/")
    ]
    require(len(matches) == 1, f"Ambiguous source provenance for {relative}")
    return matches[0]


def verify_measured_rows(measurement, budget):
    accepted = {"anchor-exact", "interior", "boundary"}
    rows = measurement["measurements"]
    require(bool(rows), "No measured rows")
    attempts_by_status = Counter()
    finals_by_status = Counter()
    retry_count = 0
    successes = 0
    evaluations = {"initial": [], "retry": []}
    for row in rows:
        attempts = row["attempts"]
        require(len(attempts) in {1, 2}, "Require one attempt or one retry")
        if len(attempts) == 2:
            first = attempts[0]
            require(
                first["status"] in accepted and first["validation_passed"] is False,
                "Retry requires accepted first fit and failed independent validation",
            )
            retry_count += 1
        for index, attempt in enumerate(attempts):
            require(
                attempt["count"] == (1024, 4096)[index], "Wrong attempt sample size"
            )
            count = attempt["evaluations"]
            require(
                type(count) is int and 0 <= count <= budget,
                "Evaluation budget exceeded",
            )
            evaluations[("initial", "retry")[index]].append(count)
            status = attempt["status"]
            attempts_by_status[status] += 1
            if status in accepted:
                residual, tolerance = attempt["residual"], attempt["tolerance"]
                require(
                    len(residual) == len(tolerance) == 2
                    and all(math.isfinite(v) for v in (*residual, *tolerance))
                    and all(v >= 0 for v in tolerance),
                    "Invalid accepted residual or tolerance",
                )
                moments = 1 if status == "boundary" else 2
                require(
                    all(abs(residual[k]) <= tolerance[k] for k in range(moments)),
                    "Accepted fit violates unchanged matching tolerance",
                )
            if attempt["validation_passed"] is True:
                z = attempt["validation_z"]
                require(status in accepted, "Validation cannot accept a failed fit")
                require(
                    z is not None
                    and len(z) == 2
                    and all(math.isfinite(value) and abs(value) <= 4 for value in z),
                    "Passed validation violates the four-SE criterion",
                )
        final = attempts[-1]
        success = final["status"] in accepted and final["validation_passed"] is True
        require(row["success"] is success, "Final success contradicts fit/validation")
        successes += int(success)
        finals_by_status[final["status"]] += 1
    return dict(
        rows=len(rows),
        successful_validations=successes,
        final_gaps=len(rows) - successes,
        attempts_by_status=dict(sorted(attempts_by_status.items())),
        final_statuses=dict(sorted(finals_by_status.items())),
        evaluation_budget_per_attempt=budget,
        max_evaluations_by_attempt={
            key: max(value) if value else None for key, value in evaluations.items()
        },
        observed_retries=retry_count,
        observed_retry_fraction=retry_count / len(rows),
        retry_interpretation=(
            "Sample frequency only; does not establish population retry probability"
        ),
        matching_and_validation_criteria_satisfied=True,
    )


def verify_matching(study, measurements, snapshots):
    root = study.parents[1]
    result = {}
    for label in ("before", "after"):
        checks = {}
        require(measurements[label]["classifiers_trained"] == 0, "Training forbidden")
        for relative, content in snapshots[label].items():
            require(
                sha256(content.encode())
                == recorded_source_hash(measurements[label], relative),
                f"{label} measurement source binding differs: {relative}",
            )
            if label == "before":
                git_path = "studies/ic-2026-2027/src/ic_study/" + relative
                frozen = subprocess.check_output(
                    ["git", "show", "688ab26:" + git_path], cwd=root
                )
                require(content.encode() == frozen, f"Baseline differs: {relative}")
                checks[relative] = {"matches_688ab26_bytes": True}
            elif relative in MATCHING_NODES:
                current = (study / "src/ic_study" / relative).read_text()
                equality = {
                    name: node(content, name) == node(current, name)
                    for name in MATCHING_NODES[relative]
                }
                require(all(equality.values()), f"Matching AST drift: {relative}")
                checks[relative] = equality
            elif relative in MATCHING_DEPENDENCIES:
                require(
                    content.encode()
                    == (study / "src/ic_study" / relative).read_bytes(),
                    f"Matching dependency drift: {relative}",
                )
                checks[relative] = {"matches_current_bytes": True}
        result[label] = checks
    return result


def verify_frozen_panel(study):
    root = study.parents[1]
    relative = "studies/ic-2026-2027/src/ic_study/models/detection_panel.py"
    revision = "d33bf4e4a485797f04775979618e25ba5f8b2ba9"
    expected = (
        "a9d294e3a5c4ed77eeca234e172e763814627ea21c38381ddc0181cab48a513a",
        "aee847707ca82acb4004e4c6288634ac294c2582da097a9183e80b698ca40be1",
    )
    contents = [
        subprocess.check_output(["git", "show", rev + ":" + relative], cwd=root)
        for rev in (revision + "^", revision)
    ]
    require(tuple(map(sha256, contents)) == expected, "Frozen source hash mismatch")
    contents.append((root / relative).read_bytes())
    require(sha256(contents[-1]) == expected[1], "Frozen file changed again")
    modules = []
    for index, content in enumerate(contents):
        module = types.ModuleType(f"verified_zero_share_{index}")
        exec(compile(content, relative, "exec"), module.__dict__)
        modules.append(module)
    panels = {}
    for size, expected_panel in (
        (600, "4df3049105b63e6d546e64af471d8b381fdb43fc76877ec57fb853623ba2aca5"),
        (10626, "0bd67064acd8f37153373d67f69952f7f6ebd9f6cbeac05048761112e3900602"),
    ):
        values = [
            module.influence_panel(
                size,
                11,
                calibration_seed("match", "state", 1),
                calibration_seed("match", "network", 1),
                share=0,
                repulsion=0.25,
            ).tobytes()
            for module in modules
        ]
        require(len(set(values)) == 1, "Zero-share bytes differ")
        require(sha256(values[0]) == expected_panel, "Calibration bytes drifted")
        panels[str(size)] = dict(equal_before_after_current=True, sha256=expected_panel)
    return dict(
        commit=revision,
        source_before=expected[0],
        source_after=expected[1],
        panels=panels,
        waves=11,
        share=0,
        repulsion=0.25,
        calibration_phase="match",
        calibration_index=1,
        reason="Skip unused network permutations and zero-share drift work",
    )


def verify_seed_lineage(study, here, snapshot):
    audit_path = here / "seed-role-audit-v42.json"
    audit = json.loads(audit_path.read_text())
    source = "simulation/detection_v4.py"
    require(
        sha256(snapshot[source].encode()) == audit["implementation_sha256"],
        "Seed audit is not bound to captured source snapshot",
    )
    require(
        sha256((here / "audit_seeds.py").read_bytes()) == audit["script_sha256"],
        "Seed audit script changed",
    )
    checks = {}
    for relative, names in (
        (source, ("ROLES", "SeedPlan")),
        ("simulation/v4_gate.py", ("task_seed_plan",)),
        ("simulation/v4_plan.py", ("G2_CELLS", "SCENARIOS", "GateTask", "gate_tasks")),
    ):
        current = (study / "src/ic_study" / relative).read_text()
        for name in names:
            checks[name] = node(snapshot[relative], name) == node(current, name)
    require(all(checks.values()), "Seed audit semantics changed")
    require(audit["collisions"] == 0, "Seed audit has collisions")
    return dict(
        audit_sha256=sha256(audit_path.read_bytes()),
        unchanged_ast=checks,
        snapshot_source_sha256=audit["implementation_sha256"],
        current_source_sha256=sha256((study / "src/ic_study" / source).read_bytes()),
        collisions=audit["collisions"],
        materials=audit["materials"],
        completed_audit_preserved=True,
        scope="AST lineage verification; full collision audit not repeated",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--before-source",
        type=Path,
        default=Path("/private/tmp/v42-baseline-688ab26/src/ic_study"),
    )
    parser.add_argument(
        "--after-source",
        type=Path,
        default=Path("/private/tmp/v42-after-final3/src/ic_study"),
    )
    parser.add_argument(
        "--audit-source",
        type=Path,
        default=Path("/private/tmp/v42-after-validated/src/ic_study"),
    )
    parser.add_argument("--review-source", type=Path, default=REVIEW_ROOT)
    parser.add_argument("--replay-evidence", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    study = here.parents[2]
    paths = {
        label: here / f"cost-fits-v42-{label}.json" for label in ("before", "after")
    }
    measurements = {
        label: json.loads(path.read_text()) for label, path in paths.items()
    }
    if args.replay_evidence:
        snapshots = json.loads(args.replay_evidence.read_text())["source_snapshots"]
    else:
        snapshots = {
            label: {name: (directory / name).read_text() for name in SOURCE_FILES}
            for label, directory in (
                ("before", args.before_source),
                ("after", args.after_source),
                ("audit", args.audit_source),
            )
        }
    reviews = {}
    for name, expected in REVIEW_HASHES.items():
        original = args.review_source / f"{name}.md"
        copy = (
            study
            / f"research/questions/exploration/2026-09-24-parallel/v4-review-{name}.md"
        )
        require(sha256(copy.read_bytes()) == expected, f"Review copy mismatch: {name}")
        if not args.replay_evidence:
            require(
                original.read_bytes() == copy.read_bytes(), f"Review differs: {name}"
            )
        reviews[name] = dict(
            sha256=expected,
            verbatim=True,
            original_comparison="recorded hash"
            if args.replay_evidence
            else "direct byte equality",
        )
    result = dict(
        kind="v4.2-revision-verification-not-gate",
        classifiers_trained=0,
        review_copies=reviews,
        frozen_panel=verify_frozen_panel(study),
        measured_source=verify_matching(study, measurements, snapshots),
        measured_row_criteria={
            label: verify_measured_rows(measurements[label], budget)
            for label, budget in (("before", 64), ("after", 96))
        },
        seed_audit_lineage=verify_seed_lineage(study, here, snapshots["audit"]),
        source_snapshots=snapshots,
        inputs={path.name: sha256(path.read_bytes()) for path in paths.values()},
        script_sha256=sha256(Path(__file__).read_bytes()),
    )
    with args.output.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "source_snapshots"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
