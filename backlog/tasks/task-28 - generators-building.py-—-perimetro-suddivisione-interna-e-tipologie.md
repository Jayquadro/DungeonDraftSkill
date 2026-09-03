---
id: TASK-28
title: 'generators/building.py — perimetro, suddivisione interna e tipologie'
status: To Do
assignee: []
created_date: '2026-09-03 11:34'
labels: []
milestone: m-4
dependencies:
  - TASK-27
  - TASK-20
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generatore di edifici urbani, secondo in ordine di priorità (SPEC.md §1.4, §9.2): perimetro esterno rettangolare o a L; suddivisione interna ricorsiva con muri portanti; un vano scale allineato verticalmente su tutti i piani; distribuzione delle stanze per piano secondo la tipologia. Taverna: piano terra sala comune, cucina e retro, primo piano camere. Magione: terra rappresentanza, primo privato, sottotetto servitù. Magazzino: terra volume unico con soppalco.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il generatore produce perimetri sia rettangolari sia a L
- [ ] #2 Le tre tipologie taverna, magione e magazzino producono distribuzioni di stanze distinte e coerenti con la descrizione della spec
- [ ] #3 Ogni stanza è raggiungibile: nessun vano cieco senza porta
- [ ] #4 Il vano scale è presente e allineato su tutti i piani
- [ ] #5 Lo stesso seed produce lo stesso Blueprint
<!-- AC:END -->
