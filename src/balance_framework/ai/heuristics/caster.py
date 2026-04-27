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
    int_mod = combatant.ability_modifiers.get("INT", 0)

    # 1. Leveled spell (modelled as a powered-up spell attack)
    #    Uses the best available slot (highest level first)
    for slot_level in range(5, 0, -1):
        pool = f"spell_slot_{slot_level}"
        if has_resource(combatant, pool):
            # Damage scales: slot_level d6 + slot_level d6 extra (simulate)
            # e.g. L1 = 2d10, L2 = 3d10, L3 = 5d6 (fireball)
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
                damage_bonus=0,
                is_ranged=True,
                # Mark as spell slot spend via resource — handled post-action for simplicity
                # (actual spend happens here so AI doesn't double-spend)
            )] + [_spend_slot_side_effect(combatant, pool)]

    # 2. Cantrip (no resource cost)
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


def _spend_slot_side_effect(combatant: "CombatantState", pool: str) -> "Action":
    """Return a no-op HealAction that triggers the resource spend as a side-effect.

    This keeps the spend inside the action resolution pipeline so it shows up
    in tests, rather than mutating resources during selector execution.
    """
    # Actually spend inline — the selector runs before actions are resolved.
    spend(combatant, pool)
    # Return a zero-effect heal on self so the list length stays consistent.
    from balance_framework.engine.combat.actions import HealAction
    return HealAction(
        caster_id=combatant.id,
        target_id=combatant.id,
        heal_dice=[],
        heal_bonus=0,
    )
