"""JSON serialisation for encounter results and suites."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.runner.collector import EncounterResult
    from balance_framework.reporting.test_report import EncounterSuite


def write_results(results: "list[EncounterResult]", path: Path) -> None:
    """Serialise a list of EncounterResults to JSON at *path*."""
    if not results:
        raise ValueError("Cannot write JSON from empty results list")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(r) for r in results]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_results(path: Path) -> list[dict]:
    """Load a results JSON file.  Returns raw dicts (not dataclasses)."""
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_suite(suite: "EncounterSuite", path: Path) -> None:
    """Serialise an EncounterSuite to JSON at *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "n": suite.n,
        "timed_out": suite.timed_out,
        "avg_rounds": suite.avg_rounds,
        "std_rounds": suite.std_rounds,
        "teams": {
            team: {
                "win_rate": ts.win_rate,
                "avg_survivors": ts.avg_survivors,
                "avg_hp_fraction": ts.avg_hp_fraction,
            }
            for team, ts in suite.teams.items()
        },
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
