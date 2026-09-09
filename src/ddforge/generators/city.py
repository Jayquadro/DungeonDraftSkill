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
from dataclasses import dataclass

from ddforge.generators import building
from ddforge.model import Blueprint, Corridor, Door, Rect, Room, Street

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
    sopra una strada che entra dentro le case.

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
        i for i, rect in enumerate(rects) if _rect_near_polyline(rect, avenue.points, radius, step=step)
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


def generate(
    *, width: int, height: int, seed: int,
    scale: str = DEFAULT_SCALE, preset: ScalePreset | None = None,
    **params,
) -> Blueprint:
    """Genera un quartiere/citta (SPEC.md §9.4). RNG locale da `seed`, mai
    il modulo `random` globale (stesso vincolo degli altri generatori).

    `scale` sceglie un preset di SCALE_PRESETS ("quartiere" o "citta", vedi
    la nota di modulo e decision-2); `preset` permette di passarne uno
    tarato a mano, scavalcando `scale`.

    rooms/corridors restano vuoti (city.py non e a stanze, vedi model.py):
    la geometria vive in streets/plazas piu buildings (preset quartiere) o
    building_footprints (preset citta)."""
    if preset is None:
        preset = SCALE_PRESETS.get(scale)
        if preset is None:
            raise ValueError(
                f"Preset di scala sconosciuto: {scale!r}. Preset validi: {sorted(SCALE_PRESETS)}"
            )

    rng = random.Random(seed)
    root = Rect(1, 1, width - 1, height - 1)

    streets: list[Street] = []
    blocks = _build_blocks(root, rng, depth=0, streets=streets, preset=preset)

    n_plazas = 2 if len(blocks) >= 4 else (1 if len(blocks) >= 2 else 0)
    plaza_indices = set(rng.sample(range(len(blocks)), n_plazas)) if n_plazas else set()
    plazas = [blocks[i] for i in sorted(plaza_indices)]

    buildings: list[Blueprint] = []
    footprints: list[Rect] = []
    for i, block in enumerate(blocks):
        if i in plaza_indices:
            continue
        for lot, front in _split_into_lots(block, preset):
            if preset.abstract_buildings:
                footprint = _place_footprint(lot, front, rng, preset)
                if footprint is not None:
                    footprints.append(footprint)
            else:
                # Il seed dell'edificio va estratto PRIMA di entrare in
                # _place_building, che a sua volta consuma l'RNG: tenerlo
                # esplicito qui evita di dipendere dall'ordine di valutazione
                # degli argomenti di una chiamata.
                building_seed = rng.randrange(1 << 30)
                placed = _place_building(lot, front, rng, preset, seed=building_seed)
                if placed is not None:
                    buildings.append(placed)

    # Le vie oblique per ultime: hanno bisogno degli edifici gia piazzati per
    # sapere quali togliere. Un canvas troppo piccolo per essere diviso
    # nemmeno una volta non ne riceve: sarebbe una strada da un bordo
    # all'altro di una mappa che non ha una rete stradale.
    n_avenues = preset.avenues if len(blocks) > 1 else 0
    for _ in range(n_avenues):
        avenue = _avenue(width, height, rng, preset)
        if preset.abstract_buildings:
            crossed = set(_clear_avenue(avenue, footprints, preset))
            footprints = [f for i, f in enumerate(footprints) if i not in crossed]
        else:
            boxes = [_footprint_of(bp) for bp in buildings]
            crossed = set(_clear_avenue(avenue, boxes, preset))
            buildings = [bp for i, bp in enumerate(buildings) if i not in crossed]
        streets.append(avenue)

    return Blueprint(
        width=width, height=height, rooms=[], corridors=[], graph={},
        seed=seed, style="city", streets=streets, plazas=plazas,
        buildings=buildings, building_footprints=footprints,
    )
