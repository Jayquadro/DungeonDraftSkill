"""Censimento degli elementi urbani notevoli (TASK-48 AC7).

AC7 chiede che le proporzioni siano MISURATE e documentate su piu' seed e per
ciascun preset, non affermate. Questo script produce la misura; la tabella che
ne esce e' riportata in docs/SPEC.md §9.4.

    python scripts/city_landmarks_census.py                  # 20 seed, 78x78
    python scripts/city_landmarks_census.py --seeds 50
    python scripts/city_landmarks_census.py --markdown        # tabelle per SPEC.md

Il canvas di default e' 78x78, cioe' l'area utile del solo template di
produzione reale (templates/blank_80x80.dungeondraft_map): misurare su un
canvas che nessuno usa darebbe numeri veri e inutili.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ddforge.generators import city  # noqa: E402
from ddforge.generators import landmarks as lm  # noqa: E402

SCALES = ("isolato", "quartiere", "citta")


def _measure(scale: str, seeds: int, size: int) -> dict:
    per_kind: Counter = Counter()
    structures: Counter = Counter()
    buildings = 0
    marks = 0
    gates = 0
    bridges = 0
    for seed in range(seeds):
        blueprint = city.generate(width=size, height=size, seed=seed, scale=scale)
        buildings += len(blueprint.buildings) + len(blueprint.building_footprints)
        marks += len(blueprint.landmarks)
        per_kind.update(mark.kind for mark in blueprint.landmarks)
        for key, field in (("mura", "walls"), ("fiume", "river"), ("porto", "port")):
            if getattr(blueprint, field) is not None:
                structures[key] += 1
        if blueprint.walls is not None:
            gates += len(blueprint.walls.gates)
        bridges += len(blueprint.bridges)
    return {
        "seeds": seeds, "buildings": buildings, "marks": marks,
        "per_kind": per_kind, "structures": structures, "gates": gates, "bridges": bridges,
    }


def _print_plain(scale: str, data: dict) -> None:
    seeds = data["seeds"]
    print(f"\n=== preset {scale} ({seeds} seed) ===")
    print(f"edifici ordinari per mappa : {data['buildings'] / seeds:8.1f}")
    print(f"luoghi notevoli per mappa  : {data['marks'] / seeds:8.1f}")
    share = data["marks"] / max(1, data["buildings"] + data["marks"])
    print(f"quota di luoghi sul totale : {share:8.1%}")
    for key in ("mura", "fiume", "porto"):
        if scale in lm.STRUCTURE_SCALES[key]:
            print(f"mappe con {key:<7}         : {data['structures'][key]:4d}/{seeds}")
    print(f"porte per mappa            : {data['gates'] / seeds:8.2f}")
    print(f"ponti per mappa            : {data['bridges'] / seeds:8.2f}")
    print(f"{'luogo':<16}{'tot':>6}{'per mappa':>12}  tipo")
    for kind in lm.LANDMARK_KINDS:
        if scale not in kind.scales:
            continue
        total = data["per_kind"][kind.key]
        tipo = "unico" if kind.unique else f"comune (rate {kind.rate})"
        print(f"{kind.key:<16}{total:>6}{total / seeds:>12.2f}  {tipo}")


def _print_markdown(results: dict) -> None:
    seeds = next(iter(results.values()))["seeds"]
    print(f"\n<!-- generato da scripts/city_landmarks_census.py --seeds {seeds} -->\n")
    print("| misura | " + " | ".join(SCALES) + " |")
    print("|---|" + "---|" * len(SCALES))
    rows = [
        ("edifici ordinari per mappa", lambda d: f"{d['buildings'] / d['seeds']:.0f}"),
        ("luoghi notevoli per mappa", lambda d: f"{d['marks'] / d['seeds']:.1f}"),
        ("quota di luoghi sul totale", lambda d: f"{d['marks'] / max(1, d['buildings'] + d['marks']):.0%}"),
        ("tipi di luogo ammissibili", lambda d: str(sum(1 for k in lm.LANDMARK_KINDS if d["scale"] in k.scales))),
        ("porte per mappa", lambda d: f"{d['gates'] / d['seeds']:.2f}"),
        ("ponti per mappa", lambda d: f"{d['bridges'] / d['seeds']:.2f}"),
    ]
    for key in ("mura", "fiume", "porto"):
        rows.append((
            f"mappe con {key}",
            lambda d, key=key: (
                f"{d['structures'][key]}/{d['seeds']}" if d["scale"] in lm.STRUCTURE_SCALES[key] else "n/d"
            ),
        ))
    for label, render in rows:
        print(f"| {label} | " + " | ".join(render(results[s]) for s in SCALES) + " |")

    print("\n| luogo | tipo | isolato | quartiere | citta |")
    print("|---|---|---|---|---|")
    for kind in lm.LANDMARK_KINDS:
        tipo = "unico" if kind.unique else "comune"
        cells = []
        for scale in SCALES:
            if scale not in kind.scales:
                cells.append("-")
            else:
                cells.append(f"{results[scale]['per_kind'][kind.key] / seeds:.2f}")
        print(f"| {kind.key} | {tipo} | " + " | ".join(cells) + " |")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--size", type=int, default=78)
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args(argv)

    results = {}
    for scale in SCALES:
        data = _measure(scale, args.seeds, args.size)
        data["scale"] = scale
        results[scale] = data

    if args.markdown:
        _print_markdown(results)
    else:
        for scale in SCALES:
            _print_plain(scale, results[scale])
    return 0


if __name__ == "__main__":
    sys.exit(main())
