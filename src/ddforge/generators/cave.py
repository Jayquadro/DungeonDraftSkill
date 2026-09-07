"""Grotte: cellular automata a risoluzione sotto-cella, layer cave nativo.

Vedi docs/SPEC.md §9.3 e la decisione presa nello spike TASK-31
(`decision-1`): il layer cave nativo di Dungeondraft si scrive come una
maschera bit-packed (docs/format.md §14, `ddforge.cave_bitmap`), non come
muri poligonali. Per sfruttare la risoluzione 4x del formato, il cellular
automata gira direttamente sulla griglia di sotto-celle
`(4*width+3) x (4*height+3)`, non su una griglia a un quadretto per cella:
e per questo che il risultato finisce in `Blueprint.cave_grid` invece che
in `Blueprint.rooms`/`corridors` (una grotta non ha stanze rettangolari con
muri, vedi model.py).

Le fognature (SPEC.md §9.3, variante a canali ortogonali) sono TASK-33, non
questo file.
"""

import random

from ddforge.cave_bitmap import cave_grid_shape
from ddforge.model import Blueprint

_FILL_PROB = 0.45
_ITERATIONS = 5
# Area minima (in sotto-celle) perche una componente secondaria riceva un
# tunnel invece di essere scartata come rumore: 16 sotto-celle e l'area di
# UN quadretto a risoluzione 4x, cioe il piu piccolo ambiente che vale la
# pena rendere raggiungibile.
_MIN_COMPONENT_SIZE = 16
# Larghezza costante del tunnel in sotto-celle (~0.75 quadretti): abbastanza
# per essere percorribile, meno di un quadretto pieno perche un tunnel di
# raccordo non deve competere visivamente con le caverne che collega.
_TUNNEL_WIDTH = 3


def _initial_grid(width: int, height: int, rng: random.Random, fill_prob: float) -> list[list[int]]:
    """1 = roccia, 0 = aperto. Bordo sempre roccia: la grotta non deve mai
    toccare il limite della griglia di sotto-celle (che include le 3
    sotto-celle di margine del formato, docs/format.md §14)."""
    grid = [[1 if rng.random() < fill_prob else 0 for _ in range(width)] for _ in range(height)]
    for x in range(width):
        grid[0][x] = grid[height - 1][x] = 1
    for y in range(height):
        grid[y][0] = grid[y][width - 1] = 1
    return grid


def _wall_neighbors(grid: list[list[int]], x: int, y: int, width: int, height: int) -> int:
    """Vicini di Moore (8-connessi). Fuori griglia conta come roccia."""
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


def _smooth(grid: list[list[int]], width: int, height: int) -> list[list[int]]:
    """Una iterazione della regola B5/S4 (SPEC.md §9.3): >=5 vicini roccia
    -> roccia, <=3 -> aperto, 4 invariato."""
    new_grid = [row[:] for row in grid]
    for y in range(height):
        for x in range(width):
            n = _wall_neighbors(grid, x, y, width, height)
            if n >= 5:
                new_grid[y][x] = 1
            elif n <= 3:
                new_grid[y][x] = 0
    for x in range(width):
        new_grid[0][x] = new_grid[height - 1][x] = 1
    for y in range(height):
        new_grid[y][0] = new_grid[y][width - 1] = 1
    return new_grid


def _neighbors4(x: int, y: int, width: int, height: int):
    if x > 0:
        yield x - 1, y
    if x < width - 1:
        yield x + 1, y
    if y > 0:
        yield x, y - 1
    if y < height - 1:
        yield x, y + 1


def _label_components(grid: list[list[int]], width: int, height: int) -> list[list[tuple[int, int]]]:
    """Componenti 4-connesse di celle aperte (0), in ordine di scansione
    riga per riga: deterministico a parita di griglia, non dipende da rng."""
    seen = [[False] * width for _ in range(height)]
    components: list[list[tuple[int, int]]] = []
    for sy in range(height):
        for sx in range(width):
            if grid[sy][sx] != 0 or seen[sy][sx]:
                continue
            stack = [(sx, sy)]
            seen[sy][sx] = True
            cells = []
            while stack:
                x, y = stack.pop()
                cells.append((x, y))
                for nx, ny in _neighbors4(x, y, width, height):
                    if not seen[ny][nx] and grid[ny][nx] == 0:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            components.append(cells)
    return components


def _boundary_cells(cells: list[tuple[int, int]], grid: list[list[int]], width: int, height: int) -> list[tuple[int, int]]:
    """Le celle della componente adiacenti a roccia: i soli candidati utili
    per l'estremo di un tunnel (partire da dentro la componente non
    accorcerebbe il percorso, e il bordo e sempre roccia, mai griglia
    esterna, dato che grid[0]/[−1] sono forzate a roccia)."""
    boundary = []
    for x, y in cells:
        if any(grid[ny][nx] == 1 for nx, ny in _neighbors4(x, y, width, height)):
            boundary.append((x, y))
    return boundary


def _closest_pair(
    cells_a: list[tuple[int, int]], cells_b: list[tuple[int, int]]
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Coppia piu vicina (euclidea) fra due insiemi di celle. Ordinamento
    esplicito dei candidati prima del confronto: a parita di distanza vince
    la coppia lessicograficamente minore, riproducibile indipendentemente
    dall'ordine con cui le celle sono state scoperte dal flood fill."""
    sorted_a, sorted_b = sorted(cells_a), sorted(cells_b)
    best_pair = (sorted_a[0], sorted_b[0])
    best_key = None
    for a in sorted_a:
        for b in sorted_b:
            d = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            key = (d, a, b)
            if best_key is None or key < best_key:
                best_key = key
                best_pair = (a, b)
    return best_pair


def _elbow_spine(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    """Percorso a L da `a` a `b`: prima orizzontale (a quota a.y), poi
    verticale (sulla colonna b.x). Ciascuna delle due gambe e monotona e non
    condivide celle con l'altra (la gamba verticale riparte da a.y +/- 1,
    mai da a.y): un percorso semplice per costruzione, nessuna
    autointersezione possibile (AC2)."""
    ax, ay = a
    bx, by = b
    points = []
    step_x = 1 if bx >= ax else -1
    for x in range(ax, bx + step_x, step_x):
        points.append((x, ay))
    step_y = 1 if by >= ay else -1
    for y in range(ay + step_y, by + step_y, step_y):
        points.append((bx, y))
    return points


def _carve_tunnel(
    grid: list[list[int]], width: int, height: int, spine: list[tuple[int, int]], tunnel_width: int
) -> None:
    """Scava (mette a 0) un intorno quadrato di lato `tunnel_width` attorno
    a ogni punto dello spine, restando dentro il bordo di roccia (mai sulla
    riga/colonna 0 o width-1/height-1): la larghezza e la stessa in ogni
    punto del percorso, per costruzione (AC2)."""
    half = tunnel_width // 2
    for x, y in spine:
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                nx, ny = x + dx, y + dy
                if 1 <= nx <= width - 2 and 1 <= ny <= height - 2:
                    grid[ny][nx] = 0


def _dig_tunnels(
    grid: list[list[int]], width: int, height: int, *, min_component_size: int, tunnel_width: int
) -> list[list[tuple[int, int]]]:
    """Etichetta le componenti aperte, tiene la piu grande, scava un tunnel
    verso ciascuna delle altre sopra `min_component_size` (SPEC.md §9.3) e
    scarta (riempie di roccia) quelle piu piccole. Muta `grid` sul posto e
    ritorna gli spine dei tunnel scavati, per l'ispezione nei test (AC2)."""
    components = _label_components(grid, width, height)
    if not components:
        return []

    main = max(components, key=len)
    main_boundary = _boundary_cells(main, grid, width, height)

    tunnels = []
    for component in components:
        if component is main:
            continue
        if len(component) < min_component_size:
            for x, y in component:
                grid[y][x] = 1
            continue
        comp_boundary = _boundary_cells(component, grid, width, height)
        a, b = _closest_pair(comp_boundary, main_boundary)
        spine = _elbow_spine(a, b)
        _carve_tunnel(grid, width, height, spine, tunnel_width)
        tunnels.append(spine)
    return tunnels


def _to_cave_grid(grid: list[list[int]]) -> list[list[int]]:
    """Inverte la convenzione: qui 1=roccia/0=aperto (SPEC.md §9.3), ma
    `cave_bitmap`/`Blueprint.cave_grid` vogliono 1=scavato/0=roccia intatta
    (docs/format.md §14)."""
    return [[1 - v for v in row] for row in grid]


def generate(
    *, width: int, height: int, seed: int,
    fill_prob: float = _FILL_PROB, iterations: int = _ITERATIONS,
    min_component_size: int = _MIN_COMPONENT_SIZE, tunnel_width: int = _TUNNEL_WIDTH,
    **params,
) -> Blueprint:
    """Genera una grotta (SPEC.md §9.3). RNG locale da `seed` (TASK-20): mai
    il modulo `random` globale. `width`/`height` sono in quadretti, come
    negli altri generatori; la griglia di lavoro e a risoluzione sotto-cella
    (`ddforge.cave_bitmap.cave_grid_shape`)."""
    rng = random.Random(seed)
    grid_w, grid_h = cave_grid_shape(width, height)

    grid = _initial_grid(grid_w, grid_h, rng, fill_prob)
    for _ in range(iterations):
        grid = _smooth(grid, grid_w, grid_h)
    _dig_tunnels(grid, grid_w, grid_h, min_component_size=min_component_size, tunnel_width=tunnel_width)

    return Blueprint(
        width=width, height=height,
        rooms=[], corridors=[], graph={},
        seed=seed, style="cave",
        cave_grid=_to_cave_grid(grid),
    )
