"""Test dell'assemblaggio del pack Dungeondraft dai PNG pronti (TASK-51)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from ddforge.pack_build.builder import assemble_pack
from ddforge.pack_build.metadata import build_pack_json, resolve_pack_id
from ddforge.pack_build.settings import PackSettings
from ddforge.sprite_prep.manifest import MANIFEST

# --------------------------------------------------------------------------- #
# resolve_pack_id: stabile fra una riassemblata e l'altra (AC2)
# --------------------------------------------------------------------------- #


def test_resolve_pack_id_generates_stable_id_of_the_observed_shape(tmp_path):
    id_file = tmp_path / "pack_id.txt"
    first = resolve_pack_id(id_file)
    assert len(first) == 8
    assert first.isalnum()
    assert id_file.read_text(encoding="utf-8").strip() == first


def test_resolve_pack_id_reuses_existing_file_instead_of_generating_a_new_one(tmp_path):
    id_file = tmp_path / "pack_id.txt"
    first = resolve_pack_id(id_file)
    second = resolve_pack_id(id_file)
    assert first == second


def test_resolve_pack_id_reads_a_preexisting_id_untouched(tmp_path):
    id_file = tmp_path / "pack_id.txt"
    id_file.write_text("Hk3gdwPN", encoding="utf-8")
    assert resolve_pack_id(id_file) == "Hk3gdwPN"


# --------------------------------------------------------------------------- #
# build_pack_json: nessun canale di ricolorabilita' (TASK-53)
# --------------------------------------------------------------------------- #


def test_build_pack_json_disables_recoloring_and_has_the_real_pack_schema():
    """TASK-53: Jay ha rinunciato al canale custom_color di Dungeondraft dopo
    due giri di bug nella normalizzazione del rosso dei tetti - il pack non
    lo offre piu'."""
    manifest = build_pack_json(PackSettings(), "abcd1234")
    assert manifest["custom_color_overrides"]["enabled"] is False
    assert set(manifest) == {
        "name", "id", "version", "author", "keywords",
        "allow_3rd_party_mapping_software_to_read", "custom_color_overrides",
    }
    assert manifest["keywords"] is None
    assert manifest["allow_3rd_party_mapping_software_to_read"] is False


def test_build_pack_json_carries_the_pack_settings_and_id():
    pack = PackSettings(name="Test Pack", folder="TestPack", author="Someone", version="2.0")
    manifest = build_pack_json(pack, "abcd1234")
    assert manifest["name"] == "Test Pack"
    assert manifest["author"] == "Someone"
    assert manifest["version"] == "2.0"
    assert manifest["id"] == "abcd1234"


# --------------------------------------------------------------------------- #
# assemble_pack: struttura della cartella (AC1), niente elaborato a caso
# --------------------------------------------------------------------------- #


def _write_png(path: Path, color=(40, 60, 200, 255), size=(8, 8)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", size, color).save(path, format="PNG")


def test_assemble_pack_creates_the_full_folder_structure(tmp_path):
    sprites_dir = tmp_path / "sprites"
    for job in MANIFEST:
        _write_png(sprites_dir / job.filename)

    report = assemble_pack(sprites_dir, tmp_path / "dist", id_file=tmp_path / "pack_id.txt")

    root = report["folder"]
    assert (root / "pack.json").is_file()
    assert (root / "preview.png").is_file()
    assert (root / "textures" / "objects").is_dir()
    assert (root / "textures" / "terrain").is_dir()
    assert (root / "textures" / "patterns" / "normal").is_dir()
    assert not report["mancanti"]
    assert len(report["copiati"]) == len(MANIFEST)
    for job in MANIFEST:
        assert (root / "textures" / "objects" / job.filename).is_file()


def test_assemble_pack_only_copies_files_present_and_reports_the_rest_as_missing(tmp_path):
    sprites_dir = tmp_path / "sprites"
    first_job = MANIFEST[0]
    _write_png(sprites_dir / first_job.filename)

    report = assemble_pack(sprites_dir, tmp_path / "dist", id_file=tmp_path / "pack_id.txt")

    assert report["copiati"] == [first_job.filename]
    assert set(report["mancanti"]) == {job.filename for job in MANIFEST[1:]}


def test_assemble_pack_skips_the_preview_when_nothing_was_copied(tmp_path):
    report = assemble_pack(tmp_path / "empty", tmp_path / "dist", id_file=tmp_path / "pack_id.txt")
    assert report["copiati"] == []
    assert not (report["folder"] / "preview.png").exists()


def test_assemble_pack_keeps_the_same_id_across_two_runs(tmp_path):
    sprites_dir = tmp_path / "sprites"
    _write_png(sprites_dir / MANIFEST[0].filename)
    id_file = tmp_path / "pack_id.txt"

    first = assemble_pack(sprites_dir, tmp_path / "dist1", id_file=id_file)
    second = assemble_pack(sprites_dir, tmp_path / "dist2", id_file=id_file)

    assert first["pack_id"] == second["pack_id"]


def test_assemble_pack_preview_is_a_valid_png_with_one_thumbnail_per_sprite(tmp_path):
    sprites_dir = tmp_path / "sprites"
    for job in MANIFEST[:3]:
        _write_png(sprites_dir / job.filename)

    report = assemble_pack(sprites_dir, tmp_path / "dist", id_file=tmp_path / "pack_id.txt")

    with Image.open(report["folder"] / "preview.png") as im:
        im.verify()
