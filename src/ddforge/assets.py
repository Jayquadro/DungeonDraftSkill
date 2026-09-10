"""Catalogo asset: pack, texture e Palette per stile.

Vedi docs/SPEC.md §6.7. `build_catalog`/`load_catalog` implementati in
TASK-4; `Palette`/`palette_for`/`required_packs` in TASK-17;
`read_dungeondraft_pack` (lettura diretta dei file .dungeondraft_pack) in
TASK-46.
"""

import json
import re
import struct
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
    # Sprite edificio dei preset di scala astratti "quartiere"/"citta"
    # (TASK-46): una texture, non una sola (a differenza di `accents`), perche
    # compose.draw_city_building ne sceglie una a caso per lotto per dare
    # varieta. (texture, larghezza_px, altezza_px): le dimensioni servono a
    # calcolare la scala di piazzamento (Dungeondraft usa i pixel nativi a
    # scala 1, 256 px/quadretto) e non sono ricavabili da un
    # .dungeondraft_map, solo da catalog["object_sizes"] (TASK-46,
    # read_dungeondraft_pack). Vuoto per ogni stile diverso da "city".
    building_variants: list = field(default_factory=list)
    # Tinte ARGB fisse per variare custom_color (il pack e "Colorable": senza
    # variarlo ogni edificio avrebbe lo stesso tetto). Non sono chiavi del
    # catalogo (non sono texture, solo colori scelti a mano): vuoto per ogni
    # stile diverso da "city".
    building_colors: tuple = ()


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


_PCK_MAGIC = b"GDPC"
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_PACK_MANIFEST_RE = re.compile(r"res://packs/[^/]+\.json")


def _read_pck_entries(data: bytes) -> dict[str, tuple[int, int]]:
    """Indice path -> (offset, size) di un file .dungeondraft_pack (Godot PCK).

    Formato verificato sul file reale di Jay (BB-51-Assets-Houses1, Godot
    3.2.1): magic 'GDPC', pack_version(int32), 3x int32 versione Godot, 16x
    int32 riservati (64 byte), file_count(int32), poi per ogni entry
    path_len(uint32)+path(padded)+offset(uint64)+size(uint64)+md5(16 byte),
    tutto little-endian. Gli offset sono assoluti nel file (nessun base_offset:
    quello serve solo al formato con embedding di Godot 4, non usato qui).
    Solo pack_version 1 e supportato (l'unico osservato); altre versioni
    falliscono esplicitamente invece di essere lette a caso.
    """
    if data[:4] != _PCK_MAGIC:
        raise ValueError("Non e un file .dungeondraft_pack valido (magic GDPC assente)")
    off = 4
    (pack_version,) = struct.unpack_from("<i", data, off)
    off += 16  # pack_version gia consumato sopra: qui i 3 int32 di versione Godot
    if pack_version != 1:
        raise ValueError(
            f"Formato .dungeondraft_pack non supportato (pack_version={pack_version}, atteso 1)"
        )
    off += 64  # 16 int32 riservati
    (file_count,) = struct.unpack_from("<i", data, off)
    off += 4

    entries: dict[str, tuple[int, int]] = {}
    for _ in range(file_count):
        (path_len,) = struct.unpack_from("<I", data, off)
        off += 4
        path = data[off : off + path_len].rstrip(b"\x00").decode("utf-8")
        off += path_len
        offset, size = struct.unpack_from("<QQ", data, off)
        off += 16 + 16  # offset+size gia letti sopra, poi 16 byte di md5
        entries[path] = (offset, size)
    return entries


def read_dungeondraft_pack(path) -> dict:
    """Legge un file .dungeondraft_pack ed estrae manifest e dimensioni pixel.

    Necessario per AC1 di TASK-46: un .dungeondraft_map non porta le
    dimensioni native delle texture, indispensabili per calcolare la scala di
    piazzamento di un object (vedi Palette.building_variants). Ritorna
    {"manifest": {id, name, author, version, ...}, "textures": {res_path:
    (width_px, height_px)}}. Solo i file .png sotto res://packs/<id>/ ricevono
    una dimensione (letta dall'IHDR): nessuna texture di questo pack e in un
    altro formato, e leggere le dimensioni di un WebP richiederebbe un parser
    diverso, fuori scope.
    """
    with open(path, "rb") as f:
        data = f.read()
    entries = _read_pck_entries(data)

    manifest_paths = [p for p in entries if _PACK_MANIFEST_RE.fullmatch(p)]
    if not manifest_paths:
        raise ValueError(f"Manifest del pack (res://packs/<id>.json) non trovato in {path}")
    offset, size = entries[manifest_paths[0]]
    manifest = json.loads(data[offset : offset + size].decode("utf-8"))
    pack_id = manifest.get("id")

    textures: dict[str, tuple[int, int]] = {}
    prefix = f"res://packs/{pack_id}/"
    for entry_path, (offset, size) in entries.items():
        if not entry_path.startswith(prefix) or not entry_path.lower().endswith(".png"):
            continue
        header = data[offset : offset + 24]
        if header[:8] != _PNG_MAGIC:
            continue
        width, height = struct.unpack_from(">II", header, 16)
        textures[entry_path] = (width, height)

    return {"manifest": manifest, "textures": textures}


def build_catalog(*docs: dict, pack_sources=()) -> dict:
    """Costruisce il catalogo unendo pack e texture osservate in piu documenti,
    piu (TASK-46) le texture lette direttamente da file .dungeondraft_pack via
    `read_dungeondraft_pack`.

    Ogni texture nel risultato e presa letteralmente da uno dei documenti o
    pack passati: nessuna categoria viene mai popolata con un path inventato.
    Vincolo non negoziabile: una texture di un pack_source il cui id non
    compare nell'asset_manifest di nessun documento --from e rifiutata con un
    errore esplicito, mai inclusa in silenzio (altrimenti DDF014 romperebbe
    ogni mappa generata dal template di produzione, che non conosce quel
    pack).
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

    object_sizes: dict[str, list[int]] = {}
    for pack_source in pack_sources:
        pack_id = pack_source["manifest"].get("id")
        if pack_id not in packs:
            raise ValueError(
                f"Pack {pack_id!r} (da --pack) assente da header.asset_manifest dei "
                "template --from: aggiungi un --from che lo referenzi prima di leggere "
                "il file .dungeondraft_pack"
            )
        for texture, (width, height) in pack_source["textures"].items():
            category = _classify(texture)
            if category is None:
                continue
            key = _slug(texture)
            buckets[category].setdefault(key, texture)
            object_sizes.setdefault(key, [width, height])

    for key, texture in list(buckets["objects"].items()):
        for alias, keywords in OBJECT_ALIASES.items():
            if alias in buckets["objects"]:
                continue
            if any(kw in key for kw in keywords):
                buckets["objects"][alias] = texture

    return {
        "packs": [packs[k] for k in sorted(packs)],
        **{name: dict(sorted(bucket.items())) for name, bucket in buckets.items()},
        "object_sizes": dict(sorted(object_sizes.items())),
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
            # "bed" e la chiave letterale (non l'alias "bed"): dopo TASK-45
            # l'alias semantico "bed" puo risolvere a texture di pack diversi
            # a seconda dell'ordine dei --from (il primo file con "bed" nel
            # nome vince), quindi non e piu stabile per una palette gia
            # approvata al gate umano.
            "table": "table_wood_rectangular_small_01", "chair": "chair_wood_01", "barrel": "barrel",
            "bench": "bench_wood_01", "bed": "bed_wood_single_01", "oven": "oven_brick_red_a2_2x2",
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
            # "bookshelf" e la chiave letterale per lo stesso motivo di "bed"
            # in tavern qui sopra: l'alias "bookshelf" non e piu stabile
            # dopo TASK-45.
            "table": "table_corner_wood_01", "bookshelf": "bookshelf_wood_01", "rug": "rug_01",
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


# Sprite edificio del preset "city" (TASK-46): le 33 texture "casa" del pack
# scelto da Jay (6VxwaRdj, "BB 51 Assets Houses1"), chiavi letterali derivate
# da _slug("BB_Houses1_HouseN.png") -> "bb_houses1_housen". Elenco esplicito
# (non un pattern/alias su substring) per lo stesso motivo di "bed"/"bookshelf"
# qui sopra: dopo TASK-45 un match per substring puo agganciarsi in silenzio a
# un pack diverso a seconda dell'ordine dei --from. Tetti/torri/tende/
# balconi/bandiere dello stesso pack restano catalogati (AC1) ma fuori scope
# per il piazzamento di un edificio (AC2 vuole "un object edificio per lotto").
_CITY_BUILDING_KEYS = tuple(f"bb_houses1_house{i}" for i in range(1, 34))

# Tinte ARGB fisse per variare custom_color fra un edificio e l'altro (il pack
# e' "Colorable": senza variarlo ogni sprite avrebbe lo stesso tetto/muro,
# sempre "ff6b3834", il default di Dungeondraft osservato in
# templates/rich_reference.dungeondraft_map). Toni terrosi plausibili per un
# tetto/muro di casa, non colori scelti a caso in tutto lo spazio RGB.
_CITY_BUILDING_COLORS = (
    "ff6b3834",  # bruno-rossiccio (il default del programma)
    "ff8a5a3b",  # bruno chiaro
    "ff5c6b73",  # grigio ardesia
    "ffa9762f",  # ocra/tan
    "ff7a3b3b",  # rosso mattone smorzato
    "ff4f5d4e",  # verde muschio
)


def _lookup(catalog: dict, category: str, key: str) -> str:
    bucket = catalog.get(category)
    if not isinstance(bucket, dict) or key not in bucket:
        raise ValueError(
            f"Chiave {key!r} assente da catalog[{category!r}]: rigenera data/assets.json "
            "con `ddforge catalog` includendo un documento che la contenga"
        )
    return bucket[key]


def _lookup_size(catalog: dict, key: str) -> tuple[float, float]:
    sizes = catalog.get("object_sizes")
    if not isinstance(sizes, dict) or key not in sizes:
        raise ValueError(
            f"Dimensioni pixel assenti per la texture {key!r}: rigenera data/assets.json "
            "con `ddforge catalog --pack <file.dungeondraft_pack>`"
        )
    width, height = sizes[key]
    return float(width), float(height)


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
    building_variants: list = []
    building_colors: tuple = ()
    if style == "city":
        building_variants = [
            (_lookup(catalog, "objects", key), *_lookup_size(catalog, key)) for key in _CITY_BUILDING_KEYS
        ]
        building_colors = _CITY_BUILDING_COLORS
    return Palette(
        wall=wall, floor=floor, door=door, accents=accents, floors=floors, roof=roof,
        wall_load_bearing=wall_load_bearing, stairs=stairs,
        building_variants=building_variants, building_colors=building_colors,
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
