"""Support and Rogue heuristics.

support_selector (Bard, Druid) priority:
  1. Heal an unconscious ally (L1 slot).
  2. Heal any ally below 30% HP (L1 slot).
  3. Cast a leveled offensive spell (highest available slot).
  4. Cantrip attack using spell_attack_bonus.

rogue_selector (Rogue) priority:
  1. Attack nearest enemy with Sneak Attack damage.
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


def support_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Action selector for support casters (bard, druid)."""
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
    for slot_level in range(5, 0, -1):
        pool = f"spell_slot_{slot_level}"
        if has_resource(combatant, pool):
            spend(combatant, pool)
            dice = [(8, 6)] if slot_level >= 3 else [(slot_level + 1, 10)]
            return [WeaponAttackAction(
                attacker_id=combatant.id,
                target_id=target.id,
                attack_bonus=spell_atk,
                damage_dice=dice,
                damage_type="fire",
                damage_bonus=0,
                is_ranged=True,
            )]

    # 4. Cantrip
    count, sides = _cantrip_count_sides(combatant.proficiency_bonus)
    return [WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=spell_atk,
        damage_dice=[(count, sides)],
        damage_type="fire",
        damage_bonus=0,
        is_ranged=True,
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
