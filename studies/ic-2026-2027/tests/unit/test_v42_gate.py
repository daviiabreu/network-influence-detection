"""Review decisions preserve denominator, CRN reference and sealing boundaries."""

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

from ic_study.simulation import v4_gate
from ic_study.simulation.v4_plan import gate_tasks
from ic_study.simulation.v4_store import SealedStore


def test_g2_aggregate_counts_gap_and_publishes_only_fd_cell_aggregate(
    tmp_path: Path,
) -> None:
    cells = ((0.03, 0.7),)
    rng = np.random.default_rng(15)
    for task in gate_tasks("G2", cells=cells):
        store = SealedStore(tmp_path / task.key)
        if task.repetition == 0:
            store.put_json("result", {"success": False})
        else:
            logit = rng.normal(0, 0.025)
            point = 1 / (1 + np.exp(-logit))
            store.put_json(
                "result",
                dict(
                    success=True,
                    auc=point,
                    se=0.025 * point * (1 - point),
                    nuisance_variance=[1, 10 if task.repetition < 40 else 1],
                    mean_shift=[0.0123, 0.0234],
                ),
            )
    report = v4_gate.aggregate(
        "G2",
        tmp_path,
        {
            "thresholds": dict(
                cell_lower=0.01, cell_upper=10.0, pooled_lower=0.01, pooled_upper=10.0
            )
        },
        cells=cells,
    )
    assert report["pass"]
    assert report["denominator"] == 100
    assert report["failures"] == 1
    assert report["successful_pair_counts"] == [49]
    assert report["fd_ratio_median_by_cell"] == [1]
    assert "mean_shift" not in report
    sealed = SealedStore(tmp_path).get_json("G2-auc-diagnostics")
    assert sealed is not None and "mean_shift" in sealed


def test_g2c_reference_uses_baseline_seeds_for_both_classes(
    monkeypatch: Any, tmp_path: Path
) -> None:
    task = gate_tasks("G2c")[2]
    seen = []

    class Source:
        def __init__(self, cell: object, seeds: object, **kwargs: object) -> None:
            self.seeds = seeds

        def profiles(
            self, phase: str, count: int, *, parameters: object = None
        ) -> np.ndarray:
            seen.append((phase, self.seeds, parameters))
            return np.zeros((count, 5))

    monkeypatch.setattr(v4_gate, "PanelSource", Source)
    monkeypatch.setattr(
        v4_gate,
        "fit_cell",
        lambda source: SimpleNamespace(
            success=True,
            final=SimpleNamespace(fit=SimpleNamespace(parameters=np.array([0.8, 0.1]))),
        ),
    )
    monkeypatch.setattr(v4_gate, "fit_record", lambda fit: {"success": True})
    monkeypatch.setattr(
        v4_gate,
        "fit_discriminant",
        lambda *args: SimpleNamespace(score=lambda values: np.zeros(len(values))),
    )
    v4_gate.run_task(task, SealedStore(tmp_path / "task"))
    references = [
        (seed, parameter) for phase, seed, parameter in seen if phase == "reference"
    ]
    baseline = replace(v4_gate.task_seed_plan(task), repetition=0)
    assert [seed for seed, _ in references] == [baseline, baseline]
    np.testing.assert_array_equal(references[0][1], [0.8, 0.1])
    assert references[1][1] is None


def test_gate_plans_and_auxiliary_namespaces_have_no_unintended_seed_aliases() -> None:
    plans = {
        v4_gate.task_seed_plan(task)
        for gate in ("G0", "G1b", "G1c", "G2", "G2c")
        for task in gate_tasks(gate)
    }
    seeds = [
        plan.seed(phase, "state", index, attempt=attempt)
        for plan in plans
        for phase in (
            "match",
            "validate",
            "train",
            "check",
            "reference",
            "stencil",
            "nuisance",
            "bootstrap",
        )
        for attempt in (0, 1)
        for index in (0, 1)
    ]
    assert len(seeds) == len(set(seeds))
    assert len({v4_gate.task_seed_plan(task) for task in gate_tasks("G1b")}) == 5000
