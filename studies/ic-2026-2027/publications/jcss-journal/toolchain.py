"""Configure external publication tools without binding sources to one host."""

from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

LEGACY_STATE = Path.home() / ".local/state/research-workbench"
LEGACY_TECTONIC = Path(
    "/nix/store/pxrhhj0zcl8ywp8ym4jw6fj7rrckfvcc-tectonic-wrapped-0.17.0/bin/tectonic"
)


def location(variable: str, fallback: Path, legacy: Path) -> Path:
    configured = os.environ.get(variable)
    if configured:
        return Path(configured).expanduser()
    return legacy if legacy.is_dir() else fallback


@dataclass(frozen=True)
class Toolchain:
    template: Path
    tectonic: Path
    cache: Path
    only_cached: bool = True

    @classmethod
    def defaults(cls) -> Toolchain:
        data = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
        cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        engine = os.environ.get("IC_STUDY_TECTONIC") or shutil.which("tectonic")
        if engine is None:
            engine = str(LEGACY_TECTONIC) if LEGACY_TECTONIC.is_file() else "tectonic"
        return cls(
            template=location(
                "IC_STUDY_SPRINGER_TEMPLATE",
                data / "ic-study/springer-template",
                LEGACY_STATE / "springer-template",
            ),
            tectonic=Path(shutil.which(engine) or engine).expanduser(),
            cache=(
                Path(os.environ["TECTONIC_CACHE_DIR"]).expanduser()
                if "TECTONIC_CACHE_DIR" in os.environ
                and "IC_STUDY_TECTONIC_CACHE" not in os.environ
                else location(
                    "IC_STUDY_TECTONIC_CACHE",
                    cache / "ic-study/tectonic",
                    LEGACY_STATE / "tectonic-cache",
                )
            ),
        )

    def validate(self) -> None:
        for name in ("sn-jnl.cls", "sn-mathphys-num.bst"):
            if not (self.template / name).is_file():
                raise ValueError(
                    f"missing Springer template file: {self.template / name}"
                )
        if not self.tectonic.is_file() or not os.access(self.tectonic, os.X_OK):
            raise ValueError(
                "Tectonic is unavailable; set --tectonic or IC_STUDY_TECTONIC"
            )
        if self.only_cached and not self.cache.is_dir():
            raise ValueError(
                "Tectonic cache is unavailable; set --cache or warm it first"
            )

    def environment(self) -> dict[str, str]:
        return dict(os.environ, TECTONIC_CACHE_DIR=str(self.cache.resolve()))

    def command(self, name: str) -> list[str]:
        return [
            str(self.tectonic.resolve()),
            *(["--only-cached"] if self.only_cached else []),
            "--keep-intermediates",
            "--keep-logs",
            name,
        ]


def arguments(parser: argparse.ArgumentParser) -> None:
    defaults = Toolchain.defaults()
    parser.add_argument("--template", type=Path, default=defaults.template)
    parser.add_argument("--tectonic", type=Path, default=defaults.tectonic)
    parser.add_argument("--cache", type=Path, default=defaults.cache)
    parser.add_argument(
        "--allow-downloads",
        action="store_true",
        help="allow Tectonic to populate its cache (offline by default)",
    )


def configured(args: argparse.Namespace) -> Toolchain:
    engine = str(args.tectonic.expanduser())
    return Toolchain(
        args.template.expanduser().resolve(),
        Path(shutil.which(engine) or engine).resolve(),
        args.cache.expanduser().resolve(),
        only_cached=not args.allow_downloads,
    )
