"""Unit tests for ContentRegistry."""

from __future__ import annotations

from pathlib import Path

import pytest

from balance_framework.registry.loader import load_content_directory
from balance_framework.registry.registry import ContentRegistry
from balance_framework.schema.exceptions import ReferenceError as ContentReferenceError


@pytest.fixture(scope="module")
def registry() -> ContentRegistry:
    return ContentRegistry(load_content_directory(Path("content")))


def test_get_class_exists(registry: ContentRegistry) -> None:
    cls = registry.get_class("fighter")
    assert cls.id == "fighter"
    assert cls.hit_die == "d10"


def test_get_subclass_exists(registry: ContentRegistry) -> None:
    sc = registry.get_subclass("battle_master")
    assert sc.id == "battle_master"
    assert sc.parent_class == "fighter"


def test_get_species_exists(registry: ContentRegistry) -> None:
    sp = registry.get_species("human")
    assert sp.id == "human"
    assert sp.creature_type == "humanoid"


def test_get_background_exists(registry: ContentRegistry) -> None:
    bg = registry.get_background("soldier")
    assert bg.id == "soldier"
    assert "athletics" in bg.skill_proficiencies


def test_get_feat_exists(registry: ContentRegistry) -> None:
    feat = registry.get_feat("tough")
    assert feat.id == "tough"
    assert feat.feat_category == "origin"


def test_get_spell_exists(registry: ContentRegistry) -> None:
    spell = registry.get_spell("fireball")
    assert spell.id == "fireball"
    assert spell.level == 3


def test_get_magic_item_exists(registry: ContentRegistry) -> None:
    item = registry.get_magic_item("plus_one_longsword")
    assert item.id == "plus_one_longsword"
    assert item.rarity == "uncommon"


def test_get_class_missing_raises(registry: ContentRegistry) -> None:
    with pytest.raises(ContentReferenceError, match="artificer"):
        registry.get_class("artificer")


def test_get_subclass_missing_raises(registry: ContentRegistry) -> None:
    with pytest.raises(ContentReferenceError, match="moon_druid"):
        registry.get_subclass("moon_druid")


def test_get_feat_missing_raises(registry: ContentRegistry) -> None:
    with pytest.raises(ContentReferenceError):
        registry.get_feat("war_caster")


def test_get_all_classes(registry: ContentRegistry) -> None:
    classes = registry.get_all_classes()
    ids = {c.id for c in classes}
    assert {"fighter", "cleric", "wizard", "rogue"}.issubset(ids)


def test_get_all_subclasses(registry: ContentRegistry) -> None:
    subs = registry.get_all_subclasses()
    ids = {s.id for s in subs}
    assert {"battle_master", "life_domain", "evoker", "thief"}.issubset(ids)


def test_get_all_feats(registry: ContentRegistry) -> None:
    feats = registry.get_all_feats()
    assert len(feats) >= 5


def test_get_all_spells(registry: ContentRegistry) -> None:
    spells = registry.get_all_spells()
    assert len(spells) >= 10
