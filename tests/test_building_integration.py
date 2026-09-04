"""Test di integrazione e golden file per generators/building.py (TASK-30).

Stesso schema di test_bsp_integration.py (TASK-25): integrazione (genera,
disegna, valida) e golden file (confronto byte-per-byte per un seed fisso).
"""

import copy
import json
import random
from collections import deque
from pathlib import Path

import pytest

from ddforge.assets import load_catalog, palette_for
from ddforge.cli import _add_building_lighting
from ddforge.compose import draw_building, furnish_building
from ddforge.generators import building
from ddforge.ids import IdAllocator
from ddforge.template import finalize, load_template, prepare
from ddforge.validate import validate

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def _bfs_reachable(graph, start=0):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


@pytest.mark.parametrize("building_type", ["tavern", "manor", "warehouse"])
def test_building_integration_has_zero_errors(building_type):
    catalog = load_catalog()
    palette = palette_for(building_type, catalog)
    bp = building.generate(width=40, height=40, seed=1337, building_type=building_type)

    doc = load_template("templates/blank_80x80.dungeondraft_map")
    prepared = prepare(doc, levels=bp.levels)
    ids = IdAllocator.from_document(prepared)
    draw_building(prepared["world"]["levels"], ids, bp, palette)
    finalize(prepared, ids)

    errors = [i for i in validate(prepared) if i.severity == "error"]
    assert errors == []


def test_building_integration_rooms_on_the_same_floor_are_all_reachable():
    bp = building.generate(width=40, height=40, seed=1337, building_type="manor")
    for level in range(bp.levels):
        indices = [i for i, r in enumerate(bp.rooms) if r.level == level]
        if len(indices) < 2:
            continue
        sub_graph = {i: [n for n in bp.graph[i] if n in indices] for i in indices}
        reachable = _bfs_reachable(sub_graph, start=indices[0])
        assert reachable == set(indices)


def _generate_full_document(seed: int) -> dict:
    doc = load_template("templates/blank_80x80.dungeondraft_map")
    bp = building.generate(width=40, height=40, seed=seed, building_type="tavern")

    prepared = prepare(doc, levels=bp.levels)
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("tavern", catalog)

    draw_building(prepared["world"]["levels"], ids, bp, palette)
    furnish_building(prepared["world"]["levels"], ids, bp, palette, density="light", rng=random.Random(seed))
    _add_building_lighting(prepared["world"]["levels"], ids, bp)
    finalize(prepared, ids)
    return prepared


def _normalize_for_golden(doc: dict) -> dict:
    doc = copy.deepcopy(doc)
    header = doc.get("header")
    if isinstance(header, dict) and "creation_date" in header:
        header["creation_date"] = "NORMALIZZATO-PER-IL-CONFRONTO-GOLDEN"
    return doc


@pytest.mark.slow
def test_building_golden_file_matches_reference_for_fixed_seed():
    """Per il seed 1337 (tavern), il documento generato deve combaciare
    esattamente (a meno di creation_date) con
    tests/fixtures/golden/building_tavern_seed_1337.json. Se questo test
    fallisce dopo una modifica intenzionale al generatore, rigenerare il
    golden con lo script in questo stesso file (_generate_full_document) e
    verificare a mano il diff prima di sovrascrivere."""
    golden_path = GOLDEN_DIR / "building_tavern_seed_1337.json"
    actual = _normalize_for_golden(_generate_full_document(seed=1337))

    assert golden_path.exists(), f"Golden file mancante: {golden_path}"
    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    assert actual == expected
