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
