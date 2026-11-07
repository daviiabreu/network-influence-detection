"""Frozen-order, resumable confirmatory curves; estimates stay private until close."""

from __future__ import annotations

import fcntl
import hashlib
import json
import signal
from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.analysis.detection_boundary_v4 import (
    band,
    curve_report,
    score_uncertainty,
)
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    Cell,
    ControlDependency,
    PanelSource,
    SeedPlan,
    pipeline,
)
from ic_study.simulation.v4_gate import pipeline_record
from ic_study.simulation.v4_plan import CLOSE_UTC, inventory
from ic_study.simulation.v4_store import SealedStore

CLOSE = datetime.fromisoformat(CLOSE_UTC)
NOT_STARTED = "não iniciado"
PARTIAL = "parcial por encerramento operacional"
INVALID = "completo inválido"
VALID = "completo válido"


@dataclass(frozen=True)
class ConfirmatorySeedPlan(SeedPlan):
    def seed(self, phase: str, role: str, index: int, *, attempt: int = 0) -> int:
        # Validate the shared domain, then derive an isolated confirmatory stream.
        super().seed(phase, role, index, attempt=attempt)
        if self.gate:
            raise ValueError("Confirmatory plans cannot be gate plans")
        purpose = "validation" if phase == "validate" else phase
        namespace = "ic-detection-boundary-v4"
        if phase in {"validate", "nuisance", "bootstrap", "stencil"}:
            namespace += f"-{purpose}"
        namespace += "-confirmatory"
        block = (self.repetition * 10000 + self.block) * 2 + attempt
        material = f"{namespace}|{block}|{phase}|{role}|{index}"
        return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


@dataclass(frozen=True)
class CurveUnit:
    key: str
    tier: int
    cells: tuple[Cell, ...]

    @property
    def seeds(self) -> ConfirmatorySeedPlan:
        return ConfirmatorySeedPlan(
            block=RELIABILITIES.index(self.cells[0].reliability)
        )


def curve_units() -> tuple[CurveUnit, ...]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in inventory():
        grouped.setdefault(str(row["unit"]), []).append(row)
    return tuple(
        CurveUnit(
            key,
            int(rows[0]["tier"]),
            tuple(
                Cell(
                    float(row["a"]),
                    float(row["r"]),
                    str(row["family"]),
                    str(row["channel"]),
                    **row["options"],
                )
                for row in rows
            ),
        )
        for key, rows in grouped.items()
    )


def observed_unit(unit: CurveUnit) -> CurveUnit | None:
    if unit.cells[0].channel == "observed":
        return None
    cells = tuple(replace(cell, channel="observed") for cell in unit.cells)
    return next(candidate for candidate in curve_units() if candidate.cells == cells)


def control_dependency(
    unit: CurveUnit, index: int, root: Path
) -> ControlDependency | None:
    dependency = observed_unit(unit)
    if dependency is None:
        return None
    path = root / dependency.key / f"a{index}"
    if not path.exists():
        return ControlDependency(np.array([0.85, 0.0]), (), False)
    store = SealedStore(path)
    record = store.get_json("result")
    if record is None or not record["success"]:
        return ControlDependency(np.array([0.85, 0.0]), (), False)
    shifts = store.get_array("eta-shifts")
    if shifts is None or shifts.shape != (2000,):
        raise ValueError("Observed dependency omitted aligned eta shifts")
    return ControlDependency(
        np.asarray(record["parameters"], dtype=float), (shifts,), True
    )


class OperationalClose(BaseException):
    """Interrupt incomplete work without converting it to a scientific gap."""


@contextmanager
def deadline() -> Iterator[None]:
    remaining = (CLOSE - datetime.now(UTC)).total_seconds()
    if remaining <= 0:
        raise OperationalClose

    def stop(_number: int, _frame: object) -> None:
        raise OperationalClose

    previous = signal.signal(signal.SIGALRM, stop)
    signal.setitimer(signal.ITIMER_REAL, remaining)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _put_array(store: SealedStore, key: str, value: np.ndarray[Any, Any]) -> None:
    existing = store.get_array(key)
    if existing is None:
        store.put_array(key, value)
    elif not np.array_equal(existing, value):
        raise ValueError("Resumed cell changed immutable numerical output")


def execute_cell(unit: CurveUnit, index: int, directory: Path) -> None:
    """A result marker commits one cell; panel checkpoints survive interruptions."""
    parent = SealedStore(directory.parent)
    store = SealedStore(directory)
    if store.get_json("result") is not None:
        if not (directory / "seal.json").exists():
            store.seal()
        return
    parent_provenance = parent.get_json("provenance")
    if parent_provenance is not None and store.get_json("provenance") is None:
        store.put_json(
            "provenance",
            {
                **parent_provenance,
                "code_sha256": hashlib.sha256(
                    json.dumps(
                        parent_provenance.get("code", {}), sort_keys=True
                    ).encode()
                ).hexdigest(),
            },
        )
    cell = unit.cells[index]
    with store.capture_output():
        with deadline():
            observed = control_dependency(unit, index, directory.parent.parent)
            result = pipeline(
                PanelSource(cell, unit.seeds, store=store),
                observed=observed,
                compute_uncertainty=False,
            )
            record = pipeline_record(result)
            success = result.fit.success
            record.update(
                dependency_gap=result.dependency_gap,
                nuisance_variance=[n.variance for n in result.nuisance],
                nuisance_mcse=[n.mcse for n in result.nuisance],
                mean_shift=[n.mean_shift for n in result.nuisance],
                projected_fraction=[n.projected_fraction for n in result.nuisance],
            )
            if success:
                if result.scores0 is None or result.scores1 is None:
                    raise ValueError("Pipeline omitted curve scores")
                _put_array(store, "scores0", result.scores0)
                _put_array(store, "scores1", result.scores1)
                _put_array(store, "nuisance", result.nuisance[0].centered)
                if cell.channel == "observed":
                    _put_array(store, "eta-shifts", result.nuisance[0].shifts[:, 1])
            record["success"] = success
        store.put_json("result", record)
    store.seal()


def complete_curve(unit: CurveUnit, directory: Path) -> dict[str, object]:
    """Stack available strengths and censor boundaries only across gaps."""
    store = SealedStore(directory)
    previous = store.get_json("curve")
    if previous is not None:
        return previous
    records = []
    scores0, scores1, nuisance = [], [], []
    for index in range(len(GRID)):
        cell = SealedStore(directory / f"a{index}")
        record = cell.get_json("result")
        if record is None:
            raise ValueError("Cannot finalize an incomplete curve")
        records.append(record)
        if record["success"]:
            left = cell.get_array("scores0")
            right = cell.get_array("scores1")
            deviations = cell.get_array("nuisance")
            if left is None or right is None or deviations is None:
                raise ValueError("Successful cell has missing numerical checkpoints")
            scores0.append(left)
            scores1.append(right)
            nuisance.append(deviations)
    gaps = sum(not record["success"] for record in records)
    report: dict[str, object] = {
        "unit": unit.key,
        "gap_count": gaps,
        "band_complete": not gaps,
        "valid_null_gate": False,
        "valid_curve": False,
        "first": None,
        "sustained": None,
        "first_interval": None,
        "sustained_interval": None,
        "cells": records,
    }
    if scores0:
        left, right = np.stack(scores0, axis=-1), np.stack(scores1, axis=-1)
        deviations = np.stack(nuisance, axis=-1)
        if (
            left.shape != (2000, 2, len(scores0))
            or right.shape != left.shape
            or deviations.shape != (2000, len(scores0))
        ):
            raise ValueError("Curve needs 2000 networks and aligned nuisance draws")
        uncertainty = score_uncertainty(
            left, right, deviations, seed=unit.seeds.seed("bootstrap", "state", 0)
        )
        report.update(
            curve_report(
                np.array(GRID),
                uncertainty,
                np.array([record["success"] for record in records], dtype=bool),
            )
        )
        interval = band(uncertainty)
        report["available_strengths"] = [
            a for a, r in zip(GRID, records, strict=True) if r["success"]
        ]
        report.update(
            auc=uncertainty.point.tolist(),
            lower=interval.lower.tolist(),
            upper=interval.upper.tolist(),
        )
    report["status"] = VALID if report["valid_null_gate"] else INVALID
    for key in ("first_interval", "sustained_interval"):
        value = report[key]
        if isinstance(value, tuple):
            report[key] = list(value)
    store.put_json("curve", report)
    return report


def unit_status(unit: CurveUnit, root: Path, *, closed: bool) -> str:
    path = root / unit.key
    if not path.exists():
        return NOT_STARTED
    store = SealedStore(path)
    result = store.get_json("curve")
    if result is not None:
        return str(result["status"])
    started = any(path.iterdir())
    if closed and started:
        return PARTIAL
    return NOT_STARTED


def _close_inventory(
    root: SealedStore, *, now: datetime | None = None
) -> dict[str, object]:
    if (now or datetime.now(UTC)) < CLOSE:
        raise ValueError("Confirmatory estimates remain sealed until close")
    existing = root.get_json("closed-inventory")
    if existing is not None and (root.root / "seal.json").exists():
        return existing
    rows = []
    main_valid = True
    for unit in curve_units():
        status = unit_status(unit, root.root, closed=True)
        rows.append({"unit": unit.key, "tier": unit.tier, "status": status})
        if unit.tier == 1 and status != VALID:
            main_valid = False
    result: dict[str, object] = {
        "closed_utc": CLOSE_UTC,
        "units": rows,
        "main_curve_valid": main_valid,
    }
    if existing is None:
        root.put_json("closed-inventory", result)
    else:
        result = existing
    for path in sorted(root.root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not (path / "seal.json").exists():
            SealedStore(path).seal()
    root.seal()
    return result


def close_inventory(
    root: SealedStore, *, now: datetime | None = None
) -> dict[str, object]:
    with ExitStack() as stack:
        root_path = root.root / "lock"
        root_lock = stack.enter_context(root_path.open("a"))
        root_path.chmod(0o600)
        fcntl.flock(root_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for path in sorted(root.root.glob("shard-*/lock")):
            lock = stack.enter_context(path.open("a"))
            path.chmod(0o600)
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _close_inventory(root, now=now)


@contextmanager
def _locked_shard(
    root: SealedStore, allocation: dict[str, object], shard: int
) -> Iterator[SealedStore]:
    with ExitStack() as stack:
        with (root.root / "lock").open("a") as root_lock:
            Path(root_lock.name).chmod(0o600)
            fcntl.flock(root_lock, fcntl.LOCK_EX)
            if (root.root / "seal.json").exists():
                raise ValueError("Confirmatory output is already closed")
            previous = root.get_json("allocation")
            if previous is None:
                root.put_json("allocation", allocation)
            elif previous != allocation:
                raise ValueError("Resume/shard provenance or allocation changed")
            shard_store = SealedStore(root.root / f"shard-{shard}")
            lock = stack.enter_context((shard_store.root / "lock").open("a"))
            Path(lock.name).chmod(0o600)
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield shard_store


def schedule(
    root: SealedStore,
    provenance: dict[str, object],
    *,
    shard: int = 0,
    shards: int = 1,
    worker: Callable[[CurveUnit, int, Path], None] = execute_cell,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> dict[str, int]:
    """One worker per shard, at most eight; a global barrier separates tiers."""
    if not 0 <= shard < shards <= 8:
        raise ValueError("Require 1..8 deterministic shards")
    shared = {
        key: value
        for key, value in provenance.items()
        if key not in {"host_sha256", "environment", "environment_sha256"}
    }
    allocation = {"shards": shards, "close_utc": CLOSE_UTC, "provenance": shared}
    with _locked_shard(root, allocation, shard) as shard_store:
        selected = [
            unit for index, unit in enumerate(curve_units()) if index % shards == shard
        ]
        manifest = {
            **allocation,
            "shard": shard,
            "units": [u.key for u in selected],
            "execution_provenance": provenance,
        }
        prior_manifest = shard_store.get_json("manifest")
        if prior_manifest is None:
            shard_store.put_json("manifest", manifest)
        elif prior_manifest != manifest:
            raise ValueError("Resume execution provenance changed for this shard")
        completed = 0
        for unit in selected:
            if now() >= CLOSE:
                return {"completed": completed, "closed": 1, "tier_blocked": 0}
            earlier = [u for u in curve_units() if u.tier < unit.tier]
            if any(not (root.root / u.key / "curve.json").exists() for u in earlier):
                return {"completed": completed, "closed": 0, "tier_blocked": 1}
            dependency = observed_unit(unit)
            if (
                dependency is not None
                and not (root.root / dependency.key / "curve.json").exists()
            ):
                return {"completed": completed, "closed": 0, "tier_blocked": 1}
            directory = root.root / unit.key
            store = SealedStore(directory)
            if store.get_json("curve") is not None:
                continue
            if store.get_json("provenance") is None:
                store.put_json("provenance", provenance)
            for index in range(9):
                if now() >= CLOSE:
                    return {"completed": completed, "closed": 1, "tier_blocked": 0}
                try:
                    worker(unit, index, directory / f"a{index}")
                except OperationalClose:
                    return {"completed": completed, "closed": 1, "tier_blocked": 0}
            try:
                with deadline():
                    complete_curve(unit, directory)
            except OperationalClose:
                return {"completed": completed, "closed": 1, "tier_blocked": 0}
            completed += 1
        return {"completed": completed, "closed": 0, "tier_blocked": 0}


def released_curves(
    root: SealedStore, *, now: datetime | None = None
) -> dict[str, object]:
    """Release only completed units at the declared close, with the full inventory."""
    result = close_inventory(root, now=now)
    curves = []
    for unit in curve_units():
        if (root.root / unit.key / "curve.json").exists():
            curve = SealedStore(root.root / unit.key).get_json("curve")
            if curve is not None and unit.tier == 1 and not result["main_curve_valid"]:
                curve["main_curve_valid"] = False
            curves.append(curve)
    return {"inventory": result, "curves": curves}
