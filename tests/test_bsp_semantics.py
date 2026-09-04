"""Test per la semantica D&D del generatore BSP (TASK-22): boss, nodi
tattici, corridoi lunghi, porte segrete. Seed fissi come richiesto dall'AC5."""

from collections import deque

from ddforge.generators import bsp


def _bfs_reachable(graph, start=0):
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen


def _non_secret_graph(blueprint):
    """Ricostruisce il grafo SENZA le porte segrete: sia i nodi tattici sia
    la scelta del boss sono congelati su questo grafo (TASK-22), prima che
    le scorciatoie nascoste possano accorciare le distanze o alzare i
    gradi. L'ordine di room.doors rispecchia l'ordine di blueprint.graph[i]
    (_connect_rooms aggiunge entrambi insieme) e _add_secret_doors gira per
    ultimo, quindi gli ultimi N vicini di ogni stanza (N = porte segrete di
    quella stanza) sono esattamente quelli aggiunti come scorciatoia."""
    graph = {}
    for i, room in enumerate(blueprint.rooms):
        n_secret = sum(1 for d in room.doors if d.kind == "secret")
        neighbors = blueprint.graph[i]
        graph[i] = neighbors[: len(neighbors) - n_secret] if n_secret else list(neighbors)
    return graph


# ---------------------------------------------------------------------------
# Stanza boss
# ---------------------------------------------------------------------------

def test_exactly_one_room_is_marked_boss():
    bp = bsp.generate(width=60, height=60, seed=1, rooms=10)
    boss_rooms = [r for r in bp.rooms if r.kind == "boss"]
    assert len(boss_rooms) == 1


def test_boss_room_is_the_farthest_from_entrance():
    """La scelta del boss usa il grafo PRIMA delle porte segrete (TASK-22):
    una scorciatoia nascosta puo accorciare la distanza del boss (o di un
    altro vicolo cieco) senza invalidare la scelta gia fatta."""
    bp = bsp.generate(width=60, height=60, seed=1, rooms=10)
    from ddforge.generators.bsp import _bfs_distances

    dist = _bfs_distances(_non_secret_graph(bp), 0)
    boss_index = next(i for i, r in enumerate(bp.rooms) if r.kind == "boss")
    assert dist[boss_index] == max(dist.values())


def test_enlarge_room_grows_rect_when_space_is_free():
    """Test diretto e deterministico su _enlarge_room, isolato dal resto
    della generazione: una stanza piccola in una mappa grande e vuota deve
    crescere sui lati senza porte."""
    from ddforge.generators.bsp import _enlarge_room
    from ddforge.model import Blueprint, Rect, Room

    room = Room(rect=Rect(40, 40, 45, 45), kind="sala")
    other = Room(rect=Rect(0, 0, 5, 5), kind="sala")  # lontana, nessuna interferenza
    blueprint = Blueprint(
        width=100, height=100, rooms=[room, other], corridors=[], graph={0: [], 1: []},
        seed=1, style="dungeon",
    )
    grown = _enlarge_room(blueprint, 0)
    assert grown is True
    assert room.rect.w > 5 or room.rect.h > 5


def test_enlarge_room_never_touches_sides_with_doors():
    from ddforge.generators.bsp import _enlarge_room
    from ddforge.model import Blueprint, Door, Rect, Room

    room = Room(rect=Rect(40, 40, 45, 45), kind="sala", doors=[Door(wall_index=1, t=0.5)])  # RIGHT
    blueprint = Blueprint(
        width=100, height=100, rooms=[room], corridors=[], graph={0: []}, seed=1, style="dungeon",
    )
    _enlarge_room(blueprint, 0)
    assert room.rect.x2 == 45  # il lato RIGHT (con la porta) non si e mosso


def test_boss_room_never_overlaps_other_rooms_after_enlargement():
    for seed in range(15):
        bp = bsp.generate(width=60, height=60, seed=seed, rooms=8)
        boss_index = next(i for i, r in enumerate(bp.rooms) if r.kind == "boss")
        boss_rect = bp.rooms[boss_index].rect
        for i, room in enumerate(bp.rooms):
            if i == boss_index:
                continue
            assert not boss_rect.overlaps(room.rect)


def test_boss_room_never_exceeds_canvas_after_enlargement():
    for seed in range(15):
        bp = bsp.generate(width=60, height=60, seed=seed, rooms=8)
        boss = next(r for r in bp.rooms if r.kind == "boss")
        assert 0 <= boss.rect.x1 < boss.rect.x2 <= 60
        assert 0 <= boss.rect.y1 < boss.rect.y2 <= 60


# ---------------------------------------------------------------------------
# Nodi tattici
# ---------------------------------------------------------------------------

def test_tactical_rooms_have_degree_at_least_3():
    bp = bsp.generate(width=70, height=70, seed=2, rooms=12, loops=0.2)
    for i in bp.tactical_rooms:
        assert len(bp.graph[i]) >= 3


def test_rooms_with_degree_at_least_3_are_all_marked_tactical():
    """tactical_rooms e congelato sul grafo PRIMA delle porte segrete
    (TASK-22): il confronto va fatto con lo stesso grafo, non con
    bp.graph finale (che include anche le scorciatoie)."""
    bp = bsp.generate(width=70, height=70, seed=2, rooms=12, loops=0.2)
    pre_secret_graph = _non_secret_graph(bp)
    expected = {i for i in range(len(bp.rooms)) if len(pre_secret_graph[i]) >= 3}
    assert set(bp.tactical_rooms) == expected


def test_secret_doors_do_not_retroactively_create_tactical_rooms():
    """Una stanza che raggiunge grado 3 SOLO grazie a una scorciatoia
    segreta non deve comparire in tactical_rooms."""
    bp = bsp.generate(width=70, height=70, seed=2, rooms=12, loops=0.2)
    pre_secret_graph = _non_secret_graph(bp)
    for i in bp.tactical_rooms:
        assert len(pre_secret_graph[i]) >= 3


# ---------------------------------------------------------------------------
# Corridoi lunghi
# ---------------------------------------------------------------------------

def test_long_corridor_indices_reference_corridors_over_threshold():
    bp = bsp.generate(width=90, height=90, seed=4, rooms=14, loops=0.2)
    for i in bp.long_corridor_indices:
        rect = bp.corridors[i]
        assert max(rect.w, rect.h) > 12


def test_no_short_corridor_is_flagged_as_long():
    bp = bsp.generate(width=90, height=90, seed=4, rooms=14, loops=0.2)
    flagged = set(bp.long_corridor_indices)
    for i, rect in enumerate(bp.corridors):
        if max(rect.w, rect.h) <= 12:
            assert i not in flagged


def test_long_corridors_exist_on_a_large_map_with_small_rooms():
    """Il marcatore non deve essere codice morto: su una mappa grande con
    stanze piccole (quindi spazio vuoto fra una e l'altra) deve comparire
    almeno un corridoio oltre soglia.

    Nota di taratura, dal gate umano M3 (TASK-26): questo test usava 5
    stanze su 100x100, e passava per il motivo sbagliato. Con poche stanze
    le foglie BSP sono enormi e le stanze inscritte si toccano quasi tutte,
    quindi corridoi lunghi non ne servono: quelli che comparivano erano
    l'effetto del difetto poi corretto (due stanze scelte a caso agli angoli
    opposti della mappa). Servono tante stanze piccole, non poche grandi."""
    found = False
    for seed in range(20):
        bp = bsp.generate(width=100, height=100, seed=seed, rooms=16, min_room=3, max_room=6)
        if bp.long_corridor_indices:
            found = True
            break
    assert found


# ---------------------------------------------------------------------------
# Porte segrete
# ---------------------------------------------------------------------------

def test_every_original_dead_end_receives_a_secret_door():
    """Ogni stanza che era un vicolo cieco (grado 1) prima delle porte
    segrete ne riceve una. Il lato "bersaglio" della connessione (l'altra
    stanza) puo invece avere qualunque grado preesistente: non e lui il
    vicolo cieco da sbloccare, e AC4 non lo vieta."""
    bp = bsp.generate(width=70, height=70, seed=2, rooms=12, loops=0.15)
    pre_secret_graph = _non_secret_graph(bp)
    dead_ends = [i for i in range(len(bp.rooms)) if len(pre_secret_graph[i]) == 1]
    for i in dead_ends:
        assert any(d.kind == "secret" for d in bp.rooms[i].doors), (
            f"stanza {i} era un vicolo cieco ma non ha ricevuto una porta segreta"
        )


def test_rooms_with_secret_doors_are_reachable_by_more_than_one_path():
    """Dopo l'aggiunta, una stanza con porta segreta ha grado >= 2 nel
    grafo completo: raggiungibile anche da un percorso diverso."""
    bp = bsp.generate(width=70, height=70, seed=2, rooms=12, loops=0.15)
    for i, room in enumerate(bp.rooms):
        if any(d.kind == "secret" for d in room.doors):
            assert len(bp.graph[i]) >= 2


def test_graph_stays_connected_after_all_semantic_passes():
    for seed in range(20):
        bp = bsp.generate(width=60, height=60, seed=seed, rooms=8)
        reachable = _bfs_reachable(bp.graph, start=0)
        assert reachable == set(range(len(bp.rooms)))
