"""Test per ddforge.validate: DDF001-DDF015 (errori) e DDF101-DDF105 (warning)."""

import copy

from ddforge.validate import Issue, validate


def _base_doc():
    """Documento minimo valido, 2x2 quadretti, per fixture corrotte mirate."""
    return {
        "header": {
            "creation_build": "1.2.0.1 test",
            "asset_manifest": [
                {"id": "PACKID01", "name": "Pack", "author": "Autore", "version": "1"}
            ],
        },
        "world": {
            "format": 3,
            "width": 2,
            "height": 2,
            "next_node_id": "10",
            "msi": {},
            "grid": {},
            "embedded": {},
            "levels": {
                "0": {
                    "label": "Piano",
                    "environment": {},
                    "layers": {},
                    "shapes": {"polygons": [], "walls": []},
                    "tiles": {"cells": _pool_int([0] * 4)},
                    "patterns": [],
                    "walls": [
                        {
                            "points": "PoolVector2Array( 0, 0, 512, 0 )",
                            "texture": "res://textures/walls/stone.png",
                            "color": "ffffffff",
                            "loop": False,
                            "type": 1,
                            "joint": 0,
                            "normalize_uv": True,
                            "shadow": True,
                            "node_id": "1",
                            "portals": [
                                {
                                    "position": "Vector2( 256, 0 )",
                                    "rotation": 0.0,
                                    "scale": "Vector2( 1, 1 )",
                                    "direction": "Vector2( 0, 1 )",
                                    "texture": "res://textures/portals/door_00.png",
                                    "radius": 128,
                                    "wall_id": "1",
                                    "wall_distance": 0.5,
                                    "closed": True,
                                    "node_id": "2",
                                }
                            ],
                        }
                    ],
                    "portals": [],
                    "cave": {"bitmap": "PoolByteArray(  )", "entrance_bitmap": "PoolByteArray(  )"},
                    "terrain": {"splat": _pool_byte([0] * (2 * 2 * 64))},
                    "water": {},
                    "materials": {},
                    "paths": [],
                    "objects": [],
                    "lights": [
                        {
                            "position": "Vector2( 100, 100 )",
                            "range": 3.0,
                            "color": "aabbcc",
                            "intensity": 0.7,
                            "shadows": True,
                            "node_id": "3",
                        }
                    ],
                    "roofs": {"shade": True, "shade_contrast": 0.5, "sun_direction": 45, "roofs": []},
                    "texts": [],
                    "texts_vis": True,
                }
            },
        },
    }


def _pool_int(values):
    return "PoolIntArray( " + ", ".join(str(v) for v in values) + " )"


def _pool_byte(values):
    return "PoolByteArray( " + ", ".join(str(v) for v in values) + " )"


def _errors(doc):
    return [i for i in validate(doc) if i.severity == "error"]


def _codes(doc):
    return {i.code for i in _errors(doc)}


def test_base_doc_is_valid():
    assert _errors(_base_doc()) == []


def test_validate_returns_issue_instances():
    doc = _base_doc()
    del doc["header"]
    issues = validate(doc)
    assert all(isinstance(i, Issue) for i in issues)
    assert all(i.severity in ("error", "warning") for i in issues)
    assert all(i.path is not None for i in issues)


def test_ddf001_missing_header():
    doc = _base_doc()
    del doc["header"]
    assert "DDF001" in _codes(doc)


def test_ddf001_format_not_int():
    doc = _base_doc()
    doc["world"]["format"] = "3"
    assert "DDF001" in _codes(doc)


def test_ddf002_missing_world_key():
    doc = _base_doc()
    del doc["world"]["msi"]
    assert "DDF002" in _codes(doc)


def test_ddf003_missing_level_key():
    doc = _base_doc()
    del doc["world"]["levels"]["0"]["texts_vis"]
    assert "DDF003" in _codes(doc)


def test_ddf003_extra_level_key():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["campo_inventato"] = 1
    assert "DDF003" in _codes(doc)


def test_ddf004_roofs_not_dict_with_roofs_list():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["roofs"] = {"roofs": "not-a-list"}
    assert "DDF004" in _codes(doc)


def test_ddf004_shapes_not_dict():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["shapes"] = []
    assert "DDF004" in _codes(doc)


def test_ddf004_drawable_list_not_a_list():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["objects"] = {}
    assert "DDF004" in _codes(doc)


def test_ddf005_duplicate_node_id():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["portals"][0]["node_id"] = "1"  # duplica il muro
    assert "DDF005" in _codes(doc)


def test_ddf006_next_node_id_not_greater_than_max():
    doc = _base_doc()
    doc["world"]["next_node_id"] = "2"  # max id usato e 3 (la luce)
    assert "DDF006" in _codes(doc)


def test_ddf007_points_not_pool_vector2_array():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["points"] = "Vector2( 0, 0 )"
    assert "DDF007" in _codes(doc)


def test_ddf007_odd_number_of_coordinates():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["points"] = "PoolVector2Array( 0, 0, 512 )"
    assert "DDF007" in _codes(doc)


def test_ddf008_position_not_vector2_format():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["portals"][0]["position"] = "100, 100"
    assert "DDF008" in _codes(doc)


def test_ddf009_color_not_8_hex_digits():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["color"] = "ffffff"  # 6 cifre, non 8
    assert "DDF009" in _codes(doc)


def test_ddf009_light_color_accepts_6_digits_but_not_5():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["lights"][0]["color"] = "aabbc"  # 5 cifre
    assert "DDF009" in _codes(doc)


def test_ddf010_tiles_cells_wrong_length():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["tiles"]["cells"] = _pool_int([0, 0, 0])  # atteso 4
    assert "DDF010" in _codes(doc)


def test_ddf011_terrain_splat_wrong_length():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["terrain"]["splat"] = _pool_byte([0, 0])  # atteso 256
    assert "DDF011" in _codes(doc)


def test_ddf012_portal_wall_id_does_not_match_any_wall():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["portals"][0]["wall_id"] = "ff"
    assert "DDF012" in _codes(doc)


def test_ddf013_wall_distance_out_of_range():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["portals"][0]["wall_distance"] = 1.5
    assert "DDF013" in _codes(doc)


def test_ddf014_pack_id_absent_from_manifest():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["texture"] = "res://packs/NONEXIST/textures/walls/x.png"
    assert "DDF014" in _codes(doc)


def test_ddf014_accepts_known_pack_id():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["texture"] = "res://packs/PACKID01/textures/walls/x.png"
    assert "DDF014" not in _codes(doc)


def test_ddf015_rotation_not_finite():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["portals"][0]["rotation"] = float("nan")
    assert "DDF015" in _codes(doc)


def test_ddf015_rotation_is_string():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["portals"][0]["rotation"] = "0.0"
    assert "DDF015" in _codes(doc)


def test_freeform_top_level_portal_not_checked_by_ddf012_013():
    """Lo schema libero scoperto in TASK-2 non ha wall_id/wall_distance:
    non deve produrre DDF012/013, solo i normali controlli di campo."""
    doc = _base_doc()
    doc["world"]["levels"]["0"]["portals"].append(
        {
            "position": "Vector2( 10, 10 )",
            "rotation": 0.0,
            "texture": "res://textures/portals/door_wood_single.png",
            "occludes_light": True,
            "node_id": "9",
        }
    )
    codes = _codes(doc)
    assert "DDF012" not in codes
    assert "DDF013" not in codes


def test_validate_never_raises_on_wildly_malformed_document():
    for broken in [
        {},
        {"header": None, "world": None},
        {"header": {}, "world": {"format": 3, "levels": "not-a-dict"}},
        {"header": {}, "world": {"format": 3, "levels": {"0": None}}},
        {"header": {}, "world": {"format": 3, "levels": {"0": {"walls": [None]}}}},
        None,
        [],
        "stringa",
        42,
    ]:
        issues = validate(broken)
        assert isinstance(issues, list)


def test_validate_on_real_demo_m1_output_has_zero_errors():
    import sys
    from pathlib import Path

    scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from demo_m1 import build_demo

    assert _errors(build_demo()) == []


def test_validate_does_not_mutate_input_document():
    doc = _base_doc()
    before = copy.deepcopy(doc)
    validate(doc)
    assert doc == before


# ---------------------------------------------------------------------------
# DDF101-105: warning
# ---------------------------------------------------------------------------

def _warnings(doc):
    return [i for i in validate(doc) if i.severity == "warning"]


def _warning_codes(doc):
    return {i.code for i in _warnings(doc)}


def test_base_doc_has_no_warnings():
    assert _warnings(_base_doc()) == []


def test_ddf101_object_position_outside_canvas():
    doc = _base_doc()  # canvas 2x2 quadretti = 512x512 px
    doc["world"]["levels"]["0"]["objects"].append(
        {
            "position": "Vector2( 9999, 9999 )",
            "rotation": 0.0,
            "scale": "Vector2( 1, 1 )",
            "mirror": False,
            "texture": "res://textures/objects/x.png",
            "layer": 100,
            "shadow": True,
            "block_light": False,
            "node_id": "50",
        }
    )
    assert "DDF101" in _warning_codes(doc)


def test_ddf101_wall_points_inside_canvas_no_warning():
    assert "DDF101" not in _warning_codes(_base_doc())


def test_ddf102_room_with_two_connected_walls_and_no_door():
    doc = _base_doc()
    level = doc["world"]["levels"]["0"]
    level["walls"] = [
        {
            "points": "PoolVector2Array( 0, 0, 512, 0 )",
            "texture": "res://textures/walls/stone.png",
            "color": "ffffffff", "loop": False, "type": 1, "joint": 0,
            "normalize_uv": True, "shadow": True, "node_id": "1", "portals": [],
        },
        {
            "points": "PoolVector2Array( 512, 0, 512, 512 )",
            "texture": "res://textures/walls/stone.png",
            "color": "ffffffff", "loop": False, "type": 1, "joint": 0,
            "normalize_uv": True, "shadow": True, "node_id": "4", "portals": [],
        },
    ]
    assert "DDF102" in _warning_codes(doc)


def test_ddf102_no_warning_when_group_has_a_door():
    assert "DDF102" not in _warning_codes(_base_doc())  # il muro base ha gia una porta


def test_ddf103_wall_with_single_point():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["walls"][0]["points"] = "PoolVector2Array( 0, 0 )"
    doc["world"]["levels"]["0"]["walls"][0]["portals"] = []
    assert "DDF103" in _warning_codes(doc)


def test_ddf104_pattern_with_two_points():
    doc = _base_doc()
    doc["world"]["levels"]["0"]["patterns"].append(
        {
            "position": "Vector2( 0, 0 )", "shape_rotation": 0, "rotation": 0,
            "scale": "Vector2( 1, 1 )",
            "points": "PoolVector2Array( 0, 0, 100, 100 )",
            "layer": -400, "color": "ffffffff", "outline": False,
            "texture": "res://textures/patterns/x.png", "node_id": "60",
        }
    )
    assert "DDF104" in _warning_codes(doc)


def test_ddf105_two_portals_too_close_on_same_wall():
    doc = _base_doc()
    wall = doc["world"]["levels"]["0"]["walls"][0]
    second_portal = copy.deepcopy(wall["portals"][0])
    second_portal["node_id"] = "5"
    second_portal["wall_distance"] = 0.52  # a 0.02 dalla prima (0.5): < 0.05
    wall["portals"].append(second_portal)
    doc["world"]["next_node_id"] = "10"
    assert "DDF105" in _warning_codes(doc)


def test_ddf105_no_warning_when_portals_far_apart():
    doc = _base_doc()
    wall = doc["world"]["levels"]["0"]["walls"][0]
    second_portal = copy.deepcopy(wall["portals"][0])
    second_portal["node_id"] = "5"
    second_portal["wall_distance"] = 0.9
    wall["portals"].append(second_portal)
    doc["world"]["next_node_id"] = "10"
    assert "DDF105" not in _warning_codes(doc)


def test_warnings_do_not_block_an_otherwise_valid_document():
    """I warning non alzano la severity a error: un documento valido con
    warning resta senza errori."""
    doc = _base_doc()
    doc["world"]["levels"]["0"]["objects"].append(
        {
            "position": "Vector2( 9999, 9999 )",
            "rotation": 0.0,
            "scale": "Vector2( 1, 1 )",
            "mirror": False,
            "texture": "res://textures/objects/x.png",
            "layer": 100,
            "shadow": True,
            "block_light": False,
            "node_id": "50",
        }
    )
    doc["world"]["next_node_id"] = "51"
    assert "DDF101" in _warning_codes(doc)
    assert _errors(doc) == []
