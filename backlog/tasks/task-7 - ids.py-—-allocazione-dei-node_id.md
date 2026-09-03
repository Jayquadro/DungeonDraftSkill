---
id: TASK-7
title: ids.py — allocazione dei node_id
status: To Do
assignee: []
created_date: '2026-09-03 11:26'
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
- [ ] #1 IdAllocator(start=0x1000).next() restituisce id esadecimali in formato stringa, es. '1001'
- [ ] #2 10.000 chiamate consecutive a next() producono 10.000 id distinti
- [ ] #3 next_free e sempre strettamente maggiore dell'ultimo id emesso
- [ ] #4 from_document(doc) inizializza l'allocatore dal massimo node_id presente nel documento, incluse le porte annidate nei muri
- [ ] #5 tests/test_ids.py copre i casi sopra ed e verde
<!-- AC:END -->
