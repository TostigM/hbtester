# Standard Party Summary — Baseline Configuration

**Purpose:** This is the fixed four-person control party used for all baseline and homebrew testing. The party composition never changes across tests. When a subclass is being tested, it is added as a fifth party member; the delta between four-person and five-person performance measures the test subclass's contribution.

---

## Party Composition

| Name | Class | Subclass | Role | Primary Stat |
|------|-------|----------|------|--------------|
| **Garrick Ironward** | Fighter | Battle Master | Tank, melee DPR, control | STR |
| **Elowyn Dawnbrook** | Cleric | Life (Thaumaturge) | Healer, buffer, utility | WIS |
| **Varian Thornweave** | Wizard | Evocation | Caster DPR, control, counter | INT |
| **Mira Shadowstep** | Rogue | Thief | Ranged DPR, skills, scout | DEX |

All characters are Human (2024 lineage). Standard array (15, 14, 13, 12, 10, 8).

---

## Design Rationale

**Why these four subclasses specifically:**
- **Battle Master Fighter:** Well-tuned martial baseline, neither broken (Echo Knight, not in 2024) nor weak (Champion). Weapon Mastery + maneuvers provide rich combat texture without breaking balance envelope.
- **Life Cleric (Thaumaturge):** Canonical healer, uncontroversial balance. Thaumaturge order chosen over Protector to keep Elowyn caster-focused rather than overlapping Garrick's tank role.
- **Evocation Wizard:** Iconic controller-damager. Well-understood performance baseline; Sculpt Spells prevents friendly fire for party AoE damage.
- **Thief Rogue:** Strong skill coverage and reliable ranged Sneak Attack. Chosen over Gloom Stalker Ranger to avoid surprise-round first-turn burst distortion. Chosen over Assassin Rogue because Assassin is widely considered underpowered post-surprise-round.

**Why a five-member party for tests:**
- Adding the subclass under test as a fifth member changes one variable. Swapping into an existing slot would change two (the subclass AND the role it displaces).
- Absolute win rates will skew higher than typical four-person play, but this is consistent across all tests, so relative comparisons remain valid.
- Phase 0 (standard party alone) establishes the baseline four-person performance; Phase 1+ tests measure delta from this baseline.

---

## Feat Summary Across Party

| Character | L1 Origin (Human) | L1 Background | L4 | L6/other bonus | L8 | L10 | L12 | L16 | L19 Epic Boon |
|-----------|-------------------|---------------|----|--------------:|----|----|----|----|---------------|
| Garrick | Tough | Savage Attacker | Resilient (WIS) | ASI +2 STR (L6 bonus) | ASI +2 STR | — | Alert | Resilient (CON) | Boon of Combat Prowess |
| Elowyn | Healer | Magic Initiate (Divine) | ASI +2 WIS | — | ASI +2 WIS | — | War Caster | Inspiring Leader | Boon of Fate |
| Varian | Alert | Magic Initiate (Wizard) | War Caster | — | ASI +2 INT | — | Resilient (CON) | Lucky | Boon of Spell Recall |
| Mira | Alert | Skilled | ASI +2 DEX | — | ASI +2 DEX | Lucky | Resilient (WIS) | Skulker | Boon of the Night Spirit |

**Note:** Fighter gets bonus feats at levels 6 and 14 on top of normal 4/8/12/16 ASIs.

---

## Magic Item Distribution Summary

Follows 2024 DMG "Magic Items Awarded by Level" guidelines, distributed by class role priority:
- **Garrick (martial):** Weapon and armor priority — gets +weapons and +armor first
- **Elowyn (support):** Utility priority — periapts, protective items, staff of healing
- **Varian (caster):** Spellcasting priority — wands, staff of power, Robe of the Archmagi
- **Mira (skill/ranged):** Utility + ranged weapon priority — elvenkind items, +hand crossbow, evasion

**Tier 1 (L1-4):** Each character gets ~1 uncommon item
**Tier 2 (L5-10):** Each character gets 3-4 items; rares begin appearing
**Tier 3 (L11-15):** Each character gets 2-3 items; very rares appear
**Tier 4 (L16-20):** Each character gets 2-3 items; legendary capstones

Total magic items per character by level 20: approximately 7-9 items each.

---

## Spellcasting Overview

### Elowyn (Cleric) Spell Access by Level
- L1: 1st-level slots (2), 4 prepared
- L3: 2nd-level slots, 6 prepared
- L5: 3rd-level slots, 9 prepared → **Spirit Guardians + Spiritual Weapon combo online**
- L7: 4th-level slots, 11 prepared → **Death Ward, Aura of Life online**
- L9: 5th-level slots, 14 prepared → **Flame Strike, Mass Cure Wounds online**
- L11: 6th-level slots, 16 prepared → **Heal, Heroes' Feast online**
- L13: 7th-level slots, 17 prepared → **Resurrection, Regenerate online**
- L15: 8th-level slots, 18 prepared → **Holy Aura, Sunburst online**
- L17: 9th-level slots, 19 prepared → **Mass Heal, True Resurrection online**

### Varian (Wizard) Spell Access by Level
- L1: 1st-level slots (2), 4 prepared
- L3: 2nd-level slots, 6 prepared → **Scorching Ray, Misty Step, Web online**
- L5: 3rd-level slots, 8 prepared → **Fireball, Counterspell, Fly, Haste online**
- L6: Sculpt Spells (Evoker subclass feature) — exclude allies from evocation AoE
- L7: 4th-level slots, 10 prepared → **Polymorph, Banishment online**
- L9: 5th-level slots, 12 prepared → **Wall of Force, Cone of Cold online**
- L10: Empowered Evocation — add INT mod to one damage roll per evocation spell
- L11: 6th-level slots, 14 prepared → **Chain Lightning, Disintegrate online**
- L13: 7th-level slots, 15 prepared → **Forcecage, Teleport online**
- L14: Overchannel — max damage evocation 1/rest
- L15: 8th-level slots, 16 prepared → **Maze, Power Word Stun online**
- L17: 9th-level slots, 18 prepared → **Meteor Swarm, Wish online**
- L18: Spell Mastery (Shield, Misty Step free)
- L20: Signature Spells (Fireball, Counterspell free 1/rest each)

---

## Known Simplifications for Simulation

These are conscious approximations in the standard party for tractability:

1. **Feat choices are locked.** Even if a simulation situation would favor a different feat, these feats are used.
2. **Spell preparation is illustrative, not exhaustive.** The actual prepared list at each simulated level will be fully enumerated in the simulation engine code.
3. **Magic item acquisition levels are fixed.** In a real campaign, items arrive irregularly; in the sim, they arrive at the level specified.
4. **No multiclassing.** All four party members stay single-class through level 20.
5. **Human lineage is fixed.** We are not testing lineage variance here; that would be a separate framework.
6. **Behavior AI is competent tactical, not optimized.** Characters play reasonably well but do not execute min-max combos beyond what their class naturally supports.

---

## Revision Tracking

- v0.1 (initial): Four-person party defined with character sheets
- Pending review: User (Liege) validation of character sheets, feat choices, magic item distributions, and spell selections
