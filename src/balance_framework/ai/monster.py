"""Monster behavior AI — simple melee attacker."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action

from balance_framework.engine.combat.actions import WeaponAttackAction
from balance_framework.engine.grid import nearest_enemy


def monster_melee_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Simple melee monster: attack the nearest living enemy once per turn.

    Uses STR for the attack roll and 1d6+STR slashing damage.
    Respects extra_attack_count (e.g. for multi-attack monsters).
    """
    target = nearest_enemy(combatant, scenario)
    if target is None:
        return None

    str_mod = combatant.ability_modifiers.get("STR", 0)
    atk_bonus = str_mod + combatant.proficiency_bonus

    actions: list[Action] = []
    for _ in range(combatant.extra_attack_count):
        if not target.is_alive:
            target = nearest_enemy(combatant, scenario)
            if target is None:
                break
        actions.append(WeaponAttackAction(
            attacker_id=combatant.id,
            target_id=target.id,
            attack_bonus=atk_bonus,
            damage_dice=[(1, 6)],
            damage_type="slashing",
            damage_bonus=str_mod,
        ))

    return actions or None
