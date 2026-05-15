"""Tests for the vocabulary constants."""

from balance_framework.schema.vocabulary import (
    ABILITY_SCORES,
    ACTION_TYPES,
    CONDITIONS,
    CREATURE_TYPES,
    DAMAGE_TYPES,
    FEAT_CATEGORIES,
    FEATURE_TYPES,
    HIT_DIES,
    ITEM_TYPES,
    MAGIC_SCHOOLS,
    RARITIES,
    SIZES,
    SKILLS,
    SPELLCASTING_PROGRESSIONS,
)


def test_ability_scores_complete() -> None:
    assert ABILITY_SCORES == {"STR", "DEX", "CON", "INT", "WIS", "CHA"}


def test_skills_count() -> None:
    assert len(SKILLS) == 18


def test_damage_types_include_common() -> None:
    for dtype in ("fire", "cold", "lightning", "slashing", "piercing", "bludgeoning"):
        assert dtype in DAMAGE_TYPES


def test_conditions_include_all_5e() -> None:
    for cond in ("blinded", "charmed", "frightened", "paralyzed", "stunned", "unconscious"):
        assert cond in CONDITIONS


def test_feature_types_non_empty() -> None:
    assert len(FEATURE_TYPES) >= 20


def test_feature_types_include_core() -> None:
    for ft in (
        "custom_action",
        "passive_feature_grant",
        "scripted_feature",
        "crit_range_modifier",
        "attack_count_modifier",
        "damage_resistance",
    ):
        assert ft in FEATURE_TYPES


def test_hit_dies() -> None:
    assert HIT_DIES == {"d6", "d8", "d10", "d12"}


def test_magic_schools_eight() -> None:
    assert len(MAGIC_SCHOOLS) == 8


def test_rarities_six() -> None:
    assert len(RARITIES) == 6
    assert "legendary" in RARITIES
    assert "artifact" in RARITIES


def test_sizes_six() -> None:
    assert len(SIZES) == 6


def test_creature_types_non_empty() -> None:
    assert "humanoid" in CREATURE_TYPES
    assert "dragon" in CREATURE_TYPES
    assert "undead" in CREATURE_TYPES


def test_feat_categories() -> None:
    assert FEAT_CATEGORIES == {"origin", "general", "fighting_style", "epic_boon"}


def test_spellcasting_progressions() -> None:
    for prog in ("full", "half", "third", "pact", "subclass_only"):
        assert prog in SPELLCASTING_PROGRESSIONS


def test_action_types_include_core() -> None:
    for at in ("action", "bonus_action", "reaction", "no_action"):
        assert at in ACTION_TYPES


def test_item_types_non_empty() -> None:
    for itype in ("weapon", "armor", "wondrous", "potion", "scroll"):
        assert itype in ITEM_TYPES
