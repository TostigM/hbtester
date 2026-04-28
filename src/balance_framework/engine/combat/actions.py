"""Action types and their resolution against a ScenarioState."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.dice import Dice


# ---------------------------------------------------------------------------
# Action dataclasses
# ---------------------------------------------------------------------------


@dataclass
class WeaponAttackAction:
    """A single weapon attack (or unarmed strike)."""

    action_type: str = "weapon_attack"
    attacker_id: str = ""
    target_id: str = ""
    attack_bonus: int = 0
    damage_dice: list[tuple[int, int]] = field(default_factory=list)  # (count, sides)
    damage_type: str = "bludgeoning"
    damage_bonus: int = 0
    crit_extra_dice: list[tuple[int, int]] = field(default_factory=list)
    is_ranged: bool = False
    advantage: bool = False
    disadvantage: bool = False


@dataclass
class DodgeAction:
    """The Dodge action: attacks against this combatant have disadvantage."""

    action_type: str = "dodge"
    combatant_id: str = ""


@dataclass
class HelpAction:
    """The Help action: grant advantage on the next attack against the target."""

    action_type: str = "help"
    helper_id: str = ""
    target_id: str = ""   # enemy being assisted against


@dataclass
class DeathSaveAction:
    """Placeholder — death saves are handled automatically in start_turn."""

    action_type: str = "death_save"
    combatant_id: str = ""


@dataclass
class HealAction:
    """Heal a target by rolling dice + a flat bonus.

    Optionally spends one charge from *resource_pool* (e.g. 'spell_slot_1').
    """

    action_type: str = "heal"
    caster_id: str = ""
    target_id: str = ""
    heal_dice: list[tuple[int, int]] = field(default_factory=list)  # (count, sides)
    heal_bonus: int = 0
    resource_pool: str | None = None   # pool to spend; None = no cost
    resource_cost: int = 1


Action = WeaponAttackAction | DodgeAction | HelpAction | DeathSaveAction | HealAction


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def resolve_action(action: Action, scenario: "ScenarioState") -> list[str]:
    """Dispatch *action* to the correct resolver; return event strings.

    All dice consumption goes through scenario.dice for determinism.
    """
    match action.action_type:
        case "weapon_attack":
            return _resolve_weapon_attack(action, scenario)  # type: ignore[arg-type]
        case "dodge":
            return _resolve_dodge(action, scenario)  # type: ignore[arg-type]
        case "help":
            return _resolve_help(action, scenario)  # type: ignore[arg-type]
        case "death_save":
            return []  # handled by turns.start_turn
        case "heal":
            return _resolve_heal(action, scenario)  # type: ignore[arg-type]
        case _:
            raise ValueError(f"Unknown action type: {action.action_type!r}")


def _resolve_weapon_attack(action: WeaponAttackAction, scenario: "ScenarioState") -> list[str]:
    from balance_framework.engine.combat.attacks import WeaponAttack, resolve_attack
    from balance_framework.engine.combat.damage import apply_damage
    from balance_framework.engine.combat.concentration import check_concentration

    attacker = scenario.get_combatant(action.attacker_id)
    target = scenario.get_combatant(action.target_id)

    spec = WeaponAttack(
        attacker_id=action.attacker_id,
        target_id=action.target_id,
        attack_bonus=action.attack_bonus,
        damage_dice=action.damage_dice,
        damage_type=action.damage_type,
        damage_bonus=action.damage_bonus,
        crit_extra_dice=action.crit_extra_dice,
        is_ranged=action.is_ranged,
        advantage=action.advantage,
        disadvantage=action.disadvantage,
    )

    result = resolve_attack(attacker, target, spec, scenario.dice)
    events = list(result.events)

    if not result.hit:
        from balance_framework.logging.event_log import AttackEvent
        scenario.structured_events.append(AttackEvent(
            round_number=scenario.round_number,
            attacker_id=action.attacker_id,
            target_id=action.target_id,
            roll=result.raw_roll,
            total=result.total_attack_roll,
            target_ac=result.target_ac,
            hit=False,
            damage_type=action.damage_type,
        ))

    if result.hit:
        dmg = apply_damage(target, result.damage_total, result.damage_type, result.crit)
        aid = action.attacker_id
        scenario.damage_dealt[aid] = scenario.damage_dealt.get(aid, 0) + dmg.applied_damage
        if dmg.killed:
            scenario.kills[aid] = scenario.kills.get(aid, 0) + 1
        from balance_framework.logging.event_log import AttackEvent, DeathEvent
        scenario.structured_events.append(AttackEvent(
            round_number=scenario.round_number,
            attacker_id=aid,
            target_id=action.target_id,
            roll=result.raw_roll,
            total=result.total_attack_roll,
            target_ac=result.target_ac,
            hit=True,
            crit=result.crit,
            damage=dmg.applied_damage,
            damage_type=result.damage_type,
            killed=dmg.killed,
        ))
        if dmg.killed:
            scenario.structured_events.append(DeathEvent(
                round_number=scenario.round_number,
                combatant_id=action.target_id,
                team=target.team,
                instant_death=dmg.instant_death,
            ))
        events.append(
            f"  {target.display_name}: {dmg.applied_damage} dmg "
            f"→ {dmg.hp_after}/{target.hp_max} HP"
            + (f" (absorbed {dmg.temp_hp_absorbed} temp HP)" if dmg.temp_hp_absorbed else "")
            + (" [INSTANT DEATH]" if dmg.instant_death else "")
            + (" [KNOCKED OUT]" if dmg.knocked_unconscious else "")
        )
        # Check concentration
        if target.concentrating_on and dmg.applied_damage > 0:
            conc = check_concentration(target, dmg.applied_damage, scenario.dice)
            if not conc.maintained:
                events.append(
                    f"  {target.display_name} loses concentration on "
                    f"{conc.spell_lost!r} (failed CON save DC {conc.dc})"
                )

    return events


def _resolve_dodge(action: DodgeAction, scenario: "ScenarioState") -> list[str]:
    from balance_framework.engine.combat.conditions import apply_condition
    combatant = scenario.get_combatant(action.combatant_id)
    apply_condition(combatant, "prone")  # placeholder — dodge adds disadvantage to attacks
    # Real implementation: set a "dodging" flag; simplified for M3
    # We'll use a special condition we track manually
    # For now just log the action
    return [f"{combatant.display_name} takes the Dodge action"]


def _resolve_help(action: HelpAction, scenario: "ScenarioState") -> list[str]:
    # Mark the target as "helped_against" so the next attack has advantage
    scenario.helped_targets.add(action.target_id)
    helper = scenario.get_combatant(action.helper_id)
    return [f"{helper.display_name} uses the Help action against {action.target_id}"]


def _resolve_heal(action: HealAction, scenario: "ScenarioState") -> list[str]:
    from balance_framework.engine.combat.damage import apply_healing
    from balance_framework.engine.combat.resources import spend, InsufficientResourceError

    caster = scenario.get_combatant(action.caster_id)
    target = scenario.get_combatant(action.target_id)

    # Spend resource if required
    if action.resource_pool is not None:
        try:
            spend(caster, action.resource_pool, action.resource_cost)
        except (KeyError, InsufficientResourceError):
            return [f"{caster.display_name} tried to heal but has no {action.resource_pool!r}"]

    # Roll healing dice
    amount = action.heal_bonus
    for count, sides in action.heal_dice:
        amount += scenario.dice.roll_sum(sides, count)

    gained = apply_healing(target, amount)
    cid = action.caster_id
    scenario.healing_done[cid] = scenario.healing_done.get(cid, 0) + gained
    from balance_framework.logging.event_log import HealEvent
    scenario.structured_events.append(HealEvent(
        round_number=scenario.round_number,
        caster_id=cid,
        target_id=action.target_id,
        amount=gained,
        resource_spent=action.resource_pool,
    ))
    return [
        f"{caster.display_name} heals {target.display_name} for {gained} HP "
        f"({target.hp_current}/{target.hp_max})"
    ]
