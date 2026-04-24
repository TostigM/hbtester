"""Cross-reference resolver — validates that IDs in one content object point to real content."""

from __future__ import annotations

from balance_framework.schema.exceptions import ReferenceError as ContentReferenceError
from balance_framework.schema.types import Subclass
from balance_framework.registry.registry import ContentRegistry


def resolve_subclass(subclass: Subclass, registry: ContentRegistry) -> None:
    """Assert that subclass.parent_class exists in the registry.

    Raises ContentReferenceError if the parent class is missing.
    """
    registry.get_class(subclass.parent_class)


def resolve_all_subclasses(registry: ContentRegistry) -> list[str]:
    """Check every loaded subclass for broken parent_class references.

    Returns a list of error strings (empty if all references resolve).
    """
    errors: list[str] = []
    for subclass in registry.get_all_subclasses():
        try:
            resolve_subclass(subclass, registry)
        except ContentReferenceError as exc:
            errors.append(f"Subclass {subclass.id!r}: {exc}")
    return errors


def resolve_spell_references(registry: ContentRegistry) -> list[str]:
    """Check every loaded subclass spell_list for spells that exist in the registry.

    Returns a list of error strings (empty if all references resolve).
    """
    errors: list[str] = []
    for subclass in registry.get_all_subclasses():
        for spell_id in subclass.spell_list:
            try:
                registry.get_spell(spell_id)
            except ContentReferenceError:
                errors.append(
                    f"Subclass {subclass.id!r} spell_list references unknown spell {spell_id!r}"
                )
    return errors
