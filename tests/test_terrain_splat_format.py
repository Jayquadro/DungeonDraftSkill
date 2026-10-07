"""Blocca la codifica di `terrain.splat` scoperta nello spike TASK-67.

Stesso schema di tests/test_cave_bitmap_format.py (TASK-31/32): questi test
proteggono due cose che altrimenti si perderebbero in silenzio:

1. `tests/fixtures/cave_freehand_80x80.dungeondraft_map` e l'UNICO file reale
   con terreno dipinto a mano trovato sul disco di Jay (lo stesso file del
   campione cave freehand — terreno e grotta disegnati nella stessa
   sessione), quindi l'unica evidenza vera della codifica;
2. la codifica documentata in docs/format.md §15 e quella che il file vero
   usa davvero.
"""

import json
from pathlib import Path

from ddforge.build import set_cave_floor_texture
from ddforge.terrain_splat import (
    CAVE_FLOOR_TEXTURES, decode_terrain_splat, default_weights,
    encode_terrain_splat, paint_tiles, terrain_grid_shape,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    return doc, doc["world"]["width"], doc["world"]["height"]


def _parse_byte_array(blob: str) -> list[int]:
    inner = blob[blob.index("(") + 1 : blob.rindex(")")].strip()
    return [int(x) for x in inner.split(",")] if inner else []


def test_splat_length_follows_the_subcell_grid_formula():
    """A differenza di cave.bitmap, nessun margine: width*height*64 byte
    esatti (4 sotto-celle per lato x 4 byte per sotto-cella)."""
    for width, height, expected in [(8, 8, 8 * 8 * 64), (80, 80, 80 * 80 * 64)]:
        grid_w, grid_h = terrain_grid_shape(width, height)
        assert (grid_w, grid_h) == (4 * width, 4 * height)
        assert grid_w * grid_h * 4 == expected


def test_real_sample_has_the_predicted_length():
    doc, width, height = _load(REPO_ROOT / "tests" / "fixtures" / "cave_freehand_80x80.dungeondraft_map")
    grid_w, grid_h = terrain_grid_shape(width, height)
    expected = grid_w * grid_h * 4
    blob = doc["world"]["levels"]["0"]["terrain"]["splat"]
    assert len(_parse_byte_array(blob)) == expected


def test_roundtrip_is_byte_identical_on_the_real_sample():
    """La prova piu forte: decodificare e ricodificare il blob scritto da
    Dungeondraft restituisce gli stessi identici byte."""
    doc, width, height = _load(REPO_ROOT / "tests" / "fixtures" / "cave_freehand_80x80.dungeondraft_map")
    original = doc["world"]["levels"]["0"]["terrain"]["splat"]
    grid = decode_terrain_splat(original, width, height)
    assert encode_terrain_splat(grid, width, height) == original


def test_real_sample_is_mostly_default_with_one_painted_blob():
    """Jay ha dipinto una zona sola (slot 3, texture_3=sand) sopra il resto
    non toccato (slot 1 pieno): e il pattern che ha permesso di isolare la
    codifica (vedi la nota di chiusura del task per i dettagli dei due test
    di ipotesi)."""
    doc, width, height = _load(REPO_ROOT / "tests" / "fixtures" / "cave_freehand_80x80.dungeondraft_map")
    grid = decode_terrain_splat(doc["world"]["levels"]["0"]["terrain"]["splat"], width, height)

    default = (255, 0, 0, 0)
    non_default = [(x, y) for y, row in enumerate(grid) for x, g in enumerate(row) if g != default]
    assert len(non_default) > 1000

    xs = [p[0] for p in non_default]
    ys = [p[1] for p in non_default]
    bbox_area = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    # Macchia coerente: densita' alta nel suo bounding box, non rumore
    # sparso su tutta la mappa (che darebbe una densita' vicino a zero).
    assert len(non_default) / bbox_area > 0.3


def test_default_weights_is_fully_one_slot():
    grid = default_weights(4, 3, slot=2)
    assert all(cell == (0, 255, 0, 0) for row in grid for cell in row)


def test_paint_tiles_full_coverage_is_one_hot_on_masked_tiles_only():
    width, height = 3, 2
    base = default_weights(width, height, slot=1)
    mask = [[False, True, False], [False, False, True]]
    painted = paint_tiles(base, mask, slot=3, coverage=1.0)

    for ty in range(height):
        for tx in range(width):
            expect_painted = mask[ty][tx]
            for sy in range(4):
                for sx in range(4):
                    cell = painted[ty * 4 + sy][tx * 4 + sx]
                    if expect_painted:
                        assert cell == (0, 0, 255, 0)
                    else:
                        assert cell == (255, 0, 0, 0)

    # Non muta l'originale.
    assert base == default_weights(width, height, slot=1)


def test_paint_tiles_partial_coverage_blends_towards_the_target_slot():
    width, height = 1, 1
    base = default_weights(width, height, slot=1)
    painted = paint_tiles(base, [[True]], slot=3, coverage=0.4)
    cell = painted[0][0]
    assert cell == (round(255 * 0.6), 0, round(255 * 0.4), 0)


def test_paint_tiles_rejects_mismatched_mask_size():
    base = default_weights(3, 2, slot=1)
    try:
        paint_tiles(base, [[True]], slot=1)
    except ValueError:
        pass
    else:
        raise AssertionError("una mask di dimensioni sbagliate deve alzare ValueError")


def test_cave_floor_texture_options_do_not_touch_the_bitmap():
    """D6: cambiare il pavimento della grotta non deve mai toccare la forma
    (cave.bitmap/entrance_bitmap)."""
    level = {
        "cave": {
            "texture": CAVE_FLOOR_TEXTURES["colorable"],
            "ground_color": "ff7f7e71",
            "wall_color": "ff7f7e71",
            "bitmap": "PoolByteArray( 1, 2, 3 )",
            "entrance_bitmap": "PoolByteArray( 4, 5, 6 )",
        }
    }
    before_bitmap = level["cave"]["bitmap"]
    before_entrance = level["cave"]["entrance_bitmap"]

    set_cave_floor_texture(level, "limestone", ground_color="ff204010")

    assert level["cave"]["texture"] == CAVE_FLOOR_TEXTURES["limestone"]
    assert level["cave"]["ground_color"] == "ff204010"
    assert level["cave"]["bitmap"] == before_bitmap
    assert level["cave"]["entrance_bitmap"] == before_entrance


def test_cave_floor_rejects_unknown_key():
    level = {"cave": {"texture": CAVE_FLOOR_TEXTURES["colorable"]}}
    try:
        set_cave_floor_texture(level, "non_esiste")
    except ValueError:
        pass
    else:
        raise AssertionError("una chiave sconosciuta deve alzare ValueError")
