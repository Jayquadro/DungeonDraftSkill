"""Elabora un file grezzo secondo la sua voce di manifest, verifica il risultato."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image

from . import imaging
from .imaging import ProcessingError, ProcessResult
from .manifest import SpriteJob
from .settings import ScaleSettings, ShadowSettings


def load_raw(path: Path) -> Image.Image:
    img = Image.open(path)
    img.load()
    return img.convert("RGB")


def process_job(
    raw: Image.Image,
    job: SpriteJob,
    scale: ScaleSettings,
    shadow: ShadowSettings,
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
    # Nessuna normalizzazione del colore (TASK-53: tolto su richiesta di Jay
    # dopo due giri di correzione insufficienti - il canale di ricolorabilita'
    # di Dungeondraft non serve a questo pacchetto). Il tetto resta esattamente
    # come disegnato nel JPEG di partenza.
    sprite = imaging.add_shadow(sprite, side, shadow)

    warnings.extend(validate_object(sprite, job, scale, obj_size=obj.size))
    return ProcessResult(image=sprite, warnings=warnings, info=info)


def validate_object(
    sprite: Image.Image,
    job: SpriteJob,
    scale: ScaleSettings,
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

    return warnings
