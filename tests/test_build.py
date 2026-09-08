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
    add_water_polygon,
    set_cave_bitmap,
)
from ddforge.cave_bitmap import cave_grid_shape, decode_cave_bitmap
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


def test_add_light_always_emits_rotation_and_texture():
    """TASK-42: una luce senza `texture` manda Dungeondraft in loop infinito
    al caricamento. I default vengono dal Light2D.tscn interno del programma."""
    level = _empty_level()
    ids = IdAllocator()
    light = add_light(level, ids, 5, 5)

    assert light["rotation"] == 0.0
    assert light["texture"] == "res://textures/lights/soft.png"
    assert light["color"] == "efc05c"
    assert light["intensity"] == 0.75
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


def test_set_cave_bitmap_writes_a_roundtrippable_blob():
    level = {"cave": {"bitmap": "PoolByteArray(  )", "ground_color": "ffffffff"}}
    width, height = 5, 4
    grid_w, grid_h = cave_grid_shape(width, height)
    grid = [[1 if (x + y) % 7 == 0 else 0 for x in range(grid_w)] for y in range(grid_h)]

    set_cave_bitmap(level, grid, width, height)

    assert decode_cave_bitmap(level["cave"]["bitmap"], width, height) == grid
    assert level["cave"]["ground_color"] == "ffffffff"  # non toccato (decision-1)


def test_add_water_polygon_creates_tree_on_first_use():
    # blank_80x80 parte senza 'tree' (solo disable_border, TASK-33).
    level: dict = {"water": {"disable_border": False}}
    ids = IdAllocator()

    polygon = add_water_polygon(level, ids, [(0, 0), (4, 0), (4, 2), (0, 2)])

    tree = level["water"]["tree"]
    assert tree["children"] == [polygon]
    assert tree["polygon"] == "PoolVector2Array(  )"  # nodo contenitore, vuoto
    assert tree["deep_color"] == "00000000"
    assert parse_pv2(polygon["polygon"]) == [(0, 0), (1024, 0), (1024, 512), (0, 512)]


def test_add_water_polygon_appends_to_existing_tree():
    level: dict = {"water": {"disable_border": False}}
    ids = IdAllocator()

    first = add_water_polygon(level, ids, [(0, 0), (2, 0), (2, 2)])
    second = add_water_polygon(level, ids, [(5, 5), (7, 5), (7, 7)])

    assert level["water"]["tree"]["children"] == [first, second]


def test_add_water_polygon_refs_are_unique_and_use_the_shared_allocator():
    level: dict = {"water": {"disable_border": False}}
    ids = IdAllocator()

    polygon = add_water_polygon(level, ids, [(0, 0), (1, 0), (1, 1)])

    tree = level["water"]["tree"]
    assert tree["ref"] != polygon["ref"]
    assert isinstance(polygon["ref"], int)


def test_add_water_polygon_custom_colors():
    level: dict = {"water": {"disable_border": False}}
    ids = IdAllocator()

    polygon = add_water_polygon(
        level, ids, [(0, 0), (1, 0), (1, 1)],
        deep_color="ff112233", shallow_color="ff445566", blend_distance=2.0,
    )

    assert polygon["deep_color"] == "ff112233"
    assert polygon["shallow_color"] == "ff445566"
    assert polygon["blend_distance"] == 2.0
