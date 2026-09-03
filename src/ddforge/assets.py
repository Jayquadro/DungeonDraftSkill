"""Catalogo asset: pack, texture e Palette per stile.

Vedi docs/SPEC.md §6.7. `build_catalog`/`load_catalog` implementati in
TASK-4; `Palette`/`palette_for`/`required_packs` in TASK-17.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

# Nomi semantici di SPEC.md §6.7: se una texture osservata li contiene nel
# nome file, riceve anche questa chiave come alias (mai una texture
# inventata: solo un secondo nome per una texture gia reale).
OBJECT_ALIASES = {
    "torch": ("torch",),
    "table_round": ("table_round", "round_table"),
    "chair": ("chair",),
    "bed": ("bed",),
    "crate": ("crate",),
    "barrel": ("barrel",),
    "bookshelf": ("bookshelf",),
    "altar": ("altar",),
    "sarcophagus": ("sarcophagus", "sarcophag"),
    "column": ("column", "pillar"),
    "brazier": ("brazier",),
    "chest": ("chest",),
}


@dataclass
class Palette:
    """Set coerente di texture per un tipo di ambiente."""

    wall: str
    floor: str
    door: str
    accents: dict = field(default_factory=dict)


def _slug(texture_path: str) -> str:
    """Deriva una chiave leggibile dal nome file di una texture res://."""
    stem = texture_path.rsplit("/", 1)[-1]
    stem = re.sub(r"\.(png|webp|jpg|jpeg)$", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"[^a-zA-Z0-9]+", "_", stem).strip("_").lower()
    return stem or "unnamed"


def _classify(texture_path: str) -> str | None:
    """Mappa un path res:// a una categoria del catalogo, o None se non riconosciuto."""
    p = texture_path.lower()
    if "/walls/" in p:
        return "walls"
    if "/patterns/" in p or "/tilesets/" in p:
        return "floors"
    if "/portals/" in p:
        return "portals"
    if "/roofs/" in p:
        return "roofs"
    if "/paths/" in p:
        return "paths"
    if "/objects/" in p:
        return "objects"
    return None


def _iter_textures(doc: dict):
    """Cammina un documento .dungeondraft_map e produce ogni texture usata."""
    levels = doc.get("world", {}).get("levels", {})
    for lvl in levels.values():
        for w in lvl.get("walls", []):
            if w.get("texture"):
                yield w["texture"]
            for portal in w.get("portals", []):
                if portal.get("texture"):
                    yield portal["texture"]
        for portal in lvl.get("portals", []):
            if portal.get("texture"):
                yield portal["texture"]
        for pattern in lvl.get("patterns", []):
            if pattern.get("texture"):
                yield pattern["texture"]
        for obj in lvl.get("objects", []):
            if obj.get("texture"):
                yield obj["texture"]
        for path_el in lvl.get("paths", []):
            if path_el.get("texture"):
                yield path_el["texture"]
        roofs = lvl.get("roofs", {})
        if isinstance(roofs, dict):
            for roof in roofs.get("roofs", []):
                if roof.get("texture"):
                    yield roof["texture"]


def build_catalog(*docs: dict) -> dict:
    """Costruisce il catalogo unendo pack e texture osservate in piu documenti.

    Ogni texture nel risultato e presa letteralmente da uno dei documenti
    passati: nessuna categoria viene mai popolata con un path inventato.
    """
    packs: dict[str, dict] = {}
    buckets: dict[str, dict[str, str]] = {
        "walls": {},
        "floors": {},
        "portals": {},
        "roofs": {},
        "paths": {},
        "objects": {},
    }

    for doc in docs:
        for m in doc.get("header", {}).get("asset_manifest", []) or []:
            pack_id = m.get("id")
            if pack_id:
                packs[pack_id] = {
                    "name": m.get("name"),
                    "id": pack_id,
                    "author": m.get("author"),
                    "version": m.get("version"),
                }
        for texture in _iter_textures(doc):
            category = _classify(texture)
            if category is None:
                continue
            key = _slug(texture)
            buckets[category].setdefault(key, texture)

    for key, texture in list(buckets["objects"].items()):
        for alias, keywords in OBJECT_ALIASES.items():
            if alias in buckets["objects"]:
                continue
            if any(kw in key for kw in keywords):
                buckets["objects"][alias] = texture

    return {
        "packs": [packs[k] for k in sorted(packs)],
        **{name: dict(sorted(bucket.items())) for name, bucket in buckets.items()},
    }


def load_catalog(path="data/assets.json") -> dict:
    """Legge il catalogo asset da file. Solleva FileNotFoundError se manca."""
    catalog_path = Path(path)
    if not catalog_path.exists():
        raise FileNotFoundError(
            f"Catalogo asset non trovato: {catalog_path}. "
            "Generalo con `ddforge catalog --from <template>`."
        )
    with open(catalog_path, encoding="utf-8") as f:
        return json.load(f)


def palette_for(style: str, catalog: dict) -> Palette:
    """style in {dungeon, crypt, sewer, cave, tavern, manor, warehouse, city}."""
    raise NotImplementedError


def required_packs(doc: dict) -> set:
    """Estrae gli ID pack referenziati dalle texture usate nel documento."""
    raise NotImplementedError
