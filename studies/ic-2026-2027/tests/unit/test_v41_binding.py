"""G0 statuses and resulting allocation are bound before dispersion tasks."""

import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest

from ic_study.simulation.v4_gate import (
    allocation_preflight,
    g0_gap_binding,
    status_digest,
)
from ic_study.simulation.v4_plan import G2_CELLS, gate_tasks


def test_two_stage_binding_rejects_missing_stale_or_changed_inputs(
    tmp_path: Path,
) -> None:
    statuses: list[dict[str, Any]] = [
        dict(
            a=t.cell.share,
            r=t.cell.reliability,
            fits=[dict(family="B", channel="observed", success=True)],
        )
        for t in gate_tasks("G0")
    ]
    criteria = (
        Path(__file__).resolve().parents[2]
        / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
    ).read_bytes()
    path = tmp_path / "allocation.json"
    with pytest.raises(ValueError, match="second"):
        allocation_preflight(path, "a" * 64, statuses, criteria)
    record = dict(
        schema=1,
        stage="post-G0-pre-G2",
        freeze_sha256="a" * 64,
        g0_statuses_sha256=status_digest(statuses),
        g2_cells=G2_CELLS,
        criteria_sha256=hashlib.sha256(criteria).hexdigest(),
    )
    record["g0_gap_binding"] = g0_gap_binding(statuses, G2_CELLS, json.loads(criteria))
    path.write_text(json.dumps(record))
    assert allocation_preflight(path, "a" * 64, statuses, criteria) == G2_CELLS
    with pytest.raises(ValueError, match="binding"):
        allocation_preflight(path, "b" * 64, statuses, criteria)
    with pytest.raises(ValueError, match="binding"):
        allocation_preflight(path, "a" * 64, statuses, criteria + b" ")
    statuses[0]["fits"][0]["success"] = False
    with pytest.raises(ValueError, match="binding"):
        allocation_preflight(path, "a" * 64, statuses, criteria)
    record["g0_statuses_sha256"] = status_digest(statuses)
    record["g2_cells"] = list(G2_CELLS)[1:]
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="allocation"):
        allocation_preflight(path, "a" * 64, statuses, criteria)


def test_g2c_cannot_rebind_the_allocation_used_by_g2(tmp_path: Path) -> None:
    from ic_study.simulation.v4_gate import authorize_stage
    from ic_study.simulation.v4_store import SealedStore

    root = SealedStore(tmp_path / "sealed")
    with pytest.raises(ValueError, match="G2 binding"):
        authorize_stage(root, "G2c", "freeze", "second")
    authorize_stage(root, "G2", "freeze", "second")
    with pytest.raises(ValueError, match="changed"):
        authorize_stage(root, "G2", "freeze", "changed")
    with pytest.raises(ValueError, match="G2 binding"):
        authorize_stage(root, "G2c", "freeze", "changed")
    authorize_stage(root, "G2c", "freeze", "second")
    authorize_stage(root, "G2c", "freeze", "second")


def test_second_binding_rejects_uncalibrated_criteria_code(tmp_path: Path) -> None:
    statuses: list[dict[str, Any]] = [
        dict(
            a=t.cell.share,
            r=t.cell.reliability,
            fits=[dict(family="B", channel="observed", success=True)],
        )
        for t in gate_tasks("G0")
    ]
    criteria = json.dumps({"G2_cells": 7, "joint_targets_met": True}).encode()
    path = tmp_path / "allocation.json"
    path.write_text(
        json.dumps(
            dict(
                schema=1,
                stage="post-G0-pre-G2",
                freeze_sha256="a" * 64,
                g0_statuses_sha256=status_digest(statuses),
                g2_cells=G2_CELLS,
                criteria_sha256=hashlib.sha256(criteria).hexdigest(),
            )
        )
    )
    with pytest.raises(ValueError, match="calibrat"):
        allocation_preflight(path, "a" * 64, statuses, criteria)


def test_first_binding_also_covers_the_verbatim_revision(tmp_path: Path) -> None:
    from ic_study.simulation.v4_gate import (
        manifest,
        numerical_probe,
        preflight,
        source_hashes,
    )

    study = Path(__file__).resolve().parents[2]
    here = study / "experiments/exploratory/detection-boundary-v4"
    docs = study / "research/questions/exploration/2026-09-24-parallel"

    def digest(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    code = source_hashes(study)
    record = dict(
        schema=2,
        status="frozen",
        allocation_binding="post-G0-pre-G2-statuses-sha256",
        code=code,
        code_sha256=hashlib.sha256(
            json.dumps(code, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        artifacts={
            n: digest(here / n) for n in ("criteria-v43.json", "inventory.json")
        },
        amendment_sha256=digest(docs / "detection-boundary-amendment-v4.md"),
        revision_sha256="wrong",
        spec_sha256=digest(docs / "amendment-v4-decision-spec.md"),
        review_findings_sha256=digest(docs / "v4-review-findings.md"),
        review_decisions_sha256=digest(docs / "v4-review-decisions.md"),
        delta_review_decisions_sha256=digest(docs / "v4-delta-review-decisions.md"),
        workers=8,
        shards=8,
        blas_threads=1,
        numerical_probe=numerical_probe(),
        environment=manifest(study)["environment"],
        environment_sha256=manifest(study)["environment_sha256"],
    )
    path = tmp_path / "synthetic-freeze.json"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="revision"):
        preflight(path, study)
    record["revision_sha256"] = digest(docs / "amendment-v4-1-revision.md")
    path.write_text(json.dumps(record))
    assert preflight(path, study) == record
    record["spec_sha256"] = "wrong"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="spec"):
        preflight(path, study)
    record["spec_sha256"] = digest(docs / "amendment-v4-decision-spec.md")
    record["delta_review_decisions_sha256"] = "wrong"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="delta"):
        preflight(path, study)
    record["delta_review_decisions_sha256"] = digest(
        docs / "v4-delta-review-decisions.md"
    )
    record["environment_sha256"] = "wrong"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="environment"):
        preflight(path, study)
    record["environment_sha256"] = manifest(study)["environment_sha256"]
    record["code_sha256"] = "wrong"
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="code"):
        preflight(path, study)


def test_delta_decisions_are_copied_and_item_11_is_verbatim() -> None:
    study = Path(__file__).resolve().parents[2]
    docs = study / "research/questions/exploration/2026-09-24-parallel"
    copied = (docs / "v4-delta-review-decisions.md").read_bytes()
    assert (
        hashlib.sha256(copied).hexdigest()
        == "0c0d2ed04f0728bb4ac0e7e34c17e841c40a1f2594000874c4e095ad23011182"
    )
    item_11 = copied.split(b"## Blocking fixes", 1)[0].split(b"## Item 11", 1)[1]
    assert (
        (docs / "v4-review-decisions.md")
        .read_bytes()
        .endswith((b"## Item 11" + item_11).rstrip(b"\n") + b"\n")
    )


def test_aggregate_only_checks_binding_without_creating_authorization(
    tmp_path: Path,
) -> None:
    from ic_study.simulation.v4_gate import authorize_stage
    from ic_study.simulation.v4_store import SealedStore

    root = SealedStore(tmp_path / "sealed")
    authorize_stage(root, "G2", "freeze", "second", create=False)
    assert root.get_json("authorization-G2") is None
    authorize_stage(root, "G2", "freeze", "second")
    with pytest.raises(ValueError, match="changed"):
        authorize_stage(root, "G2", "freeze", "other", create=False)


def test_completed_shard_cannot_resume_under_another_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dataclasses import replace

    from ic_study.simulation import v4_gate
    from ic_study.simulation.detection_v4 import Cell
    from ic_study.simulation.v4_gate import execute_task
    from ic_study.simulation.v4_plan import GateTask

    monkeypatch.setattr(v4_gate, "run_task", lambda *_args: {"success": False})

    task = GateTask("G1b", 0, 0, Cell(0, 0.7), "invalid-synthetic-scenario")
    provenance: dict[str, object] = {
        "freeze_sha256": "freeze",
        "binding_sha256": "second",
    }
    root = str(tmp_path / "sealed")
    assert execute_task((task, root, provenance)) == {"completed": 1, "failed": 1}
    with pytest.raises(ValueError, match="task binding"):
        execute_task((task, root, {**provenance, "binding_sha256": "other"}))
    with pytest.raises(ValueError, match="task binding"):
        execute_task((replace(task, cell=Cell(0, 0.9)), root, provenance))


def test_aggregation_verifies_each_transported_task_binding(tmp_path: Path) -> None:
    from ic_study.simulation.v4_gate import aggregate
    from ic_study.simulation.v4_store import SealedStore

    task = gate_tasks("G1b")[0]
    root = tmp_path / "sealed"
    store = SealedStore(root / task.key)
    binding = {"freeze_sha256": "freeze", "binding_sha256": "second"}
    store.put_json("task-binding", {"task": task.record(), **binding})
    store.put_json("result", {"success": False})
    assert aggregate("G1b", root, {}, binding=binding)["completed"] == 1
    with pytest.raises(ValueError, match="task binding"):
        aggregate("G1b", root, {}, binding={**binding, "binding_sha256": "other"})


@pytest.mark.parametrize("gap_count, should_stop", [(0, False), (3, True), (8, True)])
def test_second_binding_uses_posterior_predictive_waste_guard(
    tmp_path: Path, gap_count: int, should_stop: bool
) -> None:
    from ic_study.simulation.v4_gate import GapRateStopError

    statuses: list[dict[str, Any]] = [
        dict(
            a=t.cell.share,
            r=t.cell.reliability,
            fits=[dict(family="B", channel="observed", success=True)],
        )
        for t in gate_tasks("G0")
    ]
    selected = [row for row in statuses if 0 < row["a"] <= 0.30]
    assert len(selected) == 54
    outside_allocation = [
        row for row in selected if (row["a"], row["r"]) not in G2_CELLS
    ]
    for row in outside_allocation[:gap_count]:
        row["fits"][0]["success"] = False
    criteria = (
        Path(__file__).resolve().parents[2]
        / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
    ).read_bytes()
    measurement = g0_gap_binding(statuses, G2_CELLS, json.loads(criteria))
    path = tmp_path / "second.json"
    path.write_text(
        json.dumps(
            dict(
                schema=1,
                stage="post-G0-pre-G2",
                freeze_sha256="freeze",
                g0_statuses_sha256=status_digest(statuses),
                criteria_sha256=hashlib.sha256(criteria).hexdigest(),
                g2_cells=G2_CELLS,
                g0_gap_binding=measurement,
            )
        )
    )
    if should_stop:
        with pytest.raises(GapRateStopError) as caught:
            allocation_preflight(path, "freeze", statuses, criteria)
        assert cast(float, caught.value.report["pass_probability"]) < 0.80
    else:
        assert allocation_preflight(path, "freeze", statuses, criteria) == G2_CELLS
        assert cast(float, measurement["pass_probability"]) >= 0.80
    assert measurement["gaps"] == gap_count
    assert measurement["denominator"] == 54
    assert measurement["minimum"] == 0.80
    assert measurement["G2c_allowances"] == [3, 2]


def test_g0_gap_estimate_excludes_strengths_above_g2_range() -> None:
    statuses: list[dict[str, Any]] = [
        dict(
            a=t.cell.share,
            r=t.cell.reliability,
            fits=[dict(family="B", channel="observed", success=True)],
        )
        for t in gate_tasks("G0")
    ]
    high = [row for row in statuses if row["a"] > 0.30]
    assert len(high) == 18
    high[0]["fits"][0]["success"] = False
    criteria = json.loads(
        (
            Path(__file__).resolve().parents[2]
            / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
        ).read_bytes()
    )
    result = g0_gap_binding(statuses, G2_CELLS, criteria)
    assert result["gaps"] == 0
    assert result["denominator"] == 54


def test_amendment_states_corrected_waste_guard() -> None:
    amendment = (
        Path(__file__).resolve().parents[2]
        / "research/questions/exploration/2026-09-24-parallel"
        / "detection-boundary-amendment-v4.md"
    ).read_text()
    assert "54 ajustes" in amendment
    assert "Beta(0,5; 0,5)" in amendment
    assert "beta-binomial" in amendment
    assert "G2c" in amendment
    assert "0,80" in amendment
    assert "Clopper" not in amendment
