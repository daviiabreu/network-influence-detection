"""Drive the project implementation with docking-only seed namespaces.

Read-only use of the project's public functions; nothing in ``src/`` is changed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

from ic_study.analysis.detection_boundary import auc as project_auc
from ic_study.analysis.detection_boundary import lag_profile
from ic_study.analysis.redesign import fit_discriminant
from ic_study.models.anchored_panel import panel_mask
from ic_study.models.detection_panel import measurement, ordinal_channel
from ic_study.models.detection_panel_v4 import influence, null
from ic_study.simulation.detection_v4 import ROLES, Cell, PanelSource, SeedPlan

PROJECT_NS = "ic-detection-boundary-v4-docking-project"


@dataclass(frozen=True)
class DockingSeedPlan(SeedPlan):
    """Same material format as SeedPlan, docking namespace only."""

    def seed(self, phase: str, role: str, index: int, *, attempt: int = 0) -> int:
        if role not in ROLES or "confirmatory" in phase:
            raise ValueError("bad seed request")
        block = self.block * 2 + attempt
        material = f"{PROJECT_NS}|{block}|{phase}|{role}|{index}"
        return int.from_bytes(hashlib.sha256(material.encode()).digest()[:8], "big")


def project_cell(kind: dict) -> tuple[Cell, np.ndarray | None]:
    """Map a docking cell description to (project Cell, null parameters)."""
    fam, r = kind["family"], kind["r"]
    if fam == "social":
        return Cell(kind["a"], r), None
    if fam == "social_C_marginal":
        return Cell(kind["a"], r, family="C"), None
    return Cell(0.0, r, family=fam), np.array([kind["phi"], kind.get("eta", 0.0)])


def mirror_observed(
    cell: Cell, parameters, size: int, plan: SeedPlan, phase: str, j: int
) -> np.ndarray:
    """Replicates PanelSource._profiles (observed channel) up to the ordinal panel.

    Returns (size, 11) float with NaN for non-respondents (docking layout).
    """
    coupled = phase in {"match", "validate"}
    index = 2 * j + (1 if coupled or parameters is None else 0)

    def seed(role: str, i: int = index) -> int:
        return plan.seed(phase, role, i)

    if parameters is None:
        latent = influence(
            size,
            11,
            seed("state"),
            seed("network", index if coupled else index // 4),
            share=cell.share,
            repulsion=cell.repulsion,
            anchor=cell.anchor,
            steps=cell.steps,
        )
    else:
        latent = null(
            size,
            11,
            seed("state"),
            seed("null-state"),
            family=cell.family,
            phi=float(parameters[0]),
            eta=float(parameters[1]),
            steps=cell.steps,
        )
    mask = panel_mask(size, 11, seed("mask"), retention=0.89)
    is_c_null = cell.family == "C" and parameters is not None
    measured = measurement(
        latent,
        cell.reliability,
        seed("error"),
        heteroscedastic=is_c_null,
        error_correlation=cell.error_correlation,
    )
    observed = ordinal_channel(
        measured,
        mask,
        midpoint_mass=0.1 if cell.family == "C" else 0,
        heap_seed=seed("heap") if is_c_null else None,
    )
    return np.where(observed >= 0, observed, np.nan).T.astype(float)


def mirror_matches_panel_source(
    cell: Cell, parameters, size: int, plan: SeedPlan, count: int
) -> bool:
    src = PanelSource(cell, plan, size=size)
    prod = src.profiles("check", count, parameters=parameters)
    mine = np.array(
        [
            lag_profile(mirror_observed(cell, parameters, size, plan, "check", j).T)
            for j in range(count)
        ]
    )
    return bool(np.array_equal(prod, mine))


def project_auc_replication(
    cell: Cell, parameters, size: int, block: int, train: int, test: int
) -> dict:
    """Project pipeline minus matching/nuisance: train, fit LDA, score, AUC."""
    src = PanelSource(cell, DockingSeedPlan(block=block), size=size)
    n_tr, n_te = 2 * train, 2 * test
    tr0 = src.profiles("train", n_tr, parameters=parameters)[:, 2:5]
    tr1 = src.profiles("train", n_tr)[:, 2:5]
    te0 = src.profiles("check", n_te, parameters=parameters)[:, 2:5]
    te1 = src.profiles("check", n_te)[:, 2:5]
    model = fit_discriminant(np.concatenate([tr0, tr1]), np.repeat([0, 1], n_tr))
    value = project_auc(model.score(te0), model.score(te1))
    return {"auc": value, "features": (tr1, tr0, te1, te0)}
