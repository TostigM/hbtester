# Supplementary Templates Index v0.1

**Purpose:** Fifth-member templates for subclass testing when the test subclass is not covered by the main standard party (Garrick Fighter, Elowyn Cleric, Varian Wizard, Mira Rogue). All supplementary characters are Human for species variance elimination and use standard array ability scores with background-driven ASIs.

**Subclass selection methodology:** For each class, the subclass judged most "statistically average" or mid-tier per community optimizer consensus (Nat1Gaming tier list, RPGBOT guides, EN World discussions) was selected. Note: true statistical baseline for each subclass is what our framework is built to generate; these picks are informed guesses pre-baseline.

---

## The Nine Supplementary Templates

| # | Character | Class | Subclass | Tier Consensus | File |
|---|-----------|-------|----------|----------------|------|
| 5 | Thaddeus Vex | Artificer | Alchemist | B-tier | `05_Thaddeus_Alchemist_Artificer.md` |
| 6 | Brunhilda Stormblood | Barbarian | Wild Heart | B+ tier | `06_Brunhilda_WildHeart_Barbarian.md` |
| 7 | Caspian Thorne | Bard | Valor | B-tier | `07_Caspian_Valor_Bard.md` |
| 8 | Astra Nightwhisper | Druid | Stars | B-tier | `08_Astra_Stars_Druid.md` |
| 9 | Kenji Silentpalm | Monk | Open Hand | B/C-tier | `09_Kenji_OpenHand_Monk.md` |
| 10 | Sir Aldric Goldbrand | Paladin | Devotion | B-tier | `10_Aldric_Devotion_Paladin.md` |
| 11 | Finnian Wildwood | Ranger | Hunter | C/B-tier | `11_Finnian_Hunter_Ranger.md` |
| 12 | Vesper Ashworth | Sorcerer | Draconic | B-tier | `12_Vesper_Draconic_Sorcerer.md` |
| 13 | Morgaine Blackquill | Warlock | Fiend | B-tier | `13_Morgaine_Fiend_Warlock.md` |

Combined with the main party (templates 1-4), the system has 13 total class templates, covering every class in 2024 PHB + Forge of the Artificer.

---

## Primary Ability Score Summary

| Template | Primary | Secondary | Tertiary |
|----------|---------|-----------|----------|
| Thaddeus (Artificer) | INT | CON | WIS |
| Brunhilda (Barb) | STR | CON | — |
| Caspian (Bard) | CHA | DEX | CON |
| Astra (Druid) | WIS | CON | — |
| Kenji (Monk) | DEX | WIS | CON |
| Aldric (Paladin) | STR | CHA | CON |
| Finnian (Ranger) | DEX | WIS | CON |
| Vesper (Sorcerer) | CHA | CON | — |
| Morgaine (Warlock) | CHA | CON | — |

---

## Background Assignments

| Template | Background | Ability ASIs |
|----------|-----------|--------------|
| Thaddeus | Sage | INT+2, WIS+1 |
| Brunhilda | Soldier | STR+2, CON+1 |
| Caspian | Entertainer | CHA+2, CON+1 |
| Astra | Hermit | WIS+2, CON+1 |
| Kenji | Wayfarer | DEX+2, WIS+1 |
| Aldric | Noble | STR+2, CHA+1 |
| Finnian | Wayfarer | DEX+2, WIS+1 |
| Vesper | Noble | CHA+2, INT+1 |
| Morgaine | Charlatan | CHA+2, CON+1 |

**Note:** Some backgrounds repeat (Wayfarer used by Kenji and Finnian; Noble by Aldric and Vesper). Templates are not tested simultaneously, so duplication is acceptable.

---

## Origin Feat Assignments

| Template | Human Origin Feat | Background Origin Feat |
|----------|-------------------|------------------------|
| Thaddeus | Magic Initiate (Wizard) | Magic Initiate (Cleric) |
| Brunhilda | Tough | Savage Attacker |
| Caspian | Tough | Musician |
| Astra | Alert | Healer |
| Kenji | Tavern Brawler | Lucky |
| Aldric | Tough | Skilled |
| Finnian | Alert | Lucky |
| Vesper | Tough | Skilled |
| Morgaine | Tough | Skilled |

---

## Known Implementation Caveats

**Each template is a structured data input, not a final play character.** The engine will consume these as YAML content files. The markdown form is for human review.

**Some details may need adjustment during implementation:**
1. Specific feat choices at mid-level ASIs could vary based on simulation results; current picks are reasonable defaults
2. Spell selections for casters are "priority example" lists, not exhaustive; engine will enumerate full prepared lists per level per encounter
3. Magic item progression follows 2024 DMG guidelines but specific item choice is illustrative
4. Mechanical details (especially around edge cases like specific Invocation synergies, subclass timing interactions) should be verified against actual PHB at implementation time

**Recommended validation during Phase 2:**
- Convert each template to YAML against `class_schema_v0.1.md` and validate parse
- Run level-by-level character build verification (does feature unlock chain work?)
- Spot-check AC, HP, spell save DC calculations at key levels
- Compare simulation-generated DPR estimates vs community consensus

---

## Using These Templates in the Framework

**Subclass testing workflow:**
1. Test subclass identified (e.g., homebrew Moon Druid variant)
2. Base class identified (Druid)
3. Corresponding supplementary template loaded (Astra Nightwhisper, Stars Druid)
4. Test subclass swapped for Stars at character build
5. Standard party (Garrick/Elowyn/Varian/Mira) + modified supplementary character = 5-person test party
6. Tests run against baseline

**Edge cases requiring engine decisions:**
- **Subclass that changes base class substantially** (e.g., a homebrew Druid variant that disables Wild Shape): engine must handle missing base class features gracefully
- **Subclasses that add new spell lists** (e.g., homebrew with unique spell access): engine must merge spell access without breaking prepared-spell math
- **Subclasses with scaling features tied to levels different from canonical** (e.g., homebrew that grants a capstone at L15 instead of L17): engine must respect schema-declared levels

**Behavior AI notes per template:**
Each template includes "Behavior AI Priorities" section. These feed directly into the rule-based option scoring system described in architecture spec §8. Templates with complex resource management (Sorcerer Metamagic, Warlock Pact slots) will have the richest behavior rule sets.
