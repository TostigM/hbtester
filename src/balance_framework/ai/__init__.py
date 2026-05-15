"""AI layer — behavior heuristics and action selector dispatch."""

from balance_framework.ai.decision import select_actions
from balance_framework.ai.profiles import (
    CLASS_PROFILE,
    MARTIAL, HEALER, CASTER, ROGUE, MONSTER_MELEE, PASSIVE,
    spell_slots_for,
    resources_from_features,
)

__all__ = [
    "select_actions",
    "CLASS_PROFILE",
    "MARTIAL", "HEALER", "CASTER", "ROGUE", "MONSTER_MELEE", "PASSIVE",
    "spell_slots_for",
    "resources_from_features",
]
