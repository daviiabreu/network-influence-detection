"""Render every a*(r) figure and table from the frozen v4 release outputs.

Usage::

    python -m ic_study.analysis.detection_v4_report \\
        [--curves RELEASE.json] --gate-root GATE_DIR [--shp SHP.json] \\
        [--crosswalk CROSSWALK.json] [--criteria criteria-v43.json] \\
        [--allocation v4-allocation.json] [--stage-successor SUCCESSOR.json]... \\
        --out DIR

``RELEASE.json`` is published by ``release_on_completion.py`` alongside
``release-record.json`` (or the explicit ``--release-record`` path); the gate
root is the sealed ``sealed-v4-gate/<id>`` directory, read without writing; the
SHP file is the aggregate report of ``shp_reliability``; the optional crosswalk
is the exploratory aggregate of ``shp_crosswalk``, drawn on F6 only with
``--shp``. The allocation is the post-G0 second binding: it labels the G2 cells
and must bind ``--criteria``. Each stage successor supplies a complete stage
summary that the frozen runner could not append, used only when
``criteria.jsonl`` has no complete line for that stage. ``manifest.json`` in
``DIR`` records the SHA-256 of every input and output and the code commit.

Without ``--curves`` (no release exists because the gate failed, stopped or
did not finish before the close), only the gate outputs T3 and F4 are written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ic_study.analysis.v4_report_figures import Render, figure_gate, render_figures
from ic_study.analysis.v4_report_schema import (
    Allocation,
    Crosswalk,
    GateRecords,
    Release,
    ReleaseRecord,
    ShpAnchor,
    check_criteria_binding,
    load_allocation,
    load_crosswalk,
    load_gate,
    load_release_record,
    load_shp,
    load_thresholds,
    parse_release,
)
from ic_study.analysis.v4_report_tables import (
    Table,
    table_t1,
    table_t1_full,
    table_t3,
    table_t4,
    write_table,
)

MANIFEST_SCHEMA = "ic-study.detection-v4-report-manifest.v1"
REGISTERED = {
    "F1_a_star_by_family": "registered",
    "F2_auc_profiles": "registered",
    "F3_exploratory_family_offsets_vs_B": "exploratory",
    "F4_gate_diagnostics": "registered",
    "F5_inventory_status": "registered",
    "F6_a_star_shp_anchor": (
        "exploratory illustration (SHP preregistration and successor 1)"
    ),
    "T1_a_star_grid": "registered",
    "T1s_a_star_all_units": "registered",
    "T2_contrasts": "not emitted: no registered contrast",
    "T3_gate_summary": "registered",
    "T4_inventory": "registered",
}
_MODULES = (
    "detection_v4_report.py",
    "v4_report_schema.py",
    "v4_report_protocol.py",
    "v4_report_tables.py",
    "v4_report_figures.py",
)


@dataclass(frozen=True)
class Inputs:
    curves: Path | None
    gate_root: Path | None
    shp: Path | None = None
    criteria: Path | None = None
    crosswalk: Path | None = None
    successors: tuple[Path, ...] = ()
    allocation: Path | None = None
    release_record: Path | None = None
    public_aggregates: Path | None = None


@dataclass(frozen=True)
class Loaded:
    """Every input after validation against the frozen schemas."""

    release: Release | None
    gate: GateRecords | None
    allocation: Allocation | None
    shp: ShpAnchor | None
    crosswalk: Crosswalk | None
    thresholds: dict[str, float] | None
    release_record: ReleaseRecord | None = None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_commit() -> dict[str, object]:
    here = Path(__file__).resolve().parent
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=here,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--", str(here)],
            cwd=here,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "reporting_code_dirty": None}
    return {"commit": commit, "reporting_code_dirty": bool(dirty)}


def _gate_inputs(gate: GateRecords, root: Path) -> dict[str, object]:
    listing = "".join(f"{name}\t{digest}\n" for name, digest in gate.task_digests)
    return {
        "identifier": root.resolve().name,
        "criteria.jsonl": gate.criteria_sha256,
        "task_records": len(gate.task_digests),
        "task_records_listing_sha256": hashlib.sha256(listing.encode()).hexdigest(),
    }


def load_inputs(inputs: Inputs, *, synthetic: bool = False) -> Loaded:
    """Validate every input against the frozen schemas before anything is written."""
    if inputs.public_aggregates is not None:
        from ic_study.analysis.v4_public_aggregates import load_public

        if any(
            (
                inputs.curves,
                inputs.gate_root,
                inputs.shp,
                inputs.criteria,
                inputs.crosswalk,
                inputs.successors,
                inputs.allocation,
                inputs.release_record,
            )
        ):
            raise ValueError("Public aggregates exclude all authorized inputs")
        return load_public(inputs.public_aggregates).loaded
    if inputs.curves is None and inputs.gate_root is None:
        raise ValueError("Nothing to report: give the release or the gate root")
    release = None
    receipt = None
    if inputs.curves is not None:
        content = inputs.curves.read_bytes()
        release = parse_release(json.loads(content))
        receipt = load_release_record(
            inputs.release_record or inputs.curves.with_name("release-record.json"),
            content,
            release,
        )
    elif inputs.release_record is not None:
        raise ValueError("A release record needs released curves")
    if inputs.successors and inputs.gate_root is None:
        raise ValueError("A stage successor record needs the gate root")
    allocation = (
        None if inputs.allocation is None else load_allocation(inputs.allocation)
    )
    if allocation is not None and inputs.criteria is not None:
        check_criteria_binding(allocation, inputs.criteria)
    gate = (
        None
        if inputs.gate_root is None
        else load_gate(
            inputs.gate_root,
            successors=inputs.successors,
            allocation=allocation,
            synthetic=synthetic,
        )
    )
    shp = None if inputs.shp is None else load_shp(inputs.shp)
    if inputs.crosswalk is not None and shp is None:
        raise ValueError("The crosswalk overlay needs the SHP report (--shp)")
    if inputs.crosswalk is not None and release is None:
        raise ValueError("The crosswalk overlay needs the release (--curves)")
    crosswalk = None if inputs.crosswalk is None else load_crosswalk(inputs.crosswalk)
    thresholds = None if inputs.criteria is None else load_thresholds(inputs.criteria)
    return Loaded(release, gate, allocation, shp, crosswalk, thresholds, receipt)


def report_tables(loaded: Loaded) -> list[Table]:
    """T1, T1s and T4 from the release and T3 from the gate, whichever exist."""
    release = loaded.release
    tables = (
        []
        if release is None
        else [table_t1(release), table_t1_full(release), table_t4(release)]
    )
    if loaded.gate is not None:
        tables.append(table_t3(loaded.gate, loaded.thresholds))
    return tables


def input_record(inputs: Inputs, loaded: Loaded) -> dict[str, object]:
    """Name and SHA-256 of every input, as the manifest records them."""
    if inputs.public_aggregates is not None:
        from ic_study.analysis.v4_public_aggregates import NOTICE

        return {
            "public_aggregates": {"sha256": sha256(inputs.public_aggregates)},
            "provenance": NOTICE,
        }
    record: dict[str, object] = {}
    if inputs.curves is not None:
        receipt = loaded.release_record
        if receipt is None:
            raise ValueError("Released curves have no validated release record")
        record["curves"] = {"name": inputs.curves.name, "sha256": receipt.curves_sha256}
        record["release_record"] = {
            "name": receipt.name,
            "sha256": receipt.sha256,
            "condition": receipt.condition,
            "released_utc": receipt.released_utc,
        }
    gate = loaded.gate
    if gate is not None and inputs.gate_root is not None:
        record["gate_root"] = _gate_inputs(gate, inputs.gate_root)
        if gate.successors:
            record["stage_successors"] = [
                {
                    "name": item.name,
                    "sha256": item.sha256,
                    "stage": item.stage,
                    "used": item.stage in gate.from_successor,
                }
                for item in gate.successors
            ]
    if loaded.allocation is not None:
        record["allocation"] = {
            "name": loaded.allocation.name,
            "sha256": loaded.allocation.sha256,
        }
    for key, path in (
        ("shp", inputs.shp),
        ("criteria", inputs.criteria),
        ("crosswalk", inputs.crosswalk),
    ):
        if path is not None:
            record[key] = {"name": path.name, "sha256": sha256(path)}
    return record


def render(
    inputs: Inputs,
    out: Path,
    *,
    dpi: int = 300,
    synthetic: bool = False,
    formats: tuple[str, ...] = ("pdf", "png"),
) -> Path:
    """Validate all inputs first, then write figures, tables and the manifest."""
    if inputs.public_aggregates is not None:
        from ic_study.analysis.v4_public_aggregates import load_public

        public = load_public(inputs.public_aggregates)
        if synthetic and not public.synthetic:
            raise ValueError("--synthetic differs from the public projection")
        synthetic = public.synthetic
    loaded = load_inputs(inputs, synthetic=synthetic)
    release, gate = loaded.release, loaded.gate
    out.mkdir(parents=True, exist_ok=True)
    options = Render(out, dpi=dpi, synthetic=synthetic, formats=formats)
    if release is not None:
        outputs = render_figures(
            release,
            gate,
            options,
            shp=loaded.shp,
            thresholds=loaded.thresholds,
            crosswalk=loaded.crosswalk,
        )
    elif gate is not None:
        outputs = figure_gate(gate, options, loaded.thresholds)
    else:
        raise ValueError("Nothing to report: give the release or the gate root")
    for table in report_tables(loaded):
        outputs += write_table(table, out, suffix="_synthetic" if synthetic else "")
    here = Path(__file__).resolve().parent
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "synthetic": synthetic,
        "code": {
            **code_commit(),
            "modules_sha256": {name: sha256(here / name) for name in _MODULES},
        },
        "inputs": input_record(inputs, loaded),
        "outputs": {p.name: sha256(p) for p in sorted(outputs)},
        "classification": REGISTERED,
        "main_curve_valid": None if release is None else release.main_curve_valid,
        "dpi": dpi,
        "formats": list(formats),
    }
    path = out / "manifest.json"
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    """The report inputs; omit ``--curves`` when no release exists."""
    parser.add_argument("--curves", type=Path)
    parser.add_argument("--release-record", type=Path)
    entry = parser.add_mutually_exclusive_group(required=True)
    entry.add_argument("--gate-root", type=Path)
    entry.add_argument("--public-aggregates", type=Path)
    parser.add_argument("--shp", type=Path)
    parser.add_argument("--criteria", type=Path)
    parser.add_argument("--crosswalk", type=Path)
    parser.add_argument("--allocation", type=Path)
    parser.add_argument(
        "--stage-successor", type=Path, action="append", default=[], dest="successors"
    )


def parse_inputs(parser: argparse.ArgumentParser, args: argparse.Namespace) -> Inputs:
    if args.public_aggregates is not None:
        if any(
            (
                args.curves,
                args.shp,
                args.criteria,
                args.crosswalk,
                args.successors,
                args.allocation,
                args.release_record,
            )
        ):
            parser.error("--public-aggregates excludes all authorized inputs")
        return Inputs(None, None, public_aggregates=args.public_aggregates)
    if args.crosswalk is not None and args.shp is None:
        parser.error("--crosswalk needs --shp")
    if args.crosswalk is not None and args.curves is None:
        parser.error("--crosswalk needs --curves")
    return Inputs(
        args.curves,
        args.gate_root,
        args.shp,
        args.criteria,
        args.crosswalk,
        tuple(args.successors),
        args.allocation,
        args.release_record,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_input_arguments(parser)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--synthetic", action="store_true")
    args = parser.parse_args(argv)
    path = render(
        parse_inputs(parser, args), args.out, dpi=args.dpi, synthetic=args.synthetic
    )
    print(f"Report written; manifest {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
