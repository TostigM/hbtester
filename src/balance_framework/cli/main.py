"""CLI entry point for the balance framework."""

import click


@click.group()
@click.version_option()
def main() -> None:
    """D&D Homebrew Balance Framework — test homebrew content for balance."""


@main.group()
def test() -> None:
    """Run balance tests against homebrew content."""


@main.command()
def validate() -> None:
    """Validate all YAML content files against their schemas."""
    click.echo("Validation not yet implemented (Phase 2, M1).")


@main.command(name="generate-baseline")
def generate_baseline() -> None:
    """Generate the WotC baseline reference documents."""
    click.echo("Baseline generation not yet implemented (Phase 2, M9).")


@main.command(name="build-character")
def build_character() -> None:
    """Build and inspect a character at a given level (debug tool)."""
    click.echo("Character builder not yet implemented (Phase 2, M2).")
