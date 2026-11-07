"""Publication figures for the a*(r) detection-boundary paper.

Springer iicol widths (76 mm single, 160 mm double column), Okabe-Ito colours, 8 pt
text, no in-figure titles and byte-deterministic PDF/PNG output. Strength is an
ordinal axis over the frozen grid G: the protocol forbids interpolating
strengths, so no line ever joins estimates across a or r.
"""

from __future__ import annotations

import textwrap
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from inspect import signature
from pathlib import Path
from typing import Any, cast

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from ic_study.analysis.detection_boundary_v4 import profile_match
from ic_study.analysis.shp_reliability import STARTS_FAILURES, STARTS_NUMERICAL_ERROR
from ic_study.analysis.v4_report_schema import (
    CALIBRATION_EXPOSED_R,
    CRITICAL_FLOOR,
    CROSSWALK_REFERENCES,
    FAIL,
    FAMILIES,
    GAP_KINDS,
    GATE_STAGES,
    IN_PROGRESS,
    INVALID,
    MAIN_CURVE_INVALID,
    NOT_STARTED,
    PARTIAL,
    PASS,
    STATUSES,
    SUCCESSOR_SOURCE,
    TARGET,
    VALID,
    Boundary,
    Crosswalk,
    Curve,
    GateRecords,
    Release,
    ShpAnchor,
    grid_index,
    unit_catalog,
)
from ic_study.analysis.v4_report_tables import cell_label, failure_reason
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES
from ic_study.simulation.v4_plan import SCENARIOS

SOLVER_BUDGET: int = signature(profile_match).parameters["budget"].default
MM = 1 / 25.4
SINGLE = 76 * MM
DOUBLE = 160 * MM
OKABE_ITO = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky": "#56B4E9",
    "green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
}
FAMILY_COLOR = {
    "B": OKABE_ITO["black"],
    "A": OKABE_ITO["orange"],
    "C": OKABE_ITO["sky"],
    "D": OKABE_ITO["green"],
    "E": OKABE_ITO["purple"],
}
FAMILY_LABEL = {
    "A": "A: autoregressive persistence",
    "B": "B: trait-plus-autoregressive persistence",
    "C": "C: altered response channel",
    "D": "D: state-dependent persistence",
    "E": "E: mover\u2013stayer persistence",
}
STATUS_COLOR = {
    NOT_STARTED: "#E5E5E5",
    PARTIAL: OKABE_ITO["yellow"],
    INVALID: OKABE_ITO["vermillion"],
    VALID: OKABE_ITO["green"],
}
STATUS_LABEL = {
    VALID: "complete valid",
    INVALID: "complete invalid",
    PARTIAL: "partial at operational close",
    NOT_STARTED: "not started",
}
# F4(a): accepted fits, then each gap kind of the final attempt.
GAP_COLOR: dict[str | None, str] = {
    None: OKABE_ITO["green"],
    "screened": OKABE_ITO["yellow"],
    "family_limit": OKABE_ITO["orange"],
    "solver": OKABE_ITO["vermillion"],
    "validation": OKABE_ITO["purple"],
    "dependency": OKABE_ITO["blue"],
    "propagation": OKABE_ITO["sky"],
}
VERDICT_COLOR: dict[str | None, str] = {
    PASS: OKABE_ITO["green"],
    FAIL: OKABE_ITO["vermillion"],
    IN_PROGRESS: OKABE_ITO["sky"],
    None: "#E5E5E5",
}
MAIN_CURVE_NOTE = (
    f"{MAIN_CURVE_INVALID}: a tier-1 B unit is not {STATUS_LABEL[VALID]}; "
    "B boundaries are reported with this mark"
)
BEYOND_Y = len(GRID)  # ordinal row above a = 0.9: "not reached on the grid"
STRIP_Y = -1.4  # status strip below a = 0 for units without a valid curve
CROSSWALK_Y = STRIP_Y - 1.4  # F6 only: synthetic crosswalk row below the strip
STARTS_Y = BEYOND_Y + 0.4  # F6 only: STARTS point and Wald interval
STARTS_COLOR = OKABE_ITO["vermillion"]
CROSSWALK_COLOR = OKABE_ITO["green"]
CROSSWALK_MARKERS = dict(zip(CROSSWALK_REFERENCES, ("o", "^", "s"), strict=True))
STARTS_SHORT = dict(
    zip(
        (*STARTS_FAILURES, STARTS_NUMERICAL_ERROR),
        (
            "non-convergence",
            "information not PD",
            "variance below 1e-4 floor",
            "|φ| > 0.99",
            "r_t ∉ (0, 1)",
            "numerical error",
        ),
        strict=True,
    )
)
SMALL_LARGE_Y = grid_index(0.03) + 0.5
STYLE: dict[str, Any] = {
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "lines.linewidth": 1.0,
    "lines.markersize": 4,
    "legend.frameon": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "path",
    "svg.hashsalt": "ic-v4-report",
    "path.simplify": False,
    "hatch.linewidth": 0.5,
}
PDF_METADATA = {
    "Creator": "ic_study detection-v4 report",
    "Producer": f"Matplotlib {matplotlib.__version__}",
    "CreationDate": None,
    "ModDate": None,
}
PNG_METADATA = {"Software": "matplotlib"}


@dataclass(frozen=True)
class Render:
    directory: Path
    dpi: int = 300
    synthetic: bool = False
    formats: tuple[str, ...] = ("pdf", "png")

    def stem(self, name: str) -> str:
        return f"{name}_synthetic" if self.synthetic else name


@contextmanager
def style() -> Iterator[None]:
    with plt.rc_context(cast(Any, STYLE)):
        yield


def save(fig: Figure, render: Render, name: str) -> list[Path]:
    if render.synthetic:
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
    stem = render.directory / render.stem(name)
    paths = []
    if "pdf" in render.formats:
        paths.append(stem.with_suffix(".pdf"))
        fig.savefig(paths[-1], metadata=PDF_METADATA)
    if "png" in render.formats:
        paths.append(stem.with_suffix(".png"))
        fig.savefig(paths[-1], dpi=render.dpi, metadata=PNG_METADATA)
    plt.close(fig)
    return paths


def _panel_tag(ax: Axes, text: str) -> None:
    ax.text(0.0, 1.01, text, transform=ax.transAxes, ha="left", va="bottom")


def _main_curve_mark(ax: Axes) -> None:
    """Visible invalidation mark on B (amendment v4: boundaries stay reported)."""
    ax.text(
        1.0,
        0.93,
        MAIN_CURVE_INVALID,
        transform=ax.transAxes,
        ha="right",
        va="top",
        color="black",
        fontweight="bold",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85},
    )


def _r_axis(ax: Axes, *, labels: bool = True) -> None:
    ax.set_xticks(RELIABILITIES)
    ax.set_xticklabels(
        [
            f"{r:.2f}" + ("†" if r == CALIBRATION_EXPOSED_R else "")
            for r in RELIABILITIES
        ]
        if labels
        else [],
        rotation=90,
    )
    ax.axvspan(
        CALIBRATION_EXPOSED_R - 0.018,
        CALIBRATION_EXPOSED_R + 0.018,
        color="0.93",
        zorder=0,
        linewidth=0,
    )


def _strength_axis(ax: Axes, *, labels: bool = True, crosswalk: bool = False) -> None:
    ticks = [STRIP_Y, *range(len(GRID)), BEYOND_Y]
    names = ["status", *[f"{a:g}" for a in GRID], ">0.9"]
    if crosswalk:
        ticks.insert(0, CROSSWALK_Y)
        names.insert(0, "crosswalk")
        ax.axhline(STRIP_Y - 0.7, color="0.6", linewidth=0.5)
    ax.set_yticks(ticks)
    ax.set_yticklabels(names if labels else [])
    ax.set_ylim((CROSSWALK_Y if crosswalk else STRIP_Y) - 0.8, BEYOND_Y + 0.7)
    ax.axhline(-0.7, color="0.6", linewidth=0.5)
    ax.axhline(len(GRID) - 0.5, color="0.6", linewidth=0.5, linestyle=(0, (1, 2)))
    ax.axhline(SMALL_LARGE_Y, color="0.75", linewidth=0.5, linestyle="--", zorder=0)


def _curves_by(release: Release, family: str) -> dict[float, tuple[str, Curve | None]]:
    """Main-grid unit of one family per r: (D9 status, curve if completed)."""
    out: dict[float, tuple[str, Curve | None]] = {}
    for key, meta in unit_catalog().items():
        if meta.main and meta.family == family:
            out[meta.r] = (release.statuses[key], release.curves.get(key))
    return out


def _boundary_marks(
    ax: Axes,
    x: float,
    boundary: Boundary,
    color: str,
    *,
    filled: bool,
    width: float,
) -> None:
    face = color if filled else "white"
    if boundary.interval is not None:
        ends = []
        for index, value in enumerate(boundary.interval):
            cut = boundary.end_censored_at(index)
            if value is not None:
                ends.append(float(grid_index(value)))
            elif cut is not None:
                ends.append(float(grid_index(cut)))
            else:
                ends.append(float(BEYOND_Y))
        lo, hi = boundary.interval
        style = "-" if hi is not None and lo is not None else (0, (2, 1))
        ax.plot([x, x], ends, color=color, linewidth=width, linestyle=style)
        if hi is None and boundary.end_censored_at(1) is None:
            ax.plot(x, BEYOND_Y, marker="^", color=color, markersize=3)
    if boundary.point is not None:
        ax.plot(
            x,
            grid_index(boundary.point),
            marker="o",
            markerfacecolor=face,
            markeredgecolor=color,
            linestyle="none",
            zorder=5,
        )
    elif boundary.censored_at is not None:
        ax.plot(
            x,
            grid_index(boundary.censored_at),
            marker="s",
            markerfacecolor="white",
            markeredgecolor=color,
            linestyle="none",
            zorder=5,
        )
    else:
        ax.plot(
            x,
            BEYOND_Y,
            marker="^",
            markerfacecolor=face,
            markeredgecolor=color,
            linestyle="none",
            zorder=5,
        )


def _status_mark(ax: Axes, x: float, status: str, color: str) -> None:
    if status == INVALID:
        ax.plot(x, STRIP_Y, marker="x", color=color, markersize=5, markeredgewidth=1.2)
    elif status == PARTIAL:
        ax.plot(x, STRIP_Y, marker="d", markerfacecolor="white", markeredgecolor=color)
    else:
        ax.plot(x, STRIP_Y, marker=".", color="0.6", markersize=3)


def _draw_family(
    ax: Axes, release: Release, family: str, *, sustained: bool, width: float
) -> None:
    color = FAMILY_COLOR[family]
    for r, (status, curve) in _curves_by(release, family).items():
        if status != VALID or curve is None:
            _status_mark(ax, r, status, color)
            continue
        offset = -0.009 if sustained else 0.0
        _boundary_marks(ax, r + offset, curve.first, color, filled=True, width=width)
        if sustained:
            _boundary_marks(
                ax, r + 0.009, curve.sustained, color, filled=False, width=width * 0.6
            )


def _shp_overlay(ax: Axes, shp: ShpAnchor, *, main: bool) -> None:
    color = OKABE_ITO["blue"]
    lo, hi = shp.wald_95_interval
    ax.axvspan(lo, hi, color=color, alpha=0.16, linewidth=0, zorder=0.5)
    ax.axvspan(
        *shp.sensitivity_envelope,
        facecolor="none",
        edgecolor=color,
        hatch="////",
        alpha=0.35,
        linewidth=0,
        zorder=0.4,
    )
    ax.axvline(shp.estimate, color=color, linewidth=0.9, linestyle="--", zorder=0.6)
    starts = shp.starts
    if starts is not None and starts.estimate is not None:
        ax.axvline(
            starts.estimate,
            color=STARTS_COLOR,
            linewidth=0.9,
            linestyle=":",
            zorder=0.6,
        )
        if main and starts.wald_95_interval is not None:
            lo, hi = starts.wald_95_interval
            ax.errorbar(
                starts.estimate,
                STARTS_Y,
                xerr=[[starts.estimate - lo], [hi - starts.estimate]],
                fmt="D",
                color=STARTS_COLOR,
                markersize=3,
                capsize=1.5,
                linewidth=0.8,
                zorder=6,
            )


def _crosswalk_overlay(ax: Axes, shp: ShpAnchor, crosswalk: Crosswalk) -> None:
    """Grid r whose synthetic replicate range contains the SHP value; no r chosen."""
    contained = crosswalk.containing(shp.estimate)
    for offset, reference in zip(
        (-0.012, 0.0, 0.012), CROSSWALK_REFERENCES, strict=True
    ):
        for r in contained[reference]:
            ax.plot(
                r + offset,
                CROSSWALK_Y,
                marker=CROSSWALK_MARKERS[reference],
                color=CROSSWALK_COLOR,
                markersize=3,
                linestyle="none",
                zorder=5,
            )


def _shp_handles(shp: ShpAnchor, crosswalk: Crosswalk | None) -> list[Artist]:
    """F6 positions distinct quantities without empirical calibration to r."""
    blue = OKABE_ITO["blue"]
    handles: list[Artist] = [
        Line2D(
            [],
            [],
            color=blue,
            linestyle="--",
            label=f"SHP quasi-simplex anchor {shp.year}\n"
            "(distinct from r; uncalibrated)",
        ),
        Patch(color=blue, alpha=0.3, label="SHP quasi-simplex Wald 95% CI"),
        Patch(
            facecolor="none",
            edgecolor=blue,
            hatch="////",
            label="SHP Heise envelope (not a CI)",
        ),
    ]
    starts = shp.starts
    if starts is not None and starts.estimate is not None:
        handles.append(
            Line2D(
                [],
                [],
                color=STARTS_COLOR,
                linestyle=":",
                marker="D",
                markersize=3,
                label=f"SHP STARTS sensitivity {shp.year}\n"
                "(distinct from r), Wald 95% CI",
            )
        )
    elif starts is not None:
        reasons = "; ".join(STARTS_SHORT[r] for r in starts.failure_reasons)
        handles.append(
            Line2D(
                [],
                [],
                linestyle="none",
                label=f"SHP STARTS sensitivity {shp.year}: failed, not drawn\n"
                f"({reasons})",
            )
        )
    if crosswalk is not None:
        partial = not crosswalk.declared_plan or crosswalk.missing > 0
        for reference, marker in CROSSWALK_MARKERS.items():
            handles.append(
                Line2D(
                    [],
                    [],
                    marker=marker,
                    color=CROSSWALK_COLOR,
                    markersize=3,
                    linestyle="none",
                    label=f"synthetic crosswalk, exploratory: {reference}"
                    + ("\n(partial plan)" if partial else ""),
                )
            )
    return handles


def _r_limits(shp: ShpAnchor | None) -> tuple[float, float]:
    lo, hi = 0.47, 0.93
    if shp is not None:
        intervals = [shp.wald_95_interval, shp.sensitivity_envelope]
        if shp.starts is not None and shp.starts.wald_95_interval is not None:
            intervals.append(shp.starts.wald_95_interval)
        lo = min(lo, *(low - 0.02 for low, _ in intervals))
        hi = max(hi, *(high + 0.02 for _, high in intervals))
    return max(0.0, lo), min(1.0, hi)


def figure_a_star(
    release: Release,
    render: Render,
    shp: ShpAnchor | None = None,
    crosswalk: Crosswalk | None = None,
) -> list[Path]:
    """F1 (and F6 when ``shp`` is given): a*(r) with bands, by null family."""
    with style():
        # F6 carries a second legend column of SHP entries, hence the extra height.
        height = 150 * MM if shp is None else 175 * MM
        fig = plt.figure(figsize=(DOUBLE, height), layout="constrained")
        grid = fig.add_gridspec(2, 4)
        main = fig.add_subplot(grid[:, :2])
        others = [fig.add_subplot(grid[i // 2, 2 + i % 2]) for i in range(4)]
        xlim = _r_limits(shp)
        for ax, family in zip([main, *others], FAMILIES, strict=True):
            _r_axis(ax, labels=ax is main or ax in others[2:])
            _strength_axis(
                ax,
                labels=ax is main or ax in (others[0], others[2]),
                crosswalk=crosswalk is not None and ax is main,
            )
            ax.set_xlim(*xlim)
            if shp is not None:
                _shp_overlay(ax, shp, main=ax is main)
                if crosswalk is not None and ax is main:
                    _crosswalk_overlay(ax, shp, crosswalk)
            if family != "B":
                for r, (status, curve) in _curves_by(release, "B").items():
                    if (
                        status == VALID
                        and curve is not None
                        and curve.first.point is not None
                    ):
                        ax.plot(
                            r,
                            grid_index(curve.first.point),
                            marker="o",
                            color="0.8",
                            markersize=3,
                            linestyle="none",
                            zorder=1,
                        )
            _draw_family(
                ax,
                release,
                family,
                sustained=family == "B",
                width=1.4 if family == "B" else 0.9,
            )
            _panel_tag(
                ax,
                textwrap.fill(FAMILY_LABEL[family], width=25)
                + (" (confirmatory)" if family == "B" else ""),
            )
            if family == "B" and not release.main_curve_valid:
                _main_curve_mark(ax)
        main.text(
            1.01,
            SMALL_LARGE_Y + 0.15,
            "large",
            transform=main.get_yaxis_transform(),
            ha="left",
            va="bottom",
            color="0.45",
        )
        main.text(
            1.01,
            SMALL_LARGE_Y - 0.15,
            "small",
            transform=main.get_yaxis_transform(),
            ha="left",
            va="top",
            color="0.45",
        )
        main.set_ylabel("nominal strength a (partner drift; grid positions)")
        main.set_xlabel("response signal share r († calibration-exposed)")
        handles: list[Artist] = [
            Line2D(
                [],
                [],
                marker="o",
                color="black",
                linestyle="-",
                label="a* and interval (band inversion)",
            ),
            Line2D(
                [],
                [],
                marker="o",
                markerfacecolor="white",
                color="black",
                linestyle="-",
                linewidth=0.6,
                label="sustained a*ₛ (B)",
            ),
            Line2D(
                [],
                [],
                marker="^",
                color="black",
                linestyle="none",
                label="not reached (>0.9)",
            ),
            Line2D(
                [],
                [],
                marker="s",
                markerfacecolor="white",
                color="black",
                linestyle="none",
                label="censored at gap",
            ),
            Line2D(
                [],
                [],
                marker="x",
                color="black",
                linestyle="none",
                label=STATUS_LABEL[INVALID],
            ),
            Line2D(
                [],
                [],
                marker="d",
                markerfacecolor="white",
                color="black",
                linestyle="none",
                label=STATUS_LABEL[PARTIAL],
            ),
            Line2D(
                [],
                [],
                marker=".",
                color="0.6",
                linestyle="none",
                label=STATUS_LABEL[NOT_STARTED],
            ),
            Line2D(
                [],
                [],
                marker="o",
                color="0.8",
                linestyle="none",
                label="B a* (descriptive reference)\nno between-family inference",
            ),
        ]
        if shp is not None:
            handles += _shp_handles(shp, crosswalk)
        fig.legend(handles=handles, loc="outside lower center", ncol=2)
        return save(
            fig, render, "F6_a_star_shp_anchor" if shp else "F1_a_star_by_family"
        )


def figure_profiles(release: Release, render: Render, family: str) -> list[Path]:
    """F2: released AUC profile and band at every r, with 0.70 and the a* band."""
    with style():
        fig, axes = plt.subplots(
            3,
            3,
            figsize=(DOUBLE, 150 * MM),
            sharex=True,
            sharey=True,
            layout="constrained",
        )
        x = np.arange(len(GRID))
        color = FAMILY_COLOR[family]
        for ax, (r, (status, curve)) in zip(
            axes.flat, sorted(_curves_by(release, family).items()), strict=True
        ):
            ax.axhline(TARGET, color="0.3", linestyle="--", linewidth=0.7)
            ax.axhline(0.5, color="0.6", linestyle=":", linewidth=0.7)
            _panel_tag(
                ax,
                f"response signal share\nr = {r:.2f}"
                + ("†" if r == CALIBRATION_EXPOSED_R else ""),
            )
            if curve is None:
                for line in ax.lines:
                    line.set_visible(False)
                ax.text(
                    0.5,
                    0.5,
                    textwrap.fill(STATUS_LABEL[status], width=24),
                    transform=ax.transAxes,
                    ha="center",
                    va="center",
                )
                continue
            shown = color if status == VALID else "0.6"
            idx = [grid_index(a) for a in curve.available]
            point, lower, upper = map(np.array, (curve.auc, curve.lower, curve.upper))
            ax.errorbar(
                idx,
                (lower + upper) / 2,
                yerr=(upper - lower) / 2,
                fmt="none",
                color=shown,
                elinewidth=0.9,
                capsize=1.5,
            )
            ax.plot(idx, point, "o", color=shown, markersize=3, zorder=2.1)
            for i, ok in enumerate(curve.cell_success):
                if not ok:
                    ax.plot(
                        i, 0.47, marker="x", color=OKABE_ITO["vermillion"], markersize=4
                    )
            if status != VALID:
                tag = ax.texts[0]
                tag.set_text(
                    tag.get_text()
                    + f"\n{STATUS_LABEL[INVALID]}; a* suppressed\nnull gate failed"
                )
                continue
            first = curve.first
            edge = len(GRID) - 0.5
            lo, hi = first.interval or (None, None)
            cut = first.end_censored_at(1)
            if lo is not None:
                right = grid_index(hi) if hi is not None else edge
                if hi is None and cut is not None:
                    right = grid_index(cut)
                ax.axvspan(
                    grid_index(lo) - 0.2,
                    right + (0.2 if hi is not None or cut is not None else 0.3),
                    color=OKABE_ITO["sky"],
                    alpha=0.25,
                    linewidth=0,
                    zorder=0,
                )
            if first.point is not None:
                ax.axvline(
                    grid_index(first.point), color=OKABE_ITO["blue"], linewidth=1.0
                )
            note = ""
            if first.point is None:
                note = (
                    f"a* censored at gap a={first.censored_at:g}"
                    if first.censored_at is not None
                    else "a* not reached (>0.9)"
                )
            elif hi is None:
                note = (
                    f"upper end censored at gap a={cut:g}"
                    if cut is not None
                    else "upper end >0.9"
                )
            if note:
                tag = ax.texts[0]
                tag.set_text(tag.get_text() + "\n" + note)
        for ax in axes[-1]:
            ax.set_xticks(x)
            ax.set_xticklabels([f"{a:g}" for a in GRID], rotation=90)
        axes[0][0].set_ylim(0.44, 1.01)
        axes[0][0].set_xlim(-0.5, len(GRID) - 0.3)
        axes[-1][1].set_xlabel("nominal strength a (partner drift; grid positions)")
        axes[1][0].set_ylabel(
            f"Panel AUC, {FAMILY_LABEL[family]}\n(point, per-r 95% band)"
        )
        handles = [
            Line2D([], [], color="0.3", linestyle="--", label="target 0.70"),
            Line2D([], [], color="0.6", linestyle=":", label="null 0.5"),
            Line2D([], [], color=OKABE_ITO["blue"], label="a*"),
            Patch(
                color=OKABE_ITO["sky"], alpha=0.4, label="a* interval (band inversion)"
            ),
            Line2D(
                [],
                [],
                marker="x",
                color=OKABE_ITO["vermillion"],
                linestyle="none",
                label="gap cell",
            ),
        ]
        fig.legend(handles=handles, loc="outside lower center", ncol=5)
        if family == "B" and not release.main_curve_valid:
            fig.suptitle(
                textwrap.fill(MAIN_CURVE_NOTE, width=90),
                x=0.01,
                ha="left",
                color="black",
                fontsize=8,
                fontweight="bold",
            )
        return save(fig, render, f"F2_auc_profiles_{family}")


def figure_offsets(release: Release, render: Render) -> list[Path]:
    """F3, exploratory: grid-step offset of each family's a* from B's, per r."""
    with style():
        fig, ax = plt.subplots(figsize=(SINGLE, 62 * MM), layout="constrained")
        _r_axis(ax)
        ax.axhline(0, color="0.5", linewidth=0.6)
        b = _curves_by(release, "B")
        dodge = {"A": -0.012, "C": -0.004, "D": 0.004, "E": 0.012}
        markers = 0
        for family in FAMILIES[1:]:
            for r, (status, curve) in _curves_by(release, family).items():
                base = b[r][1]
                if (
                    status != VALID
                    or curve is None
                    or base is None
                    or b[r][0] != VALID
                    or curve.first.point is None
                    or base.first.point is None
                ):
                    continue
                offset = grid_index(curve.first.point) - grid_index(base.first.point)
                ax.plot(
                    r + dodge[family],
                    offset,
                    marker="o",
                    color=FAMILY_COLOR[family],
                    linestyle="none",
                )
                markers += 1
        if not markers:
            ax.clear()
            ax.set_axis_off()
            _unavailable(
                ax,
                "Family offsets unavailable:\nno paired valid point boundaries\n"
                "against B are available.",
            )
            return save(fig, render, "F3_exploratory_family_offsets_vs_B")
        ax.set_xlim(0.47, 0.93)
        ax.set_ylim(-len(GRID) + 0.5, len(GRID) - 0.5)
        ax.set_yticks(range(-len(GRID) + 1, len(GRID), 2))
        ax.set_ylabel("a* grid steps relative to B\n(descriptive; no contrast test)")
        ax.set_xlabel("response signal share r\n(† calibration-exposed)")
        ax.legend(
            handles=[
                Line2D(
                    [],
                    [],
                    marker="o",
                    color=FAMILY_COLOR[f],
                    linestyle="none",
                    label=FAMILY_LABEL[f],
                )
                for f in FAMILIES[1:]
            ],
            loc="upper left",
            ncol=1,
            handletextpad=0.1,
            columnspacing=0.6,
        )
        return save(fig, render, "F3_exploratory_family_offsets_vs_B")


def _unavailable(ax: Axes, text: str) -> None:
    ax.text(
        0.5, 0.5, text, transform=ax.transAxes, ha="center", va="center", color="0.4"
    )
    ax.set_xticks([])
    ax.set_yticks([])


def _complete(gate: GateRecords, stage: str) -> dict[str, Any] | None:
    """The stage summary once every planned task is aggregated, else None."""
    summary = gate.summaries.get(stage)
    if summary is None or summary["completed"] < summary["planned"]:
        return None
    return summary


def _stage_state(gate: GateRecords, stage: str) -> str:
    progress = gate.progress(stage)
    if progress is None:
        return f"{stage} not started"
    done, planned = progress
    if done < planned or stage not in gate.summaries:
        return f"{stage} {IN_PROGRESS}: {done}/{planned} tasks"
    summary = gate.summaries[stage]
    reason = failure_reason(stage, summary)
    if reason is not None:
        return "\n".join([f"{stage} failed:", *textwrap.wrap(reason, 32)])
    return f"{stage} aggregate not available"


_GAP_LABEL = {
    "screened": "{status}, screened",
    "family_limit": "{status}, profile",
    "solver": "{status}",
    "validation": "{status}, validation failed",
    "dependency": "dependency gap",
    "propagation": "propagation gap (amendment v4.4)",
}


def _fit_outcomes(ax: Axes, gate: GateRecords) -> None:
    """(a) G0 fits by final status, coloured by gap kind (family limits are gaps)."""
    counts: dict[tuple[str | None, str], int] = {}
    for fit in gate.g0_fits:
        key = (fit.gap, fit.status)
        counts[key] = counts.get(key, 0) + 1
    order = sorted(
        counts,
        key=lambda k: (-1 if k[0] is None else GAP_KINDS.index(k[0]), k[1]),
    )
    labels = [
        status if gap is None else _GAP_LABEL[gap].format(status=status)
        for gap, status in order
    ]
    ax.barh(
        range(len(order)),
        [counts[k] for k in order],
        color=[GAP_COLOR[gap] for gap, _ in order],
    )
    ax.set_yticks(range(len(order)), labels)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(left=0.5)  # a single fit still draws a visible bar
    ax.set_xlabel("G0 fits by final status")


def _stage_strip(ax: Axes, gate: GateRecords) -> None:
    """(g) Tasks completed and verdict per stage, with the summary source."""
    rows: list[tuple[str, float, str | None, str]] = []
    for stage in GATE_STAGES:
        if stage == "G2" and gate.stop is not None:
            binding = cast(dict[str, Any], gate.stop["g0_gap_binding"])
            rows.append(
                (
                    "pre-G2 stop",
                    0.0,
                    None,
                    "stopped before G2 by the economy rule "
                    f"(pass probability {binding['pass_probability']:.3f} "
                    f"< {binding['minimum']:.2f})",
                )
            )
        progress = gate.progress(stage)
        verdict = gate.verdict(stage)
        if progress is None:
            rows.append((stage, 0.0, None, "not started"))
            continue
        done, planned = progress
        text = f"{done}/{planned} tasks · {verdict}"
        if stage in gate.from_successor:
            text += f" · {SUCCESSOR_SOURCE}"
        elif stage not in gate.summaries:
            text += " · no aggregate line yet"
        rows.append((stage, done / planned, verdict, text))
    y = np.arange(len(rows))
    ax.barh(y, 1.0, color="none", edgecolor="0.6", linewidth=0.5, height=0.6)
    ax.barh(
        y,
        [share for _, share, _, _ in rows],
        color=[VERDICT_COLOR[verdict] for _, _, verdict, _ in rows],
        height=0.6,
    )
    for i, (_, _, _, text) in enumerate(rows):
        ax.text(1.03, i, textwrap.fill(text, width=54), va="center", ha="left")
    ax.set_xlim(0, 3.4)
    ax.set_xticks([0, 0.5, 1], ["0%", "50%", "100%"])
    ax.set_yticks(y, [stage for stage, _, _, _ in rows])
    ax.invert_yaxis()
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_bounds(0, 1)


def _ratio_interval(ax: Axes, point: float, lower: float, upper: float, y: int) -> None:
    color = OKABE_ITO["black"]
    ax.plot(point, y, "o", color=color, markersize=3)
    ax.hlines(y, lower, upper, color=color)
    ax.plot([lower, upper], [y, y], "|", color=color, markersize=3)


def figure_gate(
    gate: GateRecords, render: Render, thresholds: dict[str, float] | None
) -> list[Path]:
    """F4: calibration-gate diagnostics from the sealed aggregate records."""
    with style():
        fig = plt.figure(figsize=(DOUBLE, 175 * MM), layout="constrained")
        grid = fig.add_gridspec(4, 2, height_ratios=(1.3, 1, 1, 0.95))
        g0s, g0e = (fig.add_subplot(grid[0, i]) for i in range(2))
        g1b, g1bc = (fig.add_subplot(grid[1, i]) for i in range(2))
        g2, g2c = (fig.add_subplot(grid[2, i]) for i in range(2))
        stages = fig.add_subplot(grid[3, :])
        # (a) G0 final status of every fit
        _panel_tag(g0s, "(a) G0")
        if gate.g0_fits:
            _fit_outcomes(g0s, gate)
        else:
            _unavailable(g0s, "G0 task records not available")
        # (b) G0 evaluation counts against the frozen solver budget
        _panel_tag(g0e, "(b) G0")
        if gate.g0_evaluations:
            g0e.hist(
                gate.g0_evaluations,
                bins=list(range(0, SOLVER_BUDGET + 2, 2)),
                color=OKABE_ITO["sky"],
            )
            g0e.axvline(SOLVER_BUDGET, color=OKABE_ITO["vermillion"], linestyle="--")
            g0e.text(
                SOLVER_BUDGET - 1,
                1.0,
                f"budget {SOLVER_BUDGET}",
                rotation=90,
                ha="right",
                va="top",
                transform=g0e.get_xaxis_transform(),
                color="black",
            )
            g0e.set_xlabel("Evaluations per attempt")
            g0e.set_ylabel("Attempts")
        else:
            _unavailable(g0e, "G0 task records not available")
        # (c) G1b joint coverage against nominal
        _panel_tag(g1b, "(c) G1b")
        g1b_summary = _complete(gate, "G1b")
        if g1b_summary is not None and "coverage_counts" in g1b_summary:
            counts = cast(dict[str, int], g1b_summary["coverage_counts"])
            names = [k for k in SCENARIOS if k in counts]
            g1b.plot(
                [counts[k] / 1000 for k in names],
                range(len(names)),
                "o",
                color=OKABE_ITO["black"],
            )
            g1b.axvline(0.95, color="0.4", linestyle=":", label="nominal 0.95")
            g1b.axvline(
                0.935,
                color=OKABE_ITO["vermillion"],
                linestyle="--",
                label="pass ≥ 0.935",
            )
            g1b.set_yticks(range(len(names)), names)
            g1b.invert_yaxis()
            g1b.set_xlim(0.90, 1.0)
            g1b.set_xlabel("Joint coverage per scenario")
            g1b.text(
                0.95,
                1.0,
                "nominal",
                rotation=90,
                ha="right",
                va="top",
                transform=g1b.get_xaxis_transform(),
                color="0.4",
            )
            g1b.text(
                0.935,
                1.0,
                "pass",
                rotation=90,
                ha="right",
                va="top",
                transform=g1b.get_xaxis_transform(),
                color="black",
            )
        else:
            _unavailable(g1b, _stage_state(gate, "G1b"))
        # (d) G1b critical values against the 2.7729 floor
        _panel_tag(g1bc, "(d) G1b")
        if gate.g1b_critical:
            values = np.array(gate.g1b_critical)
            g1bc.hist(values, bins=40, color=OKABE_ITO["sky"])
            g1bc.axvline(CRITICAL_FLOOR, color=OKABE_ITO["vermillion"], linestyle="--")
            g1bc.set_xlabel("Critical value per repetition")
            g1bc.set_ylabel("Repetitions")
            share = float(np.mean(values > CRITICAL_FLOOR))
            g1bc.text(
                0.97,
                0.9,
                f"above floor: {share:.1%}",
                transform=g1bc.transAxes,
                ha="right",
            )
        else:
            _unavailable(g1bc, "G1b task records not available")
        # (e) G2 dispersion ratios with bootstrap intervals
        _panel_tag(g2, "(e) G2")
        g2_summary = _complete(gate, "G2")
        if g2_summary is not None and g2_summary.get("cell_ratios"):
            g = g2_summary
            ratios = [*g["cell_ratios"], g["pooled_ratio"]]
            lows = [*g["cell_lower"], g["pooled_lower"]]
            highs = [*g["cell_upper"], g["pooled_upper"]]
            y = np.arange(len(ratios))
            for index, (point, lower, upper) in enumerate(
                zip(ratios, lows, highs, strict=True)
            ):
                _ratio_interval(g2, point, lower, upper, index)
            g2.axvline(1.0, color="0.4", linestyle=":")
            if thresholds:
                g2.axvspan(
                    thresholds["cell_lower"],
                    thresholds["cell_upper"],
                    color=OKABE_ITO["green"],
                    alpha=0.12,
                    linewidth=0,
                )
                g2.plot(
                    [thresholds["pooled_lower"], thresholds["pooled_upper"]],
                    [y[-1] + 0.45] * 2,
                    color=OKABE_ITO["green"],
                    linewidth=2,
                )
            g2.set_yticks(
                y,
                [cell_label(gate, i, short=True) for i in range(len(y) - 1)]
                + ["pooled"],
            )
            g2.invert_yaxis()
            g2.set_xlabel("Dispersion ratio")
        elif g2_summary is not None and "cell_ratios" in g2_summary:
            pairs = " ".join(map(str, g2_summary.get("successful_pair_counts", [])))
            _unavailable(
                g2,
                "G2 dispersion ratios not estimable\n"
                f"(< 2 intact pairs in a cell)\nsuccessful pairs by cell:\n{pairs}",
            )
        else:
            _unavailable(g2, _stage_state(gate, "G2"))
        # (f) G2c local propagation vs full refits
        _panel_tag(g2c, "(f) G2c")
        g2c_summary = _complete(gate, "G2c")
        comparisons = cast(
            list[dict[str, Any]], (g2c_summary or {}).get("comparisons", [])
        )
        if comparisons:
            y = np.arange(len(comparisons))
            for index, comparison in enumerate(comparisons):
                if "ratio" in comparison:
                    _ratio_interval(
                        g2c,
                        comparison["ratio"],
                        comparison["lower"],
                        comparison["upper"],
                        index,
                    )
                else:
                    g2c.text(
                        0.03,
                        index,
                        "not estimable\n(fewer than 2 finite refits)",
                        transform=g2c.get_yaxis_transform(),
                        va="center",
                    )
            g2c.axvline(0.8, color=OKABE_ITO["vermillion"], linestyle="--")
            g2c.axvline(2.0, color=OKABE_ITO["vermillion"], linestyle="--")
            g2c.axvline(1.0, color="0.4", linestyle=":")
            g2c.set_xscale("log")
            g2c.set_xticks(
                [0.25, 0.5, 0.8, 1, 2, 4], ["0.25", "0.5", "0.8", "1", "2", "4"]
            )
            g2c.minorticks_off()
            g2c.set_yticks(y, ["a=0.10 (100)", "a=0.03 (40)"][: len(y)])
            g2c.set_ylim(-0.5, len(y) - 0.5)
            g2c.invert_yaxis()
            g2c.set_xlabel("Var_D5 / Var_refit")
        else:
            _unavailable(g2c, _stage_state(gate, "G2c"))
        # (g) stage verdicts, tasks completed and summary source
        _panel_tag(stages, "(g) Stages")
        _stage_strip(stages, gate)
        return save(fig, render, "F4_gate_diagnostics")


def _configuration_label(config: tuple[int, str, str, str]) -> str:
    tier, family, channel, sensitivity = config
    parts = [f"T{tier} {family}"]
    if channel != "observed":
        parts.append(channel)
    if sensitivity != "main":
        parts.append(sensitivity)
    return " · ".join(parts)


def figure_inventory(release: Release, render: Render) -> list[Path]:
    """F5: D9 status of every inventory unit, per configuration and r."""
    catalog = unit_catalog()
    configs: list[tuple[int, str, str, str]] = []
    for meta in catalog.values():
        if meta.configuration not in configs:
            configs.append(meta.configuration)
    matrix = np.zeros((len(configs), len(RELIABILITIES)), dtype=int)
    for key, meta in catalog.items():
        matrix[configs.index(meta.configuration), RELIABILITIES.index(meta.r)] = (
            STATUSES.index(release.statuses[key])
        )
    with style():
        height = (len(configs) * 3.1 + 28) * MM
        fig, ax = plt.subplots(figsize=(DOUBLE, height), layout="constrained")
        from matplotlib.colors import BoundaryNorm, ListedColormap

        cmap = ListedColormap([STATUS_COLOR[s] for s in STATUSES])
        ax.pcolormesh(
            np.arange(len(RELIABILITIES) + 1) - 0.5,
            np.arange(len(configs) + 1) - 0.5,
            matrix,
            cmap=cmap,
            norm=BoundaryNorm(np.arange(5) - 0.5, 4),
            edgecolors="white",
            linewidth=0.4,
            rasterized=False,
        )
        for row in range(len(configs)):
            for column in range(len(RELIABILITIES)):
                ax.text(
                    column,
                    row,
                    ("N", "P", "I", "V")[matrix[row, column]],
                    ha="center",
                    va="center",
                    color="black",
                )
        ax.set_xticks(
            range(len(RELIABILITIES)),
            [
                f"{r:.2f}" + ("†" if r == CALIBRATION_EXPOSED_R else "")
                for r in RELIABILITIES
            ],
            rotation=90,
        )
        ax.set_yticks(range(len(configs)), [_configuration_label(c) for c in configs])
        ax.invert_yaxis()
        ax.set_xlabel("response signal share r († calibration-exposed)")
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.legend(
            handles=[
                Patch(
                    facecolor=STATUS_COLOR[s],
                    edgecolor="0.6",
                    linewidth=0.4,
                    label=f"{('N', 'P', 'I', 'V')[i]}: {STATUS_LABEL[s]} "
                    f"({int((matrix == i).sum())})",
                )
                for i, s in enumerate(STATUSES)
            ],
            loc="outside lower center",
            ncol=1,
        )
        return save(fig, render, "F5_inventory_status")


def render_figures(
    release: Release,
    gate: GateRecords | None,
    render: Render,
    *,
    shp: ShpAnchor | None = None,
    thresholds: dict[str, float] | None = None,
    crosswalk: Crosswalk | None = None,
) -> list[Path]:
    paths = figure_a_star(release, render)
    for family in FAMILIES:
        paths += figure_profiles(release, render, family)
    paths += figure_offsets(release, render)
    if gate is not None:
        paths += figure_gate(gate, render, thresholds)
    paths += figure_inventory(release, render)
    if shp is not None:
        paths += figure_a_star(release, render, shp, crosswalk)
    return paths


def figure_names() -> Sequence[str]:
    return (
        "F1_a_star_by_family",
        *(f"F2_auc_profiles_{f}" for f in FAMILIES),
        "F3_exploratory_family_offsets_vs_B",
        "F4_gate_diagnostics",
        "F5_inventory_status",
        "F6_a_star_shp_anchor",
    )
