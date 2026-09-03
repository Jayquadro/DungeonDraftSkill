---
id: TASK-7
title: ids.py — allocazione dei node_id
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:26'
updated_date: '2026-09-03 14:33'
labels: []
milestone: m-1
dependencies:
  - TASK-1
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
I node_id sono stringhe esadecimali univoche in TUTTO il file, porte comprese. world.next_node_id deve essere maggiore di ogni id usato: se non lo e, Dungeondraft riassegna id duplicati alla prima modifica e corrompe la mappa (SPEC.md §6.2, §14). Serve la classe IdAllocator con next(), la proprieta next_free e il costruttore alternativo from_document() che parte dal massimo id gia presente nel template, necessario quando il template non e vuoto.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 IdAllocator(start=0x1000).next() restituisce id esadecimali in formato stringa, es. '1001'
- [x] #2 10.000 chiamate consecutive a next() producono 10.000 id distinti
- [x] #3 next_free e sempre strettamente maggiore dell'ultimo id emesso
- [x] #4 from_document(doc) inizializza l'allocatore dal massimo node_id presente nel documento, incluse le porte annidate nei muri
- [x] #5 tests/test_ids.py copre i casi sopra ed e verde
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementare IdAllocator (start default 0x1000, next() incrementa e restituisce hex, next_free = hex(n+1) sempre maggiore dell'ultimo emesso, from_document scansiona ricorsivamente tutti i node_id nel documento incluse le porte annidate nei muri e nel level.portals di primo livello). Test: 10000 next() distinti, next_free sempre maggiore, from_document su un documento reale (rich_reference).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato IdAllocator con scanner ricorsivo generico (_iter_node_ids) che trova qualunque chiave 'node_id' ovunque nel documento, incluse le porte annidate nei muri e l'eventuale level.portals di primo livello (schema libero scoperto in TASK-2) — robusto a entrambe le varianti senza bisogno di conoscerle esplicitamente. 7 test: 10000 id distinti, next_free sempre maggiore, from_document su documento sintetico e su rich_reference.dungeondraft_map reale (conferma che il max id trovato e coerente con world.next_node_id dichiarato dal file).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato IdAllocator (godot.py-style, base SPEC.md §12) con scanner ricorsivo che trova ogni node_id ovunque nel documento, robusto anche allo schema di portal libero scoperto in TASK-2. 7 test verdi, incluso from_document su rich_reference.dungeondraft_map reale.
<!-- SECTION:FINAL_SUMMARY:END -->
