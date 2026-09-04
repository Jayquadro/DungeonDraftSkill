"""Validatore pre-consegna: trasforma il progetto da speranza a ingegneria.

Codici DDF001-DDF015 (error) e DDF101-DDF105 (warning).
Vedi docs/SPEC.md §7 e docs/format.md per gli scostamenti scoperti sui
template reali (build 1.2.0.1): §6 (portal libero, non validato da
DDF012/013), §4 (color a 6 cifre per le luci).
"""

import math
import re
from dataclasses import dataclass

from ddforge.godot import parse_pv2
from ddforge.template import DRAWABLE_LISTS, LEVEL_KEYS

_VECTOR2_RE = re.compile(r"^Vector2\(\s*[^,()]+,\s*[^,()]+\s*\)$")
_HEX8_RE = re.compile(r"^[0-9a-fA-F]{8}$")
_HEX6_RE = re.compile(r"^[0-9a-fA-F]{6}$")


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    code: str  # es. "DDF001"
    message: str
    path: str  # es. "world.levels.0.walls[3]"


def _add(issues: list[Issue], severity: str, code: str, message: str, path: str) -> None:
    issues.append(Issue(severity, code, message, path))


def _pool_array_length(s: str) -> int:
    """Numero di elementi in una stringa PoolIntArray/PoolByteArray(...).

    Non e compito di godot.py (che gestisce solo PoolVector2Array): qui
    serve solo il conteggio per DDF010/011. Solleva ValueError se malformata.
    """
    start = s.find("(")
    end = s.rfind(")")
    if start == -1 or end == -1 or end < start:
        raise ValueError("parentesi '(' ')' mancanti o invertite")
    inner = s[start + 1 : end].strip()
    return 0 if not inner else len(inner.split(","))


# ---------------------------------------------------------------------------
# Check di campo, riusati su piu tipi di elemento
# ---------------------------------------------------------------------------

def _check_vector2(value, path: str, issues: list[Issue]) -> None:
    if not isinstance(value, str) or not _VECTOR2_RE.match(value):
        _add(issues, "error", "DDF008", f"Atteso 'Vector2( x, y )', trovato: {value!r}", path)


def _check_pool_vector2(value, path: str, issues: list[Issue]) -> None:
    if not isinstance(value, str):
        _add(issues, "error", "DDF007", f"Atteso una stringa PoolVector2Array, trovato: {type(value).__name__}", path)
        return
    try:
        parse_pv2(value)
    except ValueError as exc:
        _add(issues, "error", "DDF007", f"PoolVector2Array non valida: {exc}", path)


def _check_argb_color(value, path: str, issues: list[Issue]) -> None:
    if not isinstance(value, str) or not _HEX8_RE.match(value):
        _add(issues, "error", "DDF009", f"Atteso un colore a 8 cifre esadecimali ARGB, trovato: {value!r}", path)


def _check_rgb6_color(value, path: str, issues: list[Issue]) -> None:
    """Le luci osservate (docs/format.md §4) usano 6 cifre RGB, non ARGB."""
    if not isinstance(value, str) or not _HEX6_RE.match(value):
        _add(
            issues, "error", "DDF009",
            f"Atteso un colore a 6 cifre esadecimali RGB per le luci, trovato: {value!r}",
            path,
        )


def _check_finite_rotation(value, path: str, issues: list[Issue]) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _add(issues, "error", "DDF015", f"'rotation' deve essere un numero, trovato: {value!r}", path)
        return
    if not math.isfinite(value):
        _add(issues, "error", "DDF015", f"'rotation' non e un numero finito: {value!r}", path)


def _check_pack_reference(texture: str, known_pack_ids: set, path: str, issues: list[Issue]) -> None:
    if not texture.startswith("res://packs/"):
        return
    parts = texture.split("/")
    if len(parts) < 4:
        _add(issues, "error", "DDF014", f"Path pack malformato: {texture!r}", path)
        return
    pack_id = parts[3]
    if pack_id not in known_pack_ids:
        _add(
            issues, "error", "DDF014",
            f"Pack {pack_id!r} referenziato dalla texture ma assente da header.asset_manifest: {texture}",
            path,
        )


def _check_generic_element(el, path: str, issues: list[Issue], known_pack_ids: set) -> None:
    """Controlla i campi comuni (position/scale/direction, points, colori, rotation, texture)."""
    if not isinstance(el, dict):
        _add(issues, "error", "DDF004", "L'elemento non e un oggetto", path)
        return
    for key in ("position", "scale", "direction"):
        if key in el:
            _check_vector2(el[key], f"{path}.{key}", issues)
    if "points" in el:
        _check_pool_vector2(el["points"], f"{path}.points", issues)
    if "edit_points" in el:
        _check_pool_vector2(el["edit_points"], f"{path}.edit_points", issues)
    for key in ("color", "font_color"):
        if key in el:
            _check_argb_color(el[key], f"{path}.{key}", issues)
    if "rotation" in el:
        _check_finite_rotation(el["rotation"], f"{path}.rotation", issues)
    if "texture" in el and isinstance(el["texture"], str):
        _check_pack_reference(el["texture"], known_pack_ids, f"{path}.texture", issues)


def _check_light_element(el, path: str, issues: list[Issue], known_pack_ids: set) -> None:
    """Due varianti osservate (docs/format.md §4): 'puntiforme' (6 cifre RGB,
    82 campioni reali, niente rotation/texture) e 'con sprite' (8 cifre
    ARGB, rotation+texture, 1 solo campione). Distinta per presenza di
    texture, il segnale piu affidabile fra i due osservati."""
    if not isinstance(el, dict):
        _add(issues, "error", "DDF004", "L'elemento non e un oggetto", path)
        return
    if "position" in el:
        _check_vector2(el["position"], f"{path}.position", issues)
    if "rotation" in el:
        _check_finite_rotation(el["rotation"], f"{path}.rotation", issues)
    if "color" in el:
        if "texture" in el:
            _check_argb_color(el["color"], f"{path}.color", issues)
        else:
            _check_rgb6_color(el["color"], f"{path}.color", issues)
    if "texture" in el and isinstance(el["texture"], str):
        _check_pack_reference(el["texture"], known_pack_ids, f"{path}.texture", issues)


# ---------------------------------------------------------------------------
# DDF001-004: struttura del documento
# ---------------------------------------------------------------------------

def _check_ddf001(doc: dict, issues: list[Issue]) -> None:
    header = doc.get("header")
    if not isinstance(header, dict):
        _add(issues, "error", "DDF001", "Manca 'header' o non e un oggetto", "header")
    world = doc.get("world")
    if not isinstance(world, dict):
        _add(issues, "error", "DDF001", "Manca 'world' o non e un oggetto", "world")
        return
    fmt = world.get("format")
    if isinstance(fmt, bool) or not isinstance(fmt, int):
        _add(issues, "error", "DDF001", f"'world.format' deve essere un intero, trovato: {fmt!r}", "world.format")


def _check_ddf002(doc: dict, issues: list[Issue]) -> None:
    world = doc.get("world")
    if not isinstance(world, dict):
        return
    for key in ("width", "height", "next_node_id", "msi", "grid", "embedded"):
        if key not in world:
            _add(issues, "error", "DDF002", f"Manca 'world.{key}'", f"world.{key}")


def _check_ddf003(level, base_path: str, issues: list[Issue]) -> None:
    if not isinstance(level, dict):
        _add(issues, "error", "DDF003", "Il livello non e un oggetto", base_path)
        return
    actual = set(level.keys())
    expected = set(LEVEL_KEYS)
    missing = expected - actual
    extra = actual - expected
    if missing:
        _add(issues, "error", "DDF003", f"Chiavi mancanti nel livello: {sorted(missing)}", base_path)
    if extra:
        _add(issues, "error", "DDF003", f"Chiavi impreviste nel livello: {sorted(extra)}", base_path)


def _check_ddf004(level: dict, base_path: str, issues: list[Issue]) -> None:
    roofs = level.get("roofs")
    if not isinstance(roofs, dict) or not isinstance(roofs.get("roofs"), list):
        _add(issues, "error", "DDF004", "'roofs' deve essere un oggetto con chiave 'roofs' di tipo lista", f"{base_path}.roofs")
    if "shapes" in level and not isinstance(level["shapes"], dict):
        _add(issues, "error", "DDF004", "'shapes' deve essere un oggetto", f"{base_path}.shapes")
    if "materials" in level and not isinstance(level["materials"], dict):
        _add(issues, "error", "DDF004", "'materials' deve essere un oggetto", f"{base_path}.materials")
    for key in DRAWABLE_LISTS:
        if key in level and not isinstance(level[key], list):
            _add(issues, "error", "DDF004", f"'{key}' deve essere una lista", f"{base_path}.{key}")


# ---------------------------------------------------------------------------
# DDF005-006: node_id
# ---------------------------------------------------------------------------

def _collect_node_ids(value, path: str):
    if isinstance(value, dict):
        for key, v in value.items():
            if key == "node_id":
                yield path, v
            else:
                yield from _collect_node_ids(v, f"{path}.{key}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _collect_node_ids(v, f"{path}[{i}]")


def _check_node_ids(doc: dict, issues: list[Issue]) -> None:
    world = doc.get("world")
    if not isinstance(world, dict):
        return

    seen: dict[str, str] = {}
    max_id = None
    for path, node_id in _collect_node_ids(world, "world"):
        if not isinstance(node_id, str):
            _add(issues, "error", "DDF005", f"node_id non e una stringa: {node_id!r}", path)
            continue
        if node_id in seen:
            _add(issues, "error", "DDF005", f"node_id duplicato: {node_id!r} (gia usato in {seen[node_id]})", path)
        else:
            seen[node_id] = path
        try:
            value = int(node_id, 16)
        except ValueError:
            _add(issues, "error", "DDF005", f"node_id non esadecimale: {node_id!r}", path)
            continue
        max_id = value if max_id is None else max(max_id, value)

    if max_id is None:
        return
    next_node_id = world.get("next_node_id")
    try:
        next_value = int(next_node_id, 16)
    except (TypeError, ValueError):
        _add(issues, "error", "DDF006", f"world.next_node_id non e esadecimale valido: {next_node_id!r}", "world.next_node_id")
        return
    if next_value <= max_id:
        _add(
            issues, "error", "DDF006",
            f"world.next_node_id ({next_node_id!r}) deve essere maggiore del massimo node_id usato ({format(max_id, 'x')!r})",
            "world.next_node_id",
        )


# ---------------------------------------------------------------------------
# DDF010-011: lunghezza dei blob binari
# ---------------------------------------------------------------------------

def _check_blob_lengths(level: dict, width: int, height: int, base_path: str, issues: list[Issue]) -> None:
    tiles = level.get("tiles")
    if isinstance(tiles, dict) and isinstance(tiles.get("cells"), str):
        path = f"{base_path}.tiles.cells"
        try:
            n = _pool_array_length(tiles["cells"])
        except ValueError as exc:
            _add(issues, "error", "DDF010", f"tiles.cells illeggibile: {exc}", path)
        else:
            expected = width * height
            if n != expected:
                _add(issues, "error", "DDF010", f"tiles.cells ha {n} elementi, attesi {expected} (width*height)", path)

    terrain = level.get("terrain")
    if isinstance(terrain, dict) and isinstance(terrain.get("splat"), str):
        path = f"{base_path}.terrain.splat"
        try:
            n = _pool_array_length(terrain["splat"])
        except ValueError as exc:
            _add(issues, "error", "DDF011", f"terrain.splat illeggibile: {exc}", path)
        else:
            expected = width * height * 64
            if n != expected:
                _add(issues, "error", "DDF011", f"terrain.splat ha {n} elementi, attesi {expected} (width*height*64)", path)


# ---------------------------------------------------------------------------
# DDF012-013: coerenza delle porte annidate nei muri
# ---------------------------------------------------------------------------

def _check_nested_portals_coherence(walls: list, base_path: str, issues: list[Issue]) -> None:
    """Solo per le porte annidate in wall.portals: lo schema libero di
    level.portals (docs/format.md §6) non ha wall_id/wall_distance e non
    va controllato da queste regole."""
    wall_ids = {w.get("node_id") for w in walls if isinstance(w, dict)}
    for wi, wall in enumerate(walls):
        if not isinstance(wall, dict):
            continue
        portals = wall.get("portals")
        if not isinstance(portals, list):
            continue
        for pi, portal in enumerate(portals):
            if not isinstance(portal, dict):
                continue
            ppath = f"{base_path}.walls[{wi}].portals[{pi}]"
            wall_id = portal.get("wall_id")
            if wall_id not in wall_ids:
                _add(issues, "error", "DDF012", f"portal.wall_id {wall_id!r} non corrisponde a nessun muro del livello", f"{ppath}.wall_id")
            wd = portal.get("wall_distance")
            if isinstance(wd, bool) or not isinstance(wd, (int, float)) or not (0.0 <= wd <= 1.0):
                _add(issues, "error", "DDF013", f"portal.wall_distance deve essere in [0, 1], trovato: {wd!r}", f"{ppath}.wall_distance")


# ---------------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------------

def _validate_level(level, level_id, world, known_pack_ids, issues: list[Issue]) -> None:
    base = f"world.levels.{level_id}"
    _check_ddf003(level, base, issues)
    if not isinstance(level, dict):
        return
    _check_ddf004(level, base, issues)

    width, height = world.get("width"), world.get("height")
    if (
        isinstance(width, int) and not isinstance(width, bool)
        and isinstance(height, int) and not isinstance(height, bool)
    ):
        _check_blob_lengths(level, width, height, base, issues)

    for list_name in ("patterns", "objects", "texts", "paths", "portals"):
        items = level.get(list_name)
        if isinstance(items, list):
            for i, el in enumerate(items):
                _check_generic_element(el, f"{base}.{list_name}[{i}]", issues, known_pack_ids)

    lights = level.get("lights")
    if isinstance(lights, list):
        for i, el in enumerate(lights):
            _check_light_element(el, f"{base}.lights[{i}]", issues, known_pack_ids)

    walls = level.get("walls")
    if isinstance(walls, list):
        for wi, wall in enumerate(walls):
            wpath = f"{base}.walls[{wi}]"
            _check_generic_element(wall, wpath, issues, known_pack_ids)
            if not isinstance(wall, dict):
                continue
            nested_portals = wall.get("portals")
            if isinstance(nested_portals, list):
                for pi, portal in enumerate(nested_portals):
                    _check_generic_element(portal, f"{wpath}.portals[{pi}]", issues, known_pack_ids)
        _check_nested_portals_coherence(walls, base, issues)

    roofs = level.get("roofs")
    if isinstance(roofs, dict) and isinstance(roofs.get("roofs"), list):
        for i, roof in enumerate(roofs["roofs"]):
            _check_generic_element(roof, f"{base}.roofs.roofs[{i}]", issues, known_pack_ids)


def validate(doc: dict) -> list[Issue]:
    """Valida un documento .dungeondraft_map. Non solleva mai eccezioni."""
    issues: list[Issue] = []
    try:
        if not isinstance(doc, dict):
            _add(issues, "error", "DDF001", "Il documento non e un oggetto JSON", "")
            return issues

        _check_ddf001(doc, issues)
        _check_ddf002(doc, issues)
        _check_node_ids(doc, issues)

        world = doc.get("world")
        if not isinstance(world, dict):
            return issues

        known_pack_ids = set()
        header = doc.get("header")
        if isinstance(header, dict):
            for m in header.get("asset_manifest", []) or []:
                if isinstance(m, dict) and "id" in m:
                    known_pack_ids.add(m["id"])

        levels = world.get("levels")
        if not isinstance(levels, dict):
            return issues

        for level_id, level in levels.items():
            _validate_level(level, level_id, world, known_pack_ids, issues)

        return issues
    except Exception as exc:  # pragma: no cover - rete di sicurezza per AC6
        _add(issues, "error", "DDF000", f"Errore interno del validatore: {exc}", "")
        return issues
