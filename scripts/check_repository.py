"""Check the independently installable study without reading research inputs."""

from __future__ import annotations

import ast
import re
import tomllib
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies/ic-2026-2027"
ACTIVE_DOCS = (
    "README.md",
    "AGENTS.md",
    "docs/architecture.md",
    "docs/reproducibility.md",
    "docs/publication-toolchain.md",
    "docs/publication-selection.md",
    "docs/process/engineering-validation.md",
    "contracts/README.md",
    "studies/ic-2026-2027/README.md",
    "studies/ic-2026-2027/research/README.md",
    "studies/ic-2026-2027/tests/README.md",
)
REQUIRED = (
    *ACTIVE_DOCS,
    "studies/ic-2026-2027/AGENTS.md",
    "studies/ic-2026-2027/CONTEXT.md",
    "studies/ic-2026-2027/pyproject.toml",
    "studies/ic-2026-2027/uv.lock",
    "studies/ic-2026-2027/src/ic_study/__init__.py",
    "studies/ic-2026-2027/publications/jcss-journal/toolchain.py",
    "scripts/test_hermetic.py",
    "scripts/build_and_smoke.sh",
)


def check() -> list[str]:
    errors = [
        f"missing path: {name}" for name in REQUIRED if not (ROOT / name).is_file()
    ]
    if errors:
        return errors
    if (ROOT / "workbench").exists() or (ROOT / "pyproject.toml").exists():
        errors.append("the repository must contain only the independently locked study")
    withheld = (
        ROOT / "historical",
        STUDY / "research/agents",
        STUDY / "research/decisions",
        STUDY / "research/venues",
        STUDY
        / "experiments/exploratory/detection-boundary-v4-exploratory/POST-RELEASE.md",
        STUDY
        / "publications/jcss-manuscript/pipeline/drafts/2026-09-30"
        / "ai-disclosure-evidence.md",
    )
    errors.extend(
        f"private material in public selection: {path.relative_to(ROOT)}"
        for path in withheld
        if path.exists()
    )
    project = tomllib.loads((STUDY / "pyproject.toml").read_text())
    lock = tomllib.loads((STUDY / "uv.lock").read_text())
    if project["project"]["name"] != "ic-study" or "workspace" in project.get(
        "tool", {}
    ).get("uv", {}):
        errors.append("unexpected study project or uv workspace")
    names = {package["name"] for package in lock["package"]}
    if "ic-study" not in names or "research-workbench" in names:
        errors.append("lockfile is not independent of the workflow framework")
    for directory in (STUDY / "src", ROOT / "scripts"):
        for path in sorted(directory.rglob("*.py")):
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                imports: list[str] = []
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports = [node.module]
                if any(name.split(".")[0] == "research_workbench" for name in imports):
                    errors.append(f"framework import: {path.relative_to(ROOT)}")
    for name in ACTIVE_DOCS:
        path = ROOT / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            target = unquote(target.split("#", 1)[0])
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            destination = (path.parent / target).resolve()
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f"unresolved active link: {name}: {target}")
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("\n".join(errors))
        return 1
    print("study structure: passed (metadata, imports and active documentation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
