"""D7 criteria; scientific estimates never appear in returned public summaries."""

from __future__ import annotations

from math import ceil, comb
from typing import TypedDict

import numpy as np
from numpy.typing import NDArray

from ic_study.models.anchored_panel import Floats


class Dispersion(TypedDict):
    complete: bool
    failures: int
    denominator: int
    cell_failure_counts: list[int]
    successful_pair_counts: list[int]
    failure_allowance_met: bool
    cell_ratios: list[float]
    cell_lower: list[float]
    cell_upper: list[float]
    pooled_ratio: float
    pooled_lower: float
    pooled_upper: float
    loo_tail_counts: list[int]
    loo_z_mean: list[float]


def dispersion(
    estimates: Floats,
    se: Floats,
    success: NDArray[np.bool_],
    *,
    seed: int,
    bootstraps: int = 399,
) -> Dispersion:
    if (
        estimates.shape != se.shape
        or estimates.shape != success.shape
        or estimates.ndim != 2
        or estimates.shape[1] != 100
    ):
        raise ValueError("Require 100 pipelines per declared cell")
    failed = ~success | ~np.isfinite(estimates) | ~np.isfinite(se) | (se < 0)
    result: Dispersion = {
        "complete": not bool(np.any(failed)),
        "failures": int(failed.sum()),
        "denominator": estimates.size,
        "cell_failure_counts": failed.sum(1).tolist(),
        "successful_pair_counts": [],
        "failure_allowance_met": bool(
            np.all(failed.sum(1) <= 5) and failed.sum() <= ceil(0.02 * estimates.size)
        ),
        "cell_ratios": [],
        "cell_lower": [],
        "cell_upper": [],
        "pooled_ratio": 0,
        "pooled_lower": 0,
        "pooled_upper": 0,
        "loo_tail_counts": [],
        "loo_z_mean": [],
    }
    probability = np.clip(estimates, 1 / 4000, 1 - 1 / 4000)
    logits = np.log(probability / (1 - probability))
    variance = (np.maximum(se, 1 / 4000) / (probability * (1 - probability))) ** 2
    pair_ok = ~(failed[:, ::2] | failed[:, 1::2])
    pair_counts = pair_ok.sum(1)
    result["successful_pair_counts"] = pair_counts.tolist()
    if np.any(pair_counts < 2):
        return result
    rng = np.random.default_rng(seed)
    ratios, means, numerators, denominators, tails, z_means = [], [], [], [], [], []
    # Retain the pre-review bootstrap stream when every cell has 50 pairs.
    indices = (
        rng.integers(50, size=(bootstraps, len(estimates), 50))
        if np.all(pair_counts == 50)
        else None
    )
    for cell in range(len(estimates)):
        pairs = (logits[cell, ::2] - logits[cell, 1::2])[pair_ok[cell]]
        pair_variance = (variance[cell, ::2] + variance[cell, 1::2])[pair_ok[cell]]
        means.append(float(pair_variance.mean()))
        ratios.append(float(pairs.var(ddof=1) / pair_variance.mean()))
        sample = (
            indices[:, cell]
            if indices is not None
            else rng.integers(len(pairs), size=(bootstraps, len(pairs)))
        )
        numerators.append(pairs[sample].var(1, ddof=1))
        denominators.append(pair_variance[sample].mean(1))
        values = logits[cell, ~failed[cell]]
        variances = variance[cell, ~failed[cell]]
        loo = (values.sum() - values) / (len(values) - 1)
        loo_variance = (variances.sum() - variances) / (len(values) - 1) ** 2
        z = (values - loo) / np.sqrt(variances + loo_variance)
        tails.append(int(np.sum(np.abs(z) > 2.7729)))
        z_means.append(float(z.mean()))
    numerator, denominator = np.stack(numerators, 1), np.stack(denominators, 1)
    boot = numerator / denominator
    pooled = np.average(ratios, weights=means)
    pooled_boot = numerator.sum(1) / denominator.sum(1)
    result.update(
        {
            "cell_ratios": ratios,
            "cell_lower": np.quantile(boot, 0.025, axis=0).tolist(),
            "cell_upper": np.quantile(boot, 0.975, axis=0).tolist(),
            "pooled_ratio": float(pooled),
            "pooled_lower": float(np.quantile(pooled_boot, 0.025)),
            "pooled_upper": float(np.quantile(pooled_boot, 0.975)),
            "loo_tail_counts": tails,
            "loo_z_mean": z_means,
        }
    )
    return result


def refit_ratio(
    local: Floats, refits: Floats, *, seed: int, bootstraps: int = 399
) -> dict[str, object]:
    if local.shape != (2000,) or len(refits) not in {40, 100}:
        raise ValueError("Require 2000 local draws and 40 or 100 full refits")
    planned = len(refits)
    failures = int(np.sum(~np.isfinite(refits)))
    allowance = 3 if planned == 100 else 2
    refits = refits[np.isfinite(refits)]
    if not np.all(np.isfinite(local)) or len(refits) < 2 or refits.var() == 0:
        return {"pass": False, "failure_count": failures, "denominator": planned}
    rng = np.random.default_rng(seed)
    numerator = local[rng.integers(len(local), size=(bootstraps, len(local)))].var(
        1, ddof=1
    )
    denominator = refits[rng.integers(len(refits), size=(bootstraps, len(refits)))].var(
        1, ddof=1
    )
    ratios = numerator / np.maximum(denominator, 1e-30)
    lower, upper = np.quantile(ratios, [0.05, 0.95])
    centered = (refits - refits.mean()) / refits.std(ddof=1)
    return {
        "pass": bool(failures <= allowance and upper >= 0.8 and lower <= 2.0),
        "ratio": float(local.var(ddof=1) / refits.var(ddof=1)),
        "lower": float(lower),
        "upper": float(upper),
        "denominator": planned,
        "failure_count": failures,
        "tails": int(np.sum(np.abs(centered) > 2.7729)),
    }


class Thresholds(TypedDict):
    cell_lower: float
    cell_upper: float
    pooled_lower: float
    pooled_upper: float


def dispersion_pass(report: Dispersion, thresholds: Thresholds) -> bool:
    return bool(
        report["failure_allowance_met"]
        and bool(report["cell_upper"])
        and min(report["cell_upper"]) >= thresholds["cell_lower"]
        and max(report["cell_lower"]) <= thresholds["cell_upper"]
        and report["pooled_upper"] >= thresholds["pooled_lower"]
        and report["pooled_lower"] <= thresholds["pooled_upper"]
    )


def fd_stability(variances: Floats, success: NDArray[np.bool_]) -> dict[str, object]:
    """One median of paired FD variance ratios per cell; gaps are excluded."""
    if variances.shape != (*success.shape, 2):
        raise ValueError("Require both FD steps per planned pipeline")
    medians = []
    for cell, ok in zip(variances, success, strict=True):
        values = cell[ok]
        ratios = np.divide(
            values[:, 1],
            values[:, 0],
            out=np.full(len(values), np.inf),
            where=values[:, 0] > 0,
        )
        ratios[(values[:, 0] == 0) & (values[:, 1] == 0)] = 1
        medians.append(float(np.median(ratios)) if len(ratios) else None)
    return {
        "fd_ratio_median_by_cell": medians,
        "fd_stable": all(v is not None and 0.8 <= v <= 1.25 for v in medians),
    }


def failure_allowance_probability(rates: list[float]) -> float:
    """Exact independent-binomial probability of <=5/cell and 2% pooled."""
    pooled_limit = ceil(0.02 * 100 * len(rates))
    distribution = np.array([1.0])
    for rate in rates:
        if not 0 <= rate <= 1:
            raise ValueError("Gap rate must be a probability")
        mass = np.array(
            [comb(100, k) * rate**k * (1 - rate) ** (100 - k) for k in range(6)]
        )
        distribution = np.convolve(distribution, mass)[: pooled_limit + 1]
    return float(distribution.sum())
