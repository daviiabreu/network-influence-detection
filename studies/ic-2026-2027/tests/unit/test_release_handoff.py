"""Release-day handoff tooling over an artificial chain state; never real roots."""

from __future__ import annotations

import hashlib
import json
import os
import runpy
import shutil
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from ic_study.analysis.v4_manuscript_assembly_facts import validate_facts
from ic_study.simulation.detection_v4 import RELIABILITIES

STUDY = Path(__file__).resolve().parents[2]
TOOL = runpy.run_path(
    str(
        STUDY
        / "experiments/exploratory/detection-boundary-v4/report/release_handoff.py"
    )
)
CHAIN = runpy.run_path(
    str(
        STUDY
        / "experiments/exploratory/detection-boundary-v4-exploratory/automation"
        / "v4_event_automation.py"
    )
)
INSTALLED = (
    Path.home()
    / ".local/state/research-workbench/coord-20260925/v4_event_automation.py"
)
Refusal = TOOL["HandoffRefusalError"]
EXPLORATORY = ("x3", "x4", "x6", "x7")
ROLES = ("curves", "release_record", "gate_root", "criteria")
AVAILABLE = {"state": "disponível", "reason": None}
ABSENT = {"state": "indisponível", "reason": "agregado X5 não fornecido"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return path


def files(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): sha(p)
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def comparisons(
    curves: Path, record: Path, x5: Path | None, by_r: dict[str, Any] | None = None
) -> dict[str, Any]:
    state = AVAILABLE if x5 is not None else ABSENT
    binding = None if x5 is None else {"name": x5.name, "sha256": sha(x5)}
    return {
        "schema": "ic-study.v4-exploratory-comparisons.v1",
        "synthetic": True,
        "by_r": by_r
        or {str(r): {"r": r, "x5_state": dict(state)} for r in RELIABILITIES},
        "provenance": {
            "inputs": {
                "curves": {"name": curves.name, "sha256": sha(curves)},
                "release_record": {"name": record.name, "sha256": sha(record)},
                "x1b": None,
                "x5": binding,
                "x3": None,
                "x4": None,
            }
        },
    }


def chain_state(
    tmp: Path,
    *,
    synthetic: bool = True,
    shp: bool = True,
    x5: bool = True,
    condition: str = "declared-close",
    released: str = "2026-10-19T03:00:00Z",
    report_inputs: Callable[[dict[str, Any]], None] = lambda inputs: None,
) -> Path:
    """The files and status the installed chain leaves before the handoff."""
    coord = tmp / "state/coord-20260925"
    out = coord / "v4-release"
    study = tmp / "study/experiments/exploratory"
    criteria = write(study / "detection-boundary-v4/criteria-v43.json", {"t": 1})
    crosswalk = write(study / "shp-anchor-crosswalk-v1/crosswalk.json", {"c": 1})
    curves = write(out / "released-curves.json", {"synthetic": True, "curves": []})
    record = write(
        out / "release-record.json",
        {
            "schema": 1,
            "condition": condition,
            "released_utc": released,
            "released_curves_sha256": sha(curves),
        },
    )
    gate = tmp / "state/sealed-v4-gate/gate"
    write(gate / "G0-0000/result.json", {"synthetic": True})
    (gate / "criteria.jsonl").write_text('{"pass": true}\n')
    allocation = write(coord / "v4-allocation.json", {"synthetic": True})
    successor = write(coord / "v4-gate-logs/G1c-aggregate-successor.json", {"s": 1})
    anchor = coord / "shp-aggregate-successor-1.json"
    if shp:
        write(anchor, {"anchor": {"synthetic": True}})
    optional = [allocation, successor, anchor]
    confirmed = out / "confirmatory-1"
    report = confirmed / "report"
    report.mkdir(parents=True)
    (report / "F1_synthetic.pdf").write_bytes(b"%PDF synthetic\n")
    recorded: dict[str, Any] = {
        "curves": {"name": curves.name, "sha256": sha(curves)},
        "release_record": {"name": record.name, "sha256": sha(record)},
        "gate_root": {
            "identifier": gate.name,
            "criteria.jsonl": sha(gate / "criteria.jsonl"),
        },
        "stage_successors": [{"name": successor.name, "sha256": sha(successor)}],
        "allocation": {"name": allocation.name, "sha256": sha(allocation)},
        "criteria": {"name": criteria.name, "sha256": sha(criteria)},
    }
    if shp:
        recorded["shp"] = {"name": anchor.name, "sha256": sha(anchor)}
        recorded["crosswalk"] = {"name": crosswalk.name, "sha256": sha(crosswalk)}
    report_inputs(recorded)
    write(
        report / "manifest.json",
        {
            "schema": "ic-study.detection-v4-report-manifest.v1",
            "synthetic": synthetic,
            "dpi": 60,
            "inputs": recorded,
        },
    )
    catalog = {"schema": "ic-study.v4-result-values.v1", "values": {"v4.a": "1"}}
    write(confirmed / "result-catalog.json", catalog | {"synthetic": synthetic})
    key: dict[str, Any] = {
        "release": sha(record),
        "report_commit": "0" * 40,
        "automation": "a" * 64,
        "gate": CHAIN["manifest"](gate).decode(),
        "optional": {str(p): sha(p) for p in optional if p.is_file()},
    }
    CHAIN["save_checkpoint"](out / "confirmatory-checkpoint.json", key, confirmed)
    final = out / "exploratory-1"
    for name in ("x3", "x4", "x5", "x6", "x7"):
        write(final / f"aggregates/{name}.json", {"name": name, "synthetic": True})
    used = final / "aggregates/x5.json" if x5 else None
    write(final / "comparisons.json", comparisons(curves, record, used))
    manuscript = final / "manuscript"
    (manuscript / "generated").mkdir(parents=True)
    (manuscript / "generated/gate-outcomes.tex").write_text("% SYNTHETIC\n")
    for name in ("sn-jnl.cls", "sn-mathphys-num.bst"):
        (manuscript / name).write_text(f"% synthetic {name}\n")
    write(
        final / "catalog.json",
        {"values": {"v4.a": "1", "v4x.b": "2"}, "synthetic": synthetic},
    )
    key |= {"exports": [], "x5": "[]", "x7": "[]", "x1b": "b" * 64}
    CHAIN["save_checkpoint"](out / "exploratory-checkpoint.json", key, final)
    status = {
        "status": "awaiting-authorized-handoff",
        "assembly_ready": False,
        "confirmatory": str(confirmed),
        "exported_attempt": str(final),
        "inputs": {
            "curves": str(curves),
            "release_record": str(record),
            "gate_root": str(gate),
            "criteria": str(criteria),
            "allocation": str(allocation),
            "stage_successor": str(successor),
            "shp": str(anchor),
            "crosswalk": str(crosswalk),
            "confirmatory_catalog": str(confirmed / "result-catalog.json"),
            "merged_catalog": str(final / "catalog.json"),
            "generated": str(manuscript / "generated"),
            "report": str(report),
            "exploratory": {
                name: str(final / "aggregates" / f"{name}.json") for name in EXPLORATORY
            },
            "comparisons": str(final / "comparisons.json"),
            "owner_facts": None,
        },
    }
    CHAIN["record"](out / "chain-status.json", status)
    return out / "chain-status.json"


def authorized(tmp: Path, **state: Any) -> Path:
    status = chain_state(tmp, **state)
    synthetic = state.get("synthetic", True)
    path: Path = TOOL["prepare_copies"](status, tmp / "authorized", synthetic=synthetic)
    return path


def test_copies_every_selected_input_and_writes_the_handoff_contract(
    tmp_path: Path,
) -> None:
    spec_path = authorized(tmp_path)
    out = tmp_path / "authorized"
    spec = json.loads(spec_path.read_bytes())
    receipt = json.loads((spec_path.parent / "copy-receipt.json").read_bytes())
    source = json.loads(Path(receipt["status"]["path"]).read_bytes())["inputs"]
    assert spec["schema"] == "ic-study.v4-post-export-handoff.v1"
    assert spec["synthetic"] is True and spec["dpi"] == 60
    assert list(spec["inputs"]) == [
        *ROLES,
        "allocation",
        "stage_successors",
        "shp",
        "crosswalk",
    ]
    pairs = [(spec["inputs"][role], source[role]) for role in ROLES]
    pairs += [(spec["inputs"][r], source[r]) for r in ("allocation", "shp")]
    pairs += [(spec["inputs"]["stage_successors"][0], source["stage_successor"])]
    pairs += [(spec["inputs"]["crosswalk"], source["crosswalk"])]
    pairs += [(spec[r], source[r]) for r in ("report",)]
    pairs += [(spec[r], source[r]) for r in ("confirmatory_catalog", "merged_catalog")]
    pairs += [(spec["exploratory"][n], source["exploratory"][n]) for n in EXPLORATORY]
    pairs += [(spec["exploratory"]["comparisons"], source["comparisons"])]
    pairs += [(spec["exported_manuscript"] + "/generated", source["generated"])]
    for copied, original in pairs:
        target, origin = Path(copied), Path(original)
        assert target.is_relative_to(out) and target.name == origin.name
        if origin.is_dir():
            assert files(target) == files(origin)
        else:
            assert sha(target) == sha(origin)
    springer = Path(source["generated"]).parent
    for name in ("sn-jnl.cls", "sn-mathphys-num.bst"):
        assert sha(Path(spec["exported_manuscript"]) / name) == sha(springer / name)
    listed = {name: entry["sha256"] for name, entry in receipt["files"].items()}
    assert listed == {
        name: digest
        for name, digest in files(out).items()
        if name not in {"handoff.json", "copy-receipt.json"}
    }
    assert receipt["handoff"] == {"path": "handoff.json", "sha256": sha(spec_path)}
    assert all(not os.stat(p).st_mode & 0o077 for p in out.rglob("*"))


def test_omits_optional_inputs_the_chain_did_not_select(tmp_path: Path) -> None:
    spec = json.loads(authorized(tmp_path, shp=False).read_bytes())
    assert "shp" not in spec["inputs"] and "crosswalk" not in spec["inputs"]
    assert spec["inputs"]["stage_successors"]


@pytest.mark.skipif(
    not INSTALLED.is_file(), reason="needs the installed post-release automation"
)
def test_installed_automation_accepts_the_authorized_handoff(tmp_path: Path) -> None:
    installed = runpy.run_path(str(INSTALLED))
    spec_path = authorized(tmp_path)
    spec = installed["handoff_spec"](spec_path)
    installed["validate_handoff_report"](spec)
    chain = tmp_path / "state/coord-20260925/v4-release"
    confirmed = json.loads((chain / "confirmatory-checkpoint.json").read_bytes())
    exported = json.loads((chain / "exploratory-checkpoint.json").read_bytes())
    key = exported["inputs"]
    installed["bind_handoff"](spec, key, confirmed, exported, tmp_path / "study")


def edit_status(tmp: Path, change: Callable[[dict[str, Any]], None]) -> Path:
    path = chain_state(tmp)
    status = json.loads(path.read_bytes())
    change(status)
    path.write_text(json.dumps(status))
    return path


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda s: s.update(status="waiting-exports"), "awaiting-authorized-handoff"),
        (lambda s: s["inputs"].update(curves="relative.json"), "absolute"),
    ],
)
def test_refuses_a_status_that_is_not_an_exported_attempt(
    tmp_path: Path, change: Callable[[dict[str, Any]], None], message: str
) -> None:
    status = edit_status(tmp_path, change)
    with pytest.raises(Refusal, match=message):
        TOOL["prepare_copies"](status, tmp_path / "authorized", synthetic=True)
    assert not (tmp_path / "authorized").exists()


@pytest.mark.parametrize(
    "destination",
    [
        "sealed-v4-gate/copy",
        "restricted/copy",
        "coord-20260925/v4-release/copy",
        "coord-20260925/v4-gate-logs/copy",
        "Coord-20260925/V4-Release/copy",
        "Sealed-V4-gate/copy",
        "RESTRICTED/copy",
    ],
)
def test_refuses_a_destination_inside_a_protected_root(
    tmp_path: Path, destination: str
) -> None:
    status = chain_state(tmp_path)
    with pytest.raises(Refusal, match="protected"):
        TOOL["prepare_copies"](status, tmp_path / "other" / destination, synthetic=True)
    assert not (tmp_path / "other").exists()


def test_refuses_an_existing_destination_without_touching_it(tmp_path: Path) -> None:
    status = chain_state(tmp_path)
    existing = tmp_path / "authorized"
    existing.mkdir()
    (existing / "keep").write_text("x")
    with pytest.raises(Refusal, match="new directory"):
        TOOL["prepare_copies"](status, existing, synthetic=True)
    assert [p.name for p in existing.iterdir()] == ["keep"]


def role_file(inputs: dict[str, Any], role: str) -> Path:
    paths = {
        "gate_root": Path(inputs["gate_root"]) / "G0-0000/result.json",
        "stage_successors": Path(inputs["stage_successor"]),
        "report": Path(inputs["report"]) / "F1_synthetic.pdf",
        "generated": Path(inputs["generated"]) / "gate-outcomes.tex",
        "springer": Path(inputs["generated"]).parent / "sn-jnl.cls",
        **{name: Path(inputs["exploratory"][name]) for name in EXPLORATORY},
    }
    return paths.get(role) or Path(inputs[role])


TAMPERED = {
    "curves": "curves differ from the release record",
    "criteria": "criteria: report was rendered from another file",
    "crosswalk": "crosswalk: report was rendered from another file",
    **{
        role: f"{role} differs from the chain checkpoint"
        for role in (
            "release_record",
            "gate_root",
            "allocation",
            "stage_successors",
            "shp",
            "report",
            "confirmatory_catalog",
            "merged_catalog",
            "generated",
            "springer",
            *EXPLORATORY,
            "comparisons",
        )
    },
}


@pytest.mark.parametrize("role", sorted(TAMPERED))
def test_refuses_any_selected_input_changed_after_the_chain_recorded_it(
    tmp_path: Path, role: str
) -> None:
    status = chain_state(tmp_path)
    path = role_file(json.loads(status.read_bytes())["inputs"], role)
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(Refusal, match=TAMPERED[role]):
        TOOL["prepare_copies"](status, tmp_path / "authorized", synthetic=True)
    assert not (tmp_path / "authorized").exists()


def drop_allocation(status: dict[str, Any]) -> None:
    Path(status["inputs"]["allocation"]).unlink()


def link_in_gate(status: dict[str, Any]) -> None:
    gate = Path(status["inputs"]["gate_root"])
    (gate / "link.json").symlink_to(gate / "criteria.jsonl")


def empty_directory_in_gate(status: dict[str, Any]) -> None:
    (Path(status["inputs"]["gate_root"]) / "G9-added").mkdir()


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (drop_allocation, "allocation: selected by the chain but missing"),
        (link_in_gate, "symlink"),
        (empty_directory_in_gate, "gate_root differs from the chain checkpoint"),
    ],
)
def test_refuses_missing_linked_or_added_source_entries(
    tmp_path: Path, change: Callable[[dict[str, Any]], None], message: str
) -> None:
    status = chain_state(tmp_path)
    change(json.loads(status.read_bytes()))
    with pytest.raises(Refusal, match=message):
        TOOL["prepare_copies"](status, tmp_path / "authorized", synthetic=True)
    assert not (tmp_path / "authorized").exists()


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda r: r["gate_root"].update(identifier="other"), "gate_root"),
        (lambda r: r["crosswalk"].update(sha256="0" * 64), "crosswalk"),
        (lambda r: r.pop("allocation"), "allocation"),
        (lambda r: r["stage_successors"].clear(), "stage_successors"),
        (lambda r: r.update(stage_successors=None), "stage_successors"),
    ],
)
def test_refuses_a_report_rendered_from_other_inputs(
    tmp_path: Path, change: Callable[[dict[str, Any]], None], message: str
) -> None:
    status = chain_state(tmp_path, report_inputs=change)
    with pytest.raises(Refusal, match=message):
        TOOL["prepare_copies"](status, tmp_path / "authorized", synthetic=True)
    assert not (tmp_path / "authorized").exists()


@pytest.mark.parametrize("report_synthetic", [True, False])
def test_synthetic_marker_must_be_explicit_and_match_the_report(
    tmp_path: Path, report_synthetic: bool
) -> None:
    status = chain_state(tmp_path, synthetic=report_synthetic)
    with pytest.raises(Refusal, match="synthetic"):
        TOOL["prepare_copies"](
            status, tmp_path / "authorized", synthetic=not report_synthetic
        )
    assert not (tmp_path / "authorized").exists()


@pytest.mark.parametrize(
    ("condition", "released", "x5", "at_close"),
    [
        ("declared-close", "2026-10-19T03:00:00Z", True, True),
        ("declared-close", "2026-10-19T02:59:00Z", True, True),
        ("inventory-complete", "2026-10-05T12:00:00Z", False, False),
    ],
)
def test_owner_facts_come_from_the_authorized_copies(
    tmp_path: Path, condition: str, released: str, x5: bool, at_close: bool
) -> None:
    spec_path = authorized(tmp_path, condition=condition, released=released, x5=x5)
    out = tmp_path / "owner-facts.json"
    summary = TOOL["write_owner_facts"](spec_path, out)
    facts = json.loads(out.read_bytes())
    assert validate_facts(facts) == facts
    assert facts["synthetic"] is True and set(facts["facts"]) == {
        "gate.at_close",
        "post.x5_supplied",
    }
    close, supplied = (
        facts["facts"]["gate.at_close"],
        facts["facts"]["post.x5_supplied"],
    )
    assert close["value"] is at_close and supplied["value"] is x5
    directory = spec_path.parent
    assert close["source"]["record"] == "release-record.json"
    assert close["source"]["sha256"] == sha(directory / "release-record.json")
    assert condition in close["source"]["locator"]
    assert supplied["source"]["record"] == "comparisons.json"
    assert supplied["source"]["sha256"] == sha(directory / "comparisons.json")
    assert "/provenance/inputs/x5" in supplied["source"]["locator"]
    assert summary["facts"] == {"gate.at_close": at_close, "post.x5_supplied": x5}
    assert summary["pending_owner"] == []
    with pytest.raises(Refusal, match="new file"):
        TOOL["write_owner_facts"](spec_path, out)


def test_owner_facts_name_the_shp_declarations_left_to_the_owner(
    tmp_path: Path,
) -> None:
    spec_path = authorized(tmp_path, shp=False)
    summary = TOOL["write_owner_facts"](spec_path, tmp_path / "owner-facts.json")
    assert summary["pending_owner"] == ["shp.state", "shp.reason"]
    assert set(summary["conditional_owner"]) == {"shp.divergence"}


def rewrite_handoff(path: Path, spec: dict[str, Any]) -> None:
    """A consistent receipt over another handoff, as copy would have written it."""
    path.write_text(json.dumps(spec))
    receipt_path = path.with_name("copy-receipt.json")
    receipt = json.loads(receipt_path.read_bytes())
    receipt["handoff"]["sha256"] = sha(path)
    receipt_path.write_text(json.dumps(receipt))


def drop_release(spec: dict[str, Any]) -> None:
    del spec["inputs"]["curves"], spec["inputs"]["release_record"]


def swap_receipted_role(spec: dict[str, Any]) -> None:
    spec["inputs"]["release_record"] = spec["inputs"]["criteria"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (drop_release, "no authorized release record"),
        (lambda spec: spec.pop("exploratory"), "no authorized comparisons"),
        (swap_receipted_role, "release_record: differs from the copy receipt"),
    ],
)
def test_owner_facts_refuse_when_the_authorized_evidence_is_missing(
    tmp_path: Path, change: Callable[[dict[str, Any]], None], message: str
) -> None:
    spec_path = authorized(tmp_path)
    spec = json.loads(spec_path.read_bytes())
    change(spec)
    rewrite_handoff(spec_path, spec)
    out = tmp_path / "owner-facts.json"
    with pytest.raises(Refusal, match=message):
        TOOL["write_owner_facts"](spec_path, out)
    assert not out.exists()


def tamper_copy(directory: Path) -> None:
    path = directory / "catalog.json"
    path.chmod(0o600)
    path.write_bytes(path.read_bytes() + b"\n")


def add_copy(directory: Path) -> None:
    (directory / "report/extra.pdf").write_bytes(b"%PDF\n")


def edit_handoff(directory: Path) -> None:
    path = directory / "handoff.json"
    path.write_text(path.read_text().replace('"dpi": 60', '"dpi": 61'))


def rerun_chain(directory: Path) -> None:
    receipt = json.loads((directory / "copy-receipt.json").read_bytes())
    path = Path(receipt["checkpoints"]["exploratory"]["path"])
    path.write_bytes(path.read_bytes() + b"\n")


def add_directory(directory: Path) -> None:
    (directory / "gate/G9-added").mkdir()


RECEIPT_FAULTS = {
    "added directory": (add_directory, "directories differ from the copy receipt"),
    "tampered copy": (tamper_copy, "catalog.json: differs from the copy receipt"),
    "added copy": (add_copy, "list other files"),
    "edited handoff": (edit_handoff, "handoff.json differs from the copy receipt"),
    "chain rerun": (rerun_chain, "exploratory checkpoint changed after the copy"),
}


@pytest.mark.parametrize("fault", sorted(RECEIPT_FAULTS))
def test_owner_facts_reverify_the_receipt_before_reading_evidence(
    tmp_path: Path, fault: str
) -> None:
    spec_path = authorized(tmp_path)
    change, message = RECEIPT_FAULTS[fault]
    change(spec_path.parent)
    with pytest.raises(Refusal, match=message):
        TOOL["write_owner_facts"](spec_path, tmp_path / "owner-facts.json")


def test_receipt_check_follows_the_paths_inside_handoff_json(tmp_path: Path) -> None:
    spec_path = authorized(tmp_path)
    backup = tmp_path / "authorized-backup"
    shutil.copytree(spec_path.parent, backup)
    tamper_copy(spec_path.parent)
    with pytest.raises(Refusal, match="points outside its authorized directory"):
        TOOL["write_owner_facts"](backup / "handoff.json", tmp_path / "facts.json")


def release_record(**changes: Any) -> dict[str, Any]:
    return {
        "schema": 1,
        "condition": "declared-close",
        "released_utc": "2026-10-19T03:00:00Z",
        "released_curves_sha256": "c" * 64,
    } | changes


@pytest.mark.parametrize(
    ("record", "message"),
    [
        (release_record(schema=2), "schema"),
        (release_record(condition="partial"), "condition"),
        (release_record(released_utc="2026-10-19 03:00"), "timestamp"),
        (release_record(released_utc="2026-02-30T00:00:00Z"), "timestamp"),
        (release_record(released_utc="2026-10-18T12:00:00Z"), "precedes the close"),
        (
            release_record(condition="inventory-complete"),
            "inventory-complete release after the close",
        ),
        (
            release_record(
                condition="inventory-complete", released_utc="2026-10-19T02:59:00Z"
            ),
            "inventory-complete release after the close",
        ),
        (release_record(released_curves_sha256="d" * 64), "curves"),
    ],
)
def test_close_observation_refuses_an_inconsistent_release_record(
    record: dict[str, Any], message: str
) -> None:
    with pytest.raises(Refusal, match=message):
        TOOL["close_observation"](record, "c" * 64)


def rows(state: dict[str, Any], *, exceptional: dict[str, Any] | None = None) -> Any:
    result = {str(r): {"x5_state": dict(state)} for r in RELIABILITIES}
    if exceptional is not None:
        result["0.7"] = {"x5_state": exceptional}
    return result


def x5_cases(tmp: Path) -> list[tuple[dict[str, Any], str]]:
    curves = write(tmp / "released-curves.json", {"c": 1})
    record = write(tmp / "release-record.json", {"r": 1})
    x5 = write(tmp / "x5.json", {"x5": 1})
    fixture_style = comparisons(curves, record, x5) | {
        "provenance": {"synthetic": True}
    }
    missing_r = comparisons(curves, record, x5)
    del missing_r["by_r"]["0.9"]
    other_curves = comparisons(curves, record, x5)
    other_curves["provenance"]["inputs"]["curves"]["sha256"] = "0" * 64
    malformed = comparisons(curves, record, x5)
    malformed["provenance"]["inputs"]["x5"] = {"name": "x5.json", "sha256": "x"}
    return [
        (fixture_style, "does not record the X5 input"),
        (comparisons(curves, record, x5, rows(AVAILABLE, exceptional=ABSENT)), "0.7"),
        (comparisons(curves, record, None, rows(ABSENT, exceptional=AVAILABLE)), "0.7"),
        (missing_r, "reliabilit"),
        (other_curves, "curves"),
        (malformed, "X5 binding"),
        (comparisons(curves, record, x5) | {"schema": "other"}, "schema"),
    ]


@pytest.mark.parametrize("case", range(7))
def test_x5_supply_refuses_inconsistent_comparison_evidence(
    tmp_path: Path, case: int
) -> None:
    value, message = x5_cases(tmp_path)[case]
    curves = sha(tmp_path / "released-curves.json")
    record = sha(tmp_path / "release-record.json")
    with pytest.raises(Refusal, match=message):
        TOOL["x5_supply"](value, curves, record)


def fake_tools(tmp: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    monkeypatch.setenv("HOME", str(tmp / "home"))
    monkeypatch.setenv("FAKE_RECORD", str(tmp / "record.json"))
    automation = tmp / "automation.py"
    automation.write_text(
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "out = Path(sys.argv[sys.argv.index('--out') + 1])\n"
        "out.mkdir(parents=True, exist_ok=True)\n"
        "names = ['V4_SHORT_PATH', 'V4_TECTONIC', 'TECTONIC_CACHE_DIR',\n"
        "         'V4_OWNER_FACTS', 'V4_ALLOW_UNNICE', 'OMP_NUM_THREADS',\n"
        "         'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',\n"
        "         'VECLIB_MAXIMUM_THREADS', 'PYTHONDONTWRITEBYTECODE']\n"
        "record = {'argv': sys.argv, 'env': {n: os.environ.get(n) for n in names},\n"
        "          'nice': os.getpriority(os.PRIO_PROCESS, 0)}\n"
        "Path(os.environ['FAKE_RECORD']).write_text(json.dumps(record))\n"
        "if not os.environ.get('FAKE_NO_STATUS'):\n"
        "    status = {'status': 'awaiting-human-review', 'exit_code': 1}\n"
        "    (out / 'chain-status.json').write_text(json.dumps(status))\n"
        "sys.exit(1)\n"
    )
    tectonic = tmp / "bin/tectonic"
    tectonic.parent.mkdir()
    tectonic.write_text("#!/bin/sh\nexit 0\n")
    tectonic.chmod(tectonic.stat().st_mode | stat.S_IXUSR)
    spec = authorized(tmp)
    owner = tmp / "owner-facts.json"
    TOOL["write_owner_facts"](spec, owner)
    return {
        "automation": automation,
        "tectonic": tectonic,
        "spec": spec,
        "owner": owner,
    }


def run_arguments(tools: dict[str, Path], tmp: Path, *extra: str) -> list[str]:
    return [
        "run",
        "--checkout",
        str(tmp / "checkout"),
        "--handoff",
        str(tools["spec"]),
        "--owner-facts",
        str(tools["owner"]),
        "--out",
        str(tmp / "attempts"),
        "--automation",
        str(tools["automation"]),
        "--tectonic",
        str(tools["tectonic"]),
        *extra,
    ]


def durable_cache(tmp: Path) -> Path:
    cache = tmp / "home/.local/state/research-workbench/tectonic-cache"
    (cache / "formats").mkdir(parents=True)
    (cache / "formats/latex.fmt").write_bytes(b"fmt")
    return cache


@pytest.mark.parametrize("cache", ["missing", "empty"])
def test_run_refuses_a_missing_or_empty_tectonic_cache_before_the_handoff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    cache: str,
) -> None:
    tools = fake_tools(tmp_path, monkeypatch)
    durable = tmp_path / "home/.local/state/research-workbench/tectonic-cache"
    if cache == "empty":
        (durable / "formats").mkdir(parents=True)
    assert TOOL["main"](run_arguments(tools, tmp_path, "--synthetic")) == 2
    assert str(durable) in capsys.readouterr().err
    assert not (tmp_path / "record.json").exists()
    assert not (tmp_path / "attempts").exists()


def test_run_uses_the_durable_cache_and_the_cached_handoff_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    tools = fake_tools(tmp_path, monkeypatch)
    monkeypatch.setenv("V4_ALLOW_UNNICE", "1")
    monkeypatch.setenv("TECTONIC_CACHE_DIR", str(tmp_path / "wiped"))
    durable = durable_cache(tmp_path)
    monkeypatch.chdir(tmp_path)
    arguments = run_arguments(tools, tmp_path, "--synthetic")
    arguments[arguments.index("--out") + 1] = "attempts"
    assert TOOL["main"](arguments) == 1
    record = json.loads((tmp_path / "record.json").read_bytes())
    assert record["argv"] == [
        str(tools["automation"]),
        "handoff",
        str(tmp_path / "checkout"),
        "--spec",
        str(tools["spec"]),
        "--out",
        str(tmp_path / "attempts"),
    ]
    assert record["env"] == {
        "V4_SHORT_PATH": "1",
        "V4_TECTONIC": str(tools["tectonic"]),
        "TECTONIC_CACHE_DIR": str(durable),
        "V4_OWNER_FACTS": str(tools["owner"]),
        "V4_ALLOW_UNNICE": None,
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    assert record["nice"] >= 15
    assert "awaiting-human-review" in capsys.readouterr().out


def test_run_reports_when_the_automation_writes_no_new_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    tools = fake_tools(tmp_path, monkeypatch)
    durable_cache(tmp_path)
    (tmp_path / "attempts").mkdir()
    (tmp_path / "attempts/chain-status.json").write_text('{"status": "old"}')
    monkeypatch.setenv("FAKE_NO_STATUS", "1")
    assert TOOL["main"](run_arguments(tools, tmp_path, "--synthetic")) == 1
    output = capsys.readouterr().out
    assert "no new chain-status.json" in output and "old" not in output


def missing_tectonic(tools: dict[str, Path]) -> list[str]:
    tools["tectonic"].unlink()
    return ["--synthetic"]


def tampered_copy(tools: dict[str, Path]) -> list[str]:
    tamper_copy(tools["spec"].parent)
    return ["--synthetic"]


def real_owner_facts(tools: dict[str, Path]) -> list[str]:
    facts = json.loads(tools["owner"].read_bytes()) | {"synthetic": False}
    tools["owner"].write_text(json.dumps(facts))
    return ["--synthetic"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (missing_tectonic, "Tectonic executable missing"),
        (lambda tools: [], "--synthetic is only for rehearsals"),
        (tampered_copy, "differs from the copy receipt"),
        (real_owner_facts, "synthetic markers differ"),
    ],
)
def test_run_refuses_before_starting_the_automation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    change: Callable[[dict[str, Path]], list[str]],
    message: str,
) -> None:
    tools = fake_tools(tmp_path, monkeypatch)
    durable_cache(tmp_path)
    assert TOOL["main"](run_arguments(tools, tmp_path, *change(tools))) == 2
    assert message in capsys.readouterr().err
    assert not (tmp_path / "record.json").exists()


@pytest.mark.parametrize("option", ["--out", "--owner-facts"])
def test_run_refuses_protected_paths_in_any_letter_case(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    option: str,
) -> None:
    tools = fake_tools(tmp_path, monkeypatch)
    durable_cache(tmp_path)
    arguments = run_arguments(tools, tmp_path, "--synthetic")
    protected = tmp_path / "x/Coord-20260925/V4-Release"
    protected.mkdir(parents=True)
    if option == "--owner-facts":
        shutil.copy2(tools["owner"], protected / "owner-facts.json")
    target = protected / ("owner-facts.json" if option == "--owner-facts" else "a")
    arguments[arguments.index(option) + 1] = str(target)
    assert TOOL["main"](arguments) == 2
    assert "inside a protected root" in capsys.readouterr().err
    assert not (tmp_path / "record.json").exists()


def test_cli_reports_a_refusal_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    status = edit_status(tmp_path, lambda s: s.update(status="failed"))
    arguments = ["copy", "--status", str(status), "--out", str(tmp_path / "a")]
    assert TOOL["main"]([*arguments, "--synthetic"]) == 2
    error = capsys.readouterr().err
    assert "refused" in error and "Traceback" not in error
