"""Saving throw resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.dice import Dice


@dataclass
class SaveResult:
    raw_roll: int
    second_roll: int | None  # non-None when advantage/disadvantage
    kept_roll: int
    modifier: int
    total: int
    dc: int
    success: bool
    nat_1: bool
    nat_20: bool
    had_advantage: bool
    had_disadvantage: bool


def resolve_save(
    combatant: "CombatantState",
    ability: str,
    dc: int,
    dice: "Dice",
    advantage: bool = False,
    disadvantage: bool = False,
    legendary_resistance: bool = False,
) -> SaveResult:
    """Resolve a saving throw for *combatant* against *dc*.

    PHB 2024 rules:
    - Add proficiency bonus if proficient in *ability*.
    - Advantage / disadvantage cancel to normal if both present.
    - Auto-fail STR/DEX saves when paralyzed/unconscious/etc.
    - Legendary resistance: automatically succeed (uses one charge).
    """
    from balance_framework.engine.combat.conditions import auto_fails_str_dex

    mod = combatant.ability_modifiers.get(ability, 0)
    if ability in combatant.saving_throw_proficiencies:
        mod += combatant.proficiency_bonus
    # saving_throw_advantages can grant advantage on specific saves
    if ability in combatant.saving_throw_advantages:
        advantage = True

    # Auto-fail on STR/DEX saves when incapacitated by paralysis etc.
    if ability in ("STR", "DEX") and auto_fails_str_dex(combatant):
        return SaveResult(
            raw_roll=1, second_roll=None, kept_roll=1,
            modifier=mod, total=1 + mod, dc=dc,
            success=False, nat_1=True, nat_20=False,
            had_advantage=False, had_disadvantage=False,
        )

    # Legendary resistance overrides everything
    if legendary_resistance:
        return SaveResult(
            raw_roll=20, second_roll=None, kept_roll=20,
            modifier=mod, total=20 + mod, dc=dc,
            success=True, nat_1=False, nat_20=True,
            had_advantage=advantage, had_disadvantage=disadvantage,
        )

    # Advantage and disadvantage cancel
    net_adv = advantage and not disadvantage
    net_dis = disadvantage and not advantage

    if net_adv:
        kept, other = dice.d20_advantage()
    elif net_dis:
        kept, other = dice.d20_disadvantage()
    else:
        kept, other = dice.d20_normal()

    total = kept + mod
    nat_1 = kept == 1
    nat_20 = kept == 20

    return SaveResult(
        raw_roll=kept,
        second_roll=other if (net_adv or net_dis) else None,
        kept_roll=kept,
        modifier=mod,
        total=total,
        dc=dc,
        success=total >= dc,
        nat_1=nat_1,
        nat_20=nat_20,
        had_advantage=net_adv,
        had_disadvantage=net_dis,
    )
