---
id: TASK-10
title: build.py — primitive di disegno degli elementi
status: To Do
assignee: []
created_date: '2026-09-03 11:27'
labels: []
milestone: m-1
dependencies:
  - TASK-6
  - TASK-7
  - TASK-8
  - TASK-3
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ogni funzione aggiunge UN elemento a un livello e restituisce il dict creato, utile per attaccarci le porte (SPEC.md §6.5). Primitive: add_wall, add_portal, add_pattern, add_polygon_pattern, add_object, add_path, add_roof, add_light, add_text. Trappole da rispettare: le porte vanno annidate in wall['portals'], mai a livello mappa; con loop=True il primo punto NON va ripetuto in coda; path.edit_points sono RELATIVI a position (position = primo punto); i tetti vanno in level['roofs']['roofs'], non in una lista di primo livello. Gli input sono in quadretti e la conversione in pixel avviene dentro le primitive. add_light e add_text richiedono lo schema derivato in M0.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 add_wall accetta punti in quadretti, li converte in pixel e produce un muro conforme allo schema di SPEC.md §13
- [ ] #2 Con loop=True il primo punto non e ripetuto in coda: o loop o punto ripetuto, mai entrambi
- [ ] #3 add_portal aggiunge la porta dentro wall['portals'], imposta wall_id = wall['node_id'] e wall_distance = t, e non spezza il muro
- [ ] #4 add_path imposta position = primo punto ed edit_points relativi a position, con il primo edit_point a (0, 0)
- [ ] #5 add_roof scrive in level['roofs']['roofs']
- [ ] #6 add_light e add_text seguono lo schema documentato in docs/format.md e non campi inventati
- [ ] #7 Tutti gli elementi creati ricevono un node_id dall'IdAllocator e nessun id e duplicato
- [ ] #8 tests/test_build.py copre ogni primitiva ed e verde
<!-- AC:END -->
