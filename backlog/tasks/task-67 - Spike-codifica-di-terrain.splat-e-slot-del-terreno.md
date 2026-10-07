---
id: TASK-67
title: 'Spike: codifica di terrain.splat e slot del terreno'
status: Done
assignee: []
created_date: '2026-10-04 17:30'
updated_date: '2026-10-07 08:25'
labels: []
milestone: m-10
dependencies: []
references:
  - src/ddforge/cave_bitmap.py
  - src/ddforge/build.py
  - templates/rich_reference.dungeondraft_map
documentation:
  - docs/SPEC-decorate.md
  - docs/format.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
L'abbellimento (docs/SPEC-decorate.md §6.2, §7.3) vuole dipingere il terreno: terra e polvere ai bordi delle stanze, muschio, fango, erba fra gli edifici di una citta. Il livello ha `terrain` con 4 slot (`texture_1..texture_4`) e un blob `splat` di width×height×64 elementi, ma nessun codice del progetto lo scrive: e il template a fornirlo, mai modificato.

Lo spike, sul modello di TASK-31 per `cave.bitmap`, deve capire come e codificato lo splat (canali per slot, risoluzione sotto-cella, ordine), se si possono sostituire le texture degli slot con quelle del catalogo `terrain`, e verificarlo in Dungeondraft con campioni reali disegnati a mano da Jay. Se la codifica non si risolve, l'esito e una raccomandazione documentata di ripiego (pattern semitrasparenti).

Inoltre Jay ha deciso (SPEC-decorate §14 D6) che decorate cambia anche la texture del pavimento delle grotte (layer cave nativo): lo spike deve trovare in quale campo del livello sta, quali valori/texture accetta Dungeondraft e come scriverla senza toccare `cave.bitmap`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 La codifica di `terrain.splat` e documentata in docs/format.md in una nuova sezione, citando i file reali osservati
- [x] #2 Esiste una funzione che scrive lo splat per una maschera data, coperta da test su fixture reali committate
- [x] #3 E documentato se e come si cambiano le texture degli slot `texture_1..4`
- [x] #4 Una mappa di prova con terreno dipinto e stata aperta in Dungeondraft da Jay e il terreno appare dove previsto
- [x] #5 Se la codifica non e risolta, la nota di chiusura indica il ripiego da adottare in decorate
- [x] #6 E documentato in docs/format.md in quale campo sta la texture del pavimento del layer cave e quali texture accetta, con una funzione che la imposta e una mappa di prova aperta da Jay in Dungeondraft con il pavimento della grotta cambiato
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Cercare file .dungeondraft_map reali con terreno dipinto sul disco di Jay (AppData backups, Desktop): trovato cave_spike.dungeondraft_map, byte-identico a tests/fixtures/cave_freehand_80x80.dungeondraft_map (Jay aveva dipinto il terreno nella stessa sessione dello spike cave di TASK-31). 2. Confrontare due ipotesi di ordinamento dei gruppi di 4 byte (row-major su tutta la griglia vs blocco di 16 sotto-celle per quadretto) misurando la densita' della macchia non-default nel suo bounding box; A vince nettamente (0.54 vs 0.23) e il round-trip byte-esatto lo confirma. 3. Scrivere ddforge.terrain_splat (encode/decode/paint_tiles) e le primitive build.set_terrain_splat/set_cave_floor_texture. 4. Trovare level['cave']['texture'] per il pavimento della grotta nativa e le texture disponibili (2 base + 1 pack, scoperto anche un bug di collisione in assets.read_base_pack). 5. Documentare in docs/format.md §16. 6. Test su tests/test_terrain_splat_format.py e tests/test_build.py. 7. Generare due mappe di prova (generated/task67_terrain_spike.dungeondraft_map, generated/task67_cave_floor_spike.dungeondraft_map) per il gate umano di Jay.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Codifica di terrain.splat risolta: griglia row-major su tutta la mappa (4*width x 4*height sotto-celle, NESSUN margine a differenza di cave.bitmap), 4 byte per sotto-cella = peso 0-255 di ciascuno dei 4 slot texture_1..4 (somma 255 per un pennello pieno). Isolata confrontando due ipotesi di ordinamento sul campione reale cave_freehand_80x80.dungeondraft_map (identico a backups/cave_spike.dungeondraft_map): densita' della macchia non-default nel bounding box 0.54 (row-major, giusta) contro 0.23 (blocco per quadretto); confermata dal round-trip byte-esatto. texture_1..4 sono stringhe semplici, nessuna codifica; risolvono su data/assets.json['terrain']. Pavimento nativo della grotta: level['cave']['texture'], mai cave.bitmap/entrance_bitmap; solo 3 texture verificate sul disco di Jay (colorable/rocky della base del programma, limestone del pack DnDungeon Overhaul). Bug collaterale scoperto (non corretto, fuori perimetro): assets.read_base_pack indicizza le destinazioni solo per nome file, quindi textures/caves/colorable/floor.png e textures/caves/rocky/floor.png collidono sulla stessa chiave e una delle due sparisce silenziosamente - segnalato come follow-up. Implementato ddforge/terrain_splat.py (encode/decode/paint_tiles/default_weights/CAVE_FLOOR_TEXTURES) + build.set_terrain_splat/set_cave_floor_texture. docs/format.md §16 scritto. Test: tests/test_terrain_splat_format.py (10) + 3 nuovi in tests/test_build.py, tutti verdi; suite completa (-m 'not slow') in corso di verifica. Generate due mappe di prova per il gate umano: generated/task67_terrain_spike.dungeondraft_map (rettangolo di terreno sabbia, quadretti x10-30 y10-15, stesso angolo di calibrazione del rettangolo cave di TASK-31) e generated/task67_cave_floor_spike.dungeondraft_map (pavimento grotta -> limestone). Entrambe validate senza errori. AC4 e AC6 restano aperti: serve che Jay le apra in Dungeondraft e confermi.

Suite completa (-m 'not slow') confermata verde dopo tutte le modifiche di questo task: 819 passed, 1 skipped, 5 deselected (1087s).

AC6 confermato da Jay (chat, 2026-10-07): il pavimento della grotta (texture limestone) e' corretto e cave.bitmap/entrance_bitmap restano invariati. AC4: primo giro del rettangolo di terreno (x=10-30,y=10-15) risultava dietro al pavimento della stanza, difficile da valutare; rigenerato con x=3-23,y=10-15 (stesse dimensioni 20x5, ma interamente dentro la stanza 2,1-26,22) su richiesta di Jay. In attesa di conferma sul file aggiornato.

Scoperta utile per TASK-69/71/72: il pattern del pavimento di una stanza/corridoio copre interamente il terrain sottostante in Dungeondraft (layer sopra, opaco) - un rettangolo dipinto DENTRO una stanza non si vede affatto finche' non si cambia anche la texture del pattern. Verificato chiedendo a Jay di aprire tre varianti: (1) rettangolo a cavallo fra stanza e area vuota -> visibile solo la parte fuori stanza; (2) rettangolo tutto dentro una stanza -> invisibile; (3) stesso rettangolo su un template vuoto senza nessun pattern sopra -> in verifica. Implicazione per il planner di decorate: la pittura di terreno ha senso soprattutto ai bordi delle stanze/fuori dalle zone con pattern (esattamente come dice SPEC-decorate §6.2, 'terra e polvere AI BORDI delle stanze'), non come sostituto del floor dentro una stanza.

AC4 confermato da Jay (chat, 2026-10-07) sul terzo file di prova (rettangolo di terreno su template vuoto, senza nessun pattern sopra): 'esattamente come descritto'. Scoperta chiave durante la verifica: il pattern del pavimento di una stanza/corridoio e' sempre opaco sopra il terrain in Dungeondraft, quindi dipingere terreno DENTRO una stanza non produce alcun effetto visibile finche' non si cambia anche la texture del pattern - coerente con SPEC-decorate §6.2 ('terra e polvere ai BORDI delle stanze', non dentro). Registrata come vincolo per il planner di TASK-69/71/72.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Codifica di terrain.splat risolta: griglia row-major su tutta la mappa (4*width x 4*height sotto-celle, nessun margine), 4 byte per sotto-cella = peso 0-255 per ciascuno dei 4 slot texture_1..4. Confermata su un campione reale (cave_freehand_80x80, round-trip byte-esatto) e su tre mappe di prova aperte da Jay in Dungeondraft (l'ultima, su template vuoto, corrisponde esattamente alle attese). Scoperta rilevante per il planner futuro: il pattern del pavimento di stanze/corridoi copre sempre il terrain sottostante, quindi la pittura di terreno ha senso ai bordi/fuori dalle zone con pattern, non come sostituto del floor. Pavimento nativo delle grotte: level['cave']['texture'], mai cave.bitmap/entrance_bitmap; confermato da Jay con la texture limestone del pack DnDungeon Overhaul. Implementato ddforge/terrain_splat.py + build.set_terrain_splat/set_cave_floor_texture, documentato in docs/format.md §16, testato in tests/test_terrain_splat_format.py e tests/test_build.py. Suite completa confermata verde (819 passed, 1 skipped).
<!-- SECTION:FINAL_SUMMARY:END -->
