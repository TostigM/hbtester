"""Unit tests for the martial behavior heuristic."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.actions import WeaponAttackAction, HealAction
from balance_framework.ai.heuristics.martial import martial_selector


def _fighter(hp: int = 54, hp_current: int | None = None, resources: dict | None = None) -> CombatantState:
    return CombatantState(
        id="fighter", display_name="Fighter", team="party",
        hp_max=hp, hp_current=hp if hp_current is None else hp_current,
        ac=19, proficiency_bonus=3,
        ability_modifiers={"STR": 3, "DEX": 2, "CON": 2},
        extra_attack_count=2,
        behavior_profile="martial",
        resources=dict(resources if resources is not None else {"second_wind": 1, "action_surge": 1}),
    )


def _goblin(id: str = "g") -> CombatantState:
    return CombatantState(
        id=id, display_name="Goblin", team="enemies",
        hp_max=7, hp_current=7, ac=15,
        ability_modifiers={"STR": -1, "DEX": 2},
    )


def _scenario(*combatants: CombatantState) -> ScenarioState:
    s = ScenarioState(combatants=list(combatants), dice=Dice(0))
    s.initiative_order = [c.id for c in combatants]
    return s


# ---------------------------------------------------------------------------
# Basic attack
# ---------------------------------------------------------------------------

def test_martial_attacks_nearest_enemy() -> None:
    fighter = _fighter()
    goblin = _goblin()
    scenario = _scenario(fighter, goblin)
    actions = martial_selector(fighter, scenario)
    assert actions is not None
    attack_actions = [a for a in actions if isinstance(a, WeaponAttackAction)]
    assert all(a.target_id == "g" for a in attack_actions)


def test_martial_returns_extra_attack_count_attacks() -> None:
    fighter = _fighter(resources={})  # no surge
    goblin = _goblin()
    scenario = _scenario(fighter, goblin)
    actions = martial_selector(fighter, scenario)
    assert actions is not None
    attack_actions = [a for a in actions if isinstance(a, WeaponAttackAction)]
    assert len(attack_actions) == 2  # extra_attack_count=2


def test_martial_no_enemies_returns_none() -> None:
    fighter = _fighter()
    scenario = _scenario(fighter)
    result = martial_selector(fighter, scenario)
    assert result is None


# ---------------------------------------------------------------------------
# Second Wind
# ---------------------------------------------------------------------------

def test_martial_uses_second_wind_when_bloodied() -> None:
    hp = 54
    low_hp = int(hp * 0.25)  # well below 30%
    fighter = _fighter(hp=hp, hp_current=low_hp, resources={"second_wind": 1})
    goblin = _goblin()
    scenario = _scenario(fighter, goblin)
    actions = martial_selector(fighter, scenario)
    assert actions is not None
    heal_actions = [a for a in actions if isinstance(a, HealAction)]
    assert len(heal_actions) == 1
    assert heal_actions[0].target_id == "fighter"


def test_martial_no_second_wind_when_full_hp() -> None:
    fighter = _fighter(hp_current=54, resources={"second_wind": 1})
    goblin = _goblin()
    scenario = _scenario(fighter, goblin)
    actions = martial_selector(fighter, scenario)
    assert actions is not None
    heal_actions = [a for a in actions if isinstance(a, HealAction)]
    assert len(heal_actions) == 0


def test_martial_no_second_wind_when_depleted() -> None:
    fighter = _fighter(hp_current=5, resources={"second_wind": 0})
    goblin = _goblin()
    scenario = _scenario(fighter, goblin)
    actions = martial_selector(fighter, scenario)
    heal_actions = [a for a in (actions or []) if isinstance(a, HealAction)]
    assert len(heal_actions) == 0


# ---------------------------------------------------------------------------
# Action Surge
# ---------------------------------------------------------------------------

def test_martial_action_surge_doubles_attacks() -> None:
    fighter = _fighter(resources={"action_surge": 1})
    goblin = _goblin()
    scenario = _scenario(fighter, goblin)
    actions = martial_selector(fighter, scenario)
    assert actions is not None
    attack_actions = [a for a in actions if isinstance(a, WeaponAttackAction)]
    # extra_attack_count=2 normal + 2 from surge = 4
    assert len(attack_actions) == 4


def test_martial_no_surge_without_resource() -> None:
    fighter = _fighter(resources={})
    goblin = _goblin()
    scenario = _scenario(fighter, goblin)
    actions = martial_selector(fighter, scenario)
    assert actions is not None
    attack_actions = [a for a in actions if isinstance(a, WeaponAttackAction)]
    assert len(attack_actions) == 2


def test_martial_surge_is_spent_after_use() -> None:
    fighter = _fighter(resources={"action_surge": 1})
    goblin = _goblin()
    scenario = _scenario(fighter, goblin)
    martial_selector(fighter, scenario)
    assert fighter.resources.get("action_surge", 0) == 0
