"""Monster behavior AI — melee and caster profiles."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action

from balance_framework.engine.combat.actions import BreathWeaponAction, WeaponAttackAction
from balance_framework.engine.combat.resources import has_resource
from balance_framework.engine.grid import nearest_enemy


def monster_melee_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Melee monster: use breath weapon when available, otherwise multiattack.

    Uses melee_attack_bonus override when set, otherwise STR + proficiency.
    """
    # Use breath weapon if available — limited resource, use it first
    if combatant.breath_weapon_config and has_resource(combatant, "breath_weapon"):
        cfg = combatant.breath_weapon_config
        return [BreathWeaponAction(
            attacker_id=combatant.id,
            damage_dice=[(int(cfg["damage_die_count"]), int(cfg["damage_die"]))],
            damage_type=str(cfg["damage_type"]),
            save_ability=str(cfg["save_ability"]),
            save_dc=int(cfg["save_dc"]),
        )]

    target = nearest_enemy(combatant, scenario)
    if target is None:
        return None

    str_mod = combatant.ability_modifiers.get("STR", 0)
    if combatant.melee_attack_bonus is not None:
        atk_bonus = combatant.melee_attack_bonus
    else:
        atk_bonus = str_mod + combatant.proficiency_bonus
    dmg_dice = combatant.primary_damage_dice

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
            damage_dice=dmg_dice,
            damage_type="slashing",
            damage_bonus=str_mod,
        ))

    return actions or None


def monster_caster_selector(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """Monster caster: delegates to the shared caster heuristic."""
    from balance_framework.ai.heuristics.caster import caster_selector
    return caster_selector(combatant, scenario)
