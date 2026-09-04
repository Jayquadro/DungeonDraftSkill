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
