from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from ic_study.validation.experiments import (
    ExperimentValidationError,
    main,
    validate_experiment,
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> bytes:
    data = (json.dumps(value, sort_keys=True) + "\n").encode()
    path.write_bytes(data)
    return data


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


class Pilot:
    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.study = self.repo / "study"
        self.directory = self.study / "experiments" / "pilot"
        self.directory.mkdir(parents=True)
        package = self.study / "src" / "ic_study"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("raise RuntimeError('no simulation')\n")
        (self.study / "pyproject.toml").write_text("[project]\nname='fixture'\n")
        (self.study / "uv.lock").write_text("version = 1\n")
        git(self.repo, "init", "--quiet")
        git(self.repo, "add", ".")
        git(
            self.repo,
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.test",
            "commit",
            "--quiet",
            "-m",
            "Freeze fixture sources",
        )
        self.revision = git(self.repo, "rev-parse", "HEAD")
        self.sources = {
            str(p.relative_to(self.study)): digest(p.read_bytes())
            for p in [
                package / "__init__.py",
                self.study / "pyproject.toml",
                self.study / "uv.lock",
            ]
        }
        self.spec: dict[str, Any] = {
            "format": "fragmentation-exploratory-spec-v1",
            "status": "exploratory",
            "seed_base": 100,
            "models": {"uniform": {}, "adaptive": {}},
            "profiles": {"pair": {"kind": "complete", "n": 2, "seed_index": 0}},
            "phases": {
                "pilot": {
                    "profiles": ["pair"],
                    "confidences": [0.5],
                    "graph_replicates": 1,
                    "opinion_replicates": 1,
                    "seed_offset": 0,
                    "allowed_max_attempts": [10],
                }
            },
        }
        self.header: dict[str, Any] = {
            "record": "header",
            "format": "fragmentation-exploratory-run-v1",
            "code_revision": self.revision,
            "source_sha256": self.sources,
            "spec": self.spec,
            "phase": "pilot",
            "max_attempts": 10,
            "environment": {
                "python": "3.12",
                "platform": "test",
                "machine": "test",
                "rng": "fixture",
            },
        }
        common = {
            "record": "trial",
            "profile_id": "pair",
            "profile": self.spec["profiles"]["pair"],
            "confidence": 0.5,
            "graph_rep": 0,
            "opinion_rep": 0,
            "graph_seed": 100,
            "opinion_seed": 110,
            "event_seed": 120,
            "initial_opinions": [0.0, 0.2],
            "base_edges": [[0, 1]],
        }
        self.rows = [
            {
                **common,
                "trial_index": 0,
                "model": "uniform",
                "result": {
                    "status": "certified",
                    "attempts": 1,
                    "numerical_error": None,
                    "certified_stop": {"attempt": 1},
                },
            },
            {
                **common,
                "trial_index": 1,
                "model": "adaptive",
                "result": {
                    "status": "right_censored",
                    "attempts": 10,
                    "numerical_error": None,
                    "certified_stop": None,
                },
            },
        ]
        self.footer: dict[str, Any] = {"record": "completed", "trials": 2}
        self.artifact = root / "data.jsonl"
        self.manifest = self.directory / "run-manifest.json"
        self.save()

    def save(self) -> None:
        spec_bytes = write_json(self.directory / "spec.json", self.spec)
        self.header["spec_sha256"] = digest(spec_bytes)
        data = b"".join(
            (json.dumps(r, sort_keys=True) + "\n").encode()
            for r in [self.header, *self.rows, self.footer]
        )
        self.artifact.write_bytes(data)
        manifest = {
            "format": "fragmentation-pilot-run-manifest-v1",
            "scientific_acceptance": False,
            "phases": {
                "pilot": {
                    "artifact_path": str(self.artifact),
                    "sha256": digest(data),
                    "size_bytes": len(data),
                    "code_revision": self.revision,
                    "spec_sha256": digest(spec_bytes),
                    "trials": 2,
                    "max_attempts": 10,
                    "environment": self.header["environment"],
                }
            },
        }
        manifest_bytes = write_json(self.manifest, manifest)
        write_json(
            self.directory / "analysis-input.json",
            {
                "run_manifest_sha256": digest(manifest_bytes),
            },
        )
        for name in [
            "implementation-review.md",
            "results-review.md",
            "recommendation-input.md",
        ]:
            (self.directory / name).write_text(
                "Fixture review evidence; no approval.\n"
            )
        write_json(
            self.directory / "validation.json",
            {
                "format": "fragmentation-pilot-delivery-validation-v1",
                "reviewed_input_sha256": {
                    name: digest((self.directory / name).read_bytes())
                    for name in [
                        "run-manifest.json",
                        "analysis-input.json",
                        "implementation-review.md",
                        "results-review.md",
                        "recommendation-input.md",
                    ]
                },
            },
        )


def test_fragmentation_validation_retains_censoring_without_regeneration(
    tmp_path: Path,
) -> None:
    pilot = Pilot(tmp_path)
    receipt = validate_experiment(pilot.manifest, study_root=pilot.study)
    assert receipt["status"] == "integrity_verified"
    assert receipt["scientific_acceptance"] is False
    assert receipt["runs"][0]["records"] == 2
    assert receipt["runs"][0]["outcomes"] == {
        "certified": 1,
        "right_censored": 1,
        "numerical_failure": 0,
    }


@pytest.mark.parametrize(
    "damage", ["bytes", "size", "footer", "count", "spec", "revision"]
)
def test_corrupt_run_envelope_cannot_produce_a_receipt(
    tmp_path: Path, damage: str
) -> None:
    pilot = Pilot(tmp_path)
    if damage == "bytes":
        pilot.artifact.write_bytes(pilot.artifact.read_bytes() + b" ")
    elif damage == "footer":
        pilot.footer["record"] = "interrupted"
        pilot.save()
    elif damage == "count":
        pilot.rows.pop()
        pilot.save()
    elif damage == "spec":
        write_json(pilot.directory / "spec.json", {**pilot.spec, "seed_base": 999})
    elif damage == "revision":
        pilot.header["code_revision"] = "0" * 40
        pilot.save()
    else:
        manifest = json.loads(pilot.manifest.read_bytes())
        manifest["phases"]["pilot"]["size_bytes"] += 1
        write_json(pilot.manifest, manifest)
    with pytest.raises(ExperimentValidationError):
        validate_experiment(pilot.manifest, study_root=pilot.study)


@pytest.mark.parametrize(
    "damage",
    ["source", "lock", "missing_source", "review", "analysis", "unsafe_source"],
)
def test_recorded_sources_and_review_evidence_must_close(
    tmp_path: Path, damage: str
) -> None:
    pilot = Pilot(tmp_path)
    if damage in {"source", "lock"}:
        key = "uv.lock" if damage == "lock" else "src/ic_study/__init__.py"
        pilot.sources[key] = "0" * 64
        pilot.save()
    elif damage == "missing_source":
        del pilot.sources["src/ic_study/__init__.py"]
        pilot.save()
    elif damage == "unsafe_source":
        pilot.sources["../outside.py"] = "0" * 64
        pilot.save()
    elif damage == "review":
        (pilot.directory / "results-review.md").write_text("Changed after review")
    else:
        write_json(
            pilot.directory / "analysis-input.json", {"run_manifest_sha256": "0" * 64}
        )
        validation = json.loads((pilot.directory / "validation.json").read_bytes())
        validation["reviewed_input_sha256"]["analysis-input.json"] = digest(
            (pilot.directory / "analysis-input.json").read_bytes()
        )
        write_json(pilot.directory / "validation.json", validation)
    with pytest.raises(ExperimentValidationError):
        validate_experiment(pilot.manifest, study_root=pilot.study)


def test_historical_sources_are_checked_at_the_recorded_revision(
    tmp_path: Path,
) -> None:
    pilot = Pilot(tmp_path)
    (pilot.study / "src/ic_study/__init__.py").write_text("Different current checkout")
    receipt = validate_experiment(pilot.manifest, study_root=pilot.study)
    assert receipt["runs"][0]["code_revision"] == pilot.revision
    assert receipt["review_evidence"]["results-review.md"] == digest(
        (pilot.directory / "results-review.md").read_bytes()
    )


@pytest.mark.parametrize(
    "damage", ["duplicate", "seed", "pair", "false_certificate", "short_censor"]
)
def test_fragmentation_design_and_outcomes_are_not_just_manifest_counts(
    tmp_path: Path, damage: str
) -> None:
    pilot = Pilot(tmp_path)
    if damage == "duplicate":
        pilot.rows[1] = dict(pilot.rows[0])
    elif damage == "seed":
        pilot.rows[1]["event_seed"] = 999
    elif damage == "pair":
        pilot.rows[1]["initial_opinions"] = [0.1, 0.8]
    elif damage == "false_certificate":
        pilot.rows[1]["result"]["status"] = "certified"
    else:
        pilot.rows[1]["result"]["attempts"] = 1
    pilot.save()
    with pytest.raises(ExperimentValidationError):
        validate_experiment(pilot.manifest, study_root=pilot.study)


def test_numerical_failure_remains_distinct_from_censoring(tmp_path: Path) -> None:
    pilot = Pilot(tmp_path)
    pilot.rows[1]["result"].update(
        status="numerical_failure", numerical_error="underflow", attempts=2
    )
    pilot.save()
    receipt = validate_experiment(pilot.manifest, study_root=pilot.study)
    assert receipt["runs"][0]["outcomes"] == {
        "certified": 1,
        "right_censored": 0,
        "numerical_failure": 1,
    }


class ForecastPilot(Pilot):
    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self.spec = {
            "format": "probabilistic-forecast-pilot-spec-v1",
            "seed": 20,
            "truths": ["constant"],
            "attempts": [1],
            "sample_sizes": [11],
            "train_steps": 1,
            "test_steps": 1,
            "model_order": ["constant"],
            "models": {"constant": {"activation": 0.0}},
            "phases": {
                phase: {"data_group": group, "replicates": 1, "allowed_members": [2]}
                for phase, group in [
                    ("primary", "primary"),
                    ("precision", "primary"),
                    ("confirmation", "confirmation"),
                ]
            },
        }
        self.forecast_rows: dict[str, list[dict[str, Any]]] = {}
        for phase, config in self.spec["phases"].items():
            waves = []
            for wave in range(2):
                seed_bytes = json.dumps(
                    [20, "truth", config["data_group"], "constant-a1-n11", 0, wave],
                    separators=(",", ":"),
                ).encode()
                forecast_seed_bytes = json.dumps(
                    [20, "forecast", phase, "constant-a1-n11", 0, wave, "constant"],
                    separators=(",", ":"),
                ).encode()
                waves.append(
                    {
                        "wave": wave,
                        "split": "train" if wave == 0 else "test",
                        "observed": [1] * 11,
                        "outcome": [1] * 11,
                        "data_seed": int.from_bytes(
                            hashlib.sha256(seed_bytes).digest()[:16], "big"
                        ),
                        "forecasts": {
                            "constant": {
                                "seed": int.from_bytes(
                                    hashlib.sha256(forecast_seed_bytes).digest()[:16],
                                    "big",
                                ),
                                "ensemble": [[1] * 11, [1] * 11],
                                "scores": {
                                    score: 0.0
                                    for score in (
                                        "mean_w1",
                                        "central_w1",
                                        "energy",
                                        "mean_l2",
                                        "central_l2",
                                    )
                                },
                            }
                        },
                    }
                )
            self.forecast_rows[phase] = [
                {
                    "record": "trajectory",
                    "replicate": 0,
                    "cell": {
                        "id": "constant-a1-n11",
                        "truth": "constant",
                        "attempts": 1,
                        "sample_size": 11,
                    },
                    "waves": waves,
                    "selected_on_train": {
                        score: "constant"
                        for score in (
                            "mean_w1",
                            "central_w1",
                            "energy",
                            "mean_l2",
                            "central_l2",
                        )
                    },
                }
            ]
        self.save_forecast()

    def save_forecast(self) -> None:
        spec_bytes = write_json(self.directory / "spec.json", self.spec)
        runs = []
        for phase, rows in self.forecast_rows.items():
            header = {
                **self.header,
                "format": "probabilistic-forecast-exploratory-v1",
                "phase": phase,
                "spec": self.spec,
                "spec_sha256": digest(spec_bytes),
                "members": 2,
            }
            footer = {"record": "completed", "trajectories": len(rows)}
            data = b"".join(
                (json.dumps(r, sort_keys=True) + "\n").encode()
                for r in [header, *rows, footer]
            )
            path = self.artifact.parent / f"{phase}.jsonl"
            path.write_bytes(data)
            runs.append(
                {
                    "name": f"{phase}-r2",
                    "phase": phase,
                    "members": 2,
                    "location": str(path),
                    "sha256": digest(data),
                    "bytes": len(data),
                    "code_revision": self.revision,
                    "spec_sha256": digest(spec_bytes),
                    "source_sha256": self.sources,
                    "environment": self.header["environment"],
                    "trajectories": len(rows),
                    "status": "completed",
                }
            )
        manifest_bytes = write_json(
            self.manifest, {"format": "forecast-pilot-run-manifest-v1", "runs": runs}
        )
        write_json(
            self.directory / "analysis-input.json",
            {"run_manifest_sha256": digest(manifest_bytes)},
        )
        write_json(
            self.directory / "validation.json",
            {
                "format": "forecast-pilot-engineering-validation-v1",
                "artifact_sha256": {
                    name: digest((self.directory / name).read_bytes())
                    for name in [
                        "run-manifest.json",
                        "analysis-input.json",
                        "spec.json",
                        "implementation-review.md",
                        "results-review.md",
                        "recommendation-input.md",
                    ]
                },
            },
        )


def test_forecast_precision_does_not_inflate_distinct_data_trajectories(
    tmp_path: Path,
) -> None:
    pilot = ForecastPilot(tmp_path)
    receipt = validate_experiment(pilot.manifest, study_root=pilot.study)
    assert len(receipt["runs"]) == 3
    assert receipt["forecast_data"] == {
        "analysis_trajectory_records": 3,
        "distinct_analysis_data_trajectories": 2,
        "repeated_analysis_data_trajectories": 1,
        "benchmark_trajectory_records": 0,
        "statistical_independence_verified": False,
    }


@pytest.mark.parametrize(
    "damage",
    [
        "duplicate",
        "wrong_cell",
        "missing_wave",
        "precision_data",
        "confirmation_seed",
        "split",
        "data_group",
    ],
)
def test_forecast_data_identity_requires_complete_consistent_evidence(
    tmp_path: Path, damage: str
) -> None:
    pilot = ForecastPilot(tmp_path)
    row = pilot.forecast_rows["precision"][0]
    if damage == "duplicate":
        pilot.forecast_rows["primary"].append(
            copy.deepcopy(pilot.forecast_rows["primary"][0])
        )
    elif damage == "wrong_cell":
        row["cell"]["id"] = "different-cell"
    elif damage == "missing_wave":
        row["waves"].pop()
    elif damage == "precision_data":
        row["waves"][1]["outcome"] = [2, 0, *([1] * 9)]
    elif damage == "confirmation_seed":
        pilot.forecast_rows["confirmation"][0]["waves"][0]["data_seed"] = row["waves"][
            0
        ]["data_seed"]
    elif damage == "split":
        row["waves"][0]["split"] = "test"
    else:
        pilot.spec["phases"]["confirmation"]["data_group"] = "primary"
    pilot.save_forecast()
    with pytest.raises(ExperimentValidationError):
        validate_experiment(pilot.manifest, study_root=pilot.study)


def test_cli_creates_a_private_receipt_once_and_supports_relocated_bytes(
    tmp_path: Path,
) -> None:
    pilot = Pilot(tmp_path)
    objects = tmp_path / "objects"
    objects.mkdir()
    data = pilot.artifact.read_bytes()
    (objects / digest(data)).write_bytes(data)
    pilot.artifact.unlink()
    receipt = tmp_path / "receipt.json"
    args = [
        "--manifest",
        str(pilot.manifest),
        "--study-root",
        str(pilot.study),
        "--artifact-root",
        str(objects),
        "--receipt",
        str(receipt),
    ]
    assert main(args) == 0
    original = receipt.read_bytes()
    assert receipt.stat().st_mode & 0o777 == 0o600
    assert json.loads(original)["status"] == "integrity_verified"
    assert main(args) == 1
    assert receipt.read_bytes() == original


def test_cli_reports_missing_artifacts_without_creating_success_receipts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    pilot = Pilot(tmp_path)
    pilot.artifact.unlink()
    receipt = tmp_path / "receipt.json"
    assert (
        main(
            [
                "--manifest",
                str(pilot.manifest),
                "--study-root",
                str(pilot.study),
                "--receipt",
                str(receipt),
            ]
        )
        == 2
    )
    assert not receipt.exists()
    assert json.loads(capsys.readouterr().err)["status"] == "unavailable"


def test_receipt_is_deterministic_for_unchanged_inputs(tmp_path: Path) -> None:
    pilot = ForecastPilot(tmp_path)
    assert validate_experiment(
        pilot.manifest, study_root=pilot.study
    ) == validate_experiment(pilot.manifest, study_root=pilot.study)


@pytest.mark.parametrize(
    "damage",
    [
        "duplicate_run",
        "missing_phase",
        "boolean_budget",
        "empty_environment",
        "unsafe_review",
    ],
)
def test_invalid_manifest_bindings_fail_before_receipt_creation(
    tmp_path: Path, damage: str
) -> None:
    pilot = ForecastPilot(tmp_path)
    if damage == "empty_environment":
        pilot.header["environment"] = {}
        pilot.save_forecast()
    elif damage == "boolean_budget":
        pilot.spec["phases"]["primary"]["allowed_members"] = [True]
        pilot.save_forecast()
        manifest = json.loads(pilot.manifest.read_bytes())
        run = manifest["runs"][0]
        artifact = Path(run["location"])
        records = [json.loads(line) for line in artifact.read_text().splitlines()]
        records[0]["members"] = True
        data = b"".join((json.dumps(row) + "\n").encode() for row in records)
        artifact.write_bytes(data)
        run.update(members=True, sha256=digest(data), bytes=len(data))
        write_json(pilot.manifest, manifest)
    elif damage == "unsafe_review":
        outside = pilot.directory.parent / "outside.md"
        outside.write_text("Unrelated document")
        validation = json.loads((pilot.directory / "validation.json").read_bytes())
        validation["artifact_sha256"]["../outside.md"] = digest(outside.read_bytes())
        write_json(pilot.directory / "validation.json", validation)
    else:
        manifest = json.loads(pilot.manifest.read_bytes())
        if damage == "duplicate_run":
            manifest["runs"].append(copy.deepcopy(manifest["runs"][0]))
        else:
            manifest["runs"].pop()
        write_json(pilot.manifest, manifest)
    if damage not in {"unsafe_review", "empty_environment"}:
        write_json(
            pilot.directory / "analysis-input.json",
            {"run_manifest_sha256": digest(pilot.manifest.read_bytes())},
        )
        validation = json.loads((pilot.directory / "validation.json").read_bytes())
        for name in ("run-manifest.json", "analysis-input.json"):
            validation["artifact_sha256"][name] = digest(
                (pilot.directory / name).read_bytes()
            )
        write_json(pilot.directory / "validation.json", validation)
    with pytest.raises(ExperimentValidationError):
        validate_experiment(pilot.manifest, study_root=pilot.study)


@pytest.mark.parametrize(
    "damage",
    [
        "missing_forecast",
        "short_ensemble",
        "bad_histogram",
        "forecast_seed",
        "score_keys",
        "selection",
    ],
)
def test_forecast_outputs_must_close_over_models_and_ensemble_budget(
    tmp_path: Path, damage: str
) -> None:
    pilot = ForecastPilot(tmp_path)
    row = pilot.forecast_rows["primary"][0]
    forecast = row["waves"][0]["forecasts"]["constant"]
    if damage == "missing_forecast":
        del row["waves"][0]["forecasts"]["constant"]
    elif damage == "short_ensemble":
        forecast["ensemble"].pop()
    elif damage == "bad_histogram":
        forecast["ensemble"][0][0] = -1
    elif damage == "forecast_seed":
        forecast["seed"] += 1
    elif damage == "score_keys":
        del forecast["scores"]["energy"]
    else:
        row["selected_on_train"]["energy"] = "missing-model"
    pilot.save_forecast()
    with pytest.raises(ExperimentValidationError):
        validate_experiment(pilot.manifest, study_root=pilot.study)


def test_overflowing_json_numbers_do_not_become_infinite_scores(tmp_path: Path) -> None:
    pilot = ForecastPilot(tmp_path)
    manifest = json.loads(pilot.manifest.read_bytes())
    run = manifest["runs"][0]
    artifact = Path(run["location"])
    data = artifact.read_bytes().replace(b'"energy": 0.0', b'"energy": 1e999', 1)
    artifact.write_bytes(data)
    run.update(sha256=digest(data), bytes=len(data))
    write_json(pilot.manifest, manifest)
    write_json(
        pilot.directory / "analysis-input.json",
        {"run_manifest_sha256": digest(pilot.manifest.read_bytes())},
    )
    validation = json.loads((pilot.directory / "validation.json").read_bytes())
    for name in ("run-manifest.json", "analysis-input.json"):
        validation["artifact_sha256"][name] = digest(
            (pilot.directory / name).read_bytes()
        )
    write_json(pilot.directory / "validation.json", validation)
    with pytest.raises(ExperimentValidationError, match="finite"):
        validate_experiment(pilot.manifest, study_root=pilot.study)


def test_alternate_manifest_must_be_the_exact_reviewed_manifest(tmp_path: Path) -> None:
    pilot = ForecastPilot(tmp_path)
    candidate = pilot.directory / "candidate.json"
    candidate.write_bytes(pilot.manifest.read_bytes() + b"\n")
    write_json(
        pilot.directory / "analysis-input.json",
        {"run_manifest_sha256": digest(candidate.read_bytes())},
    )
    validation = json.loads((pilot.directory / "validation.json").read_bytes())
    validation["artifact_sha256"]["analysis-input.json"] = digest(
        (pilot.directory / "analysis-input.json").read_bytes()
    )
    write_json(pilot.directory / "validation.json", validation)
    with pytest.raises(ExperimentValidationError, match="Reviewed manifest binding"):
        validate_experiment(candidate, study_root=pilot.study)


@pytest.mark.parametrize("phase", ["primary", "precision"])
def test_precision_must_repeat_the_complete_primary_data_set(
    tmp_path: Path, phase: str
) -> None:
    pilot = ForecastPilot(tmp_path)
    pilot.spec["phases"][phase]["replicates"] = 2
    extra = copy.deepcopy(pilot.forecast_rows[phase][0])
    extra["replicate"] = 1
    for index, wave in enumerate(extra["waves"]):
        for label, parts in (
            ("truth", [20, "truth", "primary", "constant-a1-n11", 1, index]),
            (
                "forecast",
                [20, "forecast", phase, "constant-a1-n11", 1, index, "constant"],
            ),
        ):
            seed = int.from_bytes(
                hashlib.sha256(
                    json.dumps(parts, separators=(",", ":")).encode()
                ).digest()[:16],
                "big",
            )
            if label == "truth":
                wave["data_seed"] = seed
            else:
                wave["forecasts"]["constant"]["seed"] = seed
    pilot.forecast_rows[phase].append(extra)
    pilot.save_forecast()
    with pytest.raises(ExperimentValidationError, match="same data identities"):
        validate_experiment(pilot.manifest, study_root=pilot.study)


@pytest.mark.parametrize("damage", ["huge_integer", "deep_json", "environment_list"])
def test_cli_normalizes_malformed_records_without_a_success_receipt(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], damage: str
) -> None:
    pilot = Pilot(tmp_path)
    if damage == "huge_integer":
        pilot.manifest.write_bytes(b'{"n":' + b"9" * 5000 + b"}")
    elif damage == "deep_json":
        pilot.manifest.write_bytes(b'{"n":' + b"[" * 10000 + b"0" + b"]" * 10000 + b"}")
    else:
        pilot.header["environment"] = []
        pilot.save()
    receipt = tmp_path / "invalid-receipt.json"
    assert (
        main(
            [
                "--manifest",
                str(pilot.manifest),
                "--study-root",
                str(pilot.study),
                "--receipt",
                str(receipt),
            ]
        )
        == 1
    )
    assert not receipt.exists()
    assert json.loads(capsys.readouterr().err)["status"] == "invalid"


def test_growing_input_is_rejected_without_reading_past_the_byte_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pilot = Pilot(tmp_path)
    byte_limit = 8 * 1024 * 1024
    original_open = Path.open
    consumed = 0

    class GrowingReader:
        def __init__(self, stream: Any) -> None:
            self.stream = stream

        def __enter__(self) -> GrowingReader:
            with original_open(pilot.manifest, "ab") as writer:
                writer.write(b" " * (byte_limit * 2))
            return self

        def __exit__(self, *args: Any) -> None:
            self.stream.close()

        def fileno(self) -> int:
            return int(self.stream.fileno())

        def read(self, size: int = -1) -> bytes:
            nonlocal consumed
            data: bytes = self.stream.read(size)
            consumed += len(data)
            return data

    def open_input(path: Path, *args: Any, **kwargs: Any) -> Any:
        stream = original_open(path, *args, **kwargs)
        return GrowingReader(stream) if path == pilot.manifest else stream

    monkeypatch.setattr(Path, "open", open_input)
    with pytest.raises(ExperimentValidationError, match="byte limit"):
        validate_experiment(pilot.manifest, study_root=pilot.study)
    assert consumed <= byte_limit + 1
