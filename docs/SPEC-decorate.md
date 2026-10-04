# SPEC — `ddforge decorate` e la skill `dungeondraft-map-decorator`

Specifica della seconda skill del progetto: presa una mappa gia generata
dalla skill `dungeondraft-map-generator`, la **abbellisce** sul piano
estetico (texture, terreno, oggetti a tema, luci, scenografia naturale)
senza toccarne la geometria tattica.

Stato: **rivista** (2026-10-04). Le scelte marcate *[deciso]* vengono
dalle risposte di Jay ai due giri di raccolta requisiti; quelle marcate
*[proposta]* sono mie e restano da confermare al gate umano; §14 registra
le domande del secondo giro con la risposta data. Il lavoro e tracciato nella milestone Backlog
**M10 — Abbellimento mappe** e la variazione di perimetro in
`backlog/decisions/decision-3`.

---

## 1. Obiettivo e perimetro

### 1.1 Cosa deve fare

L'utente dice qualcosa come *"prendi la cripta di ieri e rendila piu
lugubre, abbandonata da secoli"*. La skill:

1. legge la mappa e il suo sidecar (§4), ne fa un'anteprima PNG;
2. **propone** l'abbellimento stanza per stanza (dry-run, §8.2);
3. raccoglie le correzioni dell'utente come override (§8.3);
4. lancia `ddforge decorate`, che scrive **un nuovo file** valido;
5. consegna il file con l'anteprima prima/dopo.

### 1.2 Cosa comprende

| Area | Esempi | Tocca l'esistente? |
|---|---|---|
| **Texture e terreno** | pavimento diverso per ruolo di stanza, muri per zona, sfumature di terreno (terra, muschio, neve, ghiaia) ai bordi e negli angoli; in citta erba/terra fra gli edifici | si: **sostituisce** la `texture` di pattern e muri esistenti, dipinge il terrain |
| **Oggetti a tema per stanza** | altare e trono nella stanza boss, botti e casse nel magazzino, librerie nello studio; clutter a ridosso dei muri (detriti, ossa, ragnatele, crepe) | no: solo aggiunte |
| **Luci e atmosfera** | torce accanto alle porte, bracieri, luci colorate per tema, `ambient_light` del livello | aggiunge luci; cambia `environment.ambient_light` *[deciso, D4]* |
| **Natura e scenografia** | alberi, cespugli, rocce, funghi nelle grotte, pozzanghere nelle fogne, carretti e vegetazione in citta | no: solo aggiunte (oggetti, poligoni d'acqua) |

Tipi di mappa coperti dalla prima versione *[deciso]*: `dungeon`,
`building`, `cave`, `sewer`, `city` (tutti e tre i preset di scala).

### 1.3 Invarianti — cosa NON fa mai *[deciso]*

- **Non sposta, non cancella, non aggiunge muri, porte, finestre, stanze,
  tetti, testi.** Di muri e pattern puo cambiare solo il campo `texture`.
  Nessun `points`, `position`, `portals` viene alterato.
- **Non rimuove ne sposta oggetti o luci esistenti** (quelli di
  `--furnish`/`--lights` restano: decorate li conta come occupazione).
- **Non sovrascrive l'originale.** Scrive sempre un file nuovo
  (§8.1); se il percorso di uscita coincide con l'ingresso, errore.
- **Non usa pack fuori dal template** *[deciso]*: solo pack gia in
  `header.asset_manifest` e texture presenti in `data/assets.json`. Un
  tema a cui manca un asset **degrada** (salta quella voce con un avviso),
  non inventa un path.
- **Non scrive JSON a mano**: tutto passa da `build.py` / `compose.py` e
  dal validatore, come per `generate`.
- **Non cambia `world.width/height`, i blob `tiles`/`cave`, `world.format`.**

### 1.4 Fuori perimetro

- Mappe disegnate a mano o di terzi, e mappe `ddforge` senza sidecar
  *[deciso]* (§4.4 dice cosa fare con le mappe vecchie).
- Rimuovere o rifare l'arredo esistente.
- Aggiungere pack al manifest.
- Abbellimento "a mano libera" dell'LLM (piazzare un oggetto a coordinate
  scelte dal modello): gli override di §8.3 lavorano per **zona** e
  **alias**, mai per coordinate.

---

## 2. Perche un comando e non una skill che edita il file *[deciso]*

La skill di generazione vieta di toccare il JSON perche il formato e pieno
di vincoli non ovvi (SPEC.md §2, §7, §14): blob dimensionati, `node_id`
univoci e `next_node_id`, pack ID, colori ARGB a 8 cifre, `PoolVector2Array`
come stringa. La stessa regola vale qui: **tutta la logica vive in
`src/ddforge/decorate/`**, la skill sceglie i parametri e legge l'esito.

Questo e anche cio che rende il risultato riproducibile (`--seed`) e
testabile senza Dungeondraft.

---

## 3. Architettura

```
mappa.dungeondraft_map ─┐
                        ├─> load ─> zone ─> planner ─> DecorationPlan ─┬─> stampa (dry-run)
mappa.ddforge.json ─────┘   (doc +   (§5)    (§6, puro)                 └─> apply (§7) ─> validate ─> save
                            Blueprint)
```

Nuovo package `src/ddforge/decorate/`:

| Modulo | Responsabilita |
|---|---|
| `sidecar.py` | serializza/deserializza il Blueprint e i parametri di generazione (§4) |
| `zones.py` | Blueprint → lista di **zone** con id stabile e ruolo semantico (§5) |
| `themes.py` | tabelle dati dei temi (§6.2): solo chiavi del catalogo, nessuna logica |
| `planner.py` | funzione pura `plan(zones, occupazione, tema, intensita, override, seed) -> DecorationPlan` |
| `apply.py` | applica un `DecorationPlan` al documento usando `build.py` |
| `terrain.py` | pittura del `terrain.splat` (dipende dallo spike di §7.3) |
| `occupancy.py` | indice di occupazione: muri, porte con il loro raggio di rispetto, oggetti esistenti (riusa `compose._placed_from_level`) |

`cli.py` riceve il sottocomando `decorate`. Il planner non tocca il
documento: e cio che rende il dry-run gratuito e il piano testabile da solo.

Riuso obbligatorio, non duplicazione: `IdAllocator.from_document` per
continuare la numerazione dei `node_id`, `template.finalize`/`save`,
`build.add_object`/`add_light`/`add_water_polygon`, le regole di
piazzamento e di scala degli sprite gia calibrate nei gate umani
(`compose._wall_slot`, `_sprite_scale`, `docs/format.md` §9.8).

---

## 4. Il sidecar `.ddforge.json` *[deciso: serve]*

Un `.dungeondraft_map` non sa che una stanza e la stanza boss o che un
corridoio e "buio": quella semantica vive solo nel Blueprint, che oggi
`generate` butta via dopo il compose. Senza, decorate dovrebbe ricostruire
le stanze dai muri e perderebbe proprio cio che rende l'abbellimento
sensato.

### 4.1 Cosa scrive `generate`

Accanto a `cripta.dungeondraft_map`, `generate` scrive
`cripta.ddforge.json`, **sempre**, senza un flag per disattivarlo
*[deciso, D2]*:

```json
{
  "ddforge_sidecar": 1,
  "generator": {"algorithm": "dungeon", "args": {"seed": 1337, "rooms": 8, "style": "crypt", "furnish": "medium", "lights": true, "...": "..."}},
  "template": "templates/blank_80x80.dungeondraft_map",
  "catalog_sha256": "…",
  "map_sha256": "…",
  "blueprint": { "…": "serializzazione completa di model.Blueprint, ricorsiva su buildings e landmarks.building" },
  "decorations": []
}
```

- `map_sha256` e l'hash del file mappa **come scritto**: serve a capire se
  la mappa e stata modificata dopo (in Dungeondraft o da altri).
- `decorations` e vuoto per una mappa generata; decorate lo riempie (§4.3).
- Serializzazione: dataclass → dict, con `Rect`/`Corridor` espliciti e tuple
  come liste; round-trip esatto (`load(dump(bp)) == bp`) coperto da test.

### 4.2 Controlli di decorate in lettura

| Situazione | Esito |
|---|---|
| sidecar assente | errore: "mappa senza sidecar, rigenera con `generate` (§4.4)" |
| `ddforge_sidecar` di versione sconosciuta | errore |
| `map_sha256` non corrisponde al file | errore, salvo `--allow-modified` *[deciso, D1]*: con il flag procede, prendendo le zone dal Blueprint e l'occupazione (muri, porte, oggetti) dal file reale, cosi non piazza nulla sopra cio che Jay ha aggiunto a mano; il test di invarianza (DDF203) confronta con il file modificato, non con quello generato |
| `catalog_sha256` diverso dal catalogo attuale | avviso: alcune chiavi potrebbero risolvere su texture diverse |

### 4.3 Mappe gia abbellite

Decorate **parte sempre da una mappa non abbellita** *[proposta]*: se il
sidecar ha `decorations` non vuoto, errore che suggerisce di ripartire
dall'originale. Il file di uscita riceve il proprio sidecar
(`cripta.decorated.ddforge.json`) con il Blueprint invariato e in
`decorations` i parametri della passata (tema, intensita, seed, override,
hash del file di origine). Cosi "rifallo piu lugubre" = rilanciare decorate
sull'originale con altri parametri, mai stratificare passate.

### 4.4 Mappe generate prima del sidecar

`generate` e riproducibile byte per byte dato template + parametri + seed.
Se l'utente ricorda i parametri, basta rigenerare; la skill lo spiega invece
di tentare ricostruzioni.

---

## 5. Zone

Una **zona** e l'unita su cui il planner ragiona e su cui l'utente da
override. Ha: `id` stabile, `kind` (ruolo), un'area (Rect o poligono),
il piano (`level`), le porte che la toccano, flag semantici.

| Mappa | Zone | id | ruoli / flag |
|---|---|---|---|
| dungeon | stanze, corridoi | `r0..rN`, `c0..cN` | `room.kind` (`sala`, `boss`, `secret`…), `tattica` (da `tactical_rooms`), `buio` (da `long_corridor_indices`), `ingresso` |
| building | stanze per piano, vano scale, esterno attorno all'edificio | `p0.r3`, `scale`, `esterno` | `room.kind` (`sala_comune`, `cucina`, `camera`…) |
| cave | regioni del `cave_grid` (componenti connesse, divise in "sale" e "strozzature" per larghezza) | `g0..gN` | `ampia`, `stretta`, `cieca` (vicolo cieco) |
| sewer | canali, camere di giunzione | `k0..kN`, `j0..jN` | `ingresso` |
| city | strade, piazze, cortili (spazio interno ai lotti), fasce extramurali, rive, banchina, landmark open-air | `s0`, `pz0`, `cort0`, `extra`, `riva`, `banchina`, `lm.<kind>` | `principale`, `a_valle`… |

Alias leggibili negli override: `boss`, `ingresso`, `scale`, `esterno`,
oltre agli id. Gli id sono deterministici (ordine del Blueprint), quindi
restano validi fra dry-run e applicazione.

---

## 6. Planner, temi e intensita

### 6.1 Parametri *[deciso: tema + intensita]*

- `--theme abbandonato|abitato|lugubre|naturale|arcano|festivo`
  (obbligatorio; i sei temi della prima versione, *[deciso, D5]*)
- `--intensity leggera|media|intensa` (default `media`)
- `--seed N` (default: il seed del sidecar; il planner deriva un RNG
  dedicato, non riusa lo stato del generatore)

### 6.2 Cosa definisce un tema

Un tema e una tabella dati in `themes.py`, indicizzata per **tipo di mappa
× ruolo di zona**, con un default per ruolo non elencato. Per ogni voce:

| Campo | Significato |
|---|---|
| `floor` | chiavi di `floors`/`terrain` candidate per il pavimento della zona (o `None` = lascia) |
| `wall` | chiave di `walls` candidata (o `None`) |
| `terrain` | pennellate di terreno: slot, dove (`bordi`, `angoli`, `chiazze`, `soglie`), copertura |
| `objects` | pool di alias oggetto con peso, **modo di piazzamento** e **classe** (§6.4) |
| `lights` | regola (`porte`, `centro`, `per_oggetto` — es. ogni braciere), colore ARGB, `range`, `intensity`, texture luce |
| `ambient` | colore `ambient_light` del livello |

Bozza di carattere dei sei temi *[proposta, da tarare al gate]*:

| | abbandonato | abitato | lugubre | naturale | arcano | festivo |
|---|---|---|---|---|---|---|
| pavimento | pietra sconnessa, terra | legno, tappeti | pietra scura | terra, erba nelle crepe | pietra levigata, piastrelle | legno chiaro, selciato pulito |
| terreno | polvere/ghiaia ai bordi | quasi nulla | terra scura, chiazze | muschio, erba, fango | quasi nulla, chiazze di cenere vicino ai banchi | quasi nulla |
| oggetti | detriti, macerie, mobili rotti, ragnatele | arredo completo, tappeti, vettovaglie | ossa, lapidi, candele, sangue, catene | radici, cespugli, funghi, rocce, alberi (citta) | banchi alchemici, librerie, alambicchi, cristalli, cerchi rituali, pergamene | tavolate imbandite, botti, bandiere/stendardi, fiori, bancarelle (citta), strumenti musicali |
| luci | poche, fioche, molte spente | calde (`ffffd9a0`), ogni porta | fredde o verdi, isolate | luce naturale, pochissime fonti | viola/azzurre, sui banchi e sui cristalli | calde e numerose, a festoni lungo strade e pareti |
| ambient | grigio scuro | neutro | quasi nero | verde-grigio | blu-viola scuro | caldo, luminoso |

Il catalogo ha gia pack adatti ai due temi aggiunti (DQ Arcane Laboratory,
Skront's Alchemy, IC Apothecary, TygerLibrary per *arcano*; TygerBar,
TygerMusic, GW Inn tables, BB BaseCity per *festivo*): TASK-68 lo
verifica oggetto per oggetto.

### 6.3 Intensita

Moltiplicatore di densita oggetti (indicativo 0,5 / 1 / 1,8 rispetto alla
base del tema), di copertura del terreno e di probabilita di sostituzione
della texture. A `leggera` le texture di muri e pavimenti **non** cambiano:
si aggiungono solo terreno, oggetti e luci.

### 6.4 Regole di piazzamento (vincoli tattici) *[proposta]*

Ogni alias oggetto ha una **classe**:

- `decal` — calpestabile, non ostacola (ragnatele, sangue, crepe, tappeti,
  foglie): puo stare ovunque tranne sopra una porta.
- `ingombro` — ostacola (casse, altari, alberi, rocce grandi).

Regole non negoziabili, verificate da test:

1. Nessun oggetto (nemmeno decal) entro **1 quadretto** dal punto di una
   porta, su entrambi i lati del muro.
2. Gli `ingombro` non coprono piu del **30%** dell'area calpestabile di una
   zona, esistente compreso.
3. Ogni corridoio largo 1 quadretto resta libero da `ingombro`: li vanno
   solo decal e oggetti a parete di profondita < 0,5 quadretti.
4. Dopo il piazzamento ogni porta di una zona resta raggiungibile da ogni
   altra porta della stessa zona (flood fill sulla griglia a mezzo
   quadretto).
5. Le zone `buio` non ricevono luci. Nessuna luce o oggetto "rivelatore"
   entro 2 quadretti da una porta segreta.
6. La stanza boss tiene libero un rettangolo centrale (meta lato per lato)
   da `ingombro`: e dove si combatte.
7. Sopra/sotto: gli oggetti nuovi non si sovrappongono a quelli esistenti
   (`_is_free`) e usano `layer` coerenti (decal sotto, ingombro sopra).
8. Scala e orientamento degli sprite seguono `docs/format.md` §9.8 e
   `object_sizes`; un oggetto a parete e parallelo al muro.

### 6.5 Specifiche per tipo di mappa

- **building multi-piano**: ogni piano e decorato come livello a se; il
  vano scale non riceve `ingombro`. L'`esterno` (fra edificio e bordo
  canvas) riceve terreno e natura solo nei temi `naturale`/`abbandonato`.
- **cave**: il pavimento della grotta e il layer cave nativo, non pattern.
  L'abbellimento ne cambia la texture secondo il tema *[deciso, D6]*
  (lo spike TASK-67 stabilisce in quale campo del livello sta e quali
  texture del catalogo sono ammesse), e in piu usa terreno, oggetti e
  acqua. Il `cave.bitmap` (la forma della grotta) non cambia mai.
- **sewer**: l'acqua dei canali esiste gia; decorate puo aggiungere
  pozzanghere (poligoni d'acqua piccoli) solo nelle camere.
- **city `isolato`**: le stanze degli edifici si decorano come `building`;
  strade e cortili come zone esterne.
- **city `quartiere`/`citta`**: niente interni (gli edifici sono sprite).
  Solo terreno nei cortili e fuori le mura, alberi/cespugli nei cortili e
  lungo il fiume, carretti/bancarelle sulle piazze — **a scala
  coerente** con il preset (un albero non puo essere piu grande di una casa).
  Nessun tetto al numero di oggetti aggiunti ne alla dimensione del file
  *[deciso, D9]*: l'aumento si misura e si riporta, senza limitarlo.

---

## 7. Applicazione

### 7.1 Ordine

1. sostituzione texture di pattern e muri (solo campo `texture`);
2. terreno (§7.3);
3. oggetti `decal`, poi `ingombro`;
4. luci; `ambient_light`;
5. `finalize`, validazione completa, salvataggio del file e del sidecar.

### 7.2 Sostituzione di texture

Un pattern o muro appartiene a una zona se il suo ingombro coincide con
quello della zona (i muri di un edificio portante sono condivisi: si
cambiano solo se **tutte** le zone che li toccano concordano, altrimenti
restano). Il test di invarianza (§10) verifica che, a parte `texture`,
ogni muro, portale e pattern sia identico all'ingresso.

### 7.3 Terreno — spike necessario

Il `terrain` del livello ha 4 slot (`texture_1..4`) e un `splat` di
`width×height×64` byte, che nessun codice del progetto scrive ancora.
Prima di implementare §6.2 `terrain` serve uno spike, sul modello di
TASK-31 per `cave.bitmap`: codifica dello splat (canali per slot,
risoluzione sotto-cella), se si possono cambiare gli slot del template,
verifica in Dungeondraft. Se lo spike fallisce, il terreno si ripiega su
pattern semitrasparenti (`add_polygon_pattern`) e il tema perde quella
voce, non il resto.

### 7.4 Validazione

Si riusa `validate.py`. Nuove regole *[proposta]*:

| Codice | Severita | Regola |
|---|---|---|
| DDF201 | error | oggetto entro il raggio di rispetto di una porta |
| DDF202 | warning | zona con `ingombro` oltre la soglia di §6.4.2 |
| DDF203 | error | geometria (muri/portali/pattern, esclusa `texture`) diversa dal file di origine |

Il comando valida **prima** di scrivere: con errori non scrive nulla, come
`generate`.

---

## 8. CLI

### 8.1 `ddforge decorate`

```bash
ddforge decorate generated/cripta.dungeondraft_map \
    --out generated/cripta.decorated.dungeondraft_map \
    --theme lugubre --intensity media --seed 7 \
    [--dry-run [--json]] \
    [--zone boss=abitato] [--zone-intensity c3=intensa] [--zone-skip r2] \
    [--add boss:altar] [--no-textures] [--no-lights] [--allow-modified]
```

- `--out` default: `<nome>.decorated.dungeondraft_map` accanto all'originale;
  se esiste gia, errore salvo `--overwrite-output` (mai sull'originale).
- Codici di uscita come `generate`: ≠0 = nulla scritto; 0 con avvisi =
  scritto.

### 8.2 Dry-run *[deciso]*

`--dry-run` non scrive file e stampa, zona per zona: id e ruolo, pavimento
e muro prima → dopo, numero di oggetti per categoria con i primi alias,
luci, avvisi (asset mancanti, zona saturata dall'arredo esistente).
`--json` stampa lo stesso piano in JSON per la skill. Dry-run e
applicazione con gli stessi parametri producono **lo stesso piano**.

### 8.3 Override per zona *[deciso]*

| Opzione | Effetto |
|---|---|
| `--zone ID=TEMA` | tema diverso per una zona |
| `--zone-intensity ID=LIV` | intensita diversa per una zona |
| `--zone-skip ID` | zona lasciata com'e |
| `--add ID:ALIAS` | oggetto richiesto esplicitamente (alias del catalogo), piazzato dal planner con le regole di §6.4; se non c'e posto, avviso |
| `--no-textures`, `--no-terrain`, `--no-objects`, `--no-lights` | spegne una categoria su tutta la mappa |

`ID` accetta id e alias di §5. Un id inesistente e un errore esplicito.

---

## 9. La skill `dungeondraft-map-decorator`

Cartella `skills/decorator/` *[deciso, D8]*, accanto a `skills/generator/`
(la skill di generazione, spostata li da `skill/` il 2026-10-04), con
`SKILL.md` e `references/themes.md` (temi, ruoli di zona, alias utili per `--add`),
`references/examples.md`.

Workflow *[deciso: propone, poi applica]*:

1. **Individua la mappa** e verifica che abbia il sidecar; se no, spiega §4.4.
2. **Guarda**: `ddforge inspect` + `ddforge preview` dell'originale.
3. **Traduci la richiesta** in tema e intensita ("lugubre, abbandonata da
   secoli" → `lugubre` con override `abbandonato` sui corridoi, `intensa`).
4. **Proponi**: `decorate --dry-run --json`, riassunto discorsivo per zona
   (non il JSON grezzo). Chiedi conferma o correzioni.
5. **Traduci le correzioni in override** (§8.3) e ripeti il dry-run se
   cambiano molto.
6. **Applica**, leggi l'esito (stesse regole della skill di generazione:
   errori → correggi i parametri, mai il file).
7. **Consegna**: percorso, preview prima/dopo affiancati. Con l'estensione
   di §9.1 il preview mostra anche luci e terreno, quindi il confronto
   rende davvero l'abbellimento; resta un'approssimazione (niente ombre
   ne illuminazione calcolata come in Dungeondraft).

### 9.1 Estensione di `ddforge preview` *[deciso, D7]*

Oggi il preview disegna pavimenti, muri, porte, oggetti e il layer cave,
ma non luci, terreno, strade e tetti: per un abbellimento fatto in buona
parte di luci e terreno il prima/dopo sarebbe quasi identico. Il preview
impara a disegnare:

- il **terreno**, decodificando `terrain.splat` con la codifica trovata
  dallo spike (§7.3) e colorando ogni slot con il colore medio della sua
  texture (o una tinta fissa per slot se la texture non e leggibile);
- le **luci**, come alone radiale additivo con `color`, `range` e
  `intensity` della luce, sopra un velo scuro proporzionale a
  `environment.ambient_light`.

Opzione `--no-lighting` per la planimetria piatta di oggi. Resta un
extra opzionale (Pillow), mai richiesto dal core.

Stessi vincoli operativi della skill esistente: lavorare dalla root del
repo, `.venv/Scripts/ddforge`, mai patchare il JSON.

---

## 10. Test

- Round-trip del sidecar per ogni algoritmo.
- **Invarianza della geometria** (DDF203) su mappe di tutti i tipi × tutti
  i temi.
- Determinismo: stessi input + seed → file byte-identico; dry-run = piano
  applicato.
- Regole di §6.4 come test di proprieta su 30 seed per tipo di mappa.
- Originale non modificato (hash prima/dopo).
- Errori: sidecar mancante, hash diverso, mappa gia abbellita, id zona
  inesistente, `--out` uguale all'ingresso.
- Degradazione: tema con un alias assente dal catalogo → avviso, nessun
  crash, nessun path inventato.
- Il file prodotto passa `ddforge validate` senza errori.

## 11. Gate umano

Come M1/M3/M4: Jay apre in Dungeondraft almeno un file per tipo di mappa
(5) per ciascun tema (6), 30 file, con preview accanto. Criteri: si apre senza
errori, nulla e fuori posto rispetto all'originale, nessun oggetto blocca
una porta o un corridoio, il tema si riconosce a colpo d'occhio, la scala
degli oggetti e credibile. Si misura anche il tempo di apertura delle
citta `citta` abbellite (sono gia le mappe piu pesanti).

## 12. Milestone e task

Milestone **M10 — Abbellimento mappe**; ordine:

| # | Task | Dipende da |
|---|---|---|
| — | decision-3: apertura del perimetro (oggi *proposed*, diventa *accepted* in TASK-73) | — |
| 1 | TASK-66 sidecar in `generate` | — |
| 2 | TASK-67 spike `terrain.splat` | — |
| 3 | TASK-68 censimento asset e tabelle dei temi | — |
| 4 | TASK-69 core di decorate end-to-end su `dungeon` (zone, planner, apply, CLI, dry-run, override, regole tattiche, DDF201–203) | 66, 68 |
| 5 | TASK-70 estensione a `building` | 69 |
| 6 | TASK-71 estensione a `cave`/`sewer` | 69, 67 |
| 7 | TASK-72 estensione a `city` | 70 |
| 8 | TASK-73 skill `dungeondraft-map-decorator` e documentazione | 69 |
| 9 | TASK-75 preview con luci e terreno (§9.1) | 67 |
| 10 | TASK-74 gate umano | 70–73, 75 |

TASK-66, 67 e 68 sono indipendenti e possono procedere in parallelo.
La riorganizzazione `skill/` → `skills/generator/` e gia fatta.

## 13. Definizione di "fatto"

Una richiesta in linguaggio naturale su una mappa di ognuno dei 5 tipi
produce, attraverso la skill, una proposta per zona, accetta correzioni,
scrive un file nuovo che passa la validazione, non altera la geometria, e
supera il gate umano di §11.

---

## 14. Domande del secondo giro

| # | Domanda | Risposta di Jay (2026-10-04) |
|---|---|---|
| D1 | Se la mappa e stata ritoccata in Dungeondraft dopo la generazione (hash diverso), decorate rifiuta o procede? | rifiuta di default, procede con `--allow-modified` (§4.2) |
| D2 | Il sidecar va scritto sempre o solo con un flag? | sempre, nessun flag per disattivarlo (§4.1) |
| D3 | Gli asset per i temi ci sono nei 52 pack? | dovrebbero esserci; TASK-68 elenca quelli mancanti e Jay decide caso per caso se farne a meno |
| D4 | Decorate puo cambiare `environment.ambient_light`? | si; spegnibile con `--no-lights` |
| D5 | Temi in piu? | si: *arcano* e *festivo* entrano nella prima versione (§6.2) |
| D6 | Nelle grotte si puo cambiare il "pavimento" del layer cave? | si, fa parte del tema (§6.5); lo spike TASK-67 trova come |
| D7 | Il preview deve disegnare luci e terreno? | si, dentro M10 (§9.1, TASK-75) |
| D8 | Dove vive la seconda skill? | `skills/generator/` + `skills/decorator/`; spostamento della skill esistente gia fatto |
| D9 | Quanto puo crescere il file delle mappe `citta`? | nessun limite per ora; l'aumento si misura e basta |
