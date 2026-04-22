# Feats and Epic Boons Content Schema — Proposal v0.1

## Purpose

Feats are discrete character options gained at specific levels (origin feats at level 1 via background/species, general feats at ASI levels, Epic Boons at level 19). In 2024 rules, most feats grant an ability score increase of +1 alongside their unique benefit.

This schema covers all feat categories in a unified structure and enables homebrew feat testing (including Epic Boon testing per Liege's direction, which uses only levels 19-20).

---

## Design Principles

Same as prior schemas, plus one specific to feats:

**Feats are small, atomic content.** Unlike subclasses or monsters, a feat is typically 1-4 mechanical benefits packaged together. The schema is correspondingly simpler.

---

## Feat Categories

The 2024 PHB defines four feat categories:

**Origin Feats:** Granted by species (Human) or background. Can also be taken as a general feat if a specific feat requires it. Weaker than general feats in raw power.

**General Feats:** Gained at ASI levels (4, 8, 12, 16). Typically grant +1 ability score alongside 2-3 mechanical benefits.

**Fighting Style Feats:** Special category; granted when a class feature grants a fighting style. Normally not taken as a general feat unless allowed.

**Epic Boons:** Granted at level 19. Powerful unique benefits often with +1 to a score (exceeding 20 cap allowed for Epic Boons).

Schemas for all four categories share the same structure; only the category tag differs.

---

## Top-Level Feat Structure

```yaml
schema_version: "0.1"
content_type: "feat"
id: "alert"
display_name: "Alert"
source: "PHB_2024"
version: "2024"
author: "Wizards of the Coast"
flavor_text: "Always on the lookout..."

# Category
feat_category: "origin"                # origin, general, fighting_style, epic_boon

# Prerequisites (if any)
prerequisites:
  min_level: 1                         # 1, 4, 8, 12, 16, 19 (Epic Boon)
  ability_score_minimums: {}           # e.g., {STR: 13} for some feats
  class_restrictions: []               # e.g., ["fighter"] for fighter-only feats
  other_prerequisites: []              # e.g., "ability to cast at least one spell"

# Ability score increase (most 2024 feats include this)
ability_score_increase:
  choose_count: 1                      # usually 1 for general feats, sometimes 0 for origin
  increase_amount: 1                   # typically 1
  eligible_abilities: ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
  max_score: 20                        # 30 for Epic Boons
  apply_to: "any"                      # any, one_of_listed, primary_ability_of_class, etc.

# Benefits granted (using standard feature_type vocabulary)
benefits: [ ... ]

# Repeatability (most feats: once only; some: multiple times with different choices)
repeatable: false
repeatable_condition: null             # e.g., "can take multiple times with a different weapon each time"

# Intent tags for test routing
intent_tags: ["combat", "initiative", "awareness"]
```

---

## Benefits Structure

Benefits use the same feature_type vocabulary as subclasses and other content.

### Example: Alert (Origin Feat)

```yaml
benefits:
  - id: "alert_initiative_bonus"
    feature_type: "passive_roll_modifier"
    body:
      roll_type: "initiative"
      amount: "proficiency_bonus"
  
  - id: "alert_surprise_immunity"
    feature_type: "condition_resistance"
    body:
      effect: "immune_to_disadvantage_on_initiative_from_surprise"
```

### Example: Great Weapon Master (General Feat)

```yaml
benefits:
  - id: "gwm_cleave"
    feature_type: "triggered_on_kill"
    body:
      trigger: "reduce_creature_to_0_hp_with_melee_weapon_attack"
      effect:
        type: "bonus_melee_attack"
        target: "different_creature_within_reach"
        restriction: "once_per_turn"
  
  - id: "gwm_heavy_strike"
    feature_type: "custom_action"
    body:
      action_type: "when_making_attack_with_heavy_weapon"
      cost: null
      effect:
        type: "damage_bonus_with_penalty"
        damage_bonus: "proficiency_bonus"
        trade_off: "no_penalty_in_2024"   # 2024 removed the -5/+10 trade-off
```

### Example: Magic Initiate (Wizard) (Origin Feat)

```yaml
benefits:
  - id: "magic_initiate_cantrips"
    feature_type: "spell_grant"
    body:
      spell_list_source: "wizard"
      cantrip_count: 2
      spell_level_1_count: 1
      spell_uses_per: "long_rest"
      spell_uses_count: 1
  
  - id: "magic_initiate_spellcasting_ability"
    feature_type: "passive_feature_grant"
    body:
      grant: "use_int_for_spells_from_this_feat"
```

### Example: War Caster (General Feat)

```yaml
benefits:
  - id: "war_caster_concentration"
    feature_type: "passive_roll_modifier"
    body:
      roll_type: "concentration_save"
      modifier: "advantage"
  
  - id: "war_caster_spell_opportunity"
    feature_type: "reaction"
    body:
      trigger: "creature_provokes_opportunity_attack_from_you"
      effect:
        type: "cast_spell_as_reaction"
        spell_restriction: "single_target_spell_with_casting_time_one_action"
  
  - id: "war_caster_somatic_with_hands_full"
    feature_type: "passive_feature_grant"
    body:
      grant: "can_perform_somatic_components_with_weapon_or_shield_hands"
```

### Example: Tough (Origin Feat)

```yaml
benefits:
  - id: "tough_hp"
    feature_type: "passive_stat_modifier"
    body:
      stat: "max_hp"
      amount: "2 * character_level"
      updates_on_level_up: true
```

### Example: Resilient (General Feat, variable)

```yaml
# Resilient actually has variable choice - player picks ability
id: "resilient"
display_name: "Resilient"
feat_category: "general"

ability_score_increase:
  choose_count: 1
  increase_amount: 1
  eligible_abilities: ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
  ability_becomes_save_proficient: true  # the ability chosen is also granted save proficiency

benefits:
  - id: "resilient_save_prof"
    feature_type: "save_proficiency"
    body:
      save: "player_chosen_ability"
```

---

## Epic Boon Structure

Epic Boons use the same schema but with the "epic_boon" category and usually higher-impact benefits.

### Example: Boon of Combat Prowess

```yaml
id: "boon_of_combat_prowess"
display_name: "Boon of Combat Prowess"
feat_category: "epic_boon"

prerequisites:
  min_level: 19

ability_score_increase:
  choose_count: 1
  increase_amount: 1
  eligible_abilities: ["STR", "DEX", "CON"]
  max_score: 30                        # Epic Boons can push past 20

benefits:
  - id: "combat_prowess_hit"
    feature_type: "triggered_on_miss"
    body:
      trigger: "miss_attack_roll"
      restriction: "once_per_turn"
      effect:
        type: "convert_miss_to_hit"
```

### Example: Boon of Spell Recall

```yaml
id: "boon_of_spell_recall"
display_name: "Boon of Spell Recall"
feat_category: "epic_boon"

prerequisites:
  min_level: 19
  other_prerequisites: ["spellcasting_class_feature"]

ability_score_increase:
  choose_count: 1
  increase_amount: 1
  eligible_abilities: ["INT", "WIS", "CHA"]
  max_score: 30

benefits:
  - id: "spell_recall"
    feature_type: "triggered_on_spell_cast"
    body:
      trigger: "cast_spell_of_level_1_to_4"
      uses_per: "long_rest_with_recharge_on_short_rest_or_smaller"
      uses_count: 1
      effect:
        type: "do_not_expend_slot"
```

### Example: Boon of the Night Spirit

```yaml
id: "boon_of_the_night_spirit"
display_name: "Boon of the Night Spirit"
feat_category: "epic_boon"

prerequisites:
  min_level: 19

ability_score_increase:
  choose_count: 1
  increase_amount: 1
  eligible_abilities: ["DEX", "CON", "WIS"]
  max_score: 30

benefits:
  - id: "night_spirit_resistance"
    feature_type: "damage_resistance"
    body:
      condition: "fully_in_dim_light_or_darkness"
      resistance_types: ["all_except_force_psychic_radiant"]
  
  - id: "night_spirit_hide"
    feature_type: "passive_feature_grant"
    body:
      grant: "take_hide_action_as_bonus_action"
```

---

## Feat Scoring

Feat value scoring is similar to species trait scoring but calibrated for the feat category.

**Origin feat expected value:** 3-5 points (backgrounds grant these freely)

**General feat expected value:** 6-10 points (cost is an ASI, which itself is ~4-5 points of stat gain)

**Epic Boon expected value:** 10-15 points (level 19 is a special slot; Epic Boons are meant to be powerful)

### Scoring Individual Benefits

Using similar categories to species scoring:

- Passive combat bonus (advantage on rolls, damage bonus): varies by magnitude
- Reaction-based ability: 3-6 points
- Bonus action ability: 3-5 points
- Resource grants (extra HP, extra spell uses): varies by magnitude
- Action economy manipulation: 5-10 points (this is where feats can be very strong)
- Spell grants (Magic Initiate): 4-6 points depending on spell level access

Total expected score depends on category:
- Origin: 3-5 points (plus the ASI embedded)
- General: 6-10 points (plus the ASI embedded)
- Epic Boon: 10-15 points (plus Epic ASI that breaks normal caps)

---

## Testing Methodology

**Origin feat testing:** Part of background testing primarily. The feat is the most impactful part of the background.

**General feat testing:** Equip the feat on a standard party member whose role benefits most from it (martial feats on fighter, caster feats on wizard, universal feats on cleric or rogue). Run the full test battery. Measure delta from party baseline without the feat.

**Epic Boon testing:** Per Liege's direction, only tested at levels 19-20. Equip the boon on a standard party member, run encounter battery at levels 19-20 only, measure delta.

**Fighting Style Feats:** Tested only if granted through a class feature (not normally a standalone test). Test by comparing two identical characters differing only in fighting style choice.

---

## Validation Rules Specific to Feats

1. **Feat category must be valid.**
2. **Prerequisites must be coherent** (epic boons require min_level 19, general feats typically require 4+).
3. **ASI must match category norms** (most general feats +1, Epic Boons often +1 with max_30, some feats +0).
4. **Benefits must use valid feature types.**
5. **Repeatability must be declared.**
6. **If benefits reference specific skills, weapons, or spells, they must exist in respective registries.**

---

## Homebrew Feat Additional Checks

1. **Origin feat power budget:** Flag if benefits exceed 5-point budget.
2. **General feat power budget:** Flag if benefits exceed 10-point budget.
3. **Epic Boon power budget:** Flag if exceeds 15 points or falls below 8.
4. **Multiple ASIs:** Feats granting more than +1 ability score are flagged (Epic Boons may have +2 in specific cases).
5. **Action economy overreach:** Feats granting extra actions without cost are flagged.
6. **Stacking issues:** Feats granting benefits that stack with identical class features (e.g., another Extra Attack) are flagged.

---

## Specific Concerns for Homebrew Epic Boons

Epic Boons are the most impactful homebrew content because:
- They break normal ability score caps
- They often grant paradigm-shifting benefits (e.g., truesight, at-will teleportation)
- Tier 4 play is less-tested than lower tiers, so balance norms are hazier

Homebrew Epic Boon tests should:
1. Compare against all WotC Epic Boons for scope reasonableness
2. Check if benefits are achievable at levels below 19 via other means (if so, the boon is underpowered for its tier)
3. Verify at-will abilities are priced appropriately
4. Check for synergy with existing class features that might overpower

---

## Open Questions for Liege Review

1. **Do we handle fighting style feats as a separate schema or as a subset of this one?** My recommendation: same schema, different category tag. Less redundancy.

2. **For feats with player choices (Resilient's ability, Magic Initiate's spell list), how are choices captured?** Option A: the character sheet captures the choice; the feat is generic. Option B: the feat has placeholders for choices. My recommendation: Option A. The feat schema describes options; the character sheet locks the choice.

3. **Multi-instance feats:** Some feats are taken multiple times with different choices (e.g., Weapon Master with different weapon masteries). How do we model this? My recommendation: feat has `repeatable: true` flag; character sheet tracks each instance separately with its own choice.

4. **Prerequisite checking during simulation:** Feats with prerequisites (e.g., spellcasting requirement for War Caster) must only apply to characters meeting them. My recommendation: engine validates on character build; ignores during sim (character is already built correctly).

5. **Epic Boon unique status:** Epic Boons are the only content where ability scores can exceed 20 legally. The engine must allow scores up to 30 when Epic Boons are involved. Flagging for engine implementation.

6. **Feat combinations:** Some feats combine unexpectedly (e.g., Polearm Master + Sentinel creating reach-based lockdown). The engine detects these combinations through simulation, not through the schema. OK?
