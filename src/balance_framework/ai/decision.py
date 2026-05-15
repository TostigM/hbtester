"""Main action selector dispatch — routes by combatant.behavior_profile."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action

from balance_framework.ai.profiles import MARTIAL, HEALER, CASTER, ROGUE, SUPPORT, MONSTER_MELEE, MONSTER_CASTER


def select_actions(
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> "list[Action] | None":
    """The primary ActionSelector for all combatants.

    Dispatches to the appropriate heuristic based on combatant.behavior_profile.
    Returns None (skip turn) for unknown or passive profiles.
    """
    profile = combatant.behavior_profile

    match profile:
        case _ if profile == MARTIAL:
            from balance_framework.ai.heuristics.martial import martial_selector
            return martial_selector(combatant, scenario)
        case _ if profile == HEALER:
            from balance_framework.ai.heuristics.healer import healer_selector
            return healer_selector(combatant, scenario)
        case _ if profile == CASTER:
            from balance_framework.ai.heuristics.caster import caster_selector
            return caster_selector(combatant, scenario)
        case _ if profile == ROGUE:
            from balance_framework.ai.heuristics.support import rogue_selector
            return rogue_selector(combatant, scenario)
        case _ if profile == SUPPORT:
            from balance_framework.ai.heuristics.support import support_selector
            return support_selector(combatant, scenario)
        case _ if profile == MONSTER_MELEE:
            from balance_framework.ai.monster import monster_melee_selector
            return monster_melee_selector(combatant, scenario)
        case _ if profile == MONSTER_CASTER:
            from balance_framework.ai.monster import monster_caster_selector
            return monster_caster_selector(combatant, scenario)
        case _:
            return None
