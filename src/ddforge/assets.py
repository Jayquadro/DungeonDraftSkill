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
    # Pavimento per room.kind (TASK-43), stesso meccanismo di _KIND_ACCENT_HINTS
    # in compose.py: solo chiavi gia risolte dal catalogo, mai un path
    # inventato. Un kind assente qui ricade su `floor` (comportamento
    # invariato prima di TASK-43).
    floors: dict = field(default_factory=dict)
    # Opzionali (TASK-27): non tutti gli stili hanno un tetto (un dungeon
    # sotterraneo non ne ha) o un muro portante distinto dai tramezzi.
    roof: str | None = None
    wall_load_bearing: str | None = None
    # Oggetto scala del vano scale (TASK-30). Campo dedicato e non una voce
    # di `accents`: gli accents sono il materiale che furnish sparge nelle
    # stanze a caso, e una scala sbucata in mezzo a una camera da letto e
    # peggio di nessuna scala. Nel gate umano M4 il vano scale era vuoto e
    # Jay non lo riconosceva.
    stairs: str | None = None


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
        # La stanza boss (bsp._assign_boss_room) si distingue anche a
        # pavimento, non solo per dimensione (TASK-43, gate umano M3).
        "floors": {"boss": "tileset_brick_basketweave"},
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
        # "table_round"/"chair" (chiavi TASK-17) puntavano a texture del pack
        # WFWMFRDX, assente da templates/blank_80x80.dungeondraft_map: DDF014
        # su ogni mappa generata da quel template. Sostituite con le varianti
        # equivalenti senza pack (TASK-29, trovato dal test end-to-end).
        "accents": {
            "table": "table_wood_rectangular_small_01", "chair": "chair_wood_01", "barrel": "barrel",
            "bench": "bench_wood_01", "bed": "bed", "oven": "oven_brick_red_a2_2x2",
            # Il retro di una taverna e una dispensa: senza casse e botti
            # riceveva SOLO barili, ed e il "non ci sono arredi se non
            # barili" del gate umano M4 (TASK-30).
            "crate": "crate", "keg": "keg_wood_light_h_1x1",
            "cupboard": "cupboard_wood_light_d_2x1",
        },
        # roof/wall_load_bearing (TASK-30): draw_building li usa solo se
        # presenti (Palette.roof/wall_load_bearing di default None, TASK-27).
        "roof": "tiles", "wall_load_bearing": "stone", "stairs": "stairs_round_08",
        # Cucina e retro sono ambienti di servizio (pavimento pratico, non il
        # legno della sala comune); la camera ha un legno piu curato di
        # quella (TASK-43, richiesto da Jay al gate M3, TASK-26).
        "floors": {
            "cucina": "cobblestone", "retro": "tileset_cobble", "camera": "wooden_flooring_m_light",
        },
    },
    "manor": {
        "wall": "battlements", "floor": "wooden_flooring_m_light", "door": "door_wood_double",
        # "statue" (TASK-17, statue_male_mage_alt_03_a) e solo su WFWMFRDX,
        # senza equivalente senza pack nel catalogo osservato: rimossa invece
        # di lasciare una palette che rompe DDF014 contro il template reale.
        "accents": {
            "table": "table_corner_wood_01", "bookshelf": "bookshelf", "rug": "rug_01",
            "bed": "bed_wood_single_01", "desk": "desk_wood_01", "cupboard": "cupboard_wood_light_d_2x1",
        },
        "roof": "tiles", "wall_load_bearing": "stone_09", "stairs": "stairs_round_08",
        # Le stanze private hanno un legno piu semplice della fascia di
        # rappresentanza; la servitu' un pavimento utilitario (TASK-43).
        "floors": {"privato": "wood_planks", "servitu": "tileset_cobble"},
    },
    "warehouse": {
        "wall": "concrete", "floor": "cobblestone", "door": "door_02",
        "accents": {
            "crate": "crate", "barrel": "barrel", "keg": "keg_wood_light_h_1x1",
            "cupboard": "cupboard_wood_light_d_2x1",
        },
        "roof": "tiles", "wall_load_bearing": "stone", "stairs": "stairs_round_04",
        # Il soppalco e in legno, sopra il pavimento in pietra del piano
        # terra (TASK-43).
        "floors": {"soppalco": "wood_planks"},
    },
    "city": {
        "wall": "cobble", "floor": "cobblestone", "door": "threshold_01",
        "accents": {"fountain": "fountain_stone_01"},
        # Serve a draw_building per gli edifici di generators/city.py
        # (TASK-35): senza, palette_for("city").roof e None e nessun tetto
        # verrebbe disegnato (SPEC.md §9.4 lo vuole su ogni edificio,
        # "si vede dall'alto").
        "roof": "tiles",
        # "piazza" non e un Room.kind (le piazze non sono Room, TASK-35):
        # riusa lo stesso meccanismo di Palette.floors con una chiave
        # sintetica, cosi la piazza ha una pavimentazione diversa dal
        # cobblestone di strade/edifici (SPEC.md §9.4 AC5) senza aggiungere
        # un campo dedicato alla Palette.
        "floors": {"piazza": "tileset_brick_basketweave"},
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
    floors = {kind: _lookup(catalog, "floors", key) for kind, key in definition.get("floors", {}).items()}
    roof = _lookup(catalog, "roofs", definition["roof"]) if "roof" in definition else None
    wall_load_bearing = (
        _lookup(catalog, "walls", definition["wall_load_bearing"]) if "wall_load_bearing" in definition else None
    )
    stairs = _lookup(catalog, "objects", definition["stairs"]) if "stairs" in definition else None
    return Palette(
        wall=wall, floor=floor, door=door, accents=accents, floors=floors, roof=roof,
        wall_load_bearing=wall_load_bearing, stairs=stairs,
    )


def required_packs(doc: dict) -> set:
    """Estrae gli ID pack referenziati dalle texture usate nel documento."""
    ids = set()
    for texture in _iter_textures(doc):
        if texture.startswith("res://packs/"):
            parts = texture.split("/")
            if len(parts) >= 4:
                ids.add(parts[3])
    return ids
