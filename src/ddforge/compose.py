"""Composti: stanza, corridoio, edificio.

Vedi docs/SPEC.md §6.6. Implementato in TASK-18 (draw_room, draw_corridor),
TASK-19 (connect) e TASK-27 (draw_building).
"""


def draw_room(level, ids, room, palette) -> dict:
    """Pavimento + muri perimetrali + porte + luci."""
    raise NotImplementedError


def draw_corridor(level, ids, rect, palette) -> dict:
    """Corridoio come stanza stretta senza porte alle estremita."""
    raise NotImplementedError


def connect(level, ids, room_a, room_b, palette) -> dict:
    """Trova il muro condiviso o genera un corridoio a L fra due stanze."""
    raise NotImplementedError


def draw_building(level_stack, ids, blueprint, palette) -> None:
    """Edificio multi-piano: distribuisce le stanze, aggiunge scale e tetto."""
    raise NotImplementedError
