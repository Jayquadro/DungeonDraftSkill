"""Spike di misurazione per TASK-34 (SPEC.md §9.4, decisione sulla scala).

Non e' il generatore city.py (TASK-35): qui l'obiettivo e produrre un caso
reale, apribile in Dungeondraft, del regime "citta" (1 quadretto = 1
edificio, abstratto a una sola pattern di ingombro) per misurarne il peso
reale contro il regime "quartiere" (edifici a piena risoluzione, gia
prodotti da building.py in generated/building_m4_*.dungeondraft_map).

Uso:
    python scripts/city_scale_spike.py [--step N] [--out FILE]

--step controlla il passo della griglia isolati/strade in quadretti (una
riga/colonna di strada ogni N edifici); non e' un parametro di qualita
urbanistica, solo un modo di variare la densita per la misura.
"""

import argparse
from pathlib import Path

from ddforge.assets import load_catalog, palette_for
from ddforge.build import add_pattern
from ddforge.ids import IdAllocator
from ddforge.model import Rect
from ddforge.template import finalize, load_template, prepare, save

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map"
DEFAULT_OUT = REPO_ROOT / "generated" / "city_scale_spike.dungeondraft_map"

MARGIN = 2  # quadretti di bordo non edificato, come gli altri generatori


def build_city_scale(step: int = 7) -> tuple[dict, int]:
    """Griglia di edifici astratti a 1 quadretto/edificio, con una via di
    rispetto di 1 quadretto ogni `step` edifici (isolati di step-1 lati).
    Restituisce (documento, numero di edifici piazzati)."""
    doc = load_template(TEMPLATE)
    catalog = load_catalog()
    palette = palette_for("city", catalog)

    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)

    world_w = prepared["world"]["width"]
    world_h = prepared["world"]["height"]

    count = 0
    for x in range(MARGIN, world_w - MARGIN):
        if x % step == 0:
            continue  # strada verticale
        for y in range(MARGIN, world_h - MARGIN):
            if y % step == 0:
                continue  # strada orizzontale
            add_pattern(level, ids, Rect(x, y, x + 1, y + 1), palette.wall, color="ff8a7a63")
            count += 1

    finalize(prepared, ids)
    return prepared, count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", type=int, default=7)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    doc, count = build_city_scale(step=args.step)
    save(doc, args.out)
    print(f"Scritto {args.out} ({count} edifici astratti)")


if __name__ == "__main__":
    main()
