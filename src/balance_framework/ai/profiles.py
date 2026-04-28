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
MONSTER_MELEE = "monster_melee"
PASSIVE = "passive"

# Maps class_id -> default behavior profile
CLASS_PROFILE: dict[str, str] = {
    "fighter": MARTIAL,
    "cleric": HEALER,
    "wizard": CASTER,
    "rogue": ROGUE,
    "barbarian": MARTIAL,
    "bard": HEALER,
}

# ---------------------------------------------------------------------------
# Spell slot tables (full casters: cleric, wizard)
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

_FULL_CASTER_CLASSES = frozenset({"cleric", "wizard", "druid", "bard", "sorcerer"})

# Barbarian rage uses per long rest by level
_RAGE_USES: dict[int, int] = {
    **{lvl: 2 for lvl in range(1, 3)},
    **{lvl: 3 for lvl in range(3, 6)},
    **{lvl: 4 for lvl in range(6, 12)},
    **{lvl: 5 for lvl in range(12, 17)},
    **{lvl: 6 for lvl in range(17, 20)},
    20: 999,  # unlimited at level 20
}


def spell_slots_for(class_id: str, level: int) -> dict[str, int]:
    """Return the spell slot pool dict for a full-caster at the given level."""
    if class_id not in _FULL_CASTER_CLASSES:
        return {}
    return dict(_FULL_CASTER_SLOTS.get(level, _FULL_CASTER_SLOTS[20]))


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

    pools.update(spell_slots_for(class_id, level))

    return pools
