"""Subclass comparison harness.

compare_subclasses() runs two CharacterBuild variants (e.g. Battle Master vs
Champion) over the same seeded encounter batch and returns side-by-side stats.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

from balance_framework.engine.combatant import CombatantState
from balance_framework.engine.scenario import ScenarioState
from balance_framework.registry.character_builder import CharacterBuild, build_character
from balance_framework.registry.registry import ContentRegistry
from balance_framework.ai.profiles import CLASS_PROFILE
from balance_framework.ai.decision import select_actions
from balance_framework.runner.orchestrator import run_encounter_batch
from balance_framework.runner.collector import EncounterResult
from balance_framework.reporting.test_report import summarize, EncounterSuite
from balance_framework.harnesses.base import default_enemy_band, make_scenario


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass
class CombatantStats:
    """Per-combatant aggregated stats across N encounters."""
    combatant_id: str
    n: int
    avg_damage_dealt: float
    avg_kills: float
    avg_healing_done: float
    avg_hp_fraction: float
    survival_rate: float


@dataclass
class VariantResult:
    """Batch outcome for one build variant."""
    label: str
    suite: EncounterSuite
    combatant_stats: dict[str, CombatantStats] = field(default_factory=dict)


@dataclass
class SubclassComparison:
    """Side-by-side results for two subclass variants."""
    variant_a: VariantResult
    variant_b: VariantResult


# ---------------------------------------------------------------------------
# Core comparison function
# ---------------------------------------------------------------------------

EnemyFactory = Callable[[int], list[CombatantState]]


def compare_subclasses(
    build_a: CharacterBuild,
    label_a: str,
    build_b: CharacterBuild,
    label_b: str,
    registry: ContentRegistry,
    *,
    n: int = 100,
    base_seed: int = 0,
    combatant_id: str = "variant",
    enemy_factory: EnemyFactory | None = None,
) -> SubclassComparison:
    """Run *n* encounters for each build and return side-by-side stats.

    Each variant fights solo against the enemies returned by *enemy_factory*
    (default: 2 standard goblins).  Using the same seeds for both variants
    makes win-rate differences more attributable to the build rather than luck.
    """
    if enemy_factory is None:
        enemy_factory = lambda seed: default_enemy_band(2)  # noqa: E731

    return SubclassComparison(
        variant_a=_run_variant(build_a, label_a, combatant_id, registry, n, base_seed, enemy_factory),
        variant_b=_run_variant(build_b, label_b, combatant_id, registry, n, base_seed, enemy_factory),
    )


def run_subclass_build(
    build: CharacterBuild,
    label: str,
    registry: ContentRegistry,
    *,
    n: int = 100,
    base_seed: int = 0,
    enemy_factory: EnemyFactory | None = None,
) -> VariantResult:
    """Run *n* encounters for one build and return aggregated stats."""
    if enemy_factory is None:
        enemy_factory = lambda seed: default_enemy_band(2)  # noqa: E731
    return _run_variant(build, label, "variant", registry, n, base_seed, enemy_factory)


def _run_variant(
    build: CharacterBuild,
    label: str,
    combatant_id: str,
    registry: ContentRegistry,
    n: int,
    base_seed: int,
    enemy_factory: EnemyFactory,
) -> VariantResult:
    profile = CLASS_PROFILE.get(build.class_id, "passive")

    def factory(seed: int) -> ScenarioState:
        char = build_character(build, registry)
        cs = CombatantState.from_character(char, combatant_id, label, "party", profile)
        return make_scenario([cs], enemy_factory(seed), seed)

    results = run_encounter_batch(factory, select_actions, n=n, base_seed=base_seed)
    suite = summarize(results)
    combatant_stats = _aggregate_combatant_stats(results, combatant_id, n)
    return VariantResult(label=label, suite=suite, combatant_stats=combatant_stats)


def _aggregate_combatant_stats(
    results: list[EncounterResult],
    combatant_id: str,
    n: int,
) -> dict[str, CombatantStats]:
    totals: dict[str, dict] = {}
    for r in results:
        for cr in r.combatants:
            entry = totals.setdefault(cr.id, {
                "damage_dealt": 0, "kills": 0, "healing_done": 0,
                "hp_frac_sum": 0.0, "survived": 0,
            })
            entry["damage_dealt"] += cr.damage_dealt
            entry["kills"] += cr.kills
            entry["healing_done"] += cr.healing_done
            entry["hp_frac_sum"] += cr.hp_final / cr.hp_max if cr.hp_max else 0.0
            entry["survived"] += 1 if cr.is_alive else 0

    stats: dict[str, CombatantStats] = {}
    for cid, t in totals.items():
        stats[cid] = CombatantStats(
            combatant_id=cid,
            n=n,
            avg_damage_dealt=t["damage_dealt"] / n,
            avg_kills=t["kills"] / n,
            avg_healing_done=t["healing_done"] / n,
            avg_hp_fraction=t["hp_frac_sum"] / n,
            survival_rate=t["survived"] / n,
        )
    return stats


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def format_comparison(comparison: SubclassComparison) -> str:
    """Return a human-readable side-by-side comparison report."""
    a, b = comparison.variant_a, comparison.variant_b

    def _party_row(v: VariantResult) -> str:
        wr = v.suite.win_rate("party") * 100
        ar = v.suite.avg_rounds
        return f"{v.label:<20} win={wr:5.1f}%  avg_rounds={ar:.1f}"

    lines = [
        "=== Subclass Comparison ===",
        "",
        f"{'Variant':<20} {'Win Rate':>10}  {'Avg Rounds':>12}",
        "-" * 46,
        _party_row(a),
        _party_row(b),
        "",
        "--- Variant combatant stats ---",
    ]

    for v in (a, b):
        cs = v.combatant_stats.get(next(iter(v.combatant_stats), ""), None)
        if cs is None:
            continue
        # Find the variant character (not enemies)
        party_ids = [cid for cid in v.combatant_stats if not cid.startswith("g")]
        if not party_ids:
            continue
        cs = v.combatant_stats[party_ids[0]]
        lines.append(
            f"  {v.label}: dmg={cs.avg_damage_dealt:.1f}  kills={cs.avg_kills:.2f}"
            f"  heal={cs.avg_healing_done:.1f}  surv={cs.survival_rate * 100:.1f}%"
        )

    return "\n".join(lines)
