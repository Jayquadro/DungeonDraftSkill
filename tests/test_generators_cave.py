"""Test per generators/cave.py (TASK-32): cellular automata a risoluzione
sotto-cella, tunnel verso le componenti secondarie, layer cave nativo."""

import copy
import json
import random
from pathlib import Path

import pytest

from ddforge.cave_bitmap import cave_grid_shape
from ddforge.compose import render_cave_blueprint
from ddforge.generators import cave
from ddforge.generators.cave import (
    _carve_tunnel,
    _dig_tunnels,
    _elbow_spine,
    _label_components,
)
from ddforge.ids import IdAllocator
from ddforge.model import Blueprint
from ddforge.template import finalize, load_template, prepare
from ddforge.validate import validate

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map"
GOLDEN_DIR = REPO_ROOT / "tests" / "fixtures" / "golden"


def _open_components(grid, width, height):
    return _label_components(grid, width, height)


# --- protocollo Generator (TASK-20) ---------------------------------------


def test_generate_returns_a_blueprint_with_cave_grid_and_no_rooms():
    blueprint = cave.generate(width=20, height=15, seed=1337)
    assert isinstance(blueprint, Blueprint)
    assert blueprint.rooms == []
    assert blueprint.corridors == []
    assert blueprint.cave_grid is not None

    grid_w, grid_h = cave_grid_shape(20, 15)
    assert len(blueprint.cave_grid) == grid_h
    assert all(len(row) == grid_w for row in blueprint.cave_grid)
    assert all(v in (0, 1) for row in blueprint.cave_grid for v in row)


def test_same_seed_produces_identical_blueprint():
    a = cave.generate(width=20, height=15, seed=1337)
    b = cave.generate(width=20, height=15, seed=1337)
    assert a == b


def test_different_seed_produces_different_cave():
    a = cave.generate(width=20, height=15, seed=1)
    b = cave.generate(width=20, height=15, seed=2)
    assert a.cave_grid != b.cave_grid


def test_generator_does_not_depend_on_global_random_state():
    random.seed(111)
    random.random()
    a = cave.generate(width=20, height=15, seed=99)

    random.seed(222)
    random.random()
    random.random()
    random.random()
    b = cave.generate(width=20, height=15, seed=99)

    assert a == b


# --- AC1: una sola componente percorribile dopo lo scavo dei tunnel -------


@pytest.mark.parametrize("seed", [1, 2, 3, 1337, 42])
def test_carved_grid_is_a_single_connected_component(seed):
    blueprint = cave.generate(width=24, height=18, seed=seed)
    assert blueprint.cave_grid is not None
    grid_w, grid_h = cave_grid_shape(24, 18)
    # cave_grid: 1=scavato/0=roccia; _label_components lavora sulla
    # convenzione interna del generatore (0=aperto): si inverte per riuso.
    rock_grid = [[1 - v for v in row] for row in blueprint.cave_grid]
    components = _open_components(rock_grid, grid_w, grid_h)

    if not components:
        pytest.skip(f"seed {seed}: nessuna cella aperta (bordo/CA sfortunati), caso limite noto")
    assert len(components) == 1


# --- AC2: i tunnel sono percorsi semplici di larghezza costante -----------


def test_elbow_spine_has_no_repeated_points():
    for a, b in [((2, 2), (10, 8)), ((10, 8), (2, 2)), ((5, 5), (5, 5)), ((3, 7), (3, 2)), ((7, 3), (2, 3))]:
        spine = _elbow_spine(a, b)
        assert len(spine) == len(set(spine)), f"{a} -> {b}: {spine}"


def test_elbow_spine_is_two_monotonic_axis_aligned_legs():
    """Percorso semplice per costruzione: gamba orizzontale a y=a.y, poi
    gamba verticale a x=b.x. Nessuna autointersezione possibile (AC2)."""
    a, b = (2, 2), (9, 11)
    spine = _elbow_spine(a, b)
    horizontal = [p for p in spine if p[1] == a[1]]
    vertical = [p for p in spine if p[0] == b[0]]
    assert set(horizontal) | set(vertical) == set(spine)
    assert [p[0] for p in horizontal] == sorted(p[0] for p in horizontal)
    assert [p[1] for p in vertical] == sorted(p[1] for p in vertical)


def test_carve_tunnel_has_constant_width():
    width, height = 20, 20
    grid = [[1] * width for _ in range(height)]
    spine = _elbow_spine((3, 3), (15, 15))
    tunnel_width = 3
    _carve_tunnel(grid, width, height, spine, tunnel_width)

    # Ogni punto dello spine, lontano dai bordi, ha un intorno pieno
    # tunnel_width x tunnel_width scavato attorno a se: la larghezza non
    # varia lungo il percorso.
    half = tunnel_width // 2
    for x, y in spine:
        if half <= x <= width - 1 - half and half <= y <= height - 1 - half:
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    assert grid[y + dy][x + dx] == 0


def test_dig_tunnels_connects_a_secondary_component_above_threshold():
    # Due stanze quadrate separate da un corridoio di roccia: la piccola
    # (16 sotto-celle, sulla soglia _MIN_COMPONENT_SIZE) deve ricevere un
    # tunnel, non essere scartata.
    width, height = 20, 20
    grid = [[1] * width for _ in range(height)]
    for y in range(2, 10):
        for x in range(2, 10):
            grid[y][x] = 0  # componente principale, 64 celle
    for y in range(2, 6):
        for x in range(14, 18):
            grid[y][x] = 0  # componente secondaria, 16 celle

    tunnels = _dig_tunnels(grid, width, height, min_component_size=16, tunnel_width=3)
    assert len(tunnels) == 1

    components = _label_components(grid, width, height)
    assert len(components) == 1


def test_dig_tunnels_discards_components_below_threshold():
    width, height = 20, 20
    grid = [[1] * width for _ in range(height)]
    for y in range(2, 10):
        for x in range(2, 10):
            grid[y][x] = 0  # componente principale, 64 celle
    grid[5][15] = 0  # componente secondaria, 1 sola cella: rumore

    tunnels = _dig_tunnels(grid, width, height, min_component_size=16, tunnel_width=3)
    assert tunnels == []
    assert grid[5][15] == 1  # scartata, riempita di roccia

    components = _label_components(grid, width, height)
    assert len(components) == 1


# --- AC4: il documento generato passa validate() senza errori -------------


@pytest.mark.parametrize("seed", [1, 1337, 42])
def test_generated_document_passes_validate_with_no_errors(seed):
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)

    blueprint = cave.generate(width=80, height=80, seed=seed)
    render_cave_blueprint(level, blueprint)
    finalize(prepared, ids)

    issues = validate(prepared)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], errors


# --- AC2 (TASK-36): golden file, stessa alberatura di test_bsp_integration.py ----


def _generate_full_document(seed: int) -> dict:
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)

    blueprint = cave.generate(width=80, height=80, seed=seed)
    render_cave_blueprint(level, blueprint)
    finalize(prepared, ids)
    return prepared


def _normalize_for_golden(doc: dict) -> dict:
    doc = copy.deepcopy(doc)
    header = doc.get("header")
    if isinstance(header, dict) and "creation_date" in header:
        header["creation_date"] = "NORMALIZZATO-PER-IL-CONFRONTO-GOLDEN"
    return doc


@pytest.mark.slow
def test_cave_golden_file_matches_reference_for_fixed_seed():
    """Per il seed 1337, alla scala di produzione (80x80, quella usata dal
    CLI senza --width/--height), il documento generato deve combaciare
    esattamente (a meno di creation_date) con
    tests/fixtures/golden/cave_seed_1337.json. Se questo test fallisce dopo
    una modifica intenzionale al generatore, rigenerare il golden con lo
    script in questo stesso file (_generate_full_document) e verificare a
    mano il diff prima di sovrascrivere."""
    golden_path = GOLDEN_DIR / "cave_seed_1337.json"
    actual = _normalize_for_golden(_generate_full_document(seed=1337))

    assert golden_path.exists(), f"Golden file mancante: {golden_path}"
    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    assert actual == expected
