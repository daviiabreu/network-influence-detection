"""Verify revision probes and measured source against final code, without training."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import types
from pathlib import Path

import numpy as np

from ic_study.analysis.detection_boundary_v4 import mean_feature_jacobian, validate_fit
from ic_study.simulation.detection_v4 import Cell, PanelSource, SeedPlan


def node(code, name):
    tree = ast.parse(code)
    for part in name.split("."):
        tree = next(n for n in tree.body if getattr(n, "name", None) == part)
    return ast.dump(tree, include_attributes=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    study = here.parents[2]
    snapshot_path = here / "cost-fit-source-v41.json"
    snapshot = json.loads(snapshot_path.read_text())
    measurement = json.loads((here / "cost-fits-v41.json").read_text())
    checks = {}
    for path, names in [
        (
            "src/ic_study/analysis/detection_boundary_v4.py",
            ["profile_match", "validate_fit", "amplification", "finite_differences"],
        ),
        (
            "src/ic_study/simulation/detection_v4.py",
            ["SeedPlan", "fit_cell", "PanelSource.profiles"],
        ),
    ]:
        old = snapshot["sources"][path]["text"]
        digest = hashlib.sha256(old.encode()).hexdigest()
        assert (
            digest == snapshot["sources"][path]["sha256"] == measurement["code"][path]
        )
        for name in names:
            checks[name] = node(old, name) == node((study / path).read_text(), name)
    assert all(checks.values())
    module = types.ModuleType("v41_executed_source")
    sys.modules[module.__name__] = module
    exec(
        snapshot["sources"]["src/ic_study/simulation/detection_v4.py"]["text"],
        module.__dict__,
    )
    comparisons = 0
    for family in "ABCDE":
        for channel in ("observed", "latent", "ordinal_one", "latent_rank"):
            for mobility in (False, True):
                if channel == "latent_rank" and mobility:
                    continue
                cell = Cell(
                    0.03, 0.7, family=family, channel=channel, mobility=mobility
                )
                old = module.PanelSource(cell, SeedPlan(9002))
                new = PanelSource(cell, SeedPlan(9002))
                for point in (None, np.array([0.85, 0 if family in "AC" else 0.1])):
                    assert (
                        old.profiles("match", 2, parameters=point).tobytes()
                        == new.profiles("match", 2, parameters=point).tobytes()
                    )
                    comparisons += 1
    rng = np.random.default_rng(4101)
    old_failures = new_failures = 0
    for _ in range(3000):
        fitting = rng.normal(size=(1024, 2))
        fresh = rng.normal(size=(4096, 2)) - fitting.mean(0)
        old_failures += bool(
            np.any(np.abs(fresh.mean(0)) > 4 * fresh.std(0, ddof=1) / 64)
        )
        new_failures += not validate_fit(
            fresh[:2048], 2, fitting.std(0, ddof=1) / 32
        ).passed
    source = PanelSource(Cell(0.03, 0.7), SeedPlan(9100))
    point, delta = np.array([0.85, 0.15]), np.array([0.001, -0.001])

    def generate(p):
        return source.profiles("match", 64, parameters=p)

    baseline = generate(point)
    derivative = mean_feature_jacobian(generate, point, 0.01, baseline)
    actual = (generate(point + delta)[:, 2:5] - baseline[:, 2:5]).mean(0)
    predicted = delta @ derivative[:, 2:5]
    error = float(np.linalg.norm(predicted - actual) / np.linalg.norm(actual))
    assert (
        0.11 < old_failures / 3000 < 0.17
        and new_failures / 3000 < 0.003
        and error < 0.05
    )
    criteria_path = here / "criteria-v4.json"
    criteria = json.loads(criteria_path.read_text())
    calibration = {}
    for key, path in [
        ("implementation_sha256", study / "src/ic_study/simulation/v4_criteria.py"),
        ("script_sha256", here / "calibrate_criteria.py"),
    ]:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert criteria[key] == digest
        calibration[key] = digest
    result = dict(
        kind="v4.1-revision-verification-not-gate",
        classifiers_trained=0,
        synthetic=dict(
            seed=4101,
            replications=3000,
            old_failures=old_failures,
            new_failures=new_failures,
        ),
        mean_shift=dict(
            seed_repetition=9100,
            phase="match",
            panels=64,
            size=10626,
            point=point.tolist(),
            delta=delta.tolist(),
            step=0.01,
            actual=actual.tolist(),
            predicted=predicted.tolist(),
            relative_shift_error=error,
        ),
        measured_source_ast_equal=checks,
        byte_equal_panel_batches=comparisons,
        panels_per_batch=2,
        criteria_unchanged=calibration,
        recalibration_required=False,
        inputs={
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (snapshot_path, here / "cost-fits-v41.json", criteria_path)
        },
        final_source_hashes={
            p: hashlib.sha256((study / p).read_bytes()).hexdigest()
            for p in snapshot["sources"]
        },
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    with args.output.open("x") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
