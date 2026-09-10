"""Test per ddforge.assets: build_catalog, load_catalog, CLI catalog."""

import json
import struct
import subprocess
import sys

import pytest

from ddforge.assets import (
    _STYLE_DEFINITIONS,
    build_catalog,
    load_catalog,
    palette_for,
    read_dungeondraft_pack,
    required_packs,
)


def _fake_png(width: int, height: int) -> bytes:
    """PNG minimo: solo signature+IHDR, quanto basta per read_dungeondraft_pack
    (legge solo i primi 24 byte, non un PNG davvero decodificabile)."""
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"\x00" * 5


def _build_pck(files: dict) -> bytes:
    """.dungeondraft_pack minimo (Godot PCK 'GDPC', pack_version 1) per i
    test, stesso formato verificato sul file reale in read_dungeondraft_pack:
    magic + pack_version(int32) + 3x int32 versione Godot + 64 byte
    riservati, poi file_count(int32) e per ogni entry
    path_len(uint32)+path+offset(uint64)+size(uint64)+md5(16 byte,
    ignorato dal reader), tutto little-endian, dati in coda."""
    header = b"GDPC" + struct.pack("<4i", 1, 3, 2, 1) + b"\x00" * 64
    entries = list(files.items())
    directory_len = 4 + sum(4 + len(p.encode("utf-8")) + 8 + 8 + 16 for p, _ in entries)
    directory = struct.pack("<i", len(entries))
    data = b""
    offset = len(header) + directory_len
    for path, blob in entries:
        path_b = path.encode("utf-8")
        directory += struct.pack("<I", len(path_b)) + path_b
        directory += struct.pack("<QQ", offset, len(blob))
        directory += b"\x00" * 16
        data += blob
        offset += len(blob)
    return header + directory + data


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


# ---------------------------------------------------------------------------
# palette_for / required_packs (TASK-17)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real_catalog():
    return load_catalog("data/assets.json")


@pytest.mark.parametrize("style", sorted(_STYLE_DEFINITIONS))
def test_palette_for_produces_valid_palette_for_every_style(style, real_catalog):
    palette = palette_for(style, real_catalog)
    assert palette.wall.startswith("res://")
    assert palette.floor.startswith("res://")
    assert palette.door.startswith("res://")
    assert all(v.startswith("res://") for v in palette.accents.values())
    assert all(v.startswith("res://") for v in palette.floors.values())


def test_palette_for_unknown_style_raises_explicit_error(real_catalog):
    with pytest.raises(ValueError, match="Stile sconosciuto"):
        palette_for("stile_a_caso", real_catalog)


def test_palette_for_missing_catalog_key_raises_explicit_error():
    catalog = {"walls": {}, "floors": {}, "portals": {}, "objects": {}}
    with pytest.raises(ValueError, match="stone"):
        palette_for("dungeon", catalog)


@pytest.mark.parametrize("style", sorted(_STYLE_DEFINITIONS))
def test_palette_textures_only_reference_packs_in_manifest(style, real_catalog):
    known_pack_ids = {p["id"] for p in real_catalog["packs"]}
    palette = palette_for(style, real_catalog)
    textures = [
        palette.wall, palette.floor, palette.door,
        *palette.accents.values(), *palette.floors.values(),
    ]
    for texture in textures:
        if texture.startswith("res://packs/"):
            pack_id = texture.split("/")[3]
            assert pack_id in known_pack_ids


# ---------------------------------------------------------------------------
# palette.floors: pavimento kind-specifico (TASK-43)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("style", "kind"),
    [
        ("dungeon", "boss"),
        ("tavern", "cucina"),
        ("tavern", "retro"),
        ("tavern", "camera"),
        ("manor", "privato"),
        ("manor", "servitu"),
        ("warehouse", "soppalco"),
    ],
)
def test_palette_for_maps_specific_kinds_to_a_floor_different_from_the_default(style, kind, real_catalog):
    palette = palette_for(style, real_catalog)
    assert kind in palette.floors
    assert palette.floors[kind] != palette.floor


def test_palette_for_leaves_unmapped_kinds_out_of_floors():
    """Un kind non elencato in _STYLE_DEFINITIONS["floors"] non deve comparire
    in palette.floors: e cosi che compose._room_floor ricade sul floor
    uniforme per lui (fallback invariato, AC5)."""
    catalog = load_catalog("data/assets.json")
    palette = palette_for("dungeon", catalog)
    assert "sala" not in palette.floors
    assert "corridoio" not in palette.floors
    assert "vano_scale" not in palette.floors


def test_required_packs_extracts_ids_from_document():
    doc = {
        "header": {},
        "world": {
            "levels": {
                "0": {
                    "walls": [{"texture": "res://packs/AAA111/textures/walls/x.png", "portals": []}],
                    "objects": [{"texture": "res://textures/objects/default.png"}],
                }
            }
        },
    }
    assert required_packs(doc) == {"AAA111"}


def test_required_packs_on_real_rich_reference_matches_manifest_subset():
    with open("templates/rich_reference.dungeondraft_map", encoding="utf-8") as f:
        doc = json.load(f)
    manifest_ids = {m["id"] for m in doc["header"]["asset_manifest"]}
    used = required_packs(doc)
    assert used.issubset(manifest_ids)


# ---------------------------------------------------------------------------
# read_dungeondraft_pack / build_catalog(pack_sources=...) (TASK-46)
# ---------------------------------------------------------------------------


def test_read_dungeondraft_pack_reads_manifest_and_png_sizes(tmp_path):
    manifest = json.dumps({"name": "Test Pack", "id": "ZZZTest1", "author": "T", "version": "1"}).encode("utf-8")
    pack_bytes = _build_pck({
        "res://packs/ZZZTest1.json": manifest,
        "res://packs/ZZZTest1/textures/objects/thing.png": _fake_png(64, 32),
        # Non .png: ignorato, nessuna dimensione nota per lui.
        "res://packs/ZZZTest1/textures/objects/other.webp": b"not-a-png",
    })
    path = tmp_path / "test.dungeondraft_pack"
    path.write_bytes(pack_bytes)

    result = read_dungeondraft_pack(path)

    assert result["manifest"]["id"] == "ZZZTest1"
    assert result["textures"] == {"res://packs/ZZZTest1/textures/objects/thing.png": (64, 32)}


def test_read_dungeondraft_pack_rejects_bad_magic(tmp_path):
    path = tmp_path / "bad.dungeondraft_pack"
    path.write_bytes(b"NOTG" + b"\x00" * 100)
    with pytest.raises(ValueError, match="GDPC"):
        read_dungeondraft_pack(path)


def test_build_catalog_with_pack_source_adds_textures_and_pixel_sizes():
    doc = _doc(packs=["ZZZTest1"])
    pack_source = {
        "manifest": {"id": "ZZZTest1"},
        "textures": {"res://packs/ZZZTest1/textures/objects/thing.png": (64, 32)},
    }
    catalog = build_catalog(doc, pack_sources=[pack_source])

    assert catalog["objects"]["thing"] == "res://packs/ZZZTest1/textures/objects/thing.png"
    assert catalog["object_sizes"]["thing"] == [64, 32]


def test_build_catalog_rejects_pack_source_absent_from_manifest():
    """Stesso vincolo non negoziabile di AC1: mai una texture di un pack
    assente da header.asset_manifest, nemmeno quando arriva da --pack."""
    doc = _doc(packs=["OTHER"])
    pack_source = {
        "manifest": {"id": "ORPHAN"},
        "textures": {"res://packs/ORPHAN/textures/objects/thing.png": (10, 10)},
    }
    with pytest.raises(ValueError, match="ORPHAN"):
        build_catalog(doc, pack_sources=[pack_source])


def test_cli_catalog_accepts_pack_flag_and_writes_object_sizes(tmp_path):
    doc = _doc(packs=["ZZZTest1"])
    src = tmp_path / "source.dungeondraft_map"
    src.write_text(json.dumps(doc), encoding="utf-8")

    manifest = json.dumps({"name": "Test Pack", "id": "ZZZTest1", "author": "T", "version": "1"}).encode("utf-8")
    pack_path = tmp_path / "test.dungeondraft_pack"
    pack_path.write_bytes(_build_pck({
        "res://packs/ZZZTest1.json": manifest,
        "res://packs/ZZZTest1/textures/objects/thing.png": _fake_png(64, 32),
    }))

    out = tmp_path / "out.json"
    result = subprocess.run(
        [
            sys.executable, "-m", "ddforge.cli", "catalog",
            "--from", str(src), "--pack", str(pack_path), "--out", str(out),
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["objects"]["thing"] == "res://packs/ZZZTest1/textures/objects/thing.png"
    assert written["object_sizes"]["thing"] == [64, 32]


# ---------------------------------------------------------------------------
# Palette.building_variants / building_colors (TASK-46)
# ---------------------------------------------------------------------------


def test_palette_for_city_populates_building_variants_and_colors(real_catalog):
    palette = palette_for("city", real_catalog)

    assert len(palette.building_variants) == 33
    for texture, width_px, height_px in palette.building_variants:
        assert texture.startswith("res://packs/6VxwaRdj/textures/objects/")
        assert width_px > 0
        assert height_px > 0

    assert len(palette.building_colors) > 0
    for color in palette.building_colors:
        assert len(color) == 8
        int(color, 16)  # ARGB esadecimale valido


@pytest.mark.parametrize("style", sorted(s for s in _STYLE_DEFINITIONS if s != "city"))
def test_palette_for_non_city_styles_have_no_building_variants(style, real_catalog):
    palette = palette_for(style, real_catalog)
    assert palette.building_variants == []
    assert palette.building_colors == ()


def test_palette_for_city_building_variants_only_reference_the_manifest_pack(real_catalog):
    known_pack_ids = {p["id"] for p in real_catalog["packs"]}
    palette = palette_for("city", real_catalog)
    for texture, _w, _h in palette.building_variants:
        assert texture.startswith("res://packs/")
        pack_id = texture.split("/")[3]
        assert pack_id in known_pack_ids
