"""Test end-to-end per il comando `ddforge generate` (TASK-24)."""

import json
import subprocess
import sys
from pathlib import Path


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "ddforge.cli", *args],
        capture_output=True,
        text=True,
    )


def test_generate_dungeon_produces_a_valid_file(tmp_path):
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "dungeon",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "80", "--height", "80",
        "--rooms", "8", "--seed", "1337",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert out.exists()
    doc = json.loads(out.read_text(encoding="utf-8"))
    level = doc["world"]["levels"]["0"]
    assert len(level["walls"]) > 0


def test_generate_blocks_write_on_validation_error(tmp_path):
    """La fixture 8x8 (build piu vecchia) non ha texts_vis: validate()
    la segnala sempre come errore DDF003, quindi generate non deve mai
    scrivere il file con quel template."""
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "dungeon",
        "--template", "tests/fixtures/reference_8x8.dungeondraft_map",
        "--out", str(out),
        "--width", "8", "--height", "8",
        "--rooms", "2", "--seed", "1",
    )
    assert result.returncode == 1
    assert not out.exists()
    assert "DDF003" in result.stdout
    assert "ERRORE" in result.stdout


def test_generate_warnings_do_not_block_write(tmp_path):
    """Su una mappa grande con piu stanze, e plausibile incontrare warning
    (es. DDF102 su canali di corridoio a L, limite noto del validatore):
    verifica che comunque il file venga scritto con exit 0."""
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "dungeon",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "80", "--height", "80",
        "--rooms", "10", "--seed", "5",
    )
    assert result.returncode == 0
    assert out.exists()


def test_generate_same_seed_is_reproducible(tmp_path):
    out1 = tmp_path / "out1.dungeondraft_map"
    out2 = tmp_path / "out2.dungeondraft_map"
    for out in (out1, out2):
        result = _run(
            "generate", "dungeon",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "60", "--height", "60",
            "--rooms", "6", "--seed", "42",
        )
        assert result.returncode == 0
    assert out1.read_text(encoding="utf-8") == out2.read_text(encoding="utf-8")


def test_generate_different_seed_changes_output(tmp_path):
    out1 = tmp_path / "out1.dungeondraft_map"
    out2 = tmp_path / "out2.dungeondraft_map"
    for out, seed in ((out1, "1"), (out2, "2")):
        _run(
            "generate", "dungeon",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "60", "--height", "60",
            "--rooms", "6", "--seed", seed,
        )
    assert out1.read_text(encoding="utf-8") != out2.read_text(encoding="utf-8")


def test_generate_cave_produces_a_valid_file_with_no_walls(tmp_path):
    """La grotta scrive il layer cave nativo (TASK-32/decision-1): niente
    stanze/muri, a differenza di dungeon/building."""
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "cave",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "80", "--height", "80",
        "--seed", "1337",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    level = doc["world"]["levels"]["0"]
    template_doc = json.loads(Path("templates/blank_80x80.dungeondraft_map").read_text(encoding="utf-8"))

    assert level["walls"] == []
    assert level["cave"]["bitmap"] != template_doc["world"]["levels"]["0"]["cave"]["bitmap"]


def test_generate_furnish_adds_objects(tmp_path):
    out_none = tmp_path / "none.dungeondraft_map"
    out_heavy = tmp_path / "heavy.dungeondraft_map"
    for out, furnish in ((out_none, "none"), (out_heavy, "heavy")):
        result = _run(
            "generate", "dungeon",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "60", "--height", "60",
            "--rooms", "6", "--seed", "9",
            "--furnish", furnish,
        )
        assert result.returncode == 0

    def n_objects(path):
        doc = json.loads(path.read_text(encoding="utf-8"))
        return len(doc["world"]["levels"]["0"]["objects"])

    assert n_objects(out_heavy) > n_objects(out_none)


def test_generate_lights_flag_adds_lights(tmp_path):
    out_no_lights = tmp_path / "nolights.dungeondraft_map"
    out_lights = tmp_path / "lights.dungeondraft_map"
    _run(
        "generate", "dungeon",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out_no_lights),
        "--width", "60", "--height", "60", "--rooms", "6", "--seed", "3",
    )
    _run(
        "generate", "dungeon",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out_lights),
        "--width", "60", "--height", "60", "--rooms", "6", "--seed", "3",
        "--lights",
    )

    def n_lights(path):
        doc = json.loads(path.read_text(encoding="utf-8"))
        return len(doc["world"]["levels"]["0"]["lights"])

    assert n_lights(out_no_lights) == 0
    assert n_lights(out_lights) > 0


def test_generate_unimplemented_style_gives_clear_error_not_traceback(tmp_path):
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "city",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
    )
    assert result.returncode == 1
    assert not out.exists()
    assert "Traceback" not in result.stderr
    assert "non e ancora implementato" in (result.stdout + result.stderr)


def test_generate_missing_template_gives_clear_error(tmp_path):
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "dungeon",
        "--template", "non_esiste.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
    )
    assert result.returncode == 1
    assert not out.exists()
    assert "Traceback" not in result.stderr


def test_generated_lights_always_have_a_texture(tmp_path):
    """TASK-42: una luce priva di `texture` manda Dungeondraft in loop
    infinito al caricamento. Il bug era arrivato fino ai file dei gate umani
    perche' nessun test guardava dentro le luci prodotte dalla CLI."""
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "dungeon",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "60", "--height", "60", "--rooms", "6", "--seed", "3",
        "--lights",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    lights = json.loads(out.read_text(encoding="utf-8"))["world"]["levels"]["0"]["lights"]
    assert lights, "il file di prova deve contenere almeno una luce"
    for light in lights:
        assert light["texture"] == "res://textures/lights/soft.png"
        assert "rotation" in light
