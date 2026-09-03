"""Verifica lo script demo di M1 (TASK-11): criterio di completamento di M1."""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from demo_m1 import TEMPLATE, build_demo  # noqa: E402


def _all_node_ids(value):
    if isinstance(value, dict):
        for key, v in value.items():
            if key == "node_id":
                yield v
            else:
                yield from _all_node_ids(v)
    elif isinstance(value, list):
        for item in value:
            yield from _all_node_ids(item)


def test_demo_produces_one_room_with_floor_walls_and_door():
    doc = build_demo()
    level = doc["world"]["levels"]["0"]

    assert len(level["patterns"]) == 1
    assert len(level["walls"]) == 4
    nested_portals = sum(len(w["portals"]) for w in level["walls"])
    assert nested_portals == 1
    assert level["portals"] == []  # mai a livello mappa


def test_demo_node_ids_unique_and_next_node_id_coherent():
    doc = build_demo()
    ids = list(_all_node_ids(doc))
    assert len(ids) == len(set(ids))

    max_id = max(int(i, 16) for i in ids)
    next_id = int(doc["world"]["next_node_id"], 16)
    assert next_id > max_id


def test_demo_does_not_modify_source_template():
    before = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
    build_demo()
    after = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()
    assert before == after


def test_demo_output_is_valid_json_after_save(tmp_path):
    from ddforge.template import save

    doc = build_demo()
    out = tmp_path / "demo.dungeondraft_map"
    save(doc, out)

    reloaded = json.loads(out.read_text(encoding="utf-8"))
    assert reloaded == doc
