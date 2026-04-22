# Milestone Checklists

Verification criteria for each Phase 2 milestone. A milestone is complete only when every checkbox can be marked.

---

## How to use this document

Each milestone has three sections:

1. **Deliverables** — What must exist in the repository
2. **Verification** — Specific commands or observations that confirm it works
3. **Exit gate** — The hard requirements that cannot be skipped

Do not mark a milestone complete if any exit gate item is unchecked. The framework's quality compounds; shortcuts at M3 become blocking bugs at M6.

When in doubt, run the verification commands fresh from a clean checkout. If they fail, the milestone is not complete.

---

## M0: Repository Setup

### Deliverables

- [ ] Repository exists at the chosen hosting location (GitHub, GitLab, etc.)
- [ ] Directory structure matches `PROJECT_STRUCTURE.md` exactly
- [ ] All Python packages have `__init__.py` files
- [ ] `pyproject.toml` exists with correct dependencies
- [ ] `.gitignore` excludes `.venv/`, `__pycache__/`, `*.egg-info/`, `.pytest_cache/`, `.coverage`, `htmlcov/`
- [ ] `.pre-commit-config.yaml` configures ruff (format + lint) and mypy
- [ ] `LICENSE` file exists with chosen license
- [ ] `README.md` at repository root (the handoff package version copied over)
- [ ] `.github/workflows/ci.yml` exists with Python 3.11 and 3.12 matrix
- [ ] At least one commit exists in `main` branch

### Verification

Run these commands from a fresh clone and verify all pass:

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install

# Verification
pre-commit run --all-files        # All hooks pass
pytest --version                   # pytest is installed
mypy --version                     # mypy is installed
ruff --version                     # ruff is installed
python -c "import balance_framework"  # Package imports without error
```

### Exit gate

- [ ] `pre-commit run --all-files` exits with code 0
- [ ] `pytest` runs (zero tests found is fine; tests come later)
- [ ] CI pipeline succeeds on at least one push to `main`
- [ ] `pip install -e ".[dev]"` succeeds on a clean machine

---

## M1: Schema Layer

### Deliverables

- [ ] `src/balance_framework/schema/__init__.py` exports the public API
- [ ] `src/balance_framework/schema/types.py` contains Pydantic models for:
  - [ ] `Class`
  - [ ] `Subclass`
  - [ ] `Species`
  - [ ] `Background`
  - [ ] `Spell`
  - [ ] `MagicItem`
  - [ ] `Monster`
  - [ ] `Feat`
- [ ] `src/balance_framework/schema/vocabulary.py` defines:
  - [ ] `FEATURE_TYPES` (list of valid strings)
  - [ ] `ACTION_TYPES`
  - [ ] `DAMAGE_TYPES`
  - [ ] `CONDITIONS`
  - [ ] `ABILITY_SCORES`
  - [ ] `SKILLS`
- [ ] `src/balance_framework/schema/exceptions.py` defines:
  - [ ] `ValidationError` (base)
  - [ ] `SchemaViolation`
  - [ ] `VocabularyViolation`
  - [ ] `ReferenceError` (used in M2)
- [ ] `src/balance_framework/schema/validators.py` contains:
  - [ ] `validate_class()`
  - [ ] `validate_subclass()`
  - [ ] `validate_species()`
  - [ ] `validate_background()`
  - [ ] `validate_spell()`
  - [ ] `validate_magic_item()`
  - [ ] `validate_monster()`
  - [ ] `validate_feat()`
- [ ] `scripts/validate_content.py` batch-validates all YAML in `content/`
- [ ] Unit tests in `tests/unit/schema/` covering each content type

### Verification

```bash
# Unit tests pass
pytest tests/unit/schema/ -v

# Champion example validates successfully
python -c "
from pathlib import Path
import yaml
from balance_framework.schema.validators import validate_subclass
data = yaml.safe_load(Path('docs/handoff/champion_fighter_example.yaml').read_text())
result = validate_subclass(data)
print(f'Validated: {result.id}')
"

# Deliberately broken YAML is rejected with clear error
python -c "
from balance_framework.schema.validators import validate_subclass
from balance_framework.schema.exceptions import SchemaViolation
try:
    validate_subclass({'content_type': 'subclass'})  # missing required fields
except SchemaViolation as e:
    print(f'Correctly rejected: {e}')
"

# Batch validation runs (even with empty content/)
python scripts/validate_content.py
```

### Test coverage requirements

- [ ] At least one valid-input test per content type
- [ ] At least one missing-required-field test per content type
- [ ] At least one invalid-enum-value test (e.g., invalid feature_type)
- [ ] At least one type-coercion test (e.g., string passed where int expected)

### Exit gate

- [ ] All schema unit tests pass (100% of tests green)
- [ ] Champion example YAML validates successfully
- [ ] Deliberately-broken YAML produces descriptive error messages (not opaque Pydantic tracebacks)
- [ ] Test coverage for `schema/` module is at least 85%

---

## M2: Content Registry and Character Builder

### Deliverables

- [ ] `src/balance_framework/registry/loader.py` walks and validates content directory
- [ ] `src/balance_framework/registry/registry.py` provides `ContentRegistry` class with:
  - [ ] `get_class(id)`, `get_subclass(id)`, etc. for all content types
  - [ ] `get_all_X()` methods for enumerating content
  - [ ] Descriptive errors for missing content (`ReferenceError`)
- [ ] `src/balance_framework/registry/resolver.py` resolves cross-references
- [ ] `src/balance_framework/registry/character_builder.py` provides:
  - [ ] `CharacterBuild` dataclass (input spec)
  - [ ] `Character` dataclass (resolved output)
  - [ ] `build_character(build, registry) -> Character`
- [ ] Standard party content authored in `content/`:
  - [ ] `classes/fighter.yaml`, `cleric.yaml`, `wizard.yaml`, `rogue.yaml` (can be minimal but complete)
  - [ ] `subclasses/fighter/battle_master.yaml`
  - [ ] `subclasses/cleric/life_domain.yaml`
  - [ ] `subclasses/wizard/evoker.yaml`
  - [ ] `subclasses/rogue/thief.yaml`
  - [ ] `species/human.yaml`
  - [ ] `backgrounds/soldier.yaml`, `acolyte.yaml`, `sage.yaml`, `charlatan.yaml`
  - [ ] `feats/origin/tough.yaml`, `alert.yaml`, `healer.yaml`, `magic_initiate_cleric.yaml`
  - [ ] Minimal spells used by standard party (see note below)
  - [ ] Minimal magic items (+1 weapon, +1 armor, Cloak of Protection)
- [ ] Unit tests in `tests/unit/registry/`
- [ ] Integration tests in `tests/integration/test_character_build_end_to_end.py`

### Note on minimal spell content

At M2, author the spells the standard party actually uses at the levels tested. Full spell coverage comes later. Required subset:

- Cleric: Bless, Cure Wounds, Healing Word, Spiritual Weapon, Prayer of Healing, Spirit Guardians, Revivify, Death Ward, Mass Cure Wounds, Heal
- Wizard: Fire Bolt, Shield, Mage Armor, Magic Missile, Misty Step, Fireball, Counterspell, Wall of Fire, Greater Invisibility, Cone of Cold, Chain Lightning, Wall of Force, Meteor Swarm, Wish
- Rogue: None (no spellcasting at this level for Thief)
- Fighter: None (no spellcasting for Battle Master)

### Verification

```bash
# Unit tests pass
pytest tests/unit/registry/ -v

# Integration tests pass
pytest tests/integration/test_character_build_end_to_end.py -v

# Content validates
python scripts/validate_content.py

# Standard party builds at all key levels
python -c "
from balance_framework.registry.loader import load_content_directory
from balance_framework.registry.registry import ContentRegistry
from balance_framework.registry.character_builder import build_character, CharacterBuild

registry = ContentRegistry(load_content_directory('content/'))

# Garrick at level 5
build = CharacterBuild(
    species_id='human', class_id='fighter', subclass_id='battle_master',
    background_id='soldier', level=5,
    ability_scores={'STR': 17, 'DEX': 14, 'CON': 15, 'INT': 10, 'WIS': 13, 'CHA': 8},
    # ... etc
)
garrick = build_character(build, registry)
print(f'Garrick L5: HP={garrick.hp_max}, AC={garrick.ac}, Proficiency={garrick.proficiency_bonus}')
assert garrick.hp_max > 40 and garrick.hp_max < 60
"
```

### Test coverage requirements

- [ ] Loader handles valid directory (happy path)
- [ ] Loader reports clear error for invalid YAML
- [ ] Registry raises `ReferenceError` for unknown IDs
- [ ] Resolver catches broken cross-references
- [ ] Character builder applies features at correct levels
- [ ] Character builder computes HP correctly (hit die + CON mod + feat bonuses)
- [ ] Character builder computes AC correctly (armor + shield + DEX + feats)
- [ ] All four standard party members build at levels 1, 5, 10, 15, 20

### Manual verification against documentation

Compare built characters to their documented sheets in `docs/party_sheets/`:

- [ ] Garrick at level 5: HP, AC, attack bonuses match `01_Garrick_BattleMaster_Fighter_v0.2.md`
- [ ] Elowyn at level 5: HP, AC, spell save DC match `02_Elowyn_Life_Cleric_v0.2.md`
- [ ] Varian at level 5: HP, AC, spell save DC match `03_Varian_Evocation_Wizard_v0.2.md`
- [ ] Mira at level 5: HP, AC, Sneak Attack dice match `04_Mira_Thief_Rogue_v0.2.md`

### Exit gate

- [ ] All four standard party characters build correctly at levels 1, 5, 10, 15, 20
- [ ] Built character stats match documented sheets within 1 HP variance (for average rolls)
- [ ] No test failures
- [ ] Content validation passes for all authored files

---

## M3: Engine Core

### Deliverables

- [ ] `src/balance_framework/engine/` package complete with:
  - [ ] `scenario.py`: `ScenarioState`, `CombatantState` dataclasses
  - [ ] `dice.py`: deterministic dice rolling
  - [ ] `grid.py`: basic positioning (5-ft grid or abstract distance)
  - [ ] `resolver.py`: main combat loop
- [ ] `src/balance_framework/engine/combat/` submodules complete:
  - [ ] `initiative.py`: initiative rolling with tie-breaking
  - [ ] `turns.py`: turn/round management
  - [ ] `actions.py`: action declaration and resolution
  - [ ] `attacks.py`: full attack roll resolution
  - [ ] `saves.py`: saving throw resolution
  - [ ] `damage.py`: damage application with resistance/vulnerability/immunity
  - [ ] `conditions.py`: all 5e conditions
  - [ ] `concentration.py`: concentration tracking
  - [ ] `resources.py`: resource pool management
- [ ] Unit tests for every combat submodule
- [ ] Integration test: single combat round with deterministic outcome

### Verification

```bash
# All engine unit tests pass
pytest tests/unit/engine/ -v

# Integration test: single round combat
pytest tests/integration/test_single_combat_round.py -v

# Determinism: same seed produces same outcome
pytest tests/integration/test_determinism.py -v
```

### Test coverage requirements

Per submodule:

- [ ] **attacks.py**: hit, miss, crit, advantage, disadvantage, advantage+disadvantage, expanded crit, nat 20/1
- [ ] **saves.py**: success, failure, advantage, disadvantage, legendary resistance, reroll (Indomitable)
- [ ] **damage.py**: flat damage, dice damage, resistance (half), vulnerability (double), immunity (zero), temp HP ordering
- [ ] **conditions.py**: each condition applies correctly, conditions with save-to-end, conditions with time limits, condition immunity
- [ ] **concentration.py**: DC calculation, success, failure, War Caster advantage, incapacitation breaks concentration
- [ ] **resources.py**: spend, recover on short rest, recover on long rest, partial refresh, pool cap

### Exit gate

- [ ] All engine unit tests pass
- [ ] Determinism test passes: running the same scenario with the same seed produces identical results across 10 runs
- [ ] Integration test (single round combat) passes with multiple seeds
- [ ] Engine throws clear errors (not `KeyError` or `AttributeError`) for malformed scenarios
- [ ] Test coverage for `engine/` module is at least 85%

---

## M4: Behavior AI

### Deliverables

- [ ] `src/balance_framework/ai/enumeration.py` lists legal actions for a combatant
- [ ] `src/balance_framework/ai/scorer.py` scores actions with utility values
- [ ] `src/balance_framework/ai/profiles.py` defines AI profiles (COMPETENT, AGGRESSIVE, CONSERVATIVE)
- [ ] `src/balance_framework/ai/heuristics/` contains:
  - [ ] `martial.py` (Fighter, Barbarian, Paladin, Ranger, Monk)
  - [ ] `caster.py` (Wizard, Sorcerer, Warlock)
  - [ ] `healer.py` (Cleric, Druid, Bard)
  - [ ] `support.py` (Rogue)
- [ ] `src/balance_framework/ai/monster.py` handles monster behavior by INT tier
- [ ] Unit tests for enumeration, scoring, each heuristic module
- [ ] Integration test: standard party vs orc with expected party victory

### Verification

```bash
pytest tests/unit/ai/ -v
pytest tests/integration/test_party_decisions.py -v
pytest tests/integration/test_monster_behavior.py -v
```

### Behavioral verification

Run the standard party vs 1 orc at level 5, 100 simulations. Check that the AI makes reasonable decisions:

- [ ] Garrick prioritizes melee attacks with weapon mastery
- [ ] Elowyn casts Bless at start of combat, heals allies when bloodied
- [ ] Varian casts damage spells at appropriate ranges, Counterspells enemy casters
- [ ] Mira uses Sneak Attack on priority targets, Steady Aim when alone
- [ ] Orc (low INT) attacks nearest party member
- [ ] No character makes obviously terrible decisions (e.g., wizard melee-attacking at low HP)

### Exit gate

- [ ] All AI unit tests pass
- [ ] Integration tests show competent decision-making
- [ ] AI is deterministic: same scenario + same seed produces same decisions
- [ ] Party vs 1 orc at level 5 wins 90%+ of the time over 100 runs (if not, AI is buggy)

---

## M5: Test Runner and Sanity Checks

### Deliverables

- [ ] `src/balance_framework/runner/orchestrator.py`
- [ ] `src/balance_framework/runner/seeding.py`
- [ ] `src/balance_framework/runner/collector.py`
- [ ] Sanity check validation suite in `tests/validation/`:
  - [ ] `test_encounter_difficulty.py`
  - [ ] `test_class_dpr.py`
  - [ ] `test_wotc_sanity.py` (can be stubbed until M9)

### Verification

```bash
# Runner tests pass
pytest tests/unit/runner/ -v

# Sanity checks pass
pytest tests/validation/ -v --timeout=1800
```

### Sanity check benchmarks

These are the specific expected ranges. If engine results fall outside these ranges, investigate before proceeding.

**Encounter difficulty:**

- [ ] Level 5 party (4 members, standard sheets) vs 4 orcs: **win rate 70-90%**
- [ ] Level 5 party vs 1 Ogre: **win rate 70-90%**
- [ ] Level 10 party vs 1 Young Red Dragon: **win rate 30-60%**
- [ ] Level 10 party vs 1 CR 10 monster: **win rate 40-70%**
- [ ] Level 1 party vs 1 orc: **win rate 50-80%** (orc is Hard encounter for level 1)

**Class DPR (damage per round) at level 5:**

- [ ] Fighter (Battle Master): 15-25 DPR against AC 15
- [ ] Wizard (Evoker) with spells: 15-30 DPR against AC 15 (averaged, including cantrip turns)
- [ ] Rogue (Thief) with Sneak Attack: 10-20 DPR against AC 15
- [ ] Cleric (Life): 8-15 DPR (lower because focused on support)

**Duration bounds:**

- [ ] No encounter exceeds 20 rounds
- [ ] Average encounter completes in 3-7 rounds
- [ ] No infinite loops

### Exit gate

- [ ] All sanity checks pass within specified ranges
- [ ] Running the full validation suite takes less than 30 minutes
- [ ] Determinism verified: same seed → same outcome
- [ ] No encounter hangs or exceeds round limit

---

## M6: Subclass Test Harness

### Deliverables

- [ ] `src/balance_framework/harnesses/base.py` with abstract base class
- [ ] `src/balance_framework/harnesses/subclass.py` with full harness implementation
- [ ] `src/balance_framework/harnesses/metrics.py` with participation/impact tier calculation
- [ ] Scenario generation: combat encounters at varied difficulty, solo endurance, non-combat pillars
- [ ] Metric collection: win rate, damage contribution, participation tier, impact tier, conditional and unconditional metrics
- [ ] Raw result output in JSON
- [ ] Integration test against Champion Fighter

### Verification

```bash
pytest tests/integration/test_subclass_harness.py -v

# Manual run
python -m balance_framework harnesses.subclass \
  --subclass champion \
  --levels 1,5,10,15,20 \
  --runs 100 \
  --output /tmp/champion_result.json

# Inspect output
cat /tmp/champion_result.json
```

### Output validation

The harness result JSON should contain:

- [ ] Subclass ID and metadata
- [ ] Per-level results for each tested level
- [ ] Per-encounter-type results (combat, solo, social, exploration, investigation)
- [ ] Participation tier distribution per scenario type
- [ ] Impact tier distribution per scenario type
- [ ] Raw metrics (damage totals, healing totals, turn counts)

### Exit gate

- [ ] Champion harness result is produced without errors
- [ ] Output JSON conforms to documented schema
- [ ] Results are reproducible with fixed seeds
- [ ] Participation tiers sum to 100% per scenario type
- [ ] Harness handles edge cases (character drops to 0 HP, encounter ends early)

---

## M7: Reporting Layer

### Deliverables

- [ ] `src/balance_framework/reporting/test_report.py` generates markdown reports
- [ ] `src/balance_framework/reporting/baseline.py` generates baseline JSON documents
- [ ] `src/balance_framework/reporting/visualizations.py` creates charts (histograms, distributions)
- [ ] `src/balance_framework/reporting/formats/markdown.py` handles markdown templating
- [ ] Sample report generated from Champion harness result

### Verification

```bash
pytest tests/integration/test_report_generation.py -v

# Generate sample report
python -m balance_framework reporting.test_report \
  --harness-result /tmp/champion_result.json \
  --output /tmp/champion_report.md

# Visually inspect
cat /tmp/champion_report.md
```

### Report quality check

Manually review the Champion report:

- [ ] Summary section gives a clear verdict (within expected range, outlier, etc.)
- [ ] Per-level details show how the subclass scales
- [ ] Participation and impact tiers are broken down clearly
- [ ] Visualizations render correctly
- [ ] Markdown formatting is clean (no broken tables, escaped characters)
- [ ] Report is usable by a DM without domain expertise

### Exit gate

- [ ] Champion report generates without errors
- [ ] Report is readable and coherent
- [ ] Baseline JSON document is structurally valid
- [ ] Visualizations are present and meaningful

---

## M8: CLI

### Deliverables

- [ ] `src/balance_framework/cli/main.py` with Click-based CLI
- [ ] `balance-framework test subclass` command
- [ ] `balance-framework validate` command
- [ ] `balance-framework generate-baseline` command (may be partial)
- [ ] `balance-framework build-character` debug command
- [ ] Entry point configured in `pyproject.toml`
- [ ] CLI help text is clear

### Verification

```bash
# After pip install -e .
balance-framework --help
balance-framework test --help
balance-framework test subclass --help
balance-framework validate --help
balance-framework generate-baseline --help

# Actually run a test
balance-framework test subclass \
  --file content/subclasses/fighter/champion.yaml \
  --runs 100 \
  --output /tmp/champion_via_cli.md
```

### Exit gate

- [ ] `balance-framework --help` lists all commands
- [ ] Each command has helpful descriptions
- [ ] CLI returns non-zero exit codes for errors
- [ ] CLI produces output files as documented
- [ ] Running `balance-framework test subclass --file docs/handoff/champion_fighter_example.yaml` produces a valid report

---

## M9: First Baseline Generation (Partial)

### Deliverables

- [ ] All 16 Tier A subclass YAMLs authored and validated:
  - [ ] Fighter: Champion, Battle Master, Eldritch Knight
  - [ ] Cleric: Life, Light, War, Trickery
  - [ ] Wizard: Evoker, Abjurer, Diviner, Illusionist
  - [ ] Rogue: Thief, Assassin, Arcane Trickster, Soulknife
  - [ ] Barbarian: Berserker, World Tree, Zealot
  - [ ] Bard: Lore
- [ ] `baselines/v0.9/subclasses/` contains JSON files for all Tier A subclasses
- [ ] Metadata file documenting baseline version, engine version, rules version
- [ ] At least one homebrew subclass tested against this partial baseline

### Verification

```bash
# Validate all authored content
python scripts/validate_content.py

# Generate partial baseline
balance-framework generate-baseline \
  --rules 2024 \
  --tier A \
  --output baselines/v0.9/

# Verify output
ls baselines/v0.9/subclasses/
cat baselines/v0.9/metadata.json
```

### Content validation

- [ ] All 16 Tier A subclass YAMLs validate without errors
- [ ] All YAMLs reference existing classes and spells
- [ ] Behavior hints are non-empty for each
- [ ] All features from PHB are present

### Baseline quality check

Review the baselines for sanity:

- [ ] No subclass shows impossible distributions (e.g., 100% high-impact at level 1)
- [ ] Distributions are continuous, not bimodal (unless the subclass has genuinely bimodal mechanics)
- [ ] Participation tiers sum correctly
- [ ] Baseline documents contain all expected fields per the schema

### Exit gate

- [ ] All 16 Tier A subclasses authored, validated, and baseline-generated
- [ ] Baseline generation completes without errors
- [ ] Homebrew test reports can be generated against the partial baseline
- [ ] Framework is usable for its primary purpose (testing homebrew subclasses)

---

## M10: Full Baseline (Stretch Goal for Phase 2)

### Deliverables

- [ ] All 61 subclass YAMLs authored (Tier A + B + C)
- [ ] Monster YAMLs for at least 50 monsters across CR range
- [ ] `baselines/v1.0/` contains full baseline
- [ ] Monster harness functional (stretch)
- [ ] Magic item harness functional (stretch)

### Verification

```bash
# Full baseline generation
balance-framework generate-baseline \
  --rules 2024 \
  --tier all \
  --output baselines/v1.0/

# This takes many hours. Plan accordingly.
```

### Exit gate

- [ ] All 61 WotC subclasses covered by baseline
- [ ] Baseline v1.0 is published (committed to repository)
- [ ] Framework Phase 2 is formally complete

---

## Phase 2 Complete

When M0-M9 are all complete (M10 is stretch):

- [ ] Repository is production-quality
- [ ] CI passes on every commit to main
- [ ] Test coverage exceeds 85%
- [ ] Documentation is current
- [ ] Baseline v0.9 (partial) or v1.0 (full) is published
- [ ] Framework is ready for Phase 3: homebrew balancing work

At this point, update `README.md` status tracker and announce Phase 2 completion.

---

## Revision History

- **v0.1 (current):** Initial milestone checklists covering M0-M10 with detailed verification criteria.
