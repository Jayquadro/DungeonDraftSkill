"""TASK-15: fixture corrotte derivate dal template 8x8 reale (TASK-5).

Criterio di completamento di M2 (SPEC.md §5, §7): per ogni codice DDFxxx,
una fixture che lo viola (un difetto per fixture) e un test che verifica
che validate() lo segnali con severity e path corretti.

reference_8x8.dungeondraft_map (TASK-5) non contiene muri, portali,
pattern ne luci (solo 5 oggetti e 1 path): valid_doc parte da una deepcopy
del documento reale e aggiunge un esemplare di ciascun tipo mancante, con
valori realistici presi da docs/format.md, cosi ogni test qui sotto
corrompe un file derivato da un export genuino, non costruito da zero.
"""

import copy

from ddforge.validate import validate

WALL_ID = "10"
PORTAL_ID = "11"
PATTERN_ID = "12"
LIGHT_ID = "13"


def _wall():
    return {
        "points": "PoolVector2Array( 0, 0, 512, 0 )",
        "texture": "res://textures/walls/stone.png",
        "color": "ffffffff",
        "loop": False,
        "type": 1,
        "joint": 0,
        "normalize_uv": True,
        "shadow": True,
        "node_id": WALL_ID,
        "portals": [_portal()],
    }


def _portal():
    return {
        "position": "Vector2( 256, 0 )",
        "rotation": 0.0,
        "scale": "Vector2( 1, 1 )",
        "direction": "Vector2( 0, 1 )",
        "texture": "res://textures/portals/door_00.png",
        "radius": 128,
        "wall_id": WALL_ID,
        "wall_distance": 0.5,
        "closed": True,
        "node_id": PORTAL_ID,
    }


def _pattern():
    return {
        "position": "Vector2( 0, 0 )",
        "shape_rotation": 0,
        "rotation": 0,
        "scale": "Vector2( 1, 1 )",
        "points": "PoolVector2Array( 0, 0, 256, 0, 256, 256, 0, 256 )",
        "layer": -400,
        "color": "ffffffff",
        "outline": False,
        "texture": "res://textures/patterns/normal/stone_floor.png",
        "node_id": PATTERN_ID,
    }


def _light():
    return {
        "position": "Vector2( 100, 100 )",
        "range": 3.0,
        "color": "aabbcc",
        "intensity": 0.7,
        "shadows": True,
        "node_id": LIGHT_ID,
    }


def _valid_doc(reference_8x8_doc):
    doc = copy.deepcopy(reference_8x8_doc)
    level = doc["world"]["levels"]["0"]
    level["texts_vis"] = True  # allinea a LEVEL_KEYS build 1.2.0.1, docs/format.md §12
    level["walls"] = [_wall()]
    level["patterns"] = [_pattern()]
    level["lights"] = [_light()]
    doc["world"]["next_node_id"] = "14"  # > 0x13, il piu alto node_id in uso
    return doc


def _find(issues, code):
    return next((i for i in issues if i.code == code), None)


def _wall0(doc):
    return doc["world"]["levels"]["0"]["walls"][0]


def _portal0(doc):
    return _wall0(doc)["portals"][0]


def test_valid_doc_derived_from_real_fixture_has_zero_errors(reference_8x8_doc):
    """AC4: nessun falso positivo su una fixture valida (derivata dal file reale)."""
    doc = _valid_doc(reference_8x8_doc)
    errors = [i for i in validate(doc) if i.severity == "error"]
    assert errors == []


def test_ddf001_missing_world(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    del doc["world"]
    found = _find(validate(doc), "DDF001")
    assert found is not None and found.severity == "error" and found.path


def test_ddf002_missing_grid(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    del doc["world"]["grid"]
    found = _find(validate(doc), "DDF002")
    assert found is not None and found.severity == "error" and found.path == "world.grid"


def test_ddf003_missing_level_key(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    del doc["world"]["levels"]["0"]["water"]
    found = _find(validate(doc), "DDF003")
    assert found is not None and found.severity == "error" and found.path


def test_ddf004_materials_not_a_dict(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    doc["world"]["levels"]["0"]["materials"] = []
    found = _find(validate(doc), "DDF004")
    assert found is not None and found.severity == "error"


def test_ddf005_duplicate_node_id(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    doc["world"]["levels"]["0"]["patterns"][0]["node_id"] = WALL_ID
    found = _find(validate(doc), "DDF005")
    assert found is not None and found.severity == "error" and found.path


def test_ddf006_next_node_id_too_low(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    doc["world"]["next_node_id"] = "1"
    found = _find(validate(doc), "DDF006")
    assert found is not None and found.severity == "error" and found.path == "world.next_node_id"


def test_ddf007_wall_points_not_pool_vector2_array(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _wall0(doc)["points"] = "not-a-pool-array"
    found = _find(validate(doc), "DDF007")
    assert found is not None and found.severity == "error"
    assert found.path == "world.levels.0.walls[0].points"


def test_ddf008_portal_position_not_vector2(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _portal0(doc)["position"] = "(1, 2)"
    found = _find(validate(doc), "DDF008")
    assert found is not None and found.severity == "error"
    assert found.path == "world.levels.0.walls[0].portals[0].position"


def test_ddf009_wall_color_not_8_hex_digits(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _wall0(doc)["color"] = "zzzzzzzz"
    found = _find(validate(doc), "DDF009")
    assert found is not None and found.severity == "error"


def test_ddf010_tiles_cells_wrong_length(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    doc["world"]["levels"]["0"]["tiles"]["cells"] = "PoolIntArray( 1, 2, 3 )"
    found = _find(validate(doc), "DDF010")
    assert found is not None and found.severity == "error"


def test_ddf011_terrain_splat_wrong_length(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    doc["world"]["levels"]["0"]["terrain"]["splat"] = "PoolByteArray( 1, 2 )"
    found = _find(validate(doc), "DDF011")
    assert found is not None and found.severity == "error"


def test_ddf012_portal_wall_id_dangling(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _portal0(doc)["wall_id"] = "ffff"
    found = _find(validate(doc), "DDF012")
    assert found is not None and found.severity == "error"


def test_ddf013_wall_distance_out_of_range(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _portal0(doc)["wall_distance"] = -0.1
    found = _find(validate(doc), "DDF013")
    assert found is not None and found.severity == "error"


def test_ddf014_pack_id_absent_from_manifest(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _wall0(doc)["texture"] = "res://packs/INESISTENTE/textures/walls/x.png"
    found = _find(validate(doc), "DDF014")
    assert found is not None and found.severity == "error"


def test_ddf015_portal_rotation_not_finite(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _portal0(doc)["rotation"] = float("inf")
    found = _find(validate(doc), "DDF015")
    assert found is not None and found.severity == "error"


def test_ddf101_light_position_outside_canvas(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    # canvas 8x8 quadretti = 2048x2048 px
    doc["world"]["levels"]["0"]["lights"][0]["position"] = "Vector2( 999999, 999999 )"
    found = _find(validate(doc), "DDF101")
    assert found is not None and found.severity == "warning"


def test_ddf102_wall_group_without_any_door(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _wall0(doc)["portals"] = []
    # Un singolo muro non loopato non basta a formare un perimetro chiuso
    # (TASK-19, validate.py._check_ddf102_unreachable_rooms): con loop=True
    # e invece un poligono chiuso a se stante, quindi resta un candidato
    # valido per l'euristica "nessuna porta".
    _wall0(doc)["loop"] = True
    found = _find(validate(doc), "DDF102")
    assert found is not None and found.severity == "warning"


def test_ddf103_wall_with_single_point(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    _wall0(doc)["points"] = "PoolVector2Array( 0, 0 )"
    _wall0(doc)["portals"] = []
    found = _find(validate(doc), "DDF103")
    assert found is not None and found.severity == "warning"


def test_ddf104_pattern_with_two_points(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    doc["world"]["levels"]["0"]["patterns"][0]["points"] = "PoolVector2Array( 0, 0, 10, 10 )"
    found = _find(validate(doc), "DDF104")
    assert found is not None and found.severity == "warning"


def test_ddf105_two_portals_too_close(reference_8x8_doc):
    doc = _valid_doc(reference_8x8_doc)
    second = copy.deepcopy(_portal0(doc))
    second["node_id"] = "15"
    second["wall_distance"] = 0.51
    _wall0(doc)["portals"].append(second)
    doc["world"]["next_node_id"] = "16"
    found = _find(validate(doc), "DDF105")
    assert found is not None and found.severity == "warning"
