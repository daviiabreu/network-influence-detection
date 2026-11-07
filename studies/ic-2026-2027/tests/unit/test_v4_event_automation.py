"""Exercise private event scripts using only local artificial hosts and artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from ic_study.analysis.v4_report_synthetic import (
    GatePlan,
    UnitPlan,
    build_gate,
    build_release,
    logistic_profile,
    unit_keys,
    write_release,
)

STUDY = Path(__file__).resolve().parents[2]
AUTOMATION = (
    STUDY / "experiments/exploratory/detection-boundary-v4-exploratory/automation"
)
MODULE = runpy.run_path(str(AUTOMATION / "v4_event_automation.py"))
COMMIT = MODULE["COMMIT"]
GATE_ID = "6d6f9f4d5d04fbc1cd79f20d3beff499ccdc318584f3f348bdb956c71a344c90"
SPRINGER_TEMPLATE = Path.home() / ".local/state/research-workbench/springer-template"
requires_springer_template = pytest.mark.skipif(
    not all(
        (SPRINGER_TEMPLATE / name).is_file()
        for name in ("sn-jnl.cls", "sn-mathphys-num.bst")
    ),
    reason="Chain tests require the local Springer template (sn-jnl.cls and BST)",
)

FAKE_TOOL = r"""
import importlib, json, os, shlex, shutil, subprocess, sys
from pathlib import Path
tool = Path(sys.argv[0]).name
args = sys.argv[1:]
root = Path(os.environ['FAKE_ROOT'])
control = root / 'control'
def consume(name):
    path = control / name
    if path.exists():
        path.unlink()
        return True
    return False
def audit(message):
    with (control / 'audit').open('a') as stream:
        stream.write(message + '\n')
if tool == 'ssh':
    target = next(a for a in args if '@' in a)
    host = {'icmomat@100.66.168.30':'icmomat', 'icllm@100.116.144.101':'icllm',
            'davi@homelab':'homelab'}[target]
    port = args[args.index('-p') + 1]
    program = sys.stdin.read()
    home = root / 'hosts' / host
    remote_args = shlex.split(args[args.index(target) + 1])
    kind = ('marker' if 'EXPORTED' in program else
            'manifest' if 'hashlib' in program else 'finished')
    audit('ssh ' + host + ' ' + port + ' ' + kind)
    if kind == 'marker' and consume('ack-fail-' + host):
        sys.exit(1)
    env = dict(os.environ, FAKE_REMOTE_HOME=str(home), FAKE_HOST=host)
    program = program.replace('$HOME', '$FAKE_REMOTE_HOME')
    result = subprocess.run(remote_args, input=program.encode(), cwd=home, env=env)
    sys.exit(result.returncode)
elif tool == 'rsync':
    source, destination = args[-2:]
    target, path = source.split(':', 1)
    host = {'icmomat@100.66.168.30':'icmomat', 'icllm@100.116.144.101':'icllm',
            'davi@homelab':'homelab'}[target]
    audit('rsync ' + host)
    if consume('copy-fail-' + host):
        sys.exit(12)
    source = root / 'hosts' / host / path
    destination = Path(destination)
    for child in destination.iterdir():
        shutil.rmtree(child) if child.is_dir() else child.unlink()
    shutil.copytree(source, destination, dirs_exist_ok=True, copy_function=shutil.copy2)
    for child in destination.rglob('*'):
        child.chmod(0o700 if child.is_dir() else 0o600)
    if consume('diverge-' + host):
        with (destination / 'payload.bin').open('ab') as stream:
            stream.write(b'changed')
    sys.exit(0)
elif tool == 'pgrep':
    worker = control / ('worker-' + os.environ.get('FAKE_HOST', 'none'))
    if os.environ.get('FAKE_HOST') and worker.exists():
        sys.exit(0)
    sys.exit(1)
elif tool == 'date':
    print('202610200300' if (control / 'closed').exists() else '202609300000')
elif tool == 'sleep':
    audit('sleep ' + args[0])
    (control / 'ready').touch()
elif tool == 'git':
    checkout = args[args.index('-C') + 1]
    if 'status' in args:
        if (control / 'dirty').exists(): print(' M synthetic')
    else:
        print('3334ac0f96268a76d62c3b68a9705cb7fe05587e'
              if checkout.endswith('aggregate-checkout') else 'a' * 40)
elif tool == 'uv':
    if any('release_on_completion.py' in a for a in args):
        if '--check-only' in args:
            print(json.dumps({'complete': (control / 'ready').exists(), 'pending': 0}))
            sys.exit(0)
        count = control / 'release-attempts'
        n = int(count.read_text()) + 1 if count.exists() else 1
        count.write_text(str(n))
        if n <= int(os.environ.get('FAKE_RELEASE_FAILURES', '0')):
            print('synthetic preflight refused', file=sys.stderr)
            sys.exit(2)
        receipt = Path(args[args.index('--record') + 1])
        for name in ('release-record.json', 'released-curves.json'):
            shutil.copy2(root / 'seed-release' / name, receipt.parent / name)
        sys.exit(0)
    if '-m' in args:
        module = args[args.index('-m') + 1]
        remaining = args[args.index('-m') + 2:]
        audit(module)
        if consume('command-fail-' + module.rsplit('_', 1)[-1]): sys.exit(9)
        if module.startswith('ic_study.simulation.'):
            name = module.rsplit('_', 1)[-1]
            assert Path.cwd() == root / 'aggregate-checkout' / 'studies/ic-2026-2027'
            assert remaining.count('--out') == (3 if name in ('x3','x4','x6') else 1)
            shutil.copy2(root / 'fixtures' / (name + '.json'),
                         remaining[remaining.index('--output') + 1])
        else:
            if module.endswith('detection_v4_report'):
                remaining += ['--synthetic', '--dpi', '40']
            sys.exit(importlib.import_module(module).main(remaining))
    else:
        checker = args.index('python') + 1
        result = subprocess.run([sys.executable, *args[checker:]])
        sys.exit(result.returncode)
elif tool == 'nix':
    audit('compile')
    if consume('compile-fail'): sys.exit(8)
    if os.environ.get('FAKE_REAL_TECTONIC'):
        result = subprocess.run([os.environ['FAKE_REAL_TECTONIC'], 'shell',
                                 'nixpkgs#tectonic', '--command', 'tectonic',
                                 'main.tex'])
        sys.exit(result.returncode)
    Path('main.pdf').write_bytes(b'%PDF-1.4\nsynthetic compiler placeholder\n')
    Path('main.log').write_text('synthetic compile\n')
"""


@pytest.fixture
def sandbox(tmp_path: Path) -> dict[str, Any]:
    root = tmp_path
    control = root / "control"
    control.mkdir()
    binaries = root / "bin"
    binaries.mkdir()
    for name in ("ssh", "rsync", "pgrep", "date", "sleep", "git", "uv", "nix"):
        tool = binaries / name
        tool.write_text(f"#!{sys.executable}\n" + FAKE_TOOL)
        tool.chmod(0o700)
    coord = root / "coord"
    coord.mkdir()
    for host, (_, _, base) in MODULE["HOSTS"].items():
        output = root / "hosts" / host / base / "sealed-v4-exploratory-x3-x7/3334ac0f"
        (output / "logs").mkdir(parents=True)
        (output / "empty").mkdir()
        (output / "logs/run.log").write_text("started synthetic\nfinished synthetic\n")
        (output / "payload.bin").write_bytes(b"artificial private bytes\x00\xff")
        os.utime(output / "payload.bin", (1234567890, 1234567890))
    checkout = root / "report-checkout"
    experiment = (
        checkout / "studies/ic-2026-2027/experiments/exploratory/detection-boundary-v4"
    )
    experiment.mkdir(parents=True)
    (experiment / "release_on_completion.py").touch()
    frozen = root / "frozen/studies/ic-2026-2027"
    frozen.mkdir(parents=True)
    aggregate = root / "aggregate-checkout/studies/ic-2026-2027"
    aggregate.mkdir(parents=True)
    env = dict(
        os.environ,
        FAKE_ROOT=str(root),
        PATH=str(binaries) + os.pathsep + os.environ["PATH"],
        PYTHONPATH=str(STUDY / "src"),
        V4_COORD=str(coord),
        V4_EXPORT_ROOT=str(root / "exports"),
        V4_FROZEN=str(root / "frozen"),
        V4_UV=str(binaries / "uv"),
        V4_AGGREGATE_CHECKOUT=str(root / "aggregate-checkout"),
        V4_SPRINGER=str(root / "springer"),
        X5_OUT=str(root / "x5-out"),
        X7_OUT=str(root / "x7-out"),
        X1B_JSON=str(root / "fixtures/x1b.json"),
        MPLCONFIGDIR=str(root / "mpl"),
    )
    return {
        "root": root,
        "env": env,
        "coord": coord,
        "control": control,
        "checkout": checkout,
        "exports": root / "exports",
    }


def invoke(
    sandbox: dict[str, Any], script: str, *args: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(AUTOMATION / script), *args],
        env=sandbox["env"],
        capture_output=True,
        text=True,
        timeout=180,
    )


def seed_release(sandbox: dict[str, Any], destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    plans = {
        unit: UnitPlan(logistic_profile(0.02))
        for unit in unit_keys(tier=1, family="B").values()
    }
    write_release(
        destination / "released-curves.json",
        build_release(destination / "panels", plans, draws=30),
    )


def prepare_chain(sandbox: dict[str, Any]) -> None:
    root = sandbox["root"]
    source = sandbox["checkout"] / "studies/ic-2026-2027"
    shutil.copytree(
        STUDY / "publications/jcss-manuscript", source / "publications/jcss-manuscript"
    )
    criteria = "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
    shutil.copy2(STUDY / criteria, source / criteria)
    seed_release(sandbox, sandbox["coord"] / "v4-release")
    gate = build_gate(root / GATE_ID, GatePlan(stages=("G0",)))
    (sandbox["coord"] / "v4-gate-driver.log").write_text(f"sealed root: {gate}\n")
    fixtures = runpy.run_path(str(STUDY / "tests/unit/test_v4_exploratory_export.py"))
    fixtures["synthetic_inputs"](root / "fixtures")
    extra = runpy.run_path(str(STUDY / "tests/unit/test_v4_exploratory_comparisons.py"))
    for name in ("x1b", "x5"):
        (root / "fixtures" / f"{name}.json").write_text(
            json.dumps(extra[f"{name}_input"]())
        )
    for name in ("x5", "x7"):
        (root / f"{name}-out").mkdir()
        (root / f"{name}-out/record.bin").write_bytes(b"synthetic")
    (root / "springer").mkdir()
    for name in ("sn-jnl.cls", "sn-mathphys-num.bst"):
        shutil.copy2(
            SPRINGER_TEMPLATE / name,
            root / "springer" / name,
        )


def test_wait_retries_beyond_three_then_releases(sandbox: dict[str, Any]) -> None:
    seed_release(sandbox, sandbox["root"] / "seed-release")
    sandbox["env"]["FAKE_RELEASE_FAILURES"] = "4"
    (sandbox["control"] / "ready").touch()
    result = invoke(sandbox, "v4-release-wait.next.sh", str(sandbox["checkout"]))
    assert result.returncode == 0, result.stderr
    out = sandbox["coord"] / "v4-release"
    assert (out / "release-ALERT").read_text().splitlines()[
        -1
    ] == "synthetic preflight refused"
    assert (sandbox["control"] / "release-attempts").read_text() == "5"
    assert (sandbox["control"] / "audit").read_text().count("sleep 1800") == 4
    assert MODULE["release_pair"](out)
    assert (
        invoke(sandbox, "v4-release-wait.next.sh", str(sandbox["checkout"])).returncode
        == 0
    )


def test_wait_inventory_and_alternative_close(sandbox: dict[str, Any]) -> None:
    seed_release(sandbox, sandbox["root"] / "seed-release")
    assert (
        invoke(sandbox, "v4-release-wait.next.sh", str(sandbox["checkout"])).returncode
        == 0
    )
    assert "sleep 300" in (sandbox["control"] / "audit").read_text()
    shutil.rmtree(sandbox["coord"] / "v4-release")
    (sandbox["control"] / "ready").unlink()
    (sandbox["control"] / "closed").touch()
    assert (
        invoke(sandbox, "v4-release-wait.next.sh", str(sandbox["checkout"])).returncode
        == 0
    )
    assert not (sandbox["control"] / "ready").exists()


@pytest.mark.parametrize(
    "failure", ["copy-fail-icmomat", "diverge-icmomat", "ack-fail-icmomat"]
)
def test_watch_failure_resume_and_idempotence(
    sandbox: dict[str, Any], failure: str
) -> None:
    (sandbox["control"] / failure).touch()
    assert invoke(sandbox, "x3x7-export-watch.sh", "--once").returncode == 1
    receipts = sandbox["coord"] / "lab-pcs/export-manifests/3334ac0f"
    assert not (receipts / "icmomat.verified.json").exists()
    assert (sandbox["coord"] / "lab-pcs/export-icmomat-ALERT").exists()
    assert invoke(sandbox, "x3x7-export-watch.sh", "--once").returncode == 0
    assert invoke(sandbox, "x3x7-export-watch.sh", "--verify-local").returncode == 0
    audit = (sandbox["control"] / "audit").read_text()
    assert invoke(sandbox, "x3x7-export-watch.sh", "--once").returncode == 0
    assert (sandbox["control"] / "audit").read_text() == audit
    for host in MODULE["HOSTS"]:
        output = sandbox["exports"] / "3334ac0f" / host
        assert output.stat().st_mode & 0o777 == 0o700
        assert (output / "empty").is_dir()
        assert (output / "payload.bin").stat().st_mtime == 1234567890
        saved = receipts / f"{host}.sha256.json"
        assert MODULE["manifest"](output) == saved.read_bytes()
        if host != "homelab":
            marker = sandbox["root"] / "hosts" / host / "Documents/ic/EXPORTED"
            assert (
                marker.read_text().strip()
                == hashlib.sha256(saved.read_bytes()).hexdigest()
            )
    assert not (sandbox["root"] / "hosts/homelab/Documents/ic/EXPORTED").exists()
    assert (
        "ssh icmomat 443" in audit
        and "ssh icllm 443" in audit
        and "ssh homelab 22" in audit
    )


def test_watch_waits_for_finished_and_no_workers(sandbox: dict[str, Any]) -> None:
    (sandbox["control"] / "worker-icmomat").touch()
    log = (
        sandbox["root"]
        / "hosts/icllm/Documents/ic/sealed-v4-exploratory-x3-x7/3334ac0f/logs/run.log"
    )
    log.write_text("started synthetic\n")
    assert invoke(sandbox, "x3x7-export-watch.sh", "--once").returncode == 3
    audit = (sandbox["control"] / "audit").read_text()
    assert "rsync icmomat" not in audit and "rsync icllm" not in audit


def test_watch_refuses_changed_verified_copy(sandbox: dict[str, Any]) -> None:
    assert invoke(sandbox, "x3x7-export-watch.sh", "--once").returncode == 0
    (sandbox["exports"] / "3334ac0f/icmomat/payload.bin").write_bytes(b"corrupt")
    assert invoke(sandbox, "x3x7-export-watch.sh", "--verify-local").returncode == 1
    assert invoke(sandbox, "x3x7-export-watch.sh", "--once").returncode == 1


def test_chain_waits_for_pair_and_refuses_wrong_commit(sandbox: dict[str, Any]) -> None:
    args = (str(sandbox["checkout"]), "--once")
    assert invoke(sandbox, "v4-post-release-chain.sh", *args).returncode == 3
    sandbox["env"]["V4_AGGREGATE_CHECKOUT"] = str(sandbox["root"] / "wrong-checkout")
    assert invoke(sandbox, "v4-post-release-chain.sh", *args).returncode == 1
    assert (sandbox["coord"] / "v4-release/chain-ALERT").exists()


def test_chain_refuses_divergent_release_pair(sandbox: dict[str, Any]) -> None:
    seed_release(sandbox, sandbox["coord"] / "v4-release")
    (sandbox["coord"] / "v4-release/released-curves.json").write_bytes(b"changed")
    assert (
        invoke(
            sandbox, "v4-post-release-chain.sh", str(sandbox["checkout"]), "--once"
        ).returncode
        == 1
    )
    assert not (sandbox["control"] / "audit").exists()


@pytest.mark.parametrize("receipt", [[], {}, "malformed"])
def test_chain_alerts_for_malformed_release_receipt(
    sandbox: dict[str, Any], receipt: Any
) -> None:
    out = sandbox["coord"] / "v4-release"
    out.mkdir()
    (out / "release-record.json").write_text(json.dumps(receipt))
    result = invoke(
        sandbox, "v4-post-release-chain.sh", str(sandbox["checkout"]), "--once"
    )
    assert result.returncode == 1
    assert "release receipt malformed" in (out / "chain-ALERT").read_text()
    assert not (sandbox["control"] / "audit").exists()


@requires_springer_template
def test_chain_two_events_real_exports_and_restart(sandbox: dict[str, Any]) -> None:
    prepare_chain(sandbox)
    manuscript = (
        sandbox["checkout"] / "studies/ic-2026-2027/publications/jcss-manuscript"
    )
    original = MODULE["manifest"](manuscript)
    args = (str(sandbox["checkout"]), "--once")
    result = invoke(sandbox, "v4-post-release-chain.sh", *args)
    assert result.returncode == 3, (
        sandbox["coord"] / "v4-release/chain-ALERT"
    ).read_text()
    assert invoke(sandbox, "x3x7-export-watch.sh", "--once").returncode == 0
    (sandbox["control"] / "command-fail-x4").touch()
    assert invoke(sandbox, "v4-post-release-chain.sh", *args).returncode == 1
    assert not (sandbox["coord"] / "v4-release/exploratory-checkpoint.json").exists()
    result = invoke(sandbox, "v4-post-release-chain.sh", *args)
    status = json.loads(
        (sandbox["coord"] / "v4-release/chain-status.json").read_bytes()
    )
    assert status["status"] == "awaiting-human-review", (
        sandbox["coord"] / "v4-release/chain-ALERT"
    ).read_text()
    final = Path(status["final"])
    assert (final / "catalog.json").is_file()
    assert (
        "SYNTHETIC" in (final / "manuscript/generated/exploratory-x3.tex").read_text()
    )
    assert (
        "\\input{sections/event-exploratory}"
        in (final / "manuscript/main.tex").read_text()
    )
    assert MODULE["manifest"](manuscript) == original
    audit = (sandbox["control"] / "audit").read_text()
    assert (
        invoke(sandbox, "v4-post-release-chain.sh", *args).returncode
        == result.returncode
    )
    assert (sandbox["control"] / "audit").read_text() == audit
    (final / "catalog.json").write_bytes(b"changed")
    assert invoke(sandbox, "v4-post-release-chain.sh", *args).returncode == 1


@requires_springer_template
def test_chain_failed_compile_creates_successor_attempt(
    sandbox: dict[str, Any],
) -> None:
    prepare_chain(sandbox)
    (sandbox["control"] / "compile-fail").touch()
    args = (str(sandbox["checkout"]), "--once")
    assert invoke(sandbox, "v4-post-release-chain.sh", *args).returncode == 1
    out = sandbox["coord"] / "v4-release"
    assert not (out / "confirmatory-checkpoint.json").exists()
    assert invoke(sandbox, "v4-post-release-chain.sh", *args).returncode == 3
    assert len(list(out.glob("confirmatory-*"))) == 3


def test_shell_selection_keeps_tables_and_omits_zero_outcomes() -> None:
    select = MODULE["select_shells"]
    shells = (
        r"\paragraph{Some outcome.}Count \resultnum{v4x.x3.count.error}{[n]}"
        + "\n% TABLE INPUTS:\n"
        + r"\input{generated/exploratory-x3}"
    )
    output = select(shells, {"v4x.x3.count.error": "0"})
    assert "Some outcome" not in output
    assert r"\input{generated/exploratory-x3}" in output


def test_shell_selection_preserves_unavailable_truth_without_denominators(
    tmp_path: Path,
) -> None:
    from ic_study.analysis.v4_exploratory_export import export

    fixture = runpy.run_path(str(STUDY / "tests/unit/test_v4_exploratory_export.py"))
    paths = fixture["synthetic_inputs"](tmp_path / "inputs")
    x6 = json.loads(paths["x6"].read_bytes())
    x6["x6a"]["band"]["vs_d1"] = None
    paths["x6"].write_text(json.dumps(x6))
    catalog = export(paths, tmp_path / "manuscript").catalog
    source = STUDY / "publications/jcss-manuscript/pipeline/drafts/2026-09-30"
    shells = MODULE["select_shells"](
        (source / "exploratory-results-shells.tex").read_text(), catalog
    )
    assert "X6: unavailable procedural truth." in shells
    assert "Primary joint D1 coverage was" not in shells
    assert "The separate gaps-as-misses reference was" not in shells
    assert r"\input{generated/exploratory-x6}" in shells


def test_watch_rejects_remote_symlink_and_export_marker_conflict(
    sandbox: dict[str, Any],
) -> None:
    root = sandbox["root"]
    source = root / "hosts/icmomat/Documents/ic/sealed-v4-exploratory-x3-x7/3334ac0f"
    (source / "link").symlink_to(source / "payload.bin")
    marker = root / "hosts/icllm/Documents/ic/EXPORTED"
    marker.write_text("previous different export\n")
    assert invoke(sandbox, "x3x7-export-watch.sh", "--once").returncode == 1
    receipts = sandbox["coord"] / "lab-pcs/export-manifests/3334ac0f"
    assert not (receipts / "icmomat.verified.json").exists()
    assert not (receipts / "icllm.verified.json").exists()
    assert marker.read_text() == "previous different export\n"
