"""Test per ddforge.compose.draw_building (TASK-27)."""

from ddforge.assets import Palette
from ddforge.compose import draw_building
from ddforge.godot import grid_to_px, parse_pv2
from ddforge.ids import IdAllocator
from ddforge.model import Blueprint, Door, Rect, Room
from ddforge.template import finalize, load_template, prepare
from ddforge.validate import validate

PALETTE = Palette(
    wall="res://textures/walls/wood_04.png",
    floor="res://textures/patterns/normal/wood_planks.png",
    door="res://textures/portals/door_wood_single.png",
    wall_load_bearing="res://textures/walls/stone.png",
    roof="res://textures/roofs/flat_clay_red/tiles.png",
)


def _empty_level_stack(n=2):
    return {
        str(i): {
            "walls": [], "portals": [], "patterns": [], "objects": [], "paths": [],
            "lights": [], "texts": [],
            "roofs": {"shade": True, "shade_contrast": 0.5, "sun_direction": 45, "roofs": []},
        }
        for i in range(n)
    }


def _two_floor_blueprint(stairs_rect=None):
    rooms = [
        Room(rect=Rect(0, 0, 10, 10), kind="sala", level=0, doors=[Door(wall_index=0, t=0.5)]),
        Room(rect=Rect(10, 0, 20, 10), kind="sala", level=0, doors=[Door(wall_index=2, t=0.5)]),
        Room(rect=Rect(0, 0, 10, 10), kind="sala", level=1, doors=[Door(wall_index=1, t=0.5)]),
    ]
    return Blueprint(
        width=30, height=30, rooms=rooms, corridors=[], graph={0: [], 1: [], 2: []},
        seed=1, style="tavern", levels=2, stairs_rect=stairs_rect,
    )


def test_rooms_are_distributed_to_the_correct_level():
    level_stack = _empty_level_stack(2)
    ids = IdAllocator()
    bp = _two_floor_blueprint()
    draw_building(level_stack, ids, bp, PALETTE)

    # Le due stanze del piano 0 tassellano il footprint (0,0)-(20,10): tutti
    # i loro lati esterni stanno sul perimetro portante e non vengono
    # ridisegnati, resta solo il tramezzo in mezzo. Perimetro (4) + tramezzo
    # di ciascuna stanza (1+1) = 6.
    assert len(level_stack["0"]["walls"]) == 6
    # Il piano 1 ha una stanza sola, che copre meta footprint: perimetro (4)
    # piu il suo unico lato interno = 5.
    assert len(level_stack["1"]["walls"]) == 5
    assert [p["texture"] for p in level_stack["0"]["patterns"]].count(PALETTE.floor) == 2


def test_nothing_is_drawn_on_top_of_the_load_bearing_perimeter():
    """Un muro di stanza ridisegnato sopra il muro portante tappa la porta
    che ci sta dentro: nel gate umano M4 l'ingresso e la porta del vano scale
    erano murati esattamente cosi (TASK-30).

    Fra due stanze i muri restano invece volutamente sdoppiati — ciascuna
    disegna il proprio tramezzo — perche la porta viene bucata su entrambi
    (convenzione di _connect_rooms) e i due segmenti coincidono."""
    level_stack = _empty_level_stack(2)
    ids = IdAllocator()
    bp = _two_floor_blueprint(stairs_rect=Rect(0, 10, 20, 14))
    draw_building(level_stack, ids, bp, PALETTE)

    # Footprint: bounding box di stanze + vano scale, cioe (0,0)-(20,14) in
    # quadretti, (0,0)-(5120,3584) in pixel.
    x1, y1, x2, y2 = 0.0, 0.0, 5120.0, 3584.0

    def on_perimeter(segment):
        (ax, ay), (bx, by) = segment
        return (
            (ax == bx and ax in (x1, x2)) or (ay == by and ay in (y1, y2))
        )

    for level_key, level in level_stack.items():
        on_boundary = [
            w for w in level["walls"] if on_perimeter(tuple(sorted(parse_pv2(w["points"]))))
        ]
        assert len(on_boundary) == 4, (
            f"piano {level_key}: {len(on_boundary)} muri sul perimetro invece di 4"
        )
        assert all(w["texture"] == PALETTE.wall_load_bearing for w in on_boundary), (
            f"piano {level_key}: un tramezzo e stato disegnato sopra il muro portante"
        )


def test_stairs_occupy_the_identical_rect_on_every_level():
    stairs = Rect(18, 18, 20, 20)
    level_stack = _empty_level_stack(2)
    ids = IdAllocator()
    bp = _two_floor_blueprint(stairs_rect=stairs)
    draw_building(level_stack, ids, bp, PALETTE)

    stair_points_per_level = []
    for level in level_stack.values():
        patterns = level["patterns"]
        stair_pattern = next(p for p in patterns if p["texture"] == PALETTE.floor and len(parse_pv2(p["points"])) == 4)
        stair_points_per_level.append(sorted(parse_pv2(stair_pattern["points"])))

    assert stair_points_per_level[0] == stair_points_per_level[1]


def test_roof_only_on_the_last_level():
    level_stack = _empty_level_stack(3)
    ids = IdAllocator()
    bp = _two_floor_blueprint()
    bp.levels = 3
    bp.rooms[2].level = 2  # sposta la terza stanza all'ultimo piano
    draw_building(level_stack, ids, bp, PALETTE)

    assert level_stack["0"]["roofs"]["roofs"] == []
    assert level_stack["1"]["roofs"]["roofs"] == []
    assert len(level_stack["2"]["roofs"]["roofs"]) == 1


def test_no_roof_when_palette_has_none():
    palette_no_roof = Palette(wall=PALETTE.wall, floor=PALETTE.floor, door=PALETTE.door)
    level_stack = _empty_level_stack(2)
    ids = IdAllocator()
    draw_building(level_stack, ids, _two_floor_blueprint(), palette_no_roof)
    assert level_stack["1"]["roofs"]["roofs"] == []


def test_roof_does_not_overhang_the_building():
    """TASK-47: prima della correzione il tetto era un poligono chiuso a 4
    vertici con `width` di default (512 px), che con la semantica di
    roof.points/roof.width verificata in TASK-41 (width = MEZZA larghezza,
    docs/format.md §5) si stende 2 quadretti oltre il perimetro su ogni
    lato. Ora usa la stessa add_ridge_roof dei preset di city.py: colmo a 2
    punti, gronde esattamente sui bordi del footprint. Stesso schema di
    test_isolato_roofs_do_not_overhang_the_building in
    tests/test_generators_city.py."""
    from ddforge.compose import _building_footprint

    level_stack = _empty_level_stack(2)
    ids = IdAllocator()
    bp = _two_floor_blueprint(stairs_rect=Rect(0, 10, 20, 14))
    draw_building(level_stack, ids, bp, PALETTE)

    footprint = _building_footprint(bp)
    roofs = level_stack["1"]["roofs"]["roofs"]
    assert len(roofs) == 1
    points = parse_pv2(roofs[0]["points"])
    assert len(points) == 2, "tetto a poligono chiuso: sborda (vedi TASK-47)"
    half = roofs[0]["width"]
    assert half <= grid_to_px(min(footprint.w, footprint.h)) / 2 + 1e-6
    for x, y in points:
        assert grid_to_px(footprint.x1) - 1e-6 <= x <= grid_to_px(footprint.x2) + 1e-6
        assert grid_to_px(footprint.y1) - 1e-6 <= y <= grid_to_px(footprint.y2) + 1e-6


def test_load_bearing_walls_use_a_different_texture_than_partitions():
    level_stack = _empty_level_stack(2)
    ids = IdAllocator()
    draw_building(level_stack, ids, _two_floor_blueprint(), PALETTE)

    textures = {w["texture"] for w in level_stack["0"]["walls"]}
    assert PALETTE.wall_load_bearing in textures
    assert PALETTE.wall in textures
    assert PALETTE.wall_load_bearing != PALETTE.wall


def test_load_bearing_falls_back_to_wall_when_not_set():
    palette_no_load_bearing = Palette(wall=PALETTE.wall, floor=PALETTE.floor, door=PALETTE.door)
    level_stack = _empty_level_stack(2)
    ids = IdAllocator()
    draw_building(level_stack, ids, _two_floor_blueprint(), palette_no_load_bearing)
    textures = {w["texture"] for w in level_stack["0"]["walls"]}
    assert textures == {palette_no_load_bearing.wall}


def test_multi_level_document_passes_validate_without_errors():
    doc = load_template("templates/blank_80x80.dungeondraft_map")
    prepared = prepare(doc, levels=2)
    ids = IdAllocator.from_document(prepared)
    draw_building(prepared["world"]["levels"], ids, _two_floor_blueprint(stairs_rect=Rect(25, 25, 27, 27)), PALETTE)
    finalize(prepared, ids)

    errors = [i for i in validate(prepared) if i.severity == "error"]
    assert errors == []
