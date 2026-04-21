# Species Content Schema — Proposal v0.1

## Purpose

Species (called "lineage" or "race" in older rules; "species" in 2024) define heritable traits a character has from birth. In 2024 rules, species grant traits but do NOT grant ability score increases (those come from backgrounds). This significantly reduces the mechanical weight of species compared to 2014 rules.

Species testing evaluates homebrew species against the WotC species distribution using a point-based scoring algorithm (per Liege's direction).

---

## Design Principles

Same as prior schemas, plus one new principle specific to species:

**Trait scoring must be explicit and auditable.** Each trait has a numerical value. The total trait value is the species's "power budget." Homebrew species are compared to the WotC distribution by total budget and by budget composition (how traits are distributed across trait types).

---

## Top-Level Species Structure

```yaml
schema_version: "0.1"
content_type: "species"
id: "human"
display_name: "Human"
source: "PHB_2024"
version: "2024"
author: "Wizards of the Coast"
flavor_text: "Humans are the most adaptable..."

# Physical properties
creature_type: "humanoid"               # affects spell targeting (e.g., Hold Person)
size: "medium"                          # tiny, small, medium, large
speed:
  walk: 30
  fly: 0
  swim: 0
  climb: 0
  burrow: 0

# Lifespan and narrative properties (ignored by engine)
lifespan_average: 80
size_range: "5 to 6 feet"

# Traits granted at level 1
traits: [ ... ]

# Optional: ability that grows with character level
scaling_traits: [ ... ]
```

---

## Trait Structure

Traits use the same `feature_type` vocabulary as class/subclass features, with some species-specific types.

Species-specific trait types (additions to the general feature vocabulary):

- `species_ability`: named species-defining ability (e.g., Dwarven Resilience, Elven Accuracy's predecessor)
- `skill_proficiency_grant`: grants proficiency in specific skills
- `damage_resistance`: natural resistance to a damage type
- `condition_resistance`: natural advantage on saves against specific conditions
- `origin_feat_grant`: 2024 Human specifically grants an origin feat from species

Most other trait types come from the general vocabulary.

---

## Example: Human (2024)

```yaml
id: "human"
display_name: "Human"
creature_type: "humanoid"
size: "medium"
speed: { walk: 30 }

traits:
  - id: "human_resourceful"
    display_name: "Resourceful"
    feature_type: "passive_feature_grant"
    body:
      grant: "heroic_inspiration_on_long_rest"
    score: 2

  - id: "human_skillful"
    display_name: "Skillful"
    feature_type: "skill_proficiency_grant"
    body:
      choose_count: 1
      choose_from: "any_skill"
    score: 2

  - id: "human_versatile"
    display_name: "Versatile"
    feature_type: "origin_feat_grant"
    body:
      feat_category: "origin"
      author_chooses: true
    score: 4

total_trait_score: 8
```

---

## Example: Elf (2024)

```yaml
id: "elf"
display_name: "Elf"
creature_type: "humanoid"
size: "medium"
speed: { walk: 30 }

traits:
  - id: "elven_darkvision"
    display_name: "Darkvision"
    feature_type: "sensory_feature"
    body:
      sense: "darkvision"
      range: 60
    score: 3

  - id: "elven_fey_ancestry"
    display_name: "Fey Ancestry"
    feature_type: "condition_resistance"
    body:
      condition: "charmed"
      effect: "advantage_on_saves"
    score: 2

  - id: "elven_keen_senses"
    display_name: "Keen Senses"
    feature_type: "skill_proficiency_grant"
    body:
      skill_choice: ["insight", "perception", "survival"]
      choose_count: 1
    score: 1

  - id: "elven_trance"
    display_name: "Trance"
    feature_type: "passive_feature_grant"
    body:
      grant: "4_hour_rest_equivalent_to_8_hour_sleep"
    score: 1     # minor benefit in most campaigns

  - id: "elven_lineage"
    display_name: "Elven Lineage"
    feature_type: "scripted_feature"
    body:
      description: "Choose one of three lineages (Drow, High Elf, Wood Elf), each with unique traits"
      # Lineage options detailed below
    score: 4     # represents average lineage value

# Sub-traits from lineage choice (one of three; each has own score)
lineage_options:
  drow:
    traits:
      - sensory_feature: { sense: "darkvision", range: 120, replaces: "elven_darkvision" }
      - spell_known: "dancing_lights" # cantrip
      - spell_known_at_3: "faerie_fire"
      - spell_known_at_5: "darkness"
    score: 5

  high_elf:
    traits:
      - spell_known: "prestidigitation" # cantrip, choice of wizard cantrip
      - ritual_caster_partial: "one_1st_level_wizard_spell_as_ritual"
    score: 3

  wood_elf:
    traits:
      - speed_increase: { walk: 35 }
      - skill_proficiency: "stealth"
      - spell_known: "druidcraft"
      - spell_known_at_3: "longstrider"
      - spell_known_at_5: "pass_without_trace"
    score: 4

# Average lineage score for budgeting comparison
total_trait_score: 11    # base (7) + avg lineage (4)
# Range: 10 - 12 depending on lineage
```

---

## Trait Scoring Algorithm

This is where the point-based scoring Liege requested lives. Each trait has a score representing its balance value. Scores are derived from the combat and utility value of the trait across a campaign.

### Proposed Score Values by Trait Category

**Senses (vision/awareness)**
- Darkvision 60 ft: 3 points
- Darkvision 120 ft: 5 points
- Blindsight 10 ft: 4 points
- Blindsight 30 ft: 7 points
- Truesight: 10 points (legendary-tier; should not appear on species)
- Tremorsense 30 ft: 5 points

**Movement**
- Walking speed 30 ft: 0 points (baseline, all species get it)
- Walking speed 35 ft: 2 points
- Walking speed 40 ft: 4 points
- Swim speed equal to walk: 2 points
- Climb speed equal to walk: 3 points
- Burrow speed equal to walk: 4 points
- Fly speed equal to walk: 8 points (major tier 1 advantage)
- Fly speed but "cannot end turn in air": 5 points (nerfed flying)

**Damage & Conditions**
- Resistance to one common damage type (acid/cold/fire/lightning/poison): 3 points
- Resistance to one rare damage type (psychic/radiant/necrotic): 4 points
- Resistance to physical damage (slash/pierce/bludgeon): 6 points
- Immunity to one condition: 3 points
- Advantage on saves vs one condition: 2 points
- Advantage on saves vs multiple conditions: 3 points
- Immunity to exhaustion: 4 points (strong; should be rare)

**Skills & Proficiencies**
- One skill proficiency (fixed): 1 point
- One skill proficiency (chosen by character): 2 points
- One tool proficiency: 1 point
- One language (beyond Common): 0.5 points
- Weapon proficiencies (if normally gated): 2 points per weapon category
- Armor proficiency upgrade: 3 points

**Spellcasting Grants**
- One cantrip (chosen): 2 points
- One cantrip (fixed): 1 point
- Innate spell 1/long rest (level 1): 2 points
- Innate spell 1/long rest (level 2): 3 points
- Innate spell 1/long rest (level 3): 4 points
- Ritual casting partial: 2 points

**Defensive Traits**
- Natural armor or armor-equivalent: varies (scored based on AC contribution)
- Heroic inspiration on long rest: 2 points
- Rerolls once per day: 1 point
- Temporary HP on trigger: varies (1-3 points based on HP amount and trigger frequency)

**Action Economy**
- Extra attack on crit: 3 points
- Bonus action ability: 3-5 points based on effect
- Reaction ability (defensive): 3-5 points
- Reaction ability (offensive): 4-6 points

**Feats**
- Origin feat (character chooses): 4 points
- Origin feat (fixed specific feat): 3 points

**Utility**
- Improved rest mechanics (Trance etc): 1 point
- Advantage on specific check type (e.g., grapple): 2 points
- Permanent minor magic item equivalent: 2-4 points based on item

### Total Budget Ranges

Based on scoring official 2024 species:

- Standard species: 8-12 points (Human: 8, Elf: 11, Dwarf: ~10)
- Notable outliers to investigate: species scoring >13 may be overtuned; species scoring <7 may be undertuned

### Homebrew Species Evaluation

1. Calculate total trait score.
2. Compare to WotC distribution (mean ~10, reasonable range 8-12).
3. Flag if outside 8-12 range as warning.
4. Hard fail if outside 5-15 range (very likely broken).

### Important Caveats

**Context-dependent value.** Darkvision is worth 3 points generally, but in a campaign that spends 80% of time in daylight, it is worth 0.5 points. In a subterranean campaign, it is worth 6 points. The scoring assumes "typical campaign" context and users are told this.

**Synergy value.** Some traits are worth more combined than separately (Stealth proficiency + Pass Without Trace known = better than either alone). The additive scoring ignores this. We note it as a known limitation.

**Impact at different tiers.** Flight at level 1 is worth 8 points; at level 11 when everyone can cast Fly, it is worth 2. The scoring uses tier 1 values. Users are told this.

These caveats do not break the scoring; they explain why it is a guideline and not an oracle.

---

## Scaling Traits

Some species gain abilities at later levels (like Elf's innate spell known at levels 3 and 5). These are modeled as scaling_traits:

```yaml
scaling_traits:
  - at_level: 3
    trait: "drow_faerie_fire"
    feature_type: "spell_grant"
    body:
      spell: "faerie_fire"
      uses_per: "long_rest"
      uses_count: 1
    score_addition: 2

  - at_level: 5
    trait: "drow_darkness"
    feature_type: "spell_grant"
    body:
      spell: "darkness"
      uses_per: "long_rest"
      uses_count: 1
    score_addition: 2
```

Scaling trait scores add to base trait scores for total budget evaluation.

---

## Validation Rules Specific to Species

1. **Size must be valid** (tiny, small, medium, large; huge+ not permitted for PC species without very strong justification).
2. **Creature type must be valid** (humanoid, fey, construct, undead, celestial, fiend, etc. — most PCs are humanoid).
3. **Walking speed must be between 20 and 40 ft** (25 for small species, 30 standard, 35-40 for species with mobility focus).
4. **Fly speed on level-1 species requires justification** (most WotC species do not grant level-1 flight without restrictions).
5. **Total trait score must fall within the acceptable range** (warning 8-12, hard fail outside 5-15).
6. **No species grants more than one ability score increase directly** (2024 rules removed these; any homebrew species with direct ASIs is rejected).

---

## Open Questions for Liege Review

1. **Are the score values I proposed reasonable?** They are my first draft based on a sense of comparative value. They need calibration: ideally we score all WotC species and tune values until WotC species cluster within 8-12 total.

2. **Should scoring be empirical or declared?** Option A: we score traits and assign values upfront (current proposal). Option B: we run simulations and derive scores from observed performance impact. Option A is simpler; Option B is more rigorous but requires the simulation to exist. My recommendation: start with Option A, validate with Option B once sim exists.

3. **Do we score by total or by category balance?** A species could hit 10 points total but all in offensive traits (no defensive value). Is that balanced or not? My recommendation: score by total AND by category distribution. Flag species that are wildly imbalanced across categories even if total is fine.

4. **How do we handle species with narrative/flavor-heavy traits that have little mechanical weight?** A trait that says "you can hold your breath for an hour" is 0.5 points mechanically but adds character. Should these count in the total? My recommendation: yes, as negligible score additions (0.5 or 1 point), so authors cannot hide mechanical value under "flavor."

5. **Should we test species performance empirically even with scoring?** Scoring is a pre-test sanity check. Actual simulation might reveal a species that scores 10 but performs as 15 due to combo effects. My recommendation: both. Scoring is the first filter; simulation is the second.
