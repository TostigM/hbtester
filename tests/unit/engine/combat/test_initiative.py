"""Unit tests for initiative rolling and ordering."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.initiative import (
    roll_initiative,
    roll_all_initiative,
    build_initiative_order,
)


def _c(id: str, dex_mod: int = 0) -> CombatantState:
    return CombatantState(
        id=id, display_name=id, team="party",
        hp_max=20, hp_current=20,
        ability_modifiers={"DEX": dex_mod},
    )


# ---------------------------------------------------------------------------
# roll_initiative
# ---------------------------------------------------------------------------

def test_roll_initiative_stores_on_combatant() -> None:
    c = _c("fighter", dex_mod=2)
    d = Dice(42)
    raw = roll_initiative(c, d)
    assert 1 <= raw <= 20
    assert c.initiative == raw + 2
    assert c.initiative_tiebreak == 2  # DEX mod


def test_roll_initiative_negative_dex() -> None:
    c = _c("goblin", dex_mod=-1)
    d = Dice(1)
    raw = roll_initiative(c, d)
    assert c.initiative == raw - 1


def test_roll_initiative_zero_dex() -> None:
    c = _c("brute", dex_mod=0)
    d = Dice(7)
    raw = roll_initiative(c, d)
    assert c.initiative == raw


# ---------------------------------------------------------------------------
# roll_all_initiative
# ---------------------------------------------------------------------------

def test_roll_all_initiative_sets_all() -> None:
    combatants = [_c("a", 2), _c("b", 0), _c("c", -1)]
    roll_all_initiative(combatants, Dice(0))
    for c in combatants:
        assert c.initiative != 0 or c.ability_modifiers["DEX"] <= 0


# ---------------------------------------------------------------------------
# build_initiative_order
# ---------------------------------------------------------------------------

def test_build_initiative_order_descending() -> None:
    a = _c("a")
    b = _c("b")
    c = _c("c")
    a.initiative = 15
    b.initiative = 20
    c.initiative = 10
    order = build_initiative_order([a, b, c])
    assert order[0].id == "b"
    assert order[1].id == "a"
    assert order[2].id == "c"


def test_build_initiative_order_tiebreak_by_dex() -> None:
    a = _c("low_dex", dex_mod=0)
    b = _c("high_dex", dex_mod=4)
    a.initiative = 12
    b.initiative = 12
    a.initiative_tiebreak = 0
    b.initiative_tiebreak = 4
    order = build_initiative_order([a, b])
    assert order[0].id == "high_dex"


def test_build_initiative_order_does_not_mutate_input() -> None:
    combatants = [_c("x"), _c("y")]
    combatants[0].initiative = 5
    combatants[1].initiative = 10
    original_order = list(combatants)
    build_initiative_order(combatants)
    assert combatants == original_order
