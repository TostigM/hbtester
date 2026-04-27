"""Unit tests for caster and rogue behavior heuristics."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.actions import WeaponAttackAction
from balance_framework.ai.heuristics.caster import caster_selector
from balance_framework.ai.heuristics.support import rogue_selector


def _scenario(*combatants: CombatantState) -> ScenarioState:
    s = ScenarioState(combatants=list(combatants), dice=Dice(0))
    s.initiative_order = [c.id for c in combatants]
    return s


def _enemy(id: str = "orc") -> CombatantState:
    return CombatantState(
        id=id, display_name=id.capitalize(), team="enemies",
        hp_max=20, hp_current=20, ac=13,
    )


# ===========================================================================
# Caster (Wizard)
# ===========================================================================

def _wizard(resources: dict | None = None) -> CombatantState:
    return CombatantState(
        id="wizard", display_name="Wizard", team="party",
        hp_max=32, hp_current=32, ac=15,
        proficiency_bonus=3,
        ability_modifiers={"INT": 3, "DEX": 2, "CON": 2},
        spell_attack_bonus=6,
        behavior_profile="caster",
        resources=dict(resources if resources is not None else {"spell_slot_1": 4, "spell_slot_2": 3}),
    )


def test_caster_uses_spell_when_slots_available() -> None:
    wizard = _wizard(resources={"spell_slot_1": 2})
    enemy = _enemy()
    scenario = _scenario(wizard, enemy)
    actions = caster_selector(wizard, scenario)
    assert actions is not None
    atk = next(a for a in actions if isinstance(a, WeaponAttackAction))
    assert atk.target_id == "orc"
    assert atk.is_ranged


def test_caster_spell_uses_spell_attack_bonus() -> None:
    wizard = _wizard(resources={"spell_slot_1": 1})
    enemy = _enemy()
    scenario = _scenario(wizard, enemy)
    actions = caster_selector(wizard, scenario)
    assert actions is not None
    atk = next(a for a in actions if isinstance(a, WeaponAttackAction))
    assert atk.attack_bonus == 6  # spell_attack_bonus


def test_caster_falls_back_to_cantrip_when_no_slots() -> None:
    wizard = _wizard(resources={})
    enemy = _enemy()
    scenario = _scenario(wizard, enemy)
    actions = caster_selector(wizard, scenario)
    assert actions is not None
    atk = next(a for a in actions if isinstance(a, WeaponAttackAction))
    assert atk.is_ranged
    assert atk.attack_bonus == 6


def test_caster_cantrip_scales_with_level() -> None:
    # prof_bonus=3 → L5 tier → 2d10
    wizard = _wizard(resources={})
    enemy = _enemy()
    scenario = _scenario(wizard, enemy)
    actions = caster_selector(wizard, scenario)
    assert actions is not None
    atk = next(a for a in actions if isinstance(a, WeaponAttackAction))
    count, sides = atk.damage_dice[0]
    assert count == 2 and sides == 10


def test_caster_spends_slot_after_leveled_spell() -> None:
    wizard = _wizard(resources={"spell_slot_1": 2})
    enemy = _enemy()
    scenario = _scenario(wizard, enemy)
    caster_selector(wizard, scenario)
    assert wizard.resources["spell_slot_1"] == 1


def test_caster_no_enemies_returns_none() -> None:
    wizard = _wizard()
    scenario = _scenario(wizard)
    assert caster_selector(wizard, scenario) is None


def test_caster_prefers_higher_slot() -> None:
    wizard = _wizard(resources={"spell_slot_1": 4, "spell_slot_3": 2})
    enemy = _enemy()
    scenario = _scenario(wizard, enemy)
    caster_selector(wizard, scenario)
    # L3 slot should be spent (higher priority)
    assert wizard.resources["spell_slot_3"] == 1
    assert wizard.resources["spell_slot_1"] == 4  # not spent


# ===========================================================================
# Rogue
# ===========================================================================

def _rogue(sneak_dice: int = 3) -> CombatantState:
    return CombatantState(
        id="rogue", display_name="Rogue", team="party",
        hp_max=38, hp_current=38, ac=15,
        proficiency_bonus=3,
        ability_modifiers={"DEX": 3, "STR": -1, "CON": 2},
        sneak_attack_dice=sneak_dice,
        behavior_profile="rogue",
    )


def test_rogue_attacks_nearest_enemy() -> None:
    rogue = _rogue()
    enemy = _enemy()
    scenario = _scenario(rogue, enemy)
    actions = rogue_selector(rogue, scenario)
    assert actions is not None
    assert len(actions) == 1
    assert isinstance(actions[0], WeaponAttackAction)
    assert actions[0].target_id == "orc"


def test_rogue_attack_uses_dex_bonus() -> None:
    rogue = _rogue()
    enemy = _enemy()
    scenario = _scenario(rogue, enemy)
    actions = rogue_selector(rogue, scenario)
    assert actions is not None
    atk = actions[0]
    assert atk.attack_bonus == 3 + 3  # DEX + prof


def test_rogue_includes_sneak_attack_dice() -> None:
    rogue = _rogue(sneak_dice=3)
    enemy = _enemy()
    scenario = _scenario(rogue, enemy)
    actions = rogue_selector(rogue, scenario)
    assert actions is not None
    atk = actions[0]
    # Should have base weapon (1d6) + sneak attack (3d6)
    total_d6 = sum(c for c, s in atk.damage_dice if s == 6)
    assert total_d6 == 4  # 1 base + 3 sneak


def test_rogue_no_sneak_attack_when_zero_dice() -> None:
    rogue = _rogue(sneak_dice=0)
    enemy = _enemy()
    scenario = _scenario(rogue, enemy)
    actions = rogue_selector(rogue, scenario)
    assert actions is not None
    atk = actions[0]
    total_d6 = sum(c for c, s in atk.damage_dice if s == 6)
    assert total_d6 == 1  # only base weapon


def test_rogue_no_enemies_returns_none() -> None:
    rogue = _rogue()
    scenario = _scenario(rogue)
    assert rogue_selector(rogue, scenario) is None
