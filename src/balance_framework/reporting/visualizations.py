"""ASCII terminal visualizations for encounter suite data."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.reporting.test_report import EncounterSuite
    from balance_framework.runner.collector import EncounterResult


def ascii_histogram(
    values: list[float | int],
    title: str = "",
    width: int = 40,
    bins: int = 10,
) -> str:
    """Return a multi-line ASCII histogram of *values*.

    Each bin is rendered as a horizontal bar scaled to *width* characters.
    """
    if not values:
        return f"{title}\n(no data)"

    lo, hi = min(values), max(values)
    if lo == hi:
        # All values identical — single bin
        bar = "#" * width
        label = f"{lo:.1f}"
        return "\n".join(filter(None, [title, f"  {label:>6}  {bar}  ({len(values)})"]))

    bin_size = (hi - lo) / bins
    counts = [0] * bins
    for v in values:
        idx = min(int((v - lo) / bin_size), bins - 1)
        counts[idx] += 1

    max_count = max(counts)
    lines: list[str] = []
    if title:
        lines.append(title)
    for i, count in enumerate(counts):
        bin_lo = lo + i * bin_size
        bin_hi = bin_lo + bin_size
        bar_len = int(count / max_count * width) if max_count else 0
        bar = "#" * bar_len
        lines.append(f"  {bin_lo:5.1f}-{bin_hi:5.1f}  {bar:<{width}}  ({count})")
    return "\n".join(lines)


def rounds_histogram(suite: "EncounterSuite", results: "list[EncounterResult]") -> str:
    """Histogram of round counts across all encounters in *results*."""
    rounds = [r.rounds for r in results]
    return ascii_histogram(rounds, title=f"Round distribution (n={suite.n})", bins=8)


def hp_fraction_histogram(
    results: "list[EncounterResult]",
    team: str,
    title: str = "",
) -> str:
    """Histogram of final HP fraction for *team* across all encounters."""
    fracs = [r.hp_fraction(team) for r in results]
    return ascii_histogram(
        fracs,
        title=title or f"HP fraction — {team} (n={len(results)})",
        bins=10,
    )


def damage_histogram(
    results: "list[EncounterResult]",
    combatant_id: str,
    title: str = "",
) -> str:
    """Histogram of total damage dealt by *combatant_id* across encounters."""
    totals = [
        sum(c.damage_dealt for c in r.combatants if c.id == combatant_id)
        for r in results
    ]
    return ascii_histogram(
        totals,
        title=title or f"Damage dealt — {combatant_id} (n={len(results)})",
        bins=10,
    )
