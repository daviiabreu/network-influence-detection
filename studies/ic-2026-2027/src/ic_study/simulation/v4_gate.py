"""Frozen-allocation gate tasks; all scientific per-repetition outputs stay sealed."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import platform
import sys
from dataclasses import replace
from math import ceil
from pathlib import Path
from typing import Any, cast

import numpy as np

from ic_study.analysis.detection_boundary import auc
from ic_study.analysis.detection_boundary_v4 import band, score_uncertainty
from ic_study.analysis.redesign import fit_discriminant
from ic_study.models.anchored_panel import Floats
from ic_study.simulation.detection_v4 import (
    Cell,
    PanelSource,
    PipelineResult,
    SeedPlan,
    ValidatedFit,
    fit_cell,
    pipeline,
)
from ic_study.simulation.v4_criteria import (
    Thresholds,
    dispersion,
    dispersion_pass,
    fd_stability,
    refit_ratio,
)
from ic_study.simulation.v4_plan import G2_CELLS, GateTask, gate_tasks, substitute_cells
from ic_study.simulation.v4_store import SealedStore


def source_hashes(study: Path) -> dict[str, str]:
    paths = (
        sorted((study / "src").rglob("*.py"))
        + sorted((study / "tests").rglob("*.py"))
        + sorted((study / "experiments/exploratory/detection-boundary-v4").glob("*.py"))
    )
    paths += [study / "uv.lock", study / "pyproject.toml"]
    return {
        str(p.relative_to(study)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    }


def numerical_probe() -> list[float]:
    source = PanelSource(Cell(0.03, 0.7), SeedPlan(9988), size=600)
    return source.profiles("match", 2).ravel().tolist()


def preflight(freeze: Path, study: Path) -> dict[str, object]:
    if not freeze.is_file():
        raise ValueError(
            "A reviewed freeze record is required; none was created by implementation"
        )
    record = json.loads(freeze.read_bytes())
    expected = source_hashes(study)
    code_sha256 = hashlib.sha256(
        json.dumps(expected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if (
        record.get("schema") != 2
        or record.get("allocation_binding") != "post-G0-pre-G2-statuses-sha256"
        or record.get("status") != "frozen"
        or record.get("code") != expected
        or record.get("code_sha256") != code_sha256
    ):
        raise ValueError("Freeze code closure mismatch")
    for name in ("criteria-v43.json", "inventory.json"):
        path = study / "experiments/exploratory/detection-boundary-v4" / name
        if (
            record.get("artifacts", {}).get(name)
            != hashlib.sha256(path.read_bytes()).hexdigest()
        ):
            raise ValueError("Freeze artifact mismatch")
    criteria_path = (
        study / "experiments/exploratory/detection-boundary-v4" / "criteria-v43.json"
    )
    calibration = json.loads(criteria_path.read_bytes())
    criteria_code = study / "src/ic_study/simulation/v4_criteria.py"
    calibration_script = criteria_path.parent / "calibrate_criteria.py"
    if (
        calibration["implementation_sha256"]
        != hashlib.sha256(criteria_code.read_bytes()).hexdigest()
        or calibration["script_sha256"]
        != hashlib.sha256(calibration_script.read_bytes()).hexdigest()
        or not calibration["joint_targets_met"]
    ):
        raise ValueError("Calibrated criteria code mismatch")
    amendment = (
        study
        / "research/questions/exploration/2026-09-24-parallel"
        / "detection-boundary-amendment-v4.md"
    )
    if (
        record.get("amendment_sha256")
        != hashlib.sha256(amendment.read_bytes()).hexdigest()
    ):
        raise ValueError("Freeze amendment mismatch")
    revision = amendment.with_name("amendment-v4-1-revision.md")
    if (
        record.get("revision_sha256")
        != hashlib.sha256(revision.read_bytes()).hexdigest()
    ):
        raise ValueError("Freeze revision mismatch")
    spec = amendment.with_name("amendment-v4-decision-spec.md")
    if record.get("spec_sha256") != hashlib.sha256(spec.read_bytes()).hexdigest():
        raise ValueError("Freeze spec mismatch")
    for name in ("findings", "decisions"):
        review = amendment.with_name(f"v4-review-{name}.md")
        if (
            record.get(f"review_{name}_sha256")
            != hashlib.sha256(review.read_bytes()).hexdigest()
        ):
            raise ValueError("Freeze review decision closure mismatch")
    delta = amendment.with_name("v4-delta-review-decisions.md")
    if (
        record.get("delta_review_decisions_sha256")
        != hashlib.sha256(delta.read_bytes()).hexdigest()
    ):
        raise ValueError("Freeze delta decision closure mismatch")
    if (
        record.get("workers") != 8
        or record.get("shards") != 8
        or record.get("blas_threads") != 1
    ):
        raise ValueError("Freeze allocation mismatch")
    environment = manifest(study)
    if (
        record.get("environment") != environment["environment"]
        or record.get("environment_sha256") != environment["environment_sha256"]
    ):
        raise ValueError("Freeze environment mismatch")
    reference = np.asarray(record.get("numerical_probe", []), dtype=float)
    actual = np.array(numerical_probe())
    if reference.shape != actual.shape or not np.allclose(
        actual, reference, rtol=0, atol=1e-12
    ):
        raise ValueError("Shard numerical equivalence check failed")
    return cast(dict[str, object], record)


def manifest(study: Path) -> dict[str, object]:
    environment = {
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "lock": hashlib.sha256((study / "uv.lock").read_bytes()).hexdigest(),
        "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
        "VECLIB_MAXIMUM_THREADS": os.environ.get("VECLIB_MAXIMUM_THREADS"),
    }
    return {
        "code": source_hashes(study),
        "environment": environment,
        "environment_sha256": hashlib.sha256(
            json.dumps(environment, sort_keys=True).encode()
        ).hexdigest(),
        "host_sha256": hashlib.sha256(
            (platform.node() + platform.machine()).encode()
        ).hexdigest(),
    }


def synthetic_scores(
    scenario: str, *, seed: int, networks: int = 2000
) -> tuple[Floats, Floats]:
    rng = np.random.default_rng(seed)
    classes = []
    for _ in range(2):
        if scenario == "non-gaussian":
            cluster = rng.standard_t(5.2, (networks, 1, 9)) / np.sqrt(5.2 / 3.2)
            event = rng.standard_t(5.2, (networks, 2, 9)) / np.sqrt(5.2 / 3.2)
        else:
            cluster = rng.normal(size=(networks, 1, 9))
            event = rng.normal(size=(networks, 2, 9))
        icc = 0 if scenario == "gaussian-icc0" else 0.5
        scores = np.sqrt(icc) * cluster + np.sqrt(1 - icc) * event
        if scenario == "ties":
            scores = np.round(scores)
        elif scenario == "dependent-slots":
            common = rng.normal(size=(networks, 1, 1))
            scores = np.sqrt(0.2) * scores + np.sqrt(0.8) * common
        elif scenario not in {"gaussian-icc0", "gaussian-icc05", "non-gaussian"}:
            raise ValueError("Unknown synthetic score scenario")
        classes.append(scores)
    return classes[0], classes[1]


def fit_record(result: ValidatedFit) -> dict[str, object]:
    attempts = []
    for attempt in result.attempts:
        fit = attempt.fit
        z = np.divide(fit.residual, fit.se, out=np.full(2, np.inf), where=fit.se > 0)
        z[(fit.residual == 0) & (fit.se == 0)] = 0
        validation = attempt.validation
        attempts.append(
            {
                "matching_pairs": attempt.count,
                "status": fit.status,
                "evaluations": fit.evaluations,
                "residual_se_units": [float(v) if np.isfinite(v) else None for v in z],
                "validation_pass": None if validation is None else validation.passed,
                "validation_combined_se_units": None
                if validation is None
                else [float(v) if np.isfinite(v) else None for v in validation.z],
                "equivalence_statistic": None
                if validation is None
                else validation.equivalence.tolist(),
                "equivalence_pass": None
                if validation is None
                else validation.equivalence_passed,
                "amplification": None
                if validation is None
                or validation.amplification is None
                or not np.isfinite(validation.amplification)
                else validation.amplification,
            }
        )
    return {"success": result.success, "attempts": attempts}


def pipeline_record(result: PipelineResult) -> dict[str, object]:
    record = fit_record(result.fit)
    record["tie_rate"] = result.tie_rate
    record["parameters"] = result.fit.final.fit.parameters.tolist()
    if result.uncertainty is None:
        return record
    u = result.uncertainty
    record.update(
        {
            "auc": float(u.point[0]),
            "se": float(u.se[0]),
            "score_se": float(u.conditional_se[0]),
            "nuisance_variance": [n.variance for n in result.nuisance],
            "nuisance_mcse": [n.mcse for n in result.nuisance],
            "mean_shift": [n.mean_shift for n in result.nuisance],
            "projected_fraction": [n.projected_fraction for n in result.nuisance],
            "covariance_diagnostics": [
                {
                    "raw_direction_shifts": d.direction_shifts.tolist(),
                    "gaussian_moment_auc_shifts": d.auc_shifts.tolist(),
                    "max_absolute_auc_shift": d.max_absolute_auc_shift,
                    "flagged": d.flagged,
                }
                for d in result.covariance_diagnostics
            ],
        }
    )
    return record


def task_seed_plan(task: GateTask) -> SeedPlan:
    block = {"G0": 0, "G1b": 100, "G1c": 200, "G2": 300, "G2c": 400}[task.gate]
    # Independent gate cells; CRN across strengths belongs to the later curve run.
    cell_index = (
        0
        if task.gate == "G0"
        else task.index
        // (100 if task.gate == "G2" else 101 if task.gate == "G2c" else 50)
    )
    return SeedPlan(task.repetition, block + cell_index, gate=task.gate != "G0")


def run_task(task: GateTask, store: SealedStore) -> dict[str, object]:
    seeds = task_seed_plan(task)
    source = PanelSource(task.cell, seeds, store=store)
    if task.gate == "G0":
        fits = []
        for family in "ABCDE":
            observed = fit_cell(
                PanelSource(replace(task.cell, family=family), seeds, store=store)
            )
            fits.append(
                {"family": family, "channel": "observed", **fit_record(observed)}
            )
            if family == "B":
                for channel in ("latent", "ordinal_one", "latent_rank"):
                    if not observed.success:
                        fits.append(
                            {
                                "family": family,
                                "channel": channel,
                                "success": False,
                                "attempts": [],
                                "dependency_gap": True,
                            }
                        )
                    else:
                        control_fit = fit_cell(
                            PanelSource(
                                replace(task.cell, channel=channel), seeds, store=store
                            ),
                            fixed_eta=float(observed.final.fit.parameters[1]),
                        )
                        fits.append(
                            {
                                "family": family,
                                "channel": channel,
                                **fit_record(control_fit),
                            }
                        )
        return {"fits": fits, "success": True}
    if task.gate == "G1b":
        null_scores, social_scores = synthetic_scores(
            task.scenario, seed=seeds.seed("bootstrap", "state", 0)
        )
        uncertainty = score_uncertainty(
            null_scores,
            social_scores,
            np.zeros((2000, 9)),
            seed=seeds.seed("bootstrap", "network", 0),
        )
        interval = band(uncertainty)
        return {
            "success": True,
            "covered": bool(np.all((interval.lower <= 0.5) & (interval.upper >= 0.5))),
            "critical": interval.critical,
            "empirical_exceeds_floor": interval.empirical_exceeds_floor,
        }
    if task.gate == "G2c" and not task.baseline:
        fit = fit_cell(source)
        record = fit_record(fit)
        if fit.success:
            p = fit.final.fit.parameters
            left, right = (
                source.profiles("train", 2000, parameters=p)[:, 2:5],
                source.profiles("train", 2000)[:, 2:5],
            )
            model = fit_discriminant(
                np.concatenate([left, right]), np.repeat([0, 1], 2000)
            )
            reference = PanelSource(
                task.cell, replace(seeds, repetition=0), store=store
            )
            reference0 = reference.profiles("reference", 4000, parameters=p)[:, 2:5]
            reference1 = reference.profiles("reference", 4000)[:, 2:5]
            record["auc"] = auc(model.score(reference0), model.score(reference1))
        return record
    result = pipeline(
        source,
        steps=(0.01, 0.005) if task.gate == "G2" else (0.01,),
        g2_diagnostic=task.gate == "G2",
    )
    record = pipeline_record(result)
    record["mechanism_degeneracy"] = task.cell.anchor == 1
    record["truth"] = None
    if task.gate == "G1c" and result.uncertainty is not None:
        u = result.uncertainty
        point = float(np.clip(u.point[0], 1 / 4000, 1 - 1 / 4000))
        z = abs(np.log(point / (1 - point))) / (
            max(float(u.se[0]), 1 / 4000) / (point * (1 - point))
        )
        record["pointwise_failure"] = bool(z > 2.7729)
        record["truth"] = 0.5
    if (
        task.gate == "G2c"
        and result.nuisance
        and store.get_array("nuisance-aucs") is None
    ):
        store.put_array("nuisance-aucs", result.nuisance[0].aucs)
    return record


def execute_task(payload: tuple[GateTask, str, dict[str, object]]) -> dict[str, object]:
    """Only criterion counts leave the worker, including on exceptions."""
    task, root, provenance = payload
    store = SealedStore(Path(root) / task.key)
    fd = os.open(store.root / "lock", os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(fd, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        binding = {
            "task": task.record(),
            "freeze_sha256": provenance.get("freeze_sha256"),
            "binding_sha256": provenance.get("binding_sha256"),
        }
        prior_binding = store.get_json("task-binding")
        existing = store.get_json("result")
        if prior_binding is None and existing is None:
            store.put_json("task-binding", binding)
        elif prior_binding != binding:
            raise ValueError("Completed or partial task binding mismatch")
        if existing is not None:
            return {"completed": 1, "failed": int(not existing.get("success", False))}
        store.append("manifest", {"task": task.record(), **provenance})
        if store.get_json("provenance") is None:
            store.put_json(
                "provenance",
                {
                    "code_sha256": hashlib.sha256(
                        json.dumps(provenance.get("code", {}), sort_keys=True).encode()
                    ).hexdigest(),
                    "environment_sha256": provenance.get("environment_sha256"),
                    "host_sha256": provenance.get("host_sha256"),
                },
            )
        with store.capture_output():
            record = run_task(task, store)
        store.append("estimates", record)
        store.put_json("result", record)
        store.seal()
        return {"completed": 1, "failed": int(not record.get("success", False))}


def aggregate(
    gate: str,
    root: Path,
    criteria: dict[str, object],
    *,
    cells: tuple[tuple[float, float], ...] = G2_CELLS,
    binding: dict[str, str] | None = None,
) -> dict[str, object]:
    tasks = gate_tasks(gate, cells=cells)
    rows = []
    for task in tasks:
        path = root / task.key
        if not path.is_dir():
            continue
        store = SealedStore(path)
        value = store.get_json("result")
        if value is not None:
            if binding is not None and store.get_json("task-binding") != {
                "task": task.record(),
                **binding,
            }:
                raise ValueError("Aggregated task binding mismatch")
            rows.append((task, value))
    failures = sum(not value.get("success", False) for _, value in rows)
    summary: dict[str, object] = {
        "gate": gate,
        "planned": len(tasks),
        "completed": len(rows),
        "failures": failures,
        "pass": False,
    }
    if len(rows) != len(tasks) or (failures and gate not in {"G2", "G2c"}):
        if gate == "G2":
            summary["denominator"] = len(tasks)
            summary["cell_failure_counts"] = [
                sum(
                    not row.get("success", False)
                    for task, row in rows
                    if task.index // 100 == ci
                )
                for ci in range(len(cells))
            ]
        return summary
    if gate == "G0":
        statuses: dict[str, int] = {}
        anchors = budget = implementation = fits_count = 0
        for task, row in rows:
            for fit in cast(list[dict[str, object]], row["fits"]):
                fits_count += 1
                attempts = cast(list[dict[str, object]], fit["attempts"])
                for attempt in attempts:
                    status = str(attempt["status"])
                    statuses[status] = statuses.get(status, 0) + 1
                    budget += int(status == "budget")
                    implementation += int(
                        status in {"numerical-limit", "ill-conditioned"}
                    )
                if task.cell.share == 0 and fit["family"] != "C":
                    anchors += int(
                        not attempts
                        or attempts[-1]["status"] != "anchor-exact"
                        or not fit["success"]
                    )
        summary.update(
            {
                "matching_mask": [
                    {"a": task.cell.share, "r": task.cell.reliability, **fit}
                    for task, row in rows
                    for fit in cast(list[dict[str, object]], row["fits"])
                ],
                "statuses": statuses,
                "fits": fits_count,
                "anchor_failures": anchors,
                "implementation_statuses": implementation,
                "budget_statuses": budget,
                "pass": anchors == 0
                and budget == 0
                and implementation / fits_count <= 0.01,
            }
        )
    elif gate == "G1b":
        counts = {
            scenario: sum(
                bool(row["covered"]) for task, row in rows if task.scenario == scenario
            )
            for scenario in {task.scenario for task in tasks}
        }
        summary.update(
            {
                "coverage_counts": counts,
                "empirical_exceeds_floor_count": sum(
                    bool(row["empirical_exceeds_floor"]) for _, row in rows
                ),
                "pass": min(counts.values()) >= 935,
            }
        )
    elif gate == "G1c":
        values = np.array([row["auc"] for _, row in rows], dtype=float)
        mean_z = abs(float(values.mean()) - 0.5) / (
            float(values.std(ddof=1)) / np.sqrt(150)
        )
        pointwise = sum(bool(row["pointwise_failure"]) for _, row in rows)
        anchors = sum(
            cast(list[dict[str, object]], row["attempts"])[-1]["status"]
            == "anchor-exact"
            for _, row in rows
        )
        summary.update(
            {
                "pointwise_failures": pointwise,
                "anchor_count": anchors,
                "mean_z": mean_z,
                "tie_rate": float(np.mean([row["tie_rate"] for _, row in rows])),
                "pass": anchors == 150 and pointwise <= 3 and mean_z <= 3,
            }
        )
    elif gate == "G2":
        points = np.array(
            [row.get("auc", np.nan) for _, row in rows], dtype=float
        ).reshape(len(cells), 100)
        errors = np.array(
            [row.get("se", np.nan) for _, row in rows], dtype=float
        ).reshape(len(cells), 100)
        success = np.array(
            [bool(row.get("success", False)) for _, row in rows]
        ).reshape(len(cells), 100)
        report = dispersion(points, errors, success, seed=80925)
        variances = np.array(
            [row.get("nuisance_variance", [np.nan, np.nan]) for _, row in rows],
            dtype=float,
        ).reshape(len(cells), 100, 2)
        fd_report = fd_stability(
            variances, success & np.isfinite(points) & np.isfinite(errors)
        )
        sealed = SealedStore(root)
        if sealed.get_json("G2-auc-diagnostics") is None:
            sealed.put_json(
                "G2-auc-diagnostics",
                {"mean_shift": [row.get("mean_shift") for _, row in rows]},
            )
        summary.update(
            {
                **report,
                **fd_report,
                "covariance_flag_counts": [
                    sum(
                        any(
                            d["flagged"]
                            for d in cast(
                                list[dict[str, Any]],
                                row.get("covariance_diagnostics", []),
                            )
                        )
                        for task, row in rows
                        if task.index // 100 == ci
                    )
                    for ci in range(len(cells))
                ],
                "pass": bool(fd_report["fd_stable"])
                and dispersion_pass(report, cast(Thresholds, criteria["thresholds"])),
            }
        )
    elif gate == "G2c":
        reports = []
        for a, _ in ((0.1, 100), (0.03, 40)):
            baseline = next(
                task for task, _ in rows if task.cell.share == a and task.baseline
            )
            local = SealedStore(root / baseline.key).get_array("nuisance-aucs")
            baseline_row = next(row for task, row in rows if task == baseline)
            if local is None or not baseline_row.get("success", False):
                return summary
            refits = np.array(
                [
                    row.get("auc", np.nan) if row.get("success", False) else np.nan
                    for task, row in rows
                    if task.cell.share == a and not task.baseline
                ],
                dtype=float,
            )
            reports.append(refit_ratio(local, refits, seed=81925))
        summary.update(
            {"comparisons": reports, "pass": all(report["pass"] for report in reports)}
        )
    return summary


def status_digest(statuses: list[dict[str, Any]]) -> str:
    return hashlib.sha256(
        json.dumps(
            statuses, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def g0_statuses(root: SealedStore) -> list[dict[str, Any]]:
    """Project only completed statuses, excluding fitted parameters and residuals."""
    statuses = []
    for task in gate_tasks("G0"):
        result = SealedStore(root.root / task.key).get_json("result")
        if result is None or "fits" not in result:
            raise ValueError("G0 statuses incomplete")
        statuses.append(
            {
                "a": task.cell.share,
                "r": task.cell.reliability,
                "fits": [
                    {
                        "family": f["family"],
                        "channel": f["channel"],
                        "success": f["success"],
                        "attempts": [
                            {
                                "status": a["status"],
                                "validation_passed": a.get("validation_pass"),
                            }
                            for a in f["attempts"]
                        ],
                    }
                    for f in cast(list[dict[str, Any]], result["fits"])
                ],
            }
        )
    return statuses


def g0_gap_binding(
    statuses: list[dict[str, Any]],
    cells: tuple[tuple[float, float], ...],
    criteria: dict[str, Any],
) -> dict[str, object]:
    """Posterior predictive waste guard for the G2 and G2c gap allowances."""
    fits = [
        fit
        for row in statuses
        if 0 < row["a"] <= 0.30
        for fit in row["fits"]
        if fit["family"] == "B" and fit["channel"] == "observed"
    ]
    if len(fits) != 54:
        raise ValueError("Require all 54 G0 B/observed G2-strength fits")
    gaps = sum(not bool(fit["success"]) for fit in fits)
    seed = 250925006
    simulations = 200_000
    rng = np.random.default_rng(seed)
    rates = rng.beta(gaps + 0.5, 54 - gaps + 0.5, simulations)
    cell_failures = rng.binomial(100, rates[:, None], size=(simulations, len(cells)))
    refits = criteria["G2c_refits"]
    g2c_allowances = [
        criteria["failure_rule"]["G2c_per_100"],
        criteria["failure_rule"]["G2c_per_40"],
    ]
    g2c_failures = [rng.binomial(count, rates) for count in refits]
    pooled_allowance = ceil(0.02 * 100 * len(cells))
    passes = (
        np.all(cell_failures <= criteria["failure_rule"]["G2_per_100"], axis=1)
        & (cell_failures.sum(axis=1) <= pooled_allowance)
        & np.logical_and.reduce(
            [
                failures <= allowance
                for failures, allowance in zip(
                    g2c_failures, g2c_allowances, strict=True
                )
            ]
        )
    )
    return {
        "gaps": gaps,
        "denominator": 54,
        "cells": [list(cell) for cell in cells],
        "posterior_alpha": gaps + 0.5,
        "posterior_beta": 54 - gaps + 0.5,
        "G2_pooled_allowance": pooled_allowance,
        "G2c_allowances": g2c_allowances,
        "seed": seed,
        "simulations": simulations,
        "pass_probability": float(passes.mean()),
        "minimum": 0.80,
        "method": "Jeffreys-beta-binomial-posterior-predictive-G2-G2c",
    }


class GapRateStopError(ValueError):
    def __init__(self, report: dict[str, object]) -> None:
        super().__init__("Stop before G2: G0 predictive pass probability below 0.80")
        self.report = report


def allocation_preflight(
    path: Path,
    freeze_sha256: str,
    statuses: list[dict[str, Any]],
    criteria_bytes: bytes,
) -> tuple[tuple[float, float], ...]:
    if not path.is_file():
        raise ValueError("A second binding record is required before G2")
    record = json.loads(path.read_bytes())
    if (
        record.get("schema") != 1
        or record.get("stage") != "post-G0-pre-G2"
        or record.get("freeze_sha256") != freeze_sha256
        or record.get("g0_statuses_sha256") != status_digest(statuses)
        or record.get("criteria_sha256") != hashlib.sha256(criteria_bytes).hexdigest()
    ):
        raise ValueError("Second-stage binding mismatch")
    eligible = {
        (row["a"], row["r"])
        for row in statuses
        if any(
            f["family"] == "B" and f["channel"] == "observed" and f["success"]
            for f in row["fits"]
        )
    }
    cells = tuple(tuple(cell) for cell in record.get("g2_cells", []))
    criteria = json.loads(criteria_bytes)
    study = Path(__file__).resolve().parents[3]
    for key, source in (
        ("implementation_sha256", Path(__file__).with_name("v4_criteria.py")),
        (
            "script_sha256",
            study
            / "experiments/exploratory/detection-boundary-v4/calibrate_criteria.py",
        ),
    ):
        if criteria.get(key) != hashlib.sha256(source.read_bytes()).hexdigest():
            raise ValueError("Second-stage criteria must bind calibrated code")
    if (
        cells != tuple(substitute_cells(eligible))
        or len(cells) != criteria["G2_cells"]
        or not criteria["joint_targets_met"]
    ):
        raise ValueError(
            "Second-stage allocation requires matching recalibrated criteria"
        )
    measured = g0_gap_binding(statuses, cells, criteria)
    if record.get("g0_gap_binding") != measured:
        raise ValueError("Second-stage G0 measured gap-rate binding mismatch")
    if float(cast(float, measured["pass_probability"])) < 0.80:
        raise GapRateStopError(measured)
    return cells


def authorize_stage(
    root: SealedStore,
    gate: str,
    freeze_digest: str,
    binding_digest: str,
    *,
    create: bool = True,
) -> None:
    authorization: dict[str, object] = {
        "freeze_sha256": freeze_digest,
        "binding_sha256": binding_digest,
    }
    if gate == "G2c" and root.get_json("authorization-G2") != authorization:
        raise ValueError("G2 binding must also govern G2c")
    key = "authorization-" + gate
    prior = root.get_json(key)
    if prior is None:
        if create:
            root.put_json(key, authorization)
    elif prior != authorization:
        raise ValueError("No rerun under changed gate criteria or allocation")
