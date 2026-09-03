"""Test per ddforge.ids.IdAllocator."""

import json

from ddforge.ids import IdAllocator


def test_next_produces_10000_distinct_ids():
    ids = IdAllocator()
    produced = {ids.next() for _ in range(10_000)}
    assert len(produced) == 10_000


def test_next_free_always_greater_than_last_emitted():
    ids = IdAllocator()
    for _ in range(1000):
        last = int(ids.next(), 16)
        assert int(ids.next_free, 16) > last


def test_default_start_is_0x1000():
    ids = IdAllocator()
    assert ids.next() == format(0x1001, "x")


def test_custom_start():
    ids = IdAllocator(start=0)
    assert ids.next() == "1"


def test_from_document_finds_max_id_nested_in_wall_portals():
    doc = {
        "world": {
            "levels": {
                "0": {
                    "walls": [
                        {
                            "node_id": "10",
                            "portals": [{"node_id": "ff"}],
                        }
                    ],
                    "objects": [{"node_id": "5"}],
                }
            }
        }
    }
    ids = IdAllocator.from_document(doc)
    assert ids.n == 0xFF
    assert int(ids.next(), 16) > 0xFF


def test_from_document_on_real_rich_reference():
    with open("templates/rich_reference.dungeondraft_map", encoding="utf-8") as f:
        doc = json.load(f)
    ids = IdAllocator.from_document(doc)

    declared_next = int(doc["world"]["next_node_id"], 16)
    assert ids.n < declared_next
    # next_free deve comunque superare ogni id realmente usato nel documento
    assert int(ids.next_free, 16) > ids.n


def test_from_document_ignores_non_hex_values():
    doc = {"world": {"levels": {"0": {"objects": [{"node_id": "not-hex"}]}}}}
    ids = IdAllocator.from_document(doc)
    assert ids.n == 0
