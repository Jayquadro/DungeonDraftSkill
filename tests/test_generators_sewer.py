"""Test per generators/sewer.py (TASK-33): griglia di canali ortogonali,
camere di giunzione circolari, connessione della rete (AC1)."""

import random
from collections import deque
from pathlib import Path

import pytest

from ddforge.assets import load_catalog, palette_for
from ddforge.compose import render_sewer_blueprint
from ddforge.generators import sewer
from ddforge.ids import IdAllocator
from ddforge.model import Blueprint
from ddforge.template import finalize, load_template, prepare
from ddforge.validate import validate

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map"


def _reachable(graph, start):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


# --- protocollo Generator (TASK-20) ----------------------------------------


def test_generate_returns_a_blueprint_with_chambers_and_corridors_no_rooms():
    blueprint = sewer.generate(width=40, height=40, seed=1337)
    assert isinstance(blueprint, Blueprint)
    assert blueprint.rooms == []
    assert blueprint.corridors != []
    assert blueprint.chambers != []
    assert blueprint.style == "sewer"


def test_same_seed_produces_identical_blueprint():
    a = sewer.generate(width=40, height=40, seed=1337)
    b = sewer.generate(width=40, height=40, seed=1337)
    assert a == b


def test_different_seed_produces_a_different_network():
    a = sewer.generate(width=40, height=40, seed=1)
    b = sewer.generate(width=40, height=40, seed=2)
    assert a.corridors != b.corridors or a.chambers != b.chambers


def test_generator_does_not_depend_on_global_random_state():
    random.seed(111)
    random.random()
    a = sewer.generate(width=40, height=40, seed=99)

    random.seed(222)
    random.random()
    random.random()
    random.random()
    b = sewer.generate(width=40, height=40, seed=99)

    assert a == b


# --- AC1: rete di canali ortogonali connessa, con camere circolari --------


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_network_is_a_single_connected_component(seed):
    blueprint = sewer.generate(width=40, height=40, seed=seed)
    reachable = _reachable(blueprint.graph, 0)
    assert reachable == set(range(len(blueprint.chambers)))


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_every_corridor_is_axis_aligned(seed):
    """'Griglia di canali ortogonali' (SPEC.md §9.3): ogni canale e dritto,
    orizzontale o verticale, mai diagonale."""
    blueprint = sewer.generate(width=40, height=40, seed=seed)
    for corridor in blueprint.corridors:
        if corridor.horizontal:
            assert corridor.y1 < corridor.y2
        else:
            assert corridor.x1 < corridor.x2


def test_exactly_one_chamber_is_the_entrance_with_a_door():
    blueprint = sewer.generate(width=40, height=40, seed=7)
    doors = [c for c in blueprint.chambers if c.door]
    assert len(doors) == 1
    # La camera d'ingresso e il nodo d'angolo (0,0): al massimo 2 lati
    # collegati (E, S), quindi resta sempre almeno un arco libero per la
    # porta (draw_chamber), qualunque seed.
    assert doors[0].connected <= {"E", "S"}


@pytest.mark.parametrize("seed", range(20))
def test_every_chamber_has_at_least_one_connection(seed):
    """Ogni camera viene dall'albero di copertura (Kruskal randomizzato su
    tutta la griglia): nessun nodo isolato, per costruzione."""
    blueprint = sewer.generate(width=40, height=40, seed=seed)
    assert all(len(c.connected) >= 1 for c in blueprint.chambers)


# --- AC4: il documento generato passa validate() senza errori -------------


@pytest.mark.parametrize("seed", [1, 1337, 42])
def test_generated_document_passes_validate_with_no_errors(seed):
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)

    catalog = load_catalog()
    palette = palette_for("sewer", catalog)

    blueprint = sewer.generate(width=80, height=80, seed=seed)
    render_sewer_blueprint(level, ids, blueprint, palette)
    finalize(prepared, ids)

    issues = validate(prepared)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], errors
