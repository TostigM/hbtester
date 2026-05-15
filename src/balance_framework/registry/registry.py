"""ContentRegistry — typed store for all loaded content objects."""

from __future__ import annotations

from balance_framework.schema.exceptions import ReferenceError as ContentReferenceError
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
from balance_framework.registry.loader import ContentItem


class ContentRegistry:
    """Immutable store of validated content, keyed by content type and ID.

    Construct via ``ContentRegistry(load_content_directory(path))``.
    """

    def __init__(self, content: list[ContentItem]) -> None:
        self._classes: dict[str, Class] = {}
        self._subclasses: dict[str, Subclass] = {}
        self._species: dict[str, Species] = {}
        self._backgrounds: dict[str, Background] = {}
        self._spells: dict[str, Spell] = {}
        self._magic_items: dict[str, MagicItem] = {}
        self._monsters: dict[str, Monster] = {}
        self._feats: dict[str, Feat] = {}

        for item in content:
            match item.content_type:
                case "class":
                    self._classes[item.id] = item  # type: ignore[arg-type]
                case "subclass":
                    self._subclasses[item.id] = item  # type: ignore[arg-type]
                case "species":
                    self._species[item.id] = item  # type: ignore[arg-type]
                case "background":
                    self._backgrounds[item.id] = item  # type: ignore[arg-type]
                case "spell":
                    self._spells[item.id] = item  # type: ignore[arg-type]
                case "magic_item":
                    self._magic_items[item.id] = item  # type: ignore[arg-type]
                case "monster":
                    self._monsters[item.id] = item  # type: ignore[arg-type]
                case "feat":
                    self._feats[item.id] = item  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def get_class(self, id: str) -> Class:
        return self._lookup(self._classes, id, "class")

    def get_subclass(self, id: str) -> Subclass:
        return self._lookup(self._subclasses, id, "subclass")

    def get_species(self, id: str) -> Species:
        return self._lookup(self._species, id, "species")

    def get_background(self, id: str) -> Background:
        return self._lookup(self._backgrounds, id, "background")

    def get_spell(self, id: str) -> Spell:
        return self._lookup(self._spells, id, "spell")

    def get_magic_item(self, id: str) -> MagicItem:
        return self._lookup(self._magic_items, id, "magic_item")

    def get_monster(self, id: str) -> Monster:
        return self._lookup(self._monsters, id, "monster")

    def get_feat(self, id: str) -> Feat:
        return self._lookup(self._feats, id, "feat")

    # ------------------------------------------------------------------
    # Enumeration helpers
    # ------------------------------------------------------------------

    def get_all_classes(self) -> list[Class]:
        return list(self._classes.values())

    def get_all_subclasses(self) -> list[Subclass]:
        return list(self._subclasses.values())

    def get_all_species(self) -> list[Species]:
        return list(self._species.values())

    def get_all_backgrounds(self) -> list[Background]:
        return list(self._backgrounds.values())

    def get_all_spells(self) -> list[Spell]:
        return list(self._spells.values())

    def get_all_magic_items(self) -> list[MagicItem]:
        return list(self._magic_items.values())

    def get_all_monsters(self) -> list[Monster]:
        return list(self._monsters.values())

    def get_all_feats(self) -> list[Feat]:
        return list(self._feats.values())

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _lookup(store: dict[str, object], id: str, type_label: str) -> object:  # type: ignore[return]
        if id not in store:
            available = sorted(store)
            raise ContentReferenceError(
                f"No {type_label} found with id {id!r}. "
                f"Available {type_label}s: {available}"
            )
        return store[id]

    def __repr__(self) -> str:  # pragma: no cover
        counts = {
            "classes": len(self._classes),
            "subclasses": len(self._subclasses),
            "species": len(self._species),
            "backgrounds": len(self._backgrounds),
            "spells": len(self._spells),
            "magic_items": len(self._magic_items),
            "monsters": len(self._monsters),
            "feats": len(self._feats),
        }
        return f"ContentRegistry({counts})"
