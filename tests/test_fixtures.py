"""Verifica le fixture di test stesse (TASK-5): dimensioni dei blob binari."""


def _parse_pool_array(s: str) -> list[str]:
    inner = s[s.index("(") + 1 : s.rindex(")")].strip()
    if not inner:
        return []
    return [x.strip() for x in inner.split(",")]


def test_reference_8x8_has_expected_blob_sizes(reference_8x8_doc):
    world = reference_8x8_doc["world"]
    assert world["width"] == 8
    assert world["height"] == 8

    level = world["levels"]["0"]
    cells = _parse_pool_array(level["tiles"]["cells"])
    splat = _parse_pool_array(level["terrain"]["splat"])
    cave_bitmap = _parse_pool_array(level["cave"]["bitmap"])

    assert len(cells) == 8 * 8
    assert len(splat) == 8 * 8 * 64
    assert len(cave_bitmap) == 154  # osservato in SPEC.md §2 per una mappa 8x8


def test_reference_8x8_file_is_small(reference_8x8_path):
    assert reference_8x8_path.stat().st_size < 100_000
