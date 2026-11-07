"""Run the pre-declared docking comparison (parts A, B, C).

Usage (from studies/ic-2026-2027, project venv):
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python \
      validation/docking-v4/compare/run_all.py --part A|B|C --raw DIR --out DIR
Per-panel arrays go to --raw (outside Git); small summaries go to --out.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from dockv4 import model as dm  # noqa: E402
from dockv4 import stats as ds  # noqa: E402
from dockv4.pipeline import Matcher, auc_replication, match  # noqa: E402
from dockv4.seeds import Streams  # noqa: E402
from project_adapter import (  # noqa: E402
    DockingSeedPlan,
    mirror_matches_panel_source,
    mirror_observed,
    project_auc_replication,
    project_cell,
)

N = 1002
CLEAN_NS = "ic-detection-boundary-v4-docking-clean"
MATCH_NS = "ic-detection-boundary-v4-docking-match"
SEEDLEVEL_NS = "ic-detection-boundary-v4-docking-seedlevel"
R_PANELS = 1000


def cells_b() -> list[dict]:
    out = []
    for r in (0.5, 0.7, 0.9):
        for a in (0.0, 0.03, 0.30):
            out.append({"family": "social", "a": a, "r": r})
        out += [
            {"family": "A", "phi": 0.85, "r": r},
            {"family": "B", "phi": 0.80, "eta": 0.30, "r": r},
            {"family": "C", "phi": 0.85, "r": r},
            {"family": "D", "phi": 0.80, "eta": 0.50, "r": r},
            {"family": "E", "phi": 0.80, "eta": 0.30, "r": r},
        ]
    out.append({"family": "social_C_marginal", "a": 0.30, "r": 0.7})
    return out


def cell_id(kind: dict) -> str:
    parts = [kind["family"], f"r{kind['r']}"]
    for key in ("a", "phi", "eta"):
        if key in kind:
            parts.append(f"{key}{kind[key]}")
    return "_".join(parts)


def dock_cell(kind: dict) -> tuple[dm.Cell, int]:
    """dockv4 Cell and class (1 social, 0 null)."""
    fam = kind["family"]
    if fam == "social":
        return dm.Cell("social", kind["r"], a=kind["a"]), 1
    if fam == "social_C_marginal":
        return dm.Cell("social", kind["r"], a=kind["a"], c_comparison=True), 1
    return dm.Cell(fam, kind["r"], phi=kind["phi"], eta=kind.get("eta", 0.0)), 0


def flatten(summ: dict) -> np.ndarray:
    return np.concatenate(
        [summ["n_obs"], summ["mean"], summ["var"], summ["lag"], summ["wave_corr"]]
    )


SUMMARY_NAMES = (
    [f"n_obs_{t}" for t in range(11)]
    + [f"mean_{t}" for t in range(11)]
    + [f"var_{t}" for t in range(11)]
    + [f"L{k}" for k in range(1, 11)]
    + [f"corr_{s}_{t}" for s in range(11) for t in range(s + 1, 11)]
)


# --------------------------------------------------------------------------
# Part B
# --------------------------------------------------------------------------
def task_b(args: tuple[dict, str]) -> tuple[str, str, np.ndarray]:
    kind, impl = args
    rows = []
    if impl == "dock":
        cell, cls = dock_cell(kind)
        for j in range(R_PANELS):
            index = 2 * j + cls
            st = Streams(CLEAN_NS, 0, "check", index, index // 4)
            rows.append(flatten(ds.panel_summaries(dm.panel(cell, N, st)["y"])))
    else:
        pcell, params = project_cell(kind)
        plan = DockingSeedPlan()
        for j in range(R_PANELS):
            y = mirror_observed(pcell, params, N, plan, "check", j)
            rows.append(flatten(ds.panel_summaries(y)))
    return cell_id(kind), impl, np.array(rows)


def part_b(raw: Path, out: Path) -> None:
    kinds = cells_b()
    checks = {}
    for kind in kinds:  # production path equals the mirror (first 50 panels)
        pcell, params = project_cell(kind)
        checks[cell_id(kind)] = mirror_matches_panel_source(
            pcell, params, N, DockingSeedPlan(), 50
        )
    (out / "partB-mirror-check.json").write_text(json.dumps(checks, indent=1))
    jobs = [(k, impl) for k in kinds for impl in ("dock", "project")]
    with Pool(4) as pool:
        for cid, impl, arr in pool.imap_unordered(task_b, jobs):
            np.save(raw / f"B_{cid}_{impl}.npy", arr)
            print(cid, impl, arr.shape, flush=True)


# --------------------------------------------------------------------------
# Part A
# --------------------------------------------------------------------------
def part_a(raw: Path, out: Path) -> None:
    from dockv4.seeds import seed

    from ic_study.analysis.detection_boundary import lag_profile
    from ic_study.models.detection_panel_v4 import influence, null

    def rng(s: int) -> np.random.Generator:
        return np.random.default_rng(s)

    res: dict[str, dict] = {}
    for i in range(20):
        s_state, s_net, s_null = (
            seed(SEEDLEVEL_NS, 0, "seed", role, i)
            for role in ("state", "network", "null-state")
        )
        pairs = {}
        for a in (0.0, 0.03, 0.30):
            pairs[f"social_a{a}"] = (
                dm.simulate_social(N, a, rng(s_state), rng(s_net)),
                influence(N, 11, s_state, s_net, share=a).T,
            )
        pairs["A"] = (
            dm.simulate_x(N, 0.85, rng(s_state)),
            null(N, 11, s_state, s_null, family="A", phi=0.85, eta=0).T,
        )
        pairs["B"] = (
            dm.simulate_b(N, 0.80, 0.30, rng(s_state), rng(s_null)),
            null(N, 11, s_state, s_null, family="B", phi=0.80, eta=0.30).T,
        )
        pairs["D"] = (
            dm.simulate_d(N, 0.80, 0.50, rng(s_state)),
            null(N, 11, s_state, s_null, family="D", phi=0.80, eta=0.50).T,
        )
        pairs["E"] = (
            dm.simulate_e(N, 0.80, 0.30, rng(s_state), rng(s_null)),
            null(N, 11, s_state, s_null, family="E", phi=0.80, eta=0.30).T,
        )
        for name, (mine, theirs) in pairs.items():
            d = res.setdefault(name, {"max_abs_diff": 0.0, "bitwise_equal": 0})
            d["max_abs_diff"] = max(
                d["max_abs_diff"], float(np.abs(mine - theirs).max())
            )
            d["bitwise_equal"] += int(np.array_equal(mine, theirs))
    # feature function on the project's own observed panels
    feat = {}
    plan = DockingSeedPlan(block=77)
    for kind in [
        {"family": "social", "a": 0.30, "r": 0.7},
        {"family": "B", "phi": 0.8, "eta": 0.3, "r": 0.7},
        {"family": "C", "phi": 0.85, "r": 0.7},
    ]:
        pcell, params = project_cell(kind)
        worst = 0.0
        for j in range(20):
            y = mirror_observed(pcell, params, N, plan, "check", j)
            theirs = lag_profile(y.T)
            mine = np.array([ds.pooled_lag_corr(y, k) for k in range(1, 6)])
            worst = max(worst, float(np.abs(mine - theirs).max()))
        feat[cell_id(kind)] = worst
    result = {"latent": res, "lag_feature_max_abs_diff": feat, "seeds_per_case": 20}
    (out / "partA-seed-level.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result, indent=1))


# --------------------------------------------------------------------------
# Part C
# --------------------------------------------------------------------------
C_CELLS = [
    {"id": "C1", "a": 0.0, "r": 0.7, "null": "A"},
    {"id": "C2", "a": 0.30, "r": 0.7, "null": "B"},
    {"id": "C3", "a": 0.03, "r": 0.5, "null": "B"},
]
TRAIN_NETS, TEST_NETS, REPS = 100, 250, 50


def task_c(args: tuple[dict, str, int]) -> tuple[str, str, int, float, np.ndarray]:
    c, impl, rep = args
    phi, eta = c["phi"], c["eta"]
    if impl == "dock":
        social = dm.Cell("social", c["r"], a=c["a"])
        nullc = dm.Cell(c["null"], c["r"], phi=phi, eta=eta)
        res = auc_replication(social, nullc, N, TRAIN_NETS, TEST_NETS, CLEAN_NS, rep)
    else:
        from ic_study.simulation.detection_v4 import Cell as PCell

        pcell = PCell(c["a"], c["r"], family=c["null"])
        res = project_auc_replication(
            pcell, np.array([phi, eta]), N, rep, TRAIN_NETS, TEST_NETS
        )
    feats = np.concatenate(res["features"])
    return c["id"], impl, rep, res["auc"], feats


def part_c(raw: Path, out: Path) -> None:
    fits = {}
    for c in C_CELLS:
        if c["a"] == 0.0:
            c["phi"], c["eta"] = 0.85, 0.0
            fits[c["id"]] = {"status": "anchor", "phi": 0.85, "eta": 0.0}
            continue
        t0 = time.time()
        mt = Matcher(dm.Cell("social", c["r"], a=c["a"]), c["null"], N, 256, MATCH_NS)
        fit = match(mt)
        fit["seconds"] = round(time.time() - t0, 1)
        fits[c["id"]] = fit
        c["phi"], c["eta"] = fit["phi"], fit["eta"]
        print(c["id"], fit, flush=True)
    (out / "partC-fits.json").write_text(json.dumps(fits, indent=1))
    jobs = [
        (c, impl, rep)
        for c in C_CELLS
        for impl in ("dock", "project")
        for rep in range(REPS)
    ]
    rows = []
    with Pool(4) as pool:
        for cid, impl, rep, value, feats in pool.imap_unordered(task_c, jobs):
            rows.append({"cell": cid, "impl": impl, "rep": rep, "auc": value})
            np.save(raw / f"C_{cid}_{impl}_{rep:03d}.npy", feats)
    rows.sort(key=lambda d: (d["cell"], d["impl"], d["rep"]))
    with open(out / "partC-auc.csv", "w") as fh:
        fh.write("cell,impl,rep,auc\n")
        for d in rows:
            fh.write(f"{d['cell']},{d['impl']},{d['rep']},{d['auc']:.10f}\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["A", "B", "C"], required=True)
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.raw.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    {"A": part_a, "B": part_b, "C": part_c}[args.part](args.raw, args.out)
    print(f"part {args.part} done in {time.time() - t0:.1f}s", flush=True)


if __name__ == "__main__":
    main()
