"""Catalogo asset: pack, texture e Palette per stile.

Vedi docs/SPEC.md §6.7. Implementato in TASK-4 (load_catalog/catalog CLI) e
TASK-17 (Palette, palette_for, required_packs).
"""

from dataclasses import dataclass, field


@dataclass
class Palette:
    """Set coerente di texture per un tipo di ambiente."""

    wall: str
    floor: str
    door: str
    accents: dict = field(default_factory=dict)


def load_catalog(path="data/assets.json") -> dict:
    raise NotImplementedError


def palette_for(style: str, catalog: dict) -> Palette:
    """style in {dungeon, crypt, sewer, cave, tavern, manor, warehouse, city}."""
    raise NotImplementedError


def required_packs(doc: dict) -> set:
    """Estrae gli ID pack referenziati dalle texture usate nel documento."""
    raise NotImplementedError
