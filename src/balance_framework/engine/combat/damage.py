"""Damage application — resistance, vulnerability, immunity, temp HP, death."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.combat.conditions import apply_condition


@dataclass
class DamageResult:
    raw_damage: int          # before resistances
    applied_damage: int      # after resistances, after temp HP
    temp_hp_absorbed: int
    hp_before: int
    hp_after: int
    killed: bool
    instant_death: bool      # massive damage rule
    knocked_unconscious: bool


def apply_damage(
    target: "CombatantState",
    raw_damage: int,
    damage_type: str,
    from_crit: bool = False,
) -> DamageResult:
    """Apply *raw_damage* of *damage_type* to *target*, respecting all modifiers.

    PHB 2024 rules:
    - Immunity: damage is 0.
    - Resistance: round down after halving.
    - Vulnerability: double.
    - Temp HP absorbs damage first (not halved by resistance).
    - Instant death: if excess damage from a single hit equals or exceeds hp_max.
    """
    hp_before = target.hp_current
    instant_death = False
    knocked_out = False
    killed_flag = False

    # 1. Apply resistance / immunity / vulnerability
    effective = raw_damage
    if damage_type in target.damage_immunities:
        effective = 0
    elif damage_type in target.damage_resistances:
        effective = effective // 2
    elif damage_type in target.damage_vulnerabilities:
        effective = effective * 2

    # 2. Temp HP absorbs first
    temp_absorbed = min(target.temp_hp, effective)
    target.temp_hp -= temp_absorbed
    net = effective - temp_absorbed

    # 3. Apply to real HP
    if net > 0:
        target.hp_current -= net
        if target.hp_current <= 0:
            excess = -target.hp_current
            target.hp_current = 0
            if not target.is_alive:
                pass  # already dead
            else:
                # Instant death rule
                if excess >= target.hp_max:
                    target.is_alive = False
                    target.is_stable = False
                    instant_death = True
                    killed_flag = True
                else:
                    # Knocked unconscious / hit at 0 HP
                    from balance_framework.engine.combat.conditions import apply_condition
                    if "unconscious" not in target.conditions:
                        apply_condition(target, "unconscious")
                        apply_condition(target, "prone")
                        knocked_out = True
                    else:
                        # Already at 0 HP: extra hit adds death save failures
                        failures = 2 if from_crit else 1
                        target.death_save_failures += failures
                        if target.death_save_failures >= 3:
                            target.is_alive = False
                            killed_flag = True

    return DamageResult(
        raw_damage=raw_damage,
        applied_damage=effective,
        temp_hp_absorbed=temp_absorbed,
        hp_before=hp_before,
        hp_after=target.hp_current,
        killed=killed_flag,
        instant_death=instant_death,
        knocked_unconscious=knocked_out,
    )


def apply_healing(target: "CombatantState", amount: int) -> int:
    """Heal *target* for *amount* HP (capped at max).  Returns actual HP gained.

    Healing removes unconscious + prone conditions if the target was at 0 HP.
    """
    if not target.is_alive:
        return 0
    was_at_zero = target.hp_current <= 0
    gained = min(amount, target.hp_max - target.hp_current)
    target.hp_current += gained

    if was_at_zero and gained > 0:
        from balance_framework.engine.combat.conditions import remove_condition
        remove_condition(target, "unconscious")
        remove_condition(target, "prone")
        target.death_save_successes = 0
        target.death_save_failures = 0
        target.is_stable = False

    return gained


def add_temp_hp(target: "CombatantState", amount: int) -> int:
    """Grant temp HP; only the higher pool survives (they don't stack)."""
    if amount > target.temp_hp:
        target.temp_hp = amount
        return amount
    return 0
