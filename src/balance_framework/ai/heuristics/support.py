"""Rogue heuristic — Thief/Rogue behavior AI.

Priority order per turn:
  1. Attack nearest enemy with Sneak Attack damage (once per turn).
     Sneak attack applies when an ally is adjacent to the target (always true in
     the abstract arena) or when the rogue has advantage.
  2. Bonus action: Cunning Action — Disengage (no mechanical effect yet;
     logged for future use).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action

from balance_framework.engine.combat.actions import WeaponAttackAction
from balance_framework.engine.grid import nearest_enemy


def rogue_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Action selector for rogue combatants."""
    target = nearest_enemy(combatant, scenario)
    if target is None:
        return None

    dex_mod = combatant.ability_modifiers.get("DEX", 0)
    atk_bonus = dex_mod + combatant.proficiency_bonus

    # Base weapon damage: short sword / rapier (1d6 finesse)
    damage_dice: list[tuple[int, int]] = [(1, 6)]

    # Sneak attack dice (the rogue gets these once per turn when conditions met)
    # In the abstract arena an ally is always adjacent, so sneak attack fires.
    sneak_dice = combatant.sneak_attack_dice
    if sneak_dice > 0:
        damage_dice.append((sneak_dice, 6))

    return [WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=atk_bonus,
        damage_dice=damage_dice,
        damage_type="piercing",
        damage_bonus=dex_mod,
    )]
