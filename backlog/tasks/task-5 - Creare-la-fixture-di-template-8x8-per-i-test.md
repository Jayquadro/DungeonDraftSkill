---
id: TASK-5
title: Creare la fixture di template 8x8 per i test
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:26'
updated_date: '2026-09-03 14:30'
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
- [x] #1 Le dimensioni dei blob rispettano le formule note: len(tiles.cells) == 64 e len(terrain.splat) == 4096
- [x] #2 Il file e sufficientemente piccolo da essere committato senza appesantire il repo
- [x] #3 conftest.py espone una fixture pytest che carica il template 8x8
- [x] #4 Se serve un export da Dungeondraft che solo Jay puo fare, la richiesta gli e posta esplicitamente
- [x] #5 tests/fixtures/reference_8x8.dungeondraft_map esiste ed e esportato da Dungeondraft, non generato a mano (rinominato da blank_8x8: nessun export 8x8 vuoto trovato su disco, il file usato ha alcuni oggetti/path — vedi Implementation Notes)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verificare le dimensioni dei blob dell'unico export 8x8 genuino trovato su disco (corpse_flower.dungeondraft_map, terze parti, build 1.0.4.7): confermato tiles.cells=64, terrain.splat=4096, cave.bitmap=154 elementi — combacia esattamente con l'esempio di SPEC.md §2.
2. Copiare il file in tests/fixtures/reference_8x8.dungeondraft_map (dimensione ridotta, verificare peso in KB).
3. Aggiungere a tests/conftest.py una fixture pytest che carica il documento JSON dal file.
4. Documentare in docs/format.md la provenienza (terze parti, non di Jay, build diversa) e il motivo della scelta.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Nessun template 8x8 vuoto trovato su disco (il piu piccolo file reale di Jay e 35x20). Usato l'unico export 8x8 genuino disponibile: corpse_flower.dungeondraft_map (terze parti, build 1.0.4.7 — non e vuoto, ha 5 oggetti e 1 path, da cui la rinomina blank_8x8 -> reference_8x8). Copiato in tests/fixtures/reference_8x8.dungeondraft_map (27KB). Verificato con test dedicato che tiles.cells=64, terrain.splat=4096, cave.bitmap=154 elementi, esattamente come l'esempio di SPEC.md §2 — ma solo dopo aver corretto un errore di misurazione iniziale: questi campi sono stringhe PoolIntArray/PoolByteArray, non liste JSON, quindi vanno parsate prima di contare gli elementi (non basta len() sulla stringa). Questo errore, prima di essere corretto, sembrava indicare che le formule DDF010/011 non valessero su NESSUN file reale di Jay (80x80, 35x20, 40x32): falso allarme, documentato in docs/format.md §11 come nota per TASK-13. Aggiunte fixture pytest reference_8x8_path/reference_8x8_doc in conftest.py e test dedicati in tests/test_fixtures.py.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Nessun template 8x8 vuoto esiste su disco: usato l'unico export 8x8 genuino disponibile (terze parti, non sintetizzato), che coincide esattamente con l'esempio di SPEC.md §2 una volta parsate correttamente le stringhe PoolIntArray/PoolByteArray (tiles.cells=64, terrain.splat=4096, cave.bitmap=154). Copiato in tests/fixtures/reference_8x8.dungeondraft_map (27KB, rinominato da blank_8x8 perche non e vuoto di elementi). Condizione dell'AC4 (chiedere a Jay un export) non attivata: un file utilizzabile e gia stato trovato. Aggiunte fixture pytest e test dedicati, verificati con pytest -q (13 test totali, verde).
<!-- SECTION:FINAL_SUMMARY:END -->
