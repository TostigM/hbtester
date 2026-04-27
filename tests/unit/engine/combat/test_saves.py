"""Unit tests for saving throw resolution."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.saves import resolve_save
from balance_framework.engine.combat.conditions import apply_condition


def _combatant(
    ability_mod: int = 2,
    ability: str = "CON",
    proficient: bool = False,
    prof_bonus: int = 2,
) -> CombatantState:
    c = CombatantState(
        id="c", display_name="C", team="party",
        hp_max=20, hp_current=20,
        proficiency_bonus=prof_bonus,
        ability_modifiers={ability: ability_mod},
        saving_throw_proficiencies=frozenset({ability} if proficient else []),
    )
    return c


# ---------------------------------------------------------------------------
# Basic success / failure
# ---------------------------------------------------------------------------

def test_save_success_when_total_meets_dc() -> None:
    # Use a very low DC to ensure success with a decent modifier
    c = _combatant(ability_mod=5, ability="CON")
    d = Dice(0)
    # DC 5 — modifier alone nearly guarantees a pass
    result = resolve_save(c, "CON", dc=5, dice=d)
    assert result.dc == 5
    assert result.modifier == 5


def test_save_fails_when_total_below_dc() -> None:
    # Very high DC, very negative modifier — find a failing roll
    c = _combatant(ability_mod=-4, ability="CON")
    d = Dice(0)
    found_fail = False
    for seed in range(200):
        d2 = Dice(seed)
        r = resolve_save(c, "CON", dc=30, dice=d2)
        if not r.success:
            found_fail = True
            break
    assert found_fail


def test_proficiency_adds_to_modifier() -> None:
    c = _combatant(ability_mod=2, ability="CON", proficient=True, prof_bonus=3)
    d = Dice(0)
    r = resolve_save(c, "CON", dc=1, dice=d)
    assert r.modifier == 5  # 2 (ability) + 3 (proficiency)


# ---------------------------------------------------------------------------
# Advantage / disadvantage
# ---------------------------------------------------------------------------

def test_advantage_keeps_higher() -> None:
    c = _combatant(ability_mod=0)
    d = Dice(0)
    r = resolve_save(c, "CON", dc=10, dice=d, advantage=True)
    assert r.had_advantage
    assert r.second_roll is not None
    assert r.kept_roll >= r.second_roll


def test_disadvantage_keeps_lower() -> None:
    c = _combatant(ability_mod=0)
    d = Dice(0)
    r = resolve_save(c, "CON", dc=10, dice=d, disadvantage=True)
    assert r.had_disadvantage
    assert r.second_roll is not None
    assert r.kept_roll <= r.second_roll


def test_advantage_and_disadvantage_cancel() -> None:
    c = _combatant(ability_mod=0)
    d = Dice(0)
    r = resolve_save(c, "CON", dc=10, dice=d, advantage=True, disadvantage=True)
    assert not r.had_advantage
    assert not r.had_disadvantage
    assert r.second_roll is None


# ---------------------------------------------------------------------------
# Auto-fail on STR/DEX when paralyzed/unconscious
# ---------------------------------------------------------------------------

def test_auto_fail_str_save_when_paralyzed() -> None:
    c = _combatant(ability_mod=5, ability="STR")
    apply_condition(c, "paralyzed")
    d = Dice(0)
    r = resolve_save(c, "STR", dc=5, dice=d)
    assert not r.success
    assert r.nat_1


def test_auto_fail_dex_save_when_unconscious() -> None:
    c = _combatant(ability_mod=5, ability="DEX")
    apply_condition(c, "unconscious")
    d = Dice(0)
    r = resolve_save(c, "DEX", dc=1, dice=d)
    assert not r.success
    assert r.nat_1


def test_con_save_not_auto_fail_when_paralyzed() -> None:
    # Only STR and DEX auto-fail; CON should roll normally
    c = _combatant(ability_mod=5, ability="CON")
    apply_condition(c, "paralyzed")
    d = Dice(0)
    found_success = False
    for seed in range(50):
        d2 = Dice(seed)
        r = resolve_save(c, "CON", dc=1, dice=d2)
        if r.success:
            found_success = True
            break
    assert found_success


# ---------------------------------------------------------------------------
# Legendary resistance
# ---------------------------------------------------------------------------

def test_legendary_resistance_auto_succeeds() -> None:
    c = _combatant(ability_mod=-5, ability="CON")
    apply_condition(c, "stunned")  # would auto-fail DEX/STR, but this is CON
    d = Dice(0)
    r = resolve_save(c, "CON", dc=30, dice=d, legendary_resistance=True)
    assert r.success
    assert r.nat_20


# ---------------------------------------------------------------------------
# saving_throw_advantages field grants advantage
# ---------------------------------------------------------------------------

def test_saving_throw_advantages_grants_advantage() -> None:
    c = CombatantState(
        id="c", display_name="C", team="party",
        hp_max=20, hp_current=20,
        ability_modifiers={"WIS": 0},
        saving_throw_advantages=frozenset({"WIS"}),
    )
    d = Dice(0)
    r = resolve_save(c, "WIS", dc=10, dice=d)
    assert r.had_advantage
