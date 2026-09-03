---
id: TASK-22
title: >-
  Semantica D&D del dungeon: stanza boss, nodi tattici, corridoi bui, porte
  segrete
status: To Do
assignee: []
created_date: '2026-09-03 11:32'
labels: []
milestone: m-3
dependencies:
  - TASK-21
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
La parte che fa la differenza fra una planimetria e una mappa giocabile al tavolo (SPEC.md §9.1). La stanza più lontana dall'ingresso nel grafo diventa kind boss e riceve dimensione maggiorata; le stanze con grado maggiore o uguale a 3 sono nodi tattici e vanno segnalate perché furnish ci metta coperture; un corridoio più lungo di 12 quadretti (60 ft) supera la scurovisione di molte specie e va segnalato come proprietà del Blueprint perché furnish ci metta una fonte di luce a metà; le porte segrete vanno su stanze di grado 1 raggiungibili anche da altrove.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 La stanza più lontana dall'ingresso nel grafo riceve kind boss e dimensione maggiorata
- [ ] #2 Le stanze con grado maggiore o uguale a 3 sono marcate come nodi tattici nel Blueprint
- [ ] #3 I corridoi più lunghi di 12 quadretti sono segnalati come proprietà del Blueprint
- [ ] #4 Le porte segrete sono collocate solo su stanze di grado 1 raggiungibili anche per altra via
- [ ] #5 I test verificano ciascuna regola su seed fissi
<!-- AC:END -->
