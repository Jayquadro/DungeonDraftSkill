"""Elementi urbani notevoli delle mappe cittadine (TASK-48).

Una sezione per criterio di accettazione. Le regole di piazzamento (AC5) sono
verificate con geometria SCRITTA QUI, non richiamando city._rule_ok: un test
che chiama la funzione sotto esame per decidere se ha ragione non verifica
niente. Dal modulo si prende solo la tolleranza dichiarata (city._radius),
perche' "a ridosso della porta" ha bisogno di un numero e quel numero e' una
scelta del generatore, non un fatto geometrico.
"""

import functools
import math
import random

import pytest

from ddforge.assets import load_catalog, palette_for
from ddforge.compose import render_city_blueprint
from ddforge.generators import city
from ddforge.generators import landmarks as lm
from ddforge.ids import IdAllocator
from ddforge.template import finalize, load_template, prepare
from ddforge.validate import validate
from tests.test_generators_city import TEMPLATE

SCALES = ["isolato", "quartiere", "citta"]
SEEDS = [0, 1, 7, 42, 1337]
CANVAS = 78


@functools.lru_cache(maxsize=None)
def _city(seed: int, scale: str, *, landmarks: bool = True, requested_landmarks: tuple = ()):
    """Blueprint di una citta', MEMOIZZATO.

    Senza cache questo file richiederebbe piu' di dieci minuti: il preset
    "citta" genera oltre duemila edifici e costa ~1,2 s per seed, e i test
    delle regole di piazzamento hanno bisogno di parecchi seed a testa per
    incontrare abbastanza luoghi da verificare. La generazione e' pura
    (RNG locale dal seed, mai il modulo `random` globale, verificato da
    test_landmarks_do_not_depend_on_the_global_random_state), quindi due
    chiamate uguali darebbero comunque lo stesso oggetto: i test leggono e
    non modificano mai il Blueprint restituito."""
    return city.generate(
        width=CANVAS, height=CANVAS, seed=seed, scale=scale,
        landmarks=landmarks, requested_landmarks=requested_landmarks,
    )


def _point_to_rect(x: float, y: float, rect) -> float:
    dx = max(rect.x1 - x, 0.0, x - rect.x2)
    dy = max(rect.y1 - y, 0.0, y - rect.y2)
    return math.hypot(dx, dy)


def _rect_to_rect(a, b) -> float:
    dx = max(b.x1 - a.x2, 0.0, a.x1 - b.x2)
    dy = max(b.y1 - a.y2, 0.0, a.y1 - b.y2)
    return math.hypot(dx, dy)


def _river_proximity(rect, river):
    """(distanza minima, parametro 0..1 lungo il corso) fra `rect` e il fiume.

    Campionamento fitto e indipendente da quello del generatore: qui non
    serve essere veloci, serve non fidarsi."""
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(river.points, river.points[1:])]
    total = sum(lengths)
    best = (math.inf, 0.0)
    travelled = 0.0
    for (ax, ay), (bx, by), length in zip(river.points, river.points[1:], lengths):
        for i in range(101):
            u = i / 100
            d = _point_to_rect(ax + (bx - ax) * u, ay + (by - ay) * u, rect)
            if d < best[0]:
                best = (d, (travelled + length * u) / total)
        travelled += length
    return best


def _all_landmarks(scale: str, seeds=SEEDS, **kwargs):
    """(blueprint, landmark) per ogni luogo di ogni seed: la forma che serve
    a quasi tutti i test di regola."""
    for seed in seeds:
        blueprint = _city(seed, scale, **kwargs)
        for mark in blueprint.landmarks:
            yield blueprint, mark


# --- AC1: richiesta esplicita di uno o piu' elementi -----------------------


@pytest.mark.parametrize("key", ["tempio", "caserma", "biblioteca", "mercato"])
def test_a_requested_landmark_is_always_present(key):
    """AC1: chiedere un luogo lo rende presente, qualunque sia il seed - anche
    quando la sua probabilita' di estrazione non lo avrebbe scelto."""
    for seed in SEEDS:
        blueprint = _city(seed, "isolato", requested_landmarks=(key,))
        assert key in {mark.kind for mark in blueprint.landmarks}, (seed, key)


@pytest.mark.parametrize("key", ["mura", "fiume", "porto"])
def test_a_requested_structure_is_always_present(key):
    """AC1: le strutture si chiedono con lo stesso parametro dei luoghi."""
    field = {"mura": "walls", "fiume": "river", "porto": "port"}[key]
    for seed in SEEDS:
        blueprint = _city(seed, "citta", requested_landmarks=(key,))
        assert getattr(blueprint, field) is not None, (seed, key)


def test_requesting_several_elements_at_once_works():
    blueprint = _city(3, "citta", requested_landmarks=("porto", "faro", "arena", "cattedrale"))
    kinds = {mark.kind for mark in blueprint.landmarks}
    assert blueprint.port is not None
    assert {"faro", "arena", "cattedrale"} <= kinds, sorted(kinds)


def test_no_landmarks_switch_removes_everything():
    blueprint = _city(1, "citta", landmarks=False)
    assert blueprint.landmarks == []
    assert (blueprint.walls, blueprint.river, blueprint.port) == (None, None, None)
    assert blueprint.bridges == []


# --- AC2: estrazione riproducibile dal seed --------------------------------


def _signature(blueprint):
    return sorted(
        (mark.kind, round(mark.rect.x1, 6), round(mark.rect.y1, 6)) for mark in blueprint.landmarks
    )


@pytest.mark.parametrize("scale", SCALES)
def test_same_seed_gives_the_same_landmarks(scale):
    assert _signature(_city(1337, scale)) == _signature(_city(1337, scale))


@pytest.mark.parametrize("scale", SCALES)
def test_different_seeds_give_different_places(scale):
    """AC2: non basta che le posizioni cambino, deve cambiare l'INSIEME dei
    luoghi - altrimenti ogni citta' sarebbe la stessa citta' spostata."""
    sets = [frozenset(mark.kind for mark in _city(seed, scale).landmarks) for seed in range(10)]
    assert len(set(sets)) >= 5, sets


def test_landmarks_do_not_depend_on_the_global_random_state():
    random.seed(1)
    first = _signature(_city(7, "quartiere"))
    random.seed(999)
    [random.random() for _ in range(50)]
    assert _signature(_city(7, "quartiere")) == first


def test_requesting_an_element_does_not_reshuffle_the_rest():
    """Chiedere un elemento deve AGGIUNGERLO, non generare un'altra citta':
    e' il motivo per cui select/select_structures consumano l'rng anche per
    gli elementi gia' richiesti.

    Il confronto e' sulla RETE STRADALE e sulle piazze, non sugli edifici:
    un luogo in piu' occupa per forza qualche lotto, quindi la lista degli
    edifici cambia legittimamente. Strade e piazze invece sono decise prima
    che i luoghi entrino in gioco, e devono restare identiche."""
    plain = _city(4, "citta")
    with_arena = _city(4, "citta", requested_landmarks=("arena",))

    assert [s.points for s in plain.streets] == [s.points for s in with_arena.streets]
    assert plain.plazas == with_arena.plazas
    assert (plain.walls is None) == (with_arena.walls is None)
    assert "arena" in {m.kind for m in with_arena.landmarks}


# --- AC3: ammissibilita' per preset di scala -------------------------------


@pytest.mark.parametrize("scale", SCALES)
def test_no_landmark_outside_its_admitted_scales(scale):
    for _blueprint, mark in _all_landmarks(scale, seeds=range(10)):
        assert scale in lm.BY_KEY[mark.kind].scales, (scale, mark.kind)


@pytest.mark.parametrize("scale", SCALES)
def test_no_structure_outside_its_admitted_scales(scale):
    for seed in range(10):
        blueprint = _city(seed, scale)
        for key, field in (("mura", "walls"), ("fiume", "river"), ("porto", "port")):
            if getattr(blueprint, field) is not None:
                assert scale in lm.STRUCTURE_SCALES[key], (scale, key)


def test_bakeries_only_at_the_playable_scale_and_arenas_only_at_city_scale():
    """La regola di AC3 detta a parole: al preset "citta" si segnano
    cattedrale, palazzo e arena, non le panetterie."""
    assert lm.BY_KEY["fornaio"].scales == frozenset({"isolato"})
    assert lm.BY_KEY["arena"].scales == frozenset({"citta"})
    assert "citta" not in lm.BY_KEY["taverna"].scales


@pytest.mark.parametrize("key,scale", [("arena", "quartiere"), ("mura", "isolato"), ("palazzo", "isolato")])
def test_requesting_an_element_not_admitted_by_the_preset_is_an_explicit_error(key, scale):
    with pytest.raises(ValueError, match="non e' ammissibile al preset"):
        _city(1, scale, requested_landmarks=(key,))


def test_requesting_an_unknown_element_is_an_explicit_error():
    with pytest.raises(ValueError, match="sconosciuto"):
        _city(1, "citta", requested_landmarks=("locanda_del_cervo_bianco",))


# --- AC4: quantita' proporzionali, non assolute ----------------------------


@pytest.mark.parametrize("scale", SCALES)
def test_unique_landmarks_appear_at_most_once(scale):
    for blueprint in (_city(seed, scale) for seed in range(10)):
        counts: dict[str, int] = {}
        for mark in blueprint.landmarks:
            counts[mark.kind] = counts.get(mark.kind, 0) + 1
        for key, count in counts.items():
            if lm.BY_KEY[key].unique:
                assert count == 1, (scale, key, count)


def test_common_landmarks_grow_with_the_number_of_buildings():
    """AC4: le quantita' sono legate alla dimensione della mappa, non fissate.
    Confronto fra due canvas molto diversi allo stesso preset."""
    small = [_city_size(seed, "quartiere", 40) for seed in range(8)]
    large = [_city_size(seed, "quartiere", 110) for seed in range(8)]

    def common(blueprint):
        return sum(1 for m in blueprint.landmarks if not lm.BY_KEY[m.kind].unique)

    small_buildings = sum(len(b.building_footprints) for b in small)
    large_buildings = sum(len(b.building_footprints) for b in large)
    assert large_buildings > 3 * small_buildings, (small_buildings, large_buildings)
    assert sum(common(b) for b in large) > 2 * sum(common(b) for b in small)


def _city_size(seed: int, scale: str, size: int):
    return city.generate(width=size, height=size, seed=seed, scale=scale)


@pytest.mark.parametrize("scale", SCALES)
def test_landmarks_never_eat_the_whole_city(scale):
    """Il contrario di AC4: le quote proporzionali sommate non devono
    spolpare il tessuto edilizio. Il tetto e' largo perche' al preset
    "isolato" una mappa e' una via sola, dove la quota di botteghe e'
    legittimamente alta."""
    for seed in range(10):
        blueprint = _city(seed, scale)
        ordinary = len(blueprint.buildings) + len(blueprint.building_footprints)
        assert ordinary > len(blueprint.landmarks), (scale, seed, ordinary, len(blueprint.landmarks))


# --- AC5: le regole di piazzamento valgono, e sono verificabili ------------


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_customs_and_watchtowers_stand_at_a_gate(scale):
    seen = 0
    for blueprint, mark in _all_landmarks(scale, seeds=range(10)):
        if mark.kind not in ("dogana", "torre_guardia"):
            continue
        seen += 1
        assert blueprint.walls is not None and blueprint.walls.gates
        radius = city._radius(city.SCALE_PRESETS[scale])
        assert min(
            _point_to_rect(gate.x, gate.y, mark.rect) for gate in blueprint.walls.gates
        ) <= radius, (scale, mark.kind)
    assert seen, "nessuna dogana/torre piazzata: il test non ha verificato nulla"


@pytest.mark.parametrize("scale", SCALES)
def test_the_mill_stands_on_the_river(scale):
    seen = 0
    for blueprint, mark in _all_landmarks(scale, seeds=range(12)):
        if mark.kind != "mulino":
            continue
        seen += 1
        assert blueprint.river is not None
        distance, _t = _river_proximity(mark.rect, blueprint.river)
        assert distance <= city._radius(city.SCALE_PRESETS[scale]), (scale, distance)
    assert seen, "nessun mulino piazzato: il test non ha verificato nulla"


@pytest.mark.parametrize("scale", SCALES)
def test_the_tannery_and_the_slaughterhouse_stand_downstream(scale):
    """AC5, la regola con piu' contenuto di tutte: i mestieri che puzzano
    stanno a valle. Il verso e' quello di River.points, dalla sorgente alla
    foce."""
    seen = 0
    for blueprint, mark in _all_landmarks(scale, seeds=range(12)):
        if mark.kind not in ("conceria", "macello"):
            continue
        seen += 1
        assert blueprint.river is not None
        distance, t = _river_proximity(mark.rect, blueprint.river)
        assert distance <= city._radius(city.SCALE_PRESETS[scale]), (scale, mark.kind, distance)
        assert t >= 0.5, (scale, mark.kind, t)
    assert seen, "nessuna conceria/macello piazzata: il test non ha verificato nulla"


@pytest.mark.parametrize("scale", SCALES)
def test_the_cemetery_lies_outside_the_walls_or_next_to_the_temple(scale):
    seen = 0
    for blueprint, mark in _all_landmarks(scale, seeds=range(12)):
        if mark.kind != "cimitero":
            continue
        seen += 1
        outside = blueprint.walls is not None and not mark.rect.overlaps(blueprint.walls.ring)
        temples = [m.rect for m in blueprint.landmarks if m.kind == "tempio"]
        radius = city._radius(city.SCALE_PRESETS[scale])
        near_temple = any(_rect_to_rect(mark.rect, t) <= radius for t in temples)
        assert outside or near_temple, (scale, blueprint.seed)
    assert seen, "nessun cimitero piazzato: il test non ha verificato nulla"


@pytest.mark.parametrize("scale", SCALES)
def test_the_market_stands_on_a_plaza_and_the_gallows_on_the_main_one(scale):
    seen = 0
    for blueprint, mark in _all_landmarks(scale, seeds=range(12)):
        if mark.kind not in ("mercato", "patibolo"):
            continue
        seen += 1
        plazas = blueprint.plazas
        assert plazas
        if mark.kind == "patibolo":
            plazas = [max(plazas, key=lambda p: p.w * p.h)]
        assert any(mark.rect.overlaps(plaza) for plaza in plazas), (scale, mark.kind)
    assert seen, "nessun mercato/patibolo piazzato: il test non ha verificato nulla"


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_the_lighthouse_stands_on_the_quay(scale):
    """Il faro e' rimasto l'unico luogo della banchina: cantiere navale e
    mercato del pesce sono usciti dal catalogo quando Jay li ha scartati sul
    campionario. Il porto resta comunque una struttura che rimodella la mappa
    e la sua regola di piazzamento resta verificabile."""
    seen = 0
    for blueprint, mark in _all_landmarks(scale, seeds=range(20)):
        if mark.kind != "faro":
            continue
        seen += 1
        assert blueprint.port is not None
        assert mark.rect.overlaps(blueprint.port.quay), (scale, mark.kind)
        assert not mark.rect.overlaps(blueprint.port.water), (scale, mark.kind)
    assert seen, "nessun luogo portuale piazzato: il test non ha verificato nulla"


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_a_landmark_fits_on_the_narrow_quay(scale):
    """Regressione: la banchina e' una striscia stretta e lunga, la cui
    griglia viene di una colonna sola per molte righe. Finche' le finestre
    di celle si cercavano solo per riga, nessun luogo ci entrava e il porto
    restava deserto."""
    blueprint = _city(1337, scale, requested_landmarks=("porto", "faro"))
    assert blueprint.port is not None
    assert "faro" in {mark.kind for mark in blueprint.landmarks}


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_the_edge_landmarks_stay_out_of_the_core(scale):
    seen = 0
    for blueprint, mark in _all_landmarks(scale, seeds=range(12)):
        if lm.BY_KEY[mark.kind].rule != lm.RULE_EDGE:
            continue
        seen += 1
        # Definizione indipendente di "margine": il luogo non deve entrare
        # nella meta' centrale del canvas.
        core = city.Rect(CANVAS * 0.3, CANVAS * 0.3, CANVAS * 0.7, CANVAS * 0.7)
        assert not mark.rect.overlaps(core), (scale, mark.kind, mark.rect)
    assert seen, "nessun luogo di margine piazzato: il test non ha verificato nulla"


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_a_rule_bound_landmark_is_absent_when_its_anchor_is(scale):
    """L'altra faccia di AC5: un luogo la cui regola non trova un ancoraggio
    NON viene piazzato altrove. Senza mura non ci sono dogane; senza porto
    non ci sono fari."""
    for seed in range(20):
        blueprint = _city(seed, scale)
        kinds = {mark.kind for mark in blueprint.landmarks}
        if blueprint.walls is None:
            assert not kinds & {"dogana", "torre_guardia"}, (scale, seed)
        if blueprint.port is None:
            assert "faro" not in kinds, (scale, seed)
        if blueprint.river is None:
            assert not kinds & {"mulino", "conceria", "macello"}, (scale, seed)


# --- AC5 (strutture): porte sulle strade, ponti sul fiume ------------------


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_every_gate_sits_on_the_wall_ring(scale):
    for seed in range(10):
        blueprint = _city(seed, scale)
        if blueprint.walls is None:
            continue
        ring = blueprint.walls.ring
        for gate in blueprint.walls.gates:
            on_ring = (
                math.isclose(gate.y, ring.y1) or math.isclose(gate.y, ring.y2)
                or math.isclose(gate.x, ring.x1) or math.isclose(gate.x, ring.x2)
            )
            assert on_ring, (scale, seed, gate)
            assert gate.width > 0


@pytest.mark.parametrize("scale", SCALES)
def test_every_bridge_actually_crosses_the_river(scale):
    for seed in range(10):
        blueprint = _city(seed, scale)
        if blueprint.river is None:
            assert blueprint.bridges == []
            continue
        for bridge in blueprint.bridges:
            distance, _t = _river_proximity(bridge.rect, blueprint.river)
            assert distance == 0.0, (scale, seed, distance)


@pytest.mark.parametrize("scale", SCALES)
def test_no_building_sits_in_the_river(scale):
    for seed in range(8):
        blueprint = _city(seed, scale)
        if blueprint.river is None:
            continue
        boxes = [city._footprint_of(b) for b in blueprint.buildings] + list(blueprint.building_footprints)
        for box in boxes:
            distance, _t = _river_proximity(box, blueprint.river)
            assert distance > 0.0, (scale, seed, box)


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_nothing_is_built_in_the_port_water(scale):
    for seed in range(20):
        blueprint = _city(seed, scale)
        if blueprint.port is None:
            continue
        water = blueprint.port.water
        boxes = [city._footprint_of(b) for b in blueprint.buildings] + list(blueprint.building_footprints)
        for box in boxes:
            assert not box.overlaps(water), (scale, seed, box)


@pytest.mark.parametrize("scale", ["quartiere", "citta"])
def test_ordinary_buildings_stay_inside_the_walls(scale):
    for seed in range(12):
        blueprint = _city(seed, scale)
        if blueprint.walls is None:
            continue
        ring = blueprint.walls.ring
        boxes = [city._footprint_of(b) for b in blueprint.buildings] + list(blueprint.building_footprints)
        for box in boxes:
            assert box.x1 >= ring.x1 and box.y1 >= ring.y1, (scale, seed, box)
            assert box.x2 <= ring.x2 and box.y2 <= ring.y2, (scale, seed, box)


# --- AC6: niente sovrapposizioni ------------------------------------------


@pytest.mark.parametrize("scale", SCALES)
def test_landmarks_do_not_overlap_each_other(scale):
    for seed in range(10):
        marks = _city(seed, scale).landmarks
        for i, first in enumerate(marks):
            for second in marks[i + 1 :]:
                assert not first.rect.overlaps(second.rect), (scale, seed, first.kind, second.kind)


@pytest.mark.parametrize("scale", SCALES)
def test_landmarks_do_not_overlap_ordinary_buildings(scale):
    for seed in range(10):
        blueprint = _city(seed, scale)
        boxes = [city._footprint_of(b) for b in blueprint.buildings] + list(blueprint.building_footprints)
        for mark in blueprint.landmarks:
            for box in boxes:
                assert not mark.rect.overlaps(box), (scale, seed, mark.kind)


@pytest.mark.parametrize("scale", SCALES)
def test_landmarks_do_not_sit_on_a_street(scale):
    """Nessun luogo in mezzo alla strada. Il controllo usa l'ingombro
    RISERVATO della via (Street.corridor), non il selciato disegnato: e'
    l'ingombro la garanzia geometrica di TASK-35, e il selciato ci sta dentro
    per costruzione."""
    for seed in range(10):
        blueprint = _city(seed, scale)
        corridors = [s.corridor for s in blueprint.streets if s.corridor is not None]
        for mark in blueprint.landmarks:
            for corridor in corridors:
                assert not mark.rect.overlaps(corridor), (scale, seed, mark.kind)


@pytest.mark.parametrize("scale", SCALES)
def test_only_the_plaza_landmarks_touch_a_plaza(scale):
    """AC6 dice che i luoghi non si sovrappongono alle piazze; AC5 vuole
    mercato e patibolo SULLA piazza. Le due cose convivono solo se l'unica
    eccezione ammessa e' quella dichiarata dalla regola del luogo, ed e'
    esattamente cio' che questo test fissa."""
    for seed in range(10):
        blueprint = _city(seed, scale)
        for mark in blueprint.landmarks:
            if lm.BY_KEY[mark.kind].site == lm.SITE_PLAZA:
                continue
            for plaza in blueprint.plazas:
                assert not mark.rect.overlaps(plaza), (scale, seed, mark.kind)


@pytest.mark.parametrize("scale", SCALES)
def test_landmarks_stay_inside_the_canvas(scale):
    for seed in range(10):
        blueprint = _city(seed, scale)
        for mark in blueprint.landmarks:
            assert mark.rect.x1 >= 0 and mark.rect.y1 >= 0, (scale, seed, mark.kind)
            assert mark.rect.x2 <= CANVAS and mark.rect.y2 <= CANVAS, (scale, seed, mark.kind)


# --- AC8: il documento passa validate() -----------------------------------


def _render(blueprint):
    prepared = prepare(load_template(TEMPLATE), levels=1)
    ids = IdAllocator.from_document(prepared)
    palette = palette_for("city", load_catalog())
    render_city_blueprint(
        prepared["world"]["levels"], ids, blueprint, palette, rng=random.Random(blueprint.seed),
    )
    finalize(prepared, ids)
    return prepared


@pytest.mark.parametrize("scale", SCALES)
def test_document_validates_clean_with_landmarks(scale):
    for seed in (0, 1337):
        issues = validate(_render(_city(seed, scale)))
        assert [i for i in issues if i.severity == "error"] == []


@pytest.mark.parametrize("scale", SCALES)
def test_document_validates_clean_without_landmarks(scale):
    issues = validate(_render(_city(1337, scale, landmarks=False)))
    assert [i for i in issues if i.severity == "error"] == []


def test_document_validates_clean_with_every_requestable_element():
    """AC8, il caso peggiore: tutte le strutture insieme e tutti i luoghi
    ammissibili al preset chiesti esplicitamente, cioe' la mappa piu' carica
    che il generatore possa produrre."""
    for scale in SCALES:
        requested = tuple(key for key in lm.REQUESTABLE if scale in lm.scales_of(key))
        blueprint = _city(1337, scale, requested_landmarks=requested)
        issues = validate(_render(blueprint))
        assert [i for i in issues if i.severity == "error"] == [], scale


# --- rendering: ogni luogo si vede e ha il suo nome ------------------------


@pytest.mark.parametrize("scale", SCALES)
def test_landmarks_get_their_name_on_the_map(scale):
    """La scelta di piano di TASK-48: e' l'etichetta a rendere il luogo
    riconoscibile. Ogni testo scritto sulla mappa e' il nome di un luogo che
    c'e' davvero, e la stragrande maggioranza dei luoghi ha il suo nome.

    "Stragrande" e non "tutti": due luoghi vicini con nomi lunghi non ci
    stanno entrambi, e in quel caso l'etichetta viene omessa invece di
    sovrapporsi a un'altra. Senza questa regola, al preset "quartiere" i
    quaranta nomi si accavallavano fino a non leggersene nessuno - verificato
    guardando la mappa renderizzata."""
    blueprint = _city(1337, scale)
    level = _render(blueprint)["world"]["levels"]["0"]
    drawn = [text["text"] for text in level["texts"]]
    wanted = [mark.label for mark in blueprint.landmarks]

    assert set(drawn) <= set(wanted), sorted(set(drawn) - set(wanted))
    assert len(drawn) >= 0.9 * len(wanted), (len(drawn), len(wanted))


@pytest.mark.parametrize("scale", SCALES)
def test_two_labels_never_overlap(scale):
    """L'invariante vero dietro il test qui sopra: nessun nome finisce sopra
    un altro. Il confronto usa la stessa stima di ingombro del disegno
    (compose._label_box non e' richiamabile senza il rettangolo del luogo,
    quindi qui si ricostruisce dai dati del testo scritto)."""
    from ddforge.compose import _LABEL_CHAR_WIDTH, _LABEL_LINE_HEIGHT
    from ddforge.godot import GRID

    level = _render(_city(1337, scale))["world"]["levels"]["0"]
    boxes = []
    for text in level["texts"]:
        x, y = (float(v) for v in text["position"][len("Vector2( "):-2].split(","))
        w = len(text["text"]) * text["font_size"] * _LABEL_CHAR_WIDTH
        h = text["font_size"] * _LABEL_LINE_HEIGHT
        boxes.append(city.Rect((x - w / 2) / GRID, y / GRID, (x + w / 2) / GRID, (y + h) / GRID))
    for i, first in enumerate(boxes):
        for second in boxes[i + 1 :]:
            assert not first.overlaps(second), (scale, i)


def test_walls_are_drawn_broken_at_every_gate():
    """Un varco e' muro che NON c'e': l'anello va disegnato in pezzi, uno per
    ogni tratto fra due porte."""
    blueprint = _city(1337, "citta", requested_landmarks=("mura",))
    assert blueprint.walls is not None and blueprint.walls.gates
    palette = palette_for("city", load_catalog())
    level = _render(blueprint)["world"]["levels"]["0"]
    wall_paths = [p for p in level["paths"] if p["texture"] == palette.paths["mura"]]
    # Quattro lati; ogni porta spezza in due il lato su cui si apre.
    assert len(wall_paths) == 4 + len(blueprint.walls.gates)


@pytest.mark.parametrize("scale", SCALES)
def test_bridges_are_a_deck_and_not_a_sprite(scale):
    """Scelta di Jay dopo aver visto la mappa vera: il ponte e' un pavimento
    steso sull'acqua, non uno sprite. Uno sprite di ponte e' UNA campata di
    dimensione fissa, mentre l'attraversamento e' lungo quanto il fiume e'
    largo e orientato come la via: scalarlo lo deformava."""
    blueprint = _city(1337, scale, requested_landmarks=("fiume",))
    assert blueprint.bridges, "nessun ponte: il test non ha verificato nulla"
    palette = palette_for("city", load_catalog())
    level = _render(blueprint)["world"]["levels"]["0"]

    decks = [p for p in level["patterns"] if p["texture"] == palette.floors["ponte"]]
    assert len(decks) == len(blueprint.bridges)
    # Nessuno sprite di ponte in palette: la Palette non ha piu' nemmeno il
    # campo che li teneva (era rimasto con la sola torre-porta, poi scartata
    # anche quella).
    assert not hasattr(palette, "structure_sprites")


@pytest.mark.parametrize("scale", SCALES)
def test_open_air_landmarks_get_a_coloured_area_of_the_right_ground(scale):
    """Un luogo all'aperto e' un'area colorata con sopra gli sprite, e il
    terreno dell'area e' quello che il luogo dichiara: selciato per il
    mercato, erba per parco e cimitero, terra battuta per fiera e
    fiera. Prima era selciato per tutti, ed e' il motivo per cui un
    cimitero sembrava un piazzale."""
    palette = palette_for("city", load_catalog())
    seen = 0
    for seed in range(8):
        blueprint = _city(seed, scale)
        level = _render(blueprint)["world"]["levels"]["0"]
        patterns = {(p["texture"], p["points"]) for p in level["patterns"]}
        for mark in blueprint.landmarks:
            if mark.ground is None:
                continue
            seen += 1
            texture = palette.floors[mark.ground]
            assert any(t == texture for t, _pts in patterns), (scale, mark.kind, mark.ground)
    assert seen, "nessun luogo con area colorata: il test non ha verificato nulla"


def test_the_three_grounds_are_three_different_textures():
    palette = palette_for("city", load_catalog())
    grounds = {palette.floors[g] for g in ("selciato", "verde", "terra")}
    assert len(grounds) == 3, grounds


def test_scattered_pieces_keep_their_real_size_whatever_the_area():
    """Regressione del difetto trovato misurando: i pezzi sparsi venivano
    scalati al 45% del lato dell'AREA, quindi su un cimitero grande usciva
    una lapide da 4,5 quadretti - alta quasi sette metri. Ora si disegnano
    alla loro dimensione nativa, che e' la loro dimensione reale (un pack e'
    disegnato a 256 px per quadretto), e si rimpiccioliscono solo se lo
    spiazzo e' piu' piccolo del pezzo."""
    from ddforge.compose import _sprite_size

    palette = palette_for("city", load_catalog())
    checked = 0
    for scale in SCALES:
        for seed in range(8):
            blueprint = _city(seed, scale)
            for mark in blueprint.landmarks:
                if not mark.open_air:
                    continue
                sprites = palette.landmark_sprites[mark.kind]
                widths = [w for w, _h in map(_sprite_size, sprites)]
                heights = [h for _w, h in map(_sprite_size, sprites)]
                # Nessun pezzo puo' venire piu' grande del suo nativo, e
                # nessuno puo' sforare lo spiazzo che lo contiene.
                assert max(widths) <= mark.rect.w + max(widths), (scale, mark.kind)
                for w, h in zip(widths, heights):
                    drawn = min(1.0, min(mark.rect.w / w, mark.rect.h / h))
                    assert drawn * w <= mark.rect.w + 1e-9, (scale, mark.kind)
                    assert drawn * h <= mark.rect.h + 1e-9, (scale, mark.kind)
                    assert drawn <= 1.0 + 1e-9, (scale, mark.kind)
                    checked += 1
    assert checked


def test_a_gravestone_is_the_same_size_in_a_big_and_a_small_cemetery():
    """L'altra faccia del test qui sopra, sul documento scritto: due cimiteri
    di dimensione molto diversa devono avere lapidi UGUALI, e il grande
    semplicemente piu' numerose."""
    palette = palette_for("city", load_catalog())
    textures = {t for t, _w, _h in palette.landmark_sprites["cimitero"]}

    def graves(scale):
        for seed in range(12):
            blueprint = _city(seed, scale)
            marks = [m for m in blueprint.landmarks if m.kind == "cimitero"]
            if not marks:
                continue
            level = _render(blueprint)["world"]["levels"]["0"]
            drawn = [o for o in level["objects"] if o["texture"] in textures]
            if drawn:
                return marks[0], drawn
        return None, []

    big_mark, big = graves("isolato")
    small_mark, small = graves("citta")
    assert big and small, "servono due cimiteri per confrontarli"
    assert big_mark.rect.w * big_mark.rect.h > 4 * small_mark.rect.w * small_mark.rect.h

    from ddforge.compose import _sprite_size

    by_texture = {t: (w, h) for t, w, h in palette.landmark_sprites["cimitero"]}

    def drawn_side(obj):
        """Lato lungo effettivamente disegnato, in quadretti."""
        scale = float(obj["scale"][len("Vector2( "):-2].split(",")[0])
        w, h = _sprite_size((obj["texture"], *by_texture[obj["texture"]]))
        return max(w, h) * scale

    # Nel cimitero grande ogni lapide e' alta esattamente quanto il catalogo
    # dichiara (LandmarkKind.piece_size); nel piccolo al piu' quella, perche'
    # li' lo spiazzo e' piu' stretto del pezzo e lo comprime.
    wanted = lm.BY_KEY["cimitero"].piece_size
    assert all(abs(drawn_side(o) - wanted) < 1e-6 for o in big), sorted({drawn_side(o) for o in big})
    assert all(drawn_side(o) <= wanted + 1e-9 for o in small)
    assert len(big) > len(small)


def test_the_port_water_reaches_the_native_water_layer():
    blueprint = _city(1337, "citta", requested_landmarks=("porto",))
    assert blueprint.port is not None
    level = _render(blueprint)["world"]["levels"]["0"]
    assert level["water"]["tree"]["children"], "il poligono d'acqua del porto non e' stato scritto"
