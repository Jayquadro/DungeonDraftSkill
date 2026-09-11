"""Quartieri e citta: rete stradale, isolati, lotti, edifici e piazze.

Vedi docs/SPEC.md §9.4. A differenza di bsp.py/building.py, city.py non
produce un Blueprint a stanze: la geometria vive in streets/plazas piu uno
dei due campi dedicati agli edifici (vedi model.Blueprint), a seconda del
preset di scala scelto. Vedi compose.render_city_blueprint per il disegno.

Tre preset di scala (TASK-41, decision-2 e round 2 del gate umano, che ha
chiesto tre preset al posto dei due iniziali con questi nomi), non uno solo:

- "isolato" (default): 1 quadretto = 5 ft/1,5 m, la scala giocabile al
  tavolo - la mappa su cui si muovono le miniature. Ogni lotto riceve un
  edificio completo, cioe un Blueprint a se (prodotto riusando
  generators/building.py) gia tradotto in coordinate assolute della mappa
  cittadina, in blueprint.buildings.
- "quartiere": 1 quadretto = 1 edificio, un quartiere intero visto
  dall'alto. A questa scala un lotto misura ~3 quadretti mentre
  building.generate ne pretende almeno 6 per lato, quindi l'edificio non e
  un Blueprint ma un rettangolo di ingombro in blueprint.building_footprints
  - la "rappresentazione astratta" che decision-2 lascia esplicitamente da
  progettare a questo task.
- "citta": una citta intera, capace di contenere una decina di quartieri.
  Stessa rappresentazione astratta di "quartiere", tarata ~3,25x piu fitta
  in lineare (~10x in numero di edifici a parita di canvas, vedi la tabella
  SCALE_PRESETS): non e pensata per essere giocata al tavolo, e uno sfondo
  cittadino visto dall'alto.

Cambia solo la taratura geometrica: la costruzione e la stessa nei tre
preset, ed e per questo che sta in una tabella di costanti e non in
generatori distinti.

Come si tiene insieme "fronte strada garantito" e "strade irregolari"
(richiesta di Jay al primo round del gate): la partizione riserva a ogni via
un ingombro RETTANGOLARE, ed e quell'ingombro a garantire per costruzione che
nessun edificio finisca in mezzo alla strada. Il selciato disegnato e piu
stretto dell'ingombro, e la sua centro-linea serpeggia nello spazio che
avanza: la via si legge irregolare senza che nessuna garanzia geometrica
dipenda dalla forma del tracciato. Le vie oblique (_avenue) sono l'eccezione
dichiarata: non nascono da un taglio, quindi si fanno spazio togliendo gli
edifici che incontrano.

Semplificazione nota, non risolta qui (riguarda il solo preset
"isolato"): l'ingresso di un edificio prodotto da building.py e sempre sul
lato "sud" locale (bsp._ensure_entry forza la porta sul lato la cui y2 e
piu vicina al bordo del footprint), indipendentemente da quale lato del lotto
e il fronte-strada. L'edificio ha comunque una porta funzionante e il lotto
ha comunque fronte strada, ma la porta non guarda sempre la via. Ruotare la
geometria (Rect + Door.wall_index + Door.t) risolverebbe, ma il rischio di un
bug di orientamento silenzioso (la classe di difetti vista ai gate M1/M3) non
vale la pena senza un riscontro visivo di Jay.
"""

import math
import random
import zlib
from dataclasses import dataclass

from ddforge.generators import building, landmarks as lm
from ddforge.model import (
    Blueprint, Bridge, CityWalls, Corridor, Door, Gate, Landmark, Port, Rect, River, Room, Street,
)

# Stessa convenzione di compose.py (_TOP=0, _RIGHT=1, _BOTTOM=2, _LEFT=3):
# non importata da li perche privata al modulo, ma i valori devono restare
# gli stessi indici usati da _draw_perimeter/Door.wall_index. Tutti e quattro
# possono essere il fronte di un lotto: gli isolati profondi si dividono in
# DUE file di lotti schiena contro schiena, e la seconda fila ha il fronte sul
# lato opposto (vedi _split_into_lots).
_TOP, _RIGHT, _BOTTOM, _LEFT = 0, 1, 2, 3


@dataclass(frozen=True)
class ScalePreset:
    """Taratura geometrica di un preset di scala (TASK-41).

    Tutte le misure sono in quadretti. `abstract_buildings` decide quale dei
    due campi edificio di Blueprint viene popolato: False = un Blueprint
    completo per lotto via building.generate, True = un rettangolo di
    ingombro.
    """

    # Ingombro riservato alla via: il taglio di profondita 0 e la via
    # principale, sempre piu larga del massimo delle secondarie (AC3 di
    # TASK-35), per costruzione e non per caso del seed.
    main_street_width: float
    street_width_range: tuple[float, float]
    # Quanta parte dell'ingombro e davvero selciata. Il resto e il margine di
    # manovra in cui la centro-linea serpeggia: senza, la via sarebbe un
    # rettangolo perfetto (vedi _street_centerline).
    street_path_fraction: float
    # Passo fra due vertici della centro-linea: piu corto = via piu tortuosa.
    street_segment_len: float
    # Un isolato smette di dividersi quando entrambi i lati stanno sotto
    # max_block (a meno che non ci stia comunque una via, vedi
    # _split_with_gap); non si divide MAI sotto min_block per lato.
    min_block: float
    max_block: float
    depth_max: int
    # Lunghezza-bersaglio di un lotto lungo il fronte strada. Va tenuta
    # nettamente sotto min_block, altrimenti ogni isolato produce un lotto
    # solo e l'edificio diventa grande quanto l'isolato: e' il difetto che
    # Jay ha visto al primo round del gate.
    target_lot_len: float
    min_lot_len: float
    # Margine fisso sui lati non-fronte (pareti in comune col lotto accanto)
    # e range dell'arretramento casuale sul lato fronte (AC1 di TASK-35).
    side_margin: float
    setback_range: tuple[float, float]
    # Profondita dell'edificio misurata dal fronte strada. E' questo il
    # freno vero alla sua dimensione: senza, l'edificio riempie tutta la
    # profondita del lotto e viene una striscia lunga quanto l'isolato.
    building_depth_range: tuple[float, float]
    # Cortile minimo fra due file di lotti schiena contro schiena: sotto
    # questo, l'isolato resta a una fila sola.
    min_yard: float
    # Sotto questo lato il lotto non ha spazio per un edificio: viene
    # semplicemente saltato invece di generarne uno rotto o troppo compresso.
    min_building_side: float
    abstract_buildings: bool
    # Vie oblique: sono loro a rompere l'ortogonalita della rete stradale.
    avenues: int


SCALE_PRESETS: dict[str, ScalePreset] = {
    # Preset "isolato" (si chiamava "quartiere" prima del round 2 del gate,
    # che ha chiesto tre preset invece di due e ha rinominato i nomi
    # esistenti). Tarato al secondo round del gate umano: al primo round gli
    # edifici venivano 9,6x8,7 quadretti (181 m2, una villa non una casa) per
    # due cause, corrette entrambe qui - i lotti coincidevano con l'isolato
    # (target_lot_len 11 contro isolati 10-16, quindi una striscia sola per
    # isolato) e l'edificio riempiva tutta la profondita del lotto.
    "isolato": ScalePreset(
        main_street_width=5.0,
        street_width_range=(2.5, 4.0),  # SPEC.md §9.4
        street_path_fraction=0.65,
        street_segment_len=7.0,
        min_block=13.0,
        max_block=22.0,
        depth_max=6,
        target_lot_len=9.0,
        min_lot_len=7.0,
        # building.generate riserva gia 1 quadretto di margine tutto intorno
        # al proprio footprint locale: questi si sommano a quello.
        side_margin=0.5,
        setback_range=(0.5, 2.0),
        building_depth_range=(6.0, 9.0),
        min_yard=3.0,
        # Sotto 6 quadretti di lato building.generate non ha spazio per una
        # stanza minima (min_room=3) piu il suo margine interno.
        min_building_side=6.0,
        abstract_buildings=False,
        avenues=1,
    ),
    # Preset "quartiere" (si chiamava "citta" prima del round 2 del gate: un
    # quartiere intero e cio che il vecchio preset "citta" gia disegnava).
    # Tarato misurando su un canvas 78x78, cioe l'unico template di
    # produzione reale (templates/blank_80x80.dungeondraft_map, vedi
    # decision-2: prepare() non tocca mai world.width/height). Anche qui il
    # secondo round del gate ha dimezzato le dimensioni: al primo round ogni
    # edificio era una striscia ~2x6 lunga quanto l'isolato.
    "quartiere": ScalePreset(
        main_street_width=3.0,
        street_width_range=(1.4, 2.2),
        street_path_fraction=0.7,
        street_segment_len=4.0,
        min_block=6.0,
        max_block=11.0,
        # Piu profondo dell'isolato: servono piu tagli per scendere da un
        # canvas di ~76 quadretti a isolati di 6-11.
        depth_max=9,
        target_lot_len=3.0,
        min_lot_len=2.2,
        side_margin=0.25,
        setback_range=(0.15, 0.6),
        building_depth_range=(1.8, 3.0),
        min_yard=1.2,
        # Nessun vincolo da building.generate qui (l'edificio e un
        # rettangolo): solo la soglia sotto la quale un ingombro non si
        # leggerebbe piu come edificio in Dungeondraft.
        min_building_side=0.8,
        abstract_buildings=True,
        avenues=1,
    ),
    # Preset "citta" (nuovo al round 2 del gate: Jay ha chiesto una mappa
    # capace di contenere una decina di quartieri, non solo due preset). Ogni
    # costante e quella del preset "quartiere" scalata di un fattore lineare
    # ~3,25 (stessa rappresentazione astratta, abstract_buildings=True):
    # misurato su blank_80x80 78x78 su 7 seed, da ~9,6x a ~10,8x il numero di
    # edifici del preset "quartiere" a parita di canvas - "un ordine di
    # grandezza in piu" (AC4), zero sovrapposizioni/uscite dal canvas su
    # canvas 3x3..100x100. depth_max piu alto: isolati piccoli richiedono
    # piu tagli per riempire lo stesso canvas.
    "citta": ScalePreset(
        main_street_width=1.2,
        street_width_range=(0.55, 0.9),
        street_path_fraction=0.7,
        street_segment_len=1.25,
        min_block=1.85,
        max_block=3.4,
        depth_max=12,
        target_lot_len=0.9,
        min_lot_len=0.7,
        side_margin=0.08,
        setback_range=(0.05, 0.2),
        building_depth_range=(0.55, 0.9),
        min_yard=0.4,
        # Sotto questa soglia un ingombro non si leggerebbe piu come edificio
        # in Dungeondraft, nemmeno alla scala citta.
        min_building_side=0.25,
        abstract_buildings=True,
        avenues=1,
    ),
}

DEFAULT_SCALE = "isolato"

# Repertorio di edifici del preset "isolato" (richiesta di Jay: "non usare
# un unico oggetto per gli edifici ma usane di diversi tipi"). Ogni voce e
# (building_type, l_shaped, peso, lato minimo): il lato minimo tiene le
# tipologie multi-piano fuori dai lotti piu piccoli, dove non avrebbero
# spazio per il vano scale piu una stanza.
#
# Le soglie sono misurate sulla distribuzione reale dei lotti di questo
# preset, non scelte a occhio: su 8 seed a 78x78 il lato minore passato a
# building.generate vale 6 nel 53% dei casi, 7 nel 34%, 8 nel 9%. Con soglie
# piu alte (il primo tentativo dava 10 alle multi-piano e 8 alla pianta a L)
# NESSUNA tipologia oltre "house" risultava mai ammissibile e tutti gli
# edifici venivano identici — cioe esattamente il difetto segnalato da Jay.
#
# I pesi non devono sommare a 1: la scelta e normalizzata sulle voci
# ammissibili per quel lotto (vedi _choose_building_type), quindi una
# tipologia esclusa non fa "saltare il turno".
# Taratura della via obliqua, comune ai due preset perche espressa come
# multiplo delle loro costanti: i vertici stanno 3 volte piu distanti che su
# una via da taglio e lo scarto laterale e il 40% della larghezza della via
# principale. Valori piu aggressivi danno una via a tornanti, non una
# diagonale.
_AVENUE_SEGMENT_FACTOR = 3.0
_AVENUE_SWAY_FACTOR = 0.4

_BUILDING_REPERTOIRE: tuple[tuple[str, bool, float, float], ...] = (
    ("house", False, 0.44, 6.0),
    ("house", True, 0.20, 6.0),
    ("tavern", False, 0.14, 7.0),
    ("warehouse", False, 0.12, 7.0),
    ("manor", False, 0.10, 8.0),
)


def _split_with_gap(rect: Rect, rng: random.Random, gap_width: float, min_block: float):
    """Taglia `rect` lungo l'asse piu lungo, riservando `gap_width` fra le
    due meta (l'ingombro di una via). None se non c'e spazio per due isolati
    di almeno `min_block` piu la via: il chiamante allora lascia `rect` cosi
    com'e, anche se supera max_block (meglio un isolato grande che nessuno)."""
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
        gap = Rect(x0, rect.y1, x0 + gap_width, rect.y2)
        rect_b = Rect(x0 + gap_width, rect.y1, rect.x2, rect.y2)
    else:
        y0 = rect.y1 + gap_start
        rect_a = Rect(rect.x1, rect.y1, rect.x2, y0)
        gap = Rect(rect.x1, y0, rect.x2, y0 + gap_width)
        rect_b = Rect(rect.x1, y0 + gap_width, rect.x2, rect.y2)
    return rect_a, gap, rect_b


def _street_centerline(
    corridor: Rect, rng: random.Random, *, path_width: float, segment_len: float,
) -> list[tuple[float, float]]:
    """Centro-linea serpeggiante di una via, dentro il suo ingombro.

    Lo scarto laterale massimo e quel che avanza fra l'ingombro riservato e
    il selciato, diviso due: cosi il selciato resta dentro l'ingombro per
    costruzione, e le garanzie di TASK-35 (nessun edificio in mezzo alla
    strada, fronte strada su ogni lotto) non dipendono dal tracciato.

    I due estremi NON vengono spostati: e quello che tiene allineati gli
    incroci con le vie che si innestano sull'ingombro."""
    vertical = corridor.h >= corridor.w
    if vertical:
        start, end = corridor.y1, corridor.y2
        axis = (corridor.x1 + corridor.x2) / 2
        room = (corridor.w - path_width) / 2
    else:
        start, end = corridor.x1, corridor.x2
        axis = (corridor.y1 + corridor.y2) / 2
        room = (corridor.h - path_width) / 2
    room = max(0.0, room)

    steps = max(1, round(abs(end - start) / segment_len))
    points = []
    for i in range(steps + 1):
        along = start + (end - start) * i / steps
        offset = 0.0 if i in (0, steps) else rng.uniform(-room, room)
        points.append((axis + offset, along) if vertical else (along, axis + offset))
    return points


def _build_blocks(
    rect: Rect, rng: random.Random, *, depth: int, streets: list, preset: ScalePreset,
) -> list:
    """Partizione ricorsiva del canvas in isolati (SPEC.md §9.4 punto 1).

    Il taglio di profondita 0 e sempre la via principale (AC3); i successivi
    usano una larghezza secondaria casuale in `preset.street_width_range`.
    Si continua a tagliare finche un isolato supera `preset.max_block` su un
    lato, o finche `preset.depth_max` blocca la ricorsione (rete di
    sicurezza, non atteso in pratica con canvas ragionevoli). Le vie generate
    finiscono in `streets` (mutato in posto, stessa convenzione di
    bsp._connect_subtree per `corridors`)."""
    oversized = rect.w > preset.max_block or rect.h > preset.max_block
    if depth >= preset.depth_max or not (oversized or depth == 0):
        return [rect]

    main = depth == 0
    gap_width = preset.main_street_width if main else rng.uniform(*preset.street_width_range)
    split = _split_with_gap(rect, rng, gap_width, preset.min_block)
    if split is None:
        return [rect]
    rect_a, gap, rect_b = split

    path_width = gap_width * preset.street_path_fraction
    streets.append(Street(
        points=_street_centerline(
            gap, rng, path_width=path_width, segment_len=preset.street_segment_len,
        ),
        width=path_width, corridor=gap, main=main,
    ))

    children = []
    for child_rect in (rect_a, rect_b):
        children.extend(_build_blocks(
            child_rect, rng, depth=depth + 1, streets=streets, preset=preset,
        ))
    return children


def _lot_rows(depth: float, preset: ScalePreset) -> int:
    """Quante file di lotti stanno nella profondita di un isolato.

    Due file schiena contro schiena, con il cortile in mezzo, se l'isolato e
    abbastanza profondo: e cosi che un isolato profondo produce case affacciate
    su entrambe le vie che lo bordano invece di una sola striscia lunga quanto
    l'isolato. Il conto usa il MINIMO di arretramento e profondita edificio,
    non il massimo: _building_area sa comunque comprimere l'edificio nella
    profondita che trova."""
    row_depth = preset.building_depth_range[0] + preset.setback_range[0]
    return 2 if depth >= 2 * row_depth + preset.min_yard else 1


def _split_into_lots(block: Rect, preset: ScalePreset) -> list:
    """Suddivide un isolato in lotti con fronte strada garantito (SPEC.md
    §9.4 punto 2).

    Lavora in coordinate (u, v): `u` corre lungo il fronte strada, `v` entra
    nell'isolato. Le strisce tagliano `u`; le file (una o due, vedi
    _lot_rows) tagliano `v`. Il fronte di un lotto e sempre uno dei due lati
    dell'isolato ortogonali a `v`, che e sempre bordato da una via (o dal
    margine esterno della mappa, trattato come confine cittadino): e cosi che
    ogni lotto ha fronte strada per costruzione, non per verifica a
    posteriori.

    Ritorna una lista di (lot_rect, front_side)."""
    vertical_strips = block.w >= block.h
    if vertical_strips:
        u1, u2, v1, v2 = block.x1, block.x2, block.y1, block.y2
        front_at_v1, front_at_v2 = _TOP, _BOTTOM
    else:
        u1, u2, v1, v2 = block.y1, block.y2, block.x1, block.x2
        front_at_v1, front_at_v2 = _LEFT, _RIGHT

    span = u2 - u1
    n = max(1, round(span / preset.target_lot_len))
    while n > 1 and span / n < preset.min_lot_len:
        n -= 1

    rows = _lot_rows(v2 - v1, preset)
    v_mid = (v1 + v2) / 2

    lots = []
    for i in range(n):
        ua = u1 + span * i / n
        # L'ultima striscia prende il bordo dell'isolato cosi com'e invece di
        # ricalcolarlo: u1 + span * n/n non ridà u2 esatto in virgola mobile,
        # e l'ULP di scarto faceva sporgere l'ultimo lotto fuori dall'isolato.
        ub = u2 if i == n - 1 else u1 + span * (i + 1) / n
        for row in range(rows):
            if rows == 1:
                va, vb, front = v1, v2, front_at_v2
            elif row == 0:
                va, vb, front = v1, v_mid, front_at_v1
            else:
                va, vb, front = v_mid, v2, front_at_v2
            lot = Rect(ua, va, ub, vb) if vertical_strips else Rect(va, ua, vb, ub)
            lots.append((lot, front))
    return lots


def _translate_rect(rect: Rect, dx: float, dy: float) -> Rect:
    return Rect(rect.x1 + dx, rect.y1 + dy, rect.x2 + dx, rect.y2 + dy)


def _translate_blueprint(bp: Blueprint, dx: float, dy: float, *, rooms) -> Blueprint:
    """Trasla un edificio (Rect/Corridor sono frozen: bisogna ricostruirli),
    tenendo solo le stanze passate in `rooms`. Le porte non si toccano:
    Door.wall_index/t sono relativi al muro della propria stanza, non
    cambiano con una traslazione."""
    kept = {id(room) for room in rooms}
    index_of = {id(room): i for i, room in enumerate(rooms)}
    translated = [
        Room(
            rect=_translate_rect(r.rect, dx, dy), kind=r.kind, name=r.name,
            doors=[Door(wall_index=d.wall_index, t=d.t, kind=d.kind, locked=d.locked) for d in r.doors],
            floor=r.floor, lights=[(x + dx, y + dy) for x, y in r.lights], level=r.level,
        )
        for r in rooms
    ]
    graph = {
        index_of[id(bp.rooms[i])]: [
            index_of[id(bp.rooms[j])] for j in neighbours if id(bp.rooms[j]) in kept
        ]
        for i, neighbours in bp.graph.items()
        if id(bp.rooms[i]) in kept
    }
    corridors = [
        Corridor(c.x1 + dx, c.y1 + dy, c.x2 + dx, c.y2 + dy, horizontal=c.horizontal)
        for c in bp.corridors
    ]
    stairs_rect = _translate_rect(bp.stairs_rect, dx, dy) if bp.stairs_rect is not None else None
    return Blueprint(
        width=bp.width, height=bp.height, rooms=translated, corridors=corridors,
        graph=graph, seed=bp.seed, style=bp.style, levels=1, stairs_rect=stairs_rect,
    )


def _building_area(
    lot: Rect, front_side: int, *, setback: float, side_margin: float, depth: float,
) -> Rect:
    """Porzione del lotto occupabile dall'edificio: margine fisso sui lati
    non-fronte, `setback` (arretramento casuale, AC1) sul lato fronte, e
    profondita al piu `depth` misurata dal fronte - il resto del lotto resta
    cortile. Puo venire degenere su un lotto minuscolo: e il chiamante a
    scartarla confrontandola con preset.min_building_side."""
    if front_side in (_TOP, _BOTTOM):
        x1, x2 = lot.x1 + side_margin, lot.x2 - side_margin
        if front_side == _BOTTOM:
            y2 = lot.y2 - setback
            y1 = max(lot.y1 + side_margin, y2 - depth)
        else:
            y1 = lot.y1 + setback
            y2 = min(lot.y2 - side_margin, y1 + depth)
    else:
        y1, y2 = lot.y1 + side_margin, lot.y2 - side_margin
        if front_side == _RIGHT:
            x2 = lot.x2 - setback
            x1 = max(lot.x1 + side_margin, x2 - depth)
        else:
            x1 = lot.x1 + setback
            x2 = min(lot.x2 - side_margin, x1 + depth)
    return Rect(x1, y1, x2, y2)


def _choose_building_type(side: float, rng: random.Random) -> tuple[str, bool]:
    """Sceglie tipologia e pianta (rettangolare o a L) fra quelle che stanno
    in un lotto di lato minimo `side`, con i pesi di _BUILDING_REPERTOIRE
    normalizzati sulle sole voci ammissibili."""
    eligible = [entry for entry in _BUILDING_REPERTOIRE if side >= entry[3]]
    if not eligible:
        eligible = [_BUILDING_REPERTOIRE[0]]
    total = sum(entry[2] for entry in eligible)
    threshold = rng.uniform(0.0, total)
    cumulative = 0.0
    for building_type, l_shaped, weight, _min_side in eligible:
        cumulative += weight
        if threshold <= cumulative:
            return building_type, l_shaped
    return eligible[-1][0], eligible[-1][1]


def _place_building(
    lot: Rect, front_side: int, rng: random.Random, preset: ScalePreset, *, seed: int,
) -> Blueprint | None:
    """Preset "isolato": genera un edificio con building.py e lo posiziona
    dentro `lot`. None se il lotto e troppo piccolo per contenerne uno
    (preset.min_building_side): si salta il lotto, non si forza un edificio
    spezzato.

    Delle tipologie multi-piano si tiene il solo piano terra: su una mappa
    cittadina i piani alti non si disegnano (il livello e uno), e portarsi
    dietro stanze che nessuno disegna vorrebbe dire lasciare un Blueprint che
    non descrive quel che si vede. Il vano scale resta: e la scala verso un
    piano che esiste ma non viene mostrato."""
    setback = rng.uniform(*preset.setback_range)
    depth = rng.uniform(*preset.building_depth_range)
    area = _building_area(
        lot, front_side, setback=setback, side_margin=preset.side_margin, depth=depth,
    )

    width, height = int(area.w), int(area.h)
    if width < preset.min_building_side or height < preset.min_building_side:
        return None

    building_type, l_shaped = _choose_building_type(min(width, height), rng)
    bp = building.generate(
        width=width, height=height, seed=seed, building_type=building_type, l_shaped=l_shaped,
    )
    ground = [room for room in bp.rooms if room.level == 0]
    if not ground:
        return None
    return _translate_blueprint(bp, area.x1, area.y1, rooms=ground)


def _place_footprint(
    lot: Rect, front_side: int, rng: random.Random, preset: ScalePreset,
) -> Rect | None:
    """Preset "quartiere"/"citta": l'edificio e il solo rettangolo di
    ingombro, con lo stesso fronte strada, arretramento e tetto di
    profondita del preset "isolato" (a scala ridotta). None se il lotto e
    troppo piccolo."""
    setback = rng.uniform(*preset.setback_range)
    depth = rng.uniform(*preset.building_depth_range)
    area = _building_area(
        lot, front_side, setback=setback, side_margin=preset.side_margin, depth=depth,
    )
    if area.w < preset.min_building_side or area.h < preset.min_building_side:
        return None
    return area


def _avenue(width: int, height: int, rng: random.Random, preset: ScalePreset) -> Street:
    """Via obliqua da un bordo del canvas a quello opposto.

    E' l'unica via che non nasce da un taglio della partizione, ed e lei a
    rompere l'ortogonalita della rete (richiesta di Jay: "le strade devono
    essere piu irregolari, non solo verticali e orizzontali"). Non avendo un
    ingombro riservato, si fa spazio: il chiamante toglie gli edifici che
    incontra (vedi _clear_avenue)."""
    path_width = preset.main_street_width * preset.street_path_fraction
    if rng.random() < 0.5:  # da sinistra a destra
        start = (1.0, rng.uniform(height * 0.2, height * 0.8))
        end = (width - 1.0, rng.uniform(height * 0.2, height * 0.8))
    else:  # dall'alto in basso
        start = (rng.uniform(width * 0.2, width * 0.8), 1.0)
        end = (rng.uniform(width * 0.2, width * 0.8), height - 1.0)

    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    # Vertici molto piu distanziati di quelli di una via da taglio, e scarto
    # molto piu contenuto: al primo tentativo (passo = street_segment_len,
    # scarto = main_street_width) la via veniva un zigzag a tornanti invece
    # di una diagonale che curva.
    steps = max(2, round(length / (preset.street_segment_len * _AVENUE_SEGMENT_FACTOR)))
    # Normale unitaria alla corda: lo scarto dei vertici intermedi le va
    # lungo, cosi la via resta una via e non un serpente che torna indietro.
    nx, ny = -dy / length, dx / length
    sway = preset.main_street_width * _AVENUE_SWAY_FACTOR

    points = []
    for i in range(steps + 1):
        px, py = start[0] + dx * i / steps, start[1] + dy * i / steps
        if i not in (0, steps):
            offset = rng.uniform(-sway, sway)
            px, py = px + nx * offset, py + ny * offset
        points.append((px, py))
    return Street(points=points, width=path_width, corridor=None, main=False)


def _distance_point_to_rect(x: float, y: float, rect: Rect) -> float:
    dx = max(rect.x1 - x, 0.0, x - rect.x2)
    dy = max(rect.y1 - y, 0.0, y - rect.y2)
    return math.hypot(dx, dy)


def _rect_near_polyline(rect: Rect, points: list, radius: float, *, step: float) -> bool:
    """Vero se `rect` arriva a meno di `radius` dalla polilinea.

    Campiona la polilinea invece di calcolare la distanza esatta
    segmento-rettangolo: il chiamante sceglie `step` in funzione del preset
    (vedi _clear_avenue) cosi da restare sempre ben sotto il lato minimo di
    un edificio, ed evita il caso scomodo del segmento che attraversa il
    rettangolo senza che nessun vertice dell'uno sia vicino a un vertice
    dell'altro."""
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        length = math.hypot(bx - ax, by - ay)
        samples = max(1, int(length / step))
        for i in range(samples + 1):
            t = i / samples
            if _distance_point_to_rect(ax + (bx - ax) * t, ay + (by - ay) * t, rect) <= radius:
                return True
    return False


def _clear_avenue(avenue: Street, rects: list, preset: ScalePreset) -> list:
    """Indici degli elementi di `rects` che la via obliqua attraversa: sono
    quelli da togliere perche la via ci passi davvero, invece di disegnarci
    sopra una strada che entra dentro le case. Serve identica al fiume
    (TASK-48), che ha gli stessi due attributi usati qui, `points` e `width`.

    `rects` puo contenere None: dopo TASK-48 gli edifici tolti lasciano un
    buco invece di far scalare la lista, perche gli indici devono restare
    stabili fra un passaggio e l'altro (un lotto sa a quale edificio
    corrisponde).

    Il passo di campionamento e derivato da preset.min_building_side (mai
    sopra 0,25 quadretti, il valore tarato per i preset "isolato" e
    "quartiere"): col preset "citta" (min_building_side 0,25) un passo fisso
    di 0,25 puo saltare interi edifici piccoli fra un campione e il
    successivo, lasciandoli addosso alla via - verificato generando 780
    combinazioni citta (seed x canvas) e campionando ogni via obliqua a un
    passo molto piu fine per cercare edifici non rimossi."""
    radius = avenue.width / 2 + preset.side_margin
    step = min(0.25, preset.min_building_side / 3)
    return [
        i for i, rect in enumerate(rects)
        if rect is not None and _rect_near_polyline(rect, avenue.points, radius, step=step)
    ]


def _footprint_of(bp: Blueprint) -> Rect:
    """Bounding box di un edificio del preset quartiere, la stessa cosa che
    compose._building_footprint deriva per disegnarne il perimetro."""
    parts = [room.rect for room in bp.rooms]
    if bp.stairs_rect is not None:
        parts.append(bp.stairs_rect)
    return Rect(
        min(p.x1 for p in parts), min(p.y1 for p in parts),
        max(p.x2 for p in parts), max(p.y2 for p in parts),
    )


# ---------------------------------------------------------------------------
# TASK-48: strutture urbane (mura, fiume, porto) e luoghi notevoli
# ---------------------------------------------------------------------------
#
# L'idea che tiene insieme tutto questo blocco: un luogo notevole non viene
# MAI disegnato in uno spazio libero trovato a occhio, ma prende il posto di
# qualcosa che la partizione aveva gia' riservato (un lotto, un isolato, una
# porzione di piazza, una cella della fascia extramurale). Cosi' la garanzia
# di TASK-35 "nessun edificio in mezzo alla strada" si estende gratis ai
# luoghi, e AC6 diventa un invariante di costruzione invece di un controllo a
# posteriori che ogni tanto fallisce.

# Profondita' della fascia di margine, in frazione del lato minore, con un
# tetto espresso in lotti. E' la fascia extramurale quando ci sono le mura
# ("fuori le mura") e il margine della citta' quando non ci sono ("ai
# margini"): un solo spazio riservato per le due regole, che sul terreno sono
# la stessa cosa.
#
# Il tetto in lotti non e' un dettaglio: alla sola frazione, sul canvas di
# produzione 78x78 la fascia veniva profonda ~7 quadretti in ENTRAMBI i preset
# astratti - due lotti al preset "quartiere" (ragionevole) e otto al preset
# "citta" (un terzo della mappa buttato in un prato). La fascia deve contenere
# un paio di celle di fascia, e una cella vale un lotto.
_FRAME_FRACTION = 0.06
_FRAME_MAX_LOTS = 2.5
# Spessore del muro, in multipli della via principale: una cinta muraria e'
# larga come mezza strada, non come un tramezzo.
_WALL_THICKNESS_FACTOR = 0.5
_PORT_DEPTH_RANGE = (0.08, 0.13)
# Oltre questa quota del lato la fascia portuale non e' piu' un porto ma un
# lago: su un canvas troppo piccolo perche' una banchina larga un lotto stia
# in una frazione ragionevole, la citta' resta senza porto.
_PORT_MAX_DEPTH = 0.25
# Quanta parte della fascia portuale e' banchina calpestabile invece che
# acqua: e' li' che vanno cantiere, faro e mercato del pesce.
_PORT_QUAY_FRACTION = 0.35
_RIVER_WIDTH_FACTOR = 1.7
# Quanto lontano puo' stare un luogo dall'elemento che lo vincola e contare
# ancora come "a ridosso" (in multipli del lotto-bersaglio). Sotto ~2 lotti
# nessun sito soddisfa mai la regola, perche' fra la porta e il primo lotto
# c'e' sempre almeno la larghezza della via.
_RULE_RADIUS_LOTS = 3.0
# Frazione del percorso del fiume oltre la quale si e' "a valle" (AC5): la
# meta' finale. Il verso e' quello di River.points, dalla sorgente alla foce.
_DOWNSTREAM_FROM = 0.5


def _shrunk(rect: Rect, d: float) -> Rect | None:
    """`rect` rimpicciolito di `d` per lato, o None se non resta nulla."""
    out = Rect(rect.x1 + d, rect.y1 + d, rect.x2 - d, rect.y2 - d)
    return out if out.w > 0 and out.h > 0 else None


def _edge_point(rect: Rect, side: int, rng: random.Random) -> tuple[float, float]:
    """Punto casuale sul lato `side` di `rect`, lontano dagli spigoli: una
    foce o una sorgente in un angolo taglierebbe via una scheggia di mappa
    invece di attraversarla."""
    lo, hi = 0.2, 0.8
    if side in (_TOP, _BOTTOM):
        x = rect.x1 + rect.w * rng.uniform(lo, hi)
        return (x, rect.y1 if side == _TOP else rect.y2)
    y = rect.y1 + rect.h * rng.uniform(lo, hi)
    return (rect.x1 if side == _LEFT else rect.x2, y)


def _make_port(rect: Rect, rng: random.Random, preset: ScalePreset):
    """Fascia portuale su un bordo di `rect`: acqua verso l'esterno, banchina
    verso la citta'. Ritorna (Port, rect_residuo).

    Ritorna (None, rect) se la fascia non ci sta: una banchina piu' stretta di
    un paio di lotti non e' un porto, e' un bordo bagnato."""
    side = rng.randrange(4)
    span = rect.h if side in (_TOP, _BOTTOM) else rect.w
    # La banchina non puo' venire piu' stretta di un lotto, altrimenti non ci
    # sta nemmeno una cella di fascia e cantiere, faro e mercato del pesce non
    # trovano mai posto: il porto risulterebbe presente e deserto. Il minimo
    # ha la precedenza sulla frazione, ed e' il motivo per cui la frazione da
    # sola non basta (al preset "quartiere" 8% di 76 quadretti da' una
    # banchina di 2,1 contro un lotto di 3).
    depth = max(span * rng.uniform(*_PORT_DEPTH_RANGE), preset.target_lot_len / _PORT_QUAY_FRACTION)
    if depth > span * _PORT_MAX_DEPTH:
        return None, rect
    water_depth = depth * (1 - _PORT_QUAY_FRACTION)

    if side == _TOP:
        water = Rect(rect.x1, rect.y1, rect.x2, rect.y1 + water_depth)
        quay = Rect(rect.x1, water.y2, rect.x2, rect.y1 + depth)
        rest = Rect(rect.x1, rect.y1 + depth, rect.x2, rect.y2)
    elif side == _BOTTOM:
        water = Rect(rect.x1, rect.y2 - water_depth, rect.x2, rect.y2)
        quay = Rect(rect.x1, rect.y2 - depth, rect.x2, water.y1)
        rest = Rect(rect.x1, rect.y1, rect.x2, rect.y2 - depth)
    elif side == _LEFT:
        water = Rect(rect.x1, rect.y1, rect.x1 + water_depth, rect.y2)
        quay = Rect(water.x2, rect.y1, rect.x1 + depth, rect.y2)
        rest = Rect(rect.x1 + depth, rect.y1, rect.x2, rect.y2)
    else:
        water = Rect(rect.x2 - water_depth, rect.y1, rect.x2, rect.y2)
        quay = Rect(rect.x2 - depth, rect.y1, water.x1, rect.y2)
        rest = Rect(rect.x1, rect.y1, rect.x2 - depth, rect.y2)
    return Port(water=water, quay=quay, side=side), rest


def _make_river(rect: Rect, rng: random.Random, preset: ScalePreset, *, mouth: int | None) -> River:
    """Fiume da un bordo di `rect` al bordo opposto, con la stessa meccanica
    di serpeggio della via obliqua (_avenue).

    `mouth` e' il lato dove sfocia: quello del porto se c'e' un porto (un
    fiume sfocia nel mare, e cosi' banchina e corso d'acqua si incontrano
    dove ci si aspetta), altrimenti a sorte. La sorgente e' sempre il lato
    opposto, quindi points va SEMPRE da monte a valle: e' quello a rendere
    definito "la conceria sta a valle" (AC5)."""
    width = preset.main_street_width * _RIVER_WIDTH_FACTOR
    mouth = rng.randrange(4) if mouth is None else mouth
    source = (mouth + 2) % 4
    start = _edge_point(rect, source, rng)
    end = _edge_point(rect, mouth, rng)

    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy) or 1.0
    steps = max(2, round(length / (preset.street_segment_len * _AVENUE_SEGMENT_FACTOR)))
    nx, ny = -dy / length, dx / length
    sway = width * _AVENUE_SWAY_FACTOR * 2

    points = []
    for i in range(steps + 1):
        px, py = start[0] + dx * i / steps, start[1] + dy * i / steps
        if i not in (0, steps):
            offset = rng.uniform(-sway, sway)
            px, py = px + nx * offset, py + ny * offset
        points.append((px, py))
    return River(points=points, width=width)


def _segment_intersection(p1, p2, p3, p4):
    """Punto di intersezione fra i segmenti p1p2 e p3p4, o None. Formula
    parametrica standard; i segmenti paralleli (denominatore nullo) non
    contano come incrocio, che e' esattamente quello che serve qui: una via
    che corre parallela al fiume non ci costruisce sopra un ponte."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, p3, p4
    den = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if abs(den) < 1e-12:
        return None
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / den
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / den
    if not (0.0 <= t <= 1.0 and 0.0 <= u <= 1.0):
        return None
    return (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)


def _river_bridges(river: River, streets: list) -> list:
    """Un ponte dove una via incrocia il fiume.

    I ponti non sono decisi a caso: sono esattamente le intersezioni fra le
    due polilinee, quindi una via che finisce nel fiume ha sempre il suo
    attraversamento e non ce ne sono di sospesi nel vuoto. Due incroci molto
    vicini (una via che ondeggia sopra il fiume e lo taglia due volte)
    diventano un ponte solo: sono lo stesso attraversamento."""
    bridges: list[Bridge] = []
    for street in streets:
        for a, b in zip(street.points, street.points[1:]):
            for c, d in zip(river.points, river.points[1:]):
                hit = _segment_intersection(a, b, c, d)
                if hit is None:
                    continue
                horizontal = abs(b[0] - a[0]) >= abs(b[1] - a[1])
                half_along = river.width * 0.75
                half_across = max(street.width, river.width * 0.35) / 2
                if horizontal:
                    rect = Rect(hit[0] - half_along, hit[1] - half_across,
                                hit[0] + half_along, hit[1] + half_across)
                else:
                    rect = Rect(hit[0] - half_across, hit[1] - half_along,
                                hit[0] + half_across, hit[1] + half_along)
                if any(rect.overlaps(existing.rect) for existing in bridges):
                    continue
                bridges.append(Bridge(rect=rect, horizontal=horizontal))
    return bridges


def _wall_gates(streets: list, buildable: Rect, ring: Rect) -> list:
    """Porte fortificate: una per lato, dove l'ingombro della via piu' larga
    incontra le mura.

    Una porta si apre dove una strada arriva davvero, altrimenti e' un varco
    che non porta da nessuna parte. L'ingombro riservato di una via (non la
    sua centro-linea, che serpeggia) e' il riferimento giusto: e' rettangolo
    e i suoi estremi coincidono con il bordo dell'area edificabile per
    costruzione."""
    eps = 1e-6
    best: dict[int, Gate] = {}

    def consider(side: int, x: float, y: float, w: float) -> None:
        current = best.get(side)
        if current is None or w > current.width:
            best[side] = Gate(x=x, y=y, side=side, width=w)

    for street in streets:
        corridor = street.corridor
        if corridor is None:
            continue
        if corridor.h >= corridor.w:  # via verticale: tocca i lati alto/basso
            cx = (corridor.x1 + corridor.x2) / 2
            if abs(corridor.y1 - buildable.y1) < eps:
                consider(_TOP, cx, ring.y1, corridor.w)
            if abs(corridor.y2 - buildable.y2) < eps:
                consider(_BOTTOM, cx, ring.y2, corridor.w)
        else:
            cy = (corridor.y1 + corridor.y2) / 2
            if abs(corridor.x1 - buildable.x1) < eps:
                consider(_LEFT, ring.x1, cy, corridor.h)
            if abs(corridor.x2 - buildable.x2) < eps:
                consider(_RIGHT, ring.x2, cy, corridor.h)
    return [best[side] for side in sorted(best)]


def _frame_strips(outer: Rect, inner: Rect, clearance: float) -> list:
    """Le quattro strisce fra `outer` e `inner`, arretrate di `clearance` sul
    lato interno per lasciare passare le mura (che corrono sul bordo di
    `inner` con meta' spessore che sborda verso l'esterno). Senza
    l'arretramento un cimitero finirebbe addosso al muro."""
    top = Rect(outer.x1, outer.y1, outer.x2, inner.y1 - clearance)
    bottom = Rect(outer.x1, inner.y2 + clearance, outer.x2, outer.y2)
    left = Rect(outer.x1, inner.y1, inner.x1 - clearance, inner.y2)
    right = Rect(inner.x2 + clearance, inner.y1, outer.x2, inner.y2)
    return [s for s in (top, bottom, left, right) if s.w > 0 and s.h > 0]


def _grid(rect: Rect, cols: int, rows: int) -> list:
    """Griglia cols x rows su `rect`, riga per riga."""
    cw, ch = rect.w / cols, rect.h / rows
    return [
        [
            Rect(rect.x1 + c * cw, rect.y1 + r * ch, rect.x1 + (c + 1) * cw, rect.y1 + (r + 1) * ch)
            for c in range(cols)
        ]
        for r in range(rows)
    ]


def _cells(rect: Rect, cell: float) -> list:
    """Griglia di celle di lato ~`cell` che copre `rect`, riga per riga."""
    return _grid(rect, max(1, int(rect.w / cell)), max(1, int(rect.h / cell)))


def _union(rects: list) -> Rect:
    return Rect(
        min(r.x1 for r in rects), min(r.y1 for r in rects),
        max(r.x2 for r in rects), max(r.y2 for r in rects),
    )


def _cell_runs(grid: list, span: int, occupied: list) -> list:
    """Tutte le finestre di `span` celle consecutive - per riga E per colonna
    - che non toccano nulla di gia' occupato.

    Le colonne non sono un di piu': una banchina e' una striscia stretta e
    lunga, e la sua griglia viene di una colonna sola per venticinque righe.
    Cercando solo per riga, nessun luogo largo piu' di una cella trovava mai
    posto e il porto restava senza cantiere navale (visto sul disegno del
    Blueprint, non da un test: i test verificavano le regole dei luoghi
    piazzati, non che venissero piazzati)."""
    lines = list(grid)
    if grid:
        lines += [list(column) for column in zip(*grid)]

    runs = []
    seen = set()
    for line in lines:
        for i in range(len(line) - span + 1):
            rect = _union(line[i : i + span])
            key = (rect.x1, rect.y1, rect.x2, rect.y2)
            if key in seen:
                continue
            seen.add(key)
            if not any(rect.overlaps(taken) for taken in occupied):
                runs.append(rect)
    return runs


def _polyline_proximity(rect: Rect, points: list, *, step: float) -> tuple[float, float]:
    """(distanza minima fra `rect` e la polilinea, parametro 0..1 del punto
    piu' vicino lungo la polilinea).

    Il secondo valore e' quello che rende verificabile "a valle" (AC5): 0 e'
    la sorgente, 1 la foce. Campionamento invece di distanza esatta, stessa
    scelta gia' fatta in _rect_near_polyline e per lo stesso motivo."""
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])]
    total = sum(lengths) or 1.0
    best = (math.inf, 0.0)
    travelled = 0.0
    for (ax, ay), (bx, by), length in zip(points, points[1:], lengths):
        samples = max(1, int(length / step))
        for i in range(samples + 1):
            u = i / samples
            d = _distance_point_to_rect(ax + (bx - ax) * u, ay + (by - ay) * u, rect)
            if d < best[0]:
                best = (d, (travelled + length * u) / total)
        travelled += length
    return best


@dataclass
class _Lot:
    """Un lotto edificabile con quel che ci e' stato costruito sopra.

    Esiste solo perche' i luoghi notevoli hanno bisogno di sapere quali lotti
    ci sono e quali sono ancora liberi: prima di TASK-48 i lotti venivano
    consumati dentro il ciclo di generate() e buttati via."""

    rect: Rect
    front: int
    block: int
    row: int
    strip: int
    area: Rect | None = None
    # Indice in buildings/footprints, o None se il lotto era troppo piccolo.
    index: int | None = None
    taken: bool = False


@dataclass
class _Sites:
    """Tutto quello che serve per decidere dove va un luogo. Un contenitore e
    non una decina di parametri: le funzioni di piazzamento ne usano quasi
    tutti i campi, e passarli sciolti nasconderebbe che sono un unico stato."""

    preset: ScalePreset
    seed: int
    # Area davvero edificabile (dentro le mura, fuori dal porto): il
    # riferimento di "ai margini", che senza non sarebbe definito.
    buildable: Rect
    lots: list
    plaza_indices: set
    plazas: list
    walls: CityWalls | None
    river: River | None
    port: Port | None
    frame: tuple | None  # (outer, inner) oppure None se non c'e' spazio
    buildings: list  # con buchi None per gli edifici tolti
    footprints: list  # idem
    occupied: list  # ingombri gia' presi su piazze e fasce
    landmarks: list


def _radius(preset: ScalePreset) -> float:
    return max(preset.target_lot_len * _RULE_RADIUS_LOTS, preset.main_street_width * 2)


def _rect_distance(a: Rect, b: Rect) -> float:
    """Distanza fra due rettangoli, 0 se si toccano o si sovrappongono."""
    dx = max(b.x1 - a.x2, 0.0, a.x1 - b.x2)
    dy = max(b.y1 - a.y2, 0.0, a.y1 - b.y2)
    return math.hypot(dx, dy)


def _rule_ok(sites: _Sites, kind, rect: Rect) -> bool:
    """La regola di piazzamento di `kind` vale per l'ingombro `rect`? (AC5)

    OGNI regola e' verificata qui in modo geometrico, anche quelle che il
    generatore di siti gia' garantirebbe da solo. Sembra ridondante e non lo
    e': "sulla piazza" e "ai margini" valgono anche per luoghi che NON stanno
    su un sito di piazza o di fascia (il municipio e la casa di cambio sono
    edifici affacciati sulla piazza, il monastero e' un isolato ai margini),
    e finche' queste regole rispondevano True fidandosi del sito quei tre
    luoghi finivano dove capitava. Verificarle tutte allo stesso modo rende
    AC5 un invariante unico invece di una collezione di casi speciali."""
    radius = _radius(sites.preset)
    if kind.rule == lm.RULE_ANY:
        return True
    if kind.rule == lm.RULE_GATE:
        walls = sites.walls
        if walls is None or not walls.gates:
            return False
        return any(
            _distance_point_to_rect(gate.x, gate.y, rect) <= radius for gate in walls.gates
        )
    if kind.rule in (lm.RULE_RIVER, lm.RULE_RIVER_DOWNSTREAM):
        if sites.river is None:
            return False
        step = max(0.25, sites.preset.target_lot_len / 4)
        distance, t = _polyline_proximity(rect, sites.river.points, step=step)
        if distance > radius:
            return False
        return kind.rule == lm.RULE_RIVER or t >= _DOWNSTREAM_FROM
    if kind.rule in (lm.RULE_PLAZA, lm.RULE_MAIN_PLAZA):
        plazas = sites.plazas
        if not plazas:
            return False
        if kind.rule == lm.RULE_MAIN_PLAZA:
            plazas = [max(plazas, key=lambda p: p.w * p.h)]
        return any(_rect_distance(rect, plaza) <= radius for plaza in plazas)
    if kind.rule == lm.RULE_PORT:
        return sites.port is not None and _rect_distance(rect, sites.port.quay) <= radius
    if kind.rule == lm.RULE_EDGE:
        # "Ai margini" = non entra nel nucleo, cioe' nell'area edificabile
        # arretrata di un raggio. Una definizione per sottrazione perche' il
        # margine di una citta' non e' un rettangolo: e' tutto quel che non e'
        # centro, dentro o fuori le mura che sia.
        core = _shrunk(sites.buildable, radius)
        return core is None or not rect.overlaps(core)
    if kind.rule == lm.RULE_OUTSIDE_WALLS_OR_TEMPLE:
        if sites.walls is not None and not rect.overlaps(sites.walls.ring):
            return True
        temples = [mark.rect.center() for mark in sites.landmarks if mark.kind == "tempio"]
        return any(_distance_point_to_rect(cx, cy, rect) <= radius for cx, cy in temples)
    return False


def _lot_candidates(sites: _Sites, kind) -> list:
    """Ingombri ricavabili da lotti liberi: `kind.lots` lotti consecutivi
    della stessa fila dello stesso isolato.

    Solo lotti che avevano davvero un edificio (`area` non None): un lotto
    troppo piccolo per una casa e' troppo piccolo anche per un luogo, e
    prendere lotti consecutivi con un buco in mezzo darebbe un ingombro che
    include spazio mai riservato a nessuno."""
    span = max(1, round(kind.lots))
    by_row: dict[tuple[int, int], list] = {}
    for index, lot in enumerate(sites.lots):
        by_row.setdefault((lot.block, lot.row), []).append(index)

    candidates = []
    for indices in by_row.values():
        indices.sort(key=lambda i: sites.lots[i].strip)
        for start in range(len(indices) - span + 1):
            window = indices[start : start + span]
            lots = [sites.lots[i] for i in window]
            if any(lot.taken or lot.area is None for lot in lots):
                continue
            if any(b.strip - a.strip != 1 for a, b in zip(lots, lots[1:])):
                continue
            candidates.append((_union([lot.area for lot in lots]), window))

    # Al preset "isolato" un luogo chiuso e' un edificio a stanze vero, e
    # building.generate pretende min_building_side per lato. Fra i lotti
    # liberi si preferiscono quindi quelli dove l'edificio ci sta davvero:
    # senza questa preferenza l'83% dei luoghi chiusi finiva su un lotto
    # troppo stretto e ripiegava sullo sprite, cioe' alla scala giocabile la
    # taverna era una taverna in cui non si entra. Se nessun lotto e'
    # abbastanza grande si ripiega su tutti: un luogo con lo sprite e'
    # comunque meglio di nessun luogo.
    if not kind.open_air and not sites.preset.abstract_buildings:
        side = sites.preset.min_building_side
        roomy = [entry for entry in candidates if entry[0].w >= side and entry[0].h >= side]
        if roomy:
            return roomy
    return candidates


def _block_candidates(sites: _Sites, _kind) -> list:
    """Isolati interi ancora liberi: un monastero, una cattedrale o un'arena
    occupano un isolato, non un lotto.

    UN isolato, non piu' d'uno, e non e' una svista. L'ingombro di un luogo e'
    un rettangolo, e fra due isolati la partizione mette SEMPRE una via:
    qualunque monumento a cavallo di due isolati si porta dentro la strada in
    mezzo, che e' esattamente cio' che AC6 vieta. Scritto, provato e tolto -
    la cattedrale finiva sopra una via. Per farlo davvero servirebbe spezzare
    quella via in due tronconi dove il monumento la ingloba: e' un lavoro sul
    modello delle strade, non un parametro in piu' qui.

    Il rilievo dei monumenti viene da altro: lo sprite dedicato
    (assets._CITY_LANDMARK_SPRITES) e il corpo dell'etichetta, che cresce con
    l'ingombro. Un isolato vale gia' tre-cinque case a tutte e tre le scale.

    `_kind` non serve (l'isolato si prende com'e) ma sta nella firma perche'
    tutte le strategie di _site_strategies vengono chiamate allo stesso modo."""
    by_block: dict[int, list] = {}
    for index, lot in enumerate(sites.lots):
        by_block.setdefault(lot.block, []).append(index)

    candidates = []
    for block_index, indices in by_block.items():
        if block_index in sites.plaza_indices:
            continue
        if any(sites.lots[i].taken for i in indices):
            continue
        areas = [sites.lots[i].area for i in indices if sites.lots[i].area is not None]
        if areas:
            candidates.append((_union(areas), indices))
    return candidates


def _plaza_candidates(sites: _Sites, kind) -> list:
    """Porzioni di piazza. La cella centrale non e' disponibile: e' della
    fontana, che render_city_blueprint disegna al centro di ogni piazza."""
    span = max(1, round(kind.lots))
    plazas = sites.plazas
    if kind.rule == lm.RULE_MAIN_PLAZA and plazas:
        plazas = [max(plazas, key=lambda p: p.w * p.h)]

    candidates = []
    for plaza in plazas:
        # Griglia 3x3 FISSA, non celle di lato dato: una piazza va divisa in
        # proporzione a se stessa. Con celle di dimensione assoluta una piazza
        # di lato pari al doppio della cella diventava 2x1, la fontana ne
        # occupava meta' e il mercato (che vuole due celle affiancate) non
        # trovava mai posto. Con 3x3 le due file esterne alla fontana restano
        # sempre libere, a qualunque scala.
        grid = _grid(plaza, 3, 3)
        centre = plaza.center()
        blocked = list(sites.occupied)
        for row in grid:
            for rect in row:
                if rect.x1 <= centre[0] <= rect.x2 and rect.y1 <= centre[1] <= rect.y2:
                    blocked.append(rect)
        candidates.extend((rect, None) for rect in _cell_runs(grid, span, blocked))
    return candidates


def _band_candidates(sites: _Sites, kind) -> list:
    """Celle della banchina (regola del porto) o della fascia
    extramurale/di margine (tutte le altre)."""
    span = max(1, round(kind.lots))
    if kind.rule == lm.RULE_PORT:
        strips = [sites.port.quay] if sites.port is not None else []
    else:
        if sites.frame is None:
            return []
        outer, inner = sites.frame
        clearance = sites.walls.thickness / 2 if sites.walls is not None else 0.0
        strips = _frame_strips(outer, inner, clearance)

    cell = max(sites.preset.target_lot_len, sites.preset.min_lot_len)
    candidates = []
    for strip in strips:
        grid = _cells(strip, cell)
        candidates.extend((rect, None) for rect in _cell_runs(grid, span, sites.occupied))
    return candidates


def _site_strategies(sites: _Sites, kind) -> list:
    """Quali generatori di siti provare per `kind`, in ordine.

    Una sola voce per quasi tutti. L'eccezione e' il cimitero: la sua regola
    ha due rami ("fuori le mura OPPURE presso il tempio") e i due rami stanno
    in posti diversi della citta', quindi anche in siti diversi - la fascia
    extramurale se le mura ci sono, un lotto vicino al tempio se non ci
    sono."""
    if kind.rule == lm.RULE_OUTSIDE_WALLS_OR_TEMPLE and sites.walls is None:
        return [_lot_candidates]
    return [{
        lm.SITE_LOT: _lot_candidates,
        lm.SITE_BLOCK: _block_candidates,
        lm.SITE_PLAZA: _plaza_candidates,
        lm.SITE_BAND: _band_candidates,
    }[kind.site]]


def _claim(sites: _Sites, kind, rect: Rect, lot_indices) -> None:
    """Registra il luogo e toglie di mezzo quel che occupava lo spazio."""
    building_blueprint = None
    if lot_indices is not None:
        for index in lot_indices:
            lot = sites.lots[index]
            lot.taken = True
            if lot.index is None:
                continue
            if sites.preset.abstract_buildings:
                sites.footprints[lot.index] = None
            else:
                # Al preset "isolato" l'edificio del luogo viene rigenerato
                # sull'ingombro COMPLESSIVO (piu' lotti uniti), con la
                # tipologia della sua destinazione d'uso: un tempio non e' la
                # casa che c'era prima con un cartello sopra.
                sites.buildings[lot.index] = None
        if not kind.open_air and not sites.preset.abstract_buildings:
            building_blueprint = _landmark_building(sites, kind, rect)
    else:
        sites.occupied.append(rect)
    sites.landmarks.append(
        Landmark(kind=kind.key, label=kind.label, rect=rect, site=kind.site,
                 open_air=kind.open_air, ground=kind.ground, piece_size=kind.piece_size,
                 building=building_blueprint)
    )


def _landmark_building(sites: _Sites, kind, rect: Rect):
    """Edificio a stanze di un luogo al preset "isolato". None se l'ingombro
    e' troppo piccolo per building.generate: il luogo resta comunque sulla
    mappa come ingombro piu' etichetta, che e' meglio di un edificio rotto."""
    width, height = int(rect.w), int(rect.h)
    if width < sites.preset.min_building_side or height < sites.preset.min_building_side:
        return None
    building_type = lm.BUILDING_TYPE.get(kind.key, lm.BUILDING_TYPE_DEFAULT)
    # Seed derivato dalla chiave del luogo e non estratto dall'rng: cosi'
    # aggiungere un luogo non sposta la geometria interna di quelli gia'
    # decisi, e lo stesso tempio con lo stesso seed di mappa e' sempre lo
    # stesso tempio.
    #
    # crc32 e non hash(): l'hash delle stringhe di Python e' randomizzato per
    # processo (PYTHONHASHSEED), quindi due esecuzioni della stessa riga di
    # comando davano due edifici diversi. Trovato dal test di riproducibilita'
    # della CLI, che gira in sottoprocesso — dai test in-process non si vede.
    bp = building.generate(
        width=width, height=height,
        seed=(sites.seed + zlib.crc32(kind.key.encode("utf-8"))) % (1 << 30),
        building_type=building_type, l_shaped=False,
    )
    ground = [room for room in bp.rooms if room.level == 0]
    if not ground:
        return None
    return _translate_blueprint(bp, rect.x1, rect.y1, rooms=ground)


def _place_landmarks(sites: _Sites, selection: list, rng: random.Random) -> None:
    """Piazza i luoghi selezionati, in ordine di catalogo (i vincolati prima
    dei liberi, vedi landmarks.LANDMARK_KINDS).

    Un luogo la cui regola non trova un sito NON viene piazzato altrove:
    viene semplicemente saltato. E' questa riga a rendere AC5 un invariante
    ("se e' sulla mappa, la regola vale") invece di una tendenza."""
    for kind, count in selection:
        for _ in range(count):
            placed = False
            for strategy in _site_strategies(sites, kind):
                candidates = [
                    (rect, owner) for rect, owner in strategy(sites, kind)
                    if _rule_ok(sites, kind, rect)
                ]
                if not candidates:
                    continue
                rect, owner = candidates[rng.randrange(len(candidates))]
                _claim(sites, kind, rect, owner)
                placed = True
                break
            if not placed:
                break


def generate(
    *, width: int, height: int, seed: int,
    scale: str = DEFAULT_SCALE, preset: ScalePreset | None = None,
    landmarks: bool = True, requested_landmarks=(),
    **params,
) -> Blueprint:
    """Genera un quartiere/citta (SPEC.md §9.4). RNG locale da `seed`, mai
    il modulo `random` globale (stesso vincolo degli altri generatori).

    `scale` sceglie un preset di SCALE_PRESETS ("quartiere" o "citta", vedi
    la nota di modulo e decision-2); `preset` permette di passarne uno
    tarato a mano, scavalcando `scale`.

    rooms/corridors restano vuoti (city.py non e a stanze, vedi model.py):
    la geometria vive in streets/plazas piu buildings (preset quartiere) o
    building_footprints (preset citta).

    TASK-48 aggiunge gli elementi urbani notevoli e le strutture che li
    ancorano. `landmarks=False` li disattiva del tutto e riporta il
    generatore a quello che era prima del task, output byte per byte
    compreso: e' l'interruttore che permette di verificare che nessuna
    regressione geometrica sia entrata insieme ai luoghi.
    `requested_landmarks` sono le richieste esplicite (AC1); tutto il resto
    e' estratto dal seed (AC2)."""
    if preset is None:
        preset = SCALE_PRESETS.get(scale)
        if preset is None:
            raise ValueError(
                f"Preset di scala sconosciuto: {scale!r}. Preset validi: {sorted(SCALE_PRESETS)}"
            )

    rng = random.Random(seed)
    root = Rect(1, 1, width - 1, height - 1)

    # --- strutture urbane: decise PRIMA di strade ed edifici -------------
    # Porto e mura non decorano una citta' gia' fatta, la rimodellano: il
    # porto sottrae una fascia di canvas, le mura riducono l'area
    # edificabile. Decidendole qui, "dentro le mura" e "sul mare" sono veri
    # per costruzione invece che da verificare a posteriori.
    structures: set = set()
    port: Port | None = None
    walls: CityWalls | None = None
    river: River | None = None
    frame: tuple | None = None
    buildable = root

    if landmarks:
        lm.check_requested(requested_landmarks, scale)
        structures = lm.select_structures(scale=scale, rng=rng, requested=requested_landmarks)
        if "porto" in structures:
            port, buildable = _make_port(buildable, rng, preset)
        if lm.needs_frame(scale) or "mura" in structures:
            depth = min(
                max(min(buildable.w, buildable.h) * _FRAME_FRACTION, preset.min_lot_len),
                preset.target_lot_len * _FRAME_MAX_LOTS,
            )
            inner = _shrunk(buildable, depth)
            # Serve almeno un isolato piu' la via che lo borda: sotto, la
            # fascia si mangerebbe la citta' invece di circondarla.
            floor_side = preset.min_block + preset.main_street_width
            if inner is not None and min(inner.w, inner.h) >= floor_side:
                frame = (buildable, inner)
                buildable = inner
                if "mura" in structures:
                    thickness = preset.main_street_width * _WALL_THICKNESS_FACTOR
                    walled = _shrunk(inner, thickness)
                    if walled is not None and min(walled.w, walled.h) >= floor_side:
                        walls = CityWalls(ring=inner, thickness=thickness)
                        buildable = walled

    streets: list[Street] = []
    blocks = _build_blocks(buildable, rng, depth=0, streets=streets, preset=preset)

    n_plazas = 2 if len(blocks) >= 4 else (1 if len(blocks) >= 2 else 0)
    plaza_indices = set(rng.sample(range(len(blocks)), n_plazas)) if n_plazas else set()
    plazas = [blocks[i] for i in sorted(plaza_indices)]

    # I lotti non vengono piu' consumati e buttati (TASK-48): sono i siti su
    # cui i luoghi notevoli prendono il posto di una casa qualunque, quindi
    # vanno conservati insieme a quale edificio ci e' finito sopra.
    lots: list[_Lot] = []
    buildings: list = []
    footprints: list = []
    for i, block in enumerate(blocks):
        if i in plaza_indices:
            continue
        # Stessa formula di _split_into_lots: la profondita' su cui si contano
        # le file e' il lato ortogonale alle strisce.
        rows = _lot_rows(block.h if block.w >= block.h else block.w, preset)
        for j, (lot_rect, front) in enumerate(_split_into_lots(block, preset)):
            record = _Lot(rect=lot_rect, front=front, block=i, row=j % rows, strip=j // rows)
            lots.append(record)
            if preset.abstract_buildings:
                footprint = _place_footprint(lot_rect, front, rng, preset)
                if footprint is not None:
                    record.area, record.index = footprint, len(footprints)
                    footprints.append(footprint)
            else:
                # Il seed dell'edificio va estratto PRIMA di entrare in
                # _place_building, che a sua volta consuma l'RNG: tenerlo
                # esplicito qui evita di dipendere dall'ordine di valutazione
                # degli argomenti di una chiamata.
                building_seed = rng.randrange(1 << 30)
                placed = _place_building(lot_rect, front, rng, preset, seed=building_seed)
                if placed is not None:
                    record.area, record.index = _footprint_of(placed), len(buildings)
                    buildings.append(placed)

    def _clear(crosser) -> None:
        """Toglie gli edifici che `crosser` (via obliqua o fiume) attraversa,
        lasciando un buco invece di far scalare la lista: gli indici sono
        quelli con cui i lotti sanno a quale edificio corrispondono."""
        if preset.abstract_buildings:
            for index in _clear_avenue(crosser, footprints, preset):
                footprints[index] = None
        else:
            boxes = [None if bp is None else _footprint_of(bp) for bp in buildings]
            for index in _clear_avenue(crosser, boxes, preset):
                buildings[index] = None

    # Il fiume prima delle vie oblique, e come loro dopo gli edifici: non ha
    # un ingombro riservato dalla partizione, quindi si fa spazio togliendo
    # quel che incontra (stessa meccanica di _avenue).
    if "fiume" in structures:
        river = _make_river(root, rng, preset, mouth=None if port is None else port.side)
        _clear(river)

    # Le vie oblique per ultime: hanno bisogno degli edifici gia piazzati per
    # sapere quali togliere. Un canvas troppo piccolo per essere diviso
    # nemmeno una volta non ne riceve: sarebbe una strada da un bordo
    # all'altro di una mappa che non ha una rete stradale.
    n_avenues = preset.avenues if len(blocks) > 1 else 0
    for _ in range(n_avenues):
        avenue = _avenue(width, height, rng, preset)
        _clear(avenue)
        streets.append(avenue)

    bridges: list[Bridge] = []
    if walls is not None:
        walls.gates = _wall_gates(streets, buildable, walls.ring)
    if river is not None:
        bridges = _river_bridges(river, streets)

    marks: list[Landmark] = []
    if landmarks:
        sites = _Sites(
            preset=preset, seed=seed, buildable=buildable, lots=lots,
            plaza_indices=plaza_indices, plazas=plazas, walls=walls, river=river,
            port=port, frame=frame, buildings=buildings, footprints=footprints,
            occupied=[], landmarks=marks,
        )
        n_buildings = sum(1 for b in (footprints if preset.abstract_buildings else buildings) if b is not None)
        selection = lm.select(
            scale=scale, n_buildings=n_buildings, rng=rng, requested=requested_landmarks,
        )
        _place_landmarks(sites, selection, rng)

    return Blueprint(
        width=width, height=height, rooms=[], corridors=[], graph={},
        seed=seed, style="city", streets=streets, plazas=plazas,
        buildings=[bp for bp in buildings if bp is not None],
        building_footprints=[f for f in footprints if f is not None],
        landmarks=marks, walls=walls, river=river, bridges=bridges, port=port,
    )
