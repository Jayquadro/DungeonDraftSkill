"""Test del sidecar `.ddforge.json` (TASK-66, docs/SPEC-decorate.md §4).

Due livelli: round-trip del Blueprint per ogni algoritmo (unita', senza
Dungeondraft) ed end-to-end via CLI (sidecar scritto accanto alla mappa,
hash corretto, nessun sidecar se la validazione blocca la scrittura).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ddforge.decorate.sidecar import (
    build_sidecar, deserialize_blueprint, hash_bytes, serialize_blueprint,
    sidecar_path, write_sidecar,
)
from ddforge.generators import bsp, building, cave, city, sewer
from ddforge.model import Blueprint, Landmark, Rect, Room


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "ddforge.cli", *args],
        capture_output=True,
        text=True,
    )


# --------------------------------------------------------------------------
# Round-trip per ogni algoritmo (AC3)
# --------------------------------------------------------------------------


def test_round_trip_bsp():
    bp = bsp.generate(width=60, height=60, seed=42, rooms=6)
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp


def test_round_trip_building_multi_piano():
    bp = building.generate(width=20, height=16, seed=7, building_type="tavern")
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp


def test_round_trip_building_l_shaped():
    bp = building.generate(width=24, height=20, seed=3, building_type="manor", l_shaped=True)
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp


def test_round_trip_cave():
    bp = cave.generate(width=80, height=80, seed=1337)
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp


def test_round_trip_sewer():
    bp = sewer.generate(width=40, height=40, seed=1337)
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp


def test_round_trip_city_isolato_with_buildings_and_landmarks():
    """scale='isolato' (default) popola sia `buildings` (Blueprint
    completi, non footprint) sia `landmarks` (--landmark forza 'tempio')."""
    bp = city.generate(width=70, height=70, seed=1337, requested_landmarks=["tempio"])
    assert bp.buildings, "il preset isolato deve produrre almeno un edificio completo"
    assert bp.landmarks, "il landmark forzato deve comparire"
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp


def test_round_trip_city_quartiere_with_footprints():
    """scale='quartiere' popola `building_footprints` invece di `buildings`
    (decision-2): ramo diverso del serializzatore, va testato separatamente."""
    bp = city.generate(width=78, height=78, seed=1337, scale="quartiere")
    assert bp.building_footprints
    assert not bp.buildings
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp


def test_round_trip_city_with_walls_river_port():
    """Mura, fiume e porto (TASK-48) sono opzionali: un giro con tutti e tre
    presenti copre i rami City* del serializzatore."""
    bp = city.generate(width=90, height=90, seed=2024, scale="citta")
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp
    # Non tutti i seed garantiscono mura/fiume/porto: verifica diretta che
    # il round-trip resti fedele anche quando sono effettivamente presenti,
    # senza richiedere che QUESTO seed li produca tutti.
    if bp.walls is not None:
        assert deserialize_blueprint(serialize_blueprint(bp)).walls == bp.walls
    if bp.river is not None:
        assert deserialize_blueprint(serialize_blueprint(bp)).river == bp.river
    if bp.port is not None:
        assert deserialize_blueprint(serialize_blueprint(bp)).port == bp.port


def test_round_trip_landmark_with_nested_building():
    """Landmark.building e' un Blueprint annidato (ricorsione esplicita del
    serializzatore): i sei landmark attualmente ammissibili a isolato sono
    tutti sprite_only (nessuna building reale nel generatore oggi), quindi
    si costruisce a mano il caso per coprire la ricorsione."""
    inner = Blueprint(
        width=8, height=6, rooms=[Room(rect=Rect(1, 1, 7, 5), kind="sala")],
        corridors=[], graph={0: []}, seed=1, style="house",
    )
    landmark = Landmark(
        kind="tempio", label="Tempio", rect=Rect(10, 10, 18, 16), site="lot",
        building=inner,
    )
    bp = Blueprint(
        width=40, height=40, rooms=[], corridors=[], graph={}, seed=1, style="city",
        landmarks=[landmark],
    )
    assert deserialize_blueprint(serialize_blueprint(bp)) == bp
    assert deserialize_blueprint(serialize_blueprint(bp)).landmarks[0].building == inner


# --------------------------------------------------------------------------
# End-to-end via CLI (AC1, AC2, AC4, AC5, AC6)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cli_args",
    [
        ["dungeon", "--width", "60", "--height", "60", "--rooms", "6", "--seed", "42"],
        ["building", "--width", "20", "--height", "16", "--seed", "7"],
        ["cave", "--width", "80", "--height", "80", "--seed", "1337"],
        ["sewer", "--width", "40", "--height", "40", "--seed", "1337"],
        ["city", "--width", "70", "--height", "70", "--seed", "1337"],
    ],
)
def test_generate_writes_sidecar_for_every_algorithm(tmp_path, cli_args):
    algorithm = cli_args[0]
    out = tmp_path / "out.dungeondraft_map"
    result = _run(
        "generate", *cli_args,
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert out.exists()

    sc_path = sidecar_path(out)
    assert sc_path.exists(), f"sidecar mancante per {algorithm}"

    sidecar = json.loads(sc_path.read_text(encoding="utf-8"))
    assert sidecar["ddforge_sidecar"] == 1
    assert sidecar["generator"]["algorithm"] == algorithm
    assert sidecar["template"] == "templates/blank_80x80.dungeondraft_map"
    assert sidecar["decorations"] == []
    assert sidecar["blueprint"]["rooms"] is not None  # sempre presente, anche se []

    map_bytes = out.read_bytes()
    assert sidecar["map_sha256"] == hash_bytes(map_bytes)
    assert sidecar["catalog_sha256"] == hash_bytes(Path("data/assets.json").read_bytes())

    # AC3: deserializzare il sidecar restituisce un Blueprint consistente
    # (round-trip esatto verificato sopra; qui si verifica solo che non
    # fallisca sul JSON realmente scritto da generate).
    bp = deserialize_blueprint(sidecar["blueprint"])
    assert bp.width > 0 and bp.height > 0


def test_generate_validation_failure_writes_neither_map_nor_sidecar(tmp_path):
    """AC5: se la validazione blocca generate (fixture 8x8 senza texts_vis,
    DDF003), non si scrive ne' la mappa ne' il sidecar."""
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
    assert not sidecar_path(out).exists()


def test_sidecar_cannot_be_disabled():
    """AC8: nessun flag spegne il sidecar (decisione di Jay, SPEC-decorate
    §14 D2). Verifica diretta sul parser: nessuna opzione lo cita."""
    import argparse

    from ddforge.cli import build_parser

    parser = build_parser()
    subparsers_action = next(
        a for a in parser._actions if isinstance(a, argparse._SubParsersAction)
    )
    generate_parser = subparsers_action.choices["generate"]
    option_strings = {s for a in generate_parser._actions for s in a.option_strings}
    assert not any("sidecar" in opt for opt in option_strings)


def test_sidecar_path_naming():
    assert sidecar_path("generated/cripta.dungeondraft_map") == Path("generated/cripta.ddforge.json")


def test_build_sidecar_contains_expected_keys(tmp_path):
    bp = bsp.generate(width=20, height=20, seed=1, rooms=3)
    catalog = tmp_path / "catalog.json"
    catalog.write_text("{}", encoding="utf-8")
    sidecar = build_sidecar(
        algorithm="dungeon", args={"seed": 1}, template="templates/blank_80x80.dungeondraft_map",
        catalog_path=catalog, map_bytes=b"abc", blueprint=bp,
    )
    assert sidecar["map_sha256"] == hash_bytes(b"abc")
    assert sidecar["decorations"] == []
    out_map = tmp_path / "out.dungeondraft_map"
    out_map.write_bytes(b"{}")
    path = write_sidecar(out_map, sidecar)
    assert path == tmp_path / "out.ddforge.json"
    assert json.loads(path.read_text(encoding="utf-8")) == sidecar
