"""M9 integration tests — Tier A content validates and baselines generate correctly."""

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
# Content validation — all 19 Tier A subclasses + 2 new classes
# ---------------------------------------------------------------------------

def test_all_content_validates(runner: CliRunner) -> None:
    result = runner.invoke(main, ["validate", "--content-dir", "content"])
    assert result.exit_code == 0, result.output
    assert "0 failed" in result.output


@pytest.mark.parametrize("subclass_id", [
    "eldritch_knight", "light_domain", "war_domain", "trickery_domain",
    "abjurer", "diviner", "illusionist",
    "assassin", "arcane_trickster", "soulknife",
    "berserker", "world_tree", "zealot", "lore",
])
def test_new_subclass_builds_and_runs(runner: CliRunner, tmp_path: Path, subclass_id: str) -> None:
    """Each new subclass should run 3 encounters without error."""
    out = tmp_path / f"{subclass_id}.md"
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", f"content/subclasses/{subclass_id}.yaml",
        "--runs", "3",
        "--output", str(out),
    ])
    assert result.exit_code == 0, f"{subclass_id}: {result.output}"
    assert out.exists()


@pytest.mark.parametrize("class_id", ["barbarian", "bard"])
def test_new_class_builds(runner: CliRunner, class_id: str) -> None:
    result = runner.invoke(main, ["build-character", "--class", class_id, "--level", "5"])
    assert result.exit_code == 0, result.output
    assert "HP" in result.output


# ---------------------------------------------------------------------------
# Baseline generation output structure
# ---------------------------------------------------------------------------

def test_baseline_dir_structure(tmp_path: Path, runner: CliRunner) -> None:
    result = runner.invoke(main, [
        "generate-baseline",
        "--output", str(tmp_path / "baseline"),
        "--runs", "3",
        "--level", "5",
        "--tier", "A",
    ])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "baseline" / "metadata.json").exists()
    assert (tmp_path / "baseline" / "subclasses").is_dir()


def test_baseline_metadata_fields(tmp_path: Path, runner: CliRunner) -> None:
    runner.invoke(main, [
        "generate-baseline",
        "--output", str(tmp_path / "b"),
        "--runs", "3",
        "--tier", "A",
    ])
    meta = json.loads((tmp_path / "b" / "metadata.json").read_text())
    assert meta["tier"] == "A"
    assert meta["rules_version"] == "PHB_2024"
    assert meta["subclass_count"] == 45
    assert "generated_on" in meta


def test_baseline_subclass_json_structure(tmp_path: Path, runner: CliRunner) -> None:
    runner.invoke(main, [
        "generate-baseline",
        "--output", str(tmp_path / "b"),
        "--runs", "3",
        "--tier", "A",
    ])
    champion = json.loads((tmp_path / "b" / "subclasses" / "champion.json").read_text())
    assert champion["subclass_id"] == "champion"
    assert champion["class_id"] == "fighter"
    assert "aggregate" in champion
    assert "encounters" in champion
    assert 0.0 <= champion["aggregate"]["avg_win_rate"] <= 1.0
    first_enc = next(iter(champion["encounters"].values()))
    assert "suite" in first_enc
    assert "combatant_stats" in first_enc
    assert 0.0 <= first_enc["suite"]["teams"]["party"]["win_rate"] <= 1.0


def test_committed_baselines_exist() -> None:
    """The baselines committed to the repo should exist and be valid JSON."""
    meta_path = Path("baselines/v1.0/metadata.json")
    assert meta_path.exists(), "baselines/v1.0/metadata.json not found in repo"
    meta = json.loads(meta_path.read_text())
    assert meta["subclass_count"] == 45
    subclass_dir = Path("baselines/v1.0/subclasses")
    assert subclass_dir.is_dir()
    json_files = list(subclass_dir.glob("*.json"))
    assert len(json_files) == 45
