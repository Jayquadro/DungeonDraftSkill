"""Test per generators/city.py (TASK-35): rete stradale, isolati, lotti,
edifici e piazze (SPEC.md §9.4)."""

import copy
import json
import random
from pathlib import Path

import pytest

from ddforge.assets import load_catalog, palette_for
from ddforge.compose import render_city_blueprint
from ddforge.generators import city
from ddforge.ids import IdAllocator
from ddforge.model import Blueprint
from ddforge.template import finalize, load_template, prepare
from ddforge.validate import validate

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map"
GOLDEN_DIR = REPO_ROOT / "tests" / "fixtures" / "golden"


# --- protocollo Generator ---------------------------------------------------


def test_generate_returns_a_blueprint_with_no_rooms():
    blueprint = city.generate(width=70, height=70, seed=1337)
    assert isinstance(blueprint, Blueprint)
    assert blueprint.rooms == []
    assert blueprint.corridors == []
    assert blueprint.style == "city"
    assert blueprint.streets != []
    assert blueprint.buildings != []


def test_same_seed_produces_identical_blueprint():
    a = city.generate(width=70, height=70, seed=1337)
    b = city.generate(width=70, height=70, seed=1337)
    assert a == b


def test_different_seed_produces_a_different_city():
    a = city.generate(width=70, height=70, seed=1)
    b = city.generate(width=70, height=70, seed=2)
    assert a.streets != b.streets or [bp.rooms for bp in a.buildings] != [bp.rooms for bp in b.buildings]


def test_generator_does_not_depend_on_global_random_state():
    random.seed(111)
    random.random()
    a = city.generate(width=70, height=70, seed=99)

    random.seed(222)
    random.random()
    random.random()
    random.random()
    b = city.generate(width=70, height=70, seed=99)

    assert a == b


# --- AC3: la via principale e' piu larga delle strade secondarie ----------


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_main_street_is_wider_than_every_secondary_street(seed):
    blueprint = city.generate(width=70, height=70, seed=seed)
    widths = [min(s.w, s.h) for s in blueprint.streets]
    main_width = max(widths)  # il primo taglio (depth 0) e' sempre il piu' largo
    assert main_width == pytest.approx(city._MAIN_STREET_WIDTH)
    others = sorted(widths, reverse=True)[1:]
    assert all(main_width > w for w in others), widths


# --- AC1: ogni lotto ha fronte strada, ogni edificio e' accessibile -------


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_every_building_footprint_lies_within_a_block_touching_its_boundary(seed):
    """Ogni edificio piazzato sta dentro l'isolato da cui e' stato ricavato
    E tocca (a meno del margine/arretramento) il lato fronte di quel
    isolato: e' la garanzia costruttiva di fronte-strada (AC1), verificata
    ricalcolando isolati e lotti con lo stesso RNG del generatore."""
    rng = random.Random(seed)
    root = city.Rect(1, 1, 70 - 1, 70 - 1)
    streets: list = []
    blocks = city._build_blocks(
        root, rng, depth=0, streets=streets,
        min_block=city._MIN_BLOCK, max_block=city._MAX_BLOCK,
        main_width=city._MAIN_STREET_WIDTH, secondary_range=city._SECONDARY_STREET_RANGE,
        depth_max=city._DEPTH_MAX,
    )
    n_plazas = 2 if len(blocks) >= 4 else (1 if len(blocks) >= 2 else 0)
    plaza_indices = set(rng.sample(range(len(blocks)), n_plazas)) if n_plazas else set()

    for i, block in enumerate(blocks):
        if i in plaza_indices:
            continue
        for lot, front in city._split_into_lots(block, city._TARGET_LOT_LEN, city._MIN_LOT_LEN):
            assert lot.x1 >= block.x1 and lot.y1 >= block.y1
            assert lot.x2 <= block.x2 and lot.y2 <= block.y2
            # i due lati corti del lotto coincidono coi lati dell'isolato
            if front in (city._TOP, city._BOTTOM):
                assert lot.y1 == block.y1 and lot.y2 == block.y2
            else:
                assert lot.x1 == block.x1 and lot.x2 == block.x2


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_every_building_has_a_working_entrance(seed):
    """building.generate garantisce gia' una porta d'ingresso sul piano
    terra (bsp._ensure_entry, force=True): qui si verifica che city.py non
    perda quella garanzia nel tradurre/piazzare l'edificio."""
    blueprint = city.generate(width=70, height=70, seed=seed)
    for building_bp in blueprint.buildings:
        ground_rooms = [r for r in building_bp.rooms if r.level == 0]
        assert any(room.doors for room in ground_rooms), "nessuna porta al piano terra"


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_no_building_overlaps_a_street_or_a_plaza(seed):
    blueprint = city.generate(width=70, height=70, seed=seed)
    obstacles = list(blueprint.streets) + list(blueprint.plazas)
    for building_bp in blueprint.buildings:
        footprint = city.Rect(
            min(r.rect.x1 for r in building_bp.rooms), min(r.rect.y1 for r in building_bp.rooms),
            max(r.rect.x2 for r in building_bp.rooms), max(r.rect.y2 for r in building_bp.rooms),
        )
        for obstacle in obstacles:
            assert not footprint.overlaps(obstacle), f"{footprint} vs {obstacle}"


# --- AC5: 1-2 piazze con pavimentazione diversa ed elemento centrale ------


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_one_or_two_plazas_are_present(seed):
    blueprint = city.generate(width=70, height=70, seed=seed)
    assert 1 <= len(blueprint.plazas) <= 2


def test_no_building_sits_inside_a_plaza_block():
    """Le piazze sono isolati esclusi dalla suddivisione in lotti (SPEC.md
    §9.4): nessun edificio dovrebbe avere un genitore in blueprint.plazas."""
    blueprint = city.generate(width=70, height=70, seed=1337)
    for plaza in blueprint.plazas:
        for building_bp in blueprint.buildings:
            footprint = city.Rect(
                min(r.rect.x1 for r in building_bp.rooms), min(r.rect.y1 for r in building_bp.rooms),
                max(r.rect.x2 for r in building_bp.rooms), max(r.rect.y2 for r in building_bp.rooms),
            )
            assert not footprint.overlaps(plaza)


# --- AC2/AC4/AC6: rendering end-to-end -------------------------------------


def test_end_to_end_render_through_render_city_blueprint_passes_validate():
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)

    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=70, height=70, seed=1337)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)
    finalize(prepared, ids)

    issues = validate(prepared)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], errors

    level = prepared["world"]["levels"]["0"]
    # AC2: le strade sono add_path, non pattern.
    assert len(level["paths"]) == len(blueprint.streets)
    assert all(p["texture"] == "res://textures/paths/cobble.png" for p in level["paths"])
    # AC4: ogni edificio ha un tetto (un draw_building per edificio).
    assert len(level["roofs"]["roofs"]) == len(blueprint.buildings)


def test_plaza_pattern_uses_a_different_texture_than_buildings_and_has_a_fountain():
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=70, height=70, seed=1337)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)
    finalize(prepared, ids)

    level = prepared["world"]["levels"]["0"]
    plaza_patterns = [p for p in level["patterns"] if p["texture"] == palette.floors["piazza"]]
    assert len(plaza_patterns) == len(blueprint.plazas)
    assert palette.floors["piazza"] != palette.floor

    fountains = [o for o in level["objects"] if o["texture"] == palette.accents["fountain"]]
    assert len(fountains) == len(blueprint.plazas)


# --- AC2 (TASK-36): golden file, stessa alberatura di test_bsp_integration.py ----


def _generate_full_document(seed: int) -> dict:
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=70, height=70, seed=seed)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)
    finalize(prepared, ids)
    return prepared


def _normalize_for_golden(doc: dict) -> dict:
    doc = copy.deepcopy(doc)
    header = doc.get("header")
    if isinstance(header, dict) and "creation_date" in header:
        header["creation_date"] = "NORMALIZZATO-PER-IL-CONFRONTO-GOLDEN"
    return doc


@pytest.mark.slow
def test_city_golden_file_matches_reference_for_fixed_seed():
    """Per il seed 1337 (70x70, la stessa scala usata dagli altri test di
    questo file), il documento generato deve combaciare esattamente (a meno
    di creation_date) con tests/fixtures/golden/city_seed_1337.json. Se
    questo test fallisce dopo una modifica intenzionale al generatore,
    rigenerare il golden con lo script in questo stesso file
    (_generate_full_document) e verificare a mano il diff prima di
    sovrascrivere."""
    golden_path = GOLDEN_DIR / "city_seed_1337.json"
    actual = _normalize_for_golden(_generate_full_document(seed=1337))

    assert golden_path.exists(), f"Golden file mancante: {golden_path}"
    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    assert actual == expected
