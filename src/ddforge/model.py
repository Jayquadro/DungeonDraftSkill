"""Modello dati intermedio fra i generatori e la serializzazione.

I generatori producono Blueprint, non JSON: cosi restano testabili senza
toccare il formato. Flusso: generatore -> Blueprint -> compose -> build -> JSON.
Vedi docs/SPEC.md §6.4. Implementato in TASK-9.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Rect:
    """Rettangolo in coordinate-quadretto. x2/y2 esclusivi.

    I bordi delle stanze cadono su quadretti interi, ma un corridoio di
    larghezza dispari ha l'asse a meta quadretto: i lati sono float, non
    int (Dungeondraft lavora in pixel, 256 per quadretto, e le mezze
    coordinate sono legittime)."""

    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def w(self) -> float:
        return self.x2 - self.x1

    @property
    def h(self) -> float:
        return self.y2 - self.y1

    def center(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def overlaps(self, other: "Rect", margin: int = 0) -> bool:
        """Vero se i due rettangoli si intersecano, allargati di `margin` per lato."""
        return not (
            self.x2 + margin <= other.x1
            or other.x2 + margin <= self.x1
            or self.y2 + margin <= other.y1
            or other.y2 + margin <= self.y1
        )

    def shrink(self, n: int) -> "Rect":
        return Rect(self.x1 + n, self.y1 + n, self.x2 - n, self.y2 - n)


@dataclass(frozen=True)
class Corridor(Rect):
    """Segmento di corridoio: un Rect con l'orientamento del canale esplicito.

    `horizontal` dice quali sono i due lati lunghi, cioe dove vanno i muri:
    TOP/BOTTOM se True, LEFT/RIGHT se False. Non e derivabile da `w >= h`:
    il gomito fra due stanze separate da un solo quadretto e un segmento
    1x1, e indovinarlo al contrario mura le testate del canale sigillando
    il passaggio. E' il difetto che Jay ha visto in Dungeondraft nel gate
    umano M3 ("i muri girati sui lati sbagliati", TASK-26).
    """

    horizontal: bool = True


@dataclass
class Door:
    wall_index: int
    t: float
    kind: str = "wood"
    locked: bool = False


@dataclass
class Chamber:
    """Camera di giunzione circolare della variante fognature (TASK-33,
    SPEC.md §9.3). Qui resta solo la geometria astratta: compose.draw_chamber
    la approssima con un poligono regolare, aprendo un varco angolare su
    ogni lato di `connected` (dove entra un canale, TASK-33). `door=True`
    sulla camera d'ingresso (convenzione bsp._ENTRANCE_ROOM: la prima
    generata) apre una porta su un arco libero, l'unico punto in cui la
    variante fognature usa `palette.door` (AC3)."""

    center: tuple[float, float]
    radius: float
    connected: frozenset[str] = field(default_factory=frozenset)
    door: bool = False


@dataclass
class Street:
    """Una via di generators/city.py: centro-linea e larghezza selciata.

    La centro-linea e una polilinea, non un segmento: serpeggia dentro
    l'ingombro che le e stato riservato, cosi la rete stradale non e una
    griglia di rettangoli perfetti (TASK-41, richiesta di Jay al primo round
    del gate). Le coordinate sono in quadretti, come Rect.

    `corridor` e l'ingombro riservato dalla partizione degli isolati: la
    centro-linea vi resta dentro per costruzione e nessun edificio vi entra.
    E None per le vie oblique, che non nascono da un taglio e si fanno spazio
    togliendo gli edifici che incontrano (vedi city._avenue).
    """

    points: list[tuple[float, float]]
    width: float
    corridor: "Rect | None" = None
    # La via principale (il taglio di profondita 0): sempre piu larga delle
    # secondarie (SPEC.md §9.4). Campo esplicito e non "quella piu larga"
    # perche una via obliqua puo essere larga come lei.
    main: bool = False


@dataclass
class Room:
    rect: Rect
    kind: str
    name: str = ""
    doors: list[Door] = field(default_factory=list)
    floor: str | None = None
    lights: list[tuple[float, float]] = field(default_factory=list)
    # Piano dell'edificio a cui appartiene la stanza (TASK-27/§9.2): 0 per
    # un dungeon a un livello. generators/building.py (TASK-28) lo popola;
    # opzionale e retrocompatibile, i generatori a un piano lo ignorano.
    level: int = 0


@dataclass
class Blueprint:
    """Output di un generatore: solo geometria e semantica."""

    width: int
    height: int
    rooms: list[Room]
    corridors: list[Corridor]
    graph: dict[int, list[int]]
    seed: int
    style: str
    levels: int = 1
    # Semantica D&D del BSP (TASK-22): indici in `rooms`/`corridors`, non
    # derivati al volo da furnish perche il criterio va congelato nel
    # momento in cui il grafo e ancora quello "visibile" (prima di
    # eventuali scorciatoie segrete che non devono contare come snodi
    # tattici). Campi opzionali e retrocompatibili: i generatori diversi
    # da bsp.py possono ignorarli.
    tactical_rooms: list[int] = field(default_factory=list)
    long_corridor_indices: list[int] = field(default_factory=list)
    # Vano scale di un edificio multi-piano (TASK-27/§9.2): stesso Rect su
    # ogni piano per costruzione, altrimenti la mappa non si legge al
    # tavolo. None per un dungeon a un livello senza scale.
    stairs_rect: Rect | None = None
    # Griglia booleana del layer cave nativo (TASK-32/decision-1), a
    # risoluzione sotto-cella: (4*width+3) x (4*height+3) celle, 1=scavato.
    # None per i generatori a stanze (bsp/building/city): una grotta non ha
    # Room/Corridor rettangolari, quindi non si presta al modello a stanze
    # e usa questo campo al loro posto (rooms/corridors restano []).
    cave_grid: list[list[int]] | None = None
    # Camere di giunzione della variante fognature (TASK-33): None/[] per
    # gli altri generatori. I canali ortogonali non hanno un campo proprio,
    # sono Corridor come qualunque altro canale (rooms resta [], corridors
    # li contiene tutti).
    chambers: list[Chamber] = field(default_factory=list)
    # Campi dedicati al generatore cittadino (TASK-35/§9.4): come cave_grid
    # e chambers, city.py non si presta al modello a stanze (rooms/corridors
    # restano []). Una piazza e un semplice Rect; una via e una Street
    # (polilinea + larghezza, vedi sopra); ogni edificio e un Blueprint
    # completo (con le sue Room, il suo stairs_rect) gia tradotto in
    # coordinate assolute della mappa cittadina, cosi compose.py puo
    # disegnarlo con draw_building() esattamente come farebbe per un edificio
    # a se stante, senza forzare piu edifici dentro un unico bounding
    # box/tetto.
    streets: list[Street] = field(default_factory=list)
    plazas: list[Rect] = field(default_factory=list)
    buildings: list["Blueprint"] = field(default_factory=list)
    # Edifici dei preset di scala astratti "quartiere"/"citta"
    # (TASK-41/decision-2): un rettangolo di ingombro invece di un Blueprint
    # completo. A quelle scale un lotto e piu piccolo di quanto
    # building.generate pretenda per lato (stanza minima piu il suo
    # margine): la geometria a stanze non e rappresentabile, ed e per questo
    # che decision-2 prevede per questi preset una rappresentazione astratta.
    # I due campi si escludono a vicenda: `buildings` e popolato dal preset
    # "isolato", `building_footprints` dai preset "quartiere"/"citta".
    building_footprints: list[Rect] = field(default_factory=list)
