---
id: TASK-18
title: compose.py — draw_room e draw_corridor
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:31'
updated_date: '2026-09-04 07:06'
labels: []
milestone: m-3
dependencies:
  - TASK-10
  - TASK-9
  - TASK-17
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Primo livello di composti sopra le primitive (SPEC.md §6.6): draw_room disegna pavimento, muri perimetrali, porte e luci di una Room e restituisce un dict con le chiavi walls, pattern e portals; draw_corridor disegna un corridoio come stanza stretta senza porte alle estremità. Deve rispettare la calibrazione delle porte fissata nel gate umano di M1.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 draw_room produce un perimetro chiuso, un pavimento coerente con la Palette e le porte richieste dalla Room
- [x] #2 draw_room restituisce il dict con walls, pattern e portals come da SPEC.md §6.6
- [x] #3 draw_corridor non mette porte alle estremità del corridoio
- [x] #4 Il documento risultante passa validate() senza errori
- [x] #5 Test unitari su rettangoli noti verificano coordinate e conteggio degli elementi generati
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Prima di implementare: derivata dai 3 campioni reali osservati (SPEC.md §13 + i 2 portali di rich_reference) la relazione rotation = atan2(direction.y, direction.x), verificata esatta su tutti e 3 (docs/format.md, sezione portal aggiornata). draw_room: add_pattern sul rettangolo della Room, 4 muri perimetrali separati (stesso pattern del demo M1, per poter agganciare le porte a un muro specifico), per ogni Door in room.doors calcolare la normale uscente del muro rispetto al centro stanza (helper _outward_normal), derivare rotation con la formula sopra, chiamare add_portal con palette.door; per ogni luce in room.lights chiamare add_light. draw_corridor: stessa logica di draw_room ma senza porte. Aggiornare anche scripts/demo_m1.py per usare la stessa formula invece del placeholder rotation=0.0 scollegato da direction=(0,1), cosi il file che Jay controllera per il gate umano ha gia la miglior ipotesi disponibile. Test su rettangoli noti: coordinate dei muri, numero di porte, rotation coerente con la formula, validate() senza errori sul risultato.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Prima di implementare: derivata dai 3 campioni reali osservati la relazione rotation = atan2(direction.y, direction.x), verificata esatta (differenza < 1e-6) su SPEC.md §13 e i 2 portali di rich_reference. Documentato in docs/format.md §5. draw_room/draw_corridor condividono un helper interno _draw_perimeter; _outward_normal calcola la normale del muro rivolta lontano dal centro della Room (in coordinate px), usata come portal.direction, con rotation derivata dalla formula sopra invece di un placeholder arbitrario. Aggiornato anche scripts/demo_m1.py per usare compose.draw_room invece di chiamare le primitive a mano (dogfooding), correggendo un'inconsistenza: il placeholder precedente aveva direction=(0,1) ma rotation=0.0, che non rispettava la formula ora nota — rigenerato generated/demo_m1.dungeondraft_map con rotation=1.5707963267948966 coerente. 11 test in tests/test_compose.py, incluso un test end-to-end che passa il risultato di draw_room a validate() (zero errori, esclusi DDF010/011 che richiedono blob binari reali non presenti nel documento sintetico del test). Suite completa: 188 test verdi.

Correzione post-chiusura (gate umano TASK-12): _outward_normal era una perpendicolare al muro (normale uscente), ma lo screenshot reale mostrava la porta ruotata di 90 gradi col muro visivamente spezzato. Il vero significato di portal.direction, confermato sui 2 campioni reali di rich_reference, e la TANGENTE del muro (dal primo punto all'ultimo), non la normale. Rinominata in _wall_tangent, semplificata (non serve piu il centro della stanza per scegliere il verso 'uscente', la tangente e univocamente determinata dall'ordine dei punti del muro). Aggiornato docs/format.md §5. Tutti i 244 test restano verdi dopo la correzione (nessuno verificava un valore di rotazione specifico legato alla vecchia semantica).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementati draw_room/draw_corridor. Derivata e verificata (su 3 campioni reali) la formula rotation=atan2(direction.y, direction.x) per le porte, sostituendo il placeholder arbitrario usato in demo_m1.py (ora dogfooda draw_room). 11 test nuovi, suite completa 188 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
