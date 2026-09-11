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
| **edificio a stanze** | preset `isolato`, luogo chiuso | niente: lo genera `building.py` con muri, porte e tetto |
| **uno sprite che riempie l'ingombro** | preset `quartiere`/`citta`, luogo chiuso | **1 sprite** (o più varianti dello stesso luogo) |
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

## 3. Luoghi chiusi — uno sprite ciascuno (28)

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
| `gilda` | Sede di Gilda | 1,65 / 4,00 | stendardo sopra l'ingresso |
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
| `mercato` | Piazza del Mercato | 4,7 × 3,8 q | selciato | 2 q = **3 m** | banco con tenda ×3, cesta di merci, carro |
| `patibolo` | Patibolo | 3,6 × 3,2 q | selciato | 2 q = **3 m** | forca, gogna, ceppo |
| `statua` | Statua | 3,0 × 2,8 q | nessuno | 1,5 q = **2,2 m** | statua su piedistallo ×3 (guerriero, mago, figura ammantata) |
| `giardino` | Giardino Pubblico | 7,8 × 7,8 q | erba | 3 q = **4,5 m** | albero ×3, cespuglio ×2, aiuola, panchina |
| `cimitero` | Cimitero | 4,4 × 5,2 q | erba | 1,5 q = **2,2 m** | lapide ×3, tomba a cassa, croce, cappella |
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
| mercato, patibolo, cantiere | `tileset_cobble` (selciato) |
| statua | nessuna: sta già su una piazza pavimentata |

> **Non verificato:** che Dungeondraft accetti una texture di categoria
> `terrain` (`chr_grass`, `chr_dirt`) dentro un elemento `pattern`. L'indizio
> a favore è che il template ricco disegnato a mano da Jay usa come pattern
> texture di `tilesets/simple/`, quindi lo strumento non si limita a
> `patterns/normal/`. La conferma arriva dal foglio di
> `scripts/label_calibration.py`, che stende una toppa per ciascuna. Se il
> pacchetto includesse le stesse texture anche sotto
> `textures/patterns/normal/`, la questione sparirebbe del tutto.

## 7. Cosa NON serve

- Ponti, mura, fiume, riva: sono `path` o pavimenti, non object.

Nient'altro. In particolare **servono** anche `fornaio` e `macelleria`, che
esistono solo al preset `isolato`: pur essendo lì dei luoghi chiusi, ricadono
spesso sullo sprite (vedi la nota qui sotto).

> **Perché anche i luoghi del preset `isolato` hanno bisogno di uno sprite.**
> Lì un luogo chiuso *dovrebbe* essere un edificio a stanze vero, ma
> `building.generate` pretende almeno 6 quadretti per lato e molti lotti sono
> più stretti. Il generatore preferisce i lotti in cui l'edificio ci sta —
> misurato su 30 seed, il 55% dei luoghi chiusi ottiene la geometria vera
> contro il 17% di prima — ma il restante 45% ripiega sullo sprite. Il
> ripiego è voluto: un luogo con lo sprite è meglio di nessun luogo.

## 8. Facoltativo ma consigliato: le case ordinarie

Una mappa `quartiere` ha ~160 edifici ordinari, una `citta` ~2700. Oggi usano
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

Tre elementi che c'erano in una versione precedente di questo documento sono
stati **tolti dal catalogo** perché Jay li ha scartati guardando il
campionario: cantiere navale, mercato del pesce e quartiere povero. Con loro
è uscita anche la torre sulla porta delle mura: il varco nella cinta resta,
ma senza sprite sopra. Sulla banchina del porto resta il solo faro.
