---
id: TASK-30
title: 'CLI, test e gate umano per lo stile building'
status: In Progress
assignee: []
created_date: '2026-09-03 11:34'
updated_date: '2026-09-04 08:03'
labels: []
milestone: m-4
dependencies:
  - TASK-29
  - TASK-24
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Chiusura di M4 (SPEC.md §5): il comando ddforge generate building deve produrre un edificio multi-piano con tetti che Jay apre correttamente in Dungeondraft. Include test di integrazione e golden file come per il BSP.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ddforge generate building genera un edificio multi-piano con tetto, validato prima della scrittura
- [x] #2 Il CLI espone i parametri specifici dell'edificio, inclusa la tipologia e il numero di piani
- [x] #3 Esistono test di integrazione e un golden file per un seed fisso
- [ ] #4 Jay apre il file in Dungeondraft e conferma che i piani, le scale e il tetto sono corretti
- [ ] #5 Ogni difetto segnalato da Jay è riprodotto in un test prima della correzione
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. cli.py: registrare building in _load_generators; aggiungere --building-type
   e --l-shaped; ramificare _cmd_generate per il caso multi-piano (draw_building
   + furnish_building + _add_building_lighting invece di render_blueprint/furnish
   a singolo livello); style di default = building_type quando --style e assente.
2. compose.py: rooms_by_level/floor_blueprint/furnish_building, riusabili sia
   da cli.py che dai test (furnish() resta a singolo livello, TASK-23 invariato).
3. Estendere _STYLE_DEFINITIONS/palette_for (assets.py) con roof/wall_load_bearing
   per tavern/manor/warehouse: senza, draw_building non disegnava mai il tetto
   ne differenziava i muri portanti dai tramezzi (nessuna delle due cose e mai
   stata popolata da TASK-17 in poi).
4. Test: integrazione+golden file per building.generate (come TASK-25 per bsp),
   test end-to-end del CLI (multi-piano, tetto, arredo/luci per piano corretti,
   riproducibilita).
5. Generare un file demo reale e chiedere a Jay di aprirlo (gate umano AC4/5).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
CLI: 'ddforge generate building --building-type {tavern,manor,warehouse} [--l-shaped]' funzionante end-to-end (draw_building + furnish per piano + luci per piano, verificato con AC1-2). Bug trovati e corretti durante l'integrazione (nessuno di questi era coperto da test prima, tutti riprodotti in test prima della correzione, coerente con AC5):
- generators/building.py: c'era un margine di 1 quadretto fra il vano scale e l'area stanze, mai riempito da pavimento ne muri -> striscia vuota visibile dentro il perimetro portante. Rimosso (stairs_rect e generation_footprint ora esattamente adiacenti, Rect.overlaps con margin=0 conferma nessuna sovrapposizione).
- assets.py: palette_for non popolava mai roof/wall_load_bearing per nessuno stile (campi esistenti da TASK-27 ma mai valorizzati da TASK-17): draw_building quindi non disegnava MAI il tetto ne differenziava i muri portanti. Aggiunti a _STYLE_DEFINITIONS per tavern/manor/warehouse (roof='tiles', wall_load_bearing=stone/stone_09, uniche texture disponibili nel catalogo osservato).

Limite noto e non bloccante: 'ddforge generate building' produce 3 avvisi DDF102 non bloccanti (perimetro portante e vano scale del piano superiore senza porta propria). Stesso limite gia documentato per il dungeon (TASK-26): il validatore non distingue "muro esterno raggiungibile solo dall'interno" da "stanza davvero isolata". Segnalato esplicitamente a Jay nella richiesta di gate, non nascosto.

Test: tests/test_cli_generate_building.py (7), tests/test_building_integration.py (3, incluso golden file tests/fixtures/golden/building_tavern_seed_1337.json). Aggiornato anche un test preesistente in test_cli_generate.py che assumeva 'building' non ancora implementato (ora testa 'cave' per lo stesso scopo). Suite completa: 303/303 verdi.

File demo generato: generated/building_m4.dungeondraft_map (tavern, seed 1337, furnish medium, luci attive; rigenerabile con 'ddforge generate building --template templates/blank_80x80.dungeondraft_map --out generated/building_m4.dungeondraft_map --width 40 --height 40 --seed 1337 --building-type tavern --furnish medium --lights').
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-04 08:03
---
File pronto: generated/building_m4.dungeondraft_map (taverna a 2 piani, seed 1337, arredo medium, luci attive). Passa la validazione con 3 soli avvisi non bloccanti (DDF102 sul perimetro portante e sul vano scale del piano superiore, limite noto e documentato del validatore, non necessariamente un difetto della mappa).

Jay, quando puoi aprilo in Dungeondraft e verifica:
1. Il piano terra (sala comune, cucina, retro) e il primo piano (camere) sono entrambi presenti e navigabili tra le rispettive schede/livelli.
2. Il vano scale occupa la stessa posizione su entrambi i piani.
3. Le porte sono sul muro e orientate bene (stessa calibrazione di TASK-12).
4. C'e un tetto visibile sull'ultimo piano.
5. L'arredo (tavoli/sedie al piano terra, letti al primo piano) e plausibile e non blocca porte o passaggi.

In attesa della tua conferma prima di chiudere il task.
---
<!-- COMMENTS:END -->
