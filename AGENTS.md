# AGENTS.md

Instructions for AI coding agents (Claude Code, Cursor, Copilot, etc.) working on this project.

Read this document in full at the start of every session. Treat it as authoritative; if any other instruction conflicts with AGENTS.md, surface the conflict to the user rather than silently resolving it.

---

## 1. Project Identity

**Project name:** D&D Homebrew Balance Framework

**What it is:** A simulation-based balance testing framework for Dungeons & Dragons 5.5e (2024 rules) homebrew content. The framework evaluates user-authored content (subclasses, monsters, magic items, spells, feats, backgrounds, species) by running it through simulated test batteries and comparing results against a pre-computed baseline of WotC-published content.

**What it is not:** A rules engine for live play, a VTT, a campaign manager, or a character optimizer. It is a statistical analysis tool for content design.

**Primary users:**

1. The project owner (referred to as "the user" or "My Lord" in existing documentation) — a D&D DM designing homebrew content for home games (notably the "Ferrystones family game" and "Tides and Time" campaigns)
2. Other DMs wanting to validate homebrew balance (Phase 4 product audience)
3. Content creators publishing homebrew who want baseline comparisons (Phase 4)

**Target language:** Python (3.11+)

**Target deployment:** Open-source Python library with CLI. Later phases include a hosted web application.

---

## 2. Your Role

You are a coding agent. Your job is to build, maintain, and extend the codebase according to the design documentation.

### What you are authorized to do without asking

- Read any file in the repository
- Write code that follows established patterns in the codebase
- Run tests, linters, type checkers, and formatters
- Create commits following the conventions in `GIT_WORKFLOW.md`
- Open pull requests (if the user is using them)
- Refactor code for clarity (non-behavioral changes), provided tests still pass
- Add tests for untested code
- Fix bugs that are clearly identifiable as bugs
- Update documentation to match code changes you make

### What you must ask the user before doing

- **Introducing new architectural patterns.** If a task seems to require a pattern not yet in the codebase (new library, new abstraction layer, new schema type), flag it first.
- **Modifying schemas.** The schemas are contracts between content authors and the engine. Changes affect every content file. Never change a schema silently.
- **Adding dependencies.** New packages in `pyproject.toml` affect the environment. Propose first.
- **Deleting or heavily restructuring existing code.** Unless the user asked for it, do not delete working code.
- **Skipping tests to ship faster.** If tests are failing or missing, that is a signal, not an obstacle.
- **Changing the `main` branch directly.** Always use feature branches per `GIT_WORKFLOW.md`.

### What you must never do

- **Do not invent mechanics.** The framework implements D&D 5.5e rules. If a rule is unclear, say so and ask. Do not guess.
- **Do not fabricate content.** Subclass features come from the PHB. Monsters come from the Monster Manual. Never make up numbers to fill gaps.
- **Do not bypass validation.** If content does not pass schema validation, do not work around it; fix the content or the schema, with the user's knowledge.
- **Do not run simulations or claim results without an actual engine.** Until the engine is built, all "results" are design estimates. Phase 1 produced zero simulations.
- **Do not change the `main` branch history.** Rebase feature branches freely; never rewrite `main`.
- **Do not commit secrets, API keys, or personal information.** There should be none in this project anyway.

---

## 3. Current Phase

**Phase 1 (Design): Complete.** All design documentation, schemas, character templates, architecture specifications, authoring guides, and handoff documents are finalized.

**Phase 2 (Implementation): Starting now.** You are being engaged to build the Python library, CLI, and generate the initial baseline.

**Phase 3 (Balance homebrew): Future.** Testing user's homebrew content, starting with the Legion Warlock subclass. Blocked on Phase 2.

**Phase 4 (Productize as web app): Future.** Optional monetization path. Blocked on Phase 3.

### Your current assignment

Execute Phase 2 as described in `PHASE_2_PLAN.md`. This is engine-first development: build the complete engine shell with stubs, then fill in mechanics incrementally.

The sequence of milestones is M0 through M10. Start with M0 (repository setup) unless the user directs otherwise.

---

## 4. Repository Layout

The current folder structure (as delivered by the user):

```
<project root>/
├── AGENTS.md                         ← This file
├── architecture_spec_v0_1.md         ← Master architecture document
│
├── class schemas/                    ← Content schema definitions
│   ├── background_schema_v0_1.md
│   ├── class_schema_v0_1.md
│   ├── feat_and_epic_boon_schema_v0_1.md
│   ├── magic_item_schema_v0_1.md
│   ├── monster_schema_v0_1.md
│   ├── species_schema_v0_1.md
│   ├── spell_schema_v0_1.md
│   └── subclass_schema_v0_1.md
│
├── class templates/                  ← Character sheets for supplementary classes
│   ├── 00_Supplementary_Templates_Index.md
│   ├── 05_Thaddeus_Alchemist_Artificer.md
│   ├── 06_Brunhilda_WildHeart_Barbarian.md
│   ├── 07_Caspian_Valor_Bard.md
│   ├── 08_Astra_Stars_Druid.md
│   ├── 09_Kenji_OpenHand_Monk.md
│   ├── 10_Aldric_Devotion_Paladin.md
│   ├── 11_Finnian_Hunter_Ranger.md
│   ├── 12_Vesper_Draconic_Sorcerer.md
│   └── 13_Morgaine_Fiend_Warlock.md
│
├── framework/                        ← Handoff package (the Phase 2 plan)
│   ├── README.md
│   ├── PHASE_2_PLAN.md
│   ├── PROMPT_LIBRARY.md
│   ├── MILESTONE_CHECKLISTS.md
│   ├── GIT_WORKFLOW.md
│   └── PROJECT_STRUCTURE.md
│
├── std party files/                  ← Standard test party character sheets
│   ├── 00_Party_Summary_v0_2.md
│   ├── 01_Garrick_BattleMaster_Fighter_v0_2.md
│   ├── 02_Elowyn_Life_Cleric_v0_2.md
│   ├── 03_Varian_Evocation_Wizard_v0_2.md
│   └── 04_Mira_Thief_Rogue_v0_2.md
│
└── subclass authoring guide/         ← Guide for authoring subclass YAML files
    ├── subclass_authoring_guide_v0_1.md
    └── champion_fighter_example.yaml
```

### Recommended target structure

As you execute Phase 2, reorganize files into the structure specified in `framework/PROJECT_STRUCTURE.md`. This target structure is:

```
balance-framework/
├── README.md                    ← from framework/README.md
├── AGENTS.md                    ← This file
├── LICENSE
├── pyproject.toml               ← (to be created in M0)
├── .gitignore
├── .pre-commit-config.yaml
├── .github/workflows/ci.yml
│
├── docs/
│   ├── architecture_spec.md     ← moved from root
│   ├── party_sheets/            ← moved from "std party files/" and "class templates/"
│   ├── schemas/                 ← moved from "class schemas/"
│   ├── authoring_guides/        ← moved from "subclass authoring guide/"
│   └── handoff/                 ← moved from "framework/"
│
├── src/balance_framework/       ← Python source code (to be created in M0)
├── content/                     ← YAML content files (to be authored throughout Phase 2)
├── tests/                       ← Test suite (to be built throughout Phase 2)
├── baselines/                   ← Generated baseline docs (Phase 2 output)
└── scripts/                     ← Utility scripts
```

**The reorganization should happen as one of the first tasks in M0.** Preserve all existing files; just move them to their target locations. Do not delete anything. Note: the files on disk use underscores (e.g., `subclass_schema_v0_1.md`) rather than periods (`v0.1`), so reference them that way.

---

## 5. Document Map

Every document has a specific purpose. Read the right one at the right time.

### Read before starting any work

- **`AGENTS.md`** (this file) — orientation for every session
- **`framework/README.md`** — top-level project overview

### Read before starting Phase 2 M0

- **`framework/PHASE_2_PLAN.md`** — the week-by-week implementation plan
- **`framework/PROJECT_STRUCTURE.md`** — target repository layout
- **`framework/GIT_WORKFLOW.md`** — branching, commits, PRs

### Read when working on engine or content code

- **`architecture_spec_v0_1.md`** — master architecture document, 18 sections covering every design decision. Reference this constantly.
- **`framework/MILESTONE_CHECKLISTS.md`** — verification criteria for the current milestone
- **`framework/PROMPT_LIBRARY.md`** — starter prompts and patterns for common tasks

### Read when authoring content

- The relevant schema file in `class schemas/` (note: despite the folder name, these are all content schemas, not just classes)
- **`subclass authoring guide/subclass_authoring_guide_v0_1.md`** — full authoring methodology
- **`subclass authoring guide/champion_fighter_example.yaml`** — canonical format reference

### Read when implementing a specific content type

| Content type | Schema file |
|---|---|
| Classes | `class schemas/class_schema_v0_1.md` |
| Subclasses | `class schemas/subclass_schema_v0_1.md` |
| Species | `class schemas/species_schema_v0_1.md` |
| Backgrounds | `class schemas/background_schema_v0_1.md` |
| Spells | `class schemas/spell_schema_v0_1.md` |
| Magic items | `class schemas/magic_item_schema_v0_1.md` |
| Monsters | `class schemas/monster_schema_v0_1.md` |
| Feats and Epic Boons | `class schemas/feat_and_epic_boon_schema_v0_1.md` |

### Read when building a character

The standard party and supplementary templates define concrete characters that the engine must be able to build. Use them as test cases:

- `std party files/00_Party_Summary_v0_2.md` — overview of the 4-person test party
- `std party files/01_Garrick_BattleMaster_Fighter_v0_2.md` — Fighter (Battle Master) at all 20 levels
- `std party files/02_Elowyn_Life_Cleric_v0_2.md` — Cleric (Life Domain)
- `std party files/03_Varian_Evocation_Wizard_v0_2.md` — Wizard (Evocation)
- `std party files/04_Mira_Thief_Rogue_v0_2.md` — Rogue (Thief)
- `class templates/` — nine supplementary characters covering all remaining classes (for subclass testing when the test subclass is not in the main party)

---

## 6. Core Concepts You Must Understand

### The standard party

Four characters (Garrick, Elowyn, Varian, Mira) are the fixed control group. They are Human, use standard array, and are fully specified at every level 1-20. Every simulation uses this party unless overridden.

When testing a subclass not covered by the main party (e.g., a homebrew Paladin), the engine swaps the subclass into a supplementary class template (Aldric the Paladin) and uses that character as the fifth party member for delta measurement.

### Test methodology

- **1000 runs** per scenario configuration
- **~12-15 million simulations** for full baseline generation
- **Categorized tracking** (not filtering): participation tier (fully/partial/none) + impact tier (high/moderate/low-mechanical/low-random)
- **Per-class distribution bands** (not global)
- **Pillar-by-pillar evaluation**: combat, solo endurance, social, exploration, investigation

Never reduce the sample size to save time without the user's approval. Statistical significance depends on run count.

### Seven content types

The framework handles seven distinct content categories, each with its own schema, test harness, and baseline:

1. **Subclasses** — primary test target; also primary use of the supplementary templates
2. **Monsters** — tested as encounter components
3. **Magic items** — tested for impact on character capability
4. **Spells** — tested for power relative to slot level
5. **Feats** (including Epic Boons) — tested for opportunity cost
6. **Backgrounds** — tested for ASI distribution and origin feat value
7. **Species** — tested via point-based trait scoring

### Engine layers

Seven layers, strict downward dependency:

1. Schema validation
2. Content registry
3. Simulation engine
4. Behavior AI
5. Test runner
6. Test harnesses
7. Reporting

Never import upward (engine must not import from reporting). If you find a circular dependency, the architecture is wrong; flag it.

### Deterministic simulation

Every simulation is reproducible from its random seed. Same seed + same content + same engine version = identical result. Non-determinism is a bug.

---

## 7. Execution Protocol

When the user assigns a task, follow this protocol.

### Step 1: Orient

- Re-read AGENTS.md if you have not this session
- Read the relevant milestone section of `PHASE_2_PLAN.md`
- Read the relevant milestone checklist in `MILESTONE_CHECKLISTS.md`
- Read any schema or architecture section the task touches

### Step 2: Plan

Before writing code:

- State what you are about to do, in 2-4 sentences
- Identify what existing code or documentation the work touches
- Identify any ambiguities in the specification; ask the user before proceeding
- If the task is larger than one commit, break it into logical units

### Step 3: Implement

- Follow established patterns in the codebase
- Write tests for new or changed behavior
- Use descriptive names; avoid single-letter variables except in mathematical contexts
- Add type hints
- Keep functions under 100 lines and modules under 300 lines where practical

### Step 4: Verify

- Run relevant tests: `pytest tests/unit/<area>` or `pytest tests/integration/<area>`
- Run the full suite if changes are cross-cutting: `pytest`
- Run pre-commit: `pre-commit run --all-files`
- Check the milestone checklist: does this work tick any boxes?

### Step 5: Commit

- Follow commit conventions in `GIT_WORKFLOW.md` (Conventional Commits format)
- One logical change per commit
- If multiple logical changes occurred, split into multiple commits
- Reference the milestone in the commit body when helpful

### Step 6: Report

When the task is complete, tell the user:

- What was done (in plain language)
- What tests now pass
- What milestone checklist items are now complete
- Any caveats, known limitations, or follow-up work needed

---

## 8. Quality Standards

### Code quality

- **Type hints required.** Public functions need complete type signatures. Private helpers should have them when non-obvious.
- **Docstrings required** for public functions and classes. Use concise descriptions; no reformatted restating of the signature.
- **Tests required** for every non-trivial function. If you cannot write a test, the function is probably wrong.
- **No silent exception handling.** Never `except Exception: pass`. Catch specific exceptions; log or re-raise with context.
- **No magic numbers.** Constants get named. `WEAPON_DAMAGE_BONUS_CAP = 10` is clearer than `10`.

### Test quality

- **Tests are deterministic.** Use fixed seeds for anything involving randomness.
- **Tests are isolated.** No global state; no dependencies between tests; no order sensitivity.
- **Tests are fast.** Unit tests under 1 second each. Integration tests under 30 seconds.
- **Tests are specific.** `test_attack_hits_when_roll_meets_ac` is better than `test_attack_works`.

### Content quality

- **Quote the source text** in comments above each feature in YAML files. Makes review trivially easy.
- **Use schema-compliant field names.** Do not invent fields not in the schema.
- **Use `scripted_feature` sparingly.** Every `scripted_feature` requires custom engine logic; use standard types first.
- **Verify against the 2024 PHB.** Subclass feature levels changed from 2014. Do not work from memory.

### Commit quality

- **Subject under 72 characters.**
- **Body explains why, not how.** Code shows how.
- **Conventional Commits format.** `type(scope): subject`
- **One logical change per commit.** No "and" in commit subjects.

### Documentation quality

- **Update docs when code changes.** If a public API changes, the docs that reference it must change in the same PR.
- **Examples over prose.** Short code examples are worth more than paragraphs.
- **Link to architecture spec** when referring to design decisions; do not re-explain them inline.

---

## 9. Specific Guardrails

### On D&D rules

The project targets **D&D 5.5e (2024 PHB)**, not 2014 fifth edition. Differences that have caused confusion already:

- **Ability score increases come from backgrounds**, not species (species no longer grant ASI in 2024)
- **Human 2024** grants Origin Feat + Skillful + Resourceful, no ASI
- **Cleric Divine Intervention at L10** now casts any 5th-level-or-lower spell (no d100 roll); Greater Divine Intervention at L20 casts Wish
- **Life Domain** 2024 spell list differs substantially from 2014; Preserve Life only targets Bloodied creatures; Blessed Strikes is a L7 base Cleric feature (not subclass)
- **Battle Master subclass levels:** 3, 7, 10, 15, 18 (not the 2014 timing)
- **Thief subclass levels:** 3, 9, 13, 17 (specifically not 14)
- **Evoker subclass levels:** 3, 6, 10, 14
- **2025 Monster Manual:** legendary actions are SINGLE-USE per action (not recharge); unified ability score + modifier + save table; monsters in lair get bonus legendary resistance/action uses

When in doubt about a rule, search the web or ask the user rather than guessing. Do not invent mechanics.

### On file paths with spaces

Current folders use spaces (`class schemas/`, `std party files/`, etc.). When reorganizing to target structure (which uses underscores or no separator — `docs/schemas/`, `docs/party_sheets/`), preserve git history via `git mv` rather than delete + create.

### On version suffixes

Some files use `v0_1` (underscore); the architecture spec internally references `v0.1` (period). Both refer to the same version. When creating new versions, use the period format inside documents and underscore in filenames.

### On simulation claims

**No simulations have been run.** Phase 1 was design only. Any document or comment suggesting otherwise is in error. Never claim simulation results before the engine exists and has been validated.

When you do run simulations (Phase 2 onward), always report:
- The engine version used
- The content version used
- The random seed(s) used
- The number of runs
- The statistical confidence bounds

### On the Legion Warlock

The user has a homebrew Legion Warlock subclass (written for 2014 rules) that is the primary motivating use case for this framework. It needs to be converted to 2024 rules. **Do not attempt this conversion without the user's explicit direction** — it is Phase 3 work, and the user may have specific design intent that is not documented.

### On breaking changes

The schemas are versioned. If you must change a schema in a breaking way:

1. Flag it to the user before making the change
2. Bump the schema version (v0.1 → v0.2)
3. Provide a migration path for any existing content files
4. Update the architecture spec and this AGENTS.md to reflect the change

### On asking the user

The user is knowledgeable about D&D and the design of this framework. When you ask a question:

- Be specific about what you need to know
- State the options you see
- Recommend one, with reasoning
- Accept that the user may choose an option you did not foresee

Do not ask trivial questions (style preferences, variable names); make reasonable choices and flag them in the commit message.

The user is addressed as "My Lord" / "Liege" in existing documentation. This is a style preference, not a required form of address. Natural professional tone is fine.

---

## 10. First-Session Checklist

If this is your first session on the project, do the following in order:

1. [ ] Read this AGENTS.md in full
2. [ ] Read `framework/README.md`
3. [ ] Read `architecture_spec_v0_1.md` sections 1-5 (the overview and layer descriptions)
4. [ ] Read `framework/PHASE_2_PLAN.md` sections 1-3
5. [ ] Read `framework/MILESTONE_CHECKLISTS.md` M0 section
6. [ ] Read `framework/GIT_WORKFLOW.md` (full)
7. [ ] Report to the user: "I have oriented on the project. I am ready to begin Phase 2 Milestone M0 (Repository Setup). Shall I proceed?"

Wait for the user's go-ahead before executing M0. Do not begin creating files until the user confirms.

---

## 11. Every-Session Start Habits

At the start of every session (after the first), do the following:

1. Check `git status` and `git log --oneline -20` to understand the current repository state
2. Read the current milestone section in `PHASE_2_PLAN.md` and the matching checklist in `MILESTONE_CHECKLISTS.md`
3. Identify where the previous session left off (look at recent commits, open PRs, TODO comments)
4. Re-read any AGENTS.md sections relevant to the current task
5. Report your understanding of the current state and propose the next step to the user

**Do not assume state from memory.** The repository is the source of truth; your memory across sessions is not.

---

## 12. Common Pitfalls to Avoid

Based on the design process that produced Phase 1, these errors are likely and should be watched for:

### Pitfall: Using 2014 rules data from memory

LLM training data includes substantial 2014 fifth edition content. When authoring content for 2024 rules, always verify against the 2024 PHB or 2025 Monster Manual. Do not trust your initial recall.

### Pitfall: Paraphrasing mechanics

When encoding a feature from the PHB, quote the exact text in a comment, then translate mechanically. Do not summarize "in your own words" — summarization drops constraints like "once per turn" or "creatures you can see."

### Pitfall: Skipping the schema validator

It is tempting to author content directly without running validation. This creates subtle bugs that only surface later. Run `python scripts/validate_content.py` after every content change.

### Pitfall: Overusing `scripted_feature`

The `scripted_feature` feature type is an escape hatch for genuinely novel mechanics. Every use requires custom engine code. Before using it, check whether an existing feature type fits.

### Pitfall: Inflating test sample sizes

1000 runs per configuration is the standard. More runs do not improve results meaningfully and slow development. Fewer runs compromise statistical significance. Do not tune this number without the user's approval.

### Pitfall: Large, multi-concern PRs

Keep PRs focused. A PR titled "schema layer, registry, and character builder" is three PRs. Split them.

### Pitfall: Forgetting about determinism

Anything that uses randomness must accept a seed. If you find yourself unable to reproduce a test failure, non-determinism has crept in; fix it immediately.

### Pitfall: Silent content duplication

If a mechanic appears in both a class and a subclass (e.g., Fighter's Second Wind vs. a subclass that grants an additional Second Wind use), the class defines the pool; the subclass modifies it. Never duplicate the pool definition.

### Pitfall: Drifting from the architecture spec

The architecture spec is authoritative. If implementation reveals a design that seems wrong, flag it for discussion and possible spec revision; do not quietly implement a different design.

---

## 13. When Stuck

If you are stuck on a task:

1. **Re-read the relevant specification.** The architecture spec and milestone checklists contain more detail than any summary.
2. **Search the existing codebase.** Similar problems have likely been solved already.
3. **Write a test case first.** If you cannot write a test, the requirements are unclear; clarify them before coding.
4. **Ask the user.** State what you are trying to do, what you have tried, and what is blocking you.

Do not:

- Guess and ship
- Write code you cannot justify
- Mark a milestone complete when checklist items remain unchecked
- Skip tests because "they are hard for this feature"

---

## 14. Success Criteria for Phase 2

Phase 2 is complete when all of these are true:

- [ ] All seven content types validate from YAML (M1)
- [ ] Standard party builds correctly at all levels 1-20 (M2)
- [ ] Engine passes the full sanity check suite (M5)
- [ ] Subclass test harness produces reports for at least the 16 Tier A subclasses (M6-M9)
- [ ] Partial baseline v0.9 is published and usable (M9)
- [ ] At least one homebrew subclass has been tested end-to-end with a real report
- [ ] CLI is usable without Python knowledge

Stretch goals (Phase 2.5):

- [ ] All 61 subclass YAMLs authored
- [ ] Full baseline v1.0 published
- [ ] Monster test harness functional

See `framework/PHASE_2_PLAN.md` §6 for details.

---

## 15. Beyond Phase 2

Phase 3 (balancing the user's homebrew) and Phase 4 (productizing as web app) are out of scope for the current work.

If you complete Phase 2 successfully, report the completion and wait for direction on Phase 3. Do not pre-emptively begin Phase 3 work.

---

## Revision History

- **v0.1 (initial):** First AGENTS.md for the project. Captures Phase 2 starting state with the folder layout delivered by the user.

If you update this file, increment the version, add a revision entry, and summarize the change.
