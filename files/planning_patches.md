# Planning Document Patches

These additions close the gap Claude Code identified during M10 planning. Apply both patches as part of the M10 PR (commit message: `docs: clarify class-level prerequisites for subclass authoring`).

---

## Patch 1: PHASE_2_PLAN.md

### Add a new subsection after the existing M10 description

Insert this block in `PHASE_2_PLAN.md` immediately after the existing M10 section, before the "Beyond Week 12" content.

```markdown
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
```

### Update the Tier B subclass count

In the existing "Tier B" listing inside the "M10 Full Baseline" milestone description, replace the rough estimate with the actual count:

**Before:**

> ### Tier B: Author second (PHB 2024 remaining, ~24 subclasses)

**After:**

> ### Tier B: Author second (PHB 2024 remaining, 20 subclasses)
> 
> Distribution by class: Druid (3), Monk (3), Paladin (3), Ranger (3), Sorcerer (3), Warlock (3), Bard (2 remaining).

---

## Patch 2: AGENTS.md

### Add a new pitfall to Section 12

Insert this entry in Section 12 (Common Pitfalls to Avoid), placed before the existing "Pitfall: Drifting from the architecture spec":

```markdown
### Pitfall: Assuming class infrastructure exists when authoring subclasses

Subclasses cannot be authored or tested in isolation. Each subclass requires 
its parent class to have complete infrastructure in place: a class YAML, a 
`_CLASS_DEFAULTS` entry in the character builder, and a `CLASS_PROFILE` 
mapping in the AI layer. After M2 (standard party) and M9 (Tier A), only 6 
of 12 PHB classes (Fighter, Cleric, Wizard, Rogue, Barbarian, Bard) have 
this infrastructure. The other 6 (Druid, Monk, Paladin, Ranger, Sorcerer, 
Warlock) need it added during M10 before their subclasses can be authored.

**Symptom:** Authoring a Land Druid subclass and finding that the validator 
or engine cannot process it because `parent_class: druid` has no class YAML 
or AI profile to attach to.

**Fix:** Before authoring subclasses for any class, verify the class's 
infrastructure exists. If it does not, add it (class YAML + defaults + 
profile + smoke test) and only then proceed to subclass authoring.

This is documented in `framework/PHASE_2_PLAN.md` M10 section under 
"Class-level groundwork."
```

### Add a class infrastructure check to Section 11 (Every-Session Start Habits)

Append this to the existing list of session-start steps:

```markdown
6. If you are about to author or test subclasses for a class you have not 
   touched before, verify that class's infrastructure exists (class YAML in 
   `content/classes/`, `_CLASS_DEFAULTS` entry, `CLASS_PROFILE` mapping). If 
   any are missing, halt subclass work and add the infrastructure first per 
   `PHASE_2_PLAN.md` M10 prerequisite section.
```

---

## Application notes

- Both patches are documentation-only; no code changes required.
- Apply as a single commit at the start of M10 work, before any class infrastructure changes. This way the docs describe what is about to be built rather than describing past work.
- Commit message: `docs: clarify class-level prerequisites for subclass authoring`
- After applying, run the docs validators if the project has any (markdown linting, link checking) before continuing with M10 implementation.
