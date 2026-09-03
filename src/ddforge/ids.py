"""Allocazione dei node_id esadecimali univoci in tutto il documento.

Vedi docs/SPEC.md §6.2. Implementato in TASK-7.
"""


class IdAllocator:
    """Alloca node_id esadecimali univoci, porte incluse."""

    def __init__(self, start: int = 0x1000) -> None:
        raise NotImplementedError

    def next(self) -> str:
        """Restituisce l'id esadecimale successivo, es. '1001'."""
        raise NotImplementedError

    @property
    def next_free(self) -> str:
        """Valore da scrivere in world.next_node_id."""
        raise NotImplementedError

    @classmethod
    def from_document(cls, doc: dict) -> "IdAllocator":
        """Inizializza partendo dal max id gia presente nel documento."""
        raise NotImplementedError
