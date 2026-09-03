---
id: TASK-33
title: 'Variante fognature: canali ortogonali, camere di giunzione e acqua'
status: To Do
assignee: []
created_date: '2026-09-03 11:34'
labels: []
milestone: m-5
dependencies:
  - TASK-32
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Variante del generatore di grotte descritta in SPEC.md §9.3: griglia di canali ortogonali invece del cellular automata, camere di giunzione circolari, e uso del layer water. Serve la palette sewer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il generatore produce una rete di canali ortogonali connessa, con camere di giunzione circolari
- [ ] #2 Il layer water è popolato coerentemente con i canali
- [ ] #3 La palette sewer è usata per muri, pavimenti e porte
- [ ] #4 Il documento generato passa validate() senza errori
<!-- AC:END -->
