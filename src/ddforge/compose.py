"""Composti: stanza, corridoio, edificio.

Vedi docs/SPEC.md §6.6. draw_room/draw_corridor implementati in TASK-18;
connect in TASK-19; draw_building in TASK-27.
"""

import math

from ddforge.build import add_light, add_pattern, add_portal, add_wall
from ddforge.godot import grid_to_px, parse_pv2
from ddforge.model import Room


def _outward_normal(wall: dict, room_center_grid: tuple[float, float]) -> tuple[float, float]:
    """Normale unitaria al muro, orientata verso l'esterno della stanza.

    Derivazione evidence-based (non ancora confermata dal gate umano,
    docs/format.md §5): la normale "uscente" e la scelta piu plausibile
    per portal.direction, ma la convenzione esatta di Dungeondraft resta
    da verificare aprendo il file in Dungeondraft.
    """
    points = parse_pv2(wall["points"])
    (ax, ay), (bx, by) = points[0], points[-1]
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return (0.0, 1.0)
    nx, ny = -dy / length, dx / length

    mid_x, mid_y = (ax + bx) / 2, (ay + by) / 2
    center_x, center_y = grid_to_px(room_center_grid[0]), grid_to_px(room_center_grid[1])
    to_center_x, to_center_y = center_x - mid_x, center_y - mid_y

    if nx * to_center_x + ny * to_center_y > 0:
        nx, ny = -nx, -ny
    return (nx, ny)


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
        center = rect.center()
        for door in room.doors:
            wall = walls[door.wall_index]
            direction = _outward_normal(wall, center)
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


def connect(level, ids, room_a, room_b, palette) -> dict:
    """Trova il muro condiviso o genera un corridoio a L fra due stanze."""
    raise NotImplementedError


def draw_building(level_stack, ids, blueprint, palette) -> None:
    """Edificio multi-piano: distribuisce le stanze, aggiunge scale e tetto."""
    raise NotImplementedError
