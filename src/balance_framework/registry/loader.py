"""Content directory loader — walks YAML files, validates, and returns typed objects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from balance_framework.schema.exceptions import ValidationError
from balance_framework.schema.types import (
    Background,
    Class,
    Feat,
    MagicItem,
    Monster,
    Species,
    Spell,
    Subclass,
)
from balance_framework.schema.validators import (
    validate_background,
    validate_class,
    validate_feat,
    validate_magic_item,
    validate_monster,
    validate_species,
    validate_spell,
    validate_subclass,
)

ContentItem = Class | Subclass | Species | Background | Spell | MagicItem | Monster | Feat

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


def load_content_directory(path: Path) -> list[ContentItem]:
    """Walk *path* recursively, validate every ``*.yaml`` file, and return all content.

    Raises:
        FileNotFoundError: if *path* does not exist.
        ValueError: if any YAML file fails validation (all errors collected, then raised).
    """
    if not path.exists():
        raise FileNotFoundError(f"Content directory not found: {path}")

    yaml_files = sorted(path.rglob("*.yaml"))
    loaded: list[ContentItem] = []
    errors: list[str] = []

    for yaml_path in yaml_files:
        try:
            raw: Any = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{yaml_path}: YAML parse error: {exc}")
            continue

        if not isinstance(raw, dict):
            errors.append(f"{yaml_path}: top-level value must be a YAML mapping")
            continue

        content_type = raw.get("content_type")
        if content_type not in _VALIDATORS:
            errors.append(
                f"{yaml_path}: unknown or missing content_type {content_type!r}"
            )
            continue

        try:
            loaded.append(_VALIDATORS[content_type](raw))
        except ValidationError as exc:
            errors.append(f"{yaml_path}: {exc}")

    if errors:
        raise ValueError(
            f"Content validation failed ({len(errors)} error(s)):\n"
            + "\n".join(f"  * {e}" for e in errors)
        )

    return loaded
