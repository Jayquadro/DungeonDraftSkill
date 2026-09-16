"""Numeri del post-processing sprite: stessi valori di sprite-batch.zip/catalogo.yaml.

Non inventare numeri qui: se cambiano vanno cambiati anche nel brief e nelle
schede prompt/*.md, perche' sono gli stessi che quelle schede promettono a Jay.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScaleSettings:
    grid_px: int = 256  # 256 px = 1,5 m
    grid_m: float = 1.5
    margin: float = 0.05  # margine trasparente per lato
    round_to: int = 16

    @property
    def px_per_m(self) -> float:
        return self.grid_px / self.grid_m


@dataclass(frozen=True)
class ShadowSettings:
    offset: float = 0.04  # frazione del lato maggiore dell'oggetto
    blur: float = 0.025
    opacity: float = 0.45
    color: tuple[int, int, int] = (22, 16, 10)

    @property
    def extent(self) -> float:
        """Di quanto l'ombra sporge oltre l'oggetto, come frazione del lato maggiore."""
        return self.offset + 2.0 * self.blur


@dataclass(frozen=True)
class RedSettings:
    # Soglie di Dungeondraft (custom_color_overrides del pack)
    dd_min_redness: float = 0.1
    dd_min_saturation: float = 0.0
    dd_red_tolerance: float = 0.04
    # Normalizzazione dei tetti (rosso: tetto)
    roof_hue_window_deg: float = 25.0
    roof_min_saturation: float = 0.35
    roof_min_value: float = 0.15
    roof_saturation: float = 0.85
    # Soppressione del rosso (rosso: vietato)
    forbidden_target_hue_deg: float = 26.0
    forbidden_safety: float = 1.5


CATEGORY_CANVAS = {"C1": 1024, "C2": 768, "C3": 512, "C4": 256}
