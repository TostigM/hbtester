"""Unit tests for the content directory loader."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from balance_framework.registry.loader import load_content_directory


def test_load_valid_content_directory(tmp_path: Path) -> None:
    yaml_text = textwrap.dedent("""\
        schema_version: "0.1"
        content_type: feat
        id: test_feat
        display_name: Test Feat
        source: TEST
        author: Test
        feat_category: origin
        benefits: []
    """)
    (tmp_path / "test_feat.yaml").write_text(yaml_text, encoding="utf-8")
    items = load_content_directory(tmp_path)
    assert len(items) == 1
    assert items[0].id == "test_feat"


def test_load_empty_directory(tmp_path: Path) -> None:
    items = load_content_directory(tmp_path)
    assert items == []


def test_load_nonexistent_directory() -> None:
    with pytest.raises(FileNotFoundError):
        load_content_directory(Path("/no/such/path"))


def test_load_invalid_yaml_raises(tmp_path: Path) -> None:
    (tmp_path / "bad.yaml").write_text("key: [\nnot closed", encoding="utf-8")
    with pytest.raises(ValueError, match="YAML parse error"):
        load_content_directory(tmp_path)


def test_load_unknown_content_type_raises(tmp_path: Path) -> None:
    (tmp_path / "unknown.yaml").write_text(
        "content_type: dragon_breath\nid: x", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="unknown or missing content_type"):
        load_content_directory(tmp_path)


def test_load_invalid_schema_raises(tmp_path: Path) -> None:
    bad = textwrap.dedent("""\
        schema_version: "0.1"
        content_type: feat
        id: bad_feat
        display_name: Bad Feat
        source: TEST
        author: Test
        feat_category: totally_made_up
        benefits: []
    """)
    (tmp_path / "bad.yaml").write_text(bad, encoding="utf-8")
    with pytest.raises(ValueError, match="Content validation failed"):
        load_content_directory(tmp_path)


def test_load_all_errors_collected(tmp_path: Path) -> None:
    (tmp_path / "bad1.yaml").write_text(
        "content_type: dragon_breath\nid: x", encoding="utf-8"
    )
    (tmp_path / "bad2.yaml").write_text(
        "content_type: bad_type\nid: y", encoding="utf-8"
    )
    with pytest.raises(ValueError) as exc_info:
        load_content_directory(tmp_path)
    assert "2 error" in str(exc_info.value)


def test_load_real_content_directory() -> None:
    """Happy-path integration: the actual content/ directory loads cleanly."""
    items = load_content_directory(Path("content"))
    assert len(items) > 0
    ids = {item.id for item in items}
    assert "fighter" in ids
    assert "battle_master" in ids
    assert "human" in ids
