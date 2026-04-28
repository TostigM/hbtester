"""Unit tests for seed generation."""

from __future__ import annotations

import pytest

from balance_framework.runner.seeding import seed_range


def test_seed_range_length() -> None:
    assert len(seed_range(0, 10)) == 10


def test_seed_range_values() -> None:
    assert seed_range(42, 5) == [42, 43, 44, 45, 46]


def test_seed_range_base_zero() -> None:
    assert seed_range(0, 3) == [0, 1, 2]


def test_seed_range_n_one() -> None:
    assert seed_range(7, 1) == [7]


def test_seed_range_no_overlap_different_bases() -> None:
    a = set(seed_range(0, 100))
    b = set(seed_range(1000, 100))
    assert a.isdisjoint(b)


def test_seed_range_invalid_n() -> None:
    with pytest.raises(ValueError):
        seed_range(0, 0)
