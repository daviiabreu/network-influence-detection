"""Exploratory X1b: the frozen v4 tier-1 curve with only the social generator swapped.

Declared on 2026-09-28 in
``experiments/exploratory/detection-boundary-v4-exploratory``. X1b estimates
the boundary of the mean-field twin against null B, a*_MF(r), under the frozen
fitting, validation, discrimination, band and inversion rules. It may run only
after this successor, driven by the original generator, reproduces the frozen
cell pipeline bit for bit on the declared precondition cells. Every stream
comes from the exploratory namespace; no confirmatory seed is derived or
consumed. Outputs are exploratory and never promoted to confirmatory evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.models.anchored_panel import Floats
from ic_study.models.detection_panel_v4 import influence
from ic_study.simulation import v4_curve
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    Cell,
    PanelSource,
    SeedPlan,
    pipeline,
)
from ic_study.simulation.v4_curve import (
    CurveUnit,
    _put_array,
    complete_curve,
    curve_units,
    deadline,
)
from ic_study.simulation.v4_exploratory import (
    FREEZE,
    NAMESPACE,
    ROOT,
    SIZE,
    STUDY,
    WAVES,
    Analysis,
    code_provenance,
    declaration_digests,
    derive_seed,
    host_description,
    load_records,
    mean_field_path,
    observed_profile,
    run_shard,
    shared_provenance,
    timing_summary,
    utc_now,
    write_json,
)
from ic_study.simulation.v4_gate import manifest, pipeline_record
from ic_study.simulation.v4_store import SealedStore

PRECONDITION_CELLS = ((0.0, 0.9), (0.003, 0.7), (0.03, 0.5), (0.3, 0.6))
SIDES = ("frozen", "successor")
VERIFICATION_SCHEMA = "ic-study.v4-exploratory-x1b-precondition.v1"
SEEDS = {
    "namespace": NAMESPACE,
    "root": ROOT,
    "material": "{namespace}|{root}|x1b|{block}|{phase}|{role}|{index}",
    "block": "2 * reliability index + attempt, as in the frozen plans",
    "digest": "sha256(material)[:8] as big-endian unsigned",
}

type Seed = Callable[[str, int], int]
type Generator = Callable[[Cell, int, Seed, int, bool], Floats]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Exploratory seeds and units ------------------------------------------------


@dataclass(frozen=True)
class ExploratorySeedPlan(SeedPlan):
    """The frozen ``SeedPlan`` interface over the exploratory namespace.

    Blocks keep the frozen ``block * 2 + attempt`` layout, so the nine
    strengths of one reliability share their streams as in the frozen curve.
    """

    def seed(self, phase: str, role: str, index: int, *, attempt: int = 0) -> int:
        if self.gate or self.repetition or attempt not in (0, 1):
            raise ValueError("Exploratory plans have one repetition and no gate")
        return derive_seed("x1b", 2 * self.block + attempt, phase, role, index)


@dataclass(frozen=True)
class ExploratoryUnit(CurveUnit):
    """A frozen curve unit whose streams come from the exploratory plan.

    Frozen ``execute_cell`` and ``complete_curve`` read only ``seeds.seed``.
    """

    @property
    def seeds(self) -> ExploratorySeedPlan:  # type: ignore[override]
        return ExploratorySeedPlan(block=RELIABILITIES.index(self.cells[0].reliability))


def x1b_units() -> tuple[ExploratoryUnit, ...]:
    """The frozen tier-1 units (null B, observed channel), one per reliability."""
    return tuple(
        ExploratoryUnit(f"x1b-{unit.key}", unit.tier, unit.cells)
        for unit in curve_units()
        if unit.tier == 1
    )


def x1b_cells() -> tuple[tuple[ExploratoryUnit, int], ...]:
    return tuple((unit, index) for unit in x1b_units() for index in range(len(GRID)))


# Social generators and the swapped source -----------------------------------


def original_generator(
    cell: Cell, size: int, seed: Seed, index: int, coupled: bool
) -> Floats:
    """The frozen social call of ``PanelSource._profiles``, argument for argument."""
    return influence(
        size,
        WAVES,
        seed("state", index),
        seed("network", index if coupled else index // 4),
        share=cell.share,
        repulsion=cell.repulsion,
        anchor=cell.anchor,
        steps=cell.steps,
    )


def twin_generator(
    cell: Cell, size: int, seed: Seed, index: int, coupled: bool
) -> Floats:
    """X1 mean-field twin: no network, and a xi stream of the panel's own."""
    return mean_field_path(
        size,
        WAVES,
        seed("state", index),
        seed("xi", index),
        share=cell.share,
        repulsion=cell.repulsion,
        anchor=cell.anchor,
        steps=cell.steps,
    ).path


class SwappedSource(PanelSource):
    """Frozen ``PanelSource`` for a tier-1 cell with only the social generator swapped.

    Null panels come from the frozen ``_profiles``. Social panels keep its
    index layout, seeds and observed channel and call the injected generator.
    """

    def __init__(
        self,
        cell: Cell,
        seeds: SeedPlan,
        *,
        generator: Generator,
        size: int = SIZE,
        store: SealedStore | None = None,
    ) -> None:
        if cell != Cell(cell.share, cell.reliability):
            raise ValueError("The successor covers tier-1 cells only")
        if not isinstance(seeds, ExploratorySeedPlan):
            raise ValueError("The successor draws exploratory seeds only")
        super().__init__(cell, seeds, size=size, store=store)
        self.generator = generator

    def _profiles(
        self,
        phase: str,
        count: int,
        *,
        parameters: Floats | None = None,
        attempt: int = 0,
        start: int = 0,
    ) -> Floats:
        if parameters is not None:
            return super()._profiles(
                phase, count, parameters=parameters, attempt=attempt, start=start
            )

        def seed(role: str, index: int) -> int:
            return self.seeds.seed(phase, role, index, attempt=attempt)

        coupled = phase in {"match", "validate"}
        rows = []
        for j in range(start, start + count):
            index = 2 * j + 1
            latent = self.generator(self.cell, self.size, seed, index, coupled)
            rows.append(
                observed_profile(
                    latent,
                    self.cell.reliability,
                    seed("mask", index),
                    seed("error", index),
                )
            )
            self.panels += 1
        return np.stack(rows)


def execute_swapped_cell(
    unit: ExploratoryUnit,
    index: int,
    directory: Path,
    generator: Generator,
    *,
    size: int = SIZE,
) -> None:
    """Frozen ``v4_curve.execute_cell`` with ``SwappedSource`` for ``PanelSource``.

    Tier-1 cells have no control dependency, so the frozen lookup, which
    returns none for them, is omitted. Store layout, record, arrays and seal
    are the frozen ones; the precondition compares them file by file.
    """
    parent = SealedStore(directory.parent)
    store = SealedStore(directory)
    if store.get_json("result") is not None:
        if not (directory / "seal.json").exists():
            store.seal()
        return
    parent_provenance = parent.get_json("provenance")
    if parent_provenance is not None and store.get_json("provenance") is None:
        code = json.dumps(parent_provenance.get("code", {}), sort_keys=True)
        store.put_json(
            "provenance",
            {
                **parent_provenance,
                "code_sha256": hashlib.sha256(code.encode()).hexdigest(),
            },
        )
    cell = unit.cells[index]
    with store.capture_output():
        with deadline():
            result = pipeline(
                SwappedSource(
                    cell, unit.seeds, generator=generator, size=size, store=store
                ),
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
                _put_array(store, "eta-shifts", result.nuisance[0].shifts[:, 1])
            record["success"] = success
        store.put_json("result", record)
    store.seal()


# Provenance -------------------------------------------------------------------


def successor_provenance() -> dict[str, Any]:
    """This module's digest and the frozen Python closure checked against freeze-v4."""
    freeze = json.loads((STUDY / FREEZE).read_bytes())["code"]
    frozen = sorted(path for path in freeze if path.endswith(".py"))
    return {
        "successor_sha256": _digest(Path(__file__)),
        "freeze_sha256": _digest(STUDY / FREEZE),
        "frozen_python_files": len(frozen),
        "frozen_python_mismatched": [
            path
            for path in frozen
            if not (STUDY / path).is_file() or _digest(STUDY / path) != freeze[path]
        ],
    }


def require_frozen_closure() -> dict[str, Any]:
    provenance = successor_provenance()
    if provenance["frozen_python_mismatched"]:
        raise ValueError("Frozen v4 sources differ from freeze-v4.json")
    return provenance


def unit_provenance(analysis: str, generator: str, size: int) -> dict[str, object]:
    """Frozen ``manifest`` plus the exploratory labels, stored once per unit."""
    return {
        **manifest(STUDY),
        "analysis": analysis,
        "generator": generator,
        "size": size,
        "namespace": NAMESPACE,
        "root": ROOT,
        "declaration": declaration_digests(),
        "freeze_sha256": _digest(STUDY / FREEZE),
    }


def ensure_provenance(store: SealedStore, provenance: dict[str, object]) -> None:
    """Write a unit's provenance once; a resumed unit must match it exactly."""
    existing = store.get_json("provenance")
    if existing is None:
        try:
            store.put_json("provenance", provenance)
            return
        except FileExistsError:
            existing = store.get_json("provenance")
    if existing != provenance:
        raise ValueError("Resumed unit provenance changed")


# Precondition: bitwise reproduction with the original generator -------------


def precondition_cell(position: int) -> tuple[ExploratoryUnit, int]:
    share, reliability = PRECONDITION_CELLS[position]
    unit = next(u for u in x1b_units() if u.cells[0].reliability == reliability)
    return unit, GRID.index(share)


def _side_directory(out: Path, side: str, position: int) -> Path:
    unit, index = precondition_cell(position)
    return out / "precondition" / side / unit.key / f"a{index}"


def _side_record(out: Path, side: str, position: int) -> Path:
    return out / "precondition" / "runs" / f"{side}-{position}.json"


def precondition_side(
    out: Path, position: int, side: str, *, size: int = SIZE
) -> dict[str, Any]:
    """One precondition cell, original generator, through one executor.

    ``frozen`` calls ``v4_curve.execute_cell`` unchanged, whose
    ``PanelSource`` has the declared size; ``successor`` calls
    ``execute_swapped_cell``. Both get the same exploratory unit and the same
    unit provenance. A ValueError from the pipeline is recorded, not hidden.
    """
    if side not in SIDES:
        raise ValueError("Unknown precondition side")
    unit, index = precondition_cell(position)
    directory = _side_directory(out, side, position)
    ensure_provenance(
        SealedStore(directory.parent),
        unit_provenance("x1b-precondition", "original", size),
    )
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    error = None
    try:
        if side == "frozen":
            v4_curve.execute_cell(unit, index, directory)
        else:
            execute_swapped_cell(unit, index, directory, original_generator, size=size)
    except ValueError as failure:
        error = repr(failure)
    record = {
        "schema": "ic-study.v4-exploratory-x1b-precondition-side.v1",
        "position": position,
        "side": side,
        "size": size,
        "error": error,
        "timing": {
            "started_utc": started,
            "finished_utc": utc_now(),
            "wall_seconds": time.perf_counter() - clock,
            "cpu_seconds": time.process_time() - cpu,
        },
        "code": code_provenance(),
        "successor": successor_provenance(),
        "host": host_description(),
    }
    write_json(_side_record(out, side, position), record)
    return record


def compare_cells(frozen: Path, successor: Path) -> dict[str, Any]:
    """Byte comparison of two cell stores.

    Every file must match except ``access.jsonl``, whose timestamps and
    process ids differ by construction; its (action, key) sequence must match.
    Profile checkpoints are named by the SHA-256 of their seed material.
    """

    def contents(directory: Path) -> dict[str, bytes]:
        return {
            path.name: path.read_bytes()
            for path in directory.iterdir()
            if path.is_file() and path.name != "access.jsonl"
        }

    def accesses(directory: Path) -> list[list[str]]:
        path = directory / "access.jsonl"
        lines = path.read_text().splitlines() if path.exists() else []
        return [[entry["action"], entry["key"]] for entry in map(json.loads, lines)]

    left, right = contents(frozen), contents(successor)
    differing = sorted(
        name for name in left.keys() | right.keys() if left.get(name) != right.get(name)
    )
    checkpoints = sorted(
        name for name in left if len(name) == 68 and name.endswith(".npy")
    )
    sequence = accesses(frozen) == accesses(successor)
    return {
        "equal": not differing and sequence,
        "differing_files": differing,
        "access_sequence_equal": sequence,
        "files": len(left),
        "checkpoints": len(checkpoints),
        "checkpoints_sha256": hashlib.sha256(
            b"".join(name.encode() + left[name] for name in checkpoints)
        ).hexdigest(),
        "sha256": {
            name: hashlib.sha256(left[name]).hexdigest()
            for name in sorted(left)
            if name not in checkpoints
        },
    }


def verify(out: Path, *, size: int = SIZE) -> dict[str, Any]:
    """Declared precondition over every precondition cell run in ``out``.

    It passes when both executors ran at this commit and size, every cell's
    stores are byte-identical with identical unit provenance and identical
    errors, and at least two cells reached a result.
    """
    code, successor = code_provenance(), successor_provenance()
    cells = []
    for position, (share, reliability) in enumerate(PRECONDITION_CELLS):
        unit, index = precondition_cell(position)
        sides = {side: _side_directory(out, side, position) for side in SIDES}
        runs = {
            side: json.loads(_side_record(out, side, position).read_text())
            for side in SIDES
        }
        comparison = compare_cells(sides["frozen"], sides["successor"])
        provenance = [
            (sides[side].parent / "provenance.json").read_bytes() for side in SIDES
        ]
        same_run = all(
            runs[side]["size"] == size
            and runs[side]["code"]["commit"] == code["commit"]
            and runs[side]["successor"] == successor
            for side in SIDES
        )
        errors = [runs[side]["error"] for side in SIDES]
        result = sides["frozen"] / "result.json"
        record = json.loads(result.read_bytes()) if result.exists() else None
        cells.append(
            {
                "a": share,
                "r": reliability,
                "unit": unit.key,
                "index": index,
                "equal": comparison["equal"]
                and provenance[0] == provenance[1]
                and errors[0] == errors[1]
                and same_run,
                "result": record is not None,
                "success": None if record is None else record["success"],
                "attempts": []
                if record is None
                else [attempt["status"] for attempt in record["attempts"]],
                "errors": dict(zip(SIDES, errors, strict=True)),
                "same_commit_size_and_successor": same_run,
                "unit_provenance_equal": provenance[0] == provenance[1],
                "unit_provenance_sha256": hashlib.sha256(provenance[0]).hexdigest(),
                **comparison,
                "timing": {side: runs[side]["timing"] for side in SIDES},
            }
        )
    reproduced = sum(cell["equal"] and cell["result"] for cell in cells)
    return {
        "schema": VERIFICATION_SCHEMA,
        "label": "exploratory; never promoted to confirmatory evidence",
        "declaration": declaration_digests(),
        "rule": (
            "frozen v4_curve.execute_cell and execute_swapped_cell with the "
            "original generator, same exploratory unit and seeds, declared "
            "sizes, separate processes; every file of each cell store equal "
            "byte for byte except access.jsonl, whose (action, key) sequence "
            "must be equal"
        ),
        "size": size,
        "cells": cells,
        "cells_reproduced_with_result": reproduced,
        "passed": all(cell["equal"] for cell in cells) and reproduced >= 2,
        "seeds": SEEDS,
        "code": code,
        "successor": successor,
        "host": host_description(),
        "verified_utc": utc_now(),
    }


def require_verification(path: Path, size: int) -> str:
    """X1b runs only after a passing precondition of this exact successor."""
    record = json.loads(path.read_bytes())
    if (
        record.get("schema") != VERIFICATION_SCHEMA
        or record.get("passed") is not True
        or record.get("size") != size
        or record["code"]["commit"] != code_provenance()["commit"]
        or record["successor"] != successor_provenance()
    ):
        raise ValueError("X1b needs a passing precondition of this successor")
    return _digest(path)


# X1b: the twin curve under the frozen rules ----------------------------------


@dataclass(frozen=True)
class X1bSizes:
    size: int = SIZE


DECLARED_X1B = X1bSizes()


def x1b_cell(
    index: int, directory: Path, verification: str, sizes: X1bSizes = DECLARED_X1B
) -> dict[str, Any]:
    """One twin cell into the frozen store layout under ``directory/stores``.

    A ValueError from the frozen pipeline leaves the cell without a result,
    so its unit cannot be completed; it is recorded and the shard goes on.
    """
    unit, position = x1b_cells()[index]
    cell = unit.cells[position]
    stores = directory / "stores" / unit.key
    ensure_provenance(
        SealedStore(stores), unit_provenance("x1b", "mean-field-twin", sizes.size)
    )
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    error = None
    try:
        execute_swapped_cell(
            unit, position, stores / f"a{position}", twin_generator, size=sizes.size
        )
    except ValueError as failure:
        error = repr(failure)
    path = stores / f"a{position}" / "result.json"
    result = json.loads(path.read_bytes()) if path.exists() else None
    seal = stores / f"a{position}" / "seal.json"
    return {
        "schema": "ic-study.v4-exploratory-x1b-cell.v1",
        "cell": {
            "index": index,
            "unit": unit.key,
            "position": position,
            "a": cell.share,
            "r": cell.reliability,
            "block": RELIABILITIES.index(cell.reliability),
            "family": cell.family,
            "channel": cell.channel,
            "generator": "mean-field-twin",
        },
        "sizes": asdict(sizes),
        "verification_sha256": verification,
        "error": error,
        "success": None if result is None else result["success"],
        "attempts": []
        if result is None
        else [attempt["status"] for attempt in result["attempts"]],
        "seal_sha256": json.loads(seal.read_bytes())["sha256"]
        if seal.exists()
        else None,
        "successor": successor_provenance(),
        "timing": {
            "started_utc": started,
            "finished_utc": utc_now(),
            "wall_seconds": time.perf_counter() - clock,
            "cpu_seconds": time.process_time() - cpu,
        },
    }


def x1b_analysis(
    directory: Path, verification: str, sizes: X1bSizes = DECLARED_X1B
) -> Analysis:
    return Analysis(
        "x1b",
        len(x1b_cells()),
        asdict(sizes),
        lambda index: x1b_cell(index, directory, verification, sizes),
    )


def aggregate_x1b(directory: Path, sizes: X1bSizes = DECLARED_X1B) -> dict[str, Any]:
    """Frozen ``complete_curve`` on every unit whose nine cells have results."""
    records = load_records(directory, "x1b", len(x1b_cells()))
    if any(record["sizes"] != asdict(sizes) for record in records):
        raise ValueError("X1b cells were not all run at the requested sizes")
    curves: list[dict[str, object]] = []
    for unit in x1b_units():
        errors = {
            record["cell"]["a"]: record["error"]
            for record in records
            if record["cell"]["unit"] == unit.key and record["error"]
        }
        if errors:
            curves.append({"unit": unit.key, "status": "cell errors", "errors": errors})
            continue
        store = SealedStore(directory / "stores" / unit.key)
        curve = complete_curve(unit, store.root)
        if not (store.root / "seal.json").exists():
            store.seal()
        curves.append(curve)
    return {
        "schema": "ic-study.v4-exploratory-x1b.v1",
        "label": "exploratory; never promoted to confirmatory evidence",
        "estimand": "a*_MF(r): mean-field twin against null B, frozen tier-1 rules",
        "declaration": declaration_digests(),
        "sizes": asdict(sizes),
        "verification_sha256": sorted({r["verification_sha256"] for r in records}),
        "summary": [
            {
                "r": unit.cells[0].reliability,
                "unit": unit.key,
                **{
                    key: curve.get(key)
                    for key in (
                        "status",
                        "valid_null_gate",
                        "gap_count",
                        "first",
                        "first_interval",
                        "sustained",
                        "sustained_interval",
                    )
                },
            }
            for unit, curve in zip(x1b_units(), curves, strict=True)
        ],
        "seeds": {**SEEDS, "common_across_strengths": True},
        "code": shared_provenance(records, "code"),
        "host": shared_provenance(records, "host"),
        "timing": timing_summary(records),
        "curves": curves,
        "cells": [
            {k: v for k, v in record.items() if k != "provenance"} for record in records
        ],
    }


def _indices(text: str | None) -> list[int] | None:
    return None if text is None else [int(part) for part in text.split(",")]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="v4 exploratory X1b")
    commands = parser.add_subparsers(dest="command", required=True)
    side = commands.add_parser("precondition")
    side.add_argument("--out", type=Path, required=True)
    side.add_argument("--cell", type=int, required=True)
    side.add_argument("--side", choices=SIDES, required=True)
    check = commands.add_parser("verify")
    check.add_argument("--out", type=Path, required=True)
    check.add_argument("--output", type=Path, required=True)
    run = commands.add_parser("x1b")
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--verification", type=Path, required=True)
    run.add_argument("--shard", type=int, default=0)
    run.add_argument("--shards", type=int, default=1)
    run.add_argument("--only", help="comma-separated cell indices")
    aggregate = commands.add_parser("aggregate")
    aggregate.add_argument("--out", type=Path, required=True)
    aggregate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "aggregate":
        write_json(args.output, aggregate_x1b(args.out))
        return 0
    if args.command == "verify":
        result = verify(args.out)
        write_json(args.output, result)
        print(json.dumps({"passed": result["passed"]}))
        return 0 if result["passed"] else 1
    require_frozen_closure()
    if args.command == "precondition":
        record = precondition_side(args.out, args.cell, args.side)
        print(json.dumps({k: record[k] for k in ("position", "side", "error")}))
        return 0
    verification = require_verification(args.verification, DECLARED_X1B.size)
    run_shard(
        x1b_analysis(args.out, verification),
        args.out,
        shard=args.shard,
        shards=args.shards,
        only=_indices(args.only),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
