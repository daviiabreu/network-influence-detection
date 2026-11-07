"""Release on inventory completion, on synthetic sealed stores only."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import stat
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest

from ic_study.simulation.v4_curve import CLOSE, VALID, curve_units, released_curves
from ic_study.simulation.v4_plan import CLOSE_UTC
from ic_study.simulation.v4_store import SealedStore

STUDY = Path(__file__).resolve().parents[2]
SCRIPT = (
    STUDY / "experiments/exploratory/detection-boundary-v4/release_on_completion.py"
)
BEFORE_CLOSE = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    for variable in (
        "OPENBLAS_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "OMP_NUM_THREADS",
    ):
        monkeypatch.setenv(variable, "1")
    spec = importlib.util.spec_from_file_location("release_on_completion", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from ic_study.simulation import v4_curve

    class Clock(datetime):
        @classmethod
        def now(cls, tz: object = None) -> Clock:
            return cls(2026, 10, 19, 2, 59, tzinfo=UTC)

    monkeypatch.setattr(v4_curve, "datetime", Clock)
    return module


def put_curve(root: SealedStore, key: str) -> None:
    SealedStore(root.root / key).put_json("curve", {"unit": key, "status": VALID})


def test_pending_units_look_only_for_the_curve_file(
    script: ModuleType, tmp_path: Path
) -> None:
    units = tuple(
        replace(curve_units()[0], key=key) for key in ("done", "started", "absent")
    )
    (tmp_path / "done").mkdir()
    (tmp_path / "done" / "curve.json").write_bytes(b"not a curve record")
    (tmp_path / "started" / "a0").mkdir(parents=True)
    (tmp_path / "started" / "a0" / "result.json").write_text("{}")
    assert script.pending_units(tmp_path, units) == ["started", "absent"]
    assert script.pending_units(tmp_path / "missing", units[:1]) == ["done"]


def test_release_condition_allows_only_complete_inventory_or_close(
    script: ModuleType,
) -> None:
    before = CLOSE - timedelta(seconds=1)
    assert script.release_condition(before, 0, False) == "inventory-complete"
    assert script.release_condition(CLOSE, 0, False) == "declared-close"
    assert script.release_condition(CLOSE, 414, False) == "declared-close"
    for now, pending, running in (
        (before, 1, False),
        (before, 0, True),
        (CLOSE, 0, True),
    ):
        with pytest.raises(ValueError):
            script.release_condition(now, pending, running)


def test_check_only_prints_completion_and_pending_count_only(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    freeze = tmp_path / "freeze.json"
    freeze.write_text(json.dumps({"code": {"src/module.py": "0" * 64}}))
    monkeypatch.setattr(script, "DEFAULT_SEALED", tmp_path / "sealed-v4-gate")
    units = curve_units()[:2]
    monkeypatch.setattr(script, "curve_units", lambda: units)
    monkeypatch.setattr(script, "curve_workers_running", lambda: False)
    argv = ["release", "--freeze", str(freeze), "--allocation", "-", "--check-only"]
    monkeypatch.setattr(sys, "argv", argv)
    root = SealedStore(script.confirmatory_path(json.loads(freeze.read_bytes())))
    put_curve(root, units[0].key)
    assert script.main() == 0
    assert capsys.readouterr().out == '{"complete": false, "pending": 1}\n'
    put_curve(root, units[1].key)
    assert script.main() == 0
    assert capsys.readouterr().out == '{"complete": true, "pending": 0}\n'
    monkeypatch.setattr(script, "curve_workers_running", lambda: True)
    assert script.main() == 0
    assert capsys.readouterr().out == '{"complete": false, "pending": 0}\n'


def test_release_after_close_follows_the_frozen_path(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[datetime | None] = []

    def frozen(root: SealedStore, *, now: datetime | None = None) -> dict[str, object]:
        calls.append(now)
        return {"inventory": {}, "curves": []}

    monkeypatch.setattr(script, "released_curves", frozen)
    record = tmp_path / "release-record.json"
    after = CLOSE + timedelta(minutes=1)
    script.release(SealedStore(tmp_path / "run"), record, now=after, running=False)
    assert calls == [None]
    assert json.loads(record.read_text())["condition"] == "declared-close"


def test_complete_inventory_releases_early_under_the_declared_close(
    script: ModuleType, tmp_path: Path
) -> None:
    units = curve_units()
    root = SealedStore(tmp_path / "sealed-v4-confirmatory" / "run")
    for unit in units[:-1]:
        put_curve(root, unit.key)
    record = tmp_path / "release-record.json"
    with pytest.raises(ValueError, match="partial"):
        script.release(root, record, now=BEFORE_CLOSE, running=False)
    assert not (root.root / "seal.json").exists() and not record.exists()

    put_curve(root, units[-1].key)
    curves = [root.root / unit.key / "curve.json" for unit in units]
    for path in curves:
        path.chmod(0)
    assert script.pending_units(root.root, units) == []
    for path in curves:
        path.chmod(0o600)

    copy = SealedStore(Path(shutil.copytree(root.root, tmp_path / "copy")))
    frozen = released_curves(copy, now=CLOSE)
    output = script.release(root, record, now=BEFORE_CLOSE, running=False)
    assert output == json.dumps(frozen, allow_nan=False) + "\n"
    released = json.loads(output)
    assert released["inventory"]["closed_utc"] == CLOSE_UTC
    assert [row["status"] for row in released["inventory"]["units"]] == [VALID] * len(
        units
    )
    assert len(released["curves"]) == len(units)
    side = json.loads(record.read_text())
    assert side["condition"] == "inventory-complete"
    assert side["released_utc"] == "2026-10-05T12:00:00Z"
    assert side["released_curves_sha256"] == hashlib.sha256(output.encode()).hexdigest()
    assert side["script_sha256"] == hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
    assert (STUDY.parents[1] / side["amendment"]["path"]).is_file()
    assert stat.S_IMODE(record.stat().st_mode) == 0o600
    published = record.with_name("released-curves.json")
    assert published.read_bytes() == output.encode()
    receipt = record.read_bytes()
    assert script.release(root, record, now=BEFORE_CLOSE, running=False) == output
    assert record.read_bytes() == receipt


@pytest.mark.parametrize("checkpoint", ("output", "receipt"))
def test_interrupted_publication_can_be_retried(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checkpoint: str
) -> None:
    record = tmp_path / "release-record.json"
    published = record.with_name("released-curves.json")
    root = SealedStore(tmp_path / "run")
    rename = script.os.replace

    def interrupted(source: Path, target: Path) -> None:
        if target == (published if checkpoint == "output" else record):
            raise InterruptedError("publication interrupted")
        rename(source, target)

    with monkeypatch.context() as patch:
        patch.setattr(script.os, "replace", interrupted)
        with pytest.raises(InterruptedError):
            script.release(root, record, now=CLOSE, running=False)
    assert not record.exists()
    assert published.exists() == (checkpoint == "receipt")
    output = script.release(root, record, now=CLOSE, running=False)
    assert published.read_bytes() == output.encode()
    assert (
        json.loads(record.read_bytes())["released_curves_sha256"]
        == hashlib.sha256(published.read_bytes()).hexdigest()
    )


@pytest.mark.parametrize("failed_write", (1, 2))
def test_disk_full_never_publishes_a_receipt(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failed_write: int,
) -> None:
    import errno
    from typing import Any

    record = tmp_path / "release-record.json"
    published = record.with_name("released-curves.json")
    published.write_bytes(b"interrupted previous attempt")
    fdopen = script.os.fdopen
    writes = 0

    class Writer:
        def __init__(self, handle: Any) -> None:
            self.handle = handle

        def __enter__(self) -> Writer:
            return self

        def __exit__(self, *args: Any) -> None:
            self.handle.close()

        def __getattr__(self, name: str) -> Any:
            return getattr(self.handle, name)

        def write(self, content: Any) -> None:
            nonlocal writes
            writes += 1
            if writes == failed_write:
                raise OSError(errno.ENOSPC, "simulated disk full")
            self.handle.write(content)

    def failing_fdopen(descriptor: int, mode: str) -> Any:
        handle = fdopen(descriptor, mode)
        return Writer(handle) if "w" in mode else handle

    with monkeypatch.context() as patch:
        patch.setattr(
            script,
            "released_curves",
            lambda root, now=None: {"inventory": {}, "curves": []},
        )
        patch.setattr(script.os, "fdopen", failing_fdopen)
        with pytest.raises(OSError, match="disk full"):
            script.release(
                SealedStore(tmp_path / "run"), record, now=CLOSE, running=False
            )
    assert not record.exists()
    assert published.read_bytes() == b"interrupted previous attempt"
    script.release(SealedStore(tmp_path / "run"), record, now=CLOSE, running=False)
    assert record.exists()


def test_concurrent_attempt_is_refused_without_overwriting_output(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    entered, resume = Event(), Event()
    frozen = script.released_curves

    def waiting(root: SealedStore, *, now: datetime | None = None) -> object:
        entered.set()
        assert resume.wait(10)
        return frozen(root, now=now)

    monkeypatch.setattr(script, "released_curves", waiting)
    root = SealedStore(tmp_path / "run")
    record = tmp_path / "release-record.json"
    with ThreadPoolExecutor(max_workers=1) as pool:
        winner = pool.submit(script.release, root, record, now=CLOSE, running=False)
        try:
            assert entered.wait(10)
            with pytest.raises(BlockingIOError):
                script.release(root, record, now=CLOSE, running=False)
        finally:
            resume.set()
        output = winner.result(timeout=10)
    assert record.with_name("released-curves.json").read_bytes() == output.encode()
    receipt = record.read_bytes()
    assert script.release(root, record, now=CLOSE, running=True) == output
    assert record.read_bytes() == receipt


@pytest.mark.parametrize("corruption", ("missing", "different"))
def test_restart_refuses_a_receipt_without_matching_output(
    script: ModuleType, tmp_path: Path, corruption: str
) -> None:
    record = tmp_path / "release-record.json"
    record.write_text(json.dumps({"released_curves_sha256": "0" * 64}))
    if corruption == "different":
        record.with_name("released-curves.json").write_bytes(b"different bytes")
    with pytest.raises(ValueError, match="receipt"):
        script.release(SealedStore(tmp_path / "run"), record, now=CLOSE, running=False)
