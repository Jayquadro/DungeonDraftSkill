"""Fixture condivise per la suite di test di ddforge."""

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Percorso della cartella tests/fixtures."""
    return FIXTURES_DIR


@pytest.fixture
def reference_8x8_path() -> Path:
    """Percorso del template 8x8 di riferimento (TASK-5).

    Export genuino di terze parti (non di Jay): usato solo per le
    dimensioni dei blob binari (tiles.cells=64, terrain.splat=4096,
    cave.bitmap=154 elementi), coerenti con l'esempio di SPEC.md §2.
    Vedi docs/format.md per la provenienza completa.
    """
    return FIXTURES_DIR / "reference_8x8.dungeondraft_map"


@pytest.fixture
def reference_8x8_doc(reference_8x8_path) -> dict:
    """Documento JSON gia caricato del template 8x8 di riferimento."""
    with open(reference_8x8_path, encoding="utf-8") as f:
        return json.load(f)


# --- campioni del layer cave nativo (TASK-31, per TASK-32) ---
#
# Sono l'UNICA evidenza reale della codifica di `cave.bitmap` in tutto il
# progetto: nessun altro file .dungeondraft_map trovato sul sistema di Jay
# ha il layer cave popolato. Disegnati da Jay in Dungeondraft 1.2.0.1 e
# risalvati dal programma, quindi genuini. Provenienza in docs/format.md
# §14; la codifica che verificano e documentata li.


@pytest.fixture
def cave_rect_path() -> Path:
    """Campione CONTROLLATO: un rettangolo netto di 21x3 quadretti in alto a
    sinistra (Jay: "circa 20x3"), disegnato apposta con bordi netti per
    disambiguare la mappatura bit -> sotto-cella. E' il campione che ha
    permesso di risolvere la codifica."""
    return FIXTURES_DIR / "cave_rect_80x80.dungeondraft_map"


@pytest.fixture
def cave_freehand_path() -> Path:
    """Campione A MANO LIBERA: una caverna organica con un tunnel
    serpeggiante. Contiene anche 1 wall e 1 pattern, resti del prototipo a
    muri poligonali su cui Jay ha disegnato: e un file reale, non ripulito."""
    return FIXTURES_DIR / "cave_freehand_80x80.dungeondraft_map"
