---
id: TASK-36
title: 'CLI, test e gate umano per gli stili cave e city'
status: To Do
assignee: []
created_date: '2026-09-03 11:35'
labels: []
milestone: m-5
dependencies:
  - TASK-33
  - TASK-35
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Chiusura di M5 (SPEC.md §5): ddforge generate cave e ddforge generate city devono produrre file validati che Jay apre correttamente in Dungeondraft. Include test di integrazione e golden file per entrambi gli stili.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ddforge generate cave e ddforge generate city funzionano con validazione obbligatoria pre-scrittura
- [ ] #2 Esistono test di integrazione e golden file per entrambi gli stili
- [ ] #3 Jay apre entrambi i file in Dungeondraft e conferma che sono utilizzabili al tavolo
- [ ] #4 Ogni difetto segnalato è riprodotto in un test prima della correzione
<!-- AC:END -->
