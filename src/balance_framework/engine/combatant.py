"""CombatantState — mutable combat state for one participant in an encounter."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CombatantState:
    """All mutable state for one combatant during an encounter.

    Build via ``from_character()`` or ``from_monster_stats()`` factory helpers,
    or construct directly for tests.
    """

    id: str
    display_name: str
    team: str  # "party" | "enemies" | any label

    # HP
    hp_max: int
    hp_current: int
    temp_hp: int = 0

    # Defenses
    ac: int = 10
    speed: int = 30
    proficiency_bonus: int = 2

    # Ability modifiers (pre-computed)
    ability_modifiers: dict[str, int] = field(default_factory=dict)
    saving_throw_proficiencies: frozenset[str] = field(default_factory=frozenset)
    saving_throw_advantages: frozenset[str] = field(default_factory=frozenset)  # e.g. from paladin aura

    # Damage modifiers
    damage_resistances: frozenset[str] = field(default_factory=frozenset)
    damage_immunities: frozenset[str] = field(default_factory=frozenset)
    damage_vulnerabilities: frozenset[str] = field(default_factory=frozenset)
    condition_immunities: frozenset[str] = field(default_factory=frozenset)

    # Conditions: name -> rounds remaining (None = indefinite)
    conditions: dict[str, int | None] = field(default_factory=dict)

    # Concentration
    concentrating_on: str | None = None  # spell id

    # Death saves
    death_save_successes: int = 0
    death_save_failures: int = 0

    # Resource pools: pool_id -> current value
    resources: dict[str, int] = field(default_factory=dict)

    # Initiative (set by initiative.roll_all_initiative)
    initiative: int = 0
    initiative_tiebreak: int = 0  # DEX mod used as tiebreaker

    # Per-turn economy (reset at start of each turn)
    actions_remaining: int = 1
    bonus_actions_remaining: int = 1
    reactions_remaining: int = 1
    movement_remaining: int = 30

    # Crit threshold (normally 20; Champion reduces to 19)
    crit_threshold: int = 20

    # Spellcasting (None for non-casters)
    spell_attack_bonus: int | None = None
    spell_save_dc: int | None = None

    # Combat role (drives behavior AI dispatch)
    behavior_profile: str = "passive"  # "martial" | "healer" | "caster" | "rogue" | "monster_melee"

    # Attack economy
    extra_attack_count: int = 1   # total attacks per Attack action (1 = one, 2 = Extra Attack, etc.)
    sneak_attack_dice: int = 0    # number of d6 added to first sneak attack per turn
    primary_damage_dice: list[tuple[int, int]] = field(default_factory=lambda: [(1, 6)])
    bonus_damage_dice: list[tuple[int, int]] = field(default_factory=list)   # once-per-turn bonus (e.g. Hunter's Prey, Divine Fury)
    bonus_damage_flat: int = 0   # flat bonus added to spell damage rolls (e.g. Elemental Affinity)

    # Subclass combat flags (set by from_character via combat_stats_from_features)
    frenzy_bonus_attack: bool = False    # Berserker: bonus action attack while raging
    dread_ambusher: bool = False         # Gloom Stalker: extra attack on round 1 with +2d6
    assassinate: bool = False            # Assassin: advantage on round-1 attacks
    war_priest_attack: bool = False      # War Domain: bonus action weapon attack
    sacred_weapon: bool = False          # Devotion Paladin: spend CD → +CHA to attacks
    vow_of_enmity: bool = False          # Vengeance Paladin: spend CD → advantage on attacks
    cd_offensive_active: bool = False    # Tracks whether CD offensive buff is running

    # choice_feature pool definitions extracted from active features
    # Each entry: {"feature_id": str, "pool": list[dict]}
    active_pool_features: list[dict] = field(default_factory=list)

    # Character level (used by pool effect amount resolution)
    character_level: int = 1

    # Monster special attacks
    breath_weapon_config: dict | None = None   # None if no breath weapon
    melee_attack_bonus: int | None = None      # overrides STR-based calc if set

    # Status flags
    is_alive: bool = True
    is_stable: bool = False  # True = unconscious but no longer rolling saves

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_character(
        cls,
        character: object,  # Character — avoid circular import at module level
        combatant_id: str,
        display_name: str,
        team: str,
        behavior_profile: str = "passive",
    ) -> "CombatantState":
        """Build a CombatantState from a resolved Character, populating resource pools
        from active features so the behavior AI can spend them."""
        from balance_framework.registry.character_builder import Character
        from balance_framework.ai.profiles import resources_from_features, combat_stats_from_features

        assert isinstance(character, Character)
        c = character

        ability_mods = dict(c.ability_modifiers)
        resources = resources_from_features(c.active_features, c.build.class_id, c.build.level)
        combat_stats = combat_stats_from_features(
            c.active_features, c.build.class_id, c.build.level,
            ability_modifiers=ability_mods,
        )

        # War Priest uses = WIS mod (min 1), tracked as a resource pool
        if combat_stats["has_war_priest"]:
            resources["war_priest"] = max(1, ability_mods.get("WIS", 0))

        # Extract choice_feature pool definitions for the AI scorer
        pool_features = []
        for f in c.active_features:
            if f.feature_type == "choice_feature":
                pool = f.body.get("pool", [])
                if pool:
                    pool_features.append({"feature_id": f.id, "pool": pool})

        return cls(
            id=combatant_id,
            display_name=display_name,
            team=team,
            hp_max=c.hp_max,
            hp_current=c.hp_max,
            ac=c.ac,
            proficiency_bonus=c.proficiency_bonus,
            ability_modifiers=ability_mods,
            saving_throw_proficiencies=c.saving_throw_proficiencies,
            spell_attack_bonus=c.spell_attack_bonus,
            spell_save_dc=c.spell_save_dc,
            sneak_attack_dice=c.sneak_attack_dice,
            extra_attack_count=max(1, c.extra_attack_count + 1),
            behavior_profile=behavior_profile,
            resources=resources,
            temp_hp=combat_stats["arcane_ward_hp"],
            crit_threshold=combat_stats["crit_threshold"],
            bonus_damage_dice=combat_stats["bonus_damage_dice"],
            bonus_damage_flat=combat_stats["bonus_damage_flat"],
            frenzy_bonus_attack=combat_stats["frenzy_bonus_attack"],
            dread_ambusher=combat_stats["dread_ambusher"],
            assassinate=combat_stats["assassinate"],
            war_priest_attack=combat_stats["has_war_priest"],
            sacred_weapon=combat_stats["sacred_weapon"],
            vow_of_enmity=combat_stats["vow_of_enmity"],
            active_pool_features=pool_features,
            character_level=c.build.level,
        )

    @classmethod
    def from_monster(
        cls,
        monster: object,  # Monster — avoid circular import
        combatant_id: str,
        team: str = "enemies",
    ) -> "CombatantState":
        """Build a CombatantState from a Monster schema object."""
        from balance_framework.schema.types import Monster as MonsterType
        assert isinstance(monster, MonsterType)
        m = monster

        def _mod(score: int) -> int:
            return (score - 10) // 2

        ability_mods = {
            stat: _mod(getattr(m.abilities, stat))
            for stat in ("STR", "DEX", "CON", "INT", "WIS", "CHA")
        }

        hints = m.behavior_hints
        profile = hints.get("profile", "monster_melee")
        multiattack = int(hints.get("multiattack", 1))
        die_count = int(hints.get("damage_die_count", 1))
        die_size = int(hints.get("damage_die", 6))

        breath_cfg: dict | None = hints.get("breath_weapon")
        atk_bonus_override = hints.get("attack_bonus")
        spell_atk = hints.get("spell_attack_bonus")
        spell_dc = hints.get("spell_save_dc")

        resources: dict[str, int] = {}
        if profile == "monster_caster":
            for lvl_str, count in hints.get("spell_slots", {}).items():
                resources[f"spell_slot_{lvl_str}"] = int(count)
        if breath_cfg is not None:
            resources["breath_weapon"] = 1

        avg_hp = m.hp.get("average", 7)

        return cls(
            id=combatant_id,
            display_name=m.display_name,
            team=team,
            hp_max=avg_hp,
            hp_current=avg_hp,
            ac=m.ac,
            proficiency_bonus=m.proficiency_bonus,
            ability_modifiers=ability_mods,
            saving_throw_proficiencies=frozenset(m.saving_throw_proficiencies),
            damage_resistances=frozenset(m.damage_resistances),
            damage_immunities=frozenset(m.damage_immunities),
            damage_vulnerabilities=frozenset(m.damage_vulnerabilities),
            condition_immunities=frozenset(m.condition_immunities),
            behavior_profile=profile,
            extra_attack_count=multiattack,
            primary_damage_dice=[(die_count, die_size)],
            resources=resources,
            spell_attack_bonus=int(spell_atk) if spell_atk is not None else None,
            spell_save_dc=int(spell_dc) if spell_dc is not None else None,
            breath_weapon_config=breath_cfg,
            melee_attack_bonus=int(atk_bonus_override) if atk_bonus_override is not None else None,
        )

    # ------------------------------------------------------------------
    # Derived state helpers
    # ------------------------------------------------------------------

    @property
    def is_conscious(self) -> bool:
        return self.is_alive and "unconscious" not in self.conditions

    @property
    def is_at_zero_hp(self) -> bool:
        return self.hp_current <= 0 and self.is_alive

    @property
    def effective_hp(self) -> int:
        """Total HP including temp HP."""
        return self.hp_current + self.temp_hp

    def __repr__(self) -> str:
        return (
            f"<Combatant {self.id!r} hp={self.hp_current}/{self.hp_max} "
            f"ac={self.ac} team={self.team!r}>"
        )
