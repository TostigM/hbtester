"""Pydantic models for all seven content types.

The ``body`` field on Feature (and similar free-form dicts) is intentionally
typed as ``dict[str, Any]``.  The engine layer interprets the body based on
``feature_type``; the schema layer only validates that ``feature_type`` is a
known vocabulary value, not the internal structure of each body variant.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from balance_framework.schema.vocabulary import (
    ABILITY_SCORES,
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


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class Feature(BaseModel):
    """A single feature, trait, or benefit entry used across all content types."""

    id: str
    display_name: str
    feature_type: str
    body: dict[str, Any] = Field(default_factory=dict)
    unlock_level: int | None = None
    scaling: list[dict[str, Any]] = Field(default_factory=list)
    flavor: str | None = None
    score: float | None = None  # species traits carry a point-budget score

    @field_validator("feature_type")
    @classmethod
    def _validate_feature_type(cls, v: str) -> str:
        if v not in FEATURE_TYPES:
            raise ValueError(
                f"[VOCAB] Unknown feature_type {v!r}. "
                f"Valid types: {sorted(FEATURE_TYPES)}"
            )
        return v


class ResourcePool(BaseModel):
    """A named resource pool defined by a class or subclass."""

    id: str
    display_name: str
    max_size: int
    refresh: str
    die_size: str | None = None
    partial_refresh: list[dict[str, Any]] = Field(default_factory=list)
    scaling: list[dict[str, Any]] = Field(default_factory=list)
    gated_by_subclass: str | None = None


class ContentBase(BaseModel):
    """Fields shared by every content type."""

    schema_version: str
    content_type: str
    id: str
    display_name: str
    source: str
    version: str | None = None
    author: str
    flavor_text: str | None = None


# ---------------------------------------------------------------------------
# Class
# ---------------------------------------------------------------------------


class Class(ContentBase):
    """A base class definition (Fighter, Cleric, Wizard, etc.)."""

    content_type: Literal["class"]
    hit_die: str
    primary_ability_options: list[str]
    saving_throw_proficiencies: list[str]
    spellcasting_ability: str | None = None
    spellcasting_progression: str | None = None
    subclass_choice_level: int = 3
    starting_proficiencies: dict[str, Any] = Field(default_factory=dict)
    starting_equipment: dict[str, Any] = Field(default_factory=dict)
    features: list[Feature] = Field(default_factory=list)
    resource_pools: list[ResourcePool] = Field(default_factory=list)
    progression_table: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("hit_die")
    @classmethod
    def _validate_hit_die(cls, v: str) -> str:
        if v not in HIT_DIES:
            raise ValueError(
                f"[VOCAB] Invalid hit_die {v!r}. Must be one of: {sorted(HIT_DIES)}"
            )
        return v

    @field_validator("saving_throw_proficiencies")
    @classmethod
    def _validate_saves(cls, v: list[str]) -> list[str]:
        if len(v) != 2:
            raise ValueError(
                f"saving_throw_proficiencies must have exactly 2 entries, got {len(v)}"
            )
        for ability in v:
            if ability not in ABILITY_SCORES:
                raise ValueError(
                    f"[VOCAB] Unknown ability score {ability!r} in saving_throw_proficiencies"
                )
        return v

    @field_validator("primary_ability_options")
    @classmethod
    def _validate_primary_abilities(cls, v: list[str]) -> list[str]:
        for ability in v:
            if ability not in ABILITY_SCORES:
                raise ValueError(
                    f"[VOCAB] Unknown ability score {ability!r} in primary_ability_options"
                )
        return v

    @field_validator("spellcasting_progression")
    @classmethod
    def _validate_spell_progression(cls, v: str | None) -> str | None:
        if v is not None and v not in SPELLCASTING_PROGRESSIONS:
            raise ValueError(
                f"[VOCAB] Invalid spellcasting_progression {v!r}. "
                f"Must be one of: {sorted(SPELLCASTING_PROGRESSIONS)}"
            )
        return v


# ---------------------------------------------------------------------------
# Subclass
# ---------------------------------------------------------------------------


class Subclass(ContentBase):
    """A subclass definition (Battle Master, Life Domain, Champion, etc.)."""

    content_type: Literal["subclass"]
    parent_class: str
    features: list[Feature] = Field(default_factory=list)
    resource_pools: list[ResourcePool] = Field(default_factory=list)
    spell_list: list[str] = Field(default_factory=list)
    behavior_hints: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    complexity_rating: str | None = None


# ---------------------------------------------------------------------------
# Species
# ---------------------------------------------------------------------------


class ScalingTrait(BaseModel):
    """A trait granted to a species at a specific character level."""

    at_level: int
    trait: str
    feature_type: str
    body: dict[str, Any] = Field(default_factory=dict)
    score_addition: float = 0.0

    @field_validator("feature_type")
    @classmethod
    def _validate_feature_type(cls, v: str) -> str:
        if v not in FEATURE_TYPES:
            raise ValueError(f"[VOCAB] Unknown feature_type {v!r}")
        return v


class Species(ContentBase):
    """A species definition (Human, Elf, Dwarf, etc.)."""

    content_type: Literal["species"]
    creature_type: str
    size: str
    speed: dict[str, int]
    traits: list[Feature] = Field(default_factory=list)
    total_trait_score: float | None = None
    lineage_options: dict[str, Any] = Field(default_factory=dict)
    scaling_traits: list[ScalingTrait] = Field(default_factory=list)

    @field_validator("creature_type")
    @classmethod
    def _validate_creature_type(cls, v: str) -> str:
        if v not in CREATURE_TYPES:
            raise ValueError(f"[VOCAB] Unknown creature_type {v!r}")
        return v

    @field_validator("size")
    @classmethod
    def _validate_size(cls, v: str) -> str:
        if v not in SIZES:
            raise ValueError(f"[VOCAB] Unknown size {v!r}")
        return v


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------


class AbilityScoreIncreases(BaseModel):
    """The ASI block for a background (2024 rules: backgrounds grant +2/+1 or +1/+1/+1)."""

    mode: str
    eligible_abilities: list[str]

    @field_validator("eligible_abilities")
    @classmethod
    def _validate_abilities(cls, v: list[str]) -> list[str]:
        for ability in v:
            if ability not in ABILITY_SCORES:
                raise ValueError(f"[VOCAB] Unknown ability score {ability!r}")
        return v


class Background(ContentBase):
    """A background definition (Soldier, Sage, Acolyte, Charlatan, etc.)."""

    content_type: Literal["background"]
    ability_score_increases: AbilityScoreIncreases
    skill_proficiencies: list[str]
    tool_proficiency: str
    origin_feat: str
    starting_equipment: list[str] = Field(default_factory=list)

    @field_validator("skill_proficiencies")
    @classmethod
    def _validate_skills(cls, v: list[str]) -> list[str]:
        if len(v) != 2:
            raise ValueError(
                f"skill_proficiencies must have exactly 2 entries, got {len(v)}"
            )
        for skill in v:
            if skill not in SKILLS:
                raise ValueError(f"[VOCAB] Unknown skill {skill!r}")
        return v


# ---------------------------------------------------------------------------
# Spell
# ---------------------------------------------------------------------------


class SpellComponents(BaseModel):
    """Verbal, somatic, and material components of a spell."""

    verbal: bool = False
    somatic: bool = False
    material: bool = False
    material_description: str | None = None
    material_cost_gp: int = 0
    material_consumed: bool = False


class Spell(ContentBase):
    """A spell definition (Fireball, Cure Wounds, Bless, Hold Person, etc.)."""

    content_type: Literal["spell"]
    level: int
    school: str
    casting_time: str
    range: str
    components: SpellComponents
    duration: str
    concentration: bool = False
    ritual: bool = False
    class_lists: list[str] = Field(default_factory=list)
    intent_tags: list[str] = Field(default_factory=list)
    effects: list[dict[str, Any]] = Field(default_factory=list)
    area_of_effect: dict[str, Any] | None = None
    target: dict[str, Any] = Field(default_factory=dict)
    upcast_scaling: list[dict[str, Any]] = Field(default_factory=list)
    character_level_scaling: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("level")
    @classmethod
    def _validate_level(cls, v: int) -> int:
        if not 0 <= v <= 9:
            raise ValueError(f"Spell level must be 0-9, got {v}")
        return v

    @field_validator("school")
    @classmethod
    def _validate_school(cls, v: str) -> str:
        if v not in MAGIC_SCHOOLS:
            raise ValueError(f"[VOCAB] Unknown magic school {v!r}")
        return v

    @model_validator(mode="after")
    def _validate_concentration_duration(self) -> "Spell":
        if self.concentration and not self.duration.startswith("concentration"):
            raise ValueError(
                "concentration=true requires duration starting with 'concentration_'"
            )
        return self

    @model_validator(mode="after")
    def _validate_cantrip_vs_leveled_scaling(self) -> "Spell":
        if self.level == 0 and self.upcast_scaling:
            raise ValueError("Cantrips (level 0) must not have upcast_scaling")
        if self.level > 0 and self.character_level_scaling:
            raise ValueError("Leveled spells must not have character_level_scaling")
        return self


# ---------------------------------------------------------------------------
# Magic Item
# ---------------------------------------------------------------------------


class MagicItem(ContentBase):
    """A magic item definition (+1 Sword, Flame Tongue, Cloak of Protection, etc.)."""

    content_type: Literal["magic_item"]
    item_type: str
    subtype: str | None = None
    rarity: str
    requires_attunement: bool = False
    attunement_restriction: str | None = None
    consumable: bool = False
    base_item_stats: dict[str, Any] = Field(default_factory=dict)
    passive_modifiers: list[dict[str, Any]] = Field(default_factory=list)
    active_abilities: list[dict[str, Any]] = Field(default_factory=list)
    charges: dict[str, Any] | None = None
    testing_category: str | None = None
    intent_tags: list[str] = Field(default_factory=list)

    @field_validator("item_type")
    @classmethod
    def _validate_item_type(cls, v: str) -> str:
        if v not in ITEM_TYPES:
            raise ValueError(f"[VOCAB] Unknown item_type {v!r}")
        return v

    @field_validator("rarity")
    @classmethod
    def _validate_rarity(cls, v: str) -> str:
        if v not in RARITIES:
            raise ValueError(f"[VOCAB] Unknown rarity {v!r}")
        return v


# ---------------------------------------------------------------------------
# Monster
# ---------------------------------------------------------------------------


class MonsterAbilities(BaseModel):
    """The six ability scores for a monster stat block."""

    STR: int
    DEX: int
    CON: int
    INT: int
    WIS: int
    CHA: int


class Monster(ContentBase):
    """A monster stat block (Orc, Young Red Dragon, Adult Red Dragon, etc.)."""

    content_type: Literal["monster"]
    creature_type: str
    size: str
    subtype: str | None = None
    alignment: str | None = None
    ac: int
    ac_source: str | None = None
    hp: dict[str, Any]
    speed: dict[str, int]
    abilities: MonsterAbilities
    saving_throw_proficiencies: list[str] = Field(default_factory=list)
    skill_proficiencies: list[dict[str, Any]] = Field(default_factory=list)
    senses: dict[str, Any] = Field(default_factory=dict)
    languages: list[str] = Field(default_factory=list)
    challenge_rating: str | int | float
    proficiency_bonus: int
    damage_resistances: list[str] = Field(default_factory=list)
    damage_immunities: list[str] = Field(default_factory=list)
    damage_vulnerabilities: list[str] = Field(default_factory=list)
    condition_immunities: list[str] = Field(default_factory=list)
    traits: list[Feature] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    bonus_actions: list[dict[str, Any]] = Field(default_factory=list)
    reactions: list[dict[str, Any]] = Field(default_factory=list)
    legendary_actions: dict[str, Any] | None = None
    legendary_resistance: dict[str, Any] | None = None
    lair_actions: list[dict[str, Any]] = Field(default_factory=list)
    regional_effects: dict[str, Any] | None = None
    spellcasting: dict[str, Any] | None = None
    behavior_hints: dict[str, Any] = Field(default_factory=dict)

    @field_validator("creature_type")
    @classmethod
    def _validate_creature_type(cls, v: str) -> str:
        if v not in CREATURE_TYPES:
            raise ValueError(f"[VOCAB] Unknown creature_type {v!r}")
        return v

    @field_validator("size")
    @classmethod
    def _validate_size(cls, v: str) -> str:
        if v not in SIZES:
            raise ValueError(f"[VOCAB] Unknown size {v!r}")
        return v

    @field_validator("damage_immunities", "damage_resistances", "damage_vulnerabilities")
    @classmethod
    def _validate_damage_types(cls, v: list[str]) -> list[str]:
        for dtype in v:
            if dtype not in DAMAGE_TYPES:
                raise ValueError(f"[VOCAB] Unknown damage type {dtype!r}")
        return v


# ---------------------------------------------------------------------------
# Feat
# ---------------------------------------------------------------------------


class FeatPrerequisites(BaseModel):
    """Prerequisites that must be met before a feat can be taken."""

    min_level: int = 1
    ability_score_minimums: dict[str, int] = Field(default_factory=dict)
    class_restrictions: list[str] = Field(default_factory=list)
    other_prerequisites: list[str] = Field(default_factory=list)


class Feat(ContentBase):
    """A feat or Epic Boon definition (Alert, War Caster, Boon of Combat Prowess, etc.)."""

    content_type: Literal["feat"]
    feat_category: str
    prerequisites: FeatPrerequisites = Field(default_factory=FeatPrerequisites)
    ability_score_increase: dict[str, Any] | None = None
    benefits: list[Feature] = Field(default_factory=list)
    repeatable: bool = False
    repeatable_condition: str | None = None
    intent_tags: list[str] = Field(default_factory=list)

    @field_validator("feat_category")
    @classmethod
    def _validate_feat_category(cls, v: str) -> str:
        if v not in FEAT_CATEGORIES:
            raise ValueError(f"[VOCAB] Unknown feat_category {v!r}")
        return v
