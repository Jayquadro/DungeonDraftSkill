"""Composti: stanza, corridoio, edificio.

Vedi docs/SPEC.md §6.6. draw_room/draw_corridor implementati in TASK-18;
connect in TASK-19; furnish in TASK-23 (SPEC.md §9.5 non gli assegna un
file dedicato: e un altro composto Blueprint -> JSON); draw_building in
TASK-27.
"""

import math
import re

from ddforge.build import (
    add_light, add_object, add_path, add_pattern, add_polygon_pattern, add_portal, add_roof,
    add_wall, add_water_polygon, set_cave_bitmap,
)
from ddforge.godot import GRID, grid_to_px, parse_pv2
from ddforge.model import Blueprint, Chamber, Corridor, Door, Rect, Room

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
    == direction osservata. Vedi docs/format.md §9.1.
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
    tutti e 3 i campioni reali osservati (docs/format.md §9.1)."""
    return math.atan2(direction[1], direction[0])


def _room_floor(room, palette) -> str:
    """Texture di pavimento per una stanza: l'override esplicito di
    Room.floor vince sempre, poi la mappatura kind->floor della palette
    (TASK-43, stesso meccanismo di _KIND_ACCENT_HINTS), infine il floor
    uniforme. Un kind assente da palette.floors ricade sul floor uniforme:
    e cosi che corridoi e vano scale (kind non mappati) restano invariati."""
    return room.floor or palette.floors.get(room.kind) or palette.floor


def _draw_perimeter(level, ids, room, palette, *, add_doors: bool, skip_sides=()) -> dict:
    rect = room.rect
    pattern = add_pattern(level, ids, rect, _room_floor(room, palette))

    corners = [
        (rect.x1, rect.y1),
        (rect.x2, rect.y1),
        (rect.x2, rect.y2),
        (rect.x1, rect.y2),
    ]
    # `skip_sides`: lati che qualcun altro ha gia disegnato (il muro portante
    # di un edificio, TASK-30). Ridisegnarli sopra significa sovrapporre due
    # muri, e quello di sotto tappa la porta dell'altro: nel gate umano M4
    # l'ingresso e la porta del vano scale erano murati proprio cosi. La
    # porta di un lato saltato la riporta il chiamante sul muro che resta.
    walls = [
        None if i in skip_sides
        else add_wall(level, ids, [corners[i], corners[(i + 1) % 4]], palette.wall)
        for i in range(4)
    ]

    portals = []
    if add_doors:
        for door in room.doors:
            wall = walls[door.wall_index]
            if wall is None:
                continue
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


def draw_room(level, ids, room, palette, *, skip_sides=()) -> dict:
    """Pavimento + muri perimetrali + porte + luci. Restituisce
    {'walls': [...], 'pattern': ..., 'portals': [...]}; le voci di 'walls'
    corrispondenti a `skip_sides` sono None."""
    return _draw_perimeter(level, ids, room, palette, add_doors=True, skip_sides=skip_sides)


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


def _add_door_to_wall(wall: dict, ids, point_grid: tuple[float, float], palette, *, locked: bool = False) -> dict:
    """Apre una porta su un muro gia disegnato, nel punto indicato."""
    point_px = (grid_to_px(point_grid[0]), grid_to_px(point_grid[1]))
    t = _t_along_wall(parse_pv2(wall["points"]), point_px)
    direction = _wall_tangent(wall)
    rotation = _rotation_for_direction(direction)
    return add_portal(wall, ids, t=t, direction=direction, rotation=rotation, texture=palette.door, locked=locked)


def _add_door_at_point(level, ids, room, point_grid: tuple[float, float], palette, side: int) -> dict | None:
    wall = _wall_for_side(level, room.rect, side)
    if wall is None:
        return None
    return _add_door_to_wall(wall, ids, point_grid, palette)


def _side_of_point(rect: Rect, x: float, y: float) -> int | None:
    """Il lato di `rect` su cui cade il punto, o None se il punto non sta sul
    suo perimetro. Tolleranza stretta: le coordinate qui sono calcolate, non
    misurate, e un punto o e sul bordo o non c'e."""
    eps = 1e-9
    if abs(y - rect.y1) < eps and rect.x1 - eps <= x <= rect.x2 + eps:
        return _TOP
    if abs(y - rect.y2) < eps and rect.x1 - eps <= x <= rect.x2 + eps:
        return _BOTTOM
    if abs(x - rect.x1) < eps and rect.y1 - eps <= y <= rect.y2 + eps:
        return _LEFT
    if abs(x - rect.x2) < eps and rect.y1 - eps <= y <= rect.y2 + eps:
        return _RIGHT
    return None


def _t_on_rect_side(rect: Rect, side: int, point: tuple[float, float]) -> float:
    """Posizione del punto lungo il lato `side` di rect, come frazione 0..1."""
    (x0, y0), (x1, y1) = _side_corners(rect, side)
    dx, dy = x1 - x0, y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return 0.0
    t = ((point[0] - x0) * dx + (point[1] - y0) * dy) / length_sq
    return min(max(t, 0.0), 1.0)


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


def _long_sides(corridor: Rect) -> tuple[int, int]:
    """I due lati su cui vanno i muri di un canale: quelli paralleli alla
    direzione di marcia. L'orientamento e un dato esplicito di Corridor, non
    si indovina piu da `w >= h` (vedi model.Corridor e il gate M3, TASK-26);
    il fallback serve solo ai Rect nudi passati a mano nei test."""
    horizontal = getattr(corridor, "horizontal", corridor.w >= corridor.h)
    return (_TOP, _BOTTOM) if horizontal else (_LEFT, _RIGHT)


def _subtract_intervals(span: tuple[float, float], holes) -> list[tuple[float, float]]:
    """`span` meno una lista di intervalli, come lista di pezzi rimasti."""
    pieces = [span]
    for h1, h2 in holes:
        remaining = []
        for a, b in pieces:
            if h2 <= a or h1 >= b:
                remaining.append((a, b))
                continue
            if a < h1:
                remaining.append((a, h1))
            if h2 < b:
                remaining.append((h2, b))
        pieces = remaining
    return pieces


def _channel_wall_pieces(corridor: Rect, side: int, channels) -> list[tuple[tuple, tuple]]:
    """Pezzi del muro `side` di `corridor` che vanno davvero disegnati.

    Si toglie ogni tratto che cade DENTRO un altro canale: li il corridoio
    prosegue, e un muro pieno chiuderebbe il passaggio. E' la regola che
    apre il gomito di una L (docs/format.md §9.3): senza, il braccio
    orizzontale mura a meta l'imbocco di quello verticale."""
    (x1, y1), (x2, y2) = _side_corners(corridor, side)
    vertical = x1 == x2
    if vertical:
        fixed, start, end = x1, min(y1, y2), max(y1, y2)
    else:
        fixed, start, end = y1, min(x1, x2), max(x1, x2)

    holes = []
    for other in channels:
        if other is corridor:
            continue
        # Confine escluso: un muro appoggiato al bordo di un altro canale
        # non lo attraversa, e restare li e proprio quello che chiude
        # l'angolo esterno del gomito.
        across = (other.x1, other.x2) if vertical else (other.y1, other.y2)
        if not across[0] < fixed < across[1]:
            continue
        holes.append((other.y1, other.y2) if vertical else (other.x1, other.x2))

    pieces = [(a, b) for a, b in _subtract_intervals((start, end), holes) if b > a]
    if vertical:
        return [((fixed, a), (fixed, b)) for a, b in pieces]
    return [((a, fixed), (b, fixed)) for a, b in pieces]


def draw_corridor_network(level, ids, corridors, palette) -> dict:
    """Disegna una rete di canali aperti: per ogni segmento il pavimento e i
    due muri lunghi, tagliati dove un altro segmento li attraversa.

    Gli estremi restano aperti di proposito: un box chiuso a 4 muri
    (draw_corridor) ribloccherebbe la porta appena tagliata nel muro della
    stanza all'estremita del corridoio (TASK-19)."""
    channels = list(corridors)
    walls, patterns = [], []
    for corridor in channels:
        patterns.append(add_pattern(level, ids, corridor, palette.floor))
        for side in _long_sides(corridor):
            for p1, p2 in _channel_wall_pieces(corridor, side, channels):
                walls.append(add_wall(level, ids, [p1, p2], palette.wall))
    return {"walls": walls, "patterns": patterns}


_ROUTE_SCAN_STEP = 1.0  # quadretti fra due posizioni provate per l'asse di un canale
_ROUTE_SCAN_MAX = 12  # posizioni provate per asse: oltre, la stanza e semplicemente troppo lontana


def _overlap_area(rect: Rect, other: Rect) -> float:
    """Area della sovrapposizione STRETTA fra due rettangoli. Zero se si
    toccano soltanto lungo un bordo: un corridoio che si ferma sul muro
    della stanza che collega la tocca, ed e esattamente quello che deve
    fare."""
    ox = min(rect.x2, other.x2) - max(rect.x1, other.x1)
    oy = min(rect.y2, other.y2) - max(rect.y1, other.y1)
    return ox * oy if ox > 0 and oy > 0 else 0.0


def _centers_to_try(lo: float, hi: float, half: float, preferred: float) -> list[float]:
    """Posizioni possibili per l'asse di un canale largo 2*half che deve
    restare dentro [lo, hi], ordinate a partire da `preferred` e poi verso
    l'esterno: la rotta preferita resta quella centrata, gli scostamenti
    servono solo a scansare una stanza."""
    low, high = lo + half, hi - half
    if high < low:  # banda piu stretta del corridoio: resta solo il centro
        return [(lo + hi) / 2]
    base = min(max(preferred, low), high)
    centers = [base]
    offset = _ROUTE_SCAN_STEP
    while len(centers) < _ROUTE_SCAN_MAX and (base - offset >= low or base + offset <= high):
        for center in (base - offset, base + offset):
            if low <= center <= high:
                centers.append(center)
        offset += _ROUTE_SCAN_STEP
    return centers


def _straight_route(rect_a: Rect, rect_b: Rect, half: float, center: float, *, horizontal: bool):
    """Corridoio dritto fra due rettangoli che condividono una banda su un
    asse. `center` e la quota dell'asse del canale."""
    if horizontal:
        side_a, side_b = (_RIGHT, _LEFT) if rect_a.x2 <= rect_b.x1 else (_LEFT, _RIGHT)
        x1, x2 = (rect_a.x2, rect_b.x1) if side_a == _RIGHT else (rect_b.x2, rect_a.x1)
        segment = Corridor(x1, center - half, x2, center + half, horizontal=True)
        door_a = (side_a, (rect_a.x2 if side_a == _RIGHT else rect_a.x1, center))
        door_b = (side_b, (rect_b.x1 if side_b == _LEFT else rect_b.x2, center))
    else:
        side_a, side_b = (_BOTTOM, _TOP) if rect_a.y2 <= rect_b.y1 else (_TOP, _BOTTOM)
        y1, y2 = (rect_a.y2, rect_b.y1) if side_a == _BOTTOM else (rect_b.y2, rect_a.y1)
        segment = Corridor(center - half, y1, center + half, y2, horizontal=False)
        door_a = (side_a, (center, rect_a.y2 if side_a == _BOTTOM else rect_a.y1))
        door_b = (side_b, (center, rect_b.y1 if side_b == _TOP else rect_b.y2))
    return [segment], door_a, door_b


def _elbow_route(rect_a: Rect, rect_b: Rect, half: float, cy: float, cx: float):
    """L: esce da rect_a in orizzontale alla quota cy, gira sulla verticale
    x=cx ed entra in rect_b dall'alto o dal basso. None se la piega cadrebbe
    dentro uno dei due rettangoli.

    I due bracci coprono ENTRAMBI il quadrato d'angolo: a lasciare aperto il
    gomito e il taglio dei muri di _channel_wall_pieces, non un buco nella
    geometria. Se il braccio si fermasse prima, il pavimento avrebbe un
    tassello mancante proprio nella piega."""
    if cx > rect_a.x2:
        side_a, exit_x = _RIGHT, rect_a.x2
    elif cx < rect_a.x1:
        side_a, exit_x = _LEFT, rect_a.x1
    else:
        return None

    if cy < rect_b.y1:
        side_b, entry_y = _TOP, rect_b.y1
    elif cy > rect_b.y2:
        side_b, entry_y = _BOTTOM, rect_b.y2
    else:
        return None

    leg_h = Corridor(
        min(exit_x, cx - half), cy - half, max(exit_x, cx + half), cy + half, horizontal=True
    )
    leg_v = Corridor(
        cx - half, min(cy - half, entry_y), cx + half, max(cy + half, entry_y), horizontal=False
    )
    return [leg_h, leg_v], (side_a, (exit_x, cy)), (side_b, (cx, entry_y))


def _pairs_by_closeness(first: list, second: list):
    """Coppie dalle due liste, che sono gia ordinate dal valore preferito in
    fuori: si scorre per somma degli indici, cosi le rotte piu vicine a
    quella centrata vengono provate per prime."""
    for _, i, j in sorted(
        (i + j, i, j) for i in range(len(first)) for j in range(len(second))
    ):
        yield first[i], second[j]


def _candidate_routes(rect_a: Rect, rect_b: Rect, half: float):
    """Rotte possibili in ordine di preferenza: prima il corridoio dritto
    (quando le due stanze condividono una banda su un asse), poi le due L,
    quella che esce in orizzontale e quella che esce in verticale."""
    if max(rect_a.y1, rect_b.y1) < min(rect_a.y2, rect_b.y2):
        lo, hi = max(rect_a.y1, rect_b.y1), min(rect_a.y2, rect_b.y2)
        for cy in _centers_to_try(lo, hi, half, (lo + hi) / 2):
            yield _straight_route(rect_a, rect_b, half, cy, horizontal=True)

    if max(rect_a.x1, rect_b.x1) < min(rect_a.x2, rect_b.x2):
        lo, hi = max(rect_a.x1, rect_b.x1), min(rect_a.x2, rect_b.x2)
        for cx in _centers_to_try(lo, hi, half, (lo + hi) / 2):
            yield _straight_route(rect_a, rect_b, half, cx, horizontal=False)

    ys_a = _centers_to_try(rect_a.y1, rect_a.y2, half, rect_a.center()[1])
    xs_b = _centers_to_try(rect_b.x1, rect_b.x2, half, rect_b.center()[0])
    for cy, cx in _pairs_by_closeness(ys_a, xs_b):
        route = _elbow_route(rect_a, rect_b, half, cy, cx)
        if route is not None:
            yield route

    # Stessa L percorsa dall'altro capo: da rect_a esce in verticale.
    ys_b = _centers_to_try(rect_b.y1, rect_b.y2, half, rect_b.center()[1])
    xs_a = _centers_to_try(rect_a.x1, rect_a.x2, half, rect_a.center()[0])
    for cy, cx in _pairs_by_closeness(ys_b, xs_a):
        route = _elbow_route(rect_b, rect_a, half, cy, cx)
        if route is not None:
            segments, door_b, door_a = route
            yield segments, door_a, door_b


def plan_corridor(rect_a: Rect, rect_b: Rect, width: float = 1.0, obstacles=()):
    """Geometria pura (nessun accesso a level/ids) del corridoio fra due
    rettangoli NON adiacenti: usata sia da connect() per disegnare, sia dai
    generatori (TASK-21+) per popolare Blueprint.corridors/Room.doors prima
    che qualunque muro esista. Ritorna (segments, door_a, door_b) dove
    segments e una lista di Corridor e door_a/door_b sono (side, point_grid).

    `obstacles` sono le altre stanze della mappa: fra le rotte candidate si
    sceglie la prima che non entra in nessuna, e se sono tutte bloccate la
    meno invadente. Senza questo controllo la rotta a L predefinita passa
    dritta dentro le stanze che trova, com'e successo nel gate umano M3
    (TASK-26: "il corridoio che le collega interseca altre stanze")."""
    half = width / 2
    blockers = [rect_a, rect_b, *obstacles]

    best_route, best_cost = None, None
    for route in _candidate_routes(rect_a, rect_b, half):
        cost = sum(_overlap_area(segment, b) for segment in route[0] for b in blockers)
        if cost == 0:
            return route
        if best_cost is None or cost < best_cost:
            best_route, best_cost = route, cost

    if best_route is None:
        raise ValueError(f"Nessuna rotta possibile fra {rect_a} e {rect_b}")
    return best_route


def _connect_with_corridor(level, ids, room_a, room_b, palette, obstacles=()) -> dict:
    segments, door_a, door_b = plan_corridor(room_a.rect, room_b.rect, obstacles=obstacles)
    draw_corridor_network(level, ids, segments, palette)

    portals = []
    for room, (side, point) in ((room_a, door_a), (room_b, door_b)):
        portal = _add_door_at_point(level, ids, room, point, palette, side)
        if portal is not None:
            portals.append(portal)

    return {"portal": None, "corridors": list(segments), "portals": portals}


def connect(level, ids, room_a, room_b, palette, obstacles=()) -> dict:
    """Trova il muro condiviso o genera un corridoio a L fra due stanze.

    `obstacles` sono i Rect delle altre stanze, da evitare quando serve un
    corridoio. Ritorna sempre {'portal', 'corridors', 'portals'}: nel caso
    adiacente 'portal' e la singola porta creata (anche in 'portals'); nel
    caso a corridoio 'portal' e None e 'portals' contiene le porte agli
    estremi.
    """
    shared = _shared_wall_segment(room_a.rect, room_b.rect)
    if shared is not None:
        side_a, side_b, midpoint = shared
        return _connect_adjacent(level, ids, room_a, room_b, palette, side_a, side_b, midpoint)

    return _connect_with_corridor(level, ids, room_a, room_b, palette, obstacles)


def _building_footprint(blueprint) -> Rect:
    """Bounding box di tutte le stanze PIU il vano scale: perimetro portante
    e sagoma del tetto.

    Il vano scale va incluso: e un ambiente dell'edificio come gli altri, e
    lasciarlo fuori dal bounding box significa disegnargli il muro portante
    addosso e mettere il tetto solo su meta pianta. Nel gate umano M4 il vano
    scale cadeva proprio fuori dal perimetro e Jay non lo riconosceva
    (TASK-30)."""
    rects = [room.rect for room in blueprint.rooms]
    if blueprint.stairs_rect is not None:
        rects.append(blueprint.stairs_rect)
    return Rect(
        min(r.x1 for r in rects), min(r.y1 for r in rects),
        max(r.x2 for r in rects), max(r.y2 for r in rects),
    )


def rooms_by_level(blueprint) -> dict[int, list[Room]]:
    """Raggruppa blueprint.rooms per Room.level (TASK-27/28). Riusata da
    draw_building, furnish_building e dal wiring CLI per la luce (TASK-30)."""
    grouped: dict[int, list[Room]] = {}
    for room in blueprint.rooms:
        grouped.setdefault(room.level, []).append(room)
    return grouped


def floor_blueprint(blueprint, rooms: list[Room]) -> Blueprint:
    """Blueprint sintetico con le sole stanze di un piano: furnish() (TASK-23)
    ha un contratto a un solo livello, quindi va invocata una volta per
    piano su un edificio multi-livello."""
    return Blueprint(
        width=blueprint.width, height=blueprint.height, rooms=rooms, corridors=[],
        graph={i: [] for i in range(len(rooms))}, seed=blueprint.seed, style=blueprint.style,
    )


def furnish_building(level_stack: dict, ids, blueprint, palette, *, density: str = "medium", rng) -> None:
    """Come furnish(), ma per un edificio multi-piano (TASK-30): ogni stanza
    riceve arredo solo nel livello a cui appartiene."""
    for level_key, floor_rooms in rooms_by_level(blueprint).items():
        level = level_stack.get(str(level_key))
        if level is None or not floor_rooms:
            continue
        furnish(level, ids, floor_blueprint(blueprint, floor_rooms), palette, density=density, rng=rng)


def _sides_on_rect(rect: Rect, outer: Rect) -> set[int]:
    """I lati di `rect` che giacciono su un lato di `outer` (tipicamente il
    perimetro portante dell'edificio)."""
    sides = set()
    if rect.y1 == outer.y1:
        sides.add(_TOP)
    if rect.x2 == outer.x2:
        sides.add(_RIGHT)
    if rect.y2 == outer.y2:
        sides.add(_BOTTOM)
    if rect.x1 == outer.x1:
        sides.add(_LEFT)
    return sides


def _stairwell_room(stairs: Rect, floor_rooms: list[Room]) -> Room:
    """Il vano scale come Room, con le porte che le stanze adiacenti gli
    aprono gia rispecchiate sui suoi lati.

    Una porta fra due ambienti sta su due muri sovrapposti — quello di chi
    apre e quello di chi riceve — e va bucata su entrambi: e la stessa
    convenzione che _connect_rooms usa fra due stanze. Prima del gate umano
    M4 il vano scale veniva disegnato come quattro muri ciechi, che
    tappavano da dentro la porta appena aperta dalla stanza accanto
    (TASK-30)."""
    room = Room(rect=stairs, kind="vano_scale")
    for neighbour in floor_rooms:
        for door in neighbour.doors:
            point = _door_point_grid(neighbour.rect, door)
            side = _side_of_point(stairs, point[0], point[1])
            if side is None:
                continue
            room.doors.append(Door(
                wall_index=side, t=_t_on_rect_side(stairs, side, point),
                kind=door.kind, locked=door.locked,
            ))
    return room


def draw_building(level_stack: dict, ids, blueprint, palette) -> None:
    """Edificio multi-piano (SPEC.md §6.6/§9.2): distribuisce le stanze sui
    livelli (Room.level), aggiunge il vano scale (blueprint.stairs_rect,
    stesso Rect su ogni piano per costruzione) e il tetto solo sull'ultimo
    piano. level_stack e nella stessa forma di prepared['world']['levels']
    (dict con chiavi stringa '0'..'N-1', da template.prepare)."""
    load_bearing = palette.wall_load_bearing or palette.wall
    footprint = _building_footprint(blueprint)
    footprint_corners = [
        (footprint.x1, footprint.y1), (footprint.x2, footprint.y1),
        (footprint.x2, footprint.y2), (footprint.x1, footprint.y2),
    ]

    rooms_by_level: dict[int, list[Room]] = {}
    for room in blueprint.rooms:
        rooms_by_level.setdefault(room.level, []).append(room)

    level_keys = sorted(level_stack.keys(), key=int)
    top_level_key = level_keys[-1] if level_keys else None

    for level_key in level_keys:
        level = level_stack[level_key]
        floor_index = int(level_key)
        floor_rooms = rooms_by_level.get(floor_index, [])

        # Perimetro portante: stesso footprint su ogni piano. Va disegnato per
        # primo perche le stanze che ci si appoggiano contro possano saltare
        # quel lato invece di raddoppiarlo.
        perimeter_walls = [
            add_wall(level, ids, [footprint_corners[i], footprint_corners[(i + 1) % 4]], load_bearing)
            for i in range(4)
        ]

        # Tramezzi e porte delle stanze di questo piano, piu il vano scale,
        # che e un ambiente come gli altri: stesso Rect su ogni piano per
        # costruzione, e le porte che gli aprono le stanze adiacenti gli
        # vanno rispecchiate addosso, altrimenti il suo muro le tappa.
        drawn = list(floor_rooms)
        if blueprint.stairs_rect is not None:
            drawn.append(_stairwell_room(blueprint.stairs_rect, floor_rooms))

        for room in drawn:
            skip_sides = _sides_on_rect(room.rect, footprint)
            draw_room(level, ids, room, palette, skip_sides=skip_sides)
            # Le porte dei lati saltati finiscono sul muro portante: e li che
            # devono stare, o restano murate sotto di esso (gate umano M4).
            for door in room.doors:
                if door.wall_index in skip_sides:
                    point = _door_point_grid(room.rect, door)
                    side = _side_of_point(footprint, point[0], point[1])
                    if side is not None:
                        _add_door_to_wall(perimeter_walls[side], ids, point, palette, locked=door.locked)

        # Una scala visibile al centro del vano: senza, il vano scale e
        # una stanzetta vuota indistinguibile da un ripostiglio (gate
        # umano M4, TASK-30).
        if blueprint.stairs_rect is not None and palette.stairs is not None:
            stairs_x, stairs_y = blueprint.stairs_rect.center()
            add_object(level, ids, stairs_x, stairs_y, palette.stairs)

        # Tetto solo sull'ultimo piano. sun_direction non viene toccato:
        # template.prepare duplica lo stesso livello sorgente su ogni
        # piano, quindi e gia coerente su tutto l'edificio.
        if level_key == top_level_key and palette.roof is not None:
            add_roof(level, ids, footprint_corners, palette.roof)


def render_blueprint(level, ids, blueprint, palette) -> None:
    """Disegna un Blueprint intero in un livello gia preparato (TASK-24):
    ogni Room via draw_room (le porte sono gia decise dal generatore in
    Room.doors) e tutti i corridoi come un'unica rete di canali aperti.
    La rete va disegnata in blocco, non un segmento alla volta: e cosi che
    i muri di un braccio sanno di doversi fermare dove ne inizia un altro
    (docs/format.md §9.3)."""
    for room in blueprint.rooms:
        draw_room(level, ids, room, palette)
    draw_corridor_network(level, ids, blueprint.corridors, palette)


# Texture base di Dungeondraft (non di un pack, quindi esente da DDF014) per
# le strade di generators/city.py (TASK-35, SPEC.md §9.4 AC2). Nessun
# template disponibile contiene un elemento 'path' da cui ricavarla via
# assets.build_catalog (data/assets.json['paths'] e vuoto): verificata
# cercando 'res://textures/paths/' dentro Dungeondraft.pck (installazione
# locale), dove compare come texture base — stesso trattamento gia dato ai
# base texture path di scripts/demo_m1.py (stone.png), mai passati dal
# catalogo. Da confermare visivamente al gate umano di TASK-36.
_STREET_TEXTURE = "res://textures/paths/cobble.png"


def _street_path_points(street: Rect) -> tuple[list[tuple[float, float]], float]:
    """Centro-linea e larghezza (in quadretti) di un segmento di strada:
    city._split_with_gap produce Rect stretti e lunghi, mai quadrati (vedi
    city._MIN_BLOCK), quindi il lato corto identifica sempre l'asse di
    marcia senza ambiguita (a differenza di compose._long_sides, che per
    questo ha bisogno del campo esplicito Corridor.horizontal)."""
    if street.h >= street.w:
        cx = (street.x1 + street.x2) / 2
        return [(cx, street.y1), (cx, street.y2)], street.w
    cy = (street.y1 + street.y2) / 2
    return [(street.x1, cy), (street.x2, cy)], street.h


def render_city_blueprint(level_stack: dict, ids, blueprint, palette) -> None:
    """Disegna un Blueprint di quartiere/citta (TASK-35, SPEC.md §9.4):
    strade come add_path (AC2, mai come pattern), piazze come pavimento
    diverso + elemento centrale (AC5), ed edifici delegati a draw_building,
    una chiamata per edificio perche ognuno e un Blueprint a se (footprint e
    tetto propri, TASK-35: "riusa building.py a un solo piano" vuol dire un
    edificio per lotto, non tutti i lotti in un unico Blueprint)."""
    level = level_stack["0"]

    for street in blueprint.streets:
        points, width = _street_path_points(street)
        add_path(level, ids, points, _STREET_TEXTURE, width=int(grid_to_px(width)))

    plaza_texture = palette.floors.get("piazza", palette.floor)
    fountain = palette.accents.get("fountain")
    for plaza in blueprint.plazas:
        add_pattern(level, ids, plaza, plaza_texture)
        if fountain is not None:
            cx, cy = plaza.center()
            add_object(level, ids, cx, cy, fountain)

    for building_blueprint in blueprint.buildings:
        draw_building(level_stack, ids, building_blueprint, palette)


def render_cave_blueprint(level, blueprint) -> None:
    """Scrive un Blueprint di grotta (TASK-32/decision-1) nel layer cave
    nativo, invece di render_blueprint: una grotta non ha Room/Corridor
    (blueprint.cave_grid al loro posto), quindi niente draw_room/muri/porte.
    Nessun `palette`/`ids`: set_cave_bitmap non disegna elementi con
    node_id, sovrascrive un blob gia dimensionato dal template."""
    if blueprint.cave_grid is None:
        raise ValueError("blueprint.cave_grid e None: non e un Blueprint di grotta")
    set_cave_bitmap(level, blueprint.cave_grid, blueprint.width, blueprint.height)


# ---------------------------------------------------------------------------
# fognature: camere di giunzione circolari (TASK-33)
# ---------------------------------------------------------------------------

_CHAMBER_SIDES = 16
# Angolo (in radianti, convenzione standard x=cos/y=sin) di ciascun lato
# cardinale sul poligono che approssima il cerchio: E=0 e l'origine da cui
# partono gli indici del poligono in _chamber_circle_points, gli altri sono
# multipli di sides/4 (16 e divisibile per 4 apposta, cosi i cardinali
# cadono esattamente su un indice intero del poligono, mai fra due campioni).
_CARDINAL_ANGLE = {"E": 0.0, "S": math.pi / 2, "W": math.pi, "N": 3 * math.pi / 2}


def _chamber_gap_depth(radius: float, canal_width: float) -> float:
    """Distanza dal centro della camera al punto in cui il muro si
    interrompe per un canale (TASK-33): geometria a corda del cerchio, cosi
    il canale (largo `canal_width`, centrato sul lato cardinale) incontra il
    poligono esattamente ai due estremi del varco, senza sovrapposizioni ne
    fessure fra i due elementi."""
    half_w = canal_width / 2
    if half_w >= radius:
        raise ValueError(
            f"canal_width ({canal_width}) troppo largo per chamber_radius ({radius}): il varco non ci sta nel cerchio"
        )
    return math.sqrt(radius * radius - half_w * half_w)


def _chamber_circle_points(chamber: Chamber, sides: int = _CHAMBER_SIDES) -> list[tuple[float, float]]:
    """Poligono regolare senza varchi, per pavimento e acqua: non hanno
    bisogno di aperture, come il pavimento rettangolare di una stanza copre
    tutto il rettangolo anche dove i muri hanno una porta (_room_floor)."""
    cx, cy = chamber.center
    return [
        (
            cx + chamber.radius * math.cos(2 * math.pi * k / sides),
            cy + chamber.radius * math.sin(2 * math.pi * k / sides),
        )
        for k in range(sides)
    ]


def _chamber_gap_edge_points(chamber: Chamber, direction: str, canal_width: float) -> tuple[tuple, tuple]:
    """I due punti (quadretti) dove il muro si interrompe per il canale in
    `direction`: 'before'/'after' nel verso di angolo crescente (lo stesso
    verso di _chamber_circle_points), cosi inserirli al posto del campione
    cardinale mantiene il poligono in ordine. Calcolati dalla tangente al
    cerchio nel punto cardinale, non da un'approssimazione angolare: cosi
    coincidono esattamente con gli estremi del canale costruito con la
    stessa `_chamber_gap_depth` (generators/sewer.py)."""
    cx, cy = chamber.center
    theta = _CARDINAL_ANGLE[direction]
    depth = _chamber_gap_depth(chamber.radius, canal_width)
    half_w = canal_width / 2
    ux, uy = math.cos(theta), math.sin(theta)
    tx, ty = -math.sin(theta), math.cos(theta)  # tangente nel verso di angolo crescente
    before = (cx + depth * ux - half_w * tx, cy + depth * uy - half_w * ty)
    after = (cx + depth * ux + half_w * tx, cy + depth * uy + half_w * ty)
    return before, after


def _chamber_wall_arcs(chamber: Chamber, canal_width: float, sides: int = _CHAMBER_SIDES) -> list[list[tuple]]:
    """Punti dei muri della camera, gia spezzati sui varchi verso i canali
    collegati: un arco (lista di punti) per ogni tratto ininterrotto di
    parete. Lista vuota se tutti e 4 i lati cardinali sono collegati
    (incrocio completamente aperto: niente da murare, resta solo
    pavimento/acqua). Un solo arco (l'intero poligono) se la camera non e
    collegata a nessun canale: un anello chiuso, non spezzato."""
    if len(chamber.connected) == 4:
        return []
    if not chamber.connected:
        return [_chamber_circle_points(chamber, sides)]

    cx, cy = chamber.center
    step = 2 * math.pi / sides
    cardinal_index = {"E": 0, "S": sides // 4, "W": sides // 2, "N": 3 * sides // 4}
    gap_at = {cardinal_index[d]: d for d in chamber.connected}

    points: list[tuple] = []
    gap_after_positions: list[int] = []  # indice del punto 'after' (inizio di un arco)
    gap_before_positions: list[int] = []  # indice del punto 'before' (fine di un arco)
    for k in range(sides):
        if k in gap_at:
            before, after = _chamber_gap_edge_points(chamber, gap_at[k], canal_width)
            gap_before_positions.append(len(points))
            points.append(before)
            gap_after_positions.append(len(points))
            points.append(after)
        else:
            theta = step * k
            points.append((cx + chamber.radius * math.cos(theta), cy + chamber.radius * math.sin(theta)))

    n = len(points)
    arcs = []
    for start in gap_after_positions:
        end = min(gap_before_positions, key=lambda p: (p - start) % n)
        length = (end - start) % n
        arcs.append([points[(start + i) % n] for i in range(length + 1)])
    return arcs


def draw_chamber(level, ids, chamber: Chamber, palette, *, canal_width: float) -> dict:
    """Pavimento pieno + muri ad arco (spezzati sui varchi verso i canali
    collegati) + porta sulla camera d'ingresso (`chamber.door`, stessa
    convenzione di bsp._ENTRANCE_ROOM: la prima camera generata). Nessuna
    porta se la camera non ha nemmeno un arco libero (crocevia a 4 vie)."""
    pattern = add_polygon_pattern(level, ids, _chamber_circle_points(chamber), palette.floor)

    arcs = _chamber_wall_arcs(chamber, canal_width)
    walls = [
        add_wall(level, ids, arc, palette.wall, loop=(len(arcs) == 1 and not chamber.connected))
        for arc in arcs
    ]

    portals = []
    if chamber.door and walls:
        wall = walls[0]
        direction = _wall_tangent(wall)
        rotation = _rotation_for_direction(direction)
        portals.append(add_portal(wall, ids, t=0.5, direction=direction, rotation=rotation, texture=palette.door))

    return {"walls": walls, "pattern": pattern, "portals": portals}


def render_sewer_blueprint(level, ids, blueprint, palette) -> None:
    """Disegna la variante fognature (TASK-33, SPEC.md §9.3): i canali sono
    Corridor come qualunque altro canale (draw_corridor_network, invariato),
    le camere di giunzione sono draw_chamber. Un poligono d'acqua per ogni
    canale e ogni camera, stessa impronta dei rispettivi pavimenti (AC2)."""
    draw_corridor_network(level, ids, blueprint.corridors, palette)
    for corridor in blueprint.corridors:
        add_water_polygon(level, ids, [
            (corridor.x1, corridor.y1), (corridor.x2, corridor.y1),
            (corridor.x2, corridor.y2), (corridor.x1, corridor.y2),
        ])

    # canal_width e un parametro del generatore, non del Blueprint (nessun
    # campo dedicato): tutti i canali lo condividono per costruzione
    # (generators/sewer.py), quindi si ricava da un corridoio qualunque.
    canal_width = None
    if blueprint.corridors:
        first = blueprint.corridors[0]
        canal_width = first.h if first.horizontal else first.w

    for chamber in blueprint.chambers:
        draw_chamber(level, ids, chamber, palette, canal_width=canal_width or 0.0)
        add_water_polygon(level, ids, _chamber_circle_points(chamber))


# ---------------------------------------------------------------------------
# furnish (TASK-23)
# ---------------------------------------------------------------------------

_FURNISH_KIND_MULTIPLIER = {"boss": 1.5, "servizio": 0.5}
_WALL_MARGIN = 0.5
_DOOR_CLEARANCE = 1.5

# Distanza fra il centro di un pezzo addossato e il muro. Mezzo quadretto,
# non uno: cosi uno sprite 1x1 tocca il muro esatto e uno 2x2 (camino,
# madia) ci entra dentro per meta. Al gate M4 round 2 Jay ha corretto a mano
# i camini della cucina, portandoli da y=20.0 a y=20.5 col muro a y=21: e
# questa la misura (TASK-30).
_WALL_OFFSET = 0.5

# Ingombro in quadretti degli sprite il cui nome file non lo dichiara.
# Le texture dei pack recenti lo scrivono (Oven_..._2x2, Cupboard_..._2x1,
# Keg_..._1x1) e quello vince sempre; le png del FA Starter Pack no.
_TEXTURE_SIZE_HINTS = {
    "table": 2.0, "bed": 2.0, "oven": 2.0, "cupboard": 2.0, "bookshelf": 2.0,
    "desk": 2.0, "rug": 2.0, "bench": 2.0, "fountain": 2.0, "sarcophag": 2.0,
    "altar": 2.0, "stairs": 2.0, "cage": 2.0,
}
_TEXTURE_SIZE_DEFAULT = 1.0

# Sprite che a rotazione 0 NON hanno la faccia rivolta in giu, e a cui la
# regola generale `rotazione = lato * pi/2` va corretta di un offset fisso.
# Non e una regola geometrica ma una proprieta del singolo sprite, quindi si
# tabella per texture invece di dedurla.
#
# La botte piccola (Keg_..._H_..., "H" per horizontal) e coricata sul fianco
# lungo l'asse orizzontale: il suo asse parte gia ruotato di un quarto di
# giro. Misura del gate M4 round 3, Jay: "le botti piccole vanno ancora
# girate a destra di 90 gradi. Tutti gli altri vanno bene" — cioe il resto
# del catalogo la faccia in giu ce l'ha davvero.
_TEXTURE_ROTATION_OFFSET = {"keg": math.pi / 2}
_TACTICAL_COVER_KEYS = ("column", "crate", "barrel")
_TACTICAL_SPACING_MIN, _TACTICAL_SPACING_MAX = 3.0, 4.0

# Chiavi di Palette.accents (non texture: vedi assets._STYLE_DEFINITIONS) da
# preferire per ciascun room.kind di generators/building.py (TASK-29,
# SPEC.md §9.5 "rispettano il kind della stanza"). Se il kind non compare
# qui, o nessuna delle chiavi mappate e presente nella palette, _furnish_room
# ricade su tutti gli accents disponibili (comportamento originale di
# TASK-23, cosi dungeon/crypt/sewer/cave restano invariati).
_KIND_ACCENT_HINTS = {
    "sala_comune": ("table", "chair", "bench"),
    "cucina": ("oven", "crate", "barrel"),
    "retro": ("crate", "barrel", "keg", "cupboard"),
    "camera": ("bed", "cupboard", "desk", "bookshelf"),
    "rappresentanza": ("table", "rug", "chair", "bookshelf"),
    "privato": ("bed", "desk", "bookshelf", "cupboard"),
    "servitu": ("cupboard", "barrel", "bed", "crate"),
    "magazzino": ("crate", "barrel", "keg"),
    "soppalco": ("crate", "barrel", "keg"),
}

# Come si dispone ciascun accent dentro la stanza (TASK-30, gate umano M4).
# _WALL: addossato a una parete, parallelo a essa. _CENTER: nella fascia
# centrale. _AROUND: attorno all'ultimo pezzo _CENTER piazzato (le sedie
# intorno al tavolo). Le chiavi non elencate ricadono su _WALL: quasi tutto
# l'arredo di un ambiente abitato sta contro un muro, non in mezzo al
# pavimento.
_WALL, _CENTER, _AROUND = "wall", "center", "around"
_ACCENT_PLACEMENT = {
    "table": _CENTER,
    "chair": _AROUND,
    "rug": _CENTER,
    "fountain": _CENTER,
    "brazier": _CENTER,
}

# Quanti pezzi per accent, in funzione dell'area: (quadretti per pezzo,
# massimo). Un arredo deve far capire a cosa serve la stanza, non
# ricoprirne il pavimento: nel gate M4 la densita per-quadretto senza tetto
# produceva 77 letti in una camera e Jay ha visto solo "stanze piene di
# botti".
#
# Tarate su stanze VERE: a 1.5 m per quadretto una camera sta in 20-30
# quadretti e una sala comune in 50. La prima taratura (90 quadretti per
# tavolo, 110 per letto) valeva per le stanze da 600 quadretti del round 1 e
# su una stanza vera dava un pezzo per tipo e basta.
_ACCENT_QUOTA = {
    "table": (18, 4),
    "chair": (6, 8),
    "bench": (22, 4),
    "bed": (16, 3),
    "crate": (14, 5),
    "barrel": (16, 5),
    "keg": (20, 3),
    "cupboard": (22, 3),
    "desk": (30, 2),
    "bookshelf": (20, 4),
    "oven": (40, 2),
    "rug": (30, 2),
}
_ACCENT_QUOTA_DEFAULT = (20, 3)

# Moltiplicatore per densita richiesta dal CLI: 'medium' e la taratura di
# riferimento delle quote qui sopra.
_DENSITY_SCALE = {"none": 0.0, "light": 0.5, "medium": 1.0, "heavy": 1.5}


def _door_point_grid(rect: Rect, door) -> tuple[float, float]:
    (x0, y0), (x1, y1) = _side_corners(rect, door.wall_index)
    return (x0 + (x1 - x0) * door.t, y0 + (y1 - y0) * door.t)


def _is_clear_of_walls_and_doors(x: float, y: float, rect: Rect, door_points) -> bool:
    if not (rect.x1 + _WALL_MARGIN <= x <= rect.x2 - _WALL_MARGIN):
        return False
    if not (rect.y1 + _WALL_MARGIN <= y <= rect.y2 - _WALL_MARGIN):
        return False
    return all(math.hypot(x - dx, y - dy) >= _DOOR_CLEARANCE for dx, dy in door_points)


def _texture_size(texture: str) -> float:
    """Ingombro di uno sprite in quadretti (il lato maggiore).

    Serve a non piazzare due pezzi uno sopra l'altro. Il nome file e la
    fonte migliore quando lo dichiara — Oven_Brick_Red_A2_2x2,
    Cupboard_Wood_Light_D_2x1, Keg_Wood_Light_H_1x1 — e in quel caso vince
    su tutto; per le png del FA Starter Pack, che non lo scrivono, resta una
    tabella di ripiego per nome semantico."""
    name = texture.rsplit("/", 1)[-1].lower()
    match = re.search(r"(\d+)x(\d+)", name)
    if match:
        return float(max(int(match.group(1)), int(match.group(2))))
    for hint, size in _TEXTURE_SIZE_HINTS.items():
        if hint in name:
            return size
    return _TEXTURE_SIZE_DEFAULT


def _rotation_offset(texture: str) -> float:
    """Quarto di giro (o zero) da sommare alla rotazione dettata dal lato,
    per gli sprite il cui asse non parte rivolto in giu. Vedi
    _TEXTURE_ROTATION_OFFSET."""
    name = texture.rsplit("/", 1)[-1].lower()
    for hint, offset in _TEXTURE_ROTATION_OFFSET.items():
        if hint in name:
            return offset
    return 0.0


def _oriented(texture: str, rotation: float) -> float:
    """La rotazione da scrivere davvero per questo sprite, normalizzata in
    [0, 2pi)."""
    return (rotation + _rotation_offset(texture)) % (2 * math.pi)


def _is_free(x: float, y: float, size: float, placed, ignore: int | None = None) -> bool:
    """True se il pezzo non si sovrappone a nessuno di quelli gia piazzati.

    Due pezzi non possono stare piu vicini della semisomma dei loro
    ingombri. `ignore` esclude un indice: e il tavolo attorno a cui una
    sedia sta girando, dove l'adiacenza stretta e voluta."""
    for index, (px, py, psize) in enumerate(placed):
        if index == ignore:
            continue
        if math.hypot(x - px, y - py) < (size + psize) / 2:
            return False
    return True


def _wall_slot(rect: Rect, rng) -> tuple[float, float, float]:
    """Un punto addossato a una parete, con la faccia rivolta VERSO L'INTERNO
    della stanza.

    La rotazione dipende dal lato e da nient'altro: top 0, right pi/2,
    bottom pi, left 3pi/2, cioe `lato * pi/2` con gli indici di
    _draw_perimeter. Prima del gate M4 round 2 i lati alto e basso avevano
    entrambi rotazione 0 e i lati destro e sinistro entrambi pi/2: meta
    dell'arredo finiva con la faccia contro il muro, ed e quello che Jay ha
    visto ('i camini sono girati', 'l'armadio a sinistra e girato', 'molti
    degli sprite guardano il muro'). La misura che fissa la convenzione e il
    camino che ha raddrizzato lui sul muro basso della cucina: pi, non 0."""
    side = rng.choice((_TOP, _RIGHT, _BOTTOM, _LEFT))
    rotation = side * math.pi / 2
    if side in (_TOP, _BOTTOM):
        x = rng.uniform(rect.x1 + 1.0, rect.x2 - 1.0)
        y = rect.y1 + _WALL_OFFSET if side == _TOP else rect.y2 - _WALL_OFFSET
        return x, y, rotation
    y = rng.uniform(rect.y1 + 1.0, rect.y2 - 1.0)
    x = rect.x1 + _WALL_OFFSET if side == _LEFT else rect.x2 - _WALL_OFFSET
    return x, y, rotation


def _center_slot(rect: Rect, rng) -> tuple[float, float, float]:
    """Un punto nella fascia centrale della stanza (tavoli, tappeti)."""
    x = rng.uniform(rect.x1 + rect.w * 0.3, rect.x2 - rect.w * 0.3)
    y = rng.uniform(rect.y1 + rect.h * 0.3, rect.y2 - rect.h * 0.3)
    return x, y, rng.choice((0.0, math.pi / 2))


def _around_slot(anchor: tuple[float, float], index: int) -> tuple[float, float, float]:
    """Il posto di una sedia attorno al tavolo `anchor`: i quattro lati in
    ordine, ciascuno con la faccia rivolta al tavolo."""
    dx, dy = ((0, -1.2), (1.2, 0), (0, 1.2), (-1.2, 0))[index % 4]
    rotation = (math.pi, 3 * math.pi / 2, 0.0, math.pi / 2)[index % 4]
    return anchor[0] + dx, anchor[1] + dy, rotation


def _accent_count(key: str, area: float, scale: float) -> int:
    """Quanti pezzi di questo accent, per una stanza di `area` quadretti.

    `scale` moltiplica sia il tasso sia il TETTO. Se agisse solo sul tasso,
    in una stanza abbastanza grande il tetto saturerebbe comunque e
    density=light, medium e heavy darebbero lo stesso arredo — che e quel
    che succedeva appena le quote sono state tarate su stanze vere."""
    per_piece, cap = _ACCENT_QUOTA.get(key, _ACCENT_QUOTA_DEFAULT)
    return min(max(1, round(cap * scale)), max(1, round(area / per_piece * scale)))


def _furnish_room(level, ids, room: Room, palette, rng, density: str, placed: list) -> None:
    """Arreda una stanza per ricetta, non per densita uniforme.

    Ogni accent previsto dal kind riceve una quota propria (poche unita, con
    un tetto) e una disposizione propria: addossato a un muro, al centro, o
    attorno a un pezzo centrale. Fino al gate umano M4 si spargeva invece un
    numero di oggetti proporzionale all'area, a caso e con rotazione
    casuale: 65 pezzi nella sala comune, 77 letti in una camera, e stanze
    che Jay ha descritto come "piene di botti" (TASK-30).

    `placed` e la lista (x, y, ingombro) di tutto cio che sta gia sul piano,
    condivisa fra le stanze: e cosi che due pezzi non si sovrappongono."""
    if not palette.accents:
        return
    # Il moltiplicatore del kind entra nella scala, non nell'area: deve
    # muovere anche il tetto per pezzo, o la stanza del boss e lo sgabuzzino
    # saturano lo stesso tetto e ricevono lo stesso arredo.
    scale = _DENSITY_SCALE[density] * _FURNISH_KIND_MULTIPLIER.get(room.kind, 1.0)
    if scale == 0:
        return

    hint_keys = _KIND_ACCENT_HINTS.get(room.kind, ())
    keys = [k for k in hint_keys if k in palette.accents] or sorted(palette.accents)
    door_points = [_door_point_grid(room.rect, d) for d in room.doors]
    area = room.rect.w * room.rect.h

    anchors: list[int] = []  # indici in `placed` dei pezzi _CENTER di questa stanza
    for key in keys:
        placement = _ACCENT_PLACEMENT.get(key, _WALL)
        texture = palette.accents[key]
        size = _texture_size(texture)
        if placement == _AROUND and not anchors:
            placement = _WALL  # niente tavolo in questa stanza: la sedia va al muro
        for i in range(_accent_count(key, area, scale)):
            anchor_index = None
            if placement == _AROUND:
                # Quattro sedie per tavolo, poi si passa al tavolo dopo. Con
                # un solo indice `i % 4` e un'ancora sola le sedie oltre la
                # quarta ricadevano sugli stessi quattro punti: sul file del
                # round 1 c'erano quattro coppie di sedie sovrapposte.
                if i // 4 >= len(anchors):
                    break
                anchor_index = anchors[i // 4]

            for _ in range(24):  # qualche tentativo, poi si rinuncia al pezzo
                if placement == _CENTER:
                    x, y, rotation = _center_slot(room.rect, rng)
                elif anchor_index is not None:
                    ax, ay, _size = placed[anchor_index]
                    x, y, rotation = _around_slot((ax, ay), i % 4)
                else:
                    x, y, rotation = _wall_slot(room.rect, rng)

                free = (
                    _is_clear_of_walls_and_doors(x, y, room.rect, door_points)
                    and _is_free(x, y, size, placed, ignore=anchor_index)
                )
                if free:
                    add_object(level, ids, x, y, texture, rotation=_oriented(texture, rotation))
                    placed.append((x, y, size))
                    if placement == _CENTER:
                        anchors.append(len(placed) - 1)
                    break
                if anchor_index is not None:
                    break  # il posto attorno al tavolo e quello, non se ne cerca un altro


def _furnish_tactical_cover(level, ids, room: Room, palette, rng, placed: list) -> None:
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
            texture = rng.choice(cover_textures)
            size = _texture_size(texture)
            if _is_clear_of_walls_and_doors(x, y, room.rect, door_points) and _is_free(x, y, size, placed):
                add_object(level, ids, x, y, texture, rotation=_oriented(texture, 0.0))
                placed.append((x, y, size))
            y += spacing
        x += spacing


def _placed_from_level(level) -> list[tuple[float, float, float]]:
    """Quel che sta gia sul livello, nella forma che serve a _is_free.

    furnish() gira DOPO draw_building, che ha gia messo la scala nel vano:
    senza contarla, un barile ci finirebbe sopra."""
    placed = []
    for obj in level.get("objects", []):
        try:
            inner = obj["position"][obj["position"].index("(") + 1 : obj["position"].index(")")]
            x_str, y_str = inner.split(",")
        except (KeyError, ValueError):
            continue
        placed.append((float(x_str) / GRID, float(y_str) / GRID, _texture_size(obj.get("texture", ""))))
    return placed


def furnish(level, ids, blueprint, palette, *, density: str = "medium", rng) -> None:
    """Arredo trasversale applicato dopo la geometria (SPEC.md §9.5).

    Non tocca mai i corridoi (blueprint.corridors non sono Room: restano
    sempre vuoti). rng va passato dal chiamante, mai creato qui, per
    riproducibilita a parita di seed."""
    if density not in _DENSITY_SCALE:
        raise ValueError(f"density sconosciuta: {density!r}. Valide: {sorted(_DENSITY_SCALE)}")

    placed = _placed_from_level(level)
    tactical = set(getattr(blueprint, "tactical_rooms", []))
    for i, room in enumerate(blueprint.rooms):
        _furnish_room(level, ids, room, palette, rng, density, placed)
        if i in tactical:
            _furnish_tactical_cover(level, ids, room, palette, rng, placed)
