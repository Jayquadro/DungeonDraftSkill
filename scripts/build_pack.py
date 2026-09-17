"""Assembla la cartella del pack Dungeondraft dai PNG pronti (TASK-51).

    python scripts/build_pack.py                          # assets/sprites/ -> dist/NovaMistralisCitta/
    python scripts/build_pack.py --input X --output Y

Copia i PNG del manifest di TASK-50 in textures/objects/, crea le cartelle
textures/terrain/ e textures/patterns/normal/ (vuote finche' il manifest non
ha voci di terreno), scrive pack.json (con le stesse soglie di ricolorabilita'
usate per normalizzare i tetti, TASK-50) e preview.png. L'id del pack resta
stabile fra una riassemblata e l'altra (persistito in --id-file). Dettagli in
docs/pack-assembly.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ddforge.pack_build.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
