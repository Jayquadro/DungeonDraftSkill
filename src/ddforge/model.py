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
        raise NotImplementedError

    @property
    def h(self) -> int:
        raise NotImplementedError

    def center(self) -> tuple[float, float]:
        raise NotImplementedError

    def overlaps(self, other: "Rect", margin: int = 0) -> bool:
        raise NotImplementedError

    def shrink(self, n: int) -> "Rect":
        raise NotImplementedError


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
