"""Elabora un file grezzo secondo la sua voce di manifest, verifica il risultato."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image

from . import imaging
from .imaging import ProcessingError, ProcessResult
from .manifest import SpriteJob
from .settings import RedSettings, ScaleSettings, ShadowSettings


def load_raw(path: Path) -> Image.Image:
    img = Image.open(path)
    img.load()
    return img.convert("RGB")


def process_job(
    raw: Image.Image,
    job: SpriteJob,
    scale: ScaleSettings,
    shadow: ShadowSettings,
    red: RedSettings,
) -> ProcessResult:
    warnings: list[str] = []
    info: dict[str, object] = {}

    keyed = imaging.magenta_chroma_key(raw)
    keyed = imaging.clean_alpha(keyed)

    touched = imaging.edges_touched(keyed)
    if touched >= 2:
        warnings.append(
            f"il soggetto tocca {touched} bordi dell'immagine generata: "
            "probabile sfondo rimasto o soggetto tagliato"
        )
    info["soggetto_tocca_bordi"] = touched

    box = imaging.alpha_bbox(keyed)
    if box is None:
        raise ProcessingError("dopo lo scontorno del magenta l'immagine è vuota")
    obj = keyed.crop(box)

    side, canvas = imaging.target_geometry(
        job.canvas, job.scale_mode, job.max_size_m, scale, shadow
    )
    info.update({"lato_oggetto_px": side, "canvas_px": canvas})
    if canvas != job.canvas:
        info["canvas_ampliato_da"] = job.canvas

    sprite = imaging.place_centered(obj, side, canvas)

    if job.red_mode == "tetto":
        sprite, fraction = imaging.normalize_roof_red(sprite, red)
        info["rosso_normalizzato"] = round(fraction, 4)
    elif job.red_mode == "vietato":
        sprite, fraction = imaging.suppress_red(sprite, red)
        info["rosso_rimosso"] = round(fraction, 4)

    sprite = imaging.add_shadow(sprite, side, shadow)

    warnings.extend(validate_object(sprite, job, scale, red, obj_size=obj.size))
    info["ricolorabile"] = round(imaging.recolorable_fraction(sprite, red), 4)
    return ProcessResult(image=sprite, warnings=warnings, info=info)


def validate_object(
    sprite: Image.Image,
    job: SpriteJob,
    scale: ScaleSettings,
    red: RedSettings,
    obj_size: tuple[int, int] | None = None,
) -> list[str]:
    warnings: list[str] = []
    if sprite.mode != "RGBA" or not imaging.has_real_alpha(sprite):
        warnings.append("manca un canale alfa con trasparenza reale")

    w, h = sprite.size
    if w != h:
        warnings.append(f"canvas non quadrato ({w}x{h})")

    box = imaging.alpha_bbox(sprite, threshold=24)
    if box is not None:
        limit = math.floor(scale.margin * w * 0.5)  # tolleranza: metà del margine richiesto
        left, top, right, bottom = box
        if min(left, top, w - right, h - bottom) < limit:
            warnings.append("il contenuto invade il margine trasparente")

    if obj_size and job.size_m and len(job.size_m) >= 2:
        expected = max(job.size_m) / min(job.size_m)
        actual = max(obj_size) / max(min(obj_size), 1)
        if actual / expected > 1.35 or expected / actual > 1.35:
            warnings.append(f"proporzioni {actual:.2f}:1 lontane da quelle attese {expected:.2f}:1")

    fraction = imaging.recolorable_fraction(sprite, red)
    if job.red_mode == "tetto" and fraction < 0.02:
        warnings.append(f"quasi nessun pixel ricolorabile ({fraction:.1%}): tetto rosso non riconosciuto")
    if job.red_mode == "vietato" and fraction > 0.002:
        warnings.append(f"restano pixel ricolorabili ({fraction:.1%}) in uno sprite che non deve cambiare colore")
    return warnings
