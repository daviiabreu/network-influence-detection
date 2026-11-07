"""Run the study's synthetic engineering suite with an isolated home."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1] / "studies/ic-2026-2027"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ic-study-tests-") as temporary:
        home = Path(temporary)
        env = dict(
            os.environ,
            HOME=str(home),
            XDG_CACHE_HOME=str(home / "cache"),
            XDG_CONFIG_HOME=str(home / "config"),
            XDG_DATA_HOME=str(home / "data"),
            MPLCONFIGDIR=str(home / "matplotlib"),
            IC_REPRO_ARTIFACT_ROOT=str(home / "unavailable-artifacts"),
        )
        return subprocess.run(
            [sys.executable, "-m", "pytest", *sys.argv[1:]],
            cwd=STUDY,
            env=env,
            check=False,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
