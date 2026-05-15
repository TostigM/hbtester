"""M7 integration tests — report generation from a full encounter batch.

Uses the same party/goblin setup as M5 sanity checks but drives the reporting
and export pipeline end-to-end.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.ai.decision import select_actions
from balance_framework.ai.profiles import CLASS_PROFILE
from balance_framework.registry.loader import load_content_directory
from balance_framework.registry.registry import ContentRegistry
from balance_framework.registry.character_builder import CharacterBuild, build_character
from balance_framework.runner.orchestrator import run_encounter_batch
from balance_framework.runner.collector import EncounterResult
from balance_framework.reporting.test_report import summarize, format_report
from balance_framework.reporting.formats.markdown import format_suite_markdown
from balance_framework.reporting.formats.csv import write_encounter_csv, write_combatant_csv
from balance_framework.reporting.formats.json import write_results, read_results, write_suite
from balance_framework.reporting.visualizations import (
    rounds_histogram, hp_fraction_histogram, damage_histogram,
)
from balance_framework.logging.event_log import AttackEvent, HealEvent, DeathEvent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def registry() -> ContentRegistry:
    return ContentRegistry(load_content_directory(Path("content")))


_GARRICK_BUILD = CharacterBuild(
    species_id="human", class_id="fighter", subclass_id="battle_master",
    background_id="soldier", level=5,
    ability_scores={"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8},
    feat_ids=["tough", "savage_attacker"],
    armor_type="chain_mail", has_shield=True, selected_fighting_style="defense",
)


def _goblin(id: str) -> CombatantState:
    return CombatantState(
        id=id, display_name=f"Goblin {id}",
        team="enemies", hp_max=7, hp_current=7, ac=15,
        proficiency_bonus=2,
        ability_modifiers={"STR": -1, "DEX": 2, "CON": 0},
        extra_attack_count=1, behavior_profile="monster_melee",
    )


@pytest.fixture(scope="module")
def batch_results(registry: ContentRegistry) -> list[EncounterResult]:
    def factory(seed: int) -> ScenarioState:
        char = build_character(_GARRICK_BUILD, registry)
        cs = CombatantState.from_character(char, "garrick", "Garrick", "party", "martial")
        goblins = [_goblin(f"g{i}") for i in range(2)]
        return ScenarioState(combatants=[cs] + goblins, dice=Dice(seed))

    return run_encounter_batch(factory, select_actions, n=30, base_seed=0)


# ---------------------------------------------------------------------------
# Structured events
# ---------------------------------------------------------------------------

def test_structured_events_populated(registry: ContentRegistry) -> None:
    """At least some attack events should be recorded per encounter."""
    def factory(seed: int) -> ScenarioState:
        char = build_character(_GARRICK_BUILD, registry)
        cs = CombatantState.from_character(char, "garrick", "Garrick", "party", "martial")
        return ScenarioState(combatants=[cs, _goblin("g0")], dice=Dice(seed))

    # Run one encounter and inspect structured events
    scenario = factory(42)
    from balance_framework.engine.resolver import run_combat
    run_combat(scenario, select_actions)
    attack_events = [e for e in scenario.structured_events if isinstance(e, AttackEvent)]
    assert len(attack_events) > 0


def test_death_events_match_kills(registry: ContentRegistry) -> None:
    """Every kill should have a corresponding DeathEvent in structured_events."""
    def factory(seed: int) -> ScenarioState:
        char = build_character(_GARRICK_BUILD, registry)
        cs = CombatantState.from_character(char, "garrick", "Garrick", "party", "martial")
        return ScenarioState(combatants=[cs, _goblin("g0")], dice=Dice(seed))

    from balance_framework.engine.resolver import run_combat
    scenario = factory(0)
    run_combat(scenario, select_actions)
    deaths = [e for e in scenario.structured_events if isinstance(e, DeathEvent)]
    kills = scenario.kills.get("garrick", 0)
    assert len(deaths) >= kills  # could be more deaths (unconscious then killed on save fails)


# ---------------------------------------------------------------------------
# Markdown export
# ---------------------------------------------------------------------------

def test_markdown_report_not_empty(batch_results: list[EncounterResult]) -> None:
    suite = summarize(batch_results)
    md = format_suite_markdown(suite, "Garrick Solo vs 2 Goblins")
    assert len(md) > 100
    assert "Garrick Solo vs 2 Goblins" in md


def test_markdown_report_has_tables(batch_results: list[EncounterResult]) -> None:
    suite = summarize(batch_results)
    md = format_suite_markdown(suite)
    table_lines = [l for l in md.splitlines() if l.startswith("|")]
    assert len(table_lines) >= 4


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def test_csv_encounter_export(
    batch_results: list[EncounterResult], tmp_path: Path
) -> None:
    path = tmp_path / "encounters.csv"
    write_encounter_csv(batch_results, path)
    import csv as csv_mod
    rows = list(csv_mod.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 30


def test_csv_combatant_export(
    batch_results: list[EncounterResult], tmp_path: Path
) -> None:
    path = tmp_path / "combatants.csv"
    write_combatant_csv(batch_results, path)
    import csv as csv_mod
    rows = list(csv_mod.DictReader(path.open(encoding="utf-8")))
    # 30 encounters × 3 combatants each (garrick + 2 goblins)
    assert len(rows) == 90


def test_csv_garrick_damage_nonzero(
    batch_results: list[EncounterResult], tmp_path: Path
) -> None:
    path = tmp_path / "combatants.csv"
    write_combatant_csv(batch_results, path)
    import csv as csv_mod
    rows = list(csv_mod.DictReader(path.open(encoding="utf-8")))
    garrick_rows = [r for r in rows if r["combatant_id"] == "garrick"]
    total_dmg = sum(int(r["damage_dealt"]) for r in garrick_rows)
    assert total_dmg > 0


# ---------------------------------------------------------------------------
# JSON export / roundtrip
# ---------------------------------------------------------------------------

def test_json_results_roundtrip(
    batch_results: list[EncounterResult], tmp_path: Path
) -> None:
    path = tmp_path / "results.json"
    write_results(batch_results, path)
    loaded = read_results(path)
    assert len(loaded) == 30
    assert loaded[0]["winner_team"] in ("party", "enemies", "")


def test_json_suite_export(
    batch_results: list[EncounterResult], tmp_path: Path
) -> None:
    suite = summarize(batch_results)
    path = tmp_path / "suite.json"
    write_suite(suite, path)
    data = json.loads(path.read_text())
    assert data["n"] == 30
    assert "party" in data["teams"]
    assert 0.0 <= data["teams"]["party"]["win_rate"] <= 1.0


# ---------------------------------------------------------------------------
# Visualizations
# ---------------------------------------------------------------------------

def test_rounds_histogram_output(batch_results: list[EncounterResult]) -> None:
    suite = summarize(batch_results)
    text = rounds_histogram(suite, batch_results)
    assert len(text) > 20
    assert "#" in text


def test_hp_fraction_histogram_output(batch_results: list[EncounterResult]) -> None:
    text = hp_fraction_histogram(batch_results, "party")
    assert "party" in text


def test_damage_histogram_output(batch_results: list[EncounterResult]) -> None:
    text = damage_histogram(batch_results, "garrick")
    assert "garrick" in text
