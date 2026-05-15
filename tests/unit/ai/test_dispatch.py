"""Unit tests for select_actions dispatch and from_character factory."""

from __future__ import annotations

import pytest

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.dice import Dice
from balance_framework.engine.combat.actions import WeaponAttackAction, HealAction
from balance_framework.ai.decision import select_actions
from balance_framework.ai.profiles import MARTIAL, HEALER, CASTER, ROGUE, MONSTER_MELEE, PASSIVE


def _combatant(profile: str, team: str = "party", id: str = "c") -> CombatantState:
    return CombatantState(
        id=id, display_name=id.capitalize(), team=team,
        hp_max=30, hp_current=30, ac=14,
        proficiency_bonus=2,
        ability_modifiers={"STR": 2, "DEX": 2, "CON": 1, "INT": 1, "WIS": 1},
        spell_attack_bonus=4,
        behavior_profile=profile,
        extra_attack_count=1,
        resources={"spell_slot_1": 2, "second_wind": 1, "action_surge": 1},
    )


def _enemy() -> CombatantState:
    return CombatantState(
        id="enemy", display_name="Enemy", team="enemies",
        hp_max=15, hp_current=15, ac=12,
    )


def _scenario(actor: CombatantState, *others: CombatantState) -> ScenarioState:
    all_c = [actor] + list(others)
    s = ScenarioState(combatants=all_c, dice=Dice(0))
    s.initiative_order = [c.id for c in all_c]
    return s


# ---------------------------------------------------------------------------
# Profile dispatch
# ---------------------------------------------------------------------------

def test_dispatch_martial_returns_attack() -> None:
    c = _combatant(MARTIAL)
    scenario = _scenario(c, _enemy())
    actions = select_actions(c, scenario)
    assert actions is not None
    assert any(isinstance(a, WeaponAttackAction) for a in actions)


def test_dispatch_healer_returns_action() -> None:
    c = _combatant(HEALER)
    scenario = _scenario(c, _enemy())
    actions = select_actions(c, scenario)
    assert actions is not None


def test_dispatch_caster_returns_attack() -> None:
    c = _combatant(CASTER)
    scenario = _scenario(c, _enemy())
    actions = select_actions(c, scenario)
    assert actions is not None
    assert any(isinstance(a, WeaponAttackAction) for a in actions)


def test_dispatch_rogue_returns_attack() -> None:
    c = _combatant(ROGUE)
    scenario = _scenario(c, _enemy())
    actions = select_actions(c, scenario)
    assert actions is not None
    assert any(isinstance(a, WeaponAttackAction) for a in actions)


def test_dispatch_monster_melee_returns_attack() -> None:
    c = _combatant(MONSTER_MELEE, team="enemies", id="m")
    c.ability_modifiers["STR"] = 2
    enemy = CombatantState(
        id="hero", display_name="Hero", team="party",
        hp_max=30, hp_current=30, ac=14,
    )
    scenario = _scenario(c, enemy)
    actions = select_actions(c, scenario)
    assert actions is not None
    assert any(isinstance(a, WeaponAttackAction) for a in actions)


def test_dispatch_passive_returns_none() -> None:
    c = _combatant(PASSIVE)
    scenario = _scenario(c, _enemy())
    assert select_actions(c, scenario) is None


def test_dispatch_unknown_profile_returns_none() -> None:
    c = _combatant("dragon_breath")
    scenario = _scenario(c, _enemy())
    assert select_actions(c, scenario) is None


# ---------------------------------------------------------------------------
# from_character factory
# ---------------------------------------------------------------------------

def test_from_character_factory() -> None:
    from pathlib import Path
    from balance_framework.registry.loader import load_content_directory
    from balance_framework.registry.registry import ContentRegistry
    from balance_framework.registry.character_builder import CharacterBuild, build_character
    from balance_framework.ai.profiles import CLASS_PROFILE

    registry = ContentRegistry(load_content_directory(Path("content")))

    build = CharacterBuild(
        species_id="human", class_id="fighter", subclass_id="battle_master",
        background_id="soldier",
        ability_scores={"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8},
        feat_ids=["tough", "savage_attacker"],
        armor_type="chain_mail", has_shield=True, selected_fighting_style="defense",
        level=5,
    )
    char = build_character(build, registry)
    cs = CombatantState.from_character(
        char, "garrick", "Garrick", "party", CLASS_PROFILE["fighter"]
    )
    assert cs.hp_current == 54
    assert cs.ac == 19
    assert cs.extra_attack_count == 2
    assert cs.behavior_profile == MARTIAL
    assert cs.resources.get("second_wind") == 1
    assert cs.resources.get("action_surge") == 1
    assert cs.resources.get("superiority_dice") == 4


def test_from_character_rogue_sneak_attack() -> None:
    from pathlib import Path
    from balance_framework.registry.loader import load_content_directory
    from balance_framework.registry.registry import ContentRegistry
    from balance_framework.registry.character_builder import CharacterBuild, build_character
    from balance_framework.ai.profiles import CLASS_PROFILE

    registry = ContentRegistry(load_content_directory(Path("content")))

    build = CharacterBuild(
        species_id="human", class_id="rogue", subclass_id="thief",
        background_id="charlatan",
        ability_scores={"STR": 8, "DEX": 16, "CON": 15, "INT": 12, "WIS": 14, "CHA": 10},
        feat_ids=["alert", "skilled"],
        armor_type="studded_leather", level=5,
    )
    char = build_character(build, registry)
    cs = CombatantState.from_character(
        char, "mira", "Mira", "party", CLASS_PROFILE["rogue"]
    )
    assert cs.sneak_attack_dice == 3
    assert cs.behavior_profile == ROGUE
