"""Unit tests for the CLI using Click's CliRunner (no real simulation)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from balance_framework.cli.main import main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# Main group
# ---------------------------------------------------------------------------

def test_main_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "test" in result.output
    assert "validate" in result.output
    assert "build-character" in result.output
    assert "generate-baseline" in result.output


def test_main_version(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# validate command
# ---------------------------------------------------------------------------

def test_validate_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["validate", "--help"])
    assert result.exit_code == 0
    assert "--content-dir" in result.output


def test_validate_missing_dir_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(main, ["validate", "--content-dir", str(tmp_path / "nope")])
    assert result.exit_code != 0


def test_validate_empty_dir_exits_zero(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(main, ["validate", "--content-dir", str(tmp_path)])
    assert result.exit_code == 0


def test_validate_invalid_yaml_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("content_type: subclass\n# missing required fields\n", encoding="utf-8")
    result = runner.invoke(main, ["validate", "--content-dir", str(tmp_path)])
    assert result.exit_code != 0
    assert "FAIL" in result.output or "failed" in result.output


def test_validate_valid_content_exits_zero(runner: CliRunner, tmp_path: Path) -> None:
    good = tmp_path / "champ.yaml"
    good.write_text(
        Path("content/subclasses/champion.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    result = runner.invoke(main, ["validate", "--content-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "1 passed" in result.output


# ---------------------------------------------------------------------------
# test subclass command
# ---------------------------------------------------------------------------

def test_test_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["test", "--help"])
    assert result.exit_code == 0
    assert "subclass" in result.output


def test_test_subclass_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["test", "subclass", "--help"])
    assert result.exit_code == 0
    assert "--file" in result.output
    assert "--runs" in result.output
    assert "--output" in result.output
    assert "--level" in result.output


def test_test_subclass_missing_file_exits_nonzero(runner: CliRunner, tmp_path: Path) -> None:
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", str(tmp_path / "nope.yaml"),
        "--runs", "1",
        "--output", str(tmp_path / "out.md"),
    ])
    assert result.exit_code != 0


def test_test_subclass_missing_parent_class_exits_nonzero(
    runner: CliRunner, tmp_path: Path
) -> None:
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("id: foo\ndisplay_name: Foo\ncontent_type: subclass\n", encoding="utf-8")
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", str(bad_yaml),
        "--runs", "1",
        "--output", str(tmp_path / "out.md"),
    ])
    assert result.exit_code != 0


def test_test_subclass_unknown_class_exits_nonzero(
    runner: CliRunner, tmp_path: Path
) -> None:
    yaml_file = tmp_path / "exotic.yaml"
    yaml_file.write_text(
        "id: dragon_knight\ndisplay_name: Dragon Knight\n"
        "parent_class: artificer\ncontent_type: subclass\n",
        encoding="utf-8",
    )
    result = runner.invoke(main, [
        "test", "subclass",
        "--file", str(yaml_file),
        "--runs", "1",
        "--output", str(tmp_path / "out.md"),
    ])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# build-character command
# ---------------------------------------------------------------------------

def test_build_character_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["build-character", "--help"])
    assert result.exit_code == 0
    assert "--class" in result.output
    assert "--subclass" in result.output
    assert "--level" in result.output


def test_build_character_unknown_class_exits_nonzero(runner: CliRunner) -> None:
    result = runner.invoke(main, ["build-character", "--class", "artificer"])
    assert result.exit_code != 0


def test_build_character_missing_content_dir_exits_nonzero(
    runner: CliRunner, tmp_path: Path
) -> None:
    result = runner.invoke(main, [
        "build-character", "--class", "fighter",
        "--content-dir", str(tmp_path / "nope"),
    ])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# generate-baseline command
# ---------------------------------------------------------------------------

def test_generate_baseline_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["generate-baseline", "--help"])
    assert result.exit_code == 0
    assert "--output" in result.output
    assert "--runs" in result.output


def test_generate_baseline_missing_output_exits_nonzero(runner: CliRunner) -> None:
    result = runner.invoke(main, ["generate-baseline"])
    assert result.exit_code != 0
