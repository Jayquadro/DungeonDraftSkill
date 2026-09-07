"""Blocca la codifica di `cave.bitmap` scoperta in TASK-31.

Questi test NON coprono codice di produzione: il codec vive ancora in
`scripts/cave_spike.py` (codice di spike). Servono a proteggere due cose che
altrimenti si perderebbero in silenzio:

1. i due campioni in `tests/fixtures/` sono l'unica evidenza reale del
   formato in tutto il progetto — se qualcuno li tocca o li sostituisce,
   questi test se ne accorgono;
2. la codifica documentata in `docs/format.md` §14 e quella che i file veri
   usano davvero.

TASK-32 portera il codec in `src/ddforge/` e potra riusare gli stessi
campioni tramite le fixture `cave_rect_path` / `cave_freehand_path`.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from cave_spike import (  # noqa: E402
    cave_grid_shape,
    decode_cave_bitmap,
    encode_cave_bitmap,
)


def _load(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    return doc, doc["world"]["width"], doc["world"]["height"]


def _parse_byte_array(blob: str) -> list[int]:
    inner = blob[blob.index("(") + 1 : blob.rindex(")")].strip()
    return [int(x) for x in inner.split(",")] if inner else []


def test_bitmap_length_follows_the_subcell_grid_formula():
    """La lunghezza dipende solo dalle dimensioni della mappa, mai dal
    contenuto: SPEC.md §2 la dava per "non lineare" e non ricavabile."""
    # (width, height) -> byte attesi. 8x8/30x30/50x25 sono i campioni gia
    # citati in SPEC.md §2; 80x80 e quello misurato sui file di Jay.
    for width, height, expected in [(8, 8, 154), (30, 30, 1892), (50, 25, 2614), (80, 80, 13042)]:
        grid_w, grid_h = cave_grid_shape(width, height)
        assert (grid_w, grid_h) == (4 * width + 3, 4 * height + 3)
        assert (grid_w * grid_h + 7) // 8 == expected


def test_real_samples_have_the_predicted_length(cave_rect_path, cave_freehand_path):
    for path in (cave_rect_path, cave_freehand_path):
        doc, width, height = _load(path)
        grid_w, grid_h = cave_grid_shape(width, height)
        expected = (grid_w * grid_h + 7) // 8
        cave = doc["world"]["levels"]["0"]["cave"]
        for field in ("bitmap", "entrance_bitmap"):
            assert len(_parse_byte_array(cave[field])) == expected, f"{path.name}.{field}"


def test_roundtrip_is_byte_identical_on_real_samples(cave_rect_path, cave_freehand_path):
    """La prova piu forte che la codifica e quella giusta: decodificare e
    ricodificare un blob scritto da Dungeondraft restituisce gli stessi
    identici byte. Una codifica anche solo leggermente sbagliata (ordine dei
    bit, allineamento delle righe) non passerebbe."""
    for path in (cave_rect_path, cave_freehand_path):
        doc, width, height = _load(path)
        cave = doc["world"]["levels"]["0"]["cave"]
        for field in ("bitmap", "entrance_bitmap"):
            original = cave[field]
            grid = decode_cave_bitmap(original, width, height)
            assert encode_cave_bitmap(grid, width, height) == original, f"{path.name}.{field}"


def test_controlled_sample_decodes_to_the_rectangle_jay_drew(cave_rect_path):
    """Jay: "circa 20x3 quadretti, in alto a sinistra"."""
    doc, width, height = _load(cave_rect_path)
    grid = decode_cave_bitmap(doc["world"]["levels"]["0"]["cave"]["bitmap"], width, height)

    rows = [y for y, row in enumerate(grid) if any(row)]
    cols = [x for x in range(len(grid[0])) if any(row[x] for row in grid)]

    # 4 sotto-celle per quadretto: il rettangolo e alto 3 quadretti esatti e
    # largo 21, e sta nel quadrante in alto a sinistra della mappa 80x80.
    assert (max(rows) - min(rows) + 1) / 4 == 3.0
    assert (max(cols) - min(cols) + 1) / 4 == 21.0
    assert min(cols) / 4 < width / 2 and min(rows) / 4 < height / 2


def test_freehand_sample_is_a_single_organic_blob(cave_freehand_path):
    """Contro-campione: una forma disegnata a mano libera, non un rettangolo.
    Se la decodifica fosse sbagliata (p.es. bit order invertito) verrebbe
    fuori rumore sparso, non una macchia connessa che copre mezza mappa."""
    doc, width, height = _load(cave_freehand_path)
    grid = decode_cave_bitmap(doc["world"]["levels"]["0"]["cave"]["bitmap"], width, height)

    carved = {(x, y) for y, row in enumerate(grid) for x, v in enumerate(row) if v}
    assert len(carved) > 5000

    # Quasi tutto in UNA componente 4-connessa: una macchia, non rumore
    # sparso. Non il 100%: il disegno a mano libera lascia qualche schizzo
    # staccato (61 sotto-celle su 9284 nel campione reale).
    #
    # NB: questo test NON e quello che fissa l'ordine dei bit — misurato,
    # con MSB-first il rapporto scende solo da 0.993 a 0.941, troppo poco
    # per distinguerli in modo affidabile. A inchiodare la codifica e il
    # round-trip byte-esatto sopra. Qui si verifica solo che il campione sia
    # ancora una forma disegnata a mano coerente, cioe che la fixture non sia
    # stata sostituita con altro.
    remaining = set(carved)
    largest = 0
    while remaining:
        stack = [remaining.pop()]
        size = 1
        while stack:
            x, y = stack.pop()
            for neighbour in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if neighbour in remaining:
                    remaining.discard(neighbour)
                    size += 1
                    stack.append(neighbour)
        largest = max(largest, size)
    assert largest / len(carved) > 0.95


def test_blank_template_has_an_empty_cave_of_the_right_size():
    """Il template vuoto ha gia il blob della lunghezza finale, tutto a zero:
    e per questo che la lunghezza non puo dipendere dal contenuto."""
    doc, width, height = _load(REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map")
    grid = decode_cave_bitmap(doc["world"]["levels"]["0"]["cave"]["bitmap"], width, height)
    assert not any(any(row) for row in grid)
