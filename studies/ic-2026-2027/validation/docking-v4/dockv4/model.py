"""Clean-room panel generator for the v4 detection-boundary study.

Written only from the protocol documents listed in ``AMBIGUITIES.md``.
Interpretations of ambiguous text are tagged ``[Qn]`` and logged there.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from statistics import NormalDist

import numpy as np

N_WAVES = 11
RHO = 0.85  # per-step persistence of the social recursion
B_REPULSION = 0.25
N_PERMUTATIONS = 8
RETENTION = 0.89
LATE_ENTRY_WAVE = 5
N_CATEGORIES = 11
HEAP_SHARE = 0.10
FAMILIES = ("social", "A", "B", "C", "D", "E")


# --------------------------------------------------------------------------
# Normal-rank transport R_N
# --------------------------------------------------------------------------
@lru_cache(maxsize=16)
def normal_scores(n: int) -> np.ndarray:
    """Normal quantiles at (j+0.5)/n, rescaled to mean 0 and variance 1. [Q3]"""
    inv = NormalDist().inv_cdf
    q = np.array([inv((j + 0.5) / n) for j in range(n)])
    q = (q - q.mean()) / q.std()
    q.setflags(write=False)
    return q


def rank_transport(u: np.ndarray) -> np.ndarray:
    """R_N: preserve ranks, assign standardised normal scores."""
    out = np.empty_like(u, dtype=float)
    out[np.argsort(u, kind="stable")] = normal_scores(u.shape[0])
    return out


# --------------------------------------------------------------------------
# Geometry and mask
# --------------------------------------------------------------------------
def entry_waves(n: int) -> np.ndarray:
    """Two-person households; 2/3 of persons enter at t=0, 1/3 at t=5. [Q1,Q2]"""
    if n % 6:
        raise ValueError("N must be divisible by six")
    households = n // 2
    early = 2 * households // 3
    hh_entry = np.where(np.arange(households) < early, 0, LATE_ENTRY_WAVE)
    return np.repeat(hh_entry, 2)


def panel_mask(n: int, rng: np.random.Generator) -> np.ndarray:
    """(n, 11) bool; household-level annual retention 0.89, permanent exit. [Q2]"""
    households = n // 2
    entry = entry_waves(n)[::2]
    survive = rng.random((households, N_WAVES)) < RETENTION
    mask = np.zeros((households, N_WAVES), dtype=bool)
    for h in range(households):
        e = entry[h]
        mask[h, e] = True
        for t in range(e + 1, N_WAVES):
            if not survive[h, t]:
                break
            mask[h, t] = True
    return np.repeat(mask, 2, axis=0)


# --------------------------------------------------------------------------
# Latent processes
# --------------------------------------------------------------------------
def network(n: int, rng: np.random.Generator) -> np.ndarray:
    """(n, 8): person i hears from perm_k[i]; self-loops/repeats allowed. [Q5]"""
    return np.stack([rng.permutation(n) for _ in range(N_PERMUTATIONS)], axis=1)


def social_drift(z: np.ndarray, nbr: np.ndarray, b: float) -> np.ndarray:
    g = z[nbr] - z[:, None]
    f = np.where(np.abs(g) <= 1.0, g, -b * g)
    big_d = f.mean(axis=1)
    sd = big_d.std()  # [Q6] population SD
    if not sd > 0:
        raise FloatingPointError("SD(D)=0 with a>0")
    return (big_d - big_d.mean()) / sd


def simulate_social(
    n: int,
    a: float,
    state: np.random.Generator,
    net: np.random.Generator,
    *,
    b: float = B_REPULSION,
    steps: int = 1,
) -> np.ndarray:
    """Bounded confidence with repulsion; returns latent z of shape (n, 11)."""
    z = rank_transport(state.standard_normal(n))
    nbr = network(n, net) if a > 0 else None  # [Q7]
    out = np.empty((n, N_WAVES))
    out[:, 0] = z
    c_innov = np.sqrt(1.0 - RHO**2)
    for t in range(1, N_WAVES):
        for _ in range(steps):
            eps = state.standard_normal(n)
            if a > 0:
                d = social_drift(z, nbr, b)
                u = RHO * z + c_innov * (np.sqrt(a) * d + np.sqrt(1 - a) * eps)
            else:
                u = RHO * z + c_innov * eps
            z = rank_transport(u)
        out[:, t] = z
    return out


def simulate_x(
    n: int, phi: float, state: np.random.Generator, *, steps: int = 1
) -> np.ndarray:
    """X_phi: the a=0 recursion with persistence phi (D2)."""
    x = rank_transport(state.standard_normal(n))
    out = np.empty((n, N_WAVES))
    out[:, 0] = x
    c_innov = np.sqrt(1.0 - phi**2)
    for t in range(1, N_WAVES):
        for _ in range(steps):
            x = rank_transport(phi * x + c_innov * state.standard_normal(n))
        out[:, t] = x
    return out


def simulate_b(n, phi, lam, state, null_state, *, steps=1):
    x = simulate_x(n, phi, state, steps=steps)
    trait = null_state.standard_normal(n)  # not rank-transported (D2)
    if lam == 0:
        return x
    mix = np.sqrt(lam) * trait[:, None] + np.sqrt(1 - lam) * x
    return np.column_stack([rank_transport(mix[:, t]) for t in range(N_WAVES)])


def simulate_e(n, phi, pi, state, null_state, *, steps=1):
    x = simulate_x(n, phi, state, steps=steps)
    stayer = null_state.random(n) < pi
    if pi == 0:
        return x
    mix = np.where(stayer[:, None], x[:, :1], x)
    return np.column_stack([rank_transport(mix[:, t]) for t in range(N_WAVES)])


def simulate_d(n, rho0, gamma, state, *, steps=1):
    z = rank_transport(state.standard_normal(n))
    out = np.empty((n, N_WAVES))
    out[:, 0] = z
    for t in range(1, N_WAVES):
        for _ in range(steps):
            rho_z = rho0 + gamma * (1 - rho0) * (1 - np.exp(-(z**2) / 2))
            eps = state.standard_normal(n)
            z = rank_transport(rho_z * z + np.sqrt(1 - rho_z**2) * eps)
        out[:, t] = z
    return out


# --------------------------------------------------------------------------
# Observation channel
# --------------------------------------------------------------------------
_S_NORM = np.sqrt(1 + 4 / np.sqrt(2) + 4 / np.sqrt(3))  # sqrt(E[s(z)^2]), z~N(0,1)


def c_error_scale(z: np.ndarray) -> np.ndarray:
    """s(z)=1+2exp(-z^2/2), normalised so E[s^2]=1 under N(0,1). [Q10]"""
    return (1 + 2 * np.exp(-(z**2) / 2)) / _S_NORM


def measured(
    z: np.ndarray,
    r: float,
    error: np.random.Generator,
    *,
    c: float = 0.0,
    hetero: bool = False,
) -> np.ndarray:
    """w = sqrt(r) z + sqrt(1-r) e; optional persistent style c; C scale."""
    n = z.shape[0]
    if c > 0:
        u = error.standard_normal(n)
        v = error.standard_normal(z.shape)
        e = np.sqrt(c) * u[:, None] + np.sqrt(1 - c) * v
    else:
        e = error.standard_normal(z.shape)
    if hetero:
        e = c_error_scale(z) * e
    return np.sqrt(r) * z + np.sqrt(1 - r) * e


def c_marginal() -> np.ndarray:
    p = np.full(N_CATEGORIES, 0.9 / N_CATEGORIES)
    p[5] += 0.1
    return p


def discretise(
    w: np.ndarray,
    mask: np.ndarray,
    *,
    marginal: np.ndarray | None = None,
    tiebreak: np.random.Generator | None = None,
) -> np.ndarray:
    """Per wave, map respondent ranks to 0..10 via quantiles (j+0.5)/n_t. [Q8,Q9]

    Returns float (n, 11) with NaN where unobserved.
    """
    cum = np.cumsum(c_marginal() if marginal is None else marginal)
    cum[-1] = 1.0
    y = np.full(w.shape, np.nan)
    for t in range(N_WAVES):
        idx = np.flatnonzero(mask[:, t])
        vals = w[idx, t]
        if tiebreak is not None:
            order = np.lexsort((tiebreak.random(idx.size), vals))
        else:
            order = np.argsort(vals, kind="stable")
        q = (np.arange(idx.size) + 0.5) / idx.size
        if marginal is None:
            cat = np.floor(q * N_CATEGORIES)
        else:
            cat = np.searchsorted(cum, q, side="right")
        y[idx[order], t] = np.minimum(cat, N_CATEGORIES - 1)
    return y


# --------------------------------------------------------------------------
# One panel
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Cell:
    family: str
    r: float
    a: float = 0.0  # social only
    phi: float = 0.85  # A/B/C/E persistence, D rho0
    eta: float = 0.0  # lambda (B), pi (E), gamma (D)
    c_comparison: bool = False  # use C marginal for either arm
    steps: int = 1
    b: float = B_REPULSION
    c_style: float = 0.0


def latent(cell: Cell, n: int, streams) -> np.ndarray:
    f = cell.family
    if f == "social":
        return simulate_social(
            n, cell.a, streams.state, streams.network, b=cell.b, steps=cell.steps
        )
    if f in ("A", "C"):
        return simulate_x(n, cell.phi, streams.state, steps=cell.steps)
    if f == "B":
        return simulate_b(
            n, cell.phi, cell.eta, streams.state, streams.null_state, steps=cell.steps
        )
    if f == "E":
        return simulate_e(
            n, cell.phi, cell.eta, streams.state, streams.null_state, steps=cell.steps
        )
    if f == "D":
        return simulate_d(n, cell.phi, cell.eta, streams.state, steps=cell.steps)
    raise ValueError(f)


def panel(cell: Cell, n: int, streams) -> dict[str, np.ndarray]:
    """Return latent z, mask and observed ordinal y for one panel."""
    z = latent(cell, n, streams)
    mask = panel_mask(n, streams.mask)
    is_c = cell.family == "C"
    w = measured(z, cell.r, streams.error, c=cell.c_style, hetero=is_c)
    tiebreak = None
    if is_c:  # 10% heaping at w=0 among respondents, independent tie-break [Q9]
        heap = streams.heap.random(w.shape) < HEAP_SHARE
        w = np.where(heap, 0.0, w)
        tiebreak = streams.heap
    marginal = c_marginal() if (is_c or cell.c_comparison) else None
    y = discretise(w, mask, marginal=marginal, tiebreak=tiebreak)
    return {"z": z, "mask": mask, "y": y}
