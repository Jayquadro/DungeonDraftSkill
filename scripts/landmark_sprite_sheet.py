"""Campionario degli sprite dei luoghi: scrivilo, potalo in Dungeondraft,
rileggilo (TASK-48).

Il problema che risolve: per ogni luogo urbano notevole il catalogo offre
parecchi sprite plausibili, e quale sia BELLO non lo puo' decidere chi scrive
il codice. Questo script mette tutti i candidati sulla mappa, una riga per
luogo, e li rilegge dopo che Jay ha cancellato quelli che non vuole.

    # 1. genera i fogli
    python scripts/landmark_sprite_sheet.py --write

    # 2. Jay li apre in Dungeondraft, CANCELLA gli sprite che non gli
    #    piacciono e salva, lasciando sulla riga solo quelli da usare

    # 3. rileggi la scelta
    python scripts/landmark_sprite_sheet.py --read generated/campionario_*.dungeondraft_map

Il passo 3 stampa la tabella gia' pronta da incollare in
`assets._CITY_LANDMARK_SPRITES`.

COME E' FATTA UNA RIGA: a sinistra il nome del luogo, a destra i candidati in
celle affiancate. Ogni sprite e' ingrandito per riempire la sua cella, quindi
il foglio serve a giudicare il DISEGNO e non la dimensione: le dimensioni
vere a cui ogni sprite verra' reso sulla mappa stanno in
`docs/sprite-luoghi.md`.

COME VIENE RILETTA: dalla posizione. La riga si ricava dalla y dell'oggetto e
la colonna non conta, quindi si possono cancellare sprite liberamente, ma NON
spostarli da una riga all'altra.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ddforge.assets import load_catalog, palette_for  # noqa: E402
from ddforge.build import add_object, add_pattern, add_text  # noqa: E402
from ddforge.ids import IdAllocator  # noqa: E402
from ddforge.model import Rect  # noqa: E402
from ddforge.template import finalize, load_template, prepare, save  # noqa: E402
from ddforge.validate import validate  # noqa: E402

# Candidati per luogo: tutto quello che nel catalogo puo' ragionevolmente
# rappresentare quel luogo, non solo quello in uso oggi. Meglio offrirne uno
# di troppo che costringere a un secondo giro: cancellare e' gratis, aggiungere
# no.
#
# L'ultima voce di ogni riga NON e' un suggerimento: l'ordine e' solo quello
# in cui i candidati compaiono sulla mappa.
# Cantiere navale, mercato del pesce, quartiere povero e porta delle mura
# erano qui e sono stati tolti: Jay li ha scartati guardando il campionario
# e non gli interessano, quindi sono usciti anche dal catalogo dei luoghi
# (generators/landmarks.py). Rimetterli vuol dire rimetterli in entrambi i
# posti.
CANDIDATES: dict[str, tuple[str, ...]] = {
    # --- culto e potere --------------------------------------------------
    "tempio": (
        "church_01", "cathedral_simple", "cathedral", "bb_city_cathedral_1_color",
        "bb_keepsandcastles_cathedral_color", "estate1", "house_02",
    ),
    "cattedrale": (
        "cathedral", "cathedral_simple", "bb_city_cathedral_1_color",
        "bb_keepsandcastles_cathedral_color", "church_01",
    ),
    "monastero": (
        "cathedral_simple", "bb_seasandshores_island_monastery_color",
        "bb_keepsandcastles_forestkeep_color", "estate1", "estate2_lg",
        "church_01", "hamlet3",
    ),
    "palazzo": (
        "estate2_lg", "castle_w_moat", "bb_keepsandcastles_castle_color",
        "bb_keepsandcastles_castle_2_color", "bb_keepsandcastles_keep_color",
        "bb_keepsandcastles_moatkeep_color", "bb_city_fort_1_color", "estate1",
    ),
    "municipio": ("estate1", "estate2_sm", "estate2_lg", "house_09", "house_02", "bb_houses1_flag1"),
    "caserma": (
        "castle_w_moat", "bb_city_fort_1_color", "bb_keepsandcastles_keep_color",
        "estate2_sm", "bb_houses1_tower2", "wood_walls_tower", "hamlet2",
    ),
    "prigione": (
        "estate2_sm", "bb_keepsandcastles_moatkeep_color", "bb_keepsandcastles_keep_color",
        "cage_04", "bb_houses1_tower2", "castle_w_moat",
    ),
    "arena": ("bb_keepsandcastles_amphitheatre_color", "bb_city_tournament_1_color", "tourney_grounds"),
    "teatro": (
        "tourney_grounds", "bb_city_tournament_1_color", "estate1", "house_09",
        "bb_keepsandcastles_amphitheatre_color",
    ),
    # --- sapere -----------------------------------------------------------
    "accademia": (
        "bb_keepsandcastles_maze_color", "castle_w_moat", "cathedral_simple",
        "estate2_lg", "bb_houses1_tower2", "magic_circle_01",
        "bb_keepsandcastles_forestkeep_color",
    ),
    "biblioteca": ("house_02", "house_11", "estate2_sm", "bookshelf_wood_01", "bookshelf_4_v3", "house_05"),
    "alchimista": (
        "house_07", "house_06", "alchemy_potion_colorable_12",
        "dq_alchemy_ingredient_prefab_09", "shed_02",
    ),
    # --- commercio --------------------------------------------------------
    "banca": ("house_05", "estate2_sm", "estate1", "house_09"),
    "gilda": ("house_09", "house_12", "estate2_sm", "bb_houses1_flag1", "bb_houses1_flag2", "hamlet2"),
    "magazzino": ("shed_02", "shed_01", "crates_01", "large_house", "hamlet1", "deck", "crate_wood_01"),
    "dogana": ("shed_01", "shed_02", "crates_01", "palisade_gate", "bounty_board_01", "signpost"),
    # --- artigianato ------------------------------------------------------
    "fabbro": ("forge", "bb_city_blacksmith_1_color", "barrel_forge_01", "shed_01", "house_10"),
    "stalle": ("shed_01", "shed_02", "trough_barn_04", "hamlet1", "large_platform"),
    "fornaio": ("house_10", "house_05", "oven_brick_red_a2_2x2", "gw_bakery_table_2", "small_house"),
    "macelleria": ("house_08", "house_01", "shed_01", "small_house"),
    "conceria": ("shed_02", "shed_01", "hamlet1", "deck", "dirty_tarp", "large_platform"),
    "macello": ("shed_01", "shed_02", "hamlet1", "animal_cage_top_02_a", "trough_barn_04"),
    "mulino": ("moulin", "windmill_01", "windmill_02", "windmill_03", "bb_city_woodmill_1_color"),
    # --- svago e servizi --------------------------------------------------
    "taverna": ("inn_01", "house_03", "house_04", "large_house", "large_red_house", "hamlet2"),
    "locanda": ("inn_01", "large_house", "large_red_house", "house_02", "hamlet3"),
    "bordello": ("house_06", "house_08", "small_red_house", "bb_houses1_balcony", "house_04"),
    "bagni": ("house_04", "estate2_sm", "house_01", "hamlet1"),
    "lazzaretto": ("shed_02", "strawhouse_03", "small_house", "hamlet1", "house_08"),
    # --- struttura urbana -------------------------------------------------
    "torre_guardia": (
        "wood_walls_tower", "bb_houses1_tower1", "bb_houses1_tower2",
        "bb_keepsandcastles_wall_corner_2_color",
    ),
    "faro": (
        "bb_city_lighthouse_1_color", "bb_seasandshores_cliff_lighthouse_color",
        "bb_houses1_tower1", "bb_houses1_tower2", "wood_walls_tower",
    ),
    # --- luoghi all'aperto: qui si sceglie un INSIEME di pezzi, non uno solo
    "mercato": (
        "canopy_01", "canopy_02", "canopy_03", "tent_01", "tent_02", "tent_03",
        "bb_houses1_tarp1", "bb_houses1_tarp2", "bb_houses1_tarp3", "small_tarp_1",
        "small_tarp_2", "dirty_tarp", "patched_tarp", "crates_01", "crates_02",
        "table_01", "table_02",
    ),
    "patibolo": (
        "thehangedman", "gibbet", "noose_1", "noose_2", "noose_3", "cage_04",
        "pillar_01", "spike_barricade_01",
    ),
    "statua": (
        "statue_male_mage_alt_03_a", "ornament5", "ornament1", "pillar_01",
        "column", "fountain_stone_01", "bounty_board_01",
    ),
    "giardino": (
        "tree1", "tree2", "tree3", "tree4", "tree_01", "tree_03", "tree_05",
        "bush_01", "bush_03", "bush_07", "bench_01", "bench_wood_01", "rock_01",
        "fence_01", "bb_keepsandcastles_garden_color", "bb_city_orchard_1_color",
    ),
    "cimitero": (
        "cemetery", "cemetery_nondenominational", "skeleton_grave_02", "skeleton_04",
        "pillar_01", "column", "cathedral_simple", "fence_01", "bb_houses1_tower1",
    ),
    "fiera": (
        "tent_01", "tent_02", "tent_03", "canopy_01", "canopy_03", "campfire_01",
        "campfire_07", "table_01", "bb_houses1_tarp1", "bounty_board_01", "worker_3",
    ),
}

# Geometria del foglio, in quadretti. Il template di riferimento e'
# blank_160x160, che di area utile ne ha 128.
MARGIN = 1.0
LABEL_W = 13.0
ROW_H = 7.0
CELL = 6.5
SPRITE_FILL = 0.85
LABEL_FONT = 256  # un quadretto di corpo: qualunque sia la semantica vera, si legge


def _layout(canvas: int) -> tuple[int, int]:
    """(righe per foglio, celle per riga) che stanno nel canvas."""
    rows = int((canvas - 2 * MARGIN) / ROW_H)
    cells = int((canvas - LABEL_W - 2 * MARGIN) / CELL)
    return rows, cells


def _chunks(canvas: int) -> list[list[str]]:
    """I luoghi divisi in fogli, nell'ordine di CANDIDATES.

    Le righe si spartiscono in parti uguali fra i fogli necessari invece di
    riempirne uno alla volta: con 40 luoghi e 18 righe per foglio verrebbero
    18+18+4, e l'ultimo foglio sembrerebbe rotto. Meglio 14+13+13, tre fogli
    corti e uguali.

    Questa funzione decide anche la RILETTURA (riga -> luogo), quindi
    cambiarla invalida i fogli gia' potati: se serve, prima rileggerli."""
    rows_per_sheet, _ = _layout(canvas)
    keys = list(CANDIDATES)
    sheets = -(-len(keys) // rows_per_sheet)  # divisione intera per eccesso
    per_sheet = -(-len(keys) // sheets)
    return [keys[i : i + per_sheet] for i in range(0, len(keys), per_sheet)]


def _row_rect(row: int, canvas: int) -> Rect:
    top = MARGIN + row * ROW_H
    return Rect(MARGIN, top, canvas - MARGIN, top + ROW_H)


def _cell_rect(row: int, col: int, canvas: int) -> Rect:
    top = MARGIN + row * ROW_H + 0.5
    left = MARGIN + LABEL_W + col * CELL
    return Rect(left, top, left + CELL - 0.5, top + ROW_H - 1.0)


def _sprite(catalog: dict, key: str) -> tuple[str, float, float]:
    texture = catalog["objects"][key]
    size = (catalog.get("object_sizes") or {}).get(key)
    if size:
        return texture, float(size[0]), float(size[1])
    return texture, 256.0, 256.0  # texture non-PNG: nessuna dimensione in catalogo


def _check_keys(catalog: dict) -> None:
    missing = {
        kind: [k for k in keys if k not in catalog["objects"]]
        for kind, keys in CANDIDATES.items()
    }
    missing = {k: v for k, v in missing.items() if v}
    if missing:
        raise SystemExit(f"Chiavi assenti dal catalogo: {missing}")


def write(template: str, out_prefix: str) -> int:
    catalog = load_catalog()
    _check_keys(catalog)
    palette = palette_for("city", catalog)

    doc = load_template(template)
    canvas = min(doc["world"]["width"], doc["world"]["height"])
    rows_per_sheet, cells_per_row = _layout(canvas)

    too_many = {k: len(v) for k, v in CANDIDATES.items() if len(v) > cells_per_row}
    if too_many:
        raise SystemExit(
            f"Righe piu' larghe del foglio ({cells_per_row} celle): {too_many}. "
            "Riduci i candidati oppure alza il canvas del template."
        )

    written = []
    for sheet, kinds in enumerate(_chunks(canvas), start=1):
        prepared = prepare(load_template(template), levels=1)
        ids = IdAllocator.from_document(prepared)
        level = prepared["world"]["levels"]["0"]

        for row, kind in enumerate(kinds):
            # Bande alternate: separano le righe a colpo d'occhio, cosi' si
            # vede subito a quale luogo appartiene uno sprite.
            band = palette.floors["piazza"] if row % 2 == 0 else palette.floors["selciato"]
            add_pattern(level, ids, _row_rect(row, canvas), band)
            # Il nome va al CENTRO della colonna di sinistra, non al suo
            # bordo: l'ancoraggio di `text.position` non e' ancora noto (vedi
            # scripts/label_calibration.py). Centrato a meta' colonna il nome
            # sta dentro la colonna se l'ancoraggio e' il centro, e sconfina
            # al piu' su una cella se e' l'angolo sinistro. Messo sul bordo,
            # nel secondo caso sarebbe leggibile ma nel primo meta' nome
            # finirebbe fuori dal canvas.
            band_rect = _row_rect(row, canvas)
            add_text(
                level, ids, MARGIN + LABEL_W / 2, band_rect.y1 + ROW_H / 2, kind,
                font_size=LABEL_FONT,
            )
            for col, key in enumerate(CANDIDATES[kind]):
                cell = _cell_rect(row, col, canvas)
                texture, width_px, height_px = _sprite(catalog, key)
                scale = min(cell.w / (width_px / 256), cell.h / (height_px / 256)) * SPRITE_FILL
                cx, cy = cell.center()
                add_object(level, ids, cx, cy, texture, scale=scale)

        finalize(prepared, ids)
        issues = [i for i in validate(prepared) if i.severity == "error"]
        if issues:
            for issue in issues:
                print(f"[ERRORE] {issue.code} {issue.path}: {issue.message}", file=sys.stderr)
            return 1

        out = f"{out_prefix}_{sheet}.dungeondraft_map"
        save(prepared, out)
        written.append((out, kinds))

    print(f"Scritti {len(written)} fogli ({rows_per_sheet} righe l'uno, {cells_per_row} celle per riga):")
    for out, kinds in written:
        print(f"  {out}")
        for row, kind in enumerate(kinds):
            print(f"      riga {row + 1:2d}  {kind:<28} {len(CANDIDATES[kind])} candidati")
    print("\nAprili in Dungeondraft, CANCELLA gli sprite che non vuoi e salva.")
    print("Non spostare gli sprite da una riga all'altra: la riga dice a quale luogo appartengono.")
    print(f"\nPoi: python {Path(__file__).name} --read {out_prefix}_*.dungeondraft_map")

    base = sorted(
        key for keys in CANDIDATES.values() for key in keys
        if not catalog["objects"][key].startswith("res://packs/")
    )
    if base:
        print(
            f"\n{len(base)} candidati sono texture base del programma e non di un pack "
            f"({', '.join(dict.fromkeys(base))}): Dungeondraft le disegna, ma un'anteprima "
            "esterna che legge solo i .dungeondraft_pack no."
        )
    return 0


def read(paths: list[str], template: str) -> int:
    catalog = load_catalog()
    by_texture = {texture: key for key, texture in catalog["objects"].items()}
    doc = load_template(template)
    canvas = min(doc["world"]["width"], doc["world"]["height"])
    sheets = _chunks(canvas)

    chosen: dict[str, list[str]] = {}
    for path in sorted(paths):
        # Il numero di foglio sta nel nome: _1, _2, ... come li ha scritti write().
        stem = Path(path).stem
        try:
            sheet = int(stem.rsplit("_", 1)[1]) - 1
        except (IndexError, ValueError):
            print(f"Salto {path}: il nome non finisce con _<numero di foglio>", file=sys.stderr)
            continue
        if not 0 <= sheet < len(sheets):
            print(f"Salto {path}: foglio {sheet + 1} fuori dai {len(sheets)} attesi", file=sys.stderr)
            continue

        with open(path, encoding="utf-8") as f:
            level = json.load(f)["world"]["levels"]["0"]
        for obj in level.get("objects", []):
            y = float(obj["position"].split(",")[1].strip(" )")) / 256
            row = int((y - MARGIN) / ROW_H)
            if not 0 <= row < len(sheets[sheet]):
                continue
            kind = sheets[sheet][row]
            key = by_texture.get(obj["texture"])
            if key is None or key not in CANDIDATES[kind]:
                continue
            if key not in chosen.setdefault(kind, []):
                chosen[kind].append(key)

    print("# Scelta di Jay, da incollare in assets._CITY_LANDMARK_SPRITES")
    print("_CITY_LANDMARK_SPRITES: dict[str, tuple[str, ...]] = {")
    for kind in CANDIDATES:
        keys = chosen.get(kind, [])
        if not keys:
            print(f'    # "{kind}": NESSUNO SCELTO - riga vuota o foglio non riletto')
            continue
        joined = ", ".join(f'"{k}"' for k in keys)
        print(f'    "{kind}": ({joined},),')
    print("}")

    absent = [k for k in CANDIDATES if k not in chosen]
    if absent:
        print(f"\n# righe senza nessuno sprite superstite: {absent}", file=sys.stderr)
    return 0


# Varianti di giardino e cimitero da mettere a confronto (--areas). Un'area
# di questo tipo non e' uno sprite ma una SCENA, e una scena non si giudica
# vedendo i pezzi in fila sul campionario: va vista montata. Ogni variante e'
# un insieme di pezzi diverso, disegnato con lo stesso codice che genera le
# mappe vere (compose.draw_landmark), quindi quel che si vede e' quel che si
# otterra'.
AREA_VARIANTS: dict[str, list[tuple[str, tuple[str, ...]]]] = {
    # Solo sprite VERDI, su richiesta di Jay: fuori gli alberi di City
    # Terrain (`tree1`..`tree4`, marroni: sono simboli da mappa di regione,
    # non chiome) e fuori aceri rossi, ciliegi rosa, alberi autunnali e
    # alberi secchi, che il catalogo ha ma che verdi non sono.
    "giardino": [
        ("A - chiome grandi", ("tree_big_green_01", "tree_big_green_02", "tree_big_green_03")),
        ("B - chiome semplici", (
            "tree_green_simple_01", "tree_green_simple_02", "tree_green_simple_03",
            "tree_green_simple_04",
        )),
        ("C - pini", ("pine_tree_01", "pine_tree_02", "pine_tree_03", "pine_tree_04")),
        ("D - misto di chiome", (
            "tree_big_green_01", "tree_big_green_03", "tree_green_simple_01",
            "tree_green_simple_03", "tree_massive_green_01",
        )),
        ("E - alberi e cespugli", (
            "tree_big_green_01", "tree_green_simple_02", "bush_green_simple_01",
            "bush_green_simple_05", "bush_green_simple_09",
        )),
        ("F - conifere CHR", ("tree_01", "tree_03", "tree_05")),
    ],
    # Lapidi VERE: il pck base del programma ha una cartella
    # objects/graveyard/ che nessun template di Jay usava, quindi non era mai
    # entrata in catalogo. `gravestone_*` sono lastre con la pietra in testa
    # viste dall'alto; `grave_*` sono le fosse, con bordo di pietra o di
    # legno. I gruppi di tombe di City Terrain, che erano l'unica cosa che
    # avevo da mostrare al primo giro, non sono lapidi: sono cimiteri interi
    # visti da lontano.
    "cimitero": [
        ("A - solo lapidi", (
            "gravestone_01", "gravestone_02", "gravestone_04", "gravestone_05",
        )),
        ("B - lapidi e croci", (
            "gravestone_01", "gravestone_03", "gravestone_05", "gravestone_07",
        )),
        ("C - lapidi e tumuli", (
            "gravestone_01", "gravestone_02", "grave_01", "grave_02", "grave_08",
        )),
        ("D - fosse recintate", ("grave_03", "grave_04", "grave_05", "grave_06")),
        ("E - misto completo", (
            "gravestone_01", "gravestone_03", "gravestone_05", "grave_03", "grave_08",
        )),
        ("F - gruppi City Terrain", ("cemetery", "cemetery_nondenominational")),
    ],
}

# Ogni variante si mostra a DUE dimensioni: quella del preset "quartiere",
# che e' la scala a cui si guarda davvero una di queste aree, e quella del
# preset "citta", dove la stessa area vale poco piu' di un quadretto. Un
# insieme di pezzi puo' funzionare a una scala e non all'altra, e sceglierlo
# guardandone una sola sarebbe scegliere a meta'.
AREA_BIG = (8.0, 8.0)
AREA_SMALL = (2.5, 2.5)
AREA_CELL_W = 13.0
AREA_CELL_H = 15.0


def areas(template: str, out: str) -> int:
    """Foglio di confronto per le aree con sprite multipli (giardino,
    cimitero): ogni variante disegnata da compose.draw_landmark, alle due
    scale a cui la si guarda.

    Passa dal codice di rendering vero e non da un disegno di comodo: quel
    che si vede sul foglio e' esattamente quel che finira' sulle mappe."""
    import random

    from ddforge.compose import draw_landmark
    from ddforge.generators.landmarks import BY_KEY
    from ddforge.model import Landmark

    catalog = load_catalog()
    palette = palette_for("city", catalog)
    prepared = prepare(load_template(template), levels=1)
    ids = IdAllocator.from_document(prepared)
    levels = prepared["world"]["levels"]
    canvas = prepared["world"]["width"]
    per_row = max(1, int((canvas - 2 * MARGIN) / AREA_CELL_W))

    cell = 0
    for kind, variants in AREA_VARIANTS.items():
        ground = BY_KEY[kind].ground
        for title, keys in variants:
            # La palette e' l'unico canale per dire a draw_landmark che
            # sprite usare: la si riscrive prima di ogni variante.
            palette.landmark_sprites[kind] = [
                (catalog["objects"][k], *(catalog.get("object_sizes") or {}).get(k, (256, 256)))
                for k in keys
            ]
            x = MARGIN + (cell % per_row) * AREA_CELL_W
            y = MARGIN + (cell // per_row) * AREA_CELL_H
            big = Rect(x, y, x + AREA_BIG[0], y + AREA_BIG[1])
            small = Rect(x, big.y2 + 1.0, x + AREA_SMALL[0], big.y2 + 1.0 + AREA_SMALL[1])
            for rect in (big, small):
                mark = Landmark(
                    kind=kind, label="", rect=rect, site="band", open_air=True,
                    ground=ground, piece_size=BY_KEY[kind].piece_size,
                )
                # rng fisso: due varianti affiancate devono differire per i
                # PEZZI, non per come sono caduti i dadi.
                draw_landmark(levels, ids, mark, palette, random.Random(1337), labels=[])
            add_text(
                levels["0"], ids, x + AREA_CELL_W / 2, small.y2 + 0.8,
                f"{kind} {title}", font_size=LABEL_FONT,
            )
            cell += 1

    finalize(prepared, ids)
    issues = [i for i in validate(prepared) if i.severity == "error"]
    for issue in issues:
        print(f"[ERRORE] {issue.code} {issue.path}: {issue.message}", file=sys.stderr)
    if issues:
        return 1

    save(prepared, out)
    print(f"Scritto {out}")
    for kind, variants in AREA_VARIANTS.items():
        print(f"  {kind}: {len(variants)} varianti")
        for title, keys in variants:
            print(f"      {title:<34} {', '.join(keys)}")
    print("\nOgni variante e' disegnata due volte: grande come al preset 'quartiere'")
    print("e piccola come al preset 'citta'. Dimmi quale lettera tenere per ciascuna.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", default="templates/blank_160x160.dungeondraft_map")
    parser.add_argument("--write", action="store_true", help="genera i fogli")
    parser.add_argument("--out-prefix", default="generated/campionario")
    parser.add_argument("--read", nargs="+", metavar="FOGLIO", help="rilegge i fogli potati")
    parser.add_argument(
        "--areas", action="store_true",
        help="foglio di confronto per le aree con sprite multipli (giardino, cimitero)",
    )
    parser.add_argument("--areas-out", default="generated/aree.dungeondraft_map")
    args = parser.parse_args(argv)

    if args.read:
        return read(args.read, args.template)
    if args.areas:
        return areas(args.template, args.areas_out)
    if args.write:
        return write(args.template, args.out_prefix)
    parser.error("serve --write, --read oppure --areas")


if __name__ == "__main__":
    sys.exit(main())
