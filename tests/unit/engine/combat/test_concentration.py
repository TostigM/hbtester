"""Unit tests for concentration checks."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.concentration import (
    concentration_dc,
    check_concentration,
    break_concentration,
    start_concentration,
)
from balance_framework.engine.combat.conditions import apply_condition


def _caster(con_mod: int = 2, spell: str = "bless") -> CombatantState:
    c = CombatantState(
        id="caster", display_name="Caster", team="party",
        hp_max=30, hp_current=30,
        ability_modifiers={"CON": con_mod},
        concentrating_on=spell,
    )
    return c


# ---------------------------------------------------------------------------
# DC calculation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("damage,expected_dc", [
    (0, 10), (1, 10), (18, 10), (19, 10),
    (20, 10), (21, 10), (22, 11), (30, 15), (40, 20),
])
def test_concentration_dc(damage: int, expected_dc: int) -> None:
    assert concentration_dc(damage) == expected_dc


# ---------------------------------------------------------------------------
# check_concentration: maintained / broken
# ---------------------------------------------------------------------------

def test_high_modifier_tends_to_maintain() -> None:
    caster = _caster(con_mod=10)  # effectively guaranteed success
    d = Dice(0)
    result = check_concentration(caster, damage=20, dice=d)
    assert result.maintained
    assert result.spell_lost is None
    assert caster.concentrating_on == "bless"


def test_low_modifier_can_break() -> None:
    caster = _caster(con_mod=-5)
    found_break = False
    for seed in range(200):
        caster2 = _caster(con_mod=-5)
        d = Dice(seed)
        result = check_concentration(caster2, damage=20, dice=d)
        if not result.maintained:
            assert result.spell_lost == "bless"
            assert caster2.concentrating_on is None
            found_break = True
            break
    assert found_break


def test_war_caster_advantage_helps() -> None:
    # With advantage and a modest modifier, should pass more often
    caster = _caster(con_mod=0)
    successes_normal = 0
    successes_warcaster = 0
    for seed in range(300):
        c1 = _caster(con_mod=0)
        r1 = check_concentration(c1, damage=20, dice=Dice(seed))
        if r1.maintained:
            successes_normal += 1

        c2 = _caster(con_mod=0)
        r2 = check_concentration(c2, damage=20, dice=Dice(seed), war_caster_advantage=True)
        if r2.maintained:
            successes_warcaster += 1

    assert successes_warcaster >= successes_normal


# ---------------------------------------------------------------------------
# Incapacitation breaks concentration immediately
# ---------------------------------------------------------------------------

def test_incapacitated_breaks_concentration_no_save() -> None:
    caster = _caster(con_mod=10)  # would always pass a normal save
    apply_condition(caster, "stunned")
    d = Dice(0)
    result = check_concentration(caster, damage=1, dice=d)
    assert not result.maintained
    assert result.spell_lost == "bless"
    assert caster.concentrating_on is None


# ---------------------------------------------------------------------------
# break_concentration / start_concentration
# ---------------------------------------------------------------------------

def test_break_concentration_clears_spell() -> None:
    caster = _caster(spell="hold_person")
    lost = break_concentration(caster)
    assert lost == "hold_person"
    assert caster.concentrating_on is None


def test_break_concentration_when_not_concentrating() -> None:
    c = CombatantState(
        id="c", display_name="C", team="party",
        hp_max=20, hp_current=20,
    )
    result = break_concentration(c)
    assert result is None


def test_start_concentration_replaces_existing() -> None:
    caster = _caster(spell="bless")
    start_concentration(caster, "hold_monster")
    assert caster.concentrating_on == "hold_monster"


def test_start_concentration_on_empty() -> None:
    c = CombatantState(
        id="c", display_name="C", team="party",
        hp_max=20, hp_current=20,
    )
    start_concentration(c, "web")
    assert c.concentrating_on == "web"
