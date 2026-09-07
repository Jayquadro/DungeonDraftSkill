"""Regressioni del gate umano M4 (TASK-30).

Jay ha aperto generated/building_m4.dungeondraft_map (taverna, seed 1337) in
Dungeondraft e il risultato non era utilizzabile. Ogni test qui riproduce uno
dei difetti segnalati PRIMA della correzione, come richiede il criterio di
accettazione #5 del task.

Difetti riportati, testuali:
1. "Ho due livelli entrambi chiamati Ground"
2. "in uno c'e una stanza piena di botti e camini, e una piena di botti"
3. "Non si capisce la divisione delle stanze"
4. "ne quale sarebbe il vano scale"
5. "Il tetto e visibile in un layer che comunque si chiama Ground"
6. "Non ci sono arredi se non barili e camini"

I difetti 1 e 5 sono lo stesso (le etichette dei piani non vengono mai
scritte); 2, 3 e 6 sono lo stesso (l'arredo tappezza la stanza e ripete un
solo oggetto); 4 e indipendente (il vano scale finisce fuori dall'edificio).

Round 2 (difetti sotto la riga ROUND 2 piu in basso), testuali:
7.  "i due camini sono girati e parzialmente sovrapposti"
8.  "alcuni sprite, come i camini, e necessario che siano compenetrati coi
    muri. Ugualmente le madie"
9.  "ci sono due botti sovrapposte nella stanza a destra in alto"
10. "l'armadio a sinistra e girato"
11. "le stanze che hai fatto sono molto molto grandi. Considera che un
    quadretto dovrebbe essere 1.5m reali"
12. "nella magione al piano terra gli sprite sono tutti sovrapposti"
13. "molti degli sprite guardano il muro"

7, 10 e 13 sono lo stesso difetto (la rotazione non dipende dal lato);
7, 9 e 12 sono lo stesso (nessun controllo di sovrapposizione); 8 e 11 sono
indipendenti.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from ddforge.generators import building

TEMPLATE = "templates/blank_80x80.dungeondraft_map"
SEED = 1337


def _blueprint(building_type="tavern", **kwargs):
    """L'edificio alla sua taglia di default, che e quella che Jay apre: a
    1.5 m per quadretto una taverna sta in 18x14 quadretti, non nei 40x40
    generici del round 1 (che valevano 60x60 m)."""
    width, height = building.default_size(building_type)
    return building.generate(
        width=width, height=height, seed=SEED, building_type=building_type, **kwargs
    )


@pytest.fixture(scope="module")
def rendered():
    """L'edificio come lo produce DAVVERO il CLI: i difetti del gate vanno
    verificati sul file che Jay apre, non su una sua imitazione nel test
    (la label dei piani, per esempio, si perdeva proprio nel wiring)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "tavern.dungeondraft_map"
        result = subprocess.run(
            [
                sys.executable, "-m", "ddforge.cli", "generate", "building",
                "--template", TEMPLATE, "--out", str(out), "--seed", str(SEED),
                "--building-type", "tavern", "--furnish", "medium", "--lights",
            ],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return _blueprint(), json.loads(out.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Difetti 1 e 5: i piani non hanno un nome proprio
# ---------------------------------------------------------------------------

def test_each_floor_gets_its_own_label(rendered):
    """'Ho due livelli entrambi chiamati Ground'. template.prepare accetta
    gia `labels`, ma nessuno gliele passava: ogni piano ereditava la label
    del template."""
    _, prepared = rendered
    labels = [level["label"] for _, level in sorted(prepared["world"]["levels"].items())]

    assert len(labels) == 2
    assert len(set(labels)) == len(labels), f"piani con la stessa etichetta: {labels}"
    assert all(label.strip() for label in labels), f"piani senza etichetta: {labels}"


def test_the_floor_carrying_the_roof_is_named_as_the_top_floor(rendered):
    """'Il tetto e visibile in un layer che comunque si chiama Ground': il
    piano che porta il tetto dev'essere riconoscibile come l'ultimo."""
    _, prepared = rendered
    levels = sorted(prepared["world"]["levels"].items(), key=lambda kv: int(kv[0]))
    with_roof = [label for _, level in levels for label in [level["label"]] if level["roofs"]["roofs"]]

    assert with_roof, "nessun piano ha il tetto"
    assert with_roof[0] != levels[0][1]["label"], (
        "il piano col tetto ha la stessa etichetta del piano terra"
    )


# ---------------------------------------------------------------------------
# Difetto 4: il vano scale
# ---------------------------------------------------------------------------

def test_stairwell_and_rooms_tile_the_perimeter_without_dead_space():
    """'ne quale sarebbe il vano scale'. Il vano scale cadeva FUORI dal
    perimetro portante, adiacente solo per l'angolo, e fra lui e le stanze
    restava una fascia di spazio morto dentro i muri.

    Non basta chiedere che il vano scale stia dentro il perimetro: dato che
    il perimetro e il bounding box di cio che si disegna, quella condizione
    e vera per costruzione. La proprieta che manca davvero e la tassellatura:
    su ogni piano, vano scale e stanze devono coprire il perimetro senza
    lasciare buchi. Un buco dentro i muri portanti e esattamente cio che
    rende illeggibile la pianta."""
    from ddforge.compose import _building_footprint

    blueprint = _blueprint()
    stairs = blueprint.stairs_rect
    footprint = _building_footprint(blueprint)

    assert stairs is not None
    assert footprint.x1 <= stairs.x1 and stairs.x2 <= footprint.x2, f"vano scale fuori dai muri in x: {stairs}"
    assert footprint.y1 <= stairs.y1 and stairs.y2 <= footprint.y2, f"vano scale fuori dai muri in y: {stairs}"

    covered = footprint.w * footprint.h
    floors = {room.level for room in blueprint.rooms}
    for floor in sorted(floors):
        area = stairs.w * stairs.h + sum(
            room.rect.w * room.rect.h for room in blueprint.rooms if room.level == floor
        )
        assert area == covered, (
            f"piano {floor}: stanze e vano scale coprono {area} quadretti "
            f"su {covered} del perimetro (spazio morto dentro i muri)"
        )


def test_stairwell_is_reachable_from_a_room_on_every_floor():
    """Un vano scale senza porta non e un vano scale: e un ripostiglio
    murato. Su ogni piano deve esserci almeno una stanza adiacente al vano
    scale che gli apra una porta."""
    blueprint = _blueprint()
    stairs = blueprint.stairs_rect
    floors = {room.level for room in blueprint.rooms}

    for floor in sorted(floors):
        touching = [
            room for room in blueprint.rooms
            if room.level == floor and (
                (room.rect.x2 == stairs.x1 or room.rect.x1 == stairs.x2)
                and min(room.rect.y2, stairs.y2) > max(room.rect.y1, stairs.y1)
                or (room.rect.y2 == stairs.y1 or room.rect.y1 == stairs.y2)
                and min(room.rect.x2, stairs.x2) > max(room.rect.x1, stairs.x1)
            )
        ]
        assert touching, f"piano {floor}: nessuna stanza tocca il vano scale"
        assert any(room.doors for room in touching), (
            f"piano {floor}: il vano scale non ha nessuna porta che lo colleghi"
        )


def test_stairwell_contains_a_visible_stairs_object(rendered):
    """Un vano scale vuoto non si legge come una scala. Il catalogo ha
    stairs_round_04/stairs_round_08 e non venivano mai usati."""
    blueprint, prepared = rendered
    stairs = blueprint.stairs_rect

    for level_key, level in prepared["world"]["levels"].items():
        inside = [
            obj for obj in level["objects"]
            if "stairs" in obj["texture"]
        ]
        assert inside, f"piano {level_key}: nessun oggetto scala nel vano scale"


# ---------------------------------------------------------------------------
# Difetti 2, 3 e 6: l'arredo tappezza la stanza e ripete un solo oggetto
# ---------------------------------------------------------------------------

def _objects_per_room(blueprint, prepared):
    """Conta gli oggetti che cadono dentro ciascuna stanza."""
    counts = {}
    for room_index, room in enumerate(blueprint.rooms):
        level = prepared["world"]["levels"][str(room.level)]
        n = 0
        for obj in level["objects"]:
            x, y = (float(v) / 256 for v in obj["position"][len("Vector2( "):-2].split(","))
            if room.rect.x1 <= x <= room.rect.x2 and room.rect.y1 <= y <= room.rect.y2:
                n += 1
        counts[room_index] = n
    return counts


def test_no_room_is_carpeted_with_furniture(rendered):
    """'una stanza piena di botti': la densita per-quadretto era applicata
    all'intera area senza tetto massimo, quindi 65 oggetti nella sala comune
    e 77 letti in una camera. Un arredo deve suggerire la funzione della
    stanza, non ricoprirne il pavimento."""
    blueprint, prepared = rendered
    counts = _objects_per_room(blueprint, prepared)

    # Soglia: un oggetto ogni 15 quadretti, con un minimo di 16 per le stanze
    # piccole. E larga di proposito — non deve fissare un numero esatto, ma
    # separare l'arredo dalla tappezzeria. I conteggi del round 1 la superano
    # tutti di parecchio: sala comune 65 su 36 ammessi, camera 77 su 42,
    # cucina 37 su 20, retro 28 su 16.
    too_full = {
        i: n for i, n in counts.items()
        if n > max(16, (blueprint.rooms[i].rect.w * blueprint.rooms[i].rect.h) // 15)
    }
    assert not too_full, (
        "stanze tappezzate (indice -> numero di oggetti): "
        + ", ".join(f"{i} ({blueprint.rooms[i].kind}) -> {n}" for i, n in too_full.items())
    )


def test_every_kind_of_room_gets_more_than_one_kind_of_object(rendered):
    """'Non ci sono arredi se non barili e camini': la stanza 'retro' di una
    taverna riceveva SOLO barili, perche _KIND_ACCENT_HINTS le mappa
    ('crate', 'barrel') ma la palette tavern non ha 'crate'.

    La proprieta e per KIND, non per singola stanza: una cameretta da 4x10 m
    con dentro il solo letto e arredata bene, il difetto e che TUTTE le
    camere dell'edificio abbiano solo quello."""
    blueprint, prepared = rendered

    by_kind: dict[str, set] = {}
    for room in blueprint.rooms:
        level = prepared["world"]["levels"][str(room.level)]
        for obj, x, y in _objects_of(level):
            if room.rect.x1 <= x <= room.rect.x2 and room.rect.y1 <= y <= room.rect.y2:
                by_kind.setdefault(room.kind, set()).add(obj["texture"])

    for kind, textures in sorted(by_kind.items()):
        assert len(textures) > 1, (
            f"stanze di tipo {kind}: arredate con un solo oggetto ripetuto ({textures})"
        )


def test_furniture_against_walls_is_aligned_with_them(rendered):
    """'Non si capisce la divisione delle stanze'. Oltre alla quantita, la
    disposizione: oggetti a rotazione casuale in mezzo alla stanza nascondono
    i muri invece di sottolinearli. Un pezzo addossato a un muro dev'essere
    parallelo al muro, non storto."""
    import math

    blueprint, prepared = rendered
    tolerance = 1e-6
    right_angles = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi]

    skewed = []
    for room in blueprint.rooms:
        level = prepared["world"]["levels"][str(room.level)]
        for obj in level["objects"]:
            x, y = (float(v) / 256 for v in obj["position"][len("Vector2( "):-2].split(","))
            if not (room.rect.x1 <= x <= room.rect.x2 and room.rect.y1 <= y <= room.rect.y2):
                continue
            near_wall = (
                min(x - room.rect.x1, room.rect.x2 - x) <= 1.5
                or min(y - room.rect.y1, room.rect.y2 - y) <= 1.5
            )
            if near_wall and not any(abs(obj["rotation"] - a) < tolerance for a in right_angles):
                skewed.append((room.kind, round(obj["rotation"], 3)))

    assert not skewed, f"oggetti addossati ai muri ma storti: {skewed[:10]}"


# ===========================================================================
# ROUND 2 — difetti 7-13, segnalati da Jay sul file corretto del round 1.
#
# Per i difetti 7 e 8 ho una misura diretta e non un'impressione: Jay ha
# corretto i due camini a mano dentro generated/building_m4.dungeondraft_map
# e le sue posizioni sono il riferimento. Camino sul muro BASSO della cucina
# (5,1)-(25,21): lui lo mette a y=20.5 (mezzo quadretto DENTRO il muro, che
# sta a y=21) con rotazione +-pi. Io lo mettevo a y=20.0 con rotazione 0.
# ===========================================================================

import math

# Un quadretto di Dungeondraft vale 1.5 m (Jay, gate round 2). Tutte le
# soglie "realistiche" di questi test partono da qui.
TILE_METERS = 1.5


def _objects_of(level):
    for obj in level["objects"]:
        x, y = (float(v) / 256 for v in obj["position"][len("Vector2( "):-2].split(","))
        yield obj, x, y


def _nearest_side(rect, x, y):
    """(indice_lato, distanza) del lato di rect piu vicino al punto, con gli
    indici di compose: 0=top, 1=right, 2=bottom, 3=left."""
    distances = [y - rect.y1, rect.x2 - x, rect.y2 - y, x - rect.x1]
    side = min(range(4), key=lambda i: distances[i])
    return side, distances[side]


def test_a_wall_slot_puts_the_piece_against_the_wall_facing_the_room():
    """Difetti 7, 8, 10 e 13: 'i camini sono girati', 'devono essere
    compenetrati coi muri', 'l'armadio a sinistra e girato', 'molti degli
    sprite guardano il muro'.

    Tutti e quattro nascono da _wall_slot, e qui c'e la misura esatta invece
    di un'euristica sul file: Jay ha raddrizzato a mano i camini della
    cucina, il cui muro basso sta a y=21, portandoli da (y=20.0, rot=0) a
    (y=20.5, rot=+-pi). Quindi offset mezzo quadretto — cosi uno sprite 1x1
    tocca il muro e uno 2x2 ci entra per meta — e rotazione lato*pi/2, che
    e l'unica formula che passa per quel punto (top 0, right pi/2, bottom
    pi, left 3pi/2). Prima: offset 1.0 e rotazione 0 per top E bottom, pi/2
    per right E left."""
    from ddforge.compose import _BOTTOM, _LEFT, _RIGHT, _TOP, _wall_slot
    from ddforge.model import Rect

    rect = Rect(10, 1, 17, 7)  # la cucina della taverna, alla taglia di default

    class _FixedSide:
        """rng che sceglie sempre il lato voluto; uniform resta al centro."""
        def __init__(self, side):
            self.side = side

        def choice(self, options):
            return self.side

        def uniform(self, a, b):
            return (a + b) / 2

    expected = {
        _TOP: (rect.y1 + 0.5, 0.0),
        _RIGHT: (rect.x2 - 0.5, math.pi / 2),
        _BOTTOM: (rect.y2 - 0.5, math.pi),
        _LEFT: (rect.x1 + 0.5, 3 * math.pi / 2),
    }
    for side, (coordinate, rotation) in expected.items():
        x, y, actual_rotation = _wall_slot(rect, _FixedSide(side))
        along = y if side in (_TOP, _BOTTOM) else x
        assert math.isclose(along, coordinate), (
            f"lato {side}: il pezzo sta a {along}, non addossato a {coordinate}"
        )
        assert math.isclose(actual_rotation, rotation), (
            f"lato {side}: rotazione {actual_rotation}, attesa {rotation} (guarda il muro)"
        )


def test_furniture_against_a_wall_faces_into_the_room(rendered):
    """La stessa regola verificata end-to-end sul file che Jay apre.

    Il marcatore di 'addossato' e la distanza esatta di mezzo quadretto: e
    l'invariante che _wall_slot garantisce. Un pezzo a distanza qualunque
    e stato messo al centro o attorno a un tavolo, e prende la rotazione da
    quelli, non dal muro.

    All'angolo dettato dal lato si somma l'offset proprio dello sprite, che
    per tutto il catalogo e zero tranne che per la botte piccola (round 3,
    vedi _rotation_offset)."""
    from ddforge.compose import _rotation_offset

    blueprint, prepared = rendered
    expected = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]

    against_wall, wrong = 0, []
    for room in blueprint.rooms:
        level = prepared["world"]["levels"][str(room.level)]
        for obj, x, y in _objects_of(level):
            if not (room.rect.x1 <= x <= room.rect.x2 and room.rect.y1 <= y <= room.rect.y2):
                continue
            side, distance = _nearest_side(room.rect, x, y)
            if abs(distance - 0.5) > 1e-9:
                continue
            against_wall += 1
            want = (expected[side] + _rotation_offset(obj["texture"])) % (2 * math.pi)
            if abs(obj["rotation"] - want) > 1e-6:
                wrong.append((room.kind, side, round(obj["rotation"], 4), obj["texture"].rsplit("/", 1)[-1]))

    assert against_wall > 0, "nessun pezzo risulta addossato: l'offset non arriva fino al file"
    assert not wrong, f"oggetti addossati che guardano il muro: {wrong[:10]}"


# Una sedia attorno al suo tavolo e adiacenza voluta, non sovrapposizione:
# e l'unica coppia esentata dal controllo di ingombro.
_SEATING = ("chair", "stool", "bench")
_TABLES = ("table", "desk")


def _is_seat_at_table(a: str, b: str) -> bool:
    a, b = a.lower(), b.lower()
    return (
        any(s in a for s in _SEATING) and any(t in b for t in _TABLES)
        or any(s in b for s in _SEATING) and any(t in a for t in _TABLES)
    )


def _overlapping_pairs(level):
    from ddforge.compose import _texture_size

    placed = [(x, y, _texture_size(obj["texture"]), obj["texture"].rsplit("/", 1)[-1])
              for obj, x, y in _objects_of(level)]
    pairs = []
    for i, (ax, ay, asize, aname) in enumerate(placed):
        for bx, by, bsize, bname in placed[i + 1:]:
            if _is_seat_at_table(aname, bname):
                continue
            limit = (asize + bsize) / 2
            distance = math.hypot(ax - bx, ay - by)
            if distance < limit - 1e-9:
                pairs.append((aname, bname, round(distance, 3), limit))
    return pairs


@pytest.mark.parametrize("building_type", ["tavern", "manor", "warehouse"])
def test_no_two_pieces_of_furniture_overlap(building_type, tmp_path):
    """Difetti 7, 9 e 12: 'i due camini sono parzialmente sovrapposti', 'due
    botti sovrapposte nella stanza a destra in alto', 'nella magione al piano
    terra gli sprite sono tutti sovrapposti'.

    _furnish_room piazzava ogni pezzo senza sapere nulla dei precedenti: sul
    file del round 1 c'erano quattro coppie di sedie nella stessa identica
    posizione, due camini 2x2 a 1.25 quadretti l'uno dall'altro, una botte e
    un keg a 0.37. Due pezzi non possono stare piu vicini della semisomma dei
    loro ingombri — tranne le sedie attorno al loro tavolo, che e adiacenza
    voluta."""
    out = tmp_path / f"{building_type}.dungeondraft_map"
    result = subprocess.run(
        [
            sys.executable, "-m", "ddforge.cli", "generate", "building",
            "--template", TEMPLATE, "--out", str(out),
            "--width", "40", "--height", "40", "--seed", str(SEED),
            "--building-type", building_type, "--furnish", "medium",
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    prepared = json.loads(out.read_text(encoding="utf-8"))

    for level_key, level in prepared["world"]["levels"].items():
        pairs = _overlapping_pairs(level)
        assert not pairs, f"{building_type} piano {level_key}: oggetti sovrapposti: {pairs[:10]}"


@pytest.mark.parametrize("building_type", ["tavern", "manor", "warehouse"])
def test_rooms_have_the_size_of_real_rooms(building_type):
    """Difetto 11: 'le stanze che hai fatto sono molto molto grandi.
    Considera che un quadretto dovrebbe essere 1.5m reali'.

    Il generatore chiedeva a _build_tree tante stanze quanti erano i kind del
    piano (3 per una taverna) e _build_tree si ferma appena le raggiunge:
    tre foglie su un footprint 34x38 danno stanze da 34x18 quadretti, cioe
    51x27 METRI. Il tetto va messo sulla dimensione della stanza, non sul
    loro numero.

    Il magazzino e l'unica eccezione, e per specifica (SPEC.md 9.2: piano
    terra a volume unico): un capannone e grande davvero."""
    blueprint = building.generate(width=40, height=40, seed=SEED, building_type=building_type)
    if building_type == "warehouse":
        pytest.skip("magazzino: volume unico per specifica, SPEC.md 9.2")

    max_side_m = 12.0
    oversized = [
        (room.kind, room.rect.w * TILE_METERS, room.rect.h * TILE_METERS)
        for room in blueprint.rooms
        if max(room.rect.w, room.rect.h) * TILE_METERS > max_side_m
    ]
    assert not oversized, (
        f"stanze piu lunghe di {max_side_m} m di lato (kind, larghezza_m, altezza_m): {oversized[:10]}"
    )


# ===========================================================================
# ROUND 3 — un solo difetto residuo:
# 14. "le botti piccole vanno ancora girate a destra di 90 gradi. Tutti gli
#     altri vanno bene"
# ===========================================================================

def test_a_keg_is_rotated_a_quarter_turn_more_than_everything_else():
    """Difetto 14. La regola `rotazione = lato * pi/2` presuppone che a
    rotazione 0 la faccia dello sprite guardi in giu, e per tutto il
    catalogo e vero — Jay ha confermato che al round 3 va bene tutto tranne
    le botti piccole.

    Keg_Wood_Light_H_1x1 fa eccezione: la 'H' sta per horizontal, la botte e
    coricata sul fianco lungo l'asse orizzontale, quindi il suo asse parte
    gia ruotato di un quarto di giro rispetto agli altri. Non e una regola
    generale ma una proprieta di quello sprite, e come tale va tabellata per
    texture e non dedotta dal lato."""
    from ddforge.compose import _rotation_offset

    keg = "res://packs/FA30DDXY/textures/objects/[FA] Asset Testing/Keg_Wood_Light_H_1x1.webp"
    assert math.isclose(_rotation_offset(keg), math.pi / 2), (
        "la botte piccola non riceve il quarto di giro in piu"
    )
    for other in (
        "res://textures/objects/containers/barrel_forge_01.png",
        "res://textures/objects/tables/bed_wood_single_01.png",
        "res://packs/FA30DDXY/textures/objects/[FA] Asset Testing/Oven_Brick_Red_A2_2x2.webp",
    ):
        assert _rotation_offset(other) == 0.0, f"{other}: non deve ruotare piu degli altri"


def test_kegs_in_the_rendered_building_carry_the_extra_quarter_turn(rendered):
    """La stessa cosa end-to-end: sul file che Jay apre, una botte piccola
    addossata a un muro sta a lato*pi/2 + pi/2, non a lato*pi/2."""
    blueprint, prepared = rendered
    expected = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]

    kegs = []
    for room in blueprint.rooms:
        level = prepared["world"]["levels"][str(room.level)]
        for obj, x, y in _objects_of(level):
            if "keg" not in obj["texture"].lower():
                continue
            if not (room.rect.x1 <= x <= room.rect.x2 and room.rect.y1 <= y <= room.rect.y2):
                continue
            side, distance = _nearest_side(room.rect, x, y)
            if abs(distance - 0.5) > 1e-9:
                continue
            kegs.append((side, obj["rotation"]))

    assert kegs, "nessuna botte piccola addossata a un muro nel file: il test non verifica nulla"
    for side, rotation in kegs:
        want = (expected[side] + math.pi / 2) % (2 * math.pi)
        assert abs(rotation - want) < 1e-6, (
            f"botte piccola sul lato {side}: rotazione {rotation}, attesa {want}"
        )
