"""Initiative rolling and ordering."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.dice import Dice


def roll_initiative(combatant: "CombatantState", dice: "Dice") -> int:
    """Roll initiative for one combatant: d20 + DEX mod.

    Stores the result on combatant.initiative and combatant.initiative_tiebreak.
    Returns the raw d20 result (before modifier).
    """
    raw = dice.d20()
    dex_mod = combatant.ability_modifiers.get("DEX", 0)
    combatant.initiative = raw + dex_mod
    combatant.initiative_tiebreak = dex_mod  # PHB tie-break rule
    return raw


def roll_all_initiative(combatants: list["CombatantState"], dice: "Dice") -> None:
    """Roll initiative for every combatant in place."""
    for c in combatants:
        roll_initiative(c, dice)


def build_initiative_order(combatants: list["CombatantState"]) -> list["CombatantState"]:
    """Sort combatants by initiative (desc), then DEX mod (desc) as tiebreaker.

    Returns a new list; does not modify the input.
    """
    return sorted(
        combatants,
        key=lambda c: (c.initiative, c.initiative_tiebreak),
        reverse=True,
    )
