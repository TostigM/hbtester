"""Engine layer — Layer 3 of the balance framework.

Public API:
  Dice:      Dice
  State:     CombatantState, ScenarioState
  Actions:   WeaponAttackAction, DodgeAction, HelpAction, resolve_action
  Resolver:  run_combat, run_combat_round
  Helpers:   nearest_enemy
"""

from balance_framework.engine.dice import Dice
from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.engine.resolver import run_combat, run_combat_round
from balance_framework.engine.combat.actions import (
    WeaponAttackAction, DodgeAction, HelpAction, resolve_action,
)
from balance_framework.engine.grid import nearest_enemy

__all__ = [
    "Dice",
    "CombatantState",
    "ScenarioState",
    "run_combat",
    "run_combat_round",
    "WeaponAttackAction",
    "DodgeAction",
    "HelpAction",
    "resolve_action",
    "nearest_enemy",
]
