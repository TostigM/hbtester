"""Deterministic dice rolling backed by a seeded numpy RNG.

All randomness in the engine flows through a single Dice instance per scenario.
Passing the same seed to Dice always produces the same sequence of rolls.
"""

from __future__ import annotations

import re

import numpy as np


class Dice:
    """Seeded dice roller.  A single instance should be passed through an entire
    combat scenario to guarantee determinism.
    """

    def __init__(self, seed: int) -> None:
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Core primitives
    # ------------------------------------------------------------------

    def roll(self, sides: int, count: int = 1) -> list[int]:
        """Roll *count* dice with *sides* faces. Returns individual results."""
        if sides < 1:
            raise ValueError(f"sides must be >= 1, got {sides}")
        if count < 1:
            raise ValueError(f"count must be >= 1, got {count}")
        return [int(x) for x in self._rng.integers(1, sides + 1, size=count)]

    def roll_sum(self, sides: int, count: int = 1) -> int:
        """Roll *count* dice and return their sum."""
        return sum(self.roll(sides, count))

    # ------------------------------------------------------------------
    # d20 convenience helpers
    # ------------------------------------------------------------------

    def d20(self) -> int:
        return self.roll_sum(20)

    def d20_advantage(self) -> tuple[int, int]:
        """Roll two d20s; return (kept, discarded) where kept is the higher."""
        a, b = self.d20(), self.d20()
        return (max(a, b), min(a, b))

    def d20_disadvantage(self) -> tuple[int, int]:
        """Roll two d20s; return (kept, discarded) where kept is the lower."""
        a, b = self.d20(), self.d20()
        return (min(a, b), max(a, b))

    def d20_normal(self) -> tuple[int, int]:
        """Roll one d20; return (result, 0) for consistent API."""
        return (self.d20(), 0)

    # ------------------------------------------------------------------
    # Formula parser
    # ------------------------------------------------------------------

    _FORMULA_RE = re.compile(
        r"^(?:(\d+)d(\d+))?"   # optional XdY
        r"(?:([+-]\d+))*$",    # optional +N / -N modifiers
        re.IGNORECASE,
    )

    def roll_formula(self, formula: str) -> int:
        """Roll a dice formula like ``2d6+3``, ``1d8``, ``5``, or ``d20``.

        Raises ValueError if the formula cannot be parsed.
        """
        formula = formula.strip().replace(" ", "")
        # Normalise a leading 'd' (e.g. 'd6' → '1d6')
        if formula.startswith("d"):
            formula = "1" + formula

        total = 0
        # Extract all terms: e.g. "2d6+3-1" → ["2d6", "+3", "-1"]
        tokens = re.findall(r"[+-]?(?:\d+d\d+|\d+)", formula, re.IGNORECASE)
        if not tokens:
            raise ValueError(f"Cannot parse dice formula: {formula!r}")

        for token in tokens:
            sign = -1 if token.startswith("-") else 1
            token = token.lstrip("+-")
            if "d" in token.lower():
                parts = token.lower().split("d")
                count, sides = int(parts[0]), int(parts[1])
                total += sign * self.roll_sum(sides, count)
            else:
                total += sign * int(token)
        return total
