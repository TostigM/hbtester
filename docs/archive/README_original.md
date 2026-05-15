# D&D Homebrew Balance Framework

A simulation-based balance testing framework for D&D 5.5e (2024 rules) homebrew content.

## What this project does

The framework evaluates D&D content for mechanical balance by:

1. Running each piece of content through a simulated test battery
2. Comparing results against a pre-computed baseline of WotC-published content
3. Generating reports showing how the tested content compares to the baseline distribution

The system supports seven content categories: subclasses, monsters, magic items, backgrounds, species, spells, and feats (including Epic Boons).

## Current status

**Phase 1 (Design): Complete.** All design documentation, content schemas, character templates, and architecture specifications are finalized in the `docs/` directory.

**Phase 2 (Implementation): In progress.** The Python library and CLI tool are being built. Current milestone: [update as work progresses]

**Phase 3 (Balance homebrew): Not started.**

**Phase 4 (Productize as web app): Not started.**

## Repository structure

```
balance-framework/
├── README.md                    # This file
├── LICENSE                      # License terms
├── pyproject.toml               # Python project config, dependencies
├── .gitignore                   # Git exclusions
├── .pre-commit-config.yaml      # Pre-commit hooks
│
├── docs/                        # All design documentation (Phase 1 output)
│   ├── architecture_spec.md
│   ├── party_sheets/            # Main party and supplementary templates
│   ├── schemas/                 # Content schema definitions
│   ├── authoring_guides/        # How to author content
│   └── handoff/                 # This handoff package
│
├── src/balance_framework/       # The Python library
│   ├── __init__.py
│   ├── schema/                  # Schema validation
│   ├── registry/                # Content registry
│   ├── engine/                  # Simulation engine
│   ├── ai/                      # Behavior AI
│   ├── harnesses/               # Test harnesses
│   ├── runner/                  # Test orchestration
│   ├── reporting/               # Report generation
│   └── cli/                     # Command-line interface
│
├── content/                     # YAML content files
│   ├── classes/
│   ├── subclasses/
│   ├── species/
│   ├── backgrounds/
│   ├── spells/
│   ├── magic_items/
│   ├── monsters/
│   └── feats/
│
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests per module
│   ├── integration/             # Multi-component tests
│   ├── validation/              # Engine validation suite (rules correctness)
│   └── fixtures/                # Test data
│
├── baselines/                   # Generated baseline reference documents
│   └── v1.0/                    # First baseline release (not yet generated)
│
└── scripts/                     # Utility scripts (baseline generation, etc.)
```

## Quick start

### Prerequisites

- Python 3.11 or later
- Git
- A terminal with reasonable performance (simulations are CPU-bound)

### Setup

```bash
# Clone the repository
git clone <repository-url> balance-framework
cd balance-framework

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify setup
pytest tests/unit
```

### Running your first simulation

Once Phase 2 is sufficiently advanced (post-Milestone 4; see `docs/handoff/MILESTONE_CHECKLISTS.md`):

```bash
# Run a single subclass test against the baseline
balance-framework test subclass \
  --file my_homebrew_subclass.yaml \
  --runs 1000 \
  --output report.md

# Generate the WotC baseline (one-time, takes 24-72 hours)
balance-framework generate-baseline \
  --rules 2024 \
  --output baselines/v1.0/

# Run engine validation suite (quick sanity check)
balance-framework validate
```

## Navigating the documentation

**If you want to understand the design:**
- Start with `docs/architecture_spec.md` (the master design doc)
- Then read the character sheets in `docs/party_sheets/` to understand the standard party
- Then read the schemas in `docs/schemas/` for content structure

**If you are implementing Phase 2:**
- Start with `docs/handoff/PHASE_2_PLAN.md`
- Reference `docs/handoff/PROMPT_LIBRARY.md` for Claude Code prompts
- Use `docs/handoff/MILESTONE_CHECKLISTS.md` to verify progress
- Follow `docs/handoff/GIT_WORKFLOW.md` for repo hygiene
- Understand the layout from `docs/handoff/PROJECT_STRUCTURE.md`

**If you are authoring content:**
- Read the schema document for the content type you are authoring
- Read the relevant authoring guide (e.g., `docs/authoring_guides/subclass_authoring_guide.md`)
- Follow the Claude Code prompt template in the authoring guide

## Contributing

This project is in active development. Before contributing:

1. Read the architecture spec to understand the design
2. Read `GIT_WORKFLOW.md` for commit and PR conventions
3. Run the full test suite locally before opening a PR
4. Ensure any new content files pass schema validation

## Design philosophy

The framework prioritizes:

- **Rigor over speed.** Simulation bugs invalidate downstream results. Slow and correct beats fast and wrong.
- **Determinism.** Every run is reproducible from its random seed.
- **Honest categorization.** Reports never silently filter out "bad" runs. Users see participation and impact breakdowns.
- **Library-first architecture.** The core engine is a standalone Python library. CLI, web service, and hybrid deployments are layers above it.
- **Schema-enforced content.** All content is validated at the boundary. The engine never operates on unvalidated data.

For the full philosophy, see `docs/architecture_spec.md` §2.

## License

[To be determined. Current recommendation: MIT or Apache 2.0 for permissive open-source.]

## Acknowledgments

Built on the D&D 5.5e (2024) rules published by Wizards of the Coast. This framework is an independent project and is not affiliated with or endorsed by Wizards of the Coast. All rules content remains WotC's intellectual property; this project contains only mechanical abstractions and homebrew-balancing tools.

---

## Status Tracker

_(Update this section as Phase 2 progresses.)_

### Current milestone

**[M0] Repository Setup** — Initial scaffolding, tooling, pre-commit hooks, CI configuration.

### Milestones completed

None yet.

### Next milestone

**[M1] Schema Layer** — Schema validation for all seven content types. See `docs/handoff/MILESTONE_CHECKLISTS.md`.
