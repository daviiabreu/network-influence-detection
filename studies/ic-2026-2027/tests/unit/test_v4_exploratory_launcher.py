"""Launcher scheduling exercised with short non-scientific worker processes."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from ic_study.simulation import v4_exploratory_x3x7 as f

ORDER = ["x5", "x7", "x3", "x4a", "x4b", "x6a", "x6b"]


def run_supervisor(
    tmp_path: Path,
    names: str,
    fail: str = "",
    *,
    base: int = 0,
    total: int | None = 2,
    stages: str = ",".join(ORDER),
    only: str = "",
    fail_both: bool = False,
) -> tuple[int, list[dict[str, str]]]:
    launcher = f.DECLARATION / "launch-x3x7.sh"
    supervisor = tmp_path / "supervisor.sh"
    supervisor.write_text(
        launcher.read_text().split("<<'EOF'\n", 1)[1].split("\nEOF\n", 1)[0]
    )
    stage_script = f.DECLARATION / "run-x3x7-stages.sh"
    if stage_script.exists():
        destination = (
            tmp_path / "experiments/exploratory/detection-boundary-v4-exploratory"
        )
        destination.mkdir(parents=True)
        shutil.copyfile(stage_script, destination / stage_script.name)
    python = tmp_path / ".venv/bin/python"
    python.parent.mkdir(parents=True)
    python.write_text(
        f"#!{sys.executable}\n"
        + """import json, os, sys, time
name = sys.argv[2].rsplit("_", 1)[1]
command = sys.argv[3]
if command == "describe":
    print(name, "sealed", {"x4": "x4a,x4b", "x6": "x6a,x6b"}.get(name, name))
if command in ("stage-check", "stage-receipt"):
    with open(os.environ["EVENTS"], "a") as stream:
        stream.write(json.dumps({"action": command}) + "\\n")
    sys.exit(91)
if command == "run":
    stage = sys.argv[sys.argv.index("--kind") + 1]
    if "--shard" in sys.argv:
        shard = sys.argv[sys.argv.index("--shard") + 1]
    else:
        shard = str(os.getppid())
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
    def event(action):
        with open(os.environ["EVENTS"], "a") as stream:
            row = {"stage": stage, "shard": shard, "action": action, "only": only}
            stream.write(json.dumps(row) + "\\n")
    event("start")
    from pathlib import Path
    marker = Path(os.environ["EVENTS"]).parent
    slow = shard == os.environ["SLOW_SHARD"]
    if stage == "x3":
        if slow:
            (marker / "slow-started").touch()
        deadline = time.monotonic() + 1
        target = marker / ("fast-advanced" if slow else "slow-started")
        while not target.exists() and time.monotonic() < deadline:
            time.sleep(0.005)
    if stage == "x4a" and not slow:
        (marker / "fast-advanced").touch()

    event("end")
    code = 0
    if stage == os.environ.get("FAIL_STAGE"):
        code = 17 if slow else 23 if os.environ["FAIL_BOTH"] == "1" else 0
    sys.exit(code)
"""
    )
    python.chmod(0o700)
    out = tmp_path / "out"
    (out / "logs").mkdir(parents=True)
    events = tmp_path / "events.jsonl"
    result = subprocess.run(
        [
            "bash",
            str(supervisor),
            str(tmp_path),
            str(out),
            "2",
            "run",
            names,
            only,
            "1",
            str(base),
            "" if total is None else str(total),
        ],
        env={
            **os.environ,
            "EVENTS": str(events),
            "FAIL_STAGE": fail,
            "STAGES": stages,
            "SLOW_SHARD": str(base),
            "FAIL_BOTH": "1" if fail_both else "0",
        },
        capture_output=True,
        text=True,
        timeout=20,
    )
    return result.returncode, [
        json.loads(line) for line in events.read_text().splitlines()
    ] if events.exists() else []


def worker_starts(events: list[dict[str, str]], shard: str) -> list[str]:
    return [
        event["stage"]
        for event in events
        if event.get("shard") == shard and event["action"] == "start"
    ]


def test_split_host_launch_2_runs_all_selected_stages_without_receipts(
    tmp_path: Path,
) -> None:
    status, events = run_supervisor(tmp_path, "x3,x4,x6", base=28, total=64)
    assert status == 0
    assert all(event["action"] in ("start", "end") for event in events)
    for shard in ("28", "29"):
        assert worker_starts(events, shard) == ["x3", "x4a", "x4b", "x6a", "x6b"]


def test_fast_worker_advances_before_slow_worker_finishes_x3(tmp_path: Path) -> None:
    status, events = run_supervisor(tmp_path, "x3,x4")
    assert status == 0
    fast_next = next(
        i
        for i, e in enumerate(events)
        if e == {"stage": "x4a", "shard": "1", "action": "start", "only": ""}
    )
    slow_end = next(
        i
        for i, e in enumerate(events)
        if e == {"stage": "x3", "shard": "0", "action": "end", "only": ""}
    )
    assert fast_next < slow_end


@pytest.mark.parametrize("names", ["x5,x7,x3,x4,x6", "x6,x4,x3,x7,x5"])
def test_each_worker_follows_registered_order(tmp_path: Path, names: str) -> None:
    status, events = run_supervisor(tmp_path, names)
    assert status == 0
    for shard in ("0", "1"):
        assert worker_starts(events, shard) == ORDER


def test_failed_worker_stops_but_other_worker_finishes(tmp_path: Path) -> None:
    status, events = run_supervisor(tmp_path, "x3,x4,x6", fail="x3")
    assert status == 17
    assert worker_starts(events, "0") == ["x3"]
    assert worker_starts(events, "1") == ["x3", "x4a", "x4b", "x6a", "x6b"]
    assert "exit=17" in (tmp_path / "out/logs/worker-0.status").read_text()
    assert "x6 x6b" in (tmp_path / "out/logs/worker-1.status").read_text()


@pytest.mark.parametrize("total", [None, 64])
def test_only_and_stage_subset_apply_with_or_without_shards(
    tmp_path: Path, total: int | None
) -> None:
    status, events = run_supervisor(
        tmp_path,
        "x6,x4,x3",
        base=0 if total is None else 28,
        total=total,
        stages="x6b,x4b,x3",
        only="0-35,40",
    )
    assert status == 0
    shards = {event["shard"] for event in events}
    assert len(shards) == 2
    for shard in shards:
        assert worker_starts(events, shard) == ["x3", "x4b", "x6b"]
    assert {event["only"] for event in events} == {"0-35,40"}


def test_launcher_returns_the_first_worker_failure(tmp_path: Path) -> None:
    status, events = run_supervisor(tmp_path, "x3,x4", fail="x3", fail_both=True)
    assert status == 17
    for shard in ("0", "1"):
        assert worker_starts(events, shard) == ["x3"]
    assert "exit=23" in (tmp_path / "out/logs/worker-1.status").read_text()
