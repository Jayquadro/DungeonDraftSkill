---
id: TASK-22
title: >-
  Semantica D&D del dungeon: stanza boss, nodi tattici, corridoi bui, porte
  segrete
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:32'
updated_date: '2026-09-04 06:48'
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
- [x] #1 La stanza più lontana dall'ingresso nel grafo riceve kind boss e dimensione maggiorata
- [x] #2 Le stanze con grado maggiore o uguale a 3 sono marcate come nodi tattici nel Blueprint
- [x] #3 I corridoi più lunghi di 12 quadretti sono segnalati come proprietà del Blueprint
- [x] #4 Le porte segrete sono collocate solo su stanze di grado 1 raggiungibili anche per altra via
- [x] #5 I test verificano ciascuna regola su seed fissi
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Estendere Blueprint (model.py, TASK-9) con due campi opzionali retrocompatibili: tactical_rooms: list[int] e long_corridor_indices: list[int], default_factory=list, cosi il codice/i test esistenti non si rompono. Boss room: BFS delle distanze dal grafo a partire dalla stanza 0 (convenzione: l'ingresso e la prima stanza creata), stanza col massimo, pareggio spezzato per indice piu basso per riproducibilita; kind='boss'; ingrandimento tentato con margini decrescenti (3,2,1 quadretti) SOLO sui lati senza porte (i lati con porte non si toccano, altrimenti la posizione assoluta della porta si sposterebbe rispetto al corridoio/stanza collegata), clampato al canvas e verificato senza sovrapposizioni; se nessun margine funziona la stanza resta com'e. Nodi tattici: grado>=3 nel grafo COSI COM'E dopo l'albero+anelli, prima delle porte segrete (le scorciatoie segrete non devono contare come nodi tattici 'visibili'). Porte segrete: per ogni stanza di grado 1, collegarla alla stanza piu vicina non ancora connessa con una porta di kind='secret' su entrambi gli estremi (estende _connect_rooms con un parametro kind), aumentando il suo grado e rendendola raggiungibile anche da un percorso diverso da quello principale. Corridoi lunghi: dopo TUTTI i passaggi che possono aggiungere corridoi (incluse le porte segrete), scandire blueprint.corridors e segnalare gli indici con max(w,h) > 12. Ordine in generate(): albero+anelli (gia esistente) -> nodi tattici -> boss+ingrandimento -> porte segrete -> corridoi lunghi. Test su seed fissi per ciascuna regola.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Estesa Blueprint (model.py) con due campi opzionali retrocompatibili: tactical_rooms e long_corridor_indices. Implementate le 4 regole: boss (BFS delle distanze dalla stanza 0, pareggio spezzato per indice piu basso; ingrandimento tentato con margini decrescenti 3/2/1 SOLO sui lati senza porte, per non disallineare le connessioni gia risolte, clampato al canvas e verificato senza sovrapposizioni); nodi tattici (grado>=3, congelati SUBITO dopo albero+anelli, prima delle porte segrete); porte segrete (ogni stanza di grado 1 riceve una connessione extra kind='secret' verso la stanza libera piu vicina, riusando _connect_rooms/_non_colliding_t esteso con un parametro kind); corridoi lunghi (>12 quadretti, scansionati per ultimi cosi da includere eventuali corridoi aggiunti dalle porte segrete). Durante la scrittura dei test scoperti 4 bug nei TEST STESSI (non nel generatore): confrontavano bp.graph finale invece del grafo precedente alle porte segrete per boss/nodi tattici (ovviamente diverso, dato che le scorciatoie li modificano di proposito); assumevano che anche il lato 'bersaglio' di una porta segreta dovesse essere un vicolo cieco (falso: solo il lato che la riceve lo e); confrontavano t fra wall_index diversi credendoli collisioni. Aggiunto un helper _non_secret_graph nei test per ricostruire il grafo pre-porte-segrete (l'ordine di room.doors rispecchia l'ordine di blueprint.graph, le porte segrete sono sempre le ultime N aggiunte). Aggiornato anche un test di TASK-21 (test_zero_loops_produces_a_tree) che assumeva erroneamente nessun arco extra oltre l'albero: ora tiene conto delle porte segrete separatamente dagli anelli. 15 test nuovi in tests/test_bsp_semantics.py su seed fissi, piu 2 test diretti e deterministici su _enlarge_room isolata. Suite completa: 232 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementate le 4 regole di semantica D&D (boss piu lontano+ingrandimento sicuro, nodi tattici congelati pre-porte-segrete, corridoi lunghi post-porte-segrete, porte segrete sui vicoli ciechi). Blueprint esteso con 2 campi opzionali. 15 test su seed fissi, dopo aver corretto 4 bug nei test stessi (non nel generatore) causati da confronti sul grafo finale invece che su quello pre-scorciatoie. Suite completa: 232 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
