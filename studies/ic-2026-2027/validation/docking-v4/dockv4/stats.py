"""Per-panel features, frozen LDA and AUC (clean-room)."""

from __future__ import annotations

import numpy as np

from .model import N_WAVES

LDA_FEATURE_LAGS = (3, 4, 5)
SHRINK = 0.2  # covariance 0.8 S + 0.2 I
TARGET_AUC = 0.70


def pooled_lag_corr(y: np.ndarray, k: int) -> float:
    """L_k: Pearson over all valid (t, t+k) pairs pooled within a panel. [Q11]"""
    a = y[:, : N_WAVES - k].ravel()
    b = y[:, k:].ravel()
    ok = ~(np.isnan(a) | np.isnan(b))
    a, b = a[ok], b[ok]
    a = a - a.mean()
    b = b - b.mean()
    return float((a @ b) / np.sqrt((a @ a) * (b @ b)))


def lag_features(
    y: np.ndarray, lags: tuple[int, ...] = tuple(range(1, 11))
) -> np.ndarray:
    return np.array([pooled_lag_corr(y, k) for k in lags])


def wave_corr(y: np.ndarray) -> np.ndarray:
    """11x11 pairwise-complete Pearson matrix between waves (NaN if <3 pairs)."""
    out = np.full((N_WAVES, N_WAVES), np.nan)
    for s in range(N_WAVES):
        for t in range(s, N_WAVES):
            ok = ~(np.isnan(y[:, s]) | np.isnan(y[:, t]))
            if ok.sum() < 3:
                continue
            out[s, t] = out[t, s] = np.corrcoef(y[ok, s], y[ok, t])[0, 1]
    return out


def panel_summaries(y: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "n_obs": (~np.isnan(y)).sum(axis=0).astype(float),
        "mean": np.nanmean(y, axis=0),
        "var": np.nanvar(y, axis=0, ddof=1),
        "lag": lag_features(y),
        "wave_corr": wave_corr(y)[np.triu_indices(N_WAVES, 1)],
    }


# --------------------------------------------------------------------------
# Discriminator
# --------------------------------------------------------------------------
def lda_fit(x_social: np.ndarray, x_null: np.ndarray) -> dict[str, np.ndarray]:
    """Standardise on pooled training data; within-class S shrunk to 0.8S+0.2I.

    Direction points towards the social class (higher score = reorganisation).
    [Q12]
    """
    x = np.vstack([x_social, x_null])
    mu = x.mean(axis=0)
    sd = x.std(axis=0, ddof=1)
    zs = (x_social - mu) / sd
    zn = (x_null - mu) / sd
    m1, m0 = zs.mean(axis=0), zn.mean(axis=0)
    resid = np.vstack([zs - m1, zn - m0])
    s = resid.T @ resid / (resid.shape[0] - 2)
    cov = (1 - SHRINK) * s + SHRINK * np.eye(s.shape[0])
    w = np.linalg.solve(cov, m1 - m0)
    return {"mu": mu, "sd": sd, "w": w}


def lda_score(model: dict[str, np.ndarray], x: np.ndarray) -> np.ndarray:
    return ((x - model["mu"]) / model["sd"]) @ model["w"]


def auc(score_pos: np.ndarray, score_neg: np.ndarray) -> float:
    """P(pos > neg) + 0.5 P(tie), over all pairs (Mann-Whitney)."""
    s = np.concatenate([score_pos, score_neg])
    order = np.argsort(s, kind="mergesort")
    ranks = np.empty(s.size)
    sorted_s = s[order]
    i = 0
    while i < s.size:  # average ranks for ties
        j = i
        while j + 1 < s.size and sorted_s[j + 1] == sorted_s[i]:
            j += 1
        ranks[order[i : j + 1]] = 0.5 * (i + j) + 1
        i = j + 1
    n1, n0 = score_pos.size, score_neg.size
    return float((ranks[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def detected(auc_value: float) -> bool:
    return auc_value >= TARGET_AUC
