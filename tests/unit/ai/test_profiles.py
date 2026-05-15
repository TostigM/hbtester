"""Unit tests for behavior profiles and resource pool builder."""

from __future__ import annotations

import pytest

from balance_framework.ai.profiles import (
    CLASS_PROFILE,
    MARTIAL, HEALER, CASTER, ROGUE, SUPPORT,
    spell_slots_for,
    resources_from_features,
    combat_stats_from_features,
)
from balance_framework.schema.types import Feature


def _feature(feature_type: str, id: str, body: dict | None = None) -> Feature:
    return Feature(feature_type=feature_type, id=id, display_name=id, body=body or {})


# ---------------------------------------------------------------------------
# CLASS_PROFILE mapping
# ---------------------------------------------------------------------------

def test_class_profile_fighter() -> None:
    assert CLASS_PROFILE["fighter"] == MARTIAL


def test_class_profile_cleric() -> None:
    assert CLASS_PROFILE["cleric"] == SUPPORT


def test_class_profile_wizard() -> None:
    assert CLASS_PROFILE["wizard"] == CASTER


def test_class_profile_rogue() -> None:
    assert CLASS_PROFILE["rogue"] == ROGUE


# ---------------------------------------------------------------------------
# spell_slots_for
# ---------------------------------------------------------------------------

def test_spell_slots_fighter_none() -> None:
    assert spell_slots_for("fighter", 5) == {}


def test_spell_slots_wizard_level1() -> None:
    slots = spell_slots_for("wizard", 1)
    assert slots["spell_slot_1"] == 2
    assert "spell_slot_2" not in slots


def test_spell_slots_cleric_level5() -> None:
    slots = spell_slots_for("cleric", 5)
    assert slots["spell_slot_1"] == 4
    assert slots["spell_slot_2"] == 3
    assert slots["spell_slot_3"] == 2


def test_spell_slots_wizard_level9() -> None:
    slots = spell_slots_for("wizard", 9)
    assert slots.get("spell_slot_5") == 1


# ---------------------------------------------------------------------------
# resources_from_features
# ---------------------------------------------------------------------------

def test_resources_fighter_features() -> None:
    features = [
        _feature("second_wind", "second_wind"),
        _feature("action_surge", "action_surge"),
    ]
    pools = resources_from_features(features, "fighter", 5)
    assert pools["second_wind"] == 1
    assert pools["action_surge"] == 1
    assert "spell_slot_1" not in pools


def test_resources_battle_master_has_superiority_dice() -> None:
    features = [
        _feature("second_wind", "second_wind"),
        _feature("scripted_feature", "combat_superiority"),
    ]
    pools = resources_from_features(features, "fighter", 5)
    assert pools["superiority_dice"] == 4


def test_resources_battle_master_level7_has_5_dice() -> None:
    features = [_feature("scripted_feature", "combat_superiority")]
    pools = resources_from_features(features, "fighter", 7)
    assert pools["superiority_dice"] == 5


def test_resources_cleric_has_spell_slots_and_channel() -> None:
    features = [_feature("channel_divinity", "channel_divinity")]
    pools = resources_from_features(features, "cleric", 5)
    assert pools["channel_divinity"] == 1
    assert pools["spell_slot_1"] == 4
    assert pools["spell_slot_3"] == 2


def test_resources_wizard_has_arcane_recovery() -> None:
    features = [_feature("arcane_recovery", "arcane_recovery")]
    pools = resources_from_features(features, "wizard", 5)
    assert pools["arcane_recovery"] == 1
    assert pools["spell_slot_1"] == 4


def test_resources_rogue_empty() -> None:
    pools = resources_from_features([], "rogue", 5)
    assert pools == {}


def test_resources_action_surge_doubles_at_level_17() -> None:
    features = [_feature("action_surge", "action_surge")]
    pools = resources_from_features(features, "fighter", 17)
    assert pools["action_surge"] == 2


# ---------------------------------------------------------------------------
# combat_stats_from_features
# ---------------------------------------------------------------------------

def test_combat_stats_default_crit_threshold() -> None:
    stats = combat_stats_from_features([], "fighter", 5)
    assert stats["crit_threshold"] == 20
    assert stats["bonus_damage_dice"] == []
    assert stats["bonus_damage_flat"] == 0


def test_combat_stats_improved_critical() -> None:
    features = [_feature("passive_feature_grant", "improved_critical")]
    stats = combat_stats_from_features(features, "fighter", 5)
    assert stats["crit_threshold"] == 19


def test_combat_stats_superior_critical_overrides_improved() -> None:
    features = [
        _feature("passive_feature_grant", "improved_critical"),
        _feature("passive_feature_grant", "superior_critical"),
    ]
    stats = combat_stats_from_features(features, "fighter", 15)
    assert stats["crit_threshold"] == 18


def test_combat_stats_bonus_damage_dice_from_hunters_prey() -> None:
    features = [_feature(
        "passive_roll_modifier", "hunters_prey",
        body={"modifier_type": "bonus_damage", "die_count": 1, "die_size": 8},
    )]
    stats = combat_stats_from_features(features, "ranger", 5)
    assert stats["bonus_damage_dice"] == [(1, 8)]


def test_combat_stats_bonus_damage_flat_from_elemental_affinity() -> None:
    features = [_feature(
        "passive_roll_modifier", "elemental_affinity",
        body={"modifier_type": "bonus_damage"},
    )]
    ability_mods = {"CHA": 3}
    stats = combat_stats_from_features(features, "sorcerer", 6, ability_modifiers=ability_mods)
    assert stats["bonus_damage_flat"] == 3


def test_combat_stats_bonus_damage_flat_zero_if_no_cha() -> None:
    features = [_feature(
        "passive_roll_modifier", "elemental_affinity",
        body={"modifier_type": "bonus_damage"},
    )]
    stats = combat_stats_from_features(features, "sorcerer", 6, ability_modifiers={"CHA": 0})
    assert stats["bonus_damage_flat"] == 0
