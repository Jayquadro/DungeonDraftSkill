"""Test per ddforge.build: le primitive di disegno."""

import pytest

from ddforge.build import (
    add_light,
    add_object,
    add_pattern,
    add_path,
    add_polygon_pattern,
    add_portal,
    add_roof,
    add_text,
    add_wall,
)
from ddforge.godot import parse_pv2
from ddforge.ids import IdAllocator
from ddforge.model import Rect


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


def test_add_wall_converts_grid_to_px():
    level = _empty_level()
    ids = IdAllocator()
    wall = add_wall(level, ids, [(2, 2), (8, 2)], "res://textures/walls/stone.png")

    assert parse_pv2(wall["points"]) == [(512.0, 512.0), (2048.0, 512.0)]
    assert wall in level["walls"]
    assert wall["portals"] == []


def test_add_wall_rejects_repeated_closing_point_with_loop():
    level = _empty_level()
    ids = IdAllocator()
    square = [(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)]
    with pytest.raises(ValueError):
        add_wall(level, ids, square, "res://textures/walls/stone.png", loop=True)


def test_add_wall_loop_without_repeated_point_is_fine():
    level = _empty_level()
    ids = IdAllocator()
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    wall = add_wall(level, ids, square, "res://textures/walls/stone.png", loop=True)
    assert wall["loop"] is True
    assert len(parse_pv2(wall["points"])) == 4


def test_add_portal_nested_in_wall_not_top_level():
    level = _empty_level()
    ids = IdAllocator()
    wall = add_wall(level, ids, [(0, 0), (10, 0)], "res://textures/walls/stone.png")
    portal = add_portal(wall, ids, t=0.5, direction=(0, 1), texture="res://textures/portals/door_00.png")

    assert portal in wall["portals"]
    assert level["portals"] == []  # mai a livello mappa
    assert portal["wall_id"] == wall["node_id"]
    assert portal["wall_distance"] == 0.5


def test_add_portal_position_interpolated_along_wall():
    level = _empty_level()
    ids = IdAllocator()
    wall = add_wall(level, ids, [(0, 0), (10, 0)], "res://textures/walls/stone.png")
    portal = add_portal(wall, ids, t=0.5, direction=(0, 1), texture="door.png")

    # muro di 10 quadretti (2560px), t=0.5 -> a meta, cioe 1280px
    assert portal["position"] == "Vector2( 1280, 0 )"


def test_add_portal_does_not_split_wall_points():
    level = _empty_level()
    ids = IdAllocator()
    wall = add_wall(level, ids, [(0, 0), (10, 0)], "res://textures/walls/stone.png")
    original_points = wall["points"]
    add_portal(wall, ids, t=0.3, direction=(0, 1), texture="door.png")
    assert wall["points"] == original_points


def test_add_portal_rejects_out_of_range_t():
    level = _empty_level()
    ids = IdAllocator()
    wall = add_wall(level, ids, [(0, 0), (10, 0)], "res://textures/walls/stone.png")
    with pytest.raises(ValueError):
        add_portal(wall, ids, t=1.5, direction=(0, 1), texture="door.png")


def test_add_portal_omits_locked_key_when_false():
    level = _empty_level()
    ids = IdAllocator()
    wall = add_wall(level, ids, [(0, 0), (10, 0)], "res://textures/walls/stone.png")
    portal = add_portal(wall, ids, t=0.5, direction=(0, 1), texture="door.png", locked=False)
    assert "locked" not in portal


def test_add_portal_includes_locked_key_when_true():
    level = _empty_level()
    ids = IdAllocator()
    wall = add_wall(level, ids, [(0, 0), (10, 0)], "res://textures/walls/stone.png")
    portal = add_portal(wall, ids, t=0.5, direction=(0, 1), texture="door.png", locked=True)
    assert portal["locked"] is True


def test_add_pattern_rectangle_matches_polygon_corners():
    level = _empty_level()
    ids = IdAllocator()
    pattern = add_pattern(level, ids, Rect(0, 0, 2, 1), "res://textures/patterns/normal/stone_floor.png")
    points = parse_pv2(pattern["points"])
    assert points == [(0.0, 0.0), (512.0, 0.0), (512.0, 256.0), (0.0, 256.0)]


def test_add_polygon_pattern_arbitrary_shape():
    level = _empty_level()
    ids = IdAllocator()
    pattern = add_polygon_pattern(level, ids, [(0, 0), (1, 0), (0.5, 1)], "res://textures/patterns/cave.png")
    assert len(parse_pv2(pattern["points"])) == 3


def test_add_object_position_in_px():
    level = _empty_level()
    ids = IdAllocator()
    obj = add_object(level, ids, 3, 4, "res://textures/objects/camp/campfire_07.png")
    assert obj["position"] == "Vector2( 768, 1024 )"
    assert obj in level["objects"]


def test_add_path_position_is_first_point_edit_points_relative():
    level = _empty_level()
    ids = IdAllocator()
    path = add_path(level, ids, [(2, 2), (10, 2)], "res://textures/paths/cobble.png")

    assert path["position"] == "Vector2( 512, 512 )"
    edit_points = parse_pv2(path["edit_points"])
    assert edit_points[0] == (0.0, 0.0)
    assert edit_points[1] == (pytest.approx(2048.0), 0.0)


def test_add_roof_goes_into_roofs_roofs_list():
    level = _empty_level()
    ids = IdAllocator()
    roof = add_roof(level, ids, [(0, 0), (5, 5)], "res://textures/roofs/flat_clay_red/tiles.png")

    assert roof in level["roofs"]["roofs"]
    assert "roofs" not in level or "roof" not in level  # niente lista di primo livello


def test_add_light_default_variant_has_no_rotation_or_texture():
    level = _empty_level()
    ids = IdAllocator()
    light = add_light(level, ids, 5, 5)

    assert "rotation" not in light
    assert "texture" not in light
    assert light["color"] == "ffffff"
    assert light in level["lights"]


def test_add_light_sprite_variant_with_rotation_and_texture():
    level = _empty_level()
    ids = IdAllocator()
    light = add_light(level, ids, 5, 5, rotation=0.0, texture="res://textures/lights/fragments.png", color="ffeccd8b")

    assert light["rotation"] == 0.0
    assert light["texture"] == "res://textures/lights/fragments.png"


def test_add_text_matches_observed_schema():
    level = _empty_level()
    ids = IdAllocator()
    text = add_text(level, ids, 10, 10, "Fiumicello")

    assert text["text"] == "Fiumicello"
    assert text["font_name"] == "Libre Baskerville"
    assert text["box_shape"] == 0
    assert text in level["texts"]


def test_all_node_ids_are_unique_across_a_scene():
    level = _empty_level()
    ids = IdAllocator()
    wall1 = add_wall(level, ids, [(0, 0), (10, 0)], "wall.png")
    wall2 = add_wall(level, ids, [(0, 0), (0, 10)], "wall.png")
    portal = add_portal(wall1, ids, t=0.5, direction=(0, 1), texture="door.png")
    obj = add_object(level, ids, 1, 1, "obj.png")
    light = add_light(level, ids, 1, 1)
    text = add_text(level, ids, 1, 1, "hi")
    roof = add_roof(level, ids, [(0, 0), (5, 5)], "roof.png")
    path = add_path(level, ids, [(0, 0), (5, 0)], "path.png")
    pattern = add_pattern(level, ids, Rect(0, 0, 5, 5), "floor.png")

    all_ids = [wall1["node_id"], wall2["node_id"], portal["node_id"], obj["node_id"],
               light["node_id"], text["node_id"], roof["node_id"], path["node_id"],
               pattern["node_id"]]
    assert len(all_ids) == len(set(all_ids))
