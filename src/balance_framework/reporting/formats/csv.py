"""CSV export for encounter results."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.runner.collector import EncounterResult


def write_encounter_csv(results: "list[EncounterResult]", path: Path) -> None:
    """Write one row per encounter to *path*.

    Columns: seed, winner_team, rounds, timed_out, then per-team win/hp columns
    for every team found across all encounters.
    """
    if not results:
        raise ValueError("Cannot write CSV from empty results list")

    teams: list[str] = sorted({c.team for r in results for c in r.combatants})
    path.parent.mkdir(parents=True, exist_ok=True)

    base_fields = ["seed", "winner_team", "rounds", "timed_out"]
    team_fields = [f"{t}_win" for t in teams] + [f"{t}_hp_fraction" for t in teams]

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=base_fields + team_fields)
        writer.writeheader()
        for r in results:
            row: dict = {
                "seed": r.seed,
                "winner_team": r.winner_team or "",
                "rounds": r.rounds,
                "timed_out": int(r.timed_out),
            }
            for t in teams:
                row[f"{t}_win"] = int(r.winner_team == t)
                row[f"{t}_hp_fraction"] = round(r.hp_fraction(t), 4)
            writer.writerow(row)


def write_combatant_csv(results: "list[EncounterResult]", path: Path) -> None:
    """Write one row per combatant per encounter to *path*.

    Columns: seed, winner_team, rounds, combatant_id, display_name, team,
             hp_final, hp_max, is_alive, damage_dealt, kills, healing_done.
    """
    if not results:
        raise ValueError("Cannot write CSV from empty results list")

    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "seed", "winner_team", "rounds",
        "combatant_id", "display_name", "team",
        "hp_final", "hp_max", "is_alive",
        "damage_dealt", "kills", "healing_done",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for r in results:
            for c in r.combatants:
                writer.writerow({
                    "seed": r.seed,
                    "winner_team": r.winner_team or "",
                    "rounds": r.rounds,
                    "combatant_id": c.id,
                    "display_name": c.display_name,
                    "team": c.team,
                    "hp_final": c.hp_final,
                    "hp_max": c.hp_max,
                    "is_alive": int(c.is_alive),
                    "damage_dealt": c.damage_dealt,
                    "kills": c.kills,
                    "healing_done": c.healing_done,
                })
