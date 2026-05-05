# Phase 2 Implementation Plan

This document defines the sequence of work for Phase 2 (implementation). The plan uses **engine-first development**: build the complete engine shell with stubs, then fill in mechanics incrementally, validating against the test suite at each step.

---

## Table of Contents

1. [Phase 2 Overview](#1-phase-2-overview)
2. [Engine-First Development Rationale](#2-engine-first-development-rationale)
3. [Milestone Sequence](#3-milestone-sequence)
4. [Parallel Work Streams](#4-parallel-work-streams)
5. [Week-by-Week Plan](#5-week-by-week-plan)
6. [Success Criteria](#6-success-criteria)
7. [Risk Management](#7-risk-management)

---

## 1. Phase 2 Overview

**Phase 2 goal:** Produce a functional Python library and CLI tool that can:

1. Load and validate all seven content types from YAML
2. Build a standard party character at any level 1-20
3. Run a single-encounter combat simulation with deterministic results
4. Run the full subclass test harness against any single subclass
5. Generate a baseline reference document for WotC content
6. Generate a homebrew test report

**Phase 2 is NOT:**

- A web service (that is Phase 4)
- A production-grade product (quality-first, polish later)
- Feature-complete across all harnesses (subclass and monster are primary; others are stretch)

**Phase 2 duration estimate:** 6-12 weeks of focused work, depending on time availability. Can be compressed if content authoring is parallelized effectively.

---

## 2. Engine-First Development Rationale

**Why engine-first:**

Content authoring and engine implementation could theoretically happen in either order. Engine-first was chosen for these reasons:

**Content validation requires the engine.** Before knowing whether a subclass YAML is correctly encoded, the engine must be able to load and use it. Authoring 47 subclass files before the engine exists risks discovering schema bugs after significant rework is needed.

**Engine architecture exposes content gaps.** When the engine needs a feature type that the schema does not support, the gap becomes visible during implementation. Early engine work identifies these gaps before content authoring commits to the current schema.

**Sanity checks need the engine.** Determining whether the engine applies rules correctly requires running simulations. These simulations need content, but the minimum content needed is just the standard party and one or two opponents. That content can be authored incrementally alongside engine development.

**Engine-first does not mean zero content.** Every engine capability has corresponding content requirements. As each engine milestone lands, the content needed for that milestone is authored.

**Alternative considered (content-first):** Authoring all subclass YAMLs first, then building the engine against them, was rejected because schema bugs would only surface during engine implementation, requiring bulk content revisions.

**Alternative considered (vertical slice):** Getting one full test working end-to-end before expanding was rejected because the standard party involves four characters across 20 levels, representing most of the engine's complexity. A "vertical slice" would effectively be 70% of the full engine.

---

## 3. Milestone Sequence

Each milestone has a defined scope, deliverables, and verification criteria. See `MILESTONE_CHECKLISTS.md` for detailed criteria.

### M0: Repository Setup

**Scope:** Initial scaffolding, tooling, CI/CD, pre-commit hooks.

**Deliverables:**
- Repository initialized with proper structure (per `PROJECT_STRUCTURE.md`)
- `pyproject.toml` with dependencies declared
- `.pre-commit-config.yaml` with ruff and mypy
- `.github/workflows/ci.yml` running tests on push
- README.md explaining setup
- First commit following conventions

**Estimated effort:** 2-4 hours

### M1: Schema Layer

**Scope:** Schema validation for all seven content types.

**Deliverables:**
- `src/balance_framework/schema/` package with Pydantic models
- Validators for class, subclass, species, background, spell, magic_item, monster, feat
- Vocabulary module defining allowed `feature_type` values
- Clear error messages for validation failures
- Unit tests covering valid and invalid inputs for each content type

**Verification:**
- Can load the Champion example YAML from `docs/handoff/`
- Rejects malformed YAML with a descriptive error
- Rejects YAML missing required fields
- Rejects YAML with invalid `feature_type` values

**Estimated effort:** 1 week

### M2: Content Registry and Character Builder

**Scope:** Load validated content, resolve cross-references, build characters at specified levels.

**Deliverables:**
- `src/balance_framework/registry/` package
- `ContentRegistry` class loading from `content/` directory
- Cross-reference resolution (subclass → class → spells → etc.)
- Character builder producing resolved character objects
- Unit tests for reference resolution
- Integration test: build Garrick at levels 1, 5, 10, 15, 20

**Verification:**
- All content YAML files in `content/` directory load without error
- Cross-references resolve correctly
- Character builder produces a `Character` object with all features correctly applied at the requested level
- Standard party characters match their documented sheets (HP, AC, skills, features)

**Content needed before M2 completion:**
- All 13 class YAML files (the base class chassis; can be minimal)
- 4 subclass YAMLs for the standard party (Battle Master, Life Domain, Evoker, Thief)
- Human species YAML
- Backgrounds used by the standard party (Soldier, Acolyte, Sage, Charlatan)
- A handful of spells used by the standard party (Cure Wounds, Fireball, Shield, etc.)
- A minimal magic item set (+1 weapon, +1 armor, Cloak of Protection)
- Origin feats for the standard party (Tough, Alert, Healer)

**Estimated effort:** 1-2 weeks (includes first content authoring pass)

### M3: Engine Core (Combat Resolution)

**Scope:** Full combat simulation for a single encounter, with deterministic dice and complete rules handling.

**Deliverables:**
- `src/balance_framework/engine/combat/` submodules (attacks, saves, damage, conditions, concentration, resources)
- Scenario state and combatant state dataclasses
- Turn and round management
- Condition tracking and application
- Death and dying rules
- Unit tests for each combat component
- Integration test: run a single combat round with deterministic seed

**Verification:**
- Attack roll resolution matches PHB math exactly (attack bonus, crit range, advantage/disadvantage)
- Saving throws resolve correctly with all relevant modifiers
- Damage resistance/vulnerability/immunity applied correctly
- Conditions tracked across turns with correct end conditions
- Concentration breaks on sufficient damage and save failure
- Death saves tracked correctly with stabilize/die outcomes
- Same seed produces same outcomes across runs

**Estimated effort:** 2-3 weeks (longest single milestone)

### M4: Behavior AI

**Scope:** Rule-based AI making tactical decisions for combatants.

**Deliverables:**
- `src/balance_framework/ai/` package
- Action enumeration (given a combatant and scenario state, list all legal actions)
- Action scoring (assign utility score to each legal action)
- Decision loop (select highest-scoring action with tie-breaking)
- Three AI profiles: competent tactical, aggressive, conservative
- Class-specific heuristics for at least Fighter, Cleric, Wizard, Rogue
- Monster AI with intelligence tier handling
- Unit tests for scoring logic
- Integration test: standard party versus single orc, expected party victory

**Verification:**
- AI makes reasonable decisions for each standard party member
- AI does not make obviously bad choices (e.g., wizard melee-attacking at 1 HP)
- AI respects behavior hints from YAML content
- Same seed produces same decision sequence

**Content needed before M4 completion:**
- Monster YAML for orc, goblin, ogre (used as common test opponents)

**Estimated effort:** 2 weeks

### M5: Test Runner and Sanity Checks

**Scope:** Orchestrate multi-run simulations and validate the engine produces sensible outcomes.

**Deliverables:**
- `src/balance_framework/runner/` package
- Multi-run orchestrator with seed management
- Result collection and aggregation
- Sanity check validation suite
- Integration test: standard party at level 5 versus 4 orcs, 1000 runs

**Verification:**
- Sanity checks: win rate for level-5 party vs 4 orcs falls in 70-90% range (per DMG encounter difficulty)
- Class DPR estimates match published optimization guide expectations within reasonable bounds
- No infinite loops or hangs (encounter terminates within 20 rounds default)
- Results are reproducible across runs with same seeds

**Estimated effort:** 1 week

### M6: Subclass Test Harness

**Scope:** The first and most important test harness. Tests a single subclass against the standard party, produces structured results.

**Deliverables:**
- `src/balance_framework/harnesses/subclass.py`
- Scenario generation (combat encounters at varied difficulty, solo endurance test, non-combat batteries)
- Metric collection (win rate, damage contribution, participation tier, impact tier)
- Raw result output (JSON)
- Integration test: test the Champion Fighter against the standard party

**Verification:**
- Harness generates the expected number of scenarios (combat + solo + non-combat)
- Participation and impact categorization works correctly
- Conditional and unconditional metrics both computed
- Results are reproducible with fixed seeds

**Content needed before M6 completion:**
- At least 5-10 monster YAMLs across different CRs (for encounter variety)
- Full subclass YAML for at least Champion Fighter (test target)

**Estimated effort:** 1-2 weeks

### M7: Reporting Layer (Markdown)

**Scope:** Generate human-readable reports from test results.

**Deliverables:**
- `src/balance_framework/reporting/` package
- Markdown report generator for homebrew tests
- Baseline reference document generator (JSON output)
- Visualizations (histograms, distribution charts)
- Integration test: produce a full report for a test run

**Verification:**
- Reports are well-formatted and readable
- All relevant metrics appear in the report
- Distribution visualizations render correctly
- Baseline JSON is valid and complete

**Estimated effort:** 1 week

### M8: CLI and End-to-End

**Scope:** Command-line interface wrapping the library for user-facing operation.

**Deliverables:**
- `src/balance_framework/cli/` package
- `balance-framework test subclass` command
- `balance-framework validate` command (sanity check suite)
- `balance-framework generate-baseline` command (long-running; stretches into M9)
- Documentation in README

**Verification:**
- CLI commands run without Python tracebacks
- Output files appear where expected
- Help text is clear and accurate

**Estimated effort:** 3-5 days

### M9: First Baseline Generation (Partial)

**Scope:** Generate baseline for Tier A subclasses (the 16 most common PHB subclasses).

**Deliverables:**
- Full subclass YAMLs for all Tier A subclasses (per authoring guide)
- `baselines/v0.9/` directory with partial baseline
- Documented limitations of the partial baseline
- First homebrew test against the partial baseline

**Verification:**
- All Tier A subclass YAMLs pass schema validation
- Baseline generation runs to completion (may take hours)
- Partial baseline reports are coherent
- At least one homebrew subclass can be tested against the partial baseline and produce a report

**Estimated effort:** 1-2 weeks (mostly content authoring and compute time)

### M10: Full Baseline (Stretch Goal for Phase 2)

**Scope:** Extend baseline to all 61 subclasses plus common monsters.

**Deliverables:**
- Full subclass YAMLs for all 61 subclasses
- Monster YAMLs for a curated set of 50+ monsters across CR range
- `baselines/v1.0/` directory with full baseline
- Phase 2 complete

**Verification:**
- All subclasses in baseline with participation/impact data
- Baseline reference documents complete
- Framework ready for Phase 3 (homebrew balancing)

**Estimated effort:** 2-4 weeks

### M10 prerequisite: Class-level groundwork

Before any subclass can be authored, its parent class must have full engine
infrastructure in place:

1. **Class YAML** at `content/classes/<class_id>.yaml` with all base class
   features for levels 1-20
2. **`_CLASS_DEFAULTS` entry** in the character builder defining default
   ability score arrays, starting equipment templates, and skill proficiency
   options for the class
3. **`CLASS_PROFILE` mapping** in the AI layer, linking the class to the
   appropriate heuristic module (`ai/heuristics/martial.py`, `caster.py`,
   `healer.py`, or `support.py`)
4. **Smoke test** confirming the engine builds and simulates a character of
   this class without errors

After M9 (Tier A), the following classes have this infrastructure:

- Fighter (M2 standard party)
- Cleric (M2 standard party)
- Wizard (M2 standard party)
- Rogue (M2 standard party)
- Barbarian (M9 Tier A: Berserker, World Tree, Zealot)
- Bard (M9 Tier A: Lore)

The following classes need infrastructure added during M10 before their
subclasses can be authored:

- Druid
- Monk
- Paladin
- Ranger
- Sorcerer
- Warlock

(Artificer is Tier C; deferred until later.)

**Recommended ordering** (by increasing engine complexity, so simpler cases
surface engine bugs before complex ones):

1. Paladin (martial half-caster; similar to Cleric)
2. Ranger (martial half-caster; tests Hunter's Mark concentration)
3. Monk (martial with Focus Points; tests new resource mechanic)
4. Druid (full caster + Wild Shape; flag complex transformation logic early)
5. Sorcerer (full caster + Metamagic; tests Sorcery Point spending)
6. Warlock (full caster with Pact Magic; tests short-rest slot recovery)

For each class, complete steps 1-4 (class YAML, defaults, profile, smoke test)
before authoring any of its subclasses. If a smoke test fails, stop and
investigate before proceeding to subclasses; mass-authoring on a broken
chassis multiplies debugging cost.

---

## 4. Parallel Work Streams

While the milestone sequence is mostly linear (each milestone depends on previous ones), some work can be parallelized:

### Stream A: Engine implementation (main path)

M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8

This is the critical path. Each milestone depends on the previous.

### Stream B: Content authoring

After M1 (schema layer) lands, subclass YAML authoring can begin in parallel with engine work:

- During M2: author class YAMLs (13 files), standard party subclasses (4 files), species/backgrounds/spells/items for the standard party
- During M3: author Tier A subclasses (16 files)
- During M4-M5: author Tier B subclasses (20 files: Druid 3, Monk 3, Paladin 3, Ranger 3, Sorcerer 3, Warlock 3, Bard 2)
- During M6-M7: author Tier C subclasses (7 files) and monster YAMLs

Total content authoring effort: approximately 25-40 hours spread across Phase 2.

### Stream C: Test suite expansion

As each engine component lands, corresponding unit and integration tests are written. This is not a separate stream; it happens as part of each milestone. Flagging it to emphasize that tests are required for milestone completion.

### Coordination points

Engine and content streams must sync at:
- **End of M1:** Schema is locked; content authors can proceed without fear of major schema churn
- **End of M2:** Character builder works; content authors can verify their YAML via character build
- **End of M6:** Subclass harness exists; content authors can run test simulations against their subclasses
- **End of M9:** Partial baseline published; content authors finalize Tier A quality

---

## 5. Week-by-Week Plan

This plan assumes approximately 10-20 hours per week of focused effort. Adjust accordingly for your actual pace.

### Week 1: M0 + M1 start

- **Day 1-2:** Repository setup, tooling, CI/CD, pre-commit
- **Day 3-4:** Author base class YAMLs for Fighter and Wizard (simplest cases)
- **Day 5+:** Start M1 schema validation for class and subclass types

### Week 2: M1 complete

- **Day 1-3:** Finish schema validators for all seven content types
- **Day 4-5:** Unit tests for schema layer
- **Day 6-7:** Start M2 content registry

### Week 3: M2 complete

- **Day 1-3:** Content registry and cross-reference resolution
- **Day 4-5:** Character builder
- **Day 6-7:** Integration tests (standard party builds at all levels)

### Week 4-5: M3 Engine Core (combat mechanics)

- **Week 4:** Attacks, saves, damage, dice
- **Week 5:** Conditions, concentration, resources, turn management
- **Ongoing:** Unit tests for each component

### Week 6: M3 complete + M4 start

- **Day 1-3:** Finish combat integration tests
- **Day 4-7:** Start behavior AI (action enumeration, scoring)

### Week 7-8: M4 Behavior AI

- **Week 7:** Scoring, profiles, class heuristics
- **Week 8:** Monster AI, integration tests

### Week 9: M5 Test Runner + Sanity Checks

- **Day 1-3:** Orchestrator, seeding, collector
- **Day 4-7:** Sanity check suite, verify engine correctness

### Week 10: M6 Subclass Harness

- **Day 1-4:** Scenario generation, metric collection
- **Day 5-7:** Integration test with Champion Fighter

### Week 11: M7 Reporting + M8 CLI

- **Day 1-4:** Markdown report generator, visualizations
- **Day 5-7:** CLI implementation

### Week 12: M9 Partial Baseline

- **Content authoring catching up on Tier A if not done**
- **Run baseline generation for Tier A subclasses**
- **Validate baseline, document any issues**

### Beyond Week 12: M10 and Phase 2 completion

- Continue content authoring (Tier B, Tier C)
- Expand baseline to full 61 subclasses
- Monster baseline generation
- Phase 2 complete

---

## 6. Success Criteria

Phase 2 is successful when all of the following are true:

- [ ] All seven content types can be validated from YAML
- [ ] Standard party characters build correctly at all levels 1-20
- [ ] Engine passes full sanity check suite
- [ ] Subclass test harness produces reports for at least the 16 Tier A subclasses
- [ ] Partial baseline v0.9 is published and usable
- [ ] At least one homebrew subclass has been tested end-to-end with a real report
- [ ] CLI is usable without Python knowledge (with clear documentation)

**Stretch goals (Phase 2.5):**

- [ ] All 61 subclass YAMLs authored
- [ ] Full baseline v1.0 published
- [ ] Monster test harness functional
- [ ] Additional harnesses (item, spell, feat) prototyped

---

## 7. Risk Management

### Risk: Engine complexity underestimated

Combat mechanics in 5e have many edge cases (opportunity attacks, reactions, concentration interactions, legendary actions, etc.). M3 could expand significantly.

**Mitigation:** Start with the simple cases (attack rolls, saves, damage). Add complexity incrementally. If a specific mechanic proves too complex, defer it with a `# TODO: not yet supported` marker in the engine.

### Risk: Content authoring bottleneck

If content authoring is delayed, engine milestones requiring content (M2, M6, M9) stall.

**Mitigation:** Author minimum viable content for each milestone (enough to test, not comprehensive). Expand coverage later.

### Risk: Behavior AI complexity

Rule-based AI making competent tactical decisions is hard. Poor AI produces unrealistic simulation results.

**Mitigation:** Start with simple heuristics (attack strongest enemy; use resources when bloodied). Observe AI behavior; iterate based on obvious errors. Accept that AI will be imperfect; document known limitations.

### Risk: Dice variance masking bugs

A bug that causes 5% deviation in outcomes may be hard to distinguish from random dice variance. Engine correctness can be hard to verify.

**Mitigation:** Unit tests use fixed seeds and assert exact outcomes. Validation tests use large sample sizes (1000+ runs) to reduce noise. If a sanity check fails, investigate immediately rather than assuming variance.

### Risk: Scope creep

Adding "one more feature" before releasing is tempting. Phase 2 completion stretches indefinitely.

**Mitigation:** The success criteria above are the definition of Phase 2 complete. Features beyond those criteria are Phase 2.5 or Phase 3.

### Risk: Claude Code producing inconsistent code quality

LLM-generated code may have subtle bugs, inconsistent patterns, or style violations.

**Mitigation:** Review every generated change before committing. Use pre-commit hooks (ruff, mypy) as a baseline. Require tests for every non-trivial change. When in doubt, ask Claude Code to explain its approach before accepting the change.

---

## Revision History

- **v0.1:** Initial Phase 2 plan with engine-first approach. Covers M0-M10 milestones, week-by-week plan, parallel work streams.
- **v0.2 (current):** Phase 2 complete (M10 shipped). Phase 3 roadmap appended below.

---

## Phase 3 Roadmap

Phase 2 delivered a working simulation engine, 45 subclass baselines, and a static web dashboard. Phase 3 expands simulation fidelity and the web product.

### Phase 3 Milestone Sequence

#### M11: Encounter Variety Expansion *(highest priority)*

The current encounter suite uses five fixed compositions, all standard humanoid monsters with simple melee AI. This limits the simulator's ability to surface class weaknesses that only appear against certain enemy types.

**Target enemy categories to add:**

| Category | Examples | Why it matters |
|---|---|---|
| Spellcasting monsters | Mage, Priest, Banshee, Lich | Tests spell interruption, concentration, save-vs-AOE |
| Undead | Zombie horde, Wight, Vampire Spawn | Immunity to conditions, frightened, necrotic |
| Beasts | Wolf pack, Giant Ape, Owlbear pack | Pack tactics, multiattack variety, grapple |
| Fiends | Quasit, Hell Hound, Cambion | Fire immunity, darkness, charm |
| Dragons | Young dragons (CR 7-10) | Breath weapon save, Frightful Presence, legendary feel |
| Constructs | Animated Armor, Iron Golem | Magic immunity, condition immunity |

**Engine work required:**

1. **Spellcasting monster AI profile** — a `monster_caster` behavior profile that spends spell slots (stored in `behavior_hints`) to cast AOE or single-target spells, mirroring `caster_selector` logic
2. **Breath weapon / AOE mechanic** — a `BreathWeaponAction` that hits all enemy combatants in range with a DEX/CON save for half; recharge mechanic (recharges on 5-6)
3. **Mixed-composition encounters** — encounter templates with heterogeneous enemy groups (e.g., 1 caster + 2 warriors, dragon + 2 kobolds), not just N copies of the same monster
4. **Encounter difficulty calibration** — after adding harder enemies, recalibrate so win rates span ~40-90% (currently 78-99% for most classes; not enough spread to see subclass differences)

**Content work required:**

- 20-30 additional monster YAMLs covering the categories above (currently have 10)
- At minimum: mage, priest, zombie, wight, hell hound, young red dragon, iron golem
- `behavior_hints` extended with `spell_slots`, `breath_weapon_damage`, `breath_weapon_save`
- New `STANDARD_ENCOUNTERS` set (replace or extend the current 5-encounter suite)

**Verification:**
- At least 3 spellcasting monsters in the encounter pool
- At least 1 dragon-type encounter (breath weapon fires, frightful presence applies)
- Win rates across all 45 subclasses span a meaningful range (target: some encounters at 40-60% for casters/rogues)
- Existing 540 tests still pass

**Estimated effort:** 2-3 weeks

---

#### M12: Subclass Feature Simulation Depth

Currently only 4 features are simulated (champion crit, hunter's prey, divine fury, elemental affinity). Most subclasses score identically to their class baseline because their defining features aren't wired into the engine.

**Priority features to simulate:**

| Subclass | Feature | Mechanism |
|---|---|---|
| Battle Master | Superiority dice (4d8) | Spend die on first attack for bonus damage + maneuver effect |
| Eldritch Knight | Spell slots + cantrip | Switch to `caster_selector` when no melee targets, or use War Magic |
| Berserker | Frenzy (bonus action attack) | Extra `WeaponAttackAction` appended as bonus action |
| Life Domain | +bonus healing | Heal bonus = `2 + spell_level` added to `HealAction` |
| Wild Magic | Surge table | Random additional effect on spell cast (1-in-20 chance) |
| Gloom Stalker | First-round bonus attack | Extra attack on round 1 only |
| Open Hand | Knockdown on hit | Apply `prone` condition after successful unarmed strike |

This milestone also includes regenerating `baselines/v1.0/` and `web/data/` after each batch of features lands, so the dashboard reflects actual differentiation.

**Estimated effort:** 3-4 weeks (iterative; each feature is a self-contained PR)

---

#### M13: Web Interface Phase 2 — Flask API

Add a Python backend on a cloud host (Render/Railway free tier) so the dashboard can run on-demand small tests without pre-generated data.

**Endpoints:**
- `POST /api/character/build` — accepts `CharacterBuild` JSON, returns stat block
- `POST /api/encounter/quick-test` — runs 10 encounters, returns win rate + summary
- `POST /api/validate` — accepts YAML text, returns validation errors or success

**Key constraints:**
- Runs on Render/Railway (not Bluehost — shared hosting can't run persistent Python)
- Bluehost serves the static frontend; CORS allows it to call the API subdomain
- Encounter runs capped at 20 per request to stay within free-tier CPU limits

**Estimated effort:** 1-2 weeks

---

#### M14: Homebrew Submission Workflow

The end goal of the tool: a DM pastes their homebrew subclass YAML, gets a balance report in under a minute.

**Deliverables:**
- YAML editor in the dashboard with schema hints
- "Run Quick Test" button → calls M13 API → displays results inline
- Comparison against the nearest class baseline ("Your Ranger subclass vs Hunter baseline")
- Shareable result URL (encoded in query string or stored as a short-lived server-side key)

**Estimated effort:** 2-3 weeks (depends on M13 landing first)

---

### Phase 3 Priority Order

```
M11 (encounter variety)  ← start here; unlocks meaningful differentiation
    ↓
M12 (feature simulation) ← makes subclass scores diverge
    ↓
M13 (Flask API)          ← enables interactive testing
    ↓
M14 (homebrew workflow)  ← the product
```

M11 is the gate. Until the encounter pool is harder and more varied, expanding simulation depth (M12) produces numbers that cluster too tightly to be useful.
