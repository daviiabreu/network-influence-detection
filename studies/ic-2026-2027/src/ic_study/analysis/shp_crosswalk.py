"""Exploratory synthetic crosswalk between the SHP anchor estimators and v4 r.

SHP reliability successor 1, Addition 2. Observed panels come from the frozen v4
generator (commit 37513841), imported unmodified and composed exactly as
``PanelSource._profiles`` composes the tier-1 observed channel: the latent path
(``influence`` for the interaction arm, ``null`` for family B), ``panel_mask``,
``measurement`` and ``ordinal_channel``, which gives 11 equiprobable categories
per wave by rank among the people observed. Categories are coded 0-10 and
unobserved person-waves are NaN, as in the SHP panel. Every anchor estimator then
runs through the ``shp_reliability`` functions that ``analyze_panel`` uses. No v4
seed plan, gate result, tier output, AUC or a*(r) is read.

Usage::

    python -m ic_study.analysis.shp_crosswalk --out DIR \\
        [--cells N | --cells KEY,KEY] [--replicates R] [--shard K --shards N]

Each finished cell is written to ``DIR/cells/<key>.json`` and skipped when the
command runs again, so shards can run on different hosts and be merged by copying
``cells/``. The process that finds every selected cell complete writes
``DIR/crosswalk.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from inspect import signature
from pathlib import Path
from typing import Any, cast

import numpy as np
import scipy
from numpy.typing import NDArray

from ic_study.analysis.shp_reliability import (
    YEARS,
    _ordinal_sensitivity,
    _simplex_fit,
    _triplet_fit,
    starts_sensitivity,
)
from ic_study.models.anchored_panel import panel_mask
from ic_study.models.detection_panel import measurement, ordinal_channel
from ic_study.models.detection_panel_v4 import influence, null
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES, Cell, PanelSource

NAMESPACE = "shp-crosswalk-v1"
SEED_ROOT = 20260928
# Frozen v4 seeds (SeedPlan, ConfirmatorySeedPlan) are 8-byte SHA-256 prefixes,
# so every one lies below 2**64; crosswalk seeds lie in [2**64, 2**65).
SEED_OFFSET = 1 << 64
ROLES = ("state", "network", "null-state", "mask", "error")
SIZE: int = signature(PanelSource.__init__).parameters["size"].default
WAVES = len(YEARS)  # the frozen PanelSource._profiles literal 11
RETENTION = 0.89  # the frozen PanelSource._profiles literal
CATEGORIES = 11
REPLICATES = 10
INTERACTION_PHI: float = signature(influence).parameters["phi"].default
NULL_PHI = 0.85
TRAIT_WEIGHTS = (0.25, 0.5)
ANCHOR = len(YEARS) // 2
QUASI_SIMPLEX = f"quasi_simplex_r_{YEARS[ANCHOR]}"
STARTS = f"starts_r_{YEARS[ANCHOR]}"
POLYCHORIC_INADMISSIBLE = "polychoric Heise estimate outside (0, 1)"
SCHEMA = "ic-study.shp-crosswalk.v1"
CELL_SCHEMA = "ic-study.shp-crosswalk-cell.v1"
FROZEN_COMMIT = "37513841"
STUDY = Path(__file__).resolve().parents[3]
FREEZE_V4 = "experiments/exploratory/detection-boundary-v4/freeze-v4.json"
SPECIFICATION = "research/questions/exploration/2026-09-24-parallel"
GENERATOR_MODULES = (
    "src/ic_study/simulation/detection_v4.py",
    "src/ic_study/models/detection_panel_v4.py",
    "src/ic_study/models/detection_panel.py",
    "src/ic_study/models/anchored_panel.py",
    "src/ic_study/simulation/amendment_a.py",
)
ESTIMATOR_MODULES = (
    "src/ic_study/analysis/shp_reliability.py",
    "src/ic_study/analysis/shp_crosswalk.py",
)
_NUMERICAL = (ValueError, ArithmeticError)


@dataclass(frozen=True)
class CrosswalkCell:
    """The v4 interaction arm at (a, r), or null family B with trait weight eta."""

    family: str
    r: float
    a: float | None = None
    eta: float | None = None

    def __post_init__(self) -> None:
        interaction = self.family == "interaction" and self.eta is None
        reference = self.family == "B" and self.a is None
        if not (
            self.r in RELIABILITIES
            and (
                (interaction and self.a in GRID)
                or (reference and self.eta in TRAIT_WEIGHTS)
            )
        ):
            raise ValueError("Cell is outside the declared crosswalk")

    @property
    def key(self) -> str:
        if self.family == "interaction":
            return f"interaction-a{cast(float, self.a):g}-r{self.r:.2f}"
        return f"B-eta{cast(float, self.eta):.2f}-r{self.r:.2f}"

    def record(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "family": self.family,
            "a": self.a,
            "r": self.r,
            "eta": self.eta,
            "phi": INTERACTION_PHI if self.family == "interaction" else NULL_PHI,
        }


def plan_cells() -> tuple[CrosswalkCell, ...]:
    """Declared order: the interaction arm over G x R, then B references by eta."""
    interaction = [
        CrosswalkCell("interaction", r, a=a) for r in RELIABILITIES for a in GRID
    ]
    references = [
        CrosswalkCell("B", r, eta=eta) for eta in TRAIT_WEIGHTS for r in RELIABILITIES
    ]
    return (*interaction, *references)


def crosswalk_seed(root: int, block: int, replicate: int, role: str) -> int:
    if role not in ROLES or block < 0 or replicate < 0:
        raise ValueError("Invalid crosswalk seed material")
    material = f"{NAMESPACE}|{root}|r{block}|replicate{replicate}|{role}"
    digest = hashlib.sha256(material.encode()).digest()[:8]
    return SEED_OFFSET + int.from_bytes(digest, "big")


def cell_seeds(
    cell: CrosswalkCell, replicate: int, *, root: int = SEED_ROOT
) -> dict[str, int]:
    """Common random numbers across a and family within (r, replicate), like the
    confirmatory plans, whose seed block depends on r only."""
    block = RELIABILITIES.index(cell.r)
    return {role: crosswalk_seed(root, block, replicate, role) for role in ROLES}


def synthetic_panel(
    cell: CrosswalkCell, seeds: Mapping[str, int], *, size: int = SIZE
) -> NDArray[np.float64]:
    """People x waves observed 0-10 panel, NaN where the SHP geometry is unobserved.

    Mirrors ``PanelSource._profiles`` for the tier-1 family-B observed channel,
    whose defaults come from the frozen ``Cell``: no heteroscedasticity, no error
    correlation or tenure gain, no heaping and equiprobable categories.
    """
    frozen = Cell(0.0 if cell.a is None else cell.a, cell.r)
    if cell.family == "interaction":
        latent = influence(
            size,
            WAVES,
            seeds["state"],
            seeds["network"],
            share=frozen.share,
            repulsion=frozen.repulsion,
            anchor=frozen.anchor,
            steps=frozen.steps,
        )
    else:
        latent = null(
            size,
            WAVES,
            seeds["state"],
            seeds["null-state"],
            family=frozen.family,
            phi=NULL_PHI,
            eta=cast(float, cell.eta),
            steps=frozen.steps,
        )
    mask = panel_mask(size, WAVES, seeds["mask"], retention=RETENTION)
    measured = measurement(
        latent,
        frozen.reliability,
        seeds["error"],
        heteroscedastic=False,
        error_correlation=frozen.error_correlation,
    )
    observed = ordinal_channel(measured, mask, midpoint_mass=0, heap_seed=None)
    values = np.where(observed >= 0, observed, np.nan).astype(np.float64)
    return np.ascontiguousarray(values.T)


def estimator_names(years: tuple[int, ...] = YEARS) -> tuple[str, ...]:
    anchor = years[len(years) // 2]
    names = [f"quasi_simplex_r_{anchor}"]
    for i in range(len(years) - 2):
        span = f"{years[i]}-{years[i + 2]}"
        names.append(f"heise_{span}")
        names += [f"wiley_wiley_{span}_r_{year}" for year in years[i : i + 3]]
    names += [
        f"polychoric_heise_{years[i]}-{years[i + 2]}" for i in range(len(years) - 2)
    ]
    names.append(f"starts_r_{anchor}")
    return tuple(names)


def _reason(error: Exception) -> str:
    return str(error) or type(error).__name__


def apply_estimators(
    panel: NDArray[np.float64], years: tuple[int, ...] = YEARS
) -> tuple[dict[str, float], dict[str, list[str]]]:
    """Every anchor estimator of the SHP analysis; failures are kept, not clipped."""
    values: dict[str, float] = {}
    failures: dict[str, list[str]] = {}
    anchor = len(years) // 2
    name = f"quasi_simplex_r_{years[anchor]}"
    try:
        values[name] = float(_simplex_fit(panel)["reliability"][anchor])
    except _NUMERICAL as error:
        failures[name] = [_reason(error)]
    for i in range(len(years) - 2):
        window = (years[i], years[i + 1], years[i + 2])
        span = f"{window[0]}-{window[2]}"
        names = [f"heise_{span}", *(f"wiley_wiley_{span}_r_{y}" for y in window)]
        try:
            fit = _triplet_fit(panel[:, i : i + 3], window)
        except _NUMERICAL as error:
            failures |= {item: [_reason(error)] for item in names}
            continue
        estimates = [fit["heise_reliability"], *fit["wiley_reliability_by_wave"]]
        values |= {
            item: float(value) for item, value in zip(names, estimates, strict=True)
        }
    polychoric = [
        f"polychoric_heise_{years[i]}-{years[i + 2]}" for i in range(len(years) - 2)
    ]
    try:
        ordinal = _ordinal_sensitivity(panel, years)
    except _NUMERICAL as error:
        failures |= {item: [_reason(error)] for item in polychoric}
    else:
        for item, triplet in zip(polychoric, ordinal, strict=True):
            if triplet["admissible"]:
                values[item] = float(triplet["polychoric_heise_reliability"])
            else:
                failures[item] = [POLYCHORIC_INADMISSIBLE]
    starts = starts_sensitivity(panel, years)
    name = f"starts_r_{years[anchor]}"
    if starts["status"] == "admissible":
        values[name] = float(starts["anchor"]["estimate"])
    else:
        failures[name] = [str(reason) for reason in starts["reasons"]]
    return values, failures


def summarize(
    values: Sequence[float], failures: Sequence[Sequence[str]]
) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    reasons = Counter(reason for listed in failures for reason in listed)
    return {
        "n_values": len(array),
        "failures": len(failures),
        "failure_reasons": dict(sorted(reasons.items())),
        "mean": float(array.mean()) if len(array) else None,
        "sd": float(array.std(ddof=1)) if len(array) > 1 else None,
        "min": float(array.min()) if len(array) else None,
        "max": float(array.max()) if len(array) else None,
    }


def plan_record(replicates: int, root: int, size: int) -> dict[str, Any]:
    return {
        "namespace": NAMESPACE,
        "seed_root": root,
        "replicates": replicates,
        "size": size,
        "waves": WAVES,
        "retention": RETENTION,
        "categories": CATEGORIES,
        "years": list(YEARS),
        "anchor_wave_index": ANCHOR,
        "null_family": "B",
        "null_phi": NULL_PHI,
    }


def cell_record(
    cell: CrosswalkCell,
    plan: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    *,
    provenance: Mapping[str, Any],
    cpu_seconds: float,
    wall_seconds: float,
) -> dict[str, Any]:
    names = estimator_names()
    for row in rows:
        if set(row["values"]) | set(row["failures"]) != set(names) or set(
            row["values"]
        ) & set(row["failures"]):
            raise ValueError("Each estimator needs one value or one failure")
    return {
        "schema": CELL_SCHEMA,
        "cell": cell.record(),
        "plan": dict(plan),
        "estimators": {
            name: summarize(
                [row["values"][name] for row in rows if name in row["values"]],
                [row["failures"][name] for row in rows if name in row["failures"]],
            )
            for name in names
        },
        "replicates": [dict(row) for row in rows],
        "provenance": dict(provenance),
        "cpu_seconds": cpu_seconds,
        "wall_seconds": wall_seconds,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def specification() -> dict[str, Any]:
    directory = STUDY / SPECIFICATION
    return {
        name: {
            "path": f"studies/{STUDY.name}/{SPECIFICATION}/{file}",
            "sha256": _sha256(directory / file),
        }
        for name, file in (
            ("markdown", "shp-reliability-successor-1.md"),
            ("machine_json", "shp-reliability-successor-1.json"),
        )
    }


def aggregate_record(
    cells: Sequence[CrosswalkCell],
    plan: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summary per cell, family and estimator; the declared-plan flag is explicit."""
    provenance: dict[str, Any] = {}
    for record in records:
        provenance.setdefault(
            json.dumps(record["provenance"], sort_keys=True), record["provenance"]
        )
    declared = (
        dict(plan) == plan_record(REPLICATES, SEED_ROOT, SIZE)
        and tuple(cells) == plan_cells()
    )
    return {
        "schema": SCHEMA,
        "status": "exploratory",
        "specification": specification(),
        "declared_plan": declared,
        "parameters": {
            **plan,
            "grid": list(GRID),
            "reliabilities": list(RELIABILITIES),
            "trait_weights": list(TRAIT_WEIGHTS),
            "interaction_phi": INTERACTION_PHI,
            "estimators": list(estimator_names()),
            "cells": [cell.key for cell in cells],
        },
        "provenance": list(provenance.values()),
        "cpu_seconds": float(sum(record["cpu_seconds"] for record in records)),
        "cells": [
            {**record["cell"], "estimators": record["estimators"]} for record in records
        ],
    }


def _git(*arguments: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=STUDY,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


@cache
def provenance() -> dict[str, Any]:
    """Code, frozen generator, host and environment; stops if the generator drifted."""
    freeze = json.loads((STUDY / FREEZE_V4).read_text(encoding="utf-8"))
    generator = {name: _sha256(STUDY / name) for name in GENERATOR_MODULES}
    if any(freeze["code"].get(name) != digest for name, digest in generator.items()):
        raise ValueError("Frozen v4 generator modules differ from freeze-v4.json")
    status = _git("status", "--porcelain", "--", "src")
    return {
        "code": {
            "commit": _git("rev-parse", "HEAD"),
            "source_dirty": None if status is None else bool(status),
            "modules_sha256": {
                name: _sha256(STUDY / name) for name in ESTIMATOR_MODULES
            },
        },
        "generator": {
            "frozen_commit": FROZEN_COMMIT,
            "freeze_record": FREEZE_V4,
            "modules_sha256": generator,
            "matches_freeze_v4": True,
        },
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "node_sha256": hashlib.sha256(
                (platform.node() + platform.machine()).encode()
            ).hexdigest(),
        },
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "lock_sha256": _sha256(STUDY / "uv.lock"),
            "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
            "VECLIB_MAXIMUM_THREADS": os.environ.get("VECLIB_MAXIMUM_THREADS"),
        },
    }


def run_cell(
    cell: CrosswalkCell, plan: Mapping[str, Any], *, context: Mapping[str, Any]
) -> dict[str, Any]:
    cpu, wall = time.process_time(), time.perf_counter()
    rows = []
    for replicate in range(int(plan["replicates"])):
        start = time.process_time()
        seeds = cell_seeds(cell, replicate, root=int(plan["seed_root"]))
        panel = synthetic_panel(cell, seeds, size=int(plan["size"]))
        values, failures = apply_estimators(panel)
        rows.append(
            {
                "replicate": replicate,
                "values": values,
                "failures": failures,
                "cpu_seconds": time.process_time() - start,
            }
        )
    return cell_record(
        cell,
        plan,
        rows,
        provenance=context,
        cpu_seconds=time.process_time() - cpu,
        wall_seconds=time.perf_counter() - wall,
    )


def _write_json(path: Path, data: object) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def _load_cell(
    path: Path, cell: CrosswalkCell, plan: Mapping[str, Any]
) -> dict[str, Any]:
    record = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    if (
        record.get("schema") != CELL_SCHEMA
        or record.get("cell") != cell.record()
        or record.get("plan") != dict(plan)
    ):
        raise ValueError(f"{path.name} was written by a different crosswalk plan")
    return record


def run(
    out: Path,
    cells: Sequence[CrosswalkCell],
    *,
    replicates: int = REPLICATES,
    shard: int = 0,
    shards: int = 1,
    root: int = SEED_ROOT,
    size: int = SIZE,
    log: Callable[[str], None] = print,
) -> Path | None:
    """Run this shard's missing cells; aggregate once every selected cell exists."""
    if replicates < 1 or shards < 1 or not 0 <= shard < shards or not cells:
        raise ValueError("Invalid crosswalk selection, replicates or shard")
    plan = plan_record(replicates, root, size)
    directory = out / "cells"
    directory.mkdir(parents=True, exist_ok=True)
    context = provenance()
    for index, cell in enumerate(cells):
        path = directory / f"{cell.key}.json"
        if index % shards != shard:
            continue
        if path.exists():
            _load_cell(path, cell, plan)
            log(f"{cell.key}: complete, skipped")
            continue
        record = run_cell(cell, plan, context=context)
        _write_json(path, record)
        failed = {
            name: summary["failures"]
            for name, summary in record["estimators"].items()
            if summary["failures"]
        }
        log(
            f"{cell.key}: {replicates} replicates, "
            f"{record['cpu_seconds']:.1f} s CPU, failures {failed or 'none'}"
        )
    records = []
    for cell in cells:
        path = directory / f"{cell.key}.json"
        if not path.exists():
            return None
        records.append(_load_cell(path, cell, plan))
    target = out / "crosswalk.json"
    _write_json(target, aggregate_record(cells, plan, records))
    return target


def select_cells(selection: str | None) -> tuple[CrosswalkCell, ...]:
    """All declared cells, the first N of them, or comma-separated cell keys."""
    cells = plan_cells()
    if selection is None:
        return cells
    if selection.isdigit():
        count = int(selection)
        if not 1 <= count <= len(cells):
            raise ValueError(f"--cells must be between 1 and {len(cells)}")
        return cells[:count]
    keys = [key.strip() for key in selection.split(",") if key.strip()]
    unknown = sorted(set(keys) - {cell.key for cell in cells})
    if unknown or not keys:
        raise ValueError(f"Unknown crosswalk cells: {', '.join(unknown) or 'none'}")
    return tuple(cell for cell in cells if cell.key in keys)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exploratory SHP anchor-estimator crosswalk on frozen v4 panels"
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--cells", help="first N declared cells, or comma-separated cell keys"
    )
    parser.add_argument("--replicates", type=int, default=REPLICATES)
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        cells = select_cells(args.cells)
        target = run(
            args.out,
            cells,
            replicates=args.replicates,
            shard=args.shard,
            shards=args.shards,
            size=SIZE,
        )
    except ValueError as error:
        parser.exit(2, f"SHP crosswalk stopped: {error}\n")
    if target is None:
        print(f"Shard {args.shard}/{args.shards} done; other cells still pending.")
    else:
        print(f"Crosswalk aggregate written: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
