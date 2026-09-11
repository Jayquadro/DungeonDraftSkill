"""Foglio di calibrazione per le etichette dei luoghi e per le aree colorate
(TASK-48).

Serve a rispondere a tre domande a cui il codice, da solo, non puo' rispondere,
perche' riguardano come DUNGEONDRAFT rende quello che scriviamo nel file. Su
`text` il progetto ha un solo campione osservato in tutto (docs/format.md §4),
e finora le risposte le ho DEDOTTE: la deduzione si e' rivelata sbagliata e le
etichette sono uscite fuori misura e sovrapposte. Questo foglio le misura
invece di indovinarle.

    python scripts/label_calibration.py --out generated/calibrazione.dungeondraft_map

Poi il file va APERTO IN DUNGEONDRAFT e guardato. Le tre domande:

1. QUANTO E' GRANDE UN CORPO DI FONT. Ogni riga scrive lo stesso nome a un
   corpo diverso, ancorato al centro di un quadrato ROSA di esattamente 1x1
   quadretto. Guardando la mappa a schermo intero: quale riga si legge senza
   ingrandire e senza coprire mezza citta'? Quello e' il corpo giusto per un
   luogo largo un quadretto.

2. DOVE STA `position`. Il quadrato rosa e' il punto che abbiamo passato a
   Dungeondraft. Il testo ci esce centrato sopra, oppure parte da li' verso
   destra, oppure sta sotto? E' l'ancoraggio, e non lo sappiamo.

3. QUANTO E' LARGO UN TESTO. Sotto ogni riga corre un righello di quadretti
   alternati chiaro/scuro, numerati ogni cinque. Quanti quadretti occupa il
   nome? Da li' si ricava la larghezza media di un carattere, che e' il numero
   con cui si evita che due etichette si sovrappongano.

In fondo al foglio ci sono le AREE COLORATE: una toppa per ogni texture di
terreno candidata, col suo nome accanto. Serve a vedere quali rende davvero
Dungeondraft - in particolare se accetta le texture di categoria `terrain`
(erba e terra battuta) dentro un elemento `pattern`, che e' l'unica cosa non
verificata delle aree di parchi e cimiteri.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ddforge.assets import load_catalog, palette_for  # noqa: E402
from ddforge.build import add_pattern, add_text  # noqa: E402
from ddforge.ids import IdAllocator  # noqa: E402
from ddforge.model import Rect  # noqa: E402
from ddforge.template import finalize, load_template, save  # noqa: E402
from ddforge.template import prepare  # noqa: E402
from ddforge.validate import validate  # noqa: E402

# I corpi da provare. 32 e' l'unico valore mai osservato in un file scritto da
# Dungeondraft (docs/format.md §4); gli altri raddoppiano attorno a lui in
# entrambe le direzioni, cosi' la risposta cade dentro l'intervallo qualunque
# sia l'ordine di grandezza giusto.
FONT_SIZES = (16, 24, 32, 48, 64, 96, 128, 192, 256, 384)

ROW_HEIGHT = 5.0  # quadretti fra una riga e la successiva
ANCHOR_X = 2.0  # colonna del quadrato rosa
RULER_LEN = 40  # quadretti di righello
_PINK = "ffff66cc"


def _ruler(level, ids, palette, x0: float, y: float, length: int) -> None:
    """Righello di quadretti alternati, per contare quanto e' largo un testo."""
    light = palette.floors["piazza"]
    dark = palette.floor
    for i in range(length):
        texture = light if i % 2 == 0 else dark
        add_pattern(level, ids, Rect(x0 + i, y, x0 + i + 1, y + 1), texture)


def _label_rows(level, ids, palette) -> float:
    """Una riga per corpo di font. Ritorna la y a cui riprendere."""
    for row, size in enumerate(FONT_SIZES):
        top = 2.0 + row * ROW_HEIGHT
        # Quadrato rosa di ESATTAMENTE un quadretto: e' insieme il punto
        # passato a Dungeondraft e il metro di paragone per il corpo del font.
        anchor = Rect(ANCHOR_X, top, ANCHOR_X + 1, top + 1)
        add_pattern(level, ids, anchor, palette.floors["piazza"], color=_PINK)
        _ruler(level, ids, palette, ANCHOR_X + 1.5, top, RULER_LEN)
        cx, cy = anchor.center()
        add_text(level, ids, cx, cy, f"Cattedrale corpo {size}", font_size=size)
    return 2.0 + len(FONT_SIZES) * ROW_HEIGHT


def _ground_swatches(level, ids, palette, catalog, y0: float) -> None:
    """Una toppa per ogni terreno candidato, col nome accanto.

    Le prime vengono da `floors` (categoria pattern/tileset del catalogo) e
    sappiamo che Dungeondraft le rende. Le ultime vengono da `terrain`, ed e'
    proprio quello che questo foglio deve verificare: se restano bianche o
    trasparenti, le aree di parchi e cimiteri vanno ripensate."""
    side = 4.0
    swatches = [(f"floors: {name}", texture) for name, texture in sorted(palette.floors.items())]
    swatches += [
        (f"terrain: {name}", texture) for name, texture in sorted((catalog.get("terrain") or {}).items())
    ]

    for i, (name, texture) in enumerate(swatches):
        col, row = i % 6, i // 6
        x = 2.0 + col * (side + 3.0)
        y = y0 + 3.0 + row * (side + 3.0)
        add_pattern(level, ids, Rect(x, y, x + side, y + side), texture)
        # Corpo 128: se la calibrazione dice che e' sbagliato, questi nomi
        # saranno fuori misura ma restano leggibili ingrandendo.
        add_text(level, ids, x + side / 2, y + side + 0.5, name, font_size=128)


def build(template: str, out: str) -> int:
    catalog = load_catalog()
    palette = palette_for("city", catalog)
    prepared = prepare(load_template(template), levels=1)
    ids = IdAllocator.from_document(prepared)
    level = prepared["world"]["levels"]["0"]

    next_y = _label_rows(level, ids, palette)
    _ground_swatches(level, ids, palette, catalog, next_y)

    finalize(prepared, ids)
    issues = validate(prepared)
    errors = [i for i in issues if i.severity == "error"]
    for issue in issues:
        print(f"[{'ERRORE' if issue.severity == 'error' else 'AVVISO'}] {issue.code} {issue.message}")
    if errors:
        print(f"\n{len(errors)} errori: {out} NON scritto.", file=sys.stderr)
        return 1

    save(prepared, out)
    print(f"\nScritto {out}")
    print(f"  {len(FONT_SIZES)} righe di calibrazione del testo (corpi {FONT_SIZES[0]}-{FONT_SIZES[-1]})")
    print(f"  {len(palette.floors)} terreni da `floors` + {len(catalog.get('terrain') or {})} da `terrain`")
    print("\nAprilo in Dungeondraft e dimmi:")
    print("  1. quale corpo si legge a mappa intera senza coprire tutto")
    print("  2. dove cade il testo rispetto al quadrato rosa (sopra, centrato, a destra)")
    print("  3. quanti quadretti del righello occupa il nome, su quella riga")
    print("  4. quali toppe di terreno si vedono e quali restano vuote")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", default="templates/blank_80x80.dungeondraft_map")
    parser.add_argument("--out", default="generated/calibrazione_etichette.dungeondraft_map")
    args = parser.parse_args(argv)
    return build(args.template, args.out)


if __name__ == "__main__":
    sys.exit(main())
