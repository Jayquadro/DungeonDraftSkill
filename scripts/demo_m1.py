"""Script demo M1 (TASK-11): 1 stanza + 1 porta a partire dal template vuoto.

Chiude il ciclo template -> build -> save prima che esista qualunque
generatore (criterio di completamento di M1, SPEC.md §5). Da TASK-18
in poi usa compose.draw_room, la stessa funzione che useranno i
generatori veri.

Uso:
    python scripts/demo_m1.py [--out FILE]
"""

import argparse
from pathlib import Path

from ddforge.assets import Palette
from ddforge.compose import draw_room
from ddforge.ids import IdAllocator
from ddforge.model import Door, Rect, Room
from ddforge.template import finalize, load_template, prepare, save

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map"
DEFAULT_OUT = REPO_ROOT / "generated" / "demo_m1.dungeondraft_map"

DEMO_PALETTE = Palette(
    wall="res://textures/walls/stone.png",
    floor="res://textures/patterns/normal/stone_floor.png",
    door="res://textures/portals/door_00.png",
)


def build_demo() -> dict:
    """Costruisce il documento demo. Non tocca mai il template sorgente."""
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)

    # 10x10 quadretti, circa al centro di una mappa 80x80. La porta e sul
    # muro inferiore (wall_index=2: da (x2,y2) a (x1,y2)).
    room = Room(
        rect=Rect(35, 35, 45, 45),
        kind="sala",
        doors=[Door(wall_index=2, t=0.5)],
    )

    # NOTA PER IL GATE UMANO (TASK-12): compose.draw_room deriva
    # direction/rotation dalla normale uscente del muro e dalla formula
    # rotation = atan2(direction.y, direction.x), evidence-based su 3
    # campioni reali (docs/format.md §5). Resta da confermare aprendo
    # questo file in Dungeondraft che la porta appaia sul muro inferiore
    # della stanza, non fluttui, e si apra verso l'esterno.
    draw_room(level, ids, room, DEMO_PALETTE)

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
