"""Unit tests for structured event log and decision log."""

from __future__ import annotations

import pytest

from balance_framework.logging.event_log import (
    AttackEvent, HealEvent, DeathEvent, RoundStartEvent, CombatEndEvent,
)
from balance_framework.logging.decision_log import DecisionLog, DecisionRecord
from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.actions import (
    WeaponAttackAction, HealAction, resolve_action,
)


# ---------------------------------------------------------------------------
# Event dataclasses
# ---------------------------------------------------------------------------

def test_attack_event_fields() -> None:
    e = AttackEvent(round_number=2, attacker_id="hero", target_id="goblin",
                    roll=17, total=22, target_ac=15, hit=True, crit=False,
                    damage=8, damage_type="slashing")
    assert e.hit is True
    assert e.damage == 8
    assert e.event_type == "attack"


def test_heal_event_fields() -> None:
    e = HealEvent(round_number=1, caster_id="cleric", target_id="hero", amount=12)
    assert e.amount == 12
    assert e.event_type == "heal"


def test_death_event_fields() -> None:
    e = DeathEvent(round_number=3, combatant_id="goblin", team="enemies")
    assert e.team == "enemies"
    assert e.event_type == "death"


def test_events_are_immutable() -> None:
    e = AttackEvent(attacker_id="h", target_id="g", hit=True)
    with pytest.raises(Exception):
        e.hit = False  # type: ignore[misc]  # frozen dataclass


# ---------------------------------------------------------------------------
# Structured events emitted by resolvers
# ---------------------------------------------------------------------------

def _make_scenario(seed: int = 0) -> ScenarioState:
    hero = CombatantState(
        id="hero", display_name="Hero", team="party",
        hp_max=50, hp_current=50, ac=18, proficiency_bonus=3,
        ability_modifiers={"STR": 4},
    )
    goblin = CombatantState(
        id="goblin", display_name="Goblin", team="enemies",
        hp_max=7, hp_current=7, ac=13, proficiency_bonus=2,
        ability_modifiers={},
    )
    return ScenarioState(combatants=[hero, goblin], dice=Dice(seed))


def test_weapon_attack_emits_structured_event() -> None:
    s = _make_scenario()
    action = WeaponAttackAction(
        attacker_id="hero", target_id="goblin",
        attack_bonus=20, damage_dice=[(1, 6)], damage_type="slashing", damage_bonus=4,
    )
    resolve_action(action, s)
    attack_events = [e for e in s.structured_events if isinstance(e, AttackEvent)]
    assert len(attack_events) == 1
    assert attack_events[0].attacker_id == "hero"


def test_weapon_attack_hit_records_damage() -> None:
    s = _make_scenario()
    action = WeaponAttackAction(
        attacker_id="hero", target_id="goblin",
        attack_bonus=20,  # will hit
        damage_dice=[(1, 6)], damage_type="slashing", damage_bonus=4,
    )
    resolve_action(action, s)
    hits = [e for e in s.structured_events if isinstance(e, AttackEvent) and e.hit]
    if hits:
        assert hits[0].damage > 0


def test_kill_emits_death_event() -> None:
    hero = CombatantState(
        id="hero", display_name="Hero", team="party",
        hp_max=50, hp_current=50, ac=18, proficiency_bonus=3,
        ability_modifiers={"STR": 4},
    )
    goblin = CombatantState(
        id="goblin", display_name="Goblin", team="enemies",
        hp_max=1, hp_current=1, ac=13, proficiency_bonus=2,
        ability_modifiers={},
    )
    s = ScenarioState(combatants=[hero, goblin], dice=Dice(0))
    action = WeaponAttackAction(
        attacker_id="hero", target_id="goblin",
        attack_bonus=20, damage_dice=[(1, 6)], damage_type="slashing", damage_bonus=1,
    )
    resolve_action(action, s)
    deaths = [e for e in s.structured_events if isinstance(e, DeathEvent)]
    assert len(deaths) == 1
    assert deaths[0].combatant_id == "goblin"


def test_heal_emits_heal_event() -> None:
    cleric = CombatantState(
        id="cleric", display_name="Cleric", team="party",
        hp_max=40, hp_current=40, ac=16, proficiency_bonus=3,
        ability_modifiers={},
    )
    wounded = CombatantState(
        id="wounded", display_name="Wounded", team="party",
        hp_max=30, hp_current=5, ac=14, proficiency_bonus=2,
        ability_modifiers={},
    )
    s = ScenarioState(combatants=[cleric, wounded], dice=Dice(0))
    action = HealAction(caster_id="cleric", target_id="wounded", heal_bonus=10)
    resolve_action(action, s)
    heals = [e for e in s.structured_events if isinstance(e, HealEvent)]
    assert len(heals) == 1
    assert heals[0].caster_id == "cleric"
    assert heals[0].amount > 0


# ---------------------------------------------------------------------------
# DecisionLog
# ---------------------------------------------------------------------------

def test_decision_log_record() -> None:
    log = DecisionLog()
    action = WeaponAttackAction(attacker_id="hero", target_id="goblin")
    log.record(1, "hero", "martial", [action])
    assert len(log.records) == 1
    r = log.records[0]
    assert r.combatant_id == "hero"
    assert "weapon_attack" in r.action_types


def test_decision_log_for_combatant() -> None:
    log = DecisionLog()
    action = WeaponAttackAction(attacker_id="hero", target_id="g")
    log.record(1, "hero", "martial", [action])
    log.record(1, "cleric", "healer", [])
    assert len(log.for_combatant("hero")) == 1
    assert len(log.for_combatant("cleric")) == 1


def test_decision_log_for_round() -> None:
    log = DecisionLog()
    action = WeaponAttackAction(attacker_id="hero", target_id="g")
    log.record(1, "hero", "martial", [action])
    log.record(2, "hero", "martial", [action])
    assert len(log.for_round(1)) == 1
    assert len(log.for_round(2)) == 1


def test_decision_log_empty_actions() -> None:
    log = DecisionLog()
    log.record(1, "passive", "passive", None)
    assert log.records[0].action_types == []
