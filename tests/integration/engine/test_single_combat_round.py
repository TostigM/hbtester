"""Integration tests for single-round and short-encounter combat."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.resolver import run_combat, run_combat_round
from balance_framework.engine.combat.actions import WeaponAttackAction, Action


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fighter(id: str, team: str, hp: int = 20, ac: int = 14) -> CombatantState:
    return CombatantState(
        id=id, display_name=id.capitalize(), team=team,
        hp_max=hp, hp_current=hp,
        ac=ac, speed=30, proficiency_bonus=2,
        ability_modifiers={"DEX": 2, "STR": 3, "CON": 2},
    )


def _attack_all_enemies(combatant: CombatantState, scenario: ScenarioState) -> list[Action] | None:
    """Always attack the first living enemy."""
    enemies = [c for c in scenario.living_combatants() if c.team != combatant.team]
    if not enemies:
        return None
    target = enemies[0]
    return [WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=5,
        damage_dice=[(1, 8)],
        damage_type="slashing",
        damage_bonus=3,
    )]


# ---------------------------------------------------------------------------
# Round counter
# ---------------------------------------------------------------------------

def test_run_combat_increments_round() -> None:
    party = [_fighter("hero", "party")]
    enemy = [_fighter("goblin", "enemies", hp=1, ac=5)]
    scenario = ScenarioState(combatants=party + enemy, dice=Dice(42))
    run_combat(scenario, _attack_all_enemies, max_rounds=5)
    assert scenario.round_number >= 1


# ---------------------------------------------------------------------------
# Combat ends when one team is eliminated
# ---------------------------------------------------------------------------

def test_combat_ends_when_enemy_dies() -> None:
    party = [_fighter("hero", "party", hp=100, ac=20)]
    # Very low HP enemy dies quickly
    enemy = [_fighter("goblin", "enemies", hp=1, ac=1)]
    scenario = ScenarioState(combatants=party + enemy, dice=Dice(7))
    run_combat(scenario, _attack_all_enemies, max_rounds=20)
    assert scenario.is_over
    assert scenario.winner_team == "party"


def test_combat_ends_when_party_dies() -> None:
    # Hero with 1 HP and AC 1 dies in one hit from anything
    party = [_fighter("hero", "party", hp=1, ac=1)]
    enemy = [_fighter("ogre", "enemies", hp=100, ac=20)]
    scenario = ScenarioState(combatants=party + enemy, dice=Dice(7))
    run_combat(scenario, _attack_all_enemies, max_rounds=20)
    assert scenario.is_over
    assert scenario.winner_team == "enemies"


# ---------------------------------------------------------------------------
# max_rounds cap
# ---------------------------------------------------------------------------

def test_combat_stops_at_max_rounds() -> None:
    # Both sides have very high HP and AC so nobody dies
    party = [_fighter("hero", "party", hp=1000, ac=25)]
    enemy = [_fighter("ogre", "enemies", hp=1000, ac=25)]
    scenario = ScenarioState(combatants=party + enemy, dice=Dice(0))
    run_combat(scenario, _attack_all_enemies, max_rounds=3)
    assert scenario.round_number == 3
    assert not scenario.is_over


# ---------------------------------------------------------------------------
# Events are logged
# ---------------------------------------------------------------------------

def test_events_logged_during_combat() -> None:
    party = [_fighter("hero", "party", hp=50)]
    enemy = [_fighter("goblin", "enemies", hp=1, ac=1)]
    scenario = ScenarioState(combatants=party + enemy, dice=Dice(42))
    run_combat(scenario, _attack_all_enemies, max_rounds=10)
    assert len(scenario.events) > 0
    assert any("INITIATIVE" in e.upper() for e in scenario.events)


# ---------------------------------------------------------------------------
# Two-sided combat with multiple combatants
# ---------------------------------------------------------------------------

def test_two_vs_two_combat_resolves() -> None:
    party = [_fighter("hero1", "party"), _fighter("hero2", "party")]
    enemies = [_fighter("orc1", "enemies", hp=8), _fighter("orc2", "enemies", hp=8)]
    scenario = ScenarioState(combatants=party + enemies, dice=Dice(123))
    run_combat(scenario, _attack_all_enemies, max_rounds=20)
    assert scenario.is_over
    assert scenario.winner_team is not None


# ---------------------------------------------------------------------------
# Dead combatants are skipped
# ---------------------------------------------------------------------------

def test_dead_combatant_skipped() -> None:
    alive = _fighter("hero", "party", hp=100)
    dead = _fighter("ally", "party", hp=10)
    dead.is_alive = False
    enemy = _fighter("goblin", "enemies", hp=1, ac=1)
    scenario = ScenarioState(combatants=[alive, dead, enemy], dice=Dice(1))
    run_combat(scenario, _attack_all_enemies, max_rounds=10)
    # dead combatant should still be dead and unchanged
    assert not dead.is_alive


# ---------------------------------------------------------------------------
# initiative order is set
# ---------------------------------------------------------------------------

def test_initiative_order_set_after_run() -> None:
    party = [_fighter("hero", "party")]
    enemy = [_fighter("goblin", "enemies")]
    scenario = ScenarioState(combatants=party + enemy, dice=Dice(0))
    run_combat(scenario, _attack_all_enemies, max_rounds=5)
    assert len(scenario.initiative_order) == 2
    assert "hero" in scenario.initiative_order
    assert "goblin" in scenario.initiative_order
