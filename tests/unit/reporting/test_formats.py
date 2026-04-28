"""Unit tests for reporting format modules (markdown, CSV, JSON) and visualizations."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from balance_framework.runner.collector import EncounterResult, CombatantResult
from balance_framework.reporting.test_report import summarize
from balance_framework.reporting.formats.markdown import format_suite_markdown
from balance_framework.reporting.formats.csv import write_encounter_csv, write_combatant_csv
from balance_framework.reporting.formats.json import write_results, read_results, write_suite
from balance_framework.reporting.visualizations import (
    ascii_histogram, rounds_histogram, hp_fraction_histogram, damage_histogram,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _cr(id: str, team: str, hp: int = 20, hp_max: int = 30,
        alive: bool = True, dmg: int = 5, kills: int = 0) -> CombatantResult:
    return CombatantResult(id, id, team, hp, hp_max, alive, False,
                           damage_dealt=dmg, kills=kills, healing_done=0)


def _result(winner: str, rounds: int = 3, seed: int = 0) -> EncounterResult:
    return EncounterResult(
        seed=seed, winner_team=winner, rounds=rounds, timed_out=False,
        combatants=[
            _cr("hero", "party", hp=20, dmg=12, kills=1),
            _cr("goblin", "enemies", hp=0, alive=False, dmg=3),
        ],
    )


def _batch(n: int = 10) -> list[EncounterResult]:
    return [_result("party", rounds=3 + i % 3, seed=i) for i in range(n)]


# ---------------------------------------------------------------------------
# Markdown format
# ---------------------------------------------------------------------------

def test_markdown_contains_title() -> None:
    suite = summarize(_batch())
    md = format_suite_markdown(suite, "My Report")
    assert "My Report" in md


def test_markdown_contains_team_names() -> None:
    suite = summarize(_batch())
    md = format_suite_markdown(suite)
    assert "party" in md
    assert "enemies" in md


def test_markdown_contains_win_rate() -> None:
    suite = summarize(_batch())
    md = format_suite_markdown(suite)
    assert "100.0%" in md  # all party wins


def test_markdown_is_well_formed_table() -> None:
    suite = summarize(_batch())
    md = format_suite_markdown(suite)
    table_lines = [l for l in md.splitlines() if l.startswith("|")]
    assert len(table_lines) >= 3  # header + separator + at least one row


# ---------------------------------------------------------------------------
# CSV — encounter-level
# ---------------------------------------------------------------------------

def test_csv_encounter_creates_file(tmp_path: Path) -> None:
    path = tmp_path / "enc.csv"
    write_encounter_csv(_batch(), path)
    assert path.exists()


def test_csv_encounter_row_count(tmp_path: Path) -> None:
    results = _batch(n=5)
    path = tmp_path / "enc.csv"
    write_encounter_csv(results, path)
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 5


def test_csv_encounter_has_expected_columns(tmp_path: Path) -> None:
    path = tmp_path / "enc.csv"
    write_encounter_csv(_batch(), path)
    reader = csv.DictReader(path.open(encoding="utf-8"))
    assert "seed" in reader.fieldnames
    assert "winner_team" in reader.fieldnames
    assert "rounds" in reader.fieldnames
    assert "party_win" in reader.fieldnames


def test_csv_encounter_winner_column(tmp_path: Path) -> None:
    path = tmp_path / "enc.csv"
    write_encounter_csv([_result("party", seed=0)], path)
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows[0]["winner_team"] == "party"
    assert rows[0]["party_win"] == "1"


def test_csv_encounter_creates_parent_dirs(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "dir" / "enc.csv"
    write_encounter_csv(_batch(1), path)
    assert path.exists()


# ---------------------------------------------------------------------------
# CSV — combatant-level
# ---------------------------------------------------------------------------

def test_csv_combatant_row_count(tmp_path: Path) -> None:
    results = _batch(n=3)  # 3 encounters × 2 combatants each
    path = tmp_path / "cbt.csv"
    write_combatant_csv(results, path)
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 6


def test_csv_combatant_damage_column(tmp_path: Path) -> None:
    path = tmp_path / "cbt.csv"
    write_combatant_csv([_result("party")], path)
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    hero_row = next(r for r in rows if r["combatant_id"] == "hero")
    assert int(hero_row["damage_dealt"]) == 12
    assert int(hero_row["kills"]) == 1


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------

def test_json_write_creates_valid_file(tmp_path: Path) -> None:
    path = tmp_path / "results.json"
    write_results(_batch(), path)
    data = json.loads(path.read_text())
    assert isinstance(data, list)
    assert len(data) == 10


def test_json_read_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "r.json"
    write_results(_batch(5), path)
    loaded = read_results(path)
    assert len(loaded) == 5
    assert loaded[0]["winner_team"] == "party"


def test_json_read_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_results(tmp_path / "nope.json")


def test_json_write_suite(tmp_path: Path) -> None:
    suite = summarize(_batch())
    path = tmp_path / "suite.json"
    write_suite(suite, path)
    data = json.loads(path.read_text())
    assert data["n"] == 10
    assert "party" in data["teams"]


def test_json_empty_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        write_results([], tmp_path / "x.json")


# ---------------------------------------------------------------------------
# ASCII visualizations
# ---------------------------------------------------------------------------

def test_ascii_histogram_returns_string() -> None:
    result = ascii_histogram([1, 2, 3, 4, 5], title="Test")
    assert isinstance(result, str)
    assert "Test" in result


def test_ascii_histogram_empty_data() -> None:
    result = ascii_histogram([], title="Empty")
    assert "no data" in result.lower() or "Empty" in result


def test_ascii_histogram_uniform_values() -> None:
    result = ascii_histogram([3, 3, 3, 3], title="Uniform")
    assert "3" in result


def test_ascii_histogram_bin_count() -> None:
    result = ascii_histogram(list(range(20)), bins=5)
    # Should have 5 rows of data
    data_lines = [l for l in result.splitlines() if "#" in l or l.strip().startswith("-")]
    assert len(data_lines) >= 4  # at least most bins populated


def test_rounds_histogram_uses_result_data() -> None:
    results = _batch(n=20)
    suite = summarize(results)
    text = rounds_histogram(suite, results)
    assert "20" in text  # n=20 in title


def test_hp_fraction_histogram() -> None:
    results = _batch(n=10)
    text = hp_fraction_histogram(results, "party")
    assert "party" in text


def test_damage_histogram() -> None:
    results = _batch(n=10)
    text = damage_histogram(results, "hero")
    assert "hero" in text
