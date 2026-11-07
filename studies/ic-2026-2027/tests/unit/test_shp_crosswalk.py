"""Synthetic SHP crosswalk (successor 1, Addition 2) on tiny configurations."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from ic_study.analysis import shp_crosswalk
from ic_study.analysis.shp_crosswalk import (
    QUASI_SIMPLEX,
    SEED_OFFSET,
    CrosswalkCell,
    apply_estimators,
    cell_seeds,
    crosswalk_seed,
    estimator_names,
    main,
    plan_cells,
    select_cells,
    synthetic_panel,
)
from ic_study.simulation import detection_v4
from ic_study.simulation.detection_v4 import (
    GRID,
    RELIABILITIES,
    ROLES,
    Cell,
    PanelSource,
    SeedPlan,
)
from ic_study.simulation.v4_curve import ConfirmatorySeedPlan

SMOKE = ("interaction-a0-r0.70", "B-eta0.50-r0.70")
PHASES = (
    "match",
    "validate",
    "train",
    "check",
    "reference",
    "nuisance",
    "bootstrap",
    "stencil",
)


class _RoleSeeds(SeedPlan):
    """Test-only plan: one fixed seed per role, outside every v4 namespace."""

    def seed(self, phase: str, role: str, index: int, *, attempt: int = 0) -> int:
        return 1000 + sorted(ROLES).index(role)


def _frozen_observed(cell: Cell, parameters: np.ndarray | None, size: int) -> Any:
    captured = []

    def capture(latent: np.ndarray, observed: np.ndarray, **_: object) -> np.ndarray:
        captured.append(observed)
        return np.zeros(5)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(detection_v4, "selected_features", capture)
        PanelSource(cell, _RoleSeeds(), size=size)._profiles(
            "check", 1, parameters=parameters
        )
    return np.where(captured[0] >= 0, captured[0], np.nan).T


@pytest.mark.parametrize(
    ("crosswalk", "frozen", "parameters"),
    [
        (CrosswalkCell("interaction", 0.7, a=0.0), Cell(0.0, 0.7), None),
        (CrosswalkCell("interaction", 0.55, a=0.3), Cell(0.3, 0.55), None),
        (
            CrosswalkCell("B", 0.8, eta=0.25),
            Cell(0.0, 0.8),
            np.array([0.85, 0.25]),
        ),
    ],
)
def test_panels_reproduce_the_frozen_panel_source_composition(
    crosswalk: CrosswalkCell, frozen: Cell, parameters: np.ndarray | None
) -> None:
    seeds = {role: _RoleSeeds().seed("check", role, 0) for role in ROLES}
    panel = synthetic_panel(crosswalk, seeds, size=240)
    expected = _frozen_observed(frozen, parameters, 240)
    np.testing.assert_array_equal(panel, expected)
    observed = np.isfinite(panel)
    assert panel.shape == (240, 11) and set(np.unique(panel[observed])) == set(
        range(11)
    )
    assert not observed[160:, :5].any() and observed[160:, 5].all()


def test_crosswalk_seeds_cannot_coincide_with_v4_seed_plans() -> None:
    crosswalk = {
        crosswalk_seed(shp_crosswalk.SEED_ROOT, block, replicate, role)
        for block in range(len(RELIABILITIES))
        for replicate in range(10)
        for role in shp_crosswalk.ROLES
    }
    assert len(crosswalk) == len(RELIABILITIES) * 10 * len(shp_crosswalk.ROLES)
    assert all(SEED_OFFSET <= seed < 2 * SEED_OFFSET for seed in crosswalk)
    frozen = set()
    plans = [
        SeedPlan(),
        SeedPlan(repetition=3, block=7),
        SeedPlan(repetition=9999, block=9999, gate=True),
        *(ConfirmatorySeedPlan(block=block) for block in range(len(RELIABILITIES))),
    ]
    for plan, phase, role, index, attempt in itertools.product(
        plans, PHASES, sorted(ROLES), (0, 1, 4095), (0, 1)
    ):
        frozen.add(plan.seed(phase, role, index, attempt=attempt))
    # Every v4 seed is an 8-byte digest, so the value spaces are disjoint.
    assert all(0 <= seed < SEED_OFFSET for seed in frozen)
    assert not crosswalk & frozen
    assert not shp_crosswalk.NAMESPACE.startswith("ic-detection-boundary")


def test_declared_plan_covers_the_frozen_grids_and_both_b_references() -> None:
    cells = plan_cells()
    assert len(cells) == len(GRID) * len(RELIABILITIES) + 2 * len(RELIABILITIES)
    assert len({cell.key for cell in cells}) == len(cells)
    interaction = {(c.a, c.r) for c in cells if c.family == "interaction"}
    assert interaction == set(itertools.product(GRID, RELIABILITIES))
    references = {(c.eta, c.r) for c in cells if c.family == "B"}
    assert references == set(itertools.product((0.25, 0.5), RELIABILITIES))
    assert select_cells("2") == cells[:2]
    assert [c.key for c in select_cells(",".join(reversed(SMOKE)))] == list(SMOKE)
    with pytest.raises(ValueError, match="Unknown"):
        select_cells("interaction-a0.2-r0.70")
    with pytest.raises(ValueError):
        CrosswalkCell("B", 0.7, eta=0.3)
    seeds = cell_seeds(cells[0], 0)
    assert cell_seeds(cells[1], 0) == seeds  # common random numbers across a
    assert cell_seeds(cells[0], 1) != seeds


@pytest.fixture(scope="module")
def smoke(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Two cells x two replicates at N=600, as two shards, then shard 0 again."""
    out = tmp_path_factory.mktemp("crosswalk")
    calls: list[str] = []

    def forbidden(*_: object, **__: object) -> int:
        calls.append("seed")
        raise AssertionError("A v4 seed plan was consumed")

    def shard(index: int) -> Path | None:
        return shp_crosswalk.run(
            out,
            select_cells(",".join(SMOKE)),
            replicates=2,
            shard=index,
            shards=2,
            size=600,
            log=lambda _: None,
        )

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(SeedPlan, "seed", forbidden)
        patch.setattr(ConfirmatorySeedPlan, "seed", forbidden)
        pending = shard(0)
        target = shard(1)
        cells = {p.name: p.stat().st_mtime_ns for p in (out / "cells").iterdir()}
        aggregate = (out / "crosswalk.json").read_bytes()
        rerun = shard(0)
    return {
        "out": out,
        "pending_after_first_shard": pending is None,
        "targets": (target, rerun),
        "untouched_on_rerun": cells
        == {p.name: p.stat().st_mtime_ns for p in (out / "cells").iterdir()},
        "same_aggregate": aggregate == (out / "crosswalk.json").read_bytes(),
        "seed_plan_calls": calls,
    }


def test_smoke_run_shards_resumes_and_aggregates(smoke: dict[str, Any]) -> None:
    assert smoke["pending_after_first_shard"]
    assert smoke["targets"] == (smoke["out"] / "crosswalk.json",) * 2
    assert smoke["untouched_on_rerun"] and smoke["same_aggregate"]
    assert smoke["seed_plan_calls"] == []
    data = json.loads((smoke["out"] / "crosswalk.json").read_text())
    assert data["schema"] == shp_crosswalk.SCHEMA and data["status"] == "exploratory"
    assert data["declared_plan"] is False
    assert data["parameters"]["cells"] == list(SMOKE)
    assert data["parameters"]["size"] == 600 and data["parameters"]["replicates"] == 2
    assert data["parameters"]["estimators"] == list(estimator_names())
    assert len(data["parameters"]["estimators"]) == 1 + 9 * 4 + 9 + 1
    assert [cell["key"] for cell in data["cells"]] == list(SMOKE)
    for cell in data["cells"]:
        for name, summary in cell["estimators"].items():
            assert summary["n_values"] + summary["failures"] == 2, name
            if summary["n_values"]:
                assert summary["min"] <= summary["mean"] <= summary["max"]
        assert 0 < cell["estimators"][QUASI_SIMPLEX]["mean"] < 1
    (provenance,) = data["provenance"]
    assert provenance["generator"]["matches_freeze_v4"] is True
    assert set(provenance["host"]) >= {"platform", "machine", "node_sha256"}
    assert provenance["code"]["commit"]
    specification = data["specification"]
    assert specification["machine_json"]["path"].endswith(
        "shp-reliability-successor-1.json"
    )


def test_smoke_values_are_deterministic_for_a_fixed_seed(
    smoke: dict[str, Any],
) -> None:
    cell = select_cells(SMOKE[1])[0]
    record = json.loads((smoke["out"] / "cells" / f"{cell.key}.json").read_text())
    stored = record["replicates"][1]
    panel = synthetic_panel(cell, cell_seeds(cell, 1), size=600)
    values, failures = apply_estimators(panel)
    assert values == stored["values"] and failures == stored["failures"]
    other = synthetic_panel(cell, cell_seeds(cell, 1, root=20260929), size=600)
    assert not np.array_equal(panel, other, equal_nan=True)


def test_existing_cells_from_another_plan_are_refused(smoke: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="different crosswalk plan"):
        shp_crosswalk.run(
            smoke["out"], select_cells(",".join(SMOKE)), replicates=3, size=600
        )


@pytest.mark.parametrize(
    "arguments",
    [
        ["--cells", "interaction-a0.2-r0.70"],
        ["--cells", "0"],
        ["--replicates", "0"],
        ["--shard", "2", "--shards", "2"],
    ],
)
def test_cli_rejects_invalid_selections(tmp_path: Path, arguments: list[str]) -> None:
    with pytest.raises(SystemExit) as stopped:
        main(["--out", str(tmp_path), *arguments])
    assert stopped.value.code == 2
    assert not (tmp_path / "cells").exists()
