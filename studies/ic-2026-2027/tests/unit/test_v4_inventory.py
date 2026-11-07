from ic_study.simulation.v4_plan import gate_tasks, inventory


def test_inventory_keeps_all_families_controls_and_sensitivities() -> None:
    units = inventory()
    assert len({row["id"] for row in units}) == len(units) == 3726
    assert sum(row["tier"] == 1 for row in units) == 81
    assert sum(row["tier"] == 2 for row in units) == 324
    assert sum(row["tier"] == 6 for row in units) == 81
    assert {row["family"] for row in units if row["channel"] == "latent_rank"} == set(
        "ABCDE"
    )
    assert sum(row["sensitivity"] == "c050-d020-exploratory" for row in units) == 81


def test_gate_allocations_have_real_denominators_and_shards_are_disjoint() -> None:
    assert len(gate_tasks("G0")) == 81
    assert len(gate_tasks("G1b")) == 5000
    assert len(gate_tasks("G1c")) == 150
    assert len(gate_tasks("G2")) == 700
    assert len(gate_tasks("G2c")) == 142


def test_substitution_moves_toward_center_without_reusing_existing_cell() -> None:
    from ic_study.simulation.v4_plan import G2_CELLS, substitute_cells

    eligible = set(G2_CELLS) - {(0.03, 0.5), (0.03, 0.9)}
    eligible |= {(0.03, 0.55), (0.03, 0.85)}
    result = substitute_cells(eligible)
    assert result[-2:] == [(0.03, 0.55), (0.03, 0.85)]
    assert len(set(result)) == 7
    assert len(substitute_cells(set(G2_CELLS) - {(0.03, 0.5)})) == 6
