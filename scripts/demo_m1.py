"""Script demo M1 (TASK-11): 1 stanza + 1 porta a partire dal template vuoto.

Chiude il ciclo template -> build -> save prima che esista qualunque
generatore (criterio di completamento di M1, SPEC.md §5).

Uso:
    python scripts/demo_m1.py [--out FILE]
"""

import argparse
from pathlib import Path

from ddforge.build import add_pattern, add_portal, add_wall
from ddforge.ids import IdAllocator
from ddforge.model import Rect
from ddforge.template import finalize, load_template, prepare, save

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map"
DEFAULT_OUT = REPO_ROOT / "generated" / "demo_m1.dungeondraft_map"

FLOOR_TEXTURE = "res://textures/patterns/normal/stone_floor.png"
WALL_TEXTURE = "res://textures/walls/stone.png"
DOOR_TEXTURE = "res://textures/portals/door_00.png"


def build_demo() -> dict:
    """Costruisce il documento demo. Non tocca mai il template sorgente."""
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)

    room = Rect(35, 35, 45, 45)  # 10x10 quadretti, circa al centro di una mappa 80x80
    add_pattern(level, ids, room, FLOOR_TEXTURE)

    corners = [
        (room.x1, room.y1),
        (room.x2, room.y1),
        (room.x2, room.y2),
        (room.x1, room.y2),
    ]
    walls = [
        add_wall(level, ids, [corners[i], corners[(i + 1) % 4]], WALL_TEXTURE)
        for i in range(4)
    ]

    # NOTA PER IL GATE UMANO (TASK-12): direction e rotation sono
    # placeholder. Il verso corretto di portal.direction e il segno delle
    # rotazioni non sono documentati da nessuna parte e vanno calibrati
    # aprendo questo file in Dungeondraft: la porta deve apparire sul muro
    # inferiore della stanza, non fluttuare, e aprirsi verso l'esterno.
    add_portal(
        walls[2],  # muro inferiore (da corners[2] a corners[3])
        ids,
        t=0.5,
        direction=(0, 1),
        rotation=0.0,
        texture=DOOR_TEXTURE,
    )

    finalize(prepared, ids)
    return prepared


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    doc = build_demo()
    save(doc, args.out)
    print(f"Scritto {args.out}")


if __name__ == "__main__":
    main()
