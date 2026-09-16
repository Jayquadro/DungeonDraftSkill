# Post-processing degli sprite grezzi (TASK-50)

Le schede in `prompt/` producono JPEG con un soggetto isolato su fondo magenta
piatto (`#FF00FF`). In quella forma non sono usabili su Dungeondraft: niente
canale alfa, frangia magenta sul bordo, ombra e canvas diversi da sprite a
sprite, rosso dei tetti disomogeneo. Questa procedura porta un JPEG grezzo al
PNG pronto per il pack, con **gli stessi numeri per tutto il pacchetto**.

## Comando

```bash
python scripts/prepare_sprites.py                       # assets/ -> assets/sprites/
python scripts/prepare_sprites.py --only ospedale,faro   # solo questi due (nome sprite, senza nm_/.png)
python scripts/prepare_sprites.py --input X --output Y --report Y/rapporto.json
```

Un solo passaggio: legge ogni JPEG di `--input` che ha una voce nel manifest
(sotto), lo elabora e scrive il PNG risultante in `--output`, poi scrive
`rapporto.json` (default: `<output>/rapporto.json`) e ne stampa un riassunto
in console. Richiede `pip install -e ".[sprites]"` (Pillow + numpy).

Il comando esce con codice diverso da zero se qualche sprite del manifest è
**mancante** o in **errore** (non se ci sono solo avvisi): comodo per uno
script che lo richiama in sequenza.

## Cosa fa, in ordine

1. **Scontorno del magenta.** Distanza euclidea di ogni pixel dal magenta
   puro `(255, 0, 255)`: sotto una soglia è sfondo (alfa 0), sopra un'altra è
   soggetto pieno (alfa 255), in mezzo l'alfa sfuma linearmente — copre la
   frangia che la compressione JPEG lascia sul bordo del soggetto.
   **Non usa un modello di segmentazione** (tipo rembg): lo sfondo delle
   schede è sintetico e piatto, non una foto, quindi una soglia di colore è
   più affidabile, non scarica nulla e non dipende dalla rete o dalla GPU —
   è anche l'unico modo per avere un passo deterministico e testabile in CI.
2. **Despill.** Sui pixel di bordo (alfa intermedio) la tinta magenta residua
   (R e B più alti di G) viene riportata al livello di G, così un bordo
   parzialmente trasparente non resta rosa.
3. **Pulizia alfa e ritaglio.** I pixel quasi trasparenti (< soglia) vengono
   azzerati, poi l'immagine si ritaglia al bounding box del soggetto.
4. **Scala e centratura.** Due modalità, prese dalla categoria dello sprite:
   - `canvas` (C1/C2/C3): l'oggetto riempie il canvas della categoria, con
     margine trasparente del **5%** per lato anche per l'ombra.
   - `reale` (C4, pezzi a scala reale): 256 px = 1,5 m; il canvas si allarga
     quanto serve per contenere oggetto, margine e ombra, arrotondato a un
     multiplo di 16.
5. **Rosso dei tetti.** Secondo la regola della scheda:
   - `tetto`: i rossi entro ±25° di tinta e sopra le soglie di saturazione
     minima vanno a tinta 0, saturazione 0,85, luminosità invariata —
     rosso saturo uniforme, la stessa cosa che Dungeondraft userà come
     canale di ricolorazione.
   - `vietato`: i pixel che rientrano nelle soglie `custom_color_overrides`
     di Dungeondraft (vedi sotto) vengono spostati su una tinta ocra, con un
     margine di sicurezza più largo delle soglie stesse.
   - `libero`: nessun intervento sul colore.
6. **Ombra.** Aggiunta in post, mai lasciata al modello che ha generato
   l'immagine: offset 4% del lato maggiore dell'oggetto, sfocatura 2,5%,
   opacità 45%, colore `(22, 16, 10)`, portata in basso a destra (luce da
   in alto a sinistra).
7. **Validazione.** Per ogni sprite: canale alfa reale, canvas quadrato,
   margine trasparente rispettato, proporzioni coerenti con le dimensioni in
   metri dichiarate (dove note), frazione di pixel "ricolorabili" secondo le
   soglie di Dungeondraft, quanti bordi dell'immagine grezza il soggetto
   tocca (indizio di un soggetto tagliato in fase di generazione).
8. **Salvataggio.** PNG con canale alfa, mai WebP: `assets.read_dungeondraft_pack`
   legge le dimensioni dall'header IHDR di un PNG, con un WebP resta cieco.

I numeri (margine, ombra, soglie del rosso) sono quelli di
`sprite-batch.zip/catalogo.yaml` — non duplicarli altrove, cambiarli in un
posto solo (`src/ddforge/sprite_prep/settings.py`) se mai devono cambiare.

## Il manifest: quale file va con quale sprite

`src/ddforge/sprite_prep/manifest.py` associa ogni **nome file grezzo** in
`assets/` alla sua categoria, canvas e regola del rosso, presi dalla tabella
di intestazione della scheda corrispondente in `prompt/*.md`. Un file senza
voce nel manifest (compreso `assets/template.png`, che non è uno sprite
grezzo ma un'icona di riferimento) **non viene elaborato**: compare nella
sezione "ignorati" del rapporto, così non sparisce senza spiegazione.

Quando arriva un nuovo JPEG da Jay, la prima cosa da fare è aggiungere una
riga al manifest — non un file a parte, non un caso speciale nel codice.

Due voci non hanno un LandmarkKind misurato in `generators/landmarks.py`
(`villa_nobiliare`, `armeria`): canvas e categoria sono quelli scritti come
proposta non misurata in `prompt/10-villa-nobiliare.md` e `prompt/12-armeria.md`.

Il cimitero (`prompt/11-cimitero.md`) è un luogo all'aperto: produce più
pezzi a scala reale (`nm_cimitero_croce.png`, `nm_cimitero_fossa.png`,
`nm_cimitero_lapide_1.png`, …), non un edificio. Il manifest ha oggi solo
`lapide_1`: le varianti `_2`/`_3` si aggiungono con la stessa riga quando
Jay le genera.

## Il rapporto

`rapporto.json` elenca, per ogni voce del manifest:

- `stato`: `ok` (nessun avviso), `avvisi` (elaborato, ma con avvisi da
  guardare), `errore` (non elaborabile, es. immagine vuota dopo lo
  scontorno), `mancante` (il file grezzo non c'è in `--input`);
- `avvisi`: la lista dei controlli falliti (vedi punto 7 sopra);
- `info`: lato dell'oggetto e canvas usati, frazione di pixel ricolorabili,
  quanti bordi tocca il soggetto grezzo.

**Da rigenerare**: tutto ciò che non è `ok`. `avvisi` non blocca — lo sprite
è comunque salvato — ma va guardato prima di considerarlo definitivo.

## Perché non il pacchetto `spritebatch` di `sprite-batch.zip` così com'è

Quello zip contiene un pacchetto Python più grande, pensato per generare gli
sprite via API (`openai`/`comfyui`), scontornarli con `rembg` quando il
modello non dà trasparenza reale, e assemblare l'intero pack Dungeondraft.
Per TASK-50 (solo post-processing: le immagini le genera Jay a mano) tre
pezzi di quel pacchetto non servivano ed erano un costo netto:

- la generazione via API e i suoi backend;
- `rembg`, un modello di segmentazione fotografica da ~1 GB da scaricare,
  non deterministico e senza bisogno reale con uno sfondo magenta sintetico
  e piatto — un chroma-key per distanza di colore fa lo stesso lavoro senza
  rete, senza GPU e in modo riproducibile nei test;
- l'assemblaggio del pack (`pack.json`, `preview.png`, …), che è TASK-51.

I **numeri** di scala, ombra e soglie del rosso restano identici a quelli di
`sprite-batch.zip/catalogo.yaml`: il codice puro che li applica (geometria,
normalizzazione del rosso) è portato quasi identico in
`src/ddforge/sprite_prep/imaging.py`.
