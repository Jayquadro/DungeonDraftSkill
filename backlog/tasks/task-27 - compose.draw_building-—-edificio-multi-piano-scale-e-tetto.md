---
id: TASK-27
title: 'compose.draw_building — edificio multi-piano, scale e tetto'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:34'
updated_date: '2026-09-04 07:21'
labels: []
milestone: m-4
dependencies:
  - TASK-19
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Composto multi-livello descritto in SPEC.md §6.6 e §9.2: distribuisce le stanze sui livelli, aggiunge il vano scale e il tetto sull'ultimo piano. Vincolo non negoziabile: le scale devono occupare lo stesso Rect su tutti i livelli, altrimenti la mappa non si legge al tavolo. Il tetto va scritto in level['roofs']['roofs'] con sun_direction coerente su tutto l'edificio.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 draw_building distribuisce le stanze su N livelli preparati da template.prepare
- [x] #2 Il vano scale occupa lo stesso Rect su tutti i livelli, verificato da un test
- [x] #3 Il tetto è aggiunto solo sull'ultimo livello, in level['roofs']['roofs'], con sun_direction coerente
- [x] #4 I muri portanti usano una texture diversa da quelle dei tramezzi
- [x] #5 Il documento multi-livello passa validate() senza errori
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Estensioni minime e retrocompatibili (default che non rompono nulla di gia Done): Room.level:int=0 (piano dell'edificio a cui appartiene la stanza — generators/building.py, TASK-28, lo popolera; qui testato costruendo Room a mano), Blueprint.stairs_rect:Rect|None=None (vano scale, stesso rettangolo su ogni piano per costruzione), Palette.roof:str|None=None (data/assets.json ha gia una categoria roofs non ancora mappata da palette_for). draw_building(level_stack, ids, blueprint, palette): raggruppa le stanze per room.level; calcola il footprint come bounding box di tutte le stanze; per ogni piano in level_stack (chiavi '0'..'N-1' come da template.prepare) disegna il perimetro portante del footprint con palette.wall_load_bearing (fallback a palette.wall se assente, altro campo opzionale su Palette) SEMPRE sullo stesso rettangolo, poi le stanze di quel piano come tramezzi via draw_room, poi il vano scale (stesso stairs_rect su ogni piano, se presente); il tetto va aggiunto SOLO sull'ultimo piano (indice piu alto in level_stack) con palette.roof, senza toccare sun_direction (gia coerente perche prepare duplica lo stesso livello sorgente su tutti i piani). Test: costruire Blueprint/Room a mano con livelli espliciti (TASK-28 non esiste ancora), verificare distribuzione corretta, stesso stairs_rect su ogni livello, tetto solo sull'ultimo, texture portante diversa dai tramezzi, validate() pulito su un documento multi-livello reale (prepare(doc, levels=2)+draw_building+finalize).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Estesa model.py con Room.level:int=0 (piano dell'edificio, TASK-28 lo popolera) e Blueprint.stairs_rect:Rect|None=None; estesa assets.Palette con roof:str|None=None e wall_load_bearing:str|None=None (entrambi opzionali e retrocompatibili, default None non rompe nulla di gia Done). Implementato draw_building: raggruppa le stanze per room.level, calcola il footprint come bounding box di tutte le stanze, disegna il perimetro portante (stesso footprint, palette.wall_load_bearing con fallback a palette.wall) su ogni piano, le stanze del piano come tramezzi via draw_room, il vano scale (stesso stairs_rect su ogni piano per costruzione, non serve verificarlo altrimenti: e garantito dal fatto di passare lo stesso oggetto Rect), il tetto SOLO sull'ultimo piano (senza toccare sun_direction, gia coerente perche prepare duplica lo stesso livello sorgente su tutti i piani). Verificato manualmente prima dei test formali su un documento reale a 2 piani: zero errori di validazione. 7 test in tests/test_draw_building.py: distribuzione corretta per piano, stesso stairs_rect su ogni livello, tetto solo sull'ultimo, texture portante diversa dai tramezzi con fallback esplicito, documento multi-livello reale senza errori. Suite completa: 263 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato draw_building: distribuisce le stanze per Room.level, perimetro portante con texture distinta (fallback a palette.wall), vano scale identico su ogni piano, tetto solo sull'ultimo. Estesi model.py (Room.level, Blueprint.stairs_rect) e assets.Palette (roof, wall_load_bearing), entrambi opzionali e retrocompatibili. 7 test nuovi, suite completa 263 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
