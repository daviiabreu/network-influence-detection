"""Verification binds executed bytes before checking selected source semantics."""

import copy
import runpy
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def verification() -> dict[str, Any]:
    script = (
        Path(__file__).resolve().parents[2]
        / "experiments/exploratory/detection-boundary-v4/verify_v42.py"
    )
    return runpy.run_path(str(script))


def test_ast_identity_ignores_unrelated_pipeline_changes_but_detects_matching_drift(
    verification: dict[str, Any],
) -> None:
    node = verification["node"]
    original = (
        "BUDGET = 96\ndef matching():\n return BUDGET\ndef pipeline():\n return 0\n"
    )
    changed = original.replace("return 0", "return 1")
    assert node(original, "matching") == node(changed, "matching")
    assert node(original, "BUDGET") == node(changed, "BUDGET")
    assert node(original, "BUDGET") != node(original.replace("96", "64"), "BUDGET")
    assert node(original, "matching") != node(
        original.replace("return BUDGET", "return BUDGET - 1"), "matching"
    )


def test_source_hash_binding_rejects_missing_or_ambiguous_provenance(
    verification: dict[str, Any],
) -> None:
    bound_hash = verification["recorded_source_hash"]
    relative = "simulation/detection_v4.py"
    path = "/private/tmp/snapshot/src/ic_study/" + relative
    assert bound_hash({"code": {path: "digest"}}, relative) == "digest"
    with pytest.raises(ValueError, match="Ambiguous"):
        bound_hash({"code": {}}, relative)
    with pytest.raises(ValueError, match="Ambiguous"):
        bound_hash(
            {"code": {path: "first", "src/ic_study/" + relative: "second"}}, relative
        )


def measured_record() -> dict[str, Any]:
    return {
        "measurements": [
            {
                "success": True,
                "attempts": [
                    {
                        "count": 1024,
                        "evaluations": 40,
                        "status": "interior",
                        "residual": [1e-6, -2e-6],
                        "tolerance": [3e-6, 3e-6],
                        "validation_passed": True,
                        "validation_z": [1.0, -4.0],
                    }
                ],
            }
        ],
    }


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("evaluations", 97, "budget"),
        ("count", 4096, "sample size"),
        ("residual", [1e-6, 4e-6], "matching tolerance"),
        ("tolerance", [float("nan"), 3e-6], "Invalid accepted"),
        ("validation_z", [1.0, 4.000001], "four-SE"),
        ("validation_z", [float("nan"), 0.0], "four-SE"),
        ("validation_passed", False, "Final success"),
    ],
)
def test_measurement_tampering_fails_unchanged_acceptance_checks(
    verification: dict[str, Any],
    field: str,
    value: object,
    message: str,
) -> None:
    measurement = measured_record()
    measurement["measurements"][0]["attempts"][0][field] = value
    with pytest.raises(ValueError, match=message):
        verification["verify_measured_rows"](measurement, 96)


def test_boundary_keeps_strict_l1_tolerance(verification: dict[str, Any]) -> None:
    measurement = measured_record()
    attempt = measurement["measurements"][0]["attempts"][0]
    attempt["status"] = "boundary"
    attempt["residual"][1] = 0.01
    result = verification["verify_measured_rows"](measurement, 96)
    assert result["final_statuses"] == {"boundary": 1}
    attempt["residual"][0] = 4e-6
    with pytest.raises(ValueError, match="matching tolerance"):
        verification["verify_measured_rows"](measurement, 96)


def test_retry_requires_failed_validation_and_receives_own_budget(
    verification: dict[str, Any],
) -> None:
    measurement = measured_record()
    attempts = measurement["measurements"][0]["attempts"]
    attempts.append(copy.deepcopy(attempts[0]))
    attempts[1].update(count=4096, evaluations=96)
    verify = verification["verify_measured_rows"]
    with pytest.raises(ValueError, match="Retry requires"):
        verify(measurement, 96)
    attempts[0].update(validation_passed=False, validation_z=[5.0, 0.0])
    result = verify(measurement, 96)
    assert result["observed_retries"] == 1
    assert result["max_evaluations_by_attempt"] == {"initial": 40, "retry": 96}
    assert "Sample frequency only" in result["retry_interpretation"]
    with pytest.raises(ValueError, match="budget"):
        verify(measurement, 64)
    attempts[0]["status"] = "budget"
    with pytest.raises(ValueError, match="Retry requires"):
        verify(measurement, 96)
