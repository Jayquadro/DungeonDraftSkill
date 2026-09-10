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


def test_generate_sewer_produces_a_valid_file_with_sewer_palette(tmp_path):
    """La variante fognature disegna muri/pavimenti/porte veri con la
    palette sewer (TASK-33/AC3), a differenza della grotta nativa."""
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "sewer",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
        "--seed", "1337",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    level = doc["world"]["levels"]["0"]

    assert len(level["walls"]) > 0
    assert all(w["texture"] == "res://textures/walls/concrete.png" for w in level["walls"])
    assert all(p["texture"] == "res://textures/patterns/normal/cobblestone.png" for p in level["patterns"])
    doors = [portal for wall in level["walls"] for portal in wall.get("portals", [])]
    assert len(doors) == 1
    assert doors[0]["texture"] == "res://textures/portals/portcullis.png"

    water_children = level["water"]["tree"]["children"]
    assert len(water_children) == len(level["patterns"])


def test_generate_sewer_same_seed_is_reproducible(tmp_path):
    out1 = tmp_path / "out1.dungeondraft_map"
    out2 = tmp_path / "out2.dungeondraft_map"
    for out in (out1, out2):
        result = _run(
            "generate", "sewer",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "40", "--height", "40",
            "--seed", "42",
        )
        assert result.returncode == 0
    assert out1.read_text(encoding="utf-8") == out2.read_text(encoding="utf-8")


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


def test_generate_city_produces_a_valid_file(tmp_path):
    """TASK-35: 'city' e' l'ultimo stile delle choices del parser a essere
    cablato in _load_generators (dungeon/building/cave/sewer lo erano
    gia'). Sostituisce il vecchio test che verificava l'errore esplicito
    'non ancora implementato' per questo stesso stile."""
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", "city",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "70", "--height", "70",
        "--seed", "1337",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    level = doc["world"]["levels"]["0"]
    assert len(level["paths"]) > 0
    assert len(level["roofs"]["roofs"]) > 0


def test_generate_city_same_seed_is_reproducible(tmp_path):
    out1 = tmp_path / "out1.dungeondraft_map"
    out2 = tmp_path / "out2.dungeondraft_map"
    for out in (out1, out2):
        result = _run(
            "generate", "city",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "70", "--height", "70",
            "--seed", "42",
        )
        assert result.returncode == 0
    assert out1.read_text(encoding="utf-8") == out2.read_text(encoding="utf-8")


def test_generate_city_scale_quartiere_produces_a_valid_file(tmp_path):
    """TASK-41 AC1/AC3/AC7: --scale quartiere produce un file valido, con
    molti piu edifici del preset isolato sullo stesso canvas e senza muri (a
    1 quadretto = 1 edificio non c'e geometria di stanze)."""
    out_isolato = tmp_path / "isolato.dungeondraft_map"
    out_quartiere = tmp_path / "quartiere.dungeondraft_map"

    for out, scale in ((out_isolato, "isolato"), (out_quartiere, "quartiere")):
        result = _run(
            "generate", "city",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "78", "--height", "78",
            "--seed", "1337", "--scale", scale,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    isolato = json.loads(out_isolato.read_text(encoding="utf-8"))["world"]["levels"]["0"]
    quartiere = json.loads(out_quartiere.read_text(encoding="utf-8"))["world"]["levels"]["0"]

    # TASK-46: quartiere/citta piazzano un object sprite per edificio invece
    # di un tetto astratto, quindi il confronto di densita' passa da
    # roofs["roofs"] a objects.
    assert len(quartiere["objects"]) > 5 * len(isolato["roofs"]["roofs"])
    assert len(quartiere["paths"]) > len(isolato["paths"])
    assert quartiere["walls"] == []
    assert isolato["walls"] != []


def test_generate_city_scale_citta_has_an_order_of_magnitude_more_buildings(tmp_path):
    """AC4: la citta e' capace di contenere una decina di quartieri, cioe'
    un ordine di grandezza in piu' di edifici del preset quartiere sullo
    stesso canvas (vedi la stessa garanzia gia' verificata su city.generate()
    in tests/test_generators_city.py, qui end-to-end via CLI)."""
    out_quartiere = tmp_path / "quartiere.dungeondraft_map"
    out_citta = tmp_path / "citta.dungeondraft_map"

    for out, scale in ((out_quartiere, "quartiere"), (out_citta, "citta")):
        result = _run(
            "generate", "city",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "78", "--height", "78",
            "--seed", "1337", "--scale", scale,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    quartiere = json.loads(out_quartiere.read_text(encoding="utf-8"))["world"]["levels"]["0"]
    citta = json.loads(out_citta.read_text(encoding="utf-8"))["world"]["levels"]["0"]

    # TASK-46: un object sprite per edificio invece di un tetto astratto.
    ratio = len(citta["objects"]) / len(quartiere["objects"])
    assert 5.0 < ratio < 20.0, ratio
    assert citta["walls"] == []


def test_generate_city_scale_defaults_to_isolato(tmp_path):
    """AC2: senza --scale il risultato deve essere identico a --scale
    isolato, cioe' all'output di TASK-35 gia' esistente (rinominato da
    "quartiere" a "isolato" al round 2 del gate)."""
    outs = []
    for name, args in (("implicito", []), ("esplicito", ["--scale", "isolato"])):
        out = tmp_path / f"{name}.dungeondraft_map"
        result = _run(
            "generate", "city",
            "--template", "templates/blank_80x80.dungeondraft_map",
            "--out", str(out),
            "--width", "70", "--height", "70",
            "--seed", "1337", *args,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        doc = json.loads(out.read_text(encoding="utf-8"))
        doc["header"].pop("creation_date", None)
        outs.append(doc)
    assert outs[0] == outs[1]


def test_all_declared_algorithms_are_wired_to_a_generator():
    """Nessuno stile fantasma nelle choices del parser (build_parser)
    che poi fallisce silenziosamente in _cmd_generate: regressione diretta
    del vecchio test 'city non e' ancora implementato', ora superato."""
    import argparse

    from ddforge.cli import _load_generators, build_parser

    parser = build_parser()
    subparsers_action = next(
        a for a in parser._actions if isinstance(a, argparse._SubParsersAction)
    )
    generate_parser = subparsers_action.choices["generate"]
    algorithm_action = next(a for a in generate_parser._actions if a.dest == "algorithm")
    assert set(algorithm_action.choices) == set(_load_generators())


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
