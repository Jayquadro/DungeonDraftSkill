---
id: TASK-33
title: 'Variante fognature: canali ortogonali, camere di giunzione e acqua'
status: Done
assignee:
  - '@claude'
created_date: '2026-09-03 11:34'
updated_date: '2026-09-08 06:53'
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
- [x] #1 Il generatore produce una rete di canali ortogonali connessa, con camere di giunzione circolari
- [x] #2 Il layer water è popolato coerentemente con i canali
- [x] #3 La palette sewer è usata per muri, pavimenti e porte
- [x] #4 Il documento generato passa validate() senza errori
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Nuovo modulo generators/sewer.py (non cave.py: gia annotato in cave.py durante TASK-32 che le fognature vanno altrove, decisione di rendering diversa - qui serve la palette su muri/pavimenti/porte, non il layer cave nativo).
2. model.py: nuovo dataclass Chamber (center, radius, connected: set di lati N/E/S/O, door: bool). Blueprint riceve chambers: list[Chamber] = []. I canali riusano Corridor/Blueprint.corridors esistenti (nessun campo nuovo li): un canale ortogonale e esattamente un Corridor.
3. Generazione: griglia di nodi spaziati di `spacing` quadretti; grafo completo delle adiacenze ortogonali; albero di copertura casuale (Kruskal randomizzato, garantisce connessione, AC1) piu una piccola percentuale di archi extra per gli anelli. blueprint.graph = adiacenza fra camere (indice), per verifica BFS nei test.
4. Rendering canali: compose.draw_corridor_network gia esistente, invariato (un canale e un Corridor).
5. Rendering camere: nuova compose.draw_chamber, poligono a 16 lati che approssima il cerchio; sui lati collegati a un canale si apre un varco angolare della stessa larghezza del canale (i muri del canale si fermano esattamente sul bordo del cerchio, geometria a corda, niente sovrapposizioni). La prima camera generata (stessa convenzione di bsp._ENTRANCE_ROOM) riceve una porta (palette.door) su un arco non collegato a nessun canale.
6. Water: nuova build.add_water_polygon(level, points_grid, *, deep_color, shallow_color, blend_distance). Inizializza level['water']['tree'] come nodo contenitore vuoto se assente (schema decodificato ora da templates/rich_reference.dungeondraft_map, mai documentato finora - lo aggiungo a docs/format.md come nuova sezione, stesso trattamento del cave bitmap in TASK-31/32). Un poligono d'acqua per ogni canale e uno per ogni camera, stessa impronta dei pavimenti.
7. compose.render_sewer_blueprint(level, ids, blueprint, palette): disegna canali, camere, acqua.
8. cli.py: algoritmo "sewer" aggiunto alle scelte e a _load_generators; ramo dedicato in _cmd_generate (come "cave", niente furnish/luci: le camere non sono Room).
9. Test: tests/test_generators_sewer.py (riproducibilita seed, RNG globale intatto, AC1 via BFS su blueprint.graph, geometria dei varchi delle camere), tests/test_build.py (add_water_polygon), tests/test_cli_generate.py (ddforge generate sewer + validate() zero errori, AC4), verifica manuale palette sewer su muri/pavimenti/porte (AC3).
10. docs/format.md: nuova sezione per lo schema water.tree (analoga a §14 per cave.bitmap).

Parametri non fissati da SPEC.md (scelti e documentati nel codice, aggiustabili via parametro, stesso approccio di TASK-32): spacing griglia, canal_width, chamber_radius, probabilita' archi extra per gli anelli.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verifica: suite completa 428 passed, 1 skipped (+59 rispetto ai 369 post-TASK-32: 40 in test_generators_sewer.py, 15 in test_compose.py, 4 in test_build.py, 2 in test_cli_generate.py), nessuna regressione.

AC1 (rete connessa, camere circolari): test_network_is_a_single_connected_component (6 seed, BFS su blueprint.graph raggiunge tutte le camere) + test_every_corridor_is_axis_aligned + test_every_chamber_has_at_least_one_connection (20 seed, garantito dalla costruzione via albero di copertura). Le camere sono poligoni regolari a 16 lati (compose._chamber_circle_points, verificato equidistanti dal centro nei test).

AC2 (water coerente con i canali): compose.render_sewer_blueprint aggiunge un poligono d'acqua per ogni canale e ogni camera, stessa impronta dei pavimenti - verificato che il conteggio dei figli di water.tree coincide sempre con quello dei pattern (test_render_sewer_blueprint_water_footprint_matches_corridors_and_chambers, e end-to-end via CLI).

AC3 (palette sewer su muri/pavimenti/porte): verificato via CLI end-to-end (test_generate_sewer_produces_a_valid_file_with_sewer_palette) - tutti i muri usano concrete.png, tutti i pavimenti cobblestone.png, l'unica porta (camera d'ingresso) portcullis.png, dalla vera palette_for("sewer", catalog).

AC4 (validate() senza errori): test_generated_document_passes_validate_with_no_errors (3 seed, mappa 80x80 reale via template) e generazione manuale via CLI (seed multipli, mappe 40x40/60x60/80x80): sempre 0 errori, solo avvisi DDF102 attesi (canali/camere sono passaggi aperti senza porte, stesso limite noto del validatore gia documentato per i corridoi bsp, vedi validate.py).

Decisione geometrica chiave: le camere circolari sono approssimate con un 16-gono; dove un canale entra, il muro si interrompe esattamente sulla corda del cerchio (profondita' sqrt(radius^2 - (canal_width/2)^2)), calcolata identicamente sia in generators/sewer.py (per gli estremi del Corridor) sia in compose._chamber_gap_edge_points (per i vertici del poligono): niente sovrapposizioni ne fessure fra canale e camera, verificato in test_chamber_wall_arcs_single_gap_starts_and_ends_exactly_on_the_gap_edges.

Schema water.tree mai documentato prima: decodificato da un campione reale (templates/rich_reference.dungeondraft_map, che Dungeondraft riapre), non serviva uno spike separato (JSON puro, non un blob binario come cave.bitmap). Documentato in docs/format.md §15.

Camera d'ingresso: convenzione bsp._ENTRANCE_ROOM riusata (il primo nodo generato, angolo (0,0) della griglia, ha al massimo 2 lati collegati per costruzione: resta sempre almeno un arco libero per la porta, qualunque seed - verificato su 20 seed).

Caso limite gestito: un incrocio a 4 vie (tutti e 4 i lati cardinali collegati, puo' capitare con gli anelli extra) non ha muri ne' porta, solo pavimento/acqua - verificato con test_chamber_wall_arcs_all_four_sides_connected_is_no_walls_at_all e test_draw_chamber_no_door_when_no_free_arc_exists.

Parametri non fissati da SPEC.md, scelti e documentati nel codice (generators/sewer.py), aggiustabili via parametro come in TASK-32: spacing griglia (8 quadretti), canal_width (2), chamber_radius (1.5), extra_loop_prob (0.15, per gli anelli oltre l'albero di copertura).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementata la variante fognature (SPEC.md §9.3): griglia di canali ortogonali (Corridor riusati com'erano, draw_corridor_network invariato) con camere di giunzione circolari (nuovo model.Chamber, approssimate a 16-gono in compose.draw_chamber, con un varco esatto - geometria a corda - dove entra ogni canale), e un poligono d'acqua per ogni canale/camera nel layer water nativo (nuova primitiva build.add_water_polygon, schema mai documentato prima e ora in docs/format.md §15).

Architettura: nuovo modulo generators/sewer.py (non cave.py, come gia annotato in cave.py durante TASK-32), perche qui la palette sewer disegna muri/pavimenti/porte veri invece del layer cave nativo. La rete e generata con un albero di copertura casuale (Kruskal randomizzato) su una griglia di nodi, garantendo la connessione per costruzione (AC1), piu una piccola probabilita di anelli extra. La camera d'ingresso (convenzione bsp._ENTRANCE_ROOM, il nodo d'angolo) riceve l'unica porta della mappa.

Cosa e cambiato:
- model.py: Chamber (center, radius, connected, door) e Blueprint.chambers.
- build.py: add_water_polygon (crea level['water']['tree'] al primo uso).
- compose.py: _chamber_circle_points/_chamber_gap_depth/_chamber_gap_edge_points/_chamber_wall_arcs (geometria dei varchi), draw_chamber, render_sewer_blueprint.
- generators/sewer.py (nuovo): generate().
- cli.py: algoritmo "sewer" (choices, _load_generators, ramo di rendering dedicato, niente furnish/luci).
- docs/format.md §15: schema water.tree, decodificato da templates/rich_reference.dungeondraft_map.
- Test: tests/test_generators_sewer.py (nuovo, 40 test), tests/test_compose.py (+15), tests/test_build.py (+4), tests/test_cli_generate.py (+2).

Verifica: suite completa 428 passed, 1 skipped (+59, nessuna regressione). AC1-4 verificati con evidenza automatica (BFS di connessione su piu seed, conteggio poligoni water vs pattern, texture della palette sewer end-to-end via CLI, validate() a 0 errori su piu seed e dimensioni mappa) - dettagli nelle implementation notes.

Fuori perimetro, per scelta esplicita: nessun furnish/illuminazione per le fognature (nessun AC lo richiede, le camere non sono Room, stesso principio delle grotte in TASK-32); il caso limite dell'incrocio a 4 vie completamente aperto (nessun muro, solo pavimento/acqua) e gestito ma non e un difetto - e la geometria corretta per un nodo con tutti i lati connessi.
<!-- SECTION:FINAL_SUMMARY:END -->
