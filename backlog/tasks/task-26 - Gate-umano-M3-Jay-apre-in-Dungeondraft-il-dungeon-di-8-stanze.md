---
id: TASK-26
title: 'Gate umano M3: Jay apre in Dungeondraft il dungeon di 8 stanze'
status: To Do
assignee: []
created_date: '2026-09-03 11:32'
labels: []
milestone: m-3
dependencies:
  - TASK-25
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Secondo e ultimo passaggio manuale obbligatorio (SPEC.md §5). Genera un dungeon di 8 stanze validato, poi fermati e chiedi esplicitamente a Jay di aprirlo in Dungeondraft indicando cosa controllare. Le correzioni di orientamento e allineamento emerse qui vanno codificate, non solo documentate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A Jay è chiesto esplicitamente di verificare: tutte le stanze sono raggiungibili, le porte sono orientate bene, i pavimenti non sbordano
- [ ] #2 Jay conferma che la mappa è utilizzabile al tavolo senza ritocchi manuali di struttura
- [ ] #3 Ogni difetto segnalato è riprodotto in un test prima di essere corretto
- [ ] #4 Le regole di orientamento e allineamento definitive sono codificate e annotate in docs/format.md
<!-- AC:END -->
