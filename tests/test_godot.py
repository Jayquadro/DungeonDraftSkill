"""Test per ddforge.godot: v2, pv2, parse_pv2, argb, grid_to_px."""

import pytest

from ddforge.godot import GRID, argb, grid_to_px, parse_pv2, pv2, v2


def test_v2_exact_format():
    assert v2(256, 512) == "Vector2( 256, 512 )"


def test_v2_with_floats():
    assert v2(1029.38, 979.371) == "Vector2( 1029.38, 979.371 )"


def test_pv2_flattens_points_not_grouped():
    result = pv2([(0, 0), (2560, 0)])
    assert result == "PoolVector2Array( 0, 0, 2560, 0 )"


def test_pv2_empty():
    assert pv2([]) == "PoolVector2Array(  )"


@pytest.mark.parametrize(
    "points",
    [
        [],
        [(0, 0)],
        [(512, 512), (2048, 512)],
        [(1029.38, 979.371), (-100.5, 0), (0, -50.25)],
    ],
)
def test_roundtrip_pv2_parse_pv2_pv2_is_idempotent(points):
    s1 = pv2(points)
    parsed = parse_pv2(s1)
    s2 = pv2(parsed)
    assert s1 == s2


def test_parse_pv2_matches_original_points():
    points = [(512.0, 512.0), (2048.0, 512.0)]
    assert parse_pv2(pv2(points)) == points


def test_parse_pv2_rejects_invalid_string():
    with pytest.raises(ValueError):
        parse_pv2("Vector2( 1, 2 )")


@pytest.mark.parametrize("n", [8.567903932998888e-05, -0.0000000001, 5e-10])
def test_pv2_never_emits_scientific_notation(n):
    """repr() passa a 'e' sotto 1e-4 (osservato con coordinate vicine a zero
    nel preset "citta" di generators/city.py, TASK-41): ne' il letterale
    Godot ne' _PV2_RE/parse_pv2 la riconoscono (DDF007 in validate.py)."""
    s = pv2([(0, 0), (n, 1.0)])
    inner = s[s.index("(") + 1 : s.rindex(")")]
    assert "e" not in inner and "E" not in inner
    assert parse_pv2(s) == [(0.0, 0.0), (n, 1.0)]


def test_argb_prepends_full_alpha_by_default():
    assert argb("aabbcc") == "ffaabbcc"


def test_argb_accepts_explicit_alpha():
    assert argb("aabbcc", alpha=0x7f) == "7faabbcc"


def test_argb_rejects_already_8_digit_input():
    with pytest.raises(ValueError):
        argb("ffaabbcc")


@pytest.mark.parametrize("bad", ["", "aabbc", "aabbccd", "gghhii", "aabbcc1"])
def test_argb_rejects_wrong_length_or_non_hex(bad):
    with pytest.raises(ValueError):
        argb(bad)


def test_grid_to_px_uses_grid_constant():
    assert GRID == 256
    assert grid_to_px(1) == 256
    assert grid_to_px(2.5) == 640
