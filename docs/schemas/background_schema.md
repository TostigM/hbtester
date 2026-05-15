# Background Content Schema — Proposal v0.1

## Purpose

Backgrounds represent a character's pre-adventuring life. In 2024 rules, backgrounds are the primary source of ability score increases (a reversal from 2014), grant skill and tool proficiencies, provide an origin feat, and give starting equipment.

Background testing primarily evaluates non-combat contribution but also considers the impact of granted origin feats.

---

## Design Principles

Same as prior schemas, plus one specific to backgrounds:

**The origin feat grant is the biggest single mechanical lever of a background.** Backgrounds with strong origin feats (like Alert, Tough, Magic Initiate) are measurably stronger than those with weaker ones. The schema captures this explicitly so balance evaluation can focus on it.

---

## Top-Level Background Structure

```yaml
schema_version: "0.1"
content_type: "background"
id: "soldier"
display_name: "Soldier"
source: "PHB_2024"
version: "2024"
author: "Wizards of the Coast"
flavor_text: "You served in an army..."

# Ability score increases (2024: backgrounds grant +2/+1 or +1/+1/+1 from a fixed list)
ability_score_increases:
  mode: "plus_2_plus_1"              # or "plus_1_plus_1_plus_1"
  eligible_abilities: ["STR", "CON", "CHA"]   # 3 abilities; player distributes +2/+1 among them
  # Alternative mode: "plus_1_plus_1_plus_1" distributes +1 to each

# Skill proficiencies granted (always fixed in 2024, not player choice)
skill_proficiencies: ["athletics", "intimidation"]

# Tool proficiency granted (typically one fixed tool or gaming set)
tool_proficiency: "gaming_set"

# Origin feat granted (background determines this in 2024)
origin_feat: "savage_attacker"

# Starting equipment
starting_equipment:
  - "spear"
  - "shortbow"
  - "20_arrows"
  - "gaming_set_of_choice"
  - "travelers_clothes"
  - "14_gp"
# Alternatively: starting_gold: "50 gp"
```

---

## Example: Sage

```yaml
id: "sage"
display_name: "Sage"
source: "PHB_2024"

ability_score_increases:
  mode: "plus_2_plus_1"
  eligible_abilities: ["CON", "INT", "WIS"]

skill_proficiencies: ["arcana", "history"]
tool_proficiency: "calligrapher_supplies"
origin_feat: "magic_initiate_wizard"

starting_equipment:
  - "book_history"
  - "calligrapher_supplies"
  - "parchment_bundle"
  - "ink_bottle"
  - "quill"
  - "small_knife"
  - "travelers_clothes"
  - "8_gp"
```

---

## Example: Charlatan

```yaml
id: "charlatan"
display_name: "Charlatan"
source: "PHB_2024"

ability_score_increases:
  mode: "plus_2_plus_1"
  eligible_abilities: ["DEX", "CON", "CHA"]

skill_proficiencies: ["deception", "sleight_of_hand"]
tool_proficiency: "forgery_kit"
origin_feat: "skilled"

starting_equipment:
  - "fine_clothes"
  - "disguise_kit"
  - "forgery_kit"
  - "signet_ring_fake"
  - "love_letter"
  - "15_gp"
```

---

## Origin Feat Reference

Origin feats are defined in their own feat registry (covered briefly in the Epic Boons schema document since feats share similar structure). Background schemas only reference origin feat IDs; the actual feat definition lives in the feat registry.

Origin feats available in 2024 PHB:
- Alert
- Crafter
- Healer
- Lucky
- Magic Initiate (Cleric, Druid, Wizard — three variants)
- Musician
- Savage Attacker
- Skilled
- Tavern Brawler
- Tough

Each has its own feat definition. The background references which one it grants.

---

## Scoring Framework for Backgrounds

Unlike species, backgrounds are not scored primarily on trait point values because WotC designed them to be mostly equivalent. All backgrounds grant roughly the same package: 3 ability score points (via +2/+1), 2 skill proficiencies, 1 tool proficiency, 1 origin feat, and starting equipment.

**The variable is the origin feat.** This is where background variance comes from.

Origin feat value scoring:
- Magic Initiate (any variant): 6 points (grants spellcasting access)
- Alert: 5 points (initiative bonus + surprise immunity)
- Tough: 5 points (HP increase scaling with level)
- Lucky: 4 points (3 rerolls per day)
- Healer: 3 points (party support)
- Savage Attacker: 3 points (damage reroll once per turn)
- Skilled: 3 points (3 extra skill proficiencies)
- Musician: 2 points (inspiration granting, limited utility)
- Tavern Brawler: 3 points (improvised weapons + unarmed bonus)
- Crafter: 3 points (crafting cost reduction, tool proficiencies)

Skill proficiency value (for non-feat part of background):
- One skill: 1 point
- Combo of stealth + perception (scouts): 2.5 points (high synergy)
- Combo of persuasion + deception (faces): 2.5 points

Tool proficiency value: 0.5-1 point depending on tool utility.

**Total expected background score: approximately 6-9 points depending on origin feat.**

Homebrew backgrounds should fall in this range. Backgrounds granting novel origin feats with very high power could score higher and flag as overtuned.

---

## Homebrew Background Concerns

The most common homebrew background imbalance is granting custom origin feats that are too powerful. The schema handles this by requiring homebrew backgrounds to reference either:

1. An existing official origin feat (safe)
2. A homebrew origin feat (which must itself pass the feat balance test)

A homebrew background that grants a homebrew feat is essentially submitting two pieces of content, each needing separate evaluation.

---

## Testing Methodology

Background testing uses the standard party but modifies one character's background for the test. The test battery focuses on non-combat pillars:

**Social pillar:** Weighted skill check battery across Persuasion, Deception, Intimidation, Insight, Performance. Measures the background's contribution to face skill reliability.

**Exploration pillar:** Weighted skill check battery across Survival, Perception, Investigation (environmental), Athletics, Acrobatics, Stealth. Plus any movement or detection features from the origin feat.

**Investigation pillar:** Skill checks for Investigation, Perception, Insight, Arcana, History, Religion, Nature. Plus any information-gathering features from the origin feat.

**Combat pillar:** Minor. Most backgrounds contribute nothing to combat directly. The origin feat may have combat impact (Tough, Savage Attacker, Tavern Brawler, Magic Initiate spells), which is tested.

**Metrics:** Skill success rate, feat impact on combat outcomes (via delta from standard party baseline), novel capabilities the background unlocks.

---

## Validation Rules Specific to Backgrounds

1. **Ability score increase mode must be valid** (plus_2_plus_1 or plus_1_plus_1_plus_1).
2. **Eligible abilities list must contain exactly 3 abilities** (RAW constraint for plus_2_plus_1 mode) or all 6 (for plus_1_plus_1_plus_1 mode).
3. **Skill proficiencies list must contain exactly 2 skills** (RAW constraint).
4. **Tool proficiency must be exactly 1 tool** (RAW constraint).
5. **Origin feat must exist in the feat registry.**
6. **Starting equipment list should be reasonable** (not granting magic items, not granting legendary-tier items).

---

## Homebrew Background Additional Checks

1. **Origin feat power budget:** If homebrew background grants homebrew feat, the feat is evaluated separately. Background gets no automatic pass.
2. **Skill combo sanity:** Flagging skill combinations that are unusually powerful together (e.g., Stealth + Perception + Insight from one background would be overtuned).
3. **Starting equipment value:** Starting gold/equivalent should not exceed ~50 gp for tier 1 balance.

---

## Open Questions for Liege Review

1. **Should we score backgrounds by skill combo synergies?** A background granting Stealth + Perception is more useful than Athletics + Intimidation for most campaigns. My recommendation: yes, note synergistic combos in scoring but do not penalize them heavily (WotC does some of this).

2. **Do homebrew backgrounds get tested for all their feat options if the feat has choices (like Magic Initiate)?** Magic Initiate Wizard grants different spells per author. Do we evaluate the background with "the best likely spell choice" or "the worst likely spell choice" or "average"? My recommendation: author declares the specific spell choices, and those are what get tested.

3. **Backgrounds vs subclasses: should we test them using the same standard party and same non-combat batteries, or is there a meaningful methodology difference?** My recommendation: same batteries, different interpretations. A background's contribution is smaller than a subclass's, so we expect smaller deltas.

4. **Are we comfortable that backgrounds are the least rigorous test in the framework?** They have simpler structure and mostly derive value from the origin feat. The test methodology is correspondingly simpler. Not a concern as long as we acknowledge it.
