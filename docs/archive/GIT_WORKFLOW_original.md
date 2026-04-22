# Git Workflow

Branching strategy, commit conventions, and pull request patterns for the D&D Homebrew Balance Framework repository.

---

## Table of Contents

1. [Branch Strategy](#1-branch-strategy)
2. [Commit Message Conventions](#2-commit-message-conventions)
3. [Pull Request Patterns](#3-pull-request-patterns)
4. [Code Review Checklist](#4-code-review-checklist)
5. [Release Tagging](#5-release-tagging)
6. [Common Scenarios](#6-common-scenarios)
7. [Pre-Commit Hooks](#7-pre-commit-hooks)

---

## 1. Branch Strategy

### Primary branches

**`main`** — Always stable. Every commit passes CI. No direct commits; all changes merge via pull request. Represents the latest reviewed and tested state.

**`develop`** — Optional integration branch for rapid iteration. Used when a milestone involves multiple PRs that need to land together before merging to main. Most work does not need develop; branch directly off main.

### Working branches

All working branches follow the pattern `type/description`:

- `feat/schema-layer` — New feature
- `fix/attack-roll-critical` — Bug fix
- `refactor/split-combat-module` — Non-behavioral refactoring
- `docs/update-architecture-spec` — Documentation-only change
- `content/fighter-subclasses` — Content additions (YAML files)
- `test/add-concentration-tests` — Test additions
- `chore/update-dependencies` — Repository maintenance

Keep branches short-lived. A branch that lives longer than two weeks should be split into smaller PRs.

### Branch naming rules

- Lowercase, hyphen-separated
- Descriptive but concise (3-5 words max)
- Start with type prefix matching commit convention
- No dates, ticket numbers, or author names in the branch name

### Branch lifecycle

```
main
 │
 ├── feat/schema-layer ────────► PR ──► main
 │
 ├── fix/crit-range-bug ────────► PR ──► main
 │
 └── content/tier-a-subclasses ─► PR ──► main
```

Each feature branch has a narrow focus. If work expands, split into multiple branches rather than growing one.

---

## 2. Commit Message Conventions

This repository uses **Conventional Commits** (https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Only the first line is required. The body and footer are for larger commits that benefit from explanation.

### Types

| Type | Use for |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `docs` | Documentation changes only |
| `content` | YAML content additions (subclasses, monsters, spells, etc.) |
| `chore` | Tooling, dependencies, CI, or repository maintenance |
| `perf` | Performance improvement |
| `style` | Code formatting (automated by pre-commit; rarely a manual commit) |

### Scopes

Common scopes for this repository:

- `schema` — Changes to schema validation layer
- `registry` — Content registry and character builder
- `engine` — Simulation engine (combat, mechanics)
- `ai` — Behavior AI
- `harness` — Test harnesses
- `runner` — Multi-run orchestration
- `reporting` — Report generation
- `cli` — Command-line interface
- Class or subclass name for content — `champion`, `life-domain`, `wild-heart`
- Module path abbreviation for focused fixes — `attacks`, `saves`, `concentration`

### Subject line rules

- **Imperative mood**: "add schema validator", not "added" or "adds"
- **Lowercase**: "fix crit range calculation", not "Fix Crit Range Calculation"
- **No period at the end**: "add X", not "add X."
- **Under 72 characters**: if longer, move detail to body
- **Specific**: "fix off-by-one in crit range threshold" beats "fix bug"

### Body rules

- Wrap at 72 characters
- Explain **what** and **why**, not how (code shows how)
- Separated from subject by blank line
- Use bullet points for multiple items

### Examples

**Good:**

```
feat(schema): add Pydantic validation for all content types

Introduces validators for each content type defined in the schemas.
Raises SchemaViolation for structural errors, VocabularyViolation
for invalid enum values. Paves the way for M2 (content registry)
which will use these validators at load time.

Tests cover happy path, missing required fields, and invalid
feature_type values for each content type.
```

```
fix(engine/attacks): correct crit range supersession

Improved Critical (L3) and Superior Critical (L15) both set the
crit threshold, but without supersession the lower threshold (18
from Superior) should take effect when both are active. Engine
was applying whichever was declared later in YAML order, which
is unreliable.

Now respects the `supersedes` field on crit_range_modifier.
```

```
content: add champion fighter subclass

First subclass YAML content. Serves as the reference example
for subsequent subclass authoring work.
```

```
docs: update Phase 2 plan with revised timeline

Weeks 4-5 expanded to cover engine core in more detail based
on actual complexity encountered in M3 implementation.
```

**Bad (and why):**

```
update stuff                    # Too vague; no type or scope
Fixed bug.                      # Capital, period, no type, vague
feat: stuff                     # Missing scope, vague subject
WIP                             # Never commit WIP to main
feat(engine): add massive refactor with new AI and reporting changes  # Multiple concerns
```

### Breaking changes

If a commit changes public API in a breaking way (removes or renames exports, changes schema format, alters content file paths):

- Add `!` after the type/scope: `feat(schema)!: rename feature_type "ability_check_bonus" to "skill_check_bonus"`
- Include a `BREAKING CHANGE:` footer explaining the impact and migration

```
feat(schema)!: rename feature_type "ability_check_bonus" to "skill_check_bonus"

The previous name was ambiguous because it suggested bonuses to
raw ability checks (rare) rather than skill checks (common).

BREAKING CHANGE: All existing content files using "ability_check_bonus"
must be updated to "skill_check_bonus". A migration script is provided
at scripts/migration/v0_1_to_v0_2.py.
```

### Commits per unit of work

One logical change per commit. If a single work session produces multiple logical changes, make multiple commits. Signs that a commit should be split:

- Multiple `feat(X)` changes in one commit
- A mix of `feat` and `refactor`
- Commit message contains "and" between major items

Exception: trivial changes (fixing a typo, adjusting formatting) can piggyback on the commit they relate to.

---

## 3. Pull Request Patterns

### When to open a PR

- Every change to `main` goes through a PR, even if you are the only contributor
- This enforces the pre-commit checks, CI, and review habit
- Solo developers: open PR, review it yourself, merge it

### PR title

Same format as commit message subject:

```
feat(schema): add Pydantic validation for all content types
```

The PR title becomes the squash commit message if you squash-merge (see below).

### PR description template

```markdown
## What this PR does

[One-paragraph summary of the change]

## Why

[Motivation: what problem does this solve?]

## How to verify

- [ ] Step 1: [specific action]
- [ ] Step 2: [specific action]
- [ ] Step 3: [specific action]

## Milestone

Contributes to: [M1 / M2 / M3 / etc.]

## Checklist

- [ ] Code follows repository style conventions
- [ ] Tests added or updated for changed behavior
- [ ] Documentation updated if needed
- [ ] Pre-commit hooks pass locally
- [ ] CI pipeline passes
- [ ] No scope creep beyond the PR title

## Notes for reviewer

[Optional: specific areas you want feedback on, known limitations, follow-up work]
```

### PR size guidelines

| Size | Lines Changed | Review Time | Appropriate for |
|---|---|---|---|
| Small | < 100 | 5-15 min | Bug fixes, content files, small refactors |
| Medium | 100-500 | 15-45 min | Most feature PRs |
| Large | 500-1500 | 45+ min | Initial scaffolding, major refactors |
| Huge | > 1500 | Discouraged | Split into multiple PRs |

**If your PR exceeds 1500 lines, split it.** Exception: generated files or bulk content imports.

### Merging strategy

**Squash and merge** is the default. It keeps `main` history clean (one commit per PR) while preserving detail via the PR description.

**Merge commit** is used for PRs that genuinely contain multiple useful commits (e.g., a refactor followed by a feature that builds on it).

**Rebase and merge** is avoided for simplicity; squash accomplishes the same outcome without rewriting individual commit hashes.

### Self-review before requesting review

Before marking a PR ready for review:

1. Re-read the diff yourself
2. Run the full test suite locally
3. Run any relevant manual verification steps
4. Check that the PR description accurately describes the change
5. Remove debug code, commented-out code, and TODO comments for this PR's scope

---

## 4. Code Review Checklist

Use this checklist when reviewing PRs (including your own self-reviews).

### Correctness

- [ ] Does the code do what the PR description says?
- [ ] Are there tests covering the new or changed behavior?
- [ ] Do the tests actually test the behavior (not just exercise the code)?
- [ ] Are edge cases considered (empty inputs, boundary values, error conditions)?
- [ ] Does the code handle failures gracefully (no silent catches, no unhelpful errors)?

### Architecture alignment

- [ ] Does this follow the patterns established in the architecture spec?
- [ ] Are layer boundaries respected (engine doesn't import from reporting, etc.)?
- [ ] If a new pattern is introduced, is it justified?

### Schema and content

- [ ] If schema changes: are all affected content files updated?
- [ ] If content changes: does it pass validation?
- [ ] Is new vocabulary (feature types, etc.) documented?

### Testing

- [ ] Do tests run in reasonable time (unit tests under 1 second each)?
- [ ] Are tests deterministic (fixed seeds where randomness is involved)?
- [ ] Is coverage maintained or improved?

### Documentation

- [ ] If public API changes: is README or relevant doc updated?
- [ ] If architecture changes: is the architecture spec updated?
- [ ] Are non-obvious decisions explained in comments?

### Style

- [ ] Does `pre-commit run --all-files` pass?
- [ ] Are type hints used consistently?
- [ ] Are functions and classes appropriately sized (under 100 lines for functions, under 300 for modules)?
- [ ] Are names descriptive and consistent with the rest of the codebase?

### Git hygiene

- [ ] Is the commit message clear and following conventions?
- [ ] Is the PR focused on one concern?
- [ ] Are there no stray files (IDE configs, OS-specific files, binary junk)?

---

## 5. Release Tagging

### Version scheme

This project uses **Semantic Versioning** (SemVer):

- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- `MAJOR`: incompatible API changes (including schema format changes)
- `MINOR`: backward-compatible feature additions
- `PATCH`: backward-compatible bug fixes

Pre-release phase uses `0.Y.Z`:

- `0.1.0`: First functional milestone (e.g., M3 complete)
- `0.5.0`: Usable for subclass testing (e.g., M6 complete)
- `0.9.0`: Partial baseline (M9)
- `1.0.0`: Full baseline published (M10, Phase 2 complete)

### When to tag

- After each major milestone is complete and merged to `main`
- When publishing a baseline (baseline version matches engine version)
- Before major refactors (so there is a rollback point)

### Tag format

```bash
git tag -a v0.1.0 -m "M1 complete: schema layer"
git push origin v0.1.0
```

### Release notes

For each tag, write release notes in the repository (either as a GitHub/GitLab release or a `CHANGELOG.md` entry):

```markdown
## v0.1.0 — 2024-MM-DD

### Added
- Schema validation layer for all seven content types
- Pydantic models for Class, Subclass, Species, Background, Spell, MagicItem, Monster, Feat
- Validation script at `scripts/validate_content.py`

### Changed
- None (first release)

### Known limitations
- Engine not yet implemented (planned for v0.2.0)
- Only Champion Fighter example content available
```

### Baseline versioning

Baselines have their own version independent of code version:

- `baselines/v0.9/` — first partial baseline (Tier A only)
- `baselines/v1.0/` — first complete baseline
- `baselines/v1.1/` — updated baseline with new subclasses from expansion releases

Each baseline directory contains a `metadata.json` with:
- Baseline version
- Engine version used to generate it
- Rules version (2024 PHB, etc.)
- Date generated
- Number of runs per configuration

---

## 6. Common Scenarios

### Scenario: starting new work

```bash
git checkout main
git pull
git checkout -b feat/behavior-ai
# ... do work ...
git add -A
git commit -m "feat(ai): add action enumeration"
# ... more work, more commits ...
git push -u origin feat/behavior-ai
# Open PR on GitHub/GitLab
```

### Scenario: update branch with latest main

Use rebase to keep history linear:

```bash
git checkout feat/behavior-ai
git fetch origin main
git rebase origin/main
# Resolve conflicts if any
git push --force-with-lease
```

Use `--force-with-lease` instead of `--force` to avoid clobbering someone else's work on the same branch.

### Scenario: fix a typo in a commit just made

```bash
# If not yet pushed
git commit --amend

# If already pushed (and no one else is working on the branch)
git commit --amend
git push --force-with-lease
```

### Scenario: fix a typo in an older commit

```bash
# Interactive rebase
git rebase -i HEAD~5  # Adjust N based on how many commits back

# Change "pick" to "reword" for the commit to fix, save and exit
# Git will reopen with the commit message; edit and save

git push --force-with-lease
```

**Do not rewrite history on `main`.** Only rewrite on feature branches before merging.

### Scenario: content-only PR is large

When adding many subclass YAMLs in bulk (e.g., all 16 Tier A subclasses):

- Group by class: "content: add all Fighter subclasses" or "content: add Tier A PHB subclasses (part 1)"
- Include the authoring guide reference in PR description
- Link to the authoring process followed

A single PR with 16 subclass files is acceptable because they are pure content and review is about correctness of each YAML, which can be parallelized.

### Scenario: reverting a bad change

```bash
# For a single commit
git revert <commit-hash>

# For a merged PR with multiple commits
git revert -m 1 <merge-commit-hash>
```

Do not rewrite history on `main` to "un-merge" a PR. Revert it, document the reason, and move on.

### Scenario: work has stalled and branch is outdated

If a branch has been open for more than two weeks without activity:

- If the work is still relevant: rebase onto `main`, resume
- If the work is no longer relevant: close the PR with explanation, delete the branch
- If the work is partially useful: extract what is valuable into a new, focused PR

Do not let stale branches accumulate. They create confusion and hide useful work.

---

## 7. Pre-Commit Hooks

The `.pre-commit-config.yaml` file (created in M0) runs automatically before each commit.

### Hooks configured

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, types-PyYAML]
        args: [--strict]
```

### What each hook does

- **trailing-whitespace**: Removes trailing spaces from lines
- **end-of-file-fixer**: Ensures files end with a newline
- **check-yaml**: Validates YAML syntax (not schema; just that it parses)
- **check-added-large-files**: Prevents accidentally committing large binaries
- **check-merge-conflict**: Prevents committing files with merge conflict markers
- **ruff**: Python linting with automatic fixes
- **ruff-format**: Python code formatting
- **mypy**: Static type checking in strict mode

### Running hooks manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run a specific hook
pre-commit run ruff --all-files

# Update hook versions periodically
pre-commit autoupdate
```

### When a hook fails

If pre-commit fails:

1. Read the error message carefully
2. Fix the issue (most hooks auto-fix; re-stage the fixed files)
3. Commit again

If a hook genuinely needs to be bypassed (rare):

```bash
git commit --no-verify -m "..."
```

Do not make `--no-verify` a habit. If you find yourself bypassing hooks often, either the hooks are misconfigured (fix them) or the code is genuinely low-quality (fix the code).

---

## Workflow summary

For a typical feature:

1. `git checkout main && git pull`
2. `git checkout -b feat/my-feature`
3. Make changes, committing frequently with good messages
4. Run tests locally (`pytest`)
5. Run pre-commit (`pre-commit run --all-files`)
6. Push and open PR
7. Self-review the diff
8. Wait for CI to pass
9. Request review (or self-review for solo work)
10. Address feedback with additional commits
11. Squash-merge when approved and CI green
12. Delete the branch
13. `git checkout main && git pull` to update local

For content authoring:

1. Follow the authoring guide's process
2. Author one subclass (or one small batch) per branch
3. Validate content before committing (`python scripts/validate_content.py`)
4. Commit with message `content: add [subclass name]`
5. Open PR, self-review, merge

---

## Revision History

- **v0.1 (current):** Initial Git workflow document covering branches, commits, PRs, reviews, releases, pre-commit hooks.
