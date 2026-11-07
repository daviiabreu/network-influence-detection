"""Invariant tests for the clean-room docking implementation."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dockv4 import model as m
from dockv4 import stats as st
from dockv4.pipeline import Matcher, match
from dockv4.seeds import Streams, seed

NS = "ic-detection-boundary-v4-docking-test"
N = 600


def streams(i: int, phase: str = "match") -> Streams:
    return Streams(NS, 0, phase, i, i)


def test_confirmatory_namespace_refused():
    with pytest.raises(ValueError):
        seed("ic-detection-boundary-v4-confirmatory", 0, "test", "state", 0)
    with pytest.raises(ValueError):
        seed("ic-detection-boundary-v4-docking-confirmatory", 0, "x", "state", 0)


def test_rank_transport_is_standardised_and_rank_preserving():
    u = np.random.default_rng(1).standard_normal(1002) ** 3
    z = m.rank_transport(u)
    assert abs(z.mean()) < 1e-12 and abs(z.var() - 1) < 1e-12
    assert np.array_equal(np.argsort(u), np.argsort(z))
    np.testing.assert_array_equal(m.rank_transport(z), z)  # idempotent


@pytest.mark.parametrize("r", [0.5, 0.7, 0.9])
def test_a_zero_social_equals_null_a_pathwise(r):
    social = m.Cell("social", r, a=0.0)
    for fam, eta in (("A", 0.0), ("B", 0.0), ("E", 0.0), ("D", 0.0)):
        null = m.Cell(fam, r, phi=0.85, eta=eta)
        p1 = m.panel(social, N, streams(3))
        p0 = m.panel(null, N, streams(3))
        for key in ("z", "mask", "y"):
            np.testing.assert_array_equal(p1[key], p0[key], err_msg=f"{fam} {key}")


def test_a_zero_is_exchangeable_in_distribution():
    """a=0 vs A(0.85) on independent seeds: LDA AUC averages to ~0.5."""
    social, null = m.Cell("social", 0.7, a=0.0), m.Cell("A", 0.7)
    aucs = []
    for rep in range(6):
        f1 = np.array(
            [
                st.lag_features(
                    m.panel(social, 300, Streams(NS, rep, "train", 2 * i + 1, i))["y"]
                )[2:5]
                for i in range(60)
            ]
        )
        f0 = np.array(
            [
                st.lag_features(
                    m.panel(null, 300, Streams(NS, rep, "train", 2 * i, i))["y"]
                )[2:5]
                for i in range(60)
            ]
        )
        mdl = st.lda_fit(f1[:30], f0[:30])
        aucs.append(st.auc(st.lda_score(mdl, f1[30:]), st.lda_score(mdl, f0[30:])))
    assert abs(np.mean(aucs) - 0.5) < 0.1


@pytest.mark.parametrize("r", [0.5, 0.7, 0.9])
def test_reliability_is_signal_variance_ratio(r):
    rng = np.random.default_rng(7)
    z = rng.standard_normal((200_000, 2))
    z[:, 1] = 0.6 * z[:, 0] + 0.8 * z[:, 1]
    w = m.measured(z, r, rng)
    assert abs(np.var(np.sqrt(r) * z[:, 0]) / np.var(w[:, 0]) - r) < 0.01
    # continuous-channel attenuation corr(w_t, w_s) = r corr(z_t, z_s)
    assert abs(np.corrcoef(w.T)[0, 1] - r * 0.6) < 0.01


def test_c_error_scale_has_unit_second_moment():
    x = np.linspace(-12, 12, 200_001)
    dens = np.exp(-(x**2) / 2) / np.sqrt(2 * np.pi)
    assert abs(np.trapezoid(m.c_error_scale(x) ** 2 * dens, x) - 1) < 1e-8


def test_geometry_and_retention():
    n = 10_626
    entry = m.entry_waves(n)
    assert (entry == 0).sum() == 7084 and (entry == 5).sum() == 3542
    mask = m.panel_mask(n, np.random.default_rng(2))
    assert np.array_equal(mask[::2], mask[1::2])  # households
    assert mask[:, 0].sum() == 7084
    hh = mask[::2]
    stay = hh[:, 1:5].sum() / hh[:, 0:4].sum()
    assert abs(stay - 0.89) < 0.01
    first_obs = np.argmax(mask, axis=1)
    assert np.array_equal(first_obs, entry)
    # monotone attrition: once out, never back
    assert not np.any(np.diff(mask[entry == 0].astype(int), axis=1) > 0)


def test_equiprobable_categories_and_c_marginal():
    p = m.panel(m.Cell("A", 0.7), N, streams(1))
    for t in range(m.N_WAVES):
        counts = np.bincount(
            p["y"][~np.isnan(p["y"][:, t]), t].astype(int), minlength=11
        )
        assert counts.max() - counts.min() <= 1
    pc = m.panel(m.Cell("C", 0.7), 6000, streams(2))
    y0 = pc["y"][~np.isnan(pc["y"][:, 0]), 0]
    assert abs(np.mean(y0 == 5) - (0.1 + 0.9 / 11)) < 0.002


def test_auc_basics():
    assert st.auc(np.array([2.0, 3.0]), np.array([0.0, 1.0])) == 1.0
    assert st.auc(np.array([1.0]), np.array([1.0])) == 0.5
    rng = np.random.default_rng(3)
    vals = [
        st.auc(rng.standard_normal(200), rng.standard_normal(200)) for _ in range(300)
    ]
    assert abs(np.mean(vals) - 0.5) < 0.01


def test_lda_matches_closed_form():
    rng = np.random.default_rng(4)
    x1 = rng.standard_normal((50, 3)) + np.array([0.5, 0, 0])
    x0 = rng.standard_normal((40, 3))
    mdl = st.lda_fit(x1, x0)
    x = np.vstack([x1, x0])
    z1 = (x1 - x.mean(0)) / x.std(0, ddof=1)
    z0 = (x0 - x.mean(0)) / x.std(0, ddof=1)
    s = (np.cov(z1.T) * 49 + np.cov(z0.T) * 39) / 88
    w = np.linalg.solve(0.8 * s + 0.2 * np.eye(3), z1.mean(0) - z0.mean(0))
    np.testing.assert_allclose(mdl["w"], w)
    assert mdl["w"][0] > 0


def test_social_changes_law_when_a_positive():
    p0 = m.panel(m.Cell("social", 0.9, a=0.0), N, streams(5))
    p1 = m.panel(m.Cell("social", 0.9, a=0.3), N, streams(5))
    assert not np.array_equal(p0["z"], p1["z"])
    np.testing.assert_array_equal(p0["mask"], p1["mask"])


def test_matching_recovers_anchor_at_a_zero():
    mt = Matcher(m.Cell("social", 0.7, a=0.0), "A", 300, 16, NS)
    fit = match(mt)
    assert fit["status"] == "interior"
    assert abs(fit["phi"] - 0.85) < 0.02
