"""Rigenera i golden file del generatore cittadino (TASK-48).

Prima di TASK-48 il golden si rigenerava a mano riusando
`tests/test_generators_city.py::_generate_full_document`. Ora i golden sono
due (con e senza elementi urbani notevoli) e serve uno script, perche'
sovrascriverli a mano dal test e' esattamente il modo in cui un golden smette
di significare qualcosa.

    python scripts/regen_city_golden.py            # mostra cosa cambierebbe
    python scripts/regen_city_golden.py --write    # scrive

Il diff va SEMPRE guardato prima di scrivere: un golden aggiornato senza
leggere il diff e' un test che approva qualunque regressione.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tests"))

GOLDEN_DIR = REPO_ROOT / "tests" / "fixtures" / "golden"
TARGETS = {
    "city_seed_1337.json": False,
    "city_seed_1337_landmarks.json": True,
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="sovrascrive i golden invece di mostrare il diff")
    args = parser.parse_args(argv)

    from test_generators_city import _generate_full_document, _normalize_for_golden

    changed = 0
    for name, landmarks in TARGETS.items():
        path = GOLDEN_DIR / name
        actual = _normalize_for_golden(_generate_full_document(seed=1337, landmarks=landmarks))
        text = json.dumps(actual, indent=2, ensure_ascii=False) + "\n"
        previous = path.read_text(encoding="utf-8") if path.exists() else None
        if previous == text:
            print(f"invariato: {name}")
            continue
        changed += 1
        if args.write:
            path.write_text(text, encoding="utf-8")
            print(f"scritto:   {name}")
        else:
            old_size = len(previous) if previous is not None else 0
            print(f"DIVERSO:   {name} ({old_size} -> {len(text)} byte); riesegui con --write per sovrascrivere")
    return 1 if changed and not args.write else 0


if __name__ == "__main__":
    sys.exit(main())
