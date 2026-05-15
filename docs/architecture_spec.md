# D&D Homebrew Balance Framework — Architecture Specification v0.1

## Document Purpose

This document specifies the architecture of a simulation-based balance testing framework for D&D 5.5e homebrew content. It defines how the system is organized, how components interact, how tests are run, and how results are generated and reported.

It does NOT contain implementation code. Code comes in Phase 2.

It assumes familiarity with the content schemas (subclass, class, species, background, spell, magic item, monster, feat/epic boon) produced previously. Those schemas define the data; this document defines the behavior.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Core Principles](#2-core-principles)
3. [System Layers](#3-system-layers)
4. [Content Registry](#4-content-registry)
5. [Standard Party System](#5-standard-party-system)
6. [Combat Resolution Engine](#6-combat-resolution-engine)
7. [Non-Combat Resolution Engine](#7-non-combat-resolution-engine)
8. [Behavior AI Specification](#8-behavior-ai-specification)
9. [Test Harness Design](#9-test-harness-design)
10. [Participation and Impact Tracking](#10-participation-and-impact-tracking)
11. [Baseline Generation Pipeline](#11-baseline-generation-pipeline)
12. [Reporting System](#12-reporting-system)
13. [Logging System](#13-logging-system)
14. [Deployment Architecture](#14-deployment-architecture)
15. [Scoring Systems](#15-scoring-systems)
16. [Versioning and Compatibility](#16-versioning-and-compatibility)
17. [Testing the Test Framework](#17-testing-the-test-framework)
18. [Known Unknowns and Deferred Decisions](#18-known-unknowns-and-deferred-decisions)

---

## 1. System Overview

### 1.1 What the system does

The framework evaluates D&D 5.5e content for mechanical balance by:

1. Running each piece of content through a simulated test battery
2. Comparing results against a pre-computed baseline of WotC-published content
3. Generating reports showing how the tested content compares to the baseline distribution

The system supports seven content categories:
- Subclasses
- Monsters
- Magic items
- Backgrounds
- Species
- Spells
- Feats (including Epic Boons)

### 1.2 How the system is used

Two usage modes exist:

**Offline baseline generation (Phase 2):** The framework generates comprehensive baseline data by testing all official WotC content. This runs once per rules version and produces reference documents.

**Online homebrew testing (Phase 2+):** Users submit homebrew content; the framework tests it against the same protocols and compares against stored baselines. Returns a balance report.

### 1.3 Separation of concerns

The architecture separates:

- **Content representation** (the schemas) from **content behavior** (this spec)
- **Simulation engine** (deterministic mechanics) from **test harnesses** (what to measure)
- **Test execution** from **result interpretation**
- **Mechanical data** from **narrative flavor** (flavor ignored during simulation)

This separation allows each component to evolve independently. Rules updates touch content; mechanical changes touch the engine; new test categories add harnesses without modifying the engine.

---

## 2. Core Principles

### 2.1 Determinism with controlled randomness

Every simulation run is fully determined by its random seed. Given the same inputs and seed, results are reproducible. This matters for debugging, for statistical analysis, and for allowing users to audit surprising results.

### 2.2 Categorized honest reporting over filtered clean results

Per our earlier conversation: the system never silently filters out encounters where content "had no chance to contribute." Instead, every run is tagged with participation and impact categories, and results are reported broken down by category. Users see both conditional performance (how content does when it gets to act) and unconditional performance (how content does across all encounters).

### 2.3 Baseline-first, homebrew-second

The system generates WotC baseline data comprehensively before testing any homebrew. Homebrew reports always reference specific baseline versions. If baseline changes (due to engine updates or new WotC content), homebrew reports reference the old baseline version until retested.

### 2.4 Library first, product second

The simulation engine is designed as a standalone library with a clean interface. Deployment modes (CLI tool, web service, hybrid) are layers above the library and can be chosen without modifying the engine.

### 2.5 Rigor over speed where it matters

The framework prioritizes correctness over speed. Bugs in the simulation engine invalidate downstream results. Slow-but-correct is preferred to fast-but-wrong. Optimization happens after correctness is validated.

### 2.6 Schema compliance is enforced at boundaries

All content entering the system is validated against schemas before processing. Invalid content is rejected with clear error messages. The engine never operates on unvalidated data.

---

## 3. System Layers

The framework is organized into seven layers. Each layer has a well-defined interface with adjacent layers. Dependencies flow downward; upper layers depend on lower layers, never the reverse.

```
┌─────────────────────────────────────────┐
│  7. Reporting & Presentation Layer      │
│     (Generate reports, visualizations)  │
├─────────────────────────────────────────┤
│  6. Test Harness Layer                  │
│     (Subclass, monster, item, etc.)     │
├─────────────────────────────────────────┤
│  5. Test Runner Layer                   │
│     (Orchestrate multi-run simulations) │
├─────────────────────────────────────────┤
│  4. Behavior AI Layer                   │
│     (Tactical decisions)                │
├─────────────────────────────────────────┤
│  3. Simulation Engine Layer             │
│     (Combat + non-combat mechanics)     │
├─────────────────────────────────────────┤
│  2. Content Registry Layer              │
│     (Validated content, character build)│
├─────────────────────────────────────────┤
│  1. Content Schema Layer                │
│     (YAML validation, data loading)     │
└─────────────────────────────────────────┘
```

### 3.1 Layer 1: Content Schema Layer

Parses YAML content files, validates against schemas, produces in-memory content objects. Rejects invalid content with descriptive errors.

Inputs: YAML files (classes, subclasses, species, backgrounds, spells, magic items, monsters, feats).
Outputs: Validated Python/JSON objects representing the content.

### 3.2 Layer 2: Content Registry Layer

Stores validated content, resolves references between content (subclass → class → ability references, spells referenced in class spell lists, etc.). Handles character building (combining species, class, subclass, background, equipment, feats into a complete character sheet).

Inputs: Validated content objects, character build specifications.
Outputs: Fully-resolved character sheets, resolved monster stat blocks, ready-to-use content.

### 3.3 Layer 3: Simulation Engine Layer

Resolves combat and non-combat mechanics. Stateless: takes a scenario state and event, produces a new scenario state. Does not make tactical decisions (that is Layer 4).

Core responsibilities:
- Initiative tracking
- Turn and round management
- Action resolution (attacks, spells, saves)
- Condition tracking
- Damage and healing calculation
- Resource pool management
- Concentration tracking
- Rest mechanics
- Death saves and revival
- Non-combat skill check resolution

Inputs: Scenario state, event (action declaration, dice rolls).
Outputs: Updated scenario state, resolution details.

### 3.4 Layer 4: Behavior AI Layer

Makes tactical decisions for each combatant on its turn. Given the current scenario state and a character's available options, chooses what to do.

Multiple AI profiles exist (competent tactical, aggressive, conservative) but only one is active per simulation. Standard party uses "competent tactical."

Inputs: Scenario state, character options, AI profile.
Outputs: Action declaration for the character.

### 3.5 Layer 5: Test Runner Layer

Orchestrates multi-run simulations. Given a test specification (party, encounter, number of runs), runs the simulations using the engine and AI layers, collects results, handles randomness seeding.

Inputs: Test specification.
Outputs: Collection of run results with metadata.

### 3.6 Layer 6: Test Harness Layer

Defines what each test category measures and how. Seven harnesses exist: subclass, monster, magic item, background, species, spell, feat/epic boon. Each knows which party configurations to use, which metrics to collect, which baseline distribution to compare against.

Inputs: Content under test.
Outputs: Structured test results ready for reporting.

### 3.7 Layer 7: Reporting and Presentation Layer

Generates human-readable reports from test results. Handles comparison against baselines, computes statistics, identifies outliers, formats output (summary reports, detailed reports, raw data exports).

Inputs: Test results.
Outputs: Reports (Markdown, PDF, JSON, CSV, depending on use case).

---

## 4. Content Registry

### 4.1 Content organization

The registry stores content by type and ID:

```
registry/
├── classes/
│   ├── fighter.yaml
│   ├── wizard.yaml
│   └── ...
├── subclasses/
│   ├── battle_master.yaml
│   ├── evoker.yaml
│   └── ...
├── species/
├── backgrounds/
├── spells/
├── magic_items/
├── monsters/
├── feats/
└── epic_boons/
```

Each content file has a unique ID and references other content by ID.

### 4.2 Content versioning

Every content file has a `version` field (the rules edition, e.g., "2024") and a `source` field (the publication, e.g., "PHB_2024", "MM_2025", "homebrew:user_id:submission_id").

The registry can host multiple versions simultaneously for backward compatibility, but active tests use a single version.

### 4.3 Content resolution

When building a character, the registry resolves all references:

1. User specifies: class=fighter, subclass=battle_master, species=human, background=soldier, level=8
2. Registry loads fighter.yaml, battle_master.yaml, human.yaml, soldier.yaml
3. Registry applies progression through level 8: class features unlocked, subclass features unlocked, ASIs applied, feats selected per progression
4. Registry produces a resolved character object with all features, stats, spells prepared, equipment

The same resolution happens for monsters (simpler, since monsters don't progress).

### 4.4 Homebrew content handling

Homebrew content enters through the registry with a `homebrew:` source prefix. Validation is strict structurally (must match schema) but permissive semantically (may flag power budget warnings without rejecting).

Homebrew content is isolated per submission. Submitted content doesn't affect baseline data.

### 4.5 Content hot-loading and caching

For offline baseline generation, all content is loaded once at startup.

For online homebrew testing, content is loaded on-demand and cached. Submitted homebrew is loaded per test request and discarded after (unless user saves for retest).

**Open question:** Should submitted homebrew persist server-side for users? If yes, database design is required. If no, users must resubmit YAML each time they want to retest. **Recommendation:** persist for authenticated users, session-only for anonymous.

---

## 5. Standard Party System

### 5.1 Definition

The standard party consists of four pre-defined characters (Garrick Battle Master Fighter, Elowyn Life Cleric, Varian Evocation Wizard, Mira Thief Rogue). Their sheets are locked at the character sheet documents v0.2.

### 5.2 Level scaling

The party exists at all levels 1-20. At each level, every character has:
- Full ability scores (including ASIs and feat bonuses applied)
- Full feature list (class + subclass + feats)
- Full equipment (including level-appropriate magic items)
- Full prepared spell list (for casters; illustrative at schema level, fully enumerated at engine level)

The registry materializes the party at any requested level.

### 5.3 Party composition immutability

The party composition never changes. When testing a subclass, the test subclass is added as a FIFTH member. When testing a feat, the feat is applied to the most-appropriate existing party member (determined by feat prerequisites and target ability).

### 5.4 Fifth member templates

For tests requiring a class-specific fifth member (e.g., testing a druid-only spell), supplementary "standard" templates exist for every class not in the baseline party. These templates follow the same design principles: competent but not minmaxed, standard feat/item progression.

Supplementary templates include all 13 classes: Artificer, Barbarian, Bard, Cleric (with different subclass than Elowyn), Druid, Fighter (different from Garrick), Monk, Paladin, Ranger, Rogue (different from Mira), Sorcerer, Warlock, Wizard (different from Varian).

**Open question:** Do supplementary templates need full-detail progressions (like the standard party) for all 13 classes? **Recommendation:** yes, per earlier direction. This is substantial work, deferred to baseline generation phase.

---

## 6. Combat Resolution Engine

### 6.1 Scenario state

A scenario represents a combat encounter. State includes:

- All combatants (party members, enemies) with current HP, active conditions, remaining resources
- Battlefield position (grid-based, 5-foot squares)
- Round counter
- Turn order (initiative)
- Current turn
- Active effects (concentration spells, area effects, ongoing damage)
- Environmental features (cover, lighting, terrain)
- Event log (for this scenario)

### 6.2 Round structure

A round follows canonical 5e order:

1. **Start of round:** Legendary actions refresh (2025 format); some ongoing effects trigger
2. **Initiative order:** Each combatant takes their turn
3. **End of round:** Some ongoing effects tick (e.g., spirit guardians damage on turn start)

A turn follows canonical 5e structure:

1. **Start of turn:** Condition checks (end of hold person saves, regeneration, etc.)
2. **Action phase:** Character takes action (attack, spell, dash, dodge, help, hide, ready, search, other)
3. **Bonus action phase:** Character may take bonus action
4. **Movement phase:** May be split before/after action (movement tracked separately)
5. **Reaction window:** Character may react to triggered events
6. **End of turn:** Save-to-end effects rolled

Turn structure is not strictly sequential; movement can be split, reactions can trigger between other events. Engine handles interleaving.

### 6.3 Action resolution

Every action resolves through a common pipeline:

1. **Declaration:** Combatant (via Behavior AI) declares an action
2. **Validation:** Engine checks action is legal (range, resources, conditions)
3. **Targeting:** Engine identifies target(s)
4. **Attack roll (if applicable):** d20 + modifiers vs target AC
5. **Save request (if applicable):** Target rolls save vs DC
6. **Damage calculation:** Apply modifiers, resistance, vulnerability, immunity
7. **Application:** Update target state (HP, conditions, position)
8. **Triggered events:** Check for reactions, on-hit/on-miss features
9. **Log:** Record action and result

### 6.4 Attack roll resolution

```
Raw roll: 1d20
+ Ability modifier (STR or DEX typically)
+ Proficiency bonus (if proficient)
+ Item bonuses (+1/+2/+3 weapon)
+ Feature bonuses (Bless, Archery fighting style, etc.)
+ Situational modifiers (advantage/disadvantage rolled as 2d20 keep high/low)
- Penalties (cover, certain conditions)
= Total attack roll

Compare to target AC:
- ≥ AC: hit
- < AC: miss
- Natural 20: critical hit (all damage dice rolled twice)
- Natural 1: miss (plus may trigger fumble features)
```

### 6.5 Saving throw resolution

```
Raw roll: 1d20
+ Ability modifier
+ Proficiency bonus (if save proficient)
+ Item bonuses (Cloak of Protection, Ring of Protection)
+ Feature bonuses (Bless, Paladin aura, etc.)
± Situational modifiers
= Total save

Compare to DC:
- ≥ DC: success
- < DC: failure
```

Special: Legendary Resistance can convert fail to success (consumes LR use). Some effects have save-for-half vs save-for-none.

### 6.6 Damage and healing

**Damage application:**
```
Raw damage dice rolled
+ Ability modifier (if applicable)
+ Feature bonuses (Savage Attacker reroll, Sneak Attack dice)
± Item bonuses (weapon enhancement, etc.)

Apply modifiers:
- Resistance: damage halved (rounded down) for that damage type
- Vulnerability: damage doubled
- Immunity: damage = 0

Apply to target HP.

If target has Temporary HP: subtract from temp HP first, overflow to real HP.
```

**Healing:**
```
Raw healing dice rolled
+ Ability modifier (if applicable)
+ Feature bonuses (Disciple of Life bonus)

Apply to target:
- If target at 0 HP: restore to specified amount (stabilize)
- Otherwise: add HP but cannot exceed max HP
```

### 6.7 Conditions

The engine tracks all 5e conditions: Blinded, Charmed, Deafened, Exhaustion (levels 1-6 in 2024, scaling penalties), Frightened, Grappled, Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, Unconscious, Bloodied (new 2024: at or below half HP).

Each condition has specific mechanical effects automatically applied while active.

### 6.8 Concentration

Concentration is tracked per caster. Rules:
- Caster can maintain at most one concentration spell
- Casting a new concentration spell ends the old one
- Taking damage forces a concentration save (DC = max of 10 or half damage taken)
- War Caster grants advantage on concentration saves
- Resilient (CON) adds CON save proficiency
- Certain conditions (Incapacitated, Unconscious) end concentration
- Death ends concentration

### 6.9 Resources

Each combatant has a set of resource pools tracked during the encounter:

- Spell slots (per level)
- Class-specific pools (Superiority Dice, Channel Divinity, Second Wind, Action Surge, Indomitable)
- Subclass-specific pools (if any)
- Item charges (wands, staves, potions not yet consumed)
- Feat-based uses (Lucky points, Alert's situational benefits, etc.)
- Legendary Actions (for monsters)
- Legendary Resistance (for monsters)

Rest mechanics:
- **Short rest:** Recover some pools (Superiority Dice, Channel Divinity partial, Second Wind partial, Arcane Recovery for wizards once per day)
- **Long rest:** Recover all pools, regain HP, spell slots, etc.

The engine supports encounter chains with rests between encounters for multi-encounter day testing.

### 6.10 Battlefield and positioning

Positioning uses a grid system (5-foot squares). This is important because:
- Range matters (spells, weapons)
- Area of effect matters (cones, lines, spheres)
- Cover matters (half cover, three-quarters cover, total cover)
- Flanking matters (2024: flanking is optional rule; default OFF for standardization)
- Opportunity attacks depend on movement

Battlefield sizes: standard 60x60 foot encounter area, with configurable terrain features. Larger arenas for ranged encounters (120-ft for sniper scenarios).

### 6.11 Movement

Movement is tracked as "remaining speed this turn." Different movement types (walk, fly, swim, climb, burrow) have different speeds per combatant.

Difficult terrain doubles movement cost. Opportunity attacks trigger when leaving an enemy's reach without Disengage.

Dash action grants additional speed equal to movement speed. Cunning Action (rogue) grants Dash as bonus action.

### 6.12 Cover and line of sight

- **Half cover:** +2 AC, +2 DEX saves
- **Three-quarters cover:** +5 AC, +5 DEX saves
- **Total cover:** Cannot be targeted directly

Line of sight is computed from attacker square to target square. Intervening obstacles determine cover.

### 6.13 Death and dying

At 0 HP: character falls unconscious, begins making death saves at start of turn.

Death saves: roll d20. 10+ = success. 9- = failure. Three successes = stabilized at 0 HP. Three failures = dead. Natural 20 = revive at 1 HP. Natural 1 = two failures.

Damage while at 0 HP: counts as a death save failure (2 failures if critical).

Revivify, Raise Dead, Resurrection, True Resurrection all function per spell rules.

### 6.14 Encounter initialization

To start an encounter, the engine needs:
- Party members (from Content Registry)
- Enemies (from Content Registry)
- Battlefield (arena size, terrain features)
- Starting positions
- Initial conditions (any pre-combat buffs, surprise status)
- Random seed

Engine rolls initiative, applies surprise disadvantage (2024 rule change), and begins round 1.

### 6.15 Encounter termination

An encounter ends when:
- All enemies defeated (party victory)
- All party members defeated (TPK)
- One side flees (if behavior AI decides to retreat)
- Turn limit reached (default: 20 rounds, prevents infinite loops)

Outcome is recorded with metrics.

---

## 7. Non-Combat Resolution Engine

### 7.1 Non-combat test structure

Non-combat tests evaluate content against standardized challenge batteries. Unlike combat (which is emergent from mechanics), non-combat tests are more structured.

Three non-combat pillars:
- **Social:** Conversation, negotiation, deception, intimidation
- **Exploration:** Movement, survival, navigation, environmental hazards
- **Investigation:** Information gathering, deduction, lore retrieval, detection

### 7.2 Skill check resolution

```
Raw roll: 1d20
+ Ability modifier
+ Proficiency bonus (if proficient)
+ Expertise (if expertise: add proficiency bonus again)
+ Item bonuses (Guidance cantrip, etc.)
+ Feature bonuses (Reliable Talent: treat d20 as 10 minimum if proficient)
± Situational

Compare to DC (typically 10/15/20/25 for Easy/Medium/Hard/Very Hard).
```

### 7.3 Social pillar battery

A standard set of social encounters tests:

- **Persuasion battery:** 20 persuasion checks at varied DCs (10, 15, 20, 25)
- **Deception battery:** 20 deception checks at varied DCs
- **Intimidation battery:** 20 intimidation checks at varied DCs
- **Insight battery:** 20 insight checks (detecting lies, reading motivation)
- **Performance battery:** 10 performance checks (when relevant to content)

Success rate per DC tier is computed and reported.

**Content features that matter:**
- Skill proficiency (+prof to checks)
- Expertise (+prof again)
- Ability score (primary stat for this skill)
- Spells: Friends, Charm Person, Suggestion, Enthrall, Detect Thoughts, Zone of Truth
- Class features: Bardic Inspiration (not directly, but enhancing allies), Expertise features
- Feats: Skilled, Actor

Scoring: weighted average success rate across all DC tiers, with tiers weighted to reflect typical play (more medium checks than very hard).

### 7.4 Exploration pillar battery

A standard set of exploration challenges:

- **Survival battery:** Tracking, foraging, weather interpretation, navigation
- **Perception battery:** Spotting hidden things, hearing, noticing environment
- **Investigation battery (environmental):** Examining scenes, finding clues in physical space
- **Athletics battery:** Climbing, jumping, swimming
- **Acrobatics battery:** Balancing, falling gracefully, escaping grapples
- **Stealth battery:** Evading detection
- **Movement challenges:** Cross a 60-ft chasm, traverse difficult terrain, reach a high ledge

**Content features that matter:**
- Skill proficiencies and expertise (as above)
- Movement types (flight, climb, swim, teleport) matter enormously
- Sensory features (darkvision, truesight, blindsight)
- Spells: Fly, Misty Step, Dimension Door, Pass Without Trace, Speak with Animals
- Feats: Athlete, Skulker, Keen Mind

### 7.5 Investigation pillar battery

A standard set of investigation challenges:

- **Investigation (deduction):** Piecing together clues from scattered information
- **Arcana, History, Religion, Nature:** Lore retrieval at varying DCs
- **Insight:** Social/psychological deduction
- **Perception:** Detail noticing
- **Divination coverage:** Does the content grant access to divination spells?

**Content features that matter:**
- Mental ability scores (INT primary, WIS secondary)
- Skill proficiencies and expertise
- Spells: Detect Thoughts, Commune, Contact Other Plane, Divination, Legend Lore, Scrying, Speak with Dead, True Seeing
- Languages known (each language is 0.5 points of utility coverage)
- Features: Bardic Lore (Jack of All Trades), Inscrutable, Truesight

### 7.6 Non-combat scoring

Each pillar generates a score from 0 to 100:

- **Skill success rate** weighted by DC tier (40% of score)
- **Spell/feature coverage** (how many utility options content provides; 30%)
- **Situational versatility** (how often features are applicable across diverse situations; 20%)
- **Resource economy** (spells slots needed vs at-will features; 10%)

Scores are per content type and pillar. Baseline distributions are computed across WotC content.

### 7.7 Limitations to acknowledge

Non-combat simulation is a proxy, not a true measure. Actual play involves DM adjudication, creativity, and narrative context that cannot be fully simulated. Reports will include a disclaimer to this effect.

What we DO measure reliably:
- Raw skill check success probability
- Spell access for utility effects
- Feature coverage breadth

What we CANNOT measure:
- Whether the content is fun to play
- Whether creative applications of features will succeed at a given DM's table
- Whether the content's narrative fits the campaign

---

## 8. Behavior AI Specification

### 8.1 AI design philosophy

Behavior AI is where "what is possible" becomes "what will happen." The AI plays each character competently within their role, making tactical decisions that a thoughtful player would make.

The AI is **rule-based with option scoring**, not a neural network or LLM call. This is intentional for:
- **Determinism:** Same seed gives same decisions
- **Auditability:** Users can inspect why a decision was made
- **Performance:** Rules fire in microseconds; LLM calls are slow
- **Cost:** Running millions of simulations with LLM calls would be prohibitive

### 8.2 Decision-making structure

Each turn, for each combatant, the AI:

1. **Surveys the scenario:** current HP, ally status, enemy threats, remaining resources, active effects
2. **Enumerates available actions:** from the combatant's feature list, what can they do this turn?
3. **Scores each action:** assigns a utility score based on situational fit
4. **Selects highest-scoring action** (with minor randomization for tie-breaking to avoid degenerate loops)
5. **Executes:** declares the action to the engine

### 8.3 Action scoring heuristics

Actions are scored based on:

- **Expected damage output:** How much damage will this deal? (higher = better for offense)
- **Damage mitigation:** How much damage does this prevent/heal? (higher = better for defense)
- **Resource efficiency:** What's the cost vs benefit? (lower cost for same effect = better)
- **Concentration economy:** If concentration slot needed, is this the best use?
- **Action economy:** Is this the best use of this action slot (action vs bonus action vs reaction)?
- **Situational multipliers:** E.g., AoE spells score higher against many enemies, single-target higher against bosses

Each character class has specialized heuristics. A Battle Master scores Trip Attack higher against enemies who haven't been proned; a Cleric scores Healing Word higher when an ally is at 0 HP; a Wizard scores Shield (reaction) higher when a hit would drop them below 50% HP.

### 8.4 Tactical profiles

Three AI profiles define overall strategy:

**Competent tactical (standard):** Uses resources appropriately. Conserves for tough fights. Focuses fire. Protects vulnerable allies. Does not make obviously bad choices.

**Aggressive:** Spends resources freely. Always takes the highest-damage action available. Rarely defensive.

**Conservative:** Hoards resources. Prefers cantrips and at-will abilities. Uses spell slots only when necessary.

For the baseline, all tests use **competent tactical**. Aggressive and Conservative profiles are available for variance analysis.

### 8.5 Monster AI

Monsters use the same decision framework but with additional considerations:

- **Intelligence tier** (from schema): low-INT (animal) monsters are more predictable and reactive; high-INT monsters coordinate, target spellcasters, use terrain
- **Retreat behavior:** Intelligent monsters at low HP may attempt to flee
- **Behavior hints from schema:** "Prefer breath weapon when multiple enemies in cone" etc.

### 8.6 Behavior AI for homebrew content

This is a real challenge. Homebrew subclasses may have features the base AI doesn't know how to score. Two approaches:

**Approach 1: Schema hints.** Homebrew authors include behavior hints (combat role, priority targets, resource conservation, synergy notes) in the subclass/monster schema. AI consults hints when scoring actions.

**Approach 2: Generic fallback.** If no hint is provided, AI applies generic heuristics based on feature type (damage features scored on damage output, control features scored on target count and save DC, etc.).

Both approaches are needed. Hints give authors control; fallback handles authors who don't provide them.

**Open question:** Should AI use an LLM for novel homebrew actions? **Recommendation:** No for baseline generation (performance + determinism). Possibly yes as a premium feature for homebrew testing, if baseline rules AI scores actions as "unknown." Defer to Phase 4.

### 8.7 AI consistency guarantees

The AI:
- Never cheats (doesn't know information the character shouldn't)
- Never makes decisions that require information not available in-scenario
- Never deliberately plays badly (no "sandbagging")
- Always prefers the highest-scoring action given known information

The AI does NOT:
- Play optimally in a meta-game sense (e.g., no "save Counterspell for this specific spell at turn 3 because I know the DM will cast it")
- Simulate player mistakes or creative plays
- Handle improvisation or unorthodox tactics

---

## 9. Test Harness Design

### 9.1 Common harness structure

Every test harness shares a common structure:

1. **Setup:** Build party configuration (4-person baseline, or 5-person with test content added, or party + test monster)
2. **Scenario generation:** Create a set of scenarios per test protocol
3. **Execution:** Run scenarios through simulation engine, multiple times per scenario for statistical validity
4. **Metric collection:** Gather outcome data (win rate, damage, resources, etc.)
5. **Comparison:** Compare to baseline distribution for this content type
6. **Report generation:** Produce structured output

### 9.2 Subclass test harness

**Configuration:** Standard party + test subclass as fifth member. The fifth member is built using the class template (e.g., if testing a Warlock subclass, use the supplementary Warlock template).

**Scenarios:**
- **Combat:** 4 encounter difficulties (low, moderate, high, deadly) × 20 levels × 1000 runs = 80,000 combat simulations per subclass
- **Solo endurance:** Horde wave survival test × 20 levels × 500 runs = 10,000 solo simulations
- **Non-combat:** All three pillars (social, exploration, investigation) run through standardized batteries

**Metrics:**
- Party win rate (combat)
- Party HP remaining at encounter end
- Rounds to resolution
- Subclass damage contribution
- Resources spent by subclass
- Participation tier distribution
- Impact tier distribution
- Solo survival rate (wave count)
- Non-combat skill success rates per pillar

**Baseline comparison:** Against the class's WotC subclass distribution on all metrics.

**Verdict categories per metric:**
- Within 1 standard deviation of WotC mean: "Balanced"
- Within 1-2 standard deviations: "Slightly over/under tuned, investigate"
- Beyond 2 standard deviations: "Significantly over/under tuned, likely broken"

### 9.3 Monster test harness

**Configuration:** Standard party (4-person) vs test monster. No fifth member for monster tests.

**Party levels tested:** CR of monster, CR±2, CR±4 (skipping levels below 1 or above 20).

**Encounter compositions:**
- Solo: 1 test monster
- Pair: 2 test monsters
- Squad: 3-5 test monsters (for CR ≤ 10)
- Horde: 6+ test monsters (for CR ≤ 4)
- Mixed: Test monster as leader with supporting weaker creatures

**Scenarios:** Each composition × each party level × 1000 runs.

**Metrics:**
- Party win rate
- Party HP remaining
- Rounds to resolution
- Damage taken by party
- Damage dealt by test monster
- Resources consumed by party
- Number of party deaths during encounter (pre-revivify)
- Monster's legendary resistance/action usage
- Environmental factors (in-lair vs standard)

**Baseline comparison:** Against CR-appropriate WotC monsters at same encounter compositions.

**Verdict:** Is the monster a viable encounter threat at its stated CR? Does it over/under-perform relative to published monsters of the same CR?

### 9.4 Magic item test harness

**Configuration:** Standard party with test item equipped on appropriate member. Selection by item type:
- Weapons → Garrick (martial) or Mira (ranged)
- Armor → Garrick
- Cleric-focused items → Elowyn
- Wizard-focused items → Varian
- Rogue-focused items → Mira
- Universal items → run tests on multiple party members, take best fit

**Scenarios:** Standard combat encounter battery + type-specific non-combat scenarios.

**Metrics:**
- Party performance delta (with item vs without)
- Specific item feature usage (charges spent, abilities triggered)
- Encounter shift (does the item change outcome categories?)

**Baseline comparison:** Against WotC items of the same rarity tier.

**Verdict:** Does the item match its rarity tier in impact? Is it under-rarity or over-rarity?

### 9.5 Background test harness

**Configuration:** Standard party with test background swapped onto one member (typically chosen by background's ability score alignment).

**Scenarios:** Primary focus on non-combat batteries, with limited combat impact testing (origin feat effect on combat).

**Metrics:**
- Skill success rates (social, exploration, investigation)
- Origin feat combat impact (if any)
- Resource/feature coverage

**Baseline comparison:** Against WotC background distribution, especially focusing on origin feat balance.

**Verdict:** Does the background's origin feat fit within the origin feat power distribution? Are skill combos reasonable?

### 9.6 Species test harness

**Configuration:** Standard party with test species applied to one member. The base class is kept (e.g., testing a new species on a Fighter chassis).

**Scenarios:** Full test battery (combat, solo, non-combat).

**Metrics:**
- Same as subclass tests (delta from party baseline)
- Species trait utilization (which traits actually activated during tests)

**Primary scoring:** Species trait point system (per species schema). Additionally validated by simulation.

**Baseline comparison:** Against WotC species trait point distribution.

**Verdict:** Is trait point total within WotC range? Does simulation confirm the scoring?

### 9.7 Spell test harness

**Configuration:** Standard party with test spell added to appropriate caster's known/prepared list.

**Scenarios:** Scenario set tailored to spell intent tags:
- Damage spells → damage-focused combat battery
- Control spells → combat with save-requiring enemies
- Healing spells → combat with high-damage enemies
- Utility spells → relevant non-combat scenarios
- Buff/debuff → combat where spell impact can be measured

**Metrics:**
- How often behavior AI chooses to cast the spell (usage rate)
- Outcome delta when spell is cast vs not
- Resource cost vs benefit

**Baseline comparison:** Against baseline spells of the same level and intent category.

**Verdict:** Does the spell outperform, match, or underperform baseline spells of its level?

### 9.8 Feat and Epic Boon test harness

**Configuration:** Feat applied to appropriate party member. Epic Boon test restricted to levels 19-20 only.

**Scenarios:** Full test battery at feat's relevant levels.

**Metrics:**
- Party performance delta (with feat vs without)
- Feat feature utilization rate
- Combat impact vs non-combat impact

**Baseline comparison:** Against feat distribution (origin vs general vs epic boon, per category).

**Verdict:** Does feat match its category's power distribution?

---

## 10. Participation and Impact Tracking

### 10.1 Categorization system

Every run of every scenario is tagged with:

**Participation tier:**
- **Fully participated:** Content under test was active for ≥50% of encounter rounds
- **Partial participation:** Active for 1-49% of rounds
- **No participation:** Incapacitated or dead before first turn
- **Not relevant:** Encounter ended before content could contribute (rare)

**Impact tier (for participated runs):**
- **High impact:** Contributed significantly beyond average baseline (damage, healing, control)
- **Moderate impact:** Contributed within expected range
- **Low impact (mechanical):** Had turns but features did nothing due to enemy immunities, high saves, unfavorable conditions
- **Low impact (random):** Had turns with appropriate targets but dice rolls were poor

### 10.2 Inferring impact tier

Mechanical vs random low-impact distinction:
- If content shows low impact across many runs in a specific scenario, that's MECHANICAL (the scenario is bad for this content)
- If content shows low impact in scattered runs with no scenario pattern, that's RANDOM (variance)

Statistical test: compare variance within scenario to variance across scenarios. Higher scenario-specific variance than overall variance suggests mechanical issue.

### 10.3 Reporting categorization

Reports include both conditional and unconditional metrics:

**Conditional:** "When this subclass fully participated, its average damage contribution was 42.3 per round."
**Unconditional:** "Across all encounters, this subclass's average damage contribution was 38.7 per round (factoring in runs where it was dead or partially participating)."

Users see both numbers. The difference reveals survivability concerns.

### 10.4 Never silently filter

Per earlier methodological discussion: the framework never silently drops runs. All runs are preserved; users see categorized breakdowns. This prevents survivorship bias from inflating fragile content's apparent performance.

---

## 11. Baseline Generation Pipeline

### 11.1 Offline generation (Phase 2)

Baseline generation runs once per rules version. It:

1. Loads all WotC content for the rules version
2. For every content piece, runs the appropriate test harness at full sample size
3. Stores results per content type as versioned reference documents
4. Generates per-class/per-category distribution statistics (mean, stddev, quartiles, outlier thresholds)
5. Stores as immutable baseline v1.0 (or whatever version)

### 11.2 Baseline scope (Phase 1 initial)

First baseline run targets:
- All PHB 2024 subclasses (48) plus Heroes of Faerûn (8) plus Forge of the Artificer (5) = 61 subclasses
- All published WotC monsters (500+)
- All published WotC magic items (several hundred)
- All PHB 2024 backgrounds (16)
- All PHB 2024 species (10) plus any subsequent additions
- All published WotC spells (several hundred)
- All PHB 2024 feats plus Epic Boons (several dozen)

Total baseline simulation count: approximately 12-15 million simulations across all content types.

Estimated compute: roughly 24-72 hours on a modest cloud instance, or overnight on a dedicated desktop with modern hardware. Probably $50-200 in cloud compute for full baseline.

### 11.3 Baseline storage format

Each baseline reference document is a structured JSON/YAML file containing:

- Baseline version ID (e.g., "baseline_v1.0")
- Rules version tested against (e.g., "2024_phb_plus_forge_plus_heroes")
- Content category
- Per-content results with participation/impact breakdowns
- Per-category distribution statistics
- Pass/fail thresholds derived from distribution
- Generation timestamp
- Engine version used

These documents are immutable. If engine or rules change, a new baseline version is generated.

### 11.4 Baseline immutability and versioning

Critical: once a baseline is published, it doesn't change. Homebrew reports reference specific baseline versions.

If engine updates change results, a new baseline is generated. Old reports still reference old baseline (with a note that a newer baseline is available).

Migration tool: when new baseline released, users can retest their homebrew against it and see updated results.

### 11.5 Continuous baseline updates

As WotC releases new content, baseline is appended to (new subclasses tested, distribution stats updated). Each update bumps baseline version.

Rules errata may require engine updates, which in turn may invalidate prior baselines. Clear communication to users about baseline versions and their compatibility.

---

## 12. Reporting System

### 12.1 Report types

**Baseline reference reports:** Generated once per baseline version. Contain full distributions, per-content statistics, methodology notes. Used as the reference against which homebrew is compared.

**Homebrew test reports:** Generated per homebrew submission. Show how the submission compares to the relevant baseline distribution.

**Raw data exports:** CSV/JSON of all simulation results for user analysis (optional, per Liege's direction for log access).

### 12.2 Homebrew test report structure

A homebrew report contains:

1. **Executive summary:** One-line verdict per test pillar (combat, non-combat pillars, solo endurance if applicable)
2. **Submission details:** What was tested, when, against which baseline
3. **Per-pillar analysis:**
   - Specific metrics measured
   - Comparison to baseline distribution
   - Position in distribution (percentile, standard deviations from mean)
   - Verdict (balanced/slightly off/significantly off)
4. **Participation and impact breakdown:** Tiered reporting
5. **Diagnostic observations:** Specific situations where content over/under performed
6. **Raw data link:** If logging enabled
7. **Recommendations:** Suggested tweaks if content is out of balance (optional, based on common patterns)

### 12.3 Report formats

Reports are generated in multiple formats:
- **Markdown:** Primary format for human readability
- **PDF:** Exportable/shareable format
- **JSON:** Machine-readable for integration with other tools
- **CSV:** Raw data for statistical analysis

Users select which format they need; all are generated from the same underlying data.

### 12.4 Visualizations

Reports include charts where useful:
- Distribution histogram showing WotC content positions with test content's position highlighted
- Performance across levels (line chart: metric vs character level)
- Radar/spider chart: content's scores across all pillars
- Participation/impact pie charts

Visualizations use a consistent style across reports (library like matplotlib or plotly).

### 12.5 Report versioning

Every report includes:
- Engine version
- Baseline version
- Schema version
- Report template version

This allows old reports to be reinterpreted if methodology evolves.

---

## 13. Logging System

Per Liege's direction: logs are an optional, user-toggled feature, structured as CSV, with each line containing decision/roll/resolution.

### 13.1 Log toggle

Before a test runs, user indicates whether to generate detailed logs. Default: off (saves compute and storage).

Higher-tier subscription or paid tests always generate logs; free-tier tests may log summaries only.

### 13.2 Log format

**Columns (base CSV):**
- `run_id`: unique identifier for this simulation run
- `round`: encounter round number
- `turn_number`: turn within round
- `actor_id`: who is acting
- `action_type`: category of action (attack, spell, move, etc.)
- `action_id`: specific action identifier
- `target_id`: target of action (if applicable)
- `roll`: primary die roll (attack roll, save, ability check)
- `modifiers`: all modifiers applied, comma-separated
- `total`: final resolved value
- `outcome`: hit/miss/save/fail/etc.
- `damage`: damage dealt (if any)
- `hp_change`: HP change on actor/target
- `resources_used`: resources consumed this action
- `conditions_applied`: conditions added
- `conditions_removed`: conditions ended
- `details_json`: JSON blob for event-specific extra data

### 13.3 Log volume estimation

Typical encounter: 5 rounds × 9 combatants × 3 events per combatant per round = 135 events per encounter.

At 300 bytes per event: 40KB per encounter.

80,000 simulations per subclass test: 3.2 GB per test (uncompressed). Compressed: roughly 500-800MB.

This is downloadable but non-trivial. Provide compressed (gzip) download by default.

### 13.4 Log retention

- **Free tier:** Summary logs only, retained 7 days
- **Paid tier:** Full logs, retained 90 days
- **Per-test download:** Available immediately after test completion

Long-term archival (>90 days) requires user download. Storage costs prohibit indefinite retention.

### 13.5 Log utility

Logs enable users to:
- Verify specific outcomes (why did my subclass die in round 2?)
- Run their own statistical analysis (custom metrics)
- Debug behavior AI decisions (what did the AI choose and why?)
- Identify patterns (is my subclass weaker against specific enemy types?)

### 13.6 AI decision logging

For logs-enabled runs, AI decision traces are logged separately (or as part of details_json):
- Candidate actions considered
- Score per candidate
- Selected action and rationale

This provides full transparency on behavior AI decisions for auditing.

---

## 14. Deployment Architecture

### 14.1 Library-first design

The core engine (Layers 1-5) is designed as a standalone Python library with a clean API. No dependencies on web frameworks, databases, or UIs.

```python
# Pseudocode example of library API
from balance_framework import (
    ContentRegistry, 
    StandardParty, 
    SubclassTestHarness,
    BaselineLoader,
    ReportGenerator
)

registry = ContentRegistry.load(content_path="./content/")
party = StandardParty.at_level(8)
harness = SubclassTestHarness(registry, party)
result = harness.test(subclass_id="my_homebrew_subclass", runs=1000)
baseline = BaselineLoader.load("baseline_v1.0")
report = ReportGenerator.compare(result, baseline)
print(report.to_markdown())
```

### 14.2 CLI tool (Phase 2)

A command-line interface wraps the library for local use:

```bash
balance-framework test subclass --file my_subclass.yaml --runs 1000 --output report.md
balance-framework generate-baseline --rules 2024 --output baselines/v1.0/
```

This is the primary Phase 2 deliverable. You run simulations locally on your hardware; the CLI outputs reports.

### 14.3 Web service (Phase 4 option)

A web service wraps the library with:
- User authentication
- Submission storage
- Rate limiting (free tier = 1 test/day)
- Billing (paid tiers)
- Report generation and download

Architecture:
- **Frontend:** Web UI (React or similar) for content submission and result viewing
- **Backend API:** Wraps library calls, handles auth and limits
- **Worker queue:** Simulations run asynchronously (Celery, RQ, or similar)
- **Database:** User accounts, submissions, report metadata
- **Storage:** Baselines (static files), logs (object storage)

### 14.4 Hybrid model

Per Liege's pondering: library is open-source, web service is hosted. Users can choose local (free, technical) or hosted (fee-based, convenient).

The library is licensed permissively (e.g., MIT or Apache 2.0). The hosted service adds value through:
- No setup required
- Pre-computed baseline (no generation wait)
- Form-based authoring UI
- Result persistence and history
- Collaborative features

### 14.5 Deployment phases

**Phase 2:** Library + CLI, local use only. Solves Liege's personal use case.
**Phase 3:** Homebrew authoring and report generation refined based on usage.
**Phase 4:** Web service launched (if pursued).

### 14.6 Content delivery

Baselines are delivered as:
- Downloadable files (for library users)
- Pre-loaded on hosted service

Baselines are version-stamped so library users can validate their baseline against the official release.

---

## 15. Scoring Systems

### 15.1 Combat scoring

Combat metrics are quantitative:
- Win rate (0-100%)
- HP remaining at encounter end (0-party_total%)
- Rounds to resolution (lower = faster victory)
- Resource efficiency (features used per encounter / effectiveness)

Baseline distribution is computed from WotC content. Test content is placed in distribution and evaluated.

### 15.2 Non-combat scoring

Per pillar (social, exploration, investigation):
- Weighted skill success rate (0-100)
- Feature coverage score (0-100)
- Situational versatility score (0-100)
- Resource economy score (0-100)

Composite pillar score: weighted average of component scores.

### 15.3 Species trait scoring

Per species schema v0.1: point-based system. Each trait has a score. Total score compared to WotC distribution.

Scoring values are calibrated so WotC species cluster in 8-12 point range. Homebrew outside 5-15 flagged.

### 15.4 Magic item scoring

Per magic item schema v0.1: rarity-based budget. Each item feature has a score. Item score compared to rarity budget and WotC items of same rarity.

### 15.5 Feat scoring

Per feat schema v0.1: category-based budget (origin 3-5 points, general 6-10, epic boon 10-15). Feat features scored, total compared to category distribution.

### 15.6 Score normalization

All scores are normalized to comparable scales (typically 0-100) for reporting. Raw data is preserved; normalized scores are for presentation only.

### 15.7 Context-dependent scores

Some scoring values are context-dependent (e.g., darkvision more valuable in dark campaigns). Reports note context assumptions used in scoring.

Users can see both context-neutral (average) scores and context-specific scores if they specify a campaign context.

---

## 16. Versioning and Compatibility

### 16.1 Version types

- **Schema version:** Structure of content files. Incremented when schema changes (rare after v1.0).
- **Engine version:** Simulation engine code. Incremented on mechanic changes, bug fixes, optimizations.
- **Baseline version:** Pre-computed baseline. Incremented when baseline regenerated.
- **Rules version:** D&D rules edition (e.g., "2024"). Incremented by WotC.

### 16.2 Compatibility matrix

Each baseline is associated with:
- Specific engine version
- Specific rules version
- Specific schema version (typically the current one)

Reports state the versions used. Incompatible combinations (e.g., old engine + new content) are rejected.

### 16.3 Backward compatibility

When schema updates:
- Old content is migrated automatically where possible
- Migration may generate warnings for author review
- Significant schema changes create new schema version; both supported during transition

When engine updates:
- Old baselines become legacy (still usable for historical reports)
- Users prompted to retest against new baseline for updated verdicts

### 16.4 WotC rules updates

When WotC releases new content or errata:
- Engine maintainers update content registry
- New baseline generated including new content
- Users notified of baseline version bump
- Existing homebrew can be retested against new baseline

---

## 17. Testing the Test Framework

### 17.1 Validation needs

The framework itself must be validated. Possible issues:
- Simulation engine bugs (rules misapplied)
- Behavior AI making obviously bad decisions
- Scoring algorithms producing nonsense values
- Baseline generation inconsistencies

### 17.2 Validation methodology

**Unit tests:** Each engine component tested against known-correct outcomes.

Example: Cast Fireball (5 enemies in area, DEX save DC 15) with fixed seeds. Verify damage dealt, saves made, damage applied. Hundreds of such tests.

**Integration tests:** Full encounter scenarios with known expected outcomes.

Example: Level 5 standard party vs 4 ogres. Run 10,000 times. Expected win rate should be roughly 70-90% based on DMG encounter difficulty. If our sim says 15% or 100%, something is wrong.

**WotC sanity checks:** Baseline generation includes validation: WotC subclasses should cluster in expected performance ranges. If Assassin Rogue tests as the strongest subclass in the game, our sim is lying.

**User-reported issues:** Bug reports from users lead to targeted tests.

### 17.3 Validation batteries

A dedicated validation test suite (separate from balance tests) runs before every baseline generation:
- 500+ unit tests
- 50+ integration scenarios
- 10+ sanity checks per class

All must pass before baseline is published.

### 17.4 Ongoing validation

Engine changes trigger re-running validation battery. Any regression blocks release.

Users can report suspicious results. These become new validation tests if confirmed as bugs.

---

## 18. Known Unknowns and Deferred Decisions

### 18.1 Decisions deferred to implementation

- **Specific programming language:** Python recommended for ecosystem (NumPy, pandas, matplotlib). Discuss in Phase 2 kickoff.
- **Specific behavior AI rule language:** Could be code-based rules, config-based, or hybrid. Decide during implementation.
- **Database choice for web service:** PostgreSQL recommended but deferred to Phase 4.
- **Specific billing system:** Stripe likely, deferred to Phase 4.

### 18.2 Known limitations

- **Campaign context variability:** Scoring assumes "typical" context; specific campaigns (all-dungeon, high-magic, low-magic) may differ.
- **DM adjudication:** Real-world variability not captured.
- **Player creativity:** Improvised tactics not simulated.
- **Long-term campaign dynamics:** Each test is session-scale; multi-session implications not modeled.

### 18.3 Questions still to answer

1. **Power budget estimation for homebrew:** Pre-test sanity check would require the engine to estimate power budget from features. Complex to implement; defer to Phase 3.

2. **Homebrew class support:** Currently scoped for subclasses, not full classes. Full class testing adds complexity (base chassis variance). Phase 5 consideration.

3. **Multi-class character testing:** Not in scope. Framework assumes single-class for simplicity.

4. **Variant rules support:** Flanking, resting variants, etc. Default is RAW; variants may be added as configuration options.

5. **Campaign setting specifics:** Eberron, Forgotten Realms, Ravenloft may have setting-specific content. Framework is setting-agnostic; setting-specific content tested with same harness.

6. **Group balance vs individual balance:** Framework measures individual content against peers. Doesn't directly evaluate whether a whole party of mixed homebrew is balanced. This is a party-construction problem, not content balance.

7. **Meta-balance issues:** Features that are weak alone but overpowered in combination. Framework tests individual content; combinations are user's responsibility.

### 18.4 Phase 2 scope check

Phase 2 (library + CLI, local baseline generation) should target:
- Core engine (Layers 1-5)
- Subclass and monster harnesses (the two most critical)
- Baseline generation for PHB 2024 content
- Markdown reports
- CSV log export

Other harnesses (item, background, species, spell, feat) can be Phase 2.5 or 3.

### 18.5 Success criteria for Phase 2

Phase 2 is successful when:
- Engine passes full validation suite
- Standard party builds correctly at all levels 1-20
- Subclass test harness generates reports for all 61 WotC subclasses
- Monster test harness generates reports for at least 50 WotC monsters across CR range
- Baseline v1.0 generated and published
- Reports match sanity expectations (no obviously broken results)
- CLI usable for non-programmers with clear documentation

### 18.6 Out of scope for this document

- Specific UI design (Phase 4)
- Specific pricing model (Phase 4)
- Marketing strategy
- Community building
- Documentation for end users (will be a separate deliverable)

---

## Document Revision History

- **v0.1 (current):** Initial architecture specification. Covers all layers, test harnesses, deployment considerations. Ready for Phase 2 implementation planning.

---

## Next Steps

Upon approval of this specification:

1. Finalize remaining open questions (deferred above).
2. Set up VS Code + Git repository for Phase 2 implementation.
3. Generate handoff package: implementation prompts for Claude Code, file structure, starting commit.
4. Begin Phase 2 implementation with engine layer first (bottom-up).

The specification is deliberately detailed to minimize Phase 2 rework. If implementation reveals missing details, this document is updated (v0.2) and implementation adjusts.
