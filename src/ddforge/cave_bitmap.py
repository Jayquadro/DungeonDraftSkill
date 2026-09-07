"""Codec di `level['cave']['bitmap']`/`entrance_bitmap`: layer cave nativo.

Codifica decodificata nello spike TASK-31 (docs/format.md §14, decisione
`decision-1`): maschera bit-packed su una griglia di `(4*width+3) x
(4*height+3)` BIT, 4 sotto-celle per quadretto piu 3 di margine per lato,
row-major, flusso di bit continuo NON allineato al byte, bit meno
significativo per primo dentro ogni byte. `1` = grotta scavata, `0` = roccia
intatta. Portato qui da `scripts/cave_spike.py` (codice di spike) per
TASK-32, che e il primo a scriverlo in produzione.
"""

_SUB = 4  # sotto-celle per quadretto
_MARGIN = 3  # sotto-celle in eccesso sul lato della griglia


def cave_grid_shape(width: int, height: int) -> tuple[int, int]:
    """(larghezza, altezza) della griglia di bit per una mappa width x height quadretti."""
    return _SUB * width + _MARGIN, _SUB * height + _MARGIN


def encode_cave_bitmap(grid: list[list[int]], width: int, height: int) -> str:
    """Griglia di sotto-celle (1=scavato, 0=roccia) -> stringa PoolByteArray."""
    grid_w, grid_h = cave_grid_shape(width, height)
    if len(grid) != grid_h or any(len(row) != grid_w for row in grid):
        raise ValueError(f"la griglia deve essere {grid_w}x{grid_h} sotto-celle")
    data = bytearray((grid_w * grid_h + 7) // 8)
    for y in range(grid_h):
        for x in range(grid_w):
            if grid[y][x]:
                i = y * grid_w + x
                data[i // 8] |= 1 << (i % 8)
    return "PoolByteArray( " + ", ".join(str(b) for b in data) + " )"


def decode_cave_bitmap(blob: str, width: int, height: int) -> list[list[int]]:
    """Inverso di encode_cave_bitmap, per verificare il round-trip."""
    grid_w, grid_h = cave_grid_shape(width, height)
    inner = blob[blob.index("(") + 1 : blob.rindex(")")].strip()
    data = [int(x) for x in inner.split(",")] if inner else []
    return [
        [(data[(y * grid_w + x) // 8] >> ((y * grid_w + x) % 8)) & 1 for x in range(grid_w)]
        for y in range(grid_h)
    ]
