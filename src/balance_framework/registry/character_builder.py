"""Character builder — assembles a resolved Character from a CharacterBuild spec."""

from __future__ import annotations

from dataclasses import dataclass, field

from balance_framework.schema.types import Feature
from balance_framework.registry.registry import ContentRegistry

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HIT_DIE_AVERAGE: dict[str, int] = {
    "d6": 4,
    "d8": 5,
    "d10": 6,
    "d12": 7,
}

_HIT_DIE_MAX: dict[str, int] = {
    "d6": 6,
    "d8": 8,
    "d10": 10,
    "d12": 12,
}

# (base_ac, armor_category)
_ARMOR: dict[str, tuple[int, str]] = {
    "padded":          (11, "light"),
    "leather":         (11, "light"),
    "studded_leather": (12, "light"),
    "hide":            (12, "medium"),
    "chain_shirt":     (13, "medium"),
    "scale_mail":      (14, "medium"),
    "breastplate":     (14, "medium"),
    "half_plate":      (15, "medium"),
    "ring_mail":       (14, "heavy"),
    "chain_mail":      (16, "heavy"),
    "splint":          (17, "heavy"),
    "plate":           (18, "heavy"),
}

PROF_BY_LEVEL: dict[int, int] = {
    **{lvl: 2 for lvl in range(1, 5)},
    **{lvl: 3 for lvl in range(5, 9)},
    **{lvl: 4 for lvl in range(9, 13)},
    **{lvl: 5 for lvl in range(13, 17)},
    **{lvl: 6 for lvl in range(17, 21)},
}


# ---------------------------------------------------------------------------
# Input / output dataclasses
# ---------------------------------------------------------------------------


@dataclass
class CharacterBuild:
    """Declarative spec for building a character at a specific level."""

    species_id: str
    class_id: str
    background_id: str
    level: int
    # Final ability scores at the given level (post-species/background bonuses, post-ASI)
    ability_scores: dict[str, int]

    subclass_id: str | None = None
    feat_ids: list[str] = field(default_factory=list)
    equipment_ids: list[str] = field(default_factory=list)

    # Armor specification
    armor_type: str = "none"          # key into _ARMOR, or "none" / "mage_armor"
    has_shield: bool = False

    # Optional build choices that affect stats
    selected_fighting_style: str | None = None  # "defense", "archery", etc.
    uses_mage_armor: bool = False               # wizard / sorcerer unarmored with Mage Armor


@dataclass
class Character:
    """Fully resolved character stat block at a specific level."""

    build: CharacterBuild

    # Core derived stats
    hp_max: int
    ac: int
    proficiency_bonus: int
    ability_modifiers: dict[str, int]

    # Proficiencies
    saving_throw_proficiencies: frozenset[str]
    skill_proficiencies: frozenset[str]

    # Spellcasting (None for non-casters)
    spellcasting_ability: str | None
    spell_save_dc: int | None
    spell_attack_bonus: int | None

    # Class-specific combat stats
    sneak_attack_dice: int    # number of d6 (0 for non-rogues)
    extra_attack_count: int   # 0 = base, 1 = two attacks total, 2 = three, etc.

    # All features active at this level
    active_features: list[Feature]


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_character(build: CharacterBuild, registry: ContentRegistry) -> Character:
    """Assemble a Character from a CharacterBuild, resolving all stats.

    Raises:
        ReferenceError: if any referenced content ID is not in the registry.
    """
    cls = registry.get_class(build.class_id)
    species = registry.get_species(build.species_id)
    background = registry.get_background(build.background_id)
    subclass = registry.get_subclass(build.subclass_id) if build.subclass_id else None
    feats = [registry.get_feat(fid) for fid in build.feat_ids]

    prof = PROF_BY_LEVEL[build.level]
    ability_mods = {ab: _mod(score) for ab, score in build.ability_scores.items()}

    # ----------------------------------------------------------------
    # Collect active features
    # ----------------------------------------------------------------
    active: list[Feature] = []

    # Class features up to current level
    for feat_obj in cls.features:
        if feat_obj.unlock_level is None or feat_obj.unlock_level <= build.level:
            active.append(feat_obj)

    # Subclass features up to current level (only after subclass_choice_level)
    if subclass and build.level >= cls.subclass_choice_level:
        for feat_obj in subclass.features:
            if feat_obj.unlock_level is None or feat_obj.unlock_level <= build.level:
                active.append(feat_obj)

    # Species traits (always active)
    active.extend(species.traits)

    # Feat benefits
    for feat in feats:
        active.extend(feat.benefits)

    # ----------------------------------------------------------------
    # HP
    # ----------------------------------------------------------------
    con_mod = ability_mods.get("CON", 0)
    extra_hp_per_level = _sum_hp_bonus_per_level(active)
    hp = _compute_hp(cls.hit_die, build.level, con_mod, extra_hp_per_level)

    # ----------------------------------------------------------------
    # AC
    # ----------------------------------------------------------------
    dex_mod = ability_mods.get("DEX", 0)
    has_defense_style = (
        build.selected_fighting_style == "defense"
        or _has_active_fighting_style(active, "defense")
    )
    ac = _compute_ac(
        armor_type=build.armor_type,
        dex_mod=dex_mod,
        has_shield=build.has_shield,
        has_defense_style=has_defense_style,
        uses_mage_armor=build.uses_mage_armor,
    )

    # ----------------------------------------------------------------
    # Proficiencies
    # ----------------------------------------------------------------
    save_profs = frozenset(cls.saving_throw_proficiencies)
    skill_profs = frozenset(background.skill_proficiencies)

    # ----------------------------------------------------------------
    # Spellcasting
    # ----------------------------------------------------------------
    spell_ability = cls.spellcasting_ability
    if spell_ability:
        sp_mod = ability_mods.get(spell_ability, 0)
        spell_dc: int | None = 8 + prof + sp_mod
        spell_atk: int | None = prof + sp_mod
    else:
        spell_dc = None
        spell_atk = None

    # ----------------------------------------------------------------
    # Class-specific stats
    # ----------------------------------------------------------------
    sneak_dice = _compute_sneak_attack(build.class_id, build.level)
    extra_atk = _compute_extra_attack(active, build.level)

    return Character(
        build=build,
        hp_max=hp,
        ac=ac,
        proficiency_bonus=prof,
        ability_modifiers=ability_mods,
        saving_throw_proficiencies=save_profs,
        skill_proficiencies=skill_profs,
        spellcasting_ability=spell_ability,
        spell_save_dc=spell_dc,
        spell_attack_bonus=spell_atk,
        sneak_attack_dice=sneak_dice,
        extra_attack_count=extra_atk,
        active_features=active,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _mod(score: int) -> int:
    return (score - 10) // 2


def _compute_hp(hit_die: str, level: int, con_mod: int, extra_per_level: int) -> int:
    """PHB 2024 average HP: max die at level 1, average (die/2 + 1) thereafter."""
    level_1 = _HIT_DIE_MAX[hit_die] + con_mod + extra_per_level
    per_level = _HIT_DIE_AVERAGE[hit_die] + con_mod + extra_per_level
    return level_1 + (level - 1) * per_level


def _compute_ac(
    armor_type: str,
    dex_mod: int,
    has_shield: bool,
    has_defense_style: bool,
    uses_mage_armor: bool,
) -> int:
    if armor_type == "none":
        if uses_mage_armor:
            base_ac = 13 + dex_mod
            wearing_armor = False  # Mage Armor doesn't satisfy "wearing armor" for Defense
        else:
            base_ac = 10 + dex_mod
            wearing_armor = False
    else:
        base, category = _ARMOR[armor_type]
        if category == "light":
            base_ac = base + dex_mod
        elif category == "medium":
            base_ac = base + min(dex_mod, 2)
        else:
            base_ac = base
        wearing_armor = True

    if has_shield:
        base_ac += 2
    if has_defense_style and wearing_armor:
        base_ac += 1
    return base_ac


def _sum_hp_bonus_per_level(features: list[Feature]) -> int:
    """Sum ``amount`` from all hp_bonus_per_level features (e.g., Tough feat)."""
    total = 0
    for f in features:
        if f.feature_type == "hp_bonus_per_level":
            total += int(f.body.get("amount", 0))
    return total


def _has_active_fighting_style(features: list[Feature], style: str) -> bool:
    for f in features:
        if f.feature_type == "fighting_style" and f.body.get("style") == style:
            return True
    return False


def _compute_sneak_attack(class_id: str, level: int) -> int:
    if class_id != "rogue":
        return 0
    return (level + 1) // 2


def _compute_extra_attack(features: list[Feature], level: int) -> int:  # noqa: ARG001
    """Return the highest extra_attack count from active features (0 = one attack total)."""
    best = 0
    for f in features:
        if f.feature_type == "extra_attack":
            count = int(f.body.get("count", 1))
            best = max(best, count)
    return best
