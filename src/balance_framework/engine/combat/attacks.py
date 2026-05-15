"""Attack roll resolution — the full 5e 2024 attack pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.dice import Dice


@dataclass
class WeaponAttack:
    """Specification for one weapon attack (or unarmed strike)."""

    attacker_id: str
    target_id: str
    attack_bonus: int          # total to-hit modifier
    damage_dice: list[tuple[int, int]]  # list of (count, sides) e.g. [(1, 8)]
    damage_type: str
    damage_bonus: int = 0      # flat damage bonus (ability mod + magic bonus)
    crit_extra_dice: list[tuple[int, int]] = field(default_factory=list)  # extra on crit
    is_ranged: bool = False
    advantage: bool = False    # external advantage (e.g. from Help action)
    disadvantage: bool = False  # external disadvantage


@dataclass
class AttackResult:
    hit: bool
    crit: bool
    nat_1: bool
    nat_20: bool
    raw_roll: int
    second_roll: int | None
    total_attack_roll: int
    target_ac: int
    damage_rolls: list[int]    # individual die results
    damage_total: int          # after crit doubling, before resistances
    damage_type: str
    had_advantage: bool
    had_disadvantage: bool
    events: list[str] = field(default_factory=list)


def resolve_attack(
    attacker: "CombatantState",
    target: "CombatantState",
    attack: "WeaponAttack",
    dice: "Dice",
) -> AttackResult:
    """Resolve a single weapon attack from *attacker* against *target*.

    Returns an AttackResult with hit/miss/crit and damage rolled.
    Damage is NOT yet applied to the target; call damage.apply_damage() next.
    """
    from balance_framework.engine.combat.conditions import (
        get_attack_modifiers,
        target_crits_within_5ft,
    )

    # Compute advantage/disadvantage from conditions
    cond_adv, cond_dis = get_attack_modifiers(attacker, target, attack.is_ranged)
    adv = (attack.advantage or cond_adv) and not (attack.disadvantage or cond_dis)
    dis = (attack.disadvantage or cond_dis) and not (attack.advantage or cond_adv)
    # Both cancel → normal
    if (attack.advantage or cond_adv) and (attack.disadvantage or cond_dis):
        adv = dis = False

    # d20 roll
    if adv:
        kept, other = dice.d20_advantage()
    elif dis:
        kept, other = dice.d20_disadvantage()
    else:
        kept, other = dice.d20_normal()

    nat_1 = kept == 1
    nat_20 = kept == 20

    # Crit threshold (Champion can lower to 19)
    crit_threshold = attacker.crit_threshold
    # Paralyzed / unconscious target: any hit within 5 ft is a crit
    force_crit = not attack.is_ranged and target_crits_within_5ft(target)

    total_roll = kept + attack.attack_bonus
    hits = nat_20 or (not nat_1 and total_roll >= target.ac)
    is_crit = nat_20 or (kept >= crit_threshold) or (hits and force_crit)

    events: list[str] = []
    damage_rolls: list[int] = []
    damage_total = 0

    if hits:
        # Roll damage
        for count, sides in attack.damage_dice:
            rolls = dice.roll(sides, count)
            damage_rolls.extend(rolls)
            damage_total += sum(rolls)
            if is_crit:
                extra = dice.roll(sides, count)
                damage_rolls.extend(extra)
                damage_total += sum(extra)

        # Crit extra dice (e.g. Savage Attacker, Brutal Crit)
        if is_crit:
            for count, sides in attack.crit_extra_dice:
                extra = dice.roll(sides, count)
                damage_rolls.extend(extra)
                damage_total += sum(extra)

        damage_total += attack.damage_bonus

        kind = "CRIT" if is_crit else "HIT"
        events.append(
            f"{attacker.display_name} → {target.display_name}: "
            f"roll {kept}+{attack.attack_bonus}={total_roll} vs AC {target.ac} "
            f"→ {kind} → {damage_total} {attack.damage_type}"
        )
    else:
        reason = "NAT 1" if nat_1 else f"roll {total_roll} vs AC {target.ac}"
        events.append(
            f"{attacker.display_name} → {target.display_name}: "
            f"roll {kept}+{attack.attack_bonus}={total_roll} → MISS ({reason})"
        )

    return AttackResult(
        hit=hits,
        crit=is_crit,
        nat_1=nat_1,
        nat_20=nat_20,
        raw_roll=kept,
        second_roll=other if (adv or dis) else None,
        total_attack_roll=total_roll,
        target_ac=target.ac,
        damage_rolls=damage_rolls,
        damage_total=max(damage_total, 0) if hits else 0,
        damage_type=attack.damage_type,
        had_advantage=adv,
        had_disadvantage=dis,
        events=events,
    )
