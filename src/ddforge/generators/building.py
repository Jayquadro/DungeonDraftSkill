"""Edifici urbani multi-piano: taverne, magioni, magazzini.

Vedi docs/SPEC.md §9.2. Riusa l'infrastruttura di partizione e connessione
di bsp.py (TASK-21), generica e non specifica al dungeon: _build_tree
partiziona un rettangolo qualsiasi, _connect_rooms decide porta-diretta o
corridoio fra due stanze qualsiasi. Produce solo un Blueprint, nessun
accesso a level/ids/JSON (stesso vincolo di bsp.py).
"""

import math
import random

from ddforge.compose import _shared_wall_segment
from ddforge.generators.bsp import _build_tree, _connect_rooms, _non_colliding_t, _t_on_side
from ddforge.model import Blueprint, Corridor, Door, Rect, Room

# Ogni tipologia: lista di (indice_piano, [kind per ogni stanza attesa]).
# SPEC.md §9.2: taverna terra=sala comune+cucina+retro, primo=camere;
# magione terra=rappresentanza, primo=privato, sottotetto=servitu;
# magazzino terra=volume unico, primo=soppalco (copre solo meta pianta).
_BUILDING_TYPES = {
    "tavern": [
        (0, ["sala_comune", "cucina", "retro"]),
        (1, ["camera", "camera", "camera"]),
    ],
    "manor": [
        (0, ["rappresentanza", "rappresentanza"]),
        (1, ["privato", "privato", "privato"]),
        (2, ["servitu", "servitu"]),
    ],
    "warehouse": [
        (0, ["magazzino"]),
        (1, ["soppalco"]),
    ],
    # Edificio generico a un solo piano, per i lotti di generators/city.py
    # (TASK-35, SPEC.md §9.4): la spec non chiede una destinazione d'uso per
    # gli edifici di contorno di una via, solo che ci sia "un edificio per
    # lotto". Nessuna delle tipologie sopra e a un piano solo.
    "house": [
        (0, ["stanza", "stanza", "stanza"]),
    ],
}

# Larghezza del vano scale: 2 quadretti, cioe 3 m. Una rampa sta in 1 m,
# il resto e pianerottolo. Con 4 (6 m) un vano scale mangiava un quarto di
# una taverna.
_STAIRS_MIN_SIDE = 2

# Un quadretto di Dungeondraft vale 1.5 m reali (Jay, gate umano M4 round 2).
# Tutte le misure "da edificio vero" di questo modulo partono da qui.
_TILE_METERS = 1.5

# Lato massimo di una stanza abitata: 12 m. Oltre non e piu una stanza, e un
# capannone. _build_tree smette di tagliare una foglia quando ENTRAMBI i lati
# scendono sotto max_room*2, quindi il parametro che gli si passa vale meta
# del lato che si vuole ottenere.
_MAX_ROOM_SIDE_M = 12.0
_MAX_ROOM_SIDE = int(_MAX_ROOM_SIDE_M / _TILE_METERS)

# Piani che restano un ambiente solo, per specifica e non per caso: SPEC.md
# §9.2 vuole il piano terra del magazzino a volume unico e il soppalco come
# una balconata aperta. Un capannone e grande davvero, e l'unica eccezione
# alla regola dei 12 m.
_SINGLE_VOLUME_FLOORS = {("warehouse", 0), ("warehouse", 1)}

# Ingombro di default (width, height in quadretti, bordo compreso) per
# tipologia. A 1.5 m per quadretto un edificio 40x40 misura 60x60 METRI: al
# gate M4 round 2 il piano terra della taverna veniva diviso in 51 stanze
# regolamentari, che e la risposta giusta alla domanda sbagliata. Una
# taverna sta in 24x18 m, una magione in 30x24, un magazzino in 30x18.
_DEFAULT_SIZE = {
    "tavern": (18, 14),
    "manor": (22, 18),
    "warehouse": (22, 14),
}


def default_size(building_type: str) -> tuple[int, int]:
    """(width, height) in quadretti per una tipologia, se il chiamante non
    ne impone una. Vedi _DEFAULT_SIZE."""
    return _DEFAULT_SIZE.get(building_type, (18, 14))

# Etichette dei piani (level.label). Nel gate umano M4 Jay si e trovato due
# livelli entrambi chiamati "Ground", quello del template, perche nessuno
# passava mai `labels` a template.prepare: senza un nome proprio non si
# distingue il piano terra dal primo, e il tetto sembra stare sul piano
# sbagliato (TASK-30).
_FLOOR_LABELS = ["Piano terra", "Primo piano", "Secondo piano", "Terzo piano"]


def floor_labels(levels: int) -> list[str]:
    """Nomi dei piani per un edificio di `levels` piani. Oltre i nomi noti
    prosegue in modo generico invece di ripetersi."""
    return [
        _FLOOR_LABELS[i] if i < len(_FLOOR_LABELS) else f"Piano {i}"
        for i in range(levels)
    ]


def _footprint_parts(footprint: Rect, l_shaped: bool) -> list[Rect]:
    """Un rettangolo, o due che insieme formano una L (notch fisso in
    basso a destra: un solo caso e sufficiente, SPEC.md non chiede angoli
    diversi, solo che il generatore sappia produrre entrambe le forme)."""
    if not l_shaped:
        return [footprint]
    notch_w = max(2, int(footprint.w) // 3)
    notch_h = max(2, int(footprint.h) // 3)
    main_part = Rect(footprint.x1, footprint.y1, footprint.x2, footprint.y2 - notch_h)
    wing_part = Rect(footprint.x1, footprint.y2 - notch_h, footprint.x2 - notch_w, footprint.y2)
    return [main_part, wing_part]


def _stairwell_rect(footprint: Rect) -> Rect:
    """Vano scale: una fascia stretta lungo tutto il lato sinistro, che fa
    da corpo scale e da corridoio di distribuzione.

    Occupa un lato intero, non un angolo, e la scelta e deliberata: quel che
    resta del footprint e allora UN SOLO rettangolo, che le stanze possono
    tassellare esattamente. Ritagliando un angolo restano due parti, e una
    delle due e sempre una scheggia (col primo tentativo la sala comune
    veniva 2x36) oppure costringe a spezzare in due un piano che SPEC.md
    §9.2 vuole a volume unico, come il piano terra del magazzino.

    Tassellare esattamente e anche cio che tiene il vano scale DENTRO il
    perimetro portante: quel perimetro e il bounding box di cio che viene
    davvero disegnato, e nel gate umano M4 il vano scale ne restava fuori
    (TASK-30)."""
    width = max(_STAIRS_MIN_SIDE, int(min(footprint.w, footprint.h)) // 8)
    return Rect(footprint.x1, footprint.y1, footprint.x1 + width, footprint.y2)


def _parts_around_stairwell(footprint: Rect, stairs: Rect, l_shaped: bool) -> list[Rect]:
    """Il footprint meno il vano scale: un solo rettangolo (o due, se
    l'edificio e a L)."""
    rest = Rect(stairs.x2, footprint.y1, footprint.x2, footprint.y2)
    if rest.w <= 0 or rest.h <= 0:
        return []
    return _footprint_parts(rest, l_shaped)


def _generate_room_rects(parts: list[Rect], rng: random.Random, *, max_room: int, depth_max: int) -> list[Rect]:
    """Taglia ogni parte del footprint in stanze finche non stanno tutte
    entro il lato massimo.

    A guidare e la DIMENSIONE della stanza, non il numero di stanze. Con un
    numero fisso — tanti quanti i kind del piano, che era il criterio prima
    del gate M4 round 2 — _build_tree si ferma appena lo raggiunge: tre
    foglie su un footprint 34x38 danno stanze da 34x18 quadretti, cioe 51x27
    METRI. Qui il numero lo si lascia libero (rooms_target irraggiungibile) e
    a fermare i tagli e _can_split, che guarda i lati."""
    rects = []
    for part in parts:
        # rooms_target volutamente irraggiungibile: la condizione d'arresto
        # vera e _can_split(max_room), cioe entrambi i lati sotto max_room*2.
        unreachable = int(part.w * part.h) + 1
        _, leaves = _build_tree(part, rng, rooms_target=unreachable, max_room=max_room, depth_max=depth_max)
        # Le foglie diventano le stanze SENZA margine di inscrizione: in un
        # edificio le stanze condividono i tramezzi e il muro esterno, non
        # ci sono intercapedini fra una stanza e l'altra. Con _inscribe_room
        # (che va bene per un dungeon scavato nella roccia) le stanze
        # galleggiavano a distanze casuali e la pianta non si leggeva piu
        # come una pianta: e il difetto "non si capisce la divisione delle
        # stanze" del gate umano M4 (TASK-30).
        rects.extend(leaf.rect for leaf in leaves)
    return rects


def _connect_floor_rooms(rooms: list[Room], corridors: list[Corridor], corridor_width: float) -> dict:
    """Connette le stanze di un piano con un albero minimo (Prim): un
    edificio si legge bene anche come albero puro, non serve la ricorsione
    BSP ne gli anelli extra (quelli sono specifici del dungeon, TASK-21).
    Garantisce che ogni stanza sia raggiungibile.

    Fra due candidate a pari merito vince SEMPRE una coppia adiacente: in un
    edificio le stanze tassellano il footprint, quindi due stanze che
    condividono un tramezzo si collegano con una porta e basta. La coppia
    piu vicina di centro non e detto che sia adiacente, e per una coppia non
    adiacente _connect_rooms scava un corridoio — dentro le altre stanze
    del piano. Con le stanze grandi del round 1 la differenza non si vedeva;
    con stanze da 12 m si vedrebbe eccome (TASK-30)."""
    graph = {i: [] for i in range(len(rooms))}
    if len(rooms) < 2:
        return graph

    connected = [0]
    remaining = list(range(1, len(rooms)))
    while remaining:
        best_pair, best_key = None, None
        for i in connected:
            ax, ay = rooms[i].rect.center()
            for j in remaining:
                bx, by = rooms[j].rect.center()
                adjacent = _shared_wall_segment(rooms[i].rect, rooms[j].rect) is not None
                key = (0 if adjacent else 1, math.hypot(bx - ax, by - ay))
                if best_key is None or key < best_key:
                    best_key, best_pair = key, (i, j)
        assert best_pair is not None  # remaining non vuoto => almeno una coppia
        i, j = best_pair
        _connect_rooms(rooms, i, j, corridors, corridor_width)
        graph[i].append(j)
        graph[j].append(i)
        connected.append(j)
        remaining.remove(j)
    return graph


def _ensure_entry(floor_rooms: list[Room], footprint: Rect, *, force: bool) -> None:
    """Apre una porta sulla stanza del piano il cui lato inferiore e piu
    vicino al bordo del footprint (probabile parete esterna), evitando
    collisioni con porte gia presenti sullo stesso lato.

    force=True (piano terra): apre SEMPRE una porta d'ingresso, anche se le
    stanze hanno gia porte interne fra loro — quelle non danno accesso
    dall'esterno. force=False (altri piani): apre una porta solo se
    nessuna stanza del piano ne ha gia una, il caso di un piano con
    un'unica stanza (es. il soppalco di un magazzino) che altrimenti
    resterebbe un vicolo cieco senza porta (AC3)."""
    if not floor_rooms:
        return
    if not force and any(room.doors for room in floor_rooms):
        return
    entrance_room = min(floor_rooms, key=lambda r: abs(r.rect.y2 - footprint.y2))
    t = _non_colliding_t(entrance_room, 2, 0.5)
    entrance_room.doors.append(Door(wall_index=2, t=t, kind="wood"))


def _connect_stairwell(floor_rooms: list[Room], stairs: Rect) -> bool:
    """Apre una porta dalla stanza piu grande adiacente al vano scale verso
    il vano scale. Ritorna False se nessuna stanza del piano lo tocca.

    Senza questa porta il vano scale e una scatola murata: nel gate umano M4
    Jay non riusciva a capire quale fosse (TASK-30), ed era anche una delle
    DDF102 segnalate dal validatore."""
    adjacent = [
        (room, shared) for room in floor_rooms
        for shared in [_shared_wall_segment(room.rect, stairs)]
        if shared is not None
    ]
    if not adjacent:
        return False

    room, (side_room, _, midpoint) = max(adjacent, key=lambda pair: pair[0].rect.w * pair[0].rect.h)
    t = _non_colliding_t(room, side_room, _t_on_side(room.rect, side_room, midpoint))
    room.doors.append(Door(wall_index=side_room, t=t, kind="wood"))
    return True


def generate(*, width: int, height: int, seed: int,
             building_type: str = "tavern", l_shaped: bool = False,
             min_room: int = 3, max_room: int = _MAX_ROOM_SIDE // 2,
             corridor_width: float = 1.0,
             depth_max: int = 8, **params) -> Blueprint:
    """Genera un edificio multi-piano. building_type in
    {tavern, manor, warehouse} (SPEC.md §9.2).

    `max_room` e mezza dimensione: _build_tree taglia finche un lato supera
    max_room*2, quindi il default corrisponde a stanze fino a
    _MAX_ROOM_SIDE_M metri di lato. Vedi _generate_room_rects."""
    if building_type not in _BUILDING_TYPES:
        raise ValueError(f"Tipologia sconosciuta: {building_type!r}. Valide: {sorted(_BUILDING_TYPES)}")

    rng = random.Random(seed)
    footprint = Rect(1, 1, width - 1, height - 1)

    # Vano scale nell'angolo in alto a sinistra, stesso Rect su ogni piano.
    # Le stanze tassellano tutto il resto del footprint, quindi il perimetro
    # portante (che draw_building deriva dal bounding box di cio che
    # disegna) coincide col footprint e il vano scale ci sta DENTRO. Prima
    # del gate M4 si riservava una colonna intera larga quanto il vano ma
    # alta quanto l'edificio: meta restava spazio morto e il vano scale
    # finiva fuori dai muri (TASK-30).
    floors_spec = _BUILDING_TYPES[building_type]
    # Un edificio a un solo piano non ha scale da ospitare (TASK-41): il vano
    # si mangiava una fascia larga _STAIRS_MIN_SIDE su tutta l'altezza, cioe
    # un terzo di una casetta di citta, per portare da nessuna parte. Le case
    # generate da city.py erano cosi: un ripostiglio murato piu una stanza.
    single_floor = max(floor_index for floor_index, _ in floors_spec) == 0
    stairs_rect = None if single_floor else _stairwell_rect(footprint)
    generation_footprint = footprint
    parts = (
        _footprint_parts(footprint, l_shaped) if stairs_rect is None
        else _parts_around_stairwell(footprint, stairs_rect, l_shaped)
    )

    all_rooms: list[Room] = []
    all_graph: dict[int, list[int]] = {}
    corridors: list[Corridor] = []

    for floor_index, kinds in floors_spec:
        floor_parts = parts
        # `stairs_rect is not None` e implicito (un soppalco e un secondo
        # piano, quindi l'edificio non e a piano unico), ma tenerlo esplicito
        # evita di dipendere da quell'implicazione.
        if building_type == "warehouse" and floor_index == 1 and stairs_rect is not None:
            # Soppalco: copre solo meta della pianta, non l'intero footprint.
            # Parte comunque dal bordo destro del vano scale, che resta
            # riservato su ogni piano.
            half_width = max(min_room, int(generation_footprint.w) // 2)
            floor_parts = [Rect(
                stairs_rect.x2, generation_footprint.y1,
                stairs_rect.x2 + half_width, generation_footprint.y2,
            )]

        if (building_type, floor_index) in _SINGLE_VOLUME_FLOORS:
            room_rects = list(floor_parts)
        else:
            room_rects = _generate_room_rects(
                floor_parts, rng, max_room=max_room, depth_max=depth_max
            )

        # `kinds` e il repertorio del piano, non un elenco a lunghezza fissa:
        # il numero di stanze ora lo decide la loro dimensione, quindi i kind
        # si ripetono ciclicamente. Il primo della lista tocca alla stanza
        # piu grande — la sala comune di una taverna e la sala comune, non
        # uno sgabuzzino scelto a caso.
        order = sorted(range(len(room_rects)), key=lambda i: -room_rects[i].w * room_rects[i].h)
        kind_of = {}
        for position, index in enumerate(order):
            kind_of[index] = kinds[position % len(kinds)]
        floor_rooms = [
            Room(rect=rect, kind=kind_of[index], level=floor_index)
            for index, rect in enumerate(room_rects)
        ]
        floor_graph = _connect_floor_rooms(floor_rooms, corridors, corridor_width)
        if stairs_rect is not None:
            _connect_stairwell(floor_rooms, stairs_rect)
        _ensure_entry(floor_rooms, generation_footprint, force=(floor_index == 0))

        offset = len(all_rooms)
        for local_i, neighbors in floor_graph.items():
            all_graph[offset + local_i] = [offset + n for n in neighbors]
        all_rooms.extend(floor_rooms)

    n_levels = max(floor_index for floor_index, _ in floors_spec) + 1

    return Blueprint(
        width=width, height=height,
        rooms=all_rooms, corridors=corridors,
        graph=all_graph, seed=seed, style=building_type, levels=n_levels,
        stairs_rect=stairs_rect,
    )
