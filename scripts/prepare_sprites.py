"""Porta gli sprite grezzi (JPEG, fondo magenta) al PNG pronto per il pack (TASK-50).

    python scripts/prepare_sprites.py                         # assets/ -> assets/sprites/
    python scripts/prepare_sprites.py --only ospedale,faro     # solo questi due
    python scripts/prepare_sprites.py --input X --output Y

Un solo passaggio per cartella: scontorno del magenta, ritaglio e centratura,
canvas per categoria (C1 1024 / C2 768 / C3 512), normalizzazione del rosso dei
tetti, ombra aggiunta in post, salvataggio in PNG con alfa. I numeri sono quelli
di sprite-batch.zip/catalogo.yaml. Dettagli in docs/sprite-postprocessing.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ddforge.sprite_prep.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
