"""Test per ddforge.compose: draw_room, draw_corridor."""

import pytest

from ddforge.assets import Palette
from ddforge.compose import _rotation_for_direction, _wall_tangent, draw_corridor, draw_room
from ddforge.godot import parse_pv2, v2
from ddforge.ids import IdAllocator
from ddforge.model import Door, Rect, Room
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
