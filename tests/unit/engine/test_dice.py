"""Tests for the Dice class."""

from __future__ import annotations

import pytest

from balance_framework.engine.dice import Dice


def test_determinism_same_seed() -> None:
    d1 = Dice(42)
    d2 = Dice(42)
    rolls1 = [d1.roll_sum(20) for _ in range(10)]
    rolls2 = [d2.roll_sum(20) for _ in range(10)]
    assert rolls1 == rolls2


def test_different_seeds_differ() -> None:
    d1 = Dice(1)
    d2 = Dice(2)
    rolls1 = [d1.roll_sum(20) for _ in range(20)]
    rolls2 = [d2.roll_sum(20) for _ in range(20)]
    assert rolls1 != rolls2


def test_roll_bounds() -> None:
    d = Dice(0)
    for _ in range(100):
        r = d.roll_sum(6)
        assert 1 <= r <= 6


def test_roll_count() -> None:
    d = Dice(0)
    results = d.roll(6, count=4)
    assert len(results) == 4
    assert all(1 <= r <= 6 for r in results)


def test_d20_bounds() -> None:
    d = Dice(99)
    for _ in range(100):
        r = d.d20()
        assert 1 <= r <= 20


def test_advantage_returns_higher() -> None:
    d = Dice(7)
    for _ in range(50):
        kept, discarded = d.d20_advantage()
        assert kept >= discarded


def test_disadvantage_returns_lower() -> None:
    d = Dice(7)
    for _ in range(50):
        kept, discarded = d.d20_disadvantage()
        assert kept <= discarded


def test_normal_second_is_zero() -> None:
    d = Dice(0)
    kept, other = d.d20_normal()
    assert other == 0
    assert 1 <= kept <= 20


@pytest.mark.parametrize("formula,expected_min,expected_max", [
    ("1d6", 1, 6),
    ("2d6", 2, 12),
    ("1d8+3", 4, 11),
    ("2d6+2", 4, 14),
    ("d20", 1, 20),
    ("5", 5, 5),
    ("1d6-1", 0, 5),
])
def test_roll_formula(formula: str, expected_min: int, expected_max: int) -> None:
    d = Dice(0)
    for _ in range(50):
        r = d.roll_formula(formula)
        assert expected_min <= r <= expected_max, f"Formula {formula!r} gave {r}"


def test_roll_formula_invalid() -> None:
    d = Dice(0)
    with pytest.raises(ValueError):
        d.roll_formula("???")


def test_roll_invalid_sides() -> None:
    d = Dice(0)
    with pytest.raises(ValueError):
        d.roll(0)


def test_roll_invalid_count() -> None:
    d = Dice(0)
    with pytest.raises(ValueError):
        d.roll(6, count=0)
