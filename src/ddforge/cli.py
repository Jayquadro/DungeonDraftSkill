"""Entry point della CLI ddforge.

Sottocomandi previsti in docs/SPEC.md §8: generate, validate, inspect,
catalog, preview. Le implementazioni arrivano milestone per milestone
(TASK-16, TASK-24, TASK-4, TASK-37); qui il parser espone gia l'interfaccia
completa cosi `ddforge --help` la documenta fin da subito.
"""

import argparse
import sys
from pathlib import Path


_GENERATORS = {}  # popolato pigramente in _cmd_generate: import lazy per stile


def _load_generators() -> dict:
    if not _GENERATORS:
        from ddforge.generators import bsp, building, cave, city, sewer
        _GENERATORS["dungeon"] = bsp
        _GENERATORS["building"] = building
        _GENERATORS["cave"] = cave
        _GENERATORS["sewer"] = sewer
        _GENERATORS["city"] = city
    return _GENERATORS


def _add_lighting(level, ids, blueprint) -> None:
    """Una luce al centro di ogni stanza e al centro di ogni corridoio
    lungo (SPEC.md §9.1: 'furnish ci mette una fonte di luce a meta')."""
    from ddforge.build import add_light

    for room in blueprint.rooms:
        cx, cy = room.rect.center()
        add_light(level, ids, cx, cy)
    for i in blueprint.long_corridor_indices:
        rect = blueprint.corridors[i]
        cx, cy = rect.center()
        add_light(level, ids, cx, cy)


def _add_building_lighting(level_stack, ids, blueprint) -> None:
    """Come _add_lighting, ma una volta per piano (TASK-30): ogni stanza
    riceve la sua luce solo nel livello a cui appartiene (Room.level)."""
    from ddforge.build import add_light
    from ddforge.compose import floor_blueprint, rooms_by_level

    for level_key, floor_rooms in rooms_by_level(blueprint).items():
        level = level_stack.get(str(level_key))
        if level is None or not floor_rooms:
            continue
        _add_lighting(level, ids, floor_blueprint(blueprint, floor_rooms))
        # Il vano scale non e in blueprint.rooms, ma e un ambiente illuminato
        # come gli altri: senza la sua luce resta un pozzo nero in mezzo a un
        # edificio acceso, proprio dove Jay deve riconoscere la scala.
        if blueprint.stairs_rect is not None:
            add_light(level, ids, *blueprint.stairs_rect.center())


def _cmd_generate(args: argparse.Namespace) -> int:
    import random

    from ddforge.assets import load_catalog, palette_for
    from ddforge.compose import (
        draw_building, furnish, furnish_building, render_blueprint, render_cave_blueprint,
        render_city_blueprint, render_sewer_blueprint,
    )
    from ddforge.generators.building import floor_labels as building_labels
    from ddforge.ids import IdAllocator
    from ddforge.template import TemplateError, finalize, load_template, prepare, save
    from ddforge.validate import validate

    generators = _load_generators()
    if args.algorithm not in generators:
        print(f"Errore: lo stile '{args.algorithm}' non e ancora implementato.", file=sys.stderr)
        return 1

    try:
        doc = load_template(args.template)
    except TemplateError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    try:
        catalog = load_catalog()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    is_building = args.algorithm == "building"
    is_cave = args.algorithm == "cave"
    is_sewer = args.algorithm == "sewer"
    is_city = args.algorithm == "city"
    style_name = args.style or (args.building_type if is_building else args.algorithm)
    try:
        palette = palette_for(style_name, catalog)
    except ValueError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    if is_building:
        # Senza --width/--height esplicite, ogni tipologia ha il suo ingombro
        # realistico: a 1.5 m per quadretto il default generico di 40x40 vale
        # 60x60 METRI, cioe un isolato e non una taverna (TASK-30).
        from ddforge.generators.building import default_size

        default_w, default_h = default_size(args.building_type)
        blueprint = generators[args.algorithm].generate(
            width=args.width if args.width is not None else default_w,
            height=args.height if args.height is not None else default_h,
            seed=args.seed,
            building_type=args.building_type, l_shaped=args.l_shaped,
        )
    elif is_city:
        # --scale e l'unico parametro esclusivo di city (TASK-41): passato
        # solo qui, come --building-type/--l-shaped per building.
        blueprint = generators[args.algorithm].generate(
            width=args.width if args.width is not None else 40,
            height=args.height if args.height is not None else 40,
            seed=args.seed, scale=args.scale,
        )
    else:
        blueprint = generators[args.algorithm].generate(
            width=args.width if args.width is not None else 40,
            height=args.height if args.height is not None else 40,
            seed=args.seed, rooms=args.rooms,
        )

    # Ogni piano riceve un nome proprio: senza, ereditano tutti la label del
    # template ("Ground") e in Dungeondraft non si distingue un piano
    # dall'altro (gate umano M4, TASK-30).
    labels = building_labels(blueprint.levels) if is_building else None
    prepared = prepare(doc, levels=blueprint.levels, labels=labels)
    ids = IdAllocator.from_document(prepared)

    if is_building:
        level_stack = prepared["world"]["levels"]
        draw_building(level_stack, ids, blueprint, palette)
        if args.furnish != "none":
            furnish_building(level_stack, ids, blueprint, palette, density=args.furnish, rng=random.Random(args.seed))
        if args.lights:
            _add_building_lighting(level_stack, ids, blueprint)
    elif is_cave:
        # Una grotta non ha Room/Corridor (blueprint.cave_grid al loro
        # posto, decision-1): niente furnish/luci, che presumono stanze.
        level = prepared["world"]["levels"]["0"]
        render_cave_blueprint(level, blueprint)
    elif is_sewer:
        # Le camere di giunzione non sono Room (blueprint.chambers al loro
        # posto, TASK-33): niente furnish/luci, stesso motivo di is_cave.
        level = prepared["world"]["levels"]["0"]
        render_sewer_blueprint(level, ids, blueprint, palette)
    elif is_city:
        # Niente furnish/luci qui: presumono un solo Blueprint a stanze come
        # quello passato loro, e blueprint.rooms per una citta e sempre vuoto.
        # Nel preset isolato le stanze vive sono quelle di ogni
        # blueprint.buildings (TASK-35); nei preset quartiere/citta non ce ne
        # sono affatto, gli edifici sono solo ingombri (TASK-41).
        level_stack = prepared["world"]["levels"]
        render_city_blueprint(level_stack, ids, blueprint, palette)
    else:
        level = prepared["world"]["levels"]["0"]
        render_blueprint(level, ids, blueprint, palette)
        if args.furnish != "none":
            furnish(level, ids, blueprint, palette, density=args.furnish, rng=random.Random(args.seed))
        if args.lights:
            _add_lighting(level, ids, blueprint)

    finalize(prepared, ids)

    issues = validate(prepared)
    for issue in issues:
        marker = "ERRORE" if issue.severity == "error" else "AVVISO"
        print(f"[{marker}] {issue.code} {issue.path}: {issue.message}")

    errors = [i for i in issues if i.severity == "error"]
    if errors:
        print(f"\n{len(errors)} errori di validazione: {args.out} NON scritto.", file=sys.stderr)
        return 1

    save(prepared, args.out)
    warnings = [i for i in issues if i.severity == "warning"]
    suffix = f" ({len(warnings)} avvisi)" if warnings else ""
    print(f"\nScritto {args.out}{suffix}")
    return 0


def _load_document(path) -> dict | None:
    """Carica un documento JSON, stampando un messaggio chiaro (non un
    traceback) se il file manca o non e JSON valido."""
    import json

    p = Path(path)
    if not p.exists():
        print(f"Errore: file non trovato: {p}", file=sys.stderr)
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Errore: JSON non valido in {p}: {exc}", file=sys.stderr)
        return None


def _cmd_validate(args: argparse.Namespace) -> int:
    from ddforge.validate import validate

    doc = _load_document(args.file)
    if doc is None:
        return 1

    issues = validate(doc)
    if not issues:
        print("Nessun problema trovato.")
        return 0

    for issue in issues:
        marker = "ERRORE" if issue.severity == "error" else "AVVISO"
        print(f"[{marker}] {issue.code} {issue.path}: {issue.message}")

    n_errors = sum(1 for i in issues if i.severity == "error")
    n_warnings = len(issues) - n_errors
    print(f"\n{n_errors} errori, {n_warnings} avvisi.")
    return 1 if n_errors else 0


def _cmd_inspect(args: argparse.Namespace) -> int:
    doc = _load_document(args.file)
    if doc is None:
        return 1

    header = doc.get("header", {}) if isinstance(doc.get("header"), dict) else {}
    world = doc.get("world", {}) if isinstance(doc.get("world"), dict) else {}
    levels = world.get("levels", {}) if isinstance(world.get("levels"), dict) else {}

    print(f"File: {args.file}")
    print(f"Dimensioni: {world.get('width')} x {world.get('height')} quadretti")
    print(f"Format: {world.get('format')}")
    print(f"Creation build: {header.get('creation_build')}")
    print(f"Livelli: {len(levels)}")

    manifest = header.get("asset_manifest") or []
    print(f"Pack referenziati ({len(manifest)}):")
    for m in manifest:
        if isinstance(m, dict):
            print(f"  - {m.get('id')}: {m.get('name')} ({m.get('author')}, v{m.get('version')})")

    element_lists = ("patterns", "walls", "portals", "paths", "objects", "lights", "texts")
    for level_id, level in levels.items():
        if not isinstance(level, dict):
            continue
        print(f"\nLivello {level_id} ({level.get('label', '')!r}):")
        for name in element_lists:
            items = level.get(name)
            n = len(items) if isinstance(items, list) else 0
            print(f"  {name}: {n}")
        walls = level.get("walls")
        if isinstance(walls, list):
            nested = sum(len(w.get("portals", [])) for w in walls if isinstance(w, dict))
            print(f"  portali annidati nei muri: {nested}")
        roofs = level.get("roofs")
        if isinstance(roofs, dict):
            print(f"  roofs.roofs: {len(roofs.get('roofs') or [])}")

    return 0


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
    from ddforge.preview import PillowMissingError, render_preview

    doc = _load_document(args.file)
    if doc is None:
        return 1

    out = args.out or str(Path(args.file).with_suffix(".png"))
    try:
        render_preview(doc, out, level_id=args.level, scale=args.scale)
    except PillowMissingError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    print(f"Scritto {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ddforge",
        description="Generatore procedurale di mappe .dungeondraft_map per Dungeondraft.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_generate = subparsers.add_parser("generate", help="genera una nuova mappa")
    p_generate.add_argument("algorithm", choices=["dungeon", "building", "cave", "city", "sewer"])
    p_generate.add_argument("--template", required=True, help="template .dungeondraft_map di partenza")
    p_generate.add_argument("--out", required=True, help="percorso del file da scrivere")
    p_generate.add_argument(
        "--width", type=int, default=None,
        help="larghezza in quadretti (1 quadretto = 1.5 m); default 40, "
             "o l'ingombro realistico della tipologia per 'building'",
    )
    p_generate.add_argument("--height", type=int, default=None, help="altezza in quadretti; vedi --width")
    p_generate.add_argument("--rooms", type=int, default=8)
    p_generate.add_argument("--seed", type=int, default=0)
    p_generate.add_argument(
        "--building-type", choices=["tavern", "manor", "warehouse"], default="tavern",
        help="tipologia dell'edificio (solo per l'algoritmo 'building')",
    )
    p_generate.add_argument(
        "--l-shaped", action="store_true",
        help="pianta a L invece che rettangolare (solo per l'algoritmo 'building')",
    )
    p_generate.add_argument(
        "--scale", choices=["isolato", "quartiere", "citta"], default="isolato",
        help="preset di scala della mappa cittadina (solo per l'algoritmo 'city'): "
             "'isolato' = 1 quadretto = 5 ft, edifici completi da giocare al tavolo; "
             "'quartiere' = 1 quadretto = 1 edificio, un quartiere intero visto dall'alto; "
             "'citta' = una citta intera, capace di contenere una decina di quartieri",
    )
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
    p_preview.add_argument(
        "--out", default=None,
        help="percorso del PNG da scrivere; default: il file di input con estensione .png",
    )
    p_preview.add_argument(
        "--level", default=None,
        help="id del livello da renderizzare (es. '0'); default: il primo livello del documento",
    )
    p_preview.add_argument("--scale", type=int, default=8, help="pixel per quadretto nel PNG (default 8)")
    p_preview.set_defaults(func=_cmd_preview)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
