---
id: TASK-17
title: 'assets.py — catalogo, Palette e required_packs'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:31'
updated_date: '2026-09-04 06:14'
labels: []
milestone: m-3
dependencies:
  - TASK-4
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modulo che traduce l'intento semantico in texture concrete (SPEC.md §6.7): load_catalog legge data/assets.json, palette_for(style, catalog) restituisce una Palette coerente (wall, floor, door, accents) per style in {dungeon, crypt, sewer, cave, tavern, manor, warehouse, city}, required_packs(doc) estrae gli ID pack referenziati dalle texture usate. Regola: assets.py non deve MAI restituire un path il cui pack non è nel template, altrimenti Dungeondraft segnala missing assets al caricamento.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 load_catalog legge data/assets.json e fallisce con messaggio esplicito se il file manca o è malformato
- [x] #2 palette_for restituisce una Palette valida per tutti e otto gli stili previsti
- [x] #3 required_packs(doc) estrae correttamente gli ID da tutti i path res://packs/<ID>/... del documento
- [x] #4 Un test verifica che ogni Palette restituita usi solo texture i cui pack sono nel manifest del template
- [x] #5 palette_for su uno stile sconosciuto solleva un errore esplicito invece di restituire una palette a caso
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Ispezionato data/assets.json (generato in TASK-4) per verificare quali chiavi reali sono disponibili in ogni categoria. Definire una tabella statica _STYLE_DEFINITIONS per gli 8 stili (dungeon, crypt, sewer, cave, tavern, manor, warehouse, city), ognuna riferita SOLO a chiavi realmente presenti nel catalogo (verificate a mano contro data/assets.json, non inventate). palette_for guarda le chiavi tramite un helper _lookup che solleva ValueError esplicito se una chiave attesa manca dal catalogo (es. dopo una rigenerazione che perde qualcosa) o se lo stile e sconosciuto. load_catalog gia implementato in TASK-4. required_packs(doc) riusa _iter_textures gia scritta in TASK-4 per estrarre i pack ID da un documento qualsiasi. Test: palette_for per tutti gli 8 stili produce una Palette con testure reali; stile sconosciuto solleva errore; ogni texture di ogni Palette ha il pack (se presente) nel manifest di data/assets.json; required_packs su documenti reali (rich_reference) confrontato con l'elenco dei pack effettivamente usati.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementato palette_for con una tabella statica _STYLE_DEFINITIONS per gli 8 stili, ogni voce verificata a mano contro le chiavi realmente presenti in data/assets.json (nessuna inventata). _lookup solleva ValueError esplicito se una chiave attesa manca dal catalogo; palette_for su stile sconosciuto solleva ValueError con l'elenco degli stili validi. required_packs riusa _iter_textures gia scritta in TASK-4. load_catalog ora gestisce esplicitamente anche JSON malformato (non solo file mancante). 12 test nuovi: uno per ogni stile che verifica una Palette valida, stile sconosciuto, chiave di catalogo mancante, nessuna texture con pack assente dal manifest (per tutti gli 8 stili), required_packs su documento sintetico e su rich_reference reale. Suite completa: 177 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementato palette_for (8 stili, tabella statica verificata contro data/assets.json reale, mai texture inventate), required_packs (riusa _iter_textures) e load_catalog con gestione esplicita di JSON malformato. 12 test nuovi, suite completa 177 test verdi.
<!-- SECTION:FINAL_SUMMARY:END -->
