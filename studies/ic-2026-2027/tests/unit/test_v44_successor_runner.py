"""Amendment v4.4 worker: one recorded projection error becomes a sealed gap."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

from ic_study.simulation.v4_store import SealedStore

STUDY = Path(__file__).resolve().parents[2]
RUNNER = (
    STUDY
    / "experiments/exploratory/detection-boundary-v4-successor-v44/v44_run_curve.py"
)


def load(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def successor() -> ModuleType:
    return load(RUNNER, "v44_run_curve_under_test")


@pytest.fixture
def projection(tmp_path: Path) -> ModuleType:
    source = tmp_path / "detection_boundary_v4.py"
    source.write_text(
        "def project_shift(message='ill-conditioned local profile'):\n"
        "    raise ValueError(message)\n"
        "def other_function():\n"
        "    raise ValueError('ill-conditioned local profile')\n"
    )
    return load(source, f"fake_projection_{tmp_path.name}")


def raise_in(call: object) -> BaseException:
    try:
        call()  # type: ignore[operator]
    except BaseException as error:
        return error
    raise AssertionError("expected an exception")


def test_only_the_recorded_projection_error_is_recognized(
    successor: ModuleType, projection: ModuleType
) -> None:
    assert successor.raised_by_projection(raise_in(projection.project_shift))
    assert not successor.raised_by_projection(
        raise_in(lambda: projection.project_shift("other message"))
    )
    assert not successor.raised_by_projection(raise_in(projection.other_function))
    assert not successor.raised_by_projection(
        raise_in(lambda: (_ for _ in ()).throw(RuntimeError(successor.MESSAGE)))
    )


def test_recorded_error_becomes_a_sealed_propagation_gap(
    successor: ModuleType, projection: ModuleType, tmp_path: Path
) -> None:
    cell = tmp_path / "unit" / "a2"

    def execute_cell(unit: object, index: int, directory: Path) -> None:
        SealedStore(directory).put_json("provenance", {"unit": "t2-test"})
        projection.project_shift()

    successor.successor_worker(
        object(), 2, cell, execute_cell=execute_cell, store_type=SealedStore
    )
    store = SealedStore(cell)
    record = store.get_json("result")
    assert record is not None and record == successor.gap_record()
    assert record["success"] is False and record["attempts"] == []
    gap = record["successor_gap"]
    assert isinstance(gap, dict)
    assert gap["kind"] == "propagation"
    assert gap["successor_sha256"] == successor.SELF_SHA256
    assert (cell / "seal.json").exists()
    with pytest.raises(ValueError, match="already sealed"):
        store.put_json("result", {"success": True})


def test_every_other_failure_still_ends_the_shard(
    successor: ModuleType, projection: ModuleType, tmp_path: Path
) -> None:
    failures = [
        lambda: projection.project_shift("singular matrix"),
        projection.other_function,
        lambda: (_ for _ in ()).throw(KeyError("x")),
    ]
    for number, failure in enumerate(failures):
        cell = tmp_path / f"cell-{number}"

        def execute_cell(
            unit: object, index: int, directory: Path, failure: object = failure
        ) -> None:
            failure()  # type: ignore[operator]

        with pytest.raises((ValueError, KeyError)):
            successor.successor_worker(
                object(), 0, cell, execute_cell=execute_cell, store_type=SealedStore
            )
        assert SealedStore(cell).get_json("result") is None


def test_an_existing_result_is_never_overwritten(
    successor: ModuleType, projection: ModuleType, tmp_path: Path
) -> None:
    cell = tmp_path / "unit" / "a4"
    SealedStore(cell).put_json("result", {"success": True})

    def execute_cell(unit: object, index: int, directory: Path) -> None:
        projection.project_shift()

    with pytest.raises(ValueError, match="ill-conditioned"):
        successor.successor_worker(
            object(), 4, cell, execute_cell=execute_cell, store_type=SealedStore
        )
    assert SealedStore(cell).get_json("result") == {"success": True}


def test_frozen_runner_runs_unchanged_with_only_the_worker_replaced(
    successor: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    frozen = tmp_path / "frozen" / "experiments/exploratory/detection-boundary-v4"
    frozen.mkdir(parents=True)
    freeze = frozen / "freeze-v4.json"
    freeze.write_text("{}")
    calls = tmp_path / "calls.json"
    (frozen / "run_curve.py").write_text(
        "import json, sys\n"
        "def schedule(root, provenance, *, shard=0, shards=1, worker=None):\n"
        "    return {'default': True}\n"
        "def main():\n"
        "    outcome = schedule('root', {}, shard=3, shards=8)\n"
        f"    open({str(calls)!r}, 'w').write(json.dumps(sorted(outcome)))\n"
        "    return 0\n"
    )
    captured: dict[str, object] = {}

    def fake_schedule(root: object, provenance: object, **kwargs: object) -> object:
        captured.update(kwargs)
        return {"tier_blocked": 0}

    import ic_study.simulation.v4_curve as curve

    monkeypatch.setattr(curve, "schedule", fake_schedule)
    monkeypatch.setattr(sys, "argv", ["v44_run_curve.py", "--freeze", str(freeze)])
    assert successor.main() == 0
    assert json.loads(calls.read_text()) == ["tier_blocked"]
    assert captured["shard"] == 3 and captured["shards"] == 8
    worker = captured["worker"]
    assert worker.func is successor.successor_worker  # type: ignore[attr-defined]
    assert worker.keywords["execute_cell"] is curve.execute_cell  # type: ignore[attr-defined]
