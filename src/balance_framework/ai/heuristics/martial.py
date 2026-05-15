"""Martial heuristic — Fighter behavior AI.

Priority order per turn:
  1. Second Wind (bonus action) when HP <= 30% and available.
  2. Attack up to extra_attack_count times against the nearest living enemy.
     - Battle Master: spend a superiority die (1d8) on each attack.
     - Gloom Stalker: on round 1, one extra attack with +2d6 damage (Dread Ambusher).
     - Berserker: after attacks, bonus action weapon attack (Frenzy).
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
            heal_bonus=combatant.proficiency_bonus,
        ))

    # Sacred Weapon (Devotion) / Vow of Enmity (Vengeance): bonus action CD buff
    # Activate on first turn; bonus persists the whole combat via cd_offensive_active.
    if not combatant.cd_offensive_active and combatant.bonus_actions_remaining > 0:
        if (combatant.sacred_weapon or combatant.vow_of_enmity) and has_resource(combatant, "channel_divinity"):
            spend(combatant, "channel_divinity")
            combatant.cd_offensive_active = True
            combatant.bonus_actions_remaining -= 1

    # 2. Attack action
    target = nearest_enemy(combatant, scenario)
    if target is None:
        return actions or None

    str_mod = combatant.ability_modifiers.get("STR", 0)
    dex_mod = combatant.ability_modifiers.get("DEX", 0)
    stat_mod = max(str_mod, dex_mod)
    atk_bonus = stat_mod + combatant.proficiency_bonus
    dmg_bonus = stat_mod

    # Sacred Weapon: +CHA mod to attack rolls while buff is active
    if combatant.sacred_weapon and combatant.cd_offensive_active:
        atk_bonus += max(0, combatant.ability_modifiers.get("CHA", 0))

    # Vow of Enmity: advantage on all attacks while buff is active
    vow_advantage = combatant.vow_of_enmity and combatant.cd_offensive_active

    # Once-per-turn bonus damage (Hunter's Prey, Divine Fury, etc.)
    bonus_dice_remaining = list(combatant.bonus_damage_dice)

    # Dread Ambusher: one extra attack with +2d6 on round 1
    extra_attacks = combatant.extra_attack_count
    dread_active = combatant.dread_ambusher and scenario.round_number == 1

    for i in range(extra_attacks + (1 if dread_active else 0)):
        if not target.is_alive:
            target = nearest_enemy(combatant, scenario)
            if target is None:
                break

        dice: list[tuple[int, int]] = [(1, 8)]

        # Once-per-turn bonus dice (only on first attack)
        if bonus_dice_remaining:
            dice += bonus_dice_remaining
            bonus_dice_remaining = []

        # Dread Ambusher extra attack gets +2d6 and is the last in the loop
        if dread_active and i == extra_attacks:
            dice.append((2, 6))

        # Battle Master: spend a superiority die for +1d8 per attack
        if has_resource(combatant, "superiority_dice"):
            spend(combatant, "superiority_dice")
            dice.append((1, 8))

        actions.append(WeaponAttackAction(
            attacker_id=combatant.id,
            target_id=target.id,
            attack_bonus=atk_bonus,
            damage_dice=dice,
            damage_type="slashing",
            damage_bonus=dmg_bonus,
            advantage=vow_advantage,
        ))

    # Berserker Frenzy: bonus action attack (models rage being active)
    if (
        combatant.frenzy_bonus_attack
        and combatant.bonus_actions_remaining > 0
        and has_resource(combatant, "rage")
    ):
        t = target if target.is_alive else nearest_enemy(combatant, scenario)
        if t is not None:
            combatant.bonus_actions_remaining -= 1
            actions.append(WeaponAttackAction(
                attacker_id=combatant.id,
                target_id=t.id,
                attack_bonus=atk_bonus,
                damage_dice=[(1, 8)],
                damage_type="slashing",
                damage_bonus=dmg_bonus,
            ))

    # 3. Action Surge: repeat the attack action (bonus dice already spent)
    if has_resource(combatant, "action_surge") and target is not None and target.is_alive:
        spend(combatant, "action_surge")
        for _ in range(combatant.extra_attack_count):
            if not target.is_alive:
                target = nearest_enemy(combatant, scenario)
                if target is None:
                    break
            dice = [(1, 8)]
            if has_resource(combatant, "superiority_dice"):
                spend(combatant, "superiority_dice")
                dice.append((1, 8))
            actions.append(WeaponAttackAction(
                attacker_id=combatant.id,
                target_id=target.id,
                attack_bonus=atk_bonus,
                damage_dice=dice,
                damage_type="slashing",
                damage_bonus=dmg_bonus,
                advantage=vow_advantage,
            ))

    return actions or None
