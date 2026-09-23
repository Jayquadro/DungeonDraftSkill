# Sprite dei luoghi di interesse — cosa serve

Elenco degli sprite necessari a `generators/city.py` per disegnare i luoghi
urbani notevoli (TASK-48). Serve come base per commissionare un pacchetto di
asset dedicato: il prompt pronto da usare sta in `docs/prompt-sprite-pack.md`.

Misure prese generando 20 seed per preset su un canvas 78×78, cioè l'area
utile del template di produzione (`templates/blank_80x80.dungeondraft_map`).
Rigenerabili con `python scripts/city_landmarks_census.py`.

---

## 1. Come viene usato uno sprite

Un luogo si disegna in una di tre forme, e solo due delle tre hanno bisogno
di uno sprite.

| forma | quando | cosa serve |
|---|---|---|
| **edificio a stanze** | preset `isolato`, luogo chiuso NON coperto dal pacchetto | niente: lo genera `building.py` con muri, porte e tetto |
| **uno sprite che riempie l'ingombro** | preset `quartiere`/`citta`, luogo chiuso; oppure luogo chiuso coperto dal pacchetto a QUALUNQUE preset, isolato compreso (`LandmarkKind.sprite_only`, TASK-63) | **1 sprite** (o più varianti dello stesso luogo) |
| **più sprite sparsi** | luogo all'aperto, tutti i preset | **più pezzi** che compongono la scena (i banchi di un mercato, le lapidi di un cimitero) |

Lo sprite viene scalato uniformemente per stare dentro l'ingombro del luogo
(`compose._sprite_scale`): le proporzioni sono preservate, quindi **la forma
conta e la dimensione in pixel no** — serve solo che ci siano abbastanza
pixel da non sgranare alla dimensione massima a cui viene disegnato.

## 1-bis. Scegliere fra gli sprite che ci sono già

Prima di commissionare un pacchetto nuovo si può scegliere il meglio fra i
440 object già in catalogo. `scripts/landmark_sprite_sheet.py` genera tre
**fogli campionario**: una riga per luogo, col nome a sinistra e tutti i
candidati plausibili affiancati.

```bash
python scripts/landmark_sprite_sheet.py --write        # genera i tre fogli
# Jay li apre in Dungeondraft, CANCELLA gli sprite che non vuole e salva
python scripts/landmark_sprite_sheet.py --read generated/campionario_*.dungeondraft_map
```

La rilettura stampa la tabella già pronta da incollare in
`assets._CITY_LANDMARK_SPRITES`. Il luogo di appartenenza si ricava dalla
**riga**, quindi si possono cancellare sprite liberamente ma non spostarli da
una riga all'altra.

Sul foglio ogni sprite è ingrandito per riempire la sua cella: serve a
giudicare il **disegno**, non la dimensione. Le dimensioni vere sono nelle
tabelle qui sotto.

## 2. Vincoli tecnici, non negoziabili

- **PNG.** Non WebP. `assets.read_dungeondraft_pack` legge le dimensioni
  native dall'header IHDR di un PNG; per un WebP il catalogo resta senza
  dimensioni e il piazzamento ricade su una stima per nome.
- **256 px = 1 quadretto = 1,5 m.** È la scala di Dungeondraft.
- **Sfondo trasparente, e nient'altro dentro l'immagine.** Questo è il
  difetto che ci ha già morso: gli sprite BB ritraggono un complesso *con le
  sue pertinenze* — l'abbazia porta con sé l'isola e il mare, il maschio il
  fossato — e piazzati in mezzo a un quartiere fitto diventano toppe di
  campagna. Un edificio, il suo perimetro, nient'altro.
- **Vista dall'alto ortogonale** (bird's eye), non assonometrica. Le mappe
  `quartiere` e `citta` sono viste dall'alto; una casa disegnata in
  prospettiva stona con quelle accanto e con le strade.
- **Ombra corta e coerente**, sempre nella stessa direzione su tutto il
  pacchetto (proposta: in basso a destra).
- **Ricolorabilità (dedotto, non verificato).** Dungeondraft ricolora la
  parte *rossa* di un object quando gli si passa `custom_color`; è così che
  le case del pacchetto BB cambiano tinta. Se si vuole la stessa variazione,
  la parte variabile (il tetto) va disegnata in rosso saturo.

## 3. Luoghi chiusi — uno sprite ciascuno (29)

`disegnato a` è la dimensione a cui lo sprite viene effettivamente reso sulla
mappa, misurata; `px consigliati` è la risoluzione nativa da consegnare, presa
con un margine sul caso peggiore.

### Monumenti — 1024×1024 px

| luogo | etichetta sulla mappa | disegnato a (quartiere / città) | per mappa | note per chi disegna |
|---|---|---|---|---|
| `cattedrale` | Cattedrale | 8,9 × 7,5 q / 2,5 × 2,5 q | 0,8 / 0,6 | navata, transetto, abside; il monumento religioso più grande della città |
| `palazzo` | Palazzo del Signore | 8,4 × 8,1 q / 2,7 × 2,7 q | 1,0 / 0,95 | residenza fortificata con corte interna, non un castello isolato |
| `monastero` | Monastero | 8,3 × 7,8 q / 2,1 × 2,2 q | 0,5 / 0,4 | chiostro quadrato, chiesa laterale, orto; sta ai margini |
| `accademia` | Accademia di Magia | 8,7 × 8,1 q / 2,7 × 2,9 q | 0,4 / 0,55 | corpo centrale con torre osservatorio |
| `arena` | Arena | — / 2,6 × 2,6 q | — / 0,4 | anfiteatro ellittico con gradinate; solo preset `citta` |

### Edifici pubblici medi — 768×768 px

| luogo | etichetta | disegnato a (quartiere / città) | per mappa | note |
|---|---|---|---|---|
| `tempio` | Tempio | 4,2 × 3,9 q / 1,1 × 1,3 q | 0,8 / 0,95 | chiesa a navata unica; deve distinguersi dalla cattedrale per dimensione e forma |
| `municipio` | Municipio | 4,1 × 4,1 q / 1,3 × 1,1 q | 0,75 / 0,7 | edificio civile con loggia e torre dell'orologio |
| `caserma` | Caserma della Guardia | 4,4 × 3,5 q / 1,3 × 1,2 q | 0,75 / 0,9 | corpo di guardia con cortile d'armi recintato |
| `teatro` | Teatro | 4,9 × 3,4 q / 1,1 × 1,2 q | 0,4 / 0,45 | pianta semicircolare |
| `bagni` | Bagni Pubblici | 4,0 × 4,4 q / 1,2 × 1,3 q | 0,25 / 0,35 | vasche a cielo aperto e spogliatoi |
| `ospedale` | Ospedale | 4,0 × 4,1 q / 1,1 × 1,3 q | 0,60 / 0,65 | corsia unica con chiostro e orto dei semplici; dentro le mura, non isolato come il lazzaretto |
| `mulino` | Mulino ad Acqua | 5,2 × 3,3 q / 1,0 × 1,4 q | 0,25 / 0,2 | **ad acqua**, con ruota sul lato: sta sempre sulla riva del fiume |
| `faro` | Faro | 3,1 × 3,0 q / 1,0 × 1,2 q | 0,2 / 0,2 | torre cilindrica vista dall'alto, lanterna al centro; sta sulla banchina |
| `lazzaretto` | Lazzaretto | 3,3 × 3,6 q / 0,9 × 1,0 q | 0,5 / 0,5 | edificio lungo e basso, isolato, con recinto; sta fuori le mura |
| `prigione` | Prigione | 2,3 × 2,3 q / 0,7 × 0,7 q | 0,35 / 0,55 | blocco massiccio senza finestre, cortile chiuso |

### Botteghe e servizi — 512×512 px

Tutte disegnate a ~2,4 × 2,4 q al preset `quartiere` e ~0,7 × 0,7 q al preset
`citta`. Sono edifici di taglia ordinaria: devono distinguersi **dal tipo di
casa**, non dalla dimensione.

| luogo | etichetta | per mappa (q / c) | segno che lo rende riconoscibile |
|---|---|---|---|
| `taverna` | Taverna | 6,75 / — | insegna sporgente, tavoli fuori |
| `locanda` | Locanda | 3,15 / — | come la taverna ma con stalla annessa e più piani |
| `bordello` | Casa di Piacere | 1,70 / — | balconata, lanterne |
| `fabbro` | Fabbro | 4,20 / — | fucina a cielo aperto sul retro, incudine, catasta di carbone |
| `stalle` | Stalle e Maniscalco | 2,75 / — | tettoia lunga, recinto, abbeveratoio |
| `magazzino` | Magazzino | 4,65 / — | capannone, portone largo, casse accatastate |
| `alchimista` | Bottega dell'Alchimista | 2,00 / — | serra o alambicchi sul tetto |
| `biblioteca` | Biblioteca | 0,60 / 0,45 | edificio compatto con lucernari |
| `banca` | Casa di Cambio | 0,60 / 0,65 | facciata con colonne, ingresso presidiato |
| `dogana` | Dogana | 0,95 / 3,20 | tettoia per le merci e sbarra; sta **alle porte delle mura** |
| `torre_guardia` | Torre di Guardia | 1,30 / 3,20 | torre quadrata dall'alto; sta **alle porte delle mura** |
| `conceria` | Conceria | 0,30 / 0,20 | vasche di concia scoperte; sta **sul fiume, a valle** |
| `macello` | Macello | 0,15 / 0,25 | cortile lastricato e recinto; sta **sul fiume, a valle** |

## 4. Luoghi all'aperto — più pezzi ciascuno (6)

Questi non sono un edificio: sono **un'area colorata con sopra degli sprite
sparsi**. Servono quindi più pezzi piccoli, che il generatore ripete e
distribuisce a caso dentro l'area, senza mai sovrapporli.

| luogo | etichetta | area | terreno | lato di un pezzo | pezzi da disegnare |
|---|---|---|---|---|---|
| `mercato` | Piazza del Mercato | 4,7 × 3,8 q | nessuno | 2 q = **3 m** | banco con tenda ×3, cesta di merci, carro |
| `patibolo` | Patibolo | 3,6 × 3,2 q | nessuno | 2 q = **3 m** | forca, gogna, ceppo |
| `statua` | Statua | 3,0 × 2,8 q | nessuno | 1,5 q = **2,2 m** | statua su piedistallo ×3 (guerriero, mago, figura ammantata) |
| `giardino` | Giardino Pubblico | 7,8 × 7,8 q | erba | 3 q = **4,5 m** | chioma d'albero ×3 (sole **verdi**), cespuglio ×2, aiuola |
| `cimitero` | Cimitero | 4,4 × 5,2 q | erba | 1,5 q = **2,2 m** | lapide ×3 (lastra con la pietra in testa, vista dall'alto), croce, fossa recintata |
| `fiera` | Fiera | 5,2 × 4,9 q | terra battuta | 3 q = **4,5 m** | tendone ×2, palco, fuoco da campo, carro, bancarella |

**Dimensione dei pezzi sparsi: 512×512 px.**

**La dimensione reale la decide il generatore, non lo sprite.** La colonna
"lato di un pezzo" è quanto il generatore disegna il lato lungo di ogni
pezzo, qualunque sia la sua risoluzione nativa: serve solo che le
**proporzioni** dello sprite siano giuste, perché il resto viene scalato.

> Perché funziona così. I pack sono disegnati a scale incompatibili fra
> loro: `tree1` di City Terrain è nativo 0,3 quadretti (45 cm — è un simbolo
> da mappa di regione), mentre un albero di CHR ne misura 0,6. Fidandosi del
> nativo, gli alberi di un parco venivano puntini; prima ancora, scalando
> ogni pezzo a una frazione dell'**area**, un cimitero grande produceva una
> lapide alta sette metri. Entrambi visti e corretti.

## 5. Strutture — nessuno sprite

Nessuna struttura urbana usa uno sprite:

- **mura, fiume, riva del porto**: `path` con una texture piastrellabile;
- **ponti**: un pavimento steso sull'acqua, largo quanto l'attraversamento
  (uno sprite di ponte è una campata di dimensione fissa, e scalarlo per
  coprire l'attraversamento lo deformava);
- **porte delle mura**: il varco resta un'apertura nella cinta, senza torre
  sopra. Continua a essere il punto a cui dogana e torre di guardia si
  agganciano.

## 6. Aree colorate

Servono texture di terreno piastrellabili sotto gli sprite sparsi. Quelle già
disponibili nei pack di Jay sono `chr_grass`, `chr_dirt`, `chr_cobblestones`
(pacchetto CHR Town Maps) e `chr_forest` (bosco fitto).

Già in uso dal generatore:

| area | texture usata oggi |
|---|---|
| giardino pubblico, cimitero | `chr_grass` (erba) |
| fiera, quartiere povero | `chr_dirt` (terra battuta) |
| statua, mercato, patibolo | nessuna: stanno già su una piazza pavimentata |

Mercato e patibolo disegnavano in passato un secondo pattern `tileset_cobble`
sopra la propria cella della piazza: creava un rettangolo a sfondo opaco
visibilmente diverso dalla piazza intorno, e Jay lo ha chiesto trasparente
(TASK-60). Tolto: ora, come la statua, non dichiarano un terreno proprio e
resta visibile solo il pavimento della piazza.

**Verificato**: Dungeondraft accetta una texture di categoria `terrain`
dentro un elemento `pattern`. Il foglio di `scripts/label_calibration.py`
stende una toppa per ognuna delle sedici texture candidate, e aperto in
Dungeondraft si vedono tutte. Il pacchetto non ha quindi bisogno di
consegnare le texture di terreno in doppia copia.

## 7. Cosa NON serve

- Ponti, mura, fiume, riva: sono `path` o pavimenti, non object.

Nient'altro. In particolare **servono** anche `fornaio` e `macelleria`, che
esistono solo al preset `isolato`: sono coperti dal pacchetto, quindi
mostrano sempre lo sprite li' (vedi la nota qui sotto).

> **Perché anche i luoghi del preset `isolato` hanno bisogno di uno sprite.**
> Per un luogo chiuso NON coperto dal pacchetto, `isolato` *dovrebbe* sempre
> essere un edificio a stanze vero, ma `building.generate` pretende almeno 6
> quadretti per lato e molti lotti sono più stretti. Il generatore preferisce
> i lotti in cui l'edificio ci sta — misurato su 30 seed, il 55% dei luoghi
> chiusi ottiene la geometria vera contro il 17% di prima — ma il resto
> ripiega sullo sprite, meglio di nessun luogo. Per i 24 luoghi coperti dal
> pacchetto (`LandmarkKind.sprite_only`, TASK-63) non è un ripiego: mostrano
> sempre l'illustrazione commissionata, anche quando il lotto sarebbe
> abbastanza grande per un edificio vero — Jay preferisce l'illustrazione
> alla pianta interna generica.

## 8. Facoltativo ma consigliato: le case ordinarie

Una mappa `quartiere` ha ~325 edifici ordinari (raddoppiati da TASK-64, sez.
10), una `citta` ~3300. Oggi usano
gli sprite del pacchetto BB Houses1, che sono icone piatte ricolorabili,
mentre i luoghi useranno edifici dipinti: **i due registri grafici non
combaciano**, ed è il motivo principale per cui la mappa non è ancora bella.

Se il pacchetto includesse **10–15 varianti di casa ordinaria** nello stesso
stile dei luoghi (512×512, con il tetto in rosso saturo per la
ricolorabilità), l'intera mappa diventerebbe coerente. È la singola aggiunta
che cambia di più il risultato.

## 9. Riepilogo delle quantità

| categoria | pezzi |
|---|---|
| luoghi chiusi | 28 |
| pezzi dei luoghi all'aperto | ~18 |
| **totale minimo** | **~46** |
| case ordinarie (facoltative) | 10–15 |

Quattro elementi che c'erano in una versione precedente di questo documento
sono stati **tolti dal catalogo** perché Jay li ha scartati guardando il
campionario: cantiere navale, mercato del pesce, quartiere povero e sede di
gilda. Con loro è uscita anche la torre sulla porta delle mura: il varco
nella cinta resta, ma senza sprite sopra. Sulla banchina del porto resta il
solo faro.

## 10. Chi ha già lo sprite del pacchetto, chi è ancora sul ripiego

TASK-52: il pacchetto Nova Mistralis (pack `Ada7IQuz`, assemblato in
TASK-51 da `src/ddforge/sprite_prep/manifest.py`, TASK-50) è agganciato ad
`assets._CITY_LANDMARK_SPRITES` per i luoghi che copre; gli altri restano sul
ripiego preso dai 440 object dei pack di Jay (sez. 1-bis). TASK-62: cattedrale,
palazzo e arena sono stati commissionati (prompt/26-28, TASK-55/57/58),
elaborati in TASK-61 e agganciati qui. Stato ad oggi, 26 luoghi su 36 coperti:

### Coperti dal pacchetto (26)

| luogo | sprite | note |
|---|---|---|
| ospedale, teatro, accademia, prigione, municipio, faro, bagni, biblioteca, tempio, monastero, caserma, banca, alchimista, magazzino, fabbro, stalle, fornaio, macelleria, taverna, locanda, bordello | `nm_<luogo>` | 1:1, un edificio singolo come commissionato |
| cattedrale, palazzo, arena | `nm_<luogo>` | TASK-62, sono SITE_BLOCK (occupano un isolato intero come accademia/monastero): cambia solo lo sprite, l'ingombro resta quello di un isolato |
| cimitero | `nm_cimitero_croce`, `nm_cimitero_fossa`, `nm_cimitero_lapide_1` | commissionate 3 varianti di lapide (prompt/11-cimitero.md), prodotta solo `lapide_1`: meno varietà fra una tomba e l'altra, non un errore |
| mercato | `nm_banco_mercato_1` | commissionati banco×3/cesta/carro (sez. 4), prodotto solo un banco |

### Ancora sul ripiego (10)

| luogo | sprite di ripiego | perché |
|---|---|---|
| dogana, conceria, macello | `shed_02` | non commissionato |
| mulino | `windmill_02` | non commissionato |
| lazzaretto | `strawhouse_03` | non commissionato |
| torre_guardia | `wood_walls_tower` | non commissionato |
| patibolo | `thehangedman` | non commissionato |
| statua | `statue_male_mage_alt_03_a` | non commissionato |
| fiera | `tent_03` | non commissionato |
| giardino | alberi delle texture base del programma | non commissionato |

### Scala dei lotti (TASK-59, TASK-62)

I 19 luoghi chiusi SITE_LOT/SITE_BAND coperti dal pacchetto (tutti quelli
della prima tabella tranne accademia/monastero/cattedrale/palazzo/arena, che
sono SITE_BLOCK e a isolato intero) hanno `LandmarkKind.lots=3.0` da
TASK-62: partivano da 1.0 (un lotto), TASK-59 li aveva portati a 1.5/2.0,
TASK-62 li ha portati tutti uniformemente a 3.0 su richiesta di Jay. Un
lotto in più nella stessa fila allarga l'ingombro solo in larghezza (la
profondità della fila resta fissa), quindi lo sprite cresce di scala ma non
raddoppia semplicemente moltiplicando `lots` per due; una riscrittura del
piazzamento su due assi resta fuori scope. Quando la fila non ha 3 lotti
liberi di fila (soprattutto al preset "isolato"), `city._lot_candidates` e
`city._band_candidates` ripiegano su uno span più piccolo invece di non
piazzare il luogo: mercato, cimitero, accademia e monastero restano
invariati (esclusi da Jay o senza una leva sicura, vedi commento su
`_block_candidates`).

### Sprite sempre, anche a isolato; fill maggiore a quartiere (TASK-63)

Dopo aver visto le mappe di TASK-62, Jay ha chiesto due cose in più. Primo:
i 24 luoghi chiusi coperti dal pacchetto (i 19 della sez. "Scala dei lotti"
più cattedrale, palazzo, arena, accademia, monastero) mostrano ora sempre lo
sprite dedicato anche al preset `isolato`, invece dell'edificio a stanze che
`building.py` genererebbe quando il lotto è abbastanza grande
(`LandmarkKind.sprite_only=True`, sez. 1 e 7). I luoghi ancora sul ripiego
(dogana, conceria, macello, mulino, lazzaretto, torre_guardia) restano un
edificio a stanze a isolato come prima, invariati. Secondo: a `quartiere` lo
sprite riempie il lotto di più (`compose._SPRITE_FILL_QUARTIERE=1.0` invece
di `_SPRITE_FILL=0.92`, un margine in meno attorno allo sprite, mai oltre il
rettangolo buildable del lotto). A `citta` non cambia niente: Jay ha chiesto
esplicitamente di non toccarla.

### Ancora più grandi a quartiere, statua più piccola (TASK-64)

Nemmeno il fill a 1.0 bastava: Jay ha aperto
`generated/city_quartiere_task63.dungeondraft_map` in Dungeondraft e
ridimensionato a mano la locanda (`nm_locanda`, scala 2.80804 → 3.33594,
+18.8%) come riferimento. `compose._SPRITE_SCALE_BOOST_QUARTIERE` applica
lo stesso fattore alla scala finale di ogni luogo chiuso coperto, solo a
`quartiere`: un moltiplicatore diretto sull'oggetto invece di spingere
ancora `LandmarkKind.lots` (che avrebbe sbattuto di nuovo contro il tetto di
profondità del lotto, sez. "Scala dei lotti") — può sconfinare leggermente
nel margine attorno al lotto, ma è il riferimento scelto da Jay stesso.
Le case ordinarie a `quartiere` sono state dimezzate in larghezza per
riempire di più la mappa (`SCALE_PRESETS["quartiere"]` in `city.py`), il che
rendeva la statua (`piece_size=1.5` su tutti i preset) sproporzionata:
`compose._STATUA_PIECE_FACTOR_QUARTIERE=0.6` la rimpicciolisce, solo a
`quartiere`. Le strade a `quartiere` ora si toccano e si intersecano sempre
ai T e agli incroci (`street_path_fraction` portato a 1.0, costo: niente
più serpeggiamento). Tutto solo a `quartiere`: `isolato` e `citta` restano
come in TASK-63.

### Generati ma non ancora agganciati

`nm_villa_nobiliare.png` e `nm_armeria.png` sono nel pacchetto e nel catalogo
(`data/assets.json`) ma **non finiscono su nessuna mappa**: non esiste un
`LandmarkKind` "villa nobiliare" o "armeria" in
`src/ddforge/generators/landmarks.py` (prompt/10-villa-nobiliare.md,
prompt/12-armeria.md, TASK-49). Serve un task a parte per aggiungere il
`LandmarkKind` (categoria, `scales`, `rule`, dimensione dei lotti, misurata
come per l'ospedale in TASK-48.1) prima che questi due sprite abbiano un
posto dove finire.
