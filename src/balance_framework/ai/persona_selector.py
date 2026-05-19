"""Persona-aware action selector — wraps base heuristics with LLM-driven behavioral params."""

from __future__ import annotations

import random
from dataclasses import replace
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action

from balance_framework.ai.decision import select_actions
from balance_framework.ai.personas import PersonaStrategy

ActionSelector = Callable[["CombatantState", "ScenarioState"], "list[Action] | None"]


def make_persona_selector(strategy: PersonaStrategy, rng_seed: int = 0) -> ActionSelector:
    """Return an ActionSelector that wraps the heuristic selectors with persona behaviour.

    The selector is deterministic given the same rng_seed — use the encounter seed
    so results are reproducible across runs with the same inputs.
    """
    rng = random.Random(rng_seed)

    def selector(
        combatant: "CombatantState",
        scenario: "ScenarioState",
    ) -> "list[Action] | None":
        # Bonus action reliability: persona may "forget" their bonus action
        if rng.random() > strategy.bonus_action_reliability:
            saved = combatant.bonus_actions_remaining
            combatant.bonus_actions_remaining = 0
            actions = select_actions(combatant, scenario)
            combatant.bonus_actions_remaining = saved
        else:
            actions = select_actions(combatant, scenario)

        if not actions:
            return None

        if strategy.target_priority != "nearest":
            actions = _retarget_attacks(actions, combatant, scenario, strategy.target_priority, rng)

        return actions or None

    return selector


def _retarget_attacks(
    actions: list,
    combatant: "CombatantState",
    scenario: "ScenarioState",
    priority: str,
    rng: random.Random,
) -> list:
    from balance_framework.engine.combat.actions import WeaponAttackAction

    enemies = [c for c in scenario.combatants
               if c.team != combatant.team and c.is_alive]
    if not enemies:
        return actions

    def pick() -> str:
        alive = [e for e in enemies if e.is_alive]
        if not alive:
            return ""
        if priority == "lowest_hp":
            return min(alive, key=lambda e: e.hp_current).id
        if priority == "random":
            return rng.choice(alive).id
        return alive[0].id

    result = []
    for action in actions:
        if isinstance(action, WeaponAttackAction):
            tid = pick()
            if tid:
                action = replace(action, target_id=tid)
        result.append(action)
    return result
