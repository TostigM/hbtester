"""Unit tests for character builder stat calculations."""

from __future__ import annotations

import pytest

from balance_framework.registry.character_builder import (
    CharacterBuild,
    PROF_BY_LEVEL,
    _compute_ac,
    _compute_hp,
    _compute_sneak_attack,
    _mod,
)


# ---------------------------------------------------------------------------
# Ability modifier
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("score,expected", [
    (10, 0), (11, 0), (12, 1), (13, 1),
    (14, 2), (15, 2), (16, 3), (20, 5),
    (8, -1), (9, -1), (7, -2), (6, -2), (1, -5),
])
def test_ability_modifier(score: int, expected: int) -> None:
    assert _mod(score) == expected


# ---------------------------------------------------------------------------
# Proficiency bonus by level
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("level,prof", [
    (1, 2), (4, 2), (5, 3), (8, 3), (9, 4),
    (12, 4), (13, 5), (16, 5), (17, 6), (20, 6),
])
def test_proficiency_by_level(level: int, prof: int) -> None:
    assert PROF_BY_LEVEL[level] == prof


# ---------------------------------------------------------------------------
# HP computation
# ---------------------------------------------------------------------------


def test_hp_fighter_level1() -> None:
    # d10, CON+2, Tough (+2/level): L1 = 10+2+2 = 14
    hp = _compute_hp("d10", level=1, con_mod=2, extra_per_level=2)
    assert hp == 14


def test_hp_fighter_level5_with_tough() -> None:
    # d10(6)+CON(2)+Tough(2)=10/level; L1=14, L5=14+4*10=54
    hp = _compute_hp("d10", level=5, con_mod=2, extra_per_level=2)
    assert hp == 54


def test_hp_cleric_level1() -> None:
    # d8, CON+2, no bonus: L1 = 8+2 = 10
    hp = _compute_hp("d8", level=1, con_mod=2, extra_per_level=0)
    assert hp == 10


def test_hp_cleric_level5() -> None:
    # d8(5)+CON(2)=7/level; L1=10, L5=10+4*7=38
    hp = _compute_hp("d8", level=5, con_mod=2, extra_per_level=0)
    assert hp == 38


def test_hp_wizard_level1() -> None:
    # d6, CON+2: L1 = 6+2 = 8
    hp = _compute_hp("d6", level=1, con_mod=2, extra_per_level=0)
    assert hp == 8


def test_hp_wizard_level5() -> None:
    # d6(4)+CON(2)=6/level; L1=8, L5=8+4*6=32
    hp = _compute_hp("d6", level=5, con_mod=2, extra_per_level=0)
    assert hp == 32


def test_hp_rogue_level5() -> None:
    # d8(5)+CON(2)=7/level; L1=10, L5=10+4*7=38
    hp = _compute_hp("d8", level=5, con_mod=2, extra_per_level=0)
    assert hp == 38


# ---------------------------------------------------------------------------
# AC computation
# ---------------------------------------------------------------------------


def test_ac_unarmored() -> None:
    assert _compute_ac("none", dex_mod=2, has_shield=False,
                        has_defense_style=False, uses_mage_armor=False) == 12


def test_ac_mage_armor() -> None:
    assert _compute_ac("none", dex_mod=2, has_shield=False,
                        has_defense_style=False, uses_mage_armor=True) == 15


def test_ac_chain_mail_with_shield_and_defense() -> None:
    # 16 (chain) + 2 (shield) + 1 (defense) = 19
    assert _compute_ac("chain_mail", dex_mod=2, has_shield=True,
                        has_defense_style=True, uses_mage_armor=False) == 19


def test_ac_scale_mail_with_dex_and_shield() -> None:
    # 14 + min(1, 2) + 2 = 17
    assert _compute_ac("scale_mail", dex_mod=1, has_shield=True,
                        has_defense_style=False, uses_mage_armor=False) == 17


def test_ac_medium_armor_dex_capped() -> None:
    # half_plate: 15 + min(DEX+5=5, 2) = 17; heavy is harder to cap
    assert _compute_ac("scale_mail", dex_mod=5, has_shield=False,
                        has_defense_style=False, uses_mage_armor=False) == 16


def test_ac_studded_leather_with_high_dex() -> None:
    # 12 + 4 = 16
    assert _compute_ac("studded_leather", dex_mod=4, has_shield=False,
                        has_defense_style=False, uses_mage_armor=False) == 16


def test_ac_defense_style_no_bonus_without_armor() -> None:
    # Defense requires wearing armor; mage armor doesn't count
    assert _compute_ac("none", dex_mod=2, has_shield=False,
                        has_defense_style=True, uses_mage_armor=True) == 15


# ---------------------------------------------------------------------------
# Sneak attack
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("level,dice", [
    (1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (10, 5), (19, 10), (20, 10),
])
def test_sneak_attack_rogue(level: int, dice: int) -> None:
    assert _compute_sneak_attack("rogue", level) == dice


def test_sneak_attack_non_rogue() -> None:
    assert _compute_sneak_attack("fighter", 10) == 0
    assert _compute_sneak_attack("wizard", 5) == 0
