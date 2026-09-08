"""Fognature: griglia di canali ortogonali e camere di giunzione circolari.

Variante del generatore di grotte descritta in SPEC.md §9.3. A differenza di
cave.py (layer `cave` nativo, niente palette, TASK-32/decision-1), qui la
palette sewer disegna muri/pavimenti/porte veri (compose.render_sewer_blueprint):
per questo vive in un modulo suo, gia annotato in cave.py durante TASK-32,
anche se SPEC.md raggruppa le due varianti nella stessa sezione.
"""

import math
import random

from ddforge.model import Blueprint, Chamber, Corridor

_SPACING = 8.0  # quadretti fra due nodi della griglia (centri delle camere)
_CANAL_WIDTH = 2.0
_CHAMBER_RADIUS = 1.5
# Probabilita' di riaggiungere, dopo l'albero di copertura, un arco altrimenti
# scartato: senza, la rete sarebbe un albero puro (comunque connesso, AC1,
# ma senza anelli). Valore non fissato da SPEC.md, scelto e documentato qui
# come i parametri equivalenti di cave.py (TASK-32): abbastanza per qualche
# anello senza avvicinarsi alla griglia completa.
_EXTRA_LOOP_PROB = 0.15


def _grid_dims(width: float, height: float, spacing: float, margin: float) -> tuple[int, int]:
    """Numero di nodi per asse: almeno 2, cosi c'e sempre almeno un arco."""
    nx = max(2, int((width - 2 * margin) // spacing) + 1)
    ny = max(2, int((height - 2 * margin) // spacing) + 1)
    return nx, ny


class _UnionFind:
    """Trova/unisce per il Kruskal randomizzato di _connected_edges."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.parent[ra] = rb
        return True


def _all_edges(nx: int, ny: int) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Ogni arco della griglia completa nx*ny, come coppie di nodi (i, j).
    Convenzione fissa: il primo nodo ha sempre indice (i o j) minore del
    secondo, mai il contrario (generate() la sfrutta per orientare i canali
    senza dover confrontare di nuovo gli indici)."""
    edges = []
    for j in range(ny):
        for i in range(nx):
            if i + 1 < nx:
                edges.append(((i, j), (i + 1, j)))
            if j + 1 < ny:
                edges.append(((i, j), (i, j + 1)))
    return edges


def _connected_edges(
    nx: int, ny: int, rng: random.Random, extra_loop_prob: float
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Albero di copertura casuale (Kruskal randomizzato sugli archi
    mescolati): la rete risultante e connessa per costruzione, qualunque
    seed (AC1) - non serve verificarlo a posteriori. Gli archi scartati
    dall'albero hanno comunque `extra_loop_prob` di probabilita' di essere
    riaggiunti, per dare alla rete degli anelli invece di restare un albero
    puro."""
    edges = _all_edges(nx, ny)
    rng.shuffle(edges)
    uf = _UnionFind(nx * ny)

    def node_id(node: tuple[int, int]) -> int:
        i, j = node
        return j * nx + i

    kept, discarded = [], []
    for a, b in edges:
        (kept if uf.union(node_id(a), node_id(b)) else discarded).append((a, b))

    for a, b in discarded:
        if rng.random() < extra_loop_prob:
            kept.append((a, b))
    return kept


def generate(
    *, width: int, height: int, seed: int,
    spacing: float = _SPACING, canal_width: float = _CANAL_WIDTH,
    chamber_radius: float = _CHAMBER_RADIUS, extra_loop_prob: float = _EXTRA_LOOP_PROB,
    **params,
) -> Blueprint:
    """Genera una rete di fognature (SPEC.md §9.3). RNG locale da `seed`
    (TASK-20): mai il modulo `random` globale. `width`/`height` in
    quadretti, come negli altri generatori.

    rooms/corridors non seguono il modello a stanze rettangolari: i canali
    sono comunque Corridor (un canale ortogonale e esattamente quello), ma
    le camere di giunzione circolari vivono in blueprint.chambers
    (model.Chamber), non in blueprint.rooms - stesso principio di
    Blueprint.cave_grid in TASK-32, un campo dedicato invece di forzare la
    geometria nel modello a stanze."""
    rng = random.Random(seed)
    margin = chamber_radius + 1.0
    nx, ny = _grid_dims(width, height, spacing, margin)
    xs = [margin + i * spacing for i in range(nx)]
    ys = [margin + j * spacing for j in range(ny)]

    edges = _connected_edges(nx, ny, rng, extra_loop_prob)

    connected: dict[tuple[int, int], set] = {(i, j): set() for j in range(ny) for i in range(nx)}
    for (i1, j1), (i2, j2) in edges:
        if i2 > i1:
            connected[(i1, j1)].add("E")
            connected[(i2, j2)].add("W")
        else:
            connected[(i1, j1)].add("S")
            connected[(i2, j2)].add("N")

    # Convenzione (bsp._ENTRANCE_ROOM): il nodo d'angolo (0, 0) e sempre
    # l'ingresso. E' un angolo della griglia completa, quindi ha al massimo
    # 2 lati collegati (E, S): resta sempre almeno un arco libero per la
    # porta (draw_chamber), qualunque seed.
    entrance = (0, 0)

    chambers = []
    index_of = {}
    for j in range(ny):
        for i in range(nx):
            index_of[(i, j)] = len(chambers)
            chambers.append(Chamber(
                center=(xs[i], ys[j]), radius=chamber_radius,
                connected=frozenset(connected[(i, j)]), door=((i, j) == entrance),
            ))

    depth = math.sqrt(chamber_radius**2 - (canal_width / 2) ** 2)
    half = canal_width / 2
    corridors = []
    for (i1, j1), (i2, j2) in edges:
        x1, y1 = xs[i1], ys[j1]
        x2, y2 = xs[i2], ys[j2]
        if j1 == j2:  # arco orizzontale, x1 < x2 per convenzione di _all_edges
            corridors.append(Corridor(x1 + depth, y1 - half, x2 - depth, y1 + half, horizontal=True))
        else:  # arco verticale, y1 < y2
            corridors.append(Corridor(x1 - half, y1 + depth, x1 + half, y2 - depth, horizontal=False))

    graph: dict[int, list[int]] = {index_of[node]: [] for node in index_of}
    for a, b in edges:
        graph[index_of[a]].append(index_of[b])
        graph[index_of[b]].append(index_of[a])

    return Blueprint(
        width=width, height=height,
        rooms=[], corridors=corridors, graph=graph,
        seed=seed, style="sewer",
        chambers=chambers,
    )
