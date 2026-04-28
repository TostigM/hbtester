"""M5 sanity checks — the standard party must meet baseline performance thresholds.

These tests run the full four-member party at level 5 against a goblin band
(CR 1/4 x4) over 100 encounters and assert that the simulation is working
correctly at a statistical level.

Pass criteria (deliberately loose to avoid flakiness):
  - Party win rate >= 90%   (L5 party vs 4 CR1/4 goblins is a very easy encounter)
  - No encounter times out  (max_rounds=20 should be plenty)
  - Avg rounds in [1, 8]    (combat should not be trivially instant OR dragging on)
  - Outcomes vary across seeds (simulation is not degenerate)
"""

from __future__ import annotations

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
from balance_framework.reporting.test_report import summarize, format_report

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

GARRICK_BASE = dict(
    species_id="human", class_id="fighter", subclass_id="battle_master",
    background_id="soldier",
    ability_scores={"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8},
    feat_ids=["tough", "savage_attacker"],
    armor_type="chain_mail", has_shield=True, selected_fighting_style="defense",
)
ELOWYN_BASE = dict(
    species_id="human", class_id="cleric", subclass_id="life_domain",
    background_id="acolyte",
    ability_scores={"STR": 14, "DEX": 12, "CON": 15, "INT": 8, "WIS": 16, "CHA": 10},
    feat_ids=["healer", "magic_initiate_cleric"],
    armor_type="scale_mail", has_shield=True,
)
VARIAN_BASE = dict(
    species_id="human", class_id="wizard", subclass_id="evoker",
    background_id="sage",
    ability_scores={"STR": 8, "DEX": 14, "CON": 15, "INT": 16, "WIS": 12, "CHA": 10},
    feat_ids=["alert", "magic_initiate_wizard"],
    armor_type="none", uses_mage_armor=True,
)
MIRA_BASE = dict(
    species_id="human", class_id="rogue", subclass_id="thief",
    background_id="charlatan",
    ability_scores={"STR": 8, "DEX": 16, "CON": 15, "INT": 12, "WIS": 14, "CHA": 10},
    feat_ids=["alert", "skilled"],
    armor_type="studded_leather",
)

ALL_BUILDS = [
    ("garrick", "fighter", GARRICK_BASE),
    ("elowyn", "cleric", ELOWYN_BASE),
    ("varian", "wizard", VARIAN_BASE),
    ("mira", "rogue", MIRA_BASE),
]


@pytest.fixture(scope="module")
def registry() -> ContentRegistry:
    return ContentRegistry(load_content_directory(Path("content")))


def _goblin(id: str) -> CombatantState:
    return CombatantState(
        id=id, display_name=f"Goblin {id[-1]}",
        team="enemies",
        hp_max=7, hp_current=7, ac=15,
        proficiency_bonus=2,
        ability_modifiers={"STR": -1, "DEX": 2, "CON": 0},
        extra_attack_count=1,
        behavior_profile="monster_melee",
    )


def _make_factory(registry: ContentRegistry, level: int = 5, num_goblins: int = 4):
    def factory(seed: int) -> ScenarioState:
        party = []
        for name, class_id, base in ALL_BUILDS:
            char = build_character(CharacterBuild(level=level, **base), registry)
            cs = CombatantState.from_character(
                char, name, name.capitalize(), "party", CLASS_PROFILE[class_id]
            )
            party.append(cs)
        goblins = [_goblin(f"g{i}") for i in range(num_goblins)]
        return ScenarioState(combatants=party + goblins, dice=Dice(seed))
    return factory


# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------

def test_party_win_rate_at_least_90_percent(registry: ContentRegistry) -> None:
    """L5 party vs 4 goblins should win >= 90% of the time."""
    results = run_encounter_batch(
        _make_factory(registry), select_actions, n=100, base_seed=0
    )
    suite = summarize(results)
    win_rate = suite.win_rate("party")
    assert win_rate >= 0.90, (
        f"Party win rate {win_rate:.1%} is below 90% threshold.\n"
        + format_report(suite, "Failing Suite")
    )


def test_no_encounter_times_out(registry: ContentRegistry) -> None:
    """Every encounter should resolve within max_rounds=20."""
    results = run_encounter_batch(
        _make_factory(registry), select_actions, n=50, base_seed=200
    )
    timed_out = [r for r in results if r.timed_out]
    assert len(timed_out) == 0, (
        f"{len(timed_out)} encounters timed out (seeds: {[r.seed for r in timed_out]})"
    )


def test_avg_rounds_in_reasonable_range(registry: ContentRegistry) -> None:
    """Average combat length should be between 1 and 8 rounds."""
    results = run_encounter_batch(
        _make_factory(registry), select_actions, n=50, base_seed=300
    )
    suite = summarize(results)
    assert 1 <= suite.avg_rounds <= 8, (
        f"avg_rounds={suite.avg_rounds:.1f} is outside [1, 8]"
    )


def test_outcomes_vary_across_seeds(registry: ContentRegistry) -> None:
    """At least some variation in final party HP across 50 encounters."""
    results = run_encounter_batch(
        _make_factory(registry), select_actions, n=50, base_seed=400
    )
    hp_totals = {
        sum(c.hp_final for c in r.combatants if c.team == "party" and c.is_alive)
        for r in results
    }
    assert len(hp_totals) > 1, "All encounters ended with identical party HP (degenerate)"


def test_party_members_survive_most_encounters(registry: ContentRegistry) -> None:
    """In >70% of encounters, at least 3 of 4 party members should survive."""
    results = run_encounter_batch(
        _make_factory(registry), select_actions, n=100, base_seed=500
    )
    good_runs = sum(
        1 for r in results
        if len(r.survivors("party")) >= 3
    )
    assert good_runs / len(results) >= 0.70, (
        f"Only {good_runs}/100 encounters ended with >=3 survivors"
    )


def test_suite_report_is_printable(registry: ContentRegistry) -> None:
    """format_report should produce non-empty output without error."""
    results = run_encounter_batch(
        _make_factory(registry), select_actions, n=10, base_seed=600
    )
    suite = summarize(results)
    report = format_report(suite, "Smoke Test Suite")
    assert len(report) > 50
    assert "party" in report


def test_determinism_across_batch_reruns(registry: ContentRegistry) -> None:
    """Running the same batch twice with the same base_seed yields identical results."""
    factory = _make_factory(registry)
    r1 = run_encounter_batch(factory, select_actions, n=20, base_seed=0)
    r2 = run_encounter_batch(factory, select_actions, n=20, base_seed=0)
    for a, b in zip(r1, r2):
        assert a.winner_team == b.winner_team
        assert a.rounds == b.rounds
        assert [(c.hp_final, c.is_alive) for c in a.combatants] == \
               [(c.hp_final, c.is_alive) for c in b.combatants]
