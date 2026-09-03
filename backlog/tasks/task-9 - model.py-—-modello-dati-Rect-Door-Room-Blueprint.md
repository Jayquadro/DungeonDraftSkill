---
id: TASK-9
title: 'model.py — modello dati Rect, Door, Room, Blueprint'
status: To Do
assignee: []
created_date: '2026-09-03 11:27'
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
- [ ] #1 Rect e frozen, espone w, h, center(), overlaps(other, margin) e shrink(n) con semantica x2/y2 esclusivi
- [ ] #2 overlaps con margin > 0 rileva anche i rettangoli troppo vicini, non solo quelli sovrapposti
- [ ] #3 Door, Room e Blueprint sono definiti con i campi e i default di SPEC.md §6.4
- [ ] #4 Blueprint non contiene stringhe Godot ne path res://
- [ ] #5 tests coprono Rect (w, h, center, overlaps con e senza margine, shrink) ed e verde
<!-- AC:END -->
