---
id: TASK-6
title: godot.py — serializzazione dei tipi Godot
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:26'
updated_date: '2026-09-03 14:32'
labels: []
milestone: m-1
dependencies:
  - TASK-1
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Dungeondraft salva i tipi Godot come stringhe. Questo modulo deve essere l'UNICO posto del progetto che le costruisce (SPEC.md §6.1). Funzioni: v2, pv2, parse_pv2, argb, grid_to_px, con GRID = 256 px per quadretto (5 ft). Regole invariabili: spazi obbligatori dopo la parentesi aperta e prima della chiusa; colori sempre a 8 cifre esadecimali ARGB con alpha per primo; rotazioni in radianti; world.width/height in quadretti mentre tutte le coordinate dentro gli elementi sono in pixel. Le coordinate in pv2 sono appiattite in una sola stringa, non raggruppate. Base di partenza gia verificata contro una mappa reale in SPEC.md §12.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 v2(256, 512) restituisce esattamente 'Vector2( 256, 512 )' con gli spazi interni
- [x] #2 pv2 appiattisce le coppie in una singola PoolVector2Array senza raggruppamenti
- [x] #3 Il round-trip pv2 -> parse_pv2 -> pv2 e idempotente su punti arbitrari
- [x] #4 argb('aabbcc') restituisce 'ffaabbcc' e argb accetta un alpha esplicito
- [x] #5 argb rifiuta input gia a 8 cifre e qualunque lunghezza diversa da 6 con un errore esplicito
- [x] #6 grid_to_px converte quadretti in pixel usando GRID = 256
- [x] #7 tests/test_godot.py copre tutti i casi sopra ed e verde
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementare v2/pv2/parse_pv2/argb/grid_to_px in godot.py secondo SPEC.md §6.1 e §12. parse_pv2 tollerante a spazi. argb valida lunghezza esattamente 6 cifre esadecimali, alza ValueError altrimenti. Scrivere tests/test_godot.py con round-trip su punti con float, verificare formati esatti delle stringhe.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato v2/pv2/parse_pv2/argb/grid_to_px. parse_pv2 valida il formato con una regex prima di parsare, solleva ValueError su input invalido o numero dispari di coordinate. argb valida esattamente 6 cifre esadecimali (rifiuta 8 cifre e qualunque altra lunghezza). 19 test in tests/test_godot.py, incluso round-trip parametrico e verifica diretta contro i due muri reali di templates/rich_reference.dungeondraft_map (pv2(parse_pv2(x)) == x).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato godot.py completo (v2, pv2, parse_pv2, argb, grid_to_px) secondo SPEC.md §6.1. Verificato con 19 test (formati esatti, round-trip parametrico, validazione argb) piu una verifica manuale contro i muri reali di rich_reference.dungeondraft_map. pytest -q verde.
<!-- SECTION:FINAL_SUMMARY:END -->
