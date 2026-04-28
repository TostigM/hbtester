"""Unit tests for encounter suite summarization and formatting."""

from __future__ import annotations

import pytest

from balance_framework.runner.collector import EncounterResult, CombatantResult
from balance_framework.reporting.test_report import summarize, format_report, EncounterSuite


def _party_cr(id: str, hp: int, hp_max: int = 30) -> CombatantResult:
    return CombatantResult(id, id, "party", hp, hp_max, hp > 0, False)


def _enemy_cr(id: str, hp: int, hp_max: int = 7) -> CombatantResult:
    return CombatantResult(id, id, "enemies", hp, hp_max, hp > 0, False)


def _result(
    winner: str | None,
    rounds: int,
    party_hp: int = 20,
    enemy_alive: bool = False,
    timed_out: bool = False,
) -> EncounterResult:
    return EncounterResult(
        seed=0, winner_team=winner, rounds=rounds, timed_out=timed_out,
        combatants=[
            _party_cr("hero", party_hp),
            _enemy_cr("goblin", 0 if not enemy_alive else 5),
        ],
    )


# ---------------------------------------------------------------------------
# summarize
# ---------------------------------------------------------------------------

def test_summarize_count() -> None:
    results = [_result("party", 2) for _ in range(5)]
    suite = summarize(results)
    assert suite.n == 5


def test_summarize_win_rate_all_party() -> None:
    results = [_result("party", 2) for _ in range(10)]
    suite = summarize(results)
    assert suite.win_rate("party") == 1.0
    assert suite.win_rate("enemies") == 0.0


def test_summarize_win_rate_mixed() -> None:
    results = [_result("party", 2)] * 7 + [_result("enemies", 3, party_hp=0, enemy_alive=True)] * 3
    suite = summarize(results)
    assert abs(suite.win_rate("party") - 0.7) < 1e-9
    assert abs(suite.win_rate("enemies") - 0.3) < 1e-9


def test_summarize_avg_rounds() -> None:
    results = [_result("party", r) for r in [2, 3, 4, 3, 3]]
    suite = summarize(results)
    assert abs(suite.avg_rounds - 3.0) < 1e-9


def test_summarize_timed_out_count() -> None:
    results = [_result("party", 2)] * 3 + [_result(None, 20, timed_out=True)] * 2
    suite = summarize(results)
    assert suite.timed_out == 2


def test_summarize_std_rounds_uniform() -> None:
    results = [_result("party", 3) for _ in range(10)]
    suite = summarize(results)
    assert suite.std_rounds == 0.0


def test_summarize_empty_raises() -> None:
    with pytest.raises(ValueError):
        summarize([])


def test_summarize_avg_hp_fraction() -> None:
    # party hero at 15/30 = 50%
    results = [_result("party", 2, party_hp=15) for _ in range(4)]
    suite = summarize(results)
    assert abs(suite.teams["party"].avg_hp_fraction - 0.5) < 1e-9


# ---------------------------------------------------------------------------
# format_report
# ---------------------------------------------------------------------------

def test_format_report_contains_title() -> None:
    results = [_result("party", 2)]
    suite = summarize(results)
    report = format_report(suite, title="Test Report")
    assert "Test Report" in report


def test_format_report_contains_win_rate() -> None:
    results = [_result("party", 2) for _ in range(10)]
    suite = summarize(results)
    report = format_report(suite)
    assert "100.0%" in report


def test_format_report_contains_round_info() -> None:
    results = [_result("party", 3) for _ in range(5)]
    suite = summarize(results)
    report = format_report(suite)
    assert "3.0" in report


def test_format_report_contains_team_names() -> None:
    results = [_result("party", 2)]
    suite = summarize(results)
    report = format_report(suite)
    assert "party" in report
    assert "enemies" in report
