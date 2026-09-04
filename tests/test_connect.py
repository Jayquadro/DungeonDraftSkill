"""Test per ddforge.compose.connect (TASK-19), scritti PRIMA dell'implementazione
come richiesto esplicitamente da SPEC.md §6.6: rettangoli noti, un caso per
tipo di adiacenza."""

import pytest

from ddforge.assets import Palette
from ddforge.compose import connect, draw_room
from ddforge.ids import IdAllocator
from ddforge.model import Rect, Room
from ddforge.validate import validate

PALETTE = Palette(
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


def _count_portals(level):
    return sum(len(w["portals"]) for w in level["walls"])


def _full_doc(level, next_node_id):
    return {
        "header": {"asset_manifest": []},
        "world": {
            "format": 3, "width": 100, "height": 100, "next_node_id": next_node_id,
            "msi": {}, "grid": {}, "embedded": {},
            "levels": {"0": {
                **level,
                "label": "", "environment": {}, "layers": {}, "shapes": {"polygons": [], "walls": []},
                "tiles": {"cells": "PoolIntArray(  )"},
                "cave": {"bitmap": "PoolByteArray(  )", "entrance_bitmap": "PoolByteArray(  )"},
                "terrain": {"splat": "PoolByteArray(  )"}, "water": {}, "materials": {},
                "texts_vis": True,
            }},
        },
    }


def _errors_excluding_blob_size(doc):
    return [i for i in validate(doc) if i.severity == "error" and i.code not in ("DDF010", "DDF011")]


# ---------------------------------------------------------------------------
# Adiacenza orizzontale: room_b esattamente a destra di room_a, stessa altezza
# ---------------------------------------------------------------------------

def test_connect_horizontal_adjacency_full_overlap():
    level = _empty_level()
    ids = IdAllocator()
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(10, 0, 20, 10), kind="sala")
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)

    result = connect(level, ids, room_a, room_b, PALETTE)

    assert result["portal"] is not None
    t = result["portal"]["wall_distance"]
    assert 0.0 <= t <= 1.0
    assert _count_portals(level) == 1


def test_connect_horizontal_adjacency_portal_centered_on_full_overlap():
    """Le due stanze hanno la stessa altezza: l'overlap e l'intero muro,
    quindi la porta deve cadere esattamente al centro (t=0.5)."""
    level = _empty_level()
    ids = IdAllocator()
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(10, 0, 20, 10), kind="sala")
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)

    result = connect(level, ids, room_a, room_b, PALETTE)
    assert result["portal"]["wall_distance"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Adiacenza verticale
# ---------------------------------------------------------------------------

def test_connect_vertical_adjacency():
    level = _empty_level()
    ids = IdAllocator()
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(0, 10, 10, 20), kind="sala")
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)

    result = connect(level, ids, room_a, room_b, PALETTE)
    assert result["portal"] is not None
    assert _count_portals(level) == 1


# ---------------------------------------------------------------------------
# Adiacenza parziale: la porta deve centrarsi sulla sovrapposizione, non sul muro intero
# ---------------------------------------------------------------------------

def test_connect_partial_adjacency_centers_on_overlap_not_whole_wall():
    level = _empty_level()
    ids = IdAllocator()
    # room_a: x in [0,10], y in [0,10]. room_b: x in [10,20], y in [4,8].
    # muro condiviso a x=10, overlap y in [4,8] -> centro overlap y=6.
    # Sul muro intero di room_a (y da 0 a 10, lunghezza 10), y=6 sta a t=0.6.
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(10, 4, 20, 8), kind="sala")
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)

    result = connect(level, ids, room_a, room_b, PALETTE)
    assert result["portal"]["wall_distance"] == pytest.approx(0.6)


def test_connect_no_overlap_returns_corridor_not_a_direct_door():
    """Stesse x ma y separate da un gap: non adiacenti, niente muro condiviso."""
    level = _empty_level()
    ids = IdAllocator()
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(20, 0, 30, 10), kind="sala")  # gap di 10 quadretti, stessa y
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)

    result = connect(level, ids, room_a, room_b, PALETTE)
    assert result["portal"] is None
    assert len(result["corridors"]) >= 1


# ---------------------------------------------------------------------------
# Nessun contatto: corridoio dritto (un solo asse allineato)
# ---------------------------------------------------------------------------

def test_connect_straight_corridor_when_x_ranges_overlap():
    level = _empty_level()
    ids = IdAllocator()
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(0, 20, 10, 30), kind="sala")  # sotto, gap di 10 in y
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)

    result = connect(level, ids, room_a, room_b, PALETTE)
    assert result["portal"] is None
    assert len(result["corridors"]) == 1  # un solo segmento, nessuna piega
    assert len(result["portals"]) == 2  # una porta per stanza


# ---------------------------------------------------------------------------
# Nessun contatto: corridoio a L (nessun asse allineato)
# ---------------------------------------------------------------------------

def test_connect_l_shaped_corridor_when_no_axis_aligned():
    level = _empty_level()
    ids = IdAllocator()
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(20, 20, 30, 30), kind="sala")  # diagonale, nessun asse in comune
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)

    result = connect(level, ids, room_a, room_b, PALETTE)
    assert result["portal"] is None
    assert len(result["corridors"]) == 2  # due segmenti, una piega
    assert len(result["portals"]) == 2


def test_connect_l_corridor_result_passes_validate_with_no_errors_or_blocking_warnings():
    level = _empty_level()
    ids = IdAllocator()
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(20, 20, 30, 30), kind="sala")
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)
    connect(level, ids, room_a, room_b, PALETTE)

    doc = _full_doc(level, ids.next_free)
    assert _errors_excluding_blob_size(doc) == []
    warnings = {i.code for i in validate(doc) if i.severity == "warning"}
    assert "DDF102" not in warnings
    assert "DDF105" not in warnings


def test_connect_adjacent_rooms_result_passes_validate_with_no_errors():
    level = _empty_level()
    ids = IdAllocator()
    room_a = Room(rect=Rect(0, 0, 10, 10), kind="sala")
    room_b = Room(rect=Rect(10, 0, 20, 10), kind="sala")
    draw_room(level, ids, room_a, PALETTE)
    draw_room(level, ids, room_b, PALETTE)
    connect(level, ids, room_a, room_b, PALETTE)

    doc = _full_doc(level, ids.next_free)
    assert _errors_excluding_blob_size(doc) == []
