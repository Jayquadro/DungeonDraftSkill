"""Serializzazione dei tipi Godot usati da Dungeondraft.

Unico modulo del progetto che costruisce le stringhe Vector2 / PoolVector2Array
e i colori ARGB. Vedi docs/SPEC.md §6.1, base verificata in §12.
"""

import decimal
import re
from typing import Sequence

GRID = 256  # pixel per quadretto D&D (5 ft)

_NUMBER = r"-?\d+(?:\.\d+)?"
_PV2_RE = re.compile(rf"^PoolVector2Array\(\s*((?:{_NUMBER}\s*,\s*)*{_NUMBER})?\s*\)$")


def _fmt_number(n: float) -> str:
    """Interi senza '.0', float con la rappresentazione minima di Python.

    repr() passa alla notazione scientifica sotto 1e-4 (es. '8.57e-05'), che
    ne' il letterale Godot ne' _NUMBER/_PV2_RE sopra riconoscono: puo
    capitare con coordinate vicine a zero per errore di arrotondamento
    (osservato nel preset "citta" di generators/city.py, isolati/vie di
    meno di un quadretto amplificano il rumore in virgola mobile). Se
    succede, decimal.Decimal riespande le stesse cifre di repr() in
    notazione posizionale, senza perdere precisione (round-trip esatto)."""
    if isinstance(n, int) or (isinstance(n, float) and n.is_integer()):
        return str(int(n))
    s = repr(float(n))
    if "e" in s:
        s = format(decimal.Decimal(s), "f")
    return s


def v2(x: float, y: float) -> str:
    """Vector2 -> 'Vector2( 256, 512 )'. Spazi interni obbligatori."""
    return f"Vector2( {_fmt_number(x)}, {_fmt_number(y)} )"


def pv2(points: Sequence[tuple[float, float]]) -> str:
    """Punti -> 'PoolVector2Array( x1, y1, x2, y2, ... )', coordinate appiattite."""
    flat = ", ".join(_fmt_number(c) for p in points for c in p)
    return f"PoolVector2Array( {flat} )"


def parse_pv2(s: str) -> list[tuple[float, float]]:
    """Inverso di pv2(). Solleva ValueError se la stringa non e una PoolVector2Array valida."""
    if not _PV2_RE.match(s):
        raise ValueError(f"Non e una PoolVector2Array valida: {s!r}")
    inner = s[s.index("(") + 1 : s.rindex(")")].strip()
    if not inner:
        return []
    numbers = [float(x) for x in inner.split(",")]
    if len(numbers) % 2 != 0:
        raise ValueError(f"Numero dispari di coordinate in: {s!r}")
    return [(numbers[i], numbers[i + 1]) for i in range(0, len(numbers), 2)]


def argb(rgb: str, alpha: int = 255) -> str:
    """'aabbcc' -> 'ffaabbcc'. Alpha per primo, 8 cifre sempre."""
    if not re.fullmatch(r"[0-9a-fA-F]{6}", rgb):
        raise ValueError(
            f"argb() richiede esattamente 6 cifre esadecimali RGB, ricevuto: {rgb!r}"
        )
    if not (0 <= alpha <= 255):
        raise ValueError(f"alpha deve essere in [0, 255], ricevuto: {alpha!r}")
    return f"{alpha:02x}{rgb.lower()}"


def grid_to_px(n: float) -> float:
    """Quadretti -> pixel."""
    return n * GRID
