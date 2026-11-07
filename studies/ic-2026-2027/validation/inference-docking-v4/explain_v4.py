"""Post-hoc explanation runs (NOT pre-declared): check that the band
discrepancy (G01) is fully explained by three readings (A15, A22-A23), and
record the S09/S21 solver paths. Writes explain-results.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from ic_study.analysis import detection_boundary_v4 as pv  # noqa: E402

import compare_v4 as cv  # noqa: E402
import docking_v4 as dk  # noqa: E402


def band_variant(
    point, boot, dev, v, n=2000, centre=True, draw_se=True, method="higher"
):
    eps = 1 / (2 * n)
    se = np.sqrt(boot.std(0, ddof=1) ** 2 + v)
    pc = np.clip(point, eps, 1 - eps)
    rep = boot - boot.mean(0) + point if centre else boot
    star = np.clip(np.clip(rep + dev, 0, 1), eps, 1 - eps)
    se_l = np.maximum(se, eps) / (pc * (1 - pc))
    se_d = np.maximum(se, eps) / (star * (1 - star)) if draw_se else se_l
    t = np.max(np.abs(np.log(star / (1 - star)) - np.log(pc / (1 - pc))) / se_d, axis=1)
    return max(float(np.quantile(t, 0.95, method=method)), dk.Z_FLOOR)


def main():
    out = {}
    rng = np.random.default_rng(cv.seed("band"))
    for i in range(10):
        S, B = 9, 500
        point = np.sort(rng.uniform(0.45, 0.99, S))
        boot = point + rng.normal(0, 0.01 + 0.01 * i, (B, S))
        dev = rng.normal(0, 0.005, (B, S))
        dev -= dev.mean(0)
        v = dev.var(0, ddof=1)
        se = np.sqrt(boot.std(0, ddof=1) ** 2 + v)
        repl = np.clip(point + boot - boot.mean(0) + dev, 0, 1)
        p = pv.band(pv.Uncertainty(point, boot.std(0, ddof=1), se, repl)).critical
        rec = {"project": p, "all_three": band_variant(point, boot, dev, v)}
        rec["all_three_equal"] = cv.close(rec["all_three"], p)
        rec["plugin_se_only"] = band_variant(point, boot, dev, v, draw_se=False)
        rec["linear_quantile_only"] = band_variant(point, boot, dev, v, method="linear")
        rec["uncentred_only"] = band_variant(point, boot, dev, v, centre=False)
        out[f"G01_{i}"] = rec
    # solver path records
    for case in ("S09_hump_profile", "S21_near_threshold_endpoint"):
        fn, opts = cv.SOLVER_CASES[case]
        seen = []

        def rec_fn(phi, eta, fn=fn, seen=seen):
            seen.append([phi, eta])
            return fn(phi, eta)

        p = cv.run_project_solver(rec_fn, opts)
        out[case] = {
            "project_status": p.status,
            "project_theta": p.parameters.tolist(),
            "project_residual": p.residual.tolist(),
            "project_tolerance": p.tolerance.tolist(),
            "project_evaluated_points": seen,
        }
    (HERE / "explain-results.json").write_text(json.dumps(out, indent=1))
    print(
        json.dumps(
            {
                k: v.get("all_three_equal", v.get("project_status"))
                for k, v in out.items()
            }
        )
    )


if __name__ == "__main__":
    main()
