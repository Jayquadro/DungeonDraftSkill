---
id: TASK-21
title: 'generators/bsp.py — partizione, stanze e corridoi'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:32'
updated_date: '2026-09-04 06:39'
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
- [x] #1 Il generatore restituisce un Blueprint con rooms, corridors, graph, seed e style valorizzati
- [x] #2 Il numero di stanze prodotte si avvicina al target rooms richiesto
- [x] #3 Nessuna stanza si sovrappone a un'altra e nessuna esce dal canvas
- [x] #4 Il grafo delle stanze è sempre connesso
- [x] #5 Con loops=0.15 il grafo contiene almeno un ciclo su mappe di dimensione sufficiente
- [x] #6 Lo stesso seed produce lo stesso Blueprint
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
0. Refactor preliminare di compose.py: estrarre da connect() la parte puramente geometrica (nessun accesso a level/ids) in plan_connection(rect_a, rect_b) -> ConnectionPlan, che decide lato+t per il caso adiacente o lati+corridoi per il caso non adiacente. connect() diventa un consumatore sottile che disegna cio che plan_connection decide. Necessario perche il generatore BSP produce un Blueprint puro (nessun JSON, per SPEC.md 'generatore -> Blueprint -> compose -> build -> JSON') e deve decidere porte/corridoi PRIMA che qualunque muro esista, riusando la stessa geometria gia debuggata in TASK-19 invece di duplicarla. Verificare che tutti i test di TASK-19 restino verdi dopo il refactor.
1. Implementare l'albero BSP: nodo con rect, split lungo l'asse piu lungo a frazione casuale 35-65%, iterativo (non ricorsivo a profondita fissa) fino a raggiungere il target 'rooms' o esaurire le foglie divisibili (piu piccole di max_room*2) o depth_max come valvola di sicurezza.
2. Per ogni foglia, inscrivere una Room con margine casuale 0-2, clampata a min_room se il margine la rimpicciolisce troppo.
3. Risalendo l'albero, per ogni nodo interno collegare una stanza rappresentativa del sottoalbero sinistro con una del sottoalbero destro usando plan_connection: side/t vanno dentro Room.doors (Door coi campi wall_index/t), i corridoi (se presenti) vanno in Blueprint.corridors; costruire contestualmente blueprint.graph.
4. Collegamenti extra per gli anelli: round(loops * len(rooms)) coppie di stanze vicine (per distanza fra centri) non ancora connesse nel grafo, connesse allo stesso modo.
5. Test: Blueprint valorizzato, stesso seed -> stesso Blueprint, nessuna stanza fuori canvas o sovrapposta, grafo connesso (BFS/DFS da nodo 0 raggiunge tutti), con loops=0.15 il grafo ha almeno un ciclo su una mappa abbastanza grande, numero di stanze vicino al target.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Refactor preliminare di compose.py: estratta la geometria pura di connect() in plan_corridor(rect_a, rect_b, width) (gia esisteva _shared_wall_segment come funzione pura per il caso adiacente); connect() diventa un consumatore sottile. Tutti i test di TASK-19 restano verdi dopo il refactor, confermando che il comportamento e identico. Implementato l'albero BSP iterativo (non ricorsivo a profondita fissa): mantiene una lista di foglie divisibili e continua a dividere finche non raggiunge il target 'rooms' o esaurisce le foglie valide, con depth_max come valvola di sicurezza. Risalendo l'albero (_connect_subtree, post-order), ogni nodo interno collega una stanza rappresentativa di ciascun sottoalbero riusando _shared_wall_segment/plan_corridor, popolando Room.doors e Blueprint.corridors senza toccare nessun JSON. Durante la scrittura del test di integrazione end-to-end (render reale via draw_room) scoperto e corretto un bug reale nel generatore: due connessioni diverse della stessa stanza potevano atterrare esattamente sullo stesso t sullo stesso muro (violando DDF105) quando entrambe si proiettavano sul centro del lato — risolto con _non_colliding_t, che scosta la nuova porta se troppo vicina a una gia presente sullo stesso wall_index. 14 test in tests/test_bsp.py: Blueprint completo, riproducibilita, nessuna sovrapposizione/uscita canvas, connettivita del grafo su 20 seed, presenza di cicli con loops=0.15, assenza di cicli con loops=0, ogni stanza con almeno una porta su 30 seed, nessuna collisione DDF105 su 30 seed, un caso limite a 1 stanza, e un test di integrazione end-to-end che renderizza le sole stanze via draw_room e verifica zero errori/DDF102 con validate(). Documentata nel docstring del modulo la convenzione per renderizzare Blueprint.corridors (TASK-24): orientamento derivato da rect.w >= rect.h, ambiguo solo per segmenti quasi quadrati d'angolo dove non e comunque critico. Suite completa: 217 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato il generatore BSP (albero iterativo, stop a max_room*2 o depth_max, margine casuale 0-2 per stanza, connessione bottom-up con anelli extra). Refactor di compose.py per condividere la geometria pura con connect() (plan_corridor). Trovato e corretto un bug reale (collisione di porte sullo stesso muro, DDF105) durante il test di integrazione end-to-end. 14 test nuovi, suite completa 217 verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
