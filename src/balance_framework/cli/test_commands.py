"""CLI commands for running balance tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
import yaml

from balance_framework.registry.character_builder import CharacterBuild

# Default stat arrays and equipment per class, matching the standard party
_CLASS_DEFAULTS: dict[str, dict] = {
    "fighter": dict(
        species_id="human", background_id="soldier",
        ability_scores={"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8},
        feat_ids=["tough"], armor_type="chain_mail", has_shield=True,
        selected_fighting_style="defense",
    ),
    "cleric": dict(
        species_id="human", background_id="acolyte",
        ability_scores={"STR": 14, "DEX": 12, "CON": 15, "INT": 8, "WIS": 16, "CHA": 10},
        feat_ids=["healer"], armor_type="scale_mail", has_shield=True,
    ),
    "wizard": dict(
        species_id="human", background_id="sage",
        ability_scores={"STR": 8, "DEX": 14, "CON": 15, "INT": 16, "WIS": 12, "CHA": 10},
        feat_ids=["alert"], armor_type="none", uses_mage_armor=True,
    ),
    "rogue": dict(
        species_id="human", background_id="charlatan",
        ability_scores={"STR": 8, "DEX": 16, "CON": 15, "INT": 12, "WIS": 14, "CHA": 10},
        feat_ids=["alert"], armor_type="studded_leather",
    ),
    "barbarian": dict(
        species_id="human", background_id="soldier",
        ability_scores={"STR": 17, "DEX": 14, "CON": 16, "INT": 8, "WIS": 12, "CHA": 10},
        feat_ids=["tough"], armor_type="none",
    ),
    "bard": dict(
        species_id="human", background_id="charlatan",
        ability_scores={"STR": 8, "DEX": 14, "CON": 14, "INT": 10, "WIS": 12, "CHA": 16},
        feat_ids=["alert"], armor_type="studded_leather",
    ),
    "paladin": dict(
        species_id="human", background_id="soldier",
        ability_scores={"STR": 17, "DEX": 10, "CON": 14, "INT": 8, "WIS": 12, "CHA": 14},
        feat_ids=["tough"], armor_type="chain_mail", has_shield=True,
        selected_fighting_style="defense",
    ),
    "ranger": dict(
        species_id="human", background_id="soldier",
        ability_scores={"STR": 8, "DEX": 17, "CON": 14, "INT": 12, "WIS": 14, "CHA": 10},
        feat_ids=["alert"], armor_type="studded_leather",
        selected_fighting_style="archery",
    ),
    "monk": dict(
        species_id="human", background_id="soldier",
        ability_scores={"STR": 10, "DEX": 17, "CON": 14, "INT": 8, "WIS": 16, "CHA": 10},
        feat_ids=["tough"], armor_type="none",
    ),
}


def _build_from_subclass_file(
    subclass_path: Path, level: int
) -> tuple[CharacterBuild, str]:
    """Parse a subclass YAML and assemble a CharacterBuild with class defaults."""
    raw: Any = yaml.safe_load(subclass_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise click.ClickException(f"Invalid YAML: {subclass_path}")

    subclass_id = raw.get("id")
    display_name = raw.get("display_name", subclass_id)
    parent_class = raw.get("parent_class")

    if not subclass_id:
        raise click.ClickException(f"Subclass YAML missing 'id' field: {subclass_path}")
    if not parent_class:
        raise click.ClickException(f"Subclass YAML missing 'parent_class' field: {subclass_path}")

    defaults = _CLASS_DEFAULTS.get(parent_class)
    if defaults is None:
        raise click.ClickException(
            f"No default build for class {parent_class!r}. "
            f"Supported: {sorted(_CLASS_DEFAULTS)}"
        )

    build = CharacterBuild(
        class_id=parent_class,
        subclass_id=subclass_id,
        level=level,
        **defaults,
    )
    return build, display_name


@click.group()
def test() -> None:
    """Run balance tests against homebrew content."""


@test.command()
@click.option(
    "--file", "subclass_file", required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the subclass YAML file to test.",
)
@click.option(
    "--runs", default=100, show_default=True,
    help="Number of encounters to simulate.",
)
@click.option(
    "--output", required=True,
    type=click.Path(dir_okay=False),
    help="Output path (.md for markdown, .json for JSON, otherwise plain text).",
)
@click.option("--level", default=5, show_default=True, help="Character level to test.")
@click.option("--seed", default=0, show_default=True, help="Base random seed.")
@click.option(
    "--content-dir", default="content", show_default=True,
    type=click.Path(file_okay=False),
    help="Path to the content directory.",
)
def subclass(
    subclass_file: str,
    runs: int,
    output: str,
    level: int,
    seed: int,
    content_dir: str,
) -> None:
    """Test a subclass and generate a balance report."""
    from balance_framework.registry.loader import load_content_directory
    from balance_framework.registry.registry import ContentRegistry
    from balance_framework.harnesses.subclass import run_subclass_build
    from balance_framework.reporting.test_report import summarize, format_report
    from balance_framework.reporting.formats.markdown import format_suite_markdown
    from balance_framework.reporting.formats.json import write_results

    click.echo(f"Loading content from {content_dir!r}...")
    registry = ContentRegistry(load_content_directory(Path(content_dir)))

    click.echo(f"Parsing subclass from {subclass_file!r}...")
    build, label = _build_from_subclass_file(Path(subclass_file), level)

    click.echo(f"Running {runs} encounters for {label!r} at level {level}...")
    result = run_subclass_build(build, label, registry, n=runs, base_seed=seed)

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = out_path.suffix.lower()

    if suffix == ".json":
        from balance_framework.reporting.formats.json import write_suite
        write_suite(result.suite, out_path)
        click.echo(f"JSON suite written to {out_path}")
    elif suffix == ".md":
        md = format_suite_markdown(result.suite, title=f"{label} — Level {level} Balance Report")
        out_path.write_text(md, encoding="utf-8")
        click.echo(f"Markdown report written to {out_path}")
    else:
        report = format_report(result.suite, title=f"{label} — Level {level}")
        out_path.write_text(report, encoding="utf-8")
        click.echo(report)
        click.echo(f"Text report written to {out_path}")

    # Always print summary to console
    wr = result.suite.win_rate("party")
    ar = result.suite.avg_rounds
    click.echo(f"\nSummary: win rate = {wr:.1%}, avg rounds = {ar:.1f}")
