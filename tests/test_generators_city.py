"""Test per generators/city.py (TASK-35): rete stradale, isolati, lotti,
edifici e piazze (SPEC.md §9.4)."""

import collections
import copy
import json
import random
from pathlib import Path

import pytest

from ddforge.assets import load_catalog, palette_for
from ddforge.compose import render_city_blueprint
from ddforge.generators import city
from ddforge.godot import grid_to_px, parse_pv2
from ddforge.ids import IdAllocator
from ddforge.model import Blueprint
from ddforge.template import finalize, load_template, prepare
from ddforge.validate import validate

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = REPO_ROOT / "templates" / "blank_80x80.dungeondraft_map"
GOLDEN_DIR = REPO_ROOT / "tests" / "fixtures" / "golden"


# --- protocollo Generator ---------------------------------------------------


def test_generate_returns_a_blueprint_with_no_rooms():
    blueprint = city.generate(width=70, height=70, seed=1337)
    assert isinstance(blueprint, Blueprint)
    assert blueprint.rooms == []
    assert blueprint.corridors == []
    assert blueprint.style == "city"
    assert blueprint.streets != []
    assert blueprint.buildings != []


@pytest.mark.parametrize("scale", ["isolato", "quartiere", "citta"])
def test_same_seed_produces_identical_blueprint(scale):
    a = city.generate(width=70, height=70, seed=1337, scale=scale)
    b = city.generate(width=70, height=70, seed=1337, scale=scale)
    assert a == b


def test_different_seed_produces_a_different_city():
    a = city.generate(width=70, height=70, seed=1)
    b = city.generate(width=70, height=70, seed=2)
    assert a.streets != b.streets or [bp.rooms for bp in a.buildings] != [bp.rooms for bp in b.buildings]


def test_generator_does_not_depend_on_global_random_state():
    random.seed(111)
    random.random()
    a = city.generate(width=70, height=70, seed=99)

    random.seed(222)
    random.random()
    random.random()
    random.random()
    b = city.generate(width=70, height=70, seed=99)

    assert a == b


# --- AC3: la via principale e' piu larga delle strade secondarie ----------


@pytest.mark.parametrize("scale", ["isolato", "quartiere", "citta"])
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_main_street_is_wider_than_every_secondary_street(seed, scale):
    """La via principale e' quella con Street.main, non "la piu' larga":
    dopo TASK-41 una via obliqua e' larga come lei (vedi city._avenue)."""
    preset = city.SCALE_PRESETS[scale]
    blueprint = city.generate(width=70, height=70, seed=seed, scale=scale)

    main = [s for s in blueprint.streets if s.main]
    assert len(main) == 1, "un solo taglio a profondita 0"
    expected = preset.main_street_width * preset.street_path_fraction
    assert main[0].width == pytest.approx(expected)

    secondary = [s for s in blueprint.streets if not s.main and s.corridor is not None]
    assert all(main[0].width > s.width for s in secondary), [s.width for s in secondary]


@pytest.mark.parametrize("scale", ["isolato", "quartiere", "citta"])
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_street_centerline_stays_inside_its_reserved_corridor(seed, scale):
    """La centro-linea serpeggia (piu' di due vertici, scarto laterale non
    nullo) ma il selciato resta dentro l'ingombro riservato: e' da questo
    che dipendono le garanzie di TASK-35, non dalla forma del tracciato."""
    blueprint = city.generate(width=70, height=70, seed=seed, scale=scale)
    with_corridor = [s for s in blueprint.streets if s.corridor is not None]
    assert with_corridor, "nessuna via da un taglio"

    swaying = 0
    for street in with_corridor:
        corridor = street.corridor
        assert corridor is not None
        half = street.width / 2
        vertical = corridor.h >= corridor.w
        # Il vincolo e' LATERALE: lungo l'asse di marcia la via percorre tutto
        # l'ingombro da un capo all'altro, e la testa del tracciato sborda di
        # mezza larghezza sull'incrocio, che e' esattamente cio che serve.
        index = 0 if vertical else 1
        lo, hi = (corridor.x1, corridor.x2) if vertical else (corridor.y1, corridor.y2)
        along_lo, along_hi = (corridor.y1, corridor.y2) if vertical else (corridor.x1, corridor.x2)
        for point in street.points:
            lateral, along = point[index], point[1 - index]
            assert lo - 1e-9 <= lateral - half and lateral + half <= hi + 1e-9
            assert along_lo - 1e-9 <= along <= along_hi + 1e-9
        # gli estremi restano sull'asse: e' cio che tiene allineati gli incroci
        axis = (lo + hi) / 2
        assert street.points[0][index] == pytest.approx(axis)
        assert street.points[-1][index] == pytest.approx(axis)
        if len(street.points) > 2 and any(
            abs(p[index] - axis) > 1e-6 for p in street.points[1:-1]
        ):
            swaying += 1
    assert swaying > 0, "nessuna via serpeggia: la rete e' tornata una griglia"


@pytest.mark.parametrize("scale", ["isolato", "quartiere", "citta"])
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_an_oblique_avenue_crosses_the_map(seed, scale):
    """Richiesta di Jay: "le strade devono essere piu' irregolari, non solo
    verticali e orizzontali". La via obliqua e' l'unica senza ingombro
    riservato, e non e' ne' verticale ne' orizzontale."""
    preset = city.SCALE_PRESETS[scale]
    blueprint = city.generate(width=70, height=70, seed=seed, scale=scale)
    avenues = [s for s in blueprint.streets if s.corridor is None]
    assert len(avenues) == preset.avenues

    # Un canvas troppo piccolo per essere diviso nemmeno una volta non ha vie
    # oblique: sarebbe una strada su una mappa senza rete stradale. La soglia
    # dipende dal preset (preset.min_block varia da ~1,85 a 13 fra citta e
    # isolato), quindi il canvas "tiny" e' derivato da preset.min_block
    # invece di un 8x8 fisso tarato solo sui preset piu radi.
    too_small = int(2 * preset.min_block + preset.main_street_width)
    tiny_side = max(3, too_small)
    tiny = city.generate(width=tiny_side, height=tiny_side, seed=seed, scale=scale)
    assert [s for s in tiny.streets if s.corridor is None] == []

    for avenue in avenues:
        (x1, y1), (x2, y2) = avenue.points[0], avenue.points[-1]
        assert abs(x2 - x1) > 1 and abs(y2 - y1) > 1, "via ne' obliqua ne' passante"
        # da un bordo del canvas a quello opposto
        assert min(x1, x2) <= 1.001 or min(y1, y2) <= 1.001
        assert max(x1, x2) >= 69 - 0.001 or max(y1, y2) >= 69 - 0.001


@pytest.mark.parametrize("scale", ["isolato", "quartiere", "citta"])
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_no_building_sits_on_an_oblique_avenue(seed, scale):
    """La via obliqua non ha ingombro riservato: si fa spazio togliendo gli
    edifici che incontra (city._clear_avenue). Se non lo facesse, la strada
    passerebbe dentro le case."""
    preset = city.SCALE_PRESETS[scale]
    blueprint = city.generate(width=78, height=78, seed=seed, scale=scale)
    boxes = (
        list(blueprint.building_footprints) if preset.abstract_buildings
        else [city._footprint_of(bp) for bp in blueprint.buildings]
    )
    step = min(0.25, preset.min_building_side / 3)
    for avenue in (s for s in blueprint.streets if s.corridor is None):
        radius = avenue.width / 2 + preset.side_margin
        for box in boxes:
            assert not city._rect_near_polyline(box, avenue.points, radius, step=step), box


# --- AC1: ogni lotto ha fronte strada, ogni edificio e' accessibile -------


@pytest.mark.parametrize("scale", ["isolato", "quartiere", "citta"])
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_every_building_footprint_lies_within_a_block_touching_its_boundary(seed, scale):
    """Ogni edificio piazzato sta dentro l'isolato da cui e' stato ricavato
    E tocca (a meno del margine/arretramento) il lato fronte di quel
    isolato: e' la garanzia costruttiva di fronte-strada (AC1), verificata
    ricalcolando isolati e lotti con lo stesso RNG del generatore."""
    preset = city.SCALE_PRESETS[scale]
    rng = random.Random(seed)
    root = city.Rect(1, 1, 70 - 1, 70 - 1)
    streets: list = []
    blocks = city._build_blocks(root, rng, depth=0, streets=streets, preset=preset)
    n_plazas = 2 if len(blocks) >= 4 else (1 if len(blocks) >= 2 else 0)
    plaza_indices = set(rng.sample(range(len(blocks)), n_plazas)) if n_plazas else set()

    for i, block in enumerate(blocks):
        if i in plaza_indices:
            continue
        for lot, front in city._split_into_lots(block, preset):
            assert lot.x1 >= block.x1 and lot.y1 >= block.y1
            assert lot.x2 <= block.x2 and lot.y2 <= block.y2
            # Il lato fronte del lotto coincide col lato corrispondente
            # dell'isolato, che e' sempre bordato da una via (o dal margine
            # esterno della mappa). Con due file di lotti schiena contro
            # schiena il lato opposto e' quello dell'altra fila, non
            # dell'isolato: e' il fronte che conta, non entrambi i lati.
            if front == city._BOTTOM:
                assert lot.y2 == block.y2
            elif front == city._TOP:
                assert lot.y1 == block.y1
            elif front == city._RIGHT:
                assert lot.x2 == block.x2
            else:
                assert lot.x1 == block.x1


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_every_building_has_a_working_entrance(seed):
    """building.generate garantisce gia' una porta d'ingresso sul piano
    terra (bsp._ensure_entry, force=True): qui si verifica che city.py non
    perda quella garanzia nel tradurre/piazzare l'edificio."""
    blueprint = city.generate(width=70, height=70, seed=seed)
    for building_bp in blueprint.buildings:
        ground_rooms = [r for r in building_bp.rooms if r.level == 0]
        assert any(room.doors for room in ground_rooms), "nessuna porta al piano terra"


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_no_building_overlaps_a_street_or_a_plaza(seed):
    """Il confronto e' con l'ingombro riservato alla via (Street.corridor),
    non col tracciato: e' l'ingombro la garanzia geometrica, il selciato ci
    sta dentro per costruzione. Le vie oblique non hanno ingombro e sono
    verificate a parte (test_no_building_sits_on_an_oblique_avenue)."""
    blueprint = city.generate(width=70, height=70, seed=seed)
    obstacles = [s.corridor for s in blueprint.streets if s.corridor is not None]
    obstacles += list(blueprint.plazas)
    for building_bp in blueprint.buildings:
        footprint = city._footprint_of(building_bp)
        for obstacle in obstacles:
            assert not footprint.overlaps(obstacle), f"{footprint} vs {obstacle}"


# --- AC5: 1-2 piazze con pavimentazione diversa ed elemento centrale ------


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_one_or_two_plazas_are_present(seed):
    blueprint = city.generate(width=70, height=70, seed=seed)
    assert 1 <= len(blueprint.plazas) <= 2


def test_no_building_sits_inside_a_plaza_block():
    """Le piazze sono isolati esclusi dalla suddivisione in lotti (SPEC.md
    §9.4): nessun edificio dovrebbe avere un genitore in blueprint.plazas."""
    blueprint = city.generate(width=70, height=70, seed=1337)
    for plaza in blueprint.plazas:
        for building_bp in blueprint.buildings:
            assert not city._footprint_of(building_bp).overlaps(plaza)


# --- AC2/AC4/AC6: rendering end-to-end -------------------------------------


def test_end_to_end_render_through_render_city_blueprint_passes_validate():
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)

    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=70, height=70, seed=1337)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)
    finalize(prepared, ids)

    issues = validate(prepared)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], errors

    level = prepared["world"]["levels"]["0"]
    # AC2: le strade sono add_path, non pattern.
    assert len(level["paths"]) == len(blueprint.streets)
    # La texture e' una superficie stradale vera, non `cobble.png`, che a
    # dispetto del nome e' una texture da muretto (vedi il commento su
    # compose._STREET_TEXTURE: bocciata da Jay al primo round del gate).
    assert all(p["texture"] == "res://textures/paths/path_blender_03.png" for p in level["paths"])
    assert all(p["texture"] != "res://textures/paths/cobble.png" for p in level["paths"])
    # AC4: ogni edificio ha un tetto (un draw_building per edificio).
    assert len(level["roofs"]["roofs"]) == len(blueprint.buildings)


def test_plaza_pattern_uses_a_different_texture_than_buildings_and_has_a_fountain():
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=70, height=70, seed=1337)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)
    finalize(prepared, ids)

    level = prepared["world"]["levels"]["0"]
    plaza_patterns = [p for p in level["patterns"] if p["texture"] == palette.floors["piazza"]]
    assert len(plaza_patterns) == len(blueprint.plazas)
    assert palette.floors["piazza"] != palette.floor

    fountains = [o for o in level["objects"] if o["texture"] == palette.accents["fountain"]]
    assert len(fountains) == len(blueprint.plazas)


# --- AC2 (TASK-36): golden file, stessa alberatura di test_bsp_integration.py ----


def _generate_full_document(seed: int) -> dict:
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=70, height=70, seed=seed)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)
    finalize(prepared, ids)
    return prepared


def _normalize_for_golden(doc: dict) -> dict:
    doc = copy.deepcopy(doc)
    header = doc.get("header")
    if isinstance(header, dict) and "creation_date" in header:
        header["creation_date"] = "NORMALIZZATO-PER-IL-CONFRONTO-GOLDEN"
    return doc


@pytest.mark.slow
def test_city_golden_file_matches_reference_for_fixed_seed():
    """Per il seed 1337 (70x70, la stessa scala usata dagli altri test di
    questo file), il documento generato deve combaciare esattamente (a meno
    di creation_date) con tests/fixtures/golden/city_seed_1337.json. Se
    questo test fallisce dopo una modifica intenzionale al generatore,
    rigenerare il golden con lo script in questo stesso file
    (_generate_full_document) e verificare a mano il diff prima di
    sovrascrivere."""
    golden_path = GOLDEN_DIR / "city_seed_1337.json"
    actual = _normalize_for_golden(_generate_full_document(seed=1337))

    assert golden_path.exists(), f"Golden file mancante: {golden_path}"
    expected = json.loads(golden_path.read_text(encoding="utf-8"))
    assert actual == expected


# --- TASK-41: preset di scala isolato/quartiere/citta ----------------------


def test_scale_presets_are_exactly_the_three_named_by_jay_al_round_2():
    assert sorted(city.SCALE_PRESETS) == ["citta", "isolato", "quartiere"]
    assert city.DEFAULT_SCALE == "isolato"


def test_unknown_scale_fails_explicitly():
    with pytest.raises(ValueError, match="Preset di scala sconosciuto"):
        city.generate(width=70, height=70, seed=1337, scale="villaggio")


def test_default_scale_is_the_isolato_preset_unchanged():
    """AC2: il preset isolato deve restare bit per bit quello di TASK-35
    (si chiamava "quartiere" prima del round 2 del gate), che e' anche il
    default quando --scale non viene passato."""
    implicit = city.generate(width=70, height=70, seed=1337)
    explicit = city.generate(width=70, height=70, seed=1337, scale="isolato")
    assert implicit == explicit


def test_isolato_uses_buildings_quartiere_and_citta_use_footprints():
    """AC1/AC3/AC4: nel preset isolato ogni edificio e' un Blueprint
    completo; nei preset quartiere e citta e' un solo rettangolo di
    ingombro. I due campi si escludono a vicenda (vedi model.Blueprint)."""
    isolato = city.generate(width=70, height=70, seed=1337, scale="isolato")
    assert isolato.buildings != []
    assert isolato.building_footprints == []

    for scale in ("quartiere", "citta"):
        abstract = city.generate(width=70, height=70, seed=1337, scale=scale)
        assert abstract.building_footprints != []
        assert abstract.buildings == []
        assert all(isinstance(f, city.Rect) for f in abstract.building_footprints)


@pytest.mark.parametrize("seed", [0, 1, 1337, 42])
def test_quartiere_preset_fits_many_more_and_much_smaller_buildings_than_isolato(seed):
    """AC3: "1 quadretto = 1 edificio" contro "1 quadretto = 5 ft" deve
    vedersi nei numeri, sullo stesso canvas e con lo stesso seed."""
    isolato = city.generate(width=78, height=78, seed=seed, scale="isolato")
    quartiere = city.generate(width=78, height=78, seed=seed, scale="quartiere")

    assert len(quartiere.streets) > len(isolato.streets)
    assert len(quartiere.building_footprints) > 5 * len(isolato.buildings)

    quartiere_areas = [f.w * f.h for f in quartiere.building_footprints]
    assert max(quartiere_areas) < 30, "un edificio del preset quartiere resta di pochi quadretti"


@pytest.mark.parametrize("seed", [0, 1, 1337, 42])
def test_citta_preset_has_an_order_of_magnitude_more_buildings_than_quartiere(seed):
    """AC4: la citta e' capace di contenere una decina di quartieri, cioe'
    un ordine di grandezza in piu' di edifici del preset quartiere sullo
    stesso canvas. Misurato al momento della taratura (SCALE_PRESETS["citta"]):
    fra ~9,6x e ~10,8x su 7 seed a 78x78; qui si verifica un margine largo
    (5x-20x) per non far dipendere il test dal seed esatto."""
    quartiere = city.generate(width=78, height=78, seed=seed, scale="quartiere")
    citta = city.generate(width=78, height=78, seed=seed, scale="citta")

    ratio = len(citta.building_footprints) / len(quartiere.building_footprints)
    assert 5.0 < ratio < 20.0, (len(citta.building_footprints), len(quartiere.building_footprints), ratio)


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_abstract_footprints_never_overlap_streets_or_plazas(seed, scale):
    blueprint = city.generate(width=78, height=78, seed=seed, scale=scale)
    obstacles = [s.corridor for s in blueprint.streets if s.corridor is not None]
    obstacles += list(blueprint.plazas)
    for footprint in blueprint.building_footprints:
        for obstacle in obstacles:
            assert not footprint.overlaps(obstacle), f"{footprint} vs {obstacle}"


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
@pytest.mark.parametrize("seed", [0, 1, 2, 3, 1337, 42])
def test_abstract_footprints_stay_inside_the_canvas(seed, scale):
    blueprint = city.generate(width=78, height=78, seed=seed, scale=scale)
    preset = city.SCALE_PRESETS[scale]
    for footprint in blueprint.building_footprints:
        assert footprint.x1 >= 1 and footprint.y1 >= 1
        assert footprint.x2 <= 77 and footprint.y2 <= 77
        assert footprint.w >= preset.min_building_side
        assert footprint.h >= preset.min_building_side


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_abstract_preset_renders_and_validates_clean(scale):
    """AC7: il documento generato nei preset quartiere/citta passa validate()
    senza errori, e ogni edificio ha il suo pavimento e il suo tetto."""
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=78, height=78, seed=1337, scale=scale)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)
    finalize(prepared, ids)

    issues = validate(prepared)
    errors = [i for i in issues if i.severity == "error"]
    assert errors == [], errors

    level = prepared["world"]["levels"]["0"]
    assert len(level["paths"]) == len(blueprint.streets)
    # un tetto per edificio, nessuno di draw_building (che qui non gira)
    assert len(level["roofs"]["roofs"]) == len(blueprint.building_footprints)
    # un pavimento per edificio piu uno per piazza
    n_footprint_floors = sum(1 for p in level["patterns"] if p["texture"] == palette.floor)
    assert n_footprint_floors == len(blueprint.building_footprints)
    # nessun muro: a questa scala non c'e geometria di stanze da disegnare
    assert level["walls"] == []


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_abstract_roof_eaves_land_on_the_footprint_edges(scale):
    """Il tetto e' una linea di colmo con `width` = MEZZA larghezza
    (compose._ridge_line, verificato su un file Dungeondraft reale): con
    width = meta del lato corto le due gronde cadono sui bordi del
    footprint, senza sbordare sulla strada."""
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=78, height=78, seed=1337, scale=scale)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)

    roofs = prepared["world"]["levels"]["0"]["roofs"]["roofs"]
    assert len(roofs) == len(blueprint.building_footprints)
    for footprint, roof in zip(blueprint.building_footprints, roofs):
        (ax, ay), (bx, by) = parse_pv2(roof["points"])
        width = roof["width"]
        short_side = min(footprint.w, footprint.h)
        # la mezza larghezza non supera mai meta del lato corto: la gronda
        # cade sul bordo o appena dentro, mai fuori
        assert width <= grid_to_px(short_side) / 2 + 1e-6
        if footprint.h >= footprint.w:  # colmo verticale, lungo il lato lungo
            assert ax == bx == pytest.approx(grid_to_px((footprint.x1 + footprint.x2) / 2))
            assert sorted((ay, by)) == pytest.approx(
                [grid_to_px(footprint.y1), grid_to_px(footprint.y2)]
            )
        else:
            assert ay == by == pytest.approx(grid_to_px((footprint.y1 + footprint.y2) / 2))
            assert sorted((ax, bx)) == pytest.approx(
                [grid_to_px(footprint.x1), grid_to_px(footprint.x2)]
            )


def test_isolato_roofs_do_not_overhang_the_building():
    """Il tetto di draw_building e' un poligono chiuso con `width` 512, che
    con la semantica verificata in TASK-41 (width = MEZZA larghezza) si
    stende 2 quadretti oltre il perimetro su ogni lato: su una casa da 5x5
    quadretti sarebbe un tetto 9x9 in mezzo alla strada. render_city_blueprint
    lo disattiva e usa una linea di colmo (compose.add_ridge_roof), quindi qui
    ogni tetto deve avere 2 punti e stare dentro il suo edificio."""
    doc = load_template(TEMPLATE)
    prepared = prepare(doc, levels=1)
    ids = IdAllocator.from_document(prepared)
    catalog = load_catalog()
    palette = palette_for("city", catalog)

    blueprint = city.generate(width=78, height=78, seed=1337)
    render_city_blueprint(prepared["world"]["levels"], ids, blueprint, palette)

    roofs = prepared["world"]["levels"]["0"]["roofs"]["roofs"]
    assert len(roofs) == len(blueprint.buildings)
    footprints = [city._footprint_of(bp) for bp in blueprint.buildings]
    for footprint, roof in zip(footprints, roofs):
        points = parse_pv2(roof["points"])
        assert len(points) == 2, "tetto a poligono chiuso: sborda (vedi TASK-47)"
        half = roof["width"]
        # la falda arriva al piu' al bordo dell'edificio, mai oltre
        assert half <= grid_to_px(min(footprint.w, footprint.h)) / 2 + 1e-6
        for x, y in points:
            assert grid_to_px(footprint.x1) - 1e-6 <= x <= grid_to_px(footprint.x2) + 1e-6
            assert grid_to_px(footprint.y1) - 1e-6 <= y <= grid_to_px(footprint.y2) + 1e-6


def test_isolato_uses_more_than_one_building_type():
    """Richiesta di Jay: "non usare un unico oggetto per gli edifici ma usane
    di diversi tipi". Con le soglie del primo tentativo nessuna tipologia
    oltre "house" risultava mai ammissibile."""
    kinds = collections.Counter()
    for seed in range(8):
        blueprint = city.generate(width=78, height=78, seed=seed)
        for building_bp in blueprint.buildings:
            kinds[building_bp.style] += 1
    assert len(kinds) >= 3, kinds
    assert kinds["house"] > 0
    # nessuna tipologia deve monopolizzare del tutto: le case restano la
    # maggioranza (e' un quartiere abitato), ma non il 100%
    assert kinds["house"] < sum(kinds.values())


def test_isolato_buildings_are_house_sized_not_villa_sized():
    """Al primo round del gate gli edifici venivano 9,6x8,7 quadretti, cioe'
    181 m2 a 1,5 m per quadretto. Jay: "le case possono essere grandi la
    meta' di quello che sono"."""
    areas = []
    for seed in range(8):
        blueprint = city.generate(width=78, height=78, seed=seed)
        for building_bp in blueprint.buildings:
            footprint = city._footprint_of(building_bp)
            areas.append(footprint.w * footprint.h)
    mean_area = sum(areas) / len(areas)
    assert mean_area < 40, f"area media {mean_area:.0f} quadretti: edifici di nuovo troppo grandi"


def test_building_depth_is_capped_so_the_lot_keeps_a_yard():
    """La profondita' dell'edificio e' limitata da building_depth_range: senza
    quel tetto l'edificio riempie tutta la profondita' del lotto e viene una
    striscia lunga quanto l'isolato (il difetto del primo round nel preset
    quartiere)."""
    for scale in ("isolato", "quartiere", "citta"):
        preset = city.SCALE_PRESETS[scale]
        blueprint = city.generate(width=78, height=78, seed=1337, scale=scale)
        boxes = (
            list(blueprint.building_footprints) if preset.abstract_buildings
            else [city._footprint_of(bp) for bp in blueprint.buildings]
        )
        limit = preset.building_depth_range[1]
        for box in boxes:
            assert min(box.w, box.h) <= limit + 1e-6, (scale, box)
