---
id: TASK-21
title: 'generators/bsp.py — partizione, stanze e corridoi'
status: To Do
assignee: []
created_date: '2026-09-03 11:32'
labels: []
milestone: m-3
dependencies:
  - TASK-20
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generatore di dungeon a stanze per cripte, complessi sotterranei e prigioni: primo generatore in ordine di priorità (SPEC.md §1.4, §9.1). Algoritmo: rettangolo width x height meno un margine di 1 quadretto; tagli ricorsivi lungo l'asse più lungo in un punto casuale entro il 35-65%, fino a quando la partizione è più piccola di max_room*2 o si raggiunge depth_max; in ogni foglia si inscrive una stanza con margine casuale 0-2 quadretti; risalendo l'albero le due sorelle si collegano con un corridoio a L; infine il 10-20% di collegamenti extra fra stanze vicine crea anelli ed evita il dungeon-albero percorribile in un solo modo. Parametri: rooms (target), min_room=3, max_room=10, corridor_width 1 o 2, loops=0.15.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il generatore restituisce un Blueprint con rooms, corridors, graph, seed e style valorizzati
- [ ] #2 Il numero di stanze prodotte si avvicina al target rooms richiesto
- [ ] #3 Nessuna stanza si sovrappone a un'altra e nessuna esce dal canvas
- [ ] #4 Il grafo delle stanze è sempre connesso
- [ ] #5 Con loops=0.15 il grafo contiene almeno un ciclo su mappe di dimensione sufficiente
- [ ] #6 Lo stesso seed produce lo stesso Blueprint
<!-- AC:END -->
