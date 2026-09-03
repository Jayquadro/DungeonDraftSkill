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

## 4. Schema di `light` e `text` — osservazione TASK-2, derivazione formale TASK-3

Questi due schemi **non erano verificati** in SPEC.md §13. Quanto segue e
un'osservazione diretta e letterale del singolo esemplare presente nel
template ricco. **Un solo campione non e sufficiente per derivarne le
regole generali** (es. quali campi sono opzionali, quali range sono validi):
questo resta compito di TASK-3, che deve anche verificare se altri
esempi nelle mappe reali di Jay (`NovaMistralis/Mappe/*.dungeondraft_map`,
che contengono fino a 41 luci ciascuna) confermano lo schema.

### `light` (osservato, 1 campione)

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

Non e annidata in nessun'altra struttura: e un elemento di primo livello in
`level.lights`, come le altre liste disegnabili.

### `text` (osservato, 1 campione)

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

`box_shape` e un intero, significato non ancora determinato (probabile enum
per la forma dello sfondo/box del testo: da verificare in TASK-3, magari
provando valori diversi in Dungeondraft e osservando l'effetto).

## 5. Differenza osservata nello schema `portal` rispetto a SPEC.md §13

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

## 6. Scoperta importante: esistono due schemi di `portal` distinti

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

## 7. File `.dungeondraft_map` trovati sul sistema (catalogo completo)

Ricerca eseguita su home directory, Desktop, Documents, Downloads,
`%AppData%\Roaming\Dungeondraft`, e le cartelle di lavoro sotto
`source/github`. Nessun altro file trovato altrove sul disco.

### 6.1 Candidati al ruolo di template (cartella `Desktop/ddraft_examples/`)

| File | Dimensione file | world (w×h) | format | build | pack | elementi |
|---|---:|---|---|---|---:|---|
| `template_80x80.dungeondraft_map` | 1.659.493 B | 80×80 | 3 | 1.2.0.1 opulent kirin | 1 | 0 in tutte le liste — **usato come blank** |
| `template_ricco.dungeondraft_map` | 1.690.233 B | 80×80 | 3 | 1.2.0.1 opulent kirin | 42 | 2 patterns, 2 walls (2 portals annidati), 1 object, 1 light, 1 text, 1 roof, 0 paths — **usato come rich** |
| `mappa_ricca.dungeondraft_map` | 1.690.233 B | 80×80 | 3 | 1.2.0.1 opulent kirin | 42 | identico byte-per-byte a `template_ricco.dungeondraft_map` (SHA-256 uguale) |

### 6.2 Backup automatico di Dungeondraft

| File | Dimensione | world (w×h) | format | build | pack | elementi |
|---|---:|---|---|---|---:|---|
| `%AppData%\Roaming\Dungeondraft\backups\mappa_ricca.dungeondraft_map` | 436.003 B | 40×40 | 3 | 1.2.0.1 opulent kirin | 42 | 2 patterns, 2 walls (2 portals annidati), 0 object/light/text — snapshot intermedio, meno completo della versione su Desktop. **Non usato**: interessante solo perche conferma che Jay ha lavorato anche a 40×40 in passato, ma la versione finale e la 80×80 su Desktop. |

### 6.3 File esclusi perche non genuini: `fortezza_san_leandro.dungeondraft_map`

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

### 6.4 Mappe reali della campagna (Nova Mistralis, cartella `source/github/NovaMistralis`)

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

### 6.5 Mappe di terze parti (repo `source/github/dungeondraft_maps`, stile "Crosshead")

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

## 8. Prossimi passi

- **TASK-3**: derivazione formale dello schema di `lights`/`texts` (piu
  campioni, verifica di `box_shape`), da consolidare in questo stesso file.
- **TASK-4**: generare `data/assets.json` da `templates/rich_reference.dungeondraft_map`
  usando l'elenco pack di §2.
- **Gate umano M1/M3**: confermare il segno delle rotazioni delle porte e il
  significato di `direction`, aggiornando §5 di questo documento.
