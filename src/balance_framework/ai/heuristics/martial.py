"""Martial heuristic — Fighter behavior AI.

Priority order per turn:
  1. Second Wind (bonus action) when HP <= 30% and available.
  2. Attack up to extra_attack_count times against the nearest living enemy.
  3. Action Surge: spend it if any enemies remain after the main attack.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action

from balance_framework.engine.combat.actions import WeaponAttackAction, HealAction
from balance_framework.engine.combat.resources import has_resource, spend
from balance_framework.engine.grid import nearest_enemy


def martial_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Action selector for martial combatants (fighters, paladins, etc.)."""
    actions: list[Action] = []

    # 1. Second Wind when bloodied (<= 30% HP)
    if (
        combatant.hp_current <= combatant.hp_max * 0.30
        and combatant.bonus_actions_remaining > 0
        and has_resource(combatant, "second_wind")
    ):
        spend(combatant, "second_wind")
        combatant.bonus_actions_remaining -= 1
        actions.append(HealAction(
            caster_id=combatant.id,
            target_id=combatant.id,
            heal_dice=[(1, 10)],
            heal_bonus=combatant.proficiency_bonus,  # approx fighter level bonus
        ))

    # 2. Attack action (up to extra_attack_count attacks)
    target = nearest_enemy(combatant, scenario)
    if target is None:
        return actions or None

    # Use the better of STR or DEX (covers DEX-based martials like ranger/monk)
    str_mod = combatant.ability_modifiers.get("STR", 0)
    dex_mod = combatant.ability_modifiers.get("DEX", 0)
    stat_mod = max(str_mod, dex_mod)
    atk_bonus = stat_mod + combatant.proficiency_bonus
    dmg_bonus = stat_mod

    # Once-per-turn bonus damage (e.g. Hunter's Prey, Divine Fury)
    bonus_dice_remaining = list(combatant.bonus_damage_dice)

    for _ in range(combatant.extra_attack_count):
        # Re-check target is still alive between attacks
        if not target.is_alive:
            target = nearest_enemy(combatant, scenario)
            if target is None:
                break
        extra = bonus_dice_remaining
        bonus_dice_remaining = []  # only first attack gets the bonus
        actions.append(WeaponAttackAction(
            attacker_id=combatant.id,
            target_id=target.id,
            attack_bonus=atk_bonus,
            damage_dice=[(1, 8)] + extra,  # longsword / versatile + once-per-turn bonus
            damage_type="slashing",
            damage_bonus=dmg_bonus,
        ))

    # 3. Action Surge: repeat the attack action (bonus dice already spent this turn)
    if has_resource(combatant, "action_surge") and target is not None and target.is_alive:
        spend(combatant, "action_surge")
        for _ in range(combatant.extra_attack_count):
            if not target.is_alive:
                target = nearest_enemy(combatant, scenario)
                if target is None:
                    break
            actions.append(WeaponAttackAction(
                attacker_id=combatant.id,
                target_id=target.id,
                attack_bonus=atk_bonus,
                damage_dice=[(1, 8)],
                damage_type="slashing",
                damage_bonus=dmg_bonus,
            ))

    return actions or None
