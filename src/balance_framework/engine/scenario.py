"""ScenarioState — the top-level mutable state of one combat encounter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.logging.event_log import CombatEvent
    from balance_framework.logging.decision_log import DecisionLog

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice


@dataclass
class ScenarioState:
    """Mutable state for one complete combat encounter."""

    combatants: list[CombatantState]
    dice: Dice
    round_number: int = 0
    initiative_order: list[str] = field(default_factory=list)  # combatant IDs
    current_turn_index: int = 0
    is_over: bool = False
    winner_team: str | None = None

    # Event log (plain strings for human-readable output)
    events: list[str] = field(default_factory=list)

    # Structured events (typed; populated alongside events list)
    structured_events: list["CombatEvent"] = field(default_factory=list)

    # Optional decision log (populated by the AI dispatcher if attached)
    decision_log: "DecisionLog | None" = None

    # Tracking for Help action targets
    helped_targets: set[str] = field(default_factory=set)

    # Per-combatant stat accumulation (keyed by combatant ID)
    damage_dealt: dict[str, int] = field(default_factory=dict)
    kills: dict[str, int] = field(default_factory=dict)
    healing_done: dict[str, int] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def get_combatant(self, id: str) -> CombatantState:
        for c in self.combatants:
            if c.id == id:
                return c
        raise KeyError(f"No combatant with id {id!r} in scenario")

    def living_combatants(self) -> list[CombatantState]:
        return [c for c in self.combatants if c.is_alive]

    def conscious_combatants(self) -> list[CombatantState]:
        return [c for c in self.combatants if c.is_conscious]

    def combatants_for_team(self, team: str) -> list[CombatantState]:
        return [c for c in self.combatants if c.team == team]

    def living_teams(self) -> set[str]:
        return {c.team for c in self.combatants if c.is_alive}

    def log(self, event: str) -> None:
        self.events.append(event)

    def current_combatant(self) -> CombatantState | None:
        if not self.initiative_order or self.current_turn_index >= len(self.initiative_order):
            return None
        cid = self.initiative_order[self.current_turn_index]
        return self.get_combatant(cid)

    # ------------------------------------------------------------------
    # Serialisable snapshot for determinism tests
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, object]:
        """Return a minimal, serialisable snapshot of key state for comparison."""
        return {
            "round": self.round_number,
            "is_over": self.is_over,
            "winner_team": self.winner_team,
            "combatants": [
                {
                    "id": c.id,
                    "hp": c.hp_current,
                    "temp_hp": c.temp_hp,
                    "is_alive": c.is_alive,
                    "is_stable": c.is_stable,
                    "conditions": sorted(c.conditions.keys()),
                    "concentrating_on": c.concentrating_on,
                    "death_successes": c.death_save_successes,
                    "death_failures": c.death_save_failures,
                }
                for c in self.combatants
            ],
        }
