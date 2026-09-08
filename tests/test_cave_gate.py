"""Regressione del gate umano M5 per lo stile cave (TASK-36).

Round 1 — Jay ha aperto generated/cave_m5.dungeondraft_map (80x80, seed
1337) e il risultato non era utilizzabile: "La cave è molto sparsa. Le
mappe delle caverne perché siano utili devono comunque essere delle sorte
di 'stanze', anche irregolari, collegate tra di loro."

Diagnosi (vedi generators/cave.py, TASK-44): a fill_prob=0.45/iterations=5
la componente aperta principale del cellular automata sopravviveva come
un'unica area sprawling che copriva gran parte della mappa (69% a 80x80),
non un insieme di camere leggibili — nessuna soglia sui "componenti
secondari" poteva correggerlo, perche il problema era la forma della
componente PRINCIPALE, mai filtrata.

Corretto ricalibrando fill_prob/iterations cosi che il CA si frammenti
sempre in piu camere indipendenti dalla scala della mappa (verificato su
24x18 e 80x80), e collegandole TUTTE con un albero di copertura minimo
invece che "verso la principale".

Round 2 — Jay, sul file corretto: "il file della grotta va meglio ma
mancano delle 'stanze' più ampie. Sembrano tutti dei corridoi." Misurato:
il rapporto area/bounding-box delle camere restava ~0.30-0.45 qualunque
fossero fill_prob (0.50-0.72) o iterations (5-40) — intrinseco alla regola
B5/S4, non un problema di parametri. Corretto con un'apertura morfologica
(erosione poi dilatazione, `_extract_rooms`) che isola solo i nuclei
davvero larghi prima del collegamento dei tunnel.

Round 3 — Jay, sul file corretto: "le stanze sono ancora troppo piccole
rispetto alla lunghezza dei corridoi." Le camere isolate dal round 2 erano
larghe ma piccole (4-14 quadretti) e rade (copertura ~1-2% della mappa),
quindi i tunnel fra loro risultavano lunghi in proporzione. Corretto
abbassando fill_prob (0.57->0.48, blob grezzi piu grandi in partenza) e
alzando il raggio dell'apertura (2->3 sotto-celle, per arrotondarli
comunque) e la soglia minima (4->15 quadretti): camere molto piu grandi
(15-55 quadretti) e copertura 9-13% della mappa — piu vicine fra loro, con
tunnel proporzionalmente piu corti.

Round 4 — Jay, sul file corretto: "meglio, ma alcune stanze possono essere
molto più grandi." Non serviva alzare il pavimento (le camere piccole
andavano bene), serviva allungare la coda verso l'alto: fill_prob
riportato a 0.45 (blob di partenza ancora piu grandi — e' lo STESSO
fill_prob del round 1, ma ora l'apertura morfologica lo spezza comunque in
decine di camere, il meccanismo di fix non e' piu quello) e raggio
dell'apertura alzato a 4 (per arrotondarli comunque). Stessa camera minima
di prima (15 quadretti), ma il massimo sale da ~55 a ~130 quadretti — piu
varieta di taglia, nessuna camera che pero' domina il totale (misurato:
la piu grande non supera mai l'11% dell'area totale delle camere).

Round 5 — Jay, sul file corretto: "ci siamo quasi. l'ottimo sarebbe che ci
fossero almeno un paio di stanze molto grandi." La coda del round 4 era
naturale (dipendeva dal seed, non garantita), e comunque non abbastanza
lunga. Aggiunta una seconda estrazione dedicata (`_GRAND_COUNT=2`
camere), con un'apertura piu gentile (`_GRAND_RADIUS=3` invece dello
standard 4: eroso meno, trattiene piu area) sulla STESSA griglia grezza —
non un algoritmo diverso, solo meno aggressiva sulle 2 camere che
sopravvivono piu grandi. Risultato: sempre almeno 2 camere di 150+
quadretti (contro il tetto naturale di ~130 del round 4), ancora larghe in
entrambe le dimensioni (mai sotto ~14 quadretti di lato, verificato sulle
bounding box — non il regime "corridoio" del round 2 nonostante un
rapporto area/bounding-box piu basso, atteso su un contorno cosi esteso).
"""

import random

from ddforge.cave_bitmap import cave_grid_shape
from ddforge.generators import cave
from ddforge.generators.cave import _initial_grid, _label_components, _smooth

_SEEDS = (1, 2, 3, 1337, 42)


def _rooms_after_opening(width, height, seed):
    """Le camere finali (dopo `_extract_rooms`, prima dei tunnel di
    collegamento) per un seed a scala di produzione: la base comune a
    quasi tutti i test di questo file."""
    rng = random.Random(seed)
    grid_w, grid_h = cave_grid_shape(width, height)
    grid = _initial_grid(grid_w, grid_h, rng, cave._FILL_PROB)
    for _ in range(cave._ITERATIONS):
        grid = _smooth(grid, grid_w, grid_h)
    rooms_grid = cave._extract_rooms(
        grid, grid_w, grid_h, radius=cave._OPEN_RADIUS, min_room_size=cave._MIN_COMPONENT_SIZE,
        grand_radius=cave._GRAND_RADIUS, grand_count=cave._GRAND_COUNT,
    )
    return _label_components(rooms_grid, grid_w, grid_h)


def test_no_single_room_dominates_the_total_room_area():
    """Il difetto originale (round 1): a fill_prob=0.45 SENZA apertura
    morfologica, un'unica componente copriva il 69% della mappa — non un
    insieme di camere, una sola area sprawling. Dal round 4 fill_prob e'
    tornato a 0.45 (per camere di taglia massima piu alta, vedi sopra), ma
    ora e' l'apertura a garantire che nessuna camera FINALE domini le
    altre: misurato che la piu grande non supera mai l'11% dell'area
    totale delle camere su 7 seed. Soglia larga apposta (30%): guardia
    contro un ritorno al regime "un blob sprawling e basta", non contro la
    variabilita' di taglia che il round 4 chiede esplicitamente."""
    for seed in _SEEDS:
        rooms = _rooms_after_opening(80, 80, seed)
        assert rooms, f"seed {seed}: nessuna camera estratta"
        sizes = sorted((len(r) for r in rooms), reverse=True)
        total = sum(sizes)
        assert sizes[0] / total < 0.30, (
            f"seed {seed}: la camera piu grande copre {sizes[0] / total:.1%} dell'area totale "
            f"delle camere, troppo vicino alla singola area sprawling segnalata da Jay"
        )


def test_cave_produces_multiple_distinct_rooms_at_production_scale():
    """'devono comunque essere delle sorte di stanze ... collegate tra di
    loro': serve piu di una camera, altrimenti non c'e nulla da collegare.

    Conta le camere DOPO l'apertura morfologica (`_extract_rooms`), non i
    componenti grezzi del CA: dal round 3 la soglia (15 quadretti) e'
    tarata sulle camere gia' aperte/larghe, non sui frammenti grezzi."""
    for seed in _SEEDS:
        rooms = _rooms_after_opening(80, 80, seed)
        assert len(rooms) >= 3, f"seed {seed}: solo {len(rooms)} camere sopra la soglia minima"


def test_cave_rooms_have_a_wide_size_range():
    """'alcune stanze possono essere molto più grandi': non basta che le
    camere siano larghe (round 2) e vicine (round 3), serve varieta' di
    taglia — la piu grande deve essere un multiplo netto della piu
    piccola, non un gruppo uniforme. Soglia (3x) ben sotto il rapporto
    misurato (~5-9x su 7 seed: minimo sempre ~15 quadretti per costruzione
    — la soglia — massimo 73-132 quadretti)."""
    for seed in _SEEDS:
        rooms = _rooms_after_opening(80, 80, seed)
        sizes = sorted(len(r) for r in rooms)
        assert sizes[-1] / sizes[0] >= 3.0, (
            f"seed {seed}: camera piu grande {sizes[-1] / 16:.1f} quadretti, "
            f"piu piccola {sizes[0] / 16:.1f} — poca varieta' di taglia"
        )


def test_at_least_two_rooms_are_grand_caverns():
    """'l'ottimo sarebbe che ci fossero almeno un paio di stanze molto
    grandi': non basta la coda naturale del round 4 (dipendeva dal seed),
    servono almeno 2 camere marcatamente piu grandi delle altre — e
    comunque larghe in entrambe le dimensioni, non solo estese (altrimenti
    e' di nuovo il regime 'corridoio' del round 2, solo piu grande).

    Soglia (150 quadretti) ben sopra il tetto naturale del round 4 (~130,
    senza `_GRAND_COUNT`/`_GRAND_RADIUS`) e ben sotto il minimo osservato
    col fix (150-450 quadretti su 7 seed); soglia sulla bounding box (10
    quadretti di lato) per escludere corridoi enormi ma stretti."""
    for seed in _SEEDS:
        rooms = _rooms_after_opening(80, 80, seed)
        grand = 0
        for room in rooms:
            if len(room) < 150 * 16:
                continue
            xs = [p[0] for p in room]
            ys = [p[1] for p in room]
            bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
            if min(bw, bh) >= 10 * 4:
                grand += 1
        assert grand >= 2, f"seed {seed}: solo {grand} camere >= 150 quadretti e larghe in entrambe le dimensioni"


def test_cave_rooms_are_wide_not_corridor_shaped():
    """'mancano delle stanze più ampie. Sembrano tutti dei corridoi.' Le
    camere isolate da `_extract_rooms` (dopo l'apertura morfologica, prima
    dei tunnel di collegamento) devono riempire in MEDIA una parte
    consistente del proprio bounding box — una forma larga — non restare
    sottili e serpeggianti come un corridoio.

    Media per seed, non un minimo per singola camera: alcune camere vicine
    alla soglia hanno forme meno rotonde, un rumore normale; e' la media
    che separa nettamente i due regimi — ~0.35 senza apertura (round 1),
    ~0.66-0.71 con l'apertura (round 4, misurato su 7 seed, minimo
    osservato 0.66)."""
    for seed in _SEEDS:
        rooms = _rooms_after_opening(80, 80, seed)
        assert rooms, f"seed {seed}: nessuna camera estratta"
        ratios = []
        for room in rooms:
            xs = [p[0] for p in room]
            ys = [p[1] for p in room]
            bbox_area = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
            ratios.append(len(room) / bbox_area)
        avg_ratio = sum(ratios) / len(ratios)
        assert avg_ratio >= 0.55, (
            f"seed {seed}: rapporto area/bounding-box medio {avg_ratio:.0%} sulle {len(rooms)} "
            f"camere, troppo vicino al regime 'corridoio' segnalato da Jay (~35% senza apertura)"
        )


def test_all_rooms_end_up_in_a_single_connected_network():
    """Le camere devono essere collegate FRA LORO (non solo raggiungibili
    dalla piu grande): dopo lo scavo dei tunnel resta una sola componente
    connessa, qualunque sia la topologia delle camere di partenza."""
    for seed in _SEEDS:
        blueprint = cave.generate(width=80, height=80, seed=seed)
        assert blueprint.cave_grid is not None
        grid_w, grid_h = cave_grid_shape(80, 80)
        rock_grid = [[1 - v for v in row] for row in blueprint.cave_grid]
        components = _label_components(rock_grid, grid_w, grid_h)
        assert len(components) == 1, f"seed {seed}: {len(components)} componenti dopo lo scavo dei tunnel"
