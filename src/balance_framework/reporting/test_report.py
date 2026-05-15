"""Aggregate encounter results into a human-readable test report."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from balance_framework.runner.collector import EncounterResult


@dataclass
class TeamStats:
    """Per-team aggregated statistics across an encounter batch."""
    team: str
    win_rate: float          # fraction of encounters won
    avg_survivors: float     # average living members at end
    avg_hp_fraction: float   # average HP fraction of survivors


@dataclass
class EncounterSuite:
    """Aggregated statistics for a batch of encounters."""
    n: int                          # total encounters run
    timed_out: int                  # encounters that hit max_rounds
    avg_rounds: float
    std_rounds: float
    teams: dict[str, TeamStats] = field(default_factory=dict)

    def win_rate(self, team: str) -> float:
        return self.teams[team].win_rate if team in self.teams else 0.0


def summarize(results: list[EncounterResult]) -> EncounterSuite:
    """Compute aggregate statistics from a list of EncounterResults."""
    if not results:
        raise ValueError("Cannot summarize an empty result list")

    n = len(results)
    timed_out = sum(1 for r in results if r.timed_out)

    rounds = [r.rounds for r in results]
    avg_rounds = sum(rounds) / n
    variance = sum((r - avg_rounds) ** 2 for r in rounds) / n
    std_rounds = math.sqrt(variance)

    # Collect all team names
    teams: set[str] = set()
    for r in results:
        for c in r.combatants:
            teams.add(c.team)

    team_stats: dict[str, TeamStats] = {}
    for team in teams:
        wins = sum(1 for r in results if r.winner_team == team)
        total_survivors = sum(len(r.survivors(team)) for r in results)
        total_hp_frac = sum(r.hp_fraction(team) for r in results)

        team_stats[team] = TeamStats(
            team=team,
            win_rate=wins / n,
            avg_survivors=total_survivors / n,
            avg_hp_fraction=total_hp_frac / n,
        )

    return EncounterSuite(
        n=n,
        timed_out=timed_out,
        avg_rounds=avg_rounds,
        std_rounds=std_rounds,
        teams=team_stats,
    )


def format_report(suite: EncounterSuite, title: str = "Encounter Suite") -> str:
    """Return a human-readable text summary of the suite."""
    lines = [
        f"=== {title} ===",
        f"Encounters : {suite.n}",
        f"Timed out  : {suite.timed_out}",
        f"Avg rounds : {suite.avg_rounds:.1f} ± {suite.std_rounds:.1f}",
        "",
    ]
    for team, ts in sorted(suite.teams.items()):
        lines.append(f"[{team}]")
        lines.append(f"  Win rate      : {ts.win_rate * 100:.1f}%")
        lines.append(f"  Avg survivors : {ts.avg_survivors:.1f}")
        lines.append(f"  Avg HP frac   : {ts.avg_hp_fraction * 100:.1f}%")
    return "\n".join(lines)
