"""Export released X3/X4/X6/X7 aggregates and comparisons into JCSS tables.

Only explicit JSON inputs are read. No stores, fitting or aggregation are used.
The catalog retains machine labels alongside restricted manuscript wording.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import textwrap
from collections import Counter
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from ic_study.analysis.v4_exploratory_comparisons import (
    OUTSIDE_DOMAIN,
    UNAVAILABLE,
    compare_exploratory,
)
from ic_study.analysis.v4_report_export import RESULT, fill, used_ids
from ic_study.simulation.detection_v4 import GRID, RELIABILITIES

STUDY = Path(__file__).resolve().parents[3]
DECLARATION = (
    STUDY
    / "experiments/exploratory/detection-boundary-v4-exploratory/declaration-x3-x7.json"
)
SCHEMA = "ic-study.v4-exploratory-result-values.v1"
NAMES = ("x3", "x4", "x6", "x7", "comparisons")
PROSE_COUNTS = (
    "x3.sizes.matching",
    "x3.sizes.retry_matching",
    "x4.sizes.check",
    "x6.x6a.recorded",
    "x6.x6a.units",
    "x6.sizes.population_pairs",
)
X3_READINGS = (
    "supports-objection",
    "against-objection",
    "inconclusive",
    "error",
    "gap",
    "free-gap",
)
X7_READINGS = (
    "far",
    "close",
    "inconclusive",
    "invalid",
    "censored",
    "unavailable",
    "incomplete",
)
X6_READINGS = (
    "adequate",
    "subnominal",
    "failure",
    "no reading",
    "inconclusive-truth-precision",
)
SKIP = {
    "schema",
    "label",
    "declaration",
    "release",
    "sources",
    "code",
    "host",
    "seeds",
    "timing",
    "verification_sha256",
    "successor",
    "compatibility",
    "panels",
    "provenance",
}


def escaped(value: str) -> str:
    symbols = {
        "\\": r"\textbackslash ",
        "{": r"\textbraceleft ",
        "}": r"\textbraceright ",
        "_": r"\_",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
        "$": r"\$",
        "^": r"\textasciicircum ",
        "~": r"\textasciitilde ",
        "<": r"\textless ",
        ">": r"\textgreater ",
    }
    return "".join(symbols.get(c, c) for c in value).replace("\n", " ")


def formatted(value: Any) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Nonfinite aggregate value")
        return f"{value:.6g}"
    return escaped(str(value))


def row_key(row: Any, index: int) -> str:
    if isinstance(row, dict):
        cell = row.get("cell", row)
        if isinstance(cell, dict) and "r" in cell:
            key = f"r{round(cell['r'] * 100):03d}"
            key += f".a{round(cell['a'] * 10000):04d}" if "a" in cell else ""
            channel = row.get("channel")
            if isinstance(channel, dict) and "name" in channel:
                key += "." + re.sub(r"[^A-Za-z0-9_-]", "-", channel["name"])
            return key
    return f"i{index:03d}"


@dataclass(frozen=True)
class Export:
    catalog: dict[str, str]
    sources: dict[str, dict[str, str]]
    written: tuple[Path, ...]
    synthetic: bool
    provenance: dict[str, Any]


def _flatten(
    value: Any,
    key: str,
    pointer: str,
    name: str,
    catalog: dict[str, str],
    sources: dict[str, dict[str, str]],
) -> None:
    if isinstance(value, dict):
        for field, item in value.items():
            if field in SKIP:
                continue
            segment = re.sub(r"[^A-Za-z0-9_-]", "-", str(field))
            _flatten(
                item, f"{key}.{segment}", f"{pointer}/{field}", name, catalog, sources
            )
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _flatten(
                item,
                f"{key}.{row_key(item, index)}",
                f"{pointer}/{index}",
                name,
                catalog,
                sources,
            )
    else:
        if key in catalog:
            raise ValueError(f"Duplicate result ID {key}")
        catalog[key] = formatted(value)
        sources[key] = {"input": name, "pointer": pointer}


def _macro(catalog: MutableMapping[str, str], key: str) -> str:
    if key not in catalog:
        key = "v4x.unavailable." + key.removeprefix("v4x.")
        catalog.setdefault(key, "unavailable")
    return rf"\resultnum{{{key}}}{{{catalog[key]}}}"


def _interval(catalog: MutableMapping[str, str], key: str) -> str:
    if f"{key}.i000" not in catalog:
        return _macro(catalog, key)
    return (
        "["
        + _macro(catalog, f"{key}.i000")
        + ", "
        + _macro(catalog, f"{key}.i001")
        + "]"
    )


def _comparison_boundary(
    catalog: dict[str, str], key: str, view: Mapping[str, Any], kind: str
) -> str:
    if kind not in view:
        return _macro(catalog, key + ".state") + "; " + _macro(catalog, key + ".reason")
    prefix = key + "." + kind
    parts = [
        _macro(catalog, prefix + ".point")
        + " "
        + _interval(catalog, prefix + ".interval"),
        _macro(catalog, prefix + ".state"),
        _macro(catalog, key + ".unit_status"),
        "C: " + _macro(catalog, prefix + ".censoring"),
        "IC: " + _macro(catalog, prefix + ".interval_censoring"),
    ]
    if view[kind]["reason"] is not None:
        parts.append(_macro(catalog, prefix + ".reason"))
    return "; ".join(parts)


def _table(
    name: str,
    caption: str,
    columns: Sequence[str],
    rows: Sequence[Sequence[str]],
    synthetic: bool,
) -> str:
    lines = ["% Generated by v4_exploratory_export; regenerate instead of editing."]
    marker = "SYNTHETIC REHEARSAL, NOT A RESULT. " if synthetic else ""
    if synthetic:
        lines.append("% SYNTHETIC REHEARSAL, NOT A RESULT.")
    if not rows:
        lines.extend(
            [
                r"\begin{table*}[htbp]",
                rf"\caption{{{marker}{caption}}}\label{{tab:v4x-{name}}}",
                r"\noindent No rows are available.",
                r"\end{table*}",
            ]
        )
        return "\n".join(lines) + "\n"
    displayed = [
        [RESULT.sub(lambda match: match[2], cell) for cell in row] for row in rows
    ]
    weights = []
    for index, column in enumerate(columns):
        lengths = sorted(len(row[index]) for row in displayed)
        longest_word = max(len(word) for word in column.replace("-", " ").split())
        weights.append(max(7, longest_word, min(40, lengths[len(lengths) * 3 // 4])))
    widths = [0.92 * weight / sum(weights) for weight in weights]
    chunks: list[list[Sequence[str]]] = [[]]
    height = 0
    for row, text in zip(rows, displayed, strict=True):
        row_height = max(
            len(textwrap.wrap(cell, max(1, int(width * 110)))) or 1
            for cell, width in zip(text, widths, strict=True)
        )
        if chunks[-1] and height + row_height > 36:
            chunks.append([])
            height = 0
        chunks[-1].append(row)
        height += row_height
    layout = "".join(rf"p{{{width:.3f}\textwidth}}" for width in widths)
    for index, chunk in enumerate(chunks):
        label = f"tab:v4x-{name}" + (f"-part{index}" if index else "")
        continuation = (
            f" (continued, part {index + 1} of {len(chunks)})" if index else ""
        )
        lines += [
            r"\begin{table*}[htbp]",
            r"\setlength{\tabcolsep}{2pt}",
            *(
                [
                    r"\addtocounter{table}{-\csname @ne\endcsname}",
                    r"\providecommand{\theHtable}{\thetable}",
                    rf"\renewcommand{{\theHtable}}{{v4x-{name}-part{index}}}",
                ]
                if index
                else []
            ),
            rf"\caption{{{marker}{caption}{continuation}}}\label{{{label}}}",
            r"\centering\small",
            r"\begin{tabular}{@{}" + layout + "@{}}",
            r"\hline",
            " & ".join(
                r"\raggedright "
                + "".join(
                    word if word in {" ", "-"} else rf"\mbox{{{word}}}"
                    for word in re.split(r"([ -])", column)
                    if word
                )
                for column in columns
            )
            + r" \tabularnewline",
            r"\hline",
        ]
        lines += [
            " & ".join(rf"\raggedright {cell}" for cell in row) + r" \tabularnewline"
            for row in chunk
        ]
        lines += [r"\hline", r"\end{tabular}", r"\end{table*}"]
    return "\n".join(lines) + "\n"


def _inventory(
    rows: Sequence[Mapping[str, Any]],
    incomplete: list[int],
    expected: Sequence[tuple[float, float]],
    name: str,
) -> None:
    indices = [row["cell"]["index"] for row in rows]
    if len(set(indices)) != len(indices) or len(set(incomplete)) != len(incomplete):
        raise ValueError(f"Duplicate {name} cell identity")
    if set(indices) & set(incomplete) or set(indices) | set(incomplete) != set(
        range(len(expected))
    ):
        raise ValueError(f"{name} denominator does not account for the declared cells")
    for row in rows:
        cell = row["cell"]
        if (cell["a"], cell["r"]) != expected[cell["index"]]:
            raise ValueError(f"{name} cell identity differs from declaration")


def _declared_number(text: str, pattern: str = r"0\.\d+") -> float:
    match = re.search(pattern, text)
    if match is None:
        raise ValueError("Declaration lacks the required numerical field")
    return float(match[1] if match.lastindex else match[0])


def _comparison_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _comparison_fields(item)
            for key, item in value.items()
            if key != "reason"
            or value.get("state") not in {UNAVAILABLE, OUTSIDE_DOMAIN, "parcial"}
        }
    if isinstance(value, list):
        return [_comparison_fields(item) for item in value]
    return value


def _boundary_consistency(value: Any, locator: str, *, valid: bool = True) -> None:
    """A valid uncensored boundary lies in its inverted interval.

    The frozen inversion leaves the upper end empty, without interval censoring,
    when the lower band's first or sustained crossing is not reached on the
    gap-free grid; that end is open, beyond the grid.
    """
    if isinstance(value, dict):
        valid = (
            valid
            and value.get("unit_status", value.get("status", "completo válido"))
            == "completo válido"
            and value.get("valid_null_gate", True) is True
        )
        for kind in ("first", "sustained"):
            record = value.get(kind)
            if isinstance(record, dict):
                point = record.get("point")
                interval = record.get("interval")
                censoring = record.get("censoring")
                interval_censoring = record.get("interval_censoring")
            else:
                point = record
                interval = value.get(kind + "_interval")
                censoring = value.get(kind + "_censoring")
                interval_censoring = value.get(kind + "_interval_censoring")
            if (
                valid
                and isinstance(point, (int, float))
                and math.isfinite(point)
                and censoring is None
                and interval_censoring is None
                and not (
                    isinstance(interval, list)
                    and len(interval) == 2
                    and isinstance(interval[0], (int, float))
                    and math.isfinite(interval[0])
                    and interval[0] <= point
                    and (
                        interval[1] is None
                        or (
                            isinstance(interval[1], (int, float))
                            and math.isfinite(interval[1])
                            and point <= interval[1]
                        )
                    )
                )
            ):
                raise ValueError(
                    f"X6R-03: {locator}/{kind}: valid uncensored point {point} "
                    "requires an interval containing it with a finite lower end; "
                    f"recorded {interval}"
                )
        for key, item in value.items():
            _boundary_consistency(item, f"{locator}/{key}", valid=valid)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _boundary_consistency(item, f"{locator}/{index}", valid=valid)


def _coverage_consistency(section: Mapping[str, Any], locator: str) -> None:
    band = section["band"]
    complete = band["band_complete"]
    for truth in ("vs_d1", "vs_pop"):
        if band[truth] is None:
            continue
        primary, misses = band[truth]["primary"], band[truth]["gaps_as_misses"]
        if (
            primary["total"] != complete
            or primary["complete"] != complete
            or misses["complete"] != complete
            or misses["total"] != band["with_curve"]
            or misses["covered"] != primary["covered"]
        ):
            raise ValueError(
                f"X6R-02: {locator}/band/{truth}: gaps-as-misses must preserve "
                "the joint covered numerator and complete set"
            )
        if complete == 0:
            continue
        if any(row[truth] is None for row in section["strengths"]):
            raise ValueError(f"X6R-02: {locator}/{truth}: joint truth lacks a marginal")
        marginals = [row[truth]["band_interval"] for row in section["strengths"]]
        if any(row["complete"] < complete for row in marginals):
            raise ValueError(
                f"X6R-02: {locator}/{truth}: joint set exceeds a marginal set"
            )
        lower = max(
            0,
            sum(
                max(0, row["covered"] - (row["complete"] - complete))
                for row in marginals
            )
            - (len(marginals) - 1) * complete,
        )
        upper = min([complete, *(row["covered"] for row in marginals)])
        if not lower <= primary["covered"] <= upper:
            raise ValueError(
                f"X6R-02: {locator}/band/{truth}/primary: joint covered "
                f"{primary['covered']} violates intersection bounds [{lower}, {upper}]"
            )


def _validate(data: Mapping[str, Any], declaration: Mapping[str, Any]) -> None:
    grid = [(a, r) for r in RELIABILITIES for a in GRID]
    positive = [(a, r) for a, r in grid if a > 0]
    subset_text = declaration["x4_single_panel_power"]["x4b"]["cells"]
    match = re.search(r"\{([^}]+)\}", subset_text)
    if match is None:
        raise ValueError("X4b declaration lacks its subset")
    subset = [float(v) for v in re.findall(r"\d+\.\d+", match[1])]
    _inventory(data["x3"]["cells"], data["x3"]["incomplete"], positive, "X3")
    if data["x3"]["cells_declared"] != len(positive):
        raise ValueError("X3 declared denominator differs")
    for name, expected in (
        ("x4a", grid),
        ("x4b", [(a, r) for a, r in grid if r in subset]),
    ):
        _inventory(
            data["x4"][name], data["x4"]["incomplete"][name], expected, name.upper()
        )
    _inventory(data["x7"]["cells"], data["x7"]["incomplete"], grid, "X7")
    if sorted(row["r"] for row in data["x7"]["units"]) != list(RELIABILITIES):
        raise ValueError("X7 unit denominator differs from declaration")
    for index, row in enumerate(data["x7"]["units"]):
        incomplete = any(
            k in data["x7"]["incomplete"]
            for k in range(index * len(GRID), (index + 1) * len(GRID))
        )
        if incomplete != (row.get("status") == "incomplete"):
            raise ValueError("X7 incomplete cells require an incomplete unit")
        if not incomplete and row.get("reading") not in X7_READINGS:
            raise ValueError("Unknown X7 reading")
    declared_minimum = int(
        _declared_number(
            declaration["x6_interior_coverage"]["reading"]["minimum"], r"\d+"
        )
    )
    if data["x6"]["minimum_complete_repetitions"] != declared_minimum:
        raise ValueError("X6 minimum differs from declaration")
    sizes = data["x6"]["sizes"]
    for name, count, repetitions in (
        ("x6a", len(GRID) - 1, sizes["repetitions"]),
        (
            "x6b",
            len(declaration["x6_interior_coverage"]["x6b"]["cells"]),
            len(declaration["x6_interior_coverage"]["x6b"]["cells"])
            * sizes["repetitions"],
        ),
    ):
        section = data["x6"][name]
        expected_units = count * (sizes["truth_pipelines"] + 1) + repetitions
        incomplete_units = section["incomplete_units"]
        if (
            section["units"] != expected_units
            or section["recorded"] + len(incomplete_units) != expected_units
            or len(set(incomplete_units)) != len(incomplete_units)
            or any(
                type(i) is not int or not 0 <= i < expected_units
                for i in incomplete_units
            )
        ):
            raise ValueError(f"{name} denominator does not account for declared units")
        if name == "x6a":
            band = section["band"]
            if (
                not 0
                <= band["band_complete"]
                <= band["with_curve"]
                <= section["repetitions"]["recorded"]
                <= repetitions
            ):
                raise ValueError("X6a band denominator is inconsistent")
            if sorted(row["a"] for row in section["strengths"]) != list(GRID):
                raise ValueError("X6a requires the whole grid denominator")

    def readings(value: Any) -> None:
        if isinstance(value, dict):
            if "pointwise_gaps_as_misses" in value and "pointwise" in value:
                primary, misses = value["pointwise"], value["pointwise_gaps_as_misses"]
                if (
                    primary["covered"] != misses["covered"]
                    or primary["complete"] != misses["complete"]
                    or primary["total"] > misses["total"]
                ):
                    raise ValueError(
                        "X6R-02: pointwise gaps-as-misses must preserve the covered "
                        "numerator and complete set"
                    )
            if "covered" in value and "wilson95" in value:
                if not 0 <= value["covered"] <= value["complete"] <= value["total"]:
                    raise ValueError("X6 invalid coverage denominator")
                if value["reading"] not in X6_READINGS:
                    raise ValueError("Unknown X6 reading")
                if (
                    value["complete"] < declared_minimum
                    and value["reading"] != "no reading"
                ):
                    raise ValueError(
                        "X6 reading requires the declared minimum complete denominator"
                    )
            for item in value.values():
                readings(item)
        elif isinstance(value, list):
            for item in value:
                readings(item)

    readings(data["x6"])
    _coverage_consistency(data["x6"]["x6a"], "x6/x6a")
    for name in ("x7", "comparisons"):
        _boundary_consistency(data[name], name)

    comparisons = data["comparisons"]["by_r"]
    for key, row in comparisons.items():
        if row["r"] not in RELIABILITIES or key != str(row["r"]):
            raise ValueError("Comparison projection differs from the declared r domain")
    expected = compare_exploratory(
        {row["r"]: row["main_curve"] for row in comparisons.values()},
        x3=data["x3"],
        x4=data["x4"],
    )["by_r"]
    for key, row in comparisons.items():
        for name in ("x3", "x4"):
            if _comparison_fields(row[name]) != _comparison_fields(expected[key][name]):
                raise ValueError(
                    f"{name.upper()} comparison projection differs from the selected "
                    f"aggregate at r={row['r']}, "
                    f"a={row['main_curve']['first']['point']}"
                )


def export(inputs: Mapping[str, Path], manuscript: Path) -> Export:
    """Read explicit aggregates, preserve their fields and write fixed table names."""
    if set(inputs) != set(NAMES):
        raise ValueError("Provide x3, x4, x6, x7 and comparisons JSON")
    data: dict[str, Any] = {}
    provenance: dict[str, Any] = {}
    for name in NAMES:
        raw = inputs[name].read_bytes()
        value = json.loads(raw)
        expected = f"ic-study.v4-exploratory-{name}.v1"
        if not isinstance(value, dict) or value.get("schema") != expected:
            raise ValueError(f"Unexpected {name} aggregate schema")
        data[name] = value
        provenance[name] = {
            "name": inputs[name].name,
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    synthetic = any(value.get("synthetic") is True for value in data.values())
    declaration_raw = DECLARATION.read_bytes()
    declaration = json.loads(declaration_raw)
    _validate(data, declaration)
    comparison_inputs = data["comparisons"].get("provenance", {}).get("inputs", {})
    for name in ("x3", "x4"):
        binding = comparison_inputs.get(name)
        if binding is None and not synthetic:
            raise ValueError(f"Comparison provenance requires the {name} input binding")
        if binding is not None and (
            not isinstance(binding, dict)
            or binding.get("sha256") != provenance[name]["sha256"]
        ):
            raise ValueError(
                f"Comparison provenance differs from {name} aggregate bytes"
            )
    provenance["declaration"] = {
        "name": DECLARATION.name,
        "sha256": hashlib.sha256(declaration_raw).hexdigest(),
    }
    catalog: dict[str, str] = {}
    sources: dict[str, dict[str, str]] = {}
    for name, value in data.items():
        _flatten(value, f"v4x.{name}", "", name, catalog, sources)

    def add(key: str, value: Any, source: str) -> None:
        ident = f"v4x.{key}"
        if ident in catalog:
            raise ValueError(f"Duplicate result ID {ident}")
        catalog[ident] = formatted(value)
        name = key.split(".")[0]
        sources[ident] = {
            "input": "x4"
            if name in {"x4a", "x4b"}
            else "declaration"
            if name == "protocol"
            else name,
            "derivation": source,
        }

    statuses = []
    for name, rows, incomplete in (
        ("x3", data["x3"]["cells"], data["x3"]["incomplete"]),
        ("x4a", data["x4"]["x4a"], data["x4"]["incomplete"]["x4a"]),
        ("x4b", data["x4"]["x4b"], data["x4"]["incomplete"]["x4b"]),
        ("x7", data["x7"]["cells"], data["x7"]["incomplete"]),
    ):
        prefix = name if name != "x7" else "x7.inventory"
        for field, value in (
            ("recorded", len(rows)),
            ("incomplete", len(incomplete)),
            ("errors", sum(bool(row.get("error")) for row in rows)),
            (
                "gaps",
                sum(
                    row.get("success") is False and not row.get("error") for row in rows
                ),
            ),
            (
                "successful",
                sum(
                    row.get("success") is True and not row.get("error") for row in rows
                ),
            ),
        ):
            add(
                f"{prefix}.{field}",
                value,
                f"count of {field} records; errors and gaps are distinct",
            )
        statuses.append(
            [name]
            + [
                _macro(catalog, f"v4x.{prefix}.{k}")
                for k in ("recorded", "incomplete", "errors", "gaps")
            ]
        )
    for name, readings, rows in (
        ("x3", X3_READINGS, data["x3"]["cells"]),
        ("x7", X7_READINGS, data["x7"]["units"]),
    ):
        counts = Counter(row.get("reading") or row.get("status") for row in rows)
        for reading in readings:
            add(
                f"{name}.count.{reading}",
                counts[reading],
                f"count /{'cells' if name == 'x3' else 'units'} "
                f"with reading/status={reading}",
            )
    for name in ("x6a", "x6b"):
        section = data["x6"][name]
        add(
            f"x6.{name}.incomplete",
            len(section["incomplete_units"]),
            "length /incomplete_units",
        )
        if name == "x6a":
            add(
                "x6.x6a.without_curve",
                section["repetitions"]["recorded"] - section["band"]["with_curve"],
                "/x6a/repetitions/recorded minus /x6a/band/with_curve",
            )
    add("protocol.grid_strengths", len(GRID), "length of frozen GRID")
    add("protocol.zero", GRID[0], "first frozen GRID entry")
    add(
        "protocol.target",
        _declared_number(
            declaration["x3_free_signal_share_null"]["reading"]["lost_crossing"],
            r">= (\d+\.\d+)",
        ),
        "declaration /x3_free_signal_share_null/reading/lost_crossing",
    )
    for name, field in (
        ("nominal", "adequate"),
        ("failure", "failure_of_interior_inference"),
        ("conservative", "conservative"),
    ):
        add(
            f"protocol.x6.{name}",
            _declared_number(declaration["x6_interior_coverage"]["reading"][field]),
            f"declaration /x6_interior_coverage/reading/{field}",
        )
    add(
        "protocol.x4.level",
        _declared_number(declaration["x4_single_panel_power"]["x4b"]["rule"]),
        "declaration /x4_single_panel_power/x4b/rule",
    )
    add(
        "x3.count.lost_crossing",
        sum(row.get("lost_crossing") is True for row in data["x3"]["cells"]),
        "count /cells/lost_crossing=true",
    )
    for name in ("x4a", "x4b"):
        for flag in ("calibrated", "liberal", "conservative"):
            add(
                f"{name}.count.{flag}",
                sum(
                    value == flag
                    for value in data["x4"]["summary"]["size_at_a0"][name].values()
                ),
                f"count /summary/size_at_a0/{name}={flag}",
            )
        field = "normal_theory_reading" if name == "x4a" else "single_panel_reading"
        records = data["x4"][name]
        if name == "x4a":
            lower, upper = data["x4"]["summary"]["normal_theory_in_auc_range"]["range"]
            records = [
                row
                for row in records
                if row.get("x4a") is not None
                and lower <= row["x4a"]["auc_ref"] <= upper
            ]
        for reading in (
            ("describes", "overstates", "understates")
            if name == "x4a"
            else ("removes-power", "no-material-change", "inconclusive")
        ):
            add(
                f"{name}.count.{reading}",
                sum(row.get(field) == reading for row in records),
                f"count /{name}/{field}={reading}; "
                + (
                    "within /summary/normal_theory_in_auc_range/range"
                    if name == "x4a"
                    else (
                        "recorded non-null readings with their original "
                        "size conditioning"
                    )
                ),
            )
    for name in ("x6a", "x6b"):
        section = data["x6"][name]
        references: list[Any] = []
        if "band" in section:
            references.extend((section["band"].get("vs_d1") or {}).values())
        for row in section.get("strengths", section.get("cells", [])):
            references.extend((row.get("vs_d1") or {}).values())
        for reading in X6_READINGS:
            add(
                f"x6.{name}.count.{reading.replace(' ', '-')}",
                sum(
                    isinstance(value, dict) and value.get("reading") == reading
                    for value in references
                ),
                f"count D1 coverage references in {name}; "
                "primary and gaps-as-misses separately tabulated",
            )
        add(
            f"x6.{name}.count.conservative",
            sum(
                isinstance(value, dict) and value.get("conservative") is True
                for value in references
            ),
            f"count D1 coverage references with conservative=true in {name}",
        )
    comparison_rows = list(data["comparisons"]["by_r"].values())
    for component in ("main_curve", "x1b", "x3", "x4"):
        for state, label in (
            ("disponível", "available"),
            ("indisponível", "unavailable"),
            ("parcial", "partial"),
        ):
            add(
                f"comparisons.count.{component}.{label}",
                sum(row[component].get("state") == state for row in comparison_rows),
                f"count /by_r/{component}/state={state}",
            )
    stress_entries = [entry for row in comparison_rows for entry in row["x5"]]
    for state, label in (
        ("disponível", "available"),
        ("censurada", "censored"),
        ("acima da grade", "above-grid"),
        ("indisponível", "unavailable"),
    ):
        add(
            f"comparisons.count.x5.equivalent.{label}",
            sum(
                entry["equivalent_strength"]["state"] == state
                for entry in stress_entries
            ),
            f"count X5 condition/r entries with /equivalent_strength/state={state}",
        )
    for relation, label in (
        ("sobrepõe", "overlap"),
        ("acima", "above"),
        ("abaixo", "below"),
        (None, "unavailable"),
    ):
        add(
            f"comparisons.count.x5.interval.{label}",
            sum(
                entry["interval_comparison"].get("relation") == relation
                for entry in stress_entries
            ),
            f"count X5 condition/r entries with "
            f"/interval_comparison/relation={relation}",
        )
    for key in PROSE_COUNTS:
        ident = "v4x." + key
        if ident in catalog:
            add(
                key + "_prose",
                f"{int(catalog[ident]):,}",
                f"presentation of {ident} with thousands separators",
            )
    primary = "x6.x6a.band.vs_d1.primary.wilson95"
    for index, label in enumerate(("lower", "upper")):
        ident = f"v4x.{primary}.i{index:03d}"
        if ident in catalog and catalog[ident] != "unavailable":
            endpoint = Decimal(
                str(data["x6"]["x6a"]["band"]["vs_d1"]["primary"]["wilson95"][index])
            )
            thresholds = [
                Decimal(catalog["v4x.protocol.x6." + name])
                for name in (
                    ("conservative",) if label == "lower" else ("nominal", "failure")
                )
            ]
            decimals = 3
            while any(
                endpoint != threshold
                and f"{endpoint:.{decimals}f}" == f"{threshold:.{decimals}f}"
                for threshold in thresholds
            ):
                decimals += 1
            add(
                primary + ".prose_" + label,
                f"{endpoint:.{decimals}f}",
                f"presentation of /x6a/band/vs_d1/primary/wilson95/{index} "
                "to at least three decimals, distinguishing the prose comparison cuts",
            )
    files = {
        "exploratory-status": _table(
            "status",
            (
                "Exploratory execution inventory. Recorded cells include errors "
                "and fit gaps; incomplete cells remain outside their outcome "
                "denominators."
            ),
            ("Analysis", "Recorded", "Incomplete", "Errors", "Fit gaps"),
            statuses,
            synthetic,
        )
    }
    rows = []
    for index, row in enumerate(data["x3"]["cells"]):
        key = f"v4x.x3.cells.{row_key(row, index)}"
        rows.append(
            [
                _macro(catalog, key + ".cell.r"),
                _macro(catalog, key + ".cell.a"),
                _macro(catalog, key + ".reading"),
                _macro(catalog, key + ".delta.point"),
                _interval(catalog, key + ".delta.interval_95"),
            ]
        )
    files["exploratory-x3"] = _table(
        "x3",
        (
            "Free versus known signal share for the lag-pair LDA. Intervals "
            "condition on accepted fitting and training and omit uncertainty "
            "in three-parameter matching. Missing contrasts are gaps or "
            "recorded errors."
        ),
        ("$r$", "$a$", "Machine reading", r"$\Delta$AUC", "Interval"),
        rows,
        synthetic,
    )
    for name, field in (("x4a", "power_or"), ("x4b", "power_pu")):
        rows = []
        for index, row in enumerate(data["x4"][name]):
            key = f"v4x.x4.{name}.{row_key(row, index)}"
            rows.append(
                [
                    _macro(catalog, key + ".cell.r"),
                    _macro(catalog, key + ".cell.a"),
                    _macro(catalog, key + f".{name}.{field}"),
                    _interval(catalog, key + f".{name}.{field}_interval_95"),
                    _macro(catalog, key + f".{name}.test_panels"),
                ]
            )
        files[f"exploratory-{name}"] = _table(
            name,
            (
                "Conditional oracle rejection reference. The direction knows the "
                "alternative; fitted-panel failures count as non-rejections. "
                "Zero-strength compatibility is local to that cell."
            ),
            ("$r$", "$a$", "Rejection reference", "Interval", "Panels"),
            rows,
            synthetic,
        )
    rows = []
    for name in ("x6a", "x6b"):
        section = data["x6"][name]
        entries = (
            [("Joint band", f"v4x.x6.{name}.band", section["band"])]
            if "band" in section
            else []
        )
        entries += [
            (name, f"v4x.x6.{name}.{field}.{row_key(row, index)}", row)
            for field in ("strengths", "cells")
            for index, row in enumerate(section.get(field, []))
        ]
        for label, key, row in entries:
            for truth in ("d1", "pop"):
                for kind, reading in (row.get(f"vs_{truth}") or {}).items():
                    if not isinstance(reading, dict) or "covered" not in reading:
                        continue
                    prefix = f"{key}.vs_{truth}.{kind}"
                    short = {
                        "primary": "joint",
                        "gaps_as_misses": "joint+gap",
                        "pointwise": "PW",
                        "pointwise_gaps_as_misses": "PW+gap",
                        "band_interval": "band",
                    }[kind]
                    coordinates = (
                        (
                            _macro(catalog, key + ".a")
                            + ", "
                            + _macro(catalog, key + ".r")
                        )
                        if "a" in row
                        else "joint"
                    )
                    rows.append(
                        [
                            coordinates,
                            escaped(label + " / " + truth + " / " + short),
                            _macro(catalog, prefix + ".covered")
                            + "/"
                            + _macro(catalog, prefix + ".total"),
                            _interval(catalog, prefix + ".wilson95"),
                            _macro(catalog, prefix + ".reading"),
                        ]
                    )
    files["exploratory-x6"] = _table(
        "x6",
        (
            "Coverage relative to success-conditioned procedural truth or "
            "approximate population-match truth. Primary joint coverage "
            "requires a complete gap-free band over the entire declared grid. "
            "Gaps-as-misses references exclude errors without curves and "
            "incomplete units."
        ),
        ("$a,r$", "Reference", "Covered / total", "Wilson interval", "Machine reading"),
        rows,
        synthetic,
    )
    rows = []
    for index, row in enumerate(data["x7"]["units"]):
        key = f"v4x.x7.units.{row_key(row, index)}"
        rows.append(
            [
                _macro(catalog, key + ".r"),
                _macro(
                    catalog,
                    key
                    + (".status" if row.get("status") == "incomplete" else ".reading"),
                ),
                _macro(catalog, key + ".x7.first"),
                _macro(catalog, key + ".rich.first"),
                _interval(catalog, key + ".rich.first_interval"),
            ]
        )
    files["exploratory-x7"] = _table(
        "x7",
        (
            "Frozen-feature and expanded-feature LDAs on paired exploratory "
            "seeds. Boundary intervals and censoring follow the frozen rules. "
            "Feature expansion changes estimation and regularization as well "
            "as information."
        ),
        (
            "$r$",
            "Machine reading",
            "Frozen first",
            "Expanded first",
            "Expanded interval",
        ),
        rows,
        synthetic,
    )
    rows = []
    for field in data["comparisons"]["by_r"]:
        key = "v4x.comparisons.by_r." + re.sub(r"[^A-Za-z0-9_-]", "-", field)
        rows.append(
            [
                _macro(catalog, key + ".r"),
                _macro(catalog, key + ".main_curve.first.point"),
                _macro(catalog, key + ".x3.state"),
                _macro(catalog, key + ".x4.P_or.state"),
                _macro(catalog, key + ".x4.P_pu.state"),
            ]
        )
    files["exploratory-comparisons"] = _table(
        "comparisons",
        (
            "Exploratory readings at the released first point boundary, "
            "without interpolation. Local availability does not remove a "
            "false global main-curve validity mark. Machine labels: disponível "
            "= available; indisponível = unavailable; parcial = partial; "
            "fora do domínio declarado = outside the declared domain."
        ),
        (
            "$r$",
            "Released first",
            "Free-share contrast",
            "Oracle reference",
            "Fitted reference",
        ),
        rows,
        synthetic,
    )
    files.update(_details(data, catalog, add, synthetic))
    files["exploratory-x6-diagnostics"] = _coverage_diagnostics(
        data["x6"], catalog, synthetic
    )
    for key in catalog:
        if key.startswith("v4x.unavailable."):
            absent = key.removeprefix("v4x.unavailable.")
            sources[key] = {
                "input": absent.split(".")[0],
                "derivation": f"field absent: v4x.{absent}; no number substituted",
            }
    target = manuscript / "generated"
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name, content in files.items():
        path = target / f"{name}.tex"
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return Export(catalog, sources, tuple(written), synthetic, provenance)


def _details(
    data: Mapping[str, Any],
    catalog: dict[str, str],
    add: Callable[[str, Any, str], None],
    synthetic: bool,
) -> dict[str, str]:
    files = {}
    rows = []
    for index, row in enumerate(data["x3"]["cells"]):
        key = f"v4x.x3.cells.{row_key(row, index)}"
        for arm in ("known", "free"):
            for attempt, _item in enumerate((row.get(arm) or {}).get("attempts", [])):
                prefix = f"{key}.{arm}.attempts.i{attempt:03d}"
                rows.append(
                    [
                        _macro(catalog, key + ".cell.a")
                        + ", "
                        + _macro(catalog, key + ".cell.r"),
                        arm,
                        _macro(catalog, prefix + ".matching_pairs"),
                        _macro(catalog, prefix + ".status"),
                        _macro(catalog, prefix + ".validation_pass"),
                    ]
                )
    files["exploratory-x3-attempts"] = _table(
        "x3-attempts",
        (
            "Recorded matching attempts for known and free signal share. "
            "Budget exhaustion, unsuccessful numerical search and validation "
            "rejection are distinct; a search label alone is not proof of "
            "infeasibility. Residuals and evaluations remain in the values "
            "catalog."
        ),
        ("$a,r$", "Arm", "Matching pairs", "Status", "Validation"),
        rows,
        synthetic,
    )
    rows = []
    for name in ("x4a", "x4b"):
        for index, row in enumerate(data["x4"][name]):
            if row["cell"]["a"] != 0:
                continue
            key = f"v4x.x4.{name}.{row_key(row, index)}"
            flag_key = (
                "v4x.x4.summary.size_at_a0."
                + name
                + "."
                + str(row["cell"]["r"]).replace(".", "-")
            )
            power = "power_or" if name == "x4a" else "power_pu"
            rows.append(
                [
                    name,
                    _macro(catalog, key + ".cell.r"),
                    _macro(catalog, flag_key),
                    _macro(catalog, key + f".{name}.{power}"),
                    _interval(catalog, key + f".{name}.{power}_interval_95"),
                    _macro(catalog, key + f".{name}.test_panels"),
                ]
            )
    files["exploratory-x4-calibration"] = _table(
        "x4-calibration",
        (
            "Zero-strength rejection references and original calibration "
            "labels. Compatibility with the nominal level applies to the "
            "specified cell only. Positive-strength references retain the "
            "corresponding local flag."
        ),
        ("Procedure", "$r$", "Machine flag", "Rate", "Interval", "Panels"),
        rows,
        synthetic,
    )
    rows = []
    for index, row in enumerate(data["x4"]["x4a"]):
        key = f"v4x.x4.x4a.{row_key(row, index)}"
        rows.append(
            [
                _macro(catalog, key + ".cell.a")
                + ", "
                + _macro(catalog, key + ".cell.r"),
                _macro(catalog, key + ".x4a.normal_theory_power.at_auc_ref"),
                _macro(catalog, key + ".normal_theory_reading"),
                _macro(catalog, key + ".x4a.auc_ref"),
                _interval(catalog, key + ".x4a.auc_ref_interval_95"),
            ]
        )
    files["exploratory-x4-normal"] = _table(
        "x4-normal",
        (
            "Normal-theory reference at the cell's own reference AUC. Machine "
            "labels describe its position inside, above or below the oracle "
            "rejection interval; interval compatibility does not validate "
            "normal theory."
        ),
        (
            "$a,r$",
            "Normal reference",
            "Machine reading",
            "Reference AUC",
            "AUC interval",
        ),
        rows,
        synthetic,
    )
    rows = []
    for index, row in enumerate(data["x4"]["x4b"]):
        key = f"v4x.x4.x4b.{row_key(row, index)}"
        stats = row.get("x4b")
        failed = _macro(catalog, key + ".x4b.fit_failures")
        panels = _macro(catalog, key + ".x4b.test_panels")
        if stats is not None:
            add(
                key.removeprefix("v4x.") + ".successful_panels",
                stats["test_panels"] - stats["fit_failures"],
                f"/x4b/{index}/x4b/test_panels minus fit_failures",
            )
        rows.append(
            [
                _macro(catalog, key + ".cell.a")
                + ", "
                + _macro(catalog, key + ".cell.r"),
                failed if stats is None else failed + "/" + panels,
                _macro(catalog, key + ".x4b.power_pu_without_failures"),
                _macro(catalog, key + ".successful_panels"),
                _macro(catalog, key + ".quantity"),
            ]
        )
    files["exploratory-x4-failures"] = _table(
        "x4-failures",
        (
            "Fitted-panel failure treatment and success-conditioned rejection "
            "reference. The quantity column preserves the original machine "
            "label without adopting a universal power-bound interpretation."
        ),
        (
            "$a,r$",
            "Failed / panels",
            "Success-conditioned",
            "Successful panels",
            "Machine quantity",
        ),
        rows,
        synthetic,
    )
    rows = []
    for index, row in enumerate(data["x4"]["x4b"]):
        key = f"v4x.x4.x4b.{row_key(row, index)}"
        rows.append(
            [
                _macro(catalog, key + ".cell.a")
                + ", "
                + _macro(catalog, key + ".cell.r"),
                _macro(catalog, key + ".x4b.difference"),
                _interval(catalog, key + ".x4b.difference_interval_95"),
                _macro(catalog, key + ".single_panel_reading"),
                _macro(catalog, key + ".size_flag"),
            ]
        )
    files["exploratory-x4-paired"] = _table(
        "x4-paired",
        (
            "Paired difference between conditional oracle rejection "
            "procedures. The difference combines fitted-panel estimation, "
            "simulation precision and failure treatment. Missing readings "
            "remain unavailable."
        ),
        ("$a,r$", "Difference", "Interval", "Machine reading", "Size flag"),
        rows,
        synthetic,
    )
    rows = []
    truth_rows = []
    precision_rows = []
    diagnostic_rows = []
    for name in ("x6a", "x6b"):
        section = data["x6"][name]
        rows.append(
            [
                name,
                _macro(catalog, f"v4x.x6.{name}.units"),
                _macro(catalog, f"v4x.x6.{name}.recorded"),
                _macro(catalog, f"v4x.x6.{name}.incomplete"),
            ]
        )
        for field in ("strengths", "cells"):
            for index, row in enumerate(section.get(field, [])):
                key = f"v4x.x6.{name}.{field}.{row_key(row, index)}"
                coordinate = (
                    _macro(catalog, key + ".a") + ", " + _macro(catalog, key + ".r")
                )
                diagnostic_rows.append(
                    [
                        coordinate,
                        _macro(catalog, key + ".complete"),
                        _macro(catalog, key + ".cell_complete"),
                        _macro(catalog, key + ".gaps"),
                        _macro(catalog, key + ".errors"),
                        _macro(catalog, key + ".retry_fraction"),
                    ]
                )
                for truth in ("d1", "pop"):
                    prefix = key + ".truth_" + truth
                    truth_rows.append(
                        [
                            coordinate,
                            truth,
                            _macro(catalog, prefix + ".value"),
                            _macro(catalog, prefix + ".mcse"),
                            _macro(catalog, prefix + ".retry_fraction"),
                            _macro(
                                catalog,
                                prefix + ".successful"
                                if truth == "d1"
                                else prefix + ".trainings",
                            ),
                        ]
                    )
                for kind, reading in (row.get("vs_d1") or {}).items():
                    if not isinstance(reading, dict) or "covered" not in reading:
                        continue
                    prefix = key + ".vs_d1." + kind
                    precision_rows.append(
                        [
                            coordinate,
                            escaped(
                                kind.replace("pointwise", "PW").replace(
                                    "_gaps_as_misses", "+gap"
                                )
                            ),
                            _macro(catalog, prefix + ".conservative"),
                            _macro(catalog, prefix + ".truth_precision.inconclusive"),
                            _macro(catalog, prefix + ".nominal_reading"),
                        ]
                    )
    files["exploratory-x6-inventory"] = _table(
        "x6-inventory",
        (
            "Exploratory coverage job inventory, including independent truth "
            "and population-match jobs. Incomplete jobs at the declared cut "
            "are separate from recorded errors and fit gaps."
        ),
        ("Analysis", "Declared jobs", "Recorded jobs", "Incomplete jobs"),
        rows,
        synthetic,
    )
    files["exploratory-x6-denominators"] = _table(
        "x6-denominators",
        (
            "Cell and complete-unit denominators as computed by the "
            "aggregator. For the unit-wide analysis, successful cells from an "
            "incomplete band do not enter its primary coverage. Errors "
            "preserve the aggregator's conditioning."
        ),
        (
            "$a,r$",
            "Complete units/cells",
            "Successful cells",
            "Gaps",
            "Errors",
            "Retry fraction",
        ),
        diagnostic_rows,
        synthetic,
    )
    files["exploratory-x6-truth"] = _table(
        "x6-truth",
        (
            "Independent procedural D1 truth conditional on successful "
            "pipelines, including declared retries, and approximate "
            "population-match truth. Monte Carlo error for the latter omits "
            "population-fit approximation error. Zero-strength truth is by "
            "construction."
        ),
        (
            "$a,r$",
            "Truth",
            "Estimate",
            "MC error",
            "Retry fraction",
            "Successes / trainings",
        ),
        truth_rows,
        synthetic,
    )
    files["exploratory-x6-precision"] = _table(
        "x6-precision",
        (
            "Conservative flags and procedural-truth precision sensitivity. A "
            "changed reading remains inconclusive due to reference precision; "
            "unavailable sensitivity fields are not false flags."
        ),
        (
            "$a,r$",
            "Reference",
            "Conservative flag",
            "Precision inconclusive",
            "Nominal reading",
        ),
        precision_rows,
        synthetic,
    )
    rows = []
    delta_rows = []
    for index, row in enumerate(data["x7"]["units"]):
        key = f"v4x.x7.units.{row_key(row, index)}"
        for arm in ("x7", "rich"):
            for kind in ("first", "sustained"):
                prefix = key + "." + arm + "." + kind
                rows.append(
                    [
                        _macro(catalog, key + ".r"),
                        arm + " / " + kind,
                        _macro(catalog, prefix),
                        _interval(catalog, prefix + "_interval"),
                        _macro(catalog, prefix + "_censoring"),
                        _macro(catalog, prefix + "_interval_censoring"),
                    ]
                )
        for position, delta in enumerate(row.get("delta_auc", [])):
            prefix = key + f".delta_auc.{row_key(delta, position)}"
            delta_rows.append(
                [
                    _macro(catalog, key + ".r"),
                    _macro(catalog, prefix + ".a"),
                    _macro(catalog, prefix + ".delta"),
                    _interval(catalog, prefix + ".interval"),
                ]
            )
    files["exploratory-x7-boundaries"] = _table(
        "x7-boundaries",
        (
            "First and sustained boundaries with point and interval censoring "
            "for both paired LDAs. Unavailable denotes a null field: in the "
            "censoring columns, no censoring; an unavailable point or interval "
            "end is censored at the gap named there or, in a complete valid "
            "unit without a gap label, was not reached on the complete "
            "eligible grid ($>0.9$). "
            "x7: frozen-feature LDA; rich: expanded-feature LDA."
        ),
        (
            "$r$",
            "Arm / boundary",
            "Point",
            "Interval",
            "Point censoring",
            "Interval censoring",
        ),
        rows,
        synthetic,
    )
    files["exploratory-x7-deltas"] = _table(
        "x7-deltas",
        (
            "Expanded-minus-frozen AUC with paired network bootstrap "
            "intervals by strength. These contrasts apply to the two declared "
            "fitted LDAs."
        ),
        ("$r$", "$a$", r"$\Delta$AUC", "Interval"),
        delta_rows,
        synthetic,
    )
    boundaries = []
    twin_boundaries = []
    selected = []
    missing = []
    stress = []
    x7_by_r = {row["r"]: index for index, row in enumerate(data["x7"]["units"])}
    for field, row in data["comparisons"]["by_r"].items():
        key = "v4x.comparisons.by_r." + field.replace(".", "-")
        rich_key = "v4x.x7.units." + row_key(data["x7"]["units"][x7_by_r[row["r"]]], 0)
        boundaries.append(
            [
                _macro(catalog, key + ".r"),
                _macro(catalog, key + ".main_curve.first.point"),
                _macro(catalog, key + ".x1b.first.point"),
                _macro(catalog, rich_key + ".x7.first"),
                _macro(catalog, rich_key + ".rich.first"),
                _macro(catalog, key + ".main_curve.main_curve_valid"),
            ]
        )
        twin_boundaries.append(
            [
                _macro(catalog, key + ".r"),
                *(
                    _comparison_boundary(
                        catalog, key + "." + component, row[component], kind
                    )
                    for component in ("x1b", "main_curve")
                    for kind in ("first", "sustained")
                ),
                _macro(catalog, key + ".main_curve.main_curve_valid"),
            ]
        )
        selected.append(
            [
                _macro(catalog, key + ".r"),
                _macro(catalog, key + ".x3.reading"),
                _macro(catalog, key + ".x3.delta.point"),
                _interval(catalog, key + ".x3.delta.interval_95"),
                _macro(catalog, key + ".x4.P_or.statistics.power_or"),
                _macro(catalog, key + ".x4.P_pu.statistics.power_pu"),
            ]
        )
        for component in ("main_curve", "x1b", "x3", "x4"):
            prefix = key + "." + component
            reason = _macro(catalog, prefix + ".reason")
            missing.append(
                [
                    _macro(catalog, key + ".r"),
                    escaped(component),
                    _macro(catalog, prefix + ".state"),
                    reason if row[component].get("state") != "disponível" else "",
                ]
            )
        for index, condition in enumerate(row["x5"]):
            prefix = key + ".x5." + row_key(condition, index)
            stress.append(
                [
                    _macro(catalog, key + ".r"),
                    _macro(catalog, prefix + ".channel.name"),
                    _macro(catalog, prefix + ".equivalent_strength.point"),
                    _macro(catalog, prefix + ".equivalent_strength.state"),
                    _macro(catalog, prefix + ".equivalent_strength.censored_at"),
                    _macro(catalog, prefix + ".interval_comparison.relation"),
                ]
            )
    files["exploratory-x1b-boundaries"] = _table(
        "x1b-boundaries",
        (
            "Exploratory X1b: mean-field twin boundaries against null B at every "
            "$r$, including units with no attained boundary. The principal "
            "confirmatory curve appears beside it for context only, without a "
            "between-curve test. Each boundary cell gives the point, inverted "
            "interval, availability state, unit status, point censoring (C) "
            "and interval censoring (IC), retaining reasons for unavailability. "
            "The catalog's unavailable token denotes a null or absent field: "
            "C or IC unavailable means no gap censoring, and a point or "
            "interval end that is unavailable in a complete valid unit "
            "without a gap label was not "
            "reached on the complete eligible grid ($>0.9$, right-censored; "
            r"Table~\ref{tab:v4-T1}). "
            "Machine labels: disponível = available; indisponível = "
            "unavailable; censurada = censored at a gap; não atingida na "
            "grade = not reached on the grid; completo válido = complete "
            "valid; completo inválido = complete invalid. "
            "Global main-curve validity ($V_B$) remains explicit."
        ),
        (
            "$r$",
            "$a^*_{MF}(r)$ first",
            "$a^*_{MF}(r)$ sustained",
            "Principal first",
            "Principal sustained",
            "$V_B$",
        ),
        twin_boundaries,
        synthetic,
    )
    files["exploratory-boundary-comparisons"] = _table(
        "boundary-comparisons",
        (
            "Released confirmatory first boundary beside twin and both "
            "exploratory LDA boundaries. Different seed sets are displayed "
            "side by side without a between-curve test. Global validity "
            "remains explicit. Unavailable denotes a null or absent field; "
            "an unavailable boundary in a complete valid unit without a gap "
            "label was not reached on the complete eligible grid, and a "
            "gap-labelled boundary is censored there. Point and interval "
            r"censoring appear in Table~\ref{tab:v4x-x1b-boundaries}; C or IC "
            "unavailable means no gap censoring."
        ),
        ("$r$", "Released", "Twin", "Frozen exploratory", "Expanded", "Global valid"),
        boundaries,
        synthetic,
    )
    files["exploratory-selected-comparisons"] = _table(
        "selected-comparisons",
        (
            "Free-share contrast and conditional oracle rejection references "
            "selected at the released first point boundary. Selection neither "
            "estimates the frozen boundary nor adds a confirmatory contrast."
        ),
        ("$r$", "X3 label", r"$\Delta$AUC", "Interval", "Oracle", "Fitted"),
        selected,
        synthetic,
    )
    files["exploratory-comparison-states"] = _table(
        "comparison-states",
        (
            "Comparison availability and original reasons. Missing "
            "aggregates, a zero-strength boundary, unestimated cells, errors "
            "and censoring do not imply a null result. Machine labels: "
            "disponível = available; indisponível = unavailable; "
            "parcial = partial; fora do domínio declarado = outside the "
            "declared domain. Reasons appear on every row that is not available."
        ),
        ("$r$", "Component", "State", "Reason"),
        missing,
        synthetic,
    )
    files["exploratory-stress-comparisons"] = _table(
        "stress-comparisons",
        (
            "Misspecification equivalent strength is the first point-AUC "
            "attainment on the declared grid. A preceding gap censors it; "
            "overlap refers to the misspecification interval and the band at "
            "the released first boundary. Machine labels: disponível = "
            "available; indisponível = unavailable; censurada = censored at "
            "a gap; acima da grade = above the grid; abaixo/sobrepõe/acima = "
            "below/overlaps/above. The censoring strength is reported separately. "
            "In the Gap at $a$ column, unavailable means no gap before the attainment."
        ),
        (
            "$r$",
            "Condition",
            "Equivalent strength",
            "State",
            "Gap at $a$",
            "Interval relation",
        ),
        stress,
        synthetic,
    )
    return files


def _coverage_diagnostics(
    data: Mapping[str, Any], catalog: MutableMapping[str, str], synthetic: bool
) -> str:
    rows = []
    for name in ("x6a", "x6b"):
        for field in ("strengths", "cells"):
            for index, row in enumerate(data[name].get(field, [])):
                key = f"v4x.x6.{name}.{field}.{row_key(row, index)}"
                coordinate = (
                    _macro(catalog, key + ".a") + ", " + _macro(catalog, key + ".r")
                )
                for label, metric, error in (
                    (
                        "Mean standardized error",
                        "vs_d1.standardized_error.mean",
                        "vs_d1.standardized_error.mean_interval95",
                    ),
                    (
                        "SD standardized error / bias flag",
                        "vs_d1.standardized_error.sd",
                        "vs_d1.standardized_error.uncovered_bias",
                    ),
                    (
                        "Lower standardized tail",
                        "vs_d1.standardized_error.below_minus_1_96",
                        None,
                    ),
                    (
                        "Upper standardized tail",
                        "vs_d1.standardized_error.above_1_96",
                        None,
                    ),
                    ("Mean D5 shift", "matching_bias.d5_mean_shift.mean", None),
                    (
                        "Empirical matching bias",
                        "matching_bias.empirical_bias.mean",
                        "matching_bias.empirical_bias.mcse",
                    ),
                    (
                        "D1 minus population truth",
                        "matching_bias.truth_d1_minus_pop.value",
                        "matching_bias.truth_d1_minus_pop.se",
                    ),
                    ("Mean amplification", "matching_bias.amplification.mean", None),
                    ("MSE / mean squared SE", "matching_bias.mse_to_mean_se2", None),
                ):
                    rows.append(
                        [
                            coordinate,
                            label,
                            _macro(catalog, key + "." + metric),
                            _interval(catalog, key + "." + error)
                            if error
                            else "not applicable",
                        ]
                    )
                for moment in range(2):
                    rows.append(
                        [
                            coordinate,
                            "Lag-one residual mean / SD"
                            if moment == 0
                            else "Lag-two residual mean / SD",
                            _macro(
                                catalog,
                                key
                                + ".matching_bias.fit_residual_se_units.mean."
                                + f"i{moment:03d}",
                            ),
                            _macro(
                                catalog,
                                key
                                + ".matching_bias.fit_residual_se_units.sd."
                                + f"i{moment:03d}",
                            ),
                        ]
                    )
    return _table(
        "x6-diagnostics",
        (
            "Standardized errors and matching-bias diagnostics relative to "
            "procedural D1 truth. The last column reports a Monte Carlo "
            "interval, Monte Carlo error, residual SD or recorded bias flag "
            "as named by the metric. These diagnostics do not establish a "
            "coverage or causation claim."
        ),
        ("$a,r$", "Diagnostic", "Estimate", "MC interval / error / SD / flag"),
        rows,
        synthetic,
    )


def values_record(result: Export) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "synthetic": result.synthetic,
        "values": result.catalog,
        "sources": result.sources,
        "inputs": result.provenance,
        "code": {
            "exporter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        },
    }


def merge_values(*records: Mapping[str, Any]) -> dict[str, Any]:
    """Join confirmatory and exploratory catalogs without overriding any ID."""
    values: dict[str, str] = {}
    sources: dict[str, Any] = {}
    for record in records:
        if not isinstance(record.get("values"), dict):
            raise ValueError("Invalid result values map")
        overlap = values.keys() & record["values"].keys()
        if overlap:
            raise ValueError("Result ID collision: " + ", ".join(sorted(overlap)))
        values.update(record["values"])
        sources.update(record.get("sources", {}))
    return {
        "schema": "ic-study.v4-merged-result-values.v1",
        "synthetic": any(record.get("synthetic") is True for record in records),
        "values": values,
        "sources": sources,
        "components": [
            {k: v for k, v in record.items() if k not in {"values", "sources"}}
            for record in records
        ],
    }


def _write_json(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            record, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
        )
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in NAMES:
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--values", type=Path, required=True)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument(
        "--confirmatory-values",
        type=Path,
        help="Explicit values/catalog JSON to merge; collisions are errors",
    )
    parser.add_argument("--fill", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = export({name: getattr(args, name) for name in NAMES}, args.manuscript)
        records = [values_record(result)]
        if args.confirmatory_values is not None:
            records.insert(0, json.loads(args.confirmatory_values.read_bytes()))
        merged = merge_values(*records)
        used = used_ids(args.manuscript)
        missing = sorted(used - merged["values"].keys())
        if missing:
            raise ValueError("Unresolved result IDs: " + ", ".join(missing))
        if args.fill:
            fill(args.manuscript, merged["values"])
        merged["values"] = {key: merged["values"][key] for key in sorted(used)}
        merged["sources"] = {
            key: value for key, value in merged["sources"].items() if key in used
        }
        _write_json(args.values, merged)
        if args.catalog is not None:
            _write_json(args.catalog, merge_values(*records))
        print(
            f"Exported {len(result.written)} exploratory tables; "
            f"{len(used)} bound IDs; synthetic={merged['synthetic']}"
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
