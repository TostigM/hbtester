"""CLI entry point for the balance framework."""

from __future__ import annotations

from pathlib import Path

import click

from balance_framework.cli.validate_commands import validate
from balance_framework.cli.test_commands import test
from balance_framework.cli.baseline_commands import generate_baseline


@click.group()
@click.version_option()
def main() -> None:
    """D&D Homebrew Balance Framework — test homebrew content for balance."""


main.add_command(validate)
main.add_command(test)
main.add_command(generate_baseline)


@main.command(name="build-character")
@click.option(
    "--class", "class_id", required=True,
    help="Class ID (e.g. fighter, cleric, wizard, rogue).",
)
@click.option("--subclass", "subclass_id", default=None, help="Subclass ID.")
@click.option("--level", default=5, show_default=True, help="Character level.")
@click.option(
    "--content-dir", default="content", show_default=True,
    type=click.Path(file_okay=False),
    help="Path to the content directory.",
)
def build_character_cmd(
    class_id: str, subclass_id: str | None, level: int, content_dir: str
) -> None:
    """Build and inspect a character at a given level (debug tool)."""
    from balance_framework.registry.loader import load_content_directory
    from balance_framework.registry.registry import ContentRegistry
    from balance_framework.registry.character_builder import CharacterBuild, build_character
    from balance_framework.cli.test_commands import _CLASS_DEFAULTS

    defaults = _CLASS_DEFAULTS.get(class_id)
    if defaults is None:
        raise click.ClickException(
            f"No default build for class {class_id!r}. "
            f"Supported: {sorted(_CLASS_DEFAULTS)}"
        )

    registry = ContentRegistry(load_content_directory(Path(content_dir)))
    build = CharacterBuild(class_id=class_id, subclass_id=subclass_id, level=level, **defaults)
    char = build_character(build, registry)

    click.echo(f"\n{'='*40}")
    click.echo(f"  {class_id.capitalize()}")
    if subclass_id:
        click.echo(f"  Subclass : {subclass_id}")
    click.echo(f"  Level    : {level}")
    click.echo(f"{'='*40}")
    click.echo(f"  HP       : {char.hp_max}")
    click.echo(f"  AC       : {char.ac}")
    click.echo(f"  Prof     : +{char.proficiency_bonus}")
    mods = {k: v for k, v in char.ability_modifiers.items() if v != 0}
    click.echo(f"  Ability mods: {mods}")
    if char.spell_save_dc:
        click.echo(f"  Spell DC : {char.spell_save_dc}")
    if char.sneak_attack_dice:
        click.echo(f"  Sneak attack: {char.sneak_attack_dice}d6")
    if char.extra_attack_count > 0:
        click.echo(f"  Extra attack count: {char.extra_attack_count}")
    features = [f.display_name for f in char.active_features[:8]]
    click.echo(f"  Features : {', '.join(features)}")
