"""Test per ddforge.assets: build_catalog, load_catalog, CLI catalog."""

import json
import subprocess
import sys

import pytest

from ddforge.assets import build_catalog, load_catalog


def _doc(*, packs=(), walls=(), portals=(), patterns=(), objects=(), roofs=()):
    return {
        "header": {
            "asset_manifest": [
                {"id": pid, "name": f"Pack {pid}", "author": "Autore", "version": "1"}
                for pid in packs
            ]
        },
        "world": {
            "levels": {
                "0": {
                    "walls": [
                        {"texture": t, "portals": []} for t in walls
                    ],
                    "portals": [{"texture": t} for t in portals],
                    "patterns": [{"texture": t} for t in patterns],
                    "objects": [{"texture": t} for t in objects],
                    "paths": [],
                    "roofs": {"roofs": [{"texture": t} for t in roofs]},
                }
            }
        },
    }


def test_build_catalog_classifies_by_path_segment():
    doc = _doc(
        packs=["ABC123"],
        walls=["res://textures/walls/stone.png"],
        portals=["res://textures/portals/door_wood_single.png"],
        patterns=["res://textures/patterns/normal/cobblestone.png"],
        objects=["res://textures/objects/containers/barrel_01.png"],
        roofs=["res://textures/roofs/flat_clay_red/tiles.png"],
    )
    catalog = build_catalog(doc)

    assert catalog["walls"] == {"stone": "res://textures/walls/stone.png"}
    assert catalog["portals"] == {
        "door_wood_single": "res://textures/portals/door_wood_single.png"
    }
    assert catalog["floors"] == {
        "cobblestone": "res://textures/patterns/normal/cobblestone.png"
    }
    assert catalog["roofs"] == {"tiles": "res://textures/roofs/flat_clay_red/tiles.png"}
    assert catalog["paths"] == {}


def test_build_catalog_adds_semantic_alias_for_known_objects():
    doc = _doc(objects=["res://textures/objects/containers/barrel_01.png"])
    catalog = build_catalog(doc)

    assert catalog["objects"]["barrel_01"] == "res://textures/objects/containers/barrel_01.png"
    assert catalog["objects"]["barrel"] == "res://textures/objects/containers/barrel_01.png"


def test_build_catalog_does_not_invent_unobserved_aliases():
    doc = _doc(objects=["res://textures/objects/containers/barrel_01.png"])
    catalog = build_catalog(doc)

    assert "torch" not in catalog["objects"]
    assert "altar" not in catalog["objects"]


def test_build_catalog_merges_multiple_documents():
    doc_a = _doc(packs=["AAA"], walls=["res://textures/walls/stone.png"])
    doc_b = _doc(packs=["BBB"], walls=["res://textures/walls/concrete.png"])
    catalog = build_catalog(doc_a, doc_b)

    pack_ids = {p["id"] for p in catalog["packs"]}
    assert pack_ids == {"AAA", "BBB"}
    assert set(catalog["walls"]) == {"stone", "concrete"}


def test_build_catalog_never_references_pack_absent_from_manifest():
    """Ogni texture res://packs/<ID>/... nel catalogo deve avere <ID> in un pack noto."""
    doc = _doc(
        packs=["FA30DDXY"],
        objects=["res://packs/FA30DDXY/textures/objects/keg.webp"],
    )
    catalog = build_catalog(doc)

    known_ids = {p["id"] for p in catalog["packs"]}
    for bucket_name in ("walls", "floors", "portals", "roofs", "paths", "objects"):
        for texture in catalog[bucket_name].values():
            if texture.startswith("res://packs/"):
                pack_id = texture.split("/")[3]
                assert pack_id in known_ids


def test_load_catalog_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_catalog(tmp_path / "non_esiste.json")


def test_load_catalog_reads_written_file(tmp_path):
    catalog = {"packs": [], "walls": {}, "floors": {}, "portals": {}, "roofs": {}, "paths": {}, "objects": {}}
    p = tmp_path / "assets.json"
    p.write_text(json.dumps(catalog), encoding="utf-8")

    assert load_catalog(p) == catalog


def test_cli_catalog_is_deterministic(tmp_path):
    doc = _doc(
        packs=["ZZZ"],
        walls=["res://textures/walls/stone.png"],
        objects=["res://textures/objects/containers/barrel_01.png"],
    )
    src = tmp_path / "source.dungeondraft_map"
    src.write_text(json.dumps(doc), encoding="utf-8")

    out1 = tmp_path / "out1.json"
    out2 = tmp_path / "out2.json"
    for out in (out1, out2):
        subprocess.run(
            [sys.executable, "-m", "ddforge.cli", "catalog", "--from", str(src), "--out", str(out)],
            check=True,
            capture_output=True,
            text=True,
        )

    assert out1.read_text(encoding="utf-8") == out2.read_text(encoding="utf-8")


def test_cli_catalog_merges_repeated_from(tmp_path):
    doc_a = _doc(packs=["AAA"], walls=["res://textures/walls/stone.png"])
    doc_b = _doc(packs=["BBB"], walls=["res://textures/walls/concrete.png"])
    src_a = tmp_path / "a.dungeondraft_map"
    src_b = tmp_path / "b.dungeondraft_map"
    src_a.write_text(json.dumps(doc_a), encoding="utf-8")
    src_b.write_text(json.dumps(doc_b), encoding="utf-8")
    out = tmp_path / "out.json"

    subprocess.run(
        [
            sys.executable, "-m", "ddforge.cli", "catalog",
            "--from", str(src_a), "--from", str(src_b), "--out", str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    written = json.loads(out.read_text(encoding="utf-8"))
    assert set(written["walls"]) == {"stone", "concrete"}
