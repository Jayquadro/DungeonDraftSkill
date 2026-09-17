"""preview.png: tutti gli sprite del pack affiancati, per giudicare la coerenza d'insieme (AC4)."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

_PARCHMENT = (214, 196, 160, 255)
_LABEL_INK = (60, 45, 30, 255)


def build_contact_sheet(paths: list[Path], cell: int = 160, columns: int = 8) -> Image.Image:
    columns = max(1, min(columns, len(paths)))
    rows = math.ceil(len(paths) / columns)
    label_h = 18
    sheet = Image.new("RGBA", (columns * cell, rows * (cell + label_h)), _PARCHMENT)
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        with Image.open(path) as im:
            thumb = im.convert("RGBA")
            thumb.thumbnail((cell - 8, cell - 8), Image.Resampling.LANCZOS)
        col, row = i % columns, i // columns
        x = col * cell + (cell - thumb.width) // 2
        y = row * (cell + label_h) + (cell - thumb.height) // 2
        sheet.alpha_composite(thumb, (x, y))
        label = path.stem.removeprefix("nm_")[:22]
        draw.text((col * cell + 4, row * (cell + label_h) + cell), label, fill=_LABEL_INK)
    return sheet
