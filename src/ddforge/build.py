"""Primitive di disegno: ogni funzione aggiunge un elemento a un livello.

Input in quadretti, conversione in pixel dentro le primitive. Vedi
docs/SPEC.md §6.5 e docs/format.md §4-5 per gli schemi derivati.
"""

import math

from ddforge.godot import grid_to_px, parse_pv2, pv2, v2


def _point_along_polyline(points_px, t: float) -> tuple[float, float]:
    """Punto alla frazione `t` (0..1) lungo la spezzata, per lunghezza d'arco."""
    if len(points_px) == 1:
        return points_px[0]
    segment_lengths = [
        math.hypot(points_px[i + 1][0] - points_px[i][0], points_px[i + 1][1] - points_px[i][1])
        for i in range(len(points_px) - 1)
    ]
    total = sum(segment_lengths)
    if total == 0:
        return points_px[0]
    target = t * total
    accum = 0.0
    for i, seg_len in enumerate(segment_lengths):
        if accum + seg_len >= target or i == len(segment_lengths) - 1:
            local_t = 0.0 if seg_len == 0 else (target - accum) / seg_len
            local_t = min(max(local_t, 0.0), 1.0)
            x = points_px[i][0] + (points_px[i + 1][0] - points_px[i][0]) * local_t
            y = points_px[i][1] + (points_px[i + 1][1] - points_px[i][1]) * local_t
            return (x, y)
        accum += seg_len
    return points_px[-1]


def add_wall(level, ids, points_grid, texture, *,
             color="ffffffff", loop=False, wall_type=1,
             joint=0, shadow=True) -> dict:
    """points_grid in quadretti, convertiti in px internamente.

    Con loop=True NON ripetere il primo punto in coda: Dungeondraft chiude
    gia il poligono da solo, un punto ripetuto produce un lato doppio
    (SPEC.md §14).
    """
    if loop and len(points_grid) >= 2 and points_grid[0] == points_grid[-1]:
        raise ValueError(
            "loop=True chiude gia il poligono: non ripetere il primo punto in coda"
        )
    points_px = [(grid_to_px(x), grid_to_px(y)) for x, y in points_grid]
    wall = {
        "points": pv2(points_px),
        "texture": texture,
        "color": color,
        "loop": loop,
        "type": wall_type,
        "joint": joint,
        "normalize_uv": True,
        "shadow": shadow,
        "node_id": ids.next(),
        "portals": [],
    }
    level["walls"].append(wall)
    return wall


def add_portal(wall, ids, *, t: float, direction, texture,
                radius=128, rotation=0.0, closed=True, locked=False) -> dict:
    """Aggiunge la porta DENTRO wall['portals'].

    Imposta wall_id = wall['node_id'] e wall_distance = t. NON spezza il
    muro: Dungeondraft buca da solo. `direction`/`rotation` sono presi
    cosi come li passa il chiamante (compose.py): il segno corretto va
    calibrato sul gate umano di M1 (SPEC.md §5), non e responsabilita di
    questa primitiva meccanica.
    """
    if not 0.0 <= t <= 1.0:
        raise ValueError(f"t (wall_distance) deve essere in [0, 1], ricevuto: {t!r}")

    points_px = parse_pv2(wall["points"])
    position = _point_along_polyline(points_px, t)

    portal = {
        "position": v2(*position),
        "rotation": rotation,
        "scale": v2(1, 1),
        "direction": v2(*direction),
        "texture": texture,
        "radius": radius,
        "wall_id": wall["node_id"],
        "wall_distance": t,
        "closed": closed,
        "node_id": ids.next(),
    }
    if locked:
        portal["locked"] = True
    wall["portals"].append(portal)
    return portal


def add_polygon_pattern(level, ids, points_grid, texture, *,
                         layer=-400, color="ffffffff", outline=False) -> dict:
    """Per pavimenti non rettangolari (grotte, isolati irregolari)."""
    points_px = [(grid_to_px(x), grid_to_px(y)) for x, y in points_grid]
    pattern = {
        "position": v2(0, 0),
        "shape_rotation": 0,
        "rotation": 0,
        "scale": v2(1, 1),
        "points": pv2(points_px),
        "layer": layer,
        "color": color,
        "outline": outline,
        "texture": texture,
        "node_id": ids.next(),
    }
    level["patterns"].append(pattern)
    return pattern


def add_pattern(level, ids, rect_grid, texture, *,
                 layer=-400, color="ffffffff", outline=False) -> dict:
    """Pavimento rettangolare. `rect_grid` espone x1, y1, x2, y2 in quadretti."""
    corners = [
        (rect_grid.x1, rect_grid.y1),
        (rect_grid.x2, rect_grid.y1),
        (rect_grid.x2, rect_grid.y2),
        (rect_grid.x1, rect_grid.y2),
    ]
    return add_polygon_pattern(level, ids, corners, texture, layer=layer, color=color, outline=outline)


def add_object(level, ids, x, y, texture, *,
                rotation=0.0, scale=1.0, layer=100,
                shadow=True, block_light=False, mirror=False) -> dict:
    obj = {
        "position": v2(grid_to_px(x), grid_to_px(y)),
        "rotation": rotation,
        "scale": v2(scale, scale),
        "mirror": mirror,
        "texture": texture,
        "layer": layer,
        "shadow": shadow,
        "block_light": block_light,
        "node_id": ids.next(),
    }
    level["objects"].append(obj)
    return obj


def add_path(level, ids, points_grid, texture, *,
             width=472, layer=100, smoothness=1, loop=False) -> dict:
    """ATTENZIONE: edit_points sono RELATIVI a position.

    position = primo punto; edit_points = tutti i punti meno position.
    """
    points_px = [(grid_to_px(x), grid_to_px(y)) for x, y in points_grid]
    origin_x, origin_y = points_px[0]
    relative = [(px - origin_x, py - origin_y) for px, py in points_px]
    path = {
        "position": v2(origin_x, origin_y),
        "rotation": 0,
        "scale": v2(1, 1),
        "edit_points": pv2(relative),
        "smoothness": smoothness,
        "texture": texture,
        "width": width,
        "layer": layer,
        "fade_in": False,
        "fade_out": False,
        "grow": False,
        "shrink": False,
        "block_light": False,
        "loop": loop,
        "node_id": ids.next(),
    }
    level["paths"].append(path)
    return path


def add_roof(level, ids, points_grid, texture, *, width=512, roof_type=0) -> dict:
    """Va in level['roofs']['roofs'], non in una lista di primo livello."""
    points_px = [(grid_to_px(x), grid_to_px(y)) for x, y in points_grid]
    roof = {
        "position": v2(0, 0),
        "rotation": 0,
        "scale": v2(1, 1),
        "points": pv2(points_px),
        "texture": texture,
        "width": width,
        "type": roof_type,
        "node_id": ids.next(),
    }
    level["roofs"]["roofs"].append(roof)
    return roof


def add_light(level, ids, x, y, *,
              light_range=3.0, color="ffffff", intensity=0.7, shadows=True,
              rotation=None, texture=None) -> dict:
    """Variante 'puntiforme' di default (docs/format.md §4, 82 campioni reali):

    niente `rotation`/`texture`, colore a 6 cifre RGB (non passare per
    `godot.argb()`). Passa `rotation`/`texture` esplicitamente solo per la
    variante con sprite (1 solo campione osservato, meno affidabile).
    """
    light = {
        "position": v2(grid_to_px(x), grid_to_px(y)),
        "range": light_range,
        "color": color,
        "intensity": intensity,
        "shadows": shadows,
        "node_id": ids.next(),
    }
    if rotation is not None:
        light["rotation"] = rotation
    if texture is not None:
        light["texture"] = texture
    level["lights"].append(light)
    return light


def add_text(level, ids, x, y, content, *,
             font_name="Libre Baskerville", font_size=32,
             font_color="ff000000", box_shape=0) -> dict:
    """Schema derivato da un solo campione (docs/format.md §4): non aggiungere
    campi ulteriori non osservati."""
    text = {
        "text": content,
        "position": v2(grid_to_px(x), grid_to_px(y)),
        "font_name": font_name,
        "font_size": font_size,
        "font_color": font_color,
        "box_shape": box_shape,
        "node_id": ids.next(),
    }
    level["texts"].append(text)
    return text
