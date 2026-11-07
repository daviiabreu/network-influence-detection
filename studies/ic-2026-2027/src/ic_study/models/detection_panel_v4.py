"""D2 finite laws, using proposal A's byte-preserving rank transport."""

from __future__ import annotations

import numpy as np

from ic_study.models.anchored_panel import Floats
from ic_study.models.detection_panel import influence_update
from ic_study.simulation.amendment_a import fast_ranks


def influence(
    size: int,
    waves: int,
    state_seed: int,
    network_seed: int,
    *,
    share: float,
    phi: float = 0.85,
    repulsion: float = 0.25,
    anchor: float = 0,
    steps: int = 1,
) -> Floats:
    if not 0 <= share < 1 or not 0 <= phi <= 0.999 or not 0 <= anchor <= 1 or steps < 1:
        raise ValueError("Invalid successor kernel")
    rng = np.random.default_rng(state_seed)
    partners = None
    if share:
        network = np.random.default_rng(network_seed)
        partners = np.stack([network.permutation(size) for _ in range(8)], axis=1)
    state = fast_ranks(rng.normal(size=size))
    initial = state.copy()
    out = [state]
    for _ in range(1, waves):
        for _ in range(steps):
            noise = rng.normal(size=size)
            update = (
                phi * state + np.sqrt(1 - phi**2) * noise
                if partners is None
                else influence_update(
                    state, partners, noise, rho=phi, share=share, repulsion=repulsion
                )
            )
            state = fast_ranks((1 - anchor) * update + anchor * initial)
        out.append(state)
    return np.stack(out)


def null(
    size: int,
    waves: int,
    state_seed: int,
    component_seed: int,
    *,
    family: str,
    phi: float,
    eta: float,
    steps: int = 1,
) -> Floats:
    if family not in {"A", "B", "C", "D", "E"} or not 0 <= eta <= 0.8:
        raise ValueError("Invalid null family or weight")
    if not 0 <= phi <= 0.999 or steps < 1:
        raise ValueError("Invalid null persistence or resolution")
    if family in {"A", "C"} and eta != 0:
        raise ValueError("One-parameter family has no mixture weight")
    if family == "D":
        rng = np.random.default_rng(state_seed)
        state = fast_ranks(rng.normal(size=size))
        out = [state]
        for _ in range(1, waves):
            for _ in range(steps):
                persistence = phi + eta * (1 - phi) * (1 - np.exp(-(state**2) / 2))
                state = fast_ranks(
                    persistence * state
                    + np.sqrt(1 - persistence**2) * rng.normal(size=size)
                )
            out.append(state)
        return np.stack(out)
    state_path = influence(size, waves, state_seed, 0, share=0, phi=phi, steps=steps)
    if eta == 0:
        return state_path
    rng = np.random.default_rng(component_seed)
    if family == "B":
        fixed = rng.normal(size=size)
        return np.stack(
            [
                fast_ranks(np.sqrt(eta) * fixed + np.sqrt(1 - eta) * x)
                for x in state_path
            ]
        )
    stable = rng.random(size) < eta
    return np.stack(
        [fast_ranks(np.where(stable, state_path[0], x)) for x in state_path]
    )
