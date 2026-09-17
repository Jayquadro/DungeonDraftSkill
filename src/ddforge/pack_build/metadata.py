"""pack.json: id stabile fra una riassemblata e l'altra.

Schema verificato su asset_manifest di .dungeondraft_map reali (docs/SPEC.md
§13, tests/fixtures/*.dungeondraft_map): pack.json duplica quella stessa voce
(docs/format.md §10.2). Non inventare campi qui: solo quelli osservati.
"""

from __future__ import annotations

import secrets
import string
from pathlib import Path

from .settings import PackSettings

_ID_ALPHABET = string.ascii_letters + string.digits
_ID_LENGTH = 8  # lunghezza degli id reali osservati nei fixture (es. "6VxwaRdj", "Hk3gdwPN")


def resolve_pack_id(id_file: Path) -> str:
    """Id del pack: dal file se gia' esiste, altrimenti generato una volta e salvato li'.

    `id_file` va tracciato in git (non nella dist/ ignorata): deve sopravvivere
    a una dist/ ripulita, altrimenti ogni riassemblata produrrebbe un pack
    nuovo agli occhi di Dungeondraft invece di aggiornare quello importato.
    """
    if id_file.exists():
        existing = id_file.read_text(encoding="utf-8").strip()
        if existing:
            return existing
    new_id = "".join(secrets.choice(_ID_ALPHABET) for _ in range(_ID_LENGTH))
    id_file.parent.mkdir(parents=True, exist_ok=True)
    id_file.write_text(new_id, encoding="utf-8")
    return new_id


def build_pack_json(pack: PackSettings, pack_id: str) -> dict:
    return {
        "name": pack.name,
        "id": pack_id,
        "version": pack.version,
        "author": pack.author,
        "keywords": None,
        "allow_3rd_party_mapping_software_to_read": False,
        # enabled=false (TASK-53): gli sprite non hanno piu' un tetto
        # normalizzato a rosso uniforme - Jay ha deciso di rinunciare al
        # canale di ricolorabilita' di Dungeondraft dopo due giri di bug in
        # quella normalizzazione. I tre numeri restano solo perche' i pack
        # reali osservati (tests/fixtures/*.dungeondraft_map) portano sempre
        # questi tre campi anche quando enabled e' false: con enabled=false
        # Dungeondraft non li usa per ricolorare nulla.
        "custom_color_overrides": {
            "enabled": False,
            "min_redness": 0.1,
            "min_saturation": 0.0,
            "red_tolerance": 0.04,
        },
    }
