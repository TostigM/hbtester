"""CLI commands for YAML content validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
import yaml

from balance_framework.schema.exceptions import ValidationError
from balance_framework.schema.validators import (
    validate_background, validate_class, validate_feat, validate_magic_item,
    validate_monster, validate_species, validate_spell, validate_subclass,
)

_VALIDATORS = {
    "class": validate_class,
    "subclass": validate_subclass,
    "species": validate_species,
    "background": validate_background,
    "spell": validate_spell,
    "magic_item": validate_magic_item,
    "monster": validate_monster,
    "feat": validate_feat,
}


def _validate_file(path: Path) -> list[str]:
    try:
        data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return ["File does not contain a YAML mapping"]
    content_type = data.get("content_type")
    if content_type not in _VALIDATORS:
        return [f"Unknown or missing content_type: {content_type!r}"]
    try:
        _VALIDATORS[content_type](data)
    except ValidationError as exc:
        return [str(exc)]
    return []


@click.command()
@click.option(
    "--content-dir", default="content", show_default=True,
    type=click.Path(file_okay=False),
    help="Path to the content directory.",
)
def validate(content_dir: str) -> None:
    """Validate all YAML content files against their schemas."""
    cdir = Path(content_dir)
    if not cdir.exists():
        click.echo(f"Content directory not found: {cdir}", err=True)
        raise SystemExit(1)

    yaml_files = sorted(cdir.rglob("*.yaml"))
    if not yaml_files:
        click.echo(f"No YAML files found in {cdir}")
        raise SystemExit(0)

    errors: list[tuple[Path, list[str]]] = []
    for path in yaml_files:
        file_errors = _validate_file(path)
        if file_errors:
            errors.append((path, file_errors))

    total = len(yaml_files)
    failed = len(errors)
    passed = total - failed
    click.echo(f"Validated {total} files: {passed} passed, {failed} failed")

    for path, errs in errors:
        click.echo(f"\n  FAIL  {path}", err=True)
        for err in errs:
            click.echo(f"        {err}", err=True)

    if errors:
        raise SystemExit(1)
