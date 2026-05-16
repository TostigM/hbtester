"""Utility scorer for choice_feature pool options.

Scores each available pool option given current combat state and returns
the best PoolEffectAction for a given action_type budget (bonus_action,
reaction, no_action). Returns None if nothing useful is available.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState

from balance_framework.engine.combat.actions import PoolEffectAction
from balance_framework.engine.grid import nearest_enemy


# ---------------------------------------------------------------------------
# Amount resolution (mirrors _pool_resolve_amount in actions.py but without dice)
# ---------------------------------------------------------------------------

def _expected_amount(spec: object, combatant: "CombatantState") -> float:
    """Resolve a spec to an expected float value (no dice rolls — use average)."""
    if isinstance(spec, (int, float)):
        return float(spec)
    s = str(spec)
    if s == "warlock_level" or s == "character_level":
        return float(getattr(combatant, "character_level", 1))
    if s == "proficiency_bonus":
        return float(combatant.proficiency_bonus)
    if s.endswith("_mod"):
        stat = s[:-4].upper()
        return float(max(0, combatant.ability_modifiers.get(stat, 0)))
    if "d" in s:
        parts = s.split("d", 1)
        try:
            count = int(parts[0]) if parts[0] else 1
            sides = int(parts[1])
            return count * (sides / 2.0 + 0.5)
        except (ValueError, IndexError):
            return 0.0
    try:
        return float(s)
    except (TypeError, ValueError):
        return 0.0


# ---------------------------------------------------------------------------
# Target resolution
# ---------------------------------------------------------------------------

def _find_lowest_hp_ally(combatant: "CombatantState", scenario: "ScenarioState") -> "CombatantState | None":
    allies = [
        c for c in scenario.combatants
        if c.team == combatant.team and c.is_conscious and c.id != combatant.id
    ]
    if not allies:
        return None
    return min(allies, key=lambda c: c.hp_current / max(1, c.hp_max))


def _find_ally_with_condition(
    combatant: "CombatantState",
    scenario: "ScenarioState",
    conditions: list[str],
) -> "CombatantState | None":
    for c in scenario.combatants:
        if c.team == combatant.team and c.is_conscious:
            if any(cond in c.conditions for cond in conditions):
                return c
    return None


# ---------------------------------------------------------------------------
# Per-effect scoring
# ---------------------------------------------------------------------------

def _score_and_target(
    effect: dict,
    combatant: "CombatantState",
    scenario: "ScenarioState",
) -> tuple[float, str | None]:
    """Return (utility_score, target_id). score=0 means option is useless right now."""
    effect_type = effect.get("type")

    match effect_type:
        case "temp_hp":
            # Only useful if we don't already have temp HP of equal or greater value
            amount = _expected_amount(effect.get("amount", 0), combatant)
            if combatant.temp_hp >= amount:
                return 0.0, None
            hp_ratio = combatant.hp_current / max(1, combatant.hp_max)
            # More valuable when low on HP; score as fraction of max HP gained
            score = (amount / max(1, combatant.hp_max)) * (2.0 - hp_ratio)
            return score, combatant.id

        case "heal":
            target_spec = effect.get("target", "ally")
            if target_spec == "self":
                target = combatant
            else:
                target = _find_lowest_hp_ally(combatant, scenario) or combatant
            missing = target.hp_max - target.hp_current
            if missing <= 0:
                return 0.0, None
            expected = _expected_amount(effect.get("amount", 0), combatant)
            bonus = _expected_amount(effect.get("bonus", 0), combatant)
            heal_value = min(expected + bonus, missing)
            return heal_value / max(1, target.hp_max), target.id

        case "condition_remove":
            conditions = effect.get("conditions", [])
            target = _find_ally_with_condition(combatant, scenario, conditions)
            if target is None:
                # Check self
                if any(c in combatant.conditions for c in conditions):
                    return 0.7, combatant.id
                return 0.0, None
            return 0.7, target.id

        case "condition_apply":
            target = nearest_enemy(combatant, scenario)
            if target is None:
                return 0.0, None
            # Frightened is high value; deafened is low
            condition = effect.get("condition", "frightened")
            base_scores = {
                "frightened": 0.5,
                "prone": 0.4,
                "stunned": 0.7,
                "poisoned": 0.35,
                "blinded": 0.45,
                "deafened": 0.2,
            }
            return base_scores.get(condition, 0.3), target.id

        case "advantage_grant":
            # Useful if we're attacking this turn; modest static value
            return 0.3, combatant.id

        case "disadvantage_impose":
            target = nearest_enemy(combatant, scenario)
            if target is None:
                return 0.0, None
            return 0.3, target.id

        case "reroll":
            # Situational; low base value
            return 0.2, combatant.id

        case "speed_change" | "utility":
            return 0.0, None

        case _:
            return 0.0, None


# ---------------------------------------------------------------------------
# Public selector
# ---------------------------------------------------------------------------

def select_best_pool_option(
    combatant: "CombatantState",
    scenario: "ScenarioState",
    action_type: str,
) -> PoolEffectAction | None:
    """Pick the highest-utility pool option available for the given action_type budget.

    Returns a ready-to-resolve PoolEffectAction, or None if nothing is useful.
    """
    best_score = 0.0
    best_action: PoolEffectAction | None = None

    for pool_def in combatant.active_pool_features:
        feature_id = pool_def["feature_id"]
        resource_key = f"choice_feature_{feature_id}"
        if combatant.resources.get(resource_key, 0) <= 0:
            continue

        for option in pool_def.get("pool", []):
            if not option.get("simulatable", False):
                continue
            if option.get("action_type") != action_type:
                continue

            effect = option.get("effect", {})
            score, target_id = _score_and_target(effect, combatant, scenario)

            if score > best_score and target_id is not None:
                best_score = score
                best_action = PoolEffectAction(
                    actor_id=combatant.id,
                    target_id=target_id,
                    feature_id=feature_id,
                    option_id=option.get("id", "unknown"),
                    effect=effect,
                )

    return best_action
