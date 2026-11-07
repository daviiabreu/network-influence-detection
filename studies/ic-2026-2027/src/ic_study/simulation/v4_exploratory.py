"""Exploratory v4 successors X1a (mean-field twin) and X2 (drift R² map).

Declared on 2026-09-28 in
``experiments/exploratory/detection-boundary-v4-exploratory`` before any
confirmatory result. Frozen v4 components are reused by import and never
edited. Outputs are exploratory aggregates and are never promoted to
confirmatory evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ic_study.analysis.detection_boundary import auc
from ic_study.analysis.redesign import fit_discriminant
from ic_study.models.anchored_panel import Floats, Integers, panel_mask
from ic_study.models.detection_panel import bounded_drift, measurement, ordinal_channel
from ic_study.models.detection_panel_v4 import influence
from ic_study.simulation.amendment_a import fast_ranks
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES, selected_features

NAMESPACE = "v4-exploratory-x1-x2"
ROOT = 20260928
SIZE = 10626
WAVES = 11
PHI = 0.85
REPULSION = 0.25
PARTNERS = 8
KNOT_QUANTILES = (0.05, 0.275, 0.5, 0.725, 0.95)
X2_REPULSIONS = (0.25, 0.0)
X2_STEPS = (1, 24)
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
PHASES = {
    "x1a": frozenset({"train", "reference", "bootstrap"}),
    "x1b": FROZEN_PHASES,
    "x2": frozenset({"replicate"}),
}
ROLES = frozenset(
    {"state", "null-state", "network", "xi", "mask", "error", "heap", "resample"}
)
THREAD_VARIABLES = ("OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS")
STUDY = Path(__file__).resolve().parents[3]
DECLARATION = "experiments/exploratory/detection-boundary-v4-exploratory"
FREEZE = "experiments/exploratory/detection-boundary-v4/freeze-v4.json"
FROZEN_SOURCES = (
    "src/ic_study/analysis/detection_boundary.py",
    "src/ic_study/analysis/redesign.py",
    "src/ic_study/models/anchored_panel.py",
    "src/ic_study/models/detection_panel.py",
    "src/ic_study/models/detection_panel_v4.py",
    "src/ic_study/simulation/amendment_a.py",
    "src/ic_study/simulation/detection_v4.py",
)

type SeedFn = Callable[[str, int], int]


def derive_seed(analysis: str, block: int, phase: str, role: str, index: int) -> int:
    """SHA-256 stream seed whose preimage leads with this namespace and root."""
    if (
        phase not in PHASES.get(analysis, ())
        or role not in ROLES
        or min(block, index) < 0
    ):
        raise ValueError("Invalid exploratory seed material")
    material = f"{NAMESPACE}|{ROOT}|{analysis}|{block}|{phase}|{role}|{index}"
    return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


# Mean-field drift ----------------------------------------------------------


type Predicate = Callable[[Floats, Floats], NDArray[np.bool_]]


def _bisect(ordered: Floats, values: Floats, accept: Predicate) -> Integers:
    """First sorted index whose monotone predicate holds, bisected per value."""
    lo = np.zeros(len(values), dtype=np.int64)
    hi = np.full(len(values), len(ordered), dtype=np.int64)
    while True:
        active = lo < hi
        if not active.any():
            return lo
        middle = (lo + hi) // 2
        accepted = accept(ordered[np.minimum(middle, len(ordered) - 1)], values)
        hi = np.where(active & accepted, middle, hi)
        lo = np.where(active & ~accepted, middle + 1, lo)


def first_index(
    ordered: Floats, values: Floats, accept: Predicate, guess: Integers
) -> Integers:
    """Exact first index of a monotone predicate over sorted values.

    A guess is the answer iff the predicate holds at it and fails just
    before it; values whose guess fails that check are bisected.
    """
    size = len(ordered)
    holds = (guess == size) | accept(ordered[np.minimum(guess, size - 1)], values)
    fails_before = (guess == 0) | ~accept(ordered[np.maximum(guess - 1, 0)], values)
    wrong = ~(holds & fails_before)
    if not wrong.any():
        return guess
    exact = guess.copy()
    exact[wrong] = _bisect(ordered, values[wrong], accept)
    return exact


def mean_field_moments(values: Floats, repulsion: float) -> tuple[Floats, Floats]:
    """Exact m(z_i) and v(z_i) of f(z_j - z_i) over the whole current population.

    The window uses the frozen predicate ``|z_j - z_i| <= 1`` on the same
    floating-point gap, so membership agrees with ``bounded_drift`` exactly;
    sums over the window come from prefix sums of the sorted z and z².
    """
    size = len(values)
    ordered = np.sort(values)
    first = np.concatenate(([0.0], np.cumsum(ordered)))
    second = np.concatenate(([0.0], np.cumsum(ordered * ordered)))
    lo = first_index(
        ordered,
        values,
        lambda z_j, z: z_j - z >= -1,
        np.searchsorted(ordered, values - 1, side="left"),
    )
    hi = first_index(
        ordered,
        values,
        lambda z_j, z: z_j - z > 1,
        np.searchsorted(ordered, values + 1, side="right"),
    )
    near = (hi - lo).astype(np.float64)
    near_first = first[hi] - first[lo]
    near_second = second[hi] - second[lo]
    far = size - near
    far_first = first[-1] - near_first
    far_second = second[-1] - near_second
    z = values
    near_gap = near_first - near * z
    far_gap = far_first - far * z
    near_square = near_second - 2 * z * near_first + near * z * z
    far_square = far_second - 2 * z * far_first + far * z * z
    mean = (near_gap - repulsion * far_gap) / size
    square = (near_square + repulsion**2 * far_square) / size
    # v is a variance; the clip only removes rounding below zero.
    variance = np.maximum(square - mean * mean, 0.0)
    return np.asarray(mean, dtype=np.float64), np.asarray(variance, dtype=np.float64)


# Diagnostic re-implementation of the frozen update -------------------------


@dataclass(frozen=True)
class DriftPath:
    """Every step's state (first row initial) and the standardized drift used."""

    states: Floats
    drift: Floats
    steps: int

    @property
    def path(self) -> Floats:
        return self.states[:: self.steps]


def _standardize(drift: Floats, share: float) -> Floats:
    scale = float(drift.std())
    if share > 0 and scale < 1e-12:
        raise ValueError("Degenerate drift cannot receive a variance share")
    return np.asarray((drift - drift.mean()) / max(scale, 1e-12), dtype=np.float64)


def _simulate(
    size: int,
    waves: int,
    state_seed: int,
    drift: Callable[[Floats], Floats],
    *,
    share: float,
    phi: float,
    anchor: float,
    steps: int,
) -> DriftPath:
    """Frozen ``influence`` loop with the raw drift supplied by the caller.

    With ``share == 0`` the trajectory takes the frozen AR branch and the
    drift is computed only as a diagnostic.
    """
    if not 0 <= share < 1 or not 0 <= phi <= 0.999 or not 0 <= anchor <= 1 or steps < 1:
        raise ValueError("Invalid successor kernel")
    rng = np.random.default_rng(state_seed)
    state = fast_ranks(rng.normal(size=size))
    initial = state.copy()
    states = [state]
    drifts = []
    for _ in range(1, waves):
        for _ in range(steps):
            noise = rng.normal(size=size)
            standardized = _standardize(drift(state), share)
            if share:
                innovation = np.sqrt(share) * standardized + np.sqrt(1 - share) * noise
                update = np.asarray(
                    phi * state + np.sqrt(1 - phi**2) * innovation, dtype=np.float64
                )
            else:
                update = phi * state + np.sqrt(1 - phi**2) * noise
            state = fast_ranks((1 - anchor) * update + anchor * initial)
            states.append(state)
            drifts.append(standardized)
    drift_rows = np.stack(drifts) if drifts else np.empty((0, size))
    return DriftPath(np.stack(states), drift_rows, steps)


def network_partners(size: int, network_seed: int) -> Integers:
    network = np.random.default_rng(network_seed)
    return np.stack([network.permutation(size) for _ in range(PARTNERS)], axis=1)


def interaction_path(
    size: int,
    waves: int,
    state_seed: int,
    network_seed: int,
    *,
    share: float,
    phi: float = PHI,
    repulsion: float = REPULSION,
    anchor: float = 0,
    steps: int = 1,
) -> DriftPath:
    """Frozen interaction arm, also exposing the standardized drift of each step.

    At ``share == 0`` the drift comes from a network drawn by the frozen
    scheme and has no effect on the trajectory (the X2 baseline).
    """
    partners = network_partners(size, network_seed)
    return _simulate(
        size,
        waves,
        state_seed,
        lambda values: bounded_drift(values, partners, repulsion),
        share=share,
        phi=phi,
        anchor=anchor,
        steps=steps,
    )


def mean_field_path(
    size: int,
    waves: int,
    state_seed: int,
    xi_seed: int,
    *,
    share: float,
    phi: float = PHI,
    repulsion: float = REPULSION,
    anchor: float = 0,
    steps: int = 1,
) -> DriftPath:
    """Twin: network drift replaced by m(z_i) + xi_i sqrt(v(z_i) / 8)."""
    xi = np.random.default_rng(xi_seed)

    def drift(values: Floats) -> Floats:
        mean, variance = mean_field_moments(values, repulsion)
        sampled = xi.normal(size=len(values))
        return np.asarray(mean + sampled * np.sqrt(variance / PARTNERS))

    return _simulate(
        size,
        waves,
        state_seed,
        drift,
        share=share,
        phi=phi,
        anchor=anchor,
        steps=steps,
    )


# X1a: observed tier-1 panels and the fixed discriminator ------------------


def observed_profile(
    latent: Floats, reliability: float, mask_seed: int, error_seed: int
) -> Floats:
    """Tier-1 observed channel as frozen ``PanelSource`` builds it for family B."""
    if latent.shape[0] != WAVES:
        raise ValueError("Tier-1 panels have eleven waves")
    mask = panel_mask(latent.shape[1], WAVES, mask_seed, retention=0.89)
    measured = measurement(
        latent, reliability, error_seed, heteroscedastic=False, error_correlation=0
    )
    observed = ordinal_channel(measured, mask, midpoint_mass=0, heap_seed=None)
    return selected_features(
        latent, observed, channel="observed", mobility=False, midpoint_mass=0
    )


def arm_profiles(
    share: float,
    reliability: float,
    count: int,
    seed: SeedFn,
    *,
    twin: bool,
    size: int = SIZE,
    start: int = 0,
) -> Floats:
    """Profiles in the frozen train/check/reference index layout.

    The interaction arm takes the odd indices and shares each network between
    two consecutive panels (``index // 4``), as frozen ``PanelSource`` does;
    the twin takes the even indices that the frozen null arm uses.
    """
    rows = []
    for j in range(start, start + count):
        index = 2 * j + (0 if twin else 1)
        if twin:
            latent = mean_field_path(
                size, WAVES, seed("state", index), seed("xi", index), share=share
            ).path
        else:
            latent = influence(
                size,
                WAVES,
                seed("state", index),
                seed("network", index // 4),
                share=share,
                repulsion=REPULSION,
                anchor=0,
                steps=1,
            )
        rows.append(
            observed_profile(
                latent, reliability, seed("mask", index), seed("error", index)
            )
        )
    return np.stack(rows)


def network_bootstrap(
    twin: Floats, arm: Floats, *, seed: int, resamples: int
) -> Floats:
    """Frozen ``score_uncertainty`` resampling: each arm's network rows
    independently, both events of a resampled network kept."""
    if twin.ndim != 2 or twin.shape[1] != 2 or arm.shape != twin.shape:
        raise ValueError("Require network x two events scores for both arms")
    rng = np.random.default_rng(seed)
    draws = np.empty(resamples)
    for b in range(resamples):
        left = twin[rng.integers(len(twin), size=len(twin))]
        right = arm[rng.integers(len(arm), size=len(arm))]
        draws[b] = auc(left.ravel(), right.ravel())
    return draws


@dataclass(frozen=True)
class X1aSizes:
    size: int = SIZE
    train: int = 2000
    networks: int = 2000
    resamples: int = 1000


DECLARED_X1A = X1aSizes()


def x1a_cells() -> tuple[tuple[float, float], ...]:
    return tuple((a, r) for r in RELIABILITIES for a in GRID if a > 0)


class _Recorder:
    """Seed function for one phase that keeps every derived seed in order."""

    def __init__(self, block: int, phase: str) -> None:
        self.block, self.phase = block, phase
        self.seeds: list[int] = []

    def __call__(self, role: str, index: int) -> int:
        value = derive_seed("x1a", self.block, self.phase, role, index)
        self.seeds.append(value)
        return value


def _seed_digest(seeds: Iterable[int]) -> str:
    return hashlib.sha256(np.array(list(seeds), dtype=">u8").tobytes()).hexdigest()


def x1a_cell(index: int, sizes: X1aSizes = DECLARED_X1A) -> dict[str, Any]:
    share, reliability = x1a_cells()[index]
    block = RELIABILITIES.index(reliability)
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    train_seeds, reference_seeds = (
        _Recorder(block, "train"),
        _Recorder(block, "reference"),
    )
    twin_train = arm_profiles(
        share, reliability, sizes.train, train_seeds, twin=True, size=sizes.size
    )
    arm_train = arm_profiles(
        share, reliability, sizes.train, train_seeds, twin=False, size=sizes.size
    )
    model = fit_discriminant(
        np.concatenate([twin_train[:, 2:5], arm_train[:, 2:5]]),
        np.repeat([0, 1], sizes.train),
    )
    trained = time.perf_counter()
    reference = 2 * sizes.networks
    twin_reference = arm_profiles(
        share, reliability, reference, reference_seeds, twin=True, size=sizes.size
    )
    arm_reference = arm_profiles(
        share, reliability, reference, reference_seeds, twin=False, size=sizes.size
    )
    twin_scores = model.score(twin_reference[:, 2:5])
    arm_scores = model.score(arm_reference[:, 2:5])
    point = auc(twin_scores, arm_scores)
    bootstrap_seed = derive_seed("x1a", block, "bootstrap", "resample", 0)
    draws = network_bootstrap(
        twin_scores.reshape(sizes.networks, 2),
        arm_scores.reshape(sizes.networks, 2),
        seed=bootstrap_seed,
        resamples=sizes.resamples,
    )
    lower, upper = (float(q) for q in np.quantile(draws, [0.025, 0.975]))
    twin_mean, arm_mean = twin_reference.mean(0), arm_reference.mean(0)
    return {
        "schema": "ic-study.v4-exploratory-x1a-cell.v1",
        "cell": {
            "index": index,
            "a": share,
            "r": reliability,
            "block": block,
            "family_replaced": "B",
            "channel": "observed",
            "repulsion": REPULSION,
            "anchor": 0,
            "steps": 1,
            "waves": WAVES,
        },
        "sizes": asdict(sizes),
        "auc": point,
        "interval_95": [lower, upper],
        "excludes_half": lower > 0.5 or upper < 0.5,
        "bootstrap_sd": float(draws.std(ddof=1)),
        "lags": {
            "set": "reference panels, all five lags L1..L5 (columns 0:5)",
            "twin_mean": twin_mean.tolist(),
            "arm_mean": arm_mean.tolist(),
            "arm_minus_twin": (arm_mean - twin_mean).tolist(),
            "twin_sd": twin_reference.std(0, ddof=1).tolist(),
            "arm_sd": arm_reference.std(0, ddof=1).tolist(),
        },
        "discriminant": {
            "center": model.center.tolist(),
            "scale": model.scale.tolist(),
            "direction": model.direction.tolist(),
            "midpoint": model.midpoint.tolist(),
        },
        "seeds": {
            "bootstrap": bootstrap_seed,
            "train_count": len(train_seeds.seeds),
            "train_sha256": _seed_digest(train_seeds.seeds),
            "reference_count": len(reference_seeds.seeds),
            "reference_sha256": _seed_digest(reference_seeds.seeds),
        },
        "timing": {
            "started_utc": started,
            "finished_utc": utc_now(),
            "train_seconds": trained - clock,
            "wall_seconds": time.perf_counter() - clock,
            "cpu_seconds": time.process_time() - cpu,
        },
    }


# X2: drift R² map ------------------------------------------------------------


def natural_cubic_basis(values: Floats, knots: Sequence[float] | Floats) -> Floats:
    """Natural cubic spline basis (Hastie, Tibshirani and Friedman, eqs. 5.4-5.5).

    Columns are 1, x and d_k(x) - d_{K-1}(x) for k = 1..K-2, with
    d_k(x) = ((x - t_k)_+^3 - (x - t_K)_+^3) / (t_K - t_k). They span the
    cubic splines with these knots that are linear beyond the boundary knots.
    """
    points = np.asarray(knots, dtype=np.float64)
    if points.ndim != 1 or len(points) < 3 or np.any(np.diff(points) <= 0):
        raise ValueError("Require at least three strictly increasing knots")
    last = points[-1]
    tail = np.maximum(values - last, 0) ** 3

    def difference(k: int) -> Floats:
        return np.asarray(
            (np.maximum(values - points[k], 0) ** 3 - tail) / (last - points[k])
        )

    final = difference(len(points) - 2)
    columns = [np.ones_like(values), values]
    columns += [difference(k) - final for k in range(len(points) - 2)]
    return np.column_stack(columns)


def _residual_sum(response: Floats, design: Floats) -> float:
    coefficients = np.linalg.lstsq(design, response, rcond=None)[0]
    residual = response - design @ coefficients
    return float(residual @ residual)


def r2_gain(response: Floats, base: Floats, added: Floats) -> dict[str, float]:
    """R² of the base and base-plus-added pooled OLS fits and their gains."""
    total = float(((response - response.mean()) ** 2).sum())
    reduced = _residual_sum(response, base)
    full = _residual_sum(response, np.column_stack([base, added]))
    return {
        "r2_reduced": 1 - reduced / total,
        "r2_full": 1 - full / total,
        "partial_r2": (reduced - full) / reduced,
        "incremental_r2": (reduced - full) / total,
    }


@dataclass(frozen=True)
class X2Sizes:
    size: int = SIZE
    waves: int = WAVES
    replicates: int = 10


DECLARED_X2 = X2Sizes()


def x2_conditions() -> tuple[tuple[float, float, int], ...]:
    return tuple(
        (a, b, steps) for steps in X2_STEPS for b in X2_REPULSIONS for a in GRID
    )


def x2_replicate(index: int, sizes: X2Sizes = DECLARED_X2) -> dict[str, Any]:
    condition, replicate = divmod(index, sizes.replicates)
    share, repulsion, steps = x2_conditions()[condition]
    state_seed = derive_seed("x2", 0, "replicate", "state", replicate)
    network_seed = derive_seed("x2", 0, "replicate", "network", replicate)
    started, clock, cpu = utc_now(), time.perf_counter(), time.process_time()
    diagnostic = interaction_path(
        sizes.size,
        sizes.waves,
        state_seed,
        network_seed,
        share=share,
        repulsion=repulsion,
        anchor=0,
        steps=steps,
    )
    frozen = influence(
        sizes.size,
        sizes.waves,
        state_seed,
        network_seed,
        share=share,
        repulsion=repulsion,
        anchor=0,
        steps=steps,
    )
    if not np.array_equal(diagnostic.path, frozen):
        raise RuntimeError("Diagnostic path diverged from frozen influence")
    simulated = time.perf_counter()
    before = diagnostic.states[:-1].ravel()
    after = diagnostic.states[1:].ravel()
    drift = diagnostic.drift.ravel()
    x2a = r2_gain(after, np.column_stack([np.ones_like(before), before]), drift)
    knots = np.quantile(before, KNOT_QUANTILES)
    x2b = r2_gain(after, natural_cubic_basis(before, knots), drift)
    return {
        "schema": "ic-study.v4-exploratory-x2-replicate.v1",
        "unit": index,
        "condition": {
            "index": condition,
            "a": share,
            "repulsion": repulsion,
            "steps": steps,
            "anchor": 0,
            "phi": PHI,
        },
        "replicate": replicate,
        "sizes": asdict(sizes),
        "observations": len(before),
        "bitwise_equal_to_frozen_influence": True,
        "seeds": {"state": state_seed, "network": network_seed},
        "x2a": {"statistic": "partial_r2", "value": x2a["partial_r2"], **x2a},
        "x2b": {
            "statistic": "incremental_r2",
            "value": x2b["incremental_r2"],
            "knots": knots.tolist(),
            **x2b,
        },
        "timing": {
            "started_utc": started,
            "finished_utc": utc_now(),
            "simulation_seconds": simulated - clock,
            "wall_seconds": time.perf_counter() - clock,
            "cpu_seconds": time.process_time() - cpu,
        },
    }


# Provenance, sharded execution and aggregation -----------------------------


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _git(*arguments: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *arguments], cwd=STUDY, capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def host_description() -> dict[str, Any]:
    cpu = platform.processor()
    try:
        if sys.platform == "linux":
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
        elif sys.platform == "darwin":
            cpu = _sysctl_brand() or cpu
    except OSError:
        pass
    return {
        "hostname": platform.node(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "cpu": cpu,
        "logical_cpus": os.cpu_count(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "threads": {name: os.environ.get(name) for name in THREAD_VARIABLES},
    }


def _sysctl_brand() -> str | None:
    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def code_provenance() -> dict[str, Any]:
    status = _git("status", "--porcelain", "--untracked-files=no", "--", ".")
    try:
        frozen = json.loads((STUDY / FREEZE).read_text())["code"]
    except (OSError, KeyError, ValueError):
        frozen = {}
    sources = {path: _sha256(STUDY / path) for path in FROZEN_SOURCES}
    return {
        "commit": _git("rev-parse", "HEAD"),
        "tracked_tree_clean": None if status is None else status == "",
        "module_sha256": _sha256(Path(__file__)),
        "lock_sha256": _sha256(STUDY / "uv.lock"),
        "frozen_sources_sha256": sources,
        "frozen_sources_match_freeze": bool(frozen)
        and all(frozen.get(path) == digest for path, digest in sources.items()),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=1, allow_nan=False)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _unit_path(directory: Path, kind: str, index: int) -> Path:
    return directory / kind / f"{kind}-{index:03d}.json"


@dataclass(frozen=True)
class Analysis:
    """One declared analysis: its unit count, sizes and per-unit computation."""

    kind: str
    total: int
    sizes: dict[str, int]
    compute: Callable[[int], dict[str, Any]]


def x1a_analysis(sizes: X1aSizes = DECLARED_X1A) -> Analysis:
    return Analysis(
        "x1a", len(x1a_cells()), asdict(sizes), lambda index: x1a_cell(index, sizes)
    )


def x2_analysis(sizes: X2Sizes = DECLARED_X2) -> Analysis:
    return Analysis(
        "x2",
        len(x2_conditions()) * sizes.replicates,
        asdict(sizes),
        lambda index: x2_replicate(index, sizes),
    )


def run_shard(
    analysis: Analysis,
    directory: Path,
    *,
    shard: int = 0,
    shards: int = 1,
    only: Sequence[int] | None = None,
) -> list[int]:
    """Compute this shard's missing units (index % shards == shard)."""
    if not 0 <= shard < shards:
        raise ValueError("Require 0 <= shard < shards")
    selected = [
        index
        for index in range(analysis.total)
        if index % shards == shard and (only is None or index in only)
    ]
    provenance = {
        "code": code_provenance(),
        "host": host_description(),
        "shard": shard,
        "shards": shards,
    }
    done = []
    for index in selected:
        path = _unit_path(directory, analysis.kind, index)
        if path.exists():
            if json.loads(path.read_text())["sizes"] != analysis.sizes:
                raise ValueError(f"Existing {path.name} has different sizes")
            continue
        record = analysis.compute(index)
        record["provenance"] = provenance
        write_json(path, record)
        wall = record["timing"]["wall_seconds"]
        print(json.dumps({"kind": analysis.kind, "unit": index, "wall": wall}))
        sys.stdout.flush()
        done.append(index)
    return done


def declaration_digests() -> dict[str, str | None]:
    base = STUDY / DECLARATION
    return {
        "readme_sha256": _sha256(base / "README.md"),
        "declaration_sha256": _sha256(base / "declaration.json"),
    }


def shared_provenance(records: Sequence[dict[str, Any]], key: str) -> list[Any]:
    unique: list[Any] = []
    for record in records:
        if record["provenance"][key] not in unique:
            unique.append(record["provenance"][key])
    return unique


def timing_summary(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
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
        "shards": sorted({r["provenance"]["shards"] for r in records}),
    }


def load_records(directory: Path, kind: str, total: int) -> list[dict[str, Any]]:
    missing = [i for i in range(total) if not _unit_path(directory, kind, i).exists()]
    if missing:
        raise ValueError(f"Missing {kind} units: {missing}")
    return [
        json.loads(_unit_path(directory, kind, i).read_text()) for i in range(total)
    ]


def aggregate_x1a(directory: Path, sizes: X1aSizes = DECLARED_X1A) -> dict[str, Any]:
    records = load_records(directory, "x1a", len(x1a_cells()))
    if any(record["sizes"] != asdict(sizes) for record in records):
        raise ValueError("X1a cells were not all run at the requested sizes")
    above = [r["cell"] for r in records if r["interval_95"][0] > 0.5]
    below = [r["cell"] for r in records if r["interval_95"][1] < 0.5]
    by_block: dict[str, dict[str, Any]] = {}
    for record in records:
        seeds = {k: v for k, v in record["seeds"].items()}
        entry = by_block.setdefault(str(record["cell"]["r"]), seeds)
        if entry != seeds:
            raise ValueError("Cells of one reliability must share their seeds")
    return {
        "schema": "ic-study.v4-exploratory-x1a.v1",
        "label": "exploratory; never promoted to confirmatory evidence",
        "declaration": declaration_digests(),
        "sizes": asdict(sizes),
        "summary": {
            "cells": len(records),
            "interval_excludes_half": len(above) + len(below),
            "above_half": [[c["a"], c["r"]] for c in above],
            "below_half": [[c["a"], c["r"]] for c in below],
        },
        "seeds": {
            "namespace": NAMESPACE,
            "root": ROOT,
            "material": "{namespace}|{root}|x1a|{block}|{phase}|{role}|{index}",
            "digest": "sha256(material)[:8] as big-endian unsigned",
            "by_reliability": by_block,
        },
        "code": shared_provenance(records, "code"),
        "host": shared_provenance(records, "host"),
        "timing": timing_summary(records),
        "cells": [
            {k: v for k, v in record.items() if k != "provenance"} for record in records
        ],
    }


def aggregate_x2(directory: Path, sizes: X2Sizes = DECLARED_X2) -> dict[str, Any]:
    conditions = x2_conditions()
    records = load_records(directory, "x2", len(conditions) * sizes.replicates)
    if any(record["sizes"] != asdict(sizes) for record in records):
        raise ValueError("X2 replicates were not all run at the requested sizes")
    rows = []
    for index, (share, repulsion, steps) in enumerate(conditions):
        group = [r for r in records if r["condition"]["index"] == index]
        summary: dict[str, Any] = {"a": share, "repulsion": repulsion, "steps": steps}
        for key in ("x2a", "x2b"):
            values = np.array([r[key]["value"] for r in group])
            summary[key] = {
                "statistic": group[0][key]["statistic"],
                "mean": float(values.mean()),
                "sd": float(values.std(ddof=1)),
                "min": float(values.min()),
                "max": float(values.max()),
            }
        summary["replicates"] = [
            {k: r[k] for k in ("replicate", "seeds", "observations", "x2a", "x2b")}
            for r in group
        ]
        rows.append(summary)
    return {
        "schema": "ic-study.v4-exploratory-x2.v1",
        "label": "exploratory; never promoted to confirmatory evidence",
        "declaration": declaration_digests(),
        "sizes": asdict(sizes),
        "summary_sd": "sample standard deviation across replicates (ddof=1)",
        "bitwise_equal_to_frozen_influence": all(
            r["bitwise_equal_to_frozen_influence"] for r in records
        ),
        "seeds": {
            "namespace": NAMESPACE,
            "root": ROOT,
            "material": "{namespace}|{root}|x2|0|replicate|{role}|{replicate}",
            "digest": "sha256(material)[:8] as big-endian unsigned",
            "common_across_conditions": True,
        },
        "code": shared_provenance(records, "code"),
        "host": shared_provenance(records, "host"),
        "timing": timing_summary(records),
        "conditions": rows,
    }


def _indices(text: str | None) -> list[int] | None:
    return None if text is None else [int(part) for part in text.split(",")]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="v4 exploratory X1a and X2")
    commands = parser.add_subparsers(dest="command", required=True)
    for kind in ("x1a", "x2"):
        command = commands.add_parser(kind)
        command.add_argument("--out", type=Path, required=True)
        command.add_argument("--shard", type=int, default=0)
        command.add_argument("--shards", type=int, default=1)
        command.add_argument("--only", help="comma-separated unit indices")
        command.add_argument("--size", type=int, default=SIZE)
        if kind == "x1a":
            command.add_argument("--train", type=int, default=X1aSizes.train)
            command.add_argument("--networks", type=int, default=X1aSizes.networks)
            command.add_argument("--resamples", type=int, default=X1aSizes.resamples)
        else:
            command.add_argument("--replicates", type=int, default=X2Sizes.replicates)
    aggregate = commands.add_parser("aggregate")
    aggregate.add_argument("kind", choices=("x1a", "x2"))
    aggregate.add_argument("--out", type=Path, required=True)
    aggregate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "aggregate":
        result = (aggregate_x1a if args.kind == "x1a" else aggregate_x2)(args.out)
        write_json(args.output, result)
        return 0
    analysis = (
        x1a_analysis(X1aSizes(args.size, args.train, args.networks, args.resamples))
        if args.command == "x1a"
        else x2_analysis(X2Sizes(args.size, WAVES, args.replicates))
    )
    run_shard(
        analysis,
        args.out,
        shard=args.shard,
        shards=args.shards,
        only=_indices(args.only),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
