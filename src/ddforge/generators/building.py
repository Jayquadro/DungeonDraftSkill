"""Edifici urbani multi-piano: taverne, magioni, magazzini.

Vedi docs/SPEC.md §9.2. Riusa l'infrastruttura di partizione e connessione
di bsp.py (TASK-21), generica e non specifica al dungeon: _build_tree
partiziona un rettangolo qualsiasi, _connect_rooms decide porta-diretta o
corridoio fra due stanze qualsiasi. Produce solo un Blueprint, nessun
accesso a level/ids/JSON (stesso vincolo di bsp.py).
"""

import math
import random

from ddforge.generators.bsp import _build_tree, _connect_rooms, _inscribe_room, _non_colliding_t
from ddforge.model import Blueprint, Door, Rect, Room

# Ogni tipologia: lista di (indice_piano, [kind per ogni stanza attesa]).
# SPEC.md §9.2: taverna terra=sala comune+cucina+retro, primo=camere;
# magione terra=rappresentanza, primo=privato, sottotetto=servitu;
# magazzino terra=volume unico, primo=soppalco (copre solo meta pianta).
_BUILDING_TYPES = {
    "tavern": [
        (0, ["sala_comune", "cucina", "retro"]),
        (1, ["camera", "camera", "camera"]),
    ],
    "manor": [
        (0, ["rappresentanza", "rappresentanza"]),
        (1, ["privato", "privato", "privato"]),
        (2, ["servitu", "servitu"]),
    ],
    "warehouse": [
        (0, ["magazzino"]),
        (1, ["soppalco"]),
    ],
}

_STAIRS_WIDTH = 2


def _footprint_parts(footprint: Rect, l_shaped: bool) -> list[Rect]:
    """Un rettangolo, o due che insieme formano una L (notch fisso in
    basso a destra: un solo caso e sufficiente, SPEC.md non chiede angoli
    diversi, solo che il generatore sappia produrre entrambe le forme)."""
    if not l_shaped:
        return [footprint]
    notch_w = max(2, footprint.w // 3)
    notch_h = max(2, footprint.h // 3)
    main_part = Rect(footprint.x1, footprint.y1, footprint.x2, footprint.y2 - notch_h)
    wing_part = Rect(footprint.x1, footprint.y2 - notch_h, footprint.x2 - notch_w, footprint.y2)
    return [main_part, wing_part]


def _generate_room_rects(parts: list[Rect], target: int, rng: random.Random, *, min_room: int, max_room: int, depth_max: int) -> list[Rect]:
    """Distribuisce `target` stanze fra le parti del footprint, proporzionalmente
    all'area. len() del risultato puo avvicinarsi a target senza combaciare
    esattamente (stessa proprieta di _build_tree, TASK-21)."""
    if target <= 0:
        return []
    areas = [max(1, part.w * part.h) for part in parts]
    total_area = sum(areas)
    budgets = []
    remaining = target
    for i, area in enumerate(areas):
        if i == len(parts) - 1:
            budgets.append(max(0, remaining))
        else:
            budget = min(max(1, round(target * area / total_area)), remaining)
            budgets.append(budget)
            remaining -= budget

    rects = []
    for part, budget in zip(parts, budgets):
        if budget <= 0:
            continue
        _, leaves = _build_tree(part, rng, rooms_target=budget, max_room=max_room, depth_max=depth_max)
        for leaf in leaves:
            rects.append(_inscribe_room(leaf.rect, rng, min_room))
    return rects


def _connect_floor_rooms(rooms: list[Room], corridors: list[Rect], corridor_width: float) -> dict:
    """Connette le stanze di un piano con un albero minimo per vicinanza
    (Prim): un edificio si legge bene anche come albero puro, non serve la
    ricorsione BSP ne gli anelli extra (quelli sono specifici del dungeon,
    TASK-21). Garantisce che ogni stanza sia raggiungibile."""
    graph = {i: [] for i in range(len(rooms))}
    if len(rooms) < 2:
        return graph

    connected = [0]
    remaining = list(range(1, len(rooms)))
    while remaining:
        best_pair, best_dist = None, None
        for i in connected:
            ax, ay = rooms[i].rect.center()
            for j in remaining:
                bx, by = rooms[j].rect.center()
                dist = math.hypot(bx - ax, by - ay)
                if best_dist is None or dist < best_dist:
                    best_dist, best_pair = dist, (i, j)
        i, j = best_pair
        _connect_rooms(rooms[i], rooms[j], corridors, corridor_width)
        graph[i].append(j)
        graph[j].append(i)
        connected.append(j)
        remaining.remove(j)
    return graph


def _ensure_entry(floor_rooms: list[Room], footprint: Rect, *, force: bool) -> None:
    """Apre una porta sulla stanza del piano il cui lato inferiore e piu
    vicino al bordo del footprint (probabile parete esterna), evitando
    collisioni con porte gia presenti sullo stesso lato.

    force=True (piano terra): apre SEMPRE una porta d'ingresso, anche se le
    stanze hanno gia porte interne fra loro — quelle non danno accesso
    dall'esterno. force=False (altri piani): apre una porta solo se
    nessuna stanza del piano ne ha gia una, il caso di un piano con
    un'unica stanza (es. il soppalco di un magazzino) che altrimenti
    resterebbe un vicolo cieco senza porta (AC3)."""
    if not floor_rooms:
        return
    if not force and any(room.doors for room in floor_rooms):
        return
    entrance_room = min(floor_rooms, key=lambda r: abs(r.rect.y2 - footprint.y2))
    t = _non_colliding_t(entrance_room, 2, 0.5)
    entrance_room.doors.append(Door(wall_index=2, t=t, kind="wood"))


def generate(*, width: int, height: int, seed: int,
             building_type: str = "tavern", l_shaped: bool = False,
             min_room: int = 3, max_room: int = 8, corridor_width: float = 1.0,
             depth_max: int = 6, **params) -> Blueprint:
    """Genera un edificio multi-piano. building_type in
    {tavern, manor, warehouse} (SPEC.md §9.2)."""
    if building_type not in _BUILDING_TYPES:
        raise ValueError(f"Tipologia sconosciuta: {building_type!r}. Valide: {sorted(_BUILDING_TYPES)}")

    rng = random.Random(seed)
    footprint = Rect(1, 1, width - 1, height - 1)

    # Striscia riservata al vano scale: esclusa dal footprint di
    # generazione stanze su OGNI piano, mai sovrapposta per costruzione.
    stairs_rect = Rect(footprint.x1, footprint.y1, footprint.x1 + _STAIRS_WIDTH, footprint.y1 + _STAIRS_WIDTH)
    generation_footprint = Rect(footprint.x1 + _STAIRS_WIDTH + 1, footprint.y1, footprint.x2, footprint.y2)
    parts = _footprint_parts(generation_footprint, l_shaped)

    floors_spec = _BUILDING_TYPES[building_type]
    all_rooms: list[Room] = []
    all_graph: dict[int, list[int]] = {}
    corridors: list[Rect] = []

    for floor_index, kinds in floors_spec:
        floor_parts = parts
        if building_type == "warehouse" and floor_index == 1:
            # Soppalco: copre solo meta della pianta, non l'intero footprint.
            half_width = max(min_room, generation_footprint.w // 2)
            floor_parts = [Rect(
                generation_footprint.x1, generation_footprint.y1,
                generation_footprint.x1 + half_width, generation_footprint.y2,
            )]

        room_rects = _generate_room_rects(
            floor_parts, len(kinds), rng, min_room=min_room, max_room=max_room, depth_max=depth_max
        )
        floor_rooms = [
            Room(rect=rect, kind=kind, level=floor_index)
            for rect, kind in zip(room_rects, kinds)
        ]
        floor_graph = _connect_floor_rooms(floor_rooms, corridors, corridor_width)
        _ensure_entry(floor_rooms, generation_footprint, force=(floor_index == 0))

        offset = len(all_rooms)
        for local_i, neighbors in floor_graph.items():
            all_graph[offset + local_i] = [offset + n for n in neighbors]
        all_rooms.extend(floor_rooms)

    n_levels = max(floor_index for floor_index, _ in floors_spec) + 1

    return Blueprint(
        width=width, height=height,
        rooms=all_rooms, corridors=corridors,
        graph=all_graph, seed=seed, style=building_type, levels=n_levels,
        stairs_rect=stairs_rect,
    )
