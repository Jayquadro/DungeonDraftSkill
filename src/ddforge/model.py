"""Modello dati intermedio fra i generatori e la serializzazione.

I generatori producono Blueprint, non JSON: cosi restano testabili senza
toccare il formato. Flusso: generatore -> Blueprint -> compose -> build -> JSON.
Vedi docs/SPEC.md §6.4. Implementato in TASK-9.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Rect:
    """Rettangolo in coordinate-quadretto. x2/y2 esclusivi."""

    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def w(self) -> int:
        return self.x2 - self.x1

    @property
    def h(self) -> int:
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
    corridors: list[Rect]
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
