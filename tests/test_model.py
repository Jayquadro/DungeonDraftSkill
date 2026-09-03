"""Test per ddforge.model.Rect."""

from ddforge.model import Blueprint, Door, Rect, Room


def test_w_and_h_use_exclusive_x2_y2():
    r = Rect(0, 0, 10, 5)
    assert r.w == 10
    assert r.h == 5


def test_center():
    r = Rect(0, 0, 10, 4)
    assert r.center() == (5.0, 2.0)


def test_shrink_moves_all_sides_inward():
    r = Rect(0, 0, 10, 10)
    shrunk = r.shrink(2)
    assert shrunk == Rect(2, 2, 8, 8)


def test_overlaps_true_for_intersecting_rects():
    a = Rect(0, 0, 10, 10)
    b = Rect(5, 5, 15, 15)
    assert a.overlaps(b)
    assert b.overlaps(a)


def test_overlaps_false_for_disjoint_rects():
    a = Rect(0, 0, 5, 5)
    b = Rect(10, 10, 15, 15)
    assert not a.overlaps(b)


def test_overlaps_false_for_touching_rects_without_margin():
    """x2/y2 esclusivi: due rettangoli che si toccano sul bordo non si sovrappongono."""
    a = Rect(0, 0, 5, 5)
    b = Rect(5, 0, 10, 5)
    assert not a.overlaps(b)


def test_overlaps_true_for_nearby_rects_with_margin():
    a = Rect(0, 0, 5, 5)
    b = Rect(6, 0, 10, 5)  # gap di 1 quadretto fra i due
    assert not a.overlaps(b, margin=0)
    assert not a.overlaps(b, margin=1)  # gap == margin: clearance sufficiente
    assert a.overlaps(b, margin=2)  # gap < margin: troppo vicini


def test_overlaps_false_for_far_rects_even_with_margin():
    a = Rect(0, 0, 5, 5)
    b = Rect(20, 20, 25, 25)
    assert not a.overlaps(b, margin=2)


def test_room_and_blueprint_hold_expected_fields():
    room = Room(rect=Rect(0, 0, 5, 5), kind="sala", doors=[Door(wall_index=0, t=0.5)])
    blueprint = Blueprint(
        width=40, height=40, rooms=[room], corridors=[], graph={0: []}, seed=1, style="dungeon"
    )
    assert blueprint.rooms[0].doors[0].kind == "wood"
    assert blueprint.levels == 1
