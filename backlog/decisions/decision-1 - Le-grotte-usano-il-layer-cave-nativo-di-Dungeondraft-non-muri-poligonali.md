---
id: decision-1
title: 'Le grotte usano il layer cave nativo di Dungeondraft, non muri poligonali'
date: '2026-09-07 11:49'
status: accepted
---
## Context

SPEC.md §9.3 lasciava esplicitamente aperta a M5 la scelta di come rendere
il contorno di una grotta:

- **muri poligonali** (`add_wall` con molti punti): funziona di sicuro, ma
  la risoluzione e di un quadretto e il contorno resta a gradini ortogonali;
- **layer `cave` nativo** di Dungeondraft: visivamente molto migliore, ma
  la codifica di `cave.bitmap` non era stata risolta dall'analisi, che
  dichiarava le lunghezze osservate "non lineari" e non ricavabili per
  interpolazione (50×25→2614 B, 30×30→1892 B, 8×8→154 B).

La prescrizione era: provare **prima** i muri poligonali, e passare al
layer nativo solo se il risultato non fosse soddisfacente **e** solo dopo
aver decodificato il bitmap.

Nello spike TASK-31 sono successe due cose:

1. Il prototipo a muri poligonali e stato realizzato e Jay lo ha aperto in
   Dungeondraft: il contorno a gradini e stato giudicato **accettabile**.
   La via di riserva quindi esiste ed e valida.
2. La codifica di `cave.bitmap` e stata **risolta per intero**, grazie a due
   campioni prodotti da Jay disegnando nel layer cave e risalvando (uno a
   mano libera, uno controllato: un rettangolo netto di ~20×3 quadretti in
   alto a sinistra).

La condizione che teneva chiusa la porta al layer nativo — "non sappiamo
scrivere il bitmap" — non vale piu.

## Decision

**Le grotte si generano scrivendo il layer `cave` nativo di Dungeondraft.**
I muri poligonali restano la via di riserva documentata, non la strada
maestra.

La codifica e documentata per intero in `docs/format.md` §14: maschera
bit-packed su una griglia di `(4w+3) × (4h+3)` bit, 4 sotto-celle per
quadretto, row-major, flusso di bit continuo non allineato al byte,
LSB-first dentro ogni byte.

Motivazioni, in ordine di peso:

1. **Risoluzione 4× migliore.** La griglia nativa e a un quarto di
   quadretto: il contorno che si puo esprimere e quattro volte piu fine di
   qualunque muro poligonale costruito per quadretto. Su una grotta, dove
   l'irregolarita *e* la forma, e la differenza fra una caverna e una
   stanza dai bordi frastagliati.
2. **Il rendering lo fa Dungeondraft.** Il layer nativo ha gia ombreggiatura
   e smussatura delle pareti di roccia; con i muri poligonali stiamo invece
   usando un muro da edificio per rappresentare una parete di caverna.
3. **Il formato e verificato in scrittura, non solo in lettura.** Un
   rettangolo scritto da noi su quadretti noti e apparso esattamente dove
   previsto quando Jay ha aperto il file, e una grotta da cellular automata
   a risoluzione sotto-cella e stata approvata. Non e una decodifica
   plausibile: e un round-trip chiuso.
4. **Meno elementi nel documento.** Una grotta nativa e un blob di lunghezza
   fissa (gia presente nel template, anche vuoto) invece di un muro con
   centinaia di punti piu un pattern poligonale altrettanto grande.
5. **Niente falso positivo DDF102.** Il prototipo a muri produce l'avviso
   "gruppo di muri connessi senza porte" (limite noto del validatore,
   `docs/format.md` §9.5); la versione nativa valida pulita, perche non ci
   sono muri da scambiare per una stanza isolata.

## Consequences

- **TASK-32** (`generators/cave.py`) implementa il cellular automata
  direttamente a **risoluzione sotto-cella** (4× i quadretti), non a
  quadretti, e scrive il risultato in `level['cave']['bitmap']`. Il codec
  di riferimento vive oggi in `scripts/cave_spike.py` (codice di spike) e va
  portato in `src/ddforge/` **con i test**: il round-trip byte-esatto oggi e
  verificato a mano, non dalla suite.
- Serve una **primitiva nuova** in `build.py` (o un modulo dedicato) per il
  layer cave: le primitive attuali aggiungono elementi a liste disegnabili,
  mentre qui si scrive un blob di livello. Non e un `add_*` come gli altri.
- `template.blank_level` **preserva gia** `cave` fra i blob dimensionati
  sulla mappa: nessuna modifica necessaria li. Gli altri campi di `cave`
  (`ground_color`, `wall_color`, `texture`) sono gia popolati nel template
  vuoto e non vanno toccati.
- **Le grotte non avranno `walls`**, quindi non hanno `portals`: le porte
  annidate nei muri (`compose.connect`, TASK-19) non si applicano a una
  grotta. Un collegamento fra una grotta e una struttura costruita
  (dungeon, fognatura) va progettato a parte — `cave.entrance_bitmap`, che
  ha la stessa identica codifica, e il candidato naturale ma **non e ancora
  stato studiato**: in tutti i campioni disponibili e tutto a zero.
- Le **fognature** (TASK-33) sono una variante a canali ortogonali: non e
  detto che il layer cave sia la scelta giusta anche per loro, dove i bordi
  dritti sono voluti. Questa decisione riguarda le grotte; per le fognature
  va valutata quando ci si arriva.
- SPEC.md §2 e §9.3 restano **superate** su questo punto (dicono che la
  lunghezza del bitmap e non ricavabile). La correzione e in
  `docs/format.md` §11 e §14, coerentemente con §0 di quel documento, che
  raccoglie gli scostamenti verificati rispetto alla spec.

