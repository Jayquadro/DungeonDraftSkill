---
id: TASK-74
title: 'Gate umano dell''abbellimento: 5 tipi di mappa x 6 temi in Dungeondraft'
status: To Do
assignee: []
created_date: '2026-10-04 17:31'
updated_date: '2026-10-04 18:39'
labels: []
milestone: m-10
dependencies:
  - TASK-70
  - TASK-71
  - TASK-72
  - TASK-73
  - TASK-75
documentation:
  - docs/SPEC-decorate.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Come i gate di M1/M3/M4: Jay apre in Dungeondraft le mappe abbellite e conferma che funzionano e sono belle. Il preview PNG (esteso con luci e terreno in TASK-75) resta un'approssimazione senza ombre ne illuminazione vera, quindi questa verifica non e sostituibile. Vedi docs/SPEC-decorate.md §11.

Si preparano almeno 30 file (dungeon, building, cave, sewer, city × abbandonato, abitato, lugubre, naturale, arcano, festivo), ciascuno con l'originale e il preview prima/dopo accanto. I difetti trovati diventano task figli di questo, e i valori tarati (densita, soglie, colori) tornano nelle tabelle dei temi. Non si impone alcun limite di dimensione ai file (decisione di Jay): si misurano soltanto.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Tutti i file del gate si aprono in Dungeondraft senza errori
- [ ] #2 Jay conferma che geometria, porte e arredo originale sono invariati rispetto all'originale
- [ ] #3 Jay conferma che nessun oggetto aggiunto blocca una porta o un corridoio
- [ ] #4 Jay riconosce il tema di ogni file senza sapere quale fosse
- [ ] #5 La scala degli oggetti aggiunti e credibile a ogni preset cittadino
- [ ] #6 I tempi di apertura delle citta `citta` abbellite sono misurati e riportati
- [ ] #7 Jay conferma che il preview prima/dopo rende riconoscibile l'abbellimento senza aprire Dungeondraft
<!-- AC:END -->
