"""Integration tests for deterministic combat reproduction."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.resolver import run_combat
from balance_framework.engine.combat.actions import WeaponAttackAction, Action


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _combatant(id: str, team: str, hp: int = 30, ac: int = 14) -> CombatantState:
    return CombatantState(
        id=id, display_name=id.capitalize(), team=team,
        hp_max=hp, hp_current=hp,
        ac=ac, speed=30, proficiency_bonus=2,
        ability_modifiers={"DEX": 2, "STR": 2, "CON": 1},
    )


def _attack_selector(combatant: CombatantState, scenario: ScenarioState) -> list[Action] | None:
    enemies = [c for c in scenario.living_combatants() if c.team != combatant.team]
    if not enemies:
        return None
    target = enemies[0]
    return [WeaponAttackAction(
        attacker_id=combatant.id,
        target_id=target.id,
        attack_bonus=4,
        damage_dice=[(1, 6)],
        damage_type="slashing",
        damage_bonus=2,
    )]


def _run(seed: int) -> dict:
    """Run a deterministic combat and return its snapshot."""
    party = [_combatant("hero", "party")]
    enemies = [_combatant("goblin", "enemies", hp=15, ac=12)]
    scenario = ScenarioState(combatants=party + enemies, dice=Dice(seed))
    run_combat(scenario, _attack_selector, max_rounds=20)
    return scenario.snapshot()


# ---------------------------------------------------------------------------
# Same seed → same outcome
# ---------------------------------------------------------------------------

def test_same_seed_produces_same_outcome() -> None:
    snap1 = _run(seed=42)
    snap2 = _run(seed=42)
    assert snap1 == snap2


def test_same_seed_same_event_log() -> None:
    def _run_events(seed: int) -> list[str]:
        party = [_combatant("hero", "party")]
        enemies = [_combatant("goblin", "enemies", hp=15, ac=12)]
        scenario = ScenarioState(combatants=party + enemies, dice=Dice(seed))
        run_combat(scenario, _attack_selector, max_rounds=20)
        return scenario.events

    events1 = _run_events(99)
    events2 = _run_events(99)
    assert events1 == events2


# ---------------------------------------------------------------------------
# Different seeds → different outcomes (probabilistic)
# ---------------------------------------------------------------------------

def test_different_seeds_can_differ() -> None:
    """Two seeds should eventually produce different combat snapshots."""
    outcomes: set[str] = set()
    for seed in range(20):
        snap = _run(seed=seed)
        outcomes.add(str(snap))
    assert len(outcomes) > 1, "All seeds produced identical combat outcomes — very unlikely"


# ---------------------------------------------------------------------------
# Larger party — still deterministic
# ---------------------------------------------------------------------------

def test_four_vs_four_deterministic() -> None:
    def _run4(seed: int) -> dict:
        party = [_combatant(f"hero{i}", "party") for i in range(2)]
        enemies = [_combatant(f"orc{i}", "enemies", hp=20) for i in range(2)]
        scenario = ScenarioState(combatants=party + enemies, dice=Dice(seed))
        run_combat(scenario, _attack_selector, max_rounds=20)
        return scenario.snapshot()

    assert _run4(7) == _run4(7)
    assert _run4(13) == _run4(13)


# ---------------------------------------------------------------------------
# snapshot covers all combatants
# ---------------------------------------------------------------------------

def test_snapshot_includes_all_combatants() -> None:
    party = [_combatant("hero", "party")]
    enemies = [_combatant("goblin", "enemies", hp=15, ac=12)]
    scenario = ScenarioState(combatants=party + enemies, dice=Dice(42))
    run_combat(scenario, _attack_selector, max_rounds=20)
    snap = scenario.snapshot()
    ids = {c["id"] for c in snap["combatants"]}
    assert ids == {"hero", "goblin"}


def test_snapshot_records_winner() -> None:
    party = [_combatant("hero", "party", hp=200, ac=25)]
    enemies = [_combatant("goblin", "enemies", hp=5, ac=5)]
    scenario = ScenarioState(combatants=party + enemies, dice=Dice(0))
    run_combat(scenario, _attack_selector, max_rounds=20)
    snap = scenario.snapshot()
    assert snap["is_over"]
    assert snap["winner_team"] == "party"
