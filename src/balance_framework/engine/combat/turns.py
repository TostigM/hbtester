"""Turn/round management — start-of-turn and end-of-turn hooks."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.dice import Dice


def start_turn(combatant: "CombatantState", dice: "Dice") -> list[str]:
    """Reset action economy; process start-of-turn effects.

    Returns a list of event strings (death save result, condition expiry, etc.).
    """
    from balance_framework.engine.combat.conditions import (
        is_incapacitated,
        tick_conditions,
    )

    events: list[str] = []

    # Reset per-turn resources
    if not is_incapacitated(combatant) or combatant.is_at_zero_hp:
        combatant.actions_remaining = 1
        combatant.bonus_actions_remaining = 1
        combatant.movement_remaining = combatant.speed
    else:
        combatant.actions_remaining = 0
        combatant.bonus_actions_remaining = 0
        combatant.movement_remaining = 0

    combatant.reactions_remaining = 1  # reset even if incapacitated

    # Death saves (only while at 0 HP and alive)
    if combatant.is_at_zero_hp and combatant.is_alive and not combatant.is_stable:
        result = _roll_death_save(combatant, dice)
        events.append(result)

    # Tick timed conditions (start-of-turn)
    expired = tick_conditions(combatant)
    for cond in expired:
        events.append(f"{combatant.display_name}: condition {cond!r} expired")

    return events


def end_turn(combatant: "CombatantState") -> list[str]:
    """Process end-of-turn effects (end-of-turn condition ticks, etc.)."""
    events: list[str] = []
    # Most conditions are ticked at start of next turn; reserved for future use.
    return events


def _roll_death_save(combatant: "CombatantState", dice: "Dice") -> str:
    """Roll one death saving throw.  Mutates death_save_successes/failures."""
    from balance_framework.engine.dice import Dice as _D  # local import avoids cycle

    roll = dice.d20()

    if roll == 20:
        # Nat 20: regain 1 HP and regain consciousness
        from balance_framework.engine.combat.conditions import remove_condition
        combatant.hp_current = 1
        remove_condition(combatant, "unconscious")
        combatant.death_save_successes = 0
        combatant.death_save_failures = 0
        return f"{combatant.display_name} nat 20 on death save — regains 1 HP!"

    if roll == 1:
        combatant.death_save_failures += 2
    elif roll >= 10:
        combatant.death_save_successes += 1
    else:
        combatant.death_save_failures += 1

    if combatant.death_save_failures >= 3:
        combatant.is_alive = False
        from balance_framework.engine.combat.conditions import remove_condition
        remove_condition(combatant, "unconscious")
        return f"{combatant.display_name} failed 3 death saves — DEAD"

    if combatant.death_save_successes >= 3:
        combatant.is_stable = True
        return f"{combatant.display_name} passed 3 death saves — STABLE"

    suc = combatant.death_save_successes
    fail = combatant.death_save_failures
    return (
        f"{combatant.display_name} death save roll {roll}: "
        f"{suc}/3 successes, {fail}/3 failures"
    )
