# Class Content Schema — Proposal v0.1

## Purpose

Classes are the base chassis that subclasses attach to. A class defines everything common across its subclasses: hit die, proficiencies, base features, resource pools that all subclasses draw from, the progression table, and the level at which a subclass is chosen.

A class is not directly tested in the framework (subclasses are). But every character requires a class, and every subclass references a parent class. The class schema is the foundation beneath the subclass schema.

---

## Design Principles

Same as subclass schema: explicit, composable, declarative, versioned, mechanics separated from flavor.

One additional principle specific to classes: **classes define the shared vocabulary that subclasses reuse.** When a Fighter subclass grants "an additional use of Second Wind," it references the Second Wind pool defined by the Fighter class. The class schema is where these shared resources and features live.

---

## Top-Level Class Structure

```yaml
schema_version: "0.1"
content_type: "class"
id: "fighter"
display_name: "Fighter"
source: "PHB_2024"
version: "2024"
author: "Wizards of the Coast"
flavor_text: "Masters of martial combat..."

# Core mechanical properties
hit_die: "d10"
primary_ability_options: ["STR", "DEX"]    # one or more (Fighter is either)
saving_throw_proficiencies: ["STR", "CON"]
spellcasting_ability: null                   # or "INT", "WIS", "CHA", or "choice_in_subclass"
spellcasting_progression: null               # "full", "half", "third", "pact", "subclass_only", or null

# Proficiencies granted at level 1
starting_proficiencies:
  armor: ["light", "medium", "heavy", "shields"]
  weapons: ["simple", "martial"]
  tools: []
  skills:
    choose_count: 2
    choose_from: ["acrobatics", "animal_handling", "athletics", "history", "insight", "intimidation", "perception", "survival"]

# Starting equipment (in 2024, characters choose from a set or take starting gold)
starting_equipment:
  option_a: ["chain_mail", "martial_weapon_and_shield", "light_crossbow_with_bolts", "dungeoneers_pack", "2gp"]
  option_b: ["leather_armor", "longsword", "martial_weapon_two", "light_crossbow_with_bolts", "dungeoneers_pack"]
  # ... etc
  starting_gold_alternative: "155 gp"

# When subclass is chosen
subclass_choice_level: 3

# Class features that apply to all subclasses (not subclass-specific)
features: [ ... ]

# Resource pools defined by the class (subclasses may reference these)
resource_pools: [ ... ]

# Progression table (BAB-equivalent, proficiency bonus, feature unlocks, etc.)
progression_table: [ ... ]
```

---

## Feature Structure

Classes use the same feature schema as subclasses (same `feature_type` vocabulary). The difference is scope: class features apply to all characters of the class regardless of subclass.

Example class-level features for Fighter:

### Second Wind (level 1)

```yaml
- id: "second_wind"
  unlock_level: 1
  display_name: "Second Wind"
  feature_type: "custom_action"
  body:
    action_type: "bonus_action"
    resource_cost:
      pool: "second_wind_uses"
      amount: 1
    effect:
      - type: "self_healing"
        amount: "1d10 + fighter_level"
  scaling:
    - level: 5
      description: "Recover one use of Second Wind on short rest (not just long rest)"
    - level: 10
      pool_size_increase: 1    # now 3 uses per long rest
    - level: 15
      pool_size_increase: 1    # now 4 uses per long rest
```

### Action Surge (level 2)

```yaml
- id: "action_surge"
  unlock_level: 2
  display_name: "Action Surge"
  feature_type: "custom_action"
  body:
    action_type: "no_action"       # you simply gain an extra action on your turn
    resource_cost:
      pool: "action_surge_uses"
      amount: 1
    effect:
      - type: "grant_additional_action"
        count: 1
    restriction: "once_per_turn"
  scaling:
    - level: 17
      pool_size_increase: 1        # 2 uses per short rest
```

### Extra Attack (level 5)

```yaml
- id: "extra_attack"
  unlock_level: 5
  display_name: "Extra Attack"
  feature_type: "attack_count_modifier"
  body:
    attack_action_count: 2         # total attacks per Attack action
  scaling:
    - level: 11
      attack_action_count: 3
    - level: 20
      attack_action_count: 4
```

### Indomitable (level 9)

```yaml
- id: "indomitable"
  unlock_level: 9
  display_name: "Indomitable"
  feature_type: "reaction"
  body:
    trigger: "fail_saving_throw"
    resource_cost:
      pool: "indomitable_uses"
      amount: 1
    effect:
      - type: "reroll_save"
  scaling:
    - level: 13
      pool_size_increase: 1        # 2 uses
    - level: 17
      pool_size_increase: 1        # 3 uses
```

### Weapon Mastery (level 1)

```yaml
- id: "weapon_mastery"
  unlock_level: 1
  display_name: "Weapon Mastery"
  feature_type: "passive_feature_grant"
  body:
    grant_type: "weapon_mastery_selection"
    count: 3
    eligible_weapons: "all_simple_and_martial"
  scaling:
    - level: 4
      count: 4
    - level: 10
      count: 5
    - level: 16
      count: 6
```

---

## Resource Pools

Classes define the resource pools their subclasses might draw from. Resource pools have a name, max size, refresh condition, and optional scaling.

```yaml
resource_pools:
  - id: "second_wind_uses"
    display_name: "Second Wind"
    max_size: 2
    refresh: "long_rest"
    partial_refresh:
      - condition: "short_rest"
        amount: 1
        unlock_level: 5
    scaling:
      - level: 10
        max_size: 3
      - level: 15
        max_size: 4

  - id: "action_surge_uses"
    display_name: "Action Surge"
    max_size: 1
    refresh: "short_rest"
    scaling:
      - level: 17
        max_size: 2

  - id: "indomitable_uses"
    display_name: "Indomitable"
    max_size: 1
    refresh: "long_rest"
    scaling:
      - level: 13
        max_size: 2
      - level: 17
        max_size: 3

  - id: "superiority_dice"
    display_name: "Superiority Dice"
    max_size: 0                    # subclass-defined if present
    die_size: "d8"
    refresh: "short_rest"
    gated_by_subclass: "battle_master"
```

The last example shows how a subclass-specific pool can be declared at the class level but gated by subclass. Alternatively, the subclass defines the pool itself. Both patterns work; we pick one as standard. My recommendation: subclass-specific pools are defined by the subclass, not the class, unless multiple subclasses share them. The Battle Master is the only Fighter subclass with Superiority Dice, so it defines the pool itself.

---

## Progression Table

The progression table enumerates, for every level 1 through 20, the proficiency bonus, features gained, and any class-specific columns (spell slots, cantrips known, etc.).

```yaml
progression_table:
  - level: 1
    proficiency_bonus: 2
    features: ["fighting_style", "second_wind", "weapon_mastery"]
  - level: 2
    proficiency_bonus: 2
    features: ["action_surge", "tactical_mind"]
  - level: 3
    proficiency_bonus: 2
    features: ["subclass"]        # subclass chosen here
  - level: 4
    proficiency_bonus: 2
    features: ["asi"]
    weapon_mastery_count: 4
  - level: 5
    proficiency_bonus: 3
    features: ["extra_attack", "tactical_shift"]
  - level: 6
    proficiency_bonus: 3
    features: ["asi"]             # Fighter bonus feat level
  - level: 7
    proficiency_bonus: 3
    features: []                  # subclass feature here for BM
  - level: 8
    proficiency_bonus: 3
    features: ["asi"]
  - level: 9
    proficiency_bonus: 4
    features: ["indomitable", "tactical_master"]
  - level: 10
    proficiency_bonus: 4
    features: []                  # subclass feature here for BM
    weapon_mastery_count: 5
    second_wind_uses: 3
  - level: 11
    proficiency_bonus: 4
    features: ["extra_attack_improved"]  # 3 attacks
  - level: 12
    proficiency_bonus: 4
    features: ["asi"]
  - level: 13
    proficiency_bonus: 5
    features: ["studied_attacks"]
    indomitable_uses: 2
  - level: 14
    proficiency_bonus: 5
    features: ["asi"]             # Fighter bonus feat level
  - level: 15
    proficiency_bonus: 5
    features: []                  # subclass feature here for BM
    second_wind_uses: 4
  - level: 16
    proficiency_bonus: 5
    features: ["asi"]
    weapon_mastery_count: 6
  - level: 17
    proficiency_bonus: 6
    features: ["action_surge_improved"]  # 2 uses
    indomitable_uses: 3
  - level: 18
    proficiency_bonus: 6
    features: ["studied_attacks_improved"]
  - level: 19
    proficiency_bonus: 6
    features: ["epic_boon"]
  - level: 20
    proficiency_bonus: 6
    features: ["extra_attack_improved_2"]  # 4 attacks
```

---

## Example: Spellcasting Classes

For classes with spellcasting, the progression table includes spell slot columns and cantrip counts.

### Wizard

```yaml
progression_table:
  - level: 1
    proficiency_bonus: 2
    features: ["spellcasting", "ritual_adept", "arcane_recovery"]
    cantrips_known: 3
    spell_slots: {1: 2}
  - level: 2
    proficiency_bonus: 2
    features: ["scholar"]
    cantrips_known: 3
    spell_slots: {1: 3}
  - level: 3
    proficiency_bonus: 2
    features: ["subclass"]
    cantrips_known: 3
    spell_slots: {1: 4, 2: 2}
  # ... and so on
```

### Half-Casters (Paladin, Ranger, Artificer)

Use the half-caster spell slot progression, start spellcasting at a later level (typically level 2 for paladin, level 1 for 2024 ranger, level 1 for artificer).

### Warlock (Pact Magic)

Uses the unique Pact Magic progression where all slots are the same level and refresh on short rest. The class schema captures this difference:

```yaml
spellcasting_progression: "pact"
pact_magic_slots:
  level_1: {count: 1, slot_level: 1}
  level_2: {count: 2, slot_level: 1}
  level_3: {count: 2, slot_level: 2}
  # ... through level 20
```

---

## Class Features vs Subclass Features

Some features conflict in where they should live. A rule of thumb:

**Class feature if:** All subclasses of the class get it (Second Wind, Extra Attack, Spellcasting).

**Subclass feature if:** Only some subclasses get it (Combat Superiority is Battle Master only, Spirit Guardians-like auras are cleric subclass specific, Bladesinger's Bladesong is only for that wizard subclass).

**Gray area:** Features that some subclasses replace or override. The 2024 Monk's Flurry of Blows can be modified by subclass (Warrior of Shadow's different flurry). In this case, the class defines the base feature, and the subclass declares an "override" or "modification" of it.

```yaml
# Subclass feature that modifies a class feature
- id: "shadow_flurry_mod"
  unlock_level: 3
  display_name: "Shadow's Flurry"
  feature_type: "scripted_feature"
  body:
    modifies_feature: "flurry_of_blows"
    modification: "add_option_to_teleport_self_with_flurry"
```

---

## Starting Equipment Handling

In 2024 PHB, starting equipment for each class is a choice between a predefined set or starting gold. For simulation, we need to lock one choice.

My recommendation: each class schema includes the RAW starting equipment options, but standard party characters use Option A (most common / martial-friendly) unless otherwise specified.

For homebrew testing, the user's submission includes which starting package they use. Not a test variable, just a setup parameter.

---

## Validation Rules Specific to Classes

In addition to general schema validation:

1. **Hit die must be valid** (d6, d8, d10, d12).
2. **Saving throw proficiencies must be exactly two** (RAW constraint).
3. **Subclass choice level must be between 1 and 3** (standard), with special handling if the class has unusual timing.
4. **Progression table must include all 20 levels.**
5. **Proficiency bonus must match the standard 5e progression** (2-2-2-2-3-3-3-3-4-4-4-4-5-5-5-5-6-6-6-6).
6. **Total ASI/feat count must match class definition** (Fighters get bonus feats at 6 and 14; all classes get ASI at 4, 8, 12, 16 and Epic Boon at 19).
7. **Spellcasting progression must be one of the defined types** (full, half, third, pact, subclass_only, null).

---

## Homebrew Classes

Homebrew classes are harder to balance than homebrew subclasses because they define the base chassis. A homebrew class with too many features, wrong hit die, or broken spell progression can dwarf any official class.

For homebrew classes, additional sanity checks apply:

1. **Feature count per level** should fall within the range of official classes (flagged if >2 standard deviations).
2. **Hit die** compared against class role (martials get d10 or d12, half-casters d10, full casters d6 or d8).
3. **Spell progression type** must match feature profile (a full-caster class gets fewer combat features).
4. **ASI/feat count** must be exactly what the standard class progression provides, no extras.

Homebrew classes would get their own test battery, separate from subclass testing. We have not scoped this explicitly, but it is a likely Phase 5 extension.

---

## Open Questions for Liege Review

1. **Are there class-level features I am missing?** I have focused on mechanical features but classes also include things like "starting languages" or "expertise selection at certain levels." Should these be captured in the schema or left as implicit (every class gets the default languages; we do not simulate language interactions)?

2. **Should the class schema include out-of-combat class features explicitly?** Rogue's Reliable Talent, Ranger's Natural Explorer equivalents, Druid's Druidcraft-style utility. Most of these do not matter for combat simulation but matter for exploration/investigation testing.

3. **How do we handle classes that change significantly mid-career?** Druid's Wild Shape completely changes combat mechanics at high levels. The feature_type system handles it, but the behavior AI complexity is non-trivial. Flagging for architecture spec discussion.

4. **Do homebrew classes need the same validation strictness as homebrew subclasses?** My recommendation is yes, plus additional sanity checks on base chassis. Acceptable?
