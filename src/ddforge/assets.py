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
    """Legge il catalogo asset da file. Fallisce con messaggio esplicito
    se il file manca o non e JSON valido."""
    catalog_path = Path(path)
    if not catalog_path.exists():
        raise FileNotFoundError(
            f"Catalogo asset non trovato: {catalog_path}. "
            "Generalo con `ddforge catalog --from <template>`."
        )
    with open(catalog_path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Catalogo asset non e JSON valido: {catalog_path} ({exc})") from exc


# Ogni voce e (categoria, chiave) dentro il catalogo di data/assets.json,
# verificate a mano contro le chiavi realmente presenti (TASK-4): mai
# inventare una chiave che potrebbe non esistere in una rigenerazione futura
# del catalogo, in tal caso palette_for fallisce esplicitamente (AC5).
_STYLE_DEFINITIONS: dict[str, dict] = {
    "dungeon": {
        "wall": "stone", "floor": "stone_floor", "door": "door_iron",
        "accents": {"brazier": "brazier", "crate": "crate", "barrel": "barrel"},
    },
    "crypt": {
        "wall": "stone_09", "floor": "stone_floor", "door": "door_secret",
        "accents": {"skeleton": "skeleton_04", "grave": "skeleton_grave_02", "brazier": "brazier"},
    },
    "sewer": {
        "wall": "concrete", "floor": "cobblestone", "door": "portcullis",
        "accents": {"barrel": "barrel", "cage": "cage_04"},
    },
    "cave": {
        "wall": "stone", "floor": "stone_floor", "door": "archway",
        "accents": {},
    },
    "tavern": {
        "wall": "wood_04", "floor": "wood_planks", "door": "door_wood_single",
        "accents": {"table_round": "table_round", "chair": "chair", "barrel": "barrel", "bench": "bench_wood_01"},
    },
    "manor": {
        "wall": "battlements", "floor": "wooden_flooring_m_light", "door": "door_wood_double",
        "accents": {"table_round": "table_round", "bookshelf": "bookshelf", "rug": "rug_01", "statue": "statue_male_mage_alt_03_a"},
    },
    "warehouse": {
        "wall": "concrete", "floor": "cobblestone", "door": "door_02",
        "accents": {"crate": "crate", "barrel": "barrel", "keg": "keg_wood_light_h_1x1"},
    },
    "city": {
        "wall": "cobble", "floor": "cobblestone", "door": "threshold_01",
        "accents": {"fountain": "fountain_stone_01"},
    },
}


def _lookup(catalog: dict, category: str, key: str) -> str:
    bucket = catalog.get(category)
    if not isinstance(bucket, dict) or key not in bucket:
        raise ValueError(
            f"Chiave {key!r} assente da catalog[{category!r}]: rigenera data/assets.json "
            "con `ddforge catalog` includendo un documento che la contenga"
        )
    return bucket[key]


def palette_for(style: str, catalog: dict) -> Palette:
    """style in {dungeon, crypt, sewer, cave, tavern, manor, warehouse, city}."""
    definition = _STYLE_DEFINITIONS.get(style)
    if definition is None:
        raise ValueError(f"Stile sconosciuto: {style!r}. Stili validi: {sorted(_STYLE_DEFINITIONS)}")

    wall = _lookup(catalog, "walls", definition["wall"])
    floor = _lookup(catalog, "floors", definition["floor"])
    door = _lookup(catalog, "portals", definition["door"])
    accents = {name: _lookup(catalog, "objects", key) for name, key in definition["accents"].items()}
    return Palette(wall=wall, floor=floor, door=door, accents=accents)


def required_packs(doc: dict) -> set:
    """Estrae gli ID pack referenziati dalle texture usate nel documento."""
    ids = set()
    for texture in _iter_textures(doc):
        if texture.startswith("res://packs/"):
            parts = texture.split("/")
            if len(parts) >= 4:
                ids.add(parts[3])
    return ids
