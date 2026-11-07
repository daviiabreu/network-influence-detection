"""Bounded exploratory calibration; primary outcomes leave only coarse gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import signal
import subprocess
import sys
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.analysis.redesign import (
    balanced_accuracy,
    critical_dose,
    fit_discriminant,
    lag_correlation,
    lag_features,
)
from ic_study.models.anchored_panel import (
    Floats,
    Integers,
    latent_panel,
    observe,
    panel_mask,
)
from ic_study.models.critical_dose import make_groups, run_dose

PILOT_PHASES = {
    "match",
    "operating-train",
    "operating-check",
    "primary-train",
    "primary-check",
    "dose-calibration",
    "dose-check",
}


def pilot_seed(phase: str, role: str, index: int) -> int:
    if phase not in PILOT_PHASES:
        raise ValueError("Unknown phase or forbidden confirmatory namespace")
    text = f"ic-redesign-v1|{phase}|{role}|{index}"
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:8], "big")


def operating_choice(rows: Sequence[tuple[float, float, float]]) -> float | None:
    for strength, baseline_accuracy, lag_gap in rows:
        if 0.68 <= baseline_accuracy <= 0.82 and abs(lag_gap) <= 0.01:
            return strength
    return None


def panel_gate(accuracy: float) -> dict[str, bool]:
    return {"non_floor_non_ceiling": 0.55 < accuracy < 0.95}


def dose_gate(
    doses: Sequence[float], rates: Sequence[Sequence[float]]
) -> dict[str, bool]:
    from ic_study.analysis.redesign import critical_dose

    return {
        "each_arm_has_interior_cell": all(
            any(0.1 < p < 0.9 for p in row) for row in rates
        ),
        "both_cross_half": all(critical_dose(doses, row) is not None for row in rates),
    }


@dataclass(frozen=True)
class CalibrationSpec:
    panel_size: int
    waves: int
    retention: float
    strengths: list[float]
    match_count: int
    operating_count: int
    primary_count: int
    baseline_reliability: float
    primary_reliability: float
    social_rho: float
    dose_size: int
    dose_count: int
    doses: list[float]
    bisections: int
    horizon: int
    coefficient: float
    max_seconds: int


class CalibrationRun:
    def __init__(self, spec: CalibrationSpec, destination: Path) -> None:
        self.spec = spec
        destination.mkdir(parents=True, exist_ok=False)
        self.destination = destination
        self.started = time.perf_counter()
        self.simulations = 0
        self.records: list[dict[str, Any]] = []

    def check_budget(self) -> None:
        if time.perf_counter() - self.started >= self.spec.max_seconds:
            raise TimeoutError("Exploratory compute budget exhausted")

    def record(self, kind: str, **values: Any) -> None:
        row = {"kind": kind, **values}
        self.records.append(row)
        with (self.destination / "progress.jsonl").open("a") as stream:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
        print(json.dumps(row, sort_keys=True), flush=True)

    def panel(
        self, phase: str, index: int, strength: float, rho: float
    ) -> tuple[Floats, Integers, float]:
        self.check_budget()
        seeds = {
            role: pilot_seed(phase, role, index)
            for role in ("state", "network", "events", "mask", "error")
        }
        latent = latent_panel(
            self.spec.panel_size,
            self.spec.waves,
            seeds["state"],
            seeds["network"],
            seeds["events"],
            rho=rho,
            strength=strength,
        )
        mask = panel_mask(
            self.spec.panel_size,
            self.spec.waves,
            seeds["mask"],
            retention=self.spec.retention,
        )
        reliability = (
            self.spec.primary_reliability
            if phase.startswith("primary")
            else self.spec.baseline_reliability
        )
        response = observe(latent, mask, reliability, seeds["error"])
        self.simulations += 1
        with (self.destination / "panel-ledger.jsonl").open("a") as stream:
            stream.write(
                json.dumps(
                    {
                        "phase": phase,
                        "index": index,
                        "seeds": seeds,
                        "strength": strength,
                        "rho": rho,
                        "reliability": reliability,
                        "latent_sha256": hashlib.sha256(latent.tobytes()).hexdigest(),
                        "response_sha256": hashlib.sha256(
                            response.tobytes()
                        ).hexdigest(),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
        return latent, response, lag_correlation(latent, 1, missing=False)

    def sample(
        self, phase: str, count: int, strength: float, rho: float
    ) -> tuple[Floats, Integers, dict[str, float]]:
        features = []
        labels = []
        correlations: list[list[float]] = [[], []]
        histograms: list[list[Floats]] = [[], []]
        counts = []
        for i in range(count):
            for label in (0, 1):
                _, response, _ = self.panel(
                    phase,
                    2 * i + label,
                    strength if label else 0,
                    self.spec.social_rho if label else rho,
                )
                features.append(lag_features(response))
                labels.append(label)
                correlations[label].append(lag_correlation(response, 1, missing=True))
                histogram = np.bincount(response[response >= 0], minlength=11)
                histograms[label].append(histogram / histogram.sum())
                counts.append(int(np.sum((response[:-1] >= 0) & (response[1:] >= 0))))
        diagnostic = {
            "observed_lag1_gap": float(
                np.mean(correlations[1]) - np.mean(correlations[0])
            ),
            "observed_marginal_total_variation": float(
                0.5
                * np.abs(
                    np.mean(histograms[1], axis=0) - np.mean(histograms[0], axis=0)
                ).sum()
            ),
            "mean_adjacent_pairs": float(np.mean(counts)),
        }
        return np.stack(features), np.array(labels, dtype=np.int64), diagnostic

    def calibrate_panel(self) -> None:
        selected: tuple[float, float] | None = None
        for strength in self.spec.strengths:
            target = np.mean(
                [
                    self.panel("match", i, strength, self.spec.social_rho)[2]
                    for i in range(self.spec.match_count)
                ]
            )
            rho = float(np.clip(target, 0, 1))
            achieved = np.mean(
                [
                    self.panel("match", self.spec.match_count + i, 0, rho)[2]
                    for i in range(self.spec.match_count)
                ]
            )
            train, labels, _ = self.sample(
                "operating-train", self.spec.operating_count, strength, rho
            )
            check, truth, diagnostics = self.sample(
                "operating-check", self.spec.operating_count, strength, rho
            )
            model = fit_discriminant(train, labels)
            baseline_accuracy = balanced_accuracy(model.score(check), truth)
            gap = float(target - achieved)
            self.record(
                "panel_operating",
                strength=strength,
                rho=rho,
                latent_lag1_gap=gap,
                baseline_accuracy=baseline_accuracy,
                **diagnostics,
            )
            if operating_choice([(strength, baseline_accuracy, gap)]) is not None:
                selected = strength, rho
                break
        if selected is None:
            self.record("panel_selection", status="failed_no_operating_point")
            return
        strength, rho = selected
        self.record("panel_selection", status="selected", strength=strength, rho=rho)
        train, labels, _ = self.sample(
            "primary-train", self.spec.primary_count, strength, rho
        )
        check, truth, diagnostics = self.sample(
            "primary-check", self.spec.primary_count, strength, rho
        )
        model = fit_discriminant(train, labels)
        self.record(
            "panel_primary_gate",
            **panel_gate(balanced_accuracy(model.score(check), truth)),
            **diagnostics,
        )

    def dose_rate(self, phase: str, dose: float, projected: bool) -> float:
        locked = 0
        for i in range(self.spec.dose_count):
            self.check_budget()
            groups = make_groups(self.spec.dose_size, pilot_seed(phase, "network", i))
            rng = np.random.default_rng(pilot_seed(phase, "state", i))
            initial = np.where(
                rng.permutation(self.spec.dose_size) < round(0.7 * self.spec.dose_size),
                0.2,
                0.8,
            ) + rng.normal(0, 0.05, self.spec.dose_size)
            initial = np.clip(initial, 0, 1)
            recipients = np.random.default_rng(pilot_seed(phase, "source", i)).choice(
                self.spec.dose_size, round(0.1 * self.spec.dose_size), replace=False
            )
            outcome = run_dose(
                initial,
                groups,
                recipients,
                dose,
                self.spec.coefficient,
                projected=projected,
                horizon=self.spec.horizon,
            )
            locked += outcome.status == "locked"
            self.simulations += 1
        return locked / self.spec.dose_count

    def calibrate_dose(self) -> None:
        rates = {}
        for dose in self.spec.doses:
            rate = self.dose_rate("dose-calibration", dose, True)
            rates[dose] = rate
            self.record("dose_operating", dose=dose, control_lock_probability=rate)
        if rates[self.spec.doses[0]] < 0.9 or rates[self.spec.doses[-1]] > 0.1:
            self.record("dose_selection", status="failed_no_bracket")
            return
        for _ in range(self.spec.bisections):
            ordered = sorted(rates)
            crossing = next(i for i, d in enumerate(ordered) if rates[d] <= 0.5)
            dose = (ordered[crossing - 1] + ordered[crossing]) / 2
            rate = self.dose_rate("dose-calibration", dose, True)
            rates[dose] = rate
            self.record("dose_operating", dose=dose, control_lock_probability=rate)
        doses = sorted(rates)
        probabilities = [rates[d] for d in doses]
        if any(b - a > 0.1 for a, b in pairwise(probabilities)):
            self.record("dose_selection", status="failed_nonmonotonic")
            return
        self.record(
            "dose_selection",
            status="selected",
            doses=doses,
            control_critical_dose=critical_dose(doses, probabilities),
        )
        checked = [
            [self.dose_rate("dose-check", d, projected) for d in doses]
            for projected in (False, True)
        ]
        self.record("dose_primary_gate", **dose_gate(doses, checked))


def _deadline(_signum: int, _frame: object) -> None:
    raise TimeoutError("Exploratory compute deadline reached")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.spec = arguments.spec.resolve()
    spec = CalibrationSpec(**json.loads(arguments.spec.read_text()))
    if not 1 <= spec.max_seconds <= 1200:
        raise ValueError("Pilot budget must be between 1 and 1200 seconds")
    run = CalibrationRun(spec, arguments.output)
    project = Path(__file__).resolve().parents[3]
    root = project.parents[1]
    paths = [
        *sorted((project / "src/ic_study").rglob("*.py")),
        project / "uv.lock",
        arguments.spec.resolve(),
        arguments.spec.parent / "protocol.md",
    ]
    metadata = {
        "started_utc": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "tracked_diff": subprocess.check_output(
            ["git", "diff", "HEAD", "--stat"], cwd=root, text=True
        ),
        "inputs_sha256": {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths
        },
        "spec": asdict(spec),
        "seed_rule": "SHA256 ic-redesign-v1|phase|role|index, first 8 bytes big endian",
        "dose_seed_roles": ["network", "state", "source"],
        "dose_indices": [0, spec.dose_count - 1],
        "confirmatory_runs": 0,
    }
    (arguments.output / "manifest.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    signal.signal(signal.SIGALRM, _deadline)
    signal.setitimer(signal.ITIMER_REAL, spec.max_seconds)
    status = "completed"
    try:
        run.calibrate_panel()
        run.calibrate_dose()
    except (TimeoutError, ValueError, RuntimeError) as error:
        status = f"incomplete: {type(error).__name__}: {error}"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        summary = {
            "status": status,
            "elapsed_seconds": time.perf_counter() - run.started,
            "simulations": run.simulations,
            "records": run.records,
            "primary_values_exported": False,
        }
        (arguments.output / "summary.json").write_text(
            json.dumps(summary, indent=2) + "\n"
        )
        print(
            json.dumps({k: v for k, v in summary.items() if k != "records"}), flush=True
        )
    if status != "completed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
