"""Successor profile matching and local propagation, separate from frozen refits."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray

from ic_study.models.anchored_panel import Floats

ACCEPTED = {"anchor-exact", "interior", "boundary"}


@dataclass(frozen=True)
class ProfileFit:
    parameters: Floats
    differences: Floats
    residual: Floats
    se: Floats
    tolerance: Floats
    evaluations: int
    status: str
    fitted_moments: int

    @property
    def success(self) -> bool:
        return self.status in ACCEPTED


class _SolverError(Exception):
    pass


def profile_match(
    target: Floats,
    evaluate: Callable[[float, float], Floats],
    *,
    identity: bool = False,
    fixed_eta: float | None = None,
    budget: int = 96,
) -> ProfileFit:
    """Null minus target, L1 first. Lower-bound KKT is checked on the profile.

    Monotonicity is checked at every sampled profile point, including a fresh
    local probe at the lower face. It is not a theorem about unsampled points.
    """
    if target.ndim != 2 or target.shape[1] != 2 or len(target) < 2:
        raise ValueError("Require paired two-moment rows")
    if not np.all(np.isfinite(target)) or not 1 <= budget <= 96:
        raise ValueError("Invalid target or evaluation budget")
    if fixed_eta is not None and not 0 <= fixed_eta <= 0.8:
        raise ValueError("Invalid fixed second parameter")
    cache: dict[tuple[float, float], ProfileFit] = {}
    calls = 0
    last = ProfileFit(
        np.array([0.85, 0.0]),
        np.zeros_like(target),
        np.zeros(2),
        np.zeros(2),
        np.zeros(2),
        0,
        "numerical-limit",
        1 if fixed_eta is not None else 2,
    )

    def at(phi: float, eta: float) -> ProfileFit:
        nonlocal calls, last
        key = (phi, eta)
        if key in cache:
            return cache[key]
        if calls == budget:
            raise _SolverError("budget")
        calls += 1
        values = evaluate(phi, eta)
        if values.shape != target.shape or not np.all(np.isfinite(values)):
            raise _SolverError("numerical-limit")
        differences = values - target
        se = differences.std(0, ddof=1) / np.sqrt(len(target))
        last = ProfileFit(
            np.array(key),
            differences,
            differences.mean(0),
            se,
            np.minimum(5e-5, np.maximum(1e-6, 0.25 * se)),
            calls,
            "interior",
            1 if fixed_eta is not None else 2,
        )
        cache[key] = last
        return last

    def good(fit: ProfileFit, k: int) -> bool:
        return bool(abs(fit.residual[k]) <= fit.tolerance[k])

    jacobian: Floats | None = None
    prediction = np.array([0.85, 0.0])
    stepped: set[tuple[float, float]] = set()

    def inner(eta: float, *, inexact: bool = False, refine: bool = False) -> ProfileFit:
        candidates = [v for v in cache.values() if v.parameters[1] == eta]
        near = min(cache.values(), key=lambda v: abs(v.parameters[1] - eta))
        phi = float(prediction[0])
        if jacobian is not None and abs(jacobian[0, 0]) > 1e-10:
            phi = float(
                near.parameters[0]
                - (near.residual[0] + jacobian[0, 1] * (eta - near.parameters[1]))
                / jacobian[0, 0]
            )
        current = at(float(np.clip(phi, 0, 0.999)), eta)
        if 1e-12 < current.parameters[0] < 0.999 - 1e-12 and not np.array_equal(
            current.parameters, near.parameters
        ):
            stepped.add(tuple(current.parameters))
        candidates.append(current)
        lo = max(
            (v for v in candidates if v.residual[0] < 0),
            key=lambda v: v.parameters[0],
            default=None,
        )
        hi = min(
            (v for v in candidates if v.residual[0] > 0),
            key=lambda v: v.parameters[0],
            default=None,
        )
        local_slope = jacobian[0, 0] if jacobian is not None else 0.0
        for _ in range(budget):
            tolerance = current.tolerance[0]
            if refine:
                tolerance = min(1e-6, 0.1 * tolerance)
            if inexact:
                tolerance = max(tolerance, min(5e-5, 0.02 * abs(current.residual[1])))
            if abs(current.residual[0]) <= tolerance:
                if (
                    tuple(current.parameters) not in stepped
                    and 1e-12 < current.parameters[0] < 0.999 - 1e-12
                ):
                    trial = float(current.parameters[0])
                    trial += 0.001 if trial < 0.998 else -0.001
                    current = at(trial, eta)
                    stepped.add(tuple(current.parameters))
                    if current.residual[0] < 0:
                        lo = current
                    else:
                        hi = current
                    continue
                return current
            slope = local_slope
            if lo is not None and hi is not None:
                width = hi.parameters[0] - lo.parameters[0]
                if width < 1e-12:
                    raise _SolverError("numerical-limit")
                slope = (hi.residual[0] - lo.residual[0]) / width
            trial = (
                current.parameters[0] - current.residual[0] / slope
                if slope > 1e-10
                else np.nan
            )
            left = 0.0 if lo is None else float(lo.parameters[0])
            right = 0.999 if hi is None else float(hi.parameters[0])
            if not np.isfinite(trial) or not left < trial < right:
                if lo is None:
                    trial = left
                elif hi is None:
                    trial = right
                else:
                    trial = (left + right) / 2
            # Force progress for discrete maps and repeated secant endpoints.
            if (float(trial), eta) in cache:
                trial = (left + right) / 2
            previous = current
            current = at(float(trial), eta)
            distance = current.parameters[0] - previous.parameters[0]
            if abs(distance) > 1e-12:
                local_slope = (current.residual[0] - previous.residual[0]) / distance
            stepped.add(tuple(current.parameters))
            if current.residual[0] < 0:
                lo = current
            else:
                hi = current
            if (
                current.parameters[0] in {0.0, 0.999}
                and not good(current, 0)
                and (
                    (current.parameters[0] == 0 and current.residual[0] > 0)
                    or (current.parameters[0] == 0.999 and current.residual[0] < 0)
                )
            ):
                raise _SolverError("no-L1-root")
            if np.array_equal(previous.parameters, current.parameters):
                raise _SolverError("numerical-limit")
        raise _SolverError("budget")

    profiles: dict[float, ProfileFit] = {}

    def profile(
        eta: float, *, inexact: bool = False, refine: bool = False
    ) -> ProfileFit:
        result = inner(eta, inexact=inexact, refine=refine)
        if inexact and abs(result.residual[1]) < 10 * max(result.tolerance):
            result = inner(eta)
        profiles[eta] = result
        ordered = sorted(profiles.items())
        for (_, left), (_, right) in pairwise(ordered):
            if right.residual[1] < left.residual[1] - max(
                left.tolerance[1], right.tolerance[1]
            ):
                left = inner(float(left.parameters[1]), refine=True)
                right = inner(float(right.parameters[1]), refine=True)
                profiles[float(left.parameters[1])] = left
                profiles[float(right.parameters[1])] = right
                if right.residual[1] < left.residual[1] - max(
                    left.tolerance[1], right.tolerance[1]
                ):
                    raise _SolverError("non-monotone-profile")
        return profiles[eta]

    def finish(fit: ProfileFit, status: str) -> ProfileFit:
        if status == "interior" and tuple(fit.parameters) not in stepped:
            status = "boundary"
        return ProfileFit(
            fit.parameters,
            fit.differences,
            fit.residual,
            fit.se,
            fit.tolerance,
            calls,
            status,
            fit.fitted_moments,
        )

    try:
        if identity and (fixed_eta is None or fixed_eta == 0):
            anchor = at(0.85, 0.0)
            if not np.any(anchor.differences):
                return finish(anchor, "anchor-exact")
        anchor_eta = 0.0 if fixed_eta is None else fixed_eta
        anchor = at(0.85, anchor_eta)
        phi_probe = at(0.86, anchor_eta)
        if fixed_eta is None:
            eta_probe = at(0.85, 0.01)
            jacobian = np.column_stack(
                (
                    (phi_probe.residual - anchor.residual) / 0.01,
                    (eta_probe.residual - anchor.residual) / 0.01,
                )
            )
            if np.linalg.cond(jacobian) < 1e10:
                prediction = np.clip(
                    anchor.parameters - np.linalg.solve(jacobian, anchor.residual),
                    [0, 0],
                    [0.999, 0.8],
                )
        else:
            jacobian = np.column_stack(
                ((phi_probe.residual - anchor.residual) / 0.01, np.zeros(2))
            )
        if fixed_eta is not None:
            result = inner(fixed_eta)
            return finish(result, "interior")
        try:
            lower = profile(0.0)
        except _SolverError as exc:
            if str(exc) != "no-L1-root" or at(0.999, 0).residual[0] >= 0:
                raise
            face_lo, face_hi = at(0.999, 0), at(0.999, 0.8)
            if face_hi.residual[0] < -face_hi.tolerance[0]:
                raise _SolverError("no-L1-root") from exc
            lower = face_hi
            iteration = 0
            while not good(lower, 0):
                lo_eta, hi_eta = face_lo.parameters[1], face_hi.parameters[1]
                denom = face_hi.residual[0] - face_lo.residual[0]
                trial = (lo_eta + hi_eta) / 2
                if denom and iteration % 4 != 3:
                    secant = hi_eta - face_hi.residual[0] * (hi_eta - lo_eta) / denom
                    if lo_eta + 1e-12 < secant < hi_eta - 1e-12:
                        trial = secant
                if hi_eta - lo_eta < 1e-12:
                    raise _SolverError("numerical-limit") from exc
                lower = at(0.999, float(trial))
                stepped.add(tuple(lower.parameters))
                if lower.residual[0] < 0:
                    face_lo = lower
                else:
                    face_hi = lower
                iteration += 1
            profiles[float(lower.parameters[1])] = lower
            if good(lower, 1):
                return finish(lower, "interior")
            if lower.residual[1] > 0:
                return finish(lower, "family-limit-lower")
        eta = min(0.8, float(lower.parameters[1]) + 0.01)
        if eta == lower.parameters[1]:
            return finish(lower, "family-limit-upper")
        try:
            local = profile(eta)
        except _SolverError as exc:
            if str(exc) == "no-L1-root" and good(lower, 1):
                return finish(lower, "interior")
            raise
        if local.residual[1] <= lower.residual[1] + 1e-12:
            lower = profile(float(lower.parameters[1]), refine=True)
            local = profile(eta, refine=True)
            if local.residual[1] <= lower.residual[1] + 1e-12:
                raise _SolverError("ill-conditioned")
        if lower.residual[1] >= -lower.tolerance[1]:
            return finish(lower, "boundary")
        upper = local
        while upper.residual[1] < -upper.tolerance[1]:
            lower = upper
            if eta == 0.8:
                return finish(upper, "family-limit-upper")
            next_eta = min(0.8, max(eta * 2, float(prediction[1])))
            try:
                upper = profile(next_eta, inexact=True)
            except _SolverError as exc:
                if str(exc) != "no-L1-root":
                    raise
                # Locate the end of the feasible L1 profile without clipping phi.
                hi_eta = next_eta
                while hi_eta - eta > 1e-6:
                    mid = (hi_eta + eta) / 2
                    try:
                        candidate = profile(mid)
                    except _SolverError as inner_exc:
                        if str(inner_exc) != "no-L1-root":
                            raise
                        hi_eta = mid
                        continue
                    if candidate.residual[1] >= -candidate.tolerance[1]:
                        upper = candidate
                        break
                    eta, lower = mid, candidate
                else:
                    return finish(lower, "family-limit-upper")
                break
            eta = next_eta
        if good(upper, 1):
            upper = profile(float(upper.parameters[1]))
            if good(upper, 1):
                return finish(upper, "interior")
        lower_weight = upper_weight = 1.0
        previous_side = 0
        for iteration in range(budget):
            lo_eta, hi_eta = lower.parameters[1], upper.parameters[1]
            denominator = (
                upper_weight * upper.residual[1] - lower_weight * lower.residual[1]
            )
            trial_eta = (lo_eta + hi_eta) / 2
            if denominator and iteration % 4 != 3:
                secant = (
                    hi_eta
                    - upper_weight * upper.residual[1] * (hi_eta - lo_eta) / denominator
                )
                if lo_eta + 1e-12 < secant < hi_eta - 1e-12:
                    trial_eta = secant
            if hi_eta - lo_eta < 1e-12:
                raise _SolverError("numerical-limit")
            candidate = profile(float(trial_eta), inexact=True)
            if good(candidate, 1):
                candidate = profile(float(trial_eta))
                if good(candidate, 1):
                    return finish(candidate, "interior")
            if candidate.residual[1] < 0:
                lower = candidate
                lower_weight = 1.0
                upper_weight = upper_weight / 2 if previous_side == -1 else 1.0
                previous_side = -1
            else:
                upper = candidate
                upper_weight = 1.0
                lower_weight = lower_weight / 2 if previous_side == 1 else 1.0
                previous_side = 1
        raise _SolverError("budget")
    except _SolverError as exc:
        return finish(last, str(exc))


@dataclass(frozen=True)
class Validation:
    passed: bool
    residual: Floats
    se: Floats
    z: Floats
    equivalence: Floats
    equivalence_passed: bool
    amplification: float | None


def validate_fit(differences: Floats, moments: int, fit_se: Floats) -> Validation:
    if differences.ndim != 2 or len(differences) != 2048 or moments not in {1, 2}:
        raise ValueError("Validation requires 2048 fresh coupled pairs")
    residual = differences.mean(0)
    se = differences.std(0, ddof=1) / np.sqrt(len(differences))
    if (
        fit_se.shape != residual.shape
        or np.any(fit_se < 0)
        or not np.all(np.isfinite(fit_se))
    ):
        raise ValueError("Require finite nonnegative fitting standard errors")
    total_se = np.hypot(fit_se, se)
    z = np.divide(
        residual, total_se, out=np.where(residual == 0, 0.0, np.inf), where=total_se > 0
    )
    equivalence = np.abs(residual) + 2.2414 * se
    return Validation(
        bool(
            np.all(np.isfinite(differences))
            and np.all(np.abs(residual[:moments]) <= 4 * total_se[:moments])
        ),
        residual,
        se,
        z,
        equivalence,
        bool(np.all(equivalence[:moments] <= 0.0003)),
        None,
    )


def project_shift(
    point: Floats,
    jacobian: Floats,
    residual: Floats,
    *,
    inherited_eta_shift: float | None = None,
) -> tuple[Floats, bool]:
    """Box projection with L1 re-solved after fixing eta (not least squares)."""
    if (
        point.shape != (2,)
        or jacobian.shape != (2, 2)
        or residual.shape != (2,)
        or not np.all(np.isfinite(jacobian))
        or abs(jacobian[0, 0]) < 1e-10
    ):
        raise ValueError("ill-conditioned local profile")
    if inherited_eta_shift is None:
        slope = jacobian[1, 1] - jacobian[1, 0] * jacobian[0, 1] / jacobian[0, 0]
        if slope <= 1e-10:
            raise ValueError("ill-conditioned local profile")
        eta_shift = (
            -(residual[1] - jacobian[1, 0] * residual[0] / jacobian[0, 0]) / slope
        )
    else:
        eta_shift = inherited_eta_shift
    eta = float(np.clip(point[1] + eta_shift, 0, 0.8))
    delta_eta = eta - point[1]
    phi_shift = -(residual[0] + jacobian[0, 1] * delta_eta) / jacobian[0, 0]
    phi = float(np.clip(point[0] + phi_shift, 0, 0.999))
    projected = eta != point[1] + eta_shift or phi != point[0] + phi_shift
    return np.array([phi, eta]) - point, projected


@dataclass(frozen=True)
class NuisanceInput:
    parameters: Floats
    differences: Floats
    jacobian: Floats
    null_train: Floats
    social_train: Floats
    null_reference: Floats
    social_reference: Floats
    mean_derivative: Floats


@dataclass(frozen=True)
class NuisanceResult:
    aucs: Floats
    centered: Floats
    shifts: Floats
    variance: float
    mean_shift: float
    mcse: float
    projected_fraction: float


def anchor_nuisance(draws: int = 2000) -> NuisanceResult:
    return NuisanceResult(
        np.full(draws, 0.5), np.zeros(draws), np.zeros((draws, 2)), 0, 0, 0, 0
    )


def nuisance_draws(
    data: NuisanceInput,
    *,
    seed: int,
    draws: int = 2000,
    inherited_eta: Floats | None = None,
) -> NuisanceResult:
    from ic_study.analysis.detection_boundary import auc
    from ic_study.analysis.redesign import fit_discriminant

    n0, n1 = len(data.null_train), len(data.social_train)
    if min(n0, n1) < 4 or n0 % 2 or n1 % 2 or draws < 2:
        raise ValueError("Require two events per training network")
    if data.mean_derivative.shape != (2, data.null_train.shape[1]):
        raise ValueError("Require a Jacobian of mean features from matching draws")
    if inherited_eta is not None and inherited_eta.shape != (draws,):
        raise ValueError("Control and observed draws must align")
    match_rng, null_rng, social_rng = [
        np.random.default_rng(child) for child in np.random.SeedSequence(seed).spawn(3)
    ]
    labels = np.repeat([0, 1], [n0, n1])
    baseline = fit_discriminant(
        np.concatenate([data.null_train, data.social_train]), labels
    )
    auc0 = auc(
        baseline.score(data.null_reference), baseline.score(data.social_reference)
    )
    values, shifts = np.empty(draws), np.empty((draws, 2))
    projected = 0
    for b in range(draws):
        uniforms = match_rng.random(4096)
        indices_match = np.floor(
            uniforms[: len(data.differences)] * len(data.differences)
        ).astype(int)
        residual = data.differences[indices_match].mean(0)
        shifts[b], hit = project_shift(
            data.parameters,
            data.jacobian,
            residual,
            inherited_eta_shift=None
            if inherited_eta is None
            else float(inherited_eta[b]),
        )
        projected += int(hit)
        indices = []
        for n, generator in ((n0, null_rng), (n1, social_rng)):
            networks = generator.integers(n // 2, size=n // 2)
            indices.append((2 * networks[:, None] + np.arange(2)).ravel())
        mean_shift = shifts[b] @ data.mean_derivative
        train = data.null_train + mean_shift
        reference = data.null_reference + mean_shift
        model = fit_discriminant(
            np.concatenate([train[indices[0]], data.social_train[indices[1]]]), labels
        )
        values[b] = auc(model.score(reference), model.score(data.social_reference))
    deviations = values - values.mean()
    variance = float(values.var(ddof=1))
    fourth = float(np.mean(deviations**4))
    mcse = float(
        np.sqrt(max(0, (fourth - (draws - 3) / (draws - 1) * variance**2) / draws))
    )
    return NuisanceResult(
        values,
        deviations,
        shifts,
        variance,
        float(values.mean() - auc0),
        mcse,
        projected / draws,
    )


@dataclass(frozen=True)
class Uncertainty:
    point: Floats
    conditional_se: Floats
    se: Floats
    replicates: Floats


def score_uncertainty(
    null_scores: Floats,
    social_scores: Floats,
    nuisance_centered: Floats,
    *,
    seed: int,
    draws: int = 2000,
) -> Uncertainty:
    from ic_study.analysis.detection_boundary import auc

    if (
        null_scores.ndim != 3
        or social_scores.shape != null_scores.shape
        or null_scores.shape[1] != 2
    ):
        raise ValueError("Require network x two events x strength scores")
    cells = null_scores.shape[-1]
    if nuisance_centered.shape != (draws, cells) or draws < 2:
        raise ValueError("Require aligned local propagation draws")
    if not all(
        np.all(np.isfinite(a)) for a in (null_scores, social_scores, nuisance_centered)
    ):
        raise ValueError("Nonfinite inference input")
    point = np.array(
        [
            auc(null_scores[..., k].ravel(), social_scores[..., k].ravel())
            for k in range(cells)
        ]
    )
    rng = np.random.default_rng(seed)
    fixed = np.empty((draws, cells))
    for b in range(draws):
        left = null_scores[rng.integers(len(null_scores), size=len(null_scores))]
        right = social_scores[rng.integers(len(social_scores), size=len(social_scores))]
        fixed[b] = [
            auc(left[..., k].ravel(), right[..., k].ravel()) for k in range(cells)
        ]
    conditional = fixed.std(0, ddof=1)
    nuisance = nuisance_centered - nuisance_centered.mean(0)
    total = np.sqrt(conditional**2 + nuisance.var(0, ddof=1))
    # The same row is added at every strength, preserving cross-strength draws.
    replicates = np.clip(point + fixed - fixed.mean(0) + nuisance, 0, 1)
    return Uncertainty(point, conditional, total, replicates)


@dataclass(frozen=True)
class Band:
    lower: Floats
    upper: Floats
    critical: float
    empirical_exceeds_floor: bool


def band(result: Uncertainty, *, networks: int = 2000) -> Band:
    epsilon = 1 / (2 * networks)
    point = np.clip(result.point, epsilon, 1 - epsilon)
    draws = np.clip(result.replicates, epsilon, 1 - epsilon)
    logit = np.log(point / (1 - point))
    se = np.maximum(result.se, epsilon) / (point * (1 - point))
    draw_se = np.maximum(result.se, epsilon) / (draws * (1 - draws))
    max_t = np.max(np.abs(np.log(draws / (1 - draws)) - logit) / draw_se, axis=-1)
    empirical = float(np.quantile(max_t, 0.95, method="higher"))
    critical = max(empirical, 2.7729)
    lower = 1 / (1 + np.exp(np.clip(-logit + critical * se, -700, 700)))
    upper = 1 / (1 + np.exp(np.clip(-logit - critical * se, -700, 700)))
    return Band(
        np.where(result.point == 0, 0, lower),
        np.where(result.point == 1, 1, upper),
        critical,
        empirical > 2.7729,
    )


def finite_differences(
    evaluate: Callable[[Floats], Floats],
    point: Floats,
    step: float,
    baseline: Floats,
    *,
    parameters: int = 2,
) -> Floats:
    if step not in {0.01, 0.005} or parameters not in {1, 2}:
        raise ValueError("Only declared stencil steps and dimensions are available")
    derivatives = np.zeros((2, *baseline.shape))
    for j in range(parameters):
        trial = point.copy()
        direction = step if point[j] + step <= (0.999, 0.8)[j] else -step
        trial[j] += direction
        derivatives[j] = (evaluate(trial) - baseline) / direction
    return derivatives


def curve_report(
    grid: Floats,
    uncertainty: Uncertainty,
    successful: NDArray[np.bool_],
) -> dict[str, object]:
    from ic_study.analysis.detection_boundary import boundary_report

    if (
        successful.shape != grid.shape
        or grid[successful].shape != uncertainty.point.shape
    ):
        raise ValueError("Require aligned curve and gap mask")
    interval = band(uncertainty)
    available = grid[successful]
    report: dict[str, object]
    if len(available) and available[0] == 0:
        report = boundary_report(
            available,
            uncertainty.point,
            interval.lower,
            interval.upper,
        )
    else:
        report = {
            "valid_null_gate": False,
            "nonmonotone_band": False,
            "first": None,
            "sustained": None,
            "first_interval": None,
            "sustained_interval": None,
        }
    report.update(
        {
            "gap_count": int(np.sum(~successful)),
            "critical": interval.critical,
            "empirical_exceeds_floor": interval.empirical_exceeds_floor,
        }
    )
    if not np.all(successful):
        gaps = grid[~successful]

        def allowed(value: object, kind: str, limit: float) -> bool:
            return isinstance(value, (float, int)) and (
                value < limit if kind == "first" else value > limit
            )

        for kind, limit in (("first", float(gaps[0])), ("sustained", float(gaps[-1]))):
            interval_key = f"{kind}_interval"
            if not allowed(report[kind], kind, limit):
                report[kind] = None
                report[f"{kind}_censoring"] = f"gap at a={limit:g}"
            bounds = report[interval_key]
            if isinstance(bounds, tuple):
                retained = tuple(
                    value if allowed(value, kind, limit) else None for value in bounds
                )
                report[interval_key] = retained
                if None in retained:
                    report[f"{interval_key}_censoring"] = f"gap at a={limit:g}"
    report["valid_curve"] = report["valid_null_gate"]
    return report


def amplification(
    jacobian: Floats, residual: Floats, covariance: Floats, moments: int
) -> float:
    """B's local mismatch-to-feature Mahalanobis diagnostic; no AUC conversion."""
    moment_map = jacobian[:moments, :moments]
    if np.linalg.cond(moment_map) > 1e10:
        return float("nan")
    correction = np.linalg.solve(moment_map, -residual[:moments])
    drift = jacobian[2:5, :moments] @ correction
    return float(np.sqrt(max(0, float(drift @ np.linalg.pinv(covariance) @ drift))))


def mean_feature_jacobian(
    evaluate: Callable[[Floats], Floats],
    point: Floats,
    step: float,
    baseline: Floats,
    *,
    parameters: int = 2,
) -> Floats:
    """CRN mean derivative, using the matching realisations only."""
    return finite_differences(
        evaluate, point, step, baseline, parameters=parameters
    ).mean(1)


@dataclass(frozen=True)
class CovarianceDiagnostic:
    direction_shifts: Floats
    auc_shifts: Floats
    max_absolute_auc_shift: float
    flagged: bool


def covariance_diagnostic(
    train0: Floats,
    train1: Floats,
    reference0: Floats,
    reference1: Floats,
    train_jacobian: Floats,
    reference_jacobian: Floats,
    shifts: Floats,
    *,
    d5_se: float,
) -> CovarianceDiagnostic:
    """Omitted covariance effect: raw LDA coefficients and Gaussian-moment AUC.

    This smooth moment diagnostic is not the empirical rank AUC or a gate criterion.
    Training standardization and shrinkage are differentiated in raw coordinates.
    """
    n0, n1 = len(train0), len(train1)
    n = n0 + n1
    c0, c1 = np.cov(train0, rowvar=False), np.cov(train1, rowvar=False)
    delta = train1.mean(0) - train0.mean(0)
    pooled = ((n0 - 1) * c0 + (n1 - 1) * c1) / (n - 2)
    total_var = (
        (n0 - 1) * np.diag(c0) + (n1 - 1) * np.diag(c1)
    ) / n + n0 * n1 / n**2 * delta**2
    matrix = 0.8 * pooled + 0.2 * np.diag(total_var)
    direction = np.linalg.solve(matrix, delta)
    matrix_derivative = 0.8 * (n0 - 1) / (n - 2) * train_jacobian
    matrix_derivative += (
        0.2 * (n0 - 1) / n * np.array([np.diag(np.diag(c)) for c in train_jacobian])
    )
    direction_jacobian = np.array(
        [-np.linalg.solve(matrix, dc @ direction) for dc in matrix_derivative]
    )
    covariance = np.cov(reference0, rowvar=False) + np.cov(reference1, rowvar=False)
    difference = reference1.mean(0) - reference0.mean(0)
    variance = float(direction @ covariance @ direction)
    if variance <= 0:
        raise ValueError("Degenerate covariance diagnostic")
    z = float(direction @ difference / np.sqrt(variance))
    variance_jacobian = np.array(
        [
            2 * dw @ covariance @ direction + direction @ dc @ direction
            for dw, dc in zip(direction_jacobian, reference_jacobian, strict=True)
        ]
    )
    z_jacobian = direction_jacobian @ difference / np.sqrt(
        variance
    ) - z * variance_jacobian / (2 * variance)
    auc_jacobian = np.exp(-z * z / 2) / np.sqrt(2 * np.pi) * z_jacobian
    auc_shifts = shifts @ auc_jacobian
    maximum = float(np.max(np.abs(auc_shifts)))
    return CovarianceDiagnostic(
        shifts @ direction_jacobian, auc_shifts, maximum, maximum > 0.1 * d5_se
    )
