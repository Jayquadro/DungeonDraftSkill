---
id: TASK-15
title: Fixture corrotte e test per ogni codice DDFxxx
status: To Do
assignee: []
created_date: '2026-09-03 11:28'
labels: []
milestone: m-2
dependencies:
  - TASK-13
  - TASK-14
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Criterio di completamento di M2 (SPEC.md §5, §7): per OGNI codice DDFxxx serve una fixture che lo viola e un test che verifica che validate() lo segnali. Le fixture si costruiscono corrompendo in modo mirato il template 8x8, un difetto per fixture, cosi il test isola una sola regola.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Esiste una fixture corrotta per ciascuno dei 15 codici di errore e dei 5 di warning
- [ ] #2 Per ogni codice esiste un test che verifica che validate() lo segnali con severity e path corretti
- [ ] #3 Un test verifica che il documento generato dallo script demo di M1 non produca alcun errore
- [ ] #4 Un test verifica che non ci siano falsi positivi: una fixture valida produce zero Issue di severity error
- [ ] #5 pytest -q e verde
<!-- AC:END -->
