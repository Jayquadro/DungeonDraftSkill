---
id: TASK-6
title: godot.py — serializzazione dei tipi Godot
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
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Dungeondraft salva i tipi Godot come stringhe. Questo modulo deve essere l'UNICO posto del progetto che le costruisce (SPEC.md §6.1). Funzioni: v2, pv2, parse_pv2, argb, grid_to_px, con GRID = 256 px per quadretto (5 ft). Regole invariabili: spazi obbligatori dopo la parentesi aperta e prima della chiusa; colori sempre a 8 cifre esadecimali ARGB con alpha per primo; rotazioni in radianti; world.width/height in quadretti mentre tutte le coordinate dentro gli elementi sono in pixel. Le coordinate in pv2 sono appiattite in una sola stringa, non raggruppate. Base di partenza gia verificata contro una mappa reale in SPEC.md §12.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 v2(256, 512) restituisce esattamente 'Vector2( 256, 512 )' con gli spazi interni
- [ ] #2 pv2 appiattisce le coppie in una singola PoolVector2Array senza raggruppamenti
- [ ] #3 Il round-trip pv2 -> parse_pv2 -> pv2 e idempotente su punti arbitrari
- [ ] #4 argb('aabbcc') restituisce 'ffaabbcc' e argb accetta un alpha esplicito
- [ ] #5 argb rifiuta input gia a 8 cifre e qualunque lunghezza diversa da 6 con un errore esplicito
- [ ] #6 grid_to_px converte quadretti in pixel usando GRID = 256
- [ ] #7 tests/test_godot.py copre tutti i casi sopra ed e verde
<!-- AC:END -->
