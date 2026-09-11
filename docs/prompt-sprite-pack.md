# Prompt per Claude Design — pacchetto sprite "Nova Mistralis Città"

Da incollare in Claude Design. Se lo strumento genera un'immagine alla volta,
usa la **parte A** una volta sola come contesto e poi la **riga della parte
C** del pezzo che ti serve; se accetta un brief intero, incolla tutto.

Contenuto derivato da `docs/sprite-luoghi.md`, dove ci sono le misure vere e
il perché di ogni vincolo.

---

## Parte A — Brief (incollare per primo)

> Devi disegnare un pacchetto di sprite per mappe di città da gioco di ruolo,
> destinato a Dungeondraft. Sono elementi di una mappa **vista dall'alto**:
> ogni sprite è un edificio o un oggetto ritagliato, che verrà appoggiato su
> una mappa già disegnata da qualcun altro (strade, terreno, altre case).
>
> **Punto di vista.** Ortogonale dall'alto, perfettamente a picco. Nessuna
> prospettiva, nessuna assonometria, nessun punto di fuga: si vedono i tetti
> e le corti, non le facciate. Gli sprite verranno ruotati sulla mappa, quindi
> non devono avere un "sotto" e un "sopra" prospettici.
>
> **Sfondo.** Trasparente. Dentro l'immagine c'è **solo** l'edificio o
> l'oggetto e il terreno strettamente suo (la corte recintata di una caserma,
> la vasca di una conceria). Mai prato, mare, bosco, colline o strade intorno:
> lo sprite viene incollato in mezzo a un quartiere fitto, e un contorno di
> campagna lo fa sembrare una toppa fuori posto. Questo è l'errore da evitare
> più di ogni altro.
>
> **Stile.** Illustrazione dipinta a mano, calda, da mappa fantasy di
> ambientazione medievale europea. Tratto morbido, non pixel art, non
> vettoriale piatto, non fotorealistico. Il riferimento è una mappa di città
> disegnata a mano per un manuale di gioco di ruolo.
>
> **Luce e ombra.** Una sola sorgente di luce per tutto il pacchetto, in alto
> a sinistra; ombra corta e morbida proiettata in basso a destra. L'ombra fa
> parte dello sprite ma deve restare contenuta, non allargarsi oltre l'oggetto
> più di un decimo della sua larghezza.
>
> **Palette.** Toni terrosi e naturali: pietra grigia e ocra, legno bruno,
> intonaco chiaro, verde smorzato. Niente colori saturi o acidi.
>
> **Tetti in rosso.** I tetti degli edifici ordinari vanno dipinti in **rosso
> mattone saturo e uniforme**: il programma li ricolora automaticamente
> intervenendo sul rosso, ed è così che due case identiche appaiono di colore
> diverso sulla mappa. Le parti che NON devono cambiare colore (pietra, legno,
> terreno) non devono contenere rosso saturo.
>
> **Formato di consegna.** PNG con canale alfa. **Non WebP**: il resto della
> pipeline legge le dimensioni dall'header di un PNG e con un WebP non
> funziona. Un file per sprite, quadrato, con l'oggetto centrato e un margine
> trasparente di circa il 5% per lato.
>
> **Scala.** 256 pixel corrispondono a 1,5 metri reali. Disegna ogni pezzo
> alla sua dimensione vera: una lapide è alta circa un metro, un banco da
> mercato ne misura due, una baracca quattro, una cattedrale trenta. Le
> proporzioni fra un pezzo e l'altro devono reggere, perché finiscono tutti
> sulla stessa mappa.
>
> **Nomi dei file.** `nm_<nome>.png`, tutto minuscolo, solo lettere ASCII e
> underscore. I nomi sono indicati nell'elenco.

## Parte B — Coerenza del pacchetto

> Gli sprite verranno visti tutti insieme sulla stessa mappa, spesso a
> poche decine di pixel di distanza. Tieni quindi costanti su tutto il
> pacchetto: direzione della luce, spessore del tratto, grana della texture,
> saturazione, e il modo in cui rendi i materiali ricorrenti (tegole, paglia,
> pietra a vista, intonaco, legno, acqua).
>
> Gli edifici devono distinguersi **per forma e per dettaglio caratteristico**,
> non per dimensione: sulla mappa la loro dimensione la decide il programma.
> Una taverna e una locanda occupano lo stesso spazio, e chi guarda deve
> riconoscerle dall'insegna e dalla stalla annessa.

## Parte C — Elenco degli sprite

### C1. Monumenti — 1024×1024 px

| nome file | soggetto |
|---|---|
| `nm_cattedrale.png` | Cattedrale: navata lunga, transetto, abside semicircolare, campanile su un fianco. L'edificio religioso più grande della città, ~30 m. |
| `nm_palazzo.png` | Palazzo del Signore: residenza fortificata a corte interna quadrata, torri angolari basse, ingresso monumentale. Non un castello isolato: sta dentro la città. |
| `nm_monastero.png` | Monastero: chiostro quadrato con portico, chiesa su un lato, orto coltivato a filari, muro di cinta basso. |
| `nm_accademia.png` | Accademia di magia: corpo centrale a L con una torre-osservatorio, cupola o astrolabio sul tetto, cortile lastricato. |
| `nm_arena.png` | Arena: anfiteatro ellittico, gradinate concentriche, sabbia al centro, ingressi contrapposti. |

### C2. Edifici pubblici — 768×768 px

| nome file | soggetto |
|---|---|
| `nm_tempio.png` | Tempio: chiesa a navata unica con piccolo campanile e sagrato. Deve leggersi come una versione minore della cattedrale. |
| `nm_municipio.png` | Municipio: palazzo civico con loggia al piano terra e torre dell'orologio. |
| `nm_caserma.png` | Caserma della guardia: edificio a U attorno a un cortile d'armi recintato, rastrelliere. |
| `nm_teatro.png` | Teatro: pianta semicircolare, gradinate coperte, palco sul lato piatto. |
| `nm_bagni.png` | Bagni pubblici: vasche rettangolari a cielo aperto, portico su tre lati. |
| `nm_mulino.png` | Mulino **ad acqua**: casa in pietra con grande ruota idraulica su un fianco e canale di derivazione. Verrà sempre piazzato sulla riva di un fiume. |
| `nm_faro.png` | Faro: torre cilindrica vista a picco, lanterna vetrata al centro, base allargata. Verrà piazzato sulla banchina del porto. |
| `nm_lazzaretto.png` | Lazzaretto: edificio lungo e basso, isolato, recinto di pali, portantine all'ingresso. |
| `nm_prigione.png` | Prigione: blocco massiccio in pietra senza aperture sul tetto, cortile chiuso da mura alte. |

### C3. Botteghe e servizi — 512×512 px

Edifici di taglia ordinaria (~10 m). Si distinguono per il dettaglio, non per
la mole.

| nome file | soggetto |
|---|---|
| `nm_taverna.png` | Taverna: casa a due piani, insegna sporgente, tavoli e panche all'aperto, botti. |
| `nm_locanda.png` | Locanda: come la taverna ma più grande, con stalla annessa e cortile per i cavalli. |
| `nm_bordello.png` | Casa di piacere: casa a due piani con balconata coperta e lanterne all'ingresso. |
| `nm_fabbro.png` | Fabbro: bottega con fucina a cielo aperto sul retro, incudine, catasta di carbone, tempra. |
| `nm_stalle.png` | Stalle e maniscalco: tettoia lunga aperta, recinto, abbeveratoio, balle di fieno. |
| `nm_magazzino.png` | Magazzino: capannone con portone largo, casse e barili accatastati fuori, argano. |
| `nm_alchimista.png` | Bottega dell'alchimista: casa stretta con serra vetrata sul tetto e alambicchi. |
| `nm_biblioteca.png` | Biblioteca: edificio compatto con lucernari sul tetto e scalinata d'ingresso. |
| `nm_banca.png` | Casa di cambio: facciata con colonne, ingresso presidiato, finestre sbarrate. |
| `nm_gilda.png` | Sede di gilda: casa signorile con stendardo sopra l'ingresso e cortile chiuso. |
| `nm_dogana.png` | Dogana: edificio basso con tettoia per le merci, sbarra, banco di controllo. Verrà piazzata a ridosso di una porta delle mura. |
| `nm_torre_guardia.png` | Torre di guardia: torre quadrata vista a picco, ballatoio merlato, scala esterna. |
| `nm_conceria.png` | Conceria: capannone con vasche di concia scoperte allineate e pelli stese ad asciugare. Verrà piazzata sul fiume, a valle della città. |
| `nm_macello.png` | Macello: edificio basso con cortile lastricato, recinto per il bestiame, canale di scolo. |

### C4. Pezzi dei luoghi all'aperto — 256×256 px

Oggetti singoli, non scene: il programma li ripete e li distribuisce a caso
dentro un'area. Disegnali alla dimensione vera indicata.

| nome file | soggetto | dimensione vera |
|---|---|---|
| `nm_banco_mercato_1.png` … `_3.png` | Banco da mercato con tenda a strisce, merci esposte. Tre varianti diverse per tenda e merce. | 2 × 2 m |
| `nm_cesta_merci.png` | Ceste e sacchi accatastati. | 1,5 m |
| `nm_carro.png` | Carro a due ruote, carico coperto da un telo. | 3 × 1,5 m |
| `nm_banco_pesce_1.png`, `_2.png` | Banco del pescivendolo, cassette di pesce, ghiaccio. | 2 × 2 m |
| `nm_rete_stesa.png` | Rete da pesca stesa ad asciugare su cavalletti. | 3 × 2 m |
| `nm_scafo_cantiere.png` | Scafo di barca in costruzione su invasatura. **512×512** | 6 × 3 m |
| `nm_impalcatura.png` | Impalcatura in legno da cantiere. | 3 × 2 m |
| `nm_catasta_legname.png` | Catasta di tronchi squadrati. | 2,5 × 1,5 m |
| `nm_forca.png` | Forca in legno con cappio. | 2 × 2 m |
| `nm_gogna.png` | Gogna, ceppi in legno su piedistallo. | 1,5 × 1,5 m |
| `nm_statua_1.png` … `_3.png` | Statua su piedistallo, vista dall'alto: guerriero, figura ammantata, mago. | 1,5 × 1,5 m |
| `nm_albero_1.png` … `_3.png` | Chioma d'albero a picco: latifoglia larga, latifoglia stretta, conifera. | 4–6 m |
| `nm_cespuglio_1.png`, `_2.png` | Cespuglio tondeggiante. | 1,5 m |
| `nm_aiuola.png` | Aiuola fiorita bordata di pietra. | 2 × 2 m |
| `nm_panchina.png` | Panchina in pietra. | 1,5 × 0,5 m |
| `nm_lapide_1.png` … `_3.png` | Lapide vista dall'alto con il suo tumulo: arcuata, spezzata, a croce. | 1 × 2 m |
| `nm_tomba_cassa.png` | Sarcofago in pietra a livello del suolo. | 1 × 2,5 m |
| `nm_cappella.png` | Cappella funeraria. **512×512** | 3 × 4 m |
| `nm_baracca_1.png` … `_3.png` | Baracca di assi e teli rattoppati, tetti storti. Tre varianti. | 4 × 3 m |
| `nm_catasta_rifiuti.png` | Cumulo di rifiuti e assi rotte. | 2 m |
| `nm_fuoco.png` | Fuoco acceso con cerchio di pietre. | 1,5 m |
| `nm_tendone_1.png`, `_2.png` | Tendone da fiera a strisce. **512×512** | 5 × 5 m |
| `nm_palco.png` | Palco in legno per spettacoli. | 4 × 3 m |
| `nm_bancarella.png` | Bancarella da fiera con insegna. | 2 × 2 m |

### C5. Struttura — 512×512 px

| nome file | soggetto |
|---|---|
| `nm_porta_mura.png` | Porta fortificata: due torri gemelle affiancate all'apertura, arco fra le due, saracinesca. Verrà piazzata a cavallo della cinta muraria, che è disegnata come una striscia continua: l'apertura deve stare al centro dello sprite. |

### C6. Case ordinarie — 512×512 px (facoltative ma consigliate)

| nome file | soggetto |
|---|---|
| `nm_casa_01.png` … `nm_casa_12.png` | Casa cittadina ordinaria, dodici varianti: pianta rettangolare, a L, con cortile, con bottega al piano terra, con ballatoio, a schiera. **Tetti in rosso mattone saturo** (è il canale che il programma ricolora). Ogni variante ~8 × 6 m. |
| `nm_casa_povera_1.png` … `_3.png` | Casa povera col tetto di paglia, tre varianti. Tetto in **paglia**, non rosso: queste non devono cambiare colore. |

Una mappa ne usa da 160 a 2700 copie: è il tessuto su cui si staccano tutti
gli altri sprite, e la sua coerenza con loro decide l'aspetto della mappa.

### C7. Texture di terreno — 1024×1024 px, piastrellabili senza cuciture

| nome file | soggetto |
|---|---|
| `nm_prato.png` | Erba corta, verde smorzato. |
| `nm_terra.png` | Terra battuta bruna. |
| `nm_selciato.png` | Selciato in ciottoli grigi. |
| `nm_ghiaia.png` | Ghiaia chiara per i vialetti. |

Vanno consegnate **due volte**, in `textures/terrain/` e in
`textures/patterns/normal/`: la prima cartella è quella naturale per un
terreno, la seconda è l'unica da cui sappiamo per certo che il programma le
accetta come area dipinta.

---

## Parte D — Come consegnare

Struttura del pacchetto, se lo strumento può produrre un archivio:

```
NovaMistralisCitta/
  data.json                     # id, name, author, version del pack
  textures/objects/             # C1-C6, tutti i PNG
  textures/terrain/             # C7
  textures/patterns/normal/     # C7, gli stessi file
  preview.png
```

Altrimenti va bene una cartella piatta di PNG con i nomi indicati: la
struttura del pack la si costruisce dopo.

## Parte E — Checklist prima di consegnare

- [ ] Ogni PNG ha il canale alfa e lo sfondo è davvero trasparente
- [ ] Nessuno sprite contiene terreno, prato, mare o strada che non gli appartenga
- [ ] Vista a picco: non si vede nessuna facciata
- [ ] Luce da in alto a sinistra su tutti i pezzi, senza eccezioni
- [ ] I tetti delle case ordinarie sono rosso saturo e uniforme
- [ ] Le proporzioni reggono fra pezzi diversi (lapide, banco, baracca, cattedrale sulla stessa scala)
- [ ] Nessun file in WebP
- [ ] I nomi seguono `nm_<nome>.png`, minuscolo, ASCII
