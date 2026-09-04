"""Test per ddforge.generators.bsp (TASK-21)."""

from collections import deque

from ddforge.generators import bsp


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


def test_generate_returns_blueprint_with_all_fields_set():
    bp = bsp.generate(width=40, height=40, seed=1)
    assert bp.width == 40
    assert bp.height == 40
    assert bp.seed == 1
    assert bp.style == "dungeon"
    assert len(bp.rooms) > 0
    assert isinstance(bp.graph, dict)


def test_room_count_approaches_target():
    bp = bsp.generate(width=60, height=60, seed=1, rooms=8)
    assert 6 <= len(bp.rooms) <= 10  # vicino al target, non necessariamente esatto


def test_no_rooms_overlap():
    bp = bsp.generate(width=60, height=60, seed=42, rooms=10)
    for i, a in enumerate(bp.rooms):
        for b in bp.rooms[i + 1 :]:
            assert not a.rect.overlaps(b.rect)


def test_no_room_exits_canvas():
    bp = bsp.generate(width=50, height=50, seed=7, rooms=8)
    for room in bp.rooms:
        assert 0 <= room.rect.x1 < room.rect.x2 <= 50
        assert 0 <= room.rect.y1 < room.rect.y2 <= 50


def test_room_graph_is_always_connected():
    for seed in range(20):
        bp = bsp.generate(width=50, height=50, seed=seed, rooms=8)
        reachable = _bfs_reachable(bp.graph, start=0)
        assert reachable == set(range(len(bp.rooms))), f"seed={seed}: grafo non connesso"


def test_loops_produce_at_least_one_cycle_on_large_map():
    """Con loops=0.15 su una mappa abbastanza grande, il grafo deve avere
    almeno un ciclo: numero di archi >= numero di nodi (un albero ne ha
    esattamente n-1)."""
    found_cycle = False
    for seed in range(10):
        bp = bsp.generate(width=80, height=80, seed=seed, rooms=12, loops=0.15)
        n_edges = sum(len(neighbors) for neighbors in bp.graph.values()) // 2
        if n_edges >= len(bp.rooms):
            found_cycle = True
            break
    assert found_cycle


def test_zero_loops_produces_a_tree():
    bp = bsp.generate(width=50, height=50, seed=3, rooms=8, loops=0.0)
    n_edges = sum(len(neighbors) for neighbors in bp.graph.values()) // 2
    assert n_edges == len(bp.rooms) - 1


def test_same_seed_produces_identical_blueprint():
    a = bsp.generate(width=50, height=50, seed=999, rooms=8)
    b = bsp.generate(width=50, height=50, seed=999, rooms=8)
    assert a == b


def test_different_seed_produces_different_blueprint():
    a = bsp.generate(width=50, height=50, seed=1, rooms=8)
    b = bsp.generate(width=50, height=50, seed=2, rooms=8)
    assert a != b


def test_every_room_has_at_least_one_door():
    """Coerente col criterio 'nessuna stanza irraggiungibile': ogni stanza
    del grafo connesso ha almeno una porta (DDF102 di TASK-14). Verificato
    su piu seed: e una proprieta strutturale dell'algoritmo (ogni foglia
    riceve una porta al piu tardi quando il suo genitore diretto la
    collega), non un caso fortunato di un seed specifico."""
    for seed in range(30):
        bp = bsp.generate(width=50, height=50, seed=seed, rooms=8)
        for i, room in enumerate(bp.rooms):
            assert len(room.doors) >= 1, f"seed={seed}: stanza {i} senza porte"


def test_no_two_doors_on_the_same_wall_too_close():
    """Regressione: una stanza collegata a piu vicini dallo stesso lato puo
    proiettare piu porte vicino allo stesso punto (es. il centro del lato).
    Verifica su molti seed che _non_colliding_t le tenga sempre separate
    di almeno 0.05 (soglia DDF105)."""
    for seed in range(30):
        bp = bsp.generate(width=60, height=60, seed=seed, rooms=12, loops=0.2)
        for room in bp.rooms:
            by_wall: dict[int, list[float]] = {}
            for door in room.doors:
                by_wall.setdefault(door.wall_index, []).append(door.t)
            for wall_index, ts in by_wall.items():
                ts.sort()
                for a, b in zip(ts, ts[1:]):
                    assert b - a >= 0.05, f"seed={seed}: porte troppo vicine su wall_index={wall_index}"


def test_door_t_is_always_in_valid_range():
    bp = bsp.generate(width=50, height=50, seed=11, rooms=10)
    for room in bp.rooms:
        for door in room.doors:
            assert 0.0 <= door.t <= 1.0
            assert door.wall_index in (0, 1, 2, 3)


def test_single_room_when_target_is_one():
    bp = bsp.generate(width=20, height=20, seed=1, rooms=1)
    assert len(bp.rooms) == 1
    assert bp.graph == {0: []}


def test_end_to_end_render_through_draw_room_passes_validate():
    """Integrazione: le porte decise a livello di Blueprint (wall_index/t
    puramente geometrici) devono risolversi correttamente quando draw_room
    disegna davvero i muri, producendo un documento senza errori.

    Disegna solo le stanze (draw_room), non i corridoi: renderizzare
    Blueprint.corridors come canali aperti e responsabilita del passo
    generate->JSON (TASK-24), che avra i propri test dedicati."""
    from ddforge.assets import Palette
    from ddforge.compose import draw_room
    from ddforge.ids import IdAllocator
    from ddforge.validate import validate

    palette = Palette(
        wall="res://textures/walls/stone.png",
        floor="res://textures/patterns/normal/stone_floor.png",
        door="res://textures/portals/door_00.png",
    )

    bp = bsp.generate(width=50, height=50, seed=1, rooms=8)
    level = {
        "walls": [], "portals": [], "patterns": [], "objects": [], "paths": [],
        "lights": [], "texts": [],
        "roofs": {"shade": True, "shade_contrast": 0.5, "sun_direction": 45, "roofs": []},
    }
    ids = IdAllocator()
    for room in bp.rooms:
        draw_room(level, ids, room, palette)

    doc = {
        "header": {"asset_manifest": []},
        "world": {
            "format": 3, "width": 50, "height": 50, "next_node_id": ids.next_free,
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
    issues = validate(doc)
    errors = [i for i in issues if i.severity == "error" and i.code not in ("DDF010", "DDF011")]
    assert errors == []
    warnings = {i.code for i in issues if i.severity == "warning"}
    assert "DDF102" not in warnings
