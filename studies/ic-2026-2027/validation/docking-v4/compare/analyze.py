"""Pre-declared statistics for the docking comparison (needs scipy).

Usage: PYTHON_WITH_SCIPY analyze.py --raw DIR --out validation/docking-v4/results
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "src"))

from dockv4 import stats as ds  # noqa: E402
from run_all import (  # noqa: E402
    C_CELLS,
    SUMMARY_NAMES,
    TEST_NETS,
    TRAIN_NETS,
    cell_id,
    cells_b,
)

PRIMARY = ["L1", "L2", "L3", "L4", "L5", "n_obs_total"]
MARGIN_D = 0.20
MARGIN_AUC = 0.02
ALPHA = 0.05


def welch(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Return (diff, se, df)."""
    vx, vy = x.var(ddof=1) / x.size, y.var(ddof=1) / y.size
    se = np.sqrt(vx + vy)
    df = (vx + vy) ** 2 / (vx**2 / (x.size - 1) + vy**2 / (y.size - 1))
    return float(x.mean() - y.mean()), float(se), float(df)


def tost(x: np.ndarray, y: np.ndarray, margin: float) -> float:
    diff, se, df = welch(x, y)
    p_low = stats.t.sf((diff + margin) / se, df)
    p_up = stats.t.cdf((diff - margin) / se, df)
    return float(max(p_low, p_up))


def pooled_sd(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.sqrt((x.var(ddof=1) + y.var(ddof=1)) / 2))


def holm(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals)
    order = np.argsort(p)
    m = p.size
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()


def analyse(raw: Path, out: Path) -> None:
    secondary: list[dict] = []  # Holm family
    summary_rows: list[dict] = []
    primary_rows: list[dict] = []
    matrix_rows: list[dict] = []
    for kind in cells_b():
        cid = cell_id(kind)
        dock = np.load(raw / f"B_{cid}_dock.npy")
        proj = np.load(raw / f"B_{cid}_project.npy")
        cols = {name: i for i, name in enumerate(SUMMARY_NAMES)}
        for name, i in cols.items():
            x, y = dock[:, i], proj[:, i]
            ok_x, ok_y = x[np.isfinite(x)], y[np.isfinite(y)]
            row = {
                "cell": cid,
                "summary": name,
                "mean_dock": ok_x.mean(),
                "mean_project": ok_y.mean(),
                "sd_dock": ok_x.std(ddof=1),
                "sd_project": ok_y.std(ddof=1),
            }
            if row["sd_dock"] == 0 and row["sd_project"] == 0:
                row.update(
                    d=0.0,
                    p_welch=np.nan,
                    note="constant; equal"
                    if row["mean_dock"] == row["mean_project"]
                    else "constant; DIFFERENT",
                )
            else:
                diff, se, df = welch(ok_x, ok_y)
                sd = pooled_sd(ok_x, ok_y)
                p = float(2 * stats.t.sf(abs(diff / se), df))
                row.update(d=diff / sd, p_welch=p, note="")
                secondary.append(
                    {
                        "test": "welch",
                        "cell": cid,
                        "summary": name,
                        "p": p,
                        "effect": diff / sd,
                    }
                )
            summary_rows.append(row)
        for k in (1, 3, 5):
            i = cols[f"L{k}"]
            ks = stats.ks_2samp(dock[:, i], proj[:, i])
            secondary.append(
                {
                    "test": "ks",
                    "cell": cid,
                    "summary": f"L{k}",
                    "p": float(ks.pvalue),
                    "effect": float(ks.statistic),
                }
            )
        for k in range(1, 6):
            i = cols[f"L{k}"]
            bf = stats.levene(dock[:, i], proj[:, i], center="median")
            ratio = dock[:, i].var(ddof=1) / proj[:, i].var(ddof=1)
            secondary.append(
                {
                    "test": "brown-forsythe",
                    "cell": cid,
                    "summary": f"L{k}",
                    "p": float(bf.pvalue),
                    "effect": float(ratio),
                }
            )
        # primary TOST
        n_idx = [cols[f"n_obs_{t}"] for t in range(11)]
        prim = {
            f"L{k}": (dock[:, cols[f"L{k}"]], proj[:, cols[f"L{k}"]])
            for k in range(1, 6)
        }
        prim["n_obs_total"] = (dock[:, n_idx].sum(1), proj[:, n_idx].sum(1))
        for name in PRIMARY:
            x, y = prim[name]
            sd = pooled_sd(x, y)
            p = tost(x, y, MARGIN_D * sd)
            primary_rows.append(
                {
                    "cell": cid,
                    "endpoint": name,
                    "mean_dock": x.mean(),
                    "mean_project": y.mean(),
                    "diff": x.mean() - y.mean(),
                    "pooled_sd": sd,
                    "d": (x.mean() - y.mean()) / sd,
                    "margin_abs": MARGIN_D * sd,
                    "p_tost": p,
                    "equivalent": bool(p < ALPHA),
                }
            )
        corr_idx = [i for n, i in cols.items() if n.startswith("corr_")]
        md = np.nanmean(dock[:, corr_idx], 0) - np.nanmean(proj[:, corr_idx], 0)
        matrix_rows.append(
            {
                "cell": cid,
                "max_abs_delta": float(np.abs(md).max()),
                "frobenius_delta": float(np.sqrt(2 * (md**2).sum())),
            }
        )

    # part C
    with open(out / "partC-auc.csv") as fh:
        auc_rows = list(csv.DictReader(fh))
    auc_summary = []
    cross = []
    for c in C_CELLS:
        a = {
            impl: np.array(
                [
                    float(r["auc"])
                    for r in auc_rows
                    if r["cell"] == c["id"] and r["impl"] == impl
                ]
            )
            for impl in ("dock", "project")
        }
        x, y = a["dock"], a["project"]
        diff, se, df = welch(x, y)
        p = float(2 * stats.t.sf(abs(diff / se), df))
        ks = stats.ks_2samp(x, y)
        bf = stats.levene(x, y, center="median")
        for test, pv, eff in (
            ("welch", p, diff / pooled_sd(x, y)),
            ("ks", ks.pvalue, ks.statistic),
            ("brown-forsythe", bf.pvalue, x.var(ddof=1) / y.var(ddof=1)),
        ):
            secondary.append(
                {
                    "test": test,
                    "cell": c["id"],
                    "summary": "AUC",
                    "p": float(pv),
                    "effect": float(eff),
                }
            )
        auc_summary.append(
            {
                "cell": c["id"],
                "a": c["a"],
                "r": c["r"],
                "null": c["null"],
                "mean_dock": x.mean(),
                "mean_project": y.mean(),
                "sd_dock": x.std(ddof=1),
                "sd_project": y.std(ddof=1),
                "diff": diff,
                "p_tost_0.02": tost(x, y, MARGIN_AUC),
                "frac_ge_0.70_dock": float(np.mean(x >= 0.70)),
                "frac_ge_0.70_project": float(np.mean(y >= 0.70)),
            }
        )
        # same features, two LDA/AUC implementations
        from ic_study.analysis.detection_boundary import auc as p_auc
        from ic_study.analysis.redesign import fit_discriminant

        worst = 0.0
        for impl in ("dock", "project"):
            for rep in range(len(x)):
                f = np.load(raw / f"C_{c['id']}_{impl}_{rep:03d}.npy")
                n_tr, n_te = 2 * TRAIN_NETS, 2 * TEST_NETS  # rows: tr1 tr0 te1 te0
                tr1, tr0, te1, te0 = np.split(f, np.cumsum([n_tr, n_tr, n_te]))
                mdl = ds.lda_fit(tr1, tr0)
                mine = ds.auc(ds.lda_score(mdl, te1), ds.lda_score(mdl, te0))
                pm = fit_discriminant(
                    np.concatenate([tr0, tr1]), np.repeat([0, 1], n_tr)
                )
                theirs = p_auc(pm.score(te0), pm.score(te1))
                worst = max(worst, abs(mine - theirs))
        cross.append({"cell": c["id"], "max_abs_auc_diff_same_features": worst})

    adj = holm([s["p"] for s in secondary])
    for s, pa in zip(secondary, adj, strict=True):
        s["p_holm"] = pa
    rejected = [s for s in secondary if s["p_holm"] < ALPHA]

    def write(name: str, rows: list[dict]) -> None:
        with open(out / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            for r in rows:
                w.writerow(
                    {
                        k: (f"{v:.6g}" if isinstance(v, float) else v)
                        for k, v in r.items()
                    }
                )

    write("partB-summaries.csv", summary_rows)
    write("partB-primary-tost.csv", primary_rows)
    write("partB-wave-corr.csv", matrix_rows)
    write("partC-auc-summary.csv", auc_summary)
    write("secondary-tests-holm.csv", secondary)
    verdict = {
        "primary_endpoints": len(primary_rows),
        "primary_equivalent": sum(r["equivalent"] for r in primary_rows),
        "primary_not_equivalent": [
            (r["cell"], r["endpoint"], round(r["d"], 4), round(r["p_tost"], 4))
            for r in primary_rows
            if not r["equivalent"]
        ],
        "secondary_tests": len(secondary),
        "secondary_rejected_holm": [
            (s["test"], s["cell"], s["summary"], s["p"], s["effect"]) for s in rejected
        ],
        "constant_summaries_different": [
            (r["cell"], r["summary"])
            for r in summary_rows
            if r.get("note") == "constant; DIFFERENT"
        ],
        "auc_tost_equivalent": {
            r["cell"]: bool(r["p_tost_0.02"] < ALPHA) for r in auc_summary
        },
        "lda_auc_same_features": cross,
        "max_abs_d_any_welch": max(
            abs(s["effect"]) for s in secondary if s["test"] == "welch"
        ),
    }
    (out / "verdict.json").write_text(json.dumps(verdict, indent=1, default=float))
    print(json.dumps(verdict, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    analyse(a.raw, a.out)
