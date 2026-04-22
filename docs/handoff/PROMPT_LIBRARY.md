# Claude Code Prompt Library

This document contains concrete prompts for building each Phase 2 component using Claude Code in VS Code. Prompts are organized by milestone and designed to produce working, tested code that fits the architecture specification.

---

## How to use this library

Each prompt is a starting point. Customize the bracketed sections for your specific situation. Before running any prompt, ensure:

1. Claude Code has access to the relevant documentation files (architecture spec, schemas, this handoff package) — add them to context
2. The prerequisite milestones are complete (do not run M3 prompts before M2 is done)
3. Your local repository is clean (no uncommitted changes that could be clobbered)

**Prompt conventions:**
- Square brackets `[like this]` indicate content you customize
- Prompts assume Claude Code is running in the repository root
- Every prompt includes a validation step; do not skip it
- Every prompt should result in a commit (or a set of commits); never leave uncommitted work

**When a prompt produces unexpected output:**
- Do not accept the change blindly
- Ask Claude Code to explain its reasoning
- If the reasoning is unsound, refine the prompt and retry
- If the architecture spec is ambiguous, resolve the ambiguity explicitly before proceeding

---

## Table of Contents

1. [M0: Repository Setup](#m0-repository-setup)
2. [M1: Schema Layer](#m1-schema-layer)
3. [M2: Content Registry and Character Builder](#m2-content-registry-and-character-builder)
4. [M3: Engine Core](#m3-engine-core)
5. [M4: Behavior AI](#m4-behavior-ai)
6. [M5: Test Runner and Sanity Checks](#m5-test-runner-and-sanity-checks)
7. [M6: Subclass Test Harness](#m6-subclass-test-harness)
8. [M7: Reporting Layer](#m7-reporting-layer)
9. [M8: CLI](#m8-cli)
10. [Content Authoring Prompts](#content-authoring-prompts)
11. [Cross-Cutting Prompts](#cross-cutting-prompts)

---

## M0: Repository Setup

### Prompt M0.1: Initialize repository structure

```
Task: Initialize the D&D Homebrew Balance Framework repository.

Context files to load:
- docs/handoff/PROJECT_STRUCTURE.md
- docs/handoff/README.md

Requirements:
1. Create the directory structure exactly as specified in PROJECT_STRUCTURE.md
2. Create empty __init__.py files for all Python packages
3. Create a pyproject.toml with:
   - Project name: balance-framework
   - Python requirement: >=3.11
   - Core dependencies: pydantic>=2.0, pyyaml, click, numpy
   - Dev dependencies: pytest, pytest-cov, ruff, mypy, pre-commit
   - Reporting dependencies: matplotlib, pandas
   - src layout (src/balance_framework/)
4. Create .gitignore for Python projects (include .venv/, __pycache__/, .pytest_cache/, *.egg-info/)
5. Create .pre-commit-config.yaml with ruff (format and lint) and mypy
6. Create LICENSE file (MIT or Apache 2.0 — ask user which they prefer if unclear)
7. Create initial README.md (copy from docs/handoff/README.md)

Deliverables:
- All directories exist with __init__.py where needed
- Configuration files in place
- pre-commit install runs successfully

Validation: Run these commands and verify success:
- python -m venv .venv
- source .venv/bin/activate  (or .venv\Scripts\activate on Windows)
- pip install -e ".[dev]"
- pre-commit install
- pre-commit run --all-files (may have formatting adjustments; accept them)
- pytest --version

Do not commit until all validation passes. When ready, commit with message:
"chore: initial repository scaffolding"
```

### Prompt M0.2: CI/CD configuration

```
Task: Set up GitHub Actions CI pipeline.

Create .github/workflows/ci.yml that:
1. Runs on push to any branch and on pull requests to main
2. Sets up Python 3.11 and 3.12 matrix
3. Installs dependencies with pip install -e ".[dev]"
4. Runs pre-commit checks
5. Runs pytest with coverage
6. Uploads coverage report as an artifact

Validation: Push to a feature branch and verify the workflow runs and passes.

Commit with message: "chore: add GitHub Actions CI workflow"
```

---

## M1: Schema Layer

### Prompt M1.1: Build Pydantic models for all content types

```
Task: Implement the schema layer using Pydantic models.

Context files to load:
- docs/schemas/class_schema.md
- docs/schemas/subclass_schema.md
- docs/schemas/species_schema.md
- docs/schemas/background_schema.md
- docs/schemas/spell_schema.md
- docs/schemas/magic_item_schema.md
- docs/schemas/monster_schema.md
- docs/schemas/feat_and_epic_boon_schema.md
- docs/handoff/champion_fighter_example.yaml (as a known-valid reference)

Requirements:
1. Create src/balance_framework/schema/types.py with Pydantic models for:
   - Class, Subclass, Species, Background, Spell, MagicItem, Monster, Feat
   - Shared types: Feature, ResourcePool, ProgressionEntry, BehaviorHint
2. Create src/balance_framework/schema/vocabulary.py defining allowed values:
   - FEATURE_TYPES: list of valid feature_type strings from the schemas
   - ACTION_TYPES: bonus_action, action, reaction, etc.
   - DAMAGE_TYPES: all 5e damage types
   - CONDITIONS: all 5e conditions
   - ABILITY_SCORES: STR, DEX, CON, INT, WIS, CHA
3. Create src/balance_framework/schema/exceptions.py:
   - ValidationError (base)
   - SchemaViolation (for structural errors)
   - VocabularyViolation (for invalid values in enums)
   - ReferenceError (for broken cross-references — used in M2)
4. Create src/balance_framework/schema/validators.py:
   - validate_class(yaml_dict) -> Class
   - validate_subclass(yaml_dict) -> Subclass
   - ... one function per content type
   - Each raises descriptive errors on failure

Style:
- Use Pydantic v2 (BaseModel, Field, field_validator)
- Use Literal types for enum-like fields
- Provide descriptive field descriptions for documentation
- Enforce constraints via Field (ge=1, le=20 for levels, etc.)

Deliverables:
- src/balance_framework/schema/ package complete
- Unit tests in tests/unit/schema/ covering:
  - Valid content validates successfully
  - Missing required fields raise SchemaViolation
  - Invalid feature_type raises VocabularyViolation
  - Wrong value types raise clear errors

Validation:
- Run: pytest tests/unit/schema/ -v
- All tests must pass
- Load docs/handoff/champion_fighter_example.yaml through validate_subclass() and verify it returns a valid Subclass object

Commit with message: "feat(schema): add Pydantic validation for all content types"
```

### Prompt M1.2: Schema validation script

```
Task: Add a CLI-accessible script to validate all YAML content files.

Create scripts/validate_content.py that:
1. Walks the content/ directory
2. For each YAML file, determines its content type from the directory path
3. Runs the appropriate validator from balance_framework.schema.validators
4. Reports success/failure per file
5. Returns non-zero exit code if any file fails
6. Supports a --fix flag that reports common issues (trailing whitespace, tab indentation) without auto-fixing

Validation:
- Run: python scripts/validate_content.py
- Should report 0 files validated (content/ is empty at this point)
- Create a deliberately broken YAML file and verify it is caught
- Create a valid YAML file (port docs/handoff/champion_fighter_example.yaml to content/subclasses/fighter/champion.yaml) and verify it validates

Commit with message: "feat(scripts): add content validation script"
```

---

## M2: Content Registry and Character Builder

### Prompt M2.1: Content registry

```
Task: Build the content registry that loads and stores all validated content.

Context files to load:
- docs/architecture_spec.md (especially §3.2 Layer 2: Content Registry)
- docs/schemas/*.md

Requirements:
1. Create src/balance_framework/registry/loader.py:
   - load_content_directory(path: Path) -> dict[str, dict[str, Any]]
   - Walks the content/ directory, loads YAML files, validates each
   - Returns nested dict: {content_type: {id: validated_object}}
2. Create src/balance_framework/registry/registry.py:
   - ContentRegistry class
   - Holds all loaded content in memory
   - get_class(id), get_subclass(id), get_spell(id), etc.
   - get_all_subclasses_for_class(class_id)
   - Raises ReferenceError if content not found
3. Create src/balance_framework/registry/resolver.py:
   - Resolves cross-references: subclass → class, always-prepared spells → spell objects
   - Called after loading completes
   - Raises descriptive errors for broken references

Deliverables:
- registry/ package complete
- Unit tests covering:
  - Loading a well-formed content/ directory
  - Loading with one invalid file raises descriptive error
  - Cross-reference resolution catches missing references
  - Registry getters work correctly

Validation:
- Run: pytest tests/unit/registry/ -v
- Create a minimal content/ directory with:
  - content/classes/fighter.yaml (stub; can be minimal)
  - content/subclasses/fighter/champion.yaml (from M1.2)
  - content/species/human.yaml (stub)
  - content/backgrounds/soldier.yaml (stub)
- Load the registry and verify all content is accessible

Commit with message: "feat(registry): add content registry and cross-reference resolution"
```

### Prompt M2.2: Character builder

```
Task: Implement the character builder that produces a fully-resolved Character at a specified level.

Context files to load:
- docs/architecture_spec.md (§3.2)
- docs/party_sheets/01_Garrick_BattleMaster_Fighter_v0.2.md (Battle Master reference)

Requirements:
1. Create src/balance_framework/registry/character_builder.py
2. Define dataclasses:
   - CharacterBuild (input): species_id, class_id, subclass_id, background_id, level, ability_scores, feat_choices, equipment, prepared_spells
   - Character (output): fully resolved with all features applied, HP, AC, save bonuses, attack bonuses, spell DC, active conditions slot, resource pools, etc.
3. Implement build_character(build: CharacterBuild, registry: ContentRegistry) -> Character:
   - Applies species traits
   - Applies background ASIs
   - Applies class features up to specified level
   - Applies subclass features up to specified level
   - Applies feat choices
   - Applies equipment modifiers
   - Computes derived stats (HP, AC, save DC, attack bonuses)
4. HP calculation: use average hit die + CON mod per level, plus any HP-granting features (Tough, Draconic Resilience, etc.)

Deliverables:
- CharacterBuild and Character dataclasses
- build_character() function
- Unit tests for each build stage
- Integration tests: build each standard party member at levels 1, 5, 10, 15, 20

Validation:
- Run: pytest tests/integration/test_character_build_end_to_end.py -v
- Manually verify: Garrick at level 20 should have ~200 HP, AC ~22 with +3 plate + shield, save DC matching WIS, etc. Match against docs/party_sheets/.

Commit with message: "feat(registry): add character builder"
```

---

## M3: Engine Core

### Prompt M3.1: Engine scaffolding

```
Task: Build the engine package structure with stubs for all combat mechanics.

Context files to load:
- docs/architecture_spec.md (§3.3 and §6 Engine)

Requirements:
1. Create src/balance_framework/engine/ package
2. Create engine/scenario.py:
   - ScenarioState dataclass: combatants list, round_number, current_turn_index, environment
   - CombatantState dataclass: character_ref, hp_current, hp_max, conditions, concentration_spell, resources_current, position
3. Create engine/dice.py:
   - Deterministic dice rolling using numpy's Generator
   - roll(notation: str, advantage: bool = False, disadvantage: bool = False) -> int
   - Supports standard 5e notation: "1d20+5", "2d6", etc.
4. Create engine/combat/ submodules, each with stub functions:
   - initiative.py: roll_initiative(combatants, rng) -> turn_order
   - turns.py: start_of_turn_effects(state, combatant), end_of_turn_effects(state, combatant)
   - actions.py: ActionDeclaration dataclass, resolve_action(state, declaration, rng) -> ActionResult
   - attacks.py: resolve_attack(attacker, target, weapon, rng) -> AttackResult
   - saves.py: resolve_save(target, dc, ability, rng) -> bool
   - damage.py: apply_damage(target, amount, damage_type) -> new_state
   - conditions.py: Condition enum, apply_condition(target, condition, duration)
   - concentration.py: check_concentration(combatant, damage, rng) -> bool
   - resources.py: spend_resource(combatant, pool_id, amount) -> new_state
5. Create engine/resolver.py:
   - Main engine entry point: run_combat(scenario, ai, rng) -> CombatResult

Deliverables:
- Complete package structure
- All stub functions return placeholder values (attack always hits, damage always 10, etc.)
- Stubs raise NotImplementedError for any operation not yet stubbed
- Unit tests for each stub verifying the interface

Validation:
- Run: pytest tests/unit/engine/ -v
- All stub tests pass (they test interface shape, not behavior)

Commit with message: "feat(engine): add engine scaffolding with stubs"
```

### Prompt M3.2: Attack resolution

```
Task: Implement full attack roll resolution in engine/combat/attacks.py.

Context:
- 5e 2024 PHB attack rules
- Crit ranges can be modified (Champion: 19-20, then 18-20)
- Advantage/disadvantage from multiple sources cancel out

Requirements:
1. Implement resolve_attack(attacker, target, weapon, rng, advantage_sources, disadvantage_sources) -> AttackResult:
   - AttackResult contains: hit: bool, crit: bool, total_roll: int, damage_rolled: int (if hit)
   - Handles advantage/disadvantage correctly (roll twice, take appropriate)
   - Applies attack bonus from character (ability mod + proficiency + weapon bonuses)
   - Checks against target AC
   - Natural 20 always crits (regardless of AC)
   - Natural 1 always misses
   - Expanded crit ranges apply from features
2. Implement roll_damage(weapon, crit: bool, rng) -> int:
   - Rolls weapon dice
   - On crit, doubles weapon dice (not modifiers)
   - Applies damage bonuses (ability mod, magic weapon bonus, feats)

Deliverables:
- attacks.py fully implemented (no stubs)
- Unit tests covering:
  - Normal attack (hit/miss/crit)
  - Advantage: reroll low d20 taken
  - Disadvantage: reroll high d20 taken
  - Advantage + disadvantage cancel
  - Expanded crit range applies correctly
  - Crit doubles weapon dice only, not modifiers
  - Nat 20 crits against any AC
  - Nat 1 always misses

Validation:
- Run: pytest tests/unit/engine/combat/test_attacks.py -v
- All tests pass with deterministic seeds

Commit with message: "feat(engine): implement attack resolution"
```

### Prompt M3.3 through M3.N: Remaining combat mechanics

For each component (saves, damage, conditions, concentration, resources, turns), use this template:

```
Task: Implement [COMPONENT] in engine/combat/[file].py.

Reference: 5e 2024 PHB rules for [COMPONENT].

Requirements:
1. Replace the stub in [file].py with full implementation
2. Handle all standard cases per PHB
3. Edge cases to cover:
   - [LIST SPECIFIC EDGE CASES FOR THIS COMPONENT]

Deliverables:
- [file].py fully implemented
- Unit tests in tests/unit/engine/combat/test_[component].py
- Each test uses a fixed seed for determinism
- Tests cover: happy path, edge cases, interaction with other components

Validation:
- pytest tests/unit/engine/combat/test_[component].py -v

Commit with message: "feat(engine): implement [COMPONENT]"
```

**Edge cases per component:**

- **Saves:** legendary resistance, save vs half damage, save vs full effect, advantage/disadvantage on saves, reroll features (Indomitable)
- **Damage:** resistance (half, rounded down), vulnerability (double), immunity (zero), temporary HP ordering, damage types (mundane vs magical)
- **Conditions:** stacking rules (conditions don't stack, but durations refresh), condition immunity, save-to-end conditions, automatic end triggers
- **Concentration:** DC calculation (10 or half damage, whichever higher), concentration saves with War Caster advantage, losing concentration on incapacitation
- **Resources:** short rest recovery, long rest recovery, pool caps, partial refresh conditions
- **Turns:** start-of-turn effects (regeneration, ongoing damage, condition saves), end-of-turn effects, initiative ties

### Prompt M3.Final: Engine integration test

```
Task: Write a full-round combat integration test.

Requirements:
1. Create tests/integration/test_single_combat_round.py
2. Scenario: Garrick (level 5 Battle Master, standard sheet) versus one orc
3. Expected behavior:
   - Garrick wins initiative (rolled with fixed seed)
   - Round 1: Garrick Attacks (2 attacks via Extra Attack), hits some, misses some
   - Orc responds with attack or action
   - Damage applied, conditions tracked
4. Assertions:
   - Final state is reachable from initial state via deterministic operations
   - Damage totals match expected values with known seeds
   - HP tracking is accurate
   - No NotImplementedError raised (all engine components functional)

Validation:
- Run: pytest tests/integration/test_single_combat_round.py -v
- Run with multiple seeds (10 different seeds) and verify all complete without errors

Commit with message: "test(engine): add end-to-end single round combat test"
```

---

## M4: Behavior AI

### Prompt M4.1: Action enumeration

```
Task: Implement action enumeration — given a scenario state and a combatant, list all legal actions.

Context:
- docs/architecture_spec.md (§8 Behavior AI)

Requirements:
1. Create src/balance_framework/ai/enumeration.py
2. Implement enumerate_actions(state, combatant) -> list[ActionDeclaration]:
   - For each action type (action, bonus action, reaction, movement):
     - List all legal options given combatant's features, resources, and state
     - Include: weapon attacks, spell casts, feature activations, dodge/disengage/help/hide
   - Legality checks: resource availability, range, line of sight, condition restrictions

Deliverables:
- enumeration.py complete
- Unit tests for typical combatants (Fighter, Wizard, Cleric) producing expected action lists

Validation:
- pytest tests/unit/ai/test_enumeration.py -v

Commit with message: "feat(ai): add action enumeration"
```

### Prompt M4.2: Action scoring

```
Task: Implement action scoring — assign utility value to each legal action.

Context:
- docs/architecture_spec.md (§8.4 Action Scoring)

Requirements:
1. Create src/balance_framework/ai/scorer.py
2. Implement score_action(action: ActionDeclaration, state, combatant, behavior_hints) -> float:
   - Base score from expected outcome (e.g., expected damage for attacks)
   - Adjustments from behavior hints (combat role, target preferences, resource conservatism)
   - Adjustments from game state (HP ratios, encounter progress, threat assessment)
3. Implement select_action(state, combatant, behavior_hints) -> ActionDeclaration:
   - Enumerates actions
   - Scores each
   - Returns highest-scoring (with random tie-break using rng)

Deliverables:
- scorer.py complete
- Unit tests covering:
  - Healer scores healing over damage when ally is bloodied
  - Striker scores attack on highest-HP enemy
  - Caster scores appropriate spells for situation
  - Tie-breaking is deterministic with fixed seed

Validation:
- pytest tests/unit/ai/test_scorer.py -v

Commit with message: "feat(ai): add action scoring and selection"
```

### Prompt M4.3: AI profiles and class heuristics

```
Task: Implement AI profiles (competent, aggressive, conservative) and class-specific heuristics.

Requirements:
1. Create src/balance_framework/ai/profiles.py:
   - AIProfile class with risk tolerance, resource conservatism, target preference weights
   - Default profiles: COMPETENT, AGGRESSIVE, CONSERVATIVE
2. Create src/balance_framework/ai/heuristics/:
   - martial.py: fighter, barbarian, paladin, ranger, monk heuristics
   - caster.py: wizard, sorcerer, warlock heuristics
   - healer.py: cleric, druid, bard heuristics
   - support.py: rogue heuristics
   - Each module registers scoring adjustments for its class
3. Integrate heuristics into scorer.py (heuristics add bonus/penalty to base scores)

Deliverables:
- Profiles and heuristics complete
- Integration test: standard party members make class-appropriate decisions in test scenarios

Validation:
- Run integration test: tests/integration/test_party_decisions.py
- Manually verify decisions look competent (e.g., Varian casts Fireball against groups, Mira Sneak Attacks priority targets)

Commit with message: "feat(ai): add profiles and class heuristics"
```

### Prompt M4.4: Monster AI

```
Task: Implement monster AI with intelligence tier handling.

Context:
- docs/architecture_spec.md (§8.5 Monster AI)

Requirements:
1. Create src/balance_framework/ai/monster.py
2. Monster AI uses simpler heuristics than player character AI:
   - Low INT (under 4): attack nearest enemy, use most damaging attack available
   - Medium INT (5-11): attack weakest visible enemy, use signature abilities when available
   - High INT (12+): target backline, use tactical positioning, preserve resources
3. Honor monster YAML's behavior_hints where present

Deliverables:
- monster.py complete
- Unit tests for each INT tier
- Integration test: orc (low INT) attacks frontline, mind flayer (high INT) targets backline

Validation:
- pytest tests/unit/ai/test_monster.py -v
- pytest tests/integration/test_monster_behavior.py -v

Commit with message: "feat(ai): add monster behavior AI"
```

---

## M5: Test Runner and Sanity Checks

### Prompt M5.1: Test runner

```
Task: Build the multi-run test orchestrator.

Context:
- docs/architecture_spec.md (§7 Test Runner)

Requirements:
1. Create src/balance_framework/runner/orchestrator.py:
   - TestRun dataclass: scenario, num_runs, seed_base
   - run_test(test_run) -> TestResult
   - For each run: derive seed from seed_base + run_index, create RNG, run engine, collect result
2. Create src/balance_framework/runner/seeding.py:
   - Deterministic seed derivation: hash(seed_base + run_index) or similar
   - Ensures runs are independent but reproducible
3. Create src/balance_framework/runner/collector.py:
   - Aggregate outcomes across runs
   - Compute statistics: win rate, mean/median damage, HP distributions, round counts

Deliverables:
- Runner package complete
- Unit tests for seeding (determinism, distribution)
- Integration test: run 100 simulations of a fixed scenario, verify statistics are sensible

Validation:
- pytest tests/unit/runner/ -v
- pytest tests/integration/test_runner_determinism.py -v

Commit with message: "feat(runner): add multi-run orchestrator"
```

### Prompt M5.2: Sanity check suite

```
Task: Build the engine validation (sanity check) suite.

Context:
- docs/architecture_spec.md (§18.3 Engine Validation)

Requirements:
1. Create tests/validation/ directory with specific test files:
   - test_encounter_difficulty.py: DMG-guided encounter outcomes
   - test_class_dpr.py: per-class damage per round matches optimization guides
   - test_wotc_sanity.py: WotC subclasses cluster appropriately
2. Each sanity check runs 1000+ simulations and asserts statistical properties:
   - test_encounter_difficulty.py:
     - Level 5 standard party vs 1 Hard encounter (4 orcs): 70-90% win rate
     - Level 10 standard party vs 1 Deadly encounter: 40-70% win rate
   - test_class_dpr.py:
     - Level 5 Fighter with +1 weapon: DPR between 15-25
     - Level 5 Wizard with Fireball available: DPR between 15-30
   - test_wotc_sanity.py:
     - No WotC subclass shows outlier participation tier (all should fall in the reference band)

Deliverables:
- tests/validation/ complete
- Each sanity check documented with expected ranges and rationale
- Running all validation tests takes no more than 30 minutes

Validation:
- Run: pytest tests/validation/ -v --timeout=1800
- All checks pass (if any fail, investigate engine correctness immediately)

Commit with message: "test(validation): add engine sanity check suite"
```

---

## M6: Subclass Test Harness

### Prompt M6.1: Subclass harness

```
Task: Build the subclass test harness.

Context:
- docs/architecture_spec.md (§9 Test Harnesses, §9.1 Subclass Harness)

Requirements:
1. Create src/balance_framework/harnesses/base.py with abstract Harness base class
2. Create src/balance_framework/harnesses/subclass.py:
   - SubclassHarness class
   - test(subclass_yaml_path, levels: list[int], num_runs: int) -> HarnessResult
   - For each level:
     - Build the test character with the target subclass (replaces supplementary template's subclass)
     - Build standard party at same level
     - Run combat encounters (varying difficulty: easy, medium, hard, deadly)
     - Run solo endurance encounters
     - Run non-combat pillar tests (social, exploration, investigation)
     - Collect participation and impact tiers
3. Output HarnessResult as structured JSON

Deliverables:
- Subclass harness complete
- Integration test: test Champion Fighter subclass, produce valid result
- Documentation of result schema

Validation:
- pytest tests/integration/test_subclass_harness.py -v
- Manually run harness on Champion and verify output is sensible

Commit with message: "feat(harnesses): add subclass test harness"
```

---

## M7: Reporting Layer

### Prompt M7.1: Markdown reports

```
Task: Build markdown report generation for homebrew test results.

Context:
- docs/architecture_spec.md (§11 Reporting)

Requirements:
1. Create src/balance_framework/reporting/test_report.py:
   - generate_homebrew_report(harness_result, baseline_data) -> str (markdown)
   - Sections: summary, comparison to baseline, participation/impact breakdown, per-level details, per-encounter details
2. Create src/balance_framework/reporting/visualizations.py:
   - Histogram generation for distributions (using matplotlib)
   - Output as PNG files embedded in markdown
3. Create src/balance_framework/reporting/formats/markdown.py:
   - Template rendering helpers

Deliverables:
- Reporting layer complete for markdown
- Integration test: generate report for Champion harness result

Validation:
- pytest tests/integration/test_report_generation.py -v
- Visually inspect generated report for readability

Commit with message: "feat(reporting): add markdown report generation"
```

### Prompt M7.2: Baseline reference documents

```
Task: Build baseline reference document generation.

Requirements:
1. Create src/balance_framework/reporting/baseline.py:
   - generate_baseline_doc(subclass_id, harness_results_all_levels) -> dict (JSON-serializable)
   - Contains distribution statistics, percentiles, participation/impact bands
2. Save baseline to baselines/vX.Y/subclasses/{subclass_id}.json

Deliverables:
- Baseline generation complete
- Test: generate baseline for Champion

Validation:
- pytest tests/integration/test_baseline_generation.py -v

Commit with message: "feat(reporting): add baseline reference document generation"
```

---

## M8: CLI

### Prompt M8.1: CLI implementation

```
Task: Build the command-line interface.

Requirements:
1. Create src/balance_framework/cli/ package using Click
2. Commands:
   - balance-framework test subclass --file FILE --runs N --output FILE
   - balance-framework validate (runs sanity check suite)
   - balance-framework generate-baseline --rules 2024 --output DIR --tier [A|B|C|all]
   - balance-framework build-character --class X --subclass Y --level N (for debugging)
3. Configure entry point in pyproject.toml: balance-framework = "balance_framework.cli.main:cli"

Deliverables:
- CLI package complete
- After `pip install -e .`, `balance-framework --help` works
- Each command has descriptive --help text

Validation:
- Run each CLI command and verify sensible output or errors
- Check: `balance-framework --help` lists all commands

Commit with message: "feat(cli): add command-line interface"
```

---

## Content Authoring Prompts

These are prompts for authoring YAML content files. Run them as needed throughout Phase 2.

### Prompt C.1: Author a class YAML

```
Task: Author a class YAML file for [CLASS NAME].

Context files to load:
- docs/schemas/class_schema.md
- docs/handoff/champion_fighter_example.yaml (subclass example; similar patterns)

Requirements:
1. Use the class schema exactly
2. Use 2024 PHB rules (not 2014)
3. Include ALL class features for all 20 levels
4. Include the full progression table
5. Declare class resource pools (e.g., Second Wind, Channel Divinity)
6. Place output at content/classes/[class_id].yaml

Input: The 2024 PHB entry for [CLASS NAME] follows below. Use only this text.

[PASTE PHB TEXT]

Validation:
- python scripts/validate_content.py
- Must show content/classes/[class_id].yaml validates successfully

Commit with message: "content: add [class name] class YAML"
```

### Prompt C.2: Author a subclass YAML

Use the Claude Code prompt template from `docs/authoring_guides/subclass_authoring_guide.md` §10.

### Prompt C.3: Author a monster YAML

```
Task: Author a monster YAML file for [MONSTER NAME].

Context files to load:
- docs/schemas/monster_schema.md
- docs/architecture_spec.md (§9.2 Monster Harness)

Requirements:
1. Use 2025 Monster Manual rules (unified ability table, Gear field, Habitat field, single-use legendary actions)
2. Include all actions, reactions, bonus actions
3. Include spellcasting (if applicable) with at-will and per-day lists
4. Populate behavior_hints based on creature intelligence
5. Place output at content/monsters/cr_[CR]/[monster_id].yaml

Input: The 2025 MM entry for [MONSTER NAME] follows below.

[PASTE MM TEXT]

Validation:
- python scripts/validate_content.py

Commit with message: "content: add [monster name] monster YAML"
```

### Prompt C.4: Author species, backgrounds, spells, feats, magic items

Use templates analogous to C.1, referencing the appropriate schema document.

---

## Cross-Cutting Prompts

### Prompt X.1: Add a new feature type to the schema vocabulary

```
Task: Extend the schema vocabulary to support a new feature type.

Situation: Content authoring revealed that [FEATURE DESCRIPTION] cannot be expressed with the existing feature_type vocabulary.

Requirements:
1. Analyze the gap: explain why existing types don't fit
2. Propose a new feature_type name (snake_case, descriptive)
3. Define the body schema for this type (what fields are required/optional)
4. Update src/balance_framework/schema/vocabulary.py
5. Update src/balance_framework/schema/types.py (Pydantic model for the new body shape)
6. Update docs/schemas/subclass_schema.md (or relevant schema doc) to document the new type
7. Update the engine to handle the new type (which module? what behavior?)
8. Add unit tests for the new type
9. Update docs/authoring_guides/subclass_authoring_guide.md to mention the new type

Deliverables:
- Schema updated with new type
- Engine supports the new type
- Tests pass
- Documentation updated

Validation:
- Author at least one subclass YAML using the new type
- Validate and test the subclass

Commit with multiple commits:
- "feat(schema): add [feature_type] to vocabulary"
- "feat(engine): handle [feature_type] in engine"
- "docs: document [feature_type]"
- "content: use [feature_type] in [subclass]"
```

### Prompt X.2: Refactor a module for clarity

```
Task: Refactor [MODULE PATH] for improved readability.

Context:
- The module has grown to [LINES] lines and is difficult to navigate
- Related concerns are mixed

Requirements:
1. Identify logical separations (e.g., attack roll vs damage roll)
2. Split into multiple modules if appropriate
3. Update imports in dependent modules
4. Ensure all tests still pass
5. Do not change behavior; this is pure refactoring

Deliverables:
- Refactored code
- All tests still pass
- Diff shows movement, not behavioral change

Validation:
- pytest (full suite)
- Coverage unchanged (no new untested paths introduced)

Commit with message: "refactor([module]): split into focused submodules"
```

### Prompt X.3: Debug a failing test

```
Task: Investigate and fix [TEST_PATH]::[test_name].

Context:
- Test is failing with: [ERROR MESSAGE]
- Git bisect or recent changes might identify the breaking change

Requirements:
1. Reproduce the failure locally
2. Identify whether the bug is in the test or in the code under test
3. If code bug: fix the code and add a regression test
4. If test bug: fix the test (with justification for why the original was wrong)

Deliverables:
- Fix committed
- Test passes
- Related tests also pass

Commit with message (code bug): "fix([module]): [brief description of bug]"
Commit with message (test bug): "test([module]): correct test for [behavior]"
```

---

## Prompt quality principles

When crafting prompts for Claude Code, follow these principles:

**Be specific about outputs.** "Build a schema validator" is vague. "Create src/balance_framework/schema/validators.py with one validator function per content type that returns a Pydantic model or raises SchemaViolation with the path of the invalid field" is specific.

**Reference architecture docs.** Always include file paths to the relevant specification sections. Claude Code has limited memory; it needs the spec in context.

**Require tests.** Every prompt should include a validation step that runs tests. Code without tests is an anti-pattern.

**Require commits.** Every prompt ends with a commit message. This forces closure on each unit of work.

**Forbid scope expansion.** If the prompt says "implement attacks," do not let Claude Code also implement saves. Separate prompts for separate concerns.

**Validate before accepting.** Read every generated file. Understand why each line exists. Reject code you do not understand or that does not match the specification.

---

## Revision History

- **v0.1 (current):** Initial prompt library covering M0-M8 and content authoring patterns.
