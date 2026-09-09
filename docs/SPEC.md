# SPEC — Dungeondraft Forge

Specifica di progetto per lo sviluppo con Claude Code.
Generatore procedurale di mappe `.dungeondraft_map` per Dungeondraft.

**Autore della spec:** analisi condotta su 9 mappe reali esportate da Dungeondraft 1.0.4.x
**Committente:** Jay — DM di una campagna homebrew D&D 5e (2024), mondo di Nova Mistralis
**Lingua del progetto:** codice e docstring in italiano, nomi di funzione in inglese

---

## 0. Come usare questo documento

Questa spec è scritta per essere data a Claude Code come contesto iniziale.
Salvala come `SPEC.md` nella root del repo.

**Prima riga di lavoro suggerita per Claude Code:**

> Leggi `SPEC.md`. Implementa la Milestone M0 e M1. Non passare a M2 finché
> `pytest` non è verde e `ddforge validate` non conferma il file di esempio.

Il documento è organizzato in modo che ogni milestone sia completabile e
verificabile in isolamento. **Non saltare l'ordine delle milestone**: il
progetto ha un vincolo tecnico (§2) che rende inutile qualunque lavoro
sull'algoritmica prima che il formato sia confermato funzionante.

---

## 1. Obiettivo e perimetro

### 1.1 Cosa deve fare

Generare file `.dungeondraft_map` apribili senza errori in Dungeondraft,
partendo da una descrizione di alto livello di una mappa (tipo di ambiente,
dimensioni, numero di stanze, tono), producendo geometria e arredo coerenti
con l'uso al tavolo in D&D 5e.

### 1.2 Cosa comprende il progetto

| Componente | Descrizione |
|---|---|
| **`ddforge`** | Libreria Python: modello dati, serializzazione, generatori |
| **`ddforge` CLI** | Interfaccia a riga di comando per generare e validare |
| **Skill Claude** | `dungeondraft-map-generator`, riscritta, che invoca il CLI |

### 1.3 Cosa NON comprende (fuori perimetro per ora)

- Renderer di anteprima PNG → previsto come **M6**, dopo che il formato è confermato
- Web UI
- Mod GDScript interno a Dungeondraft
- Editing di mappe esistenti (solo generazione ex novo)

### 1.4 Generatori richiesti, in ordine di priorità

1. **Dungeon a stanze (BSP)** — cripte, complessi sotterranei, prigioni
2. **Edifici urbani** — taverne, magioni, magazzini; multi-piano con tetti
3. **Grotte e fognature** — cellular automata, forme organiche
4. **Quartieri e città** — isolati, strade, edifici multipli con tetti

---

## 2. Il vincolo che determina tutta l'architettura

**LEGGERE PRIMA DI SCRIVERE CODICE.**

Un livello di mappa Dungeondraft contiene quattro campi con blob binari
serializzati la cui lunghezza dipende dalle dimensioni della mappa:

| Campo | Tipo | Lunghezza |
|---|---|---|
| `tiles.cells` | PoolIntArray | esattamente `width × height` |
| `terrain.splat` | PoolByteArray | esattamente `width × height × 64` |
| `cave.bitmap`, `cave.entrance_bitmap` | PoolByteArray | non lineare (50×25→2614 B, 30×30→1892 B, 8×8→154 B) |
| `materials[layer][].bitmap` | PoolByteArray | idem |

Una mappa 40×40 richiede **102.400 byte** di `terrain.splat`. La lunghezza di
`cave.bitmap` non segue una formula ricavabile per interpolazione.

### Conseguenza architetturale — non negoziabile

> **Il generatore NON costruisce il JSON da zero. Carica un template
> `.dungeondraft_map` esportato dall'installazione reale dell'utente, svuota
> solo le liste disegnabili, e ci inietta la geometria generata.**

Il template porta con sé gratuitamente: i blob binari della dimensione giusta,
i pack ID reali dell'installazione, il `creation_build` corretto, e il valore
di `world.format` che quell'eseguibile si aspetta.

Un tentativo precedente di questo progetto è fallito esattamente qui: generava
JSON sintatticamente valido che Dungeondraft apriva vuoto, senza messaggio di
errore.

---

## 3. Input dell'utente disponibili

Jay ha già esportato dalla propria installazione i file di riferimento.
**Primo compito di Claude Code (M0): trovarli, catalogarli, e derivarne le
costanti del progetto.**

Attesi (i nomi possono variare — cerca `*.dungeondraft_map` nelle cartelle
di lavoro):

- **template vuoto**, dimensione tipica (es. 40×40) — lo scheletro di produzione
- **template "ricco"** — contiene un esemplare di ogni tipo di elemento: muro,
  porta, finestra, pavimento, oggetto, **luce**, tetto, percorso, **testo**

> **Nota importante:** lo schema di `lights` e `texts` **non è stato verificato**
> nell'analisi che ha prodotto questa spec — nessuna delle mappe pubbliche
> analizzate ne conteneva. Vanno derivati leggendo il template ricco. Non
> inventarli: se il template ricco non li contiene, fermati e chiedi.

---

## 4. Architettura del repo

```
dungeondraft-forge/
├── SPEC.md                      # questo documento
├── README.md
├── pyproject.toml               # packaging + entry point CLI
├── src/ddforge/
│   ├── __init__.py
│   ├── godot.py                 # serializzazione tipi Godot
│   ├── ids.py                   # allocazione node_id
│   ├── template.py              # caricamento/svuotamento template
│   ├── model.py                 # dataclass Map/Level/Wall/Room/...
│   ├── build.py                 # primitive di disegno
│   ├── compose.py               # composti: stanza, corridoio, edificio
│   ├── assets.py                # catalogo asset + risoluzione texture
│   ├── validate.py              # validatore pre-consegna
│   ├── cli.py                   # entry point
│   └── generators/
│       ├── __init__.py
│       ├── base.py              # protocollo comune + Blueprint
│       ├── bsp.py               # M3 — dungeon a stanze
│       ├── building.py          # M4 — edifici urbani
│       ├── cave.py              # M5 — grotte / fognature
│       └── city.py              # M5 — quartieri e città
├── templates/                   # i .dungeondraft_map di riferimento
│   ├── blank_40x40.dungeondraft_map
│   └── rich_reference.dungeondraft_map
├── data/
│   └── assets.json              # catalogo generato in M0
├── tests/
│   ├── conftest.py
│   ├── test_godot.py
│   ├── test_ids.py
│   ├── test_template.py
│   ├── test_build.py
│   ├── test_validate.py
│   ├── test_generators.py
│   └── fixtures/
└── skill/                       # la skill Claude, in M7
    ├── SKILL.md
    └── references/
```

**Stack:** Python ≥3.11, solo stdlib per il core. `pytest` per i test.
`Pillow` solo in M6 (renderer). Nessuna dipendenza runtime pesante.

---

## 5. Milestone

Ogni milestone ha un criterio di completamento oggettivo. Non procedere
finché non è soddisfatto.

| # | Milestone | Criterio di completamento |
|---|---|---|
| **M0** | Ricognizione template e catalogo asset | `data/assets.json` esiste e contiene pack ID reali + path texture; schema di `lights` e `texts` documentato in `docs/format.md` |
| **M1** | Core: godot, ids, template, build | `pytest` verde; script demo produce un file con 1 stanza + 1 porta |
| **M2** | Validatore | `ddforge validate` rileva tutti gli errori della §7 su fixture appositamente corrotte |
| **M3** | Generatore BSP | Genera un dungeon 8 stanze connesso, validato, aperto correttamente in Dungeondraft |
| **M4** | Edifici urbani | Edificio multi-piano con tetti, aperto correttamente |
| **M5** | Grotte + città | Entrambi validati e aperti |
| **M6** | Renderer PNG di anteprima | Un PNG leggibile della planimetria senza aprire Dungeondraft |
| **M7** | Skill Claude | La skill genera una mappa da richiesta in linguaggio naturale |

### Il gate di M1 e M3 (verifica umana)

M1 e M3 richiedono un **passaggio manuale di Jay**: aprire il file generato in
Dungeondraft e confermare. Quando arrivi a quel punto, fermati e chiediglielo
esplicitamente, indicando cosa deve controllare:

- **M1:** la stanza appare, i muri sono chiusi, la porta è sul muro e non fluttua
- **M3:** le stanze sono tutte raggiungibili, le porte sono orientate bene,
  i pavimenti non sbordano

Nessuna documentazione cattura il verso di `portal.direction`, il segno delle
rotazioni e l'allineamento esatto delle porte. **Vanno calibrati su screenshot.**

---

## 6. Specifica dei moduli

### 6.1 `godot.py` — serializzazione

Dungeondraft salva tipi Godot come **stringhe**. Questo modulo è l'unico posto
del progetto che le costruisce.

```python
GRID = 256  # pixel per quadretto D&D (5 ft)

def v2(x: float, y: float) -> str:
    """Vector2 → 'Vector2( 256, 512 )'. Spazi interni obbligatori."""

def pv2(points: Sequence[tuple[float, float]]) -> str:
    """Punti → 'PoolVector2Array( x1, y1, x2, y2, ... )'.
    Coordinate APPIATTITE in una sola stringa, non raggruppate."""

def parse_pv2(s: str) -> list[tuple[float, float]]:
    """Inverso di pv2(). Serve al validatore e ai test di round-trip."""

def argb(rgb: str, alpha: int = 255) -> str:
    """'aabbcc' → 'ffaabbcc'. ALPHA PER PRIMO. 8 cifre sempre."""

def grid_to_px(n: float) -> float:
    """Quadretti → pixel."""
```

**Regole invariabili:**
- `v2` e `pv2` producono spazi dopo `(` e prima di `)`
- i colori sono **sempre** 8 cifre esadecimali ARGB
- le rotazioni sono in **radianti**
- `world.width` / `world.height` sono in **quadretti**; tutte le coordinate
  dentro gli elementi sono in **pixel**

**Test obbligatori:** round-trip `pv2 → parse_pv2 → pv2` idempotente; `argb`
rifiuta input a 8 cifre già formattati o lunghezze diverse da 6.

---

### 6.2 `ids.py` — allocazione node_id

I `node_id` sono stringhe esadecimali univoche **in tutto il file**, porte
incluse. `world.next_node_id` deve essere maggiore di ogni id usato: se non lo
è, Dungeondraft riassegna id duplicati alla prima modifica e corrompe la mappa.

```python
class IdAllocator:
    def __init__(self, start: int = 0x1000) -> None: ...
    def next(self) -> str:
        """Restituisce l'id esadecimale successivo, es. '1001'."""
    @property
    def next_free(self) -> str:
        """Valore da scrivere in world.next_node_id."""

    @classmethod
    def from_document(cls, doc: dict) -> "IdAllocator":
        """Inizializza partendo dal max id già presente nel template.
        Necessario se il template non è vuoto."""
```

**Test:** 10.000 chiamate consecutive producono 10.000 id distinti;
`next_free` è sempre strettamente maggiore dell'ultimo emesso.

---

### 6.3 `template.py` — caricamento e svuotamento

```python
LEVEL_KEYS = (
    "label", "environment", "layers", "shapes", "tiles", "patterns",
    "walls", "portals", "cave", "terrain", "water", "materials",
    "paths", "objects", "lights", "roofs", "texts",
)

DRAWABLE_LISTS = (
    "patterns", "walls", "portals", "paths", "objects", "lights", "texts",
)

def load_template(path: str | Path) -> dict:
    """Carica il JSON. Verifica che sia un documento Dungeondraft valido
    (header + world + world.format + world.levels). Solleva TemplateError
    con messaggio esplicito se manca qualcosa."""

def blank_level(level: dict) -> dict:
    """Deep copy del livello con SOLO le liste disegnabili svuotate.
    MANTIENE INTATTI: tiles, terrain, cave, water, environment, layers
    — sono i blob binari dimensionati sulla mappa."""

def prepare(doc: dict, *, levels: int = 1, labels: Sequence[str] | None = None) -> dict:
    """Restituisce un documento pronto per l'injection, con `levels` piani
    svuotati. Se il template ha meno piani di quelli richiesti, duplica il
    primo — i blob hanno già la dimensione giusta."""

def finalize(doc: dict, ids: IdAllocator) -> dict:
    """Aggiorna world.next_node_id. Da chiamare SEMPRE prima di save()."""

def save(doc: dict, path: str | Path) -> None:
    """json.dump con indent=2, ensure_ascii=False, encoding utf-8."""
```

**Test:** dopo `blank_level`, `len(level['terrain']['splat'])` è invariato;
tutte le 17 chiavi sono ancora presenti; `roofs` resta un dict con la chiave
`roofs` svuotata.

---

### 6.4 `model.py` — modello dati

Livello intermedio tra i generatori e la serializzazione. I generatori
producono **modello**, non JSON. Questo rende i generatori testabili senza
toccare il formato.

```python
@dataclass(frozen=True)
class Rect:
    """Rettangolo in coordinate-quadretto. x2/y2 esclusivi."""
    x1: int; y1: int; x2: int; y2: int
    @property
    def w(self) -> int: ...
    @property
    def h(self) -> int: ...
    def center(self) -> tuple[float, float]: ...
    def overlaps(self, other: "Rect", margin: int = 0) -> bool: ...
    def shrink(self, n: int) -> "Rect": ...

@dataclass
class Door:
    wall_index: int          # quale muro della stanza
    t: float                 # posizione lungo il muro, 0..1
    kind: str = "wood"       # wood | metal | secret | double | window | arch
    locked: bool = False

@dataclass
class Room:
    rect: Rect
    kind: str                # ingresso | corridoio | sala | boss | servizio | ...
    name: str = ""
    doors: list[Door] = field(default_factory=list)
    floor: str | None = None   # override texture
    lights: list[tuple[float, float]] = field(default_factory=list)

@dataclass
class Blueprint:
    """Output di un generatore. Contiene SOLO geometria e semantica,
    nessun path res:// e nessuna stringa Godot."""
    width: int; height: int          # in quadretti
    rooms: list[Room]
    corridors: list[Rect]
    graph: dict[int, list[int]]      # adiacenze fra indici di rooms
    seed: int
    style: str                       # dungeon | building | cave | city
    levels: int = 1
```

Il flusso è: **generatore → Blueprint → compose → build → JSON**.
Ogni freccia è testabile separatamente.

---

### 6.5 `build.py` — primitive di disegno

Ogni funzione aggiunge **un** elemento a un livello e restituisce il dict
creato (utile per attaccarci le porte).

```python
def add_wall(level, ids, points_grid, texture, *,
             color="ffffffff", loop=False, wall_type=1,
             joint=0, shadow=True) -> dict:
    """points_grid in QUADRETTI, convertiti in px internamente.
    Con loop=True NON ripetere il primo punto in coda."""

def add_portal(wall, ids, *, t: float, direction, texture,
               radius=128, rotation=0.0, closed=True, locked=False) -> dict:
    """Aggiunge la porta DENTRO wall['portals'].
    Imposta wall_id = wall['node_id'] e wall_distance = t.
    NON spezzare il muro: Dungeondraft buca da solo."""

def add_pattern(level, ids, rect_grid, texture, *,
                layer=-400, color="ffffffff", outline=False) -> dict: ...

def add_polygon_pattern(level, ids, points_grid, texture, **kw) -> dict:
    """Per pavimenti non rettangolari (grotte, isolati irregolari)."""

def add_object(level, ids, x, y, texture, *,
               rotation=0.0, scale=1.0, layer=100,
               shadow=True, block_light=False, mirror=False) -> dict: ...

def add_path(level, ids, points_grid, texture, *,
             width=472, layer=100, smoothness=1, loop=False) -> dict:
    """ATTENZIONE: edit_points sono RELATIVI a position.
    position = primo punto; edit_points = tutti i punti meno position."""

def add_roof(level, ids, points_grid, texture, *, width=512, roof_type=0) -> dict:
    """Va in level['roofs']['roofs'], non in una lista di primo livello."""

def add_light(level, ids, x, y, **kw) -> dict:
    """SCHEMA DA DERIVARE DAL TEMPLATE RICCO IN M0."""

def add_text(level, ids, x, y, content, **kw) -> dict:
    """SCHEMA DA DERIVARE DAL TEMPLATE RICCO IN M0."""
```

---

### 6.6 `compose.py` — composti

```python
def draw_room(level, ids, room: Room, palette: "Palette") -> dict:
    """Pavimento + muri perimetrali + porte + luci. Restituisce
    {'walls': [...], 'pattern': ..., 'portals': [...]}."""

def draw_corridor(level, ids, rect: Rect, palette) -> dict:
    """Corridoio come stanza stretta senza porte alle estremità."""

def connect(level, ids, room_a: Room, room_b: Room, palette) -> dict:
    """Trova il muro condiviso o il percorso a L fra due stanze,
    e ci mette una porta. Se non c'è muro condiviso, genera un corridoio."""

def draw_building(level_stack, ids, blueprint, palette) -> None:
    """Edificio multi-piano: distribuisce le stanze sui livelli,
    aggiunge scale e tetto sull'ultimo."""
```

**Nota sulle porte:** `connect` è la funzione più delicata del progetto.
Il muro condiviso fra due stanze adiacenti va trovato geometricamente, poi
convertito in una frazione `t` lungo quel muro. Scrivi test unitari con
rettangoli noti prima di implementare qualsiasi generatore.

---

### 6.7 `assets.py` — catalogo

`data/assets.json` è prodotto in M0 leggendo i template. Struttura:

```json
{
  "packs": [
    {"name": "Forgotten Adventures Objects A", "id": "xjCzavyl",
     "author": "Forgotten Adventures", "version": "1"}
  ],
  "walls":   {"stone": "res://textures/walls/stone.png", "wood": "..."},
  "floors":  {"stone_dungeon": "...", "wood_planks": "...", "dirt": "..."},
  "portals": {"wood": "...", "metal": "...", "double": "...", "window": "..."},
  "roofs":   {"shingle": "...", "hay": "..."},
  "paths":   {"carpet_red": "...", "cobble": "..."},
  "objects": {
    "torch": "...", "table_round": "...", "chair": "...", "bed": "...",
    "crate": "...", "barrel": "...", "bookshelf": "...", "altar": "...",
    "sarcophagus": "...", "column": "...", "brazier": "...", "chest": "..."
  }
}
```

```python
@dataclass
class Palette:
    """Set coerente di texture per un tipo di ambiente."""
    wall: str; floor: str; door: str
    accents: dict[str, str]
    floors: dict[str, str]  # room.kind -> floor, es. {"boss": "..."} (TASK-43)

def load_catalog(path="data/assets.json") -> dict: ...
def palette_for(style: str, catalog: dict) -> Palette:
    """style ∈ {dungeon, crypt, sewer, cave, tavern, manor, warehouse, city}"""
def required_packs(doc: dict) -> set[str]:
    """Estrae gli ID pack referenziati dalle texture usate nel documento."""
```

**Regola:** ogni path `res://packs/<ID>/...` usato deve avere `<ID>` presente in
`header.asset_manifest`. Il validatore lo verifica; `assets.py` non deve mai
restituire un path il cui pack non è nel template.

---

## 7. `validate.py` — il validatore

È il pezzo che trasforma il progetto da "speriamo" a ingegneria. Ogni errore
deve essere un messaggio leggibile, non un'eccezione generica.

```python
@dataclass
class Issue:
    severity: str      # "error" | "warning"
    code: str          # es. "DDF001"
    message: str
    path: str          # es. "world.levels.0.walls[3]"

def validate(doc: dict) -> list[Issue]: ...
```

### Regole obbligatorie (severity = error)

| Codice | Regola |
|---|---|
| DDF001 | `header` e `world` presenti; `world.format` è un intero |
| DDF002 | `world` contiene `width`, `height`, `next_node_id`, `msi`, `grid`, `embedded` |
| DDF003 | Ogni livello ha esattamente le 17 chiavi di `LEVEL_KEYS` |
| DDF004 | Tipi corretti: `roofs` è dict con chiave `roofs`; `shapes` è dict; `materials` è dict; le 7 liste disegnabili sono liste |
| DDF005 | Nessun `node_id` duplicato in tutto il documento, porte comprese |
| DDF006 | `int(world.next_node_id, 16)` > max di tutti i `node_id` |
| DDF007 | Ogni `points` / `edit_points` matcha `^PoolVector2Array\( .* \)$` con numero **pari** di coordinate |
| DDF008 | Ogni `position` / `scale` / `direction` matcha `^Vector2\( .*, .* \)$` |
| DDF009 | Ogni colore è 8 cifre esadecimali |
| DDF010 | `len(tiles.cells) == width × height` |
| DDF011 | `len(terrain.splat) == width × height × 64` |
| DDF012 | Ogni `portal.wall_id` esiste fra i `node_id` dei muri dello stesso livello |
| DDF013 | Ogni `portal.wall_distance` ∈ [0, 1] |
| DDF014 | Ogni texture `res://packs/<ID>/...` ha `<ID>` in `header.asset_manifest` |
| DDF015 | Ogni `rotation` è un numero finito (non NaN, non stringa) |
| DDF016 | Ogni `light` ha `texture`: senza, Dungeondraft resta in caricamento all'infinito (TASK-42) |

### Warning (severity = warning)

| Codice | Regola |
|---|---|
| DDF101 | Elemento con coordinate fuori dal canvas `width × height` |
| DDF102 | Stanza non raggiungibile dal grafo (nessuna porta) |
| DDF103 | Muro con meno di 2 punti |
| DDF104 | Pattern con meno di 3 punti |
| DDF105 | Due porte sullo stesso muro a distanza < 0.05 |

### Test del validatore

Per ogni codice `DDFxxx`, una fixture che lo viola e un test che verifica che
`validate()` lo segnali. **Questo è il criterio di completamento di M2.**

---

## 8. CLI

```
ddforge generate <style> [opzioni]
ddforge validate <file.dungeondraft_map>
ddforge inspect  <file.dungeondraft_map>     # dump struttura e statistiche
ddforge catalog  --from <template>           # rigenera data/assets.json
ddforge preview  <file.dungeondraft_map>     # M6
```

### `generate`

```
ddforge generate dungeon \
    --template templates/blank_40x40.dungeondraft_map \
    --out cripta.dungeondraft_map \
    --width 40 --height 40 \
    --rooms 8 \
    --seed 1337 \
    --style crypt \
    --lights \
    --furnish medium          # none | light | medium | heavy
```

Stili disponibili: `dungeon`, `building`, `cave`, `city`.

**Comportamento obbligatorio:** `generate` esegue `validate` sul risultato
prima di scrivere il file. Se ci sono errori, **non scrive** ed esce con codice
1 stampando gli Issue. Un warning stampa ma non blocca.

**`--seed`**: ogni generazione è riproducibile. Lo stesso seed con gli stessi
parametri produce byte identici (escluso `creation_date`). È un requisito di
testabilità, non un vezzo.

---

## 9. I generatori

Tutti implementano lo stesso protocollo e restituiscono un `Blueprint`.

```python
class Generator(Protocol):
    def generate(self, *, width: int, height: int, seed: int, **params) -> Blueprint: ...
```

### 9.1 `bsp.py` — dungeon a stanze (M3)

Partizione binaria dello spazio:

1. Parti da un rettangolo `width × height` meno un margine di 1 quadretto
2. Taglia ricorsivamente lungo l'asse più lungo, in un punto casuale entro
   il 35–65% della dimensione, finché la partizione è più piccola di
   `max_room * 2` o si raggiunge `depth_max`
3. In ogni foglia inscrivi una stanza con margine casuale 0–2 quadretti
4. Risalendo l'albero, collega le due sorelle con un corridoio a L
5. Aggiungi il 10–20% di collegamenti extra fra stanze vicine → crea anelli,
   evita il dungeon-albero che si percorre in un solo modo

**Parametri:** `rooms` (target), `min_room=3`, `max_room=10`, `corridor_width=1|2`,
`loops=0.15`.

**Semantica D&D — questa parte fa la differenza fra una planimetria e una mappa
giocabile:**

- La stanza più lontana dall'ingresso nel grafo diventa `kind="boss"`,
  e riceve dimensione maggiorata
- Le stanze con grado ≥ 3 sono nodi tattici: `furnish` ci mette coperture
  (colonne, casse) ogni 3–4 quadretti
- Un corridoio più lungo di 12 quadretti (60 ft) supera la scurovisione di
  molte specie: segnalalo in `Blueprint` come proprietà, così `furnish` può
  metterci una fonte di luce a metà
- Le porte segrete vanno su stanze di grado 1 raggiungibili anche da altrove

### 9.2 `building.py` — edifici urbani (M4)

1. Perimetro esterno rettangolare o a L
2. Suddivisione interna ricorsiva con muri portanti (più spessi visivamente:
   usa una texture diversa)
3. Un vano scale allineato verticalmente su tutti i piani
4. Distribuzione stanze per piano secondo il tipo:
   - **taverna**: piano terra = sala comune + cucina + retro; primo = camere
   - **magione**: terra = rappresentanza; primo = privato; sottotetto = servitù
   - **magazzino**: terra = unico volume + soppalco
5. Tetto sull'ultimo livello, con `roofs.sun_direction` coerente

**Vincolo multi-piano:** le scale devono occupare lo stesso `Rect` su tutti i
livelli, altrimenti la mappa non si legge al tavolo.

### 9.3 `cave.py` — grotte e fognature (M5)

Cellular automata classico:

1. Griglia `width × height`, ogni cella roccia con probabilità 0.45
2. 4–5 iterazioni: una cella diventa roccia se ≥5 vicini su 8 sono roccia
3. Etichetta le componenti connesse, tieni la più grande, scava tunnel verso
   le altre sopra una certa dimensione
4. Estrai il contorno con marching squares → poligoni

**Decisione da prendere in M5, non prima:** se il risultato va reso come muri
poligonali (`add_wall` con molti punti) o scritto nel layer `cave` di
Dungeondraft (`cave.bitmap`). Il layer nativo è visivamente molto migliore ma
richiede di capire la codifica del bitmap — che l'analisi non ha risolto.
**Prova prima i muri poligonali**, che funzionano di sicuro; passa al layer
nativo solo se il risultato non è soddisfacente e solo dopo aver decodificato
il bitmap con esperimenti su template di dimensioni diverse.

Le **fognature** sono una variante: griglia di canali ortogonali invece di
cellular automata, più camere di giunzione circolari, più acqua nel layer
`water`.

### 9.4 `city.py` — quartieri e città (M5)

1. Rete stradale: partizione ricorsiva del canvas in isolati con strade di
   larghezza 2–4 quadretti; via principale più larga
2. Ogni isolato viene suddiviso in lotti con fronte strada garantito
3. Ogni lotto riceve un edificio (riusa `building.py` a un solo piano) con
   arretramento casuale dal fronte
4. Tetti su tutti gli edifici — in una mappa cittadina si vede dall'alto
5. Piazze: 1–2 isolati lasciati vuoti con pavimentazione diversa, pozzo o
   fontana al centro
6. Strade come `add_path` con texture di acciottolato, non come pattern

**Scala:** una città intera a 256 px/quadretto diventa enorme. Prevedi un
parametro `--scale` che permetta di generare a 1 quadretto = 1 edificio per le
mappe di regione, contro 1 quadretto = 5 ft per il quartiere giocabile.
Decidi in M5 se supportare entrambe o solo il quartiere.

> **Deciso in M5** (`backlog/decisions/decision-2`, TASK-34): si supportano
> **entrambi** i regimi come preset selezionabili, non uno solo. Implementato
> in TASK-41 con due preset, `quartiere` (5 ft/quadretto) e `citta` (1
> quadretto = 1 edificio). Al round 2 del gate umano Jay ha rivisto scala e
> nomi e ha chiesto **tre** preset: `ddforge generate city --scale
> isolato|quartiere|citta`, default `isolato`. `isolato` è il vecchio
> `quartiere` rinominato (edifici a pianta completa); `quartiere` è il
> vecchio `citta` rinominato (1 quadretto = 1 edificio); `citta` è nuovo, una
> città intera capace di contenere una decina di quartieri (~10x gli edifici
> del preset `quartiere` a parità di canvas). Nei preset `quartiere`/`citta`
> un edificio non è una pianta a stanze ma il suo solo ingombro (pavimento +
> tetto): `building.generate` pretende almeno 6-8 quadretti per lato, che a
> queste scale il lotto non ha. Punti 1–6 di questa sezione valgono per tutti
> e tre i preset; cambiano solo i valori numerici (SCALE_PRESETS in
> `generators/city.py`). Differenza fra i preset e come scegliere:
> `README.md` e `skill/references/styles.md`.

### 9.5 Arredo (`furnish`)

Modulo trasversale, applicato dopo la geometria:

```python
def furnish(level, ids, blueprint, palette, *, density="medium", rng) -> None:
```

Regole: gli oggetti non toccano i muri (margine 0.5 quadretti); non ostruiscono
le porte (raggio libero di 1.5 quadretti davanti a ogni porta); rispettano il
`kind` della stanza; densità `light`/`medium`/`heavy` = circa 0.05/0.12/0.25
oggetti per quadretto.

Il pavimento rispetta il `kind` della stanza allo stesso modo: `draw_room`
sceglie `room.floor` (override esplicito) o `palette.floors[room.kind]` (se
mappato) prima di ricadere su `palette.floor` (TASK-43). Corridoi e vano
scale non hanno un `kind` mappato e restano sempre sul floor uniforme.

---

## 10. Testing

`pytest`, con questa piramide:

**Unit (veloci, senza I/O):** `godot`, `ids`, `model.Rect`, algoritmi dei
generatori su seed fissi.

**Integrazione:** carica un template di fixture → genera → valida. Ogni
generatore ha un test che verifica: nessun errore di validazione, tutte le
stanze raggiungibili nel grafo, nessuna sovrapposizione fra stanze.

**Golden file:** per un seed fisso, il documento generato viene confrontato con
un file di riferimento in `tests/fixtures/golden/`. Normalizza `creation_date`
prima del confronto. Serve a intercettare regressioni silenziose nel formato.

**Property-based (opzionale, `hypothesis`):** per 100 seed casuali, il grafo
delle stanze è sempre connesso e nessuna stanza esce dal canvas.

```
pytest -q                    # tutto
pytest -m "not slow"         # senza i golden
```

Un template di fixture piccolo (8×8) va committato in `tests/fixtures/` così i
test girano senza i template di produzione.

---

## 11. La skill Claude (M7)

L'errore da non ripetere: **la skill non deve contenere lo schema del formato
né riscrivere il generatore.** Deve essere sottile e chiamare il CLI.

```
skill/
├── SKILL.md
└── references/
    ├── styles.md        # stili disponibili e quando usarli
    └── examples.md      # esempi di invocazione del CLI
```

Il `SKILL.md` descrive un workflow di quattro passi:

1. Interpretare la richiesta in linguaggio naturale → scegliere `style`,
   dimensioni, numero di stanze, densità di arredo
2. Invocare `ddforge generate` con quei parametri
3. Se il comando esce con errore, **leggere gli Issue e correggere i
   parametri** — mai modificare il JSON a mano
4. Consegnare il file, indicando dove salvarlo e come aprirlo

Il modello fa quello che sa fare bene (tradurre l'intento in parametri) e non
tocca il formato.

---

## 12. Codice di partenza verificato

Questo nucleo è già stato testato contro una mappa Dungeondraft reale: carica
un template, lo svuota, inietta due stanze e una porta, e produce un documento
strutturalmente corretto. Usalo come base di `godot.py`, `ids.py`,
`template.py` e `build.py`.

```python
import json, copy

GRID = 256

def v2(x, y):  return f"Vector2( {x}, {y} )"
def pv2(pts):  return "PoolVector2Array( " + ", ".join(
                   f"{c}" for p in pts for c in p) + " )"

class Ids:
    def __init__(self, start=0x1000): self.n = start
    def next(self):
        self.n += 1
        return format(self.n, 'x')

def blank_level(level):
    lv = copy.deepcopy(level)
    for k in ("patterns", "walls", "portals", "paths", "objects", "lights", "texts"):
        lv[k] = []
    lv["roofs"]["roofs"] = []
    lv["shapes"] = {"polygons": [], "walls": []}
    lv["materials"] = {}
    return lv

def add_pattern(lv, ids, x1, y1, x2, y2, texture, layer=-400, color="ffffffff"):
    lv["patterns"].append({
        "position": v2(0, 0), "shape_rotation": 0, "scale": v2(1, 1),
        "points": pv2([(x1*GRID, y1*GRID), (x2*GRID, y1*GRID),
                       (x2*GRID, y2*GRID), (x1*GRID, y2*GRID)]),
        "layer": layer, "color": color, "outline": False,
        "texture": texture, "rotation": 0, "node_id": ids.next()})

def add_wall(lv, ids, pts, texture, color="ffffffff", loop=False):
    w = {"points": pv2([(x*GRID, y*GRID) for x, y in pts]),
         "texture": texture, "color": color, "loop": loop,
         "type": 1, "joint": 0, "normalize_uv": True, "shadow": True,
         "node_id": ids.next(), "portals": []}
    lv["walls"].append(w)
    return w

def add_portal_on_wall(wall, ids, x, y, direction, texture,
                       radius=128, distance=0.5, rotation=0.0):
    wall["portals"].append({
        "position": v2(x*GRID, y*GRID), "rotation": rotation,
        "scale": v2(1, 1), "direction": v2(*direction),
        "texture": texture, "radius": radius,
        "wall_id": wall["node_id"], "wall_distance": distance,
        "closed": True, "node_id": ids.next()})

def add_object(lv, ids, x, y, texture, rotation=0.0, scale=1.0, layer=100):
    lv["objects"].append({
        "position": v2(x*GRID, y*GRID), "rotation": rotation,
        "scale": v2(scale, scale), "mirror": False, "texture": texture,
        "layer": layer, "shadow": True, "block_light": False,
        "node_id": ids.next()})

def finalize(doc, ids):
    doc["world"]["next_node_id"] = format(ids.n + 1, 'x')
    return doc
```

---

## 13. Appendice — schema del formato, verificato

Estratto da mappe reali Dungeondraft 1.0.4.x. Non ricostruito a memoria.

### Radice
```
{ "header": {...}, "world": {...} }
```

### `header`
`creation_build` (str, es. `"1.0.4.7 corrosive medusa"`), `creation_date`
(dict: year, month, day, weekday, dst, hour, minute, second),
`uses_default_assets` (bool), `asset_manifest` (list), `editor_state` (dict).

Ogni voce di `asset_manifest`:
```json
{"name": "...", "id": "Hk3gdwPN", "version": "2", "author": "...",
 "keywords": null, "allow_3rd_party_mapping_software_to_read": false,
 "custom_color_overrides": {"enabled": false, "min_redness": 0.1,
                            "min_saturation": 0, "red_tolerance": 0.04}}
```

### `world`
```json
{"format": 3, "width": 32, "height": 20,
 "next_node_id": "cea", "next_prefab_id": "0",
 "msi": {"offset_map_size": 512, "max_offset_distance": 0.2,
         "cell_size": 64, "seed": "6253df56"},
 "grid": {"color": "7f000000", "texture": "res://textures/grid/dotted_line.png"},
 "building_wear": null, "wall_shadow": false, "object_shadow": false,
 "trace_image_visible": false, "embedded": {}, "levels": {"0": {...}}}
```

### `level` — 17 chiavi
`label, environment, layers, shapes, tiles, patterns, walls, portals, cave,
terrain, water, materials, paths, objects, lights, roofs, texts`

Liste: `patterns, walls, portals, paths, objects, lights, texts`
Dict: `environment, layers, shapes, tiles, cave, terrain, water, materials, roofs`

### `wall`
```json
{"points": "PoolVector2Array( 512, 512, 2048, 512 )",
 "texture": "res://textures/walls/stone.png", "color": "ffffffff",
 "loop": true, "type": 1, "joint": 0, "normalize_uv": true,
 "shadow": true, "node_id": "8e", "portals": []}
```
`type` osservato: sempre 1. `joint`: 0 o 1.

### `portal` (dentro `wall.portals`)
```json
{"position": "Vector2( 5504, 1792 )", "rotation": 3.141593,
 "scale": "Vector2( 1, 1 )", "direction": "Vector2( -1, 0 )",
 "texture": "res://packs/xjCzavyl/textures/portals/door_metal_03.png",
 "radius": 128, "wall_id": "8e", "wall_distance": 0.5,
 "closed": true, "node_id": "90", "locked": true}
```

### `pattern`
```json
{"position": "Vector2( 0, 0 )", "shape_rotation": 0, "rotation": 0,
 "scale": "Vector2( 1, 1 )",
 "points": "PoolVector2Array( 2816, 512, 3840, 512, 3840, 1280, 2816, 1280 )",
 "layer": -400, "color": "ffffffff", "outline": false,
 "texture": "...", "node_id": "1a", "locked": true}
```

### `object`
```json
{"position": "Vector2( 1029.38, 979.371 )", "rotation": -1.047195,
 "scale": "Vector2( 1, 1 )", "mirror": false, "texture": "...",
 "layer": 100, "shadow": false, "block_light": false, "node_id": "a0d"}
```

### `path`
```json
{"position": "Vector2( 4608, 3456 )", "rotation": 0, "scale": "Vector2( 1, 1 )",
 "edit_points": "PoolVector2Array( 0, 0, 2560, 0 )",
 "smoothness": 1, "texture": "...", "width": 472, "layer": 100,
 "fade_in": false, "fade_out": false, "grow": false, "shrink": false,
 "block_light": false, "loop": false, "node_id": "a30"}
```
**`edit_points` sono relativi a `position`.**

### `roof` (dentro `level.roofs.roofs`)
```json
{"position": "Vector2( 0, 0 )", "rotation": 0, "scale": "Vector2( 1, 1 )",
 "points": "PoolVector2Array( 8960, 5888, 8960, 4352 )",
 "texture": "...", "width": 512, "type": 0, "node_id": "7e5"}
```
Contenitore: `{"shade": true, "shade_contrast": 0.5, "sun_direction": 45, "roofs": [...]}`

### `light`, `text`
**Non verificati.** Da derivare dal template ricco in M0.

### Layer standard
| Valore | Nome |
|---|---|
| -400 | Below Ground |
| -100 | Below Water |
| 100–400 | User Layer 1–4 |
| 700 | Above Walls |
| 900 | Above Roofs |

---

## 14. Riepilogo delle trappole

| Trappola | Sintomo | Rimedio |
|---|---|---|
| Blob binari sintetizzati | crash o mappa vuota | usa il template |
| `points` come lista di Vector2 | muri e pavimenti assenti | stringa `PoolVector2Array` |
| Colore a 6 cifre | elementi trasparenti o neri | ARGB 8 cifre |
| Porte a livello mappa | porte fuori dai muri | annidale in `wall.portals` |
| `next_node_id` non aggiornato | corruzione alla prima modifica | `finalize()` sempre |
| Pack ID inventati | "missing assets" al caricamento | solo ID dal template |
| `format` diverso dalla build | rifiuto silenzioso | eredita dal template |
| Coordinate in px in `world.width` | canvas gigantesco | quadretti nel world, px negli elementi |
| `path.edit_points` assoluti | percorsi spostati | relativi a `position` |
| Primo punto ripetuto con `loop: true` | muro doppio sull'ultimo lato | o `loop` o punto ripetuto, mai entrambi |

**Backup:** un `.dungeondraft_map` malformato può in casi rari far crashare
Dungeondraft. Lavora sempre su copie; tieni `templates/` in sola lettura.

---

## 15. Definizione di "fatto"

Il progetto è completo quando:

- `pytest` è verde, con copertura di tutti i codici `DDFxxx`
- `ddforge generate dungeon --seed 1 --rooms 8` produce un file che Jay
  apre in Dungeondraft e trova utilizzabile al tavolo senza ritocchi manuali
  di struttura
- lo stesso vale per `building`, `cave`, `city`
- la skill Claude genera una mappa da una frase in italiano
- il README spiega come esportare un nuovo template quando Dungeondraft
  aggiorna il formato
