"""Fixture condivise per la suite di test di ddforge."""

import pytest


@pytest.fixture
def fixtures_dir(request):
    """Percorso della cartella tests/fixtures."""
    return request.path.parent / "fixtures"
