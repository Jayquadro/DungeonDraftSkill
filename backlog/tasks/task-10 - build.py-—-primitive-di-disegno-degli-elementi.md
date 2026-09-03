---
id: TASK-10
title: build.py — primitive di disegno degli elementi
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:27'
updated_date: '2026-09-03 14:39'
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
- [x] #1 add_wall accetta punti in quadretti, li converte in pixel e produce un muro conforme allo schema di SPEC.md §13
- [x] #2 Con loop=True il primo punto non e ripetuto in coda: o loop o punto ripetuto, mai entrambi
- [x] #3 add_portal aggiunge la porta dentro wall['portals'], imposta wall_id = wall['node_id'] e wall_distance = t, e non spezza il muro
- [x] #4 add_path imposta position = primo punto ed edit_points relativi a position, con il primo edit_point a (0, 0)
- [x] #5 add_roof scrive in level['roofs']['roofs']
- [x] #6 add_light e add_text seguono lo schema documentato in docs/format.md e non campi inventati
- [x] #7 Tutti gli elementi creati ricevono un node_id dall'IdAllocator e nessun id e duplicato
- [x] #8 tests/test_build.py copre ogni primitiva ed e verde
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementare le 9 primitive con conversione quadretti->pixel via godot.grid_to_px/v2/pv2 e node_id via IdAllocator. add_wall: validazione difensiva che rifiuta loop=True con punto di chiusura ripetuto (trappola SPEC.md §14). add_portal: calcola position interpolando lungo la polilinea del muro alla frazione t (helper _point_along_polyline, generalizza a muri con piu di 2 punti), valida t in [0,1], aggiunge 'locked' solo se True (coerente con l'ipotesi documentata in docs/format.md §5). add_pattern delega a add_polygon_pattern sui 4 vertici del rettangolo. add_object/add_path/add_roof come da SPEC.md §6.5, path con edit_points relativi a position. add_light/add_text seguono la variante A (piu comune, 82 campioni reali) documentata in docs/format.md §4, con rotation/texture opzionali per la variante con sprite. Test in tests/test_build.py per ogni primitiva, unicita dei node_id, round-trip via godot.parse_pv2 per verificare le coordinate scritte.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementate tutte e 9 le primitive. add_portal calcola position interpolando lungo la polilinea del muro (helper _point_along_polyline, generalizza a muri con piu di 2 punti) invece di richiedere x,y espliciti: direction/rotation restano parametri del chiamante, non calcolati qui, perche il segno corretto va calibrato nel gate umano di M1 (TASK-12) — build.py resta meccanico. add_portal valida t in [0,1] e omette la chiave 'locked' quando False (coerente con l'ipotesi di docs/format.md §5). add_wall rifiuta esplicitamente loop=True con punto di chiusura ripetuto. add_light usa la variante puntiforme (82 campioni reali, colore a 6 cifre) come default, con rotation/texture opzionali per la variante sprite. 18 test in tests/test_build.py, inclusa verifica di unicita dei node_id su una scena con tutte le primitive insieme. Suite completa: 84 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementate tutte le primitive di build.py (add_wall, add_portal, add_pattern, add_polygon_pattern, add_object, add_path, add_roof, add_light, add_text). add_portal interpola la posizione lungo il muro per la frazione t, lasciando direction/rotation al chiamante in attesa della calibrazione del gate umano M1. 18 test nuovi, suite completa 84 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
