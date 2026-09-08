"""Quartieri e citta: rete stradale, isolati, lotti, edifici e piazze.

Vedi docs/SPEC.md §9.4. A differenza di bsp.py/building.py, city.py non
produce un Blueprint a stanze: le stanze vive sono quelle di ciascun
edificio, che e a sua volta un Blueprint completo (prodotto riusando
generators/building.py "a un solo piano", building_type="house") gia
tradotto in coordinate assolute della mappa cittadina. Vedi model.Blueprint
per i tre campi dedicati (streets, plazas, buildings) e compose.py per
render_city_blueprint, che li disegna.

Semplificazione nota, non risolta qui: l'ingresso di un edificio prodotto da
building.py e sempre sul lato "sud" locale (bsp._ensure_entry forza la porta
sul lato la cui y2 e piu vicina al bordo del footprint). Per i lotti
ricavati da isolati piu larghi che alti (front=_BOTTOM) l'ingresso finisce
quindi correttamente sul lato fronte-strada; per i lotti ricavati da isolati
piu alti che larghi (front=_RIGHT) l'ingresso resta sul lato sud del lotto,
che qui e un muro cieco fra lotti (party wall), non il lato fronte. Ruotare
la geometria dell'edificio (Rect + Door.wall_index + Door.t) risolverebbe,
ma nessun acceptance criteria di TASK-35 lo richiede esplicitamente
("nessun edificio e inaccessibile" resta vero: l'edificio ha comunque una
porta funzionante, generata da building.py, solo non necessariamente rivolta
alla strada) e il rischio di un bug di orientamento silenzioso (esattamente
la classe di difetti vista ai gate umani M1/M3) non vale la pena senza un
riscontro visivo di Jay. Annotato anche nelle note di implementazione del
task.
"""

import random

from ddforge.generators import building
from ddforge.model import Blueprint, Corridor, Door, Rect, Room

# Stessa convenzione di compose.py (_TOP=0, _RIGHT=1, _BOTTOM=2, _LEFT=3):
# non importata da li perche privata al modulo, ma i valori devono restare
# gli stessi indici usati da _draw_perimeter/Door.wall_index. _LEFT (3) non
# e mai usato come front_side (vedi _split_into_lots), solo TOP/RIGHT/BOTTOM.
_TOP, _RIGHT, _BOTTOM = 0, 1, 2

# Larghezza della via principale: sempre maggiore del range delle strade
# secondarie (AC3), per costruzione, non per caso del seed.
_MAIN_STREET_WIDTH = 5.0
_SECONDARY_STREET_RANGE = (2.0, 4.0)  # SPEC.md §9.4

# Un isolato smette di dividersi quando entrambi i lati stanno sotto
# _MAX_BLOCK (a meno che non ci stia comunque una via, vedi _split_with_gap);
# non si divide MAI sotto _MIN_BLOCK per lato, per lasciare spazio a lotti
# veri (building.generate ha bisogno di margine per vano scale + stanza
# minima, vedi _MIN_BUILDING_SIDE).
_MIN_BLOCK = 10.0
_MAX_BLOCK = 16.0
_DEPTH_MAX = 6

# Lunghezza-bersaglio di un lotto lungo l'asse della striscia (facciata sulla
# via): ne entrano quanti ci stanno interi nell'isolato, mai sotto
# _MIN_LOT_LEN.
_TARGET_LOT_LEN = 11.0
_MIN_LOT_LEN = 8.0

# Margine fisso sui lati non-fronte (pareti in comune col lotto accanto o
# retro) e range dell'arretramento casuale sul lato fronte (AC1 "arretramento
# casuale dal fronte"). Building.generate riserva gia 1 quadretto di margine
# tutto intorno al proprio footprint locale: questi si sommano a quello.
_SIDE_MARGIN = 0.75
_SETBACK_RANGE = (0.5, 2.5)

# Sotto questo lato (larghezza o altezza passata a building.generate), il
# lotto non ha spazio per vano scale (2) + una stanza minima (min_room=3) +
# margine interno: l'edificio viene semplicemente saltato invece di
# generarne uno rotto o troppo compresso.
_MIN_BUILDING_SIDE = 8


def _split_with_gap(rect: Rect, rng: random.Random, gap_width: float, min_block: float):
    """Taglia `rect` lungo l'asse piu lungo, riservando `gap_width` fra le
    due meta (una strada). None se non c'e spazio per due isolati di almeno
    `min_block` piu la strada: il chiamante allora lascia `rect` cosi com'e,
    anche se supera _MAX_BLOCK (meglio un isolato grande che nessuno)."""
    vertical_cut = rect.w >= rect.h  # taglia lungo x, isolati affiancati in orizzontale
    span = rect.w if vertical_cut else rect.h
    if span < 2 * min_block + gap_width:
        return None
    lo = min_block
    hi = span - gap_width - min_block
    frac = rng.uniform(0.35, 0.65)
    gap_start = min(max(span * frac, lo), hi)

    if vertical_cut:
        x0 = rect.x1 + gap_start
        rect_a = Rect(rect.x1, rect.y1, x0, rect.y2)
        street = Rect(x0, rect.y1, x0 + gap_width, rect.y2)
        rect_b = Rect(x0 + gap_width, rect.y1, rect.x2, rect.y2)
    else:
        y0 = rect.y1 + gap_start
        rect_a = Rect(rect.x1, rect.y1, rect.x2, y0)
        street = Rect(rect.x1, y0, rect.x2, y0 + gap_width)
        rect_b = Rect(rect.x1, y0 + gap_width, rect.x2, rect.y2)
    return rect_a, street, rect_b


def _build_blocks(
    rect: Rect, rng: random.Random, *, depth: int, streets: list,
    min_block: float, max_block: float, main_width: float,
    secondary_range: tuple, depth_max: int,
) -> list:
    """Partizione ricorsiva del canvas in isolati (SPEC.md §9.4 punto 1).

    Il taglio di profondita 0 e sempre la via principale (AC3); i successivi
    usano una larghezza secondaria casuale in `secondary_range`. Si continua
    a tagliare finche un isolato supera `max_block` su un lato, o finche
    `depth_max` blocca la ricorsione (rete di sicurezza, non atteso in
    pratica con canvas ragionevoli). Le strade generate finiscono in
    `streets` (mutato in posto, stessa convenzione di bsp._connect_subtree
    per `corridors`)."""
    oversized = rect.w > max_block or rect.h > max_block
    if depth >= depth_max or not (oversized or depth == 0):
        return [rect]

    gap_width = main_width if depth == 0 else rng.uniform(*secondary_range)
    split = _split_with_gap(rect, rng, gap_width, min_block)
    if split is None:
        return [rect]
    rect_a, street, rect_b = split
    streets.append(street)

    children = []
    for child_rect in (rect_a, rect_b):
        children.extend(_build_blocks(
            child_rect, rng, depth=depth + 1, streets=streets,
            min_block=min_block, max_block=max_block, main_width=main_width,
            secondary_range=secondary_range, depth_max=depth_max,
        ))
    return children


def _split_into_lots(block: Rect, target_len: float, min_lot_len: float) -> list:
    """Suddivide un isolato in lotti a striscia lungo il lato piu lungo
    (SPEC.md §9.4 punto 2): ogni striscia copre per intero il lato corto
    dell'isolato, quindi i suoi due lati corti coincidono sempre con un
    bordo dell'isolato (una via, o il margine esterno della mappa - vedi
    nota di modulo). E' cosi che ogni lotto ha fronte strada per
    costruzione (AC1), non per verifica a posteriori.

    Ritorna una lista di (lot_rect, front_side): front_side e sempre lo
    stesso lato per tutte le strisce di un isolato (BOTTOM se le strisce
    sono verticali, RIGHT se orizzontali), perche entrambi i lati corti di
    ogni striscia toccano comunque il bordo dell'isolato."""
    vertical_strips = block.w >= block.h
    span = block.w if vertical_strips else block.h
    n = max(1, round(span / target_len))
    while n > 1 and span / n < min_lot_len:
        n -= 1

    front_side = _BOTTOM if vertical_strips else _RIGHT
    lots = []
    for i in range(n):
        a = span * i / n
        b = span * (i + 1) / n
        if vertical_strips:
            lot = Rect(block.x1 + a, block.y1, block.x1 + b, block.y2)
        else:
            lot = Rect(block.x1, block.y1 + a, block.x2, block.y1 + b)
        lots.append((lot, front_side))
    return lots


def _translate_rect(rect: Rect, dx: float, dy: float) -> Rect:
    return Rect(rect.x1 + dx, rect.y1 + dy, rect.x2 + dx, rect.y2 + dy)


def _translate_blueprint(bp: Blueprint, dx: float, dy: float) -> Blueprint:
    """Trasla un Blueprint di edificio (Rect/Corridor sono frozen: bisogna
    ricostruirli). Le porte non si toccano: Door.wall_index/t sono relativi
    al muro della propria stanza, non cambiano con una traslazione."""
    rooms = [
        Room(
            rect=_translate_rect(r.rect, dx, dy), kind=r.kind, name=r.name,
            doors=[Door(wall_index=d.wall_index, t=d.t, kind=d.kind, locked=d.locked) for d in r.doors],
            floor=r.floor, lights=[(x + dx, y + dy) for x, y in r.lights], level=r.level,
        )
        for r in bp.rooms
    ]
    corridors = [
        Corridor(c.x1 + dx, c.y1 + dy, c.x2 + dx, c.y2 + dy, horizontal=c.horizontal)
        for c in bp.corridors
    ]
    stairs_rect = _translate_rect(bp.stairs_rect, dx, dy) if bp.stairs_rect is not None else None
    return Blueprint(
        width=bp.width, height=bp.height, rooms=rooms, corridors=corridors,
        graph=bp.graph, seed=bp.seed, style=bp.style, levels=bp.levels, stairs_rect=stairs_rect,
    )


def _place_building(lot: Rect, front_side: int, rng: random.Random, seed: int) -> Blueprint | None:
    """Genera un edificio a un piano (building.py, building_type='house') e
    lo posiziona dentro `lot`: margine fisso sui lati non-fronte, arretramento
    casuale su quello fronte (AC1). None se il lotto e troppo piccolo per
    contenerne uno (_MIN_BUILDING_SIDE): si salta il lotto, non si forza un
    edificio spezzato."""
    setback = rng.uniform(*_SETBACK_RANGE)

    if front_side in (_TOP, _BOTTOM):
        x1, x2 = lot.x1 + _SIDE_MARGIN, lot.x2 - _SIDE_MARGIN
        if front_side == _BOTTOM:
            y1, y2 = lot.y1 + _SIDE_MARGIN, lot.y2 - setback
        else:
            y1, y2 = lot.y1 + setback, lot.y2 - _SIDE_MARGIN
    else:
        y1, y2 = lot.y1 + _SIDE_MARGIN, lot.y2 - _SIDE_MARGIN
        if front_side == _RIGHT:
            x1, x2 = lot.x1 + _SIDE_MARGIN, lot.x2 - setback
        else:
            x1, x2 = lot.x1 + setback, lot.x2 - _SIDE_MARGIN

    width, height = int(x2 - x1), int(y2 - y1)
    if width < _MIN_BUILDING_SIDE or height < _MIN_BUILDING_SIDE:
        return None

    bp = building.generate(width=width, height=height, seed=seed, building_type="house")
    return _translate_blueprint(bp, x1, y1)


def generate(
    *, width: int, height: int, seed: int,
    main_street_width: float = _MAIN_STREET_WIDTH,
    street_width_range: tuple = _SECONDARY_STREET_RANGE,
    min_block: float = _MIN_BLOCK, max_block: float = _MAX_BLOCK, depth_max: int = _DEPTH_MAX,
    target_lot_len: float = _TARGET_LOT_LEN, min_lot_len: float = _MIN_LOT_LEN,
    **params,
) -> Blueprint:
    """Genera un quartiere/citta (SPEC.md §9.4). RNG locale da `seed`, mai
    il modulo `random` globale (stesso vincolo degli altri generatori).

    rooms/corridors restano vuoti (city.py non e a stanze, vedi model.py):
    la geometria vive in streets/plazas/buildings."""
    rng = random.Random(seed)
    root = Rect(1, 1, width - 1, height - 1)

    streets: list[Rect] = []
    blocks = _build_blocks(
        root, rng, depth=0, streets=streets, min_block=min_block, max_block=max_block,
        main_width=main_street_width, secondary_range=street_width_range, depth_max=depth_max,
    )

    n_plazas = 2 if len(blocks) >= 4 else (1 if len(blocks) >= 2 else 0)
    plaza_indices = set(rng.sample(range(len(blocks)), n_plazas)) if n_plazas else set()
    plazas = [blocks[i] for i in sorted(plaza_indices)]

    buildings: list[Blueprint] = []
    for i, block in enumerate(blocks):
        if i in plaza_indices:
            continue
        for lot, front in _split_into_lots(block, target_lot_len, min_lot_len):
            placed = _place_building(lot, front, rng, seed=rng.randrange(1 << 30))
            if placed is not None:
                buildings.append(placed)

    return Blueprint(
        width=width, height=height, rooms=[], corridors=[], graph={},
        seed=seed, style="city", streets=streets, plazas=plazas, buildings=buildings,
    )
