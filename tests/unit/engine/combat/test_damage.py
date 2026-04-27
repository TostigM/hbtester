"""Unit tests for damage application."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.combat.damage import apply_damage, apply_healing, add_temp_hp


def _target(hp: int = 20, **kw) -> CombatantState:
    return CombatantState(
        id="t", display_name="Target", team="enemies",
        hp_max=hp, hp_current=hp,
        **kw,
    )


# ---------------------------------------------------------------------------
# Flat damage
# ---------------------------------------------------------------------------

def test_flat_damage_reduces_hp() -> None:
    t = _target(hp=20)
    result = apply_damage(t, 7, "slashing")
    assert result.hp_after == 13
    assert result.applied_damage == 7
    assert t.hp_current == 13


def test_damage_cannot_go_below_zero() -> None:
    t = _target(hp=5)
    apply_damage(t, 20, "slashing")
    assert t.hp_current == 0


# ---------------------------------------------------------------------------
# Immunity
# ---------------------------------------------------------------------------

def test_immunity_prevents_all_damage() -> None:
    t = _target(damage_immunities=frozenset({"fire"}))
    result = apply_damage(t, 30, "fire")
    assert result.applied_damage == 0
    assert t.hp_current == 20


# ---------------------------------------------------------------------------
# Resistance (half, floor)
# ---------------------------------------------------------------------------

def test_resistance_halves_damage() -> None:
    t = _target(damage_resistances=frozenset({"piercing"}))
    result = apply_damage(t, 10, "piercing")
    assert result.applied_damage == 5
    assert t.hp_current == 15


def test_resistance_floors_on_odd() -> None:
    t = _target(damage_resistances=frozenset({"bludgeoning"}))
    result = apply_damage(t, 7, "bludgeoning")
    assert result.applied_damage == 3  # floor(7/2)
    assert t.hp_current == 17


# ---------------------------------------------------------------------------
# Vulnerability (double)
# ---------------------------------------------------------------------------

def test_vulnerability_doubles_damage() -> None:
    t = _target(damage_vulnerabilities=frozenset({"thunder"}))
    result = apply_damage(t, 5, "thunder")
    assert result.applied_damage == 10
    assert t.hp_current == 10


# ---------------------------------------------------------------------------
# Temp HP absorbs first
# ---------------------------------------------------------------------------

def test_temp_hp_absorbs_before_real_hp() -> None:
    t = _target(hp=20)
    t.temp_hp = 5
    result = apply_damage(t, 8, "slashing")
    assert result.temp_hp_absorbed == 5
    assert t.temp_hp == 0
    assert t.hp_current == 17  # 20 - (8 - 5) = 17


def test_temp_hp_fully_absorbs_small_damage() -> None:
    t = _target(hp=20)
    t.temp_hp = 10
    result = apply_damage(t, 6, "slashing")
    assert result.temp_hp_absorbed == 6
    assert t.temp_hp == 4
    assert t.hp_current == 20  # no real HP lost


def test_temp_hp_not_affected_by_resistance() -> None:
    t = _target(hp=20, damage_resistances=frozenset({"fire"}))
    t.temp_hp = 3
    # Resistance halves fire: 10 → 5. Temp HP absorbs 3, then 2 hits real HP.
    result = apply_damage(t, 10, "fire")
    assert result.applied_damage == 5
    assert result.temp_hp_absorbed == 3
    assert t.hp_current == 18


# ---------------------------------------------------------------------------
# Knocked unconscious at 0 HP
# ---------------------------------------------------------------------------

def test_knocked_unconscious_at_zero() -> None:
    t = _target(hp=10)
    result = apply_damage(t, 10, "slashing")
    assert t.hp_current == 0
    assert result.knocked_unconscious
    assert "unconscious" in t.conditions
    assert "prone" in t.conditions


def test_existing_unconscious_adds_death_save_failure() -> None:
    from balance_framework.engine.combat.conditions import apply_condition
    t = _target(hp=10)
    apply_damage(t, 10, "slashing")  # knock out
    assert t.death_save_failures == 0
    apply_damage(t, 5, "slashing")  # hit at 0 HP
    assert t.death_save_failures == 1


def test_crit_at_zero_adds_two_failures() -> None:
    from balance_framework.engine.combat.conditions import apply_condition
    t = _target(hp=10)
    apply_damage(t, 10, "slashing")  # knock out
    apply_damage(t, 5, "slashing", from_crit=True)
    assert t.death_save_failures == 2


# ---------------------------------------------------------------------------
# Instant death (massive damage)
# ---------------------------------------------------------------------------

def test_instant_death_when_excess_equals_hp_max() -> None:
    t = _target(hp=10)
    result = apply_damage(t, 20, "slashing")  # 10 excess = 10 hp_max
    assert result.instant_death
    assert result.killed
    assert not t.is_alive


def test_no_instant_death_when_excess_below_hp_max() -> None:
    t = _target(hp=10)
    result = apply_damage(t, 15, "slashing")  # 5 excess < 10 hp_max
    assert not result.instant_death
    assert t.is_alive


# ---------------------------------------------------------------------------
# apply_healing
# ---------------------------------------------------------------------------

def test_healing_restores_hp() -> None:
    t = _target(hp=20)
    t.hp_current = 5
    gained = apply_healing(t, 10)
    assert gained == 10
    assert t.hp_current == 15


def test_healing_capped_at_max() -> None:
    t = _target(hp=20)
    t.hp_current = 18
    gained = apply_healing(t, 10)
    assert gained == 2
    assert t.hp_current == 20


def test_healing_at_zero_clears_unconscious() -> None:
    t = _target(hp=10)
    apply_damage(t, 10, "slashing")
    assert "unconscious" in t.conditions
    apply_healing(t, 5)
    assert "unconscious" not in t.conditions
    assert "prone" not in t.conditions
    assert t.hp_current == 5


def test_healing_dead_combatant_does_nothing() -> None:
    t = _target(hp=10)
    apply_damage(t, 30, "slashing")  # instant death
    assert not t.is_alive
    gained = apply_healing(t, 10)
    assert gained == 0


# ---------------------------------------------------------------------------
# add_temp_hp
# ---------------------------------------------------------------------------

def test_add_temp_hp_grants() -> None:
    t = _target()
    add_temp_hp(t, 5)
    assert t.temp_hp == 5


def test_add_temp_hp_does_not_stack() -> None:
    t = _target()
    add_temp_hp(t, 5)
    add_temp_hp(t, 3)
    assert t.temp_hp == 5  # higher pool wins


def test_add_temp_hp_replaces_with_higher() -> None:
    t = _target()
    add_temp_hp(t, 3)
    result = add_temp_hp(t, 8)
    assert result == 8
    assert t.temp_hp == 8
