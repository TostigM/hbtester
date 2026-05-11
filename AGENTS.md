# AGENTS.md

Instructions for AI coding agents (Claude Code, Cursor, Copilot, etc.) working on this project.

Read this document in full at the start of every session. Treat it as authoritative; if any other instruction conflicts with AGENTS.md, surface the conflict to the user rather than silently resolving it.

---

## 1. Project Identity

**Project name:** D&D Homebrew Balance Framework

**What it is:** A simulation-based balance testing framework for Dungeons & Dragons 5.5e (2024 rules) homebrew content. The framework evaluates user-authored content (subclasses, monsters, magic items, spells, feats, backgrounds, species) by running it through simulated test batteries and comparing results against a pre-computed baseline of WotC-published content.

**What it is not:** A rules engine for live play, a VTT, a campaign manager, or a character optimizer. It is a statistical analysis tool for content design.

**Primary users:**

1. The project owner (referred to as "the user" in documentation) — a D&D DM designing homebrew content for home games (notably the "Ferrystones family game" and "Tides and Time" campaigns)
2. Other DMs wanting to validate homebrew balance (Phase 4 product audience)
3. Content creators publishing homebrew who want baseline comparisons (Phase 4)

**Target language:** Python (3.11+). Use `C:\Users\tosti\AppData\Local\Programs\Python\Python312\python.exe` on this machine — not `python` or `python3`, which may resolve to wrong installations.

**Target deployment:** Open-source Python library with CLI. Flask REST API for web use. Static HTML dashboard hosted on Bluehost; API deployed on Render.com free tier.

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
- **Adding dependencies.** New packages in `pyproject.toml` or `api/requirements.txt` affect the environment. Propose first.
- **Deleting or heavily restructuring existing code.** Unless the user asked for it, do not delete working code.
- **Skipping tests to ship faster.** If tests are failing or missing, that is a signal, not an obstacle.
- **Changing the `main` branch directly.** Always use feature branches per `GIT_WORKFLOW.md`.

### What you must never do

- **Do not invent mechanics.** The framework implements D&D 5.5e rules. If a rule is unclear, say so and ask. Do not guess.
- **Do not fabricate content.** Subclass features come from the PHB. Monsters come from the Monster Manual. Never make up numbers to fill gaps.
- **Do not bypass validation.** If content does not pass schema validation, do not work around it; fix the content or the schema, with the user's knowledge.
- **Do not claim results without running the engine.** Report actual run outputs, not estimates.
- **Do not change the `main` branch history.** Rebase feature branches freely; never rewrite `main`.
- **Do not commit secrets, API keys, or personal information.** There should be none in this project anyway.

---

## 3. Current Phase

**Phase 1 (Design): Complete.**

**Phase 2 (Implementation M0–M10): Complete.** All seven content types validate, standard party builds at all levels, engine runs, 45 subclasses baselined at L5, CLI functional.

**Phase 3 (Encounter depth + feature simulation): In progress.** M11–M13 complete. Encounter pool expanded to 8 scenarios; key subclass features simulate meaningfully; Flask API and homebrew test panel built.

**Phase 4 (Productize as web app): Underway** via M13 (API + static dashboard).

### Phase 3 milestones completed

| Milestone | Description | Commit |
|---|---|---|
| M11 | Encounter variety expansion — breath weapons, casters, undead, dragons | c03445c |
| M12 | Subclass feature simulation — Battle Master, Berserker, Gloom Stalker, Assassin | 49bab60 |
| M12b | Paladin CD buffs (Sacred Weapon, Vow of Enmity) + Abjurer Arcane Ward | 339b9ea |
| M13 | Flask REST API + homebrew test panel in static dashboard | 5f162ad |

### Immediate next step

Deploy to Render.com (user action required — see Section 17). After deploy, update `const API_BASE` in `web/index.html` with the live URL.

---

## 4. Repository Layout

```
<project root>/
├── AGENTS.md                    ← This file
├── Procfile                     ← gunicorn start command for Render/Heroku
├── render.yaml                  ← Render.com deployment config
├── pyproject.toml
├── .gitignore
│
├── api/                         ← Flask REST API (M13)
│   ├── app.py                   ← Routes, rate limiter, registry injection, simulation helper
│   └── requirements.txt         ← flask, flask-cors, gunicorn, pydantic, pyyaml, numpy
│
├── src/balance_framework/
│   ├── schema/                  ← Pydantic models for all 7 content types
│   ├── registry/                ← Content loading, ContentRegistry, CharacterBuild
│   ├── engine/
│   │   ├── combat/              ← CombatEngine, actions.py
│   │   ├── noncombat/           ← Non-combat stubs
│   │   ├── combatant.py         ← CombatantState (all simulation mutable fields)
│   │   ├── dice.py              ← Seeded dice roller
│   │   └── scenario.py          ← CombatScenario, round_number
│   ├── ai/
│   │   ├── profiles.py          ← AI profile constants; combat_stats_from_features()
│   │   ├── decision.py          ← Dispatcher: profile → selector function
│   │   ├── monster.py           ← monster_melee_selector, monster_caster_selector
│   │   ├── scorer.py            ← Target-scoring heuristics
│   │   └── heuristics/
│   │       ├── martial.py       ← Fighter/Barbarian/Ranger/Rogue action selectors
│   │       ├── support.py       ← Cleric/Paladin/Bard selectors; _war_priest_bonus
│   │       ├── caster.py        ← Wizard/Sorcerer/Warlock selectors
│   │       └── healer.py        ← Healing heuristics
│   ├── harnesses/               ← Per-content-type test harnesses (subclass, monster, …)
│   ├── cli/                     ← Click CLI; _CLASS_DEFAULTS dict; test_commands
│   ├── runner/                  ← SimulationRunner, SuiteResult
│   └── reporting/               ← Baseline generation, metadata.json writer
│
├── content/
│   ├── classes/                 ← 12 class YAMLs (all PHB 2024 classes)
│   ├── subclasses/              ← 45 subclass YAMLs
│   ├── monsters/                ← 16 monster YAMLs (see Section 16)
│   ├── spells/
│   ├── feats/
│   ├── magic_items/
│   ├── species/
│   └── backgrounds/
│
├── baselines/
│   ├── v0.9/                    ← Early partial baseline
│   ├── v1.0/                    ← 45 subclasses, single encounter
│   ├── v1.1/                    ← 8 encounters (M11)
│   ├── v1.2/                    ← Feature simulation depth (M12)
│   └── v1.3/                    ← Paladin CD + Abjurer ward (M12b) — CURRENT
│
├── web/
│   ├── index.html               ← Static balance dashboard + homebrew test panel
│   └── data/                    ← Bundled baseline data for offline/local viewing
│
├── tests/                       ← pytest suite
├── scripts/                     ← CLI utilities (validate_content, gen_baseline, …)
└── docs/                        ← Architecture spec, schemas, authoring guides
```

---

## 5. Document Map

### Read before starting any work

- **`AGENTS.md`** (this file) — orientation for every session
- **`framework/README.md`** — top-level project overview

### Read when working on engine or content code

- **`docs/architecture_spec_v0_1.md`** (or `architecture_spec_v0_1.md` at root) — master architecture document; 18 sections covering every design decision
- **`framework/MILESTONE_CHECKLISTS.md`** — verification criteria per milestone
- **`framework/GIT_WORKFLOW.md`** — branching, commits, PRs

### Read when authoring content

- **`docs/schemas/`** or **`class schemas/`** — schema definitions for all 7 content types
- **`subclass authoring guide/subclass_authoring_guide_v0_1.md`** — full authoring methodology
- **`subclass authoring guide/champion_fighter_example.yaml`** — canonical YAML format reference

### Read when implementing a specific content type

| Content type | Schema file |
|---|---|
| Classes | `class schemas/class_schema_v0_1.md` |
| Subclasses | `class schemas/subclass_schema_v0_1.md` |
| Monsters | `class schemas/monster_schema_v0_1.md` |
| Species | `class schemas/species_schema_v0_1.md` |
| Backgrounds | `class schemas/background_schema_v0_1.md` |
| Spells | `class schemas/spell_schema_v0_1.md` |
| Magic items | `class schemas/magic_item_schema_v0_1.md` |
| Feats and Epic Boons | `class schemas/feat_and_epic_boon_schema_v0_1.md` |

### Read when building a character

- `std party files/00_Party_Summary_v0_2.md` — overview of the 4-person test party
- `std party files/01_Garrick_BattleMaster_Fighter_v0_2.md` — Fighter (Battle Master)
- `std party files/02_Elowyn_Life_Cleric_v0_2.md` — Cleric (Life Domain)
- `std party files/03_Varian_Evocation_Wizard_v0_2.md` — Wizard (Evocation)
- `std party files/04_Mira_Thief_Rogue_v0_2.md` — Rogue (Thief)
- `class templates/` — nine supplementary characters covering all remaining classes

---

## 6. Core Concepts You Must Understand

### The standard party

Four characters (Garrick, Elowyn, Varian, Mira) are the fixed control group. They use standard array and are fully specified. Every simulation uses this party unless overridden.

When testing a subclass not in the main party (e.g., a homebrew Paladin), the engine builds a character using `_CLASS_DEFAULTS` from `cli/test_commands.py` and sets the test subclass on it. The standard party is not extended — class defaults determine stats.

### Test methodology

- **Development runs:** 50–100 per scenario (fast iteration)
- **Baseline generation:** 200 runs per scenario (currently used for v1.x baselines)
- **Full production baseline:** 1000 runs (Phase 4 target)
- **Current standard encounters:** 8 scenarios across `STANDARD_ENCOUNTERS` in `harnesses/base.py`
- **Categorized tracking:** win rate, avg rounds, avg damage dealt, avg kills, survival rate per combatant

Never reduce sample size without the user's approval.

### The 8 standard encounters (as of M11)

| Key | Monster | Count |
|---|---|---|
| `goblin_band` | goblin | 2 |
| `skeleton_pack` | skeleton | 3 |
| `orc_pair` | orc | 2 |
| `lone_ogre` | ogre | 1 |
| `hell_hound_pair` | hell_hound | 2 |
| `lone_banshee` | banshee | 1 |
| `lone_mage` | mage | 1 |
| `dragon_wyrmling` | black_dragon_wyrmling | 1 |

If you add encounters, update both `STANDARD_ENCOUNTERS` in `harnesses/base.py` **and** the encounter filter buttons + JS constants in `web/index.html`.

### Seven content types

1. **Subclasses** — primary test target
2. **Monsters** — encounter components
3. **Magic items** — character capability impact
4. **Spells** — power relative to slot level
5. **Feats** (including Epic Boons) — opportunity cost
6. **Backgrounds** — ASI distribution and origin feat value
7. **Species** — point-based trait scoring

### Engine layers (strict downward dependency)

1. Schema validation
2. Content registry
3. Simulation engine
4. Behavior AI
5. Test runner
6. Test harnesses
7. Reporting

Never import upward. Circular dependency = architectural error; flag it.

### Deterministic simulation

Every simulation is reproducible from its random seed. Same seed + same content + same engine version = identical result. Non-determinism is a bug.

---

## 7. AI Profiles and Subclass Feature Simulation

This section documents decisions made in M11–M12b that are not obvious from the code alone.

### AI profile constants (`ai/profiles.py`)

| Constant | Used by |
|---|---|
| `MARTIAL` | Fighter, Barbarian, Ranger |
| `CASTER` | Wizard, Sorcerer, Warlock |
| `SUPPORT` | Cleric, Paladin, Bard, Druid |
| `ROGUE` | Rogue |
| `MONSTER_MELEE` | Default monster profile |
| `MONSTER_CASTER` | Monsters with `behavior_hints.spell_slots` |

### `combat_stats_from_features()` output keys

This function reads a subclass's feature list and returns a dict that `CombatantState.from_character()` consumes. Keys added in M12/M12b:

```
frenzy_bonus_attack    # Berserker: bonus attack using Frenzy
dread_ambusher         # Gloom Stalker: extra attack + damage on round 1
assassinate            # Assassin: advantage on round 1
has_war_priest         # War Priest: bonus attack after Attack action
sacred_weapon          # Oath of Devotion: CHA to attack rolls via CD
vow_of_enmity          # Oath of Ancients: advantage via CD
arcane_ward_hp         # Abjurer: temp HP = 2*level + INT mod
```

### `CombatantState` fields added in M11–M12b

All fields default to `False` / `None` / `0` so existing content is unaffected:

```python
frenzy_bonus_attack: bool = False
dread_ambusher: bool = False
assassinate: bool = False
war_priest_attack: bool = False
sacred_weapon: bool = False
vow_of_enmity: bool = False
cd_offensive_active: bool = False   # tracks one-time CD spend for sacred_weapon/vow
breath_weapon_config: dict | None = None
melee_attack_bonus: int | None = None  # override for monsters with non-STR attacks
```

### Battle Master superiority dice

Tracked as a resource pool (`"superiority_dice": ResourcePool(current, max)`). In `martial.py`, each attack action call to `has_resource("superiority_dice")` + `spend()` appends `(1, 8)` to `damage_dice`. Action Surge attacks also spend superiority dice.

### Berserker Frenzy

After the main attack loop, if `frenzy_bonus_attack=True` and `bonus_actions_remaining > 0` and `has_resource("rage")`, a bonus `WeaponAttackAction` is appended. Frenzy does **not** spend the rage resource (rage lasts the encounter); it only checks that rage is active.

### Gloom Stalker Dread Ambusher

On `round_number == 1`: `extra_attack_count + 1`, and the last attack in the sequence appends `(2, 6)` to `damage_dice`. No effect on rounds 2+.

### Assassin Assassinate

`advantage = combatant.assassinate and scenario.round_number == 1`. No resource tracking needed — advantage is purely conditional.

### Paladin Channel Divinity (Sacred Weapon / Vow of Enmity)

Both use the `cd_offensive_active` flag:
1. Before the attack loop, if `cd_offensive_active=False` and `bonus_actions_remaining > 0` and `has_resource("channel_divinity")`: spend CD, set flag, decrement bonus action.
2. Sacred Weapon: `atk_bonus += max(0, CHA mod)` while flag is set.
3. Vow of Enmity: all attacks use `advantage=True` while flag is set.

`cd_offensive_active` resets to `False` each new encounter because `from_character()` creates a fresh `CombatantState`.

### War Priest

`_war_priest_bonus(combatant, target)` in `support.py` fires after any offensive action (spell or cantrip). Spends 1 `war_priest` resource, decrements bonus action, returns a `WeaponAttackAction`. War Priest pool max = `max(1, WIS mod)`, reset on long rest.

### Arcane Ward (Abjurer)

Set directly in `from_character()`: `state.temp_hp = combat_stats["arcane_ward_hp"]`. Value = `2 * level + INT_mod`. No runtime recharge logic — the ward absorbs hits via the standard temp HP subtraction in the damage resolver.

### BreathWeaponAction

`BreathWeaponAction` in `engine/combat/actions.py` hits **all living enemies**. Each makes a DEX (or specified) save vs `save_dc`; failure = full damage, success = half. Spends the `"breath_weapon"` resource (max 1). Monsters get `breath_weapon: 1` in their resource pool if `behavior_hints.breath_weapon` is set.

### Monster caster profile

If a monster YAML has `behavior_hints.spell_slots`, the monster gets `ai_profile: monster_caster`. `monster_caster_selector` in `ai/monster.py` delegates to `caster_selector`. The monster's spell attack bonus, spell save DC, and spell slots are read from `behavior_hints`.

### Banshee / non-STR melee

Set `melee_attack_bonus: int` in `behavior_hints` to override the default STR-based attack bonus. The banshee uses CHA (+4) instead of STR (-5).

---

## 8. Flask API (`api/app.py`)

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Liveness probe — returns `{"status":"ok","version":"0.1.0"}` |
| GET | `/api/baselines` | Serves `baselines/v1.3/metadata.json` |
| GET | `/api/subclasses/<id>` | Serves `baselines/v1.3/subclasses/<id>.json` |
| POST | `/api/simulate` | Accepts homebrew YAML, runs simulation, returns results |

### `/api/simulate` request schema

```json
{
  "yaml_content": "<full subclass YAML as a string>",
  "runs": 50,
  "level": 5
}
```

`runs` is clamped to `[1, MAX_RUNS]` (default 100). `level` is clamped to `[1, MAX_LEVEL]` (default 10).

### Registry injection pattern

The shared `ContentRegistry` is loaded once at startup. Simulations inject the homebrew subclass temporarily:

```python
old = registry._subclasses.get(sc_id)
registry._subclasses[sc_id] = subclass_obj
try:
    # run harness
finally:
    if old is None: registry._subclasses.pop(sc_id, None)
    else: registry._subclasses[sc_id] = old
```

`_sim_lock` (threading.Lock) serializes all simulations to prevent concurrent registry mutations.

### Rate limiter

In-memory dict of `IP → [monotonic timestamps]`. 5 requests per 60-second window. Resets on process restart (acceptable for free tier). Reads `X-Forwarded-For` header (set by Render).

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `PYTHONPATH` | — | Must be set to `src` |
| `CONTENT_DIR` | `content` | Path to content YAML directory |
| `BASELINES_DIR` | `baselines/v1.3` | Path to baseline JSON files |
| `MAX_RUNS` | `100` | Max simulation runs per API request |
| `MAX_LEVEL` | `10` | Max character level per API request |
| `PORT` | `5000` | Port for gunicorn (set automatically by Render) |

### Running locally

```powershell
$env:PYTHONPATH="src"; $env:CONTENT_DIR="content"; $env:BASELINES_DIR="baselines/v1.3"; $env:PORT="5000"
C:\Users\tosti\AppData\Local\Programs\Python\Python312\python.exe api/app.py
```

---

## 9. Static Web Dashboard (`web/index.html`)

The dashboard is a single self-contained HTML file. Key constants at the top of the `<script>` block:

```js
const API_BASE = window.HB_API_BASE || 'https://hbtester-api.onrender.com';
const ENCOUNTERS = ['goblin_band','skeleton_pack','orc_pair','lone_ogre',
                    'hell_hound_pair','lone_banshee','lone_mage','dragon_wyrmling'];
```

**When the API is deployed**, replace the `onrender.com` URL with the actual Render service URL. `window.HB_API_BASE` can also be set in a `<script>` tag on the hosting page as an override.

The "Test Homebrew Subclass" panel sends a `POST /api/simulate` request and renders aggregate summary cards + per-encounter grid. The placeholder YAML in the textarea is a valid minimal subclass skeleton.

---

## 10. Execution Protocol

When the user assigns a task, follow this protocol.

### Step 1: Orient

- Re-read AGENTS.md if you have not this session
- Run `git status` and `git log --oneline -10`
- Read the relevant section of `framework/PHASE_2_PLAN.md` if it exists for the task
- Read any schema or architecture section the task touches

### Step 2: Plan

Before writing code:

- State what you are about to do, in 2–4 sentences
- Identify what existing code the work touches
- Identify any ambiguities; ask the user before proceeding

### Step 3: Implement

- Follow established patterns in the codebase
- Write tests for new or changed behavior
- Use descriptive names; add type hints
- Keep functions under 100 lines and modules under 300 lines where practical

### Step 4: Verify

- Run relevant tests: `C:\Users\tosti\AppData\Local\Programs\Python\Python312\python.exe -m pytest tests/`
- Check that baselines still generate if combat engine changed
- For API changes, run the server locally and hit the endpoints manually

### Step 5: Commit

- Follow Conventional Commits format: `type(scope): subject`
- One logical change per commit; split multi-concern changes
- Reference the milestone in the commit body when helpful

### Step 6: Report

When the task is complete, tell the user:

- What was done (in plain language)
- What tests now pass
- Any caveats, known limitations, or follow-up work needed

---

## 11. Quality Standards

### Code quality

- **Type hints required** on public functions.
- **No silent exception handling.** Never `except Exception: pass`.
- **No magic numbers.** Named constants only.
- **No unnecessary comments.** Only comment the non-obvious WHY.

### Test quality

- **Tests are deterministic.** Use fixed seeds for randomness.
- **Tests are isolated.** No global state; no order sensitivity.
- **Tests are fast.** Unit tests < 1 second each.

### Content quality

- **Quote source text** in YAML comments above each feature.
- **Schema-compliant fields only.** Do not invent fields.
- **`scripted_feature` sparingly.** Every use requires custom engine logic.
- **Verify against 2024 PHB.** Do not work from memory.

### Commit quality

- Subject under 72 characters.
- Body explains why, not how.
- `type(scope): subject` format.

---

## 12. Specific Guardrails

### On D&D rules

The project targets **D&D 5.5e (2024 PHB)**, not 2014 fifth edition. Known differences:

- **Ability score increases come from backgrounds**, not species
- **Human 2024:** Origin Feat + Skillful + Resourceful, no ASI
- **Cleric Divine Intervention at L10:** casts any ≤5th-level spell (no d100 roll)
- **Life Domain 2024:** Preserve Life only targets Bloodied creatures; Blessed Strikes is base Cleric L7
- **Battle Master subclass levels:** 3, 7, 10, 15, 18
- **Thief subclass levels:** 3, 9, 13, 17
- **Evoker subclass levels:** 3, 6, 10, 14
- **2025 Monster Manual:** legendary actions are single-use per action (not recharge); monsters in lair get bonus uses

### On schema changes

The schemas are versioned contracts. If you must change a schema in a breaking way:

1. Flag it to the user before making the change
2. Bump the schema version (v0.1 → v0.2)
3. Provide a migration path for existing content files
4. Update AGENTS.md and the architecture spec

### On simulation claims

Simulations have been run from M5 onward. Always report the baseline version, run count, and level when citing results. Current canonical baseline: **v1.3**, 200 runs, L5.

### On the Legion Warlock

The user has a homebrew Legion Warlock subclass (written for 2014 rules) that is the primary motivating use case. It needs conversion to 2024 rules. **Do not attempt this without explicit direction** — it is Phase 3 work with user-specific design intent.

### On asking the user

- Be specific: state what you need, list the options you see, recommend one with reasoning.
- Do not ask trivial questions (style, variable names); make reasonable choices and note them in commits.

---

## 13. Every-Session Start Habits

1. Check `git status` and `git log --oneline -20` to understand current state
2. Read any AGENTS.md sections relevant to the current task
3. Identify where the previous session left off
4. Report your understanding of the current state and propose the next step
5. Before working on any class's subclasses, verify class infrastructure exists: class YAML in `content/classes/`, `_CLASS_DEFAULTS` entry in `cli/test_commands.py`, `CLASS_PROFILE` mapping in `ai/profiles.py` or `ai/decision.py`

**Do not assume state from memory.** The repository is the source of truth.

---

## 14. Common Pitfalls to Avoid

### Pitfall: Wrong Python executable

On this machine, use `C:\Users\tosti\AppData\Local\Programs\Python\Python312\python.exe` explicitly. `python` and `python3` may resolve to Windows Store stubs or a different install.

### Pitfall: Using 2014 rules data from memory

LLM training data includes substantial 2014 content. Always verify against the 2024 PHB. Do not trust initial recall.

### Pitfall: Paraphrasing mechanics

Quote the exact PHB text in a YAML comment, then translate mechanically. Summarization drops constraints like "once per turn" or "creatures you can see."

### Pitfall: Skipping the schema validator

Run `python scripts/validate_content.py` after every content change. Do not author content without validating.

### Pitfall: Overusing `scripted_feature`

Every `scripted_feature` requires custom engine code. Use standard feature types first.

### Pitfall: Inflating encounter pool without updating the dashboard

`STANDARD_ENCOUNTERS` in `harnesses/base.py` and the `ENCOUNTERS` / `ENC_LABEL` constants in `web/index.html` must stay in sync. The encounter filter buttons must also match.

### Pitfall: Forgetting `_sim_lock` when extending the API

Any code that mutates `registry._subclasses` must run inside `_sim_lock`. The lock is in `api/app.py`.

### Pitfall: Assuming class infrastructure exists

All 12 PHB classes have infrastructure as of M10. If you add a new class (homebrew or supplement), add: class YAML + `_CLASS_DEFAULTS` entry + `CLASS_PROFILE` mapping + smoke test, in that order.

### Pitfall: Forgetting about determinism

Anything that uses randomness must accept a seed. Non-determinism is a bug, not a feature.

### Pitfall: Silent content duplication

The class defines resource pools; the subclass modifies them. Never duplicate pool definitions.

---

## 15. When Stuck

1. **Re-read the relevant specification.** The architecture spec and milestone checklists contain more detail than any summary.
2. **Search the existing codebase.** Similar problems have been solved already.
3. **Write a test case first.** If you cannot write a test, the requirements are unclear.
4. **Ask the user.** State what you are trying to do, what you have tried, and what is blocking you.

Do not guess and ship. Do not skip tests. Do not mark a milestone complete when checklist items remain.

---

## 16. Content Inventory

### Monster YAMLs (`content/monsters/`)

16 monsters as of M11:

| File | CR | Notes |
|---|---|---|
| `goblin.yaml` | 1/4 | Standard melee |
| `skeleton.yaml` | 1/4 | Undead; archer |
| `orc.yaml` | 1/2 | Melee |
| `ogre.yaml` | 2 | Large, high damage |
| `bugbear.yaml` | 1 | Melee |
| `kobold.yaml` | 1/8 | Pack tactics |
| `wolf.yaml` | 1/4 | Pack tactics, knockdown |
| `owlbear.yaml` | 3 | Multiattack |
| `troll.yaml` | 5 | Regeneration |
| `ghoul.yaml` | 1 | Undead; paralysis |
| `manticore.yaml` | 3 | Multiattack 3 |
| `animated_armor.yaml` | 1 | Construct; multiattack 2 |
| `hell_hound.yaml` | 3 | Fiend; breath weapon (6d10 fire, DEX DC12) |
| `banshee.yaml` | 4 | Undead; CHA attack bonus override (+4) |
| `mage.yaml` | 6 | Humanoid; monster_caster profile; spell slots |
| `black_dragon_wyrmling.yaml` | 2 | Dragon; breath weapon (5d8 acid, DEX DC11) |

### Subclasses (`content/subclasses/`) — 45 total

All 12 PHB 2024 classes represented. Run `python scripts/list_baselines.py` or check `baselines/v1.3/metadata.json` for the full list with win rates.

---

## 17. Deployment

### Render.com (API)

1. Create a free account at render.com
2. New → Web Service → connect GitHub repo
3. Render auto-detects `render.yaml` — no manual config needed
4. After deploy, copy the service URL (e.g. `https://hbtester-api.onrender.com`)
5. Update `const API_BASE` in `web/index.html` with the live URL

**Cold start warning:** Free tier spins down after 15 min idle. First request after idle takes 30–60 s. The dashboard's loading state handles this gracefully.

### Static dashboard (Bluehost)

Upload `web/index.html` and `web/data/` to the hosting directory. No server-side processing needed. CORS is enabled on the API for all origins.

---

## 18. Success Criteria

### Phase 3 remaining work

- [ ] Deploy API to Render and update `API_BASE` in dashboard
- [ ] Test homebrew panel end-to-end against live API
- [ ] Validate that all 8 encounters render correctly in the web dashboard

### Phase 4 targets

- [ ] Full 1000-run baseline for all 45 subclasses
- [ ] Homebrew subclass testing via web UI (Legion Warlock conversion)
- [ ] User authentication and saved results (optional)

---

## Revision History

- **v0.1 (initial):** First AGENTS.md for the project. Captures Phase 2 starting state.
- **v0.2 (M11–M13 update):** Reflects completed Phase 2 (M0–M10) and Phase 3 progress through M13. Updated repository layout, added Sections 7–9 (AI profiles, Flask API, web dashboard), added Section 16 (content inventory), added Section 17 (deployment), updated success criteria, updated pitfalls, corrected Python executable path, removed M0 first-session checklist (obsolete).
