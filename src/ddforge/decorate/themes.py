"""Tabelle dati dei sei temi di abbellimento (docs/SPEC-decorate.md §6.2).

Solo dati: nessuna logica di piazzamento (quella vive in `planner.py`,
TASK-69). Ogni chiave qui citata DEVE risolvere su una texture di
`data/assets.json` (test in tests/test_decorate_themes.py) e appartenere a
un pack del manifest del template di produzione (stesso test): mai un path
inventato, mai un pack fuori dal manifest (SPEC §1.3).

TASK-68: censimento in backlog/docs/censimento-asset-temi-m10 (o il
documento Backlog equivalente). I sei pack citati nello SPEC per arcano e
festivo (DQ Arcane Laboratory, Skront's Alchemy, IC Apothecary,
TygerLibrary, TygerBar, TygerMusic, GW Inn tables, BB BaseCity) sono gia nel
manifest del template di produzione; il censimento non ha trovato nessuna
categoria scoperta, quindi non ci sono voci "in attesa di nuovo sprite".
"""

from dataclasses import dataclass

THEMES: tuple[str, ...] = ("abbandonato", "abitato", "lugubre", "naturale", "arcano", "festivo")
MAP_TYPES: tuple[str, ...] = ("dungeon", "building", "cave", "sewer", "city")

DEFAULT_ROLE = "_default"

# Texture luce unica del progetto (TASK-42, docs/format.md): una luce senza
# `texture` manda Dungeondraft in loop infinito al caricamento.
_LIGHT_TEXTURE = "res://textures/lights/soft.png"


@dataclass(frozen=True)
class ObjectEntry:
    """Un alias del catalogo nel pool di oggetti di una zona (SPEC §6.2,
    §6.4). `cls` decide le regole tattiche non negoziabili: 'decal' puo
    stare ovunque (tranne sopra una porta), 'ingombro' conta per la soglia
    del 30% e non entra nei corridoi larghi 1."""

    key: str
    weight: float = 1.0
    # sparso (a caso nell'area libera) | parete (addossato a un muro,
    # parallelo ad esso) | centro (al centro della zona) | soglia (vicino a
    # una porta, fuori dal raggio di rispetto)
    placement: str = "sparso"
    cls: str = "decal"


@dataclass(frozen=True)
class TerrainPaint:
    """Una pennellata di `terrain.splat` (SPEC §6.2, §7.3): lo spike
    TASK-67 decide come scriverla; qui c'e solo quale slot e dove."""

    slot: str
    where: str  # bordi | angoli | chiazze | soglie
    coverage: float = 0.3


@dataclass(frozen=True)
class LightRule:
    rule: str  # porte | centro | per_oggetto
    color: str  # ARGB a 8 cifre
    range: float = 4.0
    intensity: float = 1.0
    texture: str = _LIGHT_TEXTURE


@dataclass(frozen=True)
class ZoneTheme:
    """Cosa fa il tema a una zona di un dato ruolo (SPEC §6.2). `None` su
    `floor`/`wall` significa "lascia com'e", non "nessuna preferenza"."""

    floor: str | None = None
    wall: str | None = None
    terrain: tuple[TerrainPaint, ...] = ()
    objects: tuple[ObjectEntry, ...] = ()
    lights: LightRule | None = None
    ambient: str = "ffb0b0b0"


def theme_for(theme: str, map_type: str, role: str) -> ZoneTheme:
    """ZoneTheme per (tema, tipo di mappa, ruolo), col default del tipo di
    mappa se il ruolo non e elencato (AC4)."""
    by_role = THEMES_TABLE[theme][map_type]
    return by_role.get(role, by_role[DEFAULT_ROLE])


# ---------------------------------------------------------------------------
# abbandonato — polvere, macerie, mobili rotti, ragnatele; luci poche e fioche
# ---------------------------------------------------------------------------

_ABBANDONATO_AMBIENT = "ff3a3a3a"
_ABBANDONATO_LIGHT = LightRule(rule="porte", color="80c9a876", range=2.5, intensity=0.5)
_ABBANDONATO_CLUTTER = (
    ObjectEntry("rubble_01", weight=2.0, cls="decal"),
    ObjectEntry("web_medium_01_a", weight=1.5, cls="decal"),
    ObjectEntry("web_small_01_a", weight=1.5, cls="decal"),
    ObjectEntry("stone_block_debris_scatter_01_a", weight=1.0, cls="decal"),
    ObjectEntry("broken_chair_01_ashen", weight=1.0, cls="ingombro"),
    ObjectEntry("broken_table_rectangle_01_ashen", weight=0.6, cls="ingombro", placement="parete"),
    ObjectEntry("wood_board_broken_01_a_ashen", weight=1.2, cls="decal"),
    ObjectEntry("bone_pile_01_a", weight=0.8, cls="decal"),
)
_ABBANDONATO_TERRAIN_INDOOR = (
    TerrainPaint("dirt", "bordi", 0.35),
    TerrainPaint("gravel_01_a", "angoli", 0.2),
)

THEME_ABBANDONATO: dict[str, dict[str, ZoneTheme]] = {
    "dungeon": {
        "sala": ZoneTheme(
            floor="cracked_stone_01_a", wall=None, terrain=_ABBANDONATO_TERRAIN_INDOOR,
            objects=_ABBANDONATO_CLUTTER, lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
        "boss": ZoneTheme(
            floor="cracked_stone_01_a", wall=None, terrain=_ABBANDONATO_TERRAIN_INDOOR,
            objects=(ObjectEntry("stone_block_debris_pile_01_a", weight=1.0, cls="ingombro"),) + _ABBANDONATO_CLUTTER,
            lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
        "secret": ZoneTheme(
            floor="cracked_stone_01_a", wall=None, terrain=_ABBANDONATO_TERRAIN_INDOOR,
            objects=(ObjectEntry("web_small_01_a", weight=2.0, cls="decal"),),
            lights=None, ambient=_ABBANDONATO_AMBIENT,
        ),
        "corridoio": ZoneTheme(
            floor="cracked_stone_01_a", wall=None, terrain=_ABBANDONATO_TERRAIN_INDOOR,
            objects=(ObjectEntry("web_medium_01_a", weight=1.0, cls="decal", placement="parete"),),
            lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
        "ingresso": ZoneTheme(
            floor="cracked_stone_01_a", wall=None, terrain=_ABBANDONATO_TERRAIN_INDOOR,
            objects=(), lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
        DEFAULT_ROLE: ZoneTheme(
            floor="cracked_stone_01_a", wall=None, terrain=_ABBANDONATO_TERRAIN_INDOOR,
            objects=_ABBANDONATO_CLUTTER, lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
    },
    "building": {
        "sala_comune": ZoneTheme(
            floor="wooden_floor_damaged_01_a_ashen", wall=None, terrain=(),
            objects=_ABBANDONATO_CLUTTER, lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
        "cucina": ZoneTheme(
            floor="wooden_floor_damaged_01_a_ashen", wall=None, terrain=(),
            objects=(ObjectEntry("barrel_broken_01_a_ashen", weight=1.0, cls="ingombro"),) + _ABBANDONATO_CLUTTER,
            lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
        "camera": ZoneTheme(
            floor="wooden_floor_damaged_01_a_ashen", wall=None, terrain=(),
            objects=(ObjectEntry("rug_damaged_small_01_a", weight=1.0, cls="decal"),) + _ABBANDONATO_CLUTTER,
            lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
        "scale": ZoneTheme(floor="wooden_floor_damaged_01_a_ashen", ambient=_ABBANDONATO_AMBIENT),
        "esterno": ZoneTheme(
            floor=None, wall=None,
            terrain=(TerrainPaint("dirt", "chiazze", 0.5), TerrainPaint("dead_tree_01", "angoli", 0.1)),
            objects=(ObjectEntry("tree_stump_broken_01_a_ashen", weight=1.0, cls="ingombro"),),
            lights=None, ambient=_ABBANDONATO_AMBIENT,
        ),
        DEFAULT_ROLE: ZoneTheme(
            floor="wooden_floor_damaged_01_a_ashen", wall=None, terrain=(),
            objects=_ABBANDONATO_CLUTTER, lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
    },
    "cave": {
        "ampia": ZoneTheme(
            floor="cave_floor_stone_01_a", terrain=(TerrainPaint("rubble", "bordi", 0.3),),
            objects=(ObjectEntry("stone_block_debris_scatter_01_a", weight=1.0, cls="decal"),),
            lights=_ABBANDONATO_LIGHT, ambient=_ABBANDONATO_AMBIENT,
        ),
        "stretta": ZoneTheme(floor="cave_floor_stone_01_a", ambient=_ABBANDONATO_AMBIENT),
        "cieca": ZoneTheme(
            floor="cave_floor_stone_01_a",
            objects=(ObjectEntry("bone_pile_01_a", weight=1.0, cls="decal"),),
            ambient=_ABBANDONATO_AMBIENT,
        ),
        DEFAULT_ROLE: ZoneTheme(floor="cave_floor_stone_01_a", ambient=_ABBANDONATO_AMBIENT),
    },
    "sewer": {
        "canale": ZoneTheme(ambient=_ABBANDONATO_AMBIENT),
        "camera": ZoneTheme(
            objects=(ObjectEntry("rubble_01", weight=1.0, cls="decal"),), ambient=_ABBANDONATO_AMBIENT,
        ),
        "ingresso": ZoneTheme(ambient=_ABBANDONATO_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(ambient=_ABBANDONATO_AMBIENT),
    },
    "city": {
        "strada": ZoneTheme(ambient=_ABBANDONATO_AMBIENT),
        "piazza": ZoneTheme(
            terrain=(TerrainPaint("dirt", "chiazze", 0.4),),
            objects=(ObjectEntry("rubble_01", weight=1.0, cls="decal"),), ambient=_ABBANDONATO_AMBIENT,
        ),
        "cortile": ZoneTheme(terrain=(TerrainPaint("dirt", "chiazze", 0.5),), ambient=_ABBANDONATO_AMBIENT),
        "extra": ZoneTheme(terrain=(TerrainPaint("dirt", "chiazze", 0.6),), ambient=_ABBANDONATO_AMBIENT),
        "riva": ZoneTheme(ambient=_ABBANDONATO_AMBIENT),
        "banchina": ZoneTheme(ambient=_ABBANDONATO_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(ambient=_ABBANDONATO_AMBIENT),
    },
}

# ---------------------------------------------------------------------------
# abitato — arredo completo, caldo, vissuto; quasi nessun terreno dipinto
# ---------------------------------------------------------------------------

_ABITATO_AMBIENT = "ffe8e0c8"
_ABITATO_LIGHT = LightRule(rule="porte", color="ffffd9a0", range=4.0, intensity=1.1)
_ABITATO_FURNISH = (
    ObjectEntry("chair", weight=1.5, cls="ingombro", placement="parete"),
    ObjectEntry("table_round", weight=1.0, cls="ingombro"),
    ObjectEntry("rug_decorative_01_a", weight=1.2, cls="decal", placement="centro"),
    ObjectEntry("candlestick_1_silver", weight=1.0, cls="decal", placement="parete"),
    ObjectEntry("bookshelf", weight=0.8, cls="ingombro", placement="parete"),
)

THEME_ABITATO: dict[str, dict[str, ZoneTheme]] = {
    "dungeon": {
        "sala": ZoneTheme(
            floor=None, wall=None, objects=_ABITATO_FURNISH, lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT,
        ),
        "boss": ZoneTheme(floor=None, wall=None, objects=_ABITATO_FURNISH, lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT),
        "secret": ZoneTheme(ambient=_ABITATO_AMBIENT),
        "corridoio": ZoneTheme(
            objects=(ObjectEntry("candlestick_1_silver", weight=1.0, cls="decal", placement="parete"),),
            lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT,
        ),
        "ingresso": ZoneTheme(lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(objects=_ABITATO_FURNISH, lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT),
    },
    "building": {
        "sala_comune": ZoneTheme(
            floor="dq_floor_wood_frame_oak_01", objects=_ABITATO_FURNISH, lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT,
        ),
        "cucina": ZoneTheme(
            floor="dq_floor_wood_frame_oak_01",
            objects=(ObjectEntry("gw_kitchen_table_1", weight=1.0, cls="ingombro"),),
            lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT,
        ),
        "camera": ZoneTheme(
            floor="dq_floor_wood_frame_oak_01",
            objects=(ObjectEntry("rug_bedside_01_a", weight=1.2, cls="decal"),),
            lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT,
        ),
        "rappresentanza": ZoneTheme(
            floor="dq_floor_carpet_01_light", objects=_ABITATO_FURNISH, lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT,
        ),
        "privato": ZoneTheme(floor="dq_floor_carpet_01_light", lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT),
        "servitu": ZoneTheme(floor="dq_floor_wood_frame_oak_01", lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT),
        "magazzino": ZoneTheme(
            floor="dq_floor_wood_frame_oak_01",
            objects=(ObjectEntry("crate", weight=1.5, cls="ingombro"), ObjectEntry("wooden_barrel", weight=1.2, cls="ingombro")),
            ambient=_ABITATO_AMBIENT,
        ),
        "soppalco": ZoneTheme(floor="dq_floor_wood_frame_oak_01", ambient=_ABITATO_AMBIENT),
        "stanza": ZoneTheme(floor="dq_floor_wood_frame_oak_01", objects=_ABITATO_FURNISH, lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT),
        "scale": ZoneTheme(floor="dq_floor_wood_frame_oak_01", ambient=_ABITATO_AMBIENT),
        "esterno": ZoneTheme(ambient=_ABITATO_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(floor="dq_floor_wood_frame_oak_01", objects=_ABITATO_FURNISH, lights=_ABITATO_LIGHT, ambient=_ABITATO_AMBIENT),
    },
    "cave": {
        DEFAULT_ROLE: ZoneTheme(ambient=_ABITATO_AMBIENT),
    },
    "sewer": {
        DEFAULT_ROLE: ZoneTheme(ambient=_ABITATO_AMBIENT),
    },
    "city": {
        "strada": ZoneTheme(ambient=_ABITATO_AMBIENT),
        "piazza": ZoneTheme(
            objects=(ObjectEntry("readymade_market_stall_01_a", weight=1.0, cls="ingombro"),), ambient=_ABITATO_AMBIENT,
        ),
        "cortile": ZoneTheme(terrain=(TerrainPaint("grass_green", "chiazze", 0.3),), ambient=_ABITATO_AMBIENT),
        "extra": ZoneTheme(ambient=_ABITATO_AMBIENT),
        "riva": ZoneTheme(ambient=_ABITATO_AMBIENT),
        "banchina": ZoneTheme(ambient=_ABITATO_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(ambient=_ABITATO_AMBIENT),
    },
}

# ---------------------------------------------------------------------------
# lugubre — ossa, lapidi, candele, sangue, catene; luci fredde o verdi
# ---------------------------------------------------------------------------

_LUGUBRE_AMBIENT = "ff0d0d10"
_LUGUBRE_LIGHT = LightRule(rule="porte", color="8060c080", range=3.0, intensity=0.6)
_LUGUBRE_CLUTTER = (
    ObjectEntry("bone_human_skull_01_a", weight=1.5, cls="decal"),
    ObjectEntry("bone_pile_01_a", weight=1.2, cls="decal"),
    ObjectEntry("blood_stain_01_a", weight=1.0, cls="decal"),
    ObjectEntry("chain_pile_messy_01_a", weight=0.8, cls="decal"),
    ObjectEntry("candle_single_purple", weight=1.0, cls="decal", placement="parete"),
    ObjectEntry("grave_stone_broken_01_a", weight=0.6, cls="ingombro"),
)

THEME_LUGUBRE: dict[str, dict[str, ZoneTheme]] = {
    "dungeon": {
        "sala": ZoneTheme(
            floor="cracked_stone_01_a", wall=None,
            objects=_LUGUBRE_CLUTTER, lights=_LUGUBRE_LIGHT, ambient=_LUGUBRE_AMBIENT,
        ),
        "boss": ZoneTheme(
            floor="cracked_stone_01_a", wall=None,
            objects=(ObjectEntry("ritual_skull_prefab_01_a", weight=1.0, cls="ingombro"),) + _LUGUBRE_CLUTTER,
            lights=_LUGUBRE_LIGHT, ambient=_LUGUBRE_AMBIENT,
        ),
        "secret": ZoneTheme(floor="cracked_stone_01_a", ambient=_LUGUBRE_AMBIENT),
        "corridoio": ZoneTheme(
            floor="cracked_stone_01_a",
            objects=(ObjectEntry("candle_single_purple", weight=1.0, cls="decal", placement="parete"),),
            lights=_LUGUBRE_LIGHT, ambient=_LUGUBRE_AMBIENT,
        ),
        "ingresso": ZoneTheme(floor="cracked_stone_01_a", lights=_LUGUBRE_LIGHT, ambient=_LUGUBRE_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(floor="cracked_stone_01_a", objects=_LUGUBRE_CLUTTER, lights=_LUGUBRE_LIGHT, ambient=_LUGUBRE_AMBIENT),
    },
    "building": {
        DEFAULT_ROLE: ZoneTheme(floor="wooden_floor_damaged_01_a_ashen", objects=_LUGUBRE_CLUTTER, lights=_LUGUBRE_LIGHT, ambient=_LUGUBRE_AMBIENT),
        "scale": ZoneTheme(floor="wooden_floor_damaged_01_a_ashen", ambient=_LUGUBRE_AMBIENT),
        "esterno": ZoneTheme(terrain=(TerrainPaint("dirt", "chiazze", 0.4),), ambient=_LUGUBRE_AMBIENT),
    },
    "cave": {
        DEFAULT_ROLE: ZoneTheme(
            floor="catacomb_floor_01_a", objects=(ObjectEntry("bone_pile_01_a", weight=1.0, cls="decal"),),
            lights=_LUGUBRE_LIGHT, ambient=_LUGUBRE_AMBIENT,
        ),
    },
    "sewer": {
        DEFAULT_ROLE: ZoneTheme(objects=(ObjectEntry("chain_pile_messy_01_a", weight=1.0, cls="decal"),), ambient=_LUGUBRE_AMBIENT),
    },
    "city": {
        DEFAULT_ROLE: ZoneTheme(ambient=_LUGUBRE_AMBIENT),
        "extra": ZoneTheme(
            objects=(ObjectEntry("grave_stone_broken_01_a", weight=1.0, cls="ingombro"),), ambient=_LUGUBRE_AMBIENT,
        ),
    },
}

# ---------------------------------------------------------------------------
# naturale — muschio, radici, funghi, rocce; luce naturale, pochissime fonti
# ---------------------------------------------------------------------------

_NATURALE_AMBIENT = "ffa8b8a0"
_NATURALE_LIGHT = LightRule(rule="centro", color="c0d9ffd0", range=3.0, intensity=0.4)
_NATURALE_CLUTTER = (
    ObjectEntry("forest_mushroom_colorable_05", weight=1.5, cls="decal"),
    ObjectEntry("mushroom_small_a_02", weight=1.5, cls="decal"),
    ObjectEntry("forest_root_03", weight=1.0, cls="decal"),
    ObjectEntry("rock_04", weight=1.0, cls="ingombro"),
    ObjectEntry("bush_green_simple_03", weight=1.2, cls="ingombro"),
)

THEME_NATURALE: dict[str, dict[str, ZoneTheme]] = {
    "dungeon": {
        DEFAULT_ROLE: ZoneTheme(
            floor=None, wall=None, terrain=(TerrainPaint("moss_01_a", "bordi", 0.3), TerrainPaint("dirt", "angoli", 0.2)),
            objects=_NATURALE_CLUTTER, lights=_NATURALE_LIGHT, ambient=_NATURALE_AMBIENT,
        ),
    },
    "building": {
        DEFAULT_ROLE: ZoneTheme(ambient=_NATURALE_AMBIENT),
        "esterno": ZoneTheme(
            terrain=(TerrainPaint("grass_green", "chiazze", 0.6), TerrainPaint("moss_01_a", "bordi", 0.2)),
            objects=(ObjectEntry("bush_green_simple_03", weight=1.5, cls="ingombro"), ObjectEntry("oak_02", weight=1.0, cls="ingombro")),
            ambient=_NATURALE_AMBIENT,
        ),
    },
    "cave": {
        "ampia": ZoneTheme(
            floor="cave_floor_stone_01_a", terrain=(TerrainPaint("moss_01_a", "bordi", 0.4),),
            objects=_NATURALE_CLUTTER, lights=_NATURALE_LIGHT, ambient=_NATURALE_AMBIENT,
        ),
        "stretta": ZoneTheme(floor="cave_floor_stone_01_a", terrain=(TerrainPaint("moss_01_a", "bordi", 0.3),), ambient=_NATURALE_AMBIENT),
        "cieca": ZoneTheme(
            floor="cave_floor_stone_01_a",
            objects=(ObjectEntry("forest_mushroom_colorable_05", weight=2.0, cls="decal"),), ambient=_NATURALE_AMBIENT,
        ),
        DEFAULT_ROLE: ZoneTheme(floor="cave_floor_stone_01_a", terrain=(TerrainPaint("moss_01_a", "bordi", 0.3),), ambient=_NATURALE_AMBIENT),
    },
    "sewer": {
        DEFAULT_ROLE: ZoneTheme(terrain=(TerrainPaint("moss_01_a", "bordi", 0.25),), ambient=_NATURALE_AMBIENT),
    },
    "city": {
        "cortile": ZoneTheme(
            terrain=(TerrainPaint("grass_green", "chiazze", 0.6),),
            objects=(ObjectEntry("bush_green_simple_03", weight=1.5, cls="ingombro"),), ambient=_NATURALE_AMBIENT,
        ),
        "riva": ZoneTheme(
            terrain=(TerrainPaint("grass_green", "bordi", 0.4),),
            objects=(ObjectEntry("bush_green_simple_05", weight=1.0, cls="ingombro"),), ambient=_NATURALE_AMBIENT,
        ),
        "extra": ZoneTheme(terrain=(TerrainPaint("grass_green", "chiazze", 0.7),), ambient=_NATURALE_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(ambient=_NATURALE_AMBIENT),
    },
}

# ---------------------------------------------------------------------------
# arcano — banchi alchemici, alambicchi, cristalli, cerchi rituali, pergamene
# ---------------------------------------------------------------------------

_ARCANO_AMBIENT = "ff201038"
_ARCANO_LIGHT = LightRule(rule="per_oggetto", color="a0a060ff", range=3.5, intensity=0.9)
_ARCANO_CLUTTER = (
    ObjectEntry("dq_magical_glyph_gold_03", weight=1.0, cls="decal"),
    ObjectEntry("scroll_fancy_01_a", weight=1.2, cls="decal"),
    ObjectEntry("dq_magical_orb_prefab_small_16", weight=0.8, cls="decal"),
    ObjectEntry("cauldron_filled_01_a", weight=0.7, cls="ingombro"),
    ObjectEntry("glass_beaker_01", weight=1.2, cls="decal"),
)

THEME_ARCANO: dict[str, dict[str, ZoneTheme]] = {
    "dungeon": {
        "sala": ZoneTheme(floor="cracked_stone_01_a", objects=_ARCANO_CLUTTER, lights=_ARCANO_LIGHT, ambient=_ARCANO_AMBIENT),
        "boss": ZoneTheme(
            floor="cracked_stone_01_a",
            objects=(ObjectEntry("dq_magical_circle_advanced_red_01", weight=1.0, cls="decal", placement="centro"),) + _ARCANO_CLUTTER,
            lights=_ARCANO_LIGHT, ambient=_ARCANO_AMBIENT,
        ),
        "secret": ZoneTheme(floor="cracked_stone_01_a", ambient=_ARCANO_AMBIENT),
        "corridoio": ZoneTheme(floor="cracked_stone_01_a", lights=_ARCANO_LIGHT, ambient=_ARCANO_AMBIENT),
        "ingresso": ZoneTheme(floor="cracked_stone_01_a", lights=_ARCANO_LIGHT, ambient=_ARCANO_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(floor="cracked_stone_01_a", objects=_ARCANO_CLUTTER, lights=_ARCANO_LIGHT, ambient=_ARCANO_AMBIENT),
    },
    "building": {
        DEFAULT_ROLE: ZoneTheme(objects=_ARCANO_CLUTTER, lights=_ARCANO_LIGHT, ambient=_ARCANO_AMBIENT),
        "scale": ZoneTheme(ambient=_ARCANO_AMBIENT),
        "esterno": ZoneTheme(ambient=_ARCANO_AMBIENT),
    },
    "cave": {
        DEFAULT_ROLE: ZoneTheme(objects=(ObjectEntry("dq_magical_orb_prefab_small_16", weight=1.0, cls="decal"),), lights=_ARCANO_LIGHT, ambient=_ARCANO_AMBIENT),
    },
    "sewer": {
        DEFAULT_ROLE: ZoneTheme(ambient=_ARCANO_AMBIENT),
    },
    "city": {
        DEFAULT_ROLE: ZoneTheme(ambient=_ARCANO_AMBIENT),
        "piazza": ZoneTheme(objects=(ObjectEntry("dq_magical_glyph_gold_03", weight=1.0, cls="decal"),), ambient=_ARCANO_AMBIENT),
    },
}

# ---------------------------------------------------------------------------
# festivo — tavolate, stendardi, fiori, bancarelle, strumenti musicali
# ---------------------------------------------------------------------------

_FESTIVO_AMBIENT = "fff0d8a0"
_FESTIVO_LIGHT = LightRule(rule="porte", color="ffffc060", range=4.5, intensity=1.2)
_FESTIVO_CLUTTER = (
    ObjectEntry("tapestry_01_a", weight=1.2, cls="decal", placement="parete"),
    ObjectEntry("flag_blowing_01_a", weight=1.0, cls="decal", placement="parete"),
    ObjectEntry("bush_flower_02", weight=1.0, cls="decal"),
    ObjectEntry("drum01", weight=0.6, cls="ingombro"),
)

THEME_FESTIVO: dict[str, dict[str, ZoneTheme]] = {
    "dungeon": {
        DEFAULT_ROLE: ZoneTheme(objects=_FESTIVO_CLUTTER, lights=_FESTIVO_LIGHT, ambient=_FESTIVO_AMBIENT),
    },
    "building": {
        "sala_comune": ZoneTheme(
            floor="dq_floor_wood_frame_oak_01",
            objects=(ObjectEntry("gw_pub_table_1", weight=1.2, cls="ingombro"),) + _FESTIVO_CLUTTER,
            lights=_FESTIVO_LIGHT, ambient=_FESTIVO_AMBIENT,
        ),
        "cucina": ZoneTheme(floor="dq_floor_wood_frame_oak_01", lights=_FESTIVO_LIGHT, ambient=_FESTIVO_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(objects=_FESTIVO_CLUTTER, lights=_FESTIVO_LIGHT, ambient=_FESTIVO_AMBIENT),
        "scale": ZoneTheme(ambient=_FESTIVO_AMBIENT),
        "esterno": ZoneTheme(ambient=_FESTIVO_AMBIENT),
    },
    "cave": {
        DEFAULT_ROLE: ZoneTheme(ambient=_FESTIVO_AMBIENT),
    },
    "sewer": {
        DEFAULT_ROLE: ZoneTheme(ambient=_FESTIVO_AMBIENT),
    },
    "city": {
        "piazza": ZoneTheme(
            objects=(
                ObjectEntry("readymade_market_stall_02_a", weight=1.2, cls="ingombro"),
                ObjectEntry("flag_blowing_01_a", weight=1.0, cls="decal"),
            ),
            lights=_FESTIVO_LIGHT, ambient=_FESTIVO_AMBIENT,
        ),
        "strada": ZoneTheme(
            objects=(ObjectEntry("flag_blowing_01_a", weight=1.0, cls="decal", placement="parete"),),
            lights=_FESTIVO_LIGHT, ambient=_FESTIVO_AMBIENT,
        ),
        "cortile": ZoneTheme(objects=(ObjectEntry("bush_flower_02", weight=1.0, cls="decal"),), ambient=_FESTIVO_AMBIENT),
        DEFAULT_ROLE: ZoneTheme(ambient=_FESTIVO_AMBIENT),
    },
}

THEMES_TABLE: dict[str, dict[str, dict[str, ZoneTheme]]] = {
    "abbandonato": THEME_ABBANDONATO,
    "abitato": THEME_ABITATO,
    "lugubre": THEME_LUGUBRE,
    "naturale": THEME_NATURALE,
    "arcano": THEME_ARCANO,
    "festivo": THEME_FESTIVO,
}
