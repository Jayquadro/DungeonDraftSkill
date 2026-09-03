"""Test per ddforge.template: load_template, blank_level, prepare, finalize, save."""

import hashlib
import json

import pytest

from ddforge.ids import IdAllocator
from ddforge.template import (
    DRAWABLE_LISTS,
    LEVEL_KEYS,
    TemplateError,
    blank_level,
    finalize,
    load_template,
    prepare,
    save,
)


def test_load_template_reads_reference_8x8(reference_8x8_path):
    doc = load_template(reference_8x8_path)
    assert doc["world"]["format"] == 3
    assert "0" in doc["world"]["levels"]


def test_load_template_missing_file_raises(tmp_path):
    with pytest.raises(TemplateError):
        load_template(tmp_path / "non_esiste.dungeondraft_map")


def test_load_template_invalid_json_raises(tmp_path):
    p = tmp_path / "broken.dungeondraft_map"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(TemplateError):
        load_template(p)


@pytest.mark.parametrize(
    "broken_doc",
    [
        {},
        {"header": {}},
        {"header": {}, "world": "not-a-dict"},
        {"header": {}, "world": {"format": "3", "levels": {"0": {}}}},
        {"header": {}, "world": {"format": 3, "levels": {}}},
    ],
)
def test_load_template_rejects_malformed_documents(tmp_path, broken_doc):
    p = tmp_path / "broken.dungeondraft_map"
    p.write_text(json.dumps(broken_doc), encoding="utf-8")
    with pytest.raises(TemplateError):
        load_template(p)


def test_blank_level_clears_only_drawable_lists_and_metadata(reference_8x8_doc):
    level = reference_8x8_doc["world"]["levels"]["0"]
    blanked = blank_level(level)

    # blank_level non deve mai perdere chiavi: preserva esattamente quelle
    # del livello sorgente. La fixture 8x8 e di una build che non ha
    # texts_vis (assente da SPEC.md §13, aggiunta in build successive alla
    # 1.0.4.x -- vedi docs/format.md §12), quindi qui non verifichiamo
    # LEVEL_KEYS come sovrainsieme fisso, solo che nulla vada perso.
    assert set(blanked.keys()) == set(level.keys())
    for key in DRAWABLE_LISTS:
        assert blanked[key] == []

    for key in ("tiles", "terrain", "cave", "water", "environment", "layers"):
        assert blanked[key] == level[key]


def test_blank_level_covers_level_keys_on_current_build_template():
    """Sulla build 1.2.0.1 reale (blank_80x80), LEVEL_KEYS include texts_vis."""
    doc = load_template("templates/blank_80x80.dungeondraft_map")
    level = doc["world"]["levels"]["0"]
    blanked = blank_level(level)
    assert set(LEVEL_KEYS).issubset(blanked.keys())


def test_blank_level_preserves_terrain_splat_length(reference_8x8_doc):
    level = reference_8x8_doc["world"]["levels"]["0"]
    blanked = blank_level(level)
    assert len(blanked["terrain"]["splat"]) == len(level["terrain"]["splat"])


def test_blank_level_roofs_keeps_only_roofs_list_emptied(reference_8x8_doc):
    level = reference_8x8_doc["world"]["levels"]["0"]
    level = dict(level)
    level["roofs"] = {"shade": True, "shade_contrast": 0.5, "sun_direction": 45, "roofs": [{"node_id": "x"}]}
    blanked = blank_level(level)

    assert blanked["roofs"]["roofs"] == []
    assert blanked["roofs"]["shade"] is True
    assert blanked["roofs"]["shade_contrast"] == 0.5
    assert blanked["roofs"]["sun_direction"] == 45


def test_blank_level_does_not_mutate_original(reference_8x8_doc):
    level = reference_8x8_doc["world"]["levels"]["0"]
    original_walls = json.dumps(level["walls"])
    blank_level(level)
    assert json.dumps(level["walls"]) == original_walls


def test_prepare_duplicates_first_level_when_more_requested(reference_8x8_doc):
    prepared = prepare(reference_8x8_doc, levels=3)
    levels = prepared["world"]["levels"]
    assert set(levels.keys()) == {"0", "1", "2"}
    original_keys = set(reference_8x8_doc["world"]["levels"]["0"].keys())
    for lvl in levels.values():
        assert lvl["walls"] == []
        assert set(lvl.keys()) == original_keys


def test_prepare_uses_labels(reference_8x8_doc):
    prepared = prepare(reference_8x8_doc, levels=2, labels=["Piano Terra", "Primo Piano"])
    assert prepared["world"]["levels"]["0"]["label"] == "Piano Terra"
    assert prepared["world"]["levels"]["1"]["label"] == "Primo Piano"


def test_prepare_does_not_mutate_original_document(reference_8x8_doc):
    original = json.dumps(reference_8x8_doc, sort_keys=True)
    prepare(reference_8x8_doc, levels=2)
    assert json.dumps(reference_8x8_doc, sort_keys=True) == original


def test_finalize_writes_next_node_id_from_allocator(reference_8x8_doc):
    ids = IdAllocator.from_document(reference_8x8_doc)
    ids.next()
    ids.next()
    finalize(reference_8x8_doc, ids)
    assert reference_8x8_doc["world"]["next_node_id"] == ids.next_free
    assert int(reference_8x8_doc["world"]["next_node_id"], 16) > ids.n


def test_save_writes_indented_utf8_json(tmp_path):
    doc = {"header": {"x": "città"}, "world": {"format": 3, "levels": {"0": {}}}}
    out = tmp_path / "out.dungeondraft_map"
    save(doc, out)

    text = out.read_text(encoding="utf-8")
    assert "città" in text  # ensure_ascii=False
    assert "\n  " in text  # indent=2
    assert json.loads(text) == doc


def test_save_never_modifies_the_source_template(reference_8x8_path, tmp_path):
    before_hash = hashlib.sha256(reference_8x8_path.read_bytes()).hexdigest()

    doc = load_template(reference_8x8_path)
    ids = IdAllocator.from_document(doc)
    prepared = prepare(doc, levels=1)
    finalize(prepared, ids)
    save(prepared, tmp_path / "out.dungeondraft_map")

    after_hash = hashlib.sha256(reference_8x8_path.read_bytes()).hexdigest()
    assert before_hash == after_hash
