"""Bounded decision-14 sanity pilot; no confirmatory execution or AUC disclosure."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ic_study.analysis.detection_boundary import (
    boundary,
    feasible_lag1,
    feature_channels,
    lag_profile,
    match_lag1,
    match_observed_lags,
)
from ic_study.analysis.redesign import fit_discriminant
from ic_study.models.anchored_panel import Floats, panel_mask
from ic_study.models.detection_panel import (
    influence_panel,
    measurement,
    mover_stayer_panel,
    null_panel,
    ordinal_channel,
    state_dependent_panel,
    tenure_reliability,
)

NAMESPACE = "ic-detection-boundary-v3-calibration"


def calibration_seed(phase: str, role: str, index: int, *, replicate: int = 0) -> int:
    if phase not in {"match", "train", "check", "reference"} or replicate < 0:
        raise ValueError("Only fresh calibration phases are available")
    block = 0 if phase == "reference" else replicate
    material = f"{NAMESPACE}|{block}|{phase}|{role}|{index}"
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


def disclosure(grid: Floats, values: Floats) -> dict[str, bool]:
    point = boundary(grid, values)
    return {"interior_at_r070": bool(point is not None and grid[0] < point < grid[-1])}


@dataclass(frozen=True)
class PilotSpec:
    grid: tuple[float, ...]
    size: int = 10626
    waves: int = 11
    retention: float = 0.89
    reliability: float = 0.70
    matching: int = 256
    training: int = 64
    checking: int = 64
    seconds: int = 600
    repulsion: float = 0.25
    interactions: int = 1
    error_correlation: float = 0
    reliability_gain: float = 0
    events_per_network: int = 2
    replicate: int = 0


@dataclass(frozen=True)
class CellFit:
    rho: float
    trait: float
    channel: str
    target_lag1: float


class DetectionPilot:
    def __init__(self, spec: PilotSpec, output: Path) -> None:
        if spec.matching < 256 or not 0.5 <= spec.reliability <= 0.9:
            raise ValueError(
                "Require >=256 matches and reliability in the declared grid range"
            )
        output.mkdir(parents=True, exist_ok=False)
        self.spec, self.output = spec, output
        self.started = time.monotonic()
        self.seeds: dict[str, int] = {}
        self.panels = 0
        self.targets: dict[tuple[float, str], list[dict[str, Floats]]] = {}
        self.joint_fits: dict[tuple[float, str], tuple[float, float]] = {}

    def seed(self, phase: str, role: str, i: int) -> int:
        value = calibration_seed(phase, role, i, replicate=self.spec.replicate)
        self.seeds[f"{phase}|{role}|{i}"] = value
        return value

    def check_time(self) -> None:
        if time.monotonic() - self.started > self.spec.seconds:
            raise TimeoutError("Fixed pilot compute budget exhausted")

    def mask(self, phase: str, i: int) -> NDArray[np.bool_]:
        return panel_mask(
            self.spec.size,
            self.spec.waves,
            self.seed(phase, "mask", i),
            retention=self.spec.retention,
        )

    def panel(
        self,
        phase: str,
        i: int,
        share: float,
        *,
        rho: float | None = None,
        trait: float = 0,
        family: str = "B",
        observed_only: bool = False,
    ) -> dict[str, Floats]:
        self.check_time()
        spec = self.spec
        if family not in {"A", "B", "C", "D", "E"}:
            raise ValueError("Unknown null family")
        if rho is None:
            z = influence_panel(
                spec.size,
                spec.waves,
                self.seed(phase, "state", i),
                self.seed(
                    phase,
                    "network",
                    i if phase == "match" else i // (2 * spec.events_per_network),
                ),
                share=share,
                repulsion=spec.repulsion,
                interactions=spec.interactions,
            )
        elif family == "D":
            z = state_dependent_panel(
                spec.size,
                spec.waves,
                self.seed(phase, "null-state", i),
                center=rho,
                heterogeneity=trait,
            )
        elif family == "E":
            z = mover_stayer_panel(
                spec.size,
                spec.waves,
                self.seed(phase, "null-state", i),
                rho=rho,
                stayers=trait,
            )
        else:
            z = null_panel(
                spec.size,
                spec.waves,
                self.seed(phase, "null-state", i),
                rho=rho,
                trait=trait,
            )
        mask = self.mask(phase, i)
        reliability: float | Floats = spec.reliability
        if spec.reliability_gain:
            reliability = tenure_reliability(
                mask, spec.reliability, spec.reliability_gain
            )
        measured = measurement(
            z,
            reliability,
            self.seed(phase, "error", i),
            heteroscedastic=family == "C" and rho is not None,
            error_correlation=spec.error_correlation,
        )
        y = ordinal_channel(
            measured,
            mask,
            midpoint_mass=0.1 if family == "C" else 0,
            heap_seed=self.seed(phase, "heap", i)
            if family == "C" and rho is not None
            else None,
        )
        self.panels += 1
        if observed_only:
            return {"observed": lag_profile(np.where(mask, y, np.nan))}
        return feature_channels(z, y, midpoint_mass=0.1 if family == "C" else 0)

    def match_cell(self, share: float, *, family: str, channel: str) -> CellFit:
        if channel not in {"observed", "latent", "ordinal_one", "latent_rank"}:
            raise ValueError("Matching requires a lag channel")
        key = (share, family)
        if key not in self.targets:
            self.targets[key] = [
                self.panel("match", 2 * i + 1, share, family=family)
                for i in range(self.spec.matching)
            ]
        profiles = self.targets[key]
        target = np.stack([p[channel] for p in profiles])
        if channel == "observed" and not feasible_lag1(
            float(target[:, 0].mean()),
            min(0.95, self.spec.reliability + self.spec.reliability_gain)
            if self.spec.reliability_gain
            else self.spec.reliability,
            error_correlation=self.spec.error_correlation,
        ):
            raise ValueError("Infeasible reliability/target cell before classification")
        trait = 0.0
        if family in {"B", "D", "E"}:
            if key not in self.joint_fits:
                observed = np.stack([p["observed"][:2] for p in profiles])
                joint = match_observed_lags(
                    observed,
                    lambda rho, lam: np.stack(
                        [
                            self.panel(
                                "match",
                                2 * i + 1,
                                share,
                                rho=rho,
                                trait=lam,
                                family=family,
                            )["observed"][:2]
                            for i in range(self.spec.matching)
                        ]
                    ),
                )
                self.joint_fits[key] = (joint.rho, joint.trait)
            rho, trait = self.joint_fits[key]
            if channel == "observed":
                return CellFit(rho, trait, channel, float(target[:, 0].mean()))
        fit = match_lag1(
            target[:, 0],
            lambda rho: np.array(
                [
                    self.panel(
                        "match", 2 * i + 1, share, rho=rho, trait=trait, family=family
                    )[channel][0]
                    for i in range(self.spec.matching)
                ]
            ),
            (0.0, 0.999),
            max_evaluations=64,
        )
        return CellFit(fit.rho, trait, channel, float(target[:, 0].mean()))

    def scores(
        self,
        share: float,
        fitted: CellFit,
        *,
        family: str,
        mobility: bool = False,
        evaluation_phase: str = "check",
    ) -> tuple[Floats, Floats]:
        if evaluation_phase not in {"check", "reference"}:
            raise ValueError("Only calibration evaluation phases are available")
        key = fitted.channel + "_mobility" if mobility else fitted.channel
        feature_slice = slice(None) if mobility else slice(2, 5)
        buckets: list[list[list[Floats]]] = [[[], []], [[], []]]
        for k, (phase, count) in enumerate(
            (("train", self.spec.training), (evaluation_phase, self.spec.checking))
        ):
            for label in (0, 1):
                for i in range(count):
                    channels = self.panel(
                        phase,
                        2 * i + label,
                        share,
                        rho=fitted.rho if label == 0 else None,
                        trait=fitted.trait,
                        family=family,
                    )
                    buckets[k][label].append(channels[key][feature_slice])
        model = fit_discriminant(
            np.concatenate([np.stack(v) for v in buckets[0]]),
            np.repeat([0, 1], self.spec.training),
        )
        return model.score(np.stack(buckets[1][0])), model.score(
            np.stack(buckets[1][1])
        )

    def run(self) -> dict[str, object]:
        """Operational matching check only: no new primary gates or scores disclosed."""
        matched = 0
        report: dict[str, object] = {
            "status": "incomplete",
            "primary_contrasts": "hidden",
        }
        try:
            for share in self.spec.grid:
                self.match_cell(share, family="B", channel="observed")
                matched += 1
            report["status"] = "complete"
        except (ValueError, TimeoutError) as exc:
            report["failure"] = str(exc)
        finally:
            report.update(
                {
                    "matched_cells": matched,
                    "elapsed_seconds": time.monotonic() - self.started,
                    "namespace": NAMESPACE,
                    "panels": self.panels,
                }
            )
            (self.output / "seed-ledger.json").write_text(
                json.dumps(self.seeds, indent=2) + "\n"
            )
            (self.output / "summary.json").write_text(
                json.dumps(report, indent=2) + "\n"
            )
        return report
