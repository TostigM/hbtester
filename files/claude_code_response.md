# Response to Claude Code

Confirmed gap; good catch. Proceed on that basis with two additions.

## Approved approach

For each of the 6 missing classes (druid, monk, paladin, ranger, sorcerer, warlock):

1. Add the class YAML in `content/classes/`
2. Add the `_CLASS_DEFAULTS` entry
3. Add the `CLASS_PROFILE` mapping
4. **Smoke test** before authoring subclasses: build a character of that class at levels 1, 5, 10, 20 and run a single combat simulation against a CR-appropriate baseline encounter (e.g., CR 1 orc at L1, CR 5 ogre at L5, CR 10 monster at L10, CR 17 monster at L20). Verify the engine processes the class without errors. This is a 5-minute cost per class that prevents debugging cascades during subclass authoring.
5. Then author the class's Tier B subclasses
6. Then move to the next class

For Bard: only the two missing Tier B subclasses (Dance, Glamour) need to be authored; the class infrastructure is already in place.

## Suggested order

Author classes in order of increasing engine complexity, so simpler cases surface engine bugs before complex ones:

1. **Paladin** (martial half-caster, simplest of the six; similar enough to Cleric that issues are likely already shaken out)
2. **Ranger** (martial half-caster; tests Hunter's Mark and concentration interactions)
3. **Monk** (martial with unique resource pool — Focus Points; tests new resource mechanics)
4. **Druid** (full caster + Wild Shape; Wild Shape is a known complex feature that may need engine work, so flag any issues here before moving on)
5. **Sorcerer** (full caster + Metamagic; tests Metamagic Sorcery Point spending)
6. **Warlock** (full caster with Pact Magic; tests short-rest slot recovery and Invocations system)

If any class smoke-test fails, stop and report before proceeding. Do not mass-author subclasses for a class whose chassis is broken.

## Subclass count clarification

The actual Tier B subclass count from the source plan is approximately 20:
- Druid: 3 (Land, Moon, Sea)
- Monk: 3 (Mercy, Shadow, Elements)
- Paladin: 3 (Ancients, Glory, Vengeance)
- Ranger: 3 (Beast Master, Fey Wanderer, Gloom Stalker)
- Sorcerer: 3 (Aberrant, Clockwork, Wild Magic)
- Warlock: 3 (Archfey, Celestial, Great Old One)
- Bard: 2 (Dance, Glamour)

Total: 20. The "~24" figure in PHASE_2_PLAN.md was an estimate. If you find the actual count differs from 20 because of how Tier A landed, let me know.

## Documentation update

In addition to the implementation work, please update `framework/PHASE_2_PLAN.md` and `AGENTS.md` to close the planning gap you identified:

- In `PHASE_2_PLAN.md` M10 section, add an explicit "class-level groundwork" prerequisite step describing what infrastructure each class requires before its subclasses can be authored
- In `AGENTS.md` Section 12 (Common Pitfalls), add a pitfall for "assuming class infrastructure exists when authoring subclasses for new classes"

These updates should land in the same PR as the M10 work, as a separate commit (`docs: clarify class-level prerequisites for subclass authoring`).

## Permission

Proceed with M10 on the basis above. Report after each class chassis lands (post-smoke-test, pre-subclass-authoring) so I can spot-check before the bulk YAML work.
