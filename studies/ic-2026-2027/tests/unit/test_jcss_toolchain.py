"""Editorial tooling accepts an external engine and preserves source directories."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest

JOURNAL = Path(__file__).resolve().parents[2] / "publications/jcss-journal"
sys.path.insert(0, str(JOURNAL))
import build as journal_build  # noqa: E402
from toolchain import Toolchain, arguments, configured  # noqa: E402


def test_cli_engine_and_cache_reach_the_compiler(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    engine = tmp_path / "custom-tectonic"
    engine.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "print(json.dumps({'args': sys.argv[1:], "
        "'cache': os.environ['TECTONIC_CACHE_DIR']}))\n"
    )
    engine.chmod(0o700)
    template, cache, output = (tmp_path / name for name in ("template", "cache", "out"))
    for directory in (template, cache, output):
        directory.mkdir()
    for name in ("sn-jnl.cls", "sn-mathphys-num.bst"):
        (template / name).write_text("synthetic fixture")
    monkeypatch.setenv("IC_STUDY_TECTONIC", "unavailable-default")
    parser = argparse.ArgumentParser()
    arguments(parser)
    config = configured(
        parser.parse_args(
            [
                "--tectonic",
                str(engine),
                "--template",
                str(template),
                "--cache",
                str(cache),
            ]
        )
    )
    config.validate()
    assert journal_build.compile_tex(output, "main", config)
    record = json.loads((output / "main.tectonic.txt").read_text())
    assert record["args"] == [
        "--only-cached",
        "--keep-intermediates",
        "--keep-logs",
        "main.tex",
    ]
    assert record["cache"] == str(cache.resolve())


def test_unavailable_toolchain_does_not_replace_an_existing_build(
    tmp_path: Path,
) -> None:
    build = tmp_path / "existing"
    build.mkdir()
    (build / "sentinel").write_text("preserve")
    result = subprocess.run(
        [
            sys.executable,
            str(JOURNAL / "build.py"),
            "--out",
            str(build),
            "--template",
            str(tmp_path / "missing"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "missing Springer template" in result.stderr
    assert (build / "sentinel").read_text() == "preserve"


@pytest.mark.parametrize("directory", [JOURNAL, JOURNAL.parent, JOURNAL / "sections"])
def test_build_refuses_publication_sources(directory: Path, tmp_path: Path) -> None:
    config = Toolchain(tmp_path, tmp_path, tmp_path)
    with pytest.raises(ValueError, match="outside the publication source"):
        journal_build.stage(directory, config)
