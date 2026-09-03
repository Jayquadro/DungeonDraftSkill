---
id: TASK-18
title: compose.py — draw_room e draw_corridor
status: To Do
assignee: []
created_date: '2026-09-03 11:31'
labels: []
milestone: m-3
dependencies:
  - TASK-10
  - TASK-9
  - TASK-17
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Primo livello di composti sopra le primitive (SPEC.md §6.6): draw_room disegna pavimento, muri perimetrali, porte e luci di una Room e restituisce un dict con le chiavi walls, pattern e portals; draw_corridor disegna un corridoio come stanza stretta senza porte alle estremità. Deve rispettare la calibrazione delle porte fissata nel gate umano di M1.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 draw_room produce un perimetro chiuso, un pavimento coerente con la Palette e le porte richieste dalla Room
- [ ] #2 draw_room restituisce il dict con walls, pattern e portals come da SPEC.md §6.6
- [ ] #3 draw_corridor non mette porte alle estremità del corridoio
- [ ] #4 Il documento risultante passa validate() senza errori
- [ ] #5 Test unitari su rettangoli noti verificano coordinate e conteggio degli elementi generati
<!-- AC:END -->
