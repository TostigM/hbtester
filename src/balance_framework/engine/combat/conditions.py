"""D&D 5e 2024 condition definitions and helpers."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState

ALL_CONDITIONS: frozenset[str] = frozenset({
    "blinded", "charmed", "deafened", "exhaustion", "frightened",
    "grappled", "incapacitated", "invisible", "paralyzed", "petrified",
    "poisoned", "prone", "restrained", "stunned", "unconscious",
})

_INCAPACITATING: frozenset[str] = frozenset({
    "incapacitated", "paralyzed", "petrified", "stunned", "unconscious",
})
_AUTO_FAIL_STR_DEX: frozenset[str] = frozenset({
    "paralyzed", "petrified", "stunned", "unconscious",
})
_ADV_FOR_ATTACKERS: frozenset[str] = frozenset({
    "blinded", "paralyzed", "petrified", "restrained", "stunned", "unconscious",
})
_ADJACENT_AUTO_CRIT: frozenset[str] = frozenset({"paralyzed", "unconscious"})


def apply_condition(target: "CombatantState", condition: str, duration: int | None = None) -> bool:
    if condition not in ALL_CONDITIONS:
        raise ValueError(f"Unknown condition: {condition!r}")
    if condition in target.condition_immunities:
        return False
    target.conditions[condition] = duration
    return True


_SENTINEL = object()


def remove_condition(target: "CombatantState", condition: str) -> bool:
    return target.conditions.pop(condition, _SENTINEL) is not _SENTINEL


def tick_conditions(target: "CombatantState") -> list[str]:
    """Decrement timed conditions; return list of expired condition names."""
    expired: list[str] = []
    for cond, remaining in list(target.conditions.items()):
        if remaining is None:
            continue
        if remaining <= 1:
            del target.conditions[cond]
            expired.append(cond)
        else:
            target.conditions[cond] = remaining - 1
    return expired


def is_incapacitated(combatant: "CombatantState") -> bool:
    return bool(_INCAPACITATING & combatant.conditions.keys())


def auto_fails_str_dex(combatant: "CombatantState") -> bool:
    return bool(_AUTO_FAIL_STR_DEX & combatant.conditions.keys())


def get_attack_modifiers(
    attacker: "CombatantState",
    target: "CombatantState",
    is_ranged: bool = False,
) -> tuple[bool, bool]:
    """Return (has_advantage, has_disadvantage) from conditions on attacker/target."""
    adv = False
    dis = False

    for cond in ("blinded", "frightened", "poisoned", "restrained"):
        if cond in attacker.conditions:
            dis = True
    if "invisible" in attacker.conditions:
        adv = True

    if _ADV_FOR_ATTACKERS & attacker.conditions.keys():
        pass  # these apply to targets, not attacker
    if _ADV_FOR_ATTACKERS & target.conditions.keys():
        adv = True
    if "blinded" in target.conditions:
        adv = True
    if "invisible" in target.conditions:
        dis = True
    if "prone" in target.conditions:
        if is_ranged:
            dis = True
        else:
            adv = True

    return adv, dis


def target_crits_within_5ft(target: "CombatantState") -> bool:
    return bool(_ADJACENT_AUTO_CRIT & target.conditions.keys())
