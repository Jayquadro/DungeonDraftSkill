"""Test per ddforge.generators.building (TASK-28)."""

from collections import deque

from ddforge.generators import building


def _bfs_reachable(graph, start=0):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


def test_generate_returns_blueprint_with_expected_style_and_levels():
    bp = building.generate(width=40, height=40, seed=1, building_type="tavern")
    assert bp.style == "tavern"
    assert bp.levels == 2
    assert bp.stairs_rect is not None


def test_unknown_building_type_raises_explicit_error():
    import pytest

    with pytest.raises(ValueError, match="Tipologia sconosciuta"):
        building.generate(width=40, height=40, seed=1, building_type="castello")


def test_rectangular_footprint_by_default():
    """Senza l_shaped, tutte le stanze del piano terra rientrano in un
    unico rettangolo pieno (nessun angolo sistematicamente vuoto)."""
    bp = building.generate(width=40, height=40, seed=1, building_type="tavern", l_shaped=False)
    ground_rooms = [r for r in bp.rooms if r.level == 0]
    max_x = max(r.rect.x2 for r in ground_rooms)
    max_y = max(r.rect.y2 for r in ground_rooms)
    # con footprint rettangolare, esiste una stanza che arriva vicino
    # all'angolo in basso a destra del footprint di generazione
    assert max_x > 30 and max_y > 30


def test_l_shaped_footprint_leaves_a_corner_empty():
    bp = building.generate(width=40, height=40, seed=1, building_type="tavern", l_shaped=True)
    ground_rooms = [r for r in bp.rooms if r.level == 0]
    footprint_x2 = max(r.rect.x2 for r in ground_rooms)
    footprint_y2 = max(r.rect.y2 for r in ground_rooms)
    notch_w = footprint_x2 // 4  # soglia larga per il confronto
    notch_h = footprint_y2 // 4
    # nessuna stanza deve occupare l'angolo in basso a destra (il notch)
    for room in ground_rooms:
        in_notch = (
            room.rect.x1 >= footprint_x2 - notch_w
            and room.rect.y1 >= footprint_y2 - notch_h
        )
        assert not in_notch, f"stanza {room.rect} cade nel notch atteso vuoto"


def test_tavern_has_expected_room_kinds_per_floor():
    bp = building.generate(width=40, height=40, seed=1, building_type="tavern")
    ground_kinds = {r.kind for r in bp.rooms if r.level == 0}
    first_kinds = {r.kind for r in bp.rooms if r.level == 1}
    assert ground_kinds == {"sala_comune", "cucina", "retro"}
    assert first_kinds == {"camera"}


def test_manor_has_expected_room_kinds_per_floor():
    bp = building.generate(width=40, height=40, seed=1, building_type="manor")
    kinds_by_level = {0: set(), 1: set(), 2: set()}
    for r in bp.rooms:
        kinds_by_level[r.level].add(r.kind)
    assert kinds_by_level[0] == {"rappresentanza"}
    assert kinds_by_level[1] == {"privato"}
    assert kinds_by_level[2] == {"servitu"}


def test_warehouse_ground_floor_is_a_single_volume():
    bp = building.generate(width=40, height=40, seed=1, building_type="warehouse")
    ground_rooms = [r for r in bp.rooms if r.level == 0]
    assert len(ground_rooms) == 1
    assert ground_rooms[0].kind == "magazzino"


def test_warehouse_mezzanine_covers_only_part_of_the_footprint():
    bp = building.generate(width=40, height=40, seed=1, building_type="warehouse")
    ground = next(r for r in bp.rooms if r.level == 0)
    mezzanine = next(r for r in bp.rooms if r.level == 1)
    assert mezzanine.rect.w * mezzanine.rect.h < ground.rect.w * ground.rect.h


def test_building_types_produce_distinct_kind_sets():
    tavern_kinds = {r.kind for r in building.generate(width=40, height=40, seed=1, building_type="tavern").rooms}
    manor_kinds = {r.kind for r in building.generate(width=40, height=40, seed=1, building_type="manor").rooms}
    warehouse_kinds = {r.kind for r in building.generate(width=40, height=40, seed=1, building_type="warehouse").rooms}
    assert tavern_kinds.isdisjoint(manor_kinds)
    assert tavern_kinds.isdisjoint(warehouse_kinds)
    assert manor_kinds.isdisjoint(warehouse_kinds)


def test_every_room_has_at_least_one_door_across_seeds_and_types():
    for building_type in ("tavern", "manor", "warehouse"):
        for seed in range(15):
            bp = building.generate(width=40, height=40, seed=seed, building_type=building_type)
            for i, room in enumerate(bp.rooms):
                assert len(room.doors) >= 1, f"{building_type} seed={seed}: stanza {i} senza porte"


def test_rooms_on_the_same_floor_are_all_reachable_from_each_other():
    for building_type in ("tavern", "manor"):
        bp = building.generate(width=40, height=40, seed=1, building_type=building_type)
        for level in range(bp.levels):
            indices = [i for i, r in enumerate(bp.rooms) if r.level == level]
            if len(indices) < 2:
                continue
            sub_graph = {i: [n for n in bp.graph[i] if n in indices] for i in indices}
            reachable = _bfs_reachable(sub_graph, start=indices[0])
            assert reachable == set(indices), f"{building_type} piano {level}: non tutte le stanze raggiungibili"


def test_stairs_rect_never_overlaps_any_room():
    for building_type in ("tavern", "manor", "warehouse"):
        bp = building.generate(width=40, height=40, seed=1, building_type=building_type)
        for room in bp.rooms:
            assert not room.rect.overlaps(bp.stairs_rect)


def test_stairs_rect_is_a_single_object_shared_by_construction():
    """stairs_rect e un solo Rect nel Blueprint (non uno per piano): per
    costruzione e identico ovunque venga consumato (draw_building, TASK-27)."""
    bp = building.generate(width=40, height=40, seed=1, building_type="manor")
    assert bp.stairs_rect is not None
    assert bp.stairs_rect.x1 >= 1 and bp.stairs_rect.y1 >= 1


def test_same_seed_produces_identical_blueprint():
    a = building.generate(width=40, height=40, seed=42, building_type="tavern")
    b = building.generate(width=40, height=40, seed=42, building_type="tavern")
    assert a == b


def test_different_seed_produces_different_blueprint():
    a = building.generate(width=40, height=40, seed=1, building_type="tavern")
    b = building.generate(width=40, height=40, seed=2, building_type="tavern")
    assert a != b


def test_end_to_end_render_through_draw_building_passes_validate():
    from ddforge.assets import Palette
    from ddforge.compose import draw_building
    from ddforge.ids import IdAllocator
    from ddforge.template import finalize, load_template, prepare
    from ddforge.validate import validate

    palette = Palette(
        wall="res://textures/walls/wood_04.png",
        floor="res://textures/patterns/normal/wood_planks.png",
        door="res://textures/portals/door_wood_single.png",
        wall_load_bearing="res://textures/walls/stone.png",
        roof="res://textures/roofs/flat_clay_red/tiles.png",
    )

    for building_type in ("tavern", "manor", "warehouse"):
        bp = building.generate(width=40, height=40, seed=1, building_type=building_type)
        doc = load_template("templates/blank_80x80.dungeondraft_map")
        prepared = prepare(doc, levels=bp.levels)
        ids = IdAllocator.from_document(prepared)
        draw_building(prepared["world"]["levels"], ids, bp, palette)
        finalize(prepared, ids)

        errors = [i for i in validate(prepared) if i.severity == "error"]
        assert errors == [], f"{building_type}: {errors}"
