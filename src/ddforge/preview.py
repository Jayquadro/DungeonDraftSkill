"""Renderer PNG di anteprima (M6, TASK-37, SPEC.md §1.3/§5/§8).

Legge il documento .dungeondraft_map GIA SCRITTO SU DISCO, non il Blueprint
in memoria: cosi l'anteprima verifica davvero cio che Dungeondraft aprirebbe,
non cio che il generatore intendeva scrivere. Nessuna dipendenza da model.py
o compose.py per questo motivo: solo i campi del JSON (points/position/
texture), esattamente come li leggerebbe validate.py.

Pillow e l'unica dipendenza esterna ammessa nel progetto (SPEC.md §1.3) e
resta opzionale: importata pigramente qui, mai a livello di modulo, cosi il
core e gli altri comandi funzionano senza (AC4)."""

from __future__ import annotations

import re
from pathlib import Path

from ddforge.godot import GRID, parse_pv2

_VECTOR2_RE = re.compile(r"^Vector2\(\s*([^,()]+),\s*([^,()]+)\s*\)$")

_DEFAULT_SCALE = 8  # pixel per quadretto nel PNG (indipendente dal GRID di Dungeondraft)

_BACKGROUND = (32, 30, 28)
_FLOOR = (214, 189, 152)
_WALL = (18, 16, 15)
_DOOR = (176, 100, 40)
_OBJECT = (64, 132, 130)


class PillowMissingError(RuntimeError):
    """Pillow non e installato (AC5): messaggio chiaro invece di un traceback."""


def _require_pillow():
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise PillowMissingError(
            "Il comando 'preview' richiede Pillow, non installato in questo "
            "ambiente. Installa con: pip install ddforge[preview]"
        ) from exc
    return Image, ImageDraw


def _px(quadretti: float, scale: int) -> float:
    return quadretti * scale


def _parse_position(value, scale: int) -> tuple[float, float] | None:
    if not isinstance(value, str):
        return None
    match = _VECTOR2_RE.match(value)
    if not match:
        return None
    try:
        x, y = float(match.group(1)), float(match.group(2))
    except ValueError:
        return None
    return (_px(x / GRID, scale), _px(y / GRID, scale))


def _points_px(points: str | None, scale: int) -> list[tuple[float, float]] | None:
    if not isinstance(points, str):
        return None
    try:
        pts = parse_pv2(points)
    except ValueError:
        return None
    return [(_px(x / GRID, scale), _px(y / GRID, scale)) for x, y in pts]


def _draw_cave_bitmap(draw, level: dict, width: int, height: int, scale: int) -> None:
    """Layer cave nativo (decision-1): unica fonte di geometria per una
    grotta (generators/cave.py), che non produce walls/patterns."""
    cave = level.get("cave")
    blob = cave.get("bitmap") if isinstance(cave, dict) else None
    if not isinstance(blob, str):
        return

    from ddforge.cave_bitmap import cave_grid_shape, decode_cave_bitmap

    try:
        grid = decode_cave_bitmap(blob, width, height)
    except (ValueError, IndexError):
        return
    grid_w, grid_h = cave_grid_shape(width, height)
    sub_px = scale / 4  # 4 sotto-celle per quadretto; sotto-cella 0 = quadretto 0 (docs/format.md §14)

    for y in range(min(grid_h, len(grid))):
        row = grid[y]
        y0, y1 = y * sub_px, (y + 1) * sub_px
        run_start = None
        for x in range(grid_w + 1):
            dug = x < grid_w and x < len(row) and row[x]
            if dug and run_start is None:
                run_start = x
            elif not dug and run_start is not None:
                draw.rectangle([run_start * sub_px, y0, x * sub_px, y1], fill=_FLOOR)
                run_start = None


def _draw_patterns(draw, level: dict, scale: int) -> None:
    for pattern in level.get("patterns") or []:
        if not isinstance(pattern, dict):
            continue
        poly = _points_px(pattern.get("points"), scale)
        if poly and len(poly) >= 3:
            draw.polygon(poly, fill=_FLOOR)


def _draw_walls_and_doors(draw, level: dict, scale: int) -> None:
    line_width = max(2, round(scale / 4))
    door_radius = max(2.0, scale * 0.35)

    for wall in level.get("walls") or []:
        if not isinstance(wall, dict):
            continue
        pts = _points_px(wall.get("points"), scale)
        if pts and len(pts) >= 2:
            if wall.get("loop") and pts[0] != pts[-1]:
                pts = [*pts, pts[0]]
            draw.line(pts, fill=_WALL, width=line_width, joint="curve")

        for portal in wall.get("portals") or []:
            if not isinstance(portal, dict):
                continue
            pos = _parse_position(portal.get("position"), scale)
            if pos is None:
                continue
            x, y = pos
            draw.ellipse(
                [x - door_radius, y - door_radius, x + door_radius, y + door_radius],
                fill=_DOOR,
            )


def _draw_objects(draw, level: dict, scale: int) -> None:
    half = max(1.5, scale * 0.3)
    for obj in level.get("objects") or []:
        if not isinstance(obj, dict):
            continue
        pos = _parse_position(obj.get("position"), scale)
        if pos is None:
            continue
        x, y = pos
        draw.rectangle([x - half, y - half, x + half, y + half], fill=_OBJECT, outline=_WALL)


def _pick_level_id(levels: dict) -> str:
    def sort_key(key: str):
        try:
            return (0, int(key))
        except ValueError:
            return (1, key)

    return sorted(levels, key=sort_key)[0]


def render_preview(doc: dict, out_path, *, level_id: str | None = None, scale: int = _DEFAULT_SCALE) -> None:
    """Renderizza un livello di `doc` in un PNG a `out_path` (AC1/AC2).

    `doc` e il documento .dungeondraft_map gia caricato da JSON (AC3): questa
    funzione non genera geometria, disegna solo cio che trova nel documento.
    Solleva PillowMissingError se Pillow non e installato, ValueError se il
    documento non ha la forma minima necessaria (world/livelli/dimensioni).
    """
    Image, ImageDraw = _require_pillow()

    world = doc.get("world")
    if not isinstance(world, dict):
        raise ValueError("il documento non ha una chiave 'world' valida")

    width, height = world.get("width"), world.get("height")
    if isinstance(width, bool) or isinstance(height, bool) or not isinstance(width, int) or not isinstance(height, int):
        raise ValueError(f"world.width/world.height mancanti o non interi: {width!r}, {height!r}")
    if width <= 0 or height <= 0:
        raise ValueError(f"world.width/world.height devono essere positivi: {width!r}, {height!r}")

    levels = world.get("levels")
    if not isinstance(levels, dict) or not levels:
        raise ValueError("world.levels mancante o vuoto")

    if level_id is None:
        level_id = _pick_level_id(levels)
    if level_id not in levels:
        raise ValueError(f"livello {level_id!r} non trovato (disponibili: {sorted(levels)})")

    level = levels[level_id]
    if not isinstance(level, dict):
        raise ValueError(f"il livello {level_id!r} non e un oggetto valido")

    if scale <= 0:
        raise ValueError(f"scale deve essere positivo, ricevuto: {scale!r}")

    img = Image.new("RGB", (max(1, round(width * scale)), max(1, round(height * scale))), _BACKGROUND)
    draw = ImageDraw.Draw(img)

    _draw_cave_bitmap(draw, level, width, height, scale)
    _draw_patterns(draw, level, scale)
    _draw_walls_and_doors(draw, level, scale)
    _draw_objects(draw, level, scale)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")
