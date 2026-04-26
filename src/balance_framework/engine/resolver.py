"""Main combat loop — round runner and full-encounter runner."""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.dice import Dice
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.combat.initiative import (
    roll_all_initiative,
    build_initiative_order,
)
from balance_framework.engine.combat.turns import start_turn, end_turn
from balance_framework.engine.combat.actions import Action, resolve_action
from balance_framework.engine.combat.conditions import is_incapacitated

ActionSelector = Callable[[CombatantState, ScenarioState], list[Action] | None]


def run_combat(
    scenario: ScenarioState,
    action_selector: ActionSelector,
    max_rounds: int = 20,
) -> ScenarioState:
    """Run a complete combat encounter.

    *action_selector* is called each turn with (active_combatant, scenario)
    and should return a list of Actions the combatant takes, or None to skip.

    Stops when one team has no living members or *max_rounds* is reached.
    """
    # Roll initiative and set turn order
    roll_all_initiative(scenario.combatants, scenario.dice)
    ordered = build_initiative_order(scenario.combatants)
    scenario.initiative_order = [c.id for c in ordered]
    scenario.log(
        "=== INITIATIVE ORDER: "
        + ", ".join(f"{c.display_name} ({c.initiative})" for c in ordered)
        + " ==="
    )

    while not scenario.is_over and scenario.round_number < max_rounds:
        run_combat_round(scenario, action_selector)

    if not scenario.is_over:
        scenario.log(f"Combat ended: reached max_rounds={max_rounds} with no winner")

    return scenario


def run_combat_round(
    scenario: ScenarioState,
    action_selector: ActionSelector,
) -> None:
    """Execute one full combat round — every living combatant takes a turn."""
    scenario.round_number += 1
    scenario.log(f"\n--- ROUND {scenario.round_number} ---")
    scenario.helped_targets.clear()

    for cid in list(scenario.initiative_order):
        # Skip dead combatants
        try:
            combatant = scenario.get_combatant(cid)
        except KeyError:
            continue

        if not combatant.is_alive:
            continue

        # Start of turn (reset economy, death saves, condition ticks)
        turn_events = start_turn(combatant, scenario.dice)
        for ev in turn_events:
            scenario.log(ev)

        # Check win condition before acting
        if _check_combat_over(scenario):
            return

        # If now dead (nat 20 death save doesn't apply here, but 3 fails might)
        if not combatant.is_alive or not combatant.is_conscious:
            end_turn(combatant)
            continue

        # Get actions from selector
        actions = action_selector(combatant, scenario)
        if actions:
            for action in actions:
                action_events = resolve_action(action, scenario)
                for ev in action_events:
                    scenario.log(ev)
                # Check win after each action
                if _check_combat_over(scenario):
                    return

        end_turn(combatant)

    _check_combat_over(scenario)


def _check_combat_over(scenario: ScenarioState) -> bool:
    """Set scenario.is_over and winner_team if combat is finished."""
    teams = scenario.living_teams()
    if len(teams) <= 1:
        scenario.is_over = True
        scenario.winner_team = next(iter(teams), None)
        if scenario.winner_team:
            scenario.log(f"=== COMBAT OVER — {scenario.winner_team.upper()} WINS ===")
        else:
            scenario.log("=== COMBAT OVER — everyone is dead ===")
        return True
    return False
