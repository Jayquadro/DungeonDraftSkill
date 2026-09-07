---
id: TASK-43
title: Pavimenti kind-specifici per le stanze
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-04 13:51'
updated_date: '2026-09-07 10:20'
labels: []
dependencies:
  - TASK-26
documentation:
  - docs/SPEC.md
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Room.floor esiste gia come override per-stanza rispetto a palette.floor (model.py), e compose.draw_room lo usa gia (room.floor or palette.floor), ma nessun generatore lo popola: ogni stanza generata (dungeon BSP, edifici, e gli altri stili quando implementati) prende sempre lo stesso pavimento uniforme della palette, indipendentemente dal room.kind. Jay l'ha notato aprendo generated/dungeon_m3.dungeondraft_map nel gate umano M3 (TASK-26): i pavimenti sono tutti bianchi/uniformi, e vorrebbe un tipo di pavimento coerente col tipo di stanza (es. la stanza boss diversa da una sala normale, cucina diversa da camera negli edifici). Il catalogo data/assets.json ha solo 6 texture in 'floors' (cobblestone, stone_floor, tileset_brick_basketweave, tileset_cobble, wood_planks, wooden_flooring_m_light): la mappatura kind->floor deve usare solo chiavi gia presenti nel catalogo, nessuna inventata (stessa regola gia seguita in TASK-29 per gli accent).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Il generatore BSP (dungeon) assegna un floor coerente al kind di ogni stanza (es. boss diverso da sala normale), usando solo texture gia presenti in data/assets.json
- [x] #2 Il generatore building assegna un floor coerente al kind di ogni stanza (es. cucina/camera/sala_comune), riusando lo stesso meccanismo
- [x] #3 I corridoi e il vano scale restano sul floor della palette (non sono Room, non hanno un kind): nessuna modifica al loro rendering
- [x] #4 generated/dungeon_m3.dungeondraft_map rigenerato mostra pavimenti differenziati e passa la validazione senza nuovi errori o warning
- [x] #5 Test coprono la mappatura kind->floor per entrambi i generatori e il fallback quando un kind non e mappato (comportamento invariato: floor della palette)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. assets.py: aggiungere Palette.floors: dict[str, str] = field(default_factory=dict) (stesso pattern di accents). Aggiungere chiave "floors" (kind -> chiave gia in data/assets.json floors) a _STYLE_DEFINITIONS per dungeon (boss->tileset_brick_basketweave), tavern (cucina->cobblestone, retro->tileset_cobble, camera->wooden_flooring_m_light), manor (privato->wood_planks, servitu->tileset_cobble), warehouse (soppalco->wood_planks). Nessuna chiave inventata, solo le 6 gia nel catalogo. palette_for() popola palette.floors via _lookup(catalog, "floors", key) per ogni entry.
2. compose.py: helper _room_floor(room, palette) = room.floor or palette.floors.get(room.kind) or palette.floor, usato in _draw_perimeter al posto di `room.floor or palette.floor`. draw_corridor_network (corridoi) e _stairwell_room (kind="vano_scale", non mappato) restano invariati -> AC3 soddisfatto per costruzione.
3. Test:
   - test_assets.py: estendere i test parametrizzati esistenti (valid palette per ogni stile, texture solo da pack noti) a includere palette.floors.values(); nuovo test che verifica floors specifiche per dungeon/tavern/manor/warehouse (boss/cucina/retro/camera/privato/servitu/soppalco diversi dal floor di default dove mappati).
   - test_compose.py: nuovo test su draw_room che kind mappato in palette.floors prende quel floor, kind non mappato ricade su palette.floor (fallback invariato), e room.floor esplicito vince comunque su palette.floors.
   - test_bsp_semantics.py o simile: generate() dungeon + palette_for("dungeon") + draw_room -> la stanza boss ha floor diverso dalle sale normali.
   - test_furnish_building.py o test_building_gate.py: draw_building su tavern -> cucina/retro/camera hanno floor diversi fra loro e da sala_comune.
4. Rigenerare generated/dungeon_m3.dungeondraft_map con: ddforge generate dungeon --template templates/blank_80x80.dungeondraft_map --out generated/dungeon_m3.dungeondraft_map --width 80 --height 80 --rooms 8 --seed 1337 --furnish medium --lights; validare che non emerga alcun nuovo errore/warning oltre ai DDF102 gia noti e documentati.
5. Aggiornare docs/SPEC.md §6.7 (snippet Palette con il nuovo campo floors) e una riga in §9.5 che il pavimento, come gli accents, rispetta il kind della stanza tramite palette.floors.
6. pytest -q completo prima di chiudere.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Palette.floors: dict[str,str] (room.kind -> texture), stesso meccanismo di _KIND_ACCENT_HINTS. _STYLE_DEFINITIONS aggiorna dungeon (boss->tileset_brick_basketweave), tavern (cucina->cobblestone, retro->tileset_cobble, camera->wooden_flooring_m_light), manor (privato->wood_planks, servitu->tileset_cobble), warehouse (soppalco->wood_planks): solo le 6 chiavi gia in data/assets.json floors, nessuna inventata. palette_for() le risolve con _lookup (fallisce esplicito se assenti, come per accents).

compose._room_floor(room, palette) = room.floor or palette.floors.get(room.kind) or palette.floor, usato in _draw_perimeter. draw_corridor_network e _stairwell_room (kind="vano_scale") non passano da li: restano sempre sul floor uniforme per costruzione (AC3).

Golden bsp_seed_1337 e building_tavern_seed_1337 rigenerati: diff verificato a mano prima di sovrascrivere, solo pattern.texture cambiati (1 stanza boss nel dungeon; cucina/retro/camera nella taverna), nessun altro campo.

generated/dungeon_m3.dungeondraft_map rigenerato con il comando documentato in TASK-26 (seed 1337, furnish medium, lights). ddforge validate: "Nessun problema trovato" (zero errori, zero avvisi: anche i 2 DDF102 storici sui gomiti di corridoio non compaiono piu su questo seed).

Test aggiunti: test_assets.py (palette.floors nei due test parametrizzati esistenti + 2 nuovi test su kind mappati/non mappati), test_compose.py (kind mappato vs fallback vs override esplicito di room.floor), test_bsp_integration.py (boss vs sale normali dopo render_blueprint reale), test_building_integration.py (cucina/retro/sala_comune dopo draw_building reale). Suite completa: 344 passed, 1 skipped.

docs/SPEC.md aggiornato: campo Palette.floors nello snippet §6.7, nota su pavimento kind-specifico in §9.5.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Room.floor gia esisteva come override; nessun generatore lo popolava, quindi ogni stanza usava sempre palette.floor uniforme a prescindere dal kind (segnalato da Jay al gate M3, TASK-26).

Aggiunto Palette.floors: dict[room.kind -> texture] (stesso meccanismo di _KIND_ACCENT_HINTS/TASK-29), popolato da palette_for() via _lookup su data/assets.json (solo le 6 chiavi floors gia presenti, nessuna inventata). compose._draw_perimeter ora sceglie room.floor or palette.floors.get(room.kind) or palette.floor: dungeon (boss diverso da sala), tavern (cucina/retro/camera diversi fra loro e da sala_comune), manor (privato/servitu diversi da rappresentanza), warehouse (soppalco diverso da magazzino). Corridoi (draw_corridor_network) e vano scale (kind="vano_scale") non passano da questa mappatura: restano sul floor uniforme per costruzione.

Verificato con: suite completa 344 passed/1 skipped (incluse le nuove test_bsp_integration.test_bsp_boss_room_gets_a_different_floor_than_regular_rooms e test_building_integration.test_building_assigns_kind_specific_floors_to_each_room, che usano i generatori reali + palette_for + render_blueprint/draw_building, non solo compose isolato); golden bsp_seed_1337 e building_tavern_seed_1337 rigenerati con diff verificato a mano (solo pattern.texture, nessun altro campo); generated/dungeon_m3.dungeondraft_map rigenerato con il comando documentato in TASK-26 e validato: "Nessun problema trovato" (zero errori, zero avvisi, spariti anche i 2 DDF102 storici). docs/SPEC.md aggiornato (§6.7 Palette.floors, §9.5 nota sul pavimento kind-specifico).
<!-- SECTION:FINAL_SUMMARY:END -->
