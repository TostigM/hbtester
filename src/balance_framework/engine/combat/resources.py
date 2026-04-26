"""Resource pool management (spell slots, superiority dice, Second Wind, etc.)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState


@dataclass
class ResourcePool:
    """Definition of a resource pool (separate from combat state)."""

    id: str
    display_name: str
    max_value: int
    refresh: str  # "short_or_long" | "long" | "short"


class InsufficientResourceError(Exception):
    """Raised when a resource spend would exceed available charges."""


def spend(combatant: "CombatantState", pool_id: str, amount: int = 1) -> int:
    """Spend *amount* from pool *pool_id*.  Returns remaining charges.

    Raises InsufficientResourceError if the pool has fewer than *amount* charges.
    Raises KeyError if the pool is not registered on this combatant.
    """
    if pool_id not in combatant.resources:
        raise KeyError(f"Combatant {combatant.id!r} has no resource pool {pool_id!r}")
    current = combatant.resources[pool_id]
    if current < amount:
        raise InsufficientResourceError(
            f"{combatant.id!r} needs {amount} {pool_id!r} but only has {current}"
        )
    combatant.resources[pool_id] = current - amount
    return combatant.resources[pool_id]


def recover(combatant: "CombatantState", pool_id: str, amount: int, cap: int) -> int:
    """Recover up to *amount* charges for *pool_id*, capped at *cap*.

    Returns the new current value.
    """
    if pool_id not in combatant.resources:
        raise KeyError(f"Combatant {combatant.id!r} has no resource pool {pool_id!r}")
    new_val = min(combatant.resources[pool_id] + amount, cap)
    combatant.resources[pool_id] = new_val
    return new_val


def restore_pool(combatant: "CombatantState", pool_id: str, cap: int) -> None:
    """Fully restore *pool_id* to *cap*."""
    combatant.resources[pool_id] = cap


def restore_all_pools(combatant: "CombatantState", pool_caps: dict[str, int]) -> None:
    """Restore every pool in *pool_caps* to its cap (long-rest recovery)."""
    for pool_id, cap in pool_caps.items():
        combatant.resources[pool_id] = cap


def current(combatant: "CombatantState", pool_id: str) -> int:
    """Return current charges in *pool_id*, or 0 if pool doesn't exist."""
    return combatant.resources.get(pool_id, 0)


def has_resource(combatant: "CombatantState", pool_id: str, amount: int = 1) -> bool:
    return combatant.resources.get(pool_id, 0) >= amount
