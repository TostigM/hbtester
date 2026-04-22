# Project Structure

This document defines the repository layout for the D&D Homebrew Balance Framework. Every file and folder has a purpose; this document explains what goes where and why.

---

## Top-level layout

```
balance-framework/
├── README.md                    # Entry point, overview, quick-start
├── LICENSE                      # License terms
├── pyproject.toml               # Python project config
├── .gitignore                   # Git exclusions
├── .pre-commit-config.yaml      # Code quality hooks
├── .github/                     # CI/CD config
│   └── workflows/
│       └── ci.yml
│
├── docs/                        # All documentation
├── src/balance_framework/       # Python source code
├── content/                     # YAML content data
├── tests/                       # Test suite
├── baselines/                   # Generated baseline reference documents
└── scripts/                     # Utility scripts
```

**Rationale for this layout:** Python's `src/` layout (rather than flat layout) prevents import ambiguity and forces proper package installation. Content, tests, and baselines are sibling directories to `src/` because they are not Python packages; they are data consumed by the library.

---

## `src/balance_framework/` — The Python library

```
src/balance_framework/
├── __init__.py                  # Package version, top-level exports
├── __main__.py                  # Enables `python -m balance_framework`
│
├── schema/                      # Layer 1: Schema validation
│   ├── __init__.py
│   ├── validators.py            # Per-content-type validators
│   ├── types.py                 # Pydantic models for content types
│   ├── exceptions.py            # Validation error classes
│   └── vocabulary.py            # Allowed values for feature_type, etc.
│
├── registry/                    # Layer 2: Content registry
│   ├── __init__.py
│   ├── loader.py                # YAML file loading
│   ├── registry.py              # ContentRegistry class
│   ├── resolver.py              # Cross-reference resolution
│   └── character_builder.py     # Build characters from content
│
├── engine/                      # Layer 3: Simulation engine
│   ├── __init__.py
│   ├── scenario.py              # Scenario state dataclass
│   ├── combatant.py             # Combatant state dataclass
│   ├── combat/                  # Combat resolution
│   │   ├── __init__.py
│   │   ├── initiative.py
│   │   ├── turns.py
│   │   ├── actions.py
│   │   ├── attacks.py
│   │   ├── saves.py
│   │   ├── damage.py
│   │   ├── conditions.py
│   │   ├── concentration.py
│   │   └── resources.py
│   ├── noncombat/               # Non-combat pillars
│   │   ├── __init__.py
│   │   ├── social.py
│   │   ├── exploration.py
│   │   └── investigation.py
│   ├── dice.py                  # Deterministic dice rolling
│   ├── grid.py                  # Battlefield grid, positioning
│   └── resolver.py              # Main engine entry point
│
├── ai/                          # Layer 4: Behavior AI
│   ├── __init__.py
│   ├── decision.py              # Main decision-making loop
│   ├── scorer.py                # Action scoring
│   ├── profiles.py              # AI profiles (competent, aggressive, conservative)
│   ├── heuristics/              # Class-specific heuristics
│   │   ├── __init__.py
│   │   ├── martial.py
│   │   ├── caster.py
│   │   ├── healer.py
│   │   └── support.py
│   └── monster.py               # Monster behavior logic
│
├── runner/                      # Layer 5: Test runner
│   ├── __init__.py
│   ├── orchestrator.py          # Multi-run orchestration
│   ├── seeding.py               # Random seed management
│   └── collector.py             # Result aggregation
│
├── harnesses/                   # Layer 6: Test harnesses
│   ├── __init__.py
│   ├── base.py                  # Abstract harness base class
│   ├── subclass.py
│   ├── monster.py
│   ├── magic_item.py
│   ├── background.py
│   ├── species.py
│   ├── spell.py
│   └── feat.py
│
├── reporting/                   # Layer 7: Reporting
│   ├── __init__.py
│   ├── baseline.py              # Baseline reference doc generation
│   ├── test_report.py           # Homebrew test report generation
│   ├── formats/
│   │   ├── markdown.py
│   │   ├── pdf.py
│   │   ├── json.py
│   │   └── csv.py
│   └── visualizations.py        # Charts and graphs
│
├── logging/                     # Structured logging
│   ├── __init__.py
│   ├── event_log.py             # CSV event logging
│   └── decision_log.py          # AI decision traces
│
└── cli/                         # Command-line interface
    ├── __init__.py
    ├── main.py                  # Entry point
    ├── test_commands.py         # `balance-framework test ...`
    ├── baseline_commands.py     # `balance-framework generate-baseline ...`
    └── validate_commands.py     # `balance-framework validate`
```

### Layer structure rationale

The seven layers from the architecture spec map directly to subpackages. Dependencies flow downward only:

- `reporting` depends on `harnesses`, `runner`
- `harnesses` depend on `runner`, `engine`, `ai`
- `runner` depends on `engine`, `ai`
- `ai` depends on `engine`
- `engine` depends on `registry`
- `registry` depends on `schema`
- `schema` has no internal dependencies

Each subpackage has `__init__.py` that exposes the public API. Internal implementation details are not exported.

### Combat subdirectory breakdown

The `engine/combat/` subdirectory is detailed because combat resolution is the most complex engine component:

- `initiative.py`: Initiative rolling, turn order, surprise rules
- `turns.py`: Turn and round lifecycle, start-of-turn effects
- `actions.py`: Action declaration, validation, resolution pipeline
- `attacks.py`: Attack roll mechanics (d20 + mods vs AC)
- `saves.py`: Saving throw mechanics, DC calculation
- `damage.py`: Damage rolls, modifiers, resistance/vulnerability/immunity
- `conditions.py`: All 5e conditions (blinded, charmed, etc.) and effects
- `concentration.py`: Concentration tracking and break rules
- `resources.py`: Resource pool management, rest mechanics

Each file handles one aspect of combat. Files over 300 lines get split further.

---

## `content/` — YAML content data

```
content/
├── classes/
│   ├── artificer.yaml
│   ├── barbarian.yaml
│   ├── bard.yaml
│   ├── cleric.yaml
│   ├── druid.yaml
│   ├── fighter.yaml
│   ├── monk.yaml
│   ├── paladin.yaml
│   ├── ranger.yaml
│   ├── rogue.yaml
│   ├── sorcerer.yaml
│   ├── warlock.yaml
│   └── wizard.yaml
│
├── subclasses/
│   ├── artificer/
│   │   ├── alchemist.yaml
│   │   ├── armorer.yaml
│   │   ├── artillerist.yaml
│   │   ├── battle_smith.yaml
│   │   └── cartographer.yaml
│   ├── barbarian/
│   │   ├── berserker.yaml
│   │   ├── wild_heart.yaml
│   │   ├── world_tree.yaml
│   │   └── zealot.yaml
│   ├── bard/
│   │   ├── dance.yaml
│   │   ├── glamour.yaml
│   │   ├── lore.yaml
│   │   └── valor.yaml
│   └── [... one directory per class, with subclass YAML files inside ...]
│
├── species/
│   ├── dragonborn.yaml
│   ├── dwarf.yaml
│   ├── elf.yaml
│   ├── gnome.yaml
│   ├── goliath.yaml
│   ├── halfling.yaml
│   ├── human.yaml
│   ├── orc.yaml
│   └── tiefling.yaml
│
├── backgrounds/
│   ├── acolyte.yaml
│   ├── artisan.yaml
│   ├── charlatan.yaml
│   ├── criminal.yaml
│   ├── entertainer.yaml
│   ├── farmer.yaml
│   ├── guard.yaml
│   ├── guide.yaml
│   ├── hermit.yaml
│   ├── merchant.yaml
│   ├── noble.yaml
│   ├── sage.yaml
│   ├── sailor.yaml
│   ├── scribe.yaml
│   ├── soldier.yaml
│   └── wayfarer.yaml
│
├── spells/
│   ├── cantrips/               # Cantrips in their own subdirectory for volume
│   │   ├── fire_bolt.yaml
│   │   └── [... ~30 cantrips ...]
│   ├── level_1/
│   │   ├── cure_wounds.yaml
│   │   └── [... ~40 1st-level spells ...]
│   ├── level_2/
│   └── [... through level_9 ...]
│
├── magic_items/
│   ├── weapons/
│   │   ├── plus_one_longsword.yaml
│   │   ├── flame_tongue.yaml
│   │   └── [...]
│   ├── armor/
│   ├── wondrous/
│   └── consumables/
│
├── monsters/
│   ├── cr_0/                   # Organized by CR for ease of access
│   │   └── [...]
│   ├── cr_1_4/
│   ├── cr_1_2/
│   ├── cr_1/
│   ├── cr_2/
│   └── [... through cr_30 ...]
│
└── feats/
    ├── origin/
    │   ├── alert.yaml
    │   ├── lucky.yaml
    │   └── [...]
    ├── general/
    │   ├── resilient.yaml
    │   ├── war_caster.yaml
    │   └── [...]
    ├── fighting_styles/
    └── epic_boons/
        ├── boon_of_fate.yaml
        └── [...]
```

### Content directory conventions

- **Filenames are snake_case.** `great_weapon_master.yaml`, not `GreatWeaponMaster.yaml` or `great-weapon-master.yaml`.
- **IDs in YAML match filenames.** `alchemist.yaml` contains `id: "alchemist"`.
- **Directories separate by category, not by source.** A 2024 PHB subclass and a Forge of the Artificer subclass go in the same `subclasses/artificer/` directory. The `source` field in each YAML distinguishes them.
- **One content item per file.** Never put multiple subclasses or spells in one YAML file.
- **Non-PHB content uses source field.** `source: "Forge_of_the_Artificer_2025"` or `source: "Heroes_of_Faerun_2025"`.

### Homebrew content

Homebrew content lives outside this directory by default. When users submit homebrew for testing, it is loaded from a user-specified path (typically `./my_homebrew/` or a path provided via CLI flag). Homebrew never mixes with the baseline content repository.

For development and testing, a `content/homebrew_examples/` directory may hold example homebrew files for regression testing.

---

## `docs/` — Documentation

```
docs/
├── architecture_spec.md         # Master design document
│
├── party_sheets/                # Character templates
│   ├── 00_Party_Summary.md
│   ├── 01_Garrick_BattleMaster_Fighter.md
│   ├── 02_Elowyn_Life_Cleric.md
│   ├── 03_Varian_Evocation_Wizard.md
│   ├── 04_Mira_Thief_Rogue.md
│   └── supplementary/           # Class templates for non-party subclass tests
│       ├── 00_Supplementary_Templates_Index.md
│       └── [... 05_ through 13_ ...]
│
├── schemas/                     # Schema documentation
│   ├── class_schema.md
│   ├── subclass_schema.md
│   ├── species_schema.md
│   ├── background_schema.md
│   ├── spell_schema.md
│   ├── magic_item_schema.md
│   ├── monster_schema.md
│   └── feat_and_epic_boon_schema.md
│
├── authoring_guides/            # How to author content
│   └── subclass_authoring_guide.md
│
└── handoff/                     # This handoff package
    ├── README.md                # (Duplicate of top-level README? See note below)
    ├── PHASE_2_PLAN.md
    ├── PROMPT_LIBRARY.md
    ├── MILESTONE_CHECKLISTS.md
    ├── GIT_WORKFLOW.md
    └── PROJECT_STRUCTURE.md     # This file
```

**Note on README duplication:** The top-level `README.md` is the canonical entry point. The handoff directory does not need its own README; navigation happens from the top-level.

---

## `tests/` — Test suite

```
tests/
├── conftest.py                  # Pytest configuration, shared fixtures
│
├── unit/                        # Fast, isolated per-module tests
│   ├── schema/
│   │   ├── test_validators.py
│   │   └── test_vocabulary.py
│   ├── registry/
│   │   ├── test_loader.py
│   │   └── test_character_builder.py
│   ├── engine/
│   │   ├── combat/
│   │   │   ├── test_attacks.py
│   │   │   ├── test_saves.py
│   │   │   ├── test_damage.py
│   │   │   └── test_concentration.py
│   │   └── test_dice.py
│   ├── ai/
│   │   └── test_scorer.py
│   └── [...]
│
├── integration/                 # Multi-component tests
│   ├── test_character_build_end_to_end.py
│   ├── test_single_combat_round.py
│   ├── test_full_encounter.py
│   └── test_report_generation.py
│
├── validation/                  # Engine correctness validation
│   ├── test_combat_rules.py     # Specific 5e rules applied correctly
│   ├── test_encounter_difficulty.py  # DMG difficulty estimates match
│   ├── test_class_dpr.py        # Per-class DPR in expected ranges
│   └── test_wotc_sanity.py      # WotC content clusters correctly
│
└── fixtures/                    # Test data
    ├── sample_characters/
    ├── sample_scenarios/
    └── sample_content/          # Minimal content files for tests
```

### Test categorization

- **Unit tests** run in under 1 second each. They test isolated functions or classes.
- **Integration tests** may take seconds. They test multi-component interactions.
- **Validation tests** run the actual simulation engine against known-correct outcomes. They may take minutes for comprehensive coverage.

Tests are organized to mirror the `src/` structure. A function in `src/balance_framework/engine/combat/attacks.py` has its unit tests in `tests/unit/engine/combat/test_attacks.py`.

---

## `baselines/` — Generated baseline reference documents

```
baselines/
├── README.md                    # Explains baseline versioning
├── v1.0/                        # First baseline release
│   ├── metadata.json            # Version, engine version, rules version
│   ├── subclasses/
│   │   ├── champion.json
│   │   ├── battle_master.json
│   │   └── [...]
│   ├── monsters/
│   │   └── [...]
│   ├── magic_items/
│   └── [...]
└── v1.1/                        # Future incremental updates
    └── [...]
```

Baseline reference documents are JSON (not YAML) because they are machine-generated and machine-consumed. Each baseline version is immutable once published.

---

## `scripts/` — Utility scripts

```
scripts/
├── generate_baseline.py         # Full baseline generation pipeline
├── validate_content.py          # Batch-validate all YAML content
├── extract_stats.py             # Statistical summaries of content
└── migration/                   # Version migration scripts
    └── v1_to_v2.py
```

These are standalone scripts (not part of the library's public API). They import from `balance_framework` but provide operational tooling.

---

## `pyproject.toml` contents

Planned dependencies:

**Core:**
- `pydantic` for schema validation and typed data
- `pyyaml` for YAML parsing
- `click` or `typer` for CLI
- `numpy` for numerical work (dice rolls, statistics)

**Reporting and visualization:**
- `matplotlib` or `plotly` for charts
- `pandas` for tabular data handling
- `reportlab` or `weasyprint` for PDF generation

**Development:**
- `pytest` and `pytest-cov` for testing
- `ruff` for linting and formatting
- `mypy` for type checking
- `pre-commit` for git hooks

**Build:**
- `setuptools` with `setuptools-scm` for versioning

Example `pyproject.toml` skeleton will be created by the first Phase 2 prompt.

---

## Naming conventions summary

| Thing | Convention | Example |
|---|---|---|
| Python packages | `snake_case` | `balance_framework` |
| Python modules | `snake_case` | `character_builder.py` |
| Python classes | `PascalCase` | `ContentRegistry` |
| Python functions | `snake_case` | `roll_initiative` |
| Python constants | `UPPER_SNAKE_CASE` | `DEFAULT_ENCOUNTER_ROUNDS` |
| YAML file names | `snake_case.yaml` | `wild_heart.yaml` |
| YAML field names | `snake_case` | `unlock_level` |
| YAML IDs (in content) | `snake_case` | `id: "champion"` |
| Documentation files | `SCREAMING_SNAKE_CASE.md` for setup docs, `snake_case.md` for content | `PHASE_2_PLAN.md`, `subclass_schema.md` |

---

## Why this structure

**Separation of code from data.** `src/` contains only Python. `content/` contains only YAML. Changing a subclass's stats never requires a code change; adding a new feature type to the engine never requires a content change.

**Mirror-based testing.** Tests mirror the source directory structure, making it trivial to find the tests for any given module.

**Layered architecture enforced by directory layout.** The engine cannot accidentally import from reporting because they are in separate subpackages with explicit dependency order.

**Content authoring is independent of engine development.** While one developer builds the combat engine, another can author subclass YAML. The schema contract mediates between them.

**Baselines are first-class artifacts.** They live in version-controlled JSON files, not in a database. This makes them diffable, reviewable, and distributable without infrastructure.

**CLI is thin.** The CLI package only contains command-line parsing and dispatch. All logic lives in the library. This makes the library usable from Python scripts without CLI overhead.
