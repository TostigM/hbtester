"""Unit tests for attack roll resolution."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.attacks import WeaponAttack, AttackResult, resolve_attack


def _attacker(ac: int = 10, crit_threshold: int = 20) -> CombatantState:
    return CombatantState(
        id="attacker", display_name="Attacker", team="party",
        hp_max=20, hp_current=20, ac=ac,
        crit_threshold=crit_threshold,
    )


def _target(ac: int = 14) -> CombatantState:
    return CombatantState(
        id="target", display_name="Target", team="enemies",
        hp_max=20, hp_current=20, ac=ac,
    )


def _sword(attack_bonus: int = 5, damage_bonus: int = 3, **kw) -> WeaponAttack:
    return WeaponAttack(
        attacker_id="attacker",
        target_id="target",
        attack_bonus=attack_bonus,
        damage_dice=[(1, 8)],
        damage_type="slashing",
        damage_bonus=damage_bonus,
        **kw,
    )


# ---------------------------------------------------------------------------
# Hit vs. miss
# ---------------------------------------------------------------------------

def test_nat_20_always_hits() -> None:
    # Force a nat 20 by finding a seed that produces it
    attacker = _attacker()
    target = _target(ac=30)  # impossible AC to beat normally
    for seed in range(100):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(attack_bonus=0), d)
        if result.nat_20:
            assert result.hit
            assert result.crit
            return
    pytest.fail("Couldn't find a nat-20 seed in 100 tries")


def test_nat_1_always_misses() -> None:
    attacker = _attacker()
    target = _target(ac=1)  # lowest possible AC
    for seed in range(100):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(attack_bonus=100), d)
        if result.nat_1:
            assert not result.hit
            return
    pytest.fail("Couldn't find a nat-1 seed in 100 tries")


def test_roll_plus_bonus_meets_ac_hits() -> None:
    # Find a seed where we can calculate a guaranteed hit
    attacker = _attacker()
    target = _target(ac=10)
    for seed in range(50):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(attack_bonus=10), d)
        if result.hit and not result.nat_1 and not result.nat_20:
            assert result.total_attack_roll >= target.ac
            return


def test_roll_below_ac_misses() -> None:
    attacker = _attacker()
    target = _target(ac=25)
    for seed in range(200):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(attack_bonus=-5), d)
        if not result.nat_20 and not result.nat_1:
            if result.total_attack_roll < target.ac:
                assert not result.hit
                return


# ---------------------------------------------------------------------------
# Crits
# ---------------------------------------------------------------------------

def test_nat_20_doubles_dice() -> None:
    attacker = _attacker()
    target = _target(ac=30)
    for seed in range(100):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(attack_bonus=0), d)
        if result.nat_20 and result.hit:
            # 1d8 → 2 rolls on crit
            assert len(result.damage_rolls) == 2
            return
    pytest.fail("No nat-20 found")


def test_expanded_crit_threshold() -> None:
    """Crit threshold of 19 should crit on 19 or 20."""
    attacker = _attacker(crit_threshold=19)
    target = _target(ac=1)
    found_19 = False
    for seed in range(500):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(), d)
        if result.raw_roll == 19:
            assert result.crit
            found_19 = True
            break
    assert found_19, "No 19 roll found in 500 seeds"


def test_non_crit_hit_single_die_set() -> None:
    attacker = _attacker()
    target = _target(ac=5)
    for seed in range(200):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(), d)
        if result.hit and not result.crit:
            assert len(result.damage_rolls) == 1
            return


# ---------------------------------------------------------------------------
# Damage includes bonus
# ---------------------------------------------------------------------------

def test_damage_includes_flat_bonus() -> None:
    attacker = _attacker()
    target = _target(ac=1)
    for seed in range(50):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(), d)
        if result.hit and not result.crit:
            die_total = sum(result.damage_rolls)
            assert result.damage_total == die_total + 3
            return


# ---------------------------------------------------------------------------
# Advantage / Disadvantage
# ---------------------------------------------------------------------------

def test_advantage_uses_higher_roll() -> None:
    d = Dice(0)
    attacker = _attacker()
    target = _target(ac=5)
    result = resolve_attack(attacker, target, _sword(advantage=True), d)
    assert result.had_advantage
    assert result.second_roll is not None
    assert result.raw_roll >= result.second_roll


def test_disadvantage_uses_lower_roll() -> None:
    d = Dice(0)
    attacker = _attacker()
    target = _target(ac=5)
    result = resolve_attack(attacker, target, _sword(disadvantage=True), d)
    assert result.had_disadvantage
    assert result.second_roll is not None
    assert result.raw_roll <= result.second_roll


def test_advantage_and_disadvantage_cancel() -> None:
    d = Dice(0)
    attacker = _attacker()
    target = _target(ac=5)
    result = resolve_attack(attacker, target, _sword(advantage=True, disadvantage=True), d)
    assert not result.had_advantage
    assert not result.had_disadvantage
    assert result.second_roll is None


# ---------------------------------------------------------------------------
# Paralyzed / unconscious target → auto-crit in melee
# ---------------------------------------------------------------------------

def test_paralyzed_target_melee_always_crits() -> None:
    from balance_framework.engine.combat.conditions import apply_condition
    attacker = _attacker()
    target = _target(ac=5)
    apply_condition(target, "paralyzed")
    found_non_nat20_crit = False
    for seed in range(100):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(is_ranged=False), d)
        if result.hit and not result.nat_20:
            assert result.crit
            found_non_nat20_crit = True
            break
    assert found_non_nat20_crit


def test_paralyzed_target_ranged_no_forced_crit() -> None:
    from balance_framework.engine.combat.conditions import apply_condition
    attacker = _attacker()
    target = _target(ac=1)
    apply_condition(target, "paralyzed")
    any_non_crit = False
    for seed in range(200):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(is_ranged=True), d)
        if result.hit and not result.nat_20:
            if not result.crit:
                any_non_crit = True
                break
    assert any_non_crit, "Ranged attack on paralyzed should not always crit"


# ---------------------------------------------------------------------------
# Miss returns zero damage
# ---------------------------------------------------------------------------

def test_miss_returns_zero_damage() -> None:
    attacker = _attacker()
    target = _target(ac=25)
    for seed in range(200):
        d = Dice(seed)
        result = resolve_attack(attacker, target, _sword(attack_bonus=-5), d)
        if not result.hit:
            assert result.damage_total == 0
            assert result.damage_rolls == []
            return
