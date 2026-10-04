---
id: TASK-69
title: >-
  `ddforge decorate` end-to-end sulle mappe dungeon: zone, planner, dry-run,
  override, applicazione
status: To Do
assignee: []
created_date: '2026-10-04 17:30'
labels: []
milestone: m-10
dependencies:
  - TASK-66
  - TASK-68
references:
  - src/ddforge/cli.py
  - src/ddforge/compose.py
  - src/ddforge/build.py
  - src/ddforge/ids.py
  - src/ddforge/template.py
  - src/ddforge/validate.py
  - src/ddforge/generators/bsp.py
documentation:
  - docs/SPEC-decorate.md
  - docs/format.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Primo taglio verticale del comando di abbellimento, solo per mappe `dungeon` (le piu ricche di semantica: boss, snodi tattici, corridoi bui, porte segrete). Specifica completa in docs/SPEC-decorate.md §3, §5, §6, §7, §8.

Il comando carica una mappa ddforge e il suo sidecar `.ddforge.json` (prodotto da TASK-66), ricava le zone (stanze `r*`, corridoi `c*`, alias `boss`/`ingresso`), costruisce con una funzione pura un piano di abbellimento da tema + intensita + override + seed, e lo stampa (`--dry-run`, anche `--json`) oppure lo applica: sostituisce la `texture` di pavimenti e muri, aggiunge oggetti decal/ingombro e luci, imposta `ambient_light`, valida e scrive un file NUOVO con il suo sidecar.

Invarianti non negoziabili: nessun muro/porta/pattern/stanza spostato, aggiunto o rimosso (solo il campo `texture` cambia); oggetti e luci esistenti intatti; originale mai sovrascritto; solo asset del catalogo e pack del template; nessun JSON scritto a mano (si usano build.py, IdAllocator.from_document, template.finalize/save). Le regole tattiche di §6.4 (raggio di rispetto delle porte, soglia di ingombro 30%, corridoi da 1 liberi, porte raggiungibili, niente luci nei corridoi bui ne vicino alle porte segrete, centro della stanza boss libero) sono parte del task. Il terreno usa la funzione dello spike TASK-67 se disponibile; altrimenti il ripiego indicato da quello spike.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `ddforge decorate <mappa> --theme T [--intensity L] [--seed N] [--out F]` scrive un file nuovo; default di --out `<nome>.decorated.dungeondraft_map`
- [ ] #2 Errore esplicito, senza scrivere nulla, per: sidecar mancante, versione sidecar sconosciuta, hash della mappa diverso (salvo --allow-modified), mappa gia abbellita, --out uguale all'ingresso, id di zona inesistente
- [ ] #3 `--dry-run` stampa per ogni zona id, ruolo, texture prima/dopo, oggetti per categoria, luci e avvisi; `--json` lo stesso in JSON; il piano stampato e identico a quello applicato con gli stessi parametri (test)
- [ ] #4 Override `--zone ID=TEMA`, `--zone-intensity ID=LIV`, `--zone-skip ID`, `--add ID:ALIAS` e `--no-textures/--no-terrain/--no-objects/--no-lights` funzionano e sono coperti da test
- [ ] #5 Test di invarianza: a parte `texture`, muri, portali e pattern del file prodotto sono identici all'ingresso, e gli oggetti/luci di partenza sono tutti presenti invariati
- [ ] #6 Test di proprieta su 30 seed per tema: nessun oggetto nel raggio di rispetto di una porta, ingombro sotto soglia, corridoi larghi 1 senza ingombri, porte di ogni zona mutuamente raggiungibili, nessuna luce nei corridoi bui
- [ ] #7 Regole di validazione DDF201, DDF202, DDF203 implementate in validate.py con test
- [ ] #8 Stessi input e seed producono un file byte-identico
- [ ] #9 Il file prodotto passa `ddforge validate` senza errori e l'originale ha lo stesso hash di prima
- [ ] #10 `ddforge decorate --help` documenta tutte le opzioni
<!-- AC:END -->
