"""Protocol constants cited by the v4 Results text, read from the frozen sources.

Constants are read from hash-verified frozen sources. Module constants and plan
functions come from the frozen
v4 tree; literals of frozen functions are parsed from their source only after the
module's SHA-256 matches ``freeze-v4.json``; criteria come from the frozen
``criteria-v43.json`` and the Wald level from the frozen SHP preregistration. The
region cut and secondary targets come from the frozen v1 preregistration. Every
value is formatted as
the Results text prints it, for ``\\resultnum{v4.protocol.*}{...}``.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from functools import cache
from pathlib import Path
from statistics import NormalDist
from typing import Any, cast
from zoneinfo import ZoneInfo

from ic_study.simulation.detection_v4 import GRID, RELIABILITIES
from ic_study.simulation.v4_plan import CLOSE_UTC, SCENARIOS, gate_tasks, inventory

STUDY = Path(__file__).resolve().parents[3]
FREEZE = STUDY / "experiments/exploratory/detection-boundary-v4/freeze-v4.json"
CRITERIA = "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
SHP_FREEZE = (
    STUDY
    / "research/questions/exploration/2026-09-24-parallel/shp-reliability-freeze.json"
)
PREREGISTRATION_FREEZE = (
    STUDY
    / "research/questions/exploration/2026-09-24-parallel"
    / "detection-boundary-freeze.json"
)
PREREGISTRATION = PREREGISTRATION_FREEZE.with_name(
    "detection-boundary-preregistration-frozen.md"
)
CLOSE_ZONE = "America/Sao_Paulo"
BOUNDARIES = "src/ic_study/analysis/detection_boundary.py"
INFERENCE = "src/ic_study/analysis/detection_boundary_v4.py"
GATE = "src/ic_study/simulation/v4_gate.py"
CRITERIA_CODE = "src/ic_study/simulation/v4_criteria.py"
PANELS = "src/ic_study/simulation/detection_v4.py"
PLAN = "src/ic_study/simulation/v4_plan.py"


def _verified(path: Path, digest: str) -> bytes:
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != digest:
        raise ValueError(f"{path.name} differs from its freeze record")
    return content


@cache
def _freeze() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(FREEZE.read_text(encoding="utf-8")))


@cache
def _module(relative: str) -> ast.Module:
    return ast.parse(_verified(STUDY / relative, _freeze()["code"][relative]))


def _function(relative: str, name: str) -> ast.FunctionDef:
    for node in ast.walk(_module(relative)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ValueError(f"No frozen function {name} in {relative}")


def _single(values: list[Any], what: str) -> Any:
    if not values or any(value != values[0] for value in values):
        raise ValueError(f"No single frozen literal for {what}")
    return values[0]


def _literal(node: ast.expr) -> Any:
    try:
        return ast.literal_eval(node)
    except ValueError:
        return None


def compared(
    relative: str,
    function: str,
    left: str,
    *,
    stage: str | None = None,
    operator: type[ast.cmpop] | None = None,
) -> Any:
    """The literal that a frozen function compares the expression ``left`` with."""
    scope: ast.AST = _function(relative, function)
    if stage is not None:
        branch = next(
            node
            for node in ast.walk(scope)
            if isinstance(node, ast.If)
            and ast.unparse(node.test) == f"gate == {stage!r}"
        )
        scope = ast.Module(body=branch.body, type_ignores=[])
    values = [
        _literal(comparator)
        for node in ast.walk(scope)
        if isinstance(node, ast.Compare)
        and ast.unparse(node.left) == left
        and (operator is None or isinstance(node.ops[0], operator))
        for comparator in node.comparators
    ]
    return _single([v for v in values if v is not None], f"{function}: {left}")


def argument(relative: str, function: str, call: str, index: int) -> Any:
    """The literal passed at position ``index`` to ``call`` in a frozen function."""
    values = [
        _literal(node.args[index])
        for node in ast.walk(_function(relative, function))
        if isinstance(node, ast.Call)
        and ast.unparse(node.func) == call
        and len(node.args) > index
    ]
    return _single([v for v in values if v is not None], f"{function}: {call}")


def default(relative: str, function: str, parameter: str) -> Any:
    """The default of a frozen function's parameter."""
    arguments = _function(relative, function).args
    positional = arguments.args[len(arguments.args) - len(arguments.defaults) :]
    pairs = [
        *zip(positional, arguments.defaults, strict=True),
        *zip(arguments.kwonlyargs, arguments.kw_defaults, strict=True),
    ]
    for arg, value in pairs:
        if arg.arg == parameter and value is not None:
            return _literal(value)
    raise ValueError(f"{function} has no default for {parameter}")


def places(value: float) -> str:
    """A grid value with at least two decimals, as the text prints it (0.10)."""
    if value == 0:
        return "0"
    decimals = len(f"{value:.6f}".rstrip("0").split(".")[1])
    return f"{value:.{max(2, decimals)}f}"


def tag(value: float) -> str:
    return places(value).replace(".", "")


def percent(value: float) -> str:
    return f"{round(value * 100, 6):g}"


@dataclass(frozen=True)
class Protocol:
    """Raw protocol constants, before formatting."""

    small_cut: float
    secondary_targets: tuple[float, ...]
    target: float
    null_auc: float
    critical_floor: float
    g0_implementation_limit: float
    g1b_pass_mark: int
    g1b_repetitions: int
    g1c_fits: int
    g1c_mean_z_limit: float
    g1c_pointwise_limit: int
    g2_pipelines_per_cell: int
    g2_cell_failure_limit: int
    g2_pooled_failure_fraction: float
    g2_min_pairs: int
    g2c_failure_allowances: dict[int, int]
    fd_steps: tuple[float, ...]
    fd_range: tuple[float, float]
    joint_pass: dict[str, float]
    g2c_refits: dict[float, int]
    g2c_bound_quantile: float
    g2c_upper_minimum: float
    g2c_lower_maximum: float
    retry_pairs: int
    equivalence_margin: float
    shp_wald_level: int
    shp_anchor_year: int


def _shp_preregistration() -> dict[str, Any]:
    freeze = json.loads(SHP_FREEZE.read_text(encoding="utf-8"))
    record = freeze["preregistration"]["machine_json"]
    content = _verified(STUDY.parents[1] / record["path"], record["sha256"])
    return cast(dict[str, Any], json.loads(content))


def _preregistered_rules() -> tuple[float, tuple[float, ...]]:
    record = json.loads(PREREGISTRATION_FREEZE.read_bytes())
    text = _verified(PREREGISTRATION, record["protocol_sha256"]).decode("utf-8")
    cut = re.search(r"pequena, `0<a\*≤(\d+,\d+)`", text)
    targets = re.search(r"Alvos (\d+,\d+) e (\d+,\d+)\s+são secundários", text)
    if cut is None or targets is None:
        raise ValueError(
            "Frozen preregistration has no readable region/secondary rules"
        )
    return float(cut[1].replace(",", ".")), tuple(
        float(value.replace(",", ".")) for value in targets.groups()
    )


def _pooled_failure_fraction() -> float:
    node = next(
        node
        for node in ast.walk(_function(CRITERIA_CODE, "dispersion"))
        if isinstance(node, ast.Call) and ast.unparse(node.func) == "ceil"
    )
    product = node.args[0]
    if not isinstance(product, ast.BinOp) or not isinstance(product.op, ast.Mult):
        raise ValueError("No frozen pooled failure fraction")
    return float(_literal(product.left))


def _refit_allowances() -> dict[int, int]:
    for node in ast.walk(_function(CRITERIA_CODE, "refit_ratio")):
        if isinstance(node, ast.Assign) and any(
            ast.unparse(target) == "allowance" for target in node.targets
        ):
            value = node.value
            if isinstance(value, ast.IfExp) and isinstance(value.test, ast.Compare):
                first = int(_literal(value.test.comparators[0]))
                counts = next(
                    _literal(n.comparators[0])
                    for n in ast.walk(_function(CRITERIA_CODE, "refit_ratio"))
                    if isinstance(n, ast.Compare)
                    and ast.unparse(n.left) == "len(refits)"
                    and isinstance(n.ops[0], ast.NotIn)
                )
                second = next(count for count in counts if count != first)
                return {
                    first: int(_literal(value.body)),
                    second: int(_literal(value.orelse)),
                }
    raise ValueError("No frozen refit failure allowances")


@cache
def protocol() -> Protocol:
    """Read every constant; refuse any frozen source whose hash has drifted."""
    _module(PLAN)
    _module(PANELS)
    criteria = json.loads(
        _verified(STUDY / CRITERIA, _freeze()["artifacts"]["criteria-v43.json"])
    )
    thresholds = criteria["G2c_fixed_thresholds"]
    refits: dict[float, int] = {}
    for task in gate_tasks("G2c"):
        if not task.baseline:
            refits[task.cell.share] = refits.get(task.cell.share, 0) + 1
    primary = _shp_preregistration()["primary"]
    wald = re.fullmatch(r".*Wald (\d+) percent.*", primary["interval"])
    if wald is None:
        raise ValueError("The SHP preregistration states no Wald level")
    small_cut, secondary_targets = _preregistered_rules()
    return Protocol(
        small_cut=small_cut,
        secondary_targets=secondary_targets,
        target=default(BOUNDARIES, "boundary_report", "target"),
        null_auc=compared(BOUNDARIES, "boundary_report", "lower[0]"),
        critical_floor=compared(INFERENCE, "band", "empirical"),
        g0_implementation_limit=compared(
            GATE, "aggregate", "implementation / fits_count"
        ),
        g1b_pass_mark=compared(GATE, "aggregate", "min(counts.values())"),
        g1b_repetitions=len(gate_tasks("G1b")) // len(SCENARIOS),
        g1c_fits=compared(GATE, "aggregate", "anchors", stage="G1c"),
        g1c_mean_z_limit=compared(GATE, "aggregate", "mean_z"),
        g1c_pointwise_limit=compared(GATE, "aggregate", "pointwise"),
        g2_pipelines_per_cell=criteria["pipelines_per_cell"],
        g2_cell_failure_limit=compared(CRITERIA_CODE, "dispersion", "failed.sum(1)"),
        g2_pooled_failure_fraction=_pooled_failure_fraction(),
        g2_min_pairs=compared(
            CRITERIA_CODE, "dispersion", "pair_counts", operator=ast.Lt
        ),
        g2c_failure_allowances=_refit_allowances(),
        fd_steps=tuple(sorted(compared(INFERENCE, "finite_differences", "step"))),
        fd_range=tuple(criteria["fd_model"]["accepted_interval"]),
        joint_pass=criteria["operating_characteristics"]["correct"]["joint"],
        g2c_refits=refits,
        g2c_bound_quantile=max(
            argument(CRITERIA_CODE, "refit_ratio", "np.quantile", 1)
        ),
        g2c_upper_minimum=thresholds["one_sided_95_upper_minimum"],
        g2c_lower_maximum=thresholds["one_sided_95_lower_maximum"],
        retry_pairs=argument(PANELS, "fit_cell", "enumerate", 0)[-1],
        equivalence_margin=compared(INFERENCE, "validate_fit", "equivalence[:moments]"),
        shp_wald_level=int(wald.group(1)),
        shp_anchor_year=primary["anchor_year"],
    )


def _configurations() -> list[tuple[int, str, str, str, dict[str, Any]]]:
    seen: dict[tuple[int, str, str, str], dict[str, Any]] = {}
    for row in inventory():
        key = (
            int(cast(int, row["tier"])),
            str(row["family"]),
            str(row["channel"]),
            str(row["sensitivity"]),
        )
        seen.setdefault(key, cast(dict[str, Any], row["options"]))
    return [(*key, options) for key, options in seen.items()]


def _one(values: Iterable[int], what: str) -> int:
    found = set(values)
    if len(found) != 1:
        raise ValueError(f"The frozen inventory has no single tier for {what}")
    return found.pop()


def _inventory_values() -> tuple[dict[str, str], int]:
    """Unit counts, tier numbers and sensitivity levels, and the count of B units."""
    configurations = _configurations()
    units: dict[int, set[str]] = {}
    for row in inventory():
        units.setdefault(int(cast(int, row["tier"])), set()).add(str(row["unit"]))
    tiers = {
        "main_B": _one(
            (
                t
                for t, f, c, s, _ in configurations
                if (f, c, s) == ("B", "observed", "main")
            ),
            "B",
        ),
        "main_others": _one(
            (
                t
                for t, f, c, s, _ in configurations
                if f != "B" and (c, s) == ("observed", "main")
            ),
            "A, C, D and E",
        ),
        "controls": _one(
            (t for t, _, c, s, _ in configurations if c != "observed" and s == "main"),
            "the controls",
        ),
    }
    sensitivities = sorted(
        {t for t, _, _, s, _ in configurations if s not in ("main", "mobility")}
    )
    tiers |= {
        "first_sensitivity": sensitivities[0],
        "last_sensitivity": sensitivities[-1],
    }
    steps = [o["steps"] for *_, o in configurations if "steps" in o]
    anchors = [o["anchor"] for *_, o in configurations if "anchor" in o]
    b_units = len(
        {
            str(row["unit"])
            for row in inventory()
            if row["tier"] == tiers["main_B"] and row["family"] == "B"
        }
    )
    values = {
        "v4.protocol.units.all": str(sum(len(keys) for keys in units.values())),
        **{
            f"v4.protocol.units.t{t}": str(len(keys))
            for t, keys in sorted(units.items())
        },
        **{f"v4.protocol.tier.{name}": str(value) for name, value in tiers.items()},
        "v4.protocol.steps": str(_one(steps, "the step sensitivity")),
        "v4.protocol.omega_full": f"{max(anchors):g}",
    }
    return values, b_units


def protocol_values() -> dict[str, str]:
    """Every protocol constant the Results text may cite, as printed."""
    p = protocol()
    close = datetime.fromisoformat(CLOSE_UTC).astimezone(ZoneInfo(CLOSE_ZONE))
    inventory_values, b_units = _inventory_values()
    per_unit = 2 * (1 - NormalDist().cdf(p.critical_floor))
    chance = 1 - (1 - per_unit) ** b_units
    low, high = p.fd_range
    return {
        **{f"v4.protocol.a.{tag(a)}": places(a) for a in GRID},
        **{f"v4.protocol.r.{tag(r)}": places(r) for r in RELIABILITIES},
        **inventory_values,
        "v4.protocol.grid_cells": str(len(GRID) * len(RELIABILITIES)),
        "v4.protocol.close_local": f"{close.day} {close:%B %Y} at {close:%H:%M}",
        "v4.protocol.target": places(p.target),
        "v4.protocol.null_auc": f"{p.null_auc:g}",
        "v4.protocol.critical_floor": f"{p.critical_floor:g}",
        "v4.protocol.chance_invalidation": f"{100 * chance:.1f}",  # Methods M75
        "v4.protocol.small_cut": places(p.small_cut),
        "v4.protocol.secondary_target.lower": places(min(p.secondary_targets)),
        "v4.protocol.secondary_target.upper": places(max(p.secondary_targets)),
        "v4.protocol.g0.implementation_limit": percent(p.g0_implementation_limit),
        "v4.protocol.g1b.pass_mark": str(p.g1b_pass_mark),
        "v4.protocol.g1b.repetitions": f"{p.g1b_repetitions:,}",
        "v4.protocol.g1c.fits": str(p.g1c_fits),
        **{
            f"v4.protocol.g1c.r.{index}": places(r)
            for index, r in enumerate(
                sorted({task.cell.reliability for task in gate_tasks("G1c")}), 1
            )
        },
        "v4.protocol.g1c.mean_z_limit": f"{p.g1c_mean_z_limit:g}",
        "v4.protocol.g1c.pointwise_limit": str(p.g1c_pointwise_limit),
        "v4.protocol.g2.pipelines_per_cell": str(p.g2_pipelines_per_cell),
        "v4.protocol.g2.fd_step.small": str(min(p.fd_steps)),
        "v4.protocol.g2.fd_step.large": str(max(p.fd_steps)),
        "v4.protocol.g2.fd_range.lower": str(low),
        "v4.protocol.g2.fd_range.upper": str(high),
        "v4.protocol.g2.joint_pass_probability": f"{p.joint_pass['probability']:.4f}",
        "v4.protocol.g2.joint_pass_mcse_points": f"{100 * p.joint_pass['mcse']:.2f}",
        **{
            f"v4.protocol.g2c.refits.a{tag(a)}": str(count)
            for a, count in p.g2c_refits.items()
        },
        "v4.protocol.g2c.bound_level": percent(p.g2c_bound_quantile),
        "v4.protocol.g2c.upper_minimum": str(p.g2c_upper_minimum),
        "v4.protocol.g2c.lower_maximum": str(p.g2c_lower_maximum),
        "v4.protocol.retry_pairs": f"{p.retry_pairs:,}",
        "v4.protocol.equivalence_margin": str(p.equivalence_margin),
        "v4.protocol.shp.wald_level": str(p.shp_wald_level),
        "v4.protocol.shp.anchor_year": str(p.shp_anchor_year),
    }
