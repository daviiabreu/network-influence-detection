"""Re-audit only the named public synthetic rehearsals, without running models."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from itertools import pairwise
from pathlib import Path
from typing import Any

from ic_study.analysis.detection_v4_report import Loaded
from ic_study.analysis.v4_exploratory_export import export as export_exploratory
from ic_study.analysis.v4_manuscript_assembly import (
    RULES,
    _abstract_span,
    _permitted,
    _visible,
    assemble,
    document_errors,
    load_catalog,
)
from ic_study.analysis.v4_manuscript_assembly_facts import FACTS_SCHEMA, validate_facts
from ic_study.analysis.v4_report_export import (
    gate_values,
    generated_files,
    result_values,
)
from ic_study.analysis.v4_report_schema import (
    GateRecords,
    load_allocation,
    load_crosswalk,
    load_gate,
    load_release_record,
    load_shp,
    load_thresholds,
    parse_release,
)

STUDY = Path(__file__).resolve().parents[4]
BASELINE = "c1371ebe8f84fe11b896b94579981882a3ed62d6"
T41 = "1b9ddddd"
MANUSCRIPT = STUDY / "publications/jcss-manuscript"
FIXTURES = STUDY / "tests/fixtures/v4_manuscript_assembly"
RELEASE = Path("/private/tmp/release-day-combined.ya7qxzen")
G2C = Path("/private/tmp/g2c-failure-rehearsal.6Yk8Sb")
DRESS = Path("/private/tmp/dress-rehearsal.PFgUyQ")
CRITERIA = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
NAMES = [
    row["name"]
    for row in json.loads((FIXTURES / "manual_oracles.json").read_text())["cases"]
]
VISIBLE_IDS = set(
    json.loads(
        (
            MANUSCRIPT / "pipeline/review/t41e-shell-repin-receipt-verified.json"
        ).read_text()
    )["accepted_visible_ids"]
)


def digest(path: Path) -> str:
    return hashlib.sha256(_permitted(path).read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(_permitted(path).read_text())


def write(path: Path, obj: Any) -> None:
    path = _permitted(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    )


def input_paths(case: Path) -> dict[str, Path]:
    record = case / "input-arguments.json"
    if record.exists():
        args = read(record)["a"]
    elif (case / "a-arguments.json").exists():
        args = read(case / "a-arguments.json")
    else:
        return {
            "gate-root": case / "gate",
            **(
                {"stage-successor": case / "G1c-successor.json"}
                if (case / "G1c-successor.json").exists()
                else {}
            ),
        }
    return {
        args[i].removeprefix("--"): _permitted(Path(args[i + 1]))
        for i in range(0, len(args), 2)
    }


def gate_records(case: Path) -> tuple[GateRecords, dict[str, str]]:
    paths = input_paths(case)
    path = paths["gate-root"] / "criteria.jsonl"
    sources = {str(path): digest(path)}
    successors = (paths["stage-successor"],) if "stage-successor" in paths else ()
    allocation = load_allocation(paths["allocation"]) if "allocation" in paths else None
    for source in [*successors, *([paths["allocation"]] if allocation else [])]:
        sources[str(source)] = digest(source)
    gate = load_gate(
        _permitted(paths["gate-root"]),
        successors=successors,
        allocation=allocation,
        synthetic=True,
    )
    return gate, sources


def owner_facts(case: Path, gate: GateRecords) -> dict[str, Any]:
    note = case / "assembly-notes.txt"
    source = {
        "record": str(note),
        "locator": "explicit artificial rehearsal assumption",
        "sha256": digest(note),
    }
    facts: dict[str, Any] = {}

    def add(name: str, value: Any, origin: dict[str, str] | None = None) -> None:
        facts[name] = {"value": value, "source": origin or source}

    has_anchor = any(
        k.startswith("v4.shp.estimate") for k in load_catalog(case / "a-catalog.json")
    )
    add("shp.state", "admissible" if has_anchor else "not-run")
    if has_anchor:
        add("shp.grid_position", "inside")
    else:
        add("shp.reason", "this artificial gate-only case includes no SHP run")
    # These are explicit synthetic facts, not claims about the sealed study.
    add("gate.at_close", True)
    comparison = case / "aggregates/comparisons.json"
    if comparison.exists():
        aggregate = read(comparison)
        states = [row.get("x5_state", {}) for row in aggregate["by_r"].values()]
        supplied = "x5" in aggregate.get("provenance", {}).get("inputs", {})
        assert supplied or all(
            state == {"state": "indisponível", "reason": "agregado X5 não fornecido"}
            for state in states
        )
        add(
            "post.x5_supplied",
            supplied,
            {
                "record": str(comparison),
                "locator": "artificial provenance.inputs.x5 and every by_r.x5_state",
                "sha256": digest(comparison),
            },
        )
    paths = input_paths(case)
    if "curves" in paths:
        path = paths["curves"]
        release = parse_release(read(path))
        origin = {
            "record": str(path),
            "locator": (
                "VALID tier-2 boundary tuples and ordered VALID tier-1 "
                "first/censoring tuples (Results lines 412-417, 430-434)"
            ),
            "sha256": digest(path),
        }
        different = any(
            (
                c.first.point,
                c.first.interval,
                c.first.censoring,
                c.first.interval_censoring,
            )
            != (
                c.sustained.point,
                c.sustained.interval,
                c.sustained.censoring,
                c.sustained.interval_censoring,
            )
            for c in release.curves.values()
            if c.meta.tier == 2 and c.status == "completo válido"
        )
        ordered = []
        from ic_study.simulation.detection_v4 import GRID

        for c in sorted(release.curves.values(), key=lambda c: c.meta.r):
            if c.meta.tier != 1 or c.status != "completo válido":
                continue
            if c.first.point is not None:
                ordered.append(GRID.index(c.first.point))
            elif c.first.censoring is None:
                ordered.append(9)
        monotone = all(a <= b for a, b in pairwise(ordered)) or all(
            a >= b for a, b in pairwise(ordered)
        )
        add("tier2.boundaries_differ", different, origin)
        add("main.boundary_nonmonotone", not monotone, origin)
    if gate.verdict("G0") == "fail" and "fits" in gate.summaries["G0"]:
        summary = gate.summaries["G0"]
        failed = [
            k
            for k, yes in (
                ("anchor", summary["anchor_failures"] > 0),
                ("budget", summary["budget_statuses"] > 0),
                (
                    "implementation",
                    summary["implementation_statuses"] > summary["fits"] * 0.01,
                ),
            )
            if yes
        ]
        add(
            "gate.G0.failed_criteria",
            failed,
            {
                "record": str(input_paths(case)["gate-root"] / "criteria.jsonl"),
                "locator": "G0 complete summary; exact failed clauses",
                "sha256": digest(input_paths(case)["gate-root"] / "criteria.jsonl"),
            },
        )
    if gate.verdict("G2c") == "fail":
        comparisons = gate.summaries["G2c"].get("comparisons", [])
        if len(comparisons) == 2 and all("ratio" in c for c in comparisons):
            add(
                "gate.G2c.failed_comparisons",
                [
                    k
                    for k, c in zip(("a010", "a003"), comparisons, strict=True)
                    if not c["pass"]
                ],
                {
                    "record": str(input_paths(case)["gate-root"] / "criteria.jsonl"),
                    "locator": "G2c complete summary; comparison pass flags",
                    "sha256": digest(input_paths(case)["gate-root"] / "criteria.jsonl"),
                },
            )
    return validate_facts({"schema": FACTS_SCHEMA, "synthetic": True, "facts": facts})


def legacy_exporter(output: Path) -> Any:
    relative = "studies/ic-2026-2027/src/ic_study/analysis/v4_report_export.py"
    source = subprocess.run(
        ["git", "show", BASELINE + ":" + relative],
        cwd=STUDY,
        capture_output=True,
        check=True,
    ).stdout
    path = output / "legacy_v4_report_export.py"
    path.write_bytes(source)
    spec = importlib.util.spec_from_file_location("assembly_legacy_exporter", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def normalized(text: str) -> str:
    return " ".join(_visible(text).split())


def change_reason(block: str) -> str:
    if block in VISIBLE_IDS:
        return (
            "T41e resolve substantivos, verbos e pronomes pelo inteiro vinculado "
            "no mesmo bloco; preserva afirmação, força, bindings, marcadores, "
            "condição, ação e ordem da T41d."
        )
    reasons = {
        "P1.1": "P4: roteiro F1/F2B/T1 após validação; ordem dos displays mantida.",
        "B05": "F02: queda pontual e extremos da banda têm guards separados.",
        "B11": "X6R-05/F01: não avaliação não autoriza inferência sobre canal.",
        "C-H-B": "P9: implicação de fronteira atingida exige contagem positiva.",
        "C-H-BD": "P9: implicação de fronteira conserva o guard do conjunto B/D.",
        "C-B02": "P9: ausência de resposta validada é distinta de fronteiras locais.",
        "C-B03": "P9: limite do resumo e da grade não é indistinguibilidade.",
        "C-BD-PERSISTENCE": "P9: implicação conserva o critério registrado B10.",
        "C-EVALUATION-PASS": "X6R-07/F05: exposição parcial é conservada em CN01.",
        "D-X1B": "F04: fonte arquivada e projeção fornecida são distinguidas.",
        "E.twin-and-expanded-feature-boundaries": (
            "F04: síntese conserva todos os r e estados da fonte fornecida."
        ),
        "E.tables": "X6R-06/F03: X7 fica completo e único em main.tex.",
        "D-X6-DENOMINATORS": "X6R-02: gaps-as-misses conserva o numerador.",
    }
    if block.startswith("E.x6-"):
        return (
            "X6R-02: contagens e leituras marginais do sucessor sintético respeitam "
            "a interseção conjunta; a leitura primária registrada permanece igual."
        )
    return reasons.get(
        block, "Fragmento literal e slot do shell atual, sem alteração de guard."
    )


def run() -> None:
    output = Path(
        tempfile.mkdtemp(prefix="v4-shell-assembly-audit-", dir="/private/tmp")
    )
    old = legacy_exporter(output)
    successor_spec = importlib.util.spec_from_file_location(
        "assembly_synthetic_successors",
        Path(__file__).with_name("t41c_synthetic_successors.py"),
    )
    assert successor_spec is not None and successor_spec.loader is not None
    successors = importlib.util.module_from_spec(successor_spec)
    successor_spec.loader.exec_module(successors)
    registry = read(RULES)
    legacy_rules = json.loads(
        subprocess.run(
            [
                "git",
                "show",
                BASELINE
                + ":studies/ic-2026-2027/src/ic_study/analysis/"
                + "v4_manuscript_assembly_rules.json",
            ],
            cwd=STUDY,
            capture_output=True,
            check=True,
        ).stdout
    )

    assert {row["id"] for row in legacy_rules["rules"]} < {
        row["id"] for row in registry["rules"]
    }
    prior = json.loads(
        subprocess.run(
            [
                "git",
                "show",
                T41
                + ":studies/ic-2026-2027/publications/jcss-manuscript/pipeline/"
                + "review/v4-manuscript-assembly-audit-2026-09-30.json",
            ],
            cwd=STUDY,
            check=True,
            capture_output=True,
        ).stdout
    )
    sources = {
        name: (MANUSCRIPT / name).read_text()
        for name in (
            "main.tex",
            "sections/discussion.tex",
            "sections/conclusion.tex",
            "sections/supplement.tex",
        )
    }
    old_fixed = {
        filename: subprocess.run(
            [
                "git",
                "show",
                T41 + ":studies/ic-2026-2027/publications/jcss-manuscript/" + filename,
            ],
            cwd=STUDY,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        for filename in (
            "main.tex",
            "sections/discussion.tex",
            "sections/conclusion.tex",
        )
    }
    old_start, old_end = _abstract_span(old_fixed["main.tex"])
    base_start, base_end = _abstract_span(sources["main.tex"])
    base_abstract_changed = normalized(old_fixed["main.tex"][old_start:old_end]) != (
        normalized(sources["main.tex"][base_start:base_end])
    )
    cases: list[dict[str, Any]] = []
    proofs: list[dict[str, Any]] = []
    divergences: list[dict[str, Any]] = []
    fixture_verdicts: dict[str, Any] = {}
    current_oracles = json.loads(
        subprocess.run(
            [
                "git",
                "show",
                T41 + ":studies/ic-2026-2027/tests/fixtures/"
                "v4_manuscript_assembly/current_shell_oracles.json",
            ],
            cwd=STUDY,
            capture_output=True,
            check=True,
        ).stdout
    )
    successor_receipts = []
    for dataset, root, names in (
        ("release-day", RELEASE, [n for n in NAMES if "comparison" not in n]),
        ("g2c-failure", G2C, [n for n in NAMES if "comparison" in n]),
        ("dress", DRESS, NAMES),
    ):
        for name in names:
            case = _permitted(root / name)
            gate, gate_sources = gate_records(case)
            added = {
                k: v
                for k, v in gate_values(gate, load_thresholds(CRITERIA)).items()
                if ".verdict." in k
            }
            facts = owner_facts(case, gate)
            fact_path = FIXTURES / dataset / name / "assembly-facts.json"
            write(fact_path, facts)
            if dataset != "dress":
                fixture_verdicts[name] = {"sources": gate_sources, "values": added}
            catalog_path = case / (
                "catalog.json" if (case / "catalog.json").exists() else "a-catalog.json"
            )
            values = load_catalog(catalog_path)
            confirmatory = load_catalog(case / "a-catalog.json")
            paths = input_paths(case)
            release_path = paths.get("curves")
            release = parse_release(read(release_path)) if release_path else None
            anchor = load_shp(paths["shp"]) if "shp" in paths else None
            crosswalk = (
                load_crosswalk(paths["crosswalk"]) if "crosswalk" in paths else None
            )
            receipt = (
                load_release_record(
                    paths["release-record"], release_path.read_bytes(), release
                )
                if release is not None and release_path
                else None
            )
            loaded = Loaded(
                release,
                gate,
                None,
                anchor,
                crosswalk,
                load_thresholds(CRITERIA),
                receipt,
            )
            _, cells = generated_files(loaded, lambda stem: stem + ".pdf", True)
            before = old.result_values(loaded) | cells
            after = result_values(loaded) | cells
            projected = {k: v for k, v in after.items() if k not in added}

            def encoded(obj: Any) -> bytes:
                return (
                    json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
                ).encode()

            assert before == projected
            # Existing recorded values are checked as well as the HEAD baseline.
            assert confirmatory == before, sorted(
                k
                for k in confirmatory.keys() | before.keys()
                if confirmatory.get(k) != before.get(k)
            )
            assert encoded(before) == encoded(projected)
            proofs.append(
                {
                    "dataset": dataset,
                    "case": name,
                    "old_ids": len(before),
                    "added_ids": len(added),
                    "recorded_catalog_sha256": digest(case / "a-catalog.json"),
                    "old_values_sha256": hashlib.sha256(encoded(before)).hexdigest(),
                    "projected_values_sha256": hashlib.sha256(
                        encoded(projected)
                    ).hexdigest(),
                    "bytes_equal": True,
                    "metadata_note": (
                        "Code provenance is regenerated truthfully; this equality "
                        "concerns every pre-existing value ID."
                    ),
                }
            )
            target = output / dataset / name
            source_copy = output / "sources" / dataset / name
            shutil.copytree(MANUSCRIPT, source_copy)
            shutil.copytree(
                _permitted(case / "manuscript/generated"),
                source_copy / "generated",
                dirs_exist_ok=True,
            )
            successor_inputs, successor_receipt = successors.corrected_inputs(
                case, output / "inputs" / dataset / name
            )
            successor_receipt["missing_from_original_export"] = [
                {"name": path.name, "template_sha256": digest(path)}
                for path in sorted((MANUSCRIPT / "generated").glob("*.tex"))
                if not (case / "manuscript/generated" / path.name).exists()
            ]
            if successor_inputs:
                original_values = values
                exported = export_exploratory(successor_inputs, source_copy)
                values = confirmatory | exported.catalog
                successor_receipt["catalog_changes"] = [
                    {
                        "id": key,
                        "before": original_values.get(key),
                        "after": values.get(key),
                    }
                    for key in sorted(original_values.keys() | values.keys())
                    if original_values.get(key) != values.get(key)
                ]
                assert all(
                    change["id"].startswith("v4x.")
                    for change in successor_receipt["catalog_changes"]
                )
            successor_receipt["original_document_errors"] = document_errors(
                case / "manuscript", {}
            )
            successor_receipts.append(successor_receipt)
            report = assemble(
                values | added,
                {},
                manuscript=source_copy,
                output=target,
                facts=facts,
                values_output=target / "assembled-values.json",
                catalog_records=[read(catalog_path)],
            )
            assembled = {key: (target / key).read_text() for key in sources}
            start, end = _abstract_span(assembled["main.tex"])
            if dataset != "dress":
                current_oracles["abstracts"][name] = assembled["main.tex"][start:end]
                current_oracles["catalog_additions"][name]["values"].update(
                    {
                        change["id"]: change["after"]
                        for change in successor_receipt.get("catalog_changes", [])
                        if change["after"] is not None
                    }
                )
                x1b_required = next(
                    row["requires"]
                    for row in registry["rules"]
                    if row["id"] == "E.twin-and-expanded-feature-boundaries"
                )
                current_oracles["catalog_additions"][name]["values"].update(
                    {key: values[key] for key in x1b_required if key in values}
                )
            words = read(target / "assembly-record.json")["abstract_words"]
            manual = {
                key: _permitted(case / "manuscript" / key).read_text()
                for key in sources
            }
            for extra in (
                "sections/exploratory-rehearsal.tex",
                "sections/supplement-exploratory-x3-x7.tex",
            ):
                path = _permitted(case / "manuscript" / extra)
                if path.exists():
                    manual[extra] = path.read_text()
            ms, me = _abstract_span(manual["main.tex"])
            diff_start = len(divergences)
            for decision in report.decisions.values():
                if (
                    decision.state != "selected"
                    or not decision.text
                    or decision.slot == "abstract"
                ):
                    continue
                filename = (
                    "sections/results.tex"
                    if decision.slot.startswith(("P", "gate"))
                    else "sections/discussion.tex"
                    if decision.slot.startswith("DS")
                    else "sections/conclusion.tex"
                    if decision.slot.startswith("C")
                    else "sections/supplement-exploratory-x3-x7.tex"
                    if decision.slot == "exploratory"
                    else "sections/supplement.tex"
                )
                if decision.slot == "exploratory":
                    oracle = "\n".join(
                        text
                        for path, text in manual.items()
                        if path.startswith("sections/")
                        and ("exploratory" in path or path == "sections/supplement.tex")
                    )
                else:
                    oracle = manual.get(
                        filename,
                        (case / "manuscript" / filename).read_text()
                        if (case / "manuscript" / filename).exists()
                        else "",
                    )
                expected_text = decision.text
                if (
                    decision.id in {"P5-b.range", "P5-b.single"}
                    and report.decisions["B06"].state == "selected"
                ):
                    expected_text = re.sub(
                        r", and at every value.*?equalled it\.", ".", expected_text
                    )
                if any(
                    normalized(line) not in normalized(oracle)
                    for line in expected_text.splitlines()
                    if line.strip()
                ):
                    divergences.append(
                        {
                            "dataset": dataset,
                            "case": name,
                            "kind": "selected-shell-fragment-missing-or-paraphrased",
                            "block": decision.id,
                            "source": decision.source,
                            "line": decision.line,
                            "end_line": decision.end_line,
                            "follows_rules": "assembler",
                            "condition": next(
                                r["condition"]
                                for r in registry["rules"]
                                if r["id"] == decision.id
                            ),
                            "assessment": (
                                change_reason(decision.id)
                                + " O montador preserva o fragmento literal e o slot; "
                                "a montagem "
                                "manual omite, intercala ou parafraseia o bloco. "
                                "Divergência de "
                                "composição, sem presumir incompatibilidade "
                                "científica de toda "
                                "paráfrase."
                            ),
                            "expected_sha256": hashlib.sha256(
                                decision.text.encode()
                            ).hexdigest(),
                        }
                    )
            if normalized(assembled["main.tex"][start:end]) != normalized(
                manual["main.tex"][ms:me]
            ):
                record = read(target / "assembly-record.json")
                divergences.append(
                    {
                        "dataset": dataset,
                        "case": name,
                        "kind": "abstract-first-fit",
                        "source": registry["sources"]["abstract"]["path"],
                        "line": 13,
                        "end_line": 111,
                        "follows_rules": "assembler",
                        "assessment": (
                            "T41e resolve a concordância antes do orçamento; conserva "
                            "a composição, os fallbacks, as condições e a ordem da "
                            "T41d. O ensaio histórico mantém outra redação e "
                            "composição, inclusive plurais fixos para contagem 1."
                        ),
                        "first_fit": record["abstract_first_fit"],
                        "fixed_text_changed": base_abstract_changed,
                    }
                )
            if report.decisions["B1a"].state == "selected":

                def main_inputs(text: str) -> list[str]:
                    return re.findall(r"\\input\{generated/([^{}]+)\}", text)

                expected_inputs = main_inputs(
                    (target / "sections/results.tex").read_text()
                )
                manual_inputs = main_inputs(
                    (case / "manuscript/sections/results.tex").read_text()
                )
                if expected_inputs != manual_inputs:
                    divergences.append(
                        {
                            "dataset": dataset,
                            "case": name,
                            "kind": "results-display-order",
                            "block": "B00",
                            "source": registry["sources"]["results"]["path"],
                            "line": 642,
                            "end_line": 647,
                            "follows_rules": "assembler",
                            "expected": expected_inputs,
                            "manual": manual_inputs,
                            "assessment": (
                                "T38b exige F1/F2B/T1 antes de T4/F5 e T3/F4; "
                                "o ensaio histórico conserva a ordem anterior. "
                                "P1-P10 mantêm sua ordem textual."
                            ),
                        }
                    )
            fixed_lines = sources["sections/discussion.tex"].splitlines()
            markers = [
                (i, match[1])
                for i, line in enumerate(fixed_lines)
                if (match := re.match(r"% (DS\d\d)\b", line))
            ]
            for j, (i, marker) in enumerate(markers):
                end_fixed = (
                    markers[j + 1][0] if j + 1 < len(markers) else len(fixed_lines)
                )
                fixed = normalized("\n".join(fixed_lines[i:end_fixed]))
                if fixed and fixed not in normalized(manual["sections/discussion.tex"]):
                    divergences.append(
                        {
                            "dataset": dataset,
                            "case": name,
                            "kind": "fixed-discussion-changed",
                            "source": registry["sources"]["discussion"]["path"],
                            "line": 24,
                            "end_line": 42,
                            "fixed_source": "sections/discussion.tex",
                            "fixed_marker": marker,
                            "fixed_line": i + 1,
                            "fixed_text_changed": fixed
                            != normalized(
                                re.split(
                                    r"(?m)^% DS\d\d\b[^\n]*\n",
                                    old_fixed["sections/discussion.tex"],
                                )[j + 1]
                            ),
                            "follows_rules": "assembler",
                            "assessment": (
                                "As instruções do shell exigem reter todas as "
                                "sentenças fixas; a "
                                "montagem manual altera ou remove esse trecho."
                            ),
                        }
                    )
            fixed_conclusion = re.split(
                r"\[(?:Insert|State whether)[^]]*\]",
                _visible(sources["sections/conclusion.tex"]),
            )
            if any(
                normalized(part)
                and normalized(part)
                not in normalized(manual["sections/conclusion.tex"])
                for part in fixed_conclusion
            ):
                divergences.append(
                    {
                        "dataset": dataset,
                        "case": name,
                        "kind": "fixed-conclusion-changed",
                        "source": registry["sources"]["discussion"]["path"],
                        "line": 24,
                        "end_line": 42,
                        "follows_rules": "assembler",
                        "fixed_text_changed": normalized(
                            old_fixed["sections/conclusion.tex"]
                        )
                        != normalized(sources["sections/conclusion.tex"]),
                        "assessment": (
                            "O shell permite substituir apenas os três marcadores "
                            "CN01 e "
                            "exige reter as sentenças fixas, inclusive X5; o oráculo "
                            "altera "
                            "texto fixo."
                        ),
                    }
                )
            cases.append(
                {
                    "dataset": dataset,
                    "case": name,
                    "status": report.as_dict()["status"],
                    "counts": report.as_dict()["counts"],
                    "facts": str(fact_path.relative_to(STUDY)),
                    "facts_sha256": digest(fact_path),
                    "gate_sources": gate_sources,
                    "catalog_sha256": digest(catalog_path),
                    "manual_source_sha256": {
                        k: digest(case / "manuscript" / k) for k in manual
                    }
                    | {
                        "sections/results.tex": digest(
                            case / "manuscript/sections/results.tex"
                        )
                    },
                    "manual_sources_unchanged": True,
                    "assembly_record": str(target / "assembly-record.json"),
                    "abstract_words": words,
                    "synthetic_successor": successor_receipt,
                    "divergences": len(divergences) - diff_start,
                }
            )
    write(FIXTURES / "verdicts.json", {"synthetic": True, "cases": fixture_verdicts})
    current_oracles["baseline"] = T41
    current_oracles["change"] = (
        "T41e: bound integer agreement; T41d selection, order and claims and "
        "historical oracle preserved"
    )
    write(FIXTURES / "current_shell_oracles.json", current_oracles)
    write(
        MANUSCRIPT / "pipeline/review/t41e-synthetic-successors.json",
        successor_receipts,
    )
    old_audit = (
        MANUSCRIPT / "pipeline/review/v4-manuscript-assembly-audit-2026-09-30.json"
    )
    prior_coverage = prior.get("coverage_before", prior["coverage"])
    by_source = [
        {
            "source": s["path"],
            "entries": sum(r["source"] == name for r in registry["rules"]),
            "fully_expressible_conditions": sum(
                r["source"] == name for r in registry["rules"]
            ),
            "conditions_with_unsupported_dependency": 0,
        }
        for name, s in registry["sources"].items()
    ]
    coverage = {
        "entries": len(registry["rules"]),
        "fully_expressible_conditions": len(registry["rules"]),
        "conditions_with_unsupported_dependency": 0,
        "by_source": by_source,
    }
    assert "unsupported" not in json.dumps(registry)
    divergence_count = len(divergences)
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for divergence in divergences:
        key = divergence["dataset"], divergence["case"], divergence["kind"]
        if key not in groups:
            groups[key] = {
                field: divergence[field]
                for field in ("dataset", "case", "kind", "follows_rules", "assessment")
            } | {"observations": []}
        groups[key]["observations"].append(
            {
                field: value
                for field, value in divergence.items()
                if field not in groups[key] and field != "condition"
            }
        )

    def observation_key(row: dict[str, Any]) -> tuple[str, ...]:
        return (
            row["dataset"],
            row["case"],
            row["kind"],
            row.get("block", row.get("fixed_marker", "")),
        )

    previous = {
        observation_key(group | observation): {
            k: v for k, v in group.items() if k != "observations"
        }
        | observation
        for group in prior["divergences"]
        for observation in group["observations"]
    }
    current = {observation_key(row): row for row in divergences}
    changes = []
    for audit_key in sorted(previous.keys() | current.keys()):
        prev_observation, new_observation = (
            previous.get(audit_key),
            current.get(audit_key),
        )
        if (
            prev_observation is None
            or new_observation is None
            or prev_observation.get("expected_sha256")
            != new_observation.get("expected_sha256")
            or new_observation.get("fixed_text_changed")
        ):
            changes.append(
                {
                    "dataset": audit_key[0],
                    "case": audit_key[1],
                    "kind": audit_key[2],
                    "block": audit_key[3],
                    "change": "new"
                    if prev_observation is None
                    else "disappeared"
                    if new_observation is None
                    else "changed-text",
                    "explanation": new_observation["assessment"]
                    if new_observation
                    else (
                        "T41e passa a coincidir com a montagem histórica neste "
                        "fragmento; a redação revisada conserva guard, ação e "
                        "bindings, e as correções T41c permanecem."
                    ),
                    "follows_rules": "assembler",
                    "before": prev_observation,
                    "after": new_observation,
                }
            )
    write(
        old_audit,
        {
            "schema": "ic-study.v4-manuscript-assembly-audit.v2",
            "baseline_commit": BASELINE,
            "original_rule_ids_preserved": True,
            "new_rule_ids": [
                "C-EVALUATION-PASS",
                "D-X5-POST-UNAVAILABLE",
                "C-EVALUATION-REQUIRED",
            ],
            "repin_receipt": "pipeline/review/t41e-shell-repin-receipt-verified.json",
            "prior_audit_commit": T41,
            "prior_divergence_count": prior["divergence_count"],
            "divergence_changes": changes,
            "divergence_summary": {
                kind: sum(row["kind"] == kind for row in divergences)
                for kind in sorted({row["kind"] for row in divergences})
            },
            "shells_unchanged": False,
            "shell_change_scope": (
                "T41e grammatical number agreement; main.tex only gains the "
                "plural-default macro in the preamble"
            ),
            "selection_changes": "pipeline/review/t41e-selection-changes.json",
            "synthetic_successors": "pipeline/review/t41e-synthetic-successors.json",
            "auditor_sha256": digest(Path(__file__)),
            "synthetic": True,
            "scientific_acceptance": False,
            "scope": (
                "Somente os três ensaios públicos sintéticos nomeados; sem "
                "execução científica ou abertura de selo."
            ),
            "coverage_before": prior_coverage,
            "coverage_at_t41": prior["coverage"],
            "coverage": coverage,
            "rules_sha256": digest(RULES),
            "implementation_sha256": digest(
                STUDY / "src/ic_study/analysis/v4_manuscript_assembly.py"
            ),
            "facts_validator_sha256": digest(
                STUDY / "src/ic_study/analysis/v4_manuscript_assembly_facts.py"
            ),
            "oracle_fixture_sha256": digest(FIXTURES / "manual_oracles.json"),
            "catalog_equality": proofs,
            "cases": cases,
            "divergence_count": divergence_count,
            "divergences": list(groups.values()),
            "gates": [],
            "output": str(output),
        },
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "complete": len(cases),
                "divergences": divergence_count,
                "catalogs_equal": len(proofs),
            }
        )
    )


if __name__ == "__main__":
    run()
