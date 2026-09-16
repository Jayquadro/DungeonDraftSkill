"""Passi deterministici del post-processing: scontorno, colore, geometria, ombra.

Ordine per un oggetto: chroma-key magenta -> pulizia alfa -> ritaglio -> scala
e centratura -> normalizzazione/soppressione del rosso -> ombra -> validazione.

Adattato da sprite-batch.zip/spritebatch/postprocess.py: stessa matematica per
colore, geometria e ombra. Il solo passo diverso è lo scontorno, qui uno
chroma-key deterministico sul magenta puro invece di rembg — lo sfondo delle
schede prompt/*.md è sintetico e piatto (#FF00FF), non una foto, quindi uno
scontorno per distanza colore è più affidabile di un modello di segmentazione
pensato per soggetti fotografici, non richiede download di modelli né rete,
ed è riproducibile nei test.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

from .settings import RedSettings, ScaleSettings, ShadowSettings

ALPHA_THRESHOLD = 8
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

MAGENTA = (255, 0, 255)


class ProcessingError(RuntimeError):
    """Lo sprite non può essere elaborato (immagine vuota, scontorno impossibile, ...)."""


@dataclass
class ProcessResult:
    image: Image.Image
    warnings: list[str] = field(default_factory=list)
    info: dict[str, object] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Scontorno del magenta
# --------------------------------------------------------------------------- #


MAGENTA_HUE_DEG = 300.0


def magenta_chroma_key(
    img: Image.Image,
    hue_window_deg: float = 30.0,
    magentaness_high: float = 0.5,
    magentaness_low: float = 0.15,
    despill_strength: float = 1.0,
) -> Image.Image:
    """Rimuove uno sfondo magenta piatto e ripulisce la frangia colorata sul bordo.

    La chiave e' tinta+saturazione, non distanza RGB dal magenta puro: le
    schede chiedono un fondo piatto, ma nei JPEG reali il magenta arriva con
    una leggera vignettatura (piu' scuro agli angoli) che una soglia sulla
    sola distanza RGB scambierebbe per soggetto. Tinta e saturazione restano
    quasi invariate quando cambia solo la luminosita', quindi la chiave regge
    la vignettatura.

    `magentaness` = quanto un pixel e' "magenta": 1 entro `hue_window_deg`
    gradi dalla tinta del magenta (300°) e con saturazione piena, 0 fuori
    dalla finestra di tinta o senza saturazione (grigi, bianchi, neri, mai
    sfondo). Sopra `magentaness_high` il pixel e' sfondo (alfa 0), sotto
    `magentaness_low` e' soggetto pieno (alfa 255), in mezzo l'alfa sfuma
    linearmente — copre la frangia prodotta dalla compressione JPEG sul
    bordo del soggetto.

    Il despill toglie la tinta magenta residua sui pixel di bordo: dove
    R e B superano G (la firma del magenta), li riporta verso il livello di
    G, cosi' un pixel di bordo non resta rosa anche quando l'alfa e' gia'
    parzialmente trasparente. Non e' filtrato per tinta: un soggetto
    genuinamente viola o magenta ne risentirebbe, ma la palette del brief
    esclude colori acidi/neon apposta per questo.
    """
    rgba = np.array(img.convert("RGBA"), dtype=np.float64)
    r, g, b = rgba[..., 0], rgba[..., 1], rgba[..., 2]

    hsv = rgb_to_hsv(rgba[..., :3] / 255.0)
    hue_deg = hsv[..., 0] * 360.0
    saturation = hsv[..., 1]
    hue_dist = np.minimum(np.abs(hue_deg - MAGENTA_HUE_DEG), 360.0 - np.abs(hue_deg - MAGENTA_HUE_DEG))
    hue_term = np.clip(1.0 - hue_dist / hue_window_deg, 0.0, 1.0)
    magentaness = hue_term * saturation

    span = max(magentaness_high - magentaness_low, 1e-6)
    alpha = np.clip((magentaness_high - magentaness) / span * 255.0, 0.0, 255.0)

    spill = np.clip(np.minimum(r, b) - g, 0.0, None) * despill_strength
    r = np.clip(r - spill, 0.0, 255.0)
    b = np.clip(b - spill, 0.0, 255.0)

    out = np.empty_like(rgba)
    out[..., 0] = r
    out[..., 1] = g
    out[..., 2] = b
    out[..., 3] = alpha
    return Image.fromarray(np.round(out).astype(np.uint8), "RGBA")


def has_real_alpha(img: Image.Image, min_transparent_fraction: float = 0.01) -> bool:
    if img.mode != "RGBA":
        return False
    alpha = np.asarray(img.getchannel("A"))
    return float((alpha < 250).mean()) >= min_transparent_fraction


def clean_alpha(img: Image.Image, threshold: int = ALPHA_THRESHOLD) -> Image.Image:
    """Azzera i pixel quasi trasparenti: eliminano aloni e rumore dal bounding box."""
    arr = np.array(img.convert("RGBA"))
    faint = arr[..., 3] < threshold
    arr[faint] = 0
    return Image.fromarray(arr, "RGBA")


def alpha_bbox(img: Image.Image, threshold: int = ALPHA_THRESHOLD) -> tuple[int, int, int, int] | None:
    """Bounding box (left, top, right, bottom) esclusivo dei pixel con alfa >= soglia."""
    alpha = np.asarray(img.convert("RGBA").getchannel("A"))
    ys, xs = np.nonzero(alpha >= threshold)
    if xs.size == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def edges_touched(img: Image.Image, threshold: int = ALPHA_THRESHOLD, tolerance: int = 2) -> int:
    """Quanti dei quattro bordi dell'immagine sono toccati dal soggetto."""
    box = alpha_bbox(img, threshold)
    if box is None:
        return 0
    w, h = img.size
    left, top, right, bottom = box
    return sum((left <= tolerance, top <= tolerance, right >= w - tolerance, bottom >= h - tolerance))


# --------------------------------------------------------------------------- #
# Colore
# --------------------------------------------------------------------------- #


def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    """rgb float in [0,1] (..., 3) -> hsv in [0,1] (..., 3)."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb, axis=-1)
    minc = np.min(rgb, axis=-1)
    delta = maxc - minc
    s = np.where(maxc > 0, delta / np.where(maxc > 0, maxc, 1), 0.0)
    safe = np.where(delta > 0, delta, 1)
    rc = (maxc - r) / safe
    gc = (maxc - g) / safe
    bc = (maxc - b) / safe
    h = np.where(maxc == r, bc - gc, np.where(maxc == g, 2.0 + rc - bc, 4.0 + gc - rc))
    h = np.where(delta > 0, (h / 6.0) % 1.0, 0.0)
    return np.stack([h, s, maxc], axis=-1)


def hsv_to_rgb(hsv: np.ndarray) -> np.ndarray:
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6.0).astype(int) % 6
    f = h * 6.0 - np.floor(h * 6.0)
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    choices_r = [v, q, p, p, t, v]
    choices_g = [t, v, v, q, p, p]
    choices_b = [p, p, t, v, v, q]
    r = np.choose(i, choices_r)
    g = np.choose(i, choices_g)
    b = np.choose(i, choices_b)
    return np.stack([r, g, b], axis=-1)


def _hue_distance_to_red(h: np.ndarray) -> np.ndarray:
    return np.minimum(h, 1.0 - h)


def dungeondraft_red_mask(rgba: np.ndarray, cfg: RedSettings, safety: float = 1.0) -> np.ndarray:
    """Approssimazione dei pixel che Dungeondraft considera 'custom color'.

    Usa le tre soglie di custom_color_overrides: distanza di tinta dal rosso
    (red_tolerance), rossore minimo (qui R - max(G, B)) e saturazione minima.
    """
    rgb = rgba[..., :3].astype(np.float64) / 255.0
    hsv = rgb_to_hsv(rgb)
    redness = rgb[..., 0] - np.maximum(rgb[..., 1], rgb[..., 2])
    return (
        (rgba[..., 3] > 0)
        & (_hue_distance_to_red(hsv[..., 0]) <= cfg.dd_red_tolerance * safety)
        & (redness >= cfg.dd_min_redness / safety)
        & (hsv[..., 1] >= cfg.dd_min_saturation)
    )


def recolorable_fraction(img: Image.Image, cfg: RedSettings) -> float:
    rgba = np.asarray(img.convert("RGBA"))
    opaque = rgba[..., 3] > 0
    if not opaque.any():
        return 0.0
    return float(dungeondraft_red_mask(rgba, cfg).sum() / opaque.sum())


def normalize_roof_red(img: Image.Image, cfg: RedSettings) -> tuple[Image.Image, float]:
    """Porta i rossi dei tetti a tinta 0 e saturazione uniforme, conservando la luminosità."""
    rgba = np.array(img.convert("RGBA"))
    rgb = rgba[..., :3].astype(np.float64) / 255.0
    hsv = rgb_to_hsv(rgb)
    window = cfg.roof_hue_window_deg / 360.0
    mask = (
        (rgba[..., 3] > 0)
        & (_hue_distance_to_red(hsv[..., 0]) <= window)
        & (hsv[..., 1] >= cfg.roof_min_saturation)
        & (hsv[..., 2] >= cfg.roof_min_value)
    )
    hsv[..., 0] = np.where(mask, 0.0, hsv[..., 0])
    hsv[..., 1] = np.where(mask, cfg.roof_saturation, hsv[..., 1])
    out = hsv_to_rgb(hsv)
    rgba[..., :3] = np.where(mask[..., None], np.round(out * 255.0), rgba[..., :3]).astype(np.uint8)
    opaque = max(int((rgba[..., 3] > 0).sum()), 1)
    return Image.fromarray(rgba, "RGBA"), float(mask.sum() / opaque)


def suppress_red(img: Image.Image, cfg: RedSettings) -> tuple[Image.Image, float]:
    """Sposta su una tinta ocra i pixel che Dungeondraft ricolorerebbe."""
    rgba = np.array(img.convert("RGBA"))
    mask = dungeondraft_red_mask(rgba, cfg, safety=cfg.forbidden_safety)
    if mask.any():
        rgb = rgba[..., :3].astype(np.float64) / 255.0
        hsv = rgb_to_hsv(rgb)
        hsv[..., 0] = np.where(mask, cfg.forbidden_target_hue_deg / 360.0, hsv[..., 0])
        out = hsv_to_rgb(hsv)
        rgba[..., :3] = np.where(mask[..., None], np.round(out * 255.0), rgba[..., :3]).astype(np.uint8)
    opaque = max(int((rgba[..., 3] > 0).sum()), 1)
    return Image.fromarray(rgba, "RGBA"), float(mask.sum() / opaque)


# --------------------------------------------------------------------------- #
# Scala, canvas e ombra
# --------------------------------------------------------------------------- #


def _round_up(value: float, step: int) -> int:
    return int(math.ceil(value / step) * step)


def object_side_for_canvas(canvas: int, scale: ScaleSettings, shadow: ShadowSettings | None) -> int:
    """Lato maggiore dell'oggetto che, centrato, lascia il margine anche all'ombra."""
    extent = shadow.extent if shadow else 0.0
    available_half = canvas / 2.0 - scale.margin * canvas
    return max(1, int(math.floor(available_half / (0.5 + extent))))


def canvas_for_object(side: int, scale: ScaleSettings, shadow: ShadowSettings | None) -> int:
    """Canvas minimo che contiene un oggetto centrato di lato `side`, ombra e margine."""
    extent = shadow.extent if shadow else 0.0
    needed = (side * (0.5 + extent)) / (0.5 - scale.margin)
    return _round_up(needed, scale.round_to)


def target_geometry(
    canvas: int,
    scale_mode: str,
    max_size_m: float | None,
    scale: ScaleSettings,
    shadow: ShadowSettings,
    shadow_enabled: bool = True,
) -> tuple[int, int]:
    """(lato oggetto in px, canvas in px)."""
    sh = shadow if shadow_enabled else None
    if scale_mode == "reale":
        if not max_size_m:
            raise ProcessingError("scala 'reale' richiede una dimensione in metri")
        side = max(1, round(max_size_m * scale.px_per_m))
        return side, max(canvas, canvas_for_object(side, scale, sh))
    return object_side_for_canvas(canvas, scale, sh), canvas


def place_centered(obj: Image.Image, side: int, canvas: int) -> Image.Image:
    """Scala l'oggetto (già ritagliato) a lato maggiore `side` e lo centra sul canvas."""
    w, h = obj.size
    factor = side / max(w, h)
    new_size = (max(1, round(w * factor)), max(1, round(h * factor)))
    scaled = obj.resize(new_size, Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    out.paste(scaled, ((canvas - new_size[0]) // 2, (canvas - new_size[1]) // 2), scaled)
    return out


def add_shadow(img: Image.Image, side: int, cfg: ShadowSettings) -> Image.Image:
    """Ombra portata in basso a destra (luce da in alto a sinistra)."""
    offset = max(1, round(cfg.offset * side))
    radius = max(0.5, cfg.blur * side)
    alpha = img.getchannel("A")
    shifted = Image.new("L", img.size, 0)
    shifted.paste(alpha, (offset, offset))
    blurred = shifted.filter(ImageFilter.GaussianBlur(radius))
    shadow_alpha = np.asarray(blurred, dtype=np.float64) * cfg.opacity
    layer = np.zeros((img.size[1], img.size[0], 4), dtype=np.uint8)
    layer[..., :3] = cfg.color
    layer[..., 3] = np.clip(np.round(shadow_alpha), 0, 255).astype(np.uint8)
    return Image.alpha_composite(Image.fromarray(layer, "RGBA"), img)


# --------------------------------------------------------------------------- #
# Salvataggio
# --------------------------------------------------------------------------- #


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)
    with path.open("rb") as fh:
        if fh.read(8) != PNG_SIGNATURE:  # pragma: no cover - difesa
            raise ProcessingError(f"{path} non è un PNG valido")
