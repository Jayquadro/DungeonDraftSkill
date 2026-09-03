---
id: TASK-32
title: generators/cave.py — cellular automata e contorni
status: To Do
assignee: []
created_date: '2026-09-03 11:34'
labels: []
milestone: m-5
dependencies:
  - TASK-31
  - TASK-20
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generatore di grotte (SPEC.md §9.3): griglia width x height con ogni cella roccia con probabilità 0.45; 4-5 iterazioni in cui una cella diventa roccia se almeno 5 vicini su 8 sono roccia; etichettatura delle componenti connesse, si tiene la più grande e si scavano tunnel verso le altre sopra una certa dimensione; estrazione del contorno con marching squares per ottenere poligoni.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il generatore produce una caverna con una sola componente percorribile, dopo lo scavo dei tunnel
- [ ] #2 I contorni estratti con marching squares sono poligoni chiusi senza autointersezioni evidenti
- [ ] #3 Il risultato rispetta la decisione presa nello spike sul rendering
- [ ] #4 Il documento generato passa validate() senza errori
- [ ] #5 Lo stesso seed produce la stessa grotta
<!-- AC:END -->
