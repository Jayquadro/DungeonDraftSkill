"""Test per l'arredo e la palette degli edifici urbani (TASK-29).

furnish() (TASK-23) ha un contratto a un solo livello (list-based, come i
dungeon a un piano): per un edificio multi-piano il chiamante deve invocarla
una volta per piano, passando un Blueprint filtrato alle sole stanze di quel
piano — stesso pattern gia usato da draw_building per level_stack. Questi
test costruiscono quel Blueprint per-piano con _floor_blueprint, la stessa
cosa che fara il wiring CLI di TASK-30.
"""

import math
import random

from ddforge.assets import load_catalog, palette_for
from ddforge.cli import _add_lighting
from ddforge.compose import draw_building, draw_room, furnish
from ddforge.generators import building
from ddforge.ids import IdAllocator
from ddforge.model import Blueprint
from ddforge.template import finalize, load_template, prepare
from ddforge.validate import validate

CATALOG = load_catalog()


def _obj_grid_pos(obj) -> tuple[float, float]:
    inner = obj["position"][obj["position"].index("(") + 1 : obj["position"].index(")")]
    x_str, y_str = inner.split(",")
    return float(x_str) / 256, float(y_str) / 256


def _floor_blueprint(bp: Blueprint, level_index: int) -> Blueprint:
    rooms = [r for r in bp.rooms if r.level == level_index]
    return Blueprint(
        width=bp.width, height=bp.height, rooms=rooms, corridors=[],
        graph={i: [] for i in range(len(rooms))}, seed=bp.seed, style=bp.style,
    )


def test_palette_for_returns_style_specific_palettes_for_the_three_building_types():
    tavern = palette_for("tavern", CATALOG)
    manor = palette_for("manor", CATALOG)
    warehouse = palette_for("warehouse", CATALOG)

    walls = (tavern.wall, manor.wall, warehouse.wall)
    assert len(set(walls)) == 3  # 3 texture di muro distinte, una per stile
    assert tavern.accents and manor.accents and warehouse.accents


def test_furnish_gives_beds_to_bedrooms_and_not_to_common_rooms():
    palette = palette_for("tavern", CATALOG)
    bp = building.generate(width=40, height=40, seed=1, building_type="tavern")

    doc = load_template("templates/blank_80x80.dungeondraft_map")
    prepared = prepare(doc, levels=bp.levels)
    ids = IdAllocator.from_document(prepared)
    draw_building(prepared["world"]["levels"], ids, bp, palette)
    first_floor = prepared["world"]["levels"]["1"]
    furnish(first_floor, ids, _floor_blueprint(bp, 1), palette, density="heavy", rng=random.Random(1))

    bed_texture = palette.accents["bed"]
    common_texture = palette.accents["table"]
    # La scala del vano scale la disegna draw_building, non furnish: non e
    # arredo di stanza e non deve entrare nel conteggio (TASK-30).
    objects = [o for o in first_floor["objects"] if o["texture"] != palette.stairs]
    assert objects, "il piano delle camere deve avere arredo"
    assert any(o["texture"] == bed_texture for o in objects), "nessun letto nelle camere"
    # Una camera non e arredata solo di letti (difetto 6 del gate M4), ma
    # nemmeno di tavoli da sala comune: gli accents ammessi sono quelli che
    # _KIND_ACCENT_HINTS mappa su "camera".
    allowed = {palette.accents[k] for k in ("bed", "cupboard")}
    assert all(o["texture"] in allowed for o in objects)
    assert not any(o["texture"] == common_texture for o in objects)


def test_furnish_gives_tables_and_chairs_to_common_room_not_beds():
    palette = palette_for("tavern", CATALOG)
    bp = building.generate(width=40, height=40, seed=1, building_type="tavern")

    doc = load_template("templates/blank_80x80.dungeondraft_map")
    prepared = prepare(doc, levels=bp.levels)
    ids = IdAllocator.from_document(prepared)
    draw_building(prepared["world"]["levels"], ids, bp, palette)
    ground_floor = prepared["world"]["levels"]["0"]
    furnish(ground_floor, ids, _floor_blueprint(bp, 0), palette, density="heavy", rng=random.Random(1))

    bed_texture = palette.accents["bed"]
    allowed = {palette.accents[k] for k in ("table", "chair", "bench")}
    sala_room = next(r for r in bp.rooms if r.kind == "sala_comune")
    in_sala = [
        o for o in ground_floor["objects"]
        if sala_room.rect.x1 <= _obj_grid_pos(o)[0] <= sala_room.rect.x2
        and sala_room.rect.y1 <= _obj_grid_pos(o)[1] <= sala_room.rect.y2
    ]
    assert in_sala, "la sala comune deve avere arredo"
    assert all(o["texture"] in allowed for o in in_sala)
    assert not any(o["texture"] == bed_texture for o in in_sala)


def test_furnish_gives_crates_and_barrels_to_warehouse_rooms():
    palette = palette_for("warehouse", CATALOG)
    bp = building.generate(width=40, height=40, seed=1, building_type="warehouse")

    doc = load_template("templates/blank_80x80.dungeondraft_map")
    prepared = prepare(doc, levels=bp.levels)
    ids = IdAllocator.from_document(prepared)
    draw_building(prepared["world"]["levels"], ids, bp, palette)
    ground_floor = prepared["world"]["levels"]["0"]
    furnish(ground_floor, ids, _floor_blueprint(bp, 0), palette, density="heavy", rng=random.Random(1))

    allowed = set(palette.accents.values())  # crate, barrel, keg: gia tutti ammessi per magazzino
    objects = [o for o in ground_floor["objects"] if o["texture"] != palette.stairs]
    assert objects
    assert all(o["texture"] in allowed for o in objects)


def test_unmapped_room_kind_falls_back_to_full_accent_set():
    """Retrocompatibilita TASK-23: uno stile senza hint per il kind (es. dungeon)
    continua a pescare da tutti gli accents, come prima di TASK-29."""
    from ddforge.assets import Palette
    from ddforge.model import Rect, Room

    palette = Palette(
        wall="res://textures/walls/stone.png",
        floor="res://textures/patterns/normal/stone_floor.png",
        door="res://textures/portals/door_00.png",
        accents={"barrel": "res://x/barrel.png", "table_round": "res://x/table.png"},
    )
    level = {
        "walls": [], "portals": [], "patterns": [], "objects": [], "paths": [],
        "lights": [], "texts": [],
        "roofs": {"shade": True, "shade_contrast": 0.5, "sun_direction": 45, "roofs": []},
    }
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 20, 20), kind="sala")  # kind non mappato in _KIND_ACCENT_HINTS
    draw_room(level, ids, room, palette)

    bp = Blueprint(width=100, height=100, rooms=[room], corridors=[], graph={0: []}, seed=1, style="dungeon")
    furnish(level, ids, bp, palette, density="heavy", rng=random.Random(1))

    used_textures = {o["texture"] for o in level["objects"]}
    assert used_textures == set(palette.accents.values())


def test_no_furniture_ever_falls_inside_the_stairs_rect():
    """Il vano scale contiene la scala e nient'altro: un barile in mezzo alle
    scale e un ostacolo, non arredo. La scala stessa la piazza draw_building
    ed e l'unica cosa ammessa li dentro (TASK-30)."""
    for building_type in ("tavern", "manor", "warehouse"):
        palette = palette_for(building_type, CATALOG)
        bp = building.generate(width=40, height=40, seed=3, building_type=building_type)

        doc = load_template("templates/blank_80x80.dungeondraft_map")
        prepared = prepare(doc, levels=bp.levels)
        ids = IdAllocator.from_document(prepared)
        draw_building(prepared["world"]["levels"], ids, bp, palette)
        for level_key, level in prepared["world"]["levels"].items():
            furnish(level, ids, _floor_blueprint(bp, int(level_key)), palette, density="heavy", rng=random.Random(3))

        stairs = bp.stairs_rect
        for level in prepared["world"]["levels"].values():
            for obj in level["objects"]:
                if obj["texture"] == palette.stairs:
                    continue
                x, y = _obj_grid_pos(obj)
                inside_stairs = stairs.x1 < x < stairs.x2 and stairs.y1 < y < stairs.y2
                assert not inside_stairs, f"{building_type}: oggetto dentro il vano scale ({x}, {y})"


def test_lighting_places_one_plausible_light_per_room_in_a_building():
    bp = building.generate(width=40, height=40, seed=1, building_type="manor")
    palette = palette_for("manor", CATALOG)

    doc = load_template("templates/blank_80x80.dungeondraft_map")
    prepared = prepare(doc, levels=bp.levels)
    ids = IdAllocator.from_document(prepared)
    draw_building(prepared["world"]["levels"], ids, bp, palette)

    for level_key, level in prepared["world"]["levels"].items():
        floor_bp = _floor_blueprint(bp, int(level_key))
        _add_lighting(level, ids, floor_bp)
        assert len(level["lights"]) == len(floor_bp.rooms)
        for room, light in zip(floor_bp.rooms, level["lights"]):
            lx, ly = _obj_grid_pos(light)
            cx, cy = room.rect.center()
            assert math.isclose(lx, cx) and math.isclose(ly, cy)


def test_end_to_end_furnished_and_lit_building_passes_validate():
    for building_type in ("tavern", "manor", "warehouse"):
        palette = palette_for(building_type, CATALOG)
        bp = building.generate(width=40, height=40, seed=1, building_type=building_type)

        doc = load_template("templates/blank_80x80.dungeondraft_map")
        prepared = prepare(doc, levels=bp.levels)
        ids = IdAllocator.from_document(prepared)
        draw_building(prepared["world"]["levels"], ids, bp, palette)
        for level_key, level in prepared["world"]["levels"].items():
            floor_bp = _floor_blueprint(bp, int(level_key))
            furnish(level, ids, floor_bp, palette, density="medium", rng=random.Random(1))
            _add_lighting(level, ids, floor_bp)
        finalize(prepared, ids)

        errors = [i for i in validate(prepared) if i.severity == "error"]
        assert errors == [], f"{building_type}: {errors}"
