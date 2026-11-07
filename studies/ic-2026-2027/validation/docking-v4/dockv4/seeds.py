"""Seed material ``namespace|block|phase|role|index`` -> SHA-256 -> 8 bytes big-endian.

Docking namespaces only: ``ic-detection-boundary-v4-docking-*``. Reserved
confirmatory namespaces (decision spec D10) are refused.
"""

from __future__ import annotations

import hashlib

import numpy as np

PREFIX = "ic-detection-boundary-v4-docking-"
ROLES = ("state", "null-state", "network", "mask", "error", "heap")


def seed(namespace: str, block: int, phase: str, role: str, index: int) -> int:
    if not namespace.startswith(PREFIX):
        raise ValueError(f"docking namespace must start with {PREFIX!r}")
    if "confirmatory" in namespace:
        raise ValueError("confirmatory namespaces are reserved")
    if role not in ROLES:
        raise ValueError(f"unknown role {role!r}")
    material = f"{namespace}|{block}|{phase}|{role}|{index}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def rng(namespace: str, block: int, phase: str, role: str, index: int):
    return np.random.default_rng(seed(namespace, block, phase, role, index))


class Streams:
    """The per-panel random streams, one numpy Generator per role."""

    def __init__(
        self,
        namespace: str,
        block: int,
        phase: str,
        index: int,
        network_index: int,
    ) -> None:
        def make(role: str, idx: int):
            return rng(namespace, block, phase, role, idx)

        self.state = make("state", index)
        self.null_state = make("null-state", index)
        self.mask = make("mask", index)
        self.error = make("error", index)
        self.heap = make("heap", index)
        self.network = make("network", network_index)
