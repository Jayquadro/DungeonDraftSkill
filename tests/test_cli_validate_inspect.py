"""Test per i comandi CLI `ddforge validate` e `ddforge inspect` (TASK-16)."""

import json
import subprocess
import sys


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "ddforge.cli", *args],
        capture_output=True,
        text=True,
    )


def test_validate_valid_file_exits_zero():
    result = _run("validate", "templates/blank_80x80.dungeondraft_map")
    assert result.returncode == 0
    assert "Nessun problema" in result.stdout


def test_validate_missing_file_exits_one_with_clear_message():
    result = _run("validate", "non_esiste_davvero.dungeondraft_map")
    assert result.returncode == 1
    assert "non trovato" in (result.stdout + result.stderr).lower()
    assert "Traceback" not in result.stderr


def test_validate_invalid_json_exits_one_with_clear_message(tmp_path):
    p = tmp_path / "broken.dungeondraft_map"
    p.write_text("{not json", encoding="utf-8")
    result = _run("validate", str(p))
    assert result.returncode == 1
    assert "JSON" in (result.stdout + result.stderr)
    assert "Traceback" not in result.stderr


def test_validate_document_with_errors_exits_one_and_prints_codes(tmp_path):
    broken = {"header": {}}  # manca world -> DDF001
    p = tmp_path / "broken.dungeondraft_map"
    p.write_text(json.dumps(broken), encoding="utf-8")
    result = _run("validate", str(p))
    assert result.returncode == 1
    assert "DDF001" in result.stdout
    assert "ERRORE" in result.stdout


def test_inspect_prints_dimensions_format_build_and_packs():
    result = _run("inspect", "templates/rich_reference.dungeondraft_map")
    assert result.returncode == 0
    assert "80 x 80" in result.stdout
    assert "Format: 3" in result.stdout
    assert "1.2.0.1" in result.stdout
    assert "Livelli: 1" in result.stdout
    assert "Pack referenziati (42)" in result.stdout


def test_inspect_prints_element_counts_per_level():
    result = _run("inspect", "templates/rich_reference.dungeondraft_map")
    assert "walls: 2" in result.stdout
    assert "portali annidati nei muri: 2" in result.stdout
    assert "lights: 1" in result.stdout
    assert "roofs.roofs: 1" in result.stdout


def test_inspect_missing_file_exits_one_with_clear_message():
    result = _run("inspect", "non_esiste_davvero.dungeondraft_map")
    assert result.returncode == 1
    assert "non trovato" in (result.stdout + result.stderr).lower()
    assert "Traceback" not in result.stderr


def test_inspect_invalid_json_exits_one_with_clear_message(tmp_path):
    p = tmp_path / "broken.dungeondraft_map"
    p.write_text("{not json", encoding="utf-8")
    result = _run("inspect", str(p))
    assert result.returncode == 1
    assert "JSON" in (result.stdout + result.stderr)
    assert "Traceback" not in result.stderr
