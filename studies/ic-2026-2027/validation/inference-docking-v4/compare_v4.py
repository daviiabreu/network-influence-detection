"""Phase 2: feed identical synthetic inputs to the docking and project code.

Run from studies/ic-2026-2027 with the study venv:
    OPENBLAS_NUM_THREADS=1 .venv/bin/python \
        validation/inference-docking-v4/compare_v4.py
Writes comparison-results.json next to this file. Follows
comparison-predeclared.json. It runs no gate stage, no curve and no project seed
namespace.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from ic_study.analysis import detection_boundary_v4 as pv  # noqa: E402
from ic_study.analysis.detection_boundary import auc as p_auc  # noqa: E402
from ic_study.analysis.redesign import fit_discriminant  # noqa: E402
from ic_study.simulation import detection_v4 as pdet  # noqa: E402
from ic_study.simulation import v4_criteria as pcrit  # noqa: E402
from ic_study.simulation import v4_gate as pgate  # noqa: E402

import docking_v4 as dk  # noqa: E402


def seed(case: str) -> int:
    ns = f"ic-detection-boundary-v4-inference-docking-{case}"
    return int.from_bytes(hashlib.sha256(ns.encode()).digest()[:8], "big")


def close(x, y) -> bool:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.shape != y.shape:
        return False
    both_nan = np.isnan(x) & np.isnan(y)
    ok = np.abs(x - y) <= 1e-12 + 1e-9 * np.abs(y)
    return bool(np.all(ok | both_nan | (x == y)))


def maxdiff(x, y) -> float:
    d = np.abs(np.asarray(x, float) - np.asarray(y, float))
    d = d[np.isfinite(d)]
    return float(d.max()) if d.size else 0.0


RESULTS: dict[str, dict] = {}


def record(component: str, case: str, **fields) -> None:
    RESULTS.setdefault(component, {})[case] = fields


# ============================================================ 1 + 2: solver, tolerance
M = 1024


def noise(scale: float) -> np.ndarray:
    return np.tile(np.array([[1.0, -1.0], [-1.0, 1.0]]), (M // 2, 1)) * scale


def linear(phi0, eta0, c12=0.3, c21=0.1, s2=1.0, sc=0.02, s1=1.0):
    nz = noise(sc)

    def fn(phi, eta):
        m1 = s1 * (phi - phi0) + c12 * (eta - eta0)
        m2 = s2 * (eta - eta0) + c21 * (phi - phi0)
        return np.array([m1, m2]) + nz

    return fn


def nonlinear(phi, eta):
    m1 = math.tanh(3 * (phi - 0.55)) + 0.2 * eta**2 - 0.2 * 0.09
    m2 = (eta - 0.3) * (1 + phi) + 0.05 * (phi - 0.55)
    return np.array([m1, m2]) + noise(0.02)


def hump(phi, eta):
    return np.array([phi - 0.5, -0.1 + math.sin(12 * eta)]) + noise(0.02)


def stairs(phi, eta):
    return np.array([math.floor(phi * 50) / 50 - 0.3137, eta - 0.1]) + noise(0.02)


def flat(phi, eta):
    return np.array([phi - 0.5, -0.01 + 0 * eta]) + noise(0.02)


def nan_region(phi, eta):
    return np.full((M, 2), np.nan) if phi > 0.7 else linear(0.6, 0.2)(phi, eta)


def anchor_exact(phi, eta):
    return (
        np.zeros((M, 2)) if (phi, eta) == (0.85, 0.0) else linear(0.85, 0.0)(phi, eta)
    )


_TOL_EDGE = float(dk.acceptance_tolerance(0.02 / math.sqrt(M) * math.sqrt(M / (M - 1))))


def near_threshold(phi, eta):  # residual at phi=0.999 is 0.999*tol (inside by 0.1%)
    return np.array([phi - 0.999 + 0.999 * _TOL_EDGE, 0.0 * eta]) + noise(0.02)


SOLVER_CASES = {
    "S01_linear_interior": (linear(0.6, 0.2), {}),
    "S02_smooth_nonlinear_interior": (nonlinear, {}),
    "S03_lower_face": (linear(0.6, -0.05), {}),
    "S04_eta_beyond_upper": (linear(0.5, 1.2), {}),
    "S05_phi_beyond_upper_on_face": (linear(1.2, 0.0, c12=0), {}),
    "S06_phi_beyond_lower_on_face": (linear(-0.2, 0.0, c12=0), {}),
    "S07_corner": (linear(0.999, 0.0), {}),
    "S08_decreasing_profile": (linear(0.5, 0.3, s2=-1.0), {}),
    "S09_hump_profile": (hump, {}),
    "S10_discrete_stairs_L1": (stairs, {}),
    "S11_flat_L2": (flat, {}),
    "S12_nan_region": (nan_region, {}),
    "S13_exhausted_budget": (linear(0.6, 0.2), {"budget": 5}),
    "S14_anchor_exact": (anchor_exact, {"identity": True}),
    "S15_anchor_mean_zero_not_bytewise": (linear(0.85, 0.0), {"identity": True}),
    "S16_one_param_interior": (linear(0.4, 0.0), {"fixed_eta": 0.0}),
    "S17_one_param_beyond_upper": (linear(1.3, 0.0), {"fixed_eta": 0.0}),
    "S18_one_param_endpoint": (linear(0.0, 0.0), {"fixed_eta": 0.0}),
    "S19_zero_noise_floor_tolerance": (linear(0.6, 0.2, sc=0.0), {}),
    "S20_high_noise_cap_tolerance": (linear(0.6, 0.2, sc=1.0), {}),
    "S21_near_threshold_endpoint": (near_threshold, {"fixed_eta": 0.0}),
    "S22_steep_interior": (linear(0.3, 0.5, s1=20.0), {}),
}


def run_project_solver(fn, opts):
    def evaluate(phi, eta):
        d = np.asarray(fn(phi, eta), float)
        return d if d.ndim == 2 else d[:, None]

    return pv.profile_match(
        np.zeros((M, 2)),
        evaluate,
        identity=opts.get("identity", False),
        fixed_eta=opts.get("fixed_eta"),
        budget=opts.get("budget", 96),
    )


def run_docking_solver(fn, opts):
    one = "fixed_eta" in opts
    return dk.solve_profile(
        fn,
        None if one else (0.0, 0.8),
        fixed_eta=opts.get("fixed_eta", 0.0),
        anchor=(0.85, 0.0) if opts.get("identity") else None,
        budget=opts.get("budget", 96),
    )


def compare_solver():
    for case, (fn, opts) in SOLVER_CASES.items():
        p = run_project_solver(fn, opts)
        d = run_docking_solver(fn, opts)
        k = p.fitted_moments
        rec = {
            "project_status": p.status,
            "docking_status": d.status,
            "status_equal": p.status == d.status,
            "project_evaluations": p.evaluations,
            "docking_evaluations": d.evaluations,
        }
        if p.success:
            rec["project_theta"] = p.parameters.tolist()
            rec["project_accepts"] = bool(np.all(dk.accepts(p.residual[:k], p.se[:k])))
            # component 2: tolerance and SE recomputed by the docking formulas
            rec["tol_equal"] = close(dk.acceptance_tolerance(p.se), p.tolerance)
            rec["se_equal"] = close(dk.paired_se(p.differences), p.se)
        if d.status in dk.ACCEPTED:
            rec["docking_theta"] = [d.phi, d.eta]
            rec["docking_accepts"] = bool(np.all(dk.accepts(d.gbar[:k], d.se[:k])))
        if p.success and d.status in dk.ACCEPTED:
            rec["theta_maxdiff"] = maxdiff(p.parameters, [d.phi, d.eta])
            rec["theta_within_1e-3"] = rec["theta_maxdiff"] <= 1e-3
        record("1_profile_solver", case, **rec)


def compare_tolerance_probes():
    for se_target in (0.0, 1e-7, 4e-6, 1e-5, 2e-4, 1e-3):
        scale = se_target * math.sqrt(M) * math.sqrt((M - 1) / M)
        nz = noise(1.0)[:, :1] * scale

        def fn(phi, eta, nz=nz):
            return np.column_stack([nz[:, 0] + (phi - 0.5), nz[:, 0] * 0])

        p = run_project_solver(fn, {"fixed_eta": 0.0})
        se = dk.paired_se(p.differences)
        record(
            "2_acceptance_tolerance",
            f"T_se_{se_target:g}",
            project_se=p.se.tolist(),
            docking_se=se.tolist(),
            se_equal=close(se, p.se),
            project_tolerance=p.tolerance.tolist(),
            docking_tolerance=dk.acceptance_tolerance(p.se).tolist(),
            tol_equal=close(dk.acceptance_tolerance(p.se), p.tolerance),
            accept_equal=bool(
                dk.accepts(p.residual[0], p.se[0])
                == (abs(p.residual[0]) <= p.tolerance[0])
            ),
            status=p.status,
        )


# ============================================================ 3: validation
def compare_validation():
    rng = np.random.default_rng(seed("validation"))
    base = np.tile(np.array([[1.0, -1.0], [-1.0, 1.0]]), (1024, 1)) * 1e-3
    se_val = dk.paired_se(base)
    cases = {}
    cases["V01_zero_residual"] = (base, np.full(2, 1e-4), 2)
    thr = 4 * np.hypot(1e-4, se_val[0])
    cases["V02_at_threshold_minus"] = (
        [*base, thr * (1 - 1e-09), 0],
        np.full(2, 1e-4),
        2,
    )
    cases["V03_at_threshold_plus"] = (
        [*base, thr * (1 + 1e-09), 0],
        np.full(2, 1e-4),
        2,
    )
    v4 = base.copy()
    v4[5, 0] = np.nan
    cases["V04_nan_row"] = (v4, np.full(2, 1e-4), 2)
    cases["V05_zero_se_zero_residual"] = (np.zeros((2048, 2)), np.zeros(2), 2)
    cases["V06_one_moment_large_L2"] = ([*base, 0, 1.0], np.full(2, 1e-4), 1)
    small = base * 1e-2
    se_small = dk.paired_se(small)
    edge = 0.0003 - 2.2414 * se_small[0]
    cases["V07_equivalence_edge_minus"] = (
        [*small, edge - 1e-12, 0],
        np.full(2, 1e-3),
        2,
    )
    cases["V07_equivalence_edge_plus"] = (
        [*small, edge + 1e-09, 0],
        np.full(2, 1e-3),
        2,
    )
    for i in range(20):
        d = rng.normal(0, 0.01, (2048, 2))
        d -= d.mean(0)
        fse = np.array([2e-4, 3e-4])
        tot = np.hypot(fse, dk.paired_se(d))
        d += rng.uniform(0, 6, 2) * tot * rng.choice([-1, 1], 2)
        cases[f"V08_random_{i:02d}"] = (d, fse, 2)
    for case, (d, fse, k) in cases.items():
        p = pv.validate_fit(d, k, fse)
        q = dk.validate(d.mean(0)[:k], fse[:k], dk.paired_se(d)[:k])
        record(
            "3_validation",
            case,
            project_passed=p.passed,
            docking_passed=q.passed,
            passed_equal=p.passed == q.passed,
            z_equal=close(q.z, np.abs(p.z[:k])),
            equivalence_equal=close(q.equivalence, p.equivalence[:k]),
            equivalence_passed_equal=bool(np.all(q.equivalence_pass))
            == p.equivalence_passed,
        )


class StubSource:
    """Minimal PanelSource stand-in: linear moments, latent channel (no
    feasibility pre-check), controllable validation residuals per attempt."""

    def __init__(self, fail_attempts: set[int], gap: bool = False):
        self.cell = SimpleNamespace(
            family="B",
            reliability=0.7,
            gain=0,
            channel="latent",
            error_correlation=0,
            identity=False,
        )
        self.fail_attempts = fail_attempts
        self.gap = gap

    def profiles(self, phase, count, parameters=None, attempt=0):
        rows = np.tile(
            np.array([[1.0, -1.0, 0.1, 0.2, 0.3], [-1.0, 1.0, -0.1, -0.2, -0.3]]),
            (count // 2, 1),
        )
        out = rows * 0.02
        if parameters is None:
            return out  # target: all-zero means
        phi, eta = parameters
        out = np.roll(
            out, 1, axis=0
        )  # harness fix (b): null noise must not cancel the target's
        shift = np.array(
            [
                phi - 0.6 + 0.3 * (eta - 0.2),
                (eta - 0.2) + 0.1 * (phi - 0.6),
                phi,
                eta,
                phi * eta,
            ]
        )
        if self.gap:
            shift[0] = phi - 1.5  # beyond the family: no L1 root
        out = out + shift
        if phase == "validate" and attempt in self.fail_attempts:
            out = out.copy()
            out[:, :2] += 1.0
        return out


def compare_retry():
    scenarios = {
        "R01_retry_then_pass": ({0}, False),
        "R02_retry_then_fail": ({0, 1}, False),
        "R03_solver_gap_no_retry": (set(), True),
    }
    for case, (fails, gap) in scenarios.items():
        src = StubSource(fails, gap)
        p = pdet.fit_cell(src)
        p_counts = [a.count for a in p.attempts]

        def fit(attempt, m, src=src):
            def fn(phi, eta):
                return (
                    src.profiles("match", m, np.array([phi, eta]), attempt)[:, :2]
                    - src.profiles("match", m)[:, :2]
                )

            return dk.solve_profile(fn, (0.0, 0.8))

        def val(attempt, fr, src=src):
            th = np.array([fr.phi, fr.eta])
            return (
                src.profiles("validate", 2048, th, attempt)
                - src.profiles("validate", 2048, None, attempt)
            )[:, :2]

        d = dk.fit_with_retry(fit, val)
        d_counts = [a["M"] for a in d["attempts"]]
        record(
            "3_validation",
            case,
            project_M=p_counts,
            docking_M=d_counts,
            project_success=p.success,
            docking_success=d["accepted"],
            project_final_status=p.final.fit.status,
            docking_final_status=d["status"],
            retry_equal=(p_counts == d_counts and p.success == d["accepted"]),
        )


# ============================================================ 4: nuisance
def compare_project_shift():
    rng = np.random.default_rng(seed("project-shift"))
    lo, hi = np.array([0.0, 0.0]), np.array([0.999, 0.8])
    points = [
        np.array(x)
        for x in ([0.6, 0.3], [0.6, 0.0], [0.6, 0.8], [0.001, 0.4], [0.998, 0.4])
    ]
    n_dt = n_pr = total = 0
    worst = 0.0
    for _ in range(20):
        J = np.array(
            [
                [rng.uniform(0.5, 2), rng.uniform(-0.5, 0.5)],
                [rng.uniform(-0.5, 0.5), rng.uniform(0.5, 2)],
            ]
        )
        if J[1, 1] - J[1, 0] * J[0, 1] / J[0, 0] <= 1e-10:
            continue
        for pt in points:
            res = rng.normal(0, 0.01, (25, 2))
            for r in res:
                dp, hitp = pv.project_shift(pt, J, r)
                diffs = np.tile(r, (4, 1))
                dd, hitd = dk.linearised_shifts(
                    diffs, np.arange(4)[None, :], J, pt, lo, hi
                )
                total += 1
                n_dt += close(dd[0], dp)
                n_pr += bool(hitd[0]) == bool(hitp)
                worst = max(worst, maxdiff(dd[0], dp))
    record(
        "4_nuisance_propagation",
        "N01_project_shift_random",
        cases=total,
        dtheta_equal=n_dt,
        projected_equal=n_pr,
        max_abs_diff=worst,
    )
    J = np.array([[1.0, 1.0], [1.0, 0.5]])  # Schur 0.5 - 1 < 0
    try:
        pv.project_shift(np.array([0.6, 0.3]), J, np.array([0.01, 0.0]))
        proj = "returned"
    except ValueError as exc:
        proj = f"ValueError: {exc}"
    dd, _ = dk.linearised_shifts(
        np.tile([0.01, 0.0], (2, 1)),
        np.arange(2)[None, :],
        J,
        np.array([0.6, 0.3]),
        lo,
        hi,
    )
    record(
        "4_nuisance_propagation",
        "N02_schur_nonpositive",
        project=proj,
        docking_dtheta=dd[0].tolist(),
    )


def compare_fd():
    def fmean(t):
        return np.array(
            [math.sin(t[0]) + t[1] ** 2, t[0] * t[1], math.exp(t[1]) - t[0]]
        )

    for pt in ([0.6, 0.3], [0.995, 0.3], [0.6, 0.795]):
        for step in (0.01, 0.005):
            pt_a = np.array(pt)
            p = pv.finite_differences(
                lambda t: fmean(t), pt_a, step, fmean(pt_a)
            )  # (2, 3)
            d = dk.fd_jacobian(fmean, pt_a, np.array([0.999, 0.8]), step)  # (3, 2)
            record(
                "4_nuisance_propagation",
                f"N03_fd_{pt}_{step}",
                equal=close(d, p.T),
                max_abs_diff=maxdiff(d, p.T),
            )


def project_auc_fn(ntr, ttr, nref, tref):
    labels = np.repeat([0, 1], [len(ntr), len(ttr)])
    model = fit_discriminant(np.concatenate([ntr, ttr]), labels)
    return p_auc(model.score(nref), model.score(tref))


def compare_nuisance_draws():
    for case, theta, bias in (
        ("N04_nuisance_draws_interior", (0.6, 0.3), (0.0, 0.0)),
        ("N05_nuisance_draws_face", (0.6, 0.0), (0.0, 0.004)),
    ):
        rng = np.random.default_rng(seed(case))
        Mm, nets, f, B = 64, 20, 3, 200
        diffs = rng.normal(0, 0.02, (Mm, 2)) + np.array(bias)
        J = np.array([[1.2, 0.3], [0.2, 0.9]])
        Dm = rng.normal(0, 1, (2, f))  # project: (parameters, features)
        null_train = rng.normal(0, 1, (2 * nets, f))
        social_train = rng.normal(0.4, 1, (2 * nets, f))
        null_ref = rng.normal(0, 1, (80, f))
        social_ref = rng.normal(0.4, 1, (80, f))
        s = seed(case + "-stream")
        data = pv.NuisanceInput(
            np.array(theta),
            diffs,
            J,
            null_train,
            social_train,
            null_ref,
            social_ref,
            Dm,
        )
        p = pv.nuisance_draws(data, seed=s, draws=B)
        # reproduce the project's documented index stream for the docking side
        mr, nr, sr = [
            np.random.default_rng(c) for c in np.random.SeedSequence(s).spawn(3)
        ]
        midx = np.empty((B, Mm), int)
        i0 = np.empty((B, nets), int)
        i1 = np.empty((B, nets), int)
        for b in range(B):
            midx[b] = np.floor(mr.random(4096)[:Mm] * Mm).astype(int)
            i0[b] = nr.integers(nets, size=nets)
            i1[b] = sr.integers(nets, size=nets)
        d = dk.propagate_nuisance(
            diffs,
            midx,
            i0,
            i1,
            J,
            Dm.T,
            np.array(theta),
            np.array([0.0, 0.0]),
            np.array([0.999, 0.8]),
            null_train.reshape(nets, 2, f),
            social_train.reshape(nets, 2, f),
            null_ref,
            social_ref,
            auc_fn=project_auc_fn,
        )
        record(
            "4_nuisance_propagation",
            case,
            shifts_equal=close(d.dtheta, p.shifts),
            shifts_maxdiff=maxdiff(d.dtheta, p.shifts),
            aucs_equal=close(d.auc_draws, p.aucs),
            aucs_maxdiff=maxdiff(d.auc_draws, p.aucs),
            v_nuis_equal=close(d.v_nuis, p.variance),
            project_v=p.variance,
            docking_v=d.v_nuis,
            mean_shift_equal=close(d.mean_shift, p.mean_shift),
            projected_fraction_equal=d.projected_fraction == p.projected_fraction,
            projected_fraction=p.projected_fraction,
            project_mcse=p.mcse,
            docking_mcse=d.mcse_v,
            mcse_rel_diff=abs(d.mcse_v - p.mcse) / p.mcse,
        )
    pa = pv.anchor_nuisance(2000)
    da = dk.propagate_nuisance(
        np.zeros((4, 2)),
        np.zeros((2000, 4), int),
        None,
        None,
        None,
        None,
        np.array([0.85, 0.0]),
        None,
        None,
        np.zeros((2, 2, 1)),
        None,
        None,
        None,
        anchor_exact=True,
    )
    record(
        "4_nuisance_propagation",
        "N06_anchor",
        project_v=pa.variance,
        docking_v=da.v_nuis,
        equal=pa.variance == da.v_nuis == 0
        and not pa.shifts.any()
        and not da.dtheta.any(),
        project_anchor_auc_draws=float(pa.aucs[0]),
        docking_anchor_auc_draws="NaN (not produced)",
    )


# ============================================================ 5: bootstrap
def bootstrap_both(null, social, s, B, v_nuis_dev):
    p = pv.score_uncertainty(null, social, v_nuis_dev, seed=s, draws=B)
    rng = np.random.default_rng(s)
    i0 = np.empty((B, len(null)), int)
    i1 = np.empty((B, len(social)), int)
    for b in range(B):
        i0[b] = rng.integers(len(null), size=len(null))
        i1[b] = rng.integers(len(social), size=len(social))
    ah, boot = dk.cluster_bootstrap_auc(social, null, i1, i0)
    return p, ah, boot


def compare_bootstrap():
    cases = {}
    rng = np.random.default_rng(seed("bootstrap"))
    n, S = 200, 9
    u0, u1 = (
        rng.normal(0, math.sqrt(0.5), (n, 1, 1)),
        rng.normal(0, math.sqrt(0.5), (n, 1, 1)),
    )
    shifts = np.array(dk.GRID)[None, None, :] * 2
    cases["B01_gaussian_icc05"] = (
        u0 + rng.normal(0, math.sqrt(0.5), (n, 2, S)),
        u1 + rng.normal(0, math.sqrt(0.5), (n, 2, S)) + shifts,
    )
    cases["B02_integer_ties"] = tuple(np.round(x) for x in cases["B01_gaussian_icc05"])
    cases["B03_constant_scores"] = (np.zeros((n, 2, S)), np.zeros((n, 2, S)))
    sep = cases["B01_gaussian_icc05"][1].copy()
    sep[..., 6:] += 100
    cases["B04_perfect_separation"] = (cases["B01_gaussian_icc05"][0], sep)
    cases["B05_single_network"] = (
        rng.normal(size=(1, 2, S)),
        rng.normal(size=(1, 2, S)) + 1,
    )
    B = 300
    for case, (null, social) in cases.items():
        dev = rng.normal(0, 0.01, (B, S))
        p, ah, boot = bootstrap_both(null, social, seed(case), B, dev)
        se_sc = boot.std(0, ddof=1)
        v = (dev - dev.mean(0)).var(0, ddof=1)
        record(
            "5_cluster_bootstrap",
            case,
            point_equal=close(ah, p.point),
            point_maxdiff=maxdiff(ah, p.point),
            se_scores_equal=close(se_sc, p.conditional_se),
            se_scores_maxdiff=maxdiff(se_sc, p.conditional_se),
            se_total_equal=close(dk.se_total(se_sc, v), p.se),
        )


def compare_bootstrap_distribution():
    """B06: one slot, production size; both SE estimates vs the Monte Carlo SD."""
    rng = np.random.default_rng(seed("bootstrap-distribution"))
    n, reps, B = 2000, 40, 400
    aucs, se_p, se_d = [], [], []
    for r in range(reps):
        u0, u1 = (
            rng.normal(0, math.sqrt(0.5), (n, 1, 1)),
            rng.normal(0, math.sqrt(0.5), (n, 1, 1)),
        )
        null = u0 + rng.normal(0, math.sqrt(0.5), (n, 2, 1))
        social = u1 + rng.normal(0, math.sqrt(0.5), (n, 2, 1)) + 0.3
        p, ah, boot = bootstrap_both(
            null, social, seed(f"b06-{r}"), B, np.zeros((B, 1))
        )
        aucs.append(ah[0])
        se_p.append(p.conditional_se[0])
        se_d.append(boot[:, 0].std(ddof=1))
    sd = float(np.std(aucs, ddof=1))
    rel_sd_error = 1 / math.sqrt(2 * (reps - 1))
    record(
        "5_cluster_bootstrap",
        "B06_production_size_distribution",
        mc_sd=sd,
        project_mean_se=float(np.mean(se_p)),
        docking_mean_se=float(np.mean(se_d)),
        project_within_15pct=abs(np.mean(se_p) / sd - 1) <= 0.15,
        docking_within_15pct=abs(np.mean(se_d) / sd - 1) <= 0.15,
        note=f"reps={reps}; the relative SE of the MC SD is about {rel_sd_error:.3f}",
    )


# ============================================================ 6: band / gap / gate
def compare_band():
    rng = np.random.default_rng(seed("band"))
    for i in range(10):
        S, B = 9, 500
        point = np.sort(rng.uniform(0.45, 0.99, S))
        boot = point + rng.normal(0, 0.01 + 0.01 * i, (B, S))
        dev = rng.normal(0, 0.005, (B, S))
        dev -= dev.mean(0)
        v = dev.var(0, ddof=1)
        se = np.sqrt(boot.std(0, ddof=1) ** 2 + v)
        repl = np.clip(point + boot - boot.mean(0) + dev, 0, 1)
        p = pv.band(pv.Uncertainty(point, boot.std(0, ddof=1), se, repl))
        d = dk.band(point, boot, dev, v, np.ones(S, bool))
        record(
            "6_band_gap_gate",
            f"G01_band_random_{i}",
            critical_equal=close(d.critical, p.critical),
            project_critical=p.critical,
            docking_critical=d.critical,
            lower_equal=close(d.lower, p.lower),
            upper_equal=close(d.upper, p.upper),
            band_maxdiff=max(maxdiff(d.lower, p.lower), maxdiff(d.upper, p.upper)),
            exceeds_equal=d.exceeds_floor == p.empirical_exceeds_floor,
        )
    point = np.linspace(0.5, 0.9, 9)
    boot = np.tile(point, (100, 1))
    p = pv.band(pv.Uncertainty(point, np.zeros(9), np.zeros(9), boot))
    d = dk.band(point, boot, np.zeros((100, 9)), np.zeros(9), np.ones(9, bool))
    record(
        "6_band_gap_gate",
        "G02_band_floor_degenerate",
        project_critical=p.critical,
        docking_critical=d.critical,
        both_at_floor=p.critical == d.critical == 2.7729,
        lower_equal=close(d.lower, p.lower),
        upper_equal=close(d.upper, p.upper),
    )


def gap_case(auc, avail, halfwidth=0.05, lo0=None):
    grid = np.array(dk.GRID)
    auc = np.asarray(auc, float)
    avail = np.asarray(avail, bool)
    lower, upper = auc - halfwidth, auc + halfwidth
    if lo0 is not None:
        lower[0] = lo0
    # project path: curve_report on available slots with a band whose lower/upper
    # equal ours: inject through a stub of pv.band
    orig = pv.band
    pv.band = lambda u, networks=2000: pv.Band(
        lower[avail], upper[avail], 2.7729, False
    )
    try:
        u = pv.Uncertainty(
            auc[avail],
            np.zeros(avail.sum()),
            np.zeros(avail.sum()),
            np.zeros((2, avail.sum())),
        )
        p = pv.curve_report(grid, u, avail)
    finally:
        pv.band = orig
    b = dk.Band(auc, lower, upper, 2.7729, 0.0, False, np.zeros(9))
    d = dk.boundaries(b, avail)
    return p, d


def compare_gaps():
    base = [0.5, 0.5, 0.52, 0.6, 0.66, 0.72, 0.8, 0.9, 0.95]
    allv = np.ones(9, bool)

    def av(*gaps):
        a = allv.copy()
        for g in gaps:
            a[g] = False
        return a

    cases = {
        "C01_all_available": (base, allv, {}),
        "C02_gap_before_crossing": (base, av(4), {}),
        "C03_gap_after_crossing": (base, av(7), {}),
        "C04_gap_top": (base, av(8), {}),
        "C05_gap_a0": (base, av(0), {}),
        "C06_null_gate_fail": ([0.6, *base[1:]], allv, {}),
        "C07_no_crossing": (
            [0.5, 0.5, 0.52, 0.55, 0.6, 0.62, 0.64, 0.66, 0.68],
            allv,
            {},
        ),
        "C08_exact_target_tie": (
            [0.5, 0.5, 0.52, 0.6, 0.70, 0.72, 0.8, 0.9, 0.95],
            allv,
            {"halfwidth": 0.0},
        ),
        "C09_nonmonotone": (
            [0.5, 0.5, 0.52, 0.6, 0.66, 0.72, 0.64, 0.9, 0.95],
            allv,
            {},
        ),
        "C10_sustained_across_gap": (
            [0.5, 0.5, 0.52, 0.75, 0.76, 0.78, 0.8, 0.9, 0.95],
            av(4),
            {},
        ),
        "C11_crossing_at_a0_valid_gate": (
            [0.72, 0.72, 0.73, 0.74, 0.75, 0.76, 0.8, 0.9, 0.95],
            allv,
            {"lo0": 0.45},
        ),
    }
    for case, (auc, avail, kw) in cases.items():
        p, d = gap_case(auc, avail, **kw)
        valid = bool(p["valid_null_gate"])
        fi = (
            p["first_interval"]
            if isinstance(p["first_interval"], tuple)
            else (None, None)
        )
        si = (
            p["sustained_interval"]
            if isinstance(p["sustained_interval"], tuple)
            else (None, None)
        )
        proj = {
            "valid": valid,
            "first": p["first"],
            "first_lo": fi[0],
            "first_hi": fi[1],
            "sustained": p["sustained"],
            "sust_lo": si[0],
            "sust_hi": si[1],
        }
        dock = {
            "valid": d["null_gate"],
            "first": d["first_point"],
            "first_lo": d["first_ci_lower"],
            "first_hi": d["first_ci_upper"],
            "sustained": d["sustained_point"],
            "sust_lo": d["sustained_ci_lower"],
            "sust_hi": d["sustained_ci_upper"],
        }
        norm = lambda x: None if x is None else round(float(x), 12)  # noqa: E731
        diffs = {
            k: [proj[k], dock[k]]
            for k in proj
            if (norm(proj[k]) if k != "valid" else proj[k])
            != (norm(dock[k]) if k != "valid" else dock[k])
        }
        record(
            "6_band_gap_gate",
            case,
            project=proj,
            docking=dock,
            equal=not diffs,
            differences=diffs,
            project_nonmonotone=p["nonmonotone_band"],
            docking_nonmonotone=d["band_decrease_flag"],
        )


# ============================================================ 7: stop rule, allowances
def compare_stop_rule():
    crit = {
        "G2c_refits": [100, 40],
        "failure_rule": {"G2c_per_100": 3, "G2c_per_40": 2, "G2_per_100": 5},
    }
    for n_cells in (7, 6):
        cells = tuple((0.03, 0.5 + 0.05 * i) for i in range(n_cells))
        for gaps in range(7) if n_cells == 7 else (0, 2):
            statuses = [
                {
                    "a": 0.1,
                    "fits": [
                        {"family": "B", "channel": "observed", "success": i >= gaps}
                        for i in range(54)
                    ],
                }
            ]
            p = pgate.g0_gap_binding(statuses, cells, crit)
            mc = dk.stop_rule_mc(gaps, n_cells=n_cells, sims=200_000, seed=250925006)
            ex = dk.stop_rule_exact(gaps, n_cells=n_cells)
            tol = 4 * math.sqrt(ex * (1 - ex) / 200_000) + 1e-12
            record(
                "7_stop_rule_allowances",
                f"J_cells{n_cells}_gaps{gaps}",
                project=p["pass_probability"],
                docking_mc=mc,
                exact=ex,
                shared_seed_equal=p["pass_probability"] == mc,
                project_vs_exact_ok=abs(p["pass_probability"] - ex) <= tol,
                docking_vs_exact_ok=abs(mc - ex) <= tol,
                stop_equal=(p["pass_probability"] < 0.80) == dk.stop_before_g2(mc),
                pooled_allowance_equal=p["G2_pooled_allowance"]
                == math.ceil(0.02 * 100 * n_cells),
                posterior_equal=(p["posterior_alpha"], p["posterior_beta"])
                == dk.jeffreys_posterior(gaps),
            )


def compare_allowances():
    rng = np.random.default_rng(seed("allowances"))
    patterns = {
        "A01_all_zero": [0] * 7,
        "A01_cell5": [5, 0, 0, 0, 0, 0, 0],
        "A01_cell6": [6, 0, 0, 0, 0, 0, 0],
        "A01_pooled14": [5, 2, 2, 2, 1, 1, 1],
        "A01_pooled15": [5, 2, 2, 2, 2, 1, 1],
        "A01_six_cells_12": [2] * 6,
        "A01_six_cells_13": [3, 2, 2, 2, 2, 2],
    }
    for case, fails in patterns.items():
        k = len(fails)
        success = np.ones((k, 100), bool)
        for c, f in enumerate(fails):
            success[c, :f] = False
        est = rng.normal(0, 1, (k, 100))
        se = np.ones((k, 100))
        p = pcrit.dispersion(est, se, success, seed=1, bootstraps=19)
        record(
            "7_stop_rule_allowances",
            case,
            project=p["failure_allowance_met"],
            docking=dk.g2_allowance_pass(fails),
            equal=p["failure_allowance_met"] == dk.g2_allowance_pass(fails),
        )
    local = rng.normal(0, 1, 2000)
    for planned, f in ((100, 3), (100, 4), (40, 2), (40, 3)):
        refits = rng.normal(0, 1, planned)
        refits[:f] = np.nan
        p = pcrit.refit_ratio(local, refits, seed=1)
        allow_d = dk.g2c_allowance_pass(
            f if planned == 100 else 0, f if planned == 40 else 0
        )
        allow_p = p["failure_count"] <= (3 if planned == 100 else 2)
        record(
            "7_stop_rule_allowances",
            f"A02_g2c_{planned}_{f}",
            project_allowance=allow_p,
            project_pass=p["pass"],
            docking=allow_d,
            equal=allow_p == allow_d,
            project_pass_consistent=(not allow_d) <= (not p["pass"]),
        )
    for case, ratios in {
        "A03_edge_low": [0.8, 0.8, 0.9],
        "A03_edge_high": [1.25, 1.25, 1.0],
        "A03_out": [1.26, 1.3, 1.0],
        "A03_zero_zero": "zz",
        "A03_x_zero": "xz",
    }.items():
        if ratios == "zz":
            var = np.array([[[0.0, 0.0], [1.0, 1.0], [1.0, 1.0]]])
        elif ratios == "xz":
            var = np.array([[[0.0, 1.0], [0.0, 1.0], [1.0, 1.0]]])
        else:
            var = np.array([[[1.0, r] for r in ratios]])
        p = pcrit.fd_stability(var, np.ones(var.shape[:2], bool))
        with np.errstate(divide="ignore", invalid="ignore"):
            rat = var[0, :, 1] / var[0, :, 0]
        d = dk.fd_stability_pass(rat)
        record(
            "7_stop_rule_allowances",
            case,
            project=p["fd_stable"],
            docking=d,
            equal=p["fd_stable"] == d,
            project_median=p["fd_ratio_median_by_cell"][0],
            docking_median=float(np.median(rat)),
        )


def main() -> None:
    compare_solver()
    compare_tolerance_probes()
    compare_validation()
    compare_retry()
    compare_project_shift()
    compare_fd()
    compare_nuisance_draws()
    compare_bootstrap()
    compare_bootstrap_distribution()
    compare_band()
    compare_gaps()
    compare_stop_rule()
    compare_allowances()
    out = HERE / "comparison-results.json"
    out.write_text(
        json.dumps(
            RESULTS,
            indent=1,
            default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o),
        )
    )
    print("wrote", out)


if __name__ == "__main__":
    main()
