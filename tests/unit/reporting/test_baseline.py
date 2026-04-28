"""Unit tests for baseline save/load/diff."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from balance_framework.runner.collector import EncounterResult, CombatantResult
from balance_framework.reporting.test_report import summarize
from balance_framework.reporting.baseline import save_baseline, load_baseline, diff_baseline


def _result(winner: str, rounds: int, party_hp: int = 20) -> EncounterResult:
    return EncounterResult(
        seed=0, winner_team=winner, rounds=rounds, timed_out=False,
        combatants=[
            CombatantResult("hero", "Hero", "party", party_hp, 30, True, False),
            CombatantResult("goblin", "G", "enemies", 0, 7, False, False),
        ],
    )


# ---------------------------------------------------------------------------
# save_baseline / load_baseline
# ---------------------------------------------------------------------------

def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    results = [_result("party", 3) for _ in range(10)]
    suite = summarize(results)
    path = tmp_path / "baseline.json"
    save_baseline(suite, path)
    loaded = load_baseline(path)
    assert loaded["n"] == 10
    assert abs(loaded["avg_rounds"] - 3.0) < 1e-9
    assert "party" in loaded["teams"]


def test_save_creates_parent_dirs(tmp_path: Path) -> None:
    results = [_result("party", 2)]
    suite = summarize(results)
    path = tmp_path / "subdir" / "nested" / "baseline.json"
    save_baseline(suite, path)
    assert path.exists()


def test_load_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_baseline(tmp_path / "nonexistent.json")


def test_saved_baseline_is_valid_json(tmp_path: Path) -> None:
    results = [_result("party", 2)]
    suite = summarize(results)
    path = tmp_path / "b.json"
    save_baseline(suite, path)
    data = json.loads(path.read_text())
    assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# diff_baseline
# ---------------------------------------------------------------------------

def test_diff_no_regression_when_identical() -> None:
    results = [_result("party", 3) for _ in range(20)]
    suite = summarize(results)
    baseline = {"avg_rounds": 3.0, "teams": {"party": {"win_rate": 1.0, "avg_hp_fraction": suite.teams["party"].avg_hp_fraction}}}
    flags = diff_baseline(suite, baseline)
    assert flags == []


def test_diff_flags_win_rate_regression() -> None:
    results = [_result("party", 3) for _ in range(20)]
    suite = summarize(results)
    # Baseline expected 100% party win rate; suite has 100% — no regression
    # Now simulate a regression: baseline expected 95%, got 50%
    results_bad = [_result("party", 3)] * 10 + [_result("enemies", 2)] * 10
    suite_bad = summarize(results_bad)
    baseline = {"avg_rounds": 3.0, "teams": {"party": {"win_rate": 0.95, "avg_hp_fraction": 0.7}}}
    flags = diff_baseline(suite_bad, baseline, win_rate_threshold=0.05)
    flag_metrics = [f.metric for f in flags]
    assert "party.win_rate" in flag_metrics


def test_diff_flags_rounds_regression() -> None:
    results = [_result("party", 8) for _ in range(10)]
    suite = summarize(results)
    baseline = {"avg_rounds": 3.0, "teams": {}}
    flags = diff_baseline(suite, baseline, rounds_threshold=1.0)
    assert any(f.metric == "avg_rounds" for f in flags)


def test_diff_no_flag_within_threshold() -> None:
    results = [_result("party", 3) for _ in range(10)]
    suite = summarize(results)
    # avg_rounds=3, baseline=3.5, threshold=1.0 → delta=0.5, no flag
    # party hp_fraction = 20/30 ≈ 0.667; baseline 0.72 is within 0.1 threshold
    baseline = {"avg_rounds": 3.5, "teams": {"party": {"win_rate": 1.0, "avg_hp_fraction": 0.72}}}
    flags = diff_baseline(suite, baseline, rounds_threshold=1.0, win_rate_threshold=0.1, hp_threshold=0.1)
    assert flags == []


def test_regression_flag_str() -> None:
    from balance_framework.reporting.baseline import RegressionFlag
    f = RegressionFlag("party.win_rate", 0.95, 0.50, -0.45, 0.10)
    s = str(f)
    assert "party.win_rate" in s
    assert "0.95" in s
