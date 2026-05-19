"""Caster heuristic — Wizard behavior AI.

Priority order per turn:
  1. Use a leveled spell (modelled as a spell-attack roll with bonus damage)
     when a L1+ slot is available.
  2. Cantrip attack (fire bolt equivalent) using spell_attack_bonus.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action

from balance_framework.engine.combat.actions import WeaponAttackAction
from balance_framework.engine.combat.resources import has_resource, spend
from balance_framework.engine.grid import nearest_enemy
from balance_framework.ai.choice_scorer import select_best_pool_option


# Cantrip damage by character level (Fire Bolt / Eldritch Blast tiers)
_CANTRIP_DICE: dict[int, tuple[int, int]] = {
    1: (1, 10),   # L1-4
    5: (2, 10),   # L5-10
    11: (3, 10),  # L11-16
    17: (4, 10),  # L17+
}


def _cantrip_count_sides(prof_bonus: int) -> tuple[int, int]:
    """Map proficiency bonus to cantrip dice (proxy for character level tiers)."""
    # prof 2=L1-4, 3=L5-8, 4=L9-12, 5=L13-16, 6=L17-20
    level_approx = {2: 1, 3: 5, 4: 11, 5: 11, 6: 17}.get(prof_bonus, 1)
    for threshold in sorted(_CANTRIP_DICE.keys(), reverse=True):
        if level_approx >= threshold:
            return _CANTRIP_DICE[threshold]
    return (1, 10)


def caster_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Action selector for arcane casters (wizards, sorcerers, etc.)."""
    target = nearest_enemy(combatant, scenario)
    if target is None:
        return None

    spell_atk = combatant.spell_attack_bonus or 0
    spell_dmg_bonus = combatant.bonus_damage_flat  # e.g. Elemental Affinity (Draconic CHA mod)

    # 1. Leveled spell (modelled as a powered-up spell attack)
    #    Uses the best available slot (highest level first)
    for slot_level in range(5, 0, -1):
        pool = f"spell_slot_{slot_level}"
        if has_resource(combatant, pool):
            spend(combatant, pool)
            if slot_level >= 3:
                dice = [(8, 6)]  # 8d6 fireball baseline
            else:
                dice = [(slot_level + 1, 10)]
            return [WeaponAttackAction(
                attacker_id=combatant.id,
                target_id=target.id,
                attack_bonus=spell_atk,
                damage_dice=dice,
                damage_type="fire",
                damage_bonus=spell_dmg_bonus,
                is_ranged=True,
            )]

    # 2. Cantrip (no resource cost)
    count, sides = _cantrip_count_sides(combatant.proficiency_bonus)
    actions = [WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=spell_atk,
        damage_dice=[(count, sides)],
        damage_type="fire",
        damage_bonus=spell_dmg_bonus,
        is_ranged=True,
    )]

    # Bonus action: use the highest-utility pool option if available
    if combatant.bonus_actions_remaining > 0 and combatant.active_pool_features:
        pool_action = select_best_pool_option(combatant, scenario, "bonus_action")
        if pool_action is not None:
            combatant.bonus_actions_remaining -= 1
            actions.append(pool_action)

    return actions
