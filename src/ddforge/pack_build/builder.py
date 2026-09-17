"""Assembla la cartella del pack a partire dai PNG gia' pronti (assets/sprites/, TASK-50)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ddforge.sprite_prep.manifest import MANIFEST

from .metadata import build_pack_json, resolve_pack_id
from .preview import build_contact_sheet
from .settings import PackSettings

# Oggi ogni voce del manifest di sprite_prep e' un object (C1-C4): nessuna
# texture di terreno (C7) ancora nel manifest. Le due cartelle si creano
# comunque vuote, perche' fanno parte della struttura che il packer di
# Dungeondraft si aspetta (AC1) - si popoleranno quando una voce C7 arrivera'
# nel manifest di sprite_prep.
_TEXTURES_OBJECTS = "textures/objects"
_TEXTURES_TERRAIN = "textures/terrain"
_TEXTURES_PATTERNS_NORMAL = "textures/patterns/normal"


def assemble_pack(
    sprites_dir: Path,
    dist_dir: Path,
    pack: PackSettings | None = None,
    id_file: Path | None = None,
) -> dict:
    pack = pack or PackSettings()
    id_file = id_file or Path("data/pack_id.txt")

    root = dist_dir / pack.folder
    objects_dir = root / _TEXTURES_OBJECTS
    objects_dir.mkdir(parents=True, exist_ok=True)
    (root / _TEXTURES_TERRAIN).mkdir(parents=True, exist_ok=True)
    (root / _TEXTURES_PATTERNS_NORMAL).mkdir(parents=True, exist_ok=True)

    copied: list[Path] = []
    missing: list[str] = []
    for job in MANIFEST:
        src = sprites_dir / job.filename
        if not src.exists():
            missing.append(job.filename)
            continue
        dst = objects_dir / job.filename
        shutil.copyfile(src, dst)
        copied.append(dst)

    pack_id = resolve_pack_id(id_file)
    manifest_json = build_pack_json(pack, pack_id)
    (root / "pack.json").write_text(
        json.dumps(manifest_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if copied:
        build_contact_sheet(copied).save(root / "preview.png", format="PNG")

    return {
        "folder": root,
        "pack_id": pack_id,
        "copiati": [p.name for p in copied],
        "mancanti": missing,
    }
