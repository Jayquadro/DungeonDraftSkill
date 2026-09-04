"""Regressioni del gate umano M3 (TASK-26).

Jay ha aperto generated/dungeon_m3.dungeondraft_map (seed 1337) in
Dungeondraft e ha segnalato tre difetti, tutti sui corridoi. Ogni test qui
riproduce uno dei tre PRIMA della correzione, come richiesto dal criterio
di accettazione #3 del task.

Difetto 1: "la stanza in basso a sinistra e collegata con quella in alto al
centro e il corridoio che le collega interseca altre stanze".
Difetto 2: "la stanza a sinistra al centro e collegata con quella al centro
in alto con un corridoio che entra completamente nella stanza in alto a
sinistra".
Difetto 3: "il corridoio che dalla stanza in alto a sinistra si apre nel suo
angolo in basso a destra ha i muri girati sui lati sbagliati".

I primi due sono lo stesso difetto (rotta dei corridoi cieca rispetto alle
altre stanze), il terzo e indipendente (orientamento del canale).

Alla seconda apertura, corretti i primi tre, Jay ne ha segnalato un quarto:
"nella stanza in basso a sinistra il muro che arriva alla porta in alto a
destra e lungo mezzo quadretto in piu e ostacola il passaggio" (vedi
test_enlarging_a_room_does_not_move_its_doors).
"""

from ddforge.assets import Palette
from ddforge.compose import plan_corridor, render_blueprint
from ddforge.godot import parse_pv2
from ddforge.ids import IdAllocator
from ddforge.generators import bsp
from ddforge.model import Blueprint, Door, Rect, Room

PALETTE = Palette(
    wall="res://textures/walls/stone.png",
    floor="res://textures/patterns/normal/stone_floor.png",
    door="res://textures/portals/door_00.png",
)


def _empty_level():
    return {
        "walls": [], "portals": [], "patterns": [], "objects": [], "paths": [],
        "lights": [], "texts": [],
        "roofs": {"shade": True, "shade_contrast": 0.5, "sun_direction": 45, "roofs": []},
    }


def _strict_overlap(a: Rect, b: Rect) -> bool:
    """Sovrapposizione con area non nulla. Un corridoio che si ferma sul muro
    della stanza che collega la tocca senza sovrapporsi (overlap 0 su un
    asse): quello e corretto e non deve far fallire il test."""
    return (min(a.x2, b.x2) - max(a.x1, b.x1)) > 0 and (min(a.y2, b.y2) - max(a.y1, b.y1)) > 0


def _corridors_crossing_rooms(blueprint) -> list[tuple[int, int]]:
    return [
        (i, j)
        for i, corridor in enumerate(blueprint.corridors)
        for j, room in enumerate(blueprint.rooms)
        if _strict_overlap(corridor, room.rect)
    ]


# ---------------------------------------------------------------------------
# Difetti 1 e 2: corridoi che attraversano stanze
# ---------------------------------------------------------------------------

def test_m3_seed_1337_has_no_corridor_crossing_a_room():
    """Il caso esatto aperto da Jay: dungeon_m3 e seed=1337, 80x80, 8 stanze."""
    blueprint = bsp.generate(width=80, height=80, seed=1337, rooms=8)
    assert _corridors_crossing_rooms(blueprint) == []


def test_no_corridor_crosses_a_room_on_any_seed():
    """Non e un caso sfortunato del seed 1337: prima della correzione 37 seed
    su 40 avevano almeno un attraversamento."""
    for seed in range(40):
        blueprint = bsp.generate(width=80, height=80, seed=seed, rooms=8)
        crossings = _corridors_crossing_rooms(blueprint)
        assert crossings == [], f"seed={seed}: corridoi che attraversano stanze {crossings}"


def test_plan_corridor_avoids_a_room_sitting_on_the_default_l_route():
    """Geometria minima del difetto 2: la rotta a L predefinita (orizzontale
    dal primo rettangolo, poi verticale) passa in pieno dentro `obstacle`.
    Con l'ostacolo dichiarato, plan_corridor deve scegliere l'altra piega."""
    room_a = Rect(30, 4, 40, 20)    # stanza in alto al centro
    room_b = Rect(3, 24, 18, 46)    # stanza a sinistra al centro
    obstacle = Rect(2, 2, 27, 22)   # stanza in alto a sinistra, sulla L predefinita

    corridors, _, _ = plan_corridor(room_a, room_b, obstacles=[obstacle])

    assert corridors, "plan_corridor deve produrre almeno un segmento"
    for corridor in corridors:
        assert not _strict_overlap(corridor, obstacle), (
            f"il segmento {corridor} entra nella stanza {obstacle}"
        )


# ---------------------------------------------------------------------------
# Difetto 3: muri del canale sui lati sbagliati
# ---------------------------------------------------------------------------

def test_square_elbow_segment_keeps_its_real_orientation():
    """Il gomito fra due stanze separate da un solo quadretto e un segmento
    1x1: l'euristica 'w >= h -> orizzontale' lo dichiarava orizzontale anche
    quando e un passaggio verticale. plan_corridor conosce l'orientamento
    vero e deve conservarlo nel Rect che restituisce."""
    room_a = Rect(2, 1, 26, 22)   # stanza in alto a sinistra
    room_b = Rect(22, 23, 31, 31) # stanza sotto, separata da un quadretto

    corridors, _, _ = plan_corridor(room_a, room_b)

    assert len(corridors) == 1
    segment = corridors[0]
    assert segment.w == segment.h == 1, "il caso da riprodurre e il segmento quadrato"
    assert segment.horizontal is False, "e un passaggio verticale, non orizzontale"


# ---------------------------------------------------------------------------
# Difetto 4: porta disallineata dal corridoio che ci arriva
# ---------------------------------------------------------------------------

def _door_point(rect: Rect, door) -> tuple[float, float]:
    """Punto assoluto della porta, in quadretti."""
    corners = [(rect.x1, rect.y1), (rect.x2, rect.y1), (rect.x2, rect.y2), (rect.x1, rect.y2)]
    (x0, y0), (x1, y1) = corners[door.wall_index], corners[(door.wall_index + 1) % 4]
    return (x0 + (x1 - x0) * door.t, y0 + (y1 - y0) * door.t)


def _misaligned_doors(blueprint) -> list[str]:
    """Estremi di corridoio che sboccano su un muro di stanza senza trovarci
    una porta centrata sull'asse del corridoio. Se la porta e spostata anche
    di poco, fra il suo bordo e la parete del corridoio resta un moncone di
    muro in mezzo al passaggio: e il difetto segnalato da Jay."""
    problems = []
    for i, corridor in enumerate(blueprint.corridors):
        axis = (corridor.x1 + corridor.x2) / 2 if not corridor.horizontal else (corridor.y1 + corridor.y2) / 2
        for end in ((corridor.y1, corridor.y2) if not corridor.horizontal else (corridor.x1, corridor.x2)):
            for j, room in enumerate(blueprint.rooms):
                rect = room.rect
                if corridor.horizontal:
                    touches = (rect.x1 == end or rect.x2 == end) and rect.y1 <= axis <= rect.y2
                    expected = (end, axis)
                else:
                    touches = (rect.y1 == end or rect.y2 == end) and rect.x1 <= axis <= rect.x2
                    expected = (axis, end)
                if not touches:
                    continue
                if not any(
                    abs(_door_point(rect, d)[0] - expected[0]) < 1e-6
                    and abs(_door_point(rect, d)[1] - expected[1]) < 1e-6
                    for d in room.doors
                ):
                    points = [tuple(round(c, 3) for c in _door_point(rect, d)) for d in room.doors]
                    problems.append(
                        f"corridoio {i} sbocca in {expected} sulla stanza {j} {rect}, "
                        f"ma le sue porte sono in {points}"
                    )
    return problems


def test_m3_seed_1337_has_no_door_offset_from_its_corridor():
    """Il caso esatto riaperto da Jay: la porta in alto a destra della stanza
    in basso a sinistra cadeva a x=31.487 invece che a x=31.0, il centro del
    corridoio che ci arriva. Mezzo quadretto di muro in mezzo al passaggio."""
    blueprint = bsp.generate(width=80, height=80, seed=1337, rooms=8)
    assert _misaligned_doors(blueprint) == []


def test_no_door_is_offset_from_its_corridor_on_any_seed():
    for seed in range(40):
        blueprint = bsp.generate(width=80, height=80, seed=seed, rooms=8)
        assert _misaligned_doors(blueprint) == [], f"seed={seed}"


def test_enlarging_a_room_does_not_move_its_doors():
    """Causa del difetto 4. _enlarge_room (stanza boss) non tocca i lati che
    portano una porta, ma allargando i lati PERPENDICOLARI allunga comunque
    il muro su cui la porta e appoggiata. La porta e memorizzata come
    frazione `t` di quel muro, quindi si sposta insieme a lui, mentre il
    corridoio a cui era allineata resta dov'era."""
    room = Room(rect=Rect(2, 48, 41, 77), kind="sala")
    room.doors.append(Door(wall_index=0, t=(31 - 2) / 39))  # porta a x=31 sul lato TOP
    blueprint = Blueprint(
        width=80, height=80, rooms=[room], corridors=[], graph={0: []},
        seed=1337, style="dungeon",
    )

    bsp._enlarge_room(blueprint, 0)

    assert room.rect != Rect(2, 48, 41, 77), "il test ha senso solo se la stanza si allarga"
    assert room.rect.y1 == 48, "il lato con la porta non si sposta"
    x, y = _door_point(room.rect, room.doors[0])
    assert (x, y) == (31, 48), "la porta deve restare dov'era in coordinate assolute"


def test_render_draws_the_long_sides_of_a_vertical_square_channel():
    """Conseguenza visibile in Dungeondraft del difetto 3: su un canale
    verticale i muri vanno a sinistra e a destra. Con i muri sopra e sotto il
    passaggio risulta murato e la porta appena tagliata ributta contro un
    muro (e quello che Jay ha visto come 'muri girati sui lati sbagliati')."""
    room_a = Room(rect=Rect(2, 1, 26, 22), kind="sala")
    room_b = Room(rect=Rect(22, 23, 31, 31), kind="sala")
    corridors, _, _ = plan_corridor(room_a.rect, room_b.rect)
    blueprint = Blueprint(
        width=80, height=80, rooms=[room_a, room_b], corridors=list(corridors),
        graph={0: [1], 1: [0]}, seed=1337, style="dungeon",
    )

    level = _empty_level()
    render_blueprint(level, IdAllocator(), blueprint, PALETTE)

    segment = corridors[0]
    channel_walls = [
        parse_pv2(wall["points"])
        for wall in level["walls"]
        if all(
            segment.x1 * 256 <= x <= segment.x2 * 256 and segment.y1 * 256 <= y <= segment.y2 * 256
            for x, y in parse_pv2(wall["points"])
        )
    ]
    assert len(channel_walls) == 2, "il canale ha esattamente due muri lunghi"
    for points in channel_walls:
        (x0, _), (x1, _) = points[0], points[-1]
        assert x0 == x1, "su un canale verticale i due muri sono verticali (sinistra e destra)"
