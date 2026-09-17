"""Test dei passi deterministici della procedura di post-processing sprite (TASK-50)."""

from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from ddforge.sprite_prep import batch, imaging, manifest, pipeline
from ddforge.sprite_prep.imaging import ProcessingError
from ddforge.sprite_prep.manifest import SpriteJob
from ddforge.sprite_prep.settings import CATEGORY_CANVAS, ScaleSettings, ShadowSettings

MAGENTA = (255, 0, 255)


def _flat_magenta_with_subject(size=(240, 240), box=(70, 70, 170, 170), color=(40, 60, 200)) -> Image.Image:
    """Sfondo magenta piatto con un rettangolo pieno al centro, bordi netti (nessuna frangia)."""
    img = Image.new("RGB", size, MAGENTA)
    left, top, right, bottom = box
    for y in range(top, bottom):
        for x in range(left, right):
            img.putpixel((x, y), color)
    return img


# --------------------------------------------------------------------------- #
# Chroma-key del magenta
# --------------------------------------------------------------------------- #


def test_magenta_chroma_key_flat_background_becomes_transparent():
    raw = _flat_magenta_with_subject()
    keyed = imaging.clean_alpha(imaging.magenta_chroma_key(raw))
    alpha = np.asarray(keyed.getchannel("A"))
    assert alpha[0, 0] == 0
    assert alpha[10, 200] == 0


def test_magenta_chroma_key_subject_stays_opaque_and_its_color_unchanged():
    raw = _flat_magenta_with_subject(color=(40, 60, 200))
    keyed = imaging.clean_alpha(imaging.magenta_chroma_key(raw))
    arr = np.asarray(keyed)
    center = arr[120, 120]
    assert center[3] == 255
    assert tuple(int(c) for c in center[:3]) == (40, 60, 200)


def test_magenta_chroma_key_despills_the_fringe():
    """Un pixel di bordo, meta' magenta e meta' soggetto, non deve restare rosa."""
    blended = tuple(round(MAGENTA[i] * 0.5 + (40, 60, 200)[i] * 0.5) for i in range(3))
    raw = Image.new("RGB", (4, 4), blended)
    keyed = imaging.magenta_chroma_key(raw)
    arr = np.asarray(keyed)[0, 0]
    r, g, _b, a = (int(v) for v in arr)
    assert 0 < a < 255, "il pixel di bordo deve restare semi-trasparente, non pieno o azzerato"
    assert abs(r - g) <= 1, f"la componente rossa deve tornare al livello del verde dopo il despill, r={r} g={g}"
    original_r_minus_g = blended[0] - blended[1]
    assert (r - g) < original_r_minus_g, "il despill deve ridurre la tinta magenta residua"


def test_edges_touched_counts_sides_reaching_the_frame():
    raw = Image.new("RGB", (100, 100), MAGENTA)
    for x in range(100):
        raw.putpixel((x, 0), (10, 10, 10))  # il soggetto tocca il bordo superiore
    keyed = imaging.clean_alpha(imaging.magenta_chroma_key(raw))
    assert imaging.edges_touched(keyed) >= 1


# --------------------------------------------------------------------------- #
# Geometria: canvas, centratura, ombra
# --------------------------------------------------------------------------- #


def test_target_geometry_canvas_mode_respects_margin_and_shadow_extent():
    scale, shadow = ScaleSettings(), ShadowSettings()
    side, canvas = imaging.target_geometry(768, "canvas", None, scale, shadow)
    assert canvas == 768
    # il lato + l'ombra deve stare nel canvas meno il margine dichiarato, per lato
    half_extent_px = side * (0.5 + shadow.extent)
    assert half_extent_px <= canvas / 2.0 - scale.margin * canvas + 1e-6


def test_target_geometry_reale_mode_uses_metres_and_rounds_canvas():
    scale, shadow = ScaleSettings(), ShadowSettings()
    side, canvas = imaging.target_geometry(256, "reale", 2.0, scale, shadow)
    assert side == round(2.0 * scale.px_per_m)
    assert canvas % scale.round_to == 0
    assert canvas >= 256


def test_target_geometry_reale_requires_size():
    with pytest.raises(ProcessingError):
        imaging.target_geometry(256, "reale", None, ScaleSettings(), ShadowSettings())


def test_place_centered_produces_exact_canvas_and_centred_content():
    obj = Image.new("RGBA", (50, 30), (10, 20, 30, 255))
    placed = imaging.place_centered(obj, side=100, canvas=200)
    assert placed.size == (200, 200)
    box = imaging.alpha_bbox(placed)
    assert box is not None
    left, top, right, bottom = box
    assert (left + right) / 2 == pytest.approx(100, abs=1)
    assert (top + bottom) / 2 == pytest.approx(100, abs=1)


def test_add_shadow_extends_alpha_below_right_without_changing_object_pixels():
    obj = imaging.place_centered(Image.new("RGBA", (40, 40), (200, 30, 30, 255)), side=40, canvas=120)
    shadowed = imaging.add_shadow(obj, side=40, cfg=ShadowSettings())
    obj_box = imaging.alpha_bbox(obj)
    shadow_box = imaging.alpha_bbox(shadowed)
    assert shadow_box[2] > obj_box[2]  # l'ombra sporge oltre il bordo destro dell'oggetto
    assert shadow_box[3] > obj_box[3]  # e oltre il bordo inferiore
    left, top, right, bottom = obj_box
    center = np.asarray(shadowed)[(top + bottom) // 2, (left + right) // 2]
    assert tuple(int(c) for c in center) == (200, 30, 30, 255)  # il soggetto non e' alterato dall'ombra


# --------------------------------------------------------------------------- #
# Validazione
# --------------------------------------------------------------------------- #


def _job(**overrides) -> SpriteJob:
    base = dict(source="x.jpg", stem="x", category="C3")
    base.update(overrides)
    return SpriteJob(**base)


def test_validate_object_flags_missing_alpha():
    opaque = Image.new("RGBA", (512, 512), (100, 100, 100, 255))
    warnings = pipeline.validate_object(opaque, _job(), ScaleSettings())
    assert any("alfa" in w for w in warnings)


def test_validate_object_flags_margin_violation():
    sprite = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for y in range(200):
        for x in range(200):
            sprite.putpixel((x, y), (10, 10, 10, 255))  # riempie tutto: nessun margine
    warnings = pipeline.validate_object(sprite, _job(), ScaleSettings(margin=0.05))
    assert any("margine" in w for w in warnings)


# --------------------------------------------------------------------------- #
# Manifest
# --------------------------------------------------------------------------- #


def test_manifest_sources_are_unique():
    sources = [job.source for job in manifest.MANIFEST]
    assert len(sources) == len(set(sources))


@pytest.mark.parametrize("stem,category", [("ospedale", "C2"), ("accademia", "C1"), ("biblioteca", "C3")])
def test_manifest_canvas_matches_category_table(stem, category):
    job = next(j for j in manifest.MANIFEST if j.stem == stem)
    assert job.category == category
    assert job.canvas == CATEGORY_CANVAS[category]


def test_manifest_reale_scale_jobs_declare_size_m():
    for job in manifest.MANIFEST:
        if job.scale_mode == "reale":
            assert job.size_m, f"{job.stem}: scala 'reale' senza dimensioni_m"


# --------------------------------------------------------------------------- #
# Pipeline end-to-end (fixture sintetica) e salvataggio PNG
# --------------------------------------------------------------------------- #


def test_process_job_end_to_end_produces_valid_square_rgba_png(tmp_path):
    raw = _flat_magenta_with_subject(size=(400, 400), box=(120, 120, 280, 260), color=(196, 90, 60))
    job = _job(category="C3")
    result = pipeline.process_job(raw, job, ScaleSettings(), ShadowSettings())

    assert result.image.mode == "RGBA"
    assert result.image.size == (job.canvas, job.canvas)
    assert imaging.has_real_alpha(result.image)

    out_path = tmp_path / job.filename
    imaging.save_png(result.image, out_path)
    with out_path.open("rb") as fh:
        assert fh.read(8) == imaging.PNG_SIGNATURE
    reloaded = Image.open(out_path)
    assert reloaded.size == (job.canvas, job.canvas)
    assert reloaded.mode == "RGBA"


def test_process_job_raises_on_empty_image():
    raw = Image.new("RGB", (50, 50), MAGENTA)  # tutto sfondo, nessun soggetto
    with pytest.raises(ProcessingError):
        pipeline.process_job(raw, _job(), ScaleSettings(), ShadowSettings())


def test_process_job_does_not_touch_the_subject_color():
    """TASK-53: niente normalizzazione del rosso, il colore resta quello del
    JPEG di partenza - compreso un rosso che in una versione precedente della
    procedura sarebbe stato interpretato come tetto e ridipinto."""
    color = (196, 90, 60)  # dentro la ex "finestra di tinta" del tetto
    raw = _flat_magenta_with_subject(size=(400, 400), box=(120, 120, 280, 260), color=color)
    result = pipeline.process_job(raw, _job(category="C3"), ScaleSettings(), ShadowSettings())
    box = imaging.alpha_bbox(result.image)
    assert box is not None
    left, top, right, bottom = box
    center = np.asarray(result.image)[(top + bottom) // 2, (left + right) // 2]
    assert tuple(int(c) for c in center[:3]) == color


# --------------------------------------------------------------------------- #
# Passaggio su una cartella intera
# --------------------------------------------------------------------------- #


def test_run_batch_reports_ok_missing_and_ignored(tmp_path):
    input_dir = tmp_path / "in"
    output_dir = tmp_path / "out"
    input_dir.mkdir()

    _flat_magenta_with_subject(size=(400, 400), box=(120, 120, 280, 260), color=(196, 90, 60)).save(
        input_dir / "ospedale.jpg"
    )
    Image.new("RGB", (10, 10), (0, 0, 0)).save(input_dir / "misteriosa.png")

    report = batch.run_batch(input_dir, output_dir)

    by_source = {e["source"]: e for e in report["sprite"]}
    assert by_source["ospedale.jpg"]["stato"] in ("ok", "avvisi")
    assert (output_dir / "nm_ospedale.png").exists()
    assert by_source["teatro.jpg"]["stato"] == "mancante"
    assert "misteriosa.png" in report["ignorati"]
    assert report["riepilogo"]["mancante"] == len(manifest.MANIFEST) - 1
