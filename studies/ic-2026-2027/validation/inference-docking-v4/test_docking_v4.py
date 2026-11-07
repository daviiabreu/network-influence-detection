"""Phase 1 invariant tests for the clean-room docking implementation."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))
import docking_v4 as dk

M = 1024
_NOISE = (
    np.tile(np.array([[1.0, -1.0], [-1.0, 1.0]]), (M // 2, 1)) * 0.02
)  # exact zero mean


def linear_moments(phi0, eta0, c12=0.3, c21=0.1, s2=1.0):
    def fn(phi, eta):
        m1 = (phi - phi0) + c12 * (eta - eta0)
        m2 = s2 * (eta - eta0) + c21 * (phi - phi0)
        return np.array([m1, m2]) + _NOISE

    return fn


# ------------------------------------------------------------------ tolerance
def test_tolerance_formula():
    se = np.array([0.0, 1e-7, 4e-6, 1e-4, 2e-4, 1.0])
    assert np.allclose(
        dk.acceptance_tolerance(se), [1e-6, 1e-6, 1e-6, 2.5e-5, 5e-5, 5e-5]
    )
    assert not dk.accepts(np.nan, 1.0)


# ------------------------------------------------------------------ solver
def test_interior_root_found():
    r = dk.solve_profile(linear_moments(0.6, 0.2), (0.0, 0.8))
    assert r.status == "interior" and r.stepped
    assert abs(r.eta - 0.2) < 1e-3 and abs(r.phi - 0.6) < 1e-3
    assert np.all(dk.accepts(r.gbar, r.se))
    assert r.evaluations <= dk.BUDGET


def test_smooth_nonlinear_root():
    def fn(phi, eta):
        m1 = math.tanh(3 * (phi - 0.55)) + 0.2 * eta**2 - 0.2 * 0.09
        m2 = (eta - 0.3) * (1 + phi) + 0.05 * (phi - 0.55)
        return np.array([m1, m2]) + _NOISE

    r = dk.solve_profile(fn, (0.0, 0.8))
    assert r.status == "interior"
    assert np.all(dk.accepts(r.gbar, r.se))


def test_lower_face_boundary():
    r = dk.solve_profile(linear_moments(0.6, -0.05), (0.0, 0.8))
    assert r.status == "boundary" and r.eta == 0.0
    assert dk.accepts(r.gbar[0], r.se[0])  # L1 priority holds on the face


def test_upper_eta_beyond_limit():
    r = dk.solve_profile(linear_moments(0.5, 1.2), (0.0, 0.8))
    assert r.status == "family-limit-upper"


def test_phi_beyond_limits_on_face_are_family_limits():
    assert (
        dk.solve_profile(linear_moments(1.2, 0.0, c12=0), (0.0, 0.8)).status
        == "family-limit-upper"
    )
    assert (
        dk.solve_profile(linear_moments(-0.2, 0.0, c12=0), (0.0, 0.8)).status
        == "family-limit-lower"
    )


def test_corner_is_boundary_without_step():
    # target exactly at phi = 0.999, eta = 0:
    # both endpoints accepted without a real step
    r = dk.solve_profile(linear_moments(0.999, 0.0), (0.0, 0.8))
    assert r.status == "boundary" and r.phi == 0.999 and r.eta == 0.0 and not r.stepped


def test_non_monotone_profile():
    # decreasing profile: h(0) > 0 but the face probe goes down
    r = dk.solve_profile(linear_moments(0.5, 0.3, s2=-1.0), (0.0, 0.8))
    assert r.status == "non-monotone-profile"

    def hump(phi, eta):
        m1 = phi - 0.5
        m2 = -0.1 + math.sin(12 * eta)  # sign change, then non-monotone points
        return np.array([m1, m2]) + _NOISE

    assert dk.solve_profile(hump, (0.0, 0.8)).status in (
        "non-monotone-profile",
        "interior",
    )


def test_degenerate_secant_and_discrete_steps_terminate():
    def stairs(phi, eta):
        m1 = math.floor(phi * 50) / 50 - 0.3137  # never within tolerance
        return np.array([m1, eta - 0.1]) + _NOISE

    r = dk.solve_profile(stairs, (0.0, 0.8))
    assert r.status in dk.GAP_STATUSES and r.status != "interior"
    assert r.evaluations <= dk.BUDGET

    def flat(phi, eta):  # flat profile: zero derivative is singular (A07)
        return np.array([phi - 0.5, -0.01 + 0 * eta]) + _NOISE

    assert dk.solve_profile(flat, (0.0, 0.8)).status == "ill-conditioned"


def test_nan_is_numerical_limit():
    def fn(phi, eta):
        return (
            np.full((M, 2), np.nan) if phi > 0.7 else linear_moments(0.6, 0.2)(phi, eta)
        )

    assert dk.solve_profile(fn, (0.0, 0.8)).status == "numerical-limit"


def test_budget_counting_and_exhaustion():
    calls = []

    def fn(phi, eta):
        calls.append((phi, eta))
        return linear_moments(0.6, 0.2)(phi, eta)

    r = dk.solve_profile(fn, (0.0, 0.8))
    assert r.evaluations == len(calls) == len(set(calls))  # cache hits are free
    assert (
        dk.solve_profile(linear_moments(0.6, 0.2), (0.0, 0.8), budget=5).status
        == "budget"
    )


def test_anchor_exact():
    def fn(phi, eta):
        return (
            np.zeros((M, 2))
            if (phi, eta) == (0.85, 0.0)
            else linear_moments(0.85, 0.0)(phi, eta)
        )

    r = dk.solve_profile(fn, (0.0, 0.8), anchor=(0.85, 0.0))
    assert r.status == "anchor-exact" and r.evaluations == 1
    # mean zero but not bytewise zero: never anchor-exact
    r2 = dk.solve_profile(linear_moments(0.85, 0.0), (0.0, 0.8), anchor=(0.85, 0.0))
    assert r2.status != "anchor-exact"


def test_one_parameter_family():
    r = dk.solve_profile(linear_moments(0.4, 0.0), None)
    assert r.status == "interior" and abs(r.phi - 0.4) < 1e-3
    assert (
        dk.solve_profile(linear_moments(1.3, 0.0), None).status == "family-limit-upper"
    )
    assert dk.solve_profile(linear_moments(0.0, 0.0), None).status == "boundary"


# ------------------------------------------------------------------ validation
def test_validation_rule_and_equivalence():
    v = dk.validate([4 * math.sqrt(2) * 1e-4 - 1e-12], [1e-4], [1e-4])
    assert v.passed
    assert not dk.validate([4 * math.sqrt(2) * 1e-4 + 1e-9], [1e-4], [1e-4]).passed
    assert not dk.validate([np.nan], [1e-4], [1e-4]).passed
    assert dk.validate([1e-4], [1e-5], [1e-5]).equivalence[0] == pytest.approx(
        1e-4 + 2.2414e-5
    )


def test_validation_false_failure_rate_under_correct_fit():
    rng = np.random.default_rng(1)
    se_fit, se_val = 1e-4, 0.71e-4
    res = rng.normal(0, math.hypot(se_fit, se_val), size=(20000, 2))
    rate = np.mean(
        [not dk.validate(r, [se_fit] * 2, [se_val] * 2).passed for r in res[:5000]]
    )
    old = np.mean(np.any(np.abs(res) > 4 * se_val, axis=1))
    assert rate < 0.002 and old > 0.03


def test_retry_protocol():
    def fit(attempt, m):
        fr = dk.FitResult("interior", 0.5, 0.1, 10, True, np.zeros(2), np.full(2, 1e-4))
        return fr

    bad = np.full((2048, 2), 1.0)
    good = np.tile([[1e-4], [-1e-4]], (1024, 2))
    out = dk.fit_with_retry(fit, lambda a, fr: bad if a == 0 else good)
    assert out["accepted"] and [x["M"] for x in out["attempts"]] == [1024, 4096]
    out = dk.fit_with_retry(fit, lambda a, fr: bad)
    assert out["status"] == "validation-failed" and len(out["attempts"]) == 2
    out = dk.fit_with_retry(lambda a, m: dk.FitResult("budget"), lambda a, fr: good)
    assert out["status"] == "budget" and len(out["attempts"]) == 1


# ------------------------------------------------------------------ nuisance
def test_fd_step_direction():
    assert dk.fd_step(0.5, 0.999) == 0.01 and dk.fd_step(0.995, 0.999) == -0.01
    J = dk.fd_jacobian(
        lambda t: np.array([2 * t[0] + t[1], t[1]]),
        np.array([0.995, 0.0]),
        np.array([0.999, 0.8]),
    )
    assert np.allclose(J, [[2, 1], [0, 1]])


def test_linearised_shift_zero_at_anchor_and_projection():
    rng = np.random.default_rng(0)
    diffs = rng.normal(0, 0.01, (M, 2))
    idx = rng.integers(0, M, (50, M))
    J = np.array([[1.0, 0.3], [0.1, 1.0]])
    lo, hi = np.array([0.0, 0.0]), np.array([0.999, 0.8])
    d0, p0 = dk.linearised_shifts(
        diffs, idx, J, np.array([0.85, 0.0]), lo, hi, anchor_exact=True
    )
    assert not d0.any() and not p0.any()
    d, p = dk.linearised_shifts(diffs, idx, J, np.array([0.5, 0.0]), lo, hi)
    gb = diffs[idx].mean(1)
    assert np.all(d[:, 1] >= 0)
    assert p.any()
    # projected draws keep L1 solved (L1 priority)
    l1 = gb[:, 0] + d @ J[0]
    assert np.allclose(l1[p], 0.0, atol=1e-15)
    free = ~p
    assert np.allclose(gb[free] + d[free] @ J.T, 0.0, atol=1e-15)


def test_nuisance_variance_matches_delta_method():
    rng = np.random.default_rng(2)
    diffs = rng.normal(0, 0.05, (M, 2))
    B = 2000
    idx = rng.integers(0, M, (B, M))
    J = np.array([[1.0, 0.3], [0.1, 1.0]])
    D = np.array([[1.0, 0.0], [0.5, 2.0]])
    lo, hi = np.array([0.0, 0.0]), np.array([0.999, 0.8])
    null_ref = np.zeros((4, 2))

    def auc_fn(ntr, ttr, nref, tref):  # linear functional of the null shift
        return float(nref[0, 0] + nref[0, 1])

    tr = np.zeros((10, 2, 2))
    res = dk.propagate_nuisance(
        diffs,
        idx,
        idx[:, :10] % 10,
        idx[:, :10] % 10,
        J,
        D,
        np.array([0.5, 0.4]),
        lo,
        hi,
        tr,
        tr,
        null_ref,
        null_ref,
        auc_fn,
    )
    a = np.array([1.0, 1.0]) @ D @ np.linalg.inv(J)
    expected = a @ np.cov(diffs, rowvar=False) @ a / M
    assert res.v_nuis == pytest.approx(expected, rel=0.1)
    assert res.projected_fraction == 0.0
    assert abs(res.deviations.mean()) < 1e-15


# ------------------------------------------------------------------ bootstrap
def _cluster_scores(rng, n, shift, icc):
    u = rng.normal(0, math.sqrt(icc), (n, 1))
    return u + rng.normal(0, math.sqrt(1 - icc), (n, 2)) + shift


def test_cluster_bootstrap_se_converges():
    rng = np.random.default_rng(3)
    n, reps, B = 150, 120, 200
    aucs, ses = [], []
    for _ in range(reps):
        t = _cluster_scores(rng, n, 0.5, 0.5)[:, :, None]
        z = _cluster_scores(rng, n, 0.0, 0.5)[:, :, None]
        it, iz = rng.integers(0, n, (B, n)), rng.integers(0, n, (B, n))
        ah, boot = dk.cluster_bootstrap_auc(t, z, it, iz)
        aucs.append(ah[0])
        ses.append(boot[:, 0].std(ddof=1))
    true_sd = np.std(aucs, ddof=1)
    assert np.mean(ses) == pytest.approx(true_sd, rel=0.2)


def test_bootstrap_identity_weights_equal_plain_auc():
    rng = np.random.default_rng(4)
    t, z = rng.normal(size=(30, 2, 3)), rng.normal(size=(30, 2, 3))
    t[0, 0, 0] = z[1, 1, 0]  # tie
    idx = np.arange(30)[None, :]
    ah, boot = dk.cluster_bootstrap_auc(t, z, idx, idx)
    assert np.allclose(ah, boot[0])
    s = t[:, :, 0].ravel()[:, None] - z[:, :, 0].ravel()[None, :]
    assert ah[0] == pytest.approx(np.mean((s > 0) + 0.5 * (s == 0)))


def test_se_total_no_division():
    assert dk.se_total(0.03, 0.0016) == pytest.approx(0.05)


# ------------------------------------------------------------------ band
def test_band_never_below_floor_and_endpoints():
    rng = np.random.default_rng(5)
    for scale in (0.0, 1e-4, 0.02):
        auc = np.array([0.5, 0.52, 0.6, 0.7, 0.8, 0.9, 1.0, 0.99, 0.0])
        boot = auc + rng.normal(0, scale, (500, 9))
        b = dk.band(auc, boot, np.zeros((500, 9)), np.zeros(9), np.ones(9, bool))
        assert b.critical >= dk.Z_FLOOR
        assert b.upper[6] == 1.0 and b.lower[8] == 0.0
        assert np.all(b.lower <= auc + 1e-15) and np.all(b.upper >= auc - 1e-15)


def _band(auc, avail=None, lo=None, hi=None):
    auc = np.asarray(auc, float)
    lo = auc - 0.05 if lo is None else np.asarray(lo)
    hi = auc + 0.05 if hi is None else np.asarray(hi)
    return dk.Band(auc, lo, hi, 2.7729, 2.0, False, np.zeros(9))


def test_inversion_and_gap_rules():
    auc = [0.5, 0.5, 0.52, 0.6, 0.66, 0.72, 0.8, 0.9, 0.95]
    out = dk.boundaries(_band(auc), np.ones(9, bool))
    assert (
        out["first_point"] == 0.10
        and out["first_ci_lower"] == 0.03
        and out["first_ci_upper"] == 0.30
    )
    assert out["sustained_point"] == 0.10 and out["unit_status"] == "completo válido"
    av = np.ones(9, bool)
    av[4] = False  # gap at a=0.03 hides the CI lower end and the point
    out = dk.boundaries(_band(auc), av)
    assert (
        out["first_ci_lower"] is None
        and out["first_ci_lower_reason"] == "gap at a=0.03"
    )
    assert out["first_point"] is None and out["sustained_point"] == 0.10
    av = np.ones(9, bool)
    av[8] = False  # top gap: sustained censored
    out = dk.boundaries(_band(auc), av)
    assert (
        out["sustained_point"] is None
        and out["sustained_point_reason"] == "gap at a=0.9"
    )
    assert out["first_point"] == 0.10


def test_null_gate_invalidates():
    auc = [0.6, 0.6, 0.62, 0.66, 0.7, 0.72, 0.8, 0.9, 0.95]
    out = dk.boundaries(_band(auc), np.ones(9, bool))  # 0.5 not in [0.55, 0.65]
    assert out["unit_status"] == "completo inválido" and out["first_point"] is None
    av = np.ones(9, bool)
    av[0] = False
    out = dk.boundaries(_band([0.5, *auc[1:]]), av)
    assert out["unit_status"] == "completo inválido"
    assert dk.null_gate(0.5, 0.6, True) and not dk.main_curve_valid(
        {0.5: True, 0.7: False}
    )


# ------------------------------------------------------- allowances / stop rule
def test_allowances():
    assert dk.g2_allowance_pass([5, 2, 2, 2, 1, 1, 1])
    assert not dk.g2_allowance_pass([5, 2, 2, 2, 2, 1, 1])  # 15 > 14
    assert not dk.g2_allowance_pass([6, 0, 0, 0, 0, 0, 0])
    assert dk.g2_allowance_pass([2, 2, 2, 2, 2, 2])  # 6 cells -> ceil(12)=12
    assert dk.g2c_allowance_pass(3, 2) and not dk.g2c_allowance_pass(4, 0)
    assert dk.fd_stability_pass([0.8, 1.3, 1.0]) and not dk.fd_stability_pass(
        [1.3, 1.3, 1.0]
    )


def _betabinom_cdf(k, n, a, b):
    lb = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    tot = 0.0
    for x in range(k + 1):
        lc = math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(n - x + 1)
        lbx = math.lgamma(x + a) + math.lgamma(n - x + b) - math.lgamma(n + a + b)
        tot += math.exp(lc + lbx - lb)
    return tot


@pytest.mark.parametrize("gaps", [0, 1, 3])
def test_jeffreys_exact_matches_closed_form_betabinomial(gaps):
    a, b = dk.jeffreys_posterior(gaps)
    # one cell: pooled allowance ceil(0.02*100)=2 binds
    assert dk.stop_rule_exact(gaps, n_cells=1, include_g2c=False) == pytest.approx(
        _betabinom_cdf(2, 100, a, b), rel=1e-8
    )


@pytest.mark.parametrize("gaps", [0, 1, 2])
def test_jeffreys_mc_matches_exact(gaps):
    exact = dk.stop_rule_exact(gaps)
    mc = dk.stop_rule_mc(gaps, sims=200_000, seed=11)
    assert abs(mc - exact) <= 4 * math.sqrt(exact * (1 - exact) / 200_000) + 1e-12
    assert dk.stop_before_g2(0.7999) and not dk.stop_before_g2(0.80)
