# Formato `.dungeondraft_map` — costanti verificate

Documento derivato dai template reali dell'installazione di Jay (TASK-2) e
dall'analisi in `docs/SPEC.md` §13. Aggiornato man mano che le milestone
verificano campi aggiuntivi (TASK-3 per `lights`/`texts`, i gate umani di
M1/M3 per l'orientamento delle porte).

## 0. Scostamento importante rispetto a SPEC.md

`docs/SPEC.md` §13 e stato scritto analizzando mappe esportate da
**Dungeondraft 1.0.4.x**. L'installazione attuale di Jay (verificata in
`C:\Program Files\Dungeondraft`, dati utente in
`%AppData%\Roaming\Dungeondraft`) e **Dungeondraft 1.2.0.1** (build
`"1.2.0.1 opulent kirin"`). Tutti i template e le mappe reali di Jay
trovate sul suo sistema sono in questa build o piu recenti (build minima
osservata fra i suoi file: `1.2.0.1`).

**Conseguenza pratica:** i template da usare nel progetto sono quelli
esportati dalla build 1.2.0.1, non gli esempi 1.0.4.x citati nella spec.
Lo schema di §13 e stato verificato quasi interamente compatibile (vedi
§3 sotto per l'unica differenza osservata: il campo `point_index` nei
`portal`).

## 1. Template scelti per il progetto

| Ruolo | File in `templates/` | Sorgente originale | Dimensione mappa | Note |
|---|---|---|---|---|
| Template vuoto (skeleton di produzione) | `blank_80x80.dungeondraft_map` | `Desktop/ddraft_examples/template_80x80.dungeondraft_map` | 80×80 quadretti | 0 elementi disegnabili, un solo pack (`FA30DDXY`, cioe gli asset di default) |
| Template ricco (un esemplare per tipo) | `rich_reference.dungeondraft_map` | `Desktop/ddraft_examples/template_ricco.dungeondraft_map` (identico byte-per-byte a `mappa_ricca.dungeondraft_map` nella stessa cartella, SHA-256 `eda0a71f...`) | 80×80 quadretti | 42 pack nel manifest, 1 esemplare di quasi ogni tipo di elemento |

**Nota sul nome del template vuoto:** SPEC.md §4 usa `blank_40x40.dungeondraft_map`
come *esempio* illustrativo ("es. 40×40" in §3). Nessun template 40×40 esiste
sull'installazione di Jay: il preset di default della sua installazione
(`config.ini`, sezione `[New]`) e `width=80 height=80`. Si e usato
`blank_80x80.dungeondraft_map` per non mentire sul contenuto del file.
Se in futuro servisse un template piu piccolo per velocizzare i test, va
esportato esplicitamente da Jay (la fixture di test usera comunque un
8×8 dedicato, TASK-5).

Entrambi i file sono impostati **read-only** (attributo filesystem Windows,
`chmod 444`) per rispettare la regola di SPEC.md §14: "un `.dungeondraft_map`
malformato puo in rari casi far crashare Dungeondraft, lavora sempre su
copie". Nessun modulo del codice deve scrivere in `templates/`.

## 2. Costanti derivate

| Costante | Valore osservato | Fonte |
|---|---|---|
| `world.format` | `3` | Tutti i file di Jay in build 1.2.0.1 (coerente anche con le mappe di terze parti in build 1.0.x-1.1.x, quindi stabile da tempo) |
| `header.creation_build` | `"1.2.0.1 opulent kirin"` | `templates/*.dungeondraft_map` |
| `header.uses_default_assets` | `true` in entrambi i template scelti | — |

### Pack ID del template ricco (`header.asset_manifest`, 42 voci)

Elenco completo id/nome/autore/versione salvato per riferimento (usato da
TASK-4 per generare `data/assets.json`; qui solo la fonte):

```
qTwZcByF  [DQ] 2Y_Anniversary_Pack                         DungeonQuill              1.1
2VHJB262  BB BaseCity Colored                               BluBerrey                 1
KtpqsMIX  BB KeepsAndCastles Colored                        BluBerrey                 1
4MPa6ax6  BB RiversRunnin Colored                            BluBerrey                 1
a8D9WX4I  BB RugsNRiches Colored                             BluBerrey                 1
QofNvPQx  BB SeasAndShores Colored                           BluBerrey                 1
E0ZgzvXT  Benthic Botany                                      Stovetop                  1
Prdr1WET  CH - Worldmap                                       Crosshead                 0,5
Bp03igMq  CHR - Town Maps                                     Crosshead                 0,2
RchUgE31  City Terrain                                        Clay Robeson              1
eMSwy6B7  Crosshead's Ghibli Pack                             Crosshead                 1
566ki5wO  CSA - Community Suggested Assets                    Nexoness                  1,1
LPjlqz9Q  DQ_Pack_Theme_16 Arcane Laboratory FREE              DungeonQuill              1
JoOKLIJc  Expanded Nature Vol. 1                               Scott Avery               1
FA30DDXY  FA_Starter_Pack_v3.0                                 Forgotten Adventures      3.0
QzahaP3O  GF Colorable Furniture and Stairs                    Gnome Factory             1
HJANrMeL  GoGots-Forest                                        GoGots                    1,2
vpUPLad1  GoGots-Forest Add                                    GoGots                    1
FjQPhftV  GoGots-Mushroom                                      GoGots                    1
74SaGFcV  GoGots-Water                                         GoGots                    1
MKedRBxF  IC_Apothecary                                        InsightCheque             1
0vMF1pHo  Lost Lands Castles                                   Lost Lands                1
roSIrsHG  Lost Lands Hamlets                                   Lost Lands                1
P5JygHfx  Maelstrom Maps Free Simple Castle Asset Pack         Maelstrom Maps            1
kNUrZPY0  Skront's Alchemy                                     Skront                    1
dS0IUhwf  Skront's Alchemy Mk2                                 Skront                    1
MiS6cyNC  Skront's Books                                       Skront                    1.1
hA8yMy2D  Skront's Farm and Field                              Skront                    1.1
o4K03ljk  Skront's Rocks and Bricks                            Skront                    1
PGz110gg  Skront's Treasure                                    Skront                    1
8LR9chxF  Skront's Wooden Stuff                                Skront                    1.3
pkqBedwn  Spacious Stable                                      InsightCheque             1.1
u492rwJO  Stained Glass Windows                                Olooriel                  1
LLmsOZ4X  T23's Royal Furniture                                Toblakai23                1
H2ndnvOE  TygerBar                                             Tyger_purr                1.1
MJQ9gdYx  TygerLibrary                                         Tyger_purr                1
pMI97nEl  TygerMusic                                           Tyger_purr                1.1
sI3jbFGs  TygerNautical                                        Tyger_purr                2.1
CJYX8Yjo  TygerWagons                                          Tyger_purr                1
s7XNt1yd  Unofficial Jonathan Roberts Free Pack                (nessuno)                  1
WFWMFRDX  WFW 5th Anniversary Free Megapack                    White Fox Works           1
ygxXFHkC  WFW Sample Pack                                      White Fox Works           1
```

Il template vuoto referenzia un solo pack: `FA30DDXY` (`FA_Starter_Pack_v3.0`,
Forgotten Adventures) — quello incluso di default con l'installazione.

## 3. Contenuto del template ricco: cosa c'e e cosa manca

Verificato per ispezione diretta di `templates/rich_reference.dungeondraft_map`:

| Elemento richiesto da SPEC.md §3 | Presente? | Dettaglio |
|---|---|---|
| muro | si | 2 `walls` |
| porta | si | portal con `texture: res://textures/portals/door_00.png` |
| finestra | si | portal con `texture: res://textures/portals/window_05.png` |
| pavimento | si | 2 `patterns` (`tileset_brick_basketweave.png`, `tileset_cobble.png`) |
| oggetto | si | 1 `object` (`campfire_07.png`) |
| **luce** | si | 1 `light` — vedi schema in §4 |
| tetto | si | 1 `roof` (`flat_clay_red/tiles.png`) |
| percorso (path) | **NO** | 0 elementi in `paths`. Non blocca TASK-2 (l'AC5 di questo task richiede solo luce+testo), ma va tenuto presente: se in futuro serve calibrare `add_path` su un esempio reale, questo template non lo fornisce. Lo schema di `path` e comunque gia verificato in SPEC.md §13 (non e fra i due campi marcati "non verificati"), quindi non blocca `build.py`. |
| **testo** | si | 1 `text` — vedi schema in §4 |

**Condizione di stop dell'AC5 di TASK-2 (luce e testo assenti): non applicabile.**
Il template ricco contiene sia una luce sia un testo: si procede senza fermarsi.

## 4. Schema di `light` e `text` (TASK-3 — derivazione consolidata)

Questi due schemi **non erano verificati** in SPEC.md §13. Oltre al campione
di `rich_reference.dungeondraft_map` (TASK-2), sono state ispezionate le
mappe reali della campagna di Jay in `NovaMistralis/`, che contengono luci
in quantita (fino a 41 per mappa). **Attenzione: quella derivazione ha
prodotto una conclusione sbagliata sulle luci, corretta in TASK-42 — vedi
sotto.** Per `text` non e stato trovato nessun altro
campione: resta **un solo esemplare** in tutto il progetto (verificato
anche nelle mappe di terze parti in `dungeondraft_maps/crosshead_style/`,
che non ne contengono nessuno).

### `light` — `texture` e obbligatoria (corretto in TASK-42)

> **Questa sezione e stata riscritta.** La derivazione originale di TASK-3
> concludeva che esistessero due varianti e che quella *senza*
> `rotation`/`texture` fosse la forma normale, perche osservata su 82
> campioni contro 1. **Quella conclusione era sbagliata**: i campioni
> venivano da file che Dungeondraft non riesce a riaprire.

**Una `light` priva del campo `texture` manda Dungeondraft 1.2.0.1 in loop
infinito al caricamento.** Il file non da errori e non fa crashare il
programma: il JSON viene letto senza lamentele e il blocco avviene dopo,
nella costruzione della scena. Basta **una sola** luce per bloccare la
mappa; oggetti, muri, ombre, colore, ambient e numero di livelli sono
irrilevanti.

Verificato con Jay (TASK-42) su due file identici a meno di questi campi:
`blank_80x80` piu una luce senza `texture` non si apre; lo stesso file con
`rotation: 0` e `texture: res://textures/lights/fragments.png` si apre.

#### Perche i "82 campioni" non valgono

Le 82 luci senza `texture` provenivano tutte e sole da quattro mappe di
Jay: `Carcere_Nova` (20), `Carcere_Nova_2` (20),
`Carcere_Nova_Mistralis_PianoTerra` (21), `ProvaMappa` (21). Jay ha
confermato che **`Carcere_Nova` e `Carcere_Nova_2` non si aprono** e li ha
cancellati; le altre due sono quasi certamente rotte allo stesso modo.
**Non vanno piu usate come evidenza sullo schema delle luci.** Restano
valide come fonte per il catalogo texture (`data/assets.json`): i path che
contengono sono reali, ed e verificato che una mappa generata con quelle
texture si apre senza problemi.

L'unico campione di luce che si apre davvero e quello di
`templates/rich_reference.dungeondraft_map`, scritto da Dungeondraft
1.2.0.1:

```json
{
  "position": "Vector2( 9355.93, 9866.53 )",
  "rotation": 0,
  "range": 5,
  "intensity": 1,
  "color": "ffeccd8b",
  "texture": "res://textures/lights/fragments.png",
  "shadows": true,
  "node_id": "9"
}
```

#### Default reali, dagli asset interni del programma

Estratti da `Light2D.tscn` dentro `Dungeondraft.pck`:

```
[ext_resource path="res://textures/lights/soft.png" type="Texture" id=1]
[node name="Light2D" type="Light2D"]
texture = ExtResource( 1 )
texture_scale = 0.75
color = Color( 0.937255, 0.752941, 0.360784, 1 )   # = efc05c
energy = 0.75
```

Le uniche texture di luce esistenti nel programma sono `soft.png` (il
default), `point.png` e `fragments.png` (decorativa).

#### Campi

- `position`: Vector2.
- `rotation`: float. **Obbligatorio**, emesso sempre.
- `texture`: path `res://`. **Obbligatorio**, emesso sempre; default
  `res://textures/lights/soft.png`.
- `range`: float, raggio in quadretti (non pixel). Valori osservati fra
  1.5 e 6.0.
- `color`: esadecimale a **6 cifre RGB oppure 8 cifre ARGB** — entrambi
  accettati da Dungeondraft, verificato su file che si aprono. Non passare
  comunque per `godot.argb()`: il default e `efc05c`, quello del programma.
- `intensity`: float, default `0.75`. Valori osservati fra 0.45 e 1.0.
- `shadows`: bool. **Ipotizzato, non osservato in un file scritto da
  Dungeondraft:** che `false` sia accettato. E comunque irrilevante per il
  caricamento: un file con `shadows: false` e senza `texture` si blocca
  lo stesso.

`validate` applica **DDF016** (errore) su ogni luce priva di `texture`.

L'elemento non e annidato in nessun'altra struttura: e un elemento di primo
livello in `level.lights`.

### `text` (osservato, 1 solo campione in tutto il progetto)

```json
{
  "text": "Fiumicello",
  "position": "Vector2( 8374.57, 8793.2 )",
  "font_name": "Libre Baskerville",
  "font_size": 32,
  "font_color": "ff000000",
  "box_shape": 0,
  "node_id": "a"
}
```

Tutti i campi **osservati** (non ipotizzati), ma su un solo esemplare:

- `text`: stringa, il contenuto letterale.
- `position`: Vector2.
- `font_name`: stringa, nome del font di sistema/Godot (`"Libre Baskerville"`).
- `font_size`: intero, in punti presumibilmente (32 qui).
- `font_color`: colore 8 cifre ARGB (coerente con `godot.argb()`, a
  differenza di `light.color`).
- `box_shape`: intero, **significato non determinato — ipotizzato essere un
  enum per la forma dello sfondo/box del testo** (0 osservato, valori
  alternativi non noti). Nessuna seconda istanza disponibile per
  confrontare. Se `build.add_text` (TASK-10) necessita di variare
  `box_shape`, va prima chiesto a Jay di esportare un template con piu
  testi diversi, oppure sperimentato direttamente in Dungeondraft
  osservando l'effetto — non va inventato un valore.
- Nessun campo di rotazione osservato per `text`.

**Condizione di stop dell'AC5 di TASK-3: non applicabile.** Il template
ricco contiene sia luci sia testi (confermato anche in TASK-2): si procede.

## 5. Schema di riferimento consolidato di tutti gli elementi

Riferimento unico del progetto (AC4 di TASK-3): schema verificato di ogni
tipo di elemento disegnabile. `wall`, `portal` (variante annidata),
`pattern`, `object`, `path` e `roof` sono presi da SPEC.md §13 (verificati
sull'analisi originale su mappe 1.0.4.x) e confermati compatibili con la
build 1.2.0.1 osservata nei template di questo progetto, salvo le eccezioni
segnalate esplicitamente. `light` e `text` sono quelli derivati sopra (§4).

### `wall`

```json
{
  "points": "PoolVector2Array( 512, 512, 2048, 512 )",
  "texture": "res://textures/walls/stone.png",
  "color": "ffffffff",
  "loop": true,
  "type": 1,
  "joint": 0,
  "normalize_uv": true,
  "shadow": true,
  "node_id": "8e",
  "portals": []
}
```

`type` osservato sempre `1`. `joint`: `0` o `1`. `portals` e la lista delle
porte annidate (vedi sotto): sempre presente, anche se vuota.

### `portal` (annidato in `wall.portals` — l'unico tipo che il generatore deve produrre)

```json
{
  "position": "Vector2( 5504, 1792 )",
  "rotation": 3.141593,
  "scale": "Vector2( 1, 1 )",
  "direction": "Vector2( -1, 0 )",
  "texture": "res://packs/xjCzavyl/textures/portals/door_metal_03.png",
  "radius": 128,
  "wall_id": "8e",
  "wall_distance": 0.5,
  "closed": true,
  "node_id": "90",
  "locked": true
}
```

**Eccezioni osservate in build 1.2.0.1** (§6-7 sotto per il dettaglio):
campo `point_index` aggiuntivo osservato in `rich_reference`; campo
`locked` assente quando la porta non e bloccata (ipotesi, non confermata).
Esiste anche un secondo tipo di `portal`, non annidato e con schema
completamente diverso, usato per porte posizionate liberamente: **il
generatore di questo progetto non lo produce mai** (§7).

**`direction` e la TANGENTE del muro, non la normale — CALIBRATO dal gate
umano TASK-12 (screenshot `task12.png`, `task12_zoom.png`,
`task12_selected.png`).** La prima ipotesi (TASK-18: normale uscente dalla
stanza, perpendicolare al muro) produceva una porta ruotata di 90 gradi:
nello screenshot il muro col la porta appariva visivamente spezzato in due
segmenti storti, con la porta (evidenziata in blu nello screenshot
"selected") disegnata quasi verticale invece che distesa nel muro
orizzontale. Confrontando di nuovo i 2 campioni reali di
`rich_reference.dungeondraft_map`, `direction` risulta essere esattamente
il vettore tangente del muro (dal primo punto all'ultimo), non la normale:

| muro (`points`) | tangente (punto0->puntoN) | `direction` osservata |
|---|---|---|
| verticale `(8704,9216)->(8704,10496)` | `(0, 1)` | `(0, 1)` — combacia |
| orizzontale `(8704,10496)->(9984,10496)` | `(1, 0)` | `(1, 0)` — combacia |

`rotation = atan2(direction.y, direction.x)` resta corretta (era gia stata
verificata su 3 campioni, docs/format.md §5 versione precedente): quello
che era sbagliato era il calcolo di `direction` stesso, non la formula che
ne deriva `rotation`. `compose._wall_tangent` (ex `_outward_normal`,
rinominata dopo la correzione) ora restituisce semplicemente la tangente
del muro. Rigenerato `generated/demo_m1.dungeondraft_map`: la porta ora ha
`direction=(-1,0)`, `rotation=3.141593`, identico all'esempio verificato
di SPEC.md §13. In attesa di una nuova conferma visiva da Jay.

### `pattern`

```json
{
  "position": "Vector2( 0, 0 )",
  "shape_rotation": 0,
  "rotation": 0,
  "scale": "Vector2( 1, 1 )",
  "points": "PoolVector2Array( 2816, 512, 3840, 512, 3840, 1280, 2816, 1280 )",
  "layer": -400,
  "color": "ffffffff",
  "outline": false,
  "texture": "...",
  "node_id": "1a",
  "locked": true
}
```

### `object`

```json
{
  "position": "Vector2( 1029.38, 979.371 )",
  "rotation": -1.047195,
  "scale": "Vector2( 1, 1 )",
  "mirror": false,
  "texture": "...",
  "layer": 100,
  "shadow": false,
  "block_light": false,
  "node_id": "a0d"
}
```

### `path`

```json
{
  "position": "Vector2( 4608, 3456 )",
  "rotation": 0,
  "scale": "Vector2( 1, 1 )",
  "edit_points": "PoolVector2Array( 0, 0, 2560, 0 )",
  "smoothness": 1,
  "texture": "...",
  "width": 472,
  "layer": 100,
  "fade_in": false,
  "fade_out": false,
  "grow": false,
  "shrink": false,
  "block_light": false,
  "loop": false,
  "node_id": "a30"
}
```

`edit_points` sono relativi a `position` (`position` = primo punto). Nessun
campione reale disponibile in questo progetto (§3): schema preso
integralmente da SPEC.md §13, non riverificato qui.

### `roof` (dentro `level.roofs.roofs`)

```json
{
  "position": "Vector2( 0, 0 )",
  "rotation": 0,
  "scale": "Vector2( 1, 1 )",
  "points": "PoolVector2Array( 8960, 5888, 8960, 4352 )",
  "texture": "...",
  "width": 512,
  "type": 0,
  "node_id": "7e5"
}
```

Contenitore: `{"shade": true, "shade_contrast": 0.5, "sun_direction": 45, "roofs": [...]}`.

### `light` e `text`

Vedi §4 sopra: entrambi derivati per questo progetto, `light` ha due
varianti osservate, `text` un solo campione.

## 6. Differenza osservata nello schema `portal` rispetto a SPEC.md §13

Il portal osservato nel template ricco (build 1.2.0.1) ha un campo
**`point_index`** non presente nello schema documentato in SPEC.md §13
(derivato da mappe 1.0.4.x):

```json
{
  "rotation": 1.570796,
  "scale": "Vector2( 1, 1 )",
  "direction": "Vector2( 0, 1 )",
  "texture": "res://textures/portals/door_00.png",
  "radius": 128,
  "point_index": 0,
  "wall_id": "0",
  "wall_distance": 0.5,
  "closed": true,
  "node_id": "1"
}
```

Nessuno dei due portali osservati ha il campo `locked` (che SPEC.md §13
mostra con valore `true` in un esempio): probabilmente e omesso quando la
porta non e bloccata, oppure il default e cambiato fra le build. Da
confermare quando si implementa `build.add_portal` (TASK-10): se
Dungeondraft accetta il documento anche senza `locked`, ometterlo per le
porte sbloccate invece di scrivere sempre `"locked": false`.

## 7. Scoperta importante: esistono due schemi di `portal` distinti

L'ispezione delle mappe reali della campagna di Jay (`NovaMistralis/`, non
template ma mappe di gioco vere, disegnate a mano nell'editor) mostra un
secondo tipo di `portal` **non annidato in nessun muro**, molto diverso da
quello documentato in SPEC.md §13 e osservato in `rich_reference.dungeondraft_map`:

```json
{
  "position": "Vector2( 5248, 2304 )",
  "rotation": 0.0,
  "texture": "res://textures/portals/door_wood_single.png",
  "occludes_light": true,
  "node_id": "19"
}
```

Confermato identico (stesso set di campi: `position`, `rotation`, `texture`,
`occludes_light`, `node_id`) su due mappe diverse
(`Mappe/Carcere_Nova.dungeondraft_map`, 18 istanze, e
`Da espandere/.../ProvaMappa.dungeondraft_map`, 14 istanze). Vive in
`level.portals` (la lista di primo livello prevista da `LEVEL_KEYS`), **non**
in `wall['portals']`. Non ha `wall_id`, `wall_distance`, `radius`,
`direction`, `scale` ne `closed`: sembra un posizionamento libero della porta
(non agganciata a un muro), con `occludes_light` al posto di `closed` per
controllare se blocca la luce/visione.

**Questo contraddice la regola di SPEC.md §14** ("porte a livello mappa →
porte fuori dai muri → annidale in wall.portals, mai a livello mappa"), che
resta pero corretta per il tipo di porta che il generatore di questo
progetto deve produrre: `compose.connect` (TASK-19) e pensato per trovare un
muro condiviso e agganciarci la porta con una frazione `t`, quindi il
generatore continuera a usare **esclusivamente** il tipo annidato (quello
verificato in `rich_reference.dungeondraft_map` e in SPEC.md §13). Non c'e
motivo di generare porte libere: gli edifici e i dungeon generati hanno
sempre un muro su cui agganciare la porta.

**Implicazione da non perdere per le milestone successive:**

- **TASK-13 (validate.py, DDF012/DDF013):** le regole "ogni `portal.wall_id`
  esiste fra i `node_id` dei muri" e "ogni `portal.wall_distance` ∈ [0, 1]"
  vanno applicate solo ai portal annidati in `wall['portals']`. Se il
  validatore itera anche su un eventuale `level['portals']` di primo livello
  (che esiste come chiave nello schema — vedi `LEVEL_KEYS` — anche se il
  generatore la lascia sempre vuota), non deve pretendere `wall_id` su
  elementi che per costruzione non ce l'hanno. Il modo piu semplice: il
  generatore lascia sempre `level['portals']` vuoto (coerente con
  `blank_level` che la svuota comunque) e il validatore verifica solo i
  portal annidati nei muri.
- **TASK-10 (build.py):** `add_portal` continua a scrivere esclusivamente
  dentro `wall['portals']`, come da SPEC.md §6.5. Non serve una primitiva per
  il tipo libero: fuori perimetro per questo progetto.

## 8. File `.dungeondraft_map` trovati sul sistema (catalogo completo)

Ricerca eseguita su home directory, Desktop, Documents, Downloads,
`%AppData%\Roaming\Dungeondraft`, e le cartelle di lavoro sotto
`source/github`. Nessun altro file trovato altrove sul disco.

### 7.1 Candidati al ruolo di template (cartella `Desktop/ddraft_examples/`)

| File | Dimensione file | world (w×h) | format | build | pack | elementi |
|---|---:|---|---|---|---:|---|
| `template_80x80.dungeondraft_map` | 1.659.493 B | 80×80 | 3 | 1.2.0.1 opulent kirin | 1 | 0 in tutte le liste — **usato come blank** |
| `template_ricco.dungeondraft_map` | 1.690.233 B | 80×80 | 3 | 1.2.0.1 opulent kirin | 42 | 2 patterns, 2 walls (2 portals annidati), 1 object, 1 light, 1 text, 1 roof, 0 paths — **usato come rich** |
| `mappa_ricca.dungeondraft_map` | 1.690.233 B | 80×80 | 3 | 1.2.0.1 opulent kirin | 42 | identico byte-per-byte a `template_ricco.dungeondraft_map` (SHA-256 uguale) |

### 7.2 Backup automatico di Dungeondraft

| File | Dimensione | world (w×h) | format | build | pack | elementi |
|---|---:|---|---|---|---:|---|
| `%AppData%\Roaming\Dungeondraft\backups\mappa_ricca.dungeondraft_map` | 436.003 B | 40×40 | 3 | 1.2.0.1 opulent kirin | 42 | 2 patterns, 2 walls (2 portals annidati), 0 object/light/text — snapshot intermedio, meno completo della versione su Desktop. **Non usato**: interessante solo perche conferma che Jay ha lavorato anche a 40×40 in passato, ma la versione finale e la 80×80 su Desktop. |

### 7.3 File esclusi perche non genuini: `fortezza_san_leandro.dungeondraft_map`

`Desktop/fortezza_san_leandro.dungeondraft_map` (62.437 B, dichiara
`creation_build: "1.0.4.3 treacherous tiefling"`) **non e un export reale
di Dungeondraft** ed e stato escluso dal catalogo dei template. Evidenza:

- `world` contiene **solo** la chiave `levels`: mancano `format`, `width`,
  `height`, `next_node_id`, `msi`, `grid`, `embedded` — tutti obbligatori
  per DDF001/DDF002.
- `header.asset_manifest` e vuoto (0 pack) nonostante le texture usate
  puntino a `res://textures/...` (percorsi validi solo per gli asset di
  base, plausibile) ma la struttura generale non torna.
- **`pattern.points` e una lista di stringhe `Vector2(...)` separate**,
  non un'unica stringa `PoolVector2Array(...)` appiattita — esattamente la
  trappola numero uno descritta in SPEC.md §14 ("`points` come lista di
  Vector2 → muri e pavimenti assenti").
- I colori sono a 6 cifre (`"ffffff"`), non 8 cifre ARGB.
- I `node_id` sono stringhe tipo `"p1"`, `"p2"` — non esadecimali.

**Conclusione: questo file e quasi certamente un artefatto del tentativo
precedente fallito citato in SPEC.md §2** ("generava JSON sintatticamente
valido che Dungeondraft apriva vuoto, senza messaggio di errore"), non un
file esportato dall'applicazione. Non va usato come riferimento per nessuno
schema. Puo pero essere utile in TASK-15 come fixture "corrotta" gia pronta
per testare DDF002/DDF007/DDF009 nel validatore, se si preferisce a fixture
costruite ad hoc.

### 7.4 Mappe reali della campagna (Nova Mistralis, cartella `source/github/NovaMistralis`)

Non sono template ma mappe di gioco vere e proprie della campagna di Jay
("Carcere" = complesso carcerario, coerente col mondo Nova Mistralis citato
in SPEC.md). Tutte in build 1.2.0.1, format 3. Utili in futuro come casi
reali su cui far girare `ddforge validate` per verificare che il validatore
non produca falsi positivi su mappe fatte a mano.

| File | Dimensione | world (w×h) | pack | elementi (patterns/walls/portals annidati/objects/lights) |
|---|---:|---|---:|---|
| `Da espandere/Bozze - Atto 1/Carcere/Carcere1.dungeondraft_map` | 2.986.106 B | 80×80 | 2 | 0/45/31/0/0 |
| `Da espandere/Bozze - Atto 1/Carcere/Carcere_Nova_Mistralis_PianoTerra.dungeondraft_map` | 210.706 B | 35×20 | 0 | 9/35/14/0/21 |
| `Da espandere/Bozze - Atto 1/Carcere/cave1.dungeondraft_map` | 190.836 B | 35×20 | 2 | 0/0/0/0/0 |
| `Da espandere/Bozze - Atto 1/Carcere/prova2.dungeondraft_map` | 193.347 B | 35×20 | 2 | 0/6/1/0/0 |
| `Da espandere/Bozze - Atto 1/Carcere/prova3.dungeondraft_map` | 197.061 B | 35×20 | 2 | 0/11/5/0/0 |
| `Da espandere/Bozze - Atto 1/Carcere/ProvaMappa.dungeondraft_map` | 202.605 B | 35×20 | 0 | 9/16/0/0/21 (14 portali qui sono top-level, non annidati — struttura da verificare se questo file viene usato) |
| `Mappe/Carcere_celle.dungeondraft_map` | 594.142 B | 65×31 | 4 | 0/62/53/47/0 |
| `Mappe/Carcere_Nova.dungeondraft_map` | 384.516 B | 40×32 | 2 | 9/51/0*/55/20 (*18 portali top-level, non annidati) |
| `Mappe/Carcere_Nova_2.dungeondraft_map` | 384.153 B | 40×32 | 1 | 9/51/0*/55/20 (*18 portali top-level, non annidati) |
| `Mappe/Carcere_sotterraneo.dungeondraft_map` | 334.075 B | 40×30 | 0 | 0/10/14/5/0 |
| `Mappe/Carcere_torre.dungeondraft_map` | 577.253 B | 55×38 | 0 | 10/26/3/14/0 |

### 7.5 Mappe di terze parti (repo `source/github/dungeondraft_maps`, stile "Crosshead")

Repository Git separato di mappe di esempio scaricate/di terze parti, usato
presumibilmente come riferimento stilistico. Build fra `1.0.1.3` e
`1.1.0.5`, **piu vecchie dell'installazione corrente di Jay (1.2.0.1)**:
escluse dal ruolo di template per lo stesso motivo per cui SPEC.md richiede
di usare template dell'installazione reale dell'utente, non file di terzi.
Elencate qui solo per completezza del censimento richiesto dall'AC1.

| File | Dimensione | world (w×h) | build | pack | livelli |
|---|---:|---|---|---:|---:|
| `Conyberry.dungeondraft_map` | 3.955.789 B | 64×44 | 1.0.3.2 tricky vampire | 11 | 3 |
| `corpse_flower.dungeondraft_map` | 27.382 B | 8×8 | 1.0.4.7 corrosive medusa | 10 | 1 |
| `forest_fort_ruins.dungeondraft_map` | 618.711 B | 40×30 | 1.0.4.7 corrosive medusa | 12 | 1 |
| `old_owl_well_underground_cave.dungeondraft_map` | 1.230.988 B | 50×40 | 1.0.3.2 tricky vampire | 11 | 2 |
| `Pahla_Manor.dungeondraft_map` | 1.842.414 B | 50×25 | 1.0.4.7 corrosive medusa | 12 | 3 |
| `path_through_hills.dungeondraft_map` | 494.002 B | 50×30 | 1.1.0.5 pudgy phoenix | 13 | 1 |
| `path_through_hills_2.dungeondraft_map` | 1.193.992 B | 40×30 | 1.1.0.5 pudgy phoenix | 13 | 2 |
| `random_encounters/Hill_Rock_Dirt_Earth_Stone_Wildernis.dungeondraft_map` | 293.772 B | 30×30 | 1.0.3.2 tricky vampire | 13 | 1 |
| `Spiritual_Weapon_Rose_Entwined_Sword.dungeondraft_map` | 31.983 B | 8×8 | 1.0.4.7 corrosive medusa | 9 | 1 |
| `tresendar_manor_full.dungeondraft_map` | 1.392.564 B | 32×20 | 1.0.3.2 tricky vampire | 8 | 6 |
| `tua_lia_tower.dungeondraft_map` | 1.845.865 B | 40×30 | 1.0.3.2 tricky vampire | 7 | 5 |
| `wyvern_tor_orc_camp.dungeondraft_map` | 2.114.629 B | 40×44 | 1.0.1.3 awaken dryad | 7 | 4 |

Nota: questi file confermano comunque che `world.format = 3` e stabile da
almeno la build `1.0.1.3` fino alla `1.2.0.1` attuale — utile per sapere che
il formato non e cambiato di recente, anche se i template da usare restano
quelli dell'installazione corrente.

## 9. Regole definitive di orientamento e allineamento (gate umani M1 e M3)

Regole ricavate aprendo davvero i file generati in Dungeondraft, non dallo
schema. Sono **codificate nel codice**, non solo scritte qui: accanto a
ciascuna e indicato dove vive e quale test la protegge.

### 9.1 Orientamento della porta: `direction` e la tangente del muro

`portal.direction` **non** e la normale uscente dalla stanza, e la tangente
del muro (parallela, dal primo all'ultimo punto), e
`rotation = atan2(direction.y, direction.x)`.

Trovata nel gate M1 (TASK-12): con la normale, la porta appariva ruotata di
90° e visivamente spezzava il muro in due segmenti storti. Confermata sui
campioni reali di `rich_reference` (§5): muro verticale
`(8704,9216)→(8704,10496)` ha `direction` `(0,1)`; muro orizzontale
`(8704,10496)→(9984,10496)` ha `(1,0)`.

- Codice: `compose._wall_tangent` e `compose._rotation_for_direction`.
- Test: `tests/test_compose.py`.

### 9.2 L'orientamento di un corridoio e un dato, non si deduce

Un corridoio e un **canale aperto**: si disegnano solo i due lati lunghi
(paralleli alla direzione di marcia), mai le testate. Un box chiuso a 4
muri ribloccherebbe la porta appena tagliata nel muro della stanza
all'estremita (TASK-19).

Quali siano i lati lunghi **va saputo, non indovinato**. Fino al gate M3 si
derivava da `rect.w >= rect.h` ("piu largo che alto → orizzontale"), che
sembrava sicuro perche un canale e sempre molto piu lungo che largo. Non lo
e nel caso che conta: il segmento di raccordo fra due stanze separate da un
solo quadretto e **1×1**, l'euristica lo dichiarava orizzontale anche quando
era un passaggio verticale, e i muri finivano sulle testate **sigillando il
passaggio**. E' il difetto che Jay ha visto in Dungeondraft come "i muri
girati sui lati sbagliati" (TASK-26). Su 40 seed di prova, 102 segmenti
ricadevano in questo caso ambiguo.

- Codice: `model.Corridor.horizontal` (campo esplicito, popolato da
  `compose.plan_corridor`) e `compose._long_sides`.
- Test: `tests/test_corridor_routing.py::test_square_elbow_segment_keeps_its_real_orientation`.

### 9.3 Il muro di un canale si ferma dove ne inizia un altro

Nel gomito di una L i due bracci si sovrappongono sul quadrato d'angolo: il
pavimento non ha buchi, ma il muro del braccio orizzontale attraverserebbe
l'imbocco di quello verticale, murandolo a meta. Regola: **un muro di canale
non viene disegnato nel tratto che cade dentro un altro canale** (bordo
escluso: appoggiarsi al bordo dell'altro canale e proprio cio che chiude
l'angolo esterno del gomito).

Conseguenza operativa: i corridoi vanno disegnati **in blocco**, mai uno
alla volta, perche ogni braccio deve sapere dove passano gli altri.

- Codice: `compose._channel_wall_pieces`, usato solo da
  `compose.draw_corridor_network`.
- Test: `tests/test_corridor_routing.py::test_render_draws_the_long_sides_of_a_vertical_square_channel`.

### 9.4 Un corridoio non attraversa mai una stanza

La rotta fra due stanze si sceglie fra piu candidate (dritta con l'asse
spostabile dentro la banda condivisa, L che esce in orizzontale, L che esce
in verticale) prendendo la prima che non entra in nessun'altra stanza. La
rotta a L predefinita, presa alla cieca, passava dritta dentro quello che
trovava: nel gate M3 Jay ha segnalato un corridoio che "interseca altre
stanze" e uno che "entra completamente" nella stanza in alto a sinistra
(TASK-26). Su 40 seed di prova, 37 avevano almeno un attraversamento.

Tre regole concorrono, e servono tutte e tre:

1. **Rotta consapevole degli ostacoli** — `compose.plan_corridor(...,
   obstacles=...)`. Da sola porta 37 seed su 40 a 14.
2. **Collegare le stanze piu vicine** — le due meta di una partizione BSP si
   collegano attraverso la coppia di stanze piu vicina al taglio, non
   attraverso due rappresentanti a caso: cosi ogni corridoio resta locale.
   Con il rappresentante casuale capitava che due stanze agli angoli opposti
   della mappa si collegassero fra loro (`bsp._connect_subtree`).
3. **I collegamenti facoltativi rinunciano** — anelli extra e porte segrete
   sono un abbellimento: se la rotta migliore entra comunque in una terza
   stanza, il collegamento non si fa (`_connect_rooms(require_clean=True)`).
   La connettivita non ne soffre, la garantisce l'albero.

In piu, l'ingrandimento della stanza boss tratta i corridoi gia tracciati
come ostacoli quanto le stanze (`bsp._enlarge_room`): allargarsi sopra un
corridoio produrrebbe lo stesso difetto dal lato opposto.

- Test: `tests/test_corridor_routing.py::test_no_corridor_crosses_a_room_on_any_seed`
  (40 seed) e `::test_m3_seed_1337_has_no_corridor_crossing_a_room` (il caso
  esatto aperto da Jay).

### 9.5 Nota sul falso positivo DDF102

Da quando i bracci della L si uniscono davvero (§9.3), i loro muri
condividono un estremo e formano un gruppo connesso senza porte: e
esattamente il caso che `validate._check_ddf102_unreachable_rooms` non sa
distinguere da una stanza irraggiungibile (il validatore non sa quali muri
appartengano a un corridoio). Warning non bloccante, gia documentato nel
validatore. Su una mappa vera non compare: `generated/dungeon_m3` valida
senza nessun problema.

### 9.6 Ingrandire una stanza deve riproiettare le sue porte

`Door.t` e una frazione del muro su cui la porta e appoggiata: dipende dalla
**lunghezza** di quel muro, non solo dalla sua posizione. `bsp._enlarge_room`
(usata per la stanza boss) allarga solo i lati senza porte, ma allargare un
lato PERPENDICOLARE allunga comunque il muro adiacente su cui una porta e
gia appoggiata — la porta scivola via insieme a lui, anche se il lato che
la porta, di per se, non si e mosso.

Alla riapertura del gate M3, Jay ha trovato esattamente questo: la porta
della stanza boss, allineata al corridoio esterno a x=31.0, era slittata a
x=31.487 dopo l'ingrandimento, lasciando mezzo quadretto di muro in mezzo al
passaggio. Regola: ogni ingrandimento di stanza con porte esistenti deve
**riproiettare** ciascuna porta sul nuovo perimetro al punto assoluto che
occupava prima, non lasciare `t` invariato.

- Codice: `bsp._reproject_doors`, chiamata da `bsp._enlarge_room` subito
  dopo aver sostituito `room.rect`.
- Test: `tests/test_corridor_routing.py::test_enlarging_a_room_does_not_move_its_doors`
  (caso minimo) e `::test_m3_seed_1337_has_no_door_offset_from_its_corridor`
  (il caso esatto segnalato da Jay).

### 9.7 Due muri sovrapposti: quello senza porta tappa quello con la porta

Scoperta al gate umano M4 (TASK-30). In un edificio le stanze condividono i
tramezzi e il muro esterno: se il perimetro portante viene disegnato come
quattro muri interi E ogni stanza ridisegna anche i propri lati esterni, ogni
tratto di muro esterno esiste due volte. Dungeondraft li rende come un muro
solo, quindi la duplicazione non si vede � ma un `portal` appartiene a UN
muro, e il gemello cieco che gli sta sopra lo richiude. Nel file del gate
l'ingresso della taverna e la porta del vano scale erano murati esattamente
cosi.

Regole:

1. Ogni segmento sul perimetro portante va disegnato **una volta sola**, dal
   muro portante. Una stanza che appoggia un lato sul perimetro salta quel
   lato (`draw_room(..., skip_sides=...)`) e riporta la sua eventuale porta
   sul muro portante.
2. Fra due ambienti interni i muri restano invece volutamente sdoppiati �
   ciascuno disegna il proprio tramezzo � perche la porta viene bucata su
   **entrambi** (convenzione di `_connect_rooms`). E la sovrapposizione
   asimmetrica a fare danno, non la sovrapposizione in se.
3. Ne segue che il vano scale non puo essere quattro muri ciechi disegnati a
   mano: e un ambiente come gli altri e va trattato come tale, con le porte
   delle stanze adiacenti rispecchiate sui suoi lati
   (`compose._stairwell_room`).

- Codice: `compose.draw_building`, `compose._sides_on_rect`,
  `compose._stairwell_room`, `compose._draw_perimeter(skip_sides=...)`.
- Test: `tests/test_draw_building.py::test_nothing_is_drawn_on_top_of_the_load_bearing_perimeter`,
  `tests/test_building_gate.py::test_stairwell_is_reachable_from_a_room_on_every_floor`.

### 9.8 Scala reale e orientamento degli sprite (gate umano M4 round 2)

Un quadretto di Dungeondraft vale **1.5 m reali** (Jay). Tutto quello che
riguarda dimensioni "da edificio vero" discende da questa costante, e
ignorarla e il modo piu facile per generare una pianta che passa tutti i
test e non sta in piedi: al round 2 una taverna 40x40 quadretti era un
edificio di **60x60 metri** con stanze da 51x27 m.

- Costanti: `building._TILE_METERS`, `_MAX_ROOM_SIDE_M` (12 m di lato
  massimo per una stanza abitata), `_DEFAULT_SIZE` (ingombro realistico per
  tipologia).
- A guidare la suddivisione dev'essere la **dimensione** della stanza, non
  il numero di stanze: `_build_tree` si ferma appena raggiunge
  `rooms_target`, quindi passargli il numero di kind del piano produce
  poche foglie enormi.

**Rotazione di uno sprite addossato a un muro.** Vale
`rotazione = lato * pi/2` con gli indici di lato di `_draw_perimeter`
(0=top -> 0, 1=right -> pi/2, 2=bottom -> pi, 3=left -> 3pi/2). Equivale a
dire che la faccia dello sprite, che a rotazione 0 guarda in giu (+y),
finisce sempre rivolta **verso l'interno** della stanza. Calibrato sul
campione reale del gate: Jay ha raddrizzato a mano i camini sul muro basso
della cucina (y=21) portandoli da `rot=0` a `rot=+-pi`. La formula
precedente — 0 per top E bottom, pi/2 per left E right — lasciava meta
dell'arredo con la faccia contro il muro.

**Compenetrazione.** Il centro di un pezzo addossato sta a **mezzo
quadretto** dal muro (`compose._WALL_OFFSET`), non a uno: cosi uno sprite
1x1 tocca il muro esatto e uno 2x2 (camino, madia) ci entra dentro per
meta, che e come Dungeondraft si aspetta di vederli. Stessa misura di Jay:
camino a y=20.5 con il muro a y=21.

**Sovrapposizione.** Due pezzi non possono stare piu vicini della semisomma
dei loro ingombri (`compose._is_free`, `_texture_size`). L'ingombro si legge
dal nome file quando c'e (`Oven_..._2x2`, `Keg_..._1x1`), altrimenti da una
tabella per nome semantico. Unica eccezione: una sedia attorno al suo
tavolo, dove l'adiacenza stretta e voluta.

**Sprite con asse proprio.** La formula sopra presuppone che a rotazione 0
la faccia dello sprite guardi in giu, e per tutto il catalogo osservato e
vero — con una sola eccezione confermata da Jay al round 3: la botte piccola
(`Keg_..._H_...`, "H" per horizontal) e coricata sul fianco lungo l'asse
orizzontale e parte gia ruotata di un quarto di giro. Non e una regola
geometrica ma una proprieta del singolo sprite, quindi va **tabellata per
texture** (`compose._TEXTURE_ROTATION_OFFSET`) e sommata all'angolo del lato,
mai dedotta.

- Test: `tests/test_building_gate.py::test_a_wall_slot_puts_the_piece_against_the_wall_facing_the_room`,
  `::test_no_two_pieces_of_furniture_overlap`,
  `::test_rooms_have_the_size_of_real_rooms`,
  `::test_a_keg_is_rotated_a_quarter_turn_more_than_everything_else`.

## 10. `data/assets.json` — provenienza (TASK-4)

`rich_reference.dungeondraft_map` da solo ha troppo poche texture per
popolare un catalogo utile (1 muro, 2 pattern, 2 portal, 1 oggetto, 1
tetto). Il file committato in `data/assets.json` e stato generato unendo
`rich_reference.dungeondraft_map` con le mappe reali della campagna di Jay
in `NovaMistralis/` (non template, ma file `.dungeondraft_map` genuini
esportati dalla stessa installazione, quindi con lo stesso `world.format`
e build, e con i pack ID reali nel loro `header.asset_manifest`):

```
templates/rich_reference.dungeondraft_map
NovaMistralis/Mappe/Carcere_celle.dungeondraft_map
NovaMistralis/Mappe/Carcere_Nova.dungeondraft_map
NovaMistralis/Mappe/Carcere_Nova_2.dungeondraft_map
NovaMistralis/Mappe/Carcere_sotterraneo.dungeondraft_map
NovaMistralis/Mappe/Carcere_torre.dungeondraft_map
NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/Carcere1.dungeondraft_map
NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/Carcere_Nova_Mistralis_PianoTerra.dungeondraft_map
NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/prova2.dungeondraft_map
NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/prova3.dungeondraft_map
NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/ProvaMappa.dungeondraft_map
```

Comando esatto usato (`ddforge catalog --from` e ripetibile):

```
ddforge catalog --from templates/rich_reference.dungeondraft_map \
  --from ".../NovaMistralis/Mappe/Carcere_celle.dungeondraft_map" \
  --from ".../NovaMistralis/Mappe/Carcere_Nova.dungeondraft_map" \
  --from ".../NovaMistralis/Mappe/Carcere_Nova_2.dungeondraft_map" \
  --from ".../NovaMistralis/Mappe/Carcere_sotterraneo.dungeondraft_map" \
  --from ".../NovaMistralis/Mappe/Carcere_torre.dungeondraft_map" \
  --from ".../NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/Carcere1.dungeondraft_map" \
  --from ".../NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/Carcere_Nova_Mistralis_PianoTerra.dungeondraft_map" \
  --from ".../NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/prova2.dungeondraft_map" \
  --from ".../NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/prova3.dungeondraft_map" \
  --from ".../NovaMistralis/Da espandere/Bozze - Atto 1/Carcere/ProvaMappa.dungeondraft_map" \
  --out data/assets.json
```

Risultato: 44 pack, 6 walls, 6 floors, 15 portals, 1 roof, 0 paths, 46
oggetti (chiave = slug del nome file). Nessuna texture nel catalogo e stata
inventata: ogni voce e presa letteralmente da uno dei documenti sopra.

**Categorie di SPEC.md §6.7 senza controparte reale, lasciate assenti:**
`torch`, `altar`, `sarcophagus`, `column`, `chest`. Nessuno dei file
`.dungeondraft_map` reali di Jay contiene un oggetto identificabile con
questi nomi. Per popolarle: Jay puo aggiungere un esemplare di ciascuno
al template ricco (o in una qualunque mappa) e rilanciare `ddforge catalog`
con quel file incluso fra i `--from` — mai inventare un path a mano.

**Alias semantici popolati con successo** (nome SPEC.md -> texture reale
trovata): `table_round`, `chair`, `bed`, `crate`, `barrel`, `bookshelf`,
`brazier`. `paths` resta vuota: nessuna mappa reale di Jay usa un elemento
`path`, coerente con quanto gia notato in §3 per `rich_reference`.

## 11. `tests/fixtures/reference_8x8.dungeondraft_map` — provenienza (TASK-5)

Nessun template 8×8 vuoto esiste sull'installazione di Jay (il piu piccolo
file reale trovato e 35×20, §8.4). E stato quindi usato un export genuino
di terze parti gia presente sul sistema:
`source/github/dungeondraft_maps/crosshead_style/corpse_flower.dungeondraft_map`
(build `1.0.4.7 corrosive medusa`, 10 pack, 5 oggetti, 1 percorso — **non e
vuoto** di elementi disegnabili, da cui il nome `reference_8x8` invece di
`blank_8x8` usato inizialmente nell'AC del task).

**Perche va bene comunque come fixture:** le dimensioni dei blob, una volta
interpretate correttamente come stringhe `PoolIntArray`/`PoolByteArray` (non
come lunghezza della stringa JSON grezza — vedi nota metodologica sotto),
coincidono esattamente con l'esempio verificato in SPEC.md §2:

| Campo | Atteso (SPEC.md §2 per 8×8) | Osservato in `reference_8x8` |
|---|---|---|
| `tiles.cells` | `width×height` = 64 elementi | 64 |
| `terrain.splat` | `width×height×64` = 4096 elementi | 4096 |
| `cave.bitmap` | 154 byte (valore noto, non lineare) | 154 elementi |

**Nota (TASK-31):** la colonna "non lineare" qui sopra riporta cio che
SPEC.md §2 credeva. **Non e vero:** la lunghezza di `cave.bitmap` e
`ceil((4w+3)(4h+3)/8)`, e i 154 byte dell'8×8 ne sono un caso particolare.
Vedi §14.

Il file e usato **solo** per verificare le formule dimensionali dei blob e
il meccanismo di `template.blank_level`/`prepare` (TASK-8): non e la fonte
di nessuno schema di elemento (quello resta `rich_reference.dungeondraft_map`
e le mappe reali di Jay, §5). La build piu vecchia non e un problema per
questo scopo: le differenze osservate finora fra build (`point_index` nei
portal, schema di `light`) non riguardano i blob binari.

**Nota metodologica importante (per chi tocca `validate.py`, TASK-13):**
`tiles.cells` e `terrain.splat` sono serializzati come **stringhe**
`"PoolIntArray( ... )"` / `"PoolByteArray( ... )"`, esattamente come
`PoolVector2Array` (§6.1 di SPEC.md). **Non chiamare `len()` sulla stringa
grezza**: bisogna prima fare il parsing (dividere sulla virgola dopo aver
tolto il wrapper `PoolXxxArray( ... )`) e contare gli elementi. Un tentativo
di misurazione errato durante questo task ha inizialmente suggerito che le
formule di DDF010/DDF011 non tornassero su nessun file reale di Jay — errore
di misurazione, non del formato: dopo il parsing corretto, tutte le mappe
controllate (80×80, 35×20, 40×32, 8×8) rispettano le formule esattamente.

## 12. `texts_vis` — 18ª chiave di livello, assente da SPEC.md §13 (TASK-13)

Le 17 chiavi di `LEVEL_KEYS` (SPEC.md §13, `template.py` §6.3) sono state
derivate da mappe build 1.0.4.x. Sia `blank_80x80.dungeondraft_map` sia
`rich_reference.dungeondraft_map` (build 1.2.0.1, i due template di questo
progetto) hanno una **18ª chiave**: `texts_vis`, booleana (`true` in
entrambi), quasi certamente un flag di visibilita del layer testi nell'
editor. La fixture 8×8 di terze parti (build 1.0.4.7, TASK-5) **non** ce
l'ha, confermando che e stata aggiunta in una build successiva.

**Correzione applicata:** `template.LEVEL_KEYS` ora include `texts_vis`
come 18ª voce. `blank_level`/`prepare` non ne risentivano (preservano
sempre tutte le chiavi del livello sorgente, comprese quelle non elencate),
ma `validate.py` (DDF003, TASK-13) avrebbe segnalato un falso errore
"chiave imprevista" su ogni documento reale della build corrente se
`LEVEL_KEYS` fosse rimasto a 17 voci. Nessun'altra chiave extra e stata
trovata nei documenti ispezionati finora.

## 13. Prossimi passi

- **Gate umano M1/M3**: confermare il segno delle rotazioni delle porte e il
  significato di `direction`, aggiornando §6 di questo documento.

## 14. `cave.bitmap` — codifica risolta (TASK-31)

SPEC.md §2 dava la lunghezza di `cave.bitmap` per **non lineare e non
ricavabile per interpolazione** (50×25→2614 B, 30×30→1892 B, 8×8→154 B), e
su questa base SPEC.md §9.3 rimandava a M5 la scelta fra muri poligonali e
layer nativo. **La codifica e stata risolta per intero** nello spike
TASK-31, e la decisione conseguente e registrata nella decision
`decision-1` (layer cave nativo).

### La struttura

`cave.bitmap` e una maschera booleana **bit-packed** su una griglia di

```
(4·width + 3) × (4·height + 3)   BIT
```

cioe **4 sotto-celle per quadretto** (risoluzione di un quarto di
quadretto), piu 3 sotto-celle di margine per lato. Regole di
serializzazione:

- ordine **row-major** (riga per riga);
- flusso di bit **continuo, NON allineato al byte**: una riga non
  ricomincia su un confine di byte, quindi l'offset in byte della riga `k`
  e `floor(k · larghezza_griglia / 8)`;
- dentro ogni byte, **bit meno significativo per primo** (LSB-first):
  il bit `i` del flusso sta in `data[i // 8] >> (i % 8) & 1`;
- `1` = grotta scavata, `0` = roccia intatta;
- lunghezza in byte = `ceil((4w+3)·(4h+3) / 8)`, che dipende **solo** dalle
  dimensioni della mappa e **mai** dal contenuto disegnato (il template
  vuoto ha gia la lunghezza finale, tutta a zero).

`cave.entrance_bitmap` ha esattamente le stesse dimensioni e la stessa
codifica (verificato: round-trip byte-esatto anche su quello). Gli altri
campi di `cave` — `ground_color`, `wall_color`, `texture` — sono gia
popolati nel template vuoto e **non vanno toccati**: scrivere il solo
`bitmap` basta perche Dungeondraft renda la grotta.

### Perche l'analisi precedente si era arenata

Due trappole, entrambe evitabili solo conoscendo la struttura:

1. **La lunghezza sembra irregolare** perche la griglia e a 4×: il termine
   dominante e `2wh` byte, non `wh/8`, e la costante additiva dipende da
   `w+h`. Interpolare fra tre punti non ci arriva.
2. **Il passo fra le righe in byte non e costante** — nel campione 80×80 le
   run di byte non nulli distano 40, 40, 41, 40, 40, 41, … proprio perche
   una riga di 323 bit non e multipla di 8. Cercare una larghezza di riga
   *in byte* (che e quello che si fa istintivamente) non puo funzionare, ed
   e il motivo per cui i tentativi di reshape a 40/41/80/163 colonne
   davano forme "quasi giuste" ma sporche di dither.

Aggiunge rumore anche il fatto che i valori dei byte sono molti e
apparentemente arbitrari (51 valori distinti nel campione a mano libera):
non sono un enum, sono semplicemente gruppi di 8 sotto-celle adiacenti.

### Verifica sperimentale

Il formato non e stato dedotto ma **confermato**, su campioni prodotti da
Jay disegnando nel layer cave con Dungeondraft 1.2.0.1 e risalvando:

| Prova | Esito |
|---|---|
| Formula di lunghezza sui 4 campioni noti (8×8→154, 30×30→1892, 50×25→2614, 80×80→13042) | esatta su tutti e 4 |
| Round-trip `decode`→`encode` sui blob reali di Jay (`bitmap` + `entrance_bitmap` di 2 file) | **byte-identico**, 4 blob su 4 |
| Decodifica del campione controllato (Jay: «circa 20×3 quadretti, in alto a sinistra») | rettangolo di 21×3 quadretti con gli angoli arrotondati dal pennello, in alto a sinistra |
| Decodifica del campione a mano libera | caverna organica con tunnel serpeggiante, palesemente disegnata a mano |
| **Scrittura**: rettangolo generato da noi sui quadretti x 10–20, y 10–15 e riaperto da Jay | compare esattamente dove previsto |
| **Scrittura**: grotta da cellular automata a risoluzione sotto-cella | approvata da Jay |

L'ultima riga e quella che conta di piu: le prime confermano che sappiamo
**leggere** il formato, solo le ultime due che sappiamo **scriverlo** e che
Dungeondraft accetta cio che scriviamo.

**Origine della griglia** (l'unico punto rimasto ambiguo dopo la sola
lettura, perche la posizione dei campioni di Jay era descritta a parole):
la sotto-cella `0` corrisponde al quadretto `0`, e le 3 sotto-celle di
margine stanno **in coda**, non in testa. Risolto dal file di
calibrazione: un rettangolo scritto sui quadretti 10–20 × 10–15 e apparso
esattamente li, non spostato di 0.75 quadretti.

### Campioni (fixture committate)

I due file disegnati da Jay sono l'**unica evidenza reale** di questo
formato in tutto il progetto: nessun altro `.dungeondraft_map` trovato sul
suo sistema (§8) ha il layer cave popolato — in tutti, `cave.bitmap` e
interamente a zero. Sono stati quindi promossi a fixture committate, perche
`generated/` e gitignored e li si perderebbero:

| Fixture | Contenuto | Ruolo |
|---|---|---|
| `tests/fixtures/cave_rect_80x80.dungeondraft_map` | rettangolo netto di 21×3 quadretti in alto a sinistra (Jay: «circa 20×3») | campione **controllato**, disegnato apposta con bordi netti: e quello che ha permesso di risolvere la codifica |
| `tests/fixtures/cave_freehand_80x80.dungeondraft_map` | caverna organica con tunnel serpeggiante | campione **a mano libera**. Contiene anche 1 wall e 1 pattern, resti del prototipo a muri poligonali su cui Jay ha disegnato: e un file reale, non ripulito |

Entrambi salvati da Dungeondraft 1.2.0.1, mappa 80×80, quindi
`cave.bitmap` di 13042 byte.

`tests/test_cave_bitmap_format.py` blocca quanto sopra: formula della
lunghezza sui 4 campioni noti, round-trip byte-esatto sui blob reali
(`bitmap` **e** `entrance_bitmap`), e forma decodificata dei due campioni.
E' il round-trip a inchiodare l'ordine dei bit — la connettivita della
macchia no: con MSB-first il rapporto scende solo da 0.993 a 0.941, troppo
poco per distinguerli.

### Codice

Codec in produzione da TASK-32: `ddforge.cave_bitmap` (`encode_cave_bitmap`,
`decode_cave_bitmap`, `cave_grid_shape`), scritto tramite la primitiva
`build.set_cave_bitmap`. `tests/test_cave_bitmap_format.py` importa da li.

`scripts/cave_spike.py` (spike TASK-31) resta invariato con la sua stessa
copia del codec e i tre modi `--mode walls|native|calib`: e' codice di
spike, non piu l'unica implementazione, ma non e' stato rimosso da
TASK-32.

## 15. `water.tree` — schema del layer acqua nativo (TASK-33)

Mai documentato prima: nessun task precedente aveva bisogno del layer
`water`. Decodificato direttamente da `templates/rich_reference.dungeondraft_map`
(campione che Dungeondraft riapre), non da uno spike a parte come per
`cave.bitmap` (qui non c'e' un blob binario da decifrare, e' JSON puro,
autoesplicativo dal campione).

### La struttura

`level['water']` in `blank_80x80` (il template usato in produzione) e'
`{"disable_border": false}`: **niente chiave `tree`**. La chiave compare
solo quando c'e' davvero dell'acqua disegnata (osservato in
`rich_reference`, che ne ha).

`water.tree` e' un albero binario-poligonale (verosimilmente lo stesso
meccanismo CSG che Dungeondraft usa per `terrain`/`shapes`): un nodo
contenitore alla radice, con `children` che sono i poligoni d'acqua veri.
Ogni nodo, contenitore o poligono, ha lo stesso schema:

```json
{"ref": -1716689034, "polygon": "PoolVector2Array(  )", "join": 0, "end": 0,
 "is_open": false, "deep_color": "00000000", "shallow_color": "00000000",
 "blend_distance": 0, "children": [...]}
```

- `ref`: intero, positivo o negativo, univoco nel documento osservato.
  Nessun controllo di validate.py lo riguarda (DDF005/006 controllano solo
  `node_id`, mai `ref`): probabilmente un id interno dell'editor Godot, non
  un requisito del formato file. `build.add_water_polygon` gli assegna
  comunque un valore univoco (dallo stesso `IdAllocator` dei `node_id`),
  per prudenza.
- `polygon`: `PoolVector2Array` di coordinate **assolute** in pixel (non
  relative a una `position`, a differenza di `path.edit_points`, §5).
- `join`/`end`: sempre `0` in tutti i nodi osservati, significato non
  investigato (probabilmente parametri dell'operazione booleana CSG che
  qui non serve mai: ogni figlio e' un poligono indipendente, mai unito o
  sottratto a un altro).
- `is_open`: sempre `false` osservato, poligono chiuso.
- `deep_color`/`shallow_color`: colori ARGB a 8 cifre. Sul nodo contenitore
  sono sempre `00000000` (trasparente: il contenitore non viene mai
  disegnato lui stesso). Sui poligoni figli sono i colori veri dell'acqua
  (`ff3c8ab8`/`ff54c1da` nel campione osservato: blu-verde standard).
- `blend_distance`: `0` sul contenitore, `1.5` sul poligono figlio nel
  campione osservato (probabilmente la sfumatura fra `deep_color` e
  `shallow_color` verso il bordo, in quadretti).
- `children`: lista di nodi con lo stesso schema, ricorsiva. Nel campione
  osservato il contenitore ha un solo figlio con `children: []` (nessuna
  annidatura piu' profonda osservata).

### Codice

`build.add_water_polygon(level, ids, points_grid, *, deep_color, shallow_color,
blend_distance)` (TASK-33): crea `level['water']['tree']` come nodo
contenitore vuoto al primo utilizzo (se il template non ce l'ha, come
`blank_80x80`), poi appende un figlio per ogni poligono passato. Usato da
`compose.render_sewer_blueprint` per disegnare un poligono d'acqua per ogni
canale e ogni camera della variante fognature.
