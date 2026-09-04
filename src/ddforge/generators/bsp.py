"""Dungeon a stanze via partizione binaria dello spazio (BSP).

Cripte, complessi sotterranei, prigioni. Vedi docs/SPEC.md §9.1.
Produce solo un Blueprint (geometria pura): nessun accesso a level/ids/JSON
qui, coerente col flusso generatore -> Blueprint -> compose -> build -> JSON
(SPEC.md, model.py). La semantica D&D (stanza boss, nodi tattici, corridoi
bui, porte segrete) e in TASK-22.

Nota per chi renderizza Blueprint.corridors in JSON (TASK-24): ogni Rect e
un canale aperto (compose._draw_corridor_channel-style: solo 2 lati lunghi,
niente muri di testata, altrimenti si riblocca la porta appena tagliata nel
muro della stanza, vedi TASK-19). L'orientamento non e salvato esplicitamente
nel Rect: derivarlo da rect.w >= rect.h (piu largo che alto -> orizzontale,
lati TOP/BOTTOM) e affidabile perche un canale e sempre molto piu lungo che
largo, TRANNE per segmenti quasi quadrati all'angolo di una L generale
(lunghezza vicina a corridor_width): in quel caso l'orientamento e ambiguo
per costruzione e la scelta non e critica per la connettivita.
"""

import math
import random

from ddforge.compose import _shared_wall_segment, _side_corners, plan_corridor
from ddforge.model import Blueprint, Door, Rect, Room


class _BSPNode:
    __slots__ = ("rect", "depth", "left", "right", "room_index")

    def __init__(self, rect: Rect, depth: int) -> None:
        self.rect = rect
        self.depth = depth
        self.left: "_BSPNode | None" = None
        self.right: "_BSPNode | None" = None
        self.room_index: int | None = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None


def _can_split(rect: Rect, max_room: int, depth: int, depth_max: int) -> bool:
    if depth >= depth_max:
        return False
    return rect.w >= max_room * 2 or rect.h >= max_room * 2


def _split_rect(rect: Rect, rng: random.Random) -> tuple[Rect, Rect]:
    """Taglia lungo l'asse piu lungo a una frazione casuale 35-65%."""
    frac = rng.uniform(0.35, 0.65)
    if rect.w >= rect.h:
        cut = rect.x1 + round(rect.w * frac)
        cut = min(max(cut, rect.x1 + 1), rect.x2 - 1)
        return Rect(rect.x1, rect.y1, cut, rect.y2), Rect(cut, rect.y1, rect.x2, rect.y2)
    cut = rect.y1 + round(rect.h * frac)
    cut = min(max(cut, rect.y1 + 1), rect.y2 - 1)
    return Rect(rect.x1, rect.y1, rect.x2, cut), Rect(rect.x1, cut, rect.x2, rect.y2)


def _build_tree(root_rect: Rect, rng: random.Random, *, rooms_target: int, max_room: int, depth_max: int):
    root = _BSPNode(root_rect, 0)
    leaves = [root]
    splittable = [root] if _can_split(root_rect, max_room, 0, depth_max) else []

    while len(leaves) < rooms_target and splittable:
        idx = rng.randrange(len(splittable))
        node = splittable.pop(idx)
        leaves.remove(node)

        rect_a, rect_b = _split_rect(node.rect, rng)
        node.left = _BSPNode(rect_a, node.depth + 1)
        node.right = _BSPNode(rect_b, node.depth + 1)
        for child in (node.left, node.right):
            leaves.append(child)
            if _can_split(child.rect, max_room, child.depth, depth_max):
                splittable.append(child)

    return root, leaves


def _inscribe_room(leaf_rect: Rect, rng: random.Random, min_room: int) -> Rect:
    max_margin_x = max(0, (leaf_rect.w - min_room) // 2)
    max_margin_y = max(0, (leaf_rect.h - min_room) // 2)
    margin_x = rng.randint(0, min(2, max_margin_x))
    margin_y = rng.randint(0, min(2, max_margin_y))
    return Rect(
        leaf_rect.x1 + margin_x, leaf_rect.y1 + margin_y,
        leaf_rect.x2 - margin_x, leaf_rect.y2 - margin_y,
    )


def _t_on_side(rect: Rect, side: int, point_grid: tuple[float, float]) -> float:
    (x0, y0), (x1, y1) = _side_corners(rect, side)
    dx, dy = x1 - x0, y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return 0.0
    px, py = point_grid
    t = ((px - x0) * dx + (py - y0) * dy) / length_sq
    return min(max(t, 0.0), 1.0)


def _non_colliding_t(room: Room, wall_index: int, desired_t: float, min_gap: float = 0.12) -> float:
    """Scosta desired_t se troppo vicino (< DDF105, con margine) a una porta
    gia presente sullo stesso muro. Puo succedere quando una stanza si
    collega a piu vicini dallo stesso lato: piu connessioni verso stanze
    diverse possono proiettarsi vicino allo stesso punto (es. il centro del
    lato), specialmente per i corridoi (SPEC.md §9.1 non lo vieta
    esplicitamente, ma DDF105 esiste apposta per segnalarlo)."""
    existing = [d.t for d in room.doors if d.wall_index == wall_index]
    if not existing:
        return desired_t
    t = desired_t
    step = 1
    while any(abs(t - e) < min_gap for e in existing) and step <= 10:
        offset = min_gap * ((step + 1) // 2)
        t = desired_t + offset if step % 2 == 1 else desired_t - offset
        t = min(max(t, 0.05), 0.95)
        step += 1
    return t


def _connect_rooms(room_a: Room, room_b: Room, corridors: list, corridor_width: float) -> None:
    """Decide come collegare due stanze e popola Room.doors/corridors,
    senza toccare nessun JSON: riusa la stessa geometria di compose.py."""
    shared = _shared_wall_segment(room_a.rect, room_b.rect)
    if shared is not None:
        side_a, side_b, midpoint = shared
        t_a = _non_colliding_t(room_a, side_a, _t_on_side(room_a.rect, side_a, midpoint))
        t_b = _non_colliding_t(room_b, side_b, _t_on_side(room_b.rect, side_b, midpoint))
        room_a.doors.append(Door(wall_index=side_a, t=t_a))
        room_b.doors.append(Door(wall_index=side_b, t=t_b))
        return

    segments, door_a, door_b = plan_corridor(room_a.rect, room_b.rect, width=corridor_width)
    corridors.extend(rect for rect, _ in segments)
    side_a, point_a = door_a
    side_b, point_b = door_b
    t_a = _non_colliding_t(room_a, side_a, _t_on_side(room_a.rect, side_a, point_a))
    t_b = _non_colliding_t(room_b, side_b, _t_on_side(room_b.rect, side_b, point_b))
    room_a.doors.append(Door(wall_index=side_a, t=t_a))
    room_b.doors.append(Door(wall_index=side_b, t=t_b))


def _connect_subtree(node: _BSPNode, rng: random.Random, rooms: list, graph: dict, corridors: list, corridor_width: float) -> int:
    """Risale l'albero collegando le due sorelle di ogni nodo interno.
    Ritorna l'indice (in `rooms`) di una stanza rappresentativa del
    sottoalbero di `node`, da usare per la connessione del livello superiore."""
    if node.is_leaf:
        return node.room_index

    idx_left = _connect_subtree(node.left, rng, rooms, graph, corridors, corridor_width)
    idx_right = _connect_subtree(node.right, rng, rooms, graph, corridors, corridor_width)

    _connect_rooms(rooms[idx_left], rooms[idx_right], corridors, corridor_width)
    graph[idx_left].append(idx_right)
    graph[idx_right].append(idx_left)

    return rng.choice((idx_left, idx_right))


def _add_loop_connections(rooms: list, graph: dict, corridors: list, rng: random.Random, loops: float, corridor_width: float) -> None:
    """Il 10-20% di collegamenti extra fra le stanze piu vicine non ancora
    connesse, per creare anelli ed evitare un dungeon-albero (SPEC.md §9.1)."""
    n = len(rooms)
    if n < 3:
        return
    connected = {frozenset((a, b)) for a, neighbors in graph.items() for b in neighbors}

    candidates = []
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) in connected:
                continue
            ax, ay = rooms[i].rect.center()
            bx, by = rooms[j].rect.center()
            candidates.append((math.hypot(bx - ax, by - ay), i, j))
    candidates.sort(key=lambda c: (c[0], c[1], c[2]))

    n_extra = round(loops * n)
    for _, i, j in candidates[:n_extra]:
        _connect_rooms(rooms[i], rooms[j], corridors, corridor_width)
        graph[i].append(j)
        graph[j].append(i)


def generate(*, width: int, height: int, seed: int,
             rooms: int = 8, min_room: int = 3, max_room: int = 10,
             corridor_width: float = 1.0, loops: float = 0.15,
             depth_max: int = 8, **params) -> Blueprint:
    """Genera un dungeon a stanze. Parametri per SPEC.md §9.1."""
    rng = random.Random(seed)
    root_rect = Rect(1, 1, width - 1, height - 1)

    tree_root, leaves = _build_tree(
        root_rect, rng, rooms_target=rooms, max_room=max_room, depth_max=depth_max
    )

    blueprint_rooms: list[Room] = []
    for i, leaf in enumerate(leaves):
        room_rect = _inscribe_room(leaf.rect, rng, min_room)
        blueprint_rooms.append(Room(rect=room_rect, kind="sala"))
        leaf.room_index = i

    graph: dict[int, list[int]] = {i: [] for i in range(len(blueprint_rooms))}
    corridors: list[Rect] = []
    _connect_subtree(tree_root, rng, blueprint_rooms, graph, corridors, corridor_width)
    _add_loop_connections(blueprint_rooms, graph, corridors, rng, loops, corridor_width)

    return Blueprint(
        width=width, height=height,
        rooms=blueprint_rooms, corridors=corridors,
        graph=graph, seed=seed, style="dungeon",
    )
