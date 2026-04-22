# Monster Content Schema — Proposal v0.1

## Purpose

Monsters are the opposition in combat encounters. The schema covers stat blocks, actions, bonus actions, reactions, legendary actions, lair actions, regional effects, spellcasting (for monsters that cast), and all associated mechanics. This is the most content-heavy schema because monsters are diverse.

Monster testing evaluates homebrew monsters against the standard party at character level equal to CR, CR ± 2, and CR ± 4 (per Liege's direction).

---

## Design Principles

Same as prior schemas, plus two specific to monsters:

**Full 2024 Monster Manual coverage.** The schema must handle every mechanical pattern in the 2024 MM, including unique boss mechanics (legendary actions, legendary resistance, lair actions, regional effects, recharge abilities).

**Encounter-centric, not creature-centric.** The schema models a monster instance in combat. Narrative flavor (society, lifespan, treasure, lore) is stored but ignored by engine. The engine cares about stat block, actions, and in-combat behavior.

---

## Top-Level Monster Structure

```yaml
schema_version: "0.1"
content_type: "monster"
id: "adult_red_dragon"
display_name: "Adult Red Dragon"
source: "MM_2025"
version: "2024"
author: "Wizards of the Coast"
flavor_text: "A colossal winged reptile..."

# Classification
creature_type: "dragon"                # aberration, beast, celestial, construct, dragon, elemental, fey, fiend, giant, humanoid, monstrosity, ooze, plant, undead
size: "huge"                           # tiny, small, medium, large, huge, gargantuan
subtype: null                          # e.g., "chromatic" for chromatic dragons
alignment: "chaotic_evil"              # for narrative; engine ignores

# Core stats
ac: 19
ac_source: "natural_armor"
hp:
  average: 256
  formula: "19d12 + 133"
hit_dice: "19d12"

# Speed
speed:
  walk: 40
  fly: 80
  swim: 0
  climb: 40
  burrow: 0

# Ability scores
abilities:
  STR: 27
  DEX: 10
  CON: 25
  INT: 16
  WIS: 13
  CHA: 21

# Save proficiencies (add prof bonus to these saves)
saving_throw_proficiencies: ["DEX", "CON", "WIS", "CHA"]

# Skill proficiencies
skill_proficiencies:
  - skill: "perception"
    bonus: 13              # explicit value (includes all modifiers)
  - skill: "stealth"
    bonus: 6

# Senses
senses:
  darkvision: 120
  blindsight: 60
  tremorsense: 0
  truesight: 0
  passive_perception: 23

# Languages
languages: ["common", "draconic"]

# Challenge Rating
challenge_rating: 17
proficiency_bonus: 6         # derived from CR; 5.5e MM includes explicitly
xp_value: 18000

# Damage/condition modifiers
damage_resistances: []
damage_immunities: ["fire"]
damage_vulnerabilities: []
condition_immunities: []

# Actions and abilities
traits: [ ... ]                    # always-on features, passive abilities
actions: [ ... ]                   # things the monster does on its turn
bonus_actions: [ ... ]             # bonus-action options
reactions: [ ... ]                 # reaction options
legendary_actions: [ ... ]          # legendary action options (if applicable)
legendary_resistance: { ... }       # legendary resistance (if applicable)
lair_actions: [ ... ]               # lair actions (if monster has a lair)
regional_effects: [ ... ]           # regional effects around lair

# Spellcasting (if monster casts spells)
spellcasting: { ... }

# Behavior hints for AI
behavior_hints: { ... }
```

---

## Traits

Traits are passive abilities always active. They use feature_type vocabulary consistent with other schemas.

```yaml
traits:
  - id: "fire_immunity"
    display_name: "Fire Immunity"
    feature_type: "damage_immunity"
    body:
      damage_type: "fire"

  - id: "legendary_resistance"
    display_name: "Legendary Resistance (3/Day)"
    feature_type: "scripted_trait"
    body:
      description: "If the dragon fails a saving throw, it can choose to succeed instead."
      uses_per_day: 3

  - id: "frightful_presence_trait"
    display_name: "Frightful Presence"
    feature_type: "aura"
    body:
      range: 120
      affects: "enemies"
      effect_on_enter_or_see_first_time:
        save: "WIS"
        dc: 19
        on_fail: "frightened_until_end_of_next_turn"
```

---

## Actions

Actions are what the monster does on its turn. Each has an activation type (action, which is default) and effect details.

### Multiattack (core to most monsters)

```yaml
actions:
  - id: "multiattack"
    display_name: "Multiattack"
    activation: "action"
    effect:
      type: "multiple_attacks"
      attacks:
        - action_id: "bite"
          count: 1
        - action_id: "claw"
          count: 2
```

### Weapon Attack

```yaml
  - id: "bite"
    display_name: "Bite"
    activation: "action"
    effect:
      type: "melee_weapon_attack"
      attack_bonus: 14
      reach: 10
      target: "one_target"
      damage:
        - die: "2d10"
          modifier: 8
          damage_type: "piercing"
        - die: "2d6"
          modifier: 0
          damage_type: "fire"
```

### Breath Weapon (AoE save-for-half)

```yaml
  - id: "fire_breath"
    display_name: "Fire Breath (Recharge 5-6)"
    activation: "action"
    recharge: "5_6"           # recharges on d6 roll of 5 or 6 at start of turn
    effect:
      type: "aoe_save_half"
      shape: "cone"
      size: 60
      damage: "18d6"
      damage_type: "fire"
      save: "DEX"
      dc: 21
```

---

## Legendary Actions

Legendary creatures act outside their turn via legendary actions. Typically 3 legendary action points per round, spent on listed abilities.

```yaml
legendary_actions:
  points_per_round: 3
  refresh: "start_of_own_turn"
  options:
    - id: "detect"
      cost: 1
      display_name: "Detect"
      effect:
        type: "skill_check"
        skill: "perception"
        purpose: "automatic_perception_check_against_visible_enemies"
    
    - id: "tail_attack"
      cost: 1
      display_name: "Tail Attack"
      effect:
        type: "melee_weapon_attack"
        attack_bonus: 14
        reach: 15
        damage:
          - die: "2d8"
            modifier: 8
            damage_type: "bludgeoning"
    
    - id: "wing_attack"
      cost: 2
      display_name: "Wing Attack"
      effect:
        type: "aoe_save_or_effect"
        shape: "adjacent_creatures_within_reach"
        save: "DEX"
        dc: 22
        on_fail:
          - damage: "2d6+8"
            damage_type: "bludgeoning"
          - condition: "prone"
        on_success: "no_effect"
      movement_granted: "fly_up_to_half_speed_after_effect"
```

---

## Legendary Resistance

```yaml
legendary_resistance:
  uses_per_day: 3
  effect: "fail_save_then_choose_to_succeed_instead"
  scope: "any_saving_throw"
```

---

## Lair Actions

Lair actions trigger on initiative count 20 (losing ties) in the creature's lair.

```yaml
lair_actions:
  trigger: "initiative_count_20_in_lair"
  options:
    - id: "magma_eruption"
      effect:
        type: "aoe_save_half"
        shape: "20ft_radius_sphere"
        placement: "anywhere_in_lair"
        damage: "7d10"
        damage_type: "fire"
        save: "DEX"
        dc: 15
    
    - id: "tremor"
      effect:
        type: "aoe_save_or_effect"
        shape: "lair_wide"
        save: "STR"
        dc: 15
        on_fail:
          - condition: "prone"
```

---

## Regional Effects

Passive effects in the region around the monster's lair. Ignored by combat simulation but listed for completeness.

```yaml
regional_effects:
  range_miles: 6
  effects:
    - id: "volcanic_activity"
      description: "Area within 6 miles has increased volcanic activity"
    - id: "fire_resistant_wildlife"
      description: "Creatures in the region are more resistant to fire"
```

---

## Spellcasting Monsters

Monsters that cast spells include a spellcasting block similar to character spellcasting, simplified for the creature context.

```yaml
spellcasting:
  caster_level: 18
  spellcasting_ability: "CHA"
  spell_save_dc: 21
  spell_attack_bonus: 13
  
  at_will:
    - "detect_magic"
    - "mage_hand"
  
  per_day:
    - spell: "counterspell"
      uses_per_day: 3
    - spell: "dispel_magic"
      uses_per_day: 3
    - spell: "fireball"
      uses_per_day: 3
  
  # Alternative: traditional spell slot system (for some monster types)
  spell_slots:
    1: { max: 4, remaining: 4 }
    2: { max: 3, remaining: 3 }
    3: { max: 3, remaining: 3 }
```

---

## Behavior Hints for Monsters

```yaml
behavior_hints:
  intelligence_tier: "high"               # low (animal), medium (humanoid typical), high (cunning)
  tactical_preferences:
    - "use_breath_weapon_when_multiple_enemies_in_cone"
    - "target_spellcasters_first_with_frightful_presence"
    - "stay_airborne_when_possible_for_advantage"
    - "use_legendary_actions_defensively_when_bloodied"
  retreat_behavior: "flee_when_at_25_percent_hp_if_intelligent"
  resource_conservation: "aggressive"      # aggressive, moderate, conservative
  combat_role: "solo_boss"                 # solo_boss, elite, skirmisher, soldier, minion
```

---

## Monster Categorization for Testing

Monsters are tested based on their role in combat:

**solo_boss:** Single high-CR monster expected to fight an entire party alone (adult dragons, most legendary creatures). Tested against party at levels equal to CR, CR-2, CR-4 (party overmatched), and CR+2, CR+4 (monster becomes speedbump).

**elite:** High-CR monster typically accompanied by minions, or appearing in pairs/trios (ogres, hill giants, liches with allies). Tested as standalone and as part of mixed encounter.

**skirmisher:** Medium-CR fast attacker (goblins, wolves, spectres at low tiers). Typically appears in groups of 3-6. Tested as group encounter.

**soldier:** Medium-CR durable fighter (orcs, hobgoblins, knights). Typically in groups of 3-5. Tested as group encounter.

**minion:** Low-CR mob monsters (goblins, kobolds, zombies). Tested in hordes of 8-20+.

**trap_monster:** Monsters with environmental or ambush mechanics (mimics, cloakers, invisible stalkers). Tested in specific scenario contexts.

---

## CR-to-Party-Level Mapping

Per Liege's direction, each monster is tested against standard party at:
- **Character level = CR:** Balanced encounter for that level
- **Character level = CR - 2:** Party is underleveled; tests if monster is viable overkill
- **Character level = CR - 4:** Party should flee; tests if monster is indeed dangerous at this gap
- **Character level = CR + 2:** Party is overleveled; tests if monster remains challenging
- **Character level = CR + 4:** Party should trivially win; tests if monster is truly underleveled now

For low-CR monsters (CR <= 4), the CR-4 test may go below level 1 and is skipped. For high-CR monsters (CR >= 17), the CR+4 test may go above level 20 and is skipped.

---

## Encounter Composition Variations

A single monster test actually runs multiple encounter compositions:

**Solo:** One monster vs standard party
**Pair:** Two monsters vs standard party (for elites and skirmishers)
**Squad:** 3-5 monsters vs standard party (for soldiers)
**Horde:** 6+ monsters vs standard party (for minions)
**Mixed:** Test monster as leader with weaker supporting monsters

Encounter difficulty guidelines from the 2024 DMG are used to calibrate numbers. Each composition is tagged for reporting.

---

## Validation Rules Specific to Monsters

1. **All stat fields present** (AC, HP, speed, ability scores, CR).
2. **CR must be a valid 5e CR** (0, 1/8, 1/4, 1/2, 1-30).
3. **Hit dice formula must match HP average** (roughly; some MM entries have imperfect alignment).
4. **Proficiency bonus must match CR** per 2024 MM (CR 0-4: +2; 5-8: +3; 9-12: +4; 13-16: +5; 17-20: +6; 21-24: +7; 25-28: +8; 29-30: +9).
5. **Legendary actions, if present, must have valid point budget.**
6. **Lair actions require the monster to be flagged as "has_lair".**
7. **Spellcasting, if present, must have valid DC and attack bonus formulas.**
8. **Damage types on attacks must be valid.**
9. **Creature type must be valid.**

---

## Homebrew Monster Additional Checks

1. **CR calculation sanity:** The 2024 DMG provides CR calculation guidelines. Homebrew monsters are checked against these; wide deviations are flagged.
2. **Action economy vs CR:** High-CR monsters should have multiattack or multiple action options. A CR 10 monster with only one single-target attack action is flagged as underpowered.
3. **Save DC vs CR:** Save DCs should be roughly 8 + proficiency + relevant ability mod. Outliers are flagged.
4. **Damage per round vs CR:** The DMG's monster-building tables specify expected DPR ranges. Homebrew outside these ranges is flagged.
5. **Legendary resistance presence:** CR 10+ solo bosses typically have legendary resistance. Its absence in homebrew bosses is flagged.
6. **Spellcasting overreach:** Homebrew monster-casters should not exceed what classes of the same caster-level equivalent can cast.

---

## Open Questions for Liege Review

1. **How complex should the "environment" be during monster testing?** An adult red dragon in its lava-filled lair (with lair actions) fights differently than one caught in a field. Standardizing environment across tests creates consistency; allowing lair-testing captures the creature's full power. My recommendation: test both conditions separately and report both.

2. **Do we simulate the "minion support" aspect of lower-CR monsters?** Goblins are much more dangerous with a Bugbear leader directing them. If testing a homebrew Goblin, do we test solo or in a squad with a leader? My recommendation: test both; a new monster's solo performance and squad performance are both useful data points.

3. **Monster behavior AI complexity.** High-intelligence monsters (dragons, liches, devils) should play strategically. Animal-intelligence monsters play instinctively. The behavior AI needs to handle both. Flagging for architecture spec.

4. **Legendary resistance as a meta-mechanic.** LR changes the entire dynamic of casters vs boss. The engine must track LR uses precisely. Flagging implementation importance.

5. **Monster scaling across tiers.** Some monsters are designed to be tier-specific. A dire wolf at tier 4 is trivial; an ancient dragon at tier 1 is a campaign-ending TPK. The CR-sweep testing reveals this but we should report findings in tier-appropriate context.

6. **Treasure and rewards:** Monster entries often specify treasure. Irrelevant for combat simulation but tracked for baseline documents. OK to ignore in simulation, include in reference documentation?
