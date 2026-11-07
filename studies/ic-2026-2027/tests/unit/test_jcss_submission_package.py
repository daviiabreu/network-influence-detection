"""Private source assembly preserves bytes and refuses unsafe destinations."""

from __future__ import annotations

import hashlib
import json
import stat
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "experiments/package_jcss_submission.py"


@pytest.fixture
def tree(tmp_path: Path) -> tuple[Path, Path]:
    manuscript, template = tmp_path / "manuscript", tmp_path / "template"
    (manuscript / "sections").mkdir(parents=True)
    (manuscript / "generated").mkdir()
    template.mkdir()
    (manuscript / "main.tex").write_text(
        "\\input{sections/body}\n\\bibliography{references}\n"
        "[Insert validated results]\n"
    )
    (manuscript / "sections/body.tex").write_text("Draft body\n")
    (manuscript / "references.bib").write_text("@article{example, title={Example}}\n")
    (manuscript / "unrelated.tex").write_text("Do not package me\n")
    for name in ("sn-jnl.cls", "sn-mathphys-num.bst"):
        (template / name).write_text(name + "\n")
    (template / "sn-mathphys-num.bst").write_text(
        "FUNCTION {make.tag}\n{ bother #0 = }\nFUNCTION {next}\n{}\n"
        'FUNCTION {format.doi}\n{ "\\doiurl{" process.doi * "} " * }\n'
    )
    return manuscript, template


def run(
    tree: tuple[Path, Path], out: Path, *extra: str
) -> subprocess.CompletedProcess[str]:
    manuscript, template = tree
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--manuscript",
            str(manuscript),
            "--template",
            str(template),
            "--out",
            str(out),
            *extra,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_draft_is_complete_private_and_hash_bound(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    out = tmp_path / "package"
    result = run(tree, out)
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "source-manifest.json").read_text())
    assert set(manifest["files"]) == {
        "main.tex",
        "sections/body.tex",
        "references.bib",
        "sn-jnl.cls",
        "sn-mathphys-num.bst",
    }
    for name, record in manifest["files"].items():
        content = (out / name).read_bytes()
        assert record["sha256"] == hashlib.sha256(content).hexdigest()
        assert record["bytes"] == len(content)
    assert manifest["draft_markers"][0]["marker"] == "[Insert validated results]"
    assert manifest["synthetic"] is False
    assert "generated/T1s_a_star_all_units.csv absent" in manifest["pending_assets"]
    for path in (out, *out.rglob("*")):
        assert stat.S_IMODE(path.stat().st_mode) == (0o700 if path.is_dir() else 0o600)
    assert (out / "main.tex").read_bytes() == (tree[0] / "main.tex").read_bytes()
    style_record = manifest["files"]["sn-mathphys-num.bst"]
    original_style = (tree[1] / "sn-mathphys-num.bst").read_bytes()
    assert style_record["original_sha256"] == hashlib.sha256(original_style).hexdigest()
    assert (out / "sn-mathphys-num.bst").read_bytes() == original_style.replace(
        b"bother #0 =", b'bother #0 = t "jtitle" = not and t "btitle" = not and'
    ).replace(b'"\\doiurl{" process.doi * "} " *', b'"\\doiurl{" process.doi * "}" *')


def test_generated_vectors_and_t1s_are_copied_without_transformation(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    generated = tree[0] / "generated"
    (generated / "F1.pdf").write_bytes(b"vector fixture")
    (generated / "T1s_a_star_all_units.csv").write_text("unit,status\nu1,valid\n")
    out = tmp_path / "package"
    assert run(tree, out).returncode == 0
    for name in ("F1.pdf", "T1s_a_star_all_units.csv"):
        assert (out / "generated" / name).read_bytes() == (
            generated / name
        ).read_bytes()
    manifest = json.loads((out / "source-manifest.json").read_text())
    assert manifest["generated_vector_figures"] == ["generated/F1.pdf"]
    assert manifest["pending_assets"] == ["compiled manuscript PDF not supplied"]


def test_existing_package_is_never_overwritten(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    out = tmp_path / "package"
    out.mkdir()
    (out / "sentinel").write_text("preserve")
    result = run(tree, out)
    assert result.returncode == 2 and "already exists" in result.stderr
    assert list(out.iterdir()) == [out / "sentinel"]


def test_git_destination_is_rejected_before_copying(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    (checkout / ".git").write_text("gitdir: fixture\n")
    out = checkout / "package"
    result = run(tree, out)
    assert result.returncode == 2 and "outside every Git" in result.stderr
    assert not out.exists()


def test_source_symlink_cannot_escape_the_manuscript(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    body = tree[0] / "sections/body.tex"
    body.unlink()
    external = tmp_path / "outside.tex"
    external.write_text("external source")
    body.symlink_to(external)
    out = tmp_path / "package"
    result = run(tree, out)
    assert result.returncode == 2 and "outside manuscript" in result.stderr
    assert not out.exists()


def test_synthetic_assets_are_never_substituted_for_final_results(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    (tree[0] / "generated/F1_synthetic.pdf").write_bytes(b"review only")
    out = tmp_path / "package"
    result = run(tree, out)
    assert result.returncode == 2 and "review-only" in result.stderr
    assert not out.exists()


def test_explicit_synthetic_staging_preserves_marks_and_recognizes_csv(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    generated = tree[0] / "generated"
    names = ("F1_a_star_by_family_synthetic.pdf", "T1s_a_star_all_units_synthetic.csv")
    for name in names:
        (generated / name).write_bytes(b"synthetic fixture\n")
    out = tmp_path / "synthetic-package"
    result = run(tree, out, "--synthetic")
    assert result.returncode == 0, result.stderr
    manifest = json.loads((out / "source-manifest.json").read_text())
    assert manifest["synthetic"] is True
    assert "local staging only" in manifest["purpose"]
    assert manifest["pending_assets"] == ["compiled manuscript PDF not supplied"]
    for name in names:
        assert (out / "generated" / name).read_bytes() == (
            generated / name
        ).read_bytes()


def test_synthetic_mode_still_refuses_git_destinations(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    (checkout / ".git").write_text("gitdir: fixture\n")
    out = checkout / "package"
    result = run(tree, out, "--synthetic")
    assert result.returncode == 2 and "outside every Git" in result.stderr
    assert not out.exists()


def test_internal_symlink_cannot_drop_a_required_input_name(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    body = tree[0] / "sections/body.tex"
    body.rename(tree[0] / "sections/shared.tex")
    body.symlink_to("shared.tex")
    out = tmp_path / "package"
    result = run(tree, out)
    assert result.returncode == 2 and "symlinks are unsupported" in result.stderr
    assert not out.exists()


def test_unsupported_style_fails_before_creating_a_package(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    (tree[1] / "sn-mathphys-num.bst").write_text("different vendor structure\n")
    out = tmp_path / "package"
    result = run(tree, out)
    assert result.returncode == 2 and "unsupported Springer style" in result.stderr
    assert not out.exists()


def test_internal_manuscript_inputs_are_refused(
    tree: tuple[Path, Path], tmp_path: Path
) -> None:
    manuscript, _ = tree
    (manuscript / "pipeline/drafts").mkdir(parents=True)
    (manuscript / "pipeline/drafts/shell.tex").write_text("Shell\n")
    (manuscript / "main.tex").write_text(
        "\\input{sections/body}\n\\input{pipeline/drafts/shell}\n"
        "\\bibliography{references}\n"
    )
    out = tmp_path / "package"
    result = run(tree, out)
    assert result.returncode == 2 and "internal manuscript input" in result.stderr
    assert not out.exists()


def test_the_checker_is_not_packaged(tree: tuple[Path, Path], tmp_path: Path) -> None:
    manuscript, _ = tree
    (manuscript / "pipeline").mkdir()
    (manuscript / "pipeline/paper_check.py").write_text("# checker\n")
    out = tmp_path / "package"
    result = run(tree, out)
    assert result.returncode == 0, result.stderr
    assert not (out / "pipeline").exists()


@pytest.mark.parametrize("name", ["v4-release", "sealed-synthetic"])
def test_private_destinations_are_refused(
    tree: tuple[Path, Path], tmp_path: Path, name: str
) -> None:
    out = tmp_path / name / "package"
    result = run(tree, out)
    assert result.returncode == 2 and "restricted input path" in result.stderr
    assert not out.exists()


def test_output_inside_the_manuscript_is_refused(
    tree: tuple[Path, Path],
) -> None:
    manuscript, _ = tree
    out = manuscript / "package"
    result = run(tree, out)
    assert result.returncode == 2 and "outside the manuscript" in result.stderr
    assert not out.exists()
