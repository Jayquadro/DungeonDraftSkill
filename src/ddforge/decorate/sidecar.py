"""Sidecar `.ddforge.json` (docs/SPEC-decorate.md §4).

Un `.dungeondraft_map` non porta la semantica del `model.Blueprint` che lo
ha generato (quale stanza e la stanza boss, quali corridoi sono bui,
i ruoli delle stanze di un edificio, strade/piazze/landmark di una
citta...): quella informazione il generatore la butta via dopo il compose.
Il sidecar la conserva accanto alla mappa, cosi `ddforge decorate` (M10)
puo ragionare per zona invece di dover ricostruire le stanze dai muri.

Scritto sempre da `generate`, letto da `decorate`. Non cambia nulla del
file `.dungeondraft_map`.
"""

import hashlib
import json
from pathlib import Path

from ddforge.model import (
    Blueprint, Bridge, Chamber, CityWalls, Corridor, Door, Gate, Landmark,
    Port, Rect, River, Room, Street,
)

SIDECAR_VERSION = 1


def sidecar_path(map_path: str | Path) -> Path:
    """`<nome>.dungeondraft_map` -> `<nome>.ddforge.json`, accanto al file."""
    p = Path(map_path)
    return p.with_name(p.stem + ".ddforge.json")


def hash_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------
# Serializzazione del Blueprint: round-trip esatto (load(dump(bp)) == bp),
# coperto da test per ogni algoritmo. dataclasses.asdict() non basta perche'
# non sa ricostruire tuple/frozenset/chiavi-intero dal JSON (che ha solo
# liste, oggetti e chiavi stringa): ogni tipo del modello ha qui la sua
# coppia esplicita di funzioni to/from.
# --------------------------------------------------------------------------


def _rect_fields(r: Rect) -> dict:
    return {"x1": r.x1, "y1": r.y1, "x2": r.x2, "y2": r.y2}


def _rect_to_json(r: Rect | None) -> dict | None:
    return None if r is None else _rect_fields(r)


def _rect_from_json(d: dict | None) -> Rect | None:
    if d is None:
        return None
    return Rect(d["x1"], d["y1"], d["x2"], d["y2"])


def _require_rect(d: dict) -> Rect:
    rect = _rect_from_json(d)
    assert rect is not None
    return rect


def _corridor_to_json(c: Corridor) -> dict:
    return {**_rect_fields(c), "horizontal": c.horizontal}


def _corridor_from_json(d: dict) -> Corridor:
    return Corridor(d["x1"], d["y1"], d["x2"], d["y2"], horizontal=d["horizontal"])


def _door_to_json(d: Door) -> dict:
    return {"wall_index": d.wall_index, "t": d.t, "kind": d.kind, "locked": d.locked}


def _door_from_json(d: dict) -> Door:
    return Door(wall_index=d["wall_index"], t=d["t"], kind=d["kind"], locked=d["locked"])


def _chamber_to_json(c: Chamber) -> dict:
    return {
        "center": list(c.center),
        "radius": c.radius,
        "connected": sorted(c.connected),
        "door": c.door,
    }


def _chamber_from_json(d: dict) -> Chamber:
    return Chamber(
        center=tuple(d["center"]), radius=d["radius"],
        connected=frozenset(d["connected"]), door=d["door"],
    )


def _street_to_json(s: Street) -> dict:
    return {
        "points": [list(p) for p in s.points],
        "width": s.width,
        "corridor": _rect_to_json(s.corridor),
        "main": s.main,
    }


def _street_from_json(d: dict) -> Street:
    return Street(
        points=[tuple(p) for p in d["points"]], width=d["width"],
        corridor=_rect_from_json(d.get("corridor")), main=d["main"],
    )


def _gate_to_json(g: Gate) -> dict:
    return {"x": g.x, "y": g.y, "side": g.side, "width": g.width}


def _gate_from_json(d: dict) -> Gate:
    return Gate(x=d["x"], y=d["y"], side=d["side"], width=d["width"])


def _city_walls_to_json(w: CityWalls) -> dict:
    return {
        "ring": _rect_to_json(w.ring),
        "thickness": w.thickness,
        "gates": [_gate_to_json(g) for g in w.gates],
    }


def _city_walls_from_json(d: dict) -> CityWalls:
    return CityWalls(
        ring=_require_rect(d["ring"]), thickness=d["thickness"],
        gates=[_gate_from_json(g) for g in d.get("gates", [])],
    )


def _river_to_json(r: River) -> dict:
    return {"points": [list(p) for p in r.points], "width": r.width}


def _river_from_json(d: dict) -> River:
    return River(points=[tuple(p) for p in d["points"]], width=d["width"])


def _bridge_to_json(b: Bridge) -> dict:
    return {"rect": _rect_to_json(b.rect), "horizontal": b.horizontal}


def _bridge_from_json(d: dict) -> Bridge:
    return Bridge(rect=_require_rect(d["rect"]), horizontal=d["horizontal"])


def _port_to_json(p: Port) -> dict:
    return {"water": _rect_to_json(p.water), "quay": _rect_to_json(p.quay), "side": p.side}


def _port_from_json(d: dict) -> Port:
    return Port(water=_require_rect(d["water"]), quay=_require_rect(d["quay"]), side=d["side"])


def _landmark_to_json(l: Landmark) -> dict:
    return {
        "kind": l.kind,
        "label": l.label,
        "rect": _rect_to_json(l.rect),
        "site": l.site,
        "open_air": l.open_air,
        "piece_size": l.piece_size,
        "layout": l.layout,
        "ground": l.ground,
        "building": serialize_blueprint(l.building) if l.building is not None else None,
    }


def _landmark_from_json(d: dict) -> Landmark:
    return Landmark(
        kind=d["kind"], label=d["label"], rect=_require_rect(d["rect"]), site=d["site"],
        open_air=d["open_air"], piece_size=d["piece_size"], layout=d["layout"],
        ground=d.get("ground"),
        building=deserialize_blueprint(d["building"]) if d.get("building") is not None else None,
    )


def _room_to_json(r: Room) -> dict:
    return {
        "rect": _rect_to_json(r.rect),
        "kind": r.kind,
        "name": r.name,
        "doors": [_door_to_json(d) for d in r.doors],
        "floor": r.floor,
        "lights": [list(p) for p in r.lights],
        "level": r.level,
    }


def _room_from_json(d: dict) -> Room:
    return Room(
        rect=_require_rect(d["rect"]), kind=d["kind"], name=d.get("name", ""),
        doors=[_door_from_json(x) for x in d.get("doors", [])],
        floor=d.get("floor"), lights=[tuple(p) for p in d.get("lights", [])],
        level=d.get("level", 0),
    )


def serialize_blueprint(bp: Blueprint) -> dict:
    """Blueprint -> dict JSON-serializzabile, ricorsiva su `buildings` e
    `landmarks[].building` (docs/SPEC-decorate.md §4.1)."""
    return {
        "width": bp.width,
        "height": bp.height,
        "rooms": [_room_to_json(r) for r in bp.rooms],
        "corridors": [_corridor_to_json(c) for c in bp.corridors],
        "graph": {str(k): v for k, v in bp.graph.items()},
        "seed": bp.seed,
        "style": bp.style,
        "levels": bp.levels,
        "tactical_rooms": bp.tactical_rooms,
        "long_corridor_indices": bp.long_corridor_indices,
        "stairs_rect": _rect_to_json(bp.stairs_rect),
        "cave_grid": bp.cave_grid,
        "chambers": [_chamber_to_json(c) for c in bp.chambers],
        "scale": bp.scale,
        "streets": [_street_to_json(s) for s in bp.streets],
        "plazas": [_rect_to_json(p) for p in bp.plazas],
        "buildings": [serialize_blueprint(b) for b in bp.buildings],
        "building_footprints": [_rect_to_json(r) for r in bp.building_footprints],
        "landmarks": [_landmark_to_json(l) for l in bp.landmarks],
        "walls": _city_walls_to_json(bp.walls) if bp.walls is not None else None,
        "river": _river_to_json(bp.river) if bp.river is not None else None,
        "bridges": [_bridge_to_json(b) for b in bp.bridges],
        "port": _port_to_json(bp.port) if bp.port is not None else None,
    }


def deserialize_blueprint(d: dict) -> Blueprint:
    """Inverso esatto di `serialize_blueprint`."""
    return Blueprint(
        width=d["width"],
        height=d["height"],
        rooms=[_room_from_json(r) for r in d["rooms"]],
        corridors=[_corridor_from_json(c) for c in d["corridors"]],
        graph={int(k): v for k, v in d["graph"].items()},
        seed=d["seed"],
        style=d["style"],
        levels=d.get("levels", 1),
        tactical_rooms=d.get("tactical_rooms", []),
        long_corridor_indices=d.get("long_corridor_indices", []),
        stairs_rect=_rect_from_json(d.get("stairs_rect")),
        cave_grid=d.get("cave_grid"),
        chambers=[_chamber_from_json(c) for c in d.get("chambers", [])],
        scale=d.get("scale", ""),
        streets=[_street_from_json(s) for s in d.get("streets", [])],
        plazas=[_require_rect(p) for p in d.get("plazas", [])],
        buildings=[deserialize_blueprint(b) for b in d.get("buildings", [])],
        building_footprints=[_require_rect(r) for r in d.get("building_footprints", [])],
        landmarks=[_landmark_from_json(l) for l in d.get("landmarks", [])],
        walls=_city_walls_from_json(d["walls"]) if d.get("walls") is not None else None,
        river=_river_from_json(d["river"]) if d.get("river") is not None else None,
        bridges=[_bridge_from_json(b) for b in d.get("bridges", [])],
        port=_port_from_json(d["port"]) if d.get("port") is not None else None,
    )


# --------------------------------------------------------------------------
# Il sidecar completo
# --------------------------------------------------------------------------


def build_sidecar(
    *, algorithm: str, args: dict, template: str,
    catalog_path: str | Path, map_bytes: bytes, blueprint: Blueprint,
) -> dict:
    """Costruisce il dict del sidecar (docs/SPEC-decorate.md §4.1).

    `map_bytes` sono i byte esatti scritti sul file mappa: l'hash deve
    corrispondere a quello scritto, non a una ricostruzione (AC4)."""
    return {
        "ddforge_sidecar": SIDECAR_VERSION,
        "generator": {"algorithm": algorithm, "args": dict(args)},
        "template": str(template),
        "catalog_sha256": hash_file(catalog_path),
        "map_sha256": hash_bytes(map_bytes),
        "blueprint": serialize_blueprint(blueprint),
        "decorations": [],
    }


def write_sidecar(map_path: str | Path, sidecar: dict) -> Path:
    """Scrive `<nome>.ddforge.json` accanto a `map_path`. Ritorna il percorso."""
    path = sidecar_path(map_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def load_sidecar(map_path: str | Path) -> dict:
    """Legge il sidecar di `map_path`. Alza `FileNotFoundError` se assente."""
    path = sidecar_path(map_path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)
