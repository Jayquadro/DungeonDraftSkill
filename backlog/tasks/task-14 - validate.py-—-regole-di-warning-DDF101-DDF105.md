---
id: TASK-14
title: validate.py — regole di warning DDF101-DDF105
status: To Do
assignee: []
created_date: '2026-09-03 11:28'
labels: []
milestone: m-2
dependencies:
  - TASK-13
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Warning che non bloccano la generazione ma segnalano mappe probabilmente sbagliate al tavolo (SPEC.md §7): elementi fuori canvas, stanze irraggiungibili, muri e pattern degeneri, porte troppo vicine sullo stesso muro. Servono soprattutto ai generatori delle milestone successive come rete di sicurezza.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 DDF101 segnala elementi con coordinate fuori dal canvas width x height
- [ ] #2 DDF102 segnala stanze non raggiungibili dal grafo, cioe senza alcuna porta
- [ ] #3 DDF103 segnala muri con meno di 2 punti e DDF104 pattern con meno di 3 punti
- [ ] #4 DDF105 segnala due porte sullo stesso muro a distanza minore di 0.05
- [ ] #5 I warning sono distinguibili dagli errori tramite il campo severity
<!-- AC:END -->
