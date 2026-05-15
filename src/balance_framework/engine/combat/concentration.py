"""Concentration tracking and break checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.dice import Dice


@dataclass
class ConcentrationCheckResult:
    damage: int
    dc: int
    save_result: object  # SaveResult
    maintained: bool
    spell_lost: str | None  # spell id if concentration broken


def concentration_dc(damage: int) -> int:
    """PHB 2024: DC = max(10, damage // 2)."""
    return max(10, damage // 2)


def check_concentration(
    caster: "CombatantState",
    damage: int,
    dice: "Dice",
    war_caster_advantage: bool = False,
) -> ConcentrationCheckResult:
    """Check whether *caster* maintains concentration after taking *damage*.

    Also broken automatically if the caster becomes incapacitated.
    Returns a ConcentrationCheckResult; if maintained=False the caller should
    call ``break_concentration(caster)``.
    """
    from balance_framework.engine.combat.saves import resolve_save
    from balance_framework.engine.combat.conditions import is_incapacitated

    spell_id = caster.concentrating_on

    # Incapacitation breaks concentration immediately (no save)
    if is_incapacitated(caster):
        break_concentration(caster)
        from balance_framework.engine.combat.saves import SaveResult
        dummy = SaveResult(
            raw_roll=1, second_roll=None, kept_roll=1,
            modifier=0, total=1, dc=10,
            success=False, nat_1=True, nat_20=False,
            had_advantage=False, had_disadvantage=False,
        )
        return ConcentrationCheckResult(
            damage=damage, dc=10, save_result=dummy,
            maintained=False, spell_lost=spell_id,
        )

    dc = concentration_dc(damage)
    save = resolve_save(
        caster, "CON", dc, dice, advantage=war_caster_advantage
    )

    if not save.success:
        break_concentration(caster)
        return ConcentrationCheckResult(
            damage=damage, dc=dc, save_result=save,
            maintained=False, spell_lost=spell_id,
        )

    return ConcentrationCheckResult(
        damage=damage, dc=dc, save_result=save,
        maintained=True, spell_lost=None,
    )


def break_concentration(caster: "CombatantState") -> str | None:
    """Immediately end concentration; returns the spell id that was lost."""
    spell = caster.concentrating_on
    caster.concentrating_on = None
    return spell


def start_concentration(caster: "CombatantState", spell_id: str) -> None:
    """Start concentrating on *spell_id*, breaking any previous concentration."""
    if caster.concentrating_on is not None:
        break_concentration(caster)
    caster.concentrating_on = spell_id
