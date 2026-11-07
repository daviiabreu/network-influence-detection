"""Validate preserved exploratory experiment bytes without executing models."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import subprocess
import sys
from collections import Counter
from itertools import product
from pathlib import Path, PurePosixPath
from typing import Any


class ExperimentValidationError(ValueError):
    """A supplied record fails the declared integrity contract."""


class ExperimentArtifactsUnavailableError(ExperimentValidationError):
    """A local artifact or historical Git object is unavailable."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExperimentValidationError(message)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read(path: Path, limit: int = 8 * 1024 * 1024) -> bytes:
    try:
        info = path.lstat()
        _require(stat.S_ISREG(info.st_mode), f"Not a regular file: {path}")
        _require(info.st_size <= limit, f"File exceeds byte limit: {path}")
        with path.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            _require(
                stat.S_ISREG(opened.st_mode)
                and (opened.st_dev, opened.st_ino) == (info.st_dev, info.st_ino),
                f"Input changed before read: {path}",
            )
            _require(opened.st_size <= limit, f"File exceeds byte limit: {path}")
            data = stream.read(limit + 1)
        _require(len(data) <= limit, f"File exceeds byte limit: {path}")
        return data
    except FileNotFoundError as exc:
        raise ExperimentArtifactsUnavailableError(
            f"Missing local artifact: {path}"
        ) from exc


def _json(data: bytes) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            _require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value: str) -> None:
        raise ExperimentValidationError(f"Non-finite JSON number: {value}")

    def finite_float(value: str) -> float:
        number = float(value)
        _require(math.isfinite(number), f"Non-finite JSON number: {value}")
        return number

    value = json.loads(
        data, object_pairs_hook=pairs, parse_constant=constant, parse_float=finite_float
    )
    _require(isinstance(value, dict), "Expected a JSON object")
    return dict(value)


def _relative(value: str) -> str:
    path = PurePosixPath(value)
    _require(
        bool(value)
        and not path.is_absolute()
        and ".." not in path.parts
        and str(path) == value
        and "\\" not in value,
        f"Unsafe relative path: {value}",
    )
    return value


def _git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=False,
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0"},
    )
    if result.returncode:
        raise ExperimentArtifactsUnavailableError(
            "Required local Git object/repository unavailable"
        )
    return result.stdout


def _sources(study_root: Path, revision: str) -> dict[str, str]:
    _require(
        re.fullmatch(r"[0-9a-f]{40}", revision) is not None,
        "Expected full Git revision",
    )
    root = Path(
        _git(study_root, "rev-parse", "--show-toplevel").decode().strip()
    ).resolve()
    relative = study_root.resolve().relative_to(root).as_posix()
    resolved = (
        _git(root, "rev-parse", "--verify", f"{revision}^{{commit}}").decode().strip()
    )
    _require(resolved == revision, "Revision is not a commit")
    prefix = f"{relative}/" if relative != "." else ""
    records = _git(
        root,
        "ls-tree",
        "-r",
        "-z",
        revision,
        "--",
        f"{prefix}src/ic_study",
        f"{prefix}pyproject.toml",
        f"{prefix}uv.lock",
    )
    sources = {}
    for record in records.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.decode().split("\t", 1)
        mode, kind, _ = metadata.split()
        path = raw_path.removeprefix(prefix)
        if not (path.endswith(".py") or path in {"pyproject.toml", "uv.lock"}):
            continue
        _require(
            mode in {"100644", "100755"} and kind == "blob",
            f"Non-regular source: {path}",
        )
        sources[path] = _digest(_git(root, "show", f"{revision}:{raw_path}"))
    _require(
        {"pyproject.toml", "uv.lock"}.issubset(sources)
        and any(p.endswith(".py") for p in sources),
        "Incomplete historical source/lock set",
    )
    return sources


def _reviews(
    directory: Path, manifest_hash: str, fragmentation: bool
) -> tuple[str, dict[str, str]]:
    validation_bytes = _read(directory / "validation.json")
    validation = _json(validation_bytes)
    expected = (
        "fragmentation-pilot-delivery-validation-v1"
        if fragmentation
        else "forecast-pilot-engineering-validation-v1"
    )
    _require(validation["format"] == expected, "Unsupported review validation format")
    bindings = validation[
        "reviewed_input_sha256" if fragmentation else "artifact_sha256"
    ]
    required = {
        "run-manifest.json",
        "analysis-input.json",
        "implementation-review.md",
        "results-review.md",
        "recommendation-input.md",
    }
    _require(required.issubset(bindings), "Review evidence bindings missing")
    _require(
        bindings["run-manifest.json"] == manifest_hash,
        "Reviewed manifest binding does not match the supplied manifest",
    )
    for name, digest in bindings.items():
        _require(
            _digest(_read(directory / _relative(name))) == digest,
            f"Review/input hash mismatch: {name}",
        )
    analysis = _json(_read(directory / "analysis-input.json"))
    _require(
        analysis["run_manifest_sha256"] == manifest_hash,
        "Analysis manifest binding mismatch",
    )
    return _digest(validation_bytes), dict(sorted(bindings.items()))


def _fragmentation(
    rows: list[dict[str, Any]],
    spec: dict[str, Any],
    phase: str,
    cap: int,
    inputs: dict[tuple[int, int], Any],
) -> dict[str, Any]:
    config = spec["phases"][phase]
    expected = []
    for profile_id, confidence, graph_rep, opinion_rep, model in product(
        config["profiles"],
        config["confidences"],
        range(config["graph_replicates"]),
        range(config["opinion_replicates"]),
        ("uniform", "adaptive"),
    ):
        profile = spec["profiles"][profile_id]
        seed = (
            spec["seed_base"]
            + config["seed_offset"]
            + profile["seed_index"] * 10000
            + graph_rep * 100
        )
        expected.append(
            {
                "profile_id": profile_id,
                "profile": profile,
                "confidence": confidence,
                "graph_rep": graph_rep,
                "opinion_rep": opinion_rep,
                "model": model,
                "graph_seed": seed,
                "opinion_seed": seed + 10 + opinion_rep,
                "event_seed": seed + 20 + opinion_rep,
            }
        )
    if phase == "benchmark":
        expected = expected[:10]
    _require(
        len(rows) == len(expected), f"Declared fragmentation design incomplete: {phase}"
    )
    counts: Counter[str] = Counter()
    for index, (row, design) in enumerate(zip(rows, expected, strict=True)):
        _require(
            row["trial_index"] == index and all(row[k] == v for k, v in design.items()),
            f"Fragmentation trial identity mismatch: {phase}/{index}",
        )
        key = (row["graph_seed"], row["opinion_seed"])
        value = (row["base_edges"], row["initial_opinions"])
        _require(
            inputs.setdefault(key, value) == value, "Paired fragmentation inputs differ"
        )
        result = row["result"]
        status = result["status"]
        _require(
            status in {"certified", "right_censored", "numerical_failure"},
            "Unknown fragmentation outcome",
        )
        _require(
            type(result["attempts"]) is int and 1 <= result["attempts"] <= cap,
            "Invalid attempt count",
        )
        if status == "certified":
            _require(
                isinstance(result["certified_stop"], dict)
                and result["certified_stop"]["attempt"] == result["attempts"]
                and result["numerical_error"] is None,
                "Certified outcome lacks a valid stop",
            )
        elif status == "right_censored":
            _require(
                result["certified_stop"] is None
                and result["numerical_error"] is None
                and result["attempts"] == cap,
                "Censoring must reach the attempt cap without certification",
            )
        else:
            _require(
                isinstance(result["numerical_error"], str)
                and bool(result["numerical_error"]),
                "Numerical failure requires its diagnostic",
            )
        counts[status] += 1
    return {
        "outcomes": {
            status: counts[status]
            for status in ("certified", "right_censored", "numerical_failure")
        },
        "sampling_unit": "model rows paired within graph and opinion realizations",
    }


def _histogram(value: Any, sample_size: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 11
        and all(type(x) is int and x >= 0 for x in value)
        and sum(value) == sample_size
    )


def _seed(*parts: str | int) -> int:
    payload = json.dumps(parts, ensure_ascii=True, separators=(",", ":")).encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:16], "big")


def _forecast(
    rows: list[dict[str, Any]],
    spec: dict[str, Any],
    phase: str,
    data: dict[tuple[str, str, int], Any],
    members: int,
) -> set[tuple[str, str, int]]:
    config = spec["phases"][phase]
    models = spec["model_order"]
    _require(
        isinstance(models, list)
        and bool(models)
        and all(isinstance(model, str) and bool(model) for model in models)
        and len(set(models)) == len(models)
        and set(models) == set(spec["models"]),
        "Forecast models must match the declared unique model order",
    )
    score_names = {"mean_w1", "central_w1", "energy", "mean_l2", "central_l2"}
    expected = [
        (
            {
                "id": f"{truth}-a{attempts}-n{sample}",
                "truth": truth,
                "attempts": attempts,
                "sample_size": sample,
            },
            replicate,
        )
        for truth, attempts, sample, replicate in product(
            spec["truths"],
            spec["attempts"],
            spec["sample_sizes"],
            range(config["replicates"]),
        )
    ]
    _require(
        len(rows) == len(expected), f"Declared forecast design incomplete: {phase}"
    )
    seen = set()
    for row, (cell, replicate) in zip(rows, expected, strict=True):
        _require(
            row["cell"] == cell and row["replicate"] == replicate,
            f"Forecast cell/replicate mismatch: {phase}",
        )
        key = (config["data_group"], cell["id"], replicate)
        _require(key not in seen, "Duplicate forecast data identity in one run")
        seen.add(key)
        _require(
            len(row["waves"]) == spec["train_steps"] + spec["test_steps"],
            "Incomplete forecast waves",
        )
        selection = row["selected_on_train"]
        _require(
            isinstance(selection, dict)
            and set(selection) == score_names
            and all(model in models for model in selection.values()),
            "Training selections must bind each score to a declared model",
        )
        prior = [cell["sample_size"] // 11] * 11
        observed_data = []
        for index, wave in enumerate(row["waves"]):
            split = "train" if index < spec["train_steps"] else "test"
            _require(
                wave["wave"] == index and wave["split"] == split,
                "Forecast wave/split mismatch",
            )
            _require(wave["observed"] == prior, "Forecast observed history mismatch")
            for field in ("observed", "outcome"):
                _require(
                    _histogram(wave[field], cell["sample_size"]),
                    "Invalid observed histogram",
                )
            parts = (
                spec["seed"],
                "truth",
                config["data_group"],
                cell["id"],
                replicate,
                index,
            )
            _require(
                type(wave["data_seed"]) is int and wave["data_seed"] == _seed(*parts),
                "Forecast data seed does not match its declared identity",
            )
            forecasts = wave["forecasts"]
            _require(
                isinstance(forecasts, dict) and set(forecasts) == set(models),
                "Forecast outputs must cover exactly the declared models",
            )
            for model in models:
                forecast = forecasts[model]
                expected_seed = _seed(
                    spec["seed"], "forecast", phase, cell["id"], replicate, index, model
                )
                _require(
                    type(forecast["seed"]) is int and forecast["seed"] == expected_seed,
                    "Forecast seed does not match its model identity",
                )
                ensemble = forecast["ensemble"]
                _require(
                    isinstance(ensemble, list)
                    and len(ensemble) == members
                    and all(
                        _histogram(histogram, cell["sample_size"])
                        for histogram in ensemble
                    ),
                    "Forecast ensemble cardinality or histogram content is invalid",
                )
                scores = forecast["scores"]
                _require(
                    isinstance(scores, dict)
                    and set(scores) == score_names
                    and all(
                        type(value) in (int, float)
                        and -sys.float_info.max <= value <= sys.float_info.max
                        for value in scores.values()
                    ),
                    "Forecast score keys or finite numeric values are invalid",
                )
            observed_data.append(
                {
                    field: wave[field]
                    for field in ("wave", "split", "observed", "outcome", "data_seed")
                }
            )
            prior = wave["outcome"]
        _require(
            data.setdefault(key, observed_data) == observed_data,
            "Repeated forecast identity contains different observed data",
        )
    return seen


def _artifact(run: dict[str, Any], artifact_root: Path | None) -> Path:
    sha: str = run["sha256"]
    _require(
        isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{64}", sha) is not None,
        "Invalid artifact digest",
    )
    if artifact_root is None:
        return Path(run["location"])
    direct = artifact_root / sha
    return direct if direct.exists() else artifact_root / sha[:2] / sha


def _validate(
    manifest: Path, study_root: Path, artifact_root: Path | None
) -> dict[str, Any]:
    _require(
        manifest.resolve().is_relative_to(study_root.resolve()),
        "Manifest must be inside the declared study",
    )
    manifest_bytes = _read(manifest)
    metadata = _json(manifest_bytes)
    spec_bytes = _read(manifest.parent / "spec.json")
    spec = _json(spec_bytes)
    spec_hash = _digest(spec_bytes)
    _require(
        metadata["format"]
        in {"fragmentation-pilot-run-manifest-v1", "forecast-pilot-run-manifest-v1"},
        "Unsupported manifest format",
    )
    fragmentation = metadata["format"] == "fragmentation-pilot-run-manifest-v1"
    validation_hash, reviews = _reviews(
        manifest.parent, _digest(manifest_bytes), fragmentation
    )
    _require(
        spec["format"]
        == (
            "fragmentation-exploratory-spec-v1"
            if fragmentation
            else "probabilistic-forecast-pilot-spec-v1"
        ),
        "Unsupported spec format",
    )
    runs = []
    historical_sources: dict[str, dict[str, str]] = {}
    fragmentation_inputs: dict[tuple[int, int], Any] = {}
    forecast_data: dict[tuple[str, str, int], Any] = {}
    forecast_identities: dict[str, set[tuple[str, str, int]]] = {}
    analysis_records = benchmark_records = 0
    entries = (
        [
            {
                **v,
                "name": k,
                "phase": k,
                "location": v["artifact_path"],
                "bytes": v["size_bytes"],
            }
            for k, v in metadata["phases"].items()
        ]
        if fragmentation
        else metadata["runs"]
    )
    _require(bool(entries), "Manifest contains no runs")
    _require(
        len({run["name"] for run in entries}) == len(entries), "Duplicate run name"
    )
    _require(
        {run["phase"] for run in entries} == set(spec["phases"]),
        "Manifest does not cover declared phases",
    )
    if not fragmentation:
        primary_group = spec["phases"]["primary"]["data_group"]
        _require(
            spec["phases"]["precision"]["data_group"] == primary_group,
            "Precision must reuse primary data",
        )
        _require(
            spec["phases"]["confirmation"]["data_group"] != primary_group,
            "Confirmation must use separate data",
        )
        if "benchmark" in spec["phases"]:
            _require(
                spec["phases"]["benchmark"]["data_group"]
                not in {primary_group, spec["phases"]["confirmation"]["data_group"]},
                "Benchmark data must remain separate",
            )
    for run in sorted(entries, key=lambda item: item["name"]):
        name, phase = run["name"], run["phase"]
        data = _read(_artifact(run, artifact_root), 256 * 1024 * 1024)
        _require(_digest(data) == run["sha256"], f"Artifact hash mismatch: {name}")
        _require(len(data) == run["bytes"], f"Artifact size mismatch: {name}")
        records = [_json(line) for line in data.splitlines()]
        _require(len(records) >= 3, f"Missing run records: {name}")
        header, footer = records[0], records[-1]
        _require(
            header["record"] == "header" and footer["record"] == "completed",
            f"Missing header/completed footer: {name}",
        )
        _require(
            header["format"]
            == (
                "fragmentation-exploratory-run-v1"
                if fragmentation
                else "probabilistic-forecast-exploratory-v1"
            ),
            "Unsupported run format",
        )
        _require(header["spec"] == spec, f"Embedded specification mismatch: {name}")
        _require(
            header["spec_sha256"] == run["spec_sha256"] == spec_hash,
            f"Specification hash mismatch: {name}",
        )
        _require(
            header["code_revision"] == run["code_revision"],
            f"Revision mismatch: {name}",
        )
        revision = header["code_revision"]
        if revision not in historical_sources:
            historical_sources[revision] = _sources(study_root, revision)
        for path in header["source_sha256"]:
            _relative(path)
        _require(
            header["source_sha256"] == historical_sources[revision],
            f"Historical source/lock closure mismatch: {name}",
        )
        if not fragmentation:
            _require(
                run["source_sha256"] == header["source_sha256"],
                f"Manifest source closure mismatch: {name}",
            )
            _require(
                run["status"] == "completed", f"Manifest run not completed: {name}"
            )
        _require(
            header["environment"] == run["environment"], f"Environment mismatch: {name}"
        )
        _require(
            isinstance(header["environment"], dict)
            and all(
                isinstance(header["environment"].get(key), str)
                and bool(header["environment"][key].strip())
                for key in ("python", "platform", "machine", "rng")
            ),
            f"Incomplete recorded environment: {name}",
        )
        _require(
            header["phase"] == phase and phase in spec["phases"],
            f"Phase mismatch: {name}",
        )
        budget = "max_attempts" if fragmentation else "members"
        allowed = spec["phases"][phase][f"allowed_{budget}"]
        _require(
            type(header[budget]) is int
            and type(run[budget]) is int
            and header[budget] > 0
            and all(type(n) is int and n > 0 for n in allowed),
            f"Execution budget must contain positive integers: {name}",
        )
        _require(
            header[budget] == run[budget]
            and header[budget] in spec["phases"][phase][f"allowed_{budget}"],
            f"Execution budget mismatch: {name}",
        )
        rows = records[1:-1]
        _require(
            all(
                row["record"] == ("trial" if fragmentation else "trajectory")
                for row in rows
            ),
            f"Invalid record kind: {name}",
        )
        count_key = "trials" if fragmentation else "trajectories"
        _require(
            len(rows) == run[count_key] == footer[count_key],
            f"Record count mismatch: {name}",
        )
        details = {}
        if fragmentation:
            details = _fragmentation(
                rows, spec, phase, run[budget], fragmentation_inputs
            )
        else:
            identities = _forecast(rows, spec, phase, forecast_data, run[budget])
            forecast_identities.setdefault(phase, set()).update(identities)
            if phase == "benchmark":
                benchmark_records += len(rows)
            else:
                analysis_records += len(rows)
        runs.append(
            {
                "name": name,
                "phase": phase,
                "sha256": run["sha256"],
                "bytes": run["bytes"],
                "code_revision": revision,
                "source_sha256": historical_sources[revision],
                "environment": header["environment"],
                "records": len(rows),
                **details,
            }
        )
    receipt = {
        "format": "offline-experiment-validation-v1",
        "status": "integrity_verified",
        "scientific_acceptance": False,
        "manifest_sha256": _digest(manifest_bytes),
        "spec_sha256": spec_hash,
        "validation_sha256": validation_hash,
        "review_evidence": reviews,
        "runs": runs,
        "regeneration_performed": False,
        "scope": (
            "Artifact integrity and recorded identity consistency; no score "
            "recalculation, scientific review, novelty assessment or owner approval"
        ),
    }
    if not fragmentation:
        _require(
            forecast_identities["primary"] == forecast_identities["precision"],
            "Precision and primary must contain exactly the same data identities",
        )
        distinct_analysis = sum(
            key[0] != spec["phases"].get("benchmark", {}).get("data_group")
            for key in forecast_data
        )
        receipt["forecast_data"] = {
            "analysis_trajectory_records": analysis_records,
            "distinct_analysis_data_trajectories": distinct_analysis,
            "repeated_analysis_data_trajectories": analysis_records - distinct_analysis,
            "benchmark_trajectory_records": benchmark_records,
            "statistical_independence_verified": False,
        }
    return receipt


def validate_experiment(
    manifest: Path, *, study_root: Path, artifact_root: Path | None = None
) -> dict[str, Any]:
    """Check immutable pilot artifacts; never regenerate their trajectories."""
    try:
        return _validate(manifest, study_root, artifact_root)
    except ExperimentValidationError:
        raise
    except (KeyError, TypeError, ValueError, RecursionError, AttributeError) as exc:
        raise ExperimentValidationError(f"Malformed experiment record: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--study-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        receipt = validate_experiment(
            args.manifest, study_root=args.study_root, artifact_root=args.artifact_root
        )
        content = (
            json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + "\n"
        ).encode()
        descriptor = os.open(args.receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
        print(
            json.dumps(
                {"status": "integrity_verified", "receipt_sha256": _digest(content)}
            )
        )
        return 0
    except ExperimentArtifactsUnavailableError as exc:
        print(json.dumps({"status": "unavailable", "error": str(exc)}), file=sys.stderr)
        return 2
    except (ExperimentValidationError, OSError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
