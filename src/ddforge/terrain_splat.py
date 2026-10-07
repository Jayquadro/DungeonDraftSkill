"""Codec di `level['terrain']['splat']` e del pavimento nativo delle grotte
(TASK-67, spike per decorate M10, docs/format.md §15).

Codifica decodificata sul modello di TASK-31/`cave_bitmap.py`: a differenza
del layer cave, lo splat del terreno NON ha margine. E' una griglia di
sotto-celle row-major su tutta la mappa (`4*width` x `4*height`, 4
sotto-celle per quadretto per lato), con 4 byte per sotto-cella: il peso
0-255 di ciascuno dei quattro slot `texture_1..texture_4`, che per un
pennello pieno somma a 255 (blend edge del pennello nativo di Dungeondraft).

Verificato sull'unico campione reale con terreno dipinto a mano trovato sul
disco di Jay: `tests/fixtures/cave_freehand_80x80.dungeondraft_map` (lo
stesso file del campione cave freehand di TASK-31 — Jay aveva dipinto
anche il terreno nella stessa sessione). Provato per esclusione contro
l'ipotesi alternativa (blocco di 16 sotto-celle contiguo per quadretto,
poi quadretti in row-major): solo la codifica riga-per-riga qui sotto
restituisce una macchia di pennello spazialmente coerente; l'altra la
frantuma in rumore (bounding-box density 0.54 contro 0.23, vedi la nota di
chiusura del task).
"""

_SUB = 4  # sotto-celle per quadretto, per lato — nessun margine (a differenza di cave.bitmap)
_SLOTS = 4  # texture_1..texture_4


def terrain_grid_shape(width: int, height: int) -> tuple[int, int]:
    """(larghezza, altezza) della griglia di sotto-celle per una mappa width x height quadretti."""
    return _SUB * width, _SUB * height


def default_weights(width: int, height: int, slot: int = 1) -> list[list[tuple[int, ...]]]:
    """Griglia "non dipinta": `slot` (1-4) al 100% ovunque. E' lo stato di
    ogni mappa generata da `generate`, mai toccato finora (SPEC-decorate §7.3
    e il motivo per cui serve questo spike)."""
    if slot not in (1, 2, 3, 4):
        raise ValueError(f"slot deve essere 1-4, non {slot!r}")
    grid_w, grid_h = terrain_grid_shape(width, height)
    one_hot = tuple(255 if i == slot - 1 else 0 for i in range(_SLOTS))
    return [[one_hot for _ in range(grid_w)] for _ in range(grid_h)]


def encode_terrain_splat(
    weights: list[list[tuple[int, ...]]], width: int, height: int
) -> str:
    """Griglia di pesi (sotto-cella -> 4 interi 0-255) -> stringa PoolByteArray."""
    grid_w, grid_h = terrain_grid_shape(width, height)
    if len(weights) != grid_h or any(len(row) != grid_w for row in weights):
        raise ValueError(f"la griglia deve essere {grid_w}x{grid_h} sotto-celle")
    data = bytearray(grid_w * grid_h * _SLOTS)
    for y in range(grid_h):
        row = weights[y]
        for x in range(grid_w):
            i = (y * grid_w + x) * _SLOTS
            data[i : i + _SLOTS] = bytes(row[x])
    return "PoolByteArray( " + ", ".join(str(b) for b in data) + " )"


def decode_terrain_splat(
    blob: str, width: int, height: int
) -> list[list[tuple[int, ...]]]:
    """Inverso di `encode_terrain_splat`, per il round-trip."""
    grid_w, grid_h = terrain_grid_shape(width, height)
    inner = blob[blob.index("(") + 1 : blob.rindex(")")].strip()
    data = [int(x) for x in inner.split(",")] if inner else []
    expected = grid_w * grid_h * _SLOTS
    if len(data) < expected:
        raise ValueError(
            f"terrain.splat troppo corto per {width}x{height} quadretti "
            f"(griglia {grid_w}x{grid_h} sotto-celle): {len(data)} byte, "
            f"attesi almeno {expected}"
        )
    return [
        [
            tuple(data[(y * grid_w + x) * _SLOTS : (y * grid_w + x) * _SLOTS + _SLOTS])
            for x in range(grid_w)
        ]
        for y in range(grid_h)
    ]


def paint_tiles(
    weights: list[list[tuple[int, ...]]],
    mask: list[list[bool]],
    slot: int,
    coverage: float = 1.0,
) -> list[list[tuple[int, ...]]]:
    """Dipinge `slot` (1-4) su ogni quadretto dove `mask[y][x]` e vero,
    con intensita `coverage` (0-1). `mask` e a risoluzione QUADRETTO (come
    i Rect del Blueprint), non sotto-cella: il planner di decorate (TASK-69)
    ragiona per zona, non per sotto-cella, quindi ogni quadretto marcato
    dipinge in blocco le sue 4x4 sotto-celle.

    Non muta `weights`: ritorna una nuova griglia (stessa disciplina delle
    funzioni di `compose.py` — il documento si costruisce, non si modifica
    sul posto in piu punti). Il blend e lineare fra il peso di partenza e un
    pennello pieno su `slot`, come il pennello nativo di Dungeondraft (gli
    altri slot si riducono in proporzione, invece di azzerarsi di colpo)."""
    if slot not in (1, 2, 3, 4):
        raise ValueError(f"slot deve essere 1-4, non {slot!r}")
    if not 0.0 <= coverage <= 1.0:
        raise ValueError(f"coverage deve essere in [0, 1], non {coverage!r}")
    grid_h = len(weights)
    grid_w = len(weights[0]) if grid_h else 0
    mask_h = len(mask)
    mask_w = len(mask[0]) if mask_h else 0
    if grid_h != mask_h * _SUB or grid_w != mask_w * _SUB:
        raise ValueError(
            f"mask deve essere {mask_w}x{mask_h} quadretti coerente con una griglia "
            f"di {grid_w}x{grid_h} sotto-celle (rapporto {_SUB}:1 per lato)"
        )

    idx = slot - 1
    out = [row[:] for row in weights]
    for ty in range(mask_h):
        for tx in range(mask_w):
            if not mask[ty][tx]:
                continue
            for sy in range(_SUB):
                gy = ty * _SUB + sy
                for sx in range(_SUB):
                    gx = tx * _SUB + sx
                    base = weights[gy][gx]
                    blended = tuple(
                        round(base[i] * (1 - coverage) + (255 if i == idx else 0) * coverage)
                        for i in range(_SLOTS)
                    )
                    out[gy][gx] = blended
    return out


# ---------------------------------------------------------------------------
# Pavimento nativo delle grotte: `level['cave']['texture']` (decisione di
# Jay, SPEC-decorate §14 D6). Campo stringa semplice, nessuna codifica — ma
# NON una chiave del catalogo data/assets.json: `assets._classify` non
# riconosce ancora le texture sotto `/caves/` (nessuna categoria dedicata),
# quindi finora nessuna finisce in catalogo. Lista chiusa delle texture
# verificate sul disco di Jay finche quella lacuna non viene chiusa (vedi
# nota di chiusura del task): due texture base del programma (Dungeondraft
# non le aggiunge a nessun asset_manifest, quindi non possono far scattare
# DDF014) piu una del pack DnDungeon Overhaul, gia nel manifest di produzione.
# ---------------------------------------------------------------------------

CAVE_FLOOR_TEXTURES: dict[str, str] = {
    "rocky": "res://textures/caves/rocky/floor.png",
    "colorable": "res://textures/caves/colorable/floor.png",
    "limestone": "res://packs/DnDgCORE/textures/caves/limestone_cave/floor.webp",
}

DEFAULT_CAVE_FLOOR = "colorable"

# La primitiva che muta il documento e `build.set_cave_floor_texture`
# (stessa disciplina di `cave_bitmap.encode_cave_bitmap` +
# `build.set_cave_bitmap`): qui restano solo dati e codec, mai una funzione
# che scrive sul `level`.
