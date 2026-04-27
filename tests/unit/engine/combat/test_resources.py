"""Unit tests for resource pool management."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.combat.resources import (
    InsufficientResourceError,
    spend,
    recover,
    restore_pool,
    restore_all_pools,
    current,
    has_resource,
)


def _c(pools: dict[str, int] | None = None) -> CombatantState:
    c = CombatantState(
        id="c", display_name="C", team="party",
        hp_max=20, hp_current=20,
        resources=dict(pools or {}),
    )
    return c


# ---------------------------------------------------------------------------
# spend
# ---------------------------------------------------------------------------

def test_spend_decrements_pool() -> None:
    c = _c({"second_wind": 1})
    remaining = spend(c, "second_wind")
    assert remaining == 0
    assert c.resources["second_wind"] == 0


def test_spend_multiple() -> None:
    c = _c({"spell_slot_1": 4})
    remaining = spend(c, "spell_slot_1", 2)
    assert remaining == 2


def test_spend_insufficient_raises() -> None:
    c = _c({"action_surge": 0})
    with pytest.raises(InsufficientResourceError):
        spend(c, "action_surge")


def test_spend_missing_pool_raises() -> None:
    c = _c()
    with pytest.raises(KeyError):
        spend(c, "superiority_dice")


# ---------------------------------------------------------------------------
# recover
# ---------------------------------------------------------------------------

def test_recover_adds_charges() -> None:
    c = _c({"superiority_dice": 2})
    new_val = recover(c, "superiority_dice", 2, cap=4)
    assert new_val == 4


def test_recover_capped_at_cap() -> None:
    c = _c({"superiority_dice": 3})
    new_val = recover(c, "superiority_dice", 5, cap=4)
    assert new_val == 4


def test_recover_missing_pool_raises() -> None:
    c = _c()
    with pytest.raises(KeyError):
        recover(c, "no_pool", 1, cap=3)


# ---------------------------------------------------------------------------
# restore_pool
# ---------------------------------------------------------------------------

def test_restore_pool_sets_to_cap() -> None:
    c = _c({"spell_slot_3": 0})
    restore_pool(c, "spell_slot_3", cap=2)
    assert c.resources["spell_slot_3"] == 2


# ---------------------------------------------------------------------------
# restore_all_pools
# ---------------------------------------------------------------------------

def test_restore_all_pools_long_rest() -> None:
    c = _c({"spell_slot_1": 0, "spell_slot_2": 1, "second_wind": 0})
    restore_all_pools(c, {"spell_slot_1": 4, "spell_slot_2": 3, "second_wind": 1})
    assert c.resources["spell_slot_1"] == 4
    assert c.resources["spell_slot_2"] == 3
    assert c.resources["second_wind"] == 1


# ---------------------------------------------------------------------------
# current / has_resource
# ---------------------------------------------------------------------------

def test_current_returns_value() -> None:
    c = _c({"action_surge": 1})
    assert current(c, "action_surge") == 1


def test_current_returns_zero_for_missing() -> None:
    c = _c()
    assert current(c, "nonexistent") == 0


def test_has_resource_true_when_sufficient() -> None:
    c = _c({"second_wind": 1})
    assert has_resource(c, "second_wind")


def test_has_resource_false_when_empty() -> None:
    c = _c({"action_surge": 0})
    assert not has_resource(c, "action_surge")


def test_has_resource_false_for_missing_pool() -> None:
    c = _c()
    assert not has_resource(c, "channel_divinity")
