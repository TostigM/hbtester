"""Unit tests for per-combatant stat tracking (damage, kills, healing)."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.actions import (
    WeaponAttackAction, HealAction, resolve_action,
)
from balance_framework.runner.collector import collect_result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _attacker(id: str = "hero", hp: int = 50) -> CombatantState:
    return CombatantState(
        id=id, display_name=id, team="party",
        hp_max=hp, hp_current=hp, ac=18,
        proficiency_bonus=3,
        ability_modifiers={"STR": 4},
    )


def _target(id: str = "goblin", hp: int = 7) -> CombatantState:
    return CombatantState(
        id=id, display_name=id, team="enemies",
        hp_max=hp, hp_current=hp, ac=13,
        proficiency_bonus=2,
        ability_modifiers={},
    )


def _scenario(*combatants: CombatantState, seed: int = 0) -> ScenarioState:
    return ScenarioState(combatants=list(combatants), dice=Dice(seed))


def _attack(attacker_id: str, target_id: str, bonus: int = 20) -> WeaponAttackAction:
    return WeaponAttackAction(
        attacker_id=attacker_id, target_id=target_id,
        attack_bonus=bonus,
        damage_dice=[(1, 6)], damage_bonus=4,
        damage_type="slashing",
    )


# ---------------------------------------------------------------------------
# damage_dealt tracking
# ---------------------------------------------------------------------------


def test_damage_dealt_accumulated_on_hit() -> None:
    hero = _attacker()
    goblin = _target(hp=100)  # won't die
    s = _scenario(hero, goblin)
    resolve_action(_attack("hero", "goblin"), s)
    assert s.damage_dealt.get("hero", 0) > 0


def test_damage_dealt_zero_on_miss() -> None:
    hero = _attacker()
    goblin = _target(hp=100)
    s = _scenario(hero, goblin)
    # Attack bonus -20 should always miss
    action = _attack("hero", "goblin", bonus=-20)
    resolve_action(action, s)
    assert s.damage_dealt.get("hero", 0) == 0


def test_damage_dealt_accumulates_across_attacks() -> None:
    hero = _attacker()
    goblin = _target(hp=1000)  # very tanky, won't die
    s = _scenario(hero, goblin)
    resolve_action(_attack("hero", "goblin"), s)
    first = s.damage_dealt.get("hero", 0)
    resolve_action(_attack("hero", "goblin"), s)
    second = s.damage_dealt.get("hero", 0)
    # Second should be >= first (could be same if first attack got 0 via miss)
    assert second >= first


# ---------------------------------------------------------------------------
# kills tracking
# ---------------------------------------------------------------------------


def test_kill_counted_when_target_dies() -> None:
    hero = _attacker()
    goblin = _target(hp=1)  # will die from any hit
    s = _scenario(hero, goblin)
    resolve_action(_attack("hero", "goblin"), s)
    assert s.kills.get("hero", 0) == 1


def test_no_kill_when_target_survives() -> None:
    hero = _attacker()
    goblin = _target(hp=1000)
    s = _scenario(hero, goblin)
    resolve_action(_attack("hero", "goblin"), s)
    assert s.kills.get("hero", 0) == 0


# ---------------------------------------------------------------------------
# healing_done tracking
# ---------------------------------------------------------------------------


def test_healing_done_tracked() -> None:
    healer = _attacker("healer")
    wounded = _attacker("wounded", hp=30)
    wounded.hp_current = 10
    s = _scenario(healer, wounded)
    action = HealAction(
        caster_id="healer", target_id="wounded",
        heal_dice=[(2, 8)], heal_bonus=3,
    )
    resolve_action(action, s)
    assert s.healing_done.get("healer", 0) > 0


def test_healing_done_capped_at_max_hp() -> None:
    healer = _attacker("healer")
    full = _attacker("full", hp=30)  # already at max
    s = _scenario(healer, full)
    action = HealAction(caster_id="healer", target_id="full", heal_bonus=100)
    resolve_action(action, s)
    # Gained should be 0 since target is already at max
    assert s.healing_done.get("healer", 0) == 0


# ---------------------------------------------------------------------------
# collect_result propagates stats
# ---------------------------------------------------------------------------


def test_collect_result_includes_damage_dealt() -> None:
    hero = _attacker()
    goblin = _target(hp=1000)
    s = _scenario(hero, goblin)
    s.is_over = True
    s.winner_team = "party"
    s.round_number = 1
    resolve_action(_attack("hero", "goblin"), s)
    result = collect_result(s, seed=0)
    hero_cr = next(c for c in result.combatants if c.id == "hero")
    assert hero_cr.damage_dealt == s.damage_dealt.get("hero", 0)


def test_collect_result_includes_kills() -> None:
    hero = _attacker()
    goblin = _target(hp=1)
    s = _scenario(hero, goblin)
    s.is_over = True
    s.winner_team = "party"
    s.round_number = 1
    resolve_action(_attack("hero", "goblin"), s)
    result = collect_result(s, seed=0)
    hero_cr = next(c for c in result.combatants if c.id == "hero")
    assert hero_cr.kills == s.kills.get("hero", 0)


def test_collect_result_includes_healing_done() -> None:
    healer = _attacker("healer")
    wounded = _attacker("wounded", hp=30)
    wounded.hp_current = 5
    s = _scenario(healer, wounded)
    s.is_over = True
    s.winner_team = "party"
    s.round_number = 1
    action = HealAction(caster_id="healer", target_id="wounded", heal_bonus=10)
    resolve_action(action, s)
    result = collect_result(s, seed=0)
    healer_cr = next(c for c in result.combatants if c.id == "healer")
    assert healer_cr.healing_done > 0
