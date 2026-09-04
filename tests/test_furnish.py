"""Test per ddforge.compose.furnish (TASK-23)."""

import math
import random

import pytest

from ddforge.assets import Palette
from ddforge.compose import draw_room, furnish
from ddforge.godot import parse_pv2
from ddforge.ids import IdAllocator
from ddforge.model import Blueprint, Door, Rect, Room

PALETTE = Palette(
    wall="res://textures/walls/stone.png",
    floor="res://textures/patterns/normal/stone_floor.png",
    door="res://textures/portals/door_00.png",
    accents={
        "barrel": "res://textures/objects/containers/barrel_01.png",
        "crate": "res://textures/objects/containers/crate_wood_01.png",
        "table_round": "res://textures/objects/tables/table_round.png",
    },
)

EMPTY_ACCENTS_PALETTE = Palette(
    wall="res://textures/walls/stone.png",
    floor="res://textures/patterns/normal/stone_floor.png",
    door="res://textures/portals/door_00.png",
)


def _empty_level():
    return {
        "walls": [], "portals": [], "patterns": [], "objects": [], "paths": [],
        "lights": [], "texts": [],
        "roofs": {"shade": True, "shade_contrast": 0.5, "sun_direction": 45, "roofs": []},
    }


def _blueprint(rooms, tactical_rooms=None):
    return Blueprint(
        width=100, height=100, rooms=rooms, corridors=[], graph={i: [] for i in range(len(rooms))},
        seed=1, style="dungeon", tactical_rooms=tactical_rooms or [],
    )


def _obj_grid_pos(obj) -> tuple[float, float]:
    """Estrae (x, y) in quadretti dalla stringa Vector2( x, y ) di position."""
    inner = obj["position"][obj["position"].index("(") + 1 : obj["position"].index(")")]
    x_str, y_str = inner.split(",")
    return float(x_str) / 256, float(y_str) / 256


def _wall_points_of(level):
    return [parse_pv2(w["points"]) for w in level["walls"]]


def _min_distance_to_walls(x, y, level):
    best = math.inf
    for points in _wall_points_of(level):
        (x0, y0), (x1, y1) = points[0], points[-1]
        # distanza punto-segmento in quadretti (i punti dei muri sono in px)
        x0, y0, x1, y1 = x0 / 256, y0 / 256, x1 / 256, y1 / 256
        dx, dy = x1 - x0, y1 - y0
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            t = 0.0
        else:
            t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / length_sq))
        px, py = x0 + t * dx, y0 + t * dy
        best = min(best, math.hypot(x - px, y - py))
    return best


def test_density_none_places_nothing():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 20, 20), kind="sala")
    draw_room(level, ids, room, PALETTE)
    furnish(level, ids, _blueprint([room]), PALETTE, density="none", rng=random.Random(1))
    assert level["objects"] == []


@pytest.mark.parametrize("density,expected_rate", [("light", 0.05), ("medium", 0.12), ("heavy", 0.25)])
def test_density_respects_target_rate_within_tolerance(density, expected_rate):
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 20, 20), kind="sala")  # nessuna porta: nessun rifiuto per clearance
    draw_room(level, ids, room, PALETTE)
    furnish(level, ids, _blueprint([room]), PALETTE, density=density, rng=random.Random(7))

    area = room.rect.w * room.rect.h
    expected = area * expected_rate
    assert expected * 0.7 <= len(level["objects"]) <= expected * 1.05


def test_unknown_density_raises_explicit_error():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    draw_room(level, ids, room, PALETTE)
    with pytest.raises(ValueError):
        furnish(level, ids, _blueprint([room]), PALETTE, density="estremo", rng=random.Random(1))


def test_no_object_closer_than_half_tile_to_a_wall():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 15, 15), kind="sala")
    draw_room(level, ids, room, PALETTE)
    furnish(level, ids, _blueprint([room]), PALETTE, density="heavy", rng=random.Random(3))

    assert len(level["objects"]) > 0
    for obj in level["objects"]:
        x, y = _obj_grid_pos(obj)
        assert _min_distance_to_walls(x, y, level) >= 0.5 - 1e-6


def test_no_object_within_1_5_of_a_door():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 20, 20), kind="sala", doors=[Door(wall_index=0, t=0.5)])
    draw_room(level, ids, room, PALETTE)
    furnish(level, ids, _blueprint([room]), PALETTE, density="heavy", rng=random.Random(5))

    door_x, door_y = 10.0, 0.0  # centro del lato top di un Rect(0,0,20,20)
    for obj in level["objects"]:
        x, y = _obj_grid_pos(obj)
        assert math.hypot(x - door_x, y - door_y) >= 1.5 - 1e-6


def test_boss_room_is_furnished_more_densely_than_service_room():
    level_boss = _empty_level()
    level_service = _empty_level()
    ids_boss, ids_service = IdAllocator(), IdAllocator()
    boss = Room(rect=Rect(0, 0, 20, 20), kind="boss")
    service = Room(rect=Rect(0, 0, 20, 20), kind="servizio")
    draw_room(level_boss, ids_boss, boss, PALETTE)
    draw_room(level_service, ids_service, service, PALETTE)

    furnish(level_boss, ids_boss, _blueprint([boss]), PALETTE, density="medium", rng=random.Random(1))
    furnish(level_service, ids_service, _blueprint([service]), PALETTE, density="medium", rng=random.Random(1))

    assert len(level_boss["objects"]) > len(level_service["objects"])


def test_corridors_are_never_furnished():
    """blueprint.corridors non sono Room: furnish non li tocca mai."""
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 20, 20), kind="sala")
    draw_room(level, ids, room, PALETTE)
    bp = _blueprint([room])
    bp.corridors = [Rect(20, 0, 22, 30)]  # presente ma irrilevante per furnish
    furnish(level, ids, bp, PALETTE, density="heavy", rng=random.Random(1))
    for obj in level["objects"]:
        x, y = _obj_grid_pos(obj)
        assert x <= 20  # nessun oggetto nel corridoio (x in [20,22])


def test_tactical_rooms_get_cover_objects_spaced_3_to_4_tiles():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 20, 20), kind="sala")
    draw_room(level, ids, room, PALETTE)
    furnish(level, ids, _blueprint([room], tactical_rooms=[0]), PALETTE, density="none", rng=random.Random(9))

    assert len(level["objects"]) > 0  # density=none ma il nodo tattico riceve comunque coperture
    positions = [_obj_grid_pos(obj) for obj in level["objects"]]
    positions.sort()
    for (x1, y1), (x2, y2) in zip(positions, positions[1:]):
        if abs(y1 - y2) < 0.01:  # stessa riga della griglia
            assert 2.9 <= (x2 - x1) <= 4.1


def test_palette_without_accents_furnishes_nothing():
    level = _empty_level()
    ids = IdAllocator()
    room = Room(rect=Rect(0, 0, 20, 20), kind="sala")
    draw_room(level, ids, room, EMPTY_ACCENTS_PALETTE)
    furnish(level, ids, _blueprint([room], tactical_rooms=[0]), EMPTY_ACCENTS_PALETTE, density="heavy", rng=random.Random(1))
    assert level["objects"] == []


def test_same_seed_produces_identical_furnishing():
    def run():
        level = _empty_level()
        ids = IdAllocator()
        room = Room(rect=Rect(0, 0, 20, 20), kind="sala")
        draw_room(level, ids, room, PALETTE)
        furnish(level, ids, _blueprint([room]), PALETTE, density="medium", rng=random.Random(123))
        return [(o["position"], o["texture"]) for o in level["objects"]]

    assert run() == run()
