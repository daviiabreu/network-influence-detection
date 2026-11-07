"""Audit the downloadable OSF tables without copying their contents into Git."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

FILES = {
    "ESSdataset+calibrated.csv": (
        "6b51c8cd535103e5f20b924ac40443f761885cfe2fd4b0204786a4161035feb7"
    ),
    "SHPdataset+calibrated.csv": (
        "521124758cf6da52cbc4c940215abe3fc0edf13cb767351e8678283653b0123f"
    ),
    "Simulations.csv": (
        "195134f179cc173e172840c766b9114e74767bdea5f5c7a80d5d0c5990a45ab4"
    ),
}


def read_rows(path: Path, expected_hash: str) -> list[dict[str, str]]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_hash:
        raise ValueError(f"SHA-256 mismatch: {path.name}: {digest}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def audit(cache_dir: Path) -> dict:
    ess = read_rows(
        cache_dir / "ESSdataset+calibrated.csv", FILES["ESSdataset+calibrated.csv"]
    )
    shp = read_rows(
        cache_dir / "SHPdataset+calibrated.csv", FILES["SHPdataset+calibrated.csv"]
    )
    simulations = read_rows(cache_dir / "Simulations.csv", FILES["Simulations.csv"])
    shp_years = sorted(int(row["Year"]) for row in shp if row["Year"].isdigit())
    return {
        "sha256_verified": FILES,
        "ess": {
            "rows": len(ess),
            "topic_counts": dict(sorted(Counter(row["topic"] for row in ess).items())),
            "years": sorted({int(row["Year"]) for row in ess}),
        },
        "shp": {
            "rows": len(shp),
            "numeric_years": shp_years,
            "other_rows": sorted(
                row["Year"] for row in shp if not row["Year"].isdigit()
            ),
            "r2_range": [
                min(float(row["R2"]) for row in shp),
                max(float(row["R2"]) for row in shp),
            ],
        },
        "simulations": {
            "rows": len(simulations),
            "parameter_ids": len({row["parameterid"] for row in simulations}),
            "parameter_run_pairs": len(
                {(row["parameterid"], row["run"]) for row in simulations}
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.cache_dir), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
