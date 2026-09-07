"""Spike TASK-31: grotta come muri poligonali vs layer cave nativo.

NON e il generatore vero (quello e TASK-32, dopo che questo spike decide
come renderizzare il contorno). Genera entrambe le alternative dallo stesso
cellular automata, per poterle confrontare aperte in Dungeondraft.

Modi (--mode):
  walls   muri poligonali: contorno tracciato per lati di cella (niente
          interpolazione, lati ortogonali) e disegnato con le primitive
          vere (build.add_wall in loop + build.add_polygon_pattern).
  native  layer cave nativo: il CA gira direttamente a risoluzione
          sotto-cella (4x), quindi il contorno e 4 volte piu fine di
          quanto un muro poligonale per quadretto possa essere.
  calib   rettangolo di calibrazione in una posizione nota esatta, per
          verificare l'origine della griglia sotto-cella (vedi sotto).

Codifica di cave.bitmap (decodificata in TASK-31 dai file disegnati a mano
da Jay, round-trip byte-esatto verificato su entrambi):
  griglia di (4*w+3) x (4*h+3) BIT, 4 sotto-celle per quadretto, riga per
  riga, flusso di bit continuo NON allineato al byte, bit meno
  significativo per primo dentro ogni byte. Lunghezza in byte =
  ceil((4w+3)(4h+3)/8), che dipende solo dalle dimensioni della mappa e
  mai dal contenuto. 1 = grotta scavata, 0 = roccia intatta.

Uso:
    python scripts/cave_spike.py [--mode walls|native|calib] [--seed 1337]
"""

import argparse
import random
from pathlib import Path

from ddforge.assets import load_catalog, palette_for
from ddforge.build import add_polygon_pattern, add_wall
from ddforge.ids import IdAllocator
from ddforge.template import finalize, load_template, prepare, save

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map"
DEFAULT_OUT = REPO_ROOT / "generated" / "cave_spike.dungeondraft_map"

# Dimensioni della grotta (quadretti) e offset per centrarla nella mappa
# 80x80 vuota. Il bordo esterno resta sempre muro pieno (vedi _smooth): la
# grotta non tocca mai il perimetro della mappa.
_CAVE_W, _CAVE_H = 36, 26
_OFFSET_X, _OFFSET_Y = 22, 27

_FILL_PROB = 0.45
_ITERATIONS = 5


def _initial_grid(width: int, height: int, seed: int) -> list[list[int]]:
    """1 = roccia, 0 = aperto. Bordo sempre roccia (contorno chiuso lontano
    dal limite della mappa)."""
    rng = random.Random(seed)
    grid = [[1 if rng.random() < _FILL_PROB else 0 for _ in range(width)] for _ in range(height)]
    for x in range(width):
        grid[0][x] = grid[height - 1][x] = 1
    for y in range(height):
        grid[y][0] = grid[y][width - 1] = 1
    return grid


def _wall_neighbors(grid, x: int, y: int) -> int:
    """Vicini di Moore (8-connessi). Fuori griglia conta come roccia."""
    height, width = len(grid), len(grid[0])
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                count += grid[ny][nx]
            else:
                count += 1
    return count


def _smooth(grid) -> list[list[int]]:
    """Una iterazione della regola classica B5/S4 (roguebasin: 'cellular
    automata method'): >=5 vicini roccia -> roccia, <=3 -> aperto, 4 invariato."""
    height, width = len(grid), len(grid[0])
    new_grid = [row[:] for row in grid]
    for y in range(height):
        for x in range(width):
            n = _wall_neighbors(grid, x, y)
            if n >= 5:
                new_grid[y][x] = 1
            elif n <= 3:
                new_grid[y][x] = 0
    for x in range(width):
        new_grid[0][x] = new_grid[height - 1][x] = 1
    for y in range(height):
        new_grid[y][0] = new_grid[y][width - 1] = 1
    return new_grid


def _largest_open_region(grid) -> list[list[int]]:
    """Tiene solo la componente 4-connessa di celle aperte piu grande:
    per questo spike (decidere se il contorno poligonale e leggibile) una
    sola caverna e piu facile da valutare di un arcipelago di isolette."""
    height, width = len(grid), len(grid[0])
    seen = [[False] * width for _ in range(height)]
    best: list[tuple[int, int]] = []
    for sy in range(height):
        for sx in range(width):
            if grid[sy][sx] != 0 or seen[sy][sx]:
                continue
            stack = [(sx, sy)]
            seen[sy][sx] = True
            region = []
            while stack:
                x, y = stack.pop()
                region.append((x, y))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and not seen[ny][nx] and grid[ny][nx] == 0:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            if len(region) > len(best):
                best = region
    kept = {p for p in best}
    return [[0 if (x, y) in kept else 1 for x in range(width)] for y in range(height)]


def generate_cave_grid(*, width: int, height: int, seed: int) -> list[list[int]]:
    grid = _initial_grid(width, height, seed)
    for _ in range(_ITERATIONS):
        grid = _smooth(grid)
    return _largest_open_region(grid)


def _boundary_edges(grid) -> dict[tuple[float, float], tuple[float, float]]:
    """Un lato per ogni confine cella-aperta/cella-roccia, orientato in senso
    orario attorno alla cella aperta (percorrendo top poi right poi bottom
    poi left). Per un blob semplicemente connesso senza strozzature a un
    punto, questo produce un ciclo diretto pulito: mappa punto_iniziale ->
    punto_finale, una sola uscita per vertice."""
    height, width = len(grid), len(grid[0])
    edges: dict[tuple[float, float], tuple[float, float]] = {}

    def is_open(x, y):
        return 0 <= x < width and 0 <= y < height and grid[y][x] == 0

    for y in range(height):
        for x in range(width):
            if grid[y][x] != 0:
                continue
            if not is_open(x, y - 1):
                edges[(x, y)] = (x + 1, y)
            if not is_open(x + 1, y):
                edges[(x + 1, y)] = (x + 1, y + 1)
            if not is_open(x, y + 1):
                edges[(x + 1, y + 1)] = (x, y + 1)
            if not is_open(x - 1, y):
                edges[(x, y + 1)] = (x, y)
    return edges


def _chain_loops(edges: dict[tuple[float, float], tuple[float, float]]) -> list[list[tuple[float, float]]]:
    """Ricompone le coppie punto->punto in cicli chiusi, poi rimuove i punti
    intermedi collineari (tre lati dritti di seguito -> un solo punto)."""
    remaining = dict(edges)
    loops: list[list[tuple[float, float]]] = []
    while remaining:
        start = next(iter(remaining))
        loop = [start]
        current = start
        while True:
            nxt = remaining.pop(current)
            if nxt == start:
                break
            loop.append(nxt)
            current = nxt
        loops.append(_drop_collinear(loop))
    return loops


def _drop_collinear(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    n = len(points)
    kept = []
    for i in range(n):
        a, b, c = points[i - 1], points[i], points[(i + 1) % n]
        if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) != 0:
            kept.append(b)
    return kept or points


def _polygon_area(points: list[tuple[float, float]]) -> float:
    total = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def extract_contour(grid) -> list[tuple[int, int]]:
    """Il poligono di area maggiore fra i cicli di confine trovati (l'esterno
    della caverna; eventuali buchi interni, non attesi con una sola regione
    di roccia scartata da _largest_open_region, non sono gestiti da questo
    spike)."""
    loops = _chain_loops(_boundary_edges(grid))
    outline = max(loops, key=_polygon_area)
    return [(int(x), int(y)) for x, y in outline]


# --- layer cave nativo: codifica di cave.bitmap (vedi docstring) ---

_SUB = 4  # sotto-celle per quadretto
_MARGIN = 3  # sotto-celle in eccesso sul lato della griglia


def cave_grid_shape(w: int, h: int) -> tuple[int, int]:
    """(larghezza, altezza) della griglia di bit per una mappa w x h quadretti."""
    return _SUB * w + _MARGIN, _SUB * h + _MARGIN


def encode_cave_bitmap(sub: list[list[int]], w: int, h: int) -> str:
    """Griglia di sotto-celle -> stringa PoolByteArray."""
    width, height = cave_grid_shape(w, h)
    if len(sub) != height or any(len(row) != width for row in sub):
        raise ValueError(f"la griglia deve essere {width}x{height} sotto-celle")
    data = bytearray((width * height + 7) // 8)
    for y in range(height):
        for x in range(width):
            if sub[y][x]:
                i = y * width + x
                data[i // 8] |= 1 << (i % 8)
    return "PoolByteArray( " + ", ".join(str(b) for b in data) + " )"


def decode_cave_bitmap(blob: str, w: int, h: int) -> list[list[int]]:
    """Inverso di encode_cave_bitmap, usato per verificare il round-trip."""
    width, height = cave_grid_shape(w, h)
    inner = blob[blob.index("(") + 1 : blob.rindex(")")].strip()
    data = [int(x) for x in inner.split(",")] if inner else []
    return [
        [(data[(y * width + x) // 8] >> ((y * width + x) % 8)) & 1 for x in range(width)]
        for y in range(height)
    ]


def _empty_sub_grid(w: int, h: int) -> list[list[int]]:
    width, height = cave_grid_shape(w, h)
    return [[0] * width for _ in range(height)]


def build_walls(*, seed: int) -> dict:
    """Alternativa 1: contorno come muro poligonale chiuso."""
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)

    grid = generate_cave_grid(width=_CAVE_W, height=_CAVE_H, seed=seed)
    contour = extract_contour(grid)
    points_grid = [(x + _OFFSET_X, y + _OFFSET_Y) for x, y in contour]

    catalog = load_catalog()
    palette = palette_for("cave", catalog)

    add_polygon_pattern(level, ids, points_grid, palette.floor)
    add_wall(level, ids, points_grid, palette.wall, loop=True)

    finalize(prepared, ids)
    return prepared


def build_native(*, seed: int) -> dict:
    """Alternativa 2: stesso CA, ma girato a risoluzione sotto-cella e
    scritto nel layer cave nativo. Nessun muro, nessun pattern."""
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    world = prepared["world"]
    w, h = world["width"], world["height"]
    level = world["levels"]["0"]

    cave = generate_cave_grid(
        width=_CAVE_W * _SUB, height=_CAVE_H * _SUB, seed=seed
    )
    sub = _empty_sub_grid(w, h)
    for y, row in enumerate(cave):
        for x, open_cell in enumerate(row):
            if open_cell == 0:  # 0 = aperto nel CA, 1 = scavato nel bitmap
                sub[y + _OFFSET_Y * _SUB][x + _OFFSET_X * _SUB] = 1

    level["cave"]["bitmap"] = encode_cave_bitmap(sub, w, h)
    finalize(prepared, IdAllocator.from_document(prepared))
    return prepared


# Rettangolo di calibrazione: angolo alto-sinistro sul quadretto (10, 10),
# largo 10 e alto 5 quadretti ESATTI. Se l'origine della griglia sotto-cella
# e quella assunta (sotto-cella 0 = quadretto 0), in Dungeondraft il
# rettangolo deve partire esattamente a 10 quadretti dal bordo sinistro e 10
# dal bordo alto. Uno scostamento rivela che le 3 sotto-celle di margine
# stanno in testa invece che in coda.
_CALIB = (10, 10, 10, 5)


def build_calibration() -> dict:
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    world = prepared["world"]
    w, h = world["width"], world["height"]
    level = world["levels"]["0"]

    x0, y0, rect_w, rect_h = _CALIB
    sub = _empty_sub_grid(w, h)
    for y in range(y0 * _SUB, (y0 + rect_h) * _SUB):
        for x in range(x0 * _SUB, (x0 + rect_w) * _SUB):
            sub[y][x] = 1

    level["cave"]["bitmap"] = encode_cave_bitmap(sub, w, h)
    assert decode_cave_bitmap(level["cave"]["bitmap"], w, h) == sub
    finalize(prepared, IdAllocator.from_document(prepared))
    return prepared


_MODES = {"walls": "cave_spike", "native": "cave_native", "calib": "cave_native_calib"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=sorted(_MODES), default="walls")
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    if args.mode == "walls":
        doc = build_walls(seed=args.seed)
    elif args.mode == "native":
        doc = build_native(seed=args.seed)
    else:
        doc = build_calibration()

    out = args.out or DEFAULT_OUT.with_name(f"{_MODES[args.mode]}.dungeondraft_map")
    out.parent.mkdir(parents=True, exist_ok=True)
    save(doc, out)
    print(f"Scritto {out}")


if __name__ == "__main__":
    main()
