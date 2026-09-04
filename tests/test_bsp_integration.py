"""Test di integrazione e golden file per il generatore BSP (TASK-25).

Piramide di test di SPEC.md §10: integrazione (carica fixture, genera,
valida) e golden file (confronto byte-per-byte con un riferimento, per
intercettare regressioni silenziose nel formato).
"""

import copy
import json
import random
from collections import deque
from pathlib import Path

import pytest

from ddforge.assets import load_catalog, palette_for
from ddforge.compose import furnish, render_blueprint
from ddforge.generators import bsp
from ddforge.ids import IdAllocator
from ddforge.template import finalize, prepare
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


def _patched_8x8_doc(reference_8x8_doc):
    """reference_8x8.dungeondraft_map (TASK-5) e di una build piu vecchia
    senza texts_vis: userebbe SEMPRE DDF003, indipendentemente dal
    generatore. Stessa correzione minima usata in TASK-15."""
    doc = copy.deepcopy(reference_8x8_doc)
    doc["world"]["levels"]["0"]["texts_vis"] = True
    return doc


def test_bsp_integration_on_8x8_fixture_has_zero_errors(reference_8x8_doc):
    doc = _patched_8x8_doc(reference_8x8_doc)
    blueprint = bsp.generate(width=8, height=8, seed=1, rooms=3, min_room=2, max_room=3)

    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("dungeon", catalog)
    render_blueprint(level, ids, blueprint, palette)
    finalize(prepared, ids)

    errors = [i for i in validate(prepared) if i.severity == "error"]
    assert errors == []


def test_bsp_integration_rooms_all_reachable_and_no_overlap(reference_8x8_doc):
    doc = _patched_8x8_doc(reference_8x8_doc)
    blueprint = bsp.generate(width=8, height=8, seed=1, rooms=3, min_room=2, max_room=3)

    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("dungeon", catalog)
    render_blueprint(level, ids, blueprint, palette)
    finalize(prepared, ids)

    reachable = _bfs_reachable(blueprint.graph, start=0)
    assert reachable == set(range(len(blueprint.rooms)))

    for i, a in enumerate(blueprint.rooms):
        for b in blueprint.rooms[i + 1 :]:
            assert not a.rect.overlaps(b.rect)


def _generate_full_document(seed: int) -> dict:
    from ddforge.template import load_template

    doc = load_template("templates/blank_80x80.dungeondraft_map")
    blueprint = bsp.generate(width=80, height=80, seed=seed, rooms=8)

    prepared = prepare(doc, levels=1)
    level = prepared["world"]["levels"]["0"]
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("dungeon", catalog)

    render_blueprint(level, ids, blueprint, palette)
    furnish(level, ids, blueprint, palette, density="light", rng=random.Random(seed))
    finalize(prepared, ids)
    return prepared


def _normalize_for_golden(doc: dict) -> dict:
    doc = copy.deepcopy(doc)
    header = doc.get("header")
    if isinstance(header, dict) and "creation_date" in header:
        header["creation_date"] = "NORMALIZZATO-PER-IL-CONFRONTO-GOLDEN"
    return doc


@pytest.mark.slow
def test_bsp_golden_file_matches_reference_for_fixed_seed():
    """Per il seed 1337, il documento generato deve combaciare esattamente
    (a meno di creation_date) con tests/fixtures/golden/bsp_seed_1337.json.
    Se questo test fallisce dopo una modifica intenzionale al generatore o
    al formato, rigenerare il golden con lo script in questo stesso file
    (vedi _generate_full_document) e verificare a mano il diff prima di
    sovrascrivere."""
    golden_path = GOLDEN_DIR / "bsp_seed_1337.json"
    actual = _normalize_for_golden(_generate_full_document(seed=1337))

    assert golden_path.exists(), f"Golden file mancante: {golden_path}"
    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    assert actual == expected
