"""Release packaging uses new artificial inputs, never research state."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import runpy
import subprocess
import sys
import zlib
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

STUDY = Path(__file__).resolve().parents[2]
BUILDER = STUDY / "publications/reproducibility/build_ic_release.py"
PREFIX = "studies/ic-2026-2027/"
WRAPPER = "experiments/exploratory/detection-boundary-v4/release_on_completion.py"
GENERATOR = "src/ic_study/analysis/v4_report_synthetic.py"
ASSEMBLY_SOURCES = (
    "src/ic_study/analysis/v4_public_aggregates.py",
    "publications/reproducibility/verify_short_path.py",
    "src/ic_study/analysis/v4_manuscript_assembly.py",
    "src/ic_study/analysis/v4_manuscript_assembly_derive.py",
    "src/ic_study/analysis/v4_manuscript_assembly_facts.py",
    "src/ic_study/analysis/v4_manuscript_assembly_rules.json",
    "src/ic_study/analysis/v4_manuscript_assembly_facts.schema.json",
    "publications/jcss-manuscript/pipeline/ASSEMBLY.md",
    "publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells.tex",
    "publications/jcss-manuscript/pipeline/drafts/2026-09-28/results-shells-abstract.md",
    "publications/jcss-manuscript/pipeline/drafts/2026-09-30/discussion-conclusion-shells.tex",
    "publications/jcss-manuscript/pipeline/drafts/2026-09-30/exploratory-results-shells.tex",
)
ROLES = (
    "confirmatory",
    "release-wrapper",
    "x3-x7",
    "legacy-x5-x7",
    "shp-code",
    "shp-freeze",
    "v44-successor",
    "bridge",
    "reporting-export",
)
WITHHELD = WRAPPER


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        [
            "git",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "commit.gpgsign=false",
            "-C",
            str(root),
            *args,
        ],
        text=True,
        env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull},
    ).strip()


def cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BUILDER), *args],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo = tmp_path / "repository"
    repo.mkdir()
    git(repo, "init", "--quiet")
    git(repo, "config", "user.name", "Synthetic fixture")
    git(repo, "config", "user.email", "fixture@example.invalid")
    contents = {
        "README.md": "Artificial study\n",
        ".python-version": "3.12.13\n",
        "pyproject.toml": '[project]\nname="fixture"\nversion="0"\n',
        "uv.lock": 'version=1\n[[package]]\nname="numpy"\nversion="0"\n',
        "src/ic_study/__init__.py": 'VERSION = "old"\n',
        WRAPPER: "# Artificial packaging fixture; never execute.\n",
        GENERATOR: "# Old artificial generator.\n",
        **dict.fromkeys(ASSEMBLY_SOURCES, "Artificial packaging resource\n"),
    }
    for name, content in contents.items():
        path = repo / PREFIX / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    (repo / "excluded.txt").write_text("must never enter the package")
    git(repo, "add", ".")
    git(repo, "commit", "--quiet", "-m", "Create artificial source")
    old = git(repo, "rev-parse", "HEAD")
    (repo / PREFIX / "src/ic_study/__init__.py").write_text('VERSION = "new"\n')
    (repo / PREFIX / GENERATOR).write_text("# Selected artificial generator.\n")
    git(repo, "add", ".")
    git(repo, "commit", "--quiet", "-m", "Change artificial source")
    new = git(repo, "rev-parse", "HEAD")
    plan = tmp_path / "plan.json"
    revisions = [
        arg
        for role in ROLES
        for arg in (
            "--revision",
            f"{role}={new if role == 'reporting-export' else old}",
        )
    ]
    result = cli(
        "plan",
        "--repository",
        str(repo),
        "--mode",
        "synthetic",
        "--output",
        str(plan),
        *revisions,
    )
    assert result.returncode == 0, result.stderr
    return repo, plan, tmp_path / "bundle"


def build(
    fixture: tuple[Path, Path, Path], *extra: str
) -> subprocess.CompletedProcess[str]:
    repo, plan, output = fixture
    return cli(
        "build",
        "--repository",
        str(repo),
        "--plan",
        str(plan),
        "--output",
        str(output),
        *extra,
    )


def test_offline_bundle_retains_selected_historical_sources(
    fixture: tuple[Path, Path, Path],
) -> None:
    repo, plan, output = fixture
    result = build(fixture)
    assert result.returncode == 0, result.stderr
    assert (
        output / "sources/confirmatory" / PREFIX / "src/ic_study/__init__.py"
    ).read_text() == 'VERSION = "old"\n'
    assert (
        output / "sources/reporting-export" / PREFIX / "src/ic_study/__init__.py"
    ).read_text() == 'VERSION = "new"\n'
    metadata = json.loads((output / "ic-release-manifest.json").read_text())
    assert metadata["scientific_acceptance"] is False
    assert metadata["regeneration_performed"] is False
    assert metadata["mode"] == "synthetic"
    assert metadata["license_decisions"] == "MIT"
    assert metadata["environments"]["confirmatory"]["packages"] == {"numpy": "0"}
    assert (
        (output / "LICENSE")
        .read_bytes()
        .startswith(b"MIT License\n\nCopyright (c) 2026 Davi Abreu da Silveira\n")
    )
    selection = json.loads(plan.read_text())
    assert {entry["license_status"] for entry in selection["files"]} == {"MIT"}
    old = selection["revisions"]["confirmatory"]
    assert (
        git(output / "history", "show", f"{old}:{PREFIX}src/ic_study/__init__.py")
        == 'VERSION = "old"'
    )
    with pytest.raises(subprocess.CalledProcessError):
        git(output / "history", "show", f"{old}:excluded.txt")
    repo.rename(repo.with_name("unavailable-repository"))
    result = cli("verify", "--bundle", str(output))
    assert result.returncode == 0, result.stderr
    assert "integrity_verified" in result.stdout
    assert "verify" in (output / "REPRODUCE.md").read_text()


def update_plan(path: Path, edit: Any) -> None:
    plan = json.loads(path.read_text())
    edit(plan)
    path.write_text(json.dumps(plan))


@pytest.mark.parametrize(
    "path",
    [
        PREFIX + "unapproved.py",
        "../escaped.json",
        "/absolute.json",
        "sealed-v4-confirmatory/result.json",
        "v4-tier-logs/result.json",
        "v4-gate-logs/result.json",
        "restricted/source.json",
        ".env",
        PREFIX
        + "experiments/exploratory/detection-boundary-v4-exploratory/POST-RELEASE.md",
    ],
)
def test_rejects_unapproved_or_unsafe_selection(
    fixture: tuple[Path, Path, Path],
    path: str,
) -> None:
    _, plan, output = fixture
    update_plan(plan, lambda p: p["files"][0].update(path=path))
    result = build(fixture)
    assert result.returncode == 2
    assert not output.exists()


def test_rejects_hash_change(fixture: tuple[Path, Path, Path]) -> None:
    _, plan, output = fixture
    update_plan(plan, lambda p: p["files"][0].update(sha256="0" * 64))
    assert build(fixture).returncode == 2
    assert not output.exists()


@pytest.mark.parametrize("missing", ["role", "object", "lock"])
def test_rejects_missing_revision_or_environment(
    fixture: tuple[Path, Path, Path],
    missing: str,
) -> None:
    _, plan, output = fixture
    if missing == "role":
        update_plan(plan, lambda p: p["revisions"].pop("shp-freeze"))
    elif missing == "object":
        update_plan(plan, lambda p: p["revisions"].update(confirmatory="1" * 40))
    else:
        update_plan(
            plan,
            lambda p: p.update(
                files=[f for f in p["files"] if f["path"] != PREFIX + "uv.lock"]
            ),
        )
    assert build(fixture).returncode == 2
    assert not output.exists()


@pytest.mark.parametrize("kind", ["directory", "file", "symlink"])
def test_never_overwrites_existing_output(
    fixture: tuple[Path, Path, Path],
    kind: str,
) -> None:
    _, _, output = fixture
    if kind == "directory":
        output.mkdir()
        (output / "retained.txt").write_text("retained")
    elif kind == "file":
        output.write_text("retained")
    else:
        output.symlink_to(output.with_name("absent"))
    result = build(fixture)
    assert result.returncode == 2
    assert "Output already exists" in result.stderr
    if kind == "directory":
        assert (output / "retained.txt").read_text() == "retained"
    elif kind == "file":
        assert output.read_text() == "retained"
    else:
        assert output.is_symlink()


def add_artifact(plan: Path, name: str, content: bytes) -> None:
    update_plan(
        plan,
        lambda p: p["files"].append(
            {
                "root": "release",
                "role": "approved-artifact",
                "path": name,
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "license_status": "MIT",
            }
        ),
    )


@pytest.mark.parametrize("kind", ["file", "directory", "root"])
def test_rejects_symlink_outside_release_root(
    fixture: tuple[Path, Path, Path],
    tmp_path: Path,
    kind: str,
) -> None:
    _, plan, output = fixture
    root = tmp_path / "approved-release"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "manifest.json").write_bytes(b"{}")
    name = "report/manifest.json" if kind == "directory" else "x3.json"
    add_artifact(plan, name, b"{}")
    if kind == "directory":
        (root / "report").symlink_to(outside, target_is_directory=True)
    elif kind == "root":
        root.rmdir()
        root.symlink_to(outside, target_is_directory=True)
    else:
        (root / name).symlink_to(outside / "manifest.json")
    result = build(fixture, "--release-root", str(root))
    assert result.returncode == 2
    assert "Symlink" in result.stderr or "real directory" in result.stderr
    assert not output.exists()


def test_release_pair_and_offline_tamper_gate(
    fixture: tuple[Path, Path, Path],
    tmp_path: Path,
) -> None:
    _, plan, output = fixture
    root = tmp_path / "approved-release"
    root.mkdir()
    curves = b'{"curves": [], "inventory": {}}\n'
    receipt = json.dumps(
        {
            "released_curves_sha256": hashlib.sha256(curves).hexdigest(),
            "condition": "declared-close",
            "released_utc": "2026-10-19T02:59:00Z",
            "script_sha256": hashlib.sha256(
                b"# Selected artificial generator.\n"
            ).hexdigest(),
        }
    ).encode()
    for name, content in (
        ("released-curves.json", curves),
        ("release-record.json", receipt),
    ):
        (root / name).write_bytes(content)
        add_artifact(plan, name, content)
    assert build(fixture, "--release-root", str(root)).returncode == 0
    result = cli("verify", "--bundle", str(output), "--manifest-sha256", "0" * 64)
    assert result.returncode == 2
    (output / "artifacts/released-curves.json").write_bytes(b"tampered")
    result = cli("verify", "--bundle", str(output))
    assert result.returncode == 2
    assert "hash/size mismatch" in result.stderr


def test_rejects_incomplete_release_pair(
    fixture: tuple[Path, Path, Path],
    tmp_path: Path,
) -> None:
    _, plan, output = fixture
    root = tmp_path / "approved-release"
    root.mkdir()
    (root / "release-record.json").write_bytes(b"{}")
    add_artifact(plan, "release-record.json", b"{}")
    assert build(fixture, "--release-root", str(root)).returncode == 2
    assert not output.exists()


def test_rejects_different_executed_wrapper(
    fixture: tuple[Path, Path, Path],
    tmp_path: Path,
) -> None:
    _, plan, output = fixture
    root = tmp_path / "approved-release"
    root.mkdir()
    curves = b"{}"
    receipt = json.dumps(
        {
            "released_curves_sha256": hashlib.sha256(curves).hexdigest(),
            "script_sha256": "0" * 64,
            "condition": "declared-close",
            "released_utc": "2026-10-19T02:59:00Z",
        }
    ).encode()
    for name, content in (
        ("released-curves.json", curves),
        ("release-record.json", receipt),
    ):
        (root / name).write_bytes(content)
        add_artifact(plan, name, content)
    result = build(fixture, "--release-root", str(root))
    assert result.returncode == 2
    assert "Synthetic release generator" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize("kind", ["unapproved-file", "symlink"])
def test_offline_rejects_extra_bundle_content(
    fixture: tuple[Path, Path, Path],
    kind: str,
) -> None:
    _, _, output = fixture
    assert build(fixture).returncode == 0
    if kind == "symlink":
        (output / "extra").symlink_to(output.with_name("absent"))
    else:
        (output / "extra.txt").write_text("unapproved")
    assert cli("verify", "--bundle", str(output)).returncode == 2


def test_rejects_git_symlink_without_reading_target(
    fixture: tuple[Path, Path, Path],
) -> None:
    repo, plan, output = fixture
    source = repo / PREFIX / "src/ic_study/__init__.py"
    source.unlink()
    source.symlink_to(repo.with_name("missing-private-target"))
    git(repo, "add", ".")
    git(repo, "commit", "--quiet", "-m", "Create artificial symlink")
    revision = git(repo, "rev-parse", "HEAD")
    update_plan(plan, lambda p: p["revisions"].update({"reporting-export": revision}))
    result = build(fixture)
    assert result.returncode == 2
    assert "symlinks are forbidden" in result.stderr
    assert not output.exists()


def test_rejects_extra_history_blob_even_when_inventory_hashes_match(
    fixture: tuple[Path, Path, Path],
) -> None:
    _, _, output = fixture
    assert build(fixture).returncode == 0
    raw = b"blob 17\0unapproved bytes!"
    object_id = hashlib.sha1(raw).hexdigest()
    name = f"history/.git/objects/{object_id[:2]}/{object_id[2:]}"
    content = zlib.compress(raw)
    path = output / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    manifest_path = output / "ic-release-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"].append(
        {
            "path": name,
            "sha256": hashlib.sha256(content).hexdigest(),
            "bytes": len(content),
        }
    )
    manifest_path.write_text(json.dumps(manifest))
    (output / "ic-release-manifest.sha256").write_text(
        hashlib.sha256(manifest_path.read_bytes()).hexdigest() + "\n"
    )
    result = cli("verify", "--bundle", str(output))
    assert result.returncode == 2
    assert "history" in result.stderr.lower()


def rehash(output: Path, name: str) -> None:
    """Re-inventory one edited file so only the semantic checks can object."""
    manifest_path = output / "ic-release-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    content = (output / name).read_bytes()
    for entry in manifest["files"]:
        if entry["path"] == name:
            entry.update(sha256=hashlib.sha256(content).hexdigest(), bytes=len(content))
    manifest_path.write_text(json.dumps(manifest))
    (output / "ic-release-manifest.sha256").write_text(
        hashlib.sha256(manifest_path.read_bytes()).hexdigest() + "\n"
    )


def test_license_text_is_bound(fixture: tuple[Path, Path, Path]) -> None:
    _, _, output = fixture
    assert build(fixture).returncode == 0
    (output / "LICENSE").write_bytes(b"All rights reserved.\n")
    rehash(output, "LICENSE")
    result = cli("verify", "--bundle", str(output))
    assert result.returncode == 2
    assert "license" in result.stderr


def test_withheld_source_is_recorded_not_published(
    fixture: tuple[Path, Path, Path],
) -> None:
    repo, plan, output = fixture
    plan.unlink()
    summary = json.loads(
        cli(
            "plan",
            "--repository",
            str(repo),
            "--mode",
            "synthetic",
            "--output",
            str(plan),
            *(
                arg
                for role in ROLES
                for arg in ("--revision", f"{role}={git(repo, 'rev-parse', 'HEAD')}")
            ),
            "--withhold",
            f"{PREFIX}{WITHHELD}=private-host-name,coordination-path",
        ).stdout
    )
    assert summary == {
        "files": len(ROLES) * 18,
        "redacted": 0,
        "status": "source_selection_prepared",
        "withheld": len(ROLES),
    }
    withheld = json.loads(plan.read_text())["withheld"]
    assert {tuple(entry["reasons"]) for entry in withheld} == {
        ("coordination-path", "private-host-name")
    }
    blob = git(repo, "rev-parse", f"HEAD:{PREFIX}{WITHHELD}")
    assert {entry["git_blob"] for entry in withheld} == {blob}
    assert build(fixture).returncode == 0
    objects = output / "history/.git/objects"
    assert not (output / "sources/reporting-export" / PREFIX / WITHHELD).exists()
    assert not (objects / blob[:2] / blob[2:]).exists()
    parent = git(repo, "rev-parse", "HEAD^")
    assert not (objects / parent[:2] / parent[2:]).exists()
    assert cli("verify", "--bundle", str(output)).returncode == 0
    update_plan(
        output / "plan.json", lambda p: p["withheld"][0].update(git_blob="1" * 40)
    )
    rehash(output, "plan.json")
    result = cli("verify", "--bundle", str(output))
    assert result.returncode == 2
    assert "withheld record" in result.stderr


def test_rejects_withholding_an_absent_or_environment_source(
    fixture: tuple[Path, Path, Path],
) -> None:
    repo, plan, _ = fixture
    for path, message in (
        (PREFIX + "src/ic_study/py.typed", "absent from every revision"),
        (PREFIX + "uv.lock", "Incomplete source/environment"),
    ):
        plan.unlink(missing_ok=True)
        result = cli(
            "plan",
            "--repository",
            str(repo),
            "--mode",
            "synthetic",
            "--output",
            str(plan),
            *(
                arg
                for role in ROLES
                for arg in ("--revision", f"{role}={git(repo, 'rev-parse', 'HEAD')}")
            ),
            "--withhold",
            f"{path}=excluded-by-decision",
        )
        assert result.returncode == 2
        assert message in result.stderr


def test_required_source_may_be_withheld_with_its_identity() -> None:
    builder = module(BUILDER)
    files, withheld = [], []
    for role in builder.ROLES:
        for name in (*builder.ENVIRONMENT, "src/ic_study/__init__.py"):
            files.append(
                {
                    "root": "repository",
                    "role": role,
                    "path": PREFIX + name,
                    "sha256": "0" * 64,
                    "bytes": 0,
                    "license_status": "MIT",
                }
            )
        for name in builder.REQUIRED[role]:
            entry = {
                "role": role,
                "path": PREFIX + name,
                "sha256": "0" * 64,
                "bytes": 0,
            }
            if role == "shp-code":
                withheld.append(
                    entry | {"git_blob": "2" * 40, "reasons": ["absolute-home-path"]}
                )
            else:
                files.append(entry | {"root": "repository", "license_status": "MIT"})
    plan = {
        "schema": builder.PLAN_SCHEMA,
        "mode": "source-only",
        "revisions": {
            role: builder.PINNED.get(role, "3" * 40) for role in builder.ROLES
        },
        "files": files,
        "withheld": withheld,
        "redacted": [],
    }
    builder.validate_plan(plan)
    plan["withheld"] = withheld[1:]
    with pytest.raises(ValueError, match="Incomplete source"):
        builder.validate_plan(plan)


GUIDE = "research/questions/exploration/2026-09-24-parallel/shp-reliability-guide.md"
CODE = "src/ic_study/analysis/shp_reliability.py"
PRIVATE = (b"fixture-host", b"fixture-user", b"coord-fixture", b"fixture-person")
PRIVATE_SOURCES = {
    GUIDE: "Run on fixture-host as /Users/fixture-user/bin/tool.\n"
    "Coordination files stay in ~/.state/coord-fixture/notes.json.\n"
    "Write to fixture-person@example.invalid or author@example.org.\n",
    CODE: "from pathlib import Path\n\n"
    'DEFAULT_DATA_DIR = Path("/Users/fixture-user/data")\n'
    'HOST = "fixture-host"\n'
    "SIZE = len(HOST)\n",
}
REDACTED_GUIDE = (
    "Run on [private-host] as [home]/bin/tool.\n"
    "Coordination files stay in [coordination-dir]/notes.json.\n"
    "Write to [private-email] or author@example.org.\n"
)
REASONS = {
    GUIDE: "absolute-home-path,coordination-path,non-allowed-email,private-host-name",
    CODE: "absolute-home-path,private-host-name",
}
RULES = [
    {"category": "coordination-path", "pattern": r"~/\.state/coord-fixture"},
    {
        "category": "absolute-home-path",
        "pattern": r'Path\("/Users/[a-z-]+/',
        "form": "code",
    },
    {"category": "absolute-home-path", "pattern": r"/Users/[a-z-]+"},
    {"category": "private-host-name", "pattern": "fixture-host"},
    {
        "category": "non-allowed-email",
        "pattern": r"(?<![\w.+-])(?!author@example\.org)[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
    },
]


def write_rules(path: Path, rules: list[dict[str, str]]) -> Path:
    path.write_text(json.dumps({"schema": "ic-redaction-rules-v1", "rules": rules}))
    return path


def plan_redactions(
    repo: Path, plan: Path, rules: Path | None, *redactions: str
) -> subprocess.CompletedProcess[str]:
    plan.unlink(missing_ok=True)
    head = git(repo, "rev-parse", "HEAD")
    return cli(
        "plan",
        "--repository",
        str(repo),
        "--mode",
        "synthetic",
        "--output",
        str(plan),
        *(arg for role in ROLES for arg in ("--revision", f"{role}={head}")),
        *(arg for item in redactions for arg in ("--redact", item)),
        *(("--redaction-rules", str(rules)) if rules else ()),
    )


@pytest.fixture
def redaction(
    fixture: tuple[Path, Path, Path], tmp_path: Path
) -> tuple[Path, Path, Path, Path]:
    repo, plan, output = fixture
    for name, content in PRIVATE_SOURCES.items():
        path = repo / PREFIX / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    git(repo, "add", ".")
    git(repo, "commit", "--quiet", "-m", "Add artificial private spans")
    rules = write_rules(tmp_path / "private-rules.json", RULES)
    result = plan_redactions(
        repo, plan, rules, *(f"{PREFIX}{name}={REASONS[name]}" for name in REASONS)
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["redacted"] == 2 * len(ROLES)
    return repo, plan, output, rules


def bundle_bytes(output: Path) -> list[bytes]:
    contents = []
    for path in output.rglob("*"):
        contents.append(str(path.relative_to(output)).encode())
        if path.is_file():
            content = path.read_bytes()
            contents.append(
                zlib.decompress(content)
                if "history/.git/objects/" in str(path)
                else content
            )
    return contents


def test_redacted_copy_is_published_and_bound_to_the_original(
    redaction: tuple[Path, Path, Path, Path],
) -> None:
    repo, plan, output, rules = redaction
    record = json.loads(plan.read_text())
    assert not any(private in plan.read_bytes() for private in PRIVATE)
    for entry in record["redacted"]:
        name = entry["path"].removeprefix(PREFIX)
        original = PRIVATE_SOURCES[name].encode()
        assert entry["original_git_blob"] == git(
            repo, "rev-parse", f"HEAD:{PREFIX}{name}"
        )
        assert entry["original_sha256"] == hashlib.sha256(original).hexdigest()
        assert entry["replacements"] == {
            category: 1 for category in REASONS[name].split(",")
        }
    result = build((repo, plan, output), "--redaction-rules", str(rules))
    assert result.returncode == 0, result.stderr
    for role in ROLES:
        copy = output / "redacted" / role / PREFIX
        assert (copy / GUIDE).read_text() == REDACTED_GUIDE
        assert not (output / "sources" / role / PREFIX / GUIDE).exists()
        code = runpy.run_path(str(copy / CODE))
        assert code["DEFAULT_DATA_DIR"] == Path.home() / "data"
        assert code["HOST"] == "[private-host]"
    blob = git(repo, "rev-parse", f"HEAD:{PREFIX}{GUIDE}")
    assert not (output / "history/.git/objects" / blob[:2] / blob[2:]).exists()
    assert not any(
        private in content for content in bundle_bytes(output) for private in PRIVATE
    )
    assert "[private-host]" in (output / "redacted/README.md").read_text()
    repo.rename(repo.with_name("unavailable-repository"))
    result = cli("verify", "--bundle", str(output))
    assert result.returncode == 0, result.stderr


def drop_from_inventory(output: Path, name: str) -> None:
    manifest_path = output / "ic-release-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"] = [f for f in manifest["files"] if f["path"] != name]
    manifest_path.write_text(json.dumps(manifest))
    (output / "ic-release-manifest.sha256").write_text(
        hashlib.sha256(manifest_path.read_bytes()).hexdigest() + "\n"
    )


@pytest.mark.parametrize(
    ("tamper", "message"),
    [
        ("restored-text", "Bundled redaction differs from plan"),
        ("counts", "Redaction placeholders differ from plan"),
        ("unbound-original", "not bound to one withheld source"),
        ("original-blob", "History tree differs"),
        ("unlisted-copy", "Unexpected bundle file"),
        ("extra-copy", "history allowlist"),
        ("notice", "Unexpected redaction notice"),
    ],
)
def test_verify_refuses_a_tampered_redaction(
    redaction: tuple[Path, Path, Path, Path], tamper: str, message: str
) -> None:
    repo, plan, output, rules = redaction
    built = build((repo, plan, output), "--redaction-rules", str(rules))
    assert built.returncode == 0, built.stderr
    name = f"redacted/x3-x7/{PREFIX}{GUIDE}"
    if tamper == "restored-text":
        (output / name).write_text(PRIVATE_SOURCES[GUIDE])
        rehash(output, name)
    elif tamper in {"counts", "unbound-original", "original-blob"}:

        def edit(p: dict[str, Any]) -> None:
            source = ("x3-x7", PREFIX + GUIDE)
            withheld, redacted = (
                next(e for e in p[key] if (e["role"], e["path"]) == source)
                for key in ("withheld", "redacted")
            )
            if tamper == "counts":
                redacted["replacements"]["private-host-name"] = 2
            else:
                redacted["original_git_blob"] = "1" * 40
            if tamper == "original-blob":
                withheld["git_blob"] = "1" * 40

        update_plan(output / "plan.json", edit)
        rehash(output, "plan.json")
    elif tamper == "unlisted-copy":
        drop_from_inventory(output, name)
    elif tamper == "extra-copy":
        extra = f"redacted/x3-x7/{PREFIX}README.md"
        (output / extra).write_text("unlisted public copy\n")
        manifest_path = output / "ic-release-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"].append({"path": extra, "sha256": "0" * 64, "bytes": 0})
        manifest_path.write_text(json.dumps(manifest))
        rehash(output, extra)
    else:
        (output / "redacted/README.md").write_text("Nothing was redacted.\n")
        rehash(output, "redacted/README.md")
    result = cli("verify", "--bundle", str(output))
    assert result.returncode == 2
    assert message in result.stderr


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("missing-rules", "rules required for every declared reason"),
        ("uncovered-reason", "rules required for every declared reason"),
        ("undeclared-category", "Invalid redaction counts"),
        ("broken-code", "no longer parses"),
        ("placeholder-in-code", "changed code outside string literals"),
        ("code-form-span", "Code form span must open a Path literal"),
        ("code-form-category", "Invalid redaction rule"),
        ("placeholder-in-original", "already contains a redaction placeholder"),
        ("code-form-in-original", "already contains a redaction placeholder"),
    ],
)
def test_plan_refuses_an_unsafe_redaction(
    redaction: tuple[Path, Path, Path, Path], tmp_path: Path, change: str, message: str
) -> None:
    repo, plan, _, rules = redaction
    target, reasons = CODE, REASONS[CODE]
    extra = {
        "broken-code": {"category": "private-host-name", "pattern": "HOST ="},
        "placeholder-in-code": {"category": "private-host-name", "pattern": "len"},
        "code-form-span": {
            "category": "absolute-home-path",
            "pattern": r'Path\("/Users/[a-z-]+',
            "form": "code",
        },
        "code-form-category": {
            "category": "private-host-name",
            "pattern": "fixture-host",
            "form": "code",
        },
    }
    rules_path: Path | None = rules
    if change == "missing-rules":
        rules_path = None
    elif change == "uncovered-reason":
        reasons += ",private-address"
    elif change == "undeclared-category":
        reasons = "absolute-home-path"
    elif change in extra:
        rules_path = write_rules(tmp_path / "changed.json", [extra[change], *RULES])
    else:
        if change == "placeholder-in-original":
            target, reasons = GUIDE, REASONS[GUIDE]
            content = "A [home] placeholder already exists.\n"
        else:
            content = PRIVATE_SOURCES[CODE] + 'OTHER = Path.home().joinpath("x")\n'
        (repo / PREFIX / target).write_text(content)
        git(repo, "commit", "--quiet", "-am", "Add an artificial placeholder")
    result = plan_redactions(repo, plan, rules_path, f"{PREFIX}{target}={reasons}")
    assert result.returncode == 2
    assert message in result.stderr
    assert not plan.exists()


@pytest.mark.parametrize(
    ("rules", "message"),
    [
        (None, "Redaction rules required"),
        (RULES[:-1], "Redacted copy differs from plan"),
    ],
)
def test_build_refuses_rules_that_do_not_reproduce_the_plan(
    redaction: tuple[Path, Path, Path, Path],
    tmp_path: Path,
    rules: list[dict[str, str]] | None,
    message: str,
) -> None:
    repo, plan, output, _ = redaction
    extra = (
        ("--redaction-rules", str(write_rules(tmp_path / "other.json", rules)))
        if rules
        else ()
    )
    result = build((repo, plan, output), *extra)
    assert result.returncode == 2
    assert message in result.stderr
    assert not output.exists()


def test_rejects_release_root_below_a_symlinked_directory(
    fixture: tuple[Path, Path, Path],
    tmp_path: Path,
) -> None:
    _, plan, output = fixture
    real = tmp_path / "elsewhere"
    (real / "approved-release").mkdir(parents=True)
    (real / "approved-release" / "x3.json").write_bytes(b"{}")
    link = tmp_path / "innocent"
    link.symlink_to(real, target_is_directory=True)
    add_artifact(plan, "x3.json", b"{}")
    result = build(fixture, "--release-root", str(link / "approved-release"))
    assert result.returncode == 2
    assert "Symlink" in result.stderr
    assert not output.exists()


def test_rejects_every_sealed_prefixed_root(
    fixture: tuple[Path, Path, Path],
    tmp_path: Path,
) -> None:
    _, plan, output = fixture
    root = tmp_path / "sealed-synthetic-input"
    root.mkdir()
    (root / "x3.json").write_bytes(b"{}")
    add_artifact(plan, "x3.json", b"{}")
    result = build(fixture, "--release-root", str(root))
    assert result.returncode == 2
    assert "Forbidden path" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize(
    ("files", "message"),
    [
        ({".python-version": "\n"}, "Python version missing"),
        (
            {
                "uv.lock": 'version=1\n[[package]]\nname="numpy"\nversion="0.0.1"\n'
                '[[package]]\nname="numpy"\nversion="0.0.2"\n'
            },
            "Conflicting locked versions",
        ),
    ],
)
def test_rejects_an_environment_that_cannot_be_identified(
    fixture: tuple[Path, Path, Path],
    files: dict[str, str],
    message: str,
) -> None:
    repo, plan, output = fixture
    for name, content in files.items():
        (repo / PREFIX / name).write_text(content)
    git(repo, "add", ".")
    git(repo, "commit", "--quiet", "-m", "Change the artificial environment")
    head = git(repo, "rev-parse", "HEAD")
    first = git(repo, "rev-list", "--max-parents=0", "HEAD")
    plan.unlink()
    revisions = [
        arg
        for role in ROLES
        for arg in (
            "--revision",
            f"{role}={head if role == 'reporting-export' else first}",
        )
    ]
    planned = cli(
        "plan",
        "--repository",
        str(repo),
        "--mode",
        "synthetic",
        "--output",
        str(plan),
        *revisions,
    )
    assert planned.returncode == 0, planned.stderr
    result = build(fixture)
    assert result.returncode == 2
    assert message in result.stderr
    assert not output.exists()


def module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_new_tools_and_resources_are_selected_and_verified_offline(
    fixture: tuple[Path, Path, Path],
) -> None:
    _, _, output = fixture
    result = build(fixture)
    assert result.returncode == 0, result.stderr
    for name in ASSEMBLY_SOURCES:
        assert (output / "sources/reporting-export" / PREFIX / name).is_file()
    assert cli("verify", "--bundle", str(output)).returncode == 0


@pytest.mark.parametrize(
    "name",
    [
        "public-aggregates.json",
        "expected-hashes.json",
        "owner-facts.json",
        "assembly-facts.json",
        "assembly-record.json",
        "report/F1_a_star_by_family_synthetic.pdf",
        "report/T1s_a_star_all_units_synthetic.csv",
    ],
)
def test_curated_artifacts_build_and_verify(
    fixture: tuple[Path, Path, Path], tmp_path: Path, name: str
) -> None:
    _, plan, output = fixture
    root = tmp_path / "curated"
    path = root / name
    path.parent.mkdir(parents=True)
    path.write_bytes(b"artificial artifact\n")
    add_artifact(plan, name, path.read_bytes())
    result = build(fixture, "--release-root", str(root))
    assert result.returncode == 0, result.stderr
    assert (output / "artifacts" / name).read_bytes() == path.read_bytes()
    assert cli("verify", "--bundle", str(output)).returncode == 0


@pytest.mark.parametrize("mode", ["synthetic", "approved-release", "source-only"])
@pytest.mark.parametrize(
    "name",
    ["report/F1_synthetic.pdf", "report/F1_a_star_by_family_synthetic.pdf"],
)
def test_synthetic_artifact_names_are_bounded_by_mode(
    fixture: tuple[Path, Path, Path], mode: str, name: str
) -> None:
    _, path, _ = fixture
    builder = module(BUILDER)
    plan = json.loads(path.read_bytes())
    plan["mode"] = mode
    if mode != "synthetic":
        plan["revisions"].update(builder.PINNED)
    add_artifact(path, name, b"fixture")
    plan["files"] = json.loads(path.read_bytes())["files"]
    if mode == "synthetic" and name == "report/F1_a_star_by_family_synthetic.pdf":
        builder.validate_plan(plan)
    else:
        with pytest.raises(ValueError, match="Artifact outside allowlist"):
            builder.validate_plan(plan)


@pytest.mark.parametrize("producer", ["old-generator", "wrapper", "unselected"])
def test_synthetic_receipt_requires_the_selected_generator(
    fixture: tuple[Path, Path, Path], tmp_path: Path, producer: str
) -> None:
    _, plan, output = fixture
    root = tmp_path / "curated"
    root.mkdir()
    curves = b"{}"
    script = (
        b"# Old artificial generator.\n"
        if producer == "old-generator"
        else b"# Artificial packaging fixture; never execute.\n"
    )
    receipt = json.dumps(
        {
            "released_curves_sha256": hashlib.sha256(curves).hexdigest(),
            "condition": "declared-close",
            "released_utc": "2026-10-19T02:59:00Z",
            "script_sha256": hashlib.sha256(script).hexdigest(),
        }
    ).encode()
    for name, content in (
        ("released-curves.json", curves),
        ("release-record.json", receipt),
    ):
        (root / name).write_bytes(content)
        add_artifact(plan, name, content)
    if producer == "unselected":
        update_plan(
            plan,
            lambda p: p.update(
                files=[f for f in p["files"] if f["path"] != PREFIX + GENERATOR]
            ),
        )
    result = build(fixture, "--release-root", str(root))
    assert result.returncode == 2
    assert "generator" in result.stderr or "not selected" in result.stderr
    assert not output.exists()


@pytest.mark.parametrize("synthetic_digest", [False, True])
def test_real_release_still_checks_the_wrapper(
    tmp_path: Path, synthetic_digest: bool
) -> None:
    builder = module(BUILDER)
    stage = tmp_path / "stage"
    (stage / "artifacts").mkdir(parents=True)
    curves = b"{}"
    (stage / "artifacts/released-curves.json").write_bytes(curves)
    script = stage / "sources/release-wrapper" / PREFIX / WRAPPER
    script.parent.mkdir(parents=True)
    script.write_bytes(b"real wrapper fixture")
    receipt = {
        "released_curves_sha256": hashlib.sha256(curves).hexdigest(),
        "condition": "declared-close",
        "released_utc": "2026-10-19T02:59:00Z",
        "script_sha256": hashlib.sha256(
            b"synthetic generator" if synthetic_digest else script.read_bytes()
        ).hexdigest(),
    }
    (stage / "artifacts/release-record.json").write_text(json.dumps(receipt))
    plan = {
        "mode": "approved-release",
        "files": [
            {"root": "release", "path": name}
            for name in ("released-curves.json", "release-record.json")
        ]
        + [{"root": "repository", "role": "release-wrapper", "path": PREFIX + WRAPPER}],
    }
    if synthetic_digest:
        with pytest.raises(ValueError, match="Executed release wrapper"):
            builder.check_release_pair(stage, plan)
    else:
        builder.check_release_pair(stage, plan)


def test_prepare_expected_hashes_uses_authorized_rendering(tmp_path: Path) -> None:
    from ic_study.analysis.detection_v4_report import Inputs, render
    from ic_study.analysis.v4_public_aggregates import project
    from ic_study.analysis.v4_report_synthetic import GatePlan, build_gate

    verifier = module(STUDY / "publications/reproducibility/verify_short_path.py")
    gate = build_gate(tmp_path / "gate", GatePlan(stages=("G0",)))
    criteria = STUDY / "experiments/exploratory/detection-boundary-v4/criteria-v43.json"
    inputs = Inputs(None, gate, criteria=criteria)
    report = tmp_path / "authorized-report"
    render(inputs, report, synthetic=True, dpi=40)
    bundle = tmp_path / "public"
    bundle.mkdir()
    projection = bundle / "public-aggregates.json"
    project(inputs, projection, synthetic=True)
    manifest = bundle / "expected-hashes.json"
    out = tmp_path / "authorized-reference"
    assert (
        verifier.main(
            [
                "prepare",
                "--gate-root",
                str(gate),
                "--criteria",
                str(criteria),
                "--report",
                str(report),
                "--projection",
                str(projection),
                "--out",
                str(out),
                "--manifest",
                str(manifest),
                "--synthetic",
            ]
        )
        == 0
    )
    metadata = json.loads(manifest.read_bytes())
    assert metadata["dpi"] == 40
    assert metadata["files"] == verifier.hashes(out)
    assert (
        verifier.main(
            ["verify", "--bundle", str(bundle), "--out", str(tmp_path / "replay")]
        )
        == 0
    )
    with pytest.raises(ValueError, match="already exists"):
        verifier.prepare(
            inputs, report, projection, tmp_path / "another", manifest, synthetic=True
        )
    with pytest.raises(ValueError, match="authorized inputs"):
        verifier.prepare(
            Inputs(None, None, public_aggregates=projection),
            report,
            projection,
            tmp_path / "invalid",
            bundle / "other.json",
            synthetic=True,
        )
    with pytest.raises(ValueError, match="rendered from other inputs"):
        verifier.prepare(
            inputs,
            tmp_path / "replay/report",
            projection,
            tmp_path / "from-public-replay",
            bundle / "from-public-replay.json",
            synthetic=True,
        )
    assert not (bundle / "from-public-replay.json").exists()
    (report / "F4_gate_diagnostics_synthetic.png").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="differs from the authorized report"):
        verifier.prepare(
            inputs,
            report,
            projection,
            tmp_path / "tampered-reference",
            bundle / "tampered.json",
            synthetic=True,
        )
    assert not (bundle / "tampered.json").exists()
