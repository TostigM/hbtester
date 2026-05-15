"""Unit tests for encounter result collection."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.runner.collector import collect_result, EncounterResult


def _c(id: str, team: str, hp: int = 20, alive: bool = True) -> CombatantState:
    c = CombatantState(
        id=id, display_name=id, team=team,
        hp_max=hp, hp_current=hp if alive else 0,
        is_alive=alive,
    )
    return c


def _scenario(winner: str | None = "party", rounds: int = 3, over: bool = True) -> ScenarioState:
    hero = _c("hero", "party", hp=30)
    enemy = _c("goblin", "enemies", hp=7, alive=(winner != "party"))
    s = ScenarioState(combatants=[hero, enemy], dice=Dice(0))
    s.round_number = rounds
    s.is_over = over
    s.winner_team = winner
    return s


# ---------------------------------------------------------------------------
# collect_result
# ---------------------------------------------------------------------------

def test_collect_result_winner() -> None:
    scenario = _scenario(winner="party")
    result = collect_result(scenario, seed=42)
    assert result.winner_team == "party"
    assert result.seed == 42


def test_collect_result_rounds() -> None:
    scenario = _scenario(rounds=5)
    result = collect_result(scenario, seed=0)
    assert result.rounds == 5


def test_collect_result_not_timed_out() -> None:
    scenario = _scenario(over=True)
    result = collect_result(scenario, seed=0)
    assert not result.timed_out


def test_collect_result_timed_out() -> None:
    scenario = _scenario(over=False, winner=None)
    result = collect_result(scenario, seed=0)
    assert result.timed_out


def test_collect_result_combatants_count() -> None:
    scenario = _scenario()
    result = collect_result(scenario, seed=0)
    assert len(result.combatants) == 2


def test_collect_result_hp_captured() -> None:
    hero = _c("hero", "party", hp=30)
    hero.hp_current = 18
    s = ScenarioState(combatants=[hero], dice=Dice(0))
    s.is_over = True
    s.winner_team = "party"
    s.round_number = 2
    result = collect_result(s, seed=0)
    cr = result.combatants[0]
    assert cr.hp_final == 18
    assert cr.hp_max == 30


# ---------------------------------------------------------------------------
# EncounterResult helpers
# ---------------------------------------------------------------------------

def test_party_win() -> None:
    r = EncounterResult(seed=0, winner_team="party", rounds=2, timed_out=False)
    assert r.party_win()
    assert not r.enemies_win()


def test_enemies_win() -> None:
    r = EncounterResult(seed=0, winner_team="enemies", rounds=3, timed_out=False)
    assert r.enemies_win()
    assert not r.party_win()


def test_survivors_filters_by_team_and_alive() -> None:
    from balance_framework.runner.collector import CombatantResult
    r = EncounterResult(seed=0, winner_team="party", rounds=2, timed_out=False, combatants=[
        CombatantResult("h", "Hero", "party", 20, 30, True, False),
        CombatantResult("d", "Dead", "party", 0, 30, False, False),
        CombatantResult("g", "Goblin", "enemies", 0, 7, False, False),
    ])
    assert len(r.survivors("party")) == 1
    assert r.survivors("party")[0].id == "h"


def test_hp_remaining() -> None:
    from balance_framework.runner.collector import CombatantResult
    r = EncounterResult(seed=0, winner_team="party", rounds=2, timed_out=False, combatants=[
        CombatantResult("h1", "H1", "party", 15, 30, True, False),
        CombatantResult("h2", "H2", "party", 10, 30, True, False),
        CombatantResult("g", "G", "enemies", 0, 7, False, False),
    ])
    assert r.hp_remaining("party") == 25


def test_hp_fraction() -> None:
    from balance_framework.runner.collector import CombatantResult
    r = EncounterResult(seed=0, winner_team="party", rounds=2, timed_out=False, combatants=[
        CombatantResult("h", "H", "party", 15, 30, True, False),  # 50%
    ])
    assert abs(r.hp_fraction("party") - 0.5) < 1e-9


def test_hp_fraction_no_survivors_is_zero() -> None:
    from balance_framework.runner.collector import CombatantResult
    r = EncounterResult(seed=0, winner_team="enemies", rounds=2, timed_out=False, combatants=[
        CombatantResult("h", "H", "party", 0, 30, False, False),
    ])
    assert r.hp_fraction("party") == 0.0
