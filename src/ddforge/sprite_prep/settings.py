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


# Non c'e' piu' un RedSettings (TASK-53): la procedura non tocca piu' il
# colore. Due giri di normalizzazione del rosso dei tetti (per dare a
# Dungeondraft un canale di ricolorabilita' uniforme) hanno prodotto pixel
# rossi dove non dovevano essercene - prima su travature in legno e
# contorni a inchiostro, poi su accenti isolati come salumi, dettagli su
# pozzi/ringhiere e tessitura dei muretti. Jay ha deciso di rinunciare al
# canale di ricolorabilita': i PNG mantengono esattamente i colori del JPEG
# di partenza, tetto compreso.


CATEGORY_CANVAS = {"C1": 1024, "C2": 768, "C3": 512, "C4": 256}
