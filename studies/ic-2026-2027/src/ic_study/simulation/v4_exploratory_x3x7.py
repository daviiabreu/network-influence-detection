"""Shared successor machinery for the v4 exploratory analyses X3 to X7.

Declared on 2026-09-28 in
``experiments/exploratory/detection-boundary-v4-exploratory/README-x3-x7.md``
before any confirmatory result. This module holds what the five analyses
share: the ``v4-exploratory-x3-x7`` seed namespace and a plan with the frozen
``SeedPlan`` interface, the tier-1 successor source and cell executor,
provenance checked against ``freeze-v4.json`` for every unit, the sealing and
release rules, the bitwise precondition harness, the resumable runner and the
command line every analysis module exposes. Frozen v4 components and the X1/X2
utilities are imported, never edited. Outputs are exploratory and never
promoted to confirmatory evidence.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.analysis.detection_boundary import auc
from ic_study.analysis.detection_boundary_v4 import Uncertainty
from ic_study.models.anchored_panel import Floats
from ic_study.simulation import v4_curve
from ic_study.simulation.detection_v4 import (
    RELIABILITIES,
    Cell,
    PanelSource,
    SeedPlan,
    pipeline,
)
from ic_study.simulation.detection_v4 import ROLES as FROZEN_ROLES
from ic_study.simulation.v4_curve import CurveUnit, _put_array, curve_units, deadline
from ic_study.simulation.v4_exploratory import (
    FREEZE,
    SIZE,
    STUDY,
    _git,
    host_description,
    observed_profile,
    utc_now,
    write_json,
)
from ic_study.simulation.v4_exploratory_x1b import (
    compare_cells,
    ensure_provenance,
    original_generator,
)
from ic_study.simulation.v4_gate import manifest, pipeline_record
from ic_study.simulation.v4_store import SealedStore

NAMESPACE = "v4-exploratory-x3-x7"
ROOT = 20260928
LABEL = "exploratory; never promoted to confirmatory evidence"
FROZEN_PHASES = frozenset(
    {
        "match",
        "validate",
        "train",
        "check",
        "reference",
        "nuisance",
        "bootstrap",
        "stencil",
    }
)
ANALYSES = {
    "x3": FROZEN_PHASES,
    "x4": FROZEN_PHASES | {"test", "single-fit", "single-null"},
    "x5": FROZEN_PHASES,
    "x6-rep": FROZEN_PHASES,
    "x6b-rep": FROZEN_PHASES,
    "x6-truth": FROZEN_PHASES,
    "x6-pop": FROZEN_PHASES,
    "x7": FROZEN_PHASES,
}
ROLES = frozenset(FROZEN_ROLES | {"resample"})
SEEDS = {
    "namespace": NAMESPACE,
    "root": ROOT,
    "material": "{namespace}|{root}|{analysis}|{block}|{phase}|{role}|{index}",
    "block": "2 * block + attempt, the frozen layout",
    "digest": "sha256(material)[:8] as big-endian unsigned",
}
DECLARATION = STUDY / "experiments/exploratory/detection-boundary-v4-exploratory"
STATE = Path.home() / ".local/state/research-workbench"
SEALED_ROOT = STATE / "sealed-v4-exploratory-x3-x7"
RELEASE_RECORD = STATE / "coord-20260925/v4-release/release-record.json"
WINDOW_CLOSE = datetime(2026, 10, 10, 2, 59, tzinfo=UTC)
FOUNDATION = Path(__file__).resolve()
REUSED = (
    STUDY / "src/ic_study/simulation/v4_exploratory.py",
    STUDY / "src/ic_study/simulation/v4_exploratory_x1b.py",
)
SIDES = ("frozen", "successor")
PRECONDITION_SCHEMA = "ic-study.v4-exploratory-x3-x7-precondition.v1"
STORE_RULE = (
    "frozen executor and successor executor at its neutral setting, same "
    "successor unit and seeds, declared sizes, separate processes on one host "
    "and commit; every file of each cell store equal byte for byte except "
    "access.jsonl, whose (action, key) sequence must be equal"
)
PROBE_BASE = 1 << 40

type SeedFn = Callable[[str, int], int]
type SocialProfile = Callable[[Cell, int, SeedFn, int, bool], Floats]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _log(**fields: object) -> None:
    print(json.dumps(fields, sort_keys=True), flush=True)


# Seeds, plans and units -------------------------------------------------------


def derive_seed(analysis: str, block: int, phase: str, role: str, index: int) -> int:
    """SHA-256 stream seed whose preimage leads with this namespace and root."""
    if (
        phase not in ANALYSES.get(analysis, ())
        or role not in ROLES
        or min(block, index) < 0
    ):
        raise ValueError("Invalid successor seed material")
    material = f"{NAMESPACE}|{ROOT}|{analysis}|{block}|{phase}|{role}|{index}"
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


@dataclass(frozen=True)
class SuccessorSeedPlan(SeedPlan):
    """The frozen ``SeedPlan`` interface over the ``v4-exploratory-x3-x7`` namespace.

    Blocks keep the frozen ``2 * block + attempt`` layout. The plan has no gate
    or repetition branch and derives nothing outside this namespace.
    """

    analysis: str = ""

    def seed(self, phase: str, role: str, index: int, *, attempt: int = 0) -> int:
        if self.gate or self.repetition or attempt not in (0, 1):
            raise ValueError("Successor plans have no gate, repetition or third try")
        return derive_seed(self.analysis, 2 * self.block + attempt, phase, role, index)


@dataclass(frozen=True)
class SuccessorUnit(CurveUnit):
    """A frozen curve unit whose streams come from the successor plan.

    Frozen ``execute_cell`` and ``complete_curve`` read only ``key``,
    ``cells`` and ``seeds.seed``.
    """

    analysis: str = ""
    block: int = 0

    @property
    def seeds(self) -> SuccessorSeedPlan:  # type: ignore[override]
        return SuccessorSeedPlan(block=self.block, analysis=self.analysis)


def tier1_units(analysis: str, prefix: str | None = None) -> tuple[SuccessorUnit, ...]:
    """The nine frozen tier-1 units (family B, observed channel); block = r index."""
    return tuple(
        SuccessorUnit(
            f"{prefix or analysis}-{unit.key}",
            unit.tier,
            unit.cells,
            analysis,
            RELIABILITIES.index(unit.cells[0].reliability),
        )
        for unit in curve_units()
        if unit.tier == 1
    )


def find_cell(
    units: Sequence[SuccessorUnit], share: float, reliability: float
) -> tuple[SuccessorUnit, int]:
    for unit in units:
        for index, cell in enumerate(unit.cells):
            if (cell.share, cell.reliability) == (share, reliability):
                return unit, index
    raise ValueError("Cell is outside these units")


# Tier-1 successor source and cell executor ------------------------------------


def frozen_social_profile(
    cell: Cell, size: int, seed: SeedFn, index: int, coupled: bool
) -> Floats:
    """The frozen social row of ``PanelSource._profiles`` for a tier-1 cell."""
    latent = original_generator(cell, size, seed, index, coupled)
    return observed_profile(
        latent, cell.reliability, seed("mask", index), seed("error", index)
    )


class SuccessorSource(PanelSource):
    """Frozen ``PanelSource`` for a tier-1 cell with an injected social row.

    Null panels come from the frozen ``_profiles``. Social panels keep its
    index layout and seeds; ``frozen_social_profile`` reproduces them.
    """

    def __init__(
        self,
        cell: Cell,
        seeds: SeedPlan,
        *,
        social: SocialProfile = frozen_social_profile,
        size: int = SIZE,
        store: SealedStore | None = None,
    ) -> None:
        if cell != Cell(cell.share, cell.reliability):
            raise ValueError("The successor covers tier-1 cells only")
        if not isinstance(seeds, SuccessorSeedPlan):
            raise ValueError("The successor draws successor seeds only")
        super().__init__(cell, seeds, size=size, store=store)
        self.social = social

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
            rows.append(self.social(self.cell, self.size, seed, 2 * j + 1, coupled))
            self.panels += 1
        return np.stack(rows)


type SourceFactory = Callable[[Cell, SuccessorSeedPlan, SealedStore, int], PanelSource]


def execute_source_cell(
    unit: SuccessorUnit,
    index: int,
    directory: Path,
    source: SourceFactory,
    *,
    size: int = SIZE,
) -> None:
    """Frozen ``v4_curve.execute_cell`` with the factory's source for ``PanelSource``.

    Tier-1 cells have no control dependency, so the frozen lookup, which
    returns none for them, is omitted. Store layout, record, arrays and seal
    are the frozen ones.
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
                source(cell, unit.seeds, store, size), compute_uncertainty=False
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


# Shared statistics --------------------------------------------------------------


def fixed_band(
    result: Uncertainty, critical: float, *, networks: int = 2000
) -> tuple[Floats, Floats]:
    """Frozen ``band`` interval formula (logit, floor 1/(2n)) at a fixed critical."""
    epsilon = 1 / (2 * networks)
    point = np.clip(result.point, epsilon, 1 - epsilon)
    logit = np.log(point / (1 - point))
    se = np.maximum(result.se, epsilon) / (point * (1 - point))
    lower = 1 / (1 + np.exp(np.clip(-logit + critical * se, -700, 700)))
    upper = 1 / (1 + np.exp(np.clip(-logit - critical * se, -700, 700)))
    return (
        np.asarray(np.where(result.point == 0, 0, lower), dtype=np.float64),
        np.asarray(np.where(result.point == 1, 1, upper), dtype=np.float64),
    )


def paired_network_bootstrap(
    contrasts: Sequence[tuple[Floats, Floats]], *, seed: int, resamples: int
) -> Floats:
    """AUC replicates of several contrasts under the frozen network resampling.

    Each resample draws the null network rows, then the social ones, as frozen
    ``score_uncertainty`` does, keeping both events of a network. Every
    contrast uses the same indices, so the replicates are paired.
    """
    shapes = {(null.shape, social.shape) for null, social in contrasts}
    if len(shapes) != 1:
        raise ValueError("Paired contrasts need aligned network x two-event scores")
    null_shape, social_shape = shapes.pop()
    if len(null_shape) != 2 or null_shape[1] != 2 or social_shape[1:] != (2,):
        raise ValueError("Paired contrasts need aligned network x two-event scores")
    rng = np.random.default_rng(seed)
    draws = np.empty((resamples, len(contrasts)))
    for b in range(resamples):
        left = rng.integers(null_shape[0], size=null_shape[0])
        right = rng.integers(social_shape[0], size=social_shape[0])
        draws[b] = [
            auc(null[left].ravel(), social[right].ravel()) for null, social in contrasts
        ]
    return draws


def percentile_interval(draws: Floats) -> list[float]:
    return [float(q) for q in np.quantile(draws, [0.025, 0.975])]


# Provenance -----------------------------------------------------------------------


def declaration_digests() -> dict[str, str]:
    return {
        "readme_sha256": _digest(DECLARATION / "README-x3-x7.md"),
        "declaration_sha256": _digest(DECLARATION / "declaration-x3-x7.json"),
    }


def successor_provenance(modules: Sequence[Path] = ()) -> dict[str, Any]:
    """Successor module digests and the frozen Python closure against freeze-v4."""
    freeze = json.loads((STUDY / FREEZE).read_bytes())["code"]
    frozen = sorted(path for path in freeze if path.endswith(".py"))
    paths = dict.fromkeys([FOUNDATION, *REUSED, *(Path(m).resolve() for m in modules)])
    return {
        "successor_sha256": {str(p.relative_to(STUDY)): _digest(p) for p in paths},
        "freeze_sha256": _digest(STUDY / FREEZE),
        "frozen_python_files": len(frozen),
        "frozen_python_mismatched": [
            path
            for path in frozen
            if not (STUDY / path).is_file() or _digest(STUDY / path) != freeze[path]
        ],
        "declaration": declaration_digests(),
    }


def require_frozen_closure(modules: Sequence[Path] = ()) -> dict[str, Any]:
    provenance = successor_provenance(modules)
    if provenance["frozen_python_mismatched"]:
        raise ValueError("Frozen v4 sources differ from freeze-v4.json")
    return provenance


def code_provenance() -> dict[str, Any]:
    status = _git("status", "--porcelain", "--untracked-files=no", "--", ".")
    return {
        "commit": _git("rev-parse", "HEAD"),
        "tracked_tree_clean": None if status is None else status == "",
        "lock_sha256": _digest(STUDY / "uv.lock"),
    }


def require_clean_tree() -> dict[str, Any]:
    code = code_provenance()
    if code["commit"] is None or code["tracked_tree_clean"] is not True:
        raise ValueError("Successor runs need a clean tracked tree at a commit")
    return code


def host_class() -> dict[str, object]:
    """CPU model, system and frozen environment hash: the precondition scope."""
    host = host_description()
    return {
        "cpu": host["cpu"],
        "system": host["system"],
        "environment_sha256": manifest(STUDY)["environment_sha256"],
    }


def unit_provenance(label: str, size: int) -> dict[str, object]:
    """Frozen ``manifest`` plus the successor labels, stored once per unit."""
    return {
        **manifest(STUDY),
        "analysis": label,
        "size": size,
        "namespace": NAMESPACE,
        "root": ROOT,
        "declaration": declaration_digests(),
        "freeze_sha256": _digest(STUDY / FREEZE),
    }


# Sealing and release ----------------------------------------------------------------


def private_directory(path: Path) -> Path:
    """Create every missing level of ``path`` with mode 0700."""
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    for directory in reversed(missing):
        directory.mkdir(mode=0o700, exist_ok=True)
    return path


def write_private_json(path: Path, value: dict[str, Any]) -> None:
    private_directory(path.parent)
    write_json(path, value)


def require_sealed_location(out: Path) -> Path:
    """Every X3-X7 output lives under the 0700 sealed root, outside checkouts."""
    root = private_directory(SEALED_ROOT)
    if root.is_symlink() or root.stat().st_mode & 0o077:
        raise ValueError("Sealed root must be a 0700 directory")
    resolved = out.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Successor outputs must lie under {SEALED_ROOT}")
    return private_directory(resolved)


def released(*, now: datetime | None = None) -> bool:
    """The confirmatory release: its record exists or the frozen close passed."""
    return RELEASE_RECORD.is_file() or (now or datetime.now(UTC)) >= v4_curve.CLOSE


def require_release(*, now: datetime | None = None) -> dict[str, Any]:
    if not released(now=now):
        raise ValueError("Sealed until the confirmatory release")
    present = RELEASE_RECORD.is_file()
    return {
        "release_record": str(RELEASE_RECORD) if present else None,
        "release_record_sha256": _digest(RELEASE_RECORD) if present else None,
        "frozen_close_utc": v4_curve.CLOSE.isoformat(),
        "checked_utc": utc_now(),
    }


# Bitwise precondition harness -------------------------------------------------------

type Executor = Callable[[SuccessorUnit, int, Path, int], None]


def frozen_cell_executor(
    unit: SuccessorUnit, index: int, directory: Path, _size: int
) -> None:
    """Frozen ``v4_curve.execute_cell``; its ``PanelSource`` has the declared size."""
    v4_curve.execute_cell(unit, index, directory)


@dataclass(frozen=True)
class Precondition:
    """A declared bitwise precondition: one frozen and one successor executor.

    Each executor writes one cell store; ``verify`` compares the two stores of
    every cell file by file and counts a cell as reaching a result when the
    frozen store has ``result.json``.
    """

    name: str
    units: tuple[SuccessorUnit, ...]
    cells: tuple[tuple[float, float], ...]
    successor: Executor
    frozen: Executor = frozen_cell_executor
    modules: tuple[Path, ...] = ()
    rule: str = STORE_RULE

    def cell(self, position: int) -> tuple[SuccessorUnit, int]:
        return find_cell(self.units, *self.cells[position])

    def directory(self, out: Path, side: str, position: int) -> Path:
        unit, index = self.cell(position)
        return out / "precondition" / self.name / side / unit.key / f"a{index}"

    def run_record(self, out: Path, side: str, position: int) -> Path:
        return out / "precondition" / self.name / "runs" / f"{side}-{position}.json"

    def verification(self, out: Path) -> Path:
        return out / f"{self.name}-precondition.json"


def precondition_side(
    spec: Precondition, out: Path, position: int, side: str, *, size: int = SIZE
) -> dict[str, Any]:
    """One side of one precondition cell; a ValueError is recorded, not hidden."""
    if side not in SIDES:
        raise ValueError("Unknown precondition side")
    unit, index = spec.cell(position)
    directory = spec.directory(out, side, position)
    private_directory(directory.parent)
    ensure_provenance(
        SealedStore(directory.parent),
        unit_provenance(f"{spec.name}-precondition", size),
    )
    executor = spec.frozen if side == "frozen" else spec.successor
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    error = None
    try:
        executor(unit, index, directory, size)
    except ValueError as failure:
        error = repr(failure)
    record = {
        "schema": "ic-study.v4-exploratory-x3-x7-precondition-side.v1",
        "name": spec.name,
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
        "successor": successor_provenance(spec.modules),
        "host": host_description(),
        "host_class": host_class(),
    }
    write_private_json(spec.run_record(out, side, position), record)
    return record


def verify(spec: Precondition, out: Path, *, size: int = SIZE) -> dict[str, Any]:
    """The declared rule over every cell of ``spec`` run in ``out``.

    It passes when both executors ran on this host class at this commit, size
    and successor, every cell's stores are byte-identical with identical unit
    provenance and identical errors, and at least two cells reached a result.
    """
    code, successor, scope = (
        code_provenance(),
        successor_provenance(spec.modules),
        host_class(),
    )
    cells = []
    for position, (share, reliability) in enumerate(spec.cells):
        unit, index = spec.cell(position)
        sides = {side: spec.directory(out, side, position) for side in SIDES}
        runs = {
            side: json.loads(spec.run_record(out, side, position).read_bytes())
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
            and runs[side]["host_class"] == scope
            for side in SIDES
        )
        errors = [runs[side]["error"] for side in SIDES]
        path = sides["frozen"] / "result.json"
        result = json.loads(path.read_bytes()) if path.exists() else None
        attempts = [] if result is None else result.get("attempts", [])
        cells.append(
            {
                "a": share,
                "r": reliability,
                "unit": unit.key,
                "index": index,
                **comparison,
                "stores_equal": comparison["equal"],
                "equal": comparison["equal"]
                and provenance[0] == provenance[1]
                and errors[0] == errors[1]
                and same_run,
                "result": result is not None,
                "success": None if result is None else result.get("success"),
                "attempts": [
                    attempt["status"]
                    for attempt in attempts
                    if isinstance(attempt, dict)
                ],
                "errors": dict(zip(SIDES, errors, strict=True)),
                "same_commit_size_successor_and_host_class": same_run,
                "unit_provenance_equal": provenance[0] == provenance[1],
                "unit_provenance_sha256": hashlib.sha256(provenance[0]).hexdigest(),
                "timing": {side: runs[side]["timing"] for side in SIDES},
            }
        )
    reproduced = sum(cell["equal"] and cell["result"] for cell in cells)
    return {
        "schema": PRECONDITION_SCHEMA,
        "name": spec.name,
        "label": LABEL,
        "declaration": declaration_digests(),
        "rule": spec.rule,
        "size": size,
        "cells": cells,
        "cells_reproduced_with_result": reproduced,
        "passed": all(cell["equal"] for cell in cells) and reproduced >= 2,
        "seeds": SEEDS,
        "code": code,
        "successor": successor,
        "host": host_description(),
        "host_class": scope,
        "verified_utc": utc_now(),
    }


def require_verification(spec: Precondition, path: Path, *, size: int = SIZE) -> str:
    """A unit runs only after a passing precondition of this exact successor
    at this commit on this host class."""
    record = json.loads(path.read_bytes())
    if (
        record.get("schema") != PRECONDITION_SCHEMA
        or record.get("name") != spec.name
        or record.get("passed") is not True
        or record.get("size") != size
        or record["code"]["commit"] != code_provenance()["commit"]
        or record["successor"] != successor_provenance(spec.modules)
        or record["host_class"] != host_class()
    ):
        raise ValueError(f"{spec.name} needs a passing precondition on this host class")
    return _digest(path)


# Resumable runner -------------------------------------------------------------------


@dataclass(frozen=True)
class Analysis:
    """One declared analysis: its unit count, sizes and per-unit computation."""

    kind: str
    total: int
    sizes: dict[str, int]
    compute: Callable[[int], dict[str, Any]]
    modules: tuple[Path, ...] = ()
    verification: Mapping[str, str] = field(default_factory=dict)
    identities: Sequence[Mapping[str, Any]] = ()
    identity_key: str = "cell"


def record_key(kind: str, index: int) -> str:
    return f"{kind}-{index:04d}"


@contextmanager
def claim(path: Path) -> Iterator[bool]:
    """Non-blocking exclusive lock; the kernel frees it if the holder dies."""
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
        else:
            yield True
    finally:
        os.close(descriptor)


def copy_verification(source: Path, target: Path) -> None:
    data = source.read_bytes()
    descriptor, name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            if target.read_bytes() != data:
                raise ValueError("Output contains a different verification") from None
    finally:
        temporary.unlink(missing_ok=True)


def run_manifest() -> dict[str, Any]:
    modules = tuple(
        FOUNDATION.with_name(f"v4_exploratory_x{k}.py") for k in range(3, 8)
    )
    return {
        "schema": "ic-study.v4-exploratory-run.v1",
        "code": code_provenance(),
        "successor": require_frozen_closure(modules),
        "host_class": host_class(),
        "seeds": SEEDS,
        "window_close": WINDOW_CLOSE.isoformat(),
    }


def bind_run(out: Path, analysis: Analysis) -> dict[str, Any]:
    expected = run_manifest()
    store = SealedStore(out)
    descriptor = os.open(out / "manifest.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        existing = store.get_json("run-manifest")
        if existing is None:
            if any(
                p.is_dir() and (p.name == "stores" or p.name.startswith("x"))
                for p in out.iterdir()
            ):
                raise ValueError(
                    "Existing outputs have no run manifest; "
                    "explicit compatibility required"
                )
            store.put_json("run-manifest", expected)
        elif existing != expected:
            raise ValueError("Output run manifest differs from this implementation")
        binding = {
            "identities": list(analysis.identities),
            "identity_key": analysis.identity_key,
            "verification_required": bool(analysis.modules),
            "kind": analysis.kind,
            "total": analysis.total,
            "sizes": analysis.sizes,
            "verification_sha256": dict(analysis.verification),
            "run_manifest_sha256": _digest(out / "run-manifest.json"),
            "successor": require_frozen_closure(analysis.modules),
        }
        key = f"manifest-{analysis.kind}"
        prior = store.get_json(key)
        if prior is None:
            store.put_json(key, binding)
        elif prior != binding:
            raise ValueError(
                f"{analysis.kind} manifest has different sizes or provenance"
            )
        return binding
    finally:
        os.close(descriptor)


def validate_record(
    record: Mapping[str, Any],
    kind: str,
    index: int,
    binding: Mapping[str, Any],
    manifest_record: Mapping[str, Any],
) -> None:
    provenance = record.get("provenance", {})
    if (
        record.get("sizes") != binding["sizes"]
        or record.get("run_identity") != {"kind": kind, "index": index}
        or record.get("cell", {}).get("index", index) != index
        or (
            binding.get("identities")
            and record.get(binding["identity_key"]) != binding["identities"][index]
        )
        or record.get("run_manifest_sha256") != binding["run_manifest_sha256"]
        or record.get("verification_sha256", {}) != binding["verification_sha256"]
        or provenance.get("code") != manifest_record["code"]
        or provenance.get("successor") != binding["successor"]
        or provenance.get("host_class") != manifest_record["host_class"]
    ):
        raise ValueError(f"Incompatible record {record_key(kind, index)}")


def _existing(
    store: SealedStore,
    kind: str,
    index: int,
    binding: Mapping[str, Any],
    manifest_record: Mapping[str, Any],
) -> bool:
    record = store.get_json(record_key(kind, index))
    if record is None:
        return False
    validate_record(record, kind, index, binding, manifest_record)
    return True


def run_shard(
    analysis: Analysis,
    out: Path,
    *,
    shard: int = 0,
    shards: int = 1,
    only: Sequence[int] | None = None,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> list[int]:
    """Compute this shard's missing units in declared index order.

    Workers of one shard claim units through per-unit locks, so any number of
    them share the queue. Every unit re-checks the frozen closure and records
    commit, tree state, successor digests and host. Standard output carries
    unit ids, status and timings only. No unit starts after the window close.
    """
    if not 0 <= shard < shards:
        raise ValueError("Require 0 <= shard < shards")
    root = require_sealed_location(out)
    binding = bind_run(root, analysis)
    manifest_record = json.loads((root / "run-manifest.json").read_bytes())
    records = SealedStore(private_directory(root / analysis.kind))
    locks = private_directory(root / "locks")
    done = []
    for index in range(analysis.total):
        if index % shards != shard or (only is not None and index not in only):
            continue
        if now() >= WINDOW_CLOSE:
            _log(kind=analysis.kind, status="window-closed")
            break
        key = record_key(analysis.kind, index)
        if _existing(records, analysis.kind, index, binding, manifest_record):
            continue
        with claim(locks / f"{key}.lock") as claimed:
            if not claimed or _existing(
                records, analysis.kind, index, binding, manifest_record
            ):
                continue
            successor = require_frozen_closure(analysis.modules)
            code = code_provenance()
            record = analysis.compute(index)
            record["provenance"] = {
                "code": code,
                "successor": successor,
                "host": host_description(),
                "host_class": host_class(),
                "shard": shard,
                "shards": shards,
                "pid": os.getpid(),
            }
            record["run_identity"] = {"kind": analysis.kind, "index": index}
            record["run_manifest_sha256"] = binding["run_manifest_sha256"]
            validate_record(record, analysis.kind, index, binding, manifest_record)
            records.put_json(key, record)
        _log(
            kind=analysis.kind,
            unit=index,
            status="error" if record.get("error") else "complete",
            wall_seconds=round(record["timing"]["wall_seconds"], 1),
            cpu_seconds=round(record["timing"]["cpu_seconds"], 1),
        )
        done.append(index)
    return done


def load_records(out: Path, kind: str, total: int) -> dict[int, dict[str, Any]]:
    store = SealedStore(out / kind)
    records = {}
    for index in range(total):
        record = store.get_json(record_key(kind, index))
        if record is not None:
            records[index] = record
    return records


def validate_legacy_records(
    out: Path,
    kind: str,
    records: Mapping[int, Mapping[str, Any]],
    sizes: Mapping[str, int],
    spec: Precondition,
    identities: Sequence[Mapping[str, Any]],
) -> None:
    pin = json.loads((DECLARATION / "compatibility-c8e4861f.json").read_bytes())
    if (
        kind not in ("x5", "x7")
        or spec.name != kind
        or pin["declaration"] != declaration_digests()
    ):
        raise ValueError("Unsupported legacy compatibility")
    path = spec.verification(out)
    if not path.is_file():
        raise ValueError(f"Missing legacy {kind} verification")
    evidence = json.loads(path.read_bytes())
    cells = evidence.get("cells", [])
    successor = pin["successors"][kind]
    if (
        evidence.get("schema") != PRECONDITION_SCHEMA
        or evidence.get("name") != kind
        or evidence.get("passed") is not True
        or evidence.get("size") != sizes["size"]
        or evidence.get("code") != pin["code"]
        or evidence.get("successor") != successor
        or evidence.get("declaration") != pin["declaration"]
        or evidence.get("seeds") != SEEDS
        or not evidence.get("host_class")
        or [(c.get("a"), c.get("r")) for c in cells] != list(spec.cells)
        or sum(c.get("result") is True for c in cells) < 2
        or any(
            c.get("equal") is not True
            or c.get("same_commit_size_successor_and_host_class") is not True
            or c.get("unit_provenance_equal") is not True
            or set(c.get("errors", {})) != set(SIDES)
            or c["errors"]["frozen"] != c["errors"]["successor"]
            for c in cells
        )
    ):
        raise ValueError(f"Incompatible legacy {kind} verification")
    for index, record in records.items():
        provenance = record.get("provenance", {})
        if (
            record.get("schema") != f"ic-study.v4-exploratory-{kind}-cell.v1"
            or record.get("sizes") != sizes
            or record.get("cell") != identities[index]
            or provenance.get("code") != pin["code"]
            or provenance.get("successor") != successor
            or provenance.get("host_class") != evidence["host_class"]
            or record.get("verification_sha256") != {kind: _digest(path)}
            or (
                kind == "x7"
                and not record.get("error")
                and not record.get("rich_error")
                and record.get("rich_success") is None
            )
        ):
            raise ValueError(f"Incompatible legacy record {record_key(kind, index)}")


def compatibility_summary(out: Path) -> dict[str, Any] | None:
    if (out / "run-manifest.json").exists():
        return None
    pin = json.loads((DECLARATION / "compatibility-c8e4861f.json").read_bytes())
    return {
        "source_commit": pin["code"]["commit"],
        "mode": "aggregate-only",
        "verification": "historical fields revalidated independently of passed",
        "source_records": "unchanged",
        "aggregator_code": code_provenance(),
    }


def _validated_records(
    out: Path,
    kind: str,
    total: int,
    sizes: dict[str, int],
    *,
    legacy_spec: Precondition | None = None,
    identities: Sequence[Mapping[str, Any]] = (),
    identity_key: str = "cell",
    preconditions: Sequence[Precondition] = (),
) -> dict[int, dict[str, Any]]:
    if not (out / "run-manifest.json").is_file() and legacy_spec is None:
        raise ValueError(f"Missing run manifest in {out}")
    records = load_records(out, kind, total)
    if not (out / "run-manifest.json").exists() and legacy_spec is not None:
        validate_legacy_records(out, kind, records, sizes, legacy_spec, identities)
    else:
        manifest_record = json.loads((out / "run-manifest.json").read_bytes())
        binding = json.loads((out / f"manifest-{kind}.json").read_bytes())
        expected = run_manifest()
        if any(
            manifest_record[key] != expected[key]
            for key in ("schema", "successor", "seeds", "window_close")
        ) or any(
            manifest_record["code"][key] != expected["code"][key]
            for key in ("commit", "lock_sha256")
        ):
            raise ValueError(
                "Aggregate needs this run manifest or explicit compatibility"
            )
        if (
            binding["kind"] != kind
            or binding["total"] != total
            or binding["sizes"] != sizes
            or binding["run_manifest_sha256"] != _digest(out / "run-manifest.json")
        ):
            raise ValueError(
                f"{kind} manifest differs from requested sizes or identity"
            )
        if preconditions:
            modules = tuple(
                dict.fromkeys(path for spec in preconditions for path in spec.modules)
            )
            if binding["successor"] != require_frozen_closure(modules) or set(
                binding["verification_sha256"]
            ) != {spec.name for spec in preconditions}:
                raise ValueError(f"{kind} manifest omits required provenance")
        for name, digest in binding["verification_sha256"].items():
            path = out / f"{name}-precondition.json"
            if not path.is_file() or _digest(path) != digest:
                raise ValueError(
                    f"{kind} manifest has incompatible verification {name}"
                )
        successor = binding["successor"]
        closure = manifest_record["successor"]
        if any(
            successor.get(key) != value
            for key, value in closure.items()
            if key != "successor_sha256"
        ) or any(
            closure["successor_sha256"].get(path) != digest
            for path, digest in successor["successor_sha256"].items()
        ):
            raise ValueError(f"{kind} manifest has incompatible successor hashes")
        if (
            identities
            and binding.get("identities")
            and binding["identities"] != list(identities)
        ):
            raise ValueError(f"{kind} manifest has incompatible cell identities")
        for index, record in records.items():
            validate_record(record, kind, index, binding, manifest_record)
    if identities:
        for index, record in records.items():
            if record.get(identity_key) != identities[index]:
                raise ValueError(
                    f"Incompatible cell identity {record_key(kind, index)}"
                )
    if any(record["sizes"] != sizes for record in records.values()):
        raise ValueError(f"{kind} units were not all run at the requested sizes")
    return records


def _finished_records(
    records: dict[int, dict[str, Any]], kind: str, total: int, now: datetime | None
) -> tuple[dict[int, dict[str, Any]], list[int]]:
    missing = [index for index in range(total) if index not in records]
    if missing and (now or datetime.now(UTC)) < WINDOW_CLOSE:
        raise ValueError(f"Missing {kind} units: {missing}")
    late = [
        index
        for index, record in records.items()
        if datetime.fromisoformat(record["timing"]["finished_utc"]) > WINDOW_CLOSE
    ]
    kept = {index: r for index, r in records.items() if index not in late}
    return kept, sorted(missing + late)


def complete_records(
    out: Path,
    kind: str,
    total: int,
    sizes: dict[str, int],
    *,
    now: datetime | None = None,
    legacy_spec: Precondition | None = None,
    identities: Sequence[Mapping[str, Any]] = (),
    identity_key: str = "cell",
    preconditions: Sequence[Precondition] = (),
) -> tuple[dict[int, dict[str, Any]], list[int]]:
    """Validate one directory, then report units finished inside the window.

    Before the window close a missing unit is an error; after it, missing and
    late units are reported as incomplete. X5/X7 retain their legacy path.
    """
    records = _validated_records(
        out,
        kind,
        total,
        sizes,
        legacy_spec=legacy_spec,
        identities=identities,
        identity_key=identity_key,
        preconditions=preconditions,
    )
    return _finished_records(records, kind, total, now)


def union_complete_records(
    outs: Sequence[Path],
    kind: str,
    total: int,
    sizes: dict[str, int],
    *,
    now: datetime | None = None,
    identities: Sequence[Mapping[str, Any]] = (),
    identity_key: str = "cell",
    preconditions: Sequence[Precondition] = (),
) -> tuple[dict[int, dict[str, Any]], list[int], list[dict[str, Any]]]:
    """Validate each source independently before joining disjoint unit indices."""
    if not outs:
        raise ValueError("Aggregate needs at least one output directory")
    records: dict[int, dict[str, Any]] = {}
    sources: list[dict[str, Any]] = []
    common: dict[str, Any] | None = None
    for out in outs:
        members = _validated_records(
            out,
            kind,
            total,
            sizes,
            identities=identities,
            identity_key=identity_key,
            preconditions=preconditions,
        )
        run = json.loads((out / "run-manifest.json").read_bytes())
        binding = json.loads((out / f"manifest-{kind}.json").read_bytes())
        scope = {
            "run": {
                key: value
                for key, value in run.items()
                if key not in ("host_class", "code")
            },
            "code": {key: run["code"][key] for key in ("commit", "lock_sha256")},
            "kind": {
                key: value
                for key, value in binding.items()
                if key not in ("run_manifest_sha256", "verification_sha256")
            },
        }
        if common is not None and scope != common:
            raise ValueError(f"Incompatible source manifests for {kind}: {out}")
        common = scope
        duplicate = records.keys() & members.keys()
        if duplicate:
            raise ValueError(
                f"Duplicate unit {record_key(kind, min(duplicate))} in {out}"
            )
        records.update(members)
        accepted, _ = _finished_records(members, kind, total, WINDOW_CLOSE)
        sources.append(
            {
                "out": str(out),
                "run_manifest_sha256": _digest(out / "run-manifest.json"),
                "host_class": run["host_class"],
                "accepted_units": len(accepted),
            }
        )
    kept, incomplete = _finished_records(records, kind, total, now)
    return kept, incomplete, sources


def timing_summary(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {}
    first = min(r["timing"]["started_utc"] for r in records)
    last = max(r["timing"]["finished_utc"] for r in records)
    elapsed = datetime.fromisoformat(last) - datetime.fromisoformat(first)
    return {
        "first_started_utc": first,
        "last_finished_utc": last,
        "elapsed_seconds": elapsed.total_seconds(),
        "cpu_seconds_total": sum(r["timing"]["cpu_seconds"] for r in records),
        "wall_seconds_per_unit_mean": float(
            np.mean([r["timing"]["wall_seconds"] for r in records])
        ),
    }


def shared_provenance(records: Sequence[dict[str, Any]], key: str) -> list[Any]:
    unique: list[Any] = []
    for record in records:
        if record["provenance"][key] not in unique:
            unique.append(record["provenance"][key])
    return unique


def status(out: Path, kind: str, total: int) -> dict[str, Any]:
    """Counts, fit statuses and timings only; seals the records when complete."""
    store = SealedStore(out / kind)
    records = load_records(out, kind, total)
    values = list(records.values())
    attempts = Counter(
        status for record in values for status in record.get("attempts", [])
    )
    summary = {
        "kind": kind,
        "total": total,
        "recorded": len(values),
        "missing": total - len(values),
        "errors": sum(bool(record.get("error")) for record in values),
        "fit_failures": sum(record.get("success") is False for record in values),
        "attempt_statuses": dict(sorted(attempts.items())),
        "timing": timing_summary(values),
    }
    if len(values) == total and not (store.root / "seal.json").exists():
        store.seal()
    summary["sealed"] = (store.root / "seal.json").exists()
    return summary


# Timing probe -------------------------------------------------------------------------

_PROBE_ROLES = tuple(sorted(ROLES))


def probe_seed(role: str, index: int) -> int:
    """Timing-probe stream: a plain integer outside every seed namespace."""
    return PROBE_BASE + len(_PROBE_ROLES) * index + _PROBE_ROLES.index(role)


def cpu_per_call(make: Callable[[int], object], count: int) -> float:
    started = time.process_time()
    for index in range(count):
        make(index)
    return (time.process_time() - started) / count


# Command line -------------------------------------------------------------------------


@dataclass(frozen=True)
class Suite:
    """What one analysis module exposes to the shared command line."""

    name: str
    sealed: bool
    kinds: tuple[str, ...]
    preconditions: tuple[Precondition, ...]
    analyses: Callable[[Path, Mapping[str, str]], Mapping[str, Analysis]]
    aggregate: Callable[[Path], dict[str, Any]]
    probe: Callable[[int], dict[str, Any]]
    modules: tuple[Path, ...] = ()
    aggregate_union: Callable[[Sequence[Path]], dict[str, Any]] | None = None


def parse_indices(text: str | None) -> list[int] | None:
    if text is None:
        return None
    indices: list[int] = []
    for part in text.split(","):
        first, _, last = part.partition("-")
        indices += range(int(first), int(last or first) + 1)
    return indices


def supervise_until_close(
    command: Sequence[str],
    receipt: Path,
    *,
    close: datetime = WINDOW_CLOSE,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> int:
    remaining = (close - now()).total_seconds()
    started = remaining > 0
    if started:
        process = subprocess.Popen(command, start_new_session=True)
        try:
            return process.wait(timeout=max(0.0, (close - now()).total_seconds()))
        except subprocess.TimeoutExpired:
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    write_private_json(
        receipt,
        {
            "schema": "ic-study.v4-exploratory-operational-incomplete.v1",
            "status": "incomplete",
            "reason": "execution-window-closed",
            "scientific_failure": False,
            "started": started,
            "window_close": close.isoformat(),
            "stopped_utc": now().isoformat(),
            "command": list(command),
        },
    )
    _log(status="window-closed", operational_receipt=str(receipt))
    return 124


def main(suite: Suite, argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"v4 exploratory {suite.name}")
    commands = parser.add_subparsers(dest="command", required=True)
    names = [spec.name for spec in suite.preconditions]
    commands.add_parser("plan", help="precondition jobs as 'name cell side' lines")
    commands.add_parser("describe", help="'name sealed|open kind,...'")
    passing = commands.add_parser("check", help="exit 0 iff every precondition passed")
    passing.add_argument("--out", type=Path, required=True)
    side = commands.add_parser("precondition")
    side.add_argument("--deadline-worker", action="store_true", help=argparse.SUPPRESS)
    side.add_argument("--out", type=Path, required=True)
    side.add_argument("--name", choices=names, required=True)
    side.add_argument("--cell", type=int, required=True)
    side.add_argument("--side", choices=SIDES, required=True)
    check = commands.add_parser("verify")
    check.add_argument("--out", type=Path, required=True)
    check.add_argument("--name", choices=names, required=True)
    run = commands.add_parser("run")
    run.add_argument("--deadline-worker", action="store_true", help=argparse.SUPPRESS)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--kind", choices=suite.kinds, required=True)
    run.add_argument("--verified", type=Path, help="directory of the verifications")
    run.add_argument("--shard", type=int, default=0)
    run.add_argument("--shards", type=int, default=1)
    run.add_argument("--only", help="unit indices, e.g. 0-35,40")
    state = commands.add_parser("status")
    state.add_argument("--out", type=Path, required=True)
    state.add_argument("--kind", choices=suite.kinds, required=True)
    aggregate = commands.add_parser("aggregate")
    aggregate.add_argument("--out", type=Path, action="append", required=True)
    aggregate.add_argument("--output", type=Path, required=True)
    probe = commands.add_parser("probe")
    probe.add_argument("--count", type=int, default=4)
    args = parser.parse_args(argv)
    if args.command in ("run", "precondition") and not args.deadline_worker:
        out = require_sealed_location(args.out)
        receipt = out / "operational" / f"cutoff-{os.getpid()}-{time.time_ns()}.json"
        command = [
            sys.executable,
            "-m",
            f"ic_study.simulation.v4_exploratory_{suite.name}",
            *(sys.argv[1:] if argv is None else argv),
            "--deadline-worker",
        ]
        return supervise_until_close(command, receipt, close=WINDOW_CLOSE)
    specs = {spec.name: spec for spec in suite.preconditions}
    if args.command == "plan":
        for spec in suite.preconditions:
            for position in range(len(spec.cells)):
                for name in SIDES:
                    print(spec.name, position, name)
        return 0
    if args.command == "describe":
        access = "sealed" if suite.sealed else "open"
        print(suite.name, access, ",".join(suite.kinds))
        return 0
    if args.command == "check":
        passed = {}
        for spec in suite.preconditions:
            try:
                require_verification(spec, spec.verification(args.out))
            except (OSError, KeyError, ValueError):
                passed[spec.name] = False
            else:
                passed[spec.name] = True
        _log(**passed)
        return 0 if all(passed.values()) else 1
    if args.command == "probe":
        _log(analysis=suite.name, **suite.probe(args.count))
        return 0
    if args.command == "status":
        total = suite.analyses(args.out, {})[args.kind].total
        _log(**status(require_sealed_location(args.out), args.kind, total))
        return 0
    if args.command == "aggregate":
        if suite.aggregate_union is None and len(args.out) != 1:
            parser.error(f"{suite.name} aggregate accepts exactly one --out")
        if suite.sealed:
            require_release()
        result = (
            suite.aggregate_union(args.out)
            if suite.aggregate_union is not None
            else suite.aggregate(args.out[0])
        )
        write_private_json(args.output, result)
        return 0
    if args.command == "verify":
        spec = specs[args.name]
        result = verify(spec, require_sealed_location(args.out))
        write_private_json(spec.verification(args.out), result)
        _log(name=spec.name, passed=result["passed"])
        return 0 if result["passed"] else 1
    require_frozen_closure(suite.modules)
    require_clean_tree()
    out = require_sealed_location(args.out)
    if args.command == "precondition":
        record = precondition_side(specs[args.name], out, args.cell, args.side)
        _log(**{k: record[k] for k in ("name", "position", "side", "error")})
        return 0
    verified = args.verified or out
    digests = {
        spec.name: require_verification(spec, spec.verification(verified))
        for spec in suite.preconditions
    }
    for spec in suite.preconditions:
        source = spec.verification(verified)
        target = spec.verification(out)
        if source.resolve() != target.resolve():
            copy_verification(source, target)
    run_shard(
        suite.analyses(out, digests)[args.kind],
        out,
        shard=args.shard,
        shards=args.shards,
        only=parse_indices(args.only),
    )
    return 0
