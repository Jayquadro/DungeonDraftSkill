---
id: TASK-16
title: 'CLI: comandi `ddforge validate` e `ddforge inspect`'
status: To Do
assignee: []
created_date: '2026-09-03 11:28'
labels: []
milestone: m-2
dependencies:
  - TASK-13
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Interfaccia a riga di comando per il validatore e per l'ispezione (SPEC.md §8): `ddforge validate <file>` stampa gli Issue e `ddforge inspect <file>` fa il dump della struttura e delle statistiche di una mappa. inspect e lo strumento di lavoro per capire i template reali e le mappe generate senza aprire Dungeondraft.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `ddforge validate <file>` stampa gli Issue in forma leggibile ed esce con codice 1 se ci sono errori, 0 se ci sono solo warning
- [ ] #2 `ddforge inspect <file>` stampa dimensioni mappa, format, creation_build, numero di livelli, conteggio elementi per tipo e pack referenziati
- [ ] #3 Entrambi i comandi gestiscono file inesistenti o JSON non valido con un messaggio chiaro invece di un traceback
- [ ] #4 I comandi sono coperti da test
<!-- AC:END -->
