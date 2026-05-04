"""Shared scenario-factory helpers for all comparison harnesses."""

from __future__ import annotations

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice


def standard_goblin(id: str) -> CombatantState:
    return CombatantState(
        id=id, display_name=f"Goblin {id}",
        team="enemies",
        hp_max=7, hp_current=7, ac=15,
        proficiency_bonus=2,
        ability_modifiers={"STR": -1, "DEX": 2, "CON": 0},
        extra_attack_count=1,
        behavior_profile="monster_melee",
    )


def monster_combatant(monster_id: str, combatant_id: str, registry: object) -> CombatantState:
    """Build a CombatantState from a monster in the registry."""
    from balance_framework.registry.registry import ContentRegistry
    assert isinstance(registry, ContentRegistry)
    monster = registry.get_monster(monster_id)
    return CombatantState.from_monster(monster, combatant_id)


def default_enemy_band(count: int = 2) -> list[CombatantState]:
    return [standard_goblin(f"g{i}") for i in range(count)]


def monster_enemy_band(monster_id: str, count: int, registry: object) -> list[CombatantState]:
    """Build a band of identical monsters from the registry."""
    return [monster_combatant(monster_id, f"{monster_id}_{i}", registry) for i in range(count)]


# Standard encounter set for solo-character baseline testing (calibrated for L5).
# Each entry is (encounter_name, monster_id, count).
STANDARD_ENCOUNTERS: list[tuple[str, str, int]] = [
    ("goblin_band",    "goblin",   2),
    ("skeleton_pack",  "skeleton", 3),
    ("orc_pair",       "orc",      2),
    ("lone_bugbear",   "bugbear",  1),
    ("lone_ogre",      "ogre",     1),
]


def make_scenario(
    party: list[CombatantState],
    enemies: list[CombatantState],
    seed: int,
) -> ScenarioState:
    return ScenarioState(combatants=party + enemies, dice=Dice(seed))
