"""Entry point della CLI ddforge.

Sottocomandi previsti in docs/SPEC.md §8: generate, validate, inspect,
catalog, preview. Le implementazioni arrivano milestone per milestone
(TASK-16, TASK-24, TASK-4, TASK-37); qui il parser espone gia l'interfaccia
completa cosi `ddforge --help` la documenta fin da subito.
"""

import argparse
import sys


def _cmd_generate(args: argparse.Namespace) -> int:
    raise NotImplementedError("ddforge generate: implementato in TASK-24")


def _cmd_validate(args: argparse.Namespace) -> int:
    raise NotImplementedError("ddforge validate: implementato in TASK-16")


def _cmd_inspect(args: argparse.Namespace) -> int:
    raise NotImplementedError("ddforge inspect: implementato in TASK-16")


def _cmd_catalog(args: argparse.Namespace) -> int:
    raise NotImplementedError("ddforge catalog: implementato in TASK-4")


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

    p_catalog = subparsers.add_parser("catalog", help="rigenera data/assets.json da un template")
    p_catalog.add_argument("--from", dest="from_template", required=True)
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
