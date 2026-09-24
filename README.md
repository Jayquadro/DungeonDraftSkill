# Dungeondraft Forge (`ddforge`)

Generatore procedurale di mappe `.dungeondraft_map` per Dungeondraft.

Lo stato del progetto e la specifica completa sono in [docs/SPEC.md](docs/SPEC.md).
Il lavoro e tracciato in Backlog.md sotto `backlog/` (milestone M0-M7).

## Stato

Milestone M0-M5 completate (core, validatore, generatori dungeon/edifici/
grotte/citta). M6 (renderer di anteprima) e M7 (skill Claude e
documentazione finale) sono in corso: consultare `backlog/milestones/` e
`docs/SPEC.md` §5 per il dettaglio.

## Installazione (sviluppo)

```bash
pip install -e ".[dev]"
```

Extra opzionali, mai richiesti dal core (`docs/SPEC.md` §4): `preview`
(Pillow, per `ddforge preview`) e `sprites` (Pillow + numpy, per gli script
di post-processing sprite in `src/ddforge/sprite_prep/`). Es.
`pip install -e ".[dev,preview]"`.

## Uso

```bash
ddforge --help
```

I cinque sottocomandi sono documentati in dettaglio in `docs/SPEC.md` §8;
qui un esempio minimo per ciascuno. Ogni sottocomando ha il proprio
`--help` con l'elenco completo delle opzioni.

### `generate` — genera una mappa

```bash
ddforge generate dungeon \
    --template templates/blank_80x80.dungeondraft_map \
    --out cripta.dungeondraft_map \
    --width 40 --height 40 --rooms 8 --seed 1337 \
    --style crypt --lights --furnish medium
```

`algorithm` e `dungeon | building | cave | sewer | city` (vedi
`docs/SPEC.md` §9 per la logica di ciascuno; `building` ha
`--building-type`/`--l-shaped`, `city` ha `--scale`/`--landmark`/
`--no-landmarks`, riassunti sotto in "Mappe cittadine"). `--seed` rende la
generazione riproducibile byte per byte. Il comando valida sempre il
risultato prima di scriverlo: se ci sono errori non scrive nulla e stampa
gli `Issue` (vedi `validate` sotto).

### `validate` — controlla un file gia scritto

```bash
ddforge validate cripta.dungeondraft_map
```

Rilanciato internamente da `generate` prima di salvare; utile anche da solo
su una mappa esistente (generata o disegnata a mano) per trovare gli errori
elencati in `docs/SPEC.md` §7.

### `inspect` — ispeziona un file esistente

```bash
ddforge inspect cripta.dungeondraft_map
```

Stampa dimensioni, `format`, `creation_build`, pack referenziati e conteggi
per livello (muri, porte, pattern, oggetti, luci, testi, tetti). Il primo
strumento da usare quando si esporta un nuovo template da Dungeondraft (vedi
sotto) o quando un file di terzi si comporta in modo inatteso.

### `catalog` — rigenera `data/assets.json`

```bash
ddforge catalog \
    --from templates/rich_reference.dungeondraft_map \
    --from templates/blank_80x80.dungeondraft_map \
    --out data/assets.json
```

Estrae pack, texture e alias semantici (muri, pavimenti, porte, oggetti...)
dai documenti passati con `--from` (ripetibile). `--pack` legge un
`.dungeondraft_pack` compilato per ottenere le dimensioni pixel native delle
texture; `--from-catalog` fa crescere un catalogo esistente in modo
incrementale invece di ripartire da zero; `--base-pck`/`--base-include`
importano texture di base del programma (mai soggette a DDF014). Dettagli e
comandi storici usati sul progetto in `docs/format.md` §10.

### `preview` — anteprima PNG senza aprire Dungeondraft

```bash
ddforge preview cripta.dungeondraft_map --out cripta.png --scale 8
```

Richiede l'extra opzionale `preview` (`pip install -e ".[preview]"`, vedi
sotto): senza Pillow installato il comando lo dice con un messaggio chiaro
invece di un traceback. Legge il file `.dungeondraft_map` gia scritto su
disco, mai lo stato in memoria, cosi l'anteprima verifica davvero cio che e
stato salvato.

### Mappe cittadine: i tre preset di scala

`ddforge generate city` ha un parametro `--scale` con tre preset, perche un
isolato giocabile al tavolo, un quartiere intero e una citta capace di
contenerne una decina non stanno alla stessa scala
(`backlog/decisions/decision-2`, rivista da Jay al round 2 del gate umano).
Il default e `isolato`.

Misure su un canvas 78×78 (`templates/blank_80x80.dungeondraft_map`, seed
1337; il template di riferimento pesa 1,68 MB senza nulla disegnato sopra):

| | `--scale isolato` (default) | `--scale quartiere` | `--scale citta` |
|---|---|---|---|
| Un quadretto vale | 5 ft / 1,5 m | circa un edificio | circa un edificio, ma di un quartiere fra una decina |
| Edifici ordinari sul canvas | 23 | 143 | 2.745 |
| Luoghi notevoli sul canvas | 10 | 42 | 29 |
| Ingombro medio di un edificio | 4,9×5,9 quadretti (~65 m²) | 2,4×2,4 quadretti (~13 m²) | 0,7×0,7 quadretti (~1 m²) |
| Cos'e un edificio | pianta completa: muri portanti, tramezzi, stanze, porte, tetto (riusa `generators/building.py`, con tipologie diverse per lotto) | uno sprite `object` del pack "BB 51 Assets Houses1" (BluBerrey, 33 varianti), scalato per riempire il lotto e con una tinta (`custom_color`) variata fra 6 toni — non piu un ingombro astratto | come `quartiere`, a scala ridotta |
| Dimensione del file | 1,78 MB | 1,80 MB | 3,28 MB |
| A cosa serve | far muovere le miniature dentro e fuori dagli edifici di una via | inquadrare un quartiere esteso, decidere dove si va | orientarsi in una citta intera; non e pensata per essere giocata al tavolo |

Solo il preset `isolato` produce una geometria giocabile al tavolo (muri,
stanze, porte a scala 5 ft). `quartiere` e `citta` sono mappe di citta viste
dall'alto — uno sfondo/riferimento visivo, non un layout tattico — ed e per
questo che dal TASK-46 i loro edifici sono sprite del pack scelto da Jay
invece della geometria di `generators/building.py` (vedi `docs/format.md`
§10.2 per la provenienza del pack e il calcolo della scala di piazzamento).

I tempi di apertura in Dungeondraft per i tre preset non sono ancora stati
misurati: solo Jay puo darli, aprendo i file a mano.

Strade, isolati, lotti con fronte strada e piazze ci sono in tutti e tre:
cambia solo la taratura geometrica (`SCALE_PRESETS` in
`generators/city.py`) e la rappresentazione degli edifici.

In tutti e tre i preset la rete stradale non e una griglia: la centro-linea
di ogni via serpeggia dentro l'ingombro che le e riservato, e una via
obliqua attraversa la mappa da un bordo all'altro togliendo gli edifici che
incontra. Gli isolati profondi ricevono due file di lotti schiena contro
schiena, con il cortile in mezzo, cosi le case si affacciano su entrambe le
vie che bordano l'isolato.

**Come scegliere.** Se la scena si gioca *dentro* gli edifici, serve
`isolato`: agli altri due preset un edificio e largo meno di un quadretto e
non ci sta una stanza. Se serve un quartiere intero visto dall'alto, serve
`quartiere`. Se serve un'intera citta o una vista d'insieme di piu quartieri,
serve `citta`: alla scala `quartiere` gli stessi 3.325 edifici
richiederebbero un canvas di circa 285×285 quadretti, mentre l'unico
template di produzione e 80×80 e `ddforge` non cambia mai le dimensioni del
canvas del template.

### Mappe cittadine: i luoghi notevoli

Una citta di soli edifici anonimi non ha luoghi. In tutti e tre i preset la
mappa riceve **elementi urbani notevoli** — templi, mercati, taverne,
concerie, cimiteri, mura, fiumi, porti — estratti dal seed, ciascuno con il
suo **sprite dedicato** e un'**etichetta col nome**.

Un luogo si disegna come tutto il resto della mappa: uno sprite vero preso
dal pack giusto (cattedrale, chiesa, mulino, faro, forgia, gogna, lapidi,
banchi da mercato...), non una toppa di pavimento con un'icona sopra. Gli
spiazzi aperti sono fatti di piu' sprite sparsi, perche' un mercato sono i
banchi e un cimitero sono le lapidi. L'etichetta sta sotto l'ingombro e il
corpo del testo cresce con l'importanza del luogo: una cattedrale ha un nome
grande, una bottega un nome piccolo. Due nomi non si sovrappongono mai.

Non sono sparsi a caso: chi ha una regola la rispetta, ed e questo che rende
la citta leggibile invece che solo varia.

| elemento | dove finisce |
|---|---|
| dogana, torre di guardia | alle porte delle mura |
| mulino | sulla riva del fiume |
| conceria, macello | sulla riva **a valle** (i mestieri che puzzano stanno sottovento) |
| cimitero | fuori le mura, o presso il tempio se mura non ce ne sono |
| mercato | sulla piazza; il patibolo sulla piazza principale |
| cantiere navale, faro, mercato del pesce | sulla banchina del porto |
| monastero, fiera, quartiere povero, lazzaretto | ai margini |

Un elemento la cui regola non trova posto **non viene piazzato altrove**:
viene saltato. Su una mappa senza fiume non c'e nessuna conceria.

Quantita e ammissibilita dipendono dal preset: un fornaio si vede a `isolato`,
dove la bottega e un edificio con le stanze; su una mappa di citta intera si
segnano cattedrale, palazzo, mura, porto e mercati, non le panetterie. Le
proporzioni misurate su 30 seed per preset sono in `docs/SPEC.md` §9.4.1
(rigenerabili con `python scripts/city_landmarks_census.py --markdown`).

```bash
# chiedi elementi specifici (ripetibile; accetta anche mura, fiume, porto)
ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out porto.dungeondraft_map --width 78 --height 78 --seed 1337 \
    --scale quartiere --landmark porto --landmark faro --landmark cattedrale

# nessun luogo e nessuna struttura: solo strade, isolati ed edifici
ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out spoglia.dungeondraft_map --width 78 --height 78 --seed 1337 --no-landmarks
```

Chiedere un elemento non ammissibile per il `--scale` scelto (per esempio
un'arena in un quartiere) e un errore esplicito, non un'omissione
silenziosa. `ddforge generate --help` elenca tutti i valori accettati.

```bash
# un isolato, giocabile al tavolo
ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out isolato.dungeondraft_map --width 78 --height 78 --seed 1337

# un quartiere intero visto dall'alto
ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out quartiere.dungeondraft_map --width 78 --height 78 --seed 1337 --scale quartiere

# una citta intera, per orientarsi
ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out citta.dungeondraft_map --width 78 --height 78 --seed 1337 --scale citta
```

## Test

```bash
pytest -q
```

## Schema del formato e trappole

Lo schema completo e verificato di `.dungeondraft_map` — ogni tipo di
elemento, le costanti derivate dai template reali, e tutte le regole di
orientamento/allineamento calibrate nei gate umani di M1/M3/M4 (tangente
della porta, muri di canale, riproiezione delle porte quando una stanza si
allarga, tetti a linea di colmo...) — vive in `docs/format.md`, non qui: e
un documento vivo, aggiornato ogni volta che una milestone verifica un campo
nuovo. `docs/SPEC.md` §6 e §13 restano il riferimento architetturale di
partenza, ma dove i due divergono `docs/format.md` e la fonte aggiornata
(la versione di Dungeondraft realmente in uso e piu recente di quella
analizzata per la spec).

Le trappole che hanno gia rotto una mappa una volta (`docs/SPEC.md` §14,
elenco completo li):

| Trappola | Rimedio |
|---|---|
| Costruire il JSON da zero | usa sempre un template esportato da Dungeondraft |
| `points` come lista di `Vector2` | serializza come un'unica stringa `PoolVector2Array(...)` |
| Colore a 6 cifre | sempre 8 cifre ARGB (`ffrrggbb`) |
| Porta come elemento di livello | va annidata dentro `wall['portals']` |
| `world.next_node_id` non aggiornato | chiama sempre `finalize()` prima di `save()` |
| Pack ID inventati | solo quelli gia presenti in `header.asset_manifest` del template |
| `world.format` diverso da quello del template | ereditalo sempre dal template, non impostarlo a mano |
| Coordinate in pixel dentro `world.width`/`world.height` | quei due campi sono in quadretti; le coordinate degli elementi sono in pixel |
| `path.edit_points` assoluti | sono relativi a `position` (il primo punto) |
| Primo punto ripetuto con `wall.loop = true` | o il flag o il punto ripetuto, mai entrambi |

## Esportare un nuovo template

Il progetto non genera mai il JSON da zero: carica un template esportato
dall'installazione reale di Dungeondraft e ci inietta la geometria
generata (`docs/SPEC.md` §2). Quando Dungeondraft cambia versione, i
template in `templates/` vanno rifatti con questa procedura — mai
modificati sul posto (sono tenuti in sola lettura apposta):

1. **Esporta due file da Dungeondraft**, con la versione aggiornata:
   - un template **vuoto** (`File > New`, dimensione scelta — quella in uso
     nel progetto e 80×80, il default dell'installazione di riferimento);
   - un template **ricco**, con un esemplare disegnato a mano di ogni
     elemento: muro, porta, finestra, pavimento, oggetto, **luce**, tetto,
     percorso e **testo**. Luci e testi sono i campi meno stabili fra le
     build (vedi `docs/format.md` §4): senza un esemplare vero non c'e modo
     di verificarne lo schema.
   - Salva entrambi con un nome che porti la dimensione e/o la build
     (es. `blank_80x80.dungeondraft_map`), copiali in `templates/` e
     rimettili in sola lettura. Non toccare i template esistenti finche il
     nuovo non ha superato tutti i passi seguenti.

2. **Ispeziona i nuovi file** prima di usarli:

   ```bash
   ddforge inspect templates/<nuovo_vuoto>.dungeondraft_map
   ddforge inspect templates/<nuovo_ricco>.dungeondraft_map
   ```

   Confronta `format`, `creation_build`, numero di pack e conteggi degli
   elementi con l'output sugli stessi file sulla build precedente. Un
   cambio di `world.format` o della lista di chiavi di livello (`LEVEL_KEYS`
   in `src/ddforge/template.py`) e il segnale piu importante che il formato
   e cambiato davvero, non solo il numero di build.

3. **Verifica le formule dei blob binari** (`docs/SPEC.md` §2,
   `docs/format.md` §11 e §14): `len(tiles.cells) == width*height`,
   `len(terrain.splat) == width*height*64`, e la lunghezza di
   `cave.bitmap`/`cave.entrance_bitmap` secondo
   `ceil((4*width+3)*(4*height+3)/8)`. Se una formula non torna piu sul
   nuovo template, il layer binario e cambiato e va investigato prima di
   proseguire (non ridurre la verifica a "il file si apre").

4. **Fai girare la suite di test** puntandola, dove serve, ai nuovi
   template (in particolare `tests/test_template.py`,
   `tests/test_cave_bitmap_format.py` e i test golden file):

   ```bash
   pytest -q
   ```

   Un fallimento nei golden file e atteso quando il template cambia
   davvero (i byte del documento generato includono i blob del template):
   verifica che la differenza sia spiegabile dal nuovo template, poi
   rigenera i golden invece di ignorare il test.

5. **Se emergono differenze di schema** (una chiave di livello in piu o in
   meno, un campo nuovo su `portal`/`light`/`text`, un formato diverso di un
   blob), aggiornale nel codice (`template.py`, `validate.py`) e
   documentale in `docs/format.md` nello stile delle sezioni esistenti: mai
   ipotizzare un valore, sempre citare il file reale in cui e stato
   osservato (vedi `docs/format.md` §12 per un esempio di questo tipo di
   voce, la scoperta della 18ª chiave `texts_vis`).

6. **Se il nuovo template referenzia pack diversi**, rigenera il catalogo
   invece di lasciarlo disallineato:

   ```bash
   ddforge catalog --from-catalog data/assets.json \
       --from templates/<nuovo_ricco>.dungeondraft_map \
       --from templates/<nuovo_vuoto>.dungeondraft_map \
       --out data/assets.json
   ```

   `--from-catalog` conserva le chiavi gia note che non hanno piu una fonte
   sul disco (`docs/format.md` §10.3): usalo sempre per un aggiornamento
   incrementale invece di ripartire da zero.

7. **Ripeti il gate umano** (`docs/SPEC.md` §5): genera una mappa di prova
   sul nuovo template e aprila davvero in Dungeondraft.

   ```bash
   ddforge generate dungeon --template templates/<nuovo_vuoto>.dungeondraft_map \
       --out prova_gate.dungeondraft_map --seed 1 --rooms 8
   ```

   Conferma che la stanza appare, i muri sono chiusi e le porte sono sul
   muro e non fluttuano. Solo dopo questa conferma visiva il nuovo template
   sostituisce il vecchio come riferimento di produzione.
