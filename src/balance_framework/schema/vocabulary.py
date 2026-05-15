"""Allowed-value vocabularies for all content schemas.

These constants are the single source of truth for valid enum strings across
every content type.  The schema layer validates against them; the engine layer
relies on them for dispatch.
"""

from typing import Final

ABILITY_SCORES: Final[frozenset[str]] = frozenset({
    "STR", "DEX", "CON", "INT", "WIS", "CHA",
})

SKILLS: Final[frozenset[str]] = frozenset({
    "acrobatics", "animal_handling", "arcana", "athletics",
    "deception", "history", "insight", "intimidation", "investigation",
    "medicine", "nature", "perception", "performance", "persuasion",
    "religion", "sleight_of_hand", "stealth", "survival",
})

DAMAGE_TYPES: Final[frozenset[str]] = frozenset({
    "acid", "bludgeoning", "cold", "fire", "force", "lightning",
    "necrotic", "piercing", "poison", "psychic", "radiant",
    "slashing", "thunder",
})

CONDITIONS: Final[frozenset[str]] = frozenset({
    "blinded", "charmed", "deafened", "exhaustion", "frightened",
    "grappled", "incapacitated", "invisible", "paralyzed", "petrified",
    "poisoned", "prone", "restrained", "stunned", "unconscious",
})

ACTION_TYPES: Final[frozenset[str]] = frozenset({
    "action", "bonus_action", "reaction", "no_action",
    "special", "free_action", "legendary_action", "lair_action",
})

FEATURE_TYPES: Final[frozenset[str]] = frozenset({
    # Attack and damage modifiers
    "attack_count_modifier",
    "crit_range_modifier",
    "passive_roll_modifier",
    "passive_stat_modifier",
    # Actions
    "custom_action",
    "reaction",
    # Passive grants
    "passive_feature_grant",
    "feat_grant",
    "spell_grant",
    "skill_proficiency_grant",
    "save_proficiency",
    "weapon_mastery_selection",
    # Defensive
    "damage_resistance",
    "damage_immunity",
    "damage_vulnerability",
    "condition_resistance",
    "condition_immunity_grant",
    # Species-specific
    "sensory_feature",
    "origin_feat_grant",
    "species_ability",
    # Triggered
    "triggered_on_kill",
    "triggered_on_miss",
    "triggered_on_spell_cast",
    # Monster traits
    "scripted_trait",
    "aura",
    # Class / subclass mechanical pillars (read by character builder and engine)
    "spellcasting",
    "fighting_style",
    "hp_bonus_per_level",
    "sneak_attack",
    "extra_attack",
    "expertise",
    "channel_divinity",
    "arcane_recovery",
    "second_wind",
    "action_surge",
    "bardic_inspiration",
    "rage",
    "unarmored_defense",
    "lay_on_hands",
    "focus_points",
    "sorcery_points",
    "pact_magic",
    "wild_shape",
    # Escape hatch for novel mechanics requiring custom engine logic
    "scripted_feature",
})

HIT_DIES: Final[frozenset[str]] = frozenset({"d6", "d8", "d10", "d12"})

SPELLCASTING_PROGRESSIONS: Final[frozenset[str]] = frozenset({
    "full", "half", "third", "pact", "subclass_only",
})

MAGIC_SCHOOLS: Final[frozenset[str]] = frozenset({
    "abjuration", "conjuration", "divination", "enchantment",
    "evocation", "illusion", "necromancy", "transmutation",
})

ITEM_TYPES: Final[frozenset[str]] = frozenset({
    "weapon", "armor", "shield", "wondrous", "wand",
    "staff", "rod", "ring", "potion", "scroll", "ammunition",
})

RARITIES: Final[frozenset[str]] = frozenset({
    "common", "uncommon", "rare", "very_rare", "legendary", "artifact",
})

CREATURE_TYPES: Final[frozenset[str]] = frozenset({
    "aberration", "beast", "celestial", "construct", "dragon",
    "elemental", "fey", "fiend", "giant", "humanoid",
    "monstrosity", "ooze", "plant", "undead",
})

SIZES: Final[frozenset[str]] = frozenset({
    "tiny", "small", "medium", "large", "huge", "gargantuan",
})

FEAT_CATEGORIES: Final[frozenset[str]] = frozenset({
    "origin", "general", "fighting_style", "epic_boon",
})

INTENT_TAGS: Final[frozenset[str]] = frozenset({
    "damage", "healing", "control", "buff", "debuff",
    "utility", "movement", "information", "defense", "summon",
    "transportation", "aoe", "concentration", "ritual",
    "combat", "initiative", "awareness", "bonus_damage", "social",
})

VALID_CRS: Final[frozenset[str | int | float]] = frozenset({
    0, "1/8", "1/4", "1/2",
    *range(1, 31),
})
