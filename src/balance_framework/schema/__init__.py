"""Schema validation layer — Layer 1 of the balance framework.

Public API:
  Types:       Class, Subclass, Species, Background, Spell, MagicItem, Monster, Feat
  Validators:  validate_class, validate_subclass, validate_species, validate_background,
               validate_spell, validate_magic_item, validate_monster, validate_feat
  Exceptions:  ValidationError, SchemaViolation, VocabularyViolation, ReferenceError
  Vocabulary:  FEATURE_TYPES, ACTION_TYPES, DAMAGE_TYPES, CONDITIONS, ABILITY_SCORES, SKILLS
"""

from balance_framework.schema.exceptions import (
    ReferenceError,
    SchemaViolation,
    ValidationError,
    VocabularyViolation,
)
from balance_framework.schema.types import (
    Background,
    Class,
    ContentBase,
    Feat,
    Feature,
    MagicItem,
    Monster,
    ResourcePool,
    Species,
    Spell,
    Subclass,
)
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
from balance_framework.schema.vocabulary import (
    ABILITY_SCORES,
    ACTION_TYPES,
    CONDITIONS,
    CREATURE_TYPES,
    DAMAGE_TYPES,
    FEAT_CATEGORIES,
    FEATURE_TYPES,
    HIT_DIES,
    INTENT_TAGS,
    ITEM_TYPES,
    MAGIC_SCHOOLS,
    RARITIES,
    SIZES,
    SKILLS,
    SPELLCASTING_PROGRESSIONS,
)

__all__ = [
    # Exceptions
    "ValidationError",
    "SchemaViolation",
    "VocabularyViolation",
    "ReferenceError",
    # Types
    "ContentBase",
    "Feature",
    "ResourcePool",
    "Class",
    "Subclass",
    "Species",
    "Background",
    "Spell",
    "MagicItem",
    "Monster",
    "Feat",
    # Validators
    "validate_class",
    "validate_subclass",
    "validate_species",
    "validate_background",
    "validate_spell",
    "validate_magic_item",
    "validate_monster",
    "validate_feat",
    # Vocabulary
    "FEATURE_TYPES",
    "ACTION_TYPES",
    "DAMAGE_TYPES",
    "CONDITIONS",
    "ABILITY_SCORES",
    "SKILLS",
    "CREATURE_TYPES",
    "SIZES",
    "FEAT_CATEGORIES",
    "HIT_DIES",
    "ITEM_TYPES",
    "RARITIES",
    "MAGIC_SCHOOLS",
    "SPELLCASTING_PROGRESSIONS",
    "INTENT_TAGS",
]
