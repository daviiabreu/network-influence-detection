"""Bounded measurement driver; scientific functions live in the study package."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from ic_study.analysis.redesign import fit_discriminant
from ic_study.simulation.amendment_a import (
    NAMESPACE,
    calibration_profiles,
    cluster_auc_se,
    constrained_match,
    fixed_jacobian_match,
)


def serial(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value))


def match_job(
    share: float, block: int, count: int, multiplier: float, restart: bool = False
) -> dict[str, Any]:
    started = time.perf_counter()
    cpu = time.process_time()
    target = calibration_profiles(share, 0.7, count, block=block, phase="match", lags=2)
    fit = constrained_match(
        target,
        lambda rho, trait: calibration_profiles(
            share, 0.7, count, block=block, phase="match", rho=rho, trait=trait, lags=2
        ),
        mc_multiplier=multiplier,
    )
    first = asdict(fit)
    if restart and not fit.success:
        fit = constrained_match(
            target,
            lambda rho, trait: calibration_profiles(
                share,
                0.7,
                count,
                block=block,
                phase="match",
                rho=rho,
                trait=trait,
                lags=2,
            ),
            mc_multiplier=multiplier,
            initial=(0.8, 0.1),
        )
    row = asdict(fit)
    row["initial_attempt"] = first
    row.update(
        share=share,
        block=block,
        count=count,
        multiplier=multiplier,
        target_sd=target.std(0, ddof=1),
        target_se=target.std(0, ddof=1) / np.sqrt(count),
        seconds=time.perf_counter() - started,
        cpu_seconds=time.process_time() - cpu,
    )
    return row


def reference_job(share: float, start: int, count: int, label: int) -> np.ndarray:
    return calibration_profiles(
        share,
        0.7,
        count,
        block=0,
        phase="reference",
        start=start,
        rho=0.85 if label == 0 else None,
    )[:, 2:5]


def refit_job(share: float, block: int, output: str) -> dict[str, Any]:
    start = time.perf_counter()
    cpu = time.process_time()
    response = json.loads((Path(output) / f"matching-map-{share}.json").read_text())
    target = calibration_profiles(share, 0.7, 256, block=block, phase="match", lags=2)
    matched = fixed_jacobian_match(
        target,
        lambda rho, trait: calibration_profiles(
            share, 0.7, 256, block=block, phase="match", rho=rho, trait=trait, lags=2
        ),
        np.array(response["jacobian"]),
        initial=tuple(response["initial"]),
    )
    row = asdict(matched)
    row.update(
        share=share,
        block=block,
        count=256,
        multiplier=2,
        seconds=time.perf_counter() - start,
        method="independent_fixed_jacobian",
    )
    row["matching_seconds"] = row["seconds"]
    if not row["success"]:
        row["stage"] = "matching_failed"
        return row
    fit = {"rho": row["rho"], "trait": row["trait"]}
    started = time.perf_counter()
    null = calibration_profiles(share, 0.7, 2000, block=block, phase="train", **fit)[
        :, 2:5
    ]
    social = calibration_profiles(share, 0.7, 2000, block=block, phase="train")[:, 2:5]
    model = fit_discriminant(np.concatenate((null, social)), np.repeat([0, 1], 2000))
    row["training_seconds"] = time.perf_counter() - started
    started = time.perf_counter()
    null_ref = calibration_profiles(
        share, 0.7, 4000, block=block, phase="reference", **fit
    )[:, 2:5]
    social_ref = np.load(Path(output) / f"social-{share}.npy")
    scores0, scores1 = model.score(null_ref), model.score(social_ref)
    row["auc"], row["reference_se"] = cluster_auc_se(
        scores0.reshape(-1, 2), scores1.reshape(-1, 2)
    )
    row["reference_seconds"] = time.perf_counter() - started
    row["seconds"] = time.perf_counter() - start
    row["cpu_seconds"] = time.process_time() - cpu
    if block == 1:
        with (Path(output) / f"refit-data-{share}.npz").open("xb") as stream:
            np.savez_compressed(
                stream,
                null_train=null,
                social_train=social,
                null_reference=null_ref,
                social_reference=social_ref,
                scores0=scores0,
                scores1=scores1,
            )
    row["stage"] = "complete"
    return row


def stencil_job(task: tuple[float, float, int, str]) -> dict[str, Any]:
    from local_probe import stencil

    path = Path(task[3]) / f"refit-{task[0]}-1.json"
    started = time.monotonic()
    while not path.exists():
        if time.monotonic() - started > 600:
            raise TimeoutError(
                "Baseline refit did not finish within the stencil budget"
            )
        time.sleep(1)
    return stencil(task)


def save(path: Path, value: Any) -> None:
    with path.open("x") as stream:
        json.dump(value, stream, default=serial, indent=2)
        stream.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--stage", choices=["matching", "reference", "refits", "zero"], required=True
    )
    args = parser.parse_args()
    os.umask(0o077)
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.time()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    futures: dict[Any, str] = {}
    with ProcessPoolExecutor(max_workers=8) as pool:
        if args.stage == "matching":
            for a in (0.0, 0.03, 0.1):
                for n in (256, 1024):
                    for b in range(1, 9):
                        name = f"match-{a}-{n}-{b}"
                        futures[pool.submit(match_job, a, b, n, 0)] = name
        elif args.stage == "reference":
            for a in (0.03, 0.1):
                futures[pool.submit(reference_job, a, 0, 4000, 1)] = f"social-{a}"
        elif args.stage == "refits":
            while not (args.output / "matching-map-0.1.json").exists():
                time.sleep(1)
            jobs = [(0.1, b) for b in range(1, 41)] + [(0.03, 1)]
            for a, b in jobs:
                futures[pool.submit(refit_job, a, b, str(args.output))] = (
                    f"refit-{a}-{b}"
                )
            for a in (0.1, 0.03):
                for h in (0.005, 0.01):
                    for j in (0, 1):
                        futures[
                            pool.submit(stencil_job, (a, h, j, str(args.output)))
                        ] = f"stencil-{a}-{h}-{j}"
            for b in range(2, 21):
                futures[pool.submit(refit_job, 0.03, b, str(args.output))] = (
                    f"refit-0.03-{b}"
                )
        else:
            for label in (0, 1):
                for chunk in range(8):
                    futures[
                        pool.submit(reference_job, 0.0, chunk * 5000, 5000, label)
                    ] = f"zero-{label}-{chunk}"
        for future in as_completed(futures):
            name = futures[future]
            try:
                row = future.result()
                if isinstance(row, np.ndarray):
                    with (args.output / f"{name}.npy").open("xb") as stream:
                        np.save(stream, row)
                    print(name, "saved", flush=True)
                else:
                    save(args.output / f"{name}.json", row)
                    print(
                        name, row.get("success"), round(row["seconds"], 2), flush=True
                    )
            except Exception as exc:
                save(args.output / f"{name}.json", {"error": repr(exc)})
                print(name, "ERROR", repr(exc), flush=True)
    save(
        args.output / f"stage-{args.stage}.json",
        {
            "namespace": NAMESPACE,
            "started_epoch": started,
            "wall_seconds": time.time() - started,
            "workers": 8,
            "revision": revision,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "python": platform.python_version(),
        },
    )


if __name__ == "__main__":
    main()
