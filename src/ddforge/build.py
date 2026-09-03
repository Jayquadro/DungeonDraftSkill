"""Primitive di disegno: ogni funzione aggiunge un elemento a un livello.

Vedi docs/SPEC.md §6.5. Implementato in TASK-10, dopo che lo schema di
lights/texts e stato derivato in TASK-3.
"""


def add_wall(level, ids, points_grid, texture, *,
             color="ffffffff", loop=False, wall_type=1,
             joint=0, shadow=True) -> dict:
    """points_grid in quadretti. Con loop=True non ripetere il primo punto."""
    raise NotImplementedError


def add_portal(wall, ids, *, t: float, direction, texture,
                radius=128, rotation=0.0, closed=True, locked=False) -> dict:
    """Aggiunge la porta dentro wall['portals']. Non spezza il muro."""
    raise NotImplementedError


def add_pattern(level, ids, rect_grid, texture, *,
                 layer=-400, color="ffffffff", outline=False) -> dict:
    raise NotImplementedError


def add_polygon_pattern(level, ids, points_grid, texture, **kw) -> dict:
    """Per pavimenti non rettangolari (grotte, isolati irregolari)."""
    raise NotImplementedError


def add_object(level, ids, x, y, texture, *,
                rotation=0.0, scale=1.0, layer=100,
                shadow=True, block_light=False, mirror=False) -> dict:
    raise NotImplementedError


def add_path(level, ids, points_grid, texture, *,
             width=472, layer=100, smoothness=1, loop=False) -> dict:
    """edit_points sono relativi a position (position = primo punto)."""
    raise NotImplementedError


def add_roof(level, ids, points_grid, texture, *, width=512, roof_type=0) -> dict:
    """Va in level['roofs']['roofs'], non in una lista di primo livello."""
    raise NotImplementedError


def add_light(level, ids, x, y, **kw) -> dict:
    """Schema derivato dal template ricco in TASK-3."""
    raise NotImplementedError


def add_text(level, ids, x, y, content, **kw) -> dict:
    """Schema derivato dal template ricco in TASK-3."""
    raise NotImplementedError
