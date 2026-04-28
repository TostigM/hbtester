"""Deterministic seed generation for reproducible encounter batches."""

from __future__ import annotations


def seed_range(base: int, n: int) -> list[int]:
    """Return a list of *n* deterministic seeds derived from *base*.

    Seeds are simply ``base + i`` for i in 0..n-1.  The base seed acts as a
    campaign identifier so two different test suites with the same n never
    share seeds accidentally when using different bases.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    return [base + i for i in range(n)]
