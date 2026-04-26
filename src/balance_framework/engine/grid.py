"""Minimal positioning layer — abstract distance between combatants.

For M3 the engine treats every fight as taking place in an abstract arena where
all enemies are adjacent to the active combatant unless stated otherwise.
A full grid implementation can be added in a later milestone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState


@dataclass
class Position:
    x: int = 0
    y: int = 0

    def distance_to(self, other: "Position") -> float:
        import math
        return math.hypot(self.x - other.x, self.y - other.y) * 5  # 5-ft grid


class AbstractArena:
    """All combatants are within reach of each other unless separated by teams."""

    def __init__(self) -> None:
        self._positions: dict[str, Position] = {}

    def place(self, combatant_id: str, position: Position | None = None) -> None:
        self._positions[combatant_id] = position or Position()

    def distance_feet(self, id_a: str, id_b: str) -> int:
        """Return distance in feet.  Returns 5 ft (adjacent) if not positioned."""
        if id_a not in self._positions or id_b not in self._positions:
            return 5  # treat all as adjacent in abstract mode
        a = self._positions[id_a]
        b = self._positions[id_b]
        return int(a.distance_to(b))

    def is_adjacent(self, id_a: str, id_b: str, reach: int = 5) -> bool:
        return self.distance_feet(id_a, id_b) <= reach


def nearest_enemy(
    combatant: "CombatantState",
    scenario: object,  # ScenarioState — avoid circular import
) -> "CombatantState | None":
    """Return the first living enemy of *combatant* in initiative order."""
    from balance_framework.engine.scenario import ScenarioState
    assert isinstance(scenario, ScenarioState)
    for cid in scenario.initiative_order:
        try:
            other = scenario.get_combatant(cid)
        except KeyError:
            continue
        if other.team != combatant.team and other.is_alive:
            return other
    return None
