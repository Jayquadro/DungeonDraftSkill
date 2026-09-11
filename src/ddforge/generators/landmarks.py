"""Catalogo degli elementi urbani notevoli e loro estrazione (TASK-48).

Questo modulo non piazza nulla: dichiara QUALI luoghi esistono, a quale scala
hanno senso, quanti ce ne stanno e con quale regola vanno collocati. Il
piazzamento vero (che ha bisogno di lotti, isolati, mura, fiume e porto) sta
in generators/city.py.

Le tre domande difficili del task sono tre campi di LandmarkKind, non tre
paragrafi di commento:

- QUANTI (AC4): `unique` per i luoghi che una citta' ha in copia unica
  (palazzo del signore, cattedrale, arena), `rate` per quelli comuni. `rate`
  e' un numero di istanze PER EDIFICIO generato, mai un valore assoluto: e'
  cosi' che un quartiere piccolo non si ritrova tre arene e una citta' intera
  non si ritrova una sola taverna. `max_count` e' solo la rete di sicurezza
  contro le mappe enormi.
- A QUALE SCALA (AC3): `scales`. Un fornaio si vede al preset "isolato", dove
  la bottega e' un edificio a stanze; su una mappa di citta' intera si
  segnano cattedrale, palazzo, mura, porto e mercati, non le panetterie. Un
  kind non ammissibile per il preset scelto non viene MAI piazzato, e
  chiederlo esplicitamente e' un errore esplicito (vedi select), non
  un'omissione silenziosa.
- DOVE (AC5): `rule`. Le regole valgono molto piu' della varieta': una dogana
  alle porte e una conceria a valle del fiume rendono la mappa leggibile,
  perche' riproducono una zonizzazione che chi guarda la mappa riconosce. Un
  kind con una regola che non trova sito non viene piazzato ALTROVE: viene
  saltato. E' cosi' che AC5 resta un invariante verificabile ("se e' sulla
  mappa, allora la regola vale") invece di una tendenza statistica.

Fuori dall'inventario della descrizione del task, per scelta e non per
dimenticanza: gli elementi che non sono un ingombro con un nome (chiusini
delle fognature sulle strade, edicole votive, fossato/bastioni/barbacane come
corredo delle mura, ponte coperto e guado come varianti dell'attraversamento)
non hanno un sito nel modello a lotti/isolati/fasce usato qui e chiederebbero
un tipo di sito proprio. Sono un'aggiunta incrementale a questo catalogo, non
una riprogettazione.
"""

import random
from dataclasses import dataclass

# Siti da cui puo' essere ricavato l'ingombro di un luogo. Non sono un
# dettaglio di rendering: dicono a city.py DOVE cercare spazio, ed e' la
# ragione per cui nessun luogo puo' finire in mezzo a una strada (un lotto e
# un isolato non toccano mai l'ingombro riservato a una via, per costruzione
# della partizione — vedi city._build_blocks).
SITE_LOT = "lot"  # un lotto edificabile: il luogo prende il posto della casa
SITE_BLOCK = "block"  # un isolato intero: monasteri, arene, cattedrali
SITE_PLAZA = "plaza"  # una porzione di piazza: mercato, patibolo, statue
SITE_BAND = "band"  # fascia extramurale o banchina del porto

# Regole di piazzamento (AC5). "any" e' l'unica che non vincola nulla.
RULE_ANY = "any"
RULE_GATE = "gate"  # a ridosso di una porta delle mura
RULE_RIVER = "river"  # sulla riva del fiume
RULE_RIVER_DOWNSTREAM = "river_downstream"  # sulla riva, nella meta' a valle
RULE_OUTSIDE_WALLS_OR_TEMPLE = "outside_walls_or_temple"
RULE_PLAZA = "plaza"  # su una qualunque piazza
RULE_MAIN_PLAZA = "main_plaza"  # sulla piazza principale (la piu' grande)
# Sulla banchina. Dopo la scelta di Jay sul campionario ci resta il solo
# faro: cantiere navale e mercato del pesce sono stati tolti dal catalogo
# perche' non gli interessavano. Il porto continua a esistere come struttura
# (l'acqua e la banchina ridisegnano il bordo della mappa) e il faro basta a
# rendere la regola verificabile.
RULE_PORT = "port"
RULE_EDGE = "edge"  # ai margini: fuori le mura se ci sono, sul bordo altrimenti

ISOLATO, QUARTIERE, CITTA = "isolato", "quartiere", "citta"
_ALL_SCALES = frozenset({ISOLATO, QUARTIERE, CITTA})
_BIG = frozenset({QUARTIERE, CITTA})


@dataclass(frozen=True)
class LandmarkKind:
    """Una voce del catalogo. Vedi la nota di modulo per i tre campi che
    contano (scales, unique/rate, rule)."""

    key: str
    label: str
    scales: frozenset
    site: str
    rule: str = RULE_ANY
    unique: bool = False
    # Solo per unique: probabilita' che il luogo compaia se non e' stato
    # chiesto esplicitamente. Alta per il nucleo civico (una citta' HA un
    # palazzo e una cattedrale), media per il resto: e' da qui che due seed
    # diversi danno citta' con luoghi diversi (AC2).
    chance: float = 0.6
    # Solo per i comuni: istanze per edificio generato (AC4). 0.04 = una
    # taverna ogni 25 edifici.
    rate: float = 0.0
    max_count: int = 1
    # Ingombro-bersaglio in MULTIPLI del lotto medio del preset: un luogo
    # importante occupa piu' lotti affiancati. Ignorato dai siti "block".
    lots: float = 1.0
    # Uno spiazzo, non un edificio: mercato, cimitero, fiera, giardino,
    # patibolo. Cambia il disegno (sprite sparsi invece di uno solo che
    # riempie l'ingombro) e, al preset "isolato", il fatto che non venga
    # generato nessun Blueprint a stanze per quel luogo.
    open_air: bool = False
    # Solo per open_air: lato lungo di UN pezzo sparso, in quadretti (1
    # quadretto = 1,5 m). E' il generatore a dire quanto e' grande un albero o
    # una lapide, non lo sprite.
    #
    # Perche' non ci si puo' fidare della dimensione nativa: i pack sono
    # disegnati a scale diverse fra loro. `tree1` di City Terrain e' nativo
    # 0,3 quadretti (45 cm: un alberello) perche' quel pack e' fatto per
    # mappe di regione, mentre una chioma vera ne misura tre. Disegnati a
    # dimensione nativa gli alberi di un parco venivano puntini - visto sul
    # foglio di confronto delle aree.
    piece_size: float = 1.5
    # Solo per open_air: che terreno si stende sotto gli sprite sparsi.
    # Chiave di Palette.floors, o None per lasciare il terreno della mappa.
    # Un mercato sta su un selciato, un parco sull'erba, una fiera sulla terra
    # battuta: dare a tutti la stessa pavimentazione urbana era il motivo per
    # cui un cimitero sembrava un piazzale.
    ground: str | None = None


# Strutture urbane. Non sono luoghi da visitare ma la forma della citta': le
# mura riducono l'area edificabile, il fiume toglie gli edifici che
# attraversa, il porto sottrae una fascia di canvas. Vanno decise PRIMA degli
# edifici, ed e' rispetto a loro che si verificano le regole di AC5 — per
# questo stanno in un catalogo separato e non fra i LandmarkKind.
#
# Solo il fiume e' ammesso al preset "isolato": una cinta muraria e un porto
# sono elementi di scala urbana, e un anello murario dentro un singolo isolato
# sarebbe un recinto, non una citta' fortificata.
STRUCTURE_SCALES: dict[str, frozenset] = {
    "mura": _BIG,
    "fiume": _ALL_SCALES,
    "porto": _BIG,
}
STRUCTURE_CHANCE: dict[str, float] = {
    "mura": 0.7,
    "fiume": 0.55,
    # Una citta' su tre e' costiera o fluviale abbastanza da avere un porto:
    # tenerlo raro e' cio' che rende il porto un tratto distintivo di quella
    # mappa invece dell'ennesimo elemento sempre presente.
    "porto": 0.35,
}


# Ordine significativo: un kind puo' dipendere da un kind piazzato prima
# (il cimitero cerca il tempio, vedi RULE_OUTSIDE_WALLS_OR_TEMPLE), e i
# vincolati vanno serviti prima dei liberi, altrimenti i luoghi "any" si
# prendono i lotti buoni e alla dogana non resta un lotto vicino alla porta.
LANDMARK_KINDS: tuple[LandmarkKind, ...] = (
    # --- vincolati da una regola: prima di tutti -------------------------
    LandmarkKind(
        "dogana", "Dogana", _BIG, SITE_LOT, RULE_GATE,
        rate=0.006, max_count=4,  # una per porta: le porte sono al piu' quattro
    ),
    LandmarkKind(
        "torre_guardia", "Torre di Guardia", _BIG, SITE_LOT, RULE_GATE,
        rate=0.008, max_count=4,
    ),
    LandmarkKind(
        "mulino", "Mulino ad Acqua", _ALL_SCALES, SITE_LOT, RULE_RIVER,
        unique=True, chance=0.8, lots=1.5,
    ),
    LandmarkKind(
        "conceria", "Conceria", _ALL_SCALES, SITE_LOT, RULE_RIVER_DOWNSTREAM,
        unique=True, chance=0.75,
    ),
    LandmarkKind(
        "macello", "Macello", _BIG, SITE_LOT, RULE_RIVER_DOWNSTREAM,
        unique=True, chance=0.5,
    ),
    LandmarkKind(
        "faro", "Faro", _BIG, SITE_BAND, RULE_PORT, unique=True, chance=0.7,
    ),
    LandmarkKind(
        "mercato", "Piazza del Mercato", _ALL_SCALES, SITE_PLAZA, RULE_PLAZA,
        unique=True, chance=0.9, lots=2.0, open_air=True, ground="selciato",
        piece_size=2.0,  # un banco con la sua tenda, 3 m
    ),
    LandmarkKind(
        "patibolo", "Patibolo", _ALL_SCALES, SITE_PLAZA, RULE_MAIN_PLAZA,
        unique=True, chance=0.55, open_air=True, ground="selciato",
        piece_size=2.0,  # la forca
    ),
    # --- nucleo civico e religioso: unici, quasi sempre presenti ---------
    # I quattro monumenti (cattedrale, palazzo, arena, monastero) occupano
    # piu' isolati adiacenti: e' quello che li fa leggere come monumenti alla
    # scala "citta", dove un isolato solo vale due o tre case.
    LandmarkKind(
        "tempio", "Tempio", _ALL_SCALES, SITE_LOT, unique=True, chance=0.85, lots=2.0,
    ),
    LandmarkKind(
        "cattedrale", "Cattedrale", _BIG, SITE_BLOCK, unique=True, chance=0.8,
    ),
    LandmarkKind(
        "palazzo", "Palazzo del Signore", _BIG, SITE_BLOCK, unique=True, chance=0.9,
    ),
    LandmarkKind(
        "municipio", "Municipio", _BIG, SITE_LOT, RULE_PLAZA,
        unique=True, chance=0.75, lots=1.5,
    ),
    LandmarkKind(
        "caserma", "Caserma della Guardia", _ALL_SCALES, SITE_LOT,
        unique=True, chance=0.8, lots=1.5,
    ),
    LandmarkKind(
        "prigione", "Prigione", _BIG, SITE_LOT, unique=True, chance=0.5,
    ),
    LandmarkKind(
        "monastero", "Monastero", _BIG, SITE_BLOCK, RULE_EDGE, unique=True, chance=0.45,
    ),
    LandmarkKind(
        "arena", "Arena", frozenset({CITTA}), SITE_BLOCK, unique=True, chance=0.45,
    ),
    LandmarkKind(
        "teatro", "Teatro", _BIG, SITE_LOT, unique=True, chance=0.4, lots=1.5,
    ),
    # --- sapere ----------------------------------------------------------
    LandmarkKind(
        "biblioteca", "Biblioteca", _ALL_SCALES, SITE_LOT, unique=True, chance=0.55,
    ),
    LandmarkKind(
        "accademia", "Accademia di Magia", _BIG, SITE_BLOCK, unique=True, chance=0.35,
    ),
    LandmarkKind(
        "alchimista", "Bottega dell'Alchimista", frozenset({ISOLATO, QUARTIERE}),
        SITE_LOT, rate=0.012, max_count=3,
    ),
    # --- commercio -------------------------------------------------------
    LandmarkKind(
        "banca", "Casa di Cambio", _BIG, SITE_LOT, RULE_PLAZA, unique=True, chance=0.5,
    ),
    LandmarkKind(
        "magazzino", "Magazzino", frozenset({ISOLATO, QUARTIERE}), SITE_LOT,
        rate=0.03, max_count=8,
    ),
    LandmarkKind(
        "gilda", "Sede di Gilda", _BIG, SITE_LOT, rate=0.008, max_count=4,
    ),
    # --- svago e servizi -------------------------------------------------
    LandmarkKind(
        "taverna", "Taverna", frozenset({ISOLATO, QUARTIERE}), SITE_LOT,
        rate=0.04, max_count=12,
    ),
    LandmarkKind(
        "locanda", "Locanda", frozenset({ISOLATO, QUARTIERE}), SITE_LOT,
        rate=0.02, max_count=6,
    ),
    LandmarkKind(
        "bordello", "Casa di Piacere", frozenset({ISOLATO, QUARTIERE}), SITE_LOT,
        rate=0.008, max_count=2,
    ),
    LandmarkKind(
        "bagni", "Bagni Pubblici", _BIG, SITE_LOT, unique=True, chance=0.4, lots=1.5,
    ),
    LandmarkKind(
        "lazzaretto", "Lazzaretto", _BIG, SITE_BAND, RULE_EDGE, unique=True, chance=0.4,
    ),
    # --- artigianato -----------------------------------------------------
    LandmarkKind(
        "fabbro", "Fabbro", frozenset({ISOLATO, QUARTIERE}), SITE_LOT,
        rate=0.025, max_count=6,
    ),
    LandmarkKind(
        "stalle", "Stalle e Maniscalco", frozenset({ISOLATO, QUARTIERE}), SITE_LOT,
        rate=0.016, max_count=4,
    ),
    LandmarkKind(
        "fornaio", "Fornaio", frozenset({ISOLATO}), SITE_LOT, rate=0.03, max_count=4,
    ),
    LandmarkKind(
        "macelleria", "Macelleria", frozenset({ISOLATO}), SITE_LOT,
        rate=0.02, max_count=3,
    ),
    # --- struttura urbana minore ----------------------------------------
    LandmarkKind(
        "statua", "Statua", _ALL_SCALES, SITE_PLAZA, RULE_PLAZA,
        rate=0.01, max_count=3, open_air=True, piece_size=1.5,
    ),
    LandmarkKind(
        "giardino", "Giardino Pubblico", _BIG, SITE_BLOCK,
        rate=0.004, max_count=3, open_air=True, ground="verde",
        piece_size=3.0,  # una chioma d'albero, 4,5 m
    ),
    LandmarkKind(
        "cimitero", "Cimitero", _ALL_SCALES, SITE_BAND, RULE_OUTSIDE_WALLS_OR_TEMPLE,
        unique=True, chance=0.8, lots=2.5, open_air=True, ground="verde",
        piece_size=1.5,  # una lapide col suo tumulo
    ),
    LandmarkKind(
        "fiera", "Fiera", _BIG, SITE_BAND, RULE_EDGE,
        unique=True, chance=0.4, lots=2.5, open_air=True, ground="terra",
        piece_size=3.0,  # un tendone
    ),
)

BY_KEY: dict[str, LandmarkKind] = {kind.key: kind for kind in LANDMARK_KINDS}

# Tipologia di generators/building.py con cui disegnare un luogo NON open_air
# al preset "isolato", dove un edificio e' un Blueprint a stanze e non uno
# sprite. Non e' una decorazione: la tipologia decide la suddivisione interna,
# e una taverna divisa come un magazzino si riconosce subito. Le quattro
# tipologie esistenti bastano a coprire le quattro forme urbane ricorrenti
# (sala pubblica, edificio di rappresentanza, capannone, casa); i luoghi
# assenti da questa mappa ricadono su "house".
BUILDING_TYPE: dict[str, str] = {
    "taverna": "tavern", "locanda": "tavern", "bordello": "tavern",
    "palazzo": "manor", "cattedrale": "manor", "tempio": "manor",
    "municipio": "manor", "teatro": "manor", "biblioteca": "manor",
    "accademia": "manor", "banca": "manor", "monastero": "manor",
    "arena": "manor", "bagni": "manor",
    "magazzino": "warehouse", "dogana": "warehouse", "conceria": "warehouse",
    "macello": "warehouse", "mulino": "warehouse", "fabbro": "warehouse",
    "fornaio": "warehouse", "macelleria": "warehouse", "stalle": "warehouse",
    "caserma": "warehouse", "prigione": "warehouse", "lazzaretto": "warehouse",
}
BUILDING_TYPE_DEFAULT = "house"

# Tutto quello che `--landmark` accetta: luoghi piu' strutture. Le strutture
# passano dallo stesso parametro perche' dal punto di vista di chi genera la
# mappa "voglio un porto" e "voglio un tempio" sono la stessa richiesta.
REQUESTABLE: tuple[str, ...] = tuple(BY_KEY) + tuple(STRUCTURE_SCALES)

# Frazione massima di lotti che i luoghi COMUNI possono occupare. Senza, su
# una mappa grande le quote proporzionali sommate arrivano a spolpare il
# tessuto edilizio: una citta' fatta per meta' di botteghe con un cartello non
# ha piu' luoghi notevoli.
#
# Il tetto non vale per gli unici, ed e' una scelta: sono al piu' una ventina
# per costruzione (uno per kind) e sono esattamente quelli che rendono la
# citta' leggibile. Contandoli nel budget, su una mappa piccola le taverne e i
# magazzini estratti prima si mangiavano lo spazio del tempio e del cimitero -
# il contrario di quel che serve.
MAX_LANDMARK_FRACTION = 0.15
# Scarto casuale sulle quantita' dei luoghi comuni: senza, a parita' di numero
# di edifici due seed darebbero SEMPRE lo stesso numero di taverne (AC2).
_RATE_JITTER = 0.35


def scales_of(key: str) -> frozenset:
    """Preset a cui `key` (luogo o struttura) e' ammissibile."""
    if key in BY_KEY:
        return BY_KEY[key].scales
    if key in STRUCTURE_SCALES:
        return STRUCTURE_SCALES[key]
    raise ValueError(
        f"Elemento urbano sconosciuto: {key!r}. Elementi validi: {sorted(REQUESTABLE)}"
    )


def needs_frame(scale: str) -> bool:
    """Il preset ha bisogno che city.py riservi la fascia di margine?

    Serve solo se a questa scala esiste un luogo che ci vive davvero. Al
    preset "isolato" nessuno lo fa (il cimitero, unico luogo da fascia
    ammesso li', ricade sul ramo "presso il tempio" della sua regola quando
    non ci sono mura), quindi la fascia non viene riservata affatto e la
    geometria del preset gia' approvata al gate M5 resta invariata: e' meglio
    non toccare una taratura confermata da Jay per uno spazio che nessuno
    userebbe. Le mura, quando ci sono, chiedono la fascia comunque - e' la
    fascia extramurale."""
    return any(
        scale in kind.scales
        and kind.site == SITE_BAND
        and kind.rule not in (RULE_PORT, RULE_OUTSIDE_WALLS_OR_TEMPLE)
        for kind in LANDMARK_KINDS
    )


def check_requested(requested, scale: str) -> None:
    """Valida le richieste esplicite contro il preset scelto.

    Un elemento non ammissibile per il preset e' un ERRORE esplicito, non
    un'omissione silenziosa: AC1 dice che chiederlo deve funzionare e AC3 che
    non ammissibile non va mai piazzato, e le due cose si conciliano solo
    dicendo a chi genera la mappa che ha chiesto la scala sbagliata."""
    for key in requested:
        allowed = scales_of(key)
        if scale not in allowed:
            raise ValueError(
                f"L'elemento urbano {key!r} non e' ammissibile al preset di scala "
                f"{scale!r}: preset ammessi {sorted(allowed)}"
            )


def select_structures(*, scale: str, rng: random.Random, requested=()) -> set:
    """Strutture presenti sulla mappa: quelle chieste esplicitamente piu'
    quelle estratte a sorte fra le ammissibili al preset (AC1/AC2/AC3)."""
    requested = set(requested)
    chosen = set()
    for key, scales in STRUCTURE_SCALES.items():
        if scale not in scales:
            continue
        # rng consumato SEMPRE, anche per una struttura gia' richiesta: cosi'
        # chiedere un porto non sposta l'estrazione di mura e fiume, e due
        # comandi che differiscono solo per --landmark porto danno la stessa
        # citta' piu' il porto.
        drawn = rng.random() < STRUCTURE_CHANCE[key]
        if drawn or key in requested:
            chosen.add(key)
    return chosen


def _common_count(kind: LandmarkKind, n_buildings: int, rng: random.Random) -> int:
    """Quantita' di un luogo comune: proporzionale al numero di edifici
    generati (AC4), mai un numero assoluto, con uno scarto casuale che fa
    variare il conto fra due seed a parita' di mappa."""
    expected = kind.rate * n_buildings * rng.uniform(1 - _RATE_JITTER, 1 + _RATE_JITTER)
    # Parte intera piu' una probabilita' pari alla parte frazionaria: con
    # round() un kind la cui quota vale 0,4 non comparirebbe MAI, e i mestieri
    # rari sparirebbero dalle mappe piccole invece di essere rari.
    count = int(expected)
    if rng.random() < expected - count:
        count += 1
    return min(count, kind.max_count)


def select(*, scale: str, n_buildings: int, rng: random.Random, requested=()) -> list:
    """Luoghi da piazzare: lista di (LandmarkKind, quantita'), nell'ordine
    del catalogo (i vincolati da una regola prima dei liberi, vedi
    LANDMARK_KINDS).

    `requested` (AC1) forza la presenza di un kind con almeno un'istanza;
    tutto il resto e' estratto dal `rng` derivato dal seed (AC2). I kind non
    ammissibili al preset sono saltati (AC3) — chiederne uno e' gia' stato
    respinto da check_requested."""
    requested = set(requested)
    draft = []
    for kind in LANDMARK_KINDS:
        if scale not in kind.scales:
            continue
        # Come in select_structures: l'rng viene consumato prima di guardare
        # `requested`, cosi' una richiesta esplicita aggiunge un luogo senza
        # cambiare tutti gli altri.
        if kind.unique:
            count = 1 if rng.random() < kind.chance else 0
            if kind.key in requested:
                count = 1
        else:
            count = _common_count(kind, n_buildings, rng)
            if kind.key in requested:
                count = max(count, 1)
        draft.append((kind, count))

    # Il tetto sui luoghi comuni si applica in PROPORZIONE, non a chi arriva
    # prima. Con un budget consumato in ordine di catalogo gli ultimi kind
    # restavano a zero per costruzione: misurato con
    # scripts/city_landmarks_census.py su 30 seed, al preset "quartiere"
    # statue e giardini uscivano 0,03 e 0,00 per mappa contro una quota
    # attesa di 1,6 e 0,6, perche' taverne e magazzini avevano gia' esaurito
    # il budget. Ridurre tutti della stessa frazione tiene le proporzioni
    # relative che le `rate` dichiarano.
    budget = max(1, int(n_buildings * MAX_LANDMARK_FRACTION))
    total = sum(count for kind, count in draft if not kind.unique)
    if total > budget:
        factor = budget / total
        draft = [
            (kind, count if kind.unique else max(
                1 if kind.key in requested else 0, round(count * factor),
            ))
            for kind, count in draft
        ]
    return [(kind, count) for kind, count in draft if count]
