---
id: TASK-23
title: furnish — arredo trasversale con densità configurabile
status: To Do
assignee: []
created_date: '2026-09-03 11:32'
labels: []
milestone: m-3
dependencies:
  - TASK-22
  - TASK-17
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modulo trasversale applicato dopo la geometria e condiviso da tutti i generatori (SPEC.md §9.5): furnish(level, ids, blueprint, palette, density, rng). Regole: gli oggetti non toccano i muri (margine 0.5 quadretti); non ostruiscono le porte (raggio libero di 1.5 quadretti davanti a ogni porta); rispettano il kind della stanza; densità light/medium/heavy corrispondono a circa 0.05/0.12/0.25 oggetti per quadretto.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 density accetta none, light, medium e heavy, e la densità risultante rispetta i valori indicati entro una tolleranza ragionevole
- [ ] #2 Nessun oggetto è piazzato a meno di 0.5 quadretti da un muro
- [ ] #3 Nessun oggetto cade entro 1.5 quadretti davanti a una porta
- [ ] #4 L'arredo dipende dal kind della stanza: una sala boss non è arredata come un corridoio o un locale di servizio
- [ ] #5 I nodi tattici ricevono coperture (colonne, casse) ogni 3-4 quadretti
- [ ] #6 L'arredo è riproducibile a parità di seed
<!-- AC:END -->
