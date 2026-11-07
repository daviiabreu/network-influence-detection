"""Check abstract predicate classes and maximal lists, without study execution."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any

from ic_study.analysis.v4_manuscript_assembly import (
    RESULT,
    RULES,
    _Evaluator,
    _fragment_text,
    bind,
    first_fit,
    shell_texts,
    visible_word_count,
)
from ic_study.analysis.v4_report_export import grid_runs
from ic_study.simulation.detection_v4 import RELIABILITIES

STUDY = Path(__file__).resolve().parents[4]
MANUSCRIPT = STUDY / "publications/jcss-manuscript"
# The longest r list the exporter can write: grid_runs over every subset.
SHARES = max(
    (
        grid_runs(subset)
        for size in range(1, len(RELIABILITIES) + 1)
        for subset in itertools.combinations(RELIABILITIES, size)
    ),
    key=visible_word_count,
)
GATE_BRANCHES = ("B1b-G0", "B1b-G1b", "B1b-G1c", "B1c", "B1b-G2", "B1b-G2c", "B1d")


def budget_rows(texts: dict[str, str], *, count: str = "9") -> list[dict[str, Any]]:
    registry = json.loads(RULES.read_text())
    rows = [row for row in registry["rules"] if row["slot"] == "abstract"]
    sources = {
        name: (MANUSCRIPT / source["path"]).read_text().splitlines()
        for name, source in registry["sources"].items()
    }
    base = json.loads(
        (
            STUDY / "tests/fixtures/v4_manuscript_assembly/manual_oracles.json"
        ).read_text()
    )["base_values"]
    values = {
        key: base.get(key, shown) if key.startswith("v4.protocol.") else count
        for text in texts.values()
        for key, shown in RESULT.findall(text)
    }
    values["v4.bd.r_eligible"] = SHARES
    values["v4.gate.stop.pass_probability"] = "0.01"
    values["v4.gate.stop.minimum"] = "0.80"
    contexts = []
    for (
        invalid,
        permission,
        nonattainment,
        eligible,
        persistence,
        differs,
        x6,
    ) in itertools.product((False, True), repeat=7):
        if invalid and (permission or nonattainment):
            continue
        if persistence and (not permission or not eligible or nonattainment):
            continue
        for boundary_category in (None, "small", "large", "not_attained", "censored"):
            contexts.append(
                (
                    "B1a",
                    invalid,
                    permission,
                    nonattainment,
                    eligible,
                    persistence,
                    differs,
                    x6,
                    boundary_category,
                )
            )
    contexts.extend(
        (branch, False, False, False, False, False, False, x6, None)
        for branch in GATE_BRANCHES
        for x6 in (False, True)
    )
    found: dict[tuple[tuple[str, ...], str | None, bool], dict[str, Any]] = {}
    for (
        branch,
        invalid,
        permission,
        nonattainment,
        eligible,
        persistence,
        differs,
        x6,
        boundary_category,
    ) in contexts:
        data = values | {
            "v4.bd.n_eligible": (count if count != "0" else "1") if eligible else "0",
            "v4.bd.n_persistence": (count if count != "0" else "1")
            if persistence
            else "0",
            "v4.t1.n_first_ne_sustained": (count if count != "0" else "1")
            if differs
            else "0",
            "v4x.x6.x6a.band.vs_d1.primary.reading": "failure" if x6 else "adequate",
        }
        if boundary_category is not None:
            data.update(
                {
                    "v4.t1.n_" + category: (count if count != "0" else "1")
                    if category == boundary_category
                    else "0"
                    for category in ("small", "large", "not_attained", "censored")
                }
            )
        predicates = {
            "PASS": branch == "B1a",
            "MAIN-INVALID": invalid,
            "M": permission,
            "NONATTAINMENT": nonattainment,
            "B06": branch == "B1a" and differs,
            **{name: name == branch for name in GATE_BRANCHES},
        }
        evaluator = _Evaluator(data, predicates, {})
        chosen = sorted(
            (
                row
                for row in rows
                if not row["optional"]
                and evaluator.evaluate(row["condition"]).value is True
            ),
            key=lambda row: (row["order"], row["id"]),
        )
        ids = tuple(row["id"] for row in chosen)
        mandatory = [
            bind(
                _fragment_text(
                    row, sources[row["source"]], evaluator, texts[row["id"]]
                ),
                data,
            )
            for row in chosen
        ]
        found[(ids, boundary_category, invalid)] = {
            "main_invalid": invalid,
            "ids": ids,
            "boundary_category": boundary_category,
            "mandatory_words": visible_word_count(" ".join(mandatory)),
        }
    return list(found.values())


def proof() -> dict[str, Any]:
    texts = shell_texts(manuscript=MANUSCRIPT)
    full = texts.copy()
    # T57c replaced the elliptical H-BD ending, the first authorized fallback,
    # with a paired labelled form, so only the later fallbacks remain.
    full["A.B10"] = full["A.B10"].replace(
        ", compatible with", ", a pattern compatible with"
    )
    full["A.X6"] = full["A.X6"].replace(
        "below-nominal interior coverage.",
        "below-nominal interior coverage of the AUC bands.",
    )
    full["A.design"] = full["A.design"].replace(
        "Small and large denote interval-based regions divided at 0.03.",
        "Boundaries are small or large when their interval lies "
        "at or below 0.03 or above it.",
    )
    steps = [
        {
            "fallback": None,
            "maximum": max(row["mandatory_words"] for row in budget_rows(full)),
        }
    ]
    for key in ("A.B10", "A.X6", "A.design"):
        full[key] = texts[key]
        steps.append(
            {
                "fallback": key,
                "maximum": max(row["mandatory_words"] for row in budget_rows(full)),
            }
        )
    rows = budget_rows(texts)
    agreement_cases = []
    for count in ("0", "1", "2", "9"):
        variants = budget_rows(texts, count=count)
        maximum = max(row["mandatory_words"] for row in variants)
        if maximum > 250:
            raise ValueError(f"Mandatory agreement variant exceeds 250: {count}")
        agreement_cases.append(
            {
                "count": count,
                "compositions": len(variants),
                "maximum_mandatory_words": maximum,
                "positive_guard_counts": count if count != "0" else "1",
            }
        )
    for row in rows:
        if row["mandatory_words"] > 250:
            raise ValueError(f"Mandatory abstract exceeds 250: {row}")
    optional = {
        key: RESULT.sub(lambda match: "9", texts[key])
        for key in texts
        if key.startswith("A.B")
        and key
        in (
            "A.B09.1",
            "A.B09.2",
            "A.B09.3",
            "A.B04",
            "A.B05",
            "A.B08",
            "A.B11",
            "A.B14",
        )
    }
    for row in rows:
        mandatory = ["word " * (row["mandatory_words"] - 1), "Limitation."]
        row["first_fit_words_with_all_optional_candidates"] = first_fit(
            mandatory, optional
        ).words
    return {
        "schema": "ic-study.v4-abstract-budget-review.v1",
        "synthetic": True,
        "agreement_count_cases": agreement_cases,
        "method": (
            "Finite predicate enumeration; longest grid-run r list; "
            "one-token counts. No study execution."
        ),
        "constraints": [
            "Global permission excludes an invalid main curve.",
            "All-N boundary forms require a valid main curve; "
            "invalid-main classes retain the list form.",
            "Complete valid B non-attainment excludes main invalidity "
            "and positive B/D persistence reading.",
            "Positive persistence reading requires permission "
            "and a nonempty common gap-free set.",
            "First/sustained records may differ only in intervals even without "
            "point attainment; this class is included.",
            "X6 consequence is checked both with and without gate passage, "
            "as its existing condition permits.",
            "All optional eligibility subsets are bounded by first-fit; "
            "no subset can exceed 250.",
        ],
        "fallbacks_in_order": steps,
        "opening_words": visible_word_count(texts["A.design"]),
        "compositions": rows,
        "maximum_mandatory_words": max(row["mandatory_words"] for row in rows),
    }


if __name__ == "__main__":
    payload = proof()
    Path(__file__).with_name("t58-abstract-budget.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                "compositions": len(payload["compositions"]),
                "maximum": payload["maximum_mandatory_words"],
                "fallbacks": payload["fallbacks_in_order"],
            }
        )
    )
