"""CLI commands for baseline generation."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import click

# Standard party builds (matches M5 sanity checks)
_STANDARD_PARTY = [
    ("garrick", "fighter", dict(
        species_id="human", class_id="fighter", subclass_id="battle_master",
        background_id="soldier",
        ability_scores={"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8},
        feat_ids=["tough", "savage_attacker"],
        armor_type="chain_mail", has_shield=True, selected_fighting_style="defense",
    )),
    ("elowyn", "cleric", dict(
        species_id="human", class_id="cleric", subclass_id="life_domain",
        background_id="acolyte",
        ability_scores={"STR": 14, "DEX": 12, "CON": 15, "INT": 8, "WIS": 16, "CHA": 10},
        feat_ids=["healer", "magic_initiate_cleric"],
        armor_type="scale_mail", has_shield=True,
    )),
    ("varian", "wizard", dict(
        species_id="human", class_id="wizard", subclass_id="evoker",
        background_id="sage",
        ability_scores={"STR": 8, "DEX": 14, "CON": 15, "INT": 16, "WIS": 12, "CHA": 10},
        feat_ids=["alert", "magic_initiate_wizard"],
        armor_type="none", uses_mage_armor=True,
    )),
    ("mira", "rogue", dict(
        species_id="human", class_id="rogue", subclass_id="thief",
        background_id="charlatan",
        ability_scores={"STR": 8, "DEX": 16, "CON": 15, "INT": 12, "WIS": 14, "CHA": 10},
        feat_ids=["alert", "skilled"],
        armor_type="studded_leather",
    )),
]

# All subclasses to include in a full baseline run
_TIER_A_SUBCLASSES: list[tuple[str, str]] = [
    # (class_id, subclass_id)
    ("fighter", "battle_master"),
    ("fighter", "champion"),
    ("fighter", "eldritch_knight"),
    ("cleric", "life_domain"),
    ("cleric", "light_domain"),
    ("cleric", "war_domain"),
    ("cleric", "trickery_domain"),
    ("wizard", "evoker"),
    ("wizard", "abjurer"),
    ("wizard", "diviner"),
    ("wizard", "illusionist"),
    ("rogue", "thief"),
    ("rogue", "assassin"),
    ("rogue", "arcane_trickster"),
    ("rogue", "soulknife"),
    ("barbarian", "berserker"),
    ("barbarian", "world_tree"),
    ("barbarian", "zealot"),
    ("bard", "lore"),
    ("bard", "dance"),
    ("bard", "glamour"),
    ("paladin", "devotion"),
    ("paladin", "ancients"),
    ("paladin", "glory"),
    ("paladin", "vengeance"),
    ("ranger", "gloom_stalker"),
    ("ranger", "beast_master"),
    ("ranger", "fey_wanderer"),
    ("ranger", "hunter"),
    ("monk", "shadow"),
    ("monk", "mercy"),
    ("monk", "elements"),
    ("monk", "open_hand"),
    ("druid", "land"),
    ("druid", "moon"),
    ("druid", "sea"),
    ("druid", "stars"),
    ("sorcerer", "wild_magic"),
    ("sorcerer", "aberrant_mind"),
    ("sorcerer", "clockwork_soul"),
    ("sorcerer", "draconic"),
    ("warlock", "great_old_one"),
    ("warlock", "archfey"),
    ("warlock", "celestial"),
    ("warlock", "fiend"),
]


@click.command(name="generate-baseline")
@click.option(
    "--output", required=True,
    type=click.Path(),
    help="Output path: a .json file for a single party baseline, or a directory for per-subclass baselines.",
)
@click.option(
    "--runs", default=100, show_default=True,
    help="Number of encounters to simulate.",
)
@click.option(
    "--level", default=5, show_default=True,
    help="Party/character level for the baseline.",
)
@click.option("--seed", default=0, show_default=True, help="Base random seed.")
@click.option(
    "--content-dir", default="content", show_default=True,
    type=click.Path(file_okay=False),
    help="Path to the content directory.",
)
@click.option(
    "--tier", default=None,
    type=click.Choice(["A"], case_sensitive=False),
    help="Generate per-subclass baselines for all subclasses in this tier.",
)
def generate_baseline(
    output: str,
    runs: int,
    level: int,
    seed: int,
    content_dir: str,
    tier: str | None,
) -> None:
    """Generate a balance baseline.

    Without --tier: writes a single party-vs-goblins baseline JSON to OUTPUT.

    With --tier A (or when OUTPUT has no .json extension): writes one JSON per
    Tier A subclass to OUTPUT/subclasses/ and a metadata.json to OUTPUT/.
    """
    out_path = Path(output)
    per_subclass_mode = (tier is not None) or (not output.endswith(".json"))

    if per_subclass_mode:
        _generate_tier_baselines(out_path, runs, level, seed, content_dir, tier or "A")
    else:
        _generate_party_baseline(out_path, runs, level, seed, content_dir)


def _generate_party_baseline(
    out_path: Path, runs: int, level: int, seed: int, content_dir: str
) -> None:
    from balance_framework.engine.combatant import CombatantState
    from balance_framework.engine.scenario import ScenarioState
    from balance_framework.engine.dice import Dice
    from balance_framework.ai.decision import select_actions
    from balance_framework.ai.profiles import CLASS_PROFILE
    from balance_framework.registry.loader import load_content_directory
    from balance_framework.registry.registry import ContentRegistry
    from balance_framework.registry.character_builder import CharacterBuild, build_character
    from balance_framework.runner.orchestrator import run_encounter_batch
    from balance_framework.reporting.test_report import summarize
    from balance_framework.reporting.baseline import save_baseline

    click.echo(f"Loading content from {content_dir!r}...")
    registry = ContentRegistry(load_content_directory(Path(content_dir)))

    def _goblin(id: str) -> CombatantState:
        return CombatantState(
            id=id, display_name=f"Goblin {id}",
            team="enemies", hp_max=7, hp_current=7, ac=15,
            proficiency_bonus=2,
            ability_modifiers={"STR": -1, "DEX": 2, "CON": 0},
            extra_attack_count=1, behavior_profile="monster_melee",
        )

    def factory(run_seed: int) -> ScenarioState:
        party = []
        for name, class_id, base in _STANDARD_PARTY:
            char = build_character(CharacterBuild(level=level, **base), registry)
            cs = CombatantState.from_character(
                char, name, name.capitalize(), "party", CLASS_PROFILE[class_id]
            )
            party.append(cs)
        goblins = [_goblin(f"g{i}") for i in range(4)]
        return ScenarioState(combatants=party + goblins, dice=Dice(run_seed))

    click.echo(f"Running {runs} encounters at level {level} (seed base={seed})...")
    results = run_encounter_batch(factory, select_actions, n=runs, base_seed=seed)
    suite = summarize(results)

    save_baseline(suite, out_path)
    wr = suite.win_rate("party")
    click.echo(
        f"Baseline saved to {out_path}\n"
        f"  party win rate = {wr:.1%}, avg rounds = {suite.avg_rounds:.1f}"
    )


def _generate_tier_baselines(
    out_dir: Path, runs: int, level: int, seed: int, content_dir: str, tier: str
) -> None:
    from balance_framework.registry.loader import load_content_directory
    from balance_framework.registry.registry import ContentRegistry
    from balance_framework.registry.character_builder import CharacterBuild
    from balance_framework.harnesses.subclass import run_subclass_build
    from balance_framework.harnesses.base import STANDARD_ENCOUNTERS, monster_enemy_band
    from balance_framework.cli.test_commands import _CLASS_DEFAULTS

    click.echo(f"Loading content from {content_dir!r}...")
    registry = ContentRegistry(load_content_directory(Path(content_dir)))

    subclasses_dir = out_dir / "subclasses"
    subclasses_dir.mkdir(parents=True, exist_ok=True)

    results_summary: list[dict] = []
    errors: list[str] = []

    for class_id, subclass_id in _TIER_A_SUBCLASSES:
        defaults = _CLASS_DEFAULTS.get(class_id)
        if defaults is None:
            click.echo(f"  SKIP  {class_id}/{subclass_id} (no default build)", err=True)
            continue

        click.echo(f"  Running {class_id}/{subclass_id} ({runs}×{len(STANDARD_ENCOUNTERS)} encounters)...")
        try:
            build = CharacterBuild(class_id=class_id, subclass_id=subclass_id, level=level, **defaults)
            enc_results: dict[str, object] = {}
            for enc_name, monster_id, count in STANDARD_ENCOUNTERS:
                factory = (
                    lambda s, mid=monster_id, cnt=count: monster_enemy_band(mid, cnt, registry)
                )
                enc_results[enc_name] = run_subclass_build(
                    build, subclass_id, registry, n=runs, base_seed=seed, enemy_factory=factory
                )

            out_path = subclasses_dir / f"{subclass_id}.json"
            _write_subclass_baseline(enc_results, class_id, subclass_id, level, runs, out_path)

            avg_wr = sum(
                r.suite.win_rate("party") for r in enc_results.values()
            ) / len(enc_results)
            avg_rnd = sum(r.suite.avg_rounds for r in enc_results.values()) / len(enc_results)
            click.echo(f"         avg_win={avg_wr:.1%}, avg_rounds={avg_rnd:.1f}")
            results_summary.append({
                "subclass_id": subclass_id,
                "class_id": class_id,
                "avg_win_rate": avg_wr,
                "avg_rounds": avg_rnd,
                "encounters": {
                    enc_name: {
                        "win_rate": enc_results[enc_name].suite.win_rate("party"),
                        "avg_rounds": enc_results[enc_name].suite.avg_rounds,
                    }
                    for enc_name in enc_results
                },
            })
        except Exception as exc:
            click.echo(f"  ERROR {class_id}/{subclass_id}: {exc}", err=True)
            errors.append(f"{class_id}/{subclass_id}: {exc}")

    _write_metadata(out_dir, tier, level, runs, seed, results_summary)
    click.echo(f"\nBaseline written to {out_dir}")
    click.echo(f"  {len(results_summary)} subclasses, {len(errors)} errors")
    if errors:
        for e in errors:
            click.echo(f"  ERROR: {e}", err=True)
        raise SystemExit(1)


def _write_subclass_baseline(
    enc_results: dict, class_id: str, subclass_id: str, level: int, runs: int, path: Path
) -> None:
    def _suite_dict(result) -> dict:
        cs = result.combatant_stats.get("variant")
        return {
            "suite": {
                "avg_rounds": result.suite.avg_rounds,
                "std_rounds": result.suite.std_rounds,
                "timed_out": result.suite.timed_out,
                "teams": {
                    team: {
                        "win_rate": ts.win_rate,
                        "avg_survivors": ts.avg_survivors,
                        "avg_hp_fraction": ts.avg_hp_fraction,
                    }
                    for team, ts in result.suite.teams.items()
                },
            },
            "combatant_stats": {
                "avg_damage_dealt": cs.avg_damage_dealt if cs else 0.0,
                "avg_kills": cs.avg_kills if cs else 0.0,
                "avg_healing_done": cs.avg_healing_done if cs else 0.0,
                "avg_hp_fraction": cs.avg_hp_fraction if cs else 0.0,
                "survival_rate": cs.survival_rate if cs else 0.0,
            },
        }

    win_rates = [r.suite.win_rate("party") for r in enc_results.values()]
    avg_rounds = [r.suite.avg_rounds for r in enc_results.values()]

    data = {
        "subclass_id": subclass_id,
        "class_id": class_id,
        "level": level,
        "n": runs,
        "aggregate": {
            "avg_win_rate": sum(win_rates) / len(win_rates),
            "min_win_rate": min(win_rates),
            "avg_rounds": sum(avg_rounds) / len(avg_rounds),
        },
        "encounters": {
            enc_name: _suite_dict(result)
            for enc_name, result in enc_results.items()
        },
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_metadata(
    out_dir: Path,
    tier: str,
    level: int,
    runs: int,
    seed: int,
    summary: list[dict],
) -> None:
    import balance_framework
    version = getattr(balance_framework, "__version__", "dev")
    metadata = {
        "baseline_version": "0.9",
        "framework_version": version,
        "rules_version": "PHB_2024",
        "tier": tier,
        "generated_on": date.today().isoformat(),
        "level": level,
        "runs_per_subclass": runs,
        "base_seed": seed,
        "subclass_count": len(summary),
        "subclasses": summary,
    }
    path = out_dir / "metadata.json"
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    click.echo(f"Metadata written to {path}")
