# Subclass Authoring Guide v0.1

## Purpose

This guide provides the process, patterns, and quality standards for authoring subclass content files for the D&D Homebrew Balance Framework. The framework needs YAML-format subclass data for every released 5.5e subclass (approximately 61 total) to populate the baseline.

This guide exists to make that authoring work efficient, consistent, and machine-valid. It is designed to be used in VS Code with Claude Code assistance during Phase 2 implementation.

---

## Table of Contents

1. [Authoring Philosophy](#1-authoring-philosophy)
2. [Scope and Deliverable Definition](#2-scope-and-deliverable-definition)
3. [Prerequisites](#3-prerequisites)
4. [The Authoring Process](#4-the-authoring-process)
5. [Feature Type Selection Guide](#5-feature-type-selection-guide)
6. [Behavior AI Hints Guide](#6-behavior-ai-hints-guide)
7. [Worked Example: Champion Fighter](#7-worked-example-champion-fighter)
8. [Validation Checklist](#8-validation-checklist)
9. [Prioritization Order](#9-prioritization-order)
10. [Claude Code Prompt Template](#10-claude-code-prompt-template)
11. [Common Pitfalls](#11-common-pitfalls)
12. [Style Conventions](#12-style-conventions)

---

## 1. Authoring Philosophy

Subclass YAML files are **structured data**, not documentation. They are consumed by the engine to simulate combat. Every field must be precise; flavor text is optional and separate from mechanical bodies.

Three principles govern authoring:

**Fidelity over creativity.** The PHB text is authoritative. If the PHB says "once per turn," the YAML says `restriction: once_per_turn`. Do not paraphrase mechanics in ways that change their meaning. Do not add mechanics the PHB does not describe.

**Explicit over implicit.** If a feature has a resource cost, declare it. If it has a recharge condition, declare it. If it scales with level, declare the scaling. The engine cannot infer rules.

**Composable over bespoke.** Use the standard `feature_type` vocabulary wherever possible. Reserve `scripted_feature` for genuinely unique mechanics that the vocabulary cannot express. The worked example below shows when each choice is appropriate.

---

## 2. Scope and Deliverable Definition

### What a subclass YAML file contains

- Identification (id, name, source, class, version)
- Flavor text (optional, for human readers)
- Each feature with its unlock level, type, and mechanical body
- Resource pools the subclass introduces (if any)
- Spell list additions the subclass grants (if any)
- Behavior AI hints for tactical decisions
- Tags and categorization metadata

### What a subclass YAML file does NOT contain

- Full character sheets (those use the class schema and are generated per character per level)
- Narrative lore beyond brief flavor text
- Build recommendations or multiclass advice
- Optimization notes beyond behavior AI hints

### File path convention

```
content/subclasses/<class_id>/<subclass_id>.yaml
```

Examples:
- `content/subclasses/fighter/champion.yaml`
- `content/subclasses/wizard/evoker.yaml`
- `content/subclasses/cleric/life_domain.yaml`

---

## 3. Prerequisites

Before authoring a subclass YAML, you need:

1. **The canonical rules text.** The 2024 PHB entry for the subclass, or the source book entry for non-PHB subclasses (Heroes of Faerûn, Forge of the Artificer). Do not work from memory; do not work from tier lists or build guides. Use the actual rules text.

2. **The schema files.** `subclass_schema_v0.1.md` and `class_schema_v0.1.md` from the project root. These define the `feature_type` vocabulary and structural requirements.

3. **The parent class YAML.** The class this subclass attaches to must already exist as a YAML file. The subclass references the class by ID. If the class YAML does not exist yet, author it first.

4. **A validation environment.** The Python validator (to be built in Phase 2) checks schema compliance. During Phase 2 implementation, run it against every new subclass file before committing.

---

## 4. The Authoring Process

Follow this process for each subclass. It takes roughly 25-40 minutes of focused work for an average subclass, longer for complex ones (Battle Master, Moon Druid, Warlock subclasses with spell lists).

### Step 1: Gather the rules text (5 min)

Open the PHB entry for the subclass. Identify:
- At which levels subclass features unlock (typically 3, 6 or 7, 10 or 14, 14 or 17, sometimes more)
- The name of each feature
- The mechanical body of each feature
- Any subclass-specific spell list
- Any subclass-specific resource pool (rare)

For the 2024 rules, subclass feature levels are typically:
- **Fighter subclasses:** 3, 7, 10, 15, 18
- **Wizard subclasses:** 3, 6, 10, 14
- **Cleric subclasses:** 3, 6, 17 (plus always-prepared spells scaling at multiple levels)
- **Rogue subclasses:** 3, 9, 13, 17
- **Barbarian subclasses:** 3, 6, 10, 14
- **Bard subclasses:** 3, 6, 14
- **Druid subclasses:** 3, 6, 10, 14
- **Monk subclasses:** 3, 6, 11, 17
- **Paladin subclasses:** 3, 7, 15, 20
- **Ranger subclasses:** 3, 7, 11, 15
- **Sorcerer subclasses:** 3, 6, 14, 18
- **Warlock subclasses:** 3, 6, 10, 14
- **Artificer subclasses (Forge of the Artificer 2025):** 3, 5, 9, 15

Verify the levels against your source. Non-PHB subclasses may differ.

### Step 2: Draft the header (2 min)

Every subclass YAML begins with the same metadata structure:

```yaml
schema_version: "0.1"
content_type: "subclass"
id: "champion"
display_name: "Champion"
parent_class: "fighter"
source: "PHB_2024"
version: "2024"
author: "Wizards of the Coast"
flavor_text: "A Champion Fighter is relentless in battle..."
```

The `id` must be lowercase snake_case and unique across all subclasses. The `parent_class` must match the ID of an existing class YAML.

### Step 3: Enumerate features (10-15 min, bulk of the work)

For each feature unlock level, author a feature block. Use the `feature_type` that best matches the mechanic; see the Feature Type Selection Guide below.

Order features in the file by unlock level (ascending), then by importance within the level.

### Step 4: Declare resource pools (if applicable, 3-5 min)

If the subclass introduces its own resource pool (Superiority Dice for Battle Master, Wild Shape uses for Druid subclasses that modify them), declare it in the `resource_pools` section.

Most subclasses do not introduce new pools; they use the class's existing pools (Channel Divinity, spell slots, etc.).

### Step 5: Declare spell list additions (if applicable, 3-5 min)

Some subclasses grant always-prepared spells that are not in the base class list, or expand the prepared spells count. Declare these in the `spell_list` section.

### Step 6: Write behavior AI hints (5-10 min)

Describe how the subclass should make tactical decisions. See the Behavior AI Hints Guide below.

### Step 7: Validate (3-5 min)

Run the schema validator. Fix any errors. Run the sanity checks (e.g., feature levels are in allowed range, no duplicate IDs).

### Step 8: Commit (1 min)

Commit the file with a message like `add: champion fighter subclass` or `add: light domain cleric subclass`. Commit one subclass per commit for clean history.

---

## 5. Feature Type Selection Guide

The `feature_type` field determines how the engine processes a feature. Choose the most specific type that fits; use `scripted_feature` only when no specific type applies.

The full vocabulary is defined in `subclass_schema_v0.1.md`. Below is a decision guide.

### Decision flowchart

```
Is the feature purely cosmetic or narrative?
  → skip it (do not author)

Does the feature activate in response to something?
  → reaction or triggered_ability

Does the feature require a conscious action (action, bonus action, reaction) to use?
  → custom_action

Does the feature modify the character's stats or combat math passively?
  → passive_feature_grant, damage_bonus, defense_bonus, or similar

Does the feature grant proficiencies or expand existing ones?
  → proficiency_grant, expertise_grant, or skill_proficiency_grant

Does the feature grant access to spells?
  → spell_grant or always_prepared_spell_grant

Does the feature scale attack dice or damage dice?
  → damage_bonus with scaling, or attack_count_modifier

Does the feature change critical hit rules?
  → crit_range_modifier

Does the feature modify an existing class feature?
  → feature_modification (points to another feature and describes the change)

Does the feature fit nothing above?
  → scripted_feature (last resort, requires behavior AI to interpret)
```

### Commonly used feature types (most subclasses use only these)

- **`custom_action`**: Activated ability with a resource cost. Most Channel Divinity options, Smites, Flurry of Blows variants, etc.
- **`passive_feature_grant`**: Always-on bonus. Extra damage on certain conditions, sensory grants, movement bonuses.
- **`damage_bonus`**: Flat or dice bonus to damage rolls. Divine Strike, Evocation Savant.
- **`crit_range_modifier`**: Expands crit range (Champion's Improved Critical).
- **`spell_grant`**: Learn a spell known to a non-caster class or expand a caster's spell list.
- **`always_prepared_spell_grant`**: Specific spells are always prepared for the caster (Life Domain spells).
- **`reaction`**: Triggered ability that uses the reaction slot (Shield spell is such, Cutting Words for Bard).
- **`resource_pool_modification`**: Adds uses to an existing pool, or creates a new one.

### When to use `scripted_feature`

Reserve for genuinely novel mechanics. Examples:
- Moon Druid's Wild Shape modifications (changes HP calculation)
- Warlock's Eldritch Invocations system (meta-feature that grants other features)
- Stars Druid's Starry Form (multi-mode transformation with distinct effects)

`scripted_feature` requires the behavior AI to have custom handling. Every `scripted_feature` in the codebase is a maintenance cost. Minimize.

---

## 6. Behavior AI Hints Guide

The behavior AI uses `behavior_hints` to decide what a character does on its turn. Hints are not strict rules; the AI uses them to score options.

A well-written hints block answers these questions:

1. **What is the subclass's primary role?** (damage dealer, tank, controller, healer, support)
2. **What is its signature move?** (the feature the AI should almost always use when available)
3. **What resources should be spent eagerly vs. conserved?**
4. **What enemy types or situations does it excel against?**
5. **What should it avoid?**

### Hint structure

```yaml
behavior_hints:
  combat_role: "striker"                        # one of: defender, striker, controller, support, healer, blaster, skirmisher
  
  primary_signature:
    description: "Expanded critical hit range makes every attack a potential big hit"
    priority_actions: ["attack", "extra_attack"]
  
  resource_management:
    aggressive_use: []                          # pools or features to spend freely
    conservative_use: ["action_surge_uses"]     # pools or features to save for important moments
  
  target_preferences:
    - "high_hp_single_targets"                  # Champion scales on consistent damage
    - "enemies_with_low_ac"                     # landing hits matters more than smart targeting
  
  positioning:
    preference: "frontline_melee"
    avoid: "isolated_from_party"
  
  avoid_situations:
    - "concentration_reliance"                  # Champion has no concentration spells
    - "save_or_die_dependence"                  # low save DC (no spells)
  
  notes: "Straightforward melee combatant. Attack, attack, attack. Use Second Wind when below 50%. Action Surge on round 1 of boss fights or when enemies clump for cleave."
```

### Hint quality heuristics

- **Be specific.** "Aggressive" and "conservative" are not useful hints. "Spend Superiority Dice every round, but save Commander's Strike for when the Rogue needs a turn" is useful.
- **Think about the engine, not the player.** The AI is not a human. It does not understand narrative stakes. Express hints in terms of game-state conditions (HP thresholds, enemy counts, turn numbers).
- **Cover failure modes.** What happens if the subclass's preferred situation does not arise? A Colossus Slayer Ranger should still act usefully against a mob of minions; describe how.

---

## 7. Worked Example: Champion Fighter

This is a complete, commented example of a subclass YAML file for the Champion Fighter. It demonstrates every major section of the schema and the reasoning behind the choices.

### Why Champion as the worked example

Champion is:
- Simple enough to be fully readable (three level-gated features, one scaling)
- Canonical (every D&D player knows it)
- Exercises most schema features (passive feature, scaling, crit range modifier, damage bonus)
- Has clear behavior AI implications (straightforward striker)

More complex subclasses (Battle Master, Life Domain, Draconic Sorcerer) follow the same patterns but with more features.

### The complete Champion YAML

```yaml
# ==============================================================================
# SUBCLASS: Champion (Fighter)
# Source: 2024 Player's Handbook
# ==============================================================================

schema_version: "0.1"
content_type: "subclass"
id: "champion"
display_name: "Champion"
parent_class: "fighter"
source: "PHB_2024"
version: "2024"
author: "Wizards of the Coast"
flavor_text: >
  The archetypal Champion focuses on the development of raw physical power honed 
  to deadly perfection. Those who model themselves on this archetype combine 
  rigorous training with physical excellence to deal devastating blows.

# ==============================================================================
# FEATURES: Listed in unlock_level order
# ==============================================================================

features:
  # --------------------------------------------------------------------------
  # LEVEL 3: Improved Critical
  # PHB text: "Your attack rolls with weapons and Unarmed Strikes can score a
  # critical hit on a roll of 19 or 20 on the d20."
  # --------------------------------------------------------------------------
  - id: "improved_critical"
    unlock_level: 3
    display_name: "Improved Critical"
    feature_type: "crit_range_modifier"
    body:
      new_crit_threshold: 19      # natural 19 or 20 now crits
      applies_to: "weapon_and_unarmed_attacks"
    flavor: "Weapons seem to find the chinks in your enemies' defenses."
  
  # --------------------------------------------------------------------------
  # LEVEL 3: Remarkable Athlete
  # PHB text: "You can add half your Proficiency Bonus (round up) to any
  # Strength, Dexterity, or Constitution check you make that doesn't already
  # use your Proficiency Bonus. In addition, when you make a running long jump,
  # the distance you can cover increases by a number of feet equal to your
  # Strength modifier."
  # --------------------------------------------------------------------------
  - id: "remarkable_athlete"
    unlock_level: 3
    display_name: "Remarkable Athlete"
    feature_type: "passive_feature_grant"
    body:
      grants:
        - type: "half_proficiency_to_ability_checks"
          ability_scores: ["STR", "DEX", "CON"]
          round: "up"
          condition: "not_already_proficient"
        - type: "jump_distance_bonus"
          jump_type: "running_long_jump"
          bonus: "strength_modifier"
          unit: "feet"
  
  # --------------------------------------------------------------------------
  # LEVEL 7: Additional Fighting Style
  # PHB text: "You gain another Fighting Style feat of your choice."
  # --------------------------------------------------------------------------
  - id: "additional_fighting_style"
    unlock_level: 7
    display_name: "Additional Fighting Style"
    feature_type: "feat_grant"
    body:
      feat_category: "fighting_style"
      author_chooses: true
      note: "Default selection for standard party: Great Weapon Fighting (reroll 1s and 2s on two-handed weapon damage dice)"
  
  # --------------------------------------------------------------------------
  # LEVEL 10: Heroic Warrior
  # PHB text: "The thrill of battle drives you toward victory. At the start of
  # each of your turns in combat, you can give yourself Heroic Inspiration if
  # you don't already have it."
  # --------------------------------------------------------------------------
  - id: "heroic_warrior"
    unlock_level: 10
    display_name: "Heroic Warrior"
    feature_type: "passive_feature_grant"
    body:
      grants:
        - type: "conditional_heroic_inspiration"
          trigger: "start_of_your_turn_in_combat"
          condition: "do_not_currently_have_heroic_inspiration"
          effect: "gain_heroic_inspiration"
  
  # --------------------------------------------------------------------------
  # LEVEL 15: Superior Critical
  # PHB text: "Your attack rolls with weapons and Unarmed Strikes can now
  # score a critical hit on a roll of 18 or higher on the d20."
  # --------------------------------------------------------------------------
  - id: "superior_critical"
    unlock_level: 15
    display_name: "Superior Critical"
    feature_type: "crit_range_modifier"
    body:
      new_crit_threshold: 18      # natural 18, 19, or 20 now crits
      applies_to: "weapon_and_unarmed_attacks"
      supersedes: "improved_critical"
    flavor: "Your blows find the weakest gaps with uncanny precision."
  
  # --------------------------------------------------------------------------
  # LEVEL 18: Survivor
  # PHB text: "You attain the pinnacle of resilience in battle, giving you
  # these benefits:
  #   Defy Death. You have Advantage on Death Saving Throws. Moreover, when you
  #     roll 18-20 on a Death Saving Throw, you gain the benefit of rolling a 20
  #     on it.
  #   Heroic Rally. At the start of each of your turns, you regain Hit Points
  #     equal to 5 plus your Constitution modifier if you are Bloodied and have
  #     at least 1 Hit Point."
  # --------------------------------------------------------------------------
  - id: "survivor"
    unlock_level: 18
    display_name: "Survivor"
    feature_type: "passive_feature_grant"
    body:
      grants:
        - type: "death_save_advantage"
          effect: "advantage_on_death_saves"
        - type: "death_save_threshold_improvement"
          threshold: 18                   # rolls 18-20 count as natural 20
          effect: "equivalent_to_nat_20"
        - type: "turn_start_regeneration"
          trigger: "start_of_your_turn_in_combat"
          conditions:
            - "bloodied"
            - "hp_greater_than_0"
          amount: "5 + constitution_modifier"

# ==============================================================================
# RESOURCE POOLS: (none for Champion; uses class pools only)
# ==============================================================================

resource_pools: []

# ==============================================================================
# SPELL LIST: (none; Champion is non-caster)
# ==============================================================================

spell_list: []

# ==============================================================================
# BEHAVIOR AI HINTS
# ==============================================================================

behavior_hints:
  combat_role: "striker"
  
  primary_signature:
    description: >
      Relentless weapon attacker with expanded crit range. No concentration 
      dependence, no spell slots to manage, no complex resource economy. The 
      Champion's value is consistent, reliable damage output across long 
      adventuring days.
    priority_actions: ["attack", "extra_attack_if_unlocked", "action_surge_offensively"]
  
  resource_management:
    aggressive_use: 
      - resource: "second_wind_uses"
        when: "hp_below_50_percent"
      - resource: "action_surge_uses"
        when: "round_1_or_boss_engaged"
    conservative_use:
      - resource: "indomitable_uses"
        reason: "Save for critical failed saves against save-or-die effects"
  
  target_preferences:
    - "highest_hp_enemy"                    # consistent damage excels against bosses
    - "enemies_within_extra_attack_reach"   # maximize attack count
    - "prone_or_restrained_targets"         # advantage compounds crit range benefit
  
  positioning:
    preference: "engaged_melee_frontline"
    avoid: "isolated_without_ally_support"
    target_reposition: "gap_close_to_priority_target"
  
  weapon_mastery_recommendations:
    # These are advisory; subclass does not mandate weapon choice
    # but Champion synergies well with:
    preferred_masteries: ["graze", "cleave", "vex"]
    reasoning: >
      Graze provides damage on missed attacks (compounds reliability). 
      Cleave extends damage to multiple targets. Vex provides advantage 
      that pairs well with expanded crit range.
  
  synergies_with_class_features:
    - "second_wind_is_bonus_action_between_turns"
    - "action_surge_doubles_attack_count_for_one_action"
    - "multiple_attacks_compound_improved_critical_value"
  
  avoid_situations:
    - "concentration_saves_required_in_role"     # Champion has no concentration
    - "long_range_encounters"                    # Champion lacks ranged specialization
    - "save_or_die_against_mental_save"          # no mental save proficiency
  
  notes: >
    The Champion has the simplest tactical decision tree of any Fighter subclass.
    The AI should attack every turn, use bonus action for Second Wind when 
    bloodied, and Action Surge on round 1 of hard encounters. Heroic Warrior
    (L10) grants self-inspiration at turn start; use it on the attack roll most
    likely to hit a high-value target. Survivor (L18) makes dropping to 0 HP 
    rare; play aggressively at high levels.

# ==============================================================================
# CATEGORIZATION METADATA
# ==============================================================================

tags:
  - "martial"
  - "non_caster"
  - "melee_focused"
  - "simple_mechanics"
  - "damage_dealer"

complexity_rating: "low"     # low, medium, high (for UI/onboarding)
```

### Annotations on Champion choices

**Why `crit_range_modifier` for Improved Critical:** The engine needs to know, when an attack is rolled, what threshold counts as a crit. A single field (`new_crit_threshold`) captures this cleanly. The `supersedes` field on Superior Critical prevents double-application when both features are active.

**Why `passive_feature_grant` for Remarkable Athlete, Heroic Warrior, Survivor:** These are "always on" effects that modify game state without requiring action. The `grants` list inside the body enumerates the specific modifications. Each grant has a `type` that maps to a specific engine handler.

**Why `feat_grant` for Additional Fighting Style:** The feature hands the author a choice. The YAML cannot know which fighting style will be selected, so it declares a choice point with `author_chooses: true`. The character build process asks the user (or defaults per standard party rules) which fighting style to apply.

**Why the behavior hints are so specific:** The Champion is simple mechanically, but the AI still needs to know things like "don't save Second Wind, use it when bloodied" and "target the highest-HP enemy, not the easiest to kill." These hints are the difference between the AI playing competently and playing like a random actor.

**What's NOT in the YAML:** 
- No HP totals (those come from class hit die + CON mod + level, computed by engine)
- No AC values (armor choice is separate)
- No equipment (equipment is its own content type)
- No feat choices beyond Additional Fighting Style (those come from character build)

---

## 8. Validation Checklist

Before committing a subclass YAML, verify:

### Structural validation

- [ ] `schema_version` present and valid
- [ ] `content_type` is `"subclass"`
- [ ] `id` is lowercase snake_case and unique in the repository
- [ ] `parent_class` references an existing class YAML
- [ ] `source` and `version` fields present
- [ ] All features have `id`, `unlock_level`, `display_name`, `feature_type`, `body`

### Semantic validation

- [ ] Feature unlock levels are in the valid range for the parent class's subclass progression
- [ ] Each `feature_type` used exists in the schema vocabulary
- [ ] Resource pool references (if any) point to declared pools
- [ ] Spell references (if any) point to existing spell content
- [ ] Behavior hints are non-empty and use valid vocabulary

### Content validation

- [ ] Every PHB-declared feature is present
- [ ] No features are invented that the PHB does not describe
- [ ] Mechanical bodies match PHB text (verify at least twice; this is the most common error)
- [ ] Feature levels match the 2024 PHB (not 2014 rules)
- [ ] Scaling is captured (features that improve at later levels)

### Behavior hint validation

- [ ] `combat_role` is declared and matches subclass intent
- [ ] Primary signature is described
- [ ] Resource management is addressed
- [ ] At least one target preference and one avoid situation are listed
- [ ] Notes section provides practical tactical guidance

### Style validation

- [ ] Comments explain WHY when the mechanical body is non-obvious
- [ ] PHB text quoted in comments for every feature (aids review)
- [ ] Feature IDs are descriptive (`improved_critical` not `feature_1`)
- [ ] File is formatted consistently (2-space indent, sections divided by headers)

---

## 9. Prioritization Order

Not all subclasses are equally important. Author them in this priority order.

### Tier A: Author first (PHB 2024 common subclasses, ~16 subclasses)

These are the subclasses most players use and most baseline tests reference. They exercise the widest variety of schema patterns and reveal the most bugs.

- Fighter: **Champion**, Eldritch Knight
- Cleric: Light Domain, War Domain, Trickery Domain
- Wizard: Abjurer, Diviner, Illusionist
- Rogue: Assassin, Arcane Trickster, Soulknife
- Barbarian: Berserker, World Tree, Zealot
- Bard: Lore

### Tier B: Author second (PHB 2024 remaining, ~24 subclasses)

The remaining PHB classes. By this point the authoring process is established and these go quickly.

- Druid: Land, Moon, Sea
- Monk: Mercy, Shadow, Elements
- Paladin: Ancients, Glory, Vengeance
- Ranger: Beast Master, Fey Wanderer, Gloom Stalker
- Sorcerer: Aberrant, Clockwork, Wild Magic
- Warlock: Archfey, Celestial, Great Old One
- Bard: Dance, Glamour

### Tier C: Author third (non-PHB 2024 releases)

Subclasses from Heroes of Faerûn and Forge of the Artificer. Plus the supplementary templates already authored (Alchemist, Wild Heart, etc.) get proper YAML versions here.

- Heroes of Faerûn subclasses (~8)
- Forge of the Artificer: Cartographer, and any new 2025 subclasses
- The 9 supplementary templates we authored in Phase 1 become full YAML content here

### Tier D: Future releases

As WotC releases new source books, authoring happens as content is published. Each new subclass follows the same process.

### Rationale for this ordering

**Tier A covers every distinct schema pattern.** Authoring Champion (simple martial), Eldritch Knight (half-caster fighter), Light Domain (caster with spell list additions), Evoker (already done but re-author in proper YAML format), Assassin (triggered abilities), and Berserker (conditional resource cost) exercises nearly every feature type in the vocabulary. Bugs and schema gaps surface early.

**Tier B refines the process.** By the time you reach Tier B, authoring is fast. Quality stays high because the pattern is established.

**Tier C is mop-up.** Non-PHB subclasses follow the same patterns; nothing novel.

---

## 10. Claude Code Prompt Template

Use this prompt template when working with Claude Code to author subclass YAML files. Customize the bracketed sections per subclass.

```
Task: Author a subclass YAML file for [SUBCLASS NAME] ([CLASS NAME]) from the 
[SOURCE BOOK NAME].

Requirements:
1. Follow the subclass schema defined in `content/schemas/subclass_schema_v0.1.md`
2. Use the Champion Fighter example (`content/subclasses/fighter/champion.yaml`) 
   as a format reference
3. Refer to the Subclass Authoring Guide (`docs/subclass_authoring_guide.md`) for 
   feature type selection and behavior AI hint patterns
4. Place the output at `content/subclasses/[class_id]/[subclass_id].yaml`

Input: The PHB/source book text for this subclass follows below. Use only this 
text for mechanical claims. Do not add mechanics from other sources. Do not 
infer mechanics the text does not describe.

[PASTE PHB/SOURCE BOOK TEXT FOR SUBCLASS HERE]

Deliverables:
1. The YAML file at the specified path
2. Inline comments quoting the PHB text for each feature
3. A populated behavior_hints section with at least: combat_role, primary_signature, 
   resource_management, target_preferences, positioning, avoid_situations, notes
4. Tags and complexity_rating

Validation: After authoring, run the schema validator and report any errors. Do 
not commit until validation passes. If the PHB text is ambiguous on a specific 
mechanic, flag the ambiguity in a comment rather than guessing.
```

### Prompt variations

**For subclasses with spell lists:**
Add: "Include the `spell_list` section with always-prepared spells grouped by unlock level. Verify every spell exists in `content/spells/` before referencing; if a spell is missing, flag it rather than assuming."

**For subclasses with resource pools:**
Add: "Declare the subclass's resource pool(s) in the `resource_pools` section. Include max_size at each scaling level, refresh condition, and any partial refresh rules."

**For subclasses with modifications to class features:**
Add: "Use `feature_modification` type when the subclass changes a class feature rather than adding a new one. Reference the class feature by ID (e.g., `modifies_feature: flurry_of_blows`)."

---

## 11. Common Pitfalls

### Pitfall 1: Paraphrasing mechanics

The PHB says "you deal an additional 1d8 radiant damage once per turn when you hit with a weapon attack." An author writes `damage_bonus: +1d8 radiant on hit`. This loses the "once per turn" restriction and the "weapon attack" qualifier. The engine then applies the bonus to every hit, including spell attacks.

**Fix:** Quote the full text in comments. Translate every qualifier into a field.

### Pitfall 2: Wrong feature levels from 2014 rules

Many online resources still reference 2014 subclass feature levels. The 2024 PHB changed most subclass progressions. Do not trust memory or secondary sources; open the PHB.

**Fix:** The checklist requires verification against the actual PHB. Do not skip this.

### Pitfall 3: `scripted_feature` abuse

Every `scripted_feature` requires custom engine handling. Using it for features that could be expressed with standard types creates technical debt.

**Fix:** Before using `scripted_feature`, check the feature type vocabulary. If nothing fits, ask whether a new feature type should be added to the schema rather than scripting.

### Pitfall 4: Behavior hints that are too vague

"Play aggressively" does not help the AI. "Spend Superiority Dice every round except when holding Riposte for a specific enemy with multiattack" does.

**Fix:** Behavior hints should be executable rules, not style preferences. Test-read each hint: "Could the AI follow this rule without further interpretation?"

### Pitfall 5: Missing scaling

A feature that improves at level 10 and again at level 15 must declare both. Authors often capture the base version and forget the scaling.

**Fix:** Check the PHB text for phrases like "starting at level 10" or "when you reach level 15." Every such phrase is a scaling declaration.

### Pitfall 6: Inconsistent IDs

An author writes `life_domain` as the subclass ID, then `life-domain` in a reference, then `lifeDomain` in another file. The validator catches the cross-file reference failures, but confusion wastes time.

**Fix:** All IDs are lowercase snake_case. No exceptions.

### Pitfall 7: Flavor in mechanical fields

Someone writes `damage: "a crushing blow that staggers the enemy"` instead of `damage: "1d8"`. This breaks the engine.

**Fix:** Mechanical fields are machine-readable. Flavor goes in the `flavor` field (string) or as a comment.

---

## 12. Style Conventions

### Naming

- Subclass IDs: lowercase, snake_case, descriptive. Examples: `champion`, `life_domain`, `oath_of_devotion`, `path_of_the_berserker`.
- Feature IDs: lowercase, snake_case, specific. Avoid generic names. `improved_critical` not `feature_1`. If a feature name collides across subclasses, prefix with the subclass (`champion_improved_critical`).
- Display names: Title Case matching the PHB exactly.

### Formatting

- 2-space indentation
- YAML comments using `#` with a space after
- Blank lines between feature blocks
- Major sections separated by `# ====` header lines (as shown in the example)

### Comments

- Quote the PHB text in full for each feature in a comment block above the feature. This makes review dramatically easier.
- Explain non-obvious choices with a comment after the relevant line or field.
- Link to the architecture spec or schema docs for feature types that need context.

### Organization within the file

Standard section order:
1. Metadata header
2. Features (ordered by unlock_level ascending)
3. Resource pools
4. Spell list
5. Behavior hints
6. Tags and categorization

### Character count and readability

Aim for each subclass YAML to be 150-400 lines. Significantly shorter suggests missing features or insufficient behavior hints. Significantly longer suggests verbosity; tighten comments.

---

## Revision History

- **v0.1 (current):** Initial authoring guide with Champion Fighter worked example. Covers authoring process, feature type selection, behavior AI hints, validation, prioritization, and Claude Code prompt templates.

---

## Next Steps

Upon Phase 2 implementation start:

1. Ensure `subclass_schema_v0.1.md` and `class_schema_v0.1.md` are finalized as the authoritative schemas (any changes require this guide to be updated)
2. Implement the schema validator in Python
3. Author the base Fighter class YAML (prerequisite for any Fighter subclass)
4. Author Champion Fighter as the first subclass (validates the guide and the example)
5. Proceed down Tier A, then Tier B, then Tier C per the Prioritization Order section

Estimated total authoring effort for all 61 subclasses: 25-40 hours of focused work spread across Phase 2. Most of this work is parallelizable with engine implementation; subclass authoring does not block engine development, and vice versa, until baseline generation begins.
