---
id: TASK-27
title: 'compose.draw_building — edificio multi-piano, scale e tetto'
status: To Do
assignee: []
created_date: '2026-09-03 11:34'
labels: []
milestone: m-4
dependencies:
  - TASK-19
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Composto multi-livello descritto in SPEC.md §6.6 e §9.2: distribuisce le stanze sui livelli, aggiunge il vano scale e il tetto sull'ultimo piano. Vincolo non negoziabile: le scale devono occupare lo stesso Rect su tutti i livelli, altrimenti la mappa non si legge al tavolo. Il tetto va scritto in level['roofs']['roofs'] con sun_direction coerente su tutto l'edificio.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 draw_building distribuisce le stanze su N livelli preparati da template.prepare
- [ ] #2 Il vano scale occupa lo stesso Rect su tutti i livelli, verificato da un test
- [ ] #3 Il tetto è aggiunto solo sull'ultimo livello, in level['roofs']['roofs'], con sun_direction coerente
- [ ] #4 I muri portanti usano una texture diversa da quelle dei tramezzi
- [ ] #5 Il documento multi-livello passa validate() senza errori
<!-- AC:END -->
