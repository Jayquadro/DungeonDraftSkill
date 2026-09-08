---
id: decision-2
title: >-
  Le mappe cittadine supportano entrambi i regimi di scala come preset, non uno
  solo
date: '2026-09-07 14:48'
status: accepted
---
## Context

SPEC.md §9.4 lasciava esplicitamente aperta a M5 la scelta se dare al
generatore cittadino un solo regime di scala (1 quadretto = 5 ft, il
"quartiere" giocabile, stesso livello di dettaglio di dungeon/building) o
anche un secondo regime a 1 quadretto = 1 edificio (mappa di "città"
astratta, per un'intera città o un quartiere esteso).

`generators/city.py` (TASK-35) non è ancora implementato, quindi la misura
non poteva usare un generatore cittadino reale. È stata fatta su ciò che
esiste già, senza sintetizzare blob (vincolo non negoziabile di SPEC.md §2):
l'unico template reale disponibile è `templates/blank_80x80.dungeondraft_map`
(80×80 quadretti), e `template.prepare()` non tocca mai `world.width/height`
— la dimensione del canvas di un file generato è sempre quella del template,
indipendentemente da `--width/--height` (che regolano solo la geometria
logica del Blueprint). La variabile che cambia fra i due regimi non è quindi
la dimensione dei blob base, ma **quanti edifici reali entrano nello stesso
canvas** e quanti elementi disegnabili servono per rappresentarli.

**Regime "quartiere" (dettaglio pieno):** casi reali già esistenti e già
passati al gate umano M4 (TASK-30), generati da `building.py`:

| File | Bytes | Δ da blank_80x80 (1.659.493 B) | Ingombro (quadretti, da `default_size`) |
|---|---|---|---|
| `building_m4_tavern.dungeondraft_map` | 3.462.154 | 1.802.661 | 18×14 = 252 |
| `building_m4_warehouse.dungeondraft_map` | 3.429.611 | 1.770.118 | 22×14 = 308 |
| `building_m4_manor.dungeondraft_map` | 5.278.946 | 3.619.453 | 22×18 = 396 |

Media: ≈2.397.411 B ed ≈319 quadretti per edificio a piena risoluzione
(muri multi-piano, arredo, tetto, porte).

**Regime "città" (astratto, 1 quadretto = 1 edificio):** nessun generatore
esiste, quindi è stato scritto `scripts/city_scale_spike.py` (codice di
spike, stesso schema di `scripts/cave_spike.py`: non tocca `src/ddforge/`).
Griglia di edifici astratti — un solo `add_pattern` per quadretto, nessun
muro/oggetto — con una via di rispetto ogni 7 quadretti, sullo stesso canvas
80×80. Risultato reale: `generated/city_scale_spike.dungeondraft_map`,
4225 edifici piazzati, 3.618.623 B totali (Δ 1.959.130 B, ≈464 B/edificio),
`ddforge validate` pulito (0 problemi).

**Estrapolazione** (formula lineare già verificata per `terrain.splat`
/`tiles.cells`, SPEC.md §2, applicata al costo per edificio appena misurato,
non a un nuovo formato ipotetico): rappresentare la STESSA città di 4225
edifici in regime quartiere richiederebbe un canvas di ≈4225×319 ≈1.347.775
quadretti (lato ≈1161, contro l'80×80 disponibile) e produrrebbe
≈4225×2.397.411 B ≈9,4 GB di soli elementi disegnabili, più ≈333 MB di blob
base — dell'ordine dei **10 GB**, contro i 3,6 MB dello stesso contenuto in
regime città. Anche una città molto più piccola (50 edifici) pesherebbe
≈120 MB a piena risoluzione contro ≈23 KB astratta.

**Tempi di apertura:** non è possibile pilotare Dungeondraft da questa
macchina per misurarli in modo automatico (accertato in TASK-31). Come prova
indiretta: i tre file "quartiere" sopra (1,8–5,3 MB) e `dungeon_m3.dungeondraft_map`
(1,8 MB) sono già stati aperti da Jay ai gate umani M3/M4 (TASK-26, TASK-30)
senza lentezza riportata — e la fascia di dimensione del file città-scala
(3,6 MB) rientra comodamente in quella già verificata. **Confermato anche
direttamente**: Jay ha aperto `generated/city_scale_spike.dungeondraft_map`
(4225 pattern astratti, una struttura molto diversa da poche decine di muri)
e riporta che si carica bene, senza lentezza.

## Decision

**Il generatore cittadino supporta un parametro `--scale` con due preset,
non un solo regime fisso:**

- **`quartiere`** (default): 1 quadretto = 5 ft/1,5 m, lo stesso livello di
  dettaglio già usato da dungeon/building — isolati, lotti, edifici singoli
  a piena risoluzione, strade, piazze. Pensato per una porzione di città
  giocabile al tavolo, non per l'intera città.
- **`città`**: 1 quadretto = 1 edificio, rappresentazione astratta pensata
  per un'intera città o un quartiere esteso, a dimensione di file gestibile.

Motivazioni, in ordine di peso:

1. **Il regime quartiere non scala a "città intera".** L'estrapolazione
   sopra (≈10 GB per una città di 4225 edifici a piena risoluzione, contro
   ≈3,6 MB astratta) non è un'ipotesi: è un calcolo lineare su costi per
   edificio misurati su file reali già approvati da Jay. Un solo regime
   fisso a piena risoluzione renderebbe semplicemente impossibile lo scopo
   dichiarato in SPEC.md §1.4 ("quartieri e città") per qualunque città di
   dimensione realistica.
2. **Il regime città da solo non serve al tavolo.** Un edificio ridotto a un
   quadretto è una mappa di pianificazione/regione, non qualcosa su cui
   muovere miniature e descrivere stanze — motivo per cui SPEC.md §9.4
   chiama "quartiere" il livello giocabile.
3. **Entrambi i regimi sono già raggiungibili con l'unico template reale che
   abbiamo.** Non serve a Jay esportare un template più grande: il regime
   città sta comodamente nell'80×80 esistente (4225 edifici misurati, ne
   entrerebbero molti di più) perché `world.width/height` non cambia mai fra
   i regimi — cambia solo cosa ci si disegna sopra.
4. **TASK-41 esiste già e assume questa decisione.** È stato creato (2026-09-04)
   con la descrizione "la decisione presa è: supportare entrambi i regimi
   come preset selezionabili" e con l'implementazione dei due preset come
   suo scopo. Decidere qui un solo regime avrebbe reso TASK-41 privo di senso
   o avrebbe richiesto riaprire una decisione già presa altrove senza che
   fosse mai stata registrata formalmente: questa decisione la registra,
   non la cambia.

## Consequences

- **TASK-35** (`generators/city.py`) implementa il preset `quartiere`:
  rete stradale, isolati, lotti, un edificio per lotto via `building.py`,
  piazze — esattamente come da SPEC.md §9.4, senza vincoli aggiuntivi da
  questa decisione.
- **TASK-41** implementa il parametro `--scale`/preset `città` come
  generatore di secondo tipo (probabilmente non basato su `building.py` per
  edificio, che sarebbe incoerente con "1 quadretto = 1 edificio": serve una
  rappresentazione astratta — pattern e/o oggetto singolo per edificio, non
  ancora progettata nel dettaglio). `scripts/city_scale_spike.py` è un punto
  di partenza per la misura, **non** il generatore: usa solo `add_pattern`
  senza semantica di stanze/strade/piazze, e non va promosso a produzione
  senza passare dal disegno che SPEC.md §9.4 chiede anche per questo regime
  (isolati, strade, eventualmente edifici notevoli).
- **TASK-41** chiude anche la parte di misurazione ancora aperta da questa
  decisione: un riscontro diretto di Jay sui tempi di apertura (qui solo
  indiretto, per fascia di dimensione) e la documentazione della differenza
  fra i due preset in README e skill (AC5 di TASK-41).
- Nessuna modifica a `src/ddforge/`: `generators/city.py` resta
  `NotImplementedError`. `scripts/city_scale_spike.py` resta codice di spike
  in `scripts/`, come `cave_spike.py`.
- Il file generato dallo spike, `generated/city_scale_spike.dungeondraft_map`,
  è in `generated/` (gitignored) e rigenerabile con
  `python scripts/city_scale_spike.py`.

