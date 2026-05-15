"""Baseline save/load and regression detection."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.reporting.test_report import EncounterSuite


@dataclass
class BaselineEntry:
    """A snapshot of one team's key metrics, saved as a regression reference."""
    team: str
    win_rate: float
    avg_rounds: float


@dataclass
class RegressionFlag:
    """Describes one detected regression vs. a saved baseline."""
    metric: str
    baseline_value: float
    current_value: float
    delta: float
    threshold: float

    def __str__(self) -> str:
        return (
            f"{self.metric}: {self.baseline_value:.3f} → {self.current_value:.3f} "
            f"(delta {self.delta:+.3f}, threshold ±{self.threshold:.3f})"
        )


def save_baseline(suite: "EncounterSuite", path: Path) -> None:
    """Save a minimal baseline from *suite* to a JSON file."""
    data = {
        "n": suite.n,
        "avg_rounds": suite.avg_rounds,
        "teams": {
            team: {"win_rate": ts.win_rate, "avg_hp_fraction": ts.avg_hp_fraction}
            for team, ts in suite.teams.items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_baseline(path: Path) -> dict:
    """Load a previously saved baseline dict from *path*."""
    if not path.exists():
        raise FileNotFoundError(f"Baseline not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def diff_baseline(
    suite: "EncounterSuite",
    baseline: dict,
    win_rate_threshold: float = 0.10,
    hp_threshold: float = 0.10,
    rounds_threshold: float = 1.0,
) -> list[RegressionFlag]:
    """Compare *suite* against a *baseline* dict; return any regressions.

    A regression is flagged when the delta exceeds the threshold.
    """
    flags: list[RegressionFlag] = []

    # Rounds
    base_rounds = baseline.get("avg_rounds", suite.avg_rounds)
    delta_rounds = abs(suite.avg_rounds - base_rounds)
    if delta_rounds > rounds_threshold:
        flags.append(RegressionFlag(
            metric="avg_rounds",
            baseline_value=base_rounds,
            current_value=suite.avg_rounds,
            delta=suite.avg_rounds - base_rounds,
            threshold=rounds_threshold,
        ))

    # Per-team metrics
    base_teams = baseline.get("teams", {})
    for team, ts in suite.teams.items():
        bt = base_teams.get(team, {})

        base_wr = bt.get("win_rate", ts.win_rate)
        delta_wr = abs(ts.win_rate - base_wr)
        if delta_wr > win_rate_threshold:
            flags.append(RegressionFlag(
                metric=f"{team}.win_rate",
                baseline_value=base_wr,
                current_value=ts.win_rate,
                delta=ts.win_rate - base_wr,
                threshold=win_rate_threshold,
            ))

        base_hp = bt.get("avg_hp_fraction", ts.avg_hp_fraction)
        delta_hp = abs(ts.avg_hp_fraction - base_hp)
        if delta_hp > hp_threshold:
            flags.append(RegressionFlag(
                metric=f"{team}.avg_hp_fraction",
                baseline_value=base_hp,
                current_value=ts.avg_hp_fraction,
                delta=ts.avg_hp_fraction - base_hp,
                threshold=hp_threshold,
            ))

    return flags
