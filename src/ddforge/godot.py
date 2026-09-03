"""Serializzazione dei tipi Godot usati da Dungeondraft.

Unico modulo del progetto che costruisce le stringhe Vector2 / PoolVector2Array
e i colori ARGB. Vedi docs/SPEC.md §6.1. Implementato in TASK-6.
"""

GRID = 256  # pixel per quadretto D&D (5 ft)


def v2(x: float, y: float) -> str:
    """Vector2 -> 'Vector2( 256, 512 )'. Spazi interni obbligatori."""
    raise NotImplementedError


def pv2(points) -> str:
    """Punti -> 'PoolVector2Array( x1, y1, x2, y2, ... )', coordinate appiattite."""
    raise NotImplementedError


def parse_pv2(s: str):
    """Inverso di pv2(). Serve al validatore e ai test di round-trip."""
    raise NotImplementedError


def argb(rgb: str, alpha: int = 255) -> str:
    """'aabbcc' -> 'ffaabbcc'. Alpha per primo, 8 cifre sempre."""
    raise NotImplementedError


def grid_to_px(n: float) -> float:
    """Quadretti -> pixel."""
    raise NotImplementedError
