"""Private calibration-only cost and coverage machinery for the frozen protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from ic_study.analysis.detection_boundary import auc, feasible_lag1, match_observed_lags
from ic_study.analysis.redesign import Discriminant, fit_discriminant
from ic_study.models.anchored_panel import Floats
from ic_study.simulation.detection_calibration import CellFit, DetectionPilot, PilotSpec


class CoveragePilot(DetectionPilot):
    def __init__(
        self, spec: PilotSpec, output: Path, *, repetition: int, block: int
    ) -> None:
        if repetition < 0 or not 0 <= block <= 40:
            raise ValueError("Invalid coverage repetition or refit block")
        super().__init__(spec, output)
        self.repetition = repetition
        self.block = block
        self.namespace = (
            f"ic-detection-boundary-v3-coverage-r{repetition:04d}-calibration"
        )

    def seed(self, phase: str, role: str, i: int) -> int:
        if phase not in {"match", "train", "check", "reference"} or i < 0:
            raise ValueError("Only calibration phases are available")
        block = 0 if phase == "reference" else self.block
        material = f"{self.namespace}|{block}|{phase}|{role}|{i}"
        return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


def match_observed(pilot: CoveragePilot, share: float) -> CellFit:
    target = np.stack(
        [
            pilot.panel("match", 2 * i + 1, share, observed_only=True)["observed"][:2]
            for i in range(pilot.spec.matching)
        ]
    )
    if not feasible_lag1(float(target[:, 0].mean()), pilot.spec.reliability):
        raise ValueError("Infeasible reliability/target cell before classification")
    fit = match_observed_lags(
        target,
        lambda rho, trait: np.stack(
            [
                pilot.panel(
                    "match",
                    2 * i + 1,
                    share,
                    rho=rho,
                    trait=trait,
                    observed_only=True,
                )["observed"][:2]
                for i in range(pilot.spec.matching)
            ]
        ),
    )
    return CellFit(fit.rho, fit.trait, "observed", float(target[:, 0].mean()))


def observed_features(
    pilot: CoveragePilot,
    phase: str,
    share: float,
    fit: CellFit,
    label: int,
    count: int,
) -> Floats:
    if label not in (0, 1) or count < 1:
        raise ValueError("Require a class and at least one event")
    features = np.empty((count, 3))
    for i in range(count):
        features[i] = pilot.panel(
            phase,
            2 * i + label,
            share,
            rho=fit.rho if label == 0 else None,
            trait=fit.trait,
            observed_only=True,
        )["observed"][2:5]
    return features


def train_discriminant(
    pilot: CoveragePilot, share: float, fit: CellFit
) -> Discriminant:
    null = observed_features(pilot, "train", share, fit, 0, pilot.spec.training)
    influence = observed_features(pilot, "train", share, fit, 1, pilot.spec.training)
    return fit_discriminant(
        np.concatenate((null, influence)),
        np.repeat([0, 1], pilot.spec.training),
    )


@dataclass(frozen=True)
class RefitResult:
    block: int
    auc: float
    matching_seconds: float
    training_seconds: float
    reference_seconds: float
    panels: int
    rho: float
    trait: float


def run_refit(
    spec: PilotSpec,
    repetition: int,
    block: int,
    share: float,
    output: Path,
    social_reference: Floats,
) -> RefitResult:
    if block == 0 or social_reference.shape != (spec.checking, 3):
        raise ValueError("Refit requires a fixed social reference population")
    pilot = CoveragePilot(spec, output, repetition=repetition, block=block)
    started = time.perf_counter()
    fit = match_observed(pilot, share)
    matched = time.perf_counter()
    model = train_discriminant(pilot, share, fit)
    trained = time.perf_counter()
    null_reference = observed_features(pilot, "reference", share, fit, 0, spec.checking)
    value = auc(model.score(null_reference), model.score(social_reference))
    evaluated = time.perf_counter()
    return RefitResult(
        block=block,
        auc=value,
        matching_seconds=matched - started,
        training_seconds=trained - matched,
        reference_seconds=evaluated - trained,
        panels=pilot.panels,
        rho=fit.rho,
        trait=fit.trait,
    )


def cost_probe(
    output: Path, *, repetition: int, share: float, reliability: float, workers: int
) -> dict[str, object]:
    if not 1 <= workers <= 8:
        raise ValueError("Keep at least two of ten cores free")
    os.umask(0o077)
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    spec = PilotSpec(
        grid=(share,),
        reliability=reliability,
        matching=1024,
        training=2000,
        checking=4000,
        seconds=3600,
    )
    reference = CoveragePilot(
        spec, output / "reference", repetition=repetition, block=0
    )
    dummy = CellFit(0.85, 0.0, "observed", 0.0)
    started = time.perf_counter()
    social_reference = observed_features(
        reference, "reference", share, dummy, 1, spec.checking
    )
    reference_seconds = time.perf_counter() - started
    results: list[dict[str, object]] = []
    with (
        (output / "refits.jsonl").open("w") as stream,
        ProcessPoolExecutor(max_workers=workers) as pool,
    ):
        futures = {
            pool.submit(
                run_refit,
                spec,
                repetition,
                block,
                share,
                output / f"refit-{block:02d}",
                social_reference,
            ): block
            for block in range(1, 41)
        }
        for future in as_completed(futures):
            block = futures[future]
            try:
                row: dict[str, object] = asdict(future.result())
            except (ValueError, TimeoutError) as exc:
                row = {"block": block, "error": str(exc)}
            results.append(row)
            stream.write(json.dumps(row, sort_keys=True) + "\n")
            stream.flush()
    summary: dict[str, object] = {
        "status": (
            "complete" if all("error" not in row for row in results) else "failed"
        ),
        "repetition": repetition,
        "share": share,
        "reliability": reliability,
        "namespace": reference.namespace,
        "blocks": 40,
        "successful_refits": sum("error" not in row for row in results),
        "reference_social_seconds": reference_seconds,
        "wall_seconds": time.perf_counter() - started,
        "workers": workers,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repetition", type=int, default=0)
    parser.add_argument("--strength", type=float, default=0.0)
    parser.add_argument("--reliability", type=float, default=0.7)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    summary = cost_probe(
        args.output,
        repetition=args.repetition,
        share=args.strength,
        reliability=args.reliability,
        workers=args.workers,
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
