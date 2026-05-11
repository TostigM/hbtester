"""Behavior profile constants and resource pool setup."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.schema.types import Feature

# ---------------------------------------------------------------------------
# Behavior profile names
# ---------------------------------------------------------------------------

MARTIAL = "martial"
HEALER = "healer"
CASTER = "caster"
ROGUE = "rogue"
SUPPORT = "support"
MONSTER_MELEE = "monster_melee"
MONSTER_CASTER = "monster_caster"
PASSIVE = "passive"

# Maps class_id -> default behavior profile
CLASS_PROFILE: dict[str, str] = {
    "fighter": MARTIAL,
    "cleric": SUPPORT,
    "wizard": CASTER,
    "rogue": ROGUE,
    "barbarian": MARTIAL,
    "bard": SUPPORT,
    "paladin": MARTIAL,
    "ranger": MARTIAL,
    "monk": MARTIAL,
    "druid": SUPPORT,
    "sorcerer": CASTER,
    "warlock": CASTER,
}

# ---------------------------------------------------------------------------
# Spell slot tables
# PHB 2024 spell slots by class level -> {slot_level: count}
# ---------------------------------------------------------------------------

_FULL_CASTER_SLOTS: dict[int, dict[str, int]] = {
    1:  {"spell_slot_1": 2},
    2:  {"spell_slot_1": 3},
    3:  {"spell_slot_1": 4, "spell_slot_2": 2},
    4:  {"spell_slot_1": 4, "spell_slot_2": 3},
    5:  {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 2},
    6:  {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3},
    7:  {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 1},
    8:  {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 2},
    9:  {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 1},
    10: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2},
    11: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2, "spell_slot_6": 1},
    12: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2, "spell_slot_6": 1},
    13: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2, "spell_slot_6": 1, "spell_slot_7": 1},
    14: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2, "spell_slot_6": 1, "spell_slot_7": 1},
    15: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2, "spell_slot_6": 1, "spell_slot_7": 1, "spell_slot_8": 1},
    16: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2, "spell_slot_6": 1, "spell_slot_7": 1, "spell_slot_8": 1},
    17: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2, "spell_slot_6": 1, "spell_slot_7": 1, "spell_slot_8": 1, "spell_slot_9": 1},
    18: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 3, "spell_slot_6": 1, "spell_slot_7": 1, "spell_slot_8": 1, "spell_slot_9": 1},
    19: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 3, "spell_slot_6": 2, "spell_slot_7": 1, "spell_slot_8": 1, "spell_slot_9": 1},
    20: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 3, "spell_slot_6": 2, "spell_slot_7": 2, "spell_slot_8": 1, "spell_slot_9": 1},
}

# Half-caster slot table (paladin, ranger): slot progression based on half class level.
_HALF_CASTER_SLOTS: dict[int, dict[str, int]] = {
    1:  {"spell_slot_1": 2},
    2:  {"spell_slot_1": 2},
    3:  {"spell_slot_1": 3},
    4:  {"spell_slot_1": 3},
    5:  {"spell_slot_1": 4, "spell_slot_2": 2},
    6:  {"spell_slot_1": 4, "spell_slot_2": 2},
    7:  {"spell_slot_1": 4, "spell_slot_2": 3},
    8:  {"spell_slot_1": 4, "spell_slot_2": 3},
    9:  {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 2},
    10: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 2},
    11: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3},
    12: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3},
    13: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 1},
    14: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 1},
    15: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 2},
    16: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 2},
    17: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 1},
    18: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 1},
    19: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2},
    20: {"spell_slot_1": 4, "spell_slot_2": 3, "spell_slot_3": 3, "spell_slot_4": 3, "spell_slot_5": 2},
}

_FULL_CASTER_CLASSES = frozenset({"cleric", "wizard", "druid", "bard", "sorcerer"})
_HALF_CASTER_CLASSES = frozenset({"paladin", "ranger"})

# Pact Magic: slots are all the same level; recover on short or long rest.
# Stored as spell_slot_N so the caster AI naturally selects the right level.
_PACT_MAGIC_SLOTS: dict[int, dict[str, int]] = {
    1:  {"spell_slot_1": 1},
    2:  {"spell_slot_1": 2},
    3:  {"spell_slot_2": 2},
    4:  {"spell_slot_2": 2},
    5:  {"spell_slot_3": 2},
    6:  {"spell_slot_3": 2},
    7:  {"spell_slot_4": 2},
    8:  {"spell_slot_4": 2},
    9:  {"spell_slot_5": 2},
    10: {"spell_slot_5": 2},
    11: {"spell_slot_5": 3},
    12: {"spell_slot_5": 3},
    13: {"spell_slot_5": 3},
    14: {"spell_slot_5": 3},
    15: {"spell_slot_5": 3},
    16: {"spell_slot_5": 3},
    17: {"spell_slot_5": 4},
    18: {"spell_slot_5": 4},
    19: {"spell_slot_5": 4},
    20: {"spell_slot_5": 4},
}

# Barbarian rage uses per long rest by level
_RAGE_USES: dict[int, int] = {
    **{lvl: 2 for lvl in range(1, 3)},
    **{lvl: 3 for lvl in range(3, 6)},
    **{lvl: 4 for lvl in range(6, 12)},
    **{lvl: 5 for lvl in range(12, 17)},
    **{lvl: 6 for lvl in range(17, 20)},
    20: 999,  # unlimited at level 20
}


def combat_stats_from_features(
    features: "list[Feature]",
    class_id: str,
    level: int,
    ability_modifiers: "dict[str, int] | None" = None,
) -> "dict":
    """Return combat stat overrides derived from active features.

    Keys: crit_threshold (int), bonus_damage_dice (list[tuple[int,int]]),
    bonus_damage_flat (int).
    """
    ability_modifiers = ability_modifiers or {}
    result: dict = {
        "crit_threshold": 20,
        "bonus_damage_dice": [],
        "bonus_damage_flat": 0,
        "frenzy_bonus_attack": False,
        "dread_ambusher": False,
        "assassinate": False,
        "has_war_priest": False,
        "sacred_weapon": False,
        "vow_of_enmity": False,
        "arcane_ward_hp": 0,
    }

    feature_ids = {f.id for f in features}

    if "superior_critical" in feature_ids:
        result["crit_threshold"] = 18
    elif "improved_critical" in feature_ids:
        result["crit_threshold"] = 19

    if "frenzy" in feature_ids:
        result["frenzy_bonus_attack"] = True
    if "dread_ambusher" in feature_ids:
        result["dread_ambusher"] = True
    if "assassinate" in feature_ids:
        result["assassinate"] = True
    if "war_priest" in feature_ids:
        result["has_war_priest"] = True
    if "sacred_weapon" in feature_ids:
        result["sacred_weapon"] = True
    if "vow_of_enmity" in feature_ids:
        result["vow_of_enmity"] = True
    if "arcane_ward" in feature_ids:
        int_mod = ability_modifiers.get("INT", 0)
        result["arcane_ward_hp"] = 2 * level + int_mod

    for f in features:
        if f.feature_type == "passive_roll_modifier" and f.body.get("modifier_type") == "bonus_damage":
            die_count = f.body.get("die_count")
            die_size = f.body.get("die_size")
            if die_count is not None and die_size is not None:
                result["bonus_damage_dice"].append((int(die_count), int(die_size)))
            else:
                stat = f.body.get("stat", "CHA")
                mod = ability_modifiers.get(stat, 0)
                if mod > 0:
                    result["bonus_damage_flat"] += mod

    return result


def spell_slots_for(class_id: str, level: int) -> dict[str, int]:
    """Return the spell slot pool dict for a caster at the given level."""
    if class_id in _FULL_CASTER_CLASSES:
        return dict(_FULL_CASTER_SLOTS.get(level, _FULL_CASTER_SLOTS[20]))
    if class_id in _HALF_CASTER_CLASSES:
        return dict(_HALF_CASTER_SLOTS.get(level, _HALF_CASTER_SLOTS[20]))
    if class_id == "warlock":
        return dict(_PACT_MAGIC_SLOTS.get(level, _PACT_MAGIC_SLOTS[20]))
    return {}


# ---------------------------------------------------------------------------
# Resource pool builder
# ---------------------------------------------------------------------------

def resources_from_features(
    features: "list[Feature]",
    class_id: str,
    level: int,
) -> dict[str, int]:
    """Build the initial resource pool dict from active features.

    Scans feature_type keys to configure class resource pools.
    """
    pools: dict[str, int] = {}

    feature_types = {f.feature_type for f in features}
    feature_ids = {f.id for f in features}

    if "second_wind" in feature_types or "second_wind" in feature_ids:
        pools["second_wind"] = 1
    if "action_surge" in feature_types or "action_surge" in feature_ids:
        pools["action_surge"] = 1 if level < 17 else 2

    if "combat_superiority" in feature_types or "combat_superiority" in feature_ids:
        if level >= 15:
            pools["superiority_dice"] = 6
        elif level >= 7:
            pools["superiority_dice"] = 5
        else:
            pools["superiority_dice"] = 4

    if "channel_divinity" in feature_types or "channel_divinity" in feature_ids:
        if level >= 18:
            pools["channel_divinity"] = 3
        elif level >= 6:
            pools["channel_divinity"] = 2
        else:
            pools["channel_divinity"] = 1

    if "arcane_recovery" in feature_types:
        pools["arcane_recovery"] = 1

    if "rage" in feature_types or "rage" in feature_ids:
        pools["rage"] = _RAGE_USES.get(level, 2)

    if "lay_on_hands" in feature_types or "lay_on_hands" in feature_ids:
        # Pool = 5 × level HP; model as that many 5-HP uses
        pools["lay_on_hands"] = level

    if "focus_points" in feature_types or "focus_points" in feature_ids:
        pools["focus_points"] = level

    if "sorcery_points" in feature_types or "sorcery_points" in feature_ids:
        pools["sorcery_points"] = level

    pools.update(spell_slots_for(class_id, level))

    return pools
