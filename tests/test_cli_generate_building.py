"""Test end-to-end per `ddforge generate building` (TASK-30)."""

import json
import subprocess
import sys


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "ddforge.cli", *args],
        capture_output=True,
        text=True,
    )


def test_generate_building_produces_a_multi_level_valid_file(tmp_path):
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "building",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
        "--seed", "1337", "--building-type", "tavern",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert out.exists()

    doc = json.loads(out.read_text(encoding="utf-8"))
    levels = doc["world"]["levels"]
    assert len(levels) == 2  # tavern: piano terra + camere
    assert len(levels["0"]["walls"]) > 0
    assert len(levels["1"]["walls"]) > 0


def test_generate_building_manor_has_three_levels_and_a_roof_on_the_top_one():
    result_out = None
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out = f"{tmp}/manor.dungeondraft_map"
        result = _run(
            "generate", "building",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", out,
            "--width", "40", "--height", "40",
            "--seed", "1", "--building-type", "manor",
        )
        assert result.returncode == 0, result.stdout + result.stderr
        with open(out, encoding="utf-8") as f:
            doc = json.load(f)
        result_out = doc

    levels = result_out["world"]["levels"]
    assert len(levels) == 3
    assert levels["0"]["roofs"]["roofs"] == []
    assert levels["1"]["roofs"]["roofs"] == []
    assert len(levels["2"]["roofs"]["roofs"]) == 1


def test_generate_building_l_shaped_flag_is_accepted(tmp_path):
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "building",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
        "--seed", "1", "--building-type", "warehouse", "--l-shaped",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert out.exists()


def test_generate_building_furnish_adds_objects_on_the_right_floors(tmp_path):
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "building",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
        "--seed", "1", "--building-type", "tavern", "--furnish", "heavy",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    levels = doc["world"]["levels"]
    assert len(levels["0"]["objects"]) > 0
    assert len(levels["1"]["objects"]) > 0


def test_generate_building_lights_flag_adds_lights_on_every_floor(tmp_path):
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "building",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
        "--seed", "1", "--building-type", "tavern", "--lights",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    levels = doc["world"]["levels"]
    assert len(levels["0"]["lights"]) > 0
    assert len(levels["1"]["lights"]) > 0


def test_generate_building_same_seed_is_reproducible(tmp_path):
    out1 = tmp_path / "out1.dungeondraft_map"
    out2 = tmp_path / "out2.dungeondraft_map"
    for out in (out1, out2):
        result = _run(
            "generate", "building",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "40", "--height", "40",
            "--seed", "7", "--building-type", "manor", "--furnish", "medium", "--lights",
        )
        assert result.returncode == 0
    assert out1.read_text(encoding="utf-8") == out2.read_text(encoding="utf-8")


def test_generate_building_default_style_uses_the_building_type_palette(tmp_path):
    """Senza --style, la palette usata deve essere quella del building-type
    (SPEC.md §8: style di default = algoritmo), non un fallback 'building'
    inesistente in _STYLE_DEFINITIONS."""
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "building",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
        "--seed", "1", "--building-type", "warehouse", "--furnish", "heavy",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    textures = {o["texture"] for o in doc["world"]["levels"]["0"]["objects"]}
    assert any("crate" in t.lower() or "barrel" in t.lower() for t in textures)


def test_generated_building_lights_always_have_a_texture(tmp_path):
    """TASK-42, su tutti i piani: e' il difetto che bloccava building_m4."""
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "building",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
        "--seed", "1337", "--building-type", "manor", "--lights",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    levels = json.loads(out.read_text(encoding="utf-8"))["world"]["levels"]
    seen = 0
    for level in levels.values():
        for light in level["lights"]:
            assert light["texture"] == "res://textures/lights/soft.png"
            seen += 1
    assert seen > 0
