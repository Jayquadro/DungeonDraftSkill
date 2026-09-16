"""Comando: cartella di JPEG grezzi -> cartella di PNG pronti per il pack + rapporto.

    python -m ddforge.sprite_prep --input assets --output assets/sprites
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .batch import format_report_text, run_batch, write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("assets"), help="cartella dei JPEG grezzi")
    parser.add_argument("--output", type=Path, default=Path("assets/sprites"), help="cartella dei PNG finali")
    parser.add_argument("--report", type=Path, default=None, help="dove scrivere rapporto.json (default: <output>/rapporto.json)")
    parser.add_argument("--only", type=str, default=None, help="solo questi sprite, separati da virgola (es. ospedale,faro)")
    args = parser.parse_args(argv)

    only = {name.strip() for name in args.only.split(",")} if args.only else None
    report = run_batch(args.input, args.output, only=only)

    report_path = args.report or (args.output / "rapporto.json")
    write_report(report, report_path)

    print(format_report_text(report))
    print(f"\nrapporto scritto in {report_path}")

    riepilogo = report["riepilogo"]
    return 1 if (riepilogo["errore"] or riepilogo["mancante"]) else 0


if __name__ == "__main__":
    sys.exit(main())
