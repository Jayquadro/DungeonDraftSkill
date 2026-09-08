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
from collections import deque

from ddforge.cave_bitmap import cave_grid_shape
from ddforge.model import Blueprint

_FILL_PROB = 0.45
_ITERATIONS = 5
# Raggio (Chebyshev, in sotto-celle) dell'apertura morfologica (erosione +
# dilatazione) che isola le "camere" larghe dal resto del CA (TASK-36,
# round 2 del gate M5): il CA a queste iterazioni produce sempre forme
# sfrangiate/serpeggianti (rapporto area/bounding-box ~0.3-0.45, stabile
# anche con molte piu iterazioni, verificato empiricamente), che si
# leggono come corridoi e non come stanze. L'apertura elimina qualunque
# propaggine piu stretta di 2*_OPEN_RADIUS+1 sotto-celle mantenendo intatto
# il resto del contorno: cio' che sopravvive sono i nuclei davvero larghi.
#
# fill_prob abbassato a 0.48/raggio 3 nel round 3 (camere troppo piccole
# rispetto ai tunnel), poi fill_prob riportato a 0.45/raggio alzato a 4 nel
# round 4 ("alcune stanze possono essere molto piu grandi"): un CA grezzo
# di partenza (a 0.45 e' lo STESSO fill_prob dello sprawling del round 1 —
# ma ora l'apertura, non ancora presente al round 1, lo spezza comunque in
# decine di camere separate, verificato su 7 seed) forma blob di partenza
# molto piu grandi; un raggio piu ampio (4, scarta propaggini piu strette
# di 9 sotto-celle) li arrotonda comunque a sufficienza (rapporto
# area/bounding-box medio 0.66-0.71). Risultato: la stessa camera minima
# di prima (15 quadretti) ma una coda di camere molto piu grandi (fino a
# ~130 quadretti, contro il tetto di ~55 del round 3), nessuna delle quali
# supera il ~11% dell'area totale delle camere (niente domina la mappa).
_OPEN_RADIUS = 4
# Area minima (in sotto-celle) perche una componente APERTA (dopo
# l'apertura morfologica) sia tenuta come "camera": 240 sotto-celle = 15
# quadretti (round 3: alzata da 4 quadretti, troppo piccola rispetto ai
# tunnel di collegamento — vedi sopra). Soglia ASSOLUTA (non una frazione
# dell'area mappa): a questi fill_prob/raggio il CA si frammenta gia' in
# decine di nuclei larghi indipendenti dalla dimensione della griglia
# (verificato su 24x18 e 80x80), quindi la stessa soglia in quadretti
# resta sensata a qualunque scala (il difetto di TASK-44: a
# fill_prob=0.45 SENZA apertura — round 1 — sopravviveva un'unica
# componente sprawling che copriva quasi tutta la mappa, e nessuna soglia
# fissa poteva "tagliarla" perche il problema era la forma della
# componente, non la soglia; con l'apertura lo stesso fill_prob non e'
# piu un problema, vedi sopra).
_MIN_COMPONENT_SIZE = 240
# "Almeno un paio di stanze molto grandi" (TASK-36, round 5 del gate M5):
# le _GRAND_COUNT camere piu grandi vengono re-isolate con un'apertura piu
# gentile (_GRAND_RADIUS < _OPEN_RADIUS, quindi meno area erosa) sulla
# STESSA griglia grezza, invece di accontentarsi della coda naturale delle
# camere standard. _GRAND_RADIUS=3 (contro lo standard 4) recupera camere
# di 150-450 quadretti (contro i 70-130 dello standard), sempre larghe in
# entrambe le dimensioni (mai piu strette di ~14 quadretti, verificato su
# 7 seed — non e' il regime "corridoio" del round 2 nonostante il rapporto
# area/bounding-box piu basso, ~0.30-0.48: un contorno frastagliato su
# una camera enorme resta comunque larga, a differenza di un corridoio
# stretto). _GRAND_RADIUS=2 e' gia troppo gentile: recupera un'unica area
# quasi sprawling (2400-3200 quadretti), lo stesso difetto del round 1.
_GRAND_RADIUS = 3
_GRAND_COUNT = 2
# Larghezza costante del tunnel in sotto-celle (~0.75 quadretti): abbastanza
# per essere percorribile, meno di un quadretto pieno perche un tunnel di
# raccordo non deve competere visivamente con le camere che collega.
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


def _sliding_extreme(values: list[int], window: int, take_min: bool) -> list[int]:
    """Min o max su ogni finestra scorrevole di lunghezza `window`, con una
    deque monotona: O(len(values)) invece di O(len(values) * window). Base
    di `_erode`/`_dilate`: un filtro box (Chebyshev) e' separabile in un
    passaggio 1D per riga seguito da un passaggio 1D per colonna."""
    dq: deque[int] = deque()
    out = []
    for i, v in enumerate(values):
        if take_min:
            while dq and values[dq[-1]] >= v:
                dq.pop()
        else:
            while dq and values[dq[-1]] <= v:
                dq.pop()
        dq.append(i)
        if dq[0] <= i - window:
            dq.popleft()
        if i >= window - 1:
            out.append(values[dq[0]])
    return out


def _box_filter(grid: list[list[int]], width: int, height: int, radius: int, *, take_min: bool) -> list[list[int]]:
    if radius == 0:
        return [row[:] for row in grid]
    window = 2 * radius + 1
    pad = [1] * radius
    row_pass = [_sliding_extreme(pad + grid[y] + pad, window, take_min) for y in range(height)]
    result = [[1] * width for _ in range(height)]
    for x in range(width):
        column = pad + [row_pass[y][x] for y in range(height)] + pad
        filtered = _sliding_extreme(column, window, take_min)
        for y in range(height):
            result[y][x] = filtered[y]
    return result


def _erode(grid: list[list[int]], width: int, height: int, radius: int) -> list[list[int]]:
    """Erosione morfologica (Chebyshev) = filtro MAX: una cella aperta
    sopravvive solo se OGNI cella entro `radius` e' anch'essa aperta (0=
    aperto, quindi max=0 solo se non c'e' roccia nella finestra). Isola il
    "nucleo" di un'area larga almeno 2*radius+1 sotto-celle, qualunque sia
    la sua forma — le propaggini piu strette spariscono."""
    return _box_filter(grid, width, height, radius, take_min=False)


def _dilate(grid: list[list[int]], width: int, height: int, radius: int) -> list[list[int]]:
    """Dilatazione morfologica (Chebyshev) = filtro MIN: una cella apre se
    ESISTE una cella aperta entro `radius` (min=0 se almeno una cella della
    finestra e' aperta). Applicata a un nucleo eroso, lo riporta al suo
    ingombro originale con i bordi arrotondati (erosione + dilatazione =
    apertura morfologica)."""
    return _box_filter(grid, width, height, radius, take_min=True)


def _extract_rooms(
    grid: list[list[int]], width: int, height: int, *, radius: int, min_room_size: int,
    grand_radius: int = 0, grand_count: int = 0,
) -> list[list[int]]:
    """Isola le "camere" larghe dal CA grezzo (TASK-36, round 2 del gate
    M5): il CA a fill_prob/iterations fissi produce sempre forme sfrangiate
    che si leggono come corridoi, non come stanze (rapporto area/bounding-
    box ~0.3-0.45, verificato empiricamente stabile anche con molte piu
    iterazioni — non e' un problema risolvibile ricalibrando i parametri
    del CA). Un'apertura morfologica (erosione poi dilatazione) elimina
    ogni propaggine piu stretta di 2*radius+1 sotto-celle, lasciando solo i
    nuclei davvero larghi (rapporto area/bounding-box tipicamente
    0.6-0.95 dopo l'apertura).

    Se nessuna componente aperta raggiunge `min_room_size`, riprova con un
    raggio piu piccolo (una mappa stretta puo non avere nulla di largo
    quanto il raggio pieno); se anche a raggio 0 (nessuna apertura) non
    sopravvive nulla, tiene comunque la componente piu grande del CA
    grezzo — la grotta non deve mai restare tutta roccia.

    Se `grand_count` > 0 (TASK-36, round 5 del gate M5 — "l'ottimo sarebbe
    che ci fossero almeno un paio di stanze molto grandi"), individua le
    `grand_count` camere piu grandi con un'apertura PIU GENTILE
    (`grand_radius` < `radius`: erode meno, quindi trattiene piu area del
    CA grezzo) sulla STESSA griglia grezza, e le fa vincere sulle camere
    standard che ricadono nella stessa zona. Un raggio troppo piccolo (es.
    2) recupera un'unica area quasi sprawling (lo stesso difetto del round
    1); `grand_radius` va scelto abbastanza piu piccolo di `radius` da
    recuperare camere nettamente piu grandi (misurato: 150-450 quadretti
    contro i 70-130 dello standard) ma abbastanza grande da restare
    comunque larghe in entrambe le dimensioni, mai strette come un
    corridoio (verificato sulle bounding box, non solo sull'area).

    Ritorna una griglia nuova (1=roccia/0=aperto) contenente SOLO le celle
    delle camere tenute: tutto il resto del CA (corridoi/rumore) e'
    scartato qui, non nel passo di collegamento (`_dig_tunnels`), che
    aggiunge poi i tunnel stretti fra le camere superstiti."""
    rooms: list[list[tuple[int, int]]] = []
    for r in range(radius, -1, -1):
        candidate = grid if r == 0 else _dilate(_erode(grid, width, height, r), width, height, r)
        components = _label_components(candidate, width, height)
        rooms = [c for c in components if len(c) >= min_room_size]
        if rooms:
            break

    if not rooms:
        components = _label_components(grid, width, height)
        if components:
            rooms = [max(components, key=len)]

    result = [[1] * width for _ in range(height)]
    for room in rooms:
        for x, y in room:
            result[y][x] = 0

    if grand_count > 0 and len(rooms) > grand_count:
        grand_candidate = _dilate(_erode(grid, width, height, grand_radius), width, height, grand_radius)
        grand_rooms = sorted(_label_components(grand_candidate, width, height), key=len, reverse=True)
        for room in grand_rooms[:grand_count]:
            for x, y in room:
                result[y][x] = 0

    return result


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
    """Etichetta le componenti aperte, tiene come "camere" quelle sopra
    `min_component_size` (se nessuna la raggiunge, tiene comunque la piu
    grande: la grotta non deve mai restare tutta roccia) e scarta
    (riempie di roccia) le altre come rumore.

    Le camere superstiti vengono collegate TUTTE fra loro con un albero
    di copertura minimo (Prim, su distanza euclidea fra i bordi piu
    vicini di ogni coppia): non solo quelle "vicine a una principale",
    perche non esiste piu un'unica componente dominante (TASK-36, round 1
    del gate M5 — a fill_prob piu basso la componente principale era
    un'unica area sprawling che copriva quasi tutta la mappa, non un
    insieme di camere leggibili). Un albero di copertura garantisce che il
    risultato sia una sola componente connessa (AC1) col minimo numero di
    tunnel, senza forzare una topologia a stella attorno a una camera
    arbitraria.

    Muta `grid` sul posto e ritorna gli spine dei tunnel scavati, per
    l'ispezione nei test (AC2)."""
    components = _label_components(grid, width, height)
    if not components:
        return []

    rooms = [c for c in components if len(c) >= min_component_size]
    if not rooms:
        rooms = [max(components, key=len)]

    kept_ids = {id(c) for c in rooms}
    for component in components:
        if id(component) not in kept_ids:
            for x, y in component:
                grid[y][x] = 1

    if len(rooms) <= 1:
        return []

    boundaries = [_boundary_cells(room, grid, width, height) for room in rooms]
    distance_cache: dict[tuple[int, int], tuple[int, tuple[int, int], tuple[int, int]]] = {}

    def closest_between(i: int, j: int) -> tuple[int, tuple[int, int], tuple[int, int]]:
        key = (i, j) if i < j else (j, i)
        if key not in distance_cache:
            a, b = _closest_pair(boundaries[i], boundaries[j])
            distance_cache[key] = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2, a, b)
        return distance_cache[key]

    in_tree = {0}
    tunnels = []
    while len(in_tree) < len(rooms):
        best = None
        for i in in_tree:
            for j in range(len(rooms)):
                if j in in_tree:
                    continue
                candidate = (*closest_between(i, j), j)
                if best is None or candidate[0] < best[0]:
                    best = candidate
        assert best is not None, "in_tree incompleto ma nessuna camera esterna trovata"
        _, a, b, joined = best
        spine = _elbow_spine(a, b)
        _carve_tunnel(grid, width, height, spine, tunnel_width)
        tunnels.append(spine)
        in_tree.add(joined)
    return tunnels


def _to_cave_grid(grid: list[list[int]]) -> list[list[int]]:
    """Inverte la convenzione: qui 1=roccia/0=aperto (SPEC.md §9.3), ma
    `cave_bitmap`/`Blueprint.cave_grid` vogliono 1=scavato/0=roccia intatta
    (docs/format.md §14)."""
    return [[1 - v for v in row] for row in grid]


def generate(
    *, width: int, height: int, seed: int,
    fill_prob: float = _FILL_PROB, iterations: int = _ITERATIONS,
    open_radius: int = _OPEN_RADIUS, min_component_size: int = _MIN_COMPONENT_SIZE,
    grand_radius: int = _GRAND_RADIUS, grand_count: int = _GRAND_COUNT,
    tunnel_width: int = _TUNNEL_WIDTH,
    **params,
) -> Blueprint:
    """Genera una grotta (SPEC.md §9.3). RNG locale da `seed` (TASK-20): mai
    il modulo `random` globale. `width`/`height` sono in quadretti, come
    negli altri generatori; la griglia di lavoro e a risoluzione sotto-cella
    (`ddforge.cave_bitmap.cave_grid_shape`).

    Il CA grezzo produce sempre forme sfrangiate (corridoi), non stanze
    larghe: `_extract_rooms` isola le camere vere con un'apertura
    morfologica prima che `_dig_tunnels` le colleghi (TASK-36, round 2 del
    gate M5 — vedi i due docstring per il perche'), e ne rende un paio
    molto piu grandi delle altre (round 5)."""
    rng = random.Random(seed)
    grid_w, grid_h = cave_grid_shape(width, height)

    grid = _initial_grid(grid_w, grid_h, rng, fill_prob)
    for _ in range(iterations):
        grid = _smooth(grid, grid_w, grid_h)
    rooms_grid = _extract_rooms(
        grid, grid_w, grid_h, radius=open_radius, min_room_size=min_component_size,
        grand_radius=grand_radius, grand_count=grand_count,
    )
    _dig_tunnels(rooms_grid, grid_w, grid_h, min_component_size=min_component_size, tunnel_width=tunnel_width)

    return Blueprint(
        width=width, height=height,
        rooms=[], corridors=[], graph={},
        seed=seed, style="cave",
        cave_grid=_to_cave_grid(rooms_grid),
    )
