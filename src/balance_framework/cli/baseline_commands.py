"""CLI commands for baseline generation."""

from __future__ import annotations

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


@click.command(name="generate-baseline")
@click.option(
    "--output", required=True,
    type=click.Path(dir_okay=False),
    help="Output path for the baseline JSON file.",
)
@click.option(
    "--runs", default=100, show_default=True,
    help="Number of encounters to simulate.",
)
@click.option(
    "--level", default=5, show_default=True,
    help="Party level for the baseline.",
)
@click.option("--seed", default=0, show_default=True, help="Base random seed.")
@click.option(
    "--content-dir", default="content", show_default=True,
    type=click.Path(file_okay=False),
    help="Path to the content directory.",
)
def generate_baseline(
    output: str, runs: int, level: int, seed: int, content_dir: str
) -> None:
    """Generate a balance baseline from the standard party vs 4 goblins."""
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

    out_path = Path(output)
    save_baseline(suite, out_path)

    wr = suite.win_rate("party")
    click.echo(
        f"Baseline saved to {out_path}\n"
        f"  party win rate = {wr:.1%}, avg rounds = {suite.avg_rounds:.1f}"
    )
