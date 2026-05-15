"""Per-content-type validation functions.

Each function accepts a raw dict (typically parsed from YAML), validates it
against the corresponding Pydantic model, and returns the typed model instance.

Pydantic's ValidationError is caught and re-raised as either:
  - VocabularyViolation  when all errors are vocabulary violations (tagged with [VOCAB])
  - SchemaViolation      for structural errors (missing fields, wrong types, etc.)

This keeps the schema layer's public contract independent of Pydantic internals.
"""

from __future__ import annotations

from typing import Any

import pydantic

from balance_framework.schema.exceptions import SchemaViolation, VocabularyViolation
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


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _format_errors(errors: list[dict[str, Any]]) -> str:
    """Return a human-readable summary of Pydantic validation errors."""
    lines: list[str] = []
    for err in errors:
        loc = " -> ".join(str(p) for p in err.get("loc", []))
        msg = err.get("msg", "unknown error")
        lines.append(f"  {loc}: {msg}" if loc else f"  {msg}")
    return "\n".join(lines)


def _classify_and_raise(exc: pydantic.ValidationError, content_type: str) -> None:
    """Re-raise a Pydantic ValidationError as the appropriate custom exception."""
    errors = exc.errors()
    all_vocab = all(err.get("msg", "").find("[VOCAB]") != -1 for err in errors)
    summary = _format_errors(errors)
    if all_vocab:
        raise VocabularyViolation(
            f"Vocabulary violation in {content_type}:\n{summary}"
        ) from exc
    raise SchemaViolation(
        f"Schema violation in {content_type}:\n{summary}"
    ) from exc


# ---------------------------------------------------------------------------
# Public validators
# ---------------------------------------------------------------------------


def validate_class(data: dict[str, Any]) -> Class:
    """Validate a raw dict as a Class content object."""
    try:
        return Class.model_validate(data)
    except pydantic.ValidationError as exc:
        _classify_and_raise(exc, "class")
        raise  # unreachable; satisfies mypy


def validate_subclass(data: dict[str, Any]) -> Subclass:
    """Validate a raw dict as a Subclass content object."""
    try:
        return Subclass.model_validate(data)
    except pydantic.ValidationError as exc:
        _classify_and_raise(exc, "subclass")
        raise


def validate_species(data: dict[str, Any]) -> Species:
    """Validate a raw dict as a Species content object."""
    try:
        return Species.model_validate(data)
    except pydantic.ValidationError as exc:
        _classify_and_raise(exc, "species")
        raise


def validate_background(data: dict[str, Any]) -> Background:
    """Validate a raw dict as a Background content object."""
    try:
        return Background.model_validate(data)
    except pydantic.ValidationError as exc:
        _classify_and_raise(exc, "background")
        raise


def validate_spell(data: dict[str, Any]) -> Spell:
    """Validate a raw dict as a Spell content object."""
    try:
        return Spell.model_validate(data)
    except pydantic.ValidationError as exc:
        _classify_and_raise(exc, "spell")
        raise


def validate_magic_item(data: dict[str, Any]) -> MagicItem:
    """Validate a raw dict as a MagicItem content object."""
    try:
        return MagicItem.model_validate(data)
    except pydantic.ValidationError as exc:
        _classify_and_raise(exc, "magic_item")
        raise


def validate_monster(data: dict[str, Any]) -> Monster:
    """Validate a raw dict as a Monster content object."""
    try:
        return Monster.model_validate(data)
    except pydantic.ValidationError as exc:
        _classify_and_raise(exc, "monster")
        raise


def validate_feat(data: dict[str, Any]) -> Feat:
    """Validate a raw dict as a Feat content object."""
    try:
        return Feat.model_validate(data)
    except pydantic.ValidationError as exc:
        _classify_and_raise(exc, "feat")
        raise
