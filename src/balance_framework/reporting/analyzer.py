"""Subclass YAML analyzer — format validation + simulation coverage report.

Returns a structured dict suitable for both CLI pretty-printing and JSON API
responses. No registry required; analysis is purely schema + static rules.
"""

from __future__ import annotations

from typing import Any

import yaml as _yaml

from balance_framework.schema.validators import validate_subclass
from balance_framework.schema.exceptions import ValidationError

# ---------------------------------------------------------------------------
# Coverage knowledge base — maps feature_type to (coverage, explanation)
# ---------------------------------------------------------------------------

_FULL: dict[str, str] = {
    "extra_attack":         "Increases attacks per Attack action.",
    "sneak_attack":         "Adds sneak attack dice to the first hit each turn.",
    "second_wind":          "Tracked as a resource; used as a bonus-action heal when HP <= 30%.",
    "action_surge":         "Tracked as a resource; grants an extra Attack action when enemies remain.",
    "combat_superiority":   "Superiority dice tracked and spent to add 1d8 to attacks.",
    "channel_divinity":     "Tracked as a resource pool; CD subclass effects partially dispatch.",
    "rage":                 "Tracked as rage uses per long rest.",
    "unarmored_defense":    "Formula applied to AC at build time.",
    "hp_bonus_per_level":   "Applied to HP at build time (e.g. Tough feat).",
    "fighting_style":       "Applied to AC or attack bonus at build time.",
    "lay_on_hands":         "Tracked as a healing resource pool.",
    "pact_magic":           "Tracked as Pact Magic spell slots.",
    "spellcasting":         "Tracked as spell slots by level.",
    "focus_points":         "Tracked as a ki/focus point pool.",
    "sorcery_points":       "Tracked as a sorcery point pool.",
    "damage_resistance":    "Applied to incoming damage of that type.",
    "damage_immunity":      "Negates incoming damage of that type.",
    "damage_vulnerability": "Doubles incoming damage of that type.",
    "attack_count_modifier": "Applied to attack count per turn.",
    "crit_range_modifier":  "Applied to critical hit threshold.",
    "passive_roll_modifier": "Applied as bonus damage dice or flat modifier when modifier_type=bonus_damage.",
}

_PARTIAL: dict[str, str] = {
    "choice_feature":        None,  # special-cased below; pool breakdown reported separately
    "spell_grant":           "Spells are modeled as generic spell-slot attacks; individual spell effects are not simulated.",
    "passive_feature_grant": "Named features (Dread Ambusher, Assassinate, etc.) have specific engine support; unknown features are ignored.",
    "passive_stat_modifier": "Applied only if it maps to a known engine stat (AC, damage).",
    "save_proficiency":      "Save proficiencies are respected for concentration and death saves, but not all combat saves.",
    "condition_immunity_grant": "Condition immunities are stored and respected for conditions the engine applies.",
    "bardic_inspiration":    "Tracked as a resource pool but the AI does not currently spend it.",
    "arcane_recovery":       "Tracked as a resource; recovery happens between encounters, not within combat.",
    "wild_shape":            "Wild Shape resource tracked but transformation is not simulated.",
    "expertise":             "Tracked but skill checks are not part of combat simulation.",
}

_NONE: dict[str, str] = {
    "scripted_feature":        "Only description text - no machine-readable mechanics. Convert to choice_feature with a structured pool.",
    "triggered_on_kill":       "Trigger hooks are not implemented in the combat engine.",
    "triggered_on_miss":       "Trigger hooks are not implemented in the combat engine.",
    "triggered_on_spell_cast": "Trigger hooks are not implemented in the combat engine.",
    "aura":                    "Aura effects are not implemented.",
    "skill_proficiency_grant": "Skill proficiencies have no effect on combat simulation.",
    "feat_grant":              "Granted feats are not resolved during simulation.",
    "sensory_feature":         "Sensory traits are not modeled in the abstract arena.",
    "origin_feat_grant":       "Origin feat grants are not resolved during simulation.",
    "species_ability":         "Most species abilities are not modeled in combat.",
    "scripted_trait":          "Monster-only trait; not applicable to subclasses.",
    "custom_action":           "Custom actions require manual engine dispatch; not auto-simulated.",
    "reaction":                "Reaction features are tracked but AI selectors don't spend reactions (except choice_feature pool options).",
    "condition_resistance":    "Condition resistance is not implemented.",
    "weapon_mastery_selection": "Weapon mastery properties are not implemented.",
}

# Weight used for coverage % calculation
_COVERAGE_WEIGHT = {"full": 1.0, "partial": 0.5, "none": 0.0}


# ---------------------------------------------------------------------------
# Pool option analysis
# ---------------------------------------------------------------------------

def _analyze_pool(body: dict[str, Any]) -> dict[str, Any]:
    pool = body.get("pool", [])
    if not pool:
        return {"total": 0, "simulatable": 0, "simulatable_ids": [], "not_simulatable": []}
    simulatable_ids = [o["id"] for o in pool if o.get("simulatable")]
    not_simulatable = [o["id"] for o in pool if not o.get("simulatable")]
    return {
        "total": len(pool),
        "simulatable": len(simulatable_ids),
        "simulatable_ids": simulatable_ids,
        "not_simulatable": not_simulatable,
    }


# ---------------------------------------------------------------------------
# Feature classification
# ---------------------------------------------------------------------------

def _classify_feature(feature: dict[str, Any]) -> dict[str, Any]:
    ftype = feature.get("feature_type", "unknown")
    fid   = feature.get("id", "?")
    name  = feature.get("display_name", fid)
    level = feature.get("unlock_level")
    pool_info: dict | None = None

    if ftype in _FULL:
        coverage = "full"
        reason = _FULL[ftype]
    elif ftype == "choice_feature":
        pool_info = _analyze_pool(feature.get("body", {}))
        total = pool_info["total"]
        sim   = pool_info["simulatable"]
        if total == 0:
            coverage = "none"
            reason = "choice_feature with an empty pool - add pool options with simulatable: true."
        elif sim == 0:
            coverage = "none"
            reason = f"All {total} pool options have simulatable: false. Mark options with supported effect types as simulatable: true."
        elif sim == total:
            coverage = "full"
            reason = f"All {total} pool options are simulatable."
        else:
            coverage = "partial"
            reason = f"{sim}/{total} pool options are simulatable. Not simulated: {', '.join(pool_info['not_simulatable'][:5])}{'...' if len(pool_info['not_simulatable']) > 5 else ''}."
    elif ftype in _PARTIAL:
        coverage = "partial"
        reason = _PARTIAL[ftype]
    elif ftype in _NONE:
        coverage = "none"
        reason = _NONE[ftype]
    else:
        coverage = "none"
        reason = f"Unknown feature_type {ftype!r} - not recognized by the engine."

    result: dict[str, Any] = {
        "feature_id":   fid,
        "display_name": name,
        "unlock_level": level,
        "feature_type": ftype,
        "coverage":     coverage,
        "reason":       reason,
    }
    if pool_info is not None:
        result["pool_options"] = pool_info
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyze_subclass_yaml(yaml_text: str) -> dict[str, Any]:
    """Parse, validate, and analyze a subclass YAML string.

    Returns a dict with keys:
      valid, parse_error, schema_errors, subclass_id, display_name,
      parent_class, features (list of classified feature dicts), summary.
    """
    result: dict[str, Any] = {
        "valid": False,
        "parse_error": None,
        "schema_errors": [],
        "subclass_id":   None,
        "display_name":  None,
        "parent_class":  None,
        "features":      [],
        "summary":       {},
    }

    # 1. Parse
    try:
        data = _yaml.safe_load(yaml_text)
    except _yaml.YAMLError as exc:
        result["parse_error"] = str(exc)
        return result

    if not isinstance(data, dict):
        result["parse_error"] = "YAML root must be a mapping (key: value pairs)."
        return result

    if data.get("content_type") != "subclass":
        result["schema_errors"] = [
            f"content_type must be 'subclass', got {data.get('content_type')!r}."
        ]
        return result

    # 2. Schema validate
    try:
        validate_subclass(data)
        result["valid"] = True
    except ValidationError as exc:
        result["schema_errors"] = [str(exc)]
        # Continue analysis even on schema error — partial info is still useful

    result["subclass_id"]  = data.get("id")
    result["display_name"] = data.get("display_name")
    result["parent_class"] = data.get("parent_class")

    # 3. Feature coverage
    features_raw = data.get("features", [])
    classified = [_classify_feature(f) for f in features_raw if isinstance(f, dict)]
    result["features"] = classified

    # 4. Summary
    counts = {"full": 0, "partial": 0, "none": 0}
    for f in classified:
        counts[f["coverage"]] += 1

    total = len(classified)
    if total > 0:
        weighted = sum(_COVERAGE_WEIGHT[f["coverage"]] for f in classified)
        pct = round(weighted / total * 100)
    else:
        pct = 0

    result["summary"] = {
        "total_features":      total,
        "fully_simulated":     counts["full"],
        "partially_simulated": counts["partial"],
        "not_simulated":       counts["none"],
        "coverage_pct":        pct,
    }

    return result
