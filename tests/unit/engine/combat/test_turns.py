"""Unit tests for turn start/end processing."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.turns import start_turn, end_turn
from balance_framework.engine.combat.conditions import apply_condition
from balance_framework.engine.combat.damage import apply_damage


def _c(hp: int = 20) -> CombatantState:
    return CombatantState(
        id="c", display_name="C", team="party",
        hp_max=hp, hp_current=hp,
        speed=30,
    )


# ---------------------------------------------------------------------------
# Action economy reset
# ---------------------------------------------------------------------------

def test_start_turn_resets_actions() -> None:
    c = _c()
    c.actions_remaining = 0
    c.bonus_actions_remaining = 0
    c.movement_remaining = 0
    start_turn(c, Dice(0))
    assert c.actions_remaining == 1
    assert c.bonus_actions_remaining == 1
    assert c.movement_remaining == 30


def test_start_turn_incapacitated_zeroes_actions() -> None:
    c = _c()
    apply_condition(c, "stunned")
    start_turn(c, Dice(0))
    assert c.actions_remaining == 0
    assert c.bonus_actions_remaining == 0
    assert c.movement_remaining == 0


def test_start_turn_always_resets_reaction() -> None:
    c = _c()
    c.reactions_remaining = 0
    apply_condition(c, "stunned")
    start_turn(c, Dice(0))
    assert c.reactions_remaining == 1


# ---------------------------------------------------------------------------
# Condition expiry
# ---------------------------------------------------------------------------

def test_start_turn_ticks_and_expires_conditions() -> None:
    c = _c()
    apply_condition(c, "poisoned", duration=1)
    events = start_turn(c, Dice(0))
    assert "poisoned" not in c.conditions
    assert any("poisoned" in e and "expired" in e for e in events)


def test_start_turn_ticks_multi_round_condition() -> None:
    c = _c()
    apply_condition(c, "blinded", duration=3)
    start_turn(c, Dice(0))
    assert c.conditions["blinded"] == 2


# ---------------------------------------------------------------------------
# Death saves at 0 HP
# ---------------------------------------------------------------------------

def test_start_turn_rolls_death_save_at_zero_hp() -> None:
    c = _c(hp=10)
    apply_damage(c, 10, "slashing")  # knock to 0
    events = start_turn(c, Dice(0))
    assert any("death save" in e.lower() or "death" in e.lower() for e in events)


def test_start_turn_no_death_save_when_stable() -> None:
    c = _c(hp=10)
    apply_damage(c, 10, "slashing")
    c.is_stable = True
    events = start_turn(c, Dice(0))
    # Should not roll a death save
    assert not any("death save" in e.lower() for e in events)


def test_death_save_nat_20_regains_hp() -> None:
    # Find a seed that gives nat 20 from d20
    for seed in range(200):
        d = Dice(seed)
        if d.d20() == 20:
            c = _c(hp=10)
            apply_damage(c, 10, "slashing")
            events = start_turn(c, Dice(seed))
            if any("nat 20" in e.lower() or "regains 1" in e.lower() for e in events):
                assert c.hp_current == 1
                assert "unconscious" not in c.conditions
                return
    pytest.fail("No nat-20 seed found in 200 tries")


def test_death_save_nat_1_adds_two_failures() -> None:
    for seed in range(200):
        d = Dice(seed)
        if d.d20() == 1:
            c = _c(hp=10)
            apply_damage(c, 10, "slashing")
            start_turn(c, Dice(seed))
            assert c.death_save_failures == 2
            return
    pytest.fail("No nat-1 seed found in 200 tries")


def test_three_death_save_failures_kills() -> None:
    for seed in range(200):
        d = Dice(seed)
        if d.d20() == 1:
            c = _c(hp=10)
            apply_damage(c, 10, "slashing")
            c.death_save_failures = 2  # prime: one more will kill
            start_turn(c, Dice(seed))
            assert not c.is_alive
            return
    pytest.fail("No nat-1 seed found in 200 tries")


def test_three_death_save_successes_stabilizes() -> None:
    for seed in range(200):
        d = Dice(seed)
        roll = d.d20()
        if 10 <= roll <= 19:  # success but not nat 20
            c = _c(hp=10)
            apply_damage(c, 10, "slashing")
            c.death_save_successes = 2  # prime: one more will stabilize
            start_turn(c, Dice(seed))
            assert c.is_stable
            return
    pytest.fail("No seed with 10-19 roll found in 200 tries")


# ---------------------------------------------------------------------------
# end_turn (currently a no-op stub)
# ---------------------------------------------------------------------------

def test_end_turn_returns_empty_list() -> None:
    c = _c()
    events = end_turn(c)
    assert events == []
