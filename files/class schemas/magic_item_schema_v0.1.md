# Magic Item Content Schema — Proposal v0.1

## Purpose

Magic items provide mechanical bonuses, grant abilities, or cast spells. The schema handles weapons, armor, shields, wondrous items, wands, staves, rods, rings, and potions/scrolls/consumables. Per Liege's direction, magic items are tested through type-appropriate batteries rather than one universal test.

---

## Design Principles

Same as prior schemas, plus one specific to magic items:

**Items are attached to characters and modify their capabilities.** Unlike subclasses (always on), items are acquired, attuned, equipped, and sometimes consumed. The schema captures this lifecycle explicitly.

---

## Top-Level Magic Item Structure

```yaml
schema_version: "0.1"
content_type: "magic_item"
id: "flame_tongue_longsword"
display_name: "Flame Tongue (Longsword)"
source: "PHB_2024"                       # or DMG_2024, or source-specific
version: "2024"
author: "Wizards of the Coast"
flavor_text: "A red-orange flame erupts..."

# Item category
item_type: "weapon"                      # weapon, armor, shield, wondrous, wand, staff, rod, ring, potion, scroll, ammunition
subtype: "longsword"                     # for weapons/armor; more specific type
rarity: "rare"                           # common, uncommon, rare, very_rare, legendary, artifact

# Attunement requirement
requires_attunement: true
attunement_restriction: null             # e.g., "by a good-aligned creature", "by a spellcaster"

# Physical properties (for weapons/armor)
base_item_stats:                         # only for weapons/armor; defines base mundane item
  damage: "1d8 slashing"                 # weapons only
  properties: ["versatile (1d10)"]       # weapons only
  weight: 3
  ac_bonus: 0                            # armor only; this is the base armor AC
  stealth_disadvantage: false            # armor only

# Bonuses and modifiers (passive while equipped/attuned)
passive_modifiers: [ ... ]

# Active abilities (require action to use)
active_abilities: [ ... ]

# Charges (for charge-based items like wands)
charges:
  max: 4
  recharge: "1d4_plus_1_at_dawn"         # or null for uncharged items
  destroy_on_empty: false                # relevant for some wands

# Type-specific testing category (drives test routing)
testing_category: "combat_weapon"        # combat_weapon, combat_armor, combat_defensive, spellcasting, utility, healing, consumable, etc.

# Primary intent tags
intent_tags: ["combat", "damage", "bonus_damage"]
```

---

## Item Types and Their Special Fields

### Weapons

```yaml
item_type: "weapon"
subtype: "longsword"
base_item_stats:
  damage: "1d8 slashing"
  properties: ["versatile (1d10)"]

passive_modifiers:
  - type: "attack_roll_bonus"
    amount: 1
  - type: "damage_roll_bonus"
    amount: 1
  - type: "bonus_damage"
    damage: "2d6"
    damage_type: "fire"
    trigger: "on_hit"
    
active_abilities:
  - id: "flame_ignite"
    display_name: "Ignite Flame"
    activation: "bonus_action"
    effect: "ignite_blade"          # this is a toggle; while lit, fire damage applies
```

### Armor

```yaml
item_type: "armor"
subtype: "plate_armor"
base_item_stats:
  ac_base: 18
  stealth_disadvantage: true
  strength_requirement: 15

passive_modifiers:
  - type: "ac_bonus"
    amount: 1
  - type: "save_proficiency_grant"
    save: "CHA"                     # example: armor that grants CHA save
```

### Wondrous Items

```yaml
item_type: "wondrous"
subtype: "cloak"                     # cloak, belt, helm, ring, bracers, boots, etc.

passive_modifiers:
  - type: "ac_bonus"
    amount: 1
  - type: "save_bonus"
    amount: 1
    saves: "all"
```

### Wands and Staves (charge-based)

```yaml
item_type: "wand"
display_name: "Wand of Fireballs"
requires_attunement: true

charges:
  max: 7
  recharge: "1d6_plus_1_at_dawn"
  destroy_on_empty: true
  destroy_chance: "roll_1_on_d20_when_last_charge_used"

active_abilities:
  - id: "cast_fireball"
    display_name: "Cast Fireball"
    activation: "action"
    charges_cost: 1                  # can be spent as multiple charges for upcast
    effect: "cast_spell"
    spell_id: "fireball"
    spell_level_default: 3
    upcast_available:
      - cost_charges: 2
        spell_level: 4
      - cost_charges: 3
        spell_level: 5
      # etc.
```

### Potions (consumable)

```yaml
item_type: "potion"
subtype: "healing"
requires_attunement: false
consumable: true

active_abilities:
  - id: "drink_potion"
    display_name: "Drink Potion of Healing"
    activation: "action"              # or bonus action depending on variant
    effect: "healing"
    amount: "2d4 + 2"
```

### Scrolls (consumable)

```yaml
item_type: "scroll"
subtype: "spell_scroll_3rd"
consumable: true

active_abilities:
  - id: "cast_scroll_spell"
    display_name: "Cast Spell from Scroll"
    activation: "action"
    effect: "cast_spell_from_scroll"
    spell_id_placeholder: "any_3rd_level_spell_or_lower"   # which spell the scroll contains
    save_dc: 15                      # standard for 3rd-level scroll
    attack_bonus: 7                  # standard for 3rd-level scroll
```

---

## Testing Category Routing

Per Liege's direction, magic items route to type-appropriate test batteries:

**combat_weapon:** +X weapons, special weapons (Flame Tongue, Vorpal Sword, Sun Blade). Tested by equipping on appropriate character (martial) and running combat battery.

**combat_armor:** +X armor, armor with unique protections (Armor of Invulnerability, Dragon Scale Mail). Tested by equipping on tank character and measuring survivability delta.

**combat_defensive:** Shields, protective wondrous items (Cloak of Displacement, Ring of Protection). Tested by equipping and measuring HP-remaining delta across combat battery.

**spellcasting:** Wands, staves, rods, caster-enhancing items (Robe of the Archmagi, Staff of Power). Tested by equipping on caster and running combat battery with spell-using behavior AI.

**utility:** Movement items (Boots of Flying, Cloak of the Bat), information items (Gem of Seeing, Helm of Telepathy), problem-solving items (Bag of Holding, Immovable Rod). Tested through exploration/investigation batteries.

**healing:** Potions of healing, Staff of Healing, Amulet of Health. Tested through combat battery with focus on party survivability.

**consumable:** Potions, scrolls, single-use items. Tested with specific use-case evaluation: does the consumable's one-time effect justify its tier rarity?

**social:** Hat of Disguise, Robe of Eyes, items enhancing Charisma checks. Tested through social battery.

**movement:** Boots of Flying, Winged Boots, Broom of Flying. Tested through exploration battery and tactical combat scenarios.

**legendary_meta:** Artifacts and unique items with world-changing abilities. May not fit any other category; individually evaluated.

---

## Passive vs Active Modifiers

**Passive modifiers** apply continuously while the item is equipped and (if required) attuned. They are part of the character's baseline stats during simulation. Examples: +1 to attack and damage, +2 AC, advantage on Perception checks.

**Active abilities** require a deliberate action to use. They consume an action, bonus action, or reaction, and may consume charges or have daily/hourly limits.

A single item can have both. The Staff of Power has passive modifiers (+2 to attack/damage/AC, +2 to spell save DC) AND active abilities (cast Cone of Cold, Fireball, Wall of Force from charges).

---

## Item Rarity and Balance Expectations

2024 rarity tiers and typical effects:

**Common:** Minor magical effects, no meaningful combat impact. Worth ~100 gp. (Candle of the Deep, Clothes of Mending)

**Uncommon:** Small combat bonuses, niche utility. Worth ~500 gp. (+1 weapon, Bag of Holding, Boots of Elvenkind)

**Rare:** Significant combat bonuses, powerful niche items. Worth ~5000 gp. (+2 weapon, Flame Tongue, Winged Boots)

**Very Rare:** Major combat bonuses, game-changing items. Worth ~50000 gp. (+3 weapon, Staff of Power, Cloak of Displacement)

**Legendary:** Paradigm-shifting items, campaign-defining artifacts. Worth hundreds of thousands of gp. (Holy Avenger, Staff of the Magi, Tome of Understanding)

**Artifact:** Campaign-defining, often with drawbacks. No standard pricing. (Wand of Orcus, Hand and Eye of Vecna)

Homebrew items should fit within the rarity tier they claim. An "uncommon" item with Staff-of-Power-tier effects is overtuned.

---

## Balance Scoring for Magic Items

Item scoring is more heuristic than species scoring because items vary more. Rough guidelines:

**Combat weapon scoring:**
- +1 to hit/damage: 3 points
- +2 to hit/damage: 6 points
- +3 to hit/damage: 9 points
- Bonus damage die (1d6): 3 points
- Bonus damage die (2d6): 5 points
- Special effect on crit (extra damage): 2 points
- Special effect on hit (save-or-effect): 4-8 points depending on effect

**Combat armor scoring:**
- +1 AC: 4 points
- +2 AC: 7 points
- +3 AC: 10 points
- Immunity to critical hits: 6 points
- Resistance to a damage type: 3 points

**Spellcasting item scoring:**
- +1 to spell attack/DC: 4 points
- +2 to spell attack/DC: 7 points
- Stored spells (per spell level equivalent): 2-5 points
- Spell storing (reusable): high value, flag

**Tier budgets (rough):**
- Common: 1-2 points
- Uncommon: 3-5 points
- Rare: 6-10 points
- Very Rare: 10-15 points
- Legendary: 15-25 points

Homebrew items should fall within their tier's budget range.

---

## Attunement Economics

Attunement is a hidden balance lever. Each character can attune to at most 3 magic items. Items that require attunement are competing for a scarce resource.

Homebrew items should generally require attunement if they grant significant passive bonuses or spell-like abilities. Homebrew items without attunement requirements are flagged for review.

---

## Validation Rules Specific to Magic Items

1. **Item type must be valid.**
2. **Rarity must be valid.**
3. **Attunement restriction (if present) must be sensibly worded.**
4. **Weapons must have base damage defined.**
5. **Armor must have AC base defined.**
6. **Charge-based items must specify recharge mechanic.**
7. **Consumables must be flagged appropriately.**
8. **Testing category must be valid.**
9. **Active abilities must specify activation type (action, bonus action, reaction, no action).**

---

## Homebrew Magic Item Additional Checks

1. **Rarity vs power budget:** Flag items exceeding their tier's expected point value.
2. **No-attunement red flag:** Flag items with passive bonuses that do not require attunement.
3. **Always-on action economy:** Flag items granting extra actions or bonus actions as passives.
4. **Uncharged items with repeatable effects:** Flag items that can be used repeatedly without charges or cooldowns.
5. **Stackable bonuses:** Flag items that explicitly stack with similar items (e.g., multiple AC bonuses).
6. **Curse absence for powerful items:** Legendary and artifact items in WotC often include drawbacks; homebrew without any is noted.

---

## Open Questions for Liege Review

1. **Do we model attunement in the simulator?** Characters have 3 attunement slots. Homebrew testing should assume the item under test takes one of those slots. My recommendation: yes, enforce 3-slot limit in sim.

2. **How do we handle items that grant spells?** Items with spell lists (Staff of Power, Staff of the Magi) add spells to the character's effective list. Do these count against the character's prepared/known spells? My recommendation: items grant additional spells; do not count against prepared limits.

3. **Charges and resource management:** Some items recharge per day (wands), some per short rest (Pearl of Power). The behavior AI needs to know when to burn charges aggressively vs conserve. My recommendation: AI treats charges as conservative-use resources by default; adjustable per item if author specifies.

4. **Homebrew potions:** Potions are consumable and often single-use. Testing a potion is mostly "does this one-shot effect justify its gp cost and rarity?" Less interesting simulation, more heuristic. OK with simplified evaluation?

5. **Ammunition:** +1 arrows, Javelins of Lightning, etc. These interact with ranged weapons but are not weapons themselves. Do we treat them as a subtype of item or separate? My recommendation: subtype of magic_item with item_type "ammunition".

6. **Artifact testing:** Artifacts are often unique and campaign-critical. Are we comfortable flagging artifacts as "outside normal testing" and handling them individually? My recommendation: yes.
