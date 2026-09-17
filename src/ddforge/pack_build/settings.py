"""Metadati del pack: stessi default di sprite-batch.zip/catalogo.yaml (`pacchetto:`).

Niente soglie di ricolorabilita' qui (TASK-53): il pack non offre piu' il
canale custom_color di Dungeondraft, vedi metadata.build_pack_json.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackSettings:
    name: str = "Nova Mistralis Città"
    folder: str = "NovaMistralisCitta"
    author: str = "Jay"
    version: str = "1.0"
