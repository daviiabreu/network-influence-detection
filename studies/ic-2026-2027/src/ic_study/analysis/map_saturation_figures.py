"""Render the systematic map's saturation figures from cumulative batch snapshots.

Usage::

    python -m ic_study.analysis.map_saturation_figures \\
        --series SERIES.json --out DIR [--synthetic] [--dpi N]

``SERIES.json`` follows ``ic-study.map-saturation-series.v1``: ``frame`` maps
each mapping field to its codes, ``batches`` holds the cumulative snapshot after
each ranked batch and ``rule`` the stopping thresholds. Coding is multi-label,
so every share uses all included primary works as its denominator.

Transitions mirror ``assess_stopping`` in the workbench's
``prioritized_stopping`` module. From snapshot p to c, a code shifts by
``|c/max(1, n_c) - p/max(1, n_p)|`` over the union of both snapshots' codes,
missing counts being 0, and appears when ``c > 0`` and ``p == 0``. A transition
passes when its maximum shift is at most ``max_shift_pp`` (with the workbench's
1e-12 tolerance), no code appears and the frame version is unchanged: the
protocol restarts the transitions when the frame changes. Provisional
saturation holds at a batch with at least ``min_included`` works whose last
``consecutive_transitions`` transitions pass; the random-remainder audit is not
part of the series. ``manifest.json`` in ``DIR`` records the SHA-256 of the
input and every output and the code commit.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.transforms import offset_copy

from ic_study.analysis.detection_v4_report import code_commit, sha256
from ic_study.analysis.v4_report_figures import (
    DOUBLE,
    MM,
    OKABE_ITO,
    PNG_METADATA,
    style,
)
from ic_study.analysis.v4_report_figures import (
    PDF_METADATA as REPORT_PDF_METADATA,
)
from ic_study.analysis.v4_report_tables import Table, write_table

SERIES_SCHEMA = "ic-study.map-saturation-series.v1"
MANIFEST_SCHEMA = "ic-study.map-saturation-figures-manifest.v1"
SHARE_TOLERANCE = 1e-12
TRAJECTORY = "M1_saturation_trajectory"
SHARES = "M2_category_shares"
TRANSITIONS = "T_M1_transitions"
NOT_REPORTED = "not_reported"
PDF_METADATA = {
    "Creator": "ic_study map-saturation figures",
    "Producer": REPORT_PDF_METADATA["Producer"],
    "CreationDate": None,
    "ModDate": None,
}
CODE_COLORS = tuple(
    OKABE_ITO[name]
    for name in ("orange", "sky", "green", "blue", "vermillion", "purple")
)
CODE_MARKERS = ("o", "s", "^", "D", "v", "P", "X", "<")
NEW_CATEGORY = ("^", "category appears for the first time")
FRAME_CHANGE = ("D", "frame version changed")
GLYPH: dict[str, Any] = {
    "linestyle": "none",
    "markersize": 4,
    "markerfacecolor": "white",
    "markeredgecolor": "0.15",
    "markeredgewidth": 0.8,
}
_MODULES = (
    "map_saturation_figures.py",
    "v4_report_figures.py",
    "v4_report_tables.py",
)
_OPTIONAL_METADATA = frozenset({"source", "generated_for"})


class SeriesError(ValueError):
    """The input is not a valid map-saturation series."""


@dataclass(frozen=True)
class Rule:
    min_included: int
    consecutive_transitions: int
    max_shift_pp: float


@dataclass(frozen=True)
class Snapshot:
    batch_index: int
    included_primary: int
    frame_version: str
    category_counts: Mapping[str, Mapping[str, int]]

    def share(self, field: str, code: str) -> float:
        return self.category_counts[field].get(code, 0) / max(1, self.included_primary)


@dataclass(frozen=True)
class Series:
    frame: Mapping[str, tuple[str, ...]]
    batches: tuple[Snapshot, ...]
    rule: Rule


@dataclass(frozen=True)
class Transition:
    previous: int
    current: int
    included_primary: int
    shift: float
    field: str
    code: str
    appearing: tuple[str, ...]
    frame_changed: bool
    passes: bool
    provisional_saturation: bool


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _object(value: object, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SeriesError(f"{where} must be a JSON object")
    return value


def _keys(
    value: Mapping[str, object],
    where: str,
    required: set[str],
    optional: frozenset[str] = frozenset(),
) -> None:
    missing = sorted(required - value.keys())
    unknown = sorted(value.keys() - required - optional)
    if missing or unknown:
        raise SeriesError(f"{where}: missing keys {missing}, unknown keys {unknown}")


def _rule(value: object) -> Rule:
    raw = _object(value, "rule")
    _keys(raw, "rule", {"min_included", "consecutive_transitions", "max_shift_pp"})
    minimum, window, shift = (
        raw["min_included"],
        raw["consecutive_transitions"],
        raw["max_shift_pp"],
    )
    if not _is_int(minimum) or minimum < 0:
        raise SeriesError("rule.min_included must be a non-negative integer")
    if not _is_int(window) or window < 1:
        raise SeriesError("rule.consecutive_transitions must be a positive integer")
    if (
        not isinstance(shift, int | float)
        or isinstance(shift, bool)
        or not math.isfinite(shift)
        or shift < 0
    ):
        raise SeriesError("rule.max_shift_pp must be a finite non-negative number")
    return Rule(minimum, window, float(shift))


def _frame(value: object) -> dict[str, tuple[str, ...]]:
    raw = _object(value, "frame")
    if not raw:
        raise SeriesError("frame has no fields")
    frame: dict[str, tuple[str, ...]] = {}
    for field, codes in raw.items():
        if (
            not field
            or not isinstance(codes, list)
            or not codes
            or not all(isinstance(code, str) and code for code in codes)
            or len(set(codes)) != len(codes)
        ):
            raise SeriesError(f"frame field {field!r} needs distinct non-empty codes")
        frame[field] = tuple(codes)
    return frame


def _snapshot(
    value: object, position: int, frame: Mapping[str, tuple[str, ...]]
) -> Snapshot:
    raw = _object(value, f"batch at position {position}")
    _keys(
        raw,
        f"batch at position {position}",
        {"batch_index", "included_primary", "frame_version", "category_counts"},
    )
    index, included, version = (
        raw["batch_index"],
        raw["included_primary"],
        raw["frame_version"],
    )
    if not _is_int(index) or index != position:
        raise SeriesError(
            f"batch_index must run consecutively from 1; position {position} "
            f"has {index!r}"
        )
    if not _is_int(included) or included < 0:
        raise SeriesError(f"batch {index}: included_primary must be a count")
    if not isinstance(version, str) or not version:
        raise SeriesError(f"batch {index}: frame_version must be a non-empty string")
    counts = _object(raw["category_counts"], f"batch {index} category_counts")
    missing = sorted(frame.keys() - counts.keys())
    if missing:
        raise SeriesError(f"batch {index} lacks frame fields {missing}")
    unknown = sorted(counts.keys() - frame.keys())
    if unknown:
        raise SeriesError(f"batch {index} has fields outside the frame {unknown}")
    parsed: dict[str, dict[str, int]] = {}
    for field, codes in frame.items():
        field_counts = _object(counts[field], f"batch {index} {field}")
        if not field_counts:
            raise SeriesError(f"batch {index}: {field} has no category counts")
        for code, count in field_counts.items():
            if code not in codes:
                raise SeriesError(f"batch {index}: {field}/{code} is not a frame code")
            if not _is_int(count) or count < 0:
                raise SeriesError(
                    f"batch {index}: {field}/{code} must be a non-negative integer, "
                    f"got {count!r}"
                )
            if count > included:
                raise SeriesError(
                    f"batch {index}: {field}/{code} = {count} exceeds "
                    f"included_primary {included}"
                )
        parsed[field] = dict(field_counts)
    return Snapshot(index, included, version, parsed)


def _check_cumulative(previous: Snapshot, current: Snapshot) -> None:
    where = f"batch {current.batch_index}"
    if current.included_primary < previous.included_primary:
        raise SeriesError(f"{where}: cumulative included_primary decreases")
    for field, new in current.category_counts.items():
        old = previous.category_counts[field]
        for code in sorted(old.keys() | new.keys()):
            if new.get(code, 0) < old.get(code, 0):
                raise SeriesError(
                    f"{where}: cumulative count of {field}/{code} decreases"
                )


def parse_series(data: object) -> Series:
    raw = _object(data, "series")
    _keys(
        raw,
        "series",
        {"schema", "frame", "batches", "rule"},
        _OPTIONAL_METADATA,
    )
    if raw["schema"] != SERIES_SCHEMA:
        raise SeriesError(f"schema must be {SERIES_SCHEMA!r}, got {raw['schema']!r}")
    rule = _rule(raw["rule"])
    frame = _frame(raw["frame"])
    items = raw["batches"]
    if not isinstance(items, list) or not items:
        raise SeriesError("batches must be a non-empty list")
    batches: list[Snapshot] = []
    for position, item in enumerate(items, 1):
        snapshot = _snapshot(item, position, frame)
        if batches:
            _check_cumulative(batches[-1], snapshot)
        batches.append(snapshot)
    return Series(frame, tuple(batches), rule)


def load_series(path: Path) -> Series:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SeriesError(f"{path.name} is not valid JSON: {error}") from error
    return parse_series(data)


def transitions(series: Series) -> tuple[Transition, ...]:
    """Maximum share shift of each transition; ties go to the first sorted code."""
    rule = series.rule
    limit = rule.max_shift_pp / 100 + SHARE_TOLERANCE
    steps: list[Transition] = []
    for previous, current in pairwise(series.batches):
        shift, field, code = -1.0, "", ""
        appearing: list[str] = []
        for name in sorted(series.frame):
            old = previous.category_counts[name]
            new = current.category_counts[name]
            appearing += [
                f"{name}/{key}"
                for key in sorted(new)
                if new[key] > 0 and old.get(key, 0) == 0
            ]
            for key in sorted(old.keys() | new.keys()):
                value = abs(current.share(name, key) - previous.share(name, key))
                if value > shift:
                    shift, field, code = value, name, key
        frame_changed = previous.frame_version != current.frame_version
        passes = shift <= limit and not appearing and not frame_changed
        window = [*(step.passes for step in steps), passes]
        window = window[-rule.consecutive_transitions :]
        steps.append(
            Transition(
                previous=previous.batch_index,
                current=current.batch_index,
                included_primary=current.included_primary,
                shift=shift,
                field=field,
                code=code,
                appearing=tuple(appearing),
                frame_changed=frame_changed,
                passes=passes,
                provisional_saturation=(
                    current.included_primary >= rule.min_included
                    and len(window) == rule.consecutive_transitions
                    and all(window)
                ),
            )
        )
    return tuple(steps)


def _yes(flag: bool) -> str:
    return "yes" if flag else "no"


def transition_table(series: Series, steps: Sequence[Transition]) -> Table:
    rule = series.rule
    return Table(
        TRANSITIONS,
        (
            "from_batch",
            "to_batch",
            "included_primary",
            "max_shift_pp",
            "field",
            "code",
            "appearing",
            "frame_changed",
            "passes",
            "provisional_saturation",
        ),
        tuple(
            (
                str(step.previous),
                str(step.current),
                str(step.included_primary),
                f"{100 * step.shift:.3f}",
                step.field,
                step.code,
                "; ".join(step.appearing) or "none",
                _yes(step.frame_changed),
                _yes(step.passes),
                _yes(step.provisional_saturation),
            )
            for step in steps
        ),
        (
            "max_shift_pp: largest |c/max(1,n_c) - p/max(1,n_p)| x 100 over every "
            "field and every code of either snapshot, missing counts 0; field/code "
            "attains it (ties: first in sorted order)",
            f"passes: max_shift_pp <= {rule.max_shift_pp:g}, no appearing code "
            "(c > 0, p = 0) and an unchanged frame_version",
            f"provisional_saturation: included_primary >= {rule.min_included} and the "
            f"last {rule.consecutive_transitions} transitions pass; the "
            "random-remainder audit is outside this series",
        ),
    )


def _save(
    fig: Figure, directory: Path, name: str, *, dpi: int, synthetic: bool
) -> list[Path]:
    if synthetic:
        fig.text(
            0.5,
            0.5,
            "SYNTHETIC",
            rotation=30,
            fontsize=48,
            color="0.5",
            alpha=0.13,
            ha="center",
            va="center",
            zorder=100,
        )
    stem = directory / (f"{name}_synthetic" if synthetic else name)
    pdf, png = stem.with_suffix(".pdf"), stem.with_suffix(".png")
    fig.savefig(pdf, metadata=PDF_METADATA)
    fig.savefig(png, dpi=dpi, metadata=PNG_METADATA)
    return [pdf, png]


def _flags(step: Transition) -> list[tuple[str, str]]:
    flags = []
    if step.appearing:
        flags.append(NEW_CATEGORY)
    if step.frame_changed:
        flags.append(FRAME_CHANGE)
    return flags


def _reference(ax: Axes, y: float, text: str) -> None:
    ax.axhline(y, color="0.3", linestyle="--", linewidth=0.7, zorder=1)
    ax.text(
        1.01,
        y,
        text,
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        color="0.3",
    )


def figure_trajectory(
    series: Series,
    steps: Sequence[Transition],
    directory: Path,
    *,
    dpi: int,
    synthetic: bool,
) -> list[Path]:
    """M1: maximum share shift per transition over cumulative included works."""
    rule = series.rule
    batches = [snapshot.batch_index for snapshot in series.batches]
    with style():
        fig = Figure(figsize=(DOUBLE, 135 * MM), layout="constrained")
        top, bottom = fig.subplots(2, 1, sharex=True, height_ratios=(3, 2))
        x = [step.current for step in steps]
        y = [100 * step.shift for step in steps]
        top.plot(x, y, color="0.75", linewidth=0.8, zorder=2)
        for passes, marker, color, size in (
            (True, "o", OKABE_ITO["green"], 5.0),
            (False, "X", OKABE_ITO["vermillion"], 6.5),
        ):
            chosen = [
                (a, b)
                for a, b, s in zip(x, y, steps, strict=True)
                if s.passes is passes
            ]
            top.plot(
                [a for a, _ in chosen],
                [b for _, b in chosen],
                linestyle="none",
                marker=marker,
                markersize=size,
                color=color,
                markeredgecolor="white",
                markeredgewidth=0.6,
                zorder=4,
            )
        shown: set[tuple[str, str]] = set()
        for a, b, step in zip(x, y, steps, strict=True):
            top.axvline(a, color="0.92", linewidth=0.5, zorder=0)
            for depth, flag in enumerate(_flags(step)):
                place = offset_copy(
                    top.transData, fig=fig, y=7 + 6 * depth, units="points"
                )
                top.plot([a], [b], marker=flag[0], transform=place, zorder=5, **GLYPH)
                shown.add(flag)
        _reference(top, rule.max_shift_pp, f"{rule.max_shift_pp:g} pp\nthreshold")
        top.set_ylim(0, 1.15 * max([*y, rule.max_shift_pp]))
        top.set_ylabel("Maximum category-share shift (pp)")
        labels = top.secondary_xaxis("top")
        labels.set_xticks(
            x,
            [f"{step.field}\n{step.code}" for step in steps],
            rotation=90,
            fontsize=8,
            multialignment="left",
        )
        labels.tick_params(length=2)
        labels.set_xlabel("Field and code attaining the maximum shift into batch k")
        included = [snapshot.included_primary for snapshot in series.batches]
        bottom.plot(
            batches, included, marker="o", markersize=3.5, color=OKABE_ITO["blue"]
        )
        _reference(bottom, rule.min_included, f"{rule.min_included:,}\nminimum")
        bottom.set_ylim(0, 1.15 * max([*included, rule.min_included]))
        bottom.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
        bottom.set_ylabel("Included primary works")
        bottom.set_xticks(batches)
        bottom.set_xlim(batches[0] - 0.5, batches[-1] + 0.5)
        bottom.set_xlabel("Screening batch k (cumulative snapshot after batch k)")
        handles = [
            Line2D(
                [],
                [],
                linestyle="none",
                marker="o",
                markersize=5,
                color=OKABE_ITO["green"],
                label=(
                    f"passes (≤ {rule.max_shift_pp:g} pp, no new category, same frame)"
                ),
            ),
            Line2D(
                [],
                [],
                linestyle="none",
                marker="X",
                markersize=6.5,
                color=OKABE_ITO["vermillion"],
                label="fails",
            ),
            *(
                Line2D([], [], marker=marker, label=label, **GLYPH)
                for marker, label in (NEW_CATEGORY, FRAME_CHANGE)
                if (marker, label) in shown
            ),
        ]
        fig.legend(handles=handles, loc="outside lower center", ncol=2)
        return _save(fig, directory, TRAJECTORY, dpi=dpi, synthetic=synthetic)


def _code_style(position: int, code: str) -> dict[str, Any]:
    if code == NOT_REPORTED:
        return {
            "color": "0.45",
            "linestyle": (0, (3, 1.5)),
            "marker": "o",
            "markerfacecolor": "white",
        }
    return {
        "color": CODE_COLORS[position % len(CODE_COLORS)],
        "marker": CODE_MARKERS[position % len(CODE_MARKERS)],
    }


def figure_shares(
    series: Series, directory: Path, *, dpi: int, synthetic: bool
) -> list[Path]:
    """M2: cumulative share of every category by batch, one panel per field."""
    fields = list(series.frame)
    columns = 2
    rows = math.ceil(len(fields) / columns)
    batches = [snapshot.batch_index for snapshot in series.batches]
    with style():
        fig = Figure(figsize=(DOUBLE, (rows * 40 + 14) * MM), layout="constrained")
        axes = fig.subplots(rows, columns, sharex=True, sharey=True, squeeze=False)
        for ax, field in zip(axes.flat, fields, strict=False):
            lines: list[tuple[float, str, Line2D]] = []
            colored = 0
            for code in series.frame[field]:
                shares = [
                    100 * snapshot.share(field, code) for snapshot in series.batches
                ]
                kwargs = _code_style(colored, code)
                colored += code != NOT_REPORTED
                (line,) = ax.plot(batches, shares, markersize=3, label=code, **kwargs)
                lines.append((-shares[-1], code, line))
            lines.sort(key=lambda item: item[:2])
            ax.legend(
                handles=[line for *_, line in lines],
                loc="center left",
                bbox_to_anchor=(1.02, 0.5),
                fontsize=8,
                handlelength=2.4,
            )
            ax.text(0.0, 1.02, field, transform=ax.transAxes, ha="left", va="bottom")
            ax.grid(axis="y", color="0.92", linewidth=0.5)
        for index in range(len(fields), rows * columns):
            row, column = divmod(index, columns)
            axes[row][column].remove()
            if row:
                axes[row - 1][column].tick_params(labelbottom=True)
        axes[0][0].xaxis.set_major_locator(MaxNLocator(integer=True))
        axes[0][0].set_xlim(batches[0] - 0.3, batches[-1] + 0.3)
        axes[0][0].set_ylim(-3, 103)
        axes[0][0].set_yticks(range(0, 101, 20))
        fig.supxlabel("Screening batch k", fontsize=8)
        fig.supylabel("Cumulative share of included primary works (%)", fontsize=8)
        return _save(fig, directory, SHARES, dpi=dpi, synthetic=synthetic)


def render(
    series_path: Path, out: Path, *, dpi: int = 300, synthetic: bool = False
) -> Path:
    """Validate the series first, then write figures, the table and the manifest."""
    series = load_series(series_path)
    steps = transitions(series)
    out.mkdir(parents=True, exist_ok=True)
    outputs = figure_trajectory(series, steps, out, dpi=dpi, synthetic=synthetic)
    outputs += figure_shares(series, out, dpi=dpi, synthetic=synthetic)
    outputs += write_table(
        transition_table(series, steps), out, suffix="_synthetic" if synthetic else ""
    )
    here = Path(__file__).resolve().parent
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "synthetic": synthetic,
        "code": {
            **code_commit(),
            "modules_sha256": {name: sha256(here / name) for name in _MODULES},
        },
        "inputs": {"series": {"name": series_path.name, "sha256": sha256(series_path)}},
        "outputs": {path.name: sha256(path) for path in sorted(outputs)},
        "rule": {
            "min_included": series.rule.min_included,
            "consecutive_transitions": series.rule.consecutive_transitions,
            "max_shift_pp": series.rule.max_shift_pp,
        },
        "dpi": dpi,
        "formats": ["pdf", "png"],
    }
    path = out / "manifest.json"
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--series", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args(argv)
    try:
        path = render(args.series, args.out, dpi=args.dpi, synthetic=args.synthetic)
    except SeriesError as error:
        parser.error(f"invalid series: {error}")
    print(f"Figures written; manifest {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
