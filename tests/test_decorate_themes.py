"""Test delle tabelle dei temi di abbellimento (TASK-68, SPEC-decorate §6.2).

Non testano piazzamento (quello arriva con planner.py, TASK-69): solo che
le tabelle siano dati leciti - ogni chiave risolve su una texture del
catalogo, ogni texture appartiene a un pack del manifest del template di
produzione, e i colori sono ARGB a 8 cifre.
"""

import json
import re

import pytest

from ddforge.decorate.themes import DEFAULT_ROLE, MAP_TYPES, THEMES, THEMES_TABLE, theme_for

_HEX8 = re.compile(r"^[0-9a-fA-F]{8}$")


@pytest.fixture(scope="module")
def catalog():
    with open("data/assets.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def catalog_keys(catalog):
    keys = set()
    for bucket in ("walls", "floors", "portals", "roofs", "paths", "objects", "terrain"):
        keys |= set(catalog[bucket].keys())
    return keys


@pytest.fixture(scope="module")
def manifest_ids():
    with open("templates/blank_80x80.dungeondraft_map", encoding="utf-8") as f:
        doc = json.load(f)
    return {m["id"] for m in doc["header"]["asset_manifest"]}


def _pack_of(texture_path: str) -> str | None:
    m = re.search(r"res://packs/([^/]+)/", texture_path)
    return m.group(1) if m else None


def test_every_theme_and_map_type_has_a_default_role():
    """AC4: un default per i ruoli non elencati."""
    for theme in THEMES:
        for map_type in MAP_TYPES:
            assert DEFAULT_ROLE in THEMES_TABLE[theme][map_type], (theme, map_type)


def test_all_six_map_types_are_covered_by_every_theme():
    for theme in THEMES:
        assert set(THEMES_TABLE[theme].keys()) == set(MAP_TYPES), theme


def _iter_zone_themes():
    for theme in THEMES:
        for map_type in MAP_TYPES:
            for role, zt in THEMES_TABLE[theme][map_type].items():
                yield theme, map_type, role, zt


def test_every_cited_key_resolves_to_a_catalog_texture(catalog_keys):
    """AC5."""
    for theme, map_type, role, zt in _iter_zone_themes():
        for field_name, key in (("floor", zt.floor), ("wall", zt.wall)):
            if key is not None:
                assert key in catalog_keys, (theme, map_type, role, field_name, key)
        for tp in zt.terrain:
            assert tp.slot in catalog_keys, (theme, map_type, role, "terrain", tp.slot)
        for oe in zt.objects:
            assert oe.key in catalog_keys, (theme, map_type, role, "object", oe.key)


def test_every_resolved_texture_belongs_to_a_manifest_pack(catalog, manifest_ids):
    """AC6."""
    key_to_texture = {}
    for bucket in ("walls", "floors", "portals", "roofs", "paths", "objects", "terrain"):
        key_to_texture.update(catalog[bucket])

    for theme, map_type, role, zt in _iter_zone_themes():
        keys = [zt.floor, zt.wall] + [tp.slot for tp in zt.terrain] + [oe.key for oe in zt.objects]
        for key in keys:
            if key is None:
                continue
            texture = key_to_texture[key]
            pack_id = _pack_of(texture)
            if pack_id is not None:
                assert pack_id in manifest_ids, (theme, map_type, role, key, pack_id)


def test_ambient_and_light_colors_are_argb8():
    """AC7."""
    for theme, map_type, role, zt in _iter_zone_themes():
        assert _HEX8.match(zt.ambient), (theme, map_type, role, "ambient", zt.ambient)
        if zt.lights is not None:
            assert _HEX8.match(zt.lights.color), (theme, map_type, role, "light.color", zt.lights.color)


def test_theme_for_falls_back_to_default_for_unknown_role():
    for theme in THEMES:
        for map_type in MAP_TYPES:
            default = THEMES_TABLE[theme][map_type][DEFAULT_ROLE]
            assert theme_for(theme, map_type, "ruolo_che_non_esiste_mai") == default


def test_object_classes_are_decal_or_ingombro():
    for theme, map_type, role, zt in _iter_zone_themes():
        for oe in zt.objects:
            assert oe.cls in ("decal", "ingombro"), (theme, map_type, role, oe.key, oe.cls)


def test_lights_are_disabled_only_explicitly_with_none():
    """Nessuna LightRule con parametri vuoti per errore: se una zona non
    vuole luci il campo e None, non una regola con range/intensity a zero."""
    for theme, map_type, role, zt in _iter_zone_themes():
        if zt.lights is not None:
            assert zt.lights.range > 0, (theme, map_type, role)
            assert zt.lights.intensity > 0, (theme, map_type, role)
            assert zt.lights.texture
