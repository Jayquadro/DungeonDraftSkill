"""Test per ddforge.compose: draw_room, draw_corridor."""

import math

import pytest

from ddforge.assets import Palette
from ddforge.compose import (
    _chamber_circle_points,
    _chamber_gap_depth,
    _chamber_gap_edge_points,
    _chamber_wall_arcs,
    _rotation_for_direction,
    _wall_tangent,
    draw_chamber,
    draw_corridor,
    draw_room,
    render_sewer_blueprint,
)
from ddforge.godot import parse_pv2, v2
from ddforge.ids import IdAllocator
from ddforge.model import Chamber, Corridor, Door, Rect, Room
from ddforge.validate import validate

PALETTE = Palette(
    wall="res://textures/walls/stone.png",
    floor="res://textures/patterns/normal/stone_floor.png",
    door="res://textures/portals/door_00.png",
)


def _empty_level():
    return {
        "walls": [],
        "portals": [],
        "patterns": [],
        "objects": [],
        "paths": [],
        "lights": [],
        "texts": [],
        "water": {"disable_border": False},
        "roofs": {"shade": True, "shade_contrast": 0.5, "sun_direction": 45, "roofs": []},
    }


def test_rotation_for_direction_matches_observed_real_samples():
    # docs/format.md §5: 3 campioni reali osservati
    assert _rotation_for_direction((-1, 0)) == pytest.approx(3.141593, abs=1e-5)
    assert _rotation_for_direction((0, 1)) == pytest.approx(1.570796, abs=1e-5)
    assert _rotation_for_direction((1, 0)) == pytest.approx(0.0, abs=1e-9)


def test_draw_room_returns_walls_pattern_portals_keys():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 10, 10), kind="sala", doors=[Door(wall_index=0, t=0.5)])

    result = draw_room(level, ids, room, PALETTE)

    assert set(result.keys()) == {"walls", "pattern", "portals"}
    assert len(result["walls"]) == 4
    assert len(result["portals"]) == 1


def test_draw_room_produces_closed_perimeter_matching_rect():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(2, 3, 6, 5), kind="sala")

    result = draw_room(level, ids, room, PALETTE)
    walls = result["walls"]

    # ogni lato del rettangolo deve comparire come segmento fra due vertici
    expected_px_corners = {
        (512, 768), (1536, 768), (1536, 1280), (512, 1280),
    }
    seen_points = set()
    for w in walls:
        for pt in parse_pv2(w["points"]):
            seen_points.add(pt)
    assert seen_points == expected_px_corners


def test_draw_room_floor_pattern_uses_palette_or_room_override():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 4, 4), kind="sala")
    result = draw_room(level, ids, room, PALETTE)
    assert result["pattern"]["texture"] == PALETTE.floor

    room_override = Room(rect=Rect(0, 0, 4, 4), kind="sala", floor="res://textures/patterns/normal/wood_planks.png")
    result2 = draw_room(level, ids, room_override, PALETTE)
    assert result2["pattern"]["texture"] == "res://textures/patterns/normal/wood_planks.png"


def test_draw_room_floor_pattern_uses_kind_specific_palette_floor():
    """TASK-43: un room.kind mappato in palette.floors prende quel floor."""
    palette = Palette(
        wall=PALETTE.wall, floor=PALETTE.floor, door=PALETTE.door,
        floors={"boss": "res://textures/tilesets/simple/tileset_brick_basketweave.png"},
    )
    level = _empty_level()
    ids = IdAllocator()

    boss_room = Room(rect=Rect(0, 0, 4, 4), kind="boss")
    result = draw_room(level, ids, boss_room, palette)
    assert result["pattern"]["texture"] == palette.floors["boss"]

    # Un kind non mappato ricade sul floor uniforme (comportamento invariato).
    normal_room = Room(rect=Rect(0, 0, 4, 4), kind="sala")
    result2 = draw_room(level, ids, normal_room, palette)
    assert result2["pattern"]["texture"] == palette.floor


def test_draw_room_floor_override_wins_over_kind_specific_palette_floor():
    palette = Palette(
        wall=PALETTE.wall, floor=PALETTE.floor, door=PALETTE.door,
        floors={"boss": "res://textures/tilesets/simple/tileset_brick_basketweave.png"},
    )
    level = _empty_level()
    ids = IdAllocator()

    room = Room(
        rect=Rect(0, 0, 4, 4), kind="boss",
        floor="res://textures/patterns/normal/wood_planks.png",
    )
    result = draw_room(level, ids, room, palette)
    assert result["pattern"]["texture"] == "res://textures/patterns/normal/wood_planks.png"


def test_draw_room_door_is_nested_in_the_correct_wall():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 10, 10), kind="sala", doors=[Door(wall_index=1, t=0.5)])

    result = draw_room(level, ids, room, PALETTE)
    wall1 = result["walls"][1]

    assert len(wall1["portals"]) == 1
    assert result["portals"][0] is wall1["portals"][0]
    assert wall1["portals"][0]["texture"] == PALETTE.door


def test_draw_room_multiple_doors_on_different_walls():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(
        rect=Rect(0, 0, 10, 10), kind="sala",
        doors=[Door(wall_index=0, t=0.3), Door(wall_index=2, t=0.7)],
    )
    result = draw_room(level, ids, room, PALETTE)
    assert len(result["portals"]) == 2
    assert len(result["walls"][0]["portals"]) == 1
    assert len(result["walls"][2]["portals"]) == 1


@pytest.mark.parametrize(
    "wall_index,expected_direction,expected_rotation",
    [
        (0, (1.0, 0.0), 0.0),  # top: (x1,y1)->(x2,y1)
        (1, (0.0, 1.0), 1.570796),  # right: (x2,y1)->(x2,y2)
        (2, (-1.0, 0.0), 3.141593),  # bottom: (x2,y2)->(x1,y2)
        (3, (0.0, -1.0), -1.570796),  # left: (x1,y2)->(x1,y1)
    ],
)
def test_draw_room_door_direction_and_rotation_for_all_four_wall_orientations(
    wall_index, expected_direction, expected_rotation
):
    """TASK-12: direction/rotation calibrati sul gate umano per ciascuno dei
    4 lati del perimetro (docs/format.md §5)."""
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 10, 10), kind="sala", doors=[Door(wall_index=wall_index, t=0.5)])

    result = draw_room(level, ids, room, PALETTE)
    portal = result["portals"][0]

    assert portal["direction"] == v2(*expected_direction)
    assert portal["rotation"] == pytest.approx(expected_rotation, abs=1e-5)


def test_draw_room_lights_are_added():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 10, 10), kind="sala", lights=[(5, 5)])
    draw_room(level, ids, room, PALETTE)
    assert len(level["lights"]) == 1


def test_draw_room_result_passes_validate_with_no_errors():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(10, 10, 20, 18), kind="sala", doors=[Door(wall_index=0, t=0.5)])
    draw_room(level, ids, room, PALETTE)

    doc = {
        "header": {"asset_manifest": []},
        "world": {
            "format": 3, "width": 40, "height": 40, "next_node_id": ids.next_free,
            "msi": {}, "grid": {}, "embedded": {},
            "levels": {"0": {
                **level,
                "label": "", "environment": {}, "layers": {}, "shapes": {"polygons": [], "walls": []},
                "tiles": {"cells": "PoolIntArray(  )"}, "cave": {"bitmap": "PoolByteArray(  )", "entrance_bitmap": "PoolByteArray(  )"},
                "terrain": {"splat": "PoolByteArray(  )"}, "water": {}, "materials": {}, "texts_vis": True,
            }},
        },
    }
    errors = [i for i in validate(doc) if i.severity == "error"]
    # DDF010/011 falliranno (blob fittizi vuoti): filtriamo solo quelli
    errors = [e for e in errors if e.code not in ("DDF010", "DDF011")]
    assert errors == []


def test_draw_corridor_has_no_doors():
    level = _empty_level()
    ids = IdAllocator()
    result = draw_corridor(level, ids, Rect(0, 0, 2, 8), PALETTE)

    assert result["portals"] == []
    for wall in result["walls"]:
        assert wall["portals"] == []


def test_draw_corridor_still_produces_floor_and_walls():
    level = _empty_level()
    ids = IdAllocator()
    result = draw_corridor(level, ids, Rect(0, 0, 2, 8), PALETTE)
    assert result["pattern"]["texture"] == PALETTE.floor
    assert len(result["walls"]) == 4


def test_wall_tangent_matches_direction_from_first_to_last_point():
    """Calibrato dal gate umano TASK-12: direction e la tangente del muro
    (primo punto -> ultimo), non la normale perpendicolare."""
    wall = {"points": "PoolVector2Array( 0, 0, 2560, 0 )"}  # orizzontale, x crescente
    assert _wall_tangent(wall) == pytest.approx((1.0, 0.0))

    wall_v = {"points": "PoolVector2Array( 0, 0, 0, 2560 )"}  # verticale, y crescente
    assert _wall_tangent(wall_v) == pytest.approx((0.0, 1.0))

    wall_reverse = {"points": "PoolVector2Array( 2560, 0, 0, 0 )"}  # orizzontale, x decrescente
    assert _wall_tangent(wall_reverse) == pytest.approx((-1.0, 0.0))


# --- camere di giunzione circolari (TASK-33) -------------------------------

_SEWER_PALETTE = Palette(
    wall="res://textures/walls/concrete.png",
    floor="res://textures/patterns/normal/cobblestone.png",
    door="res://textures/portals/portcullis.png",
)


def test_chamber_gap_depth_is_the_circle_chord_for_the_canal_width():
    radius, canal_width = 2.5, 2.0
    depth = _chamber_gap_depth(radius, canal_width)
    assert depth == pytest.approx(math.sqrt(radius**2 - (canal_width / 2) ** 2))
    # Per costruzione, il punto (depth, half_w) sta esattamente sul cerchio.
    assert depth**2 + (canal_width / 2) ** 2 == pytest.approx(radius**2)


def test_chamber_gap_depth_rejects_a_canal_wider_than_the_chamber():
    with pytest.raises(ValueError):
        _chamber_gap_depth(radius=1.0, canal_width=3.0)


def test_chamber_circle_points_are_all_at_radius_from_center():
    chamber = Chamber(center=(10.0, 10.0), radius=1.5)
    points = _chamber_circle_points(chamber)
    assert len(points) == 16
    for x, y in points:
        assert math.hypot(x - 10.0, y - 10.0) == pytest.approx(1.5)


def test_chamber_gap_edge_points_lie_on_the_circle():
    chamber = Chamber(center=(5.0, 5.0), radius=1.5)
    for direction in ("N", "E", "S", "W"):
        before, after = _chamber_gap_edge_points(chamber, direction, canal_width=2.0)
        for x, y in (before, after):
            assert math.hypot(x - 5.0, y - 5.0) == pytest.approx(1.5)


def test_chamber_wall_arcs_no_connections_is_a_single_closed_ring():
    chamber = Chamber(center=(0.0, 0.0), radius=1.5, connected=frozenset())
    arcs = _chamber_wall_arcs(chamber, canal_width=2.0)
    assert len(arcs) == 1
    assert arcs[0] == _chamber_circle_points(chamber)


def test_chamber_wall_arcs_all_four_sides_connected_is_no_walls_at_all():
    chamber = Chamber(center=(0.0, 0.0), radius=1.5, connected=frozenset({"N", "E", "S", "W"}))
    assert _chamber_wall_arcs(chamber, canal_width=2.0) == []


def test_chamber_wall_arcs_single_gap_starts_and_ends_exactly_on_the_gap_edges():
    chamber = Chamber(center=(0.0, 0.0), radius=1.5, connected=frozenset({"E"}))
    before, after = _chamber_gap_edge_points(chamber, "E", canal_width=2.0)
    arcs = _chamber_wall_arcs(chamber, canal_width=2.0)
    assert len(arcs) == 1
    arc = arcs[0]
    assert arc[0] == pytest.approx(after)
    assert arc[-1] == pytest.approx(before)


def test_chamber_wall_arcs_two_gaps_produce_two_disjoint_arcs():
    chamber = Chamber(center=(0.0, 0.0), radius=1.5, connected=frozenset({"E", "N"}))
    arcs = _chamber_wall_arcs(chamber, canal_width=2.0)
    assert len(arcs) == 2
    # nessun punto ripetuto fra i due archi (varchi distinti)
    assert set(arcs[0]).isdisjoint(arcs[1])


def test_draw_chamber_produces_a_closed_loop_wall_when_isolated():
    level = _empty_level()
    ids = IdAllocator()
    chamber = Chamber(center=(10.0, 10.0), radius=1.5, connected=frozenset())

    result = draw_chamber(level, ids, chamber, _SEWER_PALETTE, canal_width=2.0)

    assert len(result["walls"]) == 1
    assert result["walls"][0]["loop"] is True
    assert result["walls"][0]["texture"] == _SEWER_PALETTE.wall
    assert result["pattern"]["texture"] == _SEWER_PALETTE.floor
    assert result["portals"] == []


def test_draw_chamber_opens_a_gap_for_each_connected_canal():
    level = _empty_level()
    ids = IdAllocator()
    chamber = Chamber(center=(10.0, 10.0), radius=1.5, connected=frozenset({"E", "S"}))

    result = draw_chamber(level, ids, chamber, _SEWER_PALETTE, canal_width=2.0)

    assert len(result["walls"]) == 2
    for wall in result["walls"]:
        assert wall["loop"] is False


def test_draw_chamber_entrance_gets_a_door_on_a_free_arc():
    level = _empty_level()
    ids = IdAllocator()
    chamber = Chamber(center=(10.0, 10.0), radius=1.5, connected=frozenset({"E"}), door=True)

    result = draw_chamber(level, ids, chamber, _SEWER_PALETTE, canal_width=2.0)

    assert len(result["portals"]) == 1
    assert result["portals"][0]["texture"] == _SEWER_PALETTE.door


def test_draw_chamber_no_door_when_no_free_arc_exists():
    """Incrocio a 4 vie: niente muri, quindi niente porta anche se
    chamber.door e True (nessun arco su cui metterla)."""
    level = _empty_level()
    ids = IdAllocator()
    chamber = Chamber(
        center=(10.0, 10.0), radius=1.5, connected=frozenset({"N", "E", "S", "W"}), door=True,
    )

    result = draw_chamber(level, ids, chamber, _SEWER_PALETTE, canal_width=2.0)

    assert result["walls"] == []
    assert result["portals"] == []


def test_render_sewer_blueprint_water_footprint_matches_corridors_and_chambers():
    """AC2: il layer water e popolato con un poligono per ogni canale e uno
    per ogni camera, stessa impronta dei pavimenti (compose.render_sewer_blueprint)."""
    level = _empty_level()
    ids = IdAllocator()

    class _Blueprint:
        corridors = [Corridor(2.0, 4.0, 6.0, 6.0, horizontal=True)]
        chambers = [
            Chamber(center=(1.0, 5.0), radius=1.5, connected=frozenset({"E"})),
            Chamber(center=(7.0, 5.0), radius=1.5, connected=frozenset({"W"})),
        ]

    render_sewer_blueprint(level, ids, _Blueprint(), _SEWER_PALETTE)

    assert len(level["patterns"]) == 3  # 1 canale + 2 camere
    water_children = level["water"]["tree"]["children"]
    assert len(water_children) == 3
    for wall in level["walls"]:
        assert wall["texture"] == _SEWER_PALETTE.wall
    for pattern in level["patterns"]:
        assert pattern["texture"] == _SEWER_PALETTE.floor
