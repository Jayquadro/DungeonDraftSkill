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
    # Texture della categoria `paths` del catalogo, per nome semantico
    # (TASK-48): "mura", "fiume", "banchina". Campo a se e non voci di
    # `accents` perche un path non e un object: si disegna con add_path lungo
    # una polilinea, non si piazza in un punto. Vuoto per gli stili che non
    # disegnano strutture urbane.
    paths: dict = field(default_factory=dict)
    # Sprite dei luoghi urbani notevoli (TASK-48), per CHIAVE DI LUOGO
    # (LandmarkKind.key) e non per nome di icona: un luogo si disegna con lo
    # sprite di quel luogo, punto. Ogni voce e una lista di
    # (texture, larghezza_px, altezza_px) come building_variants, perche il
    # piazzamento ha bisogno delle dimensioni native per calcolare la scala e
    # perche piu varianti danno varieta fra un'istanza e l'altra.
    landmark_sprites: dict = field(default_factory=dict)


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
    # Le texture di terreno sono un bucket a se (TASK-48): servono per le aree
    # colorate dei luoghi all'aperto (l'erba di un parco, la terra battuta di
    # una fiera) e nei pattern non ci sono - i pack le mettono sotto
    # /terrain/. Categoria separata da "floors" perche' NON e' verificato che
    # Dungeondraft accetti una texture di terreno dentro un elemento
    # `pattern`: tenerle distinte rende la differenza visibile invece di
    # nasconderla dietro un nome comune.
    if "/terrain/" in p:
        return "terrain"
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
# res://.import/<nome originale>-<md5>.stex: e' cosi che Godot archivia una
# texture importata, col nome del file sorgente dentro il nome dell'archivio.
_STEX_RE = re.compile(r"res://\.import/(.+)-[0-9a-f]{32}\.stex")


def _image_size(blob: bytes) -> tuple[int, int] | None:
    """Dimensioni in pixel di un PNG o di un WebP, dai soli header.

    Serve perche le dimensioni native di uno sprite decidono la scala di
    piazzamento (TASK-46) e non sono ricavabili da un .dungeondraft_map. Solo
    stdlib: il core del progetto non dipende da Pillow (SPEC.md §4).

    WebP e' arrivato con TASK-48: le texture base di Dungeondraft sono tutte
    WebP dentro i .stex, e finche si leggeva il solo PNG restavano senza
    misura. Tre varianti del formato, tutte e tre necessarie perche il
    programma le usa tutte: VP8X (esteso), VP8L (lossless), VP8 (lossy).
    """
    if blob[:8] == _PNG_MAGIC:
        width, height = struct.unpack_from(">II", blob, 16)
        return width, height
    if blob[:4] != b"RIFF" or blob[8:12] != b"WEBP":
        return None
    chunk = blob[12:16]
    if chunk == b"VP8X":
        # Larghezza e altezza su 24 bit little-endian, meno uno.
        w = int.from_bytes(blob[24:27], "little") + 1
        h = int.from_bytes(blob[27:30], "little") + 1
        return w, h
    if chunk == b"VP8L":
        bits = int.from_bytes(blob[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8 ":
        # Frame header: 3 byte di tag, i 3 byte di start code 9d 01 2a, poi
        # larghezza e altezza su 14 bit ciascuna.
        if blob[23:26] != b"\x9d\x01\x2a":
            return None
        w, h = struct.unpack_from("<HH", blob, 26)
        return w & 0x3FFF, h & 0x3FFF
    return None


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
        if not entry_path.startswith(prefix):
            continue
        if not entry_path.lower().endswith((".png", ".webp")):
            continue
        size_px = _image_size(data[offset : offset + 64])
        if size_px is not None:
            textures[entry_path] = size_px

    return {"manifest": manifest, "textures": textures}


def read_base_pack(path, prefixes) -> dict:
    """Texture BASE del programma, lette da Dungeondraft.pck (TASK-48).

    Non sono texture di un pack: appartengono all'eseguibile, quindi non
    compaiono in nessun `asset_manifest` e non possono mai far scattare
    DDF014. Sono le piu' sicure che ci siano, ed e' per questo che vale la
    pena pescarle: il programma ne ha oltre duemila, fra cui intere famiglie
    (per esempio `objects/graveyard/`) che nessun template di Jay usa e che
    quindi non erano mai finite in catalogo.

    `prefixes` e' obbligatorio e senza default: si dichiara quali cartelle
    importare, una alla volta. Prendere tutto raddoppierebbe il catalogo con
    duemila voci che nessuno ha chiesto, e la disciplina del progetto e'
    che ogni texture in catalogo ci sia perche qualcuno l'ha voluta.

    Il pck base non archivia le texture al loro path: le mette in
    `res://.import/<nome>-<md5>.stex`, un contenitore Godot con dentro
    l'immagine vera. Il path di destinazione si ricostruisce dai fratelli
    `<path>.import`, che invece stanno al posto giusto.
    """
    with open(path, "rb") as f:
        data = f.read()
    entries = _read_pck_entries(data)

    # nome file originale -> path res:// di destinazione
    destinations = {}
    for entry_path in entries:
        if not entry_path.endswith(".import"):
            continue
        real = entry_path[: -len(".import")]
        if any(real.startswith(prefix) for prefix in prefixes):
            destinations[real.rsplit("/", 1)[-1]] = real

    textures: dict[str, tuple[int, int]] = {}
    for entry_path, (offset, size) in entries.items():
        match = _STEX_RE.fullmatch(entry_path)
        if match is None:
            continue
        destination = destinations.get(match.group(1))
        if destination is None:
            continue
        blob = data[offset : offset + size]
        # L'immagine e' incorporata dopo l'intestazione del .stex: la si
        # trova dal suo magic invece che da un offset fisso, che cambia con
        # la versione del formato.
        start = blob.find(_PNG_MAGIC)
        if start < 0:
            start = blob.find(b"RIFF")
        if start < 0:
            continue
        size_px = _image_size(blob[start : start + 64])
        if size_px is not None:
            textures[destination] = size_px

    return {"textures": textures}


def _pack_of(texture: str) -> str | None:
    """Id del pack a cui appartiene una texture res://packs/<id>/..., o None
    per le texture base del programma."""
    if not texture.startswith("res://packs/"):
        return None
    parts = texture.split("/")
    return parts[3] if len(parts) >= 4 else None


def build_catalog(*docs: dict, pack_sources=(), base: dict | None = None, base_pack: dict | None = None) -> dict:
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

    `base` (TASK-48) e un catalogo gia esistente da cui ripartire, e le sue
    chiavi vincono su tutto il resto. Serve perche il catalogo di TASK-45/46
    era stato costruito anche da undici mappe della campagna di Jay che non
    sono piu sul disco: rigenerarlo dai soli template perderebbe una novantina
    di chiavi che le palette usano per nome, e con loro gli stili tavern,
    manor e warehouse. Il vincolo sul pack orfano vale identico per `base`:
    una sua texture che punta a un pack assente dai manifest dei --from e un
    errore, non un'eredita da tenersi.
    """
    packs: dict[str, dict] = {}
    buckets: dict[str, dict[str, str]] = {
        "walls": {},
        "floors": {},
        "portals": {},
        "roofs": {},
        "paths": {},
        "objects": {},
        "terrain": {},
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

    # Il catalogo di partenza si innesta DOPO i documenti ma con setdefault,
    # quindi in pratica vince: le sue chiavi ci sono gia tutte e i documenti
    # non le sovrascrivono. E' l'ordine giusto perche i pack dei documenti
    # devono comunque essere noti prima del controllo sul pack orfano.
    if base is not None:
        for category, bucket in buckets.items():
            for key, texture in (base.get(category) or {}).items():
                orphan = _pack_of(texture)
                if orphan is not None and orphan not in packs:
                    raise ValueError(
                        f"La texture {key!r} del catalogo di partenza appartiene al pack "
                        f"{orphan!r}, assente da header.asset_manifest dei documenti --from: "
                        "aggiungi un --from che lo referenzi, oppure togli quella texture "
                        "dal catalogo"
                    )
                bucket.setdefault(key, texture)
        object_sizes.update(base.get("object_sizes") or {})

    # Le texture base del programma (TASK-48) non appartengono a nessun pack,
    # quindi saltano il controllo sull'orfano: non possono far scattare
    # DDF014 nemmeno in teoria.
    if base_pack is not None:
        for texture, (width, height) in base_pack["textures"].items():
            category = _classify(texture)
            if category is None:
                continue
            key = _slug(texture)
            buckets[category].setdefault(key, texture)
            object_sizes.setdefault(key, [width, height])

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
        # un campo dedicato alla Palette. Stessa cosa per le tre chiavi
        # sintetiche di TASK-48: lo spiazzo di un luogo all'aperto, la
        # banchina del porto e l'impalcato di un ponte.
        "floors": {
            "piazza": "tileset_brick_basketweave", "selciato": "tileset_cobble",
            # Non "cobblestone": e gia' `floor` di questo stile, e una
            # banchina indistinguibile dal pavimento di default non si
            # riconosce come banchina (ne' in Dungeondraft ne' in un test).
            "banchina": "stone_floor", "ponte": "wood_planks",
        },
        # TASK-48: il terreno steso sotto gli sprite di un luogo all'aperto.
        # Viene dalla categoria `terrain` del catalogo e non da `floors`
        # perche' nei pattern l'erba e la terra battuta non ci sono: i pack le
        # mettono sotto /terrain/. Finiscono comunque in Palette.floors, che
        # e' il dizionario da cui compose pesca una texture di pavimento.
        #
        # NON VERIFICATO che Dungeondraft accetti una texture di categoria
        # terrain dentro un elemento `pattern`. L'indizio a favore: il
        # template ricco disegnato a mano da Jay usa come pattern texture di
        # `tilesets/simple/`, quindi lo strumento non si limita a
        # `patterns/normal/`. La conferma sta nel file di calibrazione
        # generato da scripts/label_calibration.py, che stende una toppa per
        # ciascuna di queste texture.
        "grounds": {"verde": "chr_grass", "terra": "chr_dirt"},
        # TASK-48: le tre strutture urbane che si disegnano come path lungo
        # una polilinea. Tutte e tre dal pack 6VxwaRdj, gia' referenziato dal
        # template di produzione (nessun rischio DDF014).
        "paths": {"mura": "bb_wall_path", "fiume": "bb_river_path", "banchina": "bb_shore_path"},
    },
}


# Sprite dei luoghi urbani notevoli (TASK-48), per chiave di LandmarkKind.
#
# Perche esiste questa tabella: al primo giro un luogo era reso come una
# chiazza di pavimento piu un'iconcina, ed era l'UNICO elemento della mappa
# non disegnato come sprite. In mezzo alle case colorate leggeva come un
# rettangolo bianco — la cosa che Jay ha bocciato guardando la mappa vera.
# Ora un luogo e uno sprite come tutto il resto.
#
# Provenienza degli sprite, tutti da pack gia referenziati dal template di
# produzione (nessun rischio DDF014):
# - Bp03igMq "CHR - Town Maps": edifici singoli disegnati alla scala di una
#   mappa di paese (una casa ~0,8 quadretti). E il registro giusto per i
#   preset "quartiere" e "citta", dove un edificio ordinario e uno sprite di
#   dimensione simile.
# - RchUgE31 "City Terrain": cattedrale, cimitero, castello, molo.
# - roSIrsHG "Lost Lands Hamlets": forgia, gogna, cappi, pozzo.
# - 2VHJB262 "BB BaseCity" e KtpqsMIX "BB KeepsAndCastles": tessere 3x3
#   quadretti che ritraggono un complesso intero con le sue pertinenze. Usate
#   SOLO dove non esiste un edificio singolo equivalente (anfiteatro,
#   giardino, faro, forte, mercato): a quel punto e giusto che il monumento
#   occupi piu spazio degli altri.
#
# Chiavi LETTERALI del catalogo e mai alias semantici, per lo stesso motivo
# gia documentato su "bed" e "bookshelf": dopo TASK-45 un alias su substring
# puo agganciarsi in silenzio a un pack diverso a seconda dell'ordine dei
# --from. Piu varianti per luogo = varieta fra due istanze dello stesso tipo.
# Regola imparata guardando il primo risultato renderizzato: gli sprite BB
# ritraggono un complesso CON LE SUE PERTINENZE, terreno compreso. L'abbazia
# su un'isola porta con se il mare, il maschio col fossato porta l'acqua: in
# mezzo a un quartiere fitto sono toppe di campagna, non edifici. Vanno usati
# solo dove quel contorno e' giusto (il faro sta sulla costa, l'anfiteatro ha
# davvero i suoi spalti). Per tutto il resto servono sprite di edificio
# singolo su sfondo trasparente: CHR Town Maps, City Terrain, Lost Lands.
_CITY_LANDMARK_SPRITES: dict[str, tuple[str, ...]] = {
    # --- luoghi di culto e potere ----------------------------------------
    "tempio": ("bb_city_cathedral_1_color",),
    "cattedrale": ("bb_keepsandcastles_cathedral_color",),
    "monastero": ("bb_keepsandcastles_forestkeep_color",),
    "palazzo": ("bb_keepsandcastles_castle_color",),
    "municipio": ("bb_houses1_flag1",),
    "caserma": ("bb_city_fort_1_color",),
    "prigione": ("cage_04",),
    "arena": ("tourney_grounds",),
    "teatro": ("bb_keepsandcastles_amphitheatre_color",),
    # --- sapere -----------------------------------------------------------
    "accademia": ("castle_w_moat",),
    "biblioteca": ("house_05",),
    "alchimista": ("house_07",),
    # --- commercio --------------------------------------------------------
    "banca": ("house_05",),
    "gilda": ("house_09",),
    "magazzino": ("shed_01",),
    "dogana": ("shed_02",),
    # --- artigianato ------------------------------------------------------
    "fabbro": ("shed_01",),
    "stalle": ("shed_01",),
    "fornaio": ("house_10",),
    "macelleria": ("house_01",),
    "conceria": ("shed_02",),
    "macello": ("shed_02",),
    "mulino": ("windmill_02",),
    # --- svago e servizi --------------------------------------------------
    "taverna": ("house_03",),
    "locanda": ("inn_01",),
    "bordello": ("house_06",),
    "bagni": ("house_04",),
    "lazzaretto": ("strawhouse_03",),
    # --- struttura urbana -------------------------------------------------
    "torre_guardia": ("wood_walls_tower",),
    "faro": ("bb_seasandshores_cliff_lighthouse_color",),
    "mercato": ("canopy_01",),
    "patibolo": ("thehangedman",),
    "statua": ("statue_male_mage_alt_03_a",),
    "fiera": ("tent_03",),
    # --- aree con sprite multipli: DA CONFERMARE --------------------------
    # Giardino e cimitero non sono uno sprite ma una scena: un'area colorata
    # con dentro piu' pezzi. Jay ha lasciato sul campionario tutti i
    # candidati perche' vanno giudicati montati, non in fila. Questi sono i
    # miei insiemi di lavoro, in attesa del suo verdetto sul foglio generato
    # da `landmark_sprite_sheet.py --areas`: fuori i due sprite BB (giardino
    # e frutteto sono tessere 3x3 con il loro terreno, e sparpagliate
    # ricoprirebbero l'area invece di popolarla) e fuori panchina, recinto e
    # sasso, che a queste dimensioni non si distinguono.
    "giardino": (
        "tree_big_green_01", "tree_big_green_03", "tree_green_simple_01",
        "tree_green_simple_03", "tree_massive_green_01",
    ),
    "cimitero": ("gravestone_01", "gravestone_02", "gravestone_04", "gravestone_05"),
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


def _lookup_size(catalog: dict, key: str, *, optional: bool = False):
    """Dimensioni native in pixel di una texture, per calcolare la scala di
    piazzamento (TASK-46).

    `optional=True` ritorna (None, None) invece di fallire. Serve alle
    texture non-PNG: `read_dungeondraft_pack` legge le dimensioni dall'IHDR
    di un PNG, e i pack in WebP (per esempio WFWMFRDX, da cui viene la
    statua) non ne hanno nessuna nel catalogo. Chi riceve (None, None) ricade
    sulla stima per nome di compose._texture_size, che e meno precisa ma
    esiste sempre — meglio di rinunciare allo sprite giusto."""
    sizes = catalog.get("object_sizes")
    if not isinstance(sizes, dict) or key not in sizes:
        if optional:
            return None, None
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
    # I terreni stanno nello stesso dizionario dei pavimenti (chi disegna
    # vuole una texture, non sapere da che bucket viene) ma si risolvono da
    # una categoria diversa del catalogo.
    floors.update(
        {name: _lookup(catalog, "terrain", key) for name, key in definition.get("grounds", {}).items()}
    )
    roof = _lookup(catalog, "roofs", definition["roof"]) if "roof" in definition else None
    wall_load_bearing = (
        _lookup(catalog, "walls", definition["wall_load_bearing"]) if "wall_load_bearing" in definition else None
    )
    stairs = _lookup(catalog, "objects", definition["stairs"]) if "stairs" in definition else None
    paths = {name: _lookup(catalog, "paths", key) for name, key in definition.get("paths", {}).items()}
    building_variants: list = []
    building_colors: tuple = ()
    landmark_sprites: dict = {}
    if style == "city":
        building_variants = [
            (_lookup(catalog, "objects", key), *_lookup_size(catalog, key)) for key in _CITY_BUILDING_KEYS
        ]
        building_colors = _CITY_BUILDING_COLORS
        landmark_sprites = {
            kind: [
                (_lookup(catalog, "objects", key), *_lookup_size(catalog, key, optional=True))
                for key in keys
            ]
            for kind, keys in _CITY_LANDMARK_SPRITES.items()
        }
    return Palette(
        wall=wall, floor=floor, door=door, accents=accents, floors=floors, roof=roof,
        wall_load_bearing=wall_load_bearing, stairs=stairs,
        building_variants=building_variants, building_colors=building_colors,
        paths=paths, landmark_sprites=landmark_sprites,
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
