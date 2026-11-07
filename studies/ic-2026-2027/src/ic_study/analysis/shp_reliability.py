"""Local, aggregate-only quasi-simplex analysis of SHP P$$P04."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import stat
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize
from scipy.stats import multivariate_normal, norm

YEARS = tuple(range(1999, 2010))
DEFAULT_DATA_DIR = Path("/Users/davi/.local/state/research-workbench/restricted/shp")
SUCCESSOR = "shp-reliability-successor-1"
STARTS_VARIANCE_FLOOR = 1e-4
STARTS_PERSISTENCE_LIMIT = 0.99
STARTS_FAILURES = (
    "non-convergence",
    "observed information not positive definite",
    "variance below 1e-4 times mean observed variance",
    "abs(phi) above 0.99",
    "r_t outside (0, 1)",
)
STARTS_NUMERICAL_ERROR = "numerical error before a solution was reached"
STARTS_VARIANCES = (
    "trait_variance",
    "initial_state_variance",
    "innovation_variance",
    "error_variance",
)
# Fixed before any SHP data access. STARTS likelihoods are flat near variance
# boundaries (Lüdtke, Robitzsch and Wagner 2018), so the gradient is central and
# the tolerances are tighter than the primary fit's; neither depends on the data.
_STARTS_MAXITER = 1000
_STARTS_FTOL = 1e-13
_STARTS_GTOL = 1e-8
# Log-variance box relative to the mean observed variance: a variance pinned at
# the lower end (3e-7 of it) always meets the declared 1e-4 failure floor.
_STARTS_RELATIVE_LOG_VARIANCE_BOUNDS = (-15.0, 5.0)
_STARTS_PERSISTENCE_BOUNDS = (-2.65, 2.65)  # atanh scale; tanh(2.65) > 0.99
_STARTS_START_PERSISTENCE = 0.5


def _read_csv(path: Path, variable: str) -> dict[str, float]:
    values: dict[str, float] = {}
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        columns = {name.lower(): name for name in reader.fieldnames or []}
        if "idpers" not in columns or variable.lower() not in columns:
            raise ValueError("Person file lacks idpers or the requested P$$P04 column")
        for row in reader:
            identifier = row[columns["idpers"]]
            if identifier in values:
                raise ValueError("Duplicate idpers within an annual person file")
            values[identifier] = _parse_answer(row[columns[variable.lower()]])
    return values


def _read_dta(path: Path, variable: str) -> dict[str, float]:
    import pyreadstat

    _, metadata = pyreadstat.read_dta(
        str(path), metadataonly=True, output_format="dict"
    )
    columns = {name.lower(): name for name in metadata.column_names}
    if "idpers" not in columns or variable.lower() not in columns:
        raise ValueError("Person file lacks idpers or the requested P$$P04 column")
    frame, _ = pyreadstat.read_dta(
        str(path),
        usecols=[columns["idpers"], columns[variable.lower()]],
        apply_value_formats=False,
        output_format="dict",
    )
    values: dict[str, float] = {}
    for identifier, answer in zip(
        frame[columns["idpers"]], frame[columns[variable.lower()]], strict=True
    ):
        key = str(identifier)
        if key in values:
            raise ValueError("Duplicate idpers within an annual person file")
        values[key] = _parse_answer(answer)
    return values


def _parse_answer(raw: object) -> float:
    try:
        value = float(str(raw))
    except (TypeError, ValueError):
        return math.nan
    if not math.isfinite(value) or value < 0:
        return math.nan
    if value > 10 or not value.is_integer():
        raise ValueError("P$$P04 contains a value outside the integer 0-10 scale")
    return value


def load_person_files(
    directory: Path = DEFAULT_DATA_DIR, years: tuple[int, ...] = YEARS
) -> tuple[NDArray[np.float64], tuple[int, ...]]:
    """Read only idpers and PyyP04 from annual files; no records leave memory."""
    if not directory.is_dir():
        raise ValueError("Restricted SHP directory is missing or empty")
    if stat.S_IMODE(directory.stat().st_mode) != 0o700:
        raise ValueError("Restricted SHP directory must have mode 0700")
    files = [p for p in directory.iterdir() if p.is_file()]
    if not files:
        raise ValueError("Restricted SHP directory is empty; add annual person files")
    by_year: list[dict[str, float]] = []
    for year in years:
        prefix = f"shp{year % 100:02d}_p_user"
        matches = [
            p
            for p in files
            if p.stem.lower() == prefix and p.suffix.lower() in {".csv", ".dta"}
        ]
        if len(matches) != 1 or matches[0].is_symlink():
            raise ValueError(
                f"Expected exactly one safe SHP{year % 100:02d}_P_USER.csv or .dta"
            )
        variable = f"P{year % 100:02d}P04"
        by_year.append(
            _read_csv(matches[0], variable)
            if matches[0].suffix.lower() == ".csv"
            else _read_dta(matches[0], variable)
        )
    identifiers = sorted(set().union(*(wave.keys() for wave in by_year)))
    if not identifiers:
        raise ValueError("Annual SHP person files contain no rows")
    panel = np.full((len(identifiers), len(years)), np.nan)
    for column, wave in enumerate(by_year):
        panel[:, column] = [
            wave.get(identifier, math.nan) for identifier in identifiers
        ]
    return panel, years


def _patterns(
    panel: NDArray[np.float64],
) -> list[tuple[NDArray[np.intp], NDArray[np.float64]]]:
    masks = np.isfinite(panel)
    groups = []
    for mask in np.unique(masks, axis=0):
        if not mask.any():
            continue
        columns = np.flatnonzero(mask)
        groups.append((columns, panel[np.all(masks == mask, axis=1)][:, columns]))
    return groups


def _gaussian_nll(
    mean: NDArray[np.float64],
    covariance: NDArray[np.float64],
    groups: list[tuple[NDArray[np.intp], NDArray[np.float64]]],
) -> float:
    total = 0.0
    for columns, values in groups:
        block = covariance[np.ix_(columns, columns)]
        try:
            cholesky = np.linalg.cholesky(block)
            residual = np.linalg.solve(cholesky, (values - mean[columns]).T)
        except np.linalg.LinAlgError:
            return 1e30
        total += 0.5 * (
            len(values)
            * (
                len(columns) * math.log(2 * math.pi)
                + 2 * np.log(np.diag(cholesky)).sum()
            )
            + np.square(residual).sum()
        )
    return float(total)


def _simplex_covariance(
    parameters: NDArray[np.float64], width: int
) -> NDArray[np.float64]:
    variance, innovation, error = np.exp(parameters[:3])
    persistence = math.tanh(float(parameters[3]))
    latent = np.zeros((width, width))
    latent[0, 0] = variance
    for wave in range(1, width):
        latent[wave, :wave] = persistence * latent[wave - 1, :wave]
        latent[:wave, wave] = latent[wave, :wave]
        latent[wave, wave] = persistence**2 * latent[wave - 1, wave - 1] + innovation
    return cast(NDArray[np.float64], latent + np.eye(width) * error)


def _numerical_hessian(
    function: Any, point: NDArray[np.float64]
) -> NDArray[np.float64]:
    size = len(point)
    step = 1e-3
    hessian = np.empty((size, size))
    baseline = function(point)
    for i in range(size):
        up = point.copy()
        down = point.copy()
        up[i] += step
        down[i] -= step
        hessian[i, i] = (function(up) - 2 * baseline + function(down)) / step**2
        for j in range(i):
            a, b, c, d = (point.copy() for _ in range(4))
            a[i] += step
            a[j] += step
            b[i] += step
            b[j] -= step
            c[i] -= step
            c[j] += step
            d[i] -= step
            d[j] -= step
            hessian[i, j] = hessian[j, i] = (
                function(a) - function(b) - function(c) + function(d)
            ) / (4 * step**2)
    return hessian


def _simplex_fit(panel: NDArray[np.float64]) -> dict[str, Any]:
    width = panel.shape[1]
    groups = _patterns(panel)
    means = np.nanmean(panel, axis=0)
    observed_variance = float(np.nanvar(panel))
    initial = np.r_[
        np.log(
            [observed_variance * 0.7, observed_variance * 0.3, observed_variance * 0.2]
        ),
        np.arctanh(0.7),
        means,
    ]

    def objective(parameters: NDArray[np.float64]) -> float:
        return _gaussian_nll(
            parameters[4:], _simplex_covariance(parameters, width), groups
        )

    fit = minimize(
        objective,
        initial,
        method="L-BFGS-B",
        bounds=[(-10, 5)] * 3 + [(0.01, 2.65)] + [(None, None)] * width,
        options={"maxiter": 500, "ftol": 1e-10},
    )
    if not fit.success:
        raise ValueError("Multi-wave quasi-simplex optimizer did not converge")
    covariance = _simplex_covariance(fit.x, width)
    error = math.exp(float(fit.x[2]))
    reliabilities = 1 - error / np.diag(covariance)
    hessian = _numerical_hessian(objective, fit.x)
    if np.linalg.eigvalsh(hessian).min() <= 0:
        raise ValueError("Multi-wave information matrix is not positive definite")
    parameter_covariance = np.linalg.inv(hessian)
    errors = []
    for wave in range(width):
        gradient = np.zeros(len(fit.x))
        for index in range(4):
            upper, lower = fit.x.copy(), fit.x.copy()
            upper[index] += 1e-5
            lower[index] -= 1e-5
            first = _simplex_covariance(upper, width)
            second = _simplex_covariance(lower, width)
            gradient[index] = (
                (1 - math.exp(float(upper[2])) / first[wave, wave])
                - (1 - math.exp(float(lower[2])) / second[wave, wave])
            ) / 2e-5
        errors.append(
            math.sqrt(max(0.0, float(gradient @ parameter_covariance @ gradient)))
        )
    complete = panel[np.isfinite(panel).all(axis=1)]
    residual_correlation = None
    if len(complete) >= 30:
        observed = np.corrcoef(complete, rowvar=False)
        predicted = covariance / np.sqrt(
            np.outer(np.diag(covariance), np.diag(covariance))
        )
        residual_correlation = float(np.max(np.abs(observed - predicted)))
    return {
        "reliability": [float(value) for value in reliabilities],
        "standard_error": errors,
        "persistence": math.tanh(float(fit.x[3])),
        "error_variance": error,
        "log_likelihood": -float(fit.fun),
        "aic": 2 * len(fit.x) + 2 * float(fit.fun),
        "bic": math.log(len(panel)) * len(fit.x) + 2 * float(fit.fun),
        "max_complete_case_correlation_residual": residual_correlation,
        "converged": bool(fit.success),
        "at_parameter_bound": bool(
            any(
                abs(float(fit.x[i]) - boundary) < 1e-3
                for i, bounds in enumerate([(-10, 5)] * 3 + [(0.01, 2.65)])
                for boundary in bounds
            )
        ),
    }


def _starts_covariance(
    parameters: NDArray[np.float64], width: int
) -> NDArray[np.float64]:
    """Trait + AR(1) state + error: the quasi-simplex matrix plus a constant trait."""
    return _simplex_covariance(parameters[1:5], width) + math.exp(float(parameters[0]))


def _starts_reliability(
    parameters: NDArray[np.float64], width: int
) -> NDArray[np.float64]:
    covariance = _starts_covariance(parameters, width)
    return 1 - math.exp(float(parameters[3])) / np.diag(covariance)


def _starts_failure_reasons(
    *,
    converged: bool,
    information_positive: bool | None,
    variances: dict[str, float],
    floor: float,
    persistence: float,
    reliability: NDArray[np.float64],
) -> list[str]:
    """Declared failure rules of successor 1; NaN fails every comparison."""
    checks = (
        not converged,
        information_positive is False,
        any(not value >= floor for value in variances.values()),
        not abs(persistence) <= STARTS_PERSISTENCE_LIMIT,
        not bool(np.all((reliability > 0) & (reliability < 1))),
    )
    return [
        reason for reason, failed in zip(STARTS_FAILURES, checks, strict=True) if failed
    ]


def _json_safe(value: Any) -> Any:
    """Non-finite diagnostics become null so the strict JSON writer never fails."""
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _starts_optimizer() -> dict[str, Any]:
    return {
        "method": "L-BFGS-B",
        "jac": "3-point",
        "options": {
            "maxiter": _STARTS_MAXITER,
            "ftol": _STARTS_FTOL,
            "gtol": _STARTS_GTOL,
        },
        "log_variance_bounds": "log(mean observed variance) + "
        f"{list(_STARTS_RELATIVE_LOG_VARIANCE_BOUNDS)}",
        "atanh_persistence_bounds": list(_STARTS_PERSISTENCE_BOUNDS),
        "start": {
            "trait, initial state and error variances": "mean observed variance / 3",
            "innovation variance": "(1 - persistence^2) * mean observed variance / 3",
            "persistence": _STARTS_START_PERSISTENCE,
            "means": "observed wave means",
        },
    }


def _starts_fit(panel: NDArray[np.float64], years: tuple[int, ...]) -> dict[str, Any]:
    width = panel.shape[1]
    anchor = width // 2
    groups = _patterns(panel)
    means = np.nanmean(panel, axis=0)
    mean_variance = float(np.mean(np.nanvar(panel, axis=0)))
    floor = STARTS_VARIANCE_FLOOR * mean_variance
    third = mean_variance / 3
    initial = np.r_[
        np.log([third, third, third * (1 - _STARTS_START_PERSISTENCE**2), third]),
        math.atanh(_STARTS_START_PERSISTENCE),
        means,
    ]
    scale = math.log(mean_variance)
    variance_bounds = tuple(scale + b for b in _STARTS_RELATIVE_LOG_VARIANCE_BOUNDS)
    bounds = [variance_bounds] * 4 + [_STARTS_PERSISTENCE_BOUNDS]

    def objective(parameters: NDArray[np.float64]) -> float:
        return _gaussian_nll(
            parameters[5:], _starts_covariance(parameters, width), groups
        )

    fit = minimize(
        objective,
        initial,
        method="L-BFGS-B",
        jac="3-point",
        bounds=bounds + [(None, None)] * width,
        options={
            "maxiter": _STARTS_MAXITER,
            "ftol": _STARTS_FTOL,
            "gtol": _STARTS_GTOL,
        },
    )
    variances = dict(
        zip(STARTS_VARIANCES, (math.exp(float(v)) for v in fit.x[:4]), strict=True)
    )
    persistence = math.tanh(float(fit.x[4]))
    covariance = _starts_covariance(fit.x, width)
    reliability = _starts_reliability(fit.x, width)
    state = np.diag(covariance) - variances["trait_variance"]
    state -= variances["error_variance"]
    trait_share = variances["trait_variance"] / (
        variances["trait_variance"] + float(state[anchor])
    )
    information: float | None = None
    parameter_covariance = None
    if fit.success:
        hessian = _numerical_hessian(objective, fit.x)
        if np.all(np.isfinite(hessian)):
            information = float(np.linalg.eigvalsh(hessian).min())
            if information > 0:
                parameter_covariance = np.linalg.inv(hessian)
    reasons = _starts_failure_reasons(
        converged=bool(fit.success),
        information_positive=None
        if not fit.success
        else parameter_covariance is not None,
        variances=variances,
        floor=floor,
        persistence=persistence,
        reliability=reliability,
    )
    diagnostics = {
        "converged": bool(fit.success),
        "optimizer_message": str(fit.message),
        "iterations": int(fit.nit),
        "at_parameter_bound": bool(
            any(
                abs(float(fit.x[i]) - boundary) < 1e-3
                for i, limits in enumerate(bounds)
                for boundary in limits
            )
        ),
        "min_information_eigenvalue": information,
        "mean_observed_variance": mean_variance,
        "variance_floor": floor,
        "variances_below_floor": [
            name for name, value in variances.items() if not value >= floor
        ],
    }
    solution = {
        **variances,
        "persistence": persistence,
        "state_variance": [float(v) for v in state],
        "reliability": [float(v) for v in reliability],
        "trait_share_of_latent_variance": {
            "year": years[anchor],
            "value": trait_share,
        },
        "log_likelihood": -float(fit.fun),
    }
    if reasons or parameter_covariance is None:
        return cast(
            dict[str, Any],
            _json_safe(
                {
                    "status": "failed",
                    "reasons": reasons,
                    "diagnostics": diagnostics,
                    "solution_at_termination": solution,
                    "optimizer": _starts_optimizer(),
                }
            ),
        )
    jacobian = np.zeros((width, len(fit.x)))
    for index in range(5):
        upper, lower = fit.x.copy(), fit.x.copy()
        upper[index] += 1e-5
        lower[index] -= 1e-5
        jacobian[:, index] = (
            _starts_reliability(upper, width) - _starts_reliability(lower, width)
        ) / 2e-5
    errors = np.sqrt(
        np.maximum(
            0.0, np.einsum("ij,jk,ik->i", jacobian, parameter_covariance, jacobian)
        )
    )
    estimate, error = float(reliability[anchor]), float(errors[anchor])
    complete = panel[np.isfinite(panel).all(axis=1)]
    residual_correlation = None
    if len(complete) >= 30:
        observed = np.corrcoef(complete, rowvar=False)
        predicted = covariance / np.sqrt(
            np.outer(np.diag(covariance), np.diag(covariance))
        )
        residual_correlation = float(np.max(np.abs(observed - predicted)))
    return {
        "status": "admissible",
        "anchor": {
            "year": years[anchor],
            "estimate": estimate,
            "standard_error": error,
            "wald_95_interval": [
                float(max(0, estimate - 1.96 * error)),
                float(min(1, estimate + 1.96 * error)),
            ],
        },
        **solution,
        "standard_error": [float(v) for v in errors],
        "aic": 2 * len(fit.x) + 2 * float(fit.fun),
        "bic": math.log(len(panel)) * len(fit.x) + 2 * float(fit.fun),
        "max_complete_case_correlation_residual": residual_correlation,
        "diagnostics": diagnostics,
        "optimizer": _starts_optimizer(),
    }


def starts_sensitivity(
    panel: NDArray[np.float64], years: tuple[int, ...]
) -> dict[str, Any]:
    """Successor 1, Addition 1: trait-state-error FIML; a failure is a record.

    ``Y_it = mu_t + T_i + S_it + e_it`` with ``S_it = phi S_i,t-1 + eta_it``, on
    the primary fit's sample, scale and missing-data treatment. The reliability
    ``r_t = 1 - var_e / var(Y_t)`` is reported at the primary anchor wave. Any
    declared failure returns ``status="failed"`` with its reasons and the
    unclipped solution at termination, never an estimate.
    """
    try:
        return _starts_fit(panel, years)
    except (ValueError, ArithmeticError) as error:
        return {
            "status": "failed",
            "reasons": [STARTS_NUMERICAL_ERROR],
            "diagnostics": {"error": f"{type(error).__name__}: {error}"},
            "optimizer": _starts_optimizer(),
        }


def wave_2004_description(
    panel: NDArray[np.float64], years: tuple[int, ...], model: dict[str, Any]
) -> dict[str, Any]:
    """Successor 1, Addition 3: descriptive outputs that never replace the anchor."""
    if not {2003, 2004, 2005} <= set(years):
        return {"status": "not applicable: 2003-2005 are not all analysed years"}
    primary = {
        str(year): {
            "estimate": float(model["reliability"][years.index(year)]),
            "standard_error": float(model["standard_error"][years.index(year)]),
        }
        for year in (2003, 2004, 2005)
    }
    start = years.index(2004)
    observed = np.isfinite(panel)
    first = np.where(observed.any(axis=1), np.argmax(observed, axis=1), -1)
    group = panel[first == start][:, start:]
    edge: dict[str, Any] = {
        "label": "edge estimate: first wave of a quasi-simplex over "
        f"{years[start]}-{years[-1]} among respondents whose first valid answer "
        "is in 2004 (refreshment-entry proxy)",
        "years": list(years[start:]),
        "n_people": len(group),
        "n_per_wave": {
            str(year): int(observed_count)
            for year, observed_count in zip(
                years[start:], np.isfinite(group).sum(axis=0), strict=True
            )
        },
    }
    if len(years) - start < 3 or min(edge["n_per_wave"].values()) < 30:
        edge["status"] = "insufficient N"
    else:
        try:
            fit = _simplex_fit(group)
        except ValueError as error:
            edge |= {"status": "failed", "reason": str(error)}
        else:
            edge |= {
                "status": "estimated",
                "year": years[start],
                "estimate": fit["reliability"][0],
                "standard_error": fit["standard_error"][0],
                "fit": fit,
            }
    return {
        "status": "descriptive",
        "primary_fit": primary,
        "first_valid_answer_2004": edge,
    }


def _triplet_fit(
    panel: NDArray[np.float64], years: tuple[int, int, int]
) -> dict[str, Any]:
    groups = _patterns(panel)
    means = np.nanmean(panel, axis=0)
    complete = panel[np.isfinite(panel).all(axis=1)]
    if len(complete) < 30:
        raise ValueError("Too few complete respondents in a three-wave window")
    sample_covariance = np.cov(complete.T)
    initial = np.r_[np.linalg.cholesky(sample_covariance)[np.tril_indices(3)], means]

    def covariance(parameters: NDArray[np.float64]) -> NDArray[np.float64]:
        lower = np.zeros((3, 3))
        lower[np.tril_indices(3)] = parameters[:6]
        np.fill_diagonal(lower, np.exp(np.diag(lower)))
        return lower @ lower.T

    initial[:6][[0, 2, 5]] = np.log(initial[:6][[0, 2, 5]])

    def objective(parameters: NDArray[np.float64]) -> float:
        return _gaussian_nll(parameters[6:], covariance(parameters), groups)

    fit = minimize(
        objective, initial, method="BFGS", options={"maxiter": 350, "gtol": 1e-4}
    )
    if not fit.success and np.linalg.norm(np.asarray(fit.jac, dtype=float)) > 0.02:
        raise ValueError("Three-wave saturated FIML optimizer did not converge")
    matrix = covariance(fit.x)
    c01, c12, c02 = matrix[0, 1], matrix[1, 2], matrix[0, 2]
    if min(c01, c12, c02) <= 0:
        raise ValueError(
            "Three-wave covariance signs violate quasi-simplex assumptions"
        )
    latent_middle = c01 * c12 / c02
    error_variance = matrix[1, 1] - latent_middle
    heise = latent_middle / matrix[1, 1]
    wiley = 1 - error_variance / np.diag(matrix)
    if error_variance <= 0 or np.any((wiley <= 0) | (wiley >= 1)) or heise >= 1:
        raise ValueError("Three-wave solution has inadmissible error variance")
    hessian = _numerical_hessian(objective, fit.x)
    if np.linalg.eigvalsh(hessian).min() <= 0:
        raise ValueError("Three-wave information matrix is not positive definite")
    inverse = np.linalg.inv(hessian)
    gradient = np.zeros(len(fit.x))
    for index in range(6):
        upper, lower = fit.x.copy(), fit.x.copy()
        upper[index] += 1e-5
        lower[index] -= 1e-5

        def reliability(parameters: NDArray[np.float64]) -> float:
            value = covariance(parameters)
            return float(value[0, 1] * value[1, 2] / value[0, 2] / value[1, 1])

        gradient[index] = (reliability(upper) - reliability(lower)) / 2e-5
    se = math.sqrt(max(0.0, float(gradient @ inverse @ gradient)))
    return {
        "years": list(years),
        "heise_reliability": float(heise),
        "heise_standard_error": se,
        "wiley_reliability_by_wave": [float(value) for value in wiley],
        "wiley_middle_standard_error": se,
        "log_likelihood": -float(fit.fun),
        "aic": 2 * len(fit.x) + 2 * float(fit.fun),
        "bic": math.log(len(panel)) * len(fit.x) + 2 * float(fit.fun),
        "n_complete": int(np.isfinite(panel).all(axis=1).sum()),
    }


def _polychoric_pair(left: NDArray[np.float64], right: NDArray[np.float64]) -> float:
    valid = np.isfinite(left) & np.isfinite(right)
    counts = np.zeros((11, 11), dtype=int)
    np.add.at(counts, (left[valid].astype(int), right[valid].astype(int)), 1)
    if counts.sum() < 30:
        raise ValueError("Too few pairs for polychoric sensitivity")
    left_cumulative = np.r_[0, np.cumsum(counts.sum(axis=1))] / counts.sum()
    right_cumulative = np.r_[0, np.cumsum(counts.sum(axis=0))] / counts.sum()
    left_thresholds = norm.ppf(left_cumulative)
    right_thresholds = norm.ppf(right_cumulative)
    upper_left = np.repeat(left_thresholds[1:], 11)
    upper_right = np.tile(right_thresholds[1:], 11)
    lower_left = np.repeat(left_thresholds[:-1], 11)
    lower_right = np.tile(right_thresholds[:-1], 11)

    def log_likelihood(rho: float) -> float:
        distribution = multivariate_normal(cov=[[1, rho], [rho, 1]])

        def cdf(x: NDArray[np.float64], y: NDArray[np.float64]) -> NDArray[np.float64]:
            return np.asarray(distribution.cdf(np.column_stack((x, y))))

        probabilities = (
            cdf(upper_left, upper_right)
            - cdf(lower_left, upper_right)
            - cdf(upper_left, lower_right)
            + cdf(lower_left, lower_right)
        )
        occupied = counts.ravel() > 0
        return -float(
            np.sum(
                counts.ravel()[occupied]
                * np.log(np.maximum(probabilities[occupied], 1e-12))
            )
        )

    from scipy.optimize import minimize_scalar

    result = minimize_scalar(log_likelihood, bounds=(0.001, 0.999), method="bounded")
    if not result.success:
        raise ValueError("Polychoric pair fit did not converge")
    return float(result.x)


def _ordinal_sensitivity(
    panel: NDArray[np.float64], years: tuple[int, ...]
) -> list[dict[str, Any]]:
    correlations = {
        (i, j): _polychoric_pair(panel[:, i], panel[:, j])
        for i in range(len(years))
        for j in range(i + 1, len(years))
        if j - i <= 2
    }
    estimates = []
    for i in range(len(years) - 2):
        estimate = (
            correlations[i, i + 1] * correlations[i + 1, i + 2] / correlations[i, i + 2]
        )
        estimates.append(
            {
                "years": list(years[i : i + 3]),
                "polychoric_heise_reliability": float(estimate),
                "admissible": bool(0 < estimate < 1),
            }
        )
    return estimates


def analyze_panel(
    panel: NDArray[np.float64],
    years: tuple[int, ...] = YEARS,
    *,
    include_sensitivity: bool = False,
    include_successor: bool = False,
) -> dict[str, Any]:
    """Aggregate SHP report; ``include_successor`` adds successor 1's sections."""
    if panel.ndim != 2 or panel.shape[1] != len(years) or len(years) < 3:
        raise ValueError("Panel must have at least three annual waves")
    if np.any(np.isfinite(panel) & ((panel < 0) | (panel > 10))):
        raise ValueError("Panel contains a response outside the 0-10 scale")
    if min(np.isfinite(panel).sum(axis=0)) < 30:
        raise ValueError("At least 30 valid responses are required in every wave")
    model = _simplex_fit(panel)
    triplets = [
        _triplet_fit(panel[:, i : i + 3], (years[i], years[i + 1], years[i + 2]))
        for i in range(len(years) - 2)
    ]
    estimates = np.asarray(model["reliability"])
    errors = np.asarray(model["standard_error"])
    middle = len(years) // 2
    result = {
        "analysis": "SHP P$$P04 quasi-simplex; aggregate only",
        "years": list(years),
        "n_per_wave": {
            str(year): int(np.isfinite(panel[:, i]).sum())
            for i, year in enumerate(years)
        },
        "n_people_with_any_response": int(np.isfinite(panel).any(axis=1).sum()),
        "n_people_complete": int(np.isfinite(panel).all(axis=1).sum()),
        "missing_per_wave": {
            str(year): int((~np.isfinite(panel[:, i])).sum())
            for i, year in enumerate(years)
        },
        "heaping_at_five_per_wave": {
            str(year): float(np.mean(panel[np.isfinite(panel[:, i]), i] == 5))
            for i, year in enumerate(years)
        },
        "endpoints_per_wave": {
            str(year): float(
                np.mean(np.isin(panel[np.isfinite(panel[:, i]), i], [0, 10]))
            )
            for i, year in enumerate(years)
        },
        "multiwave": model,
        "triplets": triplets,
        "anchor": {
            "year": years[middle],
            "estimate": float(estimates[middle]),
            "standard_error": float(errors[middle]),
            "wald_95_interval": [
                float(max(0, estimates[middle] - 1.96 * errors[middle])),
                float(min(1, estimates[middle] + 1.96 * errors[middle])),
            ],
        },
        "sensitivity_envelope": [
            float(min(t["heise_reliability"] for t in triplets)),
            float(max(t["heise_reliability"] for t in triplets)),
        ],
    }
    if include_sensitivity:
        sensitivity: dict[str, Any] = {
            "polychoric_triplets": _ordinal_sensitivity(panel, years)
        }
        complete = panel[np.isfinite(panel).all(axis=1)]
        if len(complete) >= 30:
            sensitivity["complete_case_multiwave"] = _simplex_fit(complete)
            sensitivity["complete_case_n"] = len(complete)
        else:
            sensitivity["complete_case_status"] = "insufficient N"
        ever_observed = np.isfinite(panel).any(axis=1)
        first_wave = np.argmax(np.isfinite(panel), axis=1)
        early_mask = (
            ever_observed & (first_wave <= max(0, years.index(2004) - 1))
            if 2004 in years
            else ever_observed
        )
        early = panel[early_mask]
        if min(np.isfinite(early).sum(axis=0)) >= 30:
            sensitivity["observed_before_2004_multiwave"] = _simplex_fit(early)
            sensitivity["observed_before_2004_n"] = len(early)
        else:
            sensitivity["observed_before_2004_status"] = "insufficient N"
        result["sensitivity"] = sensitivity
    if include_successor:
        result["successor_1"] = {
            "specification": SUCCESSOR,
            "starts_sensitivity": starts_sensitivity(panel, years),
            "wave_2004_description": wave_2004_description(panel, years, model),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Local SHP aggregate reliability analysis"
    )
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        panel, years = load_person_files(args.data_dir)
        result = analyze_panel(
            panel, years, include_sensitivity=True, include_successor=True
        )
        if args.output.exists() or args.output.is_symlink():
            raise ValueError("Output already exists; use a new aggregate report path")
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
            stream.write("\n")
    except (OSError, ValueError) as error:
        parser.exit(2, f"SHP aggregate analysis stopped: {error}\n")
    except Exception:
        parser.exit(
            2,
            "SHP aggregate analysis stopped; input or fit error (details withheld).\n",
        )
    print("Aggregate SHP reliability report written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
