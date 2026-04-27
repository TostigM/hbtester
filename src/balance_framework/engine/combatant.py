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

    # Status flags
    is_alive: bool = True
    is_stable: bool = False  # True = unconscious but no longer rolling saves

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
