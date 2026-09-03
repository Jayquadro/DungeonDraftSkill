"""Allocazione dei node_id esadecimali univoci in tutto il documento.

Vedi docs/SPEC.md §6.2 e §12 (base di partenza verificata).
"""


def _iter_node_ids(value):
    """Cammina ricorsivamente una struttura JSON e produce ogni valore di 'node_id'."""
    if isinstance(value, dict):
        for key, v in value.items():
            if key == "node_id":
                yield v
            else:
                yield from _iter_node_ids(v)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_node_ids(item)


class IdAllocator:
    """Alloca node_id esadecimali univoci, porte incluse."""

    def __init__(self, start: int = 0x1000) -> None:
        self.n = start

    def next(self) -> str:
        """Restituisce l'id esadecimale successivo, es. '1001'."""
        self.n += 1
        return format(self.n, "x")

    @property
    def next_free(self) -> str:
        """Valore da scrivere in world.next_node_id."""
        return format(self.n + 1, "x")

    @classmethod
    def from_document(cls, doc: dict) -> "IdAllocator":
        """Inizializza partendo dal max id gia presente nel documento (ricorsivo)."""
        max_id = 0
        for node_id in _iter_node_ids(doc):
            try:
                value = int(str(node_id), 16)
            except ValueError:
                continue
            max_id = max(max_id, value)
        return cls(start=max_id)
