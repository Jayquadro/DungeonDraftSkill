---
id: TASK-25
title: Test di integrazione e golden file per il generatore BSP
status: To Do
assignee: []
created_date: '2026-09-03 11:32'
labels: []
milestone: m-3
dependencies:
  - TASK-24
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Piramide di test descritta in SPEC.md §10. Integrazione: carica il template di fixture, genera, valida; verifica che non ci siano errori di validazione, che tutte le stanze siano raggiungibili nel grafo e che nessuna stanza si sovrapponga. Golden file: per un seed fisso il documento generato viene confrontato con un riferimento in tests/fixtures/golden/, normalizzando creation_date, per intercettare regressioni silenziose nel formato. I golden vanno marcati slow così che pytest -m 'not slow' resti veloce.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Un test di integrazione genera un dungeon sulla fixture 8x8 e verifica zero Issue di severity error
- [ ] #2 Il test verifica che tutte le stanze siano raggiungibili nel grafo e che nessuna si sovrapponga
- [ ] #3 Esiste un golden file per un seed fisso, confrontato normalizzando creation_date
- [ ] #4 I test golden sono marcati slow e pytest -m 'not slow' li esclude
- [ ] #5 pytest -q è verde
<!-- AC:END -->
