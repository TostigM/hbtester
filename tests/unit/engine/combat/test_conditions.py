"""Unit tests for condition application and modifiers."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.combat.conditions import (
    ALL_CONDITIONS,
    apply_condition,
    remove_condition,
    tick_conditions,
    is_incapacitated,
    auto_fails_str_dex,
    get_attack_modifiers,
    target_crits_within_5ft,
)


def _c(**kw) -> CombatantState:
    return CombatantState(
        id="c", display_name="C", team="party",
        hp_max=20, hp_current=20, **kw,
    )


# ---------------------------------------------------------------------------
# apply_condition / remove_condition
# ---------------------------------------------------------------------------

def test_apply_condition_adds_to_dict() -> None:
    c = _c()
    result = apply_condition(c, "poisoned")
    assert result is True
    assert "poisoned" in c.conditions


def test_apply_condition_with_duration() -> None:
    c = _c()
    apply_condition(c, "blinded", duration=3)
    assert c.conditions["blinded"] == 3


def test_apply_condition_indefinite_when_no_duration() -> None:
    c = _c()
    apply_condition(c, "charmed")
    assert c.conditions["charmed"] is None


def test_apply_unknown_condition_raises() -> None:
    c = _c()
    with pytest.raises(ValueError, match="Unknown condition"):
        apply_condition(c, "flying_pig")


def test_remove_condition_clears_it() -> None:
    c = _c()
    apply_condition(c, "prone")
    removed = remove_condition(c, "prone")
    assert removed is True
    assert "prone" not in c.conditions


def test_remove_missing_condition_returns_false() -> None:
    c = _c()
    assert remove_condition(c, "stunned") is False


# ---------------------------------------------------------------------------
# Condition immunity
# ---------------------------------------------------------------------------

def test_immune_to_condition_prevents_apply() -> None:
    c = _c(condition_immunities=frozenset({"charmed"}))
    result = apply_condition(c, "charmed")
    assert result is False
    assert "charmed" not in c.conditions


# ---------------------------------------------------------------------------
# tick_conditions
# ---------------------------------------------------------------------------

def test_tick_decrements_duration() -> None:
    c = _c()
    apply_condition(c, "poisoned", duration=3)
    expired = tick_conditions(c)
    assert expired == []
    assert c.conditions["poisoned"] == 2


def test_tick_removes_at_one() -> None:
    c = _c()
    apply_condition(c, "blinded", duration=1)
    expired = tick_conditions(c)
    assert "blinded" in expired
    assert "blinded" not in c.conditions


def test_tick_leaves_indefinite_conditions() -> None:
    c = _c()
    apply_condition(c, "frightened")  # indefinite
    expired = tick_conditions(c)
    assert expired == []
    assert "frightened" in c.conditions


# ---------------------------------------------------------------------------
# is_incapacitated
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cond", ["incapacitated", "paralyzed", "petrified", "stunned", "unconscious"])
def test_is_incapacitated_for_incapacitating_conditions(cond: str) -> None:
    c = _c()
    apply_condition(c, cond)
    assert is_incapacitated(c)


def test_not_incapacitated_without_conditions() -> None:
    c = _c()
    assert not is_incapacitated(c)


def test_not_incapacitated_for_non_incapacitating(  ) -> None:
    c = _c()
    apply_condition(c, "poisoned")
    assert not is_incapacitated(c)


# ---------------------------------------------------------------------------
# auto_fails_str_dex
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("cond", ["paralyzed", "petrified", "stunned", "unconscious"])
def test_auto_fail_str_dex_conditions(cond: str) -> None:
    c = _c()
    apply_condition(c, cond)
    assert auto_fails_str_dex(c)


def test_no_auto_fail_normally() -> None:
    c = _c()
    assert not auto_fails_str_dex(c)


# ---------------------------------------------------------------------------
# get_attack_modifiers
# ---------------------------------------------------------------------------

def test_invisible_attacker_has_advantage() -> None:
    attacker = _c()
    target = _c()
    apply_condition(attacker, "invisible")
    adv, dis = get_attack_modifiers(attacker, target)
    assert adv
    assert not dis


def test_blinded_attacker_has_disadvantage() -> None:
    attacker = _c()
    target = _c()
    apply_condition(attacker, "blinded")
    adv, dis = get_attack_modifiers(attacker, target)
    assert dis


def test_paralyzed_target_gives_attacker_advantage() -> None:
    attacker = _c()
    target = _c()
    apply_condition(target, "paralyzed")
    adv, dis = get_attack_modifiers(attacker, target)
    assert adv


def test_prone_target_melee_gives_advantage() -> None:
    attacker = _c()
    target = _c()
    apply_condition(target, "prone")
    adv, dis = get_attack_modifiers(attacker, target, is_ranged=False)
    assert adv
    assert not dis


def test_prone_target_ranged_gives_disadvantage() -> None:
    attacker = _c()
    target = _c()
    apply_condition(target, "prone")
    adv, dis = get_attack_modifiers(attacker, target, is_ranged=True)
    assert dis
    assert not adv


def test_invisible_target_gives_attacker_disadvantage() -> None:
    attacker = _c()
    target = _c()
    apply_condition(target, "invisible")
    adv, dis = get_attack_modifiers(attacker, target)
    assert dis


def test_frightened_attacker_has_disadvantage() -> None:
    attacker = _c()
    target = _c()
    apply_condition(attacker, "frightened")
    adv, dis = get_attack_modifiers(attacker, target)
    assert dis


# ---------------------------------------------------------------------------
# target_crits_within_5ft
# ---------------------------------------------------------------------------

def test_paralyzed_target_crits_within_5ft() -> None:
    t = _c()
    apply_condition(t, "paralyzed")
    assert target_crits_within_5ft(t)


def test_unconscious_target_crits_within_5ft() -> None:
    t = _c()
    apply_condition(t, "unconscious")
    assert target_crits_within_5ft(t)


def test_poisoned_target_does_not_crit_within_5ft() -> None:
    t = _c()
    apply_condition(t, "poisoned")
    assert not target_crits_within_5ft(t)
