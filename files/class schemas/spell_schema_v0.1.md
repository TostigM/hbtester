# Spell Content Schema — Proposal v0.1

## Purpose

Spells are the most complex content type in the framework because they encode a vast range of effects (damage, healing, control, utility, movement, defense, information, combat buffs, and on). The schema must handle all of these uniformly while remaining authorable.

This document also defines the **spellcasting mechanics** for characters — how spell slots, preparation, and casting interact with the engine. Per Liege's direction, the spellcasting schema is part of the standard character schema even if the character does not natively cast.

---

## Design Principles

Same as prior schemas, plus two specific to spells:

**Effect atomicity.** A spell's effects are decomposed into atomic effect primitives (damage instance, save request, condition apply, movement grant, etc.). The engine implements each primitive once; spells compose them.

**Intent tagging.** Every spell is tagged with its primary intent (damage, healing, control, buff, debuff, utility, movement, information, defense, summon, transportation). This drives behavior AI and test harness routing.

---

## Top-Level Spell Structure

```yaml
schema_version: "0.1"
content_type: "spell"
id: "fireball"
display_name: "Fireball"
source: "PHB_2024"
version: "2024"
author: "Wizards of the Coast"
flavor_text: "A bright streak flashes from your pointing finger..."

# Core spell properties
level: 3                                 # 0 for cantrips, 1-9 for leveled spells
school: "evocation"                      # abjuration, conjuration, divination, enchantment, evocation, illusion, necromancy, transmutation
casting_time: "action"                   # action, bonus_action, reaction, minutes:N, hours:N, rounds:N
range: "150_feet"                        # self, touch, N_feet, unlimited, etc.
components:
  verbal: true
  somatic: true
  material: true
  material_description: "a ball of bat guano and sulfur"
  material_cost_gp: 0                    # for costly materials
  material_consumed: false               # whether material is consumed on casting
duration: "instantaneous"                # instantaneous, 1_round, concentration_up_to_N, N_minutes, N_hours, until_dispelled, etc.
concentration: false                     # true if duration is concentration
ritual: false

# Classes that have this spell on their list (used for homebrew compatibility checks)
class_lists: ["wizard", "sorcerer"]

# Primary intent tags (drives behavior AI and test routing)
intent_tags: ["damage", "aoe"]

# Effect description (machine-readable)
effects: [ ... ]

# Area of effect (if any)
area_of_effect:
  shape: "sphere"                        # sphere, cube, cone, line, cylinder, or null for single-target
  size_feet: 20

# Target specification
target:
  type: "point_in_range"                 # point_in_range, creature, creatures_up_to_N, self, etc.
  target_count: 1                        # N, "all_in_area", etc.
  target_restrictions: []                # "must_see", "humanoid_only", etc.

# Higher-level slot usage (if spell scales)
upcast_scaling: [ ... ]
```

---

## Effect Primitives

Effects are the atomic operations a spell performs. A spell is a list of one or more effects, executed in order (or conditionally based on save results).

### Effect Types

**Damage effects**
- `damage_save_half`: target makes save; half damage on success
- `damage_save_none`: target makes save; no damage on success
- `damage_attack_roll`: caster makes attack roll; damage on hit
- `damage_auto`: damage applies automatically (like Magic Missile)

**Healing effects**
- `healing`: restores HP to target
- `temp_hp`: grants temporary HP
- `revive`: revives a creature at 0 HP (Revivify, Raise Dead)

**Condition effects**
- `apply_condition`: applies a 5e condition (charmed, frightened, etc.)
- `apply_condition_save_negates`: target saves or gets condition
- `apply_condition_save_ends`: condition applied; save each turn to remove

**Control effects**
- `movement_restriction`: speed reduction, prone, restrained, etc.
- `forced_movement`: push, pull, teleport target
- `area_denial`: creates zone with hazard (Wall of Fire, Spike Growth)

**Buff/debuff effects**
- `stat_modifier`: modifies a target stat (AC, attack, damage, save)
- `advantage_grant`: grants advantage on specific roll types
- `disadvantage_impose`: imposes disadvantage on specific roll types

**Utility effects**
- `movement_grant`: grants movement speed or type (Fly, Jump)
- `sensory_grant`: grants darkvision, truesight, etc.
- `info_reveal`: reveals information (Detect Magic, Identify)
- `teleport`: caster or target teleports
- `summon`: creates a creature or object

**Defensive effects**
- `damage_reduction`: reduces incoming damage
- `damage_resistance_grant`: grants resistance to a damage type
- `condition_immunity_grant`: immunity to specific condition

**Meta effects**
- `counterspell`: stops a spell being cast
- `dispel_magic`: removes magical effects

### Example: Fireball Effects

```yaml
effects:
  - type: "damage_save_half"
    damage: "8d6"
    damage_type: "fire"
    save_ability: "DEX"
    save_dc: "caster_spell_save_dc"
    affects: "all_creatures_in_area"
```

### Example: Cure Wounds Effects

```yaml
effects:
  - type: "healing"
    amount: "2d8 + spellcasting_modifier"
    target: "single_touched_creature"
```

### Example: Hold Person Effects

```yaml
effects:
  - type: "apply_condition_save_ends"
    condition: "paralyzed"
    target_restriction: "humanoid"
    save_ability: "WIS"
    save_dc: "caster_spell_save_dc"
    save_frequency: "end_of_each_target_turn"
    duration_cap: "1_minute_or_concentration"
```

### Example: Spirit Guardians Effects

```yaml
effects:
  - type: "area_denial"
    shape: "sphere_15ft_radius_centered_on_caster"
    moves_with_caster: true
    effect_on_enter_or_start_turn:
      - type: "damage_save_half"
        damage: "3d8"
        damage_type: "radiant_or_necrotic_chosen_at_cast"
        save_ability: "WIS"
    secondary_effect: "speed_halved_while_in_area"
    duration: "concentration_up_to_10_min"
```

---

## Upcast Scaling

Many spells gain effects when cast with higher-level slots. This is modeled explicitly.

### Example: Cure Wounds Upcast

```yaml
upcast_scaling:
  - slot_level: 2
    changes:
      "effects[0].amount": "3d8 + spellcasting_modifier"
  - slot_level: 3
    changes:
      "effects[0].amount": "4d8 + spellcasting_modifier"
  - slot_level: 4
    changes:
      "effects[0].amount": "5d8 + spellcasting_modifier"
  # Each additional slot level adds 1d8
  - slot_level: "any_higher"
    formula: "slot_level + 1 d8"
```

### Example: Fireball Upcast

```yaml
upcast_scaling:
  - slot_level: 4
    changes:
      "effects[0].damage": "9d6"
  - slot_level: 5
    changes:
      "effects[0].damage": "10d6"
  # etc. through 9th level
  - slot_level: "any_higher"
    formula: "(slot_level + 5) d6"
```

---

## Cantrip Scaling

Cantrips scale with character level, not slot level. They use `character_level_scaling` instead of `upcast_scaling`.

### Example: Fire Bolt

```yaml
effects:
  - type: "damage_attack_roll"
    damage: "1d10"
    damage_type: "fire"
    to_hit: "spellcasting_modifier + proficiency"
    range: "120_feet"

character_level_scaling:
  - at_level: 5
    changes:
      "effects[0].damage": "2d10"
  - at_level: 11
    changes:
      "effects[0].damage": "3d10"
  - at_level: 17
    changes:
      "effects[0].damage": "4d10"
```

---

## Spellcasting Schema for Characters

Separate from the spell schema itself, characters need spellcasting data. This is the schema added to any character who can cast spells (through class, subclass, feat, or item).

```yaml
spellcasting:
  # Primary spellcasting source
  primary:
    source: "class"                        # class, subclass, feat, item
    class_id: "wizard"
    spellcasting_ability: "INT"
    progression: "full"                    # full, half, third, pact
    
    # Spells known/prepared
    spellbook: ["fire_bolt", "mage_armor", ...]    # wizard only
    cantrips_known: ["fire_bolt", "ray_of_frost", "mage_hand"]
    spells_prepared: ["shield", "mage_armor", ...]  # at current level
    
    # Spell slots
    spell_slots:
      1: { max: 4, current: 4 }
      2: { max: 3, current: 3 }
      3: { max: 3, current: 3 }
    
    # Focus used
    spellcasting_focus: "wand_of_the_war_mage"

  # Additional sources (feats, items, multiclass)
  additional:
    - source: "feat"
      feat_id: "magic_initiate_wizard"
      spells: ["find_familiar"]
      uses_per: "long_rest"
      uses_remaining: 1

  # Derived stats (computed by engine)
  derived:
    spell_save_dc: 15
    spell_attack_bonus: 7
```

For non-casting characters, the spellcasting section is present but empty or minimal (only populated if they have cantrips from feats, racial spells, etc.).

---

## Spell Intent Tags and Test Routing

Each spell has one or more intent tags that determine which test batteries evaluate it.

**Intent tag vocabulary:**
- `damage` — direct damage spells (Fireball, Fire Bolt, Magic Missile)
- `healing` — healing spells (Cure Wounds, Heal, Mass Heal)
- `control` — save-or-suck, battlefield control (Hold Person, Web, Wall of Force)
- `buff` — ally enhancement (Bless, Haste, Aid)
- `debuff` — enemy weakening (Bane, Slow, Bestow Curse)
- `utility` — problem-solving outside damage/healing (Knock, Dispel Magic)
- `movement` — travel/escape (Misty Step, Dimension Door, Teleport)
- `information` — divination (Detect Magic, Scrying, Commune)
- `defense` — damage mitigation (Shield, Absorb Elements, Protection from Energy)
- `summon` — creates allies (Summon X spells, Conjure Animals)
- `transportation` — long-range travel (Teleportation Circle, Plane Shift)
- `aoe` — affects multiple targets (meta-tag, combines with damage/control/etc.)
- `concentration` — meta-tag noting concentration requirement
- `ritual` — meta-tag noting ritual casting

**Test routing based on tags:**

- `damage` spells → combat test battery, damage output metric
- `healing` spells → combat test battery, healing output metric
- `control` spells → combat test battery, encounter-shortening metric
- `utility` → exploration/investigation batteries
- `information` → investigation battery primarily
- `movement`, `transportation` → exploration battery
- `buff`, `debuff`, `defense` → combat battery (measured as ally/enemy outcome delta)
- `summon` → combat battery (measured with extra combatant added)

---

## Spell Scoring and Balance Evaluation

Unlike species, spells are evaluated primarily through simulation rather than score calculation, because spell value is context-dependent in ways that are hard to capture in point values.

However, we do perform upfront sanity checks:

**Damage sanity:** A spell's damage output is compared to the 5e damage-per-spell-level expectation. Rough guidelines:
- Cantrip: 1d10 damage at 1-4, 2d10 at 5-10, 3d10 at 11-16, 4d10 at 17-20 (Fire Bolt is the baseline)
- 1st level: 3d6-3d8 average damage
- 3rd level: ~8d6 (Fireball) is the canonical benchmark
- 5th level: ~8d10 (Cone of Cold)
- 9th level: Meteor Swarm-tier (20d6 area + 20d6 more)

Homebrew spells with damage above the expected curve are flagged.

**Save-or-suck sanity:** Spells that incapacitate on a failed save are checked for:
- Save frequency (every turn vs only at cast is a big difference)
- Targets affected (single vs multiple)
- Save DC derivation (should use caster's spell save DC, not a custom number)

**Resource cost sanity:** Spells should cost appropriate action economy (action, bonus action, or reaction). Homebrew that makes powerful effects "no action" is flagged.

**Duration sanity:** Long-duration effects should require concentration unless they are minor or have other costs.

---

## Validation Rules Specific to Spells

1. **Level must be 0 (cantrip) to 9.**
2. **School must be one of the 8 valid magic schools.**
3. **Casting time must be a recognized type** (action, bonus action, reaction, 1 minute, etc.).
4. **Range must be well-formed** (self, touch, N feet, etc.).
5. **Components must have proper boolean flags and description for materials.**
6. **Duration must match concentration flag** (if concentration true, duration must start with "concentration_").
7. **Class lists must reference valid classes.**
8. **Effect types must all be recognized primitives.**
9. **Upcast scaling referenced slots must be valid (spell level+1 through 9).**
10. **Cantrips must not have upcast scaling** (they use character level scaling).
11. **Leveled spells must not have character level scaling** (they use slot scaling).

---

## Homebrew Spell Additional Checks

1. **Damage vs level curve:** Flag spells with damage significantly above their slot level's expected output.
2. **Action economy:** Flag any spell that grants extra actions, reactions, or attacks without reasonable cost.
3. **Save-or-die:** Flag instant-kill spells below 9th level (they are supposed to be very high level).
4. **Concentration absence:** Flag long-duration buff or control spells that do not require concentration.
5. **Range anomaly:** Flag unusual range values (e.g., "1 mile" at low levels).

---

## Open Questions for Liege Review

1. **Are the effect primitives I listed sufficient?** I have covered damage, healing, control, utility, defense, information, and meta-effects. Some spells have novel mechanics (Wish, Simulacrum, Clone) that may need the `scripted_effect` escape hatch. Comfortable with that approach?

2. **Do we simulate every spell in the caster's prepared list, or only the ones we expect them to cast?** Simulating all of them is exhaustive but expensive. Simulating only "combat-useful" spells undersells utility spells. My recommendation: every spell the behavior AI would consider casting given the encounter type. Non-combat spells are evaluated in non-combat batteries.

3. **How do we score utility spells that almost never fire in combat?** Feather Fall has no combat value but prevents a party wipe once per campaign. Scoring it 0 in combat battery feels wrong. My recommendation: utility spells get their value from non-combat batteries primarily; their combat score is their rare-use emergency value.

4. **Does the intent tagging feel right?** This is the core of how the test harness routes spells to evaluations. If the tag vocabulary is wrong or missing categories, the whole system is off.

5. **Concentration handling.** Only one concentration spell at a time is a massive balance constraint. The engine must enforce it strictly. Flagging that this is a meaningful engine requirement, not just schema.

6. **Area of effect shape complexity.** Shapes like "a 60-foot line that you can bend" or "a 20-foot sphere that follows the caster" exist. The engine will need robust AoE handling. The schema supports it; the engine will need the implementation.
