"""Caricamento, svuotamento e salvataggio del template .dungeondraft_map.

Il generatore non costruisce mai il JSON da zero: carica un template reale,
svuota solo le liste disegnabili e ci inietta la geometria generata.
Vedi docs/SPEC.md §2, §6.3. Implementato in TASK-8.
"""

from pathlib import Path
from typing import Sequence


class TemplateError(Exception):
    """Il documento caricato non e un template Dungeondraft valido."""


LEVEL_KEYS = (
    "label", "environment", "layers", "shapes", "tiles", "patterns",
    "walls", "portals", "cave", "terrain", "water", "materials",
    "paths", "objects", "lights", "roofs", "texts",
)

DRAWABLE_LISTS = (
    "patterns", "walls", "portals", "paths", "objects", "lights", "texts",
)


def load_template(path: str | Path) -> dict:
    """Carica il JSON e verifica che sia un documento Dungeondraft valido."""
    raise NotImplementedError


def blank_level(level: dict) -> dict:
    """Deep copy del livello con solo le liste disegnabili svuotate."""
    raise NotImplementedError


def prepare(doc: dict, *, levels: int = 1, labels: Sequence[str] | None = None) -> dict:
    """Documento pronto per l'injection, con `levels` piani svuotati."""
    raise NotImplementedError


def finalize(doc: dict, ids) -> dict:
    """Aggiorna world.next_node_id. Da chiamare sempre prima di save()."""
    raise NotImplementedError


def save(doc: dict, path: str | Path) -> None:
    """json.dump con indent=2, ensure_ascii=False, encoding utf-8."""
    raise NotImplementedError
