"""Integration tests: build all four standard party members at key levels.

Expected values are derived from PHB 2024 rules applied consistently.
Note: some character sheet HP values at L5 for Elowyn appear to reflect a
+8/level formula (vs. the correct +7/level for d8+CON+2), which we believe
is a calculation error in the sheet.  This test uses the PHB-correct values.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from balance_framework.registry.loader import load_content_directory
from balance_framework.registry.registry import ContentRegistry
from balance_framework.registry.character_builder import CharacterBuild, build_character


@pytest.fixture(scope="module")
def registry() -> ContentRegistry:
    return ContentRegistry(load_content_directory(Path("content")))


# ---------------------------------------------------------------------------
# Garrick — Human Battle Master Fighter
# d10, CON+2, Tough (+2/level), Defense fighting style, chain mail + shield
#   per-level gain: 6+2+2=10 | L1=14, L5=54
# ---------------------------------------------------------------------------

GARRICK_BASE = dict(
    species_id="human",
    class_id="fighter",
    subclass_id="battle_master",
    background_id="soldier",
    ability_scores={"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8},
    feat_ids=["tough", "savage_attacker"],
    armor_type="chain_mail",
    has_shield=True,
    selected_fighting_style="defense",
)


@pytest.mark.parametrize("level,expected_hp,expected_ac,expected_prof", [
    (1,  14, 19, 2),
    (5,  54, 19, 3),
    (10, 104, 19, 4),
    (15, 154, 19, 5),
    (20, 204, 19, 6),
])
def test_garrick(
    registry: ContentRegistry,
    level: int,
    expected_hp: int,
    expected_ac: int,
    expected_prof: int,
) -> None:
    garrick = build_character(CharacterBuild(level=level, **GARRICK_BASE), registry)
    assert garrick.hp_max == expected_hp
    assert garrick.ac == expected_ac
    assert garrick.proficiency_bonus == expected_prof
    assert garrick.sneak_attack_dice == 0
    assert garrick.spell_save_dc is None


# ---------------------------------------------------------------------------
# Elowyn — Human Life Cleric (Thaumaturge)
# d8, CON+2, no Tough, scale mail + shield (AC=14+1+2=17 with DEX+1)
#   per-level gain: 5+2=7 | L1=10, L5=38
# Note: the character sheet shows AC=16 (missing DEX mod from Scale Mail)
#       and HP=42 at L5 (using wrong +8/level formula).
#       This test uses PHB-correct values.
# ---------------------------------------------------------------------------

ELOWYN_BASE = dict(
    species_id="human",
    class_id="cleric",
    subclass_id="life_domain",
    background_id="acolyte",
    ability_scores={"STR": 14, "DEX": 12, "CON": 15, "INT": 8, "WIS": 16, "CHA": 10},
    feat_ids=["healer", "magic_initiate_cleric"],
    armor_type="scale_mail",
    has_shield=True,
)


@pytest.mark.parametrize("level,expected_hp,expected_ac,expected_dc", [
    (1,  10, 17, 13),
    (5,  38, 17, 14),
    (10, 73, 17, 15),
    (15, 108, 17, 16),
    (20, 143, 17, 17),
])
def test_elowyn(
    registry: ContentRegistry,
    level: int,
    expected_hp: int,
    expected_ac: int,
    expected_dc: int,
) -> None:
    elowyn = build_character(CharacterBuild(level=level, **ELOWYN_BASE), registry)
    assert elowyn.hp_max == expected_hp
    assert elowyn.ac == expected_ac
    assert elowyn.spell_save_dc == expected_dc
    assert elowyn.spellcasting_ability == "WIS"


# ---------------------------------------------------------------------------
# Varian — Human Evoker Wizard
# d6, CON+2, no Tough, no armor (Mage Armor=15 AC with DEX+2)
#   per-level gain: 4+2=6 | L1=8, L5=32
# ---------------------------------------------------------------------------

VARIAN_BASE = dict(
    species_id="human",
    class_id="wizard",
    subclass_id="evoker",
    background_id="sage",
    ability_scores={"STR": 8, "DEX": 14, "CON": 15, "INT": 16, "WIS": 12, "CHA": 10},
    feat_ids=["alert", "magic_initiate_wizard"],
    armor_type="none",
    uses_mage_armor=True,
)


@pytest.mark.parametrize("level,expected_hp,expected_ac,expected_dc", [
    (1,  8,  15, 13),
    (5,  32, 15, 14),
    (10, 62, 15, 15),
    (15, 92, 15, 16),
    (20, 122, 15, 17),
])
def test_varian(
    registry: ContentRegistry,
    level: int,
    expected_hp: int,
    expected_ac: int,
    expected_dc: int,
) -> None:
    varian = build_character(CharacterBuild(level=level, **VARIAN_BASE), registry)
    assert varian.hp_max == expected_hp
    assert varian.ac == expected_ac
    assert varian.spell_save_dc == expected_dc
    assert varian.spellcasting_ability == "INT"


# ---------------------------------------------------------------------------
# Mira — Human Thief Rogue (Charlatan background)
# d8, CON+2, no Tough, studded leather (12+4=16 AC)
#   per-level gain: 5+2=7 | L1=10, L5=38
# ---------------------------------------------------------------------------

MIRA_BASE = dict(
    species_id="human",
    class_id="rogue",
    subclass_id="thief",
    background_id="charlatan",
    ability_scores={"STR": 8, "DEX": 16, "CON": 15, "INT": 12, "WIS": 14, "CHA": 10},
    feat_ids=["alert", "skilled"],
    armor_type="studded_leather",
    has_shield=False,
)


@pytest.mark.parametrize("level,expected_hp,expected_ac,expected_sneak", [
    (1,  10, 15, 1),
    (5,  38, 15, 3),
    (10, 73, 15, 5),
    (15, 108, 15, 8),
    (20, 143, 15, 10),
])
def test_mira(
    registry: ContentRegistry,
    level: int,
    expected_hp: int,
    expected_ac: int,
    expected_sneak: int,
) -> None:
    mira = build_character(CharacterBuild(level=level, **MIRA_BASE), registry)
    assert mira.hp_max == expected_hp
    assert mira.ac == expected_ac
    assert mira.sneak_attack_dice == expected_sneak
    assert mira.spell_save_dc is None


# ---------------------------------------------------------------------------
# Cross-cutting: subclass features collected
# ---------------------------------------------------------------------------


def test_garrick_level5_has_battle_master_features(registry: ContentRegistry) -> None:
    garrick = build_character(CharacterBuild(level=5, **GARRICK_BASE), registry)
    feature_ids = {f.id for f in garrick.active_features}
    assert "combat_superiority" in feature_ids
    assert "extra_attack_1" in feature_ids


def test_varian_level3_has_subclass(registry: ContentRegistry) -> None:
    varian = build_character(CharacterBuild(level=3, **VARIAN_BASE), registry)
    feature_ids = {f.id for f in varian.active_features}
    assert "sculpt_spells" in feature_ids


def test_mira_level1_no_subclass_features(registry: ContentRegistry) -> None:
    mira_l1 = build_character(CharacterBuild(level=1, **MIRA_BASE), registry)
    feature_ids = {f.id for f in mira_l1.active_features}
    assert "fast_hands" not in feature_ids  # Thief unlocks at level 3


def test_mira_level3_has_thief_features(registry: ContentRegistry) -> None:
    mira_l3 = build_character(CharacterBuild(level=3, **MIRA_BASE), registry)
    feature_ids = {f.id for f in mira_l3.active_features}
    assert "fast_hands" in feature_ids


# ---------------------------------------------------------------------------
# Resolver: all subclasses reference valid parent classes
# ---------------------------------------------------------------------------


def test_all_subclass_references_resolve(registry: ContentRegistry) -> None:
    from balance_framework.registry.resolver import resolve_all_subclasses
    errors = resolve_all_subclasses(registry)
    assert errors == [], f"Cross-reference errors: {errors}"
