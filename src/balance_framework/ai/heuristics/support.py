"""Support and Rogue heuristics.

support_selector (Bard, Druid, Cleric) priority:
  1. Heal an unconscious ally (L1 slot).
  2. Heal any ally below 30% HP (L1 slot).
  3. Cast a leveled offensive spell (highest available slot).
  4. Cantrip attack using spell_attack_bonus.
  War Domain: after any offensive action, fire War Priest bonus attack.

rogue_selector (Rogue) priority:
  1. Attack nearest enemy with Sneak Attack damage.
  Assassin: advantage on all attacks in round 1 (Assassinate).
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
from balance_framework.ai.heuristics.caster import _cantrip_count_sides
from balance_framework.ai.choice_scorer import select_best_pool_option


def support_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Action selector for support casters (bard, druid, cleric)."""
    cast_mod = (combatant.spell_attack_bonus or 0) - combatant.proficiency_bonus

    # 1. Revive an unconscious ally
    if has_resource(combatant, "spell_slot_1"):
        unconscious = _find_ally(combatant, scenario, unconscious_only=True)
        if unconscious is not None:
            return [HealAction(
                caster_id=combatant.id,
                target_id=unconscious.id,
                heal_dice=[(1, 8)],
                heal_bonus=cast_mod,
                resource_pool="spell_slot_1",
            )]

    # 2. Heal a bloodied ally
    if has_resource(combatant, "spell_slot_1"):
        wounded = _find_ally(combatant, scenario, below_pct=0.30)
        if wounded is not None:
            return [HealAction(
                caster_id=combatant.id,
                target_id=wounded.id,
                heal_dice=[(1, 8)],
                heal_bonus=cast_mod,
                resource_pool="spell_slot_1",
            )]

    # 3. Offensive spell (leveled) — mirrors caster_selector
    target = nearest_enemy(combatant, scenario)
    if target is None:
        return None

    spell_atk = combatant.spell_attack_bonus or 0
    spell_dmg_bonus = combatant.bonus_damage_flat
    for slot_level in range(5, 0, -1):
        pool = f"spell_slot_{slot_level}"
        if has_resource(combatant, pool):
            spend(combatant, pool)
            dice = [(8, 6)] if slot_level >= 3 else [(slot_level + 1, 10)]
            main = WeaponAttackAction(
                attacker_id=combatant.id,
                target_id=target.id,
                attack_bonus=spell_atk,
                damage_dice=dice,
                damage_type="fire",
                damage_bonus=spell_dmg_bonus,
                is_ranged=True,
            )
            return [main] + _war_priest_bonus(combatant, target)

    # 4. Cantrip
    count, sides = _cantrip_count_sides(combatant.proficiency_bonus)
    main = WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=spell_atk,
        damage_dice=[(count, sides)],
        damage_type="fire",
        damage_bonus=spell_dmg_bonus,
        is_ranged=True,
    )
    extra = _war_priest_bonus(combatant, target)

    # Bonus action pool option (if war_priest didn't consume it)
    if combatant.bonus_actions_remaining > 0 and combatant.active_pool_features:
        pool_action = select_best_pool_option(combatant, scenario, "bonus_action")
        if pool_action is not None:
            combatant.bonus_actions_remaining -= 1
            extra.append(pool_action)

    return [main] + extra


def _war_priest_bonus(
    combatant: "CombatantState",
    target: "CombatantState",
) -> "list[Action]":
    """Return a bonus action weapon attack if War Priest is available."""
    if (
        not combatant.war_priest_attack
        or combatant.bonus_actions_remaining <= 0
        or not has_resource(combatant, "war_priest")
        or not target.is_alive
    ):
        return []
    spend(combatant, "war_priest")
    combatant.bonus_actions_remaining -= 1
    str_mod = combatant.ability_modifiers.get("STR", 0)
    return [WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=str_mod + combatant.proficiency_bonus,
        damage_dice=[(1, 8)],
        damage_type="slashing",
        damage_bonus=str_mod,
    )]


def _find_ally(
    combatant: "CombatantState",
    scenario: "ScenarioState",
    unconscious_only: bool = False,
    below_pct: float = 1.0,
) -> "CombatantState | None":
    best = None
    best_hp_pct = 1.0
    for c in scenario.living_combatants():
        if c.id == combatant.id or c.team != combatant.team:
            continue
        if unconscious_only and c.is_conscious:
            continue
        hp_pct = c.hp_current / c.hp_max
        if hp_pct < below_pct and hp_pct < best_hp_pct:
            best = c
            best_hp_pct = hp_pct
    if unconscious_only:
        for c in scenario.combatants:
            if c.id == combatant.id or c.team != combatant.team:
                continue
            if c.is_alive and not c.is_conscious:
                return c
    return best


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

    # Sneak attack (fires every turn — ally always adjacent in the abstract arena)
    sneak_dice = combatant.sneak_attack_dice
    if sneak_dice > 0:
        damage_dice.append((sneak_dice, 6))

    # Assassinate: advantage on all attacks in round 1 (before enemies have acted)
    advantage = combatant.assassinate and scenario.round_number == 1

    return [WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=atk_bonus,
        damage_dice=damage_dice,
        damage_type="piercing",
        damage_bonus=dex_mod,
        advantage=advantage,
    )]
