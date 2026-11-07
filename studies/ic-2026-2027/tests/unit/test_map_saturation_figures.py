"""Saturation figures of the systematic map, on hand-computed synthetic series."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from ic_study.analysis.map_saturation_figures import (
    SERIES_SCHEMA,
    SeriesError,
    main,
    parse_series,
    render,
    transitions,
)

FIGURES = ("M1_saturation_trajectory", "M2_category_shares")
TABLE = "T_M1_transitions"


def _batch(
    index: int, included: int, counts: dict[str, dict[str, int]]
) -> dict[str, Any]:
    return {
        "batch_index": index,
        "included_primary": included,
        "frame_version": "frame.1",
        "category_counts": counts,
    }


def _series() -> dict[str, Any]:
    """Four snapshots; the frame lists fields out of sorted order on purpose."""
    return {
        "schema": SERIES_SCHEMA,
        "frame": {
            "model": ["bc", "other", "voter"],
            "design": ["analytical", "simulation"],
            "scale": ["macro", "micro"],
        },
        "batches": [
            _batch(
                1,
                40,
                {
                    "model": {"voter": 20, "bc": 0},
                    "design": {"simulation": 30, "analytical": 10},
                    "scale": {"macro": 10},
                },
            ),
            _batch(
                2,
                50,
                {
                    "model": {"voter": 25, "bc": 2, "other": 5},
                    "design": {"simulation": 35, "analytical": 15},
                    "scale": {"macro": 12, "micro": 0},
                },
            ),
            _batch(
                3,
                500,
                {
                    "model": {"voter": 250, "bc": 20, "other": 50},
                    "design": {"simulation": 350, "analytical": 150},
                    "scale": {"macro": 120, "micro": 0},
                },
            ),
            _batch(
                4,
                510,
                {
                    "model": {"voter": 260, "bc": 20, "other": 51},
                    "design": {"simulation": 357, "analytical": 153},
                    "scale": {"macro": 122, "micro": 0},
                },
            ),
        ],
        "rule": {
            "min_included": 500,
            "consecutive_transitions": 2,
            "max_shift_pp": 2.0,
        },
    }


def _write(path: Path, data: dict[str, Any]) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _outputs(directory: Path) -> dict[str, bytes]:
    return {path.name: path.read_bytes() for path in sorted(directory.iterdir())}


# Stopping-rule transitions -------------------------------------------------


def test_transitions_match_hand_computed_shares() -> None:
    first, second, third = transitions(parse_series(_series()))
    # 1 -> 2 (40 -> 50 works): voter 25/50 - 20/40 = 0; bc 2/50 - 0/40 = 0.04 after
    # an explicit zero; other 5/50 - 0 = 0.10 although absent from batch 1;
    # simulation and analytical shift by 0.05, macro by 0.01; micro is absent
    # before and zero after, so it neither shifts nor appears.
    assert (first.previous, first.current, first.included_primary) == (1, 2, 50)
    assert first.shift == pytest.approx(0.10)
    assert (first.field, first.code) == ("model", "other")
    assert first.appearing == ("model/bc", "model/other")
    assert not first.passes and not first.provisional_saturation
    # 2 -> 3 multiplies every count by ten: the tie at zero goes to the first
    # field and code in sorted order, and the failed 1 -> 2 blocks saturation.
    assert second.shift == 0.0
    assert (second.field, second.code) == ("design", "analytical")
    assert second.passes and not second.provisional_saturation
    # 3 -> 4: voter moves by 260/510 - 250/500 = 0.98 pp, the largest shift.
    assert third.shift == pytest.approx(260 / 510 - 0.5)
    assert (third.field, third.code, third.appearing) == ("model", "voter", ())
    assert third.passes and third.provisional_saturation


def test_threshold_is_inclusive_under_the_workbench_tolerance() -> None:
    data = _series()
    data["frame"] = {"model": ["other", "voter"]}
    data["batches"] = [
        _batch(1, 100, {"model": {"voter": 12, "other": 88}}),
        _batch(2, 100, {"model": {"voter": 14, "other": 88}}),
        _batch(3, 100, {"model": {"voter": 17, "other": 88}}),
    ]
    at, above = transitions(parse_series(data))
    assert at.shift > 0.02  # 14/100 - 12/100 rounds to 0.020000000000000018
    assert at.passes
    assert above.shift == pytest.approx(0.03)
    assert not above.passes


def test_frame_change_fails_the_transition_and_restarts_the_window() -> None:
    data = _series()
    for batch in data["batches"][2:]:
        batch["frame_version"] = "frame.2"
    _, changed, after = transitions(parse_series(data))
    assert changed.shift == 0.0 and changed.frame_changed and not changed.passes
    assert after.passes and not after.provisional_saturation


# Validation ------------------------------------------------------------------

Mutation = Callable[[dict[str, Any]], object]


def _counts(data: dict[str, Any], batch: int, field: str) -> dict[str, Any]:
    counts: dict[str, Any] = data["batches"][batch]["category_counts"][field]
    return counts


MUTATIONS: list[tuple[str, Mutation, str]] = [
    (
        "index_not_from_one",
        lambda d: d["batches"][0].update(batch_index=0),
        "consecutively from 1",
    ),
    (
        "index_gap",
        lambda d: d["batches"][2].update(batch_index=4),
        "consecutively from 1",
    ),
    (
        "included_decreases",
        lambda d: d["batches"][1].update(included_primary=600),
        "included_primary decreases",
    ),
    (
        "count_decreases",
        lambda d: _counts(d, 2, "model").update(voter=24),
        "model/voter decreases",
    ),
    (
        "count_dropped",
        lambda d: _counts(d, 2, "model").pop("bc"),
        "model/bc decreases",
    ),
    (
        "field_missing",
        lambda d: d["batches"][1]["category_counts"].pop("design"),
        "lacks frame fields",
    ),
    (
        "field_outside_frame",
        lambda d: d["batches"][1]["category_counts"].update(topology={"lattice": 1}),
        "outside the frame",
    ),
    (
        "field_without_counts",
        lambda d: d["batches"][0]["category_counts"].update(scale={}),
        "no category counts",
    ),
    (
        "code_outside_frame",
        lambda d: _counts(d, 0, "model").update(majority=1),
        "not a frame code",
    ),
    (
        "negative_count",
        lambda d: _counts(d, 0, "model").update(voter=-1),
        "non-negative integer",
    ),
    (
        "fractional_count",
        lambda d: _counts(d, 0, "model").update(voter=2.5),
        "non-negative integer",
    ),
    (
        "boolean_count",
        lambda d: _counts(d, 0, "model").update(bc=True),
        "non-negative integer",
    ),
    (
        "count_above_included",
        lambda d: _counts(d, 0, "design").update(simulation=41),
        "exceeds included_primary",
    ),
    ("wrong_schema", lambda d: d.update(schema="map-series.v0"), "schema must be"),
    (
        "extra_batch_key",
        lambda d: d["batches"][0].update(complete=True),
        "unknown keys",
    ),
    ("no_batches", lambda d: d.update(batches=[]), "non-empty list"),
    (
        "invalid_rule",
        lambda d: d["rule"].update(consecutive_transitions=0),
        "consecutive_transitions",
    ),
]


@pytest.mark.parametrize(
    ("mutate", "message"),
    [(mutate, message) for _, mutate, message in MUTATIONS],
    ids=[name for name, *_ in MUTATIONS],
)
def test_series_validation_rejects(mutate: Mutation, message: str) -> None:
    data = _series()
    parse_series(data)
    mutate(data)
    with pytest.raises(SeriesError, match=message):
        parse_series(data)


# Rendering -------------------------------------------------------------------


def test_render_writes_figures_table_and_manifest(tmp_path: Path) -> None:
    series = _write(tmp_path / "series.json", _series())
    files = _outputs(render(series, tmp_path / "out", dpi=40).parent)
    assert set(files) == {
        *(f"{name}.{kind}" for name in FIGURES for kind in ("pdf", "png")),
        f"{TABLE}.csv",
        f"{TABLE}.tex",
        "manifest.json",
    }
    assert not any(b"/CreationDate" in files[f"{name}.pdf"] for name in FIGURES)
    manifest = json.loads(files["manifest.json"])
    assert manifest["outputs"] == {
        name: hashlib.sha256(content).hexdigest()
        for name, content in files.items()
        if name != "manifest.json"
    }
    assert manifest["inputs"]["series"] == {
        "name": "series.json",
        "sha256": hashlib.sha256(series.read_bytes()).hexdigest(),
    }
    assert manifest["synthetic"] is False and "commit" in manifest["code"]
    rows = list(csv.DictReader(io.StringIO(files[f"{TABLE}.csv"].decode())))
    assert [
        (
            row["max_shift_pp"],
            row["field"],
            row["code"],
            row["appearing"],
            row["passes"],
            row["provisional_saturation"],
        )
        for row in rows
    ] == [
        ("10.000", "model", "other", "model/bc; model/other", "no", "no"),
        ("0.000", "design", "analytical", "none", "yes", "no"),
        ("0.980", "model", "voter", "none", "yes", "yes"),
    ]
    tex = files[f"{TABLE}.tex"].decode()
    assert r"\begin{tabular}" in tex
    assert r"model/bc; model/other" in tex


def test_two_renders_are_byte_identical(tmp_path: Path) -> None:
    series = _write(tmp_path / "series.json", _series())
    first = _outputs(render(series, tmp_path / "one", dpi=60).parent)
    second = _outputs(render(series, tmp_path / "two", dpi=60).parent)
    assert {name for name in first if name.endswith(".png")} == {
        f"{name}.png" for name in FIGURES
    }
    assert first == second


def test_synthetic_render_is_watermarked_and_named(tmp_path: Path) -> None:
    series = _write(tmp_path / "series.json", _series())
    real = _outputs(render(series, tmp_path / "real", dpi=40).parent)
    fake = _outputs(render(series, tmp_path / "fake", dpi=40, synthetic=True).parent)
    for name in FIGURES:
        assert fake[f"{name}_synthetic.png"] != real[f"{name}.png"]
    assert f"{TABLE}_synthetic.csv" in fake
    assert json.loads(fake["manifest.json"])["synthetic"] is True


def test_single_snapshot_renders_without_transitions(tmp_path: Path) -> None:
    data = _series()
    data["batches"] = data["batches"][:1]
    out = tmp_path / "out"
    render(_write(tmp_path / "series.json", data), out, dpi=40)
    assert len((out / f"{TABLE}.csv").read_text().splitlines()) == 1
    assert (out / f"{FIGURES[0]}.png").exists()


def test_cli_renders_and_rejects_an_invalid_series_before_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    series = _write(tmp_path / "series.json", _series())
    out = tmp_path / "out"
    argv = ["--series", str(series), "--out", str(out), "--synthetic", "--dpi", "30"]
    assert main(argv) == 0
    manifest = json.loads((out / "manifest.json").read_text())
    assert (manifest["dpi"], manifest["synthetic"]) == (30, True)
    assert (out / f"{FIGURES[1]}_synthetic.pdf").exists()
    broken = _series()
    broken["batches"][1]["batch_index"] = 3
    refused = tmp_path / "refused"
    with pytest.raises(SystemExit) as stop:
        main(
            [
                "--series",
                str(_write(tmp_path / "broken.json", broken)),
                "--out",
                str(refused),
            ]
        )
    assert stop.value.code == 2
    assert "consecutively from 1" in capsys.readouterr().err
    assert not refused.exists()
