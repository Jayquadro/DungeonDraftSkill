---
id: TASK-71
title: Abbellimento delle mappe cave e sewer
status: To Do
assignee: []
created_date: '2026-10-04 17:31'
updated_date: '2026-10-04 18:39'
labels: []
milestone: m-10
dependencies:
  - TASK-69
  - TASK-67
references:
  - src/ddforge/generators/cave.py
  - src/ddforge/generators/sewer.py
  - src/ddforge/cave_bitmap.py
documentation:
  - docs/SPEC-decorate.md
  - docs/format.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Estende `ddforge decorate` (core in TASK-69) a grotte e fognature, che non hanno stanze rettangolari. Vedi docs/SPEC-decorate.md §5 e §6.5.

Grotte: le zone si ricavano dal `cave_grid` del Blueprint (componenti connesse divise in sale `ampia`, strozzature `stretta`, vicoli `cieca`, id `g*`). Il pavimento e il layer cave nativo: per decisione di Jay (SPEC-decorate §14 D6) decorate ne cambia la texture secondo il tema, usando la funzione e le texture ammesse trovate dallo spike TASK-67; in piu usa terreno, oggetti (rocce, funghi, radici, ossa...) e acqua. Fognature: zone canali `k*` e camere di giunzione `j*`; l'acqua dei canali esiste gia, decorate aggiunge pozzanghere solo nelle camere. La forma della grotta (`cave.bitmap`) e l'acqua esistente non devono cambiare.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Le zone di una grotta sono derivate dal cave_grid con id stabili e ruoli ampia/stretta/cieca (test)
- [ ] #2 Nessun oggetto ingombro nelle strozzature larghe meno di 2 quadretti (test)
- [ ] #3 Gli oggetti di una grotta cadono tutti dentro l'area scavata (test su 30 seed)
- [ ] #4 `cave.bitmap`, `cave.entrance_bitmap` e l'acqua preesistente del file prodotto sono identici all'ingresso (test)
- [ ] #5 Nelle fognature le pozzanghere aggiunte stanno solo nelle camere di giunzione e non si sovrappongono ai canali (test)
- [ ] #6 Dry-run e applicazione funzionano per entrambi i tipi con tutti e sei i temi
- [ ] #7 Il pavimento della grotta cambia texture secondo il tema, e `--no-textures` lo lascia invariato (test)
<!-- AC:END -->
