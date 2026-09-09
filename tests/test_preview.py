"""Test per il renderer PNG di anteprima e il comando `ddforge preview` (TASK-37).

Pillow resta una dipendenza opzionale del progetto (SPEC.md §1.3, AC4): i
test che producono davvero un PNG saltano se non e installata
(`pytest.importorskip`), cosi la suite resta verde anche senza. Il test del
messaggio "Pillow mancante" (AC5) non richiede Pillow disinstallata: forza
`sys.modules['PIL'] = None`, che fa fallire `import PIL` con ImportError
indipendentemente da cosa e installato davvero.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ddforge.preview import PillowMissingError, render_preview


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "ddforge.cli", *args],
        capture_output=True,
        text=True,
    )


def _generate_dungeon(tmp_path, seed=1337) -> Path:
    out = tmp_path / "dungeon.dungeondraft_map"
    result = _run(
        "generate", "dungeon",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out),
        "--width", "40", "--height", "40",
        "--rooms", "6", "--seed", str(seed),
        "--furnish", "medium", "--lights",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return out


# ---------------------------------------------------------------------------
# AC5: messaggio chiaro se Pillow manca, non un traceback
# ---------------------------------------------------------------------------

def test_render_preview_without_pillow_raises_clear_error(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "PIL", None)
    doc = json.loads(Path("templates/blank_80x80.dungeondraft_map").read_text(encoding="utf-8"))

    with pytest.raises(PillowMissingError, match="Pillow"):
        render_preview(doc, tmp_path / "out.png")


def test_cli_preview_without_pillow_prints_clear_message_not_traceback(tmp_path):
    doc_path = tmp_path / "in.dungeondraft_map"
    doc_path.write_text(
        Path("templates/blank_80x80.dungeondraft_map").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    out_path = tmp_path / "out.png"
    script = (
        "import sys; sys.modules['PIL'] = None; "
        "from ddforge.cli import main; "
        f"sys.exit(main(['preview', {str(doc_path)!r}, '--out', {str(out_path)!r}]))"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Pillow" in (result.stdout + result.stderr)
    assert "Traceback" not in result.stderr
    assert not out_path.exists()


# ---------------------------------------------------------------------------
# AC1/AC2/AC3/AC6: rendering vero, richiede Pillow installato
# ---------------------------------------------------------------------------

def test_render_preview_produces_a_readable_png(tmp_path):
    pytest.importorskip("PIL")
    from PIL import Image

    doc_path = _generate_dungeon(tmp_path)
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    out = tmp_path / "preview.png"

    render_preview(doc, out)

    assert out.exists()
    world = doc["world"]
    with Image.open(out) as img:
        assert img.format == "PNG"
        # world.width/height vengono dal template (blob dimensionati su di
        # esso, SPEC.md §2), non da --width/--height passato a 'generate':
        # blank_80x80.dungeondraft_map resta 80x80 anche generando dentro
        # una sotto-regione 40x40.
        assert img.size == (world["width"] * 8, world["height"] * 8)


def test_render_preview_shows_distinct_colors_for_walls_doors_floors_objects(tmp_path):
    """AC2: muri, porte, pavimenti e oggetti devono essere distinguibili,
    cioe renderizzati con colori diversi fra loro e dallo sfondo."""
    pytest.importorskip("PIL")
    from PIL import Image

    doc_path = _generate_dungeon(tmp_path)
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    out = tmp_path / "preview.png"
    render_preview(doc, out)

    with Image.open(out) as img:
        raw_colors = img.getcolors(maxcolors=1_000_000)
    assert raw_colors is not None
    colors = {color for _count, color in raw_colors}

    from ddforge.preview import _BACKGROUND, _DOOR, _FLOOR, _OBJECT, _WALL

    for expected in (_BACKGROUND, _FLOOR, _WALL, _DOOR, _OBJECT):
        assert expected in colors, f"colore atteso {expected} assente dal PNG"


def test_render_preview_reads_the_written_file_not_a_blueprint(tmp_path):
    """AC3: il renderer non prende nulla in input se non il documento JSON
    gia scritto — verificato rigenerando lo stesso file da zero, caricandolo
    da disco, e controllando che il render non sollevi e produca lo stesso
    PNG byte per byte a parita di seed."""
    pytest.importorskip("PIL")

    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    doc_path_a = _generate_dungeon(tmp_path / "a", seed=99)
    doc_path_b = _generate_dungeon(tmp_path / "b", seed=99)

    out_a = tmp_path / "a.png"
    out_b = tmp_path / "b.png"
    render_preview(json.loads(doc_path_a.read_text(encoding="utf-8")), out_a)
    render_preview(json.loads(doc_path_b.read_text(encoding="utf-8")), out_b)

    assert out_a.read_bytes() == out_b.read_bytes()


def test_render_preview_rejects_unknown_level():
    pytest.importorskip("PIL")
    doc = json.loads(Path("templates/blank_80x80.dungeondraft_map").read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="9"):
        render_preview(doc, "unused.png", level_id="9")


def test_render_preview_on_cave_map_is_not_blank(tmp_path):
    """La grotta usa il layer cave nativo, non walls/patterns
    (generators/cave.py, decision-1): senza decodifica del bitmap
    l'anteprima sarebbe un canvas vuoto, non 'leggibile' (AC1)."""
    pytest.importorskip("PIL")
    from PIL import Image

    out_map = tmp_path / "cave.dungeondraft_map"
    result = _run(
        "generate", "cave",
        "--template", "templates/blank_80x80.dungeondraft_map",
        "--out", str(out_map),
        "--width", "80", "--height", "80",
        "--seed", "1337",
    )
    assert result.returncode == 0, result.stdout + result.stderr

    out_png = tmp_path / "cave.png"
    doc = json.loads(out_map.read_text(encoding="utf-8"))
    render_preview(doc, out_png)

    from ddforge.preview import _BACKGROUND, _FLOOR

    with Image.open(out_png) as img:
        raw_colors = img.getcolors(maxcolors=1_000_000)
    assert raw_colors is not None
    colors = {color for _count, color in raw_colors}
    assert _BACKGROUND in colors
    assert _FLOOR in colors


# ---------------------------------------------------------------------------
# AC6: il comando CLI e coperto da test end-to-end
# ---------------------------------------------------------------------------

def test_cli_preview_writes_png_next_to_the_input_by_default(tmp_path):
    pytest.importorskip("PIL")
    doc_path = _generate_dungeon(tmp_path)
    result = _run("preview", str(doc_path))
    assert result.returncode == 0, result.stdout + result.stderr

    expected_out = doc_path.with_suffix(".png")
    assert expected_out.exists()
    assert "Scritto" in result.stdout


def test_cli_preview_honors_explicit_out_path(tmp_path):
    pytest.importorskip("PIL")
    doc_path = _generate_dungeon(tmp_path)
    out = tmp_path / "custom.png"
    result = _run("preview", str(doc_path), "--out", str(out))
    assert result.returncode == 0, result.stdout + result.stderr
    assert out.exists()


def test_cli_preview_missing_file_exits_one_with_clear_message():
    result = _run("preview", "non_esiste_davvero.dungeondraft_map")
    assert result.returncode == 1
    assert "non trovato" in (result.stdout + result.stderr).lower()
    assert "Traceback" not in result.stderr


def test_cli_preview_invalid_json_exits_one_with_clear_message(tmp_path):
    p = tmp_path / "broken.dungeondraft_map"
    p.write_text("{not json", encoding="utf-8")
    result = _run("preview", str(p))
    assert result.returncode == 1
    assert "JSON" in (result.stdout + result.stderr)
    assert "Traceback" not in result.stderr
