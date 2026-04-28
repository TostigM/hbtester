"""Structured combat event types.

These complement the plain-string event list on ScenarioState.  Each resolver
emits both a human-readable string (for the existing events list) and a typed
CombatEvent (appended to structured_events).  Consumers that want structured
data use structured_events; humans and legacy code use events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass(frozen=True)
class AttackEvent:
    """A single weapon attack, hit or miss."""
    event_type: str = "attack"
    round_number: int = 0
    attacker_id: str = ""
    target_id: str = ""
    roll: int = 0           # d20 result (before bonus)
    total: int = 0          # roll + attack_bonus
    target_ac: int = 0
    hit: bool = False
    crit: bool = False
    damage: int = 0         # applied damage (0 on miss)
    damage_type: str = ""
    killed: bool = False


@dataclass(frozen=True)
class HealEvent:
    """A heal action by a caster on a target."""
    event_type: str = "heal"
    round_number: int = 0
    caster_id: str = ""
    target_id: str = ""
    amount: int = 0         # HP gained (after cap)
    resource_spent: str | None = None


@dataclass(frozen=True)
class DeathEvent:
    """A combatant is killed or falls unconscious."""
    event_type: str = "death"
    round_number: int = 0
    combatant_id: str = ""
    team: str = ""
    instant_death: bool = False   # True = massive damage; False = 3 death failures


@dataclass(frozen=True)
class RoundStartEvent:
    """Marks the beginning of a new round."""
    event_type: str = "round_start"
    round_number: int = 0


@dataclass(frozen=True)
class CombatEndEvent:
    """Marks the end of combat."""
    event_type: str = "combat_end"
    round_number: int = 0
    winner_team: str | None = None
    timed_out: bool = False


CombatEvent = Union[AttackEvent, HealEvent, DeathEvent, RoundStartEvent, CombatEndEvent]
