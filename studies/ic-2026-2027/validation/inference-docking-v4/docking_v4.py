"""Clean-room re-implementation of the v4 inference and calibration machinery.

Written only from the v4 specification documents (D1-D11, R1-R8, review
decisions 1-11, delta-review decisions 1-8 and the v4.3 amendment text).
It does not import or read project code. numpy only. See AMBIGUITIES.md for
every reading chosen where the specification is not explicit (tagged Axx).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------------------
# Constants fixed by the specification
# ---------------------------------------------------------------------------
BUDGET = 96  # item 11(c): evaluations actually executed per attempt
PHI_BOX = (0.0, 0.999)  # D2
FACE_PROBE = 0.01  # amendment v4.3: profile re-evaluated at eta=0.01
FD_STEP = 0.01  # D5/R3
FD_STEP_G2 = 0.005  # D5: G2 second step
Z_FLOOR = 2.7729  # D6 / v1: z_(1-0.05/18)
EQUIV_Z = 2.2414  # D4: A's equivalence statistic
EQUIV_LIMIT = 0.0003
VALIDATION_SIGMAS = 4.0  # R1
VALIDATION_PAIRS = 2048  # R1
FIT_M = 1024
RETRY_M = 4096
TARGET = 0.70
GRID = (0.0, 0.001, 0.003, 0.01, 0.03, 0.10, 0.30, 0.60, 0.90)

ACCEPTED = ("anchor-exact", "interior", "boundary")
GAP_STATUSES = (
    "no-L1-root",
    "non-monotone-profile",
    "ill-conditioned",
    "numerical-limit",
    "family-limit-lower",
    "family-limit-upper",
    "budget",
)


# ---------------------------------------------------------------------------
# Component 2: strict acceptance tolerance (R2)
# ---------------------------------------------------------------------------
def acceptance_tolerance(se: np.ndarray | float) -> np.ndarray:
    """min(5e-5, max(1e-6, 0.25*SE_fit,k)) per fitted moment (R2)."""
    se = np.asarray(se, dtype=float)
    return np.minimum(5e-5, np.maximum(1e-6, 0.25 * se))


def paired_se(diffs: np.ndarray) -> np.ndarray:
    """SE_k = sd(paired differences)/sqrt(M). A01: sample sd, ddof=1."""
    d = np.asarray(diffs, dtype=float)
    return d.std(axis=0, ddof=1) / math.sqrt(d.shape[0])


def accepts(gbar: np.ndarray, se: np.ndarray) -> np.ndarray:
    """Elementwise |gbar_k| <= tol_k (NaN never accepts)."""
    gbar = np.asarray(gbar, dtype=float)
    return np.abs(gbar) <= acceptance_tolerance(se)


# ---------------------------------------------------------------------------
# Component 1: profile solver (D4, R2, decisions 7 and 11, amendment v4.3)
# ---------------------------------------------------------------------------
class BudgetExhausted(Exception):
    pass


@dataclass
class Evaluation:
    gbar: np.ndarray
    se: np.ndarray
    exact_zero: bool
    finite: bool


class CountingEvaluator:
    """Wraps evaluate(phi, eta) -> paired differences (M, k).

    Counts evaluations actually executed; cache hits are free (amendment:
    "Avaliações reutilizadas do cache não consomem o orçamento novamente").
    """

    def __init__(self, fn: Callable[[float, float], np.ndarray], budget: int = BUDGET):
        self.fn = fn
        self.budget = budget
        self.count = 0
        self.cache: dict[tuple[float, float], Evaluation] = {}

    def __call__(self, phi: float, eta: float) -> Evaluation:
        key = (float(phi), float(eta))
        if key in self.cache:
            return self.cache[key]
        if self.count >= self.budget:
            raise BudgetExhausted
        self.count += 1
        d = np.asarray(self.fn(*key), dtype=float)
        if d.ndim == 1:
            d = d[:, None]
        finite = bool(np.all(np.isfinite(d)))
        gbar = d.mean(axis=0)
        se = paired_se(d) if d.shape[0] > 1 else np.full(d.shape[1], np.nan)
        ev = Evaluation(gbar, se, bool(finite and np.all(d == 0.0)), finite)
        self.cache[key] = ev
        return ev


@dataclass
class InnerResult:
    status: str  # "ok" | gap status
    phi: float = float("nan")
    stepped: bool = False
    endpoint: bool = False


class _Gap(Exception):
    def __init__(self, status: str):
        self.status = status


def _illinois(
    f: Callable[[float], tuple[float, bool]], a: float, fa: float, b: float, fb: float
):
    """Illinois false position with bisection safeguard on a sign-change bracket.

    f(x) -> (value, accepted). Returns the accepted iterate x (always a real
    step: never a or b). Degenerate secants (fa == fb) fall back to bisection.
    Raises _Gap("ill-conditioned") when the bracket collapses without an
    accepted value (A05).
    """
    side = 0
    for _ in range(200):
        if b - a <= 1e-12 * max(1.0, abs(a), abs(b)):
            raise _Gap("ill-conditioned")
        denom = fb - fa
        x = (
            b - fb * (b - a) / denom
            if denom != 0.0 and np.isfinite(denom)
            else 0.5 * (a + b)
        )
        # safeguard: keep the step strictly inside the bracket, else bisect
        lo, hi = a + 1e-3 * (b - a), b - 1e-3 * (b - a)
        if not (lo <= x <= hi):
            x = 0.5 * (a + b)
        fx, ok = f(x)
        if not np.isfinite(fx):
            raise _Gap("numerical-limit")
        if ok:
            return x
        if fx == 0.0:  # exact zero but tolerance unmet cannot happen; kept for safety
            raise _Gap("ill-conditioned")
        if np.sign(fx) == np.sign(fb):
            b, fb = x, fx
            if side == 1:
                fa *= 0.5
            side = 1
        else:
            a, fa = x, fx
            if side == -1:
                fb *= 0.5
            side = -1
    raise _Gap("ill-conditioned")


def solve_l1(ev: CountingEvaluator, eta: float, at_face: bool) -> InnerResult:
    """Solve L1 in phi on PHI_BOX at fixed eta.

    A03: L1 residual (null minus target) is expected to increase with phi;
    both ends above tolerance => target below family range (family-limit-lower),
    both below => family-limit-upper. When the solve is not on the eta face used
    for the family limits, a missing root is `no-L1-root`.
    """
    lo, hi = PHI_BOX
    e_lo, e_hi = ev(lo, eta), ev(hi, eta)
    if not (e_lo.finite and e_hi.finite):
        raise _Gap("numerical-limit")
    f_lo, f_hi = e_lo.gbar[0], e_hi.gbar[0]
    if accepts(f_lo, e_lo.se[0]):
        return InnerResult("ok", lo, stepped=False, endpoint=True)
    if accepts(f_hi, e_hi.se[0]):
        return InnerResult("ok", hi, stepped=False, endpoint=True)
    if np.sign(f_lo) == np.sign(f_hi):
        if not at_face:
            raise _Gap("no-L1-root")
        raise _Gap("family-limit-lower" if f_lo > 0 else "family-limit-upper")

    def f(x: float) -> tuple[float, bool]:
        e = ev(x, eta)
        if not e.finite:
            return float("nan"), False
        return float(e.gbar[0]), bool(accepts(e.gbar[0], e.se[0]))

    phi = _illinois(f, lo, f_lo, hi, f_hi)
    return InnerResult("ok", phi, stepped=True, endpoint=False)


@dataclass
class FitResult:
    status: str
    phi: float = float("nan")
    eta: float = float("nan")
    evaluations: int = 0
    stepped: bool = False
    gbar: np.ndarray | None = None
    se: np.ndarray | None = None
    diagnostics: dict = field(default_factory=dict)


def solve_profile(
    fn: Callable[[float, float], np.ndarray],
    eta_box: tuple[float, float] | None,
    *,
    fixed_eta: float = 0.0,
    anchor: tuple[float, float] | None = None,
    budget: int = BUDGET,
) -> FitResult:
    """Profile solver: fixed eta -> L1 in phi; then L2 in eta along the profile.

    eta_box=None means a one-parameter family (A, C, controls): solve only L1
    at `fixed_eta`; L2 (if returned) is a diagnostic.  `anchor` is given only
    for a=0 identity families: if every paired difference at the anchor is
    exactly zero the status is anchor-exact.
    """
    ev = CountingEvaluator(fn, budget)
    try:
        if anchor is not None:
            e = ev(*anchor)
            if e.exact_zero:
                return FitResult(
                    "anchor-exact", anchor[0], anchor[1], ev.count, False, e.gbar, e.se
                )
        if eta_box is None:
            inner = solve_l1(ev, fixed_eta, at_face=True)
            e = ev(inner.phi, fixed_eta)
            status = "interior" if inner.stepped else "boundary"
            return FitResult(
                status, inner.phi, fixed_eta, ev.count, inner.stepped, e.gbar, e.se
            )
        return _solve_two(ev, eta_box)
    except BudgetExhausted:
        return FitResult("budget", evaluations=ev.count)
    except _Gap as g:
        return FitResult(g.status, evaluations=ev.count)


def _solve_two(ev: CountingEvaluator, eta_box: tuple[float, float]) -> FitResult:
    e_lo_eta, e_hi_eta = eta_box
    profile: dict[float, float] = {}

    def h(eta: float, at_face: bool) -> tuple[float, InnerResult, Evaluation]:
        inner = solve_l1(ev, eta, at_face)
        e = ev(inner.phi, eta)
        if not e.finite:
            raise _Gap("numerical-limit")
        profile[eta] = float(e.gbar[1])
        _check_monotone(profile)
        return float(e.gbar[1]), inner, e

    def result(status, eta, inner, e, stepped):
        return FitResult(status, inner.phi, eta, ev.count, stepped, e.gbar, e.se)

    h0, in0, e0 = h(e_lo_eta, at_face=True)
    if accepts(h0, e0.se[1]):
        # endpoint accepted without a real outer step -> boundary (decision 7)
        return result("boundary", e_lo_eta, in0, e0, in0.stepped)
    if h0 > 0:
        # constrained solution on the lower face: profile must be non-decreasing
        # into the interior, verified by re-evaluation at eta=0.01 (A04)
        h1, _, _ = h(e_lo_eta + FACE_PROBE, at_face=False)
        if h1 >= h0:
            return result("boundary", e_lo_eta, in0, e0, in0.stepped)
        raise _Gap("non-monotone-profile")
    hH, inH, eH = h(e_hi_eta, at_face=False)
    if accepts(hH, eH.se[1]):
        return result("boundary", e_hi_eta, inH, eH, inH.stepped)
    if hH < 0:
        raise _Gap("family-limit-upper")

    best: dict = {}

    def f(eta: float) -> tuple[float, bool]:
        val, inner, e = h(eta, at_face=False)
        ok = bool(np.all(accepts(e.gbar[:2], e.se[:2])))
        if ok:
            best["r"] = (eta, inner, e)
        return val, ok

    _illinois(f, e_lo_eta, h0, e_hi_eta, hH)
    eta, inner, e = best["r"]
    return result("interior", eta, inner, e, True)


def _check_monotone(profile: dict[float, float]) -> None:
    """The profile is checked at every evaluated point (A06): strictly
    increasing; an exact tie is a singular derivative (ill-conditioned)."""
    etas = sorted(profile)
    vals = np.array([profile[x] for x in etas])
    d = np.diff(vals)
    if np.any(d < 0):
        raise _Gap("non-monotone-profile")
    if np.any(d == 0):
        raise _Gap("ill-conditioned")


# ---------------------------------------------------------------------------
# Component 3: independent validation, retry, equivalence (D4, R1)
# ---------------------------------------------------------------------------
@dataclass
class ValidationResult:
    passed: bool
    z: np.ndarray  # |res| / sqrt(SE_fit^2 + SE_val^2)
    equivalence: np.ndarray  # |res| + 2.2414 SE_val
    equivalence_pass: np.ndarray  # <= 0.0003 (reported only)


def validate(
    res: np.ndarray, se_fit: np.ndarray, se_val: np.ndarray
) -> ValidationResult:
    """Fail if |res_k| > 4 sqrt(SE_fit,k^2 + SE_val,k^2) on any fitted moment."""
    res, se_fit, se_val = (np.asarray(x, dtype=float) for x in (res, se_fit, se_val))
    scale = np.sqrt(se_fit**2 + se_val**2)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.abs(res) / scale
    fail = ~(np.abs(res) <= VALIDATION_SIGMAS * scale)  # NaN fails (A08)
    eq = np.abs(res) + EQUIV_Z * se_val
    return ValidationResult(bool(not np.any(fail)), z, eq, eq <= EQUIV_LIMIT)


def fit_with_retry(
    fit: Callable[[int, int], FitResult],
    validation_residuals: Callable[[int, FitResult], np.ndarray],
) -> dict:
    """Attempt 0 fits with M=1,024; a validation failure triggers exactly one
    retry with M=4,096 and its own budget, then a fresh validation.

    fit(attempt, M) -> FitResult; validation_residuals(attempt, fit) returns
    fresh-pair differences (2048, k) at theta-hat. A solver gap is final: no
    opportunistic restart (amendment). Both attempts are recorded.
    """
    attempts = []
    for attempt, m in ((0, FIT_M), (1, RETRY_M)):
        fr = fit(attempt, m)
        rec = {"attempt": attempt, "M": m, "fit": fr, "validation": None}
        attempts.append(rec)
        if fr.status not in ACCEPTED:
            return {"status": fr.status, "attempts": attempts, "accepted": False}
        if fr.status == "anchor-exact":
            return {"status": fr.status, "attempts": attempts, "accepted": True}
        d = np.asarray(validation_residuals(attempt, fr), dtype=float)
        if d.ndim == 1:
            d = d[:, None]
        k = d.shape[1]
        v = validate(d.mean(0), fr.se[:k], paired_se(d))
        rec["validation"] = v
        if v.passed:
            return {"status": fr.status, "attempts": attempts, "accepted": True}
    return {"status": "validation-failed", "attempts": attempts, "accepted": False}


# ---------------------------------------------------------------------------
# Component 4: local mean-shift nuisance propagation (D5, R3, decision 4)
# ---------------------------------------------------------------------------
def fd_step(theta: float, upper: float, step: float = FD_STEP) -> float:
    """Forward step, pointing inward at the upper face (A10)."""
    return step if theta + step <= upper else -step


def fd_jacobian(
    mean_fn: Callable[[np.ndarray], np.ndarray],
    theta: np.ndarray,
    upper: np.ndarray,
    step: float = FD_STEP,
) -> np.ndarray:
    """One-sided CRN finite differences, one stencil per parameter.

    mean_fn(theta) -> vector of means (moments or L3-L5 features) under CRN.
    Returns J[i, j] = d mean_i / d theta_j.
    """
    theta = np.asarray(theta, dtype=float)
    base = np.asarray(mean_fn(theta), dtype=float)
    cols = []
    for j in range(theta.size):
        h = fd_step(theta[j], upper[j], step)
        t = theta.copy()
        t[j] += h
        cols.append((np.asarray(mean_fn(t), dtype=float) - base) / h)
    return np.column_stack(cols)


def linearised_shifts(
    diffs: np.ndarray,
    idx: np.ndarray,
    J: np.ndarray,
    theta_hat: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    anchor_exact: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Delta-theta_b from resampled (uncentred) matching differences.

    diffs (M, k) matching paired differences at theta-hat; idx (B, M) resample
    indices. Two-parameter: theta=(phi, eta), J (2x2) of (L1, L2) wrt (phi, eta).
    One-parameter: theta=(phi,), J (1x1) from L1. Projection replicates the
    solver's rule: when eta leaves the box, eta is set to the face and L1 is
    re-solved linearly in phi (L1 priority); phi is then clipped (A11).
    Returns (dtheta (B, p), projected (B,) bool).
    """
    theta_hat = np.asarray(theta_hat, dtype=float)
    p = theta_hat.size
    B = idx.shape[0]
    if anchor_exact:
        return np.zeros((B, p)), np.zeros(B, dtype=bool)
    gb = np.asarray(diffs, dtype=float)[idx].mean(axis=1)[:, :p]  # uncentred
    J = np.asarray(J, dtype=float)[:p, :p]
    dth = -np.linalg.solve(J, gb.T).T
    projected = np.zeros(B, dtype=bool)
    if p == 2:
        eta = theta_hat[1] + dth[:, 1]
        for face, mask in ((lower[1], eta < lower[1]), (upper[1], eta > upper[1])):
            if np.any(mask):
                deta = face - theta_hat[1]
                dth[mask, 1] = deta
                dth[mask, 0] = -(gb[mask, 0] + J[0, 1] * deta) / J[0, 0]
                projected |= mask
    phi = theta_hat[0] + dth[:, 0]
    clip = (phi < lower[0]) | (phi > upper[0])
    dth[:, 0] = np.clip(phi, lower[0], upper[0]) - theta_hat[0]
    projected |= clip
    return dth, projected


def auc_half_ties(pos: np.ndarray, neg: np.ndarray, wpos=None, wneg=None) -> float:
    """Weighted Mann-Whitney AUC with half credit for ties."""
    pos = np.asarray(pos, float).ravel()
    neg = np.asarray(neg, float).ravel()
    wpos = np.ones_like(pos) if wpos is None else np.asarray(wpos, float).ravel()
    wneg = np.ones_like(neg) if wneg is None else np.asarray(wneg, float).ravel()
    order = np.argsort(neg, kind="mergesort")
    sn, sw = neg[order], wneg[order]
    cw = np.concatenate([[0.0], np.cumsum(sw)])
    left = cw[np.searchsorted(sn, pos, side="left")]
    right = cw[np.searchsorted(sn, pos, side="right")]
    num = np.sum(wpos * (left + 0.5 * (right - left)))
    return float(num / (wpos.sum() * wneg.sum()))


def lda_auc(train0, train1, ref0, ref1, shrink: float = 0.8) -> float:
    """Reference discriminator for self-tests (not under comparison, A12):
    standardise on training, covariance 0.8 S + 0.2 I, LDA direction, AUC
    of class-1 vs class-0 reference scores with half-credit ties."""
    X = np.vstack([train0, train1])
    mu, sd = X.mean(0), X.std(0, ddof=1)
    sd = np.where(sd > 0, sd, 1.0)
    z0, z1 = (train0 - mu) / sd, (train1 - mu) / sd
    S = 0.5 * (np.cov(z0, rowvar=False) + np.cov(z1, rowvar=False))
    S = np.atleast_2d(S)
    C = shrink * S + (1 - shrink) * np.eye(S.shape[0])
    w = np.linalg.solve(C, z1.mean(0) - z0.mean(0))
    s0 = ((ref0 - mu) / sd) @ w
    s1 = ((ref1 - mu) / sd) @ w
    return auc_half_ties(s1, s0)


@dataclass
class NuisanceResult:
    v_nuis: float
    deviations: np.ndarray  # centred AUC_b - mean(AUC_b), aligned for max-t
    auc_draws: np.ndarray
    mean_shift: float
    mcse_v: float
    projected_fraction: float
    dtheta: np.ndarray


def nuisance_variance(
    auc_draws: np.ndarray, auc0: float
) -> tuple[float, np.ndarray, float, float]:
    """V_nuis = centred variance of AUC_b (A13: ddof=1), no division by B.
    MCSE of V via the fourth central moment: sqrt((m4 - v^2)/B)."""
    a = np.asarray(auc_draws, float)
    dev = a - a.mean()
    v = float(dev.var(ddof=1))
    m4 = float(np.mean(dev**4))
    mcse = math.sqrt(max(m4 - float(np.mean(dev**2)) ** 2, 0.0) / a.size)
    return v, dev, float(np.mean(a - auc0)), mcse


def propagate_nuisance(
    diffs: np.ndarray,
    match_idx: np.ndarray,
    train_idx0: np.ndarray,
    train_idx1: np.ndarray,
    J: np.ndarray,
    D: np.ndarray,
    theta_hat: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    null_train: np.ndarray,
    target_train: np.ndarray,
    null_ref: np.ndarray,
    target_ref: np.ndarray,
    auc_fn: Callable = lda_auc,
    anchor_exact: bool = False,
    null_class: int = 0,
) -> NuisanceResult:
    """D5 with R3 mean-shift. Training arrays are (n_networks, 2, f): the two
    events of a network are resampled together; classes separately.
    Reference arrays are (n_ref_events, f), fixed. D (f x p) is the Jacobian
    of mean L3-L5 features wrt theta."""
    B = match_idx.shape[0]
    if anchor_exact:
        p = np.asarray(theta_hat).size
        return NuisanceResult(
            0.0, np.zeros(B), np.full(B, np.nan), 0.0, 0.0, 0.0, np.zeros((B, p))
        )
    dth, proj = linearised_shifts(diffs, match_idx, J, theta_hat, lower, upper)
    shift = dth @ np.asarray(D, float).T  # (B, f)
    f = null_train.shape[-1]
    t0_all = target_train.reshape(-1, f)
    auc0 = auc_fn(null_train.reshape(-1, f), t0_all, null_ref, target_ref)
    out = np.empty(B)
    for b in range(B):
        n_tr = null_train[train_idx0[b]].reshape(-1, f) + shift[b]
        t_tr = target_train[train_idx1[b]].reshape(-1, f)
        out[b] = auc_fn(n_tr, t_tr, null_ref + shift[b], target_ref)
    v, dev, ms, mcse = nuisance_variance(out, auc0)
    return NuisanceResult(v, dev, out, ms, mcse, float(proj.mean()), dth)


# ---------------------------------------------------------------------------
# Component 5: cluster bootstrap on fixed scores, SE_total
# ---------------------------------------------------------------------------
def cluster_bootstrap_auc(
    target: np.ndarray, null: np.ndarray, idx_t: np.ndarray, idx_n: np.ndarray
):
    """target/null scores (n_networks, 2, S); idx_* (B, n) network indices,
    drawn separately per class, shared across all S slots.
    Returns (auc_hat (S,), auc_boot (B, S))."""
    n_t, e_t, S = target.shape
    n_n = null.shape[0]
    auc_hat = np.array(
        [auc_half_ties(target[:, :, s], null[:, :, s]) for s in range(S)]
    )
    B = idx_t.shape[0]
    boot = np.empty((B, S))
    for b in range(B):
        wt = np.bincount(idx_t[b], minlength=n_t).astype(float)
        wn = np.bincount(idx_n[b], minlength=n_n).astype(float)
        wt2 = np.repeat(wt, e_t)
        wn2 = np.repeat(wn, null.shape[1])
        for s in range(S):
            boot[b, s] = auc_half_ties(
                target[:, :, s].ravel(), null[:, :, s].ravel(), wt2, wn2
            )
    return auc_hat, boot


def se_total(se_scores: np.ndarray, v_nuis: np.ndarray) -> np.ndarray:
    """SE_total^2 = SE_scores^2 + V_nuis, with no division."""
    return np.sqrt(np.asarray(se_scores, float) ** 2 + np.asarray(v_nuis, float))


# ---------------------------------------------------------------------------
# Component 6: band, inversion, gap/censoring rules, a=0 gate
# ---------------------------------------------------------------------------
def _logit(p):
    return np.log(p) - np.log1p(-p)


def _expit(x):
    return 1.0 / (1.0 + np.exp(-x))


@dataclass
class Band:
    auc: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    critical: float
    empirical_max_t: float
    exceeds_floor: bool
    se_total: np.ndarray


def band(
    auc_hat: np.ndarray,
    boot: np.ndarray,
    nuis_dev: np.ndarray,
    v_nuis: np.ndarray,
    available: np.ndarray,
    n: int = 2000,
    level: float = 0.95,
) -> Band:
    """Per-r simultaneous band over available strengths (delta decision 1).

    logit studentisation, eps = 1/(2n), SE_logit = max(SE_total, eps)/(p(1-p))
    with p clipped to [eps, 1-eps]; critical = max(q_0.95 of max_s |t|, 2.7729).
    Bootstrap draws carry the same centred nuisance deviations (B, S)."""
    auc_hat = np.asarray(auc_hat, float)
    avail = np.asarray(available, bool) & np.isfinite(auc_hat)
    eps = 1.0 / (2 * n)
    se_sc = boot.std(axis=0, ddof=1)  # A14
    se_tot = se_total(se_sc, v_nuis)
    pc = np.clip(auc_hat, eps, 1 - eps)
    se_l = np.maximum(se_tot, eps) / (pc * (1 - pc))
    star = np.clip(boot + nuis_dev, eps, 1 - eps)
    t = np.abs(_logit(star) - _logit(pc)) / se_l
    tmax = np.max(t[:, avail], axis=1) if avail.any() else np.zeros(boot.shape[0])
    q = float(np.quantile(tmax, level))  # A15: numpy default (linear)
    c = max(q, Z_FLOOR)
    lo = _expit(_logit(pc) - c * se_l)
    hi = _expit(_logit(pc) + c * se_l)
    lo = np.where(auc_hat == 0.0, 0.0, lo)
    hi = np.where(auc_hat == 1.0, 1.0, hi)
    lo = np.where(avail, lo, np.nan)
    hi = np.where(avail, hi, np.nan)
    return Band(auc_hat, lo, hi, c, q, q > Z_FLOOR, se_tot)


def null_gate(lower0: float, upper0: float, available0: bool) -> bool:
    """Per-run a=0 gate: band at a=0 must contain 0.5 (inclusive). An
    infeasible/unmatched a=0 cell also fails."""
    if not available0 or not (np.isfinite(lower0) and np.isfinite(upper0)):
        return False
    return bool(lower0 <= 0.5 <= upper0)


def _first(values, avail, grid, first_gap_idx, target):
    """First available index with value >= target, declared only before the
    first gap (A17: strictly before it in grid order)."""
    for i, v in enumerate(values):
        if first_gap_idx is not None and i >= first_gap_idx:
            return None, f"gap at a={grid[first_gap_idx]:g}"
        if v >= target:
            return grid[i], None
    return None, "not reached"


def _sustained(values, avail, grid, last_gap_idx, target):
    """min a such that every a' >= a is available with value >= target;
    declared only above the last gap."""
    S = len(grid)
    best = None
    for i in range(S - 1, -1, -1):
        if not avail[i] or not (values[i] >= target):
            break
        best = i
    if best is None:
        if last_gap_idx is not None and last_gap_idx == S - 1:
            return None, f"gap at a={grid[last_gap_idx]:g}"
        return None, "not reached"
    return grid[best], None


def boundaries(
    b: Band, available: np.ndarray, grid=GRID, target: float = TARGET
) -> dict:
    """Inversion (inclusive): point = first AUC >= target; CI lower = first
    upper-band >= target; CI upper = first lower-band >= target. Same for the
    sustained boundary. Gap and censoring rules per delta decision 1; the a=0
    gate decides unit validity."""
    avail = np.asarray(available, bool)
    gaps = [i for i in range(len(grid)) if not avail[i]]
    fg = gaps[0] if gaps else None
    lg = gaps[-1] if gaps else None
    out: dict = {}
    for name, vals in (("point", b.auc), ("ci_lower", b.upper), ("ci_upper", b.lower)):
        v = np.where(avail, vals, np.nan)
        out[f"first_{name}"], out[f"first_{name}_reason"] = _first(
            v, avail, grid, fg, target
        )
        out[f"sustained_{name}"], out[f"sustained_{name}_reason"] = _sustained(
            v, avail, grid, lg, target
        )
    gate = null_gate(b.lower[0], b.upper[0], bool(avail[0]))
    out["null_gate"] = gate
    out["unit_status"] = "completo válido" if gate else "completo inválido"
    if not gate:  # invalid run: boundaries suppressed
        for k in list(out):
            if k.startswith(("first_", "sustained_")) and not k.endswith("_reason"):
                out[k] = None
    lo = np.where(avail, b.lower, np.nan)
    hi = np.where(avail, b.upper, np.nan)
    out["band_decrease_flag"] = bool(
        np.any(np.diff(lo[np.isfinite(lo)]) < 0)
        or np.any(np.diff(hi[np.isfinite(hi)]) < 0)
    )
    return out


def main_curve_valid(b_null_gates: dict[float, bool]) -> bool:
    """B failing the a=0 gate at any eligible r blocks main-curve validation."""
    return all(b_null_gates.values())


# ---------------------------------------------------------------------------
# Component 7: gate failure allowances and the Jeffreys stop rule
# ---------------------------------------------------------------------------
def g2_allowance_pass(failures_per_cell: list[int], per_cell: int = 100) -> bool:
    pipelines = per_cell * len(failures_per_cell)
    pooled = math.ceil(0.02 * pipelines)
    return all(f <= 5 for f in failures_per_cell) and sum(failures_per_cell) <= pooled


def g2c_allowance_pass(f100: int, f40: int) -> bool:
    return f100 <= 3 and f40 <= 2


def fd_stability_pass(ratios: np.ndarray) -> bool:
    """Per-cell aggregate: median V_nuis(0.005)/V_nuis(0.01) in [0.8, 1.25]."""
    m = float(np.median(np.asarray(ratios, float)))
    return 0.8 <= m <= 1.25


def jeffreys_posterior(gaps: int, fits: int = 54) -> tuple[float, float]:
    return 0.5 + gaps, 0.5 + fits - gaps


def stop_rule_mc(
    gaps: int,
    fits: int = 54,
    n_cells: int = 7,
    sims: int = 100_000,
    seed: int = 0,
    include_g2c: bool = True,
) -> float:
    """Posterior predictive P(G2 and G2c meet all allowances), beta-binomial
    by simulation: one failure rate per simulated world shared by every G2
    cell and both G2c refit sets (A20)."""
    rng = np.random.default_rng(seed)
    a, b = jeffreys_posterior(gaps, fits)
    p = rng.beta(a, b, size=sims)
    cells = rng.binomial(100, p[:, None], size=(sims, n_cells))
    pooled = math.ceil(0.02 * 100 * n_cells)
    ok = (cells <= 5).all(1) & (cells.sum(1) <= pooled)
    if include_g2c:
        ok &= rng.binomial(100, p) <= 3
        ok &= rng.binomial(40, p) <= 2
    return float(ok.mean())


def _log_binom_pmf(n: int, p: np.ndarray) -> np.ndarray:
    k = np.arange(n + 1)
    lc = np.array(
        [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) for i in k]
    )
    with np.errstate(divide="ignore"):
        return (
            lc[None, :]
            + k[None, :] * np.log(p[:, None])
            + (n - k)[None, :] * np.log1p(-p[:, None])
        )


def stop_rule_exact(
    gaps: int,
    fits: int = 54,
    n_cells: int = 7,
    nodes: int = 4000,
    include_g2c: bool = True,
) -> float:
    """Deterministic reference: integrate the conditional joint pass
    probability over the Beta posterior (Gauss-Jacobi via substitution
    p = sin^2(u), which removes the Jeffreys endpoint singularities)."""
    a, b = jeffreys_posterior(gaps, fits)
    x, w = np.polynomial.legendre.leggauss(nodes)
    u = (x + 1) * (math.pi / 4)  # u in (0, pi/2)
    wu = w * (math.pi / 4)
    p = np.sin(u) ** 2
    # density of p ~ Beta(a,b) times dp/du = 2 sin u cos u
    logB = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    dens = (
        np.exp((a - 1) * np.log(p) + (b - 1) * np.log1p(-p) - logB)
        * 2
        * np.sin(u)
        * np.cos(u)
    )
    pooled = math.ceil(0.02 * 100 * n_cells)
    kmax = min(5, pooled)
    pm = np.exp(_log_binom_pmf(100, p))[:, : kmax + 1]  # cell counts 0..5
    # convolve n_cells truncated cells, keep sums <= pooled
    dist = np.zeros((p.size, pooled + 1))
    dist[:, 0] = 1.0
    for _ in range(n_cells):
        new = np.zeros_like(dist)
        for k in range(kmax + 1):
            new[:, k:] += dist[:, : pooled + 1 - k] * pm[:, k : k + 1]
        dist = new
    g2 = dist.sum(1)
    g2c = np.ones_like(p)
    if include_g2c:
        g2c = np.exp(_log_binom_pmf(100, p))[:, :4].sum(1) * np.exp(
            _log_binom_pmf(40, p)
        )[:, :3].sum(1)
    return float(np.sum(wu * dens * g2 * g2c))


def stop_before_g2(probability: float) -> bool:
    return probability < 0.80
