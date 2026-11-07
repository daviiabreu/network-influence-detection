"""Private event orchestration; scientific work stays in the existing modules."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

COMMIT = "3334ac0f96268a76d62c3b68a9705cb7fe05587e"
GATE_ID = "6d6f9f4d5d04fbc1cd79f20d3beff499ccdc318584f3f348bdb956c71a344c90"
STUDY = Path("studies/ic-2026-2027")
HOSTS = {
    "icmomat": ("icmomat@100.66.168.30", 443, "Documents/ic"),
    "icllm": ("icllm@100.116.144.101", 443, "Documents/ic"),
    "homelab": ("davi@homelab", 22, ".local/state/research-workbench"),
}
MANIFEST_PROGRAM = """import hashlib, json, os, stat, sys
from pathlib import Path
root = Path(sys.argv[1])
if not root.is_dir() or root.is_symlink():
    raise ValueError("invalid tree root")
entries = []
for path in sorted(root.rglob("*")):
    mode = path.lstat().st_mode
    name = path.relative_to(root).as_posix()
    if stat.S_ISDIR(mode):
        entries.append([name, "directory"])
    elif stat.S_ISREG(mode):
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        entries.append([name, "file", digest.hexdigest()])
    else:
        raise ValueError("symlink or special file refused")
print(json.dumps(entries, ensure_ascii=True, separators=(",", ":")))
"""
FINISHED_PROGRAM = """set -eu
test -f "$1/logs/run.log" || exit 3
grep -Eq '^finished( |$)' "$1/logs/run.log" || exit 3
if pgrep -f '[i]c_study.simulation.v4_exploratory' >/dev/null; then
    exit 3
else
    code=$?
    test "$code" -eq 1 || exit 1
fi
"""


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def record(path: Path, value: Any) -> None:
    atomic(path, (json.dumps(value, sort_keys=True, indent=2) + "\n").encode())


def operational(path: Path, message: str) -> None:
    with path.open("a") as stream:
        stream.write(
            time.strftime("%Y-%m-%dT%H:%M:%SZ ", time.gmtime()) + message + "\n"
        )


@contextlib.contextmanager
def lock(path: Path) -> Iterator[None]:
    with path.open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def command(
    args: list[str],
    *,
    cwd: Path | None = None,
    data: str | None = None,
    capture: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        args,
        cwd=cwd,
        input=data.encode() if data is not None else None,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def require_run(args: list[str], cwd: Path | None = None) -> None:
    result = command(args, cwd=cwd)
    if result.returncode:
        raise RuntimeError(f"command failed: exit={result.returncode}")


def manifest(root: Path) -> bytes:
    result = command([sys.executable, "-c", MANIFEST_PROGRAM, str(root)], capture=True)
    if result.returncode:
        raise RuntimeError("local manifest failed")
    return result.stdout


def remote(host: str, program: str, *args: str) -> subprocess.CompletedProcess[bytes]:
    target, port, _ = HOSTS[host]
    invocation = " ".join(shlex.quote(arg) for arg in args)
    return command(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=20",
            "-p",
            str(port),
            target,
            invocation,
        ],
        data=program,
        capture=True,
    )


def remote_manifest(host: str, root: str) -> bytes:
    result = remote(host, MANIFEST_PROGRAM, "python3", "-", root)
    if result.returncode:
        raise RuntimeError("remote manifest failed")
    return result.stdout


def exported_roots(coord: Path, exports: Path) -> list[Path] | None:
    receipts = coord / "lab-pcs/export-manifests/3334ac0f"
    roots = []
    for host in HOSTS:
        receipt = receipts / f"{host}.verified.json"
        if not receipt.exists():
            return None
        root = exports / "3334ac0f" / host
        saved = receipts / f"{host}.sha256.json"
        value = json.loads(receipt.read_bytes())
        if (
            value
            != {
                "host": host,
                "commit": COMMIT,
                "root": str(root),
                "manifest_sha256": sha(saved),
            }
            or manifest(root) != saved.read_bytes()
        ):
            raise RuntimeError("export integrity failed")
        roots.append(root)
    return roots


def export_host(host: str, coord: Path, exports: Path) -> bool:
    target, port, base = HOSTS[host]
    source = f"{base}/sealed-v4-exploratory-x3-x7/3334ac0f"
    receipts = coord / "lab-pcs/export-manifests/3334ac0f"
    receipts.mkdir(mode=0o700, parents=True, exist_ok=True)
    saved = receipts / f"{host}.sha256.json"
    receipt = receipts / f"{host}.verified.json"
    destination = exports / "3334ac0f" / host
    if receipt.exists():
        value = json.loads(receipt.read_bytes())
        if (
            value
            != {
                "host": host,
                "commit": COMMIT,
                "root": str(destination),
                "manifest_sha256": sha(saved),
            }
            or manifest(destination) != saved.read_bytes()
        ):
            raise RuntimeError("previous export changed")
        return True
    if not destination.exists():
        ready = remote(host, FINISHED_PROGRAM, "bash", "-s", "--", source)
        if ready.returncode == 3:
            return False
        if ready.returncode:
            raise RuntimeError("finish check failed")
        before = remote_manifest(host, source)
        destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        partial = destination.parent / f".partial-{host}"
        partial.mkdir(mode=0o700, exist_ok=True)
        result = command(
            [
                "rsync",
                "-rt",
                "--checksum",
                "--delete",
                "--chmod=Du=rwx,Dgo=,Fu=rw,Fgo=",
                "-e",
                f"ssh -o BatchMode=yes -o ConnectTimeout=20 -p {port}",
                f"{target}:{source}/",
                f"{partial}/",
            ]
        )
        if result.returncode:
            raise RuntimeError("copy failed")
        after = remote_manifest(host, source)
        if before != after or manifest(partial) != before:
            raise RuntimeError("manifest mismatch")
        for path in [partial, *partial.rglob("*")]:
            path.chmod(0o700 if path.is_dir() else 0o600)
        if remote(host, FINISHED_PROGRAM, "bash", "-s", "--", source).returncode:
            raise RuntimeError("host became active during copy")
        atomic(saved, before)
        os.replace(partial, destination)
        sync_directory(destination.parent)
    elif not saved.exists() or manifest(destination) != saved.read_bytes():
        raise RuntimeError("unacknowledged export changed")
    digest = sha(saved)
    if host != "homelab":
        marker = """set -eu
umask 077
mkdir -p "$HOME/Documents/ic"
marker="$HOME/Documents/ic/EXPORTED"
if test -e "$marker"; then
    test "$(cat "$marker")" = "$1"
else
    temporary=$(mktemp "$HOME/Documents/ic/.EXPORTED.XXXXXX")
    printf '%s\\n' "$1" >"$temporary"
    mv "$temporary" "$marker"
fi
"""
        if remote(host, marker, "bash", "-s", "--", digest).returncode:
            raise RuntimeError("EXPORTED acknowledgment failed")
    record(
        receipt,
        {
            "host": host,
            "commit": COMMIT,
            "root": str(destination),
            "manifest_sha256": digest,
        },
    )
    return True


def watch(coord: Path, exports: Path, once: bool, verify_only: bool) -> int:
    if verify_only:
        return 0 if exported_roots(coord, exports) else 3
    state = coord / "lab-pcs"
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    with lock(state / ".export-watch.lock"):
        while True:
            statuses = {}
            for host in HOSTS:
                try:
                    done = export_host(host, coord, exports)
                    statuses[host] = "verified" if done else "waiting"
                    operational(
                        state / "x3x7-export-watch.log", f"{host} {statuses[host]}"
                    )
                except (OSError, ValueError, RuntimeError) as error:
                    statuses[host] = "failed"
                    atomic(
                        state / f"export-{host}-ALERT", f"{host}: {error}\n".encode()
                    )
                    operational(state / "x3x7-export-watch.log", f"{host} failed")
            record(state / "x3x7-export-status.json", statuses)
            if all(value == "verified" for value in statuses.values()):
                return 0
            if once:
                return 1 if "failed" in statuses.values() else 3
            time.sleep(600)


def release_pair(out: Path) -> str | None:
    receipt = out / "release-record.json"
    if not receipt.exists():
        return None
    value = json.loads(receipt.read_bytes())
    if not isinstance(value, dict) or not isinstance(
        value.get("released_curves_sha256"), str
    ):
        raise RuntimeError("release receipt malformed")
    curves = out / "released-curves.json"
    if sha(curves) != value["released_curves_sha256"]:
        raise RuntimeError("release pair integrity failed")
    return sha(receipt)


def clean_revision(checkout: Path, expected: str | None = None) -> str:
    result = command(["git", "-C", str(checkout), "rev-parse", "HEAD"], capture=True)
    dirty = command(["git", "-C", str(checkout), "status", "--porcelain"], capture=True)
    revision = result.stdout.decode().strip()
    if (
        result.returncode
        or dirty.returncode
        or dirty.stdout
        or (expected and revision != expected)
    ):
        raise RuntimeError("checkout revision or cleanliness failed")
    return revision


def checkpoint(path: Path, key: dict[str, Any]) -> Path | None:
    if not path.exists():
        return None
    value = json.loads(path.read_bytes())
    root = Path(value["root"])
    if value["inputs"] != key or manifest(root).decode() != value["outputs"]:
        raise RuntimeError("checkpoint integrity failed")
    return root


def save_checkpoint(path: Path, key: dict[str, Any], root: Path) -> None:
    record(path, {"inputs": key, "root": str(root), "outputs": manifest(root).decode()})


def attempt(out: Path, phase: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"{phase}-", dir=out))


def scientific(study: Path, module: str, args: list[str]) -> None:
    require_run(["uv", "run", "--locked", "python", "-m", module, *args], study)


def compile_check(study: Path, root: Path, coord_out: Path) -> dict[str, int]:
    manuscript = root / "manuscript"
    require_run(
        [
            "nix",
            "shell",
            "nixpkgs#tectonic",
            "--command",
            "tectonic",
            "main.tex",
        ],
        manuscript,
    )
    results = {}
    for mode in ("draft", "submission"):
        args = [
            "uv",
            "run",
            "--locked",
            "python",
            str(study / "publications/jcss-manuscript/pipeline/paper_check.py"),
            "--root",
            str(manuscript),
            "--venue",
            "jcss",
            "--pdf",
            str(manuscript / "main.pdf"),
            "--result-values",
            str(root / "result-values.json"),
        ]
        if mode == "submission":
            args.append("--submission")
        results[mode] = command(args, cwd=study).returncode
        if results[mode]:
            atomic(
                coord_out / "chain-ALERT",
                f"paper_check {mode} failed; human review required\n".encode(),
            )
    record(root / "paper-check-status.json", results)
    return results


def select_shells(shells: str, values: dict[str, str]) -> str:
    """Select existing prose by its exported counts; never invent a verdict."""
    shells, tables = shells.split("% TABLE INPUTS:", 1)
    parts = re.split(r"(?=\\paragraph\{|\\subsection\*\{)", shells)
    selected = [parts[0]]
    for part in parts[1:]:
        title = part.split("}", 1)[0].removeprefix(r"\paragraph{")
        keys = re.findall(r"\\resultnum\{([^}]+)\}", part)
        counts = [key for key in keys if ".count." in key]
        if counts and not any(float(values[key]) > 0 for key in counts):
            continue
        if title == "X6: coverage denominators.":
            part = (
                "\n".join(
                    line
                    for line in part.splitlines()
                    if all(
                        key in values and values[key] != "unavailable"
                        for key in re.findall(r"\\resultnum\{([^}]+)\}", line)
                    )
                )
                + "\n"
            )
        if title == "X6: unavailable procedural truth." and not any(
            key.startswith("v4x.x6.")
            and key.endswith(".vs_d1")
            and value == "unavailable"
            for key, value in values.items()
        ):
            continue
        selected.append(part)
    return "".join(selected) + "\n% TABLE INPUTS:" + tables


def chain(checkout: Path, coord: Path, exports: Path, once: bool) -> int:
    out = coord / "v4-release"
    out.mkdir(mode=0o700, parents=True, exist_ok=True)
    phase = "preflight"
    with lock(out / ".post-release-chain.lock"):
        try:
            revision = clean_revision(checkout)
            aggregate_checkout = Path(
                os.environ.get(
                    "V4_AGGREGATE_CHECKOUT",
                    str(
                        Path.home()
                        / "Documents/github/worktrees/research-workbench/review"
                        / "x3x7-launch-2-3334ac0f"
                    ),
                )
            )
            clean_revision(aggregate_checkout, COMMIT)
            x5 = Path(os.environ["X5_OUT"]).resolve()
            x7 = Path(os.environ["X7_OUT"]).resolve()
            x1b = Path(os.environ["X1B_JSON"]).resolve()
            study = checkout / STUDY
            phase = "waiting-release"
            while (release_digest := release_pair(out)) is None:
                record(out / "chain-status.json", {"status": phase})
                if once:
                    return 3
                time.sleep(30)
            gate_log = coord / "v4-gate-driver.log"
            gate = next(
                line.removeprefix("sealed root: ").strip()
                for line in gate_log.read_text().splitlines()
                if line.startswith("sealed root: ")
            )
            if Path(gate).name != GATE_ID:
                raise RuntimeError("gate root identity failed")
            optional = [
                coord / "v4-allocation.json",
                coord / "v4-gate-logs/G1c-aggregate-successor.json",
                coord / "shp-aggregate-successor-1.json",
            ]
            key = {
                "release": release_digest,
                "report_commit": revision,
                "automation": sha(Path(__file__)),
                "gate": manifest(Path(gate)).decode(),
                "optional": {
                    str(path): sha(path) for path in optional if path.is_file()
                },
            }
            phase = "confirmatory"
            confirmed = checkpoint(out / "confirmatory-checkpoint.json", key)
            if confirmed is None:
                confirmed = attempt(out, phase)
                inputs = [
                    "--gate-root",
                    gate,
                    "--criteria",
                    "experiments/exploratory/detection-boundary-v4/criteria-v43.json",
                    "--curves",
                    str(out / "released-curves.json"),
                    "--release-record",
                    str(out / "release-record.json"),
                ]
                for flag, path in (
                    ("--allocation", coord / "v4-allocation.json"),
                    (
                        "--stage-successor",
                        coord / "v4-gate-logs/G1c-aggregate-successor.json",
                    ),
                ):
                    if path.is_file():
                        inputs += [flag, str(path)]
                shp = coord / "shp-aggregate-successor-1.json"
                if shp.is_file():
                    inputs += [
                        "--shp",
                        str(shp),
                        "--crosswalk",
                        "experiments/exploratory/shp-anchor-crosswalk-v1/crosswalk.json",
                    ]
                scientific(
                    study,
                    "ic_study.analysis.detection_v4_report",
                    [*inputs, "--out", str(confirmed / "report")],
                )
                shutil.copytree(
                    study / "publications/jcss-manuscript", confirmed / "manuscript"
                )
                springer = Path(
                    os.environ.get(
                        "V4_SPRINGER",
                        str(
                            Path.home()
                            / ".local/state/research-workbench/springer-template"
                        ),
                    )
                )
                for name in ("sn-jnl.cls", "sn-mathphys-num.bst"):
                    shutil.copy2(springer / name, confirmed / "manuscript" / name)
                results = confirmed / "manuscript/sections/results.tex"
                text = results.read_text()
                start = text.index("This section is reserved")
                end = text.index("\\subsection", start)
                atomic(
                    results,
                    (
                        text[:start]
                        + "This automated assembly awaits human review against "
                        "the hash-bound v4 report.\n\n" + text[end:]
                    ).encode(),
                )
                scientific(
                    study,
                    "ic_study.analysis.v4_report_export",
                    [
                        *inputs,
                        "--report",
                        str(confirmed / "report"),
                        "--manuscript",
                        str(confirmed / "manuscript"),
                        "--values",
                        str(confirmed / "result-values.json"),
                        "--catalog",
                        str(confirmed / "result-catalog.json"),
                        "--fill",
                    ],
                )
                compile_check(study, confirmed, out)
                save_checkpoint(out / "confirmatory-checkpoint.json", key, confirmed)
            phase = "waiting-exports"
            while (roots := exported_roots(coord, exports)) is None:
                record(
                    out / "chain-status.json",
                    {"status": phase, "confirmatory": str(confirmed)},
                )
                if once:
                    return 3
                time.sleep(30)
            if release_pair(out) != release_digest:
                raise RuntimeError("release changed during wait")
            clean_revision(checkout, revision)
            clean_revision(aggregate_checkout, COMMIT)
            key = {
                **key,
                "exports": [manifest(root).decode() for root in roots],
                "x5": manifest(x5).decode(),
                "x7": manifest(x7).decode(),
                "x1b": sha(x1b),
            }
            phase = "exploratory"
            final = checkpoint(out / "exploratory-checkpoint.json", key)
            if final is None:
                final = attempt(out, phase)
                aggregates = final / "aggregates"
                aggregates.mkdir(mode=0o700)
                for name in ("x3", "x4", "x6", "x5", "x7"):
                    sources = (
                        roots
                        if name in ("x3", "x4", "x6")
                        else [x5 if name == "x5" else x7]
                    )
                    scientific(
                        aggregate_checkout / STUDY,
                        f"ic_study.simulation.v4_exploratory_{name}",
                        [
                            "aggregate",
                            *[a for p in sources for a in ("--out", str(p))],
                            "--output",
                            str(aggregates / f"{name}.json"),
                        ],
                    )
                comparisons = final / "comparisons.json"
                scientific(
                    study,
                    "ic_study.analysis.v4_exploratory_comparisons",
                    [
                        "--curves",
                        str(out / "released-curves.json"),
                        "--release-record",
                        str(out / "release-record.json"),
                        "--x1b",
                        str(x1b),
                        *[
                            a
                            for n in ("x5", "x3", "x4")
                            for a in (f"--{n}", str(aggregates / f"{n}.json"))
                        ],
                        "--output",
                        str(comparisons),
                    ],
                )
                shutil.copytree(confirmed / "manuscript", final / "manuscript")
                args = [
                    a
                    for n in ("x3", "x4", "x6", "x7")
                    for a in (f"--{n}", str(aggregates / f"{n}.json"))
                ]
                args += [
                    "--comparisons",
                    str(comparisons),
                    "--manuscript",
                    str(final / "manuscript"),
                    "--confirmatory-values",
                    str(confirmed / "result-catalog.json"),
                    "--values",
                    str(final / "result-values.json"),
                    "--catalog",
                    str(final / "catalog.json"),
                ]
                scientific(study, "ic_study.analysis.v4_exploratory_export", args)
                values = json.loads((final / "catalog.json").read_bytes())["values"]
                shells = (
                    study
                    / "publications/jcss-manuscript/pipeline/drafts/2026-09-30"
                    / "exploratory-results-shells.tex"
                ).read_text()
                atomic(
                    final / "manuscript/sections/event-exploratory.tex",
                    select_shells(shells, values).encode(),
                )
                main = final / "manuscript/main.tex"
                text = main.read_text()
                atomic(
                    main,
                    text.replace(
                        r"\end{document}",
                        r"\input{sections/event-exploratory}"
                        + "\n"
                        + r"\end{document}",
                    ).encode(),
                )
                scientific(
                    study, "ic_study.analysis.v4_exploratory_export", [*args, "--fill"]
                )
                compile_check(study, final, out)
                save_checkpoint(out / "exploratory-checkpoint.json", key, final)
            checks = json.loads((final / "paper-check-status.json").read_bytes())
            record(
                out / "chain-status.json",
                {
                    "status": "awaiting-human-review",
                    "final": str(final),
                    "pdf": str(final / "manuscript/main.pdf"),
                    "paper_check": checks,
                },
            )
            operational(out / "chain.log", "awaiting-human-review")
            return 1 if any(checks.values()) else 0
        except (OSError, ValueError, RuntimeError, KeyError, StopIteration) as error:
            atomic(
                out / "chain-ALERT",
                f"{phase}: {type(error).__name__}: {error}\n".encode(),
            )
            record(out / "chain-status.json", {"status": "failed", "phase": phase})
            operational(out / "chain.log", f"{phase} failed")
            return 1


def main() -> int:
    os.umask(0o077)
    for name in (
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ):
        os.environ[name] = "1"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("watch", "chain"))
    parser.add_argument("checkout", nargs="?", type=Path)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--verify-local", action="store_true")
    args = parser.parse_args()
    coord = Path(
        os.environ.get(
            "V4_COORD",
            str(Path.home() / ".local/state/research-workbench/coord-20260925"),
        )
    ).resolve()
    exports = Path(
        os.environ.get(
            "V4_EXPORT_ROOT",
            str(
                Path.home()
                / ".local/state/research-workbench/sealed-v4-exploratory-x3-x7"
            ),
        )
    ).resolve()
    try:
        if args.mode == "watch":
            return watch(coord, exports, args.once, args.verify_local)
        if args.checkout is None:
            parser.error("chain requires the report checkout")
        return chain(args.checkout.resolve(), coord, exports, args.once)
    except (OSError, ValueError, RuntimeError):
        print(
            "automation refused; check operational status and alerts", file=sys.stderr
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
