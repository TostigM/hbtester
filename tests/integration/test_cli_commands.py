"""Integration tests for CLI commands — run against real content with small N."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from balance_framework.cli.main import main


@pytest.fixture(scope="module")
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def test_validate_real_content(runner: CliRunner) -> None:
    """All 50 content files should validate cleanly."""
    result = runner.invoke(main, ["validate", "--content-dir", "content"])
    assert result.exit_code == 0
    assert "passed" in result.output
    assert "0 failed" in result.output


# ---------------------------------------------------------------------------
# build-character
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("class_id,subclass_id", [
    ("fighter", "battle_master"),
    ("cleric", "life_domain"),
    ("wizard", "evoker"),
    ("rogue", "thief"),
])
def test_build_character_standard_party(
    runner: CliRunner, class_id: str, subclass_id: str
) -> None:
    result = runner.invoke(main, [
        "build-character",
        "--class", class_id,
        "--subclass", subclass_id,
        "--level", "5",
    ])
    assert result.exit_code == 0, result.output
    assert "HP" in result.output
    assert "AC" in result.output


def test_build_character_no_subclass(runner: CliRunner) -> None:
    result = runner.invoke(main, ["build-character", "--class", "fighter", "--level", "3"])
    assert result.exit_code == 0
    assert "HP" in result.output


def test_build_character_outputs_level(runner: CliRunner) -> None:
    result = runner.invoke(main, [
        "build-character", "--class", "rogue", "--level", "10",
    ])
    assert result.exit_code == 0
    assert "10" in result.output


# ---------------------------------------------------------------------------
# test subclass (small run count for speed)
# ---------------------------------------------------------------------------

def test_test_subclass_champion_markdown(runner: CliRunner, tmp_path: Path) -> None:
    out = tmp_path / "champion.md"
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", "content/subclasses/champion.yaml",
        "--runs", "5",
        "--output", str(out),
    ])
    assert result.exit_code == 0, result.output
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "Champion" in content
    assert "|" in content  # markdown table


def test_test_subclass_battle_master_json(runner: CliRunner, tmp_path: Path) -> None:
    out = tmp_path / "bm.json"
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", "content/subclasses/battle_master.yaml",
        "--runs", "5",
        "--output", str(out),
    ])
    assert result.exit_code == 0, result.output
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["n"] == 5
    assert "party" in data["teams"]


def test_test_subclass_text_output(runner: CliRunner, tmp_path: Path) -> None:
    out = tmp_path / "result.txt"
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", "content/subclasses/champion.yaml",
        "--runs", "3",
        "--output", str(out),
    ])
    assert result.exit_code == 0, result.output
    assert out.exists()


def test_test_subclass_summary_in_stdout(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", "content/subclasses/champion.yaml",
        "--runs", "5",
        "--output", str(tmp_path / "out.md"),
    ])
    assert result.exit_code == 0
    assert "win rate" in result.output.lower()


def test_test_subclass_cleric(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", "content/subclasses/life_domain.yaml",
        "--runs", "5",
        "--output", str(tmp_path / "cleric.md"),
    ])
    assert result.exit_code == 0, result.output


# ---------------------------------------------------------------------------
# generate-baseline
# ---------------------------------------------------------------------------

def test_generate_baseline_small_run(runner: CliRunner, tmp_path: Path) -> None:
    out = tmp_path / "baseline.json"
    result = runner.invoke(main, [
        "generate-baseline",
        "--output", str(out),
        "--runs", "5",
        "--level", "5",
    ])
    assert result.exit_code == 0, result.output
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["n"] == 5
    assert "party" in data["teams"]


def test_generate_baseline_win_rate_reasonable(runner: CliRunner, tmp_path: Path) -> None:
    out = tmp_path / "b.json"
    runner.invoke(main, [
        "generate-baseline", "--output", str(out), "--runs", "10",
    ])
    data = json.loads(out.read_text(encoding="utf-8"))
    wr = data["teams"]["party"]["win_rate"]
    assert wr >= 0.5, f"Unexpected party win rate: {wr}"
