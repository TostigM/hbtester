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


@dataclass
class PoolEffectAction:
    """Apply one effect option from a choice_feature pool (e.g. a Community Spirit)."""

    action_type: str = "pool_effect"
    actor_id: str = ""
    target_id: str = ""
    feature_id: str = ""   # the choice_feature id (resource key: choice_feature_{id})
    option_id: str = ""    # the specific pool option chosen
    effect: dict = field(default_factory=dict)


@dataclass
class BreathWeaponAction:
    """Breath weapon: hits all living enemies with a DEX/CON save for half."""

    action_type: str = "breath_weapon"
    attacker_id: str = ""
    damage_dice: list[tuple[int, int]] = field(default_factory=list)  # (count, sides)
    damage_type: str = "fire"
    save_ability: str = "DEX"
    save_dc: int = 13


Action = WeaponAttackAction | DodgeAction | HelpAction | DeathSaveAction | HealAction | BreathWeaponAction | PoolEffectAction


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
        case "breath_weapon":
            return _resolve_breath_weapon(action, scenario)  # type: ignore[arg-type]
        case "pool_effect":
            return _resolve_pool_effect(action, scenario)  # type: ignore[arg-type]
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


def _pool_resolve_amount(spec: object, actor: "Any") -> int:
    """Resolve a pool effect amount spec to an integer using combatant state."""
    if isinstance(spec, int):
        return spec
    s = str(spec)
    if s == "warlock_level" or s == "character_level":
        return getattr(actor, "character_level", 1)
    if s == "proficiency_bonus":
        return actor.proficiency_bonus
    if s.endswith("_mod"):
        stat = s[:-4].upper()
        return max(0, actor.ability_modifiers.get(stat, 0))
    try:
        return int(s)
    except (TypeError, ValueError):
        return 0


def _pool_resolve_dice(spec: object, actor: "Any", scenario: "ScenarioState") -> int:
    """Resolve a dice string like '1d4' or a plain amount spec to a rolled integer."""
    if isinstance(spec, int):
        return spec
    s = str(spec)
    if "d" in s:
        parts = s.split("d", 1)
        try:
            count = int(parts[0]) if parts[0] else 1
            sides = int(parts[1])
            return scenario.dice.roll_sum(sides, count)
        except (ValueError, IndexError):
            return 0
    return _pool_resolve_amount(spec, actor)


def _resolve_pool_effect(action: "PoolEffectAction", scenario: "ScenarioState") -> list[str]:
    from balance_framework.engine.combat.resources import spend, InsufficientResourceError

    actor = scenario.get_combatant(action.actor_id)
    resource_key = f"choice_feature_{action.feature_id}"

    try:
        spend(actor, resource_key, 1)
    except (KeyError, InsufficientResourceError):
        return [f"{actor.display_name} has no {action.feature_id!r} charges remaining"]

    effect = action.effect
    effect_type = effect.get("type")
    label = f"[{action.option_id}]"

    match effect_type:
        case "temp_hp":
            amount = _pool_resolve_amount(effect.get("amount", 0), actor)
            actor.temp_hp = max(actor.temp_hp, amount)
            return [f"{actor.display_name} {label} gains {amount} temp HP"]

        case "heal":
            target = scenario.get_combatant(action.target_id)
            rolled = _pool_resolve_dice(effect.get("amount", 0), actor, scenario)
            bonus = _pool_resolve_amount(effect.get("bonus", 0), actor)
            total = max(1, rolled + bonus)
            from balance_framework.engine.combat.damage import apply_healing
            gained = apply_healing(target, total)
            cid = action.actor_id
            scenario.healing_done[cid] = scenario.healing_done.get(cid, 0) + gained
            return [f"{actor.display_name} {label} heals {target.display_name} for {gained} HP"]

        case "condition_remove":
            target = scenario.get_combatant(action.target_id)
            conditions = effect.get("conditions", [])
            removed = [c for c in conditions if c in target.conditions]
            for c in removed:
                del target.conditions[c]
            return [f"{actor.display_name} {label} removes {removed} from {target.display_name}"]

        case "condition_apply":
            target = scenario.get_combatant(action.target_id)
            condition = effect.get("condition", "frightened")
            save_ability = effect.get("save_ability", "WIS")
            dc = _pool_resolve_amount(effect.get("dc", actor.spell_save_dc or 10), actor)
            from balance_framework.engine.combat.saves import resolve_save
            from balance_framework.engine.combat.conditions import apply_condition
            save_result = resolve_save(target, save_ability, dc, scenario.dice)
            if not save_result.success:
                apply_condition(target, condition)
                return [f"{actor.display_name} {label} applies {condition!r} to {target.display_name}"]
            return [f"{target.display_name} resisted {condition!r} {label}"]

        case _:
            return [f"{actor.display_name} {label} (effect type {effect_type!r} not simulated)"]


def _resolve_breath_weapon(action: BreathWeaponAction, scenario: "ScenarioState") -> list[str]:
    from balance_framework.engine.combat.saves import resolve_save
    from balance_framework.engine.combat.damage import apply_damage
    from balance_framework.engine.combat.resources import spend, InsufficientResourceError

    attacker = scenario.get_combatant(action.attacker_id)

    try:
        spend(attacker, "breath_weapon")
    except (KeyError, InsufficientResourceError):
        return [f"{attacker.display_name} has no breath weapon charges remaining"]

    enemies = [c for c in scenario.combatants if c.team != attacker.team and c.is_alive]
    if not enemies:
        return [f"{attacker.display_name} uses its breath weapon but hits no one"]

    events = [f"{attacker.display_name} uses its breath weapon!"]

    for target in enemies:
        total_damage = sum(
            scenario.dice.roll_sum(sides, count)
            for count, sides in action.damage_dice
        )

        save_result = resolve_save(target, action.save_ability, action.save_dc, scenario.dice)
        actual_damage = total_damage // 2 if save_result.success else total_damage

        dmg = apply_damage(target, actual_damage, action.damage_type, False)
        aid = action.attacker_id
        scenario.damage_dealt[aid] = scenario.damage_dealt.get(aid, 0) + dmg.applied_damage
        if dmg.killed:
            scenario.kills[aid] = scenario.kills.get(aid, 0) + 1
            from balance_framework.logging.event_log import DeathEvent
            scenario.structured_events.append(DeathEvent(
                round_number=scenario.round_number,
                combatant_id=target.id,
                team=target.team,
                instant_death=dmg.instant_death,
            ))

        events.append(
            f"  {target.display_name}: {'saved' if save_result.success else 'failed'} "
            f"({action.save_ability} DC {action.save_dc}), "
            f"{dmg.applied_damage} {action.damage_type} dmg "
            f"→ {dmg.hp_after}/{target.hp_max} HP"
        )

    return events
