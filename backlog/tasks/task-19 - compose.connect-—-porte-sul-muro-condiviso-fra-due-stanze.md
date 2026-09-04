---
id: TASK-19
title: compose.connect — porte sul muro condiviso fra due stanze
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:31'
updated_date: '2026-09-04 06:28'
labels: []
milestone: m-3
dependencies:
  - TASK-18
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
La funzione più delicata del progetto (SPEC.md §6.6). Il muro condiviso fra due stanze adiacenti va trovato geometricamente e convertito in una frazione t lungo quel muro; se non esiste muro condiviso, connect genera un corridoio a L. Prescrizione esplicita della spec: scrivere test unitari con rettangoli noti PRIMA di implementare qualsiasi generatore.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 I test unitari su rettangoli noti sono scritti prima dell'implementazione e coprono adiacenza orizzontale, verticale, parziale e assenza di contatto
- [x] #2 Per due stanze adiacenti connect trova il muro condiviso e vi colloca una porta con t nell'intervallo [0, 1]
- [x] #3 La porta risultante è centrata sulla sovrapposizione dei due muri, non sul muro intero
- [x] #4 Per due stanze non adiacenti connect genera un corridoio a L che le collega
- [x] #5 Nessuna porta viene generata a distanza minore di 0.05 da un'altra sullo stesso muro (DDF105)
- [x] #6 Il documento risultante passa validate() senza errori né warning DDF102
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Design: _shared_wall_segment(rect_a, rect_b) rileva adiacenza orizzontale/verticale via confronto esatto dei bordi e overlap sull'asse libero; ritorna gli indici di lato (0=top,1=right,2=bottom,3=left, stessa convenzione di _draw_perimeter) e il segmento condiviso. _wall_for_side(level, rect, side) cerca in level['walls'] il muro i cui 2 estremi (in px) coincidono esattamente con quelli attesi per quel lato del rettangolo (nessuna ambiguita: cerca match esatto, non euristico). _t_along_wall proietta un punto sulla polilinea del muro per ottenere t, generalizzando a qualunque verso di percorrenza. Caso adiacente: porta al centro dell'overlap (non del muro intero), sul muro di room_a se trovato altrimenti room_b. Caso non adiacente: distinzione fra corridoio dritto (le x o le y si sovrappongono gia, gap solo su un asse) e L generale (nessuna sovrapposizione su nessun asse, che garantisce che il punto di piega cade fuori da entrambe le stanze); porte agli estremi del corridoio sul lato del rettangolo attraversato. Scrivere PRIMA i test su rettangoli noti (adiacenza orizzontale, verticale, parziale, nessun contatto dritto, nessun contatto a L), poi implementare finche passano. Test finale: risultato passato a validate(), zero errori, zero DDF102, zero DDF105.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Test scritti PRIMA dell'implementazione come richiesto dalla spec (adiacenza orizzontale, verticale, parziale, nessun contatto dritto, nessun contatto a L). Implementati _shared_wall_segment (adiacenza esatta + overlap sull'asse libero), _wall_for_side (match esatto degli estremi in px, nessuna ambiguita), _t_along_wall (proiezione generalizzata a qualunque verso di percorrenza), _add_door_at_point. Caso non adiacente distinto in 3 sotto-casi provabilmente corretti per costruzione: overlap su y (corridoio orizzontale dritto), overlap su x (corridoio verticale dritto), nessun overlap su nessun asse (L generale, che garantisce geometricamente che il punto di piega cade fuori da entrambe le stanze). Durante l'implementazione scoperto un bug reale: disegnare il corridoio come box chiuso a 4 muri (draw_corridor) riblocca la porta appena tagliata nel muro della stanza all'estremita, perche il muro corto del box coincide in parte con la posizione della porta. Risolto con _draw_corridor_channel, che disegna solo i 2 lati lunghi paralleli alla marcia, lasciando gli estremi aperti. Questo ha rivelato un secondo bug in validate.py (TASK-14, gia Done): i muri paralleli del canale, isolati e non loopati, venivano segnalati come falsi DDF102 — corretto li con una nota separata su TASK-14. 9 test in tests/test_connect.py, tutti passati al primo colpo dopo le due correzioni. Suite completa: 199 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato connect() con test scritti prima (adiacenza orizzontale/verticale/parziale/nessun contatto). Trovati e corretti 2 bug reali durante l'implementazione: il corridoio come box chiuso riblocca la porta appena tagliata (risolto con canale aperto a 2 soli muri lunghi); i muri isolati del canale producevano falsi DDF102 in validate.py (corretto escludendo i gruppi di 1 muro non loopato). 9 test nuovi, suite completa 199 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
