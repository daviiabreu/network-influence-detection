from __future__ import annotations

import json
from typing import Any

import numpy as np
import pytest

from ic_study.analysis.shp_reliability import (
    STARTS_FAILURES,
    YEARS,
    _polychoric_pair,
    _starts_failure_reasons,
    analyze_panel,
    load_person_files,
    starts_sensitivity,
)


def synthetic_panel(n: int = 2400, seed: int = 18) -> np.ndarray:
    rng = np.random.default_rng(seed)
    latent = np.empty((n, 5))
    latent[:, 0] = rng.normal(0, 1, n)
    for wave in range(1, 5):
        latent[:, wave] = 0.8 * latent[:, wave - 1] + rng.normal(0, 0.6, n)
    observed = latent + rng.normal(0, np.sqrt(0.25), latent.shape)
    observed += 5
    for wave in range(1, 5):
        gone = rng.random(n) < (0.11 + 0.02 * wave)
        observed[gone, wave:] = np.nan
    return observed


def test_fiml_recovers_known_reliability_with_attrition() -> None:
    panel = synthetic_panel()
    result = analyze_panel(panel, years=tuple(range(1999, 2004)))
    anchor = result["anchor"]
    assert isinstance(anchor, dict)
    assert abs(anchor["estimate"] - 0.8) < 0.09
    assert 0 < anchor["standard_error"] < 0.12
    assert len(result["triplets"]) == 3
    assert result["n_per_wave"]["2003"] < result["n_per_wave"]["1999"]


def test_empty_restricted_directory_fails_clearly(tmp_path: object) -> None:
    from pathlib import Path

    directory = Path(str(tmp_path))
    directory.chmod(0o700)
    with pytest.raises(ValueError, match=r"empty|vazio"):
        load_person_files(directory)


def test_reader_uses_variable_names_and_never_returns_ids(tmp_path: object) -> None:
    import csv
    from pathlib import Path

    directory = Path(str(tmp_path))
    directory.chmod(0o700)
    for year in range(1999, 2002):
        code = str(year)[-2:]
        with (directory / f"SHP{code}_P_USER.csv").open("w", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=[f"P{code}P04", "idpers"])
            writer.writeheader()
            writer.writerow({"idpers": "secret-id", f"P{code}P04": "6"})
    panel, years = load_person_files(directory, years=(1999, 2000, 2001))
    assert years == (1999, 2000, 2001)
    assert panel.shape == (1, 3)
    assert panel.tolist() == [[6.0, 6.0, 6.0]]


def test_polychoric_recovers_rounded_normal_correlation() -> None:
    rng = np.random.default_rng(49)
    left = rng.normal(size=1500)
    right = 0.7 * left + np.sqrt(0.51) * rng.normal(size=1500)
    left_scale = np.clip(np.rint(5 + 1.5 * left), 0, 10)
    right_scale = np.clip(np.rint(5 + 1.5 * right), 0, 10)
    assert abs(_polychoric_pair(left_scale, right_scale) - 0.7) < 0.08


# Successor 1 -----------------------------------------------------------------


def starts_panel(
    n: int,
    *,
    trait: float,
    initial: float,
    innovation: float,
    error: float,
    phi: float,
    seed: int,
    centre: float = 0.0,
) -> np.ndarray:
    """Trait + AR(1) state + error over 1999-2009 with SHP-like missingness.

    A third of the people enter in 2004, 10% of the rest drop out per wave and 3%
    of answers are missing at random, so patterns are monotone and intermittent.
    ``centre`` subtracts that share of each person's mean before missingness.
    """
    rng = np.random.default_rng(seed)
    waves = 11
    state = np.empty((n, waves))
    state[:, 0] = rng.normal(0, np.sqrt(initial), n)
    for wave in range(1, waves):
        state[:, wave] = phi * state[:, wave - 1] + rng.normal(
            0, np.sqrt(innovation), n
        )
    observed = state + rng.normal(0, np.sqrt(error), state.shape)
    observed += rng.normal(0, np.sqrt(trait), (n, 1))
    observed -= centre * observed.mean(axis=1, keepdims=True)
    observed += 5
    entry = np.where(rng.random(n) < 2 / 3, 0, 5)
    active = np.ones(n, dtype=bool)
    for wave in range(waves):
        active &= ~((rng.random(n) < 0.1) & (entry < wave))
        observed[(entry > wave) | ~active, wave] = np.nan
    observed[rng.random(observed.shape) < 0.03] = np.nan
    return observed


def test_starts_recovers_known_trait_state_and_error() -> None:
    truth = {"trait": 1.0, "initial": 1.5, "innovation": 0.6, "error": 1.0}
    panel = starts_panel(4000, **truth, phi=0.6, seed=3)
    state = [truth["initial"]]
    for _ in range(10):
        state.append(0.36 * state[-1] + truth["innovation"])
    latent = truth["trait"] + state[5]
    r_2004 = latent / (latent + truth["error"])
    result = starts_sensitivity(panel, YEARS)
    assert result["status"] == "admissible"
    anchor = result["anchor"]
    assert anchor["year"] == 2004
    assert abs(anchor["estimate"] - r_2004) < 0.03
    lo, hi = anchor["wald_95_interval"]
    assert lo < r_2004 < hi and 0 < anchor["standard_error"] < 0.03
    assert anchor["estimate"] == result["reliability"][5]
    assert all(0 < se < 0.03 for se in result["standard_error"])
    assert abs(result["trait_variance"] - truth["trait"]) < 0.15
    assert abs(result["initial_state_variance"] - truth["initial"]) < 0.25
    assert abs(result["innovation_variance"] - truth["innovation"]) < 0.1
    assert abs(result["error_variance"] - truth["error"]) < 0.1
    assert abs(result["persistence"] - 0.6) < 0.06
    share = result["trait_share_of_latent_variance"]
    assert share["year"] == 2004
    assert abs(share["value"] - truth["trait"] / latent) < 0.06
    assert result["aic"] < result["bic"] and result["log_likelihood"] < 0
    assert result["max_complete_case_correlation_residual"] < 0.1
    assert result["diagnostics"]["min_information_eigenvalue"] > 0


def test_starts_boundary_trait_is_a_failure_record_not_a_clipped_value() -> None:
    """Long-lag covariances below any trait push the trait variance to its bound."""
    panel = starts_panel(
        1500,
        trait=0.0,
        initial=1.0,
        innovation=0.64,
        error=0.64,
        phi=0.6,
        seed=8,
        centre=0.2,
    )
    scale = np.clip(np.round(5 + 1.3 * (panel - 5)), 0, 10)
    result = analyze_panel(scale, YEARS, include_successor=True)
    assert 0 < result["anchor"]["estimate"] < 1  # the analysis was not aborted
    starts = result["successor_1"]["starts_sensitivity"]
    assert starts["status"] == "failed"
    assert STARTS_FAILURES[2] in starts["reasons"]
    assert "trait_variance" in starts["diagnostics"]["variances_below_floor"]
    assert "anchor" not in starts and "standard_error" not in starts
    floor = starts["diagnostics"]["variance_floor"]
    assert starts["solution_at_termination"]["trait_variance"] < floor
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ({"converged": False}, 0),
        ({"information_positive": False}, 1),
        ({"variances": {"error_variance": 0.99e-4}}, 2),
        ({"persistence": 0.9901}, 3),
        ({"persistence": -0.995}, 3),
        ({"reliability": np.array([0.5, 1.0])}, 4),
        ({"reliability": np.array([0.0, 0.5])}, 4),
        ({"reliability": np.array([np.nan, 0.5])}, 4),
    ],
)
def test_starts_failure_rules_are_the_declared_ones(
    change: dict[str, Any], reason: int
) -> None:
    admissible: dict[str, Any] = {
        "converged": True,
        "information_positive": True,
        "variances": dict.fromkeys(("trait_variance", "error_variance"), 1e-4),
        "floor": 1e-4,
        "persistence": 0.99,
        "reliability": np.array([1e-9, 1 - 1e-9]),
    }
    assert _starts_failure_reasons(**admissible) == []
    assert _starts_failure_reasons(**(admissible | change)) == [STARTS_FAILURES[reason]]


def test_successor_sections_leave_every_primary_output_unchanged() -> None:
    panel = synthetic_panel()
    years = tuple(range(1999, 2004))
    before = analyze_panel(panel, years)
    after = analyze_panel(panel, years, include_successor=True)
    assert set(after) - set(before) == {"successor_1"}
    assert {key: after[key] for key in before} == before
    description = after["successor_1"]["wave_2004_description"]
    assert description["status"].startswith("not applicable")


def test_wave_2004_description_and_first_answer_2004_edge_fit() -> None:
    rng = np.random.default_rng(21)
    n = 3000
    latent = np.empty((n, 11))
    latent[:, 0] = rng.normal(0, 1, n)
    for wave in range(1, 11):
        latent[:, wave] = 0.8 * latent[:, wave - 1] + rng.normal(0, 0.6, n)
    panel = latent + rng.normal(0, 0.5, latent.shape) + 5
    panel[: n // 3, :5] = np.nan  # refreshment entrants
    panel[n // 3 : n // 3 + 60, :5] = np.nan  # item nonresponse until 2004
    panel[n // 3 + 60 : n // 3 + 90, :6] = np.nan  # first answer in 2005
    panel[rng.random(panel.shape) < 0.05] = np.nan
    result = analyze_panel(np.clip(panel, 0, 10), YEARS, include_successor=True)
    description = result["successor_1"]["wave_2004_description"]
    multiwave = result["multiwave"]
    for year in (2003, 2004, 2005):
        index = YEARS.index(year)
        assert description["primary_fit"][str(year)] == {
            "estimate": multiwave["reliability"][index],
            "standard_error": multiwave["standard_error"][index],
        }
    edge = description["first_valid_answer_2004"]
    observed = np.isfinite(panel)
    first = np.argmax(observed, axis=1)
    expected = int(np.sum(observed.any(axis=1) & (first == YEARS.index(2004))))
    assert edge["status"] == "estimated" and edge["n_people"] == expected
    assert edge["years"] == list(range(2004, 2010))
    assert edge["label"].startswith("edge estimate")
    assert edge["estimate"] == edge["fit"]["reliability"][0]
    stationary = 0.36 / (1 - 0.64)  # latent variance of the stationary AR(1)
    assert abs(edge["estimate"] - stationary / (stationary + 0.25)) < 0.05
