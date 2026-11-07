from __future__ import annotations

import json
from pathlib import Path

import pytest

from ic_study.analysis.fragmentation_pilot import execute, trial_inputs

SPEC = (
    Path(__file__).resolve().parents[2]
    / "experiments/exploratory/fragmentation-pilot-v1/spec.json"
)


def test_frozen_design_counts_pairing_and_sensitivity_inputs() -> None:
    spec = json.loads(SPEC.read_text())
    expected = {"benchmark": 10, "pilot": 112, "sensitivity": 16, "control": 10}
    for phase, count in expected.items():
        trials = trial_inputs(spec, phase)
        assert trials == trial_inputs(
            json.loads(json.dumps(spec, sort_keys=True)), phase
        )
        assert len(trials) == count
        for first, second in zip(trials[::2], trials[1::2], strict=True):
            assert first["model"] == "uniform"
            assert second["model"] == "adaptive"
            assert {k: v for k, v in first.items() if k != "model"} == {
                k: v for k, v in second.items() if k != "model"
            }
    pilot = trial_inputs(spec, "pilot")
    assert all(t in pilot for t in trial_inputs(spec, "sensitivity"))
    assert not any(t in pilot for t in trial_inputs(spec, "benchmark"))


def test_executor_retains_inputs_and_rejects_output_overwrite(tmp_path: Path) -> None:
    spec = json.loads(SPEC.read_text())
    spec["profiles"] = {"pair": {"kind": "complete", "n": 2, "seed_index": 0}}
    spec["phases"]["control"]["profiles"] = ["pair"]
    spec["phases"]["control"]["confidences"] = [1.0]
    spec["phases"]["control"]["opinion_replicates"] = 1
    spec["phases"]["control"]["allowed_max_attempts"] = [10]
    local_spec = tmp_path / "spec.json"
    local_spec.write_text(json.dumps(spec))
    output = tmp_path / "run.jsonl"
    execute(local_spec, "control", output, 10)
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert [r["record"] for r in rows] == ["header", "trial", "trial", "completed"]
    assert rows[0]["source_sha256"]
    assert rows[0]["spec"] == spec
    assert rows[1]["base_edges"] == [[0, 1]]
    assert len(rows[1]["initial_opinions"]) == 2
    assert rows[1]["result"]["status"] == "certified"
    assert rows[-1]["trials"] == 2
    original = output.read_bytes()
    with pytest.raises(FileExistsError):
        execute(local_spec, "control", output, 10)
    assert output.read_bytes() == original
