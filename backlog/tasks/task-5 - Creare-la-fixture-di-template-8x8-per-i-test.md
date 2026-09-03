---
id: TASK-5
title: Creare la fixture di template 8x8 per i test
status: To Do
assignee: []
created_date: '2026-09-03 11:26'
labels: []
milestone: m-0
dependencies:
  - TASK-2
documentation:
  - docs/SPEC.md
priority: medium
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
I test devono girare senza i template di produzione, che sono grossi e legati all'installazione di Jay (SPEC.md §10). Serve un template minimo 8x8 committato in tests/fixtures/, con blob binari della dimensione giusta (tiles.cells = 64, terrain.splat = 4096, cave.bitmap = 154 byte come osservato per 8x8) e un manifest pack ridotto ma reale. Va esportato da Dungeondraft, non sintetizzato: i blob binari sintetizzati sono la trappola numero uno del progetto (SPEC.md §2, §14).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 tests/fixtures/blank_8x8.dungeondraft_map esiste ed e esportato da Dungeondraft, non generato a mano
- [ ] #2 Le dimensioni dei blob rispettano le formule note: len(tiles.cells) == 64 e len(terrain.splat) == 4096
- [ ] #3 Il file e sufficientemente piccolo da essere committato senza appesantire il repo
- [ ] #4 conftest.py espone una fixture pytest che carica il template 8x8
- [ ] #5 Se serve un export da Dungeondraft che solo Jay puo fare, la richiesta gli e posta esplicitamente
<!-- AC:END -->
