"""Integration test: standard four-member party vs. goblin band.

Builds all four party members from YAML content at level 5, then runs them
against four goblins using the real behavior AI (select_actions).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.engine.resolver import run_combat
from balance_framework.ai.decision import select_actions
from balance_framework.ai.profiles import CLASS_PROFILE
from balance_framework.registry.loader import load_content_directory
from balance_framework.registry.registry import ContentRegistry
from balance_framework.registry.character_builder import CharacterBuild, build_character


# ---------------------------------------------------------------------------
# Standard party (L5)
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


def _build_party(registry: ContentRegistry) -> list[CombatantState]:
    combatants = []
    for name, base, class_id in [
        ("garrick", GARRICK_BASE, "fighter"),
        ("elowyn", ELOWYN_BASE, "cleric"),
        ("varian", VARIAN_BASE, "wizard"),
        ("mira", MIRA_BASE, "rogue"),
    ]:
        char = build_character(CharacterBuild(level=5, **base), registry)
        cs = CombatantState.from_character(
            char, name, name.capitalize(), "party", CLASS_PROFILE[class_id]
        )
        combatants.append(cs)
    return combatants


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_party_defeats_goblin_band(registry: ContentRegistry) -> None:
    """L5 party should defeat four goblins (CR 1/4 each) reliably."""
    party = _build_party(registry)
    goblins = [_goblin(f"goblin{i}") for i in range(4)]
    scenario = ScenarioState(combatants=party + goblins, dice=Dice(42))
    run_combat(scenario, select_actions, max_rounds=20)
    assert scenario.is_over
    assert scenario.winner_team == "party"


def test_party_vs_goblins_deterministic(registry: ContentRegistry) -> None:
    """Same seed produces the same combat outcome."""
    def _run(seed: int) -> dict:
        party = _build_party(registry)
        goblins = [_goblin(f"goblin{i}") for i in range(4)]
        scenario = ScenarioState(combatants=party + goblins, dice=Dice(seed))
        run_combat(scenario, select_actions, max_rounds=20)
        return scenario.snapshot()

    assert _run(seed=0) == _run(seed=0)
    assert _run(seed=7) == _run(seed=7)


def test_party_all_members_participate(registry: ContentRegistry) -> None:
    """Every party member should appear in the event log (took at least one action)."""
    party = _build_party(registry)
    goblins = [_goblin(f"goblin{i}") for i in range(2)]  # fewer goblins to speed test
    scenario = ScenarioState(combatants=party + goblins, dice=Dice(42))
    run_combat(scenario, select_actions, max_rounds=20)
    log = "\n".join(scenario.events)
    for member in party:
        assert member.display_name in log, f"{member.display_name} never acted"


def test_cleric_heals_during_combat(registry: ContentRegistry) -> None:
    """Elowyn should cast at least one healing spell if any ally takes damage."""
    party = _build_party(registry)
    goblins = [_goblin(f"goblin{i}") for i in range(6)]  # more goblins = more damage taken
    scenario = ScenarioState(combatants=party + goblins, dice=Dice(1))
    run_combat(scenario, select_actions, max_rounds=20)
    heal_events = [e for e in scenario.events if "heals" in e.lower()]
    assert len(heal_events) >= 1, "Cleric never healed during the encounter"


def test_different_seeds_can_vary(registry: ContentRegistry) -> None:
    """Different seeds should produce at least some variation in final HP state."""
    snapshots = set()
    for seed in range(20):
        party = _build_party(registry)
        goblins = [_goblin(f"goblin{i}") for i in range(4)]
        scenario = ScenarioState(combatants=party + goblins, dice=Dice(seed))
        run_combat(scenario, select_actions, max_rounds=20)
        # Key on surviving party HP to detect variation
        hp_key = tuple(c.hp_current for c in scenario.combatants if c.team == "party")
        snapshots.add(hp_key)
    assert len(snapshots) > 1, "All seeds produced identical final HP distribution"
