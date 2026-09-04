---
id: TASK-23
title: furnish — arredo trasversale con densità configurabile
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:32'
updated_date: '2026-09-04 06:52'
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
- [x] #1 density accetta none, light, medium e heavy, e la densità risultante rispetta i valori indicati entro una tolleranza ragionevole
- [x] #2 Nessun oggetto è piazzato a meno di 0.5 quadretti da un muro
- [x] #3 Nessun oggetto cade entro 1.5 quadretti davanti a una porta
- [x] #4 L'arredo dipende dal kind della stanza: una sala boss non è arredata come un corridoio o un locale di servizio
- [x] #5 I nodi tattici ricevono coperture (colonne, casse) ogni 3-4 quadretti
- [x] #6 L'arredo è riproducibile a parità di seed
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
furnish vive in compose.py (SPEC.md non gli assegna un file dedicato; e concettualmente un altro composto che va da Blueprint a JSON, come draw_room/connect). Densita come oggetti/quadretto (0.05/0.12/0.25/0 per light/medium/heavy/none) moltiplicata per l'area della stanza, con un moltiplicatore per kind (boss piu arredato, locale di servizio piu spoglio, default 1x altrove) per soddisfare AC4 anche se bsp.py oggi produce solo sala/corridoio/boss. Posizionamento con rejection sampling: punto casuale nel rettangolo ristretto di 0.5 dai muri, scartato se entro 1.5 da un punto porta (calcolato da Room.doors con wall_index/t, senza bisogno di leggere il level). Nodi tattici (blueprint.tactical_rooms): oltre all'arredo normale, una griglia di coperture (column/crate/barrel se presenti in palette.accents, altrimenti un qualunque accent disponibile) spaziate 3-4 quadretti. Palette senza accents (es. cave) non piazza nulla, comportamento degradato esplicito. rng passato dal chiamante (mai creato internamente), per riproducibilita. Test: densita rispettata entro tolleranza su stanze grandi, nessun oggetto a <0.5 dai muri, nessuno a <1.5 da una porta, boss arredato diversamente da servizio/sala, nodi tattici con coperture a distanza 3-4, stesso seed -> stesso output.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato furnish in compose.py (SPEC.md non gli assegna un file dedicato). Densita come oggetti/quadretto*area, moltiplicata per un fattore dipendente dal kind (boss 1.5x, servizio 0.5x, default 1x) per rendere AC4 verificabile anche se bsp.py oggi produce solo sala/corridoio/boss (servizio testato via Room costruita a mano). Posizionamento con rejection sampling: punto casuale nel rettangolo ristretto di 0.5 dai muri, scartato se entro 1.5 da un punto porta (calcolato da Room.doors senza leggere il level). Nodi tattici (blueprint.tactical_rooms): griglia di coperture spaziate 3-4 quadretti, preferendo column/crate/barrel se presenti in palette.accents. Palette senza accents (es. cave) non piazza nulla, comportamento degradato esplicito e testato. rng sempre passato dal chiamante, mai creato internamente. Verificato manualmente prima dei test formali: su una stanza 20x20 senza porte vicine, densita medium produce esattamente 48/48 oggetti attesi (area*0.12). 12 test in tests/test_furnish.py: densita per tutti i livelli con tolleranza, errore esplicito su densita sconosciuta, distanza minima dai muri (calcolata come distanza punto-segmento contro i muri realmente disegnati), distanza minima dalle porte, boss piu arredato di un servizio, corridoi mai arredati, coperture tattiche con spaziatura verificata, palette senza accents, riproducibilita. Suite completa: 244 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato furnish(level, ids, blueprint, palette, density, rng) in compose.py: densita per area con moltiplicatore per kind, rejection sampling per rispettare margine muri (0.5) e distanza porte (1.5), coperture per nodi tattici spaziate 3-4 quadretti, degradazione esplicita su palette senza accents. 12 test nuovi, suite completa 244 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
