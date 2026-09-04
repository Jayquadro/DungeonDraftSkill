---
id: TASK-29
title: Arredo e palette per gli edifici urbani
status: Done
assignee: []
created_date: '2026-09-03 11:34'
updated_date: '2026-09-04 07:53'
labels: []
milestone: m-4
dependencies:
  - TASK-28
  - TASK-23
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Estensione di furnish e delle Palette agli stili tavern, manor e warehouse (SPEC.md §6.7, §9.5). Un edificio arredato con la palette del dungeon non è utilizzabile: servono pavimenti in assi, tavoli, letti, casse e scaffali coerenti con la funzione della stanza.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 palette_for restituisce palette specifiche per tavern, manor e warehouse
- [x] #2 L'arredo rispetta il kind della stanza: camere con letti, sala comune con tavoli e sedie, magazzino con casse e barili
- [x] #3 Nessun oggetto ostruisce porte o scale
- [x] #4 Le luci sono collocate in modo plausibile per un ambiente abitato
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. assets.py: estendere gli accents di _STYLE_DEFINITIONS[tavern|manor] con chiavi
   catalogo reali per bed/oven/desk/cupboard (warehouse ha gia crate/barrel/keg,
   sufficienti per magazzino+soppalco). Nessuna chiave inventata: solo chiavi gia
   presenti in data/assets.json.
2. compose.py: aggiungere _KIND_ACCENT_HINTS (room.kind -> tuple di chiavi accent)
   e usarla in _furnish_room per filtrare palette.accents prima di rng.choice;
   fallback su tutti gli accents se il kind non e mappato o nessuna chiave mappata
   e presente nella palette (retrocompatibile con dungeon/crypt/ecc, TASK-23).
3. Verificare (test) che gli oggetti non cadano mai dentro blueprint.stairs_rect:
   gia garantito geometricamente (gli oggetti nascono solo dentro room.rect e
   stairs_rect non si sovrappone mai a nessuna room, TASK-28), ma va reso esplicito
   con un test end-to-end su un edificio vero.
4. Verificare che _add_lighting (cli.py, gia generico) produca una luce plausibile
   per stanza anche su un Blueprint di building (test, nessuna modifica al codice
   di lighting: e gia agnostico rispetto allo stile).
5. Test: palette_for per i 3 stili (gia in gran parte coperto ma va esplicitato),
   arredo kind-specific per tavern/manor/warehouse, nessun oggetto in stairs_rect,
   luci per building.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato: (1) assets.py, accents estesi per tavern (bed, oven) e manor (bed, desk, cupboard); (2) compose.py, _KIND_ACCENT_HINTS mappa room.kind -> chiavi accent preferite, usata in _furnish_room con fallback su tutti gli accents se il kind non e mappato (retrocompatibile con dungeon/crypt/sewer/cave, TASK-23 invariato).

Bug trovato e corretto durante il test end-to-end: le chiavi preesistenti "table_round"/"chair" (tavern, TASK-17) e "table_round"/"statue" (manor, TASK-17) puntavano a texture del pack WFWMFRDX, assente da templates/blank_80x80.dungeondraft_map (che ha solo FA30DDXY in asset_manifest) -> DDF014 su ogni mappa reale. Sostituite con varianti equivalenti senza pack (chair_wood_01, table_wood_rectangular_small_01, table_corner_wood_01); "statue" rimossa (nessun equivalente senza pack nel catalogo osservato). Chiave "table_round" rinominata "table" in entrambi gli stili per coerenza.

furnish() ha un contratto a un solo livello (invariato da TASK-23): per gli edifici multi-piano il chiamante costruisce un Blueprint filtrato per piano prima di invocarla (pattern _floor_blueprint nei test, stesso che user'a il wiring CLI di TASK-30). Non ho modificato la firma di furnish: e fuori scope per TASK-29 e la userà TASK-30.

Test: tests/test_furnish_building.py (8 nuovi). Suite completa: 290 test verdi (era 282).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
palette_for restituisce palette complete per tavern/manor/warehouse; furnish sceglie gli accents in base al kind della stanza (camera->letto, sala_comune->tavoli/sedie, cucina->forno, magazzino/soppalco->casse/barili/keg, rappresentanza->tavolo/tappeto, privato->letto/scrivania/libreria, servitu->credenza/barile), con fallback sul comportamento TASK-23 per kind non mappati. Verificato con 8 nuovi test (tests/test_furnish_building.py): arredo kind-specific per i 3 stili, nessun oggetto dentro il vano scale, luci plausibili per building, e un test end-to-end che genera+arreda+illumina i 3 tipi di edificio e valida senza errori contro il template reale. In corso ho trovato e corretto un DDF014 latente da TASK-17 (accents che referenziavano un pack assente dal template). Suite: 290/290 verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
