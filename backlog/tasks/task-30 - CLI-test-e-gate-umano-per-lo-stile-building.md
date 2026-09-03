---
id: TASK-30
title: 'CLI, test e gate umano per lo stile building'
status: To Do
assignee: []
created_date: '2026-09-03 11:34'
labels: []
milestone: m-4
dependencies:
  - TASK-29
  - TASK-24
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Chiusura di M4 (SPEC.md §5): il comando ddforge generate building deve produrre un edificio multi-piano con tetti che Jay apre correttamente in Dungeondraft. Include test di integrazione e golden file come per il BSP.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ddforge generate building genera un edificio multi-piano con tetto, validato prima della scrittura
- [ ] #2 Il CLI espone i parametri specifici dell'edificio, inclusa la tipologia e il numero di piani
- [ ] #3 Esistono test di integrazione e un golden file per un seed fisso
- [ ] #4 Jay apre il file in Dungeondraft e conferma che i piani, le scale e il tetto sono corretti
- [ ] #5 Ogni difetto segnalato da Jay è riprodotto in un test prima della correzione
<!-- AC:END -->
