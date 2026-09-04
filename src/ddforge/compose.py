"""Composti: stanza, corridoio, edificio.

Vedi docs/SPEC.md §6.6. draw_room/draw_corridor implementati in TASK-18;
connect in TASK-19; furnish in TASK-23 (SPEC.md §9.5 non gli assegna un
file dedicato: e un altro composto Blueprint -> JSON); draw_building in
TASK-27.
"""

import math

from ddforge.build import add_light, add_object, add_pattern, add_portal, add_roof, add_wall
from ddforge.godot import grid_to_px, parse_pv2
from ddforge.model import Blueprint, Corridor, Rect, Room

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
    """Bounding box di tutte le stanze: perimetro portante e sagoma del tetto."""
    rects = [room.rect for room in blueprint.rooms]
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

        # Perimetro portante: stesso footprint su ogni piano.
        for i in range(4):
            add_wall(level, ids, [footprint_corners[i], footprint_corners[(i + 1) % 4]], load_bearing)

        # Tramezzi e porte delle stanze di questo piano.
        for room in rooms_by_level.get(floor_index, []):
            draw_room(level, ids, room, palette)

        # Vano scale: stesso Rect su ogni piano, per costruzione.
        if blueprint.stairs_rect is not None:
            add_pattern(level, ids, blueprint.stairs_rect, palette.floor)
            stair_corners = [
                (blueprint.stairs_rect.x1, blueprint.stairs_rect.y1),
                (blueprint.stairs_rect.x2, blueprint.stairs_rect.y1),
                (blueprint.stairs_rect.x2, blueprint.stairs_rect.y2),
                (blueprint.stairs_rect.x1, blueprint.stairs_rect.y2),
            ]
            for i in range(4):
                add_wall(level, ids, [stair_corners[i], stair_corners[(i + 1) % 4]], palette.wall)

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


# ---------------------------------------------------------------------------
# furnish (TASK-23)
# ---------------------------------------------------------------------------

_DENSITY_PER_TILE = {"none": 0.0, "light": 0.05, "medium": 0.12, "heavy": 0.25}
_FURNISH_KIND_MULTIPLIER = {"boss": 1.5, "servizio": 0.5}
_WALL_MARGIN = 0.5
_DOOR_CLEARANCE = 1.5
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
    "retro": ("crate", "barrel"),
    "camera": ("bed",),
    "rappresentanza": ("table", "rug"),
    "privato": ("bed", "desk", "bookshelf"),
    "servitu": ("cupboard", "barrel"),
    "magazzino": ("crate", "barrel", "keg"),
    "soppalco": ("crate", "barrel"),
}


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
    hint_keys = _KIND_ACCENT_HINTS.get(room.kind, ())
    textures = [palette.accents[k] for k in hint_keys if k in palette.accents]
    if not textures:
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
