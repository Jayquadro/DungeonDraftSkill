---
id: TASK-43
title: Pavimenti kind-specifici per le stanze
status: To Do
assignee: []
created_date: '2026-09-04 13:51'
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
- [ ] #1 Il generatore BSP (dungeon) assegna un floor coerente al kind di ogni stanza (es. boss diverso da sala normale), usando solo texture gia presenti in data/assets.json
- [ ] #2 Il generatore building assegna un floor coerente al kind di ogni stanza (es. cucina/camera/sala_comune), riusando lo stesso meccanismo
- [ ] #3 I corridoi e il vano scale restano sul floor della palette (non sono Room, non hanno un kind): nessuna modifica al loro rendering
- [ ] #4 generated/dungeon_m3.dungeondraft_map rigenerato mostra pavimenti differenziati e passa la validazione senza nuovi errori o warning
- [ ] #5 Test coprono la mappatura kind->floor per entrambi i generatori e il fallback quando un kind non e mappato (comportamento invariato: floor della palette)
<!-- AC:END -->
