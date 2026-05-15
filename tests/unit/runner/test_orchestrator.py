"""Unit tests for the encounter batch orchestrator."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.actions import Action, WeaponAttackAction
from balance_framework.runner.orchestrator import run_encounter_batch
from balance_framework.runner.collector import EncounterResult


def _hero(hp: int = 50) -> CombatantState:
    return CombatantState(
        id="hero", display_name="Hero", team="party",
        hp_max=hp, hp_current=hp, ac=18,
        proficiency_bonus=3, extra_attack_count=2,
        ability_modifiers={"STR": 4, "DEX": 2},
        behavior_profile="martial",
        resources={"second_wind": 1, "action_surge": 1},
    )


def _goblin(id: str) -> CombatantState:
    return CombatantState(
        id=id, display_name=id, team="enemies",
        hp_max=7, hp_current=7, ac=13,
        proficiency_bonus=2, extra_attack_count=1,
        ability_modifiers={"STR": -1, "DEX": 2},
        behavior_profile="monster_melee",
    )


def _simple_factory(seed: int) -> ScenarioState:
    return ScenarioState(
        combatants=[_hero(), _goblin("g1"), _goblin("g2")],
        dice=Dice(seed),
    )


def _attack_selector(combatant: CombatantState, scenario: ScenarioState) -> list[Action] | None:
    enemies = [c for c in scenario.living_combatants() if c.team != combatant.team]
    if not enemies:
        return None
    return [WeaponAttackAction(
        attacker_id=combatant.id, target_id=enemies[0].id,
        attack_bonus=6, damage_dice=[(1, 8)], damage_type="slashing", damage_bonus=4,
    )]


# ---------------------------------------------------------------------------
# Basic batch properties
# ---------------------------------------------------------------------------

def test_batch_returns_correct_count() -> None:
    results = run_encounter_batch(_simple_factory, _attack_selector, n=5, base_seed=0)
    assert len(results) == 5


def test_batch_seeds_match() -> None:
    results = run_encounter_batch(_simple_factory, _attack_selector, n=5, base_seed=100)
    assert [r.seed for r in results] == [100, 101, 102, 103, 104]


def test_batch_all_complete() -> None:
    results = run_encounter_batch(_simple_factory, _attack_selector, n=10, base_seed=0)
    # Hero is strong — all should finish within max_rounds
    assert all(not r.timed_out for r in results)


def test_batch_deterministic() -> None:
    r1 = run_encounter_batch(_simple_factory, _attack_selector, n=10, base_seed=42)
    r2 = run_encounter_batch(_simple_factory, _attack_selector, n=10, base_seed=42)
    assert [(r.winner_team, r.rounds) for r in r1] == [(r.winner_team, r.rounds) for r in r2]


def test_batch_different_seeds_produce_variation() -> None:
    results = run_encounter_batch(_simple_factory, _attack_selector, n=30, base_seed=0)
    round_counts = {r.rounds for r in results}
    # Should see some variation in combat length
    assert len(round_counts) > 1


def test_batch_n1_returns_one_result() -> None:
    results = run_encounter_batch(_simple_factory, _attack_selector, n=1, base_seed=0)
    assert len(results) == 1
    assert isinstance(results[0], EncounterResult)


def test_batch_max_rounds_respected() -> None:
    # Make both sides unkillable to force timeout
    def immortal_factory(seed: int) -> ScenarioState:
        hero = CombatantState(
            id="h", display_name="H", team="party",
            hp_max=10000, hp_current=10000, ac=30,
        )
        enemy = CombatantState(
            id="e", display_name="E", team="enemies",
            hp_max=10000, hp_current=10000, ac=30,
        )
        return ScenarioState(combatants=[hero, enemy], dice=Dice(seed))

    results = run_encounter_batch(immortal_factory, _attack_selector, n=3, max_rounds=2)
    assert all(r.timed_out for r in results)
    assert all(r.rounds == 2 for r in results)
