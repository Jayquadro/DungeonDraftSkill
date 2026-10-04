# Esempi di invocazione del CLI

Invocazioni concrete di `ddforge generate`. **Tutti i comandi di questa
pagina sono stati eseguiti davvero**: escono con codice 0 e scrivono il
file, salvo quelli marcati come esempi di errore.

Due premesse operative (vedi `SKILL.md`):

- **lancia dalla root del repo**: `data/assets.json` e `templates/` sono
  percorsi relativi;
- **`ddforge` non è nel PATH**: usa `.venv/Scripts/ddforge` (o attiva
  l'ambiente). Qui sotto è scritto `ddforge` per brevità.

Adatta seed, dimensioni e opzioni alla richiesta — questi sono punti di
partenza. Per il significato di ogni opzione vedi `references/styles.md` o
`ddforge generate --help`.

## Scegliere il template e le dimensioni

`ddforge` non ridimensiona mai il canvas: viene dal template, e
`--width`/`--height` dicono solo quanta di quell'area riempire.

| Template | Canvas reale | Massimo consigliato |
|---|---|---|
| `templates/blank_80x80.dungeondraft_map` | 80×80 | `--width 78 --height 78` |
| `templates/blank_160x160.dungeondraft_map` | **128×128** (nome ingannevole) | `--width 126 --height 126` |

```bash
# mappa grande: template da 128x128, non 80x80
ddforge generate dungeon \
    --template templates/blank_160x160.dungeondraft_map \
    --out generated/cripta_grande.dungeondraft_map \
    --width 126 --height 126 \
    --rooms 16 --seed 1337
```

## Dungeon a stanze (cripte, sotterranei, prigioni)

Richiesta: *"una cripta di otto stanze con poca luce"*. "Otto stanze" →
`--rooms 8`; "poca luce" → non passare `--lights`, la cripta resta buia
(vale la scurovisione al tavolo).

```bash
ddforge generate dungeon \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/cripta.dungeondraft_map \
    --width 78 --height 78 \
    --rooms 8 --seed 1337 \
    --style crypt
```

Un dungeon più arredato e illuminato:

```bash
ddforge generate dungeon \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/sotterranei.dungeondraft_map \
    --width 60 --height 60 \
    --rooms 12 --seed 42 \
    --lights --furnish medium
```

## Edifici urbani (taverne, magioni, magazzini)

Senza `--width`/`--height` ogni tipologia usa il suo ingombro realistico di
default: non specificarle a meno che la richiesta non dia una misura.

```bash
# una taverna, pianta rettangolare
ddforge generate building \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/taverna.dungeondraft_map \
    --seed 7 \
    --building-type tavern --furnish medium --lights

# una magione a pianta a L
ddforge generate building \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/magione.dungeondraft_map \
    --seed 99 \
    --building-type manor --l-shaped --furnish heavy --lights
```

Entrambe scrivono il file con un paio di avvisi `DDF102`: normale, vedi
"Leggere l'esito" in fondo.

## Grotte

Niente `--furnish`/`--lights`: una grotta non ha stanze nel senso del
Blueprint principale. Niente `--width`/`--height` nemmeno: il layer cave
nativo copre sempre l'intera mappa del template (mai una sotto-regione più
piccola, a differenza degli altri stili), quindi le dimensioni sono sempre
quelle del template scelto.

```bash
ddforge generate cave \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/grotta.dungeondraft_map \
    --seed 1337
```

## Fognature

```bash
ddforge generate sewer \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/fognature.dungeondraft_map \
    --width 70 --height 70 --seed 1337
```

Una fognatura normale produce una ventina di avvisi `DDF102`: è previsto,
non è un difetto da correggere.

## Mappe cittadine

`--scale isolato` (default) è l'unico preset con edifici giocabili stanza
per stanza; `quartiere` e `citta` sono viste dall'alto, non layout tattici
— vedi `references/styles.md` per la differenza.

```bash
# un isolato giocabile al tavolo
ddforge generate city \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/isolato.dungeondraft_map \
    --width 78 --height 78 --seed 1337

# un quartiere intero visto dall'alto, con porto e faro garantiti
ddforge generate city \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/quartiere.dungeondraft_map \
    --width 78 --height 78 --seed 1337 \
    --scale quartiere --landmark porto --landmark faro

# una città intera, senza luoghi notevoli
ddforge generate city \
    --template templates/blank_80x80.dungeondraft_map \
    --out generated/citta.dungeondraft_map \
    --width 78 --height 78 --seed 1337 \
    --scale citta --no-landmarks
```

Il preset `citta` genera qualche migliaio di edifici: è sensibilmente più
lento degli altri due e produce un file molto più grande.

## Anteprima PNG (autocontrollo)

```bash
ddforge preview generated/cripta.dungeondraft_map \
    --out generated/cripta.png --scale 6
```

`--scale` sono i pixel per quadretto (default 8). Disegna pavimenti, muri,
porte, oggetti e il layer cave nativo delle grotte; **non** le strade
(`paths`) né i tetti — su una mappa cittadina si vedono gli edifici ma non
la viabilità.

## Rivalidare un file già scritto

`generate` valida sempre prima di scrivere, quindi non serve di norma; è
utile su un file ricevuto o vecchio.

```bash
ddforge validate generated/cripta.dungeondraft_map
# -> "Nessun problema trovato."
```

## Leggere l'esito

**Errore di parametro o di validazione — uscita ≠ 0, file NON scritto.**
Correggi i parametri, mai il JSON:

```bash
$ ddforge generate city --template templates/blank_80x80.dungeondraft_map \
    --out generated/prova.dungeondraft_map \
    --width 70 --height 70 --seed 1 --landmark arena --scale quartiere
Errore: L'elemento urbano 'arena' non e' ammissibile al preset di scala 'quartiere': preset ammessi ['citta']
```

**Avvisi `DDF101` — uscita 0, ma la mappa è sbagliata.** Dimensioni oltre il
canvas del template: il file viene scritto lo stesso, con geometria fuori
dal canvas. Rigenera entro il canvas o con il template da 128×128:

```bash
$ ddforge generate dungeon --template templates/blank_80x80.dungeondraft_map \
    --out generated/_troppo_grande.dungeondraft_map \
    --width 100 --height 100 --rooms 6 --seed 1
[AVVISO] DDF101 world.levels.0.patterns[12]: Coordinate (12800, 20608) fuori dal canvas (0..20480 x 0..20480 px)
...
Scritto generated/_troppo_grande.dungeondraft_map (23 avvisi)
```

**Avvisi `DDF102`** ("gruppo di muri connessi senza alcuna porta"): ordinari,
presenti su quasi tutte le mappe. Non rigenerare per farli sparire.
