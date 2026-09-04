"""Composti: stanza, corridoio, edificio.

Vedi docs/SPEC.md §6.6. draw_room/draw_corridor implementati in TASK-18;
connect in TASK-19; furnish in TASK-23 (SPEC.md §9.5 non gli assegna un
file dedicato: e un altro composto Blueprint -> JSON); draw_building in
TASK-27.
"""

import math

from ddforge.build import add_light, add_object, add_pattern, add_portal, add_wall
from ddforge.godot import grid_to_px, parse_pv2
from ddforge.model import Rect, Room

# Indici di lato coerenti con l'ordine di _draw_perimeter: 0=top, 1=right,
# 2=bottom, 3=left (percorrendo i 4 vertici di Rect in senso orario a
# partire da x1,y1).
_TOP, _RIGHT, _BOTTOM, _LEFT = 0, 1, 2, 3


def _wall_tangent(wall: dict) -> tuple[float, float]:
    """Vettore tangente unitario del muro, dal primo punto all'ultimo.

    CALIBRATO dal gate umano TASK-12 (screenshot task12_zoom.png e
    task12_selected.png): la prima ipotesi (normale uscente dalla stanza,
    perpendicolare al muro) produceva una porta ruotata di 90 gradi, che
    visivamente spezzava il muro in due segmenti storti. portal.direction
    e in realta la TANGENTE del muro stesso (parallela, non perpendicolare),
    confermato esattamente sui 2 campioni reali di rich_reference:
    muro verticale (8704,9216)->(8704,10496): tangente (0,1) == direction
    osservata; muro orizzontale (8704,10496)->(9984,10496): tangente (1,0)
    == direction osservata. Vedi docs/format.md §5.
    """
    points = parse_pv2(wall["points"])
    (ax, ay), (bx, by) = points[0], points[-1]
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return (1.0, 0.0)
    return (dx / length, dy / length)


def _rotation_for_direction(direction: tuple[float, float]) -> float:
    """rotation = atan2(direction.y, direction.x): formula confermata su
    tutti e 3 i campioni reali osservati (docs/format.md §5)."""
    return math.atan2(direction[1], direction[0])


def _draw_perimeter(level, ids, room, palette, *, add_doors: bool) -> dict:
    rect = room.rect
    pattern = add_pattern(level, ids, rect, room.floor or palette.floor)

    corners = [
        (rect.x1, rect.y1),
        (rect.x2, rect.y1),
        (rect.x2, rect.y2),
        (rect.x1, rect.y2),
    ]
    walls = [
        add_wall(level, ids, [corners[i], corners[(i + 1) % 4]], palette.wall)
        for i in range(4)
    ]

    portals = []
    if add_doors:
        for door in room.doors:
            wall = walls[door.wall_index]
            direction = _wall_tangent(wall)
            rotation = _rotation_for_direction(direction)
            portal = add_portal(
                wall, ids,
                t=door.t, direction=direction, rotation=rotation,
                texture=palette.door, locked=door.locked,
            )
            portals.append(portal)

    for x, y in room.lights:
        add_light(level, ids, x, y)

    return {"walls": walls, "pattern": pattern, "portals": portals}


def draw_room(level, ids, room, palette) -> dict:
    """Pavimento + muri perimetrali + porte + luci. Restituisce
    {'walls': [...], 'pattern': ..., 'portals': [...]}."""
    return _draw_perimeter(level, ids, room, palette, add_doors=True)


def draw_corridor(level, ids, rect, palette) -> dict:
    """Corridoio come stanza stretta senza porte alle estremita."""
    corridor_room = Room(rect=rect, kind="corridoio")
    return _draw_perimeter(level, ids, corridor_room, palette, add_doors=False)


def _side_corners(rect: Rect, side: int) -> tuple[tuple[float, float], tuple[float, float]]:
    """Estremi (in quadretti) del lato `side` di rect, stesso ordine di _draw_perimeter."""
    corners = [
        (rect.x1, rect.y1), (rect.x2, rect.y1),
        (rect.x2, rect.y2), (rect.x1, rect.y2),
    ]
    return corners[side], corners[(side + 1) % 4]


def _wall_for_side(level: dict, rect: Rect, side: int) -> dict | None:
    """Trova in level['walls'] il muro i cui estremi coincidono esattamente
    (in px) con quelli attesi per quel lato di rect. Nessuna euristica: match
    esatto, cosi non c'e ambiguita fra muri di stanze diverse."""
    p1, p2 = _side_corners(rect, side)
    expected = {(grid_to_px(p1[0]), grid_to_px(p1[1])), (grid_to_px(p2[0]), grid_to_px(p2[1]))}
    for wall in level.get("walls", []):
        try:
            points = parse_pv2(wall["points"])
        except (KeyError, ValueError):
            continue
        if len(points) < 2:
            continue
        if {points[0], points[-1]} == expected:
            return wall
    return None


def _t_along_wall(wall_points_px: list[tuple[float, float]], point_px: tuple[float, float]) -> float:
    """Proiezione di point_px sulla polilinea (primo-ultimo punto) del muro,
    come frazione 0..1. Gestisce qualunque verso di percorrenza."""
    (x0, y0), (x1, y1) = wall_points_px[0], wall_points_px[-1]
    dx, dy = x1 - x0, y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return 0.0
    px, py = point_px
    t = ((px - x0) * dx + (py - y0) * dy) / length_sq
    return min(max(t, 0.0), 1.0)


def _add_door_at_point(level, ids, room, point_grid: tuple[float, float], palette, side: int) -> dict | None:
    wall = _wall_for_side(level, room.rect, side)
    if wall is None:
        return None
    point_px = (grid_to_px(point_grid[0]), grid_to_px(point_grid[1]))
    t = _t_along_wall(parse_pv2(wall["points"]), point_px)
    direction = _wall_tangent(wall)
    rotation = _rotation_for_direction(direction)
    return add_portal(wall, ids, t=t, direction=direction, rotation=rotation, texture=palette.door)


def _shared_wall_segment(rect_a: Rect, rect_b: Rect):
    """Ritorna (side_a, side_b, midpoint_grid) del segmento condiviso fra
    due rettangoli adiacenti (bordi coincidenti + overlap non nullo
    sull'asse libero), o None se non adiacenti."""
    if rect_a.x2 == rect_b.x1 or rect_b.x2 == rect_a.x1:
        y1, y2 = max(rect_a.y1, rect_b.y1), min(rect_a.y2, rect_b.y2)
        if y2 > y1:
            mid = ((y1 + y2) / 2,)
            if rect_a.x2 == rect_b.x1:
                return (_RIGHT, _LEFT, (rect_a.x2, mid[0]))
            return (_LEFT, _RIGHT, (rect_a.x1, mid[0]))
    if rect_a.y2 == rect_b.y1 or rect_b.y2 == rect_a.y1:
        x1, x2 = max(rect_a.x1, rect_b.x1), min(rect_a.x2, rect_b.x2)
        if x2 > x1:
            mid = ((x1 + x2) / 2,)
            if rect_a.y2 == rect_b.y1:
                return (_BOTTOM, _TOP, (mid[0], rect_a.y2))
            return (_TOP, _BOTTOM, (mid[0], rect_a.y1))
    return None


def _connect_adjacent(level, ids, room_a, room_b, palette, side_a, side_b, midpoint) -> dict:
    portal = _add_door_at_point(level, ids, room_a, midpoint, palette, side_a)
    room = room_a
    if portal is None:
        portal = _add_door_at_point(level, ids, room_b, midpoint, palette, side_b)
        room = room_b
    if portal is None:
        raise ValueError(
            "Nessun muro trovato per collegare le stanze: sono gia state "
            "disegnate con draw_room prima di chiamare connect()?"
        )
    return {"portal": portal, "corridors": [], "portals": [portal], "room": room}


def _draw_corridor_channel(level, ids, rect: Rect, palette, *, horizontal: bool) -> dict:
    """Segmento di corridoio usato da connect(): disegna solo i due lati
    lunghi (paralleli alla direzione di marcia), lasciando gli estremi
    aperti. Un box chiuso a 4 muri (draw_corridor) ribloccherebbe la porta
    appena tagliata nel muro della stanza all'estremita del corridoio."""
    pattern = add_pattern(level, ids, rect, palette.floor)
    sides = (_TOP, _BOTTOM) if horizontal else (_LEFT, _RIGHT)
    walls = [add_wall(level, ids, list(_side_corners(rect, side)), palette.wall) for side in sides]
    return {"walls": walls, "pattern": pattern}


def plan_corridor(rect_a: Rect, rect_b: Rect, width: float = 1.0):
    """Geometria pura (nessun accesso a level/ids) del corridoio fra due
    rettangoli NON adiacenti: usata sia da connect() per disegnare, sia dai
    generatori (TASK-21+) per popolare Blueprint.corridors/Room.doors prima
    che qualunque muro esista. Ritorna (segments, door_a, door_b) dove
    segments e una lista di (Rect, horizontal) e door_a/door_b sono
    (side, point_grid)."""
    half = width / 2
    x_overlap = max(rect_a.x1, rect_b.x1) < min(rect_a.x2, rect_b.x2)
    y_overlap = max(rect_a.y1, rect_b.y1) < min(rect_a.y2, rect_b.y2)

    segments = []

    if y_overlap:
        cy = (max(rect_a.y1, rect_b.y1) + min(rect_a.y2, rect_b.y2)) / 2
        if rect_a.x2 <= rect_b.x1:
            x1, x2 = rect_a.x2, rect_b.x1
            side_a, side_b = _RIGHT, _LEFT
        else:
            x1, x2 = rect_b.x2, rect_a.x1
            side_a, side_b = _LEFT, _RIGHT
        segments.append((Rect(x1, cy - half, x2, cy + half), True))
        door_a = (side_a, (rect_a.x2 if side_a == _RIGHT else rect_a.x1, cy))
        door_b = (side_b, (rect_b.x1 if side_b == _LEFT else rect_b.x2, cy))

    elif x_overlap:
        cx = (max(rect_a.x1, rect_b.x1) + min(rect_a.x2, rect_b.x2)) / 2
        if rect_a.y2 <= rect_b.y1:
            y1, y2 = rect_a.y2, rect_b.y1
            side_a, side_b = _BOTTOM, _TOP
        else:
            y1, y2 = rect_b.y2, rect_a.y1
            side_a, side_b = _TOP, _BOTTOM
        segments.append((Rect(cx - half, y1, cx + half, y2), False))
        door_a = (side_a, (cx, rect_a.y2 if side_a == _BOTTOM else rect_a.y1))
        door_b = (side_b, (cx, rect_b.y1 if side_b == _TOP else rect_b.y2))

    else:
        # L generale: nessun asse condiviso, quindi il centro dell'altra
        # stanza cade sempre fuori dal proprio rettangolo (vedi TASK-19).
        ax, ay = rect_a.center()
        bx, by = rect_b.center()

        side_a = _RIGHT if bx > rect_a.x2 else _LEFT
        exit_a = (rect_a.x2 if side_a == _RIGHT else rect_a.x1, ay)
        segments.append((Rect(min(exit_a[0], bx), ay - half, max(exit_a[0], bx), ay + half), True))
        door_a = (side_a, exit_a)

        side_b = _TOP if ay < rect_b.y1 else _BOTTOM
        entry_b = (bx, rect_b.y1 if side_b == _TOP else rect_b.y2)
        segments.append((Rect(bx - half, min(ay, entry_b[1]), bx + half, max(ay, entry_b[1])), False))
        door_b = (side_b, entry_b)

    return segments, door_a, door_b


def _connect_with_corridor(level, ids, room_a, room_b, palette) -> dict:
    segments, door_a, door_b = plan_corridor(room_a.rect, room_b.rect)

    corridors = []
    for rect, horizontal in segments:
        _draw_corridor_channel(level, ids, rect, palette, horizontal=horizontal)
        corridors.append(rect)

    portals = []
    for room, (side, point) in ((room_a, door_a), (room_b, door_b)):
        portal = _add_door_at_point(level, ids, room, point, palette, side)
        if portal is not None:
            portals.append(portal)

    return {"portal": None, "corridors": corridors, "portals": portals}


def connect(level, ids, room_a, room_b, palette) -> dict:
    """Trova il muro condiviso o genera un corridoio a L fra due stanze.

    Ritorna sempre {'portal', 'corridors', 'portals'}: nel caso adiacente
    'portal' e la singola porta creata (anche in 'portals'); nel caso a
    corridoio 'portal' e None e 'portals' contiene le porte agli estremi.
    """
    shared = _shared_wall_segment(room_a.rect, room_b.rect)
    if shared is not None:
        side_a, side_b, midpoint = shared
        return _connect_adjacent(level, ids, room_a, room_b, palette, side_a, side_b, midpoint)

    return _connect_with_corridor(level, ids, room_a, room_b, palette)


def draw_building(level_stack, ids, blueprint, palette) -> None:
    """Edificio multi-piano: distribuisce le stanze, aggiunge scale e tetto."""
    raise NotImplementedError


def render_blueprint(level, ids, blueprint, palette) -> None:
    """Disegna un Blueprint intero in un livello gia preparato (TASK-24):
    ogni Room via draw_room (le porte sono gia decise dal generatore in
    Room.doors) e ogni corridoio come canale aperto. L'orientamento del
    canale e derivato da rect.w >= rect.h, vedi la nota in
    generators/bsp.py sul perche e affidabile."""
    for room in blueprint.rooms:
        draw_room(level, ids, room, palette)
    for rect in blueprint.corridors:
        _draw_corridor_channel(level, ids, rect, palette, horizontal=rect.w >= rect.h)


# ---------------------------------------------------------------------------
# furnish (TASK-23)
# ---------------------------------------------------------------------------

_DENSITY_PER_TILE = {"none": 0.0, "light": 0.05, "medium": 0.12, "heavy": 0.25}
_FURNISH_KIND_MULTIPLIER = {"boss": 1.5, "servizio": 0.5}
_WALL_MARGIN = 0.5
_DOOR_CLEARANCE = 1.5
_TACTICAL_COVER_KEYS = ("column", "crate", "barrel")
_TACTICAL_SPACING_MIN, _TACTICAL_SPACING_MAX = 3.0, 4.0


def _door_point_grid(rect: Rect, door) -> tuple[float, float]:
    (x0, y0), (x1, y1) = _side_corners(rect, door.wall_index)
    return (x0 + (x1 - x0) * door.t, y0 + (y1 - y0) * door.t)


def _is_clear_of_walls_and_doors(x: float, y: float, rect: Rect, door_points) -> bool:
    if not (rect.x1 + _WALL_MARGIN <= x <= rect.x2 - _WALL_MARGIN):
        return False
    if not (rect.y1 + _WALL_MARGIN <= y <= rect.y2 - _WALL_MARGIN):
        return False
    return all(math.hypot(x - dx, y - dy) >= _DOOR_CLEARANCE for dx, dy in door_points)


def _furnish_room(level, ids, room: Room, palette, rng, density: str) -> None:
    if not palette.accents:
        return
    base_rate = _DENSITY_PER_TILE[density]
    if base_rate == 0:
        return
    multiplier = _FURNISH_KIND_MULTIPLIER.get(room.kind, 1.0)
    area = room.rect.w * room.rect.h
    count = round(area * base_rate * multiplier)
    if count <= 0:
        return

    door_points = [_door_point_grid(room.rect, d) for d in room.doors]
    textures = list(palette.accents.values())

    placed = 0
    attempts = 0
    max_attempts = max(count * 25, 50)
    while placed < count and attempts < max_attempts:
        attempts += 1
        x = rng.uniform(room.rect.x1, room.rect.x2)
        y = rng.uniform(room.rect.y1, room.rect.y2)
        if not _is_clear_of_walls_and_doors(x, y, room.rect, door_points):
            continue
        texture = rng.choice(textures)
        add_object(level, ids, x, y, texture, rotation=rng.uniform(0, 2 * math.pi))
        placed += 1


def _furnish_tactical_cover(level, ids, room: Room, palette, rng) -> None:
    """Colonne/casse ogni 3-4 quadretti per i nodi tattici (SPEC.md §9.1/§9.5)."""
    if not palette.accents:
        return
    cover_textures = [palette.accents[k] for k in _TACTICAL_COVER_KEYS if k in palette.accents]
    if not cover_textures:
        cover_textures = list(palette.accents.values())

    door_points = [_door_point_grid(room.rect, d) for d in room.doors]
    spacing = rng.uniform(_TACTICAL_SPACING_MIN, _TACTICAL_SPACING_MAX)

    x = room.rect.x1 + _WALL_MARGIN + spacing / 2
    while x < room.rect.x2 - _WALL_MARGIN:
        y = room.rect.y1 + _WALL_MARGIN + spacing / 2
        while y < room.rect.y2 - _WALL_MARGIN:
            if _is_clear_of_walls_and_doors(x, y, room.rect, door_points):
                add_object(level, ids, x, y, rng.choice(cover_textures))
            y += spacing
        x += spacing


def furnish(level, ids, blueprint, palette, *, density: str = "medium", rng) -> None:
    """Arredo trasversale applicato dopo la geometria (SPEC.md §9.5).

    Non tocca mai i corridoi (blueprint.corridors non sono Room: restano
    sempre vuoti). rng va passato dal chiamante, mai creato qui, per
    riproducibilita a parita di seed."""
    if density not in _DENSITY_PER_TILE:
        raise ValueError(f"density sconosciuta: {density!r}. Valide: {sorted(_DENSITY_PER_TILE)}")

    tactical = set(getattr(blueprint, "tactical_rooms", []))
    for i, room in enumerate(blueprint.rooms):
        _furnish_room(level, ids, room, palette, rng, density)
        if i in tactical:
            _furnish_tactical_cover(level, ids, room, palette, rng)
