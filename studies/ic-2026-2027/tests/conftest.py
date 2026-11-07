"""Make research-state dependencies explicit and opt in before collection."""

from __future__ import annotations

from pathlib import Path

import pytest

EXTERNAL_TESTS = {
    (
        "test_release_handoff.py",
        "test_installed_automation_accepts_the_authorized_handoff",
    ): "external_state",
    (
        "test_v4_event_automation.py",
        "test_chain_two_events_real_exports_and_restart",
    ): "external_toolchain",
    (
        "test_v4_event_automation.py",
        "test_chain_failed_compile_creates_successor_attempt",
    ): "external_toolchain",
}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-external-gates",
        action="store_true",
        help="collect/run gates needing separately authorized external state",
    )


def pytest_configure(config: pytest.Config) -> None:
    for name, description in (
        ("external_state", "needs private state or the original installation"),
        ("external_toolchain", "needs third-party publication resources"),
        ("scientific_replay", "replays retained real scientific outputs"),
        ("historical_contract", "binds original monorepo history and framework"),
        ("real_clock", "needs actual elapsed wall time for process supervision"),
    ):
        config.addinivalue_line("markers", f"{name}: {description}")


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool | None:
    if collection_path.name == "test_reproducibility_example.py":
        return not config.getoption("--run-external-gates")
    return None


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    selected, external = [], []
    for item in items:
        name = getattr(item, "originalname", item.name)
        key = (item.path.name, name)
        marker = EXTERNAL_TESTS.get(key)
        if item.path.name == "test_reproducibility_example.py":
            marker = "scientific_replay"
        if marker:
            item.add_marker(getattr(pytest.mark, marker))
        if marker and not config.getoption("--run-external-gates"):
            external.append(item)
        else:
            selected.append(item)
    if external:
        config.hook.pytest_deselected(items=external)
        items[:] = selected
