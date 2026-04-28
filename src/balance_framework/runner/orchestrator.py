"""Encounter batch runner."""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.combat.actions import Action
    from balance_framework.engine.combatant import CombatantState

from balance_framework.engine.dice import Dice
from balance_framework.engine.resolver import run_combat
from balance_framework.runner.seeding import seed_range
from balance_framework.runner.collector import EncounterResult, collect_result

# A factory callable: given a seed, returns a fresh ScenarioState ready to run.
ScenarioFactory = Callable[[int], "ScenarioState"]

# The action selector to use (matches resolver.ActionSelector signature).
ActionSelector = Callable[["CombatantState", "ScenarioState"], "list[Action] | None"]


def run_encounter_batch(
    factory: ScenarioFactory,
    selector: ActionSelector,
    n: int = 100,
    base_seed: int = 0,
    max_rounds: int = 20,
) -> list[EncounterResult]:
    """Run *n* encounters, each with a fresh scenario from *factory*.

    Seeds are ``base_seed + i`` for i in 0..n-1 so the batch is fully
    reproducible.  The factory receives the seed and is responsible for
    injecting it into the ScenarioState's Dice instance.

    Returns one EncounterResult per encounter.
    """
    seeds = seed_range(base_seed, n)
    results: list[EncounterResult] = []
    for seed in seeds:
        scenario = factory(seed)
        run_combat(scenario, selector, max_rounds=max_rounds)
        results.append(collect_result(scenario, seed))
    return results
