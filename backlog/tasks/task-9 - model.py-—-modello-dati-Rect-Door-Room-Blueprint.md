---
id: TASK-9
title: 'model.py — modello dati Rect, Door, Room, Blueprint'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:27'
updated_date: '2026-09-03 14:34'
labels: []
milestone: m-1
dependencies:
  - TASK-1
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Livello intermedio fra i generatori e la serializzazione: i generatori producono MODELLO, non JSON, cosi restano testabili senza toccare il formato. Il flusso e generatore -> Blueprint -> compose -> build -> JSON, e ogni freccia e testabile separatamente (SPEC.md §6.4). Rect e in coordinate-quadretto con x2/y2 esclusivi. Nessun path res:// e nessuna stringa Godot deve comparire in questo modulo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Rect e frozen, espone w, h, center(), overlaps(other, margin) e shrink(n) con semantica x2/y2 esclusivi
- [x] #2 overlaps con margin > 0 rileva anche i rettangoli troppo vicini, non solo quelli sovrapposti
- [x] #3 Door, Room e Blueprint sono definiti con i campi e i default di SPEC.md §6.4
- [x] #4 Blueprint non contiene stringhe Godot ne path res://
- [x] #5 tests coprono Rect (w, h, center, overlaps con e senza margine, shrink) ed e verde
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementare Rect (w,h,center,overlaps con margin,shrink) con semantica x2/y2 esclusivi come da SPEC.md §6.4. Door/Room/Blueprint gia definiti come dataclass nello stub, verificarli contro la spec. Test su Rect: w/h, center, overlaps senza e con margine (inclusi casi limite adiacenti), shrink.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementati w/h/center/overlaps/shrink su Rect con semantica x2/y2 esclusivi. overlaps(other, margin): due rettangoli si considerano troppo vicini solo se il gap fra loro e STRETTAMENTE minore di margin (gap==margin -> clearance sufficiente, non overlap) — scelta deliberata coerente con l'uso di margin come distanza minima richiesta fra stanze. 9 test in tests/test_model.py, incluso un caso limite che ha rivelato questa semantica (il test iniziale assumeva gap==margin gia overlap: corretto il test, non il codice, dopo aver verificato che l'interpretazione 'clearance esatta e sufficiente' e quella sensata per l'uso previsto in compose.connect/generators).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato Rect (w/h/center/overlaps/shrink, x2/y2 esclusivi) e verificati Door/Room/Blueprint gia definiti nello stub. 9 test verdi, inclusi i casi limite di overlaps con margine.
<!-- SECTION:FINAL_SUMMARY:END -->
