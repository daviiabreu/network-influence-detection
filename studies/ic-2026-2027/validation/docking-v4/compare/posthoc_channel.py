"""POST-HOC (not pre-declared): pathwise docking of the observation channel.

Feeds identical latent paths, masks and measured values into the dockv4 and
project discretisers, and compares the C error-scale normalisations.
Usage (project venv): .venv/bin/python validation/docking-v4/compare/posthoc_channel.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from ic_study.models.anchored_panel import panel_mask
from ic_study.models.detection_panel import measurement, ordinal_channel
from ic_study.models.detection_panel_v4 import influence

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from dockv4 import model as dm  # noqa: E402
from dockv4.seeds import seed  # noqa: E402

NS = "ic-detection-boundary-v4-docking-posthoc"
N = 1002


def main() -> None:
    equal = {"equiprobable": 0, "c_marginal_no_heap": 0}
    mask_first_obs_ok = 0
    for i in range(20):
        s = [seed(NS, 0, "posthoc", role, i) for role in ("state", "network", "mask")]
        latent = influence(N, 11, s[0], s[1], share=0.3)
        mask = panel_mask(N, 11, s[2], retention=0.89)
        w = measurement(latent, 0.7, seed(NS, 0, "posthoc", "error", i))
        theirs = ordinal_channel(w, mask).T.astype(float)
        theirs[theirs < 0] = np.nan
        mine = dm.discretise(w.T, mask.T)
        equal["equiprobable"] += int(np.array_equal(mine, theirs, equal_nan=True))
        theirs_c = ordinal_channel(w, mask, midpoint_mass=0.1).T.astype(float)
        theirs_c[theirs_c < 0] = np.nan
        mine_c = dm.discretise(w.T, mask.T, marginal=dm.c_marginal())
        equal["c_marginal_no_heap"] += int(
            np.array_equal(mine_c, theirs_c, equal_nan=True)
        )
        mask_first_obs_ok += int(
            np.array_equal(np.argmax(mask.T, axis=1), dm.entry_waves(N))
        )
    # C error scale: project normalises empirically over the (11, N) latent panel
    latent = influence(N, 11, 1, 2, share=0.0)
    raw = 1 + 2 * np.exp(-(latent**2) / 2)
    empirical = float(np.sqrt(np.mean(raw**2)))
    analytic = float(np.sqrt(1 + 4 / np.sqrt(2) + 4 / np.sqrt(3)))
    out = {
        "note": "post-hoc, exploratory; not part of the pre-declared comparison",
        "cases": 20,
        "discretiser_bitwise_equal": equal,
        "project_mask_entry_matches_spec_geometry": mask_first_obs_ok,
        "c_scale_norm_project_empirical_N1002": empirical,
        "c_scale_norm_dock_analytic": analytic,
        "c_scale_relative_difference": empirical / analytic - 1,
    }
    path = HERE.parent / "results" / "posthoc-channel.json"
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
