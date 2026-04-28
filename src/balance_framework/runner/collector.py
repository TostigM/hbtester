"""Collect and summarise per-encounter results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.scenario import ScenarioState


@dataclass
class CombatantResult:
    """Final state for one combatant at the end of an encounter."""
    id: str
    display_name: str
    team: str
    hp_final: int
    hp_max: int
    is_alive: bool
    is_stable: bool  # alive but at 0 HP


@dataclass
class EncounterResult:
    """All observable outcomes from one completed encounter."""
    seed: int
    winner_team: str | None      # None = draw / timeout
    rounds: int
    timed_out: bool              # True if combat hit max_rounds without ending
    combatants: list[CombatantResult] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    def party_win(self) -> bool:
        return self.winner_team == "party"

    def enemies_win(self) -> bool:
        return self.winner_team == "enemies"

    def survivors(self, team: str) -> list[CombatantResult]:
        return [c for c in self.combatants if c.team == team and c.is_alive]

    def hp_remaining(self, team: str) -> int:
        return sum(c.hp_final for c in self.combatants if c.team == team and c.is_alive)

    def hp_fraction(self, team: str) -> float:
        """Average HP fraction (current/max) for living members of *team*."""
        living = [c for c in self.combatants if c.team == team and c.is_alive]
        if not living:
            return 0.0
        return sum(c.hp_final / c.hp_max for c in living) / len(living)


def collect_result(scenario: "ScenarioState", seed: int) -> EncounterResult:
    """Extract an EncounterResult from a completed ScenarioState."""
    combatants = [
        CombatantResult(
            id=c.id,
            display_name=c.display_name,
            team=c.team,
            hp_final=c.hp_current,
            hp_max=c.hp_max,
            is_alive=c.is_alive,
            is_stable=c.is_stable,
        )
        for c in scenario.combatants
    ]
    return EncounterResult(
        seed=seed,
        winner_team=scenario.winner_team,
        rounds=scenario.round_number,
        timed_out=not scenario.is_over,
        combatants=combatants,
    )
