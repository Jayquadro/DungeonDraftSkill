"""Entry point della CLI ddforge.

Sottocomandi previsti in docs/SPEC.md §8: generate, validate, inspect,
catalog, preview. Le implementazioni arrivano milestone per milestone
(TASK-16, TASK-24, TASK-4, TASK-37); qui il parser espone gia l'interfaccia
completa cosi `ddforge --help` la documenta fin da subito.
"""

import argparse
import sys
from pathlib import Path


def _cmd_generate(args: argparse.Namespace) -> int:
    raise NotImplementedError("ddforge generate: implementato in TASK-24")


def _cmd_validate(args: argparse.Namespace) -> int:
    raise NotImplementedError("ddforge validate: implementato in TASK-16")


def _cmd_inspect(args: argparse.Namespace) -> int:
    raise NotImplementedError("ddforge inspect: implementato in TASK-16")


def _cmd_catalog(args: argparse.Namespace) -> int:
    import json

    from ddforge.assets import build_catalog

    docs = []
    for path in args.from_template:
        with open(path, encoding="utf-8") as f:
            docs.append(json.load(f))

    catalog = build_catalog(*docs)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")

    counts = ", ".join(f"{k}={len(v)}" for k, v in catalog.items() if k != "packs")
    print(f"Scritto {out_path}: {len(catalog['packs'])} pack, {counts}")
    return 0


def _cmd_preview(args: argparse.Namespace) -> int:
    raise NotImplementedError("ddforge preview: implementato in TASK-37")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ddforge",
        description="Generatore procedurale di mappe .dungeondraft_map per Dungeondraft.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_generate = subparsers.add_parser("generate", help="genera una nuova mappa")
    p_generate.add_argument("algorithm", choices=["dungeon", "building", "cave", "city"])
    p_generate.add_argument("--template", required=True, help="template .dungeondraft_map di partenza")
    p_generate.add_argument("--out", required=True, help="percorso del file da scrivere")
    p_generate.add_argument("--width", type=int, default=40)
    p_generate.add_argument("--height", type=int, default=40)
    p_generate.add_argument("--rooms", type=int, default=8)
    p_generate.add_argument("--seed", type=int, default=0)
    p_generate.add_argument("--style", default=None, help="palette semantica, es. crypt, tavern, sewer")
    p_generate.add_argument("--lights", action="store_true")
    p_generate.add_argument("--furnish", choices=["none", "light", "medium", "heavy"], default="none")
    p_generate.set_defaults(func=_cmd_generate)

    p_validate = subparsers.add_parser("validate", help="valida un file .dungeondraft_map")
    p_validate.add_argument("file")
    p_validate.set_defaults(func=_cmd_validate)

    p_inspect = subparsers.add_parser("inspect", help="dump struttura e statistiche di un file")
    p_inspect.add_argument("file")
    p_inspect.set_defaults(func=_cmd_inspect)

    p_catalog = subparsers.add_parser("catalog", help="rigenera data/assets.json da uno o piu template")
    p_catalog.add_argument(
        "--from", dest="from_template", action="append", required=True,
        help="documento .dungeondraft_map sorgente; ripetibile per unire piu file",
    )
    p_catalog.add_argument("--out", default="data/assets.json")
    p_catalog.set_defaults(func=_cmd_catalog)

    p_preview = subparsers.add_parser("preview", help="renderizza un PNG di anteprima (M6)")
    p_preview.add_argument("file")
    p_preview.set_defaults(func=_cmd_preview)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
