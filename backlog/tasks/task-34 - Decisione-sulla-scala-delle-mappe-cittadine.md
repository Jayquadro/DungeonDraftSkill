---
id: TASK-34
title: Decisione sulla scala delle mappe cittadine
status: To Do
assignee: []
created_date: '2026-09-03 11:34'
updated_date: '2026-09-04 07:23'
labels: []
milestone: m-8
dependencies:
  - TASK-26
documentation:
  - docs/SPEC.md
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
- [ ] #1 Le dimensioni in byte e i tempi di apertura di una mappa cittadina nei due regimi sono misurati su un caso reale
- [ ] #2 La decisione su --scale è presa e registrata come decision di Backlog con le motivazioni
- [ ] #3 Se si supporta un solo regime, la limitazione è documentata nel README e nella skill
<!-- AC:END -->
