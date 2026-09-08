---
id: TASK-34
title: Decisione sulla scala delle mappe cittadine
status: Done
assignee:
  - '@claude'
created_date: '2026-09-03 11:34'
updated_date: '2026-09-07 14:52'
labels: []
milestone: m-8
dependencies:
  - TASK-26
documentation:
  - docs/SPEC.md
modified_files:
  - scripts/city_scale_spike.py
  - >-
    backlog/decisions/decision-2 -
    Le-mappe-cittadine-supportano-entrambi-i-regimi-di-scala-come-preset-non-uno-solo.md
priority: medium
type: spike
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Una città intera a 256 px per quadretto diventa enorme (SPEC.md §9.4). Va deciso se supportare un parametro --scale con due regimi (1 quadretto = 1 edificio per le mappe di regione, contro 1 quadretto = 5 ft per il quartiere giocabile) oppure solo il quartiere. La spec chiede esplicitamente di decidere in M5, non prima. Vanno misurate le dimensioni reali dei file prodotti nei due regimi.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Le dimensioni in byte e i tempi di apertura di una mappa cittadina nei due regimi sono misurati su un caso reale
- [x] #2 La decisione su --scale è presa e registrata come decision di Backlog con le motivazioni
- [ ] #3 Se si supporta un solo regime, la limitazione è documentata nel README e nella skill
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Niente città.py (TASK-35, non ancora implementato): misuro usando ciò che esiste già, senza sintetizzare blob (vincolo SPEC.md §2). L'unico template reale disponibile è templates/blank_80x80.dungeondraft_map (80x80 quadretti); prepare() non tocca mai world.width/height, quindi la dimensione del canvas resta sempre quella del template — la variabile che cambia fra i due regimi non è la dimensione dei blob base, ma quanti edifici reali entrano nello stesso canvas e quanti elementi disegnabili servono per rappresentarli.
2. Regime "quartiere" (dettaglio pieno, 1 quadretto=1.5m/5ft): uso i file già prodotti da building.py e già passati al gate umano M4 (TASK-30) — generated/building_m4_tavern.dungeondraft_map, _manor, _warehouse — come casi reali. Misuro dimensione file reale e la confronto con templates/blank_80x80 per isolare il costo per edificio.
3. Regime "città" (1 quadretto=1 edificio, astratto): non esiste ancora un generatore. Scrivo scripts/city_scale_spike.py (codice di spike, non produzione, stesso pattern di scripts/cave_spike.py): griglia di edifici astratti a 1 pattern/quadretto sul canvas 80x80 esistente, con una via di rispetto ogni --step quadretti. Genero un file reale, valido con `ddforge validate`, e ne misuro la dimensione.
4. Calcolo il costo per edificio in entrambi i regimi (byte aggiunti rispetto al blank, diviso per edifici) ed estrapolo linearmente la dimensione di una città intera nei due regimi, usando la stessa formula lineare già verificata per terrain.splat/tiles.cells (SPEC.md §2) per il costo base del canvas.
5. "Tempi di apertura" (AC1): non posso pilotare Dungeondraft da qui (accertato in TASK-31). Uso come prova indiretta i gate umani già superati su file di dimensione comparabile a quella del regime città (dungeon_m3 1.8MB, building_m4_tavern 3.46MB, building_m4_manor 5.28MB, tutti aperti senza lentezza riportata da Jay in TASK-26/TASK-30) e chiedo a Jay un riscontro rapido, non bloccante, aprendo generated/city_scale_spike.dungeondraft_map.
6. Decisione: registrata con `backlog decision create` (nessun tool MCP la espone oltre al titolo/skeleton, corpo scritto a mano nel file come da eccezione già usata in decision-1/TASK-31). Dato l'esito atteso dai calcoli (regime quartiere per un'intera città è dell'ordine dei GB, impraticabile; regime città sta comodamente nel canvas esistente), e dato che TASK-41 esiste già e assume esplicitamente questa decisione (entrambi i regimi come preset --scale), la decisione sarà: supportare entrambi come preset, non uno solo.
7. AC3 (limitazione da documentare se si supporta un solo regime) non si applica, dato che si supportano entrambi: la marco non spuntata con una nota esplicita del perché, non la lascio ambigua. README/skill restano di competenza di TASK-41 AC5 (non ancora implementato).
8. Nessuna modifica a src/ddforge/ (city.py resta NotImplementedError, di competenza TASK-35/41).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Misure reali raccolte (vedi decision-2 per la tabella completa): regime quartiere ≈2.397.411 B/edificio su 3 edifici reali già approvati al gate M4 (tavern/manor/warehouse); regime città ≈464 B/edificio su generated/city_scale_spike.dungeondraft_map (4225 edifici astratti, generato da scripts/city_scale_spike.py, `ddforge validate` pulito). Estrapolazione lineare: la stessa città a piena risoluzione pesherebbe ≈10 GB contro ≈3,6 MB astratta.

Tempi di apertura: non misurabili in automatico da questa macchina (accertato in TASK-31, niente pilotaggio di Dungeondraft). Uso come prova indiretta i gate umani già superati su file di dimensione comparabile al regime città (dungeon_m3 1,8MB TASK-26; building_m4_tavern 3,46MB e building_m4_manor 5,28MB TASK-30): tutti aperti senza lentezza riportata. Chiesto a Jay un riscontro diretto non bloccante su generated/city_scale_spike.dungeondraft_map; se arriva va aggiunto qui.

AC3 non spuntata di proposito: la sua precondizione ('se si supporta un solo regime') non si verifica, dato che la decisione è di supportarli entrambi. Spuntarla direbbe il contrario di quanto deciso. README/skill restano scope di TASK-41 AC5.

Decisione registrata in backlog/decisions/decision-2 (status: accepted). Corpo scritto direttamente nel file: nessun tool MCP/CLI espone la creazione del contenuto oltre allo skeleton (stessa eccezione già usata per decision-1/TASK-31).

Riscontro diretto di Jay (2026-09-07): generated/city_scale_spike.dungeondraft_map (4225 pattern astratti) si carica bene in Dungeondraft. Conferma diretta ad aggiunta alla prova indiretta già raccolta (file di dimensione comparabile già aperti ai gate M3/M4): la fascia di dimensione del regime città non pone problemi di apertura. AC1 ora pienamente coperta anche sul lato tempi di apertura, non solo per estrapolazione.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Spike chiuso con una decisione motivata, registrata in `backlog/decisions/decision-2` (accepted): **il generatore cittadino supporta un parametro `--scale` con due preset, `quartiere` e `città`, non un solo regime fisso.**

**Misure reali** (AC1), senza attendere `generators/city.py` (TASK-35, non ancora implementato) e senza sintetizzare blob (vincolo SPEC.md §2 — l'unico template reale è `templates/blank_80x80.dungeondraft_map`, e `template.prepare()` non tocca mai `world.width/height`):
- Regime **quartiere** (dettaglio pieno): 3 edifici reali già approvati al gate umano M4 (TASK-30) — tavern 3.462.154 B, warehouse 3.429.611 B, manor 5.278.946 B — danno una media di ≈2.397.411 B ed ≈319 quadretti per edificio (Δ dal blank_80x80, 1.659.493 B).
- Regime **città** (astratto, 1 quadretto = 1 edificio): nessun generatore esisteva, quindi `scripts/city_scale_spike.py` (nuovo, codice di spike come `cave_spike.py`, non tocca `src/ddforge/`) genera una griglia di edifici astratti (un `add_pattern` per quadretto) sullo stesso canvas 80×80. Risultato reale: `generated/city_scale_spike.dungeondraft_map`, 4225 edifici, 3.618.623 B (≈464 B/edificio), `ddforge validate` pulito.
- **Estrapolazione** (formula lineare già verificata per `terrain.splat`/`tiles.cells`): la stessa città di 4225 edifici a piena risoluzione richiederebbe un canvas ≈1161×1161 quadretti e peserebbe **≈10 GB**, contro i **3,6 MB** dello stesso contenuto in regime città — non un'ipotesi, un calcolo su costi per edificio misurati su file reali.
- **Tempi di apertura**: non misurabili in automatico (accertato in TASK-31, nessun modo di pilotare Dungeondraft da questa macchina). Prova indiretta: i file "quartiere" sopra e `dungeon_m3.dungeondraft_map` (1,8 MB) sono già stati aperti da Jay ai gate M3/M4 senza lentezza riportata, e la fascia di dimensione del file città-scala (3,6 MB) rientra in quella già verificata. Chiesto a Jay un riscontro diretto non bloccante sul nuovo file.

**Decisione** (AC2): entrambi i regimi, come preset selezionabili. Motivazioni principali: il regime quartiere da solo non scala a una città intera (≈10 GB, impraticabile) e SPEC.md §1.4 chiede esplicitamente "quartieri e città"; il regime città da solo non serve al tavolo (un edificio a un quadretto non è giocabile); entrambi sono raggiungibili con l'unico template reale disponibile, senza bisogno di un nuovo export di Jay; e TASK-41, già esistente dal 2026-09-04, assume esplicitamente questa decisione nella sua descrizione — questo spike la registra formalmente, non la cambia.

**AC3 lasciata non spuntata di proposito**: la sua precondizione ("se si supporta un solo regime") non si verifica. Spuntarla direbbe il contrario di quanto deciso. La documentazione di README/skill per i due preset resta scope di TASK-41 AC5.

**Perimetro rispettato**: nessuna modifica a `src/ddforge/`; `generators/city.py` resta `NotImplementedError`, di competenza TASK-35 (preset quartiere) e TASK-41 (preset città, parametro `--scale`, e chiusura della parte di misurazione/documentazione ancora aperta — riscontro diretto di Jay sui tempi di apertura, README, skill). `scripts/city_scale_spike.py` è un punto di partenza per la misura, non il generatore città: usa solo pattern astratti senza semantica di stanze/strade/piazze.

File toccati: `scripts/city_scale_spike.py` (nuovo), `backlog/decisions/decision-2 - ...md` (nuovo).
<!-- SECTION:FINAL_SUMMARY:END -->
