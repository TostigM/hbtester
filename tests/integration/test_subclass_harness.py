"""Integration tests for the subclass comparison harness.

Runs Battle Master (fighter/battle_master) vs Champion (fighter/champion) over
20 seeded encounters each.  Checks that:
  - Both variants produce valid EncounterSuite results
  - Both achieve a reasonable win rate against 2 goblins
  - Per-combatant stats are populated (damage, kills)
  - The comparison report is printable and non-empty
  - Running the same comparison twice yields identical results (determinism)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from balance_framework.registry.loader import load_content_directory
from balance_framework.registry.registry import ContentRegistry
from balance_framework.registry.character_builder import CharacterBuild
from balance_framework.harnesses.subclass import (
    compare_subclasses,
    format_comparison,
    SubclassComparison,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_BATTLE_MASTER = CharacterBuild(
    species_id="human", class_id="fighter", subclass_id="battle_master",
    background_id="soldier", level=5,
    ability_scores={"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8},
    feat_ids=["tough", "savage_attacker"],
    armor_type="chain_mail", has_shield=True, selected_fighting_style="defense",
)

_CHAMPION = CharacterBuild(
    species_id="human", class_id="fighter", subclass_id="champion",
    background_id="soldier", level=5,
    ability_scores={"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8},
    feat_ids=["tough", "savage_attacker"],
    armor_type="chain_mail", has_shield=True, selected_fighting_style="defense",
)


@pytest.fixture(scope="module")
def registry() -> ContentRegistry:
    return ContentRegistry(load_content_directory(Path("content")))


@pytest.fixture(scope="module")
def comparison(registry: ContentRegistry) -> SubclassComparison:
    return compare_subclasses(
        _BATTLE_MASTER, "Battle Master",
        _CHAMPION, "Champion",
        registry,
        n=20,
        base_seed=0,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_both_variants_have_results(comparison: SubclassComparison) -> None:
    assert comparison.variant_a.suite.n == 20
    assert comparison.variant_b.suite.n == 20


def test_battle_master_wins_majority(comparison: SubclassComparison) -> None:
    win_rate = comparison.variant_a.suite.win_rate("party")
    assert win_rate >= 0.60, f"Battle Master win rate {win_rate:.1%} < 60%"


def test_champion_wins_majority(comparison: SubclassComparison) -> None:
    win_rate = comparison.variant_b.suite.win_rate("party")
    assert win_rate >= 0.60, f"Champion win rate {win_rate:.1%} < 60%"


def test_variant_combatant_stats_present(comparison: SubclassComparison) -> None:
    assert "variant" in comparison.variant_a.combatant_stats
    assert "variant" in comparison.variant_b.combatant_stats


def test_variant_deals_nonzero_damage(comparison: SubclassComparison) -> None:
    bm_stats = comparison.variant_a.combatant_stats["variant"]
    champ_stats = comparison.variant_b.combatant_stats["variant"]
    assert bm_stats.avg_damage_dealt > 0
    assert champ_stats.avg_damage_dealt > 0


def test_variant_records_kills(comparison: SubclassComparison) -> None:
    bm_stats = comparison.variant_a.combatant_stats["variant"]
    assert bm_stats.avg_kills > 0, "Battle Master should kill at least some goblins"


def test_comparison_report_is_printable(comparison: SubclassComparison) -> None:
    report = format_comparison(comparison)
    assert len(report) > 50
    assert "Battle Master" in report
    assert "Champion" in report


def test_comparison_is_deterministic(registry: ContentRegistry) -> None:
    c1 = compare_subclasses(
        _BATTLE_MASTER, "Battle Master", _CHAMPION, "Champion",
        registry, n=10, base_seed=99,
    )
    c2 = compare_subclasses(
        _BATTLE_MASTER, "Battle Master", _CHAMPION, "Champion",
        registry, n=10, base_seed=99,
    )
    assert c1.variant_a.suite.avg_rounds == c2.variant_a.suite.avg_rounds
    assert c1.variant_b.suite.avg_rounds == c2.variant_b.suite.avg_rounds
    a_stats1 = c1.variant_a.combatant_stats["variant"]
    a_stats2 = c2.variant_a.combatant_stats["variant"]
    assert a_stats1.avg_damage_dealt == a_stats2.avg_damage_dealt
