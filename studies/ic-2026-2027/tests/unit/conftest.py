"""Synthetic evidence bindings for exploratory aggregate fixtures."""

import hashlib
import json
import platform
import sys
from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import datetime, timedelta, tzinfo
from decimal import Decimal
from pathlib import Path
from typing import Any, Self

import pytest

from ic_study.analysis.v4_report_schema import GateRecords
from ic_study.simulation import v4_curve, v4_exploratory
from ic_study.simulation import v4_exploratory_x3x7 as f

CLOCK_FILES = frozenset(
    {
        "test_v4_curve.py",
        "test_v4_exploratory_x1b.py",
        "test_v4_exploratory_x3.py",
        "test_v4_exploratory_x3x7.py",
        "test_v4_exploratory_x4.py",
        "test_v4_exploratory_x5.py",
        "test_v4_exploratory_x6.py",
        "test_v4_exploratory_x7.py",
    }
)


def fixed_datetime(instant: datetime) -> type[datetime]:
    class ScientificTestClock(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> Self:
            return cls.fromtimestamp(instant.timestamp(), tz)

    return ScientificTestClock


@pytest.fixture(autouse=True)
def scientific_test_clocks(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    if request.node.path.name not in CLOCK_FILES or request.node.get_closest_marker(
        "real_clock"
    ):
        return
    exploratory_time = f.WINDOW_CLOSE - timedelta(days=1)
    for module, instant in (
        (v4_curve, v4_curve.CLOSE - timedelta(days=1)),
        (v4_exploratory, exploratory_time),
        (f, exploratory_time),
    ):
        monkeypatch.setattr(module, "datetime", fixed_datetime(instant))


@pytest.fixture
def catalog_presentation_proof(
    tmp_path: Path,
) -> Callable[..., None]:
    def verify(
        catalog: dict[str, str],
        previous: str,
        gate: GateRecords | None = None,
        *,
        wilson95: Sequence[float] | None = None,
    ) -> None:
        added = {}
        for key, value in catalog.items():
            if key == "v4.tab.T3.G0.status-dependency-gap.value":
                assert gate is not None
                assert int(value) == sum(
                    fit.gap == "dependency" for fit in gate.g0_fits
                )
            elif key in {
                "v4.gate.G1b.completed_prose",
                "v4.gate.G1b.exceeds_floor_count_prose",
                "v4x.x3.sizes.matching_prose",
                "v4x.x3.sizes.retry_matching_prose",
                "v4x.x4.sizes.check_prose",
                "v4x.x6.x6a.recorded_prose",
                "v4x.x6.x6a.units_prose",
                "v4x.x6.sizes.population_pairs_prose",
            }:
                assert value == f"{int(catalog[key.removesuffix('_prose')]):,}"
            elif key.startswith("v4x.x6.x6a.band.vs_d1.primary.wilson95.prose_"):
                assert wilson95 is not None
                lower = key.endswith("lower")
                endpoint = Decimal(str(wilson95[0 if lower else 1]))
                cuts = [
                    Decimal(catalog["v4x.protocol.x6." + name])
                    for name in (("conservative",) if lower else ("nominal", "failure"))
                ]
                decimals = len(value.partition(".")[2])
                assert decimals >= 3
                assert value == f"{endpoint:.{decimals}f}"
                for precision in range(3, decimals + 1):
                    ties = any(
                        endpoint != cut
                        and f"{endpoint:.{precision}f}" == f"{cut:.{precision}f}"
                        for cut in cuts
                    )
                    assert ties == (precision < decimals)
            else:
                continue
            added[key] = value
        baseline = {k: v for k, v in catalog.items() if k not in added}

        def digest(values: dict[str, str]) -> str:
            raw = (
                json.dumps(values, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
            ).encode()
            return hashlib.sha256(raw).hexdigest()

        assert digest(baseline) == previous
        (tmp_path / "t58-catalog-proof.json").write_text(
            json.dumps(
                {
                    "pinned": previous,
                    "new": digest(catalog),
                    "added_keys": added,
                    "removing_only_documented_additions_reproduces_the_pin": True,
                },
                indent=2,
            )
            + "\n"
        )

    return verify


@pytest.fixture
def synthetic_analysis() -> Callable[
    [Path, f.Analysis, tuple[f.Precondition, ...]], f.Analysis
]:
    def prepare(
        out: Path, analysis: f.Analysis, specs: tuple[f.Precondition, ...]
    ) -> f.Analysis:
        f.require_sealed_location(out)
        for spec in specs:
            f.write_private_json(spec.verification(out), {"synthetic": True})
        digests = {spec.name: f._digest(spec.verification(out)) for spec in specs}

        def compute(index: int) -> dict[str, Any]:
            record = analysis.compute(index)
            record["verification_sha256"] = digests
            return record

        return replace(
            analysis, modules=specs[0].modules, verification=digests, compute=compute
        )

    return prepare


FROZEN_HOST_PINS = frozenset(
    {
        "test_detection_panel.py::test_zero_share_panel_keeps_frozen_calibration_bytes",
        "test_v42_solver.py::"
        "test_inner_updates_slope_when_trait_weight_attenuates_phi_derivative",
    }
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if sys.platform == "darwin" and platform.machine() == "arm64":
        return
    skip = pytest.mark.skip(
        reason="Bitwise pins are defined on the frozen macOS arm64 host"
    )
    for item in items:
        name = getattr(item, "originalname", item.name)
        if f"{item.path.name}::{name}" in FROZEN_HOST_PINS:
            item.add_marker(skip)
