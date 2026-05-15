"""Healer heuristic — Cleric behavior AI.

Priority order per turn:
  1. Heal an unconscious ally (Cure Wounds, L1 slot) if any are down.
  2. Heal any ally below 30% HP if a slot is available.
  3. Attack nearest enemy (weapon / cantrip).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action

from balance_framework.engine.combat.actions import WeaponAttackAction, HealAction
from balance_framework.engine.combat.resources import has_resource
from balance_framework.engine.grid import nearest_enemy


def healer_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Action selector for healer combatants (clerics, etc.)."""
    wis_mod = combatant.ability_modifiers.get("WIS", 0)

    # 1. Revive an unconscious ally first
    if has_resource(combatant, "spell_slot_1"):
        unconscious_ally = _find_ally(combatant, scenario, unconscious_only=True)
        if unconscious_ally is not None:
            return [HealAction(
                caster_id=combatant.id,
                target_id=unconscious_ally.id,
                heal_dice=[(1, 8)],
                heal_bonus=wis_mod,
                resource_pool="spell_slot_1",
            )]

    # 2. Heal a bloodied ally
    if has_resource(combatant, "spell_slot_1"):
        wounded_ally = _find_ally(combatant, scenario, below_pct=0.30)
        if wounded_ally is not None:
            return [HealAction(
                caster_id=combatant.id,
                target_id=wounded_ally.id,
                heal_dice=[(1, 8)],
                heal_bonus=wis_mod,
                resource_pool="spell_slot_1",
            )]

    # 3. Attack nearest enemy (mace / cantrip)
    target = nearest_enemy(combatant, scenario)
    if target is None:
        return None

    atk_bonus = (
        combatant.ability_modifiers.get("STR", 0) + combatant.proficiency_bonus
    )
    dmg_bonus = combatant.ability_modifiers.get("STR", 0)

    return [WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=atk_bonus,
        damage_dice=[(1, 6)],
        damage_type="bludgeoning",
        damage_bonus=dmg_bonus,
    )]


def _find_ally(
    combatant: "CombatantState",
    scenario: "ScenarioState",
    unconscious_only: bool = False,
    below_pct: float = 1.0,
) -> "CombatantState | None":
    """Find the most wounded ally matching the criteria (excluding self)."""
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
    # Also check unconscious (at 0 HP) allies not in living_combatants
    if unconscious_only:
        for c in scenario.combatants:
            if c.id == combatant.id or c.team != combatant.team:
                continue
            if c.is_alive and not c.is_conscious:
                return c
    return best
