"""Complete frozen inventory and deterministic, result-independent gate allocation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import cast

from ic_study.simulation.detection_v4 import GRID, RELIABILITIES, Cell

G2_CELLS = (
    (0.003, 0.7),
    (0.01, 0.7),
    (0.03, 0.7),
    (0.1, 0.7),
    (0.3, 0.7),
    (0.03, 0.5),
    (0.03, 0.9),
)
SCENARIOS = (
    "gaussian-icc0",
    "gaussian-icc05",
    "non-gaussian",
    "ties",
    "dependent-slots",
)
CLOSE_UTC = "2026-10-19T02:59:00Z"


def inventory() -> list[dict[str, object]]:
    configurations: list[tuple[int, str, str, str, dict[str, object]]] = [
        (1, "B", "observed", "main", {})
    ]
    configurations += [(2, f, "observed", "main", {}) for f in "ACDE"]
    configurations += [
        (3, f, c, "main", {})
        for f in "ABCDE"
        for c in ("latent", "ordinal_one", "latent_rank")
    ]
    configurations += [
        (3, f, c, "mobility", {"mobility": True})
        for f in "ABCDE"
        for c in ("observed", "latent", "ordinal_one")
    ]
    configurations += [
        (4, "B", "observed", name, cast(dict[str, object], options))
        for name, options in (
            ("c025", {"error_correlation": 0.25}),
            ("c050", {"error_correlation": 0.5}),
            ("d010", {"gain": 0.1}),
            ("d020", {"gain": 0.2}),
            ("c050-d020-exploratory", {"error_correlation": 0.5, "gain": 0.2}),
        )
    ]
    configurations += [(5, "B", "observed", "b000", {"repulsion": 0.0})]
    configurations += [
        (5, "B", "observed", f"omega{int(w * 100):03}", {"anchor": w})
        for w in (0.25, 0.5, 0.75, 1.0)
    ]
    configurations += [(6, "B", "observed", "steps24", {"steps": 24})]
    rows = []
    for number, (tier, family, channel, sensitivity, options) in enumerate(
        configurations
    ):
        for ri, r in enumerate(RELIABILITIES):
            for ai, a in enumerate(GRID):
                rows.append(
                    {
                        "id": f"t{tier}-u{number:02}-r{ri}-a{ai}",
                        "unit": f"t{tier}-u{number:02}-r{ri}",
                        "tier": tier,
                        "family": family,
                        "a": a,
                        "r": r,
                        "channel": channel,
                        "sensitivity": sensitivity,
                        "options": options,
                        "status": "não iniciado",
                    }
                )
    return rows


@dataclass(frozen=True)
class GateTask:
    gate: str
    index: int
    repetition: int
    cell: Cell
    scenario: str = ""
    baseline: bool = False

    @property
    def key(self) -> str:
        return f"{self.gate}-{self.index:05}"

    def record(self) -> dict[str, object]:
        return asdict(self)


def gate_tasks(
    gate: str, *, cells: tuple[tuple[float, float], ...] = G2_CELLS
) -> list[GateTask]:
    if gate == "G0":
        return [
            GateTask(gate, i, 0, Cell(a, r))
            for i, (a, r) in enumerate((a, r) for r in RELIABILITIES for a in GRID)
        ]
    if gate == "G1b":
        return [
            GateTask(gate, si * 1000 + rep, rep, Cell(0, 0.7), scenario)
            for si, scenario in enumerate(SCENARIOS)
            for rep in range(1000)
        ]
    if gate == "G1c":
        return [
            GateTask(gate, ri * 50 + rep, rep, Cell(0, r))
            for ri, r in enumerate((0.5, 0.7, 0.9))
            for rep in range(50)
        ]
    if gate == "G2":
        return [
            GateTask(gate, ci * 100 + rep, rep, Cell(a, r))
            for ci, (a, r) in enumerate(cells)
            for rep in range(100)
        ]
    if gate == "G2c":
        tasks = []
        for ci, (a, count) in enumerate(((0.1, 100), (0.03, 40))):
            tasks.append(GateTask(gate, ci * 101, 0, Cell(a, 0.7), baseline=True))
            tasks += [
                GateTask(gate, ci * 101 + rep + 1, rep + 1, Cell(a, 0.7))
                for rep in range(count)
            ]
        return tasks
    raise ValueError("Unknown gate")


def substitute_cells(eligible: set[tuple[float, float]]) -> list[tuple[float, float]]:
    """Only move toward .70, without duplicating another G2 cell."""
    allocation = list(G2_CELLS)
    used = set(allocation)
    output = []
    for a, r in allocation:
        if (a, r) in eligible:
            output.append((a, r))
            continue
        choices = [
            rr
            for rr in RELIABILITIES
            if min(r, 0.7) <= rr <= max(r, 0.7)
            and rr != r
            and (a, rr) in eligible
            and (a, rr) not in used
        ]
        if choices:
            chosen = min(choices, key=lambda rr: (abs(rr - r), rr))
            output.append((a, chosen))
            used.add((a, chosen))
    return output
