"""Sealing and checkpoints fail closed and do not disclose scientific estimates."""

import json
from pathlib import Path

import numpy as np
import pytest

from ic_study.simulation.v4_store import SealedStore


def test_private_immutable_checkpoints_and_logged_reads(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = SealedStore(tmp_path / "sealed")
    store.put_array("matching", np.array([[0.123456789]]))
    np.testing.assert_array_equal(store.get_array("matching"), [[0.123456789]])
    store.append("result", {"auc": 0.87654321})
    store.seal()
    assert (store.root.stat().st_mode & 0o777) == 0o700
    assert all(
        (p.stat().st_mode & 0o777) == 0o600 for p in store.root.iterdir() if p.is_file()
    )
    assert capsys.readouterr().out == ""
    assert "read-array" in (store.root / "access.jsonl").read_text()
    with pytest.raises(FileExistsError):
        store.put_array("matching", np.ones((1, 1)))
    record = json.loads((store.root / "seal.json").read_text())
    assert len(record["sha256"]) == 64


def test_refuses_git_tree_and_path_escape(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    with pytest.raises(ValueError, match="checkout"):
        SealedStore(tmp_path / "sealed")
    with pytest.raises(ValueError):
        SealedStore(Path(__file__).parent / "sealed")


def test_seal_detects_mutated_scientific_records(tmp_path: Path) -> None:
    store = SealedStore(tmp_path / "sealed")
    store.put_json("result", {"auc": 0.6})
    store.seal()
    (store.root / "result.json").write_text('{"auc": 0.8}')
    with pytest.raises(ValueError, match="digest"):
        store.get_json("result")


def test_infrastructure_error_stops_without_permanent_gap(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from ic_study.simulation import v4_gate
    from ic_study.simulation.detection_v4 import Cell
    from ic_study.simulation.v4_gate import execute_task
    from ic_study.simulation.v4_plan import GateTask

    task = GateTask("G1b", 0, 0, Cell(0, 0.7), "gaussian-icc0")
    payload: tuple[GateTask, str, dict[str, object]] = (
        task,
        str(tmp_path / "sealed"),
        {},
    )

    def broken(*_args: object) -> None:
        raise OSError("private-value-0.987654321")

    monkeypatch.setattr(v4_gate, "run_task", broken)
    with pytest.raises(OSError):
        execute_task(payload)
    assert capsys.readouterr().out == ""
    store = SealedStore(tmp_path / "sealed" / task.key)
    assert store.get_json("result") is None
    assert not (store.root / "seal.json").exists()


def test_sealed_scientific_output_cannot_be_extended(tmp_path: Path) -> None:
    store = SealedStore(tmp_path / "sealed")
    store.append("estimates", {"auc": 0.5})
    store.seal()
    with pytest.raises(ValueError, match="sealed"):
        store.append("estimates", {"auc": 0.6})
    store.log("read-denied", "example")


def test_worker_output_capture_keeps_estimates_private(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = SealedStore(tmp_path / "sealed")
    with store.capture_output():
        print("auc=0.9123456789")
    assert capsys.readouterr().out == ""
    assert "0.9123456789" in (store.root / "worker-output.log").read_text()
