"""Seed plan, profile matching and one train/test AUC replication (clean-room)."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from .model import Cell, panel
from .seeds import Streams
from .stats import LDA_FEATURE_LAGS, auc, lda_fit, lda_score, pooled_lag_corr

EVENTS_PER_NETWORK = 2


def lags_of(cell: Cell, n: int, streams: Streams, lags) -> np.ndarray:
    y = panel(cell, n, streams)["y"]
    return np.array([pooled_lag_corr(y, k) for k in lags])


# --------------------------------------------------------------------------
# Matching: CRN pairs, index 2i+1, own network per realisation (v1 seeds, D3)
# --------------------------------------------------------------------------
class Matcher:
    def __init__(self, target: Cell, family: str, n: int, m: int, ns: str, block=0):
        self.target, self.family, self.n, self.m = target, family, n, m
        self.ns, self.block = ns, block
        self.evaluations = 0
        self._cache: dict[tuple[float, float], np.ndarray] = {}
        self.target_lags = np.array(
            [lags_of(target, n, self._streams(i), (1, 2)) for i in range(m)]
        )

    def _streams(self, i: int) -> Streams:
        return Streams(self.ns, self.block, "match", 2 * i + 1, i)

    def differences(self, phi: float, eta: float) -> np.ndarray:
        key = (round(phi, 12), round(eta, 12))
        if key not in self._cache:
            self.evaluations += 1
            null = Cell(
                self.family,
                self.target.r,
                phi=phi,
                eta=eta,
                c_comparison=self.target.c_comparison,
                steps=self.target.steps,
            )
            lags = np.array(
                [lags_of(null, self.n, self._streams(i), (1, 2)) for i in range(self.m)]
            )
            self._cache[key] = lags - self.target_lags
        return self._cache[key]

    def g(self, phi: float, eta: float) -> np.ndarray:
        return self.differences(phi, eta).mean(axis=0)

    def se(self, phi: float, eta: float) -> np.ndarray:
        d = self.differences(phi, eta)
        return d.std(axis=0, ddof=1) / np.sqrt(self.m)

    def tol(self, phi: float, eta: float, k: int) -> float:
        return min(5e-5, max(1e-6, 0.25 * self.se(phi, eta)[k]))


def _illinois(f, lo, hi, flo, fhi, done, max_iter=40):
    """Illinois false position on a sign-changing bracket."""
    side = 0
    x = lo
    for _ in range(max_iter):
        x = (lo * fhi - hi * flo) / (fhi - flo)
        fx = f(x)
        if done(x, fx):
            return x
        if np.sign(fx) == np.sign(flo):
            lo, flo = x, fx
            if side == -1:
                fhi /= 2
            side = -1
        else:
            hi, fhi = x, fx
            if side == 1:
                flo /= 2
            side = 1
    return x


def solve_phi(mt: Matcher, eta: float) -> float | None:
    """L1 root in phi on [0, 0.999] at fixed eta; None if no bracket."""
    lo, hi = 0.0, 0.999
    flo, fhi = mt.g(lo, eta)[0], mt.g(hi, eta)[0]
    if flo * fhi > 0:
        return None
    return _illinois(
        lambda p: mt.g(p, eta)[0],
        lo,
        hi,
        flo,
        fhi,
        lambda p, fp: abs(fp) <= mt.tol(p, eta, 0),
    )


def match(mt: Matcher, eta_hi: float = 0.8) -> dict:
    """Profile solver: L1 in phi, then L2 in eta (two-parameter families)."""
    if mt.family in ("A", "C"):
        phi = solve_phi(mt, 0.0)
        return _result(mt, phi, 0.0, "interior" if phi is not None else "no-L1-root")

    def profile(eta):
        phi = solve_phi(mt, eta)
        return phi, (np.nan if phi is None else mt.g(phi, eta)[1])

    phi0, g0 = profile(0.0)
    if phi0 is None:
        return _result(mt, None, 0.0, "no-L1-root")
    if g0 >= 0:
        return _result(mt, phi0, 0.0, "boundary")
    phi1, g1 = profile(eta_hi)
    if phi1 is None or g1 < 0:
        return _result(mt, phi1, eta_hi, "family-limit-upper")
    state = {}

    def f(eta):
        phi, g2 = profile(eta)
        state[eta] = phi
        return g2

    eta = _illinois(
        f, 0.0, eta_hi, g0, g1, lambda e, fe: abs(fe) <= mt.tol(state[e], e, 1)
    )
    return _result(mt, state[eta], eta, "interior")


def _result(mt: Matcher, phi, eta, status) -> dict:
    out = {"status": status, "phi": phi, "eta": eta, "evaluations": mt.evaluations}
    if phi is not None:
        out["residual"] = mt.g(phi, eta).tolist()
        out["se"] = mt.se(phi, eta).tolist()
    return out


# --------------------------------------------------------------------------
# Train / test sets: index 2i+class, network floor(index/(2*events)), class 1=social
# --------------------------------------------------------------------------
def feature_set(
    cell: Cell,
    cls: int,
    n: int,
    networks: int,
    ns: str,
    block: int,
    phase: str,
    lags=LDA_FEATURE_LAGS,
) -> np.ndarray:
    rows = []
    for i in range(networks * EVENTS_PER_NETWORK):
        index = 2 * i + cls
        net = index // (2 * EVENTS_PER_NETWORK)
        rows.append(lags_of(cell, n, Streams(ns, block, phase, index, net), lags))
    return np.array(rows)


def auc_replication(
    social: Cell,
    null: Cell,
    n: int,
    train_networks: int,
    test_networks: int,
    ns: str,
    block: int,
) -> dict:
    tr1 = feature_set(social, 1, n, train_networks, ns, block, "train")
    tr0 = feature_set(null, 0, n, train_networks, ns, block, "train")
    te1 = feature_set(social, 1, n, test_networks, ns, block, "check")
    te0 = feature_set(null, 0, n, test_networks, ns, block, "check")
    model = lda_fit(tr1, tr0)
    return {
        "auc": auc(lda_score(model, te1), lda_score(model, te0)),
        "features": (tr1, tr0, te1, te0),
    }


def null_cell(social: Cell, family: str, fit: dict) -> Cell:
    return replace(social, family=family, a=0.0, phi=fit["phi"], eta=fit["eta"])
