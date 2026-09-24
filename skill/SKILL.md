---
name: dungeondraft-map-generator
description: Genera mappe .dungeondraft_map (dungeon, edifici, grotte, fognature, città) da una richiesta in linguaggio naturale, invocando la CLI ddforge. Da usare quando l'utente chiede una mappa, un dungeon, un edificio, una grotta o una città per Dungeondraft.
---

# Dungeondraft Map Generator

Questa skill traduce una richiesta in linguaggio naturale in una mappa
`.dungeondraft_map` giocabile, invocando la CLI `ddforge`. **Non genera mai
il file da sola**: tutta la geometria e la serializzazione vivono in
`src/ddforge/`, questa skill si limita a scegliere i parametri giusti e a
leggere l'esito.

Riferimenti da consultare durante il lavoro (non duplicarne il contenuto
qui):
- `references/styles.md` — algoritmi disponibili, palette, tipologie di
  edificio, preset di scala città, quando usare ciascuno
- `references/examples.md` — invocazioni concrete della CLI per ogni caso

## Prima di invocare: due vincoli operativi

1. **Lavora dalla root del repo.** `ddforge` risolve `data/assets.json` e
   `templates/` come percorsi *relativi*: lanciato da un'altra directory
   fallisce subito con `Errore: Catalogo asset non trovato: data\assets.json`.
2. **`ddforge` non è nel PATH** e `python -m ddforge` non funziona (il
   package non ha `__main__.py`). Usa l'eseguibile dell'ambiente virtuale
   del progetto — su questa installazione `.venv/Scripts/ddforge` — oppure
   `ddforge` se l'ambiente è già attivato. Negli esempi è scritto `ddforge`
   per brevità.

## Workflow (quattro passi)

### 1. Interpretare la richiesta

Leggi la richiesta dell'utente e traducila nei parametri di
`ddforge generate`, consultando `references/styles.md` per scegliere:

- **algoritmo** (`dungeon`, `building`, `cave`, `sewer`, `city`) dal tipo di
  ambiente richiesto ("una cripta" → `dungeon`, "una taverna" → `building`,
  "una grotta" → `cave`, "fognature" → `sewer`, "un quartiere/una città" →
  `city`)
- **dimensioni** (`--width`/`--height`) coerenti con quanto chiesto, **senza
  mai superare il canvas del template** (vedi il passo 2: è il vincolo più
  facile da sbagliare, e non produce un errore). Per `building` non passarle
  affatto se la richiesta non dà una misura: ogni tipologia ha già il suo
  ingombro realistico.
- **numero di stanze** (`--rooms`, solo `dungeon`) se la richiesta lo
  specifica ("otto stanze" → `--rooms 8`)
- **palette** (`--style`) e, per `building`, **tipologia**
  (`--building-type`) dal tono della richiesta
- **densità di arredo** (`--furnish none|light|medium|heavy`) e **luci**
  (`--lights`) dal tono richiesto (es. "poca luce" → non passare `--lights`;
  "arredata riccamente" → `--furnish heavy`); non si applicano a `cave`,
  `sewer` e `city`
- per `city`, lo **`--scale`** (`isolato`/`quartiere`/`citta`) e gli
  eventuali `--landmark`/`--no-landmarks`, come spiegato in
  `references/styles.md`

Se la richiesta è ambigua su un parametro che cambia sostanzialmente il
risultato (dimensioni molto diverse, scala città), chiedi chiarimento
invece di indovinare.

### 2. Invocare il CLI

Esegui `ddforge generate <algoritmo> [opzioni]` con i parametri scelti,
scrivendo in `generated/` salvo indicazione diversa dell'utente. Scegli un
`--seed` esplicito così la mappa è riproducibile se va rigenerata.

`ddforge` **non ridimensiona mai il canvas**: le dimensioni della mappa sono
quelle del template, e `--width`/`--height` dicono solo quanta di quell'area
riempire. Scegli il template in base a quanto deve essere grande la mappa:

| Template | Canvas reale | `--width`/`--height` massimi consigliati |
|---|---|---|
| `templates/blank_80x80.dungeondraft_map` | 80×80 | 78×78 |
| `templates/blank_160x160.dungeondraft_map` | **128×128** (il nome inganna) | 126×126 |

`generate` valida sempre il risultato **prima** di scrivere il file.

### 3. Leggere l'esito e correggere i parametri

Il comando fallisce in due modi diversi, e **solo uno dei due si vede dal
codice di uscita**:

- **Uscita ≠ 0** — errori di validazione: il file **non è stato scritto**.
  Gli `Issue` (`[ERRORE] DDFxxx <percorso>: <messaggio>`) sono stampati, così
  come gli errori di parametro (es. un `--landmark` non ammissibile per lo
  `--scale` scelto). Leggi il messaggio e correggi i parametri.
- **Uscita 0 ma con avvisi `DDF101`** — il file è stato scritto, ma contiene
  geometria **fuori dal canvas**: succede quando `--width`/`--height`
  eccedono il template (passo 2). Il comando non lo considera un errore, ma
  la mappa è sbagliata: rigenera con dimensioni che stanno nel canvas, o con
  il template più grande.

Gli avvisi **`DDF102`** ("gruppo di muri connessi senza alcuna porta") sono
invece ordinaria amministrazione: ne compaiono su quasi tutte le mappe (una
fognatura normale ne produce una ventina). Non inseguirli e non rigenerare
per farli sparire; al massimo menzionali di sfuggita.

**Non modificare mai il file `.dungeondraft_map` a mano, né scrivere o
patchare il JSON direttamente.** Si correggono sempre e solo i **parametri**
della prossima invocazione. Il generatore e il validatore esistono apposta
perché il formato è pieno di vincoli non ovvi (§2 e §7 di `docs/SPEC.md`);
un JSON toccato a mano rischia di produrre una mappa che Dungeondraft apre
vuota o corrotta senza nessun errore visibile. Se dopo aver corretto i
parametri ragionevoli il comando continua a fallire, fermati e chiedi
all'utente invece di intervenire sul file.

### 4. Consegnare il file

Quando `generate` scrive il file con successo:

- indica il percorso esatto dove è stato salvato
- **facoltativo ma consigliato**, come autocontrollo prima di consegnare:
  `ddforge preview <file> --out <file>.png` rende una planimetria PNG che
  puoi guardare senza aprire Dungeondraft, utile per accorgersi di una mappa
  vistosamente sbagliata. Attenzione ai suoi limiti: disegna pavimenti,
  muri, porte e oggetti, **non** le strade (`paths`) né i tetti, e per le
  grotte esce **completamente vuota** (bug noto nella decodifica del layer
  `cave`: il PNG nero non significa che la mappa sia vuota).
- spiega come aprirlo: in Dungeondraft, **File → Open Map** (o l'analogo nel
  menu principale) e selezionare il file `.dungeondraft_map` generato; non
  serve importarlo o convertirlo, è già nel formato nativo
