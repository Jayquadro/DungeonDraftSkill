"""Comando: cartella di PNG pronti -> cartella del pack Dungeondraft.

    python -m ddforge.pack_build --input assets/sprites --output dist
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .builder import assemble_pack
from .settings import PackSettings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("assets/sprites"), help="cartella dei PNG pronti (TASK-50)")
    parser.add_argument("--output", type=Path, default=Path("dist"), help="cartella in cui creare il pack")
    parser.add_argument("--id-file", type=Path, default=Path("data/pack_id.txt"), help="dove persistere l'id del pack")
    parser.add_argument("--name", type=str, default=None, help="nome del pack (default: catalogo.yaml)")
    parser.add_argument("--folder", type=str, default=None, help="nome della cartella del pack (default: catalogo.yaml)")
    parser.add_argument("--author", type=str, default=None, help="autore del pack (default: catalogo.yaml)")
    parser.add_argument("--version", type=str, default=None, help="versione del pack (default: catalogo.yaml)")
    args = parser.parse_args(argv)

    defaults = PackSettings()
    pack = PackSettings(
        name=args.name or defaults.name,
        folder=args.folder or defaults.folder,
        author=args.author or defaults.author,
        version=args.version or defaults.version,
    )

    report = assemble_pack(args.input, args.output, pack=pack, id_file=args.id_file)

    print(f"pack:   {pack.name} ({report['pack_id']})")
    print(f"cartella: {report['folder']}")
    print(f"sprite copiati: {len(report['copiati'])}")
    if report["mancanti"]:
        print("mancanti (non in --input, non copiati):")
        for name in report["mancanti"]:
            print(f"  - {name}")

    return 1 if report["mancanti"] else 0


if __name__ == "__main__":
    sys.exit(main())
