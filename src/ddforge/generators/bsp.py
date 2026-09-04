"""Dungeon a stanze via partizione binaria dello spazio (BSP).

Cripte, complessi sotterranei, prigioni. Vedi docs/SPEC.md §9.1.
Produce solo un Blueprint (geometria pura): nessun accesso a level/ids/JSON
qui, coerente col flusso generatore -> Blueprint -> compose -> build -> JSON
(SPEC.md, model.py). La semantica D&D (stanza boss, nodi tattici, corridoi
bui, porte segrete) e in TASK-22.

Nota per chi renderizza Blueprint.corridors in JSON (TASK-24): ogni elemento
e un Corridor, cioe un canale aperto (solo i 2 lati lunghi, niente muri di
testata, altrimenti si riblocca la porta appena tagliata nel muro della
stanza, vedi TASK-19). L'orientamento e un campo esplicito di Corridor, e
va usato quello: derivarlo da rect.w >= rect.h sembrava innocuo, ma i
segmenti di gomito sono quadrati e l'euristica li murava di traverso
(gate umano M3, TASK-26). Disegnali sempre in blocco con
compose.draw_corridor_network, mai uno alla volta: i muri di un braccio si
devono fermare dove ne inizia un altro.
"""

import math
import random

from ddforge.compose import _overlap_area, _shared_wall_segment, _side_corners, plan_corridor
from ddforge.model import Blueprint, Corridor, Door, Rect, Room


class _BSPNode:
    __slots__ = ("rect", "depth", "left", "right", "room_index")

    def __init__(self, rect: Rect, depth: int) -> None:
        self.rect = rect
        self.depth = depth
        self.left: "_BSPNode | None" = None
        self.right: "_BSPNode | None" = None
        self.room_index: int | None = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None


def _can_split(rect: Rect, max_room: int, depth: int, depth_max: int) -> bool:
    if depth >= depth_max:
        return False
    return rect.w >= max_room * 2 or rect.h >= max_room * 2


def _split_rect(rect: Rect, rng: random.Random) -> tuple[Rect, Rect]:
    """Taglia lungo l'asse piu lungo a una frazione casuale 35-65%."""
    frac = rng.uniform(0.35, 0.65)
    if rect.w >= rect.h:
        cut = rect.x1 + round(rect.w * frac)
        cut = min(max(cut, rect.x1 + 1), rect.x2 - 1)
        return Rect(rect.x1, rect.y1, cut, rect.y2), Rect(cut, rect.y1, rect.x2, rect.y2)
    cut = rect.y1 + round(rect.h * frac)
    cut = min(max(cut, rect.y1 + 1), rect.y2 - 1)
    return Rect(rect.x1, rect.y1, rect.x2, cut), Rect(rect.x1, cut, rect.x2, rect.y2)


def _build_tree(root_rect: Rect, rng: random.Random, *, rooms_target: int, max_room: int, depth_max: int):
    root = _BSPNode(root_rect, 0)
    leaves = [root]
    splittable = [root] if _can_split(root_rect, max_room, 0, depth_max) else []

    while len(leaves) < rooms_target and splittable:
        idx = rng.randrange(len(splittable))
        node = splittable.pop(idx)
        leaves.remove(node)

        rect_a, rect_b = _split_rect(node.rect, rng)
        node.left = _BSPNode(rect_a, node.depth + 1)
        node.right = _BSPNode(rect_b, node.depth + 1)
        for child in (node.left, node.right):
            leaves.append(child)
            if _can_split(child.rect, max_room, child.depth, depth_max):
                splittable.append(child)

    return root, leaves


def _inscribe_room(leaf_rect: Rect, rng: random.Random, min_room: int) -> Rect:
    max_margin_x = max(0, int(leaf_rect.w - min_room) // 2)
    max_margin_y = max(0, int(leaf_rect.h - min_room) // 2)
    margin_x = rng.randint(0, min(2, max_margin_x))
    margin_y = rng.randint(0, min(2, max_margin_y))
    return Rect(
        leaf_rect.x1 + margin_x, leaf_rect.y1 + margin_y,
        leaf_rect.x2 - margin_x, leaf_rect.y2 - margin_y,
    )


def _t_on_side(rect: Rect, side: int, point_grid: tuple[float, float]) -> float:
    (x0, y0), (x1, y1) = _side_corners(rect, side)
    dx, dy = x1 - x0, y1 - y0
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return 0.0
    px, py = point_grid
    t = ((px - x0) * dx + (py - y0) * dy) / length_sq
    return min(max(t, 0.0), 1.0)


def _non_colliding_t(room: Room, wall_index: int, desired_t: float, min_gap: float = 0.12) -> float:
    """Scosta desired_t se troppo vicino (< DDF105, con margine) a una porta
    gia presente sullo stesso muro. Puo succedere quando una stanza si
    collega a piu vicini dallo stesso lato: piu connessioni verso stanze
    diverse possono proiettarsi vicino allo stesso punto (es. il centro del
    lato), specialmente per i corridoi (SPEC.md §9.1 non lo vieta
    esplicitamente, ma DDF105 esiste apposta per segnalarlo)."""
    existing = [d.t for d in room.doors if d.wall_index == wall_index]
    if not existing:
        return desired_t
    t = desired_t
    step = 1
    while any(abs(t - e) < min_gap for e in existing) and step <= 10:
        offset = min_gap * ((step + 1) // 2)
        t = desired_t + offset if step % 2 == 1 else desired_t - offset
        t = min(max(t, 0.05), 0.95)
        step += 1
    return t


def _connect_rooms(rooms: list, index_a: int, index_b: int, corridors: list, corridor_width: float, *, kind: str = "wood", require_clean: bool = False) -> bool:
    """Decide come collegare due stanze e popola Room.doors/corridors,
    senza toccare nessun JSON: riusa la stessa geometria di compose.py.
    Ritorna True se il collegamento e stato fatto.

    Prende la lista completa delle stanze, non solo le due da collegare:
    tutte le altre sono ostacoli che il corridoio deve scansare (gate umano
    M3, TASK-26). Con `require_clean` rinuncia del tutto al collegamento se
    la rotta migliore entra comunque in una stanza di passaggio: e la scelta
    giusta per i collegamenti facoltativi (anelli, porte segrete), che sono
    un abbellimento e non devono mai scavare dentro un'altra stanza pur di
    esistere. La connettivita non dipende da loro: quella la garantisce
    l'albero."""
    room_a, room_b = rooms[index_a], rooms[index_b]
    shared = _shared_wall_segment(room_a.rect, room_b.rect)
    if shared is not None:
        side_a, side_b, point_a = shared
        point_b = point_a
        segments = []
    else:
        obstacles = [r.rect for i, r in enumerate(rooms) if i not in (index_a, index_b)]
        segments, (side_a, point_a), (side_b, point_b) = plan_corridor(
            room_a.rect, room_b.rect, width=corridor_width, obstacles=obstacles
        )
        if require_clean and any(
            _overlap_area(segment, obstacle) for segment in segments for obstacle in obstacles
        ):
            return False

    corridors.extend(segments)
    t_a = _non_colliding_t(room_a, side_a, _t_on_side(room_a.rect, side_a, point_a))
    t_b = _non_colliding_t(room_b, side_b, _t_on_side(room_b.rect, side_b, point_b))
    room_a.doors.append(Door(wall_index=side_a, t=t_a, kind=kind))
    room_b.doors.append(Door(wall_index=side_b, t=t_b, kind=kind))
    return True


def _closest_pair(rooms: list, group_a: list, group_b: list) -> tuple[int, int]:
    """Coppia di stanze piu vicina (centro-centro) fra i due sottoalberi."""
    def distance(pair: tuple[int, int]) -> float:
        (ax, ay), (bx, by) = rooms[pair[0]].rect.center(), rooms[pair[1]].rect.center()
        return math.hypot(bx - ax, by - ay)

    return min(
        ((i, j) for i in group_a for j in group_b),
        key=lambda pair: (distance(pair), pair),  # pareggio -> indici piu bassi, riproducibile
    )


def _connect_subtree(node: _BSPNode, rooms: list, graph: dict, corridors: list, corridor_width: float) -> list:
    """Risale l'albero collegando i due sottoalberi di ogni nodo interno.
    Ritorna gli indici (in `rooms`) di tutte le stanze del sottoalbero.

    Le due meta si collegano attraverso la coppia di stanze piu vicina al
    taglio, non attraverso due rappresentanti a caso: cosi ogni corridoio
    resta locale alla partizione BSP che lo genera. Con il rappresentante
    casuale (com'era fino al gate M3, TASK-26) capitava che due stanze agli
    angoli opposti della mappa si collegassero fra loro, con un corridoio
    che attraversava tutto quello che trovava in mezzo."""
    if node.is_leaf:
        return [node.room_index]

    left = _connect_subtree(node.left, rooms, graph, corridors, corridor_width)
    right = _connect_subtree(node.right, rooms, graph, corridors, corridor_width)

    idx_left, idx_right = _closest_pair(rooms, left, right)
    _connect_rooms(rooms, idx_left, idx_right, corridors, corridor_width)
    graph[idx_left].append(idx_right)
    graph[idx_right].append(idx_left)

    return left + right


def _add_loop_connections(rooms: list, graph: dict, corridors: list, rng: random.Random, loops: float, corridor_width: float) -> None:
    """Il 10-20% di collegamenti extra fra le stanze piu vicine non ancora
    connesse, per creare anelli ed evitare un dungeon-albero (SPEC.md §9.1)."""
    n = len(rooms)
    if n < 3:
        return
    connected = {frozenset((a, b)) for a, neighbors in graph.items() for b in neighbors}

    candidates = []
    for i in range(n):
        for j in range(i + 1, n):
            if frozenset((i, j)) in connected:
                continue
            ax, ay = rooms[i].rect.center()
            bx, by = rooms[j].rect.center()
            candidates.append((math.hypot(bx - ax, by - ay), i, j))
    candidates.sort(key=lambda c: (c[0], c[1], c[2]))

    n_extra = round(loops * n)
    for _, i, j in candidates[:n_extra]:
        if not _connect_rooms(rooms, i, j, corridors, corridor_width, require_clean=True):
            continue
        graph[i].append(j)
        graph[j].append(i)


_TOP, _RIGHT, _BOTTOM, _LEFT = 0, 1, 2, 3
_ENTRANCE_ROOM = 0  # convenzione: la prima stanza creata e l'ingresso
_LONG_CORRIDOR_THRESHOLD = 12  # quadretti = 60 ft, oltre la scurovisione comune


def _bfs_distances(graph: dict, start: int) -> dict:
    dist = {start: 0}
    queue = [start]
    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        for neighbor in graph.get(node, []):
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist


def _mark_tactical_rooms(blueprint: Blueprint) -> None:
    """Stanze di grado >= 3: nodi tattici che furnish deve coprire con
    colonne/casse (SPEC.md §9.1). Congelato SUBITO dopo albero+anelli,
    prima delle porte segrete: una scorciatoia nascosta non deve far
    scattare la copertura tattica su una stanza altrimenti lineare."""
    blueprint.tactical_rooms = sorted(
        i for i in range(len(blueprint.rooms)) if len(blueprint.graph.get(i, [])) >= 3
    )


def _reproject_doors(room: Room, old_rect: Rect) -> None:
    """Riporta ogni porta al punto assoluto che occupava con `old_rect`.

    Door.t e una frazione del muro su cui la porta e appoggiata, quindi
    dipende dalla LUNGHEZZA di quel muro. Allargare una stanza sui lati
    perpendicolari non sposta il lato che porta la porta, ma lo allunga, e
    la porta scivola via insieme a lui: nel gate M3 (TASK-26) la porta della
    stanza boss e finita a mezzo quadretto dal corridoio che ci arrivava,
    lasciando un moncone di muro in mezzo al passaggio."""
    for door in room.doors:
        (x0, y0), (x1, y1) = _side_corners(old_rect, door.wall_index)
        point = (x0 + (x1 - x0) * door.t, y0 + (y1 - y0) * door.t)
        door.t = _t_on_side(room.rect, door.wall_index, point)


def _enlarge_room(blueprint: Blueprint, room_index: int, margins=(3, 2, 1)) -> bool:
    """Ingrandisce room_index solo sui lati SENZA porte, e riproietta le
    porte esistenti sul nuovo perimetro perche restino dove sono in
    coordinate assolute (la loro posizione e gia stata proiettata su
    corridoi e stanze vicine: se si spostano, si disallineano). Prova
    margini decrescenti; se nessuno entra nel
    canvas senza sovrapporsi ad altre stanze o ai corridoi gia tracciati,
    lascia la stanza com'e.

    I corridoi contano come ostacoli quanto le stanze: allargarsi sopra un
    corridoio di passaggio produce esattamente il difetto segnalato nel
    gate M3, un corridoio che finisce dentro una stanza (TASK-26)."""
    room = blueprint.rooms[room_index]
    occupied = {d.wall_index for d in room.doors}
    rect = room.rect

    for margin in margins:
        x1 = max(1, rect.x1 - (0 if _LEFT in occupied else margin))
        y1 = max(1, rect.y1 - (0 if _TOP in occupied else margin))
        x2 = min(blueprint.width - 1, rect.x2 + (0 if _RIGHT in occupied else margin))
        y2 = min(blueprint.height - 1, rect.y2 + (0 if _BOTTOM in occupied else margin))
        if x2 - x1 <= rect.w and y2 - y1 <= rect.h:
            continue  # il clamp al canvas ha vanificato l'espansione
        candidate = Rect(x1, y1, x2, y2)
        collides = any(
            i != room_index and candidate.overlaps(blueprint.rooms[i].rect, margin=1)
            for i in range(len(blueprint.rooms))
        ) or any(_overlap_area(candidate, corridor) for corridor in blueprint.corridors)
        if not collides:
            room.rect = candidate
            _reproject_doors(room, rect)
            return True
    return False


def _assign_boss_room(blueprint: Blueprint) -> None:
    """La stanza piu lontana dall'ingresso (grafo, non distanza euclidea)
    diventa il boss: kind='boss' e dimensione maggiorata quando possibile."""
    if not blueprint.rooms:
        return
    dist = _bfs_distances(blueprint.graph, _ENTRANCE_ROOM)
    boss_index = max(
        range(len(blueprint.rooms)),
        key=lambda i: (dist.get(i, -1), -i),  # pareggio -> indice piu basso, riproducibile
    )
    blueprint.rooms[boss_index].kind = "boss"
    _enlarge_room(blueprint, boss_index)


def _add_secret_doors(blueprint: Blueprint, corridor_width: float) -> None:
    """Le stanze di grado 1 (vicoli ciechi sul percorso principale)
    ricevono una porta segreta verso la stanza libera piu vicina, cosi
    diventano raggiungibili anche da un percorso diverso da quello
    principale (SPEC.md §9.1).

    Fra i candidati, in ordine di distanza, si prende il primo che si
    raggiunge senza passare dentro una terza stanza: una scorciatoia
    nascosta e un extra, e non vale un cunicolo che sbuca in mezzo al
    pavimento di qualcun altro. Se nessun candidato e pulito, il vicolo
    cieco resta tale (gate umano M3, TASK-26)."""
    rooms = blueprint.rooms
    graph = blueprint.graph
    n = len(rooms)
    dead_ends = sorted(i for i in range(n) if len(graph.get(i, [])) == 1)

    for i in dead_ends:
        already_connected = set(graph.get(i, [])) | {i}
        candidates = sorted(
            (j for j in range(n) if j not in already_connected),
            key=lambda j: (
                math.hypot(*(c1 - c2 for c1, c2 in zip(rooms[i].rect.center(), rooms[j].rect.center()))),
                j,
            ),
        )
        for j in candidates:
            if _connect_rooms(
                rooms, i, j, blueprint.corridors, corridor_width,
                kind="secret", require_clean=True,
            ):
                graph[i].append(j)
                graph[j].append(i)
                break


def _mark_long_corridors(blueprint: Blueprint) -> None:
    """Corridoi oltre 12 quadretti (60 ft, SPEC.md §9.1): furnish ci mette
    una fonte di luce a meta. Calcolato per ultimo, dopo ogni passaggio che
    puo aggiungere corridoi (porte segrete comprese)."""
    blueprint.long_corridor_indices = [
        i for i, rect in enumerate(blueprint.corridors)
        if max(rect.w, rect.h) > _LONG_CORRIDOR_THRESHOLD
    ]


def generate(*, width: int, height: int, seed: int,
             rooms: int = 8, min_room: int = 3, max_room: int = 10,
             corridor_width: float = 1.0, loops: float = 0.15,
             depth_max: int = 8, **params) -> Blueprint:
    """Genera un dungeon a stanze. Parametri per SPEC.md §9.1."""
    rng = random.Random(seed)
    root_rect = Rect(1, 1, width - 1, height - 1)

    tree_root, leaves = _build_tree(
        root_rect, rng, rooms_target=rooms, max_room=max_room, depth_max=depth_max
    )

    blueprint_rooms: list[Room] = []
    for i, leaf in enumerate(leaves):
        room_rect = _inscribe_room(leaf.rect, rng, min_room)
        blueprint_rooms.append(Room(rect=room_rect, kind="sala"))
        leaf.room_index = i

    graph: dict[int, list[int]] = {i: [] for i in range(len(blueprint_rooms))}
    corridors: list[Corridor] = []
    _connect_subtree(tree_root, blueprint_rooms, graph, corridors, corridor_width)
    _add_loop_connections(blueprint_rooms, graph, corridors, rng, loops, corridor_width)

    blueprint = Blueprint(
        width=width, height=height,
        rooms=blueprint_rooms, corridors=corridors,
        graph=graph, seed=seed, style="dungeon",
    )

    # Semantica D&D (TASK-22), in quest'ordine: i nodi tattici e il boss si
    # basano sul grafo "visibile" prima delle scorciatoie segrete; i
    # corridoi lunghi si scandiscono per ultimi perche le porte segrete
    # possono aggiungerne altri.
    _mark_tactical_rooms(blueprint)
    _assign_boss_room(blueprint)
    _add_secret_doors(blueprint, corridor_width)
    _mark_long_corridors(blueprint)

    return blueprint
