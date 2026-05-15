"""Unit tests for the healer behavior heuristic."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.actions import WeaponAttackAction, HealAction
from balance_framework.engine.combat.damage import apply_damage
from balance_framework.ai.heuristics.healer import healer_selector


def _cleric(resources: dict | None = None) -> CombatantState:
    return CombatantState(
        id="cleric", display_name="Cleric", team="party",
        hp_max=38, hp_current=38, ac=17,
        proficiency_bonus=3, ability_modifiers={"WIS": 3, "STR": 2, "CON": 2},
        behavior_profile="healer",
        resources=dict(resources or {"spell_slot_1": 4}),
    )


def _ally(id: str, hp: int = 30, hp_current: int | None = None) -> CombatantState:
    return CombatantState(
        id=id, display_name=id.capitalize(), team="party",
        hp_max=hp, hp_current=hp if hp_current is None else hp_current, ac=14,
    )


def _enemy(id: str = "orc") -> CombatantState:
    return CombatantState(
        id=id, display_name=id.capitalize(), team="enemies",
        hp_max=15, hp_current=15, ac=13,
    )


def _scenario(*combatants: CombatantState) -> ScenarioState:
    s = ScenarioState(combatants=list(combatants), dice=Dice(0))
    s.initiative_order = [c.id for c in combatants]
    return s


# ---------------------------------------------------------------------------
# Healing unconscious ally
# ---------------------------------------------------------------------------

def test_healer_heals_unconscious_ally_first() -> None:
    cleric = _cleric()
    ally = _ally("fighter", hp=30)
    apply_damage(ally, 30, "slashing")  # knock out
    assert not ally.is_conscious
    enemy = _enemy()
    scenario = _scenario(cleric, ally, enemy)
    actions = healer_selector(cleric, scenario)
    assert actions is not None
    assert len(actions) == 1
    assert isinstance(actions[0], HealAction)
    assert actions[0].target_id == "fighter"


def test_healer_uses_spell_slot_to_heal() -> None:
    from balance_framework.engine.combat.actions import resolve_action
    cleric = _cleric(resources={"spell_slot_1": 2})
    ally = _ally("fighter", hp=30)
    apply_damage(ally, 30, "slashing")
    scenario = _scenario(cleric, ally, _enemy())
    actions = healer_selector(cleric, scenario)
    assert actions is not None
    resolve_action(actions[0], scenario)
    assert cleric.resources["spell_slot_1"] == 1  # slot spent during resolution


# ---------------------------------------------------------------------------
# Healing bloodied ally
# ---------------------------------------------------------------------------

def test_healer_heals_bloodied_ally() -> None:
    cleric = _cleric()
    ally = _ally("fighter", hp=30, hp_current=5)  # < 30%
    enemy = _enemy()
    scenario = _scenario(cleric, ally, enemy)
    actions = healer_selector(cleric, scenario)
    assert actions is not None
    heal = [a for a in actions if isinstance(a, HealAction)]
    assert len(heal) == 1
    assert heal[0].target_id == "fighter"


def test_healer_does_not_heal_healthy_ally() -> None:
    cleric = _cleric()
    ally = _ally("fighter", hp=30, hp_current=25)  # > 30%
    enemy = _enemy()
    scenario = _scenario(cleric, ally, enemy)
    actions = healer_selector(cleric, scenario)
    # Should attack instead
    assert actions is not None
    assert all(isinstance(a, WeaponAttackAction) for a in actions)


# ---------------------------------------------------------------------------
# Attacks when no one needs healing
# ---------------------------------------------------------------------------

def test_healer_attacks_when_no_healing_needed() -> None:
    cleric = _cleric()
    ally = _ally("fighter")  # full HP
    enemy = _enemy()
    scenario = _scenario(cleric, ally, enemy)
    actions = healer_selector(cleric, scenario)
    assert actions is not None
    assert any(isinstance(a, WeaponAttackAction) for a in actions)


def test_healer_attacks_enemy_when_no_spell_slots() -> None:
    cleric = _cleric(resources={"spell_slot_1": 0})
    ally = _ally("fighter", hp_current=1)  # would normally heal
    enemy = _enemy()
    scenario = _scenario(cleric, ally, enemy)
    actions = healer_selector(cleric, scenario)
    # No slots → attacks
    assert actions is not None
    assert any(isinstance(a, WeaponAttackAction) for a in actions)


def test_healer_no_enemies_returns_none() -> None:
    cleric = _cleric()
    ally = _ally("fighter")
    scenario = _scenario(cleric, ally)
    result = healer_selector(cleric, scenario)
    assert result is None


# ---------------------------------------------------------------------------
# Heal action has WIS bonus
# ---------------------------------------------------------------------------

def test_heal_action_includes_wis_bonus() -> None:
    cleric = _cleric()
    ally = _ally("fighter", hp=30)
    apply_damage(ally, 30, "slashing")
    scenario = _scenario(cleric, ally, _enemy())
    actions = healer_selector(cleric, scenario)
    assert actions is not None
    heal = actions[0]
    assert isinstance(heal, HealAction)
    assert heal.heal_bonus == 3  # WIS mod
