"""Public Owner facts absent from formatted catalogs; provenance is never followed."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import datetime, timedelta
from typing import Any, cast

FACTS_SCHEMA = "ic-study.v4-manuscript-assembly-facts.v1"
FACT_TYPES: dict[str, type | tuple[str, ...]] = {
    "shp.state": (
        "not-run",
        "failed",
        "pre-run-divergence",
        "parameter-bound",
        "admissible",
    ),
    "shp.reason": str,
    "shp.divergence": dict,
    "shp.grid_position": ("below", "above", "interval-outside", "inside"),
    "gate.at_close": bool,
    "tier2.boundaries_differ": bool,
    "main.boundary_nonmonotone": bool,
    "post.x5_supplied": bool,
    "gate.G0.failed_criteria": ("anchor", "budget", "implementation"),
    "gate.G1c.failed_criteria": ("anchor", "pointwise", "mean"),
    "gate.G2.failed_criteria": ("allowance", "above", "below", "fd", "insufficient"),
    "gate.G2c.failed_comparisons": ("a010", "a003"),
}
OWNER_SHP_STATES = frozenset({"not-run", "failed", "pre-run-divergence"})
DERIVABLE_FACTS = frozenset(
    {
        "shp.state",
        "shp.grid_position",
        "tier2.boundaries_differ",
        "main.boundary_nonmonotone",
        "gate.G0.failed_criteria",
        "gate.G1c.failed_criteria",
        "gate.G2.failed_criteria",
        "gate.G2c.failed_comparisons",
    }
)


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("Duplicate JSON key: " + key)
        obj[key] = value
    return obj


def _pre_run_divergence(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != {
        "kind",
        "recorded_utc",
        "execution_started_utc",
    }:
        return False
    if not isinstance(value["kind"], str) or value["kind"] not in {
        "item",
        "scale",
        "mode",
    }:
        return False
    try:
        recorded = datetime.fromisoformat(value["recorded_utc"])
        started = datetime.fromisoformat(value["execution_started_utc"])
        return (
            recorded.utcoffset() == started.utcoffset() == timedelta(0)
            and recorded < started
        )
    except (TypeError, ValueError):
        return False


def validate_facts(obj: object) -> dict[str, Any]:
    """Validate a closed schema, strict types and an immutable source per fact.

    Missing facts remain missing: only the selected shell conditions decide
    which are required. Sources identify public records; no path is opened.
    """
    if not isinstance(obj, dict) or set(obj) != {"schema", "synthetic", "facts"}:
        raise ValueError("Expected assembly-facts schema, synthetic and facts")
    if obj["schema"] != FACTS_SCHEMA or type(obj["synthetic"]) is not bool:
        raise ValueError("Unsupported assembly-facts schema or synthetic flag")
    facts = obj["facts"]
    if not isinstance(facts, dict) or facts.keys() - FACT_TYPES.keys():
        raise ValueError("Unknown assembly fact")
    for name, fact in facts.items():
        if not isinstance(fact, dict) or set(fact) != {"value", "source"}:
            raise ValueError("Fact needs value and source: " + name)
        source = fact["source"]
        if (
            not isinstance(source, dict)
            or set(source) != {"record", "locator", "sha256"}
            or any(not isinstance(v, str) or not v.strip() for v in source.values())
            or re.fullmatch(r"[0-9a-f]{64}", source["sha256"]) is None
        ):
            raise ValueError("Fact needs record, locator and SHA-256: " + name)
        value, expected = fact["value"], FACT_TYPES[name]
        if isinstance(expected, tuple):
            if name.endswith(("failed_criteria", "failed_comparisons")):
                valid = (
                    isinstance(value, list)
                    and bool(value)
                    and all(isinstance(v, str) and v in expected for v in value)
                    and len(value) == len(set(value))
                )
            else:
                valid = isinstance(value, str) and value in expected
        else:
            valid = type(value) is expected
            if expected is str:
                valid = (
                    valid
                    and bool(value.strip())
                    and "\n" not in value
                    and "\r" not in value
                )
            elif expected is dict:
                valid = _pre_run_divergence(value)
        if not valid:
            raise ValueError("Invalid assembly fact value: " + name)
    return cast(dict[str, Any], json.loads(json.dumps(obj)))


def facts_values(obj: Mapping[str, Any]) -> dict[str, Any]:
    return {name: fact["value"] for name, fact in obj["facts"].items()}


def merge_facts(owner: object, derived: object) -> dict[str, Any]:
    """Merge partial records, refusing overrides even when their values agree."""
    human, calculated = validate_facts(owner), validate_facts(derived)
    if human["synthetic"] != calculated["synthetic"]:
        raise ValueError("Owner and derived synthetic flags differ")
    left, right = human["facts"], calculated["facts"]
    conflicts = sorted(
        k for k in left.keys() & right.keys() if left[k]["value"] != right[k]["value"]
    )
    if conflicts:
        raise ValueError("Conflicting Owner and derived facts: " + ", ".join(conflicts))
    for name, fact in left.items():
        if name in DERIVABLE_FACTS and not (
            name == "shp.state" and fact["value"] in OWNER_SHP_STATES
        ):
            raise ValueError("Owner cannot supply a derivable fact: " + name)
    for name, fact in right.items():
        if name not in DERIVABLE_FACTS or (
            name == "shp.state" and fact["value"] in OWNER_SHP_STATES
        ):
            raise ValueError("Derivation cannot supply an Owner declaration: " + name)
    return validate_facts(human | {"facts": left | right})


def facts_sha256(obj: Mapping[str, Any]) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()
