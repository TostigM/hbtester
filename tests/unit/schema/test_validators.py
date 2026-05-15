"""Unit tests for schema validators — one per content type, covering valid input,
missing required fields, invalid vocabulary, and type coercion."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from balance_framework.schema.exceptions import SchemaViolation, VocabularyViolation
from balance_framework.schema.validators import (
    validate_background,
    validate_class,
    validate_feat,
    validate_magic_item,
    validate_monster,
    validate_species,
    validate_spell,
    validate_subclass,
)

# ---------------------------------------------------------------------------
# Fixtures — minimal valid dicts for each content type
# ---------------------------------------------------------------------------

VALID_SUBCLASS: dict[str, Any] = {
    "schema_version": "0.1",
    "content_type": "subclass",
    "id": "champion",
    "display_name": "Champion",
    "source": "PHB_2024",
    "author": "Wizards of the Coast",
    "parent_class": "fighter",
    "features": [
        {
            "id": "improved_critical",
            "unlock_level": 3,
            "display_name": "Improved Critical",
            "feature_type": "crit_range_modifier",
            "body": {"new_crit_threshold": 19, "applies_to": "weapon_and_unarmed_attacks"},
        }
    ],
    "resource_pools": [],
    "spell_list": [],
}

VALID_CLASS: dict[str, Any] = {
    "schema_version": "0.1",
    "content_type": "class",
    "id": "fighter",
    "display_name": "Fighter",
    "source": "PHB_2024",
    "author": "Wizards of the Coast",
    "hit_die": "d10",
    "primary_ability_options": ["STR", "DEX"],
    "saving_throw_proficiencies": ["STR", "CON"],
}

VALID_SPECIES: dict[str, Any] = {
    "schema_version": "0.1",
    "content_type": "species",
    "id": "human",
    "display_name": "Human",
    "source": "PHB_2024",
    "author": "Wizards of the Coast",
    "creature_type": "humanoid",
    "size": "medium",
    "speed": {"walk": 30},
}

VALID_BACKGROUND: dict[str, Any] = {
    "schema_version": "0.1",
    "content_type": "background",
    "id": "soldier",
    "display_name": "Soldier",
    "source": "PHB_2024",
    "author": "Wizards of the Coast",
    "ability_score_increases": {
        "mode": "plus_2_plus_1",
        "eligible_abilities": ["STR", "CON", "CHA"],
    },
    "skill_proficiencies": ["athletics", "intimidation"],
    "tool_proficiency": "gaming_set",
    "origin_feat": "savage_attacker",
}

VALID_SPELL: dict[str, Any] = {
    "schema_version": "0.1",
    "content_type": "spell",
    "id": "fireball",
    "display_name": "Fireball",
    "source": "PHB_2024",
    "author": "Wizards of the Coast",
    "level": 3,
    "school": "evocation",
    "casting_time": "action",
    "range": "150_feet",
    "components": {"verbal": True, "somatic": True, "material": True,
                   "material_description": "bat guano and sulfur"},
    "duration": "instantaneous",
    "concentration": False,
}

VALID_MAGIC_ITEM: dict[str, Any] = {
    "schema_version": "0.1",
    "content_type": "magic_item",
    "id": "plus_one_longsword",
    "display_name": "+1 Longsword",
    "source": "DMG_2024",
    "author": "Wizards of the Coast",
    "item_type": "weapon",
    "subtype": "longsword",
    "rarity": "uncommon",
    "requires_attunement": False,
}

VALID_MONSTER: dict[str, Any] = {
    "schema_version": "0.1",
    "content_type": "monster",
    "id": "orc",
    "display_name": "Orc",
    "source": "MM_2025",
    "author": "Wizards of the Coast",
    "creature_type": "humanoid",
    "size": "medium",
    "ac": 13,
    "hp": {"average": 15, "formula": "2d8 + 6"},
    "speed": {"walk": 30},
    "abilities": {"STR": 16, "DEX": 12, "CON": 16, "INT": 7, "WIS": 11, "CHA": 10},
    "challenge_rating": "1/2",
    "proficiency_bonus": 2,
}

VALID_FEAT: dict[str, Any] = {
    "schema_version": "0.1",
    "content_type": "feat",
    "id": "alert",
    "display_name": "Alert",
    "source": "PHB_2024",
    "author": "Wizards of the Coast",
    "feat_category": "origin",
    "benefits": [
        {
            "id": "alert_initiative",
            "display_name": "Initiative Bonus",
            "feature_type": "passive_roll_modifier",
            "body": {"roll_type": "initiative", "amount": "proficiency_bonus"},
        }
    ],
}


# ---------------------------------------------------------------------------
# Subclass tests
# ---------------------------------------------------------------------------


def test_subclass_valid() -> None:
    result = validate_subclass(VALID_SUBCLASS)
    assert result.id == "champion"
    assert result.parent_class == "fighter"
    assert len(result.features) == 1
    assert result.features[0].feature_type == "crit_range_modifier"


def test_subclass_missing_required_field() -> None:
    bad = {k: v for k, v in VALID_SUBCLASS.items() if k != "parent_class"}
    with pytest.raises(SchemaViolation):
        validate_subclass(bad)


def test_subclass_invalid_feature_type() -> None:
    bad = {**VALID_SUBCLASS}
    bad["features"] = [
        {**VALID_SUBCLASS["features"][0], "feature_type": "not_a_real_type"}
    ]
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_subclass(bad)


def test_subclass_wrong_content_type() -> None:
    bad = {**VALID_SUBCLASS, "content_type": "class"}
    with pytest.raises(SchemaViolation):
        validate_subclass(bad)


# ---------------------------------------------------------------------------
# Class tests
# ---------------------------------------------------------------------------


def test_class_valid() -> None:
    result = validate_class(VALID_CLASS)
    assert result.id == "fighter"
    assert result.hit_die == "d10"


def test_class_missing_required_field() -> None:
    bad = {k: v for k, v in VALID_CLASS.items() if k != "hit_die"}
    with pytest.raises(SchemaViolation):
        validate_class(bad)


def test_class_invalid_hit_die() -> None:
    bad = {**VALID_CLASS, "hit_die": "d7"}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_class(bad)


def test_class_saves_must_be_two() -> None:
    bad = {**VALID_CLASS, "saving_throw_proficiencies": ["STR"]}
    with pytest.raises(SchemaViolation):
        validate_class(bad)


def test_class_invalid_ability_in_saves() -> None:
    bad = {**VALID_CLASS, "saving_throw_proficiencies": ["STR", "LUCK"]}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_class(bad)


# ---------------------------------------------------------------------------
# Species tests
# ---------------------------------------------------------------------------


def test_species_valid() -> None:
    result = validate_species(VALID_SPECIES)
    assert result.id == "human"
    assert result.creature_type == "humanoid"


def test_species_missing_required_field() -> None:
    bad = {k: v for k, v in VALID_SPECIES.items() if k != "creature_type"}
    with pytest.raises(SchemaViolation):
        validate_species(bad)


def test_species_invalid_creature_type() -> None:
    bad = {**VALID_SPECIES, "creature_type": "robot"}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_species(bad)


def test_species_invalid_size() -> None:
    bad = {**VALID_SPECIES, "size": "colossal"}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_species(bad)


# ---------------------------------------------------------------------------
# Background tests
# ---------------------------------------------------------------------------


def test_background_valid() -> None:
    result = validate_background(VALID_BACKGROUND)
    assert result.id == "soldier"
    assert result.origin_feat == "savage_attacker"


def test_background_missing_required_field() -> None:
    bad = {k: v for k, v in VALID_BACKGROUND.items() if k != "origin_feat"}
    with pytest.raises(SchemaViolation):
        validate_background(bad)


def test_background_invalid_skill() -> None:
    bad = {**VALID_BACKGROUND, "skill_proficiencies": ["athletics", "prestidigitation"]}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_background(bad)


def test_background_wrong_skill_count() -> None:
    bad = {**VALID_BACKGROUND, "skill_proficiencies": ["athletics"]}
    with pytest.raises(SchemaViolation):
        validate_background(bad)


def test_background_type_coercion_skills_string_rejected() -> None:
    bad = {**VALID_BACKGROUND, "skill_proficiencies": "athletics"}
    with pytest.raises(SchemaViolation):
        validate_background(bad)


# ---------------------------------------------------------------------------
# Spell tests
# ---------------------------------------------------------------------------


def test_spell_valid() -> None:
    result = validate_spell(VALID_SPELL)
    assert result.id == "fireball"
    assert result.level == 3
    assert result.school == "evocation"


def test_spell_missing_required_field() -> None:
    bad = {k: v for k, v in VALID_SPELL.items() if k != "school"}
    with pytest.raises(SchemaViolation):
        validate_spell(bad)


def test_spell_invalid_school() -> None:
    bad = {**VALID_SPELL, "school": "pyromancy"}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_spell(bad)


def test_spell_level_out_of_range() -> None:
    bad = {**VALID_SPELL, "level": 10}
    with pytest.raises(SchemaViolation):
        validate_spell(bad)


def test_spell_concentration_requires_matching_duration() -> None:
    bad = {**VALID_SPELL, "concentration": True, "duration": "1_minute"}
    with pytest.raises(SchemaViolation):
        validate_spell(bad)


def test_spell_cantrip_no_upcast_scaling() -> None:
    bad = {
        **VALID_SPELL,
        "level": 0,
        "upcast_scaling": [{"slot_level": 2, "changes": {}}],
    }
    with pytest.raises(SchemaViolation):
        validate_spell(bad)


def test_spell_type_coercion_level_string() -> None:
    # Pydantic v2 coerces "3" -> 3 for int fields by default in lax mode;
    # we verify the model accepts the result is an int either way.
    data = {**VALID_SPELL, "level": "3"}
    result = validate_spell(data)
    assert result.level == 3


# ---------------------------------------------------------------------------
# Magic Item tests
# ---------------------------------------------------------------------------


def test_magic_item_valid() -> None:
    result = validate_magic_item(VALID_MAGIC_ITEM)
    assert result.id == "plus_one_longsword"
    assert result.rarity == "uncommon"


def test_magic_item_missing_required_field() -> None:
    bad = {k: v for k, v in VALID_MAGIC_ITEM.items() if k != "rarity"}
    with pytest.raises(SchemaViolation):
        validate_magic_item(bad)


def test_magic_item_invalid_item_type() -> None:
    bad = {**VALID_MAGIC_ITEM, "item_type": "trinket"}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_magic_item(bad)


def test_magic_item_invalid_rarity() -> None:
    bad = {**VALID_MAGIC_ITEM, "rarity": "mythic"}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_magic_item(bad)


# ---------------------------------------------------------------------------
# Monster tests
# ---------------------------------------------------------------------------


def test_monster_valid() -> None:
    result = validate_monster(VALID_MONSTER)
    assert result.id == "orc"
    assert result.challenge_rating == "1/2"
    assert result.abilities.STR == 16


def test_monster_missing_required_field() -> None:
    bad = {k: v for k, v in VALID_MONSTER.items() if k != "ac"}
    with pytest.raises(SchemaViolation):
        validate_monster(bad)


def test_monster_invalid_creature_type() -> None:
    bad = {**VALID_MONSTER, "creature_type": "magical_beast"}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_monster(bad)


def test_monster_invalid_damage_immunity() -> None:
    bad = {**VALID_MONSTER, "damage_immunities": ["void"]}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_monster(bad)


# ---------------------------------------------------------------------------
# Feat tests
# ---------------------------------------------------------------------------


def test_feat_valid() -> None:
    result = validate_feat(VALID_FEAT)
    assert result.id == "alert"
    assert result.feat_category == "origin"


def test_feat_missing_required_field() -> None:
    bad = {k: v for k, v in VALID_FEAT.items() if k != "feat_category"}
    with pytest.raises(SchemaViolation):
        validate_feat(bad)


def test_feat_invalid_category() -> None:
    bad = {**VALID_FEAT, "feat_category": "legendary"}
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_feat(bad)


def test_feat_invalid_benefit_feature_type() -> None:
    bad = {**VALID_FEAT}
    bad["benefits"] = [
        {
            "id": "bad_feat",
            "display_name": "Bad",
            "feature_type": "definitely_not_valid",
            "body": {},
        }
    ]
    with pytest.raises((SchemaViolation, VocabularyViolation)):
        validate_feat(bad)


# ---------------------------------------------------------------------------
# Champion example YAML (M1 exit gate: the canonical example must validate)
# ---------------------------------------------------------------------------


def test_champion_example_yaml_validates() -> None:
    yaml_path = Path("docs/authoring_guides/champion_fighter_example.yaml")
    assert yaml_path.exists(), f"Champion example not found at {yaml_path}"
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    result = validate_subclass(data)
    assert result.id == "champion"
    assert result.parent_class == "fighter"
    assert len(result.features) == 6
