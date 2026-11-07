#!/usr/bin/env python3
"""Build the JCSS article and Online Resource 1, then run check.py on the build."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from toolchain import Toolchain, arguments, configured

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parents[1]
SOURCES = (
    "main.tex",
    "esm.tex",
    "references.bib",
    "sections",
    "esm",
    "generated",
    "values",
)

sys.path.insert(0, str(STUDY / "experiments"))
from package_jcss_submission import bibliography_style  # noqa: E402


def stage(out: Path, toolchain: Toolchain) -> None:
    if ROOT.is_relative_to(out.resolve()) or out.resolve().is_relative_to(ROOT):
        raise ValueError("build directory must be outside the publication source tree")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for name in SOURCES:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, out / name)
        elif source.is_file():
            shutil.copy2(source, out / name)
    shutil.copy2(toolchain.template / "sn-jnl.cls", out / "sn-jnl.cls")
    style = (toolchain.template / "sn-mathphys-num.bst").read_bytes()
    (out / "sn-mathphys-num.bst").write_bytes(bibliography_style(style))


def compile_tex(out: Path, name: str, toolchain: Toolchain) -> bool:
    result = subprocess.run(
        toolchain.command(f"{name}.tex"),
        cwd=out,
        env=toolchain.environment(),
        capture_output=True,
        text=True,
    )
    transcript = result.stdout + result.stderr
    (out / f"{name}.tectonic.txt").write_text(transcript)
    if result.returncode:
        errors = [line for line in transcript.splitlines() if line.startswith("error")]
        print(f"ERROR: {name}.tex did not compile", file=sys.stderr)
        print("\n".join(errors[-12:]), file=sys.stderr)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(tempfile.gettempdir()) / "ic-study-jcss-journal-build",
        help="scratch build directory, replaced on every run",
    )
    parser.add_argument(
        "--submission",
        action="store_true",
        help="fail on placeholders and unresolved journal keys",
    )
    arguments(parser)
    args = parser.parse_args()
    out = args.out.resolve()
    toolchain = configured(args)
    try:
        toolchain.validate()
        stage(out, toolchain)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for name in ("esm", "main", "esm"):
        if not compile_tex(out, name, toolchain):
            return 1
    print(f"built {out / 'main.pdf'} and {out / 'esm.pdf'}")
    command = [sys.executable, str(ROOT / "check.py"), "--build", str(out)]
    if args.submission:
        command.append("--submission")
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
